import sys, time
from pathlib import Path
import probe, arms_turn0

k = int(sys.argv[1]); runs = sys.argv[2:]
allsamples = []
for run in runs:
    src = Path("/home/nick/output/runs") / run
    t0 = time.time()
    try:
        s = probe.probe(src, 0, arms_turn0.ARMS, k=k,
                        workdir=Path("/home/nick/output/probe-work"))
    except Exception as e:
        print(f"\n--- position {run}: SKIPPED ({e})", flush=True); continue
    allsamples += s
    print(f"\n--- position {run}  ({time.time()-t0:.0f}s)", flush=True)
    print(probe.report(s), flush=True)
print("\n=== all positions", flush=True)
print(probe.report(allsamples), flush=True)
