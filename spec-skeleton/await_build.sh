#!/usr/bin/env bash
# await_build.sh <rid> <tag>: wait for a run's build, sync the game to :8765, record it.
cd "$(dirname "$0")"; REPO=$(cd ../.. && pwd); source $REPO/venv/bin/activate
python - "$1" >> logs/build.platformer.$2.par.prod.log 2>&1 <<'PY'
import sys, logging
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
from maestro.codegen.run import _await_build
r = _await_build(sys.argv[1])
print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
rsync -a --delete /home/nick/output/runs/$1/game/ $REPO/runtime/games/$1/ 2>/dev/null
echo -e "platformer\tprod-par-$2\t$1" >> builds.tsv
