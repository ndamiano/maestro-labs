import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time, importlib
from pathlib import Path
from lib.replay import probe

mod = importlib.import_module(sys.argv[1])
src = Path(sys.argv[2]); k = int(sys.argv[3]); positions = [int(x) for x in sys.argv[4:]]
allsamples = []
for pos in positions:
    t0 = time.time()
    try:
        s = probe.probe(src, pos, mod.ARMS, k=k, workdir=Path("/home/nick/output/probe-work"),
                        before_compaction=True)
    except Exception as e:
        print(f"\n--- position {pos}: SKIPPED ({e})", flush=True); continue
    allsamples += s
    print(f"\n--- position {pos}  ({time.time()-t0:.0f}s)", flush=True)
    print(probe.report(s), flush=True)
print("\n=== all positions", flush=True)
print(probe.report(allsamples), flush=True)
