import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from pathlib import Path
from lib.replay import probe
import arms_compaction

src = Path(sys.argv[1]); k = int(sys.argv[2]); positions = [int(x) for x in sys.argv[3:]]
avail = probe.compaction_positions(src)
print(f"{src.name}: compactions at {avail[:12]}{' ...' if len(avail)>12 else ''}")
chosen = positions or avail[:1]
all_samples = []
for pos in chosen:
    t0 = time.time()
    s = probe.probe(src, pos, arms_compaction.ARMS, k=k,
                    workdir=Path("/home/nick/output/probe-work"), before_compaction=True)
    all_samples += s
    print(f"\n--- position {pos}  ({time.time()-t0:.0f}s)")
    print(probe.report(s))
if len(chosen) > 1:
    print("\n=== all positions"); print(probe.report(all_samples))
