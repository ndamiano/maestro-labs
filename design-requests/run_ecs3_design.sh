#!/usr/bin/env bash
# Arm "ecs3": ecs2 prompt + 2D/3D decided by the designer, 3D outdoors = generated world (compose_world). Design only, skyrim ask.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; ARM=ecs3
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
pgrep -f "python run.py" >/dev/null || { python run.py > $LAB/backend_$ARM.log 2>&1 & sleep 6; }

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
for slug in; do
  design $slug "$(python3 -c 'import json;print(dict(json.load(open("'$LAB'/requests_short.json")))["'$slug'"])')"
done
design skyrim "an open world RPG like skyrim"
wait $GPU; echo "ALLDONE $(date)"
