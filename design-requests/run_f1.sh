#!/usr/bin/env bash
# waits for the design arm, then the staged plain control; both logged to builds.tsv
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test
cd $REPO/src
idle() { python3 - "$1" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<10800:
    try: d=json.load(open(p)); done = d.get("phase")=="done"
    except Exception: done=False
    quiet = quiet+1 if done else 0; time.sleep(1); t+=1
PY
}
t0=$(date +%s); idle cb99894cf98e; echo -e "f1\tsystems\tcb99894cf98e\t$(( $(date +%s) - t0 - 45 ))" >> $LAB/builds.tsv
log=$LAB/logs/f1.plain-staged.log; t0=$(date +%s)
../venv/bin/python -m maestro.codegen.run --staged "Make me an f1 racing game." > "$log" 2>&1
rid=$(grep -m1 -o 'build [0-9a-f]\{12\}' "$log" | awk '{print $2}'); [[ -n $rid ]] && idle $rid
echo -e "f1\tplain-staged\t$rid\t$(( $(date +%s) - t0 - 45 ))" >> $LAB/builds.tsv; echo ALLDONE >> $LAB/builds.tsv
