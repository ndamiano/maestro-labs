#!/usr/bin/env bash
# Arm "verbs": the rewritten designer (systems = what the player does, no count, loop first and
# longest) on npcs + rhythm, designed and built by the local 27B. Control = the "short" arm
# (design_prompt_nouns.txt), already built and played.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; ARM=verbs
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
python run.py > $LAB/backend_verbs.log 2>&1 &
BE=$!; sleep 6
python scripts/local_gpu.py auto --idle-exit 600 > $LAB/gpu_$ARM.log 2>&1 &
GPU=$!
cd src
idle() { python3 - "$1" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<7200:
    try: d=json.load(open(p)); done=d.get("phase")=="done"
    except Exception: done=False
    quiet=quiet+1 if done else 0; time.sleep(1); t+=1
PY
}
for slug in npcs rhythm; do
  grep -qP "^$slug\t$ARM\t" $LAB/builds.tsv && continue
  text=$(python3 -c 'import json;print(dict(json.load(open("'$LAB'/requests_short.json")))["'$slug'"])')
  log=$LAB/logs/$slug.$ARM.log; t0=$(date +%s)
  python -m maestro.codegen.run --new "$text" > "$log" 2>&1
  rid=$(grep -m1 '^run:' "$log" | awk '{print $2}')
  python3 -c "import json;print(json.load(open('/home/nick/output/runs/$rid/spec.json'))['request'])" > $LAB/design_${ARM}_$slug.txt
  echo -e "$slug\t$rid\t$(( $(date +%s)-t0 ))\t$(wc -w < $LAB/design_${ARM}_$slug.txt)" >> $LAB/designs_$ARM.tsv
  t1=$(date +%s)
  python -m maestro.codegen.run --build "$rid" >> "$log" 2>&1
  idle $rid
  echo -e "$slug\t$ARM\t$rid\t$(( $(date +%s)-t1-45 ))" >> $LAB/builds.tsv; echo "$slug $ARM $rid"
done
wait $GPU; kill $BE; echo "ALLDONE $(date)"
