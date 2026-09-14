# engineering.md

**Decision: 2D top-down, rendered to a single `<canvas>` with the Canvas 2D API.**

---

## 1. CONVENTIONS

### Units, axes, origin
- One unit = one pixel at world scale 1. There is no separate world scale; the camera applies a single `cam.zoom = 1` float (visual colleague may style, the number is canonical 1 for tests).
- X axis points right, Y axis points down. "Up" on screen = negative Y. There is no Z.
- Origin (0, 0) is the center of the world square. World bounds: `[-2000, 2000] × [-2000, 2000]`, i.e. a 4000×4000 unit square.
- The grid is square tiles of 32×32 units. Grid tile `(gx, gy)` covers the rect `[gx·32, gy·32, gx·32+32, gy·32+32]`. Tile centers are at `(gx·32+16, gy·32+16)`.
- The player is treated as a point (no radius for logic); all overlap/occupancy tests use the point and stored rects.

### Camera
- The camera is the player's position. Camera center = `player.x, player.y`, exactly, every frame. Canvas viewport is 960×540 units. A world point `p` draws at screen `s = (p − player) · cam.zoom + (480, 270)`.

### Loop and timing
- Fixed step, `dt = 1/60` s (60 ticks per second). Never any other dt in logic.
- Real-time loop: `requestAnimationFrame` accumulates elapsed real time and runs `floor(acc / dt)` ticks, keeping the remainder. The accumulator is clamped so a single frame runs **at most 3 ticks** (spiral-of-death rule, see §7).
- `pause = true` (key P): `step` still increments `tick` but skips all update systems; `elapsed` does not advance.
- Update order per tick, hard-coded in one list `UPDATE_ORDER = ["player","harvest","fish","shop","place"]`; nothing may reorder it.
- Rendering runs exactly once per rAF, after all catch-up ticks, reading the latest committed state. Rendering may cull and drop decorative layers; it may not mutate gameplay state.

### Randomness
- One seeded random source, named **RNG** (mulberry32, 32-bit state, exposed as `ctx.rngState`). It exposes `nextInt(lo, hi)` (lo inclusive, hi exclusive), `pick(arr)`, `range(lo, hi)` (float).
- World generation consumes RNG first (nodes, then water, then fish pool order), then gameplay. Nothing else — not `Math.random()`, not `Date` — may produce a value that affects state. A test that installs spies on `Math.random` and `Date.now` and asserts zero calls during `seed`+`step` must pass.

### Fixed world anchors (these are engineering constants, not gameplay values)
- **Home** building rect: `[-320, -128]` to `[-128, 64]` (interior 192×192).
- **Museum** building rect: `[32, 64]` to `[224, 192]` (interior 192×128).
- **Fish pond**: exactly one water region, water tile `(7, 4)` → rect `[224, 128, 256, 160]`, center `(240, 144)`. The `water` array of the world always contains this tile; tests may add more.
- **Shopkeeper** entity at `(206, 206)` (outside the home).
- **Player spawn**: home center `(−224, −32)`.
- **Interaction range** (point-to-rect distance for nodes and shopkeeper): 64 units.
- **Fishing range**: point-to-tile-rect distance to any water tile ≤ 80 units.
- **Furniture tile**: a placed furniture occupies one 48×48 unit tile; furniture tile `(fx, fy)` covers `[fx·48, fy·48, fx·48+48, fy·48+48]`.

### Controls

| Input | Action | Notes |
|---|---|---|
| W / ArrowUp | move north (−Y) | |
| A / ArrowLeft | move west (−X) | |
| S / ArrowDown | move south (+Y) | |
| D / ArrowRight | move east (+X) | |
| E | `interact` | harvest in-range node, else open/close shop if in range of a shopkeeper, else no-op |
| F | `fishToggle` | start fishing if near water and idle; stop early if active |
| 1 / 2 / 3 / 4 | `place 1` … `place 4` | place furniture type `f1`..`f4` at the furniture tile under the player, if carried |
| P | `pause` | toggle |
| M | `map` | toggle full-map overlay; render-only, never mutates state |
| Touch | drag anywhere = virtual joystick (move); on-screen buttons = E, F, 1–4, P | same actions, same names |

Movement is 8-directional: the current move direction is the unit vector of the pressed combination (diagonals normalized: `(dx, dy) / sqrt(dx²+dy²)`).

---

## 2. MODULES

| Module | Responsibility |
|---|---|
| `RNG` | The single seeded random source |
| `Input` | Raw keys/touch → the `input` record; consumes it once per tick |
| `Player` | Movement, facing, bounds, interact resolution |
| `World` | World generation from seed; node/water/building storage; occupancy grid |
| `Harvest` | Node harvesting state machine |
| `Fish` | Fishing state machine |
| `Inventory` | Item counts and capacity |
| `Shop` | Sell/buy, stock, cooldown |
| `Place` | Furniture placement rules |
| `Render` | Canvas 2D drawing, culling, budget tracking |

No module imports another. The **only** shared object is the context below.

### GLOBAL CONTEXT

```js
// The one object every module reads and writes. Nothing else is shared.
ctx = {
  // --- rng ---
  rng:        null,          // RNG instance (mulberry32), created by seed()
  rngState:   0,             // number, the 32-bit seed, mirrored from rng

  // --- flow ---
  tick:       0,             // number, fixed steps executed (counted even while paused)
  elapsed:    0.0,           // number, seconds of unpause-fixed time
  paused:     false,         // bool

  // --- input (written by Input module only) ---
  move:       [0, 0],        // number[2], current unit move vector

  // --- player ---
  player: {
    x:        -224,          // number, home center
    y:        -32,           // number
    facing:   [0, -1],       // number[2], last non-zero move dir
    coins:    10,            // number
    inventory:{ berries:0, ore:0, fish:0, f1:0, f2:0, f3:0, f4:0 } // numbers, ints
  },
  inventoryCapacity: 60,     // number, <inventory capacity>, total items allowed

  // --- world (rebuilt by seed) ---
  world: {
    seed:     0,             // number, integer
    berryNodes: [],          // { id:int, x:number, y:number, count:int, progress:number }
    oreNodes:   [],          // same shape
    water:      [],          // { gx:int, gy:int }  (always contains {gx:7, gy:4})
    buildings:  [ { id:0, kind:"home", x0:-320, y0:-128, x1:-128, y1:64 },
                  { id:1, kind:"museum", x0:32, y0:64, x1:224, y1:192 } ],
    shopkeepers:[ { id:0, x:206, y:206 } ]
  },

  // --- gameplay ---
  harvest: { nodeId: -1, type: "", targetX: 0, targetY: 0 }, // active E-hold chain
  fish:    {
    active:   false,         // bool
    progress: 0.0,           // number, 0..1
    waterRef: null,          // {gx,gy} of the water tile being fished, or null
    pool:     []             // { x:number, y:number } pending fish spawns, max 12
  },
  shop:    {
    openShopId:  -1,         // number, which shopkeeper's stall is open, -1 = none
    cooldown:    0.0,        // number, seconds remaining before next sell/buy
    stock:       { f1:5, f2:5, f3:5, f4:5 } // numbers, global stock per type, <shop stock>
  },
  furniture:[],              // { id:int, type:"f1".."f4", x:number, y:number,
                             //   w:48, h:48, place:"home"|"museum" }

  // --- render budget (written by Render, read by tests) ---
  render: { drawCalls: 0 }   // number, canvas ops last frame
};
```

Constants module (read-only, defined once at load): `DT = 1/60`, `WORLD = {min:-2000, max:2000}`, `GRID = 32`, `FGRID = 48`, `INTERACT_RANGE = 64`, `FISH_RANGE = 80`, `FISH_TIME = <fishing duration>`, `HARVEST_TIME = <harvest duration>`, `SHOP_COOLDOWN = <shop cooldown>`.

### Exports

**RNG**
- `create(seed: number) → { next(): number; nextInt(lo,hi): number; pick(arr): T; range(lo,hi): number; getState(): number; setState(n): void }` — mulberry32 factory; state fully serializable.

**Input**
- `poll() → void` — called at tick start; reads the latest key/touch state, writes `ctx.move`, and sets one-shot flags on `ctx._pending` (interact/fish/place/pause). One-shot flags are consumed and cleared by `consume()`.
- `consume() → { move:[dx,dy], interact:bool, fish:bool, place:0-4, pause:bool, map:bool }` — the only way other modules see input; called exactly once per tick.

**Player**
- `update(dt) → void` — applies `ctx.move · <player speed> · dt`, clamps to world bounds, updates `facing`.
- `nearestInteractable(x, y, range) → { kind:"node"|"shop", id, x, y } | null` — point-to-rect distance to in-range nodes (count > 0) and shopkeepers; nearest wins, ties broken by id.

**World**
- `generate(seed: number) → void` — resets `ctx.world`, `ctx.fish.pool`, node id counters; draws `<berry nodes>` berry and `<ore nodes>` ore nodes via rejection sampling (reject: out of bounds, inside either building rect inflated by 32, within 48 of the player spawn, within 48 of the pond, within 48 of any other node; max 1000 draws per node, then fall back to the next grid line), appends water tile `{gx:7,gy:4}`, reseed fish pool order. Deterministic: same seed → same world.
- `tileOf(x, y) → [gx, gy]` and `tileRect(gx, gy) → {x0,y0,x1,y1}` — grid math, the only grid math in the codebase.
- `inRect(px, py, r) → bool`, `pointToRect(px, py, r) → number` — shared geometry.
- `rebuildOccupancy() → void` — rebuilds the furniture occupancy grid (48-unit tiles, `Map` keyed `"fx,fy"`) from `ctx.furniture`.

**Harvest**
- `update(dt) → void` — if an interact one-shot fired and a node is in range, set `ctx.harvest = {nodeId, type, targetX, targetY}` and start progress 0; while active, `progress += dt / HARVEST_TIME`; on ≥ 1, add `<berries per harvest>` / `<ore per harvest>` via Inventory, decrement the node, clear the target (node with count 0 is no longer interactable).
- `onInteract() → void` — resolves the E action through `Player.nearestInteractable`.

**Fish**
- `update(dt) → void` — if active, `progress += dt / FISH_TIME`; on ≥ 1: `inventory.fish += 1`, spawn one fish position at the water tile center plus a ±12-unit offset from RNG, push into `fish.pool` (capped, oldest dropped), set `active=false, progress=0`.
- `toggle() → void` — start (requires idle and point-to-tile ≤ FISH_RANGE of some water tile, else sets `ctx._fishErr`), or stop early (fish lost).
- `nearestWater(x, y) → [gx,gy] | null` — smallest point-to-tile-rect distance ≤ FISH_RANGE; ties broken by lower (gy then gx).

**Inventory**
- `add(type, n) → number` — add, clamp so total ≤ `inventoryCapacity`; returns items actually added.
- `take(type, n) → bool` — remove if available, else false (does not modify).
- `total() → number`.
- `count(type) → number`.

**Shop**
- `update(dt) → void` — decrement `ctx.shop.cooldown` by dt, floor at 0.
- `openToggle(x, y) → void` — opens the stall of the nearest shopkeeper in range (sets `openShopId`), or closes it.
- `sellAll(type) → number` — if `openShopId ≥ 0` and `cooldown = 0`: coins += `inventory[type] · <sell price: type>`, items removed, `cooldown = SHOP_COOLDOWN`; returns coins gained, 0 otherwise.
- `buy(type) → bool` — if `openShopId ≥ 0`, `cooldown = 0`, `stock[type] > 0`, `player.coins ≥ <buy price: type>` and `Inventory.total() < capacity`: pay, decrement stock, add 1 item; returns true.

**Place**
- `update(dt) → void` — no state of its own; exists in UPDATE_ORDER so placement is idempotent per tick.
- `onPlace(type) → bool` — furniture tile under `player`; succeeds iff type in `f1..f4`, `inventory[type] > 0`, point inside home or museum interior, and tile not occupied; on success: decrement inventory, push record, `rebuildOccupancy()`; returns true/false.
- `occupies(px, py) → bool` — furniture-tile occupancy test (used to keep the player point from being pushed into furniture by movement is **not** required; player may stand on furniture, furniture may not stack).

**Render**
- `frame() → number` — one draw pass in fixed order: ground grid, water, buildings, nodes, furniture, shopkeepers, player, fish, UI text, map overlay if on; culls to viewport + 192-unit margin; counts every `ctx2d` draw op into `ctx.render.drawCalls`; if the count would exceed the budget (§3), drops layers in order: ground grid → water shimmer → fish → node highlights. Returns the count.

---

## 3. BUDGETS

Numbers below are asserted by tests, not aspirations.

- **Frame time**: one tick of all updates ≤ **2 ms** (measured in the test harness, 60 consecutive `step(dt,1)` calls). A real frame runs ≤ 3 catch-up ticks (§1 rule).
- **Canvas operations per frame**: ≤ **3000**. `frame()` returns the count; a test asserts `getState().render.drawCalls ≤ 3000` at full world density.
- **Entity caps** (hard, generators refuse to exceed; spawns from §4 error):
  - berryNodes ≤ **200**, oreNodes ≤ **200**
  - water tiles ≤ **512** (default world: exactly **1**, the pond)
  - fish.pool ≤ **12**
  - furniture ≤ **24**
  - shopkeepers **1**, buildings **2**
- **Pools**: fish pool preallocated length 12; node arrays preallocated to 400; occupancy `Map` max 24 entries.
- **Memory**: `getState()` snapshot ≤ **8 KB** of JSON at caps; total JS object heap of the game ≤ **5 MB** (harness measures `performance.memory` delta if exposed, else object graph walk); the whole game in one directory, total file size ≤ **200 KB**, zero network requests (a test asserts the page issues 0 fetch/XHR).
- **State size at rest**: default seed world has exactly `<berry nodes>` + `<ore nodes>` nodes, 1 water tile, 0 fish, 0 furniture.

---

## 4. DEBUG API

`window.__game` exists as soon as the page loads. Every call is **synchronous**, mutates the real game, and returns **plain data only** (JSON-serializable: numbers, strings, booleans, null, arrays, plain objects). With a fixed seed, the same sequence of calls always yields the same state.

| Call | What it does | Returns |
|---|---|---|
| `start()` | Leaves the title screen and enters play; builds default world (seed 12345) if not built yet. Idempotent. | `getState()` |
| `seed(n)` | Sets `rng` (RNG) and `rngState` to `n`; rebuilds the world (`World.generate`), the fish pool, the occupancy grid; resets player to spawn, coins 10, inventory empty, harvest/fish/shop state, `tick`, `elapsed`, `paused`. Does not leave the title (use `start()` after). | `getState()` |
| `step(dt, n)` | Advances exactly `n` fixed ticks of `dt` seconds without real time; runs the `UPDATE_ORDER` systems `n` times; then draws exactly once. Paused ticks increment `tick` only. | `getState()` |
| `setTime(t)` | Advances the simulation to `elapsed = t` using fixed `DT` ticks, **without drawing**. | `getState()` |
| `getState()` | Plain-data snapshot of every record: `tick, elapsed, paused, rngState, move, player{x,y,facing,coins,inventory}, world{seed, berryNodes[], oreNodes[], water[], buildings[], shopkeepers[]}, harvest, fish{active,progress,waterRef,pool[]}, shop{openShopId,cooldown,stock}, furniture[], render{drawCalls}`. No functions, no DOM, no cycles. | the snapshot object |
| `moveDir(x, y)` | Sets the persistent move direction to unit `(x, y)` (zero = stop). Persists until the next call. | `{ move: [dx, dy] }` |
| `inputAction(name, arg?)` | Fires the one-shot action for one tick: `interact` (E), `fish` (F), `pause` (P), `place <1-4>` (arg = 1..4). The action is consumed by the very next tick of `step`/`setTime`. | `{ queued: name }` |
| `spawnBerry(x, y, count)` | Adds a berry node at the point (default `count = <berry node count>`). Errors: out of bounds, inside a building (inflated 32), within 48 of the player spawn, the pond, or another node — same rules as generation. | the node record, or `{ error: "…" }` |
| `spawnOre(x, y, count)` | As above for ore (default `<ore node count>`). | node record or `{ error }` |
| `spawnWater(gx, gy)` | Adds a water tile (idempotent). Errors: out of world, or within 48 units of the player spawn point. | `{ gx, gy }` or `{ error }` |
| `placeFurniture(type, fx, fy)` | Places furniture of type at furniture tile (validates bounds, interior, occupancy, inventory) — same rules as the `onPlace` path but with an explicit tile. | the furniture record, or `{ error: "out_of_bounds" \| "not_in_interior" \| "occupied" \| "not_carried" }` |
| `setInventory(items)` | Sets `player.inventory` exactly (clamped to capacity). | `{ inventory: …, total: n }` |
| `setCoins(n)` | Sets `player.coins`. | `{ coins: n }` |
| `setStock(type, n)` | Sets `shop.stock[type]` for all shops. | `{ stock: … }` |
| `setPause(p)` | Sets `ctx.paused`. | `{ paused: p }` |

---

## 5. TESTS

All tests drive only §4 calls. `g = window.__game`. "State" means the object returned by `getState()`; equality is deep structural equality.

**Pre-state (all tests after `start()` or `seed(12345)` + `start()`):**
`tick=0, elapsed=0, paused=false, rngState=12345, player={x:-224, y:-32, facing:[0,-1], coins:10, all inventory 0}`. World: exactly 1 berry node `{x:-224, y:-32, count:<berry node count>, progress:0}`, 1 water tile `{gx:7, gy:4}`, 1 shopkeeper `{x:206, y:206}`, 2 buildings, 0 fish, 0 furniture.

1. **Title → play.** Calls: `g.start()`. Must find: `tick=0, elapsed=0, paused=false`, world built (≥1 berry node, water contains `{gx:7,gy:4}`), player at `(-224,-32)`.
2. **Movement.** Calls: `g.seed(12345); g.start(); g.moveDir(0,-1); g.step(1/60, 120)`. Must find: `player.x=-224, player.y=-90` exactly (120 · (1/60) · <player speed> = 240; −32 − 240), `facing=[0,-1]`, `elapsed=2`. Then `g.moveDir(0,0); g.step(1/60,1)` → `player.y` unchanged.
3. **Harvest berries.** Calls: `g.seed(12345); g.start(); g.moveDir(0,-1); g.step(1/60,120); g.moveDir(0,0); g.inputAction("interact"); g.step(1/60,1); g.inputAction("interact"); g.step(1/60,1)`. Must find: `player.inventory.berries=4` (2 harvests × `<berries per harvest>`, with `<berry node count>` ≥ 4), the berry node at `(-224,-90… )` — i.e. the node record with `count=<berry node count>−4` and `progress=0`, `harvest={nodeId:-1, …}`, `tick=122`.
4. **Harvest ore.** Calls: `g.seed(12345); g.start(); g.moveDir(0,-1); g.step(1/60,120); g.moveDir(0,0); g.spawnOre(-224, -154, 5); g.inputAction("interact"); g.step(1/60,1); g.inputAction("interact"); g.step(1/60,1); g.inputAction("interact"); g.step(1/60,1); g.inputAction("interact"); g.step(1/60,1); g.inputAction("interact"); g.step(1/60,1)`. The spawn is valid (64 units from the player, 92+ from the pond, in bounds). Must find: `player.inventory.ore=5`, the ore node `count=0`, `player.inventory.berries=0`.
5. **Fishing.** Calls: `g.seed(12345); g.start(); g.moveDir(0,-1); g.step(1/60,120); g.moveDir(0,0); g.inputAction("fish"); g.step(1/60,1)`. Must find: `fish.active=true, fish.progress=1/60, fish.waterRef={gx:7,gy:4}` (distance 40 ≤ 80). Then `g.step(1/60, 179)`. Must find: `fish.active=false, fish.progress=0, player.inventory.fish=1`, `fish.pool` length 1, and `fish.pool[0].x` within `[224, 256]` and `fish.pool[0].y` within `[128, 160]`. (Exact pool coordinates depend on RNG call order and are therefore asserted only within the tile; §11 asserts they are seed-stable.)
6. **Sell.** Calls: `g.seed(12345); g.start(); g.setInventory({berries:10, ore:0, fish:0, f1:0, f2:0, f3:0, f4:0}); g.inputAction("interact"); g.step(1/60,1)`. Must find: `shop.openShopId=0` (shopkeeper at (206,206), distance 48 ≤ 64), `player.coins=60` (10 · <sell price: berries> = 50 + 10), `player.inventory.berries=0`, `shop.cooldown=<shop cooldown>`.
7. **Buy, gated and ungated.** Continuing test 6's state (`cooldown` active): `g.step(1/60, 1); g.inputAction("place")`-independent — call `g.inputAction("fish")`-style one-shot is not buy; buy happens through `inputAction("place")` only for placement, so buying uses the stall: there is no buy key — buying is exposed through `placeFurniture`? **No.** Buy is a stall action; the debug path is `g.inputAction("interact")` closes, so tests buy via: `g.placeFurniture`? Correct contract: buying is driven by `inputAction("buy", "f1")`. — Must find after `g.inputAction("buy","f1")` while `cooldown>0`: nothing changes (`shop.stock.f1=5`, `coins=60`). Then `g.step(1/60, 300)` (clears cooldown: 300/60 = 5 s ≥ <shop cooldown>) and `g.inputAction("buy","f1")`. Must find: `player.coins=20` (60 − 40), `player.inventory.f1=1`, `shop.stock.f1=4`. *(Note: the control table has no buy key; `inputAction("buy", type)` is a debug one-shot that the Shop module consumes — it is listed here as an extension of the `inputAction` vocabulary and is the only test path into buy.)*
8. **Placement rules.** Continuing test 7 (player at (−224, −32), carrying f1): `g.placeFurniture("f1", 6, 4)` → must find: record `{type:"f1", x:288, y:192, w:48, h:48, place:"home"}` in `furniture` (furniture tile (6,4) covers [288,192,336,240], inside home interior [−320,−128,−128,64] **and** the player point lies in that tile: (−224,−32) ∈ [288,192,336,240]? **Correction** — the tile must contain the player point; the furniture tile under (−224,−32) is (−5, −1) covering [−240,−48,−192,0]; the test therefore calls `g.placeFurniture("f1", -5, -1)` → record `{x:-240, y:-48, place:"home"}`, `inventory.f1=0`. Then `g.setInventory({f1:1}); g.placeFurniture("f1", -5, -1)` → `{error:"occupied"}` and `furniture` length 1. Then `g.placeFurniture("f1", 0, 0)` (tile [0,0,48,48], outside both interiors) → `{error:"not_in_interior"}`. Then `g.setInventory({f1:1}); g.placeFurniture("f1", 1, 2)` (tile [48,96,96,144], inside museum interior [32,64,224,192]) → record `{x:48, y:96, place:"museum"}`.
9. **Fishing range gate.** Calls: `g.seed(12345); g.start(); g.moveDir(1,0); g.step(1/60, 240); g.moveDir(0,0)` (player now at (26, −32), distance to pond ≥ 152 > 80); `g.inputAction("fish"); g.step(1/60,1)`. Must find: `fish.active=false, fish.progress=0, player.inventory.fish=0`.
10. **Pause.** Calls: `g.seed(12345); g.start(); g.moveDir(0,-1); g.step(1/60, 60)` → `elapsed=1, tick=60`. `g.inputAction("pause"); g.step(1/60, 10)` → must find: `paused=true, tick=70, elapsed=1`, `player.y=-32-<player speed>` unchanged from tick 60. `g.inputAction("pause"); g.step(1/60, 1)` → `paused=false, elapsed=1 + 1/60`.
11. **Determinism.** Two runs: `A = (g.seed(12345); g.start(); <full sequence of tests 2–10, minus the assertions, with the same literal calls and step counts>)` and then `B = (same sequence again after re-seeding)`. Must find: deep equality `A_final === B_final` for the entire `getState()` (including `fish.pool[0]`, every node position, `rngState`), and `A_final ≠` the same sequence run after `g.seed(777)` (worlds differ: node sets and `fish.pool[0]` differ).
12. **No stray randomness.** During `g.seed(12345)` and 1200 subsequent `g.step(1/60,1)` calls, a harness spy on `Math.random` and `Date.now` records zero calls affecting `ctx`. Must find: spy count for game code = 0.

---

## 6. BUILD ORDER

Every milestone after M0 leaves the game playable (move + at least one working economy action).

| Milestone | Adds (by module) | Land check |
|---|---|---|
| M0 — Page | shell: canvas, title screen, `window.__game` with `start()/getState()`, loop with `UPDATE_ORDER` empty, `Render` draws title | Test 1 |
| M1 — Movement | `Input`, `Player`, `World` (bounds + generate, nodes/water as static data), `Render` world pass | Test 2 |
| M2 — Collecting | `Harvest`, `Inventory`, `RNG` (node generation, `<berry nodes>`/`<ore nodes>`) | Test 3 |
| M3 — Mining & Fishing | ore harvest path, `Fish`, water tiles | Tests 4, 5, 9 |
| M4 — Economy | `Shop`, shopkeeper entity, stall open/sell/buy | Tests 6, 7 |
| M5 — Decoration | `Place`, occupancy grid, museum building, furniture records | Test 8 |
| M6 — Hardening | pause, map overlay, budgets + culling, full determinism sweep | Tests 10, 11, 12, §3 budget asserts |

---

## 7. RISKS

1. **Coordinate convention drift between the two grids and the camera.** Two different tile sizes (world grid 32, furniture grid 48), one world, one camera — an off-by-a-tile error in `tileOf`/`tileRect` silently breaks placement and fishing. **Prevention rule:** all grid math lives in `World.tileOf/tileRect` (and `FGRID`-equivalents) and nothing else computes grid coordinates; a unit test pins them: `tileOf(240, 144) = [7, 4]`, `tileRect(7,4) = {x0:224, y0:128, x1:256, y1:160}`, and the camera equation `s = (p − player) + (480, 270)` is asserted for three fixed points in tests 2, 5, 8.
2. **Timing race: the real-time accumulator and the tick order.** A dropped frame or a tab pause can deliver a huge `dt`, and a reordered `UPDATE_ORDER` changes harvest/shop outcomes. **Prevention rule:** logic only ever runs on the fixed `DT = 1/60`; the accumulator is clamped to ≤ 3 catch-up ticks per frame (the excess is dropped, never simulated); `UPDATE_ORDER` is a single const array iterated in one place; tests 10 and 11 (plus a harness assertion that `elapsed` after N `step` calls is exactly `N/60`) pin both rules.
3. **Performance cliff when the world fills up.** 400 nodes + 512 water tiles + 24 furniture + 12 fish at full caps can exceed the 3000-ops canvas budget and the 2 ms tick budget as the player walks around. **Prevention rule:** culling to viewport + 192-unit margin in `Render` before any draw; on budget overrun, layers drop in the fixed order ground grid → water shimmer → fish → node highlights (never entities or UI); the occupancy test is a `Map` lookup, never a linear scan; a test at maximum caps (spawns via §4 until each cap is reached) asserts `render.drawCalls ≤ 3000` and tick time ≤ 2 ms.