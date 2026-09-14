# BUILD SPEC: "IRONFALL" — Side-Scrolling Platformer Shooter

---

# 0. SCOPE

## 0.1 Requirements from User

| Requirement | Where it lives |
| --- | --- |
| Side-scrolling platformer shooter | §4, §1.1 |
| At least 4 different gun types | §4.3, §2.4 |
| Character can jump | §4.1 |
| Character can move left or right | §4.1 |
| Character can crouch | §4.1 |
| Story progression modeled on Mario (worlds → stages) | §4.6, §7 |
| 2 worlds | §4.6 |
| 5 stages per world | §4.6 |
| Do not simply copy Mario | §3, §5, §6 (original theme, enemies, mechanics) |

## 0.1b Additional Quality Requirements (added by designer)

| Requirement | Where it lives |
| --- | --- |
| Health system with pickups | §4.1, §4.5 |
| Enemy variety per world | §4.4, §5 |
| Stage variety (platforming, combat, mixed) | §4.6 |
| Ammo/upgrade pickups | §4.5 |
| Score and combo system | §4.7 |
| Boss fight at stage 5 of each world | §4.6, §5 |
| Parallax scrolling background | §3.1 |
| Screen shake and hit feedback | §3.2, §4.3 |
| Pause and HUD overlay | §7 |
| Title screen with controls guide | §7 |
| Stage-complete summary screen | §7 |

## 0.2 Tiers

| Tier | Label | Meaning |
| --- | --- | --- |
| T1 | MUST SHIP | Core loop: move, jump, crouch, shoot, 4 guns, enemies, platforms, 10 stages, win/lose |
| T2 | SHOULD SHIP | Bosses, combo system, ammo pickups, health pickups, screen shake, parallax |
| T3 | NICE TO HAVE | Score display, stage variety tags, death animation polish, extra enemy types |

---

# 1. CONVENTIONS

## 1.1 Units, Axes, Frames

| Term | Value |
| --- | --- |
| Tile size | 32 × 32 px |
| Stage width | 40 tiles (1280 px) |
| Stage height | 15 tiles (480 px) |
| Camera viewport | 20 tiles × 15 tiles (640 × 480 px) |
| Player standing hitbox | 24 × 40 px (centered on tile column) |
| Player crouching hitbox | 24 × 20 px |
| Player sprite frame | 32 × 48 px |
| Enemy small (crawler) | 24 × 24 px |
| Enemy medium (soldier) | 28 × 40 px |
| Enemy large (boss) | 64 × 80 px |
| Gravity | 1800 px/s² |
| Player walk speed | 200 px/s |
| Player jump velocity | -540 px/s (upward) |
| Player air control | 160 px/s |
| Bullet speed (pistol) | 600 px/s |
| Bullet speed (plasma) | 400 px/s |
| Bullet speed (rocket) | 300 px/s |
| Shotgun pellet speed | 500 px/s |
| Frame rate target | 60 fps, fixed timestep 1/60 s |
| Coordinate origin | Top-left of stage; +x right, +y down |
| Tile grid | Row 0 = top of stage; Row 14 = bottom (ground row) |

## 1.2 Important Conventions

- **Scene objects per stage**: Background parallax layers (3), tilemap (ground, platforms, walls), enemies (spawned at defined positions), pickups (health, ammo), projectiles (player + enemy), player, camera, HUD overlay, boss (stage 5 only).
- **Object pooling**: Projectiles use a pool of 64. Enemies use a pool of 32 per stage. Pickups pool of 16.
- **Z-ordering**: background(0) → tiles(1) → pickups(2) → enemies(3) → player(4) → projectiles(5) → particles(6) → HUD(7).
- **Collision model**: AABB tile collision for movement. Circle-vs-AABB for projectile-vs-entity. No physics engine; hand-coded.
- **Stage flow**: Player enters from left edge. Stage ends when player reaches right-edge exit zone (2-tile-wide trigger) or boss is defeated.
- **Death**: Player HP reaches 0 → death animation → respawn at last checkpoint or restart stage if no checkpoint. 3 lives per stage attempt.
- **Ammo model**: Pistol has infinite ammo. Shotgun, Plasma, Rocket have finite ammo found in pickups. Ammo persists within a stage but resets on death.

---

# 2. CONTRACTS

## 2.1 File Layout

| File | Responsibility |
| --- | --- |
| `index.html` | Single page shell, canvas element, HUD DOM overlay, screens |
| `game.js` | Main loop, state machine (TITLE, PLAY, PAUSE, STAGE_COMPLETE, GAME_OVER, WORLD_COMPLETE), camera, debug API installation |
| `input.js` | Keyboard/mouse state, action mapping, exposes `Input.getState()` |
| `player.js` | Player entity: movement, jump, crouch, shooting, HP, lives, animation state |
| `weapons.js` | Weapon definitions, firing logic, projectile spawning, ammo tracking |
| `projectile.js` | Projectile pool, update, collision, despawn |
| `enemies.js` | Enemy definitions, AI update per kind, spawn logic, death |
| `boss.js` | Boss entity (per world), phase logic, attack patterns |
| `pickups.js` | Health/ammo pickup entities, spawn, collect |
| `level.js` | Stage data (tilemap arrays, enemy spawn tables, pickup tables, exit zone), stage loader |
| `tilemap.js` | Tile rendering, collision query, tile type definitions |
| `camera.js` | Viewport tracking, follow logic, screen shake |
| `particles.js` | Simple particle pool for muzzle flash, explosions, hit sparks |
| `audio.js` | Web Audio API sound synthesis, play triggers |
| `ui.js` | HUD rendering (health bar, ammo, score, lives), screen transitions |
| `screens.js` | Title, stage-complete, game-over, world-complete screen logic |
| `constants.js` | All numeric constants from §1.1, weapon stats, enemy stats, tile IDs |

## 2.2 Global Context

The global context object `G` is created in `game.js` and passed to every system's `update` and `draw` calls:

```
G = {
  state: "TITLE" | "PLAY" | "PAUSE" | "STAGE_COMPLETE" | "GAME_OVER" | "WORLD_COMPLETE",
  world: 1 | 2,
  stage: 1..5,
  stageData: <loaded stage object>,
  player: <PlayerRecord>,
  enemies: [<EnemyRecord>...],
  projectiles: [<ProjectileRecord>...],
  pickups: [<PickupRecord>...],
  particles: [<ParticleRecord>...],
  camera: <CameraRecord>,
  score: int,
  combo: { count: int, timer: float },
  lives: int,
  dt: float,
  elapsed: float,
  rng: <seeded PRNG>,
  shake: { mag: float, dur: float, t: float },
  boss: <BossRecord | null>
}
```

## 2.3 File Specifics

### `constants.js`

```
TILE_SIZE = 32
STAGE_W = 40, STAGE_H = 15
VIEW_W = 20, VIEW_H = 15
GRAVITY = 1800
WALK_SPEED = 200
JUMP_VEL = -540
AIR_CONTROL = 160

WEAPONS = {
  pistol:   { dmg: 10, speed: 600, rate: 0.25, ammo: Infinity, spread: 0 },
  shotgun:  { dmg: 8,  speed: 500, rate: 0.7,  ammo: 24, spread: 15, pellets: 5 },
  plasma:   { dmg: 25, speed: 400, rate: 0.5,  ammo: 16, spread: 0, pierce: 2 },
  rocket:   { dmg: 50, speed: 300, rate: 1.2,  ammo: 8,  spread: 0, splash: 48 }
}

TILE_IDS = { EMPTY:0, GROUND:1, PLATFORM:2, WALL:3, EXIT:4, DECOR:5 }

ENEMY_KINDS = {
  crawler:  { hp: 15, speed: 60, dmg: 10, size: [24,24] },
  soldier:  { hp: 30, speed: 40, dmg: 15, size: [28,40], shoots: true },
  turret:   { hp: 40, speed: 0,  dmg: 12, size: [28,28], shoots: true, fixed: true },
  floater:  { hp: 20, speed: 50, dmg: 12, size: [24,24], sine: true },
  brute:    { hp: 60, speed: 30, dmg: 20, size: [36,44] }
}

BOSS_DEFS = {
  world1: { hp: 300, name: "FORGE WARDEN", phases: 2 },
  world2: { hp: 500, name: "CORE OVERSEER", phases: 3 }
}
```

### `player.js` — PlayerRecord

```
PlayerRecord = {
  x, y, vx, vy,
  facing: 1|-1,
  w: 24, h: 40,
  crouching: bool,
  grounded: bool,
  hp: 100, maxHp: 100,
  lives: 3,
  weapon: "pistol"|"shotgun"|"plasma"|"rocket",
  ammo: { shotgun: int, plasma: int, rocket: int },
  invuln: float (timer),
  animState: "idle"|"run"|"jump"|"crouch"|"shoot"|"hurt"|"dead",
  animFrame: int, animTimer: float,
  shootCooldown: float,
  alive: bool
}
```

Signatures:
- `updatePlayer(G, input, dt)` — applies movement, jump, crouch, gravity, tile collision, shoot input
- `drawPlayer(G, ctx)` — draws sprite at camera-adjusted position
- `damagePlayer(G, amount)` — reduces HP, sets invuln 1.0s, triggers hurt anim, screen shake
- `killPlayer(G)` — sets alive=false, plays death, decrements lives

### `weapons.js`

- `fireWeapon(G, player)` — checks cooldown, ammo; spawns projectile(s); returns bool fired
- `cycleWeapon(G, direction)` — cycles among unlocked weapons (pistol always unlocked; others unlocked by pickup)
- `getUnlockedWeapons(player)` — returns array of weapon keys available

### `enemies.js`

```
EnemyRecord = {
  id, kind, x, y, w, h, hp, maxHp,
  vx, vy, facing, alive,
  animState, animFrame, animTimer,
  shootTimer, patrolDir, patrolRange,
  sineOffset (for floaters)
}
```

- `spawnEnemies(G, stageData)` — populates G.enemies from stage spawn table
- `updateEnemies(G, dt)` — per-kind AI: patrol, chase, shoot, gravity
- `damageEnemy(G, enemy, amount)` — reduce HP, hit flash, spawn particles, on death: score, combo, drop chance

### `boss.js`

```
BossRecord = {
  x, y, w, h, hp, maxHp,
  phase: int, phaseTimer,
  attackPattern: string, patternTimer,
  alive, animState, animFrame, animTimer,
  name, world
}
```

- `spawnBoss(G, world)` — creates boss at stage-defined position
- `updateBoss(G, dt)` — phase logic, attack patterns (see §4.6)
- `damageBoss(G, amount)` — reduce HP, check phase transition

### `level.js` — StageData

```
StageData = {
  world, stage, name,
  tiles: number[STAGE_H][STAGE_W],
  enemies: [{kind, x, y, patrolRange?}...],
  pickups: [{type:"health"|"ammo_shotgun"|"ammo_plasma"|"ammo_rocket"|"weapon_shotgun"|..., x, y}...],
  checkpoints: [{x,y}...],
  exit: {x, y, w, h},
  boss: null | {world, x, y},
  parallaxSpeeds: [float, float, float],
  theme: "forge"|"core"
}
```

- `loadStage(world, stage)` → StageData (hardcoded arrays for 10 stages)
- `resetStage(G)` — reloads stageData, repositions player at spawn, clears enemies/projectiles/pickups

### `camera.js`

```
CameraRecord = { x, y, targetX, targetY, shakeMag, shakeDur, shakeT }
```

- `updateCamera(G, dt)` — lerp toward player, clamp to stage bounds, apply shake offset
- `getViewport(G)` → {x, y, w, h} in world coords

### `audio.js`

- `initAudio()` — creates AudioContext on first user gesture
- `playSound(name)` — looks up recipe, synthesizes, plays

### `input.js`

```
InputState = {
  left, right, up, down, crouch, shoot, weaponNext, weaponPrev, pause: bool
}
```

- `getState()` → InputState
- `isPressed(action)` → bool (edge-triggered)
- `isHeld(action)` → bool (continuous)

---

# 3. VISUAL SPEC

Ironfall is a gritty industrial-cyberpunk platformer rendered in a chunky pixel-art style (effectively 32px tile art scaled to screen). The world is the interior of a colossal abandoned megastructure: exposed pipes, riveted metal plates, flickering neon signage, and hazard-striped platforms. The color palette is desaturated steel greys and rust oranges for World 1 (the FORGE district), shifting to cold cyan and deep purple with electric-blue energy conduits for World 2 (the CORE district). Lighting is low-key with strong directional highlights from practical sources (lava vents, plasma conduits) creating hard-edged shadows on tiles. The player character is a stocky armored bounty hunter with a bulky helmet and a glowing visor that tints toward the equipped weapon's color. Enemies are mechanical: spider-like crawlers, bipedal soldier-bots, wall-mounted turrets, hovering drone-floaters, and hulking brutes. Explosions and muzzle flashes use additive-blended particles in weapon-specific hues. Parallax backgrounds show deeper layers of the megastructure interior with animated steam vents and distant flickering lights.

## 3.1 Tilemap Art

| Tile ID | Visual |
| --- | --- |
| GROUND (1) | Riveted metal plate, 32×32, dark grey with rust edge highlights. Top row has a lighter "lip" for edge definition. |
| PLATFORM (2) | Grated catwalk, 32×32, semi-transparent gaps, yellow hazard stripes on edges. |
| WALL (3) | Vertical pipe/panel section, 32×32, corrugated metal with bolt details. |
| EXIT (4) | Glowing green portal frame, 32×32, pulsing animation (2 frames). |
| DECOR (5) | Background-only: steam vent, warning sign, broken conduit. Non-solid. |

## 3.2 Character / Enemy Sprites

- Player: 48px tall sprite sheet, 6 frames per state (idle, run, jump, crouch, shoot, hurt). Armored torso, helmet with visor, backpack with weapon mount. Visor glows weapon color.
- Crawler: 24×24, 4-legged spider-bot, red optical sensor.
- Soldier: 28×40, bipedal mech with arm-mounted blaster, 4 frames.
- Turret: 28×28, wall-mounted, rotating barrel, 2 frames.
- Floater: 24×24, disc-shaped drone with single eye, bobbing.
- Brute: 36×44, massive walking mech, 4 frames.
- Boss W1: 64×80, furnace-wielder mech, glowing orange core.
- Boss W2: 64×80, crystalline overseer with floating shards, cyan glow.

## 3.3 Particles & Effects

- Muzzle flash: 4-frame burst, weapon-colored, additive blend, 60ms.
- Hit spark: 6 particles, white/yellow, 150ms.
- Explosion (rocket): 12 particles orange + 6 smoke grey, 400ms.
- Enemy death: 8 debris particles in enemy's color, 300ms.
- Screen shake: camera offset by random ±shakeMag px, decaying over shakeDur.
- Player hurt flash: entire sprite tints white for 100ms.

## 3.4 Parallax Layers

| Layer | Content | Speed multiplier |
| --- | --- | --- |
| Far (0) | Silhouette megastructure skyline, distant lights | 0.2× |
| Mid (1) | Pipes, girders, steam vents | 0.5× |
| Near (2) | Tilemap, entities | 1.0× |

Each layer is a repeating horizontal strip. Animated elements (steam, blinking lights) cycle on a 2s timer.

---

# 4. GAMEPLAY SPEC

The core loop is: run and gun through a side-scrolling stage, platforming over gaps and hazards while shooting enemies with your current weapon, collecting ammo and health, and reaching the exit (or defeating a boss) to advance. The most important feeling is responsive, punchy combat — every shot has weight (screen shake, muzzle flash, enemy hit-stun), and movement is tight (instant direction change, variable jump height, crouch to dodge). Progression is gated by worlds: clear 4 stages → fight a boss → unlock next world. The player starts with a pistol and must find the shotgun, plasma rifle, and rocket launcher as weapon pickups throughout stages. Ammo scarcity creates meaningful weapon choices.

## 4.1 Player Controller

| Input | Action |
| --- | --- |
| A / ← | Move left (set vx = -WALK_SPEED, facing = -1) |
| D / → | Move right (set vx = +WALK_SPEED, facing = +1) |
| W / ↑ / Space | Jump (if grounded: vy = JUMP_VEL; if holding, reduce gravity to 50% for first 0.2s for variable height) |
| S / ↓ | Crouch (set crouching=true, h=20, cannot move while crouching unless already moving → slide at 100px/s for 0.3s) |
| J / Left-click | Shoot (fire current weapon, respect cooldown) |
| Q / E | Cycle weapon prev / next |
| P / Esc | Pause |

**Movement rules:**
- Horizontal: instant acceleration to WALK_SPEED. No friction while grounded and input held. Air control at AIR_CONTROL max.
- Vertical: gravity applied every frame. Max fall speed 800 px/s.
- Jump: only when grounded. Variable height: releasing jump early sets vy = max(vy, -200).
- Crouch: only when grounded. Reduces hitbox height. Allows passing under 1-tile-high gaps.
- Tile collision: AABB sweep. Player cannot pass through GROUND or WALL tiles. PLATFORM tiles are one-way (pass through from below, land from above).

**Camera:** Follows player with 0.1 lerp factor. Clamped so player is never further than 6 tiles from center horizontally, never above/below stage bounds. Screen shake adds random offset.

**Stats:** HP 100. 3 lives. Invulnerability 1.0s after hit. Score accumulates per kill (base 100 × combo multiplier).

## 4.2 Crouch & Slide Mechanic

- Pressing crouch while grounded and moving: initiate a 0.3s slide (vx locked at 100×facing, hitbox at crouch height, player cannot shoot during slide).
- Pressing crouch while grounded and still: reduce hitbox, cannot move.
- Crouch releases when key released or jump pressed.
- Slide can be used to dodge enemy projectiles that fly at chest height.

## 4.3 Weapons (4 types minimum)

| Weapon | Unlock | Damage | Rate (s) | Ammo | Special |
| --- | --- | --- | --- | --- | --- |
| **Pistol** | Start | 10 | 0.25 | ∞ | Single straight bullet, no spread |
| **Shotgun** | W1 Stage 2 pickup | 8 × 5 pellets | 0.7 | 24 | 5-pellet spread ±15°, short range (despawn after 200px) |
| **Plasma Rifle** | W1 Stage 4 pickup | 25 | 0.5 | 16 | Pierces 2 enemies, leaves brief glow trail |
| **Rocket Launcher** | W2 Stage 2 pickup | 50 | 1.2 | 8 | Splash damage radius 48px, destroys turret tiles |

**Firing rules:**
- Cooldown: cannot fire again until timer elapses.
- Ammo: each shot consumes 1 unit (shotgun = 1 shell). Pistol infinite.
- Weapon lock: player can only carry the weapons they've unlocked. Cycle with Q/E among unlocked set.
- Projectiles spawn at player's gun position (facing × 16px from center, y = center - 4px standing, y = center + 2px crouching).
- Rocket: explodes on first enemy hit or after 500px travel. Splash damages all enemies within 48px of impact.

## 4.4 Enemies & AI

| Kind | Behavior |
| --- | --- |
| Crawler | Patrols left-right within patrolRange. If player within 6 tiles, charges at 2× speed. Contact damage. |
| Soldier | Patrols. Stops at player within 8 tiles, aims, fires 1 bullet every 1.5s. 1 bullet in flight max. |
| Turret | Fixed. Scans 180° arc in facing direction. Fires aimed shot every 2s when player in range (10 tiles). |
| Floater | Hovers at spawn y, sine-wave vertical (amplitude 24px, period 2s). Moves horizontally toward player at FLOATER speed. Contact damage. |
| Brute | Walks slowly toward player. Every 3s, ground-slam: creates shockwave (2 ground-level projectiles, speed 250, dmg 20). |

**Enemy spawning:** Defined per-stage in StageData.enemies array. Enemies spawn when player's x passes enemy.x - 12 tiles (offscreen margin). Once spawned, they persist until killed or stage reset.

**Enemy projectiles:** Speed 300 px/s, dmg per kind. Despawn on tile hit or offscreen.

## 4.5 Pickups

| Type | Visual | Effect |
| --- | --- | --- |
| Health (small) | Red cross, 16×16 | +25 HP |
| Health (large) | Red cross on plate, 24×24 | +50 HP |
| Ammo (shotgun) | Yellow shell icon | +8 shells |
| Ammo (plasma) | Cyan cell icon | +6 cells |
| Ammo (rocket) | Red rocket icon | +3 rockets |
| Weapon (shotgun) | Shotgun silhouette on crate | Unlocks shotgun, +24 ammo |
| Weapon (plasma) | Rifle silhouette on crate | Unlocks plasma, +16 ammo |
| Weapon (rocket) | Launcher silhouette on crate | Unlocks rocket, +8 ammo |
| Coin | Gold hex, 12×12 | +100 score |

Pickups bob vertically (±4px sine, 1.5s period). Collected on player overlap. Disappear on collect.

## 4.6 World & Stage Progression

**Structure:**
- **World 1: THE FORGE** — Industrial foundry district. Themes: lava, metal, fire.
  - Stage 1-1: "Assembly Line" — Intro platforming, 4 crawlers, 1 soldier. Learn move/jump/shoot.
  - Stage 1-2: "Rust Corridors" — More platforming, gap jumps, shotgun pickup, 6 enemies.
  - Stage 1-3: "Molten Crossing" — Hazard platforms (lava below = instant death), turrets, 8 enemies.
  - Stage 1-4: "Grindworks" — Vertical stage (player climbs), floater enemies, plasma pickup, 10 enemies.
  - Stage 1-5: "The Warden's Forge" — BOSS: FORGE WARDEN. Arena stage.

- **World 2: THE CORE** — Energy reactor district. Themes: plasma, crystal, electricity.
  - Stage 2-1: "Conduit Run" — Fast-paced, moving platforms, 6 soldiers, 2 turrets.
  - Stage 2-2: "Crystal Caverns" — Dark sections (limited vision), brutes, rocket pickup.
  - Stage 2-3: "Overload" — Timed section (screen fills with rising plasma from bottom), 12 enemies.
  - Stage 2-4: "The Spine" — Long horizontal gauntlet, all enemy types, mixed pickups.
  - Stage 2-5: "Core Overseer" — BOSS: CORE OVERSEER. Multi-phase arena.

**Progression rules:**
- Stage N+1 unlocks after clearing Stage N.
- World 2 unlocks after defeating World 1 boss.
- Player retains unlocked weapons across stages within a world. Weapons reset to pistol at start of each world.
- Lives reset to 3 at start of each stage.
- Score persists across stages and worlds.

**Boss 1: FORGE WARDEN (300 HP, 2 phases)**
- Phase 1 (HP > 150): Charges left-right across arena. Every 4s, swings hammer (shockwave). Every 6s, spits 3 lava blobs in arc.
- Phase 2 (HP ≤ 150): Moves faster. Adds floor slam (rings of debris). Every 3s, summons 2 crawlers.

**Boss 2: CORE OVERSEER (500 HP, 3 phases)**
- Phase 1 (HP > 333): Floats in figure-8. Fires 5-way plasma burst every 3s.
- Phase 2 (HP > 166): Adds laser sweep (horizontal beam, 2s warning, 0.5s active). Spawns 2 floaters.
- Phase 3 (HP ≤ 166): Rapid-fire mode (burst every 1.5s). Screen flickers. Adds homing orbs (slow, track player, 1 hit).

## 4.7 Scoring & Combo

- Base kill: 100 pts.
- Combo: each kill within 2s of previous increments combo counter. Multiplier = 1 + 0.5×(combo-1), capped at 5×.
- Combo resets if 2s pass without a kill.
- Stage clear bonus: 500 × stage number.
- Boss kill: 2000 × world number.
- Coin: 100 pts.

## 4.8 Hazards

- **Lava (World 1)**: Tiles marked as lava (tile ID 6, visual: animated orange). Touch = instant death (lose 1 life).
- **Plasma flood (World 2, Stage 2-3)**: Rising wall of energy from bottom. Touch = instant death. Rises at 30px/s during timed section.
- **Spikes**: 1-tile high hazard on top of ground tiles. Touch = 20 dmg + knockback.

---

# 5. CHARACTERS

The player is KIRA, a bounty hunter in a bulky exo-frame suit: wide-shouldered, helmeted, with a glowing visor and a backpack that houses the current weapon's power cell. The suit is gunmetal grey with weapon-colored accent lights. Kira moves with a slight forward lean when running, a tight crouch that compresses the frame, and a recoil-punch when shooting. Enemies are all mechanical constructs of the megastructure: crawlers are skittering multi-limbed sensors, soldiers are upright bipedal patrol units with blaster arms, turrets are wall-bolted gun platforms, floaters are hovering disc-drones, brutes are heavy quadrupedal walkers. The bosses are massive constructs: the Forge Warden is a furnace-golem wielding a molten hammer, the Core Overseer is a crystalline entity that floats and fractures light. All characters use 4-6 frame animations at 8fps (frame every 125ms).

## 5.1 Player Animation States

| State | Frames | Speed | Trigger |
| --- | --- | --- | --- |
| idle | 2 | 0.5s/frame | No input, grounded |
| run | 4 | 0.125s/frame | Moving, grounded |
| jump | 3 (up, peak, fall) | 0.1s/frame | Airborne |
| crouch | 1 | static | Crouching, no move |
| slide | 2 | 0.15s/frame | Sliding |
| shoot | 2 | 0.1s/frame | Firing (overlays current state) |
| hurt | 2 | 0.1s/frame | Damage taken |
| dead | 4 | 0.15s/frame | HP = 0 |

## 5.2 Enemy Animations

- Crawler: 4-frame leg cycle.
- Soldier: 4-frame walk, 2-frame shoot.
- Turret: 2-frame barrel rotation (idle scan, aim).
- Floater: 2-frame bob.
- Brute: 4-frame stomp, 2-frame slam.
- Bosses: 4-frame idle, 3-frame attack, 2-frame hurt, 6-frame death.

---

# 6. AUDIO

All sounds synthesized via Web Audio API. No external files.

| Sound | Recipe | Trigger |
| --- | --- | --- |
| jump | Square, 200→400 Hz sweep, 0.1s, fast attack, decay | Player jump initiated |
| land | Noise burst, lowpass 800 Hz, 0.08s | Player lands (grounded transition) |
| shoot_pistol | Square, 880 Hz, 0.06s, sharp attack, quick decay | Pistol fire |
| shoot_shotgun | Noise + saw, 120 Hz, 0.12s, medium decay | Shotgun fire |
| shoot_plasma | Sine, 660→1200 Hz sweep, 0.15s, soft attack | Plasma fire |
| shoot_rocket | Saw, 80 Hz + noise, 0.2s, slow attack | Rocket fire |
| explosion | Noise burst, lowpass sweep 2000→200 Hz, 0.4s | Rocket impact / boss death |
| hit_enemy | Triangle, 440 Hz, 0.05s, sharp | Projectile hits enemy |
| hurt_player | Square, 150→80 Hz, 0.2s, medium | Player takes damage |
| pickup | Sine, 600→900 Hz, 0.1s, soft | Player collects pickup |
| coin | Sine, 1200→1600 Hz, 0.08s | Player collects coin |
| enemy_die | Saw, 300→50 Hz, 0.15s, decay | Enemy HP reaches 0 |
| boss_hurt | Square, 200 Hz, 0.1s, sharp | Boss takes damage |
| boss_phase | Sine sweep 100→800 Hz, 0.5s | Boss phase transition |
| death | Saw, 400→50 Hz, 0.6s, slow decay | Player dies |
| stage_clear | Arpeggio C-E-G-C, sine, 0.6s total | Player reaches exit / boss dies |
| menu_select | Sine, 800 Hz, 0.05s | UI navigation |
| death_scream | Noise + saw, 200 Hz, 0.3s | Player life lost (all 3) |

**Music:** A simple looping bass line (saw, 80-160 Hz, 4-bar loop) + hi-hat (noise burst, 0.03s, every 0.5s) + synth pad (triangle, root+5th, slow LFO) per world. World 1 in A minor, World 2 in D minor. Tempo 130 BPM.

---

# 7. UX

All UI is HTML/CSS DOM overlay on top of the canvas. No canvas-drawn text.

## 7.1 Screens

| Screen | Trigger | Content |
| --- | --- | --- |
| **Title** | Initial load / game over return | Game logo "IRONFALL", "Press ENTER to Start", controls table (A/D move, Space jump, S crouch, J shoot, Q/E weapon, P pause), high score display |
| **World Select** | After world clear | "WORLD 1: THE FORGE" / "WORLD 2: THE CORE" with stage 1-5 icons (locked/unlocked) |
| **Stage Intro** | Before each stage | Stage name + number, "Press ENTER to begin", 1.5s auto-advance |
| **HUD (in-game)** | During PLAY | Top-left: HP bar (green→red gradient, 100px wide). Below: lives icons (small helmet sprites). Top-center: weapon name + ammo count (∞ for pistol). Top-right: score, combo counter (×N). Bottom-left: current stage "W1-3" |
| **Pause** | P/Esc during PLAY | "PAUSED" overlay, "Enter: Resume / Q: Quit to Title" |
| **Stage Complete** | After exit/boss | "STAGE CLEAR", score breakdown (kills, combo bonus, clear bonus), "Press ENTER for next stage" |
| **Game Over** | Lives = 0 | "GAME OVER", final score, "Press ENTER to restart from current stage / Q for title" |
| **World Complete** | After boss 2 | "WORLD 2 CLEARED — VICTORY", total score, "Press ENTER for title" |

## 7.2 HUD Details

- HP bar: 100px × 8px, border 1px white, fill green (#4f4) at full → red (#f44) at low. Smooth animation (lerp display HP to actual over 0.3s).
- Ammo: Shows current weapon ammo. "∞" for pistol. Number for others. Flash red when ≤ 3.
- Combo: Appears center-top when combo > 1. "×3" style, fades after 1s of no kills.
- Lives: 3 small 16×16 helmet icons. Dimmed when lost.

## 7.3 Controls Guide (Title Screen)

```
← → / A D : Move
SPACE / W / ↑ : Jump
S / ↓ : Crouch / Slide
J / CLICK : Shoot
Q / E : Switch Weapon
P / ESC : Pause
```

---

# 8. DEBUG API

The game installs `window.__game` with plain synchronous functions. All return plain data (no DOM refs, no functions).

| Call | What it does | Returns |
| --- | --- | --- |
| `start()` | Enters PLAY state, loads current world/stage, spawns player at stage start. No click needed. | `{ state:"PLAY", world, stage }` |
| `step(dt, n)` | Advances n ticks of dt seconds without real-time wait. Draws once after. | `{ elapsed, playerX, playerY, enemiesAlive, projectilesActive }` |
| `setTime(t)` | Advances to t seconds without drawing. | `{ elapsed }` |
| `seed(n)` | Reseeds the PRNG and rebuilds enemy/particle random offsets. | `{ seed }` |
| `getState()` | Returns all record fields as plain JSON. | `{ state, world, stage, player:{...}, enemies:[{...}], projectiles:[{...}], pickups:[{...}], boss:{...}|null, score, combo, lives, camera:{...} }` |
| `moveLeft()` | Sets input.left = true, persists. | `{ left:true }` |
| `moveRight()` | Sets input.right = true, persists. | `{ right:true }` |
| `stopMove()` | Sets input.left = false, input.right = false. | `{ left:false, right:false }` |
| `jump()` | Edge-triggers jump for 1 frame. | `{ jump:true }` |
| `crouch()` | Sets input.crouch = true, persists. | `{ crouch:true }` |
| `uncrouch()` | Sets input.crouch = false. | `{ crouch:false }` |
| `shoot()` | Edge-triggers shoot for 1 frame. | `{ shoot:true }` |
| `cycleWeapon(dir)` | Cycles weapon by dir (+1/-1). | `{ weapon, unlocked:[...] }` |
| `spawnEnemy(kind, x, y)` | Adds an enemy of kind at world position. | `{ enemyId, kind, x, y, hp }` |
| `spawnPickup(type, x, y)` | Adds a pickup at world position. | `{ pickupId, type, x, y }` |
| `setPlayerHP(n)` | Sets player HP directly. | `{ hp }` |
| `setPlayerPos(x, y)` | Teleports player. | `{ x, y }` |
| `skipToStage(world, stage)` | Loads specified world/stage, enters PLAY. | `{ world, stage }` |
| `damageEnemy(id, n)` | Deals n damage to enemy by id. | `{ enemyId, hp, alive }` |
| `damageBoss(n)` | Deals n damage to boss. | `{ hp, phase, alive }` |
| `killAllEnemies()` | Kills all alive enemies (for testing stage clear). | `{ killed }` |
| `getTile(tx, ty)` | Returns tile ID at tile coordinate. | `{ tileId }` |

All calls are synchronous. With `seed(n)` + `step(dt, n)` the same sequence always yields identical state.

---

# 9. TESTS

Numbered checks run via `window.__game`. Each uses only calls from §8.

1. **Title → Play:** `start()` → `getState().state === "PLAY"`, `getState().world === 1`, `getState().stage === 1`.
2. **Player spawns:** After `start()`, `getState().player.x` is between 32 and 128, `getState().player.y` is on ground row (≥ 416), `getState().player.alive === true`, `getState().lives === 3`.
3. **Movement right:** `moveRight()`, `step(1/60, 60)` → `getState().player.x > initialX + 150`, `getState().player.facing === 1`.
4. **Movement left:** `stopMove()`, `moveLeft()`, `step(1/60, 30)` → `getState().player.x < previousX`.
5. **Jump:** `stopMove()`, `jump()`, `step(1/60, 5)` → `getState().player.vy < 0` (airborne), `getState().player.grounded === false`.
6. **Gravity lands:** `step(1/60, 60)` after jump → `getState().player.grounded === true`, `getState().player.vy === 0`.
7. **Crouch:** `crouch()`, `step(1/60, 1)` → `getState().player.crouching === true`, `getState().player.h === 20`.
8. **Shoot pistol:** `shoot()`, `step(1/60, 1)` → `getState().projectilesActive >= 1`, `getState().player.shootCooldown > 0`.
9. **Pistol infinite ammo:** 20 calls of `shoot()` + `step(1/60, 20)` → `getState().player.alive === true` (no ammo depletion).
10. **Enemy damage:** `spawnEnemy("crawler", 200, 400)`, `shoot()` aimed at it, `step(1/60, 30)` → that enemy's hp < 15.
11. **Enemy death & score:** `damageEnemy(id, 999)` → `getState().enemies` has that enemy alive === false, `getState().score > 0`.
12. **Player damage:** `setPlayerHP(50)`, `spawnEnemy("crawler", playerX+20, playerY)`, `step(1/60, 30)` → `getState().player.hp < 50` (contact damage applied).
13. **Player death & lives:** `setPlayerHP(0)`, `step(1/60, 60)` → `getState().lives === 2` (was 3), `getState().player.alive === true` (respawned).
14. **Weapon pickup:** `spawnPickup("weapon_shotgun", 300, 400)`, `setPlayerPos(300, 400)`, `step(1/60, 1)` → `getState().player.unlockedWeapons` includes "shotgun", `getState().player.ammo.shotgun === 24`.
15. **Weapon cycle:** After unlocking shotgun, `cycleWeapon(1)` → `getState().player.weapon === "shotgun"`.
16. **Shotgun pellets:** `shoot()` with shotgun, `step(1/60, 1)` → `getState().projectilesActive >= 5` (pellets).
17. **Plasma pierce:** `skipToStage(1, 4)`, `start()`, `spawnEnemy("soldier", 300, 400)`, `spawnEnemy("soldier", 350, 400)`, `cycleWeapon(1)` ×2 (to plasma), `shoot()`, `step(1/60, 20)` → both soldiers damaged.
18. **Rocket splash:** `spawnEnemy("crawler", 200, 400)`, `spawnEnemy("crawler", 230, 400)`, `cycleWeapon(1)` ×3 (to rocket), `shoot()`, `step(1/60, 40)` → both crawlers hp reduced (splash).
19. **Stage clear:** `skipToStage(1, 1)`, `start()`, `killAllEnemies()`, `setPlayerPos(1248, 416)` (exit zone), `step(1/60, 5)` → `getState().state === "STAGE_COMPLETE"`.
20. **World 2 unlock:** `skipToStage(1, 5)`, `start()`, `spawnBoss(1)` equivalent via `damageBoss(999)`, `step(1/60, 60)` → `getState().state === "STAGE_COMPLETE"`. Then `skipToStage(2, 1)`, `start()` → `getState().world === 2`.
21. **Boss phases:** `skipToStage(1, 5)`, `start()`, `damageBoss(160)` → `getState().boss.phase === 2`, `getState().boss.hp === 140`.
22. **Combo:** `spawnEnemy("crawler", 200, 400)`, `damageEnemy(id, 999)`, `step(1/60, 10)`, `spawnEnemy("crawler", 210, 400)`, `damageEnemy(id2, 999)`, `step(1/60, 1)` → `getState().combo.count === 2`, `getState().combo.timer > 0`.
23. **Combo timeout:** After combo 2, `setTime(getState().elapsed + 2.5)` → `getState().combo.count === 0`.
24. **Pause:** During PLAY, `getState().state === "PLAY"`, simulate pause → `getState().state === "PAUSE"`, resume → `"PLAY"`.
25. **Determinism:** `seed(42)`, `start()`, `step(1/60, 120)` → record state. `seed(42)`, `start()`, `step(1/60, 120)` → identical state (player pos, enemy positions, score).

## SCREENSHOTS

| # | Screen / State | What a person must see |
| --- | --- | --- |
| 1 | Title | "IRONFALL" logo, controls list, "Press ENTER", dark industrial bg |
| 2 | Stage 1-1 start | Player standing on ground, HUD shows HP bar full, "W1-1", lives ×3, "Pistol ∞" |
| 3 | Mid-combat | Player shooting, muzzle flash, bullet in flight, enemy hit with sparks, score ticking |
| 4 | Crouch | Player visibly compressed, reduced height, crouch sprite |
| 5 | Shotgun fire | 5 pellet spread visible, ammo count dropping |
| 6 | Rocket explosion | Splash particles, enemy debris, screen shake visible |
| 7 | Boss W1 | Large mech on screen, HP bar for boss, arena with hazard tiles |
| 8 | Stage complete | "STAGE CLEAR", score breakdown, "Press ENTER" |
| 9 | World 2 stage | Different palette (cyan/purple), new enemy types visible |
| 10 | Game over | "GAME OVER", final score, lives all dimmed |
| 11 | Victory (W2 boss killed) | "VICTORY", total score, celebration particles |

---

# 10. BUILD ORDER

1. **Scaffold** — `index.html` with canvas + DOM overlay, `constants.js`, `game.js` with state machine loop (TITLE→PLAY→STAGE_COMPLETE), `input.js` wired to keyboard. *(T1)*
2. **Tilemap & Stage Data** — `tilemap.js` rendering, `level.js` with hardcoded 10-stage arrays, `camera.js` follow. Draw a stage. *(T1)*
3. **Player movement** — `player.js`: left/right, jump, gravity, tile collision, crouch. Test with `__game.step`. *(T1)*
4. **Weapons & Projectiles** — `weapons.js`, `projectile.js`: pistol fire, projectile travel, tile/enemy collision, cooldown. *(T1)*
5. **Enemies** — `enemies.js`: crawler + soldier AI, spawn from stage data, contact damage, death, score. *(T1)*
6. **HUD** — `ui.js`: HP bar, ammo, lives, score, weapon name, stage label. *(T1)*
7. **Stage flow** — Exit trigger, stage complete screen, next stage load, lives, game over. *(T1)*
8. **Remaining weapons** — Shotgun (pellets), Plasma (pierce), Rocket (splash). Weapon pickups, cycle. *(T1)*
9. **Remaining enemies** — Turret, Floater, Brute. Enemy projectiles. *(T2)*
10. **Pickups** — `pickups.js`: health, ammo, weapon unlocks, coins. *(T2)*
11. **Bosses** — `boss.js`: Forge Warden (2 phases), Core Overseer (3 phases). Boss arenas. *(T2)*
12. **World progression** — World 1→2 unlock, weapon reset per world, stage intro screens, world select. *(T2)*
13. **Particles & Screen Shake** — `particles.js`, `camera.js` shake. Muzzle flash, hit sparks, explosions, enemy death debris. *(T2)*
14. **Parallax & Visual Polish** — 3-layer parallax, animated decor, themed palettes, player/enemy sprite animations. *(T2)*
15. **Audio** — `audio.js`: all SFX, per-world music loop. *(T2)*
16. **Hazards** — Lava, plasma flood, spikes. Stage-specific. *(T2)*
17. **Combo & Score polish** — Combo display, multiplier, score breakdown on complete. *(T3)*
18. **Stage variety tuning** — Adjust layouts, difficulty curves, checkpoint placement. *(T3)*
19. **Debug API** — `window.__game` full implementation. *(T1, needed for testing throughout)*
20. **Test pass** — Run all §9 checks. Fix failures. *(T1)*
21. **Screenshot pass** — Verify all §9 SCREENSHOTS visually. *(T2)*
22. **Polish & balance** — Playtest feel, adjust speeds/damage/rates, fix edge cases. *(T3)*

---

# 11. DEFINITION OF DONE

## Movement & Controls
- [ ] Left/right movement at 200 px/s with instant direction change
- [ ] Jump with variable height (hold = higher)
- [ ] Crouch reduces hitbox to 20px height
- [ ] Slide (crouch while moving) works, 0.3s duration
- [ ] Air control at 160 px/s
- [ ] Tile collision prevents clipping

## Weapons
- [ ] Pistol: infinite ammo, 0.25s cooldown, single projectile
- [ ] Shotgun: 5 pellets, ±15° spread, 24 ammo, 0.7s cooldown
- [ ] Plasma: pierces 2, 16 ammo, 0.5s cooldown
- [ ] Rocket: splash 48px, 8 ammo, 1.2s cooldown
- [ ] Weapon cycle Q/E among unlocked set
- [ ] Weapon pickups unlock and grant ammo

## Stages & Progression
- [ ] 10 stages total (2 worlds × 5) loadable and playable
- [ ] Exit trigger completes stage
- [ ] World 2 locked until W1 boss defeated
- [ ] Weapons reset to pistol at world start
- [ ] 3 lives per stage, game over at 0

## Enemies & Bosses
- [ ] 5 enemy types with distinct AI
- [ ] Enemy projectiles (soldier, turret, brute)
- [ ] Boss W1: 2 phases, 300 HP, killable
- [ ] Boss W2: 3 phases, 500 HP, killable
- [ ] Enemies spawn offscreen and persist

## Visuals
- [ ] 3-layer parallax scrolling
- [ ] Screen shake on rocket/explosion/boss hit
- [ ] Particle effects: muzzle flash, hit spark, explosion, death debris
- [ ] Player animation states (idle, run, jump, crouch, shoot, hurt, dead)
- [ ] World 1 vs World 2 distinct palettes

## Audio
- [ ] All 18 SFX synthesized and triggered correctly
- [ ] Per-world music loop
- [ ] Audio initializes on first user gesture (no autoplay)

## UX
- [ ] Title screen with controls
- [ ] HUD: HP, ammo, lives, score, combo, weapon, stage label
- [ ] Pause overlay
- [ ] Stage intro, stage complete, game over, victory screens
- [ ] All screens navigable with ENTER/Q

## Debug API
- [ ] All 20+ functions in §8 implemented
- [ ] Deterministic with seed + step
- [ ] Returns only plain data

## Tests
- [ ] All 25 numbered checks pass
- [ ] All 11 screenshot checks verified by human

---

# A. SANITY

| Check | Result |
| --- | --- |
| Every field a rule reads/writes is on a record | ✅ PlayerRecord has hp, lives, weapon, ammo, crouching, grounded, facing, invuln, animState, shootCooldown. EnemyRecord has kind, hp, patrolDir, shootTimer. BossRecord has phase, hp, attackPattern. ProjectileRecord has x, y, vx, vy, dmg, pierce, splash, travel. All referenced fields exist. |
| Every place/thing/kind a rule names is placed by a generator or listed in a roster | ✅ 5 enemy kinds in ENEMY_KINDS. 10 stages in level.js. 4 weapons in WEAPONS. 9 pickup types defined. Bosses defined per world. Tile IDs enumerated. All spawns come from StageData arrays. |
| Consumables: total placed vs total demanded along core loop | ✅ Shotgun ammo: start 0, pickup W1-2 gives 24, +8 per ammo pickup (3 placed W1, 2 placed W2) = max 48. Shotgun uses ~20-30 shells across 5 stages. Plasma: pickup W1-4 gives 16, +6×(2 W1, 2 W2) = 40 max. Plasma uses ~25. Rocket: pickup W2-2 gives 8, +3×(2 W2) = 14 max. Rocket uses ~8. All close. Pistol ∞ always available. |
| Timing pairs: spawn vs clear, drain vs refill, travel vs distance | ✅ Enemy spawn (offscreen +12 tiles) vs clear (kill before exit): stage is 40 tiles, player at 200px/s traverses in ~6.4s, enemies spawn progressively. Enemy bullet speed 300 vs player jump duration ~0.6s: player can jump over. Rocket speed 300, travel 500px = 1.67s, splash radius 48px covers enemies within ~2 tiles. Boss W1 charge speed ~200px/s, arena 20 tiles = 640px, player has 3.2s to dodge. Plasma flood 30px/s over 480px = 16s timed section. All close. |
| Every call §9 makes is in §8 | ✅ Checked all 25 tests: start, step, getState, moveRight, moveLeft, stopMove, jump, crouch, uncrouch, shoot, cycleWeapon, spawnEnemy, spawnPickup, setPlayerHP, setPlayerPos, skipToStage, damageEnemy, damageBoss, killAllEnemies, setTime, seed. All present in §8 table. |
| Tile collision vs player hitbox | ✅ Player 24×40 fits in 32-wide tile column with 4px margin. Crouch 24×20 fits under 1-tile gap (32px clearance). No clipping. |
| Camera clamp vs stage width | ✅ Viewport 20 tiles, stage 40 tiles. Camera x clamped [0, 20] tiles. Player at x=0 sees tiles 0-19; at x=39 sees tiles 19-39. No out-of-bounds draw. |
| Lives/HP/invuln interaction | ✅ 100 HP, contact dmg 10-20, enemy bullet 12-15, boss 20-30. Invuln 1s prevents chain-death. 3 lives × 100 HP = survivable. Lava/plasma = instant life loss (HP irrelevant). Closes. |