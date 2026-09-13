"""The question, constrained: is the character facing the camera, turned 90 either way,
turned away, or none of those. Five answers, nothing else."""
import argparse, base64, glob, json, re, time
from pathlib import Path
import urllib.request

URL = "http://127.0.0.1:8090/v1/chat/completions"
MODEL = "qwen3.8_27b_quasar"
ASK = ("Look at the character in this image and answer which way it is facing.\n"
       "Answer with EXACTLY ONE of these five words, and nothing else:\n"
       "FRONT   - the character faces the camera; you can see its face and the front of its body\n"
       "RIGHT   - the character is turned 90 degrees so it faces the right edge of the image; "
       "you see its side in profile\n"
       "LEFT    - the character is turned 90 degrees so it faces the left edge of the image; "
       "you see its side in profile\n"
       "BACK    - the character is turned away from the camera; you see the back of its head "
       "and body\n"
       "OTHER   - it is between these, such as a three-quarter view\n"
       "Answer with one word.")
WORDS = ("FRONT", "RIGHT", "LEFT", "BACK", "OTHER")


def ask(path, effort, max_tokens):
    b64 = base64.b64encode(Path(path).read_bytes()).decode()
    body = {"model": MODEL, "max_tokens": max_tokens, "temperature": 0,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": ASK}]}]}
    if effort:
        body["reasoning_effort"] = effort
    r = urllib.request.Request(URL, data=json.dumps(body).encode(),
                               headers={"Content-Type": "application/json"})
    d = json.loads(urllib.request.urlopen(r, timeout=900).read())
    ch = d["choices"][0]
    if ch.get("finish_reason") == "length":
        return "TRUNC", d["usage"]["completion_tokens"]
    txt = ch["message"]["content"].split("</think>")[-1].upper()
    hit = [w for w in WORDS if re.search(rf"\b{w}\b", txt)]
    return (hit[-1] if hit else "??"), d["usage"]["completion_tokens"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--effort", default=None, help="ninfer reasoning_effort; 'none' = no thinking")
    ap.add_argument("--max-tokens", type=int, default=16384)
    args = ap.parse_args()
    paths = sorted(glob.glob(args.frames))
    out = []
    for i, p in enumerate(paths):
        t = time.time()
        a, toks = ask(p, args.effort, args.max_tokens)
        out.append(a)
        print(f"  {i:2d}  {a:6s} {toks:6d} tok {round(time.time()-t,1):5.1f}s", flush=True)
    print(json.dumps(out))
