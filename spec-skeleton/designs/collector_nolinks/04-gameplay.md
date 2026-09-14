# 4. GAMEPLAY SPEC

**The game in one paragraph.** A single-player, no-combat, no-fail collector: the player walks a compact `120×120` island, gathers berries from bushes, mines charged ore rocks, and fishes a lake with a small timing minigame; sells each category to its matching shopkeeper (Moss/Grit/Reed) whose prices soften as you flood them and recover over time; buys tiered tools and furniture; decorates a Home and a locked-then-unlocked Museum; assigns unlocked specimens to unique display cases; and works through six count-based goals to earn the Curator’s Seal. Target playtime to full completion ≈ 2–3 hours; after completion the game remains fully open-ended — everything keeps working, nothing locks.

**Records and rosters.**

*Resources (9)* — node IDs: berry/ore `${resourceId}_${x}_${y}`; fish `fish_${resourceId}_${x}_${y}`.

| ID | Name | Category | Tier | Base sell | Stack | Nodes/Spots | Respawn / Empty | Charges | Exhibit score | Submask | Hint |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| `sweet_berry` | Sweet Berry | berry | 1 | 2 | 20 | 30 | 20s | — | 10 | full Berry Grove | Berry Grove, common |
| `moon_berry` | Moon Berry | berry | 2 | 5 | 20 | 15 | 45s | — | 25 | Grove and `y ≥ 20` | Grove, middle/south |
| `ember_berry` | Ember Berry | berry | 3 | 12 | 20 | 5 | 120s | — | 60 | Grove and `y ≤ 12` | Grove, northern edge |
| `copper_ore` | Copper Ore | ore | 1 | 4 | 10 | 25 | 300s | 3 | 10 | full Ore Ridge | Ridge, common |
| `silver_ore` | Silver Ore | ore | 2 | 10 | 10 | 12 | 360s | 3 | 25 | Ridge and `x ≥ 98` | Ridge, eastern half |
| `crystal_shard` | Crystal Shard | ore | 3 | 25 | 10 | 4 | 720s | 3 | 60 | Ridge and `x ≥ 112` | Ridge, eastern tip |
| `minnow` | Minnow | fish | 1 | 4 | 5 | 15 | none | — | 10 | shore water (adjacent to non-water) | Lake shore |
| `trout` | Trout | fish | 2 | 10 | 5 | 8 | none | — | 25 | non-shore water, `d² ≤ 0.7` | Lake center |
| `moonfish` | Moonfish | fish | 3 | 25 | 5 | 3 | none | — | 60 | water `y ≥ 85` | Deep south lake |

(`d² = (dx/17)² + (dy/29)²` from lake center `(22,70)`; fish spots never deplete.)

*Tools (9)* — bought from the matching shop; buying replaces the current tool; no downgrade, no resell; Tier 1 owned at start, not buyable.

| ID | Name | Shop | Category | Tier | Cost |
| --- | --- | --- | --- | ---: | ---: |
| `woven_basket` | Woven Basket | moss | berry | 1 | owned |
| `honey_pouch` | Honey Pouch | moss | berry | 2 | 35 |
| `ember_satchel` | Ember Satchel | moss | berry | 3 | 90 |
| `hand_pick` | Hand Pick | grit | ore | 1 | owned |
| `copper_pick` | Copper Pick | grit | ore | 2 | 35 |
| `silver_pick` | Silver Pick | grit | ore | 3 | 90 |
| `short_rod` | Short Rod | reed | fish | 1 | owned |
| `bamboo_rod` | Bamboo Rod | reed | fish | 2 | 35 |
| `moon_rod` | Moon Rod | reed | fish | 3 | 90 |

*Shopkeepers (3)* — standing (non-solid), open-air Trading Post; canopy matches category.

| ID | Name | Category | Position | Line (T2) |
| --- | --- | --- | ---: | --- |
| `moss` | Moss | berry | `(58, 65)` | “Sweet berries make sweet homes.” |
| `grit` | Grit | ore | `(60, 65)` | “Good ore, good tools.” |
| `reed` | Reed | fish | `(62, 65)` | “The lake gives. Take your share.” |

*Furniture (18)* — all decor repeatable; display cases unique (one owned at a time), Museum-only, repurchasable after sale if the stock tier is still unlocked.

| ID | Name | Shop | Unlock | Type | Size | Cost | Museum only | Unique | Slots |
| --- | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| `berry_planter` | Berry Planter | moss | 1 | decor | 1x1 | 10 | no | no | 0 |
| `berry_jar` | Berry Jar | moss | 1 | decor | 1x1 | 15 | no | no | 0 |
| `rug` | Rug | moss | 1 | decor | 2x2 | 10 | no | no | 0 |
| `berry_bench` | Berry Bench | moss | 2 | decor | 2x1 | 45 | no | no | 0 |
| `small_display_case` | Small Display Case | moss | 2 | display | 1x1 | 40 | yes | yes | 2 |
| `berry_rug` | Berry Rug | moss | 3 | decor | 2x2 | 70 | no | no | 0 |
| `side_table` | Side Table | grit | 1 | decor | 1x1 | 10 | no | no | 0 |
| `bookshelf` | Bookshelf | grit | 1 | decor | 1x2 | 20 | no | no | 0 |
| `ore_lamp` | Ore Lamp | grit | 1 | decor | 1x1 | 15 | no | no | 0 |
| `ore_workbench` | Ore Workbench | grit | 2 | decor | 2x1 | 55 | no | no | 0 |
| `pedestal` | Pedestal | grit | 2 | display | 1x1 | 35 | yes | yes | 1 |
| `crystal_display_case` | Crystal Display Case | grit | 3 | display | 1x1 | 80 | yes | yes | 3 |
| `fish_net_rack` | Fish Net Rack | reed | 1 | decor | 1x1 | 10 | no | no | 0 |
| `fish_barrel` | Fish Barrel | reed | 1 | decor | 1x1 | 15 | no | no | 0 |
| `water_shelf` | Water Shelf | reed | 1 | decor | 1x1 | 15 | no | no | 0 |
| `fish_bench` | Fish Bench | reed | 2 | decor | 2x1 | 45 | no | no | 0 |
| `fish_tank` | Fish Tank | reed | 2 | decor | 2x1 | 70 | no | no | 0 |
| `moon_display_case` | Moon Display Case | reed | 3 | display | 1x1 | 80 | yes | yes | 3 |

Display-case slot total: 2+1+3+3 = **9** (exactly the 9 specimens). Totals: 14 decor + 4 display + 9 tools = 27 distinct items (per ruling).

*Buildings (2)*:

| Building | Interior floor | Door (interior) | Exterior door | Exterior exit | Exterior footprint | Initially locked |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Home | 10×8 | `(5,7)` | `(52,68)` | `(52,69)` | x 49..55, y 64..69 | no |
| Museum | 12×10 | `(6,9)` | `(68,68)` | `(68,69)` | x 65..71, y 64..69 | yes (until First Trades) |

Interior walls = tiles outside the floor bounds; the door tile is walkable and cannot carry furniture.

*Zones (5 + perimeter)*:

| Zone | Mask |
| --- | --- |
| Village | x 45..75, y 45..75 |
| Berry Grove | x 25..95, y 5..38 |
| Ore Ridge | x 82..115, y 30..90 |
| Lake | x 5..40, y 40..100 (water = ellipse center (22,70), rx 17, ry 29) |
| Perimeter | x<2 ‖ x≥118 ‖ y<2 ‖ y≥118 (solid, 2-tile band) |

Biome label priority: interior scene → water/Lake (`Lakeside`) → Berry Grove → Ore Ridge → Village → default `Village`.

*Paths (carved before node placement; never onto perimeter/walls; water left as water)*: North `x=60, y 39..66`; East `y=70, x 65..82`; West `y=70, x 15..64`; Plaza `x 56..64, y 66..70`; Home front `x 50..54, y 69`; Museum front `x 66..70, y 69`.

*Goals (6)* and *start*: player starts at tile `(57,70)`, coins 25, Tier-1 tools, empty inventory, Museum locked, empty collection.

---

## 4.1 Player & movement (T1)

- Movement: WASD/arrows; walk speed `6` tiles/s; water `3` tiles/s; diagonal input normalized (never faster than straight).
- Collision AABB half-size `0.32` tiles, axis-separated (try X, cancel on hit; try Y, cancel on hit).
- Solid: perimeter, building walls, berry bushes, ore nodes. Walkable: grass, paths, all water, doors, interior floors. Fish spots and shopkeepers do not block.
- The player does **not** have: health, stamina, level, combat stats, weight, hunger, or inventory weight. No fail state exists anywhere in the game.
- Scene transition: interact at an exterior door (within `1.2` tiles) → scene becomes the interior, player at interior door center; interact at the interior door → scene `world`, player at the exterior exit center. The Museum door is blocked while locked (prompt + requirement text). Doors are walkable, but scene changes happen only via interaction.

## 4.2 World, generation, interaction (T1)

- Deterministic generation from `worldRng(42)`; the save stores runtime state only; on load the world is rebuilt and saved node/fish/shop state applied.
- Node placement: per resource quota, attempts ≤ 1000, Euclidean minimum distance `4`; on shortfall relax to `3`, then `1`; still short ⇒ content-validation error. For seed 42 the exact quotas are reached **without** using distance `1` (test-asserted; min distance ≥ 3 holds).
- A tile is valid for a land node if: inside the resource submask; not perimeter; not water; not path; not building wall/door; not within `2` tiles of any exterior door; ≥ minDistance from every existing node; unoccupied.
- Fish spots: on water tiles; one fixed resource each; no shared tiles; initial min distance `2`, relax to `1`; never in perimeter; never block movement.
- Initial node state: berries `empty:false, count: runtime-independent worldRng.int(1,2), respawn:0`; ores `empty:false, charges:3, respawn:0`; fish `cooldown:0`.
- Targeting: nearest interactable within `1.2` tiles; tie priority door > shopkeeper > berry > ore > fish; fish requires standing on the spot tile.

Prompts (derived from state):

| State | Prompt |
| --- | --- |
| Full berry node, space available | `Pick Sweet Berry` (per resource name) |
| Empty berry node | `Waiting` |
| Ore with charges, space available | `Mine Copper Ore` |
| Fish spot, cooldown 0, space available | `Cast Line` |
| Fish spot, cooldown > 0 | `Wait` |
| Bite meter active | `Strike!` |
| Shopkeeper | `Talk to Moss` (per name) |
| Home door | `Enter Home` |
| Museum locked | `Museum Locked` + “Sell 5 Sweet Berries, 5 Copper Ores, 5 Minnows” |
| Museum unlocked | `Enter Museum` |
| Interior door | `Exit` |
| No inventory space for targeted resource | `Bag Full` |

## 4.3 Resource nodes: berries and ores (T1)

**Berries** (solid bushes; full or empty; a full bush holds 1–2 berries):
- Pick removes the entire available stack (base yield = `node.count`, 1 or 2).
- After picking: `empty = true`, `respawn = resource.respawnTime` (20s / 45s / 120s).
- On respawn: `empty = false`, `count = runtimeRng.int(1,2)`, `respawn = 0`; visual fade-in ≈ 0.3s.

**Ores** (solid rocks; 3 charges):
- Each completed mine consumes 1 charge and yields ore.
- When charges hit 0: `empty = true`, `respawn = resource.emptyTime` (300s / 360s / 720s).
- On respawn: `charges = 3`, `empty = false`; cracks close, mineral fades in ≈ 0.3s.
- Visual charge states: 3 intact; 2 one chip/crack; 1 large crack + missing chunk; 0 dark interior, no bright mineral.

## 4.4 Gathering: picking & mining (T1)

- Started with `E`/left-click on the targeted node while within `1.2` tiles, the node actionable, and `canHold(resourceId, 1)` true.
- Hold to progress: `progress += dt / tool.gatherTime`; progress bar shown (160×12). Releasing the interact key **or** moving cancels (no yield, no node change).
- **Yield rules**: maximum action yield is 2 for every gathering action.
  - Berry: base = node `count` (1–2); bonus +1 only if base = 1 **and** `runtimeRng.next() < tool.bonusChance`; final capped at 2.
  - Ore: base 1; bonus +1 if `runtimeRng.next() < tool.bonusChance`; capped at 2.
  - If inventory space < final yield, take as many as fit (minimum 1, since the action could start).
- Tool effects (per category):

| Category | T1 | T2 | T3 |
| --- | ---: | ---: | ---: |
| Berry gather time | 0.80s | 0.65s | 0.55s |
| Berry bonus chance | 0% | 30% | 60% |
| Mine time | 1.20s | 0.95s | 0.80s |
| Mine bonus chance | 0% | 30% | 60% |

- Why tools are bought, not crafted: the loop is gather → sell → buy → gather better; crafting is cut.

## 4.5 Fishing (T1)

States: `idle → casting → waiting → biteMeter → (catch|fail) → idle`, with per-spot cooldown.

- Start: stand on the fish-spot tile, `cooldown == 0`, `canHold(fish, 1)`, press `E`/left-click. **Committed once casting starts.**
- Casting: `0.6s` (rod extends, bobber appears, water-entry plop).
- Waiting: `runtimeRng.range(waitMin, waitMax)` — T1 `1.0–3.0s`, T2 `0.8–2.5s`, T3 `0.6–2.0s`; bobber bobs gently.
- Bite meter: lasts `1.5s`; indicator travels progress 0→1; prompt `Strike!`; bobber dips, ripple expands.
- **Strike** (`E`/left-click during `biteMeter`): with `p = meterProgress`, `greenHalf = tool.greenWidth/2/1.5`, `yellowHalf = 0.20/2/1.5`, green centered at `0.5` (fixed):
  - `|p−0.5| ≤ greenHalf` ⇒ success 100%.
  - `|p−0.5| ≤ greenHalf + yellowHalf` ⇒ success `runtimeRng.next() < tool.yellowSuccess`.
  - else fail.
  - Green widths: T1 0.30s, T2 0.40s, T3 0.50s; yellow zones 0.20s each side; yellow success: 40% / 55% / 70%.
- Catch: base 1 fish; bonus +1 if `runtimeRng.next() < tool.bonusFishChance` (0% / 25% / 50%) and space allows; take as fits (min 1).
- Fail (bad strike, meter expiry, **or leaving the spot in any phase**): no fish.
- Success and failure both: `spot.cooldown = tool.cooldown` (T1 3.0s, T2 2.5s, T3 2.0s), `state.fishing = null`.
- Fish spot state per spot: `{ cooldown }`. Spots never deplete.

## 4.6 Inventory (T1)

- One inventory, `10` slots; each slot one stack of one resource type. Tools and furniture are not stored here. No weight, no dropping, no manual splitting, no conversion.
- Stack limits: berry 20, ore 10, fish 5. Ten slots hold all nine types plus one spare stack.
- `addResource`: fill existing same-resource stacks first (up to limit), then empty slots; returns actual added.
- `removeResource`: take from same-resource slots; clear slots at 0; returns actual removed.
- `canHold(resourceId, n)`: existing same-resource space + empty slots × limit ≥ n.
- Gathering/catching can start only if `canHold(resourceId, 1)`; bonus units are added only if space exists. Full ⇒ prompt `Bag Full`, movement unaffected.

## 4.7 Shops & economy (T1)

- Currency: coins; starting 25. Shopkeepers buy one category each (Moss berries, Grit ores, Reed fish) and sell tools + furniture from their shop.
- **Supply meter** (per shop, float 0.0–3.0):
  - Multiplier by `floor(supply)` (with 1e-9 epsilon): `0 → 1.00`, `1 → 0.85`, `2 → 0.70`, `3 → 0.60`.
  - Unit price: `max(1, floor(basePrice × multiplier))`.
  - Selling `n` units: `supply = min(3.0, supply + n/5)`; **the price used is the pre-update price** (Sell All uses one pre-update multiplier for all its resources).
  - Recovery: every 120s after the last sale, `supply −= 1` down to 0 (multi-step for long idles: `steps = floor(elapsed/120)`).
  - Display: floor 0/1/2/3 ⇒ `Normal Price` 5/5 `#6FBF73`; `Low Price` 4/5 `#E3B23C`; `Very Low Price` 3/5 `#E37B3C`; `Barely Buying` 2/5 `#D96A5A` — label + segments, never color alone.
- Selling: one unit; full stack (button or shift-click); Sell All (all matching-category resources).
- **Shop stock tier** per shop from cumulative category sales: `0 → Tier 1`, `≥5 → Tier 2`, `≥25 → Tier 3`. Tier-up emits `shop:tierUnlocked` + toast.
- Buying: fixed prices, no haggling, no stock limits. Tools: must be higher tier than current (no downgrade/no repurchase), affordable; replaces the current tool. Furniture: tier-unlocked, affordable; unique display cases cannot be bought while owned (build inventory or placed); sold display cases can be repurchased while their tier is unlocked.
- Why the supply meter: it soft-discourages one-resource spam, keeps all three shopkeepers relevant, and can never permanently ruin prices (recovery + price floor 1).

## 4.8 Furniture & build mode (T1)

- Purchased furniture enters the **Build Inventory** (separate from resource inventory) as `{ instanceId, itemId, hasBeenPlaced:false }`.
- Build mode only inside Home/Museum; toggle `B`. Floor grid highlights; ghost follows the mouse anchor; `R` rotates 90° (1x1/2x2 unchanged, 2x1↔1x2); `E`/left-click places; `X`/right-click removes the targeted placed item; `Esc` cancels selection / exits; clicking a placed display case opens the exhibit panel; a resell panel sells unplaced furniture.
- **Placement valid iff**, in order: (1) display case ⇒ building is Museum (else `Museum Only`); (2) footprint fully on interior floor (else `Not Floor`); (3) does not cover the door tile (`Covers Door`); (4) does not cover the player’s current tile (`Covers Player`); (5) no overlap with placed furniture (`Blocked`); (6) simulating the new footprint, a BFS path exists from the player tile to the door tile over floor+door tiles only (`Blocks Door Path` if not). Ghost: green/red 40% + reason pill; steady, no flashing.
- Why the path check: with no fail state, a softlock is unacceptable; placement that would wall off the door is refused.
- **Removing**: returns the item to Build Inventory with `hasBeenPlaced:true`; a display case’s specimens are all unassigned; scores and goal counts update.
- **Reselling unplaced furniture**: never placed ⇒ refund `100%` of cost; previously placed ⇒ `max(1, floor(cost/2))`; item leaves the Build Inventory. No profit loop is possible.

## 4.9 Museum & specimens (T1)

- **Collection log**: first collection of a resource unlocks its specimen (no sale required). Nine specimens with exhibit scores: tier 1 = 10, tier 2 = 25, tier 3 = 60 (per roster).
- **Display cases** (Museum-only, unique, 9 total slots): only placed cases can hold specimens; each slot holds one unlocked specimen; each specimen in at most one slot; specimens can be assigned/unassigned from the exhibit panel while the case is placed; removing or selling a case unassigns its specimens.
- **Museum unlock**: on First Trades completion (door lock fades, brass shimmer, toast).

## 4.10 Scores (T1)

- Furniture value: `value = ceil(cost / 10)`.
- `Home Score = Σ value(placed home furniture)`.
- `Museum Score = Σ exhibitScore(assigned specimens) + Σ value(placed museum furniture)`.
- Non-binding; shown in the build menu and Ledger scores tab.

## 4.11 Goals & progression (T1)

| Goal (order) | Requirement | Reward / unlock |
| --- | --- | --- |
| First Harvest (1) | Collect 1 Sweet Berry, 1 Copper Ore, 1 Minnow | 10 coins |
| First Trades (2) | Sell 5 Sweet Berries, 5 Copper Ores, 5 Minnows | 25 coins; unlock Museum; (guarantees Tier 2 at all shops) |
| Cozy Home (3) | 5 furniture pieces placed in Home | 50 coins |
| Open Museum (4) | 3 display cases placed in Museum **and** 3 specimens assigned | 50 coins |
| Full Collection (5) | All 9 resource types collected | 100 coins |
| Curator’s Seal (6) | Sell 25 berries + 25 ores + 25 fish (category totals); all 9 specimens assigned; 12 furniture pieces placed in Museum | Completion |

- Goals are count-based and **latching**: once complete they never uncomplete (removing furniture or unassigning specimens does not undo completion, including the final goal). Rewards are granted once, with toast + goal-complete sound; the Ledger shows the active goal (first incomplete by order) with progress, plus completed goals checkmarked.
- Completion: `state.completion = true`, `completion:completed` event, completion screen; the game remains fully playable and save-latched afterward. No new required goals, no fail state added.
- Pacing (target, not enforced): 5–10 min → First Trades + Museum + Tier 2 stock; 15–25 min → first furniture, Open Museum, Tier-2 tools; 30–45 min → Tier-3 stock (25 category sales); 60–90 min → Full Collection, curation, Curator’s Seal; total ≈ 2–3 hours.

## 4.12 Settings (T2)

Fields (reserved in T1 state): `musicVolume 0.7`, `sfxVolume 0.8`, `ambienceVolume 0.5` (range 0–1), `reduceMotion`, `highContrast`. Open with `P` (in play) or the title-screen button. Effects: Reduce Motion ⇒ disable water ripple frames, Tier-3 pulse, particles, toast slide (essential state changes and text remain). High Contrast ⇒ thicker borders, stronger contrast/highlights (no mechanic changes). Persisted with the save; applied via `<html data-reduce-motion data-high-contrast>`.

**Progression & difficulty.** Direction comes from the six latching goals plus per-shop tier thresholds (5/25). Difficulty exists only as the fishing timing meter (a small skill moment, never punishing: yellow-zone fallback 40–70% by tier, mild fail). Nothing can fail the player: resources respawn, prices recover, no resource is permanently unavailable, and mistakes are recoverable (remove/resell furniture).

**Feel.** Small satisfying cycles: a 10–30s gathering trip, a 3–10s sell, a 5–20s placement or upgrade decision, then a visible progression update (goal progress, stock unlock, new specimen, score tick). The world is a compact cozy diorama where every zone is reachable from the village in about 3–6 seconds; gathering feels tactile (shake, pop, +1/+2), selling feels rewarding (coin flight, plink), placing feels personal (green ghost, dust settle), and the museum slowly becomes the place the player is proud of. Calm, curated, never loud.
