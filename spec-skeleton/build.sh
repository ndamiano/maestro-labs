#!/usr/bin/env bash
# One build from a saved design pinned as the prompt (no designer call), through the prod build path.
# Needs the control plane (venv/bin/python run.py from the repo root) and ./worker.sh up.
# Usage: ./build.sh designs/island.skel.xhigh.md "island — skel xhigh"   (STEPS=200 default)
set -u
LAB="$(cd "$(dirname "$0")" && pwd)"; cd "$LAB/../.."; source venv/bin/activate; cd src
python3 - "$LAB/$1" "$2" "${STEPS:-200}" <<'PY'
import logging, sys
from pathlib import Path
from auth import store
from billing.packages import MICROS_PER_CREDIT
from db import games
from maestro.codegen.run import create_run, open_ask, set_prompt, run_build
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
design, label, steps = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3])
rid = create_run(store.list_users()[0].id); games.charge_game(rid, 0, MICROS_PER_CREDIT)
open_ask(rid, label)
set_prompt(rid, design.read_text())
print(f"run: {rid} {label}", flush=True)
r = run_build(rid, max_steps=steps)
print("result:", r.ok, r.steps, f"{r.elapsed:.0f}s", r.summary, flush=True)
PY
