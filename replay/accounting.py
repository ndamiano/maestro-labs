"""Where a build's tokens actually go.

Completion tokens are the ones that cost GPU seconds and wall clock — a prompt token is prefilled at
~7,000/s against a decode of ~150/s, and most of the prompt is cache-reused across a build's turns.
So the accounting below is of what the model WROTE, split by what the turn did with it.
"""
import json, glob, re, statistics, sys
from collections import defaultdict

READ  = re.compile(r"read_file\(")
WRITE = re.compile(r"(write_file|edit_file)\(")
ART   = re.compile(r"(generate_media|compose_world)\(")
DONE  = re.compile(r"\bdone\(")
CHECK = re.compile(r"check_syntax\(")

def programs(r):
    """The turn's program source, and the tool NAMES it called.

    The corpus spans two harnesses: one python program per turn, and before it seven JSON tools with
    no program at all. A classifier that only reads `code` files every pre-program turn under
    "other", which is how 70.8% of the spend hid there.
    """
    code, names = [], []
    for tc in ((r.get("response") or {}).get("tool_calls") or []):
        fn = tc.get("function") or {}
        names.append(fn.get("name") or "")
        try: code.append(json.loads(fn.get("arguments") or "{}").get("code") or "")
        except Exception: pass
    return code, names

def classify(n, code, names, called):
    if not called:            return "no tool call (thought, emitted nothing)"
    if n == 0:                return "turn 0 (the opening think)"
    # A program calls `write_file(`; a JSON tool call is NAMED write_file with no parens. Matching
    # only the call syntax filed every pre-program turn under "other".
    hay = code + " " + " ".join(f"{x}(" for x in names if x)
    if DONE.search(hay):      return "done / the nudge round"
    if WRITE.search(hay):     return "writing files"
    if ART.search(hay):       return "asking for art"
    if "python" in names and not code: return "a program that would not parse"
    if CHECK.search(hay):     return "checking syntax"
    if READ.search(hay):      return "reading only"
    return "other (a tool call that matched nothing)"

def main(paths):
    spend = defaultdict(int); counts = defaultdict(int); per_turn = defaultdict(list)
    kind_spend = defaultdict(int)     # original build vs everything after (gate fixes, changes)
    reasoning_seen = reasoning_tok = 0
    builds = 0
    for f in paths:
        metas = 0; n = 0
        for line in open(f, encoding="utf-8"):
            r = json.loads(line)
            if r["kind"] == "meta":
                metas += 1; n = 0; builds += 1; continue
            if r["kind"] != "turn": continue
            u = r.get("usage") or {}
            gen = u.get("completion_tokens") or 0
            if u.get("reasoning_tokens"): reasoning_seen += 1; reasoning_tok += u["reasoning_tokens"]
            code_parts, names = programs(r)
            code = "\n".join(code_parts)
            called = bool((r.get("response") or {}).get("tool_calls"))
            bucket = classify(n, code, names, called)
            spend[bucket] += gen; counts[bucket] += 1; per_turn[bucket].append(gen)
            kind_spend["the original build" if metas == 1 else "gate fixes and changes"] += gen
            n += 1
    total = sum(spend.values())
    print(f"{builds} builds across {len(paths)} runs, {sum(counts.values())} turns, "
          f"{total/1e6:.2f}M generated tokens\n")
    print(f"{'where the tokens went':38} {'tokens':>10} {'share':>7} {'turns':>7} {'median/turn':>12}")
    for k in sorted(spend, key=spend.get, reverse=True):
        med = statistics.median(per_turn[k]) if per_turn[k] else 0
        print(f"{k:38} {spend[k]:10,} {spend[k]/total:6.1%} {counts[k]:7} {med:12,.0f}")
    print()
    for k, v in sorted(kind_spend.items(), key=lambda x: -x[1]):
        print(f"{k:38} {v:10,} {v/total:6.1%}")
    if reasoning_seen:
        print(f"\nturns reporting reasoning_tokens: {reasoning_seen} ({reasoning_tok/1e6:.2f}M tokens)")

def era(f):
    """Which harness this run was built by. The corpus is mostly the JSON-tool harness we no longer
    run, and pooling the two describes a machine that does not exist."""
    for line in open(f, encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") != "meta": continue
        return "program" if "python" in [(t.get("function") or {}).get("name")
                                         for t in (r.get("tools") or [])] else "json-tools"
    return "empty"


if __name__ == "__main__":
    files = sorted(glob.glob("/home/nick/output/runs/*/turns.jsonl"))
    want = sys.argv[1] if len(sys.argv) > 1 else "program"
    picked = [f for f in files if era(f) == want]
    print(f"=== {want} era: {len(picked)} runs\n")
    main(picked)
