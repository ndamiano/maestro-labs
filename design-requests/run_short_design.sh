#!/usr/bin/env bash
# Design-only arm: one-line asks (requests_short.json) through the repo designer, no build.
# Designs land as design_short_<slug>.txt; run ids in designs_short.tsv.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; ARM=short_design
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
python scripts/local_gpu.py auto --idle-exit 300 > $LAB/gpu_$ARM.log 2>&1 &
GPU=$!
cd src
python3 -c 'import json;[print(s+"\t"+t) for s,t in json.load(open("'$LAB'/requests_short.json"))]' |
while IFS=$'\t' read -r slug text; do
  grep -qP "^$slug\t" $LAB/designs_short.tsv 2>/dev/null && continue
  log=$LAB/logs/$slug.$ARM.log; t0=$(date +%s)
  python -m maestro.codegen.run --new "$text" > "$log" 2>&1
  rid=$(grep -m1 '^run:' "$log" | awk '{print $2}')
  python3 -c "import json;print(json.load(open('/home/nick/output/runs/$rid/spec.json'))['request'])" > $LAB/design_short_$slug.txt
  echo -e "$slug\t$rid\t$(( $(date +%s)-t0 ))\t$(wc -w < $LAB/design_short_$slug.txt)" >> $LAB/designs_short.tsv
  echo "$slug $rid $(( $(date +%s)-t0 ))s $(wc -w < $LAB/design_short_$slug.txt)w"
done
wait $GPU; echo "ALLDONE $(date)"
