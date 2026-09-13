"""Ask the local vision model, one frame at a time, which way the character faces."""
import argparse, base64, glob, json, re, sys, time
from pathlib import Path
import urllib.request

URL = "http://127.0.0.1:8090/v1/chat/completions"
MODEL = "qwen3.8_27b_quasar"
ASK = ("This is one frame of a character turntable. The character is rotating in place. "
       "Answer with the angle in degrees that the character is rotated away from facing the "
       "camera, measured clockwise as seen from above: 0 means facing the camera straight on, "
       "90 means its right side is to the camera and it faces screen left, 180 means its back "
       "is to the camera, 270 means its left side is to the camera and it faces screen right. "
       "Reply with ONLY the number.")


def ask(path, retries=1):
    b64 = base64.b64encode(Path(path).read_bytes()).decode()
    body = {"model": MODEL, "max_tokens": 16384, "temperature": 0,
            "messages": [{"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                {"type": "text", "text": ASK}]}]}
    for _ in range(retries + 1):
        r = urllib.request.Request(URL, data=json.dumps(body).encode(),
                                   headers={"Content-Type": "application/json"})
        d = json.loads(urllib.request.urlopen(r, timeout=600).read())
        ch = d["choices"][0]
        txt = ch["message"]["content"]
        if ch.get("finish_reason") == "length":
            txt = "TRUNCATED"
        m = re.findall(r"-?\d+", txt.split("</think>")[-1])
        if m:
            return int(m[-1]) % 360, txt
    return None, txt


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    args = ap.parse_args()
    paths = sorted(glob.glob(args.frames))
    print(f"{len(paths)} frames")
    out = []
    for i, p in enumerate(paths):
        t = time.time()
        deg, raw = ask(p)
        out.append(deg)
        print(f"  {i:2d}  {str(deg):>5s}deg   {round(time.time()-t,1):5.1f}s", flush=True)
    print(json.dumps(out))
