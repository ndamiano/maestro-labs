"""Does a nudge at ten no-write turns end the circling, or end the build early?

Four prod builds by people who are not us, and every one has a stretch where the model stops
writing and reads instead. The longest run to a first `done`: 20 turns on 345fcb132db8, 12 on
e153dddc53b6, and 68 — the whole build — on the fix that capped out and shipped nothing. Ten
consecutive no-write turns is where the four part: the three that converged crossed it once each,
the one that failed never came back from it.

The streak is a COUNTER on the cursor, never a scan of the transcript. Compaction drops the rounds
the reading happened in — at turn 145 of 74a9f0b3 the live history had lost every turn of the
twenty-turn stretch — so a transcript scan measures what the model can still see and the build's
own behaviour goes unmeasured. `no_call_streak` is a counter for the same reason.

The nudge is a USER message, not a tool result. `_done_nudge` rides the tool result because it
answers the `done` CALL; this one answers nothing — it is the system interrupting because ten turns
changed no file, which is the shape of `_nudge(no_call_streak)` at build_steps.py:216, itself a
user message.

Spending `done_nudged` here is deliberate: the build has already been asked what is unfinished, so
the next `done` ends it and the error gate takes over.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List, Optional

STREAK = 10

NUDGE = ("You have read the project ten turns running without changing it. If you are chasing a "
         "specific bug, say which and keep going. Otherwise the game is as finished as reading "
         "will make it — call done.")

_WRITES = re.compile(r"\b(write_file|edit_file)\s*\(")
_LEDGER = re.compile(r"\[what the program called:(.*?)\n\]", re.S)
_CALL = re.compile(r"^\s*(\w+)\s")


def _program(message: Dict) -> Optional[str]:
    for tc in message.get("tool_calls") or []:
        fn = tc.get("function") or {}
        if fn.get("name") != "python":
            continue
        try:
            return json.loads(fn.get("arguments") or "{}").get("code") or ""
        except (ValueError, TypeError):
            return ""
    return None


def _newest_program(history: List[Dict]) -> Optional[str]:
    for m in reversed(history):
        if m.get("role") == "assistant":
            code = _program(m)
            if code is not None:
                return code
    return None


def seed_at(run_dir, build_id: str, position: int) -> tuple:
    """(streak, wrote_anything) as the real build stood entering `position`.

    Read off the recorded LEDGERS — what each program actually called — so a branch starts its
    counter where the build's own was rather than at zero.
    """
    turns, cur = [], None
    for line in open(f"{run_dir}/turns.jsonl", encoding="utf-8"):
        r = json.loads(line)
        if r.get("kind") == "meta":
            cur = r.get("build_id")
        elif r.get("kind") == "turn" and cur == build_id:
            turns.append(r)
    wrote_by_turn = {}
    for i, r in enumerate(turns):
        for m in r["added"]:
            if m.get("role") != "tool":
                continue
            mm = _LEDGER.search(m.get("content") or "")
            if mm and i > 0:
                names = [_CALL.match(l).group(1) for l in mm.group(1).splitlines() if _CALL.match(l)]
                wrote_by_turn[turns[i - 1]["turn"]] = sum(
                    1 for n in names if n in ("write_file", "edit_file"))
    streak, wrote = 0, False
    for r in turns:
        if r["turn"] >= position:
            break
        if wrote_by_turn.get(r["turn"], 0):
            wrote, streak = True, 0
        else:
            streak += 1
    return streak, wrote


def install(seed: int = 0, wrote: bool = False, floor: bool = False,
            min_turn: int = 0) -> Dict[str, object]:
    """Patch `_infer` — the one place a request is built from the cursor's own history, so the
    nudge is in the transcript the very next turn reads and not one turn late.

    Two floors, each holding the nudge off the opening of a build, by different tests:

    `floor=True` waits for the build to have written something at least once. `min_turn=N` waits
    for turn N whatever the build has done. A fix opens on an empty transcript and has to read the
    game back before it can touch anything — a736b59e read for thirty turns, made one correct edit
    and finished — and three of the six fire points in the corpus are that opening. The turn floor
    is the cruder of the two and the one that cannot be fooled by an early write that changes
    nothing.
    """
    from maestro.codegen import build_steps

    was = {"_infer": build_steps._infer, "fired": [], "held": [], "state": {
        "streak": seed, "wrote": wrote, "scored": None}}
    st = was["state"]

    def _infer(run_dir, cursor, report=None, *, full_window=False):
        # A resend of a reply that ran out of room is the same turn again, not a new one.
        if report is None and st["scored"] != cursor.turn:
            st["scored"] = cursor.turn
            code = _newest_program(cursor.history)
            if code is not None:
                if _WRITES.search(code):
                    st["streak"], st["wrote"] = 0, True
                else:
                    st["streak"] += 1
        if report is None and not cursor.done_nudged and st["streak"] >= STREAK \
                and (not floor or st["wrote"]) and cursor.turn >= min_turn:
            cursor.done_nudged = True
            cursor.history.append({"role": "user", "content": NUDGE})
            was["fired"].append(cursor.turn)
            print(f"    [nudge fired at turn {cursor.turn}, streak {st['streak']}]", flush=True)
        elif report is None and not cursor.done_nudged and st["streak"] >= STREAK:
            was["held"].append(cursor.turn)
            print(f"    [nudge HELD at turn {cursor.turn}, streak {st['streak']}: "
                  f"{'no write yet' if floor and not st['wrote'] else f'before turn {min_turn}'}]",
                  flush=True)
        return was["_infer"](run_dir, cursor, report=report, full_window=full_window)

    build_steps._infer = _infer
    return was


def restore(was: Dict[str, object]) -> None:
    from maestro.codegen import build_steps

    build_steps._infer = was["_infer"]
