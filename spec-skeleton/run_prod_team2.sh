#!/usr/bin/env bash
# Integrator retry (first landed truncated at a self-stop): re-integrate the saved three docs, build.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd); source $REPO/venv/bin/activate
python design_prod.py integrate platformer > logs/design.platformer.team2.prod.log 2>&1 || { echo "integrate retry failed: $(tail -1 logs/design.platformer.team2.prod.log)" >> logs/run_prod.out; echo ALLDONE > prod.done; exit 1; }
rid=$(grep -m1 '^run:' logs/design.platformer.team2.prod.log | awk '{print $2}')
echo "run: $rid platformer — team design (integrator retry) on Flash-Next (prod pods)" > logs/build.platformer.team.prod.log
python - "$rid" >> logs/build.platformer.team.prod.log 2>&1 <<'PY'
import sys, logging
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
from maestro.codegen.run import _await_build
r = _await_build(sys.argv[1]); print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
echo -e "platformer\tprod-team\t$rid" >> builds.tsv
echo ALLDONE > prod.done
