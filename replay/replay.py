"""Put a finished run back on the table at any turn it ever stood at.

`run_to_position(source_run, position, target_dir)` materialises `target_dir` as the run dir the
build really had before turn `position`: the game folder byte for byte, the read history, the
transcript as that turn sent it. From there a caller may change ONE thing — a prompt line, a tool,
an injected message, what compaction did — and infer the next turn to see what the change bought.

The disk cannot be reconstructed by reading the programs. A body a program ASSEMBLED — a loop over
a roster, an f-string, a generated level table — has no literal in its source, so the only thing
that produces the real bytes is running the program again. So this re-EXECUTES each recorded
program in order, through the same confined runner and the same `build_tools` the build used, with
no model in the loop. That is also what makes it checkable: a turn's printed result was recorded,
so a replayed turn that prints something else is a replay that has diverged, and `Replay.fidelity`
says so rather than handing back a plausible wrong world.

Two tools would otherwise cost real money and real GPU seconds to replay, and neither needs to:
`generate_media` and `compose_world` are answered from the SOURCE run's own art. The build asked
for a picture and got one; the replay copies that same file to the same path.

Nothing here writes to the source run. `target_dir` must not exist.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from maestro.codegen import staging, turn_log
from maestro.codegen.pyexec import runner


@dataclass
class Turn:
    """One replayed turn: what it printed then, what it printed now.

    `evidence` is whether this turn can speak to fidelity at all. A turn that printed nothing, or
    whose program never ran, agrees with every recording ever made — counting it as a match is how
    a replay that executed NOTHING reports itself faithful.
    """
    turn: int
    programs: int
    recorded: str
    replayed: str
    matched: bool
    evidence: bool
    error: Optional[str] = None


@dataclass
class Replay:
    run_dir: Path
    position: int
    messages: List[Dict]                    # the transcript as that turn's request carried it
    system: str
    tools: List[Dict]
    turns: List[Turn] = field(default_factory=list)
    # Compactions whose note was never archived (the log format predates it). The transcript the
    # build really sent cannot be rebuilt at or after these, so a probe must not pretend otherwise.
    gaps: List[int] = field(default_factory=list)

    @property
    def fidelity(self) -> Optional[float]:
        """Share of the turns that COULD disagree which did not. None when none of them could —
        an unknown fidelity, never a perfect one."""
        speaking = [t for t in self.turns if t.evidence]
        return None if not speaking else sum(t.matched for t in speaking) / len(speaking)

    @property
    def diverged(self) -> List[Turn]:
        return [t for t in self.turns if t.evidence and not t.matched]

    @property
    def errors(self) -> List[Turn]:
        """Turns whose programs did not run — a broken replay, not a divergent one."""
        return [t for t in self.turns if t.error]


def _seed_vendor_as_it_was(source_run: Path, target: Path) -> None:
    """Seed the vendored files the SOURCE run had, not the ones in the repo today.

    `list_files` reports byte counts, so a lib that has grown since the build turns every listing
    into a divergence and a re-run into a different world. The build's own copies are in its game
    folder, which is the only record of the versions it actually read.
    """
    src_game, dst_game = staging.game_dir(source_run), staging.game_dir(target)
    dst_game.mkdir(parents=True, exist_ok=True)
    if not src_game.exists():
        staging.seed_vendor(target)
        return
    for src in sorted(src_game.glob("*.js")):
        if staging.is_vendored(src, src_game):
            shutil.copy2(src, dst_game / src.name)
    if (src_game / "lib").is_dir():
        (dst_game / "lib").mkdir(exist_ok=True)
        for src in sorted((src_game / "lib").glob("*.js")):
            shutil.copy2(src, dst_game / "lib" / src.name)


def _records(source_run: Path) -> List[Dict]:
    return [json.loads(line) for line in (Path(source_run) / turn_log.FILE).open(encoding="utf-8")]


def _programs(record: Dict) -> List[str]:
    out = []
    for tc in ((record.get("response") or {}).get("tool_calls") or []):
        try:
            code = json.loads(tc["function"]["arguments"]).get("code")
        except (ValueError, KeyError, TypeError):
            continue
        if isinstance(code, str) and code.strip():
            out.append(code)
    return out


def _recorded_output(record: Dict) -> str:
    """What the build was shown for this turn: the `tool` messages the NEXT turn carried."""
    return "\n".join(str(m.get("content", "")) for m in (record.get("added") or [])
                     if m.get("role") == "tool")


def _landing_schedule(records: List[Dict], src_game: Path) -> Dict[str, int]:
    """The turn each asset's real render appeared, read out of what the build was shown.

    Renders land while the build keeps writing, so a turn mid-build sees a stand-in where a later
    turn sees the picture. Nothing logs the landing, but every `list_files` the model ran was
    recorded with each file's size at that moment, and an asset AT ITS FINAL SIZE has landed. Assets
    the model never listed are left to land when they were asked for — the best guess available,
    and a generous one.
    """
    final = {str(p.relative_to(src_game)): p.stat().st_size
             for p in src_game.rglob("*") if p.is_file() and "assets/" in str(p.relative_to(src_game))}
    landed: Dict[str, int] = {}
    for r in records:
        if r["kind"] != "turn":
            continue
        shown = _recorded_output(r)
        for rel, size in final.items():
            if rel in landed:
                continue
            if f"'path': '{rel}', 'bytes': {size}" in shown or f'"path": "{rel}", "bytes": {size}' in shown:
                landed[rel] = r["turn"]
    return landed


def _replay_media(source_run: Path, target: Path):
    """`generate_media` answered out of the source run's art.

    The path a render lands at is the build's own choice of id, so the same id in the same run
    resolves to the same file — copying it is enough, and the model sees the answer it really got.
    A render the source run never landed is answered as pending, exactly as the build saw it.
    """
    from maestro.codegen.assets import read_manifest
    from maestro.codegen.staging import game_dir

    src_game, dst_game = game_dir(source_run), game_dir(target)

    def generate_media(id=None, **kwargs) -> dict:
        # The answer has to be the one the build was really given — a replay whose tool replies in
        # a different dialect measures a different harness.
        entry = next((e for e in read_manifest(source_run) if e.get("id") == id), None)
        if entry is None:
            return {"ok": False, "error": "no compute left for art — draw this one with code instead"}
        rel = entry.get("file")
        if rel:
            dst = dst_game / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists():
                # A stand-in now, the real render when the recording says it landed. Handing the
                # model finished art at a turn the build only had a placeholder for is a different
                # world, and `list_files` reports the size, so the model can see the difference.
                from maestro.codegen.assets import write_placeholder
                kind = entry.get("kind") or "sprite"
                try:
                    write_placeholder(dst, kind, id, (entry.get("details") or {}).get("anims"))
                except Exception:                       # a kind with no stand-in shape
                    dst.write_bytes(b"")
        _record_in_manifest(entry)
        out = {"ok": True, "path": rel, "status": "rendering"}
        if (entry.get("kind") or "sprite") != "mesh":
            out["note"] = ("a stand-in image is at that path now; the render replaces it when it "
                           "lands.")
        return out

    def _record_in_manifest(entry: Dict) -> None:
        """The manifest is a file IN the game folder, so `list_files` reports it and a replay
        without one lists a project the build never had."""
        p = dst_game / "assets.json"
        try:
            images = json.loads(p.read_text(encoding="utf-8")).get("images", [])
        except (OSError, ValueError):
            images = []
        if any(e.get("id") == entry.get("id") for e in images):
            return
        images.append(entry)
        p.write_text(json.dumps({"images": images}, ensure_ascii=False, indent=2), encoding="utf-8")

    def compose_world(description=None, seed=None, **_) -> dict:
        src_world, dst_world = src_game / "world", dst_game / "world"
        if not src_world.exists():
            return {"ok": False, "error": "this run built no world"}
        if not dst_world.exists():
            shutil.copytree(src_world, dst_world)
        for name in ("world.js",):
            if (src_game / name).exists() and not (dst_game / name).exists():
                shutil.copy2(src_game / name, dst_game / name)
        try:
            return {"ok": True, **json.loads((dst_world / "world.json").read_text())}
        except (OSError, ValueError):
            return {"ok": True}

    return generate_media, compose_world


def _tools_for(target: Path, build_id: str, source_run: Path) -> Dict:
    """The build's own tools, bound to the replay dir, with the two GPU tools answered from the
    source run. Everything else — the path jail, the ERROR: strings, the ledger — is unchanged,
    because a replay that reasons about a different tool surface measures a different harness."""
    from maestro.codegen.tools import build_tools
    from maestro.state import RunState

    # Not RunState(...): its constructor makes runs/<id> under the real base path, and a replay
    # that leaves a directory in the archive has already touched what it came to read.
    state = object.__new__(RunState)
    state.run_id, state.run_dir = target.name, target
    tools = build_tools(state, build_id)
    media, world = _replay_media(source_run, target)
    tools["generate_media"] = media
    tools["compose_world"] = world
    return tools


def run_to_position(source_run, position: int, target_dir, *,
                    before_compaction: bool = False) -> Replay:
    """Materialise `target_dir` as `source_run` stood before turn `position`.

    `position` is a turn number from the source log; every turn BEFORE it is replayed, and the
    returned messages are what that turn's request carried. A position past the end replays the
    whole build.

    `before_compaction` stops short of applying the compaction recorded AT `position`, handing back
    the transcript that compaction was about to act on. That is the only useful position for an arm
    that changes what compaction does: compacting an already-compacted transcript finds nothing to
    trim, writes no new note, and leaves every arm carrying the note the build really used.
    """
    source_run, target = Path(source_run), Path(target_dir)
    if target.exists():
        raise FileExistsError(f"{target} exists; a replay needs a fresh directory")
    target.mkdir(parents=True)
    for name in ("spec.json", "build_state.json"):
        if (source_run / name).exists():
            shutil.copy2(source_run / name, target / name)
    _seed_vendor_as_it_was(source_run, target)

    records = _records(source_run)
    meta = next((r for r in records if r["kind"] == "meta"), {})
    build_id = meta.get("build_id", "replay")
    tools = _tools_for(target, build_id, source_run)
    src_game, dst_game = staging.game_dir(source_run), staging.game_dir(target)
    schedule = _landing_schedule(records, src_game) if src_game.exists() else {}

    out = Replay(run_dir=target, position=position, messages=[], system=meta.get("system", ""),
                 tools=meta.get("tools", []))

    for record in records:
        if record["kind"] == "meta":
            # A fix restarts the transcript in the same run dir; its disk is what the build left.
            out.system, out.tools, build_id = (record.get("system", ""), record.get("tools", []),
                                               record.get("build_id", build_id))
            out.messages = []
            continue
        if record["kind"] == "compact":
            if before_compaction and record["turn"] >= position:
                break
            if record.get("note") is None:
                out.gaps.append(record["turn"])
            out.messages = [m for m in turn_log._compacted(out.messages, record)
                            if m.get("content") is not None or m.get("tool_calls")]
            continue
        if record["kind"] != "turn":
            continue
        out.messages = out.messages + (record.get("added") or [])
        if record["turn"] >= position:
            break
        for rel, when in schedule.items():
            if when <= record["turn"] and (src_game / rel).exists():
                (dst_game / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_game / rel, dst_game / rel)
        printed, trouble = [], []
        programs = _programs(record)
        for code in programs:
            outcome = runner.run(code, tools)
            printed.append(outcome.stdout or "")
            if outcome.refused:
                trouble.append(f"refused: {outcome.refused}")
            elif outcome.timed_out:
                trouble.append("timed out")
            elif not outcome.stdout and not outcome.ledger:
                # No output AND no tool call: the child never got far enough to do either.
                trouble.append("the program produced neither output nor a tool call")
        replayed = "\n".join(printed)
        following = _next_turn(records, record["turn"])
        recorded = _recorded_output(following)
        out.turns.append(Turn(
            turn=record["turn"], programs=len(programs), recorded=recorded, replayed=replayed,
            matched=_agrees(recorded, replayed),
            # The LAST turn's result was never carried by a following turn, so nothing recorded
            # what it printed: no evidence either way, rather than a divergence.
            evidence=bool(replayed.strip()) and bool(following) and not trouble,
            error="; ".join(trouble) or None))
    return out


def _next_turn(records: List[Dict], turn: int) -> Dict:
    for r in records:
        if r["kind"] == "turn" and r["turn"] == turn + 1:
            return r
    return {}


def _agrees(recorded: str, replayed: str) -> bool:
    """Did the replayed program print what the recording says it printed?

    The recorded tool message wraps the program's output in the turn's ledger and any repeat note,
    so the test is containment of the program's own lines, not equality. An empty program that
    printed nothing agrees with anything — it carries no evidence either way.
    """
    lines = [ln.strip() for ln in replayed.splitlines() if ln.strip()]
    if not lines:
        return True
    return all(ln in recorded for ln in lines)
