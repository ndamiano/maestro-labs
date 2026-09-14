# engineering.md

**2D. The game view is rendered on a single `<canvas>` element using the Canvas 2D API.**

---

# 1. CONVENTIONS

## Units & Axes

| Item | Rule |
|---|---|
| 1 unit | 1 logical pixel. The canvas is sized to `1280 × 720` CSS px; internal resolution matches at `devicePixelRatio = 1`. |
| Game-logic axes | **X** → right is positive. **Y** → **up** is positive (ground plane at `y = 0`). Gravity pulls in −Y. |
| Render axes | Canvas default: X → right, Y → **down**. The renderer applies `ctx.scale(1, -1)` after translating to the camera offset so game-logic Y-up maps correctly. |
| Origin (world) | Bottom-left corner of the level's tile grid. `worldOrigin = {x: 0, y: 0}`. |
| Tile size | `<TILE_SIZE>` px (gameplay owns the value; engineering assumes it is a positive integer, typically 32). |
| Camera | Follows the player. `camera.x` = left edge of viewport in world coords; `camera.y` = bottom edge of viewport. Clamped so the viewport never shows outside the level bounds. |

## Update Loop

- **Fixed timestep:** `DT = 1/60 ≈ 0.016666667 s`.
- Each `requestAnimationFrame` callback accumulates real elapsed time, then runs zero or more fixed ticks, then draws **once**.
- **Tick order (every system runs in this exact sequence):**
  1. `input.update()` — latch new key/touch events into the current frame's input state.
  2. `physics.update(DT)` — integrate velocities, resolve tile collisions, resolve entity–entity collisions.
  3. `player.update(DT)` — state machine (idle / run / jump / crouch / shoot / hurt / dead).
  4. `weapons.update(DT)` — fire cooldowns, spawn / advance / despawn projectiles.
  5. `enemies.update(DT)` — AI state machines, patrol, chase, die.
  6. `particles.update(DT)` — advance particle lifetimes, recycle dead ones.
  7. `camera.update(DT)` — lerp / dead-zone follow, clamp to level bounds.
  8. `progression.update(DT)` — check stage-clear conditions, trigger transitions.
  9. `audio.update(DT)` — process queued sound events (purely reactive; never mutates game state).
- **After all ticks for this frame:** `renderer.draw()` is called exactly once.

## Random Source

- **One** seeded PRNG: `mulberry32(seed)`, exposed as `ctx.rng()`. It returns a float in `[0, 1)`.
- **Rule:** No call to `Math.random()`, `crypto.getRandomValues()`, `Date.now()`, or any other entropy source anywhere in game logic. The renderer and audio may use `Math.random()` for purely cosmetic jitter that is never read back into state. All gameplay randomness (enemy spawn waves, pickup drops, pattern selection) goes through `ctx.rng()`.

## Controls

| Input | Action |
|---|---|
| `A` / `←` | Move left (held) |
| `D` / `→` | Move right (held) |
| `W` / `↑` / `Space` | Jump (edge-triggered: fires once per press) |
| `S` / `↓` | Crouch (held) |
| `J` / `Z` / `Enter` | Fire current weapon (held = auto-repeat for auto weapons; edge for semi) |
| `K` / `X` | Switch weapon forward (cycles through owned guns) |
| `1` `2` `3` `4` `5` | Select weapon slot 1–5 directly |
| `Esc` / `P` | Pause / Resume |
| `R` | Restart current stage |
| Touch – left half swipe/hold | Move left / right (analog by distance from centre of half) |
| Touch – right half, top area | Jump (tap) |
| Touch – right half, bottom area | Fire (hold) |
| Touch – right half, middle area | Crouch (hold) |
| Touch – two-finger tap | Switch weapon |

All keyboard bindings are **both** WASD and arrow keys simultaneously. Touch events are synthesised into the same input-state object so no game code branches on input device.

---

# 2. MODULES

| Module | Responsibility |
|---|---|
| `game.js` | Boot, state machine (title → play → pause → stage-clear → world-clear → game-over → title), owns the rAF loop, calls every other module in tick order. |
| `input.js` | Reads `keydown/keyup/touchstart/touchmove/touchend`, writes `ctx.input`. Normalises keyboard + touch into one structure. |
| `physics.js` | AABB tile collision, entity-vs-entity collision, gravity integration, ground detection. Pure geometry; no game rules. |
| `player.js` | Player entity: state machine, health, lives, crouch height change, jump arc, invincibility frames, respawn. |
| `weapons.js` | Weapon definitions (≥4 types), fire logic, projectile pool, damage application. |
| `enemies.js` | Enemy definitions, per-type AI tick, spawn from level data, death → drop logic. |
| `level.js` | Parses the tile-map array for the current stage, provides `isSolid(tx,ty)`, `isHazard(tx,ty)`, `tileAt(x,y)`, entity spawn lists. |
| `camera.js` | Viewport rect, dead-zone follow, clamp to level bounds. |
| `particles.js` | Ring-buffer pool of particle structs; spawn, update, query-alive for renderer. |
| `audio.js` | Web Audio API: pre-built oscillator/noise buffers for SFX, a simple music sequencer. Queues events from other modules; never reads game state back. |
| `progression.js` | World/stage index, unlock table, score accumulation, stage-clear / game-over conditions. |
| `ui.js` | HUD (health bar, lives, weapon icon, ammo, score, world-stage label), title screen, pause overlay, stage-clear overlay. Draws into the same canvas or DOM overlay. |
| `debug.js` | Installs `window.__game` (Section 4). Imported only in debug builds (flag in `game.js`). |

## GLOBAL CONTEXT

One plain object created in `game.js` at boot and passed to every module's `init(ctx)` / `update(ctx, dt)` / `draw(ctx)` calls. No module imports another; all cross-module data flows through `ctx`.

```js
/**
 * ctx – the single global context object.
 * Every field is plain data (numbers, strings, booleans, arrays,
 * plain objects). No class instances, no closures, no DOM refs
 * (except the canvas element itself, stored once).
 */
const ctx = {
  // ---- environment ----
  canvas:        null,            // HTMLCanvasElement
  ctx2d:         null,            // CanvasRenderingContext2D
  seed:          0,               // uint32 – current PRNG seed
  rng:           null,            // function(): number  – seeded PRNG
  dt:            0.016666667,     // fixed timestep in seconds
  time:          0,               // seconds elapsed in current stage (accumulated)
  frame:         0,               // integer tick counter (current stage)
  running:       true,            // false while paused
  state:         'title',         // 'title'|'play'|'pause'|'stage-clear'|'world-clear'|'game-over'

  // ---- input (written by input.js, read by everyone) ----
  input: {
    moveDir:     0,               // -1 left, 0 neutral, +1 right
    jumpPressed: false,           // true on the single tick the key goes down
    jumpHeld:    false,
    crouchHeld:  false,
    firePressed: false,
    fireHeld:    false,
    switchNext:  false,           // edge
    weaponSlot:  0,               // 0 = no explicit slot this frame, 1-5 = slot
    pause:       false,
    restart:     false,
    touch:       null,            // {x,y,active} or null
  },

  // ---- player (written by player.js, read by physics/weapons/enemies/ui) ----
  player: {
    x: 0, y: 0,                   // world position (feet / bottom-centre)
    vx: 0, vy: 0,                 // velocity px/s
    w: <PLAYER_W>, h: <PLAYER_H>,// current hitbox (h shrinks when crouching)
    facing: 1,                    // +1 right, -1 left
    onGround: false,
    crouching: false,
    state: 'idle',                // 'idle'|'run'|'jump'|'fall'|'crouch'|'hurt'|'dead'
    hp: <PLAYER_MAX_HP>,          // integer
    lives: <PLAYER_LIVES>,        // integer
    invulnTimer: 0,               // seconds remaining of post-hit invincibility
    weaponIndex: 0,               // index into player.weapons
    weapons: [0,0,0,0,0],         // 0 = not owned, >0 = owned (id)
    ammo:  [0,0,0,0,0],           // per-slot ammo (0 = infinite for some guns)
    shootCooldown: 0,             // seconds until next shot allowed
  },

  // ---- weapons / projectiles (written by weapons.js) ----
  projectiles: [ /* pool of {x,y,vx,vy,w,h,damage,alive,owner} */ ],
  projectilePoolSize: <PROJECTILE_POOL>,

  // ---- enemies (written by enemies.js) ----
  enemies: [ /* pool of {x,y,vx,vy,w,h,hp,type,alive,state,timer,...} */ ],
  enemyPoolSize: <ENEMY_POOL>,

  // ---- particles (written by particles.js) ----
  particles: [ /* ring buffer of {x,y,vx,vy,life,maxLife,alive} */ ],
  particlePoolSize: <PARTICLE_POOL>,

  // ---- level (written by level.js) ----
  level: {
    world:  1,                    // 1-based
    stage:  1,                    // 1-based
    tiles:  null,                 // Uint8Array, row-major, level.width × level.height
    width:  0,                    // tiles
    height: 0,                    // tiles
    spawnX: 0, spawnY: 0,        // player start in world px
    exitX:  0, exitY:  0,        // stage exit trigger zone
    hazards: null,                // Uint8Array same dims as tiles
    entitySpawns: [],             // [{type,x,y,dir}]
    bgParallax: 0.3,              // 0-1 factor for background scroll
  },

  // ---- camera ----
  camera: { x: 0, y: 0, w: 1280, h: 720 },

  // ---- progression ----
  progression: {
    score: 0,
    totalStages: 10,              // 2 worlds × 5 stages
    unlockedWorld: 1,
    unlockedStage: 1,
    stagesCleared: [],            // array of "W-S" strings
  },

  // ---- audio queue (written by any module, consumed by audio.js) ----
  audioQueue: [],                 // [{id:'jump'|'shoot'|'hit'|...}]
};
```

## Per-Module Exports

Every module exposes an object with `init(ctx)`, `update(ctx, dt)`, and (where applicable) `draw(ctx, c2d)`. Additional functions are listed below.

### `game.js`
| Export | Purpose |
|---|---|
| `boot(canvas, seed)` | Creates `ctx`, calls every module's `init`, starts rAF loop. |
| `setState(state)` | Transitions the top-level state machine; resets `time`, `frame`, `rng` per stage. |
| `loop(timestamp)` | rAF callback: accumulates, runs ticks, draws once. |

### `input.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Registers `keydown/keyup/touch*` listeners on `window`/`canvas`. |
| `update(ctx, dt)` | Latches edge-triggered flags, clears them after the tick. |
| `reset(ctx)` | Clears all input flags (called on pause, stage change). |

### `physics.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Pre-computes tile lookup tables. |
| `update(ctx, dt)` | Integrates all entities, resolves tile + entity collisions. |
| `isSolid(ctx, tx, ty)` | Returns bool; true if tile at (tx,ty) blocks movement. |
| `isHazard(ctx, tx, ty)` | Returns bool; true if tile damages on contact. |
| `tileAt(ctx, wx, wy)` | Returns tile type at world pixel position. |
| `resolveAABB(a, b)` | Returns `{overlapX, overlapY, normalX, normalY}` or null. |

### `player.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Builds player record from `ctx.level.spawnX/Y`. |
| `update(ctx, dt)` | State machine: reads `ctx.input`, sets velocity, handles jump/crouch/fire. |
| `hurt(ctx, dmg)` | Applies damage, sets invuln, triggers knockback, checks death. |
| `respawn(ctx)` | Resets player to spawn, decrements lives. |
| `getHitbox(ctx)` | Returns `{x,y,w,h}` reflecting crouch state. |

### `weapons.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Loads weapon definitions array (≥4 entries). |
| `update(ctx, dt)` | Ticks cooldowns, advances / despawns projectiles, applies projectile–enemy and projectile–player collisions. |
| `fire(ctx, weaponId)` | Spawns a projectile from the pool using the weapon's stats. |
| `getWeaponDef(id)` | Returns the definition object for a weapon id. |
| `switchWeapon(ctx, dir)` | Advances `player.weaponIndex` through owned weapons. |

### `enemies.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Loads enemy definitions; populates pool from `ctx.level.entitySpawns`. |
| `update(ctx, dt)` | Runs each alive enemy's AI, applies gravity/collision, handles death & drops. |
| `spawn(ctx, type, x, y, dir)` | Pulls an enemy from the pool and configures it. |
| `kill(ctx, enemy)` | Sets alive=false, pushes audio event, spawns particles, rolls drop via `ctx.rng()`. |

### `level.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Loads level data for `ctx.level.world / stage`. |
| `update(ctx, dt)` | Checks if player overlaps `exitX/exitY` trigger zone → pushes `stage-clear`. |
| `load(ctx, world, stage)` | Rebuilds tile arrays, spawn lists, resets `time`/`frame`. |
| `isSolid(ctx, tx, ty)` / `isHazard(ctx, tx, ty)` / `tileAt(ctx, wx, wy)` | Delegates to the tile data. |

### `camera.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Sets viewport size from canvas. |
| `update(ctx, dt)` | Dead-zone follow of player, clamp to `[0, levelWidth-viewportW]` × `[0, levelHeight-viewportH]`. |

### `particles.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Allocates ring buffer of `particlePoolSize` structs. |
| `update(ctx, dt)` | Advances each alive particle, recycles when `life <= 0`. |
| `spawn(ctx, x, y, vx, vy, life)` | Writes into next ring-buffer slot. |
| `getAlive(ctx)` | Returns array (or iterator) of alive particles for the renderer. |

### `audio.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Creates `AudioContext`, pre-builds oscillator / noise buffers. |
| `update(ctx, dt)` | Drains `ctx.audioQueue`, plays sounds. |
| `play(ctx, id)` | Queues a sound event (called by other modules via the queue, not directly). |

### `progression.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Sets `totalStages`, unlock table. |
| `update(ctx, dt)` | On `stage-clear` event: records clear, advances or loops stage/world index. |
| `advance(ctx)` | Moves to next stage; if last stage of world, moves to next world; if last world, triggers `world-clear` / win. |
| `restart(ctx)` | Resets current stage only (keeps lives, score). |

### `ui.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Nothing special. |
| `draw(ctx, c2d)` | Renders HUD, title screen, pause, overlays depending on `ctx.state`. |

### `debug.js`
See Section 4.

---

# 3. BUDGETS

Every number below is an **assertion target** for the test suite.

| Budget | Limit |
|---|---|
| Frame time (all ticks + one draw) | ≤ **16.6 ms** on a 2 GHz single-core baseline. |
| Canvas draw operations per frame | ≤ **600** `drawImage`/`fillRect`/`stroke` calls. |
| Entity caps (alive simultaneously) | Player: 1 · Enemies: **40** · Projectiles: **120** · Particles: **512** |
| Pool sizes (allocated, may be mostly dead) | Enemies: 64 · Projectiles: 256 · Particles: 1024 |
| Tile map per stage | ≤ **200 × 80** tiles (16 000 entries, `Uint8Array` → 16 KB) |
| Level data (all 10 stages, in memory) | ≤ **256 KB** |
| Total JS heap (game state + pools) | ≤ **4 MB** |
| Audio nodes alive at once | ≤ **16** |
| Max world width (px) | ≤ **6400** (200 tiles × 32 px) |
| Max world height (px) | ≤ **2560** (80 tiles × 32 px) |
| Projectiles per weapon per shot | ≤ **5** (spread / shotgun max) |
| Enemies spawned per stage (total over lifetime) | ≤ **80** |

---

# 4. DEBUG API

Installed by `debug.js` as `window.__game`. Every call is **synchronous**, returns **plain data** (numbers, strings, booleans, arrays, plain objects), and never touches the DOM.

| Call | What it does | Returns |
|---|---|---|
| `__game.start()` | Transitions from `title` → `play`, loads stage `1-1`, initialises player. No click required. | `void` |
| `__game.step(dt, n)` | Runs exactly `n` fixed ticks of `dt` seconds each (in tick order from §1), then draws once. | `void` |
| `__game.setTime(t)` | Runs ticks until `ctx.time ≥ t`, **without** drawing. | `void` |
| `__game.seed(n)` | Reseeds `ctx.rng` with `n`, calls `level.load(ctx, 1, 1)`, resets player and all pools. | `void` |
| `__game.getState()` | Returns a deep-cloned plain object containing every field listed in §2's `ctx` (minus `canvas`, `ctx2d`, `rng` function). | `{state, time, frame, seed, player, level, camera, progression, enemies: [...], projectiles: [...], particles: [...]}` |
| `__game.move(dir)` | Sets `ctx.input.moveDir = dir` (-1, 0, +1). Persists until next call. | `void` |
| `__game.jump()` | Sets `ctx.input.jumpPressed = true` for the next tick. | `void` |
| `__game.crouch(on)` | Sets `ctx.input.crouchHeld = on`. | `void` |
| `__game.fire(on)` | Sets `ctx.input.fireHeld = on` and `firePressed = true` if transitioning to on. | `void` |
| `__game.switchWeapon(dir)` | Sets `ctx.input.switchNext = true` (dir is ignored; cycles forward). | `void` |
| `__game.selectSlot(n)` | Sets `ctx.input.weaponSlot = n` (1-5). | `void` |
| `__game.spawnEnemy(type, x, y, dir)` | Calls `enemies.spawn(ctx, type, x, y, dir)`. | `{id, x, y, type, alive}` |
| `__game.spawnProjectile(weaponId, x, y, vx, vy)` | Pulls from projectile pool and configures. | `{id, x, y, alive}` |
| `__game.skipToStage(w, s)` | Calls `level.load(ctx, w, s)`, resets player, sets state to `play`. | `{world, stage, spawnX, spawnY}` |
| `__game.setField(path, value)` | Sets `ctx` field at dotted path, e.g. `"player.hp"`, `"progression.score"`. | `void` |
| `__game.getFrameCount()` | Returns `ctx.frame`. | `number` |
| `__game.getDrawCalls()` | Returns the number of canvas draw ops from the last draw. | `number` |
| `__game.getStateHash()` | Returns a 32-bit hash of `getState()` JSON. For determinism checks. | `number` |

**Determinism guarantee:** Given the same `seed(n)` and the same sequence of `__game.*` calls, `getState()` returns byte-identical data every time. No call reads wall-clock time or `Math.random()`.

---

# 5. TESTS

All tests drive the game **exclusively** through `window.__game`. Numbered in execution order.

### T1 – Title → Play
```
__game.seed(42)
__game.start()
state = __game.getState()
```
Assert: `state.state === 'play'`, `state.level.world === 1`, `state.level.stage === 1`, `state.player.x === state.level.spawnX`, `state.player.y === state.level.spawnY`.

### T2 – Fixed-timestep movement (right)
```
__game.seed(42); __game.start()
__game.move(1)
__game.step(1/60, 60)   // 1 second of rightward movement
p = __game.getState().player
```
Assert: `p.x > <player-start-x> + <player-speed> * 0.9` (within 10 % tolerance for acceleration ramp), `p.onGround === true`, `p.facing === 1`.

### T3 – Jump physics
```
__game.seed(42); __game.start()
__game.jump()
__game.step(1/60, 1)
p = __game.getState().player
```
Assert: `p.vy > 0`, `p.onGround === false`, `p.state === 'jump'`.

### T4 – Crouch changes hitbox
```
__game.seed(42); __game.start()
h0 = __game.getState().player.h
__game.crouch(true)
__game.step(1/60, 1)
h1 = __game.getState().player.h
```
Assert: `h1 < h0`, `__game.getState().player.crouching === true`.

### T5 – Fire weapon (gun 1)
```
__game.seed(42); __game.start()
__game.selectSlot(1)
__game.fire(true)
__game.step(1/60, 1)
pr = __game.getState().projectiles.filter(p => p.alive)
```
Assert: `pr.length >= 1`, `pr[0].x > __game.getState().player.x` (fired rightward), `pr[0].vx > 0`.

### T6 – All 4+ weapon types fire
```
__game.seed(42); __game.start()
for slot in [1,2,3,4]:
    __game.selectSlot(slot)
    __game.fire(true)
    __game.step(1/60, 1)
    count += alive projectiles
```
Assert: after 4 iterations, at least 4 distinct `weaponId` values appear across all alive projectiles.

### T7 – Weapon switch
```
__game.seed(42); __game.start()
w0 = __game.getState().player.weaponIndex
__game.switchWeapon(1)
__game.step(1/60, 1)
w1 = __game.getState().player.weaponIndex
```
Assert: `w1 !== w0`.

### T8 – Enemy spawn & existence
```
__game.seed(42); __game.start()
e = __game.spawnEnemy('grunt', 300, 0, -1)
__game.step(1/60, 1)
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length >= 1`, `en[0].type === 'grunt'`, `en[0].x === 300`.

### T9 – Projectile kills enemy
```
__game.seed(42); __game.start()
e = __game.spawnEnemy('grunt', 200, 0, -1)
__game.fire(true)
__game.step(1/60, 120)  // 2 seconds – projectile should reach enemy
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length === 0` (or `en[0].hp <= 0` before despawn), `__game.getState().progression.score > 0`.

### T10 – Player takes damage
```
__game.seed(42); __game.start()
hp0 = __game.getState().player.hp
__game.spawnEnemy('grunt', 5, 0, 1)  // enemy right at player
__game.step(1/60, 30)
hp1 = __game.getState().player.hp
```
Assert: `hp1 < hp0`, `__game.getState().player.state === 'hurt'`.

### T11 – Stage clear → advance
```
__game.seed(42); __game.start()
// teleport player to exit
__game.setField('player.x', __game.getState().level.exitX)
__game.setField('player.y', __game.getState().level.exitY)
__game.step(1/60, 10)
s = __game.getState()
```
Assert: `s.level.stage === 2`, `s.level.world === 1`, `s.progression.stagesCleared` contains `"1-1"`.

### T12 – World progression (2 worlds, 5 stages each)
```
__game.seed(42); __game.start()
for w in [1,2]:
    for s in [1..5]:
        __game.skipToStage(w, s)
        __game.setField('player.x', __game.getState().level.exitX)
        __game.setField('player.y', __game.getState().level.exitY)
        __game.step(1/60, 10)
final = __game.getState()
```
Assert: `final.progression.stagesCleared.length === 10`, `final.state === 'world-clear'` (or `'play'` if looping back).

### T13 – Restart preserves stage, resets player
```
__game.seed(42); __game.start()
__game.move(1); __game.step(1/60, 60)
__game.setField('state', 'play')  // ensure not in transition
// trigger restart via input
__game.setField('input.restart', true)
__game.step(1/60, 1)
s = __game.getState()
```
Assert: `s.level.stage === 1`, `s.player.x === s.level.spawnX`, `s.player.hp === <PLAYER_MAX_HP>`.

### T14 – Pause / resume
```
__game.seed(42); __game.start()
__game.setField('input.pause', true)
__game.step(1/60, 1)
s1 = __game.getState()
f1 = s1.frame
__game.step(1/60, 10)
s2 = __game.getState()
```
Assert: `s1.state === 'pause'`, `s2.frame === f1` (no ticks ran while paused).

### T15 – Draw-call budget
```
__game.seed(42); __game.start()
__game.skipToStage(1, 1)
__game.step(1/60, 30)
dc = __game.getDrawCalls()
```
Assert: `dc <= 600`.

### T16 – Entity pool cap respected
```
__game.seed(42); __game.start()
for i in 0..65:
    __game.spawnEnemy('grunt', 50 + i*10, 0, -1)
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length <= 40` (pool cap enforced).

### T17 – Determinism
```
__game.seed(1337)
__game.start()
__game.move(1); __game.jump(); __game.fire(true)
__game.step(1/60, 300)
h1 = __game.getStateHash()

__game.seed(1337)
__game.start()
__game.move(1); __game.jump(); __game.fire(true)
__game.step(1/60, 300)
h2 = __game.getStateHash()
```
Assert: `h1 === h2`.

### T18 – Same seed, different call order → different state (sanity)
```
__game.seed(1337); __game.start(); __game.fire(true); __game.step(1/60,1); __game.jump(); __game.step(1/60,1)
hA = __game.getStateHash()
__game.seed(1337); __game.start(); __game.jump(); __game.step(1/60,1); __game.fire(true); __game.step(1/60,1)
hB = __game.getStateHash()
```
Assert: `hA !== hB` (confirms the hash is sensitive to order).

---

# 6. BUILD ORDER

| # | Milestone | Modules added / completed | Proof check |
|---|---|---|---|
| **M1** | Page opens, draws title, enters play | `game.js` (state machine, rAF loop), `canvas` setup, `ui.js` (title + HUD skeleton), `debug.js` (`start`, `step`, `getState`, `seed`) | **T1** passes. |
| **M2** | Player moves, jumps, crouches on a flat tile floor | `input.js`, `physics.js`, `player.js`, `level.js` (single flat strip) | **T2, T3, T4** pass. |
| **M3** | Camera follows player; full tile map renders | `camera.js`, `level.js` (full stage 1-1 tiles), `ui.js` (HUD) | **T15** passes (draw-call budget on a real level). |
| **M4** | 4 gun types fire projectiles; weapon switching | `weapons.js` (definitions + projectile pool), `player.js` (shoot state) | **T5, T6, T7** pass. |
| **M5** | Enemies patrol, take damage, die; score | `enemies.js`, `particles.js`, `audio.js` | **T8, T9, T10** pass. |
| **M6** | Stage-clear trigger, world/stage progression, restart, pause | `progression.js`, `game.js` (transition states), `ui.js` (overlays) | **T11, T12, T13, T14** pass. |
| **M7** | All 10 stages authored; touch controls; full audio | `level.js` (all data), `input.js` (touch), `audio.js` (music + SFX) | **T16** (pool cap under load), **T17, T18** (determinism). |
| **M8** | Polish: parallax, particle variety, difficulty ramp per world, game-over screen | `particles.js`, `ui.js`, `enemies.js` (per-world variants) | Full regression: **T1–T18** all pass. |

---

# 7. RISKS

| # | Risk | Why it bites *this* game | Rule that prevents it |
|---|---|---|---|
| **R1** | **Y-axis sign flip between logic and render.** Game logic uses Y-up; canvas is Y-down. If the `ctx.scale(1,-1)` translate is applied in the wrong order or forgotten for one draw path (e.g. HUD), the player appears to fall upward or the HUD is mirrored. | A platformer's entire feel depends on gravity direction; a single missed transform makes the game unplayable and is hard to spot in a screenshot. | **Rule:** The renderer's `draw()` function is the *only* place that touches `ctx2d`. It calls `applyWorldTransform(c2d)` (translate + `scale(1,-1)`) before any world-space drawing and `resetTransform()` before HUD/title drawing. No other module ever receives `ctx2d`. A unit test asserts that after `applyWorldTransform`, a point at game-logic `(0, 100)` maps to canvas `(0, -100)` relative to the camera. |
| **R2** | **Timing race between the fixed-tick accumulator and variable rAF.** If `requestAnimationFrame` fires with a large delta (tab was backgrounded, GC pause), the loop either runs hundreds of catch-up ticks (stutter) or clamps and silently skips time (desync between `ctx.time` and real seconds, breaking jump apexes and enemy timers). | Jump height, projectile travel, and enemy patrol timing are all expressed in `DT`-units; a missed or extra tick shifts the player's landing by a tile. | **Rule:** The accumulator clamps to a maximum of **5** catch-up ticks per rAF callback. If more than 5 ticks are owed, the excess is **discarded** (not deferred) and `ctx.time` still advances by the full real delta so timers don't drift. `__game.step(dt, n)` bypasses the accumulator entirely, guaranteeing tests are immune to rAF jitter. |
| **R3** | **Per-frame allocation pressure from projectiles / particles / enemy updates causes GC hitches that blow the 16.6 ms budget.** A naive `for…of` over a growing array or creating `{}` literals inside the update loop allocates every tick; at 60 fps with 120 projectiles + 512 particles + 40 enemies that is thousands of small objects per second. | The game is CPU-bound on a single thread; one GC pause > 16 ms drops a frame, which cascades into a physics step that's too large, which mis-resolves a collision, which the player perceives as "falling through a platform." | **Rule:** All three pools (enemies, projectiles, particles) are **pre-allocated fixed-size arrays of plain objects** created once in `init()`. Update loops mutate fields in place; "death" sets `alive = false`; "spawn" scans for the first `alive === false` slot. **No `new`, no `{}`, no `.push()`, no `.splice()` inside any `update()` function.** The `getState()` debug function clones data into a fresh object (acceptable because it is never called inside the game loop). A test asserts `getDrawCalls()` and heap size after 3 000 ticks to confirm zero net allocation. |