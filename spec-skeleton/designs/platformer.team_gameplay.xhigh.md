2D, fixed side-view camera that scrolls horizontally with the player, does not rotate or zoom, and clamps to the stage bounds.

# 1. THE GAME IN ONE PARAGRAPH

The player is a salvage gunner running right through a collapsing orbital factory, jumping gaps, crouching under low ceilings, and shooting mechanical enemies to clear the path to each stage exit. The run is organized into 2 worlds and 5 stages each, with the four gun types unlocking in story order: Bolt Pistol at start, Scatter Rivet in World 1 Stage 2, Rail Lance in World 1 Stage 4, and Plasma Arc in World 2 Stage 2. Minute to minute, the player moves, jumps, crouches, switches guns, reloads, collects scrap, health, ammo, and gun pickups, and kills enemies. The structure is worlds-and-stages, but the content is a sci-fi salvage run, not a prince-rescue platformer. The end is World 2 Stage 5: defeat the Magnet Boss, clear the stage, and see the victory screen with score, time, and best score. If the player reaches 0 lives, the screen is game over and they may retry the current stage.

# 2. RECORDS

RECORDS: GAME_SESSION, INPUT, PLAYER, GUN, GUN_STATE, ENEMY_TYPE, ENEMY, PROJECTILE, ITEM_TYPE, ITEM, TILE_TYPE, TILE, WORLD, STAGE, STAGE_RUNTIME

GAME_SESSION: screen, world_id, stage_number, score, stage_start_score, best_score, lives, stage_attempt.  
`screen`: enum `title`, `stage_intro`, `playing`, `paused`, `respawn`, `stage_clear`, `world_clear`, `game_over`, `victory`; start `title`. `world_id`: int, start 1, range 1-2. `stage_number`: int, start 1, range 1-5. `score`: int score points, start 0, range 0-999999. `stage_start_score`: int score points, start 0, range 0-999999. `best_score`: int score points, start 0, range 0-999999. `lives`: int, start 3, range 0-3. `stage_attempt`: int, start 1, range 1-99.

INPUT: left, right, jump, crouch, fire, reload, pause, gun1, gun2, gun3, gun4.  
All fields: boolean, start `false`, range `true`/`false`. These are the current frame’s logical inputs.

PLAYER: x, y, vx, vy, facing, grounded, crouching, health, max_health, invuln_s, coyote_s, jump_buffer_s, current_gun_id, hitbox_w, hitbox_h, crouch_hitbox_h.  
`x`: float pixels, start 120, range 0-stage length. `y`: float pixels, start 468, range 0-600. `vx`: float pixels/s, start 0, range -260 to 260 except knockback. `vy`: float pixels/s, start 0, range -900 to 900. `facing`: int, start 1, range -1 or 1. `grounded`: boolean, start `false`. `crouching`: boolean, start `false`. `health`: int HP, start 10, range 0-10. `max_health`: int HP, start 10. `invuln_s`: float seconds, start 0, range 0-2.0. `coyote_s`: float seconds, start 0, range 0-0.1. `jump_buffer_s`: float seconds, start 0, range 0-0.12. `current_gun_id`: int, start 1, range 1-4. `hitbox_w`: int pixels, start 26. `hitbox_h`: int pixels, start 52, range 30-52. `crouch_hitbox_h`: int pixels, start 30.

GUN: id, name, damage, cooldown_s, magazine_size, reload_s, projectile_speed, projectile_life_s, spread_half_deg, projectile_count, pierce_limit, splash_radius, splash_damage, knockback, unlock_stage.  
`id`: int, range 1-4. `name`: string. `damage`: int HP, range 1-4. `cooldown_s`: float seconds, range 0.2-1.111. `magazine_size`: int rounds, range 4-12. `reload_s`: float seconds, range 0.8-1.4. `projectile_speed`: int px/s, range 420-1100. `projectile_life_s`: float seconds, range 0.9-1.5. `spread_half_deg`: float degrees, range 0-18. `projectile_count`: int, range 1-5. `pierce_limit`: int enemies, range 0-3. `splash_radius`: int px, range 0-70. `splash_damage`: int HP, range 0-3. `knockback`: int px/s, range 40-220. `unlock_stage`: string, range `W1S1` to `W2S5`.

| id | name | damage HP | cooldown s | magazine rounds | reload s | projectile_speed px/s | projectile_life s | spread_half_deg | projectile_count | pierce_limit | splash_radius px | splash_damage HP | knockback px/s | unlock_stage |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Bolt Pistol | 2 | 0.2 | 12 | 0.8 | 780 | 1.2 | 0 | 1 | 0 | 0 | 0 | 60 | W1S1 |
| 2 | Scatter Rivet | 1 | 0.625 | 6 | 1.2 | 620 | 0.9 | 18 | 5 | 0 | 0 | 0 | 40 | W1S2 |
| 3 | Rail Lance | 4 | 0.833 | 4 | 1.4 | 1100 | 1.0 | 0 | 1 | 3 | 0 | 0 | 220 | W1S4 |
| 4 | Plasma Arc | 3 | 1.111 | 8 | 1.1 | 420 | 1.5 | 0 | 1 | 0 | 70 | 3 | 160 | W2S2 |

GUN_STATE: gun_id, magazine, reloading, reload_timer_s, fire_cooldown_s, unlocked.  
`gun_id`: int, start 1, range 1-4. `magazine`: int rounds, start equal to `GUN.magazine_size` for that gun, range 0-`GUN.magazine_size`. `reloading`: boolean, start `false`. `reload_timer_s`: float seconds, start 0, range 0-`GUN.reload_s`. `fire_cooldown_s`: float seconds, start 0, range 0-`GUN.cooldown_s`. `unlocked`: boolean, start `true` for gun 1 and `false` for guns 2-4.

ENEMY_TYPE: id, name, max_hp, contact_damage, attack_interval_s, attack_damage, projectile_speed, charge_speed, patrol_speed, detection_range, burst_shots, score, drop_heal_percent, drop_ammo_percent, width, height, hover.  
`id`: int, range 1-5. `name`: string. `max_hp`: int HP, range 3-70. `contact_damage`: int HP, range 0-2. `attack_interval_s`: float seconds, range 0-6.0. `attack_damage`: int HP, range 0-2. `projectile_speed`: int px/s, range 0-420. `charge_speed`: int px/s, range 0-420. `patrol_speed`: int px/s, range 0-160. `detection_range`: int px, range 140-800. `burst_shots`: int, range 0-2. `score`: int score points, range 50-1000. `drop_heal_percent`: int percent, range 0-100. `drop_ammo_percent`: int percent, range 0-100. `width`: int px, range 28-72. `height`: int px, range 22-80. `hover`: boolean.

| id | name | max_hp HP | contact_damage HP | attack_interval_s | attack_damage HP | projectile_speed px/s | charge_speed px/s | patrol_speed px/s | detection_range px | burst_shots | score pts | drop_heal % | drop_ammo % | width px | height px | hover |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Scrap Drone | 3 | 1 | 2.0 | 1 | 260 | 0 | 120 | 320 | 1 | 50 | 10 | 10 | 28 | 28 | true |
| 2 | Bolt Crawler | 4 | 1 | 0 | 1 | 0 | 320 | 80 | 140 | 0 | 60 | 10 | 15 | 32 | 22 | false |
| 3 | Rivet Turret | 6 | 1 | 1.6 | 1 | 300 | 0 | 0 | 260 | 2 | 80 | 15 | 10 | 30 | 30 | false |
| 4 | Pulse Brute | 10 | 2 | 3.0 | 2 | 0 | 380 | 90 | 380 | 0 | 150 | 25 | 15 | 44 | 50 | false |
| 5 | Magnet Boss | 70 | 2 | 4.0 | 2 | 240 | 420 | 160 | 800 | 0 | 1000 | 100 | 100 | 72 | 80 | false |

ENEMY: type_id, x, y, vx, vy, hp, max_hp, state, state_timer_s, active, boss_phase, attack_timer_s, dash_timer_s, laser_timer_s, charge_timer_s, spawn_x, spawn_y.  
`type_id`: int, start from ENEMY_TYPE, range 1-5. `x`, `y`: float pixels, start from generated position, range 0-stage length. `vx`, `vy`: float px/s, start 0, range -900 to 900. `hp`: int HP, start `ENEMY_TYPE.max_hp + WORLD.enemy_hp_bonus`, range 0-`max_hp`. `max_hp`: int HP, start equal to `hp`, range 3-72. `state`: enum `idle`, `patrol`, `chase`, `aim`, `charge`, `windup`, `stunned`, `dead`; start `idle`. `state_timer_s`: float seconds, start 0. `active`: boolean, start `false`. `boss_phase`: int, start 1, range 1-3. `attack_timer_s`, `dash_timer_s`, `laser_timer_s`, `charge_timer_s`: float seconds, start 0. `spawn_x`, `spawn_y`: float pixels, start from generated position.

PROJECTILE: owner, gun_id, enemy_type_id, x, y, vx, vy, damage, life_s, pierce_left, splash_radius, splash_damage, knockback, active.  
`owner`: enum `player`, `enemy`; start set at spawn. `gun_id`: int, start 0, range 0-4. `enemy_type_id`: int, start 0, range 0-5. `x`, `y`: float pixels, start set at spawn. `vx`, `vy`: float px/s, start set at spawn, range -1100 to 1100. `damage`: int HP, start set at spawn, range 1-4. `life_s`: float seconds, start set at spawn, range 0-1.5. `pierce_left`: int enemies, start set at spawn, range 0-3. `splash_radius`: int px, start set at spawn, range 0-70. `splash_damage`: int HP, start set at spawn, range 0-3. `knockback`: int px/s, start set at spawn, range 0-220. `active`: boolean, start `true`.

ITEM_TYPE: id, name, size, score, heal, magazine_fill, gun_id, effect.  
`id`: int, range 1-8. `name`: string. `size`: int px, range 16-40. `score`: int score points, range 0-100. `heal`: int HP, range 0-2. `magazine_fill`: boolean. `gun_id`: int, range 0-4. `effect`: string.

| id | name | size px | score pts | heal HP | magazine_fill | gun_id | effect |
|---:|---|---:|---:|---:|---|---:|---|
| 1 | Scrap Coin | 16 | 10 | 0 | false | 0 | Add score |
| 2 | Energy Cell | 18 | 0 | 2 | false | 0 | Heal 2 HP |
| 3 | Ammo Pack | 18 | 0 | 0 | true | 0 | Fill unlocked guns |
| 4 | Gun Pickup Scatter | 24 | 100 | 0 | false | 2 | Unlock and equip gun 2 |
| 5 | Gun Pickup Rail | 24 | 100 | 0 | false | 3 | Unlock and equip gun 3 |
| 6 | Gun Pickup Plasma | 24 | 100 | 0 | false | 4 | Unlock and equip gun 4 |
| 7 | Checkpoint | 32 | 0 | 0 | false | 0 | Set checkpoint |
| 8 | Exit Door | 40 | 0 | 0 | false | 0 | End stage if open |

ITEM: type_id, x, y, active.  
`type_id`: int, start from ITEM_TYPE, range 1-8. `x`, `y`: float pixels, start from generated position. `active`: boolean, start `true`.

TILE_TYPE: id, name, collision, damage, bounce_vy, default_thickness.  
`id`: int, range 1-5. `name`: string. `collision`: enum `solid`, `oneway_top`, `hazard`. `damage`: int HP, range 0-1. `bounce_vy`: int px/s, range -820 to 0. `default_thickness`: int px, range 12-80.

| id | name | collision | damage HP | bounce_vy px/s | default_thickness px |
|---:|---|---|---:|---:|---:|
| 1 | Solid Ground | solid | 0 | 0 | 80 |
| 2 | One-way Platform | oneway_top | 0 | 0 | 12 |
| 3 | Spike | hazard | 1 | 0 | 12 |
| 4 | Bounce Pad | oneway_top | 0 | -820 | 12 |
| 5 | Low Ceiling | solid | 0 | 0 | 50 |

TILE: type_id, x, y, w, h, active.  
`type_id`: int, start from TILE_TYPE, range 1-5. `x`, `y`, `w`, `h`: float pixels, start from generated position. `active`: boolean, start `true`.

WORLD: id, name, stage_count, enemy_hp_bonus, enemy_damage_bonus, enemy_projectile_speed_bonus.  
`id`: int, start 1, range 1-2. `name`: string. `stage_count`: int, start 5. `enemy_hp_bonus`: int HP, range 0-2. `enemy_damage_bonus`: int HP, range 0-1. `enemy_projectile_speed_bonus`: int px/s, range 0-60.

| id | name | stage_count | enemy_hp_bonus HP | enemy_damage_bonus HP | enemy_projectile_speed_bonus px/s |
|---:|---|---:|---:|---:|---:|
| 1 | Scrap Yard | 5 | 0 | 0 | 0 |
| 2 | Orbital Forge | 5 | 2 | 1 | 60 |

STAGE: world_id, stage_number, stage_id, seed, length_px, checkpoint_x, enemy_count, item_count, platform_count, spike_count, gun_unlock_id, has_boss.  
`world_id`: int, range 1-2. `stage_number`: int, range 1-5. `stage_id`: string. `seed`: int. `length_px`: int px. `checkpoint_x`: int px. `enemy_count`: int. `item_count`: int. `platform_count`: int. `spike_count`: int. `gun_unlock_id`: int, range 0-4. `has_boss`: boolean.

| stage_id | world_id | stage_number | seed | length_px | checkpoint_x | enemy_count | item_count | platform_count | spike_count | gun_unlock_id | has_boss |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| W1S1 | 1 | 1 | 101 | 4000 | 2000 | 6 | 20 | 18 | 4 | 0 | false |
| W1S2 | 1 | 2 | 102 | 4200 | 2100 | 8 | 24 | 20 | 6 | 2 | false |
| W1S3 | 1 | 3 | 103 | 4400 | 2200 | 10 | 26 | 22 | 8 | 0 | false |
| W1S4 | 1 | 4 | 104 | 4600 | 2300 | 12 | 28 | 24 | 10 | 3 | false |
| W1S5 | 1 | 5 | 105 | 4800 | 2400 | 14 | 30 | 26 | 12 | 0 | false |
| W2S1 | 2 | 1 | 201 | 5000 | 2500 | 14 | 30 | 26 | 12 | 0 | false |
| W2S2 | 2 | 2 | 202 | 5200 | 2600 | 16 | 32 | 28 | 14 | 4 | false |
| W2S3 | 2 | 3 | 203 | 5400 | 2700 | 18 | 34 | 30 | 16 | 0 | false |
| W2S4 | 2 | 4 | 204 | 5600 | 2800 | 20 | 36 | 32 | 18 | 0 | false |
| W2S5 | 2 | 5 | 205 | 6000 | 3000 | 8 | 20 | 20 | 8 | 0 | true |

STAGE_RUNTIME: stage_id, generated_seed, elapsed_time_s, checkpoint_x, exit_open, gun_collected, boss_dead, stage_complete.  
`stage_id`: string, start from current STAGE. `generated_seed`: int, start from `STAGE.seed`. `elapsed_time_s`: float seconds, start 0. `checkpoint_x`: int px, start from `STAGE.checkpoint_x`. `exit_open`: boolean, start `true` if `STAGE.gun_unlock_id` is 0 and `STAGE.has_boss` is `false`, otherwise `false`. `gun_collected`: boolean, start `false`. `boss_dead`: boolean, start `false`. `stage_complete`: boolean, start `false`.

# 3. SYSTEMS

SYSTEMS: Controls, Movement and Jump, Crouch, Guns and Projectiles, Enemy AI, Boss, Pickups and Stage Flow, Stage Generation

## Controls

RULES:

- IF key `A` or `Left Arrow` is down, THEN set `INPUT.left = true`; otherwise set `INPUT.left = false`.
- IF key `D` or `Right Arrow` is down, THEN set `INPUT.right = true`; otherwise set `INPUT.right = false`.
- IF key `W`, `Up Arrow`, or `Space` is down, THEN set `INPUT.jump = true`; otherwise set `INPUT.jump = false`.
- IF key `S` or `Down Arrow` is down, THEN set `INPUT.crouch = true`; otherwise set `INPUT.crouch = false`.
- IF key `J`, key `K`, or mouse left button is down, THEN set `INPUT.fire = true`; otherwise set `INPUT.fire = false`.
- IF key `R` just became true, THEN set `INPUT.reload = true`; otherwise set `INPUT.reload = false`.
- IF key `Escape` just became true and `GAME_SESSION.screen = playing`, THEN set `GAME_SESSION.screen = paused`.
- IF key `Escape` just became true and `GAME_SESSION.screen = paused`, THEN set `GAME_SESSION.screen = playing`.
- IF key `1` just became true and `GUN_STATE[1].unlocked = true`, THEN set `PLAYER.current_gun_id = 1`.
- IF key `2` just became true and `GUN_STATE[2].unlocked = true`, THEN set `PLAYER.current_gun_id = 2`.
- IF key `3` just became true and `GUN_STATE[3].unlocked = true`, THEN set `PLAYER.current_gun_id = 3`.
- IF key `4` just became true and `GUN_STATE[4].unlocked = true`, THEN set `PLAYER.current_gun_id = 4`.
- Touch left move button active: set `INPUT.left = true`.
- Touch right move button active: set `INPUT.right = true`.
- Touch jump button active: set `INPUT.jump = true`.
- Touch fire button active: set `INPUT.fire = true`.
- Touch crouch button active: set `INPUT.crouch = true`.
- Touch gun button tapped: cycle `PLAYER.current_gun_id` to the next unlocked gun ID from 1 to 4, wrapping 4 to 1.

## Movement and Jump

RULES:

- Let `dt` be the elapsed frame time in seconds.
- IF `PLAYER.crouching = true`, THEN horizontal speed limit is 100 px/s.
- IF `PLAYER.crouching = false`, THEN horizontal speed limit is 260 px/s.
- IF `INPUT.left = true` and `INPUT.right = false`, THEN target horizontal velocity is `-horizontal_speed_limit`.
- IF `INPUT.right = true` and `INPUT.left = false`, THEN target horizontal velocity is `horizontal_speed_limit`.
- IF neither `INPUT.left` nor `INPUT.right` is true, THEN target horizontal velocity is 0.
- IF `PLAYER.vx < target_horizontal_velocity`, THEN increase `PLAYER.vx` by 1800 * dt, but not above target horizontal velocity.
- IF `PLAYER.vx > target_horizontal_velocity`, THEN decrease `PLAYER.vx` by 1800 * dt, but not below target horizontal velocity.
- IF target horizontal velocity is 0 and `PLAYER.vx != 0`, THEN move `PLAYER.vx` toward 0 by 2200 * dt.
- IF `PLAYER.grounded = false`, THEN increase `PLAYER.vy` by 2200 * dt.
- IF `PLAYER.vy > 900`, THEN set `PLAYER.vy = 900`.
- IF `INPUT.jump` just became true, THEN set `PLAYER.jump_buffer_s = 0.12`.
- IF `PLAYER.jump_buffer_s > 0` and `PLAYER.grounded = true` and `PLAYER.crouching = false`, THEN set `PLAYER.vy = -620`, set `PLAYER.grounded = false`, set `PLAYER.coyote_s = 0`, set `PLAYER.jump_buffer_s = 0`, and set `PLAYER.crouching = false`.
- IF `PLAYER.jump_buffer_s > 0` and `PLAYER.coyote_s > 0` and `PLAYER.crouching = false`, THEN set `PLAYER.vy = -620`, set `PLAYER.grounded = false`, set `PLAYER.coyote_s = 0`, and set `PLAYER.jump_buffer_s = 0`.
- IF `INPUT.jump` released and `PLAYER.vy < 0`, THEN set `PLAYER.vy = max(PLAYER.vy, -320)`.
- Every frame, decrease `PLAYER.jump_buffer_s`, `PLAYER.coyote_s`, and `PLAYER.invuln_s` by dt, but not below 0.
- IF `PLAYER.vy > 0` and the player’s feet cross the top of a `solid` or `oneway_top` TILE from above, THEN set `PLAYER.y` to that tile top minus `PLAYER.hitbox_h`, set `PLAYER.vy = 0`, set `PLAYER.grounded = true`, and set `PLAYER.coyote_s = 0.1`.
- IF `PLAYER.grounded = true` and the player moves off the edge of the supporting TILE, THEN set `PLAYER.grounded = false` and set `PLAYER.coyote_s = 0.1`.
- IF the player’s horizontal movement intersects a `solid` TILE, THEN stop horizontal movement and set `PLAYER.vx = 0`.

## Crouch

RULES:

- Let vertical clearance be the distance from `PLAYER.y` to the lowest solid TILE top above the player.
- IF `INPUT.crouch = true` and `PLAYER.grounded = true` and vertical clearance >= 30, THEN set `PLAYER.crouching = true`, set `PLAYER.hitbox_h = 30`, and increase `PLAYER.y` by 22.
- IF `INPUT.crouch = false` and `PLAYER.crouching = true`, THEN set `PLAYER.crouching = false`, set `PLAYER.hitbox_h = 52`, and decrease `PLAYER.y` by 22, but only if vertical clearance >= 52; otherwise remain crouched.
- IF `PLAYER.crouching = true`, THEN jumping is disabled.
- IF `PLAYER.crouching = true`, THEN the player’s hitbox is 26 px wide and 30 px tall.
- IF `PLAYER.crouching = false`, THEN the player’s hitbox is 26 px wide and 52 px tall.

## Guns and Projectiles

RULES:

- Every frame, decrease `GUN_STATE[PLAYER.current_gun_id].fire_cooldown_s` by dt, but not below 0.
- IF `GUN_STATE[PLAYER.current_gun_id].reloading = true`, THEN decrease `GUN_STATE[PLAYER.current_gun_id].reload_timer_s` by dt.
- IF `GUN_STATE[PLAYER.current_gun_id].reloading = true` and `GUN_STATE[PLAYER.current_gun_id].reload_timer_s <= 0`, THEN set `GUN_STATE[PLAYER.current_gun_id].reloading = false` and set `GUN_STATE[PLAYER.current_gun_id].magazine = GUN.magazine_size` for the current gun.
- IF `INPUT.reload = true` and the current `GUN_STATE.magazine < GUN.magazine_size` and `GUN_STATE.reloading = false`, THEN set `GUN_STATE.reloading = true` and set `GUN_STATE.reload_timer_s = GUN.reload_s`.
- IF `INPUT.fire` just became true and the current `GUN_STATE.magazine = 0` and `GUN_STATE.reloading = false`, THEN set `GUN_STATE.reloading = true` and set `GUN_STATE.reload_timer_s = GUN.reload_s`.
- IF switching guns, THEN clear the previous current gun’s `reloading` flag and `reload_timer_s`; keep each gun’s `magazine` unchanged.
- IF `INPUT.fire = true` and the current gun is unlocked and `GUN_STATE.reloading = false` and `GUN_STATE.fire_cooldown_s <= 0` and `GUN_STATE.magazine > 0`, THEN:
  - set `PLAYER.facing = 1` if `INPUT.right` was more recently true than `INPUT.left`, otherwise set `PLAYER.facing = -1` if `INPUT.left` was more recently true, otherwise keep `PLAYER.facing`;
  - set `GUN_STATE.fire_cooldown_s = GUN.cooldown_s`;
  - set `GUN_STATE.magazine = GUN_STATE.magazine - 1`;
  - spawn `GUN.projectile_count` PROJECTILE objects.
- For a projectile spawned by the player:
  - set `owner = player`;
  - set `gun_id = PLAYER.current_gun_id`;
  - set `x` to `PLAYER.x + PLAYER.hitbox_w/2 + PLAYER.facing * 18`;
  - set `y` to `PLAYER.y + 14` if standing, or `PLAYER.y + 8` if crouching;
  - set `damage = GUN.damage`;
  - set `life_s = GUN.projectile_life_s`;
  - set `pierce_left = GUN.pierce_limit`;
  - set `splash_radius = GUN.splash_radius`;
  - set `splash_damage = GUN.splash_damage`;
  - set `knockback = GUN.knockback`.
- For Bolt Pistol, Rail Lance, and Plasma Arc, spawn one projectile at angle 0 degrees relative to `PLAYER.facing`.
- For Scatter Rivet, spawn five projectiles at angles -18, -9, 0, 9, and 18 degrees relative to `PLAYER.facing`.
- For each player projectile, set `vx = PLAYER.facing * GUN.projectile_speed * cos(angle)` and `vy = GUN.projectile_speed * sin(angle)`.
- Every frame, for each active PROJECTILE:
  - set `PROJECTILE.x += PROJECTILE.vx * dt`;
  - set `PROJECTILE.y += PROJECTILE.vy * dt`;
  - decrease `PROJECTILE.life_s` by dt.
- IF `PROJECTILE.life_s <= 0`, THEN set `PROJECTILE.active = false`.
- IF a player PROJECTILE intersects an ENEMY, THEN:
  - set `ENEMY.hp = ENEMY.hp - PROJECTILE.damage`;
  - if `ENEMY.type_id != 5`, set `ENEMY.vx = sign(PROJECTILE.vx) * PROJECTILE.knockback`, set `ENEMY.state = stunned`, and set `ENEMY.state_timer_s = 0.15`;
  - if `PROJECTILE.pierce_left > 0`, set `PROJECTILE.pierce_left = PROJECTILE.pierce_left - 1`;
  - if `PROJECTILE.pierce_left = 0`, set `PROJECTILE.active = false`;
  - if `PROJECTILE.splash_radius > 0`, apply `PROJECTILE.splash_damage` to every other ENEMY within `PROJECTILE.splash_radius` px of the impact point, and remove the projectile.
- IF an ENEMY projectile intersects PLAYER and `PLAYER.invuln_s = 0`, THEN:
  - set `PLAYER.health = PLAYER.health - PROJECTILE.damage`;
  - set `PLAYER.invuln_s = 0.8`;
  - set `PLAYER.vx = sign(PROJECTILE.vx) * 180`;
  - set `PLAYER.vy = -220`.
- IF any PROJECTILE intersects a `solid` TILE, THEN set `PROJECTILE.active = false`.

## Enemy AI

RULES:

- Every frame, decrease each ENEMY’s `state_timer_s`, `attack_timer_s`, `dash_timer_s`, `laser_timer_s`, and `charge_timer_s` by dt, but not below 0.
- IF `ENEMY.hover = false` and `ENEMY.state != dead`, THEN apply gravity: `ENEMY.vy += 2200 * dt`; if `ENEMY.vy > 900`, set `ENEMY.vy = 900`.
- IF `ENEMY.active = false` and horizontal distance from `PLAYER.x` to `ENEMY.x` is less than `ENEMY_TYPE.detection_range`, THEN set `ENEMY.active = true` and set `ENEMY.state = patrol`.
- IF `ENEMY.hp <= 0`, THEN set `ENEMY.state = dead`, set `ENEMY.active = false`, add `ENEMY_TYPE.score` to `GAME_SESSION.score`, spawn drops, and remove the ENEMY after 0.2 s.
- IF an active non-boss ENEMY’s rectangle overlaps PLAYER and `PLAYER.invuln_s = 0` and `ENEMY_TYPE.contact_damage > 0`, THEN:
  - set `PLAYER.health = PLAYER.health - ENEMY_TYPE.contact_damage - WORLD.enemy_damage_bonus`;
  - set `PLAYER.invuln_s = 0.8`;
  - set `PLAYER.vx = sign(PLAYER.x - ENEMY.x) * 180`;
  - set `PLAYER.vy = -220`.

### Scrap Drone

- IF `ENEMY.state = patrol`, THEN move `ENEMY.x` toward `ENEMY.spawn_x` at 120 px/s, reversing direction when within 160 px of `ENEMY.spawn_x`.
- IF `ENEMY.active = true` and horizontal distance to PLAYER is less than 320 px, THEN set `ENEMY.state = aim`.
- IF `ENEMY.state = aim` and `ENEMY.attack_timer_s <= 0`, THEN:
  - set `ENEMY.attack_timer_s = 2.0`;
  - let distance be the straight-line distance from ENEMY to PLAYER;
  - spawn one enemy projectile with `vx = (PLAYER.x - ENEMY.x) / distance * (ENEMY_TYPE.projectile_speed + WORLD.enemy_projectile_speed_bonus)`;
  - spawn one enemy projectile with `vy = (PLAYER.y - ENEMY.y) / distance * (ENEMY_TYPE.projectile_speed + WORLD.enemy_projectile_speed_bonus)`;
  - set projectile `damage = ENEMY_TYPE.attack_damage + WORLD.enemy_damage_bonus`.

### Bolt Crawler

- IF `ENEMY.state = patrol`, THEN move `ENEMY.x` at 80 px/s, reversing at walls or platform edges.
- IF `ENEMY.active = true` and horizontal distance to PLAYER is less than 140 px and vertical difference is less than 40 px, THEN set `ENEMY.state = charge` and set `ENEMY.charge_timer_s = 1.2`.
- IF `ENEMY.state = charge`, THEN move `ENEMY.x` toward PLAYER at 320 px/s.
- IF `ENEMY.charge_timer_s <= 0` and `ENEMY.state = charge`, THEN set `ENEMY.state = patrol`.

### Rivet Turret

- IF `ENEMY.active = true` and horizontal distance to PLAYER is less than 260 px, THEN set `ENEMY.state = aim`.
- IF `ENEMY.state = aim` and `ENEMY.attack_timer_s <= 0`, THEN:
  - set `ENEMY.attack_timer_s = 1.6`;
  - spawn two enemy projectiles aimed at PLAYER, 0.25 s apart;
  - each projectile uses speed `300 + WORLD.enemy_projectile_speed_bonus` and damage `1 + WORLD.enemy_damage_bonus`.

### Pulse Brute

- IF `ENEMY.active = true` and horizontal distance to PLAYER is less than 380 px, THEN set `ENEMY.state = chase`.
- IF `ENEMY.state = chase`, THEN move `ENEMY.x` toward PLAYER at 90 px/s.
- IF `ENEMY.state = chase` and horizontal distance to PLAYER is less than 120 px and `ENEMY.attack_timer_s <= 0`, THEN set `ENEMY.state = windup`, set `ENEMY.state_timer_s = 0.7`, and set `ENEMY.attack_timer_s = 3.0`.
- IF `ENEMY.state = windup` and `ENEMY.state_timer_s <= 0`, THEN set `ENEMY.state = charge`, set `ENEMY.charge_timer_s = 1.0`, and set `ENEMY.vx = sign(PLAYER.x - ENEMY.x) * 380`.
- IF `ENEMY.state = charge` and `ENEMY.charge_timer_s <= 0`, THEN set `ENEMY.state = patrol` and set `ENEMY.vx = 0`.

## Boss

RULES:

- The Magnet Boss is present only in W2S5.
- IF `STAGE.has_boss = true` and `PLAYER.x > STAGE.length_px - 950`, THEN set the boss ENEMY `active = true`.
- IF the boss is active, THEN `STAGE_RUNTIME.exit_open = false` until the boss dies.
- Boss phase:
  - IF `ENEMY.hp > 45`, THEN set `ENEMY.boss_phase = 1`;
  - IF `ENEMY.hp <= 45` and `ENEMY.hp > 20`, THEN set `ENEMY.boss_phase = 2`;
  - IF `ENEMY.hp <= 20`, THEN set `ENEMY.boss_phase = 3`.
- Boss movement:
  - Phase 1: move toward PLAYER at 160 px/s.
  - Phase 2: move toward PLAYER at 200 px/s.
  - Phase 3: move toward PLAYER at 240 px/s.
- Boss radial attack:
  - Phase 1: every 4.0 s, spawn 8 projectiles at 45-degree intervals, speed 240, damage 2 + `WORLD.enemy_damage_bonus`.
  - Phase 2: every 3.0 s, spawn 10 projectiles at 36-degree intervals, speed 260, damage 2 + `WORLD.enemy_damage_bonus`.
  - Phase 3: every 2.5 s, spawn 12 projectiles at 30-degree intervals, speed 280, damage 2 + `WORLD.enemy_damage_bonus`.
- Boss dash attack:
  - Phase 1: every 6.0 s, enter `windup` for 0.8 s, then dash for 1.2 s at 420 px/s.
  - Phase 2: every 5.0 s, enter `windup` for 0.8 s, then dash for 1.2 s at 420 px/s.
  - Phase 3: every 4.0 s, enter `windup` for 0.8 s, then dash for 1.2 s at 420 px/s.
- Boss laser attack:
  - Phase 3 only: every 8.0 s, enter laser charge for 1.0 s, then create a vertical laser at `PLAYER.x` for 0.8 s.
  - The laser is 8 px wide.
  - IF the laser is active and `PLAYER.x` is within 8 px of the laser x, THEN set `PLAYER.health = PLAYER.health - (2 + WORLD.enemy_damage_bonus)` once and set `PLAYER.invuln_s = 0.8`.
- IF the boss ENEMY `hp <= 0`, THEN set `STAGE_RUNTIME.boss_dead = true`, set `STAGE_RUNTIME.exit_open = true`, add 1000 score points to `GAME_SESSION.score`, and remove the boss after 0.8 s.

## Pickups and Stage Flow

RULES:

- Every frame, increase `STAGE_RUNTIME.elapsed_time_s` by dt while `GAME_SESSION.screen = playing`.
- IF PLAYER overlaps an active ITEM:
  - IF `ITEM.type_id = 1`, THEN add 10 to `GAME_SESSION.score` and set `ITEM.active = false`.
  - IF `ITEM.type_id = 2`, THEN set `PLAYER.health = min(PLAYER.health + 2, PLAYER.max_health)` and set `ITEM.active = false`.
  - IF `ITEM.type_id = 3`, THEN set every unlocked `GUN_STATE.magazine = GUN.magazine_size` and set `ITEM.active = false`.
  - IF `ITEM.type_id = 4`, THEN set `GUN_STATE[2].unlocked = true`, set `PLAYER.current_gun_id = 2`, set `GUN_STATE[2].magazine = GUN.magazine_size`, add 100 to `GAME_SESSION.score`, set `ITEM.active = false`, and if `STAGE.gun_unlock_id = 2`, set `STAGE_RUNTIME.gun_collected = true`.
  - IF `ITEM.type_id = 5`, THEN set `GUN_STATE[3].unlocked = true`, set `PLAYER.current_gun_id = 3`, set `GUN_STATE[3].magazine = GUN.magazine_size`, add 100 to `GAME_SESSION.score`, set `ITEM.active = false`, and if `STAGE.gun_unlock_id = 3`, set `STAGE_RUNTIME.gun_collected = true`.
  - IF `ITEM.type_id = 6`, THEN set `GUN_STATE[4].unlocked = true`, set `PLAYER.current_gun_id = 4`, set `GUN_STATE[4].magazine = GUN.magazine_size`, add 100 to `GAME_SESSION.score`, set `ITEM.active = false`, and if `STAGE.gun_unlock_id = 4`, set `STAGE_RUNTIME.gun_collected = true`.
  - IF `ITEM.type_id = 7`, THEN set `STAGE_RUNTIME.checkpoint_x = ITEM.x`.
  - IF `ITEM.type_id = 8` and `STAGE_RUNTIME.exit_open = true`, THEN set `STAGE_RUNTIME.stage_complete = true`, add 250 to `GAME_SESSION.score`, and set `GAME_SESSION.screen = stage_clear`.
- IF an ITEM of type Scrap Coin is within 60 px of PLAYER, THEN move the ITEM toward PLAYER at 160 px/s.
- When an ENEMY dies:
  - let `r_heal = PRNG(STAGE_RUNTIME.generated_seed + ENEMY.spawn_x + ENEMY.spawn_y) mod 100`;
  - IF `r_heal < ENEMY_TYPE.drop_heal_percent`, THEN spawn an Energy Cell at the ENEMY position;
  - let `r_ammo = PRNG(STAGE_RUNTIME.generated_seed + ENEMY.spawn_x + ENEMY.spawn_y + 7) mod 100`;
  - IF `r_ammo < ENEMY_TYPE.drop_ammo_percent`, THEN spawn an Ammo Pack at the ENEMY position.
- IF `PLAYER.health <= 0`, THEN decrease `GAME_SESSION.lives` by 1.
- IF `GAME_SESSION.lives > 0` after death, THEN:
  - set `GAME_SESSION.screen = respawn`;
  - after 1.0 s, set `PLAYER.x = STAGE_RUNTIME.checkpoint_x`;
  - set `PLAYER.y = 468`;
  - set `PLAYER.health = PLAYER.max_health`;
  - set `PLAYER.invuln_s = 2.0`;
  - reset all active ENEMY positions, states, and HP to their generated values;
  - keep collected ITEM positions collected;
  - keep `STAGE_RUNTIME.gun_collected` and `STAGE_RUNTIME.boss_dead`;
  - set `GAME_SESSION.screen = playing`.
- IF `GAME_SESSION.lives = 0` after death, THEN set `GAME_SESSION.screen = game_over` and set `GAME_SESSION.best_score = max(GAME_SESSION.best_score, GAME_SESSION.score)`.
- IF `GAME_SESSION.screen = stage_clear`:
  - IF `GAME_SESSION.stage_number < 5`, THEN next `GAME_SESSION.stage_number` and go to `stage_intro`;
  - IF `GAME_SESSION.stage_number = 5`, THEN add 500 to `GAME_SESSION.score` and go to `world_clear`.
- IF `GAME_SESSION.screen = world_clear`:
  - IF `GAME_SESSION.world_id = 1`, THEN set `GAME_SESSION.world_id = 2`, set `GAME_SESSION.stage_number = 1`, and go to `stage_intro`;
  - IF `GAME_SESSION.world_id = 2`, THEN set `GAME_SESSION.screen = victory`.
- IF `GAME_SESSION.screen = game_over` and Enter is pressed, THEN retry the current stage:
  - set `GAME_SESSION.lives = 3`;
  - set `GAME_SESSION.score = GAME_SESSION.stage_start_score`;
  - regenerate the current stage;
  - keep guns unlocked from earlier stages;
  - IF the current stage has `gun_unlock_id > 0` and `STAGE_RUNTIME.gun_collected = false`, THEN set that `GUN_STATE.unlocked = false` and refill its magazine.

## Stage Generation

RULES:

- Stage coordinate rules:
  - stage width is `STAGE.length_px`;
  - stage height is 600 px;
  - main ground top is y = 520 px;
  - stage exit x is `STAGE.length_px - 100`;
  - player spawn x is 120 px.
- SEEDED GENERATOR:
  - Use `STAGE.seed` and `STAGE_RUNTIME.generated_seed`.
  - Use a deterministic PRNG with an integer seed and an integer channel.
  - Generate in this order: spawn ground, exit ground, ground patterns, floating platforms, items, checkpoint, gun pickup, spikes, enemies, boss, exit door.
- For each generation attempt, starting at attempt 0:
  - set `STAGE_RUNTIME.generated_seed = STAGE.seed + attempt`.
  - clear all TILE, ITEM, and ENEMY records for the stage.
- Spawn ground:
  - place TILE type Solid Ground at x = 0, y = 520, w = 300, h = 80.
- Exit ground:
  - place TILE type Solid Ground at x = `STAGE.length_px - 100`, y = 520, w = 100, h = 80.
- Ground patterns:
  - set `segment_start = 300`.
  - while `segment_start + 400 <= STAGE.length_px - 100`:
    - let `pattern = PRNG(STAGE_RUNTIME.generated_seed, segment_start / 400) mod 6`.
    - pattern 0 Flat: place Solid Ground x = `segment_start`, y = 520, w = 400, h = 80.
    - pattern 1 Gap: place Solid Ground x = `segment_start`, y = 520, w = 200, h = 80; place Solid Ground x = `segment_start + 300`, y = 520, w = 100, h = 80.
    - pattern 2 Step Up: place Solid Ground x = `segment_start`, y = 520, w = 200, h = 80; place Solid Ground x = `segment_start + 200`, y = 460, w = 200, h = 140.
    - pattern 3 Step Down: place Solid Ground x = `segment_start`, y = 460, w = 200, h = 140; place Solid Ground x = `segment_start + 200`, y = 520, w = 200, h = 80.
    - pattern 4 Low Ceiling: place Solid Ground x = `segment_start`, y = 520, w = 400, h = 80; place Low Ceiling x = `segment_start + 120`, y = 420, w = 160, h = 50.
    - pattern 5 Bounce: place Solid Ground x = `segment_start`, y = 520, w = 400, h = 80; place Bounce Pad x = `segment_start + 180`, y = 508, w = 40, h = 12.
    - set `segment_start = segment_start + 400`.
  - after the loop, place Solid Ground from `segment_start` to `STAGE.length_px - 100` at y = 520, h = 80.
- Floating platforms:
  - for `p = 1` to `STAGE.platform_count`:
    - let `x = 320 + floor((p - 1) * (STAGE.length_px - 1140) / STAGE.platform_count) + PRNG(STAGE_RUNTIME.generated_seed, p) mod 80`;
    - let `y = 440` if `PRNG(STAGE_RUNTIME.generated_seed, p + 100) mod 2 = 0`, otherwise let `y = 470`;
    - place TILE type One-way Platform at x, y, w = 90, h = 12.
- Items:
  - for `i = 1` to `STAGE.item_count`:
    - let `x = 360 + floor((i - 1) * (STAGE.length_px - 1160) / STAGE.item_count) + PRNG(STAGE_RUNTIME.generated_seed, 1000 + i) mod 40`;
    - if there is solid ground top at y = 520 under x, set `y = 500`; otherwise set `y = 450`;
    - let `r = PRNG(STAGE_RUNTIME.generated_seed, 2000 + i) mod 100`;
    - if `r` is 0-69, place Scrap Coin;
    - if `r` is 70-79, place Energy Cell;
    - if `r` is 80-99, place Ammo Pack.
- Checkpoint:
  - place ITEM type Checkpoint at x = `STAGE.checkpoint_x`, y = 500.
- Gun pickup:
  - IF `STAGE.gun_unlock_id = 2`, place ITEM type Gun Pickup Scatter at x = `STAGE.checkpoint_x + 200`, y = 500.
  - IF `STAGE.gun_unlock_id = 3`, place ITEM type Gun Pickup Rail at x = `STAGE.checkpoint_x + 200`, y = 500.
  - IF `STAGE.gun_unlock_id = 4`, place ITEM type Gun Pickup Plasma at x = `STAGE.checkpoint_x + 200`, y = 500.
- Spikes:
  - for `s = 1` to `STAGE.spike_count`:
    - let `x = 400 + floor((s - 1) * (STAGE.length_px - 1100) / STAGE.spike_count) + PRNG(STAGE_RUNTIME.generated_seed, 3000 + s) mod 20`;
    - if there is solid ground top at y = 520 under x, place TILE type Spike at x, y = 508, w = 12, h = 12.
- Enemies:
  - for `e = 1` to `STAGE.enemy_count`:
    - choose enemy type:
      - World 1: `r = PRNG(STAGE_RUNTIME.generated_seed, 4000 + e) mod 10`; 0-3 Scrap Drone, 4-6 Bolt Crawler, 7-8 Rivet Turret, 9 Pulse Brute.
      - World 2: `r = PRNG(STAGE_RUNTIME.generated_seed, 4000 + e) mod 10`; 0-2 Scrap Drone, 3-5 Bolt Crawler, 6-7 Rivet Turret, 8-9 Pulse Brute.
    - let `x = 400 + floor((e - 1) * (STAGE.length_px - 1100) / STAGE.enemy_count) + PRNG(STAGE_RUNTIME.generated_seed, 5000 + e) mod 60`;
    - if the chosen type is Scrap Drone, set `y = 440`; otherwise set `y = 520 - ENEMY_TYPE.height`;
    - place ENEMY with `hp = ENEMY_TYPE.max_hp + WORLD.enemy_hp_bonus`, `max_hp = ENEMY_TYPE.max_hp + WORLD.enemy_hp_bonus`, `state = idle`, `active = false`, `spawn_x = x`, `spawn_y = y`.
- Boss:
  - IF `STAGE.has_boss = true`, place ENEMY type Magnet Boss at x = `STAGE.length_px - 500`, y = 440, with `hp = 70 + WORLD.enemy_hp_bonus`, `max_hp = 70 + WORLD.enemy_hp_bonus`, `state = idle`, `active = false`.
- Exit door:
  - place ITEM type Exit Door at x = `STAGE.length_px - 50`, y = 480.
- VERIFIER:
  - spawn ground exists from x = 0 to x = 300.
  - exit ground exists from x = `STAGE.length_px - 100` to `STAGE.length_px`.
  - no gap between consecutive ground top surfaces is greater than 100 px.
  - no vertical step between consecutive ground or platform top surfaces is greater than 80 px.
  - no ENEMY is within 300 px of x = 120.
  - no ENEMY is within 200 px of `STAGE.length_px - 100`.
  - no ITEM or ENEMY is inside a solid TILE.
  - no Spike is inside a Low Ceiling.
  - IF `STAGE.gun_unlock_id > 0`, the required gun pickup exists and is not inside a solid TILE.
  - IF `STAGE.has_boss = true`, the area from x = `STAGE.length_px - 900` to x = `STAGE.length_px - 100` has no spikes and no floating platforms.
  - IF any check fails, re-roll with the next seed: set `attempt = attempt + 1` and regenerate.
  - If attempts 0 through 9 all fail, use the flat fallback:
    - place continuous Solid Ground from x = 0 to `STAGE.length_px` at y = 520, h = 80;
    - place Checkpoint at `STAGE.checkpoint_x`;
    - place required gun pickup at `STAGE.checkpoint_x + 200`;
    - place Exit Door at x = `STAGE.length_px - 50`, y = 480;
    - place enemies every 300 px from x = 400 to x = `STAGE.length_px - 400`;
    - place Scrap Coins every 200 px from x = 300 to x = `STAGE.length_px - 300`;
    - place no spikes and no floating platforms.

# 4. PROGRESSION AND DIFFICULTY

The player does not gain permanent damage, speed, or health upgrades. Growth is the arsenal: Bolt Pistol is available at start, Scatter Rivet unlocks in W1S2, Rail Lance unlocks in W1S4, and Plasma Arc unlocks in W2S2. In stages with a gun unlock, `STAGE_RUNTIME.exit_open` remains false until the required gun pickup is collected. After a gun is unlocked, it remains unlocked for the rest of the run.

Early game is easy because World 1 has 0 enemy HP bonus, 0 enemy damage bonus, 0 enemy projectile speed bonus, and lower enemy counts: W1S1 has 6 enemies, W1S2 has 8, W1S3 has 10, W1S4 has 12, and W1S5 has 14. Spike counts also grow slowly: 4, 6, 8, 10, and 12 across World 1.

Late game is harder because World 2 adds 2 enemy HP, 1 enemy damage, and 60 px/s enemy projectile speed to enemy types 1-4. W2S1 has 14 enemies, W2S2 has 16, W2S3 has 18, W2S4 has 20, and W2S5 has 8 normal enemies plus the Magnet Boss. Spike counts rise to 12, 14, 16, 18, and 8 in the boss stage.

The player is expected to start failing in W2S2 through W2S4, where enemy density, bonus damage, and bonus HP overlap. The biggest expected failure is the Magnet Boss in W2S5. Recovery is through 3 lives, checkpoint respawn, full health on respawn, 2.0 s respawn invulnerability, and game-over retry of the current stage. On game over, the player recovers by entering the stage intro again with 3 lives, score reset to `stage_start_score`, and the current stage’s gun unlock reset only if it was not collected.

Score is the persistent replay hook: Scrap Coin 10, enemy kills 50-150, gun pickup 100, stage clear 250, world clear 500, boss kill 1000. Time is recorded but does not add or subtract score in this build.

# 5. FEEL

Horizontal movement:
- run speed: 260 px/s;
- crouch speed: 100 px/s;
- acceleration: 1800 px/s²;
- friction: 2200 px/s²;
- tuned to feel responsive but not slippery, with crouching clearly slower.

Vertical movement:
- gravity: 2200 px/s²;
- max fall: 900 px/s;
- jump velocity: 620 px/s;
- jump cut floor: -320 px/s;
- coyote time: 0.10 s;
- jump buffer: 0.12 s;
- tuned so gaps up to 100 px are clearable and vertical steps up to 80 px are reachable, but platforming still has a clear risk threshold.

Gun feel:
- Bolt Pistol cooldown: 0.2 s; magazine 12; reload 0.8 s; projectile life 1.2 s;
- Scatter Rivet cooldown: 0.625 s; magazine 6; reload 1.2 s; projectile life 0.9 s; five pellets at -18, -9, 0, 9, 18 degrees;
- Rail Lance cooldown: 0.833 s; magazine 4; reload 1.4 s; projectile life 1.0 s; pierce 3;
- Plasma Arc cooldown: 1.111 s; magazine 8; reload 1.1 s; projectile life 1.5 s; splash radius 70 px; splash damage 3.
- Tuned so Pistol is safe, Scatter is aggressive close range, Rail is precise anti-line, and Plasma is crowd control with a heavier swing.

Damage and hit response:
- player knockback: 180 px/s horizontally and -220 px/s vertically;
- player invulnerability: 0.8 s after projectile or contact damage;
- respawn invulnerability: 2.0 s;
- enemy stun from player hits: 0.15 s;
- enemy knockback: 40-220 px/s depending on gun;
- Boss ignores player knockback.

Timers:
- checkpoint respawn screen: 1.0 s;
- stage clear transition: 1.2 s;
- world clear transition: 2.0 s;
- Bounce Pad launch velocity: -820 px/s;
- Boss dash windup: 0.8 s;
- Boss dash duration: 1.2 s;
- Boss laser charge: 1.0 s;
- Boss laser duration: 0.8 s.

Pickup feel:
- coin magnet radius: 60 px;
- coin magnet speed: 160 px/s;
- tuned so coins feel collectible but do not sweep the whole screen.

# 6. HUD AND SCREENS

Screen state machine:

`title (title name, best score, Start) → stage_intro (world/stage, goal, gun) → playing (HUD) ↔ paused (menu)`  
`playing → respawn (1.0 s) → playing`  
`playing → stage_clear (score bonus) → stage_intro or world_clear`  
`world_clear (score bonus) → stage_intro or victory`  
`playing with 0 lives → game_over (retry) → stage_intro`  
`victory (score, time, best score) → title`

Key/button destinations:
- `title`: Enter or Touch Start leads to `stage_intro` for W1S1.
- `stage_intro`: Enter or Touch Continue leads to `playing`.
- `playing`: Escape leads to `paused`.
- `paused`: Escape or Touch Resume leads to `playing`; Touch Restart leads to `stage_intro` for the current stage; Touch Quit leads to `title`.
- `respawn`: no player input; automatically returns to `playing` after 1.0 s.
- `stage_clear`: Enter or Touch Continue leads to next `stage_intro`, or to `world_clear` after stage 5.
- `world_clear`: Enter or Touch Continue leads to next world `stage_intro`, or to `victory` after World 2.
- `game_over`: Enter or Touch Retry leads to `stage_intro` for the current stage.
- `victory`: Enter or Touch Menu leads to `title`.

HUD table:

| HUD element | Record field shown | Visible when |
|---|---|---|
| World and stage label | `WORLD.name`, `STAGE.world_id`, `STAGE.stage_number` | `stage_intro`, `playing` |
| Stage goal | `STAGE.gun_unlock_id`, `STAGE.has_boss` | `stage_intro`, `playing` |
| Health | `PLAYER.health`, `PLAYER.max_health` | `playing`, `paused` |
| Lives | `GAME_SESSION.lives` | `playing`, `paused` |
| Current gun name | `PLAYER.current_gun_id`, `GUN.name` | `playing` |
| Magazine count | `GUN_STATE.magazine`, `GUN.magazine_size` | `playing` |
| Reload bar | `GUN_STATE.reload_timer_s` | `playing` while `GUN_STATE.reloading = true` |
| Gun slots | `GUN_STATE.unlocked`, `PLAYER.current_gun_id` | `playing` |
| Score | `GAME_SESSION.score` | `playing`, `stage_clear`, `world_clear`, `victory` |
| Stage time | `STAGE_RUNTIME.elapsed_time_s` | `playing` |
| Boss health bar | `ENEMY.hp`, `ENEMY.max_hp` for `ENEMY.type_id = 5` | `playing` while boss is active |
| Best score | `GAME_SESSION.best_score` | `title`, `victory` |