"""One position, two arms, k branches each: does the ten-read nudge end the circling?

    python run_readstreak.py <run_dir> <build_id> <position> [turns] [k] [arms]

The patch is installed and removed here around the whole k-loop, so the branch is handed neither
`install` nor `restore`.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import sys
import time
from pathlib import Path

import arms_readstreak
from lib.replay import branch
from lib.replay import direct

direct.install()

src = Path(sys.argv[1])
build = sys.argv[2]
position = int(sys.argv[3])
turns = int(sys.argv[4]) if len(sys.argv) > 4 else 8
k = int(sys.argv[5]) if len(sys.argv) > 5 else 2
arms = (sys.argv[6] if len(sys.argv) > 6 else "control,nudge").split(",")

OUT = Path("/home/nick/output/branch-work/readstreak.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)
stamp = time.strftime("%m%d-%H%M%S")

for arm in arms:
    for i in range(k):
        label = f"{arm}-{src.name[:6]}-{build[:6]}-{stamp}-s{i}"
        print(f"\n=== {arm} sample {i} @ {src.name}/{build[:8]} position {position} ===", flush=True)
        was = None
        if arm.startswith("nudge"):
            seed, wrote = arms_readstreak.seed_at(src, build, position)
            min_turn = int(arm.split("-t")[1]) if "-t" in arm else 0
            was = arms_readstreak.install(seed=seed, wrote=wrote,
                                          floor=(arm == "nudge-floor"),
                                          min_turn=min_turn)
        try:
            out = branch.run(src, position, turns, install=None, arm=label,
                             build=build, reasoning="medium")
        except Exception as e:
            print(f"  BRANCH FAILED: {type(e).__name__}: {e}", flush=True)
            continue
        finally:
            if was is not None:
                arms_readstreak.restore(was)
        wrote = sum(1 for t in out.turns
                    if any(x in t.tools_called for x in ("write_file", "edit_file")))
        called_done = any("done" in t.tools_called for t in out.turns)
        rec = {"arm": arm, "sample": i, "run": src.name, "build": build, "position": position,
               "turns": len(out.turns), "stopped": out.stopped,
               "nudge_fired_at": (was or {}).get("fired", []),
               "nudge_held_at": (was or {}).get("held", []),
               "write_turns": wrote, "called_done": called_done,
               "reads": sum(len(t.reads) for t in out.turns),
               "repeat_reads": sum(len(t.repeat_reads) for t in out.turns),
               "seconds": sum(t.seconds for t in out.turns),
               "tools": [t.tools_called for t in out.turns],
               # per turn, so write payload and think cost can be split after the fact — the
               # branch dirs carry no turn log of their own (build_chain writes those, not
               # build_steps), so anything not kept here is gone.
               "per_turn": [{"turn": t.turn, "gen": t.generated, "prompt": t.prompt_tokens,
                             "secs": round(t.seconds, 1), "tools": t.tools_called,
                             "reads": len(t.reads), "repeat": len(t.repeat_reads),
                             "error": t.error} for t in out.turns]}
        with OUT.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"  -> {wrote} write turns, done={called_done}, "
              f"{rec['reads']} reads ({rec['repeat_reads']} repeat), "
              f"{rec['seconds']:.0f}s, stopped={out.stopped!r}", flush=True)
