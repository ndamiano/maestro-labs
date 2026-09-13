"""Step 2: does the still's framing change the SHEET?

Runs the repo's real video leg (`worker.handlers.anim_sheet`) on two stills of the same
character — the side-profile crop prod renders today, and the front-facing full body from
arm 4 — with the same four animations. Motion is scored the way the worker scores it.
"""
import argparse, base64, json, sys, time
from pathlib import Path

REPO = Path("/home/nick/Documents/ai-agent-test")
sys.path.insert(0, str(REPO / "src"))
import requests  # noqa: E402
from tools.comfyui_tools import build_anim_payload  # noqa: E402
from worker import handlers, anim_sheet as sheets  # noqa: E402


class Agent:
    """What handlers.anim_sheet needs of a worker: a session and a ComfyUI address."""
    target = "http://127.0.0.1:8188"
    api = "comfy"

    def __init__(self):
        self.session = requests.Session()
        self.token = None


ANIMS = [
    {"name": "walk", "action": "walks in place, legs alternating, sword at side"},
    {"name": "idle", "action": "stands ready, slight breathing bob"},
    {"name": "attack", "action": "lunges forward with a two-handed sword slash"},
    {"name": "defeat", "action": "staggers and drops to one knee, head bowed"},
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--facings", type=int, default=4)
    ap.add_argument("--out", default="/home/nick/output/anim-still/sheets")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

    b64 = base64.b64encode(Path(args.still).read_bytes()).decode("ascii")
    payload = build_anim_payload(b64, ANIMS, args.facings)
    t = time.time()
    result, err = handlers.anim_sheet(Agent(), payload)
    if err:
        print("ERROR:", err); return 1
    secs = round(time.time() - t, 1)
    (out / f"{args.label}.png").write_bytes(base64.b64decode(result["sheet_b64"]))
    manifest = result["manifest"]
    (out / f"{args.label}.json").write_text(json.dumps(manifest, indent=1))
    warned = {w.split(":")[0] for w in manifest.get("warnings") or []}
    total = sum(len(s["rows"]) for s in manifest["anims"].values())
    print(f"{args.label}: {secs}s, {len(warned)}/{total} clips weak "
          f"(threshold {sheets.WEAK_MOTION})")
    for w in sorted(warned):
        print("   weak:", w)
    return 0


if __name__ == "__main__":
    sys.exit(main())
