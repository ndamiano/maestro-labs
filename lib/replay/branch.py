"""Run a replayed position FORWARD for k turns, with one thing about the harness changed.

`probe.py` asks a position once and never executes the reply, because the questions it answers live
in the program's source. A question about what compaction costs over a BUILD cannot be answered
that way: the second cut lands ten turns after the first, and the transcript that reaches it is the
one the arm's own turns wrote. So this drives `build_steps.step` — the build's real turn machine,
its real trigger, its real tools — with a direct inference where the queue job would be, and
executes every program the model writes.

A branch is one trajectory, not a rate. Two branches of the same arm diverge on the first sample.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from lib import paths
from . import probe, replay

READ = re.compile(r"read_file\(\s*['\"]([^'\"]+)")


@dataclass
class TurnRecord:
    turn: int
    reads: List[str]
    repeat_reads: List[str]
    tools_called: List[str]
    generated: int
    prompt_tokens: int
    compacted: int                    # cuts so far at the END of this turn
    seconds: float
    error: Optional[str] = None


@dataclass
class Branch:
    arm: str
    position: int
    turns: List[TurnRecord] = field(default_factory=list)
    stopped: str = ""

    def report(self) -> str:
        ok = [t for t in self.turns if not t.error]
        reads = sum(len(t.reads) for t in ok)
        repeats = sum(len(t.repeat_reads) for t in ok)
        lines = [f"{self.arm} @ {self.position}: {len(self.turns)} turns, "
                 f"{reads} reads ({repeats} already shown), "
                 f"{sum(1 for t in ok if t.repeat_reads)}/{len(ok)} turns re-read"
                 + (f" — stopped: {self.stopped}" if self.stopped else "")]
        for t in self.turns:
            mark = f"  ERROR {t.error}" if t.error else ""
            lines.append(f"  turn {t.turn:3} reads={len(t.reads):2} (already {len(t.repeat_reads):2}) "
                         f"gen={t.generated:6} prompt={t.prompt_tokens:6} cuts={t.compacted} "
                         f"{t.seconds:5.1f}s {','.join(t.tools_called)}{mark}")
        return "\n".join(lines)


def _infer_once(inf, system: str, reasoning: Optional[str]) -> Dict:
    from llm_clients.connector import get_connector

    kwargs = {"max_tokens": inf.max_tokens}
    if reasoning is not None:
        kwargs["reasoning"] = reasoning
    return get_connector().generate_with_tools(inf.messages, inf.schemas, **kwargs)


def run(source_run, position: int, turns: int, *, install: Optional[Callable] = None,
        restore: Optional[Callable] = None,
        arm: str = "arm", workdir: Optional[Path] = None, build: Optional[str] = None,
        reasoning: Optional[str] = None) -> Branch:
    """Replay to `position`, apply `install()`, then take `turns` real turns from there.

    `install` returns whatever it replaced and `restore` is handed that back before returning, so
    a branch leaves the imported harness as it found it.
    """
    from maestro.codegen import build_state, build_steps

    base = Path(workdir or paths.OUTPUT / "branch-work")
    target = base / f"{arm}-pos{position}"
    if target.exists():
        raise FileExistsError(f"{target} exists; a branch needs a fresh directory")
    world = replay.run_to_position(source_run, position, target, before_compaction=True,
                                   build=build)
    if world.gaps:
        raise ValueError(f"position {position} sits after unarchived compactions {world.gaps}")

    spec = json.loads((Path(source_run) / "spec.json").read_text(encoding="utf-8"))
    tools = replay._tools_for(target, build or "branch", Path(source_run))
    cursor = build_state.BuildCursor(build_id="branch", started=True, turn=position,
                                     system=world.system,
                                     history=[dict(m) for m in world.messages],
                                     logged=len(world.messages))

    out = Branch(arm=arm, position=position)
    was = install() if install else None
    try:
        outcome = build_steps.step(spec, target, tools, cursor, None)
        for _ in range(turns):
            if isinstance(outcome, build_steps.Done):
                out.stopped = outcome.report
                break
            t0 = time.time()
            result = _infer_once(outcome, world.system, reasoning)
            seen = probe.files_already_read(target)
            before = cursor.turn
            outcome = build_steps.step(spec, target, tools, cursor, result)
            program = _program_of(cursor, before)
            reads = READ.findall(program)
            usage = (result or {}).get("usage") or {}
            out.turns.append(TurnRecord(
                turn=cursor.turn, reads=reads,
                repeat_reads=[r for r in reads if r in seen],
                tools_called=_tools_of(program),
                generated=usage.get("completion_tokens") or 0,
                prompt_tokens=usage.get("prompt_tokens") or 0,
                compacted=cursor.compacted, seconds=time.time() - t0,
                error=result.get("error") or (None if program else "no tool call")))
            t = out.turns[-1]
            print(f"  turn {t.turn:3} reads={len(t.reads):2} (already {len(t.repeat_reads):2}) "
                  f"gen={t.generated:6} prompt={t.prompt_tokens:6} cuts={t.compacted} "
                  f"{t.seconds:5.1f}s {','.join(t.tools_called)}"
                  + (f"  ERROR {t.error}" if t.error else ""), flush=True)
    finally:
        if restore is not None:
            restore(was)
    return out


def _program_of(cursor, before_turn: int) -> str:
    """The program the turn just ran, taken from the transcript the step machine wrote.

    Reading it back out of the cursor rather than the raw reply is what keeps this honest about
    what RAN: the machine sends only the first of several calls, and recovers calls the server's
    parser missed.
    """
    for m in reversed(cursor.history):
        if m.get("role") == "assistant" and m.get("tool_calls"):
            fn = (m["tool_calls"][0].get("function") or {})
            try:
                return json.loads(fn.get("arguments") or "{}").get("code") or ""
            except (ValueError, TypeError):
                return ""
    return ""


def _tools_of(program: str) -> List[str]:
    return sorted({m for m in re.findall(
        r"\b(list_files|read_file|write_file|edit_file|generate_media|compose_world|check_syntax|done)\s*\(",
        program)})
