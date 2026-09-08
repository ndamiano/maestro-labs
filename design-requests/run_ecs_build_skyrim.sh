#!/usr/bin/env bash
# Build the ecs skyrim design (run e8d51252d08e), 4,287 words: the turn-0 overflow test. No control.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; ARM=ecs; slug=skyrim; rid=e8d51252d08e
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
pgrep -f "python run.py" >/dev/null || { python run.py > $LAB/backend_$ARM.log 2>&1 & sleep 6; }
pgrep -f "local_gpu.py auto" >/dev/null || { python scripts/local_gpu.py auto --idle-exit 240 > $LAB/gpu_${ARM}_build.log 2>&1 & }
cd src
log=$LAB/logs/$slug.$ARM.log; t1=$(date +%s)
python -m maestro.codegen.run --build "$rid" >> "$log" 2>&1
python3 - "$rid" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<7200:
    try: d=json.load(open(p)); done=d.get("phase")=="done"
    except Exception: done=False
    quiet=quiet+1 if done else 0; time.sleep(1); t+=1
PY
echo -e "$slug\t$ARM\t$rid\t$(( $(date +%s)-t1-45 ))" >> $LAB/builds.tsv; echo "BUILT $slug $ARM $rid $(date)"
