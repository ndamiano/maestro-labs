"""Two triggers replayed over every recorded build, no model in the loop.

STREAK: ten consecutive turns whose program wrote nothing (the readstreak counter).
FINGERPRINT: SWE-agent's doom-loop rule — a call fingerprint seen 3+ times in a window of the
last 20 calls. Two grains, because the ledger records name+path only:
  loose  = (tool, path) from the ledger
  strict = sha1 of the whole program source (the model sent the same program again)

For every fire: how many turns until the next write, and until done. The RECALL number is the
share of fires that a write follows within 5 turns — the fraction of run-ups a nudge there
would interrupt.

    python offline_triggers.py [turns.jsonl ...]     default: corpus + ~/output/runs
"""

import glob
import hashlib
import json
import re
import sys
from collections import Counter, deque

STREAK = 10
WINDOW = 20
REPEATS = 3
SOON = 5

LEDGER = re.compile(r"\[what the program called:(.*?)\n\]", re.S)
CALL = re.compile(r"^\s*(\w+)(?:\s+(\S+))?")


def builds(path):
    cur = None
    for line in open(path, encoding="utf-8"):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        k = r.get("kind")
        if k == "meta":
            if cur:
                yield cur
            cur = {"build_id": r.get("build_id"), "model": r.get("model"),
                   "tools": [t.get("function", {}).get("name") for t in (r.get("tools") or [])],
                   "turns": []}
        elif k == "turn" and cur is not None:
            cur["turns"].append(r)
    if cur:
        yield cur


def program(r):
    tc = (r.get("response") or {}).get("tool_calls") or []
    if not tc:
        return None
    try:
        return json.loads(tc[0]["function"]["arguments"]).get("code", "")
    except (ValueError, KeyError, TypeError):
        return ""


def ledger_calls(turns):
    """turn -> [(tool, path)] for the program that turn ran, read off the next turn's ledger."""
    out = {}
    for i, r in enumerate(turns):
        for m in r["added"]:
            if m.get("role") != "tool":
                continue
            mm = LEDGER.search(m.get("content") or "")
            if mm and i > 0:
                calls = []
                for l in mm.group(1).splitlines():
                    c = CALL.match(l)
                    if c and c.group(1):
                        calls.append((c.group(1), c.group(2) or ""))
                out[turns[i - 1]["turn"]] = calls
    return out


def analyse(b):
    ts = b["turns"]
    led = ledger_calls(ts)
    done_turn = next((r["turn"] for r in ts if "done(" in (program(r) or "")), None)
    end = done_turn if done_turn is not None else ts[-1]["turn"]
    core = [r for r in ts if r["turn"] <= end]
    wrote = {t: any(n in ("write_file", "edit_file") for n, _ in calls) for t, calls in led.items()}
    write_turns = sorted(t for t, w in wrote.items() if w)

    def next_write(t):
        return next((w - t for w in write_turns if w > t), None)

    fires = {"streak": [], "loose": [], "strict": []}
    streak = 0
    loose_win, strict_win = deque(), deque()
    loose_armed = strict_armed = True
    for r in core:
        t = r["turn"]
        if wrote.get(t):
            streak = 0
        else:
            streak += 1
            if streak == STREAK:
                fires["streak"].append(t)
        for fp in led.get(t, []):
            loose_win.append(fp)
            while len(loose_win) > WINDOW:
                loose_win.popleft()
        src = program(r)
        if src:
            strict_win.append(hashlib.sha1(src.encode()).hexdigest())
            while len(strict_win) > WINDOW:
                strict_win.popleft()
        # fire once per stretch: re-arm only after a turn with no repeat
        lc = Counter(loose_win)
        if lc and max(lc.values()) >= REPEATS:
            if loose_armed:
                fires["loose"].append(t)
                loose_armed = False
        else:
            loose_armed = True
        sc = Counter(strict_win)
        if sc and max(sc.values()) >= REPEATS:
            if strict_armed:
                fires["strict"].append(t)
                strict_armed = False
        else:
            strict_armed = True

    def describe(t):
        nw = next_write(t)
        nd = (done_turn - t) if done_turn is not None and done_turn > t else None
        return {"turn": t, "next_write": nw, "to_done": nd}

    return {"build": b["build_id"][:8], "model": b["model"], "turns": len(core),
            "done": done_turn, "capped": done_turn is None,
            "writes": len(write_turns),
            "fires": {k: [describe(t) for t in v] for k, v in fires.items()}}


def main(paths):
    rows = []
    for p in paths:
        for b in builds(p):
            if "python" not in (b["tools"] or []) or len(b["turns"]) < 15:
                continue
            a = analyse(b)
            a["run"] = p.split("/")[-2][:8]
            rows.append(a)

    def fmt(f):
        nw = "never" if f["next_write"] is None else f"+{f['next_write']}"
        return f"{f['turn']}(w{nw})"

    print(f"{'run':9} {'build':9} {'model':16} {'turns':>5} {'done':>5} {'wr':>3} | streak fires | loose fp | strict fp")
    for a in rows:
        f = a["fires"]
        print(f"{a['run']:9} {a['build']:9} {str(a['model'])[:16]:16} {a['turns']:>5} "
              f"{str(a['done'] if a['done'] is not None else 'CAP'):>5} {a['writes']:>3} | "
              f"{' '.join(map(fmt, f['streak'])) or '-'} | "
              f"{len(f['loose'])}:{' '.join(map(fmt, f['loose'][:4]))}{'…' if len(f['loose']) > 4 else ''} | "
              f"{len(f['strict'])}:{' '.join(map(fmt, f['strict'][:4]))}")

    print()
    for kind in ("streak", "loose", "strict"):
        for model_sel in ("all", "pennyroyal", "local"):
            fs = [f for a in rows for f in a["fires"][kind]
                  if model_sel == "all" or (a["model"] == "pennyroyal") == (model_sel == "pennyroyal")]
            if not fs:
                continue
            soon = sum(1 for f in fs if f["next_write"] is not None and f["next_write"] <= SOON)
            later = sum(1 for f in fs if f["next_write"] is not None and f["next_write"] > SOON)
            never = sum(1 for f in fs if f["next_write"] is None)
            n_b = sum(1 for a in rows if a["fires"][kind]
                      and (model_sel == "all" or (a["model"] == "pennyroyal") == (model_sel == "pennyroyal")))
            print(f"{kind:7} {model_sel:10} fires={len(fs):3} in {n_b} builds | "
                  f"write within {SOON}: {soon} ({soon / len(fs):.0%}) | later: {later} | never: {never}")


if __name__ == "__main__":
    paths = sys.argv[1:] or (sorted(glob.glob("/home/nick/output/replay-corpus/*/turns.jsonl"))
                             + sorted(glob.glob("/home/nick/output/runs/*/turns.jsonl")))
    main(paths)
