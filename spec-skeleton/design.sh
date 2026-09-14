#!/usr/bin/env bash
# Designer only, straight at ninfer on :8090. Usage: ARM=skel REASONING=xhigh SLUGS="island" ./design.sh
# Writes designs/<slug>.<arm>.<reasoning>.md (the design) and .json (the raw reply).
set -u
cd "$(dirname "$0")"
python3 - "${ARM:-skel}" "${REASONING:-xhigh}" ${SLUGS:-} <<'PY'
import json, sys, time, urllib.request
arm, effort, want = sys.argv[1], sys.argv[2], sys.argv[3:]
tmpl = open(f"variants/{arm}.txt").read()
for slug, ask in json.load(open("asks.json")):
    if want and slug not in want: continue
    body = {"model": "qwen3.8_27b_quasar", "max_tokens": 100000, "reasoning_effort": effort,
            "messages": [{"role": "system", "content": "You design browser games."},
                         {"role": "user", "content": tmpl.replace("{request}", ask)}]}
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8090/v1/chat/completions",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=3600))
    text = r["choices"][0]["message"].get("content") or ""
    open(f"designs/{slug}.{arm}.{effort}.md", "w").write(text)
    json.dump(r, open(f"designs/{slug}.{arm}.{effort}.json", "w"))
    print(f"{slug} {arm} {effort} {len(text)} chars {time.time()-t0:.0f}s usage={r.get('usage')}", flush=True)
PY
