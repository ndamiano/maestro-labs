| Idle | 2 frames: barrel drifts ±5°, eye blinks | 2.0 s |
| Aim | Continuous rotation toward player angle | While chasing |
| Fire | 1 frame: barrel recoil kick 2 px back | 0.1 s |
| Hurt | 1 frame: white flash on barrel | 0.1 s |
| Death | Barrel droops, sparks ×4, body sinks 4 px, fades | 0.5 s |

## Proximity Mine [T2]

**Silhouette:** Flat octagonal disc on the ground, 4 blinking dots around the rim. At a glance: "a hockey puck that hates you."

**Facings:** None (symmetric).

| Animation | Frames | Loop |
|---|---|---|
| Dormant | 1 pose: dots blink slowly (0.8 s) | Continuous |
| Armed (player near) | 4 frames: dots blink fast (0.1 s), body pulses scale 1.0→1.1 | 0.2 s loop |
| Fuse (0.6 s) | Body flashes #FF2D78 each tick | 0.1 s per flash |
| Detonate | Expanding ring r=0→70 px, 8 spark lines, smoke ×6 | 0.3 s |

## Shieldbot [T2]

**Silhouette:** Bulky rectangular torso with a large front-mounted energy shield plate. Glowing eye slit. At a glance: "a riot cop made of scrap metal."

**Facings:** Left, Right (shield always faces movement direction toward player).

| Animation | Frames | Loop |
|---|---|---|
| Shuffle walk | 4 frames: alternating leg step, body sway y ±2 | 0.6 s |
| Shield block (frontal hit) | 1 frame: shield plate flashes #00E5FF, spark particles ×3 | 0.1 s |
| Slam windup | 2 frames: arm raises overhead, body leans back | 0.3 s |
| Slam active | 1 frame: arm slams down, ground impact ring r=50 | 0.1 s |
| Hurt (rear/above) | 1 frame: white flash, body staggers | 0.1 s |
| Death | Shield plate shatters (4 fragments), body collapses, sparks | 0.8 s |

## Press Golem (W1 Boss)

**Silhouette:** A squat hydraulic press given legs. Two massive piston arms, a visor slit across its "face," exhaust pipes on shoulders. At a glance: "a construction press that wants to flatten you."

**Facings:** Left, Right.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Steam puffs from joints every 1.5 s. Body bobs y ±2. | 2 s |
| Arm Slam | 4 frames: arm raises 48 px → descends fast → impact squash → recover. | 0.8 s |
| Fan Shot | 2 frames: visor opens, 5 muzzle lines fan ±25°. | 0.3 s |
| Charge (telegraph) | Visor pulses amber 3× over 0.6 s, body glows #FFB347. | Before attack |
| Charge (active) | Body leans forward, legs blur, dust trail. | 1.5 s |
| Drone summon | Shoulder pipes vent steam, 2 driplings materialise in cyan flash. | 0.5 s |
| Phase transition | Screen flash white 100%. Body shakes 0.5 s. New colour accent on visor. | 1.0 s |
| Hurt | White flash on piston joints. | 0.1 s |
| Death | Pistons explode outward (8 shards), body crumbles over 2 s, steam floods screen. | 2 s |

## Reservoir Warden (W2 Boss)

**Silhouette:** A floating octagonal core with four long segmented tentacle arms ending in claw pincers. Bioluminescent veins pulse across its surface. At a glance: "a deep-sea jellyfish made of subway infrastructure."

**Facings:** Rotates; no fixed facing.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Arms rotate slowly (15°/s). Core pulses cyan. | Continuous |
| Sweep | 2 arms extend 80 px in a line, core flashes magenta (telegraph 0.5 s). | 1 s |
| Mine drop | Core opens bottom, 3 mines detach and fall. | 0.3 s |
| Teleport | Core shrinks to r=8, reappears at new x with cyan ring expanding. | 0.4 s |
| Ring shot | All 4 arms extend, core spins 360° in 0.8 s, 8 bullets emit. | 0.8 s |
| Shieldbot deploy | 2 arms reach down, shieldbots rise from floor. | 0.6 s |
| Triple slam | 3× rapid arm-down impacts, ground rings r=60 each. | 1.8 s |
| Phase transition | Screen flash white 100%. Core cracks glow brighter. Arms speed up. | 1.0 s |
| Hurt | Core dims to 30% for 0.15 s, veins flash white. | 0.15 s |
| Death | Core cracks (4 lines), collapses inward to r=8, then detonates in expanding cyan ring + 12 shard fragments. | 2.5 s |

---

# 6. AUDIO

All sounds generated with the Web Audio API. No external files. Each oscillator/noise buffer is pre-built in `audio.js init()` and triggered via `ctx.audioQueue.push({id})`.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| jump | Oscillator: square, 220→440 Hz sweep, 0.1 s, attack 0.01 s, decay 0.09 s | §4 Movement: jump or double-jump triggered |
| double_jump | Oscillator: triangle, 330→550 Hz, 0.08 s, sharper attack | §4 Movement: second jump in air |
| land | Noise buffer: low-pass 800 Hz, 0.06 s, gain 0.3 | §4 Movement: player touches ground after airborne |
| crouch | Oscillator: sine, 180 Hz, 0.05 s, soft | §4 Movement: crouch state entered |
| shoot_pulse | Oscillator: sawtooth, 880→440 Hz, 0.04 s, gain 0.4 | §4 Combat: pulse_rifle fires |
| shoot_scatter | Noise burst: band-pass 2000 Hz, 0.12 s, gain 0.6 | §4 Combat: scatter_cannon fires |
| shoot_rail | Oscillator: sine, 1200→200 Hz sweep, 0.25 s, gain 0.7 + sub-bass 60 Hz 0.15 s | §4 Combat: rail_lance fires |
| shoot_arc | Oscillator: square, 600 Hz, 0.06 s + noise crackle 0.04 s | §4 Combat: arc_burst fires |
| arc_chain | Oscillator: triangle, 1000→1500 Hz, 0.08 s, gain 0.3 | §4 Combat: arc_burst chain triggers |
| hit_enemy | Noise: high-pass 3000 Hz, 0.05 s, gain 0.3 | §4 Combat: projectile hits enemy |
| enemy_die | Oscillator: sawtooth, 200→80 Hz, 0.2 s, gain 0.4 | §4 EnemyAI: enemy hp ≤ 0 |
| enemy_shoot | Oscillator: square, 500 Hz, 0.04 s, gain 0.25 | §4 EnemyAI: dripling/sentry fires bullet |
| mine_fuse | Oscillator: sine, 1000 Hz, 0.1 s repeat ×6 (0.6 s total), gain 0.3 | §4 EnemyAI: mine proximity triggered |
| mine_explode | Noise: low-pass 400 Hz, 0.3 s, gain 0.7 + oscillator 80 Hz 0.2 s | §4 EnemyAI: mine detonates |
| player_hurt | Oscillator: square, 300→150 Hz, 0.15 s, gain 0.5 | §4 DamageAndDeath: player takes damage |
| player_die | Oscillator: sawtooth, 400→50 Hz, 0.6 s, gain 0.6 + noise 0.4 s | §4 DamageAndDeath: hp ≤ 0, state="dead" |
| shield_regen | Oscillator: sine, 600 Hz, 0.3 s, gain 0.1 (quiet) | §4 DamageAndDeath: shield reaches 50 after regen |
| pickup_health | Oscillator: sine, 523→659→784 Hz (3-note), 0.2 s, gain 0.4 | §4 PickupAndAmmo: health pickup collected |
| pickup_ammo | Oscillator: triangle, 440→520 Hz, 0.1 s, gain 0.3 | §4 PickupAndAmmo: ammo pickup collected |
| pickup_coin | Oscillator: sine, 1047 Hz, 0.08 s, gain 0.3 | §4 PickupAndAmmo: coin collected |
| pickup_shield | Oscillator: sine, 660→880 Hz, 0.15 s, gain 0.35 | §4 PickupAndAmmo: shield pickup collected |
| checkpoint | Oscillator: sine, 440→660→880 Hz arpeggio, 0.4 s, gain 0.5 | §4 StageFlow: checkpoint touched |
| stage_clear | Oscillator: square, 523→659→784→1047 Hz, 0.6 s, gain 0.5 | §4 StageFlow: extraction pad touched |
| boss_phase | Noise: band-pass 1000 Hz, 0.5 s, gain 0.6 + oscillator 100 Hz 0.3 s | §4 BossAI: phase transition |
| boss_slam | Noise: low-pass 200 Hz, 0.2 s, gain 0.7 | §4 BossAI: ground slam attack |
| boss_die | Oscillator: sawtooth, 200→30 Hz, 1.0 s, gain 0.7 + noise 0.8 s | §4 BossAI: boss hp ≤ 0 |
| weapon_switch | Oscillator: triangle, 800 Hz, 0.03 s, gain 0.2 | §4 Combat: weapon switched |
| game_over | Oscillator: sine, 220→110 Hz, 1.5 s, gain 0.4 | §4 DamageAndDeath: lives = 0 |
| game_complete | Oscillator: sine, 523→659→784→1047→1319 Hz, 2.0 s, gain 0.5 | §4 StageFlow: W2S5 boss defeated |
| ui_select | Oscillator: square, 600 Hz, 0.04 s, gain 0.2 | §7: menu navigation confirm |
| ui_back | Oscillator: square, 400 Hz, 0.04 s, gain 0.2 | §7: menu back |
| crumble_shake | Noise: band-pass 1500 Hz, 0.3 s, gain 0.25 | §4 Movement: crumble platform shakes before removal |
| laser_gate_on | Oscillator: sawtooth, 2000 Hz, 0.1 s, gain 0.3 | §4 Hazard: laser gate activates |
| laser_gate_off | Oscillator: sawtooth, 2000→500 Hz, 0.08 s, gain 0.2 | §4 Hazard: laser gate deactivates |
| low_ammo | Oscillator: square, 300 Hz, 0.08 s, gain 0.2, repeats every 1 s | §7 HUD: ammo ≤ 10% of max |

**Music:** A simple looping bass-pad track per world. W1: 80 BPM, sawtooth bass 55 Hz + pad 220/330 Hz, gain 0.15. W2: 90 BPM, sine bass 50 Hz + pad 196/294 Hz, gain 0.12. Boss arenas: add kick drum (noise 100 Hz, 0.1 s, every 2 beats). Music is queued as a persistent oscillator set, not via `audioQueue`. Volume ducks to 50% during boss phase transitions.

---

# 7. UX

**HTML/CSS only for the page shell.** The `<canvas>` fills the viewport. All game UI (HUD, screens, overlays) is drawn onto the canvas by `ui.js` and `renderer.js`. No DOM elements for in-game UI.

## Screen state machine

```
TITLE → WORLD_SELECT → STAGE_PLAY ⇄ PAUSE
                         ↓              ↓
                    STAGE_CLEAR → (next stage STAGE_PLAY or WORLD_SELECT)
                         ↓
                    GAME_OVER → TITLE
                         ↓
                    GAME_COMPLETE → TITLE
```

| State | Trigger in | Trigger out | Content |
|---|---|---|---|
| TITLE | Boot, or from GAME_OVER/GAME_COMPLETE | Enter / tap | "GRIDFALL" stencil logo (#FFB347), subtitle "A DATA-RUNNER'S DESCENT" (#00E5FF), "PRESS ENTER / TAP TO START" pulsing (#FF2D78). BG: parallax layers 1–3, one neon sign flickering. Vignette + grain. Best total stars shown if localStorage has data. |
| WORLD_SELECT | Enter from TITLE; after stage clear if boss | Enter (select stage); Escape (→ TITLE) | 2×5 grid of stage nodes. W1 row: 5 nodes. W2 row: locked (grey #3D3D3D) until W1S5 cleared. Completed nodes glow cyan (#00E5FF). Current node pulses magenta (#FF2D78). Path line amber (#FFB347). Stars shown as 0–3 filled diamonds under each node. Arrow keys / tap to select. Enter → STAGE_PLAY. |
| STAGE_PLAY | Enter from WORLD_SELECT; next stage from STAGE_CLEAR | Escape (→ PAUSE); lives=0 (→ GAME_OVER); extraction pad / boss dead (→ STAGE_CLEAR) | Gameplay. HUD overlaid. Stage intro banner slides in (0.6 s in, 1.5 s hold, 0.4 s fade): "WORLD X – STAGE Y" (#FFB347) + world name (#00E5FF) on dark BG (#0F1B1F). |
| PAUSE | Escape/P from STAGE_PLAY | Escape (→ STAGE_PLAY); R (→ STAGE_PLAY restart); Q (→ WORLD_SELECT) | Semi-transparent overlay (#0F1B1F 85%). "PAUSED" text. Three options: Resume, Restart Stage, Quit to World Select. |
| STAGE_CLEAR | Extraction pad touched or boss dead | Enter (→ next STAGE_PLAY or WORLD_SELECT) | Stage name, clear time, enemies killed %, coins collected, stars earned (1–3 filled diamonds, #FFB347). "PRESS ENTER TO CONTINUE." |
| GAME_OVER | Lives = 0 | Enter (→ WORLD_SELECT, stage 1 of current world) | "SYSTEM FAILURE — LIVES EXHAUSTED" (#FF2D78). Stage reached shown. "PRESS ENTER TO RESTART WORLD." |
| GAME_COMPLETE | W2S5 boss dead, W2S5 cleared | Enter (→ TITLE) | "SPIRE PURGE COMPLETE" (#FFB347). Total stars (max 30). Best time. "PRESS ENTER TO RETURN TO TITLE." |

## HUD (drawn during STAGE_PLAY)

| Element | Record field shown | Position | When visible |
|---|---|---|---|
| HP bar (120 px wide, green→red gradient) | `player.hp / player.maxHp` | Top-left (16, 16) | Always |
| Shield bar (120 px, #00E5FF, below HP) | `player.shield / player.maxShield` | Top-left (16, 32) | Always (dimmed if shield = 0) |
| Lives counter (3 small helmet icons) | `player.lives` | Top-left (16, 48) | Always |
| Weapon name + ammo count | `player.weaponIndex` → weapon id + `player.ammo[weaponIndex]` | Bottom-left (16, canvasH−32) | Always |
| Weapon icon row (4 slots, active ringed #00E5FF) | `player.weapons[0..3]` (owned/locked) | Bottom-left (16, canvasH−64) | Always; locked slots show "?" |
| Stage indicator "W1-S3" | `level.world` / `level.stage` | Top-centre (canvasW/2, 16) | Always |
| Timer (counts up, MM:SS) | `ctx.time` | Top-right (canvasW−100, 16) | Always |
| Coin count | `ScoreBoard.coinsCollected` | Top-right (canvasW−100, 32) | Always |
| Boss HP bar (wide, top-centre) | `Boss.hp / Boss.maxHp` | Top-centre (canvasW/2−150, 48) | Boss stage only, from first arena entry |
| Checkpoint flash text "CHECKPOINT" | Triggered on touch | Centre screen | 1.0 s on activation |
| Low-ammo warning (weapon icon pulses red) | `player.ammo[active] ≤ 10% of max` | Bottom-left | While condition true |

---

# 8. DEBUG API

Installed by `debug.js` as `window.__game`. Every call is synchronous, returns plain data, never touches the DOM.

| Call | What it does | Returns |
|---|---|---|
| `__game.start()` | Transitions `title` → `play`, loads stage 1-1, initialises player. | `void` |
| `__game.step(dt, n)` | Runs exactly `n` fixed ticks of `dt` seconds each (in §1.2 tick order), then draws once. | `void` |
| `__game.setTime(t)` | Runs ticks until `ctx.time ≥ t`, without drawing. | `void` |
| `__game.seed(n)` | Reseeds `ctx.rng` with `n`, calls `level.load(ctx, 1, 1)`, resets player and all pools. | `void` |
| `__game.getState()` | Deep-cloned plain object of all `ctx` fields (minus `canvas`, `ctx2d`, `rng`). | `{state, time, frame, seed, player, level, camera, progression, enemies:[...], projectiles:[...], particles:[...], shake, hitFlash}` |
| `__game.move(dir)` | Sets `ctx.input.moveDir = dir` (−1, 0, +1). Persists. | `void` |
| `__game.jump()` | Sets `ctx.input.jumpPressed = true` for next tick. | `void` |
| `__game.crouch(on)` | Sets `ctx.input.crouchHeld = on`. | `void` |
| `__game.fire(on)` | Sets `ctx.input.fireHeld = on`; `firePressed = true` if transitioning to on. | `void` |
| `__game.switchWeapon(dir)` | Sets `ctx.input.switchNext = true`. | `void` |
| `__game.selectSlot(n)` | Sets `ctx.input.weaponSlot = n` (1–4). | `void` |
| `__game.spawnEnemy(type, x, y, dir)` | Calls `enemies.spawn(ctx, type, x, y, dir)`. | `{id, x, y, type, alive}` |
| `__game.spawnProjectile(weaponId, x, y, vx, vy)` | Pulls from projectile pool. | `{id, x, y, alive}` |
| `__game.skipToStage(w, s)` | Calls `level.load(ctx, w, s)`, resets player, sets state to `play`. | `{world, stage, spawnX, spawnY}` |
| `__game.setField(path, value)` | Sets `ctx` field at dotted path. | `void` |
| `__game.getFrameCount()` | Returns `ctx.frame`. | `number` |
| `__game.getDrawCalls()` | Returns canvas draw ops from last draw. | `number` |
| `__game.getStateHash()` | 32-bit hash of `getState()` JSON. | `number` |
| `__game.triggerCheckpoint()` | Forces checkpoint activation at `level.checkpointX`. | `void` |
| `__game.killBoss()` | Sets boss `hp = 0`, triggers death sequence. | `void` |
| `__game.setAmmo(weaponIndex, amount)` | Sets `player.ammo[weaponIndex]`. | `void` |
| `__game.unlockAllWeapons()` | Sets all `player.weapons` slots to owned. | `void` |
| `__game.spawnBoss(bossId, x, y)` | Calls `enemies.spawnBoss(ctx, bossId, x, y)`. | `{id, x, y, hp, alive}` |
| `__game.setPlayerPos(x, y)` | Teleports player to (x, y), resets velocity. | `void` |
| `__game.hurtPlayer(dmg)` | Calls `player.hurt(ctx, dmg)`. | `void` |
| `__game.setLives(n)` | Sets `player.lives = n`. | `void` |
| `__game.setShield(n)` | Sets `player.shield = n`. | `void` |
| `__game.setHp(n)` | Sets `player.hp = n`. | `void` |
| `__game.triggerHazard(hazardType, x, y)` | Spawns a hazard entity at position. | `{type, x, y}` |
| `__game.placePickup(type, x, y)` | Spawns a pickup entity. | `{type, x, y}` |
| `__game.setNgPlus(on)` | Sets `progression.ngPlus = on`, `difficultyScale = 1.4`. | `void` |

**Determinism guarantee:** Given the same `seed(n)` and the same sequence of `__game.*` calls, `getState()` returns byte-identical data every time. No call reads wall-clock time or `Math.random()`.

---

# 9. TESTS

All tests drive the game exclusively through `window.__game`. Numbered in execution order.

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
__game.step(1/60, 60)   // 1 second rightward
p = __game.getState().player
```
Assert: `p.x > state.level.spawnX + 280 * 0.9` (within 10% for accel ramp), `p.onGround === true`, `p.facing === 1`.

### T3 – Jump physics
```
__game.seed(42); __game.start()
__game.jump()
__game.step(1/60, 1)
p = __game.getState().player
```
Assert: `p.vy < 0` (Y-down: jump is negative vy), `p.onGround === false`, `p.state === 'airborne'`, `p.jumpCount === 1`.

### T4 – Crouch changes hitbox
```
__game.seed(42); __game.start()
h0 = __game.getState().player.h
__game.crouch(true)
__game.step(1/60, 1)
h1 = __game.getState().player.h
```
Assert: `h1 === 28`, `h0 === 48`, `__game.getState().player.crouching === true`, `__game.getState().player.state === 'crouching'`.

### T5 – Fire weapon (pulse_rifle)
```
__game.seed(42); __game.start()
__game.selectSlot(1)
__game.fire(true)
__game.step(1/60, 1)
pr = __game.getState().projectiles.filter(p => p.alive)
```
Assert: `pr.length >= 1`, `pr[0].x > __game.getState().player.x` (fired rightward), `pr[0].vx > 0`.

### T6 – All 4 weapon types fire
```
__game.seed(42); __game.start()
__game.unlockAllWeapons()
__game.setAmmo(0, 120); __game.setAmmo(1, 24); __game.setAmmo(2, 10); __game.setAmmo(3, 40)
for slot in [1,2,3,4]:
    __game.selectSlot(slot)
    __game.fire(true)
    __game.step(1/60, 1)
allProj = __game.getState().projectiles.filter(p => p.alive)
```
Assert: `allProj.length >= 4` (at least one alive per weapon), distinct `weaponId` values ≥ 4.

### T7 – Weapon switch
```
__game.seed(42); __game.start()
__game.unlockAllWeapons()
w0 = __game.getState().player.weaponIndex
__game.switchWeapon(1)
__game.step(1/60, 1)
w1 = __game.getState().player.weaponIndex
```
Assert: `w1 !== w0`.

### T8 – Enemy spawn & existence
```
__game.seed(42); __game.start()
e = __game.spawnEnemy('rust_crawler', 300, 440, -1)
__game.step(1/60, 1)
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length >= 1`, `en[0].type === 'rust_crawler'`, `en[0].hp === 30`.

### T9 – Projectile kills enemy
```
__game.seed(42); __game.start()
__game.unlockAllWeapons(); __game.setAmmo(0, 120)
e = __game.spawnEnemy('rust_crawler', 200, 440, -1)
__game.selectSlot(1)
__game.fire(true)
__game.step(1/60, 120)  // 2 seconds – pulse rifle proj at 700 px/s covers 1400 px
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length === 0` (crawler hp 30, pulse damage 12, 3 shots needed, 120 ticks = ~14 shots at 7/s).

### T10 – Player takes damage
```
__game.seed(42); __game.start()
hp0 = __game.getState().player.hp
sh0 = __game.getState().player.shield
__game.spawnEnemy('rust_crawler', 50, 440, 1)  // enemy right at player
__game.step(1/60, 30)
p = __game.getState().player
```
Assert: `p.shield < sh0 || p.hp < hp0`, `p.invulnTimer > 0`.

### T11 – Stage clear → advance
```
__game.seed(42); __game.start()
s = __game.getState()
__game.setField('player.x', s.level.exitX)
__game.setField('player.y', s.level.exitY)
__game.step(1/60, 10)
s2 = __game.getState()
```
Assert: `s2.level.stage === 2`, `s2.level.world === 1`, `s2.progression.stagesCleared` includes `"1-1"`.

### T12 – World progression (2 worlds × 5 stages)
```
__game.seed(42); __game.start()
for w in [1,2]:
    for st in [1,2,3,4,5]:
        __game.skipToStage(w, st)
        if st < 5:
            s = __game.getState()
            __game.setField('player.x', s.level.exitX)
            __game.setField('player.y', s.level.exitY)
            __game.step(1/60, 10)
        else:
            __game.skipToStage(w, 5)
            __game.spawnBoss(w === 1 ? 'press_golem' : 'reservoir_warden', 800, 300)
            __game.killBoss()
            __game.step(1/60, 200)  // 3s death sequence + transition
final = __game.getState()
```
Assert: `final.progression.stagesCleared.length === 10`, `final.state === 'game-complete'`.

### T13 – Restart preserves stage, resets player
```
__game.seed(42); __game.start()
__game.move(1); __game.step(1/60, 60)
__game.setField('input.restart', true)
__game.step(1/60, 1)
s = __game.getState()
```
Assert: `s.level.stage === 1`, `s.player.x === s.level.spawnX`, `s.player.hp === 100`, `s.player.shield === 50`.

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
    __game.spawnEnemy('rust_crawler', 50 + i*10, 440, -1)
en = __game.getState().enemies.filter(x => x.alive)
```
Assert: `en.length <= 40`.

### T17 – Determinism
```
__game.seed(1337); __game.start()
__game.move(1); __game.jump(); __game.fire(true)
__game.step(1/60, 300)
h1 = __game.getStateHash()

__game.seed(1337); __game.start()
__game.move(1); __game.jump(); __game.fire(true)
__game.step(1/60, 300)
h2 = __game.getStateHash()
```
Assert: `h1 === h2`.

### T18 – Same seed, different call order → different state
```
__game.seed(1337); __game.start(); __game.fire(true); __game.step(1/60,1); __game.jump(); __game.step(1/60,1)
hA = __game.getStateHash()
__game.seed(1337); __game.start(); __game.jump(); __game.step(1/60,1); __game.fire(true); __game.step(1/60,1)
hB = __game.getStateHash()
```
Assert: `hA !== hB`.

### T19 – Shield regen
```
__game.seed(42); __game.start()
__game.setShield(0)
__game.setField('player.shieldRegenDelay', 0)
__game.step(1/60, 200)  // ~3.3 s; regen starts at 2.0 s, gains 12/s for 1.3 s ≈ 15 pts
p = __game.getState().player
```
Assert: `p.shield >= 12`, `p.shield <= 50`.

### T20 – Double-jump
```
__game.seed(42); __game.start()
__game.jump()
__game.step(1/60, 10)
__game.jump()
__game.step(1/60, 1)
p = __game.getState().player
```
Assert: `p.jumpCount === 2`, `p.vy < 0` (second jump applied).

### T21 – Crumble platform
```
__game.seed(42); __game.start()
__game.skipToStage(1, 1)
// Find a crumble platform in level.platforms, place player on it
s = __game.getState()
cp = s.level.platforms.find(p => p.type === 'crumble')
__game.setPlayerPos(cp.x + cp.w/2, cp.y - 48)
__game.step(1/60, 120)  // 2 s > 1.5 s timer + 0.4 s shake
cp2 = __game.getState().level.platforms.find(p => p.type === 'crumble' && p.x === cp.x)
```
Assert: `cp2 === undefined || cp2.removed === true`.

### T22 – Boss phase transition
```
__game.seed(42); __game.start()
__game.skipToStage(1, 5)
__game.spawnBoss('press_golem', 800, 380)
__game.setField('enemies[0].hp', 399)  // below phaseTransitionHP 400
__game.step(1/60, 10)
b = __game.getState().enemies[0]
```
Assert: `b.phase === 2`, `b.state === 'transition'` or `b.invulnTimer > 0`.

### T23 – Pickup collection
```
__game.seed(42); __game.start()
__game.placePickup('health', 100, 420)
__game.setField('player.hp', 50)
__game.setPlayerPos(100, 420)
__game.step(1/60, 1)
p = __game.getState().player
```
Assert: `p.hp === 75` (50 + 25).

### T24 – Weapon unlock progression
```
__game.seed(42); __game.start()
w0 = __game.getState().player.weapons  // [1,0,0,0]
__game.skipToStage(1, 2)
// Find unlock crate in level, place player on it
__game.setField('level.unlockCrate', {type:'scatter_cannon', x:500, y:440})
__game.setPlayerPos(500, 440)
__game.step(1/60, 1)
w1 = __game.getState().player.weapons
```
Assert: `w1[1] === 1` (scatter owned).

### T25 – Game over (lives exhausted)
```
__game.seed(42); __game.start()
__game.setLives(1)
__game.setHp(1)
__game.setShield(0)
__game.hurtPlayer(50)  // kills player, lives → 0
__game.step(1/60, 120)  // 2 s > 1.5 s respawn fade
s = __game.getState()
```
Assert: `s.state === 'game-over'`.

## SCREENSHOTS

| Screen / State | How to Reach | What a Reviewer Must See |
|---|---|---|
| Title screen | Launch game | "GRIDFALL" in stencil (#FFB347), subtitle cyan (#00E5FF), "PRESS START" pulsing magenta. BG: parallax layers 1–3, neon sign flickering. Vignette + grain. |
| World map | After title | 2×5 node grid. W1 row: 5 nodes (W2 locked grey). Path line amber. Player icon at 1-1. Completed nodes cyan. |
| Stage intro banner | Enter any stage | Full-screen slide-in: "WORLD 1 – STAGE 1" (#FFB347), "THE RUSTBELT" (#00E5FF), dark BG. Holds 1.5 s. |
| Gameplay – W1 S1 mid-run | Play to x≈600 | Player on corrugated-steel platform, right-facing, running. BG: smokestacks (far), pipes (mid), dripping chain (near). Neon sign flickering. Ground rust-orange/steel. Rust Crawler ahead. HUD: HP bar, shield bar, lives, ammo counter, 4 gun icons with Pulse Rifle ringed cyan. |
| Gameplay – firing Scatter Cannon | Equip slot 2, shoot | Muzzle flash: 3 radial magenta lines. 6 pellets fanning 18° cone. Player recoil lean-back. Selector ring on Scatter. |
| Gameplay – Rail Lance firing | Equip slot 3, shoot | Long thin cyan projectile with wavy edge, 1400 px/s. Coil glow on gun. Player frozen (recoil lockout). |
| Gameplay – Arc Burst chain | Equip slot 4, shoot near 2 enemies | Magenta orb hits first enemy, wavy cyan chain arc to second enemy within 90 px. |
| Gameplay – crouch under low pipe | Crouch beneath 32-px gap | Player squashed 24×28, helmet retracted, passing under pipe. Conveyor platform nearby with scrolling chevrons. |
| Gameplay – W2 S3 flooded section | Play W2 S3 mid | Player ankle-deep in electrified water (cyan, wavy top, white sparks). Dripling hovering above. Bioluminescent moss (pulsing cyan). BG: brick arches. Teal-dominant palette. |
| Checkpoint activation | Touch totem mid-stage (S3+) | Ring expanding from totem orb, 12 amber motes rising. Orb bright cyan. Radial white flash. |
| Boss – Press Golem | W1 S5, enter arena | Arena: ambient 10%, overhead white spotlight. Press Golem (80×100) far side, visor pulsing amber. Player small foreground. Steam puffs. Ceiling at 160 px. |
| Boss – Reservoir Warden | W2 S5, enter arena | Drained reservoir, concentric ring platforms. Octagonal core floating centre, 4 tentacle arms extended. Bioluminescent veins pulsing. Dark ambient, cyan glow. |
| Player hurt – low HP | Take damage until hp < 25 | Player flashing magenta. Vignette 55%, red edge tint. HP bar nearly empty, green→red. |
| Player death | HP reaches 0 | Screen desaturated 20%. 8 triangle shards flying apart. "SCRAPPED" text #FF2D78. |
| Stage clear | Reach extraction pad | Pad ring pulses, confetti 20 rects scatter. Stage number stencil. Player walking toward light. |
| Game complete | W2S5 boss dead | "SPIRE PURGE COMPLETE" (#FFB347). Total stars count. Best time. |
| Particle close-up | Any moment with multiple effects | Hit sparks (lines), dust (ellipses), pickup sparkles (stars), steam (circles). All 3-px black outlines. |

---

# 10. BUILD ORDER

| # | Milestone | Modules added / completed | Proof check |
|---|---|---|---|
| **M1** | Page opens, draws title, enters play | `game.js` (state machine, rAF loop), `canvas` setup, `ui.js` (title + HUD skeleton), `debug.js` (`start`, `step`, `getState`, `seed`) | **T1** passes. |
| **M2** | Player moves, jumps, crouches on flat tile floor | `input.js`, `physics.js`, `player.js`, `level.js` (single flat strip) | **T2, T3, T4** pass. |
| **M3** | Camera follows player; full tile map renders | `camera.js`, `level.js` (full stage 1-1 tiles), `ui.js` (HUD) | **T15** passes (draw-call budget on real level). |
| **M4** | 4 gun types fire projectiles; weapon switching | `weapons.js` (definitions + projectile pool), `player.js` (shoot state) | **T5, T6, T7** pass. |
| **M5** | Enemies patrol, take damage, die; score | `enemies.js`, `particles.js`, `audio.js` | **T8, T9, T10** pass. |
| **M6** | Stage-clear trigger, world/stage progression, restart, pause | `progression.js`, `game.js` (transition states), `ui.js` (overlays) | **T11, T12, T13, T14** pass. |
| **M7** | Shield regen, double-jump, crumble platforms, pickups | `player.js` (shield, coyote, buffer), `level.js` (platform types), `progression.js` (pickups) | **T19, T20, T21, T23** pass. |
| **M8** | All 10 stages generated; touch controls; full audio; weapon unlocks | `level.js` (generator + verifier all stages), `input.js` (touch), `audio.js` (music + all SFX), `progression.js` (unlock table) | **T16, T17, T18, T24** pass. |
| **M9** | Bosses, hazards, mine/shieldbot, phase AI | `enemies.js` (boss AI, mine, shieldbot), `level.js` (hazard placement) | **T22, T25** pass. |
| **M10** | Polish: full parallax, all particles, post-effects, scoring, NG+, world-select, game-complete | `renderer.js` (parallax, post-effects), `particles.js` (all types), `progression.js` (stars, NG+), `ui.js` (all screens) | Full regression: **T1–T25** all pass. |

---

# 11. DEFINITION OF DONE

| Requirement (from 0.1) | Checks that prove it | Screenshot rows that prove it |
|---|---|---|
| Side-scrolling platformer shooter | T2, T3, T4, T9, T15 | Gameplay – W1 S1 mid-run |
| At least 4 different gun types | T5, T6, T7 | Firing Scatter Cannon, Rail Lance, Arc Burst chain |
| Character can jump | T3, T20 | Gameplay – W1 S1 mid-run (airborne) |
| Character can move left or right | T2 | Gameplay – W1 S1 mid-run |
| Character can crouch | T4 | Crouch under low pipe |
| Story progression: worlds and stages | T11, T12 | World map, Stage intro banner |
| 2 worlds | T12 (loops w=1,2) | Boss – Press Golem, Boss – Reservoir Warden |
| 5 stages per world | T12 (loops st=1..5) | World map (2×5 grid) |
| Do not simply copy Mario | T6 (4 distinct weapons), T8 (5 enemy types), T22 (multi-phase bosses), T24 (weapon unlock crates), seeded generation (T17 determinism) | All gameplay screenshots show distinct art/style |
| **Added:** Camera with look-ahead/dead-zone | T15 (draw calls include camera offset) | Gameplay – W1 S1 (camera shows ahead) |
| **Added:** Seeded procedural levels | T17, T18 | — |
| **Added:** Shield regen | T19 | — |
| **Added:** Checkpoints and lives | T25, T13 | Checkpoint activation |
| **Added:** Star scoring and par times | T12 (stagesCleared length) | Stage clear |
| **Added:** Boss fights | T22 | Boss – Press Golem, Boss – Reservoir Warden |
| **Added:** Parallax, particles, post-effects | T15 (draw budget with all layers) | Particle close-up, all gameplay shots |
| **Added:** Touch controls | (manual test; synthesises into same ctx.input) | — |
| **Added:** New Game+ | (manual: `__game.setNgPlus(true)`, verify HP scaling) | — |

When every header row is complete, the game is complete.

---

# A. SANITY

Checks performed against sections 2, 4, 8, and 9:

1. **Every field a rule reads or writes is in the global context.** Player fields (x, y, vx, vy, facing, state, hp, shield, shieldRegenDelay, crouchHeight, jumpCount, invulnTimer, coyoteTimer, jumpBufferTimer, weaponIndex, weapons, ammo, shootCooldown, recoilLockout, lives) — all present in §2.2 `ctx.player`. ✓

2. **Every place, thing or kind a rule names is placed by a generator or listed in a roster.** Enemies: 5 types in §4 Enemy Roster + 2 bosses in §4 Boss Roster. Platforms: 4 types in §4 Platform record. Hazards: 3 types in §4 Hazard record. Pickups: 7 types in §4 Pickup record. LevelGenerator places all of these per §4 rules. ✓

3. **For every consumable, total placed vs total demanded along core loop.** Pulse Rifle: 120 start, W1S1 has ~7 enemies × 24 HP / 12 dmg = 14 shots. W1S2–S4 add ammo pickups (2 per stage × 20 = 40 more). Rail Lance: 10 charges, each does 55 dmg; bosses need 600/55 ≈ 11 hits but pierce hits multiple enemies. Ammo pickups in W2 refill. Shieldbot: 70 HP × 15% of W2 enemies (W2S4: 16 enemies, ~2 shieldbots = 140 HP). Pulse Rifle at 12 dmg needs 12 shots per shieldbot from behind. Total ammo across a full run is sufficient with pickups. Closes. ✓

4. **Every timing pair closes AND still bites.**
   - Spawn vs clear: W1S1 has 7 enemies, player DPS with pulse rifle = 12×7 = 84 dps. Kill time ≈ 7×30/84 ≈ 2.5 s of sustained fire. Stage clear (reach pad) at 280 px/s across 3200 px ≈ 11.4 s travel + combat. Par time 55 s. Closes, bites (player must fight while moving). ✓
   - Drain vs refill: Shield 50, regen 12/s after 2 s delay. A hit of 20 damage drains 20 shield. Recovery: 2 s delay + 20/12 ≈ 1.7 s = 3.7 s total. Laser gate fires every 2 s. Closes, bites (can't regen between two laser ticks). ✓
   - Travel time vs distance at given speed: Pulse Rifle projectile 700 px/s, life 1.1 s → range 770 px. Sentry aggro 320 px. Player can out-range sentry. Closes. ✓
   - End-condition clock vs expected clear time: Game is 10 stages. Par times sum to 55+65+75+85+95+55+65+75+85+95 = 750 s (12.5 min). Skilled run 20–25 min (includes deaths, exploration). No hard timer on the game itself (only per-stage par for 3 stars). Closes. ✓
   - Boss HP vs player DPS: Press Golem 600 HP. Pulse Rifle 84 dps → 7.1 s of sustained fire. With dodging, expect 30–60 s. Phase transitions add invuln. Closes, bites (player must dodge while dealing damage). ✓
   - Crumble timer 1.5 s vs jump arc: Player at 280 px/s covers 420 px in 1.5 s. Platform widths 64–192 px. Player can jump off before removal. Closes. ✓
   - Laser gate on 1.0 s / off 1.0 s vs player speed: Player traverses 280 px in 1.0 s. Laser is a vertical beam at fixed x. Player must time crossing during off phase. Closes, bites. ✓

5. **Every call section 9 makes is in section 8.** T1–T25 use: `seed`, `start`, `getState`, `step`, `move`, `jump`, `crouch`, `fire`, `selectSlot`, `switchWeapon`, `unlockAllWeapons`, `setAmmo`, `spawnEnemy`, `skipToStage`, `spawnBoss`, `killBoss`, `setField`, `setPlayerPos`, `placePickup`, `hurtPlayer`, `setLives`, `setShield`, `setHp`, `getStateHash`, `getDrawCalls`, `setNgPlus`. All present in §8. ✓

6. **No placeholder in angle brackets remains.** All `<TILE_SIZE>`, `<PLAYER_W>`, `<PLAYER_H>`, `<PLAYER_MAX_HP>`, `<PLAYER_LIVES>`, `<PROJECTILE_POOL>`, `<ENEMY_POOL>`, `<PARTICLE_POOL>` have been filled in §2.2 and §1.1. Scanned all sections: none remain. ✓

7. **Every system in §4 is tagged with its tier.** Movement [T1], Combat [T1], DamageAndDeath [T1], EnemyAI [T1 for 3 types, T2 for 2], BossAI [T2], PickupAndAmmo [T1], LevelGenerator [T1 basic, T2 full], StageFlow [T1], Scoring [T2]. All tagged. ✓

8. **Visual implies a rule: Conveyor platform.** Visual shows conveyor with scrolling chevrons. Ruled T2 visual-only (no gameplay effect beyond solid). No velocity added to player standing on it. Consistent with §4 Platform types. ✓

9. **Visual implies a rule: Arc Welder as continuous beam.** Visual described Arc Welder as a beam weapon. Ruled: Arc Burst is a projectile (chain orb), NOT a beam. Visual recipe remapped to "electric orb with chain arc." No beam mechanic exists in §4 Combat. ✓

10. **Engineering's 5-slot weapon array reduced to 4.** §2.2 shows `weapons: [1,0,0,0]` and `ammo: [120,24,10,40]` — 4 entries. Controls table says 1/2/3/4 only. §8 `selectSlot(n)` accepts 1–4. Consistent. ✓

11. **Stage 5 boss arenas: no extraction pad.** §4 StageFlow states "No extraction pad; defeating boss triggers clear." §4 LevelGenerator step 8 places extraction pad only on non-boss stages. Generator skips step 8 for stage 5. Closes. ✓

12. **Coyote time and jump buffer are in the player record and the movement rules.** §2.2 has `coyoteTimer: 0` and `jumpBufferTimer: 0`. §4 Movement states both values. §5 Characters doesn't contradict. Closes. ✓

13. **Weapon unlock crates are placed by the generator (step 9).** §4 LevelGenerator step 9 lists fixed unlock positions. §2.2 `level` object includes entitySpawns which can carry crate type. §8 has `unlockAllWeapons()` for testing. T24 tests the unlock. Closes. ✓

14. **`renderer.js` is the only module touching `ctx2d`.** §2.1 lists it. §2.3 confirms. Engineering R1 eliminated by Y-down convention (§1.1). Closes. ✓

All checks pass. No changes needed.