"""One position, one change, k samples — a rate instead of an anecdote.

`replay.run_to_position` rebuilds the world a build stood in. This asks the model what it would do
NEXT from there, with and without one change, and counts what came back.

Sampling is temp=0.7: the same position answered twice is two different turns, so a single sample
says nothing and k samples say a rate. The unit of measurement is therefore (positions × k), and
the arm is a function over the position rather than a branch of the harness.

Nothing here executes what the model replies with. The questions this answers — did it read a file
it had already read, did it call the tool we added, did it write its own AudioContext — are all
answerable from the program's SOURCE, and a probe that runs the program would need a sandbox per
sample and would change the world it is measuring.
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional

from . import replay

READ = re.compile(r"read_file\(\s*['\"]([^'\"]+)")


@dataclass
class Sample:
    position: int
    arm: str
    reads: List[str]
    repeat_reads: List[str]          # of files this build had already been shown
    tools_called: List[str]
    program: str
    error: Optional[str] = None
    generated: int = 0          # completion tokens: what the turn COST before it did anything
    called_tool: bool = False   # a turn that thought and emitted nothing is the failure to catch


@dataclass
class Arm:
    """One thing to change about a position. `apply` gets the replayed world and the messages that
    position would have sent, and returns the messages to send instead.

    `reasoning` overrides the effort for this arm alone — the knob is not in the transcript, so an
    arm that changes it cannot be expressed as a message.
    """
    name: str
    apply: Callable[[replay.Replay, List[Dict]], List[Dict]]
    reasoning: Optional[str] = None
    max_tokens: Optional[int] = None   # a ceiling the transcript cannot express


def compaction_positions(run_dir) -> List[int]:
    """The turns a build compacted at — the positions where a compaction arm has anything to say."""
    return [r["turn"] for r in replay._records(Path(run_dir)) if r["kind"] == "compact"]


def files_already_read(run_dir: Path) -> set:
    """What the build had been shown by this point, as the replay itself recorded it: `read_file`
    goes through the real tool, so the read history is rebuilt rather than assumed."""
    try:
        return set(json.loads((run_dir / "reads.json").read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return set()


def _ask(messages: List[Dict], schemas: List[Dict], system: str, k: int,
         reasoning: Optional[str] = None, max_tokens: Optional[int] = None) -> List[Dict]:
    from llm_clients.connector import get_connector
    from maestro.codegen.build_steps import MessageBuilder

    conn = get_connector()
    ctx = conn.get_context_length() or 131072
    prompt_estimate = (len(system) + sum(len(json.dumps(m)) for m in messages)) // 3
    out = []
    for _ in range(k):
        msgs = MessageBuilder(system).extend(messages).build()
        kwargs = {"max_tokens": max_tokens or max(4000, ctx - prompt_estimate - 2000)}
        if reasoning is not None:
            kwargs["reasoning"] = reasoning
        out.append(conn.generate_with_tools(msgs, schemas, **kwargs))
    return out


def _message_of(result: Dict) -> Dict:
    """The reply, whichever shape came back: the connector hands through the raw response, so the
    tool calls are under choices[0].message, not at the top level."""
    choices = (result or {}).get("choices") or []
    if choices:
        return choices[0].get("message") or {}
    return result or {}


def _calls_of(result: Dict) -> List[Dict]:
    return _message_of(result).get("tool_calls") or []


def _program_of(result: Dict) -> str:
    """The turn's program, or the JSON calls rendered as one.

    Two harnesses are in the corpus: one `python` program per turn, and before it seven JSON tools
    with no program at all. Reading only `code` scores every pre-program turn as "no tool call",
    which is indistinguishable from a turn that thought and emitted nothing.
    """
    out = []
    for tc in _calls_of(result):
        fn = tc.get("function") or {}
        try:
            args = json.loads(fn.get("arguments") or "{}")
        except (ValueError, TypeError):
            args = {}
        if args.get("code"):
            out.append(args["code"])
        elif fn.get("name"):
            inner = ", ".join(f'"{v}"' for k, v in args.items() if k in ("path", "id", "description"))
            out.append(f'{fn["name"]}({inner})')
    return "\n".join(out)


def _tools_of(program: str) -> List[str]:
    return sorted({m for m in re.findall(
        r"\b(list_files|read_file|write_file|edit_file|generate_media|compose_world|check_syntax|done)\s*\(",
        program)})


def probe(source_run, position: int, arms: List[Arm], k: int = 3,
          workdir: Optional[Path] = None, before_compaction: bool = False) -> List[Sample]:
    """Replay to `position` once, then ask each arm's version of it k times.

    The world is built ONCE and shared: the arms differ in what they SAY, not in what is on disk,
    and rebuilding it per arm would spend minutes re-executing programs to reach the same files.
    """
    base = Path(workdir or tempfile.mkdtemp(prefix="probe-"))
    target = base / f"pos{position}"
    if target.exists():
        shutil.rmtree(target)
    world = replay.run_to_position(source_run, position, target,
                                   before_compaction=before_compaction)
    if world.gaps:
        raise ValueError(f"position {position} sits after compactions whose note was never "
                         f"archived (turns {world.gaps}); this transcript cannot be rebuilt")
    seen = files_already_read(world.run_dir)

    samples: List[Sample] = []
    for arm in arms:
        messages = arm.apply(world, [dict(m) for m in world.messages])
        for result in _ask(messages, world.tools, world.system, k, arm.reasoning, arm.max_tokens):
            gen = ((result or {}).get("usage") or {}).get("completion_tokens") or 0
            if result.get("error"):
                samples.append(Sample(position, arm.name, [], [], [], "", error=result["error"],
                                      generated=gen))
                continue
            program = _program_of(result)
            if not _calls_of(result):
                # A turn that called no tool is a real outcome, not a zero — counting it as "read
                # nothing" is how an arm that broke the reply looks like an arm that stopped reads.
                samples.append(Sample(position, arm.name, [], [], [], "", error="no tool call",
                                      generated=gen, called_tool=False))
                continue
            reads = READ.findall(program)
            samples.append(Sample(
                position=position, arm=arm.name, reads=reads,
                repeat_reads=[r for r in reads if r in seen],
                tools_called=_tools_of(program), program=program,
                generated=gen, called_tool=True))
    return samples


def report(samples: List[Sample]) -> str:
    by_arm: Dict[str, List[Sample]] = {}
    for s in samples:
        by_arm.setdefault(s.arm, []).append(s)
    lines = []
    for arm, rows in by_arm.items():
        ok = [r for r in rows if not r.error]
        reads = sum(len(r.reads) for r in ok)
        repeats = sum(len(r.repeat_reads) for r in ok)
        turns_reading = sum(1 for r in ok if r.reads)
        turns_repeating = sum(1 for r in ok if r.repeat_reads)
        gens = sorted(r.generated for r in rows if r.generated)
        med = gens[len(gens)//2] if gens else 0
        nocall = sum(1 for r in rows if r.error == "no tool call")
        lines.append(
            f"{arm:26} samples={len(ok):3} errors={len(rows) - len(ok):2}  "
            f"median_generated={med:6}  no_tool_call={nocall}/{len(rows)}  "
            f"reads={reads:3}(already {repeats:3})  RE-read={turns_repeating}/{len(ok)}")
    return "\n".join(lines)
