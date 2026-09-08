"""Round 6: prod res (48px/cell) + feathered region masks + tuned material phrases.

Full chain per map: fine-jitter guide -> regional 0.55 (feathered masks) -> blend 0.35.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

import run_ground as g1
from run_ground import NEGATIVE, upload, run_wf, workflow, MAPS
from run_ground3 import fine_only
from run_ground4 import regional_workflow

CELL = 48

WORDS2 = {
    "grass": "soft green meadow grass, small tufts",
    "sand": "pale beige sand beach, subtle ripples, light warm tone",
    "water": "calm sea water, deep teal blue, gentle ripples, soft foam near the shore",
    "pavement": "weathered stone dock planks and paving",
    "stone": "weathered laid stone paving",
    "rock": "rough gray rock",
    "dirt": "packed earth path",
    "path": "packed earth path",
    "forest": "dense forest canopy, individual treetops",
    "tree": "dense forest canopy, individual treetops",
    "floor": "worn flagstone dungeon floor slabs",
    "wall": "dark rough dungeon stone wall",
    "gold": "gleaming gold coins treasure floor",
    "dark": "dark shadowed stone",
    "mud": "wet brown earth bank",
}


def guide_image(m):
    grid = m["grid"]
    colors = {t["symbol"]: t["color"] for t in m["terrain"]}
    h, w = len(grid), len(grid[0])
    img = Image.new("RGB", (w * CELL, h * CELL))
    d = ImageDraw.Draw(img)
    for r in range(h):
        for c in range(w):
            d.rectangle([c * CELL, r * CELL, (c + 1) * CELL - 1, (r + 1) * CELL - 1],
                        fill=colors.get(grid[r][c], "#ff00ff"))
    return img


def region_word(name):
    n = name.lower()
    for key, phrase in WORDS2.items():
        if key in n:
            return phrase
    return n


def masks_feathered(m):
    grid = m["grid"]
    h, w = len(grid), len(grid[0])
    out = []
    for t in m["terrain"]:
        sym = t["symbol"]
        a = np.zeros((h, w), dtype=np.uint8)
        for r in range(h):
            for c in range(w):
                if grid[r][c] == sym:
                    a[r][c] = 255
        if a.any():
            big = Image.fromarray(np.kron(a, np.ones((CELL, CELL), dtype=np.uint8)), "L")
            big = big.filter(ImageFilter.GaussianBlur(CELL // 2)).convert("RGB")
            out.append((t, big))
    return out


def main():
    outdir = Path("output/ground6")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        flat = guide_image(m)
        g = fine_only(flat)
        up = f"lab_g6_{place}_{seed}.png"
        upload(g, up)
        mask_names = []
        for t, mask_img in masks_feathered(m):
            mn = f"lab_g6_mask_{place}_{seed}_{t['symbol']}.png"
            upload(mask_img, mn)
            mask_names.append((mn, region_word(t["name"])))
        regional = run_wf(regional_workflow(up, mask_names, 0.55, seed=7))
        regional.save(outdir / f"{place}_regional.png")
        up2 = f"lab_g6_blendin_{place}_{seed}.png"
        upload(regional, up2)
        words = ", ".join(dict.fromkeys(region_word(t["name"]) for t in m["terrain"]))
        prompt = (f"top-down painted 2d game terrain map, {words}, soft painterly texture, "
                  "unified soft lighting, seamless natural transitions, no objects, empty ground")
        final = run_wf(workflow(up2, prompt, 0.35, seed=7))
        final.save(outdir / f"{place}_final.png")
        old = Image.open(f"output/ground5/{place}_blend_dn35.png")
        w, h = 640, 480
        pad = 6
        sheet = Image.new("RGB", (pad + 3 * (w + pad), h + 36), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 3), f"{place} — old final vs prod-res feathered final", fill="#ffffff")
        for i, (im, lab) in enumerate([(flat, "guide"), (old, "round5 final (32px)"),
                                       (final, "round6 final (48px, feathered)")]):
            x = pad + i * (w + pad)
            sheet.paste(im.resize((w, h)), (x, 18))
            d.text((x, h + 21), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print(place, "done", final.size)


if __name__ == "__main__":
    main()
