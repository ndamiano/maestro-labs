#!/usr/bin/env bash
# One build under the layered build prompt: variants/build_layered.txt swapped in for
# src/maestro/codegen/prompts/build.txt for the run (restored on exit), the spec seeded as
# design.md and the tool docs as docs/ in the game folder, a two-line user prompt.
# Usage: ./build_layered.sh designs/collector.team_integrate_p2.xhigh.md collector "label"
set -u
LAB="$(cd "$(dirname "$0")" && pwd)"; cd "$LAB/../.."; REPO="$PWD"
P="$REPO/src/maestro/codegen/prompts/build.txt"
cp "$P" "$LAB/build.txt.orig"
trap 'cp "$LAB/build.txt.orig" "$P"; echo "build.txt restored"' EXIT
cp "$LAB/variants/build_layered.txt" "$P"
source venv/bin/activate; cd src
python3 - "$LAB/$1" "$2" "$3" "${STEPS:-200}" "$LAB" <<'PY'
import json, logging, shutil, sys
from pathlib import Path
from auth import store
from billing.packages import MICROS_PER_CREDIT
from db import games
from maestro.state import RunState
from maestro.codegen.staging import game_dir
from maestro.codegen.run import create_run, open_ask, set_prompt, run_build
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
design, slug, label, steps, lab = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]), Path(sys.argv[5])
ask = dict(json.load(open(lab / "asks.json")))[slug]
rid = create_run(store.list_users()[0].id); games.charge_game(rid, 0, MICROS_PER_CREDIT)
open_ask(rid, label)
d = game_dir(RunState(rid).run_dir); (d / "docs").mkdir(parents=True, exist_ok=True)
(d / "design.md").write_text(design.read_text())
for f in (lab / "variants" / "docs").glob("*.md"): shutil.copy(f, d / "docs" / f.name)
set_prompt(rid, f"A user asked for: {ask}\n\nYour design team wrote the build spec in design.md, a well structured document with sections for each system you need to implement, and a section on build order.")
print(f"run: {rid} {label}", flush=True)
r = run_build(rid, max_steps=steps)
print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
