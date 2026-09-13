# Design arms — patterns from ASHWORTH ST

Source: `design.md` here (274 KB, Fable 5.1; one Qwen3.8 27B built it in ~12 h, 11M tokens read,
3.2M written). Target: a design stage + builder on Flash-Next that makes games of that class,
even at 6 h / ~$10 a game.

Control for every arm: current `src/maestro/codegen/prompts/design.txt`, same asks, same seeds,
same builder. Nick judges by playing. Battery: the usual asks plus two 3D ones (one indoor, one
outdoor), since arms A and C are 3D-heavy.

---------------------------------------------------------------------------------------------------

## Arm A — coverage, decisions, conventions (design-only, small)

Three insertions into design.txt. Everything else unchanged.

A1, after the first line ("Build this …"):

> Then one line per thing the user asked for, in their words: "ASKED: <their words> → <the
> systems and records below that deliver it>". Nothing the user asked for is left without a line,
> and no line points at a system the design does not have.

A2, before CORE LOOP:

> Then a paragraph "DECISIONS:" — every choice the request left open that the builder would
> otherwise have to make, each as the choice and one clause saying why ("the camera is third
> person, because the player must see the character's gear"). These are final.

A3, 3D only, directly after the 2D/3D decision:

> A 3D design then states its conventions in one paragraph "CONVENTIONS:": units (metres), which
> axis is up, where the origin is, which way the player faces at yaw 0 and which way yaw turns,
> the camera (first or third person, its height and distance), and the ground height rule.

Why each: A1 is the starvation law made checkable (ASHWORTH §0.1). A2 stops mid-build
re-deciding (§0.3, "do not re-litigate"). A3 is where 3D breaks silently — mirrored controls,
a camera facing backwards, two coordinate systems (§1.1).

## Arm B — code-drawn art as recipes (design-only, bigger bet)

Replace the ART paragraph's "Everything else … is drawn in code." with:

> Everything drawn in code gets a RECIPE, one line per thing: its shapes, sizes in the game's
> units, colours as hex, and counts ("a bush is 5 overlapping spheres, radius 0.3–0.5 m,
> #3f7a35 to #5c9a44, with 8 berries of radius 0.05 m, #c0283a"). A 3D object is built from
> geometry this way unless it is AI art.

Why: ASHWORTH ships zero asset files — every surface is a canvas recipe with hex, sizes and
counts (§3.1), and the enemies are a 21-bone procedural rig (§5.1). Art written as code cannot
fail to land, which is exactly today's failure (c9b2521e2828: world never came, sprites on a
plane).

## Fix candidate C — the designer cannot ask for a mesh

The ART paragraph offers sprite/tile/scene/anim. `generate_media` also has `mesh`. A 3D design
has no way to say "ask for X as a mesh", so c9b2521e2828 asked for 12 furniture pieces and
every building as billboards. Candidate line, inside ART:

> In a 3D game, a thing the player walks around or sees from more than one side is a mesh
> ("ask for the table as a mesh").

It is an omission rather than a new rule, but it is still a prompt line: measure it (3D asks,
with and without) before it ships.

## The ceiling levers (not prompt lines)

- Step cap. 200 steps is a ~1 h build. ASHWORTH was 12 h. An uncapped (or 1,000-step) arm on
  ONE ask is the only way to learn whether Flash-Next keeps improving past 200 or starts
  inventing work.
- Design as a file. A 267 KB design is ~67K tokens pinned in every turn (history[0], never
  compacted). As DESIGN.md on disk it is read by section through the program, survives
  compaction, and has no size ceiling. Needed before a frontier-sized design can be fed at all.
- Transplant. Build `design.md` itself (or a Fable design of one of our asks) on Flash-Next
  through our harness — needs the design-as-file change first. Separates "design is the
  ceiling" from "compute is the ceiling".

## Order

1. Arm A + C together vs control (cheap, design-only, 3D-heavy battery).
2. Arm B vs the winner of 1.
3. Design-as-file, then the transplant of a Fable design at the long step cap.

---------------------------------------------------------------------------------------------------

## Arm D — DEBUG API + DONE (design-only) — RUN 2026-09-12, designer only, local 27B

`variants/dod.txt` = ctrl + two paragraphs (DEBUG API: window.__game with start/step/setTime/seed/
getState + one reach-in function per system; DONE: one line per user phrase, checks under it,
script-decidable ones against the API with numbers). `run_designs.sh` straight at ninfer :8090,
no build. Designs in `designs/<slug>.dod.md`.

| ask | secs | completion tokens | DEBUG API | DONE |
|---|---|---|---|---|
| collector | 48 | 7.4K | full field list, spawnNode/spawnFish/setMoney/placeItem/skipToMilestone | per phrase, numbers; only 1 of 7 checks against the API, rest "presses E" |
| island | 235 | 35K | namespaced per system incl. movement.setInput, combat.attack | every check script-decidable with numbers + one human line |
| station | 51 | 8.3K | spawnDrone/setRoom/giveItem/setPower/wakeAI/triggerFlood | "Check:" per phrase, mostly API; determinism check; keypress checks go vague |
| forest | 32 | 5.3K | spawnWraith/setFear/setBattery/teleportPlayer/setKeyCollected | per phrase, mixed API + visual |

4/4 both paragraphs present, shape held, no filler. One gap: 3 of 4 APIs have no INPUT
injection (move direction, action keys), so checks needing a keypress fall back to prose.
Candidate clause for round 2, inside DEBUG API: "and the player's inputs as functions — a move
direction that persists until changed, and one call per action key".
Not yet measured: whether a builder ticks the DONE lines (needs build arm + nudge change).

## Arm E — full ASHWORTH skeleton, one call (`variants/skel.txt`) — RUN 2026-09-12, medium

Sections 0 SCOPE (asked/decisions/tiers), 1 CONVENTIONS, 2 RECORDS, 3 SYSTEMS tagged T1/T2,
4 CORE LOOP (no end assumed), 5 SCREENS, 6 AUDIO, 7 ART + code recipes, 8 DEBUG API with inputs,
9 TESTS + screenshot table, 10 BUILD ORDER, 11 DONE, A SANITY (fix, then "closes").

| ask | chars | secs | tokens | think chars | complete | notes |
|---|---|---|---|---|---|---|
| collector | 51K | 98 | 17K | 6K | yes | 3D via compose_world; sanity name-checks only: tests call sell/buy that the API lacks; ownedFurniture not in PLAYER record |
| island | 38K | 333 | 50K | 139K | yes | best: exact-value tests derived from numbers, clear*/spawn* scaffolding, real arithmetic sanity, pirates/weather T2 |
| station | 33K | 90 | 16K | 20K | NO — EOS mid-word in §10, no DONE/SANITY | finish_reason=stop; design.py needs a last-heading check + one retry |
| forest | 43K | 114 | 20K | 23K | yes (last sanity bullet cut) | key placed by generator (round-1 shrine/oak defect gone); oil budget + travel time computed |

Quality tracks think length exactly. Round-1 closure defects gone in every design that ran
SANITY. ninfer accepts reasoning_effort low/medium/xhigh only (Nick). xhigh run queued, same asks.
Skeleton misses: `mesh` art kind (arm C) — collector asked buildings "as a scene sprite" in 3D.

### Arm E at xhigh (same prompt, same asks)

| ask | chars | secs | tokens | think chars | complete | notes |
|---|---|---|---|---|---|---|
| collector | 37K | 348 | 52K | 151K | yes | sell/buy in API; real fish-timing derivation; went 2D (medium went 3D) |
| island | 37K | 281 | 43K | 110K | yes | setRectangle scaffolding before move tests; "within 0.001"; lastSound asserts |
| station | 36K | 382 | 57K | 156K | yes | SANITY EDITED THE DESIGN: medkits 3→7, lockers 6→8 to close combat damage 138 |
| forest | 29K | 359 | 53K | 150K | yes | ART regressed: "title scene is the only AI art", every sprite a code circle — the RECIPE clause won over the art clause |

4/4 complete at xhigh vs 3/4 at medium; every xhigh sanity did arithmetic and one fixed the
design. Cost ~5–6 min per design on the 27B (medium 1.5–5.5). Think chars 110–156K at xhigh
vs 6–139K at medium: xhigh makes the deep think reliable instead of lucky.
Open prompt fixes before a build arm: (1) art clause must win over recipes — AI art for every
thing with a subject, recipes only for what code draws; (2) `mesh` kind for 3D (arm C);
(3) design.py: reject a design missing the last heading, retry once.

## One-off BUILD on the island xhigh skeleton design — 2026-09-12, run cd725c2f14d8, local 27B

Pinned as the prompt (10K tokens), prod nudge, cap 200. 20 steps, ~12 min GPU, done twice, error
gate 0 rounds, play gate 0 broken / 9 of 9 predictions met. game.js 1000 lines + world.js 703.
window.__game built with EVERY section-8 function (setRectangle, placeCache, setDay, ...).
Turn 0 = 27K-token think, no program (known). Big writes landed turns 3–4; edits 7–11; the nudge
was answered with 5 read-only turns, nothing built, done again. The prod nudge says "first thirty
seconds", not "section 11 DONE" — the DONE list was never ticked. Play gate impression: island
reads small (its guess; code has land radius 120 tiles of 256); terrain is per-tile hash speckle.
Harness bugs hit: hand-started worker has usd_per_hour NULL → complete 500 (fixed in jobs.py,
uncommitted); a worker that gave up completing keeps renewing the lease so the reaper never
requeues (restart the worker). VERDICT: Nick plays.

## v2 island design, one build WITH play() — 2026-09-12, run b5dc1d577b9b, local 27B

Same pinned design as 2ef1ff3a508b (which shipped movement dead: play gate 4/4 unmet, fix round).
With play(): 60 steps, done at 58, error gate 0 rounds. Model reached for play() unprompted at
turn 8 and used it in ~40 turns: found "import outside a module", "rng is not a function", a lose
condition that never fired, a rope gap that never blocked, a missing setVolume; ran the design's
15 tests to 15/15 (turn 57); pressed REAL keys via __press at turns 44/55/56 (x 48→53.9);
clicked Begin through the DOM, checked pause/win/lose/clue/compass text. After the compaction at
turn 29 it went straight back to play(), no re-read spiral.
