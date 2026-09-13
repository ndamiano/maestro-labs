"""Render the four facings directly instead of deriving them from a turntable.

txt2img: each facing is its own render off the same prompt and seed.
img2img: each facing denoises from the front still, to hold the design.
"""
import argparse, base64, json, sys, time, urllib.request, urllib.parse
from pathlib import Path
REPO = Path("/home/nick/Documents/ai-agent-test")
sys.path.insert(0, str(REPO / "src"))
from tools.comfyui_tools import (_load_workflow, _NEGATIVE_SUBJECT,  # noqa
                                 _TXT2IMG_SUBJECT_WORKFLOW_PATH, _IMG2IMG_SUBJECT_WORKFLOW_PATH)

COMFY = "http://127.0.0.1:8188"
FRAMING = (" Full body from head to feet, both feet visible and planted on the ground, standing "
           "upright in a neutral pose with arms clear of the body and space around the figure on "
           "every side. Plain flat white background, flat even lighting, no cast shadow.")
FACINGS = {
    "front": "seen from the front, facing the camera",
    "right": "seen from the side in full profile, facing screen right",
    "back": "seen from directly behind, facing away from the camera",
    "left": "seen from the side in full profile, facing screen left",
}
STYLE_TACTICS = ("painted fantasy tactics style, warm parchment palette with deep teal shadows, "
                 "soft dark outlines, chunky readable shapes")
STYLE_COZY = "hand-painted cozy storybook style, warm muted palette, soft dark outlines"
SUBJECTS = {
    "aldric": ("a young noble lord swordsman with silver-blond hair, blue and gold tabard, "
               "ornate short sword, small winged pauldrons", STYLE_TACTICS),
    "brann": ("a stout veteran knight with a horned helmet, heavy steel pauldrons, kite shield "
              "and a long lance", STYLE_TACTICS),
    "sera": ("a young mage woman with violet hooded robe, floating open tome, crackling orange "
             "arcane orb in hand", STYLE_TACTICS),
    "cavalier": ("a rider on a stocky barded warhorse, blue caparison, carrying a lance",
                 STYLE_TACTICS),
    "shopkeeper": ("a cozy elderly shopkeeper with a long grey beard, half-moon spectacles, a "
                   "deep plum apron over a cream shirt, rolled sleeves", STYLE_COZY),
}


def submit(wf):
    r = urllib.request.Request(f"{COMFY}/prompt", data=json.dumps({"prompt": wf}).encode(),
                               headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))["prompt_id"]


def wait(pid, timeout=900):
    end = time.time() + timeout
    while time.time() < end:
        h = json.load(urllib.request.urlopen(f"{COMFY}/history/{pid}"))
        if pid in h:
            return h[pid]
        time.sleep(2)
    raise TimeoutError(pid)


def fetch(img):
    q = urllib.parse.urlencode({k: img[k] for k in ("filename", "subfolder", "type")})
    return urllib.request.urlopen(f"{COMFY}/view?{q}").read()


def upload(name, data):
    boundary = "----lab"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; "
            f"filename=\"{name}\"\r\nContent-Type: image/png\r\n\r\n").encode() + data + \
           f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    r = urllib.request.Request(f"{COMFY}/upload/image", data=body,
                               headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    urllib.request.urlopen(r).read()


def render(prompt, seed, init=None, denoise=0.55):
    if init is None:
        wf = _load_workflow(_TXT2IMG_SUBJECT_WORKFLOW_PATH)
    else:
        wf = _load_workflow(_IMG2IMG_SUBJECT_WORKFLOW_PATH)
        wf["li"]["inputs"]["image"] = init
        wf["k"]["inputs"]["denoise"] = denoise
    wf["p"]["inputs"]["text"] = prompt
    wf["n"]["inputs"]["text"] = _NEGATIVE_SUBJECT
    wf["k"]["inputs"]["seed"] = seed
    hist = wait(submit(wf))
    imgs = [i for o in hist["outputs"].values() for i in o.get("images", [])]
    return fetch(imgs[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["txt2img", "img2img"], default="txt2img")
    ap.add_argument("--denoise", type=float, default=0.55)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--chars", default=",".join(SUBJECTS))
    ap.add_argument("--out", default="/home/nick/output/anim-still/four_facings")
    args = ap.parse_args()
    out = Path(args.out) / args.mode
    out.mkdir(parents=True, exist_ok=True)
    for c in args.chars.split(","):
        subj, style = SUBJECTS[c]
        init = None
        if args.mode == "img2img":
            src = Path(f"/home/nick/output/anim-still/{c}_front_s1000.png")
            upload(f"init_{c}.png", src.read_bytes())
            init = f"init_{c}.png"
        for d, phrase in FACINGS.items():
            t = time.time()
            prompt = f"{style}. {subj}, {phrase}." + FRAMING
            data = render(prompt, args.seed, init, args.denoise)
            (out / f"{c}_{d}.png").write_bytes(data)
            print(f"{c:11s} {d:6s} {round(time.time()-t,1):5.1f}s", flush=True)
    print("done")


if __name__ == "__main__":
    main()
