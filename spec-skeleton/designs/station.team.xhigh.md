# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Survive on a derelict space station | Section 4: Player, Life Support, Station Power, Hazards, Enemies, Daily Cycle |
| Added: 2D top-down station cross-section with tile-based movement | Section 1, Section 3, Section 4: Map Generator, Player |
| Added: collect scrap, batteries, filters, coolant, emergency supplies | Section 4: Records, Map Generator, Interact, Crafting |
| Added: repair power bays, oxygen scrubbers, hull seals | Section 4: Station Power, Life Support, Player |
| Added: fight awakened maintenance drones that hunt by sight and noise | Section 4: Enemies, Player |
| Added: personal oxygen and station oxygen management | Section 4: Life Support |
| Added: day counter, threat level, random station events | Section 4: Daily Cycle, Threat Event roster |
| Added: beacon milestones that unlock small permanent upgrades | Section 4: Daily Cycle |
| Added: best day and best score across runs | Section 4: Run Record, Life Support game over rule |
| Added: HUD, screens, touch controls | Section 7 |
| Added: Web Audio API generated feedback | Section 6 |
| Added: debug API and deterministic tests | Section 8, Section 9 |

## 0.2 Decisions

| Topic | Gameplay said | Visual said | Engineering said | Ruling and one clause why |
| --- | --- | --- | --- | --- |
| Perspective | 2D top-down orthographic camera follows player | 3D first-person eye-level camera | 2D Canvas 2D | T1 is 2D top-down Canvas 2D; true 3D first-person is T2, because two documents agree on 2D and the engineering budget is 2D. |
| Camera | Top-down follow | Eye-level, 72 degree vertical FOV, yaw unlimited, pitch clamped | Render after update ticks | T1 camera is centered on the player, no rotation; T2 adds first-person yaw/pitch, because T1 must use the fixed-step 2D loop. |
| World size | 48 by 30 tile world | 48 by 30 by 4.2 unit bounding box | Floor bounds 0 to 30000 on both axes | World is 48 by 30 tiles, 1 tile equals 1 metre equals 10000 game units, so bounds are x 0 to 480000 and y 0 to 300000, because gameplay and visual agree on 48 by 30. |
| Unit scale | Tile and seconds | 1 game unit equals 1 metre | 100 game units equals 1 CSS pixel | 1 metre equals 10000 game units and 100 game units equals 1 CSS pixel, because this keeps visual metre sizes, engineering pixel scale, and tile gameplay together. |
| Resource precision | Decimal points per second | No resource numbers | Integer centipercents per tick | Resource values use 10000 units per point, so 100 points equals 1000000 units and every listed decimal rate becomes integer units per 10 ms tick, because centipercents cannot represent 0.35 point per second exactly. |
| Facing | Radians, atan2, 60 degree and 120 degree arcs | Yaw/pitch first person | Integer octants | Facing is stored as integer centiradians, 0 to 6283, 0 equals plus x, because gameplay needs exact arc checks and determinism needs integer state. |
| Station layout | Generated 48 by 30 rooms, hub console, corridors | Six fixed modules around central hub | Walls, doors, pickups | T1 uses the generated 48 by 30 layout; visual modules become room decoration presets; engineering wall records become a 48 by 30 floor grid, because the core loop needs many generated rooms and no fixed module set. |
| Doors | No door rules | Closed/open/jammed doors | Door records and interaction | T1 has no physical doors; doorway status lights are cosmetic; door animation and door interaction are T2, because generated tile reachability must remain simple and deterministic. |
| Start and goal | Player start at 23.5, 15.5, no scripted ending | Start in Medbay, goal escape pod | No start/goal | T1 starts in a Medbay-decorated generated room at 23.5, 15.5; there is no escape-pod victory; the airlock is cosmetic T2, because the request is to survive, not escape. |
| Enemy roster | Mite, wraith, overseer with stats | One Scav Bot design | No enemy records | T1 uses mite, wraith, and overseer; the Scav Bot is the mite visual, and wraith/overseer variants are derived from it, because gameplay supplies the only complete enemy stats. |
| Hazards | Fixed vent and radiation areas | Hull breach mist, emergency lights | Moving plasma hazard with speed and damage | T1 hazards are fixed vent and radiation areas; the engineering moving plasma hazard is T2; breach mist visuals are used on active radiation hazards, because gameplay defines the survival drain rules. |
| Oxygen model | Player oxygen and station oxygen | HUD O2 bar | Single oxygen field | T1 keeps player oxygen and station oxygen; engineering single oxygen is ruled out, because scrubbers, hull, vents, and player suit all need separate values. |
| Stage completion | No stage; run ends on health 0 or hull 0 | No stage | Stage kits required | Engineering stage/kits are ruled out and replaced by Run Record and death conditions, because the gameplay loop has no kit objective. |
| Controls | Movement, sprint, attack, interact, slots, craft, pause | No controls | Move and interact only | T1 uses the merged controls table in Section 1, because the gameplay rules need attack, interact, slots, crafting, and pause. |
| Initial seed | No seed uses current time milliseconds | No seed rule | Math.random and Date.now not allowed for game logic | Date.now is allowed only once when creating a new run from UI to choose a seed; fixed-tick logic uses only Rng, because gameplay wants varied runs and engineering wants deterministic ticks. |
| Beacon day 3 field | beacon_day3 boolean with no explicit rule | No beacon rule | No beacon rule | When day reaches 3, beaconDay3 becomes true and beacon increases by 5 capped at 100, because the field exists in the gameplay record and needs a use. |
| Audio | No audio recipes | Visual feedback names | Audio module and queue | T1 uses the Web Audio table in Section 6, because feedback events are named by gameplay and visual but not by engineering. |
| Touch | Virtual joystick and Action, Attack, Sprint, Item buttons | No touch rule | Touch drag and tap | T1 uses the merged touch controls in Section 1, because gameplay names the four touch buttons and engineering names drag/tap. |
| Visual recipe sizes | No visual sizes | Sizes in metres | No visual sizes | All visual sizes are metres; multiply by 10000 for game units; height is used for sprite sort only in T1, because T1 is top-down. |
| Entity budget | 24 loot, 6 hazards, up to 8 drones, 13 station objects | Many decorative counts | Active dynamic entities 112, draw ops 120 | T1 caps are loot 48, hazards 24, enemies 16, station objects 13; decorative visual counts are culled or pre-baked in T1, because the engineering budget must hold. |
| Coolant supply | Coolant item and hazard disable rule, but initial loot list has no coolant | No coolant rule | No coolant rule | Add 3 coolant containers to the Medbay start room and add 1 coolant drop on every enemy death, because the rules can demand coolant but the original loot list cannot supply it. |

## 0.3 Tiers

**T1 is the game that must ship:** Map Generator, Player, Interact, Life Support, Station Power, Hazards, Enemies, Crafting, Daily Cycle, HUD/UX, Audio, Run Record, Debug/Test harness.

**T2 items, in order to add:**

1. True 3D first-person presentation using the visual recipe table, yaw/pitch camera, and first-person hand.
2. Interactable doors with closed/open/jammed states and door audio.
3. Escape pod victory sequence in the Escape Airlock room.
4. Moving plasma hazard entity from engineering, with speed and damage.
5. Full post-processing: grain, vignette, death desaturation, hit-stop, death shake.
6. Full particle set: 400 dust motes, hydro mist, hull breach bubbles, bot smoke, spark systems.
7. Continuous ambient audio loops beyond the one-shot event table.
8. Additional room presets beyond the seven visual regions, using neutral storage/utility language.

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- 100 game units equals 1 CSS pixel.
- 1 metre equals 1 tile equals 10000 game units.
- World size is 48 tiles by 30 tiles, so world bounds are x 0 to 480000 and y 0 to 300000.
- x increases right, y increases down. Up is negative y.
- Origin is the top-left corner of tile 0, 0.
- Tile index is floor coordinate divided by 10000.
- One canonical tick is 10 milliseconds. `dt` is 0.01 seconds per tick.
- `tick` is an integer. `timeMs` is an integer.
- Resource values use 10000 units per point. 100 points equals 1000000 units. Load values use the same scale; load 10 equals 100000 units.
- Speeds are integer game units per tick.
  - Walk speed: 3 tile/s equals 300 units/tick.
  - Sprint speed: 5 tile/s equals 500 units/tick.
  - Acceleration: 12 tile/s squared equals 12 units/tick per tick.
  - Deceleration: 20 tile/s squared equals 20 units/tick per tick.
  - Mite base speed: 2.2 tile/s equals 220 units/tick.
  - Wraith base speed: 1.8 tile/s equals 180 units/tick.
  - Overseer base speed: 1.6 tile/s equals 160 units/tick.
- Facing is integer centiradians. 100 centiradians equals 1 radian. Full turn is 6283 centiradians. 0 equals plus x. 60 degrees is 600 centiradians. 120 degrees is 1200 centiradians.
- Distances are game units unless stated as tiles or metres. Gameplay radii convert by multiplying tiles or metres by 10000.

## 1.2 Important conventions

**Loop.** `requestAnimationFrame` accumulates elapsed milliseconds, clamps accumulated time to 20 milliseconds, runs whole 10 ms ticks, then draws once.

**System order each tick.**

1. `Input`
2. `Player`
3. `Interact`
4. `Enemies`
5. `Hazards`
6. `LifeSupport`
7. `Power`
8. `Daily`
9. `Audio`
10. `Renderer.draw()`

**Randomness.** One named source, `Rng`, uses the Lehmer LCG:

```js
rngState = (rngState * 16807) % 2147483647;
if (rngState === 0) rngState = 1;
next = rngState / 2147483647;
```

All tick logic uses only `Rng`. `Math.random` is forbidden in tick logic. `Date.now` is allowed only once when creating a new run from UI to choose an initial seed; it is never used inside a tick.

**Input convention.** Movement is persistent. Actions are edge-queued and consumed once per tick. Craft selection is stored in `G.craft.selected`.

**Collision convention.** The player is a point for tile collision. If the next tile on an axis is wall, cancel that axis and zero that axis velocity. Enemy movement is blocked by wall tiles and slides perpendicular to the target direction.

**Line of sight.** Line of sight exists if a straight segment from enemy to player does not pass through a wall tile.

**Budgets.**

- Target frame time is 16 ms.
- Maximum catch-up is 2 ticks, 20 ms, then drop the rest.
- `frame.drawOps` must be 120 or less per rendered frame.
- Entity caps: loot 48, hazards 24, enemies 16, station objects 13. Active dynamic entities must be 112 or less.
- Audio queue maximum is 16. Active Web Audio sources maximum is 4.
- `JSON.stringify(getState()).length` must be 65536 or less at maximum entity caps.
- No per-tick allocations except short-lived Web Audio source nodes.

**Engineering risks carried as rules.**

1. Coordinate convention error: all game code uses y-down integer game units after input is read; no coordinate conversion is allowed.
2. Timing race: the loop only runs whole 10 ms ticks, input is edge-queued and consumed once per tick, and debug `step` and `setTime` bypass real time.
3. Performance cliff: fixed caps, draw-op budget, spawner rejection when full, and renderer stops adding draw operations once the budget is reached.

**Controls.**

| Input | Action |
| --- | --- |
| W / ArrowUp | move(0,-1) |
| S / ArrowDown | move(0,1) |
| A / ArrowLeft | move(-1,0) |
| D / ArrowRight | move(1,0) |
| Release all movement input | move(0,0) |
| Shift hold | sprint held true |
| Shift release | sprint held false |
| Space / J pressed | attack() |
| E pressed | interact() |
| Q / Tab pressed | cycleSlot() |
| Number 1 to 10 pressed while craft menu closed | selectSlot(number) |
| Number 1 to 4 pressed while craft menu open | craftSelect(number) |
| P / Escape pressed | pauseToggle() or close craft menu if open |
| Touch left virtual joystick | move(dominant x sign, dominant y sign) |
| Touch left virtual joystick release | move(0,0) |
| Touch right Action button | interact() |
| Touch right Attack button | attack() |
| Touch right Sprint button hold | sprint held true |
| Touch right Item button | cycleSlot() |

# 2. CONTRACTS

## 2.1 Module layout

| Module | Responsibility |
| --- | --- |
| `Loop` | Fixed-timestep scheduling and render dispatch |
| `Input` | Keyboard/touch to `G.input` and action queues |
| `Rng` | Seeded random source |
| `World` | Floor grid, rooms, station objects, loot, hazards, enemies, placement, reachability, line of sight |
| `Player` | Movement, facing, sprint, stamina, attack, interaction state, player survival |
| `Interact` | Nearest target selection, interaction timers, loot, items, objects, hazards, craft triggers |
| `Enemies` | Spawn scaling, perception, patrol/search/chase/windup, object sabotage, death |
| `Hazards` | Vent/radiation timers, disable timer, oxygen/health effects |
| `LifeSupport` | Player oxygen, station oxygen, health, game over |
| `Power` | Station power drain, scrubber cost, power bay generation |
| `Crafting` | Craft menu, recipes, craft timer, item consumption |
| `Daily` | Day timer, threat escalation, daily generator, threat events, beacon milestones |
| `Audio` | Web Audio event playback and audio queue |
| `Renderer` | Canvas 2D drawing and draw-op count |
| `Debug` | Installs `window.__game` |

Modules communicate only through one global context, `G`. No module imports another except through `G`.

## 2.2 Global context

```js
const G = {
  state: 'title', // 'title' | 'run' | 'pause' | 'game_over'
  tick: 0,
  timeMs: 0,
  fixedTickMs: 10,
  seed: 1,
  rngState: 1,

  input: {
    moveX: 0,
    moveY: 0,
    sprintHeld: false,
    attackQueued: false,
    interactQueued: false,
    cycleSlotQueued: false,
    slotSelect: 0,
    craftSelect: 0,
    pauseQueued: false
  },

  player: {
    x: 235000,
    y: 155000,
    vx: 0,
    vy: 0,
    facing: 0,
    health: 1000000,
    healthCap: 1000000,
    oxygen: 1000000,
    stamina: 1000000,
    staminaCap: 1000000,
    selectedSlot: 1,
    attackCooldownMs: 0,
    attackDamage: 100000,
    lastDamageAtMs: 0,
    timeMs: 0,
    sprinting: false,
    interacting: false,
    interactionTimerMs: 0,
    interactionKind: 'none',
    interactionTargetId: 0,
    interactionItemId: '',
    interactionRecipeId: 0
  },

  inventory: [
    { slotIndex: 1, itemId: 'o2_cell', count: 1 },
    { slotIndex: 2, itemId: 'medkit', count: 1 },
    { slotIndex: 3, itemId: 'scrap', count: 2 },
    { slotIndex: 4, itemId: 'battery', count: 1 },
    { slotIndex: 5, itemId: 'filter', count: 1 },
    { slotIndex: 6, itemId: '', count: 0 },
    { slotIndex: 7, itemId: '', count: 0 },
    { slotIndex: 8, itemId: '', count: 0 },
    { slotIndex: 9, itemId: '', count: 0 },
    { slotIndex: 10, itemId: '', count: 0 }
  ],

  station: {
    day: 1,
    dayTimerMs: 0,
    threatLevel: 1,
    power: 500000,
    oxygen: 600000,
    hull: 700000,
    beacon: 0,
    score: 0,
    kills: 0,
    repairs: 0,
    beaconDay3: false,
    beaconWraith: false,
    beaconHazard: false,
    lastEvent1: 'none',
    lastEvent2: 'none',
    lastEvent3: 'none'
  },

  objects: [],
  enemies: [],
  hazards: [],
  loot: [],

  runRecord: {
    bestDay: 0,
    bestScore: 0
  },

  craft: {
    open: false,
    selected: 0,
    timerMs: 0
  },

  map: {
    widthTiles: 48,
    heightTiles: 30,
    floor: new Array(1440).fill(0),
    rooms: [],
    hubConsoleX: 245000,
    hubConsoleY: 155000,
    reachable: false,
    visualVerifier: false
  },

  ui: {
    bannerMs: 0,
    bannerText: '',
    toastMs: 0,
    toastText: '',
    damageFlashMs: 0,
    alarmActive: false
  },

  frame: {
    drawOps: 0,
    activeEntities: 0,
    audioEvents: 0
  },

  audio: {
    muted: false,
    lastEvent: '',
    queue: []
  },

  ids: {
    object: 1,
    enemy: 1,
    hazard: 1,
    loot: 1
  },

  systemOrder: [
    'input',
    'player',
    'interact',
    'enemies',
    'hazards',
    'lifeSupport',
    'power',
    'daily',
    'audio'
  ]
};
```

## 2.3 Module specifics

**Loop.**

- `Loop.install(canvas)`: installs the fixed-step requestAnimationFrame loop.
- `Loop.advance(dtMs, n)`: runs `n` ticks of `dtMs` milliseconds, then draws once.
- `Loop.tick()`: runs one 10 ms tick in system order.

**Input.**

- `Input.install()`: binds keyboard and touch listeners.
- `Input.update()`: normalizes persistent move input and consumes queued actions.
- `Input.debugMove(x, y)`: sets persistent move direction.
- `Input.debugSprint(b)`: sets sprint held.
- `Input.debugAttack()`: queues attack.
- `Input.debugInteract()`: queues interact.
- `Input.debugCycleSlot()`: queues slot cycle.
- `Input.debugSelectSlot(n)`: sets selected slot.
- `Input.debugCraftSelect(n)`: sets craft selection.
- `Input.debugPause()`: queues pause.

**Rng.**

- `Rng.reseed(n)`: reseeds the LCG.
- `Rng.setState(n)`: sets `rngState` directly.
- `Rng.next()`: returns next random value from 0 to 1 exclusive.
- `Rng.rangeInt(min, max)`: returns integer in inclusive range.
- `Rng.pick(arr)`: returns pseudo-random element.

**World.**

- `World.init(seed)`: clears and rebuilds generated world records.
- `World.clearDynamic()`: removes enemies, hazards, loot, and station objects.
- `World.isFloor(x, y)`: returns true if game-unit point is on floor.
- `World.setFloorTile(tx, ty)`: sets tile to floor.
- `World.setWallTile(tx, ty)`: sets tile to wall.
- `World.addStationObject(type, x, y)`: adds a station object if cap allows.
- `World.addLoot(itemId, count, x, y)`: adds loot if cap allows.
- `World.addHazard(type, x, y)`: adds hazard if cap allows.
- `World.addEnemy(type, x, y)`: adds enemy if cap allows.
- `World.nearestTarget(x, y, radius)`: returns nearest interact target within radius.
- `World.lineOfSight(x1, y1, x2, y2)`: returns true if straight segment is unblocked.
- `World.verifyMap()`: sets `map.reachable` and `map.visualVerifier`.

**Player.**

- `Player.update()`: moves player, updates facing, sprint, stamina, attack cooldown, collision.
- `Player.set(x, y)`: teleports player.
- `Player.setVelocity(vx, vy)`: sets player velocity.
- `Player.setHealth(v)`: sets player health.
- `Player.setHealthCap(v)`: sets player health cap.
- `Player.setOxygen(v)`: sets player oxygen.
- `Player.setStamina(v)`: sets player stamina.
- `Player.setStaminaCap(v)`: sets player stamina cap.
- `Player.setAttackDamage(v)`: sets player attack damage.
- `Player.setAttackCooldown(ms)`: sets player attack cooldown.
- `Player.damage(v)`: applies damage.
- `Player.heal(v)`: applies healing.

**Interact.**

- `Interact.update()`: consumes queued interact, runs interaction timer, completes effects.
- `Interact.start(kind, targetId, itemId, recipeId, ms)`: starts an interaction.
- `Interact.cancel()`: cancels active interaction.

**Enemies.**

- `Enemies.update()`: advances all enemy rules.
- `Enemies.spawn(type, x, y)`: creates scaled enemy at position.
- `Enemies.set(id, fields)`: updates enemy fields.
- `Enemies.damage(id, v)`: damages enemy and applies death rule.
- `Enemies.clear()`: removes all enemies.

**Hazards.**

- `Hazards.update()`: advances hazard rules.
- `Hazards.add(type, x, y)`: adds hazard.
- `Hazards.set(id, fields)`: updates hazard fields.
- `Hazards.disable(id)`: disables hazard for 120 seconds.
- `Hazards.clear()`: removes all hazards.

**LifeSupport.**

- `LifeSupport.update()`: updates player oxygen, station oxygen, health, recovery, game over.
- `LifeSupport.setStationOxygen(v)`: sets station oxygen.
- `LifeSupport.setPlayerOxygen(v)`: sets player oxygen.

**Power.**

- `Power.update()`: updates station power and station object loads.
- `Power.setStationPower(v)`: sets station power.
- `Power.setObject(id, fields)`: updates object integrity/load/active.

**Crafting.**

- `Crafting.update()`: updates craft menu and craft timer.
- `Crafting.open()`: opens craft menu if valid.
- `Crafting.close()`: closes craft menu.
- `Crafting.select(n)`: selects recipe.
- `Crafting.start(recipeId)`: starts craft interaction if valid.

**Daily.**

- `Daily.update()`: advances day timer and beacon milestones.
- `Daily.runDayCycle()`: applies the day-end rules once.
- `Daily.applyEvent(eventId)`: applies one threat event.
- `Daily.setLastEvents(e1, e2, e3)`: sets last event history.

**Audio.**

- `Audio.update()`: processes the audio queue.
- `Audio.queue(event)`: enqueues an audio event.
- `Audio.setMuted(b)`: sets muted flag.
- `Audio.clear()`: clears queue and resets event counter.

**Renderer.**

- `Renderer.init(canvas)`: initializes Canvas 2D context.
- `Renderer.draw()`: draws current state and returns draw-op count.

**Debug.**

- `Debug.install()`: installs `window.__game`.

# 3. VISUAL SPEC

Kestrel-9 is a low-poly, hard-edge derelict service station stranded in Earth orbit. T1 renders it as a 2D top-down Canvas 2D station cross-section using flat colours, emissive fixtures, procedural gradients, and the same cold palette as the source design: #020617 void, #0b1220 deep shadow, #7d8b99 brushed station metal, #8a93a3 panel faces, #46505f scuff, #2f3743 seams, safety amber #ffbf3f, emergency red #ff3b30, O2 cyan #38bdf8, hydro teal #2ee6a8, and reactor violet #b57cff. The mood is quiet, claustrophobic, and mechanically decaying. The one screenshot the T1 game should sell is a narrow top-down corridor: an amber safety strip runs along the floor, a red emergency light pulses on the left wall, a pale player flashlight cone cuts through dust, and a far viewport glows with a cold blue Earth disc. The first-person white suited forearm and wrench from the source are carried as T2.

**Lighting and atmosphere.** Ambient base is #263244 at intensity 0.35. Floor bounce is #0b1220 at intensity 0.10. Unlit corridor base visibility is 18.0 units before fog black. Fog colour is #0b1220. Fog density is 0.045. Fog far is 24.0 units. Beyond 24.0 units is #020617 void. Light radius falloff is 1.00 at centre and 0.00 at full radius. In unlit rooms, only emissive fixtures, viewports, pickups, and the player flashlight are readable. No external weather exists; the station is sealed. Orbital Earthlight slowly changes viewport tint from #93c5fd to #1e3a8a over 180 seconds. Dust motes drift through all lit spaces. Hull breaches and radiation hazards add rising blue bubbles and a slight cold-mist cylinder. Hydroponics adds faint mist near plant racks, opacity 0.12, 1.0 second pulse.

**Space.** The T1 station is one level, floor at y equals 0, with no vertical shafts or ladders. The generated layout is 48 by 30 tiles. The central hub is carved from x 20 to 27 and y 12 to 17. The hub console is at tile 24, 15. Eleven additional rooms are generated and connected by 1-tile-wide L-shaped corridors. Room decoration presets use the visual region language: Hub, Crew Quarters, Galley, Hydroponics, Medbay, Reactor, Escape Airlock, and neutral Storage/Utility rooms. The start room is decorated as Medbay. The Escape Airlock room is cosmetic in T1. Good generated stations have start and airlock at least two corridors apart, 3 to 5 visual landmarks per module, at least 2 light anchors per corridor, no chain of 3 unlit rooms, no dead-end corridor longer than 8.0 units, at least 3 viewports, hub console visible from at least 4 spokes, and a visible status light at every doorway. Bad generated stations avoid goal adjacent to start, 3 or more consecutive unlit modules, dead-end corridors longer than 12.0 units, two doors with identical colour and no status light, first 15.0 units with no viewport/console/landmark, hub floor colour too close to wall colour, and reactor or airlock entrance visually identical to a storage door.

**Recipe table.** Sizes are metres. Multiply by 10000 for game units. Height is used for T1 sprite sort and not for collision. Counts are full-station recipe counts; T1 culls to viewport and may pre-bake static room geometry while preserving colours, sizes, and motion.

| Thing (state) | Shape | Size | Colour | Count | Motion / effect |
| --- | --- | --- | --- | ---: | --- |
| Floor plate — clean | Flat slab with 0.02 bevel | 1.0 x 1.0 x 0.12 | #6b7686 top, #46505f edge, #364152 scuff | 142 | Static |
| Floor plate — wet | Flat slab with 0.02 bevel | 1.0 x 1.0 x 0.12 | #3f4a5a top, #8ecae6 sheen | 12 | Static, slight specular band |
| Floor plate — breach stain | Flat slab with cracks | 1.0 x 1.0 x 0.12 | #2b3a4a base, #90e0ff cracks | 4 | Static |
| Wall panel — intact | Box panel with seams | 1.0 x 3.2 x 0.15 | #8a93a3 face, #2f3743 seams, #556070 rivets | 168 | Static |
| Wall panel — dented | Box panel with dent normal | 1.0 x 3.2 x 0.15 | #75808f face, #3a414d dent | 22 | Static |
| Wall panel — breached | Box panel with hole | 1.0 x 3.2 x 0.15, hole 0.9 x 0.7 | #21252b rim, #b8c2cc shards, #dbeafe rim light | 3 | Emits blue light radius 4.0 |
| Ceiling panel | Flat slab with conduit line | 1.0 x 1.0 x 0.10 | #5b6473 face, #3b4352 conduit | 121 | Static |
| Hazard floor strip | Narrow raised line | 0.18 x 0.02 x 10.0 | #ffbf3f strip, #201a12 edge | 12 | Static |
| Viewport | Recessed frame and glass | 2.4 x 1.4 x 0.12, disc 0.36 diameter | #2a303c frame, #0a1122 glass, #f8fafc stars, #93c5fd Earth | 7 | 90 star dots twinkle over 1.8s; Earth disc drifts 0.02 units over 30s |
| Hub console | Box terminal with screen | 1.2 x 0.9 x 1.8 | #334155 body, #22d3ee screen, #ffbf3f buttons | 1 | Screen flicker: alpha 0.65 to 1.00 over 0.35s |
| Crew bunk | Rectangular bed frame | 1.9 x 0.85 x 0.55 | #d1d5db sheet, #64748b frame, #475569 blanket | 3 | Static |
| Galley table | Box table with top slab | 2.2 x 1.0 x 1.0 | #94a3b8 legs, #cbd5e1 top | 1 | Static |
| Vending console | Tall box with slot | 0.8 x 0.5 x 1.9 | #1f2937 body, #38bdf8 slot | 1 | Slot glow pulse: alpha 0.45 to 0.90 over 0.8s |
| Med bed | Rectangular bed with strap | 1.8 x 0.8 x 0.5 | #e5e7eb sheet, #4b5563 strap, #ef4444 cross | 3 | Static |
| Plant rack | Frame with leaf boxes | 1.6 x 0.6 x 1.8 | #243b36 frame, #2ee6a8 leaves, #16a34a dark leaves, #1f2937 soil | 4 | Leaf sway: 0.02 amplitude over 0.8s |
| Tool cart | Box cart with wheels | 1.1 x 0.6 x 1.2 | #b45309 body, #1f2937 wheels, #94a3b8 wrench | 4 | Static |
| Crate | Box crate with tape | 0.8 x 0.8 x 0.8 | #5b6b83 body, #ffbf3f tape | 10 | Static |
| Reactor core | Glass cylinder with inner emissive cylinder | 1.8 diameter, 1.8 high | #1e1b4b glass, #b57cff core, #4b5563 pipes | 1 | Core pulse: emissive 0.65 to 1.00 over 2.2s; slow rotation 0.05 rad over 2.0s |
| Airlock pod | Rounded capsule with hatch | 2.6 x 1.4 x 1.4 | #cbd5e1 body, #2a303c hatch, #ef4444 and #f8fafc stripes | 1 | Hatch status #22c55e steady |
| Door — closed | Slab with stripe and status | 2.2 x 2.6 x 0.20 | #4b5563 door, #ffbf3f stripe, #ff3b30 status | 7 | Status glow radius 0.8 |
| Door — open | Slab rotated 90 degrees | 2.2 x 2.6 x 0.20 | #4b5563 door, #22c55e stripe, #22c55e status | 0 to 4 | Opening motion: 90 degrees over 0.70s |
| Door — jammed | Slab with fault spark | 2.2 x 2.6 x 0.20 | #4b5563 door, #f59e0b status | 0 to 2 | Status flash: 1 Hz; 2 amber sparks every 1.0s |
| Emergency light — lit | Small wall fixture | 0.18 x 0.10 x 0.10 | #ff3b30 fixture, #ff3b30 light | 14 | Radius 5.5, cone 35 degrees, flicker alpha 0.80 to 1.00 every 1.2s |
| Emergency light — dark | Small wall fixture | 0.18 x 0.10 x 0.10 | #7f1d1d fixture | 5 | No emission |
| Work light — lit | Small ceiling fixture | 0.22 x 0.12 x 0.10 | #ffd166 fixture, #ffd166 light | 7 | Radius 6.0, cone 55 degrees, steady |
| Work light — broken | Small ceiling fixture with smoke | 0.22 x 0.12 x 0.10 | #a16207 fixture, #a8a29e smoke | 2 | Cone opacity 0.25, steady; smoke rises 0.4 units over 2.0s |
| Hydro light — lit | Long wall strip | 0.30 x 0.10 x 0.10 | #2ee6a8 light | 4 | Radius 4.0, cone 60 degrees, gentle pulse 0.8s |
| Reactor light — lit | Point light around core | 1.0 sphere radius | #b57cff light | 1 | Radius 8.0, pulse 2.2s |
| Oxygen cell — active | Cylinder with band | 0.28 diameter, 0.30 high | #38bdf8 body, #f8fafc band | 3 | Bob 0.06 amplitude over 1.5s; one full spin every 2.0s; glow radius 1.2 |
| Oxygen cell — collected | Cylinder scaling down | 0.28 diameter, 0.30 high | #38bdf8 body, #f8fafc band | 0 to 3 | Scale 1.00 to 0.00 over 0.25s; cyan flash |
| Med injector — active | Small vial | 0.08 diameter, 0.22 high | #f8fafc glass, #ef4444 cap | 2 | Bob 0.05 amplitude over 1.6s; red glow radius 1.0 |
| Med injector — collected | Vial scaling down | 0.08 diameter, 0.22 high | #f8fafc glass, #ef4444 cap | 0 to 2 | Scale 1.00 to 0.00 over 0.25s |
| Repair kit — active | Small box | 0.24 x 0.18 x 0.14 | #f59e0b body, #0f172a cross | 1 | Bob 0.05 amplitude over 1.7s; amber glow radius 1.0 |
| Repair kit — collected | Box scaling down | 0.24 x 0.18 x 0.14 | #f59e0b body, #0f172a cross | 0 to 1 | Scale 1.00 to 0.00 over 0.25s |
| Player first-person hand | Right arm, glove, wrist lamp | 0.18 x 0.22 x 0.55 | #e2e8f0 suit, #1f2937 glove, #ffd166 wrist lamp | 1 | Breathing sway 0.02 amplitude over 4.0s |
| Player wrench | Handle and head | 0.42 long, 0.04 thick | #64748b handle, #94a3b8 head | 1 | Held in hand; swing arc 120 degrees |
| Flashlight beam — on | Cone from player position | Starts 0.12 radius, ends 3.5 radius at 12.0 units | #fff7d6, opacity 0.12 | 1 | Flicker alpha 0.05 to 0.12 over 0.08s when damaged |
| Flashlight beam — off | No geometry | 0.0 | #000000 | 1 | No emission |
| Scrap — active | Small ingot cluster | 0.18 x 0.08 x 0.12 | #94a3b8 body, #46505f edges | 8 | Bob 0.04 amplitude over 1.8s |
| Battery — active | Small cylinder with cap | 0.12 diameter, 0.20 high | #fbbf24 body, #1f2937 cap | 4 | Bob 0.05 amplitude over 1.6s |
| Filter — active | Cone canister | 0.14 diameter, 0.18 high | #34d399 body, #0f172a band | 3 | Bob 0.05 amplitude over 1.7s |
| Fuse — active | Small rod with terminals | 0.06 x 0.06 x 0.16 | #fbbf24 rod, #94a3b8 terminals | 2 | Bob 0.04 amplitude over 1.9s |
| Coolant — active | Small jug with hose | 0.16 x 0.12 x 0.20 | #2ee6a8 jug, #1f2937 hose | 3 | Bob 0.05 amplitude over 1.5s |
| Hull patch — active | Square plate with bolts | 0.22 x 0.22 x 0.04 | #94a3b8 plate, #ffbf3f bolts | 1 | Bob 0.04 amplitude over 2.0s |
| Scrubber — idle | Square box with vents | 1.0 x 1.0 x 1.2 | #46505f body, #38bdf8 vents | 4 | Vent glow off |
| Scrubber — active | Square box with vents | 1.0 x 1.0 x 1.2 | #46505f body, #38bdf8 vents | 0 to 4 | Vent pulse 0.8s; cyan light radius 4.0 |
| Power bay — idle | Tall box with amber window | 1.2 x 1.0 x 1.4 | #2f3743 body, #ffbf3f window | 3 | Window dim |
| Power bay — active | Tall box with amber window | 1.2 x 1.0 x 1.4 | #2f3743 body, #ffbf3f window | 0 to 3 | Amber pulse 1.1s; light radius 5.0 |
| Hull seal — intact | Floor/wall plate with rivets | 1.0 x 1.0 x 0.10 | #8a93a3 plate, #2f3743 seams | 5 | Static |
| Hull seal — damaged | Floor/wall plate with cracks | 1.0 x 1.0 x 0.10 | #2b3a4a base, #90e0ff cracks | 0 to 5 | Crack glow pulse 1.4s |
| Vent hazard — active | Circular grate with mist | 1.2 diameter | #46505f rim, #38bdf8 inner, #dbeafe mist | 3 | Mist pulse 0.8s; cyan light radius 3.0 |
| Radiation hazard — active | Circular reactor stain | 1.2 diameter | #1e1b4b rim, #b57cff glow, #dbeafe bubbles | 3 | Violet pulse 1.2s; bubbles rise 1.0 unit over 1.5s |
| Scav bot / mite — body | Box body with tracks and panel | 0.6 x 0.5 x 0.8 | #b45309 body, #1f2937 tracks, #431407 panel | 2 to 16 | Idle bob 0.03 amplitude over 2.0s |
| Scav bot / mite — eye | Sphere | 0.09 diameter | #ff3b30 emissive | 2 to 16 | Blink: alpha 1.00 to 0.00 over 0.12s every 2.8s |
| Scav bot / mite — pincer | Two angled plates | 0.12 x 0.08 x 0.35 | #94a3b8 metal | 4 to 16 | Attack extend 0.25 over 0.15s |
| Wraith — body | Slender box with skids | 0.55 x 0.45 x 0.9 | #94a3b8 body, #1f2937 skids, #b57cff seam | 1 to 16 | Idle sway 0.04 amplitude over 1.4s |
| Wraith — eye | Vertical slit | 0.04 x 0.12 | #b57cff emissive | 1 to 16 | Pulse alpha 0.60 to 1.00 over 0.7s |
| Overseer — body | Heavy box with armor plates | 1.0 x 0.8 x 1.2 | #7f1d1d armor, #1f2937 core, #ffbf3f stripe | 1 to 16 | Idle heave 0.05 amplitude over 2.6s |
| Overseer — eye | Large orb | 0.14 diameter | #ff3b30 emissive | 1 to 16 | Flicker alpha 0.70 to 1.00 over 0.4s |
| Bot smoke — hurt | Soft sphere | 0.30 diameter | #a8a29e, opacity 0.35 | 1 per hit | Rises 0.8 units over 1.0s, fades out |
| Bot smoke — death | Soft spheres | 0.30 diameter | #a8a29e, opacity 0.35 | 3 per death | Rises 0.9 units over 1.2s, fades out |
| Spark — hit | Point particles | 0.03 size | #fbbf24 | 12 per hit | Life 0.40s; random upward bias |
| Spark — door jam | Point particles | 0.03 size | #f59e0b | 2 per flash | Life 0.30s |
| Hull breach mist | Soft cylinder and bubbles | 1.2 diameter, 1.2 high | #dbeafe, opacity 0.35 | 3 | Bubbles rise 1.0 unit over 1.5s; mist opacity pulse 0.8s |
| Dust mote — ambient | Point particle | 0.02 size | #cbd5e1, opacity 0.18 | 400 | Drifts 0.30 units over 6s; visible in beams |
| HUD O2 bar — normal | Rounded rectangle bar | 26 x 3.2 UI | #0f172a background, #334155 border, #38bdf8 fill | 1 | Fill follows O2 state; smooth 0.25s catch-up |
| HUD O2 bar — low | Rounded rectangle bar | 26 x 3.2 UI | #0f172a background, #7f1d1d border, #ef4444 fill, #f8fafc strobe | 1 | Strobe: 0.125s on, 0.125s off, continuous in low state |
| HUD suit bar — normal | Rounded rectangle bar | 26 x 2.2 UI | #0f172a background, #334155 border, #f87171 fill | 1 | Fill follows suit state; smooth 0.25s catch-up |
| HUD suit bar — low | Rounded rectangle bar | 26 x 2.2 UI | #0f172a background, #7f1d1d border, #ef4444 fill | 1 | Pulse: opacity 0.70 to 1.00 at 1 Hz |
| Objective toast | Text panel | 18 x 4.0 UI | #0f172a background, #e2e8f0 text, #ffbf3f label | 1 | Pop: scale 0.95 to 1.00 over 0.25s |
| Pickup toast | Text and icon panel | 18 x 5.0 UI, icon 4.8 UI | #0f172a background, #38bdf8 border, #e2e8f0 text | 1 | Slide in 0.25s, hold 0.70s, fade 0.35s |
| Alarm border — active | Full-screen border | 3.5 UI width | #ef4444, opacity 0.18 | 1 | Strobe: 0.80s cycle, continuous in alarm state |
| Vignette | Radial screen gradient | 100 x 100 UI | #020617 edges | 1 | Base opacity 0.25; plus 0.12 in unlit rooms; plus 0.18 in low suit state |
| Grain | Monochrome noise overlay | 120 px cells | #ffffff / #000000 | 1 | Opacity 0.07; plus 0.05 in low suit state; 8 fps refresh |
| Damage overlay | Radial red edge | 100 x 100 UI | #7f1d1d | 1 | Opacity 0.00 to 0.45 over 0.35s, then decay 0.25s |
| Title overlay — active | Full-screen panel | 100 x 100 UI | #020617 background, #e2e8f0 title, #ffbf3f prompt, #334155 station ring | 1 | Fade 0.50s; station ring rotation 0.20 rad over 4.0s |
| Death overlay — active | Full-screen panel | 100 x 100 UI | #020617 background, #ef4444 text, #ffbf3f prompt | 1 | Fade 1.20s |

# 4. GAMEPLAY SPEC

The player is alone on a damaged derelict space station, moving through a tile-based station cross-section from room to room to collect scrap, batteries, filters, coolant, emergency supplies, and fuses, while repairing power bays, oxygen scrubbers, and hull seals, and fighting awakened maintenance drones that hunt by sight and noise. Minute to minute, the player balances personal oxygen against station oxygen, keeps station power above 15 so scrubbers run, repairs the systems before they decay, uses coolant to shut down vents and radiation, and decides whether to sprint for speed and risk detection or move quietly and slowly. The game has no fixed scripted ending: a run ends only when player health reaches 0 or station hull reaches 0. What keeps it going is the day counter, rising threat level, random station events, beacon milestones that unlock small permanent upgrades, and the pursuit of a higher best day and best score.

## Records

**Player.** position x, position y, velocity x, velocity y, facing, health, health cap, oxygen, stamina, stamina cap, selected slot, attack cooldown, attack damage, last damage at, time, sprinting, interacting, interaction timer, interaction kind, interaction target id, interaction item id, interaction recipe id.

Starting values: position 23.5, 15.5 tiles; velocity 0; facing 0; health 100; health cap 100; oxygen 100; stamina 100; stamina cap 100; selected slot 1; attack cooldown 0; attack damage 10; last damage at 0; time 0; sprinting false; interacting false; interaction timer 0.

**Inventory Slot.** slot index, item id, count.

Starting inventory: slot 1 o2_cell 1, slot 2 medkit 1, slot 3 scrap 2, slot 4 battery 1, slot 5 filter 1, slots 6 to 10 empty.

**Item.** item id, stack, use type, effect.

| item_id | name | stack | use_type | effect |
| --- | --- | ---: | --- | --- |
| scrap | Scrap | 10 | material | crafting only |
| battery | Battery | 5 | insert/material | adds 5 load to a power_bay, or crafting material |
| coolant | Coolant | 5 | disable/material | disables an active hazard for 120 s, or crafting material |
| filter | Filter | 5 | insert/material | adds 5 load to a scrubber, or crafting material |
| fuse | Fuse | 5 | material | crafting only |
| o2_cell | O2 Cell | 3 | consumable | player.oxygen plus 35 |
| medkit | Medkit | 3 | consumable | player.health plus 30 |
| hull_patch | Hull Patch | 3 | consumable | at hub_console: station.hull plus 20; at hull_seal: object.integrity plus 30 and station.hull plus 5 |
| repair_kit | Repair Kit | 3 | repair | target Station Object integrity plus 30 |

**Station.** day, day timer, threat level, power, oxygen, hull, beacon, score, kills, repairs, beacon day 3, beacon wraith, beacon hazard, last event 1, last event 2, last event 3.

Starting values: day 1, day timer 0, threat level 1, power 50, oxygen 60, hull 70, beacon 0, score 0, kills 0, repairs 0, beacon day 3 false, beacon wraith false, beacon hazard false, last events none.

**Station Object.** object id, type, x, y, integrity, load, load max, active, reached 100.

| type | count | start integrity | start load | load max |
| --- | ---: | ---: | ---: | ---: |
| hub_console | 1 | 100 | 0 | 0 |
| scrubber | 4 | 70 | 4 | 10 |
| power_bay | 3 | 60 | 3 | 10 |
| hull_seal | 5 | 80 | 0 | 0 |

**Enemy.** enemy id, type, x, y, health, alert, state, speed, damage, attack cooldown max, attack cooldown, windup timer, last seen x, last seen y, search timer, target type, target id, no player seen timer.

| type | base health | base speed | base damage | attack_cd_max | detection radius | noise radius | first spawn day |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| mite | 20 | 2.2 | 5 | 1.2 | 6 | 4 | 1 |
| wraith | 50 | 1.8 | 12 | 1.5 | 7 | 5 | 3 |
| overseer | 120 | 1.6 | 20 | 2.0 | 8 | 6 | 7 |

**Hazard.** hazard id, type, x, y, radius, active, disable timer.

| type | radius | active effect |
| --- | ---: | --- |
| vent | 2 | while active: station.oxygen minus 0.5/s; if player within radius: player.oxygen minus 2/s |
| radiation | 1.5 | while active and player within radius: player.health minus 2/s |

**Loot Container.** loot id, x, y, opened, item id, count.

**Threat Event.** event id, weight, effect.

| event_id | weight | effect |
| --- | ---: | --- |
| power_surge | 3 | station.power plus 30; one random power_bay with integrity greater than 50 loses 40 integrity |
| hull_crack | 3 | one random hull_seal integrity becomes 20; station.hull minus 5 |
| supply_drop | 3 | place 4 loot containers in hub floor: scrap, battery, filter, o2_cell |
| vent_burst | 3 | add one active vent hazard on a floor tile not within 5 of player |
| radiation_leak | 2 | add one active radiation hazard on a floor tile not within 5 of player |
| drone_awakening | 2 | threat_level plus 1, capped 10; spawn 2 mites not within 10 of player |

**Run Record.** best day, best score. Starting values: best day 0, best score 0.

## Systems

### Player (T1)

- If W or ArrowUp is held, add minus 1 to input y. If S or ArrowDown is held, add plus 1 to input y. If A or ArrowLeft is held, add minus 1 to input x. If D or ArrowRight is held, add plus 1 to input x. If both input x and input y are nonzero, normalize the input vector to length 1.
- Target speed is 3 tile/s. If Shift is held and player.stamina is greater than 0 and player.interacting is false, set player.sprinting true and target speed 5 tile/s; otherwise set player.sprinting false and target speed 3 tile/s.
- If player.sprinting is true, player.stamina decreases by 20 times dt. If player.sprinting is false and at least 0.5 s has passed since sprinting ended, player.stamina increases by 15 times dt. Clamp player.stamina to 0 to stamina cap.
- player.velocity x changes by at most 12 tile/s squared toward input x times target speed. If input x is 0, player.velocity x decreases toward 0 at 20 tile/s squared. Apply the same rule to player.velocity y.
- player.position x increases by player.velocity x times dt. player.position y increases by player.velocity y times dt. Clamp position to the 48 by 30 tile world. If the next tile is wall, cancel that axis of movement and zero that axis velocity.
- If input vector length is greater than 0, player.facing equals atan2 input y, input x, stored as centiradians.
- player.attack_cooldown decreases by dt, never below 0.
- If Space or J is pressed and player.attack_cooldown is 0 or less, set player.attack_cooldown to 0.5. For each enemy where distance to player is 1.2 tile or less and angle difference from player.facing is 60 degrees or less, enemy.health decreases by player.attack_damage, enemy.alert becomes 100, enemy.state becomes chase, and knock the enemy 0.5 tile away from player. If enemy.health is 0 or less, remove enemy, station.kills increases by 1, station.score increases by 10, apply the enemy death rule, and if enemy.type is wraith apply the beacon_wraith rule.
- If Q or Tab is pressed, player.selected_slot becomes selected_slot minus 1 modulo 10 plus 1. If number key 1 to 10 is pressed while craft menu is closed, player.selected_slot becomes that number.
- If E is pressed and player.interacting is false:
  - If selected Inventory Slot item_id is o2_cell or medkit, start a 0.2 s interaction. On completion, o2_cell sets player.oxygen plus 35 and medkit sets player.health plus 30; consume 1 item.
  - Else if a Loot Container is the nearest interact target within 1.5 tile and it is not opened, start a 0.3 s interaction only if there is a valid Inventory Slot to receive the item. On completion, set Loot Container.opened true, add item_id and count to inventory, and consume the container.
  - Else if a Hazard is the nearest target within 1.5 tile and selected item is coolant and hazard.active is true, start a 0.5 s interaction. On completion, hazard.active becomes false, hazard.disable_timer becomes 120, consume 1 coolant, and apply the beacon_hazard rule.
  - Else if a Station Object is the nearest target within 1.5 tile:
    - If selected item is repair_kit and object.integrity is less than 100, start a 2 s interaction. On completion, object.integrity increases by 30 capped 100, consume 1 repair_kit, station.repairs increases by 1, station.score increases by 5, and apply the reached_100 rule.
    - Else if object.type is power_bay and selected item is battery and object.load is less than 10, start a 0.5 s interaction. On completion, object.load increases by 5 capped 10, consume 1 battery.
    - Else if object.type is scrubber and selected item is filter and object.load is less than 10, start a 0.5 s interaction. On completion, object.load increases by 5 capped 10, consume 1 filter.
    - Else if selected item is hull_patch and object.type is hub_console or hull_seal, start a 0.5 s interaction. On completion, consume 1 hull_patch. If object.type is hub_console, station.hull increases by 20 capped 100. If object.type is hull_seal, object.integrity increases by 30 capped 100 and station.hull increases by 5 capped 100.
    - Else if object.integrity is less than 100, start a 1 s bare repair interaction. On completion, object.integrity increases by 5 capped 100, station.repairs increases by 1, station.score increases by 5, and apply the reached_100 rule.
  - Else if the nearest target is hub_console and selected item is not hull_patch, open the craft menu.
- While player.interacting is true, player.interaction_timer decreases by dt. If input vector length is greater than 0, cancel interaction and set player.interacting false and player.interaction_timer to 0. If player.interaction_timer is 0 or less, complete the queued effect and set player.interacting false.
- Touch: a left virtual joystick sets the same movement input as WASD/arrows. Right-side buttons Action, Attack, Sprint, and Item trigger the same rules as E, Space, Shift hold, and Q respectively.

### Life Support (T1)

- Each second, for each scrubber where integrity is 25 or more and station.power is 15 or more and load is greater than 0, set active true, station.oxygen increases by 0.35 times dt, and load decreases by 0.05 times dt. Otherwise set active false.
- station.oxygen decreases by 0.5 times dt.
- For each hull_seal where integrity is less than 50, station.oxygen decreases by 0.5 times dt.
- For each active vent hazard, station.oxygen decreases by 0.5 times dt.
- If station.hull is less than 20, station.oxygen decreases by 2 times dt.
- Clamp station.oxygen to 0 to 100.
- player.oxygen decreases by 0.4 times dt.
- If station.oxygen is less than 25, player.oxygen decreases by 0.6 times dt.
- If station.oxygen is 75 or more and player.oxygen is less than 100, player.oxygen increases by 1.5 times dt.
- For each active vent hazard, if player is within hazard.radius, player.oxygen decreases by 2 times dt.
- Clamp player.oxygen to 0 to 100.
- If player.oxygen is 0 or less, player.health decreases by 4 times dt.
- If player.time minus player.last_damage_at is 10 or more and station.oxygen is 75 or more and player.health is less than 60, player.health increases by 0.5 times dt.
- Clamp player.health to 0 to player.health_cap.
- If player.health is 0 or less or station.hull is 0 or less, go to game_over screen and update Run Record: best_day becomes max best_day, station.day, and best_score becomes max best_score, station.score.

### Station Power (T1)

- station.power decreases by 3 times dt.
- For each active scrubber, station.power decreases by 2 times dt.
- For each power_bay where integrity is 25 or more and load is greater than 0, set active true, station.power increases by 5 times dt, and load decreases by 0.05 times dt. Otherwise set active false.
- Clamp station.power to 0 to 100.

### Crafting (T1)

- The craft menu is open only while the player is standing within 1.5 tile of hub_console and not using a personal consumable.
- Recipes are visible only if unlocked by station.day:
  1. O2 Cell: unlocked day 1, cost 1 filter plus 1 battery, craft time 2 s, result 1 o2_cell.
  2. Medkit: unlocked day 2, cost 1 filter plus 1 coolant, craft time 2 s, result 1 medkit.
  3. Hull Patch: unlocked day 2, cost 2 scrap plus 1 fuse, craft time 2 s, result 1 hull_patch.
  4. Repair Kit: unlocked day 4, cost 1 scrap plus 1 fuse plus 1 coolant, craft time 3 s, result 1 repair_kit.
- If a craft recipe is selected while station.power is 10 or more and all required items are present, start a craft interaction for the recipe time. Moving cancels it without consuming items.
- On craft completion, consume required items, add the result item to inventory, station.score increases by 5, and close the craft menu if inventory is full or the result has no valid slot.
- If the result item has no valid Inventory Slot, the craft fails and no items are consumed.

### Enemies (T1)

- Enemy spawn values are scaled by station.threat_level:
  - health equals base health plus station.threat_level minus 1 times 5.
  - damage equals base damage plus station.threat_level minus 1 times 2.
  - speed equals base speed plus min 0.5, station.threat_level minus 1 times 0.05.
- Perception:
  - If line of sight to player exists and distance is 6 tile or less for mite, 7 tile or less for wraith, or 8 tile or less for overseer, set enemy.last_seen_x to player.position_x, enemy.last_seen_y to player.position_y, enemy.alert to 100, enemy.state to chase, enemy.target_type to player, and enemy.no_player_seen_timer to 0.
  - If line of sight does not exist and player is moving within the enemy noise radius, set enemy.last_seen_x to player.position_x, enemy.last_seen_y to player.position_y, and enemy.alert increases by 30 times dt. Player noise radius is 5 while sprinting, 2 while walking, and 0 while stationary.
- Behavior:
  - patrol: move at speed times 0.5 toward a waypoint chosen every 4 s from floor tiles within 3 tile. If player is detected, switch to chase.
  - search: move at speed toward last_seen_x, last_seen_y. If enemy reaches last_seen and player is not seen for 5 s, enemy.search_timer increases by dt. When enemy.search_timer is 5 or more, enemy.alert decreases by 20 times dt. If enemy.alert is 0 or less, set state to patrol.
  - chase: move at speed toward player. If distance is 0.8 or less and enemy.attack_cooldown is 0 or less, set state to windup, enemy.windup_timer becomes 0.4. If line of sight is lost and distance is greater than detection radius times 1.5, set state to search.
  - windup: after enemy.windup_timer reaches 0, player.health decreases by enemy.damage, player.last_damage_at becomes player.time, knock player 0.3 tile away from enemy, enemy.attack_cooldown becomes enemy.attack_cd_max, and set state to chase.
  - If enemy.no_player_seen_timer is 10 or more, choose the nearest Station Object with integrity less than 100 within 4 tile. If one exists, set enemy.target_type to object and enemy.target_id to object.object_id. If none exists, set enemy.target_type to none.
  - If enemy.target_type is object and distance to target object is 0.8 or less and enemy.attack_cooldown is 0 or less, target object.integrity decreases by enemy.damage, enemy.attack_cooldown becomes enemy.attack_cd_max, and station.score changes by 0.
- Enemy movement is blocked by wall tiles. If the direct path is blocked, slide perpendicular to the target direction.
- enemy.attack_cooldown decreases by dt, never below 0.
- If enemy.health is 0 or less, remove enemy, station.kills increases by 1, station.score increases by 10, if enemy.type is wraith and station.beacon_wraith is false set station.beacon_wraith true and station.beacon increases by 5 capped 100, and add a Loot Container with item_id coolant, count 1, at the enemy position if the loot cap allows.

### Hazards (T1)

- For each inactive hazard, hazard.disable_timer decreases by dt. If hazard.disable_timer is 0 or less, set hazard.active true.
- For each active hazard, if player.position is within hazard.radius, apply the active effect from the Hazard roster.
- If a hazard changes from active true to active false and station.beacon_hazard is false, set station.beacon_hazard true and station.beacon increases by 5 capped 100.

### Daily Cycle (T1)

- station.day_timer increases by dt.
- If station.day_timer is 240 or more:
  - station.day increases by 1.
  - station.day_timer becomes 0.
  - station.score increases by 100.
  - station.threat_level becomes min 10, station.threat_level plus 1.
  - If station.day is 4 or more, station.hull decreases by 1.
  - One random Station Object that is not hub_console and has integrity greater than 10 loses 10 integrity.
  - Spawn drones using the Daily SEEDED GENERATOR below.
  - If station.day is 2 or more, choose and apply one Threat Event using the Daily SEEDED GENERATOR below.
  - Update last events: last_event_3 becomes last_event_2, last_event_2 becomes last_event_1, last_event_1 becomes chosen event_id.
- If station.day is 3 or more and station.beaconDay3 is false, set station.beaconDay3 true and station.beacon increases by 5 capped 100.
- If station.beacon crosses 25 from below, player.stamina_cap increases by 10.
- If station.beacon crosses 50 from below, player.attack_damage increases by 2.
- If station.beacon crosses 75 from below, all existing and future Enemy.attack_cd_max increase by 0.2.
- If station.beacon crosses 100 from below, player.health_cap increases by 20, station.power increases by 20 capped 100, and station.score increases by 500.

**Daily SEEDED GENERATOR.**

- seed_day equals initial map seed plus station.day times 7919.
- Use `Rng` reseeded with seed_day to choose spawn tiles and event details.
- Drone count equals min 8, 2 plus floor station.day divided by 2.
- Drone types:
  - If station.day is less than 3: all mites.
  - If station.day is 3 to 6: first min count, 1 wraith, remaining mites.
  - If station.day is 7 or more: first min count, 1 overseer, next min count, 1 wraith, remaining mites.
- For each spawned drone, choose a floor tile that is not within 8 tile of player, not within 2 tile of another newly spawned drone, and not on a Station Object or Hazard. If 20 attempts fail for one drone, skip that drone.
- Event choice: choose by weight among Threat Events not equal to last_event_1, last_event_2, or last_event_3. For vent_burst or radiation_leak, choose a floor tile not within 5 tile of player and not occupied by a Station Object, Loot Container, or existing Hazard. If placement fails, choose another eligible event. If no eligible event can be applied, apply no event.
- VERIFIER for the daily generator:
  - At least one drone spawn tile is found unless drone count is 0.
  - No drone spawn tile is within 8 tile of player.
  - No two drone spawn tiles are on the same tile.
  - If an event is applied, all event effects are valid: placement hazards are not within 5 tile of player, power_surge target exists, hull_crack target exists, supply_drop placement fits in hub, and threat_level remains 1 to 10.
- Re-roll with the next seed_day if any check fails.

### Map Generator (T1)

**Initial SEEDED GENERATOR.**

- Input: a 32-bit seed. If no seed is provided by UI, seed equals current time in milliseconds modulo 4294967296, chosen once outside tick logic. Use `Rng` reseeded with that seed.
- World size: 48 by 30 tile grid. All tiles start as wall.
- Carve hub: carve floor rectangle from x 20 to 27 and y 12 to 17.
- Place hub_console at tile 24, 15, stored at game-unit center 245000, 155000.
- Set player start position to 23.5, 15.5 tiles, stored at 235000, 155000.
- Create 11 additional rooms. For each room, make up to 50 attempts:
  - Choose width 4 to 8 and height 4 to 6.
  - Choose top-left x from 2 to 41 and y from 2 to 23.
  - Discard if the room plus a 2-tile margin overlaps any existing carved floor rectangle.
  - Otherwise carve the room.
  - Connect the new room center to the nearest existing floor center with a 1-tile-wide L-shaped corridor, carving wall tiles as needed.
- Assign room decoration presets in this fixed order: Medbay, Crew Quarters, Galley, Hydroponics, Reactor, Escape Airlock, Storage, Utility, Storage, Utility, Storage. The start room is forced to Medbay.
- Place 4 scrubbers:
  - Choose 4 distinct floor tiles in rooms with width times height 24 or more, or any floor if not enough.
  - No two scrubbers may be closer than 4 tile.
  - Do not place on hub_console, power_bay, hull_seal, Loot Container, or Hazard.
- Place 3 power_bays:
  - Choose 3 distinct floor tiles not closer than 4 tile to another Station Object.
  - Do not place on an occupied tile.
- Place 5 hull_seals:
  - Choose 5 floor tiles adjacent to at least one wall tile.
  - No hull_seal may be within 2 tile of another Station Object.
- Place 24 Loot Containers in this fixed content order:
  1. scrap
  2. scrap
  3. scrap
  4. scrap
  5. scrap
  6. scrap
  7. scrap
  8. scrap
  9. battery
  10. battery
  11. battery
  12. battery
  13. filter
  14. filter
  15. filter
  16. fuse
  17. fuse
  18. o2_cell
  19. o2_cell
  20. o2_cell
  21. medkit
  22. medkit
  23. repair_kit
  24. hull_patch
- Add 3 coolant Loot Containers in the Medbay start room as emergency supplies. Each is placed on a floor tile not occupied by another Loot Container, Station Object, or Hazard, and not within 2 tile of player start.
- Each Loot Container is placed on a floor tile not occupied by another Loot Container, Station Object, or Hazard, and not within 2 tile of player start.
- Place 3 vent hazards and 3 radiation hazards on floor tiles not occupied by Station Objects or Loot Containers and not within 4 tile of player start.
- Spawn 2 mite enemies on floor tiles at least 12 tile from player start, not within 2 tile of another enemy, and not on a Station Object or Hazard.
- VERIFIER for the initial map:
  - All floor tiles are reachable from player start through floor tiles.
  - All 4 scrubbers, 3 power_bays, and 5 hull_seals are reachable from player start.
  - At least 24 fixed Loot Containers exist.
  - At least 3 coolant Loot Containers exist.
  - At least 3 o2_cell, 2 medkit, 1 repair_kit, and 1 hull_patch exist.
  - No Hazard or initial enemy is within 3 tile of player start.
  - No tile contains two Station Objects, Loot Containers, or Hazards.
  - hub_console exists at tile 24, 15.
  - Start and airlock room are at least two corridors apart.
  - Every room contains 3 to 5 visual landmarks.
  - Every corridor has at least 2 light anchors.
  - No chain of 3 unlit rooms.
  - No dead-end corridor is longer than 8.0 tile.
  - At least 3 rooms have a viewport.
  - Hub console is visible from at least 4 spokes.
  - Every doorway has a visible status light.
- Re-roll with the next seed if any check fails.

## Progression and difficulty

Early game is easy because station starts with power 50, oxygen 60, hull 70, scrubbers at integrity 70 with load 4, power bays at integrity 60 with load 3, only 2 mites are active, no Threat Event occurs on day 1, and the player starts with 1 o2_cell, 1 medkit, 2 scrap, 1 battery, and 1 filter.

Unlock order:

- Day 1: O2 Cell recipe, bare repair, O2 cells and basic resources from loot.
- Day 2: Medkit and Hull Patch recipes, first Threat Event, threat level 2, drone count 3.
- Day 3: wraith first appears, beacon day 3 milestone, drone count 3.
- Day 4: Repair Kit recipe, station.hull begins decaying 1 per day, drone count 4.
- Day 7: overseer first appears, threat level 7, drone count 5.
- Day 10: threat level reaches 10, drone count 7.
- Day 12 and later: drone count reaches the 8 cap.

Difficulty increases because threat level raises enemy health, damage, and speed; daily drone count rises; station hull decays after day 3; random events damage seals, power bays, and oxygen; and active hazards drain station oxygen and player oxygen or health.

The player is expected to fail by:

- letting station power fall below 15, which stops scrubbers and drops station oxygen;
- sprinting too often near drones, triggering noise detection;
- ignoring damaged hull_seals, which drain station oxygen;
- running out of o2_cell and medkit when personal oxygen or health is low;
- being overwhelmed after day 7 when overseer and wraith spawn together.

Recovery in a run comes from O2 cells, medkits, bare repair, Repair Kits, hull patches, coolant disabling hazards, crafting, beacon milestones, and coolant drops from defeated drones. If the player dies or station hull reaches 0, the run ends and the player recovers by retrying a new run with a new seed and updated best_day and best_score.

## Feel

- Walk speed is 3 tile/s, sprint speed is 5 tile/s, acceleration is 12 tile/s squared, deceleration is 20 tile/s squared. This makes walking feel deliberate and sprinting feel like a dangerous burst rather than free movement.
- Player attack cooldown is 0.5 s, range is 1.2 tile, arc is 120 degrees, and enemy knockback is 0.5 tile. This lets the player punish one enemy at a time without becoming a damage sponge.
- Enemy windup is 0.4 s, player knockback is 0.3 tile, and noise radii are 5 tile for sprinting and 2 tile for walking. This makes movement noise a real decision: sprinting escapes hazards but attracts drones.
- Personal oxygen drain is 0.4/s, low station oxygen adds 0.6/s, and station oxygen at 75 or more regenerates personal oxygen at 1.5/s. An O2 cell adds 35 oxygen, which is enough for a short recovery but not enough to ignore scrubbers.
- Station oxygen base decay is 0.5/s, and each active scrubber adds 0.35/s. With four scrubbers active, station oxygen slowly rises; with three, it rises slowly; with two or fewer, the station begins losing air unless leaks are repaired.
- Power base drain is 3/s, each scrubber costs 2/s, and each power_bay adds 5/s. Three working bays keep a four-scrubber station powered, but one failed bay or low battery load forces the player to repair before crafting and oxygen both stall.
- Stamina drain is 20/s and regen is 15/s after a 0.5 s delay. Sprinting is useful for 5 seconds before stamina begins to pressure the player.
- Loot open is 0.3 s, item insertion is 0.5 s, bare repair is 1 s, Repair Kit repair is 2 s, and crafting takes 2 s or 3 s. These times make the station feel like a place where the player can be interrupted, not a menu-only survival game.
- Day length is 240 s. Hazard disable duration is 120 s. Enemy search decay begins after 5 s without player contact. Enemy object sabotage begins after 10 s without player contact. These timers create repeated loops: clean the station, hunt the next threat, then reinforce before the next day.

# 5. CHARACTERS

**Player T1 top-down silhouette.** A white suited maintenance figure from above: white suit, dark glove, gray wrench, amber wrist lamp. Read at a glance: human, maintenance-grade, fragile against the rusted station.

- **Idle**: breathing vertical sway 0.02 units over 4.0 s; hand micro-drift 0.01 units over 1.7 s; wrist lamp steady.
- **Walk**: head-bob 0.08 units at 1.8 Hz while moving; arm pivot 6 degrees; wrench lags 0.05 seconds behind hand.
- **Sprint**: lean forward 0.06 units; arm pivot 10 degrees; wrist lamp brighter.
- **Attack**: wrench swing over 0.45 s: windup 0.10 s, strike 0.12 s, recover 0.23 s; swing arc 120 degrees; white slash flash 0.10 s on strike.
- **Interact**: wrench lowered 0.04 units; wrist lamp pulses at 1 Hz.
- **Hurt**: red damage overlay 0.35 s; hand recoil 0.05 units over 0.10 s; camera dip 0.08 units over 0.08 s.
- **Death**: desaturation to #475569 over 1.20 s; camera tilt 8 degrees; camera drop 0.50 units over 0.80 s; fade to #020617 over 0.80 s.

Player facings: yaw 360 degrees, no body roll in T1. T2 first-person facings: yaw 360 degrees, pitch minus 35 degrees to plus 28 degrees, no character roll except death tilt.

**Mite / Scav Bot silhouette.** A rust-orange box body, black caterpillar tracks, one large red eye, and a single pincer arm. Read at a glance: mechanical scavenger, damaged, slow, and dangerous when close.

- **Patrol / Idle**: body bob 0.03 units over 2.0 s; cable sway 0.04 units over 0.5 s; eye blink every 2.8 s, 0.12 s off.
- **Search / Walk**: trudge step 0.70 s per step; body pitch 2 degrees; tracks rotate; arm sway 4 degrees.
- **Chase / Walk**: trudge step 0.55 s per step; body pitch 3 degrees; eye alpha 1.00.
- **Windup / Attack**: pincer extend over 0.45 s: windup 0.15 s, strike 0.15 s, recover 0.15 s; eye white #f8fafc for 0.10 s on strike.
- **Hurt**: smoke puff 0.30 s; eye flicker alpha 0.00 to 1.00 over 0.40 s; body shake amplitude 0.05 units over 0.30 s.
- **Death**: collapse over 0.80 s: tilt 15 degrees, drop 0.25 units; 12 sparks for 0.40 s; 3 smoke puffs; eye becomes #450a0a.

Mite facings: yaw only, faces target, no roll; pitch changes only 5 degrees when hurt or dying in T2.

**Wraith silhouette.** A slender pale metal scout with skids, a vertical violet eye, and teal coolant vents. Read at a glance: faster, quieter, hostile.

- **Patrol / Idle**: body sway 0.04 units over 1.4 s; vent glow pulse 0.7 s.
- **Search / Walk**: glide step 0.50 s per step; body pitch 1 degree; eye pulse 0.7 s.
- **Chase / Walk**: glide step 0.40 s per step; eye white #f8fafc for 0.08 s on detection.
- **Windup / Attack**: arm snap over 0.45 s: windup 0.15 s, strike 0.15 s, recover 0.15 s.
- **Hurt**: violet smoke puff 0.30 s; eye flicker 0.40 s; body shake 0.04 units.
- **Death**: collapse over 0.80 s; violet sparks; 3 smoke puffs; eye becomes #4c1d95.

**Overseer silhouette.** A heavy rust-red armored drone with a large red eye and thick pincer arms. Read at a glance: slow, durable, dangerous.

- **Patrol / Idle**: heave 0.05 units over 2.6 s; armor plates shift 0.02 units.
- **Search / Walk**: heavy step 0.90 s per step; body pitch 2 degrees.
- **Chase / Walk**: heavy step 0.75 s per step; eye flicker 0.4 s.
- **Windup / Attack**: pincer crush over 0.60 s: windup 0.20 s, strike 0.15 s, recover 0.25 s.
- **Hurt**: smoke puff 0.35 s; eye flicker 0.40 s; body shake 0.06 units.
- **Death**: collapse over 1.00 s; tilt 12 degrees; drop 0.30 units; 16 sparks; 4 smoke puffs.

# 6. AUDIO

All sound is generated with the Web Audio API. No external audio files. One AudioContext is created on first user input. Master gain is 0.8. If muted, no audio events play. If active source count reaches 4, the newest event is dropped.

| Sound | Recipe | Rule that plays it |
| --- | --- | --- |
| ui_click | square, 880 Hz, 0.05 s, attack 0.01 s, decay 0.04 s | Any title, pause, or game-over button press |
| run_start | sawtooth, 220 Hz to 440 Hz over 0.40 s, 0.40 s, attack 0.02 s, decay 0.38 s | New run starts |
| footstep_walk | triangle, 120 Hz, 0.05 s, attack 0.005 s, decay 0.045 s | Every 0.45 s while player is moving and not sprinting |
| footstep_sprint | triangle, 160 Hz, 0.05 s, attack 0.005 s, decay 0.045 s | Every 0.28 s while player is sprinting |
| attack_swing | square, 300 Hz, 0.08 s, attack 0.01 s, decay 0.07 s | Player attack starts |
| attack_hit | square, 520 Hz, 0.06 s, attack 0.005 s, decay 0.055 s | Player attack damages an enemy |
| attack_miss | square, 240 Hz, 0.05 s, attack 0.005 s, decay 0.045 s | Player attack hits no enemy |
| player_hurt | sawtooth, 160 Hz, 0.25 s, attack 0.01 s, decay 0.24 s | Player takes damage |
| player_death | sawtooth, 80 Hz, 0.80 s, attack 0.02 s, decay 0.78 s | Player health reaches 0 |
| loot_open | triangle, 660 Hz, 0.08 s, attack 0.01 s, decay 0.07 s | Loot container interaction completes |
| use_o2 | sine, 520 Hz, 0.15 s, attack 0.02 s, decay 0.13 s | O2 cell use completes |
| use_medkit | sine, 780 Hz, 0.15 s, attack 0.02 s, decay 0.13 s | Medkit use completes |
| insert_load | square, 440 Hz, 0.10 s, attack 0.01 s, decay 0.09 s | Battery or filter insertion completes |
| repair_complete | triangle, 700 Hz, 0.12 s, attack 0.01 s, decay 0.11 s | Bare repair or Repair Kit repair completes |
| hull_patch | square, 500 Hz, 0.15 s, attack 0.01 s, decay 0.14 s | Hull patch interaction completes |
| craft_start | sine, 440 Hz, 0.10 s, attack 0.01 s, decay 0.09 s | Craft interaction starts |
| craft_complete | sine, 660 Hz, 0.15 s, attack 0.01 s, decay 0.14 s | Craft completes |
| craft_fail | sawtooth, 180 Hz, 0.20 s, attack 0.01 s, decay 0.19 s | Craft fails because inventory is full |
| hazard_alert | sawtooth, 200 Hz, 0.20 s, attack 0.01 s, decay 0.19 s | Every 1.0 s while an active hazard is within 3.0 tile of player |
| hazard_disabled | sine, 700 Hz, 0.15 s, attack 0.01 s, decay 0.14 s | Coolant disable completes |
| power_low_alarm | square, 440 Hz, 0.10 s, attack 0.01 s, decay 0.09 s | Every 1.0 s while station.power is less than 15 |
| station_oxygen_low_alarm | square, 330 Hz, 0.10 s, attack 0.01 s, decay 0.09 s | Every 1.0 s while station.oxygen is less than 25 |
| hull_low_alarm | square, 260 Hz, 0.12 s, attack 0.01 s, decay 0.11 s | Every 1.0 s while station.hull is less than 20 |
| low_o2_strobe | square, 990 Hz, 0.05 s, attack 0.005 s, decay 0.045 s | Every 0.25 s while player.oxygen is less than 25 |
| power_surge | sawtooth, 90 Hz to 180 Hz over 0.30 s, 0.30 s, attack 0.02 s, decay 0.28 s | power_surge event applies |
| hull_crack | sawtooth, 110 Hz, 0.30 s, attack 0.02 s, decay 0.28 s | hull_crack event applies |
| supply_drop | triangle, 520 Hz, 0.20 s, attack 0.02 s, decay 0.18 s | supply_drop event applies |
| vent_burst | sawtooth, 250 Hz, 0.25 s, attack 0.02 s, decay 0.23 s | vent_burst event applies |
| radiation_leak | sine, 350 Hz, 0.25 s, attack 0.02 s, decay 0.23 s | radiation_leak event applies |
| drone_awakening | square, 70 Hz, 0.40 s, attack 0.02 s, decay 0.38 s | drone_awakening event applies |
| drone_alert | square, 880 Hz, 0.08 s, attack 0.005 s, decay 0.075 s | Enemy state changes to chase |
| drone_windup | sawtooth, 180 Hz, 0.35 s, attack 0.02 s, decay 0.33 s | Enemy state changes to windup |
| drone_hit | square, 300 Hz, 0.05 s, attack 0.005 s, decay 0.045 s | Enemy takes damage |
| drone_death | sawtooth, 120 Hz, 0.40 s, attack 0.02 s, decay 0.38 s | Enemy health reaches 0 |
| beacon_milestone | sine, 660 Hz and 1320 Hz together, 0.30 s, attack 0.02 s, decay 0.28 s | Beacon crosses 25, 50, 75, or 100 |
| day_tick | triangle, 330 Hz, 0.20 s, attack 0.02 s, decay 0.18 s | New day begins |
| event_banner | triangle, 550 Hz, 0.12 s, attack 0.01 s, decay 0.11 s | Threat Event banner appears |
| pause_open | sine, 440 Hz, 0.06 s, attack 0.01 s, decay 0.05 s | Pause opens |
| pause_close | sine, 660 Hz, 0.06 s, attack 0.01 s, decay 0.05 s | Pause closes |
| game_over | sawtooth, 100 Hz, 1.00 s, attack 0.02 s, decay 0.98 s | Game over screen shows |
| alarm_state | square, 660 Hz, 0.15 s, attack 0.01 s, decay 0.14 s | Every 0.80 s while any enemy is chasing or station.oxygen is less than 15 |
| door_open | sine, 520 Hz, 0.20 s, attack 0.02 s, decay 0.18 s | T2 door opens |
| door_jam | square, 220 Hz, 0.10 s, attack 0.01 s, decay 0.09 s | T2 jammed door flashes |

# 7. UX

HTML and CSS only for UI. Canvas 2D renders the game world. UI units are screen fractions: 1 UI unit equals 1 percent of the short screen edge.

**State machine.**

| Current state | Allowed transitions |
| --- | --- |
| title | run on Enter, Space, or New Run button |
| run | pause on P or Escape; game_over on player health 0 or station hull 0; craft overlay may be open during run |
| pause | run on P, Escape, Resume, or R restart; title on T or Title |
| game_over | run on Enter or Retry; title on T or Title |

**HUD table.**

| HUD element | Record field shown | Visible when |
| --- | --- | --- |
| Title panel | runRecord.bestDay, runRecord.bestScore | state title |
| Player health bar | player.health divided by player.healthCap | state run |
| Player oxygen bar | player.oxygen | state run |
| Player stamina bar | player.stamina divided by player.staminaCap | state run |
| Day and time | station.day, station.dayTimerMs | state run |
| Station power bar | station.power | state run |
| Station oxygen bar | station.oxygen | state run |
| Station hull bar | station.hull | state run |
| Beacon meter | station.beacon | state run |
| Score | station.score | state run |
| Inventory slots | inventory slot item_id, inventory slot count, player.selectedSlot | state run |
| Interaction prompt | contextual nearest target action | state run and valid target within 1.5 tile |
| Craft menu | unlocked recipes, required Item counts, station.power | state run and craft.open true |
| Event banner | station.lastEvent1, ui.bannerText, ui.bannerMs | state run and ui.bannerMs greater than 0 |
| Pickup toast | ui.toastText, ui.toastMs | state run and ui.toastMs greater than 0 |
| Damage overlay | ui.damageFlashMs | state run and ui.damageFlashMs greater than 0 |
| Low O2 strobe | player.oxygen | state run and player.oxygen less than 25 |
| Alarm border | ui.alarmActive | state run and ui.alarmActive true |
| Vignette | ui.alarmActive, player.oxygen, player.health | state run |
| Grain | player.health, ui.alarmActive | state run |
| Pause panel | state pause | state pause |
| Game over panel | station.day, station.score, runRecord.bestDay, runRecord.bestScore | state game_over |

# 8. DEBUG API

`window.__game` exposes only synchronous functions returning plain data.

| Call | What it does | Returns |
| --- | --- | --- |
| `start(seed?)` | Starts a new run; if seed is given, reseeds and builds map; otherwise uses current seed | `{state, tick, timeMs, seed}` |
| `step(dt, n)` | Advances n ticks of dt seconds, then draws once | `{tick, timeMs, drawOps, activeEntities}` |
| `setTime(t)` | Advances to the largest 10 ms multiple less than or equal to t seconds, no draw | `{tick, timeMs}` |
| `getState()` | Returns all record fields as plain data | state object |
| `seed(n)` | Sets seed and reseeds Rng | `{seed, rngState}` |
| `setRngState(n)` | Sets rngState directly | `{rngState}` |
| `roll()` | Returns next Rng value | number |
| `move(x, y)` | Sets persistent player move direction | `{moveX, moveY}` |
| `setSprint(b)` | Sets sprint held | `{sprintHeld}` |
| `attack()` | Queues one attack action | `{attackQueued: true}` |
| `interact()` | Queues one interact action | `{interactQueued: true}` |
| `selectSlot(n)` | Sets selected inventory slot | `{selectedSlot}` |
| `cycleSlot()` | Queues slot cycle | `{cycleSlotQueued: true}` |
| `craftSelect(n)` | Sets craft selection | `{selected}` |
| `pauseToggle()` | Queues pause toggle | `{pauseQueued: true}` |
| `setPlayer(x, y)` | Teleports player | `{x, y}` |
| `setPlayerVelocity(vx, vy)` | Sets player velocity | `{vx, vy}` |
| `setHealth(v)` | Sets player health | `{health}` |
| `setHealthCap(v)` | Sets player health cap | `{healthCap}` |
| `setPlayerOxygen(v)` | Sets player oxygen | `{oxygen}` |
| `setStamina(v)` | Sets player stamina | `{stamina}` |
| `setStaminaCap(v)` | Sets player stamina cap | `{staminaCap}` |
| `setAttackDamage(v)` | Sets player attack damage | `{attackDamage}` |
| `setAttackCooldown(ms)` | Sets player attack cooldown | `{attackCooldownMs}` |
| `setStationPower(v)` | Sets station power | `{power}` |
| `setStationOxygen(v)` | Sets station oxygen | `{oxygen}` |
| `setStationHull(v)` | Sets station hull | `{hull}` |
| `setBeacon(v)` | Sets station beacon | `{beacon}` |
| `setThreatLevel(n)` | Sets station threat level | `{threatLevel}` |
| `setDay(n)` | Sets station day | `{day}` |
| `setDayTimer(ms)` | Sets station day timer | `{dayTimerMs}` |
| `setScore(v)` | Sets station score | `{score}` |
| `setLastEvents(e1, e2, e3)` | Sets last event history | `{lastEvent1, lastEvent2, lastEvent3}` |
| `addLoot(itemId, count, x, y)` | Adds loot at place | loot or `{ok: false}` |
| `setLoot(id, fields)` | Sets loot fields | loot |
| `clearLoot()` | Removes all loot | `{loot: 0}` |
| `addHazard(type, x, y)` | Adds hazard at place | hazard or `{ok: false}` |
| `setHazard(id, fields)` | Sets hazard fields | hazard |
| `clearHazards()` | Removes all hazards | `{hazards: 0}` |
| `addEnemy(type, x, y)` | Adds enemy at place | enemy or `{ok: false}` |
| `setEnemy(id, fields)` | Sets enemy fields | enemy |
| `clearEnemies()` | Removes all enemies | `{enemies: 0}` |
| `addObject(type, x, y)` | Adds station object at place | object or `{ok: false}` |
| `setObject(id, fields)` | Sets object fields | object |
| `clearObjects()` | Removes all station objects | `{objects: 0}` |
| `setInventory(slot, itemId, count)` | Sets one inventory slot | `{slot}` |
| `addItem(itemId, count)` | Adds item to a valid slot | `{slot, count}` or `{ok: false}` |
| `clearInventory()` | Empties inventory | `{inventory}` |
| `setCraftOpen(b)` | Sets craft menu open | `{open}` |
| `setCraftSelected(n)` | Sets craft selected recipe | `{selected}` |
| `setCraftTimer(ms)` | Sets craft timer | `{timerMs}` |
| `triggerEvent(eventId)` | Applies one threat event now | `{event}` |
| `runDayCycle()` | Runs one day-end cycle now | `{day}` |
| `setFloorTile(tx, ty)` | Sets tile to floor | `{tile}` |
| `setWallTile(tx, ty)` | Sets tile to wall | `{tile}` |
| `clearDynamic()` | Removes enemies, hazards, loot, and objects | `{enemies, hazards, loot, objects}` |
| `fillCaps()` | Fills loot, hazards, enemies, and objects to caps | `{loot, hazards, enemies, objects}` |
| `queueAudio(event)` | Enqueues an audio event | `{event, queued: true}` |
| `setMuted(b)` | Sets audio muted | `{muted}` |
| `clearAudio()` | Clears audio queue and counters | `{queue: 0, audioEvents: 0}` |

# 9. TESTS

All checks use only calls listed in Section 8.

1. **Boot and clean start**  
   Calls: `start(1); clearDynamic();`  
   Find: `state === 'run'`, `tick === 0`, `timeMs === 0`, `frame.drawOps === 0`, `frame.activeEntities === 0`.

2. **Time fast-forward**  
   Calls: `start(1); clearDynamic(); setPlayerOxygen(1000000); setStationOxygen(1000000); setStationPower(1000000); setHealth(1000000); setTime(0.05);`  
   Find: `state === 'run'`, `tick === 5`, `timeMs === 50`, `frame.drawOps === 0`.

3. **Rng exact state**  
   Calls: `start(1); setRngState(1); roll();`  
   Find: `rngState === 16807`.  
   Calls: `roll();`  
   Find: `rngState === 282475249`.

4. **Input persistence**  
   Calls: `start(1); clearDynamic(); move(1,0);`  
   Find: `input.moveX === 1`, `input.moveY === 0`.  
   Calls: `move(0,1);`  
   Find: `input.moveX === 0`, `input.moveY === 1`.  
   Calls: `move(0,0);`  
   Find: `input.moveX === 0`, `input.moveY === 0`.

5. **Player movement**  
   Calls: `start(1); clearDynamic(); setPlayer(100000,100000); setPlayerVelocity(300,0); move(1,0); step(0.01,1);`  
   Find: `player.x === 100300`, `player.y === 100000`, `player.facing === 0`, `timeMs === 10`.

6. **World collision**  
   Calls: `start(1); clearDynamic(); setFloorTile(1,0); setWallTile(2,0); setPlayer(19900,5000); setPlayerVelocity(300,0); move(1,0); step(0.01,1);`  
   Find: `player.x === 19900`, `player.y === 5000`.

7. **Player oxygen drain**  
   Calls: `start(1); clearDynamic(); setPlayerOxygen(1000000); setStationOxygen(600000); setHealth(1000000); step(0.01,1);`  
   Find: `player.oxygen === 999960`, `timeMs === 10`.

8. **Loot interaction**  
   Calls: `start(1); clearDynamic(); selectSlot(6); setInventory(6,'scrap',0); addLoot('scrap',2,100000,100000); setPlayer(100000,100000); interact(); step(0.01,30);`  
   Find: `loot[0].opened === true`, `inventory[2].count === 4`.

9. **Hazard effect**  
   Calls: `start(1); clearDynamic(); addHazard('vent',100000,100000); setPlayer(100000,100000); setPlayerOxygen(1000000); setStationOxygen(1000000); setHealth(1000000); step(0.01,1);`  
   Find: `player.oxygen === 999760`, `station.oxygen === 999900`.

10. **Enemy windup damage**  
   Calls: `start(1); clearDynamic(); setHealth(1000000); addEnemy('mite',105000,100000); setEnemy(1,{state:'windup', windupTimerMs:400, attackCooldownMs:0, x:105000, y:100000, health:200000}); setPlayer(100000,100000); step(0.01,40);`  
   Find: `player.health === 995000`, `enemies[0].state === 'chase'`, `enemies[0].attackCooldownMs === 1200`.

11. **Station Power**  
   Calls: `start(1); clearObjects(); clearEnemies(); clearHazards(); clearLoot(); addObject('power_bay',100000,100000); setObject(1,{integrity:1000000, load:50000, active:false}); setStationPower(900000); setStationOxygen(1000000); step(0.01,1);`  
   Find: `station.power === 900200`, `objects[0].load === 49995`.

12. **Crafting O2 Cell**  
   Calls: `start(1); clearEnemies(); clearHazards(); clearLoot(); setInventory(1,'o2_cell',1); setInventory(2,'filter',1); setInventory(3,'battery',1); setInventory(4,'scrap',0); setInventory(6,'scrap',0); setCraftOpen(true); setCraftSelected(1); setStationPower(100000); setScore(0); setCraftTimer(2000); step(0.01,200);`  
   Find: `inventory[0].count === 2`, `inventory[1].count === 0`, `inventory[2].count === 0`, `station.score === 5`.

13. **Daily Cycle**  
   Calls: `start(1); clearEnemies(); clearHazards(); clearLoot(); setDay(1); setDayTimer(239990); setThreatLevel(1); setStationHull(1000000); setScore(0); setLastEvents('vent_burst','radiation_leak','drone_awakening'); step(0.01,1);`  
   Find: `station.day === 2`, `station.dayTimerMs === 0`, `station.threatLevel === 2`, `station.score === 100`, `enemies.length >= 1`.

14. **Map Generator**  
   Calls: `start(1);`  
   Find: `map.hubConsoleX === 245000`, `map.hubConsoleY === 155000`, `map.reachable === true`, `loot.length >= 27`, `hazards.length === 6`, `enemies.length === 2`, `objects.length === 13`.

15. **Audio event**  
   Calls: `start(1); clearDynamic(); setMuted(true); queueAudio('ui_click'); step(0.01,1);`  
   Find: `audio.muted === true`, `audio.lastEvent === 'ui_click'`, `frame.audioEvents === 1`.

16. **Budget cap**  
   Calls: `start(1); clearDynamic(); fillCaps(); step(0.01,1);`  
   Find: `frame.activeEntities ≤ 112`, `frame.drawOps ≤ 120`, `JSON.stringify(getState()).length ≤ 65536`.

17. **Determinism**  
   Run 1 and Run 2 calls, identical:  
   `start(1); setRngState(1); clearDynamic(); setPlayer(100000,100000); setPlayerVelocity(0,0); setSprint(false); setPlayerOxygen(1000000); setStationOxygen(1000000); setStationPower(1000000); setHealth(1000000); addEnemy('mite',110000,100000); addHazard('vent',120000,100000); addLoot('scrap',1,105000,100000); step(0.01,5); getState();`  
   Find: the full `JSON.stringify(getState())` from Run 1 is identical to Run 2.

**SCREENSHOTS.**

| Screen / state | Tier | How to reach | What a person must see |
| --- | --- | --- | --- |
| Title | T1 | Launch the game, before pressing Start | #020617 background, #e2e8f0 title, #ffbf3f prompt, #334155 rotating station ring |
| Spawn in Medbay | T1 | Press Start | Top-down Medbay room, clean white panels, red cross decals, cyan O2 cell bobbing, white player sprite, HUD bars |
| Main corridor | T1 | Exit Medbay doorway | Dark steel corridor, red emergency light, amber floor strip, dust in player flashlight beam |
| Hub | T1 | Walk from corridor into centre | Hub floor, hub console, at least one viewport, amber floor ring, white-amber light |
| Crew Quarters | T1 | Enter quarters room | Top-down bunks, rust-orange tool cart, warm amber work light, dented wall panels |
| Galley | T1 | Enter galley room | Top-down long gray table, cyan vending slot, broken amber work light with smoke |
| Hydroponics | T1 | Enter hydro room | Four teal-lit plant racks, green leaves, wet floor plates, faint mist |
| Reactor | T1 | Enter reactor room | Violet pulsing core, dark pipes, yellow-black caution stripes, optional jammed door status if T2 |
| Escape Airlock goal | T2 | Enter airlock room | White escape pod, red-and-white hazard stripes, large viewport, green hatch status |
| Door open | T2 | Open any functional door | Door rotates 90 degrees over 0.70s, status changes from #ff3b30 to #22c55e, small dust puff |
| Door jammed | T2 | Reach a jammed door state | #f59e0b status flashes at 1 Hz, two amber sparks every 1.0s, door does not rotate |
| Mite idle | T1 | Mite present in corridor | Orange box mite, black tracks, red eye, idle bob, cable sway |
| Mite hurt | T1 | Hit the mite once | Smoke puff, eye flicker, body shake, 12 amber sparks, 0.40s |
| Mite death | T1 | Reduce mite to dead state | Mite tilts and drops 0.25 units, eye becomes #450a0a, 3 smoke puffs, sparks, coolant drop |
| Wraith idle | T1 | Wraith present after day 3 | Pale slender body, vertical violet eye, teal vents, gentle sway |
| Overseer idle | T1 | Overseer present after day 7 | Heavy rust-red armor, large red eye, slow heave |
| Hull breach | T1 | Reach an active radiation hazard | Violet-rimmed hazard, #dbeafe mist, rising bubbles, shards, floor breach stain |
| Low O2 | T1 | Player O2 enters low state | #ef4444 O2 bar strobes red/white, red vignette, increased grain, objective text pulses |
| Player damage | T1 | Take damage | Red vignette to 0.45, damage shake, suit crack line flash, 0.40s |
| Player death | T1 | Player health enters dead state | Desaturation to #475569, camera tilt and drop, #ef4444 death text, fade to black |
| Pickup toast | T1 | Collect any pickup | 18 x 5.0 UI panel, icon, #38bdf8 border, slide-in 0.25s, fade 0.35s |
| Alarm state | T1 | Alarm condition active | #ef4444 full-screen border strobes every 0.80s, emergency lights stronger, red vignette |

# 10. BUILD ORDER

| Milestone | Modules added | Check that proves it landed |
| --- | --- | --- |
| M1 | `Loop`, `Rng`, `Renderer`, `Debug`, title screen | Check 1, Check 3, Check 15 |
| M2 | `Input`, `Player` | Check 4, Check 5 |
| M3 | `World`, Map Generator | Check 6, Check 14 |
| M4 | `LifeSupport`, `Power` | Check 7, Check 11 |
| M5 | `Interact`, Loot, `Crafting` | Check 8, Check 12 |
| M6 | `Hazards`, `Enemies` | Check 9, Check 10 |
| M7 | `Daily`, Threat Events, Audio integration | Check 13, Check 15 |
| M8 | Full `Rng` integration, budget enforcement, determinism | Check 16, Check 17 |

M1 opens a page, draws the title, and can enter play. Every later milestone leaves the game playable.

# 11. DEFINITION OF DONE

**Survive on a derelict space station.**  
Checks: 2, 7, 9, 10, 11, 13.  
Screenshots: Low O2, Player damage, Player death, Mite idle, Mite hurt, Mite death, Hull breach, Alarm state.

**Added: 2D top-down station cross-section with tile-based movement.**  
Checks: 1, 5, 6, 14, 16.  
Screenshots: Title, Spawn in Medbay, Main corridor, Hub, Crew Quarters, Galley, Hydroponics, Reactor.

**Added: collect scrap, batteries, filters, coolant, emergency supplies.**  
Checks: 8, 12, 14.  
Screenshots: Spawn in Medbay, Pickup toast, Hull breach.

**Added: repair power bays, oxygen scrubbers, hull seals.**  
Checks: 11, 12, 14.  
Screenshots: Hub, Reactor, Alarm state.

**Added: fight awakened maintenance drones that hunt by sight and noise.**  
Checks: 10, 13, 17.  
Screenshots: Mite idle, Mite hurt, Mite death, Wraith idle, Overseer idle.

**Added: personal oxygen and station oxygen management.**  
Checks: 2, 7, 9, 11.  
Screenshots: Low O2, Player damage, Alarm state.

**Added: day counter, threat level, random station events.**  
Checks: 13, 17.  
Screenshots: Alarm state, Player death.

**Added: beacon milestones that unlock small permanent upgrades.**  
Checks: 13, 17.  
Screenshots: Alarm state.

**Added: best day and best score across runs.**  
Checks: 1, 13.  
Screenshots: Title, Player death.

**Added: HUD, screens, touch controls.**  
Checks: 1, 4, 15, 16.  
Screenshots: Title, Spawn in Medbay, Pickup toast, Low O2, Player death, Alarm state.

**Added: Web Audio API generated feedback.**  
Checks: 15.  
Screenshots: Pickup toast, Player damage, Player death.

**Added: debug API and deterministic tests.**  
Checks: 1 through 17.  
Screenshots: Title, Spawn in Medbay, Main corridor, Hub.

When every header is complete the game is complete.

# A. SANITY

- Checked every field read or written by Section 4 rules against Section 2 global context: Player, Inventory Slot, Item, Station, Station Object, Enemy, Hazard, Loot Container, Threat Event, Run Record, craft state, UI state, map state, frame state, and audio state are present. Result: closes.
- Checked every place, thing, or kind named by rules is placed by a generator or listed in a roster: rooms, hub_console, scrubbers, power_bays, hull_seals, loot containers, hazards, enemies, and items are placed by Map Generator or listed in rosters. Result: closes.
- Checked consumable totals against core-loop demand: initial loot gives 8 scrap, 4 battery, 3 filter, 2 fuse, 3 o2_cell, 2 medkit, 1 repair_kit, 1 hull_patch, plus 3 added coolant. Enemy deaths add coolant drops. O2 cells, medkits, repair kits, hull patches, batteries, filters, fuses, and coolant can be replenished through loot, crafting, supply_drop, and enemy drops. Result: closes.
- Checked timing pair station oxygen drain against scrubber refill: base drain is 0.5/s; four active scrubbers add 1.4/s, three add 1.05/s, two add 0.7/s, one adds 0.35/s. With four or three scrubbers the station can recover; with two or fewer it loses air unless leaks are repaired. Result: closes and bites.
- Checked timing pair hazard disable against day length: coolant disables a hazard for 120 s, which is half a 240 s day, so disabled hazards reappear and force repeated decisions. Result: closes and bites.
- Checked timing pair enemy windup against player attack: enemy windup is 0.4 s, player attack cooldown is 0.5 s, enemy attack cooldowns are 1.2 s to 2.0 s. The player can punish one enemy but can become pressured by multiple enemies. Result: closes and bites.
- Checked timing pair travel time against distance: player walk is 3 tile/s, sprint is 5 tile/s; mite base speed is 2.2 tile/s with maximum threat bonus 0.5 tile/s, so mites cannot outrun a walking player. The kill pressure comes from windup, cornering, noise detection, sabotage, and daily station decay rather than a pure chase clock. The daily clock is always reachable because it advances every 240 s. Result: closes as a survival clock; movement chase is ruled not to be a catch clock.
- Checked end-condition clock against expected clear time: there is no scripted win clock. The run ends when player health reaches 0 or station hull reaches 0. Daily decay, threat escalation, hazards, and drone spawns make both conditions reachable in a finite expected time. Result: closes.
- Checked every call in Section 9 is present in Section 8: all test calls are listed in the debug table. Result: closes.
- Checked for remaining placeholders in angle brackets: none remain. Result: closes.
- Fixed Section 1 bounds from 30000 to 480000 by 300000 to match 48 by 30 tiles at 10000 units per tile. Result: changed.
- Fixed Section 2 global context to include all gameplay records, craft state, UI state, map state, and run record. Result: changed.
- Fixed Section 4 Map Generator to add 3 coolant containers and enemy death coolant drops to close the coolant supply gap. Result: changed.
- Fixed Section 9 tests to use merged units, merged debug calls, and merged survival rules. Result: changed.