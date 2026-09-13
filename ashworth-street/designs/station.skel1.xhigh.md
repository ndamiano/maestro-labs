# 0. SCOPE

## 0.1 Asked
“Survive on a derelict space station.” → seeded station map, station power/oxygen/hull records and decay, player suit oxygen and health, locker loot, console installs, drone threat, 180-second survival, and airlock escape.

## 0.2 Decisions
- 2D top-down first: the player’s best actions are legible meter management, corridor navigation, and threat response on one readable map; a 3D view would hide the station state that the survival loop depends on.
- Single 16-by-10 tile station: it is small enough to fit on screen, large enough for rooms, corridors, doors, loot, and drones, and deterministic enough to test.
- 180-second survival run: it gives a clear end, a clear airlock deadline, and enough time for several threat waves without becoming a marathon.
- Three station meters, power, oxygen, and hull: they express “derelict station” directly and make every meter a survival decision.
- Player suit oxygen separate from station oxygen: the station can fail while the player still has a short escape window, creating urgency.
- Drones are the opponent: they force the player to move, fight, and avoid, instead of only clicking repair meters.
- Melee wrench combat: it keeps hit detection simple, makes combat timing readable, and avoids weapon inventory complexity.
- Install resource items at consoles: it creates navigation and prioritization instead of passive pickup.
- Medkit use is a single dedicated action: it keeps the control scheme small while still giving a survivability choice.
- Fixed seeded spawn schedule: it makes difficulty fair, testable, and repeatable for the same seed.
- 640-by-400 canvas with a 32-pixel tile: the whole map is visible, so the player always sees doors, meters, drones, and the airlock.
- All audio generated with the Web Audio API: it gives immediate game feedback without external assets.

## 0.3 Tiers
TIER 1 is the game: MAP GENERATOR, LOOT GENERATOR, SPAWN SCHEDULE GENERATOR, RESET, SCREENS, GAME LOOP, PLAYER MOVEMENT, PLAYER COMBAT, PLAYER INTERACTION, PLAYER MEDKIT, STATION DECAY, STATION EVENTS, DRONE AI, DRONE SPAWNING, VICTORY/DEATH.

TIER 2, in order to add:
- CONSOLE UPGRADES: installing a resource at a console reduces that meter’s decay rate.
- ALARMS: low station meters or an unlocked airlock make the HUD flash and play an alarm.
- END SUMMARY: the won and dead screens show time, drones killed, remaining meters, and a score.

TIER 3, never started before every Tier 2 item is in:
- Dodge roll with 0.5-second invulnerability.
- Stalker drone that hides in vents until the player is close.
- Hull patch repair minigame.

# 1. CONVENTIONS
The world is 2D top-down. One tile is 32 CSS pixels and one world tile unit. The map is 16 tiles wide and 10 tiles tall, so the map is 512 by 320 pixels. The canvas is 640 by 400 pixels, and the map is rendered with a top-left offset of 64 pixels horizontally and 40 pixels vertically. Tile center (0,0) is world position (0,0). The x axis points right, the y axis points down, and up is negative y. There is no ground height; all play is on one plane. The camera is fixed and shows the whole map.

The update loop uses a fixed step of dt = 0.1 seconds. Each real frame accumulates elapsed time; while at least 0.1 seconds has accumulated and the screen is play, the systems run in this order: GAME LOOP, DRONE SPAWNING, STATION EVENTS, CONSOLE UPGRADES, STATION DECAY, PLAYER MOVEMENT, PLAYER COMBAT, PLAYER INTERACTION, PLAYER MEDKIT, DRONE AI, VICTORY/DEATH, ALARMS, END SUMMARY. Rendering happens after the update loop. If the screen is not play, systems do not advance; the current state is rendered.

The only random source is R, a seeded random source. R is set by seed(n). R provides integer picks and shuffles. Nothing else is random.

Controls:

| Input | Action |
|---|---|
| W / Arrow Up | move up, y input -1 |
| A / Arrow Left | move left, x input -1 |
| S / Arrow Down | move down, y input +1 |
| D / Arrow Right | move right, x input +1 |
| Space | interact; on title, start |
| E | medkit |
| F | attack |
| Escape | pause or resume; on end screens, return to title |
| Touch left half | virtual joystick, continuous x and y move input |
| Touch button A | interact |
| Touch button B | medkit |
| Touch button C | attack |
| Touch button D | pause or resume |

Keyboard movement uses currently held keys; the resulting x and y inputs are clamped to a maximum length of 1. Touch input supplies the same persistent move direction until changed.

# 2. RECORDS
RECORDS: TILE, DOOR, LOCKER, CONSOLE, VENT, AIRLOCK, DRONE, SPAWN_EVENT, PLAYER, STATION, UI.

TILE: x (integer tile column, 0..15, set by MAP GENERATOR), y (integer tile row, 0..9, set by MAP GENERATOR), base (enum wall or floor, start wall).

DOOR: id (integer, 0..3, set by MAP GENERATOR), x (integer tile column, 0..15, set by MAP GENERATOR), y (integer tile row, 0..9, set by MAP GENERATOR), isOpen (boolean, start false).

LOCKER: id (integer, 0..7, set by MAP GENERATOR), x (integer tile column, 0..15, set by MAP GENERATOR), y (integer tile row, 0..9, set by MAP GENERATOR), isOpen (boolean, start false), itemA (enum none, powerCell, o2Cell, hullPatch, medkit, start none), itemB (enum none, powerCell, o2Cell, hullPatch, medkit, start none).

CONSOLE: id (integer, 0..2, set by MAP GENERATOR), x (integer tile column, 0..15, set by MAP GENERATOR), y (integer tile row, 0..9, set by MAP GENERATOR), kind (enum reactor, scrubber, hull, set by MAP GENERATOR), level (integer, 0..3, start 0).

VENT: id (integer, 0..3, set by MAP GENERATOR), x (integer tile column, 0..15, set by MAP GENERATOR), y (integer tile row, 0..9, set by MAP GENERATOR).

AIRLOCK: x (integer tile column, 0..15, set by MAP GENERATOR), y (integer tile row, 0..9, set by MAP GENERATOR).

DRONE: id (integer, 1 or greater, set by DRONE SPAWNING or debug), x (tile units, -1..16, set on spawn), y (tile units, -1..10, set on spawn), kind (enum scout, brute, set on spawn), health (integer, 0..50, set on spawn), speed (tiles per second, set on spawn), damage (health per hit, set on spawn), attackCooldown (seconds, 0..0.8, start 0), wanderDirection (integer, 0 up, 1 right, 2 down, 3 left, start 0), wanderTimer (seconds, 0..2, start 0), alive (boolean, start true).

SPAWN_EVENT: id (integer, 0..8, set by SPAWN SCHEDULE GENERATOR), time (seconds, 15..135, set by SPAWN SCHEDULE GENERATOR), kind (enum scout, brute, set by SPAWN SCHEDULE GENERATOR), ventId (integer, 0..3, set by SPAWN SCHEDULE GENERATOR), used (boolean, start false).

PLAYER: x (tile units, -0.5..15.5, start 4), y (tile units, -0.5..9.5, start 4), facing (integer, 0 up, 1 right, 2 down, 3 left, start 2), health (integer, 0..100, start 100), oxygen (integer, 0..100, start 100), invPowerCells (integer, 0..9, start 0), invO2Cells (integer, 0..9, start 0), invHullPatches (integer, 0..9, start 0), invMedkits (integer, 0..9, start 0), attackCooldown (seconds, 0..0.5, start 0), interactCooldown (seconds, 0..0.6, start 0), alive (boolean, start true).

STATION: time (seconds, 0 or greater, start 0), power (integer, 0..100, start 25), oxygen (integer, 0..100, start 40), hull (integer, 0..100, start 70), airlockUnlocked (boolean, start false), dronesKilled (integer, 0 or greater, start 0).

UI: screen (enum title, play, paused, won, dead, start title), alarm (boolean, start false), score (integer, 0 or greater, start 0), message (string, start empty).

ITEM KINDS are the fixed values for LOCKER.itemA, LOCKER.itemB, PLAYER.invPowerCells, PLAYER.invO2Cells, PLAYER.invHullPatches, and PLAYER.invMedkits:

| Item kind | Applies to | Amount | Unit |
|---|---|---:|---|
| powerCell | STATION.power | 30 | power units |
| o2Cell | STATION.oxygen | 30 | oxygen units |
| hullPatch | STATION.hull | 25 | hull units |
| medkit | PLAYER.health | 35 | health units |

DRONE KINDS are the fixed values for DRONE.kind, DRONE.health, DRONE.speed, and DRONE.damage:

| Drone kind | Health | Speed | Damage | Attack cooldown |
|---|---:|---:|---:|---:|
| scout | 20 | 1.8 tiles/s | 5 health/hit | 0.8 s |
| brute | 50 | 1.2 tiles/s | 12 health/hit | 0.8 s |

CONSOLE KINDS are the fixed values for CONSOLE.kind:

| Console kind | Matching item | Meter affected | Amount |
|---|---|---|---:|
| reactor | powerCell | STATION.power | 30 |
| scrubber | o2Cell | STATION.oxygen | 30 |
| hull | hullPatch | STATION.hull | 25 |

# 3. SYSTEMS
SYSTEMS: MAP GENERATOR, LOOT GENERATOR, SPAWN SCHEDULE GENERATOR, RESET, SCREENS, GAME LOOP, PLAYER MOVEMENT, PLAYER COMBAT, PLAYER INTERACTION, PLAYER MEDKIT, STATION DECAY, STATION EVENTS, DRONE AI, DRONE SPAWNING, VICTORY/DEATH, CONSOLE UPGRADES, ALARMS, END SUMMARY.

### MAP GENERATOR (T1)
- On seed(n), set R to seed n and create 160 TILE records with x from 0 to 15, y from 0 to 9, and base wall.
- Carve the fixed start room: set TILE.base to floor for x = 2..6 and y = 2..5.
- For room i = 1..4, create a random room: choose left = R.int(15), top = R.int(9), width = 3 + R.int(3), height = 3 + R.int(2); clamp the rectangle to x = 1..14 and y = 1..8; if the rectangle overlaps existing floor in more than 2 tiles, re-roll that room with the next R values up to 5 times, then accept it; set the rectangle’s TILE.base to floor.
- Store the fixed start room center as (4,4). For each random room, store its center as left + floor(width / 2), top + floor(height / 2).
- Connect rooms in order: for i = 1..4, carve floor tiles from center i-1 to center i by first carving a horizontal line at the starting y, then a vertical line at the ending x.
- Compute BFS distance from tile (4,4) over TILE.base = floor tiles.
- Place AIRLOCK at the floor tile with the greatest BFS distance; if two or more tiles tie, choose the one with the smallest x, then smallest y.
- Place CONSOLE records in fixed order reactor, scrubber, hull. For each console, choose a floor tile not occupied by AIRLOCK or an earlier CONSOLE with the greatest BFS distance from the previously placed special; if two or more tiles tie, choose the smallest x, then smallest y; set CONSOLE.kind and level 0.
- Place LOCKER record 0 at tile (5,4). For locker id 1..7, choose a floor tile adjacent to at least one wall tile, not occupied by AIRLOCK, CONSOLE, another LOCKER, VENT, or DOOR, using R; if no such tile remains, choose any unoccupied floor tile; set LOCKER.isOpen false, itemA none, itemB none.
- Place 4 VENT records on floor tiles adjacent to at least one wall tile, not occupied by AIRLOCK, CONSOLE, LOCKER, another VENT, or DOOR, using R.
- Place 4 DOOR records on corridor floor tiles carved during room connection; if fewer than 4 such tiles remain, fill the rest with unoccupied non-special floor tiles adjacent to at least one wall; set DOOR.isOpen false.
- VERIFIER: BFS from (4,4) over TILE.base = floor tiles, treating DOOR tiles as passable, reaches AIRLOCK, every CONSOLE, every LOCKER, and every VENT; the number of floor tiles is at least 40; exactly 160 TILE records exist; exactly 3 CONSOLE records exist; exactly 8 LOCKER records exist; exactly 4 VENT records exist; exactly 4 DOOR records exist; no two AIRLOCK, CONSOLE, LOCKER, VENT, or DOOR records share a tile. Re-roll with the next seed if any check fails.

### LOOT GENERATOR (T1)
- Build a deck array containing 3 powerCell, 3 o2Cell, 3 hullPatch, and 7 medkit, for 16 items total.
- Shuffle the deck with R using Fisher-Yates from the last index to the first.
- For locker id 0..7, set LOCKER.itemA to deck[2 * id] and LOCKER.itemB to deck[2 * id + 1].
- VERIFIER: every LOCKER has itemA and itemB not none; total itemA and itemB counts are exactly powerCell 3, o2Cell 3, hullPatch 3, medkit 7; the deck is empty. Re-roll with the next seed if any check fails.

### SPAWN SCHEDULE GENERATOR (T1)
- Create 6 scout SPAWN_EVENT records: id 0..5, time = 15 + 24 * id, kind scout, used false.
- Create 3 brute SPAWN_EVENT records: id 6..8, time = 75 + 30 * (id - 6), kind brute, used false.
- Sort SPAWN_EVENT records by time ascending; if two events share a time, scout comes before brute.
- For every SPAWN_EVENT, set ventId = id mod 4.
- VERIFIER: exactly 9 SPAWN_EVENT records exist; times are ascending; there are 6 scout events and 3 brute events; every ventId is 0..3; every used is false. Re-roll with the next seed if any check fails.

### RESET (T1)
- When UI.screen changes from title to play, or from won or dead to play, set PLAYER.x = 4, PLAYER.y = 4, PLAYER.facing = 2, PLAYER.health = 100, PLAYER.oxygen = 100, PLAYER.invPowerCells = 0, PLAYER.invO2Cells = 0, PLAYER.invHullPatches = 0, PLAYER.invMedkits = 0, PLAYER.attackCooldown = 0, PLAYER.interactCooldown = 0, PLAYER.alive = true.
- On reset, set STATION.time = 0, STATION.power = 25, STATION.oxygen = 40, STATION.hull = 70, STATION.airlockUnlocked = false, STATION.dronesKilled = 0.
- On reset, set UI.alarm = false, UI.score = 0, UI.message = empty.
- On reset, set every DOOR.isOpen = false, every LOCKER.isOpen = false, every CONSOLE.level = 0, the DRONE list to empty, and every SPAWN_EVENT.used = false.
- LOCKER.itemA and LOCKER.itemB remain the values produced by LOOT GENERATOR.

### SCREENS (T1)
- If UI.screen is title and Space is pressed, set UI.screen = play and trigger RESET.
- If UI.screen is play and Escape is pressed, set UI.screen = paused.
- If UI.screen is paused and Escape is pressed, set UI.screen = play.
- If UI.screen is won or dead and Space or Escape is pressed, set UI.screen = title.
- The debug start() call sets UI.screen = play and triggers RESET.

### GAME LOOP (T1)
- Each fixed tick, increase STATION.time by 0.1 seconds.
- If STATION.time is at least 180 and STATION.airlockUnlocked is false, set STATION.airlockUnlocked = true and UI.message = “Shuttle arrived”.
- Run the systems in the fixed order given in Conventions, then render.
- If UI.screen is not play, do not advance STATION.time and do not run gameplay systems.

### PLAYER MOVEMENT (T1)
- If UI.screen is not play or PLAYER.alive is false, do nothing.
- If the current move input length is greater than 0, normalize the input length to 1.
- If the normalized input x is greater than 0, set PLAYER.facing = 1; if x is less than 0, set PLAYER.facing = 3; otherwise if y is greater than 0, set PLAYER.facing = 2; otherwise if y is less than 0, set PLAYER.facing = 0.
- Compute nextX = PLAYER.x + 2.2 * dt * input.x and nextY = PLAYER.y + 2.2 * dt * input.y.
- A tile is passable if TILE.base is floor and no DOOR with isOpen = false exists at that tile.
- If the tile at round(nextX), round(PLAYER.y) is passable, set PLAYER.x = nextX; otherwise leave PLAYER.x unchanged.
- If the tile at round(PLAYER.x), round(nextY) is passable, set PLAYER.y = nextY; otherwise leave PLAYER.y unchanged.
- Clamp PLAYER.x to -0.5..15.5 and PLAYER.y to -0.5..9.5.

### PLAYER COMBAT (T1)
- If UI.screen is not play or PLAYER.alive is false, do nothing.
- Set PLAYER.attackCooldown = max(0, PLAYER.attackCooldown - dt).
- If the attack action is triggered this tick and PLAYER.attackCooldown is 0, set PLAYER.attackCooldown = 0.5.
- On an attack, choose the alive DRONE with the smallest distance to PLAYER.
- If the chosen DRONE distance is 0.9 tiles or less, reduce DRONE.health by 12.
- If DRONE.health is 0 or less, set DRONE.alive = false and increase STATION.dronesKilled by 1.

### PLAYER INTERACTION (T1)
- If UI.screen is not play or PLAYER.alive is false, do nothing.
- Set PLAYER.interactCooldown = max(0, PLAYER.interactCooldown - dt).
- If the interact action is triggered this tick and PLAYER.interactCooldown is 0, set PLAYER.interactCooldown = 0.6.
- On an interact, choose the nearest non-open DOOR, non-open LOCKER, CONSOLE, or AIRLOCK within 0.9 tiles of PLAYER; if multiple objects tie, choose in order DOOR, LOCKER, CONSOLE, AIRLOCK.
- If the target is a DOOR, set DOOR.isOpen = true and UI.message = “Door opened”.
- If the target is a LOCKER, set LOCKER.isOpen = true; for LOCKER.itemA and LOCKER.itemB that are not none, increase the matching PLAYER inventory field by 1 and set that locker item field to none; set UI.message = “Looted locker”.
- If the target is a CONSOLE, check the matching item: reactor requires PLAYER.invPowerCells, scrubber requires PLAYER.invO2Cells, hull requires PLAYER.invHullPatches.
- If the matching inventory count is greater than 0, reduce it by 1, add the CONSOLE KINDS amount to the matching STATION meter, clamp the meter to 0..100, and set UI.message = “Installed”.
- If the matching inventory count is 0, set UI.message = “Need matching item”.
- If the target is the AIRLOCK and STATION.airlockUnlocked is true, set UI.screen = won and UI.message = “Escaped”.
- If the target is the AIRLOCK and STATION.airlockUnlocked is false, set UI.message = “Airlock locked”.

### PLAYER MEDKIT (T1)
- If UI.screen is not play, PLAYER.alive is false, PLAYER.invMedkits is 0, or PLAYER.health is 100, do nothing.
- If the medkit action is triggered, reduce PLAYER.invMedkits by 1, set PLAYER.health = min(100, PLAYER.health + 35), and set UI.message = “Medkit used”.

### STATION DECAY (T1)
- If UI.screen is not play, do nothing.
- Use the decay rates supplied by CONSOLE UPGRADES; if CONSOLE UPGRADES is absent, use base rates: power decay 0.5 per second, oxygen decay 0.4 per second while STATION.power is greater than 0, oxygen decay 0.8 per second while STATION.power is 0, hull decay 0.1 per second while STATION.time is at least 60, and hull decay 0 otherwise.
- Set STATION.power = max(0, STATION.power - effectivePowerDecay * dt).
- Set STATION.oxygen = max(0, STATION.oxygen - effectiveOxygenDecay * dt).
- Set STATION.hull = max(0, STATION.hull - effectiveHullDecay * dt).
- If STATION.oxygen is at least 30, set PLAYER.oxygen = min(100, PLAYER.oxygen + 0.8 * dt); otherwise set PLAYER.oxygen = max(0, PLAYER.oxygen - 1.2 * dt).
- If PLAYER.oxygen is 0, set PLAYER.health = max(0, PLAYER.health - 10 * dt).
- If STATION.hull is 0, set PLAYER.health = max(0, PLAYER.health - 2 * dt).

### STATION EVENTS (T1)
- Fixed hull stress times are 30, 60, 90, 120, and 150 seconds.
- For each fixed time t, if STATION.time before the tick was less than t and STATION.time after the tick is at least t, set STATION.hull = max(0, STATION.hull - 5) and UI.message = “Hull stress”.

### DRONE AI (T1)
- For each alive DRONE, set DRONE.attackCooldown = max(0, DRONE.attackCooldown - dt) and DRONE.wanderTimer = max(0, DRONE.wanderTimer - dt).
- A drone is visible if its distance to PLAYER is 6.0 tiles or less and every tile on the Bresenham line from DRONE to PLAYER is passable.
- If the drone is visible, set DRONE.wanderDirection toward PLAYER: if absolute x difference is greater than or equal to absolute y difference, direction is 1 when x difference is positive and 3 when negative; otherwise direction is 2 when y difference is positive and 0 when negative.
- If the drone is not visible and DRONE.wanderTimer is 0, set DRONE.wanderDirection = (DRONE.id + floor(STATION.time / 2)) mod 4 and DRONE.wanderTimer = 2.0.
- Move speed is DRONE.speed when visible and 0.7 tiles/s when not visible.
- Compute nextX = DRONE.x + speed * dt * directionX and nextY = DRONE.y + speed * dt * directionY, where direction 0 gives y -1, direction 1 gives x +1, direction 2 gives y +1, and direction 3 gives x -1.
- Use the same passable-tile collision rule as PLAYER MOVEMENT, testing x and y separately.
- If the DRONE distance to PLAYER is 0.8 tiles or less and DRONE.attackCooldown is 0, set DRONE.attackCooldown = 0.8 and reduce PLAYER.health by DRONE.damage; if PLAYER.health becomes 0, set PLAYER.alive = false.

### DRONE SPAWNING (T1)
- For each SPAWN_EVENT where used is false and STATION.time is at least time, set used = true.
- Spawn a DRONE at the VENT with matching ventId, using x = VENT.x and y = VENT.y.
- Set the new DRONE.kind to SPAWN_EVENT.kind, health to the DRONE KINDS value, speed to the DRONE KINDS value, damage to the DRONE KINDS value, attackCooldown = 0, wanderTimer = 0, alive = true, and id to the next integer drone id.
- Set UI.message = “Drone emerging”.

### VICTORY/DEATH (T1)
- If UI.screen is not play, do nothing.
- If PLAYER.alive is false or PLAYER.health is 0, set PLAYER.alive = false, UI.screen = dead, and UI.message = “You died”.
- If PLAYER reaches the AIRLOCK while STATION.airlockUnlocked is true through PLAYER INTERACTION, UI.screen is already won.
- When UI.screen becomes won or dead, trigger END SUMMARY.

### CONSOLE UPGRADES (T2)
- When PLAYER INTERACTION installs a matching item at a CONSOLE, set CONSOLE.level = min(3, CONSOLE.level + 1).
- effectivePowerDecay = max(0, 0.5 - reactor CONSOLE.level * 0.05).
- effectiveOxygenDecay = max(0, 0.4 - scrubber CONSOLE.level * 0.05) while STATION.power is greater than 0; while STATION.power is 0, effectiveOxygenDecay = max(0, 0.8 - scrubber CONSOLE.level * 0.05).
- effectiveHullDecay = 0 while STATION.time is less than 60; while STATION.time is at least 60, effectiveHullDecay = max(0, 0.1 - hull CONSOLE.level * 0.05).

### ALARMS (T2)
- Each tick after STATION DECAY, set UI.alarm = true if STATION.power is less than 20, STATION.oxygen is less than 20, STATION.hull is less than 20, or STATION.airlockUnlocked is true; otherwise set UI.alarm = false.
- If UI.alarm is true and the whole-second boundary of STATION.time has changed, play the alarm sound once.

### END SUMMARY (T2)
- When UI.screen becomes won or dead, set UI.score = floor(STATION.time * 10) + STATION.dronesKilled * 50 + floor((STATION.power + STATION.oxygen + STATION.hull) / 10).
- If UI.screen is won, add 500 to UI.score.

# 4. CORE LOOP
The player starts in the fixed start room and repeats this cycle every minute: PLAYER MOVEMENT carries the player through the seeded station, PLAYER INTERACTION opens lockers and doors, LOOT GENERATOR has placed the items, PLAYER MEDKIT restores health when needed, PLAYER COMBAT clears drones, STATION DECAY and STATION EVENTS keep lowering power, oxygen, and hull, and DRONE AI and DRONE SPAWNING pressure the player to keep moving. The player carries resource items to CONSOLE locations and uses PLAYER INTERACTION to install them; CONSOLE UPGRADES then slows the matching meter’s decay. What grows is console level, drones killed, and score. What unlocks is reduced station decay and, at 180 seconds, the airlock. The end is winning by entering the unlocked AIRLOCK or dying from health, oxygen, or drone damage. The game has an end: escape the station before the player dies.

# 5. SCREENS
State machine: title (station logo, “press Space”) → play (full station map, player, drones, HUD) → paused (dimmed play field, “PAUSED”) → play; play → won (airlock view, score) or dead (red vignette, score); won or dead → title.

Key and button leads:
- Space on title starts play.
- Escape on play pauses; Escape on paused resumes.
- Space or Escape on won or dead returns to title.
- The controls table in Conventions applies during play.

HUD table:

| Element | Record field shown |
|---|---|
| Health bar | PLAYER.health |
| Suit oxygen bar | PLAYER.oxygen |
| Station power bar | STATION.power |
| Station oxygen bar | STATION.oxygen |
| Station hull bar | STATION.hull |
| Power cell count | PLAYER.invPowerCells |
| O2 cell count | PLAYER.invO2Cells |
| Hull patch count | PLAYER.invHullPatches |
| Medkit count | PLAYER.invMedkits |
| Survival timer | STATION.time |
| Airlock status | STATION.airlockUnlocked |
| Alarm flash | UI.alarm |
| Message line | UI.message |
| End score | UI.score |

# 6. AUDIO
All audio is generated with the Web Audio API.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| uiSelect | square, 440 Hz, 0.08 s, gain 0.25, attack 0.01 s, release 0.07 s | Space on title, Escape on play or paused |
| interact | triangle, 660 Hz, 0.10 s, gain 0.30, attack 0.01 s, release 0.09 s | successful PLAYER INTERACTION |
| medkit | sine, 780 Hz, 0.15 s, gain 0.30, attack 0.02 s, release 0.13 s | PLAYER MEDKIT uses a medkit |
| attack | square, 220 Hz, 0.06 s, gain 0.25, attack 0.005 s, release 0.055 s | PLAYER COMBAT triggers an attack |
| hit | sawtooth, 110 Hz, 0.12 s, gain 0.35, attack 0.01 s, release 0.11 s | DRONE AI reduces PLAYER.health |
| droneDeath | sawtooth, 90 Hz, 0.25 s, gain 0.35, attack 0.01 s, release 0.24 s | DRONE.alive becomes false |
| alarm | square, 880 Hz, 0.10 s, gain 0.20, attack 0.01 s, release 0.09 s | once per whole second while UI.alarm is true |
| vent | sawtooth, 60 Hz, 0.30 s, gain 0.25, attack 0.05 s, release 0.25 s | DRONE SPAWNING creates a drone |
| win | sine, 523 Hz then 659 Hz then 784 Hz, 0.20 s each, gain 0.30 | UI.screen becomes won |
| lose | sawtooth, 160 Hz sliding to 60 Hz, 0.50 s, gain 0.35 | UI.screen becomes dead |

# 7. ART
AI art:
- ask for a derelict space station title scene as a scene.
- ask for a lone astronaut as an anim with idle, walk_up, walk_down, walk_left, walk_right; faces four ways.
- ask for a maintenance drone as an anim with hover, damaged; faces one way.
- ask for a closed supply locker as a sprite.
- ask for a reactor console as a sprite.
- ask for a scrubber console as a sprite.
- ask for a hull console as a sprite.
- ask for an emergency airlock door as a sprite.
- ask for a wall vent as a sprite.
- ask for a power cell icon as a sprite.
- ask for an O2 cell icon as a sprite.
- ask for a hull patch icon as a sprite.
- ask for a medkit icon as a sprite.

Code-drawn recipes:
- RECIPE: floor tile is a 32 by 32 pixel square, fill #16202b, 1-pixel inner line #263644; up to 160 tiles.
- RECIPE: wall tile is a 32 by 32 pixel square, fill #070b11, 2-pixel top highlight #1b2836.
- RECIPE: door is a 32 by 32 pixel square; closed fill #465b6d, open fill #22313d with an 8-pixel center gap #0a1118.
- RECIPE: player hit flash is a red #ff3b3b overlay over the player for 0.15 seconds.
- RECIPE: drone health bar is a 16 by 2 pixel bar above the drone, background #000000, fill #d94a4a proportional to DRONE.health divided by kind maximum.
- RECIPE: HUD bar is a 120 by 12 pixel bar, border #3b4d5e, background #101820; health fill #ff5a5a, suit oxygen fill #6be1ff, station power fill #ffd166, station oxygen fill #7cf0b3, station hull fill #b0bec5.

Everything else — floor tiles, wall tiles, doors, collision shapes, grid lines, drone health bars, HUD bars, text, pause overlay, cursor — is drawn in code.

# 8. DEBUG API
The game installs window.__game.

| Call | What it does | What it returns |
|---|---|---|
| start() | enters play from title without a click and triggers RESET | { screen: UI.screen } |
| step(dt, n) | advances n ticks of dt seconds without waiting for real time, then draws once | { time: STATION.time } |
| setTime(t) | advances STATION.time to t seconds without drawing and without running systems | { time: STATION.time } |
| seed(n) | reseeds R, rebuilds MAP, LOOT, and SPAWN SCHEDULE, triggers RESET, and keeps the current screen | { seed: n, ok: true } |
| getState() | returns the fields of every record as plain data | object with tiles, doors, lockers, consoles, vents, airlock, drones, spawnEvents, player, station, ui |
| setMove(dx, dy) | sets the persistent player movement direction until changed | { dx: dx, dy: dy } |
| interact() | triggers one interact action | { did: boolean } |
| medkit() | triggers one medkit action | { used: boolean } |
| attack() | triggers one attack action | { hit: boolean } |
| pause() | triggers one Escape action | { screen: UI.screen } |
| setPower(v) | sets STATION.power to v clamped to 0..100 | { power: STATION.power } |
| setOxygen(v) | sets STATION.oxygen to v clamped to 0..100 | { oxygen: STATION.oxygen } |
| setHull(v) | sets STATION.hull to v clamped to 0..100 | { hull: STATION.hull } |
| setHealth(v) | sets PLAYER.health to v clamped to 0..100 and sets PLAYER.alive true when v is greater than 0 | { health: PLAYER.health } |
| giveItem(kind, count) | adds count to the matching PLAYER inventory field | { invPowerCells, invO2Cells, invHullPatches, invMedkits } |
| teleportPlayer(x, y) | sets PLAYER.x and PLAYER.y to x and y | { x: PLAYER.x, y: PLAYER.y } |
| spawnDrone(kind, x, y) | adds an alive DRONE of the given kind at x and y | { id: DRONE.id } |
| clearDrones() | removes every DRONE from the DRONE list | { count: 0 } |
| unlockAirlock() | sets STATION.airlockUnlocked = true | { unlocked: true } |
| setLockerContents(index, itemA, itemB) | sets LOCKER id index to closed and sets itemA and itemB | { locker: that LOCKER } |

# 9. TESTS
1. start(); getState() → ui.screen = “play”, station.time = 0, station.power = 25, station.oxygen = 40, station.hull = 70, player.x = 4, player.y = 4, player.health = 100, player.oxygen = 100, player.invPowerCells = 0, player.invMedkits = 0, drones.length = 0, every door.isOpen = false, every locker.isOpen = false, every spawnEvent.used = false.
2. seed(7); start(); getState() → tiles.length = 160, floor tile count is at least 40, consoles.length = 3, lockers.length = 8, vents.length = 4, doors.length = 4, and the airlock, consoles, lockers, vents, and doors have distinct x,y coordinates.
3. seed(7); start(); getState() → across all locker itemA and itemB values, powerCell = 3, o2Cell = 3, hullPatch = 3, medkit = 7, none = 0.
4. seed(1); start(); setMove(0, 0); step(0.1, 10); getState() → station.time = 1.0, station.power = 24.5, station.oxygen = 39.6, station.hull = 70, player.x = 4, player.y = 4.
5. seed(1); start(); setMove(1, 0); step(0.1, 1); getState() → player.x = 4.22, player.facing = 1; setMove(0, 0); getState() → player.x remains 4.22.
6. seed(1); start(); setLockerContents(0, “powerCell”, “medkit”); teleportPlayer(5, 4); interact(); getState() → lockers[0].isOpen = true, player.invPowerCells = 1, player.invMedkits = 1, player.interactCooldown = 0.6.
7. seed(1); start(); giveItem(“powerCell”, 1); let c = the console whose kind is reactor; teleportPlayer(c.x, c.y); interact(); getState() → station.power = 55, player.invPowerCells = 0, c.level = 1.
8. seed(1); start(); giveItem(“medkit”, 1); setHealth(70); medkit(); getState() → player.health = 100, player.invMedkits = 0.
9. seed(1); start(); setOxygen(20); setMove(0, 0); step(0.1, 10); getState() → station.oxygen = 19.6, player.oxygen = 98.8, station.power = 24.5.
10. seed(1); start(); setMove(0, 0); setTime(29.9); step(0.1, 1); getState() → station.time = 30.0, station.hull = 65.
11. seed(1); start(); clearDrones(); setMove(0, 0); setTime(14.9); step(0.1, 1); getState() → station.time = 15.0, drones.length = 1, drones[0].kind = “scout”, drones[0].alive = true.
12. seed(1); start(); clearDrones(); setMove(0, 0); teleportPlayer(4, 4); spawnDrone(“scout”, 4.7, 4.0); step(0.1, 1); getState() → player.health = 95, drones[0].attackCooldown = 0.8, drones[0].alive = true.
13. seed(1); start(); clearDrones(); setMove(0, 0); teleportPlayer(4, 4); spawnDrone(“scout”, 4.7, 4.0); attack(); getState() → drones[0].health = 8, station.dronesKilled = 0, player.attackCooldown = 0.5.
14. seed(1); start(); unlockAirlock(); let a = getState().airlock; teleportPlayer(a.x, a.y); interact(); getState() → ui.screen = “won”, ui.score = 513, station.airlockUnlocked = true.
15. seed(1); start(); setHealth(0); setMove(0, 0); step(0.1, 1); getState() → ui.screen = “dead”, player.alive = false, ui.score = 14.
16. seed(1); start(); pause(); getState() → ui.screen = “paused”; pause(); getState() → ui.screen = “play”.
17. seed(1); start(); giveItem(“powerCell”, 1); let c = the console whose kind is reactor; teleportPlayer(c.x, c.y); interact(); setPower(100); setMove(0, 0); step(0.1, 10); getState() → c.level = 1, station.power = 99.55, station.time = 1.0.
18. seed(1); start(); setPower(15); setMove(0, 0); step(0.1, 1); getState() → ui.alarm = true, station.power = 14.95.
19. seed(1); start(); getState() → spawnEvents.length = 9, times in order are 15, 39, 63, 75, 87, 105, 111, 135, 135, kinds in order are scout, scout, scout, brute, scout, brute, scout, scout, brute, and every used is false.

SCREENSHOTS:

| Screen or state | What a person must see |
|---|---|
| title | station logo scene, “press Space” prompt, no gameplay HUD bars |
| play | full 16-by-10 station map, player in start room, five HUD bars, inventory icons, timer |
| paused | dimmed play field, large “PAUSED” text, meters and drones frozen |
| won | airlock view or station view with “ESCAPED”, score visible |
| dead | red vignette over the station, “YOU DIED”, score visible |
| play low power | station power bar below 20, HUD alarm flash or alarm icon visible |

# 10. BUILD ORDER
- Milestone 1: page opens, draws title, MAP GENERATOR, RESET, SCREENS, GAME LOOP, PLAYER MOVEMENT, and basic map rendering. Check 1 shows play starts with the player at (4,4) and the station reset.
- Milestone 2: add STATION DECAY, STATION EVENTS, and the meter HUD. Check 4 shows one second of decay reducing power to 24.5 and oxygen to 39.6.
- Milestone 3: add LOOT GENERATOR, LOCKER records, PLAYER INTERACTION, and PLAYER MEDKIT. Check 6 shows a locker opening and its items entering inventory.
- Milestone 4: add CONSOLE records, console installation, and CONSOLE UPGRADES. Check 17 shows installing a power cell at the reactor and reduced power decay.
- Milestone 5: add SPAWN SCHEDULE GENERATOR, DRONE SPAWNING, DRONE AI, and PLAYER COMBAT. Check 11 shows the first scout spawning at 15 seconds.
- Milestone 6: add VICTORY/DEATH, END SUMMARY, ALARMS, and won/dead screens. Check 14 shows the airlock win and score 513.
- Milestone 7: add audio, art, pause polish, and alarm visuals. Check 16 shows pause and resume without breaking play state.

# 11. DONE
“Survive on a derelict space station.” → Checks 1 through 19 and screenshot rows title, play, paused, won, dead, and play low power make it true.

# A. SANITY
- Every field read or written by a rule is on a record: PLAYER, STATION, UI, TILE, DOOR, LOCKER, CONSOLE, VENT, AIRLOCK, DRONE, and SPAWN_EVENT fields cover all rule references; closes.
- Every place, thing, or kind named by a rule is placed by a generator or listed in a roster: TILE base by MAP GENERATOR, consoles/lockers/vents/doors/airlock by MAP GENERATOR, item kinds by ITEM KINDS and LOOT GENERATOR, drone kinds by DRONE KINDS and SPAWN SCHEDULE GENERATOR; closes.
- Consumable power total: 3 powerCell give 90 power; STATION.power starts at 25 and decays 0.5 per second for 180 seconds, total demand 90; supply plus start is 115; closes.
- Consumable oxygen total: 3 o2Cell give 90 oxygen; STATION.oxygen starts at 40 and normal demand is 72; if power is allowed to fail for the first 50 seconds, total demand is 124; supply plus start is 130; closes.
- Consumable hull total: 3 hullPatch give 75 hull; STATION.hull starts at 70, stress events remove 25, and hull decay removes 12 after 60 seconds; total demand is 37; supply plus start is 145; closes.
- Consumable medkit total: 7 medkit give 245 health; expected combat damage if the player kills each scheduled drone promptly is scouts 6 times 5 plus brutes 3 times 36, total 138; closes. Medkit supply was changed from 3 to 7 and locker count from 6 to 8 to make this close.
- Timing power against clear: start 25 plus 90 installed cells lasts 230 seconds at base decay, greater than the 180-second escape window; closes.
- Timing oxygen against power failure: if power reaches 0 at 50 seconds, oxygen demand is 124, supply plus start is 130; closes.
- Timing drone travel against player escape: first spawn is 15 seconds, drone speed is 1.8 tiles/s, player speed is 2.2 tiles/s, so a moving player can cross a 6-tile open corridor in about 2.7 seconds while a scout takes 3.3 seconds; closes.
- Timing player combat against drone health: player damage is 12 every 0.5 seconds; scout 20 health dies in 2 attacks, brute 50 health dies in 5 attacks; drone attack cooldown 0.8 seconds lets a brute hit at most 3 times before being killed; closes.
- Every call used in section 9 appears in section 8: start, step, getState, seed, setMove, setLockerContents, teleportPlayer, interact, giveItem, setHealth, medkit, setOxygen, setTime, clearDrones, spawnDrone, unlockAirlock, attack, pause, and setPower are all listed; closes.