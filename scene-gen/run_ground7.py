"""Round 7: palette-corrected guides — terrain-name-keyed colors override LLM hex.

Guide color anchors final hue at 0.55 denoise, so hue is fixed in the guide,
not the prompt. Full chain at prod res.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

from run_ground import upload, run_wf, workflow
from run_ground3 import fine_only
from run_ground4 import regional_workflow
from run_ground6 import CELL, WORDS2, region_word, masks_feathered, MAPS

PALETTE = {
    "grass": "#6da24c",
    "sand": "#dcc998",
    "water": "#39708f",
    "pavement": "#8d8578",
    "stone": "#8d8578",
    "rock": "#7a7468",
    "dirt": "#8a6f4d",
    "path": "#8a6f4d",
    "forest": "#3c6631",
    "tree": "#3c6631",
    "floor": "#7d7668",
    "wall": "#3f3b34",
    "gold": "#d9a93c",
    "dark": "#332f2a",
    "mud": "#6d5334",
}


def curated_color(t):
    n = t["name"].lower()
    for key, hexcol in PALETTE.items():
        if key in n:
            return hexcol
    return t["color"]


def guide_image(m):
    grid = m["grid"]
    colors = {t["symbol"]: curated_color(t) for t in m["terrain"]}
    h, w = len(grid), len(grid[0])
    img = Image.new("RGB", (w * CELL, h * CELL))
    d = ImageDraw.Draw(img)
    for r in range(h):
        for c in range(w):
            d.rectangle([c * CELL, r * CELL, (c + 1) * CELL - 1, (r + 1) * CELL - 1],
                        fill=colors.get(grid[r][c], "#ff00ff"))
    return img


def main():
    outdir = Path("output/ground7")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        flat = guide_image(m)
        g = fine_only(flat)
        up = f"lab_g7_{place}_{seed}.png"
        upload(g, up)
        mask_names = []
        for t, mask_img in masks_feathered(m):
            mn = f"lab_g7_mask_{place}_{seed}_{t['symbol']}.png"
            upload(mask_img, mn)
            mask_names.append((mn, region_word(t["name"])))
        regional = run_wf(regional_workflow(up, mask_names, 0.55, seed=7))
        up2 = f"lab_g7_blendin_{place}_{seed}.png"
        upload(regional, up2)
        words = ", ".join(dict.fromkeys(region_word(t["name"]) for t in m["terrain"]))
        prompt = (f"top-down painted 2d game terrain map, {words}, soft painterly texture, "
                  "unified soft lighting, seamless natural transitions, no objects, empty ground")
        final = run_wf(workflow(up2, prompt, 0.35, seed=7))
        final.save(outdir / f"{place}_final.png")
        old = Image.open(f"output/ground6/{place}_final.png")
        w, h = 640, 480
        pad = 6
        sheet = Image.new("RGB", (pad + 3 * (w + pad), h + 36), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 3), f"{place} — LLM palette vs curated palette (48px chain)", fill="#ffffff")
        for i, (im, lab) in enumerate([(flat, "curated guide"), (old, "round6 (LLM colors)"),
                                       (final, "round7 (curated colors)")]):
            x = pad + i * (w + pad)
            sheet.paste(im.resize((w, h)), (x, 18))
            d.text((x, h + 21), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print(place, "done")


if __name__ == "__main__":
    main()
