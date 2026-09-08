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

## Not built yet

- `intervene(position, fn)` — the mutation seam, so an arm is a function over the position.
- k samples per position. Sampling is `temp=0.7`: one sample is an anecdote, n positions × k
  samples is a rate.
- k-turn branching, for questions a single turn cannot answer.
