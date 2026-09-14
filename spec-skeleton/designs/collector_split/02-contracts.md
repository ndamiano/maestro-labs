# 2. CONTRACTS

## 2.1 Module layout

Carried from engineering §3, with the asset-pipeline ruling (§0.2) applied. Files:

```text
index.html
package.json
scripts/serve.mjs
styles/main.css

src/main.js
src/config/constants.js
src/content/content.js
src/assetManifest.js
src/assets/AssetFactory.js          // was AssetLoader: generates every texture from manifest recipes (offscreen canvas)
src/audio/recipes.js                 // §6 audio recipes as data (osc/noise tables)

src/core/GameCore.js
src/core/EventBus.js
src/core/SeededRNG.js
src/core/ContentValidator.js
src/core/SaveAdapter.js
src/core/LocalStorageSaveAdapter.js
src/core/InMemorySaveAdapter.js

src/world/Tiles.js
src/world/WorldGenerator.js
src/world/Pathfinding.js

src/systems/PlayerSystem.js
src/systems/InteractionSystem.js
src/systems/InventorySystem.js
src/systems/NodeSystem.js
src/systems/GatheringSystem.js
src/systems/FishingSystem.js
src/systems/ShopSystem.js
src/systems/BuildSystem.js
src/systems/MuseumSystem.js
src/systems/GoalSystem.js
src/systems/ScoreSystem.js

src/input/InputManager.js
src/render/CanvasRenderer.js
src/render/Camera.js
src/render/SpriteRenderer.js

src/ui/UIRoot.js
src/ui/TitleUI.js
src/ui/HUD.js
src/ui/MinimapUI.js
src/ui/ShopUI.js
src/ui/LedgerUI.js
src/ui/BuildUI.js
src/ui/ToastUI.js
src/ui/SettingsUI.js
src/ui/CompletionUI.js
src/audio/AudioManager.js

tests/harness/headless.js
tests/harness/mockRng.js
tests/harness/testUtils.js
tests/unit/{content,rng,pathfinding,inventory,economy,build,goals,worldGenerator}.test.js
tests/integration/{movement,gathering,fishing,shop,buildFurniture,museum,save,playthrough}.test.js
tests/e2e/{playwright.config.js,smoke.spec.js,assets.spec.js}
```

- `index.html`: canvas `#game-canvas` 960×540, `#ui-root` DOM container, module script `src/main.js`; CSS scales the canvas to fit the window at 16:9 with `image-rendering: pixelated`.
- `package.json`:
```json
{
  "name": "collector-game",
  "private": true,
  "type": "module",
  "scripts": {
    "serve": "node scripts/serve.mjs",
    "test": "node --test tests/unit tests/integration",
    "test:e2e": "playwright test"
  }
}
```
  No runtime dependencies. `@playwright/test` is the only allowed dev dependency; `npm test` must pass without it.
- `src/assetManifest.js`: semantic ID → **recipe** (palette refs, shape steps, sizes) per §3 and §5; `AssetFactory` renders each ID once to an offscreen canvas at load. No binary asset files exist in the repo.

## 2.2 Global context

`GameCore.state` — the serializable simulation state. Every field a rule reads or writes lives here (A1 verified). Fields marked *(non-persisted)* are reset on load and never written to the save.

```js
state = {
  version: 1,
  worldVersion: 1,
  seed: 42,
  time: 0,                                  // seconds, unpaused sim time
  scene: "world" | "home" | "museum",

  player: {
    x: 57.5, y: 70.5,                        // tile-space floats (center of tile 57,70)
    coins: 25,
    tools: { berry: 1, ore: 1, fish: 1 },    // current tier per category
    inventory: Array(10)                     // null | { resourceId, count }
  },

  target: null,                             // (non-persisted) { kind: "berry"|"ore"|"fish"|"shop"|"door", id, building? }
  activeGather: null,                        // (non-persisted) { type: "berry"|"ore", targetId, progress: 0..1 }
  fishing: null,                             // (non-persisted) { spotId, state: "casting"|"waiting"|"biteMeter", phaseTimer, meterProgress }
  build: null,                               // (non-persisted) { active, buildingId, selectedBuildInstanceId, selectedPlacedInstanceId, rotation: 0|1, anchor: {x,y}|null, validity: {valid, reason} }

  nodes: {                                   // keyed by node ID (§4.3); two shapes:
    // berry: { empty: bool, count: 1|2, respawn: number }
    // ore:   { empty: bool, charges: 0..3, respawn: number }
  },
  fishSpots: { [spotId]: { cooldown: number } },

  shops: {
    moss: { supply: 0.0, cumulativeSold: 0, lastSaleTime: null },
    grit: { supply: 0.0, cumulativeSold: 0, lastSaleTime: null },
    reed: { supply: 0.0, cumulativeSold: 0, lastSaleTime: null }
  },

  sales: {
    byResource: { sweet_berry:0, moon_berry:0, ember_berry:0, copper_ore:0, silver_ore:0, crystal_shard:0, minnow:0, trout:0, moonfish:0 },
    byCategory: { berry: 0, ore: 0, fish: 0 }
  },

  collection: { sweet_berry:false, moon_berry:false, ember_berry:false,
                copper_ore:false, silver_ore:false, crystal_shard:false,
                minnow:false, trout:false, moonfish:false },

  buildInventory: [ { instanceId, itemId, hasBeenPlaced } ],
  nextInstanceId: 1,

  placed: {
    home:    [ { instanceId, itemId, x, y, rotation, display: null } ],
    museum:  [ { instanceId, itemId, x, y, rotation, display: null } ]
    // display (only for type "display"): { slots: (null | resourceId)[] } length = content slots
  },

  goals: { firstHarvest:false, firstTrades:false, cozyHome:false,
           openMuseum:false, fullCollection:false, curatorsSeal:false },

  museumUnlocked: false,
  completion: false,

  settings: { musicVolume: 0.7, sfxVolume: 0.8, ambienceVolume: 0.5,
              reduceMotion: false, highContrast: false }
}
```

Derived values (never stored): active goal (first incomplete by `order`), shop tier (`floor` thresholds), unit price (supply formula), Home/Museum scores, biome label, supply display floor.

`core.world` (read-only, regenerated from seed): `{ map, nodes: [{id, resourceId, x, y}], fishSpots: [{id, resourceId, x, y}], doors, interiors, paths, start, lake }`.

## 2.3 Module specifics

**constants.js** — `TILE_SIZE=24`, `WORLD_SIZE=120`, `VIEW_WIDTH=960`, `VIEW_HEIGHT=540`, `PLAYER_SPEED=6`, `WATER_SPEED=3`, `INTERACT_RADIUS=1.2`, `INVENTORY_SLOTS=10`, `SAVE_VERSION=1`, `WORLD_VERSION=1`, `WORLD_SEED=42`, `FIXED_DT=1/60`, `MAX_STEPS_PER_FRAME=6`, `FISHING={CAST_TIME:0.6, METER_TIME:1.5, YELLOW_ZONE_TIME:0.2}`, `SHOP={SUPPLY_MAX:3.0, SUPPLY_SALE_INCREMENT:1/5, RECOVERY_INTERVAL:120, TIER_THRESHOLDS:[0,5,25]}`, `SAVE_KEY="collector_game_save_v1"`.

**content.js** — single default object; all gameplay content is data. Fields (every field gameplay records need):
`version, worldSeed:42, worldVersion:1, resources[9]` (§4.3 roster), `toolTiers` (berry/ore: `tier, gatherTime, bonusChance`; fish: `tier, waitMin, waitMax, greenWidth, yellowSuccess, bonusChance, cooldown`), `tools[9]`, `shopkeepers[3]` (`id, name, category, x, y, line, canopy`), `furniture[18]` (`id, name, shop, unlockTier, type: "decor"|"display", size:[w,h], cost, museumOnly, unique, slots, description`), `buildings` (home/museum per roster), `goals[6]` (with `order, rewardCoins, unlock, requirements[]`), `collection[9]` (specimen names, exhibitScore, iconShape, hint), `audio` (SFX/music/ambience recipe IDs per §6), `zones` (masks per §4.2), `start:[57,70]`.

**SeededRNG** — `new SeededRNG(seed)`; `next() → [0,1)`; `range(min,max)`; `int(min,max)` inclusive. Same seed ⇒ same sequence.

**EventBus** — `on(event, cb) → unsubscribe`, `off(event, cb)`, `emit(event, payload)`. Core emits; UI/audio subscribe. Required events (carried, plus two added):

| Event | Payload |
| --- | --- |
| `time:tick` | `{ time }` |
| `scene:changed` | `{ scene }` |
| `player:moved` | `{ x, y }` |
| `player:stepped` *(added)* | `{ surface: "grass"|"stone"|"water" }` |
| `inventory:changed` | `{ inventory }` |
| `coins:changed` | `{ coins, delta }` |
| `resource:collected` | `{ resourceId, amount, nodeId? }` |
| `specimen:unlocked` | `{ resourceId }` |
| `node:emptied` / `node:respawned` | `{ nodeId }` |
| `fish:cast` / `fish:waiting` / `fish:bite` / `fish:fail` | `{ spotId }` |
| `fish:catch` | `{ spotId, resourceId, amount }` |
| `shop:sold` | `{ shopId, resourceId, amount, coins, supplyBefore, supplyAfter }` |
| `shop:allSold` | `{ shopId, amounts, coins, supplyBefore, supplyAfter }` |
| `shop:tierUnlocked` | `{ shopId, tier }` |
| `shop:bought` | `{ shopId, itemId, type }` |
| `museum:unlocked` | `{}` |
| `furniture:placed` / `furniture:removed` | `{ buildingId, instanceId, itemId }` |
| `furniture:sold` | `{ instanceId, itemId, coins }` |
| `specimen:assigned` / `specimen:unassigned` | `{ displayInstanceId, slotIndex, resourceId }` |
| `goal:progress` | `{ goalId }` |
| `goal:completed` | `{ goalId, reward }` |
| `completion:completed` | `{}` |
| `save:completed` | `{}` |
| `invalid:action` | `{ reason }` |

**GameCore** — constructor `new GameCore({ content, saveAdapter, eventBus, worldRng, runtimeRng })`; methods (production API; all are also the test surface):
`init(), newGame(), saveGame(), loadGame(data), setPaused(bool), update(dt), setMoveInput(dx,dy), interactDown(), interactUp(), openShop(shopId), closeShop(), buyItem(shopId,itemId), sellOne(shopId,resourceId), sellStack(shopId,resourceId), sellAll(shopId), openLedger(), closeLedger(), toggleBuild(), selectBuildItem(instanceId), selectPlacedItem(instanceId), rotateBuildItem(), setBuildAnchor(x,y), placeBuildItem(), removePlacedItem(instanceId), sellBuildItem(instanceId), assignSpecimen(buildingId, instanceId, slotIndex, resourceIdOrNull), setSettings(partial)`.
`update(dt)` order = §1.2 run order; paused ⇒ no `time` advance.

**WorldGenerator** — `generateWorld(seed, content, worldRng) → core.world`. Steps: grass map → perimeter band → zone ground → lake ellipse → carve paths → place buildings → place nodes (berries/ores) → place fish spots. Rules in §4.2. Deterministic: same seed ⇒ identical output.

**Pathfinding** — `bfs(startTile, goalTile, blockedTiles) → [tiles] | null` (4-direction); `placementPathCheck(buildingId, playerTile, doorTile, simulatedBlocked) → bool` used by BuildSystem.

**PlayerSystem** — movement (normalized input, speed by surface, axis-separated AABB collision half-size 0.32), footstep emission (`player:stepped` every 0.4s while moving; surface: grass/berry_ground/path → `grass`; ore_ground/interior floors → `stone`; water → `water`), scene transitions (interact at exterior door → interior door center; interact at interior door → exterior exit center; museum blocked while locked), no fast travel.

**InteractionSystem** — per-frame target selection: nearest interactable within `1.2` tiles of player center; tie priority: door > shopkeeper > berry > ore > fish; fish-spot targeting requires the player to stand on the spot tile. Prompt text derived per §4.2 table.

**InventorySystem** — `addResource(resourceId, amount) → added`; `removeResource(resourceId, amount) → removed`; `canHold(resourceId, amount) → bool`; `count(resourceId) → n`. Algorithms in §4.6.

**NodeSystem** — `pickBerry(nodeId)`, `mineOre(nodeId)`, respawn updates; state shapes and rules in §4.3.

**GatheringSystem** — start on `interactDown` (valid target + `canHold(1)`), progress `dt / tool.gatherTime`, cancel on key release or player movement, completion yields per §4.4.

**FishingSystem** — state machine per §4.5; committed once casting starts; strike resolution with fixed center green zone.

**ShopSystem** — `unitPrice(shopId, resourceId)`, `sellOne/sellStack/sellAll`, `buyItem`, supply update/recovery, tier computation, `supplyDisplay(shopId) → floor 0..3`. Rules in §4.7.

**BuildSystem** — `canPlace(buildingId, itemId, ax, ay, rotation) → {valid, reason}`, `place()`, `remove()`, `sell()` per §4.8; reasons enum: `"Museum Only" | "Not Floor" | "Covers Door" | "Covers Player" | "Blocked" | "Blocks Door Path"`.

**MuseumSystem** — `assignSpecimen(...)` rules, `assignedSpecimenCount()`, unassignment on removal/sale per §4.9.

**GoalSystem** — `check()` after relevant events; requirement evaluators for types `resource_collected, resource_sold, category_sold, building_furniture_count, museum_display_count, specimen_assigned, all_resource_collected`; latching (completed goals never uncomplete); active goal = first incomplete by `order`; rewards/unlocks per §4.11.

**ScoreSystem** — `furnitureValue(item) = ceil(cost/10)`; `homeScore()`, `museumScore()` per §4.10.

**Save adapters** — `load()`, `save(data)`, `clear()`; `LocalStorageSaveAdapter` (key `collector_game_save_v1`), `InMemorySaveAdapter` (tests). Save = serializable `state` only (non-persisted fields excluded). Triggers: after mutations (collect, sell, buy, place, remove, sell furniture, assign/unassign, goal complete, museum unlock, completion, settings), every 30s unpaused time, `beforeunload`/visibility-hidden; small debounce. Corrupted/invalid version ⇒ new game, no crash, toast `Save not compatible. New game started.`

**Renderer/UI/Audio/Input** — presentation layers only; no rule logic. Renderer: camera, visible-tile culling, y-sort with Z table (§3), build ghost, minimap. UI: DOM modals per §7. AudioManager: plays §6 recipes on events, zone music, volumes from settings, starts on first user interaction. Input: maps §1.2 controls to core actions per context (title/world/shop/build/fishing; fishing restricts input to interact during `biteMeter`).
