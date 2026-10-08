# design headers in the code map

Status: done
Control: run `f91ade83c0d0` itself (tests-in-files lab, RPG ask), turns 105–110 of its main build

## Purpose

`f91ade83c0d0` read `design/design.md` in twelve chunks at turns 1–12, lost all of it at the first
compaction (turn 30), and at turn 105 wrote a 47-test suite from the build prompt's one-line
description of the harness. Section 9 of the design names 123 tests; 0 of the 47 match. The
compaction note listed `design/design.md` under "already read, reading again returns exactly what
you were shown", and no read of lines 2784–2821 happened again in 479 turns.

## Hypothesis

`code_map.render` maps markdown files by heading with a line range, so every compaction note
carries `2784-2821  9. TESTS` next to the JS declarations. Measured, over the turns from 105 that
write the suite: whether the builder reads section 9 (a `read_file("design/design.md", offset≈2784)`),
and how many of the test names it writes are the design's. Control is 0 reads, 0 of 47 names.
Idea failure: the heading is in the note and the builder still writes its own suite from the
prompt line.

## Setup

`code_map.py`: `.md` joins `_TEXT`; `_headings()` lists `#`..`######` with each heading's range to
the next heading at its level or above (66 lines, ~700 tokens for this 3068-line design).

`run.py` replays `f91ade83c0d0` to position 105 of build `bfbf7a7b2421` with `lib.replay`, patches
the archived turn-80 compaction note in the transcript with the markdown block the live map now
renders (that note was written before the change; a replay at 105 carries it verbatim), and takes
turns through `build_steps.step` against the local engine. Local 27B quasar, xhigh, as the source
run.

    cd labs && PYTHONPATH=. ../venv/bin/python design-map/run.py [turns]
    cd labs && PYTHONPATH=. ../venv/bin/python design-map/probe105.py 5 [arm ...]

Overnight battery (Nick: "run a few new prompts with new designs"): `overnight.sh` takes the five
asks in `asks.txt` through the whole production path one after another — design chain, build at
the prod 200 cap, error gate, play gate — with the src as it stands: markdown headings in the
map, one compaction note kept, the play gate's 200 ms tap, the three earlier fixes, and NO
tests bullet in the build prompt (reverted), so section 9 of the design is the only place the
tests are named. Run ids land in `builds.tsv`, chain logs in `logs/full.N.log`, heartbeat in
`logs/watch.log`. `tally.py` is the morning read: design reads whole vs ranged, section-9 reads,
test names vs the design's, done/cap, gate verdicts. Control for every column: `f91ade83c0d0`
(41 whole reads, 20 ranged, 0 section 9, 0/122 names, 479 turns).

## Log

2026-09-15 run 1 — implementation failure. `lib.replay` seeds vendor JS and program-written files
only; `design/` and `docs/` are staged by the chain, so the replayed world had no
`design/design.md`: the map block was empty and all three `read_file("design/design.md")` calls
in turns 106–109 returned "no such file". The 8 turns wrote 3 test files blind. Discarded.
Driver now copies both dirs from the source after the replay (reads during the replay itself still
miss them — fidelity 0.78, all read-only divergence). Worth moving into `lib.replay` on next need.

2026-09-15 run 2 — branch at 105, 8 turns, note carried `2784-2821  9. TESTS` (asserted).
Turn 106 booted the page in play(), 107–113 wrote `tests/run.js` + 7 suites (config, rng, save,
state, combat, world, game; 54 tests as object keys). Design reads: 0. Design test names used: 0
of 122. Same shape as the source run's own 47. One sample; `probe105.py` k=5 per arm next for a
rate on the first turn's reads.

2026-09-15 probe 1 — position 105, k=5, temp 0.7. Note verified by eye in `history.json`: the
markdown block (66 lines, 2.5K chars) sits at the top of the turn-80 note, `2784-2821  9. TESTS`
included; the note's footer still lists `design/design.md` under "already read … returns exactly
what you were shown". First-turn reads of design.md: control 1/5 (offset 1, 80 lines — blind);
design-map 3/5, all three at offset 2843–2845 = `11. DEFINITION OF DONE › Tier 1`, taken straight
off the map's line numbers. 0/10 went to section 9. Read: the map works as a locator and the
system prompt's "check every box in definition of done" decides where it points. Next: same
probe with design.md struck from the footer (`map-unlisted`).

2026-09-15 probe 2 — `map-unlisted`, k=5: design reads 1/5 (offset 79, `0.3 Tiers`), 2/5 wrote
tests at once, 2/5 read combat source. No better than the map alone; the footer is not the lever.

2026-09-15 probe 3 — after the stale-note fix in `build_steps.compact` / `turn_log._compacted`
(the transcript now replays with ONE note; probes 1–2 and the branch carried the turn-30 note
too). `map-fresh` k=5: design reads 2/5 — one at 79+2843 (Tiers, then DoD), one straight to
`offset=2784, lines=40`, the first section-9 read in the lab; 1 no-tool-call. `map-fresh-unlisted`
k=5: design reads 0/5, 2 wrote tests at once, 2 called nothing in the tool list, 1 read combat
source. Striking design.md from the footer looks no better than leaving it, twice now (1/5, 0/5
vs 3/5, 2/5). Sample sizes are 5; treat as direction, not a rate.

2026-09-15 03:12 overnight run 1 `9c62c1d1e58c` (tower defense): design 20 min, build done at
turn 120/200 in 27 min, 4 compactions. Design reads: 0 whole-file (control 41), 33 by range, 5 of
them into `9. TESTS`. Tests written 60 in `js/tests.js`, named exactly as the design's table
(`T01 debug_api_exists` …). Error gate 0 rounds, play gate 0 broken: "The full flow works: Main
Menu → Play → Campaign → Gameplay … clicking a valid tile places the tower". Summary claims all
3 tiers, 58/58 tests. 0 `__press` in the build — the gate's 200 ms tap carried the keys.

2026-09-15 03:57 overnight run 2 `e9d964fc34c7` (fishing lake): design 20 min, build done at
100/200 in 30 min, 3 compactions. Design reads 1 whole / 23 ranged / 2 into section 9. 62 tests,
65/66 of the design's names present. 24 `__press`. Gates: error 0 rounds, play 0 broken —
"Every documented control responded as expected … Holding Space charged and cast the line".
Plain DOM game, no canvas.

2026-09-15 05:21 overnight run 3 `112ec65202b2` (rhythm platformer): design 20 min, build hit
the 200 cap at 68 min, 6 compactions, no done → no gates. Design reads 2 whole / 21 ranged / 0
into section 9 (this design's section 9 is 3 backticked names; tests live in `js/tests.js`,
14 green by turn 160). Where the turns went: 16 = 30K-token reasoning blowout, no call; 60–140
= tuning a bot that clears the generated levels (fair: the levels ARE the game); 144–199 = 55
turns verifying the Definition of Done one small ranged read at a time ("Let me verify the
config numeric values match the spec…"), Tier 1 declared at 198, Tier 2 opened at 199, cap.
Map working as intended there (every read by range), but a box-by-box crawl at one read per
turn is the `check_off` tool's case. A capped build gets no play gate — prod gap to note.

2026-09-15 06:14 overnight run 4 `202198c78de5` (space salvage): design 20 min, build hit the
200 cap at 36 min, 7 compactions, no done → no gates. 34 tests, 35/36 of the design's names,
32 `__press`, all green by turn 160. Design reads 18 whole / 31 ranged / 2 into section 9 —
the whole-file reads are the search-and-print idiom (see the turn list below), not dumps.
Turns 160–199: Definition of Done verification, then filling the boxes it found unmet
(camera shake formulas, seven SFX triggers), one read per turn, cap. Second cap-out in the DoD
crawl.

2026-09-15 07:04 overnight run 5 `9e6f192bd791` (water-pipe puzzle): design 20 min, build
finalized FAILED at step 96 after 35 min: "stalled: 4 turns cut off by the output limit". Prompt
114K of 131K after 5 compactions → out cap 17K; turns 90–95 thought 26–37K tokens each about a
rework the DoD demanded (DOM tiles with data-attributes, the level table) and never emitted a
call. Compaction did not fire between the re-sends (prompt under its trigger), so the window
never reopened. Design reads 10 search-idiom / 23 ranged / 3 into section 9; no test files yet
(the design wants `test.html` + `tests/test.js`, never reached). 24 levels solving at turn 84.

## Outcome

Battery, five fresh asks, full local prod path (design chain → build at cap 200 → gates), src as
it stands. Control `f91ade83c0d0` in the last row.

| run | ask | design reads whole/ranged/§9 | tests: written, design-named | end | gates |
| --- | --- | --- | --- | --- | --- |
| 9c62c1d1e58c | tower defense | 0 / 33 / 5 | 60, 58/58 | done 120 | clean, 0 broken |
| e9d964fc34c7 | fishing lake | 1 / 23 / 2 | 62, 65/66 | done 100 | clean, 0 broken |
| 112ec65202b2 | rhythm platformer | 2 / 21 / 0 | 14 in js/tests.js, 1/3 | cap 200 (Tier 1 verified at 198) | not run |
| 202198c78de5 | space salvage | 18* / 31 / 2 | 34, 35/36 | cap 200 (green at 160, DoD crawl) | not run |
| 9e6f192bd791 | pipe puzzle | 10* / 23 / 3 | 0 | FAILED 96, 4× output cut-off | not run |
| f91ade83c0d0 | story RPG (control) | 41 / 20 / 0 | 47, 1/121 | done 478 (cap 1000) | play: 6 broken |

\* search-and-print idiom (`read_file` then slice or regex), not full dumps; the control's 41
were 12 chunked reads plus 29 later re-reads.

What the map bought: every run read the design by range after its first pass (the control
re-read it whole 29 times), and every run that reached tests named them after the design's
section 9 (58/58, 65/66, 35/36; control 1/121). Two finished games with both gates clean, in
27 and 30 min at the 200 cap. What it did not buy: the two cap-outs were both spent in a
box-by-box Definition-of-Done crawl AFTER the suite was green (turns 144–199, 160–199), one
ranged read per turn — the `check_off(row)` tool's case. Run 5 is a different lever: a turn cut
off by the output limit should compact before it is re-sent, or the window never reopens.

Shipped in src (uncommitted): `code_map.py` maps `.md` by heading; `build_steps.compact` keeps
one note; `turn_log._compacted` mirrors it; play gate `TAP_MS`. Playable copies at
`runtime/games/<run id>/index.html` on :8765. Design-less run `da1359f0b766` (two-worker 503
fallback) discarded, see the log.

The map locates: with headings in the note the builder's first move goes to a design section by
line number 3/5 and 2/5 times (two probes) against 1/5 blind, once to section 9 itself. It does not go to `9. TESTS`, in any of 10 map samples or
the 8-turn branch — the system prompt says "check every box in definition of done", so that is
the heading it picks. The branch wrote its own 54-test suite as the source run wrote its own 47.

Shipped: `code_map.py` maps `.md` by heading with line ranges (tested), 66 lines / ~700 tokens for
this design; general, kept. Not shipped: anything that makes section 9 the target — that is a
prompt line (the build prompt or the DoD naming the tests file), a separate arm. `lib.replay` gap
noted: staged `design/` and `docs/` are not seeded into a replayed world. Found and fixed on the
way: `compact()` kept every earlier note as its own round (two in this transcript at 105), now it
keeps the newest only, mirrored in the turn-log replay.
