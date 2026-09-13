#!/usr/bin/env bash
# ASHWORTH ablations on the local 27B: one build per design variant, serial, no designer call.
# The design is DESIGN.md in the game folder (read by section) and the request only points at it,
# so 270 KB is never pinned in every turn. three r185 + the addons the design uses are placed at
# the paths the design names. Needs the control plane on :8000 and an llm worker up.
set -u
LAB=/home/nick/Documents/Labs/ashworth-street; REPO=/home/nick/Documents/ai-agent-test
STEPS=${STEPS:-1000}
mkdir -p $LAB/logs
cd $REPO/src; source $REPO/venv/bin/activate
for V in ${VARIANTS:-full novisual noeng norig}; do
  log=$LAB/logs/ablation.$V.log; t0=$(date +%s)
  python3 - "$V" "$LAB" "$STEPS" > "$log" 2>&1 <<'PY'
import logging, shutil, sys
from pathlib import Path
from auth import store
from auth.billing import MICROS_PER_CREDIT
from db import store as db_store
from maestro.codegen.run import create_run, open_ask, set_prompt, run_build
from maestro.codegen.staging import game_dir
from maestro.state import RunState
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
v, lab, steps = sys.argv[1], Path(sys.argv[2]), int(sys.argv[3])
rid = create_run(store.list_users()[0].id); db_store.charge_game(rid, 0, MICROS_PER_CREDIT)
open_ask(rid, f"ASHWORTH ST subway FPS — ablation {v}")
set_prompt(rid, (lab / "request.txt").read_text())
g = game_dir(RunState(rid).run_dir); g.mkdir(parents=True, exist_ok=True)
shutil.copy(lab / "variants" / f"{v}.md", g / "DESIGN.md")
pkg = lab / "env" / "package"
# Under world/: code_map skips it, so the compaction note does not map three's own declarations.
three = g / "world" / "three"; (three / "addons").mkdir(parents=True, exist_ok=True)
for f in ("three.module.js", "three.core.js"):
    shutil.copy(pkg / "build" / f, three / f)
for d in ("postprocessing", "shaders", "objects", "math", "geometries", "utils", "controls"):
    shutil.copytree(pkg / "examples" / "jsm" / d, three / "addons" / d)
print(f"run: {rid} variant {v}", flush=True)
r = run_build(rid, max_steps=steps)
print("result:", r, flush=True)
PY
  rid=$(grep -m1 '^run:' "$log" | awk '{print $2}')
  echo -e "$V\t$rid\t$(( $(date +%s) - t0 ))" >> $LAB/ablation.tsv; echo "$V $rid done"
done
echo ALLDONE >> $LAB/ablation.tsv
