# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Side-scrolling platformer | §4 Movement, §3 The Space, §1.1 axes |
| Shooter | §4 Combat, §4 Weapon Roster |
| At least 4 different gun types | §4 Weapon Roster (exactly 4: Pulse Rifle, Scatter Cannon, Rail Lance, Arc Burst) |
| Character can jump | §4 Movement (single + double jump) |
| Character can move left or right | §4 Movement (Left/Right rules) |
| Character can crouch | §4 Movement (Crouch rule), §5 Player crouch pose |
| Worlds and stages (Mario-like progression) | §4 StageFlow, §4 Progression (2 worlds × 5 stages) |
| Start with 2 worlds, 5 stages each | §4 StageFlow (W1-S1 … W2-S5, 10 stages total) |
| Do not simply copy Mario | §0.2 ruling: cyberpunk/neon-wasteland skin, double-jump, shield regen, ammo management, seeded layouts, boss phases — none of which Mario has |
| *(added)* Shield regen for skill expression | §4 DamageAndDeath |
| *(added)* Seeded level generation for replayability | §4 LevelGenerator |
| *(added)* Star scoring and NG+ | §4 Scoring, §4 Progression |
| *(added)* Touch controls for mobile | §1.2 Controls |
| *(added)* Web Audio generated SFX | §6 Audio |
| *(added)* Screen shake, particles, parallax | §3 Lighting/Post, §4 Feel, §5 Animations |

## 0.2 Decisions

| Topic | gameplay.md said | visual.md said | engineering.md said | Ruling & why |
|---|---|---|---|---|
| Canvas / viewport | 960×540 implied (level 560 tall) | 960×540 base resolution | 1280×720 CSS px | **1280×720.** Engineering owns the canvas; the extra headroom lets the 560-px level sit comfortably with UI chrome. |
| Y-axis convention | Y-down (ground y=480, gravity vy+=1400) | Y-up implied ("up is positive") | Y-up (ground y=0, gravity −Y) | **Y-down.** Gameplay wrote every number in Y-down; flipping 40+ values invites bugs. Canvas default is Y-down, so no `scale(1,-1)` transform is needed. Engineering's R1 risk is eliminated. |
| Tile size | Implied 32 px (platform h=16/32, crouch gap=32) | "Tiles are 1×1 unit" (ambiguous) | `<TILE_SIZE>` placeholder | **32 px.** Fills engineering's placeholder from gameplay's geometry. |
| Player hitbox | crouchH=28, normal H=48; width not stated | 2×3 "units" | `<PLAYER_W>`, `<PLAYER_H>` | **W=24, H=48, crouchH=28.** Gameplay's muzzle offset (facing×24) implies 24-px width. |
| Player HP model | 100 numeric HP + 50 numeric shield | 3 hearts | `<PLAYER_MAX_HP>` | **100 HP + 50 shield, numeric.** Hearts are a visual shorthand (see §7 HUD). |
| Weapon set | Pulse Rifle, Scatter Cannon, Rail Lance, Arc Burst | Rivet Driver, Scatter Cannon, Arc Welder, Mortar Launcher | "≥4 types" | **Gameplay's 4** (full stat tables exist). Visual recipes are re-skinned to match (see §3 Recipes, §6). |
| Enemy roster | drone, sentry, runner, mine, shieldbot (5) | Rust Crawler, Dripling (2 + 2 bosses) | "grunt" in tests | **Gameplay's 5.** Visual's Rust Crawler → Runner; Dripling → Drone. Recipes for Sentry, Mine, Shieldbot authored in §5. |
| Boss names | Custodian (F1), Architect (F2) | Press Golem (W1), Reservoir Warden (W2) | — | **Visual's names** (more evocative of the look); gameplay's HP/attacks/stats carry. |
| World names | "Helix Spire floors" | "The Rustbelt" (W1), "The Undercity" (W2) | — | **Visual's names.** Gameplay's "Spire" lore is the thin narrative wrapper. |
| Stage generation | Seeded generator, reshuffles per run | Hand-placed fixed layouts | — | **Seeded generator** (gameplay). Visual's layout table is converted to px regions the generator fills. |
| Stage width | 3200 px (S1-4), 1600 px (S5 boss) | 240 "units" | ≤6400 px budget | **3200 / 1600 px** from gameplay; well within engineering's 6400 cap. |
| Level height | 560 px | 24 "units" (20 visible + 4 dead air) | ≤2560 px budget | **560 px.** Entire level fits inside the 720-px viewport vertically; no vertical scroll needed (camera Y dead-zone handles tall jumps). |
| Extraction mechanic | Touch Extraction Pad at right edge | Collect Stage Key → reach Exit Gate | — | **Gameplay's pad** (simpler, one interaction). Visual's Exit Gate shutter is the pad's look. |
| Screen shake magnitude | 4 px, 0.15 s | 0.3 "units", 0.2 s | — | **4 px / 0.15 s** (gameplay's explicit px). |
| Fire input keys | J / mouse click / touch FIRE | — | J / Z / Enter | **J, Z, mouse click.** Enter is reserved for menu confirm (gameplay's screen machine). |
| Weapon cycle key | Q | — | K / X | **Q or K** both cycle forward. 1/2/3/4 direct-select. |
| Pause key | Escape | — | Escape / P | **Escape or P.** |
| Boss arena platforms | 4 one-way platforms at corners | 3 layers of platforms, concentric rings | — | **Gameplay's 4 one-way** for W1 boss; **visual's concentric rings** for W2 boss (Reservoir Warden). |
| Conveyor platforms | Not mentioned | Visual-only scrolling chevrons | — | **T2 cosmetic** variant of solid platform; no speed effect. |
| Coyote / jump-buffer | 0.08 s / 0.10 s | Not mentioned | Not mentioned | **Keep gameplay's values** (feel parameters). |
| NG+ | Enemy HP×1.4, count×1.3, boss HP×1.3 | Not mentioned | Not mentioned | **T3 stretch goal.** |
| Lives model | 3 lives, lose all → Game Over → restart world | "3 magenta hearts" in HUD | `<PLAYER_LIVES>` | **3 lives, numeric.** Hearts in HUD are a visual representation of lives (not HP). |
| Ammo pool | Per-weapon named entries (pulse_rifle:120/240 etc.) | Ammo Crate pickup | `player.ammo[0..4]` | **Named entries** in a sub-object; `player.ammo` array indexes by weapon slot for fast access. |
| Shield regen | Delay 2.0 s, rate 12/s, max 50 | Not mentioned | Not mentioned | **Keep gameplay's shield system** verbatim. |

## 0.3 Tiers

**T1 – Must ship (the playable game):**
- Movement (run, jump, double-jump, crouch, gravity, coyote, buffering)
- Combat (4 weapons, firing, projectiles, damage, ammo)
- Weapon switch
- DamageAndDeath (HP, shield, lives, respawn, invulnerability)
- EnemyAI (5 types, patrol/chase/attack)
- BossAI (2 bosses, 3 phases each)
- PickupAndAmmo
- LevelGenerator (seeded, with verifier)
- StageFlow (10 stages, world advance, game complete)
- Camera (follow, dead-zone, clamp)
- HUD + all screens (title, world-select, stage-play, pause, stage-clear, game-over, game-complete)
- Audio (generated SFX)
- Particles + screen shake
- Parallax background (3 layers)
- Fixed-timestep loop, deterministic RNG
- Touch controls (basic)

**T2 – Polish (add after T1 is complete):**
- Crumble platforms with shard animation
- Conveyor platform cosmetic chevrons
- 4th parallax layer (stage-dependent)
- Neon sign flicker + light-source tinting
- Chromatic aberration at low HP
- Film grain overlay
- Checkpoint activation ring + motes
- Stage-intro banner animation
- Exit-gate shutter open animation + confetti
- Low-ammo warning pulse
- Boss phase-transition white flash + roar shake

**T3 – Stretch (post-ship):**
- NG+ mode (HP×1.4, count×1.3, par_time−20%)
- Full 4-layer parallax with stage-count scaling
- Acid-pool hazard (W2)
- Bioluminescent moss breathing lights (W2)
- New Game+ seed display on title
- ScoreBoard persistence to localStorage

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Item | Rule |
|---|---|
| 1 unit | 1 logical pixel. Canvas is **1280 × 720** CSS px, `devicePixelRatio = 1`. |
| Game-logic axes | **X** → right positive. **Y** → **down** positive (ground plane at y = 480 for a 560-px-tall level). Gravity pulls +Y. |
| Render axes | Identical to game-logic axes (canvas default Y-down). **No `scale(1,-1)` transform.** |
| Origin (world) | Top-left corner of the level bounding box: (0, 0). Level spans x ∈ [0, levelWidth], y ∈ [0, 560]. |
| Tile size | **32 px**. Grid is `ceil(levelWidth/32) × ceil(560/32)` tiles. |
| Camera | `camera.x` = left edge of viewport in world px; `camera.y` = top edge. Viewport 1280 × 720 (but level is only 560 tall, so camera.y is clamped to [0, 0] for most stages; it activates only if a boss arena or tall section exceeds viewport). Clamped to level bounds. |
| Fixed timestep | `DT = 1/60 ≈ 0.016666667 s`. Accumulator clamps to max **5** catch-up ticks per rAF callback; excess is discarded. |
| Tick order | `input → physics → player → weapons → enemies → particles → camera → progression → audio` (then `renderer.draw()` once). |
| Random source | One seeded PRNG: `mulberry32(seed)`, exposed as `ctx.rng()` returning `[0,1)`. No `Math.random()`, `crypto`, `Date.now()` in game logic. Renderer/audio may use `Math.random()` for cosmetic-only jitter never read back. |

## 1.2 Important conventions

**Controls table (authoritative):**

| Input | Action (STAGE_PLAY) | Action (Menus) |
|---|---|---|
| A / ← | Move left (held) | Navigate left |
| D / → | Move right (held) | Navigate right |
| W / ↑ / Space | Jump (edge-triggered) | Confirm |
| S / ↓ | Crouch (held) | Navigate down |
| J / Z / mouse click / touch FIRE | Fire (held = auto-repeat; edge = single shot for semi) | — |
| 1 / 2 / 3 / 4 | Select weapon slot 1–4 | — |
| Q / K | Cycle weapon forward | Quit to World Select (in Pause) |
| Escape / P | Pause / Resume | Back |
| R | Restart stage (in Pause) | — |
| Enter | — | Confirm |
| Touch left-half hold/swipe | Move (analog by distance from centre) | — |
| Touch right-top tap | Jump | — |
| Touch right-bottom hold | Fire | — |
| Touch right-middle hold | Crouch | — |
| Touch two-finger tap | Cycle weapon | — |

All keyboard bindings are **both** WASD and arrow keys simultaneously. Touch events synthesise into the same `ctx.input` object; no game code branches on input device.

**Conventions:**
- Player position `(x, y)` refers to the **bottom-centre** of the hitbox (feet).
- Facing: `+1` = right, `−1` = left.
- All velocities in px/s, all times in seconds, all damage in points.
- "Alive" entities have `alive === true`; dead entities are recycled in-place (no array splice).
- A "tick" = one fixed-step update of DT seconds.

---

# 2. CONTRACTS

## 2.1 Module layout

| Module | Responsibility |
|---|---|
| `game.js` | Boot, top-level state machine, rAF loop, calls every module in tick order. |
| `input.js` | Reads `keydown/keyup/touch*`, writes `ctx.input`. Normalises keyboard + touch. |
| `physics.js` | AABB tile collision, entity-vs-entity collision, gravity integration, ground detection. Pure geometry. |
| `player.js` | Player entity: state machine, movement, jump, crouch, hitbox, invuln, respawn. |
| `weapons.js` | Weapon definitions (4 types), fire logic, projectile pool, damage application, chain/pierce. |
| `enemies.js` | Enemy definitions (5 types), per-type AI tick, spawn, death, drops. |
| `level.js` | Seeded generator: builds tile arrays, entity spawns, pickups, hazards, extraction pad per stage. Provides `isSolid`, `isHazard`, `tileAt`. |
| `camera.js` | Viewport rect, dead-zone follow, clamp to level bounds. |
| `particles.js` | Ring-buffer pool of particle structs; spawn, update, query-alive for renderer. |
| `audio.js` | Web Audio API: oscillator/noise SFX, simple music. Drains `ctx.audioQueue`. Never reads game state back. |
| `progression.js` | World/stage index, unlock table, score, star calc, stage-clear / game-over / game-complete conditions. |
| `ui.js` | HUD, title screen, world-select, pause overlay, stage-clear, game-over, game-complete. Draws into canvas. |
| `debug.js` | Installs `window.__game`. Imported only in debug builds. |

## 2.2 Global context

```js
const ctx = {
  // ---- environment ----
  canvas: null,
  ctx2d: null,
  seed: 0,
  rng: null,
  dt: 0.016666667,
  time: 0,
  frame: 0,
  running: true,
  state: 'title',  // 'title'|'world-select'|'play'|'pause'|'stage-clear'|'game-over'|'game-complete'

  // ---- input ----
  input: {
    moveDir: 0,
    jumpPressed: false,
    jumpHeld: false,
    crouchHeld: false,
    firePressed: false,
    fireHeld: false,
    switchNext: false,
    weaponSlot: 0,       // 0 = none, 1-4 = slot
    pause: false,
    restart: false,
    touch: null,
  },

  // ---- player ----
  player: {
    x: 80, y: 480,
    vx: 0, vy: 0,
    w: 24, h: 48,
    facing: 1,
    onGround: false,
    crouching: false,
    state: 'grounded',   // 'grounded'|'airborne'|'crouching'|'hurt'|'dead'
    hp: 100,
    maxHp: 100,
    shield: 50,
    maxShield: 50,
    shieldRegenDelay: 0,
    jumpCount: 0,
    invulnTimer: 0,
    coyoteTimer: 0,
    jumpBufferTimer: 0,
    activeWeapon: 'pulse_rifle',
    weaponIndex: 0,
    shootCooldown: 0,
    recoilLockout: 0,
    lives: 3,
    respawnTimer: 0,
  },

  // ---- ammo pool ----
  ammoPool: {
    pulse_rifle:    { current: 120, max: 240 },
    scatter_cannon: { current: 24,  max: 48  },
    rail_lance:     { current: 10,  max: 20  },
    arc_burst:      { current: 40,  max: 80  },
  },

  // ---- unlocked weapons ----
  unlockedWeapons: ['pulse_rifle'],

  // ---- projectiles (pool) ----
  projectiles: [],
  projectilePoolSize: 256,

  // ---- enemies (pool) ----
  enemies: [],
  enemyPoolSize: 64,
  enemyAliveCap: 40,

  // ---- boss (present only in stage 5) ----
  boss: null,  // {id, hp, maxHp, phases, currentPhase, phaseTransitionHP, x, y, w, h, attackTimers:[...], alive}

  // ---- pickups (per-stage list) ----
  pickups: [],

  // ---- particles (ring buffer) ----
  particles: [],
  particlePoolSize: 1024,

  // ---- level ----
  level: {
    world: 1,
    stage: 1,
    width: 3200,
    height: 560,
    tiles: null,          // Uint8Array
    widthTiles: 0,
    heightTiles: 0,
    spawnX: 80, spawnY: 480,
    exitX: 3120, exitY: 480,
    checkpointX: 0,       // 0 = no checkpoint
    checkpointActivated: false,
    entitySpawns: [],
    hazardSpawns: [],
    pickupSpawns: [],
    platforms: [],        // {x,y,w,h,type,crumbleTimer,removed}
    bgParallax: 0.3,
    isBossStage: false,
  },

  // ---- camera ----
  camera: { x: 0, y: 0, w: 1280, h: 720, lookAhead: 120, deadZoneY: 80 },

  // ---- progression / scoring ----
  progression: {
    score: 0,
    totalStages: 10,
    unlockedWorld: 1,
    stagesCleared: [],
    stars: {},            // "W-S" → 0-3
    totalStars: 0,
  },
  scoreboard: {
    clearTime: 0,
    enemiesKilled: 0,
    totalEnemies: 0,
    coinsCollected: 0,
    stars: 0,
  },

  // ---- screen shake ----
  shake: { x: 0, y: 0, intensity: 0, timer: 0 },

  // ---- audio queue ----
  audioQueue: [],
};
```

## 2.3 Module specifics

**`game.js` exports:** `boot(canvas, seed)`, `setState(state)`, `loop(timestamp)`

**`input.js` exports:** `init(ctx)`, `update(ctx, dt)`, `reset(ctx)`

**`physics.js` exports:** `init(ctx)`, `update(ctx, dt)`, `isSolid(ctx, tx, ty)`, `isHazard(ctx, tx, ty)`, `tileAt(ctx, wx, wy)`, `resolveAABB(a, b)`

**`player.js` exports:** `init(ctx)`, `update(ctx, dt)`, `hurt(ctx, dmg)`, `respawn(ctx)`, `getHitbox(ctx)`

**`weapons.js` exports:** `init(ctx)`, `update(ctx, dt)`, `fire(ctx, weaponId)`, `getWeaponDef(id)`, `switchWeapon(ctx, dir)`, `selectSlot(ctx, n)`

**`enemies.js` exports:** `init(ctx)`, `update(ctx, dt)`, `spawn(ctx, type, x, y, dir)`, `kill(ctx, enemy)`

**`level.js` exports:** `init(ctx)`, `update(ctx, dt)`, `load(ctx, world, stage, seed)`, `isSolid(ctx, tx, ty)`, `isHazard(ctx, tx, ty)`, `tileAt(ctx, wx, wy)`

**`camera.js` exports:** `init(ctx)`, `update(ctx, dt)`

**`particles.js` exports:** `init(ctx)`, `update(ctx, dt)`, `spawn(ctx, x, y, vx, vy, life, color, size)`, `getAlive(ctx)`

**`audio.js` exports:** `init(ctx)`, `update(ctx, dt)`, `play(ctx, id)`

**`progression.js` exports:** `init(ctx)`, `update(ctx, dt)`, `advance(ctx)`, `restart(ctx)`, `calcStars(ctx)`

**`ui.js` exports:** `init(ctx)`, `draw(ctx, c2d)`

**`debug.js` exports:** `install(ctx)` → sets `window.__game` (see §8)

---

# 3. VISUAL SPEC

**The look:** 2D, side-scrolling, fixed zoom, no rotation. A neon-soaked post-industrial wasteland: a lone scavenger in a battered exo-suit blasts through the skeletal remains of a drowned mega-city. Palette: deep oxidized teal `#1A2E33` and rust-orange `#C45A2D` as ground truth, punctuated by electric cyan `#00E5FF` and hot magenta `#FF2D78` from gunfire, signage, and bioluminescence. Mood: "gritty Saturday-morning cartoon"—chunky readable shapes, bold 3-pixel black outlines, exaggerated squash-and-stretch on every impact. The screenshot that sells it: the player mid-air, crouching-then-jumping off a rusted conveyor belt, magenta plasma bolt streaking right, a two-story enemy robot reeling with a cyan hit-flash, parallax layers of dripping pipes and flickering neon signs visible behind, all in thick 3-px black outlines over flat saturated fills.

**Lighting and atmosphere:** Very low ambient (`#0F1B1F` at 25%). Light sources are diegetic: sodium lamp posts (`#FFB347`, radius 8 units→256 px), neon signs (flicker 80% on / 20% off), checkpoint orbs (pulse 4→6→4 units, 2 s), muzzle flashes (instantaneous, 0.06 s, colour per gun), bioluminescent moss in W2 (`#00E5FF`, slow 4 s breathe), boss-arena spotlight (`#FFFFFF` 60%, radius 12 units→384 px), exit-gate flood (`#FFB347`, radial 0.8 s ramp). Background layers 1–2 darkened 40% vs foreground. W2 adds a vertical fog band (`#15292E`, 30% alpha) at 60% height. Boss arenas drop global ambient to 10%. Post effects: vignette (40% edge darkening, always on), screen shake (4 px, 0.15 s, linear decay), hit flash (1-frame `#FF2D78` 15% alpha), chromatic aberration (0.02 px red/blue split at HP < 25, constant), grain (3% monochrome, 24 fps refresh), radial flash on checkpoint (white ring 0.4 s 30%), desaturation on death (→20% colour over 0.8 s).

**The space:** Coordinate system is Y-down, origin top-left of level. Stage geometry: 3200 × 560 px (stages 1–4) or 1600 × 560 px (boss stage 5). Ground plane at y = 480. Viewport 1280 × 720; the level fits within the viewport height, so camera.y stays at 0 unless a tall boss arena section is added. Regions (in px): Spawn ledge 0–160 (flickering lamp, start banner, warm sodium pool). Mid-traversal 160–2800 (platforms, pits, enemies, pickups, hazards; ground texture changes every 400 px). Checkpoint at x = 1600 (stage 3+; glowing totem). Boss arena 0–1600 (enclosed, 4 one-way platforms at corners for W1; concentric ring platforms for W2; lighting 10%, single overhead spotlight, ceiling drops). Extraction pad / Exit Gate at x = levelWidth − 80, y = 480 (shutter door, magenta rim-light, stage-number stencil).

**World 1 – "The Rustbelt":** Corrugated steel plates, broken concrete. BG: smokestacks, hanging chains, conveyor machinery. Palette rust-orange dominant. Boss arena: hydraulic press room, ceiling at y = 80, floor grate over boiling oil.

**World 2 – "The Undercity":** Cracked tile, flooded shallow channels (32 px deep, ankle-high). BG: dripping brick arches, subway tunnels, bioluminescent moss. Palette deep teal dominant with magenta/cyan fungi. Boss arena: drained reservoir with concentric ring platforms.

**Stage progression visual cue:** Each stage number adds one more BG parallax layer and one more colour accent. Stage 1: 2 layers, 2 accents. Stage 5: 4 layers, 4 accents.

**Generated vs. skin:** Stage geometry is seeded-generated (see §4 LevelGenerator). Visual recipes skin the generated output. The generator guarantees: gaps ≤ 96 px, jumps ≤ 180 px height, crouch passages ≥ 28 px clearance, path from ground to every pickup.

**Recipe table:**

| Name | Shapes & Size (px) | Colours (hex) | Count | Motion / Effect |
|---|---|---|---|---|
| Player – idle | Rounded rect body 24×48, circle head r=17 atop, 2 stub arms, 2 stub legs. 3px black outline. | Suit `#2C3E50`, visor `#00E5FF`, accents `#FF2D78` | 1 | 2-frame breathing bob y±3 px, 0.8 s cycle |
| Player – crouch | Squashed rect 24×28, head tucks into shoulders. | Same | 1 | Static pose |
| Player – run | Same body, legs alternate 4-frame stride, y±4 px bounce. | Same | 1 | Leg cycle 0.3 s; dust puffs `#8B7355` r=8 px, fade 0.3 s at feet |
| Player – jump | Body stretch 1.8× vertically (24×86), arms up. | Same | 1 | Squash→stretch→return. Trail: 3 ghost copies 40% alpha, 0.1 s apart |
| Player – hurt | Same body tinted `#FF2D78` 70%, 3-frame flash. | Flash `#FF2D78`→white→back | 1 | 0.15 s/frame, knockback wobble x±10 px |
| Player – death | Shatters into 8 triangle shards r=10 px. | Shards `#2C3E50` edges `#FF2D78` | 1 | Shards spin/fade 1.2 s |
| Gun – Pulse Rifle | Rect barrel 40×12, circle muzzle r=8. | Body `#5C6B73`, muzzle ring `#FFB347` | 1 | Recoil: barrel x−8 px, 0.08 s |
| Pulse – projectile | Circle r=6, trailing line 20 px. | Core `#FFB347`, trail→transparent | ≤12 on-screen | Linear, no arc. Fades at life end |
| Gun – Scatter Cannon | Wide rect barrel 32×22, 3 muzzle ports r=6. | Body `#8B4513`, ports `#FF2D78` | 1 | Muzzle flash: 3 radial lines 24 px `#FF2D78`, 0.06 s |
| Scatter – projectile (×6) | Tiny circles r=4, spread 18° cone. | `#FF2D78` | 6/shot | Linear, fade at life end |
| Gun – Rail Lance | Cylindrical barrel 64×16, 3 glowing coil rings. | Body `#1A2E33`, coils `#00E5FF` | 1 | Charge glow ramp 0.3 s before fire; beam-pierce trail |
| Rail – projectile | Elongated rect 30×4, bright core. | `#00E5FF` core, `#FF2D78` edge glow | 1/shot | Linear 1400 px/s, pierces 3 enemies. Flickers 60 Hz |
| Gun – Arc Burst | Short fat rect 24×28, curved arm. | Body `#4A3728`, warhead `#FF2D78` | 1 | Launch: barrel tilts up 15° 0.12 s |
| Arc – projectile | Circle r=8, 4 tiny fins. | `#FF2D78` body, `#FFB347` fins | ≤3 on-screen | Linear 480 px/s. On hit: chain arc to nearest enemy ≤90 px |
| Arc – chain effect | Wavy line between impact and chained enemy. | `#00E5FF`→`#FF2D78` gradient | 1/chain | 0.15 s, sine amp 4 px |
| Arc – explosion | Expanding circle r=0→56 px over 0.3 s, 8 triangle shards. | Ring `#FFB347`→`#FF2D78`→transparent. Shards `#4A3728` | 1/detonation | Radial burst, 6 smoke puffs `#666` r=12 px, 0.8 s |
| Enemy – Drone | Teardrop body 20×36, 2 wing arcs r=14. | Body `#00E5FF`, wings `#1A2E33`, eye `#FF2D78` | 2–5/stage | Sine hover y±12 px 1.0 s; wings 4-frame flap. Hurt: magenta flash 0.1 s. Death: pop expand 1.3×, 6 droplet circles fade 0.6 s |
| Enemy – Sentry | Turret base 28×32, rotating barrel 20×8. | Base `#5C6B73`, barrel `#C45A2D`, eye `#FF2D78` | 2–4/stage | Rotates to face player. Fires aimed bullet speed 300. Hurt: white flash 0.1 s. Death: barrel explodes 6 shards 0.5 s |
| Enemy – Runner | Low rect 28×20, 4 stub legs, single red eye r=6. | Body `#C45A2D`, eye `#FF2D78` | 3–6/stage | 4-frame leg crawl y±3 px. Charge: stretch 1.5× forward. Hurt: white flash. Death: legs fold, flatten, fade 0.5 s |
| Enemy – Mine | Sphere r=14, 4 spike nubs. | Body `#3D3D3D`, spikes `#FF2D78`, fuse glow `#FFB347` | 1–3/stage | Static. Proximity: fuse pulses 0.6 s → explode (radius 70 px). Death: expanding ring + shards 0.3 s |
| Enemy – Shieldbot | Tall rect 36×52, front shield plate 8×48. | Body `#2C3E50`, shield `#5C6B73`, eye `#FF2D78` | 1–3/stage (W2) | Shuffles 60 px/s. Slam: 0.3 s windup, 0.2 s active, radius 50 px. Hurt: white flash on rear. Death: shield falls, body crumbles 0.6 s |
| Boss – Press Golem | Massive rect 128×192, 2 piston arms 64×24, visor slit. | Body `#3D3D3D`, pistons `#C45A2D`, visor `#FFB347` | 1 | Idle: steam puffs joints every 1.5 s, y±5 px. Slam: arm raises 96 px→descends→impact squash. Charge: visor pulses amber 3× 0.6 s. Hurt: white flash joints. Death: pistons explode 8 shards, crumble 2 s, steam floods |
| Boss – Reservoir Warden | Octagonal core r=48, 4 tentacle arms length 160 r=8. | Core `#1A2E33`, arms `#00E5FF`, eye `#FF2D78` | 1 | Arms rotate 15°/s. Sweep: 2 arms extend, core flash magenta 0.5 s telegraph. Spin: all 4 extend, core 360° 0.8 s. Hurt: core dims 30% 0.15 s. Death: cracks 4 lines, collapse r=0.5→detonate cyan ring + 12 shards 2.5 s |
| Pickup – Health Cell | Hexagon r=14, cross icon inside. | Shell `#00E5FF`, cross `#FFFFFF` | 2–4/stage | Float y±6 px sine 1 s. Glow halo r=28 40% alpha |
| Pickup – Shield Cell | Hexagon r=14, shield icon. | Shell `#00E5FF`, icon `#FFB347` | 1–2/stage | Same float + halo |
| Pickup – Ammo Crate | Rect 24×24, lid 30°, bullet icon. | Body `#FFB347`, lid `#8B7355` | 2/stage | Static; wobble 2 px when player within 64 px |
| Pickup – Coin | Circle r=8, star icon. | `#FFB347` | 6–10/stage | Spin 180°/s, bob 4 px |
| Platform – Solid | Rect, variable w×16 or 32. Top surface 4 px lighter strip. | W1: `#5C6B73` top `#8B7355`. W2: `#1A2E33` top `#2C4A52` | Many | Static |
| Platform – One-way | Same as solid, bottom half transparent. | Same | Many | Static. Player can jump through from below |
| Platform – Crumble | Same as solid, 4 crack lines. | `#8B7355` cracks `#C45A2D` | 2–6/stage | Static→0.4 s shake→6 shard pieces fall (T2) |
| Platform – Conveyor | Rect with 6 chevrons scrolling. | Body `#3D3D3D`, chevrons `#FFB347` | 1–2/stage | Chevrons scroll x (visual only, no speed effect) (T2) |
| Hazard – Spikes | Row of triangles base 12 height 18. | `#8B7355` tips `#FF2D78` | Clusters 4–8 | Static |
| Hazard – Laser Gate | Vertical beam 8×96, emitter nodes top/bottom. | Beam `#FF2D78`, emitters `#5C6B73` | 1/stage | Period 2.0 s (on 1.0, off 1.0). Beam fades in/out over 0.1 s |
| Hazard – Acid Pool | Rect pool 64×32, wavy top edge. | `#00E5FF` 50% alpha, white sparks r=4 | 1–2/stage (W2) | Wave sine 3 px amp; sparks blink 0.2 s random (T3) |
| Checkpoint Totem | Pillar 16×64, glowing orb r=10 atop. | Pillar `#2C3E50`, orb `#00E5FF` | 0–1/stage (stage 3+) | Inactive: orb dim `#1A2E33`. Active: bright, ring pulses r=10→48, 1.5 s loop |
| Extraction Pad / Exit Gate | Rect 64×96, shutter lines ×8, stencil number. | Door `#3D3D3D`, rim `#FF2D78`, number `#FFB347` | 1/stage | Closed: static. Opening: shutter slides up 0.8 s, `#FFB347` radial flood + 20 confetti rects |
| BG Layer 1 – Far skyline | Silhouette rects/triangles, parallax 0.2×. | W1 `#0F1B1F`, W2 `#0A1618` | Full-width | Static (camera parallax) |
| BG Layer 2 – Mid structures | Pipes, arches, smokestacks, parallax 0.5×. | W1 `#1A2E33`, W2 `#15292E` | Full-width | Parallax scroll |
| BG Layer 3 – Near detail | Dripping chains, fungi, broken signs, parallax 0.8×. | W1 `#2C3E50`, W2 `#1E3A40` | Full-width | Parallax; drips fall 128 px 0.3 s |
| BG Layer 4 – Foreground fog | Gradient band bottom 64 px. | `#1A2E33` 20% alpha | Full-width | Static (T2) |
| Neon Sign (decor) | Rect frame 48×24, text shape. | Frame `#2C3E50`, text `#FF2D78`/`#00E5FF` | 2–4/stage | Flicker 80% on / 20% random 0.1 s off. Tiny y jitter 1 px |
| Particle – Hit spark | 6 radial lines length 14 px. | `#FFFFFF`→`#FFB347` | 1/hit | 0.1 s, scale 1→0 |
| Particle – Pickup sparkle | 8 tiny stars r=3, spiral outward. | `#FFB347`, `#00E5FF` | 1/pickup | 0.4 s, fade |
| Particle – Dust (land) | 3 ellipses 12×6 at feet. | `#8B7355` 50%→0% | 1/landing | 0.25 s, drift outward |
| Particle – Checkpoint ring | Expanding ring + 12 rising motes. | Ring `#00E5FF`, motes `#FFB347` | 1/activation | Ring r=0→80 over 0.6 s. Motes rise 64 px 0.8 s |

---

# 4. GAMEPLAY SPEC

**The game in one paragraph:** You are Kael, a freelance data-runner breaking into the floors of a mega-corporation's black-site server tower. Minute to minute you run, jump, crouch through low ducts, and shoot waves of security drones, sentries, and floor bosses with one of four weapons, managing a small ammo pool and a regenerating shield. Each world is a floor; each stage is a sector you must clear left-to-right, reaching the extraction pad at the far right. Stage 5 of every world is a boss arena. The game ends after you defeat the boss of World 2 and trigger the "Spire Purge" epilogue. Replayability comes from seeded level layouts, a hidden per-stage score (time, enemies killed, coins), and New Game+ (T3). The game is 10 stages long, roughly 20–25 minutes for a skilled run.

**Records and rosters** are defined in §2.2 (global context fields) and the tables below.

## 4.1 Movement [T1]

| Parameter | Value |
|---|---|
| Run speed cap | 280 px/s |
| Crouch speed cap | 140 px/s |
| Acceleration | 1800 px/s² |
| Deceleration | 2400 px/s² |
| Jump velocity (1st) | −480 px/s (upward) |
| Double-jump velocity | −400 px/s |
| Gravity | +1400 px/s² (downward, Y+) |
| Terminal vy | +700 px/s |
| Coyote time | 0.08 s |
| Jump buffer | 0.10 s |
| Max jump height | ≈180 px (from vy=−480, g=1400) |
| Level bounds | x ∈ [40, levelWidth−40]; y > levelHeight+100 → instant death (pit) |

**Rules:**

- **Left/Right** (A, ←, D, →, touch): set `vx` toward ±280 with accel 1800; no key → decel 2400 toward 0. Crouching cap 140.
- **Jump** (W, ↑, Space): if `jumpCount < 2` AND state ≠ crouching → `vy = −480`, `jumpCount++`. If crouching → un-crouch first (1 frame, no jump this press).
- **Double-jump**: second press while airborne, `jumpCount == 1` → `vy = −400`, `jumpCount = 2`.
- **Crouch** (S, ↓, held): if grounded → `state = "crouching"`, `h = 28`, speed cap 140. Release → `h = 48`, `state = "grounded"`. Hitbox shrinks to 28 px (passes under 32-px gaps).
- **One-way platforms**: land only if `vy > 0` AND player bottom was above platform top last frame. Press S while on one-way → `vy = 60`, disable collision 0.2 s (fall through).
- **Crumble platforms**: on landing, start `crumbleTimer`. At 1.5 s → remove platform, player falls.
- **Coyote**: if player walks off edge (grounded → not grounded without jump), `coyoteTimer = 0.08`. Jump press within coyote window counts as grounded jump.
- **Buffering**: if jump pressed within 0.10 s before landing, jump fires on land.

## 4.2 Combat [T1]

**Fire** (J, Z, mouse click, touch FIRE): if `ammoPool[activeWeapon].current > 0` AND `shootCooldown ≤ 0` AND `recoilLockout ≤ 0`:
- Decrement ammo by 1.
- Spawn `pelletsPerShot` projectiles at muzzle offset (facing × 24 px, y − 8 standing / y − 4 crouching).
- Each: velocity = `projSpeed` in facing ± `spread` random angle per pellet (via `ctx.rng()`).
- `shootCooldown = 1 / fireRate`.
- **Rail Lance**: `recoilLockout = 0.15 s` (player cannot move horizontally during lockout).
- **Arc Burst**: on projectile hit, if `chainRadius > 0`, find nearest other enemy within 90 px of impact → spawn secondary projectile toward it (damage × 0.6, one chain only).

**Weapon Switch** (1/2/3/4 direct, Q/K cycle): set `activeWeapon` to chosen id if in `unlockedWeapons`. Instant, no cost.

**Projectile update**: position += velocity × DT. Remove when `projectileLife` elapsed or hits solid platform. Projectile vs Enemy: subtract damage from `hp`. If `pierceCount > 0`, decrement and continue; else remove.

**Weapon Roster (authoritative stats):**

| id | damage | fireRate | spread | projSpeed | projLife | pellets | pierce | chainRadius | cooldown |
|---|---|---|---|---|---|---|---|---|---|
| pulse_rifle | 12 | 7.0 | 3° | 700 | 1.1 | 1 | 0 | 0 | 0 |
| scatter_cannon | 9 | 1.5 | 18° | 520 | 0.45 | 6 | 0 | 0 | 0.65 |
| rail_lance | 55 | 0.8 | 0° | 1400 | 2.0 | 1 | 3 | 0 | 1.1 |
| arc_burst | 14 | 4.0 | 8° | 480 | 0.8 | 1 | 0 | 90 | 0 |

**AmmoPool (start / max):**

| Weapon | Start | Max |
|---|---|---|
| pulse_rifle | 120 shots | 240 |
| scatter_cannon | 24 shells | 48 |
| rail_lance | 10 charges | 20 |
| arc_burst | 40 cells | 80 |

## 4.3 DamageAndDeath [T1]

- Player takes damage: subtract from `shield` first, then `hp`. Set `invulnTimer = 1.2`, `shieldRegenDelay = 0`. If `hp ≤ 0` → `state = "dead"`, `lives--`, respawn at checkpoint after 1.5 s fade.
- Shield regen: if `shieldRegenDelay ≥ 2.0` AND `shield < 50` → `shield += 12/s`. Reset `shieldRegenDelay = 0` on any hit.
- Contact damage: player hitbox overlaps enemy hitbox AND `invulnTimer ≤ 0` → apply `Enemy.damage`.
- Hazard damage per Hazard record (spike 20 instant, laser_gate 25 contact, acid_pool 10/s).
- Knockback on hit: 120 px/s impulse, 0.15 s duration.
- `lives = 0` → "Game Over" screen → restart current world at Stage 1, full HP/shield, default ammo, lives = 3.

## 4.4 EnemyAI [T1]

Per enemy, each frame:

- **Perception**: `dist = hypot(player.x - enemy.x, player.y - enemy.y)`. If `dist ≤ aggroRange` AND alive → `state = "chase"`. If `state == "chase"` AND `dist > aggroRange × 1.4` → `"patrol"`.
- **Patrol** (drone, runner): move at `vx` in `patrolDir`. Reverse after traveling `patrolRange` from spawn or at platform edge.
- **Drone chase**: move toward player at 100 px/s, sine bob y±12 px period 1.0 s. Stop at 100 px. Fire 1 bullet (speed 180, damage 10) every 1.2 s.
- **Sentry chase**: rotate to face player. Fire aimed bullet (speed 300, damage 15) every 1.0 s.
- **Runner chase**: set `vx` toward player at 160. Contact → 18 damage, 0.4 s lunge anim, reset cooldown.
- **Mine**: static. Player center within 60 px → 0.6 s fuse → explode: 35 damage within 70 px radius; destroy self.
- **Shieldbot chase**: shuffle toward player at 60. Frontal hitbox (32 px wide) blocks projectile damage; rear/above takes full. Contact 20. Slam every 2.0 s: 0.3 s windup, 0.2 s active, damage 20, radius 50 px, knockback 120 px/s.

**Enemy Roster:**

| type | hp | vx | damage | aggroRange | attackCooldown | behavior |
|---|---|---|---|---|---|---|
| drone | 24 | 100 (floats) | 10 (bullet) | 250 | 1.2 s | hovers toward player, fires |
| sentry | 40 | 0 (stationary) | 15 (bullet) | 320 | 1.0 s | rotates, fires aimed |
| runner | 30 | 160 (ground) | 18 (contact) | 200 | 0.4 s | patrols, charges |
| mine | 20 | 0 (static) | 35 (AoE 70 px) | 60 (proximity) | 0.6 s fuse | detonates on proximity |
| shieldbot | 70 | 60 (shuffles) | 20 (contact) | 180 | 2.0 s (slam) | front shield blocks; hit rear/above |

## 4.5 BossAI [T1]

- Boss stationary or moves per attack. Player dodges and shoots.
- Phase advances when `boss.hp ≤ phaseTransitionHP` → 1.0 s invulnerable transition flash, new attacks enabled.
- Boss hitbox: 128×192 px (Press Golem), 96×240 px (Reservoir Warden). Rail Lance pierce does NOT pierce boss (treated as 1 hit).
- On `boss.hp ≤ 0`: 3 s death sequence → stage clear triggers.

**Press Golem (W1-S5, 600 HP, phase transition at 400 HP):**

| # | Trigger | Effect |
|---|---|---|
| 1 | Every 3.0 s | Ground slam: 2 shockwave projectiles (speed 200, damage 20, travel along ground) |
| 2 | Every 5.0 s | 5 aimed bullets fan (±25°, speed 280, damage 15) |
| 3 | Phase 2+ | Charges horizontally (speed 300, damage 30, 1.5 s duration, 4 s cooldown) |
| 4 | Phase 3 | Summons 2 drones (200 px apart) every 6 s |

**Reservoir Warden (W2-S5, 1100 HP, phase transition at 366 HP):**

| # | Trigger | Effect |
|---|---|---|
| 1 | Every 2.5 s | Sweeps laser line across arena (travel 400 px/s, damage 25, 0.8 s duration) |
| 2 | Every 4.0 s | Drops 3 ceiling mines (fall speed 180, proximity 50 px, damage 35) |
| 3 | Phase 2+ | Teleports to random x, fires 8-bullet ring (speed 220, damage 12) |
| 4 | Phase 3 | Deploys 2 shieldbots, then 3× ground-slam (damage 30 each, 0.6 s gap) |

## 4.6 PickupAndAmmo [T1]

- Player hitbox overlaps Pickup → apply effect, remove, play collect sound.
- Ammo: add `amount` to `ammoPool[type].current`, cap at max. Amounts: pulse 20, scatter 6, rail 3, arc 10.
- Health: `hp = min(hp + 25, 100)`.
- Shield: `shield = min(shield + 20, 50)`.
- Coin: `scoreboard.coinsCollected++`.
- **No respawn** within a stage. Gone until restart.

## 4.7 LevelGenerator [T1]

Parameters: `seed` (uint32), `world` (1–2), `stage` (1–5), `difficultyScale` (1.0 default, 1.4 NG+).

Places in order:

1. **Ground**: continuous solid at y = 480, height 32, width = 3200 (S1–4) or 1600 (S5). Gaps: `gapCount = 4 + stage + world` gaps of width 48–96 px, spaced 300–500 px. Pit below gap = instant death.

2. **Mid-platforms**: `platCount = 6 + stage × 2` one_way/solid at y ∈ {320, 384, 256}, x spaced 200–400 px, w ∈ {64, 96, 128, 192}. Crumble: `crumbleCount = 2 + stage` at y = 256.

3. **Upper/ceilings**: `ceilCount = 3 + stage` solid slabs at y ∈ {128, 160}, w ∈ {96, 128}, forcing crouch passages (gap height = 32 px).

4. **Enemies**: `enemyCount = 5 + stage × 2 + world × 3`. Distribute: W1: 40% drone, 30% runner, 20% sentry, 10% mine. W2: 20% drone, 25% runner, 25% sentry, 15% mine, 15% shieldbot. Place at x ∈ [400, levelWidth−200], y on nearest platform.

5. **Hazards**: `hazardCount = 2 + stage` spikes (gap edges/floor) + 1 laser_gate per stage (x ∈ {800, 1600, 2400}, period 2.0 s). W2 adds acid_pool in 1 gap (T3).

6. **Pickups**: 2 ammo (random type weighted toward active), 1 health, 1 shield, 6–10 coins on platforms and in air pockets.

7. **Checkpoint**: solid totem at x = levelWidth × 0.5 (stage 3+ only). Touch → set respawn point.

8. **Extraction pad**: x = levelWidth − 80, y = 480. Overlap → stage clear.

9. **Weapon unlock crates** (fixed): S1-W1: none. S2-W1: Scatter Cannon. S3-W1: Arc Burst. S4-W1: Rail Lance. W2 stages: ammo/health only.

**VERIFIER** (re-roll seed+1 on failure):
- (a) No enemy/hazard inside solid platform.
- (b) Every gap ≤ 96 px AND platform within 120 px horizontal reach at jumpable height.
- (c) ≥ 1 health pickup before midpoint.
- (d) Crouch passages clearance ≥ 28 px.
- (e) Every pickup reachable via max jump height 180 px from ground.

## 4.8 StageFlow [T1]

- Touch extraction pad → stage complete → Stage Clear screen → advance `currentStage`.
- `currentStage > 5` → advance `currentWorld`, reset `currentStage = 1`. `currentWorld > 2` → Game Complete.
- Boss stages (S5): arena 1600 px wide, flat floor, 4 one-way platforms (W1) or concentric rings (W2). No extraction pad; defeating boss triggers clear.
- Death: respawn at checkpoint (or stage start if before checkpoint). Lives − 1. Lives = 0 → Game Over.

## 4.9 Scoring [T1]

- Stars: 1 = clear. 2 = clear + ≥ 60% enemies killed. 3 = clear + ≥ 60% enemies + all coins + time ≤ par_time.
- `par_time = 45 + stage × 10` s (S1 = 55, S5 = 95).
- Total stars tracked; shown on world-select and end screen.

## 4.10 Progression and Difficulty [T1]

**Unlock order:**
- Start: Pulse Rifle only, 120 ammo, 100 HP, 50 shield, 3 lives.
- W1-S2: Scatter Cannon unlocked, +24 shells.
- W1-S3: Arc Burst unlocked, +40 cells. Checkpoint introduced.
- W1-S4: Rail Lance unlocked, +10 charges.
- W1-S5: Boss 1 (Press Golem, 600 HP).
- W2-S1–S4: All four weapons available; ammo refills to start values each stage; enemy density and HP × 1.2.
- W2-S5: Boss 2 (Reservoir Warden, 1100 HP). Game ends.

**Difficulty curve:**
- W1S1: 7 enemies, 6 gaps, 2 hazards. Learns movement + pulse rifle. Forgiving.
- W1S3: 11 enemies, 8 gaps, 4 hazards, checkpoint. Mines + crouch passages.
- W1S4: 13 enemies, 10 gaps, 5 hazards. Rail Lance; pierce drone clusters.
- W2S1: 10 enemies (shieldbots appear), 7 gaps, 3 hazards + acid. HP ×1.2.
- W2S4: 16 enemies, 10 gaps, 6 hazards. All types mixed.
- Bosses: phase 2 adds charge/teleport; phase 3 adds summons.

**Expected failure points:** Boss phase 3 (both); crouch-passage + laser_gate sequences in W2. Recovery: checkpoint at mid-stage; Game Over restarts world.

**NG+ [T3]:** After full clear. Enemy HP ×1.4, count ×1.3, boss HP ×1.3, par_time −20%. Ammo caps unchanged.

## 4.11 Feel [T1]

| Parameter | Value | Tuned to achieve |
|---|---|---|
| Run speed | 280 px/s | Momentum + aim time |
| Crouch speed | 140 px/s | Deliberate traversal |
| Accel / Decel | 1800 / 2400 px/s² | Snappy start/stop (~0.16 s / ~0.12 s) |
| Jump vy | −480 px/s | ~180 px peak; clears 2-tile gaps |
| Double-jump vy | −400 px/s | Second push, not reset |
| Gravity | 1400 px/s² | Snappy arc; 180 px fall ≈ 0.5 s |
| Terminal vy | 700 px/s | Pits feel deadly |
| Coyote | 0.08 s | Walk-off-edge forgiveness |
| Buffer | 0.10 s | Pre-land jump |
| Pulse fire rate | 7/s | ~143 ms between shots |
| Scatter pump | 1.5/s + 0.65 s cooldown | "Rack the shotgun" |
| Rail lockout | 0.15 s of 1.1 s | Weight of the shot |
| Knockback | 120 px/s, 0.15 s | Visible push, recoverable |
| Hit flash | 0.1 s white | Readable, non-obscuring |
| Invuln | 1.2 s | Reposition time |
| Shield regen | 2.0 s delay, 12/s | Tension window |
| Crumble timer | 1.5 s | Punishes lingering |
| Laser period | 2.0 s (1/1) | Readable rhythm |
| Drone bullet | 180 px/s | Dodgeable |
| Sentry bullet | 300 px/s | Requires lateral/crouch |
| Boss shockwave | 200 px/s | Jump over |
| Camera look-ahead | 120 px | 1/3 screen ahead |
| Camera dead-zone Y | ±80 px | No jitter on small hops |
| Death fade | 1.5 s | Register failure |
| Screen shake | 4 px, 0.15 s | Impact, no nausea |

---

# 5. CHARACTERS

## Player (Kael / "The Scavenger")

**Silhouette:** Chunky, top-heavy. Broad shoulders, short legs, oversized helmet with glowing visor slit. Visible piston joints at knees/elbows. At a glance: "small tough thing with a big head and a big gun." Visor colour changes with equipped gun: cyan = Rail Lance, magenta = Scatter/Arc, amber = Pulse Rifle.

**Facings:** Left, Right (mirrored). Crouch, jump, run states for both. No diagonal.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | 2 frames: breathe y±3 px. Head tilts 2° alternating. | 0.8 s |
| Run | 4 frames: legs alternate, body y±4 px, arms swing ±15°. | 0.3 s |
| Crouch | 1 pose (static). Helmet retracts 6 px into shoulders. | No loop |
| Jump ascend | 1 pose: body stretch 1.8×, legs tucked, arms up. | Transition |
| Jump descend | 1 pose: body return, legs extend forward. | Transition |
| Land | 2 frames: squash 1.2× → normal. | 0.15 s |
| Shoot (Pulse/Scatter) | 2 frames: recoil lean back 5° → return. | 0.1 s |
| Shoot (Rail Lance) | 1 pose: arms locked forward, slight lean. | Hold while firing |
| Shoot (Arc Burst) | 3 frames: crouch → stand → recoil. | 0.2 s |
| Hurt | 3 frames: white flash, wobble, recover. | 0.45 s |
| Death | Shatter into 8 shards. | 1.2 s, no loop |

## Drone

**Silhouette:** Floating teardrop with two moth-like wings. Glowing cyan body, single magenta eye. "An angry glowing raindrop."

| Animation | Frames | Loop |
|---|---|---|
| Hover | 4 frames: wings up/mid/down/mid, body sine y±12 px. | 1.0 s |
| Fire | 1 frame: eye flash, bullet spawn. | 0.1 s |
| Hurt | 1 frame: magenta flash, body compress. | 0.1 s |
| Death | Pop expand 1.3×, 6 droplet circles, fade. | 0.6 s |

## Sentry

**Silhouette:** Stationary turret on a squat base. Rotating barrel. "A rusty eyeball on a pedestal."

| Animation | Frames | Loop |
|---|---|---|
| Idle | Barrel slowly scans ±30°. | 4 s |
| Aim | Barrel snaps to player. | 0.2 s |
| Fire | Barrel recoil + muzzle flash. | 0.1 s |
| Hurt | White flash. | 0.1 s |
| Death | Barrel explodes 6 shards, base crumbles. | 0.5 s |

## Runner (Rust Crawler)

**Silhouette:** Low, wide, insect-like. Four legs splayed, single glowing eye on stalk. "A rusty beetle that scuttles."

| Animation | Frames | Loop |
|---|---|---|
| Patrol | 4-frame leg crawl, body y±3 px. | 0.4 s |
| Chase/Charge | Legs blur, body stretch 1.5× forward. | 0.2 s |
| Lunge (contact) | 2-frame: extend → impact. | 0.4 s |
| Hurt | White flash, legs tuck. | 0.1 s |
| Death | Legs fold, body flatten, fade. | 0.5 s |

## Mine

**Silhouette:** Low sphere with spike nubs. "A spiky sea-mine waiting to pop."

| Animation | Frames | Loop |
|---|---|---|
| Dormant | Slight bob y±2 px. | 2 s |
| Fuse | Pulse amber 3× over 0.6 s, expand 1.2×. | 0.6 s |
| Detonate | Expanding ring + 8 shards. | 0.3 s |

## Shieldbot

**Silhouette:** Tall humanoid with a massive front shield plate. "A riot cop made of scrap."

| Animation | Frames | Loop |
|---|---|---|
| Patrol | Shuffle 2-frame, shield sways. | 1.5 s |
| Chase | Faster shuffle, shield angled forward. | 0.8 s |
| Slam | 2-frame: raise shield → slam down (0.3 s windup, 0.2 s active). | 0.5 s |
| Hurt (rear) | White flash, stagger. | 0.1 s |
| Hurt (front) | Shield clang, no damage. | 0.1 s |
| Death | Shield falls, body crumbles. | 0.6 s |

## Press Golem (W1 Boss)

**Silhouette:** Squat hydraulic press with legs. Two massive piston arms, visor slit, exhaust pipes on shoulders. "A construction press that wants to flatten you."

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Steam puffs joints every 1.5 s. Body y±5 px. | 2 s |
| Arm Slam | 4 frames: arm raises 96 px → descends fast → impact squash → recover. | 0.8 s |
| Charge (telegraph) | Visor pulses amber 3× 0.6 s, body glows `#FFB347`. | Before attack |
| Hurt | White flash on piston joints. | 0.1 s |
| Death | Pistons explode 8 shards, crumble 2 s, steam floods. | 2 s |

## Reservoir Warden (W2 Boss)

**Silhouette:** Floating octagonal core with four segmented tentacle arms ending in claws. Bioluminescent veins pulse. "A deep-sea jellyfish made of subway infrastructure."

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Arms rotate 15°/s. Core pulses cyan. | Continuous |
| Sweep | 2 arms extend 160 px in line, core flash magenta 0.5 s telegraph. | 1 s |
| Spin | All 4 arms extend, core 360° 0.8 s. | 0.8 s |
| Hurt | Core dims 30% 0.15 s, veins flash white. | 0.15 s |
| Death | Cracks 4 lines, collapse r→16, detonate cyan ring + 12 shards. | 2.5 s |

---

# 6. AUDIO

Generated with the Web Audio API. No external files.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| `jump` | Square, 320 Hz → 180 Hz sweep, 0.12 s, attack 0.01 s, decay 0.11 s | Player jump (first or double) |
| `land` | Noise burst, bandpass 800 Hz, 0.08 s, instant attack, fast decay | Player touches ground after fall |
| `shoot_pulse` | Square, 660 Hz, 0.05 s, sharp attack, 0.04 s decay | Pulse Rifle fire |
| `shoot_scatter` | Noise burst, lowpass 2000 Hz, 0.12 s, instant attack | Scatter Cannon fire |
| `shoot_rail` | Sawtooth, 120 Hz → 60 Hz sweep, 0.3 s, slow attack 0.05 s, long decay | Rail Lance fire |
| `shoot_arc` | Triangle, 880 Hz, 0.08 s + noise tail 0.1 s | Arc Burst fire |
| `chain_arc` | Sine, 1200 Hz → 600 Hz, 0.1 s, FM mod | Arc Burst chain secondary hit |
| `hit_enemy` | Square, 440 Hz, 0.04 s, instant | Projectile hits enemy |
| `enemy_die` | Sawtooth, 220 Hz → 80 Hz, 0.2 s | Enemy hp ≤ 0 |
| `player_hurt` | Square, 160 Hz, 0.15 s + noise 0.1 s | Player takes damage |
| `player_die` | Sawtooth, 300 Hz → 60 Hz, 0.6 s, slow decay | Player hp ≤ 0 |
| `pickup_ammo` | Sine, 880 Hz → 1100 Hz, 0.1 s | Ammo pickup collected |
| `pickup_health` | Sine, 660 Hz → 990 Hz, 0.12 s | Health pickup collected |
| `pickup_shield` | Sine, 740 Hz → 1040 Hz, 0.12 s | Shield pickup collected |
| `pickup_coin` | Triangle, 1320 Hz, 0.08 s, 2-frame arpeggio | Coin collected |
| `checkpoint` | Sine, 440 → 660 → 880 Hz arpeggio, 0.3 s | Checkpoint activated |
| `weapon_switch` | Sine, 520 Hz, 0.06 s, pitch-shift up | Weapon changed |
| `low_ammo` | Square, 200 Hz, 0.1 s, repeat every 1 s while ≤ 10% | Low-ammo warning |
| `boss_phase` | Sawtooth, 80 Hz, 0.4 s + noise sweep | Boss phase transition |
| `boss_die` | Sawtooth, 120 Hz → 40 Hz, 1.0 s + noise 0.5 s | Boss hp ≤ 0 |
| `stage_clear` | Triangle arpeggio 440→550→660→880, 0.4 s | Extraction pad touched |
| `game_over` | Square, 200 Hz → 80 Hz, 0.8 s | Lives exhausted |
| `game_complete` | Major chord arpeggio (440, 550, 660, 880), 1.2 s | W2-S5 boss defeated |
| `mine_fuse` | Sine, 600 Hz pulsing, 0.6 s | Mine proximity triggered |
| `mine_explode` | Noise burst, 0.2 s, lowpass 400 Hz | Mine detonation |
| `laser_gate_on` | Sawtooth, 1000 Hz, 0.08 s | Laser gate activates |
| `crumble` | Noise, bandpass 400 Hz, 0.3 s | Crumble platform breaks |
| `ui_select` | Sine, 800 Hz, 0.05 s | Menu confirm |
| `ui_back` | Sine, 400 Hz, 0.05 s | Menu back |
| `recoil_lock` | Square, 100 Hz, 0.1 s | Rail Lance movement lockout |

---

# 7. UX

## Screen state machine

```
TITLE → WORLD_SELECT → STAGE_PLAY ⇄ PAUSE
                          ↓ (pad touched)
                     STAGE_CLEAR → WORLD_SELECT (next stage) or STAGE_PLAY (next)
                          ↓ (lives=0)
                     GAME_OVER → TITLE
STAGE_PLAY → (W2-S5 boss dead) → GAME_COMPLETE → TITLE
```

**TITLE:** "GRIDFALL" logo (stencil font `#FFB347`), subtitle "Data-runner. One way out." (`#00E5FF`). "PRESS ENTER / TAP TO START" pulsing magenta. BG: parallax layers 1–3, one neon sign flickering. Vignette + grain. Enter/Tap → WORLD_SELECT.

**WORLD_SELECT:** 2×5 node grid. World 1 "The Rustbelt", World 2 "The Undercity" (locked until W1 boss defeated). Nodes: completed = cyan `#00E5FF`, locked = grey `#3D3D3D`, current = magenta `#FF2D78` pulse, available = amber outline. Path line `#FFB347`. Stars shown per node. Arrow keys/tap navigate. Enter → STAGE_PLAY. Escape → TITLE.

**STAGE_PLAY:** Gameplay screen. HUD overlaid. Stage-intro banner slides in 0.6 s, holds 1.5 s, fades 0.4 s. Escape → PAUSE.

**PAUSE (overlay):** "PAUSED" text. Resume (Esc/Enter), Restart Stage (R), Quit to World Select (Q).

**STAGE_CLEAR:** Stage name, clear time, enemies killed %, coins collected, stars (1–3 filled `#FFB347`). "Press Enter to continue." Enter → next STAGE_PLAY or WORLD_SELECT if boss.

**GAME_OVER:** "SYSTEM FAILURE — Lives exhausted." Stage reached. "Press Enter to restart world." Enter → WORLD_SELECT (stage 1 of current world).

**GAME_COMPLETE:** "SPIRE PURGE COMPLETE." Total stars (max 30), best time. "Press Enter to return to title." Enter → TITLE.

## HUD table

| Element | Record field | When visible |
|---|---|---|
| HP bar (left, 120 px wide, green→red gradient) | `player.hp` / 100 | Always in STAGE_PLAY |
| Shield bar (below HP, blue, 120 px) | `player.shield` / 50 | Always (dimmed if 0) |
| Lives (3 small diamond icons, top-left) | `player.lives` | Always |
| Weapon name + ammo count (bottom-left) | `player.activeWeapon` + `ammoPool[activeWeapon].current` | Always |
| Weapon icon row (4 slots, active ringed cyan) | `unlockedWeapons` | Always; locked slots show "?" |
| Stage indicator (top-center: "W1-S3") | `level.world` / `level.stage` | Always |
| Timer (top-right, counts up) | `scoreboard.clearTime` | Always |
| Coin count (top-right, below timer) | `scoreboard.coinsCollected` | Always |
| Boss HP bar (top-center, wide, appears stage 5) | `boss.hp` / `boss.maxHp` | Boss stage only, from arena entry |
| Checkpoint flash ("CHECKPOINT" text) | Triggered on touch | 1.0 s on activation |
| Low-ammo warning (weapon icon pulses red) | `ammoPool[activeWeapon].current ≤ 10% × max` | While condition true |
| Stage-intro banner | `level.world`, `level.stage` | First 2.5 s of stage |

---

# 8. DEBUG API

Installed by `debug.js` as `window.__game`. All calls synchronous, return plain data, never touch DOM.

| Call | What it does | Returns |
|---|---|---|
| `__game.start()` | Title → play, loads stage 1-1, init player. | `void` |
| `__game.step(dt, n)` | Runs exactly `n` fixed ticks of `dt` s each (tick order §1.1), draws once. | `void` |
| `__game.setTime(t)` | Runs ticks until `ctx.time ≥ t`, no draw. | `void` |
| `__game.seed(n)` | Reseeds `ctx.rng`, calls `level.load(ctx, 1, 1, n)`, resets player and pools. | `void` |
| `__game.getState()` | Deep-clone of all ctx fields (minus canvas, ctx2d, rng). | Plain object |
| `__game.move(dir)` | Sets `ctx.input.moveDir`. | `void` |
| `__game.jump()` | Sets `ctx.input.jumpPressed = true` for next tick. | `void` |
| `__game.crouch(on)` | Sets `ctx.input.crouchHeld = on`. | `void` |
| `__game.fire(on)` | Sets `ctx.input.fireHeld`; if transitioning to true, also `firePressed = true`. | `void` |
| `__game.switchWeapon()` | Sets `ctx.input.switchNext = true`. | `void` |
| `__game.selectSlot(n)` | Sets `ctx.input.weaponSlot = n` (1-4). | `void` |
| `__game.spawnEnemy(type, x, y, dir)` | Calls `enemies.spawn(ctx, type, x, y, dir)`. | `{id, x, y, type, alive}` |
| `__game.spawnProjectile(weaponId, x, y, vx, vy)` | Pulls from pool, configures. | `{id, x, y, alive}` |
| `__game.skipToStage(w, s)` | Calls `level.load(ctx, w, s, ctx.seed)`, resets player, state = 'play'. | `{world, stage, spawnX, spawnY}` |
| `__game.setField(path, value)` | Sets ctx field at dotted path. | `void` |
| `__game.getFrameCount()` | Returns `ctx.frame`. | `number` |
| `__game.getDrawCalls()` | Canvas draw ops from last draw. | `number` |
| `__game.getStateHash()` | 32-bit hash of `getState()` JSON. | `number` |
| `__game.setPlayerState(state)` | Sets `ctx.player.state` directly. | `void` |
| `__game.setBossHp(hp)` | Sets `ctx.boss.hp = hp`. | `void` |
| `__game.setAmmo(weaponId, amount)` | Sets `ctx.ammoPool[weaponId].current`. | `void` |
| `__game.unlockWeapon(weaponId)` | Pushes to `ctx.unlockedWeapons` if not present. | `void` |
| `__game.setScoreboard(field, value)` | Sets `ctx.scoreboard[field]`. | `void` |
| `__game.triggerCheckpoint()` | Activates checkpoint at current level's checkpointX. | `void` |
| `__game.setShake(intensity, duration)` | Sets `ctx.shake`. | `void` |
| `__game.placeExtractionPad(x, y)` | Sets `ctx.level.exitX, exitY`. | `void` |

---

# 9. TESTS

All tests drive exclusively through `window.__game`.

### T1 – Title → Play
```
__game.seed(42)
__game.start()
s = __game.getState()
```
Assert: `s.state === 'play'`, `s.level.world === 1`, `s.level.stage === 1`, `s.player.x === s.level.spawnX`, `s.player.y === s.level.spawnY`, `s.player.hp === 100`, `s.player.lives === 3`.

### T2 – Fixed-timestep movement (right)
```
__game.seed(42); __game.start()
__game.move(1)
__game.step(1/60, 60)
p = __game.getState().player
```
Assert: `p.x > 80 + 280 * 0.9` (≥ 332), `p.onGround === true`, `p.facing === 1`.

### T3 – Jump physics
```
__game.seed(42); __game.start()
__game.jump()
__game.step(1/60, 1)
p = __game.getState().player
```
Assert: `p.vy < 0` (upward, Y-down so negative = up), `p.onGround === false`, `p.state === 'airborne'`, `p.jumpCount === 1`.

### T4 – Crouch changes hitbox
```
__game.seed(42); __game.start()
h0 = __game.getState().player.h
__game.crouch(true)
__game.step(1/60, 1)
h1 = __game.getState().player.h
```
Assert: `h1 === 28`, `h1 < h0`, `__game.getState().player.crouching === true`.

### T5 – Fire weapon (Pulse Rifle)
```
__game.seed(42); __game.start()
__game.selectSlot(1)
__game.fire(true)
__game.step(1/60, 1)
pr = __game.getState().projectiles.filter(p => p.alive)
```
Assert: `pr.length >= 1`, `pr[0].x > __game.getState().player.x`, `pr[0].vx > 0`.

### T6 – All 4 weapon types fire
```
__game.seed(42); __game.start()
__game.unlockWeapon('scatter_cannon')
__game.unlockWeapon('rail_lance')
__game.unlockWeapon('arc_burst')
for slot in [1,2,3,4]:
    __game.selectSlot(slot)
    __game.fire(true)
    __game.step(1/60, 1)
```
Assert: ≥ 4 distinct weaponId values among alive projectiles.

### T7 – Weapon switch
```
__game.seed(42); __game.start()
__game.unlockWeapon('scatter_cannon')
w0 = __game.getState().player.weaponIndex
__game.switchWeapon()
__game.step(1/60, 1)
w1 = __game.getState().player.weaponIndex
```
Assert: `w1 !== w0`.

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
__game.setAmmo('pulse_rifle', 999)
e = __game.spawnEnemy('drone', 200, 400, -1)
__game.fire(true)
__game.step(1/60, 120)
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length === 0`, `__game.getState().scoreboard.enemiesKilled >= 1`.

### T10 – Player takes damage
```
__game.seed(42); __game.start()
hp0 = __game.getState().player.hp
__game.spawnEnemy('runner', 90, 480, 1)
__game.step(1/60, 30)
hp1 = __game.getState().player.hp
```
Assert: `hp1 < hp0`, `__game.getState().player.invulnTimer > 0`.

### T11 – Stage clear → advance
```
__game.seed(42); __game.start()
__game.setField('player.x', __game.getState().level.exitX)
__game.setField('player.y', __game.getState().level.exitY)
__game.step(1/60, 10)
s = __game.getState()
```
Assert: `s.level.stage === 2`, `s.level.world === 1`, `s.progression.stagesCleared` includes `"1-1"`.

### T12 – World progression (2 worlds, 5 stages)
```
__game.seed(42); __game.start()
for w in [1,2]:
    for s in [1..5]:
        __game.skipToStage(w, s)
        if s === 5:
            __game.setBossHp(0)
            __game.step(1/60, 200)
        else:
            __game.setField('player.x', __game.getState().level.exitX)
            __game.setField('player.y', __game.getState().level.exitY)
            __game.step(1/60, 10)
final = __game.getState()
```
Assert: `final.progression.stagesCleared.length === 10`, `final.state === 'game-complete'`.

### T13 – Restart preserves stage, resets player
```
__game.seed(42); __game.start()
__game.move(1); __game.step(1/60, 60)
__game.setField('state', 'play')
__game.setField('input.restart', true)
__game.step(1/60, 1)
s = __game.getState()
```
Assert: `s.level.stage === 1`, `s.player.x === s.level.spawnX`, `s.player.hp === 100`.

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
Assert: `s1.state === 'pause'`, `s2.frame === f1`.

### T15 – Draw-call budget
```
__game.seed(42); __game.start()
__game.skipToStage(1, 1)
__game.step(1/60, 30)
dc = __game.getDrawCalls()
```
Assert: `dc <= 600`.

### T16 – Entity pool cap