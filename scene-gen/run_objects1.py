"""Objects pass 1: per-item sprites (white-bg txt2img -> chroma key) pasted at placements.

Sprite size scales with what the item is: buildings ~2.5 cells, props ~1.3, creatures ~1.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from run_ground import upload, run_wf, MAPS

CELL = 48
NEGATIVE = "photo, 3d render, text, watermark, shadow, ground, scenery, frame, border"

BIG = ("cabin", "hut", "house", "stall", "tent", "pier", "boat", "market")


def sprite_workflow(prompt, seed):
    return {
        "ck": {"class_type": "CheckpointLoaderSimple",
               "inputs": {"ckpt_name": "DreamShaperXL_Turbo_v2_1.safetensors"}},
        "p": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["ck", 1]}},
        "n": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["ck", 1]}},
        "el": {"class_type": "EmptyLatentImage",
               "inputs": {"width": 768, "height": 768, "batch_size": 1}},
        "k": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 8, "cfg": 2.5, "sampler_name": "dpmpp_sde",
                         "scheduler": "karras", "denoise": 1.0, "model": ["ck", 0],
                         "positive": ["p", 0], "negative": ["n", 0],
                         "latent_image": ["el", 0]}},
        "vd": {"class_type": "VAEDecode", "inputs": {"samples": ["k", 0], "vae": ["ck", 2]}},
        "s": {"class_type": "SaveImage",
              "inputs": {"images": ["vd", 0], "filename_prefix": "lab_sprite"}},
    }


def keyed(img, thresh=235):
    """White background -> alpha, then crop to subject."""
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    white = (a > thresh).all(axis=2)
    # flood from the border so white inside the subject survives
    from collections import deque
    h, w = white.shape
    bg = np.zeros_like(white)
    dq = deque()
    for x in range(w):
        for y in (0, h - 1):
            if white[y, x] and not bg[y, x]:
                bg[y, x] = True
                dq.append((y, x))
    for y in range(h):
        for x in (0, w - 1):
            if white[y, x] and not bg[y, x]:
                bg[y, x] = True
                dq.append((y, x))
    while dq:
        y, x = dq.popleft()
        for ny, nx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
            if 0 <= ny < h and 0 <= nx < w and white[ny, nx] and not bg[ny, nx]:
                bg[ny, nx] = True
                dq.append((ny, nx))
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    rgba = np.dstack([a.astype(np.uint8), alpha])
    out = Image.fromarray(rgba, "RGBA")
    bbox = out.getbbox()
    return out.crop(bbox) if bbox else out


def item_cells(name):
    n = name.lower()
    return 2.5 if any(k in n for k in BIG) else 1.4


def main():
    outdir = Path("output/objects1")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        ground = Image.open(f"output/ground9/{place}_final.png").convert("RGBA")
        sprites = {}
        for it in m["items"]:
            prompt = (f"one {it['name']}, stylized cartoon 2d game sprite, top-down view from "
                      "directly above, chunky simplified shapes, bold colour, centered, "
                      "isolated on a plain pure white background")
            img = run_wf(sprite_workflow(prompt, seed=11))
            sp = keyed(img)
            sp.save(outdir / f"{place}_{it['symbol']}_sprite.png")
            sprites[it["symbol"]] = sp
        for p in m["placements"]:
            sp = sprites.get(p["symbol"])
            if sp is None:
                continue
            name = next(i["name"] for i in m["items"] if i["symbol"] == p["symbol"])
            target = int(item_cells(name) * CELL)
            scale = target / max(sp.width, sp.height)
            s = sp.resize((max(1, int(sp.width * scale)), max(1, int(sp.height * scale))))
            cx, cy = int((p["col"] + 0.5) * CELL), int((p["row"] + 0.5) * CELL)
            sh = Image.new("RGBA", ground.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(sh)
            d.ellipse([cx - s.width // 2, cy + s.height // 4,
                       cx + s.width // 2, cy + s.height // 2 + 6], fill=(0, 0, 0, 90))
            sh = sh.filter(ImageFilter.GaussianBlur(4))
            ground = Image.alpha_composite(ground, sh)
            ground.alpha_composite(s, (cx - s.width // 2, cy - s.height // 2))
        ground.convert("RGB").save(outdir / f"{place}_composed.png")
        print(place, "done")


if __name__ == "__main__":
    main()
