"""Recovering from a turn that ran the window dry.

Measured on the program-era corpus: 17.3% of all generated tokens went to turns that produced no
tool call, and one build (`8c824b3e2976`) accounts for most of it — it ran the window dry at turns
41, 55, 59, 63, 68 and 72. It was nudged after the first one and did it five more times, so the
standing answer ("write the file in smaller pieces") is measured as not working.

Each arm answers the same question: from the position that produced a runaway, does this change get
a tool call out of the model, and at what token cost. An arm that produces a call cheaply but writes
nothing real is not a win, so the programs are kept for reading.
"""

from __future__ import annotations

from typing import Dict, List

import probe

ONE_UNIT = (
    "\n\nWrite ONE function or one section now, not the file. Call write_file or edit_file with it, "
    "print what you wrote, and stop. The next turn continues from what is on disk."
)

ANCHOR = (
    "\n\nTo change code that exists, call edit_file with a short unique anchor — the few lines around "
    "the change — and the replacement. Do not re-send a file you have already written: it is on disk, "
    "and re-typing it is what ran out of room last time."
)


def _append_user(messages: List[Dict], text: str) -> List[Dict]:
    """A new user message, not an edit of an old one: the runaway happened against this transcript,
    and rewriting history would measure a different position."""
    return [dict(m) for m in messages] + [{"role": "user", "content": text.strip()}]


ARMS = [
    probe.Arm("baseline", lambda w, m: [dict(x) for x in m]),
    probe.Arm("one-unit-only", lambda w, m: _append_user(m, ONE_UNIT)),
    probe.Arm("edit-not-rewrite", lambda w, m: _append_user(m, ANCHOR)),
    # The ceiling itself: the model cannot write a 40K reply if it is not allowed to.
    probe.Arm("hard-cap-8k", lambda w, m: [dict(x) for x in m], max_tokens=8000),
    probe.Arm("one-unit + cap-8k", lambda w, m: _append_user(m, ONE_UNIT), max_tokens=8000),
]
