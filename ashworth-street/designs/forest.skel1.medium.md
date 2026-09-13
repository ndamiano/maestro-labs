# 0. SCOPE

## 0.1 Asked

"Explore a haunted forest at night" → Sections 3 (Forest Generator, Light & Visibility, Enemy AI, Timer & Dawn, Fear), Sections 2 (all records), Section 7 (dark art with limited light), Section 6 (ambient dread audio).

"escape before dawn" → Sections 3 (Timer & Dawn, Item Pickup, Collision & Damage), Section 4 (core loop ending at the gate), Section 5 (escape and failure screens).

## 0.2 Decisions

- **2D top-down.** The player sees a dark forest from directly above with a circular lantern glow around their character. This is the clearest way to show "you are lost in a dark place and can only see a few metres around you." A 3D first-person view would hide the map layout and make the "explore" part harder than the "dread" part; top-down lets the player plan routes while still feeling enclosed by darkness.
- **Single run, no meta-progression.** The game is one timed escape. The player wins by reaching the gate with the key before 300 seconds elapse, or loses by running out of time or health. There is no between-run progression; each run uses a new seed so the forest is different.
- **No combat.** The player does not attack enemies. The player avoids, dodges, and outruns them. This keeps the game about tension and navigation rather than shooting, matching the "haunted" and "escape" framing.
- **The key is off the main path.** The winding dirt path leads the player east toward the gate, but the key that opens the gate is placed on a ground tile at least 6 tiles away from any path tile. The player must leave the path, into the dark, to find it.
- **Wraiths ignore terrain; shamblers do not.** Wraiths are spectral and drift through trees and rocks. Shamblers are physical and are blocked by trees, rocks, and water. This makes wraiths the "unfair" threat and shamblers the "fair" threat you can outmanoeuvre.
- **The dawn glow is always visible.** A faint warm band of light sits at the eastern edge of the viewport at all times, brightening as the timer runs down. This is the player's compass: the exit is east, toward the light.
- **Lantern drains, oil refills.** The player's light radius shrinks over time. Four oil canisters in the forest restore it. This creates a resource-management pressure layered on top of the time pressure.
- **Fixed 300-second timer.** Five minutes is long enough to explore and tense enough to feel urgent. The timer is the single source of pressure; there is no "the forest heals enemies" or "waves."
- **Three enemy types, not more.** Wraith (fast, spectral, chases), Shambler (slow, physical, patrols then chases), Watcher (stationary, damage aura). Three is enough variety for a 5-minute run without overcomplicating AI.

## 0.3 Tiers

**TIER 1 (the game):** Forest Generator, Movement, Light & Visibility, Enemy AI, Timer & Dawn, Item Pickup, Collision & Damage, Camera, Audio.

**TIER 2 (what makes it good), in order to add:**
1. Fear system: fear meter, panic distortion, screen vignette at high fear.
2. Dawn phase transitions: at 200 s and 100 s the forest shifts (enemy speeds change, ambient light shifts, a low audio swell marks the shift).
3. Wraiths phase through terrain: they ignore trees and rocks when moving, making them unpredictable.
4. Eastern dawn glow: a persistent warm gradient on the east edge of the viewport that brightens as the timer decreases.
5. Mist patches: 6 translucent fog blobs that drift slowly across the map and reduce the player's effective light radius by 1 tile while the player is inside one.
6. Footstep and enemy proximity audio: quiet footstep ticks for the player, a low growl that rises in volume as an enemy closes to within 4 tiles.
7. Screen shake on damage: 0.3-second shake of ±4 px when the player takes a hit.
8. Clue direction flash: collecting a clue shows a 3-second arrow overlay pointing toward the gate.

**TIER 3 (never before all Tier 2 is in):**
- Firefly particles drift through clearing tiles; 4 per clearing, slow sine drift.
- Trees sway: each tree tile's sprite oscillates ±1 px on a 2-second sine, phase offset by tile index.
- A distant wolf howl plays every 25 seconds from a random azimuth.

# 1. CONVENTIONS

- **Units.** One tile is 32 pixels. Positions are in tiles (float). Speeds are tiles per second. Radii are in tiles. Time is in seconds. The fixed step dt is 1/60 second (≈16.67 ms).
- **Axes.** X increases to the right (east). Y increases downward (south). "Up" on screen is north (−Y). The player faces the direction of movement; there is no rotation of the world.
- **Origin.** Tile (0, 0) is the north-west corner of the 60 × 40 world.
- **Camera.** The camera centrep on the player's tile position, offset by −0.5 tiles so the player is at screen centre. The camera does not rotate. Viewport is the full browser window; the camera clamps so it never shows tiles outside the 0–59 / 0–39 range.
- **Update loop.** Fixed step of 1/60 s. Each tick, in this order: (1) Timer & Dawn, (2) Movement (player input, enemy AI, item drift for mist), (3) Collision & Damage, (4) Light & Visibility, (5) Fear, (6) Item Pickup, (7) Camera. After all systems, render.
- **Random source.** One function `rand()` seeded at game start. All randomness in the game calls `rand()`. No `Math.random()` anywhere else. The seed is an integer the player can set or that defaults to the millisecond clock.
- **Controls.**

| Input | Action |
|---|---|
| W or Arrow Up | Move north (−Y) |
| S or Arrow Down | Move south (+Y) |
| A or Arrow Left | Move west (−X) |
| D or Arrow Right | Move east (+X) |
| Touch: drag | Move in the drag direction relative to player centre |
| Touch: tap the oil/key/clue icon in HUD | No action (informational only) |
| Escape | Pause (toggle) |
| R | Restart with a new seed (only from the end screen) |

The player moves at 3.0 tiles/s. Diagonal movement is normalised (× 1/√2 on each axis) so diagonal speed equals straight-line speed.

# 2. RECORDS

RECORDS: PLAYER, ENEMY, TILE, ITEM, GAME, CAMERA, MIST

**PLAYER:** x (float, tiles, start 30.0), y (float, tiles, start 20.0), speed (float, tiles/s, 3.0), health (int, 1–5, start 5), invuln (float, seconds remaining of invulnerability, start 0.0), light_radius (float, tiles, start 5.0), max_light (float, tiles, 6.0), has_key (bool, start false), has_clue_flash (float, seconds remaining of clue arrow overlay, start 0.0), fear (float, 0–100, start 0.0, T2), facing (int, 0=N, 1=E, 2=S, 3=W, start 3/E).

**ENEMY:** x (float, tiles), y (float, tiles), kind (string, see roster), speed (float, tiles/s, from roster), aggro_radius (float, tiles, from roster), patrol_x0 (float, tiles, shambler only), patrol_x1 (float, tiles, shambler only), patrol_dir (int, +1 or −1, shambler only, start +1), patrol_y (float, tiles, shambler only), aura_radius (float, tiles, watcher only, from roster), aura_timer (float, seconds the player has been in this watcher's aura, 0.0), drift_dir (int, 0–3, wraith only, start rand 0–3), drift_timer (float, seconds until next drift direction change, wraith only, start 0.0), active (bool, start true), spawn_delay (float, seconds before this enemy appears, start 0.0, used by phase-spawned wraiths).

ENEMY roster:

| kind | speed (tiles/s) | aggro_radius (tiles) | aura_radius (tiles) | terrain_ignoring (bool) |
|---|---|---|---|---|
| wraith | 2.0 | 6.0 | 0 | true |
| shambler | 1.0 | 4.0 | 0 | false |
| watcher | 0.0 | 0.0 | 3.0 | n/a (stationary) |

**TILE:** x (int, 0–59), y (int, 0–39), type (string, see roster). One TILE record per grid cell, 2400 total.

TILE type roster:

| type | walkable (bool) | visual note |
|---|---|---|
| ground | true | very dark green-brown |
| path | true | slightly lighter brown, dirt |
| water | false | dark blue-black |
| rock | false | grey, angular |
| tree_pine | false | dark green triangle silhouette |
| tree_oak | false | rounder dark green |
| tree_dead | false | grey-brown, bare branches |
| clear | true | open, slightly lighter than ground |
| gate | false (until opened) then true | iron gate sprite |
| exit | true | dark road, beyond the gate |

**ITEM:** x (float, tiles), y (float, tiles), kind (string, see roster), collected (bool, start false).

ITEM roster:

| kind | effect on pickup |
|---|---|
| oil | PLAYER.light_radius += 3.0, capped at 6.0 |
| key | PLAYER.has_key = true |
| clue | PLAYER.has_clue_flash = 3.0 |

**GAME:** time_remaining (float, seconds, start 300.0), phase (int, 1–4, start 1), gate_open (bool, start false), state (string: "title", "playing", "paused", "won", "lost_time", "lost_health", start "title"), seed (int, start from clock), gate_x (int, start set by generator), gate_y (int, start set by generator), key_x (float, tiles, start set by generator), key_y (float, tiles, start set by generator).

**CAMERA:** x (float, tiles, start 30.0), y (float, tiles, start 20.0).

**MIST** (T2): x (float, tiles), y (float, tiles), dx (float, tiles/s, ±0.2), dy (float, tiles/s, ±0.2), radius (float, tiles, 2.0). Six MIST records total, placed by the generator.

# 3. SYSTEMS

SYSTEMS: Forest Generator (T1), Movement (T1), Light & Visibility (T1), Enemy AI (T1), Timer & Dawn (T1), Item Pickup (T1), Collision & Damage (T1), Camera (T1), Fear (T2), Audio (T2)

---

## Forest Generator (T1)

A SEEDED GENERATOR. It runs once at game start (and on `seed(n)` + restart) and fills the 2400 TILE records, places all ITEMS, ENEMIES, MISTs, and sets GAME.gate_x, gate_y, key_x, key_y.

**Parameters:** seed (int, from GAME.seed).

**Procedure, in order:**

1. Set every TILE.type to "ground."
2. **Path.** Starting at tile (30, 20). Walk east one tile at a time to x = 57. At each step, with probability 0.3 (via `rand()`), detour 1–3 tiles north or south (pick direction via `rand()`), then continue east. Mark every tile the path visits as "path." The path is 2 tiles wide: mark the tile and the tile directly south of it as "path" (or north, if south is out of bounds). Record the final path tile's y as `path_end_y`.
3. **Gate and exit.** Set TILE(58, path_end_y) to "gate." Set TILE(59, path_end_y), TILE(59, path_end_y−1), TILE(59, path_end_y+1) to "exit" (clamp y to 0–39). Set GAME.gate_x = 58, GAME.gate_y = path_end_y.
4. **Trees.** For each tile where type is "ground" (not path, not water, not yet rock, not clearing, not gate, not exit): compute base probability 0.55. For each of the four orthogonal neighbours, if that neighbour's type is already a tree type, add 0.10 to the probability (cap 0.85). If `rand() < probability`, assign a tree type: `rand() < 0.40` → "tree_pine", `rand() < 0.30` (of remainder) → "tree_oak", else "tree_dead."
5. **Water.** Place 4 water blobs. For each: pick a random tile (via `rand()`) that is "ground." Set that tile and 1–2 adjacent tiles (horizontal or vertical, via `rand()`) to "water."
6. **Rocks.** Place 5 rock tiles: random "ground" tiles, set to "rock."
7. **Clearings.** Pick 4 random "ground" tiles that are not within 3 tiles of the path. For each, set a 3×3 block centred on that tile to "clear" (only overwrite tiles that are "ground" or a tree type; do not overwrite path, water, rock, gate, exit).
8. **Key.** Pick a random tile that is "ground" or "clear," at least 6 tiles (Manhattan distance) from every "path" tile, at least 8 tiles from the player start (30, 20). Set GAME.key_x, GAME.key_y. Place an ITEM of kind "key" there.
9. **Oil.** Place 4 ITEMS of kind "oil" on random "ground" or "clear" tiles, each at least 5 tiles (Euclidean) from any other ITEM, at least 4 tiles from the player start.
10. **Clues.** Place 3 ITEMS of kind "clue" on random "ground" or "path" tiles, at least 5 tiles from the player start.
11. **Enemies.** Place:
    - 3 WRAITHS on "ground" tiles, each at least 6 tiles from the player start and at least 4 tiles from every other ENEMY.
    - 2 SHAMBLERS on "path" tiles, each at least 5 tiles from the player start. Set their patrol_x0, patrol_x1 to the path tile ± 2 (clamped to valid path tiles), patrol_y to the tile's y, patrol_dir to +1.
    - 3 WATCHERS on "ground" tiles adjacent to a "path" tile, at least 8 tiles from the player start.
    Set each ENEMY's kind, speed, aggro_radius, aura_radius from the roster. Set active = true, spawn_delay = 0.0, invuln = 0.0, aura_timer = 0.0, drift_timer = 0.0.
12. **Mist** (T2). Place 6 MIST records on random "ground" or "clear" tiles. Each: dx = ±0.2 (sign via `rand()`), dy = ±0.2, radius = 2.0.

**VERIFIER.** After generation:
- A BFS walk from (30, 20) using only walkable tiles reaches the gate tile (58, path_end_y). If the gate is "gate" (not walkable), treat it as walkable for this check (the player will open it).
- A BFS from (30, 20) reaches the key tile.
- No ENEMY is within 4 tiles (Euclidean) of (30, 20).
- At least 3 of the 4 oil ITEMS are within 15 tiles (Euclidean) of some "path" tile.
- The key tile is not "path" and not "gate."

**If any check fails, re-roll with seed + 1 and repeat. Maximum 20 re-rolls; if all fail, relax the key distance to 4 tiles from path and retry.**

---

## Movement (T1)

**Player movement.** Each tick, read the current input direction (the last held key; both WASD and arrows are bound, last-pressed wins). Convert to a (dx, dy) vector of (−1, 0), (1, 0), (0, −1), (0, 1), or a normalised diagonal. Set PLAYER.facing to the dominant axis direction. Compute new position: PLAYER.x += dx × PLAYER.speed × dt, PLAYER.y += dy × PLAYER.speed × dt. If the target tile (floor of new x, floor of new y) has a TILE.type that is not walkable (water, rock, tree_pine, tree_oak, tree_dead) and is not "gate" when GAME.gate_open is true and not "exit," revert the movement on that axis (slide along walls: try x-only, then y-only). Clamp PLAYER.x to [0, 59], PLAYER.y to [0, 39].

**Enemy movement (per ENEMY, if active and spawn_delay ≤ 0):**
- **Wraith:** If PLAYER distance ≤ ENEMY.aggro_radius, move toward PLAYER at ENEMY.speed × phase_multiplier (see Timer & Dawn). Wraiths ignore tile walkability: they move through trees and rocks. If no player in range, after ENEMY.drift_timer expires (3.0 s), pick a new drift_dir (0–3 via `rand()`), set drift_timer = 3.0, and move in that direction at 0.5 tiles/s.
- **Shambler:** If PLAYER distance ≤ ENEMY.aggro_radius, move toward PLAYER at ENEMY.speed × phase_multiplier. Shamblers respect walkability: they do not enter water, rock, tree, or (if not open) gate tiles. They stop and slide if the target tile is blocked. If PLAYER distance > 8.0 tiles, resume patrol: move along patrol_x0 to patrol_x1 (or reverse) at 0.5 tiles/s, flipping ENEMY.patrol_dir at each end.
- **Watcher:** No movement. Stationary.

**Mist drift** (T2): Each MIST: MIST.x += MIST.dx × dt, MIST.y += MIST.dy × dt. If MIST.x < 0 or > 59, flip MIST.dx. Same for y.

---

## Light & Visibility (T1)

**Lantern drain.** Each tick: PLAYER.light_radius −= (1.0 / 45.0) × dt. If PLAYER.light_radius < 1.0, set to 1.0.

**Effective visibility.** The player's visible radius is PLAYER.light_radius. Additionally, during Phase 4 (Dawn), add 2.0 tiles to the ambient (the dawn glow lifts the fog). During Phase 3, add 1.0 tile.

**Mist reduction** (T2): If the player's position is within any MIST.radius of a MIST centre, subtract 1.0 tile from effective visibility (floor at 1.0).

**Rendering rule.** Each tile is drawn only if its centre is within the effective visibility radius of the player, or if its type is "exit" (always faintly visible), or if it is within 0.5 tiles of the eastern edge of the world (the dawn glow band, T2). Tiles outside visibility are not drawn; the background is solid #0a0a0f. The visibility boundary is a soft radial gradient from the player: full brightness at 0, linear fade to 0 at the effective radius.

**Dawn glow** (T2): A vertical gradient band on the east edge of the viewport, 3 tiles wide, colour interpolated from #0a0a0f (Phase 1–2) to #1a1a3a (Phase 3) to #2a2a4a (Phase 4), alpha 0.3. Brightens linearly as time_remaining decreases from 300 to 0.

---

## Enemy AI (T1)

This system is the decision layer for enemies. Movement execution is in the Movement system; this system sets the target direction and speed.

**Wraith decision.** Each tick, for each active wraith: compute vector to PLAYER. If distance ≤ aggro_radius (6.0), target = normalised vector to PLAYER, speed = roster speed × phase_speed_mult. Else, target = drift direction vector (one of the 4 cardinal directions), speed = 0.5. Wraiths do not collide with each other.

**Shambler decision.** Each tick, for each active shambler: compute vector to PLAYER. If distance ≤ aggro_radius (4.0), target = normalised vector to PLAYER, speed = roster speed × phase_speed_mult. Else, if distance > 8.0, target = patrol direction (±1 on x), speed = 0.5. Else (between 4 and 8 tiles), hold position (speed 0).

**Watcher decision.** No decision. The watcher is always active. The Collision & Damage system checks the aura.

**Phase speed multiplier** (set by Timer & Dawn):
- Phase 1: 1.0
- Phase 2: wraiths 1.5, shamblers 1.0, watchers 1.0
- Phase 3: wraiths 1.5, shamblers 1.5, watchers 1.0
- Phase 4: wraiths 2.25, shamblers 2.25, watchers 1.0

---

## Timer & Dawn (T1)

**Countdown.** Each tick: GAME.time_remaining −= dt.

**Phase transitions.** The phase is determined by GAME.time_remaining:
- time_remaining > 200: Phase 1 ("Deep Night").
- 100 < time_remaining ≤ 200: Phase 2 ("Restless"). On the tick the phase first becomes 2, spawn 1 additional WRAITH at a random "ground" tile at least 12 tiles from the player. Set its spawn_delay = 0.0, active = true.
- 30 < time_remaining ≤ 100: Phase 3 ("Veil Thin"). On the tick the phase first becomes 3, set each WATCHER's aura_radius to 4.0 (from 3.0).
- time_remaining ≤ 30: Phase 4 ("Dawn").

**Dawn arrival.** When GAME.time_remaining reaches 0.0: if the player is on an "exit" tile, set GAME.state = "won". Otherwise set GAME.state = "lost_time."

**Phase audio cue** (T2): On each phase transition, play a low swell (see Audio).

---

## Item Pickup (T1)

Each tick, for each ITEM where collected = false: if the Euclidean distance from PLAYER to the ITEM is ≤ 0.6 tiles, set ITEM.collected = true. Then apply the effect:
- **oil:** PLAYER.light_radius = min(PLAYER.light_radius + 3.0, PLAYER.max_light).
- **key:** PLAYER.has_key = true.
- **clue:** PLAYER.has_clue_flash = 3.0. Each subsequent tick, PLAYER.has_clue_flash −= dt. While > 0, draw a 3-second arrow on the HUD pointing toward (GAME.gate_x, GAME.gate_y).

---

## Collision & Damage (T1)

**Player invulnerability.** Each tick: PLAYER.invuln −= dt (floor at 0). The player is immune to damage while PLAYER.invuln > 0.

**Enemy contact.** For each active ENEMY (wraith or shambler): if the Euclidean distance from PLAYER to ENEMY ≤ 0.7 tiles and PLAYER.invuln ≤ 0: set PLAYER.health −= 1, PLAYER.invuln = 2.0, PLAYER.fear += 15 (T2). If PLAYER.health ≤ 0, set GAME.state = "lost_health."

**Watcher aura.** For each active WATCHER: if the Euclidean distance from PLAYER to the watcher ≤ WATCHER.aura_radius: ENEMY.aura_timer += dt. If ENEMY.aura_timer ≥ 2.0 and PLAYER.invuln ≤ 0: set PLAYER.health −= 1, PLAYER.invuln = 2.0, ENEMY.aura_timer = 0.0, PLAYER.fear += 20 (T2). If PLAYER.health ≤ 0, set GAME.state = "lost_health." If PLAYER distance > aura_radius, set ENEMY.aura_timer = 0.0.

**Gate.** If the player is on the gate tile and PLAYER.has_key is true and GAME.gate_open is false: set GAME.gate_open = true, set the gate TILE.type to "exit" (now walkable). Play the gate-open sound. If the player is on the gate tile and PLAYER.has_key is false: the tile is not walkable, so the player cannot enter (handled by Movement).

---

## Camera (T1)

Each tick: CAMERA.x += (PLAYER.x − CAMERA.x) × 0.1. CAMERA.y += (PLAYER.y − CAMERA.y) × 0.1. (Exponential smoothing, 10% per tick.) Clamp CAMERA.x to [10, 50] and CAMERA.y to [7, 33] so the viewport does not show outside the world.

---

## Fear (T2)

Each tick:
- If PLAYER.light_radius < 3.0 and the player is not within any MIST: PLAYER.fear += 3.0 × dt.
- For each active ENEMY (wraith or shambler) within 3.0 tiles: PLAYER.fear += 20.0 (instantaneous, once per tick, not scaled by dt — it is a spike).
- If PLAYER.light_radius ≥ 4.0: PLAYER.fear −= 8.0 × dt.
- Clamp PLAYER.fear to [0, 100].
- If PLAYER.fear ≥ 100.0: set PLAYER.fear = 50.0, PLAYER.light_radius = max(PLAYER.light_radius − 2.0, 1.0). This is "panic": the light dims and the screen distorts for 3 seconds (the distortion is a rendering effect: 3 seconds of horizontal slice offset ±6 px on a 50 ms cycle).

**Visual fear cues:**
- fear > 50: a vignette (dark edges, alpha 0.3) is drawn over the viewport.
- fear > 80: the viewport shakes ±2 px on a 100 ms cycle.

---

## Audio (T2)

All sounds are generated with the Web Audio API. See Section 6 for recipes. The rules:

- **Ambient loop:** A low 40 Hz sine drone plays continuously during "playing" state, volume 0.08. In Phase 3, a second 55 Hz sine adds in at volume 0.05. In Phase 4, the drone frequency rises to 50 Hz.
- **Footsteps:** Every 0.4 s of player movement, play a short soft tick.
- **Enemy proximity:** For the nearest active wraith or shambler, if distance < 4.0 tiles, play a low growl whose volume scales from 0.0 (at 4.0 tiles) to 0.15 (at 0.5 tiles).
- **Heartbeat:** If PLAYER.fear > 70, play a two-beat thump (low sine 60 Hz, 0.1 s each, 0.2 s gap) every 1.0 s.
- **Phase swell:** On phase transition, a 2-second rising sine sweep from 40 Hz to 80 Hz, volume 0.12.
- **Gate open:** A 0.5 s creak (sawtooth 80 Hz → 40 Hz, volume 0.2).
- **Panic sting:** On fear reaching 100, a 0.3 s dissonant chord (two sines 220 Hz and 233 Hz, volume 0.2).

# 4. CORE LOOP

The player's minute-to-minute cycle:

1. **Orient.** The player stands in the dark at the forest centre. The lantern shows 5 tiles around. The eastern dawn glow is faint but present. The player feels the layout: trees, a path, darkness beyond the light.
2. **Push east.** The player follows the dirt path eastward, the direction of the dawn glow. The path winds; the player turns at each bend, the light sweeping the trees. Wraiths drift in the periphery. A shambler patrols a stretch of path ahead.
3. **Find the key.** The path does not lead to the key. The player must see the key's faint glow (items are always visible if within 1.5 tiles, even in darkness) or guess an off-path direction. Leaving the path means entering dense trees with less light. Fear rises if the lantern is dim.
4. **Return and navigate.** With the key, the player navigates back to the path and continues east. The gate is visible as a dark iron shape on the path's end. Without the key, it is solid. With the key, it opens.
5. **Escape.** The player walks through the opened gate onto the exit tiles. The dawn light floods in. GAME.state = "won."

**What makes it worth doing again:** Each run is a different forest (new seed). The key is in a different place, the enemies are in different positions, the tree density varies. The player learns strategies: which enemies to avoid, how to manage oil, how to time the key search against the draining lantern.

**The end:** There is no meta-progression. The game ends when the player wins (escaped) or loses (time or health). The end screen shows the result, the time remaining (or time elapsed), and an "R to try a new forest" prompt. There is no score, no leaderboard, no unlocked content. The satisfaction is the escape itself: the relief of the dawn.

# 5. SCREENS

**State machine:**

title (dark forest background, the words "HAUNTED" in large serif, "a forest at night. escape before dawn." below, "press any key to begin" pulsing) → playing → paused (semi-transparent overlay, "PAUSED", "Escape to resume, R to restart") → won (bright dawn gradient background, "You escaped into the dawn.", time remaining shown, "R for a new forest") → lost_time (black screen, "The forest swallowed you in the dark.", "R to try again") → lost_health (black screen, red tint, "Your light went out.", "R to try again").

- Any key on title → start Forest Generator with a new seed, set GAME.state = "playing."
- Escape during playing → paused. Escape during paused → playing.
- R on any end screen → new seed, re-run Forest Generator, set GAME.state = "playing."
- R during paused → same as R on end screen.

**HUD table (visible during playing and paused):**

| Element | Record field(s) shown |
|---|---|
| Health bar (5 pips, top-left) | PLAYER.health |
| Lantern radius (small radial icon, top-left below health) | PLAYER.light_radius |
| Timer (mm:ss, top-centre) | GAME.time_remaining |
| Phase name (small text below timer) | GAME.phase → "Deep Night" / "Restless" / "Veil Thin" / "Dawn" |
| Key icon (top-right, lit if held) | PLAYER.has_key |
| Clue arrow (centre-top, 3 s flash) | PLAYER.has_clue_flash > 0 → arrow toward gate |
| Fear vignette (screen edges) | PLAYER.fear (T2) |
| Dawn glow (east edge band) | GAME.phase, GAME.time_remaining (T2) |

# 6. AUDIO

All sounds are generated with the Web Audio API. One master gain node. No audio files.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| ambient_drone | Sine 40 Hz, continuous, gain 0.08. Phase 3: add sine 55 Hz gain 0.05. Phase 4: base freq → 50 Hz. | Loops while GAME.state = "playing." Stops on any other state. |
| footstep | Sine 200 Hz, 0.05 s, envelope: attack 0.01, release 0.04, gain 0.06. | Every 0.4 s while PLAYER is moving (input active). |
| enemy_proximity | Sine 80 Hz, 0.3 s, gain 0.0 → 0.15 (scaled by 1 − dist/4.0, clamped 0–1). Low-pass filter 200 Hz. | Continuously while nearest wraith or shambler is < 4.0 tiles. |
| heartbeat | Two sine 60 Hz, 0.1 s each, 0.2 s gap, gain 0.12. | Every 1.0 s while PLAYER.fear > 70. |
| phase_swell | Sine sweep 40 Hz → 80 Hz over 2.0 s, gain 0.12, attack 0.5, release 0.5. | On each phase transition (1→2, 2→3, 3→4). |
| gate_open | Sawtooth 80 Hz → 40 Hz over 0.5 s, gain 0.2, low-pass 300 Hz. | When GAME.gate_open flips to true. |
| hit | Sine 120 Hz, 0.15 s, gain 0.15, sharp attack. | When PLAYER takes damage (health decreases). |
| panic_sting | Two simultaneous sines 220 Hz and 233 Hz, 0.3 s, gain 0.2, sharp attack, sharp release. | When PLAYER.fear reaches 100. |
| item_pickup | Sine 600 Hz → 900 Hz over 0.15 s, gain 0.1. | When any ITEM.collected flips to true. |
| win_chord | Three sines 262, 330, 392 Hz, 2.0 s, gain 0.15, slow release. | When GAME.state becomes "won." |
| lose_sting | Sine 110 Hz → 55 Hz over 1.5 s, gain 0.15. | When GAME.state becomes "lost_time" or "lost_health." |

# 7. ART

**AI art (one image per distinct thing):**

- Ask for **the player character** as a sprite: a small hooded figure seen from above, 32×32 px, dark cloak with a faint warm glow at the shoulders (the lantern). One image, top-down, no background.
- Ask for **a wraith** as a sprite: a translucent ghostly figure, 32×32 px, top-down, pale blue-white, wispy edges, no shadow. One image.
- Ask for **a shambler** as a sprite: a hunched grey figure, 32×32 px, top-down, dragging one arm, dark mud-brown, slight lean. One image.
- Ask for **a watcher** as a sprite: a still eye-like shape, 32×32 px, top-down, a single unblinking pale eye in a dark oval, faintly glowing iris. One image.
- Ask for **the gate** as a sprite: an iron gate, 32×32 px, top-down (seen from above: two dark iron posts and a crossbar), rusted. One image for closed, one for open (posts apart, crossbar tilted).
- Ask for **an oil canister** as a sprite: a small brass flask, 16×16 px, top-down, warm amber glow.
- Ask for **a key** as a sprite: a small iron key, 16×16 px, top-down, pale metallic.
- Ask for **a clue scroll** as a sprite: a small rolled parchment, 16×16 px, top-down, faintly glowing edge.

Every entity moves in a way one static picture shows adequately (top-down, no walking cycle needed). No anims are required.

**Everything else is drawn in code:**

- **Tiles.** Each tile type is a filled 32×32 px rectangle: ground #1a2a1a, path #2a2a1a, water #0a1a2a, rock #3a3a3a, tree_pine #1a3a1a (draw a small triangle silhouette in the centre), tree_oak #1a4a1a (a small circle in the centre), tree_dead #3a3a2a (a small vertical line with two short branches), clear #2a3a2a, gate (use the AI sprite), exit #1a1a2a.
- **Lantern light.** A radial gradient centred on the player: #fff8e0 alpha 1.0 at centre, linear fade to alpha 0.0 at PLAYER.light_radius. Drawn as a "destination-in" composite over the tile layer.
- **Dawn glow (T2).** A linear gradient on the east 3-tile strip: from transparent to #2a2a4a alpha 0.3, height = full viewport, width = 3 × 32 px.
- **Mist (T2).** Each MIST is a radial gradient circle, radius = MIST.radius × 32 px, colour #4a4a5a alpha 0.4, centred on MIST position.
- **Vignette (T2).** A radial gradient from transparent at 60% viewport radius to #000000 alpha 0.3 at 100%, drawn when PLAYER.fear > 50.
- **Clue arrow (T2).** A 48×16 px arrow shape (triangle + rectangle), colour #fff8e0, centred top of viewport, rotated to point toward (GAME.gate_x, GAME.gate_y). Visible while PLAYER.has_clue_flash > 0.
- **Health pips.** 5 small 8×8 px squares in the top-left. Filled #e04040 for current health, #2a1a1a for lost.
- **Timer text.** Monospace 20 px, #c0c0c0, top-centre.
- **Phase text.** Sans-serif 12 px, #808080, below timer.

# 8. DEBUG API

The game installs `window.__game` with the following functions. All calls are synchronous. All return values are plain JSON-serialisable data.

| Call | What it does | Returns |
|---|---|---|
| `start()` | Sets GAME.state = "playing." If no forest is generated yet, runs Forest Generator with the current seed. | `{ state: "playing" }` |
| `step(dt, n)` | Advances the simulation by n ticks of dt seconds each (n × dt total). Runs all systems in order for each tick. Draws once at the end. | `{ time: GAME.time_remaining, player: { x, y, health, light_radius, has_key, fear }, state: GAME.state }` |
| `setTime(t)` | Sets GAME.time_remaining = t. Recomputes GAME.phase. Does not draw. | `{ phase: GAME.phase, time: t }` |
| `seed(n)` | Sets GAME.seed = n. Re-runs the Forest Generator (clears all ENEMIES, ITEMS, MISTs, TILEs and rebuilds). Resets PLAYER to start. Sets GAME.state = "title." | `{ seed: n, tiles: 2400, enemies: <count>, items: <count> }` |
| `getState()` | Returns all record fields as plain data. | `{ player: {...}, enemies: [{...}, ...], items: [{...}, ...], mists: [{...}, ...], game: {...}, camera: {...} }` |
| `setMove(dx, dy)` | Sets the player's movement input. dx, dy are −1, 0, or 1. Persists until changed. (0, 0) stops. | `{ x: dx, y: dy }` |
| `spawnEnemy(kind, x, y)` | Creates a new ENEMY of the given kind at (x, y) with roster stats. active = true, spawn_delay = 0. | `{ id: <index>, kind: kind, x: x, y: y }` |
| `setPhase(p)` | Sets GAME.phase = p (1–4) and applies phase side-effects (spawn wraith, grow watcher auras). | `{ phase: p }` |
| `setLight(r)` | Sets PLAYER.light_radius = r (clamped 1.0–6.0). | `{ light: r }` |
| `setHealth(h)` | Sets PLAYER.health = h (clamped 0–5). If 0, sets GAME.state = "lost_health." | `{ health: h, state: GAME.state }` |
| `giveKey()` | Sets PLAYER.has_key = true. | `{ has_key: true }` |
| `openGate()` | Sets GAME.gate_open = true, changes gate tile to "exit." | `{ gate_open: true }` |
| `collectItem(kind)` | Finds the first uncollected ITEM of the given kind and marks it collected, applying its effect. | `{ collected: true, kind: kind }` or `{ collected: false }` |
| `setFear(f)` | Sets PLAYER.fear = f (clamped 0–100). | `{ fear: f }` |

# 9. TESTS

1. After `seed(42)`, `start()`: `getState().game.state === "playing"`, `getState().game.phase === 1`, `getState().player.x === 30`, `getState().player.y === 20`, `getState().player.health === 5`.

2. After `start()`, `step(1/60, 60)` (1 second): `getState().player.x` has changed from 30 (if `setMove(1, 0)` was called before step) or is still 30 (if no move was set). `getState().game.time_remaining` is approximately 299.0 (±0.1).

3. After `start()`, `setMove(1, 0)`, `step(1/60, 180)` (3 seconds east): `getState().player.x` is approximately 33.0 (30 + 3 × 3.0, ±0.5 for wall sliding).

4. After `start()`, `step(1/60, 600)` (10 seconds): `getState().player.light_radius` is approximately 4.78 (5.0 − 10/45, ±0.1).

5. After `start()`, `setTime(199)`: `getState().game.phase === 2`. `getState().enemies` includes at least 4 entries with kind "wraith" (3 original + 1 phase spawn).

6. After `start()`, `setTime(99)`: `getState().game.phase === 3`. All watcher ENEMIES have `aura_radius === 4.0`.

7. After `start()`, `setTime(29)`: `getState().game.phase === 4`.

8. After `start()`, `setTime(0)`, `step(1/60, 1)`: if the player is not on an exit tile, `getState().game.state === "lost_time"`.

9. After `start()`, `giveKey()`, `openGate()`, then manually place player on gate tile via `step` + `setMove` to reach it (or `setMove` and many steps): `getState().player.has_key === true`, the gate tile type in `getState()` is "exit."

10. After `start()`, `spawnEnemy("wraith", 32, 20)`, `step(1/60, 180)` (3 s): the wraith has moved toward the player (its x is < 32 if the player is at x=30, within ±0.5).

11. After `start()`, `spawnEnemy("shambler", 35, 20)`, `setMove(1, 0)`, `step(1/60, 300)` (5 s): the shambler is still on a walkable tile (its tile type in `getState()` is "path" or "ground"), confirming it does not pass through trees.

12. After `start()`, `spawnEnemy("watcher", 31, 21)`, `setMove(0, 1)`, `step(1/60, 120)` (2 s in the aura): `getState().player.health === 4` (one aura hit), `getState().player.invuln > 0`.

13. After `start()`, `collectItem("oil")`: `getState().player.light_radius` increased by 3.0 (or is 6.0 if it would have exceeded).

14. After `start()`, `collectItem("key")`: `getState().player.has_key === true`.

15. After `start()`, `collectItem("clue")`: `getState().player.has_clue_flash > 0`.

16. After `start()`, `setHealth(0)`: `getState().game.state === "lost_health"`.

17. After `start()`, `setFear(100)`, `step(1/60, 1)`: `getState().player.fear === 50`, `getState().player.light_radius` decreased by 2.0 (capped at 1.0).

18. After `seed(7)`, `start()`, `setTime(20)`, `step(1/60, 1)`: `getState().game.phase === 4`, `getState().enemies` are all active, all with phase-4 speed multipliers applied (verify by checking a wraith's speed field is 4.5).

19. After `start()`, `setMove(1, 0)`, `step(1/60, 3600)` (60 s of continuous east movement, will hit walls and stop): `getState().player.x` is ≤ 59 (clamped), player did not leave the world.

20. After `seed(100)`, `start()`: the key item in `getState().items` has kind "key" and its position is ≥ 6 tiles (Manhattan) from the nearest path tile (verified by checking its tile type is "ground" or "clear").

**SCREENSHOTS:**

| Screen / state | What a person must see |
|---|---|
| Title | Dark forest background (trees as dark shapes), "HAUNTED" in large serif, subtitle, "press any key" pulsing. No HUD. |
| Playing, Phase 1, player at start | Dark viewport, circular warm light around the player (5-tile radius), dirt path visible in the light, trees as dark silhouettes beyond, a faint warm glow on the east edge of the screen. HUD: 5 red pips, timer "05:00", "Deep Night", key icon dark. |
| Playing, Phase 2, wraith in range | A translucent pale-blue ghost visible in the light, drifting toward the player. The ambient drone is slightly louder. Timer shows ~03:20. Phase label "Restless." |
| Playing, Phase 4, dawn | The east edge glow is noticeably brighter (deep blue-purple). The ambient light radius is 2 tiles larger (you see further). All trees and enemies appear faster. Timer shows 00:25. Phase label "Dawn." |
| Playing, high fear | Dark vignette around the screen edges. Slight screen shake. The light circle is smaller. The vignette alpha is visible. |
| Gate, closed (no key) | An iron gate sprite on the path. The player bounces off it (cannot enter). The key icon in HUD is dark. |
| Gate, open (has key) | The gate sprite shows open (posts apart). The player walks through onto the exit tiles (dark road). A creak sound plays. |
| Won screen | A warm dawn gradient (deep blue → amber) fills the screen. "You escaped into the dawn." Time remaining shown. "R for a new forest." |
| Lost (time) | Black screen. "The forest swallowed you in the dark." "R to try again." |
| Lost (health) | Black screen with a faint red tint. "Your light went out." "R to try again." |

# 10. BUILD ORDER

**Milestone 1: Page opens, title shows, play starts.**
Add: the title screen, the 2D canvas, the update loop, the Camera system, a flat ground tile map (all "ground"), the player sprite at (30, 20) with WASD/arrows movement.
Check: Test 1 (seed, start, state is playing, player at 30/20).

**Milestone 2: Forest is generated and visible.**
Add: the Forest Generator (full: path, trees, water, rocks, clearings, gate, exit, items, enemies, mist). The Light & Visibility system (radial gradient, tiles outside light are black). The dawn glow band.
Check: Test 4 (light radius drains after 10 s). Screenshot: "Playing, Phase 1, player at start."

**Milestone 3: Enemies move and hurt.**
Add: the Enemy AI system (wraith chase, shambler patrol/chase, watcher aura). The Collision & Damage system. The Movement system for enemies. Health and invulnerability.
Check: Tests 10, 11, 12. Screenshot: "Playing, Phase 2, wraith in range."

**Milestone 4: Timer, phases, and the win/lose conditions.**
Add: the Timer & Dawn system (countdown, phase transitions, phase speed multipliers, dawn arrival, phase wraith spawn, watcher aura growth). The gate-open mechanic. The won / lost_time / lost_health end screens.
Check: Tests 5, 6, 7, 8, 9, 16, 18. Screenshot: "Playing, Phase 4, dawn" and "Won screen."

**Milestone 5: Items, key, clues, and oil.**
Add: the Item Pickup system. Oil (light restore), key (gate unlock), clue (direction arrow). The gate interaction.
Check: Tests 13, 14, 15. Screenshot: "Gate, open (has key)."

**Milestone 6: Fear, audio, and atmosphere (Tier 2).**
Add: the Fear system (fear meter, panic, vignette, screen shake). The Audio system (all sounds in Section 6). Mist patches. Enemy proximity sound. Heartbeat. Phase swell.
Check: Test 17. Screenshot: "Playing, high fear."

**Milestone 7: Polish (Tier 2 and 3 items in order).**
Add: screen shake on damage, clue arrow overlay, mist drift, firefly particles in clearings (T3), tree sway (T3), distant howl (T3).
Check: All tests 1–20 pass. All screenshot rows verified.

# 11. DONE

**"Explore a haunted forest at night"**
- Forest Generator places a 60×40 tile world with trees, paths, water, rocks, clearings, 8 enemies, 8 items, 6 mist patches. Tests 1, 20.
- Light & Visibility: the player sees only a 5-tile radius, the rest is black. Test 4. Screenshot: "Playing, Phase 1."
- Enemy AI: wraiths, shamblers, and watchers behave per their rules. Tests 10, 11, 12. Screenshot: "Playing, Phase 2."
- Atmosphere: ambient drone, footstep ticks, enemy proximity growl, heartbeat at high fear, phase swells. Screenshot: "Playing, high fear."

**"escape before dawn"**
- Timer & Dawn: 300-second countdown, 4 phases, dawn arrival at 0. Tests 5, 6, 7, 8. Screenshot: "Playing, Phase 4."
- Key and gate: the player must find the key, reach the gate, open it, and walk through. Tests 9, 13, 14. Screenshot: "Gate, open."
- Win: reaching an exit tile with time remaining shows the won screen. Test 8 (negative), Screenshot: "Won screen."
- Lose (time): timer hits 0 and the player is not on an exit tile. Test 8. Screenshot: "Lost (time)."
- Lose (health): health reaches 0. Test 16. Screenshot: "Lost (health)."

The game is finished when every line above is true and all 20 tests pass and all 10 screenshot rows are verified by a person.

# A. SANITY

- **Every field a rule reads or writes is on a record.**
  - PLAYER: x, y, speed, health, invuln, light_radius, max_light, has_key, has_clue_flash, fear, facing — all on PLAYER. ✓
  - ENEMY: x, y, kind, speed, aggro_radius, patrol_x0, patrol_x1, patrol_dir, patrol_y, aura_radius, aura_timer, drift_dir, drift_timer, active, spawn_delay — all on ENEMY. ✓
  - TILE: x, y, type — on TILE. ✓
  - ITEM: x, y, kind, collected — on ITEM. ✓
  - GAME: time_remaining, phase, gate_open, state, seed, gate_x, gate_y, key_x, key_y — on GAME. ✓
  - CAMERA: x, y — on CAMERA. ✓
  - MIST: x, y, dx, dy, radius — on MIST. ✓
  - Closes.

- **Every place, thing, or kind a rule names is placed by a generator or listed in a roster.**
  - Tile types: all 10 in the TILE roster, all placed by Forest Generator step 1–7. ✓
  - Enemy kinds: wraith, shambler, watcher — all in ENEMY roster, all placed by Forest Generator step 11. Phase-spawned wraith placed by Timer & Dawn. ✓
  - Item kinds: oil, key, clue — all in ITEM roster, all placed by Forest Generator steps 8–10. ✓
  - MIST: 6 placed by Forest Generator step 12. ✓
  - Gate and exit tiles: placed by Forest Generator step 3. ✓
  - Closes.

- **Consumable totals vs. core-loop demand.**
  - Oil: 4 placed. Max demand: the lantern drains from 5.0 to 1.0 (4 tiles) over 180 s. Each oil gives +3 tiles (cap 6). The player needs at most 4 tiles of refill to survive the full 300 s (drain of 6.67 tiles from 5.0 to min 1.0, then the lantern stays at 1.0). 4 oil × 3 tiles = 12 tiles of refill available. 12 ≥ 6.67. ✓
  - Key: 1 placed. Demand: 1 (to open the gate). 1 ≥ 1. ✓
  - Clues: 3 placed. Demand: 0 required (they are optional aids). ✓
  - Closes.

- **Timing pairs.**
  - Spawn vs. clear: the phase-2 wraith spawns at t=100 s (time_remaining = 200). The game lasts 300 s. The wraith has 200 s to be encountered. The player can reach the gate in ~120 s of movement (30 tiles at 3 tiles/s). The wraith's aggro radius is 6 tiles; it will intercept the player if it is within 6 tiles of the path. The player has 200 s to navigate around it or accept the hit. Closes.
  - Drain vs. refill: lantern drains 1 tile per 45 s. Full drain from 5 to 1 is 180 s. Oil refills +3 (cap 6). With 4 oil collected by t=120 s, the player has 5 + 12 = 17 tiles of total light budget, consuming at 1/45 per second = 765 s of light. 765 ≥ 300. ✓
  - Travel time vs. distance: player speed 3.0 tiles/s. Player start to gate is ~28 tiles (30 to 58). At 3 tiles/s, straight-line is ~9.3 s. With path meandering and enemy avoidance, realistic time is 60–120 s. The key is 6+ tiles off the path, adding ~10–20 s round trip. Total realistic time: 80–150 s. Timer is 300 s. 150 < 300. Closes with margin for the player to explore, search, and avoid enemies.
  - Watcher aura: 2 s in aura to trigger damage. Player speed 3.0 tiles/s. Watcher aura radius 3–4 tiles. The player crosses a 4-tile aura in ~1.3 s at full speed. The player must cross within 2 s to avoid the hit, which is feasible (1.3 < 2.0). If the player hesitates in the aura, they take the hit. Closes.
  - Closes.

-