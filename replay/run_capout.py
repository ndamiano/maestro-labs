import sys, time
from pathlib import Path
import probe, arms_capout

run = sys.argv[1]; k = int(sys.argv[2]); positions = [int(x) for x in sys.argv[3:]]
src = Path("/home/nick/output/runs") / run
allsamples = []
for pos in positions:
    t0 = time.time()
    try:
        s = probe.probe(src, pos, arms_capout.ARMS, k=k,
                        workdir=Path("/home/nick/output/probe-work"))
    except Exception as e:
        print(f"\n--- position {pos}: SKIPPED ({e})", flush=True); continue
    allsamples += s
    print(f"\n--- position {pos}  ({time.time()-t0:.0f}s)", flush=True)
    print(probe.report(s), flush=True)
    for x in s:
        tag = x.error or ("wrote " + ",".join(x.tools_called))
        print(f"    {x.arm:20} gen={x.generated:7} {tag}", flush=True)
print("\n=== all positions", flush=True)
print(probe.report(allsamples), flush=True)
