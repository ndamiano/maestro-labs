"""Ground pass round 2: noisy guides so texture emerges at structure-safe denoise.

Variants: flat guide vs per-pixel jittered guide, denoise 0.6/0.65/0.7.
"""
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from run_ground import (CELL, guide_image, terrain_prompt, upload, workflow, run_wf,
                        MAPS)

DENOISES = [0.6, 0.65, 0.7]


def jittered(guide, strength=18, blotch=8):
    """Per-pixel color noise + coarse blotches: something for the sampler to grow."""
    a = np.asarray(guide).astype(np.int16)
    rng = np.random.default_rng(7)
    fine = rng.integers(-strength, strength + 1, a.shape)
    h, w = a.shape[:2]
    coarse = rng.integers(-strength, strength + 1, (h // blotch + 1, w // blotch + 1, 3))
    coarse = np.kron(coarse, np.ones((blotch, blotch, 1), dtype=np.int16))[:h, :w]
    return Image.fromarray(np.clip(a + fine + coarse, 0, 255).astype(np.uint8))


def main():
    outdir = Path("output/ground2")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        flat = guide_image(m)
        noisy = jittered(flat)
        prompt = terrain_prompt(m)
        results, labels = [flat], ["flat guide"]
        for gname, g in [("flat", flat), ("noisy", noisy)]:
            up = f"lab_g2_{gname}_{place}_{seed}.png"
            upload(g, up)
            for dn in DENOISES:
                img = run_wf(workflow(up, prompt, dn, seed=7))
                img.save(outdir / f"{place}_{gname}_dn{int(dn * 100)}.png")
                results.append(img)
                labels.append(f"{gname} {dn}")
        w = results[0].width // 2
        h = results[0].height // 2
        pad = 6
        sheet = Image.new("RGB", (pad + len(results) * (w + pad), h + 36), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 3), f"{place} seed {seed} — guide variant x denoise", fill="#ffffff")
        for i, (img, lab) in enumerate(zip(results, labels)):
            x = pad + i * (w + pad)
            sheet.paste(img.resize((w, h)), (x, 18))
            d.text((x, h + 21), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print(place, "done")


if __name__ == "__main__":
    main()
