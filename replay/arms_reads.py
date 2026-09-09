"""Five ways to stop a post-compaction re-read, measured against the one that did not work.

The block says a file is unchanged and the model reads it anyway (measured: 9/18 turns re-read with
it, 9/17 without). These arms attack the same turn from different directions, so a null across all
of them says something the block alone cannot: that the read is not about information the note
could carry.

Every arm asserts its own change landed. An arm whose edit is absent from the prompt reads exactly
like an arm that had no effect, which is how the first run of this probe produced a clean null from
two identical prompts.
"""

from __future__ import annotations

import json
import re
from typing import Dict, List

import probe
import replay

MARK = "have already read these files and they have NOT changed"
NOTE_HEAD = "[Earlier steps"


def _compacted(world: replay.Replay, messages: List[Dict], *, block: bool = True) -> List[Dict]:
    from maestro.codegen import build_steps, file_state
    from maestro.codegen.build_state import BuildCursor
    from config.settings_manager import settings_manager

    ctx = int((settings_manager.get_settings().get("llm") or {}).get("n_ctx") or 131072)
    cursor = BuildCursor(build_id="probe", turn=world.position,
                         history=[dict(m) for m in messages], logged=len(messages))
    real = file_state.render
    if not block:
        file_state.render = lambda run_dir, root: ""
    try:
        if not build_steps.compact(world.run_dir, cursor, int(ctx * build_steps._COMPACT_KEEP) * 4):
            raise ValueError("nothing compacted at this position — the arms would be identical")
    finally:
        file_state.render = real
    return cursor.history


def _note_index(messages: List[Dict]) -> int:
    for i, m in enumerate(messages):
        if m.get("role") == "user" and str(m.get("content", "")).startswith(NOTE_HEAD):
            return i
    raise ValueError("no compaction note in this transcript")


def _edit_note(messages: List[Dict], fn) -> List[Dict]:
    i = _note_index(messages)
    out = [dict(m) for m in messages]
    before = str(out[i]["content"])
    after = fn(before)
    if after == before:
        raise ValueError("the arm changed nothing in the note")
    out[i]["content"] = after
    return out


# --- the arms ---------------------------------------------------------------

def _baseline(w, m):
    """HEAD: code map plus the file-state block. The thing every other arm is compared to."""
    return _compacted(w, m, block=True)


def _forbid(w, m):
    """Say what to DO instead of what is true. The block states a fact; this states the rule."""
    def edit(note):
        i = note.find(MARK)
        if i < 0:
            raise ValueError("no file-state block to strengthen")
        return note.replace(
            MARK,
            "must NOT be read again — read_file on any of them returns the bytes you already have "
            "and spends the turn. Work from what is above; if you need a line number, it is in the "
            "map. These are the files you have already read and they have NOT changed", 1)
    return _edit_note(_compacted(w, m, block=True), edit)


def _no_map(w, m):
    """Drop the code map, keep the block. If reads are the model rebuilding the picture, taking the
    picture away should make them go UP — and if nothing moves, the map is not what they are about."""
    def edit(note):
        i = note.find(MARK)
        head = note.split("\n\n")[0]
        return head + "\n\n" + note[i - len("You "):] if i > 0 else head
    return _edit_note(_compacted(w, m, block=True), edit)


def _bodies(w, m):
    """Put the BODIES of the already-read files back, up to a budget. The one thing a read gives
    that no note does is the exact text; this is the arm that tests whether that is what it wants."""
    def edit(note):
        from maestro.codegen.staging import game_dir
        root = game_dir(w.run_dir)
        seen = sorted(probe.files_already_read(w.run_dir))
        budget, parts = 60_000, []
        for rel in seen:
            p = root / rel
            if not p.is_file():
                continue
            body = p.read_text(errors="replace")
            if len(body) > budget:
                continue
            budget -= len(body)
            parts.append(f"--- {rel} ---\n{body}")
        if not parts:
            raise ValueError("no bodies to inline at this position")
        return note + "\n\nThe current text of the files you have read:\n\n" + "\n\n".join(parts)
    return _edit_note(_compacted(w, m, block=True), edit)


def _terse(w, m):
    """The note without the prose: the map alone, no block, no instructions about reading. Tests
    whether the wording carries any of the weight the block was supposed to."""
    def edit(note):
        body = note.split("]\n\n", 1)[-1]
        i = body.find("You have already read")
        return "[Earlier steps were trimmed.]\n\n" + (body[:i] if i > 0 else body)
    return _edit_note(_compacted(w, m, block=True), edit)


ARMS = [
    probe.Arm("baseline(block-on)", _baseline),
    probe.Arm("forbid-rereads", _forbid),
    probe.Arm("no-code-map", _no_map),
    probe.Arm("bodies-inline", _bodies),
    probe.Arm("terse-map-only", _terse),
]


def _synthetic_read_round(w, m):
    """Insert the read as a ROUND, not as prose.

    `bodies-inline` put the same bytes in the note and the model read anyway. The difference here is
    shape: an assistant turn that called `read_file`, and the tool result carrying what it printed.
    If the model reads because its procedure is "read before you edit", a transcript in which the
    read has already happened satisfies that procedure; if it reads because it distrusts anything it
    did not fetch itself, this fails too, and the read is not reachable from the transcript at all.

    The round is well-formed on purpose: an assistant message with `tool_calls` and a `tool` message
    carrying the matching id. A tool message whose call is missing is an orphan, and a chat template
    is entitled to refuse the turn.
    """
    from maestro.codegen.staging import game_dir

    msgs = _compacted(w, m, block=True)
    root = game_dir(w.run_dir)
    seen = sorted(probe.files_already_read(w.run_dir))
    budget, program, printed = 60_000, [], []
    for rel in seen:
        p = root / rel
        if not p.is_file():
            continue
        body = p.read_text(errors="replace")
        if len(body) > budget:
            continue
        budget -= len(body)
        program.append(f'{_var(rel)} = read_file("{rel}")\nprint("--- {rel} ---")\nprint({_var(rel)})')
        printed.append(f"--- {rel} ---\n{body}")
    if not program:
        raise ValueError("no files to pre-read at this position")
    call_id = "call_replay_preread"
    return msgs + [
        {"role": "assistant", "content": "",
         "tool_calls": [{"id": call_id, "type": "function",
                         "function": {"name": "python",
                                      "arguments": json.dumps({"code": "\n".join(program)})}}]},
        {"role": "tool", "tool_call_id": call_id,
         "content": "\n".join(printed) + f"\n\nran 1 tool: read_file x{len(program)}"},
    ]


def _var(rel: str) -> str:
    return "f_" + re.sub(r"\W", "_", rel)


ARMS_PREREAD = [
    probe.Arm("baseline(block-on)", _baseline),
    probe.Arm("bodies-in-note", _bodies),
    probe.Arm("synthetic-read-round", _synthetic_read_round),
]
