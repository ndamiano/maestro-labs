#!/usr/bin/env bash
# Designer-only arm on the local 27B, straight at ninfer on :8090 (no control plane, no build).
# designs/<slug>.<arm>.md is the design; designs/<slug>.<arm>.json the raw reply.
set -u
LAB=/home/nick/Documents/Labs/ashworth-street; mkdir -p $LAB/designs
for ARM in ${ARMS:-dod}; do
python3 - "$ARM" "$LAB" <<'PY'
import json, os, sys, time, urllib.request
arm, lab = sys.argv[1], sys.argv[2]
tmpl = open(f"{lab}/variants/{arm}.txt").read()
want = os.environ.get("SLUGS","").split()
for slug, ask in json.load(open(f"{lab}/asks.json")):
    if want and slug not in want: continue
    body = {"model": "qwen3.8_27b_quasar", "max_tokens": 100000, "reasoning_effort": os.environ.get("REASONING","medium"),
            "messages": [{"role": "system", "content": "You design browser games."},
                         {"role": "user", "content": tmpl.replace("{request}", ask)}]}
    t0 = time.time()
    req = urllib.request.Request("http://127.0.0.1:8090/v1/chat/completions",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=3600))
    text = r["choices"][0]["message"].get("content") or ""
    open(f"{lab}/designs/{slug}.{arm}.{os.environ.get("REASONING","medium")}.md", "w").write(text)
    json.dump(r, open(f"{lab}/designs/{slug}.{arm}.{os.environ.get("REASONING","medium")}.json", "w"))
    print(f"{slug} {arm} {len(text)} chars {time.time()-t0:.0f}s usage={r.get('usage')}", flush=True)
PY
done
echo ALLDONE
