"""Post-process a rendered "pixel art" sprite into REAL pixel art: one pixel pitch, a small palette,
hard alpha. Diffusion pixel art has no grid; nearest-neighbour drawing at 40 px then samples noise.

usage: python pixfix.py <arm> [--h 96] [--colors 32]   -> arms/<arm>+px<h>/<id>.png
Works on the autocropped render so the pitch is relative to the SUBJECT, not the 1024 frame.
"""
import json, sys
from pathlib import Path
from PIL import Image

HERE = Path(__file__).parent
PROMPTS = json.load(open(HERE / "prompts.json"))


def pixfix(im, target_h=96, colors=32, up=8):
    im = im.convert("RGBA")
    scale = target_h / im.height
    w = max(1, round(im.width * scale))
    small = im.resize((w, target_h), Image.BOX)
    a = small.split()[-1].point(lambda v: 255 if v >= 128 else 0)
    rgb = small.convert("RGB")
    # quantize only the opaque pixels' colours; transparent pixels would waste palette slots
    q = rgb.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
    q.putalpha(a)
    return q.resize((w * up, target_h * up), Image.NEAREST)


def main():
    arm = sys.argv[1]
    h = int(sys.argv[sys.argv.index("--h") + 1]) if "--h" in sys.argv else 96
    colors = int(sys.argv[sys.argv.index("--colors") + 1]) if "--colors" in sys.argv else 32
    src = HERE / "arms" / arm
    out = HERE / "arms" / f"{arm}+px{h}"; out.mkdir(parents=True, exist_ok=True)
    for p in PROMPTS:
        f = src / f"{p['id']}.crop.png"
        if not f.exists():
            continue
        pixfix(Image.open(f), h, colors).save(out / f"{p['id']}.png")
    print(out)


if __name__ == "__main__":
    main()
