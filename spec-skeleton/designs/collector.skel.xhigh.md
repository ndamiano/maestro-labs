# Build Spec: Hollow Harvest

An open-world browser collector game where the player walks a small valley, gathers berries, ore, and fish, sells to a shopkeeper, and buys furniture for a home and a small museum. The core feeling should be cozy, spatial, and collection-driven: each region has a different resource, each resource has a different value and rarity, and the museum gives the collected world a purpose.

---

# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Open world collector game | Section 4, World unit |
| Player walks around | Section 4.1, Input and Player units |
| Collecting resources | Section 4.2, Inventory record |
| Harvest berries | Section 4.3, Berry Node system |
| Mine ores | Section 4.4, Ore Node system |
| Fish fish | Section 4.5, Fishing system |
| Sell them to a shopkeeper for each type | Section 4.6, Shopkeeper and Economy |
| Buy furniture to decorate their home | Section 4.7, Home Placement |
| Buy furniture to decorate a small museum-type building | Section 4.7, Museum Placement and Exhibits |
| Deterministic seeded world so tests can repeat | Section 1.2, Section 2.2, Section 8 |
| Day/season cycle affecting growth and rare fish | Section 1.1, Section 4.6, Section 3.1 |
| Reputation progression and shop unlocks | Section 4.6, Section 4.7 |
| Collection log and museum exhibits | Section 4.7, Section 7 |
| HUD, shop, placement, and title screens | Section 7, Overlay unit |
| Synthesized audio cues | Section 6, Sound unit |
| Debug API for scripted checks | Section 8 |
| Playable definition of done | Section 11 |

## 0.2 Tiers

| Tier | Meaning | Included features |
| --- | --- | --- |
| T1 | Must ship | Title, world generation, player movement, berry and ore harvesting, basic fishing, inventory, shopkeeper selling, basic home placement, basic debug, basic HUD |
| T2 | Core collector loop | Museum slots, museum exhibits, collection log, shopkeeper buying, reputation, requests, season/day cycle, synthesized audio |
| T3 | Progression and polish | Rare resources, night-only fish, tiered furniture, lighting, particles, request UI, slot unlocks, museum scholarship, home comfort |
| T4 | Nice-to-have | Extra furniture variety, ambient audio, more visual variation, performance tuning, screenshot states for verification |

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Concept | Value |
| --- | --- |
| View | Top-down 2D |
| X axis | Right |
| Y axis | Down |
| Tile size | 48 screen pixels |
| World size | 64 x 64 tiles |
| World pixel size | 3072 x 3072 pixels |
| Logical position | Floating-point tile coordinates, e.g. `x: 32.5, y: 35` |
| Player radius | 0.4 tile |
| Player speed | 4 tiles/second |
| Action radius | 1.4 tiles |
| Fishing radius | 2.5 tiles |
| Simulation tick | 1/60 second |
| Target frame rate | 60 frames/second |
| Day length | 60 seconds |
| Night phase | Last 15 seconds of each 60-second day |
| Season length | 300 seconds |
| Seasons | Spring, Summer, Autumn, Winter, in that order |
| Money | Integer |
| Reputation | Integer |
| Inventory max per resource | 20 |
| Storage max per item | 5 |
| Shopkeeper radius | 2.0 tiles |

A position is always in tile units unless explicitly named as pixels. Rendering converts tile units to screen pixels by multiplying by 48.

## 1.2 Important conventions

- The game state is the only source of truth.
- All random numbers come from one seeded random source.
- No hidden timers, hidden queues, or hidden per-system randomness.
- All timed events use simulation seconds, not real wall-clock time.
- The world is generated from the seed when the game is reset or seeded.
- Resource nodes occupy one tile. Ore nodes block that tile. Berry nodes also block that tile for simplicity.
- Water tiles are not walkable.
- Fishing is allowed only from a non-water tile adjacent to water.
- The player can sell and buy only when within the shopkeeper radius.
- Placement can happen anywhere, but only if the slot is unlocked and empty.
- The museum has display cases and decorative museum furniture.
- Home furniture increases comfort.
- Museum furniture and exhibits increase scholarship.
- Reputation unlocks more home slots, museum slots, and higher-tier shop stock.
- The debug layer must be able to drive the whole game without UI clicks.
- All debug calls must be synchronous and return plain data.

---

# 2. CONTRACTS

## 2.1 Build layout

These are logical build units. They describe responsibilities and interactions, not implementation artifacts.

| Unit | Responsibility | Main inputs | Main outputs |
| --- | --- | --- | --- |
| Boot | Create state, install debug hook, start title screen | Seed, viewport size | Playable game state |
| World | Generate terrain, water, shore, buildings, nodes, fish, slots | Seed | World records |
| Entities | Represent player, nodes, fish, shopkeeper, slots | State | Entity records |
| Systems | Time, movement, harvesting, fishing, shop, placement, collection, requests, progression | State and inputs | Updated state |
| Presentation | Draw world, entities, lighting, particles | State | Screen frame |
| Sound | Synthesize short audio cues | Game events | Audio output |
| Overlay | Title, HUD, shop, inventory, placement, collection | State and user intent | UI state |
| Test hook | Expose deterministic controls and state reads | Debug calls | Plain data |

Interaction model:

- Overlay sends user intent to Systems.
- Systems read and write State.
- Presentation reads State only.
- Sound reads event results or State changes.
- Test hook reads and writes State through the same public rules.

## 2.2 Global context

The whole game consumes one plain state object.

```text
state = {
  phase: string,
  seed: number,
  time: number,
  day: number,
  seasonIndex: number,
  night: boolean,
  money: number,
  reputation: number,
  homeComfort: number,
  museumScholarship: number,
  homeUnlocked: number,
  museumUnlocked: number,

  player: {
    x: number,
    y: number,
    dirX: number,
    dirY: number,
    inventory: object,
    storage: object,
    selectedItemId: string | null,
    selectedSlotId: string | null,
    actionHeld: boolean,
    actionMode: string,
    actionTimer: number
  },

  world: {
    width: number,
    height: number,
    tiles: array,
    waterTiles: array,
    shoreTiles: array,
    homeSlots: array,
    museumSlots: array,
    nodes: array,
    fish: array
  },

  shop: {
    x: number,
    y: number,
    lastRefreshDay: number,
    stock: object,
    buyPrices: object,
    requests: array
  },

  collection: object
}
```

Field meaning:

| Field | Meaning |
| --- | --- |
| `phase` | `"title"`, `"play"`, or `"paused"` |
| `seed` | Current random seed |
| `time` | Simulation seconds since play started |
| `day` | `floor(time / 60) + 1` |
| `seasonIndex` | `0` Spring, `1` Summer, `2` Autumn, `3` Winter |
| `night` | True when `(time % 60) >= 45` |
| `money` | Player money |
| `reputation` | Player reputation |
| `homeComfort` | Sum of comfort values of placed home furniture |
| `museumScholarship` | Sum of scholarship values of museum decor and exhibits |
| `homeUnlocked` | Number of unlocked home slots |
| `museumUnlocked` | Number of unlocked museum slots |
| `player.inventory` | Map of resource ID to count |
| `player.storage` | Map of item ID to count |
| `player.selectedItemId` | Item selected for placement |
| `player.selectedSlotId` | Slot selected for placement |
| `player.actionHeld` | Whether the action input is held |
| `player.actionMode` | `"none"`, `"berry"`, `"ore"`, or `"fish"` |
| `player.actionTimer` | Seconds spent on current action |
| `world.tiles` | Flat array of tile types, length 4096 |
| `world.waterTiles` | Array of `{x, y}` water tiles |
| `world.shoreTiles` | Array of `{x, y}` walkable tiles adjacent to water |
| `world.homeSlots` | Home slot records |
| `world.museumSlots` | Museum slot records |
| `world.nodes` | Berry and ore node records |
| `world.fish` | Fish records |
| `shop.stock` | Map of item ID to count |
| `shop.buyPrices` | Map of resource ID to sell price |
| `shop.requests` | Active request records |
| `collection` | Map of resource ID to collection record |

Collection record:

```text
{
  discovered: boolean,
  collectedTotal: number,
  displayedCount: number
}
```

Node record:

```text
{
  id: string,
  kind: string,
  type: string,
  x: number,
  y: number,
  count: number,
  maxCount: number,
  regrowTimer: number
}
```

Fish record:

```text
{
  id: string,
  alive: boolean,
  type: string,
  x: number,
  y: number,
  vx: number,
  vy: number,
  respawnTimer: number
}
```

Home slot record:

```text
{
  id: string,
  x: number,
  y: number,
  item: string | null,
  unlocked: boolean
}
```

Museum slot record:

```text
{
  id: string,
  x: number,
  y: number,
  item: string | null,
  exhibitResourceId: string | null,
  scholarship: number,
  unlocked: boolean
}
```

Request record:

```text
{
  id: string,
  resourceId: string,
  countNeeded: number,
  rewardMoney: number,
  rewardRep: number,
  done: boolean
}
```

## 2.3 Signatures and constants

### Resource catalog

| Resource ID | Name | Category | Value | Reputation | Rarity |
| --- | --- | --- | ---: | ---: | --- |
| `red_berry` | Red Berry | Berry | 3 | 1 | 1 |
| `blue_berry` | Blue Berry | Berry | 4 | 1 | 1 |
| `golden_berry` | Golden Berry | Berry | 8 | 2 | 2 |
| `frost_berry` | Frost Berry | Berry | 15 | 4 | 3 |
| `copper` | Copper Ore | Ore | 6 | 2 | 1 |
| `iron` | Iron Ore | Ore | 10 | 3 | 2 |
| `silver` | Silver Ore | Ore | 18 | 5 | 3 |
| `crystal` | Crystal Shard | Ore | 35 | 10 | 4 |
| `minnow` | Minnow | Fish | 5 | 2 | 1 |
| `perch` | Perch | Fish | 7 | 3 | 1 |
| `pike` | Pike | Fish | 14 | 5 | 2 |
| `trout` | Trout | Fish | 25 | 8 | 3 |
| `lumifin` | Lumifin | Fish | 45 | 15 | 4 |

### Item catalog

| Item ID | Name | Category | Tier | Price | Reputation Required | Comfort or Scholarship | Case? | Case Tier |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| `home_plant_small` | Small Plant | Home | 1 | 30 | 0 | 2 | No | 0 |
| `home_rug_round` | Round Rug | Home | 1 | 45 | 0 | 3 | No | 0 |
| `home_lamp_warm` | Warm Lamp | Home | 2 | 80 | 100 | 5 | No | 0 |
| `home_table_wood` | Wood Table | Home | 2 | 110 | 100 | 6 | No | 0 |
| `home_sofa_blue` | Blue Sofa | Home | 3 | 180 | 250 | 9 | No | 0 |
| `home_clock_tiny` | Tiny Clock | Home | 3 | 140 | 250 | 7 | No | 0 |
| `home_fireplace` | Fireplace | Home | 4 | 300 | 500 | 14 | No | 0 |
| `home_chandelier` | Chandelier | Home | 5 | 500 | 1000 | 20 | No | 0 |
| `museum_plinth_basic` | Basic Plinth | Museum | 1 | 50 | 0 | 0 | Yes | 1 |
| `museum_banner_green` | Green Banner | Museum | 1 | 60 | 0 | 4 | No | 0 |
| `museum_globe_small` | Small Globe | Museum | 2 | 100 | 100 | 6 | No | 0 |
| `museum_statue_stone` | Stone Statue | Museum | 3 | 160 | 250 | 9 | No | 0 |
| `museum_glass_case` | Glass Case | Museum | 3 | 220 | 250 | 0 | Yes | 2 |
| `museum_urn_ancient` | Ancient Urn | Museum | 4 | 320 | 500 | 15 | No | 0 |
| `museum_clockwork` | Clockwork Display | Museum | 4 | 400 | 500 | 0 | Yes | 3 |
| `museum_aurium_crystal` | Crystal Aurium | Museum | 5 | 600 | 1000 | 0 | Yes | 4 |

Museum scholarship rules:

- Non-case museum item: scholarship is the fixed value from the catalog.
- Case museum item with no assigned resource: scholarship is `0`.
- Case museum item with an assigned resource:  
  `scholarship = caseTier * resource.rarity * 2`

### Slot layout

Home slots:

| IDs | Count | Coordinates |
| --- | ---: | --- |
| `home_01` through `home_16` | 16 | A 4 x 4 grid at tile rows 27 to 30 and tile columns 27 to 30 |

Museum slots:

| IDs | Count | Coordinates |
| --- | ---: | --- |
| `museum_01` through `museum_14` | 14 | A 4 x 4 grid at tile rows 27 to 30 and tile columns 33 to 36, excluding the top-right and bottom-right corners |

### Reputation unlocks

| Reputation | Home Slots Unlocked | Museum Slots Unlocked | Shop Tier |
| ---: | ---: | ---: | ---: |
| 0 | 6 | 6 | 1 |
| 100 | 9 | 8 | 2 |
| 250 | 12 | 10 | 3 |
| 500 | 14 | 12 | 4 |
| 1000 | 16 | 14 | 5 |

### World generation counts

| Object | Count | Placement |
| --- | ---: | --- |
| Berry nodes | 40 | Mostly forest and fields |
| Ore nodes | 30 | Mostly quarry and a few scattered rocks |
| Fish | 40 | Lake water tiles |

### Season factors

| Season | Berry Regrow Factor | Ore Regrow Factor |
| --- | ---: | ---: |
| Spring | 0.8 | 1.0 |
| Summer | 1.0 | 0.9 |
| Autumn | 1.2 | 1.0 |
| Winter | 1.6 | 1.3 |

### Timing constants

| Action | Duration |
| --- | ---: |
| Berry harvest | 0.8 seconds |
| Ore harvest | 1.2 seconds |
| Fish catch | 2.5 seconds |
| Berry regrow base | 60 seconds |
| Ore regrow base | 180 seconds |
| Fish respawn | 15 seconds |
| Shop refresh | Every day divisible by 3, including day 1 |

### Public signatures

```text
start()
step(dt, n)
setTime(t)
seed(n)
getState()

setMove(x, y)
setActionHold(held)
setPlayerPosition(x, y)

setMoney(n)
addMoney(n)
setReputation(n)
setInventory(resourceId, count)
setStorage(itemId, count)
setStock(itemId, count)

spawnNode(kind, type, x, y, count)
clearNodes()
setNodeCount(id, count)
setNodeTimer(id, seconds)

spawnFish(type, x, y)
clearFish()
setFishPosition(id, x, y)
setFishAlive(id, alive)
setFishRespawn(id, seconds)

sellResource(resourceId, count)
buyItem(itemId)
placeItem(itemId, slotId)
assignExhibit(slotId, resourceId)

createRequest(resourceId, count, rewardMoney, rewardRep)
setRequestCount(requestId, count)
refreshShop(day)
setSeason(index)
setSelected(itemId, slotId)
```

All functions return plain data only.

---

# 3. VISUAL SPEC

Hollow Harvest should look like a cozy top-down valley at the edge of a small lake, with a berry forest, a rocky quarry, a central plaza with a shopkeeper, a small home, and a little museum building. The art should feel handcrafted and readable: simple shapes, warm colors, soft outlines, and clear resource colors. The world should feel explorable but compact enough that the player always knows where the next resource type is.

## 3.1 Lighting

Lighting is applied as a full-screen tint plus localized light sources.

| Time or state | Effect |
| --- | --- |
| Day | No global tint |
| Dusk | Warm orange tint, intensity rises from 10% to 25% over the last 15 seconds before night |
| Night | Blue tint, 35% intensity |
| Player at night | Warm circular light around the player, radius 4 tiles |
| Home windows | Warm light, radius 3 tiles, visible when at least one home slot is placed |
| Museum interior | Soft lavender light, radius 3 tiles, visible when at least one museum slot is placed |
| Spring | No seasonal tint |
| Summer | Slightly brighter grass, +10% saturation |
| Autumn | Faint orange overlay, 8% |
| Winter | Pale blue overlay, 10%, water becomes slightly icy |

Water has animated ripple lines. Fish leave a small wake. Berry bushes glow slightly when full. Ore nodes sparkle when count is greater than 0.

## 3.2 Tile visuals

| Tile type | Visual |
| --- | --- |
| Grass | Soft green base with 4 subtle noise variants |
| Water | Blue base with moving ripple alpha |
| Road | Sandy cobble path with rounded stones |
| Home floor | Warm wood floor |
| Museum floor | Pale stone floor |
| Rock | Gray-brown rock patch, mainly around quarry edges |

### Zone layout

| Zone | Tile rectangle |
| --- | --- |
| Lake | x 8 to 23, y 36 to 50 |
| Berry forest | x 6 to 22, y 6 to 22 |
| Quarry | x 42 to 58, y 6 to 22 |
| Fields | x 40 to 58, y 36 to 55 |
| Plaza | x 29 to 35, y 29 to 35 |
| Home | x 27 to 30, y 27 to 30 |
| Museum | x 33 to 36, y 27 to 30 |

## 3.3 Entity visuals

| Entity | Visual |
| --- | --- |
| Player | Rounded body, small backpack, direction indicator, walking bob |
| Berry bush | Round bush with 0 to 3 visible berries |
| Berry colors | Red, blue, golden, frost cyan |
| Ore node | Rock polygon with colored crystal shards |
| Ore colors | Copper orange, iron gray, silver white, crystal light blue |
| Fish | Small ellipse with tail wiggle |
| Fish colors | Minnow gray-green, perch orange, pike teal, trout gold, lumifin glowing cyan |
| Shopkeeper | Stall with red-and-white awning and a small NPC figure |
| Home furniture | Top-down furniture shapes on wood floor |
| Museum furniture | Top-down cases, banners, statues, and displays on stone floor |

## 3.4 Particles

| Event | Particle |
| --- | --- |
| Berry harvest | Small colored pop |
| Ore harvest | Small sparkle |
| Fish catch | Splash ring |
| Sell | Coin flash at shopkeeper |
| Buy | Chime sparkle |
| Placement | Soft dust ring |
| Museum assign | Small light pulse on exhibit |

---

# 4. GAMEPLAY SPEC

The most important part of playing is the gather-sell-decorate loop. The player should quickly learn the spatial rhythm: forest for berries, quarry for ore, lake for fish, plaza for selling, home and museum for spending. The game should feel satisfying when a rare fish is caught, when a request completes, and when the museum slowly fills with valuable things.

There is no combat. The challenge is scarcity, timing, travel, shop stock, reputation unlocks, and completing the collection.

## 4.1 Player Controller

### Movement

- Input: 8-way movement from keyboard.
- Movement is immediate, no inertia.
- Movement vector is normalized.
- Diagonal movement has the same speed as axis movement.
- Player cannot enter water, node tiles, or out-of-bounds tiles.
- Player position is in tile units.

### Camera

- Camera follows the player.
- Camera is clamped to world bounds.
- Viewport is 40 x 22.5 tiles.
- The player is centered when not near a world edge.

### Action

- One action input is held to work.
- If the player is near a berry node with count greater than 0, the action harvests a berry.
- If the player is near an ore node with count greater than 0, the action mines ore.
- If the player is on a shore tile and fish are within fishing radius, the action fishes.
- Action progress resets when released, when the target becomes invalid, or when the player moves out of range.
- If inventory is full for the target resource, action progress does not accumulate.

## 4.2 Inventory and Storage

### Inventory

- Holds collected resources.
- Max 20 per resource.
- Selling reduces inventory.
- Museum exhibit assignment consumes one resource.

### Storage

- Holds purchased furniture.
- Max 5 per item.
- Buying increases storage.
- Placement decreases storage.
- Placement requires an unlocked empty slot of the correct category.

## 4.3 Berry Nodes

Berry node fields:

| Field | Value |
| --- | --- |
| Kind | `berry` |
| Max count | 3 |
| Start count | 2 or 3 |
| Harvest duration | 0.8 seconds |
| Yield per harvest | 1 |
| Regrow base | 60 seconds |
| Regrow count | 2 |

Rules:

- A berry node can be harvested only if count is greater than 0 and inventory is not full.
- Each completed harvest reduces count by 1 and adds 1 resource.
- First collection of a resource marks it discovered.
- When count becomes 0, set `regrowTimer` to `60 * seasonBerryFactor`.
- When `regrowTimer` reaches 0, set count to 2.
- Berry nodes block their tile.

## 4.4 Ore Nodes

Ore node fields:

| Field | Value |
| --- | --- |
| Kind | `ore` |
| Max count | 5 |
| Start count | 3 or 4 |
| Harvest duration | 1.2 seconds |
| Yield per harvest | 1 |
| Regrow base | 180 seconds |
| Regrow count | 3 |

Rules:

- An ore node can be mined only if count is greater than 0 and inventory is not full.
- Each completed harvest reduces count by 1 and adds 1 resource.
- First collection of a resource marks it discovered.
- When count becomes 0, set `regrowTimer` to `180 * seasonOreFactor`.
- When `regrowTimer` reaches 0, set count to 3.
- Ore nodes block their tile.

## 4.5 Fishing

Fish rules:

- Fish exist only in water tiles.
- A player can fish only from a shore tile.
- Fishing requires the action input to be held.
- Fishing takes 2.5 seconds.
- On completion, the nearest alive fish within 2.5 tiles is caught.
- If no fish is in range when the action completes, the attempt fails.
- Caught fish is removed from the world and added to inventory.
- First collection of a fish type marks it discovered.

Fish population:

- Initial fish count: 40.
- Fish type distribution:
  - Minnow 35%
  - Perch 25%
  - Pike 20%
  - Trout 15%
  - Lumifin 5%
- Lumifin spawns only during night. If a Lumifin roll occurs during day, use Perch instead.
- Dead fish respawn after 15 seconds as the same type at a random water tile.
- Fish move slowly and bounce off water bounds.

## 4.6 Shopkeeper and Economy

### Shopkeeper

- Location: tile `(32, 32)`.
- Player must be within 2.0 tiles to sell or buy.
- Shopkeeper opens the shop overlay when the player enters radius.
- Shopkeeper has buy prices for every resource.

### Selling

- Selling reduces inventory.
- Selling increases money by `count * buyPrice`.
- Selling increases reputation by `count * resource.reputation`.
- Selling reduces matching active requests.
- If a request reaches 0, mark it done and add its reward money and reward reputation.

### Buying

- Buying requires:
  - Item in stock
  - Enough money
  - Reputation requirement met
  - Storage count below max
- Buying increases storage.
- Buying reduces money and stock.

### Shop stock

- Stock refreshes on day 1 and every 3 days.
- Stock is regenerated from the catalog.
- An item may appear if its tier reputation requirement is met.
- Each eligible item has a 75% chance to appear.
- If it appears, count is 1 or 2.

### Requests

- 3 requests exist after each shop refresh.
- Each request has:
  - Resource type
  - Count needed
  - Reward money
  - Reward reputation
- Requests complete automatically through selling.
- Request counts should remain modest:
  - Berries: 2 to 4
  - Ores: 1 to 3
  - Fish: 1 to 3

## 4.7 Home and Museum

### Home

- Home slots accept home furniture.
- Placement requires:
  - Item in storage
  - Slot unlocked
  - Slot empty
- Placement decreases storage.
- Placement sets slot item.
- Placement adds item comfort to `homeComfort`.

### Museum

- Museum slots accept museum furniture.
- Placement requires:
  - Item in storage
  - Slot unlocked
  - Slot empty
- Placement decreases storage.
- Placement sets slot item.
- Non-case museum items add their fixed scholarship immediately.
- Case museum items start with 0 scholarship.

### Museum exhibits

- Only museum case items can hold an exhibit.
- Assigning an exhibit requires:
  - Museum slot has a case item
  - Slot has no assigned resource yet
  - Resource is discovered
  - Inventory has at least 1 of that resource
- Assigning consumes 1 resource.
- Assigning sets `exhibitResourceId`.
- Assigning sets slot scholarship to:
  `caseTier * resource.rarity * 2`
- Assigning increases `museumScholarship` by the new scholarship.
- Assigning increases the resource's `displayedCount`.

### Progression

- Reputation changes update slot unlocks immediately.
- New slots become unlocked in slot ID order.
- Higher reputation makes higher-tier items appear at the next shop refresh.
- The long-term goal is to discover all resources, unlock all slots, and fill the museum with valuable exhibits.

---

# 5. CHARACTERS

The characters should be simple, friendly, and readable at small size. The player should feel like a curious valley gatherer, not a warrior. The shopkeeper should feel like a welcoming local. Fish should feel lively but not aggressive. There are no hostile characters.

## 5.1 Animation

| Character | Animation pieces |
| --- | --- |
| Player | Idle, walk cycle 4 frames, action hold pulse, fishing cast |
| Shopkeeper | Idle bob, sell bounce, buy sparkle |
| Berry bush | Berry pop, regrow sprout |
| Ore node | Sparkle, mine crack, regrow crystal growth |
| Fish | Tail wiggle, splash on catch, respawn bubble |
| Museum exhibit | Light pulse on assignment |
| Home furniture | Placement dust, lamp flicker for lamp and fireplace |

---

# 6. AUDIO

All audio is synthesized from oscillators, short noise bursts, and simple envelopes. No external assets.

| Sound name | Recipe | Rule that plays it |
| --- | --- | --- |
| `ui_click` | Square, 880 Hz, 0.05 s, fast decay | Any UI selection or tab change |
| `ui_open` | Triangle, 520 Hz to 660 Hz, 0.08 s | Opening a panel |
| `harvest_berry` | Sine, 660 Hz to 880 Hz, 0.08 s, pop envelope | Berry harvest completes |
| `harvest_ore` | Triangle, 220 Hz plus short noise, 0.12 s | Ore harvest completes |
| `fish_start` | Sine, 300 Hz, 0.15 s, soft attack | Fishing action starts |
| `fish_catch` | Square, 520 Hz plus noise splash, 0.10 s | Fish caught |
| `fish_fail` | Sine, 220 Hz descending to 160 Hz, 0.12 s | Fishing attempt finds no fish |
| `sell_coin` | Sine, 1200 Hz, 0.05 s, triple rapid repeat | Selling resources |
| `buy_chime` | Triangle, 660 Hz and 990 Hz, 0.20 s | Buying an item |
| `place_thud` | Sine, 120 Hz, 0.12 s, quick decay | Placing furniture |
| `exhibit_pulse` | Triangle, 440 Hz to 880 Hz, 0.18 s | Assigning museum exhibit |
| `request_complete` | Triangle arpeggio 523 Hz, 659 Hz, 784 Hz, 0.30 s | Request completes |
| `error_buzz` | Square, 110 Hz, 0.15 s, flat envelope | Failed action, buy, sell, or placement |
| `season_chime` | Triangle, 520 Hz, 0.40 s, soft decay | Season changes |

---

# 7. UX

All UI is a browser presentation layer outside the main game view. The game view only shows the world, entities, particles, and lighting.

## 7.1 Title screen

The title screen shows:

- Game name: Hollow Harvest
- Short description
- Start button
- Seed display
- Optional seed input for debugging

The Start button moves the game to play phase.

## 7.2 HUD

Always visible during play:

| HUD piece | Contents |
| --- | --- |
| Top-left | Money, reputation, day, season, time of day |
| Top-right | Buttons: Inventory, Collection, Museum Status |
| Bottom-center | Context prompt |
| Bottom-right | Current action progress, if any |

Context prompts:

- Near berry node: “Hold Action to harvest berry”
- Near ore node: “Hold Action to mine ore”
- On shore with fish nearby: “Hold Action to fish”
- Near shopkeeper: “Open Shop”
- Placing item: “Select an unlocked slot”

## 7.3 Shop panel

The shop panel has three tabs:

| Tab | Contents |
| --- | --- |
| Sell | List of player resources, counts, sell price, sell button |
| Buy | List of stocked items, price, requirement, buy button |
| Requests | Active requests, progress, rewards, completion state |

Shop panel rules:

- Sell buttons are disabled if count is 0.
- Buy buttons are disabled if money, stock, reputation, or storage limits prevent purchase.
- Request rows show completed requests with a completed badge.

## 7.4 Inventory and storage panel

Shows:

- Resource inventory counts
- Storage item counts
- Selected item highlight
- Placement hint

## 7.5 Placement mode

When a storage item is selected:

- Valid slots highlight.
- Invalid slots do not highlight.
- Selecting a valid slot places the item.
- Selecting an invalid slot shows an error message.

## 7.6 Collection panel

Shows all 13 resource types:

| Column | Meaning |
| --- | --- |
| Name | Resource name |
| Discovered | Check mark or hidden silhouette |
| Collected | Total collected |
| Displayed | Total displayed in museum |

## 7.7 Museum status panel

Shows:

- Home comfort
- Museum scholarship
- Unlocked slots
- Placed slots
- Discovered resources
- Total displayed exhibits

---

# 8. DEBUG API

The game installs `window.__game` with plain functions. Every call is synchronous and returns only plain data. With the same seed and same call sequence, the same state is produced.

| Call | What it does | Return |
| --- | --- | --- |
| `start()` | Enter play from title | `{ phase }` |
| `step(dt, n)` | Advance `n` ticks of `dt` seconds, then draw once | `{ time, day, seasonIndex, night, money, reputation }` |
| `setTime(t)` | Advance simulation to `t` seconds without drawing | `{ time, day, seasonIndex, night }` |
| `seed(n)` | Reseed and rebuild generated world, return to title | `{ seed }` |
| `getState()` | Return full state as plain data | Full state object |
| `setMove(x, y)` | Set persistent movement direction | `{ x, y }` |
| `setActionHold(held)` | Set action input held or released | `{ held }` |
| `setPlayerPosition(x, y)` | Move player to tile position | `{ x, y }` |
| `setMoney(n)` | Set player money | `{ money }` |
| `addMoney(n)` | Add to player money | `{ money }` |
| `setReputation(n)` | Set reputation and update slot unlocks | `{ reputation, homeUnlocked, museumUnlocked }` |
| `setInventory(resourceId, count)` | Set resource count directly | `{ resourceId, count }` |
| `setStorage(itemId, count)` | Set storage count directly | `{ itemId, count }` |
| `setStock(itemId, count)` | Set shop stock count directly | `{ itemId, count }` |
| `spawnNode(kind, type, x, y, count)` | Add a node at a tile | `{ id }` |
| `clearNodes()` | Remove all nodes | `{ nodes: 0 }` |
| `setNodeCount(id, count)` | Set node count | `{ id, count }` |
| `setNodeTimer(id, seconds)` | Set node regrow timer | `{ id, regrowTimer }` |
| `spawnFish(type, x, y)` | Add a fish, using given position if provided | `{ id }` |
| `clearFish()` | Remove all fish | `{ fish: 0 }` |
| `setFishPosition(id, x, y)` | Move fish | `{ id, x, y }` |
| `setFishAlive(id, alive)` | Set fish alive state | `{ id, alive }` |
| `setFishRespawn(id, seconds)` | Set fish respawn timer | `{ id, respawnTimer }` |
| `sellResource(resourceId, count)` | Sell resources using shop rules | `{ sold, money, reputation, completedRequests }` |
| `buyItem(itemId)` | Buy item using shop rules | `{ bought, money, stock }` |
| `placeItem(itemId, slotId)` | Place item using placement rules | `{ placed, slot }` |
| `assignExhibit(slotId, resourceId)` | Assign museum exhibit using exhibit rules | `{ success, slot }` |
| `createRequest(resourceId, count, rewardMoney, rewardRep)` | Add a request | `{ id, requestsLength }` |
| `setRequestCount(requestId, count)` | Set request remaining count | `{ id, countNeeded, done }` |
| `refreshShop(day)` | Force shop refresh for a day | `{ lastRefreshDay, stockKeys, requestsLength }` |
| `setSeason(index)` | Set season index | `{ seasonIndex }` |
| `setSelected(itemId, slotId)` | Set selected item and slot | `{ selectedItemId, selectedSlotId }` |

---

# 9. TESTS

All checks use only calls listed in Section 8.

1. After `seed(7)`, `start()`, `getState()`:
   - `phase === "play"`
   - `seed === 7`
   - `money === 50`
   - `reputation === 0`
   - `day === 1`
   - `seasonIndex === 0`
   - `night === false`
   - `world.width === 64`
   - `world.height === 64`
   - `player.x === 32`
   - `player.y === 35`
   - `world.nodes.length === 70`
   - `world.fish.length === 40`
   - `homeUnlocked === 6`
   - `museumUnlocked === 6`
   - `homeComfort === 0`
   - `museumScholarship === 0`
   - `shop.requests.length === 3`

2. After `seed(1)`, `start()`, `clearNodes()`, `setPlayerPosition(32, 35)`, `setMove(1, 0)`, `step(1/60, 60)`, `getState()`:
   - `player.x === 36`
   - `player.y === 35`

3. After `seed(2)`, `start()`, `clearNodes()`, `clearFish()`, `spawnNode("berry", "red_berry", 33, 35, 3)`, `setPlayerPosition(32, 35)`, `setActionHold(true)`, `step(1/60, 48)`, `setActionHold(false)`, `getState()`:
   - `player.inventory.red_berry === 1`
   - node at `(33, 35)` has `count === 2`
   - `collection.red_berry.discovered === true`
   - `collection.red_berry.collectedTotal === 1`

4. After `seed(2)`, `start()`, `clearNodes()`, `clearFish()`, `spawnNode("ore", "copper", 30, 35, 5)`, `setPlayerPosition(31, 35)`, `setActionHold(true)`, `step(1/60, 72)`, `setActionHold(false)`, `getState()`:
   - `player.inventory.copper === 1`
   - node at `(30, 35)` has `count === 4`
   - `collection.copper.discovered === true`
   - `collection.copper.collectedTotal === 1`

5. After `seed(2)`, `start()`, `clearNodes()`, `clearFish()`, `spawnFish("minnow", 23, 37)`, `setPlayerPosition(24, 37)`, `setActionHold(true)`, `step(1/60, 150)`, `setActionHold(false)`, `getState()`:
   - `player.inventory.minnow === 1`
   - the spawned fish has `alive === false`
   - `collection.minnow.discovered === true`
   - `collection.minnow.collectedTotal === 1`

6. After `seed(2)`, `start()`, `setPlayerPosition(32, 33)`, `setInventory("copper", 5)`, `sellResource("copper", 5)`, `getState()`:
   - `money === 80`
   - `reputation === 10`
   - `player.inventory.copper === 0`

7. After `seed(2)`, `start()`, `createRequest("minnow", 2, 100, 40)`, `setInventory("minnow", 2)`, `setPlayerPosition(32, 33)`, `sellResource("minnow", 2)`, `getState()`:
   - the created request has `done === true`
   - `money === 160`
   - `reputation === 44`
   - `player.inventory.minnow === 0`

8. After `seed(2)`, `start()`, `setStock("home_plant_small", 1)`, `setMoney(100)`, `setPlayerPosition(32, 33)`, `buyItem("home_plant_small")`, `getState()`:
   - `money === 70`
   - `player.storage.home_plant_small === 1`
   - `shop.stock.home_plant_small === 0`

9. After `seed(2)`, `start()`, `setStorage("home_plant_small", 1)`, `placeItem("home_plant_small", "home_01")`, `getState()`:
   - `player.storage.home_plant_small === 0`
   - home slot `home_01` has `item === "home_plant_small"`
   - `homeComfort === 2`

10. After `seed(2)`, `start()`, `setStorage("museum_plinth_basic", 1)`, `placeItem("museum_plinth_basic", "museum_01")`, `setInventory("silver", 1)`, `assignExhibit("museum_01", "silver")`, `getState()`:
    - museum slot `museum_01` has `item === "museum_plinth_basic"`
    - museum slot `museum_01` has `exhibitResourceId === "silver"`
    - museum slot `museum_01` has `scholarship === 6`
    - `museumScholarship === 6`
    - `player.inventory.silver === 0`
    - `collection.silver.displayedCount === 1`

11. After `seed(2)`, `start()`, `setReputation(250)`, `getState()`:
    - `reputation === 250`
    - `homeUnlocked === 12`
    - `museumUnlocked === 10`

12. After `seed(7)`, `start()`, `setTime(300)`, `getState()`:
    - `time === 300`
    - `day === 6`
    - `seasonIndex === 1`
    - `shop.lastRefreshDay === 4`

13. After `seed(2)`, `start()`, `clearFish()`, `spawnFish("perch", 20, 40)`, `setFishAlive(id, false)`, `setFishRespawn(id, 15)`, `step(1/60, 900)`, `getState()`:
    - the fish with that ID has `alive === true`

14. After `seed(2)`, `start()`, `clearNodes()`, `spawnNode("berry", "blue_berry", 20, 20, 0)`, `setNodeTimer(id, 60)`, `step(1/60, 3600)`, `getState()`:
    - the node with that ID has `count === 2`

15. After `seed(2)`, `start()`, `clearNodes()`, `setInventory("red_berry", 20)`, `spawnNode("berry", "red_berry", 33, 35, 3)`, `setPlayerPosition(32, 35)`, `setActionHold(true)`, `step(1/60, 48)`, `setActionHold(false)`, `getState()`:
    - `player.inventory.red_berry === 20`
    - node at `(33, 35)` has `count === 3`
    - `collection.red_berry.collectedTotal === 0`

## SCREENSHOTS

| Named screen or state | What a person must see |
| --- | --- |
| Title screen | Game name, start button, seed value, and a short collector-game description |
| World after start | Player near the plaza, shopkeeper nearby, berry forest, quarry, lake, home, and museum visible or clearly nearby |
| Berry harvest | Player next to a berry bush, action prompt visible, bush berry count decreases, inventory count increases |
| Ore mining | Player next to an ore node, action prompt visible, ore count decreases, inventory count increases |
| Fishing | Player on lake shore, fish visible in water, action prompt visible, fish disappears and inventory increases after catch |
| Shop open | Shop panel open with Sell, Buy, and Requests tabs, resource counts visible, buy items visible |
| Home placement | A home furniture item placed on a home slot, comfort value increased |
| Museum exhibit | A plinth placed in museum, a resource assigned to it, scholarship value increased |
| Reputation unlock | Reputation at 250, more home and museum slots highlighted or listed as unlocked |

---

# 10. BUILD ORDER

1. Build the state object, seed handling, debug hook, title-to-play flow, and step loop.
2. Build world generation for terrain, water, shore, plaza, home, museum, nodes, and fish.
3. Build presentation for tiles, entities, player, shopkeeper, lighting, and basic animation.
4. Build player movement, camera, collision, and action input.
5. Build berry and ore nodes with harvesting, regrowth, and collection.
6. Build fish movement, fishing, catches, and respawn.
7. Build inventory, storage, selling, buying, and shopkeeper interaction.
8. Build home and museum slots, placement, exhibits, comfort, and scholarship.
9. Build reputation, slot unlocks, shop refresh, requests, and season effects.
10. Build full overlay UI: HUD, shop, inventory, placement, collection, and museum status.
11. Add synthesized audio.
12. Add particles, lighting polish, and performance tuning.
13. Run all debug checks and screenshot checks.

---

# 11. DEFINITION OF DONE

## Core loop

- Title starts the game.
- Player can move around the open world.
- Player can harvest berries.
- Player can mine ore.
- Player can fish.
- Inventory increases on collection.
- Collection log updates on first discovery.
- Player can sell resources.
- Player can buy furniture.
- Player can place furniture in home and museum.

## World

- World is 64 x 64 tiles.
- World contains forest, quarry, lake, plaza, home, and museum.
- Water is non-walkable.
- Shore tiles are usable for fishing.
- Berry nodes are placed in berry zones.
- Ore nodes are placed in ore zones.
- Fish spawn in water.
- World regenerates deterministically from seed.

## Player

- Player moves 8-way.
- Player collides with water and nodes.
- Player camera follows and clamps.
- Action input works for harvest and fishing.
- Action progress resets correctly.
- Player cannot collect above inventory max.

## Resources

- Berry nodes harvest and regrow.
- Ore nodes harvest and regrow.
- Fish move, catch, and respawn.
- Season affects regrow speed.
- Night affects Lumifin spawning.
- All 13 resource types are collectible.

## Economy

- Shopkeeper buys every resource type.
- Selling increases money and reputation.
- Buying decreases money and stock.
- Storage limits work.
- Shop stock refreshes on schedule.
- Requests exist and complete through selling.
- Request rewards are added.

## Collection and museum

- Home furniture placement works.
- Museum furniture placement works.
- Museum cases can accept exhibits.
- Exhibit assignment consumes a resource.
- Scholarship calculates correctly.
- Home comfort calculates correctly.
- Slot unlocks update with reputation.

## UX

- Title screen works.
- HUD shows money, reputation, day, season, and prompt.
- Shop panel works.
- Inventory and storage panel works.
- Placement mode works.
- Collection panel works.
- Museum status panel works.

## Audio

- Audio cues play for UI, harvest, fish, sell, buy, placement, exhibit, request, error, and season.

## Debug and tests

- Debug API exposes all listed calls.
- All debug calls return plain data.
- Same seed and same calls produce same state.
- All numbered tests pass.
- All screenshot states are visibly correct.

## Performance and polish

- Game runs smoothly at the target frame rate.
- No invisible UI elements are drawn in the game view.
- Lighting matches day, night, and season.
- Particles do not obscure gameplay.
- World is readable at the intended tile size.

---

# A. SANITY

| Check | Result |
| --- | --- |
| Every field a rule reads or writes is on a record | Closes. Player, node, fish, slot, request, shop, and collection records include all fields used by movement, harvest, fishing, selling, buying, placement, exhibits, requests, and progression. |
| Every place, thing, or kind a rule names is placed by a generator or listed in a roster | Closes. Resource types are in the catalog. Node kinds are berry and ore. Fish types are in the catalog. Home and museum slots are generated. Shopkeeper, lake, forest, quarry, home, museum, and plaza are placed by world generation. |
| For every consumable, total generator output can satisfy rule demand along the core loop | Closes. Initial and regrowing resources: 40 berry nodes, 30 ore nodes, 40 fish. Museum can consume at most 14 resources for exhibits. Requests are small and refresh every 3 days. Inventory max is 20 per resource. Generators provide enough over time, and player action speed limits actual throughput. |
| Every timing pair closes | Closes. Berry harvest is 0.8 seconds versus 60-second regrow. Ore harvest is 1.2 seconds versus 180-second regrow. Fishing is 2.5 seconds versus 15-second respawn. Shop refresh is 180 seconds apart. Travel across the 64-tile world is at most 16 seconds at 4 tiles/second. |
| Every call section 9 makes is in section 8 | Closes. All test calls are listed in the debug table. |
| Visual state fields match lighting and presentation reads | Closes. `night`, `seasonIndex`, placed home slots, placed museum slots, node counts, fish positions, and player position are all in state and used by lighting and presentation. |
| Debug determinism constraints are explicit | Closes. One random source, fixed tick, seeded world, plain-data returns, and no real-time dependency are specified. |