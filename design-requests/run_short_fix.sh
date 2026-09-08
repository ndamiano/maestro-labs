#!/usr/bin/env bash
# Fix pass on a short-arm run: run_short_fix.sh <slug> <run_id> "<note>"
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test
slug=$1; rid=$2; note=$3
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
python scripts/local_gpu.py auto --idle-exit 300 > $LAB/gpu_shortfix_$slug.log 2>&1 &
GPU=$!
cd src; t0=$(date +%s); log=$LAB/logs/$slug.shortfix.log
python -m maestro.codegen.run --fix "$rid" "$note" > "$log" 2>&1
echo -e "$slug\tshortfix\t$rid\t$(( $(date +%s)-t0 ))" >> $LAB/builds.tsv
wait $GPU; echo "ALLDONE $(date)"
