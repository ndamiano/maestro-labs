# GAMEPLAY DESIGN — "GRIDFALL"

**2D side-scrolling platformer. Camera: horizontal follow with 120 px look-ahead in the facing direction; vertical follow activates when the player's Y leaves a ±80 px dead-zone around camera center; camera clamps to level bounds.**

---

# 1. THE GAME IN ONE PARAGRAPH

You are Kael, a freelance data-runner breaking into the seven floors of the Helix Spire, a mega-corporation's black-site server tower. Minute to minute you run, jump, crouch through low ducts, and shoot waves of security drones, sentries, and floor bosses with one of four weapons, managing a small ammo pool and a regenerating shield. Each world is a floor of the Spire; each stage is a sector you must clear left-to-right, reach the extraction pad at the far right, and survive. Stage 5 of every world is a boss arena. The game ends after you defeat the boss of World 2 (Sector 5 of Floor 2) and trigger the "Spire Purge" epilogue screen. Replayability comes from seeded level layouts that reshuffle platform and enemy placement between runs, a hidden score per stage (time, enemies killed, pickups collected), and a New Game+ mode where enemy HP and spawn density scale 1.4×. There is no endless mode; the game is 10 stages long, roughly 20–25 minutes for a skilled run.

---

# 2. RECORDS

RECORDS: Player, Weapon, AmmoPool, Enemy, Boss, Pickup, Platform, Hazard, LevelSeed, StageProgress, ScoreBoard

**Player** — Kael, the controllable character.
| Field | Unit | Start / Range |
|---|---|---|
| x, y | px | spawn point per stage (e.g. 80, 400) |
| vx, vy | px/s | 0, 0 |
| facing | −1 or +1 | +1 (right) |
| state | enum | "grounded" / "airborne" / "crouching" / "hurt" / "dead" |
| hp | points | 100 / max 100 |
| shield | points | 50 / max 50 |
| shieldRegenDelay | s | 0 (counts up after last hit; regen starts at 2.0) |
| crouchHeight | px | 28 (vs normal 48) |
| jumpCount | int | 0 (max 2 for double-jump) |
| invulnTimer | s | 0 (1.2 after being hit) |
| activeWeapon | Weapon.id | "pulse_rifle" |

**Weapon** — one of four entries (see roster table below).
| Field | Unit | Notes |
|---|---|---|
| id | string | see roster |
| damage | points/shot | see roster |
| fireRate | shots/s | see roster |
| spread | degrees (cone half-angle) | see roster |
| projectileSpeed | px/s | see roster |
| projectileLife | s | see roster |
| pelletsPerShot | int | see roster |
| pierceCount | int | see roster |
| chainRadius | px | see roster (Arc Burst only) |
| cooldownAfterFire | s | see roster |

**Weapon Roster:**
| id | damage | fireRate | spread | projSpeed | projLife | pellets | pierce | chainRadius | cooldown |
|---|---|---|---|---|---|---|---|---|---|
| pulse_rifle | 12 | 7.0 | 3° | 700 | 1.1 | 1 | 0 | 0 | 0 |
| scatter_cannon | 9 | 1.5 | 18° | 520 | 0.45 | 6 | 0 | 0 | 0.65 |
| rail_lance | 55 | 0.8 | 0° | 1400 | 2.0 | 1 | 3 | 0 | 1.1 |
| arc_burst | 14 | 4.0 | 8° | 480 | 0.8 | 1 | 0 | 90 | 0 |

**AmmoPool** — per-weapon remaining shots.
| Field | Unit | Start / Max |
|---|---|---|
| pulse_rifle | shots | 120 / 240 |
| scatter_cannon | shells | 24 / 48 |
| rail_lance | charges | 10 / 20 |
| arc_burst | cells | 40 / 80 |

**Enemy** — a spawned hostile.
| Field | Unit | Range |
|---|---|---|
| type | enum | see Enemy Roster |
| x, y | px | per spawn |
| hp | points | see roster |
| vx, vy | px/s | see roster |
| damage | points/contact | see roster |
| state | enum | "patrol" / "chase" / "attack" / "hurt" / "dead" |
| patrolDir | −1 or +1 | ±1 |
| patrolRange | px | 80–200 |
| aggroRange | px | see roster |
| attackCooldown | s | see roster |
| hitFlashTimer | s | 0 → 0.15 |

**Enemy Roster:**
| type | hp | vx | damage | aggroRange | attackCooldown | behavior |
|---|---|---|---|---|---|---|
| drone | 24 | 100 (floats, sine bob ±12 px) | 10 | 250 | 1.2 s (fires 1 slow bullet) | hovers toward player, stops at aggroRange |
| sentry | 40 | 0 (stationary turret) | 15 (bullet) | 320 | 1.0 s (fires aimed bullet, speed 300 px/s) | rotates to face player, fires |
| runner | 30 | 160 (ground, charges) | 18 (contact) | 200 | 0.4 s (melee lunge) | patrols, sprints at player |
| mine | 20 | 0 (static) | 35 (AoE radius 70 px) | 60 (proximity) | 0.6 s fuse | detonates on proximity |
| shieldbot | 70 | 60 (shuffles) | 20 (contact) | 180 | 2.0 s (melee slam) | carries front shield (blocks frontal damage), must be hit from behind/above |

**Boss** — one per world, occupies stage 5.
| Field | Unit | Range |
|---|---|---|
| id | string | "floor1_guardian" / "floor2_overseer" |
| hp | points | 600 / 1100 |
| phases | int | 3 |
| attackList | array | see Boss Attacks table |
| currentPhase | int | 1 |
| phaseTransitionHP | points | 400 / 366 (floor2) |

**Boss Attacks (Floor 1 Guardian "Custodian"):**
| # | Trigger | Effect |
|---|---|---|
| 1 | Every 3.0 s | Slams ground, spawns 2 shockwave projectiles (speed 200, damage 20, travel along ground) |
| 2 | Every 5.0 s | Fires 5 aimed bullets in a fan (±25°, speed 280, damage 15) |
| 3 | Phase 2+ | Charges horizontally across arena (speed 300, damage 30, 1.5 s duration, 4 s cooldown) |
| 4 | Phase 3 | Adds drone summons (2 drones, 200 px apart) every 6 s |

**Boss Attacks (Floor 2 Overseer "Architect"):**
| # | Trigger | Effect |
|---|---|---|
| 1 | Every 2.5 s | Sweeps a laser line across arena (travel 400 px/s, damage 25, 0.8 s duration) |
| 2 | Every 4.0 s | Drops 3 ceiling mines (fall speed 180, proximity detonate 50 px, damage 35) |
| 3 | Phase 2+ | Teleports to random x in arena, fires 8-bullet ring (speed 220, damage 12) |
| 4 | Phase 3 | Deploys 2 shieldbots, then performs a 3× ground-slam sequence (damage 30 each, 0.6 s gap) |

**Pickup** — collectible entity in level.
| Field | Unit | Range |
|---|---|---|
| type | enum | "ammo_pulse" / "ammo_scatter" / "ammo_rail" / "ammo_arc" / "health" / "shield" / "coin" |
| x, y | px | per spawn |
| amount | int | ammo: 20/6/3/10; health: 25; shield: 20; coin: 1 |

**Platform** — a solid tile or slab.
| Field | Unit | Range |
|---|---|---|
| x, y, w, h | px | w: 32–320; h: 16 or 32 |
| type | enum | "solid" / "one_way" / "crumble" |
| crumbleTimer | s | 0 → 1.5 (when stood on, starts counting; at 1.5 removes) |

**Hazard** — damaging geometry.
| Field | Unit | Range |
|---|---|---|
| type | enum | "spike" / "laser_gate" / "acid_pool" |
| x, y, w, h | px | per placement |
| damage | points/tick | spike: 20 (instant, 1.2 s invuln); laser_gate: 25 (contact); acid_pool: 10/s |
| laserPeriod | s | 2.0 (on 1.0, off 1.0) |

**LevelSeed** — integer, 32-bit, chosen at title or re-rolled.

**StageProgress** — tracks run state.
| Field | Unit | Range |
|---|---|---|
| currentWorld | int | 1–2 |
| currentStage | int | 1–5 |
| lives | int | 3 (start) |
| unlockedWeapons | set | {"pulse_rifle"} at start |

**ScoreBoard** — per-stage record.
| Field | Unit | Range |
|---|---|---|
| clearTime | s | measured |
| enemiesKilled | int | measured |
| coinsCollected | int | measured |
| stars | int | 0–3 (see Progression) |

---

# 3. SYSTEMS

SYSTEMS: Movement, Combat, WeaponSwitch, DamageAndDeath, EnemyAI, BossAI, PickupAndAmmo, LevelGenerator, StageFlow, Scoring

## Movement

**RULES (player-triggered):**

- **Left / Right** (A, ←, D, →, touch joystick L/R): set `Player.vx` toward ±280 px/s with acceleration 1800 px/s²; if no horizontal key held, decelerate at 2400 px/s² toward 0. Capping: |vx| ≤ 280 (crouching: ≤ 140).
- **Jump** (W, ↑, Space, touch A-button): if `Player.jumpCount < 2` AND `Player.state ≠ "crouching"` → apply `vy = −480`; `jumpCount += 1`. If `Player.state == "crouching"` → un-crouch first (1-frame, no jump this press).
- **Double-jump**: second press while airborne and `jumpCount == 1` → `vy = −400`; `jumpCount = 2`.
- **Crouch** (S, ↓, touch B-button held): if `Player.state == "grounded"` → set `state = "crouching"`, `crouchHeight = 28`, `vx` cap = 140. Release → restore height 48, `state = "grounded"`. While crouching, hitbox shrinks to 28 px tall (passes under 32-px gaps).
- **Gravity**: every frame, `vy += 1400 * dt`. Terminal vy = 700 px/s.
- **One-way platforms**: if `vy > 0` AND player bottom was above platform top last frame → land. If player presses S while on one-way → fall through (set `vy = 60`, disable platform collision for 0.2 s).
- **Crumble platforms**: when player lands on `type == "crumble"`, start `crumbleTimer`. At 1.5 s, platform is removed; player falls.
- **Level bounds**: clamp `Player.x` to [40, levelWidth − 40]. If `Player.y > levelHeight + 100` → instant death (pit).

## Combat

**RULES (player-triggered):**

- **Fire** (mouse click / touch FIRE button / J key): if `AmmoPool[activeWeapon] > 0` AND `fireCooldown ≤ 0`:
  - Decrement ammo by 1.
  - Spawn `pelletsPerShot` projectile(s) at player muzzle offset (facing × 24 px, y − 8 px for standing; y − 4 for crouching).
  - Each projectile: velocity = `projSpeed` in facing direction ± `spread` random angle per pellet.
  - Set `fireCooldown = 1 / fireRate`.
  - Rail Lance: while `fireCooldown > 0`, player cannot move horizontally (recoil lockout 0.15 s of the 1.1 s cooldown).
  - Arc Burst: on projectile hit, if `chainRadius > 0`, find nearest other enemy within 90 px of impact → spawn secondary projectile toward it (damage × 0.6, one chain only).
- **Weapon Switch** (1/2/3/4 keys, or Q cycles, or touch weapon-wheel tap): set `activeWeapon` to chosen id if in `StageProgress.unlockedWeapons`. No cost, instant.

**RULES (automatic):**

- Projectile updates position by `projSpeed * dt`. Remove when `projectileLife` elapsed or hits solid platform.
- Projectile vs Enemy: subtract `damage` from `Enemy.hp`. If `pierceCount > 0`, decrement and continue; else remove projectile.

## DamageAndDeath

**RULES:**

- Player takes damage: subtract from `shield` first, then `hp`. Set `invulnTimer = 1.2`, `shieldRegenDelay = 0`. If `hp ≤ 0` → `state = "dead"`, lives − 1, respawn at stage checkpoint after 1.5 s fade.
- Shield regen: if `shieldRegenDelay ≥ 2.0` AND `shield < 50` → `shield += 12/s`. Reset `shieldRegenDelay` to 0 on any hit.
- Contact damage from enemies: if player hitbox overlaps enemy hitbox AND `invulnTimer ≤ 0` → apply `Enemy.damage`.
- Hazard damage per Hazard record.
- Lives = 0 → "Game Over" screen → restart current world at Stage 1 with full HP/shield and default ammo.

## EnemyAI

**RULES (automatic, per enemy, each frame):**

- **Perception**: compute distance from enemy to player. If `dist ≤ aggroRange` AND enemy.state ≠ "dead" → `state = "chase"`. Else if `state == "chase"` AND `dist > aggroRange × 1.4` → revert to "patrol".
- **Patrol** (drone, runner): move at `vx` in `patrolDir`. Reverse `patrolDir` after traveling `patrolRange` from spawn or at platform edge.
- **Drone chase**: move toward player at `vx` with sine vertical bob (amplitude 12 px, period 1.0 s). Stop at 100 px from player. Fire 1 slow bullet (speed 180, damage 10) every `attackCooldown`.
- **Sentry chase**: rotate to face player. Fire aimed bullet (speed 300, damage 15) every `attackCooldown`.
- **Runner chase**: set `vx` toward player at 160. On contact → deal 18 damage, play 0.4 s lunge animation, reset cooldown.
- **Mine**: static. If player center within 60 px → begin 0.6 s fuse → explode: deal 35 damage to player if within 70 px radius; destroy self.
- **Shieldbot chase**: shuffle toward player at 60. Frontal hitbox (32 px wide) blocks projectile damage; rear/above hitbox takes full damage. Contact deals 20. Slam attack every 2.0 s: 0.3 s windup, then 0.2 s active (damage 20, radius 50 px, knockback player 120 px/s away).

## BossAI

**RULES (automatic, per boss, each frame):**

- Boss is stationary (or moves per attack). Player must dodge and shoot.
- Phase advances when `Boss.hp ≤ phaseTransitionHP` → 1.0 s invulnerable transition flash, then new attack set enabled.
- Execute attack list on timers as specified. All attacks deal damage to Player if hitbox overlaps.
- Boss hitbox: 80×100 px (Custodian), 90×120 px (Architect). Player projectiles deal `Weapon.damage` normally. Rail Lance pierce does NOT pierce the boss (treated as 1 hit).
- On `Boss.hp ≤ 0`: play 3 s death sequence, spawn "extraction pad" → StageFlow advances.

## PickupAndAmmo

**RULES:**

- Player hitbox overlaps Pickup → apply effect, remove Pickup, play collect sound.
- Ammo pickups add `amount` to corresponding `AmmoPool` entry, capped at max.
- Health pickup: `hp = min(hp + 25, 100)`.
- Shield pickup: `shield = min(shield + 20, 50)`.
- Coin: increment `ScoreBoard.coinsCollected`.
- Pickup respawn: NONE within a stage. Once collected, gone until stage restart.

## LevelGenerator (SEEDED GENERATOR)

**Parameters**: `LevelSeed` (int), `world` (1–2), `stage` (1–5), `difficultyScale` (1.0 default, 1.4 in NG+).

**Places, in order:**

1. **Floor/ground**: continuous solid platform at y = 480 (level height 560), width = 3200 px (stages 1–4) or 1600 px (boss stage 5). Gaps: place `gapCount` gaps of width 48–96 px, spaced every 300–500 px. `gapCount = 4 + stage + world` (stage 1 W1 → 6 gaps; stage 4 W2 → 10 gaps). Pit below gap = instant death.

2. **Mid-platforms**: `platCount = 6 + stage × 2` one_way and solid platforms, y ∈ {320, 384, 256}, x spaced 200–400 px apart, w ∈ {64, 96, 128, 192}. Crumble platforms: `crumbleCount = 2 + stage` placed at y=256 only.

3. **Upper platforms / ceilings**: `ceilCount = 3 + stage` solid slabs at y ∈ {128, 160}, w ∈ {96, 128}, forcing crouch passages (gap height = 32 px between slab and lower platform).

4. **Enemies**: spawn list = `enemyCount = 5 + stage × 2 + (world × 3)` enemies. Distribute types by world:
   - World 1: 40% drone, 30% runner, 20% sentry, 10% mine.
   - World 2: 20% drone, 25% runner, 25% sentry, 15% mine, 15% shieldbot.
   Place at x ∈ {400 … levelWidth−200}, y on nearest platform surface. Aggro ranges apply.

5. **Hazards**: `hazardCount = 2 + stage` spikes (placed in gap edges or on floor) + 1 laser_gate per stage (at x ∈ {800, 1600, 2400}, period 2.0 s). World 2 adds acid_pool in 1 gap.

6. **Pickups**: 2 ammo (random type, weighted toward active weapon), 1 health, 1 shield, 6–10 coins scattered on platforms and in air pockets.

7. **Checkpoint**: solid flag at x = levelWidth × 0.5 (stage 3+ only). Touching sets respawn point.

8. **Extraction pad**: at x = levelWidth − 80, y = 480. Triggers StageFlow on overlap.

9. **Weapon unlock crates** (fixed): Stage 1 World 1 → none. Stage 2 World 1 → Scatter Cannon. Stage 3 World 1 → Arc Burst. Stage 4 World 1 → Rail Lance. Stages in World 2 → ammo/health only.

**VERIFIER**: (a) No enemy or hazard placed inside a solid platform. (b) Every gap is jumpable: max gap width ≤ 96 px AND a platform exists within 120 px horizontal reach at a height the player can jump to. (c) At least 1 health pickup before the midpoint of any stage. (d) Crouch passages are passable: clearance ≥ 28 px. (e) No pickup is unreachable (verify path exists from ground to pickup y using max jump height 180 px). **If any check fails, re-roll with the next seed (seed+1) and regenerate.**

## StageFlow

**RULES:**

- Touch Extraction Pad → stage complete → show Stage Clear screen → advance `currentStage`.
- If `currentStage > 5` → advance `currentWorld`, reset `currentStage = 1`. If `currentWorld > 2` → Game Complete screen.
- Boss stages (stage 5): level is arena-only (1600 px wide, flat floor, 4 one-way platforms at corners). No extraction pad; defeating boss triggers clear.
- Death: respawn at checkpoint (or stage start if before checkpoint). Lives − 1. If lives = 0 → Game Over.

## Scoring

**RULES:**

- Stars per stage: 1 star = clear. 2 stars = clear + ≥ 60% enemies killed. 3 stars = clear + ≥ 60% enemies killed + all coins + time ≤ par_time.
- `par_time` = 45 s + stage × 10 s (stage 1 = 55 s, stage 5 = 95 s).
- Total stars tracked on ScoreBoard; shown on world-select and end screen.

---

# 4. PROGRESSION AND DIFFICULTY

**Unlock order:**
- Start: Pulse Rifle only, 120 ammo, 100 HP, 50 shield, 3 lives.
- Stage 1-2 (World 1, Stage 2): Scatter Cannon unlocked, +24 shells.
- Stage 1-3 (World 1, Stage 3): Arc Burst unlocked, +40 cells. Checkpoint introduced.
- Stage 1-4 (World 1, Stage 4): Rail Lance unlocked, +10 charges.
- Stage 1-5: Boss 1 (Custodian, 600 HP).
- Stage 2-1 through 2-4: All four weapons available; ammo refills to start values each stage; enemy density and HP × 1.2 (World 2 baseline).
- Stage 2-5: Boss 2 (Architect, 1100 HP). Game ends.

**Difficulty curve (numbers that make early easy, late hard):**
- W1S1: 7 enemies, 6 gaps, 2 hazards. Player learns movement + pulse rifle. Very forgiving.
- W1S3: 11 enemies, 8 gaps, 4 hazards, checkpoint. Introduces shieldbot? No—shieldbots are W2. Introduces mines + crouch passages.
- W1S4: 13 enemies, 10 gaps, 5 hazards. Rail Lance introduced here; player must use it to pierce drone clusters.
- W2S1: 10 enemies (now includes shieldbots), 7 gaps, 3 hazards + acid. HP of all enemies × 1.2.
- W2S4: 16 enemies, 10 gaps, 6 hazards. All enemy types mixed.
- Bosses: phase 2 adds charge/teleport; phase 3 adds summons. Player must manage ammo across 4 weapons to sustain DPS.

**Where the player is expected to fail:**
- Boss phase 3 (both bosses): first attempt likely results in death. Recovery: respawn at stage start (full ammo), lives − 1. Player learns attack patterns.
- Crouch-passage sequences in W2: first-time players die to a laser_gate they can't see while crouched. Recovery: checkpoint at mid-stage means only half the stage replays.
- If all 3 lives lost: Game Over → restart current world at Stage 1, ammo reset, lives reset to 3. No permanent loss.

**NG+**: unlocked after full clear. All enemy HP × 1.4, enemy count × 1.3, boss HP × 1.3, par_times reduced 20%. Ammo caps unchanged.

---

# 5. FEEL

| Parameter | Value | Tuned to achieve |
|---|---|---|
| Player run speed | 280 px/s | Fast enough to feel momentum, slow enough to aim shots |
| Crouch speed | 140 px/s | Half-speed forces deliberate crouch traversal |
| Acceleration | 1800 px/s² | Reaches top speed in ~0.16 s; snappy start |
| Deceleration | 2400 px/s² | Stops in ~0.12 s; responsive feel, no ice-skating |
| Jump velocity | −480 px/s | ~180 px peak height; clears 2-tile gaps comfortably |
| Double-jump velocity | −400 px/s | Slightly weaker; feels like a second push, not a reset |
| Gravity | 1400 px/s² | Snappy arc; fall from 180 px in ~0.5 s |
| Terminal velocity | 700 px/s | Prevents infinite fall speed; pits feel deadly |
| Coyote time | 0.08 s | Walk off edge → can still jump; forgiving |
| Jump buffering | 0.10 s | Press jump just before landing → jump fires on land |
| Fire rate feel (Pulse) | 7 shots/s | ~143 ms between shots; rapid but visible |
| Fire rate feel (Scatter) | 1.5 shots/s + 0.6 s cooldown | Pump-action rhythm; 0.6 s lockout = "rack the shotgun" |
| Rail Lance lockout | 0.15 s of 1.1 s | Brief movement freeze = weight of the shot |
| Knockback (enemy hit on player) | 120 px impulse, 0.15 s | Pushes player back visibly without losing control |
| Hit flash duration | 0.1 s white | Readable feedback without obscuring gameplay |
| Invulnerability after hit | 1.2 s | Enough to reposition; not so long it trivializes damage |
| Shield regen start | 2.0 s after hit | Creates tension window; rewards avoidance |
| Shield regen rate | 12 pts/s | Full shield in ~4.2 s of not being hit |
| Crumble platform timer | 1.5 s | Enough to jump off; punishes lingering |
| Laser gate period | 2.0 s (1.0 on / 1.0 off) | Readable rhythm; player learns the beat |
| Drone bullet speed | 180 px/s | Slow enough to dodge; fast enough to feel threatening |
| Sentry bullet speed | 300 px/s | Requires lateral movement or crouch to avoid |
| Boss slam shockwave speed | 200 px/s | Player must jump over; clear tell |
| Camera look-ahead | 120 px | Shows 1/3 of screen ahead; player sees enemies coming |
| Camera vertical dead-zone | ±80 px | Prevents jitter on small hops; activates on tall jumps |
| Death respawn fade | 1.5 s | Brief pause to register failure; not long enough to frustrate |
| Screen shake (explosion/hit) | 4 px, 0.15 s | Impact feedback without nausea |

---

# 6. HUD AND SCREENS

## Screen State Machine

```
TITLE → WORLD_SELECT → STAGE_PLAY → STAGE_CLEAR → (loop or) → WORLD_SELECT
                                          ↓
                                     GAME_OVER → TITLE
STAGE_PLAY → (lives=0) → GAME_OVER → TITLE
STAGE_PLAY → (boss dead, W2S5) → GAME_COMPLETE → TITLE
```

**TITLE**: Shows game name "GRIDFALL", "Press Enter / Tap to Start", best total stars if any save exists. Enter/Tap → WORLD_SELECT.

**WORLD_SELECT**: Shows 2 world slots (Floor 1, Floor 2). Floor 2 locked until Floor 1 boss defeated. Each world shows 5 stage icons with earned stars. Arrow keys / tap to select stage. Enter → STAGE_PLAY. Escape → TITLE.

**STAGE_PLAY**: The gameplay screen. HUD overlaid. Escape → PAUSE.

**PAUSE** (overlay on STAGE_PLAY): Shows "PAUSED", Resume (Escape/Enter), Restart Stage (R), Quit to World Select (Q). Escape again → resume.

**STAGE_CLEAR**: Shows stage name, clear time, enemies killed %, coins collected, stars earned (1–3). "Press Enter to continue." Enter → next stage STAGE_PLAY or WORLD_SELECT if boss.

**GAME_OVER**: "SYSTEM FAILURE — Lives exhausted." Shows stage reached. "Press Enter to restart world." Enter → WORLD_SELECT (stage 1 of current world).

**GAME_COMPLETE**: "SPIRE PURGE COMPLETE." Shows total stars (max 30), best time. "Press Enter to return to title." Enter → TITLE.

## Controls Summary (all screens)

| Input | STAGE_PLAY | Menus |
|---|---|---|
| A / ← / D / → | Move left / right | Navigate options |
| W / ↑ / Space | Jump | Confirm / select |
| S / ↓ | Crouch (hold) | Navigate down |
| 1 / 2 / 3 / 4 | Switch weapon | — |
| Q | Cycle weapon | Quit to World Select (Pause) |
| Mouse click / J / Touch FIRE | Shoot | — |
| Touch joystick | Move | — |
| Touch A / B | Jump / Crouch | — |
| Escape | Pause / Resume | Back / Quit |
| Enter | — | Confirm |
| R | Restart stage (Pause) | — |

## HUD (visible during STAGE_PLAY)

| Element | Record Field Shown | Visibility |
|---|---|---|
| HP bar (left, 120 px wide, green→red) | `Player.hp` / 100 | Always |
| Shield bar (below HP, blue, 120 px) | `Player.shield` / 50 | Always (dimmed if 0) |
| Lives counter (3 small icons, top-left) | `StageProgress.lives` | Always |
| Weapon name + ammo count (bottom-left) | `StageProgress.activeWeapon` + `AmmoPool[activeWeapon]` | Always |
| Weapon icon row (4 slots, active highlighted) | `StageProgress.unlockedWeapons` | Always; locked slots show "?" |
| Stage indicator (top-center: "W1-S3") | `StageProgress.currentWorld` / `currentStage` | Always |
| Timer (top-right, counts up) | `ScoreBoard.clearTime` | Always |
| Coin count (top-right, below timer) | `ScoreBoard.coinsCollected` | Always |
| Boss HP bar (top-center, wide, appears in stage 5) | `Boss.hp` / `Boss.maxHP` | Boss stage only, from first player contact with arena |
| Checkpoint flash (brief "CHECKPOINT" text) | Triggered on touch | 1.0 s on activation |
| Low-ammo warning (weapon icon pulses red) | `AmmoPool[activeWeapon] ≤ 10%` of max | While condition true |