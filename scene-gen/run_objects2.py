"""Objects pass 2: prod's sprite recipe — NetaYume Lumina + BiRefNet matte — then compose."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from run_ground import COMFY, upload, run_wf, MAPS
import io
import time
import urllib.request

CELL = 48
NEG = "worst quality, low quality, blurry, watermark, signature, text, photo, photorealistic"
BIG = ("cabin", "hut", "house", "stall", "tent", "pier", "boat", "market", "door", "chest")


def sprite_workflow(desc, seed):
    return {
        "4": {"class_type": "CheckpointLoaderSimple",
              "inputs": {"ckpt_name": "NetaYume_v4_all_in_one.safetensors"}},
        "10": {"class_type": "ModelSamplingAuraFlow", "inputs": {"shift": 6.0, "model": ["4", 0]}},
        "6": {"class_type": "CLIPTextEncode",
              "inputs": {"text": "masterpiece, best quality, " + desc, "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["4", 1]}},
        "5": {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "3": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 30, "cfg": 4.5, "sampler_name": "res_multistep",
                         "scheduler": "simple", "denoise": 1.0, "model": ["10", 0],
                         "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "47": {"class_type": "BiRefNetRMBG",
               "inputs": {"model": "BiRefNet-general", "mask_blur": 0, "mask_offset": -1,
                          "invert_output": False, "refine_foreground": False,
                          "background": "Alpha", "background_color": "#ffffff",
                          "image": ["8", 0]}},
        "s": {"class_type": "SaveImage",
              "inputs": {"images": ["47", 0], "filename_prefix": "lab_sprite2"}},
    }


def run_wf_rgba(wf):
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
            return Image.open(io.BytesIO(urllib.request.urlopen(url).read())).convert("RGBA")


def item_cells(name):
    n = name.lower()
    return 2.5 if any(k in n for k in BIG) else 1.3


def main():
    outdir = Path("output/objects2")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        ground = Image.open(f"output/ground9/{place}_final.png").convert("RGBA")
        sprites = {}
        for it in m["items"]:
            desc = (f"one {it['name']}, stylized cartoon game sprite, chunky simplified "
                    "low-poly forms, bold colour, seen from above at a steep angle, "
                    "single object, plain background")
            sp = run_wf_rgba(sprite_workflow(desc, seed=13))
            bbox = sp.getbbox()
            if bbox:
                sp = sp.crop(bbox)
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
            d.ellipse([cx - s.width // 2 + 4, cy + s.height // 3,
                       cx + s.width // 2 - 4, cy + s.height // 2 + 4], fill=(0, 0, 0, 80))
            sh = sh.filter(ImageFilter.GaussianBlur(3))
            ground = Image.alpha_composite(ground, sh)
            ground.alpha_composite(s, (cx - s.width // 2, cy - s.height // 2))
        ground.convert("RGB").save(outdir / f"{place}_composed.png")
        print(place, "done")


if __name__ == "__main__":
    main()
