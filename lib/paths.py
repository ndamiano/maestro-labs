"""Where things are, once, instead of an absolute path in every script."""
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parents[1]
REPO = LABS.parent
SRC = REPO / "src"
OUTPUT = Path.home() / "output"
RUNS = OUTPUT / "runs"


def bootstrap() -> None:
    for p in (str(SRC), str(LABS)):
        if p not in sys.path:
            sys.path.insert(0, p)
