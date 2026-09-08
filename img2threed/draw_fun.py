"""Six print-worthy subjects through the PRODUCT mesh recipe (build_image_job kind=mesh)."""
import sys, time
sys.path.insert(0, "/home/nick/Documents/Labs/worldclaw"); sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from pathlib import Path
from worldclaw.backends.images import ImageModel
from tools.comfyui_tools import build_image_job
O = Path("/home/nick/output/img2threed/fun"); O.mkdir(exist_ok=True)
SUBJECTS = {
    "dragon-on-rock": "a small dragon curled up asleep on a boulder, wings folded",
    "knight-bust": "a bust of an armoured knight with a plumed helmet, on a square plinth",
    "steampunk-airship": "a steampunk airship with a wooden hull, brass fittings and a balloon envelope",
    "octopus-teapot": "a teapot shaped like a cartoon octopus, tentacles forming the handle and spout",
    "gargoyle": "a stone gargoyle crouched on a pedestal, wings half open",
    "chess-knight": "an ornate chess knight piece carved as a rearing horse with flowing mane",
}
im = ImageModel()
while not im.up(): time.sleep(3)
for n, desc in SUBJECTS.items():
    out = O / f"{n}.png"
    if out.exists(): continue
    wf = build_image_job(desc, "mesh")["workflow_override"]
    out.write_bytes(im._view(im.run(wf)[0])); print(n, flush=True)
