3D, top-down orthographic camera centered on the player with north fixed up.

# 1. THE GAME IN ONE PARAGRAPH

This is an open-world island treasure hunt: the player explores a generated 3D island from a top-down view, rows a boat, walks over land, uses sonar and a compass, unlocks locked caches, and buries or digs treasure. Minute to minute, the player chooses a heading, follows the compass to the next map fragment, manages stamina and weather, avoids currents, whirlpools, and sharks, and loots caches. Finding the six map fragments reveals the Final Treasure at the island’s center; looting it ends the run with a score screen. The game is worth doing again because every run uses a new seed, changing terrain, cache positions, hazards, and weather timing while keeping the same objective structure and fixed cache roster.

# 2. RECORDS

RECORDS: GameRun, Island, Player, TreasureCache, TreasureItem, MapFragment, Tool, Weather, Hazard

## GameRun

A GameRun is one full island attempt. It carries: `id` (integer, starting 1, range 1 to 9999999), `seed` (integer, starting from Island.seed, range 1 to 999999), `valuePts` (points, starting 0, range 0 to 999999), `fragmentsCollected` (count, starting 0, range 0 to 6), `cachesLooted` (count, starting 0, range 0 to 13), `timeSec` (seconds, starting 0, range 0 to 999999), `finalCompleted` (boolean, starting false), `paused` (boolean, starting false), and `mapOpen` (boolean, starting false).

## Island

An Island is the generated world container. It carries: `seed` (integer, starting from input or 123456, range 1 to 999999), `widthTiles` (count, starting 256, fixed 256), `heightTiles` (count, starting 256, fixed 256), `tileSizeM` (meters, starting 10, fixed 10), `waterLevelM` (meters, starting 0, fixed 0), `maxLandHeightM` (meters, starting 60, fixed 60), `oceanFloorM` (meters, starting -15, fixed -15), `startXM` (meters, starting 0, fixed 0), `startZM` (meters, starting 1150, fixed 1150), `startRadiusM` (meters, starting 120, fixed 120), `finalXM` (meters, starting 0, fixed 0), `finalZM` (meters, starting 0, fixed 0), and `finalRadiusM` (meters, starting 60, fixed 60).

## Player

The Player is the controlled treasure hunter. It carries: `xM` (meters, starting 0, range -1280 to 1280), `zM` (meters, starting 1150, range -1280 to 1280), `headingDeg` (degrees, starting 0, range 0 to 359, 0 is north and 90 is east), `speedMS` (meters/second, starting 0, range 0 to 5.5), `healthPts` (points, starting 100, range 0 to 100), `staminaPts` (points, starting 100, range 0 to 100), `inWater` (boolean, starting false), `isOnBoat` (boolean, starting false), `sonarCooldownSec` (seconds, starting 0, range 0 to 10), `lastDamageSec` (seconds, starting -10, range 0 to GameRun.timeSec), and `ownedToolIds` (array of string, starting `["shovel", "sonar", "compass"]`).

## TreasureCache

A TreasureCache is one diggable or openable treasure location. It carries: `id` (string, fixed from `cache01` to `cache13`), `name` (string, from table), `xM` (meters, base table value plus seeded offset -20 to 20, range -1280 to 1280), `zM` (meters, base table value plus seeded offset -20 to 20, range -1280 to 1280), `depthM` (meters, from table, range 0 to 5), `requiredToolIds` (array of string, from table), `fragmentId` (integer, from table, range 0 to 6), `lootItemId` (string, from table, may be empty), `lootToolId` (string, from table, may be empty), `lootCount` (count, from table, range 1 to 3), `digTimeSec` (seconds, from table, range 1.2 to 5.0), `interactRangeM` (meters, starting 3.0, fixed 3.0), `discovered` (boolean, starting false), `looted` (boolean, starting false), `digProgressSec` (seconds, starting 0, range 0 to `digTimeSec`), and `sonarRevealedSec` (seconds, starting 0, range 0 to 6).

| id | name | baseXM | baseZM | depthM | requiredToolIds | fragmentId | lootItemId | lootToolId | lootCount | digTimeSec |
|---:|---|---:|---:|---:|---|---:|---|---|---:|---:|
| cache01 | Start Beach Cache | 0 | 1100 | 0 | shovel | 1 | silverCoin |  | 2 | 1.2 |
| cache02 | Tide Pool Cache | 400 | 850 | 0.5 | shovel | 2 | goldCoin | lantern | 3 | 1.5 |
| cache03 | Driftwood Camp Cache | 1100 | 0 | 0 | shovel | 0 | goldCoin |  | 2 | 1.5 |
| cache04 | Lagoon Cave Cache | 850 | -650 | 0 | shovel, lantern | 3 | pearl |  | 1 | 2.0 |
| cache05 | Shallow Reef Cache | 0 | -1100 | 2 | shovel, sonar | 4 | goldCoin | divingMask | 2 | 1.5 |
| cache06 | Deep Grotto Cache | -850 | -650 | 4 | shovel, sonar, divingMask | 5 | coralGem |  | 1 | 2.0 |
| cache07 | Coral Garden Cache | -1100 | 0 | 1 | shovel, sonar | 0 | pearl |  | 2 | 1.8 |
| cache08 | Volcanic Cave Cache | -850 | 650 | 0 | shovel, lantern, divingMask | 6 | ancientIdol |  | 1 | 2.4 |
| cache09 | Shipwreck Cache | -450 | 950 | 3 | shovel, sonar, divingMask | 0 | sunkenBlade |  | 1 | 2.0 |
| cache10 | Cliffs Cache | 450 | 950 | 0 | shovel, lantern | 0 | coralGem |  | 2 | 1.8 |
| cache11 | Lighthouse Vault | 300 | 150 | 0 | shovel, lantern | 0 | tideTalisman |  | 1 | 2.0 |
| cache12 | Sea Cavern Cache | -300 | -150 | 5 | shovel, sonar, divingMask, lantern | 0 | ancientIdol |  | 2 | 2.2 |
| cache13 | Final Treasure | 0 | 0 | 0 | shovel, sonar, lantern, divingMask | 0 | gildedIdol |  | 1 | 5.0 |

## TreasureItem

A TreasureItem is a loot type that converts to score when a cache is looted. It carries: `id` (string, fixed from roster), `name` (string, fixed from roster), and `valuePts` (points, fixed from roster).

| id | name | valuePts |
|---|---|---:|
| silverCoin | Silver Coin | 3 |
| goldCoin | Gold Coin | 5 |
| pearl | Pearl | 10 |
| coralGem | Coral Gem | 20 |
| ancientIdol | Ancient Idol | 40 |
| sunkenBlade | Sunken Blade | 60 |
| tideTalisman | Tide Talisman | 100 |
| gildedIdol | Gilded Idol | 1000 |

## MapFragment

A MapFragment is one of the six required objective clues. It carries: `id` (integer, starting 1 to 6, fixed roster), `name` (string, fixed from roster), `cacheId` (string, fixed from roster), `valuePts` (points, starting 500, fixed 500), and `discovered` (boolean, starting false).

| id | name | cacheId | valuePts | discovered |
|---:|---|---|---:|---|
| 1 | Fragment I | cache01 | 500 | false |
| 2 | Fragment II | cache02 | 500 | false |
| 3 | Fragment III | cache04 | 500 | false |
| 4 | Fragment IV | cache05 | 500 | false |
| 5 | Fragment V | cache06 | 500 | false |
| 6 | Fragment VI | cache08 | 500 | false |

## Tool

A Tool is a required or usable device. It carries: `id` (string, fixed from roster), `name` (string, fixed from roster), `useMode` (string, `passive` or `active`, fixed from roster), `reachM` (meters, fixed from roster), `actionTimeSec` (seconds, fixed from roster), `staminaPerSec` (points/second, fixed from roster), `cooldownSec` (seconds, fixed from roster), `effectRadiusM` (meters, fixed from roster), and `startingOwned` (boolean, fixed from roster).

| id | name | useMode | reachM | actionTimeSec | staminaPerSec | cooldownSec | effectRadiusM | startingOwned |
|---|---|---|---:|---:|---:|---:|---:|---|
| shovel | Shovel | passive | 3 | 0 | 0 | 0 | 3 | true |
| sonar | Sonar | active | 60 | 0.8 | 10 | 10 | 60 | true |
| compass | Compass | passive | 600 | 0 | 0 | 0 | 600 | true |
| lantern | Lantern | passive | 0 | 0 | 0 | 0 | 0 | false |
| divingMask | Diving Mask | passive | 0 | 0 | 0 | 0 | 0 | false |

## Weather

Weather is the current atmospheric condition. It carries: `id` (string, fixed from roster), `name` (string, fixed from roster), `remainingSec` (seconds, set to `durationSec` when weather starts, range 0 to `durationSec`), `durationSec` (seconds, fixed from roster), `windDirDeg` (degrees, fixed from roster, 0 north, 90 east), `visibilityM` (meters, fixed from roster), `currentMS` (meters/second, fixed from roster), and `damagePerSec` (points/second, fixed from roster).

| id | name | durationSec | windDirDeg | visibilityM | currentMS | damagePerSec |
|---|---|---:|---:|---:|---:|---:|
| clear | Clear | 180 | 0 | 600 | 0 | 0 |
| fog | Fog | 120 | 90 | 150 | 0 | 0 |
| storm | Storm | 60 | 180 | 300 | 1.5 | 1 |

## Hazard

A Hazard is an autonomous environmental danger. It carries: `id` (string, generated unique), `type` (string, `current`, `whirlpool`, or `shark`), `xM` (meters, generated, range -1280 to 1280), `zM` (meters, generated, range -1280 to 1280), `homeXM` (meters, equal to `xM` for shark, otherwise 0, range -1280 to 1280), `homeZM` (meters, equal to `zM` for shark, otherwise 0, range -1280 to 1280), `directionDeg` (degrees, generated 0 to 359 for current, 0 otherwise), `radiusM` (meters, from roster), `speedMS` (meters/second, from roster), `detectionM` (meters, from roster), `damagePerSec` (points/second, from roster), `biteDamagePts` (points, from roster), `attackCooldownSec` (seconds, from roster), `staminaPerSec` (points/second, from roster), `active` (boolean, starting true), and `lastAttackSec` (seconds, starting 0, range 0 to 1).

| type | radiusM | speedMS | detectionM | damagePerSec | biteDamagePts | attackCooldownSec | staminaPerSec |
|---|---:|---:|---:|---:|---:|---:|---:|
| current | 40 | 1.0 | 0 | 0 | 0 | 0 | 2 |
| whirlpool | 8 | 2.5 | 0 | 5 | 0 | 0 | 0 |
| shark | 2 | 5.0 | 50 | 0 | 10 | 1.0 | 0 |

# 3. SYSTEMS

SYSTEMS: SEEDED GENERATOR, Movement and Controls, Tools and Treasure, Weather, Hazards, Survival

## SEEDED GENERATOR

The SEEDED GENERATOR creates each run in this order: Island, TreasureCache roster, MapFragment roster, Hazards, Weather.

- New Island:
  - If the player enters a seed, use it. If no seed is entered, use seed 123456.
  - If the player chooses New Island from the Treasure Found screen, use the previous seed plus 1; if the previous seed is 999999, use 1.
- Island:
  - Set Island fields to their starting values.
  - Generate a 256 by 256 height grid from the seed.
  - Each tile farther than 1200m from the center has height -15m.
  - Each tile within 1200m of the center has height from -15m to 60m, rising with radial falloff from -15m at 1200m distance to 60m at 0m distance, with seeded noise amplitude 12m.
  - Force every tile within 120m of `startXM`, `startZM` to height 0.2m.
  - Force every tile within 60m of `finalXM`, `finalZM` to height 2.0m.
- TreasureCache:
  - Create 13 TreasureCache records using the fixed roster table.
  - For each cache, set `xM` to `baseXM` plus a seeded offset from -20 to 20, and `zM` to `baseZM` plus a seeded offset from -20 to 20.
  - Set `interactRangeM` to 3.0, `discovered` to false, `looted` to false, `digProgressSec` to 0, and `sonarRevealedSec` to 0.
- MapFragment:
  - Create 6 MapFragment records using the fixed roster table.
  - Set every `discovered` field to false.
- Hazards:
  - Place 4 current hazards, 3 whirlpool hazards, and 2 shark hazards using the seed.
  - Set each hazard’s type fields from the Hazard roster table.
  - For each shark, set `homeXM` and `homeZM` equal to its spawn `xM` and `zM`.
  - Set every `active` to true and every `lastAttackSec` to 0.
- Weather:
  - Set Weather to `id` clear and `remainingSec` 180.
- VERIFIER:
  - The tile under `startXM`, `startZM` has height 0.2m.
  - The tile under `finalXM`, `finalZM` has height 2.0m.
  - For each TreasureCache:
    - if `depthM` is 0, the tile under the cache has height at least 0.2m;
    - if `depthM` is greater than 0, the tile under the cache has height at most -1.0m.
  - For each Hazard:
    - its tile has height less than 0m;
    - it is within 1280m of the island center;
    - current and whirlpool hazards are more than 300m from `startXM`, `startZM`;
    - shark hazards are more than 500m from `startXM`, `startZM`;
    - every hazard is more than 50m from every TreasureCache;
    - every shark is more than 100m from every TreasureCache with `fragmentId` greater than 0;
    - every hazard is more than 20m from every other hazard.
  - re-roll with the next seed if any check fails.

## Movement and Controls

Movement and Controls fire while `GameRun.paused` is false and `GameRun.mapOpen` is false.

- Keyboard controls:
  - W and Up Arrow both move forward, input vector `0, -1`.
  - S and Down Arrow both move backward, input vector `0, 1`.
  - A and Left Arrow both move left, input vector `-1, 0`.
  - D and Right Arrow both move right, input vector `1, 0`.
  - Shift sprints while on land.
  - E holds interact/dig.
  - Q uses sonar.
  - F toggles the boat while in water.
  - M opens or closes the map.
  - Escape closes the map if open; otherwise toggles pause.
- Touch controls:
  - Left half of screen is a virtual joystick with input range -1 to 1 on both axes and deadzone 0.1.
  - Right side has buttons labeled RUN, DO, SCAN, BOAT, MAP, and MENU.
  - RUN maps to Shift.
  - DO maps to E.
  - SCAN maps to Q.
  - BOAT maps to F.
  - MAP maps to M.
  - MENU maps to Escape.
- Input:
  - Use the touch joystick if its magnitude is greater than 0.1.
  - Otherwise use the keyboard input vector, normalized to length 1 if any movement key is held.
  - If no movement input is held, input vector is `0, 0`.
- Water state:
  - If the tile under Player has height less than Island.waterLevelM, set Player.inWater to true.
  - If the tile under Player has height at least Island.waterLevelM, set Player.inWater to false.
  - If Player.inWater becomes false, set Player.isOnBoat to false.
- Boat toggle:
  - If F or BOAT is pressed and Player.inWater is true, set Player.isOnBoat to the opposite value.
- Land movement:
  - If Player.inWater is false:
    - If Shift or RUN is held, E is not held, and Player.staminaPts is greater than 0, target speed is 4.5 m/s.
    - Otherwise, if Player.staminaPts is greater than 0, target speed is 2.2 m/s.
    - Otherwise, target speed is 1.5 m/s.
    - Player.speedMS approaches target speed at 12 m/s².
    - If sprinting, Player.staminaPts decreases by 12 points/second.
    - If not sprinting and not digging, Player.staminaPts increases by 15 points/second.
    - Player.xM and Player.zM move by input vector times Player.speedMS times elapsed seconds.
- Water movement:
  - If Player.inWater is true:
    - If Player.isOnBoat is true:
      - target speed is 4.5 m/s during storm and 5.5 m/s otherwise.
      - Player.speedMS approaches target speed at 6 m/s².
      - Player.staminaPts increases by 10 points/second.
      - Player.headingDeg turns toward the input direction at 90 degrees/second.
    - If Player.isOnBoat is false:
      - target speed is 1.4 m/s if Player.staminaPts is greater than 0, otherwise 0.7 m/s.
      - Player.speedMS approaches target speed at 8 m/s².
      - Player.staminaPts decreases by 8 points/second.
      - If Player.staminaPts is 0, Player.healthPts decreases by 2 points/second.
    - Player.xM and Player.zM move by input vector times Player.speedMS times elapsed seconds.
- Weather current:
  - If Player.inWater is true and Weather.currentMS is greater than 0:
    - Player.xM and Player.zM move by Weather.windDirDeg vector times Weather.currentMS times elapsed seconds.
- Bounds:
  - Clamp Player.xM and Player.zM to -1280 and 1280.

## Tools and Treasure

Tools and Treasure fire while `GameRun.paused` is false and `GameRun.mapOpen` is false.

- Cache discovery:
  - For each TreasureCache that is not `discovered` and not `looted`:
    - If distance from Player to the cache is at most 3.0m;
    - and every id in `requiredToolIds` is in Player.ownedToolIds;
    - and if `depthM` is greater than 0, Player.inWater is true;
    - and if the cache id is `cache13`, GameRun.fragmentsCollected is 6;
    - set `discovered` to true.
- Digging:
  - Let target cache be the nearest TreasureCache where `discovered` is true, `looted` is false, and distance from Player is at most 3.0m.
  - If target exists, E or DO is held, every required tool is owned, and depth rules are met:
    - target.digProgressSec increases by elapsed seconds.
    - Player.staminaPts decreases by 8 points/second.
    - If Player.staminaPts becomes 0, target.digProgressSec resets to 0.
    - If target.digProgressSec is at least target.digTimeSec, loot the cache.
  - If E or DO is not held, distance is greater than 3.0m, or requirements are not met, target.digProgressSec resets to 0.
- Looting:
  - When a cache is looted:
    - set `looted` to true.
    - set `digProgressSec` to 0.
    - increase GameRun.cachesLooted by 1.
    - if `lootItemId` is not empty, add TreasureItem.valuePts times `lootCount` to GameRun.valuePts.
    - if `lootToolId` is not empty and is not already in Player.ownedToolIds, add it.
    - if `fragmentId` is not 0:
      - set the matching MapFragment.discovered to true.
      - increase GameRun.fragmentsCollected by 1.
      - add 500 points to GameRun.valuePts.
    - if the cache id is `cache13`, set GameRun.finalCompleted to true.
  - Looted caches do not restock.
- Sonar:
  - If Q or SCAN is pressed, Player.ownedToolIds includes `sonar`, Player.sonarCooldownSec is 0, and Player.staminaPts is at least 8:
    - decrease Player.staminaPts by 8.
    - set Player.sonarCooldownSec to 10.
    - For each TreasureCache where `discovered` is false, `looted` is false, `depthM` is greater than 0, and distance from Player is at most 60m, set `sonarRevealedSec` to 6.
- Cooldowns and sonar reveals:
  - Player.sonarCooldownSec decreases by elapsed seconds, minimum 0.
  - For each TreasureCache, `sonarRevealedSec` decreases by elapsed seconds, minimum 0.
- Compass:
  - If GameRun.fragmentsCollected is less than 6:
    - target is the nearest TreasureCache where `fragmentId` is greater than 0, `discovered` is false, and `looted` is false.
  - If GameRun.fragmentsCollected is 6 and GameRun.finalCompleted is false:
    - target is TreasureCache `cache13`.
  - If no target exists, compass shows no arrow.
  - If target exists and distance from Player to target is at most both Tool `compass` effectRadiusM 600 and Weather.visibilityM, compass shows an arrow to target.
  - Compass updates at 10 times per second.

## Weather

Weather fires while `GameRun.paused` is false and `GameRun.mapOpen` is false.

- Timer:
  - Weather.remainingSec decreases by elapsed seconds.
  - If Weather.remainingSec is 0:
    - if Weather.id is clear, next id is fog;
    - if Weather.id is fog, next id is storm;
    - if Weather.id is storm, next id is clear.
    - set Weather.remainingSec to the new weather’s `durationSec`.
- Fog effect:
  - Fog reduces compass range through Weather.visibilityM 150.
- Storm effect:
  - If Player.inWater is true:
    - Player is pushed by Weather.currentMS 1.5 m/s in Weather.windDirDeg 180.
    - If Player.isOnBoat is false, Player.healthPts decreases by Weather.damagePerSec 1 point/second.
    - If Player.isOnBoat is true, boat target speed is reduced to 4.5 m/s by Movement rules.

## Hazards

Hazards fire while `GameRun.paused` is false and `GameRun.mapOpen` is false.

- Current:
  - If Player distance to a current Hazard is at most Hazard.radiusM 40:
    - Player moves by Hazard.directionDeg vector times Hazard.speedMS 1.0 m/s times elapsed seconds.
    - Player.staminaPts decreases by Hazard.staminaPerSec 2 points/second.
- Whirlpool:
  - If Player distance to a whirlpool Hazard is at most Hazard.radiusM 8:
    - Player moves toward the whirlpool center by Hazard.speedMS 2.5 m/s times elapsed seconds.
    - If Player distance to the whirlpool center is at most 3m, Player.healthPts decreases by Hazard.damagePerSec 5 points/second.
- Shark:
  - For each shark Hazard:
    - Hazard.lastAttackSec decreases by elapsed seconds, minimum 0.
    - If Player.inWater is false:
      - If shark distance to its home position is greater than 2m, shark moves toward home at 3.0 m/s.
      - No damage.
    - If Player.inWater is true and Player.isOnBoat is true:
      - If shark distance to Player is greater than 5m, shark moves toward Player at 4.0 m/s.
      - No damage.
    - If Player.inWater is true and Player.isOnBoat is false:
      - If shark distance to Player is at most Hazard.detectionM 50, shark moves toward Player at Hazard.speedMS 5.0 m/s.
      - If shark distance to Player is greater than 80, shark moves toward home at 3.0 m/s.
      - If shark distance to Player is at most Hazard.radiusM 2 and Hazard.lastAttackSec is 0:
        - decrease Player.healthPts by Hazard.biteDamagePts 10.
        - set Hazard.lastAttackSec to Hazard.attackCooldownSec 1.0.
        - push Player 2m away from the shark.

## Survival

Survival fires while `GameRun.paused` is false and `GameRun.mapOpen` is false.

- Clamping:
  - Player.staminaPts is clamped to 0 to 100.
  - Player.healthPts is clamped to 0 to 100.
- Regen:
  - If Player.inWater is false, E is not held, Shift is not held, and Weather.id is not storm:
    - If GameRun.timeSec minus Player.lastDamageSec is greater than 3, Player.healthPts increases by 2 points/second.
- Damage timestamp:
  - Whenever Player.healthPts decreases from a hazard, storm, or exhaustion, set Player.lastDamageSec to GameRun.timeSec.
- Injury and recovery:
  - If Player.healthPts becomes 0:
    - set Player.xM to 0.
    - set Player.zM to 1150.
    - set Player.healthPts to 50.
    - set Player.staminaPts to 50.
    - set Player.isOnBoat to false.
    - set Player.speedMS to 0.
    - set Player.lastDamageSec to GameRun.timeSec.
    - set GameRun.valuePts to floor of GameRun.valuePts times 0.8.
    - show an injured message for 2 seconds.
  - Looted caches and discovered fragments remain unchanged after injury.

# 4. PROGRESSION AND DIFFICULTY

Progression is the order in which the player gains access to the main objective. The intended path is: Start Beach Cache gives Fragment I; Tide Pool Cache gives Fragment II and Lantern; Lagoon Cave Cache requires Lantern and gives Fragment III; Shallow Reef Cache gives Fragment IV and Diving Mask; Deep Grotto Cache requires Diving Mask and gives Fragment V; Volcanic Cave Cache requires Lantern and Diving Mask and gives Fragment VI; Final Treasure requires all six fragments.

The early game is easy because the first two caches are within 380m of the start, no current or whirlpool may be closer than 300m from the start, no shark may be closer than 500m from the start, and the first weather is clear for 180 seconds. The mid game becomes harder because the player must travel across the island, manage sonar cooldown, find the Lantern and Diving Mask, and survive fog with compass visibility reduced to 150m. The late game is hardest because Fragment V and Fragment VI require deep, dark, or tool-locked caches, storm current is 1.5 m/s, storm swimming damage is 1 point/second, whirlpool pull is 2.5 m/s, and shark damage is 10 points per bite.

The player is expected to fail through exhaustion while swimming, whirlpool pull, shark bites, or storm damage. Recovery is injury respawn at the start beach with health 50, stamina 50, and 20% of current value lost. Progress is not erased: looted caches stay looted, fragments stay collected, and tools stay owned.

# 5. FEEL

The numbers are tuned so that exploration feels active but not twitchy, water feels risky, and treasure discovery feels rewarding.

- Camera:
  - Top-down orthographic default view width is 240m.
  - Zoom in is 180m.
  - Zoom out is 320m.
  - North is fixed up.
  - The camera centers on the player every frame.
- Movement:
  - Walk speed 2.2 m/s is tuned to make the island feel large without making early caches feel far.
  - Sprint speed 4.5 m/s is tuned to make crossing open land feel urgent but stamina-limited.
  - Swim speed 1.4 m/s is tuned to make water feel slower and more exposed.
  - Exhausted swim speed 0.7 m/s is tuned to make low stamina feel dangerous.
  - Boat speed 5.5 m/s is tuned so most island crossings take about 2 to 7 minutes.
  - Storm boat speed 4.5 m/s is tuned to make storms slow travel without making it impossible.
  - Land acceleration 12 m/s² is tuned for immediate responsiveness.
  - Swim acceleration 8 m/s² is tuned for softer water movement.
  - Boat acceleration 6 m/s² is tuned for heavier movement.
  - Boat turn rate 90 degrees/second is tuned for simple top-down boating.
- Reach and cooldowns:
  - Cache interact range 3m is tuned so the player must be close but does not need pixel-perfect alignment.
  - Sonar radius 60m is tuned to reveal nearby underwater caches without revealing the whole island.
  - Sonar reveal duration 6 seconds is tuned to give a short window to plan a route.
  - Sonar cooldown 10 seconds is tuned to make sonar a deliberate tool.
  - Compass range 600m is tuned to guide the player across the island, but weather can reduce it.
- Stamina:
  - Sprint drain 12 points/second lets one full sprint last about 8.3 seconds.
  - Swim drain 8 points/second lets one full swim last about 12.5 seconds.
  - Dig drain 8 points/second makes deep or long digs tense if stamina is low.
  - Land regen 15 points/second recovers in about 6.7 seconds from full drain.
  - Boat regen 10 points/second recovers while rowing but slower than on land.
- Health:
  - Health regen 2 points/second after 3 seconds encourages finding safe land.
  - Shark bite 10 points means ten bites kill from full health.
  - Whirlpool damage 5 points/second makes the inner 3m zone lethal in 20 seconds.
  - Storm swim damage 1 point/second makes storms punishing but survivable for short periods.
  - Exhausted swim damage 2 points/second makes running out of stamina in deep water dangerous.
- Timers:
  - Dig times 1.2 to 5.0 seconds make early caches quick and the Final Treasure feel like a ceremony.
  - Weather cycle clear 180, fog 120, storm 60 creates a predictable but tense rhythm.
  - Injury respawn penalty 20% value loss makes failure meaningful without ending the run.

# 6. HUD AND SCREENS

State machine:

`title (seed, New Island, How to Play)` → `help (controls and objective)` → `title`  
`title (New Island)` → `playing (island active)`  
`playing (M or MAP)` → `map (full map, world paused)` → `playing (M, MAP, or Escape)`  
`playing (Escape)` → `paused (resume, restart, title)`  
`paused (Resume or Escape)` → `playing`  
`paused (Restart)` → `playing (same seed)`  
`paused (Title)` → `title`  
`playing (final loot)` → `treasureFound (score, New Island, Title)`  
`treasureFound (New Island)` → `playing (next seed)`  
`treasureFound (Title)` → `title`

Key and button leads:

- Title:
  - Enter or Space starts New Island.
  - H or How to Play opens help.
  - Seed text box accepts 1 to 999999.
- Help:
  - Escape or Back returns to title.
- Playing:
  - WASD and arrows move.
  - Shift or RUN sprints.
  - E or DO digs.
  - Q or SCAN uses sonar.
  - F or BOAT toggles boat.
  - M or MAP opens map.
  - Escape or MENU opens pause unless map is open.
- Map:
  - M, MAP, or Escape closes map.
- Paused:
  - Enter, R, or Resume resumes.
  - Escape resumes.
  - Restart button restarts with the same seed.
  - Title button returns to title.
- Treasure Found:
  - N or New Island starts next seed.
  - Esc or Title returns to title.

HUD table:

| HUD element | Record field shown | Visible when |
|---|---|---|
| Objective text | GameRun.fragmentsCollected, GameRun.finalCompleted | playing, not map |
| Fragment count | GameRun.fragmentsCollected | playing, not map |
| Score | GameRun.valuePts | playing, not map |
| Compass arrow | MapFragment.discovered, TreasureCache.fragmentId, Weather.visibilityM, Tool.compass.effectRadiusM | playing, not map |
| Health bar | Player.healthPts | playing, not map |
| Stamina bar | Player.staminaPts | playing, not map |
| Weather icon and time | Weather.id, Weather.remainingSec | playing, not map |
| Water/boat state | Player.inWater, Player.isOnBoat | playing, not map |
| Sonar cooldown | Player.sonarCooldownSec | playing, not map, when greater than 0 |
| Tool icons | Player.ownedToolIds | playing, not map |
| Cache prompt | TreasureCache.name, TreasureCache.digProgressSec, TreasureCache.digTimeSec | playing, not map, when target cache within 3m |
| Minimap | Player.xM, Player.zM, TreasureCache.discovered, TreasureCache.sonarRevealedSec | playing, not map |
| Full map | Island, Player.xM, Player.zM, TreasureCache.discovered, TreasureCache.sonarRevealedSec | map |
| Seed | GameRun.seed | title, treasureFound |