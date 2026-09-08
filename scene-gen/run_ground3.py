"""Round 3: happy medium — texture inside regions, boundaries true to the grid.

Noisy guide at lower denoise (0.45/0.5/0.55), plus fine-jitter-only guide
(no coarse blotch) at 0.5/0.55/0.6.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from run_ground import guide_image, terrain_prompt, upload, workflow, run_wf, MAPS
from run_ground2 import jittered


def fine_only(guide, strength=22):
    a = np.asarray(guide).astype(np.int16)
    rng = np.random.default_rng(7)
    return Image.fromarray(
        np.clip(a + rng.integers(-strength, strength + 1, a.shape), 0, 255).astype(np.uint8))


VARIANTS = [
    ("noisy", jittered, [0.45, 0.5, 0.55]),
    ("fine", fine_only, [0.5, 0.55, 0.6]),
]


def main():
    outdir = Path("output/ground3")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        flat = guide_image(m)
        prompt = terrain_prompt(m)
        results, labels = [flat], ["guide"]
        for gname, fn, dns in VARIANTS:
            g = fn(flat)
            up = f"lab_g3_{gname}_{place}_{seed}.png"
            upload(g, up)
            for dn in dns:
                img = run_wf(workflow(up, prompt, dn, seed=7))
                img.save(outdir / f"{place}_{gname}_dn{int(dn * 100)}.png")
                results.append(img)
                labels.append(f"{gname} {dn}")
        w, h = results[0].width // 2, results[0].height // 2
        pad = 6
        sheet = Image.new("RGB", (pad + len(results) * (w + pad), h + 36), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 3), f"{place} seed {seed} — round 3", fill="#ffffff")
        for i, (img, lab) in enumerate(zip(results, labels)):
            x = pad + i * (w + pad)
            sheet.paste(img.resize((w, h)), (x, 18))
            d.text((x, h + 21), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print(place, "done")


if __name__ == "__main__":
    main()
