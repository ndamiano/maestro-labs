"""Ground pass: arm-1 terrain grid -> flat-color guide -> img2img -> painted ground.

Sweeps denoise so we can see where structure survives vs. texture appears.
Comfy must be up on 127.0.0.1:8188 with DreamShaperXL_Turbo_v2_1.
"""
import io
import json
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

COMFY = "http://127.0.0.1:8188"
CELL = 40
DENOISES = [0.45, 0.6, 0.75]

WORDS = {
    "grass": "lush green grass with tufts and patches",
    "sand": "warm sandy beach with ripples",
    "water": "deep blue water with gentle waves",
    "pavement": "worn stone paving",
    "stone": "worn stone paving",
    "rock": "rough gray rock",
    "dirt": "packed earth path",
    "path": "packed earth path",
    "forest": "dense dark forest canopy",
    "tree": "dense dark forest canopy",
    "floor": "dungeon stone floor slabs",
    "wall": "dark dungeon stone wall",
    "gold": "gleaming gold treasure floor",
    "dark": "dark shadowed stone",
    "mud": "wet brown mud bank",
    "palm": "tropical green palms",
    "oasis": "lush oasis greenery",
    "market": "market plaza flagstones",
    "clearing": "sunlit grassy clearing",
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


def terrain_prompt(m):
    names = [t["name"].lower() for t in m["terrain"]]
    words = []
    for n in names:
        for key, phrase in WORDS.items():
            if key in n:
                words.append(phrase)
                break
        else:
            words.append(n)
    seen = list(dict.fromkeys(words))
    return ("top-down painted 2d game terrain map, " + ", ".join(seen)
            + ", soft painterly texture, natural transitions between terrains, "
              "no objects, no buildings, empty ground")


NEGATIVE = ("buildings, houses, trees, people, objects, characters, text, watermark, "
            "blurry, photo, 3d render, grid lines")


def upload(img, name):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    body = buf.getvalue()
    boundary = "----lab"
    payload = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
        f"filename=\"{name}\"\r\nContent-Type: image/png\r\n\r\n"
    ).encode() + body + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{COMFY}/upload/image", data=payload, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}"})
    urllib.request.urlopen(req).read()


def workflow(init_name, prompt, denoise, seed):
    return {
        "ck": {"class_type": "CheckpointLoaderSimple",
               "inputs": {"ckpt_name": "DreamShaperXL_Turbo_v2_1.safetensors"}},
        "li": {"class_type": "LoadImage", "inputs": {"image": init_name}},
        "p": {"class_type": "CLIPTextEncode", "inputs": {"text": prompt, "clip": ["ck", 1]}},
        "n": {"class_type": "CLIPTextEncode", "inputs": {"text": NEGATIVE, "clip": ["ck", 1]}},
        "ve": {"class_type": "VAEEncode", "inputs": {"pixels": ["li", 0], "vae": ["ck", 2]}},
        "k": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 8, "cfg": 2.5, "sampler_name": "dpmpp_sde",
                         "scheduler": "karras", "denoise": denoise, "model": ["ck", 0],
                         "positive": ["p", 0], "negative": ["n", 0],
                         "latent_image": ["ve", 0]}},
        "vd": {"class_type": "VAEDecode", "inputs": {"samples": ["k", 0], "vae": ["ck", 2]}},
        "s": {"class_type": "SaveImage",
              "inputs": {"images": ["vd", 0], "filename_prefix": "lab_ground"}},
    }


def run_wf(wf):
    req = urllib.request.Request(f"{COMFY}/prompt",
                                 data=json.dumps({"prompt": wf}).encode(),
                                 headers={"Content-Type": "application/json"})
    pid = json.loads(urllib.request.urlopen(req).read())["prompt_id"]
    while True:
        time.sleep(1.5)
        hist = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}").read())
        if pid in hist:
            out = hist[pid]["outputs"]["s"]["images"][0]
            url = (f"{COMFY}/view?filename={urllib.parse.quote(out['filename'])}"
                   f"&subfolder={urllib.parse.quote(out.get('subfolder', ''))}&type=output")
            return Image.open(io.BytesIO(urllib.request.urlopen(url).read()))


MAPS = [
    ("fishing_village", 2),
    ("desert_oasis", 2),
    ("forest_clearing", 1),
    ("dungeon_floor", 3),
]


def main():
    outdir = Path("output/ground")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        guide = guide_image(m)
        prompt = terrain_prompt(m)
        print(place, "->", prompt)
        name = f"lab_guide_{place}_{seed}.png"
        upload(guide, name)
        results = [guide]
        labels = ["guide"]
        for dn in DENOISES:
            t0 = time.time()
            img = run_wf(workflow(name, prompt, dn, seed=7))
            print(f"  denoise {dn}: {time.time() - t0:.1f}s")
            img.save(outdir / f"{place}_s{seed}_dn{int(dn * 100)}.png")
            results.append(img)
            labels.append(f"denoise {dn}")
        w = max(i.width for i in results)
        h = max(i.height for i in results)
        pad = 8
        sheet = Image.new("RGB", (pad + len(results) * (w + pad), h + 40), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 4), f"{place} seed {seed} — ground img2img", fill="#ffffff")
        for i, (img, lab) in enumerate(zip(results, labels)):
            x = pad + i * (w + pad)
            sheet.paste(img.resize((w, h)), (x, 20))
            d.text((x, h + 24), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print("  sheet:", outdir / f"sheet_{place}.png")


if __name__ == "__main__":
    sys.exit(main())
