"""Draw the five subjects in five image styles, cut out on alpha, for a TRELLIS style grid.

Styles A-D go through the lab's Qwen-Image path (worldclaw ImageModel, cutout). Style E is the
PRODUCT recipe: maestro's NetaYume item workflow exactly as build_image_job emits it, left unmatted
so TRELLIS's own BiRefNet cuts it out as it would any product render.
"""
import json, sys, os, time
sys.path.insert(0, "/home/nick/Documents/Labs/worldclaw")
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from pathlib import Path
from worldclaw.backends.images import ImageModel
from tools.comfyui_tools import build_image_job

O = Path("/home/nick/output/img2threed/styles"); O.mkdir(exist_ok=True)
SUBJECTS = {
    "wooden-watchtower": "a wooden watchtower",
    "rustic-stone-cottage": "a rustic stone cottage with a thatched roof",
    "weathered-wooden-barrel": "a weathered wooden barrel",
    "broken-wooden-cart": "a broken wooden cart",
    "gnarled-old-oak-tree": "a gnarled old oak tree",
}
FRAMING = ("Single object, complete and unobstructed, centred and filling the frame. "
           "Three-quarter view from slightly above, showing its depth and thickness. "
           "Plain flat mid-grey background. ")
STYLES = {
    "A-photo": FRAMING + "Soft even studio lighting from several directions. Sharp focus, high detail, photographic.",
    "B-lowpoly": FRAMING + "Low-poly stylized game asset, flat colours, clean faceted shapes, simple bold silhouette, soft even lighting, 3D render.",
    "C-handpainted": FRAMING + "Hand-painted stylized game asset, painterly textures, chunky exaggerated proportions, rich saturated colours, soft even lighting, 3D render.",
    "D-cgrender": FRAMING + "Clean 3D render, PBR materials, crisp geometry, soft even studio lighting, high detail, no film grain, Blender render.",
}
NEG = ("blurry, low detail, cropped, cut off, partial object, multiple objects, scenery, landscape, "
       "ground, floor, horizon, cast shadow, text, watermark")

im = ImageModel()
while not im.up():
    time.sleep(3)
for n, desc in SUBJECTS.items():
    for s, style in STYLES.items():
        out = O / f"{n}.{s}.png"
        if out.exists():
            continue
        im.generate(f"{desc}. {style}", out, negative=NEG, width=1024, height=1024, seed=7, cutout=True)
        print(out.name, flush=True)
    out = O / f"{n}.E-product.png"
    if not out.exists():
        job = build_image_job(desc, "sprite")
        imgs = im.run(job["workflow_override"])
        out.write_bytes(im._view(imgs[0]))
        print(out.name, flush=True)
