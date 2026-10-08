# tests in files, one in-page runner

Status: single-run
Control: prove-it run `17c92bff6bda` (station, the branch's design chain + `build.txt` at xhigh,
2026-09-14: capped 200, 75 plays, wrote tests.js + tests.html and never ran them). Run 1 below used
the spec-skeleton lab's own prompt and a skeleton-prompt design — not the production harness — and
is kept for its numbers only.

## Purpose

Every build under the layered prompt verified one scenario per play() call, one call per turn:
platformer spent 106 turns on 106 probe scripts and capped mid-list. Island, the run that finished,
wrote `tests/*.test.js` plus an in-page runner on its own and ran the whole suite through one
play(). The two finishers also tested as they wrote; the capped three wrote everything by turn ~25
and then only tested. Same verification, five to ten times the turns.

## Hypothesis

One build-prompt line: tests live in `tests/` as files, one in-page runner, one play() runs them
all, a test is written with each system. Measured: plays per build, turns to done, cap rate, on
the five spec-skeleton asks. Expect plays to fall by half or more and platformer/collector to
reach done under 200. Idea failure: the model still writes one ad-hoc probe per turn, or the
suite runs but the builder ignores its failures.

## Setup

- Model: qwen3.8_27b_quasar via ninfer on :8090 (131K, int8 KV, DFlash2 K=7). Card: local 5090.
  Box `llm.reasoning` = xhigh for both stages, as the control.
- Ask: "Survive on a derelict space station." Design: the control's `design.md` (gameplay → visual
  → engineering → integrator on the branch's chain), copied into the new run; the request line is
  `prompts/request.txt` as the chain writes it. Same design, same request, same builder.
- Change: the one bullet in `src/maestro/codegen/prompts/build.txt` (uncommitted on branch
  design-team, `git diff` shows it): tests live in `tests/<system>.test.js` written with the system,
  `tests/run.js` imports them all and exports `run()`, one play() runs the suite through
  `await import('./tests/run.js')`, a check typed into play() twice is a test in a file.

    ./build.sh 17c92bff6bda "station — tests-in-files" > logs/build.station.log   # rid on line 1
    ./watch.sh <rid>                       # heartbeat + stall flag + :8765 sync, detached
    python tally.py <rid> 17c92bff6bda     # plays / reads / writes / edits / suite runs / done / tests on disk

Control by the same tally: 200 turns, 75 plays, 94 reads, 8 writes, 57 edits, 5 compactions, 6
no-call turns, no done, no `tests/`.

## Log

### 2026-09-14 build, platformer, tests-in-files rule — INVALID HARNESS, run `bc82418d2c0b`

Nick: not the production build prompt (the spec-skeleton lab's layered variant) and a design from
the skeleton prompt, not the branch's chain. Numbers stand as a first look at the mechanism only.

`build.sh` (cap 200), `watch.sh` beside it, log `logs/build.platformer.log`. **Done at turn 110,
111 steps, 31 min wall, 23.9 llm exec-min**, 5 compactions (21/34/58/71/107), 0 out-cap turns,
error gate 0 rounds, play gate 0 broken / 0 rounds. Play: http://127.0.0.1:8765/bc82418d2c0b/index.html

| | control `82592d612763` | this run |
|---|---:|---:|
| steps | 200 (capped) | 111 (done) |
| play() calls | 106 | 43 |
| suite runs (play importing tests/run.js) | 0 | 11 |
| read / write / edit | 88 / 14 / 69 | 65 / 54 / 0 |
| compactions | 4 | 5 |
| llm exec-min | 27.2 | 23.9 |
| tests on disk | none | 26 files, 24 suites, 18 KB |

Shape: turns 1–11 whole spec + libs (unchanged); 12–31 every game file; turn 32 `tests/_util.js`
+ 24 `<system>.test.js` + `tests/run.js` in one program — the runner and the import line exactly
as the rule gives them, one `run()` export per file, failures keyed by suite. Suite at 35/36
misfired (result handled as a dict; page had no `window.__game`), first real run at 42: 7 suites
failing (sifter fired 0 pellets, boss death never armed the conduit, crouch cap 240 not 120, pit
ignored the heart cost, float epsilon); 45: 3 failing; 51: green. Re-run green at 65/66/87/107,
last one right before done. Between suite runs it still typed ad-hoc probes (43–64, 77–106:
stage traversal with a bot, boss fights, real-key checks) — the probes are for the thing at hand,
the suite for regressions, which is the split the rule asked for.

Not as written: (1) tests came AFTER all game files, not with each system; (2) zero `edit_file`
calls — every change was read_file → str.replace → write_file, against the prompt's own rule
(control: 69 edits). Watch (2) on the battery: whole-file rewrites cost output tokens and risk
clobbering.

Test quality, read by hand (Claude): files map 1:1 to §9's table with its filenames, debug calls
and numbers (chirp 7/950/4/0.7, hush phase at 60 %, w1s5 → w2s1), and they found ten real bugs.
But coverage is ~1/3 of §9's rows (physics 6 of 18: no coyote/buffer/jump-cut/gravity/one-way/
moving platform; weapons no Bloom split/switch cooldown/locked deny; boss no Null phases), bounds
are loose where the spec gives a number (`vx > 200` for accel 240), `allStagesSmoke` and
`fullGame` cannot fail (truthy stage after 5 s; completeStage() ×10 counts 10), some tests reach
into internals (`p._shots.length = 0`, `m.hp = 30`), and one function per file means the first
assert hides the rest. The prompt still carries the control's "the design's full test suite is
for the people who judge the game, not a gate you must pass" line; a follow-up arm drops it or
names §9's rows as the tests.

Gate impression: "strong industrial-cyberpunk aesthetic... canal/sump environment atmospheric and
distinct from Mario's bright palette. UI clean... Firing (mouse click and J key) was never
confirmed as producing a visible projectile across multiple attempts, though not definitively
broken... character sprite quite small relative to the environment."

Numbers: plays 106 → 43, done at 110, same design, same builder, one bullet.

**Nick played it (2026-09-14 evening): "the test files passing gave it a false sense of
'succeeded'."** The game draws in the top-left quarter of the screen and he cannot aim; otherwise
it works. Rated worse than the control's platformer, "but not by much at all".

Cause, read from the code: `js/main.js` calls `createCanvas(canvas, {960×540})` and then never
calls `view.begin()` — it draws logical units straight onto a window-sized backing store, so on a
1080p screen the world is exactly the top-left quarter. Mouse aim: `js/input.js` sets
`mouse.worldX/Y` only through `debug.setMouseWorld` / the debug mouse record; the real path copies
`mouse.x` to `screenX` and never converts (`view.toWorld` is called nowhere). The suite sets the
mouse through debug, so every aim test passes; no test asserts the canvas transform. Zero
`__press` in any test file; real keys got 9 turns in the whole run, none in the pre-done check
(turn 109 = clean boot + suites green → done). The gate saw firing "never confirmed" and called
it unclear, so no fix round.

Verdict: **works as a step lever, fails as a quality lever.** Same shape as spec-skeleton finding
(3): API-driven checks prove state, not input → sim → render, and a green suite of them is a done
signal the builder trusts. The control never called done and capped at 200 with a game Nick
rated higher. Next arm, one line more on the rule: a suite that never presses a key proves nothing
about the game — one test per control through `__press`, and done needs those green. Alternative
on the gate side: "unclear" on a core verb becomes a fix round. Battery waits on that arm.

### 2026-09-14 21:35 build, station, bullet in the real build.txt — CAPPED, implementation fixes needed, run `f3706326f1f6`

`build.sh 17c92bff6bda`: design.md and request byte-identical to the control; the cursor's system
prompt carries the bullet. **Capped at 200, no done, 46 min wall, 43.1 llm exec-min, 10
compactions.** Play (as capped): http://127.0.0.1:8765/f3706326f1f6/index.html
Smoke after the cap (play module, real KeyD 500 ms): `{"ok": true, "result": "{\"game\":true,\"state\":[\"time\",\"paused\",\"dead\",\"won\",\"deathCause\",\"player\",\"inventory\",\"inventoryMax\"],\"player\":{\"x\":19.5,\"y\":17.5,\"o2\":100,\"health\":100,\"selectedSlot\":0,\"attackCooldown\":0,\"movement\":{\"x\":0,\"y\":0},\"facing\":\"down\",\"hu`

| | control `17c92bff6bda` | this run |
|---|---:|---:|
| steps | 200 (capped) | 200 (capped) |
| play() calls | 75 | 34 |
| suite runs | 0 | 18 |
| read / write / edit | 94 / 8 / 57 | 111 / 21 / 56 |
| design.md reads | 46 | 64 |
| game.js written in full | 1× (t32) | 4× (t21, 57, 74, 90) |
| compactions | 5 | 10 |
| llm exec-min | 70.7 | 43.1 |
| turns with `__press` | 9 | 0 |
| no-call (thinking-only) turns | 10 | 5 |
| tests on disk | tests.js + tests.html (never run) | tests/core.test.js + tests/run.js, AND tests.js + tests.html |

Shape. Turns 0–15 design.md in slices; 21–27 game.js as ONE IIFE in 7 chunks; 28 `tests/core.test.js`
right after it (the rule's "with the system" held here); 34 first suite run — every test failed at
its `moveTo` helper ("reach panel"), the harness could not walk the player; 39 again. Then the
cycle: compaction → design.md re-read (~10 turns) → game.js rewritten from scratch (57, 74, 90),
three times, "to match the design exactly". Suite at 149: 9 failing; 170: 9 failing (prompts,
launch, LOS); **193: green**. 144–151 it ALSO wrote the spec's `tests.js` + `tests.html` and
turned `tests/run.js` into a bridge that calls `window.__runAllTests()` — the design (line 3020,
DoD: `window.__testResults.failed` is 0) mandates that harness; the rule mandates `tests/run.js`;
it built both. 153–169: eleven turns lost to `play(...)` called without `print(...)` ("the program
ran and printed nothing" ×3, then hello-world probes) — the bullet shows the JS line and not the
Python line around it. 196–199 checking `__testResults.total` when the cap hit.

Why the rewrites (both runs, the control too): `code_map.py` lists top-level declarations and the
functions one level inside a MATCHED top-level declaration; a file that is one
`(function () { ... })()` matches nothing, so every compaction note in both runs says
`game.js (1300 lines)` with no declarations. The model reads that as an empty file, re-reads the
spec and rewrites. Control: 5 compactions, 1 rewrite; arm: 10, 4. Product fix, out of scope
here: treat a column-0 `(function` / `(() =>` wrapper as a top-level scope.

Verdict: **implementation, not idea — three fixes, then rerun.** (1) The bullet's example must be
the whole Python line, `print(play("return await (await import('./tests/run.js')).run();", 60))`.
(2) The design chain's engineering prompt tells the designer tests run from `tests.html` through
`window.__testResults`; the build rule says `tests/run.js`. One law in both places, or the spec's
line goes — Nick's call, it is his design prompt. (3) The IIFE code-map hole drives the
rewrite cycle that ate ~60 turns here; fixing it before the rerun removes a confound that has
nothing to do with tests. Open: xhigh for the build stage (the control at xhigh capped too; last
night's finishing builds were at medium) — a medium pair (control + arm) is 2 × ~30 min.

### 2026-09-14 22:40 full chain, RPG ask — FELL BACK TO THE BARE ASK, run `d615927dc0fe`, stopped at step 7

Nick on the station run: "surprisingly good. The issues are design issues as opposed to functional
issues" — fix what is broken, then a full call on a new concept. Fixed in the working tree (all
uncommitted, branch design-team, `git diff`): (1) `code_map.py` maps a column-0 closure one level
in, with a test (`tests/test_code_map.py`, 16 pass); on the station game.js the map now lists its
~90 declarations instead of nothing; (2) `prompts/design/engineering.txt` tells the engineer the
harness is `tests/<system>.test.js` + `tests/run.js` run inside index.html, never a separate page;
(3) the build bullet's example is the whole Python line, `print(play(..., 60))`.
Ask: "A linear story RPG where the player awakens in a world remembering nothing, and journeys to
find himself, saving the world in the process." `run_full.sh` = `python -m maestro.codegen.run
"<ask>"` (design chain then build, box reasoning xhigh for both), log `logs/full.rpg.log`,
`watch.sh d615927dc0fe`. No control: first RPG ask; the station pair above is the reference shape.

gameplay.md landed in 240 s (53K out tokens), visual.md in 142 s (29K); the engineering call ran
378 s to the 100K output cap and returned no text — a reasoning-only runaway — and `design.generate`
raised "engineering came back empty" → "the ask is the prompt" → a build from the bare ask started.
Stopped by hand at step 7 (`build_chain.stop`). Product defect, both design paths: one empty reply
(3–7 % of turns on this model, [[local-model-quirks]]: retry, never salvage) silently ships the
user a no-design game. Fixed in the working tree: `design.RETRIES = 1` — an empty reply is asked
for again once with the same message, CLI (`_call`) and queue (`on_complete` + a `.retried-<step>`
marker) alike; a worker error still falls back at once. `tests/test_design.py`: 10 pass (new
test for the retry, the never-lands cases now go through it, the CLI chain test carries an empty
reply in the middle).

### 2026-09-14 23:13 full chain, RPG ask, retry fix — CAPPED 200 in 26 min, suite green, run `f91ade83c0d0`

Same ask, same command (`run_full.sh`, log `logs/full.rpg2.log`). Play (as capped, no gate ran):
http://127.0.0.1:8765/f91ade83c0d0/index.html — boots to the title screen, canvas up, `window.__game`
= {version 0.1.0, state(), commands: title/world/combat/narrative/progression/save/audio/ui/debug}.

Design, 18 min, no retry needed: gameplay 215 s / 46K out tokens, visual 195 s / 41K, engineering
337 s / 71K, integrator 296 s / 59K → spec.md 122 KB, every section present in one call.
engineering.md took the new harness line: 44 references to `tests/run.js` / `*.test.js`, "tests
must run inside the loaded game page, never a separate test page", zero `tests.html`; spec.md the
same (3 / 0).

Build: **200 turns in 26 min, 21.2 llm exec-min** (mean 8 s a turn — the cap, not the GPU, ended
it), 5 compactions (31/80/130/155/186), 70 plays, 10 suite runs, 55 reads / 46 writes / 74 edits,
1 no-call turn, 0 `__press`, no done. 20 ES modules under `js/` (config, save, input, data/scenes
per act, combat/{grid,engine,damage,statuses,unit}, state, world, game, render, api, main), no
IIFE. **After every compaction the reads are line-ranged** (`read_file("design/design.md", 965,
120)`, `read_file("js/game.js", 95, 30)`), no file was re-read whole, no file was rewritten from
scratch — the code-map fix at work (37 design reads, all slices). Tests: 9 files / 47 tests
written at turns 105–109 AFTER all game code (not "with the system"); suite 9 failing at 110 → 1
at 115 → 0 at 126, green again at 131 and 158; turns 172–178 refactored `window.__game` into
`js/api.js` (the spec's §8 command surface) and rewrote `tests/util.js` + `tests/run.js` to it;
suite at 189 returned `{}`; the last ten turns were checking each test file's exports and reading
`prologue.js` — mid-verification when the cap hit.

**Nick played it (2026-09-15 00:10): "it straight up doesn't work. Hitting enter doesn't do
anything."** Reproduced with real keys through the play module: Enter, Space, E, Z all leave
`mode` at "title". Cause: `js/input.js` registers its keydown listeners only inside `attach(el)`,
and nothing in the project calls `attach` — `game.js:23` creates the input and never attaches it.
The title handler at `game.js:409` is correct; no key ever reaches it. One line
(`input.attach(window)` after the create) on the served copy only, and Enter → "dialogue", scene
prologue-1. The run dir is untouched. Every one of the 70 plays and all 47 tests drove
`window.__game` commands; `__press` count 0. The suite was green on a game no key could start.

Read: the mechanics all held this time (retry, harness in the spec, no rewrite cycle, suite used
as a regression net), and the build ran out of turns, not of GPU or of ideas. A 200-turn cap sized
for 30 s turns is 26 min of an 8 s-turn build; whether this game is done or half-done is Nick's
play. Open: the cap; "with the system" is still ignored (tests come after the code, twice now);
0 real key presses in 200 turns.

### 2026-09-15 00:30 RPG `f91ade83c0d0`, cap raised 200 → 1000, resumed from its recorded position

Nick, after playing: "still broken — an exception about boxes in combat; this one hasn't
succeeded." His call: not a change note, the same build continued — cap lifted to 1000, replay
from step 200. `raise_cap.sh f91ade83c0d0 1000`: cursor back to phase build with the new cap, the
DB build row back to running, `build_chain.resume`; same 178-message transcript (55K tokens, 5
compactions), same game folder. The served copy's hand patch (input.attach) is overwritten when
this stages again. `watch.sh` beside it.

First resume ended at step 201 "hit the 200-turn cap": a SECOND cap, `build_steps.MAX_TURNS =
200`, a module constant checked on `cursor.turn`, sat beside the cursor's `max_steps` and won,
so `max_steps` (the kickoff argument, the CLI's `--build` default) was dead. Fixed in the working
tree: the step machine reads `cursor.max_steps`; `tests/test_build.py` pins the cursor's cap at
500 and 1000 (89 pass in test_build + test_turn_log). Control plane restarted on the new code,
`raise_cap.sh` again at 00:40: step 214 within the first minute.

### 2026-09-15 00:55 state at PC shutdown — RPG `f91ade83c0d0`, fix round 2 in flight

Main build under the raised cap: **done called at step 479** (ok=True), 15 compactions. Since 200:
~60 plays / 40 edits per 100 turns, 0 suite runs, 0 `__press`, long stretches editing
`tests/util.js` (its combat-runner helper) with debug logging on and off. Error gate 0 rounds.
**Play gate: 2 rounds (the cap)**, last fact "d | Player character moves one grid space to the
right" — real keys found it broken (input never attached, see above), fix round 2 was at step
42 when the PC went down. Cursor is durable: after reboot start ninfer (hand), `local_gpu.py
auto`, the control plane, then `build_chain.resume('f91ade83c0d0')`; `raise_cap.sh` is not
needed (the cursor's cap is 1000 and the fix build has its own). Play (pre-fix as staged):
http://127.0.0.1:8765/f91ade83c0d0/index.html
Uncommitted working tree (8 files): code_map closure fix + test, design retry + tests, build_steps
cursor cap + test, build.txt bullet, engineering.txt harness line. 1037 tests pass.

## Outcome
