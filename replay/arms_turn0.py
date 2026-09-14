"""Curbing turn 0.

Measured over 162 original builds: turn 0 generates a mean of 15,584 tokens, p75 24K, p90 50K, max
121,237 — 16.3% of a whole build's token spend in ONE turn, before a single file exists. Five of
those builds thought until the budget died and called no tool at all, 5-13 minutes each for nothing.

The model writes the whole game inside its think before the first call. These arms try to buy the
first tool call sooner, and the question each one answers is the same: does the turn still produce a
real first program, or did we just make it think less and do less?

Two things are held constant so the comparison means something: the position (every arm answers the
SAME build's turn 0) and the sampling (k per arm, temp 0.7).
"""


from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List

from lib.replay import probe

FIRST_CALL_SOON = (
    "\n\nWrite your first program now. Create index.html and one JavaScript file with the game "
    "loop in it, and print what you wrote. You have many turns after this one: the rest of the "
    "systems are written in those, against files that already exist."
)

NOT_THE_WHOLE_GAME = (
    "\n\nDo not design the whole game before your first call. Decide the file layout and the one "
    "record every system will write to, then write those files."
)

BUDGET = (
    "\n\nSpend your thinking on the FILE LAYOUT and the records, not on the code — the code goes in "
    "the program itself, where it can run and be checked. A long plan that never reaches a tool "
    "call is a turn spent for nothing."
)


def _append_to_request(messages: List[Dict], text: str) -> List[Dict]:
    """The build's one user message is the request; every arm here changes only that."""
    out = [dict(m) for m in messages]
    for i in range(len(out) - 1, -1, -1):
        if out[i].get("role") == "user" and out[i].get("content"):
            out[i] = dict(out[i], content=str(out[i]["content"]) + text)
            return out
    raise ValueError("no user message to append to")


ARMS = [
    probe.Arm("baseline", lambda w, m: [dict(x) for x in m]),
    probe.Arm("first-call-soon", lambda w, m: _append_to_request(m, FIRST_CALL_SOON)),
    probe.Arm("not-the-whole-game", lambda w, m: _append_to_request(m, NOT_THE_WHOLE_GAME)),
    probe.Arm("think-layout-not-code", lambda w, m: _append_to_request(m, BUDGET)),
    # Not expressible as a message: the effort knob itself.
    probe.Arm("reasoning-low", lambda w, m: [dict(x) for x in m], reasoning="low"),
]
