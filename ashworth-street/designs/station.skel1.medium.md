# BUILD SPEC: Derelict

## 0. SCOPE

### 0.1 Asked

- "Survive on a derelict space station" → Systems: Station Generator, Atmosphere, Power Grid, Drones, Radiation, Decompression Events, Resource Search, Door/Access, Escape/Launch, Rescue Timer; Records: Player, Drone, Tile, Station; Core Loop: explore, manage vitals, avoid threats, cross sections, reach pod bay.

### 0.2 Decisions

- **2D, top-down tile grid.** The player sees and navigates a flat map of rooms and corridors; the best version is a top-down exploration/survival game where the layout itself is the puzzle. No 3D camera, no depth axis.
- **Tile-based movement, 4-directional.** The player moves one tile at a time (0.2 s per tile). This makes drone encounters, door interactions, and line-of-sight deterministic and readable.
- **Five sections (decks) laid left to right.** The station is a gauntlet; progress is spatial. Section 1 (quarters, safe) to Section 5 (pod bay, goal). This gives the "survive and cross" tension without a level editor.
- **Scarcity, not abundance.** O2, power, and health all drain passively. The player must constantly trade exploration for resource foraging. No infinite stash.
- **Drones as the primary active threat.** No shooting. The player avoids, lures, or spends repair parts to disable. This keeps the loop tense rather than action-y.
- **Two win conditions.** Escape (reach and launch the pod) or Rescue (survive 600 s). Losing is death (oxygen or health hits 0).
- **One random source.** A single seeded PRNG drives all generation and all "random" gameplay events (loot rolls, decompression location, drone patrol paths). No unseeded Math.random anywhere.

### 0.3 Tiers

**TIER 1 (the game):** Station Generator, Player Movement, Atmosphere, Power Grid, Drones, Radiation, Resource Search, Door/Access, Escape/Launch, Fog of War, Rescue Timer.

**TIER 2 (makes it good, in order):**
1. Decompression Events — random atmosphere loss adds unpredictability.
2. Hunger — health drain after 60 s forces food management.
3. Drone Alarm — 3+ chasing drones trigger a station-wide lights-out.
4. Forced-door mechanic — desperate escape route when power is low.
5. Scan action — reveals off-screen resources and drone positions (costs power).

**TIER 3:**
1. Ambient drone sound design (dripping, groaning hull).
2. Multiple drone types (fast scout, slow heavy) in later sections.

## 1. CONVENTIONS

**Units and scale.** One tile = 32×32 pixels on screen. The station grid is 45 columns × 30 rows (1440×960 px total). The viewport is 800×608 px (25×19 tiles), centered on the player.

**Axes.** Tile column increases rightward (x-axis, 0 = left edge of station). Tile row increases downward (y-axis, 0 = top of station). "Up" on screen is row 0. The player faces N (row −1), S (row +1), E (col +1), or W (col −1).

**Origin.** (0,0) is the top-left tile of the station.

**Update loop.** Fixed step dt = 1/60 s. Systems run in this order each tick: 1. Input/Move, 2. Drone AI, 3. Atmosphere drain, 4. Power drain, 5. Radiation check, 6. Decompression events, 7. Combat/collision, 8. Win/Loss check. Render after all systems complete.

**Randomness.** One seeded PRNG named `rng` (mulberry32 or equivalent). Every "random" choice in the game calls `rng()`. No other source of randomness exists. The seed is set by the player (debug) or defaulted to 42.

**Controls (keyboard):**

| Input | Action |
|-------|--------|
| W / ArrowUp | Face and move North |
| S / ArrowDown | Face and move South |
| A / ArrowLeft | Face and move West |
| D / ArrowRight | Face and move East |
| E | Interact: search tile, use door, disable drone, prime pod |
| 1–8 | Use item in inventory slot 1–8 |
| Q | Activate scan (T2) |
| F | Force locked door (T2) |
| Escape | Pause / open menu |

**Touch (if applicable):** Left half of screen = virtual d-pad (4 directions). Right half: tap = E (interact). Two-finger tap = use first available O2 canister. (Touch is secondary; the game is playable on keyboard alone.)

## 2. RECORDS

RECORDS: TILE, ROOM, PLAYER, DRONE, STATION, ITEM, LOOT

**TILE:** column (int, 0–44), row (int, 0–29), type (enum: WALL, FLOOR_CORRIDOR, FLOOR_ROOM, DOOR_LOCKED, DOOR_UNLOCKED, RADIATION, POD_TILE), room_id (int, −1 if corridor/wall), searched (bool, start false), explored (bool, start false), decompressed_until (float seconds, start 0).

**ROOM:** id (int, 0–N), section (int, 1–5), type (enum: STORAGE, LAB, MED_BAY, ENGINE, QUARTERS, BRIDGE, AIRLOCK, POD_BAY), col_start (int), row_start (int), col_end (int), row_end (int), loot_remaining (int, start 2–4), access_card_here (bool, start false).

**PLAYER:** x (int, tile col), y (int, tile row), facing (enum: N, S, E, W), oxygen (float 0–100, start 100), health (float 0–100, start 100), power (float 0–100, start 50), inventory (array of 8, each ITEM or null, start all null), access_cards (int 0–3, start 0), repair_parts (int 0–5, start 0), food_rations (int 0–3, start 0), hunger_timer (float seconds, start 60), alive (bool, start true), moving (bool, start false), move_cooldown (float s, start 0), action_cooldown (float s, start 0), scan_active (bool, start false).

**DRONE:** id (int, 0–14), x (int), y (int), section (int, 1–5), state (enum: PATROL, ALERT, CHASE, DISABLED), patrol_path (array of [col,row], 6–12 entries), patrol_index (int, start 0), alert_timer (float s, start 0), chase_stuck_timer (float s, start 0), last_known_player (int pair, start [0,0]), hit_cooldown (float s, start 0).

**STATION:** power (float 0–100, start 100), decompression_timer (float s, start 45), alarm_active (bool, start false), alarm_timer (float s, start 0), time (float s, start 0), rescued (bool, start false), escaped (bool, start false), gameOver (bool, start false).

**ITEM:** type (enum: O2_CANISTER, POWER_CELL, MED_KIT, FOOD_RATION, REPAIR_PART, ACCESS_CARD).

**LOOT:** room_id (int), item_type (ITEM.type), found (bool, start false).

**Item effect table:**

| Item type | Effect on use | Slot consumed? |
|-----------|--------------|----------------|
| O2_CANISTER | oxygen += 30 (cap 100) | yes |
| POWER_CELL | STATION.power += 40 (cap 100) | yes |
| MED_KIT | health += 25 (cap 100) | yes |
| FOOD_RATION | health += 15 (cap 100); hunger_timer reset to 60 | yes |
| REPAIR_PART | (not directly usable; consumed by drone-disable or pod-prime) | no, tracked separately |
| ACCESS_CARD | access_cards += 1 (max 3); slot freed | yes |

**Room loot table (what a search in that room type yields, one item per search):**

| Room type | Item distribution (weight) |
|-----------|---------------------------|
| STORAGE | O2_CANISTER 4, POWER_CELL 3, FOOD_RATION 2, REPAIR_PART 1 |
| LAB | REPAIR_PART 5, POWER_CELL 2, O2_CANISTER 2 |
| MED_BAY | MED_KIT 5, FOOD_RATION 3, O2_CANISTER 2 |
| ENGINE | POWER_CELL 6, REPAIR_PART 3, ACCESS_CARD 1 |
| QUARTERS | FOOD_RATION 4, O2_CANISTER 3, MED_KIT 2, ACCESS_CARD 1 |
| BRIDGE | ACCESS_CARD 5, POWER_CELL 3, REPAIR_PART 2 |
| AIRLOCK | O2_CANISTER 4, REPAIR_PART 3, MED_KIT 3 |
| POD_BAY | (not searchable) |

## 3. SYSTEMS

SYSTEMS: Station Generator, Player Movement, Atmosphere, Power Grid, Drones, Radiation, Resource Search, Door/Access, Escape/Launch, Fog of War, Rescue Timer, Decompression Events, Hunger, Drone Alarm, Scan

### Station Generator (T1)

SEEDED GENERATOR. Parameters: seed (int).

Procedure:
1. Initialize a 45×30 grid of WALL tiles.
2. For each section s (1 through 5), define its column range: section 1 = cols 0–8, section 2 = cols 9–17, section 3 = cols 18–26, section 4 = cols 27–35, section 5 = cols 36–44.
3. In each section's 9×30 area, place 4–6 rooms (rectangles, 3–6 cols × 3–5 rows, non-overlapping, at least 1-tile gap between rooms). Room type assignment: Section 1 must contain at least one QUARTERS. Section 5 must contain exactly one POD_BAY. Other rooms are chosen from the remaining types with at least one STORAGE, one MED_BAY, and one ENGINE per section (fill remaining slots with random types).
4. Carve all room floors as FLOOR_ROOM. Carve corridors (1-tile wide) connecting all rooms within a section using BFS from each room's center to the next, carving FLOOR_CORRIDOR. Corridors between sections: carve a 2-tile-wide corridor through the boundary wall (cols 8/9, 17/18, 26/27, 35/36) at 2 random rows (one upper half, one lower half) within that section.
5. Place DOOR_LOCKED tiles: 2 per section boundary (the 2 corridor tiles at the boundary). Section 1's left boundary (col 0) is solid wall (no exit). Section 5's right boundary (col 44) is solid wall.
6. Place RADIATION tiles: in each section, pick 3–8 corridor tiles (not in rooms, not at door positions) and set type to RADIATION.
7. Place 3 DRONE records per section (15 total). Each drone: position = a random corridor tile in that section. Patrol path = a loop of 6–12 corridor tiles (walkable, same section). State = PATROL.
8. For sections 1–4, pick one room of type STORAGE, LAB, or ENGINE (if none, any room) and set access_card_here = true; place a LOOT record with item_type ACCESS_CARD in that room, guaranteed found = false.
9. Assign loot_remaining = 2 + floor(rng()×3) (i.e., 2–4) to each room. Populate LOOT records: for each loot slot, roll the room's loot table to assign an item_type. (The guaranteed access card in steps 8 is one of these slots.)
10. Place the POD_TILE: in the POD_BAY room, one central tile is marked POD_TILE.
11. Player start: the first QUARTERS room in section 1, center tile. Player.x, Player.y set there. Player.facing = E.
12. All tiles start explored = false, searched = false, decompressed_until = 0.

VERIFIER: (a) Every room in every section is reachable from the player's start tile via FLOOR_CORRIDOR, FLOOR_ROOM, or DOOR_UNLOCKED paths (DOOR_LOCKED are passable for reachability check). (b) The POD_TILE is reachable from player start. (c) No two rooms overlap. (d) Each section has exactly 3 drones. (e) Sections 1–4 each have exactly 1 ACCESS_CARD loot. (f) Total tile count of FLOOR_CORRIDOR + FLOOR_ROOM ≥ 200. Re-roll with the next seed if any check fails.

### Player Movement (T1)

RULE M1: If a direction key is held and Player.move_cooldown ≤ 0 and Player.alive = true: set Player.facing to that direction. Compute dest = (x, y) + facing vector. If dest tile type is FLOOR_CORRIDOR, FLOOR_ROOM, DOOR_UNLOCKED, RADIATION, or POD_TILE: set Player.x, Player.y to dest; set Player.move_cooldown = 0.2; set Player.moving = true. If dest is DOOR_LOCKED: if Player.access_cards ≥ 1, consume 1 card, set tile to DOOR_UNLOCKED, move into it. Else: do not move (blocked). If dest is WALL: do not move.

RULE M2: At the start of each tick, decrement Player.move_cooldown by dt. If ≤ 0, set Player.moving = false.

RULE M3: If no direction key is held for 2 consecutive ticks, set Player.moving = false (idle).

### Atmosphere (T1)

RULE A1: Each tick, compute drain rate: if Player's tile is RADIATION or decompressed_until > STATION.time: drain = 1.0. Else if Player's tile is FLOOR_CORRIDOR: drain = 0.5. Else (FLOOR_ROOM in a section with STATION.power > 0): drain = 0.2. Else (FLOOR_ROOM with STATION.power = 0): drain = 0.5. Set Player.oxygen = max(0, Player.oxygen − drain × dt).

RULE A2: If Player.oxygen ≤ 0: set Player.health = max(0, Player.health − 5.0 × dt).

RULE A3: If Player.oxygen > 50 and Player.health < 100: set Player.health = min(100, Player.health + 1.0 × dt) (natural regen when well-oxygenated).

### Power Grid (T1)

RULE P1: Each tick, set STATION.power = max(0, STATION.power − 0.3 × dt).

RULE P2: If the player uses a POWER_CELL item (key 1–8 on the slot): set STATION.power = min(100, STATION.power + 40); remove item from slot.

RULE P3: Fog radius = 3 + floor(STATION.power / 25). (At power 100: radius 7. At power 0: radius 3.) This value is read by the Fog of War system.

### Drones (T1)

RULE D1 (PATROL): Each tick, if drone.state = PATROL: advance along patrol_path by patrol_index. Move 1 tile every 0.4 s (accumulate a per-drone timer). When patrol_index reaches end, wrap to 0.

RULE D2 (Detection): Each tick, for each drone with state = PATROL or ALERT: compute Manhattan distance to player. If distance ≤ 6 AND line-of-sight is clear (no WALL or DOOR_LOCKED tiles in the straight N/S/E/W line from drone to player; only one axis is non-zero at a time for 4-dir check — check horizontal or vertical only): set drone.state = ALERT; set drone.alert_timer = 1.0; set drone.last_known_player = (Player.x, Player.y).

RULE D3 (ALERT): Each tick, if drone.state = ALERT: decrement alert_timer by dt. If alert_timer ≤ 0: if player is still within 6 tiles with LOS → set state = CHASE. Else → set state = PATROL (resume patrol from current position, find nearest patrol_path tile).

RULE D4 (CHASE): Each tick, if drone.state = CHASE: move 1 tile toward Player position (BFS step, 1 tile per 0.3 s, per-drone timer). If the drone's tile equals Player's tile: set Player.health = max(0, Player.health − 10); set drone.state = ALERT; set drone.alert_timer = 1.0; set drone.hit_cooldown = 1.0. If Player is > 12 tiles away: increment chase_stuck_timer by dt; if chase_stuck_timer ≥ 3: set state = PATROL, reset chase_stuck_timer. Else: reset chase_stuck_timer to 0.

RULE D5 (Disable): If player presses E while on a tile adjacent (Manhattan distance 1) to a drone with state ALERT or CHASE, and Player.repair_parts ≥ 1, and Player.action_cooldown ≤ 0: consume 1 repair part; set Player.action_cooldown = 1.0; set drone.state = DISABLED.

RULE D6 (hit_cooldown): A drone in ALERT with hit_cooldown > 0 does not re-detect the player for that duration. Decrement by dt each tick.

### Radiation (T1)

RULE R1: Each tick, if Player's tile type is RADIATION: set Player.health = max(0, Player.health − 3.0 × dt); set Player.oxygen = max(0, Player.oxygen − 0.5 × dt) (additional drain on top of A1).

### Resource Search (T1)

RULE S1: If player presses E and Player.action_cooldown ≤ 0 and the current tile is FLOOR_ROOM and the tile's room has loot_remaining > 0 and the tile's searched = false: set Player.action_cooldown = 1.0. Roll the room's loot table (weighted, using rng) to determine item_type. If the room has a guaranteed ACCESS_CARD loot that is not yet found and rng() < 0.3, yield ACCESS_CARD instead. Place the item in the first empty inventory slot (if no empty slot, item is lost). Set tile.searched = true. Decrement room.loot_remaining by 1. Mark the corresponding LOOT record as found.

RULE S2: If Player.action_cooldown > 0, the player is stationary (cannot move) for the remaining duration.

### Door/Access (T1)

RULE DO1: A DOOR_LOCKED tile blocks movement (see M1). If the player has ≥ 1 access card and moves into it: consume 1 card, set tile to DOOR_UNLOCKED, proceed.

RULE DO2 (Forced door, T2): If the player presses F while adjacent to a DOOR_LOCKED tile and STATION.power < 30: set Player.action_cooldown = 2.0; set Player.health = max(0, Player.health − 20); set tile to DOOR_UNLOCKED. (A desperate, costly escape.)

### Escape/Launch (T1)

RULE EL1: If the player is on the POD_TILE and presses E, and Player has ≥ 2 repair_parts and ≥ 1 POWER_CELL in inventory, and STATION.power ≥ 20: set Player.action_cooldown = 5.0 (priming). After 5 s of stationary time on the POD_TILE: set STATION.escaped = true; set STATION.gameOver = true.

RULE EL2: If conditions are not met, pressing E on POD_TILE does nothing (no priming).

### Fog of War (T1)

RULE F1: Each tick, compute fog radius from P3. For all tiles within Chebyshev distance ≤ fog_radius of (Player.x, Player.y): set tile.explored = true. These tiles are rendered at full brightness with entities visible.

RULE F2: Tiles with explored = true but outside current fog radius: rendered at 40% brightness (layout visible, entities not shown).

RULE F3: Tiles with explored = false: not rendered (black).

RULE F4: If STATION.alarm_active (T2): override fog radius to 1 for all tiles.

### Rescue Timer (T1)

RULE RT1: Each tick, set STATION.time += dt. If STATION.time ≥ 600 and Player.alive: set STATION.rescued = true; set STATION.gameOver = true.

### Decompression Events (T2)

RULE DE1: Each tick, decrement STATION.decompression_timer by dt. When it reaches 0: pick a random corridor tile (using rng) in a random section; set a linear strip of 5–8 adjacent corridor tiles (horizontal or vertical) to decompressed_until = STATION.time + 20. Reset STATION.decompression_timer = 45.

RULE DE2: Each tick, for all tiles where decompressed_until > 0 and decompressed_until ≤ STATION.time: reset decompressed_until = 0 (event ended). Tiles with decompressed_until > STATION.time are treated as "decompressed" for Atmosphere rule A1.

### Hunger (T2)

RULE H1: Each tick, decrement Player.hunger_timer by dt. If Player.hunger_timer ≤ 0: set Player.health = max(0, Player.health − 0.1 × dt). (Sustained low drain after 60 s without food.)

RULE H2: Using a FOOD_RATION resets Player.hunger_timer to 60.

### Drone Alarm (T2)

RULE DA1: Each tick, count drones with state = CHASE. If count ≥ 3 and STATION.alarm_active = false: set STATION.alarm_active = true; set STATION.alarm_timer = 10.

RULE DA2: Each tick, if STATION.alarm_active: decrement alarm_timer by dt. If alarm_timer ≤ 0: set alarm_active = false. While active, fog radius is overridden to 1 (F4).

### Scan (T2)

RULE SC1: If player presses Q and Player.power ≥ 10 and Player.action_cooldown ≤ 0: set Player.power = Player.power − 10; set Player.action_cooldown = 1.0; set Player.scan_active = true. For 1 tick: reveal all drone positions (render them on the minimap/HUD even if outside fog) and all unsearched loot tiles within 10 tiles of the player (show as a faint glint). After the tick, set scan_active = false.

## 4. CORE LOOP

Each minute of play: the player moves through corridors and rooms, watching oxygen and power drain. They search room tiles for items (E key), collect O2 canisters and power cells to stave off depletion. Drones patrol and may spot the player; the player backs off, lures them into radiation, or spends a repair part to disable one. Every 45 s a decompression event threatens a corridor. The player must reach the next section's locked door, spend an access card, and continue.

What grows: the player's stock of items, their knowledge of the map (explored tiles accumulate), and their position toward Section 5. What unlocks: each new section has more drones, more radiation, different room types, and scarcer resources. The end: reaching and priming the pod (escape) or surviving 600 s (rescue). Death (oxygen or health = 0) ends the run. There is no infinite mode; every run has a defined end.

## 5. SCREENS

**State machine:** title (station exterior art, "DERELICT" title, "Press E to begin", seed input field) → playing (the game) → paused (overlay: Resume, Restart with seed, Abandon) → game_over (cause of death or escape/rescue, stats: time survived, sections reached, drones disabled, items used; "Press E to return to title").

Transitions:
- Title: E key → playing.
- Playing: Escape → paused.
- Paused: Escape or R → playing (resume). N → restart (reseed, back to playing). Q → title.
- Playing: Player.alive = false or STATION.gameOver = true → game_over.
- Game_over: E → title.

**HUD (bottom bar, 45 px tall, below the viewport):**

| Element | Record field shown |
|---------|-------------------|
| O2 bar (green, 100 px) | Player.oxygen / 100 |
| Health bar (red, 100 px) | Player.health / 100 |
| Power bar (blue, 80 px) | STATION.power / 100 |
| Portable power (small blue, 40 px) | Player.power / 100 |
| Inventory strip (8 slots, 32 px each) | Player.inventory[0..7] item icons |
| Access cards (icon × count) | Player.access_cards |
| Repair parts (icon × count) | Player.repair_parts |
| Section indicator (1–5) | Current section of Player.x |
| Timer (mm:ss) | STATION.time |
| Hunger indicator (flash when < 10 s) | Player.hunger_timer |

## 6. AUDIO

Generated with Web Audio API. All sounds are synthesized; no audio files.

| Sound name | Recipe (waveform, freq, duration, envelope) | Trigger rule |
|------------|---------------------------------------------|--------------|
| step | Square, 80 Hz, 0.05 s, sharp attack/decay | Each successful tile move (M1) |
| search | Triangle, 220 Hz → 440 Hz sweep, 0.3 s, linear attack/decay | S1 (successful search) |
| drone_alert | Sawtooth, 440 Hz, 0.4 s, sharp attack, fast decay | D2 (drone enters ALERT) |
| drone_hit | Square, 60 Hz, 0.15 s, sharp attack/decay | D4 (drone contacts player) |
| o2_use | Sine, 600 Hz → 200 Hz, 0.2 s, decay | A3 / using O2_CANISTER |
| power_use | Sine, 300 Hz → 500 Hz, 0.3 s, linear | P2 (using POWER_CELL) |
| door_unlock | Square, 200 Hz → 400 Hz, 0.2 s, sharp | DO1 (card used on door) |
| decompression | Sawtooth, 100 Hz, 1.0 s, slow attack, slow decay | DE1 (event triggers) |
| alarm | Square, 800 Hz, 0.2 s, repeated 3× | DA1 (alarm triggers) |
| pod_prime | Sine, 200 Hz → 800 Hz, 4.0 s, slow linear | EL1 (priming countdown) |
| death | Sine, 400 Hz → 50 Hz, 1.5 s, decay | Player.alive → false |
| rescue | Sine, 400 Hz → 800 Hz → 1200 Hz, 2.0 s, linear | RT1 (rescue triggers) |
| hunger_warning | Triangle, 300 Hz, 0.1 s, soft | H1 (hunger_timer < 10, once per cycle) |

## 7. ART

**AI art (one image per distinct subject):**

- Ask for **a top-down view of a derelict space station exterior in deep space, dim red emergency lighting, hull damage, stars in background, dark palette** as a **scene** (title screen background, 800×608 px).
- Ask for **a small astronaut figure seen from directly above, white suit with orange accents, backpack, in a neutral pose** as a **sprite** (player idle, 32×32 px). One image, single subject.
- Ask for **the same astronaut from above, leaning forward, one arm extended** as a **sprite** (player moving, 32×32 px). Combined with the idle, this is a 2-frame anim. The player faces the movement direction; the game rotates the sprite 0°, 90°, 180°, 270° in code for the four directions.
- Ask for **a small industrial maintenance drone seen from above, angular metal body, a single red sensor eye, four short legs, dim** as a **sprite** (drone, 32×32 px). Rotate in code for facing. A DISABLED drone is rendered with a grey overlay in code (no separate art).

**Everything else is drawn in code:**

- RECIPE: Tile rendering. Each tile is a 32×32 px rectangle. WALL: fill #1a1a2e, 1 px border #2a2a4e. FLOOR_CORRIDOR: fill #16213e, no border. FLOOR_ROOM: fill varies by room type — STORAGE #1a2a1a, LAB #1a1a3e, MED_BAY #2e1a1a, ENGINE #2e2e1a, QUARTERS #2e1a2e, BRIDGE #1a2e2e, AIRLOCK #2e2e2e, POD_BAY #1a2e1a. DOOR_LOCKED: fill #3e1a1a, 2 px red border. DOOR_UNLOCKED: fill #1a3e1a, 2 px green border. RADIATION: fill #2e3e00, 1 px yellow border, animated 1-px green pulse (sin(time×4) alpha on a #4e7e00 overlay). POD_TILE: fill #1a2e1a, 2 px white border, small white circle center.
- RECIPE: Fog of war. Unexplored tiles: #000000. Explored-but-outside-fog: tile color at 40% opacity over #000000. In-fog: full color.
- RECIPE: HUD bars. Background #0a0a0a. Bar fill: O2 #2e8b57, Health #cd2e2e, Power #2e5ecd, Portable power #5e8ecd. Bar border #333333, 1 px.
- RECIPE: Inventory slots. 32×32 px, #0a0a0a fill, #333 border. Item icons: O2_CANISTER — green circle with "O₂" text 8 px. POWER_CELL — blue rectangle with lightning glyph. MED_KIT — white square with red cross. FOOD_RATION — brown rectangle. REPAIR_PART — grey gear shape (circle with 6 teeth). ACCESS_CARD — yellow rectangle with a dot.
- RECIPE: Drone rendering. 32×32 sprite (AI art) rotated to facing. State overlays: PATROL — no overlay. ALERT — 1-px yellow border around tile. CHASE — 1-px red border + red sensor dot pulsing. DISABLED — sprite drawn at 50% opacity, grey overlay.
- RECIPE: Decompressed tiles. Tile color with a #4488ff overlay at 30% opacity, animated 1-px cyan shimmer (sin(time×6)).
- RECIPE: Radiation visual (per tile, see above).
- RECIPE: Scan effect (T2). For 1 tick when scan active: all drone positions show as a 4×4 red square (16×16 px) on the HUD minimap; loot tiles within 10 show a 2×2 yellow pixel glint.

Everything else — tile fills, borders, fog, HUD bars, item icons, drone state overlays, decompression shimmer, scan glints, text labels, the minimap (a 45×30 scaled to 135×90 px in the HUD corner, one pixel per tile, color-coded) — is drawn in code.

## 8. DEBUG API

The game installs `window.__game` with these functions:

| Call | What it does | Returns |
|------|-------------|---------|
| `start()` | Enters the playing state from title (or game_over) without a click. Resumes with current seed. | `true` |
| `step(dt, n)` | Advances the simulation n ticks of dt seconds (dt in seconds, e.g. 1/60). Then renders once. | `getState()` |
| `setTime(t)` | Sets STATION.time to t (seconds). Advances all time-based systems to t without rendering. | `getState()` |
| `seed(n)` | Reseeds the PRNG to n. Regenerates the station, drones, loot, player position. | `getState()` |
| `getState()` | Returns plain data: all TILE fields (as 45×30 array), all ROOM fields, PLAYER fields, all DRONE fields, STATION fields, all LOOT fields. | object |
| `move(dir)` | Sets the held movement direction. dir is "N", "S", "E", or "W". Persists until `stopMove()` or a different `move()` call. | `true` |
| `stopMove()` | Clears the held movement direction. Player stops. | `true` |
| `interact()` | Triggers E-key action (search, door, disable drone, prime pod) as if the player pressed E. | `true` |
| `useItem(slot)` | Uses the item in inventory slot (0–7) as if the player pressed that number key. | `true` |
| `forceDoor()` | Triggers F-key (forced door, T2). | `true` |
| `scan()` | Triggers Q-key (scan, T2). | `true` |
| `spawnDrone(x, y, section)` | Places a new DRONE at (x,y) in the given section, state PATROL, with a generated patrol path. | the new DRONE id |
| `disableDrone(id)` | Sets the drone with given id to DISABLED. | `true` |
| `setOxygen(v)` | Sets Player.oxygen to v (0–100). | `true` |
| `setHealth(v)` | Sets Player.health to v (0–100). | `true` |
| `setStationPower(v)` | Sets STATION.power to v (0–100). | `true` |
| `setPlayerPower(v)` | Sets Player.power to v (0–100). | `true` |
| `giveItem(type, count)` | Adds `count` items of `type` to the first empty inventory slots. Returns number actually placed. | int |
| `triggerDecompression(x, y, length)` | Sets a strip of `length` corridor tiles starting at (x,y) (horizontal) to decompressed_until = STATION.time + 20. | `true` |
| `setSection(s)` | Teleports the player to the center of a random room in section s (1–5). | `true` |
| `setHungerTimer(v)` | Sets Player.hunger_timer to v. | `true` |
| `setAlarm(active)` | Sets STATION.alarm_active to bool. If true, sets alarm_timer = 10. | `true` |

All calls are synchronous. With a given seed and a given sequence of calls, the state is fully deterministic.

## 9. TESTS

All tests assume: `start(); seed(42);` is the preamble.

1. **Initial state.** After `start(); seed(42);`: `getState().player.alive` is `true`. `getState().player.oxygen` is `100`. `getState().station.power` is `100`. `getState().player.x` is in range [0,8] (section 1). `getState().drones.length` is `15`. `getState().rooms` has at least 1 room of type QUARTERS in section 1 and 1 room of type POD_BAY in section 5.

2. **Movement.** After `start(); seed(42); move("E"); step(1/60, 12); stopMove();`: `getState().player.x` is greater than the starting x (player moved east) OR the player is adjacent to a non-walkable tile. `getState().player.alive` is `true`.

3. **Oxygen drain.** After `start(); seed(42); step(1, 60);`: `getState().player.oxygen` is less than `100`. Specifically, in a corridor it should be ≈ 100 − 0.5×60 = 70 (±5 for room/corridor mix).

4. **O2 canister use.** After `start(); seed(42); setOxygen(50); giveItem("O2_CANISTER", 1); useItem(0);`: `getState().player.oxygen` is `80` (50+30). `getState().player.inventory[0]` is `null`.

5. **Power drain.** After `start(); seed(42); step(1, 100);`: `getState().station.power` is approximately `100 − 0.3×100 = 70` (±2).

6. **Drone detection.** After `start(); seed(42); d = getState().drones[0]; move("E"); step(1, 30); stopMove();`: if the player is within 6 tiles of any PATROL drone with LOS, that drone's state is `ALERT` or `CHASE`. Verify by checking `getState().drones` for any with state ≠ PATROL and state ≠ DISABLED.

7. **Drone disable.** After `start(); seed(42); d0 = getState().drones[0]; spawnDrone(d0.x, d0.y, 1); disableDrone(getState().drones[14].id);`: the last spawned drone's state is `DISABLED`.

8. **Radiation damage.** After `start(); seed(42); // move player onto a RADIATION tile via setSection or manual;`: set player position to a known radiation tile (find one via `getState().tiles`). Then `step(1, 10);`: `getState().player.health` is less than 100 (drained by 3×10 = 30, minus any regen).

9. **Door access.** After `start(); seed(42); setSection(1); giveItem("ACCESS_CARD", 1); move("E"); step(1/60, 60); stopMove();`: if the player encountered a DOOR_LOCKED tile, it is now DOOR_UNLOCKED in `getState().tiles`. `getState().player.access_cards` is `0`.

10. **Decompression.** After `start(); seed(42); triggerDecompression(5, 5, 5); step(1, 5);`: tiles (5,5) through (9,5) (or vertical equivalent) have `decompressed_until` > `getState().station.time`. `getState().station.time` < 600.

11. **Death.** After `start(); seed(42); setOxygen(0); setHealth(1); step(1, 5);`: `getState().player.alive` is `false`. `getState().station.gameOver` is `true`.

12. **Rescue.** After `start(); seed(42); setTime(600); step(1/60, 1);`: `getState().station.rescued` is `true`. `getState().station.gameOver` is `true`.

13. **Escape.** After `start(); seed(42); setSection(5); giveItem("REPAIR_PART", 2); giveItem("POWER_CELL", 1); setStationPower(50); // move to POD_TILE; interact(); step(1, 6);`: `getState().station.escaped` is `true`. `getState().station.gameOver` is `true`.

14. **Fog radius.** After `start(); seed(42); setStationPower(100);`: fog radius is `3 + floor(100/25) = 7`. After `setStationPower(0);`: fog radius is `3 + 0 = 3`.

15. **Hunger (T2).** After `start(); seed(42); setHungerTimer(0); step(1, 30);`: `getState().player.health` has decreased by approximately `0.1×30 = 3` (±1) due to hunger, assuming no other damage.

16. **Drone alarm (T2).** After `start(); seed(42); setAlarm(true);`: `getState().station.alarm_active` is `true`. `getState().station.alarm_timer` is `10`. After `setTime(getState().station.time + 11);`: alarm is `false`.

**SCREENSHOTS (human verification):**

| Screen / state | What a person must see |
|----------------|----------------------|
| Title screen | Station exterior art fills background. "DERELICT" in large text. "Press E to begin" below. A seed input box. |
| Playing — start | Player sprite visible center-screen. Green O2 bar full. Red health bar full. Blue power bar full. HUD at bottom. 5-section station layout visible around player (fog of war). Section indicator shows "1". |
| Playing — in a room | Room floor color matches type (e.g., greenish for STORAGE). Corridors visible beyond. Fog of war: tiles beyond radius are dimmed or black. |
| Playing — drone ALERT | A drone sprite has a yellow border. Player sees it approaching. |
| Playing — drone CHASE | Drone has a red border and red pulsing sensor. It is moving toward the player. |
| Playing — radiation | Tiles are green-tinted with a pulsing overlay. Standing on one: health bar visibly decreasing. |
| Playing — decompression | A strip of corridor tiles has a blue shimmer overlay. |
| Playing — locked door | A red-bordered tile blocks the path. Player must have an access card to proceed. |
| Playing — pod bay | The POD_BAY room is visible (greenish floor). The POD_TILE is marked with a white border and circle. |
| Game over — death | "YOU DIED" text. Cause shown ("Oxygen depleted" or "Health depleted"). Stats: time, sections, drones disabled. "Press E to return." |
| Game over — escape | "ESCAPED" text. Pod launch animation (1-2 frames). Stats. "Press E to return." |
| Game over — rescue | "RESCUED" text. A ship silhouette above. Stats. "Press E to return." |
| Paused | Dark overlay. "PAUSED" text. Options: Resume (Esc), Restart (N), Quit (Q). |

## 10. BUILD ORDER

**Milestone 1: Title and shell.** Title screen renders (AI art background, text, seed input). Pressing E enters playing state. The 45×30 grid renders (all WALL, black). Player is at the start tile. HUD renders (all bars full, empty inventory). *Check: Test 1 (initial state).*

**Milestone 2: Station and movement.** Station Generator runs (rooms, corridors, doors, radiation, pod bay). Player can move with WASD/arrows, tile-by-tile, with collision. Fog of war renders (explored, in-fog, unexplored). *Check: Test 2 (movement) and Test 1 (room/pod/dron