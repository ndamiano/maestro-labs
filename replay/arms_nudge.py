"""Does the cap-out nudge cause the next cap-out?

`8c824b3e2976` ran the window dry at turns 41, 55, 59, 63, 68 and 72. Replayed from the transcript
as it stood BEFORE each of those turns, the same prompts fail at 5.6% (2 of 36) — six in a row at
that rate is roughly one in ten million, so something the replay does not carry was driving it.

The candidate is the recovery itself. After a cap-out the driver appends an empty assistant message
and a user message saying the last reply was cut off and to write in smaller pieces, and every later
turn carries it. These arms take a position that HAS that exchange and remove it.

If the rate drops with it gone, the nudge is not merely ineffective — it is causal, and the fix is
to resample the turn rather than to tell the model it failed.
"""

from __future__ import annotations

from typing import Dict, List

import probe

CUT_OFF = "cut off by the output token limit"


def _strip_nudge(messages: List[Dict]) -> List[Dict]:
    """Drop the cut-off exchange: the user nudge and the empty assistant turn before it.

    The empty assistant message goes too — a reply that carried nothing is the record of the failure,
    and leaving it is leaving half the thing under test.
    """
    out, dropped = [], 0
    for m in messages:
        if m.get("role") == "user" and CUT_OFF in str(m.get("content", "")):
            dropped += 1
            if out and out[-1].get("role") == "assistant" and not str(out[-1].get("content") or "") \
                    and not out[-1].get("tool_calls"):
                out.pop()
            continue
        out.append(dict(m))
    if not dropped:
        raise ValueError("no cap-out nudge in this transcript — nothing to remove")
    return out


ARMS = [
    probe.Arm("nudge-as-recorded", lambda w, m: [dict(x) for x in m]),
    probe.Arm("nudge-removed", lambda w, m: _strip_nudge(m)),
]
