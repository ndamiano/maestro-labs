#!/usr/bin/env bash
# raise_cap.sh <run id> <max steps>: a build that ended at its step cap goes on from its recorded
# position — same transcript, same game folder — under a higher cap. The cursor goes back to
# phase build, the DB build row back to running, and build_chain.resume re-drives it; the control
# plane drives every turn after that. Needs the control plane and local_gpu auto up.
set -u
cd "$(dirname "$0")/../.."; source venv/bin/activate; cd src
python3 - "$1" "$2" <<'PY'
import logging, sys
from db import games
from maestro.state import RunState
from maestro.codegen import build_chain, build_state
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s: %(message)s")
rid, cap = sys.argv[1], int(sys.argv[2])
rs = RunState(rid); c = build_state.load(rs.run_dir)
assert c.phase == "done" and not c.finished, f"not a capped build: phase={c.phase} finished={c.finished}"
print(f"{rid}: step {c.step}, cap {c.max_steps} -> {cap}, {len(c.history)} messages, {c.compacted} compactions")
c.phase, c.max_steps, c.ok = "build", cap, None
build_state.save(rs.run_dir, c)
games.build_started(c.build_id)
build_chain.resume(rid)
print("resumed", rid)
PY
