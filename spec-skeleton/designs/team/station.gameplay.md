2D, top-down orthographic camera that follows the player.

# 1. THE GAME IN ONE PARAGRAPH

The player is alone on a damaged derelict space station, moving through a tile-based station cross-section from room to room to collect scrap, batteries, filters, coolant, and emergency supplies, while repairing power bays, oxygen scrubbers, and hull seals, and fighting awakened maintenance drones that hunt by sight and noise. Minute to minute, the player balances personal oxygen against station oxygen, keeps station power above 15 so scrubbers run, repairs the systems before they decay, uses coolant to shut down vents and radiation, and decides whether to sprint for speed and risk detection or move quietly and slowly. The game has no fixed scripted ending: a run ends only when player health reaches 0 or station hull reaches 0. What keeps it going is the day counter, rising threat level, random station events, beacon milestones that unlock small permanent upgrades, and the pursuit of a higher best day and best score.

# 2. RECORDS

RECORDS: Player, Inventory Slot, Item, Station, Station Object, Enemy, Hazard, Loot Container, Threat Event, Run Record

**Player.** position_x (tile, range 0-47.99, start 23.5), position_y (tile, range 0-29.99, start 15.5), velocity_x (tile/s, range 0-5, start 0), velocity_y (tile/s, range 0-5, start 0), facing (radians, range 0-6.283, start 0), health (points, range 0-health_cap, start 100), health_cap (points, start 100), oxygen (points, range 0-100, start 100), stamina (points, range 0-stamina_cap, start 100), stamina_cap (points, start 100), selected_slot (integer, range 1-10, start 1), attack_cooldown (seconds, range 0-0.5, start 0), attack_damage (points, start 10), last_damage_at (seconds, start 0), time (seconds, start 0), sprinting (boolean, start false), interacting (boolean, start false), interaction_timer (seconds, range 0-2, start 0).

**Inventory Slot.** slot_index (integer, range 1-10), item_id (string, start: slot 1 = o2_cell, slot 2 = medkit, slot 3 = scrap, slot 4 = battery, slot 5 = filter, slots 6-10 = empty), count (integer, range 0-stack maximum, start: slot 1 = 1, slot 2 = 1, slot 3 = 2, slot 4 = 1, slot 5 = 1, slots 6-10 = 0).

**Item.** item_id (string), stack (integer), use_type (string), effect (string). The fixed roster is:

| item_id | name | stack | use_type | effect |
|---|---:|---:|---|---|
| scrap | Scrap | 10 | material | crafting only |
| battery | Battery | 5 | insert/material | adds 5 load to a power_bay, or crafting material |
| coolant | Coolant | 5 | disable/material | disables an active hazard for 120 s, or crafting material |
| filter | Filter | 5 | insert/material | adds 5 load to a scrubber, or crafting material |
| fuse | Fuse | 5 | material | crafting only |
| o2_cell | O2 Cell | 3 | consumable | player.oxygen +35 |
| medkit | Medkit | 3 | consumable | player.health +30 |
| hull_patch | Hull Patch | 3 | consumable | at hub_console: station.hull +20; at hull_seal: object.integrity +30 and station.hull +5 |
| repair_kit | Repair Kit | 3 | repair | target Station Object integrity +30 |

**Station.** day (integer, start 1), day_timer (seconds, range 0-240, start 0), threat_level (integer, range 1-10, start 1), power (points, range 0-100, start 50), oxygen (points, range 0-100, start 60), hull (points, range 0-100, start 70), beacon (points, range 0-100, start 0), score (integer, start 0), kills (integer, start 0), repairs (integer, start 0), beacon_day3 (boolean, start false), beacon_wraith (boolean, start false), beacon_hazard (boolean, start false), last_event_1 (string, start none), last_event_2 (string, start none), last_event_3 (string, start none).

**Station Object.** object_id (integer), type (string: hub_console, scrubber, power_bay, hull_seal), x (tile integer), y (tile integer), integrity (points, range 0-100, start by type), load (points, range 0-10, start by type), active (boolean, start false), reached_100 (boolean, start false). The fixed roster and starting values are:

| type | count | start integrity | start load | load max |
|---|---:|---:|---:|---:|
| hub_console | 1 | 100 | 0 | 0 |
| scrubber | 4 | 70 | 4 | 10 |
| power_bay | 3 | 60 | 3 | 10 |
| hull_seal | 5 | 80 | 0 | 0 |

**Enemy.** enemy_id (integer), type (string: mite, wraith, overseer), x (tile), y (tile), health (points, range 0-scaled max), alert (points, range 0-100, start 0), state (string: patrol, search, chase, windup, start patrol), speed (tile/s, start scaled base), damage (points, start scaled base), attack_cd_max (seconds, start by type), attack_cooldown (seconds, range 0-attack_cd_max, start 0), windup_timer (seconds, start 0), last_seen_x (tile, start x), last_seen_y (tile, start y), search_timer (seconds, start 0), target_type (string: none, player, object, start none), target_id (integer, start 0), no_player_seen_timer (seconds, start 0). The fixed roster and base values are:

| type | base health | base speed | base damage | attack_cd_max | detection radius | noise radius | first spawn day |
|---|---:|---:|---:|---:|---:|---:|---:|
| mite | 20 | 2.2 | 5 | 1.2 | 6 | 4 | 1 |
| wraith | 50 | 1.8 | 12 | 1.5 | 7 | 5 | 3 |
| overseer | 120 | 1.6 | 20 | 2.0 | 8 | 6 | 7 |

**Hazard.** hazard_id (integer), type (string: vent, radiation), x (tile integer), y (tile integer), radius (tile, start by type), active (boolean, start true), disable_timer (seconds, range 0-120, start 0). The fixed roster is:

| type | radius | active effect |
|---|---:|---|
| vent | 2 | while active: station.oxygen -0.5/s; if player within radius: player.oxygen -2/s |
| radiation | 1.5 | while active and player within radius: player.health -2/s |

**Loot Container.** loot_id (integer), x (tile integer), y (tile integer), opened (boolean, start false), item_id (string from Item roster), count (integer, range 1-10, start 1).

**Threat Event.** event_id (string), day (integer, start current day). The fixed roster is:

| event_id | weight | effect |
|---|---:|---|
| power_surge | 3 | station.power +30; one random power_bay with integrity > 50 loses 40 integrity |
| hull_crack | 3 | one random hull_seal integrity = 20; station.hull -5 |
| supply_drop | 3 | place 4 loot containers in hub floor: scrap, battery, filter, o2_cell |
| vent_burst | 3 | add one active vent hazard on a floor tile not within 5 of player |
| radiation_leak | 2 | add one active radiation hazard on a floor tile not within 5 of player |
| drone_awakening | 2 | threat_level +1, capped 10; spawn 2 mites not within 10 of player |

**Run Record.** best_day (integer, start 0), best_score (integer, start 0).

# 3. SYSTEMS

SYSTEMS: Player, Life Support, Station Power, Crafting, Enemies, Hazards, Daily Cycle, Map Generator

## Player

- If W or ArrowUp is held, add -1 to input_y. If S or ArrowDown is held, add +1 to input_y. If A or ArrowLeft is held, add -1 to input_x. If D or ArrowRight is held, add +1 to input_x. If both input_x and input_y are nonzero, normalize the input vector to length 1.
- Target speed is 3 tile/s. If Shift is held and player.stamina > 0 and player.interacting is false, set player.sprinting = true and target speed = 5 tile/s; otherwise set player.sprinting = false and target speed = 3 tile/s.
- If player.sprinting is true, player.stamina -= 20 * dt. If player.sprinting is false and at least 0.5 s has passed since sprinting ended, player.stamina += 15 * dt. Clamp player.stamina to 0-player.stamina_cap.
- player.velocity_x changes by at most 12 tile/s^2 toward input_x * target speed. If input_x is 0, player.velocity_x decreases toward 0 at 20 tile/s^2. Apply the same rule to player.velocity_y.
- player.position_x += player.velocity_x * dt. player.position_y += player.velocity_y * dt. Clamp position to the 48x30 tile world. If the next tile is wall, cancel that axis of movement and zero that axis velocity.
- If input vector length > 0, player.facing = atan2(input_y, input_x).
- player.attack_cooldown = max(0, player.attack_cooldown - dt).
- If Space or J is pressed and player.attack_cooldown <= 0, set player.attack_cooldown = 0.5. For each enemy where distance to player <= 1.2 tile and angle difference from player.facing <= 60 degrees, enemy.health -= player.attack_damage, enemy.alert = 100, enemy.state = chase, and knock the enemy 0.5 tile away from player. If enemy.health <= 0, remove enemy, station.kills += 1, station.score += 10, and if enemy.type = wraith apply the beacon_wraith rule.
- If Q or Tab is pressed, player.selected_slot = ((player.selected_slot - 1) mod 10) + 1. If number key 1-10 is pressed while craft menu is closed, player.selected_slot = that number.
- If E is pressed and player.interacting is false:
  - If selected Inventory Slot item_id is o2_cell or medkit, start a 0.2 s interaction. On completion, o2_cell sets player.oxygen += 35 and medkit sets player.health += 30; consume 1 item.
  - Else if a Loot Container is the nearest interact target within 1.5 tile and it is not opened, start a 0.3 s interaction only if there is a valid Inventory Slot to receive the item. On completion, set Loot Container.opened = true, add item_id and count to inventory, and consume the container.
  - Else if a Hazard is the nearest target within 1.5 tile and selected item is coolant and hazard.active is true, start a 0.5 s interaction. On completion, hazard.active = false, hazard.disable_timer = 120, consume 1 coolant, and apply the beacon_hazard rule.
  - Else if a Station Object is the nearest target within 1.5 tile:
    - If selected item is repair_kit and object.integrity < 100, start a 2 s interaction. On completion, object.integrity += 30 capped 100, consume 1 repair_kit, station.repairs += 1, station.score += 5, and apply the reached_100 rule.
    - Else if object.type = power_bay and selected item is battery and object.load < 10, start a 0.5 s interaction. On completion, object.load += 5 capped 10, consume 1 battery.
    - Else if object.type = scrubber and selected item is filter and object.load < 10, start a 0.5 s interaction. On completion, object.load += 5 capped 10, consume 1 filter.
    - Else if selected item is hull_patch and object.type is hub_console or hull_seal, start a 0.5 s interaction. On completion, consume 1 hull_patch. If object.type = hub_console, station.hull += 20 capped 100. If object.type = hull_seal, object.integrity += 30 capped 100 and station.hull += 5 capped 100.
    - Else if object.integrity < 100, start a 1 s bare repair interaction. On completion, object.integrity += 5 capped 100, station.repairs += 1, station.score += 5, and apply the reached_100 rule.
  - Else if the nearest target is hub_console and selected item is not hull_patch, open the craft menu.
- While player.interacting is true, player.interaction_timer -= dt. If input vector length > 0, cancel interaction and set player.interacting = false and player.interaction_timer = 0. If player.interaction_timer <= 0, complete the queued effect and set player.interacting = false.
- Touch: a left virtual joystick sets the same movement input as WASD/arrows. Right-side buttons Action, Attack, Sprint, and Item trigger the same rules as E, Space, Shift hold, and Q respectively.

## Life Support

- Each second, for each scrubber where integrity >= 25 and station.power >= 15 and load > 0, set active = true, station.oxygen += 0.35 * dt, and load -= 0.05 * dt. Otherwise set active = false.
- station.oxygen -= 0.5 * dt.
- For each hull_seal where integrity < 50, station.oxygen -= 0.5 * dt.
- For each active vent hazard, station.oxygen -= 0.5 * dt.
- If station.hull < 20, station.oxygen -= 2 * dt.
- Clamp station.oxygen to 0-100.
- player.oxygen -= 0.4 * dt.
- If station.oxygen < 25, player.oxygen -= 0.6 * dt.
- If station.oxygen >= 75 and player.oxygen < 100, player.oxygen += 1.5 * dt.
- For each active vent hazard, if player is within hazard.radius, player.oxygen -= 2 * dt.
- Clamp player.oxygen to 0-100.
- If player.oxygen <= 0, player.health -= 4 * dt.
- If player.time - player.last_damage_at >= 10 and station.oxygen >= 75 and player.health < 60, player.health += 0.5 * dt.
- Clamp player.health to 0-player.health_cap.
- If player.health <= 0 or station.hull <= 0, go to game_over screen and update Run Record: best_day = max(best_day, station.day), best_score = max(best_score, station.score).

## Station Power

- station.power -= 3 * dt.
- For each active scrubber, station.power -= 2 * dt.
- For each power_bay where integrity >= 25 and load > 0, set active = true, station.power += 5 * dt, and load -= 0.05 * dt. Otherwise set active = false.
- Clamp station.power to 0-100.

## Crafting

- The craft menu is open only while the player is standing within 1.5 tile of hub_console and not using a personal consumable.
- Recipes are visible only if unlocked by station.day:
  1. O2 Cell: unlocked day 1, cost 1 filter + 1 battery, craft time 2 s, result 1 o2_cell.
  2. Medkit: unlocked day 2, cost 1 filter + 1 coolant, craft time 2 s, result 1 medkit.
  3. Hull Patch: unlocked day 2, cost 2 scrap + 1 fuse, craft time 2 s, result 1 hull_patch.
  4. Repair Kit: unlocked day 4, cost 1 scrap + 1 fuse + 1 coolant, craft time 3 s, result 1 repair_kit.
- If a craft recipe is selected while station.power >= 10 and all required items are present, start a craft interaction for the recipe time. Moving cancels it without consuming items.
- On craft completion, consume required items, add the result item to inventory, station.score += 5, and close the craft menu if inventory is full or the result has no valid slot.
- If the result item has no valid Inventory Slot, the craft fails and no items are consumed.

## Enemies

- Enemy spawn values are scaled by station.threat_level:
  - health = base health + (station.threat_level - 1) * 5
  - damage = base damage + (station.threat_level - 1) * 2
  - speed = base speed + min(0.5, (station.threat_level - 1) * 0.05)
- Perception:
  - If line of sight to player exists and distance <= enemy detection radius, set enemy.last_seen_x = player.position_x, enemy.last_seen_y = player.position_y, enemy.alert = 100, enemy.state = chase, enemy.target_type = player, and enemy.no_player_seen_timer = 0.
  - If line of sight does not exist and player is moving within the enemy noise radius, set enemy.last_seen_x = player.position_x, enemy.last_seen_y = player.position_y, and enemy.alert += 30 * dt. Player noise radius is 5 while sprinting, 2 while walking, and 0 while stationary.
- Behavior:
  - patrol: move at speed * 0.5 toward a waypoint chosen every 4 s from floor tiles within 3 tile. If player is detected, switch to chase.
  - search: move at speed toward last_seen_x, last_seen_y. If enemy reaches last_seen and player is not seen for 5 s, enemy.search_timer += dt. When enemy.search_timer >= 5, enemy.alert -= 20 * dt. If enemy.alert <= 0, set state = patrol.
  - chase: move at speed toward player. If distance <= 0.8 and enemy.attack_cooldown <= 0, set state = windup, enemy.windup_timer = 0.4. If line of sight is lost and distance > detection radius * 1.5, set state = search.
  - windup: after enemy.windup_timer reaches 0, player.health -= enemy.damage, player.last_damage_at = player.time, knock player 0.3 tile away from enemy, enemy.attack_cooldown = enemy.attack_cd_max, and set state = chase.
  - If enemy.no_player_seen_timer >= 10, choose the nearest Station Object with integrity < 100 within 4 tile. If one exists, set enemy.target_type = object and enemy.target_id = object.object_id. If none exists, set enemy.target_type = none.
  - If enemy.target_type = object and distance to target object <= 0.8 and enemy.attack_cooldown <= 0, target object.integrity -= enemy.damage, enemy.attack_cooldown = enemy.attack_cd_max, and station.score -= 0.
- Enemy movement is blocked by wall tiles. If the direct path is blocked, slide perpendicular to the target direction.
- enemy.attack_cooldown = max(0, enemy.attack_cooldown - dt).
- If enemy.health <= 0, remove enemy, station.kills += 1, station.score += 10, and if enemy.type = wraith and station.beacon_wraith is false, set station.beacon_wraith = true and station.beacon += 5 capped 100.

## Hazards

- For each inactive hazard, hazard.disable_timer -= dt. If hazard.disable_timer <= 0, set hazard.active = true.
- For each active hazard, if player.position is within hazard.radius, apply the active effect from the Hazard roster.
- If a hazard changes from active = true to active = false and station.beacon_hazard is false, set station.beacon_hazard = true and station.beacon += 5 capped 100.

## Daily Cycle

- station.day_timer += dt.
- If station.day_timer >= 240:
  - station.day += 1
  - station.day_timer = 0
  - station.score += 100
  - station.threat_level = min(10, station.threat_level + 1)
  - If station.day >= 4, station.hull -= 1.
  - One random Station Object that is not hub_console and has integrity > 10 loses 10 integrity.
  - Spawn drones using the Daily SEEDED GENERATOR below.
  - If station.day >= 2, choose and apply one Threat Event using the Daily SEEDED GENERATOR below.
  - Update last events: last_event_3 = last_event_2, last_event_2 = last_event_1, last_event_1 = chosen event_id.
- If station.beacon crosses 25 from below, player.stamina_cap += 10.
- If station.beacon crosses 50 from below, player.attack_damage += 2.
- If station.beacon crosses 75 from below, all existing and future Enemy.attack_cd_max += 0.2.
- If station.beacon crosses 100 from below, player.health_cap += 20, station.power += 20 capped 100, station.score += 500.

### Daily SEEDED GENERATOR

- seed_day = initial map seed + station.day * 7919.
- Use a seeded PRNG with seed_day to choose spawn tiles and event details.
- Drone count = min(8, 2 + floor(station.day / 2)).
- Drone types:
  - If station.day < 3: all mites.
  - If station.day is 3-6: first min(count, 1) wraith, remaining mites.
  - If station.day >= 7: first min(count, 1) overseer, next min(count, 1) wraith, remaining mites.
- For each spawned drone, choose a floor tile that is not within 8 tile of player, not within 2 tile of another newly spawned drone, and not on a Station Object or Hazard. If 20 attempts fail for one drone, skip that drone.
- Event choice: choose by weight among Threat Events not equal to last_event_1, last_event_2, or last_event_3. For vent_burst or radiation_leak, choose a floor tile not within 5 tile of player and not occupied by a Station Object, Loot Container, or existing Hazard. If placement fails, choose another eligible event. If no eligible event can be applied, apply no event.
- VERIFIER for the daily generator:
  - At least one drone spawn tile is found unless drone count is 0.
  - No drone spawn tile is within 8 tile of player.
  - No two drone spawn tiles are on the same tile.
  - If an event is applied, all event effects are valid: placement hazards are not within 5 tile of player, power_surge target exists, hull_crack target exists, supply_drop placement fits in hub, and threat_level remains 1-10.
- Re-roll with the next seed_day if any check fails.

## Map Generator

### Initial SEEDED GENERATOR

- Input: a 32-bit seed. If no seed is provided, seed = current time in milliseconds modulo 2^32. Use a seeded PRNG with that seed.
- World size: 48x30 tile grid. All tiles start as wall.
- Carve hub: carve floor rectangle from x = 20 to x = 27 and y = 12 to y = 17.
- Place hub_console at tile (24, 15).
- Set player start position to (23.5, 15.5).
- Create 11 additional rooms. For each room, make up to 50 attempts:
  - Choose width 4-8 and height 4-6.
  - Choose top-left x from 2-41 and y from 2-23.
  - Discard if the room plus a 2-tile margin overlaps any existing carved floor rectangle.
  - Otherwise carve the room.
  - Connect the new room center to the nearest existing floor center with a 1-tile-wide L-shaped corridor, carving wall tiles as needed.
- Place 4 scrubbers:
  - Choose 4 distinct floor tiles in rooms with width * height >= 24, or any floor if not enough.
  - No two scrubbers may be closer than 4 tile.
  - Do not place on hub_console, power_bay, hull_seal, Loot Container, or Hazard.
- Place 3 power_bays:
  - Choose 3 distinct floor tiles not closer than 4 tile to another Station Object.
  - Do not place on an occupied tile.
- Place 5 hull_seals:
  - Choose 5 floor tiles adjacent to at least one wall tile.
  - No hull_seal may be within 2 tile of another Station Object.
- Place 24 Loot Containers in this fixed content order:
  1. scrap
  2. scrap
  3. scrap
  4. scrap
  5. scrap
  6. scrap
  7. scrap
  8. scrap
  9. battery
  10. battery
  11. battery
  12. battery
  13. filter
  14. filter
  15. filter
  16. fuse
  17. fuse
  18. o2_cell
  19. o2_cell
  20. o2_cell
  21. medkit
  22. medkit
  23. repair_kit
  24. hull_patch
- Each Loot Container is placed on a floor tile not occupied by another Loot Container, Station Object, or Hazard, and not within 2 tile of player start.
- Place 3 vent hazards and 3 radiation hazards on floor tiles not occupied by Station Objects or Loot Containers and not within 4 tile of player start.
- Spawn 2 mite enemies on floor tiles at least 12 tile from player start, not within 2 tile of another enemy, and not on a Station Object or Hazard.
- VERIFIER for the initial map:
  - All floor tiles are reachable from player start through floor tiles.
  - All 4 scrubbers, 3 power_bays, and 5 hull_seals are reachable from player start.
  - At least 24 Loot Containers exist.
  - At least 3 o2_cell, 2 medkit, 1 repair_kit, and 1 hull_patch exist.
  - No Hazard or initial enemy is within 3 tile of player start.
  - No tile contains two Station Objects, Loot Containers, or Hazards.
  - hub_console exists at tile (24, 15).
- Re-roll with the next seed if any check fails.

# 4. PROGRESSION AND DIFFICULTY

Early game is easy because station starts with power 50, oxygen 60, hull 70, scrubbers at integrity 70 with load 4, power bays at integrity 60 with load 3, only 2 mites are active, no Threat Event occurs on day 1, and the player starts with 1 o2_cell, 1 medkit, 2 scrap, 1 battery, and 1 filter.

Unlock order:
- Day 1: O2 Cell recipe, bare repair, O2 cells and basic resources from loot.
- Day 2: Medkit and Hull Patch recipes, first Threat Event, threat_level 2, drone count 3.
- Day 3: wraith first appears, beacon_day3 milestone, drone count 3.
- Day 4: Repair Kit recipe, station.hull begins decaying 1 per day, drone count 4.
- Day 7: overseer first appears, threat_level 7, drone count 5.
- Day 10: threat_level reaches 10, drone count 7.
- Day 12 and later: drone count reaches the 8 cap.

Difficulty increases because threat_level raises enemy health, damage, and speed; daily drone count rises; station hull decays after day 3; random events damage seals, power bays, and oxygen; and active hazards drain station oxygen and player oxygen or health.

The player is expected to fail by:
- letting station power fall below 15, which stops scrubbers and drops station oxygen;
- sprinting too often near drones, triggering noise detection;
- ignoring damaged hull_seals, which drain station oxygen;
- running out of o2_cell and medkit when personal oxygen or health is low;
- being overwhelmed after day 7 when overseer and wraith spawn together.

Recovery in a run comes from O2 cells, medkits, bare repair, Repair Kits, hull patches, coolant disabling hazards, crafting, and beacon milestones. If the player dies or station hull reaches 0, the run ends and the player recovers by retrying a new run with a new seed and updated best_day/best_score.

# 5. FEEL

- Walk speed is 3 tile/s, sprint speed is 5 tile/s, acceleration is 12 tile/s^2, deceleration is 20 tile/s^2. This makes walking feel deliberate and sprinting feel like a dangerous burst rather than free movement.
- Player attack cooldown is 0.5 s, range is 1.2 tile, arc is 120 degrees, and enemy knockback is 0.5 tile. This lets the player punish one enemy at a time without becoming a damage sponge.
- Enemy windup is 0.4 s, player knockback is 0.3 tile, and noise radii are 5 tile for sprinting and 2 tile for walking. This makes movement noise a real decision: sprinting escapes hazards but attracts drones.
- Personal oxygen drain is 0.4/s, low station oxygen adds 0.6/s, and station oxygen at 75+ regenerates personal oxygen at 1.5/s. An O2 cell adds 35 oxygen, which is enough for a short recovery but not enough to ignore scrubbers.
- Station oxygen base decay is 0.5/s, and each active scrubber adds 0.35/s. With four scrubbers active, station oxygen slowly rises; with three, it rises slowly; with two or fewer, the station begins losing air unless leaks are repaired.
- Power base drain is 3/s, each scrubber costs 2/s, and each power_bay adds 5/s. Three working bays keep a four-scrubber station powered, but one failed bay or low battery load forces the player to repair before crafting and oxygen both stall.
- Stamina drain is 20/s and regen is 15/s after a 0.5 s delay. Sprinting is useful for 5 seconds before stamina begins to pressure the player.
- Loot open is 0.3 s, item insertion is 0.5 s, bare repair is 1 s, Repair Kit repair is 2 s, and crafting takes 2 s or 3 s. These times make the station feel like a place where the player can be interrupted, not a menu-only survival game.
- Day length is 240 s. Hazard disable duration is 120 s. Enemy search decay begins after 5 s without player contact. Enemy object sabotage begins after 10 s without player contact. These timers create repeated loops: clean the station, hunt the next threat, then reinforce before the next day.

# 6. HUD AND SCREENS

Screens: title (shows Run Record.best_day, Run Record.best_score, and New Run button) → run (gameplay, HUD, optional craft menu overlay) → pause (shows Resume, Restart, Title) → game_over (shows station.day, station.score, Run Record.best_day, Run Record.best_score, and Retry/Title buttons).

- Title: Enter or Space starts a new run.
- Run: W/ArrowUp, S/ArrowDown, A/ArrowLeft, D/ArrowRight move; Shift sprints; Space/J attacks; E interacts, uses personal items, or opens craft menu at hub_console; Q/Tab cycles selected slot; number keys 1-10 select slots; P or Escape opens pause.
- Craft menu: open only at hub_console; number keys 1-4 select recipes; E or Escape closes menu; moving cancels active crafting.
- Pause: P or Escape resumes; R restarts a new run; T returns to title.
- Game over: Enter retries a new run; T returns to title.
- Touch: left virtual joystick moves; Action button performs E; Attack button performs Space; Sprint button performs Shift hold; Item button performs Q.

| HUD element | record field shown | visible when |
|---|---|---|
| Player health bar | Player.health / Player.health_cap | always during run |
| Player oxygen bar | Player.oxygen | always during run |
| Player stamina bar | Player.stamina / Player.stamina_cap | always during run |
| Day and time | Station.day, Station.day_timer | always during run |
| Station power bar | Station.power | always during run |
| Station oxygen bar | Station.oxygen | always during run |
| Station hull bar | Station.hull | always during run |
| Beacon meter | Station.beacon | always during run |
| Score | Station.score | always during run |
| Inventory slots | Inventory Slot.item_id, Inventory Slot.count, Player.selected_slot | always during run |
| Interaction prompt | contextual target action | when a valid target is within 1.5 tile |
| Craft menu | unlocked recipes, required Item counts, station.power | while open at hub_console |
| Event banner | Threat Event.event_id | for 5 s after a Threat Event applies |