#!/usr/bin/env bash
# After the team arm: (1) the station skeleton design with tests 9/11/12 corrected by hand — one
# build isolating the bent-sim cause; (2) a SECOND PASS on the blind platformer build via
# change_from_note with the play gate's impression as the human note (the prod two-pass flow).
# The pre-change game is snapshotted first. Writes tail.done at the end.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd)
while [ ! -f team.done ]; do sleep 30; done
STEPS=200 ./build.sh designs/station.skel.xhigh.fixed.md "station — skel xhigh, tests 9/11/12 corrected" > logs/build.station.fixed.log 2>&1
rid=$(grep -m1 '^run:' logs/build.station.fixed.log | awk '{print $2}')
[ -n "$rid" ] && rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
echo -e "station\tfixed\t$rid" >> builds.tsv
mkdir -p snapshots && rsync -a --delete /home/nick/output/runs/6e2271a9571d/game/ snapshots/6e2271a9571d.pre-pass2/
cd $REPO/src && source $REPO/venv/bin/activate && python3 - > $LAB/logs/build.platformer.pass2.log 2>&1 <<'PY'
import logging
from pathlib import Path
from maestro.codegen.run import change_from_note
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
note = Path("/home/nick/Documents/ai-agent-test/labs/spec-skeleton/platformer.pass2.note.txt").read_text()
print("run: 6e2271a9571d platformer — pass 2 from the play gate's impression", flush=True)
r = change_from_note("6e2271a9571d", note, max_steps=200)
print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
cd $LAB; rsync -a --delete /home/nick/output/runs/6e2271a9571d/game/ $REPO/runtime/games/6e2271a9571d-pass2/ 2>/dev/null
echo -e "platformer\tpass2\t6e2271a9571d" >> builds.tsv
echo ALLDONE > tail.done
