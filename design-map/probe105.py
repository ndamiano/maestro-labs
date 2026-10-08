"""Position 105 asked k times per arm: does the first turn go to section 9 when the note maps it?"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: F401
from lib import paths
from lib.replay import direct, probe

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run import BUILD, POSITION, SOURCE, patch_note, seed_staged  # noqa: E402

SECTION9 = re.compile(r"design/design\.md.{0,120}(27[89]\d|28[01]\d|9\. TESTS|TESTS)", re.S)


def with_map(world, messages):
    seed_staged(world.run_dir / "game")
    assert patch_note(messages, world.run_dir / "game") == 1
    return messages


def with_map_unlisted(world, messages):
    """The map, and design.md struck from every note's "already read, reading again returns
    exactly what you were shown" list — the line that tells a model with no design in context
    that it still has it."""
    with_map(world, messages)
    for m in messages:
        c = m.get("content")
        if m.get("role") == "user" and isinstance(c, str) and "Earlier steps were trimmed" in c:
            m["content"] = c.replace("\n  design/design.md\n", "\n", 1)
    return messages


def _notes(messages):
    return [i for i, m in enumerate(messages) if m.get("role") == "user"
            and isinstance(m.get("content"), str) and "Earlier steps were trimmed" in m["content"]]


def with_map_fresh(world, messages):
    """The map, and only the newest note kept — what compact() sends since the stale-note fix."""
    with_map(world, messages)
    for i in reversed(_notes(messages)[1:]):
        del messages[i]
    assert len(_notes(messages)) == 1
    return messages


def with_map_fresh_unlisted(world, messages):
    with_map_fresh(world, messages)
    i = _notes(messages)[0]
    messages[i]["content"] = messages[i]["content"].replace("\n  design/design.md\n", "\n", 1)
    assert "  design/design.md\n" not in messages[i]["content"]
    return messages


ARMS = {"control": lambda w, m: m, "design-map": with_map, "map-unlisted": with_map_unlisted,
        "map-fresh": with_map_fresh, "map-fresh-unlisted": with_map_fresh_unlisted}


def main(k, names):
    direct.install()
    arms = [probe.Arm(n, ARMS[n]) for n in names]
    samples = probe.probe(SOURCE, POSITION, arms, k=k,
                          workdir=paths.OUTPUT / "probe-work" / "design-map")
    print(probe.report(samples))
    for s in samples:
        reads = re.findall(r"read_file\([^)]*\)", s.program)
        sec9 = bool(SECTION9.search(s.program)) or "9. TESTS" in s.program or "# 9" in s.program
        print(f"{s.arm:11} tools={','.join(s.tools_called):30} section9={sec9} reads={reads[:3]}"
              + (f" ERROR {s.error}" if s.error else ""))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5, sys.argv[2:] or list(ARMS))
