import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from lib.replay import replay
import sys
r = replay.run_to_position(Path(sys.argv[1]), 999, Path(sys.argv[2]))
for t in r.diverged:
    if t.turn != int(sys.argv[3]): continue
    for ln in [l.strip() for l in t.replayed.splitlines() if l.strip()]:
        if ln not in t.recorded:
            print("FIRST LINE NOT IN RECORDING:\n  ", ln[:300])
            import difflib
            near = difflib.get_close_matches(ln, [l.strip() for l in t.recorded.splitlines()], 1, 0.5)
            print("  closest recorded:\n  ", (near[0][:300] if near else "(nothing close)"))
            break
