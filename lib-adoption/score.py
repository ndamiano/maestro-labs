"""What each finished build did about sound and about paths."""
import json
import re
import sys
from pathlib import Path

GAMES = Path("/home/nick/Documents/ai-agent-test/runtime/games")
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from maestro.codegen.tools import _dead_refs  # noqa: E402

VEND = {"three.module.js", "world.js", "GLTFLoader.js", "BufferGeometryUtils.js"}


def own_files(g):
    return [f for f in list(g.rglob("*.js")) + list(g.rglob("*.html"))
            if "lib" not in f.parts and f.name not in VEND]


def score(run_id):
    g = GAMES / run_id
    if not g.exists():
        return {"run_id": run_id, "staged": False}
    files = own_files(g)
    text = "\n".join(f.read_text(errors="replace") for f in files)
    return {
        "run_id": run_id,
        "staged": True,
        "files": len(files),
        "imports_lib_audio": bool(re.search(r"lib/audio", text)),
        "own_audio_context": len(re.findall(r"new (?:window\.)?(?:webkit)?AudioContext|webkitAudioContext", text)),
        "own_oscillators": len(re.findall(r"createOscillator|createBiquadFilter|createBufferSource", text)),
        "audio_param_assigned": re.findall(r"\.(?:Q|frequency|gain|detune|playbackRate)\s*=\s*(?!=)[^;\n]{0,40}", text)[:5],
        "uses_new_lib": sorted({n for n in ("sound(", "noise(", "seq(", "loop(") if n in text}),
        "dead_refs": [f"{f.relative_to(g)} -> {r}" for f in files for r in _dead_refs(f, f.read_text(errors="replace"), g, set())],
        "subdir_code": sorted({f.parts[len(g.parts)] for f in files if len(f.parts) > len(g.parts) + 1}),
    }


if __name__ == "__main__":
    src = Path(sys.argv[1])
    for line in src.read_text().splitlines():
        rec = json.loads(line)
        print(json.dumps({**{k: rec[k] for k in ("arm", "ask", "result")}, **score(rec["run_id"])}))
