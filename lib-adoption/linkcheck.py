"""Prototype: does every local reference a game file makes resolve to a file on disk?

A dead `./lib/audio.js` from js/main.js is a module that never loads and a game that never
starts, and nothing in the pipeline sees it: node parses the file fine and the error gate's
chromium reports a 404 on the console, not an uncaught exception.
"""
import re
from pathlib import Path

REF = re.compile(r"""(?:from|import)\s*\(?\s*['"]([^'"\s]+)['"]|(?:src|href)\s*=\s*["']([^"'\s]+)["']""")
SKIP = ("http://", "https://", "data:", "blob:", "//", "#", "mailto:")


def dead_refs(path: Path, game_dir: Path, pending=()):
    text = path.read_text(encoding="utf-8", errors="replace")
    out = []
    for a, b in REF.findall(text):
        ref = (a or b).split("?")[0].split("#")[0]
        if not ref or ref.startswith(SKIP) or "${" in ref or "\\" in ref \
                or "." not in Path(ref).name:
            continue
        target = (path.parent / ref).resolve()
        try:
            rel = target.relative_to(game_dir.resolve())
        except ValueError:
            out.append(ref)
            continue
        if not target.exists() and str(rel) not in pending:
            out.append(ref)
    return out
