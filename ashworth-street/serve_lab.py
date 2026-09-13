"""The control plane exactly as run.py starts it, with build_steps.MAX_TURNS raised for the lab.

build_steps caps every build at MAX_TURNS (200) whatever the cursor's max_steps says, and the
build's turns advance inside this process — so the cap has to be raised here, not in the runner.
"""
import os
import runpy
import sys
from pathlib import Path

REPO = Path("/home/nick/Documents/ai-agent-test")
sys.path.insert(0, str(REPO / "src"))
os.chdir(REPO)

from maestro.codegen import build_steps  # noqa: E402

build_steps.MAX_TURNS = int(os.getenv("LAB_MAX_TURNS", "1000"))
print(f"lab: build_steps.MAX_TURNS = {build_steps.MAX_TURNS}", flush=True)
runpy.run_path(str(REPO / "run.py"), run_name="__main__")
