# 0. SCOPE

## 0.1 Asked

- "Explore a haunted forest at night" → 2D top-down map, World Generator, Player Movement, Lighting, Enemy AI, Audio Event, and code-drawn art.
- "escape before dawn" → Time, Progression, GATE record, shard pickups, and the dawn, escaped, and dead end states.

## 0.2 Decisions

- The game is 2D top-down, not 3D, because the player must read enemy positions, shard locations, the locked gate, and the shrinking light radius on one readable plane; night is the core resource and threat, and a top-down light mask makes that tension clear.
- Movement is screen-relative, not character-relative, because the player must quickly reposition on a 120 m by 120 m map and the player automatically faces the movement direction.
- The night lasts 600 seconds, because that is long enough to explore three shard locations and still feel dawn closing, but short enough that idling fails.
- Escape requires three ward shards, because the user asked to explore and escape, not merely run straight through the forest.
- The player’s lantern fuel is a consumable that also controls vision, because night is the central hazard and lighting should be a tradeoff, not decoration.
- Enemies are spectral and ignore obstacles, because the forest is haunted and the challenge should come from distance, light, fuel, and timing, not from pathing bugs around trees.
- The only attack is a lantern swing, because the game is about escape and survival, not combat progression.
- The only AI art is the title scene, because the game’s runtime is a readable stylized vector-like world, and all gameplay subjects need consistent code-drawn recipes.

## 0.3 Tiers

TIER 1 systems: World Generator, Time, Player Movement, Lighting, Combat and Fuel, Enemy AI, Interaction, Progression.

TIER 2 items, in the order to add them:

- Stalker AI adds a third enemy kind that hunts when the lantern is bright.
- Night Fog adds periodic fog events that shrink the player’s light.
- Audio Event adds footstep timing, the bell at 300 seconds, and state-change sounds.

TIER 3 items, never started before every Tier 2 item is in:

- A seed label on the title screen.
- A replay button on the end screens that restarts with the same seed.

# 1. CONVENTIONS

One unit is 1 metre. At the reference viewport, 1 metre is 16 pixels. The map is 120 metres wide and 120 metres tall. The origin is the centre of the map. The X axis points right on screen. The Y axis points down on screen. North on the map is negative Y. The player faces yaw 0 degrees toward positive X, east. Positive yaw turns clockwise on screen. The camera follows the player, centred on the player, and is clamped to the map bounds. The player radius is 0.35 metres.

The update loop uses a fixed step of 0.02 seconds. Each tick runs the systems in this order: Time, Player Movement, Lighting, Combat and Fuel, Enemy AI, Stalker AI, Interaction, Progression, Night Fog, Audio Event. Rendering happens after all systems finish.

One seeded random source is named rand. All random map placement, schedule rolls, and re-rolls use rand. Nothing else is random.

Controls:

| Input | Action |
|---|---|
| W or ArrowUp | Move screen up, inputY = -1 |
| S or ArrowDown | Move screen down, inputY = 1 |
| A or ArrowLeft | Move screen left, inputX = -1 |
| D or ArrowRight | Move screen right, inputX = 1 |
| E, Enter, or Space | Interact |
| F or Shift | Use lantern swing |
| Escape | Pause or unpause |
| Touch left half drag | Move in the drag direction; release sets move to zero |
| Touch right half tap | Interact |
| Touch bottom-right button | Use lantern swing |
| Touch top-right button | Pause or unpause |

# 2. RECORDS

RECORDS: GAME, TIME, WORLD, GATE, PLAYER, ENEMY, PICKUP, OBSTACLE, SPAWN_EVENT, FOG, AUDIO

GAME carries state, one of title, play, paused, dead, escaped, dawn; start title. GAME carries seed, integer, start 7. GAME carries stalkerSpawned, boolean, start false.

TIME carries elapsed, seconds, start 0. TIME carries dawnAt, seconds, start 600. TIME carries phase, one of night, dawn; start night.

WORLD carries sizeX, metres, start 120. WORLD carries sizeY, metres, start 120. WORLD carries spawnX, metres, start 0. WORLD carries spawnY, metres, start -50. WORLD carries waterX, metres, start 35. WORLD carries waterY, metres, start -20. WORLD carries waterRadius, metres, start 12. WORLD carries ruinX, metres, start -35. WORLD carries ruinY, metres, start 20. WORLD carries ruinHalf, metres, start 7. WORLD carries pathX, metres, start 0. WORLD carries pathYStart, metres, start -50. WORLD carries pathYEnd, metres, start 60. WORLD carries pines, list of OBSTACLE, count 90. WORLD carries rocks, list of OBSTACLE, count 18. WORLD carries pickups, list of PICKUP, count 9. WORLD carries schedule, list of SPAWN_EVENT, count 26.

GATE carries x, metres, start 0. GATE carries y, metres, start 60. GATE carries halfWidth, metres, start 2. GATE carries locked, boolean, start true.

PLAYER carries x, metres, start 0. PLAYER carries y, metres, start -50. PLAYER carries yaw, degrees, start 90. PLAYER carries radius, metres, start 0.35. PLAYER carries speed, metres per second, start 4.0. PLAYER carries health, points, start 100. PLAYER carries fuel, points, start 100. PLAYER carries shards, count, start 0. PLAYER carries inputX, ratio, start 0. PLAYER carries inputY, ratio, start 0. PLAYER carries lanternCooldown, seconds, start 0. PLAYER carries lightRadius, metres, start 12. PLAYER carries stun, seconds, start 0.

ENEMY carries id, integer, start 1 for the first enemy. ENEMY carries kind, one of shambler, wisp, stalker. ENEMY carries x, metres. ENEMY carries y, metres. ENEMY carries health, points. ENEMY carries speed, metres per second. ENEMY carries damage, points or points per second. ENEMY carries detect, metres. ENEMY carries fuelDrain, points per second. ENEMY carries attackCooldown, seconds. ENEMY carries radius, metres. ENEMY carries fuelThreshold, points.

PICKUP carries id, integer. PICKUP carries kind, one of shard, oil. PICKUP carries x, metres. PICKUP carries y, metres. PICKUP carries active, boolean, start true.

OBSTACLE carries id, integer. OBSTACLE carries kind, one of pine, rock. OBSTACLE carries x, metres. OBSTACLE carries y, metres. OBSTACLE carries radius, metres. OBSTACLE carries solid, boolean, start true.

SPAWN_EVENT carries id, integer. SPAWN_EVENT carries time, seconds. SPAWN_EVENT carries pointIndex, integer 0 through 7. SPAWN_EVENT carries roll, ratio 0 through 1. SPAWN_EVENT carries done, boolean, start false.

FOG carries active, boolean, start false. FOG carries timer, seconds, start 0. FOG carries nextEvent, seconds, start 60. FOG carries radiusReduce, metres, start 2.

AUDIO carries last, sound name, start none. AUDIO carries footstepTimer, seconds, start 0.

ROSTER: ENEMY

| kind | speed metres/second | health points | damage value | damage meaning | detect metres | fuelDrain points/second | attackCooldown seconds | radius metres | fuelThreshold points |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|
| shambler | 1.1 | 40 | 10 | per attack | 18 | 0 | 1.0 | 0.45 | 0 |
| wisp | 2.0 | 25 | 4 | per second after fuel empty | 12 | 20 | 0 | 0.30 | 0 |
| stalker | 1.5 | 30 | 8 | per second while touching | 10 | 0 | 0 | 0.40 | 40 |

ROSTER: PICKUP

| kind | effect field | value |
|---|---|---:|
| shard | PLAYER.shards | +1 |
| oil | PLAYER.fuel | +25 |

ROSTER: OBSTACLE

| kind | radius metres | solid |
|---|---:|---|
| pine | 1.1 | true |
| rock | 0.8 | true |

ROSTER: SPAWN POINTS

| pointIndex | x metres | y metres |
|---:|---:|---:|
| 0 | -20 | -30 |
| 1 | 40 | 10 |
| 2 | -45 | 0 |
| 3 | 45 | 0 |
| 4 | -45 | 35 |
| 5 | 45 | 35 |
| 6 | 0 | -40 |
| 7 | 0 | 40 |

ROSTER: SOUND

| sound name |
|---|
| footstep |
| swing |
| enemy hit |
| shambler attack |
| wisp drain |
| pickup |
| gate unlock |
| bell |
| dawn chime |
| escape |
| death |
| wind |

# 3. SYSTEMS

SYSTEMS: World Generator, Time, Player Movement, Lighting, Combat and Fuel, Enemy AI, Stalker AI, Interaction, Progression, Night Fog, Audio Event

## World Generator (T1)

- On seed(n), set GAME.seed to n, reseed rand, set GAME.state to title, set GAME.stalkerSpawned to false, set TIME.elapsed to 0, set TIME.dawnAt to 600, set TIME.phase to night, set GATE.locked to true, set FOG.active to false, set FOG.timer to 0, set FOG.nextEvent to 60, set AUDIO.last to none, and set AUDIO.footstepTimer to 0.
- The generator places fixed WORLD fields: sizeX 120, sizeY 120, spawnX 0, spawnY -50, waterX 35, waterY -20, waterRadius 12, ruinX -35, ruinY 20, ruinHalf 7, pathX 0, pathYStart -50, pathYEnd 60.
- The generator places four ruin boulders as OBSTACLE kind rock at (-42, 13), (-28, 13), (-42, 27), and (-28, 27).
- The generator places nine fixed PICKUP items in this order: shard at (-35, 20), shard at (45, -5), shard at (-45, -5), oil at (0, -35), oil at (-20, -5), oil at (20, 0), oil at (-15, 35), oil at (15, 35), and oil at (0, 50).
- The generator creates 26 SPAWN_EVENT items in this order: event 1 has time 10 and pointIndex 0; event 2 has time 10 and pointIndex 1; for event i from 3 through 26, time is 40 + 20 * (i - 3) and pointIndex is i modulo 8. Each event’s roll is one draw from rand, and done is false.
- The generator places 90 pines and 18 rocks as OBSTACLE items. For each object, it makes up to 200 attempts. Each attempt draws x from -58 + rand * 116 and y from -58 + rand * 116. An attempt is valid if the point is at least 2.0 metres from the path centreline segment from (0, -50) to (0, 60), at least 10.0 metres from spawn, at least 13.0 metres from water, at least 10.0 metres from ruin centre, at least 4.0 metres from gate, and at least 2.5 metres from every placed pine or 3.0 metres from every placed rock.
- VERIFIER: WORLD.pines has exactly 90 items, WORLD.rocks has exactly 18 items, WORLD.pickups has exactly 9 items, WORLD.schedule has exactly 26 items, no pine or rock violates the placement distances above, and no pickup is within 1.0 metre of any obstacle. Re-roll with the next seed if any check fails.

## Time (T1)

- If GAME.state is play, TIME.elapsed increases by dt each tick.
- If GAME.state is not play, TIME.elapsed does not change.

## Player Movement (T1)

- If GAME.state is not play, PLAYER.inputX and PLAYER.inputY are ignored and PLAYER does not move.
- If PLAYER.stun is greater than 0, PLAYER.stun decreases by dt and does not go below 0.
- The player’s movement speed is 4.0 metres per second. If PLAYER.stun is greater than 0, movement speed is 0. If the player is within waterRadius metres of the water centre, movement speed is 2.4 metres per second.
- If the input vector is not zero, normalize it, move PLAYER.x and PLAYER.y by input times movement speed times dt, and set PLAYER.yaw to the angle of the input vector in degrees.
- The player cannot leave the map. If PLAYER.x is less than -60 + PLAYER.radius, set it to -60 + PLAYER.radius. If PLAYER.x is greater than 60 - PLAYER.radius, set it to 60 - PLAYER.radius. If PLAYER.y is less than -60 + PLAYER.radius, set it to -60 + PLAYER.radius.
- The south boundary is solid except through the gate. If PLAYER.y is greater than 59.5 and either PLAYER.x is not within GATE.halfWidth metres of GATE.x or GATE.locked is true, set PLAYER.y to 59.5. If PLAYER.y is greater than 60 - PLAYER.radius and GATE.locked is false and PLAYER.x is within GATE.halfWidth metres of GATE.x, set PLAYER.y to 60 - PLAYER.radius.
- The player collides with solid OBSTACLE items. If the distance between the player and an obstacle is less than PLAYER.radius + obstacle.radius, push the player away along the line from obstacle to player until the distance equals the sum of their radii. If the player cannot be pushed out, stop movement.

## Lighting (T1)

- If GAME.state is play, PLAYER.fuel decreases by 0.1 * dt and does not go below 0.
- PLAYER.lightRadius is 4 + 8 * (PLAYER.fuel / 100).
- If FOG.active is true, PLAYER.lightRadius decreases by FOG.radiusReduce and does not go below 2.

## Combat and Fuel (T1)

- If GAME.state is play, PLAYER.lanternCooldown decreases by dt and does not go below 0.
- When the player uses the lantern and PLAYER.lanternCooldown is 0, set PLAYER.lanternCooldown to 0.5.
- If PLAYER.fuel is at least 5 when the lantern is used, PLAYER.fuel decreases by 5 and swing damage is 20. If PLAYER.fuel is less than 5, swing damage is 10.
- Each active ENEMY within 1.8 metres of the player and within 60 degrees of PLAYER.yaw takes swing damage. If an enemy’s health is 0 or less, remove it.
- When a swing hits at least one enemy, AUDIO.last is enemy hit. When a swing hits no enemy, AUDIO.last is swing.

## Enemy AI (T1)

- The opponent perceives the player by distance. It decides to pursue when distance is within its detect range. It acts by moving toward the player, attacking, or draining fuel.
- If FOG.active is true, each enemy’s effective detect range is roster detect minus 2, but never below 5.
- For each SPAWN_EVENT not done, if TIME.elapsed is at least its time and there are fewer than 6 active enemies, spawn one enemy at SPAWN POINTS[event.pointIndex]. If event.roll is less than 0.6, the kind is shambler; otherwise the kind is wisp. Mark the event done. If there are 6 or more active enemies, mark the event done without spawning.
- A shambler acts as follows. If distance to the player is at most 0.9 metres, it does not move. If distance is at most its effective detect and greater than 0.9, it moves toward the player at 1.1 metres per second. If distance is at most 0.9 and attackCooldown is 0, the player takes 10 damage, the shambler’s attackCooldown becomes 1.0, and AUDIO.last is shambler attack. If distance is greater than 1.0, the shambler’s attackCooldown becomes 0.
- A wisp acts as follows. If distance to the player is at most 1.2 metres, it does not move. If distance is at most its effective detect and greater than 1.2, it moves toward the player at 2.0 metres per second. If distance is at most 1.2, PLAYER.fuel decreases by 20 * dt. If PLAYER.fuel is 0, PLAYER.health decreases by 4 * dt. AUDIO.last is wisp drain while the wisp is draining.
- Enemies ignore obstacles and water.

## Stalker AI (T2)

- If GAME.state is play, GAME.stalkerSpawned is false, TIME.elapsed is at least 180, and there are fewer than 6 active enemies, spawn one stalker at (0, 30) and set GAME.stalkerSpawned to true.
- A stalker acts only while PLAYER.fuel is greater than its fuelThreshold of 40. If PLAYER.fuel is at most 40, it does not move and deals no damage.
- If distance to the player is at most 1.0 metre, the stalker does not move, PLAYER.health decreases by 8 * dt, and PLAYER.stun becomes at least 1.0.
- If distance is greater than 1.0 and at most its effective detect range, the stalker moves toward the player at 1.5 metres per second.

## Interaction (T1)

- When the player interacts, the game finds the nearest active PICKUP within 1.5 metres. If the pickup is a shard, PLAYER.shards increases by 1 and does not exceed 3. If the pickup is oil, PLAYER.fuel increases by 25 and does not exceed 100. The pickup becomes inactive and AUDIO.last is pickup.
- If no pickup is in range, the game checks the gate. If the player is within 2.0 metres of the gate and PLAYER.shards is at least 3, GATE.locked becomes false and AUDIO.last is gate unlock. If PLAYER.shards is less than 3, nothing changes.

## Progression (T1)

- If GAME.state is play and PLAYER.health is 0 or less, GAME.state becomes dead and AUDIO.last is death.
- If GAME.state is play, GATE.locked is false, PLAYER.y is greater than 59.5, and PLAYER.x is within GATE.halfWidth metres of GATE.x, GAME.state becomes escaped and AUDIO.last is escape.
- If GAME.state is play and TIME.elapsed is at least TIME.dawnAt, GAME.state becomes dawn, TIME.phase becomes dawn, and AUDIO.last is dawn chime.

## Night Fog (T2)

- If GAME.state is play and FOG.active is true, FOG.timer decreases by dt. If FOG.timer is 0 or less, FOG.active becomes false.
- If GAME.state is play, FOG.active is false, and TIME.elapsed is at least FOG.nextEvent, FOG.active becomes true, FOG.timer becomes 10, FOG.nextEvent increases by 45, and AUDIO.last is wind.

## Audio Event (T2)

- If GAME.state becomes play from title, AUDIO.last is wind.
- While GAME.state is play and the player is moving, AUDIO.footstepTimer increases by dt. If AUDIO.footstepTimer is at least 0.45, reset it to 0 and play footstep. If the player is in water, the footstep frequency is 80 instead of 120.
- If GAME.state is play and TIME.elapsed reaches 300, AUDIO.last is bell.
- If GAME.state becomes dead, AUDIO.last is death. If GAME.state becomes dawn, AUDIO.last is dawn chime. If GAME.state becomes escaped, AUDIO.last is escape.

# 4. CORE LOOP

Minute to minute, the player does this: move through the forest, collect the three ward shards, manage lantern fuel, avoid or swing at enemies, unlock the gate, and run south before dawn. The cycle is: Player Movement through the World Generator’s map, Lighting shrinking as fuel drains, Enemy AI spawning and pursuing, Combat and Fuel used to clear threats, Interaction collecting shards and unlocking the gate, Progression ending the run on death, escape, or dawn. What grows is the player’s shard count and the world’s threat level over time. What unlocks is the gate after three shards. The end is one of escaped, dead, or dawn. If the player escapes, the night ends successfully. If dawn arrives first, the player is trapped in the forest. If health reaches zero, the player dies.

# 5. SCREENS

title (AI haunted forest scene, title text, "Press Enter") → play (game world, HUD, darkness, player light) → paused (dimmed world, "Paused") → play. play → dead (dark red overlay, "You died"). play → dawn (bright horizon, "Dawn arrived"). play → escaped (bright gate, "You escaped"). dead → title on Enter. dawn → title on Enter. escaped → title on Enter. Escape toggles play and paused while in play or paused. Escape does nothing on title, dead, dawn, or escaped.

HUD:

| HUD element | Record field shown |
|---|---|
| Time to dawn | TIME.dawnAt - TIME.elapsed |
| Health | PLAYER.health |
| Fuel | PLAYER.fuel |
| Shards | PLAYER.shards |
| Gate state | GATE.locked |
| State | GAME.state |

# 6. AUDIO

All audio is generated with the Web Audio API.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| footstep | triangle, 120 Hz, 0.04 s, attack 0.005 s, decay 0.035 s | every 0.45 s while the player is moving in play; 80 Hz if in water |
| swing | sawtooth, 160 Hz, 0.08 s, attack 0.005 s, decay 0.075 s | when the player uses the lantern and hits no enemy |
| enemy hit | square, 90 Hz, 0.05 s, attack 0.002 s, decay 0.048 s | when the player’s lantern swing hits at least one enemy |
| shambler attack | sawtooth, 55 Hz, 0.5 s, attack 0.1 s, decay 0.4 s | when a shambler deals its 10-point attack |
| wisp drain | sine, 440 Hz, 0.25 s, attack 0.05 s, decay 0.2 s | while a wisp is within 1.2 metres and draining fuel |
| pickup | sine, 660 Hz, 0.12 s, attack 0.01 s, decay 0.11 s | when a shard or oil pickup is collected |
| gate unlock | square, 220 Hz rising to 440 Hz, 0.3 s, attack 0.02 s, decay 0.28 s | when the gate is unlocked |
| bell | sine, 330 Hz, 0.6 s, attack 0.05 s, decay 0.55 s | when TIME.elapsed reaches 300 |
| dawn chime | sine, 523 Hz, 0.8 s, attack 0.1 s, decay 0.7 s | when GAME.state becomes dawn |
| escape | triangle, 523 Hz, 0.4 s, attack 0.02 s, decay 0.38 s | when GAME.state becomes escaped |
| death | sine, 80 Hz, 0.8 s, attack 0.05 s, decay 0.75 s | when GAME.state becomes dead |
| wind | filtered noise, 300 Hz, looped, volume 0.2 | while GAME.state is play; stops on other states |

# 7. ART

Ask for a haunted forest title screen as a scene. That is the only AI art.

RECIPE: map ground is a 120 m by 120 m rectangle, colour #101b14.
RECIPE: path is a 3 m wide rectangle from y -50 to y 60 at x 0, colour #4a3b2a.
RECIPE: water is a circle at (35, -20) with radius 12 m, colour #16323a.
RECIPE: ruin is a 14 m by 14 m square at (-35, 20), colour #3c4138.
RECIPE: ruin boulders are four circles of radius 0.8 m at (-42, 13), (-28, 13), (-42, 27), and (-28, 27), colour #4b4b52.
RECIPE: pine is a circle of radius 1.1 m, colour #1d3526, with an inner circle of radius 0.7 m, colour #2a4d34.
RECIPE: rock is a circle of radius 0.8 m, colour #4b4b52.
RECIPE: player is a circle of radius 0.35 m, colour #d9d4c4, with a facing line 0.4 m long and 0.08 m wide, colour #ffcf6e, and a lantern dot of radius 0.12 m, colour #ffcf6e.
RECIPE: shambler is a circle of radius 0.45 m, colour #2a2330, with two eye dots of radius 0.05 m, colour #e4ff7a.
RECIPE: wisp is a circle of radius 0.30 m, colour #8ce8ff.
RECIPE: stalker is a circle of radius 0.40 m, colour #12121a, with two eye dots of radius 0.05 m, colour #ff4d6d.
RECIPE: shard is a diamond 0.5 m tall and 0.35 m wide, colour #74f7c1.
RECIPE: oil is a 0.3 m by 0.5 m rectangle, colour #a35b2b, with a 0.15 m cap, colour #d9d4c4.
RECIPE: gate posts are two circles of radius 0.3 m at (-2, 60) and (2, 60), colour #6a4a32. When GATE.locked is true, a 4.4 m by 0.4 m bar across the gap is drawn, colour #6a4a32. When GATE.locked is false, the bar is hidden.
RECIPE: darkness is a full-screen fill of #000000 with a transparent circle around the player of radius PLAYER.lightRadius.

Everything else — title text, map, pines, rocks, water, ruin, path, gate, player, enemies, pickups, darkness, HUD — is drawn in code.

# 8. DEBUG API

The game installs window.__game. Every call is synchronous and returns only plain data.

| Call | What it does | What it returns |
|---|---|---|
| start() | Enters play from title or an end state by resetting with the current seed | GAME.state |
| step(dt, n) | Advances n ticks of dt seconds, runs all systems, then draws once | TIME.elapsed |
| setTime(t) | Advances forward in 0.02 s ticks until TIME.elapsed is at least t, without drawing | TIME.elapsed |
| seed(n) | Sets GAME.seed to n, reseeds rand, rebuilds the world, schedule, and initial state | getState() |
| getState() | Returns all record fields as plain data | full state object |
| setMove(x, y) | Sets PLAYER.inputX and PLAYER.inputY; persists until changed | { x, y } |
| interact() | Triggers the Interaction system once | pickup id, "gate", or false |
| useLantern() | Triggers the Combat and Fuel swing once | { fuel, hit } where hit is a list of enemy ids |
| togglePause() | Toggles between play and paused | GAME.state |
| setDawnAt(n) | Sets TIME.dawnAt to n | n |
| clearEnemies() | Removes all active enemies | count removed |
| disableSpawns() | Marks every SPAWN_EVENT done and sets GAME.stalkerSpawned true | count disabled |
| spawnEnemy(kind, x, y) | Adds one enemy of the given kind at the given place with roster values | enemy id |
| placePickup(kind, x, y) | Adds one active pickup of the given kind at the given place | pickup id |
| setFuel(n) | Sets PLAYER.fuel clamped to 0 through 100 and recalculates PLAYER.lightRadius | { fuel, lightRadius } |
| setHealth(n) | Sets PLAYER.health clamped to 0 through 100 | PLAYER.health |
| addShard(n) | Sets PLAYER.shards to n clamped to 0 through 3 | PLAYER.shards |
| setFog(active) | Sets FOG.active; if true, sets FOG.timer to 10 | FOG.active |
| setGateLocked(locked) | Sets GATE.locked | GATE.locked |
| playSound(name) | Plays the named recipe and sets AUDIO.last | name |

# 9. TESTS

1. seed(7); getState(): GAME.state is title, WORLD.pines.length is 90, WORLD.rocks.length is 18, WORLD.pickups.length is 9, WORLD.schedule.length is 26, GATE.locked is true, TIME.dawnAt is 600.
2. seed(7); start(); getState(): GAME.state is play, TIME.elapsed is 0, PLAYER.health is 100, PLAYER.fuel is 100, PLAYER.shards is 0.
3. seed(7); start(); setMove(0, -1); step(0.02, 50); getState(): PLAYER.y is between -54.01 and -53.99, GAME.state is play.
4. seed(7); start(); clearEnemies(); disableSpawns(); setTime(600); getState(): GAME.state is dawn, TIME.phase is dawn, AUDIO.last is dawn chime.
5. seed(7); start(); clearEnemies(); disableSpawns(); setMove(0, 1); setTime(30); getState(): GAME.state is play, PLAYER.y is between 59.4 and 59.6, GATE.locked is true.
6. seed(7); start(); clearEnemies(); disableSpawns(); setFuel(0); getState(): PLAYER.fuel is 0, PLAYER.lightRadius is 4.0.
7. seed(7); start(); clearEnemies(); disableSpawns(); spawnEnemy("shambler", 0.5, -50); setHealth(100); step(0.02, 25); getState(): PLAYER.health is between 89.9 and 90.1.
8. seed(7); start(); clearEnemies(); disableSpawns(); spawnEnemy("wisp", 1, -50); setFuel(100); setHealth(100); step(0.02, 100); getState(): PLAYER.fuel is between 59.7 and 59.9.
9. seed(7); start(); clearEnemies(); disableSpawns(); placePickup("shard", 0, -48); setMove(0, 1); step(0.02, 25); interact(); getState(): PLAYER.shards is 1.
10. seed(7); start(); clearEnemies(); disableSpawns(); addShard(3); setMove(0, 1); setTime(30); interact(); step(0.02, 1); getState(): GAME.state is escaped, AUDIO.last is escape.
11. seed(7); start(); clearEnemies(); disableSpawns(); spawnEnemy("shambler", 1, -50); setFuel(100); setMove(1, 0); step(0.02, 1); useLantern(); getState(): PLAYER.fuel is between 94.9 and 95.1, enemies[0].health is between 19.9 and 20.1.
12. seed(7); start(); clearEnemies(); disableSpawns(); spawnEnemy("stalker", 0.5, -50); setFuel(100); setHealth(100); step(0.02, 50); getState(): PLAYER.health is between 91.9 and 92.1.
13. seed(7); start(); clearEnemies(); disableSpawns(); setFuel(100); setFog(true); getState(): FOG.active is true, PLAYER.lightRadius is 10.0.
14. seed(7); start(); clearEnemies(); disableSpawns(); placePickup("oil", 0, -48); setMove(0, 1); step(0.02, 25); interact(); getState(): AUDIO.last is pickup, PLAYER.fuel is 125 clamped to 100.
15. seed(7); start(); togglePause(); getState(): GAME.state is paused.
16. seed(7); start(); togglePause(); togglePause(); getState(): GAME.state is play.
17. seed(7); start(); setHealth(0); step(0.02, 1); getState(): GAME.state is dead, AUDIO.last is death.

SCREENSHOTS:

| Screen and state | What a person must see | Related check |
|---|---|---|
| Title | AI haunted forest scene, title text, "Press Enter" | 1 |
| Play after movement | Player in the north clearing, circular lantern light, visible path south, HUD time near 599 | 3 |
| Play at locked gate | Player at the south gate, locked gate bar visible, HUD shards 0 | 5 |
| Play in fog | Smaller lantern circle, darker surroundings, HUD fuel 100 | 13 |
| Paused | Dimmed world and "Paused" overlay | 15 |
| Dawn | Bright horizon and "Dawn arrived" text | 4 |
| Escaped | Bright gate area and "You escaped" text | 10 |
| Dead | Dark red overlay and "You died" text | 17 |

# 10. BUILD ORDER

Milestone 1: add the title screen, World Generator, Time, Player Movement, and HUD. Check 3 shows it landed.

Milestone 2: add Lighting, Combat and Fuel, Interaction, and gate progression. Check 9 shows it landed.

Milestone 3: add Enemy AI, spawn schedule, enemy damage, and lantern combat. Check 11 shows it landed.

Milestone 4: add Stalker AI, Night Fog, and Audio Event. Check 13 shows it landed.

Milestone 5: add end states, death, dawn, and escape polish. Check 10 shows it landed.

# 11. DONE

"Explore a haunted forest at night":

- Checks 1, 3, 5, and 13 make the forest, movement, locked gate, and night lighting true.
- Screenshot rows: title, play after movement, play at locked gate, play in fog.

"escape before dawn":

- Checks 4, 10, and 17 make dawn, escaped, and dead end states true.
- Screenshot rows: dawn, escaped, dead.

The game is finished when every line above is true.

# A. SANITY

- Every field a rule reads or writes is on a record: PLAYER.stun, ENEMY.fuelThreshold, GATE.locked, FOG.nextEvent, AUDIO.footstepTimer, SPAWN_EVENT.done, and GAME.stalkerSpawned all exist. Result: closes.
- Every place, thing, or kind a rule names is placed by a generator or listed in a roster: pines, rocks, pickups, schedule, water, ruin, and gate are placed by the World Generator; shambler, wisp, and stalker are in the ENEMY roster; shard and oil are in the PICKUP roster; spawn points are in the SPAWN POINTS roster. Result: closes.
- Consumable totals against core-loop demand: fuel total is 100 starting plus six oil pickups at 25 each, 250 fuel. Passive drain over 600 seconds is 60 fuel. The six-enemy cap can be cleared with 12 successful two-swing kills, 60 fuel, if the player chooses to clear it. Shards total 3 placed against the gate demand of 3. Result: closes.
- Timing pairs: spawn schedule adds one event every 20 seconds from 40 to 500 with a cap of 6 alive; the player can outrun shamblers and wisps and can clear a capped group with 12 swings. Fuel drain is 0.1 per second, and oil refills 25 at six locations. Travel from spawn to gate is 110 metres at 4 metres per second, 27.5 seconds, against 600 seconds to dawn. Fog events last 10 seconds and recur every 45 seconds. Result: closes.
- Every call section 9 makes is in section 8: seed, start, getState, step, setTime, setMove, clearEnemies, disableSpawns, spawnEnemy, setHealth, setFuel, placePickup, interact, addShard, useLantern, setFog, and togglePause are all listed. Result: closes.