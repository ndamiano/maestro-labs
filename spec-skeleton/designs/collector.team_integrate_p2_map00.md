# BUILD SPEC — Cozy Island Collector (merged; supersedes gameplay.md, visual.md, engineering.md)

Every number, name, and rule in this document is final. Where the three source documents agreed, the content is carried whole; where they disagreed, the ruling in §0.2 wins; nothing was dropped silently — carried, ruled on, tiered in §0.3, or listed under Cuts.

---

# 0. SCOPE

## 0.0 Reading map (builder's note)

Sections are self-contained per system. Implement in §10 milestone order and consult
only the listed section while writing that system. Sections marked "gate" must be read
before any code is written; no other section is a gate.

| While building | Read |
| --- | --- |
| anything (gate) | §0.2 Decisions, §0.3 Tiers, §1.2 conventions, §2.2 state, §2.3 module specifics |
| WorldGenerator / Pathfinding | §4.2 (zones, paths, node placement, targeting) |
| Player / Interaction | §4.1, §4.2 prompts |
| Nodes / Gathering | §4.3, §4.4, §5 node visuals |
| Fishing | §4.5 |
| Inventory | §4.6 |
| Shops / economy | §4.7, §7 shop modal row |
| Build / Museum / Scores | §4.8, §4.9, §4.10 |
| Goals / completion | §4.11 |
| Assets / renderer | §3, §5 |
| Audio | §6 |
| UI screens | §7 |
| Save | §2.3 save adapters |
| acceptance only (never a gate) | §8, §9, §11, SCREENSHOTS |

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Open world collector game (single continuous map, free roam) | §3 Space, §4.2 |
| The player walks around | §4.1 |
| Collecting resources into an inventory | §4.6 |
| Harvest berries | §4.3, §4.4 |
| Mine ores | §4.3, §4.4 |
| Fish fish | §4.5 |
| Sell them to a shop keeper for each type | §4.7 |
| Buy furniture to decorate their home | §4.8, §4.10 |
| Decorate a small museum-type building | §4.9 |
| *(added)* Relaxed, no-fail fantasy (no health, no combat, no fail state) | §4.1, §4.11 |
| *(added)* Purchasable tool tiers that improve gathering | §4.4, §4.7 |
| *(added)* Count-based goals ending in Curator’s Seal completion | §4.11 |
| *(added)* Collection log and museum specimen curation | §4.9 |
| *(added)* Supply-meter price fluctuation per shop | §4.7 |
| *(added)* Non-binding Home/Museum scores | §4.10 |
| *(added)* Save/load persistence across sessions | §2.3 (Save), §8 |
| *(added)* Accessibility settings (reduce motion, high contrast, volumes) | §4.12, §7 |
| *(added)* Deterministic world (seed 42) | §4.2 |
| *(added)* Cozy hand-painted pixel look with per-zone identity | §3 |
| *(added)* Calm generated audio (music + SFX, Web Audio) | §6 |

## 0.2 Decisions

One row per disagreement and per request-open choice a builder would otherwise have to make. Rulings are final.

| Topic | gameplay said | visual said | engineering said | Ruling (and why) |
| --- | --- | --- | --- | --- |
| Dimensionality (request open) | 2D top-down, fixed camera, no vertical axis | 2D top-down; painted sprite height and soft shadows only; no parallax, no vertical implication | 2D tile canvas, 960×540, y-sort | **2D top-down, y-sorted sprites, no parallax, no vertical mechanics** — all three agree; the request did not specify. |
| Design resolution (open) | 960×540, ≈40×22 tiles visible | 960×540, art native to 24px tiles, nearest-neighbor | 960×540 canvas, CSS-scaled | **960×540 design resolution, 24px tiles, pixelated scaling** — unanimous. |
| Input scheme (open) | WASD/arrows + interact button; mouse in build mode | Keyboard/mouse; no touch | Keyboard/mouse table; touch cut | **Keyboard + mouse only**; full table in §1.2. |
| Player start tile (open) | “starts nearby” home | — | Start tile `(57, 70)`, position `(57.5, 70.5)` | **Start at `(57, 70)`** — the only concrete value given. |
| Perimeter width (disagreement) | Impassable “outer edge tiles” (1 tile) | “1–2 tile visual border” | 2-tile band: `x<2 ‖ x≥118 ‖ y<2 ‖ y≥118` | **2-tile band** — prevents edge-grazing, satisfies “edge is impassable,” and matches the visual border width. |
| Berry base yield (disagreement; internal to gameplay) | §5.3: base = entire stack (1–2), upgrades add bonus; §6.2 pseudo: base = 1, bonus → 2 | — | Base = `node.count`; bonus +1 only if `baseYield < 2` (cap 2) | **Base = entire available stack (1 or 2); bonus +1 only when the stack was 1, capped at 2** — preserves “picking removes the entire available stack” and keeps yields bounded at 2. |
| Tool tier indicator (disagreement) | Stars/roman: T1 none, T2 `II`-ish, T3 `III`-ish | Pips: T1=1, T2=2, T3=3 filled; “do not use stars if pips are clearer” | Pips 1/2/3, no color-only | **Pips (1–3 filled)** — two documents agree; pips are clearer at 32px. |
| Water depth & speed (disagreement) | “Shallow water walkable at 3 t/s” (deep unspecified) | Shallow and deep water both readable, both walkable-looking | All water walkable at 3 t/s | **All water (shallow and deep) walkable at 3 t/s** — deep water holds Trout and Moonfish spots, so it must be enterable. |
| Fishing green-zone position (open) | Moving indicator, zone widths given, position unspecified | Meter centered on screen; green + yellow zones | Green fixed at meter center (progress 0.5) | **Green zone fixed at center** — readable and testable; tier upgrades already widen the green zone, which is the designed ease improvement. |
| Leaving a fish spot (disagreement of scope) | Fail if leaving during the bite meter | — | Fail if leaving during any phase (casting, waiting, meter) | **Fail on leaving in any phase** — superset; prevents stalling a committed cast. |
| Supply recovery (disagreement) | 1 step of 1.0 per 120s after last sale | — | `steps = floor(elapsed/120)`, subtract steps, clamp 0, bookkeep `lastSaleTime` | **Engineering multi-step version** — identical to gameplay for single-step cases, correct after long idles. |
| Museum lock requirement text (disagreement) | §9.6 door text “Sell 5 berries / ores / fish” (category); goal itself needs specific resources | “Museum Locked” prompt | Goal uses `resource_sold` per specific resource | **Door text shows the exact First Trades requirement: “Sell 5 Sweet Berries, 5 Copper Ores, 5 Minnows”** — the goal is specific; category text would mislead. |
| Inventory hotkey `I` (disagreement) | Optional `I` for separate inventory details | No separate screen | Separate inventory screen cut | **No `I`, no separate inventory screen**; slot hover tooltip carries name/count/base price/current shop price. |
| Furniture totals (disagreement) | Summary: 15 non-display, 28 total items | Item tables per shop (14 decor visuals + 4 display) | 18 furniture rows (14 decor, 4 display) + 9 tools | **14 decor + 4 display + 9 tools (3 owned at start) = 27 distinct items**; the item tables govern — the summary counts were an arithmetic error. |
| Asset pipeline (disagreement) | — | PNG sprite files + `.ogg` audio; also gives procedural tile/audio *reference* recipes | Assets “provided”; manifest maps IDs to files; no runtime deps | **All assets generated in code**: sprites/tiles drawn to offscreen canvases from §3 recipes; all audio synthesized per §6; the manifest maps semantic IDs to *recipes*, not files. The builder is code-only, so no binary assets. |
| Music approach (disagreement) | Audio out of scope | `.ogg` loops, 72–84 BPM, zone identity table | Music file paths in content | **Generated Web Audio loops and stingers** with zone identity per visual’s instrument/mood table; no audio files. Stingers are the §6 SFX rows (no separate music-stinger files). |
| Volume defaults (disagreement) | — | −18/−12/−24 dB relative | Defaults 0.7 / 0.8 / 0.5 (music/SFX/ambience) | **0.7 / 0.8 / 0.5 linear defaults** — concrete values; the dB table is honored as relative intent (SFX loudest, ambience quietest). |
| Settings access (open) | Settings not specified | Settings UI with 3 volumes + 2 toggles | SettingsUI exists; no key bound | **`P` in play opens Settings; button on title screen**; state fields reserved in T1, modal staged T2 (§0.3). |
| Scene entry (open) | Doors walkable; interaction implied | — | Entry/exit via interaction, not auto-step | **Interaction-based entry/exit** — prevents door re-entry loops. |
| Player collider (open) | — | Sprite 16×16 centered in tile | AABB half-size 0.32 tiles, axis-separated movement | **0.32-tile half-size, axis-separated collision** — the only concrete value. |
| Fixed timestep (open) | Timers in seconds | — | `update(dt)` clamps dt to 0…0.1 | **Fixed 1/60s steps via rAF accumulator, max 6 steps/frame, 0.1s clamp as safety** — deterministic timers require a fixed step. |
| Random source (open/clarify) | “One random source” implied via seeded RNG | — | Two RNG instances: `worldRng`, `runtimeRng` | **One `SeededRNG` class; exactly two instances**: `worldRng(seed 42)` for world generation only, `runtimeRng(seed 43)` for gameplay randomness; `Math.random` is banned. |
| Footsteps (open) | — | 3 SFX: grass/stone/water steps | SFX mapping includes them | **Three footstep SFX**, surface = tile under player (mapping in §6). |
| Screenshots table (missing) | — | No SCREENSHOTS table shipped (acceptance checklist §30 and moments §18/§27 exist) | — | **§9 SCREENSHOTS table synthesized from visual’s moments + acceptance checklist**, each row reachable via §8 debug calls. |
| X / right-click target (disagreement of wording) | “deletes the selected placed furniture” | — | “remove targeted placed item” | **X / right-click removes the placed item under the pointer (targeted); clicking a placed display case opens the exhibit panel.** |
| Build mode outside interiors (open) | Build mode only inside Home/Museum | — | Same | **`B` outside interiors emits `invalid:action` + toast “Build inside your Home or Museum.”** |

## 0.3 Tiers

**T1 — the game that must ship** (by system name): World generation (deterministic), Player movement & collision, Scenes (world/Home/Museum) & doors, Interaction, Berry & Ore nodes, Gathering (pick/mine), Fishing, Inventory, Shops & economy (sell/buy/supply/tiers), Furniture & build mode, Museum & specimens, Scores, Goals & completion, Save/load, Title screen, Persistent HUD + minimap, Shop UI, Ledger UI, Build UI, Toasts, core SFX, zone music.

**T2** (independent items, add in this order):
1. Settings modal (music/SFX/ambience sliders, Reduce Motion, High Contrast) — state defaults reserved in T1.
2. Zone ambience beds (generated noise beds, §6).
3. Activity music layers: shop, build.
4. Shopkeeper flavor lines on shop open (Moss/Grit/Reed).
5. One-time build-mode hint toast (“Use mouse to place, R to rotate, X to remove”).
6. Feedback juice: coin flight to HUD, HUD pulse, shopkeeper sign sparkle, gold-leaf particles on completion.

**T3** (independent items, add in this order):
7. Shopkeeper non-idle animations (talk/sell/buy/unlock); idle ships in T1.
8. Minimap current-zone brighter highlight.
9. E2E deep audio-decode suite (smoke + asset-generation checks stay T1).

**Cuts (final, not staged)** — merged from visual §28 and engineering §2.5, carried with reasons: no day/night cycle (lighting complexity, noise); no weather (visibility/pacing); no parallax (readability); no character customization (asset/UI burden); no heavy particles (noise; ≤20 small effects allowed); no complex facial animation (unreadable at sprite size); no per-small-area music files (one loop per major zone); no resource nodes on minimap (clutter, exploration); no dynamic lighting for furniture (readable placement); no scary/aggressive audio (no fail state); no touch controls (keyboard/mouse design); no multiple save slots / cloud save (single-player relaxed); no custom map editor (generator + quotas suffice); no runtime texture-generation of *art direction* beyond §3 recipes (assets are generated code, not runtime user-facing generation); no dynamic lighting, screen shake (calm tone); BFS only, no A* (placement checks + bots suffice); no separate inventory screen; no manual stack splitting; no mobile optimization pass; no replay system; no achievements outside goals.

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- **World unit**: tile. Tile size `24×24` px. Design resolution `960×540`; visible area ≈ `40×22` tiles.
- **Axes**: `x` → right, `y` → down. Origin `(0,0)` top-left. World is `120×120` tiles, coordinates `0..119`; pixel cell of tile `(x,y)` is `[24x, 24x+24) × [24y, 24y+24)`.
- **Positions**: actor positions are tile-space floats; tile `(x,y)` center = `(x+0.5, y+0.5)`.
- **Frames**: fixed timestep `dt = 1/60` s. `requestAnimationFrame` accumulator; max 6 steps per frame; a single passed `dt` is clamped to `0..0.1` as safety. `state.time` is seconds of unpaused simulation time.
- **Timers** in this document are seconds unless marked otherwise.

## 1.2 Important conventions

- **Origin/camera**: camera follows the player, never rotates, clamped to world bounds (world) or interior floor bounds (interiors):
  `cameraX = clamp(player.x*24 − 480, 0, 120*24 − 960)`, `cameraY = clamp(player.y*24 − 270, 0, 120*24 − 540)`.
- **System run order per fixed step** (all use the step’s `dt`):
  1. Player movement & collision
  2. Gathering (berry/mine progress)
  3. Fishing state machine
  4. Node respawn timers
  5. Fish-spot cooldowns
  6. Shop supply recovery
  7. Goal evaluation
  8. Event emission (batch)
- **The one random source**: `SeededRNG` (class in §2.3). Exactly two instances: `worldRng = SeededRNG(42)` — world generation only, at world (re)build; `runtimeRng = SeededRNG(43)` — all gameplay randomness (berry counts, bonus yields, wait times, yellow-zone rolls). `Math.random` is banned in production code.
- **Pause**: simulation paused in Title, Shop, Ledger, Settings, Completion modals. Not paused in build mode or interiors. While paused, `state.time` does not advance.
- **Controls** (keyboard + mouse; touch is cut):

| Input | Action |
| --- | --- |
| `W`/`A`/`S`/`D`, Arrow keys | Move (diagonals normalized) |
| `E` or left click | Interact (world); strike (fishing bite meter); place selected item (build mode) |
| `B` | Toggle build mode (interiors only; elsewhere → `invalid:action` + toast) |
| `C` | Toggle Ledger |
| `P` | Toggle Settings (T2 modal) |
| `Esc` | Close modal / cancel build selection / exit build mode |
| `R` | Rotate selected unplaced item 90° (build mode) |
| `X` or right click | Remove targeted placed furniture (build mode) |
| Mouse move | Set placement anchor tile (build mode) |
| Shift-click | Sell whole stack (shop Sell tab) |

---

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

---

# 3. VISUAL SPEC

**Look.** Cozy Hand-Painted Pixel Diorama: the world is a small, lovingly arranged painterly diorama viewed from directly above — a miniature collector’s garden, a warm little village outside a small museum. Soft pixel shading, gentle color separation, low-to-medium saturation, warm earth tones as the base, bright but controlled resource accents, rounded shapes, small animation. **No hard black outlines** — use darker shaded edges, 1-pixel dark accents, light rim highlights, and soft drop shadows. It must never read as neon action, grim survival, loud-outlined cartoon, AAA 3D, or sterile vector UI.

**Lighting and atmosphere.** No day/night, no weather, no dynamic lighting, no parallax (cut list). Light is fixed and readable: soft baked shadows under every actor/node/furniture (1-pixel `#2E241B` at 25–35% alpha, elliptical/soft-rectangular, no hard black shadows); warm lamp/window glow in the Home; soft spotlight pools around display cases in the Museum; Tier-3 resources pulse with a slow emissive cycle of `1.5s` full cycle (no fast flashing; disabled under Reduce Motion). Painted sprite height is allowed (bushes/roofs may extend above their base tile) but must never imply a vertical axis, caves, ladders, or elevation.

**Space.** One continuous `120×120` outdoor map plus two interior scenes. Tile `24×24`; design resolution `960×540` (≈`40×22` tiles); nearest-neighbor scaling, no full-screen anti-aliasing. Soft transitions between zones; small overlapping decorations; paths visually connect the village to every resource zone; the perimeter reads as a natural 2-tile boundary (dark water/forest edge), not a missing texture. Draw order bottom-to-top: 1 terrain, 2 water base, 3 shore/path, 4 low non-solid decorations, 5 placed furniture bases, 6 actors + solid resource nodes (y-sorted), 7 tall non-blocking decorations, 8 water ripples/overlays, 9 particles (≤20 active), 10 UI. Y-sort Z values: furniture base 0.5, player/shopkeeper/berry node/ore node 1.0, fish bobber 1.2, interaction highlight 1.5. Decorations never hide an interaction target (make transparent, move, or draw below). Animation limits: characters/water max 8 FPS; UI animations max 300ms; no full-screen flash/shake/wash — all feedback is localized (small pops, small coin flight, small case glow).

**Recipe table** (all colors are the shared palette; tiles are generated per recipe: fill base → 20–40 darker speckles → 10–20 lighter speckles → 1–2 accent details → 1px bottom shadow line `#2E241B` @ 15%):

| Palette | Hex | Use |
| --- | ---: | --- |
| Ink Shadow | `#2E241B` | Shadows, text, dark UI |
| Warm Dark Wood | `#5C4032` | Borders, dark wood |
| Medium Wood | `#8A5A3B` | Furniture, buttons |
| Light Wood | `#B98A63` | Trims, highlights, button hover |
| Parchment | `#F3E4C7` | UI panels, cards |
| Paper | `#F9F1DC` | Highlighted panels |
| Earth Path | `#C2A374` | Village paths, dirt, shore sand |
| Dry Grass | `#A3B37A` | Village edges, light speckles |
| Grass Base | `#85A66A` | Main grass (dark: `#5F7A4C`) |
| Stone Grey | `#8C867B` | Rocks, museum floor (dark: `#6D675D`) |
| Stone Light | `#B9B2A6` | Highlights, walls |
| Water Shallow | `#6FB0C4` | Shallow lake (ripple lines lighter blue) |
| Water Deep | `#3F7D96` | Deep lake |
| UI Gold | `#D9A441` | Coins, highlights, goal reward |
| Valid Feedback | `#6FBF73` | Valid placement, success, green zone |
| Invalid Feedback | `#D96A5A` | Invalid placement, errors, red zone |
| Warning Amber | `#E3B23C` | Low supply, yellow zone, caution |
| Coin icon | `#E5C158` | Coin HUD icon |

| Zone accent | Primary | Secondary | Minimap color |
| --- | ---: | ---: | ---: |
| Village | `#D9A441` warm amber | `#8A5A3B` wood | `#D9A441` |
| Berry Grove | `#5E8C4A` leaf green | `#D94F5C` sweet berry | `#5E8C4A` |
| Ore Ridge | `#A5765B` earth stone | `#C06A3F` copper | `#A5765B` |
| Lakeside | `#4E9BB0` teal water | `#9BB8E8` moon blue | `#4E9BB0` |
| Home interior | `#C99B6A` warm wood floor | `#F3E4C7` parchment walls | — |
| Museum interior | `#C8B494` stone plaster | `#C7A24A` brass | — |

| Resource / specimen color | Hex | Character | Icon shape (colorblind-safe) |
| --- | ---: | --- | --- |
| Sweet Berry | `#D94F5C` | Warm red-pink | Round berry with leaf |
| Moon Berry | `#8E7BD1` | Lavender-blue | Round berry with crescent mark |
| Ember Berry | `#F07A3A` | Warm orange, slight glow | Round berry with flame mark |
| Copper Ore | `#C06A3F` | Earthy orange-brown | Hexagonal ore with speckles |
| Silver Ore | `#CFCFCF` | Cool silver | Hexagonal ore with vertical stripe |
| Crystal Shard | `#86E8FF` | Bright cyan, soft glow | Triangle prism |
| Minnow | `#D8C97A` | Pale yellow-silver | Small round fish |
| Trout | `#D97A4F` | Orange-red | Longer fish |
| Moonfish | `#9BB8E8` | Pale blue-silver | Fish with crescent mark |

Tier visual logic: Tier 1 natural/no glow; Tier 2 slightly cooler/brighter; Tier 3 soft emissive pulse, 1.5s cycle. Resource colors must be identical in world sprites, inventory icons, shop UI, ledger cards, display-case contents, toasts.

Tile recipes: **grass** base `#85A66A`, dark speckles `#5F7A4C`, light `#A3B37A`, accent small flower `#D94F5C`/`#F3E4C7`; **berry_grove** grass + leaf litter + fallen leaves; **ore_ground** stone `#8C867B` base, dark `#6D675D`, light `#B9B2A6`, accent copper/crystal fleck; **path** `#C2A374` packed dirt with 1px wood trim; **water** `#6FB0C4`/`#3F7D96` with lighter ripple lines, shore edge `#C2A374`; **perimeter** darker water/forest band.

Sprite sizes: player 16×16 (shadow 12×6 ellipse); furniture `1x1`=24×24, `2x1`=48×24, `1x2`=24×48, `2x2`=48×48. UI skin: panels parchment `#F3E4C7`, border `#5C4032` 2px, radius 3px, shadow `rgba(0,0,0,0.25)` 4px offset; buttons normal `#8A5A3B` / hover `#B98A63` / pressed `#7A4A32` / disabled `#8A7A66` / selected `#D9A441` border, text `#2A1B12`; tabs: active raised parchment + brass underline, inactive darker parchment; font stack `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`; sizes: title 18px, body 14px, small/hint 12px (never below 12px); important text always on a background panel. Build ghost: valid `#6FBF73` @ 40%, invalid `#D96A5A` @ 40%, selected item white outline, steady (no flashing) with red reason pill. Grid lines `rgba(255,255,255,0.12)`; valid/invalid tile highlight `rgba(111,191,115,0.25)` / `rgba(217,106,90,0.25)`.

**Visual-implied rules, ruled**: (a) 5-segment supply meter maps to `floor(supply)` 0..3 with fills 5/4/3/2 and labels Normal/Low/Very Low/Barely (§4.7) — color plus text, never color alone; (b) target highlight = soft white outline + slight brightening, no bounce/pulse, shown when `state.target` is set; (c) “Bag Full” = red `Bag Full` prompt + one short inventory-border pulse (feedback only; movement is never blocked); (d) locked museum door shows brass lock icon + prompt `Museum Locked` with the exact First Trades requirement text; after unlock the lock fades and a brass shimmer crosses the door; (e) fishing meter 240×20: dark water background `#2E241B`, parchment border, green zone `#6FBF73`, yellow zones `#E3B23C`, white vertical indicator bar; prompt says `Strike!` during the bite meter; (f) gathering progress bar 160×12: dark wood background, neutral gold fill, parchment border, category icon — one bar for both berry and mining; (g) Reduce Motion disables water ripple frames, Tier-3 pulse, particles, and toast slide; High Contrast thickens borders and strengthens highlights without changing mechanics; (h) no resource nodes on the minimap.

---

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
- **Yield rules** (ruling §0.2): maximum action yield is 2 for every gathering action.
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

---

# 5. CHARACTERS

**Player.** Silhouette: a small, warm, curious collector — cream shirt, brown vest, straw/wool hat (silhouette hat), small canvas satchel/basket, simple legs; no weapon, no complex facial detail. Smaller than most nodes/furniture so the world feels larger. Sprite 16×16 centered in a 24×24 tile; shadow 12×6 soft ellipse.

Facings: **8 directions** for idle/walk (supports diagonal movement); **4 cardinal directions** for action animations (berry pick, mine, fish set) — actions are less frequent; this bounds the animation set.

Animations (frame = `floor(time × fps) % frames`; reduce motion ⇒ static frame 0 for idle/walk only):

| State | Frames | FPS | Motion rule |
| --- | ---: | ---: | --- |
| Idle | 2 | 4 | Gentle breathing, subtle bob |
| Walk | 4 | 8 | Short step, 8-dir |
| Berry Pick | 2 | 8 | Reaches toward the bush; faces cardinal toward target |
| Mine | 2 | 8 | Pick swings down |
| Fish Cast | 2 | 12 | Rod extends; line + bobber drawn to water |
| Fish Wait | 2 | 4 | Holding rod |
| Fish Strike | 1 | 12 | Rod snaps forward |
| Fish Catch | 2 | 12 | Small celebration |
| Fish Fail | 2 | 12 | Rod relaxes |

Feedback: gathering ⇒ resource icon pops toward player with `+1`/`+2`; targeted object ⇒ soft white outline + slight brightening; `Bag Full` ⇒ red prompt; fishing ⇒ rod line visible.

**Shopkeepers (3).** Shared painterly style; distinct silhouettes and category accents; each has a small overhead canopy/sign (canopy color: Moss berry red/green, Grit copper/stone, Reed blue/teal) and a category icon (berry / pick / fish). The Trading Post is open-air — three stalls, no closed building.

| Keeper | Silhouette | Colors | Costume |
| --- | --- | --- | --- |
| Moss | Rounded, soft | Soft green, leaf brown, cream | Leaf-like hood / small plant hat |
| Grit | Broader, sturdier | Brown, copper, grey | Sturdy coat, tool belt |
| Reed | Longer, relaxed | Blue, teal, pale straw | Loose poncho, straw hat |

Animations: Idle 2f@4 (T1); Talk 2f@8, Sell 1f@12, Buy 1f@12, Unlock 2f@12 (T3).

**Node/fish visual states** (states gameplay rules need): berry full (visible clusters — one cluster if count 1, two if 2; tier color; glow for Ember) / empty (bare branches, muted) / picking (shake once, berry pop) / respawn (fade-in 0.3s); ore 3/2/1/0 charges (intact → chip → large crack → hollow dark interior; tier speckles: copper brown-orange, silver pale, crystal cyan facets + slow glow) / mining (shake, 2–3 chips, icon pop, crack grows) / respawn (cracks close, mineral fades in 0.3s); fish spot idle (small ripple ring every 2–3s, faint slow fish shadow, low contrast) / in range (slight highlight) / casting (line + bobber) / waiting (bobber bobs) / bite (sharp dip, expanding ripple, small splash, prompt `Strike!`) / catch (splash, fish icon pop, soft ring) / fail (dull splash, line flicks, one-frame desaturation) / cooldown (no major animation).

---

# 6. AUDIO

All audio is **generated with the Web Audio API** from `src/audio/recipes.js` (no audio files). Master chain: `musicGain (0.7)`, `sfxGain (0.8)`, `ambienceGain (0.5)` → master; settings adjust 0–1. Audio context resumes on first user interaction (autoplay policy). Short SFX use playback-rate variation 0.98–1.02 to avoid mechanical repetition; stingers (rows 23–26) are never rate-varied. Recipes below are the exact build spec: `osc` = OscillatorNode (waveform, f0→f1 over duration), `noise` = white-noise buffer through the filter; envelope = attack (A) / release (R) on a GainNode.

| # | Sound | Recipe (Web Audio) | Duration | Rule that plays it |
| --- | --- | --- | ---: | --- |
| 1 | ui_hover | osc sine 1200→1100Hz, A 0.001, R 0.01, g 0.03 | 20ms | Any UI hover (buttons/tabs/rows) in any modal or HUD |
| 2 | ui_click | osc square 1800→1600Hz, A 0.001, R 0.01, g 0.05 | 30ms | Any confirmed UI click (buy, sell, assign, tab, place…) |
| 3 | ui_open | noise bandpass 400→1200Hz, g 0.06 | 80ms | Modal opens (shop, ledger, settings, completion) |
| 4 | ui_close | noise bandpass 1200→400Hz, g 0.06 | 80ms | Modal closes |
| 5 | invalid | osc square 220→180Hz through lowpass 800Hz, A 0.002, R 0.02, g 0.08 | 100ms | `invalid:action` (failed buy/place/toggle/etc.) |
| 6 | inventory_full | osc sine 120→80Hz, A 0.005, R 0.03, g 0.10 | 80ms | Gather/catch attempted while `canHold(1)` false (`Bag Full`) |
| 7 | footstep_grass | noise highpass 2000Hz, g 0.04 | 40ms | `player:stepped` surface `grass` (grass, berry_grove, path) |
| 8 | footstep_stone | noise bandpass 1000Hz, g 0.05 | 50ms | `player:stepped` surface `stone` (ore ground, interior floors) |
| 9 | water_step | osc sine 300→180Hz, g 0.06 + noise blip bandpass 900Hz g 0.03 | 80ms | `player:stepped` surface `water` (any water tile) |
| 10 | berry_pick | noise highpass 2000Hz g 0.06 (30ms) + osc sine 880→1320Hz g 0.10, A 0.002, R 0.03 | 80ms | `resource:collected` where nodeType = berry |
| 11 | ore_mine | noise bandpass 900Hz g 0.10 (60ms) + osc sine 90Hz g 0.12, A 0.002, R 0.04 | 100ms | `resource:collected` where nodeType = ore |
| 12 | fish_cast | noise bandpass 600→1400Hz g 0.05 (120ms) + plop osc sine 400→250Hz g 0.07 at end | 120ms | `fish:cast` |
| 13 | fish_bite | osc sine 300→200Hz g 0.08 (40ms) + noise blip bandpass 800Hz g 0.05 | 80ms | `fish:bite` |
| 14 | fish_catch | noise bandpass 1200Hz, pitch-slide −30%, g 0.12 (180ms) + chime osc sine 1320→1760Hz g 0.10, A 0.005, R 0.12 | 250ms | `fish:catch` |
| 15 | fish_fail | noise bandpass 700Hz g 0.08 (120ms) + osc sine 160→120Hz g 0.08 | 150ms | `fish:fail` |
| 16 | coin_sale | osc square 1400→1900Hz g 0.12 (80ms) + jingle sines 2200Hz/2700Hz offset 30ms g 0.05 (70ms) | 150ms | `shop:sold`, `shop:allSold` |
| 17 | coin_buy | osc sine 1200→1600Hz g 0.08, A 0.005, R 0.03 | 100ms | `shop:bought` (tool or furniture) |
| 18 | furniture_place | noise lowpass 600Hz g 0.10 (40ms) + osc sine 200→150Hz g 0.10 | 80ms | `furniture:placed` |
| 19 | furniture_remove | osc sine 500→300Hz g 0.06, R 0.02 | 60ms | `furniture:removed` |
| 20 | furniture_sell | osc sine 1400→1900Hz g 0.08 (60ms) + noise highpass 3000Hz g 0.05 | 120ms | `furniture:sold` |
| 21 | specimen_assign | sines 1568Hz + 2093Hz, A 0.005, R 0.15, g 0.09 | 200ms | `specimen:assigned` |
| 22 | specimen_unassign | sines 1047Hz + 1319Hz, A 0.005, R 0.10, g 0.07 | 150ms | `specimen:unassigned` |
| 23 | goal_complete | osc sine 523→784Hz g 0.12, A 0.02, R 1.2 + chord sines 659/880Hz g 0.05 at t+0.1s (1.5s) | 2s | `goal:completed` |
| 24 | shop_unlock | sines 659/880/1318Hz, A 0.01, R 0.4, g 0.06 each | 800ms | `shop:tierUnlocked` |
| 25 | museum_unlock | osc sine 440→660Hz g 0.09 (400ms) + noise highpass 4000Hz g 0.03 | 800ms | `museum:unlocked` |
| 26 | final_completion | pad sines 330/440/550/660Hz, A 0.5, R 3, g 0.08 + celesta arpeggio sines 1046/1318/1568Hz (8 notes, 0.5s apart, g 0.07) | 6s | `completion:completed` |

Music (generated loops; keys stay in the related family E major / A minor / C# minor / D major; no dissonant cuts; crossfades 1s zone-to-zone, 1s world-to-interior, 0.5s layer add/remove):

| Sound | Recipe (Web Audio) | Rule that plays it |
| --- | --- | --- |
| music_title | pad sines E3/G#3/B3 (165/208/247Hz) g 0.05 + pluck pattern (sine, fast R) 8th notes, 76 BPM | Title screen |
| music_village | pad E major (165/208/247) g 0.05 + marimba motif (sine, R 0.15) 8ths, 84 BPM | Biome `Village` |
| music_berry_grove | pad A minor (110/131/165) g 0.05 + ocarina melody (sine + 5Hz vibrato), 80 BPM | Biome `Berry Grove` |
| music_ore_ridge | pad D major (147/185/220) g 0.05 + low strings (detuned saw, lowpass 500Hz) + kalimba (triangle) 8ths, 76 BPM | Biome `Ore Ridge` |
| music_lakeside | pad A minor (110/131/165) g 0.05 + harp arpeggio (sine, R 0.4), 72 BPM | Biome `Lakeside` |
| music_home | piano-like triangles (chord + sparse melody), 72 BPM, g 0.06 | Scene `home` |
| music_museum | strings pad (detuned saw, lowpass 800Hz) + celesta sines, 74 BPM, g 0.06 | Scene `museum` |
| layer_shop (T2) | soft wood ticks: sine 800Hz, 30ms, 8/8, g 0.03 | Shop modal open |
| layer_build (T2) | kalimba tick: triangle 1046Hz, 40ms, sparse, g 0.03 | Build mode active |
| amb_village (T2) | pink-ish noise lowpass 400Hz g 0.02 + bird blips (sine 2200→2600, 60ms) every 4–8s | Biome `Village` |
| amb_berry (T2) | noise bandpass 3000Hz g 0.015 + insect chirp pattern | Biome `Berry Grove` |
| amb_ore (T2) | noise lowpass 250Hz g 0.02 + rare stone tap (rows 11-style, 10% gain) | Biome `Ore Ridge` |
| amb_lake (T2) | noise bandpass 500Hz, gain LFO 0.2Hz, g 0.02 + soft lap blips | Biome `Lakeside` |
| amb_home (T2) | noise lowpass 150Hz g 0.015 + lamp hum sine 120Hz g 0.01 | Scene `home` |
| amb_museum (T2) | noise lowpass 300Hz g 0.012 | Scene `museum` |

Stingers (goal/shop/museum/final) are SFX rows 23–26 playing over current music; no separate music-stinger files.

---

# 7. UX

HTML + CSS only (DOM in `#ui-root` over the canvas). Skin per §3 (parchment/wood/brass; panels 2px `#5C4032` border, 3px radius; button states; brass tab underline; min text 12px; important text always on a panel).

**Screens as a state machine** (sim paused in TITLE / SHOP / LEDGER / SETTINGS / COMPLETION; not paused in PLAY or BUILD):

| State | Enters on | Exits on |
| --- | --- | --- |
| TITLE | Load | Start → newGame → PLAY-WORLD; Continue → load → PLAY-{scene}; Settings button → SETTINGS |
| PLAY-WORLD / PLAY-HOME / PLAY-MUSEUM | Start/Continue, scene change via doors | `E` on shopkeeper → SHOP; `C` → LEDGER; `P` → SETTINGS; `B` (interiors) → BUILD; `curatorsSeal` complete → COMPLETION |
| BUILD (sub-state of PLAY-HOME/PLAY-MUSEUM) | `B` in interior (else `invalid:action` + toast) | `Esc` (cancel selection, then exit); `B` again |
| SHOP | `E`/left-click on a shopkeeper in range | `Esc` |
| LEDGER | `C` | `C` or `Esc` |
| SETTINGS | `P` / title button | `Esc` |
| COMPLETION | `completion:completed` (auto) | Continue button → PLAY (scene unchanged) |

Context rules: while a modal is open, world input is ignored; during an active fishing sequence, only the interact strike is honored (no modal toggles) until the attempt resolves.

**HUD table** (element → record field → when visible):

| Element | Record field | When visible |
| --- | --- | --- |
| Location label (zone name + 16px icon) | derived biome label (`scene` + player position) | Always in PLAY/BUILD |
| Ledger button (book icon, `C` hint, gold dot if active goal) | `goals` (any incomplete ⇒ dot) | PLAY |
| Coins (pill, coin icon `#E5C158`; +N/−N float; pulse) | `player.coins` | PLAY, SHOP |
| Minimap 96×96 (wood frame, parchment; biome colors; player white dot + direction triangle; home/museum/trading-post icons; no resource nodes) | `player.x/y` + static building dots; in interiors, player dot sits on the building dot | PLAY |
| Tool tier pips ×3 (32px icon, category ring, 1–3 gold pips; empty pips `#5C4032`, filled `#D9A441`) | `player.tools.berry/ore/fish` | PLAY |
| Inventory: 10 slots 28×28 (icon + stack count; empty = faint dashed border) | `player.inventory[0..9]` | PLAY |
| Slot tooltip (name, count, base price, current shop price if near matching shopkeeper) | slot + `resources` + `ShopSystem.unitPrice` | PLAY, slot hover |
| Contextual hints (key caps, only what applies) | derived from `scene`, `build`, `target` | PLAY |
| Interaction prompt (parchment pill, icon, key hint; locked = grey + lock + requirement text) | `state.target` → §4.2 prompt table | `target ≠ null` |
| Gathering progress bar 160×12 (gold fill, category icon) | `activeGather.progress` | `activeGather ≠ null` |
| Fishing meter 240×20 (green/yellow zones, white indicator; `Strike!` prompt) | `fishing.meterProgress` | `fishing.state = "biteMeter"` |
| Toasts top-center (≤3 visible, stack downward, older fades first; 320×44; 4px left color bar; 3s; slide down 16px; types: Goal Complete `#D9A441`, Shop Unlock `#86E8FF`, Museum Unlock `#C7A24A`, New Specimen `#8E7BD1`, Tool Purchase `#D9A441`, Furniture Purchase `#8A5A3B`, Coin Gain `#E5C158`, Error `#D96A5A`, Save `#6FBF73`) | event-driven queue | on events |
| Shop modal 640×420: name, coins, Buy/Sell tabs; Sell rows (icon, name, stack, unit price, stack total, Sell / Sell-stack / Sell All); supply meter 5 segments 24×10 + label; Buy grid cards (icon, name, cost, description, Buy; locked = 30% alpha + lock + requirement text; unaffordable = disabled button) | `shops[shopId].supply/cumulativeSold`, inventory, `content.furniture/tools`, `player.coins` | SHOP |
| Ledger modal 640×440: Goals tab (active goal brass-bordered with progress fraction + reward; completed checkmarked); Collection tab (3×3 grid: icon/silhouette, name, hint, exhibit score, `Displayed` badge); Scores tab (Home Score, Museum Score, furniture/exhibit counts) | `goals`, `sales`, `collection`, `placed`, scores | LEDGER |
| Build UI: floor grid, ghost (green/red 40% + reason pill), selected item card (icon, name, footprint, rotation, validity, reason), build-inventory side panel (icon, name, footprint, resell value, museum badge; selected = brass outline), resell panel (refund amount + Sell), exhibit panel (case name, slots, assigned/empty, unassigned list, Assign/Remove), building score | `build.*`, `canPlace` result, `buildInventory`, `placed[].display`, scores | BUILD |
| Settings rows (3 volume sliders 0–1; Reduce Motion, High Contrast toggles) | `settings.*` | SETTINGS |
| Completion screen (edge dim, seal stamp, `Curator’s Seal Complete` / `Your museum is open.`, slow gold-leaf particles (T2 juice), Continue) | `completion` | COMPLETION |

First-run UX: title screen lists controls (`WASD` move, `E` interact, `C` ledger, `B` build inside buildings); on first world moment, toast `Goal: First Harvest` and ledger gold dot; first new specimen ⇒ toast `New Specimen: {name}`; first build-mode entry ⇒ one-time hint (T2).

---

# 8. DEBUG API

Exposed only when running with `?test=1`: `window.__game = core`, `window.__content = content`, `window.__world = core.world` (read-only generated definitions). Never attached on normal URLs.

**8.1 Player inputs as functions** (production core API — tests drive the game through these):

`setMoveInput(dx, dy)` · `interactDown()` · `interactUp()` · `openShop(shopId)` · `closeShop()` · `buyItem(shopId, itemId)` · `sellOne(shopId, resourceId)` · `sellStack(shopId, resourceId)` · `sellAll(shopId)` · `openLedger()` · `closeLedger()` · `toggleBuild()` · `selectBuildItem(instanceId)` · `selectPlacedItem(instanceId)` · `rotateBuildItem()` · `setBuildAnchor(x, y)` · `placeBuildItem()` · `removePlacedItem(instanceId)` · `sellBuildItem(instanceId)` · `assignSpecimen(buildingId, instanceId, slotIndex, resourceIdOrNull)` · `setSettings(partial)` · `saveGame()` · `loadGame(data)` · `newGame()` · `setPaused(bool)` · `update(dt)` · `init()`

**8.2 Test harness helpers** (`tests/harness/headless.js`; all calls used by §9):

`createHeadlessGame({ seed, runtimeRng, saveAdapter }) → core` · `advance(game, seconds, step = 0.016)` · `getEvents(game) → [events]` (recorded event log) · `interactFor(game, seconds)` (interactDown + advance + interactUp) · `releaseInteract(game)` · `teleport(game, x, y)` (test-only; uses `debug.teleport`) · `walkTo(game, x, y)` (BFS + real movement updates) · `findPlaceableTile(game, buildingId, itemId, rotation) → {x,y} | null`. `MockRNG(values)` per engineering (queue of `next()` values; `range`, `int`).

**8.3 Debug state functions** — one direct-state reach per gameplay system (test-only; not part of production behavior; no-op-safe):

| System | Functions |
| --- | --- |
| Player | `debug.setCoins(n)` · `debug.teleport(x, y)` · `debug.setScene("world"|"home"|"museum")` (places player at the door) |
| Inventory | `debug.giveResource(resourceId, n)` · `debug.clearInventory()` · `debug.fillInventory()` (all 10 slots at stack limits) |
| Nodes | `debug.setNodeState(nodeId, { empty?, count?, charges?, respawn? })` · `debug.fillAllNodes(resourceId?)` (all nodes of a type, or all) |
| Fishing | `debug.setFishing(spotId, "casting"|"waiting"|"biteMeter", progress = 0)` · `debug.setFishCooldown(spotId, s)` |
| Shops | `debug.setSupply(shopId, v)` · `debug.setCumulativeSold(shopId, n)` |
| Build | `debug.giveFurniture(itemId)` (add to buildInventory, `hasBeenPlaced:false`) · `debug.forcePlace(buildingId, itemId, x, y, rotation)` (bypasses `canPlace`, records placed + display slots) · `debug.clearFurniture(buildingId)` (all placed → buildInventory, `hasBeenPlaced:true`, specimens unassigned) |
| Museum | `debug.collectAll()` (all `collection` true + `specimen:unlocked` events) |
| Goals | `debug.setGoalComplete(goalId, bool)` (test-only latch set; `true` grants reward/unlock once) |
| Scores | `debug.readScores() → { home, museum }` |
| Save | `debug.saveNow()` · `debug.loadFresh()` · `debug.resetAll()` |
| UI | `debug.toast(text, type)` · `debug.openSettings()` |

---

# 9. TESTS

`npm test` runs unit + integration in Node with zero runtime dependencies and no DOM (GameCore is headless). Every check below is driven only by §8 calls; every expected value follows from §4. (Visual’s §30 acceptance checklist is enforced through the E2E smoke test and the SCREENSHOTS table below.)

**tests/unit/content.test.js**
- All 9 resources exist; categories ⊆ {berry, ore, fish}; base prices 2/5/12/4/10/25/4/10/25; stack limits 20/10/5 per category; quotas 30/15/5/25/12/4/15/8/3; respawns 20/45/120/300/360/720 (fish none); ore charges 3; exhibit scores 10/25/60 per tier.
- 9 tools with correct shop/category/tier/cost (owned, 35, 90 ×3 categories); tier effect tables match §4.4/§4.5 exactly (times 0.80/0.65/0.55 and 1.20/0.95/0.80; bonuses 0/.30/.60; fish green 0.30/0.40/0.50, yellow 0.40/0.55/0.70, bonus 0/.25/.50, cooldown 3.0/2.5/2.0, waits 1.0–3.0 / 0.8–2.5 / 0.6–2.0).
- 18 furniture rows: shop, unlockTier, size, cost, type, museumOnly, unique, slots per the §4 roster; display cases total exactly 9 slots; totals 14 decor / 4 display.
- 3 shopkeepers at `(58,65)`, `(60,65)`, `(62,65)` with correct categories.
- Goals in order 1–6 with the exact §4.11 requirements and rewards; requirement types reference valid resources/categories/buildings.
- Buildings: home 10×8 door (5,7) exterior (52,68); museum 12×10 door (6,9) exterior (68,68); museum `lockedInitially:true`.
- Audio: every §6 recipe ID resolves in `src/audio/recipes.js`.

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
- 6 tiles in 1s on grass; diagonal not faster than straight; 3 tiles in 1s on water (shallow and deep); cannot enter perimeter, berry node, or ore node; can cross water; enter/exit Home via door interaction; museum door blocked while locked, enterable after `debug.setGoalComplete("firstTrades", true)`; target selection respects 1.2-tile radius and tie priority; prompts match the §4.2 table (including `Museum Locked` with exact requirement text and `Bag Full` after `debug.fillInventory`).

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
- New-game state matches §4 (25 coins, T1 tools, empty inventory, locked museum, all goals false). Round-trip (`debug.saveNow` → `core.loadGame`) preserves: position, coins, inventory, tool tiers, node empty/count/charges/respawn, fish cooldowns, shop supply/cumulative/lastSaleTime, sales counters, collection, buildInventory, placed furniture (+display slots), goal latches, completion, settings; non-persisted fields (target/activeGather/fishing/build) reset to null. Corrupted save and version mismatch ⇒ new game, no throw.

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

**SCREENSHOTS** (synthesized from visual’s §18 UX journey, §27 moments, and §30 acceptance checklist; each reachable by §8 calls; pass = the listed visual content is present and correct):

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

---

# 10. BUILD ORDER

Milestones (derived from engineering’s structure and acceptance criteria — it shipped no milestone list; §0.2 ruling), each naming the §9 check that proves it landed:

| Milestone | Scope | Proof (section 9) |
| --- | --- | --- |
| M1 | Bootstrap: index.html, constants, content.js + ContentValidator, package scripts, serve | content.test.js (all assertions) |
| M2 | SeededRNG, WorldGenerator (terrain/lake/paths/buildings/nodes/fish), Pathfinding | worldGenerator.test.js + rng.test.js + pathfinding.test.js |
| M3 | GameCore, EventBus, PlayerSystem (movement/collision/scene), InteractionSystem, InventorySystem | movement.test.js + inventory.test.js |
| M4 | NodeSystem, GatheringSystem, FishingSystem | gathering.test.js + fishing.test.js |
| M5 | ShopSystem, GoalSystem, ScoreSystem | economy.test.js + shop.test.js + goals.test.js |
| M6 | BuildSystem, MuseumSystem | build.test.js + buildFurniture.test.js + museum.test.js |
| M7 | Save adapters, save/load rules, full playthrough | save.test.js + playthrough.test.js |
| M8 | Renderer + all UI (title/HUD/minimap/shop/ledger/build/toasts/completion) | e2e smoke.spec.js + screenshots S1–S16 |
| M9 | Audio (all §6 recipes, zone music, settings application) + accessibility attributes | e2e assets.spec.js + screenshot S18 |
| M10 | Completion flow + T1 polish (prompts, toasts, feedback states) | playthrough.test.js (steps 6–7) + screenshot S17 |
| M11 | T2 staging in §0.3 order (settings modal → ambience → layers → lines → hint → juice); T3 after ship | S18, assets.spec.js ambience IDs, S2 toast, S6/S17 juice states |

---

# 11. DEFINITION OF DONE

One header per §0.1 row. When every header’s checks pass, the game is complete.

- **Open world collector game (single continuous map, free roam)** — worldGenerator.test (exact counts, masks, perimeter, reachability of every node/door/shopkeeper); screenshots S2, S3, S4, S5.
- **The player walks around** — movement.test (speeds 6/3, diagonal normalization, collision, doors, scene transitions); screenshot S2.
- **Collecting resources into an inventory** — inventory.test (slots, stacks 20/10/5, full behavior) + movement.test (`Bag Full`); screenshot S15.
- **Harvest berries** — gathering.test (berry: yield = stack, bonus rule, empty/respawn 20/45/120s, cancel); screenshot S3.
- **Mine ores** — gathering.test (ore: 3 charges, 1.20s T1, respawns 300/360/720s); screenshot S4.
- **Fish fish** — fishing.test (full state machine, zones, cooldowns, leave-fail); screenshots S5, S6.
- **Sell them to a shop keeper for each type** — shop.test + economy.test (per-category sells, pre-update prices, supply +n/5, recovery, tiers 5/25); screenshots S7, S8.
- **Buy furniture to decorate their home** — economy.test (buy rules, unique) + buildFurniture.test (place/score/refund); screenshots S9, S10.
- **Decorate a small museum-type building** — museum.test (cases, slots 9, assignment, unassignment, score, unlock); screenshot S11.
- **(added) Relaxed no-fail fantasy** — content.test (no health/fail fields in content or state); playthrough.test (no failure path exercised); DoD invariant: no rule can end the game.
- **(added) Purchasable tool tiers** — economy.test (tool rules: higher-tier only, replace, no resell) + gathering.test/fishing.test (tier tables 0.80/0.65/0.55, 1.20/0.95/0.80, green/yellow/cooldown values).
- **(added) Goals ending in Curator’s Seal** — goals.test (all six, latching, rewards) + playthrough.test (full completion, latch survives save/load); screenshot S17.
- **(added) Collection log & specimen curation** — museum.test (unlock on first collect, 9 specimens, uniqueness) + goals.test (fullCollection); screenshot S13.
- **(added) Supply-meter price fluctuation** — economy.test (multipliers 1.00/0.85/0.70/0.60, floor 1, recovery); screenshot S7.
- **(added) Non-binding Home/Museum scores** — buildFurniture.test + museum.test (value = ceil(cost/10); formulas); screenshot S14.
- **(added) Save/load persistence** — save.test (full round-trip, corrupted-save safety).
- **(added) Accessibility settings** — e2e smoke (data attributes applied) + §4.12 effects; screenshot S18.
- **(added) Deterministic world (seed 42)** — worldGenerator.test (repeat-identical, min distance ≥3, quotas exact) + rng.test.
- **(added) Cozy hand-painted pixel look** — visual acceptance: SCREENSHOTS S1–S18 pass (palette, no hard outlines, zone identity, ghost colors, no color-only states, 12px minimum text, node/charge/fish states readable).
- **(added) Calm generated audio** — e2e assets (every recipe renders) + §6 table complete (26 SFX + 15 music/ambience recipes) with volume defaults 0.7/0.8/0.5.

---

# A. SANITY

Re-read of §2, §4, §8, §9, checked and fixed in place:

1. **Global-context completeness** — walked every field the §4 rules read or write: `time, scene, player.{x,y,coins,tools,inventory}, target, activeGather, fishing, build, nodes, fishSpots, shops, sales, collection, buildInventory, nextInstanceId, placed, goals, museumUnlocked, completion, settings`. *Finding: engineering’s state shape (§10) omitted `activeGather`, `fishing`, `build`, and `target` while its own §17/§18/§20 referenced them.* **Fixed**: all four added to §2.2 as non-persisted fields. **Closes.**
2. **Places/things/kinds placed or rostered** — 9 resources → generator quotas + submasks (§4.2); 26 fish spots → generator; 3 shopkeepers → content positions; 2 doors + 2 exits + footprints → buildings roster; 6 path runs → generator; 5 zone masks → content/constants; start tile `(57,70)` → content; 18 furniture + 9 tools → content roster; 6 goals, 9 specimens → content. No rule names an unplaced thing. **Closes.**
3. **Consumables: placed vs demanded** —
   - Berries: 50 nodes × 1–2 = 50–100 per respawn cycle (20–120s) vs demand 25 sold + 9 collection ⇒ **closes** (≥4 cycles of headroom; respawns restore).
   - Ores: 41 nodes × 3 = 123 charges (respawn 300–720s) vs 25 sold + collection ⇒ **closes**.
   - Fish: 26 non-depleting spots, cooldown ≤ 3.0s vs 25 sold + collection ⇒ **closes**.
   - Furniture: demand = 12 museum + 5 home placed vs supply = 14 decor kinds (repeatable, tier-1 from start) + 4 unique display (3 required by Open Museum; 4 required by the 9 slots) ⇒ **closes**.
   - Coins (worst case for the full goal set): 25 start + 235 goal rewards + minimum sale income. Minimum sale income occurs when all 25+25+25 units are dumped at supply 3.0 (0.60 multiplier, floor 1): 25×`max(1,floor(2×0.6))` + 25×`floor(4×0.6)` + 25×`floor(4×0.6)` = 25×1 + 25×2 + 25×2 = 125. Total = 385. Maximum required spend: 4 display cases (40+35+80+80 = 235) + 8 museum decor @10 = 80 + 5 home decor @10 = 50 ⇒ 365. 385 ≥ 365 ⇒ **closes** (margin 20; supply recovery only widens it).
4. **Timing pairs** —
   - Pick (0.55–0.80s) vs berry respawn (20–120s): **closes**.
   - Full ore node work (3 × 0.80–1.20s = 2.4–3.6s) vs regrow (300–720s): **closes**.
   - Fishing worst cycle: cast 0.6 + wait ≤ 3.0 + meter 1.5 + cooldown ≤ 3.0 = ≤ 8.1s vs non-depleting spots: **closes**.
   - Supply drain (+n/5, cap 3.0) vs recovery (1/120s): worst 3.0 → 0.0 in 360s; price floor 1 prevents permanent ruin: **closes**.
   - Travel: longest village→zone leg ≈ 28 tiles (plaza y=66 to berry edge y=38) = 4.7s at 6 t/s, within the 3–6s design band: **closes**.
   - Bite meter: green window 0.30s/1.5s at 60Hz ≈ 18 frames in-zone; yellow fallback 40–70%: **closes AND bites** (still a timing skill).
   - End-condition clock: no timer exists; the 2–3h target is pacing guidance, not a rule: **closes** (nothing to miss).
5. **Progression graph** — Open Museum needs 3 display cases; only 2 are tier-2 (small_display_case, pedestal), so a tier-3 (25 category sales) is required first — reachable in-world ⇒ **closes**. Curator’s Seal needs 9 slots = all 4 cases, including the two tier-3 cases, whose unlock sales (25 ore, 25 fish) are already requirements of the same goal ⇒ **closes**.
6. **Every call in §9 is in §8** — calls used: `core.{init,newGame,update,setMoveInput,interactDown,interactUp,openShop,closeShop,buyItem,sellOne,sellStack,sellAll,openLedger,closeLedger,toggleBuild,selectBuildItem,selectPlacedItem,rotateBuildItem,setBuildAnchor,placeBuildItem,removePlacedItem,sellBuildItem,assignSpecimen,setSettings,saveGame,loadGame,setPaused}`; `harness.{createHeadlessGame,advance,getEvents,interactFor,releaseInteract,teleport,walkTo,findPlaceableTile,MockRNG}`; `debug.{setCoins,teleport,setScene,giveResource,clearInventory,fillInventory,setNodeState,fillAllNodes,setFishing,setFishCooldown,setSupply,setCumulativeSold,giveFurniture,forcePlace,clearFurniture,collectAll,setGoalComplete,readScores,saveNow,loadFresh,resetAll,toast,openSettings}` — all present in §8.1–8.3. **Closes.**
7. **Placeholders** — no angle-bracket placeholders exist in the merged spec; the three source documents contained none either. **Closes.**

All checks pass; sections above already carry the one fix (item 1). The spec is final.