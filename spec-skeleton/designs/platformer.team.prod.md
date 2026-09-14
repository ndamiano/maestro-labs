# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
|---|---|
| Side-scrolling platformer | §1.1 axes, §3 space, §4 Locomotion |
| Shooter with at least 4 different gun types | §4 Shooting, §2 Gun roster (4 guns) |
| Character can jump | §4 Locomotion – Jump rule |
| Character can move left or right | §4 Locomotion – Move rule |
| Character can crouch | §4 Locomotion – Crouch rule |
| Story progression modelled off Mario (worlds → stages) | §4 ProgressionAndUnlocks, §0.3 T1 |
| 2 worlds | §4 ProgressionAndUnlocks, §3 space |
| 5 stages each (10 total) | §4 ProgressionAndUnlocks, §4 StageGenerator |
| Do not simply copy Mario | §0.2 ruling on extraction point; theme is industrial salvage |
| **[added]** Multi-phase bosses as stage-5 climaxes | §4 BossAI |
| **[added]** Score ranks and replay incentive | §4 Scoring, §0.3 T3 |
| **[added]** Hidden upgrade chips for post-game chase | §4 ProgressionAndUnlocks, §0.3 T4 |
| **[added]** Touch controls for mobile | §4 TouchControls |
| **[added]** Parallax and post-effects for visual identity | §3, §0.3 T2 |

## 0.2 Decisions

| Topic | gameplay.md said | visual.md said | engineering.md said | Ruling |
|---|---|---|---|---|
| Stage dimensions | 4800×720 normal, 1200×720 boss | 4800×1200 normal, 2400×1200 boss | max 400×40 tiles (12800×1280) | **4800×704 normal (150×22 tiles), 1216×704 boss (38×22 tiles).** Gameplay's widths respected; height rounded to 22×32 for grid alignment; boss arena widened slightly from visual's 2400 to keep it a single-screen lock. |
| Player hitbox | 48 px standing, 28 px crouch (height) | 36×56 standing, 36×36 crouch (drawn sprite) | `<player width>`, `<player height>`, `<crouch height>` placeholders | **Collision hitbox 32×48 standing, 32×28 crouch.** Visual sprite drawn at 36×56 (slightly oversized for flair). Width snapped to 32 for tile-grid alignment. |
| Gun names | Scrap Pistol, Rivet Shotgun, Coil Rifle, Flare Launcher | Pulse Pistol, Scatter Cannon, Rail Driver, Acid Sprayer, Plasma Lance (5 guns) | pistol, shotgun, laser, rocket | **4 guns, gameplay names.** Visual's 5th (Plasma Lance) dropped—user asked for 4, gameplay defines 4. Visual shapes kept per-gun (see §3). |
| Boss names | Rust Colossus, Core Warden | Furnace Colossus, Absolute Zero | — | **Furnace Colossus (W1), Absolute Zero (W2).** Visual names are more evocative and thematically consistent. |
| Enemy type names | Crawler, Turret, Drone, ShieldTrooper | Smelter Bot (W1), Cryo Stalker (W2), Rivet Drone | 'grunt' placeholder | **Mechanical types: Crawler, Turret, Drone, ShieldTrooper, Boss.** Visual skins: Crawler→Smelter Bot (W1) / Cryo Stalker (W2); Drone→Rivet Drone. |
| Stage generation | Seeded procedural with verifier | "Hand-authored per stage. No procedural generation." | `level.generate()` | **Seeded procedural generation (gameplay + engineering).** Visual's 5-zone structure becomes the generator's layout template per stage; the seed fills within zones. |
| Camera follow | Deadzone 80 H / 60 V, lerp 0.12/frame | Offset 35% from left, deadzone 80 V, X-track 8%/frame, Y-track 12%/frame | Basic lerp + clamp | **Deadzone 80 H / 60 V; lerp X 0.08, Y 0.12 per tick; player offset 35% from left edge; clamp to [0, stageWidth−960].** Merges gameplay's deadzone with visual's asymmetric lerp and offset. |
| Tile size | Not stated | Ground plate 80×40 | 32×32 grid | **32×32 collision grid.** Ground plates drawn as 64×32 (2×1 cells). Visual's 80×40 overridden for grid alignment. |
| Fire key | J / left-click | — | J / Enter / Z | **J, Enter, Z, left-click all fire.** Superset. |
| Gun swap | 1/2/3/4, scroll-wheel | — | K / Shift (cycle) | **1/2/3/4 select directly; K/Shift/scroll cycles.** Both mechanisms. |
| Reload key | R | — | (not listed) | **R reloads.** Carried from gameplay. |
| Lives | 3 per stage attempt | — | `<start lives>` | **3.** Placeholder filled. |
| Max HP | 100 | — | `<player max hp>` | **100.** Placeholder filled. |
| Player speed | 280 px/s | — | `<player speed>` | **280 px/s.** Placeholder filled. |
| Extraction point | "flagpole-style" | "blast door" or "teleport pad" | `level.flagX` | **Blast door.** Renamed from "flagpole" to avoid Mario copy. Mechanic identical: reach x ≥ flagX. |
| World themes | W1 industrial pipes/catwalks; W2 cave/underground | W1 Smelting Yards; W2 Cooling Towers | — | **W1 "Smelting Yards"; W2 "Cooling Towers."** Visual names are more specific. |
| Touch gun-swap | Bottom-right circular button | — | Bottom-right virtual buttons | **Bottom-right circular swap button.** |
| Screen states | Title→WorldMap→StageIntro→Gameplay→StageComplete→WorldMap + GameOver + Victory + Pause | (implicit in feedback) | TITLE→PLAYING→PAUSED→STAGE_CLEAR→GAME_OVER | **Full state machine from gameplay; engineering's enum extended: TITLE, WORLD_MAP, STAGE_INTRO, PLAYING, PAUSED, STAGE_CLEAR, GAME_OVER, VICTORY.** |
| Parallax | Not mentioned | 3 layers (5%, 20%, 60%) | `level.parallax` array | **3-layer parallax carried from visual.** |
| Post-effects | Not mentioned | Extensive table (vignette, chromatic aberration, shake, flash, heat distortion, frost bloom, grain, slow-mo) | Screen shake in camera module | **All post-effects carried; tagged T2.** |
| Upgrade chips | 4 per world (8 total), permanent gun stat boosts | Not mentioned | Not mentioned | **4 per world, carried from gameplay; tagged T4.** |
| Scoring / ranks | Bronze/Silver/Gold thresholds, speed bonus, no-damage bonus, chip bonus | Coins 20–40/stage, "+50" text | Not specified | **Gameplay's scoring rules carried; visual's coins are cosmetic pickups worth 50 pts each; tagged T3.** |
| Touch controls | D-pad left half, fire right half, swipe jump, circular swap, reload button | — | Virtual dpad + action buttons | **Merged: left-half dpad (move+crouch), right-half tap/hold (fire/charge), swipe-up anywhere = jump, bottom-right circular swap, bottom-left reload. Tagged T1.** |
| Sound recipes | Not detailed | Not detailed | Web Audio API, oscillator+noise | **Built from scratch in §6 using both docs' event lists.** |
| Frame budget | — | — | ≤14 ms, ≤200 draw calls, pools capped | **Carried as engineering's hard caps.** |

## 0.3 Tiers

**T1 (must ship):** Locomotion, Shooting (all 4 guns), DamageAndDeath, EnemyAI (Crawler + Drone minimum), StageGenerator (basic layout + verifier), ProgressionAndUnlocks (2 worlds × 5 stages, gun chests, checkpoints), Camera, Audio (core SFX), TouchControls, HUD, Screen state machine, BossAI (W1 boss only), Renderer (tiles, entities, parallax 3 layers, basic HUD).

**T2 (visual polish):** Post-effects (vignette, chromatic aberration, screen shake, flashes, heat distortion, frost bloom, grain, slow-mo tint), particle pools for explosions/dust, enemy death animations, player hurt/death animations, door-open animation, stage-clear stamp animation, world-transition wipe.

**T3 (scoring depth):** Full enemy variety (Turret, ShieldTrooper), coin pickups (20–40/stage, 50 pts each), speed bonus, no-damage bonus, rank display (Bronze/Silver/Gold), stage-complete tally animation.

**T4 (replay incentive):** UpgradeChips (4 per world, hidden side-rooms), permanent stat boosts, Gold-rank chase UI, replay of cleared stages.

**T5 (W2 boss + final content):** Absolute Zero boss (4 phases), W2-specific hazards (ice plates, coolant vents), victory credits roll.

Every system in §4 is tagged with its tier at point of specification.

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- **Unit:** 1 logical pixel. Canvas backing store = physical pixels; logical viewport = **960 × 540** units. CSS transform scales canvas to window; all game math in logical px.
- **Axes:** X increases rightward. Y increases **downward** (canvas-native). "Up" = −Y. Gravity = positive Y acceleration.
- **Origin:** Top-left of logical viewport (0, 0). World origin also (0, 0); camera offset translates world→viewport.
- **Tile grid:** 32 × 32-unit tiles. `(tx, ty)` → world `(tx*32, ty*32)`.
- **Ground rule:** Lowest solid tile row is the floor. Feet at `y = floorTileRow*32`. No infinite ground; `y > stageHeight + 64` → fall death.
- **Stage dimensions:** Normal = 4800 × 704 px (150 × 22 tiles). Boss arena = 1216 × 704 px (38 × 22 tiles), camera locked.
- **Fixed timestep:** `DT = 1/60` s. Each rAF frame: accumulate real Δt; while accumulator ≥ DT run one tick; clamp accumulator to 5 DTs max. After all ticks: render once.

## 1.2 Important conventions

**Tick system order (strict):**

| # | System | Why |
|---|---|---|
| 1 | `input.update()` | Latch key states, build frame snapshot |
| 2 | `progression.update()` | Stage transitions / death → reload before physics |
| 3 | `level.update()` | Animate tiles, move platforms, tick hazards |
| 4 | `player.update()` | Input → velocity → position → collision |
| 5 | `weapons.update()` | Fire, advance bullet pool |
| 6 | `enemies.update()` | AI, movement, bullet/player collision |
| 7 | `camera.update()` | Follow, clamp, shake decay |
| 8 | `audio.update()` | Flush queued SFX |
| 9 | `renderer.draw()` | **After all ticks**, once per frame |

**Random source:** One seeded PRNG `rng` (32-bit xorshift). `rng.next()` → float [0,1). `rng.nextInt(n)` → int [0,n). Reseeded via `seed(n)` or at stage start. **No `Math.random()` anywhere.**

**Controls table:**

| Action | Primary | Alternate | Touch |
|---|---|---|---|
| Move left | A / ← | — | Left-half dpad ← |
| Move right | D / → | — | Left-half dpad → |
| Jump | W / ↑ / Space | — | Swipe-up anywhere |
| Crouch (hold) | S / ↓ | — | Left-half dpad ↓ |
| Fire (hold) | J / Enter / Z / left-click | — | Right-half tap/hold |
| Reload | R | — | Bottom-left reload btn |
| Gun select | 1 / 2 / 3 / 4 | — | Bottom-right circular btn (cycles) |
| Gun cycle | K / Shift / scroll-wheel | — | Bottom-right circular btn |
| Pause | P / Escape | — | Pause icon top-right |

**Camera:** Deadzone 80 px H, 60 px V. Lerp X 0.08/tick, Y 0.12/tick. Player offset 35% from left viewport edge. Clamp `camera.x ∈ [0, stageWidth − 960]`, `camera.y ∈ [0, stageHeight − 540]`. Screen shake: additive random offset, 4 px / 0.3 s decay (light); 10 px / 0.6 s (heavy).

**Conventions carried from engineering:** All entity positions in world px. `resolveAABB` queries tilemap in world coords (immune to camera). Culling window padded ±1 tile. `step()` cancels rAF; `_stepping` flag guards the loop.

---

# 2. CONTRACTS

## 2.1 Module layout

| Module | File | Responsibility |
|---|---|---|
| `game` | game.js | State machine, main loop, owns `ctx` |
| `input` | input.js | Keyboard/pointer events, key-state snapshot |
| `progression` | progression.js | World/stage index, lives, score, checkpoints, stage-clear, death |
| `level` | level.js | Tilemap, hazards, platforms, parallax, generator, collision |
| `player` | player.js | Player entity: position, velocity, state, health, animation |
| `weapons` | weapons.js | 4 guns, ammo, fire timers, bullet pool, bullet physics |
| `enemies` | enemies.js | Enemy pool, per-type AI, damage, death, drops |
| `boss` | boss.js | BossPhase state machine, attack patterns |
| `camera` | camera.js | Viewport offset, follow, shake |
| `audio` | audio.js | Web Audio graph, generated SFX, music scheduling |
| `renderer` | renderer.js | Canvas 2D draw calls, parallax, tiles, entities, post-effects |
| `ui` | ui.js | HUD, title, pause, stage-clear, game-over, world-map, victory |
| `particles` | particles.js | Particle pool (explosions, dust, sparks, coins) |

## 2.2 Global context

```js
const ctx = {
  // timing
  time: 0, frame: 0, dt: 1/60,

  // rng
  rng: null, // { next(), nextInt(n), seed(n) }

  // game state
  state: 'TITLE', // 'TITLE'|'WORLD_MAP'|'STAGE_INTRO'|'PLAYING'|'PAUSED'|'STAGE_CLEAR'|'GAME_OVER'|'VICTORY'
  paused: false,

  // progression
  world: 1, stage: 1, lives: 3, score: 0,
  stageClearTimer: 0,
  checkpointReached: false,
  checkpointX: 0,
  unlockedStages: new Set(['W1S1']),
  gunUnlocked: { scrapPistol:true, rivetShotgun:false, coilRifle:false, flareLauncher:false },
  upgradeChips: [], // collected this run

  // level
  level: {
    tiles: null, // Uint8Array, width*height
    tileW: 32, tileH: 32,
    width: 150, height: 22, // tiles
    stageWidth: 4800, stageHeight: 704,
    spawnX: 120, spawnY: 656, // feet position
    flagX: 4680,
    platforms: [], // [{x,y,w,h,vx,vy,type}]
    hazards: [],   // [{x,y,w,h,type,damage,period,activeTime,timer}]
    parallax: [],  // [{layer,drawFn}]
    chests: [],    // [{x,y,contents,opened}]
    chips: [],     // [{x,y,targetGun,statBoost,collected}]
    isBossArena: false,
  },

  // player
  player: {
    x: 120, y: 608, vx: 0, vy: 0,
    w: 32, h: 48, crouchH: 28,
    facing: 1, grounded: false, crouching: false, jumping: false,
    hp: 100, maxHp: 100,
    invulnTimer: 0,
    anim: 'idle', animFrame: 0, animTimer: 0,
    gunIndex: 0, alive: true,
    chargeMeter: 0, charging: false, chargeHoldTimer: 0,
    reloadTimer: 0, reloading: false,
    swapTimer: 0, swapping: false,
    magRemaining: 12, // current gun's remaining shots
    jumpHoldTimer: 0,
  },

  // weapons
  weapons: {
    guns: [
      { name:'scrapPistol',  dmg:12, rate:6.0, ammo:12, maxAmmo:12, bulletSpeed:600, spread:2,  pellets:1, pierce:0, aoe:0,  chargeMax:0,   knockback:80,  unlocked:true  },
      { name:'rivetShotgun', dmg:9,  rate:1.4, ammo:6,  maxAmmo:6,  bulletSpeed:450, spread:18, pellets:5, pierce:0, aoe:0,  chargeMax:0,   knockback:220, unlocked:false },
      { name:'coilRifle',    dmg:15, rate:2.5, ammo:5,  maxAmmo:5,  bulletSpeed:900, spread:0,  pellets:1, pierce:3, aoe:0,  chargeMax:1.2, knockback:140, unlocked:false },
      { name:'flareLauncher',dmg:55, rate:0.8, ammo:4,  maxAmmo:4,  bulletSpeed:320, spread:4,  pellets:1, pierce:0, aoe:90, chargeMax:0,   knockback:300, unlocked:false },
    ],
    fireTimer: 0,
    bullets: [], // pool, max 128
  },

  // enemies
  enemies: {
    pool: [], // max 64
    spawnQueue: [], // [{x,y,type,timer}]
  },

  // boss
  boss: {
    active: false,
    name: '',
    x: 0, y: 0, w: 0, h: 0,
    hp: 0, maxHp: 0,
    phase: 0,
    phaseHp: 0, phaseMaxHp: 0,
    pattern: '',
    interval: 0,
    attackTimer: 0,
    telegraphTimer: 0,
    invulnFlash: 0,
    alive: true,
  },

  // camera
  camera: { x: 0, y: 0, shakeX: 0, shakeY: 0, shakeTimer: 0, shakeIntensity: 0 },

  // input snapshot
  input: {
    left:false, right:false, jump:false, crouch:false,
    shoot:false, reload:false, switchGun:false,
    gunSelect:[false,false,false,false],
    jumpPressed:false, switchGunPressed:false,
    pausePressed:false,
  },

  // audio
  audio: { ctx:null, masterGain:null, sfxQueue:[], musicPlaying:false, musicNodes:[] },

  // particles
  particles: { pool: [], maxPool: 256 },

  // render
  canvas: null, c2d: null,
  drawCalls: 0,
};
```

## 2.3 Module specifics

### `game`
```
init(canvasEl, opts) → void   // wire canvas, build ctx, install window.__game, start rAF
start() → void               // TITLE → PLAYING, loadStage(1,1)
tick() → void                // one DT tick, system order §1.2
render() → void              // renderer.draw()
pause() / resume() → void
```

### `input`
```
attach(canvasEl) → void
snapshot() → void            // write ctx.input from raw key/pointer map
isDown(action) → bool
inject(action, down) → void  // debug synthetic key
```

### `progression`
```
loadStage(world, stage) → void
checkStageClear() → void     // player.x >= flagX → STAGE_CLEAR
checkDeath() → void          // hp<=0 or y>stageHeight+64 → lose life / game over
nextStage() → void
advanceWorld() → void
openChest(chest) → void
collectChip(chip) → void
```

### `level`
```
generate(world, stage) → void  // seeded generator, §4 StageGenerator
getTile(tx,ty) → int
isSolid(tx,ty) → bool
resolveAABB(entity) → {grounded, hitX, hitY}
update() → void                // platforms, hazards, conveyor scroll
```

### `player`
```
update() → void
hurt(amount, sourceX) → void
respawn() → void               // hp=100, invulnTimer=1.5, pos=checkpoint or spawn
die() → void
```

### `weapons`
```
update() → void
fire() → void                  // spawn bullet(s), decrement magRemaining, reset fireTimer
switchGun(index) → void        // 0-3 direct, or cycle
startReload() → void
finishReload() → void
```

### `enemies`
```
update() → void
spawn(type, x, y) → int        // 0..63 or -1
damage(id, amount, dir) → bool // true if killed
```

### `boss`
```
init(name, phaseCount) → void
update() → void                // phase machine, attack timers, telegraphs
hurt(amount) → bool            // true if phase/total killed
```

### `camera`
```
update() → void
addShake(intensity, duration) → void
```

### `audio`
```
init() → void                  // AudioContext (deferred to first gesture)
playSFX(type) → void
startMusic(track) / stopMusic() → void
update() → void                // flush sfxQueue
```

### `renderer`
```
draw() → void                  // full frame: clear→parallax→tiles→entities→bullets→particles→HUD→overlays→postFX
```

### `ui`
```
drawHUD(c2d) → void
drawTitle(c2d) → void
drawWorldMap(c2d) → void
drawStageIntro(c2d) → void
drawPause(c2d) → void
drawStageClear(c2d) → void
drawGameOver(c2d) → void
drawVictory(c2d) → void
```

### `particles`
```
emit(type, x, y, count, params) → void
update() → void
draw(c2d) → void
```

---

# 3. VISUAL SPEC

**The look:** A vast abandoned mega-factory rendered in thick, confident vector shapes with a warm-to-cool duotone palette: deep charcoal (#1A1A2E) foundations, hot molten amber (#FF8C00) and electric cyan (#00F5FF) accent lighting, and bruised violet (#4A1A6B) midtones. Everything reads as heavy industrial machinery—riveted plate, dripping coolant, spinning gears, hissing valves—stylised into clean geometric silhouettes with 3-px dark outlines (#0D0D1A). The player is a broad-shouldered, short-legged, helmeted salvage mechanic with a single glowing visor slit and a visible gun at arm-tip. Enemies are mechanical: squat furnace-bellied bots, hovering hexagonal drones with spinning rotors, tall insectoid stalkers. The one screenshot that sells the game: the player mid-air crouched-then-jumping over a conveyor belt of glowing ore, muzzle-flash painting the scene amber, two rivet-drones exploding into sparks, and three receding parallax layers of factory architecture fading into violet haze.

**Lighting and atmosphere:** No global light. Ambient tint overlay per world: W1 = #FF8C00 at 8% multiply; W2 = #00F5FF at 6% multiply. Point-light sources drawn as radial-gradient circles (additive blend): furnace glow (#FF4500→transparent, 200u radius, 3–5/stage, pulse ±20u 2s); coolant lamp (#00F5FF→transparent, 160u, 3–5/stage, flicker 5% 8Hz); muzzle flash (weapon colour, 40u, 0.08–0.15s); enemy eye glow (#FF4500 or #00F5FF, 20u, pulse ±4u 1.5s); exit door glow (#FFD700, 120u, pulse ±15u 2s); pickup glow (item colour, 30u). Zones 2 and 4 have a "shadow corridor" (vertical band 300u wide, 60%-opacity #0D0D1A overlay, broken by point-lights). Far parallax at 70% opacity, mid at 85%. Horizontal edge fade 80u. Post-effects (T2): vignette always (edges 35% darker #0D0D1A); chromatic aberration on hit (2px RGB split, 0.2s); screen shake on hit/explosion (4px/0.3s) and boss-death/stage-complete (10px/0.6s); white flash on pickup/boss-death (60%, 0.12s); red flash on damage (40%, 0.15s); heat distortion near slag (2px sine, 0.4s); frost bloom near ice (crystal particles, fade 1s); grain always (3% noise, 12fps); slow-mo tint on boss final hit (desaturate 40%, 0.8s).

**The space:** Each stage is a horizontal strip 4800 × 704 units (150 × 22 tiles). Camera viewport 960 × 540. Player starts at X=120, feet at Y=656 (W1) or Y=624 (W2, ground raised 1 row for frost tiles). Boss arena (stage 5): 1216 × 704, camera locks, no scroll. Five zones per stage (~960u wide each):

| Zone | W1 (Smelting Yards) | W2 (Cooling Towers) | Eye-cue |
|---|---|---|---|
| 1 Entry | Loading dock, crates, forklift silhouettes | Airlock vestibule, frost-rimmed pipes | Warm floor glow vs cold blue |
| 2 Gauntlet | Conveyors, piston platforms, slag pits | Cryo-tunnels, ice plates, vent shafts | Horizontal motion vs vertical ice |
| 3 Combat | Smelter floor, molten channels, crane hooks | Coolant reservoir, floating debris | Orange light pools vs cyan |
| 4 Puzzle | Gear-maze, pressure-plate bridges | Thermal-exchange, valve doors | Rotating cogs vs liquid-flow pipes |
| 5 Exit | Blast furnace core, heat-shimmer | Central chiller, frozen fountain | Red/amber shift vs blue/white |

**World differentiation:** W1 palette amber/red/charcoal; W2 cyan/white/deep-blue. Floor tiles: riveted steel (W1) vs frosted ceramic (W2). Parallax: smokestacks & gears (W1) vs condensation towers & water pipes (W2).

**Parallax (3 layers, all stages):**

| Layer | Content | Colour range | Scroll |
|---|---|---|---|
| Far (sky) | Gradient + silhouetted smokestacks / condensation towers | W1 #1A0A00→#4A1A6B; W2 #0F1F33→#1A2A4A | 5% camera |
| Mid (factory shell) | Gear silhouettes, pipe networks, building outlines | W1 #2A1F10→#3D2B5F; W2 #0F1F33→#1E3A5F | 20% camera |
| Near (foreground) | Dangling cables, steam wisps, partial pipes | #0D0D1A + accent glow | 60% camera |

**Recipe table:**

### Tiles & Environment

| Name | Shape | Size (px) | Colours | Count | Motion |
|---|---|---|---|---|---|
| Ground plate (W1) | Rounded rect, 3px stroke #0D0D1A, gradient fill, rivet dots every 60u | 64×32 (2×1 tile) | #2A2A3E→#1A1A2E, stroke #0D0D1A | ~150 | Static |
| Ground plate (W2) | Same, frost crystal overlay (3 white triangles) | 64×32 | #1E3A5F→#0F1F33, #FFFFFF | ~150 | Static |
| Platform (floating) | Rounded rect, top-edge highlight | 128×24 (4×0.75 tile) | #3D2B5F, highlight #FF8C00/#00F5FF | ~40 | Bob ±4u sine 2s |
| Conveyor belt | Rect, scrolling 45° stripes 20px spacing | 200×32 | #1A1A2E base, #FF8C00/#00F5FF stripes | ~8 | Stripe-scroll 60u/s |
| Piston platform | Rect + cylindrical stem | 100×20 + 20×60 | #4A4A5E, #2A2A3E | ~6 | Extend/retract 1.5s |
| Slag pit (W1) | Wavy-top rect, inner glow | 160×40 | #FF4500 core, #FF8C00 glow, #1A0A00 rim | ~4 | Heat shimmer 2px sine 0.5s |
| Ice plate (W2) | Rect, 2 crack lines, translucent | 120×16 | #A8E6FF 70%, #FFFFFF cracks | ~5 | Static; shatters on stomp |
| Wall / backdrop | Tall rect, riveted, 2px stroke | 64×300 | #1A1A2E, stroke #0D0D1A | ~30 | Static |
| Pipe (h/v) | Rounded rect 16u tall, joint circles every 100u | variable×16 | #3D3D5E, joints accent | ~25 | Static |
| Blast door (exit) | Arch-top rect, 2 halves, gear motif | 140×200 | #2A2A3E, gear accent, stroke #0D0D1A | 1 | Halves slide apart 0.6s ease-out |
| Breakable wall | Rect with crack lines, hp 1-3 | 64×64 | #4A3520, cracks #FFD700 | per stage | Shatters on 3 hits |

### Props & Decor

| Name | Shape | Size | Colours | Count | Motion |
|---|---|---|---|---|---|
| Crate stack | 2–3 offset rounded rects, X-brace | 50×50 each | #4A3520, #2A1F10, stroke #1A0F05 | ~12 | Static; destructible |
| Gear (wall) | 8-tooth circle, inner hole | 80 dia | #3D3D5E, teeth #4A4A5E | ~10 | Rotate 30°/s |
| Valve wheel | Circle + 4 spokes | 50 dia | accent, rim #1A1A2E | ~8 | Static; glow near player |
| Steam vent | Small rect + particle emitter | 24×12 | #2A2A3E | ~10 | 3 white particles/s, rise 40u |
| Frost drip (W2) | Icicle triangle | 12×20 | #A8E6FF | ~10 | Drip particle every 2s |
| Warning sign | Triangle + exclamation | 30×30 | #FFD700, stroke #1A1A2E | ~6 | Flash 1s on/off within 200u |
| Crane hook | Arc + line + triangle | 40×80 | #3D3D5E, hook accent | ~4 | Swing ±15° sine 3s |

### Weapons (held at arm-tip, drawn)

| Name (gameplay) | Visual name | Shape | Size | Colours | Muzzle / Effect |
|---|---|---|---|---|---|
| Scrap Pistol | Pulse Pistol | Small L-shape, cyan tip | 18×12 | #3D3D5E, tip #00F5FF | 10u cyan circle, 0.08s |
| Rivet Shotgun | Scatter Cannon | Wide double-barrel | 24×16 | #4A3520, ends #FF8C00 | 20u amber star, 0.12s; 5 pellets |
| Coil Rifle | Rail Driver | Long thin barrel, glowing rail line | 32×10 | #1A1A2E, rail #00F5FF | Charge: rail brightens 0.3s; fire: 200u cyan beam 0.1s |
| Flare Launcher | Acid Sprayer | Bulbous nozzle + hose coil | 22×18 | #2A4A1A, nozzle #7FFF00 | 5–8 green droplet arc, 0.5s lifetime |

### Pickups & Effects

| Name | Shape | Size | Colours | Motion |
|---|---|---|---|---|
| Ammo crate | Small rect, weapon icon | 30×24 | #2A2A3E, icon=weapon colour | Bob ±3u 1s, glow outline |
| Health orb | Cross in circle | 24×24 | #FF4500 cross, #FFFFFF circle | Pulse 1.0→1.1, 1s |
| Gun chest | Ammo crate + spinning icon above | 30×36 | weapon colour | Icon spin 180°/s |
| Coin | Small circle, inner ring | 16×16 | #FFD700, inner #FFA500 | Spin: ellipse squash 0.8s |
| Upgrade chip | Tiny circuit-board rect | 20×14 | #00F5FF, trace #FF8C00 | Pulse glow 1.5s |
| Bullet (player) | Circle or line-segment | 4–6 | weapon colour, 80% trail | Linear |
| Bullet (enemy) | Small circle | 6 | #FF4500, trail 40% | Linear |
| Explosion (small) | Expanding circle + 6–8 spark lines | 40→80u | #FFD700→#FF4500→transparent | 0.3s |
| Explosion (large) | Circle + 12 sparks + smoke | 80→200u | #FF4500→#1A1A2E smoke | 0.5s |

### UI Surfaces

| Name | Shape | Size | Colours | Position |
|---|---|---|---|---|
| HUD bar | Rounded rect, semi-transparent | 400×48 | fill #0D0D1A 70%, stroke #3D3D5E | Top-left, 16u margin |
| Health bar | Segmented fill | 120×12 | bg #1A1A2E, fill #FF4500→#FFD700 | Inside HUD left |
| Ammo counter | Text + weapon icon | 80×16 | #00F5FF text, #3D3D5E icon | Inside HUD right |
| Weapon name tag | Text label | auto | #FF8C00 | Below HUD |
| Stage title card | Full-width banner | 960×80 | Text #FFFFFF, bg fade | Center, 2s fade |
| Pause overlay | Full viewport | 960×540 | #0D0D1A 80%, text #FFFFFF | Center |
| Game-over screen | Full viewport | 960×540 | #1A0A00 bg, text #FF4500, heavy vignette | Center |
| World map | 2 rows × 5 circles | 600×300 | Completed=#FF8C00, next=#00F5FF pulse, locked=#3D3D5E | Center |
| Charge meter | Bar under crosshair area | 100×8 | bg #1A1A2E, fill #00F5FF→#FFFFFF | Below player |
| Boss HP bar | Centered top bar | 400×16 | bg #1A1A2E, fill #FF4500 | Top-center, boss only |

---

# 4. GAMEPLAY SPEC

**The game in one paragraph:** You are Kael, a salvage mechanic fighting through two hostile industrial zones (Smelting Yards, Cooling Towers) to reclaim the city's power grid. Minute to minute you run, jump, crouch under low pipes, and shoot waves of automated enemies and hazards across scrolling stages. You swap between four salvaged guns on the fly—tap-fire, spread, charge-release, lobbed explosion—so combat is a constant decision about spacing, timing, and which tool the current fight demands. Stages are short (45–90 s of skilled play) and end at a blast-door extraction point; the final stage of each world is a multi-phase boss. You get 3 lives per stage attempt and unlimited retries; dying resets you to the stage start or checkpoint with full HP but no score bonus. Clearing W2S5 (Absolute Zero) triggers a victory screen and 30-s credits. Between stages you pick from a world map; replaying cleared stages chases Gold rank and 4 hidden upgrade chips per world.

## Records and Rosters

**Player:** hp 0–100 (start 100), lives 0–3 (start 3), score 0+, activeGun enum{scrapPistol,rivetShotgun,coilRifle,flareLauncher} (start scrapPistol), speed (current vx), vx/vy px/s, grounded bool, crouching bool, facing {−1,+1} (start +1), hitTimer float (i-frames), chargeMeter 0–1.

**Gun roster (4):**

| Gun | damage | fireRate | projSpeed | spreadDeg | magSize | reloadTime | knockback | pierce | aoeRadius | chargeMax | unlock |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Scrap Pistol | 12 | 6.0 | 600 | 2 | 12 | 1.4 | 80 | 0 | 0 | 0 | start |
| Rivet Shotgun | 9×5 pellets | 1.4 | 450 | 18 | 6 | 2.2 | 220 | 0 | 0 | 0 | W1S2 chest |
| Coil Rifle | 40 charged / 15 tap | 2.5 | 900 | 0 | 5 | 2.8 | 140 | 3 | 0 | 1.2 | W1S4 chest |
| Flare Launcher | 55 | 0.8 | 320 (arc) | 4 | 4 | 3.5 | 300 | 0 | 90 | 0 | W2S2 chest |

**Enemy roster:**

| Enemy | hp | damage | speed | patrolRange | aggroRange | knockbackResist | score |
|---|---|---|---|---|---|---|---|
| Crawler (Smelter Bot W1 / Cryo Stalker W2) | 30 | 15 | 120 | 80 | 200 | 0.0 | 100 |
| Turret | 50 | 10 (proj) | 0 | 0 | 350 | 1.0 | 200 |
| Drone (Rivet Drone) | 20 | 12 | 160 | 120 | 280 | 0.2 | 150 |
| ShieldTrooper | 80 | 20 | 70 | 60 | 240 | 0.6 | 350 |
| Boss | per phase | — | — | — | — | 1.0 | 1000/phase |

**Projectile:** owner {player,enemy}, vx/vy, damage, pierceLeft, aoeRadius, lifetime 3.0 s default.

**Tile:** type {solid, platform, slope45, spike, conveyor, breakable}, solidity bool, hp (breakable 1–3), conveyorSpeed ±120.

**Hazard:** type {spike, steamVent, crushingPiston, electricFloor}, damage (spike 20, steam 12, piston 30, electric 18), period (0=always-on), activeTime.

**BossPhase:** hp, pattern {sweep,volley,charge,summon,lasersweep,volleyhoming,floorelectric,rotation}, interval, transitionAt.

**Stage:** id "W1S1"…"W2S5", width 4800 (boss 1216), height 704, seed int, goldThreshold, silverThreshold, bronzeThreshold.

**UpgradeChip (4 per world):** targetGun, statBoost {damage+4, fireRate+1, magSize+2, reloadTime−0.4}, permanent true.

## Systems

### Locomotion [T1]

- **Move:** A/← → vx toward −280 px/s; D/→ → toward +280 px/s. Accel 2400 px/s², friction/decel 1800 px/s² (no key). Facing = last horizontal input.
- **Jump:** W/↑/Space pressed AND grounded → vy = −520 px/s. Variable height: release within 0.18 s → vy cut to −260 px/s.
- **Crouch:** S/↓ held AND grounded → crouching=true; hitbox h: 48→28 px; max speed 140 px/s; jump disabled. Release S restores.
- **Gravity:** vy += 1600 px/s² per tick while airborne. Terminal vy = 700 px/s.
- **Conveyor:** Standing on conveyor adds ±120 px/s to vx per tick.
- **Platform (one-way):** Pass through from below/sides; land on top edge only when falling.
- **Breakable:** 3 projectile hits → removed from collision.
- **Slope45:** Horizontal speed converts to 45° diagonal at same magnitude. Jump off slope retains diagonal direction.
- **Crouch-fire:** Muzzle drops to 28 px above feet; spreadDeg halved. Cannot jump while crouch-firing.

### Shooting [T1]

- **Fire:** J/Enter/Z/click held AND magRemaining > 0 AND not reloading → spawn bullet at muzzle (facing, 8 px from hitbox edge) with gun's bulletSpeed, damage, spreadDeg jitter. Decrement magRemaining. Repeat at 1/fireRate intervals.
- **Coil Rifle charge:** Fire held ≥ 0.25 s → stop auto-fire, charge chargeMeter 0→1 over 1.2 s. Release: damage = 15 + 25×chargeMeter, pierce=3. Tap (<0.25 s): 15 dmg normal.
- **Flare Launcher arc:** Launch 45° above facing at 320 px/s; gravity 800 px/s²; first contact with solid/enemy → detonate 55 dmg in 90 px radius, knockback 300 px/s radial.
- **Reload:** Auto at magRemaining=0, or R. During reloadTime cannot fire. Mag resets to magSize.
- **Gun swap:** 1/2/3/4 select; K/Shift/scroll cycles. Swap takes 0.3 s (no fire).
- **Crouch-fire accuracy:** spreadDeg halved while crouching.

### DamageAndDeath [T1]

- **Player hit:** Contact enemy or enemy projectile, hitTimer==0 → hp -= damage; hitTimer=1.0; knockback 180 px/s away from source. While hitTimer>0: invulnerable.
- **Player dies:** hp≤0 → lives--. If lives>0: respawn at checkpoint (or start), hp=100, hitTimer=1.5, score kept. If lives==0: → GAME_OVER → Stage Select (same stage, lives reset 3).
- **Enemy dies:** hp≤0 → remove, score += value. Drop: 20% ammo (mag +3), 8% health orb (+15 hp).
- **Hazard damage:** Contact → damage once per hitTimer window.
- **Fall death:** y > stageHeight + 64 → instant death (same as hp≤0, no knockback).

### EnemyAI [T1 (Crawler, Drone) / T3 (Turret, ShieldTrooper)]

- **Perception:** Euclidean dist to player center ≤ aggroRange → CHASE; else PATROL.
- **Crawler PATROL:** Walk speed toward nearest patrolRange edge; reverse at boundary. CHASE: speed×1.4 toward player. Contact = damage.
- **Turret:** Stationary. CHASE: aim player, fire projectile (dmg 10, speed 300) every 1.8 s. knockbackResist 1.0.
- **Drone:** Hovers at player.y − 60. PATROL: sinusoidal bob ±30 px, period 2 s. CHASE: drift toward player at speed. Contact = damage. Hit only by projectiles >20° above horizontal or jump-contact.
- **ShieldTrooper:** PATROL: walk slowly. CHASE: advance at speed. Front ±60° arc blocks projectiles (shield pool 60 hp separate). Shield break → normal. Attack: 1 s wind-up lunge (30 px/s × 0.5 s), contact = damage.
- **Knockback:** Apply gun.knockback × (1 − enemy.knockbackResist) as instantaneous vx impulse away from projectile.

### BossAI [T1 (Furnace Colossus) / T5 (Absolute Zero)]

- Phase sequence; phase hp reaches transitionAt fraction → 1.5 s invuln flash → next phase.
- **Furnace Colossus (W1S5):** 3 phases, HP 200/200/200. Arena 1216×704, camera locks.
  - P1 sweep (interval 2.5 s): walk 400 px range, arm swing (hitbox 60 px, dmg 25).
  - P2 volley (interval 3.0 s): stop, fire 5 fan projectiles (dmg 12, speed 280).
  - P3 charge+summon (interval 2.0 s): telegraph 1 s → dash 500 px/s (dmg 35); every 6 s summon 2 Crawlers.
- **Absolute Zero (W2S5):** 4 phases, HP 180/180/180/180. Arena 1216×704.
  - P1 laser sweep: horizontal beam 2 s active, dmg 20/s contact.
  - P2 volley: 8 homing drones (dmg 15, speed 180, lifetime 4 s).
  - P3 floor electrification: entire arena floor = electricFloor 3 s, period 5 s; floating platforms safe.
  - P4 rotation: all three attacks, interval 1.5 s.
- Boss immune to knockback. Damaged from any angle.

### StageGenerator [T1]

- **Inputs:** seed, width (4800/1216), height 704, worldTheme (1=Smelting, 2=Cooling), difficultyTier (=stage number 1–5).
- **Placement order:**
  1. Ground layer: solid tiles along bottom (y=672). Gaps 3–6 tiles at 8–14 tile intervals (more at higher tier). 15% of gaps get breakable tile.
  2. Platform tier: every 6–10 tile interval, one-way platform at y=528 or y=416. Width 3–7 tiles.
  3. Hazard scatter: spikes on 10–20% ground (never within 2 tiles of gap edge). 1 steamVent per 12 tiles (period 3 s, active 1.5 s). Tier≥3: crushingPiston (period 4 s, active 1.0 s).
  4. Enemy spawns: one per 10–16 tiles. Tier 1: Crawler. Tier 2: +Turret. Tier 3: +Drone. Tier 4: +ShieldTrooper. Tier 5: mix all.
  5. Chest/pickup: gun-unlock chest at hard-coded stages (W1S2→Shotgun, W1S4→Coil, W2S2→Flare). Health orb every 20 tiles.
  6. Blast door at x = width − 120. Reaching it → STAGE_CLEAR.
  7. Hidden side-room (T4): stages 1,3 of each world: breakable wall, 200×120 room, UpgradeChip.
- **Verifier (post-gen):**
  - Max gap ≤ 6 tiles; platform within 12 px V and 120 px H of gap edge.
  - No enemy inside solid tile.
  - No hazard within 200 px of blast door.
  - BFS walkable+jumpable (max jump 120 px H, 84 px V) confirms door reachable from spawn.
  - Fail → re-roll seed+1.

### ProgressionAndUnlocks [T1]

- W1S1 unlocked at start. Clearing unlocks next. W1S5 clear → W2S1. W2S5 clear → VICTORY.
- Gun chests: W1S2→Rivet Shotgun; W1S4→Coil Rifle; W2S2→Flare Launcher. `unlocked=true` persists across deaths within run.
- Checkpoints: 1 mid-stage flag per stage. Touching saves respawn position (lost on full game-over).
- UpgradeChips (T4): 4 per world, permanent stat boost for run.

### Scoring [T1 base / T3 bonuses]

- Kill points: Crawler 100, Turret 200, Drone 150, ShieldTrooper 350, Boss-phase 1000.
- Coins: 20–40/stage × 50 pts (T3).
- Speed bonus: ≤60% par (par = width/200 s) → +500 (T3).
- No-damage bonus: hp==100 at door → +1000 (T3).
- Chip bonus: +250 per chip (T4).
- Rank thresholds per stage: bronze/silver/gold (in Stage record). Displayed on StageComplete.

### TouchControls [T1]

- Left half: virtual dpad (←,→,↓ crouch). Swipe-up on left half = jump.
- Right half: tap = fire; hold = auto-fire / charge (coil). Swipe-up = jump (redundant).
- Bottom-right: circular gun-swap button (cycles unlocked).
- Bottom-left: reload button.
- All map to same rule IDs as keyboard; no separate tuning.

## Progression and Difficulty

**Order:** W1S1→W1S2(shotgun)→W1S3→W1S4(coil)→W1S5(Furnace Colossus)→W2S1→W2S2(flare)→W2S3→W2S4→W2S5(Absolute Zero)→Victory.

**Early (W1S1–S2):** Crawlers only (30 hp, 3 pistol hits). Continuous ground, 3-tile gaps. 3 lives. Pistol 6/s × 12 dmg.

**Mid (W1S3–S4, W2S1–S3):** Turrets force positioning. Drones punish ground. ShieldTroopers demand shotgun/coil. Gaps 5–6 tiles. Steam+pistons. Expected 1–2 deaths/stage; checkpoints soften.

**Late/Boss:** Furnace Colossus P3 needs all 3 guns. Absolute Zero P3 forces platforming under fire; P4 demands mid-fight swaps. Boss HP 200/180 per phase ≈ 15–20 hits; fight 60–90 s.

**Recovery:** Death→checkpoint/start, full HP, 1.5 s i-frames, score kept, −1 life. All lives→Stage Select, immediate retry. No permadeath. 3 lives reset each attempt.

**Scaling knobs:** difficultyTier 1–5: enemy density (16→10 tiles), gap width (3→6), hazard count, enemy mix. Boss intervals 2.5→1.5 s. UpgradeChips: +4 dmg or +1 rate per chip.

## Feel

| Parameter | Value | Tuned to |
|---|---|---|
| Run speed | 280 px/s | 4800 px in ~25 s sprint; snappy |
| Accel | 2400 px/s² | Top speed in ~0.12 s |
| Friction | 1800 px/s² | Stop in ~0.16 s; crisp |
| Jump vy | −520 px/s | Peak ≈ 84 px (2 tiles); clears 3-tile gaps |
| Jump cut | 0.18 s / −260 | Short-hop 30 px |
| Gravity | 1600 px/s² | Hang-time ~0.65 s |
| Crouch h | 48→28 px | Fits under 32-px pipes |
| Crouch speed | 140 px/s | Mobile but vulnerable |
| Hit i-frames | 1.0 s | Escape but punishing |
| Death i-frames | 1.5 s | Grace on respawn |
| Pistol rate | 6.0/s (167 ms) | Tap-rap rhythm |
| Shotgun rate | 1.4/s (714 ms) | Heavy pump |
| Coil charge | 1.2 s | Risky but usable in 2-s window |
| Flare rate | 0.8/s (1.25 s) | Each shot is an event |
| Shotgun knockback | 220 px/s × 1.0 | Crawler tumbles ~0.3 s |
| Pistol knockback | 80 px/s | Small nudge |
| Enemy→player knockback | 180 px/s | ~0.25 s push |
| Projectile lifetime | 3.0 s | ~1800 px at pistol speed |
| Reload times | 1.4–3.5 s | Pistol fast; flare commits |
| Gun swap | 0.3 s | Fluid; prevents stacking |
| Boss telegraph | 1.0 s | Readable; jump/crouch dodge |
| Boss phase flash | 1.5 s invuln | Breather; "new pattern" |
| Stage par | width/200 s (4800→24 s) | Skilled ~20–25 s; Gold <14 s |
| Camera deadzone | 80 H, 60 V | See threats; no jitter |
| Camera lerp | X 0.08, Y 0.12 | Smooth, no rubber-band |
| Touch fire radius | 72 px | Thumb target 6" phone |

---

# 5. CHARACTERS

## Player — "Kael"

**Silhouette:** Broad-shouldered, short-legged, helmeted figure, single glowing visor slit (#00F5FF). Gun always visible at arm. Squishy proportions (head = 30% height) for small-size readability. Crouch halves silhouette. Collision hitbox 32×48 (standing) / 32×28 (crouch). Drawn sprite 36×56 / 36×36.

**Facings:** 2 (left, right). No up/down.

| Animation | Rule | Duration |
|---|---|---|
| Idle | 4-frame bob: torso Y 0,−2,0,+2. Visor pulses. | 1.5 s loop |
| Run | 4-frame leg cycle (contact,down,pass,up). Torso lean 10°. Gun bob 1u. | 0.32 s loop |
| Jump ascent | Legs tuck, arms up. Squash 0.9w×1.1h. | Hold until apex |
| Jump descent | Legs extend, arms out. Stretch 1.1w×0.9h. | Hold until land |
| Land | 3-frame squash 1.2w→1.0→0.95. Dust puff 2 grey circles 10u fade 0.3s. | 0.2 s |
| Crouch | Torso 60%. Head drops. Gun aims down 15°. | Instant, hold |
| Fire (all guns) | Arm recoil back 4u, muzzle flash. 2-frame: fire→recover. | 0.1–0.15 s |
| Hurt | White flash 3× at 0.05s. Lean back 15°. | 0.3 s |
| Death | Fall backward, spin 180°, dissolve 8 amber/cyan particles. | 1.0 s |

## Crawler / Smelter Bot (W1) / Cryo Stalker (W2)

**Silhouette (W1):** Wide squat rect torso, 2 stubby arms, furnace-glow chest. 48×44. Reads "tank."
**Silhouette (W2):** Tall narrow rect, 4 thin legs, frost-crystal head. 32×52. Reads "fast threat."
**Facings:** 2.

| Animation | Rule | Duration |
|---|---|---|
| Idle (W1) | Chest glow pulse #FF4500→#FF8C00. Sway. | 1.5 s |
| Idle (W2) | 4 legs micro-shift. Head tilt ±8°. Crystal glints. | 1.0 s |
| Walk (W1) | 2-frame stomp. Ground shake 1px. | 0.5 s loop |
| Dash (W2) | Stretch 1.3× horizontal, 3 afterimages. | 0.2 s |
| Fire | Arm extends (W1) / head snaps forward (W2). | 0.2–0.3 s |
| Hurt | Flash, stagger/recoil. | 0.2–0.25 s |
| Death | Collapse inward (W1) / shatter 6 triangles (W2). | 0.4–0.6 s |

## Turret

**Silhouette:** Stationary box with rotating barrel. 32×32. #3D3D5E, barrel accent.
**Facings:** 2 (barrel flips).

| Animation | Rule | Duration |
|---|---|---|
| Idle | Barrel rotates toward player. LED pulse. | Continuous |
| Fire | Barrel flash #FFD700, projectile spawn. | 0.15 s |
| Hurt | Flash, shake 2px. | 0.2 s |
| Death | Explode (small), barrel droops. | 0.3 s |

## Drone / Rivet Drone

**Silhouette:** Small hexagon body, 2 eye dots, single rotor. 28×28. #4A4A5E, eyes #FF4500, rotor #A8E6FF.
**Facings:** 2.

| Animation | Rule | Duration |
|---|---|---|
| Hover | Y bob ±6u sine. Rotor 360°/s. Tilt toward player. | 1.2 s loop |
| Fire | Tilt forward 10°, eye flash #FFD700. | 0.15 s |
| Hurt | Flash, drop 10u, wobble. | 0.2 s |
| Death | Spin+shrink to 0, then small explosion. | 0.3 s |

## ShieldTrooper

**Silhouette:** Armoured humanoid, large front shield plate. 40×56. #2A2A3E, shield #FF8C00 (W1)/#00F5FF (W2).
**Facings:** 2.

| Animation | Rule | Duration |
|---|---|---|
| Idle | Shield glows. Slow sway. | 2 s |
| Walk | 2-frame march. | 0.6 s loop |
| Lunge wind-up | Crouch 0.5 s, shield forward. | 1.0 s |
| Lunge | Extend 30 px/s × 0.5 s. | 0.5 s |
| Shield break | Shield shatters (4 fragments), flash. | 0.3 s |
| Hurt | Flash, stagger. | 0.25 s |
| Death | Collapse, shield clatters. | 0.5 s |

## Boss — Furnace Colossus (W1S5)

**Silhouette:** Massive 160×200, furnace torso, 2 hydraulic arms, smokestack head. #1A0A00 body, #FF4500 core, #FF8C00 arms, #3D3D5E stack.

| Animation | Rule | Duration |
|---|---|---|
| Idle | Core pulse, smokestack puffs (3 grey circles/s), sway. | 2 s loop |
| Arm sweep | Right arm arcs 120° forward, ground cracks (4 lines). | 0.8 s |
| Slag vomit | Head tilts back, orange stream projectile. | 1.0 s |
| Charge telegraph | Arms pull back, core flares white, 1 s. | 1.0 s |
| Dash | Full-speed cross, ground cracks trail. | 0.4 s |
| Hurt | Core flash white, 3 sparks, stagger 4px. | 0.3 s |
| Phase transition | 1.5 s invuln, body flashes, new pattern indicator. | 1.5 s |
| Death | Core overcharges white→red, 5 explosions over 2 s, collapse, screen flash. | 2.5 s |

## Boss — Absolute Zero (W2S5)

**Silhouette:** Tall 120×220, crystalline humanoid, 4 floating ice shards orbiting. #0F1F33, #A8E6FF shards, #00F5FF eyes.

| Animation | Rule | Duration |
|---|---|---|
| Idle | Float ±8u. 4 shards orbit 120°/s radius 60u. Eyes glow. | 3 s loop |
| Shard throw | 1 shard detaches, fires toward player. | 0.3 s |
| Ice storm | Spin 360°, 4 shards cross-pattern, frost overlay. | 1.2 s |
| Laser sweep | Arms spread, beam sweeps L→R. | 2.0 s |
| Floor charge | Raises arms, floor glows cyan 1 s telegraph. | 1.0 s |
| Hurt | Flash #A8E6FF, shards wobble, frost particles. | 0.3 s |
| Phase transition | 1.5 s, shards reconfigure. | 1.5 s |
| Death | Shards shatter outward, body freezes solid, cracks into 12 pieces. | 2.0 s |

---

# 6. AUDIO

All sounds generated via Web Audio API (oscillators + noise buffers + gain envelopes). No external files.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| scrapPistol_fire | Square, 440 Hz, 0.06 s, attack 0.005 decay 0.055, vol 0.3 | Player fires Scrap Pistol |
| rivetShotgun_fire | Sawtooth, 120 Hz, 0.12 s, attack 0.005 decay 0.115, vol 0.5; + noise burst 0.08 s | Player fires Rivet Shotgun |
| coilRifle_charge | Sine sweep 200→800 Hz over 1.2 s, vol 0.15 | Player holds Coil Rifle fire ≥0.25 s |
| coilRifle_fire | Triangle, 1200 Hz, 0.08 s, attack 0.002 decay 0.078, vol 0.4 | Coil Rifle released |
| flareLauncher_fire | Noise, bandpass 300 Hz, 0.2 s, attack 0.01 decay 0.19, vol 0.45 | Player fires Flare Launcher |
| flare_detonate | Noise, lowpass 200 Hz, 0.35 s, attack 0.005 decay 0.345, vol 0.6 | Flare contacts surface/enemy |
| bullet_impact | Square, 800 Hz, 0.04 s, attack 0.002 decay 0.038, vol 0.2 | Player bullet hits enemy |
| bullet_wall | Triangle, 200 Hz, 0.03 s, vol 0.15 | Player bullet hits wall |
| enemy_shoot | Square, 300 Hz, 0.05 s, vol 0.25 | Turret/Drone fires |
| jump | Sine sweep 300→600 Hz, 0.1 s, vol 0.2 | Player jumps |
| land | Noise, lowpass 400 Hz, 0.06 s, vol 0.15 | Player lands |
| crouch | Sine 150 Hz, 0.04 s, vol 0.1 | Player crouches |
| player_hit | Square, 100 Hz, 0.15 s, vol 0.5; + noise 0.1 s | Player takes damage |
| player_die | Sawtooth sweep 400→80 Hz, 0.6 s, vol 0.5 | Player dies |
| enemy_die_small | Noise, highpass 2000 Hz, 0.15 s, vol 0.3 | Crawler/Drone/Turret dies |
| enemy_die_large | Noise, lowpass 500 Hz, 0.4 s, vol 0.5 | ShieldTrooper dies |
| boss_hurt | Triangle, 250 Hz, 0.1 s, vol 0.35 | Boss takes damage |
| boss_phase | Sine sweep 200→1000 Hz, 0.5 s, vol 0.4 | Boss phase transition |
| boss_die | Noise, lowpass 300 Hz, 1.0 s, vol 0.7; + sub-bass 60 Hz 0.8 s | Boss dies |
| pickup_coin | Sine, 1000 Hz, 0.08 s, vol 0.2; + 1500 Hz 0.06 s delay | Coin collected |
| pickup_health | Sine sweep 400→800 Hz, 0.2 s, vol 0.3 | Health orb collected |
| pickup_ammo | Square, 500 Hz, 0.06 s, vol 0.2 | Ammo crate collected |
| pickup_gun | Sine sweep 300→1200 Hz, 0.4 s, vol 0.4; + chord | New gun chest opened |
| chip_collect | Triangle, 800→1600 Hz, 0.3 s, vol 0.35 | UpgradeChip collected |
| stage_clear | Major chord (C-E-G) sine stack, 1.0 s, vol 0.4 | Blast door reached |
| game_over | Minor chord (A-C-E) sawtooth, 1.5 s, vol 0.4, fade | Lives exhausted |
| reload | Click (noise 0.02 s) × 2, 0.3 s apart, vol 0.15 | Reload starts/finishes |
| gun_swap | Square, 600 Hz, 0.04 s, vol 0.15 | Gun swap completes |
| checkpoint | Sine, 700 Hz, 0.15 s, vol 0.25 | Checkpoint flag touched |
| hazard_tick | Square, 100 Hz, 0.05 s, vol 0.2 | Steam vent / piston cycles on |
| door_open | Noise sweep 100→500 Hz, 0.6 s, vol 0.4 | Blast door opens |
| victory_fanfare | Arpeggio (C-E-G-C) triangle, 3.0 s, vol 0.5 | W2S5 cleared |
| music_w1 | Loop: bass square 80 Hz + pad sawtooth 220 Hz + hi-hat noise, 8-bar, 120 BPM | W1 stages |
| music_w2 | Loop: bass triangle 70 Hz + pad sine 330 Hz + arp, 8-bar, 110 BPM | W2 stages |
| music_title | Slow pad sine 180 Hz + sparse notes, 16-bar loop | Title / World Map |

---

# 7. UX

## Screens (state machine)

```
TITLE ──Enter/tap──→ WORLD_MAP ──select stage──→ STAGE_INTRO (1.5 s) ──auto──→ PLAYING
PLAYING ──reach blast door──→ STAGE_CLEAR ──Enter──→ WORLD_MAP (next stage highlighted)
PLAYING ──lives==0──→ GAME_OVER ──Enter──→ PLAYING (same stage, lives=3)
PLAYING ──clear W2S5──→ VICTORY (30 s credits) ──auto/Enter──→ TITLE
PLAYING / WORLD_MAP ──P/Escape──→ PAUSED ──Enter──→ PLAYING
PAUSED ──R──→ PLAYING (restart stage)
PAUSED ──Q/Escape──→ WORLD_MAP
```

## Key/button mappings on screens

| Screen | Enter/Space | ←→/AD | Escape/P | Tap |
|---|---|---|---|---|
| Title | → WORLD_MAP | — | — | → WORLD_MAP |
| World Map | Select stage | Move cursor | → Title | Select |
| Gameplay | (unused) | Move | → Pause | Fire |
| Pause | Resume | — | → World Map | Resume |
| Stage Clear | → World Map | — | — | Continue |
| Game Over | Restart stage | — | → World Map | Restart |
| Victory | Skip credits | — | — | Skip |

## HUD table (visible during PLAYING only)

| HUD element | Record field | When visible |
|---|---|---|
| HP bar (top-left, segmented 100 units) | `player.hp` | Always |
| Life icons (3 skulls) | `player.lives` | Always |
| Score counter (top-center) | `ctx.score` | Always |
| Active gun name + icon (top-right) | `player.gunIndex` | Always |
| Magazine counter "8/12" | `player.magRemaining` / gun `magSize` | Always; flashes red ≤2 |
| Reload arc (circular under mag) | `player.reloadTimer / gun.reloadTime` | During reload only |
| Charge meter (bar below player) | `player.chargeMeter` | Coil Rifle charging only |
| Stage timer (bottom-left) | `ctx.time` | Always |
| Boss HP bar (top-center, replaces timer) | `boss.phaseHp / boss.phaseMaxHp` | Boss stage, boss alive |
| Checkpoint flag icon | `ctx.checkpointReached` | Fades in after touching |
| World/Stage label | `ctx.world`, `ctx.stage` | Always, small text |

---

# 8. DEBUG API

`game.init()` installs `window.__game`. All methods synchronous, return plain data.

| Call | Does | Returns |
|---|---|---|
| `start()` | state='PLAYING', loadStage(1,1) | undefined |
| `step(dt, n)` | Run n ticks of length dt, render once. Cancels rAF. | undefined |
| `setTime(t)` | Advance to absolute t seconds (no draw) | undefined |
| `seed(n)` | Reseed rng, rebuild generated content, reset time/frame | undefined |
| `getState()` | Deep-clone ctx → plain object | `{...}` |
| `setField(path, val)` | Set ctx field at dot-path | undefined |
| `moveDir(dx)` | Persistent h-input: −1/0/+1 | undefined |
| `jump()` | One jump press (edge, 1 tick) | undefined |
| `crouch(down)` | Hold/release crouch | undefined |
| `shoot(down)` | Hold/release fire | undefined |
| `reload()` | Trigger reload | undefined |
| `selectGun(i)` | Set gunIndex to i (0–3) | undefined |
| `switchGun()` | Cycle +1 | undefined |
| `pauseGame()` / `resumeGame()` | Toggle pause | undefined |
| `spawnEnemy(type, x, y)` | enemies.spawn | `{id,x,y,type,health}` or `{id:-1}` |
| `spawnBullet(gunIdx, x, y, dir)` | Insert bullet into pool | `{id,x,y,vx,vy}` |
| `spawnHazard(type, x, y, period)` | Insert hazard | `{id,x,y,type}` |
| `skipTo(world, stage)` | loadStage | undefined |
| `setHealth(v)` | player.hp = v | undefined |
| `setAmmo(gunIdx, v)` | gun.ammo = v | undefined |
| `setPos(x, y)` | Teleport player | undefined |
| `setBossPhase(phase)` | Jump boss to phase N | undefined |
| `triggerBossAttack(pattern)` | Force boss attack | undefined |
| `setCheckpoint(x)` | Move checkpoint flag | undefined |
| `collectChip(index)` | Simulate chip pickup | undefined |
| `unlockGun(index)` | Set gun unlocked | undefined |
| `getFPS()` | Measured FPS last 60 frames (0 if stepping) | number |
| `getDrawCalls()` | Draw-call count last frame | number |
| `getParticleCount()` | Active particles | number |
| `resume()` | Restart rAF loop (after step/setTime) | undefined |

**Determinism contract:** Same `seed(n)` + same input sequence → `getState()` byte-identical. PRNG sole source of nondeterminism.

---

# 9. TESTS

All checks via `window.__game` only. Each: call sequence → assert on `getState()`.

### Boot & state machine

1. **Title draws.** `init()`; `getState().state === 'TITLE'`. After `step(1/60,1)`, `getDrawCalls() > 0`.

2. **Start enters play.** `start()`. `state==='PLAYING'`, `world===1`, `stage===1`, `player.alive===true`, `player.hp===100`, `lives===3`.

### Movement & physics

3. **Walk right.** `seed(42)`, `start()`, `moveDir(1)`, `step(1/60,60)`. Assert `player.x > 120 + 280*0.5`, `player.grounded===true`, `player.anim==='run'`.

4. **Walk left.** `moveDir(-1)`, `step(1/60,30)`. Assert `player.x` decreased.

5. **Stop.** `moveDir(0)`, `step(1/60,60)`. Assert `Math.abs(player.vx) < 1`.

6. **Jump.** `moveDir(0)`, `jump()`, `step(1/60,1)`. Assert `player.vy < 0`, `player.grounded===false`. After `step(1/60,40)`, `player.grounded===true`.

7. **Crouch.** `crouch(true)`, `step(1/60,1)`. Assert `player.crouching===true`, `player.h===28`. `crouch(false)`, `step(1/60,1)`. Assert `player.crouching===false`, `player.h===48`.

8. **Gravity / fall.** `setPos(120, 100)`, `step(1/60,30)`. Assert `player.y > 100`, `player.vy > 0`.

### Weapons

9. **Pistol fire.** `seed(42)`, `start()`, `shoot(true)`, `step(1/60,1)`. Assert `weapons.bullets.length >= 1`, `player.magRemaining === 11`. `shoot(false)`.

10. **Switch gun.** `switchGun()`, `step(1/60,1)`. Assert `player.gunIndex===1`. `switchGun()`×3 → `player.gunIndex===0`.

11. **Shotgun pellets.** `selectGun(1)`, `shoot(true)`, `step(1/60,1)`. Assert bullets spawned this shot = 5. `shoot(false)`.

12. **Coil Rifle pierce.** `selectGun(2)`, `setField('weapons.guns[2].unlocked',true)`. `spawnEnemy('crawler', player.x+100, player.y)`, `spawnEnemy('crawler', player.x+150, player.y)`. `shoot(true)`, `step(1/60,5)`. Assert both enemies damaged (pierce=3). `shoot(false)`.

13. **Flare AoE.** `selectGun(3)`, `setField('weapons.guns[3].unlocked',true)`. Spawn 3 enemies within 90 px of (player.x+200, player.y). Fire, `step(1/60,30)`. Assert all 3 enemies hp ≤ 0.

### Enemies & combat

14. **Enemy spawn.** `seed(7)`, `start()`. `spawnEnemy('crawler', 500, 640)`. Assert pool entry `type==='crawler'`, `x===500`, `hp===30`.

15. **Player takes damage.** `setPos(500, 608)` (adjacent to crawler at 500,640). `step(1/60,1)`. Assert `player.hp === 85` (100−15), `player.invulnTimer > 0`.

16. **Invulnerability.** `step(1/60,1)` again. Assert `player.hp` unchanged.

17. **Death & respawn.** `setHealth(0)`, `step(1/60,1)`. Assert `player.alive===false`, `lives===2`. After `step(1/60,60)`, `player.alive===true`, `player.hp===100`, `player.invulnTimer > 0`.

### Level & progression

18. **Tile collision.** `setPos(120, 608)`, `step(1/60,1)`. Assert `player.grounded===true`, `player.y === 22*32 - 48` (feet on floor row).

19. **Stage clear.** `setPos(4681, 608)`, `step(1/60,1)`. Assert `state==='STAGE_CLEAR'`. After `step(1/60,90)`, `stage===2`, `state==='PLAYING'`.

20. **World progression.** `skipTo(1,5)`, clear (setPos to flagX, step). Assert `world===2`, `stage===1`.

21. **Game over.** `setField('lives',0)`, `setHealth(0)`, `step(1/60,1)`. Assert `state==='GAME_OVER'`.

### Camera

22. **Follow & clamp.** `moveDir(1)`, `step(1/60,120)`. Assert `camera.x > 0`, `camera.x <= 4800-960`.

### Audio

23. **SFX queue.** `shoot(true)`, `step(1/60,1)`. Assert `audio.sfxQueue.length > 0`. `shoot(false)`.

### Boss

24. **Boss phase transition.** `skipTo(1,5)`, `setBossPhase(0)`, `setField('boss.phaseHp', 1)`. Deal damage to push below transitionAt. Assert `boss.phase===1`, `boss.invulnFlash > 0`.

25. **Boss death → stage clear.** `setField('boss.alive',false)`, `step(1/60,1)`. Assert `state==='STAGE_CLEAR'`.

### Scoring

26. **Kill score.** `spawnEnemy('crawler', 500, 640)`, kill it (shoot or setField hp=0 + step). Assert `score >= 100`.

### Touch / Input

27. **Synthetic input.** `inject('jump',true)`, `step(1/60,1)`. Assert `player.vy < 0`. `inject('jump',false)`.

### Determinism

28. **Reproducibility.**
```
seed(1234); start(); moveDir(1); jump(); shoot(true);
step(1/60,300); const a = JSON.stringify(getState());
seed(1234); start(); moveDir(1); jump(); shoot(true);
step(1/60,300); const b = JSON.stringify(getState());
```
Assert `a === b`.

### Budgets

29. **Draw calls.** After `step(1/60,1)`, `getDrawCalls() <= 200`.

30. **Entity cap.** `spawnEnemy('crawler',100,100)` × 65. Assert 65th returns `{id:-1}`. Assert `enemies.pool.length === 64`.

31. **Bullet cap.** `shoot(true)`, `step(1/60,200)`. Assert `weapons.bullets.length <= 128`.

32. **Particle cap.** Trigger 300 explosion particles. Assert `getParticleCount() <= 256`.

## SCREENSHOTS

| Screen / State | How to Reach | What Must Be Visible |
|---|---|---|
| Title | Launch | "FORGE BREAKER" logo amber/cyan gradient, animated gear+crystal bg, "PRESS START" pulsing, parallax factory |
| World map | After title | 2 rows × 5 circles. W1 amber, W2 cyan. Completed=filled+check, next=pulse, locked=grey. Stage numbers. |
| Stage 1-1 start | Select W1S1 | Camera pans to player X=120. Zone 1: crates, forklift, warm amber floor glow. Player idle-bob. HUD visible. |
| Mid-run shooting | W1S2 zone 2 | Player mid-run, gun aimed right, muzzle flash amber, conveyor scrolling, rivet drone ahead, 2 platforms, parallax gears. |
| Crouch under pipe | W1S3 | Player 60% height under horizontal pipe, gun angled down, visor glow, amber floor. |
| Jump over slag pit | W1S2 | Player airborne legs tucked, slag pit orange glow+heat shimmer, platform ahead, bullet trail. |
| New weapon pickup | W1S3 zone 4 | Spinning Coil Rifle icon above crate, screen flash cyan, "COIL RIFLE" text sliding in. |
| Coil Rifle firing | Any stage post-W1S4 | 200u cyan beam, player arms extended, charge glow, enemy hit sparks. |
| Flare in use | W2S2+ | Green droplet arc toward Cryo Stalker, nozzle #7FFF00, sizzle particles. |
| Drone death | Kill rivet drone | Hexagon spin+shrink, explosion amber, 6 sparks, 2 coins arc up, "+150" text. |
| Boss fight (Furnace Colossus) | W1S5 | 160×200 boss center-right, orange core pulse, smokestack, player small firing, ground cracked, boss HP bar top. |
| Boss death | Defeat Colossus | Multi-explosion white/orange, shake 10px, white flash, slow-mo, 12 coins, "STAGE CLEAR" stamp. |
| Stage complete | Any stage end | "STAGE CLEAR" text, gold particle rain, score tally, opened blast door glow, player at exit. |
| Game over | Lose all lives | Desaturated, red vignette, "SYSTEM FAILURE" #FF4500, player dissolve, HUD greyed. |
| W2 contrast | Start W2S1 | Cool shift: cyan floor, frost tiles, blue-white pools, Cryo Stalker visible, condensation pipes. |
| Low health | hp < 30 | Health bar pulsing red, vignette tightened, heartbeat pulse, player white-flash, red edges. |
| Pause | P mid-stage | Dark overlay, "PAUSED" center, resume/quit, game frozen, heavier vignette. |
| W2S5 Absolute Zero | Reach final stage | Tall crystalline boss, 4 orbiting shards cyan, frost overlay edges, player crouched firing, shards mid-flight, cold ambient. |

---

# 10. BUILD ORDER

| # | Milestone | Modules | Proof check |
|---|---|---|---|
| M1 | Page opens, draws title, `start()` → PLAYING with blank ground + static player rect. | game, input, renderer(stub), ui(title) | **Checks 1, 2** |
| M2 | Player walks/jumps/crouches on hand-authored tile row. Camera follows. | player, level(static), camera | **Checks 3–8, 18, 22** |
| M3 | Pistol fires; one enemy (Crawler) walks and damages. Health, lives, death, respawn. | weapons(pistol), enemies, progression(lives/death) | **Checks 9, 14–17** |
| M4 | All 4 guns (shotgun, coil, flare). Ammo, fire-rate, switching, pierce, AoE, charge. | weapons(full) | **Checks 10–13** |
| M5 | Stage generation: 2×5 stages, tilemap, spawn points, blast door, hazards, platforms. Stage-clear → next → next world. | level(generate), progression(full) | **Checks 19–21** |