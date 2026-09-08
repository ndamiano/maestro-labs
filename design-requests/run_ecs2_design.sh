#!/usr/bin/env bash
# Arm "ecs2": ecs prompt with battery-game examples stripped and "roster = kinds, generator picks the answer". Redo of npcs + rhythm.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; ARM=ecs2
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
pgrep -f "python run.py" >/dev/null || { python run.py > $LAB/backend_$ARM.log 2>&1 & sleep 6; }
until grep -q ALLDONE $LAB/night_ecs_design.log; do sleep 30; done; sleep 20
python scripts/local_gpu.py auto --idle-exit 240 > $LAB/gpu_$ARM.log 2>&1 &
GPU=$!
cd src
design() { slug=$1; text=$2
  log=$LAB/logs/$slug.$ARM.log; t0=$(date +%s)
  python -m maestro.codegen.run --new "$text" > "$log" 2>&1
  rid=$(grep -m1 '^run:' "$log" | awk '{print $2}')
  python3 -c "import json;print(json.load(open('/home/nick/output/runs/$rid/spec.json'))['request'])" > $LAB/design_${ARM}_$slug.txt
  echo -e "$slug\t$rid\t$(( $(date +%s)-t0 ))\t$(wc -w < $LAB/design_${ARM}_$slug.txt)" >> $LAB/designs_$ARM.tsv; echo "$slug $rid"
}
for slug in npcs rhythm; do
  design $slug "$(python3 -c 'import json;print(dict(json.load(open("'$LAB'/requests_short.json")))["'$slug'"])')"
done
wait $GPU; echo "ALLDONE $(date)"
