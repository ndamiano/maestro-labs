"""Minimal OpenAI-compatible chat client with transcript logging and JSON extraction."""
import json
import re
import time

import requests

BASE_URL = "http://127.0.0.1:8090/v1"
MODEL = "qwen3.8_27b"


class TranscriptLogger:
    def __init__(self, path):
        self.path = path
        self.calls = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0

    def log(self, record):
        self.calls += 1
        self.prompt_tokens += record.get("prompt_tokens", 0)
        self.completion_tokens += record.get("completion_tokens", 0)
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")


def chat(messages, logger, stage, temperature=0.7, seed=None, max_tokens=2048):
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if seed is not None:
        payload["seed"] = seed
    t0 = time.time()
    last_err = None
    for attempt in range(3):
        try:
            r = requests.post(f"{BASE_URL}/chat/completions", json=payload, timeout=600)
            r.raise_for_status()
            data = r.json()
            break
        except Exception as e:
            last_err = e
            time.sleep(2 * (attempt + 1))
    else:
        raise RuntimeError(f"LLM call failed after retries: {last_err}")
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    logger.log({
        "stage": stage,
        "messages": messages,
        "response": content,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "seconds": round(time.time() - t0, 2),
        "temperature": temperature,
        "seed": seed,
    })
    return content


def strip_think(text):
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def extract_json(text):
    """Pull the first JSON object or array out of a model response."""
    text = strip_think(text)
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
    if fence:
        text = fence.group(1)
    start_positions = [i for i, ch in enumerate(text) if ch in "{["]
    for start in start_positions:
        opener = text[start]
        closer = "}" if opener == "{" else "]"
        depth = 0
        in_str = False
        esc = False
        for i in range(start, len(text)):
            ch = text[i]
            if esc:
                esc = False
                continue
            if ch == "\\":
                esc = True
                continue
            if ch == '"':
                in_str = not in_str
                continue
            if in_str:
                continue
            if ch == opener:
                depth += 1
            elif ch == closer:
                depth -= 1
                if depth == 0:
                    candidate = text[start:i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break
    raise ValueError(f"No parseable JSON in response:\n{text[:2000]}")


def chat_json(messages, logger, stage, temperature=0.7, seed=None, max_tokens=2048,
              validator=None, retries=2):
    """Call the model, parse JSON, optionally validate; on failure, re-ask with the error."""
    msgs = list(messages)
    last_err = None
    for attempt in range(retries + 1):
        content = chat(msgs, logger, f"{stage}#{attempt}", temperature, seed, max_tokens)
        try:
            obj = extract_json(content)
            if validator:
                try:
                    err = validator(obj)
                except Exception:
                    err = "the reply must be a JSON object with exactly the fields shown in the skeleton"
                if err:
                    raise ValueError(err)
            return obj
        except ValueError as e:
            last_err = e
            msgs = list(messages) + [
                {"role": "assistant", "content": strip_think(content)[:3000]},
                {"role": "user", "content":
                    f"That response had a problem: {e}\n"
                    "Reply again with only the corrected JSON, nothing else."},
            ]
    raise RuntimeError(f"Stage {stage}: JSON failed after {retries + 1} attempts: {last_err}")
