"""Arm: does an anim still need its own framing clause, the way a mesh subject does?

Renders the SAME subjects through the repo's real Qwen subject graph, varying only what is
appended to the prompt. Control is exactly what prod sends today.
"""
import argparse, base64, json, sys, time, uuid, urllib.request, urllib.parse
from pathlib import Path

REPO = Path("/home/nick/Documents/ai-agent-test")
sys.path.insert(0, str(REPO / "src"))
from tools.comfyui_tools import _load_workflow, _NEGATIVE_SUBJECT  # noqa: E402

COMFY = "http://127.0.0.1:8188"
WF = REPO / "src/config/workflows/txt2img_subject.json"

# A sprite sheet is made from ONE still, so the still owes the whole body in a pose that has
# somewhere to move from. Stated as what is true, never as what to avoid.
FRAMING = (" Full body from head to feet, both feet visible and planted on the ground, standing "
           "upright in a neutral pose with arms clear of the body and space around the figure on "
           "every side. Plain flat white background, flat even lighting, no cast shadow.")

ARMS = {
    "control": lambda subj, style, view: f"{style}. {subj}, {view} view.",
    "framed":  lambda subj, style, view: f"{style}. {subj}, {view} view." + FRAMING,
    "framed_sprite": lambda subj, style, view: (
        f"{style}. Full-length game sprite of {subj}, seen from the {view}." + FRAMING),
    # The video leg feeds the still in as the FRONT facing and turns it from there, so a still
    # for facings:4 owes the camera its front whatever `view` the manifest carries.
    "front": lambda subj, style, view: (
        f"{style}. {subj}, seen from the front, facing the camera." + FRAMING),
    # A mesh is voxelised: a few pixels of daylight between arm and coat weld shut at 512^3,
    # so the mesh's own still holds the limbs clear of the body.
    "tpose": lambda subj, style, view: (
        f"{style}. {subj}, seen from the front, facing the camera, standing in a T-pose with "
        f"both arms stretched straight out horizontally to the sides at shoulder height, "
        f"palms down, legs straight and shoulder-width apart." + FRAMING),
    "apose": lambda subj, style, view: (
        f"{style}. {subj}, seen from the front, facing the camera, standing in an A-pose with "
        f"both arms held straight and angled well away from the body, a clear gap of empty "
        f"space between each arm and the torso, legs straight and shoulder-width apart." + FRAMING),
    "front_sym": lambda subj, style, view: (
        f"{style}. {subj}, seen from the front, facing the camera, head-on, "
        f"shoulders square to the camera, looking straight ahead at the viewer." + FRAMING),
}

STYLE_TACTICS = ("painted fantasy tactics style, warm parchment palette with deep teal shadows, "
                 "soft dark outlines, chunky readable shapes")
STYLE_COZY = ("hand-painted cozy storybook style, warm muted palette, soft dark outlines")

SUBJECTS = [
    ("aldric", "a young noble lord swordsman with silver-blond hair, blue and gold tabard, "
     "ornate short sword, small winged pauldrons", STYLE_TACTICS, "side"),
    ("brann", "a stout veteran knight with a horned helmet, heavy steel pauldrons, kite shield "
     "and a long lance", STYLE_TACTICS, "side"),
    ("sera", "a young mage woman with violet hooded robe, floating open tome, crackling orange "
     "arcane orb in hand", STYLE_TACTICS, "side"),
    ("cavalier", "a rider on a stocky barded warhorse, blue caparison, carrying a lance",
     STYLE_TACTICS, "side"),
    ("shopkeeper", "a cozy elderly shopkeeper with a long grey beard, half-moon spectacles, a "
     "deep plum apron over a cream shirt, rolled sleeves", STYLE_COZY, "side"),
]


def submit(wf):
    req = urllib.request.Request(f"{COMFY}/prompt",
                                 data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))["prompt_id"]


def wait(pid, timeout=600):
    end = time.time() + timeout
    while time.time() < end:
        h = json.load(urllib.request.urlopen(f"{COMFY}/history/{pid}"))
        if pid in h:
            return h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def fetch(img):
    q = urllib.parse.urlencode({k: img[k] for k in ("filename", "subfolder", "type")})
    return urllib.request.urlopen(f"{COMFY}/view?{q}").read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/home/nick/output/anim-still")
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--arms", default=",".join(ARMS))
    ap.add_argument("--subjects", default=",".join(s[0] for s in SUBJECTS))
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    arms = args.arms.split(",")
    want = set(args.subjects.split(","))
    log = []
    for sid, subj, style, view in SUBJECTS:
        if sid not in want:
            continue
        for seed_i in range(args.seeds):
            seed = 1000 + seed_i
            for arm in arms:
                prompt = ARMS[arm](subj, style, view)
                wf = _load_workflow(WF)
                wf["p"]["inputs"]["text"] = prompt
                wf["n"]["inputs"]["text"] = _NEGATIVE_SUBJECT
                wf["k"]["inputs"]["seed"] = seed
                t = time.time()
                hist = wait(submit(wf))
                imgs = [i for o in hist["outputs"].values() for i in o.get("images", [])]
                dst = out / f"{sid}_{arm}_s{seed}.png"
                dst.write_bytes(fetch(imgs[-1]))
                log.append({"subject": sid, "arm": arm, "seed": seed,
                            "seconds": round(time.time() - t, 1), "prompt": prompt,
                            "file": str(dst)})
                print(f"{sid:11s} {arm:14s} seed {seed} {log[-1]['seconds']:5.1f}s -> {dst.name}",
                      flush=True)
    (out / "log.json").write_text(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()
