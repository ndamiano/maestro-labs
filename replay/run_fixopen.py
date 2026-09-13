"""a736b5 from its opening, four arms, k branches each: when does the first edit land, and is it
the right one?

    python run_fixopen.py [turns] [k] [arms] [line_template]

line_template is the fix note's thrown-error line with {threw} in it, copied from
play_fix_note.txt once the gate carries it.
"""

import json
import re
import sys
import time
from pathlib import Path

import arms_fixopen
import branch
import direct

direct.install()

import os
SRC = Path("/home/nick/output/replay-corpus/e153dddc53b6")
BUILD = os.environ.get("FIXOPEN_BUILD", "a736b59e5e11")
FIXED = re.compile(r"surfaceAt\(\s*solidGround\s*,\s*floats\s*,\s*cx\s*\)")
BROKEN = re.compile(r"surfaceAt\(\s*solidGround\.concat\(floats\)")

turns = int(sys.argv[1]) if len(sys.argv) > 1 else 15
k = int(sys.argv[2]) if len(sys.argv) > 2 else 4
arms = (sys.argv[3] if len(sys.argv) > 3 else "control,map,threw,map-threw").split(",")
line_template = sys.argv[4] if len(sys.argv) > 4 else "What the page threw: {threw}"

OUT = Path("/home/nick/output/branch-work/fixopen.jsonl")
BASE = Path("/home/nick/output/branch-work/fixopen-base-" + BUILD[:6] + "/game")
if not BASE.exists():
    import replay
    replay.run_to_position(SRC, 0, BASE.parent, before_compaction=True, build=BUILD)
CAM0 = re.search(r"function updateCamera\(dt\) \{.*?\n\}",
                 (BASE / "js" / "main.js").read_text(encoding="utf-8"), re.S).group(0)
stamp = time.strftime("%m%d-%H%M%S")

for arm in arms:
    for i in range(k):
        label = f"fixopen-{BUILD[:6]}-{arm}-{stamp}-s{i}"
        print(f"\n=== {arm} sample {i} ===", flush=True)
        target = Path("/home/nick/output/branch-work") / f"{label}-pos0"
        was = arms_fixopen.install(arm, target / "game", line_template)
        try:
            out = branch.run(SRC, 0, turns, install=None, arm=label, build=BUILD,
                             reasoning="medium")
        except Exception as e:
            print(f"  BRANCH FAILED: {type(e).__name__}: {e}", flush=True)
            continue
        finally:
            arms_fixopen.restore(was)
        gen = (target / "game" / "js" / "gen.js").read_text(encoding="utf-8")
        main = (target / "game" / "js" / "main.js").read_text(encoding="utf-8")
        cam = re.search(r"function updateCamera\(dt\) \{.*?\n\}", main, re.S)
        first_edit = next((t.turn for t in out.turns
                           if any(x in t.tools_called for x in ("write_file", "edit_file"))), None)
        prompt_at = next((t.prompt_tokens for t in out.turns if t.turn == first_edit), None)
        rec = {"arm": arm, "sample": i, "turns": len(out.turns), "stopped": out.stopped[:200],
               "first_edit": first_edit, "prompt_at_first_edit": prompt_at,
               "fixed": bool(FIXED.search(gen)), "still_broken": bool(BROKEN.search(gen)),
               "camera_changed": bool(cam) and cam.group(0) != CAM0,
               "files_changed": sorted(p.name for p in (target / "game" / "js").glob("*.js")
                                       if p.read_bytes() != (BASE / "js" / p.name).read_bytes()),
               "called_done": any("done" in t.tools_called for t in out.turns),
               "reads": sum(len(t.reads) for t in out.turns),
               "seconds": round(sum(t.seconds for t in out.turns)),
               "opening_chars": len(was["sent"] or ""),
               "per_turn": [{"turn": t.turn, "gen": t.generated, "prompt": t.prompt_tokens,
                             "tools": t.tools_called, "reads": len(t.reads), "read_paths": t.reads,
                             "error": t.error}
                            for t in out.turns]}
        with OUT.open("a") as f:
            f.write(json.dumps(rec) + "\n")
        print(f"  -> first_edit={first_edit} prompt@edit={prompt_at} fixed={rec['fixed']} "
              f"done={rec['called_done']} reads={rec['reads']} {rec['seconds']}s", flush=True)
