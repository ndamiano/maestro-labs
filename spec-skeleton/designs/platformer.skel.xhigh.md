# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Side-scrolling platformer shooter | section 4, scene layout, stage component, player component, weapon component |
| At least 4 different gun types | section 4.3, weapon component, global gun roster |
| Character can move left or right | section 4.1, player component, input component |
| Character can jump | section 4.1, player component |
| Character can crouch | section 4.1, player component, collision rules |
| Story progression with worlds and stages | section 4.6, stage/world data, progression component |
| Start with 2 worlds and 5 stages each | section 4.6, stage table, progression rules |
| Do not simply copy Mario | section 4, section 5, original setting, enemy roster, objective style, gun variety |
| Clear, testable core loop | section 4, section 8, section 9 |
| HUD and screen flow | section 7, UI component |
| Sound feedback | section 6, audio component |
| Deterministic simulation and direct debug controls | section 2.2, section 8, section 9 |
| Enemies and challenge | section 4.4, enemy component |
| Bosses at world endings | section 4.4, boss rules, stage table |
| Pickups and energy | section 4.5, pickup component |
| Score and lives | section 4.7, progression component |
| Crouch can pass low gaps | section 1.2, section 4.1 |
| Camera follows the player through the stage | section 4.1, camera component |
| Stage select progression | section 7, progression component |
| Lighting and readable scene | section 3 |

## 0.2 Tiers

| Tier | Purpose | Features |
| --- | --- | --- |
| T1 — Must Ship | The game is playable start to finish and satisfies the user request. | 10 stages, 2 worlds, player movement, jump, crouch, 4 guns, basic enemies, 3 nodes per stage, exit, stage clear, title, HUD, game over, Web Audio SFX, debug API, core tests. |
| T2 — Quality | Makes the loop feel polished and readable. | Bosses, checkpoints, score bonuses, stage select, gun slots, enemy projectile warning, particles, music loop, pause screen, world complete screen, final complete screen. |
| T3 — Stretch | Optional expansion after the core is stable. | 5th gun, moving platforms, screen shake, extra enemy variants, local high score list, replay from stage, visual theme variants. |

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Convention | Value |
| --- | --- |
| Frame rate | 60 fixed logic ticks per second |
| Tick | `1/60` second |
| Tile size | 32 logical pixels |
| Viewport | 30 tiles wide by 18 tiles tall |
| Axis X | right is positive |
| Axis Y | down is positive |
| Coordinate unit | tiles, floating point |
| Object positions | center point in tiles |
| Ground top | `y = 16` |
| Stage height | 18 tiles |
| Player width | 0.8 tile |
| Player stand height | 2.6 tiles |
| Player crouch height | 1.4 tiles |
| Player stand center above feet | 1.3 tiles |
| Player crouch center above feet | 0.7 tiles |
| Player run speed | 7 tiles/second |
| Player crouch speed | 3 tiles/second |
| Player air control speed | 6 tiles/second |
| Jump initial velocity | 17 tiles/second upward |
| Gravity | 45 tiles/second² downward |
| Max fall speed | 30 tiles/second |
| Coyote time | 0.10 second |
| Jump buffer | 0.15 second |
| Player start position | `x = 2`, `y = 14.7` |
| Project radius | 0.25 tile |
| Enemy contact damage | 1 unless noted |
| Player max HP | 3 |
| Player invulnerability | 1.5 seconds after damage |
| Max vertical step | 3 tiles |
| Max horizontal gap | 4.5 tiles |
| Low ceiling gap | 2 tiles tall |
| Crouch clearance | 1.4 tile height fits under a 2-tile gap |
| Stand clearance | 2.6 tile height does not fit under a 2-tile gap |

## 1.2 Important conventions

- The game world is a single side-scrolling stage at a time.
- The player normally moves right toward the exit, but may move left freely.
- Stages are horizontal, mostly 80 to 160 tiles wide.
- The stage is bounded by invisible walls at `x = 0` and `x = stage width`.
- Falling below `y = stage height + 2` causes a pit damage event: lose 1 HP and respawn at the last checkpoint.
- Checkpoints are placed at roughly 50% of non-boss stages and before boss arenas.
- Every stage has exactly 3 signal nodes.
- The exit opens only after all 3 signal nodes are collected.
- The exit is a rectangle. Overlapping an open exit completes the stage.
- The simulation never reads real time. Time advances only through step or direct time calls.
- One random source is used for all generated randomness.
- All named things must exist in the roster below or be placed by the stage generator.

### Roster

| Category | Kinds |
| --- | --- |
| Tile kinds | `solid`, `oneWay`, `spike` |
| Pickup kinds | `heart`, `energy`, `chip`, `signalNode` |
| Enemy kinds | `mite`, `hound`, `sentry`, `shrike`, `golem`, `tyrant`, `loom` |
| Gun kinds | `pulse`, `scatter`, `rail`, `orbit` |
| Projectile kinds | `pulse`, `scatter`, `rail`, `orbit`, `enemyPulse`, `enemyShell`, `bossShot` |
| Screen modes | `title`, `select`, `play`, `pause`, `clear`, `gameover`, `complete` |

# 2. CONTRACTS

## 2.1 Component layout

| Component | Responsibility | Consumes / Produces |
| --- | --- | --- |
| Core | Owns mode, simulation clock, update order, draw request, debug entry point. | Reads all state, writes mode and time, calls all systems. |
| Input | Holds persistent player intents: move, jump, crouch, fire, gun select. | Writes to input state, read by player and weapon systems. |
| Stage | Loads stage layout, tiles, hazards, nodes, checkpoint, exit, and generated enemies/pickups. | Writes stage records, produces spawn records. |
| Player | Movement, jump, crouch, collision, HP, energy, checkpoint, damage. | Reads input and stage, writes player state, emits damage and collection events. |
| Weapon | Gun specs, cooldowns, energy spend, projectile spawn. | Reads player and input, writes projectile state. |
| Projectile | Integrates projectiles, handles homing, pierce, lifetime, collisions. | Reads enemies/player/stage, writes damage events. |
| Enemy | Enemy state machines, boss phases, contact damage, enemy projectile firing. | Reads player and stage, writes enemy state and projectiles. |
| Pickup | Pickup bobbing, collection, node counting, score, hearts, energy. | Reads player, writes pickup and player state. |
| Camera | Follows player with deadzone and stage clamps. | Reads player and stage, writes camera offset. |
| Renderer | Draws background, tiles, entities, effects, and lighting. | Reads all visible state, produces visual output. |
| UI | DOM/CSS overlay screens and HUD. | Reads mode and key state, writes mode transitions. |
| Audio | Web Audio SFX and music flags. | Reads events and mode, produces sound. |

## 2.2 Global context

All systems consume one shared game state object. No system should keep hidden authoritative state outside this object.

| Record | Fields |
| --- | --- |
| Game | `mode`, `world`, `stage`, `time`, `score`, `lives`, `seed`, `unlockedGuns`, `currentGun`, `nodes`, `stageSelectUnlocked` |
| Input | `move`, `jump`, `crouch`, `fire` |
| Player | `x`, `y`, `vx`, `vy`, `facing`, `onGround`, `crouching`, `height`, `hp`, `maxHp`, `energy`, `maxEnergy`, `invuln`, `coyote`, `jumpBuffer`, `checkpointX`, `checkpointY`, `cooldowns` |
| Player.cooldowns | `pulse`, `scatter`, `rail`, `orbit` |
| Enemy | `id`, `kind`, `x`, `y`, `w`, `h`, `vx`, `vy`, `hp`, `maxHp`, `facing`, `state`, `stateTimer`, `hitTimer`, `phase`, `score`, `dead` |
| Projectile | `id`, `owner`, `kind`, `x`, `y`, `vx`, `vy`, `w`, `h`, `dmg`, `pierce`, `lifetime`, `hitIds`, `targetId` |
| Pickup | `id`, `kind`, `x`, `y`, `collected`, `bobTimer` |
| Exit | `x`, `y`, `open`, `anim` |
| StageMeta | `id`, `name`, `width`, `height`, `checkpointX`, `checkpointY`, `exitX`, `exitY` |
| Camera | `x`, `y` |
| Audio | `musicPlaying`, `muted` |

`stageSelectUnlocked` is an integer representing the furthest cleared stage, encoded as `world * 100 + stage`.

## 2.3 System signatures

These are behavior contracts, not implementation code.

- `loadStage(world, stage)`  
  Builds stage meta, tiles, hazards, nodes, checkpoint, exit, enemies, and pickups using the current seed.

- `updatePlayer(dt)`  
  Applies movement, jump, crouch, gravity, collision, checkpoint, and damage timers.

- `tryFire(gun)`  
  If fire is held, gun is unlocked, cooldown is ready, and energy is sufficient, subtract energy, set cooldown, and spawn the gun’s projectile pattern.

- `updateProjectiles(dt)`  
  Moves projectiles, applies homing for `orbit`, applies pierce, applies lifetime removal, and resolves collisions with stage and entities.

- `updateEnemies(dt)`  
  Runs enemy state machines, boss phases, contact damage, and enemy projectile firing.

- `damageEntity(target, amount, source)`  
  Applies damage to player or enemy, sets hit timers, reduces HP, handles death or game over.

- `collectPickup(pickup)`  
  Applies pickup effect, score, node count, energy, HP, and removal.

- `completeStage()`  
  Applies score bonus, advances progression, unlocks the next gun if the cleared stage grants one, and moves to the next screen.

- `respawnPlayer()`  
  Places player at checkpoint, keeps HP if above zero, sets invulnerability.

# 3. VISUAL SPEC

The game is a crisp side-scrolling neon-industrial scene: a small courier moves through copper, teal, and charcoal districts, shooting rusted machines while collecting glowing signal nodes. The visual language is flat vector with strong readable silhouettes: dark backgrounds, bright cyan player energy, warm orange hazards, red enemy eyes, and saturated pickup colors. The scene should feel like a handcrafted browser action game, not a pixel-perfect platform classic.

Lighting is a fixed top-left key light with soft ambient shadow. The player has a cyan rim glow. Projectiles emit additive bloom. Hazards and spikes emit a faint orange flicker. Nodes pulse with a slow cyan breath. The exit emits a steady teal glow when closed and a brighter green pulse when open. Background layers are darker and lower contrast than the play area so gameplay remains the brightest thing on screen.

## 3.1 Scene geometry and parallax

- Foreground play area uses tile rectangles for solids, one-way platforms, and spikes.
- Midground contains pipes, cables, crates, and gantries, scrolling at 50% speed.
- Background contains distant skyline, windows, or spires, scrolling at 25% speed.
- World 1 uses copper pipes, scrap piles, rusted catwalks, and warm warning stripes.
- World 2 uses glass panels, floating spires, thin clouds, and brighter cyan/white light.
- Low ceiling gaps are exactly 2 tiles tall and are visually readable by the gap above the player’s standing height.
- Boss arenas have a slightly darker floor, visible boundary walls, and a larger background emblem.

## 3.2 Texture and color table

| Surface / Object | Base Color | Accent / Glow | Notes |
| --- | --- | --- | --- |
| Solid tile | `#2b3a4a` | cyan top edge `#48f7ff` | Main floor and walls. |
| One-way platform | `#3b4d63` | yellow stripe `#ffd166` | Can jump up through from below. |
| Spike | `#ff6b35` | dark base `#3a1f17` | Damage hazard. |
| Node | `#66ffe3` | pulsing white core | 0.9 tile diamond. |
| Exit closed | `#00b8a9` | dim teal glow | Rectangle door. |
| Exit open | `#7dffb8` | strong green pulse | Animated glow. |
| Heart | `#ff4d6d` | white highlight | 0.8 tile heart. |
| Energy cell | `#ffe066` | white core | 0.8 tile rounded cell. |
| Score chip | `#8aff80` | dark edge | 0.7 tile chip. |
| Player jacket | `#ff9f1c` | cyan visor `#a8f0ff` | Small rounded silhouette. |
| Enemy base | `#607d8b` | rust `#8d6e63` | Machine shapes. |
| Enemy eye | `#ffeb3b` | red when hit | Contact damage indicator. |
| Boss core | `#ff5252` | white pulse | Large central damageable core. |

## 3.3 Character and enemy art

- Player is a compact rounded body with a visor, small backpack, and wrist blaster.
- The player should be readable against all backgrounds: bright jacket, dark boots, cyan visor.
- Enemies are machines with simple shapes and one clear eye or core.
- Bosses are much larger than normal enemies and have a visible phase indicator.
- All enemy hit reactions should include a 0.08 second white flash.
- All enemy deaths should produce a small burst of rust shards and a score popup.

## 3.4 Effects

- Muzzle flash: 0.05 second bright burst at the player’s gun position.
- Bullet trails: additive trail behind each projectile.
- Impact sparks: small colored particles matching the projectile owner.
- Node collection: cyan ring expands upward.
- Exit opening: door slides open with green glow.
- Player damage: red vignette pulse and player blink for invulnerability.
- Boss phase: large colored banner and boss core color change.

# 4. GAMEPLAY SPEC

The most important feeling is fast, readable progression: run right, choose the right gun, collect 3 signal nodes, and reach the exit. Combat is important but never mandatory; the player can dodge enemies and still complete stages. Guns should feel different: `pulse` is quick and safe, `scatter` wins close fights, `rail` punishes lined-up enemies, and `orbit` handles air and crowded spaces. Worlds introduce new layouts, hazards, enemies, and guns, while stages within a world increase distance, enemy count, and platforming demand.

## 4.1 Player Controller

### Controls

| Action | Keys |
| --- | --- |
| Move left | `A` or `Left` |
| Move right | `D` or `Right` |
| Jump | `W`, `Up`, or `Space` |
| Crouch | `S` or `Down` |
| Fire | `J` or `X` |
| Cycle gun | `Q` or `E` |
| Quick select gun 1 | `1` |
| Quick select gun 2 | `2` |
| Quick select gun 3 | `3` |
| Quick select gun 4 | `4` |
| Pause | `Esc` or `P` |

### Movement rules

- Move direction persists until changed.
- Horizontal speed is set directly to the movement target for deterministic simulation.
- Running speed is 7 tiles/second.
- Crouching speed is 3 tiles/second.
- Air control uses 6 tiles/second toward the input direction.
- Crouch changes player height from 2.6 to 1.4 tiles.
- Crouching in the air cancels downward velocity by setting `vy = 0` while held.
- Crouching on the ground allows passing under 2-tile gaps.
- Standing height cannot pass under a 2-tile gap.
- Jump is available when on ground or within coyote time.
- Jump can be buffered up to 0.15 seconds before landing.
- Releasing jump early while moving upward multiplies upward velocity by 0.45 for variable jump height.
- The player faces left or right based on last horizontal input.
- If no horizontal input is held, the player keeps its last facing direction.

### Collision and damage

- Player collides with solid tiles, spikes, enemies, and projectiles.
- One-way platforms support the player only when the player is falling and its feet were above the platform top in the previous tick.
- Player damage sets HP minus 1, invulnerability 1.5 seconds, and a small knockback away from the source.
- If HP reaches 0, mode becomes `gameover`.
- If the player falls below the stage, the player loses 1 HP and respawns at the checkpoint.
- If HP is already 1 when falling, the player dies and mode becomes `gameover`.

## 4.2 Hazards and Damage

| Hazard | Effect |
| --- | --- |
| Spike tile | 1 damage, bounces player upward slightly. |
| Pit | 1 damage, respawn at checkpoint. |
| Enemy contact | Enemy contact damage, usually 1. |
| Enemy projectile | 1 damage unless boss special. |
| Boss contact | 1 damage. |
| Boss heavy attack | 1 damage with stronger knockback. |

## 4.3 Weapons

The player starts with `pulse`. Other guns are unlocked by stage completion.

| Gun | Unlock | Damage | Cooldown | Rate | Projectile speed | Lifetime | Energy cost | Behavior |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `pulse` | Start | 1 | 0.10s | 10/second | 26 tiles/second | 1.2s | 2 | Single straight bolt, fast and reliable. |
| `scatter` | Clear W1S1 | 0.5 per pellet | 0.40s | 2.5/second | 18 tiles/second | 0.55s | 10 | 3 pellets spread across 24 degrees, strong close range. |
| `rail` | Clear W1S3 | 4 | 0.65s | about 1.54/second | 40 tiles/second | 1.0s | 20 | Piercing bolt, pierce value 1, strong against aligned enemies. |
| `orbit` | Clear W2S1 | 1 per orb | 0.55s | about 1.82/second | 14 tiles/second | 1.6s | 14 | 3 homing orbs, target nearest enemy within 12 tiles, otherwise fly straight. |

### Energy rules

- Player max energy is 100.
- Energy regenerates at 25/second.
- Firing is blocked if energy is below the gun’s cost.
- Energy does not regenerate while in `pause`, `clear`, `gameover`, or `complete`.
- Energy pickups add 25 energy and clamp at 100.

### Gun switching

- `Q` cycles left, `E` cycles right through unlocked guns.
- `1` through `4` select unlocked guns directly.
- Switching does not interrupt the current projectile.
- Each gun has its own cooldown timer.
- If a gun is not unlocked, selecting it does nothing.

## 4.4 Enemies and Bosses

### Standard enemies

| Enemy | HP | Score | Contact | Behavior |
| --- | --- | --- | --- | --- |
| `mite` | 1 | 100 | 1 | Walks horizontally, turns at walls and edges. Speed 2.5 tiles/second. |
| `hound` | 3 | 200 | 1 | Hops or dashes toward player when within 8 tiles. Speed 8 tiles/second while dashing. |
| `sentry` | 4 | 250 | 1 | Stationary turret. If player within 10 tiles, fires 3 `enemyPulse` projectiles every 1.6 seconds. |
| `shrike` | 2 | 150 | 1 | Flying enemy. Moves in a sine wave around a patrol center. Speed 4 tiles/second. |
| `golem` | 8 | 400 | 1 | Slow heavy enemy. Throws 2 arcing `enemyShell` projectiles every 2.5 seconds when player within 12 tiles. |

### Bosses

| Boss | Stage | HP | Score | Behavior |
| --- | --- | --- | --- | --- |
| `tyrant` | W1S5 | 60 | 2000 | Ground boss. Phase 1: walks and fires bursts. Phase 2 at 66% HP: faster, fires spread. Phase 3 at 33% HP: charges and summons up to 2 `mite` enemies every 8 seconds. |
| `loom` | W2S5 | 70 | 2000 | Flying boss. Phase 1: flies in arcs and fires rings of `bossShot`. Phase 2 at 66% HP: faster arcs and fires 2 rings. Phase 3 at 33% HP: vertical sweep with a telegraphed laser sweep lasting 1.2 seconds after 0.8 seconds warning. |

Boss rules:

- Boss appears when player enters the boss arena.
- Boss HP bar appears at the top of the HUD.
- Boss phase changes play `bossAlert` and change the boss core color.
- Boss contact damage is 1.
- Boss death clears the exit gate if nodes are complete.

## 4.5 Pickups and Energy

| Pickup | Effect | Score |
| --- | --- | --- |
| `heart` | +1 HP, clamps at 3. No effect at full HP. | 50 |
| `energy` | +25 energy, clamps at 100. | 50 |
| `chip` | Score only. | 50 |
| `signalNode` | Increases `nodes` by 1, clamps at 3. | 500 |

Pickup rules:

- Pickups bob vertically with a 1 second sine wave.
- A pickup is collected when its rectangle overlaps the player rectangle.
- Collected pickups are removed from the active pickup list.
- Signal nodes are the only required pickups for stage completion.
- Hearts and energy are optional and placed so no stage requires them to finish.

## 4.6 Worlds, Stages, Objectives, Progression

### World 1 — Copper Gutter

A ground-level scrap district. Theme: rust, pipes, scrap, warning stripes.

| Stage | Name | Width | Enemy roster | Nodes at x | Checkpoint | Exit | Unlock after clear |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| 1-1 | Gutter Alley | 80 | `mite` x4, `shrike` x2 | 16, 40, 64 | 40 | 76 | `scatter` |
| 1-2 | Scrap Docks | 96 | `mite` x6, `hound` x2, `shrike` x2 | 20, 48, 76 | 48 | 92 | none |
| 1-3 | Rust Foundry | 112 | `hound` x4, `sentry` x2, `shrike` x3 | 24, 56, 88 | 56 | 108 | `rail` |
| 1-4 | Pipeworks | 128 | `mite` x4, `hound` x3, `sentry` x2, `shrike` x3 | 28, 64, 100 | 64 | 124 | none |
| 1-5 | Gutter Gate | 144 | `tyrant` boss | 104, 120, 136 | 96 | 140 | none |

### World 2 — Aurora Spire

A brighter sky district. Theme: glass, light, floating platforms, cyan sky.

| Stage | Name | Width | Enemy roster | Nodes at x | Checkpoint | Exit | Unlock after clear |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| 2-1 | Spire Base | 96 | `mite` x6, `shrike` x4, `sentry` x2 | 18, 48, 78 | 48 | 92 | `orbit` |
| 2-2 | Cloudworks | 112 | `hound` x4, `shrike` x3, `golem` x1 | 22, 56, 90 | 56 | 108 | none |
| 2-3 | Crystal Loom | 128 | `hound` x3, `sentry` x3, `shrike` x4 | 26, 64, 100 | 64 | 124 | none |
| 2-4 | Storm Rail | 144 | `golem` x1, `hound` x4, `shrike` x4 | 28, 72, 116 | 72 | 140 | none |
| 2-5 | Sky Loom | 160 | `loom` boss | 114, 132, 150 | 108 | 156 | none |

### Stage generation rules

- Stage generator uses the current seed to place layout variations, but stage table values are fixed.
- Ground exists at `y = 16` from `x = 0` to `x = width`.
- One-way platforms are placed every 12 tiles at `y = 13`, with 4-tile wide segments.
- High platforms are placed at `y = 10` near each node if the node is elevated.
- Spike sections are 2 tiles wide and placed on the ground at stage-specific safe intervals.
- Low ceiling gaps are 2 tiles tall and appear at roughly 30% and 70% of non-boss stages.
- Enemies are not placed in the first 8 tiles from the player start.
- Flying enemies patrol around the nearest node or platform center.
- Ground enemies stand on the nearest solid surface below their assigned x.
- Boss stages replace most regular enemies with the boss and a few summoned adds only during boss phases.
- Pickup placement per stage:
  - Non-boss stage: 5 `energy`, 1 `heart`, 4 `chip`, 3 `signalNode`.
  - Boss stage: 7 `energy`, 2 `heart`, 6 `chip`, 3 `signalNode`.
- Score chips are placed on optional platforms or small ledges, not on the required node path.

### Progression rules

- `start()` begins at W1S1 in `play` mode.
- Clearing a stage advances to the next stage.
- Clearing W1S5 advances to W2S1.
- Clearing W2S5 advances to `complete`.
- Gun unlocks are permanent for the current session.
- Stage select unlocks the next stage after a stage is cleared.
- The player can restart the current stage from pause or game over.
- Restarting a stage resets stage-local entities, keeps unlocked guns, keeps score, and sets player HP to 3.

## 4.7 Scoring, Lives, Game Over

| Event | Score |
| --- | ---: |
| `mite` kill | 100 |
| `shrike` kill | 150 |
| `hound` kill | 200 |
| `sentry` kill | 250 |
| `golem` kill | 400 |
| Boss kill | 2000 |
| Pickup | 50 |
| Signal node | 500 |
| Stage clear time bonus | `max(0, 1000 - floor(stage time) * 10)` |

Lives rules:

- Player starts with 3 lives.
- A life is lost only when HP reaches 0.
- After a stage restart, HP is restored to 3.
- If lives reach 0 after a game over, the player returns to title.
- Every 20,000 score grants 1 life, capped at 5.

# 5. CHARACTERS

The player is Kite, a small courier in a patched copper jacket with a bright cyan visor. Kite is practical and quick, not heroic in a grand fantasy way; the character feels like a small person moving through a large, damaged machine-city. Enemies are rusted machines, not human villains: twitchy mites, leaping hounds, mounted sentries, drifting shrikes, and heavy golems. Bosses are larger district machines that guard the exits, giving the world a sense of escalating infrastructure rather than a human war.

## 5.1 Animation requirements

### Player

| State | Visual requirement |
| --- | --- |
| Idle | Slight bob, visor glow, backpack sway. |
| Run | 4-frame cycle, legs and scarf move. |
| Jump | Body stretch, visor brighter. |
| Fall | Body compresses slightly, scarf lifts. |
| Crouch | Body lowers to 1.4 tile height, visor remains visible. |
| Shoot | Muzzle flash and arm/wrist blaster recoil. |
| Hurt | Red flash, brief stagger, blink during invulnerability. |
| Death | Short ragdoll-style fall and fade. |

### Enemies

| Enemy | Required animation states |
| --- | --- |
| `mite` | Walk, hit, death. |
| `hound` | Idle, leap, hit, death. |
| `sentry` | Rotate barrel toward player, fire, hit, death. |
| `shrike` | Fly sine, hit, death. |
| `golem` | Stomp, throw, hit, death. |
| `tyrant` | Walk, charge, fire burst, phase change, death. |
| `loom` | Fly arc, ring fire, laser telegraph, phase change, death. |

# 6. AUDIO

All sound is generated with the Web Audio API. No external assets are required.

| Sound | Recipe | Rule |
| --- | --- | --- |
| `titleTheme` | 90 BPM loop. Square bass at 110 Hz each beat. Triangle lead A4/C5/E5 every 2 beats. Noise hats on 16th notes at very low gain. | Play when mode is `title` or `select`. Stop on `play`, `pause`, `gameover`, `complete`. |
| `stageTheme` | 112 BPM loop. Square bass A2/C3 alternating. Triangle lead A4/D5/E5/G5. Noise hats on 16th notes. | Play when mode is `play` and no boss is active. Stop on `pause`, `clear`, `gameover`. |
| `bossTheme` | 128 BPM loop. Sawtooth bass A2. Square lead A4/A5. Noise crash each 2 bars. | Play when a boss is active and mode is `play`. Stop when boss dies or mode changes. |
| `ui` | Square 880 Hz, 0.06 second, fast exponential decay. | On any UI button press. |
| `jump` | Triangle 300 Hz to 600 Hz over 0.12 second, gain 0.2 to 0. | On successful jump start. |
| `land` | Sine 120 Hz, 0.08 second, short decay. | On landing from a jump. |
| `shootPulse` | Square 820 Hz, 0.05 second, sharp decay. | On each `pulse` shot. |
| `shootScatter` | Square 520 Hz, 0.08 second, three voices offset 0, 8, and 16 ms. | On each `scatter` volley. |
| `shootRail` | Sawtooth 180 Hz to 80 Hz over 0.2 seconds plus square 900 Hz for 0.04 seconds. | On each `rail` shot. |
| `shootOrbit` | Triangle 320 Hz to 640 Hz over 0.15 seconds, three voices. | On each `orbit` volley. |
| `enemyHit` | Square 220 Hz, 0.05 second, fast decay. | On enemy HP loss. |
| `enemyDie` | Sawtooth 160 Hz to 40 Hz over 0.18 seconds. | On enemy death. |
| `playerHurt` | Sawtooth 200 Hz to 60 Hz over 0.25 seconds. | On player damage. |
| `heart` | Sine 880 Hz to 1320 Hz over 0.12 seconds. | On heart pickup. |
| `energy` | Sine 520 Hz to 1040 Hz over 0.08 seconds. | On energy pickup. |
| `chip` | Square 1200 Hz, 0.05 second, fast decay. | On score chip pickup. |
| `node` | Three sine notes 660, 880, and 1100 Hz together for 0.25 seconds. | On signal node pickup. |
| `bossAlert` | Sawtooth 110 Hz for 0.8 seconds with 8 Hz tremolo. | On boss spawn and phase change. |
| `exitOpen` | Triangle 440 Hz to 880 Hz over 0.4 seconds. | On exit opening. |
| `gameOver` | Sine 220 Hz to 55 Hz over 0.6 seconds. | On game over. |

# 7. UX

The UI is a DOM/CSS overlay only. No menus or HUD elements are drawn into the game scene.

## 7.1 Title screen

- Shows game title: **Conduit Run**.
- Shows a Start button.
- Shows control list.
- Shows a subtle animated background matching World 1.
- Pressing Start calls the same action as the debug start path.

## 7.2 Stage select screen

- Shows 2 rows: World 1 and World 2.
- Each row has 5 stage buttons.
- Unlocked stages are bright; locked stages are dimmed with a lock marker.
- The current stage is highlighted.
- Selecting an unlocked stage starts that stage.

## 7.3 Play HUD

- Top left: 3 heart slots.
- Top left under hearts: energy bar, yellow fill.
- Top center: current gun name and four gun slot indicators.
- Top right: score, stage time, nodes `x/3`.
- Boss HUD: when active, boss name and HP bar appear below the top center HUD.
- Center messages: “Signal Node”, “Scatter Rig acquired”, “Rail Lance acquired”, “Orbit Cannon acquired”, “Exit Open”.

## 7.4 Pause screen

- Shown over gameplay.
- Buttons: Resume, Restart Stage, Return to Stage Select.
- Simulation does not advance while paused.

## 7.5 Stage clear screen

- Shows stage name.
- Shows score, time, enemies destroyed, score chips collected.
- Shows time bonus.
- Button: Continue.

## 7.6 World complete screen

- Shown after W1S5 before entering W2S1.
- Shows world name and a short story line.
- Button: Enter Next World.

## 7.7 Game over screen

- Shows “Conduit Lost”.
- Shows score.
- Buttons: Restart Stage, Return to Title.

## 7.8 Game complete screen

- Shows “Conduit Restored”.
- Shows total score.
- Button: Play Again.

# 8. DEBUG API

The game installs `window.__game`. All calls are synchronous and return plain data.

| Call | What it does | Returns |
| --- | --- | --- |
| `start()` | Enters play from title or select at the current stage. | `{ mode, world, stage }` |
| `seed(n)` | Sets the one random seed and rebuilds generated stage content if a stage is active. | `{ seed }` |
| `step(dt, n)` | Advances `n` ticks of `dt` seconds without waiting for real time, then draws once. | `{ time, mode, playerAlive }` |
| `setTime(t)` | Advances simulation to `t` seconds without drawing. | `{ time }` |
| `getState()` | Returns all record fields as plain data. | full state object |
| `setMove(dir)` | Sets persistent move direction: `-1`, `0`, or `1`. | `{ move }` |
| `setJump(down)` | Sets persistent jump state: `true` or `false`. | `{ jump }` |
| `setCrouch(down)` | Sets persistent crouch state: `true` or `false`. | `{ crouch }` |
| `setFire(down)` | Sets persistent fire state: `true` or `false`. | `{ fire }` |
| `setGun(name)` | Sets current gun if unlocked. | `{ gun }` |
| `unlockGun(name)` | Adds a gun to unlocked guns. | `{ unlockedGuns }` |
| `setStage(world, stage)` | Loads the given stage directly and enters play. | `{ mode, world, stage }` |
| `completeStage()` | Forces stage completion, applies progression and unlocks, and advances to the next state. | `{ mode, world, stage, unlockedGuns }` |
| `spawnEnemy(kind, x, y)` | Spawns an enemy of the given roster kind at a position. | `{ enemyId, hp }` |
| `spawnPickup(kind, x, y)` | Spawns a pickup of the given roster kind at a position. | `{ pickupId }` |
| `spawnProjectile(owner, kind, x, y, dir)` | Spawns a projectile. `dir` is `1` right or `-1` left. | `{ projectileId }` |
| `clearEnemies()` | Removes all active enemies. | `{ removed }` |
| `damagePlayer(n)` | Applies `n` damage to the player. | `{ hp, mode }` |
| `teleportPlayer(x, y)` | Moves the player to a position without collision. | `{ x, y }` |
| `setHp(n)` | Sets player HP, clamped to 0 through max HP. | `{ hp }` |
| `setEnergy(n)` | Sets player energy, clamped to 0 through 100. | `{ energy }` |
| `setNodes(n)` | Sets collected signal nodes, clamped to 0 through 3. | `{ nodes }` |
| `openExit(open)` | Forces exit open state. | `{ open }` |
| `setScore(n)` | Sets score. | `{ score }` |
| `setLives(n)` | Sets lives, clamped to 0 through 5. | `{ lives }` |
| `triggerBossPhase(phase)` | Sets boss phase if a boss is present. | `{ phase }` |

With `seed` and `step`, the same sequence of calls always yields the same state.

# 9. TESTS

Each check is a sequence of debug calls followed by the exact state that must be found.

1. `seed(7); start(); let s = getState();`  
   `s.mode === 'play'`, `s.world === 1`, `s.stage === 1`, `s.player.hp === 3`, `s.player.maxHp === 3`, `s.player.x === 2`, `s.player.y === 14.7`, `s.currentGun === 'pulse'`, `s.nodes === 0`, `s.exit.open === false`, `s.enemies.length === 6`, `s.projectiles.length === 0`.

2. `seed(7); start(); step(1/60, 60); let s = getState();`  
   `s.time === 1`, `s.mode === 'play'`, `s.player.x === 2`.

3. `seed(7); start(); setMove(1); step(1/60, 60); let s = getState();`  
   `s.player.x === 9`.

4. `seed(7); start(); setMove(0); setJump(true); step(1/60, 10); let s = getState();`  
   `s.player.onGround === false`, `s.player.y < 14.7`.  
   Then `setJump(false); step(1/60, 90); s = getState();`  
   `s.player.onGround === true`, `s.player.y === 14.7`.

5. `seed(7); start(); setCrouch(true); step(1/60, 1); let s = getState();`  
   `s.player.crouching === true`, `s.player.height === 1.4`.  
   Then `setCrouch(false); s = getState();`  
   `s.player.crouching === false`, `s.player.height === 2.6`.

6. `seed(7); start(); setFire(true); step(1/60, 12); let s = getState();`  
   `s.projectiles.length === 2`, every projectile has `owner === 'player'` and `kind === 'pulse'`.

7. `seed(7); start(); unlockGun('scatter'); setGun('scatter'); setFire(true); step(1/60, 12); let s = getState();`  
   `s.projectiles.length === 3`, every projectile has `kind === 'scatter'`.

8. `seed(7); start(); clearEnemies(); spawnEnemy('mite', 8, 15.5); spawnEnemy('mite', 9, 15.5); unlockGun('rail'); setGun('rail'); setFire(true); step(1/60, 30); let s = getState();`  
   `s.enemies.length === 0`, `s.score === 200`.

9. `seed(7); start(); clearEnemies(); unlockGun('orbit'); setGun('orbit'); setFire(true); step(1/60, 12); let s = getState();`  
   `s.projectiles.length === 3`, every projectile has `kind === 'orbit'`.

10. `seed(7); start(); setHp(1); damagePlayer(1); let s = getState();`  
   `s.mode === 'gameover'`, `s.player.hp === 0`.

11. `seed(7); start(); setHp(1); spawnPickup('heart', 3, 15.5); setMove(1); step(1/60, 30); let s = getState();`  
   `s.player.hp === 2`.

12. `seed(7); start(); setEnergy(75); spawnPickup('energy', 3, 15.5); setMove(1); step(1/60, 30); let s = getState();`  
   `s.player.energy === 100`.

13. `seed(7); start(); setNodes(0); spawnPickup('signalNode', 3, 15.5); setMove(1); step(1/60, 30); let s = getState();`  
   `s.nodes === 1`.

14. `seed(7); start(); setNodes(3); step(1/60, 1); let s = getState();`  
   `s.exit.open === true`.

15. `seed(7); start(); setScore(123); setLives(1); let s = getState();`  
   `s.score === 123`, `s.lives === 1`.

16. `seed(7); setStage(1, 1); completeStage(); let s = getState();`  
   `s.mode === 'play'`, `s.world === 1`, `s.stage === 2`, `s.unlockedGuns.includes('scatter') === true`.

17. `seed(7); setStage(1, 3); completeStage(); let s = getState();`  
   `s.world === 1`, `s.stage === 4`, `s.unlockedGuns.includes('rail') === true`.

18. `seed(7); setStage(1, 5); completeStage(); let s = getState();`  
   `s.world === 2`, `s.stage === 1`.

19. `seed(7); setStage(2, 5); completeStage(); let s = getState();`  
   `s.mode === 'complete'`.

20. `seed(7); setStage(1, 5); let s = getState();`  
   `s.enemies.length === 1`, `s.enemies[0].kind === 'tyrant'`, `s.enemies[0].phase === 1`.  
   Then `triggerBossPhase(2); s = getState();`  
   `s.enemies[0].phase === 2`.

21. `seed(7); start(); setTime(20); let s = getState();`  
   `s.time === 20`.

22. `seed(7); start(); step(1/60, 120); let a = getState(); seed(7); start(); step(1/60, 120); let b = getState();`  
   `a.mode === b.mode`, `a.world === b.world`, `a.stage === b.stage`, `a.player.x === b.player.x`, `a.score === b.score`.

23. `seed(7); start(); let s = getState();`  
   `s.audio.musicPlaying === true`.

24. `seed(7); start(); spawnProjectile('enemy', 'enemyPulse', 5, 14, 1); step(1/60, 1); let s = getState();`  
   `s.projectiles.some(p => p.kind === 'enemyPulse' && p.owner === 'enemy') === true`.

## SCREENSHOTS

| Screen / State | What a person must see |
| --- | --- |
| Title | Game title **Conduit Run**, Start button, control list, World 1-style animated background. |
| Play HUD | 3 hearts, energy bar, current gun name, four gun slots, score, time, nodes `x/3`, player visible in stage. |
| Crouch under low gap | Player is in crouch pose with height 1.4 tiles, passing under a 2-tile gap. |
| Scatter acquired | Stage clear or message screen shows “Scatter Rig acquired” and gun slot 2 is lit. |
| Boss active | Large boss visible, boss HP bar at top, phase indicator, boss theme audio flag active. |
| Exit open | Exit door glows green, nodes show `3/3`, open animation is visible. |
| Game complete | Final screen shows “Conduit Restored”, total score, and Play Again button. |

# 10. BUILD ORDER

1. Core simulation clock, mode state, shared context, and fixed tick update order.
2. Stage data structure, tile collision, one-way platforms, spikes, and stage bounds.
3. Player controller: move, jump, crouch, variable jump, coyote, buffer, checkpoint, and pit respawn.
4. Camera follow with deadzone and clamping.
5. Weapon system: 4 guns, cooldowns, energy, projectile spawn patterns.
6. Projectile system: movement, lifetime, pierce, homing, player/enemy collision.
7. Standard enemies and their state machines.
8. Pickups, nodes, hearts, energy, chips, and exit opening.
9. Stage generator for all 10 stages using the stage table.
10. Progression: stage complete, world transition, gun unlocks, stage select, final complete.
11. Bosses and boss phases.
12. UI screens and HUD.
13. Audio SFX and music loops.
14. Debug API and deterministic seed/step behavior.
15. Tests, balance pass, and final polish.

# 11. DEFINITION OF DONE

## Simulation core

- Fixed 60 tick simulation works without real-time dependence.
- All modes transition correctly.
- `step`, `setTime`, and `seed` produce deterministic states.
- Global state contains every record listed in section 2.2.

## Stage and world data

- 2 worlds and 5 stages each exist.
- Every stage has nodes, checkpoint, exit, enemies, and pickups.
- Stage widths and node positions match the stage table.
- Player can complete every stage by collecting nodes and reaching the exit.
- Max vertical step and max horizontal gap are within jump limits.

## Player

- Player can move left, move right, jump, and crouch.
- Variable jump, coyote, and jump buffer work.
- Crouch changes height and allows low-gap passage.
- Player collision with solids, one-way platforms, and spikes works.
- Damage, invulnerability, checkpoint, pit respawn, and game over work.

## Weapons

- All 4 guns exist and fire.
- `pulse`, `scatter`, `rail`, and `orbit` have distinct projectile patterns.
- Cooldowns are independent per gun.
- Energy cost and energy regeneration work.
- Gun switching works with cycle and quick select inputs.

## Enemies and bosses

- All standard enemy kinds exist and behave correctly.
- Enemy contact and projectiles can damage the player.
- Player projectiles can damage enemies.
- Score is awarded for enemy kills.
- Bosses appear in W1S5 and W2S5.
- Boss phases change HP thresholds and attack patterns.
- Boss death clears the stage when nodes are complete.

## Progression

- Clearing stages advances correctly.
- W1S5 leads to W2S1.
- W2S5 leads to complete.
- Gun unlocks occur after W1S1, W1S3, and W2S1.
- Stage select unlocks stages in order.
- Restart resets the stage but keeps session progression.

## UI

- Title, stage select, play, pause, clear, world complete, game over, and complete screens exist.
- HUD shows hearts, energy, gun, score, time, and nodes.
- Boss HUD appears when a boss is active.
- UI uses DOM/CSS overlay only.

## Audio

- Web Audio SFX play for key events.
- Music loops switch by mode and boss state.
- Audio flags are exposed in state for tests.

## Debug and tests

- `window.__game` exposes every listed call.
- All calls return plain data synchronously.
- Every numbered test passes.
- Every test uses only listed debug calls.
- Same seed and step sequence produces the same state.

## Performance

- Gameplay runs at 60 logic ticks per second.
- Drawing does not block logic.
- Projectile, enemy, and particle counts stay within stage limits.
- No unbounded lists remain after stage restart.

## Balance

- Player can clear every stage without being forced to take damage.
- Energy pickups are sufficient for intended boss fights.
- Standard enemy HP totals remain below the stage combat budget.
- Boss fights are challenging but avoidable for enough energy and HP.

# A. SANITY

| Check | Result |
| --- | --- |
| Every field a rule reads or writes is on a record. | Closes. Player HP, energy, height, cooldowns, enemy HP, phase, projectile pierce, node count, exit open, and mode are all defined in section 2.2. |
| Every place, thing, or kind a rule names is placed by a generator or listed in a roster. | Closes. Tile kinds, pickup kinds, enemy kinds, gun kinds, and projectile kinds are in the roster; stage generator places nodes, checkpoint, exit, pickups, enemies, and hazards using the stage table. |
| For every consumable, total generator placement meets total rule demand along the core loop. | Closes. Energy and hearts are optional. Non-boss stages place 5 energy and 1 heart; boss stages place 7 energy and 2 hearts. Max required combat energy for a boss using `rail` is about 300 energy over 10 seconds, and available energy is starting 100 plus 10 seconds of regen at 25/second plus 7 energy cells at 25 each, totaling 525. Non-boss max required energy is about 140, and available energy is starting 100 plus 10 seconds of regen plus 5 energy cells, totaling 325. |
| Every timing pair closes. | Closes. Jump height 3.21 tiles is above max vertical step 3 tiles. Jump distance 5.29 tiles is above max horizontal gap 4.5 tiles. Crouch height 1.4 tiles fits the 2-tile low gap, while stand height 2.6 tiles does not. `pulse` range 31.2 tiles is above max local enemy distance 16 tiles. `scatter` range 9.9 tiles is above close-combat distance 8 tiles. `rail` range 40 tiles is above boss arena effective target distance 20 tiles. `orbit` homing range 12 tiles and total travel 22.4 tiles cover air combat distance. Enemy projectile travel distance 18 tiles at 12 tiles/second gives at least 1.5 seconds reaction time. Boss fight energy drain closes as shown in consumable check. |
| Every call made in section 9 is listed in section 8. | Closes. All test calls use only `seed`, `start`, `getState`, `step`, `setMove`, `setJump`, `setCrouch`, `setFire`, `unlockGun`, `setGun`, `clearEnemies`, `spawnEnemy`, `spawnPickup`, `spawnProjectile`, `setHp`, `setEnergy`, `setNodes`, `openExit`, `setScore`, `setLives`, `setStage`, `completeStage`, `triggerBossPhase`, `setTime`, and `damagePlayer`. |
| Fix applied after sanity check. | Closes. Rail energy cost was set to 20, rail cooldown to 0.65 seconds, and boss energy cells to 7 so the 40-second worst-case boss fight energy demand remains below available energy from start, regen, and pickups. |