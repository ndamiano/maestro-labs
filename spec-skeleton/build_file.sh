#!/usr/bin/env bash
# One build with the spec as design.md in the game folder and a two-line prompt, through the prod
# build path. Usage: ./build_file.sh designs/collector.team_integrate_p2.xhigh.md collector "label"
set -u
LAB="$(cd "$(dirname "$0")" && pwd)"; cd "$LAB/../.."; source venv/bin/activate; cd src
python3 - "$LAB/$1" "$2" "$3" "${STEPS:-200}" "$LAB/asks.json" <<'PY'
import json, logging, sys
from pathlib import Path
from auth import store
from billing.packages import MICROS_PER_CREDIT
from db import games
from maestro.state import RunState
from maestro.codegen.staging import game_dir
from maestro.codegen.run import create_run, open_ask, set_prompt, run_build
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
design, slug, label, steps, asks = Path(sys.argv[1]), sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
ask = dict(json.load(open(asks)))[slug]
rid = create_run(store.list_users()[0].id); games.charge_game(rid, 0, MICROS_PER_CREDIT)
open_ask(rid, label)
d = game_dir(RunState(rid).run_dir); d.mkdir(parents=True, exist_ok=True)
(d / "design.md").write_text(design.read_text())
set_prompt(rid, f"A user asked for: {ask}\n\nYour design team wrote the build spec in design.md, a well structured document with sections for each system you need to implement, and a section on build order.")
print(f"run: {rid} {label}", flush=True)
r = run_build(rid, max_steps=steps)
print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
