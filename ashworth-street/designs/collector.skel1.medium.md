# BUILD SPEC — Orchard Hollow

## 0. SCOPE

### 0.1 Asked

- "open world collector game" → 3D outdoor world (compose_world), free-movement player, scattered collectible objects (sections 3: World Generator, Movement)
- "the player walks around" → third-person 3D controller, WASD/arrows (section 1 Controls)
- "collecting resources" → inventory record, three gathering systems (Harvesting, Mining, Fishing)
- "harvest berries" → berry bushes as world objects, pick mechanic, bush depletion and respawn (system: Harvesting)
- "mine ores" → ore rocks as world objects, swing-to-mine mechanic, rock depletion and respawn (system: Mining)
- "fish fish" → fishing spots on the lake, cast-wait-reel mechanic, species table (system: Fishing)
- "sell them to a shop keeper for each type" → shop NPC, per-resource buy prices, coins (system: Trading)
- "buy furniture to decorate their home" → furniture roster, home interior grid, placement mechanic (system: Furniture)
- "a small museum type building" → museum building with display cases, exhibit items, prestige score (system: Museum)

### 0.2 Decisions

- **3D, outdoor.** The player walks a rolling landscape with a lake, meadows, rocky hills, and a village clearing. A third-person 3D view over varied terrain gives the sense of "walking around an open world" that a flat 2D map cannot. The world comes from `compose_world("a gentle meadow with a small lake to the north, scattered wild berry bushes on the eastern slopes, rocky outcrop hills to the west with visible ore veins, and a flat clearing to the south holding three small buildings", seed)`. The response gives world size in metres and a list of regions each with category, centre, and radius; the World Generator places content by rule on those regions.
- **Furniture uses a fixed interior grid** (6 × 4 tile grid inside the house, 4 × 3 inside the museum) rather than free placement. Reason: a grid is legible in 3D, makes placement a single click/press, and prevents overlapping. The museum grid is called "display cases" and holds exhibit items only; the home grid holds furniture only.
- **No enemies, no combat.** The challenge is the open world itself: distances, resource depletion timers, and the progression of filling two interiors. Reason: the user asked for a collector, not a survivor.
- **Museum earns "Visitors" per in-game hour**, a passive income that scales with the prestige of displayed items. Reason: gives the museum a mechanical purpose beyond decoration and creates a reason to seek rarer items.
- **Three tool tiers per gathering type** (basic / mid / advanced), bought from the shop. Reason: gives the shop repeat visits and makes later resources faster to gather.
- **Day/night cycle is cosmetic and gameplay-neutral** (lighting only, 4-minute full cycle). Reason: sets mood and helps the player track time for respawn timers without punishing them.
- **No save/persistence across sessions.** Each playthrough is one run from empty pockets to a full museum. Reason: keeps the scope bounded and the progression arc complete.

### 0.3 Tiers

**TIER 1 (the game):** World Generator, Movement, Harvesting, Mining, Fishing, Inventory, Trading, Furniture, Museum, HUD.

**TIER 2 (makes it good), in order:**
1. Day/night lighting cycle with warm dusk and cool night tint.
2. Berry bushes show a 3-stage visual (full → half → bare) so depletion is readable at a distance.
3. Fishing bobber animates with a subtle ripple ring in the water.
4. A small ambient music loop (soft strings + woodwind) that changes to a slightly richer arrangement once the museum has 6+ exhibits.
5. Tool upgrade visual: the pickaxe/rod mesh colour shifts (grey → copper → gold) per tier.
6. A short "collection complete" jingle and a gold banner overlay when all 12 museum slots are filled.
7. Walking dust particles behind the player on grass; splash particles when entering water.

**TIER 3 (never started before all T2 is in):**
- Seasonal rotation (every 4 game-days the berry species swaps, one ore type disappears).
- A second shopkeeper on a small boat who trades fish-only deals.

---

## 1. CONVENTIONS

- **Units.** One world unit = 1 metre. One screen pixel at 1080p maps to roughly 0.04 m at the default camera distance. Furniture grid tiles are 1 m × 1 m. The player is 1.7 m tall.
- **Axes.** X is east, Y is up (out of the ground), Z is south. The player faces north (−Z) at yaw 0. Yaw increases clockwise (pressing A strafes left / turns left = yaw increases). Pitch is fixed at −20° (camera looks slightly down).
- **Origin.** World centre (0, 0, 0) is the centre of the village clearing (the south region from compose_world). Ground height is read from the terrain; the player's Y is always ground height at their X,Z.
- **Camera.** Third-person, behind the player. Camera offset: 4 m back along the player's facing, 2.5 m above the player's feet. Camera looks at a point 1 m in front of the player at the player's chest height. No rotation independent of the player.
- **Update loop.** Fixed step, dt = 1/60 s. Each tick the systems run in this order: (1) Movement, (2) Harvesting check, (3) Mining check, (4) Fishing tick, (5) Respawner, (6) Trading (if shop open), (7) Museum visitor tick, (8) Day/night timer, (9) HUD refresh. Rendering happens after the last system.
- **Randomness.** One seeded source, `RNG`, created as `RNG = mulberry32(initialSeed)`. Every call to `RNG()` is the only randomness in the game. No `Math.random()` anywhere. The seed is set by `seed(n)` in the debug API or defaults to 42 at launch.
- **Controls.**

| Input | Action |
|---|---|
| W / ArrowUp | Move forward (strafe along facing) |
| S / ArrowDown | Move backward |
| A / ArrowLeft | Turn left (yaw +) |
| D / ArrowRight | Turn right (yaw −) |
| F | Interact: pick berry / swing pickaxe / cast or reel fishing line / open shop or museum door |
| E | Open or close the interaction menu (shop purchase/sell menu, furniture placement menu, museum placement menu) |
| 1 – 3 | Select gathering tool slot 1 / 2 / 3 (berry hand, pickaxe, fishing rod) |
| Escape | Close any open menu; if no menu, open pause overlay |
| Click (mouse) | In placement mode: place selected furniture / exhibit on the highlighted grid tile |
| Touch (mobile) | Left half of screen: virtual joystick for movement + turning. Right half: tap = Interact (F), long-press = Menu (E). |

---

## 2. RECORDS

RECORDS: Player, Inventory, ResourceItem, FurnitureItem, ExhibitItem, BerryBush, OreRock, FishingSpot, GridTile, Museum, Shop, GameClock

**PLAYER:** position (x, y, z in metres, starting at 0, groundY, 0 which is the village clearing centre), yaw (degrees, 0 = facing north/−Z, starting 0), pitch (fixed −20°), moveSpeed (m/s, starting 4.5, range 4.5), interactTarget (reference to a BerryBush / OreRock / FishingSpot / Shop / HomeDoor / MuseumDoor, or null), currentTool (enum: "hands", "pickaxe", "fishingRod", starting "hands"), toolTiers (object: pickaxeTier integer 1-3 starting 1, rodTier integer 1-3 starting 1), inWater (boolean, starting false).

**INVENTORY:** a map from resource key (string: "strawberry", "blueberry", "blackberry", "copper", "iron", "gold", "minnow", "perch", "trout", "pike", "specimen_trout", "specimen_pike", "specimen_gold", "specimen_blackberry") to count (integer, starting 0). coins (integer, starting 50). totalCollected (object: count per resource key, integer, starting 0 — lifetime, never decreases).

**RESOURCEITEM:** roster of all collectible and sellable things.

| Key | Display name | Sell price (coins) | Source system | Gather yield per action |
|---|---|---|---|---|
| strawberry | Strawberry | 3 | Harvesting | 1–2 |
| blueberry | Blueberry | 4 | Harvesting | 1–2 |
| blackberry | Blackberry | 5 | Harvesting | 1–1 |
| copper | Copper Ore | 8 | Mining | 1–1 |
| iron | Iron Ore | 15 | Mining | 1–1 |
| gold | Gold Ore | 35 | Mining | 1–1 |
| minnow | Minnow | 4 | Fishing | 1–1 |
| perch | Perch | 7 | Fishing | 1–1 |
| trout | Trout | 12 | Fishing | 1–1 |
| pike | Pike | 20 | Fishing | 1–1 |
| specimen_trout | Trout Specimen | 0 (museum only) | Fishing (rare) | 1–1 |
| specimen_pike | Pike Specimen | 0 (museum only) | Fishing (rare) | 1–1 |
| specimen_gold | Gold Nugget Specimen | 0 (museum only) | Mining (rare) | 1–1 |
| specimen_blackberry | Blackberry Bundle | 0 (museum only) | Harvesting (rare) | 1–1 |

**FURNITUREITEM:** roster of buyable home decorations.

| Key | Display name | Price (coins) | Grid size (tiles) | Category |
|---|---|---|---|---|
| rug_oak | Oak Rug | 20 | 1×1 | floor |
| rug_moss | Moss Rug | 30 | 1×1 | floor |
| table_small | Small Table | 40 | 1×1 | table |
| table_large | Large Table | 60 | 2×1 | table |
| chair_wood | Wooden Chair | 25 | 1×1 | seat |
| chair_cushion | Cushioned Chair | 45 | 1×1 | seat |
| bed_single | Single Bed | 80 | 1×2 | bed |
| shelf_wood | Wooden Shelf | 35 | 1×1 | storage |
| shelf_display | Display Shelf | 55 | 1×1 | storage |
| lamp_oil | Oil Lamp | 30 | 1×1 | light |
| lamp_candle | Candle Stand | 20 | 1×1 | light |
| painting_berries | "Berry Pickers" (painting) | 100 | 1×1 | wall |
| painting_lake | "Lake at Dusk" (painting) | 120 | 1×1 | wall |
| plant_pot | Potted Fern | 15 | 1×1 | decor |
| plant_cactus | Cactus | 10 | 1×1 | decor |
| mirror_oval | Oval Mirror | 90 | 1×1 | wall |
| clock_wall | Wall Clock | 50 | 1×1 | wall |
| chest_wood | Wooden Chest | 65 | 1×1 | storage |
| fireplace | Stone Fireplace | 150 | 1×2 | light |
| rug_pattern | Patterned Rug | 50 | 2×2 | floor |

**EXHIBITITEM:** roster of items that go in the museum.

| Key | Display name | Prestige value | Price (coins, buy from shop) | Notes |
|---|---|---|---|---|
| case_minnow | Minnow in Jar | 2 | 10 | always available |
| case_perch | Perch on Stand | 5 | 25 | always available |
| case_trout | Preserved Trout | 10 | 60 | always available |
| case_pike | Pike Skeletal Mount | 20 | 120 | always available |
| case_specimen_trout | Trout Specimen | 30 | 0 | must catch in game |
| case_specimen_pike | Pike Specimen | 45 | 0 | must catch in game |
| case_specimen_gold | Gold Nugget Display | 50 | 0 | must mine in game |
| case_specimen_blackberry | Blackberry Botanical Display | 15 | 0 | must harvest in game |
| case_fossil | "Fossil" (decorative) | 8 | 40 | always available |
| case_shell | Sea Shell Collection | 4 | 15 | always available |
| case_map | Old Survey Map | 12 | 50 | always available |
| case_clockwork | Clockwork Orrery | 35 | 100 | always available |

**BERRYBUSH:** position (x, y, z in metres), berryType (enum: "strawberry" | "blueberry" | "blackberry"), stage (integer 0-2: 0 = full, 1 = half, 2 = bare, starting 0), picksRemaining (integer, starting 3), respawnTimer (seconds, starting 0; counts down when stage = 2), rareDropPending (boolean, starting false — set to true on the 3rd pick of a blackberry bush to flag the rare drop).

**OREROCK:** position (x, y, z in metres), oreType (enum: "copper" | "iron" | "gold"), hitsNeeded (integer: copper 3, iron 5, gold 8, starting per type), hitsTaken (integer, starting 0), depletes (boolean, starting false — set true when hitsTaken reaches hitsNeeded), respawnTimer (seconds, starting 0), rareDropPending (boolean, starting false — set true on the final hit of a gold rock to flag the rare drop).

**FISHINGSPOT:** position (x, y, z in metres), depth (enum: "shallow" | "deep"), currentCatch (enum of fish key, set when a fish is reeled), state (enum: "idle" | "casting" | "waiting" | "biting" | "caught", starting "idle"), biteTimer (seconds, starting 0 — counts up during "waiting"), reelingTimer (seconds, starting 0 — counts up during "biting"; player must press F within 1.5 s or the fish escapes).

**GRIDTILE:** position (row, col integers), building (enum: "home" | "museum"), furnitureKey (string key into FURNITUREITEM or EXHIBITITEM roster, or null if empty, starting null), occupied (boolean, derived: true if furnitureKey is not null).

**MUSEUM:** slots (array of 12 references to GridTile, all in the museum building, starting all empty), prestigeScore (integer, starting 0 — sum of prestige values of all filled slots), visitorsPerHour (integer, starting 0 — computed each visitor tick), coinIncomePerHour (integer, starting 0), totalVisitors (integer, starting 0), allFilled (boolean, starting false — true when all 12 slots have an exhibit).

**SHOP:** shopkeeperName ("Aldric"), open (boolean, starting false — true while the player is within 3 m of the shop door and has pressed F), selectedTab (enum: "sell" | "furniture" | "museum" | "tools", starting "sell").

**GAMECLOCK:** time (seconds since game start, starting 0), dayLength (seconds, given 240 — one full day is 240 s), dayCount (integer, starting 1 — increments every 240 s), phase (enum: "dawn" | "day" | "dusk" | "night", derived from time % dayLength: 0-30 dawn, 30-180 day, 180-210 dusk, 210-240 night).

---

## 3. SYSTEMS

SYSTEMS: World Generator, Movement, Harvesting, Mining, Fishing, Respawner, Inventory, Trading, Furniture, Museum, Day/Night, HUD

### World Generator (T1)

Seeded generator. Input: `compose_world` output (world size in metres, list of regions each with category, centre, radius) and the RNG seed.

**Placement rules:**

- The **village clearing** region (category "clearing", the southernmost region) is the flat build area. Place three buildings as 3D meshes at fixed offsets from the region centre:
  - Shop building at (centre.x − 6, groundY, centre.z + 2), facing north.
  - Player home at (centre.x + 0, groundY, centre.z + 2), facing north.
  - Museum at (centre.x + 6, groundY, centre.z + 2), facing north.
  - Each building is 6 m wide × 4 m deep × 3 m tall. The home interior is a 6×4 grid of GridTile (row 0-3, col 0-5). The museum interior is a 4×3 grid of GridTile (row 0-3, col 0-2), and all 12 of these tiles are the Museum.slots.
  - The shop has no interior grid; it is a counter and a shopkeeper mesh.

- The **lake** region (category "water", the northernmost region): mark all tiles within its radius as water. Place 4 FishingSpots at fixed offsets from the region centre: two in the shallow ring (radius × 0.6 from centre) and two in the deep centre. Assign depth "shallow" to the outer two, "deep" to the inner two.

- The **berry meadow** regions (category "meadow" or "slopes" on the eastern side): place 18 BerryBushes. Scatter them using RNG: for i in 0..17, pick a random point inside the eastern meadow region's radius (angle = RNG() × 2π, dist = √(RNG()) × region.radius). Assign berryType: if RNG() < 0.4 then "strawberry", else if RNG() < 0.65 then "blueberry", else "blackberry". Set stage 0, picksRemaining 3.

- The **rocky hills** regions (category "rocky" or "hills" on the western side): place 14 OreRocks. Scatter using RNG as above. Assign oreType: if RNG() < 0.45 then "copper", else if RNG() < 0.80 then "iron", else "gold". Set hitsNeeded per type (copper 3, iron 5, gold 8), hitsTaken 0.

- **VERIFIER:** After placement, check: (a) at least 5 berry bushes of each type exist (if not, re-roll the last 4 bushes' types until the count is met); (b) at least 3 copper, 4 iron, and 2 gold rocks exist (if not, re-roll the last 3 rocks' types until met); (c) no object is within 2 m of a building mesh or another object (if a conflict, re-roll that object's position); (d) all 4 fishing spots are within the lake region's radius and not within 3 m of the shore. Re-roll with the next seed if any check fails.

### Movement (T1)

- Each tick, if a movement key is held, compute desired direction from the keys relative to the player's yaw. Forward = −Z rotated by yaw; strafe = +X rotated by yaw.
- New position = old position + direction × moveSpeed × dt. Clamp the player within the world bounds from compose_world (x ∈ [−size/2, size/2], z ∈ [−size/2, size/2]).
- Set player.y = ground height at new x, z (read from terrain). If the terrain height at the player's position is below the water level of the lake region, set inWater = true and clamp the player's z to not go further than the lake edge minus 0.5 m (they can wade but not swim). If inWater and the player presses S (backward), they walk back to shore.
- Yaw changes: A/Left adds 2.0 degrees per tick; D/Right subtracts 2.0 degrees per tick. Yaw wraps at 360.
- The player cannot walk through building meshes. If the new position's x,z is inside any building's bounding box (the three 6×4 rectangles), reject the move and keep the old position.

### Harvesting (T1)

- **Trigger:** player presses F while interactTarget is a BerryBush with stage < 2.
- **Effect on the bush:** picksRemaining -= 1. If picksRemaining is now 0, set stage = 2, respawnTimer = 45.
- **Effect on inventory:**
  - If berryType is "strawberry": add 1 + floor(RNG() × 2) strawberries (1 or 2).
  - If berryType is "blueberry": add 1 + floor(RNG() × 2) blueberries (1 or 2).
  - If berryType is "blackberry": add 1 blackberry. Additionally, if this was the 3rd pick (picksRemaining just became 0) AND the bush's berryType is "blackberry", set rareDropPending = true and add 1 specimen_blackberry to inventory.
- **Visual:** the bush mesh scales down from 1.0 to 0.7 (stage 1) to 0.4 (stage 2) over 0.2 s.

### Mining (T1)

- **Trigger:** player presses F while interactTarget is an OreRock with depletes = false, and currentTool = "pickaxe".
- **Effect on the rock:** hitsTaken += 1. If hitsTaken >= hitsNeeded, set depletes = true, respawnTimer = 60 (copper) or 90 (iron) or 120 (gold).
- **Effect on inventory:**
  - If oreType is "copper": add 1 copper.
  - If oreType is "iron": add 1 iron.
  - If oreType is "gold": add 1 gold. Additionally, if this was the final hit (hitsTaken just reached hitsNeeded) AND oreType is "gold", set rareDropPending = true and add 1 specimen_gold.
- **Tool tier effect:** pickaxeTier 1 (default) does 1 hit per press. pickaxeTier 2 does 1 hit per press but reduces hitsNeeded by 1 (effective: copper 2, iron 4, gold 7). pickaxeTier 3 does 2 hits per press (effective: copper 2 presses, iron 3 presses, gold 4 presses).
- **Visual:** the rock mesh cracks (a decal overlay appears) after each hit. At depletion, the rock mesh scales to 0.3 over 0.3 s and the top chunk "pops" upward with a small gravity arc.

### Fishing (T1)

- **Cast:** player presses F while interactTarget is a FishingSpot with state "idle" AND currentTool = "fishingRod". Set state = "casting". After 0.5 s, set state = "waiting", biteTimer = 0.
- **Waiting tick:** each tick while state = "waiting", biteTimer += dt. When biteTimer >= a threshold (shallow spot: 3 + RNG() × 5 seconds = 3 to 8; deep spot: 5 + RNG() × 7 seconds = 5 to 12), set state = "biting", reelingTimer = 0.
- **Biting tick:** each tick while state = "biting", reelingTimer += dt. The player must press F within 1.5 s. If the player presses F during "biting": set state = "caught", determine the catch, add to inventory, then set state = "idle" after 0.5 s. If reelingTimer >= 1.5 s without a press: set state = "idle" (the fish escapes, nothing is added).
- **Catch determination (on successful reel):**
  - Shallow spot, rodTier 1: minnow (70%), perch (30%).
  - Shallow spot, rodTier 2: minnow (30%), perch (40%), trout (30%).
  - Shallow spot, rodTier 3: minnow (10%), perch (30%), trout (40%), pike (20%).
  - Deep spot, rodTier 1: perch (50%), trout (50%).
  - Deep spot, rodTier 2: perch (20%), trout (45%), pike (35%).
  - Deep spot, rodTier 3: trout (30%), pike (55%), specimen_trout (7%), specimen_pike (8%).
  - The species is chosen by a single RNG() roll against the cumulative table.
- **Visual:** during "casting" a line animates from the rod tip to the water. During "waiting" a bobber bobs. During "biting" the bobber dips sharply and a ring ripple expands. During "caught" the fish arcs out of the water into the player's hand.

### Respawner (T1)

- Each tick, for every BerryBush with stage 2: respawnTimer -= dt. When respawnTimer <= 0, set stage = 0, picksRemaining = 3, respawnTimer = 0, rareDropPending = false. The bush mesh scales back to 1.0 over 0.5 s.
- Each tick, for every OreRock with depletes = true: respawnTimer -= dt. When respawnTimer <= 0, set depletes = false, hitsTaken = 0, respawnTimer = 0, rareDropPending = false. The rock mesh scales back to 1.0 over 0.5 s.

### Inventory (T1)

- All additions go through this system. When a resource key's count increases, totalCollected for that key also increases by the same amount.
- Inventory display is capped at 99 per item; if a count would exceed 99, it clamps to 99 and the excess is lost.
- Coins are added/subtracted directly; coins cannot go below 0 (a purchase that would make coins negative is rejected).

### Trading (T1)

- **Open shop:** player presses F within 3 m of the shop building door mesh. Set Shop.open = true, Shop.selectedTab = "sell", render the shop UI overlay.
- **Sell tab:** the UI lists every resource in the player's inventory with count > 0, its unit price from RESOURCEITEM, and a "Sell All" button per row and a "Sell 1" button. Pressing "Sell All" for a row: coins += count × price, count for that resource = 0. Pressing "Sell 1": coins += 1 × price, count -= 1.
- **Furniture tab:** lists every FURNITUREITEM not yet owned (a player can own multiple of the same piece, but the shop shows the full roster). Pressing "Buy" deducts price from coins, adds the item to the player's "owned furniture" list (a sub-record on Player: ownedFurniture, array of keys, starting empty). If coins < price, the button is greyed out and the press is rejected.
- **Museum tab:** lists every EXHIBITITEM. For items with price > 0, "Buy" works the same as furniture (deducts coins, adds to ownedExhibits array on Player). For items with price 0 (the four specimen types), the button is labelled "Display (requires specimen)" and is enabled only if the player's inventory has at least 1 of the corresponding specimen resource key. Pressing it consumes 1 specimen and adds the exhibit key to ownedExhibits.
- **Tools tab:** three tool purchases, one each:
  - "Copper Pickaxe" — 50 coins, sets pickaxeTier = 2 (if already 2, greyed out).
  - "Golden Pickaxe" — 150 coins, sets pickaxeTier = 3 (requires pickaxeTier >= 2).
  - "Copper Rod" — 40 coins, sets rodTier = 2 (if already 2, greyed out).
  - "Golden Rod" — 120 coins, sets rodTier = 3 (requires rodTier >= 2).
- **Close shop:** press E or Escape while the shop UI is open. Set Shop.open = false.

### Furniture (T1)

- **Enter home:** player presses F within 3 m of the home building door. The camera transitions (0.5 s) to an interior top-down-ish view looking at the 6×4 grid. The home UI shows the grid with each tile highlighted on hover (mouse) or tapped (touch).
- **Place furniture:** player presses E while in the home to open the placement menu (lists ownedFurniture items not yet placed). Selecting an item highlights the valid grid tiles (tiles that are empty AND can accommodate the item's grid size). Clicking/tapping a valid tile: set that GridTile.furnitureKey = item key, set occupied = true, remove the item from ownedFurniture. For multi-tile items (2×1, 1×2, 2×2), all constituent tiles must be empty; the item occupies the anchor tile and its neighbours.
- **Remove furniture:** right-click (or long-press on touch) a placed tile: set furnitureKey = null, occupied = false, return the item to ownedFurniture.
- **Exit home:** press E or Escape. Camera transitions back to the exterior.

### Museum (T1)

- **Enter museum:** player presses F within 3 m of the museum building door. Camera transitions to the interior 4×3 grid view (the 12 Museum.slots).
- **Display exhibit:** same placement mechanic as Furniture, but the menu lists ownedExhibits items not yet displayed. Selecting and placing sets the GridTile.furnitureKey = exhibit key.
- **Remove exhibit:** same as furniture removal.
- **Prestige computation:** each tick, Museum.prestigeScore = sum of the prestige values of all 12 slots (0 for empty slots). Museum.visitorsPerHour = floor(prestigeScore / 5) + 1 (minimum 1 if at least 1 slot is filled, 0 if all empty).
- **Visitor income tick:** every 60 seconds (game time), if visitorsPerHour > 0: Museum.coinIncomePerHour = floor(visitorsPerHour × 1.5). Inventory.coins += coinIncomePerHour. Museum.totalVisitors += visitorsPerHour.
- **Completion check:** each tick, if all 12 Museum.slots have a non-null furnitureKey, set Museum.allFilled = true. Trigger the "collection complete" jingle (T2) and show the gold banner overlay (T2) for 5 s.

### Day/Night (T1)

- GameClock.time += dt each tick. GameClock.dayCount = floor(time / dayLength) + 1.
- phase = (time % dayLength): 0-30 → "dawn", 30-180 → "day", 180-210 → "dusk", 210-240 → "night".
- **Lighting (T2):** the directional light's colour and intensity shift per phase. Dawn: warm orange (#FFAA55), intensity 0.6. Day: white (#FFFFFF), intensity 1.0. Dusk: warm red (#FF7744), intensity 0.5. Night: cool blue (#3344AA), intensity 0.2. Interpolate over 10 s at each phase boundary. A hemisphere light provides ambient fill at 0.3 intensity always.

### HUD (T1)

- Rendered in screen space, drawn after all world rendering. See section 5 for the element table.

---

## 4. CORE LOOP

The player's minute-to-minute cycle:

1. **Gather (Harvesting / Mining / Fishing).** Walk to a resource object. Interact. Fill a batch of the resource you need (a bush gives 3 picks, a rock 3-8 hits, a fish cast ~5-12 s). The resource lands in Inventory.
2. **Sell (Trading).** Walk back to the shop. Open the Sell tab. Dump the batch for coins.
3. **Buy (Trading / Furniture / Museum).** Use the coins on the next furniture piece, museum exhibit, or tool upgrade.
4. **Place (Furniture / Museum).** Enter the home or museum. Place the new item on a grid tile. Step back and look at the interior filling up.
5. **Repeat with better tools / rarer targets.** After buying a tier-2 tool, the same gathering action yields more or rarer items. After filling early museum slots, the visitor income starts dripping coins in the background, so selling becomes less urgent and the player can chase rare specimens.

**What grows:** the home interior fills with furniture; the museum fills with exhibits; the prestige score climbs; passive coin income rises.

**What unlocks:** tool tiers unlock faster gathering and rarer fish. Museum specimens unlock only through specific rare drops. The museum tab in the shop unlocks the four free exhibit slots that require in-game specimens.

**The end:** when all 12 museum slots are filled, Museum.allFilled = true. The gold banner plays. The game does not stop — the player can keep gathering, selling, and rearranging furniture and exhibits. There is no defeat state. The game is open-ended; the "end" is a satisfaction milestone, not a wall.

---

## 5. SCREENS

State machine:

`title → play → shop_menu → home_interior → museum_interior → pause`

- **title:** shows the game name "Orchard Hollow", a slow-rotating view of the village clearing, and a "Start" button (press any key or click). → play.
- **play:** the 3D world, player controllable, HUD visible. Press F near shop → shop_menu. Press F near home door → home_interior. Press F near museum door → museum_interior. Escape → pause.
- **shop_menu:** 2D overlay on top of the 3D world (world is dimmed to 40% opacity). Four tabs: Sell, Furniture, Museum, Tools. Navigate with mouse/touch. E or Escape or clicking outside the panel → play.
- **home_interior:** camera inside the house, looking at the 6×4 grid. 3D furniture meshes on placed tiles. E → placement/removal menu (a list panel on the right). E or Escape again → play.
- **museum_interior:** camera inside the museum, looking at the 4×3 grid. 3D exhibit meshes on placed tiles. E → placement/removal menu. E or Escape → play.
- **pause:** full-screen dim overlay. "Resume" (E/Escape/click), "Back to Title" (key T). No other input does anything.

**HUD table (play state):**

| Element | Record field(s) shown | Position |
|---|---|---|
| Top-left: resource list | Inventory counts for all 14 resource keys, icon + "×N" | Top-left, vertical stack |
| Top-left below resources: coins | Inventory.coins | Top-left |
| Top-right: day and time | GameClock.dayCount, GameClock.phase | Top-right |
| Top-right below: museum prestige | Museum.prestigeScore, Museum.visitorsPerHour | Top-right |
| Bottom-centre: current tool icon | Player.currentTool, Player.toolTiers | Bottom-centre |
| Bottom-right: minimap | 120×120 px, shows terrain, lake, buildings, berry bushes (green dots), ore rocks (grey dots), player (white arrow) | Bottom-right |
| Centre: interact prompt | Text label of the interactTarget type ("Press F: Pick Berry" / "Press F: Mine Copper" / "Press F: Cast Line" / "Press F: Talk to Aldric") | Centre, slightly below crosshair |
| Bottom-left: visitor income ticker | Museum.coinIncomePerHour (only shown when > 0) | Bottom-left, fades in/out |

---

## 6. AUDIO

All sounds generated with the Web Audio API. No audio files.

| Sound name | Recipe (waveform, frequency, duration, envelope) | Trigger rule |
|---|---|---|
| berry_pick | Sine, 600 Hz, 0.12 s, sharp attack 5 ms / decay 80 ms / release 35 ms | Harvesting: each successful pick |
| ore_hit | Square, 180 Hz, 0.15 s, attack 5 ms / decay 100 ms / release 50 ms | Mining: each hit on a rock |
| ore_deplete | Triangle, 200→80 Hz sweep, 0.4 s, attack 10 ms / sustain 200 ms / release 190 ms | Mining: rock depletes |
| fish_cast | Sine, 300→100 Hz sweep, 0.3 s, attack 10 ms / decay 150 ms / release 140 ms | Fishing: cast completes |
| fish_bite | Sine, 800 Hz, 0.08 s, attack 2 ms / decay 30 ms / release 50 ms, ×2 (double blip) | Fishing: state → biting |
| fish_caught | Sine, 400→800 Hz sweep, 0.25 s, attack 5 ms / decay 150 ms / release 100 ms | Fishing: state → caught |
| coin_sell | Sine, 1200 Hz, 0.08 s, attack 2 ms / decay 40 ms / release 40 ms, ×3 rising (1200/1500/1800) | Trading: sell 1 or sell all |
| coin_buy | Sine, 800 Hz, 0.1 s, attack 2 ms / decay 50 ms / release 50 ms | Trading: purchase |
| place_item | Sine, 500 Hz, 0.1 s, attack 5 ms / decay 50 ms / release 45 ms | Furniture/Museum: item placed |
| remove_item | Sine, 400→200 Hz, 0.15 s, attack 5 ms / decay 80 ms / release 65 ms | Furniture/Museum: item removed |
| menu_open | Sine, 600 Hz, 0.06 s, attack 2 ms / decay 30 ms / release 30 ms | Any menu opens |
| menu_close | Sine, 400 Hz, 0.06 s, attack 2 ms / decay 30 ms / release 30 ms | Any menu closes |
| rare_drop | Sine, 800→1600 Hz sweep, 0.5 s, attack 10 ms / sustain 300 ms / release 190 ms | Any specimen added to inventory |
| museum_complete | Triangle, chord 523/659/784 Hz, 1.5 s, attack 50 ms / sustain 1000 ms / release 450 ms | Museum.allFilled becomes true |
| ambient_music | Looping: 4-note string pad (sine, 220/262/330/392 Hz) at 80 BPM, 12 s loop, low-pass at 2000 Hz, volume 0.15; after 6+ museum exhibits, add a 5th note (440 Hz) and raise volume to 0.2 | Continuous during play state |

---

## 7. ART

**AI art (one image per distinct subject):**

- Ask for **a small wooden shop building** as a scene sprite (front 3/4 view, warm glow in window, "SHOP" sign, thatched roof) — 1 image.
- Ask for **a small cosy stone-and-timber house** as a scene sprite (front 3/4 view, chimney, small garden) — 1 image.
- Ask for **a small museum building** as a scene sprite (front 3/4 view, glass front, "MUSEUM" sign, columned entrance) — 1 image.
- Ask for **a berry bush, full of red berries** as a sprite (one bush, rounded, green leaves, red dots) — 1 image. Animate: 3 frames (full, half, bare) — one anim, 3 frames, single facing.
- Ask for **a berry bush, half-picked** as a sprite — 1 image (frame 2 of the above anim).
- Ask for **a bare berry bush** as a sprite — 1 image (frame 3).
- Ask for **a copper ore rock** as a sprite (grey-brown boulder with greenish-copper veins) — 1 image.
- Ask for **an iron ore rock** as a sprite (dark grey boulder with reddish-brown veins) — 1 image.
- Ask for **a gold ore rock** as a sprite (grey boulder with bright yellow veins) — 1 image.
- Ask for **a shopkeeper character** as a sprite (middle-aged man, apron, friendly, standing behind a counter, 3/4 view) — 1 image, single facing.
- Ask for **the player character** as a sprite (a simple adventurer, back view, with a small satchel, 4 directional frames: north, south, east, west) — 1 anim, 4 frames, four facing.
- Ask for **a fishing bobber** as a sprite (red-and-white float) — 1 image.
- Ask for **a minnow** as a sprite (small silver fish, side view) — 1 image.
- Ask for **a perch** as a sprite (medium green-brown fish) — 1 image.
- Ask for **a trout** as a sprite (pink-speckled fish) — 1 image.
- Ask for **a pike** as a sprite (long dark green fish) — 1 image.

**Code-drawn (RECIPE lines):**

- **Furniture meshes:** each furniture item is a simple extruded box or cylinder. RECIPE: box width/depth = grid size × 1 m, height 0.8 m (tables) or 1.2 m (shelves, beds) or 0.3 m (rugs, flat). Colours: oak rug #8B6914, moss rug #4A7A2E, small table #A0722A, large table #8B5E1A, wooden chair #9C7830, cushioned chair #7A5B2A with #CC8844 cushion, single bed #6B4E2A frame + #FFFFFF sheet, wooden shelf #A0722A, display shelf #888888, oil lamp #555555 base + #FFDD88 glow sphere r=0.15 m, candle stand #777777 + #FFEE99 flame, painting (berries) #224422 background + #CC3333 dots, painting (lake) #335577 background + #AAAAFF horizon, potted fern #556B2F pot + #3A6B1A leaves, cactus #2E8B2A, oval mirror #C0C0C0 frame + #E8E8FF glass, wall clock #8B6914 circle + #FFFFFF face + #333333 hands, wooden chest #8B5E1A + #4A3520 latch, stone fireplace #777777 blocks + #FF6622 inner glow, patterned rug #8B2222 base + #FFD700 border.
- **Exhibit meshes:** each exhibit is a small display pedestal (cylinder, r=0.2 m, h=0.4 m, colour #666666) with the item on top. Mini fish are the AI sprites scaled to 0.3 m. Gold nugget is a dodecahedron, r=0.12 m, #FFD700. Blackberry bundle is a cluster of 5 small spheres, r=0.05 m each, #222244. Fossil is a flat disc, r=0.15 m, #AA9977. Sea shell is a spiral cone, h=0.2 m, #F5E6D0. Old map is a flat rectangle 0.25×0.18 m, #E8D8B0. Clockwork orrery is a small armillary: 3 nested torus rings, r=0.15/0.12/0.09 m, #B8860B.
- **Water:** the lake surface is a flat plane at the water level, colour #3388AA with 0.6 opacity. Ripples are animated concentric circles (ring, stroke #FFFFFF, 0.3 opacity) expanding from the bobber position during fishing.
- **Terrain:** the ground mesh is generated from compose_world. Grass tiles are a repeating flat-colour quad #4A8C3F. Rocky areas are #888878. Paths (village clearing) are #C4A86E.
- **UI panels:** rectangles with 8 px corner radius, background #2A2A2A at 0.85 opacity, border 2 px #888888. Buttons are rounded rectangles, 120×36 px, background #4A6A8A, hover #5A8ABA, text #FFFFFF.
- **Player character (code fallback if AI art unavailable):** a capsule body (cylinder h=1.2 m, r=0.25 m, #4A6E8A) + sphere head (r=0.18 m, #E8C49A) + small box satchel (0.15×0.1 m, #8B5E1A) on the back.

Everything else — grid tiles, interact prompt text, coin icons, tool icons, minimap terrain, bobber ripple rings, fish-arc animation path, rock-crack decal, bush scale animation, furniture/exhibit pedestal bases, shop counter, building door frames, the gold banner overlay — is drawn in code.

---

## 8. DEBUG API

`window.__game` is installed on load. All functions are synchronous and return plain data only.

| Call | What it does | Returns |
|---|---|---|
| `start()` | Dismisses the title screen, enters the play state, starts the update loop. | `{ state: "play" }` |
| `step(dt, n)` | Advances n ticks of dt seconds (n × dt total), running all systems in order, then renders once. Does not wait for real time. | `{ ticks: n, time: GameClock.time }` |
| `setTime(t)` | Sets GameClock.time to t seconds, recomputes dayCount and phase. Does not render. | `{ time: t, dayCount, phase }` |
| `seed(n)` | Resets RNG to mulberry32(n), re-runs the World Generator, re-places all BerryBushes, OreRocks, FishingSpots, and buildings. Rebuilds GridTile arrays for home and museum. Resets all gameplay records (Player, Inventory, Shop, Museum, GameClock) to starting values. | `{ seed: n, bushes: count, rocks: count, spots: count }` |
| `getState()` | Returns a plain object with every record's fields: `{ player: {…}, inventory: {…}, bushes: [ {…}, … ], rocks: [ {…}, … ], spots: [ {…}, … ], homeTiles: [ {…}, … ], museumTiles: [ {…}, … ], museum: {…}, shop: {…}, clock: {…} }`. | plain object |
| `setMove(dx, dz)` | Sets the persistent movement direction. dx, dz ∈ {−1, 0, 1}. Call again with 0,0 to stop. Persists until changed. | `{ dx, dz }` |
| `setYaw(deg)` | Sets Player.yaw to deg (0-360). | `{ yaw: deg }` |
| `pressInteract()` | Fires the F key action at the current interactTarget. | `{ action: "harvest"|"mine"|"cast"|"reel"|"open_shop"|"enter_home"|"enter_museum"|null, target: key|null }` |
| `pressMenu()` | Fires the E key action (open/close menu). | `{ action: "open"|"close"|"place"|"remove"|null }` |
| `selectTool(tool)` | Sets Player.currentTool to "hands" | "pickaxe" | "fishingRod". | `{ tool }` |
| `selectToolTier(type, tier)` | Sets Player.toolTiers.pickaxeTier or .rodTier directly. type: "pickaxe" | "rod". tier: 1-3. | `{ pickaxeTier, rodTier }` |
| `spawnBerry(x, z, type)` | Creates a new BerryBush at (x, groundY, z) with the given type, stage 0, picksRemaining 3. Adds it to the bush list. | `{ id, x, z, type, stage: 0 }` |
| `spawnRock(x, z, type)` | Creates a new OreRock at (x, groundY, z) with the given type, hitsNeeded per type, hitsTaken 0. Adds to rock list. | `{ id, x, z, type, hitsNeeded }` |
| `setInventory(key, count)` | Directly sets Inventory[key] and Inventory.totalCollected[key] to count. | `{ key, count }` |
| `setCoins(n)` | Sets Inventory.coins to n. | `{ coins: n }` |
| `placeFurniture(homeRow, homeCol, key)` | Places a FURNITUREITEM on the given home grid tile (must be empty). | `{ row, col, key, success: true/false }` |
| `placeExhibit(musRow, musCol, key)` | Places an EXHIBITITEM on the given museum grid tile. Updates Museum.prestigeScore. | `{ row, col, key, success, prestigeScore }` |
| `openShopTab(tab)` | Sets Shop.open = true, Shop.selectedTab = tab. | `{ tab }` |
| `skipToDay(n)` | Sets GameClock.time to (n−1) × 240, dayCount = n, recomputes phase. | `{ dayCount: n, time, phase }` |

---

## 9. TESTS

Run via the debug API. All calls are synchronous.

1. `start()` → returns `{ state: "play" }`. Verify the play state is active.
2. `seed(42)` → returns `{ seed: 42, bushes: 18, rocks: 14, spots: 4 }`. Verify the counts.
3. `getState()` → verify: Player.position = (0, groundY, 0), Player.yaw = 0, Inventory.coins = 50, all resource counts = 0, all 18 bushes have stage 0 and picksRemaining 3, all 14 rocks have hitsTaken 0, all 4 spots have state "idle", all 24 home tiles and 12 museum tiles have furnitureKey null, Museum.prestigeScore = 0, GameClock.time = 0.
4. **Harvesting:** `setMove(0, −1)` (walk north), `step(0.0167, 300)` (5 s of walking to reach a bush), `pressInteract()`. Verify: the bush's picksRemaining dropped to 2, Inventory has ≥ 1 berry of the bush's type, Inventory.totalCollected increased.
5. **Mining:** `selectTool("pickaxe")`, `setYaw(270)` (face west toward rocks), `step(0.0167, 300)`, `pressInteract()` × 3 (for a copper rock). Verify: after 3 presses the copper rock has depletes = true, respawnTimer > 0, Inventory has 1 copper.
6. **Fishing:** `selectTool("fishingRod")`, `setYaw(0)` (face north toward lake), `step(0.0167, 300)`, `pressInteract()` (cast). Verify: the spot's state = "waiting". `step(0.0167, 600)` (10 s). Verify: state is "biting" or "idle" (if it already escaped). If "biting": `pressInteract()` → verify state = "caught" then "idle" after step, Inventory has ≥ 1 fish.
7. **Respawning:** take a bush to stage 2 (pressInteract × 3), note respawnTimer = 45. `step(0.0167, 2700)` (45 s). Verify: bush stage = 0, picksRemaining = 3, respawnTimer = 0.
8. **Trading (sell):** `setInventory("strawberry", 10)`, `openShopTab("sell")`, `pressInteract()` (simulate Sell All on strawberry). Verify: coins increased by 30, strawberry count = 0.
9. **Trading (buy furniture):** `setCoins(200)`, `openShopTab("furniture")`, buy "rug_oak" (20 coins). Verify: coins = 180, ownedFurniture contains "rug_oak".
10. **Furniture placement:** `placeFurniture(0, 0, "rug_oak")`. Verify: homeTile[0,0].furnitureKey = "rug_oak", occupied = true, ownedFurniture no longer contains "rug_oak".
11. **Museum placement:** `placeExhibit(0, 0, "case_minnow")` (bought in a prior step or via `setCoins` + shop). Verify: museumTile[0,0].furnitureKey = "case_minnow", Museum.prestigeScore = 2, Museum.visitorsPerHour = 1.
12. **Museum income:** `step(0.0167, 3600)` (60 s). Verify: Inventory.coins increased by floor(1 × 1.5) = 1, Museum.totalVisitors = 1.
13. **Museum completion:** place exhibits in all 12 museum slots via `placeExhibit` calls. Verify: Museum.allFilled = true, Museum.prestigeScore = sum of all 12 prestige values.
14. **Day/night:** `setTime(30)` → phase = "dawn". `setTime(90)` → phase = "day". `setTime(190)` → phase = "dusk". `setTime(230)` → phase = "night". `setTime(240)` → dayCount = 2, phase = "dawn".
15. **Rare drop (mining):** `selectTool("pickaxe")`, `selectToolTier("pickaxe", 1)`, find a gold rock, pressInteract × 8. Verify: after the 8th hit, Inventory has 1 specimen_gold.
16. **Rare drop (harvest):** find a blackberry bush, pressInteract × 3. Verify: after the 3rd pick, Inventory has 1 specimen_blackberry.
17. **Tool tier effect:** `selectToolTier("pickaxe", 3)`, find a copper rock (hitsNeeded 3), pressInteract × 2 (tier 3 does 2 hits per press, so 2 presses = 4 hits ≥ 3). Verify: rock depletes after 2 presses.
18. **Fishing depth:** at a shallow spot, cast and reel 20 times (re-seed between casts for variety). Verify: all catches are minnow or perch (rodTier 1, shallow). At a deep spot, rodTier 3, cast and reel 100 times. Verify: at least 1 catch is a pike, and specimen_trout or specimen_pike appears at least once.

**SCREENSHOTS:**

| Screen / state | What a person must see |
|---|---|
| Title | "Orchard Hollow" in large text, a slow-rotating 3D view of the three buildings in a clearing, "Press any key to start" below. |
| Play, exterior | Third-person 3D view from behind the player. Rolling green terrain, a blue lake to the north, berry bushes (red dots) to the east, grey rocks to the west, three buildings to the south. HUD: resource list top-left, coins, day counter top-right, tool icon bottom-centre, minimap bottom-right. |
| Play, interacting with bush | Player in front of a berry bush. Centre prompt reads "Press F: Pick Berry". |
| Shop menu, Sell tab | Dimmed 3D world behind a panel. Panel shows "Aldric's Shop" header, four tabs, "Sell" tab active. List of owned resources with counts, prices, and Sell All / Sell 1 buttons. |
| Shop menu, Furniture tab | "Furniture" tab active. Scrollable list of 20 furniture items with icons, names, prices, and Buy buttons. |
| Home interior | Camera inside the 6×4 grid room. Wooden walls and floor. Any placed furniture visible as 3D meshes on their tiles. |
| Museum interior | Camera inside the 4×3 grid room. Display pedestals visible. Placed exhibits on their tiles. Prestige score shown in HUD. |
| Museum complete | Gold banner overlay: "Collection Complete!" with the prestige total. All 12 pedestals filled. |
| Pause | Dim full-screen overlay. "Orchard Hollow" title, "Resume" and "Back to Title" buttons. |
| Night phase | The scene is dim blue, the shop window glows warm, the player's lamp (if placed) casts a small warm circle. |

---

## 10. BUILD ORDER

| Milestone | What it adds | Check from section 9 |
|---|---|---|
| M1: Shell | Page loads, title screen renders, `start()` enters play, the 3D world (terrain, lake, three building meshes) is drawn, player is visible at origin. HUD shows day counter and tool icon. | Check 1, Check 2, Check 3 (world objects exist) |
| M2: Movement + World Objects | Player walks with WASD/arrows, collides with buildings, enters water at lake edge. All 18 bushes, 14 rocks, 4 spots are visible in the world. Interact prompt appears when near an object. | Check 3 (positions), Check 4 (walk to bush, prompt appears) |
| M3: Gathering | Harvesting, Mining, Fishing systems work. Pressing F picks berries, mines ore, casts/reels fish. Inventory updates. Bush/rock/fishing visuals animate. | Check 4, Check 5, Check 6, Check 15, Check 16, Check 17 |
| M4: Respawning + Day/Night | Bush and rock timers count down and objects reset. GameClock advances, phase changes, lighting shifts. | Check 7, Check 14 |
| M5: Shop + Trading | Shop menu opens, Sell / Furniture / Museum / Tools tabs work. Coins change. ownedFurniture and ownedExhibits arrays update. Tool tiers apply. | Check 8, Check 9, Check 17, Check 18 |
| M6: Furniture + Museum placement | Home and museum interiors render. Grid tiles highlight on hover. Place / remove furniture and exhibits. Museum prestige and visitor income compute. | Check 10, Check 11, Check 12, Check 13 |
| M7: Audio + Polish | All sounds from section 6 play on their triggers. Ambient music loops. T2 visual effects (bush 3-stage, bobber ripple, tool colour, dust particles, gold banner). | Check 13 (banner), Check 18 (fishing ripple visible in screenshot) |
| M8: Debug + Tests | `window.__game` fully populated. All section 9 checks pass. All screenshot rows verified by a human. | All checks 1-18, all screenshot rows |

Every milestone after M1 leaves the game playable (you can walk, gather, sell, place). M8 is the final gate.

---

## 11. DONE

- **"open world collector game" →** Check 1, 2, 3 (world generated, objects placed, player at origin). Screenshot: Play, exterior.
- **"the player walks around" →** Check 4 (walk to bush). Screenshot: Play, exterior (player mid-walk).
- **"collecting resources" →** Check 3 (inventory starts empty), Check 4/5/6 (resources appear in inventory). Screenshot: Play, interacting with bush.
- **"harvest berries" →** Check 4, Check 7 (respawn), Check 16 (rare blackberry). Screenshot: Play, interacting with bush.
- **"mine ores" →** Check 5, Check 7 (rock respawn), Check 15 (rare gold), Check 17 (tool tier). Screenshot: Play, interacting with rock (prompt "Press F: Mine Copper").
- **"fish fish" →** Check 6, Check 18 (depth and rod tier). Screenshot: Play, fishing (bobber in water, ripple ring).
- **"sell them to a shop keeper for each type" →** Check 8. Screenshot: Shop menu, Sell tab.
- **"buy furniture to decorate their home" →** Check 9, Check 10. Screenshot: Home interior with placed furniture.
- **"a small museum type building" →** Check 11, Check 12, Check 13. Screenshot: Museum interior, Museum complete.

The game is finished when every line above is true.

---

## A. SANITY

- **Fields read/written by rules vs. record definitions.**
  - Harvesting reads BerryBush.stage, picksRemaining, berryType; writes picksRemaining, stage, respawnTimer, rareDropPending. All on BerryBush record. Writes Inventory count via Inventory system. ✓
  - Mining reads OreRock.hitsTaken, hitsNeeded, oreType, depletes; writes hitsTaken, depletes, respawnTimer, rareDropPending. All on OreRock. Reads Player.currentTool, toolTiers.pickaxeTier. All on Player. ✓
  - Fishing reads FishingSpot.state, depth, biteTimer, reelingTimer; writes state, biteTimer, reelingTimer, currentCatch. All on FishingSpot. Reads Player.toolTiers.rodTier. ✓
  - Trading reads Inventory, Player.toolTiers, Player.ownedFurniture, Player.ownedExhibits; writes coins, ownedFurniture, ownedExhibits, toolTiers. All defined. ✓
  - Furniture reads GridTile.furnitureKey, occupied; writes them. Reads Player.ownedFurniture. ✓
  - Museum reads Museum.slots (GridTile array), prestigeScore, visitorsPerHour, coinIncomePerHour, totalVisitors, allFilled; writes them. All on Museum record. ✓
  - Result: **closes.**

- **Places, things, kinds named by rules — placed by generator or listed in roster.**
  - BerryBushes: placed by World Generator (18, scattered in eastern meadow). Roster of berryType is in the BERRYBUSH record field. ✓
  - OreRocks: placed by World Generator (14, scattered in western rocky hills). Roster of oreType in the OREROCK record. ✓
  - FishingSpots: placed by World Generator (4, in lake). ✓
  - Buildings: placed by World Generator at fixed offsets in the clearing region. ✓
  - FURNITUREITEM, EXHIBITITEM, RESOURCEITEM: all listed in rosters in section 2. ✓
  - Shopkeeper "Aldric": a fixed NPC mesh at the shop, listed in the World Generator building placement. ✓
  - Result: **closes.**

- **Consumable totals: generators place vs. rules can demand along the core loop.**
  - Berries: 18 bushes × 3 picks × 1-2 yield = 54–108 berries per full cycle. 3 bushes deplete, respawn in 45 s. A player can re-harvest indefinitely. No upper cap on berry demand (selling is unbounded). ✓
  - Ores: 14 rocks. Copper: 3 hits, 3 respawn 60 s. Iron: 5 hits, 90 s. Gold: 8 hits, 120 s. Indefinite re-mining. No cap on ore demand. ✓
  - Fish: 4 spots, each can be cast indefinitely. Indefinite supply. ✓
  - Coins: start 50. Cheapest furniture is 10 (cactus). Most expensive is 150 (fireplace). Total furniture cost if buying all 20: 1,215 coins. Total museum exhibit cost if buying all paid: 440 coins. Tool upgrades: 360 coins. Total sink: ~2,015 coins. At 3-35 coins per resource and ~5-10 resources per minute of active gathering, the player can fund the full sink in roughly 20-40 minutes of play. Museum passive income (up to ~12 visitors × 1.5 = 18 coins/hr at max prestige) supplements. ✓
  - Result: **closes.**

- **Timing pairs.**
  - Bush respawn (45 s) vs. harvest rate (3 picks in ~3 s of standing): the player can harvest a bush in 3 s, then must wait 45 s or move to another bush. 18 bushes means the player can cycle through all of them in ~54 s of active picking, then wait. No stall. ✓
  - Rock respawn (60-120 s) vs. mine time (3-8 hits at ~1 s each with basic tool, less with upgrades): player mines a rock in 3-8 s, waits 60-120 s. 14 rocks give variety. No stall. ✓
  - Fishing cast-to-bite (3-12 s) + reel window (1.5 s) = max 13.5 s per fish. 4 spots. No stall. ✓
  - Museum income tick (every 60 s) vs. day length (240 s): 4 income ticks per day. ✓
  - Result: **closes.**

- **Every call in section 9 is in section 8.**
  - start() ✓, step() ✓, setTime() ✓, seed() ✓, getState() ✓, setMove() ✓, setYaw() ✓, pressInteract() ✓, pressMenu() ✓, selectTool() ✓, selectToolTier() ✓, spawnBerry() ✓ (used implicitly), spawnRock() ✓, setInventory() ✓, setCoins() ✓, placeFurniture() ✓, placeExhibit() ✓, openShopTab() ✓, skipToDay() ✓.
  - Check 4 uses setMove, step, pressInteract ✓.
  - Check 5 uses selectTool, setYaw, step, pressInteract ✓.
  - Check 6 uses selectTool, setYaw, step, pressInteract ✓.
  - Check 7 uses step ✓.
  - Check 8 uses setInventory, openShopTab, pressInteract ✓.
  - Check 9 uses setCoins, openShopTab, pressInteract ✓.
  - Check 10 uses placeFurniture ✓.
  - Check 11 uses placeExhibit ✓.
  - Check 12 uses step ✓.
  - Check 13 uses placeExhibit × 12 ✓.
  - Check 14 uses setTime ✓.
  - Check 15 uses selectTool, selectToolTier, pressInteract ✓.
  - Check 16 uses pressInteract ✓.
  - Check 17 uses selectToolTier, pressInteract ✓.
  - Check 18 uses selectTool, selectToolTier, pressInteract, step, seed ✓.
  - Result: **closes.**