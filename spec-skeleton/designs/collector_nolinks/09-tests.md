# 9. TESTS

`npm test` runs unit + integration in Node with zero runtime dependencies and no DOM (GameCore is headless). Every check below is driven only by debug API calls; every expected value follows from the gameplay doc. (Visual’s acceptance checklist is enforced through the E2E smoke test and the SCREENSHOTS table below.)

**tests/unit/content.test.js**
- All 9 resources exist; categories ⊆ {berry, ore, fish}; base prices 2/5/12/4/10/25/4/10/25; stack limits 20/10/5 per category; quotas 30/15/5/25/12/4/15/8/3; respawns 20/45/120/300/360/720 (fish none); ore charges 3; exhibit scores 10/25/60 per tier.
- 9 tools with correct shop/category/tier/cost (owned, 35, 90 ×3 categories); tier effect tables match the gameplay doc exactly (times 0.80/0.65/0.55 and 1.20/0.95/0.80; bonuses 0/.30/.60; fish green 0.30/0.40/0.50, yellow 0.40/0.55/0.70, bonus 0/.25/.50, cooldown 3.0/2.5/2.0, waits 1.0–3.0 / 0.8–2.5 / 0.6–2.0).
- 18 furniture rows: shop, unlockTier, size, cost, type, museumOnly, unique, slots per the gameplay doc's roster; display cases total exactly 9 slots; totals 14 decor / 4 display.
- 3 shopkeepers at `(58,65)`, `(60,65)`, `(62,65)` with correct categories.
- Goals in order 1–6 with the exact gameplay-doc requirements and rewards; requirement types reference valid resources/categories/buildings.
- Buildings: home 10×8 door (5,7) exterior (52,68); museum 12×10 door (6,9) exterior (68,68); museum `lockedInitially:true`.
- Audio: every audio-doc recipe ID resolves in `src/audio/recipes.js`.

**tests/unit/rng.test.js**
- Same seed ⇒ identical sequence (three runs). `range` within [min,max]; `int` integer, inclusive bounds; `worldRng(42)` and `runtimeRng(43)` sequences differ.

**tests/unit/pathfinding.test.js**
- BFS finds a path in an open grid; returns null when blocked; path includes start and goal; 4-direction only; `placementPathCheck` fails when the door is enclosed by simulated furniture and succeeds when a path exists.

**tests/unit/inventory.test.js** (via `debug.giveResource`, `debug.clearInventory`, `debug.fillInventory`, `core` internals)
- Add to empty creates a slot; add to existing stack respects limits (berry 20, ore 10, fish 5); overflow uses a new slot; full inventory adds 0; `canHold` false at full; partial remove keeps slot; full-stack remove clears it; bonus yields limited by available space.

**tests/unit/economy.test.js** (via `debug.setSupply`, `debug.setCumulativeSold`, `core.buyItem/sellOne/sellAll`)
- Multipliers: floor 0/1/2/3 ⇒ 1.00/0.85/0.70/0.60 at supply 0, 0.999, 1, 1.999, 2, 2.999, 3 (epsilon floor). Unit price = `max(1, floor(base×multiplier))` (e.g., sweet berry at floor 3 ⇒ 1).
- Sell 1 ⇒ supply +0.2; sell 5 ⇒ +1.0; cap 3.0; price uses pre-update supply; Sell All uses one pre-update multiplier; recovery: 1 after 120s, multi-step after long idle, clamped to [0,3].
- Tiers: 0 sales ⇒ 1; 5 ⇒ 2; 25 ⇒ 3. Tool buy: only higher tier, replaces current, lower/same rejected, unaffordable rejected. Furniture buy adds buildInventory; unique display case cannot be bought twice while owned; can be repurchased after `core.sellBuildItem`.

**tests/unit/build.test.js** (via `debug.giveFurniture`, `debug.forcePlace`, `core.canPlace`-facing actions)
- Valid placement on empty floor succeeds; outside floor ⇒ `Not Floor`; on door ⇒ `Covers Door`; on player tile ⇒ `Covers Player`; overlap ⇒ `Blocked`; display case in Home ⇒ `Museum Only`; walled-off door ⇒ `Blocks Door Path`; rotation swaps 2x1↔1x2, 1x1 unchanged; invalid placement mutates nothing and emits `invalid:action`.
- Remove returns item to buildInventory with `hasBeenPlaced:true`; refund: never-placed = 100% (e.g., 40 ⇒ 40), previously-placed = `max(1, floor(cost/2))` (40 ⇒ 20, 10 ⇒ 5); display-case removal unassigns all its specimens.

**tests/unit/goals.test.js** (via `debug.collectAll`, `debug.setCoins`, sales through `core.sellOne`, `debug.forcePlace`, `core.assignSpecimen`)
- firstHarvest completes at 1+1+1 collected (reward 10); firstTrades completes only at 5+5+5 of the specific resources (25 + museum unlock + `museum:unlocked`); cozyHome at 5 home furniture; openMuseum at 3 placed display cases + 3 assigned; fullCollection at all 9; curatorsSeal at 25/25/25 category sales + 9 assigned + 12 museum furniture (sets `completion`, emits once).
- Latching: after completion, removing furniture / unassigning specimens does not uncomplete; active goal = first incomplete by order; `completion:completed` fires exactly once.

**tests/unit/worldGenerator.test.js**
- Seed 42 twice ⇒ identical node/fish lists and tile map. Exact counts: sweet 30, moon 5-tier 15, ember 5, copper 25, silver 12, crystal 4, minnow 15, trout 8, moonfish 3. All land nodes inside their masks/submasks (ember `y≤12`, silver `x≥98`, crystal `x≥112`; minnow shore, trout non-shore `d²≤0.7`, moonfish `y≥85`); fish on water; no land node on path/perimeter; none within 2 tiles of a door; no shared tiles; min pairwise distance ≥ 3 at seed 42. Perimeter band solid. Start tile `(57,70)` walkable. BFS from start reaches every node’s adjacent tile, both exterior doors, and all three shopkeepers.

**tests/integration/movement.test.js** (PlayerSystem/InteractionSystem)
- 6 tiles in 1s on grass; diagonal not faster than straight; 3 tiles in 1s on water (shallow and deep); cannot enter perimeter, berry node, or ore node; can cross water; enter/exit Home via door interaction; museum door blocked while locked, enterable after `debug.setGoalComplete("firstTrades", true)`; target selection respects 1.2-tile radius and tie priority; prompts match the gameplay doc's table (including `Museum Locked` with exact requirement text and `Bag Full` after `debug.fillInventory`).

**tests/integration/gathering.test.js** (Nodes/Gathering)
- Berry pick completes in `tool.gatherTime` (0.80s T1); yield = node count; bonus adds +1 only when base = 1 and the RNG roll succeeds (MockRNG); pick empties the node; respawn after 20/45/120s with count 1–2; releasing the key or moving cancels with no yield; mining: 1 charge per 1.20s action, bonus ≤ +1, 3 charges empty the node, empty node does nothing, respawn restores 3; gathering blocked at `Bag Full` (no state change); first collection flips `collection` and emits `specimen:unlocked`.

**tests/integration/fishing.test.js**
- Starts only on the spot tile with `canHold(1)` and cooldown 0; casting lasts 0.6s; wait within the tier range (MockRNG `range`); meter appears after wait and lasts 1.5s; strike inside green (MockRNG-free center region) succeeds 100%; yellow uses the yellow chance (MockRNG 0.5 at T2 55% boundary values); outside fails; missing the meter fails; success ⇒ 1 fish (+1 only on bonus roll with space); both outcomes set the tier cooldown and clear `state.fishing`; new cast blocked during cooldown; leaving the spot in any phase ⇒ fail + cooldown.

**tests/integration/shop.test.js**
- Shop shows only matching-category sell rows; sellOne updates coins/inventory/supply/sales with pre-update price; sellStack and sellAll (matching category only, single pre-update multiplier); cumulative sales drive tier unlocks at 5 and 25 with `shop:tierUnlocked`; buying a tool updates `player.tools`; buying furniture adds buildInventory; locked-tier buy fails; unaffordable buy fails; unique double-buy fails; selling updates goal progress (`goal:progress`).

**tests/integration/buildFurniture.test.js** (BuildSystem/ScoreSystem)
- Build mode activates only in Home/Museum (`B` in world ⇒ `invalid:action`); selecting a buildInventory item shows the ghost; valid place removes it from buildInventory and makes its tiles solid; remove returns it (`hasBeenPlaced:true`); scores update on place/remove (`debug.readScores`): value = `ceil(cost/10)`; resell refunds 100% / 50% (min 1); invalid placement leaves state unchanged.

**tests/integration/museum.test.js** (MuseumSystem)
- Display cases placeable only in Museum; placed case exposes exactly its slot count (2/1/3/3); assignment requires a placed case + unlocked specimen; assigning updates museum score by the exhibit score; unassigning subtracts it; a specimen cannot occupy two slots; removing a case unassigns all; selling an unplaced case does not touch assignments; museum score = exhibit sum + furniture value sum; museum unlock occurs only via firstTrades.

**tests/integration/save.test.js**
- New-game state matches the gameplay doc (25 coins, T1 tools, empty inventory, locked museum, all goals false). Round-trip (`debug.saveNow` → `core.loadGame`) preserves: position, coins, inventory, tool tiers, node empty/count/charges/respawn, fish cooldowns, shop supply/cumulative/lastSaleTime, sales counters, collection, buildInventory, placed furniture (+display slots), goal latches, completion, settings; non-persisted fields (target/activeGather/fishing/build) reset to null. Corrupted save and version mismatch ⇒ new game, no throw.

**tests/integration/playthrough.test.js** — proves full completion through real actions (MockRNG biased to green-strike/favorable rolls; teleport for speed):
1. New headless game; assert start state (25 coins, T1 tools, locked museum, empty inventory/buildInventory, all goals false).
2. Collect 1 Sweet Berry, 1 Copper Ore, catch 1 Minnow ⇒ firstHarvest complete, coins +10.
3. Sell 5 sweet / 5 copper / 5 minnows ⇒ firstTrades complete; museum unlocked; all shop tiers ≥ 2.
4. `debug.collectAll()` ⇒ fullCollection complete, coins +100.
5. Sell to 25 category sales each ⇒ all tiers 3.
6. Buy all 4 display cases + 8 decor (buy via `core.buyItem`); enter Museum; place 4 cases + 8 decor on valid tiles (harness `findPlaceableTile`); assign all 9 specimens ⇒ curatorsSeal complete, `completion:true`, `completion:completed` fired once.
7. `debug.saveNow()` → load into a fresh core ⇒ completion and all final state remain true.

**tests/e2e/smoke.spec.js** (`?test=1`, Playwright + `npm run serve`)
- Page loads with no console errors; title visible; canvas present at 960×540; HUD hidden pre-start; Start begins a new game and HUD appears; world pixels render; `C` opens Ledger, `Esc` closes; `E` near Moss opens the shop; no missing-asset or recipe errors.

**tests/e2e/assets.spec.js** (adapted to the procedural pipeline)
- Every `assetManifest` ID resolves: `AssetFactory` produces a non-blank texture for every sprite ID; every audio recipe ID renders a buffer without exception; no manifest ID is missing; no 404 requests (there are no binary assets).

**SCREENSHOTS** (synthesized from visual’s UX journey, moments, and acceptance checklist; each reachable by debug API calls; pass = the listed visual content is present and correct):

| ID | Screenshot | Reach (calls) | Must show |
| --- | --- | --- | --- |
| S1 | Title screen | fresh load | Title, Start, Continue (disabled without save), controls list, Settings button; parchment/wood skin |
| S2 | First world moment | `debug.loadFresh()`, Start | Player near Home; `Village` label; coins 25; empty inventory; toast `Goal: First Harvest`; ledger gold dot; minimap with player/home/museum/trading-post dots |
| S3 | Berry grove states | `debug.teleport(60, 20)`; `debug.setNodeState(firstSweetId, {empty:true, respawn:10})` | Full bush with berry cluster vs bare empty bush; target highlight on nearest bush; prompt `Pick Sweet Berry` |
| S4 | Ore charge states | `debug.teleport(95, 60)`; `debug.setNodeState` four nodes to charges 3/2/1/0 | Intact rock → chipped → large crack → hollow; copper speckles; prompt `Mine Copper Ore` |
| S5 | Fish spot idle + highlight | `debug.teleport` onto a minnow spot | Subtle ripple/fish shadow; in-range highlight; prompt `Cast Line` |
| S6 | Fishing bite meter | `debug.setFishing(spotId, "biteMeter", 0.25)` | 240×20 meter, centered green zone, yellow side zones, white indicator at 25%, prompt `Strike!`, bobber dip |
| S7 | Shop sell, Low Price | `E` at Moss; `debug.setSupply("moss", 1.2)` | Sell rows with unit price 1 for Sweet Berry (`floor(2×0.85)`), stack totals, Sell/Sell-stack/Sell All; supply meter 4/5 amber `Low Price` |
| S8 | Shop buy, locked tiers | same shop, Buy tab | Tier-2 card 30% alpha, lock, `Sell 5 berries to unlock`; tier-3 `Sell 25 berries to unlock`; affordable items enabled |
| S9 | Home build, valid ghost | `debug.setScene("home")`; `debug.giveFurniture("berry_planter")`; `toggleBuild()`; `selectBuildItem`; `setBuildAnchor` on floor | Floor grid; green ghost 40%; item card (name, 1x1, valid); building score panel |
| S10 | Invalid placement | anchor on door tile (5,7) | Red ghost 40%; reason pill `Covers Door` |
| S11 | Museum curation | `debug.setGoalComplete("firstTrades", true)`; `debug.collectAll()`; `debug.giveFurniture("small_display_case")`; enter museum; place; `core.assignSpecimen(...)` | Unlocked door (no lock); display case with one mini specimen icon, soft case light; museum score visible; `Displayed` badge |
| S12 | Ledger — Goals | `openLedger()` | Active goal brass-bordered with progress fractions and reward; completed goals checkmarked |
| S13 | Ledger — Collection | after `debug.collectAll()` | 3×3 grid, all cards colored with hint + exhibit score; assigned ones badged |
| S14 | Ledger — Scores | with placed furniture | Home Score and Museum Score cards, furniture/exhibit counts |
| S15 | HUD full | `debug.giveResource("sweet_berry", 3)`, `debug.giveResource("copper_ore", 2)`; play in village | Location label, coins, minimap, 3 tool pip rows, filled slots with counts, contextual hints |
| S16 | Bag Full | `debug.fillInventory()`; stand on a full berry node (E) | All 10 slots filled; prompt `Bag Full`; inventory border pulse (single) |
| S17 | Completion | `debug.setGoalComplete("curatorsSeal", true)` | Edge dim, curator seal stamp, `Curator’s Seal Complete` / `Your museum is open.`, Continue (gold-leaf particles = T2) |
| S18 | Settings | `debug.openSettings()` | Three volume sliders, Reduce Motion + High Contrast toggles, parchment skin |
