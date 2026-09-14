#!/usr/bin/env bash
# Prod leg (Flash-Next on RunPod, via the funnel): one-shot skeleton design → build, then team
# design → build, same ask, all through the prod design path (design.enqueue → handler lands →
# build auto-starts). Waits for the build of each to reach phase done.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd); source $REPO/venv/bin/activate
for arm in skel team; do
  python design_prod.py $arm platformer > logs/design.platformer.$arm.prod.log 2>&1 || { echo "design $arm failed: $(tail -1 logs/design.platformer.$arm.prod.log)" >> logs/run_prod.out; continue; }
  rid=$(grep -m1 '^run:' logs/design.platformer.$arm.prod.log | awk '{print $2}')
  echo "run: $rid platformer — $arm design on Flash-Next (prod pods)" > logs/build.platformer.$arm.prod.log
  python - "$rid" >> logs/build.platformer.$arm.prod.log 2>&1 <<'PY'
import sys, logging
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
from maestro.codegen.run import _await_build
r = _await_build(sys.argv[1])
print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
  rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
  echo -e "platformer\tprod-$arm\t$rid" >> builds.tsv
done
echo ALLDONE > prod.done
