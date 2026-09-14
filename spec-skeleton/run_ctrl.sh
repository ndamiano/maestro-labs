#!/usr/bin/env bash
# Overnight queue 2026-09-13: after the forest skeleton build, the CONTROL arm — every ask through
# the prod design prompt (src/maestro/codegen/prompts/design.txt, prod reasoning) and the same
# builder — then the station skeleton design with tests 9/11/12 corrected by hand.
# Needs the control plane and local_gpu auto up. Writes queue.done at the end.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$LAB/../..
while ! grep -q ALLDONE logs/build.forest.skel.xhigh.log 2>/dev/null; do sleep 30; done
cd $REPO/src; source $REPO/venv/bin/activate
for slug in $(python3 -c "import json;print(' '.join(s for s,_ in json.load(open('$LAB/asks.json'))))"); do
  text=$(python3 -c "import json;print(dict(json.load(open('$LAB/asks.json')))['$slug'])")
  python -m maestro.codegen.run "$text" > $LAB/logs/build.$slug.ctrl.log 2>&1
  rid=$(grep -m1 '^run:' $LAB/logs/build.$slug.ctrl.log | awk '{print $2}')
  [ -n "$rid" ] && rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
  echo -e "$slug\tctrl\t$rid" >> $LAB/builds.tsv
done
cd $LAB && STEPS=200 ./build.sh designs/station.skel.xhigh.fixed.md "station — skel xhigh, tests 9/11/12 corrected" > logs/build.station.fixed.log 2>&1
rid=$(grep -m1 '^run:' logs/build.station.fixed.log | awk '{print $2}')
[ -n "$rid" ] && rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
echo -e "station\tfixed\t$rid" >> builds.tsv
echo ALLDONE > queue.done
