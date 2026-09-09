# replay — put a finished run back on the table at any turn

`run_to_position(source_run, position, target_dir)` materialises `target_dir` as the run dir a
build really had before turn `position`: the game folder byte for byte, the transcript as that
turn's request carried it. From there you change ONE thing — a prompt line, a tool, an injected
message, what compaction did — and infer the next turn to see what the change bought.

    PYTHONPATH=~/Documents/ai-agent-test/src python replay_probe.py <run_dir> <target_dir> <position>

## Why it re-executes rather than parses

A body a program ASSEMBLED — a loop over a roster, an f-string, a generated level table — has no
literal in its source. Only running the program produces the real bytes, so each recorded program
runs again through the same confined runner and the same `build_tools` the build used, with no
model in the loop.

That is also what makes it checkable: a turn's printed result was recorded, so a replayed turn that
prints something else has diverged, and `Replay.fidelity` says so. A replay whose programs never
ran reports fidelity `None` — unknown — never 1.0.

## The two GPU tools are answered from the source run

`generate_media` and `compose_world` cost real money to replay and need not. A stand-in is written
when the art is asked for, and the real render lands on the turn the recording proves it landed —
read out of the byte sizes in each recorded `list_files`. Handing the model finished art at a turn
the build only had a placeholder for is a different world.

## Measured

Tonight's rhythm game (`7f7fef4772fa`, 25 turns): fidelity 95%, zero errors, one divergence — the
manifest's own size (4,938 vs 5,127 bytes), which mutates as renders land and is not reproducible
byte-exactly.

## probe.py — one position, one change, k samples

`probe(run, position, arms, k)` replays the world once and asks each arm's version of that position
k times. An `Arm` is a function over `(world, messages)`, plus the two knobs a transcript cannot
express: `reasoning` and `max_tokens`. Sampling is `temp=0.7`, so one sample is an anecdote and
(positions × k) is a rate.

`accounting.py <era>` is the other half: where a corpus's generated tokens went, bucketed by what
each turn's program called. It takes `program` or `json-tools` — pooling the two describes a
harness that does not exist.

## What it has measured

- **The file-state block does nothing.** 18 samples an arm over six real compaction points: 8/18
  turns re-read with the block, 9/17 without. Nor did four other attacks on the same turn — a rule
  instead of a fact, no code map at all, the file bodies pasted into the note, and the bodies
  delivered as a completed `read_file` round. The last is the informative one: handing the model
  the exact bytes it would have read does not stop it reading them.
- **Turns that overrun are an inference failure, not a transcript one.** The six positions where
  one build ran the window dry fail 2 times in 36 when replayed, and the 105,867-token worst case
  resamples to a median of 1,838. The cut-off nudge is what carries it forward: 14,160 tokens with
  that exchange in context against 1,934 without. Shipped as maestro f430496.
- **Where the tokens are is not where they look.** On the 27B locally: writing 34%, reading 31%,
  turns that emitted nothing 17%. On prod Flash-Next: reading 52%, writing 34%, nothing-emitted
  2.5% — and 77% of prod's reads are of files already read. Fix builds are what read: they start
  with an empty transcript and have to read the game back.

## Not built yet

- k-turn branching, for questions a single turn cannot answer. A replay is faithful to the turn it
  starts from; after one turn the trajectory is its own.
- Anything measured against Flash-Next. Every arm here ran on the local 27B, and prod's read rate
  is worse than the one the null results were measured against.
