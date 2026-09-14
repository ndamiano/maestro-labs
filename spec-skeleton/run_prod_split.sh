#!/usr/bin/env bash
# Team arm with the split integrator (two prod calls) from the saved designer docs, then the
# build through build.sh on the prod pod. Writes split.done at the end.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd); source $REPO/venv/bin/activate
rm -f split.done
python design_prod.py cont platformer > logs/design.platformer.split.prod.log 2>&1 || { echo "split design failed: $(tail -1 logs/design.platformer.split.prod.log)" >> logs/run_prod_split.out; echo FAILED > split.done; exit 1; }
./build.sh designs/platformer.team_cont.prod.md "platformer — team continuation integrator on Flash-Next (prod pods)" > logs/build.platformer.team_split.prod.log 2>&1
rid=$(grep -m1 '^run:' logs/build.platformer.team_split.prod.log | awk '{print $2}')
rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
echo -e "platformer\tprod-par-team_cont\t$rid" >> builds.tsv
echo ALLDONE > split.done
