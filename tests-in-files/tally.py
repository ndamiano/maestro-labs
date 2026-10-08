"""Turn tally for a build: plays / reads / writes / edits, suite runs, compactions, done, cap.

    python tally.py <run id> [...]
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.replay.offline_triggers import builds, ledger_calls, program  # noqa: E402

RUNS = Path.home() / "output" / "runs"


def tally(rid):
    run = RUNS / rid
    recs = [json.loads(l) for l in open(run / "turns.jsonl", encoding="utf-8")]
    b = list(builds(run / "turns.jsonl"))[-1]
    led = ledger_calls(b["turns"])
    n = {"play": 0, "read_file": 0, "write_file": 0, "edit_file": 0, "suite": 0, "nocall": 0}
    done = None
    for r in b["turns"]:
        p = program(r)
        if p is None:
            n["nocall"] += 1
            continue
        if "tests/run.js" in p and "play(" in p:
            n["suite"] += 1
        for tool, _ in led.get(r["turn"], []):
            if tool in n:
                n[tool] += 1
            if tool == "done" and done is None:
                done = r["turn"]
    if done is None and re.search(r"^\s*done\(", program(b["turns"][-1]) or "", re.M):
        done = b["turns"][-1]["turn"]
    tests = sorted(str(p.relative_to(run / "game")) for p in (run / "game" / "tests").glob("*") ) if (run / "game" / "tests").is_dir() else []
    return {"run": rid, "turns": len(b["turns"]), "compactions": sum(r["kind"] == "compact" for r in recs),
            "done_turn": done, **n, "test_files": len(tests), "tests": tests}


if __name__ == "__main__":
    for rid in sys.argv[1:]:
        t = tally(rid)
        tests = t.pop("tests")
        print(json.dumps(t))
        print("   ", " ".join(tests) or "(no tests/)")
