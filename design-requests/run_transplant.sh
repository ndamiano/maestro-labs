#!/usr/bin/env bash
# Arm: the Flash-Next DESIGNS (spec.request of the flashnext runs) built verbatim by the local 27B —
# no designer call. Answers: is the ceiling in the design or in the builder?
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
grep -P '\tflashnext\t' $LAB/builds.tsv | while IFS=$'\t' read -r slug _ src _; do
  grep -qP "^$slug\t$ARM\t" $LAB/builds.tsv && continue
  log=$LAB/logs/$slug.$ARM.log; t0=$(date +%s)
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
  echo "run: $rid (design from $src)" > "$log"
  python -m maestro.codegen.run --build "$rid" >> "$log" 2>&1
  idle $rid; t1=$(( $(date +%s) - 45 ))
  echo -e "$slug\t$ARM\t$rid\t$((t1-t0))" >> $LAB/builds.tsv; echo "$slug $ARM $rid $((t1-t0))s"
done
echo ALLDONE >> $LAB/builds.tsv
