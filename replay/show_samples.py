import sys
from pathlib import Path
import probe, arms_compaction
s = probe.probe(Path(sys.argv[1]), int(sys.argv[2]), arms_compaction.ARMS, k=1,
                workdir=Path("/home/nick/output/probe-work"))
for x in s:
    print(f"--- {x.arm}: tools={x.tools_called} reads={x.reads} program={len(x.program)} chars")
    print("   ", x.program[:220].replace("\n", " ⏎ "))
