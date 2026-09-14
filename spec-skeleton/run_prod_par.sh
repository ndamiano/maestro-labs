#!/usr/bin/env bash
# Prod leg, parallel: all four designer jobs (3 team roles + skeleton) enqueued at once on the
# Flash-Next pod; skel builds as soon as it lands, the team spec gets the section gate then
# builds. Both builds awaited concurrently. Writes prod.done at the end.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd); source $REPO/venv/bin/activate
rm -f prod.done
python design_prod.py both platformer > logs/design.platformer.par.prod.log 2>&1 || echo "design failed: $(tail -1 logs/design.platformer.par.prod.log)" >> logs/run_prod_par.out
skel=$(grep -m1 '^skel: building run' logs/design.platformer.par.prod.log | awk '{print $4}')
team=$(grep -m1 '^run:' logs/design.platformer.par.prod.log | awk '{print $2}')
echo "skel=$skel team=$team" >> logs/run_prod_par.out
await() { python - "$1" >> logs/build.platformer.$2.par.prod.log 2>&1 <<'PY'
import sys, logging
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
from maestro.codegen.run import _await_build
r = _await_build(sys.argv[1])
print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
  rsync -a --delete /home/nick/output/runs/$1/game/ $REPO/runtime/games/$1/ 2>/dev/null
  echo -e "platformer\tprod-par-$2\t$1" >> builds.tsv; }
[ -n "$skel" ] && await $skel skel &
[ -n "$team" ] && await $team team &
wait
echo ALLDONE > prod.done
