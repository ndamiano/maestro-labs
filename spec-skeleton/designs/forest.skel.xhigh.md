# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Explore a haunted forest at night | Section 3, World module, Player module, Threats module |
| Escape before dawn | Section 4.5, Time module, Gate system, win/lose rules, Dawn timer in Global context |
| A playable browser game loop | Section 4, Core module, Debug module, UX module |
| Strong atmosphere and lighting | Section 3.2, Light module, Visual spec |
| Clear player goal and progression | Section 4.5, Objective system, three shard anchors, gate ritual |
| Survive threats while managing resources | Section 4.2, 4.3, 4.4, Player and Threats modules |
| Deterministic, testable state | Section 2.2, Section 8, Section 9 |
| Procedural audio | Section 6, Audio module |
| HTML/CSS-only UI | Section 7, UI module |
| Accessible and readable HUD | Section 7.2, UX module |

## 0.2 Tiers

| Tier | Features | Purpose |
| --- | --- | --- |
| T1 Must ship | Fixed 180-second dawn timer, player movement, forest collision, three shard anchors, gate ritual, win/lose, core HUD, core audio, debug seed/step/getState, deterministic world generation | The game must be complete and testable |
| T2 Core challenge | Flashlight battery, sanity drain, stamina, wraiths, hounds, watcher, phase-based spawns, battery and herb pickups, enemy light interaction | The core survival tension |
| T3 Atmosphere | Fog, flicker, sanity vignette, lore notes, ambience layers, camera shake, dawn visual, gate glow | Strong haunted-forest feel |
| T4 Polish | Settings, high contrast, reduced motion, colorblind mode, pause menu, optional map icon, tutorial hints, audio mixing presets | Quality of life and accessibility |

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Item | Value / rule |
| --- | --- |
| Coordinate system | World pixels. `x` increases right. `y` increases down. Top-left is `(0,0)`. |
| Simulation rate | Target 60 updates per second. Systems accept `dt` in seconds. |
| Tile size | 16 world pixels by 16 world pixels. |
| World size | 64 tiles wide by 48 tiles tall = 1024 x 768 world pixels. |
| View size | 320 x 240 world pixels. |
| Time unit | 1 real second = 1 game second. |
| Dawn time | 180 seconds from start to dawn. |
| Angle convention | Direction vectors use normalized world vectors. For cones, angle 0 points up, positive angle is clockwise. |
| Player collision radius | 5 world pixels. |
| Solid object radius | 6 world pixels for trees and rocks. |
| Pickup radius | 10 world pixels from player center. |
| Gate interact radius | 32 world pixels. |
| Gate ritual radius | 48 world pixels. |
| Enemy collision radius | 6 world pixels. |
| Sprite draw order | Sort by `y`, then `x`, so lower sprites draw over upper ones. |

## 1.2 Important conventions

- One shared context object holds every system’s state. Modules read and write only through that context.
- All randomness uses one seeded deterministic source. The random source is reset by `seed(n)`.
- World generation order is fixed: ground decor, trees, rocks, shrines, notes, pickups, baseline enemies.
- Anchor locations are fixed regardless of seed:
  - Player spawn: tile `(32,44)` = world `(520,712)`.
  - Gate: tile `(32,4)` = world `(520,68)`.
  - West shard: tile `(16,20)` = world `(264,332)`.
  - Central shard: tile `(32,12)` = world `(520,204)`.
  - East shard: tile `(48,24)` = world `(784,396)`.
- A carved corridor guarantees a path from spawn to west shard to central shard to east shard to gate. Total carved route length is at most 2048 world pixels.
- Solid trees and rocks never block anchor points, shard pickup radius, gate radius, or the carved route.
- Update order is fixed:
  1. Time and phase
  2. Player input and movement
  3. Enemy AI
  4. Pickups and objective interactions
  5. Light and battery
  6. Sanity
  7. Camera
  8. Audio events
  9. UI sync
- If status is `title`, `won`, or `lost`, gameplay updates stop. `step` may still advance nothing or only run state checks if the simulation was already ended.
- Moonlight is always visible but does not count as “bright” illumination for sanity. Flashlight and shrine flames are bright.
- Audio events set `audio.last` to the most recently triggered named event. If multiple events trigger in one tick, priority is: win/lose, shard, gate, enemy, pickup, player, ambience.

# 2. CONTRACTS

## 2.1 Module layout

| Owner | Responsibility |
| --- | --- |
| Core | Owns the context, fixed update loop, status transitions, reset, start, pause, and draw dispatch |
| RNG | Owns the seeded random source and deterministic random consumption order |
| World | Generates terrain, anchors, solids, shrines, notes, pickups, and path guarantees. Provides collision and line-of-sight checks |
| Player | Owns player movement, input state, stats, stamina, battery, sanity, pickup application, and interact action |
| Time | Owns dawn timer, phase changes, and dawn-based loss |
| Light | Owns flashlight state, light sources, illumination checks, flicker, and battery drain |
| Threats | Owns enemy roster, spawning, AI states, detection, movement, attacks, and light interaction |
| Objective | Owns shard count, gate state, ritual progress, and win condition |
| Audio | Owns procedural audio recipes, ambience, event sounds, and `audio.last` |
| UI | Reads context and updates HTML/CSS-only screens, HUD, prompts, settings, and accessibility options |
| Debug | Exposes `window.__game` functions for deterministic testing and state inspection |

## 2.2 Global context

### Constants

| Constant | Value | Meaning |
| --- | ---: | --- |
| `WORLD_W` | 1024 | World width |
| `WORLD_H` | 768 | World height |
| `TILE` | 16 | Tile size |
| `VIEW_W` | 320 | View width |
| `VIEW_H` | 240 | View height |
| `DAWN_TOTAL` | 180 | Seconds until dawn |
| `PLAYER_SPEED` | 80 | Walk speed |
| `SPRINT_SPEED` | 140 | Sprint speed |
| `STAMINA_MAX` | 100 | Maximum stamina |
| `STAMINA_DRAIN` | 10 | Stamina per second while sprinting |
| `STAMINA_REGEN` | 15 | Stamina per second while not sprinting |
| `BATTERY_MAX` | 100 | Maximum flashlight battery |
| `BATTERY_DRAIN` | 1 | Battery per second while flashlight is on |
| `BATTERY_PICKUP` | 50 | Battery added by a battery pickup |
| `SANITY_MAX` | 100 | Maximum sanity |
| `DARK_DRAIN` | 2 | Sanity per second when not brightly illuminated |
| `FLAME_REGEN` | 1 | Sanity per second when illuminated by a shrine flame |
| `HERB_RESTORE` | 30 | Sanity restored by drinking a herb |
| `CONE_LEN` | 90 | Flashlight cone length |
| `CONE_HALF_ANGLE` | 35 | Flashlight cone half-angle in degrees |
| `MOON_RADIUS` | 24 | Moonlight radius around player |
| `FLAME_RADIUS` | 60 | Shrine flame radius |
| `SHARD_REQUIRED` | 3 | Shards needed to open gate |
| `GATE_RITUAL_REQUIRED` | 2 | Seconds of ritual needed to win |
| `GATE_INTERACT_RADIUS` | 32 | Radius to interact with gate |
| `GATE_RITUAL_RADIUS` | 48 | Radius to maintain ritual |
| `PATH_MAX` | 2048 | Maximum carved route length in world pixels |

### Record fields

| Record | Fields |
| --- | --- |
| `state` | `status`, `t`, `phase`, `dawnRemaining`, `seed`, `lossReason`, `winReason`, `paused`, `shake`, `slowmo` |
| `rng` | `seed`, `state` |
| `camera` | `x`, `y` |
| `settings` | `volume`, `highContrast`, `reducedMotion`, `colorblind`, `subtitles` |
| `audio` | `last`, `ambience`, `pan`, `muted` |
| `flags` | `gatePrompt`, `shardPrompt`, `noteCount`, `lowSanity`, `ritualActive` |
| `player` | `x`, `y`, `dirX`, `dirY`, `sprinting`, `hp`, `maxHp`, `stamina`, `maxStamina`, `sanity`, `maxSanity`, `battery`, `maxBattery`, `shards`, `herbs`, `lightOn`, `invulnerableTimer`, `knockbackTimer` |
| `gate` | `x`, `y`, `open`, `ritual`, `ritualRequired`, `shardsRequired` |
| `shard` | `id`, `kind`, `x`, `y`, `taken` |
| `pickup` | `id`, `kind`, `x`, `y`, `amount`, `taken` |
| `solid` | `id`, `kind`, `x`, `y`, `radius`, `solid` |
| `light` | `id`, `kind`, `x`, `y`, `radius`, `intensity`, `active`, `flicker` |
| `enemy` | `id`, `kind`, `x`, `y`, `state`, `waypointX`, `waypointY`, `speed`, `hp`, `maxHp`, `detection`, `damage`, `attackRange`, `attackTimer`, `lightAversion`, `burn` |
| `world` | `solids`, `shrines`, `notes`, `trees`, `rocks`, `shards`, `pickups`, `enemies`, `lights` |

## 2.3 Module specifics

### Core

- `reset(seed) -> state`
  - Rebuilds world with `RNG`, sets `status = 'title'`, `t = 0`, `dawnRemaining = 180`, `phase = 1`, player at spawn, gate closed, ritual at 0.
- `start() -> { status }`
  - If `status === 'title'`, set `status = 'playing'`.
- `update(dt) -> state`
  - Runs fixed update order when `status === 'playing'`.
- `render() -> { t, status }`
  - Draws current context once.

### RNG

- `seed(n) -> { seed, state }`
- `next() -> number`
  - Returns deterministic value in `[0,1)`.

### World

- `build(seed) -> world`
  - Places anchors, carved route, solids, shrines, notes, pickups, and baseline enemies.
- `isSolid(x, y) -> boolean`
- `lineOfSight(x0, y0, x1, y1) -> boolean`
  - Returns false if the segment is blocked by a solid tree or rock.

### Player

- `updatePlayer(dt) -> player`
- `applyDamage(amount) -> { player, state }`
- `interact() -> { prompt }`
- `pickupCheck() -> { changed }`
- `drinkHerb() -> { changed }`

### Time

- `updateTime(dt) -> { phase, dawnRemaining, state }`
- `setPhase(n) -> { phase }`
  - Forces phase 1, 2, or 3 and ensures that phase’s enemy roster exists.

### Light

- `updateLight(dt) -> { player, lights }`
- `isBrightAt(x, y) -> boolean`
  - True if the point is inside flashlight cone or a shrine flame.

### Threats

- `ensurePhaseEnemies(phase) -> { enemies }`
- `updateEnemies(dt) -> { enemies, player }`
- `spawnEnemy(kind, x, y) -> enemy`
- `clearEnemies() -> { enemies }`

### Objective

- `updateObjective(dt) -> { gate, state }`
- `setGateOpen(open) -> gate`
- `setGateRitual(n) -> gate`

### Audio

- `play(name) -> { last }`
- `updateAudio(dt) -> audio`
  - Triggers footstep, low-battery, low-sanity, ambience, and enemy proximity events.

### UI

- `syncUI(state) -> void`
  - Updates HTML/CSS elements only. Does not draw on the game render surface.

# 3. VISUAL SPEC

The game is a top-down haunted forest rendered in a near-black blue palette with small pools of moonlight, drifting fog, and a narrow warm flashlight cone cutting through the dark. The forest feels alive but hostile: pine silhouettes and rocks form tight lanes, shrine flames pulse with green-gold light, shards glow cyan, and the gate rises at the top of the map like a broken stone arch. As night deepens, the edges of the screen become darker, the fog thickens, and sanity loss adds a faint red vignette. When the ritual begins, the gate runes glow bright amber, and at dawn a cold sunrise gradient rises across the map. The visual language is simple but high contrast: dark forest, bright light, glowing objective, and a clear sense of the player being small inside a large night.

## 3.1 Map and texture sets

| Surface / object | Visual rule |
| --- | --- |
| Ground base | Very dark moss blue-green, low detail, subtle noise |
| Path | Slightly lighter packed earth, narrow and organic, follows carved route |
| Tree | Dark pine silhouette with a small trunk shadow. Solid radius 6 |
| Rock | Dark gray angular mass with faint moonlit top edge |
| Shrine flame | Green-gold flame with soft radial glow, radius 60 |
| Shard | Cyan crystal with gentle pulse and small upward glow |
| Battery pickup | Small brass cell with yellow highlight |
| Herb pickup | Pale green leaf cluster |
| Note pickup | Faint white parchment glow |
| Gate | Stone arch with rune stones. Closed: dim. Open: amber rune glow |
| Wraith | Translucent pale blue will shape with trailing wisp |
| Hound | Black shadow silhouette with faint red eyes |
| Watcher | Tall thin dark figure with no face, visible mostly in fog |
| Player | Hooded nightkeeper figure with lantern, small warm outline when flashlight is on |

## 3.2 Lighting

| Light layer | Rule |
| --- | --- |
| Moonlight | Always-on soft radial light around player, radius 24, low intensity. Does not count as bright for sanity |
| Flashlight | Directional cone from player. Length 90, half-angle 35 degrees. Warm white. Counts as bright |
| Shrine flame | Radial light, radius 60, green-gold. Counts as bright and gives small sanity regen |
| Gate glow | Faint blue when closed. Amber when open. Strong amber pulse during ritual |
| Shard glow | Cyan radial light, radius 36, non-bright for sanity |
| Dawn gradient | Last 30 seconds, a thin blue-white gradient appears at top of world and slowly expands |
| Fog | Drifting translucent layer. Phase 1 target 0.2, phase 2 target 0.4, phase 3 target 0.6 |
| Sanity vignette | At sanity below 30, red-violet vignette at screen edges. At sanity below 15, pulse every 1.5 seconds |
| Flicker | Flashlight flickers when battery below 20 or phase is 2 or 3. Flicker is deterministic and does not affect test values unless battery is low |

## 3.3 Camera and post effects

- Camera centers on the player and clamps to world bounds.
- Camera shake: 0.15 seconds, 4 pixels, on player damage.
- Screen fade: 0.5 seconds on title, win, and loss.
- Reduced motion setting disables shake, fog drift, and sanity pulse.
- High contrast setting increases HUD bar contrast and adds outline around shards and gate.
- Colorblind setting changes shard cyan to orange and gate amber to purple.

# 4. GAMEPLAY SPEC

The most important part of playing is a tense loop of exploration, light management, and escape. The player must cross a dangerous forest, find three lantern shards, return to the gate, and complete a two-second ritual before the 180-second night ends. The challenge comes from darkness, limited flashlight battery, sanity loss in unlit areas, and enemies that hunt the player but are weakened or held by light. The player is not expected to kill enemies; the player is expected to observe, avoid, illuminate, and move.

## 4.1 Player Controller

| Control | Input | Rule |
| --- | --- | --- |
| Move | WASD or arrow keys | Sets desired direction. Debug uses `move(x,y)` |
| Sprint | Hold Shift | Increases speed to 140. Drains stamina. Makes noise |
| Flashlight | F or Space | Toggles flashlight. Requires battery above 0 |
| Interact | E | Opens gate if shards are available. Picks up notes |
| Drink herb | R | Restores 30 sanity if `herbs > 0` |
| Pause | Esc | Toggles pause. UI only |

Movement rules:

- Walk speed: 80 world pixels per second.
- Sprint speed: 140 world pixels per second.
- Stamina max: 100.
- Sprint drain: 10 per second.
- Stamina regen: 15 per second while not sprinting.
- If stamina reaches 0, sprinting stops until stamina is above 20.
- Collision: circle vs solids and world bounds. Movement is resolved axis-by-axis so the player can slide along obstacles.
- Direction vector updates only when movement input length is greater than zero. Otherwise the last direction persists.
- Default direction at start is `(0,-1)`.

## 4.2 Light and battery

- Battery max: 100.
- Initial battery: 100.
- Flashlight drain: 1 per second while on.
- If battery reaches 0, flashlight turns off.
- Battery pickup: +50, capped at 100.
- World places exactly four battery pickups.
- Total available battery in a normal run: 100 + 4 x 50 = 300.
- Always-on flashlight demand for full night: 180. Closes with margin.
- Flashlight cone:
  - Origin: player center.
  - Direction: player direction.
  - Length: 90.
  - Half-angle: 35 degrees.
  - Bright for sanity.
- Shrine flames:
  - Radius 60.
  - Bright for sanity.
  - Give 1 sanity per second while player is inside flame light.
- Moonlight:
  - Radius 24.
  - Visible only.
  - Not bright for sanity.

## 4.3 Sanity

- Sanity max: 100.
- Initial sanity: 100.
- Darkness drain: 2 per second when player is not in flashlight cone or shrine flame.
- Flame regen: 1 per second when player is in shrine flame light.
- Flashlight: no sanity drain while illuminated.
- Herb: restores 30 sanity. Max three herbs placed.
- Low sanity effects:
  - Below 30: player speed multiplied by 0.9, enemy detection increased by 30, UI vignette appears.
  - Below 15: heartbeat audio and vignette pulse.
- Sanity reaching 0 causes loss with reason `sanity`.

## 4.4 Threats

Enemy roster:

| Kind | HP | Speed | Detection | Damage | Attack range | Attack cooldown | Light aversion | Burn in cone |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wraith | 100 | 60 | 120 | 10 | 20 | 1.5 seconds | 1.0 | 5 per second |
| Hound | 120 | 90 | 140 | 15 | 24 | 1.5 seconds | 0.6 | 0 |
| Watcher | 150 | 50 | 160 | 20 | 28 | 1.5 seconds | 1.2 | 8 per second |

Spawn schedule:

| Phase | Time | Enemies present |
| --- | ---: | --- |
| 1 Night | 0-60 seconds | 2 wraiths |
| 2 Midnight | 60-120 seconds | 2 wraiths + 1 hound |
| 3 Pre-dawn | 120-180 seconds | 2 wraiths + 1 hound + 1 watcher |

Enemy AI states:

| State | Rule |
| --- | --- |
| Dormant | Does nothing. Used before spawn |
| Patrol | Moves between waypoint anchors at 0.6 x normal speed |
| Chase | Moves toward player at normal speed or slowed by light |
| Stunned | Stops for 1 second after taking enough burn to drop below 25% HP |
| Fleeing | Moves away from gate after third shard. Used only for cinematic calm |

Detection rules:

- Enemy detects player if:
  - Distance to player is less than detection range, and line of sight exists, or
  - Player is sprinting and distance is less than 160.
- If player sanity is below 30, enemy detection range increases by 30.
- If enemy loses player for 2 seconds, it returns to patrol.

Light interaction rules:

- If enemy is inside flashlight cone:
  - `lightAversion >= 1.0`: speed becomes 0 and enemy takes `burn` damage per second.
  - `lightAversion < 1.0`: speed is multiplied by `1 - lightAversion`.
- Enemies do not block movement. They apply damage on contact range.
- Attack:
  - If distance to player is less than attack range and `attackTimer <= 0`:
    - Deal damage.
    - Set `attackTimer = 1.5`.
    - Set player `invulnerableTimer = 0.5`.
    - Add camera shake.
    - Play damage audio.
- Enemy HP reaching 0 removes the enemy and plays dissipate audio.

## 4.5 Objectives, phase, and win/lose

Objective:

1. Find three lantern shards.
2. Return to the gate.
3. Interact with the gate.
4. Stay within 48 pixels of the gate for 2 seconds.
5. Escape before `dawnRemaining` reaches 0.

Gate rules:

- `gate.shardsRequired = 3`.
- `gate.ritualRequired = 2`.
- If player is within 32 pixels of gate:
  - If `player.shards < 3`, prompt is `Gate needs 3 shards`.
  - If `player.shards >= 3`, `gate.open = true` and ritual begins.
- Ritual:
  - While `gate.open` and player is within 48 pixels:
    - `gate.ritual += dt`.
  - If player leaves radius 48, `gate.ritual = 0`.
  - If `gate.ritual >= 2`, status becomes `won`.
- If third shard is picked up, all current enemies enter `patrol` and lose active chase state for 3 seconds.

Loss rules:

- `hp <= 0` -> loss reason `hp`.
- `sanity <= 0` -> loss reason `sanity`.
- `dawnRemaining <= 0` -> loss reason `dawn`, unless `gate.ritual >= 2` on the same tick, in which case win takes priority.

Phase changes:

| Phase | Time | Fog target | Audio ambience | Enemy change |
| --- | ---: | ---: | --- | --- |
| 1 | 0-60 | 0.2 | Night wind and creaks | Baseline wraiths |
| 2 | 60-120 | 0.4 | Add distant moans and creaks | Add hound |
| 3 | 120-180 | 0.6 | Add watcher whisper and rising dawn drone | Add watcher |

## 4.6 Pickups and notes

Pickups:

| Kind | Amount placed | Effect |
| --- | ---: | --- |
| `lanternShard` | 3 | Increases `player.shards` by 1 |
| `battery` | 4 | Adds 50 battery |
| `herb` | 3 | Adds 1 herb |
| `note` | 3 | Increases `flags.noteCount`. No win effect |

Pickup placement:

- Shards are at fixed anchors.
- Batteries are placed near west shard, central shard, east shard, and gate approach.
- Herbs are placed near the middle of each major route segment.
- Notes are placed off-route but reachable within 80 pixels of the carved path.

## 4.7 Balance timing

| Timing pair | Budget | Rule | Closes? |
| --- | ---: | --- | --- |
| Dawn vs escape route | 180 seconds | Carved route is at most 2048 pixels. At 80 px/s, minimum traversal is 25.6 seconds. With obstacles and enemies, target max is 120 seconds. | Closes |
| Battery drain vs battery pickups | 180 seconds always-on | Total battery 300. Always-on demand 180. | Closes |
| Sanity drain vs herbs and light | 180 seconds | Light prevents drain. If player is unlit constantly, herbs and flame regen are not enough, which is intended. Optimal play uses flashlight or flames. | Closes |
| Ritual vs dawn | 2 seconds | Gate ritual requires 2 seconds. Player must reach gate with at least 2 seconds remaining. | Closes |
| Enemy attack vs player movement | Attack cooldown 1.5 seconds, player speed 80 or 140 | Wraith and watcher are slower than sprint. Hound is faster but slowed 40% by light. | Closes |
| Spawn vs clear | Phase spawns at least 200 pixels from player at phase start | Spawn points are fixed and far from spawn. If a spawn point would be within 100 pixels of the player, it shifts to the next open anchor. | Closes |

# 5. CHARACTERS

The player is a quiet nightkeeper: a small hooded figure with a lantern, designed to feel fragile but careful. The enemies are not heroic monsters; they are fragments of the forest’s hunger. Wraiths drift like pale smoke and seem drawn to light but punished by it. Hounds are low, fast shadows that circle in the dark. The watcher is a rare, tall silhouette that appears mostly in fog and makes the player feel observed. All characters communicate through shape, light, motion, and sound rather than dialogue.

## 5.1 Animation pieces

| Character | Required states |
| --- | --- |
| Player | Idle, walk 4 directions, sprint 4 directions, damage, interact, drink |
| Wraith | Float idle, drift chase, burn flash, dissipate |
| Hound | Idle, run, snap, dissipate |
| Watcher | Drift idle, blink appear, fade out |
| Gate | Closed, opening, ritual pulse, dawn open |
| Shard | Pulse, picked-up sparkle |
| Shrine flame | Flame sway, flicker |

Animation constraints:

- Player walk cycle is 6 frames.
- Sprint cycle is 6 frames with wider steps.
- Wraith float is 8-frame looping pulse.
- Hound run is 8-frame looping gait.
- Watcher has no walk; it uses slow drift and occasional blink.
- Reduced motion setting reduces all looping animation to 50% speed and disables shake.

# 6. AUDIO

Generated with the Web Audio API.

| Sound | Recipe | Trigger rule |
| --- | --- | --- |
| `amb_night` | Filtered brown noise, 80-300 Hz, loop, low volume; add 55 Hz sine hum at -18 dB | Status playing and phase 1 |
| `amb_midnight` | `amb_night` plus sparse low creak, square wave 70 Hz, 0.2 second, random every 6-12 seconds | Phase 2 |
| `amb_predawn` | `amb_midnight` plus 49 Hz drone rising to 55 Hz over 10 seconds | Phase 3 |
| `footstep` | Short filtered noise burst, 0.05 seconds, 500 Hz lowpass, -24 dB | Every 0.45 seconds while walking, 0.28 seconds while sprinting |
| `flash_on` | Square click 1200 Hz, 0.03 seconds; add 120 Hz sine 0.1 seconds | Flashlight turns on |
| `flash_off` | Square click 700 Hz, 0.04 seconds | Flashlight turns off |
| `battery_low` | Soft tick, sine 800 Hz, 0.03 seconds | Every 0.5 seconds when battery below 20 and light on |
| `shard` | Two sine chimes, 660 Hz then 880 Hz, 0.4 seconds, gentle envelope | Shard picked up |
| `battery_pickup` | Brass click, triangle 440 Hz, 0.12 seconds | Battery picked up |
| `herb_pickup` | Soft leaf noise, bandpass 1000 Hz, 0.15 seconds | Herb picked up |
| `note_pickup` | Paper rustle, high noise, 0.2 seconds | Note interacted |
| `wraith_moa` | Detuned sine pair, 180 Hz and 185 Hz, 0.8 seconds, vibrato, lowpass 400 Hz | Wraith enters chase |
| `hound_snarl` | Noise burst plus sawtooth 110 Hz, 0.25 seconds | Hound enters chase |
| `watcher_whisper` | Bandpass noise, 0.6 seconds, slow amplitude wobble | Watcher appears or enters chase |
| `enemy_hit_light` | High shimmer, sine 1200 Hz, 0.1 seconds | Enemy takes burn damage in cone |
| `player_damage` | Low thump, sine 70 Hz, 0.2 seconds | Player takes damage |
| `sanity_low` | Heartbeat: sine 50 Hz, two pulses per 1.5 seconds | Sanity below 30 |
| `gate_closed` | Low stone tone, sine 80 Hz, 0.4 seconds | Player interacts with gate without enough shards |
| `gate_open` | Deep drone, sine 55 Hz, 0.6 seconds, rising fifth 88 Hz | Gate opens |
| `ritual` | Rising fifth, 220 Hz to 440 Hz over 2 seconds | Ritual active |
| `win` | Major chord, 262 Hz, 330 Hz, 392 Hz, 1.5 seconds | Win |
| `lose_dawn` | Low drone 49 Hz, 2 seconds, with brightening noise sweep | Loss by dawn |
| `lose_hp` | Low impact and dissonant minor second, 110 Hz and 116 Hz, 1.2 seconds | Loss by hp |
| `lose_sanity` | Unstable detuned sine, 220 Hz drifting 200-240 Hz, 1.5 seconds | Loss by sanity |

# 7. UX

UX is HTML/CSS only. The game render surface is not used for UI.

## 7.1 Screens

| Screen | Required content |
| --- | --- |
| Title | Game title, `Start` button, controls list, one-line goal, background forest still |
| Pause | Resume, Restart, Settings, Quit to title |
| Game Over | Loss reason, `Try Again` button, `Title` button |
| Win | Dawn visual, `Play Again` button, `Title` button, shard count and elapsed time |

## 7.2 HUD

| HUD piece | Rule |
| --- | --- |
| Vitals panel | Top-left. Four bars: HP, Sanity, Stamina, Battery |
| Objective panel | Top-center. Three shard icons. Filled when collected |
| Clock / phase | Top-right. Shows phase name and remaining dawn time as a shrinking night bar |
| Prompt line | Bottom-center. Shows `Interact: Gate`, `Gate needs 3 shards`, `Ritual in progress`, `Pick up note` |
| Minimap icon | Top-right small square. Shows player dot, gate dot, shard dots if high contrast or after 60 seconds |
| Settings menu | Volume slider, high contrast toggle, reduced motion toggle, colorblind toggle, subtitles toggle |
| Accessibility text | Subtitles line at bottom for important audio cues: enemy chase, gate ready, low sanity, low battery |

## 7.3 Controls legend

| Key | Action |
| --- | --- |
| WASD / Arrows | Move |
| Shift | Sprint |
| F / Space | Flashlight |
| E | Interact |
| R | Drink herb |
| Esc | Pause |

## 7.4 UX rules

- All HUD bars use clear labels and numeric values when hovered or focused.
- Low sanity, low battery, and low stamina add CSS pulse classes.
- Reduced motion disables CSS pulses and fade transitions.
- High contrast increases bar fill brightness and adds outline to objective icons.
- Colorblind mode changes shard icons from cyan to orange and gate runes from amber to purple.
- Buttons must be keyboard focusable and have visible focus rings.

# 8. DEBUG API

The game installs `window.__game`.

| Call | What it does | Returns |
| --- | --- | --- |
| `start()` | Enters play from title without a click | `{ status }` |
| `step(dt, n)` | Advances `n` ticks of `dt` seconds without waiting for real time, then draws once | `{ t, status }` |
| `setTime(t)` | Advances to `t` seconds without drawing | `{ t, status }` |
| `seed(n)` | Reseeds the one random source, rebuilds generated world and generators, resets to title at `t=0` | `{ seed, generated }` |
| `getState()` | Returns the fields of every record as plain data | full plain state |
| `move(x, y)` | Sets the player’s desired movement direction. Persists until changed. `(0,0)` stops movement | `{ x, y }` |
| `action(name)` | One call per action in the controls table. Names: `sprint`, `flashlight`, `interact`, `drink`, `pause` | `{ name, ok }` |
| `setPlayer(x, y)` | Moves player directly to a place | `{ x, y }` |
| `setLightOn(bool)` | Sets flashlight state directly | `{ lightOn }` |
| `setBattery(n)` | Sets player battery directly | `{ battery }` |
| `setSanity(n)` | Sets player sanity directly | `{ sanity }` |
| `setStamina(n)` | Sets player stamina directly | `{ stamina }` |
| `setHp(n)` | Sets player HP directly | `{ hp }` |
| `setShardCount(n)` | Sets player shard count directly | `{ shards }` |
| `setHerbCount(n)` | Sets player herb count directly | `{ herbs }` |
| `setDawnRemaining(n)` | Sets dawn timer directly | `{ dawnRemaining }` |
| `setPhase(n)` | Skips to phase 1, 2, or 3 and ensures phase enemies exist | `{ phase, enemies }` |
| `setFog(n)` | Sets fog level directly | `{ fog }` |
| `setGateOpen(bool)` | Sets gate open state directly | `{ open }` |
| `setGateRitual(n)` | Sets gate ritual seconds directly | `{ ritual }` |
| `spawnShard(x, y, kind)` | Spawns a shard at a place. Default kind is `lanternShard` | `{ id, x, y, kind }` |
| `spawnPickup(x, y, kind)` | Spawns a pickup at a place. Kinds: `battery`, `herb`, `note` | `{ id, x, y, kind }` |
| `spawnEnemy(kind, x, y)` | Spawns an enemy at a place. Kinds: `wraith`, `hound`, `watcher` | `{ id, kind, x, y }` |
| `clearEnemies()` | Removes all enemies | `{ enemies }` |
| `setEnemyState(id, state)` | Sets an enemy’s AI state directly | `{ id, state }` |
| `triggerAudio(name)` | Triggers a named audio event for tests | `{ last }` |

All calls are synchronous and return only plain data.

# 9. TESTS

Checks use only calls listed in Section 8.

1. Title and start.
   - `getState()` -> `state.status` is `'title'`.
   - `start()` -> `{ status: 'playing' }`.
   - `getState()` -> `state.status` is `'playing'`, `state.t` is `0`, `player.x` is `520`, `player.y` is `712`, `player.shards` is `0`, `gate.open` is `false`, `state.dawnRemaining` is `180`.

2. Straight movement.
   - `seed(1)`, `start()`, `setPlayer(520, 712)`, `move(0, -1)`, `step(1, 1)`.
   - `getState()` -> `player.x` is `520`, `player.y` is `632`, `state.t` is `1`, `state.status` is `'playing'`.

3. Sprint speed and stamina drain.
   - `seed(1)`, `start()`, `setStamina(100)`, `setPlayer(520, 712)`, `move(0, -1)`, `action('sprint')`, `step(1, 1)`.
   - `getState()` -> `player.y` is `572`, `player.stamina` is `90`, `player.sprinting` is `true`.

4. Flashlight battery drain.
   - `seed(1)`, `start()`, `setPlayer(520, 712)`, `setBattery(10)`, `setLightOn(true)`, `step(1, 1)`.
   - `getState()` -> `player.battery` is `9`, `player.lightOn` is `true`.

5. Darkness sanity drain.
   - `seed(1)`, `start()`, `setPlayer(520, 712)`, `setSanity(50)`, `setBattery(0)`, `setLightOn(false)`, `setFog(0)`, `step(1, 1)`.
   - `getState()` -> `player.sanity` is `48`.

6. Shard pickup and audio.
   - `seed(1)`, `start()`, `setPlayer(264, 332)`, `move(0, 0)`, `step(1, 1)`.
   - `getState()` -> `player.shards` is `1`, `world.shards[0].taken` is `true`, `audio.last` is `'shard'`.

7. Gate fails without three shards.
   - `seed(1)`, `start()`, `setShardCount(2)`, `setPlayer(520, 68)`, `action('interact')`, `step(1, 1)`.
   - `getState()` -> `gate.open` is `false`, `gate.ritual` is `0`, `flags.gatePrompt` is `'Gate needs 3 shards'`.

8. Gate ritual starts with three shards.
   - `seed(1)`, `start()`, `setShardCount(3)`, `setPlayer(520, 68)`, `action('interact')`, `step(1, 1)`.
   - `getState()` -> `gate.open` is `true`, `gate.ritual` is `1`, `flags.gatePrompt` is `'Ritual in progress'`.

9. Win by completing ritual.
   - `seed(1)`, `start()`, `setShardCount(3)`, `setPlayer(520, 68)`, `action('interact')`, `step(2, 1)`.
   - `getState()` -> `state.status` is `'won'`, `gate.ritual` is `2`, `state.dawnRemaining` is `178`.

10. Dawn loss.
   - `seed(1)`, `start()`, `setDawnRemaining(1)`, `step(1, 1)`.
   - `getState()` -> `state.status` is `'lost'`, `state.lossReason` is `'dawn'`.

11. Wraith chase movement.
   - `seed(1)`, `start()`, `clearEnemies()`, `setPlayer(520, 640)`, `setHp(100)`, `spawnEnemy('wraith', 520, 600)`, `step(1, 1)`.
   - `getState()` -> `world.enemies.length` is `1`, `world.enemies[0].x` is `520`, `world.enemies[0].y` is `620`, `world.enemies[0].state` is `'chase'`, `player.hp` is `100`.

12. Flashlight holds and burns wraith.
   - `seed(1)`, `start()`, `clearEnemies()`, `setPlayer(520, 640)`, `setBattery(100)`, `setLightOn(true)`, `spawnEnemy('wraith', 520, 600)`, `step(1, 1)`.
   - `getState()` -> `world.enemies[0].x` is `520`, `world.enemies[0].y` is `600`, `world.enemies[0].hp` is `95`, `player.battery` is `99`.

13. Battery pickup.
   - `seed(1)`, `start()`, `setPlayer(520, 712)`, `setBattery(60)`, `spawnPickup(520, 712, 'battery')`, `move(0, 0)`, `step(1, 1)`.
   - `getState()` -> `player.battery` is `100`, the spawned battery pickup’s `taken` is `true`.

14. Herb drink.
   - `seed(1)`, `start()`, `setPlayer(520, 712)`, `setSanity(40)`, `setBattery(100)`, `setLightOn(true)`, `spawnPickup(520, 712, 'herb')`, `move(0, 0)`, `step(1, 1)`.
   - `getState()` -> `player.herbs` is `1`, `player.sanity` is `40`, `player.battery` is `99`.
   - `action('drink')`.
   - `getState()` -> `player.herbs` is `0`, `player.sanity` is `70`.
   - `step(1, 1)`.
   - `getState()` -> `player.sanity` is `70`, `player.battery` is `98`.

15. Phase 2 enemy roster.
   - `seed(1)`, `start()`, `clearEnemies()`, `setPhase(2)`.
   - `getState()` -> `world.enemies.length` is `3`, at least one enemy kind is `'wraith'`, and at least one enemy kind is `'hound'`.

16. Fog setting.
   - `seed(1)`, `start()`, `setFog(0.6)`.
   - `getState()` -> `world.fog` is `0.6` or `state.fog` is `0.6`, depending on the chosen context field. The exposed state field is `fog`.

17. Battery audio.
   - `seed(1)`, `start()`, `setPlayer(520, 712)`, `spawnPickup(520, 712, 'battery')`, `move(0, 0)`, `step(1, 1)`.
   - `getState()` -> `audio.last` is `'battery_pickup'`.

18. HP loss.
   - `seed(1)`, `start()`, `setHp(0)`, `step(1, 1)`.
   - `getState()` -> `state.status` is `'lost'`, `state.lossReason` is `'hp'`.

19. Sanity loss.
   - `seed(1)`, `start()`, `setSanity(0)`, `step(1, 1)`.
   - `getState()` -> `state.status` is `'lost'`, `state.lossReason` is `'sanity'`.

20. Camera center.
   - `seed(1)`, `start()`, `setPlayer(520, 384)`, `move(0, 0)`, `step(1, 1)`.
   - `getState()` -> `camera.x` is `520`, `camera.y` is `384`.

21. Direct gate ritual.
   - `seed(1)`, `start()`, `setShardCount(3)`, `setPlayer(520, 68)`, `setGateOpen(true)`, `setGateRitual(2)`, `step(1, 1)`.
   - `getState()` -> `state.status` is `'won'`.

## SCREENSHOTS

| Named screen/state | What a person must see |
| --- | --- |
| Title | Dark forest background, title, Start button, controls list, no gameplay HUD |
| Playing after start | Player centered in lower forest area, flashlight off, battery bar full, shard icons empty, night bar near full |
| Sprint | Stamina bar decreasing, player silhouette shows faster walk cycle, no movement collision |
| Flashlight on | Warm cone visible in direction of player, battery bar decreasing, trees inside cone brighter than outside |
| Darkness sanity | No flashlight, no flame, red-violet vignette at edges, sanity bar decreasing |
| Shard pickup | Cyan shard disappears, one shard icon fills, small sparkle visible |
| Gate with two shards | Gate visible at top, prompt says `Gate needs 3 shards`, gate runes dim |
| Gate ritual | Gate runes amber, progress prompt visible, ritual glow intensifies |
| Win | Dawn gradient at top, gate fully glowing, win screen with play again button |
| Dawn loss | Sunrise gradient rising, player still outside gate, loss screen with dawn reason |
| Wraith chase | Wraith close to player, pale smoke visible, audio moan subtitle visible, player HP decreases if attacked |
| Flashlight holds wraith | Wraith frozen in cone, small burn shimmer, wraith HP decreases if visible in debug or high contrast |
| Phase 2 | Fog visibly thicker, at least one hound visible or subtitle/audio cue for new threat |
| High contrast | HUD bars bright, shard and gate outlines visible, objective icons outlined |

# 10. BUILD ORDER

1. Build context, constants, RNG, status states, and Core update loop.
2. Add Debug API: `seed`, `start`, `step`, `getState`, `move`, `action`, and basic setters.
3. Build World generation: anchors, carved route, solids, collision, line of sight, and fixed shard/gate positions.
4. Build Player movement, collision, direction, stamina, sprint, and camera.
5. Build Time and phase: dawn timer, phase changes, fog target, and dawn loss.
6. Build Light and battery: flashlight toggle, cone, shrine flames, battery drain, illumination checks.
7. Build Sanity and pickups: sanity drain, herbs, battery pickups, shard pickups.
8. Build Objective and gate: shard count, interact, ritual, win condition.
9. Build Threats: enemy roster, spawn schedule, detection, chase, patrol, attack, light interaction.
10. Build Audio recipes and event triggers.
11. Build HTML/CSS UX: title, HUD, prompts, game over, win, pause, settings.
12. Add visual polish: fog, flicker, sanity vignette, dawn gradient, camera shake, notes.
13. Run Section 9 checks and fix state fields, names, and timing until all pass.
14. Add accessibility settings and final balance pass.

# 11. DEFINITION OF DONE

| Header | Complete when |
| --- | --- |
| Core simulation | `seed`, `start`, `step`, `setTime`, and `getState` are deterministic. Title, playing, paused, won, and lost states work. Repeating the same debug sequence always produces the same state |
| World and map | 1024x768 forest renders. Anchors exist. Carved route is passable. Collision and line of sight work. Trees, rocks, shrines, shards, batteries, herbs, and notes are placed by generators |
| Player and resources | Movement, sprint, stamina, battery, sanity, flashlight, damage, and herb use all work. Player can die from HP or sanity |
| Objectives and win/lose | Three shards are required. Gate opens only with three shards. Ritual completes after 2 seconds. Win triggers before dawn. Dawn loss triggers at 180 seconds |
| Threats | Phase 1, 2, and 3 spawn the correct enemy roster. Enemies detect, chase, attack, and respond to light. Wraith and watcher are held by flashlight. Hound is slowed by flashlight |
| Audio | All required sounds trigger. Ambience changes by phase. `audio.last` is set by major events |
| UX | Title, HUD, prompts, pause, win, loss, and settings are HTML/CSS only. High contrast, reduced motion, colorblind, and subtitle options work |
| Debug and tests | Every Section 9 check passes using only Section 8 calls. No test relies on real time, hidden state, or unavailable functions |
| Visual polish | Night forest, flashlight cone, shrine light, fog, sanity vignette, dawn gradient, gate glow, and character readability are visible. Reduced motion disables disruptive movement |

# A. SANITY

- Record fields: closed. Added `flags`, `settings`, `audio`, `light`, and enemy `attackTimer` so every rule reads and writes only listed fields.
- Places and kinds: closed. Spawn, gate, shard, battery, herb, note, wraith, hound, and watcher are all placed by the world generator or enemy roster. No rule names an unplaced object.
- Consumables: closed. Initial battery 100 plus four battery pickups at 50 each gives 300 total battery against 180 seconds of always-on drain. Initial sanity 100 plus three herbs at 30 each gives 190 sanity capacity, and flashlight or shrine flame prevents the core sanity drain during the intended loop.
- Timing: closed. Dawn is 180 seconds. Carved route is at most 2048 pixels, under the player’s 80 px/s speed. Ritual is 2 seconds. Enemy attack cooldown is 1.5 seconds. Phase spawn points are at least 200 pixels from the player at phase start, or shifted if within 100 pixels.
- Debug calls: closed. Added `spawnPickup`, `clearEnemies`, `setGateRitual`, `setDawnRemaining`, `setPhase`, `setFog`, `setHp`, `setStamina`, and `setShardCount` so every Section 9 call exists in Section 8.
- Visual and state names: closed. Changed moonlight to be visible-only and not bright, so sanity drain tests are deterministic. Set enemy initial attack timer to 2.0 seconds so chase-movement tests do not accidentally include damage.