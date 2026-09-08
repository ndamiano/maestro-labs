"""Arm D — the widened lib/audio.js and its one build.txt line.

There is no control arm. The control is live data: of the 99 lib-era games in runtime/games, 49
import lib/audio.js, 50 do not, and ZERO run on it alone. Rebuilding that on the one card would
buy a number we already have at full sample size.

The question is why a build writes its own WebAudio instead of importing lib/audio.js. Measured
over the 99 lib-era games in runtime/games: input 88/99 imported, canvas 75/99, audio 49/99 — and
ZERO used lib/audio.js alone. So it is not adoption in general that fails; it is that the lib's
surface is eight fixed effect names and every game wants a footstep, an engine or an alarm.

Arm D widens the lib to cover those (a synth spec, a noise burst, a held sound, a sequence) and
says in one line that the game's sound IS lib/audio.js. The design is generated once per ask and
handed to both arms, so the only difference between them is the prompt and the lib.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

REPO = Path("/home/nick/Documents/ai-agent-test")
LAB = Path.home() / "Documents/Labs/lib-adoption"
SRC = REPO / "src"
PY = REPO / "venv/bin/python"
PROMPT = SRC / "maestro/codegen/prompts/build.txt"
LIB = REPO / "runtime/vendor/lib/audio.js"

ARMS = {"A": (LAB / "arms/build_A.txt", LAB / "lib_D/audio_A_backup.js"),
        "D": (LAB / "arms/build_D.txt", LAB / "lib_D/audio.js")}


def install(arm):
    prompt, lib = ARMS[arm]
    PROMPT.write_text(prompt.read_text())
    LIB.write_text(lib.read_text())


def sh(*args, **kw):
    return subprocess.run(args, cwd=SRC, capture_output=True, text=True, **kw)


def design_for(ask):
    """One design per ask, written once and reused by both arms — design variance would otherwise
    swamp the thing being measured."""
    cache = LAB / "designs" / (ask.split()[2] + "-" + str(len(ask)) + ".json")
    if cache.exists():
        return json.loads(cache.read_text())["design"]
    r = sh(str(PY), "-c",
           "import sys, json;"
           "sys.path.insert(0,'.');"
           "from maestro.codegen import design, run;"
           "from auth import store; from db import store as db;"
           "from auth.billing import SECONDS_PER_CREDIT;"
           "rid = run.create_run(store.list_users()[0].id);"
           "db.charge_game(rid, 0, SECONDS_PER_CREDIT);"
           "run.open_ask(rid, sys.argv[1]);"
           "print('DESIGN_JSON' + json.dumps({'design': design.generate(rid, sys.argv[1])}))",
           ask)
    line = next((ln for ln in r.stdout.splitlines() if ln.startswith("DESIGN_JSON")), "")
    out = json.loads(line[len("DESIGN_JSON"):]) if line else {"design": ask}
    if len(out["design"].split()) <= len(ask.split()) + 5:
        # The designer answered with the ask itself — the engine refused the request (another
        # build holding the one slot, most often). A fallback design is not the design under
        # test, so wait and ask again rather than measure the wrong thing.
        print("design refused, retrying in 120s", flush=True)
        time.sleep(120)
        return design_for(ask)
    cache.write_text(json.dumps({"ask": ask, **out}, indent=1))
    return out["design"]


def build(ask, design, arm):
    install(arm)
    r = sh(str(PY), "-c",
           "import sys;"
           "sys.path.insert(0,'.');"
           "from maestro.codegen import run;"
           "from auth import store; from db import store as db;"
           "from auth.billing import SECONDS_PER_CREDIT;"
           "rid = run.create_run(store.list_users()[0].id);"
           "db.charge_game(rid, 0, SECONDS_PER_CREDIT);"
           "run.open_ask(rid, sys.argv[1]);"
           "run.set_prompt(rid, sys.argv[2]);"
           "print('RUN' + rid);"
           "res = run.run_build(rid);"
           "print('RESULT', res.ok, res.steps, int(res.elapsed))",
           ask, design, timeout=7200)
    rid = next((ln[3:] for ln in r.stdout.splitlines() if ln.startswith("RUN")), "?")
    tail = [ln for ln in r.stdout.splitlines() if ln.startswith("RESULT")]
    return {"arm": arm, "ask": ask, "run_id": rid, "result": tail[0] if tail else r.stderr[-400:]}


def done_already() -> set:
    """(ask, arm) pairs some earlier run of this lab already built — the card is shared and a lab
    that has to be killed halfway should not pay for the same build twice."""
    out = set()
    for f in (LAB / "results").glob("*.jsonl"):
        for line in f.read_text().splitlines():
            r = json.loads(line)
            out.add((r["ask"], r["arm"]))
    return out


def main():
    asks = [a for a in (LAB / "designs/asks.txt").read_text().splitlines() if a.strip()]
    out = LAB / "results" / f"runs_{int(time.time())}.jsonl"
    have = done_already()
    try:
        for ask in asks:
            d = design_for(ask)
            print(f"design: {len(d.split())} words — {ask[:50]}", flush=True)
            for arm in ("D",):
                if (ask, arm) in have:
                    print(f"skip {arm}: already built", flush=True)
                    continue
                rec = build(ask, d, arm)
                print(json.dumps(rec), flush=True)
                with out.open("a") as f:
                    f.write(json.dumps(rec) + "\n")
    finally:
        install("A")           # the repo is left as it was found
    print("results:", out)


if __name__ == "__main__":
    sys.exit(main())
