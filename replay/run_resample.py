"""One position, many samples, printing what each one COST.

The question is not whether the median turn is small — it is how often the same prompt goes over a
ceiling. That is a tail, so only the individual samples answer it.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time, statistics
from pathlib import Path
from lib.replay import probe
import arms_rate

run, pos, k = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
src = Path("/home/nick/output/runs") / run
t0 = time.time()
s = probe.probe(src, pos, arms_rate.ARMS, k=k, workdir=Path("/home/nick/output/probe-work"))
gens = [x.generated for x in s]
print(f"\n{run} turn {pos}: {k} samples in {time.time()-t0:.0f}s", flush=True)
for x in s:
    print(f"   gen={x.generated:7,}  {'NO TOOL CALL' if x.error else 'called ' + ','.join(x.tools_called or ['(none)'])}")
print(f"   median={statistics.median(gens):,.0f}  max={max(gens):,}  "
      f"over 30K: {sum(1 for g in gens if g > 30000)}/{k}  "
      f"over 24K: {sum(1 for g in gens if g > 24000)}/{k}")
