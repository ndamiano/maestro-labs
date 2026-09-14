2D top-down browser game with a fixed 90° bird's-eye camera, no player-controlled rotation, zoom 1.0, player always centered.

# 1. THE GAME IN ONE PARAGRAPH
The player walks a 120×120 open world as a collector, routing between berry bushes, ore outcrops, and lake fishing spots each minute: harvest berries with Foraging Hands, strike ore with a Pickaxe, cast and reel fish with a Rod, carry items to three type-specific buyer shopkeepers, and buy tools, furniture, museum case slots, and home room unlocks from the General Shopkeeper. The loop keeps earning because better tools raise yield, better furniture raises Home Comfort and energy regen, filled Museum Cases raise Curation and daily visitor income, and rare items like Gemstone and Coralfish are worth more than common ones. There is no forced end: the player may keep collecting, decorating, and expanding the museum forever; the optional one-time Grand Opening fires once when Museum Curation reaches 100 and Home Comfort reaches 50, awards 1000 coins, and then the game continues.

# 2. RECORDS
RECORDS: World, Player, Inventory, ResourceNode, Shopkeeper, FurnitureInstance, Home, HomeRoom, Museum, MuseumCase, Day, Weather.

World is the persistent tile map. Fields: seed (integer, start 0), width (integer tiles, 120), height (integer tiles, 120), tiles (120×120 array of enum {grass, water, sand, mountain, interior}, start all grass), nodeIds (list of integer ids, range 1-70, start empty), fishingSpotIds (list of integer ids, range 1-12, start empty), shopkeeperIds (list of integer ids, range 1-4, start empty), playerStartX (integer tile, start 58), playerStartY (integer tile, start 58).

Player is the character and active tool state. Fields: id (string, start "player"), x (float tiles, start 58), y (float tiles, start 58), facing (integer 0-7, start 4), coins (integer coins, start 20), energy (integer energy points, 0-100, start 100), maxEnergy (integer energy points, 100, start 100), selectedToolId (string toolId, start "hands"), toolsOwned (list string toolId, start ["hands", "pickaxe1", "rod1"]), furnitureBag (list integer furnitureInstanceId, range 0-12, start empty), furnitureBagCount (integer pieces, 0-12, start 0), toolCooldown (float seconds, 0-1, start 0), focusedType (enum {none, shopkeeper, bed, case, node}, start none), focusedId (integer id, range 0-70, start 0), fishingState (enum {idle, casting, bitten, reeling}, start idle), fishingTimer (float seconds, 0-1, start 0), biteMark (float pixels, 0-200, start 0), biteWindow (float seconds, 0-2, start 0.9), sweetZone (integer pixels, 0-200, start 40), fishingSpotId (integer id, range 0-12, start 0), catchSuccess (boolean, start false).

Inventory is the carried resource/fish storage. Fields: slots (array length 20 of {itemId string or null, count integer 0-99}, start null/0), capacity (integer slots, 20), totalCount (integer items, 0-1980, start 0).

ResourceNode is a harvestable berry bush, mineable ore node, or lake fishing spot. Fields: id (integer id, range 1-70, set by generator), kind (enum {berry, ore, fishingSpot}), itemId (string resourceId, from Resource Roster, for berry/ore), x (integer tile, range 0-119, set by generator), y (integer tile, range 0-119, set by generator), stage (enum {full, empty}, start full), regrowTimer (float seconds, 0-720, start 0), remainingHits (integer strikes, 0-4, start 0), lakeType (integer 1-2, start 1).

Shopkeeper is a market stall that buys resources or sells tools/furniture/cases/room unlocks. Fields: id (string), kind (enum {berryBuyer, oreBuyer, fishBuyer, general}), x (integer tile, from roster), y (integer tile, from roster), openStart (float day fraction, 0.10), openEnd (float day fraction, 0.95), dailyCap (integer items, 0-60), dailyBought (integer items, 0-dailyCap, start 0), open (boolean, start false), toolStock (list {toolId string, count integer 0-1}, start per roster), furnitureStock (list {furnitureId string, count integer 0-3}, start per roster), caseCost (integer coins, 150 for general, 0 for others), parlorCost (integer coins, 200 for general, 0 for others), libraryCost (integer coins, 800 for general, 0 for others).

FurnitureInstance is one bought furniture piece and where it is placed. Fields: instanceId (integer id, range 1-999, start 1), definitionId (string furnitureId, from Furniture Roster), location (enum {bag, home, museum}, start bag), roomId (string HomeRoom id or null, start null), slotIndex (integer 0-7 or null, start null), comfort (integer points, from definition, range 0-10), museumPoints (integer points, from definition, range 0-10), refundCoins (integer coins, from definition, range 0-150).

Home is the player’s house and comfort total. Fields: x (integer tile, 56), y (integer tile, 56), w (integer tiles, 4), h (integer tiles, 14), comfort (integer points, 0-1000, start 0), rooms (list of 3 HomeRoom).

HomeRoom is one room in the house with furniture slots. Fields: id (string), name (string), x (integer tile, from roster), y (integer tile, from roster), w (integer tiles, from roster), h (integer tiles, from roster), unlocked (boolean, from roster), unlockCost (integer coins, from roster), slots (array length 8 of integer furnitureInstanceId or null, start null), roomComfort (integer points, 0-100, start 0).

Museum is the small museum building and its display state. Fields: x (integer tile, 48), y (integer tile, 50), w (integer tiles, 8), h (integer tiles, 6), activeCases (integer cases, 4-12, start 4), cases (list of 12 MuseumCase), decorSlots (array length 6 of integer furnitureInstanceId or null, start null), curation (integer points, 0-10000, start 0), visitorsToday (integer visitors, 0-20, start 0), incomeToday (integer coins, start 0), grandOpeningDone (boolean, start false), caseCost (integer coins, 150).

MuseumCase is one display case that can hold one collected item. Fields: id (integer 1-12), active (boolean, start per roster), x (integer tile, from roster), y (integer tile, from roster), itemId (string resourceId or null, start null), exhibitValue (integer points, start 0).

Day is the current day and time-of-day clock. Fields: dayNumber (integer day, start 1), timeOfDay (float day fraction 0-1, start 0.10), paused (boolean, start false), settledToday (boolean, start false), dawnDone (boolean, start true).

Weather is the current day’s weather and its gameplay modifiers. Fields: type (enum {sunny, rain, snow}, start sunny), berryYieldBonus (integer items, start 0), oreYieldBonus (integer items, start 0), fishSweetZoneBonus (integer pixels, start 0), fishBiteWindowDelta (float seconds, start 0), berryRegrowDelta (integer seconds, start 0).

Resource Roster

| itemId | kind | sellPrice (coins) | exhibitValue (points) | yieldMin (items) | yieldMax (items) | regrowSeconds (s) | requiredPickaxe (tier) | hitsToMine (strikes) | chanceLake1Day (%) | chanceLake1Night (%) | chanceLake2Day (%) | chanceLake2Night (%) | nightOnly (bool) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sunberry | berry | 2 | 1 | 1 | 3 | 60 | 0 | 0 | 0 | 0 | 0 | 0 | false |
| Blueberry | berry | 4 | 2 | 1 | 2 | 90 | 0 | 0 | 0 | 0 | 0 | 0 | false |
| Glowberry | berry | 9 | 4 | 1 | 1 | 180 | 0 | 0 | 0 | 0 | 0 | 0 | true |
| Copper | ore | 5 | 3 | 1 | 1 | 240 | 1 | 2 | 0 | 0 | 0 | 0 | false |
| Iron | ore | 12 | 6 | 1 | 1 | 360 | 2 | 3 | 0 | 0 | 0 | 0 | false |
| Gemstone | ore | 30 | 15 | 1 | 1 | 720 | 3 | 4 | 0 | 0 | 0 | 0 | false |
| Minnow | fish | 3 | 2 | 1 | 1 | 0 | 0 | 0 | 65 | 50 | 0 | 0 | false |
| Sunfish | fish | 6 | 4 | 1 | 1 | 0 | 0 | 0 | 35 | 30 | 55 | 40 | false |
| Moonfish | fish | 14 | 8 | 1 | 1 | 0 | 0 | 0 | 0 | 20 | 20 | 45 | false |
| Coralfish | fish | 25 | 15 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 25 | 15 | false |

Tool Roster

| toolId | kind | cost (coins) | tier | pickaxePower (strikes) | pickaxeEnergy (points) | pickaxeYieldBonus (items) | rodBiteWindow (s) | rodSweetZone (px) | rodEnergy (points) |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hands | forage | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| pickaxe1 | pickaxe | 0 | 1 | 1 | 5 | 0 | 0 | 0 | 0 |
| pickaxe2 | pickaxe | 120 | 2 | 2 | 4 | 1 | 0 | 0 | 0 |
| pickaxe3 | pickaxe | 450 | 3 | 3 | 3 | 2 | 0 | 0 | 0 |
| rod1 | rod | 0 | 1 | 0 | 0 | 0 | 0.9 | 40 | 5 |
| rod2 | rod | 90 | 2 | 0 | 0 | 0 | 0.8 | 55 | 5 |
| rod3 | rod | 260 | 3 | 0 | 0 | 0 | 0.7 | 70 | 5 |

Furniture Roster

| furnitureId | name | cost (coins) | comfort (points) | museumPoints (points) | refundCoins (coins) | allowed | maxPerRoom (pieces) |
|---|---|---:|---:|---:|---:|---|---:|
| woodenStool | Wooden Stool | 15 | 1 | 0 | 7 | home | 2 |
| berryShelf | Berry Shelf | 30 | 2 | 1 | 14 | both | 1 |
| copperLamp | Copper Wall Lamp | 45 | 3 | 2 | 22 | both | 1 |
| fishingBanner | Fishing Net Banner | 50 | 2 | 2 | 24 | both | 1 |
| ironTable | Iron Table | 80 | 4 | 2 | 40 | both | 1 |
| gemVitrine | Gemstone Vitrine | 120 | 2 | 5 | 60 | museum | 1 |
| sunflowerPot | Sunflower Pot | 60 | 3 | 1 | 30 | both | 2 |
| oldMap | Old Map | 70 | 1 | 3 | 35 | both | 1 |
| comfortChair | Comfort Chair | 100 | 5 | 1 | 50 | home | 2 |
| moonFishDisplay | Moon Fish Display | 150 | 1 | 6 | 75 | museum | 1 |
| ironFireplace | Iron Fireplace | 180 | 8 | 3 | 90 | home | 1 |
| collectorTrophy | Grand Collector Trophy | 300 | 5 | 10 | 150 | both | 1 |

Shopkeeper Roster

| shopkeeperId | name | kind | x (tile) | y (tile) | openStart | openEnd | dailyCap (items) | buysKind | sellsFurniture |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| berryBuyer | Berry Buyer | berryBuyer | 64 | 58 | 0.10 | 0.95 | 60 | berry | false |
| oreBuyer | Ore Buyer | oreBuyer | 66 | 58 | 0.10 | 0.95 | 40 | ore | false |
| fishBuyer | Fish Buyer | fishBuyer | 65 | 63 | 0.10 | 0.95 | 50 | fish | false |
| general | General Shopkeeper | general | 64 | 63 | 0.10 | 0.95 | 0 | none | true |

Home Room Roster

| roomId | name | x (tile) | y (tile) | w (tiles) | h (tiles) | unlocked | unlockCost (coins) | slots (count) |
|---|---|---:|---:|---:|---:|---|---:|---:|
| home1 | Start Room | 56 | 56 | 4 | 4 | true | 0 | 8 |
| home2 | Parlor | 56 | 61 | 4 | 4 | false | 200 | 8 |
| home3 | Library | 56 | 66 | 4 | 4 | false | 800 | 8 |

Museum Case Roster

| caseId | x (tile) | y (tile) | activeStart |
|---:|---:|---:|---|
| 1 | 49 | 51 | true |
| 2 | 51 | 51 | true |
| 3 | 53 | 51 | true |
| 4 | 55 | 51 | true |
| 5 | 49 | 53 | false |
| 6 | 50 | 53 | false |
| 7 | 51 | 53 | false |
| 8 | 52 | 53 | false |
| 9 | 53 | 53 | false |
| 10 | 54 | 53 | false |
| 11 | 55 | 53 | false |
| 12 | 48 | 52 | false |

# 3. SYSTEMS
SYSTEMS: World Generation, Time, Weather, Movement, Targeting, Energy, Foraging, Mining, Fishing, Selling, Buying, Inventory, Home, Museum.

There is no opponent. The opposing systems are time, energy, weather, shop daily caps, and restocking.

## World Generation
SEEDED GENERATOR:
- Input: World.seed.
- Step 1: Set all 120×120 World.tiles to grass.
- Step 2: Set tiles inside circle center (90,25) radius 14 to mountain.
- Step 3: Set Lake A water to circle center (24,32) radius 8; set Lake A sand ring to radius 9. Set Lake B water to circle center (92,84) radius 10; set Lake B sand ring to radius 11.
- Step 4: Set HomeRoom roster tiles to interior: home1 (56,56) to (59,59), home2 (56,61) to (59,64), home3 (56,66) to (59,69). Set bed at tile (57,57).
- Step 5: Set Museum tiles (48,50) to (55,55) to interior.
- Step 6: Set Market tiles (64,58) to (67,63) to interior.
- Step 7: Place Shopkeeper roster positions at their x/y tiles.
- Step 8: Place 40 ResourceNode kind berry. For node index 1-20, candidate tile must be inside circle center (30,90) radius 14. For node index 21-32, candidate tile must be inside circle center (30,90) radius 20. For node index 33-40, candidate tile can be anywhere. For each node, make up to 100 seeded random candidate integer tile coordinates in 0-119. Reject a candidate if the tile is not grass, is occupied by another node/fishing spot/shopkeeper, is within 3 tiles of any interior tile, or is within 1 tile of water. If accepted, place node. Assign itemId by node index: 1-14 Sunberry, 15-28 Blueberry, 29-40 Glowberry.
- Step 9: Place 30 ResourceNode kind ore. For node index 1-24, candidate tile must be inside circle center (90,25) radius 14. For node index 25-30, candidate tile can be anywhere. For each node, make up to 100 seeded random candidate integer tile coordinates in 0-119. Reject a candidate if the tile is not grass or mountain, is occupied, is within 3 tiles of any interior tile, or is within 1 tile of water. If accepted, place node. Assign itemId by node index: 1-12 Copper, 13-22 Iron, 23-30 Gemstone.
- Step 10: Place 12 ResourceNode kind fishingSpot. For Lake A, place 5 fishing spots on distinct sand tiles in the Lake A sand ring that are within 1 tile of water. For Lake B, place 7 fishing spots on distinct sand tiles in the Lake B sand ring that are within 1 tile of water. Use seeded random candidates, up to 100 attempts per spot, rejecting occupied tiles and non-adjacent-to-water sand. Set lakeType 1 for Lake A spots and lakeType 2 for Lake B spots.
- Step 11: Create 12 MuseumCase at Museum Case Roster coordinates; set active true for caseId 1-4 and false for caseId 5-12.
- Step 12: Set Player.x = World.playerStartX and Player.y = World.playerStartY.

VERIFIER:
- Check 1: All 40 berry nodes, 30 ore nodes, and 12 fishing spots were placed.
- Check 2: At least 12 berry nodes have distance <=10 tiles from (58,58).
- Check 3: At least 8 ore nodes have distance <=15 tiles from (90,25).
- Check 4: A breadth-first search from (58,58) through walkable tiles (grass, sand, mountain, interior) reaches all 4 shopkeepers, all 12 museum cases, at least 35 berry nodes, at least 25 ore nodes, and at least 10 fishing spots.
- Check 5: No two nodes share a tile; no node is on water; no node is on interior.
- If any check fails, re-roll with the next seed.

## Time
RULES:
- While game state is world and Day.paused is false, Day.timeOfDay += delta / 300.0. If Day.timeOfDay >= 1.0, Day.timeOfDay -= 1.0, Day.dayNumber += 1, Day.dawnDone = false.
- If Day.timeOfDay crosses 0.95 and Day.settledToday is false, set Day.settledToday = true and run Museum Daily Settlement.
- If Day.timeOfDay crosses 0.10 and Day.dawnDone is false, run Dawn and set Day.dawnDone = true.
- Every tick, set Shopkeeper.open = true if Day.timeOfDay >= 0.10 and Day.timeOfDay < 0.95; otherwise false.
- If Player.focusedType is bed, Player.focusedId identifies the bed, and Day.timeOfDay >= 0.75, pressing E or Space triggers Sleep:
  - If Day.settledToday is false, run Museum Daily Settlement and set Day.settledToday = true.
  - Set Day.dayNumber += 1, Day.timeOfDay = 0.10, Day.dawnDone = true, Player.energy = 100.
  - Run Dawn.
- Dawn:
  - Reset every Shopkeeper.dailyBought to 0.
  - Reset General Shopkeeper toolStock to pickaxe2=1, pickaxe3=1, rod2=1, rod3=1.
  - Reset General Shopkeeper furnitureStock to 3 for every furnitureId in Furniture Roster.
  - Roll Weather.
  - If Home.comfort >= 50, Player.coins += 30; else if Home.comfort >= 25, Player.coins += 15; else if Home.comfort >= 10, Player.coins += 5; else no change.

## Weather
RULES:
- At Dawn, roll one random integer 0-99 using the seeded random sequence.
- If roll 0-49, set Weather.type = sunny.
- If roll 50-79, set Weather.type = rain.
- If roll 80-99, set Weather.type = snow.
- Sunny sets: Weather.berryYieldBonus = 0, Weather.oreYieldBonus = 0, Weather.fishSweetZoneBonus = 0, Weather.fishBiteWindowDelta = 0, Weather.berryRegrowDelta = 0.
- Rain sets: Weather.berryYieldBonus = 1, Weather.oreYieldBonus = 0, Weather.fishSweetZoneBonus = 10, Weather.fishBiteWindowDelta = 0, Weather.berryRegrowDelta = -15.
- Snow sets: Weather.berryYieldBonus = 0, Weather.oreYieldBonus = 1, Weather.fishSweetZoneBonus = -10, Weather.fishBiteWindowDelta = -0.1, Weather.berryRegrowDelta = 30.

## Movement
RULES:
- Keyboard movement input vector: W or Up = (0, -1); S or Down = (0, 1); A or Left = (-1, 0); D or Right = (1, 0). If two axes are pressed, normalize the input vector to length 1.0.
- If input vector length > 0, target velocity = input vector × 4.0 tiles/s. If input vector length = 0, target velocity = (0, 0).
- Player velocity approaches target velocity at 10.0 tiles/s² when input is present and 12.0 tiles/s² when input is absent. Player velocity magnitude never exceeds 4.0 tiles/s.
- Player.x += velocity.x × delta and Player.y += velocity.y × delta. Move axes separately: an axis move is allowed only if the target tile is walkable. Walkable tiles are grass, sand, mountain, and interior. Water is not walkable.
- If input vector length > 0, set Player.facing to the nearest of 8 directions: 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW.
- If Player.fishingState is not idle, movement input is ignored and target velocity is (0, 0).
- Tool selection: 1 sets Player.selectedToolId to "hands" if owned. 2 sets Player.selectedToolId to the owned pickaxe with the highest tier. 3 sets Player.selectedToolId to the owned rod with the highest tier.
- Touch: left virtual joystick produces the same input vector as keyboard movement. Right-side buttons: Use triggers the same action as Space/E; Tool 1/2/3 trigger tool selection; Shop opens the nearest open shopkeeper if within 2.5 tiles; Home opens HomeMuseum; Inventory opens Inventory; Pause opens Pause.

## Targeting
RULES:
- Each tick, set Player.focusedType = none and Player.focusedId = 0.
- If any Shopkeeper is within 2.5 tiles, set Player.focusedType = shopkeeper and Player.focusedId to that shopkeeper’s id.
- Else if the bed at (57,57) is within 2.5 tiles, set Player.focusedType = bed and Player.focusedId = 0.
- Else if any active MuseumCase is within 2.5 tiles, set Player.focusedType = case and Player.focusedId to that case id.
- Else if any ResourceNode is within 2.5 tiles, choose the nearest ResourceNode and set Player.focusedType = node and Player.focusedId to that node id.
- If Player.focusedType is shopkeeper and Shopkeeper.open is false, the action is blocked and the prompt says Closed.
- If Player.focusedType is bed and Day.timeOfDay < 0.75, the action is blocked and the prompt says Night only.

## Energy
RULES:
- If Player.toolCooldown > 0, Player.toolCooldown -= delta; if < 0, set 0.
- Compute comfortBonus: if Home.comfort >= 50, comfortBonus = 0.6; else if Home.comfort >= 25, comfortBonus = 0.4; else if Home.comfort >= 10, comfortBonus = 0.2; else comfortBonus = 0.
- Player.energy += (1.0 + comfortBonus) × delta / 5.0. If Player.energy > Player.maxEnergy, set Player.energy = Player.maxEnergy.
- Sleep sets Player.energy = 100.

## Foraging
RULES:
- Let night = true if Day.timeOfDay >= 0.75 or Day.timeOfDay <= 0.10; otherwise false.
- A harvest is allowed if Player.focusedType = node, ResourceNode.kind = berry, Player.selectedToolId = hands, ResourceNode.stage = full, Player.toolCooldown = 0, Player.energy >= 2, and Inventory has space for the maximum possible yield.
- Maximum possible yield: if ResourceNode.itemId = Glowberry and night is false, maximum possible yield = 0. Else maximum possible yield = Resource Roster yieldMax + (Weather.type = rain and itemId in {Sunberry, Blueberry} ? Weather.berryYieldBonus : 0).
- On successful Use:
  - Player.energy -= 2.
  - Player.toolCooldown = 0.4.
  - Roll one integer uniformly from Resource Roster yieldMin to yieldMax.
  - If Weather.type = rain and itemId in {Sunberry, Blueberry}, add Weather.berryYieldBonus to the rolled count.
  - Add that count of ResourceNode.itemId to Inventory.
  - Set ResourceNode.stage = empty.
  - Set ResourceNode.regrowTimer = Resource Roster regrowSeconds + Weather.berryRegrowDelta. If ResourceNode.regrowTimer < 15, set ResourceNode.regrowTimer = 15.
- If ResourceNode.stage = empty and ResourceNode.regrowTimer > 0, ResourceNode.regrowTimer -= delta. If ResourceNode.regrowTimer <= 0, set ResourceNode.regrowTimer = 0 and ResourceNode.stage = full.

## Mining
RULES:
- Let tool = Tool Roster entry for Player.selectedToolId. A mine strike is allowed if Player.focusedType = node, ResourceNode.kind = ore, ResourceNode.stage = full, ResourceNode.remainingHits > 0, Player.selectedToolId kind = pickaxe, tool.tier >= Resource Roster requiredPickaxe, Player.toolCooldown = 0, Player.energy >= tool.pickaxeEnergy, and Inventory has space for the maximum possible final yield.
- Maximum possible final yield: Resource Roster yieldMax + tool.pickaxeYieldBonus + (Weather.type = snow and itemId in {Copper, Iron} ? Weather.oreYieldBonus : 0).
- On successful Use:
  - Player.energy -= tool.pickaxeEnergy.
  - Player.toolCooldown = 0.45.
  - ResourceNode.remainingHits -= tool.pickaxePower.
  - If ResourceNode.remainingHits > 0, no item is added.
  - If ResourceNode.remainingHits <= 0:
    - Add maximum possible final yield of ResourceNode.itemId to Inventory.
    - Set ResourceNode.stage = empty.
    - Set ResourceNode.regrowTimer = Resource Roster regrowSeconds.
- If ResourceNode.stage = empty and ResourceNode.regrowTimer > 0, ResourceNode.regrowTimer -= delta. If ResourceNode.regrowTimer <= 0, set ResourceNode.regrowTimer = 0, ResourceNode.stage = full, ResourceNode.remainingHits = Resource Roster hitsToMine.

## Fishing
RULES:
- Let tool = Tool Roster entry for Player.selectedToolId. A cast is allowed if Player.focusedType = node, ResourceNode.kind = fishingSpot, Player.selectedToolId kind = rod, Player.fishingState = idle, Player.toolCooldown = 0, Player.energy >= tool.rodEnergy, and Inventory has space for 1 item.
- On successful Use:
  - Player.energy -= tool.rodEnergy.
  - Player.fishingState = casting.
  - Player.fishingTimer = 0.
  - Player.fishingSpotId = ResourceNode.id.
  - Player.catchSuccess = false.
- Casting: while Player.fishingState = casting, Player.fishingTimer += delta. If Player.fishingTimer >= 0.8, set Player.fishingState = bitten, Player.fishingTimer = 0, Player.biteMark = 0.
  - Player.biteWindow = tool.rodBiteWindow + Weather.fishBiteWindowDelta. If Player.biteWindow < 0.5, set Player.biteWindow = 0.5.
  - Player.sweetZone = tool.rodSweetZone + Weather.fishSweetZoneBonus. If Player.sweetZone < 20, set Player.sweetZone = 20.
- Bitten: while Player.fishingState = bitten, Player.biteMark += (200.0 / Player.biteWindow) × delta.
  - If Use is pressed while bitten:
    - If Player.biteMark >= 100 - Player.sweetZone / 2 and Player.biteMark <= 100 + Player.sweetZone / 2, Player.catchSuccess = true; else Player.catchSuccess = false.
    - Set Player.fishingState = reeling and Player.fishingTimer = 0.
  - If no press is made and Player.biteMark >= 200, set Player.catchSuccess = false, Player.fishingState = reeling, Player.fishingTimer = 0.
- Reeling: while Player.fishingState = reeling, Player.fishingTimer += delta. If Player.fishingTimer >= 0.5:
  - If Player.catchSuccess is true, add 1 fish to Inventory using the spot’s lakeType and night table.
  - Set Player.fishingState = idle and Player.toolCooldown = 0.5.
- Fish selection:
  - Let spot = ResourceNode with id Player.fishingSpotId.
  - Let night = true if Day.timeOfDay >= 0.75 or Day.timeOfDay <= 0.10; otherwise false.
  - If spot.lakeType = 1 and night is false, use chances: Minnow 65, Sunfish 35.
  - If spot.lakeType = 1 and night is true, use chances: Minnow 50, Sunfish 30, Moonfish 20.
  - If spot.lakeType = 2 and night is false, use chances: Sunfish 55, Moonfish 20, Coralfish 25.
  - If spot.lakeType = 2 and night is true, use chances: Sunfish 40, Moonfish 45, Coralfish 15.
  - Roll one integer 1-100. In the fixed order Minnow, Sunfish, Moonfish, Coralfish, add the first species whose cumulative chance is >= roll.

## Selling
RULES:
- A buyer Shopkeeper can be opened only if Shopkeeper.open is true and the player is within 2.5 tiles.
- In Shop state for berryBuyer, oreBuyer, or fishBuyer, Sell All is available for each Inventory slot whose itemId kind matches Shopkeeper.buysKind.
- If Sell All is pressed for itemId:
  - Let remainingCap = Shopkeeper.dailyCap - Shopkeeper.dailyBought.
  - Let sellCount = min(Inventory slot count, remainingCap).
  - If sellCount > 0:
    - Player.coins += sellCount × Resource Roster sellPrice for itemId.
    - Remove sellCount from that Inventory slot.
    - Shopkeeper.dailyBought += sellCount.
- If sellCount = 0, no field changes.

## Buying
RULES:
- General Shopkeeper is the only shopkeeper that sells tools, furniture, case slots, home room unlocks, and refunds furniture.
- Buy Tool is available if the General Shopkeeper is open, tool is not in Player.toolsOwned, Shopkeeper.toolStock count for tool > 0, and Player.coins >= Tool Roster cost.
  - On buy: Player.coins -= cost, Shopkeeper.toolStock count -= 1, add toolId to Player.toolsOwned.
  - If Tool Roster kind for tool is the same as Player.selectedToolId’s kind, set Player.selectedToolId = toolId.
- Buy Furniture is available if General Shopkeeper is open, Shopkeeper.furnitureStock count for furnitureId > 0, Player.coins >= Furniture Roster cost, and Player.furnitureBagCount < 12.
  - On buy: Player.coins -= cost, Shopkeeper.furnitureStock count -= 1, create FurnitureInstance with definitionId = furnitureId, location = bag, add to Player.furnitureBag, Player.furnitureBagCount += 1.
- Buy Museum Case is available if Museum.activeCases < 12 and Player.coins >= Museum.caseCost (150).
  - On buy: Player.coins -= 150, Museum.activeCases += 1, set the lowest inactive MuseumCase id to active = true.
- Unlock Home Room is available for an unlocked = false HomeRoom if Player.coins >= HomeRoom.unlockCost.
  - On unlock: Player.coins -= HomeRoom.unlockCost, HomeRoom.unlocked = true.
- Refund Furniture is available for any FurnitureInstance with location = bag.
  - On refund: Player.coins += FurnitureInstance.refundCoins, remove that FurnitureInstance from Player.furnitureBag, Player.furnitureBagCount -= 1.
- At Dawn, General Shopkeeper.toolStock resets and Shopkeeper.furnitureStock resets as defined in Time.

## Inventory
RULES:
- Inventory has 20 slots. Each slot holds one itemId and an integer count 0-99.
- AddItem(itemId, count):
  - First, find a slot with the same itemId and count + added count <= 99. If found, increase that slot count.
  - Else find an empty slot and set itemId with count.
  - Else the add fails and no fields change.
- RemoveItem(itemId, count):
  - Decrease the matching slot count by count.
  - If a slot count becomes 0, set its itemId = null and count = 0.
- Player.furnitureBagCount is the count of entries in Player.furnitureBag and may not exceed 12.
- Adding a FurnitureInstance to Player.furnitureBag increases Player.furnitureBagCount by 1.
- Removing a FurnitureInstance from Player.furnitureBag decreases Player.furnitureBagCount by 1.

## Home
RULES:
- Home has 3 HomeRoom records. Only unlocked HomeRooms can hold furniture.
- Place Furniture in Home is available from Player.furnitureBag if:
  - The chosen HomeRoom.unlocked is true.
  - The chosen HomeRoom slot is null.
  - Furniture Roster allowed for definitionId includes home.
  - The count of the same definitionId in that HomeRoom is < Furniture Roster maxPerRoom.
  - On place: remove instance from Player.furnitureBag, set FurnitureInstance.location = home, FurnitureInstance.roomId = HomeRoom.id, FurnitureInstance.slotIndex = chosen slot, set HomeRoom.slot to FurnitureInstance.instanceId, Player.furnitureBagCount -= 1.
- Remove Furniture from Home is available if Player.furnitureBagCount < 12.
  - On remove: set HomeRoom slot to null, FurnitureInstance.location = bag, FurnitureInstance.roomId = null, FurnitureInstance.slotIndex = null, add instance to Player.furnitureBag, Player.furnitureBagCount += 1.
- Recompute Home.comfort after any place, remove, or unlock:
  - For each unlocked HomeRoom, HomeRoom.roomComfort = sum of FurnitureInstance.comfort in that room’s slots.
  - Home.comfort = sum of HomeRoom.roomComfort for all unlocked HomeRoom.

## Museum
RULES:
- Museum has 12 MuseumCase records and 6 decorSlots.
- Place Exhibit is available if a MuseumCase.active is true, MuseumCase.itemId is null, and the chosen Inventory itemId has count > 0.
  - On place: Remove 1 from that Inventory slot, set MuseumCase.itemId = itemId, MuseumCase.exhibitValue = Resource Roster exhibitValue for itemId.
- Remove Exhibit is available if MuseumCase.itemId is not null and Inventory has space for 1 item.
  - On remove: Add 1 MuseumCase.itemId to Inventory, set MuseumCase.itemId = null, MuseumCase.exhibitValue = 0.
- Place Furniture in Museum is available from Player.furnitureBag if:
  - The chosen Museum.decorSlots entry is null.
  - Furniture Roster allowed for definitionId includes museum.
  - The count of the same definitionId already in Museum.decorSlots is < Furniture Roster maxPerRoom.
  - On place: remove instance from Player.furnitureBag, set FurnitureInstance.location = museum, set the decorSlots entry to FurnitureInstance.instanceId, Player.furnitureBagCount -= 1.
- Remove Furniture from Museum is available if Player.furnitureBagCount < 12.
  - On remove: set the decorSlots entry to null, FurnitureInstance.location = bag, add instance to Player.furnitureBag, Player.furnitureBagCount += 1.
- Recompute Museum.curation after any exhibit or furniture change:
  - Museum.curation = sum of MuseumCase.exhibitValue for all active cases with itemId not null + sum of FurnitureInstance.museumPoints for all FurnitureInstance with location = museum.
- Museum Daily Settlement:
  - If Museum.curation 0-9, Museum.visitorsToday = 0.
  - If Museum.curation 10-24, Museum.visitorsToday = 1.
  - If Museum.curation 25-49, Museum.visitorsToday = 3.
  - If Museum.curation 50-99, Museum.visitorsToday = 6.
  - If Museum.curation 100-199, Museum.visitorsToday = 10.
  - If Museum.curation 200-999, Museum.visitorsToday = 15.
  - If Museum.curation >= 1000, Museum.visitorsToday = 20.
  - Museum.incomeToday = Museum.visitorsToday × 4.
  - Player.coins += Museum.incomeToday.
  - If Museum.grandOpeningDone is false and Museum.curation >= 100 and Home.comfort >= 50, set Museum.grandOpeningDone = true and Player.coins += 1000.

# 4. PROGRESSION AND DIFFICULTY
What grows: Player.coins, Player.toolsOwned, Home.comfort, Museum.curation, Museum.activeCases, and unlocked HomeRoom entries. What unlocks, in intended order: Rod T2 (90), Pickaxe T2 (120), first extra Museum Case (150), Home Parlor (200), more Museum Cases (150 each), Pickaxe T3 (450), Rod T3 (260), Home Library (800), then endless furniture/museum completion. Early game is easy because Sunberry yields 1-3, sells for 2, costs only 2 energy, regrows in 60 seconds, and at least 12 berry nodes are guaranteed within 10 tiles of the start. Ten Sunberry harvests can produce 20-60 coins, enough to approach Rod T2 or Pickaxe T2 by day 2. Mid game becomes more effortful because Copper sells for 5 but requires 2 strikes with Pickaxe T1, Iron requires Pickaxe T2, and Glowberry is night-only. Late game is harder because Gemstone requires Pickaxe T3, 4 strikes, and 720-second regrow; Coralfish only appears at Lake 2 and is most common at night; Home Comfort 50 and Museum Curation 100 require multiple high-value furniture pieces and many good exhibits. The player is expected to run out of energy, fill Inventory, hit buyer daily caps, and fail fishing casts. Recovery is always non-lethal: Sleep restores energy to 100, selling frees inventory and coins, Dawn resets buyer caps and General stock, and better tools reduce strikes/cast difficulty.

# 5. FEEL
- Movement speed 4.0 tiles/s: fast enough to cross a 12-tile gap in 3 seconds, slow enough to choose between two nearby nodes.
- Acceleration 10.0 tiles/s² and deceleration 12.0 tiles/s²: starts feel responsive but stopping is crisp enough for precise reach.
- Reach 2.5 tiles: one clear step from a node, not long-range clicking.
- Harvest cooldown 0.4s and energy cost 2: berry gathering should feel rapid, about 2.5 harvests per minute at full pace.
- Mine cooldown 0.45s and Pickaxe T1 energy 5: Copper takes 2 strikes and about 1.35 seconds, Iron 3 strikes, Gemstone 4 strikes only with T3.
- Fishing cast 0.8s, bite window 0.9/0.8/0.7s for Rod T1/T2/T3, reel 0.5s, fish cooldown 0.5s: a full T1 cast cycle is about 2.3 seconds plus cooldown, so fishing is slower than berry picking and rewards better rods.
- Sweet zone 40/55/70 pixels on a 200-pixel bar: T1 is tight, T2 is comfortable, T3 is forgiving.
- Energy max 100, base regen 1 point per 5 seconds, comfort bonuses +0.2/+0.4/+0.6 per 5 seconds at Comfort 10/25/50: max regen is 1.6 points per 5 seconds, so home comfort matters by late game.
- Day length 300 seconds, dawn 0.10, shop open 0.10-0.95, museum settlement 0.95: one full day is 5 minutes, with a clear morning-to-night rhythm.
- No knockback: this is a collector game, not a combat game; movement feel comes from speed, reach, and cooldowns.
- Menu open transition 0.15 seconds: screens feel immediate without interrupting the walking loop.

# 6. HUD AND SCREENS
Screen state machine:
- title (title, New Game, Continue, Controls) → world: Enter, New Game, or Continue.
- world → shop: E or Space on an open Shopkeeper within 2.5 tiles, or touch Shop button near an open Shopkeeper.
- world → inventory: I or touch Inventory.
- world → homeMuseum: H or E on an active MuseumCase, or touch Home.
- world → pause: Escape or P, or touch Pause.
- shop → world: Escape, E, Space, or Close.
- inventory → world: Escape, E, Space, or Close.
- homeMuseum → world: Escape, E, Space, or Close.
- pause → world: Escape, Resume, or Close.
- pause → title: Quit.
- In world: WASD and arrows both move; Space or E uses the focused target; 1/2/3 select Foraging Hands, best owned Pickaxe, best owned Rod; Escape pauses.
- In shop: buttons control Sell All, Buy Tool, Buy Furniture, Buy Case, Unlock Room, Refund Furniture.
- In homeMuseum: tabs are Home and Museum; buttons control place/remove furniture and place/remove exhibits.
- Escape behavior: title does nothing; world opens pause; shop/inventory/homeMuseum close that screen to world; pause returns to world.

HUD table:

| HUD element | Record field shown | Visible when |
|---|---|---|
| Coins | Player.coins | world, shop, homeMuseum, pause |
| Energy | Player.energy / Player.maxEnergy | world |
| Clock | Day.timeOfDay, Day.dayNumber | world |
| Weather | Weather.type | world |
| Selected tool | Player.selectedToolId | world |
| Inventory bar | Inventory.slots | world |
| Furniture bag count | Player.furnitureBagCount | world |
| Focused prompt | Player.focusedType, Player.focusedId | world when Player.focusedType is not none |
| Home comfort | Home.comfort | world, homeMuseum |
| Museum curation | Museum.curation | world, homeMuseum |
| Museum visitors/income | Museum.visitorsToday, Museum.incomeToday | world, homeMuseum |
| Shop open state | Shopkeeper.open | shop |
| Shop daily cap | Shopkeeper.dailyBought, Shopkeeper.dailyCap | shop for berryBuyer, oreBuyer, fishBuyer |
| Tool stock | Shopkeeper.toolStock | shop for general |
| Furniture stock | Shopkeeper.furnitureStock | shop for general |
| Case cost | Museum.caseCost | shop for general, homeMuseum |
| Room unlock cost | HomeRoom.unlockCost | shop for general, homeMuseum |