"""Top-down sprite set + composed map + whole-map unify pass."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from run_ground import upload, run_wf, workflow
from run_objects2 import run_wf_rgba
from run_spritebench import qwen_wf

STYLE_TD = ("Single object, complete, centred, filling the frame, seen DIRECTLY FROM ABOVE — "
            "a true top-down overhead view, the kind used for 2d game maps: a building shows "
            "its roof, a boat shows its deck, a creature shows its back and head. Plain flat "
            "mid-grey background. Stylized painterly cartoon game asset with clean ink "
            "outlines, chunky simplified shapes, flat painterly colour, soft texture, "
            "no fine detail.")
NEG_TD = ("blurry, low detail, cropped, cut off, partial object, multiple objects, scenery, "
          "landscape, ground, floor, horizon, cast shadow, text, watermark, side view, "
          "front view, three-quarter view, perspective, photograph, photorealistic")

ITEMS = {
    "cabin": "a small weathered wooden fishing cabin with a steep shingled roof and a stone chimney",
    "boat": "a small wooden rowing boat with two bench seats and oars",
    "net": "a bundled brown fishing net with cork floats",
    "fisherman": "an old fisherman in a yellow raincoat holding a fishing rod",
    "seagull": "a white seagull with grey wings",
}
SYM = {"h": "cabin", "b": "boat", "n": "net", "f": "fisherman", "s": "seagull"}
SIZES = {"cabin": 3.0, "boat": 1.8, "net": 1.2, "fisherman": 1.2, "seagull": 0.9}
CELL = 48


def td_wf(desc, seed):
    wf = qwen_wf(desc, seed)
    wf["p"]["inputs"]["text"] = desc + " " + STYLE_TD
    wf["n"]["inputs"]["text"] = NEG_TD
    return wf


def main():
    outdir = Path("output/topdown")
    outdir.mkdir(parents=True, exist_ok=True)
    sprites = {}
    for name, desc in ITEMS.items():
        im = run_wf_rgba(td_wf(desc, seed=5))
        bbox = im.getbbox()
        im = im.crop(bbox) if bbox else im
        im.save(outdir / f"{name}.png")
        sprites[name] = im
        print("sprite", name, "done")

    m = json.load(open("output/fishing_village/seed2_map.json"))
    ground = Image.open("output/ground9/fishing_village_final.png").convert("RGBA")
    for p in sorted(m["placements"], key=lambda q: q["row"]):
        name = SYM.get(p["symbol"])
        if name is None:
            continue  # pier: the pavement region IS the pier
        sp = sprites[name]
        target = int(SIZES[name] * CELL)
        scale = target / max(sp.width, sp.height)
        s = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))))
        cx, cy = int((p["col"] + 0.5) * CELL), int((p["row"] + 0.5) * CELL)
        sh = Image.new("RGBA", ground.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        d.ellipse([cx - s.width // 2 + 3, cy - s.height // 2 + 6,
                   cx + s.width // 2 + 3, cy + s.height // 2 + 6], fill=(0, 0, 0, 60))
        sh = sh.filter(ImageFilter.GaussianBlur(4))
        ground = Image.alpha_composite(ground, sh)
        ground.alpha_composite(s, (cx - s.width // 2, cy - s.height // 2))
    composed = ground.convert("RGB")
    composed.save(outdir / "composed.png")

    spec = json.load(open("output/fishing_village/seed2_paintspec.json"))
    words = ", ".join(dict.fromkeys(s["phrase"] for s in spec.values()))
    up = "lab_unify_fv.png"
    upload(composed, up)
    for dn in (0.2, 0.3):
        prompt = ("top-down painted 2d game map of a fishing village, wooden cabins, boats, "
                  f"{words}, one unified painterly illustration, consistent soft lighting, "
                  "clean ink outlines")
        img = run_wf(workflow(up, prompt, dn, seed=7))
        img.save(outdir / f"unified_dn{int(dn*100)}.png")
        print("unify", dn, "done")


if __name__ == "__main__":
    main()
