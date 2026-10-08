"""Replay f91ade83c0d0 to turn 105 with the design's headings in the compaction note, then let the
builder take the turns it wrote its test suite in."""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: F401  puts src on sys.path
from lib import paths
from lib.replay import branch, direct, replay

SOURCE = paths.RUNS / "f91ade83c0d0"
BUILD = "bfbf7a7b2421"
POSITION = 105
DESIGN_TESTS = re.compile(r"`([a-z]+: [^`]+)`")


def patch_note(messages, game_dir):
    """The archived note predates the change: splice the markdown block the map renders now in
    at the place render() would have put it."""
    from maestro.codegen import code_map
    block = code_map.render(game_dir).splitlines()
    md = [l for l in block[:next(i for i, l in enumerate(block) if l.startswith("index.html"))]]
    n = 0
    for m in messages:
        c = m.get("content")
        if m.get("role") == "user" and isinstance(c, str) and "Earlier steps were trimmed" in c \
                and "\nindex.html (" in c and "design/design.md (" not in c:
            m["content"] = c.replace("\nindex.html (", "\n" + "\n".join(md) + "\nindex.html (", 1)
            n += 1
    return n


def seed_staged(game_dir):
    """design/ and docs/ are staged into the game dir by the chain, not written by any program,
    so the replay never lands them; the build read them all along."""
    import shutil
    for sub in ("design", "docs"):
        src = SOURCE / "game" / sub
        if src.is_dir() and not (game_dir / sub).exists():
            shutil.copytree(src, game_dir / sub)


def main(turns):
    from maestro.codegen import build_state, build_steps
    direct.install()
    target = paths.OUTPUT / "branch-work" / f"design-map-pos{POSITION}-{int(time.time())}"
    world = replay.run_to_position(SOURCE, POSITION, target, build=BUILD)
    print(f"replayed to {POSITION}: fidelity {world.fidelity}, gaps {world.gaps}, "
          f"{len(world.diverged)} diverged, {len(world.errors)} errors", flush=True)
    game_dir = target / "game"
    seed_staged(game_dir)
    patched = patch_note(world.messages, game_dir)
    print(f"patched {patched} compaction note(s)", flush=True)
    assert "2784-2821  9. TESTS" in "".join(m.get("content") or "" for m in world.messages
                                            if isinstance(m.get("content"), str))
    assert patched == 1, "expected exactly the turn-80 note in the transcript"

    spec = json.loads((SOURCE / "spec.json").read_text())
    tools = replay._tools_for(target, "branch", SOURCE)
    cursor = build_state.BuildCursor(build_id="branch", started=True, turn=POSITION,
                                     system=world.system,
                                     history=[dict(m) for m in world.messages],
                                     logged=len(world.messages))
    out = branch.Branch(arm="design-map", position=POSITION)
    outcome = build_steps.step(spec, target, tools, cursor, None)
    for _ in range(turns):
        if isinstance(outcome, build_steps.Done):
            out.stopped = outcome.report
            break
        t0 = time.time()
        result = branch._infer_once(outcome, world.system, None)
        before = cursor.turn
        outcome = build_steps.step(spec, target, tools, cursor, result)
        program = branch._program_of(cursor, before)
        usage = (result or {}).get("usage") or {}
        rec = branch.TurnRecord(turn=cursor.turn, reads=branch.READ.findall(program), repeat_reads=[],
                                tools_called=branch._tools_of(program),
                                generated=usage.get("completion_tokens") or 0,
                                prompt_tokens=usage.get("prompt_tokens") or 0,
                                compacted=cursor.compacted, seconds=time.time() - t0,
                                error=result.get("error") or (None if program else "no tool call"))
        out.turns.append(rec)
        design_reads = re.findall(r"read_file\(\s*['\"]design/design\.md['\"][^)]*\)", program)
        print(f"  turn {rec.turn:3} gen={rec.generated:6} prompt={rec.prompt_tokens:6} "
              f"{rec.seconds:5.1f}s {','.join(rec.tools_called)} design reads: {design_reads}"
              + (f"  ERROR {rec.error}" if rec.error else ""), flush=True)
        (target / "programs.log").open("a").write(f"\n##### turn {rec.turn}\n{program}\n")
    print(out.report())
    (target / "history.json").write_text(json.dumps(cursor.history, indent=1))
    score(game_dir)


def score(game_dir):
    names = set(DESIGN_TESTS.findall((game_dir / "design/design.md").read_text()))
    written = []
    for p in sorted(game_dir.glob("tests/*.js")):
        src = p.read_text()
        written += re.findall(r"""name:\s*['"]([^'"]+)['"]""", src)
        written += re.findall(r"""^\s*['"]([^'"]{6,})['"]\s*:\s*(?:async\s*)?(?:\(|function)""", src, re.M)
    hits = [w for w in written if w in names]
    print(f"tests written: {len(written)}, of the design's {len(names)} names: {len(hits)}")
    for h in hits:
        print("  ", h)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 8)
