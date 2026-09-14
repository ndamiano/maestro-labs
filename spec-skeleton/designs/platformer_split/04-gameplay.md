# 4. GAMEPLAY SPEC

The game is a tight 2D side-scrolling platformer shooter called Signal Courier. Courier Jex races through a dying industrial city, restores communication nodes, and uses four tuned signal weapons to pass 10 stages across 2 worlds. Each stage requires reaching the Conduit. Boss stages require defeating the boss first. Optional Cores provide replay value and completion stats without blocking story progression.

## 4.1 Records with Rosters [T1]

World Roster:

| World | Name | Theme | Goal |
| --- | --- | --- | --- |
| 1 | Sumpworks | Lower industrial canal, rust, pipes, low ceilings, conveyors, pits, turrets | Restore lower relay by defeating Hush Warden |
| 2 | Skyloom | Floating market, vertical platforms, wind currents, wide gaps, open sightlines | Reach central Null Relay and silence final failure |

Stage Roster:

| Stage | Name | Size in Tiles | Focus | Target Time |
| --- | --- | ---: | --- | ---: |
| 1-1 | First Current | 75 x 12 | Tutorial | 45 s |
| 1-2 | Dredge Run | 95 x 12 | Moving platforms, conveyors | 70 s |
| 1-3 | Pressure Lock | 90 x 14 | Turrets, one-way platforms | 80 s |
| 1-4 | Rust Gallery | 105 x 12 | Crouching, drones, long low ceilings | 90 s |
| 1-5 | Hush Warden | 60 x 12 | Boss | 70 s |
| 2-1 | Lifted Bazaar | 80 x 20 | Vertical climb, wind | 80 s |
| 2-2 | Market Veils | 105 x 16 | One-way shelves, wraiths | 90 s |
| 2-3 | Windrace | 120 x 14 | Horizontal wind, timed platforms | 100 s |
| 2-4 | Highspire Ascent | 80 x 24 | Vertical pressure, golems | 110 s |
| 2-5 | Null Relay | 70 x 15 | Final boss | 120 s |

Target times are design goals, not enforced timers.

Weapon Roster:

| Slot | Weapon | Unlock Stage | Role |
| ---: | --- | --- | --- |
| 1 | Chirp | Start | Fast reliable default |
| 2 | Sifter | 1-2 | Close-range crowd control |
| 3 | Lance | 1-4 | Piercing high single-target damage |
| 4 | Bloom | 2-2 | Area control and tight-space damage |

Enemy Roster:

| Enemy | Type | Hitbox | Base HP | World 2 HP |
| --- | --- | ---: | ---: | ---: |
| Mite Crawler | Small ground swarm | 16 x 16 | 4 | 5 |
| Dredge Drone | Flying shooter | 24 x 20 | 10 | 12 |
| Pincer Bot | Melee charger | 24 x 24 | 18 | 21 |
| Warden Sentry | Stationary aimed turret | 32 x 32 | 30 | 35 |
| Mist Wraith | Flying phasing enemy | 24 x 24 | 22 | 25 |
| Bolt Golem | Large slow armored enemy | 48 x 48 | 60 | 69 |

Boss Roster:

| Boss | Stage | HP | Hitbox | Arena |
| --- | --- | ---: | ---: | ---: |
| Hush Warden | 1-5 | 180 | 64 x 64 | 36 x 12 tiles |
| Null Relay | 2-5 | 300 | 80 x 80 | 40 x 15 tiles |

Object Roster:

| Object | Size | Purpose |
| --- | ---: | --- |
| Conduit | 64 x 96 | Stage exit |
| Checkpoint | 32 x 48 | Respawn save |
| Core | 24 x 24 | Optional collectible |
| Signal Heart | 24 x 24 | Restores 1 heart |
| Tuner Shard | 32 x 48 | Unlocks one weapon |

Stage content roster:

| Stage | Purpose | Layout | Enemies | Pickups | Checkpoints | Exit |
| --- | --- | --- | --- | --- | --- | --- |
| 1-1 First Current | Teach movement, crouching, jumping, shooting | 0 to 15 flat start; 15 to 25 first spike cluster; 25 to 30 open corridor; 30 to 42 low ceiling passage requiring crouch; 42 to 48 small gap; 48 to 55 one-way platform above gap; 55 to 65 drone encounter; 65 to 70 small pit with mid platform; 70 to 75 conduit area | Mite Crawler x3: 2 near tile 25, 1 near tile 55; Dredge Drone x1 near tile 60 | Core 1 side alcove near tile 10; Core 2 inside low ceiling passage; Core 3 high ledge above gap; Signal Heart after checkpoint near tile 65 | Tile 40 | Conduit at tile 70 |
| 1-2 Dredge Run | Introduce moving platforms and conveyors; unlock Sifter | 0 to 15 start; 20 to 35 moving platforms over 8-tile pit; 35 to 50 conveyor belt; 50 to 70 drone corridor with low cover; 70 to 80 Pincer room; 80 to 90 second moving platform section; 90 to 95 conduit area | Dredge Drone x3: tiles 50, 60, 70; Mite Crawler x4: tiles 55, 60, 72, 78; Pincer Bot x1: tile 72 | Core 1 top of first moving platform; Core 2 spike corridor under conveyor; Core 3 high ledge before conduit; Signal Heart after checkpoint; Tuner Shard tile 85 unlocks Sifter | Tile 45 | Conduit at tile 92 |
| 1-3 Pressure Lock | Introduce Warden Sentry and one-way vertical pressure | 0 to 10 start; 10 to 20 short vertical shaft with one-way platforms; 20 to 35 low ceiling corridor; 35 to 50 Sentry alcove; 50 to 65 vertical moving pistons; 65 to 75 Pincer room; 75 to 85 second Sentry section; 85 to 90 conduit area | Warden Sentry x2: tiles 45 and 80; Pincer Bot x3: tiles 68, 72, 76; Dredge Drone x2: tiles 20 and 55 | Core 1 high ledge in vertical shaft; Core 2 behind low corridor; Core 3 on moving piston path; Signal Heart tile 55 | Tiles 35 and 60 | Conduit at tile 88 |
| 1-4 Rust Gallery | Emphasize crouching and long-range shooting; unlock Lance | 0 to 15 start; 15 to 35 long low ceiling gallery; 35 to 50 drone gap; 50 to 65 moving platforms; 65 to 80 conveyor and spike run; 80 to 95 Pincer charge corridor; 95 to 105 conduit area | Dredge Drone x4: tiles 30, 40, 55, 85; Pincer Bot x4: tiles 70, 80, 90, 95; Mite Crawler x4: tiles 35, 50, 65, 80 | Core 1 inside long low ceiling; Core 2 above moving platforms; Core 3 behind conveyor spike run; Signal Heart tile 70; Tuner Shard tile 98 unlocks Lance | Tiles 40 and 75 | Conduit at tile 102 |
| 1-5 Hush Warden | World 1 boss | 0 to 25 short gauntlet; 25 to 30 checkpoint; 30 to 58 boss arena; 58 to 60 conduit area; gauntlet has spike patch near tile 15, Sentry alcove near tile 20, two Mite Crawlers near tile 24; arena has flat floor, two side ledges, no moving platforms, no off-screen hazards | Warden Sentry x1 tile 20; Mite Crawler x2 tile 24; Hush Warden center of arena | Core 1 side alcove before boss; Core 2 high side ledge in arena; Core 3 appears above center during Phase 2 safe window; Signal Heart after checkpoint | Tile 30 before boss | Conduit locked until Hush Warden dies |
| 2-1 Lifted Bazaar | Introduce vertical climbing, updrafts, Mist Wraith | Bottom start vertical tiles 0 to 8; updraft column vertical tiles 10 to 20; one-way market shelves vertical tiles 20 to 35; drone corridor vertical tiles 35 to 45; mid checkpoint vertical tile 45; Wraith ledges vertical tiles 50 to 60; narrow top section vertical tiles 60 to 70; conduit at top vertical tile 72 | Dredge Drone x3: vertical tiles 35, 40, 45; Mist Wraith x2: vertical tiles 52 and 58; Pincer Bot x2: vertical tiles 25 and 60 | Core 1 inside updraft column; Core 2 hidden side shelf; Core 3 high ledge before conduit; Signal Heart mid checkpoint area | Vertical tile 45 | Conduit at top |
| 2-2 Market Veils | Introduce horizontal wind gusts and one-way shelf loops; unlock Bloom | 0 to 15 start; 20 to 30 left-push wind over 6-tile pit; 30 to 50 one-way market shelves; 50 to 65 Sentry row; 65 to 85 vertical loop with one-way platforms; 85 to 95 Wraith corridor; 95 to 105 conduit area | Warden Sentry x3: tiles 55, 60, 65; Mist Wraith x4: tiles 70, 75, 85, 90; Mite Crawler x4: tiles 35, 40, 80, 85 | Core 1 inside wind gust; Core 2 top of vertical loop; Core 3 low crouch under shelf; Signal Heart mid-stage; Tuner Shard tile 95 unlocks Bloom | Tile 45 | Conduit at tile 100 |
| 2-3 Windrace | Introduce Bolt Golem and stronger wind pressure | 0 to 15 start; 20 to 30 right-push wind; 30 to 50 moving platforms; 50 to 70 Sentry and Wraith mixed section; 70 to 85 strong left-push wind; 85 to 100 Golem chamber; 100 to 115 final run; 115 to 120 conduit area | Warden Sentry x3: tiles 55, 60, 90; Mist Wraith x4: tiles 50, 75, 85, 95; Bolt Golem x2: tiles 90 and 100 | Core 1 inside strong wind zone; Core 2 on moving platform; Core 3 side chamber near golem area; Signal Heart tile 75 | Tiles 40 and 80 | Conduit at tile 115 |
| 2-4 Highspire Ascent | Final non-boss stage, high vertical pressure | Bottom start vertical tiles 0 to 8; updraft vertical tiles 10 to 18; narrow ledges vertical tiles 18 to 35; Golem ledge vertical tiles 35 to 45; mid checkpoint vertical tile 45; crosswind section vertical tiles 50 to 65; Wraith shaft vertical tiles 65 to 75; conduit vertical tile 78 | Warden Sentry x4: vertical tiles 20, 30, 45, 60; Bolt Golem x2: vertical tiles 35 and 50; Mist Wraith x6: vertical tiles 25, 40, 55, 65, 70, 75 | Core 1 hidden ledge; Core 2 inside updraft; Core 3 high ledge before conduit; Signal Heart mid checkpoint | Vertical tiles 45 and 60 | Conduit at top |
| 2-5 Null Relay | Final boss and game completion | 0 to 20 short gauntlet; 20 to 30 checkpoint; 30 to 65 boss arena; 65 to 70 end area; gauntlet has spike patch near tile 10, Mist Wraiths near tiles 15 and 18, Bolt Golem near tile 20; arena has wide floor, two side ledges, no moving platforms, no off-screen hazards | Mist Wraith x2: tiles 15 and 18; Bolt Golem x1: tile 20; Null Relay center of arena | Core 1 pre-boss alcove; Core 2 side ledge in arena; Core 3 appears during Phase 3 Core Exposed window; Signal Heart after checkpoint | Tile 30 before boss | Conduit locked until Null Relay dies; after death and conduit, go to End |

## 4.2 Game States [T1]

| State | Purpose |
| --- | --- |
| Title | Start, continue, new game, controls |
| Intro | Short story setup |
| Signal Map | World and stage selection |
| Stage | Main gameplay |
| Pause | Pause stage and offer restart, title, map |
| Stage Summary | Show stage results and continue |
| Game Over | Lives exhausted; retry stage or title |
| End | Final boss complete; show run stats |

State flow:

- Title to Intro for new game.
- Intro to Signal Map.
- Signal Map to Stage for unlocked stages.
- Stage to Stage Summary after non-final completion.
- Stage Summary to Signal Map or next stage.
- Stage to Game Over when lives reach 0.
- Game Over to Stage retry, Signal Map, or Title.
- Stage to End after final completion.
- End to Signal Map or Title.

Title rules:

- If no progress exists, show Begin Signal.
- If progress exists, show Continue at the furthest unlocked uncompleted stage.
- If progress exists, show New Signal, which resets all progress.
- Show Controls.
- If all stages are completed and no uncompleted unlocked stage exists, Continue is hidden and Title offers Map.

Intro rules:

- Show 4 short story cards.
- Each card can be skipped with Enter, Space, or mouse click.
- After intro, go to Signal Map.

Signal Map rules:

- Show 2 worlds.
- Each world shows 5 stages.
- Stage states are Locked, Unlocked, Completed.
- Only unlocked stages can be started.
- Completed stages can be replayed.
- World 2 is locked until World 1 Stage 5 is completed.
- After final completion, the map remains available for replay.

Stage Summary rules:

- Shown after non-final stage completion.
- Display stage name, time, deaths in stage, cores collected in stage, total cores collected.
- Buttons are Continue and Signal Map.
- Continue proceeds to the next unlocked stage.
- Signal Map returns to map.

Game Over rules:

- Shown when lives reach 0.
- Display Signal Lost.
- Buttons are Retry Stage, Signal Map, Title.

End rules:

- Shown after World 2 Stage 5.
- Display Signal Restored.
- Display total time, total deaths, total cores collected out of 30.
- Buttons are Signal Map and Title.

## 4.3 Controls and Aiming [T1]

- Movement is keyboard.
- Aiming is mouse primary.
- J is keyboard fallback.
- Crouch is held.
- Jump is edge or held with variable cut.
- Weapon switch is by slot or cycle.
- Pause is only available during Stage state.

Aim vector:

- Mouse aim:
  - Convert mouse screen position to world position.
  - Aim vector is mouse world position minus muzzle origin.
  - Normalize aim vector.
  - If aim vector length is near zero, use last facing direction.
- Keyboard fallback:
  - Aim vector is right if facing right.
  - Aim vector is left if facing left.
  - Muzzle origin is adjusted for crouch height.

Muzzle origin ruling:

- `feetY = player.y + player.h`
- `baseY = feetY - 12`
- `centerX = player.x + player.w / 2`
- `muzzleY = baseY + (crouching ? 8 : 2)`
- Standing muzzle is 10 px above feet.
- Crouched muzzle is 4 px above feet.
- If aim is mostly horizontal:
  - `muzzleX = centerX + 14 * sign`
- If aim is mostly vertical:
  - `muzzleX = centerX`
- `mostlyHorizontal = Math.abs(aimX) >= Math.abs(aimY)`
- `sign = aimX !== 0 ? Math.sign(aimX) : player.facing`

Weapon switch rules:

- Weapons 1 through 4 can be selected only if unlocked.
- Attempting to select a locked weapon produces UI deny and no weapon change.
- Switching weapons sets universal weapon-switch cooldown of 0.12 seconds.
- Each weapon has its own fire cooldown.
- The player cannot shoot while the universal weapon-switch cooldown is active.

## 4.4 Player System [T1]

Player hitbox:

| State | Width | Height |
| --- | ---: | ---: |
| Standing | 16 px | 24 px |
| Crouching | 16 px | 12 px |

Feet are aligned to the bottom of the hitbox.

Player health:

- Player has 5 signal hearts.
- Each heart is 1 unit of health.
- All enemy contact, enemy projectiles, hazards, boss attacks, and pits deal 1 heart damage.
- When hearts reach 0, the player dies.
- After death, the player loses 1 life and respawns.

Player lives:

- Player starts each stage with 3 lives.
- If lives reach 0, show Game Over.
- On stage retry, lives reset to 3.
- On death with lives remaining, respawn at last checkpoint with full hearts.

Damage and invulnerability:

- When player takes damage:
  - Lose 1 heart.
  - Enter invulnerability for 1.0 seconds.
  - Apply horizontal knockback 280 px/s away from damage source.
  - Apply vertical knockback -240 px/s upward.
  - Player remains in control during invulnerability.
  - Enemy contact and enemy projectiles do not deal damage again during invulnerability.
  - Hazards do not deal damage again during invulnerability.

Death rules:

- If player dies:
  - If lives are greater than 0:
    - Lose 1 life.
    - Respawn at last checkpoint.
    - Restore hearts to 5.
    - Enter 1.0 second invulnerability.
  - If lives are 0:
    - Show Game Over.

Checkpoint respawn:

- Checkpoints are required every stage.
- When a checkpoint is activated:
  - Set respawn point.
  - Restore 1 heart if below 5.
  - Show checkpoint HUD notification.
  - Play checkpoint sound.
- If player dies and no checkpoint has been activated:
  - Respawn at stage start.

Checkpoint respawn position:

- Checkpoint size is 32 x 48.
- Respawn player top-left is:
  - `x = checkpoint.x + 8`
  - `y = checkpoint.y + 24`

Pit rule:

- If player falls below stage boundary by 64 pixels:
  - Take 1 heart damage.
  - Teleport to last checkpoint.
  - If no checkpoint exists, teleport to stage start.
  - Enter invulnerability for 0.5 seconds.
- If player has 0 hearts from a pit:
  - Trigger normal death.

## 4.5 Movement System [T1]

Movement numbers:

| Parameter | Value |
| --- | ---: |
| Ground max speed | 240 px/s |
| Crouched max speed | 120 px/s |
| Air max speed | 240 px/s |
| Ground acceleration | 2800 px/s² |
| Air acceleration | 1900 px/s² |
| Ground friction | 2800 px/s² |
| Air friction | 400 px/s² |
| Gravity | 1800 px/s² |
| Max fall speed | 1100 px/s |
| Initial jump velocity | -640 px/s |
| Jump cut velocity | -320 px/s |
| Coyote time | 0.09 seconds |
| Jump buffer | 0.10 seconds |

Movement algorithm:

Each fixed timestep:

1. Read horizontal input.
2. Determine target horizontal velocity:
   - `targetVX = maxSpeed * inputX`
3. Accelerate or decelerate toward `targetVX`.
4. Apply gravity unless the player is in an updraft zone.
5. Clamp fall speed.
6. Handle jump input.
7. Integrate X and resolve horizontal collision.
8. Integrate Y and resolve vertical collision.
9. Apply moving platform carry.
10. Apply conveyor and wind effects.
11. Update hitbox if crouch state changes.

Jump algorithm:

- Player can jump if:
  - Jump input was pressed within the last 0.10 seconds.
  - Player is grounded or within 0.09 seconds of leaving ground.
- On jump:
  - Set vertical velocity to -640 px/s.
  - Clear jump buffer.
- Variable jump:
  - If player releases jump while moving upward faster than -320 px/s, set vertical velocity to -320 px/s.

Crouch algorithm:

- Crouch is held.
- Crouching reduces height to 12 px.
- Crouching reduces max horizontal speed to 120 px/s.
- Player can jump while crouched.
- Player can shoot while crouched.
- Muzzle origin is lowered to match crouch height.
- Crouching is allowed in air.
- Standing requires 24 px vertical clearance.
- If standing is blocked, player remains crouched.

No double jump:

- The player does not have a double jump.
- Jump height and gap distance are calibrated for a single jump.
- Crouching and aiming provide mechanical variety.
- No double jump keeps platforming legible.

## 4.6 Collision System [T1]

The game uses tile-based collision.

Tile behavior:

| Tile or Object | Behavior |
| --- | --- |
| Solid tile | Blocks player, enemies, and projectiles |
| One-way platform | Blocks player only from below; projectiles pass through |
| Spike | Damages player on contact |
| Conveyor tile | Solid tile that adds horizontal velocity to grounded player |
| Wind zone | Invisible or visible force field that applies acceleration |
| Checkpoint | Triggers respawn save |
| Core | Optional collectible |
| Heart | Restores 1 heart if below max |
| Tuner | Unlocks a weapon |
| Conduit | Stage exit |

Player collision rules:

- Player collides with solid tiles.
- Player can land on one-way platforms.
- Player can pass upward through one-way platforms.
- Player cannot pass through solid tiles.
- Moving platforms push the player if the player is standing on them.

One-way platform landing rule:

- A one-way platform is solid only if:
  - Player is moving downward.
  - Player’s previous bottom was at or above the platform’s top.
  - Player is not jumping through.
- Projectiles ignore one-way platforms.
- One-way platform visual size is 32 x 8.
- Collision top is the top of the tile.

Moving platform rules:

- Moving platforms follow linear waypoint paths.
- If player is standing on a moving platform:
  - Apply platform position delta to player each timestep.
  - Maintain player foot offset relative to platform.
- If platform moves off-screen or resets on stage retry, player is no longer carried.
- Projectiles pass through moving platforms.
- Enemies do not ride moving platforms.
- Platform reset happens on stage reset.

Conveyor rules:

- Conveyor tiles apply horizontal speed offset only while player is grounded.
- Right conveyor adds 120 px/s horizontal offset.
- Left conveyor subtracts 120 px/s horizontal offset.
- Total horizontal speed while on conveyor can be clamped to plus or minus 360 px/s.

Wind zone rules:

- Wind zones apply acceleration to player while player hitbox intersects zone.
- Wind does not affect enemies unless specifically stated.
- Multiple overlapping wind zones sum accelerations before clamping.

| Wind Type | Acceleration | Clamp |
| --- | ---: | --- |
| Updraft | -2400 px/s² vertical | Vertical speed minimum -420 px/s |
| Horizontal gust right | +1600 px/s² horizontal | Horizontal speed maximum +360 px/s |
| Horizontal gust left | -1600 px/s² horizontal | Horizontal speed minimum -360 px/s |

Low clearance volumes:

- `lowClearance` rectangles are required for crouch-only passages.
- They block player when standing.
- They do not block player when crouching.
- They do not damage the player.
- They do not block projectiles.
- They do not block enemies.
- They do not block beams.
- If player hitbox is 16 x 24 and intersects a low clearance rectangle, resolve as solid.
- If player hitbox is 16 x 12 and does not intersect, pass through.

Spike volumes:

- Up spikes occupy lower 16 px of tile.
- Down spikes occupy upper 16 px of tile.
- Spike contact deals 1 heart damage.
- Spike size is 32 x 16.

## 4.7 Camera System [T1]

Camera follows player.

Camera rules:

- Logical viewport is 960 x 540.
- Camera smoothing: `camera += (target - camera) * min(1, 8 * dt)`
- Horizontal lookahead:
  - If moving right: plus 120 px.
  - If moving left: minus 120 px.
  - If idle: 0 px.
- Vertical target:
  - Player center Y minus 32 px.
- Camera is clamped to stage bounds when stage dimension is larger than viewport.
- Camera is centered on an axis when stage dimension is smaller than viewport.
- Background layers fill extra space.

Camera target:

- `playerCenterX = player.x + player.w / 2`
- `playerCenterY = player.y + player.h / 2`
- `lookahead = 0`
- If input right, `lookahead = 120`.
- If input left, `lookahead = -120`.
- `targetX = playerCenterX - 480 + lookahead`
- `targetY = playerCenterY - 32 - 270`

Clamp and center:

- If stage width is greater than 960, clamp camera X between 0 and stage width minus 960.
- If stage width is less than 960, center camera X at `(stage width - 960) / 2`.
- If stage height is greater than 540, clamp camera Y between 0 and stage height minus 540.
- If stage height is less than 540, center camera Y at `(stage height - 540) / 2`.

Camera feel:

- Camera should feel stable during jumps.
- Camera should not pan faster than player.
- Camera should not show outside stage bounds when stage is larger than viewport.

## 4.8 Weapons [T1]

Player has 4 gun types. Weapons are permanent unlocks. Once unlocked, they are available in all future stages and replays.

Weapon slots:

| Slot | Weapon | Unlock Stage |
| ---: | --- | --- |
| 1 | Chirp | Start |
| 2 | Sifter | 1-2 |
| 3 | Lance | 1-4 |
| 4 | Bloom | 2-2 |

Weapon switching:

- Selecting an unlocked weapon changes active weapon.
- Selecting a locked weapon does nothing except UI deny.
- Switching weapons sets universal shoot cooldown of 0.12 seconds.
- Weapon-specific fire cooldowns continue independently.
- Cycling forward advances through unlocked weapons only.
- Cycling wraps from last unlocked to first unlocked.

## 4.9 Weapon Details [T1]

Chirp:

| Parameter | Value |
| --- | ---: |
| Damage | 7 |
| Fire interval | 0.15 seconds |
| Projectile speed | 950 px/s |
| Projectile lifetime | 0.7 seconds |
| Projectile radius | 4 px |
| Projectiles per shot | 1 |
| Spread | 0 degrees |
| Pierce | None |
| Enemy knockback | 80 px/s |

Best use:

- General combat.
- Medium distance.
- Single enemies.

Sifter:

| Parameter | Value |
| --- | ---: |
| Damage per pellet | 4 |
| Fire interval | 0.55 seconds |
| Projectile speed | 720 px/s |
| Projectile lifetime | 0.35 seconds |
| Projectile radius | 3 px |
| Projectiles per shot | 5 |
| Spread angles | -8, -4, 0, +4, +8 degrees |
| Pierce | None |
| Enemy knockback per pellet | 60 px/s |

Best use:

- Swarms.
- Tight corridors.
- Enemies at close range.

Lance:

| Parameter | Value |
| --- | ---: |
| Damage | 24 |
| Fire interval | 0.62 seconds |
| Projectile speed | 1500 px/s |
| Projectile lifetime | 0.8 seconds |
| Projectile radius | 5 px |
| Projectiles per shot | 1 |
| Spread | 0 degrees |
| Pierce | 3 total enemies |
| Enemy knockback | 260 px/s |

Best use:

- Groups in a line.
- Bosses.
- Ranged enemies.

Lance pierce algorithm:

- Lance projectile can hit up to 3 enemies total.
- It stores the set of enemy IDs it has already hit.
- On enemy hit:
  - If enemy already in hit set, do nothing.
  - Add enemy to hit set.
  - Apply damage and knockback.
  - If hit set size is less than 3, projectile continues.
  - If hit set size is 3, projectile is destroyed.

Bloom:

| Parameter | Value |
| --- | ---: |
| Main damage | 12 |
| Shard damage | 6 |
| Fire interval | 1.0 second |
| Main projectile speed | 520 px/s |
| Main projectile lifetime | 0.45 seconds |
| Main projectile radius | 8 px |
| Shard speed | 620 px/s |
| Shard lifetime | 0.5 seconds |
| Shard radius | 4 px |
| Shards produced | 3 |
| Shard angles relative to main | -25, 0, +25 degrees |
| Split condition | On first enemy hit or after 0.45 seconds |
| Main enemy knockback | 180 px/s |
| Shard enemy knockback | 80 px/s |

Best use:

- Crowded rooms.
- Enemies partially behind cover.
- Boss pressure.

Bloom algorithm:

- Main projectile does not split on tile collision; it is destroyed.
- If main projectile hits an enemy:
  - Apply main damage.
  - Destroy main projectile.
  - Spawn 3 shards at hit location.
- If main projectile reaches lifetime without hitting an enemy:
  - Destroy main projectile.
  - Spawn 3 shards at current position.
- Shards do not split further.

## 4.10 Projectile System [T1]

All player and enemy projectiles:

- Are circular hitboxes.
- Move in straight lines unless affected by a stated special behavior.
- Are destroyed on solid tile collision.
- Have a lifetime.
- Deal damage only to the intended target group.
- Do not damage their owner.

Projectile collision order:

Each timestep, process projectiles in creation order:

1. Move projectile.
2. Check solid tile collision.
3. Check target collision.
4. Apply damage, knockback, or special behavior.
5. Remove projectile if lifetime expired, tile hit, or behavior destroyed it.

Projectile substeps:

- Distance moved per step is `speed * dt`.
- Substep size is 16 px.
- Segments are `max(1, ceil(distance / 16))`.
- Each segment checks tile collision.
- This prevents high-speed Lance projectiles from tunneling through tiles or enemies.

Tile collision:

- Projectile circle is expanded by radius against solid tile AABBs.
- One-way platforms are ignored.
- Low clearance is ignored.
- Moving platforms are ignored.

Lifetime:

- `age += dt`
- If `age >= lifetime`, remove projectile or apply Bloom split if applicable.

Entity limits:

- Maximum player projectiles: 80.
- Maximum enemy projectiles: 120.
- If limit is exceeded, oldest projectile expires.

## 4.11 Enemy System [T1]

Enemies activate when player enters activation radius.

Activation rules:

- Activation radius: 10 tiles, which is 320 px.
- Enemies do not act before activation.
- Once activated, enemies remain active until they die, become dormant, or stage reset.
- Maximum active enemies per stage: 16.
- If more than 16 are within radius, activate the 16 closest to player.
- If active count exceeds 16 due to summons, farthest active enemy beyond 320 px becomes dormant.
- Dormant enemies stop acting.
- Dormant enemies do not count as active.
- Dormant enemies can reactivate when space is available.

Enemy damage:

- All enemy attacks deal 1 heart to player.
- If player is invulnerable, no damage.
- If enemy is phased or intangible, no contact damage to player.

Enemy line of sight:

- Ranged enemies require line of sight before attacking.
- Sample line between enemy attack point and player center every 4 pixels.
- If any sample intersects a solid tile, line of sight is blocked.
- One-way platforms do not block line of sight.

Enemy death:

- Remove enemy.
- Clear enemy-owned projectiles.
- Play enemy death audio.
- Emit enemy death VFX.
- If Bolt Golem, spawn 1 Signal Heart at its center.

Mite Crawler:

| Parameter | Value |
| --- | ---: |
| Hitbox | 16 x 16 px |
| HP | 4 |
| Contact damage | 1 heart |
| Move speed | 90 px/s |
| Attack | Contact only |
| World 2 HP | 5 |

Behavior:

- If player is within 5 tiles, move toward player.
- Does not jump.
- Stops and waits 0.5 seconds if blocked by solid geometry.
- Dies to 1 Chirp shot.

Stage use:

- Tutorial enemies.
- Swarm pressure.
- Easy Sifter targets.

Dredge Drone:

| Parameter | Value |
| --- | ---: |
| Hitbox | 24 x 20 px |
| HP | 10 |
| Contact damage | 1 heart |
| Move speed | 120 px/s |
| Fire interval | 1.6 seconds |
| Projectile speed | 350 px/s |
| Projectile lifetime | 2.5 seconds |
| Projectile radius | 6 px |
| Attack range | 6 tiles |
| World 2 HP | 12 |
| World 2 projectile speed | 385 px/s |

Behavior:

- Patrols horizontally within 4 tiles of spawn.
- Adds vertical sine offset of 12 px.
- If player is within attack range and has line of sight:
  - Hover.
  - Fire straight projectile toward player.
- Collides with solid tiles but ignores one-way platforms.

Stage use:

- Aerial spacing.
- Forces jump timing.
- Good for Lance.

Pincer Bot:

| Parameter | Value |
| --- | ---: |
| Hitbox | 24 x 24 px |
| HP | 18 |
| Contact damage | 1 heart |
| Walk speed | 130 px/s |
| Charge speed | 420 px/s |
| Charge duration | 0.35 seconds |
| Telegraph time | 0.5 seconds |
| Attack range | 4 tiles |
| Cooldown | 1.5 seconds |
| World 2 HP | 21 |

Behavior states:

1. Idle:
   - Wanders slowly near spawn.
2. Telegraph:
   - If player is within attack range and has line of sight:
     - Stop.
     - Shake.
     - Show charge telegraph.
3. Charge:
   - Dash toward player’s current position.
   - Stop on solid collision or after charge duration.
4. Cooldown:
   - Cannot charge again until cooldown ends.

Stage use:

- Teaches reaction and spacing.
- Punishes standing still.
- Can be dodged by crouch or jump.

Warden Sentry:

| Parameter | Value |
| --- | ---: |
| Hitbox | 32 x 32 px |
| HP | 30 |
| Contact damage | 1 heart |
| Aim speed | 3 radians/second |
| Burst shots | 2 |
| Burst gap | 0.15 seconds |
| Fire cooldown | 2.6 seconds |
| Projectile speed | 520 px/s |
| Projectile lifetime | 1.5 seconds |
| Projectile radius | 6 px |
| Attack range | 8 tiles |
| World 2 HP | 35 |
| World 2 projectile speed | 572 px/s |

Behavior:

- Stationary.
- If player is within range and has line of sight:
  - Aim at player.
  - When aim is within 10 degrees of player, fire 2-round burst.
- If no line of sight:
  - Slowly return aim to last known angle.
  - If no last known angle, face right.

Stage use:

- Forces movement and cover usage.
- Good for Lance or Bloom.

Mist Wraith:

| Parameter | Value |
| --- | ---: |
| Hitbox | 24 x 24 px |
| HP | 22 |
| Contact damage | 1 heart |
| Move speed | 180 px/s |
| Phase interval | 2.5 seconds |
| Phase duration | 0.8 seconds |
| Sine offset | 30 px |
| World 2 HP | 25 |

Behavior:

- Flies toward player with vertical sine motion.
- Collides with solid tiles but ignores one-way platforms.
- Every 2.5 seconds:
  - Becomes intangible for 0.8 seconds.
  - While phased:
    - Player projectiles pass through.
    - Player contact does no damage to enemy.
    - Enemy contact does no damage to player.
  - Returns to normal.

Stage use:

- Teaches timing.
- Rewards burst damage.
- Good for Chirp and Lance timing.

Bolt Golem:

| Parameter | Value |
| --- | ---: |
| Hitbox | 48 x 48 px |
| HP | 60 |
| Contact damage | 1 heart |
| Move speed | 60 px/s |
| Heavy bolt interval | 3.0 seconds |
| Heavy bolt speed | 300 px/s |
| Heavy bolt lifetime | 3.0 seconds |
| Heavy bolt radius | 10 px |
| Attack range | 8 tiles |
| Stomp interval | 4.0 seconds |
| Stomp range | 3 tiles |
| World 2 HP | 69 |
| World 2 heavy bolt speed | 330 px/s |

Behavior:

- Moves toward player if within 8 tiles.
- Does not jump.
- If player is within range and has line of sight:
  - Fires a heavy straight bolt toward player.
- If player is within stomp range:
  - Telegraph 0.4 seconds.
  - Stomps.
  - Spawns 2 temporary ground spike patches in front of itself for 2 seconds.
- Drops 1 Signal Heart on death.

Stage use:

- Late-stage pressure.
- Requires patience.
- Good for Lance and Bloom.

## 4.12 Boss System [T1]

Boss stages have a boss. Boss is inactive until player enters boss trigger or arena. Once active, boss remains active until death or stage reset. If player dies with lives remaining, boss resets to full HP and idle. Summons are cleared.

Boss damage:

- Player projectiles can damage boss unless boss is dying.
- Contact with boss deals 1 heart.
- Boss projectiles and beams deal 1 heart.
- If player is invulnerable, no damage.

Boss death:

- Set dying.
- Stop all attacks.
- Remove boss-owned projectiles.
- Remove active beams.
- Remove summoned enemies.
- Make boss invulnerable.
- Run death sequence.
- Unlock conduit.

Hush Warden:

Location: Stage 1-5.

| Parameter | Value |
| --- | ---: |
| HP | 180 |
| Hitbox | 64 x 64 px |
| Contact damage | 1 heart |
| Boss projectile damage | 1 heart |
| Arena size | 36 x 12 tiles |
| Base move speed | 80 px/s |
| Phase 2 move speed | 88 px/s |

Phases:

| Phase | HP range |
| --- | --- |
| 1 | 100 percent to 60 percent |
| 2 | 60 percent to 0 percent |

Attack selection:

- Among ready attacks, choose lowest remaining cooldown.
- Tie priority:
  - Charge
  - Fan Bolt
  - Sweep Beam
  - Drone Summon

Charge:

- Cooldown: 6 seconds.
- Telegraph: 0.6 seconds.
- Dash horizontally toward player at 480 px/s.
- Duration: 1.2 seconds.
- Leaves 4 spike patches along path.
- Spike patches last 3 seconds.
- Spike patch placement:
  - Spawn at fractional distances along actual dash path: 25 percent, 50 percent, 75 percent, 100 percent.
  - Each patch is 32 x 16.
  - Patches snap to floor below path point.
  - If no floor exists at a sample, skip that patch.
  - Patch warning is 0.2 seconds.

Fan Bolt:

- Cooldown: 4 seconds.
- Fires 3 projectiles.
- Angles: -20, 0, +20 degrees.
- Projectile speed: 380 px/s.
- Projectile lifetime: 2.0 seconds.
- Projectile radius: 6 px.

Sweep Beam:

- Phase 2 only.
- Cooldown: 7 seconds.
- Telegraph: 0.8 seconds.
- Beam height: player Y at telegraph start.
- Beam width: 24 px.
- Beam duration: 0.7 seconds.
- Beam spans boss arena width.

Drone Summon:

- Phase 2 only.
- Cooldown: 10 seconds.
- Summons 2 Dredge Drones.
- Maximum active Dredge Drones: 3.
- Summoned drones use normal Dredge Drone behavior.
- If max is reached, summon is skipped.

Hush Warden death:

- Stop all attacks.
- Play 2-second death sequence.
- Boss hitbox becomes inactive.
- Conduit unlocks.
- Stage complete when player reaches Conduit.

Null Relay:

Location: Stage 2-5.

| Parameter | Value |
| --- | ---: |
| HP | 300 |
| Hitbox | 80 x 80 px |
| Contact damage | 1 heart |
| Boss projectile damage | 1 heart |
| Beam damage | 1 heart |
| Arena size | 40 x 15 tiles |

Phases:

| Phase | HP range |
| --- | --- |
| 1 | 100 percent to 70 percent |
| 2 | 70 percent to 35 percent |
| 3 | 35 percent to 0 percent |

Phase 2 and Phase 3 begin with a 1.5-second warning.

During warning:

- Boss does not attack.
- Boss is stationary or slowly moves to warning position.
- HUD shows phase warning.
- Boss warning audio plays.

Phase 1:

Rain:

- Interval: 1.5 seconds.
- Spawns vertical projectiles from 3 columns.
- Columns are chosen deterministically using stage RNG.
- Projectile speed: 420 px/s downward.
- Projectile lifetime: 2.0 seconds.
- Visual is 12 x 24 vertical shards.

Side Sweep:

- Cooldown: 6 seconds.
- Telegraph: 0.8 seconds.
- Horizontal beam at random Y chosen at telegraph start.
- Beam width: 24 px.
- Beam duration: 0.8 seconds.
- Beam spans arena width.

Movement:

- Moves horizontally at 60 px/s.

Phase 2:

Echo Shot:

- Cooldown: 4 seconds.
- Fires 3 projectiles toward player.
- Projectile speed: 520 px/s.
- Projectile lifetime: 2.0 seconds.
- Each projectile bounces once off arena walls.
- Bounce is reflected velocity.
- Projectile is destroyed after one bounce or if it hits solid geometry.

Wraith Summon:

- Cooldown: 12 seconds.
- Summons 2 Mist Wraiths.
- Maximum active Mist Wraiths: 4.
- If max is reached, summon is skipped.

Movement:

- Moves in small zigzag.
- Speed: 90 px/s.
- Vertical sine offset: 40 px.
- Sine period: 2.0 seconds.

Phase 3:

Overload Cycle:

Repeat until death:

1. Horizontal beam:
   - Telegraph: 0.6 seconds.
   - Duration: 0.6 seconds.
   - Beam Y locked to player Y at telegraph start.
2. Vertical beam:
   - Telegraph: 0.6 seconds.
   - Duration: 0.6 seconds.
   - Beam X locked to player X at telegraph start.
3. Core Exposed:
   - Boss becomes stationary.
   - Duration: 1.5 seconds.
   - All player damage to boss is multiplied by 1.5.
   - Boss cannot attack.

Null Relay death:

- Stop all attacks.
- Play 3-second death sequence.
- Show end state after player reaches Conduit or automatically after death sequence if Conduit is active.

Beam rules:

- Beam damage is 1 heart.
- Beam does not collide with tiles.
- Beam passes through one-way platforms.
- Beam passes through low clearance.
- Beam is removed when active time ends.
- Telegraph state has no damage.
- Active state damages player on overlap.
- Telegraph position is locked at telegraph start.
- If player moves during telegraph, beam does not follow.
- Exception: Null Relay Phase 1 Side Sweep uses a random valid arena Y chosen at telegraph start, then locks that displayed line.

## 4.13 Stage Objects [T1]

Conduit:

- Size: 64 x 96 px.
- Non-boss stages:
  - Activates when player overlaps it.
- Boss stages:
  - Inactive until boss dies.
  - Activates when player overlaps it after boss death.
- On activation:
  - Stop player input.
  - Play stage complete sequence.
  - Show Stage Summary or End state.

Checkpoint:

- Size: 32 x 48 px.
- Triggers once when player overlaps.
- Sets respawn point.
- Restores 1 heart if below max.
- Visual and audio feedback.

Core:

- Size: 24 x 24 px.
- Optional.
- 3 per stage.
- Once collected, global flag persists.
- On stage load or retry, already collected cores are not spawned.
- HUD updates total cores.

Signal Heart:

- Size: 24 x 24 px.
- Collects only if player hearts are below 5.
- If player hearts are already 5, the heart remains in the world.
- Restores 1 heart.

Tuner Shard:

- Size: 32 x 48 px.
- Unlocks one weapon.
- Once collected, weapon unlock persists globally.
- On stage load or retry, already collected tuners are not spawned.
- Shows unlock notification.

Tuner placement:

- `w1s2` has exactly one tuner for Sifter.
- `w1s4` has exactly one tuner for Lance.
- `w2s2` has exactly one tuner for Bloom.
- No other stage may have a tuner.

## 4.14 Progression and Difficulty [T1]

Weapon progression:

| Unlock | Stage | Weapon |
| --- | --- | --- |
| Start | None | Chirp |
| Stage 1-2 | Tuner Shard | Sifter |
| Stage 1-4 | Tuner Shard | Lance |
| Stage 2-2 | Tuner Shard | Bloom |

Stage unlocking:

- Stage 1-1 is always unlocked at New Signal.
- Completing a stage unlocks the next stage.
- Completing 1-5 unlocks World 2.
- Completing 2-5 completes the game.
- Completed stages can be replayed from Signal Map.

Core progression:

- 3 cores per stage.
- 30 total cores.
- Cores are optional.
- Cores persist once collected.
- Cores do not affect gameplay outside stats.

Life progression:

- Lives reset to 3 at the start of each stage.
- Lives do not carry between stages.

World 1 difficulty:

- Teaches core systems.
- Enemies have base HP.
- Hazards are predictable.
- Boss has 180 HP.

World 2 difficulty:

- Standard enemy HP multiplied by 1.15, rounded up.
- Standard enemy projectile speed multiplied by 1.1.
- More vertical movement.
- More wind interference.
- More ranged pressure.
- Bosses use their defined HP and projectile speeds without additional standard-enemy modifiers.

Fairness rules:

- No unavoidable damage.
- Boss attacks have telegraphs.
- No enemy attacks from off-screen without warning.
- No hazards activate without visible or audible cue.
- Checkpoints are placed before major hazard or boss sections.
- Gaps are never wider than 4 tiles.
- Jump height is sufficient to cross all required gaps.

Entity limits:

| Limit | Value |
| --- | ---: |
| Active enemies | 16 |
| Player projectiles | 80 |
| Enemy projectiles | 120 |
| Temporary spike patches | 20 |
| Active summoned boss enemies | 4 |

Overflow rules:

- If player projectiles exceed 80, expire oldest.
- If enemy projectiles exceed 120, expire oldest.
- If temporary spike patches exceed 20, remove oldest.
- If active enemies exceed 16, make farthest active enemy beyond 320 px dormant.

## 4.15 Stage Reset [T1]

On stage retry or Game Over retry:

- Player position resets to stage start.
- Hearts reset to 5.
- Lives reset to 3.
- Checkpoints reset.
- Enemies reset.
- Enemy projectiles reset.
- Player projectiles reset.
- Moving platforms reset.
- Wind zones reset.
- Boss resets if present.
- Beams reset.
- Temporary spikes reset.
- Uncollected stage Cores remain uncollected.
- Already globally collected Cores remain collected.
- Already globally unlocked weapons remain unlocked.
- Already globally collected Tuners remain collected.
- Global progression stats persist.

Death respawn rule:

When the player dies with lives remaining:

1. Decrement lives.
2. Restore hearts to 5.
3. Reset dynamic stage state.
4. Teleport player to last checkpoint or stage start.
5. Enter invulnerability 1.0 seconds.

Boss reset on death:

- If player dies during boss with lives remaining:
  - Respawn at checkpoint before boss.
  - Boss resets to full HP and idle.
  - Summons are cleared.

## 4.16 Feel [T1]

- Movement must feel snappy and fair.
- Weapons must have clear mechanical identity.
- Damage must be avoidable if the player watches telegraphs and stage layout.
- Player must always know the next objective: reach the Conduit.
- Cores provide optional completion value.
- No damage numbers.
- No minimap.
- No score.
- No permanent death.
- No weapon upgrades.
- No armor power-up.
- No health overcap.
- No touch controls.
- No 3D gameplay.
- No Z-axis depth.
- No camera rotation.
- No par time or star rating.
- No shops.
- No crafting.
- No side characters outside story text.
