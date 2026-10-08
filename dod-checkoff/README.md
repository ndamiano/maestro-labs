# dod-checkoff

Status: done
Control: labs/design-map overnight battery (5 asks, 2026-09-15) — same src minus the two changes below.

## Purpose

Two of the five design-map battery builds hit the 200-turn cap after a green suite: the rhythm
platformer spent turns 145–198 and the space salvage build turns 160–200 walking the design's
Definition of Done one row per turn, a ranged read each, rows re-verified after every compaction.
The cap is the only waste line on prod (docs/experiments.md, cost per game: ~$1.4 each, 2 of 6).
The fifth build died at turn 96: prompt 114K, output cap 17K, 26–37K tokens of thinking a turn,
four cut-offs in a row with no compaction between them.

## Hypothesis

Two changes, one run.

1. `check_off(rows)` tool: ticks `- [ ]` rows in `design/design.md` on disk, returns what is still
   unchecked. Bookkeeping only. The record of what is finished lives on disk, so it survives
   compaction (the map shows the DoD range) and the terminal sweep has a list of N instead of an
   open question. Takes a list so one call covers a tier. No done nudge: `done` is unchanged.
   Expected to move: turns from first green suite to done (control: 40–55 on the two cap-outs,
   cap never reached on the two that finished). Idea failure: the builder ticks rows it never
   built, or ignores the tool and sweeps anyway.
2. A turn cut off by the output limit compacts before it is re-sent when the transcript is past
   the keep fraction. Expected to move: no build dies on 4× cut-off. Only observable if a cut-off
   happens in the run.

## Setup

Uncommitted src on branch design-team: tools.py `check_off`, pyexec/child.py binding,
build_steps.py schema line + `_infer` compaction on `full_window`, build.txt one tool line and one
rule line (the old "ensure you've checked every box" rule now says `check_off` every box).
Ask in asks.txt, one fresh genre. Local prod path: control plane, `local_gpu.py auto`, quasar
ninfer :8090, k=1.

    cd labs/dod-checkoff && bash ./run.sh

## Log

2026-09-15 12:33–13:26, run `194354ba2b2e` (stealth museum heist), k=1, local 27B via the whole
prod path. Design 12 min. Build called done at turn 129, 5 compactions, error gate clean, play gate
found one dead input (E to steal) → fix 11 turns → gate found a second (S to move) → fix 56 turns →
gate clean. 200 turns total, playable at :8765/194354ba2b2e.

  turns 97–124   DoD sweep: read the DoD range (1445–1575), then one `play` per row, ~25 rows probed
  turn 125       `read_file(design.md)` whole, `replace("- [ ]", "- [x]")`, `write_file` — 65 boxes
                 ticked in one write, bypassing the tool
  turns 127–128  `check_off` on the already-ticked rows, twice (first with the box glyph in the text,
                 0 matched; then clean, 65 "ticked"), 0 unchecked
  turn 129       check_syntax + done

  check_off calls: 3, all after the bulk write. Green suite (turn ~110) → done: 19 turns.
  Control cap-outs: 40–55 turns from green and never done. Control finishers: 10–20.

Cut-off compaction: turn 20 hit the 30K cap, re-sent at turn 21 under a 40K prompt (below the
33% keep line, so no compaction) with the full window, wrote 64K tokens and landed. Max prompt
115K; no build death. The compaction branch of the change did not fire in this run.

Read: the tool did not carry the bookkeeping; write_file did. The builder still ran the terminal
sweep, then marked every row true in one edit, including rows the sweep never probed (audio,
options, a few level-2 rows). Verdict: implementation fix and rerun — the design must not be
writable by write_file/edit_file, so the only way to tick a row is check_off, one row at a time.

2026-09-15 Nick's ruling after playing: heist a good first pass. Read-only design not wanted
unless a build edits the design beyond the DoD (checked: this one did not — the builder's design
differs from the staged one only in checkboxes). No done nudge. Merge.

## Outcome

Merged with the design-map changes. docs/experiments.md 2026-09-15 entry.
