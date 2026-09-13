"""dsh-shaped compaction: one pointer, everything to its left replaced by a model-written summary.

DeepSeek Harness (packages/compaction/compaction-basic) fires at 80% of the context window, keeps
the newest 16% of the WINDOW verbatim, and replaces the whole prefix with one summary message
written by a separate model call under eight fixed headings. The left edge is fixed at the first
message after the session prefix; the right edge is walked backward from the newest message until
the retain budget is met, then pushed further back until it sits on a round boundary.

Installed over `build_steps.compact` rather than reimplemented beside it, so the step machine, the
trigger, the ledger and the turn log are the build's own and the ONE difference is what a cut does.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Dict, List, Optional

THRESHOLD_RATIO = 0.80
RETAIN_RATIO = 0.16
SUMMARY_MAX_TOKENS = 8192

_PROMPT = Path(__file__).parent / "dsh_summary.txt"


def _tokens(messages: List[Dict]) -> int:
    return sum(len(json.dumps(m, ensure_ascii=False)) for m in messages) // 3


def select_span(messages: List[Dict], retain_tokens: int) -> int:
    """The pointer: the index the summary replaces everything before.

    Walks backward from the newest message accumulating tokens until the retain budget is spent,
    then moves the boundary OLDER until it sits between rounds — dsh's `toolPairingBalancedBefore`,
    which is `build_steps.rounds` here. Never moves forward, so the tail may exceed the budget and
    never falls under it. Index 0 is the build's one user message, dsh's session prefix: outside
    every span.
    """
    from maestro.codegen import build_steps

    kept = 0
    cut = len(messages)
    for i in range(len(messages) - 1, 0, -1):
        kept += len(json.dumps(messages[i], ensure_ascii=False)) // 3
        if kept >= retain_tokens:
            cut = i
            break
    else:
        return 1
    # Push back to a round boundary: the offsets of each round's first message, in order.
    # `rounds` skips the request itself, so the first group starts at index 1.
    groups = build_steps.rounds(messages)
    starts, at = [], 1
    for g in groups:
        starts.append(at)
        at += len(g)
    boundaries = [s for s in starts if s <= cut]
    return boundaries[-1] if boundaries else 1


def summarize(system: str, span: List[Dict]) -> Optional[str]:
    """One model call: the span replayed verbatim, then the eight-heading instruction appended.

    Whatever came back is the whole of what survives the cut, so an empty or failed answer is a
    cut that would delete the prefix and put nothing in its place — the caller must not proceed.
    """
    from llm_clients.connector import get_connector
    from maestro.codegen.build_steps import MessageBuilder

    ask = {"role": "user", "content": _PROMPT.read_text(encoding="utf-8")}
    msgs = MessageBuilder(system).extend(span + [ask]).build()
    t0 = time.time()
    result = get_connector().generate_with_tools(msgs, [], max_tokens=SUMMARY_MAX_TOKENS)
    usage = (result or {}).get("usage") or {}
    print(f"  SUMMARY gen={usage.get('completion_tokens') or 0:6} "
          f"prompt={usage.get('prompt_tokens') or 0:6} {time.time() - t0:5.1f}s", flush=True)
    if (result or {}).get("error"):
        return None
    text = ((result.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    return text.strip() or None


def compact(run_dir, cursor, keep_chars: int) -> int:
    """Signature-compatible with `build_steps.compact`; `keep_chars` is ignored, because the retain
    budget is dsh's own ratio of the window rather than the caller's char budget."""
    from maestro.codegen import build_steps

    ctx = build_steps._n_ctx()
    cut = select_span(cursor.history, int(ctx * RETAIN_RATIO))
    if cut <= 1:
        return 0                      # nothing older than the request: an indivisible tail
    summary = summarize(cursor.system, cursor.history[1:cut])
    if summary is None:
        raise RuntimeError("the summarizer returned nothing; the arm cannot cut without it")
    note = {"role": "user", "content":
            "[Earlier steps were condensed into the summary below. Every file is on disk exactly "
            "as you last wrote or read it.]\n\n" + summary}
    cursor.history = cursor.history[:1] + [note] + cursor.history[cut:]
    return 1


def install() -> Dict[str, object]:
    """Swap the cut and the trigger. Returns what was replaced, so a caller can put it back."""
    from maestro.codegen import build_steps

    was = {"compact": build_steps.compact, "room": build_steps._COMPACT_ROOM}
    build_steps.compact = compact
    build_steps._COMPACT_ROOM = int(build_steps._n_ctx() * (1 - THRESHOLD_RATIO))
    return was


def restore(was: Dict[str, object]) -> None:
    from maestro.codegen import build_steps

    build_steps.compact = was["compact"]
    build_steps._COMPACT_ROOM = was["room"]
