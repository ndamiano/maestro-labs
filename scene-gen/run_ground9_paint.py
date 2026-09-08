"""Phase 2: paint the full chain from the LLM-authored paintspec — no tables."""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from run_ground import upload, run_wf, workflow
from run_ground3 import fine_only
from run_ground4 import regional_workflow
from run_ground6 import CELL
from run_ground9_phrases import MAPS


def erosion_depth(a):
    b = a.astype(bool)
    d = 0
    while b.any():
        b = (b & np.roll(b, 1, 0) & np.roll(b, -1, 0)
             & np.roll(b, 1, 1) & np.roll(b, -1, 1))
        d += 1
        if d > 32:
            break
    return d


def main():
    outdir = Path("output/ground9")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        spec = json.load(open(f"output/{place}/seed{seed}_paintspec.json"))
        grid = m["grid"]
        h, w = len(grid), len(grid[0])
        colors = {t["symbol"]: spec[t["name"]]["color"] for t in m["terrain"]}
        flat = Image.new("RGB", (w * CELL, h * CELL))
        d = ImageDraw.Draw(flat)
        for r in range(h):
            for c in range(w):
                d.rectangle([c * CELL, r * CELL, (c + 1) * CELL - 1, (r + 1) * CELL - 1],
                            fill=colors.get(grid[r][c], "#ff00ff"))
        up = f"lab_g9_{place}.png"
        upload(fine_only(flat), up)
        mask_names = []
        for t in m["terrain"]:
            a = np.zeros((h, w), dtype=np.uint8)
            for r in range(h):
                for c in range(w):
                    if grid[r][c] == t["symbol"]:
                        a[r][c] = 255
            if not a.any():
                continue
            radius = min(CELL // 2, max(0, (erosion_depth(a) - 1) * CELL // 2))
            big = Image.fromarray(np.kron(a, np.ones((CELL, CELL), dtype=np.uint8)), "L")
            if radius > 1:
                big = big.filter(ImageFilter.GaussianBlur(radius))
            mn = f"lab_g9_mask_{place}_{t['symbol']}.png"
            upload(big.convert("RGB"), mn)
            mask_names.append((mn, spec[t["name"]]["phrase"]))
        regional = run_wf(regional_workflow(up, mask_names, 0.55, seed=7))
        up2 = f"lab_g9_blendin_{place}.png"
        upload(regional, up2)
        words = ", ".join(dict.fromkeys(s["phrase"] for s in spec.values()))
        prompt = (f"top-down painted 2d game terrain map, {words}, soft painterly texture, "
                  "unified soft lighting, seamless natural transitions, no objects, empty ground")
        final = run_wf(workflow(up2, prompt, 0.35, seed=7))
        final.save(outdir / f"{place}_final.png")
        old = Image.open(f"output/ground7/{place}_final.png")
        W, H = 640, 480
        pad = 6
        sheet = Image.new("RGB", (pad + 3 * (W + pad), H + 36), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 3), f"{place} — hand table vs LLM paintspec", fill="#ffffff")
        for i, (im, lab) in enumerate([(flat, "LLM guide"), (old, "round7 (hand table)"),
                                       (final, "round9 (LLM spec)")]):
            x = pad + i * (W + pad)
            sheet.paste(im.resize((W, H)), (x, 18))
            d.text((x, H + 21), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print(place, "done")


if __name__ == "__main__":
    main()
