#!/usr/bin/env bash
# Team design arm: three designers (visual, gameplay, engineering) each write their doc, an
# integrator litigates and merges into one build spec; one build of the result. Runs after the
# vision arm, reverts vision.patch and restarts the control plane first so the builder is the same
# blind one the skeleton builds had. Writes team.done at the end.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd)
while [ ! -f vision.done ]; do sleep 30; done
python3 - <<'PY'
import json, time, urllib.request
lab='/home/nick/Documents/ai-agent-test/labs/spec-skeleton'
def call(prompt, tag):
    body={"model":"qwen3.8_27b_quasar","max_tokens":100000,"reasoning_effort":"xhigh",
          "messages":[{"role":"system","content":"You design browser games."},{"role":"user","content":prompt}]}
    t0=time.time()
    req=urllib.request.Request("http://127.0.0.1:8090/v1/chat/completions",json.dumps(body).encode(),{"Content-Type":"application/json"})
    r=json.load(urllib.request.urlopen(req,timeout=3600))
    text=r["choices"][0]["message"].get("content") or ""
    json.dump(r,open(f"{lab}/designs/team/{tag}.json","w"))
    print(f"{tag} {len(text)} chars {time.time()-t0:.0f}s usage={r.get('usage')} finish={r['choices'][0]['finish_reason']}",flush=True)
    return text
asks=dict(json.load(open(f"{lab}/asks.json")))
for slug in ("station","collector"):
    ask=asks[slug]; docs={}
    for role in ("visual","gameplay","engineering"):
        tmpl=open(f"{lab}/variants/team_{role}.txt").read()
        docs[role]=call(tmpl.replace("{request}",ask), f"{slug}.{role}")
        open(f"{lab}/designs/team/{slug}.{role}.md","w").write(docs[role])
    tmpl=open(f"{lab}/variants/team_integrate.txt").read()
    merged=call(tmpl.replace("{request}",ask).replace("{gameplay}",docs["gameplay"]).replace("{visual}",docs["visual"]).replace("{engineering}",docs["engineering"]), f"{slug}.integrate")
    open(f"{lab}/designs/{slug}.team.xhigh.md","w").write(merged)
PY
cd $REPO && git checkout -- src/maestro/codegen/play.py src/maestro/codegen/tools.py src/maestro/codegen/build_steps.py src/maestro/codegen/prompts/build.txt
cp=$(pgrep -fx 'venv/bin/python run.py'); [ -n "$cp" ] && kill $cp; for i in $(seq 1 20); do pgrep -fx 'venv/bin/python run.py' >/dev/null || break; sleep 1; done
setsid nohup venv/bin/python run.py >> /tmp/maestro-local/run.log 2>&1 < /dev/null &
for i in $(seq 1 30); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:8000/)" = 200 ] && break; sleep 2; done
echo "control plane restarted on the clean tree: $(git -C $REPO status --short src | wc -l) src files dirty" >> $LAB/logs/run_team.out
cd $LAB
for a in station collector; do
  [ "$a" = collector ] && [ $((10#$(date +%H))) -ge 9 ] && { echo "collector team build skipped: past 09:00" >> logs/run_team.out; break; }
  STEPS=200 ./build.sh designs/$a.team.xhigh.md "$a — team design (3 designers + integrator), xhigh" > logs/build.$a.team.log 2>&1
  rid=$(grep -m1 '^run:' logs/build.$a.team.log | awk '{print $2}')
  [ -n "$rid" ] && rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
  echo -e "$a\tteam\t$rid" >> builds.tsv
done
echo ALLDONE > team.done
