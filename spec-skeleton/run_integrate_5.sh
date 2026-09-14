#!/usr/bin/env bash
# Integrator on the five p2 design triples, local 27B xhigh, section gate with continuation.
cd "$(dirname "$0")"
python3 - <<'PY'
import json, re, time, urllib.request
from pathlib import Path
SECTIONS = [str(i) for i in range(12)] + ["A"]
def missing(text):
    have = set(re.findall(r"^#+\s*(\d+|A)\.", text, re.M))
    return [n for n in SECTIONS if n not in have]
def call(prompt):
    body = {"model": "qwen3.8_27b_quasar", "max_tokens": 100000, "reasoning_effort": "xhigh",
            "messages": [{"role": "system", "content": "You design browser games."},
                         {"role": "user", "content": prompt}]}
    req = urllib.request.Request("http://127.0.0.1:8090/v1/chat/completions",
                                 json.dumps(body).encode(), {"Content-Type": "application/json"})
    r = json.load(urllib.request.urlopen(req, timeout=7200))
    return r["choices"][0]["message"].get("content") or "", r
base = Path("variants/team_integrate.txt").read_text()
cont = Path("variants/team_integrate_cont.txt").read_text()
asks = dict(json.load(open("asks.json")))
for s in ("collector", "island", "station", "forest", "platformer"):
    fill = lambda t: (t.replace("{request}", asks[s])
        .replace("{gameplay}", Path(f"designs/{s}.team_gameplay_p2.xhigh.md").read_text())
        .replace("{visual}", Path(f"designs/{s}.team_visual_p2_gp.{s}.xhigh.md").read_text())
        .replace("{engineering}", Path(f"designs/{s}.team_engineering_p2_gv.{s}.xhigh.md").read_text()))
    t0 = time.time(); log = []
    text, r = call(fill(base)); log.append(r.get("usage"))
    rounds = 0
    while missing(text) and rounds < 3:
        rounds += 1
        more, r = call(fill(cont).replace("{spec_so_far}", text)); log.append(r.get("usage"))
        text += more
    Path(f"designs/{s}.team_integrate_p2.xhigh.md").write_text(text)
    json.dump({"rounds": rounds, "usage": log, "missing": missing(text)},
              open(f"designs/{s}.team_integrate_p2.xhigh.json", "w"))
    print(f"{s} {len(text)} chars rounds={rounds} missing={missing(text)} {time.time()-t0:.0f}s usage={log}", flush=True)
PY
echo done > integrate_5.done
