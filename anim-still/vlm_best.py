"""Second pass: show the model every frame of one run and ask which is the truest of them.

A per-frame label has to threshold in isolation — is THIS a profile? Ranking is the easier
question, and the frames of a run differ only by a few degrees.
"""
import argparse, base64, glob, json, re, time
from pathlib import Path
import urllib.request

URL = "http://127.0.0.1:8090/v1/chat/completions"
MODEL = "qwen3.8_27b_quasar"
ASKS = {
    "left": "Which image shows the character turned MOST exactly 90 degrees to face the LEFT "
            "edge of the frame — the truest side profile, not a three-quarter view?",
    "right": "Which image shows the character turned MOST exactly 90 degrees to face the RIGHT "
             "edge of the frame — the truest side profile, not a three-quarter view?",
    "back": "Which image shows the character turned MOST exactly away from the camera — the "
            "truest straight-on back view, square to the camera?",
    "front": "Which image shows the character facing the camera MOST exactly straight on — "
             "square to the camera, not turned at all?",
    "profile": "Which image shows the character's side view MOST exactly — a true 90 degree "
               "side profile, square to neither the front nor the back, not a three-quarter "
               "view? Ignore which way it faces.",
}


def best(paths, which, idxs):
    content = []
    for n, p in zip(idxs, paths):
        content.append({"type": "text", "text": f"Image {n}:"})
        content.append({"type": "image_url", "image_url": {
            "url": "data:image/png;base64," + base64.b64encode(Path(p).read_bytes()).decode()}})
    content.append({"type": "text", "text":
                    f"{ASKS[which]}\nAnswer with ONLY the image number."})
    body = {"model": MODEL, "max_tokens": 512, "temperature": 0,
            "reasoning_effort": "none",
            "messages": [{"role": "user", "content": content}]}
    r = urllib.request.Request(URL, data=json.dumps(body).encode(),
                               headers={"Content-Type": "application/json"})
    d = json.loads(urllib.request.urlopen(r, timeout=900).read())
    txt = d["choices"][0]["message"]["content"]
    m = re.findall(r"\d+", txt)
    return (int(m[-1]) if m else None), d["usage"]["completion_tokens"], txt.strip()[:40]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--which", required=True)
    ap.add_argument("--idxs", required=True, help="comma-separated frame indices")
    args = ap.parse_args()
    allp = sorted(glob.glob(f"{args.dir}/*.png"))
    idxs = [int(x) for x in args.idxs.split(",")]
    t = time.time()
    pick, toks, raw = best([allp[i] for i in idxs], args.which, idxs)
    print(f"{args.which:6s} candidates {idxs} -> {pick}   ({toks} tok, {round(time.time()-t,1)}s) {raw!r}")
