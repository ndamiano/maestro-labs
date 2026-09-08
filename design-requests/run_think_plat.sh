#!/usr/bin/env bash
# serial single-shot builds from systems_platformer.json (multi-line requests); waits for the error-gate round.
set -u
ARM=$1; LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test
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
for slug in $(python3 -c "import json;print(' '.join(s for s,_ in json.load(open('$LAB/systems_platformer.json'))))"); do
  text=$(python3 -c "import json;print(dict(json.load(open('$LAB/systems_platformer.json')))['$slug'])")
  log=$LAB/logs/$slug.$ARM.log; t0=$(date +%s)
  python -m maestro.codegen.run "$text" > "$log" 2>&1
  rid=$(grep -m1 '^run:' "$log" | awk '{print $2}'); [[ -n $rid ]] && idle $rid; t1=$(( $(date +%s) - 45 ))
  echo -e "$slug\t$ARM\t$rid\t$((t1-t0))" >> $LAB/builds.tsv; echo "$slug $ARM $rid $((t1-t0))s"
done
echo ALLDONE >> $LAB/builds.tsv
