"""Round 4: regional prompting — per-terrain prompt masked to its own cells.

ConditioningSetMask per terrain, combined, one sampler pass over the fine-jitter
guide at 0.55. Compare against round 3's global-prompt winner.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from run_ground import CELL, WORDS, NEGATIVE, guide_image, terrain_prompt, upload, run_wf, MAPS
from run_ground3 import fine_only

DENOISE = 0.55


def region_word(name):
    n = name.lower()
    for key, phrase in WORDS.items():
        if key in n:
            return phrase
    return n


def masks_by_terrain(m):
    grid = m["grid"]
    h, w = len(grid), len(grid[0])
    out = {}
    for t in m["terrain"]:
        sym = t["symbol"]
        a = np.zeros((h, w), dtype=np.uint8)
        for r in range(h):
            for c in range(w):
                if grid[r][c] == sym:
                    a[r][c] = 255
        if a.any():
            big = np.kron(a, np.ones((CELL, CELL), dtype=np.uint8))
            out[sym] = (t, Image.fromarray(big, "L").convert("RGB"))
    return out


def regional_workflow(init_name, mask_names, denoise, seed):
    wf = {
        "ck": {"class_type": "CheckpointLoaderSimple",
               "inputs": {"ckpt_name": "DreamShaperXL_Turbo_v2_1.safetensors"}},
        "li": {"class_type": "LoadImage", "inputs": {"image": init_name}},
        "n": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["ck", 1]}},
        "ve": {"class_type": "VAEEncode", "inputs": {"pixels": ["li", 0], "vae": ["ck", 2]}},
        "vd": {"class_type": "VAEDecode", "inputs": {"samples": ["k", 0], "vae": ["ck", 2]}},
        "s": {"class_type": "SaveImage",
              "inputs": {"images": ["vd", 0], "filename_prefix": "lab_ground4"}},
    }
    prev = None
    for i, (mask_name, phrase) in enumerate(mask_names):
        wf[f"lm{i}"] = {"class_type": "LoadImage", "inputs": {"image": mask_name}}
        wf[f"m{i}"] = {"class_type": "ImageToMask",
                       "inputs": {"image": [f"lm{i}", 0], "channel": "red"}}
        wf[f"p{i}"] = {"class_type": "CLIPTextEncode",
                       "inputs": {"text": f"top-down painted 2d game terrain, {phrase}, "
                                          "soft painterly texture, no objects, empty ground",
                                  "clip": ["ck", 1]}}
        wf[f"cm{i}"] = {"class_type": "ConditioningSetMask",
                        "inputs": {"conditioning": [f"p{i}", 0], "mask": [f"m{i}", 0],
                                   "strength": 1.0, "set_cond_area": "default"}}
        if prev is None:
            prev = f"cm{i}"
        else:
            wf[f"cc{i}"] = {"class_type": "ConditioningCombine",
                            "inputs": {"conditioning_1": [prev, 0],
                                       "conditioning_2": [f"cm{i}", 0]}}
            prev = f"cc{i}"
    wf["k"] = {"class_type": "KSampler",
               "inputs": {"seed": seed, "steps": 8, "cfg": 2.5, "sampler_name": "dpmpp_sde",
                          "scheduler": "karras", "denoise": denoise, "model": ["ck", 0],
                          "positive": [prev, 0], "negative": ["n", 0],
                          "latent_image": ["ve", 0]}}
    return wf


def main():
    outdir = Path("output/ground4")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        flat = guide_image(m)
        g = fine_only(flat)
        up = f"lab_g4_{place}_{seed}.png"
        upload(g, up)
        mask_names = []
        for sym, (t, mask_img) in masks_by_terrain(m).items():
            mn = f"lab_g4_mask_{place}_{seed}_{sym}.png"
            upload(mask_img, mn)
            mask_names.append((mn, region_word(t["name"])))
        img = run_wf(regional_workflow(up, mask_names, DENOISE, seed=7))
        img.save(outdir / f"{place}_regional_dn55.png")
        prev3 = Image.open(f"output/ground3/{place}_fine_dn55.png")
        w, h = img.width // 2, img.height // 2
        pad = 6
        sheet = Image.new("RGB", (pad + 3 * (w + pad), h + 36), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 3), f"{place} — global vs regional prompts (fine 0.55)", fill="#ffffff")
        for i, (im, lab) in enumerate([(flat, "guide"), (prev3, "global 0.55"),
                                       (img, "regional 0.55")]):
            x = pad + i * (w + pad)
            sheet.paste(im.resize((w, h)), (x, 18))
            d.text((x, h + 21), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print(place, "done")


if __name__ == "__main__":
    main()
