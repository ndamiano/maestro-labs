# gameplay.md

## 1. Design Summary

This is a single-player, open-world collector game. The player explores a compact outdoor map, gathers three categories of resources, sells them to specialized shopkeepers, buys tools and furniture, and decorates a home and a small museum.

The game has no combat, no health, no fail state, and no combat progression. The core fantasy is:

> Explore, collect, trade, improve your tools, make your home and museum feel lived-in and curated.

The game should feel relaxed but not aimless. Progression is driven by:

1. Collecting new resource types.
2. Unlocking better tools and shop stock.
3. Placing furniture.
4. Opening and curating the museum.
5. Completing a full collection and receiving the final curator reward.

Target playtime to full completion is approximately 2–3 hours. After completion, the game remains fully open-ended.

---

## 2. Dimensionality

### Decision: 2D top-down

The game is 2D top-down with a fixed camera and no vertical axis.

### Why

- Open-world readability: the player needs to see berry bushes, ore nodes, water, shops, and doors clearly.
- Furniture placement is much more understandable on a top-down floor grid.
- Browser performance is safer with a 2D tile-based world.
- The game is a collector/decoration game, not an action game. Top-down keeps the pace calm and readable.
- 2.5D or 3D would add camera and placement complexity without improving the core loop.

### Coordinate System

- World is a tile grid.
- Tile size: `24 x 24` pixels at 1x scale.
- World size: `120 x 120` tiles.
- Total world pixel size: `2880 x 2880` pixels.
- Camera follows the player.
- Camera does not rotate.
- No vertical movement, no caves, no ladders, no elevation.

### Camera Viewport

Design resolution: `960 x 540`.

At that resolution, the visible area is approximately:

- `40 x 22` tiles.

The world is larger than the viewport, giving the feeling of an open map without requiring fast travel.

---

## 3. Space and Layout

The game uses one continuous outdoor map plus two interior buildings.

There are no separate levels. Progression happens inside the single world.

### 3.1 World Structure

The world is bounded by impassable perimeter tiles. The perimeter represents ocean, cliffs, or dense forest. The player cannot leave the map.

World tile coordinates use `(x, y)` from `0` to `119`.

#### Zones

| Zone | Approximate Tiles | Purpose |
|---|---:|---|
| Village | `x: 45-75`, `y: 45-75` | Start area, shopkeepers, home, museum |
| Berry Grove | `x: 25-95`, `y: 5-38` | Berry resources |
| Ore Ridge | `x: 82-115`, `y: 30-90` | Ore resources |
| Lake / Lakeside | `x: 5-40`, `y: 40-100` | Fishing resources |
| Perimeter | all outer edge tiles | Impassable boundary |

The zones are intentionally close to the village. The player should be able to walk from the village to any resource zone in about 3–6 seconds. This keeps the collect-sell-place loop tight.

### 3.2 Village Layout

The village contains:

- Home building.
- Museum building.
- Open-air Trading Post with three shopkeepers.
- Paths connecting the house, museum, trading post, and exits to resource zones.

The Trading Post is not an interior. It is an open-air interaction area with three shopkeeper objects.

#### Building Positions

| Building | Exterior Door Tile | Notes |
|---|---:|---|
| Home | `(52, 68)` | Player starts nearby |
| Museum | `(68, 68)` | Locked until the first trading goal is complete |
| Trading Post | `x: 58-62`, `y: 65` | Three shopkeepers standing in the open |

The three shopkeepers are placed side by side:

| Shopkeeper | Position |
|---|---:|
| Berry Shopkeeper, Moss | `(58, 65)` |
| Ore Shopkeeper, Grit | `(60, 65)` |
| Fish Shopkeeper, Reed | `(62, 65)` |

### 3.3 Home Interior

The Home is a separate interior scene attached to the exterior door.

- Interior floor size: `10 x 8` tiles.
- Perimeter walls surround the floor.
- Door tile inside Home: `(5, 7)`.
- The door tile is walkable and cannot have furniture placed on it.
- The Home is available from the start.
- Furniture can be placed inside the Home.

### 3.4 Museum Interior

The Museum is a separate interior scene attached to the exterior door.

- Interior floor size: `12 x 10` tiles.
- Perimeter walls surround the floor.
- Door tile inside Museum: `(6, 9)`.
- The door tile is walkable and cannot have furniture placed on it.
- The Museum is locked until the player completes the `First Trades` goal.
- Display cases can only be placed in the Museum.
- Other furniture can be placed in the Museum or Home.

### 3.5 Movement and Collision

#### Player Movement

- Movement: WASD or arrow keys.
- Walk speed: `6 tiles per second`.
- Diagonal movement is normalized, so diagonal speed is not faster than straight-line speed.
- Shallow water is walkable at `3 tiles per second`.
- The player can enter all resource zones from the village.
- There are no fast travel points. The map is intentionally compact.

#### Collision

- Perimeter tiles are solid.
- Berry bushes are solid. The player interacts from an adjacent tile.
- Ore nodes are solid. The player interacts from an adjacent tile.
- Water is walkable and slows movement.
- Doors are walkable.
- Placed furniture is solid in the building interior.
- The player cannot pass through walls.

#### Interaction Radius

The player can interact with objects within `1.2` tiles.

If multiple interactable objects are in range, the nearest one is targeted.

---

## 4. Core Loop

The main loop is:

1. Walk to a resource area.
2. Gather berries, ores, or fish.
3. Return to the Trading Post.
4. Sell resources to the matching shopkeeper.
5. Buy better tools or furniture.
6. Place furniture in the Home or Museum.
7. Unlock new shop stock, museum exhibits, and later tools.
8. Repeat until full collection and curator completion.

The loop is designed to feel like small satisfying cycles:

- A short gathering trip: 10–30 seconds.
- A short selling action: 3–10 seconds.
- A placement or upgrade decision: 5–20 seconds.
- A visible progression update: goal progress, shop unlock, collection entry, or museum score.

There is no failure. If the player has no coins, they can always gather free resources. If a node is empty, it respawns. If the player makes a placement mistake, they can remove or resell furniture.

---

## 5. Systems

## 5.1 Player State

The player has:

- Position.
- Coins.
- Inventory.
- Current tool tier for each resource category.
- Collection log.
- Purchased but unplaced furniture inventory, called the Build Inventory.
- Placed furniture per building.
- Museum specimen assignments.
- Goal progression state.

The player does not have:

- Health.
- Stamina.
- Level.
- Combat stats.
- Weight.
- Hunger.
- Inventory weight.

### Starting State

On first play:

- Coins: `25`.
- Berry tool: Tier 1.
- Mining tool: Tier 1.
- Fishing tool: Tier 1.
- Inventory: empty.
- Home: empty interior except walls and door.
- Museum: locked.
- Collection log: empty.
- All starting shop stock available.

### Why No Fail State

This is a collector game. The fantasy is accumulation and decoration, not survival. Removing failure keeps the pacing relaxed and prevents accidental softlocks or frustration.

---

## 5.2 Resource Nodes

There are three resource categories:

1. Berries.
2. Ores.
3. Fish.

Each category has three tiers.

### Berry Nodes

Berry nodes are bushes.

- A bush is either full or empty.
- A full bush contains `1` or `2` berries.
- Picking removes the entire available stack.
- After picking, the bush becomes empty.
- The bush respawns after a timer.
- Berry bushes are solid objects.

#### Berry Resources

| Resource | Tier | Base Sell Price | Respawn Time | Node Count |
|---|---:|---:|---:|---:|
| Sweet Berry | 1 | `2` | `20s` | `30` |
| Moon Berry | 2 | `5` | `45s` | `15` |
| Ember Berry | 3 | `12` | `120s` | `5` |

#### Berry Node Placement

- Sweet Berries are common throughout the Berry Grove.
- Moon Berries are mostly in the middle and southern parts of the Berry Grove.
- Ember Berries are rare in the northernmost part of the Berry Grove.

### Ore Nodes

Ore nodes are rocks.

- An ore node has `3` charges.
- Each mine action consumes `1` charge and yields ore.
- When all charges are gone, the node becomes empty.
- The node regrows after a timer.
- Ore nodes are solid objects.

#### Ore Resources

| Resource | Tier | Base Sell Price | Charges | Empty Time | Node Count |
|---|---:|---:|---:|---:|---:|
| Copper Ore | 1 | `4` | `3` | `300s` | `25` |
| Silver Ore | 2 | `10` | `3` | `360s` | `12` |
| Crystal Shard | 3 | `25` | `3` | `720s` | `4` |

#### Ore Node Placement

- Copper Ore is common throughout the Ore Ridge.
- Silver Ore is mostly in the eastern half of the Ore Ridge.
- Crystal Shards are rare at the eastern tip of the Ore Ridge.

### Fish Spots

Fish spots are water tiles.

- The player walks into shallow water to fish.
- Each fish spot has a fixed fish type.
- Fish spots do not deplete.
- Fishing is limited by the tool cooldown and the fishing minigame.

#### Fish Resources

| Resource | Tier | Base Sell Price | Spot Count | Notes |
|---|---:|---:|---:|---|
| Minnow | 1 | `4` | `15` | Common near shore |
| Trout | 2 | `10` | `8` | Middle lake |
| Moonfish | 3 | `25` | `3` | Deep south lake |

#### Fish Spot Placement

- Minnow spots are near the lake shoreline.
- Trout spots are in the middle of the lake.
- Moonfish spots are in the deep southern area of the lake.

---

## 5.3 Gathering System

### General Gather Rules

- Gathering uses the interact button.
- The player must be within interaction radius.
- The player must have at least one inventory slot with room for at least `1` of the resource.
- If the action would produce a bonus second unit, it is only added if inventory space allows.
- If inventory is completely full for that resource, the action cannot start.
- The HUD shows a progress bar during berry picking and mining.
- Releasing the interact key cancels the current progress for berry picking and mining.
- Fishing is a committed sequence once the cast starts.

### Berry Picking

Base action:

- Base time: `0.80s`.
- Base yield: entire available berry stack, `1` or `2`.
- Tool upgrades reduce time and add bonus yield.

### Mining

Base action:

- Base time: `1.20s` per charge.
- Base yield: `1` ore.
- Tool upgrades reduce time and add bonus yield.

### Tool Upgrade Effects

Tools are owned per category. Buying a new tool automatically replaces the old one.

The player cannot downgrade. The player cannot sell tools back.

| Category | Tier 1 | Tier 2 | Tier 3 |
|---|---:|---:|---:|
| Berry gather time | `0.80s` | `0.65s` | `0.55s` |
| Berry bonus yield chance | `0%` | `30%` | `60%` |
| Mine time | `1.20s` | `0.95s` | `0.80s` |
| Mine bonus yield chance | `0%` | `30%` | `60%` |
| Fishing bite green zone | `0.30s` | `0.40s` | `0.50s` |
| Fishing yellow zone success | `40%` | `55%` | `70%` |
| Fishing bonus fish chance | `0%` | `25%` | `50%` |
| Fishing cooldown | `3.0s` | `2.5s` | `2.0s` |

### Why Tools Upgrade Instead of Craft

The request is about collecting and selling, not crafting. Buying tools keeps the loop simple:

- Gather.
- Sell.
- Buy.
- Gather better.

Crafting would add a system that is not necessary for the core fantasy.

---

## 5.4 Fishing System

Fishing is the only timed mini-action. It should feel satisfying but not demanding.

### Fishing Sequence

1. Player stands on a fish spot.
2. Player presses interact.
3. Cast animation plays for `0.6s`.
4. The line waits for a bite.
5. A bite meter appears.
6. Player presses interact to strike.
7. If successful, the player catches fish.
8. If failed, nothing is caught and the cooldown starts.

### Bite Wait

The wait before the bite meter appears is randomized.

| Tool Tier | Wait Range |
|---|---:|
| Tier 1 | `1.0s` to `3.0s` |
| Tier 2 | `0.8s` to `2.5s` |
| Tier 3 | `0.6s` to `2.0s` |

### Bite Meter

The bite meter lasts `1.5s`.

A moving indicator travels across the meter. The player presses interact when the indicator is in the target zone.

Meter zones:

| Zone | Success |
|---|---|
| Green | `100%` success |
| Yellow, adjacent to green | uses tool yellow success chance |
| Outside green/yellow | `0%` success |

Green zone width:

| Tool Tier | Green Width |
|---|---:|
| Tier 1 | `0.30s` |
| Tier 2 | `0.40s` |
| Tier 3 | `0.50s` |

Yellow zones are `0.20s` on each side of the green zone.

### Catch Result

If successful:

- Base yield: `1` fish.
- Bonus yield: `+1` fish based on tool bonus fish chance.
- Inventory space is checked before adding.
- If space for only one, the player gets one.
- If space for two, the player may get two based on bonus chance.
- Cooldown starts.

If failed:

- No fish.
- Cooldown starts.

If the player misses the meter entirely:

- No fish.
- Cooldown starts.

If the player leaves the fish spot during the bite meter:

- The attempt fails.
- Cooldown starts.

### Why a Small Minigame

A fully automatic fishing action would be too passive. A simple timing meter gives the player a small skill moment without adding difficulty or failure pressure.

---

## 5.5 Inventory System

The player has a single resource inventory.

- Inventory slots: `10`.
- Each slot holds one stack of one resource type.
- Tools are not stored in inventory.
- Furniture is not stored in inventory.
- There is no weight.
- There is no dropping.

### Stack Limits

| Resource Type | Stack Limit |
|---|---:|
| Berries | `20` |
| Ores | `10` |
| Fish | `5` |

### Inventory Rules

- When gathering, the game first checks that at least one unit can fit.
- If the resource has existing stack space, new units are added to that slot.
- If no existing stack has space, a new slot is used if available.
- If the inventory cannot hold at least one unit, the gathering action cannot start.
- Bonus units are only added if space exists.

### Why 10 Slots

There are nine resource types. Ten slots allow the player to hold all nine types plus one extra stack. This reduces forced selling during the late game while still creating mild inventory pressure.

### What the Player Cannot Do

The player cannot:

- Drop resources.
- Split stacks manually.
- Convert resources.
- Stack tools.
- Stack furniture.

This keeps the inventory system simple and avoids unnecessary UI complexity.

---

## 5.6 Economy System

### Currency

The only currency is coins.

Starting coins: `25`.

### Selling

Each shopkeeper only buys one resource category.

| Shopkeeper | Buys |
|---|---|
| Moss | Berries |
| Grit | Ores |
| Reed | Fish |

The player opens the shop UI and uses the Sell tab.

The player can sell:

- One unit at a time.
- A full stack.
- All compatible resources with a Sell All button.

### Base Prices

| Resource | Base Sell Price |
|---|---:|
| Sweet Berry | `2` |
| Moon Berry | `5` |
| Ember Berry | `12` |
| Copper Ore | `4` |
| Silver Ore | `10` |
| Crystal Shard | `25` |
| Minnow | `4` |
| Trout | `10` |
| Moonfish | `25` |

### Price Fluctuation: Supply Meter

To prevent players from spamming only one resource and to keep all three shopkeepers relevant, each shop has a supply meter for its category.

The supply meter is per shop, not per individual resource.

#### Supply Meter Values

Supply is a float from `0.0` to `3.0`.

Price multiplier is based on the integer floor of supply:

| Floor Supply | Multiplier |
|---:|---:|
| `0` | `1.00` |
| `1` | `0.85` |
| `2` | `0.70` |
| `3` | `0.60` |

Final sell price:

```text
final_price = max(1, floor(base_price * multiplier))
```

#### Selling Effect

When the player sells `n` units of a shopkeeper’s category:

```text
supply = min(3.0, supply + n / 5)
```

Example:

- Selling `5` units raises supply by `1.0`.
- Selling `1` unit raises supply by `0.2`.
- The price used for the sale is the price before the supply update.

#### Recovery

Supply recovers over time.

Every `120s` after the last sale in that category:

```text
supply = max(0.0, supply - 1.0)
```

This prevents a player from permanently ruining the price of a resource.

### Why Price Fluctuation

Without fluctuation, players may over-focus on one high-yield resource and ignore the others. The supply meter creates a soft incentive to visit all three shopkeepers and keep the economy rotating. It also gives the shopkeepers a small sense of life without requiring daily timers or complex market AI.

### Buying

Shopkeepers sell tools and furniture.

Buy prices are fixed. There is no haggling, stock limit, or buying fluctuation.

The exception is display case furniture, which is unique and cannot be purchased more than once while owned.

---

## 5.7 Shopkeeper System

There are three shopkeepers.

Each shopkeeper has:

- A buy tab.
- A sell tab.
- A current sell price list.
- A shop stock tier.
- A category supply meter.

### Shop Unlock Tiers

Each shop unlocks better stock based on cumulative units sold to that shopkeeper’s category.

| Cumulative Category Sales | Shop Stock Tier |
|---:|---|
| `0` | Tier 1 |
| `5` | Tier 2 |
| `25` | Tier 3 |

Cumulative sales include all resource types in that category.

Example:

- Selling `3` Sweet Berries, `1` Moon Berry, and `1` Ember Berry counts as `5` berry sales.
- Once the player has sold `5` berries total, the Berry shop unlocks Tier 2 stock.
- Once the player has sold `25` berries total, the Berry shop unlocks Tier 3 stock.

### Shop UI

The shop UI should show:

- Buy tab.
- Sell tab.
- Coins.
- For selling:
  - Resource name.
  - Stack count.
  - Current unit price.
  - Total price for stack.
  - Sell button.
  - Sell All button.
  - Supply meter indicator.
- For buying:
  - Item name.
  - Item cost.
  - Item description.
  - Buy button.
  - Locked items show the requirement, such as “Sell 5 berries” or “Sell 25 ores”.

### Supply Meter Display

The shop UI should display a simple supply state:

| Supply Floor | Display |
|---:|---|
| `0` | Normal price |
| `1` | Low price |
| `2` | Very low price |
| `3` | Barely buying |

The exact visual style is the visual designer’s responsibility, but the state must be readable.

### Shopkeeper Content

| Shopkeeper | Name | Resource | Personality Focus |
|---|---|---|---|
| Berry | Moss | Berries | Calm, cozy, plant-focused |
| Ore | Grit | Ores | Practical, sturdy, tool-focused |
| Fish | Reed | Fish | Easygoing, water-focused |

Short UI text examples:

- Moss: “Sweet berries make sweet homes.”
- Grit: “Good ore, good tools.”
- Reed: “The lake gives. Take your share.”

These are UI text, not audio scripts. Audio is out of scope for this document.

---

## 5.8 Furniture System

The player buys furniture and places it in the Home and Museum.

Furniture is not consumed. It exists as a purchased item in the Build Inventory until placed.

### Furniture Categories

There are four furniture groups:

1. Basic decorative furniture.
2. Themed decorative furniture.
3. Display cases for the Museum.
4. Tools, which are bought from shops but are not placeable furniture.

### Build Inventory

Purchased furniture goes into the Build Inventory.

The Build Inventory is separate from the resource inventory.

It is accessed inside buildings using the build mode.

### Build Mode

Build mode is available only inside the Home or Museum.

Toggle with `B`.

In build mode:

- The floor grid is highlighted.
- The player selects an item from the Build Inventory.
- The item follows the mouse.
- `R` rotates the item by `90°`.
- `E` or left click confirms placement.
- `X` or right click deletes the selected placed furniture.
- `Esc` cancels placement.
- The player can open a sell panel to resell unplaced furniture.

### Placement Rules

Furniture can only be placed on interior floor tiles.

A placement is valid if:

- The item fits fully inside the interior floor.
- No tile in the item’s footprint is occupied by another furniture piece.
- The item does not cover the door tile.
- The item does not cover the player’s current tile.
- If the item is a display case, the player is inside the Museum.
- After placing the item, the player still has a valid path from their current tile to the door tile.

### Path Check

The path check is required to prevent softlocks.

When confirming placement:

1. Simulate the new furniture as occupied.
2. Run a path check from the player’s current tile to the door tile.
3. If no path exists, placement is invalid.
4. If a path exists, placement is valid.

The path check only considers floor tiles, walls, door, placed furniture, and the proposed new furniture.

### Why Path Check

If the player could surround themselves with furniture, the game would softlock. Since there is no fail state, preventing placement mistakes is important.

### Rotation

Furniture with non-square footprints can be rotated.

Examples:

- `1x2` rotates to `2x1`.
- `2x1` rotates to `1x2`.
- `1x1` rotation does not change footprint.
- `2x2` rotation does not change footprint.

### Removing Furniture

Placed furniture can be removed in build mode.

When removed:

- The furniture returns to the Build Inventory.
- If it is a display case, any assigned specimens are unassigned.
- The building score updates.
- Goal counts update if the furniture was counted.

### Reselling Furniture

Unplaced furniture can be sold from the Build Inventory.

Sell rules:

- If the furniture was never placed, the player receives `100%` of its buy price.
- If the furniture was previously placed, the player receives `50%` of its buy price, rounded down, minimum `1`.
- Once sold, the furniture is removed from the Build Inventory.
- A display case that is sold can be repurchased from the shop if its stock tier is still unlocked.

### Why Refund Rules

A collector/decoration game should not punish mistakes harshly. The refund system lets players recover from accidental purchases or placements while still preventing furniture from becoming a free money source.

---

## 5.9 Museum and Specimen System

The Museum is where the player displays collection progress.

The Museum is not just a second room. It is the game’s collection showcase.

### Collection Log

When the player first collects a resource type, that resource becomes an unlocked specimen in the collection log.

The player does not need to sell the resource to unlock its specimen.

There are nine specimens total:

| Specimen | Unlocked By Collecting | Exhibit Score |
|---|---|---:|
| Sweet Berry Specimen | Sweet Berry | `10` |
| Moon Berry Specimen | Moon Berry | `25` |
| Ember Berry Specimen | Ember Berry | `60` |
| Copper Ore Specimen | Copper Ore | `10` |
| Silver Ore Specimen | Silver Ore | `25` |
| Crystal Shard Specimen | Crystal Shard | `60` |
| Minnow Specimen | Minnow | `10` |
| Trout Specimen | Trout | `25` |
| Moonfish Specimen | Moonfish | `60` |

### Display Cases

Display cases are special furniture.

Rules:

- Display cases can only be placed in the Museum.
- Display cases are unique. The player can own only one of each display case at a time.
- Display cases have exhibit slots.
- Each exhibit slot can hold one unlocked specimen.
- Each unlocked specimen can be assigned to only one exhibit slot at a time.
- Specimens can only be assigned while the display case is placed in the Museum.
- Removing a display case unassigns its specimens.
- Selling a display case unassigns its specimens.

### Display Case Slots

| Display Case | Slots | Shop |
|---|---:|---|
| Small Display Case | `2` | Berry |
| Pedestal | `1` | Ore |
| Crystal Display Case | `3` | Ore |
| Moon Display Case | `3` | Fish |

Total available exhibit slots: `9`.

This exactly matches the nine total specimens.

### Why Display Cases Are Unique

If display cases could be duplicated, the player could complete the museum by buying many cheap display cases and ignore the Tier 3 shop progression. Making them unique gives each shop a distinct museum contribution and makes Tier 3 stock meaningful.

### Exhibit Assignment UI

When the player selects a placed display case in build mode:

- A panel shows its exhibit slots.
- Each slot shows:
  - Empty state.
  - Assigned specimen.
  - Remove button.
- The panel lists unlocked, unassigned specimens.
- The player can assign or unassign specimens.

### Museum Score

The Museum has a non-binding score.

Museum Score:

```text
Museum Score = sum(exhibit scores of assigned specimens)
            + sum(value of placed museum furniture)
```

Furniture value:

```text
value = ceil(cost / 10)
```

The score is displayed in the Museum build menu.

The score is not required for completion except through the explicit goal requirements.

### Why Museum Score

The score gives the player a sense of progress and encourages optional optimization. It is not a fail check. The main completion goal uses clear count-based requirements so the player always knows what to do.

---

## 5.10 Home Score

The Home also has a non-binding score.

Home Score:

```text
Home Score = sum(value of placed home furniture)
```

Furniture value:

```text
value = ceil(cost / 10)
```

The score is displayed in the Home build menu.

The score does not affect goals.

---

## 5.11 Progression System

Progression is tracked in a Ledger.

The Ledger is accessed with `C` or a HUD button.

The Ledger has three tabs:

1. Goals.
2. Collection.
3. Building Scores.

### Goals

Goals are the player’s direction.

| Goal | Requirement | Reward / Unlock |
|---|---|---|
| First Harvest | Collect `1` Sweet Berry, `1` Copper Ore, `1` Minnow | `10` coins |
| First Trades | Sell `5` Sweet Berries, `5` Copper Ore, `5` Minnow | `25` coins, unlocks Museum, unlocks Tier 2 stock at all shops |
| Cozy Home | Have `5` furniture pieces placed in the Home | `50` coins |
| Open Museum | Have `3` display cases placed in the Museum and `3` specimens assigned | `50` coins |
| Full Collection | Collect all `9` resource types | `100` coins |
| Curator’s Seal | Sell `25` berries, `25` ores, and `25` fish total; assign all `9` specimens in the Museum; have `12` furniture pieces placed in the Museum | Completion |

### Goal Behavior

Goals are count-based.

- If the player removes furniture after completing a goal, the goal does not uncomplete unless the goal is still active.
- Once a goal is complete, it stays complete.
- The final goal, Curator’s Seal, requires the final state to be true when checked.
- If the player removes required furniture or unassigns specimens after completing the final goal, the completion remains complete.

### Shop Tier Progression

Shop tiers are separate from goals, but they are guided by selling.

| Category Sales | Shop Stock |
|---:|---|
| `0` | Tier 1 |
| `5` | Tier 2 |
| `25` | Tier 3 |

The Ledger can show progress toward shop tiers even if they are not main goals.

### Why Goals Are Count-Based

Count-based goals are clear and safe. They avoid vague “make it look good” objectives. The player can always see exactly what is needed.

---

## 6. Algorithms

## 6.1 World Node Placement Algorithm

The world should be deterministic. Use a seeded random number generator.

Suggested seed: `42`.

For each biome:

1. Define a mask of valid tiles.
2. For each resource quota:
   - Define any submask for higher-tier resources.
   - Place nodes until the quota is reached.
3. Use a minimum distance between nodes.
4. Reject placement if:
   - The tile is on a path.
   - The tile is near a door.
   - The tile is too close to another node.
   - The tile is invalid for the biome.

Pseudo:

```text
seed = 42
rng = seededRng(seed)

for each biome:
    for each resource:
        placed = 0
        minDistance = 4
        attempts = 0

        while placed < resource.quota and attempts < 1000:
            tile = rng.randomTile(resource.mask)
            if tile is valid:
                if distanceToNearestExistingNode(tile) >= minDistance:
                    placeNode(tile, resource)
                    placed += 1
            attempts += 1

        if placed < resource.quota:
            minDistance = 3
            retry placement until quota is reached or no valid tile exists
```

### Node Validity

A node tile is invalid if:

- It is outside the biome mask.
- It is on a village path.
- It is within `2` tiles of any door.
- It is too close to another node.
- It is in the perimeter.

### Tier Submasks

- Ember Berry: northernmost Berry Grove area.
- Crystal Shard: easternmost Ore Ridge area.
- Moonfish: deep southern Lake area.

### Why This Algorithm

A purely random map can feel chaotic. A hand-tuned quota-based placement gives reliable resource availability while still feeling organic. The minimum distance prevents nodes from clumping into ugly dense spots.

---

## 6.2 Berry Respawn Algorithm

For each berry node:

State:

- `full`
- `empty`
- `respawnTimer`

When picked:

```text
if inventory can hold at least 1 berry:
    yield = 1
    if rng < bonusYieldChance:
        if inventory can hold 2 berries:
            yield = 2
    addBerries(yield)
    set state to empty
    respawnTimer = resource.respawnTime
```

Update:

```text
if state == empty:
    respawnTimer -= deltaTime
    if respawnTimer <= 0:
        state = full
        berryCount = randomInt(1, 2)
```

---

## 6.3 Ore Respawn Algorithm

For each ore node:

State:

- `charges`
- `empty`
- `respawnTimer`

When mined:

```text
if charges > 0 and inventory can hold at least 1 ore:
    yield = 1
    if rng < bonusYieldChance:
        if inventory can hold 2 ores:
            yield = 2
    addOres(yield)
    charges -= 1
    if charges == 0:
        set state to empty
        respawnTimer = resource.emptyTime
```

Update:

```text
if state == empty:
    respawnTimer -= deltaTime
    if respawnTimer <= 0:
        state = full
        charges = 3
```

---

## 6.4 Fishing Algorithm

For each fish spot:

State:

- `cooldownTimer`
- `fishingState`
- `phaseTimer`

Possible fishing states:

- `idle`
- `casting`
- `waiting`
- `biteMeter`

Pseudo:

```text
on interact at fishSpot:
    if fishSpot.cooldownTimer > 0:
        return
    if not inventory can hold at least 1 fish:
        return
    fishingState = casting
    phaseTimer = 0.6

update:
    if fishingState == casting:
        phaseTimer -= deltaTime
        if phaseTimer <= 0:
            fishingState = waiting
            phaseTimer = randomInRange(tool.waitMin, tool.waitMax)

    if fishingState == waiting:
        phaseTimer -= deltaTime
        if phaseTimer <= 0:
            fishingState = biteMeter
            phaseTimer = 1.5

    if fishingState == biteMeter:
        phaseTimer -= deltaTime
        if phaseTimer <= 0:
            failFish()
```

On interact during `biteMeter`:

```text
meterProgress = 1 - phaseTimer / 1.5
position = meterProgress * meterWidth

if position is inside green zone:
    success = true
elif position is inside yellow zone:
    success = rng < tool.yellowSuccessChance
else:
    success = false

if success:
    yield = 1
    if rng < tool.bonusFishChance:
        if inventory can hold 2 fish:
            yield = 2
    addFish(yield)
else:
    failFish()
```

`failFish()` sets:

```text
fishingState = idle
fishSpot.cooldownTimer = tool.cooldown
```

---

## 6.5 Shop Price Algorithm

For each shop:

Track:

- `supply`: `0.0` to `3.0`
- `cumulativeSold`: integer
- `lastSaleTime`

Price multiplier:

```text
supplyTier = floor(supply)
multiplier = [1.00, 0.85, 0.70, 0.60][supplyTier]
```

Sell price:

```text
price = max(1, floor(basePrice * multiplier))
```

On sale of `n` units:

```text
oldPrice = current price
totalPaid = oldPrice * n
supply = min(3.0, supply + n / 5)
cumulativeSold += n
lastSaleTime = now
```

Recovery:

```text
if now - lastSaleTime >= 120:
    supply = max(0.0, supply - 1.0)
    lastSaleTime = now - (120 - ((now - lastSaleTime) % 120))
```

### Shop Tier Algorithm

```text
if cumulativeSold >= 25:
    stockTier = 3
elif cumulativeSold >= 5:
    stockTier = 2
else:
    stockTier = 1
```

---

## 6.6 Furniture Placement Algorithm

When the player attempts to place furniture:

Inputs:

- Item.
- Anchor tile.
- Rotation.
- Current building.

Pseudo:

```text
canPlace(item, anchorTile, rotation, building):
    if item is display case and building != Museum:
        return false

    footprint = getFootprint(item, anchorTile, rotation)

    if any tile in footprint is not floor:
        return false

    if any tile in footprint is the door tile:
        return false

    if any tile in footprint is occupied by placed furniture:
        return false

    if anchorTile or any footprint tile is the player tile:
        return false

    simulatedOccupancy = currentOccupancy
    add footprint tiles to simulatedOccupancy

    if not pathExists(playerTile, doorTile, simulatedOccupancy):
        return false

    return true
```

### Path Check

Use breadth-first search or any equivalent path algorithm.

Valid path tiles:

- Floor tiles.
- Door tile.

Invalid path tiles:

- Walls.
- Occupied furniture tiles.
- Proposed new furniture tiles.

If no path exists from the player’s current tile to the door tile, placement is invalid.

---

## 6.7 Goal Progression Algorithm

Goals update on events:

- Resource collected.
- Resource sold.
- Furniture placed.
- Furniture removed.
- Specimen assigned.
- Specimen unassigned.
- Display case removed.
- Display case sold.
- Shop cumulative sales changed.

For each event:

1. Update the relevant counters.
2. Check all incomplete goals.
3. If a goal becomes complete:
   - Mark it complete.
   - Grant reward.
   - Apply unlock.
   - Show toast.
   - Play goal-complete sound.
   - Update Ledger.

### Unlock Rules

- `First Trades` unlocks Museum.
- `First Trades` also ensures Tier 2 stock is available at all three shops, because it requires five sales in each category.
- Tier 2 and Tier 3 stock unlock individually per shop based on that shop’s cumulative sales.
- `Curator’s Seal` is the final completion state.

---

## 7. Content and Numbers

## 7.1 Resource Content

### Berries

| Resource | Tier | Base Sell | Stack | Nodes | Respawn | Location Hint |
|---|---:|---:|---:|---:|---:|---|
| Sweet Berry | 1 | `2` | `20` | `30` | `20s` | Berry Grove, common |
| Moon Berry | 2 | `5` | `20` | `15` | `45s` | Berry Grove, middle/south |
| Ember Berry | 3 | `12` | `20` | `5` | `120s` | Berry Grove, northern edge |

### Ores

| Resource | Tier | Base Sell | Stack | Nodes | Charges | Empty Time | Location Hint |
|---|---:|---:|---:|---:|---:|---:|---|
| Copper Ore | 1 | `4` | `10` | `25` | `3` | `300s` | Ore Ridge, common |
| Silver Ore | 2 | `10` | `10` | `12` | `3` | `360s` | Ore Ridge, eastern half |
| Crystal Shard | 3 | `25` | `10` | `4` | `3` | `720s` | Ore Ridge, eastern tip |

### Fish

| Resource | Tier | Base Sell | Stack | Spots | Notes | Location Hint |
|---|---:|---:|---:|---:|---|---|
| Minnow | 1 | `4` | `5` | `15` | Common | Lake shore |
| Trout | 2 | `10` | `5` | `8` | Middle lake | Lake center |
| Moonfish | 3 | `25` | `5` | `3` | Rare | Deep south lake |

---

## 7.2 Tool Content

Tools are purchased from the matching shop.

| Tool | Shop | Tier | Cost | Effect Summary |
|---|---|---:|---:|---|
| Woven Basket | Moss | 1 | Owned | Base berry picking |
| Honey Pouch | Moss | 2 | `35` | Faster berry picking, +1 chance |
| Ember Satchel | Moss | 3 | `90` | Best berry picking |
| Hand Pick | Grit | 1 | Owned | Base mining |
| Copper Pick | Grit | 2 | `35` | Faster mining, +1 chance |
| Silver Pick | Grit | 3 | `90` | Best mining |
| Short Rod | Reed | 1 | Owned | Base fishing |
| Bamboo Rod | Reed | 2 | `35` | Easier fishing, +1 chance |
| Moon Rod | Reed | 3 | `90` | Best fishing |

Tool purchase behavior:

- Buying a higher-tier tool replaces the current tool.
- Buying a lower-tier tool is not allowed.
- Buying the same tool is not allowed.
- Tools cannot be placed.
- Tools cannot be sold.
- Tools persist across sessions.

---

## 7.3 Furniture Content

Furniture is purchased from shops.

All non-display furniture can be purchased multiple times.

Display case furniture is unique. The player can own only one at a time.

### Furniture Value

Furniture value for building score:

```text
value = ceil(cost / 10)
```

### Berry Shop Furniture

Shopkeeper: Moss  
Buys: Berries

| Item | Unlock | Type | Size | Cost | Notes |
|---|---|---|---:|---:|---|
| Berry Planter | Start | Decor | `1x1` | `10` | Home or Museum |
| Berry Jar | Start | Decor | `1x1` | `15` | Home or Museum |
| Rug | Start | Decor | `2x2` | `10` | Home or Museum |
| Honey Pouch | Tier 2 | Tool | `—` | `35` | Berry tool |
| Berry Bench | Tier 2 | Decor | `2x1` | `45` | Home or Museum |
| Small Display Case | Tier 2 | Display | `1x1` | `40` | Museum only, `2` exhibit slots, unique |
| Ember Satchel | Tier 3 | Tool | `—` | `90` | Berry tool |
| Berry Rug | Tier 3 | Decor | `2x2` | `70` | Home or Museum |

### Ore Shop Furniture

Shopkeeper: Grit  
Buys: Ores

| Item | Unlock | Type | Size | Cost | Notes |
|---|---|---|---:|---:|---|
| Side Table | Start | Decor | `1x1` | `10` | Home or Museum |
| Bookshelf | Start | Decor | `1x2` | `20` | Home or Museum |
| Ore Lamp | Start | Decor | `1x1` | `15` | Home or Museum |
| Copper Pick | Tier 2 | Tool | `—` | `35` | Mining tool |
| Ore Workbench | Tier 2 | Decor | `2x1` | `55` | Home or Museum |
| Pedestal | Tier 2 | Display | `1x1` | `35` | Museum only, `1` exhibit slot, unique |
| Silver Pick | Tier 3 | Tool | `—` | `90` | Mining tool |
| Crystal Display Case | Tier 3 | Display | `1x1` | `80` | Museum only, `3` exhibit slots, unique |

### Fish Shop Furniture

Shopkeeper: Reed  
Buys: Fish

| Item | Unlock | Type | Size | Cost | Notes |
|---|---|---|---:|---:|---|
| Fish Net Rack | Start | Decor | `1x1` | `10` | Home or Museum |
| Fish Barrel | Start | Decor | `1x1` | `15` | Home or Museum |
| Water Shelf | Start | Decor | `1x1` | `15` | Home or Museum |
| Bamboo Rod | Tier 2 | Tool | `—` | `35` | Fishing tool |
| Fish Bench | Tier 2 | Decor | `2x1` | `45` | Home or Museum |
| Fish Tank | Tier 2 | Decor | `2x1` | `70` | Home or Museum |
| Moon Rod | Tier 3 | Tool | `—` | `90` | Fishing tool |
| Moon Display Case | Tier 3 | Display | `1x1` | `80` | Museum only, `3` exhibit slots, unique |

### Total Furniture Counts

| Category | Count |
|---|---:|
| Tools | `9` |
| Non-display furniture | `15` |
| Display cases | `4` |
| Total shop items | `28` |

The four display cases provide exactly nine exhibit slots:

| Display Case | Slots |
|---|---:|
| Small Display Case | `2` |
| Pedestal | `1` |
| Crystal Display Case | `3` |
| Moon Display Case | `3` |
| Total | `9` |

---

## 7.4 Goal and Reward Content

| Goal | Requirement | Reward |
|---|---|---|
| First Harvest | Collect `1` Sweet Berry, `1` Copper Ore, `1` Minnow | `10` coins |
| First Trades | Sell `5` Sweet Berries, `5` Copper Ore, `5` Minnow | `25` coins, Museum unlock, Tier 2 stock at all shops |
| Cozy Home | `5` furniture pieces placed in Home | `50` coins |
| Open Museum | `3` display cases placed in Museum and `3` specimens assigned | `50` coins |
| Full Collection | Collect all `9` resource types | `100` coins |
| Curator’s Seal | Sell `25` berries, `25` ores, `25` fish; assign all `9` specimens; `12` museum furniture placed | Completion |

### Goal Progress Display

The Ledger shows:

- Current goal.
- Progress bar or fraction.
- Remaining requirements.
- Completed goals with a checkmark.

Example:

```text
First Trades
Sell 5 berries: 3/5
Sell 5 ores: 5/5
Sell 5 fish: 1/5
```

---

## 7.5 Pacing

Expected progression:

| Time | Expected State |
|---|---|
| Start | Player has `25` coins, Tier 1 tools, museum locked |
| 5–10 minutes | Player completes First Trades, unlocks museum and Tier 2 stock |
| 15–25 minutes | Player places first furniture, opens museum, buys Tier 2 tools |
| 30–45 minutes | Player collects higher-tier resources, reaches 25 sales in categories, unlocks Tier 3 stock |
| 60–90 minutes | Player completes full collection, curates museum, completes Curator’s Seal |

The pacing should feel like steady accumulation. The player should rarely be stuck for more than a short time because resources respawn and basic selling is always possible.

---

## 8. HUD and UI

The HUD should be readable at a glance. Do not clutter the screen.

### 8.1 Persistent HUD

#### Top-Left

- Location label.
  - Village.
  - Berry Grove.
  - Ore Ridge.
  - Lakeside.
  - Home.
  - Museum.
- Ledger button.
  - Keyboard shortcut: `C`.
  - Shows goal progress icon if a goal is active.

#### Top-Right

- Coins.
- Minimap.
  - Size: approximately `96 x 96` pixels.
  - Shows:
    - Player dot.
    - Home dot.
    - Museum dot.
    - Trading Post dot.
    - Biome color regions.
  - Does not show individual resource nodes.

#### Bottom-Left

Tool tier indicators:

- Berry tool icon with tier.
- Mining tool icon with tier.
- Fishing tool icon with tier.

Tier display:

- Tier 1: no stars or `I`.
- Tier 2: one star or `II`.
- Tier 3: two stars or `III`.

The exact icon style is visual design’s responsibility.

#### Bottom-Center

Inventory:

- 10 slots.
- Each slot shows:
  - Resource icon.
  - Stack count.
- Empty slots are clearly visible.
- Hovering over a slot shows:
  - Resource name.
  - Stack count.
  - Base sell price.
  - Current shop price if at the matching shop.

#### Bottom-Right

Contextual input hints:

- `E` or left click: interact.
- `B`: build mode when inside Home/Museum.
- `C`: ledger.
- `I`: inventory details if separate from persistent inventory.
- `Esc`: cancel menu.

Only show hints that apply to the current context.

#### Center Screen

- Interaction prompt.
- Progress bar for gathering/mining.
- Fishing meter during bite phase.

Interaction prompt examples:

- `Pick Sweet Berry`
- `Mine Copper Ore`
- `Cast Line`
- `Talk to Moss`
- `Enter Home`
- `Museum Locked`
- `Place Furniture`

### 8.2 Shop UI

When the player talks to a shopkeeper:

The UI should show:

- Shopkeeper name.
- Coin total.
- Buy tab.
- Sell tab.

#### Sell Tab

For each sellable resource in inventory:

- Resource icon.
- Name.
- Stack count.
- Current unit price.
- Stack total.
- Sell button.

Controls:

- Click sell to sell one unit.
- Shift-click or click stack button to sell entire stack.
- Sell All button sells all compatible resources.

The supply meter should be visible, such as:

- `Normal Price`
- `Low Price`
- `Very Low Price`
- `Barely Buying`

#### Buy Tab

For each available item:

- Item icon.
- Name.
- Cost.
- Short description.
- Buy button.

Locked items should show:

- Grayed out.
- Lock icon.
- Requirement text.

Examples:

- `Sell 5 berries to unlock`
- `Sell 25 ores to unlock`
- `Museum only`
- `Unique: already owned`

### 8.3 Build Mode UI

Available only inside Home or Museum.

When build mode is active:

- Floor grid highlight.
- Selected item card.
- Rotate button or hint.
- Delete button or hint.
- Cancel button or hint.
- Sell panel for unplaced furniture.
- Building score.

#### Selected Item Card

Shows:

- Item icon.
- Item name.
- Footprint.
- Rotate state.
- Placement validity.
- If invalid:
  - Reason, such as `Blocked`, `Not Floor`, `Museum Only`, `Blocks Door Path`.

#### Exhibit Panel

Available when selecting a placed display case:

- Display case name.
- Exhibit slots.
- Assigned specimens.
- Unassigned specimen list.
- Assign button.
- Remove button.

### 8.4 Ledger UI

Accessed with `C`.

Tabs:

#### Goals Tab

Shows:

- Current goal.
- Progress.
- Rewards.
- Completed goals.

#### Collection Tab

Shows:

- 9 resource entries.
- Collected or not collected.
- Location hint.
- Exhibit score.
- Assigned status if displayed in museum.

#### Building Scores Tab

Shows:

- Home Score.
- Museum Score.
- Museum exhibit count.
- Museum furniture count.
- Home furniture count.

### 8.5 Toasts

Show short notifications for:

- Goal complete.
- Shop stock unlocked.
- Museum unlocked.
- New specimen collected.
- Tool purchased.
- Furniture placed.
- Furniture sold.
- Final completion.

Toasts should appear top-center and disappear after `3s`.

---

## 9. Edge Cases and All Cases

The game must handle every normal and abnormal player behavior without failing.

### 9.1 Player Has No Coins

- The player can always gather resources.
- Basic resources are always available.
- The player can sell at least some price, even if supply is low.
- No purchase is mandatory to continue the game.

### 9.2 Inventory Is Full

- Gathering cannot start.
- The HUD shows a clear prompt: `Bag Full`.
- The player must sell resources at a shopkeeper.
- The player cannot drop resources.
- The game does not block movement.

### 9.3 Resource Node Is Empty

- Berry bushes respawn after `20s`, `45s`, or `120s`.
- Ore nodes respawn after `300s`, `360s`, or `720s`.
- Fish spots do not deplete.
- The player can always switch zones while waiting.
- No resource is permanently unavailable.

### 9.4 Shop Price Is Low

- Supply recovers over time.
- The player can sell other resource categories.
- The player can wait.
- The game does not lock the player out of money forever.

### 9.5 Shop Stock Is Locked

- Locked items show the requirement.
- Basic stock is always available.
- The player can always progress by selling basic resources.
- Tier 2 and Tier 3 stock are not required for basic movement, but are required for full completion.

### 9.6 Museum Is Locked

- The museum door shows `Museum Locked`.
- The requirement is shown:
  - Sell `5` berries.
  - Sell `5` ores.
  - Sell `5` fish.
- The player cannot enter until the requirement is complete.
- The player can still play outside and in the Home.

### 9.7 Furniture Placement Is Invalid

Invalid if:

- It is not on floor.
- It overlaps another furniture piece.
- It covers the door.
- It covers the player.
- It is a display case placed in the Home.
- It would block the path to the door.

The UI shows a red footprint and a reason.

### 9.8 Player Removes Required Furniture

- If the goal is already complete, completion remains complete.
- If the goal is not complete, the goal progress updates downward.
- If the removed furniture was a display case, assigned specimens are unassigned.
- Museum score updates.

### 9.9 Player Sells a Display Case

- If it was never placed, the player receives `100%` refund.
- If it was previously placed, the player receives `50%` refund.
- Assigned specimens are unassigned.
- The display case can be repurchased if the shop tier is still unlocked.

### 9.10 Player Sells Furniture Repeatedly

- There is no profit loop.
- Never placed furniture refunds `100%`.
- Previously placed furniture refunds `50%`.
- The player can repurchase, but cannot create coins from nothing.

### 9.11 Player Cannot Afford a Tool

- The buy button is disabled.
- The player can sell more resources.
- The game does not block movement.

### 9.12 Player Has All Resources Collected But No Money

- Resources can still be sold.
- The player can continue placing existing furniture.
- If they need to buy a display case, they must sell resources.
- There is no fail state.

### 9.13 Player Completes the Game

- Show a completion screen: `Curator’s Seal`.
- The ledger shows all goals complete.
- The game remains playable.
- All systems remain active.
- The player can continue placing, removing, selling, and collecting.

### 9.14 Player Closes Browser Mid-Game

All meaningful state must be saved:

- Player position.
- Coins.
- Inventory.
- Tool tiers.
- Shop cumulative sales.
- Shop supply meters.
- Museum unlocked state.
- Placed furniture.
- Build Inventory.
- Sold furniture flags.
- Display case exhibit assignments.
- Collection log.
- Goal completion state.
- Home and Museum scores.

---

## 10. Completion and Post-Completion

### Completion Requirement

The final goal is `Curator’s Seal`.

To complete:

1. Sell at least `25` berries total.
2. Sell at least `25` ores total.
3. Sell at least `25` fish total.
4. Assign all `9` specimens in the Museum.
5. Have at least `12` furniture pieces placed in the Museum.

When complete:

- Show completion screen.
- Add a curator icon or badge to the ledger.
- Do not remove any existing content.
- Do not lock the player out of anything.

### Post-Completion

After completion:

- The player can continue playing.
- The museum remains accessible.
- All shop stock remains available.
- Resources continue to respawn.
- Furniture can be moved, sold, or repurchased.
- No new required goals appear.
- No failure state is added.

### Why Post-Completion Is Open-Ended

Collector players often enjoy rearranging and optimizing. The game should reward completion but not end abruptly.

---

## 11. Required Feedback

The following events need visible feedback.

### Visible Feedback

- Resource collected.
- Resource sold.
- Coins changed.
- Goal progress updated.
- Goal completed.
- Shop stock unlocked.
- Museum unlocked.
- New specimen collected.
- Tool purchased.
- Furniture purchased.
- Furniture placed.
- Furniture removed.
- Furniture sold.
- Specimen assigned.
- Specimen unassigned.
- Final completion.

### Needed Sounds

Sound specifics are the visual/audio designer’s responsibility, but these events need sounds:

- Berry pick complete.
- Ore mine complete.
- Fish cast.
- Fish bite.
- Fish catch.
- Fish fail.
- Coin sale.
- Coin buy.
- Furniture place.
- Furniture remove.
- Furniture sell.
- Goal complete.
- Shop unlock.
- Museum unlock.
- Final completion.

---

## 12. Design Rationale Summary

### Why 2D Top-Down

Open-world visibility and furniture placement are clearer in top-down. The game does not need vertical depth.

### Why No Combat

Combat is not part of the requested fantasy. It would add systems that distract from collecting and decorating.

### Why No Fail State

Collector games should feel safe. The player should be able to make mistakes without losing progress.

### Why Supply Meter

It prevents one-resource spam, encourages all three shopkeepers, and gives the economy a living feel without complex market systems.

### Why Tools Are Bought, Not Crafted

The core loop is gather-sell-buy. Crafting would add complexity that is not necessary for the collector fantasy.

### Why Display Cases Are Unique

It makes each shop’s museum contribution meaningful and prevents the player from trivializing the display goal by buying multiple cheap cases.

### Why Path Check on Furniture Placement

It prevents softlocks, which is especially important in a game with no fail state.

### Why Count-Based Goals

Count-based goals are clear, trackable, and prevent vague player confusion.

### Why the Game Is Compact

The loop is the product. If travel is too long, the collect-sell-place cycle becomes boring. A compact open world preserves the open-world feel while maintaining pacing.

---

## 13. Handoff Notes for Other Agents

### For Visual Designer

You are responsible for:

- Icons.
- Resource node art states:
  - Berry full.
  - Berry empty.
  - Ore with 3 charges.
  - Ore with 2 charges.
  - Ore with 1 charge.
  - Ore empty.
  - Fish spot idle.
  - Fish bite.
  - Fish caught.
- Player sprite states:
  - Idle.
  - Move.
  - Gather.
  - Mine.
  - Fish.
- Shopkeeper characters.
- Furniture art.
- UI skin.
- Minimap style.
- Toast style.
- Progress bar style.
- Valid/invalid placement colors.

You do not need to define gameplay numbers, but you must support the states listed above.

### For Engineering

You are responsible for:

- Tile map loading.
- Player movement and collision.
- Resource node state.
- Inventory state.
- Shop UI and economy state.
- Furniture placement validation.
- Path checking.
- Save/load.
- Fishing timer.
- Supply timer.
- Goal state.
- Museum exhibit assignment.

The algorithms in this document define the required behavior. Exact implementation is up to the engineering agent.

### For Audio Designer

You are responsible for:

- Ambient music.
- Gather sounds.
- Fishing sounds.
- Shop sounds.
- UI sounds.
- Goal completion sounds.

This gameplay document only defines which events need audio, not the sound specifics.