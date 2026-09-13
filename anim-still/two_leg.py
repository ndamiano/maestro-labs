"""A loop in two legs, so the motion never has to be undone inside one clip.

Leg A: first_frame = the still, NO last_frame — the character is free to go somewhere.
Leg B: first_frame = leg A's last frame, last_frame = the still — it comes home.
Concatenated, the pair is a real loop that H3 never had to satisfy in 22 frames.
"""
import argparse, json, subprocess, sys, time
from pathlib import Path
REPO = Path("/home/nick/Documents/ai-agent-test")
sys.path.insert(0, str(REPO / "src"))
import requests  # noqa
import numpy as np  # noqa
from PIL import Image  # noqa
from tools.comfyui_tools import _load_workflow, _I2V_LOOP_WORKFLOW_PATH  # noqa
from worker import handlers, anim_sheet as sheets  # noqa


class Agent:
    target = "http://127.0.0.1:8188"
    api = "comfy"
    def __init__(self):
        self.session = requests.Session(); self.token = None


def run(agent, still_name, prompt, length, last_name=None, steps=None):
    wf = handlers._fill(_load_workflow(_I2V_LOOP_WORKFLOW_PATH), still_name, prompt, length, steps)
    if last_name is None:
        wf["5"]["inputs"].pop("last_frame", None)
    else:
        wf["4b"] = {"class_type": "LoadImage", "inputs": {"image": last_name}}
        wf["5"]["inputs"]["last_frame"] = ["4b", 0]
    return handlers._frames(handlers._comfy_outputs(
        agent, handlers._comfy_wait(agent, handlers._comfy_submit(agent, wf), 1800)))


def motion(frames):
    g = [np.asarray(f.convert("L"), dtype=int) for f in frames]
    return max(np.abs(x - g[0]).mean() for x in g)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", required=True)
    ap.add_argument("--action", required=True)
    ap.add_argument("--length", type=int, default=22)
    ap.add_argument("--length-b", type=int, default=None, help="leg B length; defaults to --length")
    ap.add_argument("--steps", type=int, default=None)
    ap.add_argument("--label", required=True)
    args = ap.parse_args()
    out = Path("/home/nick/output/anim-still/clips"); out.mkdir(parents=True, exist_ok=True)
    a = Agent()
    still = sheets.prep_still(Image.open(args.still))
    handlers._comfy_upload(a, f"{args.label}_home.png", handlers._png(still))

    t = time.time()
    legA = run(a, f"{args.label}_home.png", args.action, args.length, None, args.steps)
    handlers._comfy_upload(a, f"{args.label}_mid.png", handlers._png(legA[-1]))
    legB = run(a, f"{args.label}_mid.png", args.action, args.length_b or args.length,
               f"{args.label}_home.png", args.steps)
    secs = round(time.time() - t, 1)

    both = legA + legB
    d = out / args.label; d.mkdir(exist_ok=True)
    for i, f in enumerate(both):
        f.save(d / f"{i:03d}.png")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "24",
                    "-i", str(d / "%03d.png"), "-c:v", "libx264", "-crf", "16",
                    "-pix_fmt", "yuv420p", str(out / f"{args.label}.mp4")], check=True)
    home = np.asarray(both[0].convert("L"), dtype=int)
    close = np.abs(np.asarray(both[-1].convert("L"), dtype=int) - home).mean()
    print(json.dumps({"label": args.label, "seconds": secs,
                      "legA_travel": round(float(motion(legA)), 2),
                      "legB_travel": round(float(motion(legB)), 2),
                      "seam_A_to_B": round(float(np.abs(
                          np.asarray(legB[0].convert("L"), dtype=int) -
                          np.asarray(legA[-1].convert("L"), dtype=int)).mean()), 2),
                      "loop_close": round(float(close), 2),
                      "frames": len(both), "prompt": args.action}, indent=1))


if __name__ == "__main__":
    main()
