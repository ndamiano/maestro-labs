#!/usr/bin/env bash
# Serial design arms on the local 27B: every ask under ctrl, then every ask under AC.
# design.txt is swapped only between arms (no run in flight) and restored from git at the end.
set -u
LAB=/home/nick/Documents/Labs/ashworth-street; REPO=/home/nick/Documents/ai-agent-test
PROMPT=$REPO/src/maestro/codegen/prompts/design.txt
trap 'cd $REPO && git checkout -- src/maestro/codegen/prompts/design.txt' EXIT
mkdir -p $LAB/logs
cd $REPO/src; source $REPO/venv/bin/activate
idle() { python3 - "$1" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<6*3600:
    try: d=json.load(open(p)); done = d.get("phase")=="done"
    except Exception: done=False
    quiet = quiet+1 if done else 0; time.sleep(1); t+=1
PY
}
for ARM in ${ARMS:-ctrl AC}; do
  cp $LAB/variants/$ARM.txt $PROMPT
  for slug in $(python3 -c "import json;print(' '.join(s for s,_ in json.load(open('$LAB/asks.json'))))"); do
    text=$(python3 -c "import json;print(dict(json.load(open('$LAB/asks.json')))['$slug'])")
    log=$LAB/logs/$slug.$ARM.log; t0=$(date +%s)
    python -m maestro.codegen.run "$text" > "$log" 2>&1
    rid=$(grep -m1 '^run:' "$log" | awk '{print $2}'); [[ -n $rid ]] && idle $rid; t1=$(( $(date +%s) - 45 ))
    echo -e "$slug\t$ARM\t$rid\t$((t1-t0))" >> $LAB/builds.tsv; echo "$slug $ARM $rid $((t1-t0))s"
  done
done
echo ALLDONE >> $LAB/builds.tsv
