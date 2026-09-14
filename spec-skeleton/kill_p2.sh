#!/usr/bin/env bash
# Stops the build that auto-starts when the stale split-p2 design lands, for up to 15 min.
cd "$(dirname "$0")/../.."; for i in $(seq 30); do venv/bin/python - <<'PY' 2>/dev/null
import sys; sys.path.insert(0,"src")
from db import jobs; from maestro.codegen import build_chain
build_chain.stop("72950076d395"); jobs.abandon_game_jobs("72950076d395","lab: stale split p2")
PY
sleep 30; done
