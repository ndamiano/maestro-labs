# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Side-scrolling platformer | §1 Conventions (camera, axes), §4 Locomotion, §3 Visual Spec |
| Shooter with at least 4 different gun types | §4 Shooting system, Gun table in §4 Records |
| Character can jump | §4 Locomotion – Jump rule |
| Character can move left or right | §4 Locomotion – Move rule |
| Character can crouch | §4 Locomotion – Crouch rule |
| Story progression modelled on worlds and stages (Mario-like) | §4 ProgressionAndUnlocks, WorldMap record |
| 2 worlds | §4 ProgressionAndUnlocks, Stage records W1S1–W1S5, W2S1–W2S5 |
| 5 stages per world | §4 StageGenerator, Progression order |
| Do not simply copy Mario | Industrial/salvage theme, 4-gun loadout, crouch mechanic, charge/arc weapons, boss multi-phase |
| *(added)* Touch controls for mobile | §4 TouchControls |
| *(added)* Upgrade chips for replay value | §4 ProgressionAndUnlocks, UpgradeChip record |
| *(added)* Score ranks (Bronze/Silver/Gold) | §4 Scoring |
| *(added)* Screen-shake, post-effects, parallax | §3 Visual Spec, §5 Characters |

## 0.2 Decisions

| Topic | Gameplay said | Visual said | Engineering said | Ruling & why |
|---|---|---|---|---|
| Stage height | 720 px default | 1200 units | ≤40 tiles × 32 = 1280 px max | **720 px.** All physics numbers (jump peak 84 px, gravity 1600) are tuned to 720; visual's 1200 would make platforming feel empty. |
| Stage width (normal) | 4800 px | 4800 units | ≤400 tiles × 32 = 12800 px max | **4800 px.** Both agree. |
| Stage width (boss) | 1200 px | 2400 × 1200 | — | **2400 px × 720 px.** Boss sweep patterns need room; visual's 2400 width is justified, height stays 720. |
| Player hitbox (standing) | 48 px tall | 36 × 56 | placeholder `<player height>` | **36 w × 48 h px.** Gameplay's 48 governs physics (crouch 48→28); visual's 56 is the drawn sprite height including headroom. |
| Player hitbox (crouch) | 28 px tall | 36 × 36 | placeholder `<crouch height>` | **36 w × 28 h px.** Gameplay's number is the collision rule. |
| Player run speed | 280 px/s | — | placeholder `<player speed>` | **280 px/s.** |
| Jump initial vy | −520 px/s | — | — | **−520 px/s.** |
| Gravity | 1600 px/s² | — | placeholder | **1600 px/s².** |
| Camera X lerp | 0.12/frame | 8%/frame | — | **0.08/frame X, 0.12/frame Y.** Visual's split is more nuanced for a side-scroller. |
| Camera deadzone | 80 px H, 60 px V | 80 units V deadzone | — | **80 px H, 60 px V.** Gameplay's numbers. |
| Player offset in viewport | — | ~35% from left | — | **35% from left edge.** Visual's number, no conflict. |
| Gun names | Scrap Pistol, Rivet Shotgun, Coil Rifle, Flare Launcher | Pulse Pistol, Scatter Cannon, Rail Driver, Acid Sprayer, Plasma Lance (5) | pistol, shotgun, laser, rocket | **Gameplay's 4 names.** Visual's 5th (Plasma Lance) dropped; request says 4. Visual recipes mapped: Pulse Pistol→Scrap Pistol, Scatter Cannon→Rivet Shotgun, Rail Driver→Coil Rifle, Acid Sprayer→Flare Launcher. |
| Boss names | Rust Colossus (W1), Core Warden (W2) | Furnace Colossus, Absolute Zero | — | **Gameplay's names.** They appear in progression logic. |
| Enemy type names | crawler, turret, drone, shieldTrooper, boss | Rivet Drone, Smelter Bot, Cryo Stalker | 'grunt' | **Gameplay's enum.** Visual's names are cosmetic labels per world theme: W1 Smelter Bot = crawler, W2 Cryo Stalker = crawler variant. Engineering's 'grunt' renamed to 'crawler'. |
| Stage generation | Seeded procedural + verifier | Hand-authored, 10 stages, "no procedural" | level.generate() | **Seeded procedural with verifier.** More testable, more replayable, and the request implies a generator ("modelled off Mario" = structured, not random). Visual's 5-zone structure is incorporated as themed regions within the generated layout. |
| Tile collision grid | — | Ground plate 80×40 | 32×32 grid | **32×32 collision grid.** Visual recipes are draw appearances; a ground plate visual spans 3×1 collision cells. |
| Conveyor physics speed | ±120 px/s added to player | Stripe-scroll 60u/s | — | **120 px/s player push; 60 px/s texture scroll.** Different things. |
| Lives per stage | 3 | — | placeholder `<start lives>` | **3.** |
| HP max | 100 | — | placeholder `<player max hp>` | **100.** |
| Fire key binding | J / left-click / touch | — | J / Enter / Z | **J / Enter / Z / left-click / touch-fire.** Union of all three. |
| Gun swap binding | 1/2/3/4, scroll-wheel | — | K / Shift | **1/2/3/4 direct, K/Shift/scroll cycles.** Both work. |
| Reload binding | R | — | not mentioned | **R.** Gameplay's addition. |
| Pause binding | P / Escape | — | not mentioned | **P / Escape.** |
| Crouch binding | S / ↓ | — | S / ↓ | **S / ↓.** Agreement. |
| Extraction point visual | Flagpole | Blast door / teleport pad | flagX trigger | **Blast door at x = width − 120.** Visual's look, gameplay's position. |
| Coins / currency | Not in scoring | 20–40/stage, "+1" text | — | **Added as T2 polish.** Not in core loop; deferred. |
| Stomp mechanic | Not present | Feedback table mentions it | — | **T2 polish.** Adds Mario-adjacency the request warns against; deferred. |
| Boss arena height | 720 (implied) | 1200 | — | **720 px.** Consistent with all stages. |
| World 1 theme | Industrial pipes/catwalks | Smelting Yards (amber/red) | — | **Smelting Yards.** Visual's name is more evocative; theme is identical. |
| World 2 theme | Cave/underground | Cooling Towers (cyan/blue) | — | **Cooling Towers.** Visual's name; theme matches gameplay's underground. |
| Touch layout | D-pad left, fire right, gun-swap BR, reload BL | — | Left half move, right half fire, BR buttons | **Gameplay's layout.** More specific. |
| Audio | Not specified | Not specified | Web Audio, oscillator+noise | **Web Audio generated SFX.** §6. |
| Parallax layers | Not specified | 3 layers (5%, 20%, 60%) | parallax array in level | **Visual's 3 layers.** |
| Post-effects | Not specified | Vignette, shake, chromatic aberration, grain, etc. | Not specified | **Visual's post-effects, T2 tier.** |
| Upgrade chips | 4 per world, hidden side-rooms | Not mentioned | Not mentioned | **Gameplay's spec.** T2 tier. |

## 0.3 Tiers

**T1 (must ship):** Locomotion, Shooting, DamageAndDeath, EnemyAI, BossAI, StageGenerator, ProgressionAndUnlocks, Scoring, Camera, HUD, Title/StageSelect/GamePause/StageComplete/GameOver/Victory screens, 4 guns, 2 worlds × 5 stages, 2 bosses, keyboard controls, Web Audio SFX (fire, jump, hit, death, explosion), parallax background, tile culling, fixed-step loop, seeded RNG.

**T2 (polish, independent, add in this order):**
1. Touch controls (virtual dpad + buttons)
2. Upgrade chips (4 per world, hidden side-rooms)
3. Screen-shake and post-effects (vignette, chromatic aberration, grain, heat distortion, frost bloom)
4. Coins / score pickups (20–40 per stage, +10 score each)
5. Stomp mechanic (land on enemy, bounce, enemy squishes)
6. Conveyor belt and breakable tile mechanics
7. Slope45 tiles
8. Stage replay with rank display (Bronze/Silver/Gold)
9. Pause menu full options (Restart Stage, Quit to Map)
10. Victory credits roll (30 s)

**T3 (stretch):**
1. Per-world background music loops
2. Achievements / stats screen
3. Speedrun timer mode
4. Accessibility: remappable keys, larger hitbox option

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Item | Rule |
|---|---|
| Unit | 1 unit = 1 logical pixel. Canvas backing store = physical pixels; logical viewport = **960 × 540** units. CSS transform scales to browser window. |
| Axes | X increases **rightward**. Y increases **downward** (canvas-native). "Up" in gameplay = **−Y**. Gravity is positive Y acceleration. |
| Origin | Top-left of logical viewport (0, 0). World origin also (0, 0); camera offset translates world→viewport. |
| Tile grid | **32 × 32**-unit tiles. `(tx, ty)` → world `(tx*32, ty*32)`. |
| Ground rule | Lowest solid tile row is floor. Player feet at `floorTileRow * 32`. Fall below `y > stageHeight + 64` → death. |
| Stage height | **720 px** (23 tile rows; ground at row 21, y = 672). |
| Stage width | **4800 px** normal; **2400 px** boss arenas. |
| Fixed timestep | `DT = 1/60` s. Accumulator loop; clamp to 5 DTs max per frame to avoid spiral-of-death. |
| Render | Once per rAF frame, after all ticks. |

## 1.2 Important conventions

**Tick system order (strict):**

| Order | System | Why |
|---|---|---|
| 1 | `input.update()` | Latch key states, build frame snapshot. |
| 2 | `progression.update()` | Stage transitions / death → reload before physics. |
| 3 | `level.update()` | Animate tiles, move platforms, tick hazards. |
| 4 | `player.update()` | Input → velocity → position → collision. |
| 5 | `weapons.update()` | Fire, advance bullet pool. |
| 6 | `enemies.update()` | AI, movement, collisions. |
| 7 | `camera.update()` | Follow, clamp, decay shake. |
| 8 | `audio.update()` | Flush SFX queue. |
| 9 | `renderer.draw()` | **After all ticks**, outside while-loop. |

**Random source:** One seeded PRNG, `rng`, implemented as 32-bit xorshift. Methods: `rng.next()` → float [0,1), `rng.nextInt(n)` → int [0,n). **No `Math.random()` anywhere.** Reseeded only via `seed(n)` in debug API or at stage start.

**Controls table:**

| Input | Action | Binding |
|---|---|---|
| Move left | ← | `KeyA`, `ArrowLeft` |
| Move right | → | `KeyD`, `ArrowRight` |
| Jump | ↑ | `KeyW`, `ArrowUp`, `Space` |
| Crouch (hold) | ↓ | `KeyS`, `ArrowDown` |
| Fire (hold) | J | `KeyJ`, `Enter`, `KeyZ`, left-click |
| Reload | R | `KeyR` |
| Gun swap (direct) | 1/2/3/4 | `Digit1`–`Digit4` |
| Gun swap (cycle) | K / Shift / scroll | `KeyK`, `ShiftLeft`, wheel |
| Pause | P / Esc | `KeyP`, `Escape` |
| Touch: left half | D-pad (move, crouch) | Pointer events |
| Touch: right half | Fire (hold = auto/charge) | Pointer events |
| Touch: bottom-right circle | Gun swap | Pointer events |
| Touch: bottom-left circle | Reload | Pointer events |

Touch inputs map to the same rule IDs as keyboard; no separate tuning.

---

# 2. CONTRACTS

## 2.1 Module layout

| Module | Responsibility |
|---|---|
| `game` | State machine (TITLE → PLAYING → PAUSED → STAGE_CLEAR → GAME_OVER → VICTORY). Owns main loop and `ctx`. |
| `input` | Keyboard/pointer events, key-state snapshot, `isDown(action)`. |
| `progression` | World/stage index, lives, score, checkpoint, stage-clear, death→respawn/game-over, unlock tracking. |
| `level` | Tilemap data, solid/hazard/platform tiles, parallax layers, stage geometry, generator + verifier. |
| `player` | Player entity: position, velocity, state, health, animation. |
| `weapons` | 4 guns, ammo, fire-rate, charge, reload, bullet pool, bullet physics/collision. |
| `enemies` | Enemy pool, per-type AI, damage, death, drops. |
| `boss` | Boss phase sequences, pattern execution, phase transitions. |
| `camera` | Viewport offset, follow lerp, deadzone, screen-shake accumulator. |
| `audio` | Web Audio graph, generated SFX, music scheduling. |
| `renderer` | Canvas 2D draw calls: clear, parallax, tiles, entities, bullets, particles, HUD, overlays, post-effects. |
| `ui` | HUD elements, title screen, pause overlay, stage-complete, game-over, world map, victory. |

## 2.2 Global context

```js
const ctx = {
  // --- timing ---
  time: 0,
  frame: 0,
  dt: 1/60,

  // --- rng ---
  rng: null,  // { next(), nextInt(n), seed(n) }

  // --- game state ---
  state: 'TITLE',  // 'TITLE'|'PLAYING'|'PAUSED'|'STAGE_CLEAR'|'GAME_OVER'|'VICTORY'
  paused: false,

  // --- progression ---
  world: 1,
  stage: 1,
  lives: 3,
  score: 0,
  stageClearTimer: 0,
  unlockedStages: new Set(['W1S1']),
  unlockedGuns: new Set(['scrapPistol']),
  upgradeChips: [],           // collected UpgradeChip records this run
  checkpointReached: false,
  checkpointX: 0,
  stageStartTime: 0,

  // --- level ---
  level: {
    tiles: null,              // Uint8Array, width*height
    tileW: 32,
    tileH: 32,
    width: 0,                 // tiles across
    height: 23,               // tiles down (720/32 ≈ 22.5 → 23)
    stageWidth: 4800,         // px
    stageHeight: 720,         // px
    spawnX: 120,
    spawnY: 672,              // ground row * 32
    flagX: 4680,              // width - 120
    platforms: [],            // [{x,y,w,h,vx,vy}]
    hazards: [],              // [{x,y,w,h,type,damage,period,activeTime}]
    chests: [],               // [{x,y,type:'gun'|'chip',gunId?,chipId?}]
    parallax: [],             // [{layer,scrollFactor}]
    extractionType: 'blastdoor' // 'blastdoor'|'teleportpad'
  },

  // --- player ---
  player: {
    x: 120,
    y: 624,                   // spawnY - height (672 - 48)
    vx: 0,
    vy: 0,
    w: 36,
    h: 48,
    crouchH: 28,
    facing: 1,                // +1 right, -1 left
    grounded: false,
    crouching: false,
    jumping: false,
    health: 100,
    maxHealth: 100,
    invulnTimer: 0,           // seconds remaining
    hitTimer: 0,              // alias for invulnTimer (gameplay name)
    anim: 'idle',             // 'idle'|'run'|'jump'|'fall'|'crouch'|'hurt'|'death'
    animFrame: 0,
    animTimer: 0,
    gunIndex: 0,              // 0..3
    alive: true,
    chargeMeter: 0,           // 0..1, coil rifle only
    swapTimer: 0,             // seconds remaining in gun-swap lockout
    reloadTimer: 0,           // seconds remaining in reload
    speed: 0,                 // current |vx| for HUD/debug
  },

  // --- weapons ---
  weapons: {
    guns: [
      { name:'scrapPistol',  dmg:12,  rate:6.0,  ammo:12, maxAmmo:12, bulletSpeed:600, spread:2,  pellets:1, knockback:80,  pierce:0, aoe:0,  chargeMax:0,   unlocked:true },
      { name:'rivetShotgun', dmg:9,   rate:1.4,  ammo:6,  maxAmmo:6,  bulletSpeed:450, spread:18, pellets:5, knockback:220, pierce:0, aoe:0,  chargeMax:0,   unlocked:false },
      { name:'coilRifle',    dmg:15,  rate:2.5,  ammo:5,  maxAmmo:5,  bulletSpeed:900, spread:0,  pellets:1, knockback:140, pierce:3, aoe:0,  chargeMax:1.2, unlocked:false },
      { name:'flareLauncher',dmg:55,  rate:0.8,  ammo:4,  maxAmmo:4,  bulletSpeed:320, spread:4,  pellets:1, knockback:300, pierce:0, aoe:90, chargeMax:0,   unlocked:false },
    ],
    fireTimer: 0,
    bullets: [],              // pool, cap 128
    charging: false,
    chargeTime: 0,
  },

  // --- enemies ---
  enemies: {
    pool: [],                 // cap 64
    spawnQueue: [],           // [{x,y,type}] generated at level load
  },

  // --- boss ---
  boss: {
    active: false,
    type: null,               // 'rustColossus'|'coreWarden'
    phase: 0,
    phases: [],               // [{hp,maxHp,pattern,interval,transitionAt}]
    x: 0, y: 0, w: 0, h: 0,
    vx: 0, vy: 0,
    hp: 0, maxHp: 0,
    invulnTimer: 0,
    attackTimer: 0,
    state: 'idle',            // 'idle'|'attack'|'telegraph'|'transition'|'dead'
  },

  // --- camera ---
  camera: {
    x: 0,
    y: 0,
    shakeX: 0, shakeY: 0,
    shakeTimer: 0,
    shakeIntensity: 0,
  },

  // --- input snapshot ---
  input: {
    left: false, right: false, jump: false, crouch: false,
    shoot: false, reload: false,
    gunDirect: -1,            // 0-3 if digit pressed, -1 otherwise
    switchGun: false,
    switchGunPressed: false,
    jumpPressed: false,
    jumpReleaseTime: -1,      // for variable jump
  },

  // --- audio ---
  audio: {
    ctx: null,
    masterGain: null,
    sfxQueue: [],
    musicPlaying: false,
    musicNodes: [],
  },

  // --- render ---
  canvas: null,
  c2d: null,
  drawCallCount: 0,
};
```

## 2.3 Module specifics

### `game`
```
init(canvasEl, opts) → void
start() → void
tick() → void
render() → void
pause() / resume() → void
```

### `input`
```
attach(canvasEl) → void
snapshot() → void
isDown(action: string) → bool
inject(action: string, down: bool) → void
```

### `progression`
```
loadStage(world: int, stage: int) → void
checkStageClear() → void
checkDeath() → void
nextStage() → void
advanceWorld() → void
unlockGun(gunName: string) → void
collectChip(chipId: int) → void
applyRank(stageId: string, score: int) → 'gold'|'silver'|'bronze'|null
```

### `level`
```
generate(world: int, stage: int) → void
getTile(tx, ty) → int
isSolid(tx, ty) → bool
resolveAABB(entity) → {grounded, hitX, hitY}
update() → void
verify() → bool   // runs all generator checks; returns true if valid
```

### `player`
```
update() → void
hurt(amount: int, sourceX: float, sourceY: float) → void
respawn() → void
die() → void
```

### `weapons`
```
update() → void
fire() → void
switchGun(index: int) → void
cycleGun() → void
reload() → void
beginCharge() → void
releaseCharge() → void
```

### `enemies`
```
update() → void
spawn(type: string, x: float, y: float) → int
damage(id: int, amount: int, knockbackVx: float) → bool
```

### `boss`
```
init(type: string, arenaX: float, arenaW: float) → void
update() → void
damage(amount: int) → void
advancePhase() → void
```

### `camera`
```
update() → void
addShake(intensity: float, duration: float) → void
```

### `audio`
```
init() → void
playSFX(type: string) → void
stopMusic() / startMusic(track: string) → void
update() → void
```

### `renderer`
```
draw() → void
```

### `ui`
```
drawHUD(c2d) → void
drawTitle(c2d) → void
drawPause(c2d) → void
drawStageClear(c2d) → void
drawGameOver(c2d) → void
drawWorldMap(c2d) → void
drawVictory(c2d) → void
```

---

# 3. VISUAL SPEC

**The look in one paragraph:** A vast abandoned mega-factory rendered in thick, confident vector shapes with a warm-to-cool duotone palette: deep charcoal (#1A1A2E) foundations, hot molten amber (#FF8C00) and electric cyan (#00F5FF) accent lighting, and bruised violet (#4A1A6B) midtones. Everything reads as heavy industrial machinery — riveted plate, dripping coolant, spinning gears, hissing valves — but stylised into clean geometric silhouettes with 3-px dark outlines. World 1 (Smelting Yards) skews amber/red/charcoal; World 2 (Cooling Towers) skews cyan/white/deep-blue. The hero shot: player mid-air over a conveyor belt of glowing ore, muzzle-flash painting the scene amber, drones exploding into sparks, three parallax layers of factory architecture fading into violet haze.

**Lighting and atmosphere:** No global light source. Ambient tint overlay per world: W1 = #FF8C00 at 8% opacity multiply; W2 = #00F5FF at 6% opacity multiply. Point-light sources drawn as radial-gradient circles, additive blend: furnace glow (#FF4500→transparent, 200u radius, pulse ±20u 2s), coolant lamp (#00F5FF→transparent, 160u, flicker 5% 8Hz), muzzle flash (weapon colour→transparent, 40u, 0.08–0.15s), enemy eye glow (#FF4500 or #00F5FF, 20u, pulse ±4u 1.5s), exit door glow (#FFD700, 120u, pulse ±15u 2s), pickup glow (item colour, 30u, static). Zones 2 and 4 of each stage have a "shadow corridor" (300u wide band, 60% #0D0D1A overlay, broken by point-lights) — purely visual, no gameplay stealth. Far parallax at 70% opacity, mid at 85%. Horizontal gradient fade (80u each edge) softens viewport. Vignette always on (radial, edges 35% darker, #0D0D1A). Grain always on (3% opacity noise, 12fps).

**The space:** Each stage is a horizontal strip, 4800 × 720 px (boss: 2400 × 720). Camera viewport 960 × 540. Player starts X=120, Y=672 (ground). Exit blast door at X = width − 120. Five thematic zones per stage (~960 px each): Entry (loading dock / airlock), Gauntlet (conveyors / cryo-tunnels), Combat (smelter floor / coolant reservoir), Puzzle (gear-maze / thermal-exchange), Exit (blast furnace core / central chiller). Zone boundaries marked by colour/light shift. Parallax: Far (sky + smokestack silhouettes, 5% scroll), Mid (gears, pipes, building outlines, 20%), Near (dangling cables, steam wisps, 60%).

**Recipe table:**

| Name | Shape / Construction | Size (units) | Colours (hex) | Count / Stage | Motion / Effect |
|---|---|---|---|---|---|
| Ground plate (W1) | Rounded rect, 3px stroke #0D0D1A, fill gradient #2A2A3E→#1A1A2E, rivet dots every 60u | 80 × 40 (spans 3×1 collision cells) | #2A2A3E, #1A1A2E, #0D0D1A | ~120 | Static |
| Ground plate (W2) | Same, fill #1E3A5F→#0F1F33, frost crystal overlay | 80 × 40 | #1E3A5F, #0F1F33, #FFFFFF | ~120 | Static |
| Platform (floating) | Rounded rect, fill #3D2B5F, top-edge highlight #FF8C00(W1)/#00F5FF(W2) | 120 × 24 | #3D2B5F, accent per world | ~40 | Bob ±4u sine, 2s |
| Conveyor belt | Rect + scrolling diagonal-stripe texture (45°, 20px spacing) | 200 × 32 | #1A1A2E base, #FF8C00(W1)/#00F5FF(W2) stripes | ~8 | Stripe-scroll 60u/s |
| Piston platform | Rect + cylindrical stem below | 100×20 + 20×60 stem | #4A4A5E, #2A2A3E | ~6 | Vertical extend/retract, 1.5s cycle |
| Slag pit (W1) | Wavy-top rect, inner glow | 160 × 40 | #FF4500 core, #FF8C00 glow, #1A0A00 rim | ~4 | Heat shimmer 2px sine 0.5s |
| Ice plate (W2) | Rect + 2 crack lines, translucent | 120 × 16 | #A8E6FF 70%, #FFFFFF cracks | ~5 | Static |
| Wall / backdrop | Tall rect, riveted, 2px stroke | 80 × 300 | #1A1A2E, stroke #0D0D1A | ~30 | Static |
| Pipe (H/V) | Rounded rect 16u tall, joint circles every 100u | variable × 16 | #3D3D5E, joints #FF8C00(W1)/#00F5FF(W2) | ~25 | Static |
| Blast door (exit) | Arch-top rect, 2 halves, gear motif | 140 × 200 | #2A2A3E, gear accent, stroke #0D0D1A | 1 | Halves slide apart 0.6s ease-out |
| Crate stack | 2–3 offset rounded rects, X-brace | 50×50 each | #4A3520, #2A1F10, stroke #1A0F05 | ~12 | Destroyable |
| Gear (wall) | 8-tooth circle, inner hole | 80 dia | #3D3D5E, teeth #4A4A5E | ~10 | Rotate 30°/s |
| Valve wheel | Circle + 4 spokes | 50 dia | accent per world, rim #1A1A2E | ~8 | Glow when near |
| Steam vent | Small rect + particle emitter | 24 × 12 | #2A2A3E | ~10 | 3 white particles/s, rise 40u, fade |
| Warning sign | Triangle + "!" | 30 × 30 | #FFD700, stroke #1A1A2E | ~6 | Flash 1s when player <200u |
| Ammo crate | Small rect, weapon icon on face | 30 × 24 | #2A2A3E, icon = weapon accent | 6–10 | Float bob ±3u 1s, glow outline |
| Health cell | Cross inside circle | 24 × 24 | #FF4500 cross, #FFFFFF circle | 3–5 | Pulse scale 1.0→1.1, 1s |
| Weapon pickup | Ammo crate + spinning icon above | 30 × 36 | weapon colour | 1–2 | Icon spin 180°/s |
| Bullet (player) | Small circle or line-segment | 4–6 | weapon colour, 80% trail | per shot | Linear travel |
| Bullet (enemy) | Small circle | 6 | #FF4500, trail 40% | per shot | Linear travel |
| Explosion (small) | Expanding circle + 6–8 sparks | 40→80u | #FFD700→#FF4500→transparent | on enemy death | 0.3s expand-fade |
| Explosion (large) | Circle + 12 sparks + smoke puffs | 80→200u | #FF4500→#1A1A2E | boss hit, crate destroy | 0.5s |

**Post-effects (T2):**

| Effect | Trigger | Strength / Duration |
|---|---|---|
| Vignette | Always | Radial, 35% darker edges |
| Chromatic aberration | Player hit | 2px RGB split, 0.2s |
| Screen shake | Player hit, explosion, boss slam | 4px random, 0.3s decay |
| Screen shake (heavy) | Boss death, stage complete | 10px, 0.6s |
| Flash (white) | Pickup, boss death | Full-screen 60%, 0.12s |
| Flash (red) | Player damage | Full-screen 40%, 0.15s |
| Heat distortion (W1) | Near slag/furnace | 2px vertical sine, 0.4s |
| Frost bloom (W2) | Near ice/coolant | White crystal shapes, fade 1s |
| Grain | Always | 3% noise, 12fps |
| Slow-mo tint | Boss death final hit | Desaturate 40%, 0.8s |

---

# 4. GAMEPLAY SPEC

**The game in one paragraph:** You are Kael, a salvage mechanic fighting through two hostile industrial zones to reclaim the city's power grid. Minute to minute you run, jump, crouch under low pipes, and shoot waves of automated enemies and hazards across scrolling stages. You swap between four salvaged guns on the fly, each with a distinct rhythm—tap-fire, spread, charge-release, lobbed explosion—so combat is a constant decision about spacing, timing, and which tool the current fight demands. Stages are short (45–90 seconds of skilled play) and end with a blast-door extraction point you must reach; the final stage of each world is a multi-phase boss. You get 3 lives per stage attempt and unlimited retries; dying resets you to the checkpoint or stage start with a full heal. The game has a definitive end: clearing W2S5 triggers a victory screen. Between stages you pick your next stage from a world map; you can replay cleared stages for higher score ranks.

## Records

**RECORDS:** Player, Gun, Enemy, Projectile, Tile, Hazard, BossPhase, Stage, WorldMap, UpgradeChip

### Player
| Field | Type | Start | Notes |
|---|---|---|---|
| hp | int 0–100 | 100 | |
| lives | int 0–3 | 3 | per stage attempt |
| score | int 0+ | 0 | resets per stage attempt |
| activeGun | enum {scrapPistol, rivetShotgun, coilRifle, flareLauncher} | scrapPistol | |
| speed | float px/s | 0 | current |vx| |
| vx, vy | float px/s | 0, 0 | |
| grounded | bool | false | |
| crouching | bool | false | |
| facing | int {−1, +1} | +1 | |
| hitTimer | float s | 0 | i-frames countdown |
| chargeMeter | float 0–1 | 0 | coilRifle only |

### Gun table

| Gun | damage | fireRate | projSpeed | spreadDeg | magSize | reloadTime | knockback | pierce | aoeRadius | chargeMax | unlock |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Scrap Pistol | 12 | 6.0 | 600 | 2 | 12 | 1.4 | 80 | 0 | 0 | 0 | start |
| Rivet Shotgun | 9×5 pellets | 1.4 | 450 | 18 | 6 | 2.2 | 220 | 0 | 0 | 0 | W1S2 chest |
| Coil Rifle | 40 charged / 15 tap | 2.5 | 900 | 0 | 5 | 2.8 | 140 | 3 | 0 | 1.2 | W1S4 chest |
| Flare Launcher | 55 | 0.8 | 320 (arc) | 4 | 4 | 3.5 | 300 | 0 | 90 | 0 | W2S2 chest |

### Enemy table

| Enemy | hp | damage | speed | patrolRange | aggroRange | knockbackResist |
|---|---|---|---|---|---|---|
| Crawler | 30 | 15 | 120 | 80 | 200 | 0.0 |
| Turret | 50 | 10 (proj) | 0 | 0 | 350 | 1.0 |
| Drone | 20 | 12 | 160 | 120 | 280 | 0.2 |
| ShieldTrooper | 80 (+60 shield) | 20 | 70 | 60 | 240 | 0.6 |
| Boss | see BossPhase | — | — | — | — | 1.0 |

### Projectile
| Field | Type | Default |
|---|---|---|
| owner | {player, enemy} | |
| vx, vy | float px/s | |
| damage | int | |
| pierceLeft | int | 0 |
| aoeRadius | float px | 0 |
| lifetime | float s | 3.0 |

### Tile
| Field | Type | Notes |
|---|---|---|
| type | enum {solid, platform, slope45, spike, conveyor, breakable} | |
| solidity | bool | true for solid, platform, slope45, conveyor |
| hp | int | breakable only, 1–3 |
| conveyorSpeed | float px/s | conveyor only, ±120 |

### Hazard
| Field | Type | Notes |
|---|---|---|
| type | enum {spike, steamVent, crushingPiston, electricFloor} | |
| damage | int | spike 20, steam 12, piston 30, electric 18 |
| period | float s | 0 = always-on |
| activeTime | float s | portion of period that hurts |

### BossPhase
| Field | Type | Notes |
|---|---|---|
| hp | int | HP in this phase |
| pattern | enum {sweep, volley, charge, summon, laser, electrify} | |
| interval | float s | between attacks |
| transitionAt | float | fraction of phase HP remaining → next phase |

### Stage
| Field | Type | Notes |
|---|---|---|
| id | string | "W1S1"…"W2S5" |
| width | float px | 4800 normal, 2400 boss |
| height | float px | 720 |
| seed | int | generator seed |
| goldThreshold | int | |
| silverThreshold | int | |
| bronzeThreshold | int | |
| parTime | float s | width / 200 |

### UpgradeChip
| Field | Type | Notes |
|---|---|---|
| targetGun | enum gun name | |
| statBoost | enum {damage+4, fireRate+1, magSize+2, reloadTime−0.4} | |
| permanent | bool | true |

## Systems

### Locomotion [T1]

- **Move left/right:** While left held, accelerate `Player.vx` toward −280 px/s at 2400 px/s². While right held, toward +280 px/s. No key held: decelerate at 1800 px/s² (friction). `Player.facing` matches last horizontal input.
- **Jump:** When jump pressed AND `Player.grounded == true`: set `Player.vy = −520 px/s`. Variable-height: releasing jump within 0.18 s of press cuts `vy` to −260 px/s (short hop).
- **Crouch:** While crouch held AND `Player.grounded == true`: `Player.crouching = true`, hitbox height 48→28 px, max speed halves to 140 px/s, jump disabled. Releasing restores.
- **Gravity:** `Player.vy += 1600 * dt` while airborne. Terminal velocity 700 px/s.
- **Conveyor tiles [T2]:** Standing on conveyor adds `Tile.conveyorSpeed` (±120 px/s) to `Player.vx` each frame.
- **Platform (one-way) [T1]:** Pass through from below/sides; land only falling onto top edge.
- **Breakable tiles [T2]:** After 3 projectile hits (hp→0), tile removed from collision.
- **Slope45 [T2]:** Moving right on 45° up-slope converts horizontal speed to 45° diagonal at same magnitude; same for down-slopes. Jump off retains diagonal direction.

### Shooting [T1]

- **Fire:** While fire held AND current gun ammo > 0 AND not reloading AND `swapTimer == 0`: spawn Projectile at muzzle (facing dir, 8 px forward from hitbox edge) with gun's `projectileSpeed`, `damage`, `spreadDeg` random angular jitter. Decrement ammo. Repeat at `1/fireRate` intervals (hold-to-fire).
- **Coil Rifle charge:** If fire held ≥ 0.25 s, stop auto-firing, begin `Player.chargeMeter` 0→1 over `chargeMax` (1.2 s). Release: fire one projectile with `damage = 15 + 25 × chargeMeter`, `pierceCount = 3`. Tap-fire (< 0.25 s): normal 15-damage shot.
- **Flare Launcher arc:** Projectile launches at 45° above facing at 320 px/s; gravity 800 px/s² applies; on first contact with solid/enemy: detonate, deal 55 damage in 90 px radius, apply 300 px/s radial knockback.
- **Reload:** Automatic when ammo hits 0, or manual on R. During `reloadTime` gun cannot fire. Ammo resets to `magSize`.
- **Gun swap:** Keys 1/2/3/4 select directly; K/Shift/scroll cycles. Swap takes 0.3 s (no fire during swap). Only unlocked guns selectable.
- **Crouch-fire:** While crouching, muzzle drops to crouched hitbox top (28 px above feet); `spreadDeg` halved.

### DamageAndDeath [T1]

- **Player takes damage:** On contact with enemy hitbox or enemy Projectile, if `hitTimer == 0`: subtract damage from `hp`; set `hitTimer = 1.0`; apply 180 px/s knockback away from source. While `hitTimer > 0`, invulnerable.
- **Player dies:** `hp ≤ 0`: decrement `lives`. If `lives > 0`: respawn at checkpoint (or stage start) with `hp = 100`, `hitTimer = 1.5`, score kept. If `lives == 0`: → GAME_OVER → Stage Select.
- **Enemy dies:** `hp ≤ 0` → remove, add score (Crawler 100, Turret 200, Drone 150, ShieldTrooper 350). Drop: 20% ammo pickup (refills current gun mag by 3), 8% health orb (+15 hp).
- **Hazard damage:** Touching spike/steam/piston/electric deals its damage once per `hitTimer` window.
- **Fall death:** `Player.y > stageHeight + 64`: instant death (same as hp≤0, no knockback).

### EnemyAI [T1]

Per-frame, each enemy independently:

- **Perception:** Euclidean distance to Player center. ≤ `aggroRange` → CHASE; else → PATROL.
- **Crawler PATROL:** Walk `speed` toward nearest patrolRange edge; reverse at boundary. CHASE: run toward player at `speed × 1.4`. Contact deals `damage`.
- **Turret:** Stationary. CHASE: aim at player (no LOS check), fire Projectile (damage 10, speed 300) every 1.8 s. Cannot be knocked back.
- **Drone:** Hovers at `Player.y − 60 px`. PATROL: sinusoidal bob (±30 px, period 2 s). CHASE: drift toward player at `speed`; contact deals `damage`. **Hit only by projectiles fired above 20° or by jump-contact.**
- **ShieldTrooper:** PATROL: walk slowly. CHASE: advance at `speed`; front ±60° arc blocks projectiles (redirects to shield, separate 60 hp pool). Shield breaks → normal damage. Attack: 1 s wind-up lunge (30 px/s for 0.5 s), deals `damage` on contact.
- **Knockback on enemy:** Apply `Gun.knockback × (1 − Enemy.knockbackResist)` as instantaneous vx impulse away from projectile.

### BossAI [T1]

Boss is a BossPhase sequence. Phase hp reaches `transitionAt` fraction → boss flashes (1.5 s invulnerable), advances to next phase.

**Rust Colossus (W1S5):** 3 phases (HP 200/200/200).
- Phase 1 (sweep, interval 2.5 s): walks back/forth across 400 px arena, arm swing (60 px hitbox, damage 25).
- Phase 2 (volley, interval 3.0 s): stops, fires 5 projectiles in fan (damage 12 each, speed 280).
- Phase 3 (charge + summon, interval 2.0 s): 1 s telegraph then dash 500 px/s (damage 35); every 6 s summons 2 Crawlers.

**Core Warden (W2S5):** 4 phases (HP 180/180/180/180).
- Phase 1 (laser, interval 3.0 s): horizontal beam sweep, 2 s active, damage 20/s contact.
- Phase 2 (volley, interval 2.5 s): 8 homing drones (damage 15, speed 180, lifetime 4 s).
- Phase 3 (electrify, interval 5.0 s): entire arena floor becomes electricFloor for 3 s; player must jump onto floating platforms.
- Phase 4 (all, interval 1.5 s): all three attacks in rotation.

Boss immune to knockback. Damaged from any angle.

### StageGenerator [T1]

Seeded generator per Stage record. Inputs: `seed`, `width`, `height` (720), `worldTheme`, `difficultyTier` (1–5 = stage number).

**Placement order:**
1. **Ground layer:** Solid tiles along bottom (y = 672). Gaps 3–6 tiles wide at intervals of 8–14 tiles (more at higher tier). Breakable tile in 15% of gaps [T2].
2. **Platform tier:** Every 6–10 tile interval, one-way platform at y = 528 or 432. Width 3–7 tiles.
3. **Hazard scatter:** Spikes on 10–20% of ground tiles (never within 2 tiles of gap edge). 1 steamVent per 12 tiles of ground (period 3 s, active 1.5 s). Tier ≥ 3: crushingPiston (period 4 s, active 1.0 s).
4. **Enemy spawn points:** One enemy every 10–16 tiles. Tier 1: Crawlers. Tier 2: + Turrets. Tier 3: + Drones. Tier 4: + ShieldTroopers. Tier 5: mix all.
5. **Chest / pickup:** Gun-unlock chest at hard-coded stage (W1S2→shotgun, W1S4→coil, W2S2→flare). Health orb every 20 tiles.
6. **Extraction point:** Blast door at x = width − 120. Reaching it ends stage.
7. **Hidden side-room [T2]:** Stages 1, 3 of each world: breakable wall at random ground position; behind it 200×120 px room with UpgradeChip.

**Verifier (runs after generation):**
- Every gap crossable: max gap ≤ 6 tiles AND platform within 12 px vertical / 120 px horizontal of gap edge.
- No enemy spawns inside solid tile.
- No hazard within 200 px of extraction point.
- Player can reach extraction from start (BFS on walkable+jumpable graph, max jump height 120 px, max jump distance 180 px).
- Any failure → re-roll with `seed + 1`.

### ProgressionAndUnlocks [T1]

- WorldMap starts with W1S1 unlocked. Clearing stage unlocks next in sequence. Clearing W1S5 unlocks W2S1. Clearing W2S5 → Victory.
- Gun chests hard-placed: W1S2→Rivet Shotgun, W1S4→Coil Rifle, W2S2→Flare Launcher. Opening sets `unlocked = true` permanently for the run.
- UpgradeChips [T2]: permanently modify target gun stat for the rest of the run.
- Checkpoints: 1 mid-stage flag per stage. Reaching saves respawn position (not after lives-0 game-over).

### Scoring [T1]

- Crawler 100, Turret 200, Drone 150, ShieldTrooper 350, Boss-phase-clear 1000.
- Speed bonus: stage completed in ≤ 60% of par time (par = width/200 s) → +500.
- No-damage bonus: `hp == 100` at extraction → +1000.
- Chip bonus [T2]: +250 per UpgradeChip.
- Rank thresholds per stage (bronze/silver/gold) displayed on StageComplete.

### TouchControls [T2]

- Left half: virtual D-pad (left, right, down=crouch). Up swipe on left half = jump.
- Right half: tap = fire (hold = auto/charge). Swipe up on right half = jump.
- Bottom-right circle: gun-swap (cycles unlocked).
- Bottom-left circle: reload.
- All map to same rule IDs as keyboard.

## Progression and Difficulty

**Order:** W1S1 → W1S2 (shotgun) → W1S3 → W1S4 (coil rifle) → W1S5 (Rust Colossus) → W2S1 → W2S2 (flare launcher) → W2S3 → W2S4 → W2S5 (Core Warden) → Victory.

**Early (W1S1–S2):** Crawlers only (30 hp, 3 pistol hits). Mostly continuous ground, 3-tile gaps. 3 lives. Scrap Pistol trivially clears.

**Mid (W1S3–S4, W2S1–S3):** Turrets force positioning. Drones punish staying grounded. ShieldTroopers demand shotgun/coil. Gaps 5–6 tiles. Steam vents, pistons. Expected 1–2 deaths per stage; checkpoints soften.

**Late/Boss (W1S5, W2S5):** Rust Colossus Phase 3 uses all guns. Core Warden Phase 3 forces platforming under fire; Phase 4 demands mid-fight swaps. Boss HP 200/180 per phase ≈ 15–20 hits; fight lasts 60–90 s.

**Recovery:** Death → respawn at checkpoint, full HP, 1.5 s i-frames, score kept, lose 1 life. All lives → Stage Select, immediate retry. No permadeath. 3 lives reset each stage attempt.

**Scaling knobs:** `difficultyTier` (1–5): enemy density 16→10 tiles, gap 3→6, hazard count, mix. Boss intervals 2.5→1.5 s. UpgradeChips: +4 dmg or +1 fireRate per chip.

## Feel

| Parameter | Value | Tuned to achieve |
|---|---|---|
| Run speed | 280 px/s | 4800 px in ~25 s sprint; snappy |
| Acceleration | 2400 px/s² | Top speed in ~0.12 s |
| Friction/decel | 1800 px/s² | Stop in ~0.16 s; crisp |
| Jump vy | −520 px/s | Peak ≈ 84 px (≈2 tiles); clears 3-tile gaps |
| Variable jump cut | 0.18 s / −260 vy | Short hop 30 px for precision |
| Gravity | 1600 px/s² | Hang-time ≈ 0.65 s |
| Crouch height | 48→28 px | Fits under 32-px pipes |
| Crouch speed | 140 px/s | Mobile but vulnerable |
| Hit i-frames | 1.0 s | Enough to escape, feels punishing |
| Death i-frames | 1.5 s | Grace on respawn |
| Pistol fire rate | 6.0/s | 167 ms tap-rap |
| Shotgun fire rate | 1.4/s | 714 ms heavy pump |
| Coil charge | 1.2 s | Risky but usable in 2-s window |
| Flare fire rate | 0.8/s | 1.25 s; each shot is an event |
| Shotgun knockback | 220 px/s × (1−0) = 220 | Crawler tumbles ~0.3 s |
| Pistol knockback | 80 px/s | Small nudge |
| Enemy→player knockback | 180 px/s | Push back ~0.25 s |
| Projectile lifetime | 3.0 s | ~1800 px at pistol speed |
| Reload times | 1.4–3.5 s | Pistol fast, flare slow |
| Gun swap | 0.3 s | Fluid but no instant stacking |
| Boss dash telegraph | 1.0 s | Readable; dodge by jump/crouch |
| Boss phase flash | 1.5 s invuln | Breather, signals new pattern |
| Stage par time | width/200 s (4800→24 s) | Skilled finish ~20–25 s; Gold <14 s |
| Camera deadzone | 80 px H, 60 px V | See threats, avoid jitter |
| Camera lerp | 0.08 X, 0.12 Y per frame | Smooth, no rubber-band |
| Touch fire radius | 72 px | Comfortable thumb on 6" phone |

---

# 5. CHARACTERS

## Player — "Kael"

**Silhouette:** Broad-shouldered, short-legged, helmeted figure with single glowing visor slit. Gun always visible at arm. Squishy proportions (head ≈ 30% of height). Crouch halves silhouette.

**Facings:** 2 (left, right). No up/down.

**Animations:**

| Name | Motion rule | Duration | State trigger |
|---|---|---|---|
| Idle | 4-frame bob: torso Y 0,−2,0,+2. Visor pulses glow. | 1.5s loop | `grounded && vx==0 && !crouching` |
| Run | 4-frame leg cycle (contact, down, pass, up). Torso leans 10°. Gun bobs 1u. | 0.32s loop | `grounded && |vx|>10` |
| Jump (ascent) | Legs tuck, arms up. Squash 0.9×w, 1.1×h. | Single pose until apex | `vy < 0` |
| Jump (descent) | Legs extend, arms out. Stretch 1.1×w, 0.9×h. | Single pose until land | `vy > 0 && !grounded` |
| Land | 3-frame squash 1.2→1.0→0.95. Dust puff (2 grey circles 10u, fade 0.3s). | 0.2s | transition to `grounded` |
| Crouch | Torso compresses to 60%. Head drops. Gun aims down 15°. | Instant pose, hold | `crouching == true` |
| Fire | Arm recoils back 4u, muzzle flash. 2-frame fire→recover. | 0.1–0.15s | on fire event |
| Hurt | Flash white 3× at 0.05s intervals. Lean back 15°. | 0.3s | `hitTimer > 0` |
| Death | Fall backward, spin 180°, dissolve into 8 amber/cyan particles. | 1.0s | `hp <= 0` |

## Crawler (W1 "Smelter Bot" / W2 "Cryo Stalker")

**Silhouette W1:** Wide, low, furnace-bellied. Reads "tank." 48×44.
**Silhouette W2:** Tall, thin, insectoid, 4 legs. Reads "fast threat." 32×52.

| Name | Rule | Duration |
|---|---|---|
| Idle | Chest glow pulse / head tilt ±8°. | 1.5s |
| Walk | 2-frame leg stomp / leg scuttle. | 0.5s loop |
| Fire (W1 only) | Arm extends, chest flares, flame projectile. | 0.3s |
| Hurt | Flash, stagger 6u. | 0.25s |
| Death | Collapse inward, glow→dark, smoke / shatter into 6 triangles. | 0.6s / 0.4s |

## Turret

**Silhouette:** Mounted barrel on base plate. 40×36. Colours: #3D3D5E, accent joint.

| Name | Rule | Duration |
|---|---|---|
| Idle | Barrel tracks player slowly. | continuous |
| Fire | Barrel flashes, projectile spawns. | 0.15s |
| Hurt | Flash white. | 0.1s |
| Death | Barrel spins off, base explodes. | 0.4s |

## Drone ("Rivet Drone")

**Silhouette:** Small hexagon, single rotor on top, 2 eye dots. 28×28.

| Name | Rule | Duration |
|---|---|---|
| Hover | Y bob ±6u sine. Rotor 360°/s. Tilt toward player. | 1.2s loop |
| Fire | Tilt forward 10°, eye flash #FFD700, bullet. | 0.15s |
| Hurt | Flash white, drop 10u, wobble. | 0.2s |
| Death | Spin + shrink to 0, small explosion. | 0.3s |

## ShieldTrooper

**Silhouette:** Armoured humanoid with front-mounted rectangular shield. 40×52.

| Name | Rule | Duration |
|---|---|---|
| Patrol | Slow walk, shield raised. | 1s loop |
| Chase | Advance, shield forward. | continuous |
| Lunge | 1 s wind-up (shield pulls back), then 0.5 s dash. | 1.5s |
| Shield break | Shield shatters into 4 fragments. | 0.3s |
| Hurt | Flash, stagger. | 0.2s |
| Death | Collapse, shield fragments scatter. | 0.5s |

## Boss — Rust Colossus

**Silhouette:** Massive 160×200, furnace torso, 2 hydraulic arms, smokestack head.

| Name | Rule | Duration |
|---|---|---|
| Idle | Core pulse, smokestack puffs (3 grey/s), sway. | 2s loop |
| Arm sweep | Right arm arcs 120° forward, ground cracks (4 lines). | 0.8s |
| Slag vomit | Head tilts back, orange stream projectile. | 1.0s |
| Charge telegraph | Crouches, core brightens, 1 s hold. | 1.0s |
| Charge dash | Horizontal dash 500 px/s, ground sparks. | 0.8s |
| Summon | Arm slams ground, 2 Crawlers emerge from cracks. | 1.0s |
| Hurt | Core flashes white, 3 sparks, stagger 4px. | 0.3s |
| Phase transition | 1.5 s invuln, body flashes, new colour accent. | 1.5s |
| Death | Core overcharges (white→red), 5 explosions over 2s, collapse, screen flash. | 2.5s |

## Boss — Core Warden

**Silhouette:** Tall 120×220, crystalline humanoid, 4 floating ice shards orbiting.

| Name | Rule | Duration |
|---|---|---|
| Idle | Float ±8u. 4 shards orbit 120°/s, radius 60u. Eyes glow. | 3s loop |
| Laser sweep | Horizontal beam extends, sweeps across arena. | 2.0s |
| Shard throw | 1 shard detaches, fires toward player. | 0.3s |
| Ice storm | Spins 360°, 4 shards in cross pattern, frost overlay. | 1.2s |
| Electrify | Floor glows cyan, arcs appear. | 3.0s |
| Hurt | Flash #A8E6FF, shards wobble, frost particles. | 0.3s |
| Phase transition | 1.5 s invuln, shards reform. | 1.5s |
| Death | Shards shatter outward, body freezes then cracks into 12 pieces. | 2.0s |

---

# 6. AUDIO

All sounds generated via Web Audio API. No external files.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| `pistol_fire` | Square wave, 440 Hz, 0.06 s, attack 0.005 s, decay 0.055 s, gain 0.3 | §4 Shooting – fire event, Scrap Pistol |
| `shotgun_fire` | Noise burst + saw 110 Hz, 0.15 s, attack 0.005 s, decay 0.14 s, gain 0.5 | §4 Shooting – fire event, Rivet Shotgun |
| `coil_charge` | Sine sweep 200→800 Hz, 1.2 s, attack 0.1 s, sustain, gain 0.2 | §4 Shooting – coil charge begins |
| `coil_fire` | Saw 600 Hz + click, 0.1 s, attack 0.002 s, decay 0.098 s, gain 0.4 | §4 Shooting – coil release |
| `flare_fire` | Sine 180 Hz + noise, 0.2 s, attack 0.01 s, decay 0.19 s, gain 0.4 | §4 Shooting – flare launch |
| `flare_explode` | Noise burst 80 Hz, 0.3 s, attack 0.005 s, decay 0.295 s, gain 0.6 | §4 Shooting – flare detonation |
| `bullet_hit` | Triangle 1200 Hz, 0.04 s, attack 0.002 s, decay 0.038 s, gain 0.2 | §4 DamageAndDeath – player bullet hits enemy |
| `bullet_wall` | Noise tick, 0.03 s, gain 0.15 | §4 Shooting – bullet hits solid tile |
| `player_hit` | Square 220 Hz, 0.12 s, attack 0.005 s, decay 0.115 s, gain 0.4 | §4 DamageAndDeath – player takes damage |
| `jump` | Sine sweep 300→600 Hz, 0.1 s, attack 0.01 s, decay 0.09 s, gain 0.2 | §4 Locomotion – jump |
| `land` | Noise thud 100 Hz, 0.08 s, gain 0.2 | §4 Locomotion – landing |
| `crouch` | Sine 250 Hz, 0.05 s, gain 0.1 | §4 Locomotion – crouch begins |
| `gun_swap` | Triangle 500→700 Hz, 0.08 s, gain 0.2 | §4 Shooting – gun swap |
| `reload` | 3× tick (square 800 Hz, 0.03 s each, spaced 0.1 s), gain 0.15 | §4 Shooting – reload |
| `enemy_death` | Noise burst + saw 150 Hz, 0.2 s, attack 0.005 s, decay 0.195 s, gain 0.4 | §4 DamageAndDeath – enemy dies |
| `boss_hit` | Square 300 Hz, 0.08 s, gain 0.3 | §4 BossAI – boss takes damage |
| `boss_phase` | Sine sweep 400→200 Hz, 0.5 s, gain 0.4 | §4 BossAI – phase transition |
| `boss_death` | Noise 60 Hz + saw 80 Hz, 1.0 s, attack 0.01 s, decay 0.99 s, gain 0.7 | §4 BossAI – boss dies |
| `pickup_ammo` | Triangle 600→900 Hz, 0.1 s, gain 0.2 | §4 DamageAndDeath – ammo pickup |
| `pickup_health` | Sine 500→800 Hz, 0.15 s, gain 0.25 | §4 DamageAndDeath – health orb |
| `pickup_weapon` | Arpeggio (400,500,600,800 Hz) 0.3 s, gain 0.35 | §4 ProgressionAndUnlocks – gun chest |
| `pickup_chip` | Sine 700→1200 Hz, 0.2 s, gain 0.3 | §4 ProgressionAndUnlocks – upgrade chip [T2] |
| `hazard_hit` | Saw 150 Hz + noise, 0.15 s, gain 0.4 | §4 DamageAndDeath – hazard damage |
| `death` | Sine sweep 400→100 Hz, 0.6 s, gain 0.5 | §4 DamageAndDeath – player dies |
| `stage_clear` | Ascending arpeggio (C-E-G-C) 0.8 s, gain 0.4 | §4 ProgressionAndUnlocks – reach extraction |
| `game_over` | Descending minor (C-Ab-F-D) 1.2 s, gain 0.4 | §4 DamageAndDeath – lives == 0 |
| `menu_select` | Triangle 500 Hz, 0.05 s, gain 0.2 | §7 UX – cursor confirm |
| `menu_move` | Triangle 400 Hz, 0.03 s, gain 0.15 | §7 UX – cursor move |
| `turret_fire` | Square 350 Hz, 0.08 s, gain 0.25 | §4 EnemyAI – turret shoots |
| `drone_fire` | Triangle 900 Hz, 0.04 s, gain 0.15 | §4 EnemyAI – drone shoots |

---

# 7. UX

## Screen state machine

```
TITLE → [Enter/Space/tap] → WORLDMAP
WORLDMAP → [select unlocked stage] → STAGEINTRO (1.5s card) → PLAYING
PLAYING → [reach extraction] → STAGE_COMPLETE → [Enter] → WORLDMAP
PLAYING → [lives == 0] → GAME_OVER → [Enter] → WORLDMAP (same stage, lives=3)
PLAYING → [clear W2S5 boss] → VICTORY (30s credits) → [auto/Enter] → TITLE
PLAYING / WORLDMAP → [P/Escape] → PAUSE → [Resume] → PLAYING
PAUSE → [R] → PLAYING (stage restart)
PAUSE → [Q/Escape] → WORLDMAP
```

## Screen controls

| Screen | Input | Action |
|---|---|---|
| Title | Enter / Space / tap | → WorldMap |
| WorldMap | ←→ / A D | Move cursor (unlocked only) |
| WorldMap | Enter / tap | → StageIntro |
| WorldMap | Escape | → Title |
| Gameplay | (as controls table §1.2) | Play |
| Gameplay | P / Escape | → Pause |
| Pause | Enter | Resume |
| Pause | R | Restart Stage |
| Pause | Q / Escape | → WorldMap |
| StageComplete | Enter | → WorldMap (next highlighted) |
| GameOver | Enter | Restart same stage (lives=3) |
| Victory | auto 30s / Enter | → Title |

## HUD (visible during PLAYING only)

| Element | Record field | Position / Style | Visibility |
|---|---|---|---|
| HP bar | `Player.hp` / 100 | Top-left, 120×12 px, fill #FF4500→#FFD700, bg #1A1A2E, 3px stroke #3D3D5E | Always |
| Life icons | `Player.lives` | Below HP bar, 3 small skull icons (filled = remaining) | Always |
| Score counter | `Player.score` | Top-center, text #FFFFFF | Always |
| Active gun name + icon | `Player.activeGun` | Top-right, text #FF8C00 + weapon icon | Always |
| Magazine counter | current gun `ammo`/`maxAmmo` | Below gun name, e.g. "8/12", text #00F5FF; flashes red ≤ 2 | Always |
| Reload arc | reload timer fraction | Circular progress under mag counter | Only during reload |
| Charge meter | `Player.chargeMeter` | Bar under crosshair area, fill #00F5FF→#FFFFFF | Only while Coil Rifle charging |
| Stage timer | `ctx.time` | Bottom-left, small text | Always (except boss stage) |
| Boss HP bar | `boss.hp` / `boss.maxHp` | Top-center, 300×16 px, fill #FF4500 | Only boss stage, boss alive |
| Checkpoint indicator | `checkpointReached` | Small flag icon, fades in after touch | After checkpoint |
| World/Stage label | `ctx.world`, `ctx.stage` | Below score, "W1 – S3", text #A0A0B0 | Always |

## HTML/CSS structure

```html
<div id="game-container" style="position:relative;width:960px;height:540px;margin:auto;">
  <canvas id="game-canvas" width="960" height="540"></canvas>
  <!-- Touch overlays (T2) -->
  <div id="touch-left" class="touch-zone"></div>
  <div id="touch-right" class="touch-zone"></div>
  <div id="touch-jump" class="touch-btn"></div>
  <div id="touch-fire" class="touch-btn"></div>
  <div id="touch-swap" class="touch-btn"></div>
  <div id="touch-reload" class="touch-btn"></div>
</div>
```

CSS: `#game-container` scales via `transform: scale()` to fit viewport while maintaining 16:9. Touch buttons: 72 px radius circles, 50% opacity, positioned in corners. All overlays pointer-events:none except touch zones.

---

# 8. DEBUG API

`game.init()` installs `window.__game`. Every method synchronous, returns plain data only.

| Call | What it does | Returns |
|---|---|---|
| `start()` | `state='PLAYING'`, `progression.loadStage(1,1)`. | `undefined` |
| `step(dt, n)` | Runs exactly `n` ticks of length `dt`, then `renderer.draw()` once. Cancels rAF during step. | `undefined` |
| `setTime(t)` | Advances to absolute time `t` s (runs required DT ticks) without drawing. | `undefined` |
| `seed(n)` | Reseeds rng, rebuilds generated content. Resets time/frame to 0. | `undefined` |
| `getState()` | Deep-clones ctx into plain object. | `{ time, frame, state, world, stage, lives, score, player:{...}, weapons:{...}, enemies:{...}, boss:{...}, camera:{...}, level:{...}, input:{...} }` |
| `setField(path, value)` | Sets ctx field at dot-path. | `undefined` |
| `moveDir(dx)` | Persistent horizontal input: −1/0/+1. | `undefined` |
| `jump()` | One jump press (jumpPressed=true for one tick). | `undefined` |
| `crouch(down)` | true=hold, false=release. | `undefined` |
| `shoot(down)` | true=hold, false=release. | `undefined` |
| `reload()` | Trigger manual reload. | `undefined` |
| `switchGun()` | One cycle press. | `undefined` |
| `selectGun(index)` | Direct select 0–3. | `undefined` |
| `spawnEnemy(type, x, y)` | `enemies.spawn(type,x,y)`. | `{id,x,y,type,health}` or `{id:-1}` |
| `spawnBullet(gunIndex, x, y, dir)` | Insert bullet into pool. | `{id,x,y,vx,vy}` |
| `skipTo(world, stage)` | `progression.loadStage(world,stage)`. | `undefined` |
| `setHealth(v)` | `player.health = v`. | `undefined` |
| `setAmmo(gunIndex, v)` | Set gun ammo. | `undefined` |
| `setPos(x, y)` | Teleport player. | `undefined` |
| `unlockAllGuns()` | Sets all guns unlocked. | `undefined` |
| `spawnBoss(type)` | Initialise boss fight. | `undefined` |
| `damageBoss(amount)` | Apply damage to boss. | `undefined` |
| `setCharge(v)` | Set `player.chargeMeter = v`. | `undefined` |
| `getFPS()` | Measured FPS over last 60 real frames (0 if stepped). | number |
| `getDrawCalls()` | Draw-call count from last renderer.draw(). | number |
| `resume()` | Restart rAF loop after step/setTime. | `undefined` |

**Determinism contract:** Same `seed(n)` + same sequence of `step`/input calls → `getState()` returns byte-identical JSON.

---

# 9. TESTS

All checks run through `window.__game` only. Assertion syntax: `ASSERT(expr, msg)`.

### Boot & state machine

**T1-01. Title draws.** `init()` called. `ASSERT(getState().state === 'TITLE')`. After `step(1/60,1)`: `ASSERT(getDrawCalls() > 0)`.

**T1-02. Start enters play.** `start()`. `ASSERT(getState().state === 'PLAYING')`. `ASSERT(getState().world === 1)`. `ASSERT(getState().stage === 1)`. `ASSERT(getState().player.alive === true)`. `ASSERT(getState().player.health === 100)`.

### Movement & physics

**T1-03. Walk right.** `seed(42)`, `start()`, `moveDir(1)`, `step(1/60, 60)`. `ASSERT(player.x > 120 + 280 * 0.5)`. `ASSERT(player.grounded === true)`. `ASSERT(player.anim === 'run')`.

**T1-04. Walk left.** `moveDir(-1)`, `step(1/60, 30)`. `ASSERT(player.x < previous_x)`.

**T1-05. Stop.** `moveDir(0)`, `step(1/60, 60)`. `ASSERT(Math.abs(player.vx) < 1)`.

**T1-06. Jump.** `moveDir(0)`, `jump()`, `step(1/60, 1)`. `ASSERT(player.jumping === true)`. `ASSERT(player.grounded === false)`. `ASSERT(player.vy < 0)`. After `step(1/60, 40)`: `ASSERT(player.grounded === true)`.

**T1-07. Variable jump cut.** `jump()`, `step(1/60, 5)` (≈0.083 s < 0.18 s), release jump (inject jump=false), `step(1/60, 1)`. `ASSERT(player.vy === -260 || player.vy > -260)` (cut applied). Compare full jump: `ASSERT(vy_cut > vy_full)` (less negative = shorter hop).

**T1-08. Crouch.** `crouch(true)`, `step(1/60, 1)`. `ASSERT(player.crouching === true)`. `ASSERT(player.h === 28)`. `crouch(false)`, `step(1/60, 1)`. `ASSERT(player.crouching === false)`. `ASSERT(player.h === 48)`.

**T1-09. Crouch disables jump.** `crouch(true)`, `step(1/60,1)`, `jump()`, `step(1/60,1)`. `ASSERT(player.vy === 0 || player.grounded === true)` (no jump while crouched).

**T1-10. Gravity / fall.** `setPos(0, 0)`, `step(1/60, 30)`. `ASSERT(player.y > 0)`. `ASSERT(player.vy > 0)`.

**T1-11. Terminal velocity.** `setPos(0, -2000)`, `step(1/60, 120)`. `ASSERT(player.vy <= 700)`.

### Weapons

**T1-12. Pistol fire.** `seed(42)`, `start()`, `selectGun(0)`. `shoot(true)`, `step(1/60, 1)`. `ASSERT(weapons.bullets.length >= 1)`. `ASSERT(weapons.guns[0].ammo === 11)`. `shoot(false)`.

**T1-13. Fire rate.** `shoot(true)`, `step(1/60, 12)` (0.2 s). At 6 shots/s, expect ≥ 1 bullet in 0.2 s. `ASSERT(weapons.bullets.length >= 1)`. `shoot(false)`.

**T1-14. Switch gun (cycle).** `switchGun()`, `step(1/60, 1)`. `ASSERT(player.gunIndex === 1)`. `switchGun()` ×3, `step(1/60,1)` each. `ASSERT(player.gunIndex === 0)` (wraps).

**T1-15. Switch gun (direct).** `selectGun(2)`, `step(1/60,1)`. `ASSERT(player.gunIndex === 2)`.

**T1-16. Gun swap lockout.** `selectGun(3)`, `step(1/60, 1)`. `shoot(true)`, `step(1/60, 1)`. `ASSERT(weapons.bullets.length === 0)` (swapTimer 0.3 s = 18 ticks; 1 tick not enough). `step(1/60, 18)`. `shoot(true)`, `step(1/60, 1)`. `ASSERT(weapons.bullets.length >= 1)`.

**T1-17. Shotgun pellets.** `unlockAllGuns()`, `selectGun(1)`, `step(1/60, 20)`. `shoot(true)`, `step(1/60, 1)`. `ASSERT(bullets_spawned_this_tick === 5)`. `shoot(false)`.

**T1-18. Coil Rifle charge.** `selectGun(2)`, `step(1/60, 20)`. `shoot(true)`, `step(1/60, 20)` (0.33 s > 0.25 s → charging begins). `ASSERT(player.chargeMeter > 0)`. `step(1/60, 52)` (total 1.2 s charge). `shoot(false)`, `step(1/60, 1)`. `ASSERT(bullet.damage >= 40)`. `ASSERT(bullet.pierceLeft === 3)`.

**T1-19. Coil tap-fire.** `selectGun(2)`, `step(1/60, 20)`. `shoot(true)`, `step(1/60, 10)` (0.17 s < 0.25 s). `shoot(false)`, `step(1/60, 1)`. `ASSERT(bullet.damage === 15)`.

**T1-20. Flare Launcher arc.** `selectGun(3)`, `step(1/60, 20)`. `shoot(true)`, `step(1/60, 1)`. `ASSERT(bullet.vy < 0)` (upward component). `step(1/60, 60)`. `ASSERT(bullet.vy > 0)` (gravity pulled it down).

**T1-21. Reload automatic.** `setAmmo(0, 1)`, `selectGun(0)`, `step(1/60, 20)`. `shoot(true)`, `step(1/60, 1)`. `shoot(false)`. `ASSERT(weapons.guns[0].ammo === 0)`. `step(1/60, 90)` (1.4 s = 84 ticks). `ASSERT(weapons.guns[0].ammo === 12)`.

**T1-22. Reload manual.** `selectGun(0)`, `step(1/60, 20)`. `shoot(true)`, `step(1/60, 1)`, `shoot(false)`. `reload()`, `step(1/60, 1)`. `ASSERT(weapons.guns[0].ammo === 12)` (or reloading flag). `step(1/60, 90)`. `ASSERT(weapons.guns[0].ammo === 12)`.

### Enemies & combat

**T1-23. Enemy spawn.** `seed(7)`, `start()`. `spawnEnemy('crawler', 500, 640)`. `ASSERT(enemies.pool contains entry with type==='crawler', x===500, y===640, hp===30)`.

**T1-24. Player takes damage.** `setPos(enemy.x, enemy.y)`, `step(1/60, 1)`. `ASSERT(player.health === 100 - 15)`. `ASSERT(player.invulnTimer > 0)`.

**T1-25. Invulnerability.** Immediately `step(1/60, 1)` again. `ASSERT(player.health === 85)` (unchanged).

**T1-26. I-frames expire.** `setHealth(100)`, `setPos(enemy.x, enemy.y)`, `step(1/60, 1)`. `step(1/60, 60)` (1 s). `ASSERT(player.invulnTimer === 0)`. `setPos(enemy.x, enemy.y)`, `step(1/60, 1)`. `ASSERT(player.health < 100)`.

**T1-27. Enemy dies.** `spawnEnemy('crawler', player.x + 50, player.y)`, `selectGun(0)`, `step(1/60, 20)`. Fire 3 shots (30 hp / 12 dmg = 3 hits). `step(1/60, 15)`. `ASSERT(crawler removed from pool)`. `ASSERT(score >= 100)`.

**T1-28. Knockback on enemy.** `spawnEnemy('crawler', player.x + 50, player.y)`. Fire pistol. `ASSERT(crawler.vx after hit === 80 * (1 - 0) = 80)` (away from player).

**T1-29. Turret fires.** `spawnEnemy('turret', player.x + 200, player.y)`. `step(1/60, 110)` (1.8 s). `ASSERT(enemy bullet exists)`.

**T1-30. Drone vulnerability.** `spawnEnemy('drone', player.x + 100, player.y - 60)`. Fire horizontally (angle 0°). `step(1/60, 10)`. `ASSERT(drone.hp === 20)` (not hit). Fire at 25° upward. `step(1/60, 10)`. `ASSERT(drone.hp < 20)`.

**T1-31. ShieldTrooper shield.** `spawnEnemy('shieldTrooper', player.x + 100, player.y)`. Fire pistol at front. `step(1/60, 5)`. `ASSERT(shieldHp < 60)`. `ASSERT(shieldTrooper.hp === 80)`.

**T1-32. Death & respawn.** `setHealth(0)`, `step(1/60, 1)`. `ASSERT(player.alive === false)`. `ASSERT(lives === 2)`. After `step(1/60, 90)`: `ASSERT(player.alive === true)`. `ASSERT(player.health === 100)`. `ASSERT(player.invulnTimer > 0)`.

**T1-33. Game over.** `setField('lives', 0)`, `setHealth(0)`, `step(1/60, 1)`. `ASSERT(state === 'GAME_OVER')`.

**T1-34. Fall death.** `setPos(200, 790)` (stageHeight 720 + 64 = 784; 790 > 784). `step(1/60, 1)`. `ASSERT(player.alive === false)`.

### Level & progression

**T1-35. Tile collision / grounded.** `setPos(120, 624)` (on ground row). `step(1/60, 1)`. `ASSERT(player.grounded === true)`. `ASSERT(player.y === 624)`.

**T1-36. Stage clear.** `setPos(level.flagX + 1, player.y)`, `step(1/60, 1)`. `ASSERT(state === 'STAGE_CLEAR')`. After `step(1/60, 120)` (2 s clear timer): `ASSERT(state === 'PLAYING')`. `ASSERT(stage === 2)`.

**T1-37. World progression.** `skipTo(1, 5)`, clear boss (damage boss to 0). `ASSERT(world === 2)`. `ASSERT(stage === 1)`.

**T1-38. Victory.** `skipTo(2, 5)`, clear Core Warden. `ASSERT(state === 'VICTORY')`.

**T1-39. Gun unlock chest.** `skipTo(1, 2)`. `setPos(chest.x, chest.y)`, `step(1/60, 1)`. `ASSERT(weapons.guns[1].unlocked === true)`.

### Boss

**T1-40. Boss init.** `skipTo(1, 5)`. `spawnBoss('rustColossus')`. `ASSERT(boss.active === true)`. `ASSERT(boss.phases.length === 3)`. `ASSERT(boss.hp === 200)`.

**T1-41. Boss phase transition.** `damageBoss(140)` (200→60, below transitionAt). `step(1/60, 90)` (1.5 s flash). `ASSERT(boss.phase === 1)`. `ASSERT(boss.hp === 200)` (new phase).

**T1-42. Boss death.** `skipTo(1, 5)`, `spawnBoss('rustColossus')`. `damageBoss(600)` (all phases). `step(1/60, 150)` (2.5 s death anim). `ASSERT(boss.state === 'dead')`.

### Camera

**T1-43. Follow & clamp.** `moveDir(1)`, `step(1/60, 120)`. `ASSERT(camera.x > 0)`. `ASSERT(camera.x <= level.stageWidth - 960)`.

**T1-44. Deadzone.** `start()`, `moveDir(1)`, `step(1/60, 1)`. `ASSERT(camera.x === 0)` (player within 80 px deadzone, camera hasn't moved yet).

### Audio

**T1-45. SFX queue.** `start()`, `shoot(true)`, `step(1/60, 1)`. `ASSERT(audio.sfxQueue.length > 0)`. `shoot(false)`.

### Determinism

**T1-46. Reproducibility.**
```
seed(1234); start(); moveDir(1); jump(); shoot(true); step(1/60, 300);
const a = JSON.stringify(getState());
seed(1234); start(); moveDir(1); jump(); shoot(true); step(1/60, 300);
const b = JSON.stringify(getState());
ASSERT(a === b);
```

### Budgets

**T1-47. Draw calls.** After `step(1/60, 1)`: `ASSERT(getDrawCalls() <= 200)`.

**T1-48. Entity cap.** `spawnEnemy('crawler', 100, 100)` × 65. `ASSERT(65th returns {id: -1})`. `ASSERT(enemies.pool.length === 64)`.

**T1-49. Bullet cap.** `shoot(true)`, `step(1/60, 200)` without hitting anything. `ASSERT(weapons.bullets.length <= 128)`.

### Generator & Verifier

**T1-50. Generator produces valid stage.** `seed(99)`, `start()`. `ASSERT(level.tiles !== null)`. `ASSERT(level.stageWidth === 4800)`. `ASSERT(level.flagX === 4680)`. `ASSERT(player.spawnX === 120)`.

**T1-51. Boss arena dimensions.** `skipTo(1, 5)`. `ASSERT(level.stageWidth === 2400)`.

### Touch (T2)

**T2-01. Touch move.** `inject('left', true)`, `step(1/60, 30)`. `ASSERT(player.vx < 0)`.

### Upgrade chips (T2)

**T2-02. Chip collection.** `skipTo(1, 1)`, navigate to chip room, `setPos(chip.x, chip.y)`, `step(1/60,1)`. `ASSERT(weapons.guns[0].dmg === 16)` (if chip is damage+4 on pistol).

### Screenshots

| Screen / State | How to Reach | What Must Be Visible |
|---|---|---|
| Title | Launch | "FORGE BREAKER" logo amber/cyan gradient, animated gear+crystal bg, "PRESS START" pulsing, parallax factory |
| World map | After title | 2 rows × 5 circles. W1 amber, W2 cyan. Completed=filled+check, next=pulse, locked=grey. Stage numbers. |
| Stage 1-1 start | Select 1-1 | Camera pans to player X=120. Loading dock, crates, warm amber glow. Player idle-bob. HUD top-left. |
| Running + shooting | Play 1-2 zone 2 | Player mid-run (leg cycle), gun aimed right, muzzle flash amber, conveyor scrolling, drone ahead, platforms above, parallax gears. |
| Crouch under pipe | 1-3 pipe section | Player 28 px tall under 32 px pipe, gun angled down, visor glow, amber floor. |
| Jump over hazard | 1-2 slag pit | Player airborne (legs tucked), slag pit glow+shimmer below, platform ahead, bullet trail. |
| New weapon pickup | 1-3 zone 4 | Spinning Coil Rifle icon above crate, screen flash cyan, "COIL RIFLE" text bottom. |
| Coil Rifle firing | After pickup | Cyan beam 200u across screen, arms extended, charge glow, enemy hit, sparks. |
| Flare Launcher in use | 2-2 | Green/amber droplet arc toward Cryo Stalker, nozzle glow, sizzle particles. |
| Enemy death (drone) | Kill drone | Hexagon spin+shrink, explosion circle, 6 sparks, coin drops, "+150" text. |
| Boss: Rust Colossus | 1-5 | 160×200 boss center-right, orange core pulse, smokestack puffs, player small firing, cracked ground, boss HP bar top-center. |
| Boss death | Defeat Colossus | Multi-explosion, screen shake 10px, white flash, slow-mo, coins raining, "STAGE CLEAR" stamp. |
| Stage complete | Any stage end | "STAGE CLEAR" large text, gold particles, score tally, blast door open, player at exit. |
| Game over | Lose all lives | Desaturated, heavy red vignette, "SYSTEM FAILURE" #FF4500, player dissolve, HUD grey. |
| World 2 contrast | Start 2-1 | Cyan floor glow, frost tiles, blue-white pools, Cryo Stalker, condensation pipes. |
| Low health | Damage to <30% | HP bar pulsing red, tightened vignette, heartbeat pulse, player white-flash. |
| Pause | P mid-stage | Dark overlay 80%, "PAUSED" center, resume/quit buttons, game frozen. |
| Core Warden boss | 2-5 | Tall crystalline boss, 4 orbiting shards cyan glow, frost overlay edges, player crouched firing, shards mid-flight. |

---

# 10. BUILD ORDER

| # | Milestone | Modules added | Proof check |
|---|---|---|---|
| **M1** | Page opens, draws title, `start()` enters play with blank ground + static player rect. | `game`, `input`, `renderer` (stub), `ui` (title) | **T1-01, T1-02** |
| **M2** | Player walks, jumps, crouches on hand-authored tile row. Camera follows. | `player`, `level` (static), `camera` | **T1-03–T1-11, T1-35, T1-43, T1-44** |
| **M3** | Pistol fires bullets; one enemy (crawler) walks and damages. Health, lives, death, respawn. | `weapons` (pistol), `enemies`, `progression` (lives/death) | **T1-12, T1-23–T1-28, T1-32, T1-33** |
| **M4** | All 4 guns (shotgun, coil, flare). Ammo, fire-rate, switching, charge, arc, reload, pierce, AoE. | `weapons` (full) | **T1-14–T1-22** |
| **M5** | Stage generator + verifier. 2 worlds × 5 stages. Tilemap fill, spawn points, flag, hazards. Stage-clear → next → next world. | `level` (generate+verify), `progression` (full) | **T1-36–T1-39, T1-50, T1-51** |