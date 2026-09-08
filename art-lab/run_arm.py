"""Render the 16 prompts of the demon-lord game through one recipe ("arm") on local ComfyUI.

usage: python run_arm.py <arm> [--ids a,b,c]
Prompts are used VERBATIM (prompts.json). Arms differ only in workflow-side knobs: checkpoint,
sampler, negative, matte model, LoRA. Seed is fixed per asset id so arms are comparable.
Output: arms/<arm>/<id>.png (raw matted render) and arms/<arm>/<id>.crop.png (prod autocrop).
"""
import json, sys, time, uuid, zlib, urllib.request, urllib.parse
from pathlib import Path
from PIL import Image

COMFY = "http://127.0.0.1:8188"
HERE = Path(__file__).parent
import os
PROMPTS = json.load(open(HERE / os.environ.get("PROMPTS", "prompts.json")))

# prod values, copied from src/tools/comfyui_tools.py
NEG_ITEM = "worst quality, low quality, blurry, watermark, signature, text, photo, photorealistic"
PREFIX_ITEM = "masterpiece, best quality, "
NEG_FRAME = ", cropped, cut off, out of frame, partial, close-up, clipped edges"


def seed_for(aid):
    return zlib.crc32(aid.encode()) & 0xFFFFFFFF


def matte(wf, img_ref, model="BiRefNet-general", offset=-1, refine=False):
    wf["47"] = {"class_type": "BiRefNetRMBG", "inputs": {
        "image": img_ref, "model": model, "mask_blur": 0, "mask_offset": offset,
        "invert_output": False, "refine_foreground": refine, "background": "Alpha",
        "background_color": "#ffffff"}}
    wf["9"] = {"class_type": "SaveImage", "inputs": {"images": ["47", 0], "filename_prefix": "artlab"}}
    return wf


def sdxl_like(ckpt, pos, neg, seed, steps, cfg, sampler, sched, lora=None, lora_w=1.0, auraflow_shift=None):
    wf = {
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ckpt}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
    }
    model_ref, clip_ref = ["4", 0], ["4", 1]
    if lora:
        wf["11"] = {"class_type": "LoraLoader", "inputs": {"model": model_ref, "clip": clip_ref,
                    "lora_name": lora, "strength_model": lora_w, "strength_clip": lora_w}}
        model_ref, clip_ref = ["11", 0], ["11", 1]
    if auraflow_shift is not None:
        wf["10"] = {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": model_ref, "shift": auraflow_shift}}
        model_ref = ["10", 0]
        wf["5"] = {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}}
    wf["6"] = {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": clip_ref}}
    wf["7"] = {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": clip_ref}}
    wf["3"] = {"class_type": "KSampler", "inputs": {"model": model_ref, "positive": ["6", 0], "negative": ["7", 0],
               "latent_image": ["5", 0], "seed": seed, "steps": steps, "cfg": cfg,
               "sampler_name": sampler, "scheduler": sched, "denoise": 1.0}}
    return wf


def qwen(pos, neg, seed, steps=20, cfg=2.5):
    return {
        "u": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_2512_fp8_e4m3fn.safetensors", "weight_dtype": "default"}},
        "c": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default"}},
        "v": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "ms": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["u", 0], "shift": 3.1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["c", 0]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": neg, "clip": ["c", 0]}},
        "5": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 1024, "height": 1024, "batch_size": 1}},
        "3": {"class_type": "KSampler", "inputs": {"model": ["ms", 0], "positive": ["6", 0], "negative": ["7", 0],
              "latent_image": ["5", 0], "seed": seed, "steps": steps, "cfg": cfg,
              "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["v", 0]}},
    }


def hidream(pos, seed, size=1024):
    return {
        "hm": {"class_type": "HiDreamO1ModelLoader", "inputs": {"model_name": "HiDream-O1-Image-Dev-2604-FP8",
               "precision": "auto", "attention": "sdpa", "download_if_missing": False}},
        "hc": {"class_type": "HiDreamO1Conditioning", "inputs": {"prompt": pos, "negative_prompt": ""}},
        "8": {"class_type": "HiDreamO1Sampler", "inputs": {"model": ["hm", 0], "conditioning": ["hc", 0],
              "model_type": "dev", "width": size, "height": size, "steps": 0, "seed": seed,
              "guidance_scale": 0.0, "shift": -1.0, "noise_scale_start": 7.5, "noise_scale_end": 7.5,
              "noise_clip_std": 2.5, "dev_editing_scheduler": "flow_match", "layout_bboxes": "",
              "preview_every": 0, "keep_image1_aspect": False, "force_offload": False,
              "image": {"image": "0"}}},
    }


def hidream_native(pos, seed, size=1024, full=False):
    ck = "hidream_o1_image_fp8_scaled.safetensors" if full else "hidream_o1_image_dev_fp8_scaled.safetensors"
    wf = {
        "ck": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": ck}},
        "ns": {"class_type": "ModelNoiseScale", "inputs": {"model": ["ck", 0], "noise_scale": 8.0 if full else 7.6}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": pos, "clip": ["ck", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "", "clip": ["ck", 1]}},
        "5": {"class_type": "EmptyHiDreamO1LatentImage", "inputs": {"width": size, "height": size, "batch_size": 1}},
        "sm": {"class_type": "SamplerLCM", "inputs": {"s_noise": 1.0, "s_noise_end": 1.0, "noise_clip_std": 2.5}},
        "sg": {"class_type": "BasicScheduler", "inputs": {"model": ["ns", 0], "scheduler": "normal", "steps": 28, "denoise": 1.0}},
        "3": {"class_type": "SamplerCustom", "inputs": {"model": ["ns", 0], "add_noise": True, "noise_seed": seed, "cfg": 1.0,
              "positive": ["6", 0], "negative": ["7", 0], "sampler": ["sm", 0], "sigmas": ["sg", 0], "latent_image": ["5", 0]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["ck", 2]}},
    }
    if full:
        wf["7"]["inputs"]["text"] = NEG_ITEM + NEG_FRAME
        wf["sm"] = {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "dpmpp_2m_sde_gpu"}}
        wf["sg"]["inputs"]["steps"] = 40
        wf["3"]["inputs"]["cfg"] = 5.0
    return wf


NETA = "NetaYume_v4_all_in_one.safetensors"
WAI = "waiIllustriousSDXL_v170.safetensors"
DS = "DreamShaperXL_Turbo_v2_1.safetensors"
FLUX = "flux1-schnell-fp8.safetensors"
PXL = "pixel-art-xl.safetensors"


def build(arm, p):
    s = seed_for(p["id"]); pr = p["prompt"]
    if arm == "base":
        return matte(sdxl_like(NETA, PREFIX_ITEM + pr, NEG_ITEM, s, 30, 4.5, "res_multistep", "simple", auraflow_shift=6.0), ["8", 0])
    if arm == "neg":
        return matte(sdxl_like(NETA, PREFIX_ITEM + pr, NEG_ITEM + NEG_FRAME, s, 30, 4.5, "res_multistep", "simple", auraflow_shift=6.0), ["8", 0])
    if arm == "toon":
        return matte(sdxl_like(NETA, PREFIX_ITEM + pr, NEG_ITEM, s, 30, 4.5, "res_multistep", "simple", auraflow_shift=6.0), ["8", 0], model="BiRefNet_toonout")
    if arm == "qwen":
        return matte(qwen(pr, NEG_ITEM + NEG_FRAME, s), ["8", 0])
    if arm == "wai_pxl":
        return matte(sdxl_like(WAI, PREFIX_ITEM + pr, NEG_ITEM + NEG_FRAME, s, 30, 6.0, "dpmpp_2m", "karras", lora=PXL), ["8", 0])
    if arm == "ds_pxl":
        return matte(sdxl_like(DS, pr, NEG_ITEM + NEG_FRAME, s, 8, 2.5, "dpmpp_sde", "karras", lora=PXL), ["8", 0])
    if arm == "hidream":
        return matte(hidream(pr, s), ["8", 0])
    if arm == "hidream2k":
        return matte(hidream(pr, s, 2048), ["8", 0])
    if arm == "hidream_n":
        return matte(hidream_native(pr, s), ["8", 0])
    if arm == "hidream_n2k":
        return matte(hidream_native(pr, s, 2048), ["8", 0])
    if arm == "hidream_full":
        return matte(hidream_native(pr, s, 1024, full=True), ["8", 0])
    if arm == "hidream_full2k":
        return matte(hidream_native(pr, s, 2048, full=True), ["8", 0])
    if arm == "flux":
        return matte(sdxl_like(FLUX, pr, "", s, 4, 1.0, "euler", "simple"), ["8", 0])
    raise SystemExit(f"unknown arm {arm}")


def submit(wf):
    req = urllib.request.Request(f"{COMFY}/prompt", json.dumps({"prompt": wf, "client_id": "artlab"}).encode(),
                                 {"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if "prompt_id" not in out:
        raise RuntimeError(out)
    return out["prompt_id"]


def wait(pid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with urllib.request.urlopen(f"{COMFY}/history/{pid}") as r:
            h = json.load(r)
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise RuntimeError(json.dumps(st)[:2000])
            for node in h[pid]["outputs"].values():
                for im in node.get("images", []):
                    return im
        time.sleep(1.0)
    raise TimeoutError(pid)


def fetch(im, dst):
    q = urllib.parse.urlencode({"filename": im["filename"], "subfolder": im.get("subfolder", ""), "type": im["type"]})
    with urllib.request.urlopen(f"{COMFY}/view?{q}") as r:
        dst.write_bytes(r.read())


def autocrop(im, pad_frac=0.06):
    bbox = im.split()[-1].getbbox()
    if not bbox:
        return im
    pad = int(max(im.width, im.height) * pad_frac)
    return im.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(im.width, bbox[2] + pad), min(im.height, bbox[3] + pad)))


def main():
    arm = sys.argv[1]
    ids = None
    if "--ids" in sys.argv:
        ids = set(sys.argv[sys.argv.index("--ids") + 1].split(","))
    out = HERE / os.environ.get("ARMS", "arms") / arm; out.mkdir(parents=True, exist_ok=True)
    log = open(out / "timing.jsonl", "a")
    for p in PROMPTS:
        if ids and p["id"] not in ids:
            continue
        dst = out / f"{p['id']}.png"
        if dst.exists():
            continue
        t0 = time.time()
        im = wait(submit(build(arm, p)))
        fetch(im, dst)
        raw = Image.open(dst).convert("RGBA")
        autocrop(raw).save(out / f"{p['id']}.crop.png")
        dt = time.time() - t0
        log.write(json.dumps({"id": p["id"], "s": round(dt, 1)}) + "\n"); log.flush()
        print(f"{arm:8} {p['id']:14} {dt:5.1f}s  {raw.size}")


if __name__ == "__main__":
    main()
