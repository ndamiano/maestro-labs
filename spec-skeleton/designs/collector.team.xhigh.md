# 0. SCOPE

This document is the single build spec. It supersedes `gameplay.md`, `visual.md`, and `engineering.md`. Where this document names a number, name, or rule, that value wins. Nothing from the three source documents is dropped silently: it is carried, ruled on in `0.2`, or listed under a tier in `0.3`.

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| An open world collector game | World Generation, Movement, Foraging, Mining, Fishing, Inventory; section 4 |
| The player walks around | Movement; section 4 |
| Collecting resources | Inventory, Foraging, Mining, Fishing; section 4 |
| Harvest berries | Foraging, Resource Roster, berry nodes; section 4 |
| Mine ores | Mining, Resource Roster, ore nodes; section 4 |
| Fish fish | Fishing, Resource Roster, fishing spots; section 4 |
| Sell them to a shop keeper for each type | Shopkeeper Roster, Selling; section 4 |
| Buy furniture to decorate their home | Buying, Home, Furniture Roster; section 4 |
| Buy furniture to decorate a small museum type building | Buying, Museum, Furniture Roster; section 4 |
| Added: day/time economy, energy limits, weather, tools, progression, museum exhibits, daily buyer caps | Time, Weather, Energy, Buying, Home, Museum; section 4, marked added in this table |
| Added: readable collector feedback and audio | section 3, section 5, section 6, section 7 |
| Added: debug API and deterministic tests | section 8, section 9 |

## 0.2 Decisions

| Topic | What gameplay said | What visual said | What engineering said | Ruling and one clause why |
| --- | --- | --- | --- | --- |
| Render dimension | 2D top-down | 3D angled overhead | 2D top-down canvas | Ruling: 2D top-down rendered with Canvas 2D. Clause: two sources agree on 2D, and the browser build stays inside the fixed-step canvas contract. |
| Camera | Fixed 90-degree bird's-eye, zoom 1.0, player centered, no rotation | 360-degree orbit, 54-degree tilt, zoom 18 to 55 units | Camera equals player, 960 by 540 viewport, `cam.zoom = 1` | Ruling: fixed top-down camera, player-centered, no orbit, no player-controlled zoom; render scale is 8 screen pixels per tile. Clause: gameplay and engineering agree on player-centered 2D, and visual camera is staged under T3. |
| World size | 120 by 120 tiles | 300 by 300 game units | 4000 by 4000 units, 32-unit grid | Ruling: world is 120 by 120 logic tiles. Clause: gameplay's generator, rosters, reach, and shop layout depend on 120 tiles. |
| Logic unit | Tiles | Game units `u` | Pixels/units, 32-unit tile | Ruling: one logic unit is one tile. Clause: all gameplay distances, reach, and timers are tile-based. |
| Origin and axes | Tile coordinates 0 to 119 | World from -150 to +150 | Origin center of 4000 square | Ruling: X right, Y down, origin at tile 0,0 top-left; tile center `(gx, gy)` is integer. Clause: gameplay coordinates are simpler and already bound the player, shops, lakes, and buildings. |
| Node counts | 40 berry, 30 ore, 12 fishing spots | 36 berry bushes, 24 ore nodes, 3 docks | Placeholder node counts | Ruling: gameplay counts win: 40 berry nodes, 30 ore nodes, 12 fishing spots. Clause: buyer caps, museum exhibits, and progression are balanced to gameplay counts. |
| Water layout | Two lakes: Lake A center 24,32 radius 8; Lake B center 92,84 radius 10; 12 fishing spots | One lake region with 3 docks | One pond tile | Ruling: gameplay two-lake layout wins. Clause: fish table uses lakeType 1 and 2, which requires two distinct waters. |
| Shopkeepers | Four shopkeepers: berry, ore, fish, general | One shop stall | One shopkeeper entity | Ruling: four shopkeepers win. Clause: the request requires a shop keeper for each type. |
| Furniture catalog | 12 furniture definitions | 8 generic furniture shapes | Four types f1 to f4 | Ruling: gameplay's 12 furniture definitions win. Clause: Home and Museum rules need allowed, comfort, museumPoints, refundCoins, and maxPerRoom. |
| Resource catalog | 10 resources with prices, yields, exhibit values | Berry, copper, tin, gold visuals | Generic berries, ore, fish | Ruling: gameplay Resource Roster wins. Clause: selling, museum exhibits, and fishing tables depend on those ids. |
| Ore visual names | Copper, Iron, Gemstone | Copper, tin, gold | No resource names | Ruling: gameplay names win; visual copper maps to Copper, visual tin maps to Iron, visual gold maps to Gemstone. Clause: keeps one resource id set while carrying visual colours. |
| Health and damage | No opponent, no health, energy only | Health bar, damage, death, low health | No health | Ruling: no health, no damage, no death. Clause: this is a non-combat collector game; energy is the only drain. |
| Energy UI | Energy record and regen | Health bar recipe | None | Ruling: visual Health bar becomes the Energy bar. Clause: preserves visual feedback shape while matching gameplay state. |
| Fishing interaction | Use/Space at fishing spot, timing bar | Bobber idle and bite | F key progress timer | Ruling: gameplay fishing state machine wins; visual shows bobber and timing bar. Clause: gameplay has rod tiers, sweet zones, and fish tables. |
| Shop transactions | Type-specific buyers, daily caps, general shop stock, no transaction cooldown | Shop panel | Sell/buy with stock and cooldown placeholder | Ruling: gameplay shop rules win; shop transaction cooldown is 0.0. Clause: daily caps and dawn restock provide economy pacing; no doc gave a shop cooldown number. |
| Harvest and mine timing | Foraging cooldown 0.4, mining cooldown 0.45 | Feedback times | `HARVEST_TIME` placeholder | Ruling: Foraging action is immediate with 0.4 cooldown; Mining strike is immediate with 0.45 cooldown. Clause: gameplay gives the numbers. |
| Fishing timing | Cast 0.8, reel 0.5, fish cooldown 0.5 | Bobber motion | `FISH_TIME` placeholder | Ruling: cast 0.8, reel 0.5, post-catch toolCooldown 0.5. Clause: gameplay gives the numbers. |
| Player speed | 4.0 tiles/second | No speed | Test implied 2 units/second | Ruling: 4.0 tiles/second. Clause: gameplay's feel section explicitly requires crossing a 12-tile gap in 3 seconds. |
| Movement acceleration | 10.0 tiles/second squared, deceleration 12.0 | None | None | Ruling: carry gameplay acceleration and deceleration. Clause: feel rule. |
| Interaction reach | 2.5 tiles | None | 64 units | Ruling: 2.5 tiles. Clause: gameplay targeting, movement, and UI prompts use 2.5. |
| Initial coins | 20 | None | 10 | Ruling: 20. Clause: early-game progression text expects enough money to approach day-2 purchases. |
| Default seed | World seed start 0 | None | seed 12345 for debug/tests | Ruling: new-game default seed is 0; debug/test default seed is 12345. Clause: preserves gameplay start while keeping engineering's deterministic test seed. |
| Player start | 58,58 | Cottage door at 80,72 | -224,-32 | Ruling: 58,58. Clause: gameplay world generation and bed position use that tile. |
| Building interiors | Home 4 by 14, museum 8 by 6, market 4 by 6; room tiles interior | Cottage 12 by 12, museum 16 by 10, shop 8 by 8 | Home and museum rects in 4000 world | Ruling: gameplay building footprints and room/case layout win. Clause: home rooms, museum cases, and shop positions are gameplay records. |
| Furniture placement | Room slots and museum decor slots | Free floor placement ghosts | Furniture tile occupancy 48 units | Ruling: slot-based placement: HomeRoom slots and Museum.decorSlots. Clause: gameplay Home/Museum rules define allowed, maxPerRoom, comfort, and museumPoints. |
| Visual free-floor ghosts | Slot-based rules | Valid/invalid free-floor ghosts | Tile occupancy | Ruling: ghosts appear over the selected slot. Clause: keeps visual feedback without changing slot rules. |
| Museum model | 12 cases, 6 decor slots, curation, settlement, grand opening | Display cases, paintings, warm interior | None | Ruling: gameplay Museum wins. Clause: request requires a museum building and museum-type progression. |
| Time system | 300-second day, dawn 0.10, night from 0.75, settlement 0.95 | Day/night lighting | None | Ruling: gameplay time system wins; visual lighting follows it. Clause: shop caps, weather, fish, and settlement depend on it. |
| Weather | Sunny, rain, snow with gameplay modifiers | Rain state visual | None | Ruling: gameplay weather modifiers win; visual rain is T1 feedback, extra post polish is T2. Clause: weather changes yield, fishing, and regrow. |
| Audio | None | None | None | Ruling: added T1 Web Audio API generated sounds. Clause: section 6 requires generated audio and every gameplay/visual event needs a rule. |
| Persistence | Title has Continue | None | None | Ruling: Continue uses localStorage only; zero network. Clause: carries gameplay title without external storage. |
| Performance budgets | None | None | Tick 2 ms, draw calls 3000, heap 5 MB, file 200 KB, state 8 KB | Ruling: keep tick and draw-call budgets; `getState` excludes the full tile matrix to satisfy 8 KB; file and heap budgets remain T1. Clause: engineering gave numbers; snapshot shape is ruled to fit the merged 120 by 120 world. |
| Entity caps | 70 nodes, 12 furniture bag, 20 inventory slots | Visual max counts | 200 nodes, 24 furniture | Ruling: gameplay caps win for logic; visual max counts are render source values. Clause: economy is balanced to gameplay counts. |
| Map overlay | None | None | M key map | Ruling: M toggles a render-only map overlay in T2. Clause: carries engineering control without mutating state. |

## 0.3 Tiers

T1 is the game that must ship.

T1 systems: World Generation, Time, Weather, Movement, Targeting, Energy, Foraging, Mining, Fishing, Selling, Buying, Inventory, Home, Museum, Render, Audio, UX, Debug API, Tests.

T2 items, in add order, each independent:

1. Decorative terrain props: berry trees, grove rocks, mine rocks, stumps, reeds, lake rocks, meadow trees, fence segments, path ribbons.
2. Weather particles: rain streaks, puddle decals, wet ground darkening, snow visual state.
3. Post effects: vignette, grain, pickup flash, invalid placement shake, door light spill.
4. Map overlay and M key.
5. Door open visual state and light spill.
6. Full particle feedback: gather sparkle, ore chips, fish splash, coin arcs, pickup pops.
7. Furniture visual variants beyond the minimum sprite.
8. localStorage Continue polish and autosave indicators.

T3 items, in add order, each independent:

1. 3D presentation upgrade: 360-degree orbit, 54-degree tilt, zoom 18 to 55 units.
2. 3D mesh shapes and depth fog.
3. 3D lighting and shadows.
4. Visual-only combat animations: player hurt, player death, shopkeeper hurt, shopkeeper death.
5. Visual-only low-health vignette if a future health system is added.

T4 items, in add order, each independent:

1. Source visual retheme using the original 300 by 300 unit region plan.
2. Extra museum exhibit types beyond the Resource Roster.
3. Extra weather audio variants.
4. Additional decorative shop items and counter jars.

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- Logic unit: 1 tile.
- World size: 120 by 120 logic tiles.
- Axes: X points right, Y points down. Up on screen is negative Y. There is no Z axis in logic.
- Tile convention: tile `(gx, gy)` has center `(gx, gy)` and covers `(gx - 0.5, gy - 0.5)` to `(gx + 0.5, gy + 0.5)`.
- World bounds: `(-0.5, -0.5)` to `(119.5, 119.5)`.
- Render unit: screen pixels.
- Canvas: 960 by 540 pixels.
- Render scale: 8 screen pixels per logic tile.
- Camera: center equals `player.x, player.y` every rendered frame. Screen position formula:  
  `screen = (world - player) * 8 + (480, 270)`.
- Fixed step: `dt = 1/60` second. Logic runs only on fixed ticks.
- Real-time loop: `requestAnimationFrame` accumulates elapsed real time, runs `floor(accumulator / dt)` ticks, and keeps the remainder.
- Spiral-of-death rule: a single frame runs at most 3 catch-up ticks. Excess time is dropped, never simulated.
- Paused state: `ctx.paused = true` increments `tick` but skips all update systems. `elapsed` does not advance while paused.
- Rendering: exactly once per animation frame, after all catch-up ticks. Rendering reads committed state and may cull, but it may not mutate gameplay state.

## 1.2 Important conventions

- One random source: `RNG`, mulberry32, 32-bit state, exposed as `ctx.rngState`.
- `RNG.nextInt(lo, hi)` returns an integer `n` where `lo <= n < hi`.
- `RNG.pick(arr)` returns one array element.
- `RNG.range(lo, hi)` returns a float `n` where `lo <= n < hi`.
- No code may use `Math.random()` or `Date.now()` for game state.
- World generation consumes RNG first, then gameplay consumes RNG.
- Update order per tick, after input is consumed:  
  `UPDATE_ORDER = ["time", "movement", "targeting", "energy", "forage", "mine", "fish", "inventory", "home", "museum", "shop"]`.
- Screen behaviour: when `ui.screen` is not `world`, player movement input is ignored; time, energy, regrowth, weather, and settlement still run unless `ctx.paused` is true.
- If a shop closes by time-of-day while `ui.screen` is `shop`, the screen returns to `world`.
- Performance budgets:
  - One update tick must be 2 milliseconds or less in the test harness.
  - Render draw calls must be 3000 or fewer per frame.
  - Total JS heap must be 5 MB or fewer.
  - The whole game must be one local directory, 200 KB or fewer total file size, and issue zero fetch or XHR requests.
  - `getState()` JSON, excluding `world.tiles`, must be 8 KB or fewer.
- Persistence: localStorage only. No network.

Controls table:

| Input | Action | Notes |
| --- | --- | --- |
| W or ArrowUp | Move north, vector `(0, -1)` | |
| S or ArrowDown | Move south, vector `(0, 1)` | |
| A or ArrowLeft | Move west, vector `(-1, 0)` | |
| D or ArrowRight | Move east, vector `(1, 0)` | |
| E or Space | Use focused target | Harvest, mine, fish, shop, bed, museum case |
| 1 | Select hands | If owned |
| 2 | Select best owned pickaxe | Highest tier |
| 3 | Select best owned rod | Highest tier |
| I | Open inventory | Touch Inventory same |
| H | Open Home/Museum | Also E on active museum case |
| Escape or P | Pause or close screen | Screen-dependent |
| M | Toggle map overlay | T2, render-only |
| Touch left joystick | Move | Same vector as keyboard |
| Touch Use | Use | Same as E or Space |
| Touch Tool 1 / 2 / 3 | Select tool | Same as 1 / 2 / 3 |
| Touch Shop | Open nearest open shopkeeper if within 2.5 tiles | |
| Touch Home | Open Home/Museum | |
| Touch Inventory | Open Inventory | |
| Touch Pause | Open Pause | |

# 2. CONTRACTS

## 2.1 Module layout

| Module | Responsibility |
| --- | --- |
| `RNG` | Single seeded random source |
| `Input` | Raw keys and touch into one input record |
| `Time` | Day clock, dawn, settlement trigger, shop open state, sleep |
| `Weather` | Weather roll and modifiers |
| `Player` | Movement, facing, tool selection, focused target resolution |
| `World` | World generation, tile storage, geometry, verifier |
| `Forage` | Berry harvest state |
| `Mine` | Ore strike state |
| `Fish` | Fishing state machine |
| `Inventory` | Item slots, capacity, add/remove |
| `Shop` | Sell, buy tools, buy furniture, buy case, unlock room, refund |
| `Home` | Home room furniture placement and comfort |
| `Museum` | Museum exhibits, decor, curation, settlement, grand opening |
| `Render` | Canvas 2D drawing, culling, draw-call budget |
| `Audio` | Web Audio API generated sounds |
| `Debug` | `window.__game` synchronous API |

No module imports another module. The only shared mutable object is `ctx`.

## 2.2 Global context

```js
ctx = {
  rng: null,
  rngState: 0,

  tick: 0,
  elapsed: 0.0,
  paused: false,

  ui: {
    screen: "title",
    shopId: 0,
    tab: "home",
    selectedSlot: 0,
    selectedInstance: 0,
    selectedRoom: "home1",
    selectedCase: 1,
    selectedDecorSlot: 0,
    doorOpen: false
  },

  input: {
    move: [0, 0],
    pending: {}
  },

  rosters: {
    resource: {},
    tool: {},
    furniture: {},
    shopkeeper: [],
    room: [],
    museumCase: []
  },

  world: {
    seed: 0,
    width: 120,
    height: 120,
    tiles: [],
    nodeIds: [],
    fishingSpotIds: [],
    shopkeeperIds: [],
    playerStartX: 58,
    playerStartY: 58
  },

  nodes: [],

  shopkeepers: [],

  player: {
    id: "player",
    x: 58,
    y: 58,
    vx: 0.0,
    vy: 0.0,
    facing: 4,
    coins: 20,
    energy: 100,
    maxEnergy: 100,
    selectedToolId: "hands",
    toolsOwned: ["hands", "pickaxe1", "rod1"],
    furnitureBag: [],
    furnitureBagCount: 0,
    toolCooldown: 0.0,
    focusedType: "none",
    focusedId: 0,
    fishingState: "idle",
    fishingTimer: 0.0,
    biteMark: 0.0,
    biteWindow: 0.9,
    sweetZone: 40,
    fishingSpotId: 0,
    catchSuccess: false
  },

  inventory: {
    slots: [],
    capacity: 20,
    totalCount: 0
  },

  home: {
    x: 56,
    y: 56,
    w: 4,
    h: 14,
    comfort: 0,
    rooms: []
  },

  museum: {
    x: 48,
    y: 50,
    w: 8,
    h: 6,
    activeCases: 4,
    cases: [],
    decorSlots: [],
    curation: 0,
    visitorsToday: 0,
    incomeToday: 0,
    grandOpeningDone: false,
    caseCost: 150
  },

  furniture: [],

  day: {
    dayNumber: 1,
    timeOfDay: 0.10,
    paused: false,
    settledToday: false,
    dawnDone: true
  },

  weather: {
    type: "sunny",
    berryYieldBonus: 0,
    oreYieldBonus: 0,
    fishSweetZoneBonus: 0,
    fishBiteWindowDelta: 0.0,
    berryRegrowDelta: 0
  },

  render: {
    drawCalls: 0
  }
}
```

`ctx.rosters` is a frozen copy of the tables in section 4.  
`ctx.inventory.slots` is initialized to 20 slots, each `{ itemId: null, count: 0 }`.  
`ctx.home.rooms` is initialized from the Home Room Roster.  
`ctx.museum.cases` is initialized from the Museum Case Roster.  
`ctx.museum.decorSlots` is initialized to 6 null entries.  
`ctx.world.tiles` is a 120 by 120 array of enum values: `grass`, `water`, `sand`, `mountain`, `interior`.

## 2.3 Module specifics

`RNG`

- `create(seed)` returns an RNG instance.
- `nextInt(lo, hi)` returns an integer `n` where `lo <= n < hi`.
- `pick(arr)` returns one element.
- `range(lo, hi)` returns a float where `lo <= n < hi`.
- `getState()` returns the 32-bit state.
- `setState(n)` sets the 32-bit state.

`Input`

- `poll()` reads raw keys and touch, writes `ctx.input.move`, and sets one-shot flags in `ctx.input.pending`.
- `consume()` returns the one-shot flags and clears them. Called exactly once per tick.

`Time`

- `update(dt)` advances `Day.timeOfDay`, triggers dawn and settlement, sets `Shopkeeper.open`, and mirrors `ctx.paused` into `Day.paused`.
- `sleep()` runs the sleep action when allowed.
- `dawn()` resets daily state, resets general stock, rolls weather, and pays comfort bonus.
- `settlement()` runs Museum Daily Settlement.

`Weather`

- `roll()` rolls weather using RNG and sets modifiers.
- `set(type)` sets weather and modifiers without RNG.

`Player`

- `update(dt)` applies movement, acceleration, collision, facing, tool cooldown, and fishing movement lock.
- `nearestInteractable(range)` returns the highest-priority target within range.
- `selectTool(slot)` selects hands, best pickaxe, or best rod.

`World`

- `generate(seed)` builds tiles, nodes, shops, home, museum, cases, and player start.
- `tileOf(x, y)` returns `[gx, gy]` using tile-center convention.
- `tileRect(gx, gy)` returns `{ x0, y0, x1, y1 }`.
- `walkable(gx, gy)` returns true for grass, sand, mountain, and interior.
- `distance(ax, ay, bx, by)` returns Euclidean distance.
- `verify()` returns the World Generation verifier checks.

`Forage`

- `update(dt)` advances regrowth and handles Use on full berry nodes.
- `onInteract()` resolves berry harvest.

`Mine`

- `update(dt)` advances regrowth and handles Use on full ore nodes.
- `onInteract()` resolves ore strike.

`Fish`

- `update(dt)` advances casting, bitten, and reeling states.
- `onInteract()` starts a cast or resolves a bite.

`Inventory`

- `add(itemId, count)` adds items, returns items actually added.
- `remove(itemId, count)` removes items, returns items actually removed.
- `count(itemId)` returns total count of one itemId.
- `total()` returns total item count.
- `hasSpaceFor(itemId, count)` returns true if the add can succeed.
- `clear()` empties all slots.

`Shop`

- `update(dt)` keeps shop open state current and closes shop screen if the focused shop closes.
- `openToggle(shopId)` opens or closes a shop if allowed.
- `sellAll(itemId)` sells matching inventory up to daily cap.
- `buyTool(toolId)` buys a tool from general shop.
- `buyFurniture(furnitureId)` buys furniture into the bag.
- `buyCase()` buys the next museum case slot.
- `unlockRoom(roomId)` unlocks a home room.
- `refundFurniture(instanceId)` refunds a bag furniture instance.

`Home`

- `placeFurniture(instanceId, roomId, slotIndex)` places bag furniture in a home slot.
- `removeFurniture(instanceId)` removes home furniture into the bag.
- `recompute()` recomputes room comfort and Home comfort.

`Museum`

- `placeExhibit(caseId, itemId)` places one inventory item in an active empty case.
- `removeExhibit(caseId)` removes an exhibit into inventory.
- `placeFurniture(instanceId, decorSlot)` places bag furniture in a museum decor slot.
- `removeFurniture(instanceId)` removes museum furniture into the bag.
- `recompute()` recomputes curation.
- `settleDaily()` runs Museum Daily Settlement.

`Render`

- `frame()` draws one frame, culls, counts draw calls, and drops layers on budget overrun in this order: ground grid, water shimmer, fish, node highlights. It never drops entities or UI.

`Audio`

- `unlock()` resumes or creates the AudioContext on first user gesture.
- `play(name)` plays one generated sound if available.
- `setRainLoop(on)` starts or stops the rain loop.

`Debug`

- All section 8 functions.

# 3. VISUAL SPEC

The game is a low-poly, sun-washed pastoral world rendered as readable 2D top-down sprites. The palette is led by moss green `#7FC850`, berry red `#E84A4F`, ore teal `#3AA6A6`, lake cyan `#7FE3F0`, warm timber `#B98A5B`, and museum cream `#F3EAD8`. The mood is calm, slightly misty, and cozy, with golden-hour warmth rather than realism. The sellable screenshot is the merged T1 view: the player at the cottage/museum cluster, a red berry bush just outside, a bobber in cyan lake water, readable berry-green, mine gray-brown, and cream museum regions, and a warm window or door light when night state is active.

Lighting and atmosphere are implemented as 2D overlays and material swaps.

- Ambient day: multiplier 0.65, sky tint `#BFE8FF`, ground tint `#7FC850`.
- Ambient night: multiplier 0.35, sky tint `#8FB8FF`, ground tint `#2E4A33`, water tint `#28788A`.
- Ambient rain: multiplier 0.50, sky tint `#9FB6C9`, ground wet darkening alpha 0.10.
- Sun/day light: colour `#FFE3A1`, intensity 0.95, angle 50 degrees above horizon.
- Dusk light: colour `#FF9E5A`, intensity 0.60, angle 15 degrees, warm ground tint `#FFC78A` alpha 0.12.
- Night light: colour `#8FB8FF`, intensity 0.20, angle 30 degrees.
- Window lights: cottage and museum windows emit `#FFE9A8`, radius 5 tiles, intensity 0.6, night only.
- Lamp lights: candle lamps emit `#FFD26B`, radius 6 tiles, intensity 0.8, flame brightness varies plus or minus 10 percent.
- Door light: open cottage door emits `#FFE9A8`, radius 5 tiles, intensity 0.6.
- Fog: distance fog starts at 60 tiles and ends at 140 tiles. Day fog colour `#CFE9F2`; night fog colour `#203044`; rain fog colour `#9FB6C9`.
- Rain visual: 800 streaks, each 0.02 tiles long, colour `#B8D9FF`, alpha 0.55; puddle decals `#28788A`, alpha 0.12.
- Post effects: vignette day 0.18, night 0.28, low-energy state 0.35 red `#E84A4F`; grain day 0.04, rain 0.07; invalid placement flash red `#E84A4F`, strength 0.12, duration 0.15 seconds; pickup flash gold `#FFE9A8`, strength 0.08, duration 0.10 seconds.
- Screen shake: mining shake strength 0.03 tiles, duration 0.12 seconds; invalid placement shake strength 0.05 tiles, duration 0.15 seconds.

Space: the merged playable space is the section 4 world: 120 by 120 tiles, berry circle centered at 30,90, mine circle centered at 90,25, Lake A centered at 24,32, Lake B centered at 92,84, home at 56,56, museum at 48,50, and market at 64,58. Visual region reading:

| Visual region | Merged location | Visual purpose |
| --- | --- | --- |
| Berry Grove | Circle center 30,90 radius 20 | Dense green ground, red berry points, leaf patches |
| Mine | Circle center 90,25 radius 14 | Gray-brown mountain ground, sparkling crystals, cracks |
| Lake A | Circle center 24,32 radius 10 | Cyan water, sand shore, reeds, fishing spots |
| Lake B | Circle center 92,84 radius 11 | Deeper cyan water, sand shore, reeds, fishing spots |
| Home Meadow | Tiles around home, museum, market | Warm timber, cream walls, placed furniture, paths |
| Crossroads | Paths between home, berry grove, mine, lakes | Neutral dirt path ribbons |

The original visual 300 by 300 unit region bounds and region prop counts are not T1 logic. They are carried here as source visual values and staged under T4 retheme.

Recipe table. Where a visual count conflicts with section 4, the section 4 count controls gameplay; the visual count is the source render maximum.

| Thing / state | 2D rendering | Size | Colour(s) | Count | Motion / effect |
| --- | --- | ---: | --- | ---: | --- |
| Grass base | Top-down ground plane | 120 by 120 tiles | `#7FC850` | 1 | Subtle vertex variation, static |
| Berry-grove ground | Ground patch | 20 radius tile circle | `#6DBA4A`, leaf patches `#3E7C3F` | 1 | 24 leaf patches, static |
| Mine ground | Mountain patch | 14 radius tile circle | `#8A8F98`, cracks `#6B4A33` | 1 | 12 crack decals, static |
| Lake water | Water plane | Circle radius 8 or 10 tiles | `#38B7C9`, ripple `#7FE3F0` | 2 | Slow ripple bands, shore depth `#7FE3F0` |
| Shore sand | Sand ring | 1 tile wide ring | `#E6D3A3`, wet edge `#C9B27D` | 2 | Static |
| Path segment | Dirt ribbon | 1 tile wide, height 0 | `#C9A15A`, edge `#A8854B` | 7 | Static |
| Cottage walls | Top-down footprint plus roof polygon | 4 by 14 tiles | `#B98A5B`, roof `#C85B3C` | 1 | Static |
| Cottage door, closed | Door rectangle | 1 by 2 tiles | `#5C3A21` | 1 | Static |
| Cottage door, open | Door rotated -80 degrees | 1 by 2 tiles | `#5C3A21`, light `#FFE9A8` | 1 | Light spill 1 by 2 tiles, alpha 0.35 |
| Cottage windows, day | 3 window rectangles | 1 by 1 tiles each | `#BDE8FF`, frame `#5C3A21` | 3 | Static |
| Cottage windows, night | 3 window rectangles | 1 by 1 tiles each | `#FFE9A8`, frame `#5C3A21` | 3 | Glow radius 4 tiles |
| Museum walls | Top-down footprint, columns, roof | 8 by 6 tiles | `#F3EAD8`, columns `#FFF8EF`, roof `#3AA6A6` | 1 | Static |
| Museum windows, day | 3 window rectangles | 1 by 1 tiles each | `#BDE8FF`, frame `#3AA6A6` | 3 | Static |
| Museum windows, night | 3 window rectangles | 1 by 1 tiles each | `#FFE9A8`, frame `#3AA6A6` | 3 | Glow radius 5 tiles |
| Shop stall | Stall footprint plus striped awning | 2 by 2 tiles per stall | `#8C5E3C`, `#F4D16C`, `#E1554F` | 4 | Awning sways 1 degree |
| Shop counter | Counter rectangle | 1 by 1 tiles | `#8C5E3C`, top `#A07A4F` | 4 | 3 jars `#D9784A` on counter |
| Fence segment | 2 posts plus 2 rails | 1 by 0.5 tiles | `#B98A5B` | 14 | Static |
| Berry bush, full | 5 overlapping circles plus 12 berry dots | 0.8 tile radius, 1.0 tile height | `#3E7C3F`, berries `#E84A4F` | 40 source 18 | Berry sway 2 degrees |
| Berry bush, sparse | Same form, 4 berries | 0.8 tile radius | `#3E7C3F`, berries `#E84A4F` | 40 source 9 | Berry sway 2 degrees |
| Berry bush, empty | Same form, 0 berries | 0.8 tile radius | `#2F5F33` | 40 source 9 | Sway 1 degree |
| Berry tree | Trunk circle plus canopy circle | 0.4 trunk, 1.8 canopy | `#6B4A33`, `#4FA35A` | 18 | Canopy sway 2 degrees |
| Ore node, Copper, full | Rock circle plus 8 crystals | 1.1 tile rock, 0.1 tile crystals | `#9AA0A6`, crystals `#D9784A` | 30 source 8 | Crystal glint 0.25 seconds |
| Ore node, Iron, full | Rock circle plus 8 crystals | 1.1 tile rock, 0.1 tile crystals | `#9AA0A6`, crystals `#DDE3E8` | 30 source 8 | Crystal glint 0.25 seconds |
| Ore node, Gemstone, full | Rock circle plus 8 crystals | 1.1 tile rock, 0.1 tile crystals | `#9AA0A6`, crystals `#F4D16C` | 30 source 8 | Crystal glint 0.25 seconds |
| Ore node, mined | Rock with hollow | 1.1 tile rock | `#9AA0A6`, hollow `#4A4E53` | 30 | Dust puff on conversion |
| Reed cluster | 7 cone sprites | 0.4 tile high | `#4F8C45` | 12 | Sway 3 degrees |
| Rock, small | Icosahedron sprite | 0.5 tile | `#7A7F86` | 26 | Static |
| Rock, large | Icosahedron sprite | 0.9 tile | `#7A7F86` | 14 | Static |
| Tree, meadow | Trunk plus canopy | 0.5 trunk, 2 canopy | `#6B4A33`, `#4FA35A` | 6 | Canopy sway 2 degrees |
| Stump | Cylinder sprite | 0.4 tile diameter, 0.3 tile high | `#A07A4F` | 4 | Static |
| Dock | Plank rectangle plus 4 posts | 2 by 0.5 tiles | `#8C5E3C`, posts `#6B4A33` | 3 | Static |
| Fishing bobber, idle | Circle with top band | 0.1 tile | `#FF6B4A`, top `#FFF8EF` | 12 source 3 | Bob 0.03 tile |
| Fishing bobber, bite | Circle | 0.1 tile | `#FF6B4A`, top `#FFF8EF` | 1 | Dip 0.1 tile |
| Fish, on hook | Elongated diamond | 0.3 by 0.1 tiles | `#8AD6E8`, belly `#FFF8EF` | 1 | Wiggle 4 degrees |
| Chair | Box seat plus 4 legs | 0.4 by 0.4 tiles | `#A05A2C`, legs `#7A431F` | max from Furniture Roster | Static |
| Table | Box top plus 4 legs | 0.7 by 0.4 tiles | `#A07A4F`, legs `#8C5E3C` | max from Furniture Roster | Static |
| Rug | Flat rectangle | 1 by 0.7 tiles | `#C85B3C`, border `#F4D16C` | T2 only | Static |
| Shelf | Box rectangle | 0.7 by 0.3 tiles | `#8C5E3C` | max from Furniture Roster | Static |
| Plant pot | Pot circle plus plant cone | 0.3 tile diameter, 0.4 tile high | `#D9784A`, plant `#55A35A` | max from Furniture Roster | Static |
| Display case | Frame plus glass rectangle | 0.7 by 0.7 tiles | frame `#3AA6A6`, glass `#FFFFFF` alpha 0.35 | max from Furniture Roster | Static |
| Painting | Flat rectangle | 0.5 by 0.3 tiles | frame `#D9B25A`, canvas `#7FC850` | max from Furniture Roster | Static |
| Candle lamp | Base plus flame circle | 0.2 tile base, 0.1 tile flame | `#7A431F`, flame `#FFD26B` | max from Furniture Roster | Flame brightness varies plus or minus 10 percent |
| Berry pickup | Circle | 0.06 tile | `#E84A4F` | 1 | Pop scale 1.25 for 0.15 seconds |
| Ore pickup, Copper | Crystal shard | 0.1 tile | `#D9784A` | 1 | Rotate 90 degrees for 0.2 seconds |
| Ore pickup, Iron | Crystal shard | 0.1 tile | `#DDE3E8` | 1 | Rotate 90 degrees for 0.2 seconds |
| Ore pickup, Gemstone | Crystal shard | 0.1 tile | `#F4D16C` | 1 | Rotate 90 degrees for 0.2 seconds |
| Fish pickup | Elongated diamond | 0.3 tile | `#8AD6E8`, belly `#FFF8EF` | 1 | Wiggle 6 degrees |
| Coin pickup | Cylinder sprite | 0.09 by 0.03 tiles | `#F4D16C`, edge `#C9A15A` | 5 | Arc 0.2 tile for 0.2 seconds |
| Gather sparkle | 8 particles | 0.04 tile each | `#FFE9A8` | 1 set | Expand 0.15 tile for 0.18 seconds |
| Ore chip | 6 shards | 0.06 tile each | `#9AA0A6` | 1 set | Fall 0.2 tile for 0.20 seconds |
| Fish splash | 8 droplets | 0.03 tile each | `#7FE3F0` | 1 set | Expand 0.25 tile for 0.25 seconds |
| Door light spill | Triangle | 1 by 2 tiles | `#FFE9A8` alpha 0.35 | 1 | Fade for 0.25 seconds |
| Selection ring | Circle outline | 0.8 tile | `#F4D16C` alpha 0.8 | 1 | Static |
| Placement ghost, valid | Selected furniture sprite, transparent | Object size | `#FFFFFF` alpha 0.45, outline `#7FE37F` | 1 | Pulse 2 times over 0.2 seconds |
| Placement ghost, invalid | Selected furniture sprite, transparent | Object size | `#FFFFFF` alpha 0.45, outline `#E84A4F` | 1 | Shake 0.03 tile for 0.15 seconds |
| Inventory bar | Rounded rectangle | 520 by 84 px | `#1F2A22` alpha 0.82, border `#F4D16C` | 1 | Static |
| Inventory slot, empty | Square | 64 by 64 px | `#334238`, border `#5A6B5D` | 12 | Static |
| Inventory slot, filled | Square plus icon | 64 by 64 px, icon 48 by 48 px | `#3E5244`, border `#F4D16C` | 12 | Icon pop 0.15 seconds |
| Inventory slot, selected | Square | 64 by 64 px | `#3E5244`, border `#FFE9A8` 4 px wide | 1 | Glow 0.2 seconds |
| Notification toast | Rounded rectangle plus icon | 220 by 48 px, icon 32 by 32 px | `#1F2A22` alpha 0.88, text `#FFF8EF`, icon `#F4D16C` | 1 | Slide in 0.18 seconds |
| Shop panel | Rounded rectangle | 420 by 520 px | `#F4E9C9`, header `#E1554F`, border `#B98A5B` | 1 | Slide in 0.18 seconds |
| Shop item row | Row plus icon | 380 by 56 px, icon 48 by 48 px | `#FFF8EF`, icon varies by item type | 8 | Static |
| Shop button, normal | Rounded rectangle | 120 by 40 px | `#7FC850`, label `#1F2A22` | 3 | Static |
| Shop button, hover | Rounded rectangle | 120 by 40 px | `#8FD45B`, label `#1F2A22` | 1 | Scale 1.03 for 0.1 seconds |
| Shop button, selected | Rounded rectangle | 120 by 40 px | `#F4D16C`, label `#1F2A22`, border `#E1554F` | 1 | Pulse 0.2 seconds |
| Energy bar | Rounded rectangle plus fill | 180 by 18 px | background `#334238`, fill `#7FE3F0` | 1 | Fill follows Player.energy |
| Energy bar, low | Rounded rectangle plus fill | 180 by 18 px | background `#334238`, fill `#FF6B4A` | 1 | Pulse 0.15 seconds |

# 4. GAMEPLAY SPEC

The player walks a 120 by 120 open world as a collector, routing between berry bushes, ore outcrops, and lake fishing spots each day. They harvest berries with Foraging Hands, strike ore with a Pickaxe, cast and reel fish with a Rod, carry items to three type-specific buyer shopkeepers, and buy tools, furniture, museum case slots, and home room unlocks from the General Shopkeeper. The loop keeps earning because better tools raise yield, better furniture raises Home Comfort and energy regen, filled Museum Cases raise Curation and daily visitor income, and rare items like Gemstone and Coralfish are worth more than common ones. There is no forced end: the player may keep collecting, decorating, and expanding the museum forever; the optional one-time Grand Opening fires once when Museum Curation reaches 100 and Home Comfort reaches 50, awards 1000 coins, and then the game continues.

Records:

- World
- Player
- Inventory
- ResourceNode
- Shopkeeper
- FurnitureInstance
- Home
- HomeRoom
- Museum
- MuseumCase
- Day
- Weather

World is the persistent tile map. Fields: `seed` integer, `width` 120, `height` 120, `tiles` 120 by 120 array of enum `grass`, `water`, `sand`, `mountain`, `interior`, `nodeIds` list of integer ids, `fishingSpotIds` list of integer ids, `shopkeeperIds` list of string ids, `playerStartX` 58, `playerStartY` 58.

Player is the character and active tool state. Fields: `id` string start `player`, `x` float tiles start 58, `y` float tiles start 58, `vx` float tiles/second start 0, `vy` float tiles/second start 0, `facing` integer 0 to 7 start 4, `coins` integer start 20, `energy` float 0 to 100 start 100, `maxEnergy` 100, `selectedToolId` string start `hands`, `toolsOwned` list start `hands`, `pickaxe1`, `rod1`, `furnitureBag` list of integer furnitureInstanceId start empty, `furnitureBagCount` 0 to 12 start 0, `toolCooldown` float seconds start 0, `focusedType` enum `none`, `shopkeeper`, `bed`, `case`, `node` start `none`, `focusedId` integer start 0, `fishingState` enum `idle`, `casting`, `bitten`, `reeling` start `idle`, `fishingTimer` float start 0, `biteMark` float 0 to 200 start 0, `biteWindow` float 0 to 2 start 0.9, `sweetZone` integer 0 to 200 start 40, `fishingSpotId` integer start 0, `catchSuccess` boolean start false.

Inventory is carried resource/fish storage. Fields: `slots` array length 20 of `{itemId string or null, count integer 0 to 99}`, `capacity` 20, `totalCount` 0 to 1980.

ResourceNode is a harvestable berry bush, mineable ore node, or lake fishing spot. Fields: `id` integer, `kind` enum `berry`, `ore`, `fishingSpot`, `itemId` string resourceId or null, `x` integer tile, `y` integer tile, `stage` enum `full`, `empty` start `full`, `regrowTimer` float seconds start 0, `remainingHits` integer start 0, `lakeType` integer 1 to 2 start 1.

Shopkeeper is a market stall. Fields: `id` string, `kind` enum `berryBuyer`, `oreBuyer`, `fishBuyer`, `general`, `x` integer tile, `y` integer tile, `openStart` 0.10, `openEnd` 0.95, `dailyCap` integer, `dailyBought` integer start 0, `open` boolean start false, `toolStock` list of `{toolId, count}`, `furnitureStock` list of `{furnitureId, count}`, `caseCost` 150 for general and 0 for others, `parlorCost` 200 for general and 0 for others, `libraryCost` 800 for general and 0 for others.

FurnitureInstance is one bought furniture piece. Fields: `instanceId` integer start 1, `definitionId` string furnitureId, `location` enum `bag`, `home`, `museum` start `bag`, `roomId` string or null, `slotIndex` integer or null, `comfort` integer from definition, `museumPoints` integer from definition, `refundCoins` integer from definition.

Home is the player house. Fields: `x` 56, `y` 56, `w` 4, `h` 14, `comfort` 0 to 1000 start 0, `rooms` list of 3 HomeRoom.

HomeRoom is one room. Fields: `id` string, `name` string, `x` integer, `y` integer, `w` integer, `h` integer, `unlocked` boolean, `unlockCost` integer, `slots` array length 8 of furnitureInstanceId or null, `roomComfort` 0 to 100 start 0.

Museum is the museum building. Fields: `x` 48, `y` 50, `w` 8, `h` 6, `activeCases` 4 to 12 start 4, `cases` list of 12 MuseumCase, `decorSlots` array length 6 of furnitureInstanceId or null, `curation` 0 to 10000 start 0, `visitorsToday` 0 to 20 start 0, `incomeToday` integer start 0, `grandOpeningDone` boolean start false, `caseCost` 150.

MuseumCase is one display case. Fields: `id` 1 to 12, `active` boolean, `x` integer, `y` integer, `itemId` string or null, `exhibitValue` integer start 0.

Day is the clock. Fields: `dayNumber` start 1, `timeOfDay` float 0 to 1 start 0.10, `paused` boolean mirror of `ctx.paused`, `settledToday` start false, `dawnDone` start true.

Weather is the current day weather. Fields: `type` enum `sunny`, `rain`, `snow` start `sunny`, `berryYieldBonus` integer start 0, `oreYieldBonus` integer start 0, `fishSweetZoneBonus` integer start 0, `fishBiteWindowDelta` float start 0, `berryRegrowDelta` integer start 0.

Resource Roster

| itemId | kind | sellPrice | exhibitValue | yieldMin | yieldMax | regrowSeconds | requiredPickaxe | hitsToMine | chanceLake1Day | chanceLake1Night | chanceLake2Day | chanceLake2Night | nightOnly |
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

| toolId | kind | cost | tier | pickaxePower | pickaxeEnergy | pickaxeYieldBonus | rodBiteWindow | rodSweetZone | rodEnergy |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| hands | forage | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| pickaxe1 | pickaxe | 0 | 1 | 1 | 5 | 0 | 0 | 0 | 0 |
| pickaxe2 | pickaxe | 120 | 2 | 2 | 4 | 1 | 0 | 0 | 0 |
| pickaxe3 | pickaxe | 450 | 3 | 3 | 3 | 2 | 0 | 0 | 0 |
| rod1 | rod | 0 | 1 | 0 | 0 | 0 | 0.9 | 40 | 5 |
| rod2 | rod | 90 | 2 | 0 | 0 | 0 | 0.8 | 55 | 5 |
| rod3 | rod | 0 | 3 | 0 | 0 | 0 | 0.7 | 70 | 5 |

Correction to the source table: `rod3` cost is 260, not 0. Ruling: `rod3` cost is 260.

Furniture Roster

| furnitureId | name | cost | comfort | museumPoints | refundCoins | allowed | maxPerRoom |
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

| shopkeeperId | name | kind | x | y | openStart | openEnd | dailyCap | buysKind | sellsFurniture |
|---|---|---|---:|---:|---:|---:|---:|---|---|
| berryBuyer | Berry Buyer | berryBuyer | 64 | 58 | 0.10 | 0.95 | 60 | berry | false |
| oreBuyer | Ore Buyer | oreBuyer | 66 | 58 | 0.10 | 0.95 | 40 | ore | false |
| fishBuyer | Fish Buyer | fishBuyer | 65 | 63 | 0.10 | 0.95 | 50 | fish | false |
| general | General Shopkeeper | general | 64 | 63 | 0.10 | 0.95 | 0 | none | true |

Home Room Roster

| roomId | name | x | y | w | h | unlocked | unlockCost | slots |
|---|---|---:|---:|---:|---:|---|---:|---:|
| home1 | Start Room | 56 | 56 | 4 | 4 | true | 0 | 8 |
| home2 | Parlor | 56 | 61 | 4 | 4 | false | 200 | 8 |
| home3 | Library | 56 | 66 | 4 | 4 | false | 800 | 8 |

Museum Case Roster

| caseId | x | y | activeStart |
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

## World Generation, T1

Seeded generator:

- Input: `World.seed`.
- Step 1: Set all 120 by 120 `World.tiles` to grass.
- Step 2: Set tiles inside circle center 90,25 radius 14 to mountain.
- Step 3: Set Lake A water to circle center 24,32 radius 8; set Lake A sand ring to radius 9. Set Lake B water to circle center 92,84 radius 10; set Lake B sand ring to radius 11.
- Step 4: Set all tiles in Home rect 56,56 to 59,69 to interior. Set all tiles in Museum rect 48,50 to 55,55 to interior. Set all tiles in Market rect 64,58 to 67,63 to interior. Set bed at tile 57,57.
- Step 5: Create HomeRoom records from the Home Room Roster.
- Step 6: Create MuseumCase records from the Museum Case Roster. Set active true for caseId 1 to 4 and false for caseId 5 to 12.
- Step 7: Create Shopkeeper records from the Shopkeeper Roster.
- Step 8: Place 40 ResourceNode kind berry. For node index 1 to 20, candidate tile must be inside circle center 30,90 radius 14. For node index 21 to 32, candidate tile must be inside circle center 30,90 radius 20. For node index 33 to 40, candidate tile can be anywhere. For each node, make up to 100 seeded random candidate integer tile coordinates in 0 to 119. Reject a candidate if the tile is not grass, is occupied by another node, fishing spot, or shopkeeper, is within 3 tiles of any interior tile, or is within 1 tile of water. If accepted, place node. Assign itemId by node index: 1 to 14 Sunberry, 15 to 28 Blueberry, 29 to 40 Glowberry.
- Step 9: Place 30 ResourceNode kind ore. For node index 1 to 24, candidate tile must be inside circle center 90,25 radius 14. For node index 25 to 30, candidate tile can be anywhere. For each node, make up to 100 seeded random candidate integer tile coordinates in 0 to 119. Reject a candidate if the tile is not grass or mountain, is occupied, is within 3 tiles of any interior tile, or is within 1 tile of water. If accepted, place node. Assign itemId by node index: 1 to 12 Copper, 13 to 22 Iron, 23 to 30 Gemstone.
- Step 10: Place 12 ResourceNode kind fishingSpot. For Lake A, place 5 fishing spots on distinct sand tiles in the Lake A sand ring that are within 1 tile of water. For Lake B, place 7 fishing spots on distinct sand tiles in the Lake B sand ring that are within 1 tile of water. Use seeded random candidates, up to 100 attempts per spot, rejecting occupied tiles and non-adjacent-to-water sand. Set lakeType 1 for Lake A spots and lakeType 2 for Lake B spots.
- Step 11: Set `Player.x = World.playerStartX` and `Player.y = World.playerStartY`.
- Step 12: Initialize General toolStock to pickaxe2 one, pickaxe3 one, rod2 one, rod3 one. Initialize General furnitureStock to 3 for every Furniture Roster id.

Circle test: a candidate integer tile `(x, y)` is inside circle center `(cx, cy)` radius `r` if `(x - cx)^2 + (y - cy)^2 <= r^2`.  
Within 3 tiles of interior: Chebyshev distance 3 or less to any interior tile.  
Within 1 tile of water: Chebyshev distance 1 or less to any water tile.

Verifier:

- Check 1: All 40 berry nodes, 30 ore nodes, and 12 fishing spots were placed.
- Check 2: At least 12 berry nodes have Euclidean distance 10 tiles or less from 58,58.
- Check 3: At least 8 ore nodes have Euclidean distance 15 tiles or less from 90,25.
- Check 4: A breadth-first search from 58,58 through walkable tiles reaches all 4 shopkeepers, all 12 museum cases, at least 35 berry nodes, at least 25 ore nodes, and at least 10 fishing spots.
- Check 5: No two nodes share a tile; no node is on water; no node is on interior.
- If any check fails, re-roll with the next seed and set `World.seed` to the accepted seed.

## Time, T1

- While screen is not paused and `Day.paused` is false, `Day.timeOfDay += delta / 300.0`.
- If `Day.timeOfDay >= 1.0`, set `Day.timeOfDay -= 1.0`, `Day.dayNumber += 1`, `Day.dawnDone = false`.
- If `Day.timeOfDay` crosses 0.95 and `Day.settledToday` is false, set `Day.settledToday = true` and run Museum Daily Settlement.
- If `Day.timeOfDay` crosses 0.10 and `Day.dawnDone` is false, run Dawn and set `Day.dawnDone = true`.
- Every tick, set `Shopkeeper.open = true` if `Day.timeOfDay >= 0.10` and `Day.timeOfDay < 0.95`; otherwise false.
- Sleep is allowed if `Player.focusedType` is `bed`, the bed is 57,57, `Day.timeOfDay >= 0.75`, and Use is pressed.
  - If `Day.settledToday` is false, run Museum Daily Settlement and set `Day.settledToday = true`.
  - Set `Day.dayNumber += 1`, `Day.timeOfDay = 0.10`, `Day.dawnDone = true`, `Player.energy = 100`.
  - Run Dawn.
- Dawn:
  - Reset every Shopkeeper `dailyBought` to 0.
  - Reset General Shopkeeper `toolStock` to pickaxe2 one, pickaxe3 one, rod2 one, rod3 one.
  - Reset General Shopkeeper `furnitureStock` to 3 for every Furniture Roster id.
  - Roll Weather.
  - If `Home.comfort >= 50`, `Player.coins += 30`; else if `Home.comfort >= 25`, `Player.coins += 15`; else if `Home.comfort >= 10`, `Player.coins += 5`; else no change.

## Weather, T1

- At Dawn, roll one random integer from 0 to 99 using `RNG.nextInt(0, 100)`.
- Roll 0 to 49: `Weather.type = sunny`.
- Roll 50 to 79: `Weather.type = rain`.
- Roll 80 to 99: `Weather.type = snow`.
- Sunny sets: `berryYieldBonus = 0`, `oreYieldBonus = 0`, `fishSweetZoneBonus = 0`, `fishBiteWindowDelta = 0`, `berryRegrowDelta = 0`.
- Rain sets: `berryYieldBonus = 1`, `oreYieldBonus = 0`, `fishSweetZoneBonus = 10`, `fishBiteWindowDelta = 0`, `berryRegrowDelta = -15`.
- Snow sets: `berryYieldBonus = 0`, `oreYieldBonus = 1`, `fishSweetZoneBonus = -10`, `fishBiteWindowDelta = -0.1`, `berryRegrowDelta = 30`.

## Movement, T1

- Keyboard and touch movement input vector: W or Up is `(0, -1)`; S or Down is `(0, 1)`; A or Left is `(-1, 0)`; D or Right is `(1, 0)`.
- If two axes are pressed, normalize the input vector to length 1.0.
- If input vector length is greater than 0, target velocity is input vector times 4.0 tiles/second. If input vector length is 0, target velocity is `(0, 0)`.
- Player velocity approaches target velocity at 10.0 tiles/second squared when input is present and 12.0 tiles/second squared when input is absent.
- Player velocity magnitude never exceeds 4.0 tiles/second.
- `Player.x += vx * delta` and `Player.y += vy * delta`.
- Move axes separately. An axis move is allowed only if the target tile is walkable. Walkable tiles are grass, sand, mountain, and interior. Water is not walkable.
- If an axis move is blocked, keep that axis position and set that axis velocity component to 0.
- If input vector length is greater than 0, set `Player.facing` to the nearest of 8 directions: 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW.
- If `Player.fishingState` is not `idle`, movement input is ignored and target velocity is `(0, 0)`.
- Tool selection:
  - 1 sets `Player.selectedToolId` to `hands` if owned.
  - 2 sets `Player.selectedToolId` to the owned pickaxe with the highest tier.
  - 3 sets `Player.selectedToolId` to the owned rod with the highest tier.
  - If no tool of that kind is owned, selection does not change.

## Targeting, T1

- Each tick, reset `Player.focusedType = none` and `Player.focusedId = 0`.
- Priority:
  1. If any Shopkeeper is within 2.5 tiles, set `focusedType = shopkeeper` and `focusedId` to that shopkeeper id.
  2. Else if the bed at 57,57 is within 2.5 tiles, set `focusedType = bed` and `focusedId = 0`.
  3. Else if any active MuseumCase is within 2.5 tiles, set `focusedType = case` and `focusedId` to that case id.
  4. Else if any ResourceNode is within 2.5 tiles, choose the nearest ResourceNode and set `focusedType = node` and `focusedId` to that node id.
- If `focusedType` is `shopkeeper` and `Shopkeeper.open` is false, the action is blocked and the prompt says Closed.
- If `focusedType` is `bed` and `Day.timeOfDay < 0.75`, the action is blocked and the prompt says Night only.

## Energy, T1

- If `Player.toolCooldown > 0`, subtract `delta`; if less than 0, set 0.
- Compute comfortBonus:
  - If `Home.comfort >= 50`, comfortBonus is 0.6.
  - Else if `Home.comfort >= 25`, comfortBonus is 0.4.
  - Else if `Home.comfort >= 10`, comfortBonus is 0.2.
  - Else comfortBonus is 0.
- `Player.energy += (1.0 + comfortBonus) * delta / 5.0`.
- If `Player.energy > Player.maxEnergy`, set `Player.energy = Player.maxEnergy`.
- Sleep sets `Player.energy = 100`.

## Foraging, T1

- Let night be true if `Day.timeOfDay >= 0.75` or `Day.timeOfDay <= 0.10`; otherwise false.
- A harvest is allowed if:
  - `Player.focusedType` is `node`.
  - `ResourceNode.kind` is `berry`.
  - `Player.selectedToolId` is `hands`.
  - `ResourceNode.stage` is `full`.
  - `Player.toolCooldown` is 0.
  - `Player.energy >= 2`.
  - Inventory has space for the maximum possible yield.
- Maximum possible yield:
  - If `ResourceNode.itemId` is Glowberry and night is false, maximum possible yield is 0.
  - Else maximum possible yield is Resource Roster `yieldMax` plus, if Weather.type is rain and itemId is Sunberry or Blueberry, Weather.berryYieldBonus.
- If maximum possible yield is 0, the harvest is blocked.
- On successful Use:
  - `Player.energy -= 2`.
  - `Player.toolCooldown = 0.4`.
  - Roll one integer uniformly from Resource Roster `yieldMin` to `yieldMax` inclusive using `RNG.nextInt(yieldMin, yieldMax + 1)`.
  - If Weather.type is rain and itemId is Sunberry or Blueberry, add Weather.berryYieldBonus to the rolled count.
  - Add that count of `ResourceNode.itemId` to Inventory.
  - Set `ResourceNode.stage = empty`.
  - Set `ResourceNode.regrowTimer = Resource Roster regrowSeconds + Weather.berryRegrowDelta`.
  - If `ResourceNode.regrowTimer < 15`, set `ResourceNode.regrowTimer = 15`.
- If `ResourceNode.stage = empty` and `ResourceNode.regrowTimer > 0`, subtract `delta` from `regrowTimer`.
- If `ResourceNode.regrowTimer <= 0`, set `regrowTimer = 0` and `stage = full`.

## Mining, T1

- Let tool be the Tool Roster entry for `Player.selectedToolId`.
- A mine strike is allowed if:
  - `Player.focusedType` is `node`.
  - `ResourceNode.kind` is `ore`.
  - `ResourceNode.stage` is `full`.
  - `ResourceNode.remainingHits > 0`.
  - Tool kind is `pickaxe`.
  - Tool tier is greater than or equal to Resource Roster `requiredPickaxe`.
  - `Player.toolCooldown = 0`.
  - `Player.energy >= tool.pickaxeEnergy`.
  - Inventory has space for the maximum possible final yield.
- Maximum possible final yield: Resource Roster `yieldMax` plus tool.pickaxeYieldBonus plus, if Weather.type is snow and itemId is Copper or Iron, Weather.oreYieldBonus.
- On successful Use:
  - `Player.energy -= tool.pickaxeEnergy`.
  - `Player.toolCooldown = 0.45`.
  - `ResourceNode.remainingHits -= tool.pickaxePower`.
  - If `ResourceNode.remainingHits > 0`, no item is added.
  - If `ResourceNode.remainingHits <= 0`:
    - Add maximum possible final yield of `ResourceNode.itemId` to Inventory.
    - Set `ResourceNode.stage = empty`.
    - Set `ResourceNode.regrowTimer = Resource Roster regrowSeconds`.
- If `ResourceNode.stage = empty` and `ResourceNode.regrowTimer > 0`, subtract `delta` from `regrowTimer`.
- If `ResourceNode.regrowTimer <= 0`, set `regrowTimer = 0`, `stage = full`, and `remainingHits = Resource Roster hitsToMine`.

## Fishing, T1

- Let tool be the Tool Roster entry for `Player.selectedToolId`.
- A cast is allowed if:
  - `Player.focusedType` is `node`.
  - `ResourceNode.kind` is `fishingSpot`.
  - Tool kind is `rod`.
  - `Player.fishingState` is `idle`.
  - `Player.toolCooldown = 0`.
  - `Player.energy >= tool.rodEnergy`.
  - Inventory has space for 1 item.
- On successful Use:
  - `Player.energy -= tool.rodEnergy`.
  - `Player.fishingState = casting`.
  - `Player.fishingTimer = 0`.
  - `Player.fishingSpotId = ResourceNode.id`.
  - `Player.catchSuccess = false`.
- Casting:
  - While `Player.fishingState = casting`, `Player.fishingTimer += delta`.
  - If `Player.fishingTimer >= 0.8`, set `Player.fishingState = bitten`, `Player.fishingTimer = 0`, `Player.biteMark = 0`.
  - Set `Player.biteWindow = tool.rodBiteWindow + Weather.fishBiteWindowDelta`. If less than 0.5, set 0.5.
  - Set `Player.sweetZone = tool.rodSweetZone + Weather.fishSweetZoneBonus`. If less than 20, set 20.
  - The new `bitten` state does not advance `biteMark` in the same tick that casting transitions.
- Bitten:
  - While `Player.fishingState = bitten`, `Player.biteMark += (200.0 / Player.biteWindow) * delta`.
  - If Use is pressed while bitten:
    - If `Player.biteMark >= 100 - Player.sweetZone / 2` and `Player.biteMark <= 100 + Player.sweetZone / 2`, set `Player.catchSuccess = true`; else set `Player.catchSuccess = false`.
    - Set `Player.fishingState = reeling` and `Player.fishingTimer = 0`.
  - If no press is made and `Player.biteMark >= 200`, set `Player.catchSuccess = false`, `Player.fishingState = reeling`, and `Player.fishingTimer = 0`.
- Reeling:
  - While `Player.fishingState = reeling`, `Player.fishingTimer += delta`.
  - If `Player.fishingTimer >= 0.5`:
    - If `Player.catchSuccess` is true, add 1 fish to Inventory using the spot's lakeType and night table.
    - Set `Player.fishingState = idle` and `Player.toolCooldown = 0.5`.
- Fish selection:
  - Let spot be the ResourceNode with id `Player.fishingSpotId`.
  - Let night be true if `Day.timeOfDay >= 0.75` or `Day.timeOfDay <= 0.10`; otherwise false.
  - If spot.lakeType is 1 and night is false, use chances: Minnow 65, Sunfish 35.
  - If spot.lakeType is 1 and night is true, use chances: Minnow 50, Sunfish 30, Moonfish 20.
  - If spot.lakeType is 2 and night is false, use chances: Sunfish 55, Moonfish 20, Coralfish 25.
  - If spot.lakeType is 2 and night is true, use chances: Sunfish 40, Moonfish 45, Coralfish 15.
  - Roll one integer from 1 to 100 inclusive using `RNG.nextInt(1, 101)`.
  - In the fixed order Minnow, Sunfish, Moonfish, Coralfish, add the first species whose cumulative chance is greater than or equal to the roll.

## Selling, T1

- A buyer Shopkeeper can be opened only if `Shopkeeper.open` is true and the player is within 2.5 tiles.
- In Shop state for `berryBuyer`, `oreBuyer`, or `fishBuyer`, Sell All is available for each Inventory slot whose itemId kind matches `Shopkeeper.buysKind`.
- If Sell All is pressed for itemId:
  - Let remainingCap be `Shopkeeper.dailyCap - Shopkeeper.dailyBought`.
  - Let sellCount be the minimum of the Inventory slot count and remainingCap.
  - If sellCount is greater than 0:
    - `Player.coins += sellCount * Resource Roster sellPrice`.
    - Remove sellCount from that Inventory slot.
    - `Shopkeeper.dailyBought += sellCount`.
  - If sellCount is 0, no field changes.

## Buying, T1

- General Shopkeeper is the only shopkeeper that sells tools, furniture, case slots, home room unlocks, and refunds furniture.
- Buy Tool is available if:
  - General Shopkeeper is open.
  - Tool is not in `Player.toolsOwned`.
  - `Shopkeeper.toolStock` count for tool is greater than 0.
  - `Player.coins >= Tool Roster cost`.
  - On buy:
    - `Player.coins -= cost`.
    - Decrement `Shopkeeper.toolStock` count by 1.
    - Add toolId to `Player.toolsOwned`.
    - If Tool Roster kind for tool is the same as `Player.selectedToolId` kind, set `Player.selectedToolId = toolId`.
- Buy Furniture is available if:
  - General Shopkeeper is open.
  - `Shopkeeper.furnitureStock` count for furnitureId is greater than 0.
  - `Player.coins >= Furniture Roster cost`.
  - `Player.furnitureBagCount < 12`.
  - On buy:
    - `Player.coins -= cost`.
    - Decrement `Shopkeeper.furnitureStock` count by 1.
    - Create FurnitureInstance with `definitionId = furnitureId`, `location = bag`, `comfort`, `museumPoints`, and `refundCoins` from the Furniture Roster.
    - Add its `instanceId` to `Player.furnitureBag`.
    - `Player.furnitureBagCount += 1`.
- Buy Museum Case is available if:
  - `Museum.activeCases < 12`.
  - `Player.coins >= Museum.caseCost`, which is 150.
  - On buy:
    - `Player.coins -= 150`.
    - `Museum.activeCases += 1`.
    - Set the lowest inactive MuseumCase id to `active = true`.
- Unlock Home Room is available for a HomeRoom with `unlocked = false` if `Player.coins >= HomeRoom.unlockCost`.
  - On unlock:
    - `Player.coins -= HomeRoom.unlockCost`.
    - `HomeRoom.unlocked = true`.
- Refund Furniture is available for any FurnitureInstance with `location = bag`.
  - On refund:
    - `Player.coins += FurnitureInstance.refundCoins`.
    - Remove that instance from `Player.furnitureBag`.
    - `Player.furnitureBagCount -= 1`.
  - Refunding does not delete the FurnitureInstance record; its location becomes `bag` only if it was not already bag. For refund from bag, the record is removed from the bag list and the instance remains owned but unplaced.
- At Dawn, General Shopkeeper toolStock and furnitureStock reset as defined in Time.

## Inventory, T1

- Inventory has 20 slots.
- Each slot holds one itemId and an integer count 0 to 99.
- `add(itemId, count)`:
  - First, find a slot with the same itemId where `count + added count <= 99`. If found, increase that slot count.
  - Else find an empty slot and set itemId with count.
  - Else the add fails and no fields change.
- `remove(itemId, count)`:
  - Decrease the matching slot count by count.
  - If a slot count becomes 0, set its itemId to null and count to 0.
- `Player.furnitureBagCount` is the count of entries in `Player.furnitureBag` and may not exceed 12.
- Adding a FurnitureInstance to `Player.furnitureBag` increases `Player.furnitureBagCount` by 1.
- Removing a FurnitureInstance from `Player.furnitureBag` decreases `Player.furnitureBagCount` by 1.

## Home, T1

- Home has 3 HomeRoom records.
- Only unlocked HomeRooms can hold furniture.
- Place Furniture in Home is available from `Player.furnitureBag` if:
  - The chosen HomeRoom.unlocked is true.
  - The chosen HomeRoom slot is null.
  - Furniture Roster allowed for definitionId includes home.
  - The count of the same definitionId in that HomeRoom is less than Furniture Roster maxPerRoom.
  - On place:
    - Remove instance from `Player.furnitureBag`.
    - Set `FurnitureInstance.location = home`.
    - Set `FurnitureInstance.roomId = HomeRoom.id`.
    - Set `FurnitureInstance.slotIndex = chosen slot`.
    - Set the HomeRoom slot to `FurnitureInstance.instanceId`.
    - `Player.furnitureBagCount -= 1`.
- Remove Furniture from Home is available if `Player.furnitureBagCount < 12`.
  - On remove:
    - Set HomeRoom slot to null.
    - Set `FurnitureInstance.location = bag`.
    - Set `FurnitureInstance.roomId = null`.
    - Set `FurnitureInstance.slotIndex = null`.
    - Add instance to `Player.furnitureBag`.
    - `Player.furnitureBagCount += 1`.
- Recompute Home.comfort after any place, remove, or unlock:
  - For each unlocked HomeRoom, `HomeRoom.roomComfort` is the sum of FurnitureInstance.comfort in that room's slots.
  - `Home.comfort` is the sum of `HomeRoom.roomComfort` for all unlocked HomeRooms.

## Museum, T1

- Museum has 12 MuseumCase records and 6 decorSlots.
- Place Exhibit is available if:
  - A MuseumCase.active is true.
  - MuseumCase.itemId is null.
  - The chosen Inventory itemId has count greater than 0.
  - On place:
    - Remove 1 from that Inventory slot.
    - Set `MuseumCase.itemId = itemId`.
    - Set `MuseumCase.exhibitValue = Resource Roster exhibitValue for itemId`.
- Remove Exhibit is available if:
  - MuseumCase.itemId is not null.
  - Inventory has space for 1 item.
  - On remove:
    - Add 1 MuseumCase.itemId to Inventory.
    - Set `MuseumCase.itemId = null`.
    - Set `MuseumCase.exhibitValue = 0`.
- Place Furniture in Museum is available from `Player.furnitureBag` if:
  - The chosen `Museum.decorSlots` entry is null.
  - Furniture Roster allowed for definitionId includes museum.
  - The count of the same definitionId already in `Museum.decorSlots` is less than Furniture Roster maxPerRoom.
  - On place:
    - Remove instance from `Player.furnitureBag`.
    - Set `FurnitureInstance.location = museum`.
    - Set the decorSlots entry to `FurnitureInstance.instanceId`.
    - `Player.furnitureBagCount -= 1`.
- Remove Furniture from Museum is available if `Player.furnitureBagCount < 12`.
  - On remove:
    - Set the decorSlots entry to null.
    - Set `FurnitureInstance.location = bag`.
    - Add instance to `Player.furnitureBag`.
    - `Player.furnitureBagCount += 1`.
- Recompute Museum.curation after any exhibit or furniture change:
  - `Museum.curation` is the sum of `MuseumCase.exhibitValue` for all active cases with itemId not null, plus the sum of `FurnitureInstance.museumPoints` for all FurnitureInstance with location museum.
- Museum Daily Settlement:
  - If `Museum.curation` is 0 to 9, `Museum.visitorsToday = 0`.
  - If `Museum.curation` is 10 to 24, `Museum.visitorsToday = 1`.
  - If `Museum.curation` is 25 to 49, `Museum.visitorsToday = 3`.
  - If `Museum.curation` is 50 to 99, `Museum.visitorsToday = 6`.
  - If `Museum.curation` is 100 to 199, `Museum.visitorsToday = 10`.
  - If `Museum.curation` is 200 to 999, `Museum.visitorsToday = 15`.
  - If `Museum.curation` is 1000 or more, `Museum.visitorsToday = 20`.
  - `Museum.incomeToday = Museum.visitorsToday * 4`.
  - `Player.coins += Museum.incomeToday`.
  - If `Museum.grandOpeningDone` is false and `Museum.curation >= 100` and `Home.comfort >= 50`, set `Museum.grandOpeningDone = true` and `Player.coins += 1000`.

## Progression and difficulty

What grows: `Player.coins`, `Player.toolsOwned`, `Home.comfort`, `Museum.curation`, `Museum.activeCases`, and unlocked HomeRoom entries.

What unlocks, in intended order: Rod T2 at 90, Pickaxe T2 at 120, first extra Museum Case at 150, Home Parlor at 200, more Museum Cases at 150 each, Pickaxe T3 at 450, Rod T3 at 260, Home Library at 800, then endless furniture and museum completion.

Early game is easy because Sunberry yields 1 to 3, sells for 2, costs only 2 energy, regrows in 60 seconds, and at least 12 berry nodes are guaranteed within 10 tiles of the start. Ten Sunberry harvests can produce 20 to 60 coins, enough to approach Rod T2 or Pickaxe T2 by day 2.

Mid game becomes more effortful because Copper sells for 5 but requires 2 strikes with Pickaxe T1, Iron requires Pickaxe T2, and Glowberry is night-only.

Late game is harder because Gemstone requires Pickaxe T3, 4 strikes, and 720-second regrow; Coralfish only appears at Lake 2 and is most common at night; Home Comfort 50 and Museum Curation 100 require multiple high-value furniture pieces and many good exhibits.

The player is expected to run out of energy, fill Inventory, hit buyer daily caps, and fail fishing casts. Recovery is always non-lethal: Sleep restores energy to 100, selling frees inventory and coins, Dawn resets buyer caps and General stock, and better tools reduce strikes and cast difficulty.

## Feel

- Movement speed 4.0 tiles/second: fast enough to cross a 12-tile gap in 3 seconds, slow enough to choose between two nearby nodes.
- Acceleration 10.0 tiles/second squared and deceleration 12.0 tiles/second squared: starts feel responsive but stopping is crisp enough for precise reach.
- Reach 2.5 tiles: one clear step from a node, not long-range clicking.
- Harvest cooldown 0.4 seconds and energy cost 2: berry gathering should feel rapid, about 2.5 harvests per minute at full pace.
- Mine cooldown 0.45 seconds and Pickaxe T1 energy 5: Copper takes 2 strikes and about 1.35 seconds, Iron 3 strikes, Gemstone 4 strikes only with T3.
- Fishing cast 0.8 seconds, bite window 0.9, 0.8, 0.7 seconds for Rod T1, T2, T3, reel 0.5 seconds, fish cooldown 0.5 seconds: a full T1 cast cycle is about 2.3 seconds plus cooldown, so fishing is slower than berry picking and rewards better rods.
- Sweet zone 40, 55, 70 pixels on a 200-pixel bar: T1 is tight, T2 is comfortable, T3 is forgiving.
- Energy max 100, base regen 1 point per 5 seconds, comfort bonuses plus 0.2, plus 0.4, plus 0.6 per 5 seconds at Comfort 10, 25, 50: max regen is 1.6 points per 5 seconds, so home comfort matters by late game.
- Day length 300 seconds, dawn 0.10, shop open 0.10 to 0.95, museum settlement 0.95: one full day is 5 minutes, with a clear morning-to-night rhythm.
- No knockback: this is a collector game, not a combat game; movement feel comes from speed, reach, and cooldowns.
- Menu open transition 0.15 seconds: screens feel immediate without interrupting the walking loop.

# 5. CHARACTERS

Player:

- Silhouette and read at a glance: a compact 0.5 tile tall, 0.3 tile wide figure with a rounded hooded cloak, a brown backpack, and a small pale face. The player reads as a soft green cone with a brown pack and one pale face dot.
- Main colours: cloak `#55A35A`, pack `#B98A5B`, face `#FFF8EF`, boots `#6B4A33`.
- Facings: 8 directions.
- idle: 12-frame loop, body bob 0.03 tile, pack settle 1 degree.
- walk: 8-frame loop, stride 0.18 tile, body bob 0.04 tile, arms swing 20 degrees.
- forage: 6-frame reach, tool extends 0.6 tile, lean 5 degrees, sparkle effect.
- mine: 6-frame reach, pickaxe extends 0.6 tile, lean 5 degrees, rock white flash.
- fish: 6-frame cast, rod extends 0.6 tile, lean 3 degrees, bobber line appears.
- sleep: 10-frame sit and fade, used when Sleep action fires.
- invalid: 4-frame flinch, body recoil 0.06 tile, red tint `#E84A4F` alpha 0.30 for 0.12 seconds. Source visual hurt state is repurposed for denied actions.

Shopkeeper:

- Silhouette and read at a glance: a stout 0.55 tile tall, 0.35 tile wide figure with a wide apron, a small hat, and a counter stance. The shopkeeper reads as a yellow triangle body with a red hat and a pale face.
- Main colours: apron `#F4D16C`, hat `#E1554F`, face `#FFF8EF`, sleeves `#8C5E3C`.
- Facings: 4 directions.
- idle: 10-frame loop, hand wave 5 degrees, body bob 0.02 tile.
- serve: 8-frame gesture, arm raises 0.3 tile, counter glow `#FFE9A8` alpha 0.25.
- closed: 6-frame sit-down, used when a shop is closed or a purchase is denied. Source visual death state is repurposed.

Source visual player death and shopkeeper hurt/death animations are not T1. They are listed under T3.

# 6. AUDIO

All audio is generated with the Web Audio API. Audio unlocks on the first user gesture.

| Sound name | Recipe | Rule that plays it |
| --- | --- | --- |
| uiOpen | Square, 660 Hz, 0.06 seconds, attack 0.005, release 0.05 | Any screen opens: shop, inventory, homeMuseum, pause |
| uiClose | Square, 440 Hz, 0.05 seconds, attack 0.005, release 0.04 | Any screen closes back to world |
| step | Triangle, 180 Hz, 0.04 seconds, decay only | Play once every 0.4 seconds while player speed is greater than 0 |
| forageSuccess | Sine, 880 Hz, 0.09 seconds, decay | Successful berry harvest |
| forageEmpty | Triangle, 220 Hz, 0.12 seconds, decay | Use on empty berry bush or denied harvest |
| mineStrike | Square, 120 Hz, 0.05 seconds, decay | Successful ore strike that does not finish the node |
| mineComplete | Sawtooth, 180 Hz, 0.12 seconds, decay | Ore node finishes and item is added |
| fishCast | Sine, 440 Hz, 0.08 seconds, decay | Successful cast starts |
| fishBite | Square, 980 Hz, 0.05 seconds, decay | Fishing state enters bitten |
| fishCatch | Sine, 660 Hz, 0.12 seconds, decay | Successful catch resolves |
| fishFail | Sawtooth, 160 Hz, 0.15 seconds, decay | Failed catch or missed bite |
| pickup | Sine, 1046 Hz, 0.06 seconds, decay | Any item enters Inventory |
| sell | Square, 1568 Hz, 0.08 seconds, decay | Sell All gains coins |
| buy | Square, 880 Hz, 0.08 seconds, decay | Tool, furniture, case, or room purchase succeeds |
| deny | Sawtooth, 120 Hz, 0.10 seconds, decay | Any denied action: no energy, no space, closed shop, full bag, insufficient coins |
| place | Sine, 523 Hz, 0.08 seconds, decay | Furniture or exhibit placement succeeds |
| remove | Sine, 392 Hz, 0.08 seconds, decay | Furniture or exhibit removal succeeds |
| unlock | Sine, 1046 Hz, 0.20 seconds, decay | Home room unlock or museum case purchase |
| refund | Square, 784 Hz, 0.08 seconds, decay | Furniture refund succeeds |
| dawn | Sine, 523 Hz, 0.30 seconds, decay | Dawn runs |
| settlement | Triangle, 659 Hz, 0.15 seconds, decay | Museum Daily Settlement runs |
| grandOpening | Sine, 1318 Hz, 0.40 seconds, decay | Grand Opening fires |
| sleep | Sine, 330 Hz, 0.50 seconds, decay | Sleep action fires |
| weatherRainLoop | Noise buffer, 0.20 amplitude, looping | Rain state active |
| energyLow | Sawtooth, 110 Hz, 0.20 seconds, decay | Play once every 5 seconds while Player.energy is less than 20 |
| energyDepleted | Sawtooth, 80 Hz, 0.30 seconds, decay | Action denied because energy is too low |
| timerWarn | Square, 740 Hz, 0.10 seconds, decay | Final 25 percent of a progress bar or fishing bite window |
| doorOpen | Sine, 587 Hz, 0.15 seconds, decay | T2 door open state toggled |

# 7. UX

UI is HTML and CSS only, overlaying the Canvas 2D world. The page is one local file or one local directory, 960 by 540 viewport, zero network requests.

Screens are a state machine:

- `title` to `world`: Enter, New Game, or Continue if a localStorage save exists.
- `world` to `shop`: E or Space on an open Shopkeeper within 2.5 tiles, or touch Shop button near an open Shopkeeper.
- `world` to `inventory`: I or touch Inventory.
- `world` to `homeMuseum`: H or E on an active MuseumCase, or touch Home.
- `world` to `pause`: Escape or P, or touch Pause.
- `shop` to `world`: Escape, E, Space, or Close.
- `inventory` to `world`: Escape, E, Space, or Close.
- `homeMuseum` to `world`: Escape, E, Space, or Close.
- `pause` to `world`: Escape, Resume, or Close.
- `pause` to `title`: Quit.

In `world`:

- WASD and arrows move.
- Space or E uses the focused target.
- 1, 2, 3 select Foraging Hands, best owned Pickaxe, best owned Rod.
- I opens Inventory.
- H opens Home/Museum.
- Escape opens Pause.
- M toggles the T2 map overlay.

In `shop`:

- Buttons control Sell All, Buy Tool, Buy Furniture, Buy Case, Unlock Room, Refund Furniture.
- Buyer shops show Sell All rows.
- General shop shows Buy Tool, Buy Furniture, Buy Case, Unlock Room, Refund Furniture.

In `homeMuseum`:

- Tabs are Home and Museum.
- Home tab: choose room, choose slot, place/remove furniture.
- Museum tab: choose case, place/remove exhibit; choose decor slot, place/remove furniture.

HUD table:

| HUD element | Record field shown | Visible when |
| --- | --- | --- |
| Coins | Player.coins | world, shop, homeMuseum, pause |
| Energy bar | Player.energy / Player.maxEnergy | world, pause |
| Clock | Day.timeOfDay, Day.dayNumber | world, shop, homeMuseum, pause |
| Weather | Weather.type | world, pause |
| Selected tool | Player.selectedToolId | world |
| Inventory bar | Inventory.slots | world, shop, homeMuseum |
| Furniture bag count | Player.furnitureBagCount | world, shop, homeMuseum |
| Focused prompt | Player.focusedType, Player.focusedId | world when Player.focusedType is not none |
| Home comfort | Home.comfort | world, homeMuseum, pause |
| Museum curation | Museum.curation | world, homeMuseum, pause |
| Museum visitors/income | Museum.visitorsToday, Museum.incomeToday | world, homeMuseum, pause |
| Shop open state | Shopkeeper.open | shop |
| Shop daily cap | Shopkeeper.dailyBought, Shopkeeper.dailyCap | shop for berryBuyer, oreBuyer, fishBuyer |
| Tool stock | Shopkeeper.toolStock | shop for general |
| Furniture stock | Shopkeeper.furnitureStock | shop for general |
| Case cost | Museum.caseCost | shop for general, homeMuseum |
| Room unlock cost | HomeRoom.unlockCost | shop for general, homeMuseum |
| Timer bar | Player.fishingTimer, Player.biteMark, Player.toolCooldown | world during fishing or tool cooldown |

# 8. DEBUG API

`window.__game` exists as soon as the page loads. Every call is synchronous, mutates the real game, and returns plain data only. With a fixed seed, the same sequence of calls always yields the same state.

| Call | What it does | Returns |
| --- | --- | --- |
| `start()` | Leaves title, builds default world with seed 12345 if not built, enters `world`. Idempotent. | `getState()` |
| `seed(n)` | Sets RNG state to n, rebuilds full game state with accepted world seed, resets player, inventory, home, museum, day, weather, and ui. | `getState()` |
| `step(dt, n)` | Advances exactly n fixed ticks. `dt` must be 1/60. Runs update systems n times, then renders once. | `getState()` |
| `getState()` | Plain-data snapshot of records. Excludes `world.tiles` to keep 8 KB budget. | snapshot object |
| `verifyWorld()` | Runs World Generation verifier without mutating state. | object of check results |
| `setScreen(screen, shopId?)` | Sets `ui.screen` and optional `ui.shopId`. If opening shop, uses that shopkeeper id. | `getState()` |
| `moveDir(x, y)` | Sets persistent move direction to unit `(x, y)`, zero stops. | `{ move: [dx, dy] }` |
| `inputAction(name, arg?)` | Fires one-shot action: `interact`, `tool1`, `tool2`, `tool3`, `inventory`, `homeMuseum`, `pause`, `map`, `shop`, `close`. | `{ queued: name }` |
| `setPlayerPosition(x, y)` | Sets `Player.x` and `Player.y`, clamped to world bounds. | `{ x, y }` |
| `setTimeOfDay(t)` | Sets `Day.timeOfDay` to t in 0 to 1 without running crossing events. | `getState()` |
| `runDawn()` | Runs Dawn immediately. | `getState()` |
| `runSettlement()` | Runs Museum Daily Settlement immediately. | `getState()` |
| `setWeather(type)` | Sets weather type and modifiers without RNG. | `getState()` |
| `setCoins(n)` | Sets `Player.coins`. | `{ coins: n }` |
| `setEnergy(n)` | Sets `Player.energy`, clamped 0 to 100. | `{ energy: n }` |
| `setTool(toolId)` | Sets `Player.selectedToolId` if owned. | `{ selectedToolId }` |
| `clearInventory()` | Empts all inventory slots. | `getState()` |
| `setInventory(itemId, count)` | Sets total count of itemId in one slot, clamped 0 to 99. Other slots unchanged. | `getState()` |
| `placeNode(kind, itemId, x, y, lakeType?)` | Forces a ResourceNode at tile x,y, replacing any node at that tile. Uses roster values for stage, remainingHits, and regrowTimer. | node record or error |
| `setNode(id, stage, regrowTimer, remainingHits)` | Sets node fields directly. | node record or error |
| `setShopDailyBought(shopId, n)` | Sets a shopkeeper's dailyBought, clamped 0 to dailyCap. | `getState()` |
| `setShopStock(shopId, kind, itemId, count)` | Sets general tool or furniture stock count. kind is `tool` or `furniture`. | `getState()` |
| `shopSellAll(itemId)` | Calls Shop.sellAll. | coins gained |
| `shopBuyTool(toolId)` | Calls Shop.buyTool. | boolean |
| `shopBuyFurniture(furnitureId)` | Calls Shop.buyFurniture. | boolean |
| `shopBuyCase()` | Calls Shop.buyCase. | boolean |
| `shopUnlockRoom(roomId)` | Calls Shop.unlockRoom. | boolean |
| `shopRefundFurniture(instanceId)` | Calls Shop.refundFurniture. | boolean |
| `giveFurniture(furnitureId)` | Creates a FurnitureInstance in bag without buying. | instance record |
| `homePlace(instanceId, roomId, slotIndex)` | Calls Home.placeFurniture. | boolean |
| `homeRemove(instanceId)` | Calls Home.removeFurniture. | boolean |
| `museumPlaceExhibit(caseId, itemId)` | Calls Museum.placeExhibit. | boolean |
| `museumRemoveExhibit(caseId)` | Calls Museum.removeExhibit. | boolean |
| `museumPlaceFurniture(instanceId, decorSlot)` | Calls Museum.placeFurniture. | boolean |
| `museumRemoveFurniture(instanceId)` | Calls Museum.removeFurniture. | boolean |
| `setMuseumCaseActive(caseId, active)` | Sets a case active and updates Museum.activeCases. | `getState()` |
| `setMuseumCuration(n)` | Sets Museum.curation directly. | `{ curation: n }` |
| `setHomeComfort(n)` | Sets Home.comfort directly. | `{ comfort: n }` |
| `setGrandOpeningDone(done)` | Sets Museum.grandOpeningDone. | `getState()` |
| `setDoorOpen(open)` | T2: sets `ui.doorOpen`. | `getState()` |
| `renderFrame()` | Renders one frame immediately. | `{ drawCalls }` |

# 9. TESTS

All tests drive only section 8 calls. `g = window.__game`. State means the object returned by `g.getState()`. Equality is deep structural equality unless a range is stated.

Pre-state after `g.seed(12345); g.start();`:

- `tick = 0`
- `elapsed = 0`
- `paused = false`
- `screen = "world"`
- `day.timeOfDay = 0.10`
- `day.dayNumber = 1`
- `weather.type = "sunny"`
- `player.x = 58`
- `player.y = 58`
- `player.coins = 20`
- `player.energy = 100`
- `player.selectedToolId = "hands"`
- `world.width = 120`
- `world.height = 120`
- `verifyWorld()` all true
- berry nodes: 40
- ore nodes: 30
- fishing spots: 12
- shopkeepers: 4
- home rooms: 3
- museum cases: 12
- museum active cases: 4

1. Title to play and world validity.

Calls:

```js
g.seed(12345);
g.start();
let s = g.getState();
let v = g.verifyWorld();
```

Must find:

- `s.screen === "world"`
- `s.tick === 0`
- `s.elapsed === 0`
- `s.paused === false`
- `s.player.x === 58`
- `s.player.y === 58`
- `s.world.width === 120`
- `s.world.height === 120`
- `s.shopkeepers.length === 4`
- `s.nodes` contains 40 berry, 30 ore, 12 fishingSpot
- `s.home.rooms.length === 3`
- `s.museum.cases.length === 12`
- `s.museum.activeCases === 4`
- `v.allTrue === true`

2. Movement.

Calls:

```js
g.seed(12345);
g.start();
g.moveDir(0, -1);
g.step(1/60, 120);
let s = g.getState();
g.moveDir(0, 0);
g.step(1/60, 1);
let s2 = g.getState();
```

Must find:

- `s.player.y === 50`
- `s.player.x === 58`
- `s.player.facing === 0`
- `s.elapsed === 2`
- `s.tick === 120`
- `s2.player.y === 50`

3. Targeting and foraging.

Calls:

```js
g.seed(12345);
g.start();
g.placeNode("berry", "Sunberry", 60, 58);
g.inputAction("interact");
g.step(1/60, 1);
let s = g.getState();
g.step(1/60, 24);
let s2 = g.getState();
```

Must find:

- `s.player.focusedType === "node"` on the tick before action or immediately before use; after action, `s.player.toolCooldown === 0.4`
- `s.inventory.count("Sunberry")` is 1, 2, or 3
- `s.nodes` node at 60,58 has `stage === "empty"`
- node at 60,58 has `regrowTimer === 60`
- `s.player.energy === 98`
- `s2.player.toolCooldown === 0`
- `s2.tick === 25`

4. Mining.

Calls:

```js
g.seed(12345);
g.start();
g.placeNode("ore", "Copper", 60, 58);
g.setTool("pickaxe1");
g.inputAction("interact");
g.step(1/60, 1);
let s1 = g.getState();
g.step(1/60, 30);
g.inputAction("interact");
g.step(1/60, 1);
let s2 = g.getState();
```

Must find after first strike:

- node at 60,58 has `remainingHits === 1`
- node at 60,58 has `stage === "full"`
- `s1.inventory.count("Copper") === 0`
- `s1.player.energy === 95`
- `s1.player.toolCooldown === 0.45`

Must find after second strike:

- `s2.inventory.count("Copper") === 1`
- node at 60,58 has `stage === "empty"`
- node at 60,58 has `regrowTimer === 240`
- `s2.player.energy === 90`
- `s2.player.toolCooldown === 0.45`

5. Fishing.

Calls:

```js
g.seed(12345);
g.start();
g.placeNode("fishingSpot", null, 60, 58, 1);
g.setTool("rod1");
g.setTimeOfDay(0.5);
g.inputAction("interact");
g.step(1/60, 1);
let s1 = g.getState();
g.step(1/60, 47);
let s2 = g.getState();
g.step(1/60, 27);
let s3 = g.getState();
g.inputAction("interact");
g.step(1/60, 1);
let s4 = g.getState();
g.step(1/60, 29);
let s5 = g.getState();
```

Must find:

- `s1.player.fishingState === "casting"`
- `s1.player.energy === 95`
- `s2.player.fishingState === "bitten"`
- `s2.player.biteMark === 0`
- `Math.abs(s3.player.biteMark - 100) < 0.1`
- `s4.player.catchSuccess === true`
- `s4.player.fishingState === "reeling"`
- `s5.player.fishingState === "idle"`
- `s5.player.toolCooldown === 0.5`
- `s5.inventory.count("Minnow") + s5.inventory.count("Sunfish") === 1`
- At day time 0.5 and lakeType 1, the caught fish must be Minnow or Sunfish.

6. Energy regen.

Calls:

```js
g.seed(12345);
g.start();
g.setEnergy(0);
g.step(1/60, 300);
let s = g.getState();
```

Must find:

- `s.player.energy === 1`
- `s.home.comfort === 0`

7. Selling.

Calls:

```js
g.seed(12345);
g.start();
g.setTimeOfDay(0.5);
g.clearInventory();
g.setInventory("Sunberry", 10);
g.setScreen("shop", "berryBuyer");
let coins = g.shopSellAll("Sunberry");
let s = g.getState();
```

Must find:

- `coins === 20`
- `s.player.coins === 40`
- `s.inventory.count("Sunberry") === 0`
- berryBuyer shopkeeper `dailyBought === 10`
- berryBuyer shopkeeper `open === true`

8. Buying tool.

Calls:

```js
g.seed(12345);
g.start();
g.setCoins(120);
g.setTool("pickaxe1");
g.setScreen("shop", "general");
let bought = g.shopBuyTool("pickaxe2");
let s1 = g.getState();
g.setCoins(120);
let denied = g.shopBuyTool("pickaxe2");
let s2 = g.getState();
```

Must find:

- `bought === true`
- `denied === false`
- `s1.player.coins === 0`
- `s1.player.toolsOwned` includes `pickaxe2`
- `s1.player.selectedToolId === "pickaxe2"`
- general toolStock pickaxe2 count is 0
- `s2.player.coins === 120`
- `s2.player.toolsOwned` includes `pickaxe2`

9. Buying furniture.

Calls:

```js
g.seed(12345);
g.start();
g.setCoins(15);
g.setScreen("shop", "general");
let bought = g.shopBuyFurniture("woodenStool");
let s1 = g.getState();
g.setCoins(15);
g.setShopStock("general", "furniture", "woodenStool", 0);
let denied = g.shopBuyFurniture("woodenStool");
let s2 = g.getState();
```

Must find:

- `bought === true`
- `denied === false`
- `s1.player.coins === 0`
- `s1.player.furnitureBagCount === 1`
- one FurnitureInstance has `definitionId === "woodenStool"` and `location === "bag"`
- general furnitureStock woodenStool count is 2
- `s2.player.coins === 15`
- `s2.player.furnitureBagCount === 1`

10. Home placement and comfort.

Calls:

```js
g.seed(12345);
g.start();
let inst = g.giveFurniture("woodenStool");
let placed = g.homePlace(inst.instanceId, "home1", 0);
let s1 = g.getState();
let removed = g.homeRemove(inst.instanceId);
let s2 = g.getState();
```

Must find:

- `placed === true`
- `removed === true`
- `s1.player.furnitureBagCount === 0`
- `s1.home.rooms` room `home1` slot 0 is `inst.instanceId`
- `s1.home.rooms` room `home1` roomComfort is 1
- `s1.home.comfort === 1`
- `s2.player.furnitureBagCount === 1`
- `s2.home.comfort === 0`

11. Museum exhibit and curation.

Calls:

```js
g.seed(12345);
g.start();
g.setInventory("Sunberry", 1);
let placed = g.museumPlaceExhibit(1, "Sunberry");
let s1 = g.getState();
let removed = g.museumRemoveExhibit(1);
let s2 = g.getState();
```

Must find:

- `placed === true`
- `removed === true`
- `s1.museum.cases` case 1 itemId is `Sunberry`
- `s1.museum.cases` case 1 exhibitValue is 1
- `s1.museum.curation === 1`
- `s1.inventory.count("Sunberry") === 0`
- `s2.museum.curation === 0`
- `s2.inventory.count("Sunberry") === 1`

12. Museum furniture and curation.

Calls:

```js
g.seed(12345);
g.start();
let inst = g.giveFurniture("moonFishDisplay");
let placed = g.museumPlaceFurniture(inst.instanceId, 0);
let s1 = g.getState();
let removed = g.museumRemoveFurniture(inst.instanceId);
let s2 = g.getState();
```

Must find:

- `placed === true`
- `removed === true`
- `s1.museum.curation === 6`
- `s1.museum.decorSlots[0] === inst.instanceId`
- `s2.museum.curation === 0`
- `s2.museum.decorSlots[0] === null`

13. Settlement and Grand Opening.

Calls:

```js
g.seed(12345);
g.start();
g.setMuseumCuration(50);
g.setCoins(100);
g.runSettlement();
let s1 = g.getState();
g.setMuseumCuration(100);
g.setHomeComfort(50);
g.setGrandOpeningDone(false);
g.runSettlement();
let s2 = g.getState();
```

Must find:

- `s1.museum.visitorsToday === 6`
- `s1.museum.incomeToday === 24`
- `s1.player.coins === 124`
- `s1.museum.grandOpeningDone === false`
- `s2.museum.visitorsToday === 10`
- `s2.museum.incomeToday === 40`
- `s2.museum.grandOpeningDone === true`
- `s2.player.coins === 1164`

14. Weather modifiers.

Calls:

```js
g.seed(12345);
g.start();
g.setWeather("rain");
let s1 = g.getState();
g.setWeather("snow");
let s2 = g.getState();
```

Must find:

- `s1.weather.type === "rain"`
- `s1.weather.berryYieldBonus === 1`
- `s1.weather.fishSweetZoneBonus === 10`
- `s1.weather.berryRegrowDelta === -15`
- `s2.weather.type === "snow"`
- `s2.weather.oreYieldBonus === 1`
- `s2.weather.fishSweetZoneBonus === -10`
- `s2.weather.fishBiteWindowDelta === -0.1`
- `s2.weather.berryRegrowDelta === 30`

15. Sleep and dawn.

Calls:

```js
g.seed(12345);
g.start();
g.setPlayerPosition(57, 57);
g.setTimeOfDay(0.8);
g.setHomeComfort(50);
g.setCoins(10);
g.inputAction("interact");
g.step(1/60, 1);
let s = g.getState();
```

Must find:

- `s.day.dayNumber === 2`
- `s.day.timeOfDay === 0.10`
- `s.player.energy === 100`
- `s.player.coins === 40`
- `s.weather.type` is one of `sunny`, `rain`, `snow`
- `s.weather` modifiers match the rolled type
- all shopkeeper `dailyBought` are 0
- general toolStock is reset
- general furnitureStock is reset to 3 for every furniture id

16. Pause.

Calls:

```js
g.seed(12345);
g.start();
g.moveDir(0, -1);
g.step(1/60, 60);
let s1 = g.getState();
g.inputAction("pause");
g.step(1/60, 10);
let s2 = g.getState();
g.inputAction("pause");
g.step(1/60, 1);
let s3 = g.getState();
```

Must find:

- `s1.elapsed === 1`
- `s1.player.y === 54`
- `s2.paused === true`
- `s2.tick === 70`
- `s2.elapsed === 1`
- `s2.player.y === 54`
- `s3.paused === false`
- `s3.elapsed === 1 + 1/60`

17. Determinism.

Let sequence S be:

```js
g.seed(12345);
g.start();
g.moveDir(0, -1);
g.step(1/60, 60);
g.moveDir(0, 0);
g.placeNode("berry", "Sunberry", 60, 58);
g.inputAction("interact");
g.step(1/60, 10);
g.placeNode("ore", "Copper", 62, 58);
g.setTool("pickaxe1");
g.inputAction("interact");
g.step(1/60, 40);
g.placeNode("fishingSpot", null, 60, 60, 1);
g.setTool("rod1");
g.inputAction("interact");
g.step(1/60, 80);
```

Calls:

```js
g.seed(12345);
// run S
let a = g.getState();
g.seed(12345);
// run S again
let b = g.getState();
g.seed(777);
// run S
let c = g.getState();
```

Must find:

- deep equality `a === b`
- `a !== c`
- `a.world.seed` may differ from 12345 only if the verifier re-rolled; if re-rolled, `a.world.seed === b.world.seed`
- `a.rngState === b.rngState`

18. No stray randomness.

Calls:

```js
// Harness installs spies on Math.random and Date.now before these calls.
g.seed(12345);
g.start();
for (let i = 0; i < 1200; i++) {
  g.step(1/60, 1);
}
```

Must find:

- spy count for `Math.random` in game code is 0
- spy count for `Date.now` in game code is 0

19. Budgets.

Calls:

```js
g.seed(12345);
g.start();
g.step(1/60, 1);
let s = g.getState();
let json = JSON.stringify(s);
```

Must find:

- `s.render.drawCalls <= 3000`
- `json.length <= 8192`
- page issues 0 fetch or XHR requests
- tick time for 60 consecutive `g.step(1/60, 1)` calls is 2 milliseconds or less per tick in harness
- total file size is 200 KB or fewer

SCREENSHOTS table:

| Screen / state | How to reach it | What a person must see there |
| --- | --- | --- |
| Spawn day view | Load the game or `g.seed(12345); g.start();` | Player at 58,58, home, museum, and market visible, three resource regions readable, no node on water or interior |
| Berry Grove entry | Walk west to berry circle center 30,90 | Green ground, red berry bushes, at least 10 bushes visible, leaf patches visible |
| Berry harvest | Stand at a full bush and press E or Space | Bush pulse, red particles, berry pickup pop, inventory slot filled |
| Empty berry bush | View a harvested bush before regrow | No red berries, darker leaves `#2F5F33`, empty state visible |
| Mine entry | Walk east to mine circle center 90,25 | Gray-brown ground, visible ore nodes, Copper, Iron, or Gemstone crystals readable |
| Ore mine | Stand at a full ore node and press E or Space | White flash, gray shards, small screen shake, ore pickup pop |
| Mined ore node | View a mined node | Hollow dark rock `#4A4E53`, no crystals, no glint |
| Lake fishing | Walk to Lake A or Lake B sand ring | Cyan water, sand shore, reeds, bobber or fishing bar |
| Fish catch | Use fishing action at a fishing spot and reel in sweet zone | Bobber dip, cyan droplets, fish pickup wiggle |
| Shop transaction | Approach a buyer and open the shop panel | Shopkeeper, stall, shop panel with item rows, buttons, coin count, header colour `#E1554F` |
| Shop button hover | Move pointer over a shop button | Button colour `#8FD45B`, scale 1.03, label readable |
| Home interior | Open Home tab | Warm room, room slots, placed furniture, comfort value |
| Museum interior | Open Museum tab | Cream museum, display cases, decor slots, curation value |
| Furniture placed | Place furniture in a valid home or museum slot | Solid furniture object, selection ring, no red ghost, notification toast |
| Valid placement ghost | Select furniture and hover over a valid slot | Transparent furniture alpha 0.45, green outline `#7FE37F`, green pulse |
| Invalid placement ghost | Select furniture and hover over an invalid slot | Transparent furniture alpha 0.45, red outline `#E84A4F`, red shake |
| Door open state | T2: `g.setDoorOpen(true);` | Door rotated -80 degrees, warm light spill triangle, path visible through doorway |
| Night state | `g.setTimeOfDay(0.8);` | Moonlight, darker fog, window/lamp glow, vignette strength 0.28, path edges readable |
| Low energy state | `g.setEnergy(10);` | Energy bar fill `#FF6B4A`, red vignette, edge pulse |
| Rain state | `g.setWeather("rain");` | Rain streaks, puddle decals, wet ground darkening, grain strength 0.07, rain fog colour `#9FB6C9` |
| Inventory filled state | Collect at least 3 item types or `g.setInventory` for Sunberry, Copper, Minnow | Inventory bar visible, filled slots with distinct berry, ore, and fish icons |

# 10. BUILD ORDER

| Milestone | Adds | Land check |
| --- | --- | --- |
| M0 — Page | Canvas, title screen, `window.__game`, loop, RNG, world generation, verifier | Test 1 |
| M1 — Movement | Input, Player, World geometry, render world pass, camera | Test 2 |
| M2 — Collecting | Foraging, Mining, Inventory, resource nodes, energy | Tests 3, 4, 6 |
| M3 — Fishing | Fishing state machine, fishing spots, fish table, bobber/bar visual | Test 5 |
| M4 — Economy | Shopkeepers, Selling, Buying, daily caps, general stock, dawn reset | Tests 7, 8, 9, 15 |
| M5 — Home and Museum | Home rooms, furniture placement, museum cases, exhibits, curation, settlement, grand opening | Tests 10, 11, 12, 13 |
| M6 — Hardening | Weather, pause, determinism, no stray randomness, budgets, audio, UX polish | Tests 14, 16, 17, 18, 19 |

# 11. DEFINITION OF DONE

| Requirement | Checks that make it true | Screenshot rows |
| --- | --- | --- |
| An open world collector game | Test 1 world validity; Test 2 movement; Test 3 foraging; Test 4 mining; Test 5 fishing | Spawn day view, Berry Grove entry, Mine entry, Lake fishing |
| The player walks around | Test 2 movement, facing, pause | Spawn day view |
| Collecting resources | Test 3 inventory gain; Test 4 inventory gain; Test 5 fish gain | Berry harvest, Ore mine, Fish catch, Inventory filled state |
| Harvest berries | Test 3 foraging rules; Test 14 weather berry effect | Berry harvest, Empty berry bush, Rain state |
| Mine ores | Test 4 mining rules; Test 14 weather ore effect | Ore mine, Mined ore node |
| Fish fish | Test 5 fishing rules; Test 14 weather fishing effect | Lake fishing, Fish catch |
| Sell them to a shop keeper for each type | Test 7 selling; Test 15 dawn daily cap reset | Shop transaction |
| Buy furniture to decorate their home | Test 9 buy furniture; Test 10 home placement and comfort | Furniture placed, Valid placement ghost, Home interior |
| Buy furniture to decorate a small museum type building | Test 12 museum furniture; Test 11 exhibit; Test 13 curation settlement | Museum interior, Furniture placed |
| Added: day/time economy, energy limits, weather, tools, progression, museum exhibits, daily buyer caps | Tests 6, 7, 8, 9, 13, 14, 15, 16 | Night state, Shop transaction, Museum interior |
| Added: readable collector feedback and audio | Test 19 render budget; audio table rules; visual feedback rules | Berry harvest, Ore mine, Fish catch, Shop button hover |
| Added: debug API and deterministic tests | Tests 1 through 19; section 8 calls | all screenshot rows |

# A. SANITY

Checks made against sections 2, 4, 8, and 9:

- Every field a rule reads or writes is in the global context: `World`, `Player`, `Inventory`, `ResourceNode`, `Shopkeeper`, `FurnitureInstance`, `Home`, `HomeRoom`, `Museum`, `MuseumCase`, `Day`, and `Weather` fields all exist in `ctx`. Result: closes.
- Every place, thing, or kind a rule names is placed by a generator or listed in a roster: berry, ore, and fishingSpot nodes are generated; shopkeepers, home rooms, museum cases, tools, resources, and furniture are in rosters. Result: closes.
- Consumables close along the core loop: 40 berry nodes, 30 ore nodes, and 12 fishing spots against buyer daily caps 60, 40, and 50; 20 inventory slots with 99 count against max yields; 12 furniture bag slots against 12 furniture definitions; 100 energy against 2, 3 to 5, and 5 action costs; 12 museum cases and 6 decor slots against curation targets. Result: closes.
- Spawn against clear timing closes and still bites: berry regrow minimum 15 and base 60 to 180 seconds against a 300-second day; ore regrow 240 to 720 seconds across one to multiple days; fishing cast 0.8 plus reel 0.5 plus cooldown 0.5 against a 300-second day; shop open window 0.10 to 0.95 gives 255 seconds for selling. Result: closes.
- Drain against refill timing closes and still bites: base energy regen is 1 point per 5 seconds; comfort bonus raises it to 1.6 points per 5 seconds; action costs are 2, 3 to 5, and 5, so energy limits actions without making the core loop impossible. Result: closes.
- Travel time against distance closes and still bites: movement speed 4.0 tiles/second, reach 2.5 tiles, world 120 by 120 tiles, cross-region travel is several seconds but not minutes. Result: closes.
- End-condition clock against expected clear time: there is no forced end; Grand Opening is optional and requires Museum Curation 100 and Home Comfort 50, both reachable by furniture and exhibits. Result: closes.
- Every call section 9 makes is in section 8: `seed`, `start`, `getState`, `verifyWorld`, `moveDir`, `step`, `placeNode`, `inputAction`, `setTool`, `setTimeOfDay`, `setEnergy`, `clearInventory`, `setInventory`, `setScreen`, `shopSellAll`, `setCoins`, `shopBuyTool`, `setShopStock`, `shopBuyFurniture`, `giveFurniture`, `homePlace`, `homeRemove`, `museumPlaceExhibit`, `museumRemoveExhibit`, `museumPlaceFurniture`, `museumRemoveFurniture`, `setMuseumCuration`, `setHomeComfort`, `setGrandOpeningDone`, `runSettlement`, `setPlayerPosition`, `setWeather`, and `renderFrame` all exist. Result: closes.
- No placeholder in angle brackets remains: the document contains no unfilled angle-bracket placeholders. Result: closes.