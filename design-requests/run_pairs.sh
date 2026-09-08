#!/usr/bin/env bash
# 2-concurrent builds: launches cells from $SET two at a time, waits for both error-gate rounds.
set -u
ARM=$1; SET=${2:-battery_conc4.json}; LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test
cd $REPO/src; source $REPO/venv/bin/activate
idle() { python3 - "$1" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<7200:
    try: d=json.load(open(p)); done = d.get("phase")=="done"
    except Exception: done=False
    quiet = quiet+1 if done else 0; time.sleep(1); t+=1
PY
}
one() { slug=$1; text=$(python3 -c "import json;print(dict(json.load(open('$LAB/$SET')))['$slug'])")
  log=$LAB/logs/$slug.$ARM.log; t0=$(date +%s)
  python -m maestro.codegen.run "$text" > "$log" 2>&1
  rid=$(grep -m1 '^run:' "$log" | awk '{print $2}'); [[ -n $rid ]] && idle $rid; t1=$(( $(date +%s) - 45 ))
  echo -e "$slug\t$ARM\t$rid\t$((t1-t0))" >> $LAB/builds.tsv; echo "$slug $ARM $rid $((t1-t0))s"; }
slugs=($(python3 -c "import json;print(' '.join(s for s,_ in json.load(open('$LAB/$SET'))))"))
for ((i=0;i<${#slugs[@]};i+=2)); do
  one ${slugs[i]} & p1=$!; sleep 20; one ${slugs[i+1]} & p2=$!; wait $p1 $p2
done
echo ALLDONE >> $LAB/builds.tsv
