"""The file-state block, on and off, at real compaction points.

The build arm this replaces spent 2-3 hours per cell and turned on whether the ask happened to fill
the window. Here the position IS a compaction that really happened, so the question is always live,
and the answer is a rate over (positions x k) instead of one build's anecdote.

What is measured: of the files the next turn reads, how many had the model already been shown? The
block's whole claim is that saying "reading this again returns what you were shown" stops the read
that the code map alone does not.
"""


from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List

from lib.replay import probe
from lib.replay import replay

MARK = "have already read these files and they have NOT changed"


def _compact_with(world: replay.Replay, messages: List[Dict], block: bool) -> List[Dict]:
    """Compact this position's transcript the way the build would have, with the block on or off.

    The recorded compaction is already applied in `world.messages`, so this re-does it from the
    same inputs rather than compacting a compacted transcript: the note is rebuilt, and the note is
    the only thing the arms differ in.
    """
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
        did = build_steps.compact(world.run_dir, cursor, int(ctx * build_steps._COMPACT_KEEP) * 4)
    finally:
        file_state.render = real
    if not did:
        raise ValueError("nothing was compacted at this position — the arms would be identical")
    note = next((str(m["content"]) for m in cursor.history
                 if m.get("role") == "user" and str(m.get("content", "")).startswith("[Earlier steps")), "")
    # An arm whose change is absent from the prompt measures nothing, and reads exactly like an
    # arm that had no effect. Both directions are asserted rather than assumed.
    present = MARK in note
    if block and not present:
        raise ValueError("block=on but the file-state block is not in the note")
    if not block and present:
        raise ValueError("block=off but the file-state block is in the note anyway")
    return cursor.history


ARMS = [
    probe.Arm("block-on", lambda w, m: _compact_with(w, m, True)),
    probe.Arm("block-off", lambda w, m: _compact_with(w, m, False)),
]
