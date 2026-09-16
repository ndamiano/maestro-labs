# who owns the levels

Status: closed — not adopted
Control: spec-skeleton overnight builds 2026-09-14: forest 90792e94d3c4 (broken), platformer 82592d612763 (capped), island 5e1cf145860b (done, "barren"); design-team harness (3e05254 + 90d82c3): pipes 9e6f192bd791 (96 steps, 5 compactions, ok=False)

## Purpose

The specs own systems and numbers; nobody owns what fills the space. Forest's gameplay.md gave a
120×80 hand-authored map with a validator and the builder ran the output cap dry 14 times trying to
author it; platformer's gave ten stages as prose ranges and the builder typed the tilemaps; island's
island was "huge and barren"; station's first minute was unclear. Nick on all six: "bones and
systems land, content is thin."

## Hypothesis

The gameplay prompt states who writes content and in what form: levels as data the builder types
from a compact scheme, or a generator with the rules, or a first-minute script — one of those per
kind of content, never prose ranges. Measured: 30K-output-cap turns, turns to first play, and
Nick's read of density/clarity, on forest and platformer first. Idea failure: the docs get
longer and the builder still authors from prose.

## Setup

Arm: content is its own design leg. Uncommitted src on branch `experiment/content-leg`:

- `prompts/design/content.txt` (new): the content designer writes every level, map, wave, puzzle
  and dialogue, one form per kind: written in full in a compact scheme it defines, a generator with
  a playability check (build from the property outward, e.g. solved state then scramble), or the
  opening-minute script (every game). Never a range, rule or parameter table; anything it cannot
  confirm by reading goes in a generator.
- `gameplay.txt`: "space and layout" becomes the shape of the spaces and the rules any one must
  follow; the content bullet moves to NOT responsible, pointing at the content designer.
- `visual.txt`, `engineering.txt`: four-person team; "gameplay designer has designed the levels"
  becomes the content designer; both get content.md. Engineering makes its data load and its
  generators and checks run.
- `integrate.txt`: four colleagues; content.md goes to the builder unchanged as
  `design/content.md`, point to it by section and never copy or summarize; rulings that break
  content are named in 0.2; §4 progression points at the content.md section per level/generator.
- `design.py`: chain is gameplay → content → (visual ∥ engineering) → integrate.
- `staging.py`: `seed_vendor` copies `<run>/design/content.md` to `game/design/content.md` beside
  design.md.
- tests: `test_design.py` chain order and content.md on disk, `test_staging_design.py` content seeded.
  `scripts/ci.sh` all green.

Ask: pipes (`asks.txt`), the same text as control 9e6f192bd791. Local prod path as dod-checkoff:
control plane, `local_gpu.py auto`, quasar ninfer :8090, k=1, prod 200 step cap.

    cd labs/content-ownership && bash ./run.sh

Read after: content.md forms (data / generator+check / script, or prose again = idea failure);
spec §4 points or copies; builder turns ≥29K out and what they were spent on; turns to first play;
reasoning tokens spent authoring levels; gates; Nick plays for density and clarity.

## Log

### 2026-09-15 control check on the design-team harness — content still unowned

Harness moved after this README (3e05254 design team, 90d82c3 design-map). gameplay.txt now lists
"the content that will fill each of the sections" as the gameplay designer's, with no form. No
forest run exists on the new harness; read the five level-shaped builds from the 2026-09-15 battery.

| run | ask | steps | 30K-cap turns | capped turns spent on |
|---|---|---|---|---|
| 9e6f192bd791 | pipes | 96 | 3 (+1 at 28K) | t13–t14 hand-solving level 23's grid in reasoning |
| 202198c78de5 | salvage | 200 | 4 | t17 placing wrecks per sector from prose rules; rest code |
| 112ec65202b2 | rhythm platformer | 200 | 4 | code planning |
| 194354ba2b2e | heist | 57 (fix) | 2 | code planning |
| 9c62c1d1e58c | tower defense | 123 | 2 | code planning |

Cap-outs fell from forest's 14 to 2–4 per build; most are now code planning, not content.
Pipes is the lab's failure intact: spec §4 "Progression and difficulty" gives a 24-row table of
grid size, outputs, needs and caps plus layout rules ("Designers must choose openings so the level
is solvable", gameplay.md §4.5) and a level data schema, but no role writes a layout. The builder
authored all 24: t13–t14 = 101K output tokens (20% of the run's 497K) solving grids by hand, t36
a Python validator over all 24, then a 47 KB levels.js. Control for the arm: pipes 9e6f192bd791.

### 2026-09-15 run 1, design only: pipes 9ac84769bb99 — content leg designs by hand and caps out

`--new` (synchronous design, no build), content.txt as Nick rewrote it: story, content "procedurally
generated (with an algorithm) or designed", opening-minute script, density; never a range or rule.

gameplay.md 33.7K, 50K tokens, 259 s: clean hand-off. §14 hard content constraints, §15 tutorial
targets, §24 "Content Designer Handoff", no layouts. It raised the campaign to 50 levels (control 24).

content: attempt 1 = 100,000 output tokens in 435 s, empty reply. Retry = 100,000 in 402 s, 18.5K
chars landed, cut off inside level 31. Chose "designed" for all 50, no generator. Story, conflict
rulings (tutorial slack, level 5 two-opening source), a compact line scheme with legend, opening
minute script and density table all good. `check_levels.py` over the level data (target state):
L1–L10 connect, L11 and L13 put a plant and a pipe on the same cell, L21–L30 have locked pipes
whose init differs from target (its own scheme forbids it) and MIN sums that disagree with its own
definition, L25 and L27 are the same layout, several levels have openings that face a neighbour
that does not face back (L14, L17, L23, L25, L28–L30). Reasoning not captured on the `--new` path.

Downstream legs both caught it. engineering.md (40.9K, 54K tokens, 272 s): "the content.md excerpt
in the prompt is truncated after level 31", found level 11's `pipe 4 1` init/target break and the
MIN that matches the other target, ruled "the engineering system must not silently fix content",
designed a content.md parser plus `validateLevel`/`validateAllLevels` in the debug API, and cut
procedural levels because gameplay had. Integrator (65.9K, 50K tokens, 231 s, one round, no
continuation): zero level blocks copied, 22 pointers to content.md, and §0.2 R1/R9 rule the broken
levels out of the Tier 1 playable set — 11 and 13 duplicate cell at (4,1), 14 unsolvable, 31
incomplete, 32–50 missing — with Tier 1 floor "levels 1–10 playable" and remediation to 50 in
Tier 3. It found 11/13/14 independently, matching check_levels.py.

Whole chain 35 min wall, 431K output tokens, no build.

Read: the leg owns content and writes it as data, the form question is answered, and the split buys
a reviewer — engineering and the integrator both audit levels as data, which no leg did before. But
the hand-solving moved from the builder's turns into the content call: correct while levels are
tiny, wrong past 6x6, and 50 levels do not fit in 100K. The prompt's own "anything you cannot
confirm by reading belongs in a generator with its check" did not bind; the leg chose "designed"
for all 50 and gameplay's §24 had already asked for 50 hand-authored levels.

### 2026-09-15 run 1 build: 9ac84769bb99 at a 400 cap — ships, the builder finishes the content

`DEFAULT_MAX_STEPS` 200 → 400 on the branch (Nick: "lift the cap to 400 just in case"). Build
`c3a4e890496f`: 400 steps, 68m42s, 17 compactions, ok=False — it hit the cap without calling done,
so neither gate ran. Control 9e6f192bd791: 96 steps, 5 compactions, ok=False.

Hand-off works end to end. content.md seeded to `game/design/content.md`, read in ranges at turns
5–10, `js/hsg-content-parser.js` written at turn 14: the builder parses the designed data instead
of inventing levels. It also wrote `tools/flowcheck.py`, a Python mirror of the flow engine, and
pre-validated levels with it (turns 95–99, 193, 220–222) — the check the content leg could not run.

Headless smoke on the staged copy: no console errors, 22 debug functions, in-page harness "Results:
65 pass", `validateAllLevels()` → `valid: true, levelCount: 50`, only soft warnings
(SINGLE_DEMAND_AFTER_5, NO_FULL_CAPACITY_IN_INTENDED). The builder edited `design/content.md` in
place: authored the missing 32–50 and fixed the duplicate cell in 11 and 13. check_levels.py on the
shipped file: 38 clean, no collisions, remaining flags are dangling openings (18, 20, 23, 25, 27,
28, 30) and repeated layouts (4≡1, 9≡7, 13≡11, 27≡25, 40≡36, 46≡43).

Cost of the second file: 17 compactions vs the control's 5, driven by whole-file content.md reads
(turns 141–144). Steps 194–201 were low-yield re-reads of its own files.

Read: content ownership holds through the build, and the pipeline degrades well — the design leg
wrote 30 of 50 levels and the builder, which can run code, finished and repaired the rest against
the validator engineering designed. Not yet judged: whether the levels are GOOD. Nick plays:
http://127.0.0.1:8765/9ac84769bb99/index.html

### 2026-09-15 four content-shaped asks, design only — the leg picks the form and finishes

Nick: pipes "doesn't really need a content designer". Four asks with design-team controls from the
same day, run through the chain only (`queue_designs.sh`, one at a time, no build):

| ask | run | control | content.md | legs peak out_tok | wall |
|---|---|---|---|---|---|
| heist | 2370c542cc42 | 194354ba2b2e | 44.0K | 77K | 22 min |
| story RPG | ce58f5503a8e | d615927dc0fe | 62.9K | 79K | 22 min |
| salvage | 14eb92cc0273 | 202198c78de5 | 34.6K | 62K | 19 min |
| rhythm platformer | 957c62fa70b6 | 112ec65202b2 | 33.5K | 69K | 22 min |

No leg hit the 100K cap and no document was truncated — pipes was the outlier, not the rule.

Forms, per a read of all four (subagent, spot-checked): each picks a form per kind of content and
mixes them. Heist writes 53 painting names, their per-mission placement and every guard's waypoints
as data, and puts the map behind a generator — "there is no manual per-tile map authoring after the
generator is implemented. The generator output is the content." Salvage writes five sectors of
wrecks and hazards as data, generators for debris and respawn placement, each with its own check.
Rhythm platformer writes 10 levels of metadata plus a platform-expansion algorithm and a literal
`validateLevel` pseudocode: "if validation fails, the build must fail." RPG goes fully authored: 70
rooms, 15 story beats, 5 anchors, 12 echoes, boss phases, all as YAML records. All four wrote the
opening-minute script. All four wrote their own validation section — heist's §7 gate has 35 checks
and argues "a painting that cannot be safely stolen is not content."

Delivered = promised in every case (53/53 paintings, 70/70 rooms, 15/15 respawn templates, 10/10
levels), checked by re-counting, not by trusting the documents' own claims.

Leakage (the forbidden "range, rule, or parameter table for someone else to fill in"): none in
heist or rhythm platformer. Two mild cases of the same shape: RPG gives a placed enemy
`damage_source: act_minor_damage` so its number comes from joining §5.2 archetypes to §5.1 act
stats, and salvage keeps wreck mass/radius in a type table the wreck rows join against. Both are
deterministic with no judgment left open, so they are indirection, not a content gap — worth a
prompt line only if the standard is zero-indirection.

Read: the leg does what it was asked on content-shaped games, and picks a generator exactly where
one is needed. The pipes cap-out was a puzzle-solving job, not the form rule failing.

### 2026-09-15 builds of the four, 400 cap (in progress)

`build_queue.sh`, one at a time, each staged to :8765/<run>/index.html.

| ask | run | steps | wall | compact | ok | gates |
|---|---|---|---|---|---|---|
| pipes | 9ac84769bb99 | 400 (cap) | 68m | 17 | False | never ran (no done) |
| heist | 2370c542cc42 | 272 | 39m | 8 | True | error 0 rounds, play 0 rounds, broken [] |

Heist play gate: "level select screen loads... WASD movement works... HUD displays painting count
(0/1) and exit status (Locked)... guard is visible and moves". Complaint is the opening: "the
player spawns extremely close to a guard... gets pinned in a corner early on, which undermines the
sense of agency", so crouch and camera cones went untested. The content leg wrote a beat-by-beat
opening minute; spawn placement (generator, §3) fights it. That seam — scripted opening vs
generated placement — is the thing to watch in the remaining builds.

### 2026-09-15 Nick plays the three builds — every defect is in the render/entry layer, none in content

pipes 9ac84769bb99 — "automatically complete every level, so is non functional". Cause is not the
levels: `index.html:30` ships `<script src="test/tests.js">` in the page a player loads. The suite
runs at load, rotates to a win and prints its 65 result lines into the DOM behind the board, so
level 1 shows the win overlay with the HUD still at 0/1 (Nick's screenshot). Loaded headless before
the suite runs, level 1 reads solved:false, plant dry. The content and its validator are fine:
validateAllLevels → valid, 50 levels.

heist 2370c542cc42 — "characters bunched up on the top left, camera doesn't move, character stays
drawn in the top left even though their position in the world is changing". Units seam inside
render.js: the world blits in pixels (`floorCache` is `m.width * TILE`, tiles at `tx * TILE`) while
the camera and entities are in tiles (`cam.x` clamped against `m.width`, follow offset `p.y - 1.5`)
and `drawPlayer`/`drawGuard` draw at `p.x, p.y` with pixel radii (12, 14). A player at tile (5,7)
draws at pixel (5,7). Spec §1.1 states the conversion outright: 1 tile = 1 m = 32 px, player radius
"0.35 m (= 11.2 px)".

RPG ce58f5503a8e — "upside down... if I hit W I jump downwards". Physics is y-up per spec §1.1
("y is vertical, positive up; y = 0 is floor"): jump sets `p.vy = +12.57`, land at `p.y <= 0`.
`renderer.js:227` does `ctx.translate(p.x, p.y)` on a y-down canvas with no negation.

Both gates passed heist and RPG (0 rounds, broken []), and the heist play gate reported "WASD
movement works — the player character visibly shifts position" while the player sprite was pinned
in the corner; it was reading the minimap. Gates detect broken, not wrong-looking.

Read: the content leg is not what is failing. Three builds, three defects, all in the layer that
maps world state to the screen or in what the entry page loads — after a design that stated the
convention correctly in §1.1 both times. Candidate general laws for the build prompt: the page a
player opens runs the game only, never the test harness; and world→screen conversion happens in
one place, in the units §1.1 names.

### 2026-09-15 hand fixes, and the gate they suggest

Fixed in the run dirs and restaged (lab-only edits; the builds stay as evidence in turns.jsonl):

- pipes: deleted `<script src="test/tests.js">` from index.html. Title screen is clean, level 1 no
  longer auto-wins, no test text in the DOM.
- heist `js/render.js`: cones, player, guard and camera draws now convert world→pixels (`* TILE`),
  the exit-dwell ring too, and the camera follow/clamp works in pixels against `m.width * TILE`.
  Verified: player, guards, cones and paintings render at scale and the camera tracks.
- RPG `js/renderer.js`: world transform flipped to y-up (`translate(ox, oy + H*s); scale(s, -s)`)
  to match spec §1.1, with the background art that assumed a y-down canvas corrected (hills, rocks,
  grass, pocket alcoves) and debug text counter-flipped. Verified: jump takes world y 0 → 1.44 m and
  moves the drawn player UP 89 px (~62 px/m, the room scale); the player stands on the floor line.

All three are one class: **what is drawn does not track what the sim says**, plus one entry-page
defect. None came from the design docs — both specs stated the convention in §1.1 and the builder
broke it in the render layer only. The existing gates cannot see this: the heist play gate said
"WASD movement works — the player character visibly shifts position" while the sprite was pinned in
the corner (it was reading the minimap, which scales correctly).

Proposed gate — **projection gate**, deterministic, no LLM, seconds:
1. Entry purity: the page a player opens must not load a test harness, and no test-runner output
   may appear in the DOM after load. (Catches pipes.)
2. Projection agreement: read the player's world position from the debug API, screenshot, move the
   player (debug teleport or held input), screenshot again, and diff. Fit drawn displacement against
   world displacement over 3–5 samples per axis. Fail when the drawn player does not move while the
   world position does (heist: ~1/32 of the expected pixels), when the sign disagrees with the
   spec's axis convention (RPG: y-up sim drawn y-down), or when the fit is not linear.
Both are BROKEN detectors, not taste: the player cannot see themselves move. Cost is one headless
page load per build.

### 2026-09-15 second round of play — two more, same family

pipes "I can't interact with the game": `#win-overlay` and the pause overlay are full-viewport,
`z-index: 20`, `opacity: 0` but `display: flex` with `pointer-events: auto`, so
`elementFromPoint` over a pipe returned the win overlay's `<h2>`. Every click on the board went to
an invisible overlay. Fix: `.overlay { pointer-events: none }`, `.overlay.show { pointer-events:
auto }`. Verified: clicking the pipe rotates it 0 → 1 and solves level 1.

RPG "I don't think there's any way for me to fight": combat exists — `KeyJ` light, `KeyK` heavy,
Shift dodge — with nothing on screen saying so. content.md §8 scripted the teaching beat by beat
("0:35 Prompt appears: Light Attack", "0:40 Prompt appears: Dodge", two Frayed Shards to practise
on) and the builder implemented the prompt widget for blocking messages only ("The door is
sealed"), never the tutorial prompts, and hardcoded an `E` badge on every prompt. Fix: a persistent
controls bar in the HUD. Also seated the shard enemies on the floor — their art straddles the
origin, which after the y-up flip put half the body under the floor line. Verified: walking right
reaches P2 with 2 live enemies and J fires an attack.

Nick's read: heist "the best version so far"; RPG "very mixed leaning towards bad... probably a ton
of content" but the character reads poorly and combat was undiscoverable.

The content leg keeps being right and the last inch keeps being wrong: the opening minute was
written, and what the player was never told is exactly what the script would have told them.

Gate proposal grows a third check — **input reachability**: after load, the documented primary
interaction must change game state. Click the element the spec calls interactive (or send the key)
and require a state delta from the debug API; fail when nothing changes, and report what
`elementFromPoint` returned so an invisible overlay names itself. That is the pipes defect, and it
is a BROKEN detector: the player cannot play at all.

### 2026-09-15 gate prototype, validated against the defects it was drawn from

`projection_gate.py` (lab, deterministic, no LLM, ~20 s/game): entry purity, input reachability,
view response. Validated by rebuilding the pre-fix code — heist and RPG from their own `game.git`
HEAD (my fixes are working-tree only), pipes reconstructed — staging both versions and running it.

| check | verdict |
|---|---|
| entry purity | WORKS. pipes pre-fix: "test-runner output in the DOM" + results object. heist (still, post-fix): `index.html` loads `tests/harness.js` + `tests/test.js` as modules and the harness sets `window.__testResults` on load — the player's page runs the suite. salvage ships `tests.js` but only defines `__runTests`, correctly reported as a note, not BROKEN. |
| input reachability | WORKS where an overlay steals clicks: pipes pre-fix named its thief — "first interactive BUTTON is covered by DIV.overlay show ('The garden exhales')". |
| view response | WORKS for the heist units bug once measured as a FRACTION of repainted pixels: pre-fix 0.07% vs post-fix 2.21%. The naive "did any pixel change" version passed the broken build, because the minimap repainted correctly — the same thing that fooled the play gate. |
| y-flip (RPG) | NOT CAUGHT. The view responds; only the sign is wrong. Undetectable without knowing the player's world position. |
| false positives | pipes post-fix fails the view-response check: a click-only puzzle has no movement keys, so 0% is correct behaviour. The RPG is never entered because its "New Game" is a `div.menu-item`, not a `button`. |

So the heuristic half is real and the rest needs a contract. Proposed: §8 DEBUG API must expose two
things every game can answer — the player's world position (or null where there is no avatar), and
a call that applies the game's primary interaction. With those, view response becomes exact (drawn
displacement fitted against world displacement, sign checked against §1.1) and input reachability
stops guessing which element to click. Both are one line in the design prompt's §8 section and cost
the builder nothing it does not already have.

### 2026-09-15 pipes, third defect: the page ships in test mode

`index.html` line 13: `window.HSG_TEST_MODE = true`. Bootstrap then puts the clock in manual mode,
so `HSG.clock.now()` stays 0 forever, the 300 ms win delay never fires and the win overlay with
"Next Level" never appears — Nick: "I don't get the ability to go to the next level". Set to false:
level 1 solves → overlay → Next Level → level 2. Third instance of one class in one game: the page
a player opens was configured for the harness, not the player.

Gate: dropped at Nick's call. The prototype is deleted; the validation table above is the record.

## Outcome

NOT ADOPTED. The content leg works as designed and does not buy quality.

What held. Content is owned and written as data: on four content-shaped asks no leg hit the cap, no
document was truncated, each picked a form per kind of content (heist put its map behind a
generator, salvage generated debris and respawns with checks, the rhythm platformer shipped a
`validateLevel` that fails the build, the RPG wrote 70 rooms out in full), delivered matched
promised on every count, and all four wrote their own validation section and opening-minute script.
The split also bought a reviewer: engineering and the integrator audit levels as data, and the
integrator pointed at content.md 22 times without copying it. The builder parses that data instead
of inventing levels, and when the leg ran out of budget on pipes it finished and repaired the rest
against the validator engineering designed.

What did not. Quality did not move. Nick played four builds: heist "alright... the best version so
far" but only after a hand fix, salvage "fine, no bugs, but it feels bad", RPG "still just kinda
bad" after two rounds of fixes, pipes unplayable until three hand fixes. Nick: "this hasn't given
me much confidence in the content agent idea. It seems like it's not viable."

Why, on the evidence. Every defect Nick hit came from the layer after the design: entity draws in
world units on a pixel canvas, a renderer y-down against a y-up sim, invisible overlays eating
clicks, a page shipped in test mode, a scripted tutorial the builder never wired. The designs were
right each time — both specs named the axis and unit convention in §1.1, and content.md §8 scripted
the exact prompts the player never saw. Content ownership is not the constraint; the constraint is
that the build loses what the design already says, and that a game with all its content present
still feels bad. Cost of the leg: one sequential design call (~20 min) and a second design file the
builder re-reads (pipes: 17 compactions vs the control's 5).

Kept as findings, not adopted as a change:
- the prompt seam is real — gameplay hands off content cleanly once it is told to;
- the builder can validate what a design leg cannot, because it runs code;
- three defect classes worth a cheap check, if the harness ever gets a debug contract for the
  player's world position and primary input (see the gate table above).

