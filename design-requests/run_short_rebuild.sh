#!/usr/bin/env bash
# Fresh run from an existing run's design (spec.json request), built: run_short_rebuild.sh <slug> <src_rid> <arm>
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test
slug=$1; src=$2; ARM=$3
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
python scripts/local_gpu.py auto --idle-exit 300 > $LAB/gpu_${ARM}_$slug.log 2>&1 &
GPU=$!
cd src
rid=$(python3 - "$src" <<'PY'
import json,sys
from auth import store
from auth.billing import SECONDS_PER_CREDIT
from db import store as db_store
from maestro.codegen.run import create_run, open_ask, set_prompt
spec=json.load(open(f"/home/nick/output/runs/{sys.argv[1]}/spec.json"))
rid=create_run(store.list_users()[0].id); db_store.charge_game(rid,0,SECONDS_PER_CREDIT)
open_ask(rid, spec["ask"]); set_prompt(rid, spec["request"]); print(rid)
PY
)
t0=$(date +%s); log=$LAB/logs/$slug.$ARM.log; echo "run: $rid (design from $src)" > "$log"
python -m maestro.codegen.run --build "$rid" >> "$log" 2>&1
echo -e "$slug\t$ARM\t$rid\t$(( $(date +%s)-t0 ))" >> $LAB/builds.tsv
wait $GPU; echo "ALLDONE $(date)"
