#!/usr/bin/env bash
# Build one already-designed short-ask run: run_short_build.sh <slug> <run_id>
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; ARM=short
slug=$1; rid=$2
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
python scripts/local_gpu.py auto --idle-exit 300 > $LAB/gpu_${ARM}_$slug.log 2>&1 &
GPU=$!
cd src; t0=$(date +%s); log=$LAB/logs/$slug.$ARM.log
python -m maestro.codegen.run --build "$rid" > "$log" 2>&1
python3 - "$rid" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<7200:
    try: d=json.load(open(p)); done=d.get("phase")=="done"
    except Exception: done=False
    quiet=quiet+1 if done else 0; time.sleep(1); t+=1
PY
echo -e "$slug\t$ARM\t$rid\t$(( $(date +%s)-t0-45 ))" >> $LAB/builds.tsv
wait $GPU; echo "ALLDONE $(date)"
