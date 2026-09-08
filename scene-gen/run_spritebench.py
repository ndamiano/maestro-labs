"""Sprite quality bench: model x prompt-richness per item, one judging sheet per item."""
import json
from pathlib import Path

from PIL import Image, ImageDraw

from run_objects2 import run_wf_rgba, sprite_workflow as netayume_wf

STYLE = ("Single object, complete and unobstructed, centred and filling the frame. "
         "Three-quarter view from slightly above, showing its depth and thickness. "
         "Plain flat mid-grey background. Soft even studio lighting from several directions. "
         "Stylized cartoon game asset: chunky simplified low-poly forms, clean bold "
         "silhouette, flat painterly colour, no fine surface detail.")
NEG = ("blurry, low detail, cropped, cut off, partial object, multiple objects, scenery, "
       "landscape, ground, floor, horizon, cast shadow, text, watermark, flat, front view, "
       "orthographic, photograph, photorealistic, fine detail, thin wispy branches")

ITEMS = {
    "cabin": "a small weathered wooden fishing cabin with a steep shingled roof and a stone chimney",
    "boat": "a small wooden rowing boat with two bench seats and oars shipped inboard",
    "pier": "a short wooden pier of rough planks on thick barnacled posts",
    "net": "a bundled brown fishing net with small cork floats along its edge",
    "fisherman": "a cheerful old fisherman in a yellow raincoat and boots holding a fishing rod",
    "seagull": "a white seagull with grey wings standing alert",
    "chest": "an iron-banded wooden treasure chest overflowing with gold coins",
}


def qwen_wf(desc, seed):
    return {
        "u": {"class_type": "UNETLoader",
              "inputs": {"unet_name": "qwen_image_2512_fp8_e4m3fn.safetensors",
                         "weight_dtype": "default"}},
        "c": {"class_type": "CLIPLoader",
              "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors",
                         "type": "qwen_image", "device": "default"}},
        "v": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "ms": {"class_type": "ModelSamplingAuraFlow", "inputs": {"shift": 3.1, "model": ["u", 0]}},
        "p": {"class_type": "CLIPTextEncode", "inputs": {"text": desc + " " + STYLE,
                                                         "clip": ["c", 0]}},
        "n": {"class_type": "CLIPTextEncode", "inputs": {"text": NEG, "clip": ["c", 0]}},
        "l": {"class_type": "EmptySD3LatentImage",
              "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "k": {"class_type": "KSampler",
              "inputs": {"seed": seed, "steps": 20, "cfg": 2.5, "sampler_name": "euler",
                         "scheduler": "simple", "denoise": 1.0, "model": ["ms", 0],
                         "positive": ["p", 0], "negative": ["n", 0], "latent_image": ["l", 0]}},
        "d": {"class_type": "VAEDecode", "inputs": {"samples": ["k", 0], "vae": ["v", 0]}},
        "47": {"class_type": "BiRefNetRMBG",
               "inputs": {"model": "BiRefNet-general", "mask_blur": 0, "mask_offset": -1,
                          "invert_output": False, "refine_foreground": False,
                          "background": "Alpha", "background_color": "#ffffff",
                          "image": ["d", 0]}},
        "s": {"class_type": "SaveImage",
              "inputs": {"images": ["47", 0], "filename_prefix": "lab_bench"}},
    }


def main():
    outdir = Path("output/spritebench")
    outdir.mkdir(parents=True, exist_ok=True)
    for name, desc in ITEMS.items():
        arms = []
        rich = desc + ", stylized cartoon game sprite, chunky simplified low-poly forms, bold colour"
        arms.append(("qwen+style", run_wf_rgba(qwen_wf(desc, seed=5))))
        arms.append(("netayume+rich", run_wf_rgba(netayume_wf(rich, seed=5))))
        old = Path(f"output/objects2/fishing_village_{name[0]}_sprite.png")
        tiles = []
        for label, im in arms:
            im.save(outdir / f"{name}_{label.replace('+','_')}.png")
            bbox = im.getbbox()
            tiles.append((label, im.crop(bbox) if bbox else im))
        S = 360
        pad = 8
        sheet = Image.new("RGB", (pad + len(tiles) * (S + pad), S + 40), "#333333")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 4), name, fill="#ffffff")
        for i, (label, im) in enumerate(tiles):
            scale = S / max(im.width, im.height)
            im2 = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))))
            x = pad + i * (S + pad)
            bg = Image.new("RGBA", (S, S), (85, 85, 85, 255))
            bg.alpha_composite(im2, ((S - im2.width) // 2, (S - im2.height) // 2))
            sheet.paste(bg.convert("RGB"), (x, 20))
            d.text((x, S + 24), label, fill="#ffffff")
        sheet.save(outdir / f"sheet_{name}.png")
        print(name, "done")


if __name__ == "__main__":
    main()
