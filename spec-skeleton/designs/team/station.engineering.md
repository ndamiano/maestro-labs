2D; the game view is rendered by Canvas 2D.

# 1. CONVENTIONS

- **Units:** 100 game units = 1 CSS pixel. All world coordinates are integer game units.
- **Time:** One canonical tick is 10 ms = 0.01 s. Gameplay speeds are integer game units per canonical tick. Gameplay rates are integer centipercents per canonical tick, where 100 = 1% and 10000 = 100%.
- **Axes:** x increases right, y increases down. Up is negative y. Origin is the top-left corner of the station floor at `(0,0)`.
- **Floor bounds:** collision and wrap bounds are `x: 0..30000`, `y: 0..30000` game units.
- **Facing:** 2D integer octants. `0` = +x, `1` = +x+y, `2` = +y, `3` = -x+y, `4` = -x, `5` = -x-y, `6` = -y, `7` = +x-y.
- **Update loop:** fixed step of 10 ms. Rendering happens after update ticks.
- **System order each tick:** `Input`, `Player`, `Interact`, `Hazards`, `Survival`, `Audio`, then `Renderer.draw()`.
- **Real-time loop:** `requestAnimationFrame` accumulates elapsed ms, clamps to 20 ms, runs whole 10 ms ticks, then draws once.
- **Randomness:** one named source, `Rng`, using the Lehmer LCG:
  ```js
  rngState = (rngState * 16807) % 2147483647;
  if (rngState === 0) rngState = 1;
  next = rngState / 2147483647;
  ```
  All game logic uses only `Rng`. `Math.random`, `Date.now`, and network are not allowed for game logic.

## Controls

| Input | Action |
|---|---|
| W / ArrowUp | `move(0,-1)` |
| S / ArrowDown | `move(0,1)` |
| A / ArrowLeft | `move(-1,0)` |
| D / ArrowRight | `move(1,0)` |
| Release all movement input | `move(0,0)` |
| E / K / Space | `interact()` |
| Touch drag | `move(axis sign, 0)` or `move(0, axis sign)` using dominant axis |
| Touch release | `move(0,0)` |
| Touch tap | `interact()` |

# 2. MODULES

| Module | Responsibility |
|---|---|
| `Loop` | Fixed-timestep scheduling and render dispatch |
| `Input` | Keyboard/touch to `G.input` |
| `Rng` | Seeded random source |
| `World` | Walls, doors, pickups, hazards storage and rebuild |
| `Player` | Movement, facing, collision, health |
| `Interact` | Consumes pickups and doors on `interact()` |
| `Survival` | Oxygen, health, stage completion |
| `Hazards` | Hazard timers, movement, damage |
| `Audio` | Web Audio event playback and audio queue |
| `Renderer` | Canvas 2D drawing and draw-op count |
| `Debug` | Installs `window.__game` |

Modules communicate only through one global context, `G`. No module imports another except through `G`.

## GLOBAL CONTEXT

```js
const G = {
  state: 'title', // 'title' | 'playing' | 'dead'
  tick: 0,        // integer
  timeMs: 0,      // integer
  fixedTickMs: 10,
  seed: 1,
  rngState: 1,

  input: {
    moveX: 0,
    moveY: 0,
    interactQueued: false
  },

  player: {
    id: 'player',
    x: 0,
    y: 0,
    facing: 0,
    radius: 1000,
    speed: <player speed>,       // integer game units/tick
    health: <starting health>,   // integer centipercents
    alive: true
  },

  oxygen: {
    level: <starting oxygen>,    // integer centipercents
    max: 10000,
    drain: <oxygen drain>,       // integer centipercents/tick
    damage: <oxygen damage>      // integer centipercents/tick when empty
  },

  hazard: {
    speed: <hazard speed>,       // integer game units/tick
    damage: <hazard damage>      // integer centipercents/tick
  },

  pickup: {
    oxygenRestore: <oxygen restore> // integer centipercents
  },

  stage: {
    current: 1,
    kits: 0,
    kitsRequired: <kits required>,
    complete: false
  },

  audio: {
    muted: false,
    lastEvent: '',
    queue: []
  },

  frame: {
    drawOps: 0,
    activeEntities: 0,
    audioEvents: 0
  },

  pools: {
    pickups: new Array(64).fill(null),
    hazards: new Array(32).fill(null),
    doors: new Array(16).fill(null),
    walls: new Array(128).fill(null)
  },

  ids: {
    pickup: 1,
    hazard: 1,
    door: 1,
    wall: 1
  },

  systemOrder: ['input', 'player', 'interact', 'hazards', 'survival', 'audio']
};
```

## Exported functions

### Loop
- `Loop.install(canvas): void` — installs the fixed-step `requestAnimationFrame` loop.
- `Loop.advance(dtMs, n): {tick, timeMs, drawOps, activeEntities}` — runs `n` ticks of `dtMs` ms and draws once.

### Input
- `Input.install(): void` — binds keyboard and touch listeners.
- `Input.update(): void` — normalizes persistent move input.
- `Input.debugMove(x, y): {moveX, moveY}` — sets persistent move direction.
- `Input.debugInteract(): {interactQueued: true}` — queues one interact action.

### Rng
- `Rng.reseed(n): {seed, rngState}` — reseeds the LCG.
- `Rng.next(): number` — returns the next random value in `[0,1)`.
- `Rng.rangeInt(min, max): number` — returns an integer in inclusive range.
- `Rng.pick(arr): any` — returns a pseudo-random element.

### World
- `World.init(seed): void` — clears and rebuilds generated world records.
- `World.clear(): {pickups, hazards, doors, walls}` — removes all records.
- `World.addWall(x, y, w, h): wall` — adds a wall if capacity allows.
- `World.addDoor(x, y, w, h): door` — adds a closed door if capacity allows.
- `World.addPickup(type, x, y): pickup` — adds a pickup if capacity allows.
- `World.addHazard(type, x, y): hazard` — adds a hazard if capacity allows.

### Player
- `Player.update(): void` — moves player, updates facing, resolves collisions.
- `Player.set(x, y): {x, y}` — teleports player.
- `Player.setSpeed(v): {speed}` — sets player speed field.
- `Player.setHealth(v): {health}` — sets player health.
- `Player.damage(v): {health, alive}` — applies damage.
- `Player.heal(v): {health}` — applies healing.

### Interact
- `Interact.update(): {consumed, targetId}` — consumes one queued interact action.

### Survival
- `Survival.update(): {health, oxygen, stageComplete}` — updates oxygen, health, stage.
- `Survival.setOxygen(v): {level}` — sets oxygen level.
- `Survival.setHealth(v): {health}` — sets health.
- `Survival.setStage(n): {stage}` — skips to stage.
- `Survival.setKits(n): {kits}` — sets kit count.
- `Survival.setKitsRequired(n): {kitsRequired}` — sets kits required.

### Hazards
- `Hazards.update(): void` — advances hazard timers, moves hazards, applies damage.
- `Hazards.setSpeed(v): {speed}` — sets hazard speed default.
- `Hazards.setDamage(v): {damage}` — sets hazard damage default.

### Audio
- `Audio.update(): void` — processes the audio queue.
- `Audio.queue(event): {queued}` — enqueues an audio event.
- `Audio.setMuted(b): {muted}` — sets muted flag.

### Renderer
- `Renderer.init(canvas): void` — initializes Canvas 2D context.
- `Renderer.draw(): number` — draws current state and returns draw-op count.

### Debug
- `Debug.install(): void` — installs `window.__game`.

# 3. BUDGETS

- **Frame time:** target 16 ms; max catch-up is 2 ticks = 20 ms, then drop the rest.
- **Canvas operations:** `frame.drawOps <= 120` per rendered frame.
- **Entity caps:**
  - pickups: 64
  - hazards: 32
  - doors: 16
  - walls: 128
  - active dynamic entities: 112
- **Pool sizes:** fixed arrays of the same sizes as caps.
- **Audio queue:** max 16 queued events; max 4 active Web Audio sources.
- **Memory/state size:** `JSON.stringify(getState()).length <= 65536` at maximum entity caps.
- **Per-tick allocations:** none except short-lived audio source nodes.

# 4. DEBUG API

`window.__game` exposes only synchronous functions returning plain data.

| Call | What it does | Returns |
|---|---|---|
| `start()` | Enters play and resets run state | `{state, tick, timeMs}` |
| `step(dt, n)` | Advances `n` ticks of `dt` seconds, then draws once | `{tick, timeMs, drawOps, activeEntities}` |
| `setTime(t)` | Advances to the largest 10 ms multiple <= `t` seconds, no draw | `{tick, timeMs}` |
| `seed(n)` | Reseeds `Rng` and rebuilds generated records | `{seed, rngState}` |
| `getState()` | Returns all record fields as plain data | state object |
| `move(x, y)` | Sets persistent player move direction | `{moveX, moveY}` |
| `interact()` | Queues one interact action | `{interactQueued: true}` |
| `spawnPickup(type, x, y)` | Adds a pickup at a place | pickup or `{ok: false}` |
| `spawnHazard(type, x, y)` | Adds a hazard at a place | hazard or `{ok: false}` |
| `spawnWall(x, y, w, h)` | Adds a wall | wall or `{ok: false}` |
| `spawnDoor(x, y, w, h)` | Adds a closed door | door or `{ok: false}` |
| `setPlayer(x, y)` | Teleports player | `{x, y}` |
| `setPlayerSpeed(v)` | Sets player speed | `{speed}` |
| `setHealth(v)` | Sets player health | `{health}` |
| `setOxygen(v)` | Sets oxygen level | `{level}` |
| `setOxygenDrain(v)` | Sets oxygen drain rate | `{drain}` |
| `setHazardSpeed(v)` | Sets hazard speed default | `{speed}` |
| `setHazardDamage(v)` | Sets hazard damage default | `{damage}` |
| `setStage(n)` | Skips to stage | `{stage}` |
| `setKits(n)` | Sets kit count | `{kits}` |
| `setKitsRequired(n)` | Sets kits required | `{kitsRequired}` |
| `setRngState(n)` | Sets `rngState` directly | `{rngState}` |
| `clearEntities()` | Removes all records | `{pickups:0, hazards:0, doors:0, walls:0}` |
| `fillPools()` | Fills pickups, hazards, doors to caps | `{pickups:64, hazards:32, doors:16}` |
| `queueAudio(event)` | Enqueues an audio event | `{event, queued: true}` |
| `setMuted(b)` | Sets audio muted | `{muted}` |
| `roll()` | Returns next `Rng` value | number |

# 5. TESTS

All checks use only calls listed in section 4. Angle-bracket values are integer gameplay values from the merged spec.

1. **Boot and clean start**  
   Calls: `seed(1); clearEntities(); start();`  
   Find: `state === 'playing'`, `tick === 0`, `timeMs === 0`, `frame.activeEntities === 0`, `frame.drawOps === 0`.

2. **Time fast-forward**  
   Calls: `seed(1); clearEntities(); start(); setOxygen(10000); setOxygenDrain(0); setHealth(10000); setTime(0.05);`  
   Find: `state === 'playing'`, `tick === 5`, `timeMs === 50`, `frame.drawOps === 0`.

3. **Rng exact state**  
   Calls: `seed(1); clearEntities(); start(); setRngState(1); roll();`  
   Find: `rngState === 16807`.  
   Calls: `roll();`  
   Find: `rngState === 282475249`.

4. **Input persistence**  
   Calls: `seed(1); clearEntities(); start(); move(1,0);`  
   Find: `input.moveX === 1`, `input.moveY === 0`.  
   Calls: `move(0,1);`  
   Find: `input.moveX === 0`, `input.moveY === 1`.  
   Calls: `move(0,0);`  
   Find: `input.moveX === 0`, `input.moveY === 0`.

5. **Player movement**  
   Calls: `seed(1); clearEntities(); start(); setPlayer(0,0); setPlayerSpeed(<player speed>); move(1,0); step(0.01,1);`  
   Find: `player.x === <player speed>`, `player.y === 0`, `player.facing === 0`, `timeMs === 10`.

6. **World collision**  
   Calls: `seed(1); clearEntities(); start(); spawnWall(12000,10000,2000,2000); setPlayer(11000,10000); setPlayerSpeed(<player speed>); move(1,0); step(0.01,1);`  
   Find: `player.x === 11000`, `player.y === 10000`, `walls[0].x === 12000`.

7. **Oxygen drain**  
   Calls: `seed(1); clearEntities(); start(); setOxygen(10000); setOxygenDrain(<oxygen drain>); step(0.01,1);`  
   Find: `oxygen.level === Math.max(0, 10000 - <oxygen drain>)`, `timeMs === 10`.

8. **Pickup interaction**  
   Calls: `seed(1); clearEntities(); start(); setPlayer(0,0); setKitsRequired(10000); setKits(0); spawnPickup('kit',0,0); interact(); step(0.01,1);`  
   Find: `stage.kits === 1`, `pickups[0].active === false`, `pickups[0].type === 'kit'`.

9. **Door interaction**  
   Calls: `seed(1); clearEntities(); start(); setPlayer(0,0); spawnDoor(1000,0,2000,2000); interact(); step(0.01,1);`  
   Find: `doors[0].open === true`, `doors[0].x === 1000`.

10. **Hazard timer and neutral damage**  
   Calls: `seed(1); clearEntities(); start(); setPlayer(10000,0); setHealth(10000); setHazardSpeed(0); setHazardDamage(0); spawnHazard('plasma',0,0); step(0.01,1);`  
   Find: `hazards[0].timerMs === 10`, `hazards[0].x === 0`, `player.health === 10000`.

11. **Stage completion**  
   Calls: `seed(1); clearEntities(); start(); setOxygen(10000); setOxygenDrain(0); setHealth(10000); setStage(1); setKitsRequired(1); setKits(1); step(0.01,1);`  
   Find: `stage.complete === true`, `stage.current === 2`, `stage.kits === 0`.

12. **Budget cap**  
   Calls: `seed(1); clearEntities(); start(); fillPools(); step(0.01,1);`  
   Find: `frame.activeEntities === 112`, `frame.drawOps <= 120`, `JSON.stringify(getState()).length <= 65536`.

13. **Audio event**  
   Calls: `seed(1); clearEntities(); start(); setMuted(true); queueAudio('footstep'); step(0.01,1);`  
   Find: `audio.muted === true`, `audio.lastEvent === 'footstep'`, `frame.audioEvents === 1`.

14. **Determinism**  
   Calls, run twice:  
   `seed(42); clearEntities(); start(); setPlayerSpeed(<player speed>); setOxygenDrain(<oxygen drain>); setHazardSpeed(0); setHazardDamage(0); setKitsRequired(10000); move(1,0); spawnPickup('oxygen',100,0); spawnHazard('plasma',200,0); step(0.01,5);`  
   Find: the full `JSON.stringify(getState())` from run 1 is identical to run 2.

# 6. BUILD ORDER

| Milestone | Modules added | Check that proves it landed |
|---|---|---|
| M1 | `Loop`, `Rng`, `Renderer`, `Debug` | Check 1 |
| M2 | `Input`, `Player` | Check 5 |
| M3 | `World` | Check 6 |
| M4 | `Survival` | Check 7 |
| M5 | `Interact`, `Survival` stage logic, `World` pickups/doors | Checks 8, 9, 11 |
| M6 | `Hazards` | Check 10 |
| M7 | `Audio`, budget enforcement | Checks 12, 13 |
| M8 | full `Rng` integration and determinism | Check 14 |

M1 opens a page, draws the title, and can enter play. Every later milestone leaves the game playable.

# 7. RISKS

1. **Coordinate convention error:** using y-up in code while Canvas uses y-down will flip movement, facing, and collision.  
   Rule: all game code uses y-down integer game units; no coordinate conversion is allowed after input is read.

2. **Timing race:** `requestAnimationFrame` delta and DOM input events can land between fixed ticks, causing nondeterministic movement and oxygen drain.  
   Rule: the loop only runs whole 10 ms ticks, input is edge-queued and consumed once per tick, and debug `step`/`setTime` bypass real time.

3. **Performance cliff:** a derelict station can accumulate too many pickups, hazards, doors, walls, or draw calls.  
   Rule: fixed pools, hard entity caps, `frame.drawOps <= 120`, spawner rejection when full, and renderer stop drawing further operations once the draw-op budget is reached.