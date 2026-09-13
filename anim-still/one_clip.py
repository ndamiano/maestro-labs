"""One MiniMax clip, straight to PNG frames — length, steps and prompt on the command line."""
import argparse, base64, json, shutil, subprocess, sys, time
from pathlib import Path
REPO = Path("/home/nick/Documents/ai-agent-test")
sys.path.insert(0, str(REPO / "src"))
import requests  # noqa
from tools.comfyui_tools import _I2V_STYLE, _I2V_ACTION_TAIL, _load_workflow, _I2V_LOOP_WORKFLOW_PATH  # noqa
from worker import handlers, anim_sheet as sheets  # noqa
from PIL import Image  # noqa
import numpy as np  # noqa


class Agent:
    target = "http://127.0.0.1:8188"
    api = "comfy"
    def __init__(self):
        self.session = requests.Session(); self.token = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--facing", default="seen from the front, facing the camera")
    ap.add_argument("--length", type=int, default=22)
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--pin", default="on", choices=["on", "off"])
    ap.add_argument("--style", default=None, help="replace _I2V_STYLE")
    ap.add_argument("--free-end", action="store_true",
                    help="drop last_frame: the clip need not return to the still")
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", default="/home/nick/output/anim-still/clips")
    args = ap.parse_args()

    a = Agent()
    job = f"{args.label}"
    still = sheets.prep_still(Image.open(args.still))
    handlers._comfy_upload(a, f"{job}.png", handlers._png(still))
    tail = _I2V_ACTION_TAIL if args.pin == "on" else ""
    style = _I2V_STYLE if args.style is None else args.style
    prompt = f"{style} {args.action.strip().rstrip('.')}.{tail} {args.facing}".strip()
    wf = handlers._fill(_load_workflow(_I2V_LOOP_WORKFLOW_PATH), f"{job}.png",
                        prompt, args.length, args.steps)
    if args.free_end:
        wf["5"]["inputs"].pop("last_frame", None)
    t = time.time()
    frames = handlers._frames(handlers._comfy_outputs(
        a, handlers._comfy_wait(a, handlers._comfy_submit(a, wf), 1800)))
    secs = round(time.time() - t, 1)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    d = out / args.label; d.mkdir(exist_ok=True)
    for i, f in enumerate(frames):
        f.save(d / f"{i:03d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "24",
                    "-i", str(d / "%03d.png"), "-c:v", "libx264", "-crf", "16",
                    "-pix_fmt", "yuv420p", str(out / f"{args.label}.mp4")], check=True)
    g = [np.asarray(f.convert("L"), dtype=int) for f in frames]
    delta = max(np.abs(x - y).mean() for x, y in zip(g, g[1:]))
    travel = max(np.abs(g[0] - x).mean() for x in g)
    print(json.dumps({"label": args.label, "frames": len(frames), "seconds": secs,
                      "steps": args.steps, "pin": args.pin,
                      "peak_motion": round(float(sheets.peak_motion(frames)), 2),
                      "delta": round(delta, 2), "travel": round(travel, 2),
                      "prompt": prompt}, indent=1))


if __name__ == "__main__":
    main()
