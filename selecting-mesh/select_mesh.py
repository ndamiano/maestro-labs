"""Generate one image, reconstruct it several cheap ways, let the LLM pick.

    python select_mesh.py "a weathered wooden barrel" --n 4

The pipeline is four holds of the card, in the order the tenants want it:

    image   ComfyUI draws the subject once, on alpha, ready for image-to-3D
    mesh    TRELLIS2 reconstructs it N times on the cheap '512' pipeline,
            one seed per candidate, in a single worker batch
    (none)  Godot renders each candidate GLB to a picture
    llm     ninfer's vision model looks at the source image next to every
            render and says which reconstruction is most faithful

Everything is written under output/<slug>/ and every step skips work that is
already on disk, so a rerun pays only for what is missing. The winner lands as
`best.glb` with the judge's verdict beside it in `selection.json`.

All the machinery — ComfyUI graphs, the TRELLIS2 worker, GPU tenancy, the
subject renderer — is worldclaw's; this module only sequences it.
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from ai_harness import LLMHarness
from ai_harness.types import Message
from worldclaw.backends import GPU, ImageModel, MeshModel
from worldclaw.backends.gpu import _default_tenants

OUTPUT_DIR = Path(__file__).parent / "output"
GODOT_PROJECT = Path(
    "/home/nick/Documents/Labs/worldclaw/worldclaw/objects/godot"
)

LLM_ENDPOINT = "http://127.0.0.1:8090"
LLM_MODEL = "qwen3.8_27b"

# Cheap on purpose: the point is many candidates, not one good one. The '512'
# pipeline samples at a quarter of the default's resolution, and a candidate
# only ever needs to survive a 512px render and a judge's glance.
PIPELINE = "512"
DECIMATION_TARGET = 15_000
TEXTURE_SIZE = 512

# Appended to the user's prompt; what makes an image reconstructable rather
# than what the object is (same reasoning as worldclaw's subject.py).
SUBJECT_STYLE = (
    "Single object, complete and unobstructed, centred and filling the frame, "
    "photographed from a three-quarter angle with visible depth, evenly lit "
    "from several directions, on a plain background."
)

JUDGE_SYSTEM = """
You compare 3D reconstructions of an object against the photograph they were
made from. The first image is the photograph. Each following image is a render
of one candidate reconstruction, introduced by its name.

Judge each candidate on:
  * shape fidelity — does the geometry match the photograph's object, with
    real depth, or is it a flat card, a blob, or missing parts?
  * texture fidelity — do the colours and surface detail match?
  * cleanliness — floating fragments, holes, smearing count against it.

Then answer with ONLY a JSON object, no prose around it:

  {"best": "<candidate name>",
   "ranking": ["<best>", "...", "<worst>"],
   "verdicts": {"<name>": "<one sentence on that candidate>"}}
""".strip()


def _judge_tenants() -> dict:
    """worldclaw's tenants, with the language model sized for judging.

    The default llm tenant carries a 65k context and needs 27.8 GiB of VRAM
    free, which a desktop with anything open cannot always give it. Judging is
    a handful of images and one JSON reply; a 24k context covers it and the
    smaller KV cache brings the admission test down with it.
    """
    tenants = _default_tenants()
    llm = tenants["llm"]
    argv = list(llm.argv)
    argv[argv.index("--max-context") + 1] = "24576"
    llm.argv = argv
    llm.vram_mib = 26000
    return tenants


def slugify(prompt: str) -> str:
    words = re.findall(r"[a-z0-9]+", prompt.lower())[:6]
    return "-".join(words) or "subject"


def _image_part(path: Path) -> dict:
    data = base64.b64encode(path.read_bytes()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{data}"}}


def generate_subject(prompt: str, out_dir: Path, gpu: GPU, *, seed: int = 0) -> Path:
    """Draw the subject once, on alpha, and return the file."""
    subject = out_dir / "subject.png"
    if subject.exists():
        return subject
    with gpu.hold("image"):
        ImageModel().generate(
            f"{prompt}. {SUBJECT_STYLE}",
            subject, width=1024, height=1024, seed=seed, cutout=True,
        )
    print(f"[select] drew {subject}")
    return subject


def reconstruct_candidates(
    subject: Path, out_dir: Path, gpu: GPU, *, n: int
) -> dict[str, Path]:
    """N cheap meshes of the same image, keyed by candidate name.

    The worker derives each item's seed from its filename, so the same image
    hard-linked under n different names is n distinct samples — and one batch,
    which loads the pipeline once instead of n times.
    """
    link_dir = out_dir / "candidates"
    link_dir.mkdir(parents=True, exist_ok=True)
    links = []
    for i in range(n):
        link = link_dir / f"cand_{i:02d}.png"
        if not link.exists():
            link.hardlink_to(subject)
        links.append(link)

    mesh_dir = out_dir / "meshes"
    wanted = [p for p in links if not (mesh_dir / f"{p.stem}.glb").exists()]
    if wanted:
        with gpu.hold("mesh"):
            MeshModel(
                pipeline=PIPELINE,
                decimation_target=DECIMATION_TARGET,
                texture_size=TEXTURE_SIZE,
            ).reconstruct(links, mesh_dir)
    made = {
        p.stem: mesh_dir / f"{p.stem}.glb"
        for p in links
        if (mesh_dir / f"{p.stem}.glb").exists()
    }
    print(f"[select] {len(made)}/{n} candidates reconstructed")
    return made


def render_candidates(meshes: dict[str, Path], out_dir: Path) -> dict[str, Path]:
    """One picture per mesh, via worldclaw's subject renderer."""
    render_dir = out_dir / "renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    items = [
        {"mesh": str(glb.resolve()), "out": str((render_dir / f"{name}.png").resolve())}
        for name, glb in meshes.items()
        if not (render_dir / f"{name}.png").exists()
    ]
    if items:
        job = out_dir / "render_job.json"
        job.write_text(json.dumps({"items": items}, indent=1))
        result = subprocess.run(
            ["godot", "--path", str(GODOT_PROJECT), "--resolution", "512x512",
             "--", "--job", str(job.resolve())],
            capture_output=True, text=True, timeout=600,
        )
        if result.returncode != 0:
            print(result.stdout[-2000:], file=sys.stderr)
    made = {
        name: render_dir / f"{name}.png"
        for name in meshes
        if (render_dir / f"{name}.png").exists()
    }
    print(f"[select] rendered {len(made)}/{len(meshes)}")
    return made


def judge(
    prompt: str, subject: Path, renders: dict[str, Path], gpu: GPU
) -> dict:
    """Show the source next to every render and get a ranking back."""
    with gpu.hold("llm"):
        harness = LLMHarness(LLM_ENDPOINT, model=LLM_MODEL, system=JUDGE_SYSTEM)
        return _ask_judge(harness, prompt, subject, renders)


def _ask_judge(
    harness: LLMHarness, prompt: str, subject: Path, renders: dict[str, Path]
) -> dict:
    parts: list[dict] = [
        {"type": "text", "text":
            f'The photograph, of "{prompt}":'},
        _image_part(subject),
    ]
    for name in sorted(renders):
        parts.append({"type": "text", "text": f"Candidate {name}:"})
        parts.append(_image_part(renders[name]))
    parts.append({"type": "text", "text":
        "Which candidate reconstructs the photograph best? Answer with the "
        "JSON object only."})

    reply = str(harness.send_message(
        [Message("user", parts)], temperature=0.0  # type: ignore[arg-type]
    ))
    match = re.search(r"\{.*\}", reply, re.DOTALL)
    if not match:
        raise RuntimeError(f"judge returned no JSON:\n{reply[:1000]}")
    verdict = json.loads(match.group())
    if verdict.get("best") not in renders:
        raise RuntimeError(f"judge picked unknown candidate: {verdict.get('best')!r}")
    return verdict


def run(prompt: str, *, n: int = 4, out_dir: Path | str | None = None, seed: int = 0) -> Path:
    """The whole pipeline. Returns the path of the winning mesh."""
    out = Path(out_dir) if out_dir is not None else OUTPUT_DIR / slugify(prompt)
    out.mkdir(parents=True, exist_ok=True)
    gpu = GPU(_judge_tenants())
    gpu.guard()

    subject = generate_subject(prompt, out, gpu, seed=seed)
    meshes = reconstruct_candidates(subject, out, gpu, n=n)
    if not meshes:
        raise RuntimeError("no candidate survived reconstruction")
    renders = render_candidates(meshes, out)
    if not renders:
        raise RuntimeError("no candidate survived rendering")

    verdict = judge(prompt, subject, renders, gpu)
    best = out / "best.glb"
    shutil.copyfile(meshes[verdict["best"]], best)
    (out / "selection.json").write_text(json.dumps(
        {"prompt": prompt, "winner": verdict["best"],
         "mesh": str(best), **verdict}, indent=2) + "\n")
    print(f"[select] winner: {verdict['best']} -> {best}")
    for name in verdict.get("ranking", []):
        print(f"  {name}: {verdict.get('verdicts', {}).get(name, '')}")
    return best


def run_many(prompts: list[str], *, n: int = 4, seed: int = 0) -> dict[str, Path]:
    """The pipeline over several subjects, one card-swap per stage.

    `run()` per prompt would swap servers three times per object; here every
    subject is drawn under one image hold, every candidate reconstructed in one
    TRELLIS batch, and every contest judged under one llm hold. The stages
    stay resumable per subject exactly as in `run()`.
    """
    gpu = GPU(_judge_tenants())
    gpu.guard()
    outs = {p: OUTPUT_DIR / slugify(p) for p in prompts}
    for out in outs.values():
        out.mkdir(parents=True, exist_ok=True)

    if any(not (o / "subject.png").exists() for o in outs.values()):
        with gpu.hold("image"):
            images = ImageModel()
            for prompt, out in outs.items():
                subject = out / "subject.png"
                if not subject.exists():
                    images.generate(
                        f"{prompt}. {SUBJECT_STYLE}",
                        subject, width=1024, height=1024, seed=seed, cutout=True,
                    )
                    print(f"[select] drew {subject}")

    # one batch across every subject: candidate links land per-subject, but the
    # worker loads the pipeline once for all of them
    batch: list[Path] = []
    for out in outs.values():
        link_dir = out / "candidates"
        link_dir.mkdir(exist_ok=True)
        for i in range(n):
            link = link_dir / f"cand_{i:02d}.png"
            if not link.exists():
                link.hardlink_to(out / "subject.png")
            if not (out / "meshes" / f"cand_{i:02d}.glb").exists():
                batch.append(link)
    if batch:
        with gpu.hold("mesh"):
            model = MeshModel(
                pipeline=PIPELINE,
                decimation_target=DECIMATION_TARGET,
                texture_size=TEXTURE_SIZE,
            )
            for out in outs.values():
                wanted = [p for p in batch if p.parent == out / "candidates"]
                if wanted:
                    model.reconstruct(wanted, out / "meshes")

    per_subject: dict[str, tuple[dict[str, Path], dict[str, Path]]] = {}
    for prompt, out in outs.items():
        meshes = {
            f"cand_{i:02d}": out / "meshes" / f"cand_{i:02d}.glb"
            for i in range(n)
            if (out / "meshes" / f"cand_{i:02d}.glb").exists()
        }
        if not meshes:
            print(f"[select] {prompt!r}: no candidate survived reconstruction")
            continue
        renders = render_candidates(meshes, out)
        if renders:
            per_subject[prompt] = (meshes, renders)

    best: dict[str, Path] = {}
    with gpu.hold("llm"):
        harness = LLMHarness(LLM_ENDPOINT, model=LLM_MODEL, system=JUDGE_SYSTEM)
        for prompt, (meshes, renders) in per_subject.items():
            out = outs[prompt]
            selection = out / "selection.json"
            if not selection.exists():
                verdict = _ask_judge(harness, prompt, out / "subject.png", renders)
                shutil.copyfile(meshes[verdict["best"]], out / "best.glb")
                selection.write_text(json.dumps(
                    {"prompt": prompt, "winner": verdict["best"],
                     "mesh": str(out / "best.glb"), **verdict}, indent=2) + "\n")
            verdict = json.loads(selection.read_text())
            best[prompt] = out / "best.glb"
            print(f"[select] {prompt!r}: {verdict['winner']}")
    return best


def refine_winners(
    out_dirs: list[Path],
    *,
    budgets: dict[str, int] | None = None,
    name: str = "refined",
) -> dict[Path, Path]:
    """Re-reconstruct each contest's winner at full quality.

    The cheap pass and this one share the image and — because the worker
    derives the seed from the filename, which is unchanged — the seed, so the
    full-quality sample generally lands in the same mode the judge picked and
    comes back as a detailed version of it rather than a new roll. Only the
    pipeline changes: '1024_cascade', 50k triangles, 1024 texture.

    `budgets` maps an output directory's name to a triangle budget for its
    winner; directories it does not name get worldclaw's 50k default. The
    budget is applied inside TRELLIS before UV unwrap and bake, so a 2k shrub
    is unwrapped for its own topology rather than decimated after the fact.
    `name` names the result (`<name>.glb` beside `best.glb`), so differently
    budgeted refinements can coexist.
    """
    gpu = GPU(_judge_tenants())
    gpu.guard()
    wanted: list[tuple[Path, Path]] = []  # (out_dir, winner image)
    for out in out_dirs:
        selection = out / "selection.json"
        if not selection.exists() or (out / f"{name}.glb").exists():
            continue
        winner = json.loads(selection.read_text())["winner"]
        wanted.append((out, out / "candidates" / f"{winner}.png"))
    made: dict[Path, Path] = {}
    if wanted:
        with gpu.hold("mesh"):
            model = MeshModel()  # worldclaw defaults: 1024_cascade, 50k, 1024
            for out, image in wanted:
                budget = (budgets or {}).get(out.name)
                produced = model.reconstruct(
                    [image], out / name,
                    targets={image.stem: budget} if budget else None,
                )
                glb = produced.get(str(image))
                if glb is not None:
                    shutil.copyfile(glb, out / f"{name}.glb")
                    made[out] = out / f"{name}.glb"
                    print(f"[select] {name} {out.name} ({budget or 50000} tris)")
    for out in out_dirs:
        if (out / f"{name}.glb").exists():
            made[out] = out / f"{name}.glb"
    return made


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("prompt", help="what to draw and reconstruct")
    parser.add_argument("--n", type=int, default=4, help="candidate count")
    parser.add_argument("--seed", type=int, default=0, help="image seed")
    parser.add_argument("--out", type=Path, default=None, help="output directory")
    arguments = parser.parse_args()
    run(arguments.prompt, n=arguments.n, out_dir=arguments.out, seed=arguments.seed)


if __name__ == "__main__":
    main()
