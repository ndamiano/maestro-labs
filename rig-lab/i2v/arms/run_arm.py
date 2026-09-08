"""One I2V clip on the maestro i2v_loop workflow against a running ComfyUI; frames + strip +
motion signal out. Usage: run_arm.py NAME STILL.png LENGTH "prompt" [--pin]"""
import sys, json, time, copy, uuid, io, os, urllib.parse
import requests, numpy as np
from PIL import Image
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from worker import anim_sheet as sheets
from tools.comfyui_tools import _I2V_STYLE

C = "http://127.0.0.1:8188"
name, still_path, length, prompt = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
pin = "--pin" in sys.argv
out = os.path.join(os.path.dirname(__file__), name); os.makedirs(out, exist_ok=True)
wf = json.load(open("/home/nick/Documents/ai-agent-test/src/config/workflows/i2v_loop.json"))
still = sheets.prep_still(Image.open(still_path))
buf = io.BytesIO(); still.save(buf, "PNG")
r = requests.post(f"{C}/upload/image", files={"image": (f"{name}.png", buf.getvalue(), "image/png")}, data={"overwrite": "true"}); r.raise_for_status()
wf["4"]["inputs"]["image"] = f"{name}.png"
wf["5"]["inputs"]["prompt"] = f"{_I2V_STYLE} {prompt}"
wf["5"]["inputs"]["length"] = length
wf["10"]["inputs"]["noise_seed"] = int(uuid.uuid4().int % 2**32)
if os.environ.get("UNET"): wf["1"]["inputs"]["unet_name"] = os.environ["UNET"]
if os.environ.get("STEPS"): wf["9"]["inputs"]["steps"] = int(os.environ["STEPS"])
if not pin:
    for k in list(wf["5"]["inputs"]):
        if "last" in k: wf["5"]["inputs"].pop(k)
print("node5 inputs:", {k: v for k, v in wf["5"]["inputs"].items() if k != "prompt"})
t0 = time.time()
pid = requests.post(f"{C}/prompt", json={"prompt": wf}).json()["prompt_id"]
while True:
    h = requests.get(f"{C}/history/{pid}").json()
    if pid in h: break
    time.sleep(2)
secs = time.time() - t0
frames = []
for no in h[pid]["outputs"].values():
    for img in no.get("images", []):
        q = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")})
        frames.append(Image.open(io.BytesIO(requests.get(f"{C}/view?{q}").content)).convert("RGB"))
for i, f in enumerate(frames): f.save(f"{out}/f{i:03d}.png")
motion = sheets.motion_signal(frames)
strip = Image.new("RGB", (len(frames) * 96, 96), (80, 80, 80))
for i, f in enumerate(frames): strip.paste(f.resize((96, 96)), (i * 96, 0))
strip.save(f"{out}/strip.png")
json.dump({"seconds": secs, "frames": len(frames), "motion": [round(float(m), 1) for m in motion]}, open(f"{out}/result.json", "w"))
print(f"{name}: {len(frames)} frames in {secs:.1f}s; motion {np.round(motion,1).tolist()}")
