# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Side-scrolling platformer shooter | §4 Movement, §4 Combat, §3 Visual Spec |
| At least 4 different gun types | §4 Combat (Weapon Roster), §5 Characters (gun recipes) |
| Character can jump | §4 Movement (Jump, Double-jump) |
| Character can move left or right | §4 Movement (Left/Right) |
| Character can crouch | §4 Movement (Crouch) |
| Story progression modelled off Mario: worlds and stages | §4 StageFlow, §4 Progression |
| 2 worlds, 5 stages each (10 stages total) | §4 Progression, §2.2 Global Context |
| Do not simply copy Mario | §0.2 Decisions (theme, mechanics, fiction all differ) |
| *(added)* Seeded level generation for replayability | §4 LevelGenerator |
| *(added)* Star-rating score system per stage | §4 Scoring |
| *(added)* Boss fights at stage 5 of each world | §4 BossAI |
| *(added)* Shield regen mechanic for combat depth | §4 DamageAndDeath |
| *(added)* Coyote time and jump buffering for feel | §4 Movement |
| *(added)* NG+ mode | §4 Progression (T2) |

## 0.2 Decisions

| Topic | Gameplay said | Visual said | Engineering said | Ruling & why |
| --- | --- | --- | --- | --- |
| Canvas internal resolution | Not stated | 960×540 viewport | 1280×720 | **960×540 internal, CSS-scaled to fit window.** Visual's pixel-art 3px-outline style demands a lower native res; 960×540 = 30×16.875 tiles at 32 px, appropriate for a side-scroller. Engineering's 1280×720 becomes the CSS display size. |
| Y-axis direction | Y-down (gravity adds +vy, jump = −vy, terminal +700) | "1 unit = 1 game-pixel", no sign stated | Y-up (gravity −Y) | **Y-down.** All gameplay numbers (vy += 1400·dt, jump vy = −480, terminal 700, pit death y > levelHeight+100) are written for Y-down. Adopting Y-up would require negating every constant and invites sign bugs. Renderer draws directly; no `ctx.scale(1,−1)`. |
| Tile size | Implied 32 px (platform h 16/32, player h 48) | "Tiles are 1×1 unit", stage 240 units wide | `<TILE_SIZE>` placeholder | **TILE_SIZE = 32 px.** Gameplay's explicit pixel numbers win; the placeholder is filled. Stage width 3200 px = 100 tiles. |
| Player dimensions | 48 px tall normal, 28 px crouch; width not stated | 2×3 units (64×96 at 32 px) | `<PLAYER_W>`, `<PLAYER_H>` | **W = 32, H = 48 (normal) / 28 (crouch).** Gameplay's crouch-under-32-px-gap rule requires height 28; width 32 = 1 tile keeps collision simple. Visual's "2×3" is a rough silhouette, not a hitbox. |
| Weapon set & names | pulse_rifle, scatter_cannon, rail_lance, arc_burst (chain/pierce mechanics) | Rivet Driver, Scatter Cannon, Arc Welder (beam), Mortar Launcher (explosive arc) | Not specified | **Gameplay's 4 weapons and their mechanics are authoritative.** Display names: "Rivet Driver" for pulse_rifle, "Scatter Cannon" for scatter_cannon, "Rail Lance" for rail_lance, "Arc Burst" for arc_burst. Visual's Arc Welder beam and Mortar arc are dropped; their art recipes are repurposed as muzzle-flash and projectile visuals for the corresponding gameplay weapons. |
| Scatter pellet count | 6 | 5 | — | **6 pellets.** Gameplay owns the number; the 30°/18° spread and damage math are built around 6. |
| Lives / HP / Shield model | HP 100, Shield 50, Lives 3, numeric bars | 3 hearts, 1-heart low-health | `<PLAYER_MAX_HP>`, `<PLAYER_LIVES>` | **Gameplay's HP/Shield/Lives numeric model.** HUD shows a numeric HP bar and Shield bar, not discrete hearts. "Low health" triggers at HP ≤ 25. |
| Level geometry | Seeded procedural generator with formulas | "Hand-placed fixed platform layouts" | Not specified | **Seeded generator.** Gameplay provides complete, testable formulas. Visual's layout table becomes the *thematic dressing* (palette, parallax, props) applied over generated geometry. |
| Stage-clear mechanism | Touch extraction pad at far right | Collect Stage Key, then reach Exit Gate | `exitX/exitY` trigger zone | **Extraction pad = Exit Gate visually.** No separate key item; overlap the pad at x = levelWidth−80 to clear. Boss stages clear on boss death. |
| Boss names | Custodian, Architect | Press Golem, Reservoir Warden | — | **Gameplay names (Custodian, Architect)** fit the data-runner fiction; visual's art descriptions (hydraulic press, octagonal core) are kept as the look. |
| Enemy type names | drone, sentry, runner, mine, shieldbot | Rust Crawler, Dripling | — | **Gameplay type IDs.** Visual's Rust Crawler = runner (ground charger); Dripling = drone (flying sine-bob). Art recipes map accordingly. |
| Screen shake magnitude | 4 px, 0.15 s | 0.3 units (≈9.6 px), 0.2 s | — | **4 px, 0.15 s.** Gameplay's numbers are in game-logic pixels and are the tuned feel values. |
| Fire input binding | Mouse click / J / Touch FIRE | — | J / Z / Enter | **J or mouse click or Z.** Enter is reserved for menu confirm; using it for fire creates conflicts. |
| Weapon switch binding | 1/2/3/4, Q cycles | — | K/X cycle, 1-5 slots | **1-4 direct select, Q cycles forward.** 4 weapons, not 5. K/X dropped to reduce key count. |
| Pause binding | Escape | — | Esc / P | **Escape only.** P removed to avoid conflict with potential future bindings. |
| Double jump | Yes (max 2) | Not mentioned | Not mentioned | **Yes.** Gameplay specifies it; it is core to the movement feel. |
| Coyote time / jump buffer | 0.08 s / 0.10 s | Not mentioned | Not mentioned | **Yes, as specified.** Critical platformer feel. |
| Fiction / theme | "Kael, data-runner, Helix Spire" | "Scavenger, drowned mega-city" | — | **Merged: Kael is a data-runner in a neon post-industrial Spire (a mega-corp server tower in a drowned industrial city).** World 1 = "The Rustbelt" (upper floors), World 2 = "The Undercity" (sub-basement). Visual's palette and art direction apply. |
| Camera viewport size | Not stated (implied by look-ahead 120 px) | 960×540 | 1280×720 | **960×540** (matches ruling above). |
| Level width | 3200 px (stages 1-4), 1600 px (boss) | 240 units (7680 px at 32) | ≤ 6400 px | **3200 px / 1600 px** (gameplay). Well within engineering's 6400 cap. |
| Level height | 560 px (ground at y=480) | 24 units (768 px) | ≤ 2560 px | **560 px** (gameplay). Ground at y = 480, ceiling area above. |
| NG+ | Yes, HP×1.4, count×1.3, boss×1.3, par−20% | Not mentioned | Not mentioned | **Yes, T2 tier.** |
| Audio | Not detailed | Not detailed | Web Audio, oscillator/noise | **Web Audio API, generated SFX.** Full table in §6. |

## 0.3 Tiers

**T1 (ships the game):** Movement · Combat (4 weapons, projectiles) · DamageAndDeath (HP/Shield/Lives) · EnemyAI (5 types) · BossAI (2 bosses, 3 phases) · PickupAndAmmo · LevelGenerator (seeded) · StageFlow (2 worlds × 5 stages) · Scoring (stars) · HUD & Screens · Basic Audio · Particles (hit-spark, dust, pickup) · Camera · Input (keyboard) · Progression · Debug API · All §9 tests T1-T18

**T2:** NG+ mode · Parallax layers 3-4 · Touch controls · Chromatic aberration post-effect · Film grain · Confetti on exit · Coin score detail · Weapon unlock crate animations · Conveyor belt hazard (visual only) · Bioluminescent moss lighting (W2)

**T3:** Seeded re-roll from title · Speed-run timer ghost · Achievement/star persistence to localStorage · Boss death steam-flood full-screen effect · World-map player-icon walk animation · Stage-intro banner slide animation

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Item | Rule |
|---|---|
| 1 unit | 1 logical pixel. Internal canvas resolution **960 × 540**. CSS display size scales to fit the browser window (maintain 16:9). `devicePixelRatio` respected: actual buffer = 960×540 × dpr, CSS size = viewport. |
| Game-logic axes | **X → right positive. Y → down positive.** Ground plane at y = 480 (stage 1-4) or y = 480 (boss). Gravity: `vy += 1400 × dt`. Jump impulse: `vy = −480`. Terminal `vy = +700`. |
| Render axes | Canvas default Y-down. **No `ctx.scale(1,−1)`.** World transform is a pure `ctx.translate(−camera.x, −camera.y)`. HUD drawn in screen space with `ctx.setTransform(1,0,0,1,0,0)`. |
| Origin (world) | Top-left of level bounding box = (0, 0). Level width 3200 px (stages 1-4) or 1600 px (stage 5). Level height 560 px. |
| TILE_SIZE | **32 px.** All tile-grid coordinates multiply by 32 to get world px. |
| Camera viewport | 960 × 540 px. `camera.x` = left edge in world px; `camera.y` = top edge in world px. Clamped to `[0, levelWidth−960] × [0, levelHeight−540]`. |
| Fixed timestep | `DT = 1/60 s ≈ 0.016667 s`. Accumulator per rAF callback; max **5** catch-up ticks; excess discarded. |
| Tick order | 1. `input.update` → 2. `physics.update` → 3. `player.update` → 4. `weapons.update` → 5. `enemies.update` → 6. `boss.update` → 7. `particles.update` → 8. `camera.update` → 9. `progression.update` → 10. `audio.update`. Then `renderer.draw()` once. |
| Random source | **One** seeded PRNG: `mulberry32(seed)` exposed as `ctx.rng()`, returns float [0,1). No `Math.random()` in game logic. Renderer/audio may use `Math.random()` for cosmetic-only jitter never read back. |

## 1.2 Important conventions

**Controls table (authoritative):**

| Input | Action | Type |
|---|---|---|
| A / ← | Move left | Held |
| D / → | Move right | Held |
| W / ↑ / Space | Jump (also double-jump) | Edge-triggered |
| S / ↓ | Crouch | Held |
| J / Z / Mouse-click | Fire current weapon | Held (auto-repeat for Pulse/Arc); edge for Scatter/Rail |
| 1 / 2 / 3 / 4 | Select weapon slot directly | Edge |
| Q | Cycle weapon forward | Edge |
| Escape | Pause / Resume | Edge |
| R | Restart stage (in Pause menu) | Edge |
| Enter | Confirm in menus | Edge |
| Touch left-half hold | Move L/R (analog by offset) | Held |
| Touch right-top tap | Jump | Edge |
| Touch right-mid hold | Crouch | Held |
| Touch right-bottom hold | Fire | Held |
| Touch two-finger tap | Switch weapon | Edge |

All keyboard bindings are **both** WASD and arrow keys simultaneously. Touch events synthesise into the same `ctx.input` object; no game code branches on device.

**One random source rule:** All gameplay randomness (enemy spawn placement, pickup type selection, scatter spread per pellet, arc-burst chain target) flows through `ctx.rng()`. The seed is set at title-screen confirm or re-roll.

**Pool rule:** Enemies, projectiles, and particles are pre-allocated fixed-size arrays of plain objects. Update loops mutate fields in place; death sets `alive = false`; spawn scans for first dead slot. **No `new`, no `{}`, no `.push()`, no `.splice()` inside any `update()` function.**

---

# 2. CONTRACTS

## 2.1 Module layout

| Module | Responsibility |
|---|---|
| `game.js` | Boot, top-level state machine, rAF loop, calls modules in tick order. |
| `input.js` | Keyboard/touch → `ctx.input`. |
| `physics.js` | AABB tile collision, entity collision, gravity integration, ground detection. |
| `player.js` | Player state machine, HP/Shield/Lives, crouch, jump, invuln, respawn. |
| `weapons.js` | 4 weapon definitions, fire logic, projectile pool, damage application, arc chain. |
| `enemies.js` | 5 enemy types, per-type AI, spawn from level data, death. |
| `boss.js` | 2 boss definitions, phase logic, attack timers. |
| `level.js` | Seeded generator → tile arrays, entity spawns, pickups, hazards, exit pad. |
| `camera.js` | Dead-zone follow, look-ahead, clamp. |
| `particles.js` | Ring-buffer pool; spawn, update, query-alive. |
| `audio.js` | Web Audio API oscillator/noise SFX; queue drain. |
| `progression.js` | World/stage index, unlocks, stars, NG+, game-over. |
| `ui.js` | HUD, title, pause, stage-clear, game-over, world-select screens. |
| `debug.js` | `window.__game` API. |

## 2.2 Global context

```js
const ctx = {
  // environment
  canvas: null, ctx2d: null,
  seed: 0, rng: null,
  dt: 0.016666667, time: 0, frame: 0,
  running: true,
  state: 'title', // 'title'|'world-select'|'play'|'pause'|'stage-clear'|'game-over'|'game-complete'

  // input
  input: {
    moveDir: 0, jumpPressed: false, jumpHeld: false,
    crouchHeld: false, firePressed: false, fireHeld: false,
    switchNext: false, weaponSlot: 0,
    pause: false, restart: false, confirm: false,
    touch: null, // {x,y,active} or null
  },

  // player
  player: {
    x: 80, y: 480, vx: 0, vy: 0,
    w: 32, h: 48,            // h=28 when crouching
    facing: 1, onGround: false, crouching: false,
    state: 'grounded',       // 'grounded'|'airborne'|'crouching'|'hurt'|'dead'
    hp: 100, maxHp: 100,
    shield: 50, maxShield: 50,
    shieldRegenDelay: 0,     // counts up; regen at 2.0
    lives: 3,
    invulnTimer: 0,          // 1.2 after hit
    jumpCount: 0,            // max 2
    coyoteTimer: 0,          // 0.08
    jumpBufferTimer: 0,      // 0.10
    activeWeapon: 'pulse_rifle',
    weapons: ['pulse_rifle'], // unlocked ids
    ammo: { pulse_rifle: 120, scatter_cannon: 24, rail_lance: 10, arc_burst: 40 },
    ammoMax: { pulse_rifle: 240, scatter_cannon: 48, rail_lance: 20, arc_burst: 80 },
    fireCooldown: 0,
    recoilLockout: 0,        // rail lance movement freeze
    checkpointX: 80, checkpointY: 480,
  },

  // projectiles (pool)
  projectiles: [], // {x,y,vx,vy,w,h,damage,alive,owner,weaponId,pierceLeft,life,chainUsed}
  projectilePoolSize: 256,

  // enemies (pool)
  enemies: [], // {x,y,vx,vy,w,h,hp,maxHp,type,alive,state,patrolDir,patrolRange,aggroRange,attackCd,timer,hitFlash}
  enemyPoolSize: 64,
  enemyCap: 40,

  // boss
  boss: null, // {id,x,y,w,h,hp,maxHp,phases,currentPhase,phaseTransitionHP,attackTimers:[],alive,invuln}

  // pickups (per-stage list, not pooled)
  pickups: [], // {type,x,y,amount,collected}

  // level
  level: {
    world: 1, stage: 1,
    width: 3200, height: 560,
    tiles: null,       // Uint8Array, row-major, (width/32)×(height/32)
    widthTiles: 100, heightTiles: 18,
    spawnX: 80, spawnY: 480,
    exitX: 3120, exitY: 480,
    hazards: [],       // {type,x,y,w,h,damage,period}
    platforms: [],     // {x,y,w,h,type,crumbleTimer}
    entitySpawns: [],  // [{type,x,y,dir}]
    checkpointX: 0,    // 0 = none
  },

  // camera
  camera: { x: 0, y: 0, w: 960, h: 540, lookAhead: 120, deadZoneY: 80 },

  // particles (ring buffer)
  particles: [], // {x,y,vx,vy,life,maxLife,alive,colour,shape}
  particlePoolSize: 1024,
  particleCap: 512,

  // progression
  progression: {
    totalStages: 10,
    unlockedWorld: 1,
    stagesCleared: [],   // ["1-1","1-2",...]
    stars: {},           // {"1-1": 3, ...}
    score: 0,
    ngPlus: false,
    difficultyScale: 1.0,
  },

  // scoreboard (current stage)
  scoreboard: { clearTime: 0, enemiesKilled: 0, totalEnemies: 0, coinsCollected: 0, stars: 0 },

  // audio queue
  audioQueue: [], // [{id:'shoot_pulse'|'hit'|...}]

  // screen shake
  shake: { intensity: 0, duration: 0, timer: 0 },
};
```

## 2.3 Module specifics

### `game.js`
| Export | Purpose |
|---|---|
| `boot(canvas, seed)` | Create `ctx`, init all modules, start rAF. |
| `setState(s)` | Transition state machine; reset `time`, `frame`, reseed per stage. |
| `loop(timestamp)` | rAF callback: accumulate, run ≤5 ticks, draw once. |

### `input.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Register listeners. |
| `update(ctx, dt)` | Latch edge flags, clear after tick. |
| `reset(ctx)` | Clear all flags (pause, stage change). |

### `physics.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Pre-compute tile lookup. |
| `update(ctx, dt)` | Integrate, resolve tile + entity collisions. |
| `isSolid(ctx, tx, ty)` | Bool. |
| `isHazard(ctx, tx, ty)` | Bool. |
| `tileAt(ctx, wx, wy)` | Tile type at world px. |
| `resolveAABB(a, b)` | `{overlapX,overlapY,normalX,normalY}` or null. |

### `player.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Build from `ctx.level.spawnX/Y`. |
| `update(ctx, dt)` | State machine, movement, jump, crouch, gravity, coyote, buffer. |
| `hurt(ctx, dmg)` | Apply damage (shield→hp), invuln, knockback, death check. |
| `respawn(ctx)` | Reset to checkpoint, decrement lives. |
| `getHitbox(ctx)` | `{x,y,w,h}` reflecting crouch. |

### `weapons.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Load 4 weapon defs. |
| `update(ctx, dt)` | Tick cooldowns, advance/despawn projectiles, collision. |
| `fire(ctx)` | Spawn projectile(s) from pool per active weapon. |
| `getWeaponDef(id)` | Definition object. |
| `switchWeapon(ctx, dir)` | Advance `player.activeWeapon` through owned list. |
| `applyArcChain(ctx, proj, hitEnemy)` | Arc Burst secondary projectile. |

### `enemies.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Load 5 enemy defs; populate from `ctx.level.entitySpawns`. |
| `update(ctx, dt)` | AI per type, gravity, collision, death. |
| `spawn(ctx, type, x, y, dir)` | Pull from pool, configure. |
| `kill(ctx, enemy)` | alive=false, audio event, particles, score increment. |

### `boss.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Load 2 boss defs. |
| `update(ctx, dt)` | Phase logic, attack timers, damage to player. |
| `spawn(ctx, id)` | Instantiate boss for stage 5. |
| `hurt(ctx, dmg)` | Apply damage, check phase transition / death. |

### `level.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | — |
| `load(ctx, world, stage)` | Run seeded generator; build tiles, platforms, spawns, pickups, hazards, exit. |
| `update(ctx, dt)` | Check player↔exit overlap, checkpoint touch, crumble timers. |
| `isSolid(ctx, tx, ty)` / `isHazard(ctx, tx, ty)` / `tileAt(ctx, wx, wy)` | Tile queries. |

### `camera.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Set viewport 960×540. |
| `update(ctx, dt)` | Look-ahead, dead-zone, clamp. |

### `particles.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Allocate 1024 structs. |
| `update(ctx, dt)` | Advance, recycle. |
| `spawn(ctx, x, y, vx, vy, life, colour, shape)` | Write next slot. |
| `getAlive(ctx)` | Iterator for renderer. |

### `audio.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | AudioContext, pre-build buffers. |
| `update(ctx, dt)` | Drain queue, play. |
| `play(ctx, id)` | Push event id. |

### `progression.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | Set totalStages, unlock table. |
| `update(ctx, dt)` | Stage-clear / game-over / game-complete checks. |
| `advance(ctx)` | Next stage or world; trigger game-complete after W2S5. |
| `restartWorld(ctx)` | Game-over: reset to stage 1 of current world. |
| `calculateStars(ctx)` | 1-3 star logic from clearTime, enemiesKilled, coins. |

### `ui.js`
| Export | Purpose |
|---|---|
| `init(ctx)` | — |
| `draw(ctx, c2d)` | Render HUD or overlay per `ctx.state`. |

### `debug.js`
See §8.

---

# 3. VISUAL SPEC

**The look in one paragraph:** 2D side-scrolling, fixed zoom, no rotation. A neon-soaked post-industrial wasteland: a lone data-runner in a battered exo-suit blasts through the skeletal remains of a drowned mega-city server tower. Palette is deep oxidized teal (#1A2E33) and rust-orange (#C45A2D) as ground truth, punctuated by electric cyan (#00E5FF) and hot magenta (#FF2D78) from gunfire, signage, and bioluminescence. Mood: "gritty Saturday-morning cartoon"—chunky readable shapes, bold 3-pixel black outlines, exaggerated squash-and-stretch on every impact. The screenshot that sells it: the player mid-air, crouching-then-jumping off a rusted conveyor belt, magenta plasma bolt streaking right, a two-story enemy reeling with a cyan hit-flash, parallax layers of dripping pipes and flickering neon signs visible behind, all in thick 3px black outlines over flat saturated fills.

**Lighting and atmosphere:** Ambient very low: base #0F1B1F at 25%. World is dark; light is diegetic (lamps, neon, gunfire, bioluminescence). Background layers 1-2 darkened 40% vs foreground. W2 adds vertical fog band (#15292E, 30% alpha) at 60% height. Boss arenas drop ambient to 10%; only spotlight and gunfire illuminate. Post-effects: vignette always (40% edge darkening, radius 70% viewport); screen shake (player hit, boss slam, explosion: 4 px, 0.15 s, linear decay); hit flash (player damage: 1-frame #FF2D78 at 15% alpha); chromatic aberration (HP ≤ 25: 0.6 px red/blue split, T2); grain (3% monochrome noise, 24 fps refresh, T2); radial flash (checkpoint: white ring 0.4 s, 30% alpha); desaturation (death: 20% colour over 0.8 s).

**The space:** Coordinate system: 1 unit = 1 game-pixel at 960×540 internal resolution. Player stands 32 px wide × 48 px tall (28 crouch). Tiles are 32×32 px. A stage is a horizontal corridor 3200 px wide × 560 px tall (stages 1-4) or 1600×560 (boss stage 5). Ground plane at y = 480. Camera viewport 960×540 with horizontal look-ahead 120 px and vertical dead-zone ±80 px.

**Stage layout (per stage, left → right):**

| Region | Width (px) | Contents | Visual tell |
|---|---|---|---|
| Spawn ledge | 0–384 | Flat ground, flickering lamp post, start banner | Warm sodium glow (#FFB347) pools on floor |
| Mid traversal | 384–2816 | Platforms, pits, enemies, pickups, hazards | BG parallax shifts; ground texture changes every 400 px |
| Checkpoint | at x = 1600 (stages 3+) | Glowing totem | Pulsing cyan ring, hum particles |
| Arena / boss room | 0–1600 (stage 5) | Enclosed, 4 one-way platforms at corners, boss pad | Lighting 10%, single overhead spotlight, walls close in |
| Exit pad | 3120 (stages 1-4) | Massive shutter door with stage-number stencil | Magenta rim-light on frame; opens on overlap |

**World 1 – "The Rustbelt":** Corrugated steel plates, broken concrete. BG: smokestacks, hanging chains, conveyor machinery. Palette rust-orange dominant. Stage 5: hydraulic-press room, ceiling at y = 128, floor is grate over boiling oil.

**World 2 – "The Undercity":** Cracked tile, flooded shallow channels (32 px deep). BG: dripping brick arches, subway tunnels, bioluminescent moss. Palette deep-teal dominant with magenta/cyan fungi. Stage 5: drained reservoir, concentric ring platforms.

**Stage progression visual cue:** Each stage number (1-5) adds one more BG parallax layer and one more colour accent. Stage 1: 2 layers, 2 accents. Stage 5: 4 layers, 4 accents.

**Recipe table:**

| Name | Shapes & Size (px) | Colours (hex) | Count | Motion / Effect |
|---|---|---|---|---|
| Player – idle | Rounded rect body 32×48, circle head r=11 atop, 2 stub arms, 2 stub legs. 3px black outline. | Suit #2C3E50. Visor #00E5FF. Accents #FF2D78. | 1 | 2-frame breathing bob (y ±2, 0.8 s cycle) |
| Player – crouch | Squashed rect 32×28, head tucks. | Same | 1 | Static pose |
| Player – run | Same body, legs alternate 4-frame stride (y ±3 bounce). | Same | 1 | Leg cycle; dust puffs (#8B7355, r=10, fade 0.3 s) at feet |
| Player – jump | Body stretched 32×58, arms up. | Same | 1 | Squash→stretch→return. Trail: 3 ghost copies at 40% alpha, 0.1 s apart |
| Player – hurt | Body tinted #FF2D78 at 70% opacity, 3-frame flash. | Flash #FF2D78→white→back | 1 | 0.1 s/frame, knockback wobble (x ±6) |
| Player – death | Shatters into 8 triangle shards (r=13 each). | Shards #2C3E50, edges #FF2D78 | 1 | Spin + fade 1.2 s |
| Gun – Rivet Driver | Rect barrel 48×13, circle muzzle r=8. | Body #5C6B73. Muzzle ring #FFB347. | 1 | Recoil: barrel x-offset −10 for 0.08 s |
| Rivet – projectile | Circle r=5, trailing line 16. | Core #FFB347. Trail fade. | ≤12 on-screen | Linear. Fade at 770 px range. |
| Gun – Scatter Cannon | Wide rect barrel 38×22, 3 muzzle ports r=4. | Body #8B4513. Ports #FF2D78. | 1 | Muzzle flash: 3 radial lines 26 px, #FF2D78, 0.06 s |
| Scatter – projectile (×6) | Tiny circles r=3, spread 18° cone. | #FF2D78 | 6 per shot | Linear, fade at 234 px range. |
| Gun – Rail Lance | Long rect barrel 64×10, glowing rings ×3. | Body #1A2E33. Rings #00E5FF. | 1 | Charge-up glow 0.3 s before fire |
| Rail – projectile | Elongated rect 24×4, bright core. | #00E5FF→#FFFFFF gradient | 1 | Linear 1400 px/s. Pierce visual: passes through enemies. |
| Gun – Arc Burst | Cylindrical barrel 32×16, 3 coil rings. | Body #1A2E33. Coils #00E5FF. | 1 | Continuous glow; on hit, arc line to chain target |
| Arc – projectile | Circle r=6, wavy trail. | #00E5FF core, #FF2D78 edge | 1 | Linear 480 px/s. On hit: chain line to next enemy within 90 px. |
| Enemy – drone (Dripling) | Teardrop body 32×48, 2 wing arcs r=26. | Body #00E5FF. Wings #1A2E33. Eye #FF2D78. | 2-5/stage | Sine hover (y ±12, 1.0 s). Wings 4-frame flap. |
| Enemy – sentry | Turret base 32×32, barrel 24×8. | Body #5C6B73. Barrel #FF2D78. | 2-4/stage | Rotates to face player. |
| Enemy – runner (Rust Crawler) | Low rect 64×38, 4 stub legs, single red eye r=6. | Body #C45A2D. Eye #FF2D78. | 3-6/stage | 4-frame leg crawl, y ±2 bob. |
| Enemy – mine | Sphere r=16, blinking light. | Body #3D3D3D. Light #FF2D78. | 1-3/stage | Static. Proximity: light blinks faster, 0.6 s fuse. |
| Enemy – shieldbot | Rect 48×64, front shield plate 16×64. | Body #2C3E50. Shield #5C6B73. Eye #FF2D78. | 2-4/stage (W2) | Shuffles. Shield blocks frontal shots. |
| Boss – Custodian | Massive rect 80×100, piston arms ×2 (48×32 each), visor slit. | Body #3D3D3D. Pistons #C45A2D. Visor #FFB347. | 1 | Idle: steam puffs from joints. Attack: arm slam, screen shake. |
| Boss – Architect | Octagonal core r=48, 4 tentacle arms (length 80, r=10). | Core #1A2E33. Arms #00E5FF. Eye #FF2D78. | 1 | Arms rotate 15°/s. Charge: core pulses magenta. |
| Pickup – Health Cell | Hexagon r=16, cross icon. | Shell #00E5FF. Cross #FFF. | 1-2/stage | Float y ±6 sine, 1 s. Glow halo r=38, 40% alpha. |
| Pickup – Shield Cell | Hexagon r=16, shield icon. | Shell #FFB347. Icon #FFF. | 1/stage | Same float. |
| Pickup – Ammo Crate | Rect 32×32, lid at 30°, bullet icon. | Body #FFB347. Lid #8B7355. | 2/stage | Static; wobble ±2 when player within 64 px. |
| Pickup – Coin | Circle r=8, spinning. | #FFB347 with #FF2D78 inner | 6-10/stage | Spin 180°/s, bob ±5. |
| Platform – Solid | Rect, variable w×32 or 16. Top 5 px lighter strip. | W1: #5C6B73 top #8B7355. W2: #1A2E33 top #2C4A52. | Many | Static. |
| Platform – Crumble | Same + 4 crack lines. | #8B7355, cracks #C45A2D. | 2-5/stage | On touch: 0.4 s shake → 6 shard pieces fall. |
| Platform – One-way | Rect, dashed bottom edge. | Same as solid, dashed. | Many | Player can drop through. |
| Platform – Conveyor | Rect + 6 scrolling chevrons. | Body #3D3D3D. Chevrons #FFB347. | 1-2/stage | Chevrons scroll (visual only, no push). T2. |
| Hazard – Spikes | Row of triangles base 13, height 19. | #8B7355, tips #FF2D78. | Clusters 4-8 | Static. |
| Hazard – Laser Gate | Vertical beam 8×128, emitter nodes. | #FF2D78 80% alpha. | 1/stage | Period 2.0 s (1.0 on / 1.0 off). |
| Hazard – Acid Pool | Rect pool, wavy top. | #00E5FF 50%, white sparks. | 0-1/stage (W2) | Wave sine amp 3; sparks blink 0.2 s random. |
| BG Layer 1 – Far skyline | Silhouette rects/triangles, parallax 0.2×. | W1 #0F1B1F. W2 #0A1618. | Full-width | Static (camera parallax). |
| BG Layer 2 – Mid structures | Pipes, arches, smokestacks, parallax 0.5×. | W1 #1A2E33. W2 #15292E. | Full-width | Parallax scroll. |
| BG Layer 3 – Near detail (T2) | Dripping chains, fungi, broken signs, parallax 0.8×. | W1 #2C3E50. W2 #1E3A40. | Full-width | Parallax; drips fall 0.3 s. |
| BG Layer 4 – Foreground fog (T2) | Gradient band, bottom 96 px. | #1A2E33 20% alpha. | Full-width | Static. |
| Neon Sign (decor) | Rect frame 96×48, text shape. | Frame #2C3E50. Text #FF2D78 or #00E5FF. | 2-4/stage | Flicker 80% on / 20% off 0.1 s. Y jitter ±1. |
| Exit Gate | Rect 128×192, shutter lines ×8, stencil number. | Door #3D3D3D. Rim #FF2D78. Number #FFB347. | 1/stage | Closed static. Open: shutter slides up 0.8 s, light floods #FFB347 radial. |
| Checkpoint Totem | Pillar 32×128, orb r=16 atop. | Pillar #2C3E50. Orb #00E5FF. | 0-1/stage | Inactive: orb dim #1A2E33. Active: bright, ring pulse r=16→64, 1.5 s loop. |
| Particle – Hit spark | 6 radial lines, length 19. | #FFF→#FFB347 | 1 per hit | 0.1 s, scale 1→0. |
| Particle – Pickup sparkle | 8 tiny stars r=3, spiral out. | #FFB347, #00E5FF | 1 per pickup | 0.4 s, fade. |
| Particle – Dust (land) | 3 ellipses 16×8 at feet. | #8B7355 50%→0%. | 1 per landing | 0.25 s, drift outward. |
| Particle – Checkpoint activate | Ring + 12 rising motes. | Ring #00E5FF. Motes #FFB347. | 1 per activation | Ring r=0→160 over 0.6 s. Motes rise 64 px, 0.8 s. |

---

# 4. GAMEPLAY SPEC

**The game in one paragraph:** You are Kael, a freelance data-runner breaking into the two floors of the Helix Spire, a mega-corporation's black-site server tower. Minute to minute you run, jump, crouch through low ducts, and shoot waves of security drones, sentries, runners, mines, and shieldbots with one of four weapons, managing a small ammo pool and a regenerating shield. Each world is a floor; each stage is a sector you clear left-to-right to reach the extraction pad. Stage 5 of every world is a boss arena. The game ends after you defeat the Architect (World 2, Stage 5) and trigger the "Spire Purge" epilogue. Replayability comes from seeded level layouts, a hidden star score per stage, and NG+ scaling. 10 stages total, roughly 20-25 minutes for a skilled run.

## Records

**Player** — Kael.

| Field | Unit | Start / Range |
|---|---|---|
| x, y | px | spawn per stage (default 80, 480) |
| vx, vy | px/s | 0, 0 |
| facing | −1 or +1 | +1 |
| state | enum | "grounded"/"airborne"/"crouching"/"hurt"/"dead" |
| hp | points | 100 / max 100 |
| shield | points | 50 / max 50 |
| shieldRegenDelay | s | 0 (regen starts at 2.0) |
| crouchHeight | px | 28 (vs normal 48) |
| jumpCount | int | 0 (max 2) |
| invulnTimer | s | 0 (1.2 after hit) |
| coyoteTimer | s | 0 (0.08 when leaving ground without jump) |
| jumpBufferTimer | s | 0 (0.10 when pressing jump just before landing) |
| activeWeapon | string | "pulse_rifle" |
| lives | int | 3 |

**Weapon Roster:**

| id | display name | damage | fireRate (shots/s) | spread (°) | projSpeed (px/s) | projLife (s) | pellets | pierce | chainRadius (px) | cooldown (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| pulse_rifle | Rivet Driver | 12 | 7.0 | 3 | 700 | 1.1 | 1 | 0 | 0 | 0 |
| scatter_cannon | Scatter Cannon | 9 | 1.5 | 18 | 520 | 0.45 | 6 | 0 | 0 | 0.65 |
| rail_lance | Rail Lance | 55 | 0.8 | 0 | 1400 | 2.0 | 1 | 3 | 0 | 1.1 |
| arc_burst | Arc Burst | 14 | 4.0 | 8 | 480 | 0.8 | 1 | 0 | 90 | 0 |

**AmmoPool:**

| Weapon | Start | Max |
|---|---|---|
| pulse_rifle (shots) | 120 | 240 |
| scatter_cannon (shells) | 24 | 48 |
| rail_lance (charges) | 10 | 20 |
| arc_burst (cells) | 40 | 80 |

**Enemy Roster:**

| type | hp | vx (px/s) | damage | aggroRange (px) | attackCooldown (s) | behavior |
|---|---|---|---|---|---|---|
| drone | 24 | 100 (floats, sine bob ±12) | 10 (bullet) | 250 | 1.2 | hovers toward player, stops at 100 px, fires slow bullet (180 px/s) |
| sentry | 40 | 0 (stationary) | 15 (bullet 300 px/s) | 320 | 1.0 | rotates to face, fires aimed bullet |
| runner | 30 | 160 (ground) | 18 (contact) | 200 | 0.4 | patrols, sprints at player, lunge |
| mine | 20 | 0 (static) | 35 (AoE r=70) | 60 (proximity) | 0.6 (fuse) | detonates on proximity |
| shieldbot | 70 | 60 (shuffles) | 20 (contact) | 180 | 2.0 | front shield blocks frontal dmg; slam: 0.3 s windup, 0.2 s active, r=50, knockback 120 px/s |

**Boss records:**

| id | hp | phases | phaseTransitionHP | hitbox (px) |
|---|---|---|---|---|
| floor1_guardian (Custodian) | 600 | 3 | 400 | 80×100 |
| floor2_overseer (Architect) | 1100 | 3 | 366 | 90×120 |

**Boss Attacks – Custodian:**

| # | Trigger | Effect |
|---|---|---|
| 1 | Every 3.0 s | Slam: 2 shockwave projectiles (speed 200, dmg 20, along ground) |
| 2 | Every 5.0 s | 5 aimed bullets fan (±25°, speed 280, dmg 15) |
| 3 | Phase 2+ | Horizontal charge (speed 300, dmg 30, 1.5 s, 4 s cooldown) |
| 4 | Phase 3 | Summon 2 drones (200 px apart) every 6 s |

**Boss Attacks – Architect:**

| # | Trigger | Effect |
|---|---|---|
| 1 | Every 2.5 s | Laser sweep (400 px/s, dmg 25, 0.8 s) |
| 2 | Every 4.0 s | Drop 3 ceiling mines (fall 180 px/s, proximity 50, dmg 35) |
| 3 | Phase 2+ | Teleport random x, fire 8-bullet ring (220 px/s, dmg 12) |
| 4 | Phase 3 | Deploy 2 shieldbots + 3× ground-slam (dmg 30 each, 0.6 s gap) |

**Pickup Roster:**

| type | amount |
|---|---|
| ammo_pulse | 20 |
| ammo_scatter | 6 |
| ammo_rail | 3 |
| ammo_arc | 10 |
| health | 25 |
| shield | 20 |
| coin | 1 |

**Platform types:** "solid", "one_way", "crumble" (crumbleTimer 0→1.5 s, then removed).

**Hazard types:** "spike" (20 instant, 1.2 s invuln), "laser_gate" (25 contact, period 2.0 s: 1.0 on / 1.0 off), "acid_pool" (10/s, W2 only).

**StageProgress:** currentWorld 1-2, currentStage 1-5, lives 3, unlockedWeapons set.

**ScoreBoard:** clearTime (s), enemiesKilled (int), coinsCollected (int), stars (0-3).

---

## 4.1 Movement — **T1**

**Left / Right** (A, ←, D, →, touch joystick): set `Player.vx` toward ±280 px/s, acceleration 1800 px/s²; no key → decelerate 2400 px/s² toward 0. Cap |vx| ≤ 280 (crouching ≤ 140).

**Jump** (W, ↑, Space, touch A): if `jumpCount < 2` AND state ≠ "crouching" → `vy = −480`; `jumpCount += 1`. If crouching → un-crouch first (1 frame, no jump this press).

**Double-jump:** second press airborne, `jumpCount == 1` → `vy = −400`; `jumpCount = 2`.

**Crouch** (S, ↓, touch B held): if grounded → state "crouching", height 28, vx cap 140. Release → height 48, state "grounded". Hitbox shrinks to 28 px tall (passes under 32-px gaps).

**Gravity:** every frame `vy += 1400 × dt`. Terminal vy = 700.

**Coyote time:** when player walks off an edge (onGround → false without jump), set `coyoteTimer = 0.08`. If jump pressed while `coyoteTimer > 0` AND `jumpCount == 0`, treat as grounded jump.

**Jump buffering:** if jump pressed while airborne AND `jumpCount == 0` AND `vy > 0` (falling), set `jumpBufferTimer = 0.10`. On landing, if buffer > 0, immediately jump.

**One-way platforms:** land if `vy > 0` AND player bottom was above platform top last frame. Press S while on one-way → fall through (`vy = 60`, disable collision 0.2 s).

**Crumble platforms:** player lands → start `crumbleTimer`. At 1.5 s → remove platform, player falls.

**Level bounds:** clamp `Player.x` to [40, levelWidth − 40]. If `Player.y > levelHeight + 100` → instant death (pit).

## 4.2 Combat — **T1**

**Fire** (mouse / J / Z / touch FIRE): if `AmmoPool[activeWeapon] > 0` AND `fireCooldown ≤ 0`:
- Decrement ammo by 1.
- Spawn `pelletsPerShot` projectile(s) at muzzle offset (facing × 24 px, y − 8 standing / y − 4 crouching).
- Each: velocity = projSpeed in facing ± spread random angle (via `ctx.rng()`).
- Set `fireCooldown = 1 / fireRate`.
- Rail Lance: `recoilLockout = 0.15` (player cannot move horizontally for 0.15 s of the 1.1 s cooldown).
- Arc Burst: on projectile hit, if `chainRadius > 0`, find nearest other enemy within 90 px of impact → spawn secondary projectile toward it (damage × 0.6, one chain only, `chainUsed = true`).

**Weapon Switch** (1/2/3/4 direct, Q cycle): set `activeWeapon` to chosen id if in `unlockedWeapons`. Instant, no cost.

**Projectile update:** position += `projSpeed × dt` in direction. Remove when `projectileLife` elapsed or hits solid platform.

**Projectile vs Enemy:** subtract `damage` from `Enemy.hp`. If `pierceCount > 0`, decrement and continue; else remove. Rail Lance pierce does NOT pierce bosses (treated as 1 hit).

## 4.3 DamageAndDeath — **T1**

- Player takes damage: subtract from `shield` first, then `hp`. Set `invulnTimer = 1.2`, `shieldRegenDelay = 0`. If `hp ≤ 0` → state "dead", lives − 1, respawn at checkpoint after 1.5 s fade.
- Shield regen: if `shieldRegenDelay ≥ 2.0` AND `shield < 50` → `shield += 12/s`. Reset delay to 0 on any hit.
- Contact damage: player hitbox overlaps enemy hitbox AND `invulnTimer ≤ 0` → apply `Enemy.damage`.
- Hazard damage per type.
- Lives = 0 → "Game Over" screen → restart current world at Stage 1, full HP/shield, default ammo, lives reset to 3.

## 4.4 EnemyAI — **T1**

Per enemy, each frame:
- **Perception:** dist to player. If ≤ aggroRange → "chase". If "chase" AND dist > aggroRange × 1.4 → "patrol".
- **Patrol** (drone, runner): move at vx in patrolDir. Reverse after patrolRange (80-200 px) or platform edge.
- **Drone chase:** move toward player at 100 px/s, sine bob (amp 12, period 1.0 s). Stop at 100 px. Fire 1 bullet (180 px/s, dmg 10) every 1.2 s.
- **Sentry chase:** rotate to face. Fire aimed bullet (300 px/s, dmg 15) every 1.0 s.
- **Runner chase:** vx toward player at 160. Contact → 18 dmg, 0.4 s lunge anim, reset cooldown.
- **Mine:** static. Player center within 60 px → 0.6 s fuse → explode: 35 dmg within 70 px radius; destroy self.
- **Shieldbot chase:** shuffle toward player at 60. Frontal shield (32 px wide) blocks projectile damage; rear/above takes full. Contact 20. Slam every 2.0 s: 0.3 s windup, 0.2 s active (dmg 20, r=50, knockback 120 px/s).

## 4.5 BossAI — **T1**

- Boss stationary (or moves per attack). Player dodges and shoots.
- Phase advances at `hp ≤ phaseTransitionHP` → 1.0 s invulnerable transition flash, new attacks enabled.
- Execute attack list on timers. All attacks damage player on hitbox overlap.
- Hitbox: 80×100 (Custodian), 90×120 (Architect). Rail Lance pierce = 1 hit on boss.
- On `hp ≤ 0`: 3 s death sequence → StageFlow advances.

## 4.6 PickupAndAmmo — **T1**

- Player hitbox overlaps Pickup → apply effect, remove, play sound.
- Ammo: add `amount` to pool, cap at max. Health: `hp = min(hp+25, 100)`. Shield: `shield = min(shield+20, 50)`. Coin: increment `coinsCollected`.
- No respawn within a stage. Gone until restart.

## 4.7 LevelGenerator (Seeded) — **T1**

**Parameters:** `seed` (int), `world` (1-2), `stage` (1-5), `difficultyScale` (1.0, or 1.4 in NG+).

**Places in order:**

1. **Floor:** continuous solid at y = 480, width 3200 (stages 1-4) or 1600 (stage 5). Gaps: `gapCount = 4 + stage + world`, width 48-96 px, spaced every 300-500 px. Pit below = instant death.

2. **Mid-platforms:** `platCount = 6 + stage × 2` one_way/solid at y ∈ {320, 384, 256}, x spaced 200-400 px, w ∈ {64, 96, 128, 192}. Crumble: `crumbleCount = 2 + stage` at y = 256 only.

3. **Upper / ceilings:** `ceilCount = 3 + stage` solid at y ∈ {128, 160}, w ∈ {96, 128}, forcing crouch passages (gap height 32 px).

4. **Enemies:** `enemyCount = 5 + stage × 2 + (world × 3)`. World 1: 40% drone, 30% runner, 20% sentry, 10% mine. World 2: 20% drone, 25% runner, 25% sentry, 15% mine, 15% shieldbot. Placed at x ∈ {400…levelWidth−200}, y on nearest platform.

5. **Hazards:** `hazardCount = 2 + stage` spikes + 1 laser_gate per stage (x ∈ {800, 1600, 2400}). W2 adds 1 acid_pool in a gap.

6. **Pickups:** 2 ammo (random type, weighted toward active weapon), 1 health, 1 shield, 6-10 coins.

7. **Checkpoint:** at x = levelWidth × 0.5 (stages 3+ only).

8. **Extraction pad:** x = levelWidth − 80, y = 480. Overlap → StageFlow.

9. **Weapon unlock crates** (fixed): W1S2 → Scatter Cannon. W1S3 → Arc Burst. W1S4 → Rail Lance. W2 → ammo/health only.

**VERIFIER:** (a) No entity inside solid. (b) Every gap jumpable: max width ≤ 96 px AND platform within 120 px horizontal reach at jumpable height. (c) ≥ 1 health pickup before midpoint. (d) Crouch passages clearance ≥ 28 px. (e) No unreachable pickup (path from ground using max jump 180 px). **If any fails: re-roll seed+1, regenerate.**

## 4.8 StageFlow — **T1**

- Touch Extraction Pad → stage complete → STAGE_CLEAR screen → advance `currentStage`.
- `currentStage > 5` → advance `currentWorld`, reset `currentStage = 1`. `currentWorld > 2` → GAME_COMPLETE.
- Boss stages (5): arena 1600 px, flat floor, 4 one-way platforms at corners. No extraction pad; boss death triggers clear.
- Death: respawn at checkpoint (or stage start). Lives − 1. Lives = 0 → GAME_OVER.

## 4.9 Scoring — **T1**

- 1 star = clear. 2 stars = clear + ≥ 60% enemies killed. 3 stars = clear + ≥ 60% killed + all coins + time ≤ par_time.
- `par_time = 45 + stage × 10` s (S1 = 55, S5 = 95).
- Total stars tracked; shown on world-select and end screen.

## Progression and Difficulty — **T1**

**Unlock order:**
- Start: Pulse Rifle only, 120 ammo, 100 HP, 50 shield, 3 lives.
- W1S2: Scatter Cannon unlocked, +24 shells.
- W1S3: Arc Burst unlocked, +40 cells. Checkpoint introduced.
- W1S4: Rail Lance unlocked, +10 charges.
- W1S5: Boss 1 (Custodian, 600 HP).
- W2S1-S4: All four weapons; ammo refills to start values each stage; enemy HP × 1.2.
- W2S5: Boss 2 (Architect, 1100 HP). Game ends.

**Difficulty curve:**
- W1S1: 7 enemies, 6 gaps, 2 hazards. Learn movement + pulse rifle.
- W1S3: 11 enemies, 8 gaps, 4 hazards, checkpoint. Mines + crouch passages.
- W1S4: 13 enemies, 10 gaps, 5 hazards. Rail Lance for drone clusters.
- W2S1: 10 enemies (shieldbots), 7 gaps, 3 hazards + acid. HP × 1.2.
- W2S4: 16 enemies, 10 gaps, 6 hazards. All types mixed.
- Bosses: phase 2 adds charge/teleport; phase 3 adds summons.

**Expected failure points:** Boss phase 3 (first attempt likely death; respawn at stage start, lives − 1). Crouch-passage sequences in W2 (laser_gate; checkpoint at mid-stage). All 3 lives lost → Game Over → restart world at Stage 1.

**NG+ (T2):** Unlocked after full clear. Enemy HP × 1.4, count × 1.3, boss HP × 1.3, par_time − 20%. Ammo caps unchanged.

## Feel — **T1**

| Parameter | Value | Tuned to achieve |
|---|---|---|
| Run speed | 280 px/s | Momentum, aimable |
| Crouch speed | 140 px/s | Deliberate traversal |
| Acceleration | 1800 px/s² | Top speed in ~0.16 s |
| Deceleration | 2400 px/s² | Stop in ~0.12 s |
| Jump velocity | −480 px/s | ~180 px peak |
| Double-jump velocity | −400 px/s | Second push, not reset |
| Gravity | 1400 px/s² | Snappy arc |
| Terminal velocity | 700 px/s | Pits feel deadly |
| Coyote time | 0.08 s | Forgiving edge jumps |
| Jump buffering | 0.10 s | Press-just-before-land works |
| Pulse fire rate | 7/s (~143 ms) | Rapid, visible |
| Scatter rhythm | 1.5/s + 0.65 s cooldown | Pump-action feel |
| Rail lockout | 0.15 s of 1.1 s | Weight of the shot |
| Knockback | 120 px impulse, 0.15 s | Visible push, retains control |
| Hit flash | 0.1 s white | Readable, not obscuring |
| Invuln | 1.2 s | Reposition; not trivializing |
| Shield regen start | 2.0 s | Tension window |
| Shield regen rate | 12 pts/s | Full in ~4.2 s |
| Crumble timer | 1.5 s | Jump off; punishes lingering |
| Laser period | 2.0 s (1.0/1.0) | Readable rhythm |
| Drone bullet | 180 px/s | Dodgeable |
| Sentry bullet | 300 px/s | Requires lateral/crouch |
| Boss shockwave | 200 px/s | Jump over |
| Camera look-ahead | 120 px | See enemies coming |
| Camera dead-zone Y | ±80 px | No jitter on small hops |
| Death respawn fade | 1.5 s | Register failure; not frustrating |
| Screen shake | 4 px, 0.15 s | Impact, no nausea |

---

# 5. CHARACTERS

## Player (Kael)

**Silhouette:** Chunky, top-heavy. Broad shoulders, short legs, oversized helmet with glowing visor slit. Exo-suit with visible piston joints at knees/elbows. At a glance: "small tough thing with a big head and a big gun." Visor colour changes with equipped gun: cyan = Arc Burst, magenta = Scatter/Rail, amber = Rivet Driver.

**Facings:** Left, Right (mirrored). Crouch, jump, run states for both. No diagonal.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | 2 frames: breathe (y ±2). Head tilts 2° alternating. | 0.8 s |
| Run | 4 frames: legs alternate, body bobs y ±3, arms swing ±15°. | 0.3 s |
| Crouch | 1 pose (static). Helmet retracts 6 px into shoulders. | No loop |
| Jump (ascend) | 1 pose: body stretch 1.8×, legs tucked, arms up. | Transition |
| Jump (descend) | 1 pose: body return, legs extend forward. | Transition |
| Land | 2 frames: squash 1.2× → normal. | 0.15 s |
| Shoot (Rivet/Scatter) | 2 frames: recoil lean back 5° → return. | 0.1 s |
| Shoot (Rail Lance) | 1 pose: arms locked forward, slight lean back. | Hold during cooldown |
| Shoot (Arc Burst) | 1 pose: arms forward, coil glow. | Hold while firing |
| Hurt | 3 frames: white flash, wobble, recover. | 0.45 s |
| Death | Shatter into 8 shards. | 1.2 s, no loop |

## Drone (Dripling)

**Silhouette:** Floating teardrop, two moth-like wings. Glowing cyan body, single magenta eye. "An angry glowing raindrop."

**Facings:** Left, Right.

| Animation | Frames | Loop |
|---|---|---|
| Hover | 4 frames: wings up/mid/down/mid, body sine y ±12. | 1.0 s |
| Attack | 2 frames: stretch forward, wings back. | 0.2 s |
| Hurt | 1 frame: magenta flash, compress. | 0.1 s |
| Death | Pop: expand 1.3×, shatter into 6 droplets, fade. | 0.6 s |

## Sentry

**Silhouette:** Stationary turret on a base. Rotating barrel. "A security camera with a gun."

**Facings:** 360° rotation to face player.

| Animation | Frames | Loop |
|---|---|---|
| Idle | Barrel slowly scans left-right. | 3.0 s |
| Aim | Barrel snaps to player. | 0.1 s |
| Fire | Barrel recoil, muzzle flash. | 0.15 s |
| Hurt | White flash. | 0.1 s |
| Death | Barrel falls, sparks. | 0.4 s |

## Runner (Rust Crawler)

**Silhouette:** Low, wide, insect-like. Four legs splayed, single glowing eye on stalk. "A rusty beetle that scuttles."

**Facings:** Left, Right.

| Animation | Frames | Loop |
|---|---|---|
| Idle | 2 frames: eye stalk sways ±3°. | 1.2 s |
| Walk | 4 frames: legs alternate, body y ±2. | 0.4 s |
| Lunge (attack) | 2 frames: stretch forward, legs tuck. | 0.2 s |
| Hurt | White flash, legs tuck. | 0.1 s |
| Death | Collapse: legs fold, body flattens, fades. | 0.5 s |

## Mine

**Silhouette:** Sphere with blinking light, small legs anchoring it. "A pressure bomb."

**Facings:** N/A (static).

| Animation | Frames | Loop |
|---|---|---|
| Idle | Light blinks slowly (1 Hz). | 1.0 s |
| Proximity | Light blinks fast (5 Hz), body pulses. | 0.6 s fuse |
| Detonate | Expand to 140 px radius flash, 8 shards. | 0.3 s |

## Shieldbot

**Silhouette:** Rectangular body with a large front shield plate, single eye. "A riot-control robot."

**Facings:** Left, Right.

| Animation | Frames | Loop |
|---|---|---|
| Shuffle | 2 frames: body rocks ±2. | 0.8 s |
| Slam windup | Arms pull back. | 0.3 s |
| Slam active | Arms thrust forward, ground crack. | 0.2 s |
| Hurt (rear) | White flash, stagger. | 0.15 s |
| Hurt (front) | Shield sparks, no damage shown. | 0.1 s |
| Death | Shield falls, body crumbles. | 0.6 s |

## Boss – Custodian (Floor 1 Guardian)

**Silhouette:** Squat hydraulic press given legs. Two massive piston arms, visor slit across "face," exhaust pipes on shoulders. "A construction press that wants to flatten you."

**Facings:** Left, Right.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Steam puffs from joints every 1.5 s. Body bobs y ±3. | 2 s |
| Arm Slam | 4 frames: arm raises 96 px → descends fast → impact squash → recover. | 0.8 s |
| Charge (telegraph) | Visor pulses amber 3× over 0.6 s, body glows #FFB347. | Before attack |
| Hurt | White flash on piston joints. | 0.1 s |
| Death | Pistons explode outward (8 shards), body crumbles 2 s, steam floods screen. | 2 s |

## Boss – Architect (Floor 2 Overseer)

**Silhouette:** Floating octagonal core, four long segmented tentacle arms ending in claw pincers. Bioluminescent veins pulse. "A deep-sea jellyfish made of subway infrastructure."

**Facings:** Rotates; no fixed facing.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Arms rotate 15°/s. Core pulses cyan. | Continuous |
| Sweep | 2 arms extend in line, core flashes magenta (telegraph 0.5 s). | 1 s |
| Spin | All 4 arms extend, core spins 360° in 0.8 s. | 0.8 s |
| Hurt | Core dims 30% for 0.15 s, veins flash white. | 0.15 s |
| Death | Core cracks (4 lines), collapses inward, detonates in expanding cyan ring + 12 shards. | 2.5 s |

---

# 6. AUDIO

Generated with Web Audio API. All sounds synthesized at runtime (oscillators + noise buffers). Max 16 audio nodes alive simultaneously.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| jump | Sine, 300→600 Hz sweep, 0.12 s, env: attack 0.01, decay 0.11, sustain 0 | Player jumps (§4.1) |
| double_jump | Sine, 400→800 Hz sweep, 0.10 s, env: attack 0.01, decay 0.09 | Player double-jumps (§4.1) |
| land | Noise, 200 Hz bandpass, 0.08 s, env: attack 0.005, decay 0.075 | Player lands (§4.1) |
| crouch | Sine, 200 Hz, 0.06 s, env: attack 0.01, decay 0.05 | Player crouches (§4.1) |
| shoot_pulse | Square, 800 Hz, 0.06 s, env: attack 0.005, decay 0.055 | Pulse Rifle fires (§4.2) |
| shoot_scatter | Noise, 400 Hz lowpass, 0.15 s, env: attack 0.01, decay 0.14 | Scatter Cannon fires (§4.2) |
| shoot_rail | Sine, 100→10 Hz sweep, 0.3 s, env: attack 0.02, decay 0.28 | Rail Lance fires (§4.2) |
| shoot_arc | Triangle, 1200 Hz, 0.10 s, env: attack 0.01, decay 0.09 | Arc Burst fires (§4.2) |
| arc_chain | Sine, 1600→800 Hz, 0.08 s, env: attack 0.005, decay 0.075 | Arc Burst chain hit (§4.2) |
| hit_enemy | Square, 200 Hz, 0.05 s, env: attack 0.005, decay 0.045 | Projectile hits enemy (§4.2) |
| enemy_die | Noise, 100 Hz, 0.2 s, env: attack 0.01, decay 0.19 | Enemy killed (§4.4) |
| player_hit | Sine, 150 Hz, 0.15 s, env: attack 0.01, decay 0.14 | Player takes damage (§4.3) |
| player_die | Sine, 400→50 Hz, 0.6 s, env: attack 0.01, decay 0.59 | Player HP reaches 0 (§4.3) |
| pickup_health | Sine, 600→900 Hz, 0.15 s, env: attack 0.01, decay 0.14 | Health pickup (§4.6) |
| pickup_ammo | Sine, 500 Hz, 0.08 s, env: attack 0.005, decay 0.075 | Ammo pickup (§4.6) |
| pickup_coin | Sine, 1000 Hz, 0.06 s, env: attack 0.005, decay 0.055 | Coin pickup (§4.6) |
| checkpoint | Sine, 400→800 Hz, 0.3 s, env: attack 0.02, decay 0.28 | Checkpoint touched (§4.7) |
| stage_clear | Sine chord (400+600+800), 0.5 s, env: attack 0.05, decay 0.45 | Stage cleared (§4.8) |
| boss_phase | Square, 80 Hz, 0.4 s, env: attack 0.02, decay 0.38 | Boss phase transition (§4.5) |
| boss_die | Noise + Sine, 60→20 Hz, 1.0 s, env: attack 0.05, decay 0.95 | Boss defeated (§4.5) |
| weapon_switch | Sine, 700 Hz, 0.05 s, env: attack 0.005, decay 0.045 | Weapon switched (§4.2) |
| mine_fuse | Square, 300 Hz, repeating 0.1 s × 6 | Mine proximity fuse (§4.4) |
| mine_explode | Noise, 80 Hz, 0.3 s, env: attack 0.005, decay 0.295 | Mine detonates (§4.4) |
| game_over | Sine, 300→100 Hz, 1.0 s, env: attack 0.05, decay 0.95 | Lives = 0 (§4.3) |
| game_complete | Sine chord (400+500+600+800), 1.5 s, env: attack 0.1, decay 1.4 | Game complete (§4.8) |

---

# 7. UX

HTML and CSS only for overlays; canvas for game render. Screens as a state machine:

```
TITLE → WORLD_SELECT → STAGE_PLAY ⇄ PAUSE
STAGE_PLAY → STAGE_CLEAR → (next stage STAGE_PLAY | WORLD_SELECT)
STAGE_PLAY → (lives=0) → GAME_OVER → WORLD_SELECT
STAGE_PLAY → (W2S5 boss dead) → GAME_COMPLETE → TITLE
```

**TITLE:** "GRIDFALL" in stencil font (#FFB347), subtitle "THE SPIRE AWAITS" (#00E5FF), "PRESS ENTER / TAP TO START" pulsing magenta. BG: parallax layers 1-2 visible, neon sign flickering. Vignette + grain (T2) active. Enter/Tap → WORLD_SELECT.

**WORLD_SELECT:** 2×5 grid of stage nodes. World 2 locked until W1S5 cleared. Each node shows earned stars (0-3). Arrow keys/tap navigate. Enter → STAGE_PLAY. Escape → TITLE.

**STAGE_PLAY:** Gameplay canvas + HUD overlay. Stage-intro banner: "WORLD 1 – STAGE 1 / THE RUSTBELT" slides in from top 0.6 s, holds 1.5 s, fades 0.4 s. Escape → PAUSE.

**PAUSE (overlay):** "PAUSED". Resume (Escape/Enter), Restart Stage (R), Quit to World Select (Q). Escape → resume.

**STAGE_CLEAR:** Stage name, clear time, enemies killed %, coins, stars (1-3 animated). "Press Enter to continue." Enter → next stage or WORLD_SELECT if boss.

**GAME_OVER:** "SYSTEM FAILURE — Lives exhausted." Stage reached. "Press Enter to restart world." Enter → WORLD_SELECT at stage 1 of current world.

**GAME_COMPLETE:** "SPIRE PURGE COMPLETE." Total stars (max 30). "Press Enter to return to title." Enter → TITLE.

**HUD table:**

| Element | Record field | When visible |
|---|---|---|
| HP bar (left, 120 px wide, green→red gradient) | `Player.hp / 100` | Always in STAGE_PLAY |
| Shield bar (below HP, blue, 120 px) | `Player.shield / 50` | Always (dimmed if 0) |
| Lives counter (3 small icons, top-left) | `StageProgress.lives` | Always |
| Weapon name + ammo count (bottom-left) | `Player.activeWeapon` + `AmmoPool[activeWeapon]` | Always |
| Weapon icon row (4 slots, active ringed cyan) | `Player.weapons` | Always; locked slots show "?" |
| Stage indicator (top-center "W1-S3") | `Level.world / Level.stage` | Always |
| Timer (top-right, counts up) | `ScoreBoard.clearTime` | Always |
| Coin count (top-right, below timer) | `ScoreBoard.coinsCollected` | Always |
| Boss HP bar (top-center, wide) | `Boss.hp / Boss.maxHp` | Boss stage only, from arena entry |
| Checkpoint flash ("CHECKPOINT" text) | Triggered on touch | 1.0 s on activation |
| Low-ammo warning (weapon icon pulses red) | `AmmoPool[activeWeapon] ≤ 10%` max | While condition true |
| Low-health warning (HP bar pulses, vignette darkens) | `Player.hp ≤ 25` | While condition true |

---

# 8. DEBUG API

Installed by `debug.js` as `window.__game`. All calls synchronous, return plain data, never touch DOM.

| Call | What it does | Returns |
|---|---|---|
| `__game.start()` | title → play, loads stage 1-1, inits player. | void |
| `__game.step(dt, n)` | Runs exactly `n` fixed ticks of `dt` each (tick order §1.1), draws once. | void |
| `__game.setTime(t)` | Runs ticks until `ctx.time ≥ t`, no drawing. | void |
| `__game.seed(n)` | Reseeds rng, calls `level.load(ctx,1,1)`, resets player and pools. | void |
| `__game.getState()` | Deep-clone of all ctx fields (minus canvas, ctx2d, rng fn). | object |
| `__game.move(dir)` | Sets `ctx.input.moveDir = dir` (−1, 0, +1). Persists. | void |
| `__game.jump()` | Sets `ctx.input.jumpPressed = true` for next tick. | void |
| `__game.crouch(on)` | Sets `ctx.input.crouchHeld = on`. | void |
| `__game.fire(on)` | Sets `ctx.input.fireHeld = on`; `firePressed = true` if transitioning to on. | void |
| `__game.switchWeapon()` | Sets `ctx.input.switchNext = true`. | void |
| `__game.selectSlot(n)` | Sets `ctx.input.weaponSlot = n` (1-4). | void |
| `__game.spawnEnemy(type, x, y, dir)` | Calls `enemies.spawn`. | `{id,x,y,type,alive}` |
| `__game.spawnProjectile(weaponId, x, y, vx, vy)` | Pulls from pool, configures. | `{id,x,y,alive}` |
| `__game.skipToStage(w, s)` | `level.load(ctx,w,s)`, reset player, state = 'play'. | `{world,stage,spawnX,spawnY}` |
| `__game.setField(path, value)` | Sets ctx field at dotted path. | void |
| `__game.getFrameCount()` | Returns `ctx.frame`. | number |
| `__game.getDrawCalls()` | Canvas draw ops from last draw. | number |
| `__game.getStateHash()` | 32-bit hash of getState() JSON. | number |
| `__game.getMovementState()` | Returns `{x,y,vx,vy,onGround,crouching,jumpCount,coyoteTimer,state}`. | object |
| `__game.getCombatState()` | Returns `{activeWeapon,ammo:{...},fireCooldown,recoilLockout,projectilesAlive}`. | object |
| `__game.getEnemyState(id)` | Returns full enemy record by pool index. | object or null |
| `__game.getBossState()` | Returns boss record or null. | object or null |
| `__game.getPickupState()` | Returns array of remaining pickups `{type,x,y,amount,collected}`. | array |
| `__game.getLevelState()` | Returns `{world,stage,width,height,spawnX,spawnY,exitX,exitY,platformCount,enemyCount,hazardCount,pickupCount}`. | object |
| `__game.getProgressionState()` | Returns `{stagesCleared,stars,unlockedWorld,ngPlus,difficultyScale}`. | object |
| `__game.getScoreboard()` | Returns `{clearTime,enemiesKilled,totalEnemies,coinsCollected,stars}`. | object |
| `__game.triggerCheckpoint()` | Forces checkpoint activation at current player position. | void |
| `__game.killBoss()` | Sets boss hp to 0, triggers death sequence. | void |
| `__game.pause(on)` | Sets `ctx.input.pause = on`. | void |
| `__game.restart()` | Sets `ctx.input.restart = true`. | void |
| `__game.confirm()` | Sets `ctx.input.confirm = true` (menu confirm). | void |

**Determinism guarantee:** Same `seed(n)` + same `__game.*` call sequence → `getState()` byte-identical. No wall-clock or `Math.random()` reads.

---

# 9. TESTS

All tests drive exclusively through `window.__game`. Numbered in execution order.

### T1 – Title → Play
```
__game.seed(42); __game.start()
s = __game.getState()
```
Assert: `s.state === 'play'`, `s.level.world === 1`, `s.level.stage === 1`, `s.player.x === s.level.spawnX` (80), `s.player.y === s.level.spawnY` (480).

### T2 – Fixed-timestep movement (right)
```
__game.seed(42); __game.start()
__game.move(1); __game.step(1/60, 60)
p = __game.getState().player
```
Assert: `p.x > 80 + 280 * 0.9` (≥ 332), `p.onGround === true`, `p.facing === 1`.

### T3 – Jump physics
```
__game.seed(42); __game.start()
__game.jump(); __game.step(1/60, 1)
p = __game.getState().player
```
Assert: `p.vy < 0` (upward in Y-down), `p.onGround === false`, `p.state === 'airborne'`.

### T4 – Crouch changes hitbox
```
__game.seed(42); __game.start()
h0 = __game.getState().player.h  // 48
__game.crouch(true); __game.step(1/60, 1)
h1 = __game.getState().player.h
```
Assert: `h1 === 28`, `__game.getState().player.crouching === true`.

### T5 – Fire weapon (slot 1, pulse_rifle)
```
__game.seed(42); __game.start()
__game.selectSlot(1); __game.fire(true); __game.step(1/60, 1)
pr = __game.getState().projectiles.filter(p => p.alive)
```
Assert: `pr.length >= 1`, `pr[0].x > __game.getState().player.x`, `pr[0].vx > 0`, `pr[0].weaponId === 'pulse_rifle'`.

### T6 – All 4 weapon types fire
```
__game.seed(42); __game.start()
// unlock all weapons for test
__game.setField('player.weapons', ['pulse_rifle','scatter_cannon','rail_lance','arc_burst'])
__game.setField('player.ammo.scatter_cannon', 24)
__game.setField('player.ammo.rail_lance', 10)
__game.setField('player.ammo.arc_burst', 40)
ids = []
for slot in [1,2,3,4]:
    __game.selectSlot(slot); __game.fire(true); __game.step(1/60, 2)
    pr = __game.getState().projectiles.filter(p => p.alive)
    if pr.length > 0: ids.add(pr[0].weaponId)
```
Assert: `ids` contains at least 4 distinct weapon ids.

### T7 – Weapon switch
```
__game.seed(42); __game.start()
__game.setField('player.weapons', ['pulse_rifle','scatter_cannon'])
w0 = __game.getState().player.activeWeapon
__game.switchWeapon(); __game.step(1/60, 1)
w1 = __game.getState().player.activeWeapon
```
Assert: `w1 !== w0`, `w1 === 'scatter_cannon'`.

### T8 – Enemy spawn & existence
```
__game.seed(42); __game.start()
e = __game.spawnEnemy('runner', 300, 480, -1)
__game.step(1/60, 1)
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length >= 1`, `en[0].type === 'runner'`, `en[0].x === 300`.

### T9 – Projectile kills enemy
```
__game.seed(42); __game.start()
__game.setField('player.weapons', ['pulse_rifle','scatter_cannon','rail_lance','arc_burst'])
__game.setField('player.ammo.rail_lance', 10)
__game.selectSlot(3)  // rail_lance, 55 dmg, 1400 px/s
e = __game.spawnEnemy('drone', 400, 400, -1)  // drone hp 24
__game.fire(true); __game.step(1/60, 30)  // 0.5 s, projectile travels 700 px
en = __game.getState().enemies.filter(x => x.alive && x.type === 'drone')
```
Assert: `en.length === 0` (drone killed by 55 dmg > 24 hp).

### T10 – Player takes damage
```
__game.seed(42); __game.start()
hp0 = __game.getState().player.hp  // 100
sh0 = __game.getState().player.shield  // 50
__game.spawnEnemy('runner', 100, 480, 1)  // right at player
__game.step(1/60, 30)
p = __game.getState().player
```
Assert: `p.shield < sh0` (shield absorbs first), `p.invulnTimer > 0`, `p.state === 'hurt'`.

### T11 – Stage clear → advance
```
__game.seed(42); __game.start()
__game.setField('player.x', __game.getState().level.exitX)  // 3120
__game.setField('player.y', __game.getState().level.exitY)  // 480
__game.step(1/60, 10)
s = __game.getState()
```
Assert: `s.level.stage === 2`, `s.level.world === 1`, `s.progression.stagesCleared` includes `"1-1"`.

### T12 – World progression (2 worlds × 5 stages)
```
__game.seed(42); __game.start()
for w in [1,2]:
    for st in [1..5]:
        __game.skipToStage(w, st)
        if st === 5:
            __game.killBoss(); __game.step(1/60, 200)
        else:
            __game.setField('player.x', __game.getState().level.exitX)
            __game.setField('player.y', __game.getState().level.exitY)
            __game.step(1/60,