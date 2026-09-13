"""What a fix build opens on: the note as recorded, the note plus the code map, the note plus the
exception the play gate's page threw, or both.

The arm rewrites the ONE user message before the first inference — `_infer` is patched the way
arms_readstreak does it, because `branch.run` builds the cursor itself. Ground truth for a736b5 is
a grep: gen.js line 166 calls `surfaceAt(solidGround, floats, cx)`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict

PROMPTS = Path("/home/nick/Documents/ai-agent-test/src/maestro/codegen/prompts")

# Filled from play_fix_note.txt once the gate carries the error; the a736b5 page threw this.
THREW = "TypeError: floats is not iterable at js/gen.js:166"


def with_map(note: str, game_dir: Path) -> str:
    from maestro.codegen import code_map
    body = code_map.render(game_dir)
    if not body:
        return note
    return note + "\n\n" + (PROMPTS / "code_map_note.txt").read_text(
        encoding="utf-8").strip().format(map=body)


def with_threw(note: str, threw: str, line_template: str) -> str:
    """Insert the gate's thrown-error line after the 'What the screen showed instead' line."""
    lines = note.split("\n")
    for i, l in enumerate(lines):
        if l.startswith("What the screen showed instead:"):
            lines.insert(i + 1, line_template.format(threw=threw))
            return "\n".join(lines)
    raise ValueError("note has no 'What the screen showed instead' line")


def install(arm: str, game_dir: Path, line_template: str) -> Dict[str, object]:
    from maestro.codegen import build_steps

    was = {"_infer": build_steps._infer, "sent": None}

    def _infer(run_dir, cursor, report=None, *, full_window=False):
        if was["sent"] is None:
            note = cursor.history[0]["content"]
            if "threw" in arm:
                note = with_threw(note, THREW, line_template)
            if "map" in arm:
                note = with_map(note, game_dir)
            cursor.history[0]["content"] = note
            was["sent"] = note
        return was["_infer"](run_dir, cursor, report=report, full_window=full_window)

    build_steps._infer = _infer
    return was


def restore(was: Dict[str, object]) -> None:
    from maestro.codegen import build_steps
    build_steps._infer = was["_infer"]
