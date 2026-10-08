# spec-skeleton — the design stage writes a build spec, not a systems design

Status: single-run
Control: the prod design prompt (`variants/ctrl.txt`, `src/maestro/codegen/prompts/design.txt`)
on the same asks and builder. Baseline builds: the 2026-09-06 cost-per-game battery (6/6 delivered,
$1.81 mean) and the ashworth-street lab's island builds (`labs/ashworth-street/arms.md`).

## Purpose

`labs/ashworth-street/design.md` is a 274 KB build spec Fable 5.1 wrote for a subway-station FPS.
One local 27B built it unattended in ~12 h into a game of a class our pipeline has never produced.
The spec is not longer prose: it has scope with the user's asks mapped to sections, conventions,
file contracts, a debug API the tests drive, numbered tests, a build order, a definition of done,
and a sanity pass that fixes the sections above it. Our design prompt produces none of that. The
ashworth-street lab reduced that document to a skeleton prompt (`variants/skel.txt`) and ran it
loosely across several arms in one folder. This lab reruns the winning path once, in the template's
shape, so the result is reproducible from this folder alone.

## Hypothesis

**What changes.** `design.txt` is replaced by `variants/skel.txt`: a 13-section build spec
(SCOPE with an asked→section table and tiers, CONVENTIONS, CONTRACTS with file layout, VISUAL,
GAMEPLAY, CHARACTERS, AUDIO, UX, DEBUG API, TESTS, BUILD ORDER, DEFINITION OF DONE, SANITY).
The designer runs at `reasoning_effort=xhigh`; the design is pinned as the build prompt.

**What is measured.**
1. The design is complete: every section present through SANITY, and SANITY does arithmetic
   (closes a timing or resource pair) rather than name-checks.
2. The build passes its own section-9 tests through `window.__game`, run by the builder via
   `play()`, and the play gate reports 0 broken / all predictions met, with 0 fix rounds.
3. Steps and GPU minutes to `done`, against the ~20-step / no-play control build.
4. Nick plays it: is it a better game than the control design's build of the same ask.

**Why it should move.** The debug API plus numbered tests give the builder something to check
against instead of a done nudge about "the first thirty seconds"; the conventions and file
contracts remove the mid-build re-deciding that produced two coordinate systems and dead inputs;
SANITY catches the field-without-a-record and consumable-budget defects before a line is written.

**Idea failure looks like.** The design completes but the builder ignores sections 8 and 9
(no `window.__game`, tests never run), or the build lands at the same play-gate result as the
control with more steps, or Nick cannot tell the two games apart.

## Setup

- Model: qwen3.8_27b_quasar via ninfer on :8090 (131K, int8 KV). Card: local 5090.
- Ask: `island` from `asks.json` ("An open world game where you explore an island and find
  treasure."). One ask, one run.
- Repo at `41bd38f` (play() in the builder) with the uncommitted worker-complete fix in
  `db/jobs.py` if the hand-started worker's rate is NULL.

Design (no control plane needed):

    ARM=skel REASONING=xhigh SLUGS=island ./design.sh > logs/design.island.skel.xhigh.log

Build (control plane `venv/bin/python run.py` from the repo root, `./worker.sh` in a second shell):

    ./build.sh designs/island.skel.xhigh.md "island — skel xhigh" > logs/build.island.skel.xhigh.log

Run dir: `~/output/runs/<run id>/`, turns in `turns.jsonl`, game under its game folder.

## Log

### 2026-09-12 design, island, skel @ xhigh — works

`design.sh`, 78 s, 11.1K completion tokens, 14K think chars, 23K chars out, finish_reason stop.
All 12 sections through A. SANITY present. SANITY closed five checks with arithmetic (dash
0.15 s × 17.3 t/s = 2.6 t; check 4 distance from step(1/60,190); points supply 7,500 vs gate
2,500) and edited §4.3/§2.3 so the compass never reads an undefined target. Went 2D top-down.
Shorter than the ashworth xhigh island design (38K chars, 33K tokens, 110K think) — xhigh think
length varies run to run; completeness held anyway. Design: `designs/island.skel.xhigh.md`.

### 2026-09-12 build, island, pinned skel @ xhigh design, with play() — works; Nick plays

`build.sh`, run `90525219fb73`, cap 200. 104 steps, 51 min wall, 29.6 GPU-min over 120 jobs
(gates included), 2 compactions, done at 99 and again at 101/103 after the nudge. Error gate
0 rounds. Play gate 0 broken, 0 fix rounds; predictions: movement, HUD, compass, minimap, clock,
biomes all met. Turns: 78 of 104 called `play()`, 4 big writes, 10 edits, zero read-only
spirals after either compaction. `window.__game` carries every §8 call. It ran the §9 suite
from turn 8 and the tests found real bugs: `seed` state field shadowing `seed()` (t12), rng not
an object (t14), a page hang from one long synchronous `step` (t22, bisected), swapped axis
push in `collideCircle` that let the player through walls (t69), a buggy test helper of its
own (t94). "All 12 §9 checks pass" at t78 and again t95. Game: ~1,300 lines over 9 modules,
2D top-down, code-drawn art. Reproduces the ashworth v2 island build (b5dc1d577b9b: 60 steps,
15/15 tests) in shape; longer here because it chased a flaky sync-step test for ~15 turns.

Open on the game: the play gate pressed E beside a chest twice, points stayed 0, chest stayed —
both verdicts "unclear", so no fix round fired. Either the 1.2-tile range misses a chest one
tile away or the key never reaches `interactQueued`. Nick's play decides. Gate note, out of
scope here: repeated "unclear" on the core action never becomes a fix round.

Art: none requested, none made. The skeleton has no ART clause (ctrl's "ask for <thing> as a
sprite/scene/anim" is absent), so §3 wrote code recipes for every subject (NPCs, player, sun,
moon). Turn 0 saw the conflict with the builder's own art rule and followed the spec; the run
made only llm jobs. Ashworth `arms.md` saw the same on the forest xhigh design; this is the
first build-level confirmation. Nick's ruling 2026-09-12: no ART clause. Generation is
unproven and the builder has no vision to check it, so a no-art game is fine; the builder keeps
generate_media for the case it wants it. Prompt unchanged.

Nick played the island build: minor flaws, generally quite good. Ladder moves up: designs for
the other three asks at xhigh, reviewed before any build.

### 2026-09-12 designs, collector / station / forest, skel @ xhigh — works; awaiting Nick's read

`design.sh`, serial. All three complete through A. SANITY, finish_reason stop, all top-down 2D.

| ask | secs | tokens | think chars | chars | lines | sanity |
|---|---|---|---|---|---|---|
| collector | 252 | 39.5K | 96K | 41K | 1146 | 7 checks as a table, all close; regrow-vs-harvest and museum demand computed |
| station | 288 | 46.3K | 101K | 50K | 1427 | 6 checks; EDITED the design 5 times to make tests exact (first event → 50 s, breaker ±10, shield → 30 s timer) |
| forest | 248 | 38.8K | 91K | 40K | 733 | closed every check; added 9 debug calls §9 used but §8 lacked; battery 300 vs 180 s drain |

Think length this round 91–101K on all three (island was 14K): xhigh deep think held.
Designs: `designs/<ask>.skel.xhigh.md`. No build until Nick reads them.

Read in full (Claude). As games: station > forest > collector. Station is real triage (six
coupled meters, events every 40-50 s, caps, drones cost wrench time) on a fixed 24x16 map.
Forest is a clean 180 s loop with light as the weapon. Collector has no tension and seven DOM
panels, and tiers the asked-for museum as T2. Defects found by hand: station tests 9, 11, 12
compute step(0.1, 10) as 10 s not 1 s (fuel 10 vs 19, radiation 50 vs 23, storm 50 vs 5);
collector test 12 lastRefreshDay 4 vs 6; forest test 11 assumes a stop at attack range no
rule states, test 16 hedges the fog field. All four designs so far are top-down 2D: the
skeleton has no decide-2D-or-3D clause. Recommendation: build station as-is (wrong tests are
the probe: does the builder bend the sim or fix the test), forest second.
Nick: collector is the interesting one BECAUSE cozy games have no obvious win/lose — the hard case for a spec-and-test loop; station first anyway.

Fifth ask added 2026-09-13, `platformer` (side-scrolling platformer shooter, 4 guns,
jump/move/crouch, 2 worlds x 5 stages, not Mario). Control exists: a prod build of this exact
ask (Flash-Next, ctrl design prompt, two passes) that its requester called "arguably
prod/market ready right now... I am legitimately going to play this through". Run id not
recorded here. The skeleton arm has to at least match that.

### 2026-09-13 design, platformer, skel @ xhigh — works; awaiting Nick's read

286 s, 43.9K tokens, 42K chars, 792 lines, complete through SANITY, side-scroller ("Conduit
Run": courier Kite, rusted machines, 3 signal nodes open each exit). 4 guns with damage/
cooldown/speed/lifetime/energy each; per-stage table (width, roster, node x, checkpoint, exit,
unlock); coyote 0.10 / buffer 0.15 / variable jump; bosses at 1-5 and 2-5 with 3 phases.
Sanity did the jump arithmetic (17²/90 = 3.21 tiles vs 3-tile step) and retuned rail cost +
boss energy cells. 24 tests; the ones checked by hand close (run 7 t/s → x 9; pulse 2 shots in
0.2 s; rail 4 dmg pierce 1 kills two 1-hp mites → score 200; 1-1 roster 6). Cleaner tests than
station. Risks: stage layouts are a generator ("one-way platforms every 12 tiles"), not
authored — the samey-stage failure; boss patterns are prose with thin numbers; T1 = 10 stages
+ 4 guns + 5 enemy kinds is the biggest T1 so far, cap-out risk at 200 steps.
Design: `designs/platformer.skel.xhigh.md`. Build queued after station.

### 2026-09-13 build, platformer — IN PROGRESS, run `6e2271a9571d`, PC restart at step 56

Started 00:35 after station. PC restarted ~00:55 with the build at step 56 (2 compactions).
Control plane, `local_gpu.py auto` (with NINFER_BIN), and the :8765 static server brought back
detached; `build_chain.resume('6e2271a9571d')` re-drove it at 01:03, next turn claimed at once.
Wall clock tainted, steps are not. The `build.sh` waiter died with the PC; the result line comes
from `build_state.json` instead of `logs/build.platformer.skel.xhigh.log`.

Turns 57–78 after resume: the builder wrote a state-driven PLAYTHROUGH BOT (scans 6 tiles
ahead via getState, jumps pits, crouches gaps, dodges boss lasers by teleport) and drove every
stage with it. Found: shrikes flew above ground-fire height (unhittable), a determinism bug
(`setSeed` called `loadStage` and shifted the RNG for a later `setStage`), a missing step
platform under an elevated node. The builder is BLIND: play() returns text only, screenshots
exist only in the post-done play gate and never reach the builder. Next-arm candidate, out of
scope here: play() returns a screenshot the builder can read (ninfer --vision is already on).
Evidence: all three builders read §9 SCREENSHOTS, said "I can't take screenshots" (island t78,
station t28/t53, platformer t28) and substituted canvas-pixel / DOM-width proxies.

DONE: 143 steps (142 turns: 91 play, 6 writes, 16 edits), 4 compactions, 38.0 llm GPU-min, no
art asked for. Done at 129, again at 138 after the nudge (nudge bought an on-stage objective
message). Error gate 0 rounds, play gate 0 broken / 7 met, 3 unclear. All 24 design tests pass.
Gate impression: "clean dark sci-fi aesthetic and clear HUD... but the difficulty is extremely
punishing — dies within 10–15 s on a fresh stage... projectile small and hard to see." The
bot proved every stage CLEARABLE by an invincible agent; nothing proved it FAIR for a human,
and the design's balance section ("player can clear every stage without being forced to take
damage") was never a test. Bar: Nick's buddy's prod build of this ask. VERDICT: Nick plays.
Play: http://127.0.0.1:8765/6e2271a9571d/index.html

### 2026-09-13 builds, collector then forest — IN PROGRESS (`run_two.sh`)

collector `555cb9cb61fb` started 01:37. Asked for art at turn 8 (2 image jobs done, 2 mesh
jobs). `local_gpu.py auto` CRASHED on the mesh leg: `SPRITE_PYTHON` defaults to
~/Documents/Labs/rig-lab/venv-kimodo/bin/python, which no longer exists anywhere on disk
(labs moved). Build sat on a pending llm turn ~26 min; mesh jobs abandoned by hand at 02:15,
auto relaunched, turn claimed. The station build's 2 lost mesh jobs were most likely this
same crash, not the monitor stop. Watcher now abandons pending mesh jobs on sight and
relaunches auto if it dies. Mesh art is therefore unavailable to these two builds. Out of
scope: `local_gpu.py` should fail the mesh leg, not the process, when its venv is absent.

collector DONE: 70 steps (35 play, 5 writes, 17 edits), 1 compaction, 18.0 llm GPU-min + 0.9
image (2 renders; 2 mesh lost to the auto crash). Error gate 0, play gate 0 broken / 8 met,
2 unclear. Gate impression: "clean, readable top-down presentation... tutorial prompt and
contextual harvest prompt make the interaction model immediately clear... cozy aesthetic
works" — the ONLY gate impression of the five with no balance complaint. Nick's hard case
(no win/lose) came out the calmest. VERDICT: Nick plays.
Play: http://127.0.0.1:8765/555cb9cb61fb/index.html
forest `1eea746f3617` started at once.

### 2026-09-13 overnight queue (`run_ctrl.sh`) — CONTROL arm + corrected station

After forest: every ask through `python -m maestro.codegen.run "<ask>"` — the prod design prompt
(`design.txt`, records/systems form) at prod's reasoning (`medium`) and the same builder with
play(). These are the fair pairs for Nick's side-by-side play. Confound, accepted: skeleton
designs were made at xhigh, control designs at medium — this is "prod as-is", not effort-
matched. Then `designs/station.skel.xhigh.fixed.md`: the station skeleton design with tests
9/11/12 corrected by hand (fuel 19, radiation 23, storm 5), one build, to isolate whether the
bent RATES were only the wrong tests. Run ids land in `builds.tsv`; logs `build.<ask>.ctrl.log`
and `build.station.fixed.log`; games synced to :8765 as each finishes.

### 2026-09-13 build, station — IN PROGRESS, run `cb639a3af329`, stalled 23:41–00:23

Turn 0 repeated the designer's error: read step(0.1, 10) as 10 s and ticked test 9 as consistent.
Turns 2–6 wrote the whole game (26K-token first write), turn 8 first play(). This build asked
for art unprompted: 14 image jobs rendered, 2 mesh jobs enqueued. At 23:41:27 `local_gpu.py
auto` (pid 383246) stopped — "stopping, held=None", same minute a Claude monitor task was
stopped; cause not proven. Build sat on a pending llm job ~40 min; reaper failed 1 llm + 2 mesh
jobs at 1800 s. Restarted auto at 00:23 under setsid + safe; job claimed at once. Wall clock
and GPU-min for this run are tainted, steps are not.

PROBE ANSWERED at turn 15–22: first test run 18/21 (7, 13, 14 failed: float epsilon, drone
engaged state, regen-under-threat), and tests 9/11/12 PASSED — because the builder had already
bent the sim to them. `state.js` RATES: fuelDrain 10 "per second (1 per tick)", radLeak 30,
radStorm 50, coolantLeak 30 — 10× the design's rules, with a comment rationalising per-tick.
The numeric test beat the prose rule every time. Consequence for the game: fuel 80 → 0 in 8 s
once power < 95; storm pins radiation at 100 in 2 s. Design→build law from this: a test
expectation the builder can check is authoritative over the rule it tests, so SANITY must
recompute every test's numbers from the rules (not eyeball), or tests must be derived by the
builder from the rules rather than given.

DONE: 71 steps (70 turns: 51 play, 5 writes, 9 edits), 1 compaction, 15.0 llm GPU-min + 5.1
image (14 renders: floor/corridor webp, drone sprite, item icons — art asked for unprompted,
2 mesh jobs lost to the stall). Error gate 0 rounds, play gate 0 broken / 7 met, 3 unclear.
Gate impression: "O2 and PSI drop fast enough that you feel the station is genuinely dying...
degradation is aggressive enough that a first-time player might feel overwhelmed" — the bent
rates, seen from the outside. ~1,900 lines over 10 modules. VERDICT: Nick plays.
Play: http://127.0.0.1:8765/cb639a3af329/index.html

## Outcome


Vision plumbing VERIFIED at platformer `f996bfd96077` turn 15 (prompt 104K, no error): the
builder's reasoning on the first frame — "I can see issues with the screenshot: 1. The
background is a red/mauve checkerboard — that's the placeholder image... 2. The player is a
purple circle?? The placeholder for assets/player.png... 3. The HUD is showing: hearts..." It
reads the image and reasons about what is placeholder vs real. Image cost on the wire is
small (35 KB JPEG); the estimate counts it flat.

### Overnight chain, as launched ~03:05 (clock times in this log above were estimated ~1 h fast)

Four detached scripts, none depending on the Claude session:
`run_vision.sh` (platformer, island; writes vision.done) → `run_team.sh` (station + collector
team designs, revert vision.patch, restart control plane, build station, collector if before
09:00; team.done) → `run_tail.sh` (station with corrected tests; then a SECOND PASS on the
blind platformer `6e2271a9571d` via `change_from_note` with the play gate's impression as the
note, pre-change game snapshotted to `snapshots/`, result synced to :8765 as
`6e2271a9571d-pass2`; tail.done). `guard.sh` runs beside them: abandons mesh jobs, relaunches
auto / control plane, logs to `logs/guard.log`, exits on tail.done. Run ids: `builds.tsv`.

Vision platformer, first behavioural delta at turn ~8: it ordered 12 image + 6 mesh assets
(mesh abandoned by the guard, no local venv). Its blind twin `6e2271a9571d` ordered NONE.
Same design, same prompt; the only change is that this builder will see the screen.

### 2026-09-13 ~03:55 — ninfer was being RESTARTED ON EVERY play() TURN (found while answering
"does eliding the image kill the KV cache")

`local_gpu.py auto` drains a leg after 6 s of empty queue. Between build turns the control
plane runs the program — a play() takes 20–30 s — so the llm queue is empty long enough that
auto stops the llm leg. After the PC restart auto had started ninfer itself, so "stop the leg"
meant KILL ninfer: 51 `[llm-server] starting` lines since 01:00, 44 server lifetimes in the
log, every build-size request `cache=0 reuse=full_reset` (~90K re-prefilled, TTFT 14–18 s,
plus a ~5 s boot). Every build since 01:02 (platformer post-resume, collector, forest, vision
platformer) paid ~20 s per turn of pure re-prefill, and their GPU-min (exec_seconds) are
inflated by it. Before the restart ninfer was hand-started and auto merely adopted it. Fix
applied 03:55: auto killed, ninfer hand-started (same argv), guard relaunched auto, which
adopts the server. Image-elision answer, for the record: a stub changes tokens at the old
frame's position, so the tail after it re-prefills — a few thousand tokens, one round back —
while a restart re-prefills the whole window. Add to local_gpu.py's list: a leg owned by auto
should not be torn down inside one build's turn gap.

Vision platformer `f996bfd96077` first pass: done at turn 102, nudge, done again ~116. Play
gate: 3 BROKEN, 6 of 10 unmet — "Player remained completely stationary; timer stuck at 0.0s;
game was in a paused state with no visual indicator" for D, ArrowRight and Space. Fix round
running (kind=fix, build b04f735b1ffb). The blind twin `6e2271a9571d` had no such failure.
Reading: 50 turns looked at a frame and called it "exactly right", but every frame came
from a play() script driving window.__game (start(), step(), setMove) — the sighted builder
verified the screens its own API produced, never the real key→clock→render path a player
uses. A screenshot proves the render, not the input. Next-arm implication: the frame that
matters is one taken after REAL key presses (__press) with no debug calls, or the gate's own
first frames handed back before done.

CORRECTION + MEASUREMENT (ninfer request logs, regex fixed to include finish=tool_calls):
auto-owned ninfer restarted 44× over 314 build-size requests (01:02–03:50), i.e. ~1 in 7 turns,
not every turn. Reuse on those: 197 append_frontier (mean TTFT 0.2 s), 107 full_reset (mean
15.2 s at 83K), 10 restore_response_checkpoint (0.9 s). ≈27 min of re-prefill across the
night's builds. On the hand-started ninfer, the vision fix build then showed 8 CONSECUTIVE
full_resets on a smoothly growing 34–37K prompt: ninfer's cache is frontier-only (append to
the last frontier, or restore the last response checkpoint, else reset), and the image
elision rewrites the prompt behind the frontier — so after the first play turn every later
play turn re-prefilled the window. ANSWER to "does eliding the image kill the KV cache": yes,
on ninfer, fully. `vision.v2-noelide.patch` (applied ~04:05, control plane restarted, fix build
resumed): every frame stays (~300 tokens each at 1280×720 with 2×2 merge; 50 frames ≈ 15K,
cheaper than one 15 s reset). Island vision build therefore runs no-elide; platformer's first
pass was elide. Compare TTFT/reuse in the ninfer log per build.

Vision platformer `f996bfd96077` FINAL: first pass 116 steps + fix round 41 steps, 53.0 llm
GPU-min (inflated by the restart era) + 4.1 image (12 renders, 28 asset files on disk), 8 mesh
lost. Play gate 2 rounds (cap), ships with 2 BROKEN: E and the number keys do not switch guns
("HUD still showed 'Pulse Rig'"). Round-1 fix: held keys were only polled in the rAF loop, so
step-driven time never moved the player — the same rAF-only key path is the likely cause of
the gun-switch failure the second round found. Gate impression: "strong visual identity —
detailed industrial/steampunk background with copper pipes, crates, atmospheric lighting...
HUD clean... pacing brisk, can die within seconds... gun-switching controls appear
non-functional, which undermines the shooter promise."
vs blind twin `6e2271a9571d`: 143 steps, 38 GPU-min, no art, 0 broken, "extremely punishing,
projectile small and hard to see". Sighted = better-looking, ordered art unprompted, worse
real-input correctness; both "punishing". Play: http://127.0.0.1:8765/f996bfd96077/index.html
Island vision `ab1512aa3eba` started (no-elide variant).

No-elide CONFIRMED on island vision `ab1512aa3eba` (hand-started ninfer): last 25 build-size
requests = 23 append_frontier at ~100 ms TTFT, 2 full_reset (one is the compaction). Frames
kept in history cost nothing measurable in prefill; the 8-in-a-row resets of the elide
variant are gone.

Island vision `ab1512aa3eba` (no-elide) DONE: 60 steps (39 play, 24 saw a frame), 2
compactions, 20.0 llm GPU-min, NO art ordered this time, error gate 0, play gate 0 broken /
8 met, 2 unclear, no fix round. Gate: "clean, readable open-world loop... island generation
feels organic with clear biome banding... compass bearing with distance readout is a smart
navigation aid... pacing feels inviting and unhurried."
vs blind twin `90525219fb73`: 104 steps, 29.6 GPU-min, E-on-chest "unclear" twice. Sighted
island: 42% fewer steps, a third less GPU, same clean gate, no dead-input regression.
Play: http://127.0.0.1:8765/ab1512aa3eba/index.html
Vision arm verdict so far: 1 of 2 clearly better (island), 1 of 2 mixed (platformer: better
look, worse real-input correctness). The failure mode is specific — API-driven frames prove
renders, not the key path — and fixable by taking the frame after real __press input.
Team designs now running (run_team.sh).

TEAM station design done (`designs/station.team.xhigh.md`, 90K chars, 1,260 lines; parts
visual 20K / gameplay 28K / engineering 14K chars; integrator 64K completion tokens on a 21K
prompt, 411 s). 23 rows in the DECISIONS table: the designers disagreed on the dimension
itself (visual 2D top-down, gameplay 3D first-person, engineering Canvas 2D) → ruled 2D T1,
first-person T2. Integrator adopted engineering's fixed-point scheme: 1 m = 10,000 units,
resources 10,000 units/point, facing in centiradians, 10 ms tick — tests read
`setPlayer(100000,100000); setPlayerOxygen(1000000); step(0.01,1)`. Exact, builder-hostile;
a different game from the skeleton station (scrubbers/crafting/mites/hull/daily cycle, no
comms-rescue). SANITY did arithmetic (scrubber refill vs drain, windup vs cooldown, walk vs
mite speed) and FIXED four sections incl. §9. Test correctness not hand-checked (units too
dense); the build is the check. Collector team design next, then the station team build.

TEAM collector design done (`designs/collector.team.xhigh.md`, 96K chars; integrator 67K
tokens / 459 s). vision.patch reverted (0 dirty src files), control plane restarted. Station
team build `e130f6e5cfef` started on the blind builder — twin of skeleton `cb639a3af329`.

Station team build `e130f6e5cfef` in progress: hang in `start(1)` at turn 39 (corridor
carver `a === b` → step −1, loop never ends), found at turn 61 by instrumenting; all 17 tests
pass at turn 123, then a real-key gameplay pass (it learned nothing from the platformer,
this is just the design's §10 order). Test-wins-again at turn 119–120: test 10 wanted mite
damage 5000 while health is 10,000 units/point; the builder declared "enemy damage uses a
1000-unit scale" — a second unit scale invented to satisfy a number, not a rule fix. The
fixed-point scheme (engineering's, adopted by the integrator) is where that ambiguity came
from.

TEAM station build `e130f6e5cfef` DONE 05:45: 158 steps, 5 compactions, 29.0 llm GPU-min,
no art, ~2,100 lines / 12 modules ("Kestrel-9"). Error gate 0, play gate 0 broken / 6 met,
4 unclear, no fix round. All 17 spec tests pass. Gate: "calm exploration loop... top-down
layout visually clean and easy to parse... HUD dense but legible... pacing slightly slow at
Threat 1, gentle tension rather than urgency... O2 Cell consumed on a stray E-press."
vs skeleton station `cb639a3af329` (71 steps, 15 GPU-min, "dying around you", rates bent
10×): the team spec's numbers held (no 10× bend; one invented sub-scale), the game is
BALANCED-TO-SLOW instead of broken-fast, at 2.2× the steps and 2× the GPU. Different game
too (survival sandbox, no comms-rescue arc). Play: http://127.0.0.1:8765/e130f6e5cfef/index.html
Collector team build `7ef33a0a15ab` started 05:46 (before the 09:00 cut).

06:05 — station team run `e130f6e5cfef` got a SECOND play-gate pass after build.sh had
returned (first pass 05:46: 0 broken; second: E at a battery pickup consumed the O2 cell →
1 broken → fix round a33b60852ffb, running beside the collector team build). Same two-pass
shape as the vision platformer. Consequence: `build.sh`'s result line is not a run's end
state and a one-shot rsync at that moment can serve a pre-fix game. `resync.sh` (detached)
now refreshes every lab run's :8765 copy every 5 min until tail.done. MORNING: play links
are only final once no `build_state.json` under ~/output/runs/<id> says phase "build".

Station team run: fix round 2 (`8ff974c205b1`) — after the E fix the gate's next pass found W
not moving the player near a console, key 1 and P-while-paused dead (4 unmet). Real-key
path failures, same class as the sighted platformer: the builder's own play() tests drive
the API, the gate presses keys. Ships after this round (gate cap 2). 38 llm GPU-min so far
on this run vs 15 for the skeleton twin.

TEAM station run `e130f6e5cfef` FINAL 07:40: first pass 158 steps + fix 1 (E→O2 cell) + fix 2
(110 steps, W near console) = 61.6 llm GPU-min. Final play gate after round 2: 8 BROKEN — w,
a, s, d, ArrowLeft, ArrowUp, a canvas click, and w again all "Player remained completely
stationary". Fix round 2 REGRESSED movement from one-situation-dead to all-dead, and the
gate's 2-round cap shipped it. The builder's own turn-97 finding was "W is working at spawn,
near the console, with the craft menu open" — in the headless API path; the gate's real
keypresses disagree. Verdict for the team arm on station: balanced numbers, clean first
gate, then the real-input path collapsed under fix rounds. 4× the GPU of the skeleton twin.
Play (as shipped): http://127.0.0.1:8765/e130f6e5cfef/index.html

TEAM collector run `7ef33a0a15ab` FINAL 07:50: first pass ~160 steps (6 compactions, 96K
spec pinned) + error-gate fix (TypeError in ui.js renderHM, 24 steps) = 88.9 llm GPU-min.
Play gate 0 broken / 9 met, 1 unclear. Gate: "reads clearly and responds instantly to every
input... core loop — walk, harvest, sell — feels tight and satisfying... pacing unhurried...
shop interface clean, daily cap adds a subtle layer of planning." vs skeleton collector
`555cb9cb61fb` (70 steps, 18 GPU-min, also a clean calm gate): same verdict class at 5× the
GPU. Play: http://127.0.0.1:8765/7ef33a0a15ab/index.html
team.done 07:51 → tail: corrected-tests station `dba201b6c217` building, then platformer
pass 2.

Corrected-tests station `dba201b6c217` (tail, step 50, already done-nudged): `game/sim.js`
has `S.reactorFuel - 1 * dt` — the design's 1/s rule, NOT the 10/s the wrong test forced in
`cb639a3af329`. The bent sim was the wrong test and nothing else. Design-side law confirmed:
the number in a test is what the builder builds to.

Corrected-tests station `dba201b6c217` DONE 08:20: 53 steps, 2 compactions, 21.8 llm GPU-min
+ 1.0 image (2 renders), error gate 0, play gate 0 broken / 7 met, 3 unclear, no fix round.
Gate: "strong sense of urgency from the moment the hull breach hits... claustrophobic
tension... comms progress gives a clear long-term goal... pacing feels WELL-TUNED".
vs original skeleton station (same design, three test numbers wrong): "degradation aggressive
enough that a first-time player might feel overwhelmed". Three numbers in §9 were the whole
difference between overwhelmed and well-tuned. Play: http://127.0.0.1:8765/dba201b6c217/index.html
Last chain item running: platformer pass 2 on `6e2271a9571d` from the gate's impression
(started 08:21).

Platformer PASS 2 `6e2271a9571d` (kind=change, note = the gate's impression) DONE 08:25: 23
steps, +2.8 GPU-min (run total 40.8). Change: enemy spawn rolls within the first 18 tiles
re-rolled further along; nothing else. Gate after: 0 broken / 6 met, 1 unmet, 3 unclear —
"pacing feels aggressive for a first stage — the player died twice within the first few
seconds of trying to move right". The note did not move the verdict. [[grades-are-aggregate]]
measured a third time: an impression fed back as a change note buys a local edit, not
balance. Both versions served: :8765/6e2271a9571d-pass1 (blind original, from
snapshots/) and :8765/6e2271a9571d-pass2.

## State at 08:30, 2026-09-13 — everything below is playable on http://127.0.0.1:8765/<id>/index.html

| ask | arm | run | steps | llm GPU-min | gate | one line |
|---|---|---|---|---|---|---|
| island | skeleton | 90525219fb73 | 104 | 29.6 | clean, E-chest unclear | Nick: minor flaws, quite good |
| island | skeleton + vision (no-elide) | ab1512aa3eba | 60 | 20.0 | clean | inviting, unhurried; 42% fewer steps |
| station | skeleton (3 wrong tests) | cb639a3af329 | 71 | 15.0* | clean | rates bent 10×, "overwhelmed" |
| station | skeleton, tests corrected | dba201b6c217 | 53 | 21.8 | clean | "well-tuned" — 3 numbers were the difference |
| station | team (3 designers + integrator) | e130f6e5cfef | 158+fix+110 | 61.6 | 8 BROKEN after 2 fix rounds | balanced numbers, movement dead on real keys |
| platformer | skeleton | 6e2271a9571d-pass1 | 143 | 38.0 | clean | "extremely punishing", small projectile |
| platformer | skeleton, pass 2 from gate note | 6e2271a9571d-pass2 | +23 | +2.8 | 1 unmet | still aggressive; note bought a spawn re-roll |
| platformer | skeleton + vision (elide) | f996bfd96077 | 116+41 | 53.0* | 2 BROKEN | ordered art, better look, gun-switch dead |
| collector | skeleton | 555cb9cb61fb | 70 | 18.0* | clean | calm, only clean impression of the first five |
| collector | team | 7ef33a0a15ab | ~160+24 | 88.9 | clean | "tight and satisfying"; 5× the GPU |
| forest | skeleton | 1eea746f3617 | 48 | 14.9* | clean | moody, pacing right |
(* inflated: auto-owned ninfer restarts, see 03:55 entry)

Findings the night bought, each with its evidence above: (1) a wrong number in a test beats
the rule it tests — the designer's SANITY must derive test values from rules; (2) vision in
the loop helps when frames come from real play (island) and misleads when they come from
API-driven state (platformer, team station) — take the frame after __press; (3) fix rounds
driven by the gate's real keys keep finding rAF-only key polling the builder's API tests never
exercise — that is the verification gap, not the spec; (4) team design = better numbers,
2–5× the GPU, and its integrator adopts whatever unit scheme engineering proposes; (5) image
elision kills ninfer's frontier-only KV cache; keep frames; (6) local_gpu.py: hand-start
ninfer before auto, mesh leg needs its venv. src tree is clean; vision.v2-noelide.patch is
the version to re-apply.

## Nick's play verdicts, 2026-09-13 morning

- platformer pass 2 (`6e2271a9571d-pass2`): "basically the best version. No art requested,
  still amazing art." (the gate's impression note bought more than the gate itself saw)
- collector, team design (`7ef33a0a15ab`): "definitely a winner"
- station: team (`e130f6e5cfef`) > tests-corrected (`dba201b6c217`) > uncorrected
  (`cb639a3af329`) — even with the team build's real-key movement failures
- vision: "gave the model some amount of clarity on fixing visual glitches which made the
  experience better"
- "overall, this leg has shown us what I want to start working on"
Control: none run, by ruling — each leg was the control for the next (skeleton → corrected →
team; blind twin → sighted twin), and the local 27B is not prod, so a local control controls
nothing. The next control is prod itself: the same designs and builds on Flash-Next via the
tunnel.

## Prod leg (Flash-Next on RunPod pods, driven from this box) — 2026-09-13 morning

Nick: go, one-shot AND team, both on prod. Ask: platformer. Path: Tailscale Funnel exposes
the local control plane (`sudo tailscale funnel --bg 8000`, Nick runs it) → `prod_settings.py
<url>` writes prod's runpod queue block (max_workers 1 per queue), `llm` = pennyroyal /
131072 / medium / 2 slots, cp_url = funnel, job timeout 2400 s → local_gpu auto stopped →
control plane restarted (autoscaler starts) → `run_prod.sh`: `design_queue.py skel` (the
skeleton prompt as a queue job at xhigh, served by the pod) → build.sh → `design_queue.py
team` (3 designers + integrator, serial queue jobs) → build.sh; `guard_prod.sh` relaunches the
control plane and logs queue/pod state. Backup of local settings: `settings.local.backup.json`.
Cost bound: one Pro 6000 (~$2.19/h) + one 5090 for art, idle-exit 90/30 s.

11:05–11:13: first prod pod. Funnel up, settings applied, design job queued 11:05:26; the
scaler's first 24 creates were refused (Pro 6000 stock-out, both DCs, both editions), then
one landed: `akaqp7p1ex9h7j`, WK edition, EU-RO-1, $2.19/h, image llm-v20, created 11:04:57,
claimed the design at ~11:08 (rent→claim ~3 min). Last heartbeat 11:10:08, then the pod
vanished from RunPod's list — no complete, no deregister, no scaler reap — and the job's
lease lapsed back to pending. Request shape was reasoning xhigh + max_tokens 100000 on a
2-slot 131K pod, which prod has never served (prod: medium, 50K). Retry at medium/50000.

ROOT CAUSE of both pod deaths (Nick's call: "was it reaped by prod?"): YES. Prod's autoscaler
runs against the SAME RunPod account and reaps any pod named `maestro-<queue>-*` that no worker
registered with PROD's control plane within boot_deadline_seconds (300). Pod 1 created
11:04:57, gone ~11:10:00; pod 2 created 11:22:52, gone ~11:27:52 — 300 s each, to the second.
The request shape was innocent. Fix on this box (`labpods.patch`, uncommitted): the local
scaler names and manages `lab-<queue>-*` pods. Belongs in local_dev.md: a second control
plane on the shared account must use its own pod-name prefix, or prod eats its pods at 5 min.

11:43 — first pod that lived (`lab-llm-b011a6ea`, x6lwusrtls6hwb) returned the skeleton design
job in 88 s (13K completion tokens at medium) but my queue designer read it back EMPTY: the
control plane elides a job's stored result to usage+finish once its completion handler has
consumed it. Rewritten as `design_prod.py`: the prod design path itself (`design.enqueue` with
the prompt file swapped, the handler lands the text as the run's prompt and auto-starts the
build); intermediate team documents get their auto-build stopped on landing, the integrator's
run builds. `run_prod.sh` v2 waits on each run's cursor. One wasted gameplay-designer job and
one empty-prompt build attempt (refused at set_prompt, no cost) along the way.

11:47 — FIRST PROD-PATH DESIGN ON FLASH-NEXT: skeleton prompt at prod's medium, 38K chars,
complete through A. SANITY, landed in 78 s (the 27B took 4–6 min at xhigh for the same size).
Run `795034905b8f` auto-built from it; step 20 at 11:53 (~20 s/turn on the pod). Pod
`lab-llm-b011a6ea` past the 5-min mark (uptime 828 s, GPU 100%): the prefix fix holds.

PROD ONE-SHOT platformer `795034905b8f` DONE 12:10: Flash-Next on `lab-llm-b011a6ea`, design
78 s + build 92 steps / 23 min, 2 compactions, 16.1 GPU-min = $0.59 billed at $2.19/h. No art
ordered. Error gate 0, play gate 0 broken / 4 met, 6 unclear, no fix round. ~1,100 lines
(62K total incl. vendored). Gate: "competent, legible side-scroller: HUD clean, dark
industrial palette with cyan player and orange scrap... locked-weapon message a nice touch of
clarity... pacing a touch static, shooting/jumping didn't produce punchy feedback (may be
capture timing)". vs local 27B skeleton platformer (143 steps, 38 GPU-min, "extremely
punishing"): prod = 3× fewer steps, gate calmer, no dead inputs. Play:
http://127.0.0.1:8765/795034905b8f/index.html. Team designers started 12:11 (visual run
0bd7df510a01).

PROD TEAM design, platformer: visual 24K/60 s, gameplay 22K/48 s, engineering (~1 min),
integrator 64K chars in 138 s (35 decision rows; all four calls ≈ 5 min total on Flash-Next
vs ~20 min on the 27B). Intermediate auto-builds stopped cleanly. Team build running on run
`7347d2dd2972`.

12:18 — the prod integrator's spec (run 7347d2dd2972) was TRUNCATED: 64K chars ending mid-
table in §10 BUILD ORDER, no §11, no SANITY; finish_reason=stop at 27,267 completion tokens
(4.5K reasoning), prompt 24K — the model ended on its own, the same early-EOS the 27B showed
at medium. Build stopped at step 3. Integrator re-run once from the three saved documents
(`design_prod.py integrate`, run_prod_team2.sh); its run builds. Rule for the design stage,
now seen on both models: a design missing its last heading is rejected and retried once.

Integrator retry (run `9cd536de2ac9`): 58K chars in 126 s, stopped at the SAME place — the
last milestone row of §10 BUILD ORDER. Completion 24,230 vs 27,267 tokens (prompt 24,113
both), finish=stop both: not a cap. Flash-Next at medium ends the document after the
milestone table and never writes §11 DEFINITION OF DONE or A. SANITY (the 27B at xhigh did).
Prompt climb for the integrate prompt, later: a termination anchor after A (or the two
closing sections before the table). The three designer docs and the one-shot design all
ended cleanly (7–13K tokens). Team build proceeds on the retry design with §9 present and
§11/A absent — the prod team result, with that caveat.

PROD TEAM platformer `9cd536de2ac9` DONE 12:50: CAPPED at 200 steps (5 compactions, 69 play
turns, 70 write turns, 9 edits — a rewrite-heavy build), ok=False, no gates ran (a capped
build is finalized on playability only), 26.4 llm GPU-min + art = $1.07. Ordered art: 13
images + 16 meshes from prod's 5090 pods (29 assets). ~1,100 lines. The design it built from
lacked §11/A (integrator early-stop). vs prod one-shot `795034905b8f` (92 steps, $0.59,
clean gates): on Flash-Next the team spec bought 2× the steps and a cap-out, no gate.
Play (as capped): http://127.0.0.1:8765/9cd536de2ac9/index.html
PROD LEG TOTAL: $1.94 billed (two reaped pods, one-shot, team, art pods). Funnel URL stays
public until `sudo tailscale funnel off` (Nick).
Wind-down 12:52: settings.local.backup.json restored, control plane restarted (autoscaler
off), ninfer hand-started on :8090, local_gpu auto relaunched. Uncommitted src edits:
`labpods.patch` (lab-<queue> pod prefix) — keep or revert is Nick's call; docs/local_dev.md
has the new section.

### Prod leg 2, parallel + section gate (2026-09-13 afternoon)

Nick: run the designers in parallel on the pod, and gate the integrated spec on "has every
major section" (subsections may be skipped). `design_prod.py both`: all four designer jobs
(visual, gameplay, engineering, skel) enqueued at once; skel builds on landing; integrator
output must carry headings 0–11 + A at any depth or its run is abandoned and the integrator
re-run (3 tries). `run_prod_par.sh` awaits both builds concurrently. Retro-test of the gate
on yesterday's specs: skel passes, both integrator outputs fail on exactly ['11','A'].

First Pro 6000 create refused (stock-out) but a pod landed on retry. All four designs in
456 s wall: gameplay 279 s, visual 285 s, engineering 390 s, skel 456 s (2 slots). Skel
39887 chars, all 13 sections, building as 2ef94c3088a6.

Integrator: try 1 4d8ba3f01c97 — 56889 chars, cut mid-§9 tests, gate FAIL ['10','11','A'];
try 2 ce520a01efd3 — 56912 chars, same cut, FAIL. Usage: 22962 (3137 reasoning) and 26191
(5947 reasoning) completion tokens, finish `stop`, cap 100000. Yesterday's 9cd536de2ac9 was
24230 (3525 reasoning). All three ≈ 20K non-reasoning output tokens — the model ends the
response there regardless of what section it is in. Not a ceiling we set. Lever: either a
termination anchor (unlikely to move a budget-shaped stop) or split integration into two
calls (§0–8, then §9–A fed the first half) so each stays under ~20K.
Try 3 d3fb389cd4c0: 60024 chars, same FAIL. Split integrator (§0–8 then §9–A, prompts
team_integrate_p1/p2.txt): part 1 stopped mid-§5 at 50622 chars / 22222 tokens — the stop is
a per-response output budget (~20K non-reasoning tokens), independent of the section list.
Part 2 abandoned. **Continuation loop** (team_integrate_cont.txt: spec_so_far + "continue from
the exact point it ends through §A", `design_prod.py cont`): one continuation, 35573 chars in
147 s, resumed mid-table in §5 with no repeat, wrote §6–A; gate PASS at 86197 chars. So the
full team spec is ~30K output tokens and needs two calls on Flash-Next. Team build
fe1ea16cd148 via build.sh on the pod, in parallel with skel 2ef94c3088a6.
**Skel prod build 2ef94c3088a6 DONE**: ok, 109 steps, 51 min, "IRONFALL", 3D (three.js,
16 meshes + 26 images landed from the art pods), gates clean, live first-30-s audit passed.
Cost: llm $1.46 (125 jobs, ~62K context at the end) + image $0.09 + mesh $0.02 = **$1.57**.
Play: http://127.0.0.1:8765/2ef94c3088a6/index.html
**Team prod build fe1ea16cd148 CAPPED at 200** (64 min): 23 files, 15 images + 16 meshes,
4 compactions, 29 play() calls; from turn ~100 it was running the spec's §9 tests via play()
and fixing failures, last turns chasing state lost across play() page loads. No gate rounds
reached (no done call). Cost llm $1.99 + art $0.11 = **$2.10**. Play as capped:
http://127.0.0.1:8765/fe1ea16cd148/index.html

Parallel vs serial (on-pod wall, pod claimed 14:31:23): paired design calls ran 2.2–2.6×
slower each (visual 131 s vs 60, gameplay 124 vs 48, engineering 112 vs 51, skel 170 vs
78); four designs 301 s parallel vs 237 s serial; integrator 279–324 s while sharing with
skel build turns vs 138 s solo. Cold 25K prefills are compute-bound; two slots lose. Nick is
queueing a separate agent on the concurrency question (replay 4 recorded builds against one
pod, sweep --max-mamba-cache-size, TTFT vs prompt tokens).

Leg total spend 14:25→16:05: **$6.62** (two builds $3.67; three failed integrators, split
p1, abandoned p2 and continuation ≈ $2.9). Wind-down 16:06: settings restored, control plane
restarted (autoscaler off), ninfer + local_gpu auto up, guards stopped. Leftover pod
lab-llm-735aa889 was still RUNNING with no autoscaler to reap it — terminated by API, worker
row marked. Wind-down rule: terminate lab pods BEFORE turning the autoscaler off.
Nick: team build rendered at 300×150, unjudgeable. Cause: index.html's CSS never sizes
`canvas#game`; lib/canvas.js takes the backing size from clientWidth (its header says "sized
by your CSS"), so the default 300×150 stuck. Spec said 960×540 scaled to window; the builder
called createCanvas right and dropped the CSS line. Never reached the play gate (capped) where
a screenshot shows it. Patched `width:100vw;height:100vh` on the runtime/games copy only for
judging. Lib lever: clientWidth of an unstyled canvas is 300, so the `|| innerWidth` fallback
never fires — fall back when the canvas has no CSS size, not only when it is 0.

### Gameplay prompt rewrite (Nick), 2026-09-13 evening, local 27B xhigh

Nick rewrote the gameplay designer prompt from the ground up (`variants/team_gameplay_p2.txt`,
1.4K chars: responsibilities owned / not owned, "add your logic for why", "on the fence → cut",
complete end to end; no headings, no given-numbers / generator / rule-shape laws — those
findings came from one-shot prompts feeding the builder directly, untested with an integrator
in between). Team order becomes sequential: gameplay first, fed into visual and engineering
(today's integrator ruled on 25 disagreements, nearly all identity/convention). Five asks with
the new prompt, then the old prompt on the three asks that lacked a local xhigh doc.

| ask | new (p2) | old |
|---|---|---|
| collector | designs/collector.team_gameplay_p2.xhigh.md 51918 ch / 355 s | designs/team/collector.gameplay.md (earlier run) |
| island | designs/island.team_gameplay_p2.xhigh.md 29040 / 279 s | designs/island.team_gameplay.xhigh.md 28130 / 315 s |
| station | designs/station.team_gameplay_p2.xhigh.md 38398 / 351 s | designs/team/station.gameplay.md (earlier run) |
| forest | designs/forest.team_gameplay_p2.xhigh.md 39072 / 348 s | designs/forest.team_gameplay.xhigh.md 18476 / 205 s |
| platformer | designs/platformer.team_gameplay_p2.xhigh.md 48500 / 290 s | designs/platformer.team_gameplay.xhigh.md 41869 / 288 s |

Nick judges by reading. Next: his visual + engineering rewrites, then sequential team on local.

### Visual + engineering rewrites (Nick), 2026-09-13 night, local 27B xhigh

Visual p2 on station without gameplay.md vs with (`variants/team_visual_p2_gp.txt` adds the
request and gameplay.md in tags): with won outright (all ten rooms designed vs generic
zones), so the other four ran with. Dimensionality stays visual's call on purpose (does it
ever argue 3D?); it deferred to gameplay on every ask, no 3D argument yet.

Engineering p2 (`variants/team_engineering_p2_gv.txt` = Nick's prompt + request, gameplay.md,
visual.md) first ran without "built in HTML CSS and JS": TypeScript ×2, React ×1, npm ×3 —
parked in `designs/bad_no_plainjs/`. With the line, 5/5 plain JS.

| ask | gameplay | visual | engineering | eng out tokens | eng test harness |
|---|---:|---:|---:|---:|---|
| collector | 52013 ch | 61055 | 81432 | 65K | npm + Playwright e2e |
| island | 29169 | 49039 | 65067 | 44K | `node --test`, "without a browser" |
| station | 38456 | 54146 | 83299 | 65K | `node --test`, "no browser required" |
| forest | 39126 | 47917 | 58683 | 58K | Vitest + npm |
| platformer | 48575 | 53667 | 72507 | 55K | `node --test` |

Files: `designs/<slug>.team_visual_p2_gp.<slug>.xhigh.md`,
`designs/<slug>.team_engineering_p2_gv.<slug>.xhigh.md`.

Platformer engineering.md read end to end against its gameplay.md. Coherent architecture,
would not build a working game as written:

1. **Nobody wrote the levels.** gameplay.md gives each stage as prose ranges ("30 to 42: low
   ceiling passage requiring crouch", "Core 3: high ledge above gap"). engineering.md defines
   a tile-string format, shows one example, and says production stages are data, "the
   gameplay designer has already designed the 10 stages". Ten 75–120 × 12–24 tilemaps plus
   validationRoute waypoints per stage fall to the builder; no document owns them. The old
   "generator" law covered this hole; the hole is real even with the law gone.
2. **Harness cannot run.** Node test runner, headless game, input proxy, completion bot, ~30
   test files; the builder has no node tool and no npm. Definition of Done 24–26 = all tests
   pass, unreachable. 5/5 docs put tests in Node; "HTML CSS and JS" fixed the stack, not the
   harness. Lever: one prompt line, tests run in the browser through a `window.__game` debug
   API driven by play().
3. **Validator + route bot = new failure surface.** Every hand-authored stage must pass a
   structural validator (spawn clearance, conduit 64×96 clear, exact enemy counts, no
   overlaps) and a route bot; the doc's own example stage fails it (width 75, rows 48 and 52
   chars). The builder fights the validator instead of the game.

Good: all 13 movement numbers, invuln, hearts, lives match gameplay.md exactly; fixed
timestep, state machine, save schema, platform carry, low-clearance rectangles for crouch —
buildable, no contradictions. Cuts list sane. With levels owned and tests in-browser it
builds. Other four docs unread at this depth.

Next: integrator (current `variants/team_integrate.txt`, still the records/generator-era
prompt) on all five p2 triples, local xhigh, section gate + continuation.

### Integrator on the p2 triples + how the builder reads a big spec, 2026-09-14 night, local 27B

Integrator (`variants/team_integrate.txt`, old prompt) on all five p2 triples, xhigh, section
gate + continuation (`run_integrate_5.sh`): 5/5 complete in one call, 0 continuations.
collector 94K chars / 65K out tokens, island 81K / 65K, station 132K / 80K (130K of the 131K
window), forest 101K / 48K, platformer 117K / 54K. Files `designs/<slug>.team_integrate_p2.xhigh.md`.
Read collector + island end to end: rulings tables and §A proofs are the best text this lab has
produced (collector §A proves the coin economy closes with margin 20; catches its own team's
furniture-count arithmetic error). Bad: §9 tests in Node 5/5 (builder has no node — the python
tool is seccomp'd: no execve/fork/socket), collector gates `window.__game` behind `?test=1`
(play() loads the bare page; one turn to notice), island §4.1 is a ten-stage level compiler with
a `createFallbackLevel` escape hatch, and the integrator ruled "all assets generated in code"
on a false premise (Nick: fine, art is our weak point anyway).

The spec had always ridden the prompt as `history[0]`, never compacted (25–33K tokens
resident). Nick: put it on disk, let the builder discover it. Seven collector runs, all cut
before turn 20 except the last, watching only how the model reads (`build_file.sh`,
`build_layered.sh`, `build_split.sh`; run ids in `builds.tsv`):

| arm | prompt | spec on disk | what it read before writing |
|---|---|---|---|
| 8d088536f1d5 | build.txt, two-line user msg | design.md | whole file, 6K-token slices, 6 turns |
| b6025fe5afbd | + "well structured … sections … build order" | design.md | whole file, `t.find(last words)` to resume |
| bc27feca816b | layered build prompt (`variants/build_layered.txt`: How you act / Environment / Rules; tool docs moved to `docs/*.md`) | design.md | whole file |
| dd182914e7de | layered + model-written reading map as §0.4 | design.md | whole file incl. the "never a gate" row |
| 5cc65b61f9b7 | layered + reading map as §0.0 (line 9) | design.md | printed a heading index first, then whole file; first code turn 7 |
| c6b51ec35d89 | layered, `design/` one file per section | 13 files | every file by name (09-tests only 3K of 14K); first code turn 7 |

Interrogation of bc27 (transcript replayed to ninfer, `interrogate_bc27*.json`): first it
defended reading lib files and claimed design.md was "targeted"; pointed at the turn numbers
it said "cross-reference anxiety" (§ back-links), "optimizing for the wrong risk", and
"reading felt like progress"; asked what prompt would have helped it proposed the reading map
(§0.4) + a §9-is-not-a-spec line + a 15 KB/turn tripwire. The map, placed as it asked, did not
stop the read. Layered prompt did land its other claims: zero Node/npm attempts across all runs,
tests only through play(), `window.__game` error fixed in one turn.

c6b51ec35d89 run to the end: **capped 200**, 10 files 140K chars, renders (title, HUD, minimap,
zone labels, lake shallow/deep, canvas fills the window — the lib fix), walks. Play:
http://127.0.0.1:8765/c6b51ec35d89/index.html. Shape: turns 7–25 wrote every file; 27–78 play-
driven probes in spec order (node counts exact, goals chain to Curator's Seal); compactions at
43/83/144/186; after 83 it re-read `design/` 39 times (turns 96–199) and made 56 edits / 45
plays / 3 writes — polishing and re-verifying, never called done. Post-compaction floor ≈ 60K
tokens = the newest body of every game file (`_COMPACT_KEEP = 0.33`, "the transcript IS the
memory"), not the spec.

Overnight (`run_overnight.sh`): collector with `§` back-links stripped (`designs/collector_nolinks/`,
112 refs removed by a subagent) + a why-comment line in the prompt (`build_layered_split_why.txt`),
then island/station/forest/platformer as split `design/` under the layered prompt.

870925d80b62 (collector, `§` links stripped + why-comment line): read pattern unchanged — every
`design/` file by name in turns 2–6, except it skipped 09-tests and A-sanity outright; why-comments
2/190 programs (line ignored). Build: 32 writes into a `src/{config,content,core,systems,ui}` ES-
module tree, 104 plays, 17 design re-reads total (vs 45), **called done at turn 191**; the done
nudge sent it re-reading for 9 turns and it capped at 200 before a second done. 37 min wall.
Renders: title card, three shopkeepers with canopies, goal tracker, inventory bar, tool pips,
minimap. Play: http://127.0.0.1:8765/870925d80b62/index.html. Neither lever moved the read; the
back-links were not what drove it.

5e1cf145860b (island, split `design/`, layered prompt): **done, gate passed, 174 steps, 49 min** —
first team build to finish under the cap. Same whole read (turns 2–6, 58K prompt at the first
write on turn 8); 145 writes, 70 edits, 92 plays, 236 reads, 5 compactions, 16 design re-reads,
done called at 165 and again at 172 after the nudge. Renders: isometric sand/shallows tile grid,
player, shipwreck, coins, objective line, K1–K5 key slots, TIDE LOW + stamina bar, hold-M hoard
map overlay. Play: http://127.0.0.1:8765/5e1cf145860b/index.html.

6cf005797a5a (station, split `design/`, layered prompt): **done, gate passed, 145 steps, 36 min.**
36 writes into `src/{core,data,presentation,simulation,state}`, 28 edits, 74 plays, 139 reads,
4 compactions, one done at 143 (no nudge loop). Play: http://127.0.0.1:8765/6cf005797a5a/index.html.

90792e94d3c4 (forest, split `design/`, layered prompt): **capped 200, 83 min, broken** — the page
never finishes loading (goto times out; a synchronous loop on load). Shape: 14 turns hit the 30K
output cap (turns 14–56). Turn 14 was the map program typed as `<tool_call>` text and cut; the
rest are thinking-only runaways — 56K, 65K, 25K chars of reasoning about A* route lengths through
the forest spec's hand-authored 120×80 map, zero content, no tool call — discarded and the same
prompt resent in place (turns 20/21/22 identical at 92,111 prompt tokens, all discarded; 23 then
produced a 5.6K-char program in 889 tokens; a replay of that position with the full window
answered in 6K). Note for reading `turns.jsonl`: a turn's `added` is the transcript slice that
PRECEDED its request, so a per-turn table's program column belongs to the turn before. Sampling variance at
a position that asks for tile arithmetic, exactly the shape f430496 measured. `assets/map.json`
written 6 times, `src/app.js` 28 (later turns: import-test stubs chasing the load hang), 12
compactions, 44 plays, 10 edits, no done. The levels-unowned + validator trap predicted for
platformer landed on forest first. Play (hangs): http://127.0.0.1:8765/90792e94d3c4/index.html.

82592d612763 (platformer, split `design/`, layered prompt): **capped 200, 35 min, playable.** Read
every `design/` file turns 2–10 (26 design reads total), first write turn 12, 14 files in `js/`
(150K chars) incl. `stages.js` with the ten stages authored as data (16.7K chars — it wrote the
tilemaps the spec left unowned, no 30K-cap turns), 106 plays, 69 edits, 4 compactions, no done:
the last 60 turns were probes of enemy kills / boss shards, still working the §9 list when the cap
hit. Renders: title, intro cards, Signal Map (W1 unlocked, W2 "RESTORE W1 SIGNAL"), stage W1·N1
FIRST CURRENT with hearts, 4 weapon slots, cores 0/3·0/30, crosshair aim, spikes, mites, core
pickup on a one-way platform. Play: http://127.0.0.1:8765/82592d612763/index.html.

#### Overnight tally, layered prompt + split `design/`, local 27B, 200-step cap

| ask | run | result | steps | wall | note |
|---|---|---|---:|---:|---|
| collector | c6b51ec35d89 | capped, playable | 200 | ~75 min | done never called; 39 design re-reads after compaction 83 |
| collector (no-links, why) | 870925d80b62 | capped, playable | 200 | 37 min | done at 191, nudge re-read loop ate the rest |
| island | 5e1cf145860b | **done** | 174 | 49 min | gate passed |
| station | 6cf005797a5a | **done** | 145 | 36 min | gate passed |
| forest | 90792e94d3c4 | capped, broken | 200 | 83 min | hand-authored map + validator blew the 30K output cap 14× |
| platformer | 82592d612763 | capped, playable | 200 | 35 min | authored the ten stages; capped mid-§9 |

Across all six: zero Node/npm attempts, tests only via play(), `window.__game` learned in one
turn. The whole-read of the spec never changed (six prompt/spec shapes); the builds that finished
are the ones whose spec had no content the builder had to author by hand. Two levers left standing:
the done nudge (both collector runs were within reach of done and lost it to a re-read loop) and
level ownership in the design (forest/platformer).

#### Nick's verdicts, 2026-09-14 morning (played all six)

"I am legitimately blown away with the quality of all of these." Per game:
- **island** — "cool as fuck": stylized isometric view, really good bones. Map huge and barren
  (size becomes an issue because it's empty), hoard map not useful, some tile weirdness. Not a
  good game yet; the kind that could be taken and improved into something cool.
- **station** — by far the best station iteration yet. UX clean but not obvious: unclear what
  to do / where to go; icons basic and not very helpful; died to a drone with no idea how to
  fight it.
- **collector (split)** — probably the cleanest collector we've gotten, by far; "what I wanted,
  actually turned into a game". Shop/selling doesn't work, house full of doors, map bland, no
  music.
- **collector (no-links)** — marginally better; same issues; selling broken; house with no
  doors; music present.
- **platformer** — "legitimately good", the game is there; issues that could be spelled out.
- **forest** — broken (1 of 6).

Threads across his notes: bones and systems land, content is thin (barren island, bland map,
unclear objective), and the same feature broke in both collector builds (selling) off the same
spec — look at the spec's shop rules before the builder.

#### Verdict against the previous approach (Nick, 2026-09-14)

Played the earlier local prod-path builds of the same prompts side by side: collector one-shot
`c96d49915eb8` "absolutely awful", `b597d18805a2` (curio gallery) more interesting but awkward and
unexplained — "I'd pick the team's output every time"; platformers `795034905b8f` (Flash-Next
one-shot) good with minor issues, `2ef94c3088a6` (Flash-Next skeleton) worse but good; island-ish
`b10d6350808a` / `90a89ba593ee` both awful. **Clear winner: gameplay → visual → engineering →
integrator, spec on disk as `design/` per section, layered build prompt.** Next: integrate.

### Prove-it runs through the integrated chain (branch `design-team`), 2026-09-14 afternoon

`python -m maestro.codegen.run --new "Survive on a derelict space station."` then `--build`,
the real path (design.py chain → design.md → seeded design/design.md → build.txt), local 27B.

- **1bb83927306e, medium (box setting):** design 5 calls / ~10 min (one continuation), spec 120K
  chars, Node harness 0 (engineering prompt line held: tests on `window.__game`, `test.html`).
  Build killed at turn 13: the control plane was still the pre-branch process and wrote
  `done_nudged` into build_state.json, which the new BuildCursor refuses — the deploy note,
  reproduced. All 224 local build_state.json files stripped.
- **17c92bff6bda, xhigh (design AND build):** design 4 calls 472/343/525/426 s = 29.5 min, no
  continuation, 57K-token integrator reply. Build **capped 200, 77 min**: whole spec read by turn
  12, libs in full, first write at turn 33 (last night's medium builds: turn 7–12), 15 turns
  thrown away at the 30K output cap (thinking), 5 compactions, 94 reads / 75 plays / 57 edits / 8
  writes, no "Tier completed" print, no done. It wrote `tests.js` (42 tests on `window.__game`)
  and `tests.html`, and never ran them: play() loads index.html only, so the designed runner page
  is unreachable — the tests-in-files lab has to make the runner importable from the game page.
  Renders well: full station map with sectors, O2/HP, "REPAIR SYSTEMS 0/6", sector status panel,
  inventory, interact prompt. Play: http://127.0.0.1:8765/17c92bff6bda/index.html.

Correction to last night's record: those builds ran at **medium** (the box's `llm.reasoning`;
only `design.sh` sent xhigh). So the configuration Nick judged was design xhigh + build medium;
this is the first build at xhigh and it doubled the wall and lost the done. One setting drives
both stages today; a per-stage reasoning (design xhigh, build medium) is a settings key + one
argument in design.py.
