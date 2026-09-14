# GRIDFALL — BUILD SPEC (Integrator's Merge)

# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Side-scrolling platformer | §4 Movement, §3 Visual Spec |
| Shooter with ≥ 4 different gun types | §4 Combat + Weapon Roster (4 weapons) |
| Character can jump | §4 Movement (jump, double-jump) |
| Character can move left or right | §4 Movement (Left/Right rules) |
| Character can crouch | §4 Movement (Crouch rule), §5 Characters |
| Worlds and stages (Mario-style progression) | §4 StageFlow, §4 Progression (2 worlds × 5 stages) |
| 2 worlds, 5 stages each (10 stages total) | §4 LevelGenerator, §4 Progression |
| Do not copy Mario | Entire spec is original IP (GRIDFALL, Helix Spire, data-runner theme) |
| Story progression model | §4 Progression (unlock order, boss gates, world advance) |
| Added: seeded level generation for replayability | §4 LevelGenerator |
| Added: per-stage scoring (stars, time, coins) | §4 Scoring |
| Added: regenerating shield layer on top of HP | §4 DamageAndDeath |
| Added: double-jump | §4 Movement |
| Added: NG+ difficulty mode | §4 Progression (T3) |
| Added: touch controls | §1.2 Controls, §8 Debug API (T3) |

## 0.2 Decisions

| Topic | Gameplay said | Visual said | Engineering said | Ruling |
|---|---|---|---|---|
| Y-axis convention | Y-down (gravity +1400, jump vy = −480) | Y-up implied (units, ground at bottom) | Y-up positive, gravity −Y, `ctx.scale(1,−1)` for render | **Engineering's Y-up.** Jump vy = +480, gravity = −1400. Renderer flips for canvas. One clause: the render pipeline must be the single transform authority. |
| Canvas / viewport size | Implied 960×540 (from visual's "base resolution") | 960×540 base | 1280×720 CSS px | **1280×720.** Engineering's value wins; all px numbers in this spec are at 1280×720. |
| Level width (stages 1–4) | 3200 px | 240 units (= 240 px at 1 u = 1 px) | Max 6400 px | **3200 px** (gameplay). Visual's 240-unit figure was a different scale assumption; discarded. |
| Level width (boss stage 5) | 1600 px | 240 units | — | **1600 px** (gameplay). |
| Level height | 560 px, floor at y = 480 | 24 units tall | Max 2560 px (80 tiles × 32) | **560 px**, floor at y = 480. |
| Tile size | Implied 32 px (platform h: 16 or 32) | 1 unit = 1 px, tiles 1×1 | `<TILE_SIZE>` placeholder | **32 px.** Fills engineering's placeholder. |
| Player hitbox (standing) | 48 px tall (crouch 28) | 3 units tall, 2 wide | `<PLAYER_W>`, `<PLAYER_H>` placeholders | **w = 32, h = 48** (standing); **h = 28** crouching. Fills placeholders. |
| Player max HP | 100 | 3 hearts | `<PLAYER_MAX_HP>` placeholder | **100 HP** (numeric bar, not hearts). Hearts concept dropped; HP bar per gameplay. |
| Player lives | 3 | — | `<PLAYER_LIVES>` placeholder | **3.** |
| Weapon count / IDs | 4: pulse_rifle, scatter_cannon, rail_lance, arc_burst | 4: Rivet Driver, Scatter Cannon, Arc Welder, Mortar Launcher | ≥ 4, 5 slots | **4 weapons** (gameplay IDs canonical). Display names: "Rivet Driver", "Scatter Cannon", "Rail Lance", "Arc Burst". Engineering's 5th slot dropped. |
| Scatter pellets | 6 | 5 | — | **6** (gameplay). |
| Scatter spread | 18° | 30° | — | **18°** (gameplay). |
| Arc Burst mechanic | Projectile with 90 px chain radius | Continuous beam (Arc Welder) | — | **Gameplay's chain projectile.** Beam concept dropped; visual's coil-ring gun art kept for the model. |
| Rail Lance mechanic | Piercing fast projectile (1400 px/s, 3 pierce) | Mortar Launcher (parabolic, AoE) | — | **Gameplay's piercing projectile.** Mortar concept dropped; visual's long-barrel art adapted. |
| Boss names | "Custodian", "Architect" | "Press Golem", "Reservoir Warden" | — | **Visual's names** (Press Golem, Reservoir Warden) with gameplay's attack tables. |
| Enemy art names | drone, sentry, runner, mine, shieldbot | Rust Crawler, Dripling | — | **Gameplay types canonical.** Display: runner → "Rust Crawler", drone → "Dripling". Sentry/mine/shieldbot get art from visual's general style. |
| World names | "Helix Spire floors" | "The Rustbelt" (W1), "The Undercity" (W2) | — | **Visual's names** as stage subtitles; "Helix Spire" is the game's fiction. |
| Level generation | Seeded procedural generator with verifier | Hand-placed fixed layouts | — | **Seeded generator** (gameplay). Visual's "hand-placed" overridden; parallax layers are fixed per world. |
| Stage clear trigger | Walk into extraction pad | Collect Stage Key → exit gate opens | — | **Walk into extraction pad** (gameplay). No separate key pickup; visual's "Stage Key" dropped. |
| Screen shake magnitude | 4 px, 0.15 s | 0.3 units, 0.2 s | — | **4 px / 0.15 s** for hits; **8 px / 0.3 s** for boss slams (scaled up). |
| Pause key | Escape | — | Esc / P | **Escape or P** (engineering's broader binding). |
| Fire key | J / mouse click | — | J / Z / Enter | **J / Z / mouse click** (Enter reserved for menus). |
| Conveyor platforms | Not mentioned | Visual recipe (chevrons scroll) | — | **T2 visual-only decoration** on some solid platforms; no gameplay effect. |
| Post-effects (vignette, grain, chromatic aberration) | Not mentioned | Specified | — | **T3 polish.** Not in T1. |
| Parallax layers | Not mentioned | 4 layers specified | bgParallax field exists | **T2.** 2 layers in T1, all 4 by T2. |
| Touch controls | Mentioned in controls table | — | Specified | **T3.** |
| NG+ mode | Mentioned | — | — | **T4.** |
| Game name | "GRIDFALL" | Implicit | — | **GRIDFALL.** |

## 0.3 Tiers

**T1 (must ship):** Movement, Combat (4 weapons + projectiles), DamageAndDeath, EnemyAI (drone + runner only), LevelGenerator (stages 1-1 through 1-2), StageFlow (linear advance), HUD, Title/Play/GameOver screens, Camera, fixed-step loop, seeded PRNG, keyboard controls.

**T2:** All 5 enemy types + mine + shieldbot, all hazards (spike, laser_gate, acid_pool), crumble platforms, one-way platforms, checkpoints, all 10 stages, BossAI (Press Golem), PickupAndAmmo (all types), Scoring (stars), World Select screen, Stage Clear screen, 4 parallax layers, weapon unlock crates, conveyor visual decoration.

**T3:** BossAI (Reservoir Warden), World 2 full content, touch controls, full audio (music + all SFX), post-effects (vignette, grain, chromatic aberration, screen desaturation on death), stage intro banners, exit-gate shutter animation.

**T4:** NG+ mode (×1.4 HP, ×1.3 density, par_time −20%), full particle variety (confetti, steam, dust, motes), neon-sign flicker, bioluminescent moss, checkpoint totem ring animation, score popups, low-health red-edge tint, weapon-switch muzzle flash.

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Item | Rule |
|---|---|
| 1 unit | 1 logical pixel. Canvas is 1280 × 720 CSS px; internal resolution matches at devicePixelRatio = 1. |
| Game-logic axes | **X → right positive. Y → up positive.** Ground plane at y = 0. Gravity pulls in −Y (−1400 px/s²). |
| Render axes | Canvas default: X right, Y down. Renderer applies `ctx.scale(1, −1)` after translating to camera offset. Only the renderer touches `ctx2d`. |
| Origin (world) | Bottom-left of level tile grid. `worldOrigin = {x: 0, y: 0}`. |
| Tile size | **32 px.** |
| Level dimensions | Width: 3200 px (stages 1–4) or 1600 px (boss stage 5). Height: 560 px. Floor surface at y = 480. |
| Camera viewport | 1280 × 720 px. `camera.x` = left edge in world coords; `camera.y` = bottom edge. Clamped to level bounds. |
| Fixed timestep | DT = 1/60 ≈ 0.016666667 s. |
| Frame budget | ≤ 16.6 ms all ticks + one draw. |

## 1.2 Important conventions

**Fixed-step loop and tick order (every tick, in this exact sequence):**
1. `input.update()` — latch new key/touch events into current frame's input state.
2. `physics.update(DT)` — integrate velocities, resolve tile collisions, resolve entity–entity collisions.
3. `player.update(DT)` — state machine (idle/run/jump/crouch/shoot/hurt/dead).
4. `weapons.update(DT)` — fire cooldowns, spawn/advance/despawn projectiles.
5. `enemies.update(DT)` — AI state machines, patrol, chase, die.
6. `particles.update(DT)` — advance lifetimes, recycle dead.
7. `camera.update(DT)` — dead-zone follow, clamp to level bounds.
8. `progression.update(DT)` — check stage-clear conditions, trigger transitions.
9. `audio.update(DT)` — drain sound queue (reactive only; never mutates game state).

After all ticks for the frame: `renderer.draw()` called exactly once.

**Accumulator rule:** `requestAnimationFrame` accumulates real elapsed time, runs zero or more fixed ticks, draws once. Maximum **5** catch-up ticks per rAF callback; excess discarded. `ctx.time` still advances by full real delta.

**Random source:** One seeded PRNG: `mulberry32(seed)`, exposed as `ctx.rng()`, returns float in [0, 1). No `Math.random()`, `crypto.getRandomValues()`, or `Date.now()` in game logic. Renderer and audio may use `Math.random()` for cosmetic jitter never read back into state.

**Determinism guarantee:** Given same `seed(n)` and same sequence of `__game.*` calls, `getState()` returns byte-identical data.

**Controls table (keyboard):**

| Key | Action |
|---|---|
| A / ← | Move left (held) |
| D / → | Move right (held) |
| W / ↑ / Space | Jump (edge-triggered, one press = one jump) |
| S / ↓ | Crouch (held) |
| J / Z / mouse click | Fire (held = auto-repeat for auto; edge for semi) |
| K / X | Cycle weapon forward |
| 1 / 2 / 3 / 4 | Select weapon slot directly |
| Escape / P | Pause / Resume |
| R | Restart current stage (while paused) |
| Enter | Confirm in menus |

**Touch controls (T3):** Left-half swipe/hold = move (analog by distance from centre). Right-half top = jump (tap). Right-half bottom = fire (hold). Right-half middle = crouch (hold). Two-finger tap = switch weapon. Touch synthesises into the same `ctx.input` object; no game code branches on device.

---

# 2. CONTRACTS

## 2.1 Module layout

| Module | Responsibility |
|---|---|
| `game.js` | Boot, top-level state machine, owns rAF loop, calls every module in tick order. |
| `input.js` | Reads keydown/keyup/touch*, writes `ctx.input`. Normalises keyboard + touch. |
| `physics.js` | AABB tile collision, entity-vs-entity, gravity integration, ground detection. Pure geometry. |
| `player.js` | Player entity: state machine, HP/shield, crouch, jump arc, invuln, respawn. |
| `weapons.js` | 4 weapon definitions, fire logic, projectile pool, damage application, chain logic. |
| `enemies.js` | 5 enemy definitions + 2 boss definitions, per-type AI tick, spawn, death, drops. |
| `level.js` | Seeded generator, tile-map array, `isSolid`, `isHazard`, `tileAt`, entity spawn lists, verifier. |
| `camera.js` | Viewport rect, dead-zone follow, clamp to level bounds. |
| `particles.js` | Ring-buffer pool; spawn, update, query-alive. |
| `audio.js` | Web Audio API: oscillator/noise buffers for SFX, simple music sequencer. Queue consumer. |
| `progression.js` | World/stage index, unlock table, score, stage-clear/game-over conditions, NG+. |
| `ui.js` | HUD, title, pause, stage-clear, world-select, game-over, game-complete overlays. |
| `debug.js` | Installs `window.__game`. Imported only in debug builds. |

## 2.2 Global context

```js
const ctx = {
  // environment
  canvas: null,
  ctx2d: null,
  seed: 0,
  rng: null,
  dt: 0.016666667,
  time: 0,
  frame: 0,
  running: true,
  state: 'title',  // 'title'|'play'|'pause'|'stage-clear'|'world-clear'|'game-over'|'game-complete'

  // input
  input: {
    moveDir: 0,
    jumpPressed: false,
    jumpHeld: false,
    crouchHeld: false,
    firePressed: false,
    fireHeld: false,
    switchNext: false,
    weaponSlot: 0,
    pause: false,
    restart: false,
    confirm: false,
    back: false,
    touch: null,
  },

  // player
  player: {
    x: 0, y: 0,
    vx: 0, vy: 0,
    w: 32, h: 48,
    facing: 1,
    onGround: false,
    crouching: false,
    state: 'idle',
    hp: 100, maxHp: 100,
    shield: 50, maxShield: 50,
    shieldRegenDelay: 0,
    lives: 3,
    invulnTimer: 0,
    jumpCount: 0,
    coyoteTimer: 0,
    jumpBufferTimer: 0,
    weaponIndex: 0,
    weapons: [1, 0, 0, 0],   // 1 = owned, 0 = not
    ammo: [120, 24, 10, 40],
    shootCooldown: 0,
    recoilLockTimer: 0,
    respawnTimer: 0,
    checkpointX: 0, checkpointY: 0,
  },

  // weapons / projectiles
  projectiles: [],
  projectilePoolSize: 256,

  // enemies
  enemies: [],
  enemyPoolSize: 64,

  // boss (null when not in boss stage)
  boss: null,

  // particles
  particles: [],
  particlePoolSize: 1024,

  // pickups (active in current stage)
  pickups: [],

  // level
  level: {
    world: 1,
    stage: 1,
    tiles: null,
    width: 100,    // tiles (3200 / 32)
    height: 17,    // tiles (560 / 32, rounded up)
    spawnX: 80, spawnY: 480,
    exitX: 3120, exitY: 480,
    hazards: null,
    entitySpawns: [],
    pickupSpawns: [],
    platforms: [],
    crumbleTimers: [],
    bgParallax: 0.3,
    hasCheckpoint: false,
    checkpointX: 1600, checkpointY: 480,
  },

  // camera
  camera: { x: 0, y: 0, w: 1280, h: 720, lookAhead: 120, deadZoneY: 80 },

  // progression
  progression: {
    score: 0,
    totalStages: 10,
    unlockedWorld: 1,
    unlockedStage: 1,
    stagesCleared: [],
    ngPlus: false,
    difficultyScale: 1.0,
  },

  // scoreboard (current stage)
  scoreboard: {
    clearTime: 0,
    enemiesKilled: 0,
    enemiesTotal: 0,
    coinsCollected: 0,
    coinsTotal: 0,
    stars: 0,
    parTime: 0,
  },

  // audio queue
  audioQueue: [],

  // screen shake
  shake: { intensity: 0, duration: 0, timer: 0 },
};
```

## 2.3 Module specifics

### `game.js`
| Export | Purpose |
|---|---|
| `boot(canvas, seed)` | Creates `ctx`, calls every module's `init`, starts rAF loop. |
| `setState(state)` | Transitions top-level state machine; resets `time`, `frame`, re-seeds `rng` per stage. |
| `loop(timestamp)` | rAF callback: accumulate, run ticks (max 5), draw once. |

### `input.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Registers keydown/keyup/touch listeners on window/canvas. |
| `update(ctx, dt)` | Latches edge-triggered flags, clears them after tick. |
| `reset(ctx)` | Clears all input flags (called on pause, stage change). |

### `physics.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Pre-computes tile lookup tables. |
| `update(ctx, dt)` | Integrates all entities, resolves tile + entity collisions. |
| `isSolid(ctx, tx, ty)` | Bool: tile blocks movement. |
| `isHazard(ctx, tx, ty)` | Bool: tile damages on contact. |
| `tileAt(ctx, wx, wy)` | Tile type at world pixel position. |
| `resolveAABB(a, b)` | Returns `{overlapX, overlapY, normalX, normalY}` or null. |
| `groundCheck(ctx, entity)` | Bool: entity bottom is on a solid surface. |

### `player.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Builds player record from `ctx.level.spawnX/Y`. |
| `update(ctx, dt)` | State machine: reads `ctx.input`, sets velocity, handles jump/crouch/fire. |
| `hurt(ctx, dmg)` | Applies damage (shield first, then hp), sets invuln, knockback, checks death. |
| `respawn(ctx)` | Resets player to checkpoint/spawn, decrements lives. |
| `getHitbox(ctx)` | Returns `{x, y, w, h}` reflecting crouch state. |

### `weapons.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Loads 4 weapon definitions. |
| `update(ctx, dt)` | Ticks cooldowns, advances/despawns projectiles, applies collisions, handles chain. |
| `fire(ctx, weaponId)` | Spawns projectile(s) from pool using weapon stats. |
| `getWeaponDef(id)` | Returns definition object. |
| `switchWeapon(ctx, dir)` | Advances `player.weaponIndex` through owned weapons. |
| `selectSlot(ctx, slot)` | Sets `player.weaponIndex = slot` if owned. |

### `enemies.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Loads enemy + boss definitions; populates pool from `ctx.level.entitySpawns`. |
| `update(ctx, dt)` | Runs each alive enemy's AI, applies gravity/collision, handles death & drops. |
| `spawn(ctx, type, x, y, dir)` | Pulls from pool, configures. |
| `kill(ctx, enemy)` | Sets alive=false, pushes audio, spawns particles, rolls drop via `ctx.rng()`. |
| `spawnBoss(ctx, id)` | Configures `ctx.boss` for the given boss id. |
| `updateBoss(ctx, dt)` | Boss AI tick, phase transitions, attack timers. |

### `level.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | — |
| `update(ctx, dt)` | Checks player overlap with exit zone → pushes stage-clear. Ticks crumble timers. Ticks laser-gate cycles. |
| `load(ctx, world, stage)` | Runs seeded generator, rebuilds tile arrays, spawn lists, resets time/frame. |
| `generate(ctx, seed, world, stage, difficultyScale)` | Full generation algorithm (see §4 LevelGenerator). |
| `verify(ctx)` | Runs all verifier checks; returns true or re-rolls. |
| `isSolid(ctx, tx, ty)` / `isHazard(ctx, tx, ty)` / `tileAt(ctx, wx, wy)` | Tile data accessors. |

### `camera.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Sets viewport size from canvas. |
| `update(ctx, dt)` | Dead-zone follow + look-ahead, clamp to `[0, levelW − vpW] × [0, levelH − vpH]`. |

### `particles.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Allocates ring buffer of 1024 structs. |
| `update(ctx, dt)` | Advances alive particles, recycles when life ≤ 0. |
| `spawn(ctx, x, y, vx, vy, life, type)` | Writes next ring-buffer slot. |
| `getAlive(ctx)` | Iterator over alive particles. |

### `audio.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Creates AudioContext, pre-builds oscillator/noise buffers. |
| `update(ctx, dt)` | Drains `ctx.audioQueue`, plays sounds. |
| `play(ctx, id)` | Queues a sound event. |

### `progression.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Sets totalStages, unlock table, par_times. |
| `update(ctx, dt)` | On stage-clear: records, advances, checks win. |
| `advance(ctx)` | Next stage; next world if stage > 5; game-complete if world > 2. |
| `restart(ctx)` | Resets current stage (keeps lives, score). |
| `restartWorld(ctx)` | Resets current world to stage 1, lives = 3, ammo reset. |
| `calcStars(ctx)` | Computes 1–3 stars for current stage. |

### `ui.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | — |
| `draw(ctx, c2d)` | Renders HUD, title, pause, overlays per `ctx.state`. |

### `debug.js`
See §8.

---

# 3. VISUAL SPEC

**The look:** 2D side-scrolling camera (horizontal follow, no rotation, fixed zoom at 1280×720). A neon-soaked post-industrial data-tower: a lone data-runner in a battered exo-suit blasts through skeletal server infrastructure. Palette is deep oxidized teal (#1A2E33) and rust-orange (#C45A2D) as ground truth, punctuated by electric cyan (#00E5FF) and hot magenta (#FF2D78) from gunfire, signage, and bioluminescence. Mood: "gritty Saturday-morning cartoon"—chunky readable shapes, bold 3-pixel black outlines, exaggerated squash-and-stretch on every impact. The player stands 48 px tall, 32 px wide.

**Lighting and atmosphere:** Very low ambient (#0F1B1F at 25%). Light is diegetic: sodium lamp posts (#FFB347, radius 8, static with 0.03 flicker), neon signs (#FF2D78/#00E5FF, radius 5, flicker 80% on / 20% random 0.1 s off), checkpoint orbs (#00E5FF, radius 6, pulse 4→6→4 over 2 s), muzzle flashes (#FFB347/#FF2D78/#00E5FF per gun, radius 4, 0.06 s), bioluminescent moss W2 (#00E5FF, radius 3, 4 s breathe), boss arena spotlight (#FFFFFF 60%, radius 12, static cone), exit-gate flood (#FFB347, radius 10, 0.8 s ramp). Background layers 1–2 darkened 40% vs foreground. W2 adds vertical fog band (#15292E, 30% alpha) at 60% height. Boss arenas drop ambient to 10%.

**The space:** Each stage is a horizontal corridor. World 1 "The Rustbelt": corrugated steel plates, broken concrete, smokestacks, hanging chains, conveyor machinery; rust-orange dominant; perpetual dusk (orange horizon glow in BG layer 1). World 2 "The Undercity": cracked tile, flooded shallow channels, dripping brick arches, subway tunnels, bioluminescent moss; teal dominant with magenta/cyan fungi pops; perpetual night (closed tunnel ceiling). Stage 5 of each world is a boss arena: W1 = hydraulic press room (ceiling at 20 tiles, floor is grate over boiling oil); W2 = drained reservoir with concentric ring platforms. Each stage number adds one more parallax layer and one more colour accent (stage 1: 2 layers/2 accents; stage 5: 4 layers/4 accents).

**Recipe table:**

| Name | Shapes & Size (px) | Colours (hex) | Count | Motion / Effect |
|---|---|---|---|---|
| Player – idle | Rounded rect body 32×48, circle head r=14 atop, 2 stub arms, 2 stub legs. 3px black outline. | Suit: #2C3E50. Visor: #00E5FF. Accents: #FF2D78. | 1 | 2-frame breathing bob (y ±2 px, 0.8 s cycle). |
| Player – crouch | Squashed rect 32×28, head tucks into shoulders. | Same | 1 | Static pose. |
| Player – run | Same body, 4-frame stride (y ±3 px bounce). | Same | 1 | Leg cycle; dust puffs (#8B7355, r=6, fade 0.3 s) at feet. |
| Player – jump | Body stretched 1.8× vertically, arms up. | Same | 1 | Squash→stretch→return. Trail: 3 ghost copies 40% alpha, 0.1 s apart. |
| Player – hurt | Tinted #FF2D78 at 70% opacity, 3-frame flash. | Flash: #FF2D78→white→back | 1 | 0.1 s per frame, knockback wobble (x ±3 px). |
| Player – death | 8 triangle shards (r=8 each) fly outward. | #2C3E50 with #FF2D78 edges | 1 | Spin and fade over 1.2 s. |
| Gun – Rivet Driver | Rect barrel 24×8, circle muzzle r=5. | Body: #5C6B73. Muzzle ring: #FFB347. | 1 | Recoil: barrel x-offset −5 px for 0.08 s. |
| Rivet – projectile | Circle r=5, trailing line 16 px. | Core: #FFB347. Trail: #FFB347→transparent. | ≤ 12 on-screen | Linear. Fades at 700 px range. |
| Gun – Scatter Cannon | Wide rect barrel 20×14, 3 muzzle ports r=4 each. | Body: #8B4513. Ports: #FF2D78. | 1 | Muzzle flash: 3 radial lines 24 px, #FF2D78, 0.06 s. |
| Scatter – projectile (×6) | Tiny circles r=3, spread 18° cone. | #FF2D78 | 6 per shot | Linear, fade at 234 px range (0.45 s × 520). |
| Gun – Rail Lance | Long thin rect barrel 40×6, glowing coil rings ×3. | Body: #1A2E33. Coils: #00E5FF. | 1 | Launch: barrel extends 0.1 s, recoil lockout visual. |
| Rail – projectile | Elongated rect 24×4, bright core. | #00E5FF core, #FF2D78 edge glow | 1 | Linear at 1400 px/s, pierces 3. |
| Gun – Arc Burst | Cylindrical barrel 16×12, glowing coil rings ×3. | Body: #1A2E33. Coils: #00E5FF. | 1 | Continuous coil glow while firing. |
| Arc – projectile | Circle r=6, crackling edge. | #00E5FF with #FF2D78 sparks | 1 | Linear at 480 px/s. On hit: chain arc to nearest enemy within 90 px. |
| Arc – chain arc | Wavy line between two points, sine amp 4 px. | #00E5FF→#FF2D78 gradient | 1 per chain | 0.15 s flash. |
| Enemy – Rust Crawler (runner) | Low rect 32×20, 4 stub legs, single red eye r=4. | Body: #C45A2D. Eye: #FF2D78. | 3–6 per stage | 4-frame leg crawl, y ±2 px bob. |
| Enemy – Dripling (drone) | Teardrop body 16×24, 2 wing arcs r=12. | Body: #00E5FF. Wings: #1A2E33. Eye: #FF2D78. | 2–5 per stage | Sine hover (y ±12 px, 1.0 s). Wings 4-frame flap. |
| Enemy – Sentry | Rect turret base 24×32, rotating barrel 16×6. | Body: #3D3D3D. Barrel: #FFB347. Eye: #FF2D78. | 2–4 per stage | Barrel rotates to face player. |
| Enemy – Mine | Octagon r=12, blinking centre. | Body: #8B7355. Blink: #FF2D78. | 1–3 per stage | Static. Fuse blink 0.6 s. |
| Enemy – Shieldbot | Rect 32×40 with front shield plate 8×40. | Body: #2C3E50. Shield: #FFB347. Eye: #FF2D78. | 1–2 per stage (W2) | Shuffles. Shield blocks frontal shots. |
| Boss – Press Golem | Massive rect 96×128, 2 piston arms 48×16, visor slit. | Body: #3D3D3D. Pistons: #C45A2D. Visor: #FFB347. | 1 | Idle: steam puffs from joints every 1.5 s, body bobs y ±3 px. |
| Boss – Reservoir Warden | Octagonal core r=48, 4 rotating tentacle arms (length 80, r=6). | Core: #1A2E33. Arms: #00E5FF. Eye: #FF2D78. | 1 | Arms rotate 15°/s. Charge: core pulses magenta. |
| Pickup – Health Cell | Hexagon r=10, cross icon inside. | Shell: #00E5FF. Cross: #FFFFFF. | 1–2 per stage | Float y ±4 px sine, 1 s. Glow halo r=24, 40% alpha. |
| Pickup – Shield Cell | Hexagon r=10, shield icon. | Shell: #00E5FF. Icon: #FFB347. | 1 per stage | Same float. |
| Pickup – Ammo Crate | Rect 16×16, lid at 30°, bullet icon. | Body: #FFB347. Lid: #8B7355. | 2 per stage | Static; wobble 2 px when player within 64 px. |
| Pickup – Coin | Circle r=6, spinning. | #FFB347 with #FF2D78 inner glow | 6–10 per stage | Spin 180°/s, bob 3 px. |
| Platform – Solid | Rect, variable width × 32. Top surface 5 px lighter strip. | W1: #5C6B73 top #8B7355. W2: #1A2E33 top #2C4A52. | Many | Static. |
| Platform – One-way | Thin rect variable width × 16, dashed underside. | Same palette, dashed #FFB347 underside. | Many | Static. |
| Platform – Crumble | Same as solid, 4 crack lines. | #8B7355 with #C45A2D cracks | 1–3 per stage | Static until touched; 0.4 s shake → 6 shard pieces fall. |
| Platform – Conveyor | Rect with 6 directional chevrons scrolling. | Body: #3D3D3D. Chevrons: #FFB347. | 1–2 per stage | Chevrons scroll x (visual only, no speed effect). T2. |
| Hazard – Spikes | Row of triangles base 16 height 24. | #8B7355 with #FF2D78 tips | Clusters of 4–8 | Static. |
| Hazard – Laser Gate | Vertical rect 4×32, glowing. | #FF2D78 core, #00E5FF edge | 1 per stage | On 1.0 s / off 1.0 s. Blink warning 0.2 s before on. |
| Hazard – Acid Pool | Rect pool in gap, wavy top edge. | #00FF88 50% alpha, white sparks ×3 r=4 | 1 per gap (W2) | Wave sine 2 px amp; sparks blink 0.2 s random. |
| BG Layer 1 – Far skyline | Silhouette rects/triangles, parallax 0.2×. | W1: #0F1B1F. W2: #0A1618. | Full-width | Static (camera parallax only). |
| BG Layer 2 – Mid structures | Pipes, arches, smokestacks, parallax 0.5×. | W1: #1A2E33. W2: #15292E. | Full-width | Parallax scroll. |
| BG Layer 3 – Near detail | Dripping chains, fungi, broken signs, parallax 0.8×. | W1: #2C3E50. W2: #1E3A40. | Full-width | Parallax; drips fall (0.3 s, 128 px drop). T2. |
| BG Layer 4 – Foreground fog | Horizontal gradient band, bottom 96 px. | #1A2E33 20% alpha | Full-width | Static. T3. |
| Neon Sign (decor) | Rect frame 48×24, text shape inside. | Frame: #2C3E50. Text: #FF2D78 or #00E5FF. | 2–4 per stage | Flicker 80% on / 20% random 0.1 s off. Tiny y jitter 1 px. T2. |
| Exit Gate / Extraction Pad | Rect 64×96, shutter lines ×8, stencil number. | Door: #3D3D3D. Rim: #FF2D78. Number: #FFB347. | 1 per stage | Closed: static. Opening: shutter slides up 0.8 s, light floods (#FFB347 radial). |
| Checkpoint Totem | Pillar 16×64, glowing orb r=10 atop. | Pillar: #2C3E50. Orb: #00E5FF. | 0–1 per stage | Inactive: orb dim #1A2E33. Active: orb bright, ring pulses outward r=10→40, 1.5 s loop. |
| Particle – Hit spark | 6 radial lines, length 12 px. | #FFFFFF→#FFB347 | 1 per hit | 0.1 s, scale 1→0. |
| Particle – Pickup sparkle | 8 tiny stars r=3, spiral outward. | #FFB347, #00E5FF | 1 per pickup | 0.4 s, fade. |
| Particle – Dust (land) | 3 ellipses 10×5 at feet. | #8B7355 50%→0% | 1 per landing | 0.25 s, drift outward. |
| Particle – Checkpoint activate | Expanding ring + 12 rising motes. | Ring: #00E5FF. Motes: #FFB347. | 1 per activation | Ring r=0→80 over 0.6 s, fade. Motes rise 64 px, 0.8 s. |
| Particle – Explosion | Expanding circle r=0→64 over 0.3 s, 8 triangle shards. | #FFB347→#FF2D78→transparent | 1 per detonation | Radial burst, smoke puffs ×6 (#666, r=10, drift up, 0.8 s). |
| UI – HUD bar | Rect 240×18 top-left. | BG: #0F1B1F 80% alpha. Border: #2C3E50. | 1 | Static. |
| UI – HP bar | Rect 120×8 inside HUD. | Full: #00E5FF→#FF2D78 (gradient by value). Empty: #3D3D3D. | 1 | Pulse scale 1.1 when < 25 HP, 0.5 s. |
| UI – Shield bar | Rect 120×6 below HP bar. | #00E5FF. Empty: #1A2E33. | 1 | Dimmed if 0. |
| UI – Ammo counter | Text block 80×18 bottom-left. | Text: #FFB347. BG: #0F1B1F 80%. | 1 | Flash white 0.1 s on pickup. |
| UI – Gun selector | 4 icons (20×20) bottom-left, active has ring. | Inactive: #5C6B73. Active ring: #00E5FF. | 1 set | Active icon pulses scale 1.0→1.15, 0.6 s. |
| UI – Stage banner (intro) | Full-screen rect, large stencil text. | BG: #0F1B1F. Text: #FFB347. Sub: #00E5FF. | 1 per stage | Slide in from top 0.6 s, hold 1.5 s, fade out 0.4 s. T3. |
| UI – Death screen | Dark overlay, "SCRAPPED" text, retry button. | Overlay: #0F1B1F 85%. Text: #FF2D78. Button: #FFB347. | 1 | Fade in 0.8 s. Button pulses 0.8 s. |
| UI – World map | 2×5 grid of stage nodes, connecting path line. | Path: #FFB347. Completed: #00E5FF. Locked: #3D3D3D. Current: #FF2D78 pulse. | 1 | Player icon walks along path. |

---

# 4. GAMEPLAY SPEC

**The game in one paragraph:** You are Kael, a freelance data-runner breaking into the seven floors of the Helix Spire, a mega-corporation's black-site server tower. Minute to minute you run, jump, crouch through low ducts, and shoot waves of security drones, sentries, and floor bosses with one of four weapons, managing a small ammo pool and a regenerating shield. Each world is a floor of the Spire; each stage is a sector you must clear left-to-right, reach the extraction pad at the far right, and survive. Stage 5 of every world is a boss arena. The game ends after you defeat the boss of World 2 and trigger the "Spire Purge" epilogue. Replayability comes from seeded level layouts that reshuffle platform and enemy placement between runs, a hidden per-stage score (time, enemies killed, coins), and a New Game+ mode. The game is 10 stages, roughly 20–25 minutes for a skilled run.

## Records

**Player** — Kael, the controllable character.

| Field | Unit | Start / Range |
|---|---|---|
| x, y | px | spawn per stage (default 80, 480) |
| vx, vy | px/s | 0, 0 |
| facing | −1 or +1 | +1 |
| state | enum | "idle"/"run"/"jump"/"fall"/"crouch"/"hurt"/"dead" |
| hp | points | 100 / max 100 |
| shield | points | 50 / max 50 |
| shieldRegenDelay | s | 0 (regen starts at 2.0) |
| crouchHeight | px | 28 (vs normal 48) |
| jumpCount | int | 0 (max 2) |
| invulnTimer | s | 0 (1.2 after hit) |
| coyoteTimer | s | 0 (0.08 after leaving ground) |
| jumpBufferTimer | s | 0 (0.10) |
| activeWeapon | index | 0 ("pulse_rifle") |

**Weapon Roster:**

| id | display name | damage | fireRate (shots/s) | spread (°) | projSpeed (px/s) | projLife (s) | pellets | pierce | chainRadius (px) | cooldown (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| pulse_rifle | Rivet Driver | 12 | 7.0 | 3 | 700 | 1.1 | 1 | 0 | 0 | 0 |
| scatter_cannon | Scatter Cannon | 9 | 1.5 | 18 | 520 | 0.45 | 6 | 0 | 0 | 0.65 |
| rail_lance | Rail Lance | 55 | 0.8 | 0 | 1400 | 2.0 | 1 | 3 | 0 | 1.1 |
| arc_burst | Arc Burst | 14 | 4.0 | 8 | 480 | 0.8 | 1 | 0 | 90 | 0 |

**AmmoPool** (per-weapon remaining shots):

| Weapon | Start | Max |
|---|---|---|
| pulse_rifle | 120 | 240 |
| scatter_cannon | 24 | 48 |
| rail_lance | 10 | 20 |
| arc_burst | 40 | 80 |

**Enemy Roster:**

| type | display | hp | vx (px/s) | damage | aggroRange (px) | attackCooldown (s) | behavior |
|---|---|---|---|---|---|---|---|
| drone | Dripling | 24 | 100 (floats, sine ±12 px) | 10 | 250 | 1.2 (fires 1 bullet, speed 180) | Hovers toward player, stops at 100 px |
| sentry | Sentry | 40 | 0 (stationary) | 15 (bullet, speed 300) | 320 | 1.0 | Rotates to face, fires aimed bullet |
| runner | Rust Crawler | 30 | 160 (ground charge) | 18 (contact) | 200 | 0.4 (melee lunge) | Patrols, sprints at player |
| mine | Mine | 20 | 0 (static) | 35 (AoE r=70 px) | 60 (proximity) | 0.6 fuse | Detonates on proximity |
| shieldbot | Shieldbot | 70 | 60 (shuffles) | 20 (contact) | 180 | 2.0 (melee slam) | Front shield blocks frontal damage; hit from behind/above |

**Boss Records:**

| id | display | hp | phases | phaseTransitionHP | hitbox (px) |
|---|---|---|---|---|---|
| floor1_guardian | Press Golem | 600 | 3 | 400 | 96×128 |
| floor2_overseer | Reservoir Warden | 1100 | 3 | 733 | 112×160 |

**Boss Attacks — Press Golem:**

| # | Trigger | Effect |
|---|---|---|
| 1 | Every 3.0 s | Slams ground, spawns 2 shockwave projectiles (speed 200, damage 20, travel along ground). |
| 2 | Every 5.0 s | Fires 5 aimed bullets in a fan (±25°, speed 280, damage 15). |
| 3 | Phase 2+ | Charges horizontally across arena (speed 300, damage 30, 1.5 s duration, 4 s cooldown). |
| 4 | Phase 3 | Adds 2 drone summons (200 px apart) every 6 s. |

**Boss Attacks — Reservoir Warden:**

| # | Trigger | Effect |
|---|---|---|
| 1 | Every 2.5 s | Sweeps laser line across arena (travel 400 px/s, damage 25, 0.8 s duration). |
| 2 | Every 4.0 s | Drops 3 ceiling mines (fall speed 180, proximity detonate r=50, damage 35). |
| 3 | Phase 2+ | Teleports to random x in arena, fires 8-bullet ring (speed 220, damage 12). |
| 4 | Phase 3 | Deploys 2 shieldbots, then 3× ground-slam sequence (damage 30 each, 0.6 s gap). |

**Pickup types:** "ammo_pulse"/"ammo_scatter"/"ammo_rail"/"ammo_arc"/"health"/"shield"/"coin". Amounts: ammo 20/6/3/10; health 25; shield 20; coin 1.

**Platform types:** "solid" (w 32–320, h 32), "one_way" (h 16), "crumble" (h 32, timer 1.5 s).

**Hazard types:** "spike" (20 dmg instant, 1.2 s invuln), "laser_gate" (25 dmg contact, period 2.0 s: on 1.0/off 1.0), "acid_pool" (10 dmg/s).

## Systems

### Movement (T1)

- **Left / Right** (A/←/D/→): set `vx` toward ±280 px/s, acceleration 1800 px/s². No key held: decelerate 2400 px/s² toward 0. Cap: |vx| ≤ 280 (crouching: ≤ 140).
- **Jump** (W/↑/Space): if `jumpCount < 2` AND state ≠ "crouch" → `vy = +480`; `jumpCount += 1`. If crouching → un-crouch first (1 frame, no jump this press).
- **Double-jump**: second press while airborne, `jumpCount == 1` → `vy = +400`; `jumpCount = 2`.
- **Crouch** (S/↓ held): if grounded → state = "crouch", h = 28, vx cap = 140. Release → h = 48, state = "idle". Crouching hitbox 28 px tall (passes under 32-px gaps).
- **Gravity**: every tick, `vy += −1400 * dt`. Terminal vy = −700 px/s.
- **Coyote time**: when player leaves ground without jumping, `coyoteTimer = 0.08`. Jump press within this window counts as grounded jump.
- **Jump buffering**: if jump pressed within 0.10 s before landing, fire jump on the landing tick.
- **One-way platforms**: land only if `vy < 0` (falling) AND player bottom was above platform top last frame. Press S while on one-way → `vy = −60`, disable that platform's collision for 0.2 s.
- **Crumble platforms**: player lands on type "crumble" → start `crumbleTimer`. At 1.5 s, platform removed; player falls.
- **Level bounds**: clamp `x` to [40, levelWidth − 40]. If `y < −100` (fell below floor) → instant death (pit).

### Combat (T1)

- **Fire** (J/Z/click): if `ammo[activeWeapon] > 0` AND `shootCooldown ≤ 0`:
  - Decrement ammo by 1.
  - Spawn `pelletsPerShot` projectile(s) at muzzle offset (facing × 24, y + 8 standing; y + 4 crouching).
  - Each projectile: velocity = projSpeed in facing direction ± random angle within spread (per pellet, via `ctx.rng()`).
  - Set `shootCooldown = 1 / fireRate`.
  - **Rail Lance**: while `shootCooldown > 0`, player `vx` locked (recoil lockout 0.15 s of the 1.1 s cooldown).
  - **Arc Burst**: on projectile hit, if chainRadius > 0, find nearest other enemy within 90 px → spawn secondary projectile toward it (damage × 0.6, one chain only).
- **Weapon Switch** (1/2/3/4, or K/X cycles): set `weaponIndex` if weapon owned. No cost, instant.
- **Projectile update**: position += velocity × dt. Remove when projLife elapsed or hits solid platform.
- **Projectile vs Enemy**: subtract damage from enemy.hp. If pierceCount > 0, decrement and continue; else remove projectile.
- **Rail Lance vs Boss**: pierce does NOT pierce boss (treated as 1 hit).

### DamageAndDeath (T1)

- Player takes damage: subtract from `shield` first, then `hp`. Set `invulnTimer = 1.2`, `shieldRegenDelay = 0`. If hp ≤ 0 → state = "dead", lives − 1, respawn at checkpoint after 1.5 s fade.
- Shield regen: if `shieldRegenDelay ≥ 2.0` AND shield < 50 → `shield += 12/s`. Reset delay to 0 on any hit.
- Contact damage: player hitbox overlaps enemy hitbox AND invulnTimer ≤ 0 → apply Enemy.damage.
- Hazard damage per Hazard record.
- Lives = 0 → "Game Over" screen → restart current world at Stage 1, full HP/shield, default ammo, lives = 3.

### EnemyAI (T1: drone + runner; T2: all 5)

- **Perception**: dist to player. If dist ≤ aggroRange → "chase". If chase AND dist > aggroRange × 1.4 → "patrol".
- **Patrol** (drone, runner): move at vx in patrolDir. Reverse after traveling patrolRange (80–200 px) from spawn or at platform edge.
- **Drone chase**: move toward player at vx with sine bob (amp 12, period 1.0 s). Stop at 100 px. Fire 1 bullet (speed 180, damage 10) every attackCooldown.
- **Sentry chase**: rotate barrel to face player. Fire aimed bullet (speed 300, damage 15) every attackCooldown.
- **Runner chase**: set vx toward player at 160. Contact → 18 damage, 0.4 s lunge anim, reset cooldown.
- **Mine**: static. Player center within 60 px → 0.6 s fuse → explode: 35 damage within 70 px radius; destroy self.
- **Shieldbot chase**: shuffle toward player at 60. Frontal hitbox (32 px wide) blocks projectile damage. Rear/above hitbox takes full damage. Contact 20. Slam every 2.0 s: 0.3 s windup, 0.2 s active (damage 20, radius 50, knockback player 120 px/s away).

### BossAI (T2: Press Golem; T3: Reservoir Warden)

- Boss stationary or moves per attack. Player dodges and shoots.
- Phase advances when hp ≤ phaseTransitionHP → 1.0 s invulnerable transition flash, new attack set enabled.
- Execute attack list on timers as specified. All attacks damage Player on hitbox overlap.
- Player projectiles deal Weapon.damage normally. Rail Lance pierce does NOT pierce boss.
- On hp ≤ 0: 3 s death sequence → stage clear.

### PickupAndAmmo (T1: health + pulse ammo; T2: all types)

- Player hitbox overlaps Pickup → apply effect, remove Pickup, play collect sound.
- Ammo: add amount to corresponding AmmoPool entry, capped at max.
- Health: hp = min(hp + 25, 100). Shield: shield = min(shield + 20, 50). Coin: increment coinsCollected.
- No respawn within a stage. Gone until stage restart.

### LevelGenerator (T1: basic; T2: full)

**Parameters:** `seed` (uint32), `world` (1–2), `stage` (1–5), `difficultyScale` (1.0 default, 1.4 NG+).

**Places in order:**

1. **Floor/ground**: continuous solid at y = 480 (level height 560), width = 3200 px (stages 1–4) or 1600 px (boss). Gaps: `gapCount = 4 + stage + world` gaps of width 48–96 px, spaced every 300–500 px. Pit below = instant death.

2. **Mid-platforms**: `platCount = 6 + stage × 2` one_way and solid platforms, y ∈ {320, 384, 256}, x spaced 200–400 px, w ∈ {64, 96, 128, 192}. Crumble: `crumbleCount = 2 + stage` at y = 256 only.

3. **Upper platforms / ceilings**: `ceilCount = 3 + stage` solid slabs at y ∈ {128, 160}, w ∈ {96, 128}, forcing crouch passages (gap height = 32 px).

4. **Enemies**: `enemyCount = 5 + stage × 2 + world × 3`. Distribute: W1: 40% drone, 30% runner, 20% sentry, 10% mine. W2: 20% drone, 25% runner, 25% sentry, 15% mine, 15% shieldbot. Place at x ∈ {400 … levelWidth−200}, y on nearest platform surface.

5. **Hazards**: `hazardCount = 2 + stage` spikes (gap edges/floor) + 1 laser_gate (x ∈ {800, 1600, 2400}). W2 adds acid_pool in 1 gap.

6. **Pickups**: 2 ammo (random type, weighted toward active weapon), 1 health, 1 shield, 6–10 coins on platforms and in air pockets.

7. **Checkpoint**: flag at x = levelWidth × 0.5 (stage 3+ only). Touch sets respawn.

8. **Extraction pad**: at x = levelWidth − 80, y = 480. Triggers stage clear on overlap.

9. **Weapon unlock crates** (fixed): W1S2 → Scatter Cannon. W1S3 → Arc Burst. W1S4 → Rail Lance. W2 stages → ammo/health only.

**Verifier:** (a) No entity inside solid platform. (b) Every gap jumpable: width ≤ 96 AND platform within 120 px horizontal at reachable height. (c) ≥ 1 health pickup before midpoint. (d) Crouch passages clearance ≥ 28 px. (e) No pickup unreachable (path from ground using max jump height ≈ 180 px). If any check fails → re-roll (seed+1), regenerate.

### StageFlow (T1)

- Touch Extraction Pad → stage complete → Stage Clear screen → advance stage.
- currentStage > 5 → advance world, reset stage = 1. currentWorld > 2 → Game Complete.
- Boss stages (5): arena 1600 px wide, flat floor, 4 one-way platforms at corners. No extraction pad; boss death triggers clear.
- Death: respawn at checkpoint (or stage start if before checkpoint). Lives − 1. Lives = 0 → Game Over.

### Scoring (T2)

- Stars: 1 = clear. 2 = clear + ≥ 60% enemies killed. 3 = clear + ≥ 60% enemies + all coins + time ≤ par_time.
- `par_time = 45 + stage × 10` s (S1 = 55, S5 = 95).
- Total stars tracked; shown on world-select and end screen.

## Progression and Difficulty

**Unlock order:**
- Start: Pulse Rifle (Rivet Driver), 120 ammo, 100 HP, 50 shield, 3 lives.
- W1S2: Scatter Cannon unlocked, +24 shells.
- W1S3: Arc Burst unlocked, +40 cells. Checkpoint introduced.
- W1S4: Rail Lance unlocked, +10 charges.
- W1S5: Boss 1 (Press Golem, 600 HP).
- W2S1–S4: All four weapons; ammo refills to start values each stage; enemy HP × 1.2 (World 2 baseline).
- W2S5: Boss 2 (Reservoir Warden, 1100 HP). Game ends.

**Difficulty curve:**
- W1S1: 7 enemies, 6 gaps, 2 hazards. Learn movement + pulse rifle.
- W1S3: 11 enemies, 8 gaps, 4 hazards, checkpoint, mines + crouch passages.
- W1S4: 13 enemies, 10 gaps, 5 hazards. Rail Lance introduced; pierce drone clusters.
- W2S1: 10 enemies (includes shieldbots), 7 gaps, 3 hazards + acid. HP × 1.2.
- W2S4: 16 enemies, 10 gaps, 6 hazards. All types mixed.
- Bosses: phase 2 adds charge/teleport; phase 3 adds summons. Manage ammo across 4 weapons.

**Where the player is expected to fail:**
- Boss phase 3: first attempt likely death. Respawn at stage start, full ammo, lives − 1.
- Crouch-passage W2: die to laser_gate. Checkpoint at mid-stage halves replay.
- All 3 lives lost: Game Over → restart current world at Stage 1, ammo reset, lives = 3. No permanent loss.

**NG+ (T4):** Unlocked after full clear. Enemy HP × 1.4, enemy count × 1.3, boss HP × 1.3, par_times −20%. Ammo caps unchanged.

## Feel

| Parameter | Value | Tuned to achieve |
|---|---|---|
| Run speed | 280 px/s | Momentum + aimability |
| Crouch speed | 140 px/s | Deliberate traversal |
| Acceleration | 1800 px/s² | Top speed in ~0.16 s; snappy |
| Deceleration | 2400 px/s² | Stop in ~0.12 s; no ice-skating |
| Jump velocity | +480 px/s | ~180 px peak; clears 2-tile gaps |
| Double-jump velocity | +400 px/s | Second push, not a reset |
| Gravity | −1400 px/s² | Snappy arc; 180 px fall in ~0.5 s |
| Terminal velocity | −700 px/s | Pits feel deadly |
| Coyote time | 0.08 s | Walk off edge → still jump |
| Jump buffering | 0.10 s | Press just before land → fires on land |
| Pulse fire rate | 7 shots/s | ~143 ms between shots |
| Scatter rhythm | 1.5 shots/s + 0.6 s cooldown | Pump-action rack |
| Rail lockout | 0.15 s of 1.1 s | Weight of the shot |
| Knockback (hit on player) | 120 px/s impulse, 0.15 s | Visible push, not loss of control |
| Hit flash | 0.1 s white | Readable, not obscuring |
| Invulnerability | 1.2 s | Reposition; not trivializing |
| Shield regen start | 2.0 s after hit | Tension window |
| Shield regen rate | 12 pts/s | Full in ~4.2 s |
| Crumble timer | 1.5 s | Enough to jump off; punishes lingering |
| Laser gate period | 2.0 s (1.0/1.0) | Readable rhythm |
| Drone bullet speed | 180 px/s | Dodgeable, threatening |
| Sentry bullet speed | 300 px/s | Requires lateral/crouch dodge |
| Boss shockwave speed | 200 px/s | Jump over; clear tell |
| Camera look-ahead | 120 px | Shows 1/3 screen ahead |
| Camera vertical dead-zone | ±80 px | No jitter on small hops |
| Death respawn fade | 1.5 s | Register failure; not frustrating |
| Screen shake (hit) | 4 px, 0.15 s | Impact, no nausea |
| Screen shake (boss slam) | 8 px, 0.3 s | Bigger event, bigger shake |

---

# 5. CHARACTERS

## Player (Kael, the Data-Runner)

**Silhouette:** Chunky, top-heavy. Broad shoulders, short legs, oversized helmet with glowing visor slit. Exo-suit with visible piston joints at knees and elbows. At a glance: "small tough thing with a big head and a big gun." Visor colour changes with equipped gun: cyan = Arc Burst/Rail Lance, magenta = Scatter, amber = Rivet Driver.

**Facings:** Left, Right (mirrored). Crouch, jump, run states for both. No diagonal.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | 2 frames: breathe (y ±2 px). Head tilts 2° alternating. | 0.8 s |
| Run | 4 frames: legs alternate, body bobs y ±3 px, arms swing ±15°. | 0.3 s |
| Crouch | 1 pose (static). Helmet retracts 4 px into shoulders. | None |
| Jump (ascend) | 1 pose: body stretch 1.8×, legs tucked, arms up. | Transition only |
| Jump (descend) | 1 pose: body return, legs extend forward. | Transition only |
| Land | 2 frames: squash 1.2× → normal. | 0.15 s |
| Shoot (Rivet/Scatter) | 2 frames: recoil lean back 5° → return. | 0.1 s |
| Shoot (Rail Lance) | 1 pose: arms locked forward, slight lean back. | Hold while cooldown |
| Shoot (Arc Burst) | 1 pose: arms locked forward, coil glow. | Hold while firing |
| Hurt | 3 frames: white flash, wobble, recover. | 0.45 s |
| Death | Shatter into 8 shards. | 1.2 s, no loop |

## Rust Crawler (runner)

**Silhouette:** Low, wide, insect-like. Four legs splayed, single glowing eye on stalk. "A rusty beetle that scuttles."

**Facings:** Left, Right.

| Animation | Frames | Loop |
|---|---|---|
| Idle | 2: eye stalk sways ±3°. | 1.2 s |
| Walk | 4: legs alternate, body y ±2 px. | 0.4 s |
| Hurt | 1: white flash, legs tuck. | 0.1 s |
| Death | Collapse: legs fold, body flattens to 12 px height, fades. | 0.5 s |

## Dripling (drone)

**Silhouette:** Floating teardrop with two moth-like wings. Glowing cyan body, single magenta eye. "An angry glowing raindrop."

**Facings:** Left, Right.

| Animation | Frames | Loop |
|---|---|---|
| Hover | 4: wings up/mid/down/mid, body sine y ±12 px. | 1.0 s |
| Lunge (attack) | 2: stretch forward 1.5×, wings back. | 0.2 s |
| Hurt | 1: magenta flash, body compresses. | 0.1 s |
| Death | Pop: expand 1.3×, shatter into 6 droplet circles, fade. | 0.6 s |

## Sentry

**Silhouette:** Rectangular turret base with a rotating barrel. Single glowing eye. "A wall-mounted gun that swivels."

**Facings:** Barrel rotates freely; base is fixed.

| Animation | Frames | Loop |
|---|---|---|
| Idle | Barrel sways ±5°. | 2.0 s |
| Aim | Barrel snaps to player angle. | Transition 0.15 s |
| Fire | Barrel recoil −4 px, muzzle flash. | 0.1 s |
| Hurt | White flash. | 0.1 s |
| Death | Barrel drops, sparks. | 0.4 s |

## Mine

**Silhouette:** Octagonal puck with blinking centre. "A pressure plate that hates you."

**Facings:** N/A (static).

| Animation | Frames | Loop |
|---|---|---|
| Idle | Centre blink slow. | 1.5 s |
| Fuse | Centre blink fast (0.6 s). | Until explode |
| Explode | Flash circle r=70, 8 shards. | 0.3 s |

## Shieldbot

**Silhouette:** Rectangular body with a large front shield plate. Glowing eye slit. "A walking riot shield."

**Facings:** Left, Right (shield faces movement direction).

| Animation | Frames | Loop |
|---|---|---|
| Shuffle | 2: body rocks ±2°, shield wobbles. | 1.0 s |
| Slam (windup) | 1: shield pulls back. | 0.3 s |
| Slam (active) | 1: shield thrusts forward. | 0.2 s |
| Hurt (rear hit) | White flash, stagger. | 0.15 s |
| Death | Shield falls, body sparks. | 0.6 s |

## Press Golem (W1 Boss)

**Silhouette:** Squat hydraulic press given legs. Two massive piston arms, visor slit across "face," exhaust pipes on shoulders. "A construction press that wants to flatten you."

**Facings:** Left, Right.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Steam puffs from joints every 1.5 s. Body bobs y ±3 px. | 2 s |
| Arm Slam | 4: arm raises 48 px → descends fast → impact squash → recover. | 0.8 s |
| Charge (telegraph) | Visor pulses amber 3× over 0.6 s, body glows #FFB347. | Before attack |
| Hurt | White flash on piston joints. | 0.1 s |
| Death | Pistons explode outward (8 shards), body crumbles over 2 s, steam floods. | 2 s |

## Reservoir Warden (W2 Boss)

**Silhouette:** Floating octagonal core with four long segmented tentacle arms ending in claw pincers. Bioluminescent veins pulse. "A deep-sea jellyfish made of subway infrastructure."

**Facings:** Rotates; no fixed facing.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Arms rotate 15°/s. Core pulses cyan. | Continuous |
| Sweep | 2 arms extend 80 px in a line, core flashes magenta (0.5 s telegraph). | 1 s |
| Spin | All 4 arms extend, core spins 360° in 0.8 s. | 0.8 s |
| Hurt | Core dims 30% for 0.15 s, veins flash white. | 0.15 s |
| Death | Core cracks (4 lines), collapses inward to r=8, detonates in expanding cyan ring + 12 shards. | 2.5 s |

---

# 6. AUDIO

All sounds generated via Web Audio API (OscillatorNode + GainNode envelopes, or noise buffer). No external files.

| Sound name | Waveform | Frequency | Duration | Envelope | Rule that plays it |
|---|---|---|---|---|---|
| jump | sine | 400→800 Hz (glide up) | 0.12 s | attack 0.01, decay 0.11 | Player jump / double-jump |
| land | noise burst | — | 0.06 s | instant attack, decay 0.06 | Player touches ground after airborne |
| shoot_pulse | square | 220 Hz | 0.06 s | attack 0.005, decay 0.055 | Pulse Rifle fires |
| shoot_scatter | sawtooth | 110 Hz + noise | 0.15 s | attack 0.01, decay 0.14 | Scatter Cannon fires |
| shoot_rail | sine | 180→60 Hz (glide down) | 0.3 s | attack 0.02, sustain 0.1, decay 0.18 | Rail Lance fires |
| shoot_arc | triangle | 660 Hz + FM mod | 0.08 s | attack 0.005, decay 0.075 | Arc Burst fires |
| chain_arc | sine | 880→1200 Hz (glide up) | 0.1 s | attack 0.01, decay 0.09 | Arc Burst chain hit |
| hit_enemy | noise burst | — | 0.04 s | instant, decay 0.04 | Projectile hits enemy |
| enemy_die | square | 200→50 Hz (glide down) | 0.25 s | attack 0.01, decay 0.24 | Enemy hp ≤ 0 |
| player_hurt | sawtooth | 150 Hz | 0.12 s | attack 0.01, decay 0.11 | Player takes damage |
| player_die | sine | 300→80 Hz (glide down) | 0.8 s | attack 0.05, decay 0.75 | Player hp ≤ 0 |
| pickup_health | sine | 523→659 Hz (two-tone) | 0.15 s | attack 0.01, decay 0.14 | Health pickup collected |
| pickup_ammo | square | 440 Hz | 0.08 s | attack 0.005, decay 0.075 | Ammo pickup collected |
| pickup_coin | sine | 1047 Hz | 0.06 s | attack 0.005, decay 0.055 | Coin collected |
| checkpoint | sine | 330→440→550 Hz (arpeggio) | 0.4 s | attack 0.02, decay 0.38 | Checkpoint activated |
| weapon_switch | triangle | 600 Hz | 0.05 s | attack 0.005, decay 0.045 | Weapon changed |
| boss_slam | noise + sine 60 Hz | 60 Hz | 0.3 s | attack 0.01, decay 0.29 | Boss ground slam |
| boss_die | sawtooth | 100→30 Hz (glide down) | 1.5 s | attack 0.05, decay 1.45 | Boss hp ≤ 0 |
| stage_clear | sine | 440→550→660→880 Hz (ascending) | 0.8 s | attack 0.05, decay 0.75 | Stage clear triggered |
| game_over | sine | 220→110 Hz (glide down) | 1.0 s | attack 0.05, decay 0.95 | Lives = 0 |
| menu_select | square | 500 Hz | 0.04 s | attack 0.005, decay 0.035 | Menu confirm |
| menu_back | square | 300 Hz | 0.04 s | attack 0.005, decay 0.035 | Menu back/cancel |
| laser_gate_on | sawtooth | 800 Hz | 0.1 s | attack 0.01, decay 0.09 | Laser gate activates |
| mine_fuse | sine | 1000 Hz (pulsing) | 0.6 s | repeated 0.1 s pulses | Mine proximity fuse |
| mine_explode | noise + sine 80 Hz | 80 Hz | 0.4 s | attack 0.01, decay 0.39 | Mine detonates |

---

# 7. UX

## Screen State Machine (HTML/CSS overlays + canvas)

```
TITLE → WORLD_SELECT → STAGE_PLAY → STAGE_CLEAR → (loop or) → WORLD_SELECT
                                          ↓
STAGE_PLAY → (pause) → PAUSE → (resume) → STAGE_PLAY
STAGE_PLAY → (lives=0) → GAME_OVER → TITLE
STAGE_PLAY → (boss dead, W2S5) → GAME_COMPLETE → TITLE
STAGE_PLAY → (stage clear, W1S5) → WORLD_CLEAR → WORLD_SELECT
```

**TITLE:** "GRIDFALL" in stencil font (#FFB347), subtitle "BREAK THE SPIRE" (#00E5FF), "PRESS ENTER / TAP TO START" pulsing magenta (#FF2D78). BG: parallax layers visible, neon sign flickering. Enter/Tap → WORLD_SELECT.

**WORLD_SELECT:** 2 world slots (Floor 1 "The Rustbelt", Floor 2 "The Undercity"). Floor 2 locked until Floor 1 boss defeated. Each world: 5 stage nodes on a path line. Stars shown per node. Arrow keys/tap to select. Enter → STAGE_PLAY. Escape → TITLE.

**STAGE_PLAY:** Gameplay screen. HUD overlaid. Stage intro banner: "WORLD X – STAGE Y" slides in 0.6 s, holds 1.5 s, fades 0.4 s. Escape/P → PAUSE.

**PAUSE:** Overlay: "PAUSED". Resume (Escape/Enter), Restart Stage (R), Quit to World Select (Q).

**STAGE_CLEAR:** Stage name, clear time, enemies killed %, coins, stars (1–3). "Press Enter to continue." → next STAGE_PLAY or WORLD_SELECT.

**WORLD_CLEAR:** "FLOOR CLEARED." World 2 unlocks. → WORLD_SELECT.

**GAME_OVER:** "SYSTEM FAILURE — Lives exhausted." Stage reached. "Press Enter to restart world." → WORLD_SELECT (stage 1 of current world).

**GAME_COMPLETE:** "SPIRE PURGE COMPLETE." Total stars (max 30), best time. "Press Enter to return to title." → TITLE.

## HUD Table

| Element | Record Field | When Visible |
|---|---|---|
| HP bar (120 px wide, cyan→magenta gradient) | `player.hp` / 100 | Always in STAGE_PLAY |
| Shield bar (120 px, cyan, below HP) | `player.shield` / 50 | Always (dimmed if 0) |
| Lives counter (3 small icons, top-left) | `player.lives` | Always |
| Weapon name + ammo count (bottom-left) | `player.weapons[weaponIndex]` + `player.ammo[weaponIndex]` | Always |
| Weapon icon row (4 slots, active ringed) | `player.weapons[]` (owned/locked) | Always; locked show "?" |
| Stage indicator (top-center: "W1-S3") | `level.world` / `level.stage` | Always |
| Timer (top-right, counts up) | `scoreboard.clearTime` | Always |
| Coin count (top-right, below timer) | `scoreboard.coinsCollected` | Always |
| Boss HP bar (top-center, wide) | `boss.hp` / boss max HP | Boss stage only, from first player entry to arena |
| Checkpoint flash ("CHECKPOINT" text) | Triggered on totem touch | 1.0 s on activation |
| Low-ammo warning (weapon icon pulses red) | `ammo[weaponIndex] ≤ 10%` of max | While condition true |
| Stage intro banner | `level.world`, `level.stage` | First 2.5 s of stage |

---

# 8. DEBUG API

Installed by `debug.js` as `window.__game`. All calls synchronous, return plain data, never touch DOM.

| Call | What it does | Returns |
|---|---|---|
| `__game.start()` | Title → play, loads stage 1-1, initialises player. | void |
| `__game.step(dt, n)` | Runs exactly n fixed ticks in tick order, then draws once. | void |
| `__game.setTime(t)` | Runs ticks until `ctx.time ≥ t`, no drawing. | void |
| `__game.seed(n)` | Reseeds `ctx.rng`, calls `level.load(ctx, 1, 1)`, resets player and all pools. | void |
| `__game.getState()` | Deep-cloned plain object of all ctx fields (minus canvas, ctx2d, rng). | object |
| `__game.move(dir)` | Sets `ctx.input.moveDir`. | void |
| `__game.jump()` | Sets `ctx.input.jumpPressed = true` for next tick. | void |
| `__game.crouch(on)` | Sets `ctx.input.crouchHeld`. | void |
| `__game.fire(on)` | Sets `ctx.input.fireHeld`; firePressed if transitioning to on. | void |
| `__game.switchWeapon(dir)` | Sets `ctx.input.switchNext = true`. | void |
| `__game.selectSlot(n)` | Sets `ctx.input.weaponSlot = n` (1–4). | void |
| `__game.spawnEnemy(type, x, y, dir)` | Calls `enemies.spawn`. | `{id, x, y, type, alive}` |
| `__game.spawnProjectile(weaponId, x, y, vx, vy)` | Pulls from pool, configures. | `{id, x, y, alive}` |
| `__game.skipToStage(w, s)` | `level.load(ctx, w, s)`, resets player, state = 'play'. | `{world, stage, spawnX, spawnY}` |
| `__game.setField(path, value)` | Sets ctx field at dotted path. | void |
| `__game.getField(path)` | Gets ctx field at dotted path. | value |
| `__game.getFrameCount()` | Returns `ctx.frame`. | number |
| `__game.getDrawCalls()` | Canvas draw ops from last draw. | number |
| `__game.getStateHash()` | 32-bit hash of getState() JSON. | number |
| `__game.spawnBoss(id)` | Calls `enemies.spawnBoss(ctx, id)`. | `{id, hp, alive}` |
| `__game.setBossHp(hp)` | Sets `ctx.boss.hp`. | void |
| `__game.getLevelGen()` | Returns current level generation data (platforms, enemies, hazards, pickups arrays). | object |
| `__game.verifyLevel()` | Runs verifier on current level; returns pass/fail + failure reasons. | `{pass, failures[]}` |
| `__game.getStageStats()` | Returns scoreboard for current stage. | `{clearTime, enemiesKilled, enemiesTotal, coinsCollected, coinsTotal, stars}` |
| `__game.triggerCheckpoint()` | Forces checkpoint activation at current position. | void |
| `__game.hurtPlayer(dmg)` | Calls `player.hurt(ctx, dmg)`. | void |
| `__game.killEnemy(id)` | Calls `enemies.kill(ctx, enemy)`. | void |

---

# 9. TESTS

All tests drive exclusively through `window.__game`.

### T1 – Title → Play
```
__game.seed(42)
__game.start()
s = __game.getState()
```
Assert: `s.state === 'play'`, `s.level.world === 1`, `s.level.stage === 1`, `s.player.x === s.level.spawnX`, `s.player.y === s.level.spawnY`.

### T2 – Fixed-timestep movement (right)
```
__game.seed(42); __game.start()
__game.move(1)
__game.step(1/60, 60)
p = __game.getState().player
```
Assert: `p.x > s