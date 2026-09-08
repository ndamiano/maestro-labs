#!/usr/bin/env bash
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; ARM=cards_nolimit
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
python scripts/local_gpu.py auto --idle-exit 600 > $LAB/gpu_$ARM.log 2>&1 &
GPU=$!
until curl -s -m 2 -o /dev/null http://127.0.0.1:8090/v1/models; do sleep 5; done; echo "ninfer up $(date)"
cd src
text=$(python3 -c "import json;print(dict(json.load(open('$LAB/requests.json')))['cards'])")
t0=$(date +%s); log=$LAB/logs/cards.$ARM.log
python -m maestro.codegen.run "$text" > "$log" 2>&1
rid=$(grep -m1 '^run:' "$log" | awk '{print $2}')
python3 - "$rid" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<7200:
    try: d=json.load(open(p)); done=d.get("phase")=="done"
    except Exception: done=False
    quiet=quiet+1 if done else 0; time.sleep(1); t+=1
PY
echo -e "cards\t$ARM\t$rid\t$(( $(date +%s)-t0-45 ))" >> $LAB/builds.tsv; echo "build done $rid $(date)"
wait $GPU; echo "ALLDONE $(date)"
