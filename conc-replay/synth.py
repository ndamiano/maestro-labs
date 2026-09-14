"""Grow N synthetic conversations concurrently, one thread each: every turn appends a chunk of
random words as a user/assistant pair, so each request extends the previous one's token prefix
exactly as a build turn does. Logs per turn: time to first token, prompt tokens, cached tokens.
Stdlib only — runs on the pod's engine venv."""
import argparse
import http.client
import json
import random
import threading
import time
from urllib.parse import urlparse

SYSTEM = "You are a terse assistant. Reply with one short sentence."


def words(rng, n):
    return " ".join("".join(rng.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(rng.randint(3, 7)))
                    for _ in range(n))


def one(target, model, messages, max_tokens, timeout, thinking_switch, ignore_eos=False):
    body = {"model": model, "messages": messages, "temperature": 0.7, "max_tokens": max_tokens,
            "stream": True, "stream_options": {"include_usage": True}}
    if ignore_eos:
        body["ignore_eos"] = True
    if thinking_switch:
        body["chat_template_kwargs"] = {"enable_thinking": False}
    payload = json.dumps(body).encode()
    u = urlparse(target)
    conn = http.client.HTTPConnection(u.hostname, u.port, timeout=timeout)
    t0 = time.perf_counter()
    first, usage, err = None, None, None
    try:
        conn.request("POST", "/v1/chat/completions", body=payload,
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        if resp.status != 200:
            err = f"HTTP {resp.status}: {resp.read(1000).decode('utf-8', 'replace')}"
        else:
            for raw in resp:
                line = raw.decode("utf-8", "replace").strip()
                if not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                chunk = json.loads(data)
                if chunk.get("usage"):
                    usage = chunk["usage"]
                for ch in chunk.get("choices") or []:
                    d = ch.get("delta") or {}
                    if first is None and (d.get("content") or d.get("reasoning_content")):
                        first = time.perf_counter()
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    finally:
        conn.close()
    details = (usage or {}).get("prompt_tokens_details") or {}
    return {"t_start": t0, "ttft": (first - t0) if first else None, "total": time.perf_counter() - t0,
            "prompt_tokens": (usage or {}).get("prompt_tokens"),
            "cached_tokens": details.get("cached_tokens"),
            "completion_tokens": (usage or {}).get("completion_tokens"), "error": err}


def stream(a, idx, out, lock, epoch):
    rng = random.Random(1000 + idx)
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": words(rng, a.start_words)}]
    for turn in range(a.turns):
        r = one(a.target, a.model, messages, a.max_tokens, a.timeout, not a.no_thinking_switch)
        r.update({"arm": a.arm, "stream": idx, "turn": turn, "t_start": r["t_start"] - epoch})
        with lock:
            out.write(json.dumps(r) + "\n")
            out.flush()
        if r["error"]:
            print(f"[{a.arm} s{idx} t{turn}] {r['error'][:200]}", flush=True)
        messages.append({"role": "assistant", "content": "Noted."})
        messages.append({"role": "user", "content": words(rng, a.step_words)})
    if a.decode_tokens:
        r = one(a.target, a.model, messages, a.decode_tokens, a.timeout, not a.no_thinking_switch,
                ignore_eos=True)
        r.update({"arm": a.arm, "stream": idx, "turn": "decode", "t_start": r["t_start"] - epoch})
        with lock:
            out.write(json.dumps(r) + "\n")
            out.flush()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True)
    ap.add_argument("--model", default="pennyroyal")
    ap.add_argument("--arm", required=True)
    ap.add_argument("--streams", type=int, default=1)
    ap.add_argument("--turns", type=int, default=100)
    ap.add_argument("--start-words", type=int, default=8000)
    ap.add_argument("--step-words", type=int, default=350)
    ap.add_argument("--max-tokens", type=int, default=32)
    ap.add_argument("--timeout", type=float, default=600)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-thinking-switch", action="store_true")
    ap.add_argument("--decode-tokens", type=int, default=0,
                    help="after the ramp, one generation of this many tokens with EOS ignored")
    a = ap.parse_args()
    lock = threading.Lock()
    epoch = time.perf_counter()
    with open(a.out, "a") as out:
        ts = [threading.Thread(target=stream, args=(a, i, out, lock, epoch)) for i in range(a.streams)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    print(f"[{a.arm}] done in {time.perf_counter() - epoch:.0f}s", flush=True)


if __name__ == "__main__":
    main()
