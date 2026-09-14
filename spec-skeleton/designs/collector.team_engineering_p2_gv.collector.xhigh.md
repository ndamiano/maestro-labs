# engineering.md

## 1. Engineering Summary

This document defines the engineering structure for the HTML/CSS/JS collector game. It is written for an integrating engineer who will implement the game from the gameplay and visual design documents.

The engineering design is based on:

- A headless simulation core that can run in Node.js without DOM, canvas, or audio.
- Content-driven data so resources, tools, furniture, goals, and audio mappings are data, not hard-coded logic.
- Deterministic world generation using the gameplay seed.
- A clear split between simulation, UI, rendering, audio, and input.
- A test harness that validates logic, content, world generation, save/load, and full playable completion.
- Scalable, low-complexity code for a compact 2D top-down browser game.

The game is not designed to be extensible to arbitrary genres. It is designed to support the exact scope in the gameplay document while leaving room for small content additions without rewriting systems.

---

## 2. Important Engineering Decisions

### 2.1 Headless Core

The game logic lives in `GameCore`.

`GameCore` must not directly use:

- `document`
- `window`
- `canvas`
- `localStorage`
- `AudioContext`
- `HTMLAudioElement`
- `requestAnimationFrame`

This allows the full simulation to be tested in Node.js.

The browser layer wires:

- Input into `GameCore` actions.
- `GameCore` events into UI and audio.
- `GameCore` state into the renderer.

### 2.2 Content Is Data

All gameplay content lives in `src/content/content.js`.

The simulation must not contain hard-coded resource names, furniture prices, goal thresholds, or audio event names except through content or generic systems.

This makes the game easier to test and easier to balance.

### 2.3 Deterministic World

The outdoor world is generated deterministically from seed `42`.

The save file stores player and runtime state, but not the full generated node list.

On load:

1. The world generator rebuilds node and fish spot definitions from the seed.
2. Saved node/fish/shop state is applied to those definitions.

This keeps saves small and ensures the world layout is stable.

### 2.4 No Runtime Dependencies

The game runtime should use only:

- HTML
- CSS
- ES modules
- Canvas 2D
- DOM
- Web Audio / HTML audio
- `localStorage`

No game engine is required.

Optional development dependencies are allowed only for testing, such as Playwright.

### 2.5 Cut List

The following are intentionally cut:

| Cut Item | Reason |
|---|---|
| Touch controls | The design is keyboard/mouse. Touch would add input complexity without improving the core fantasy. |
| Multiple save slots | One save is enough for a single-player relaxed game. |
| Cloud save | Adds network and account complexity. |
| Custom map editor | The gameplay designer defines zones and quotas; runtime generation is enough. |
| Procedural texture generation | Visual assets are provided. Runtime texture generation would duplicate art responsibility. |
| Dynamic lighting | Not needed for readability and increases complexity. |
| Particle system | Small sprite/DOM feedback is enough. A particle system is not necessary for the calm visual style. |
| Screen shake | Would contradict the calm tone. |
| Full A* pathfinding | BFS is enough for placement validation and test bots. |
| Separate inventory screen | Persistent inventory is enough. |
| Manual stack splitting | Not required by gameplay. |
| Day/night, weather, parallax | Cut by visual design and not needed by gameplay. |
| Mobile optimization pass | Desktop browser is the target. |
| Replay system | Not required. |
| Achievements outside goals | Goals already provide progression. |

---

## 3. Files That Should Exist

The integrating engineer should create the following file structure.

```text
index.html
package.json
scripts/serve.mjs
styles/main.css

src/main.js
src/config/constants.js
src/content/content.js
src/assetManifest.js

src/core/GameCore.js
src/core/EventBus.js
src/core/SeededRNG.js
src/core/ContentValidator.js
src/core/SaveAdapter.js
src/core/LocalStorageSaveAdapter.js
src/core/InMemorySaveAdapter.js
src/core/AssetLoader.js

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
tests/harness/mockRNG.js
tests/harness/testUtils.js

tests/unit/content.test.js
tests/unit/rng.test.js
tests/unit/pathfinding.test.js
tests/unit/inventory.test.js
tests/unit/economy.test.js
tests/unit/build.test.js
tests/unit/goals.test.js
tests/unit/worldGenerator.test.js

tests/integration/movement.test.js
tests/integration/gathering.test.js
tests/integration/fishing.test.js
tests/integration/shop.test.js
tests/integration/buildFurniture.test.js
tests/integration/museum.test.js
tests/integration/save.test.js
tests/integration/playthrough.test.js

tests/e2e/playwright.config.js
tests/e2e/smoke.spec.js
tests/e2e/assets.spec.js
```

### File Responsibilities

#### Root

- `index.html`: Loads the canvas, UI containers, and `src/main.js`.
- `package.json`: Defines module type, test scripts, and static server script.
- `scripts/serve.mjs`: Simple static file server for local development and E2E.
- `styles/main.css`: All UI skin, layout, accessibility classes, and HUD styling.

#### Source

- `src/main.js`: Browser bootstrap. Creates core, UI, renderer, audio, input, and runs the frame loop.
- `src/config/constants.js`: Constants such as tile size, world size, speeds, radii, and save version.
- `src/content/content.js`: All game content data.
- `src/assetManifest.js`: Semantic asset IDs mapped to visual/audio files or atlas regions.

#### Core

- `GameCore.js`: Main simulation object. Owns state and systems.
- `EventBus.js`: Tiny event pub/sub.
- `SeededRNG.js`: Deterministic RNG for world generation and runtime random events.
- `ContentValidator.js`: Validates content structure on startup.
- Save adapters:
  - `SaveAdapter.js`: Interface or base behavior.
  - `LocalStorageSaveAdapter.js`: Browser save.
  - `InMemorySaveAdapter.js`: Test save.
- `AssetLoader.js`: Loads images, atlases, and audio files.

#### World

- `Tiles.js`: Tile type constants and helpers.
- `WorldGenerator.js`: Generates terrain, paths, buildings, nodes, and fish spots.
- `Pathfinding.js`: BFS pathfinding for placement checks and test bots.

#### Systems

Each system owns one simulation concern.

- `PlayerSystem.js`: Movement, collision, scene position, water speed.
- `InteractionSystem.js`: Target selection, prompts, door/shop/node/fish interaction.
- `InventorySystem.js`: Resource inventory rules.
- `NodeSystem.js`: Berry/ore node state and respawn.
- `GatheringSystem.js`: Hold-to-pick and hold-to-mine progress.
- `FishingSystem.js`: Fishing state machine.
- `ShopSystem.js`: Selling, buying, supply meters, shop tiers.
- `BuildSystem.js`: Build mode, placement validation, removal, reselling.
- `MuseumSystem.js`: Display cases, specimen assignment, museum score.
- `GoalSystem.js`: Goal evaluation, rewards, unlocks, completion.
- `ScoreSystem.js`: Home and museum score calculation.

#### Input

- `InputManager.js`: Maps keyboard/mouse events to core actions and UI actions.

#### Render

- `CanvasRenderer.js`: Draws world/interiors to canvas.
- `Camera.js`: Camera position and clamping.
- `SpriteRenderer.js`: Draws sprites from manifest/atlas with animation and y-sort support.

#### UI

UI is DOM-based.

- `UIRoot.js`: Owns modal lifecycle and applies accessibility classes.
- `TitleUI.js`: Start/Continue/title screen.
- `HUD.js`: Persistent HUD.
- `MinimapUI.js`: Minimap rendering.
- `ShopUI.js`: Shop modal.
- `LedgerUI.js`: Ledger modal.
- `BuildUI.js`: Build mode panels.
- `ToastUI.js`: Toast notifications.
- `SettingsUI.js`: Audio and accessibility settings.
- `CompletionUI.js`: Final completion screen.

#### Audio

- `AudioManager.js`: Loads audio, plays SFX, manages music/ambience layers, applies volumes.

---

## 4. `package.json`

Required scripts:

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

Runtime dependencies: none.

Optional development dependency:

```text
@playwright/test
```

If Playwright is not installed, `npm test` must still pass. `npm run test:e2e` may fail until the dev dependency is installed.

---

## 5. `index.html`

`index.html` should contain:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Collector Game</title>
    <link rel="stylesheet" href="./styles/main.css" />
  </head>
  <body>
    <main id="game-root">
      <canvas id="game-canvas" width="960" height="540"></canvas>
      <div id="ui-root"></div>
    </main>
    <script type="module" src="./src/main.js"></script>
  </body>
</html>
```

The canvas is the world renderer. The UI root is DOM.

The canvas should be scaled with CSS to fit the window while preserving the `960 x 540` design resolution.

Use:

```css
image-rendering: pixelated;
```

for canvas sprites.

---

## 6. Constants

`src/config/constants.js` must define:

```js
export const TILE_SIZE = 24;
export const WORLD_SIZE = 120;
export const VIEW_WIDTH = 960;
export const VIEW_HEIGHT = 540;

export const PLAYER_SPEED = 6;
export const WATER_SPEED = 3;
export const INTERACT_RADIUS = 1.2;

export const INVENTORY_SLOTS = 10;

export const SAVE_VERSION = 1;
export const WORLD_VERSION = 1;
export const WORLD_SEED = 42;

export const FISHING = {
  CAST_TIME: 0.6,
  METER_TIME: 1.5,
  YELLOW_ZONE_TIME: 0.2
};

export const SHOP = {
  SUPPLY_MAX: 3.0,
  SUPPLY_SALE_INCREMENT: 1 / 5,
  RECOVERY_INTERVAL: 120,
  TIER_THRESHOLDS: [0, 5, 25]
};
```

---

## 7. Content Model

`src/content/content.js` exports a single default object.

The integrating engineer must encode all gameplay values here.

### 7.1 Top-Level Shape

```js
export default {
  version: 1,
  worldSeed: 42,
  worldVersion: 1,

  resources: [],
  toolTiers: {},
  tools: [],
  shopkeepers: [],
  furniture: [],
  buildings: {},
  goals: [],
  collection: [],
  audio: {}
};
```

### 7.2 Resources

Each resource object:

```js
{
  id: "sweet_berry",
  name: "Sweet Berry",
  category: "berry",
  tier: 1,
  basePrice: 2,
  stackLimit: 20,
  exhibitScore: 10,
  nodeType: "berry" | "ore" | "fish",
  quota: 30,
  respawnTime: 20,
  charges: 0,
  color: "#D94F5C",
  hint: "Berry Grove, common"
}
```

Required resource table:

| ID | Category | Tier | Base Price | Stack | Quota | Respawn/Empty | Exhibit Score |
|---|---|---:|---:|---:|---:|---:|---:|
| `sweet_berry` | berry | 1 | 2 | 20 | 30 | 20s | 10 |
| `moon_berry` | berry | 2 | 5 | 20 | 15 | 45s | 25 |
| `ember_berry` | berry | 3 | 12 | 20 | 5 | 120s | 60 |
| `copper_ore` | ore | 1 | 4 | 10 | 25 | 300s | 10 |
| `silver_ore` | ore | 2 | 10 | 10 | 12 | 360s | 25 |
| `crystal_shard` | ore | 3 | 25 | 10 | 4 | 720s | 60 |
| `minnow` | fish | 1 | 4 | 5 | 15 | none | 10 |
| `trout` | fish | 2 | 10 | 5 | 8 | none | 25 |
| `moonfish` | fish | 3 | 25 | 5 | 3 | none | 60 |

Fish resources do not deplete and have no respawn time.

### 7.3 Tool Tiers

Tool effects are per category.

```js
export const toolTiers = {
  berry: [
    {
      tier: 1,
      gatherTime: 0.80,
      bonusChance: 0.0
    },
    {
      tier: 2,
      gatherTime: 0.65,
      bonusChance: 0.30
    },
    {
      tier: 3,
      gatherTime: 0.55,
      bonusChance: 0.60
    }
  ],
  ore: [
    {
      tier: 1,
      gatherTime: 1.20,
      bonusChance: 0.0
    },
    {
      tier: 2,
      gatherTime: 0.95,
      bonusChance: 0.30
    },
    {
      tier: 3,
      gatherTime: 0.80,
      bonusChance: 0.60
    }
  ],
  fish: [
    {
      tier: 1,
      waitMin: 1.0,
      waitMax: 3.0,
      greenWidth: 0.30,
      yellowSuccess: 0.40,
      bonusChance: 0.0,
      cooldown: 3.0
    },
    {
      tier: 2,
      waitMin: 0.8,
      waitMax: 2.5,
      greenWidth: 0.40,
      yellowSuccess: 0.55,
      bonusChance: 0.25,
      cooldown: 2.5
    },
    {
      tier: 3,
      waitMin: 0.6,
      waitMax: 2.0,
      greenWidth: 0.50,
      yellowSuccess: 0.70,
      bonusChance: 0.50,
      cooldown: 2.0
    }
  ]
};
```

### 7.4 Tools

Tool items are purchased from shops.

```js
{
  id: "honey_pouch",
  name: "Honey Pouch",
  shop: "moss",
  category: "berry",
  tier: 2,
  cost: 35,
  description: "Faster berry picking and bonus yield chance."
}
```

Required tools:

| ID | Shop | Category | Tier | Cost |
|---|---|---|---:|---:|
| `woven_basket` | moss | berry | 1 | owned |
| `honey_pouch` | moss | berry | 2 | 35 |
| `ember_satchel` | moss | berry | 3 | 90 |
| `hand_pick` | grit | ore | 1 | owned |
| `copper_pick` | grit | ore | 2 | 35 |
| `silver_pick` | grit | ore | 3 | 90 |
| `short_rod` | reed | fish | 1 | owned |
| `bamboo_rod` | reed | fish | 2 | 35 |
| `moon_rod` | reed | fish | 3 | 90 |

Tier 1 tools are owned at start and are not buyable.

### 7.5 Shopkeepers

```js
{
  id: "moss",
  name: "Moss",
  category: "berry",
  x: 58,
  y: 65,
  line: "Sweet berries make sweet homes."
}
```

Required shopkeepers:

| ID | Name | Category | Position |
|---|---|---|---:|
| `moss` | Moss | berry | `(58, 65)` |
| `grit` | Grit | ore | `(60, 65)` |
| `reed` | Reed | fish | `(62, 65)` |

### 7.6 Furniture

Furniture item shape:

```js
{
  id: "berry_planter",
  name: "Berry Planter",
  shop: "moss",
  unlockTier: 1,
  type: "decor",
  size: [1, 1],
  cost: 10,
  museumOnly: false,
  unique: false,
  slots: 0,
  description: "A small planter with berries."
}
```

Display cases have:

```js
{
  type: "display",
  museumOnly: true,
  unique: true,
  slots: 2
}
```

Required furniture:

| ID | Shop | Unlock Tier | Type | Size | Cost | Museum Only | Unique | Slots |
|---|---|---:|---|---:|---:|---:|---:|---:|
| `berry_planter` | moss | 1 | decor | 1x1 | 10 | no | no | 0 |
| `berry_jar` | moss | 1 | decor | 1x1 | 15 | no | no | 0 |
| `rug` | moss | 1 | decor | 2x2 | 10 | no | no | 0 |
| `berry_bench` | moss | 2 | decor | 2x1 | 45 | no | no | 0 |
| `small_display_case` | moss | 2 | display | 1x1 | 40 | yes | yes | 2 |
| `berry_rug` | moss | 3 | decor | 2x2 | 70 | no | no | 0 |
| `side_table` | grit | 1 | decor | 1x1 | 10 | no | no | 0 |
| `bookshelf` | grit | 1 | decor | 1x2 | 20 | no | no | 0 |
| `ore_lamp` | grit | 1 | decor | 1x1 | 15 | no | no | 0 |
| `ore_workbench` | grit | 2 | decor | 2x1 | 55 | no | no | 0 |
| `pedestal` | grit | 2 | display | 1x1 | 35 | yes | yes | 1 |
| `crystal_display_case` | grit | 3 | display | 1x1 | 80 | yes | yes | 3 |
| `fish_net_rack` | reed | 1 | decor | 1x1 | 10 | no | no | 0 |
| `fish_barrel` | reed | 1 | decor | 1x1 | 15 | no | no | 0 |
| `water_shelf` | reed | 1 | decor | 1x1 | 15 | no | no | 0 |
| `fish_bench` | reed | 2 | decor | 2x1 | 45 | no | no | 0 |
| `fish_tank` | reed | 2 | decor | 2x1 | 70 | no | no | 0 |
| `moon_display_case` | reed | 3 | display | 1x1 | 80 | yes | yes | 3 |

Display cases total exactly 9 exhibit slots.

### 7.7 Buildings

```js
buildings: {
  home: {
    id: "home",
    name: "Home",
    scene: "home",
    width: 10,
    height: 8,
    door: [5, 7],
    exteriorDoor: [52, 68],
    exteriorExit: [52, 69],
    lockedInitially: false
  },
  museum: {
    id: "museum",
    name: "Museum",
    scene: "museum",
    width: 12,
    height: 10,
    door: [6, 9],
    exteriorDoor: [68, 68],
    exteriorExit: [68, 69],
    lockedInitially: true
  }
}
```

### 7.8 Goals

Goals are data-driven.

```js
{
  id: "firstHarvest",
  name: "First Harvest",
  order: 1,
  rewardCoins: 10,
  unlock: null,
  completion: false,
  requirements: [
    { type: "resource_collected", resource: "sweet_berry", amount: 1 },
    { type: "resource_collected", resource: "copper_ore", amount: 1 },
    { type: "resource_collected", resource: "minnow", amount: 1 }
  ]
}
```

Required goals:

| ID | Order | Requirements | Reward / Unlock |
|---|---:|---|---|
| `firstHarvest` | 1 | collect 1 `sweet_berry`, 1 `copper_ore`, 1 `minnow` | 10 coins |
| `firstTrades` | 2 | sell 5 `sweet_berry`, 5 `copper_ore`, 5 `minnow` | 25 coins, unlock museum |
| `cozyHome` | 3 | 5 furniture placed in Home | 50 coins |
| `openMuseum` | 4 | 3 display cases placed in Museum, 3 specimens assigned | 50 coins |
| `fullCollection` | 5 | all 9 resources collected | 100 coins |
| `curatorsSeal` | 6 | 25 berry category sold, 25 ore category sold, 25 fish category sold, 9 specimens assigned, 12 museum furniture placed | completion |

Requirement types:

| Type | Fields | Meaning |
|---|---|---|
| `resource_collected` | `resource`, `amount` | Collection log count |
| `resource_sold` | `resource`, `amount` | Specific resource sold count |
| `category_sold` | `category`, `amount` | Category sold count |
| `building_furniture_count` | `building`, `amount` | Placed furniture count in building |
| `museum_display_count` | `amount` | Placed display cases in Museum |
| `specimen_assigned` | `amount` | Unique assigned specimens |
| `all_resource_collected` | none | All resources collected |

### 7.9 Audio Content

Audio mapping lives in content so audio implementation is data-driven.

```js
audio: {
  music: {
    title: "music/title_loop.ogg",
    zones: {
      village: "music/village_loop.ogg",
      berry_grove: "music/berry_grove_loop.ogg",
      ore_ridge: "music/ore_ridge_loop.ogg",
      lakeside: "music/lakeside_loop.ogg",
      home: "music/home_loop.ogg",
      museum: "music/museum_loop.ogg"
    },
    layers: {
      shop: "music/shop_layer.ogg",
      build: "music/build_layer.ogg"
    },
    stingers: {
      goalComplete: "music/goal_complete.ogg",
      shopUnlock: "music/shop_unlock.ogg",
      museumUnlock: "music/museum_unlock.ogg",
      finalCompletion: "music/final_completion.ogg"
    }
  },
  ambience: {
    village: "ambience/village.ogg",
    berry_grove: "ambience/berry_grove.ogg",
    ore_ridge: "ambience/ore_ridge.ogg",
    lakeside: "ambience/lakeside.ogg",
    home: "ambience/home.ogg",
    museum: "ambience/museum.ogg"
  },
  sfx: {
    footstepGrass: "sfx/footstep_grass.ogg",
    footstepStone: "sfx/footstep_stone.ogg",
    waterStep: "sfx/water_step.ogg",
    berryPick: "sfx/berry_pick.ogg",
    oreMine: "sfx/ore_mine.ogg",
    fishCast: "sfx/fish_cast.ogg",
    fishBite: "sfx/fish_bite.ogg",
    fishCatch: "sfx/fish_catch.ogg",
    fishFail: "sfx/fish_fail.ogg",
    coinSale: "sfx/coin_sale.ogg",
    coinBuy: "sfx/coin_buy.ogg",
    furniturePlace: "sfx/furniture_place.ogg",
    furnitureRemove: "sfx/furniture_remove.ogg",
    furnitureSell: "sfx/furniture_sell.ogg",
    uiHover: "sfx/ui_hover.ogg",
    uiClick: "sfx/ui_click.ogg",
    uiOpen: "sfx/ui_open.ogg",
    uiClose: "sfx/ui_close.ogg",
    invalid: "sfx/invalid.ogg",
    inventoryFull: "sfx/inventory_full.ogg",
    specimenAssign: "sfx/specimen_assign.ogg",
    specimenUnassign: "sfx/specimen_unassign.ogg",
    goalComplete: "sfx/goal_complete.ogg",
    shopUnlock: "sfx/shop_unlock.ogg",
    museumUnlock: "sfx/museum_unlock.ogg",
    finalCompletion: "sfx/final_completion.ogg"
  }
}
```

---

## 8. Asset Manifest

`src/assetManifest.js` maps semantic IDs to asset files or atlas regions.

This allows the visual designer’s file naming to be used without hard-coding paths everywhere.

Example:

```js
export default {
  version: 1,
  sprites: {
    "tile:grass": {
      file: "world/village/grass_01.png"
    },
    "tile:path": {
      file: "world/village/path_01.png"
    },
    "node:berry_sweet_full": {
      file: "nodes/berry/sweet_full_01.png"
    },
    "node:berry_sweet_empty": {
      file: "nodes/berry/sweet_empty_01.png"
    },
    "node:ore_copper_3": {
      file: "nodes/ore/copper_3.png"
    },
    "player:idle_n": {
      files: [
        "player/idle_n_00.png",
        "player/idle_n_01.png"
      ]
    },
    "furniture:berry_planter": {
      file: "furniture/berry/planter_1x1.png"
    },
    "icon:resource:sweet_berry": {
      file: "icon/resource/sweet_berry.png"
    }
  },
  atlases: []
};
```

If atlases are provided, use atlas regions:

```js
"tile:grass": {
  atlas: "world",
  x: 0,
  y: 0,
  width: 24,
  height: 24
}
```

The `AssetLoader` must support both individual files and atlas regions.

---

## 9. World Generation

The world generator turns content, seed, and zone masks into a playable tile map plus node/fish spot definitions.

It does not create save data. It creates stable world definitions.

### 9.1 Tile Types

`src/world/Tiles.js` should define numeric tile IDs.

Required tile types:

| Tile ID | Name | Walkable | Solid | Notes |
|---:|---|---:|---:|---|
| 0 | `grass` | yes | no | Default outdoor ground |
| 1 | `path` | yes | no | Village paths |
| 2 | `shallow_water` | yes | no | Water, slow movement |
| 3 | `deep_water` | yes | no | Water, slow movement |
| 4 | `perimeter` | no | yes | Impassable border |
| 5 | `wall_home` | no | yes | Home exterior wall |
| 6 | `wall_museum` | no | yes | Museum exterior wall |
| 7 | `door_home_ext` | yes | no | Home exterior door |
| 8 | `door_museum_ext` | yes | no | Museum exterior door |
| 9 | `berry_ground` | yes | no | Berry grove ground |
| 10 | `ore_ground` | yes | no | Ore ridge ground |

Interior scenes use their own small grids. Interior floor tiles are walkable, walls are outside the floor bounds.

### 9.2 World Layout

World size: `120 x 120`.

Coordinates:

```text
x: 0..119
y: 0..119
```

Perimeter:

```text
x < 2 || x >= 118 || y < 2 || y >= 118
```

The perimeter is solid.

Zone masks:

| Zone | Mask |
|---|---|
| Village | `x: 45..75`, `y: 45..75` |
| Berry Grove | `x: 25..95`, `y: 5..38` |
| Ore Ridge | `x: 82..115`, `y: 30..90` |
| Lake | `x: 5..40`, `y: 40..100` |

### 9.3 Building Footprints

Home exterior:

```text
x: 49..55
y: 64..69
door: (52, 68)
front tile: (52, 69)
```

Museum exterior:

```text
x: 65..71
y: 64..69
door: (68, 68)
front tile: (68, 69)
```

All building footprint tiles are `wall_home` or `wall_museum`, except the door tile.

The door tile is walkable. The player interacts with it to enter/exit.

### 9.4 Path Layout

Paths are carved after terrain and before node placement.

Required paths:

```text
North path: x=60, y=39..66
East path: y=70, x=65..82
West path: y=70, x=15..64
Plaza: x=56..64, y=66..70
Home front: x=50..54, y=69
Museum front: x=66..70, y=69
```

Paths should not be carved onto solid perimeter or building walls. If a path tile is water, leave it water; water is walkable.

### 9.5 Lake Generation

The lake is generated deterministically inside the lake mask.

Use an ellipse:

```text
center = (22, 70)
rx = 17
ry = 29
```

For each tile in the lake mask:

```text
dx = x - center.x
dy = y - center.y
if (dx*dx)/(rx*rx) + (dy*dy)/(ry*ry) <= 1:
    tile = water
```

After water is placed:

- If a water tile has at least one orthogonal non-water neighbor, mark it `shallow_water`.
- Otherwise mark it `deep_water`.

All water is walkable and slows movement.

### 9.6 Biome Labels

Biome priority for location label:

1. Interior scene: `Home` or `Museum`.
2. Water or lake mask: `Lakeside`.
3. Berry Grove mask: `Berry Grove`.
4. Ore Ridge mask: `Ore Ridge`.
5. Village mask: `Village`.
6. Default: `Village`.

### 9.7 Node Placement Algorithm

The generator places land nodes for berries and ores.

Pseudo-code:

```text
function generateWorld(seed, content, rng):
    map = createGrassMap()
    setPerimeter(map)
    setZoneGround(map)
    generateLake(map)
    carvePaths(map)
    placeBuildings(map)

    nodes = []
    fishSpots = []

    for resource in content.resources:
        if resource.nodeType == "berry":
            placeNodes(resource, map, nodes, rng)
        if resource.nodeType == "ore":
            placeNodes(resource, map, nodes, rng)
        if resource.nodeType == "fish":
            placeFishSpots(resource, map, fishSpots, rng)

    return {
        map,
        biomes,
        nodes,
        fishSpots,
        doors,
        interiors,
        start
    }
```

### 9.8 Node Placement Rules

For each land resource:

```text
placed = 0
quota = resource.quota
minDistance = 4
attempts = 0

while placed < quota and attempts < 1000:
    tile = randomTileInResourceMask(rng, resource)
    if isValidNodeTile(tile, resource, map, nodes, minDistance):
        addNode(tile, resource)
        placed += 1
    attempts += 1

if placed < quota:
    minDistance = 3
    reset attempts and retry

if placed < quota:
    minDistance = 1
    reset attempts and retry

if placed < quota:
    throw content validation error
```

For seed `42`, the game must reach exact quotas without falling back to minimum distance `1`.

### 9.9 Node Tile Validity

A tile is valid for a land node if:

- It is inside the resource’s biome mask.
- It is not perimeter.
- It is not water.
- It is not path.
- It is not a building wall or door.
- It is not within 2 tiles of any exterior door.
- It is at least `minDistance` tiles from every existing node.
- It is not already occupied.

Distance uses Euclidean distance between tile centers.

### 9.10 Resource Submasks

#### Berries

| Resource | Mask |
|---|---|
| `sweet_berry` | full Berry Grove mask |
| `moon_berry` | Berry Grove mask and `y >= 20` |
| `ember_berry` | Berry Grove mask and `y <= 12` |

#### Ores

| Resource | Mask |
|---|---|
| `copper_ore` | full Ore Ridge mask |
| `silver_ore` | Ore Ridge mask and `x >= 98` |
| `crystal_shard` | Ore Ridge mask and `x >= 112` |

#### Fish

| Resource | Mask |
|---|---|
| `minnow` | water tiles adjacent to non-water |
| `trout` | non-shore water tiles with normalized lake distance <= `0.7` |
| `moonfish` | water tiles with `y >= 85` |

If a fish submask does not contain enough valid tiles, relax in this order:

1. Minimum distance from `2` to `1`.
2. Use all non-shore water for trout.
3. Use all water for moonfish.

With the default lake shape, the masks should be sufficient.

### 9.11 Fish Spot Placement

Fish spots are placed on water tiles.

Rules:

- Each fish spot has one fixed resource.
- No two fish spots occupy the same tile.
- Fish spots do not block movement.
- Initial minimum distance between fish spots is `2` tiles.
- If quota is not reached, retry with minimum distance `1`.
- Fish spots must not be in the perimeter.

### 9.12 Initial Node State

Berry nodes:

```text
state = "full"
count = rng.int(1, 2)
respawn = 0
```

Ore nodes:

```text
state = "full"
charges = 3
respawn = 0
```

Fish spots:

```text
cooldown = 0
```

### 9.13 Interiors

Interiors are separate scenes.

Home interior:

```text
floor width = 10
floor height = 8
door = (5, 7)
```

Museum interior:

```text
floor width = 12
floor height = 10
door = (6, 9)
```

Interior coordinates are local to the building.

Walls are represented by tiles outside the floor bounds.

The door tile is walkable and cannot have furniture placed on it.

### 9.14 Start Position

Player starts in the village near the home.

Recommended start tile:

```text
(57, 70)
```

Player position is stored as tile-space floats. Tile center:

```text
x = tileX + 0.5
y = tileY + 0.5
```

---

## 10. Core State Shape

`GameCore.state` is the serializable simulation state.

```js
{
  version: 1,
  worldVersion: 1,
  seed: 42,

  time: 0,

  scene: "world" | "home" | "museum",

  player: {
    x: 57.5,
    y: 70.5,
    coins: 25,
    tools: {
      berry: 1,
      ore: 1,
      fish: 1
    },
    inventory: [
      null,
      { resourceId: "sweet_berry", count: 3 },
      null
    ]
  },

  nodes: {
    "berry_sweet_30_12": {
      empty: false,
      count: 2,
      respawn: 0
    },
    "ore_copper_85_60": {
      empty: false,
      charges: 2,
      respawn: 0
    }
  },

  fishSpots: {
    "fish_minnow_20_70": {
      cooldown: 0
    }
  },

  shops: {
    moss: {
      supply: 0,
      cumulativeSold: 0,
      lastSaleTime: null
    },
    grit: {
      supply: 0,
      cumulativeSold: 0,
      lastSaleTime: null
    },
    reed: {
      supply: 0,
      cumulativeSold: 0,
      lastSaleTime: null
    }
  },

  sales: {
    byResource: {
      sweet_berry: 0,
      moon_berry: 0,
      ember_berry: 0,
      copper_ore: 0,
      silver_ore: 0,
      crystal_shard: 0,
      minnow: 0,
      trout: 0,
      moonfish: 0
    },
    byCategory: {
      berry: 0,
      ore: 0,
      fish: 0
    }
  },

  collection: {
    sweet_berry: false,
    moon_berry: false,
    ember_berry: false,
    copper_ore: false,
    silver_ore: false,
    crystal_shard: false,
    minnow: false,
    trout: false,
    moonfish: false
  },

  buildInventory: [
    {
      instanceId: 1,
      itemId: "berry_planter",
      hasBeenPlaced: false
    }
  ],

  nextInstanceId: 2,

  placed: {
    home: [],
    museum: []
  },

  goals: {
    firstHarvest: false,
    firstTrades: false,
    cozyHome: false,
    openMuseum: false,
    fullCollection: false,
    curatorsSeal: false
  },

  completion: false,
  museumUnlocked: false,

  settings: {
    musicVolume: 0.8,
    sfxVolume: 0.8,
    ambienceVolume: 0.5,
    reduceMotion: false,
    highContrast: false
  }
}
```

### 10.1 Placed Furniture Shape

```js
{
  instanceId: 1,
  itemId: "berry_planter",
  x: 2,
  y: 3,
  rotation: 0,
  display: null
}
```

Display case:

```js
{
  instanceId: 10,
  itemId: "small_display_case",
  x: 4,
  y: 4,
  rotation: 0,
  display: {
    slots: [null, "sweet_berry"]
  }
}
```

`display` exists only for furniture with `type === "display"`.

---

## 11. Event Bus

`EventBus` is a minimal pub/sub.

```js
class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(event, callback) {
    if (!this.listeners.has(event)) this.listeners.set(event, new Set());
    this.listeners.get(event).add(callback);
    return () => this.off(event, callback);
  }

  off(event, callback) {
    this.listeners.get(event)?.delete(callback);
  }

  emit(event, payload = {}) {
    this.listeners.get(event)?.forEach((cb) => cb(payload));
  }
}
```

The core emits events. UI and audio subscribe.

### 11.1 Required Core Events

| Event | Payload |
|---|---|
| `time:tick` | `{ time }` |
| `scene:changed` | `{ scene }` |
| `player:moved` | `{ x, y }` |
| `inventory:changed` | `{ inventory }` |
| `coins:changed` | `{ coins, delta }` |
| `resource:collected` | `{ resourceId, amount, nodeId, spotId }` |
| `specimen:unlocked` | `{ resourceId }` |
| `node:emptied` | `{ nodeId }` |
| `node:respawned` | `{ nodeId }` |
| `fish:cast` | `{ spotId }` |
| `fish:waiting` | `{ spotId }` |
| `fish:bite` | `{ spotId }` |
| `fish:catch` | `{ spotId, resourceId, amount }` |
| `fish:fail` | `{ spotId }` |
| `shop:sold` | `{ shopId, resourceId, amount, coins, supplyBefore, supplyAfter }` |
| `shop:allSold` | `{ shopId, amounts, coins, supplyBefore, supplyAfter }` |
| `shop:tierUnlocked` | `{ shopId, tier }` |
| `shop:bought` | `{ shopId, itemId, type }` |
| `museum:unlocked` | `{}` |
| `furniture:placed` | `{ buildingId, instanceId, itemId }` |
| `furniture:removed` | `{ buildingId, instanceId, itemId }` |
| `furniture:sold` | `{ instanceId, itemId, coins }` |
| `specimen:assigned` | `{ displayInstanceId, slotIndex, resourceId }` |
| `specimen:unassigned` | `{ displayInstanceId, slotIndex, resourceId }` |
| `goal:progress` | `{ goalId }` |
| `goal:completed` | `{ goalId, reward }` |
| `completion:completed` | `{}` |
| `save:completed` | `{}` |
| `invalid:action` | `{ reason }` |

---

## 12. `GameCore` API

`GameCore` is the main simulation object.

Constructor:

```js
new GameCore({
  content,
  saveAdapter,
  eventBus,
  worldRng,
  runtimeRng
})
```

Methods:

```js
async init()
newGame()
saveGame()
loadGame(data)
setPaused(paused)
update(dt)

setMoveInput(dx, dy)
interactDown()
interactUp()

openShop(shopId)
closeShop()
buyItem(shopId, itemId)
sellOne(shopId, resourceId)
sellStack(shopId, resourceId)
sellAll(shopId)

openLedger()
closeLedger()
toggleBuild()

selectBuildItem(instanceId)
selectPlacedItem(instanceId)
rotateBuildItem()
setBuildAnchor(tileX, tileY)
placeBuildItem()
removePlacedItem(instanceId)
sellBuildItem(instanceId)

assignSpecimen(buildingId, instanceId, slotIndex, resourceIdOrNull)

setSettings(partialSettings)
```

### 12.1 Update Rules

`update(dt)`:

1. Clamp `dt` to `0`..`0.1`.
2. If paused, do not advance simulation time.
3. Advance `state.time` by `dt`.
4. Update player movement.
5. Update gathering.
6. Update fishing.
7. Update node respawn.
8. Update fish cooldowns.
9. Update shop supply recovery.
10. Check goals.
11. Emit relevant events.

UI modals should pause the world:

- Title screen: paused.
- Shop modal: paused.
- Ledger modal: paused.
- Completion modal: paused.
- Build mode: not paused.
- Interior scenes: not paused.

---

## 13. Player Movement and Collision

### 13.1 Player Representation

Player position is in tile-space floats.

Example:

```text
x = 57.5
y = 70.5
```

means the center of tile `(57, 70)`.

The player uses an axis-aligned bounding box for collision.

Recommended bounding half-size:

```text
0.32 tiles
```

This is smaller than one tile and keeps movement smooth.

### 13.2 Movement

Movement input is normalized.

```text
if dx != 0 and dy != 0:
    dx /= Math.sqrt(2)
    dy /= Math.sqrt(2)
```

Speed:

```text
speed = player center tile is water ? 3 : 6
```

Position update:

```text
moveX = dx * speed * dt
moveY = dy * speed * dt
```

Move axis-separated:

1. Try X movement.
2. If collision, cancel X.
3. Try Y movement.
4. If collision, cancel Y.

### 13.3 World Collision

A tile is solid if:

- Tile is perimeter.
- Tile is building wall.
- Tile contains a berry node.
- Tile contains an ore node.

Walkable:

- Grass.
- Path.
- Water.
- Doors.
- Interior floor.
- Interior door.

Fish spots do not block movement.

Shopkeepers do not block movement.

### 13.4 Interior Collision

Interior floors are local grids.

Valid movement tiles:

- Inside floor bounds.
- Not occupied by placed furniture.

Door tile is walkable.

Furniture footprints are solid.

### 13.5 Scene Transition

Entering a building:

1. Player must be within interaction radius of the exterior door.
2. Museum is blocked if locked.
3. Set scene to building scene.
4. Place player at interior door center.

Exiting:

1. Player must be within interaction radius of interior door.
2. Set scene to world.
3. Place player at exterior exit tile center.

The door tiles are walkable, but scene changes happen through interaction, not automatic stepping. This prevents re-entry loops.

---

## 14. Interaction System

### 14.1 Interactable Types

- Berry node.
- Ore node.
- Fish spot.
- Shopkeeper.
- Door.

### 14.2 Target Selection

Every frame, compute the nearest interactable target within `1.2` tiles of player center.

Priority on ties:

1. Door.
2. Shopkeeper.
3. Berry node.
4. Ore node.
5. Fish spot.

Fish spot targeting requires the player to be on the fish spot tile.

### 14.3 Prompts

Prompt text is derived from state.

Examples:

| State | Prompt |
|---|---|
| Full berry node, inventory space | `Pick Sweet Berry` |
| Empty berry node | `Waiting` |
| Ore node with charges, inventory space | `Mine Copper Ore` |
| Fish spot, cooldown 0, inventory space | `Cast Line` |
| Fish spot, cooldown > 0 | `Wait` |
| Shopkeeper | `Talk to Moss` |
| Home door | `Enter Home` |
| Museum locked | `Museum Locked` |
| Museum unlocked | `Enter Museum` |
| Interior door | `Exit` |
| Bag full | `Bag Full` |

If inventory is full for the targeted resource, show `Bag Full`.

---

## 15. Inventory System

Inventory is an array of 10 slots.

Each slot:

```js
null
```

or:

```js
{
  resourceId: "sweet_berry",
  count: 4
}
```

### 15.1 Stack Limits

Stack limits come from content.

| Category | Stack Limit |
|---|---:|
| berry | 20 |
| ore | 10 |
| fish | 5 |

### 15.2 Add Resource

`addResource(resourceId, amount)` returns actual added amount.

Algorithm:

```text
added = 0
stackLimit = resource.stackLimit

for each slot with same resource and count < stackLimit:
    space = stackLimit - slot.count
    canAdd = min(space, amount - added)
    slot.count += canAdd
    added += canAdd
    if added == amount:
        break

if added < amount:
    space = amount - added
    while space > 0 and there is an empty slot:
        addSlotLimit = min(stackLimit, space)
        create slot with addSlotLimit
        space -= addSlotLimit
        added += addSlotLimit

return added
```

### 15.3 Remove Resource

`removeResource(resourceId, amount)` returns actual removed amount.

Algorithm:

```text
removed = 0
for each slot with resource:
    take = min(slot.count, amount - removed)
    slot.count -= take
    removed += take
    if slot.count == 0:
        slot = null
    if removed == amount:
        break
return removed
```

### 15.4 Space Check

`canHold(resourceId, amount)`:

```text
existingSpace = sum(stackLimit - slot.count for matching slots)
emptySlots = count(null)
totalSpace = existingSpace + emptySlots * stackLimit
return totalSpace >= amount
```

Gathering can start only if `canHold(resourceId, 1)` is true.

### 15.5 Yield Rules

Gathering actions have a maximum action yield of 2.

This keeps the economy bounded and matches the fishing/mining/berry algorithm structure.

- Berry: base yield is node `count`, capped at 2.
- Mining: base yield 1, bonus chance may add 1, capped at 2.
- Fishing: base yield 1, bonus chance may add 1, capped at 2.

If inventory space is less than final yield, take as many as fit, minimum 1 if the action started.

---

## 16. Resource Nodes

### 16.1 Node IDs

Use stable IDs.

Berry/ore:

```text
`${resourceId}_${x}_${y}`
```

Example:

```text
sweet_berry_30_12
```

Fish spot:

```text
`fish_${resourceId}_${x}_${y}`
```

### 16.2 Berry Node

State:

```js
{
  empty: boolean,
  count: 1 | 2,
  respawn: number
}
```

When picked:

```text
if node.empty:
    return

if inventory cannot hold 1 berry:
    return

baseYield = node.count
bonusYield = 0

if rng.next() < tool.bonusChance and baseYield < 2:
    bonusYield = 1

finalYield = min(inventory space, baseYield + bonusYield)
addResource(resourceId, finalYield)

node.empty = true
node.respawn = resource.respawnTime
emit resource:collected
```

When respawning:

```text
node.respawn -= dt
if node.respawn <= 0:
    node.empty = false
    node.count = rng.int(1, 2)
    node.respawn = 0
    emit node:respawned
```

### 16.3 Ore Node

State:

```js
{
  empty: boolean,
  charges: 0..3,
  respawn: number
}
```

When mined:

```text
if node.empty or node.charges == 0:
    return

if inventory cannot hold 1 ore:
    return

baseYield = 1
bonusYield = 0

if rng.next() < tool.bonusChance:
    bonusYield = 1

finalYield = min(inventory space, baseYield + bonusYield)
addResource(resourceId, finalYield)

node.charges -= 1

if node.charges == 0:
    node.empty = true
    node.respawn = resource.respawnTime

emit resource:collected
```

When respawning:

```text
node.respawn -= dt
if node.respawn <= 0:
    node.empty = false
    node.charges = 3
    node.respawn = 0
    emit node:respawned
```

---

## 17. Gathering System

Gathering is used for berries and mining.

State:

```js
state.activeGather = {
  type: "berry" | "ore",
  targetId: string,
  progress: 0..1
} | null
```

### 17.1 Start

On `interactDown`:

1. If `activeGather` exists, ignore.
2. Find targeted node.
3. Validate node is actionable.
4. Validate inventory can hold 1.
5. Set `activeGather.progress = 0`.

### 17.2 Update

```text
if activeGather:
    if interact not held:
        cancel
    if player moved:
        cancel
    else:
        progress += dt / tool.gatherTime
        if progress >= 1:
            completeGather()
```

Canceling produces no yield and no node state change.

### 17.3 Completion

Completion logic is in section 16.

UI reads `state.activeGather` for the progress bar.

---

## 18. Fishing System

Fishing is a state machine.

State:

```js
state.fishing = {
  spotId: string,
  state: "casting" | "waiting" | "biteMeter",
  phaseTimer: number,
  meterProgress: number
} | null
```

Fish spot state:

```js
{
  cooldown: number
}
```

### 18.1 Start

On `interactDown` at a fish spot:

1. If `state.fishing` exists, ignore unless state is `biteMeter` and this is a strike.
2. Validate player tile equals fish spot tile.
3. Validate `cooldown == 0`.
4. Validate inventory can hold 1 fish.
5. Set fishing state to `casting`.
6. `phaseTimer = 0.6`.

Fishing is committed once casting starts.

### 18.2 State Update

```text
if fishing.state == "casting":
    phaseTimer -= dt
    if phaseTimer <= 0:
        fishing.state = "waiting"
        waitTime = rng.range(tool.waitMin, tool.waitMax)
        phaseTimer = waitTime
        emit fish:waiting

if fishing.state == "waiting":
    phaseTimer -= dt
    if phaseTimer <= 0:
        fishing.state = "biteMeter"
        phaseTimer = 1.5
        emit fish:bite

if fishing.state == "biteMeter":
    phaseTimer -= dt
    fishing.meterProgress = 1 - phaseTimer / 1.5
    if phaseTimer <= 0:
        failFish()
```

If the player leaves the fish spot tile during casting, waiting, or bite meter, call `failFish()`.

### 18.3 Strike

On `interactDown` during `biteMeter`:

```text
progress = fishing.meterProgress
greenCenter = 0.5
greenHalf = tool.greenWidth / 2 / 1.5
yellowHalf = 0.2 / 2 / 1.5

if abs(progress - greenCenter) <= greenHalf:
    success = true
else if abs(progress - greenCenter) <= greenHalf + yellowHalf:
    success = rng.next() < tool.yellowSuccess
else:
    success = false
```

If success:

```text
baseYield = 1
bonusYield = rng.next() < tool.bonusChance ? 1 : 0
finalYield = min(inventory space, baseYield + bonusYield)
addResource(fishResourceId, finalYield)
emit fish:catch
```

If fail:

```text
emit fish:fail
```

Both success and failure set:

```text
fishSpot.cooldown = tool.cooldown
state.fishing = null
```

### 18.4 Why Fixed Green Center

The green zone is centered in the meter.

This is intentional because:

- The gameplay document does not require randomized zone position.
- A fixed center keeps the minigame readable and testable.
- Tool upgrades increase the green width, which is the designed skill ease improvement.
- Random zone position would add variance without improving the collector fantasy.

---

## 19. Shop System

### 19.1 Shop State

Each shop:

```js
{
  supply: 0..3,
  cumulativeSold: integer,
  lastSaleTime: number | null
}
```

### 19.2 Supply Meter

Supply is a float from `0.0` to `3.0`.

Price multiplier:

```text
supplyTier = clamp(floor(supply + 1e-9), 0, 3)
multipliers = [1.00, 0.85, 0.70, 0.60]
multiplier = multipliers[supplyTier]
```

Final unit price:

```text
price = max(1, floor(resource.basePrice * multiplier))
```

### 19.3 Selling One or Stack

`sellOne` and `sellStack`:

1. Validate shop category matches resource category.
2. Validate inventory count > 0.
3. Compute current unit price before supply update.
4. Remove `amount` from inventory.
5. Add `amount * unitPrice` coins.
6. Update shop:
   ```text
   supply = min(3, supply + amount / 5)
   cumulativeSold += amount
   lastSaleTime = state.time
   ```
7. Update sales counters.
8. Check shop tier.
9. Check goals.
10. Emit events.

### 19.4 Selling All

`sellAll(shopId)`:

1. Find all inventory resources matching the shop category.
2. Compute total amount `n`.
3. If `n == 0`, return.
4. Compute current multiplier before any supply update.
5. For each resource, compute unit price using the pre-update multiplier.
6. Remove all compatible resources.
7. Add total coins.
8. Update shop supply once:
   ```text
   supply = min(3, supply + n / 5)
   cumulativeSold += n
   lastSaleTime = state.time
   ```
9. Update sales counters.
10. Check goals.

Using one pre-update price for Sell All matches the gameplay rule that the sale price is the price before the supply update.

### 19.5 Supply Recovery

Every update:

```text
if shop.supply > 0 and shop.lastSaleTime != null:
    elapsed = state.time - shop.lastSaleTime
    if elapsed >= 120:
        steps = floor(elapsed / 120)
        shop.supply = max(0, shop.supply - steps)
        shop.lastSaleTime += steps * 120
        if shop.supply == 0:
            shop.lastSaleTime = state.time
```

This recovers one supply step every 120 seconds after the last sale.

### 19.6 Shop Tier

```text
if cumulativeSold >= 25:
    tier = 3
else if cumulativeSold >= 5:
    tier = 2
else:
    tier = 1
```

When tier increases, emit `shop:tierUnlocked`.

### 19.7 Buying Tools

`buyItem(shopId, itemId)`:

Tool buy rules:

1. Item must be a tool.
2. Item shop must match `shopId`.
3. Shop tier must be at least item `unlockTier`.
4. Player coins must be at least cost.
5. Current tool tier for that category must be lower than item tier.
6. Buying replaces the current tool.
7. Emit `shop:bought`.

### 19.8 Buying Furniture

Furniture buy rules:

1. Item must be furniture.
2. Item shop must match `shopId`.
3. Shop tier must be at least item `unlockTier`.
4. Player coins must be at least cost.
5. If item `unique` is true, player must not already own it in build inventory or placed state.
6. Deduct coins.
7. Add to build inventory with new `instanceId`.
8. Emit `shop:bought`.

### 19.9 Supply Display State

UI maps supply floor to display:

| Supply Floor | Label | Segments Filled |
|---:|---|---:|
| 0 | Normal Price | 5/5 |
| 1 | Low Price | 4/5 |
| 2 | Very Low Price | 3/5 |
| 3 | Barely Buying | 2/5 |

Do not rely on color alone.

---

## 20. Build System

Build mode is only available in `home` or `museum`.

Build state:

```js
state.build = {
  active: boolean,
  buildingId: "home" | "museum" | null,
  selectedBuildInstanceId: number | null,
  selectedPlacedInstanceId: number | null,
  rotation: 0 | 1,
  anchor: { x: number, y: number } | null,
  validity: { valid: boolean, reason: string | null }
} | null
```

### 20.1 Build Inventory

Build inventory holds purchased but unplaced furniture.

```js
{
  instanceId: number,
  itemId: string,
  hasBeenPlaced: boolean
}
```

### 20.2 Footprint

Furniture size is `[width, height]`.

Rotation:

```text
rotation 0:
    footprint = [width, height]
rotation 1:
    footprint = [height, width]
```

For square footprints, rotation does not change size.

### 20.3 Placement Validation

`canPlace(buildingId, itemId, anchorX, anchorY, rotation)` returns:

```js
{
  valid: boolean,
  reason: null | "Museum Only" | "Not Floor" | "Covers Door" | "Covers Player" | "Blocked" | "Blocks Door Path"
}
```

Validation order:

1. If item is display case and building is not museum:
   - invalid, reason `Museum Only`.
2. Compute footprint tiles.
3. If any footprint tile is outside floor:
   - invalid, reason `Not Floor`.
4. If any footprint tile is the building door:
   - invalid, reason `Covers Door`.
5. If any footprint tile is the player’s current tile:
   - invalid, reason `Covers Player`.
6. If any footprint tile is occupied by placed furniture:
   - invalid, reason `Blocked`.
7. Simulate new footprint as occupied.
8. Run path check from player tile to door tile.
9. If no path:
   - invalid, reason `Blocks Door Path`.
10. Otherwise valid.

### 20.4 Path Check

Use BFS on interior floor tiles.

Valid path tiles:

- Floor tiles.
- Door tile.

Invalid path tiles:

- Outside floor.
- Occupied placed furniture tiles.
- Proposed new furniture tiles.

The player’s current tile is the start and is allowed even though the player occupies it.

The door tile is the goal and must not be occupied.

### 20.5 Placement Action

`placeBuildItem()`:

1. Build mode must be active.
2. A build inventory item must be selected.
3. Anchor must be valid.
4. `canPlace` must be valid.
5. Remove item from build inventory.
6. Add placed instance:
   ```js
   {
     instanceId,
     itemId,
     x: anchorX,
     y: anchorY,
     rotation,
     display: item.type === "display" ? { slots: Array(item.slots).fill(null) } : null
   }
   ```
7. Emit `furniture:placed`.
8. Update scores and goals.

### 20.6 Removing Placed Furniture

`removePlacedItem(instanceId)`:

1. Validate item is placed in current building.
2. Remove from placed list.
3. Add to build inventory:
   ```js
   {
     instanceId,
     itemId,
     hasBeenPlaced: true
   }
   ```
4. If display case:
   - Unassign all specimens.
   - Emit `specimen:unassigned` for each removed assignment.
5. Emit `furniture:removed`.
6. Update scores and goals.

### 20.7 Reselling Unplaced Furniture

`sellBuildItem(instanceId)`:

1. Validate item is in build inventory.
2. Refund:
   ```text
   if hasBeenPlaced == false:
       refund = cost
   else:
       refund = max(1, floor(cost / 2))
   ```
3. Add coins.
4. Remove from build inventory.
5. Emit `furniture:sold`.

Display cases sold while unplaced have no assigned specimens, so no unassignment is needed.

If a display case was previously placed, removed, and then sold, refund is 50%.

---

## 21. Museum and Specimen System

### 21.1 Specimen Unlock

When a resource is first collected:

```text
if !state.collection[resourceId]:
    state.collection[resourceId] = true
    emit specimen:unlocked
```

Selling is not required.

### 21.2 Display Cases

Display cases are furniture with:

```js
type: "display"
museumOnly: true
unique: true
slots: 1..3
```

Only placed display cases can hold specimens.

### 21.3 Assignment Rules

`assignSpecimen(buildingId, instanceId, slotIndex, resourceId)`:

1. Building must be museum.
2. Display case must be placed in museum.
3. Slot index must be valid.
4. If assigning:
   - Specimen must be unlocked.
   - Specimen must not already be assigned to another placed display case.
5. If unassigning:
   - Slot must currently hold that specimen.
6. Update slot.
7. Emit `specimen:assigned` or `specimen:unassigned`.
8. Update museum score and goals.

### 21.4 Removing Display Cases

Removing a placed display case unassigns all its specimens.

Selling an unplaced display case does not unassign anything because it cannot have assigned specimens while unplaced.

### 21.5 Assigned Specimen Count

Assigned count is the number of non-null slots across all placed museum display cases.

Because assignment enforces uniqueness, this equals the number of unique assigned specimens.

---

## 22. Score System

### 22.1 Furniture Value

```text
value = ceil(furniture.cost / 10)
```

### 22.2 Home Score

```text
Home Score = sum(value of placed home furniture)
```

### 22.3 Museum Score

```text
Museum Score =
    sum(exhibitScore of assigned specimens)
  + sum(value of placed museum furniture)
```

Scores are non-binding.

---

## 23. Goal System

### 23.1 Goal Evaluation

`GoalSystem.check()` runs after relevant events and updates.

For each incomplete goal:

1. Evaluate all requirements.
2. If all requirements are met:
   - Mark goal complete.
   - Grant reward.
   - Apply unlock.
   - Emit `goal:completed`.

Once a goal is complete, it stays complete.

### 23.2 Requirement Evaluators

```text
resource_collected:
    state.collection[resource] is true and amount == 1? For amount > 1, track collected counts if needed.
```

Because collection is binary, requirement amounts for collected resources are effectively 1. For full collection, use `all_resource_collected`.

```text
resource_sold:
    state.sales.byResource[resource] >= amount
```

```text
category_sold:
    state.sales.byCategory[category] >= amount
```

```text
building_furniture_count:
    state.placed[building].length >= amount
```

```text
museum_display_count:
    state.placed.museum.filter(furniture.type == "display").length >= amount
```

```text
specimen_assigned:
    assignedSpecimenCount() >= amount
```

```text
all_resource_collected:
    every resource collection[resourceId] is true
```

### 23.3 Goal Rewards

- `firstHarvest`: +10 coins.
- `firstTrades`: +25 coins, set `museumUnlocked = true`, emit `museum:unlocked`.
- `cozyHome`: +50 coins.
- `openMuseum`: +50 coins.
- `fullCollection`: +100 coins.
- `curatorsSeal`: set `completion = true`, emit `completion:completed`.

### 23.4 Active Goal

Active goal is the first incomplete goal by `order`.

UI shows active goal progress.

### 23.5 Final Completion

When `curatorsSeal` completes:

- Set `state.completion = true`.
- Emit `completion:completed`.
- UI shows completion screen.
- Game remains fully playable after closing the screen.
- Completion is latched in save.

---

## 24. Save and Load

### 24.1 Save Adapter Interface

```js
class SaveAdapter {
  async load() {}
  async save(data) {}
  async clear() {}
}
```

Browser:

- `LocalStorageSaveAdapter`
- Key: `collector_game_save_v1`

Tests:

- `InMemorySaveAdapter`

### 24.2 Save Data

Save the serializable `state` object.

Do not save:

- Active gathering.
- Active fishing.
- UI modal state.
- Build ghost anchor.
- Temporary target.
- DOM state.

Temporary action state is reset on load.

### 24.3 Save Triggers

Save:

- After important mutations:
  - Resource collected.
  - Resource sold.
  - Tool purchased.
  - Furniture purchased.
  - Furniture placed.
  - Furniture removed.
  - Furniture sold.
  - Specimen assigned.
  - Specimen unassigned.
  - Goal completed.
  - Museum unlocked.
  - Completion.
  - Settings changed.
- Periodically every 30 seconds of unpause simulation time.
- On browser `beforeunload` and `visibilitychange` hidden.

Use a small debounce to avoid excessive writes.

### 24.4 Load Rules

On load:

1. Validate save version.
2. Validate world version.
3. Validate content version.
4. If invalid, start a new game and clear corrupted save.
5. Regenerate world from `state.seed`.
6. Apply saved node/fish/shop state.
7. Validate player position is walkable.
8. If invalid position, place player at start tile.
9. Recompute derived flags:
   - `museumUnlocked` if goal complete.
   - Active goal.
   - Scores.
10. Emit save/load event if needed.

### 24.5 Corrupted Save

If save is corrupted:

- Do not crash.
- Start new game.
- Optionally show toast `Save not compatible. New game started.`

---

## 25. UI Implementation

UI is DOM-based and should be skinned with CSS according to visual design.

The core does not know DOM details. UI calls core actions.

### 25.1 UI Root

`UIRoot` owns:

- Title screen.
- Shop modal.
- Ledger modal.
- Completion modal.
- Toast stack.
- Settings modal.
- Accessibility classes.

Accessibility root classes:

```html
<html data-reduce-motion="false" data-high-contrast="false">
```

When settings change:

- `data-reduce-motion="true"` disables CSS animations and canvas non-essential motion.
- `data-high-contrast="true"` enables stronger borders and contrast.

### 25.2 Title UI

Shows:

- Title.
- `Start`
- `Continue` if save exists.
- Controls:
  - `WASD` / arrows move
  - `E` interact
  - `C` ledger
  - `B` build inside buildings
  - `R` rotate in build mode
  - `Esc` cancel/close

`Continue` loads save.

`Start` clears save and starts new game.

### 25.3 Persistent HUD

Persistent HUD elements:

- Top-left: location label, ledger button.
- Top-right: coins, minimap.
- Bottom-left: tool tier pips.
- Bottom-center: inventory.
- Bottom-right: contextual hints.
- Center-lower: interaction prompt.
- Above prompt: gathering progress bar.
- Center: fishing meter when active.
- Top-center: toasts.

HUD updates from core events and state.

### 25.4 Tool Tier Display

Use pips.

| Tier | Pips |
|---:|---:|
| 1 | 1 filled |
| 2 | 2 filled |
| 3 | 3 filled |

Do not use color alone.

### 25.5 Inventory

10 slots.

Each slot shows:

- Resource icon.
- Stack count.

Hover tooltip shows:

- Resource name.
- Stack count.
- Base sell price.
- Current shop price if player is near matching shopkeeper.

If inventory is full and an action is attempted:

- Show `Bag Full`.
- Play `inventory_full` SFX.

### 25.6 Shop UI

Shop modal size approximately `640 x 420`.

Tabs:

- Buy.
- Sell.

Sell tab rows:

- Resource icon.
- Resource name.
- Stack count.
- Current unit price.
- Stack total.
- `Sell` button.
- `Sell Stack` button or shift-click.

`Sell All` button sells all compatible resources.

Buy tab cards:

- Item icon.
- Name.
- Cost.
- Description.
- Buy button.

Locked item states:

- Shop tier not reached:
  - Grayed out.
  - Lock icon.
  - Requirement text.
- Unique already owned:
  - `Unique: already owned`
- Museum only:
  - Not a purchase lock, but display badge.
- Cannot afford:
  - Buy button disabled.

Supply meter shows:

- Segments.
- Text label.

### 25.7 Ledger UI

Tabs:

- Goals.
- Collection.
- Scores.

Goals tab:

- Active goal.
- Progress.
- Reward.
- Completed goals.

Collection tab:

- 3x3 grid.
- Each specimen:
  - Icon or silhouette.
  - Name.
  - Location hint.
  - Exhibit score.
  - `Displayed` badge if assigned.

Scores tab:

- Home Score.
- Museum Score.
- Home furniture count.
- Museum furniture count.
- Museum exhibit count.

### 25.8 Build UI

Build UI is active inside Home/Museum.

When active:

- Floor grid highlight.
- Build inventory panel.
- Selected item card.
- Building score.
- Placement ghost.
- Invalid reason if invalid.

Controls:

- Mouse move: anchor tile.
- `R`: rotate selected unplaced item.
- `E` or left click: place selected item.
- `X` or right click: remove targeted placed item.
- `Esc`: cancel selection or exit build mode.
- Select build inventory item: prepare placement.
- Select placed display case: open exhibit panel.

Selected item card shows:

- Item icon.
- Name.
- Footprint.
- Rotation.
- Validity.
- Invalid reason.

Resell panel for selected unplaced furniture shows:

- Item icon.
- Name.
- Refund amount.
- Sell button.

Exhibit panel shows:

- Display case name.
- Slots.
- Assigned specimen or empty slot.
- Remove assignment button.
- Unassigned unlocked specimens.
- Assign button.

### 25.9 Toasts

Toasts appear top-center.

Maximum 3 visible.

Older toasts fade first.

Duration: 3 seconds.

Toast types:

| Type | Example |
|---|---|
| Goal Complete | `Goal Complete: First Trades` |
| Shop Unlock | `Moss’s Stock Updated` |
| Museum Unlock | `Museum Unlocked` |
| New Specimen | `New Specimen: Moon Berry` |
| Tool Purchase | `Bought Honey Pouch` |
| Furniture Purchase | `Bought Berry Planter` |
| Save | `Saved` |
| Error | `Not enough coins` |

### 25.10 Settings UI

Settings:

- Music volume.
- SFX volume.
- Ambience volume.
- Reduce Motion toggle.
- High Contrast toggle.

Settings are saved with the game state.

### 25.11 Completion UI

Shows:

- `Curator’s Seal Complete`
- Subtext: `Your museum is open.`
- `Continue` button.

After closing, game remains active.

---

## 26. Rendering Implementation

### 26.1 Canvas

Canvas size:

```text
960 x 540
```

Use nearest-neighbor scaling.

CSS should scale the canvas to fit the window while preserving aspect ratio.

### 26.2 Camera

Camera follows player.

Camera clamps to world or interior bounds.

For world:

```text
cameraX = clamp(player.x * TILE_SIZE - VIEW_WIDTH / 2, 0, WORLD_SIZE * TILE_SIZE - VIEW_WIDTH)
cameraY = clamp(player.y * TILE_SIZE - VIEW_HEIGHT / 2, 0, WORLD_SIZE * TILE_SIZE - VIEW_HEIGHT)
```

For interiors, clamp to interior floor bounds.

### 26.3 Visible Culling

Render only visible tiles:

```text
startX = floor(cameraX / TILE_SIZE)
startY = floor(cameraY / TILE_SIZE)
endX = startX + ceil(VIEW_WIDTH / TILE_SIZE) + 1
endY = startY + ceil(VIEW_HEIGHT / TILE_SIZE) + 1
```

### 26.4 Y-Sort

Use y-sort for drawables.

Drawable:

```js
{
  y: number,
  z: number,
  draw: function
}
```

Sort:

```text
primary: y
secondary: z
```

Z values:

| Drawable | Z |
|---|---:|
| Furniture base | 0.5 |
| Player | 1.0 |
| Shopkeeper | 1.0 |
| Berry node | 1.0 |
| Ore node | 1.0 |
| Fish bobber | 1.2 |
| Interaction highlight | 1.5 |

Terrain is drawn before y-sorted entities.

### 26.5 Sprites

`SpriteRenderer` uses asset manifest IDs.

Animation frame selection:

```text
frame = floor(time * fps) % files.length
```

Respect reduce motion:

- Disable water ripple animation frames if multiple frames exist.
- Disable tier 3 pulse animation.
- Keep essential state visible.

### 26.6 Minimap

Minimap is a small canvas or DOM/CSS grid, approximately `96 x 96`.

Shows:

- Biome regions.
- Player dot.
- Home dot.
- Museum dot.
- Trading post dot.

Does not show resource nodes.

In interiors, show the world minimap with player dot at the corresponding building dot.

### 26.7 Build Ghost

Build ghost is drawn on canvas over interior floor.

Valid footprint:

- Green overlay.

Invalid footprint:

- Red overlay.

Use steady colors, no flashing.

Reason text is rendered in DOM near player or in selected item card.

---

## 27. Audio Implementation

### 27.1 AudioManager

`AudioManager` uses the asset manifest.

Responsibilities:

- Load audio assets.
- Play SFX.
- Play zone music.
- Crossfade music.
- Play activity layers.
- Play ambience.
- Play stingers.
- Apply volume settings.
- Handle browser autoplay restrictions.

Audio should start on first user interaction.

### 27.2 Music Layers

Zone music:

- Title screen: `music/title_loop.ogg`.
- World zone: based on location label.
- Interior: `home` or `museum`.

Activity layers:

- Shop open: add `shop` layer.
- Build mode: add `build` layer.

Crossfades:

- Zone to zone: 1 second.
- Interior to world: 1 second.
- Shop layer: 0.5 second.
- Build layer: 0.5 second.

Stingers:

- Goal complete.
- Shop unlock.
- Museum unlock.
- Final completion.

Stingers play over current music.

### 27.3 SFX Event Mapping

Core events map to SFX:

| Core Event / Action | SFX |
|---|---|
| Footstep on grass/ground | `footstepGrass` |
| Footstep on stone/ore floor | `footstepStone` |
| Footstep on water | `waterStep` |
| Berry gather complete | `berryPick` |
| Ore mine complete | `oreMine` |
| Fish cast | `fishCast` |
| Fish bite | `fishBite` |
| Fish catch | `fishCatch` |
| Fish fail | `fishFail` |
| Resource sold | `coinSale` |
| Item bought | `coinBuy` |
| Furniture placed | `furniturePlace` |
| Furniture removed | `furnitureRemove` |
| Furniture sold | `furnitureSell` |
| UI hover | `uiHover` |
| UI click | `uiClick` |
| UI open | `uiOpen` |
| UI close | `uiClose` |
| Invalid action | `invalid` |
| Inventory full | `inventoryFull` |
| Specimen assigned | `specimenAssign` |
| Specimen unassigned | `specimenUnassign` |
| Goal complete | `goalComplete` |
| Shop unlock | `shopUnlock` |
| Museum unlock | `museumUnlock` |
| Final completion | `finalCompletion` |

SFX pitch variation:

- Use playback rate variation between `0.98` and `1.02` for short SFX.
- Do not vary important stingers.

### 27.4 Volume Defaults

Use visual document relative levels as defaults:

- Music: 0.7
- SFX: 0.8
- Ambience: 0.5

Settings allow user adjustment from 0 to 1.

---

## 28. Input Implementation

### 28.1 Keys

| Key | Action |
|---|---|
| `W` / Arrow Up | Move up |
| `S` / Arrow Down | Move down |
| `A` / Arrow Left | Move left |
| `D` / Arrow Right | Move right |
| `E` | Interact / place in build mode |
| `B` | Toggle build mode inside buildings |
| `C` | Toggle ledger |
| `Esc` | Close modal / cancel build selection |
| `R` | Rotate selected build item |
| `X` | Remove targeted placed furniture in build mode |

Mouse:

- Left click:
  - World: interact.
  - Build mode: place selected item.
- Right click:
  - Build mode: remove targeted placed item.

### 28.2 Input Context

Input behavior depends on context.

Title screen:

- Click Start/Continue.
- Keyboard shortcuts disabled except settings if open.

World:

- Movement.
- Interact.
- Ledger.

Shop modal:

- Mouse navigation.
- `Esc` closes.

Build mode:

- Movement allowed.
- Mouse anchor.
- `R`, `E`, `X`, `Esc`.

Fishing active:

- Only interact during bite meter is allowed.
- Other UI toggles are ignored until fishing resolves.

This prevents accidental modal opening during the committed fishing sequence.

---

## 29. Test Harness

The test harness has three layers:

1. Unit tests for pure logic.
2. Integration tests for `GameCore`.
3. E2E tests for the browser game.

All required logic tests run in Node.js with no external runtime dependencies.

### 29.1 Node Test Command

```bash
npm test
```

This should run:

```text
tests/unit
tests/integration
```

### 29.2 Headless Game Harness

`tests/harness/headless.js` exports helpers to create a headless `GameCore`.

Example:

```js
import { createHeadlessGame } from "../harness/headless.js";

const game = createHeadlessGame({
  seed: 42,
  runtimeRng: new MockRNG([0.5, 0.5, 0.5]),
  saveAdapter: new InMemorySaveAdapter()
});

await game.init();
```

Helpers:

```js
advance(game, seconds, step = 0.016)
getEvents(game)
interactFor(game, seconds)
releaseInteract(game)
teleport(game, x, y)
walkTo(game, x, y)
findPlaceableTile(game, buildingId, itemId, rotation)
```

`teleport` is test-only and should not be part of production `GameCore`. It exists to reduce test time and isolate systems.

`walkTo` uses BFS and actual movement updates. Use it for movement and E2E-style integration tests.

### 29.3 MockRNG

`tests/harness/mockRNG.js` provides deterministic RNG for tests.

```js
class MockRNG {
  constructor(values = []) {
    this.values = values;
  }

  next() {
    if (this.values.length === 0) return 0.5;
    return this.values.shift();
  }

  range(min, max) {
    return min + this.next() * (max - min);
  }

  int(min, max) {
    return Math.floor(this.range(min, max + 1));
  }
}
```

For tests requiring success or failure, queue exact values.

Example fishing green strike:

```js
new MockRNG([
  0.5, // wait time
  0.99 // yellow success not used if green
])
```

### 29.4 Browser Mock

Do not require a full DOM mock for required tests.

UI is validated primarily by:

- Core event tests.
- E2E browser tests.

If an integrating engineer wants additional UI unit tests, they may add an optional DOM stub, but it is not required.

### 29.5 E2E Harness

E2E uses Playwright.

Required files:

```text
tests/e2e/playwright.config.js
tests/e2e/smoke.spec.js
tests/e2e/assets.spec.js
```

Local server:

```bash
npm run serve
npm run test:e2e
```

The game should expose a debug hook only when running tests:

```text
http://localhost:8000/?test=1
```

When `?test=1` is present, `src/main.js` attaches:

```js
window.__game = game;
window.__content = content;
window.__manifest = manifest;
```

Do not attach in normal production URLs.

---

## 30. Required Tests

The following tests are required for completion.

### 30.1 Content Tests

File: `tests/unit/content.test.js`

Assert:

- All 9 resources exist.
- Resource categories are only `berry`, `ore`, `fish`.
- Stack limits match gameplay values.
- Node quotas match gameplay values.
- Respawn times match gameplay values.
- All tools exist with correct shop, category, tier, and cost.
- All furniture exists with correct shop, unlock tier, size, cost, type, museumOnly, unique, and slots.
- Display cases total 9 slots.
- Goals exist in correct order.
- Goal requirements reference valid resources, categories, and buildings.
- Audio manifest references exist in content or manifest.
- Shopkeepers exist at expected positions.

### 30.2 RNG Tests

File: `tests/unit/rng.test.js`

Assert:

- Same seed produces same sequence.
- `range` stays within bounds.
- `int` returns integers within inclusive bounds.
- Values are stable across repeated calls.

### 30.3 Pathfinding Tests

File: `tests/unit/pathfinding.test.js`

Assert:

- BFS finds path in open grid.
- BFS returns null when blocked.
- BFS avoids blocked tiles.
- Path includes start and goal.
- Path uses 4-direction movement.
- Placement path check fails when door is enclosed.
- Placement path check succeeds when path exists.

### 30.4 Inventory Tests

File: `tests/unit/inventory.test.js`

Assert:

- Adding to empty slot creates slot.
- Adding to existing stack respects stack limit.
- Adding overflow uses new slot.
- Full inventory returns 0 added.
- `canHold` returns false when no space.
- Removing partial stack works.
- Removing full stack clears slot.
- Berry stack max 20.
- Ore stack max 10.
- Fish stack max 5.
- Bonus yield is limited by available space.

### 30.5 Economy Tests

File: `tests/unit/economy.test.js`

Assert:

- Supply 0 gives multiplier 1.00.
- Supply 0.999 gives multiplier 1.00.
- Supply 1 gives multiplier 0.85.
- Supply 1.999 gives multiplier 0.85.
- Supply 2 gives multiplier 0.70.
- Supply 2.999 gives multiplier 0.70.
- Supply 3 gives multiplier 0.60.
- Final price is `max(1, floor(basePrice * multiplier))`.
- Selling 1 unit increases supply by 0.2.
- Selling 5 units increases supply by 1.0.
- Sale price uses supply before update.
- Sell All uses one pre-update multiplier for all compatible resources.
- Supply recovers by 1 after 120 seconds.
- Supply recovers by multiple steps after long idle time.
- Supply never below 0 or above 3.
- Shop tier is 1 at 0 sales.
- Shop tier is 2 at 5 sales.
- Shop tier is 3 at 25 sales.
- Tool purchase only allowed for higher tier.
- Tool purchase replaces current tool.
- Furniture purchase adds build inventory.
- Unique display case cannot be purchased twice while owned.
- Unique display case can be repurchased after sold.

### 30.6 Build Tests

File: `tests/unit/build.test.js`

Assert:

- Valid placement on empty floor succeeds.
- Placement outside floor fails with `Not Floor`.
- Placement on door fails with `Covers Door`.
- Placement on player tile fails with `Covers Player`.
- Placement overlapping furniture fails with `Blocked`.
- Display case in Home fails with `Museum Only`.
- Placement blocking door path fails with `Blocks Door Path`.
- Rotation swaps footprint.
- 1x1 rotation does not change footprint.
- Removing placed furniture returns it to build inventory.
- Removed furniture has `hasBeenPlaced = true`.
- Never placed furniture refunds 100%.
- Previously placed furniture refunds 50%, minimum 1.
- Display case removal unassigns specimens.
- Display case assignment requires unlocked specimen.
- Specimen cannot be assigned to two slots.

### 30.7 Goal Tests

File: `tests/unit/goals.test.js`

Assert:

- `firstHarvest` completes when one sweet berry, one copper ore, and one minnow are collected.
- `firstHarvest` reward is 10 coins.
- `firstTrades` completes only when 5 sweet berries, 5 copper ores, and 5 minnows are sold.
- `firstTrades` rewards 25 coins and unlocks museum.
- `cozyHome` completes at 5 home furniture.
- `openMuseum` completes at 3 display cases and 3 assigned specimens.
- `fullCollection` completes when all 9 resources collected.
- `curatorsSeal` completes when all final requirements are true.
- Completed goals do not uncomplete after furniture removal or specimen unassignment.
- Active goal is first incomplete goal.
- Completion event fires only once.

### 30.8 World Generator Tests

File: `tests/unit/worldGenerator.test.js`

Assert:

- Generating with seed 42 twice produces identical node and fish spot lists.
- Tile map version matches `WORLD_VERSION`.
- Perimeter tiles are solid.
- Node counts are exact:
  - Sweet Berry: 30
  - Moon Berry: 15
  - Ember Berry: 5
  - Copper Ore: 25
  - Silver Ore: 12
  - Crystal Shard: 4
  - Minnow: 15
  - Trout: 8
  - Moonfish: 3
- Berry nodes are inside Berry Grove mask.
- Ore nodes are inside Ore Ridge mask.
- Fish spots are on water tiles.
- No land node is on path.
- No land node is on perimeter.
- No land node is within 2 tiles of a door.
- No two nodes occupy the same tile.
- Node minimum distance is at least 3 for seed 42.
- Ember berries are in northern Berry Grove submask.
- Silver ore is in eastern Ore Ridge submask.
- Crystal shards are in eastern tip submask.
- Minnow spots are shore water.
- Trout spots are middle water.
- Moonfish spots are deep south water.
- Start tile is walkable.
- Pathfinding from start reaches an adjacent tile for every node.
- Home exterior door is reachable.
- Museum exterior door is reachable.
- Trading post shopkeepers are reachable.

### 30.9 Movement Integration Tests

File: `tests/integration/movement.test.js`

Assert:

- Player moves 6 tiles in 1 second on grass.
- Diagonal movement distance is not faster than straight-line movement.
- Player moves 3 tiles in 1 second on water.
- Player cannot move into perimeter.
- Player cannot move into berry node.
- Player cannot move into ore node.
- Player can move through water.
- Player can enter Home from exterior door.
- Player can exit Home to exterior exit tile.
- Museum door is blocked while locked.
- Museum door becomes enterable after unlock.

### 30.10 Gathering Integration Tests

File: `tests/integration/gathering.test.js`

Assert:

- Berry pick completes after tool gather time.
- Berry pick yields node count.
- Berry bonus yield only adds 1 if base yield was 1 and chance succeeds.
- Berry pick empties node.
- Berry node respawns after respawn time.
- Canceling berry pick produces no yield.
- Moving while picking cancels pick.
- Mining consumes 1 charge per completed action.
- Mining completes after tool mine time.
- Mining bonus yield adds at most 1.
- Mining 3 charges empties node.
- Mining empty node does nothing.
- Ore node respawns with 3 charges.
- Gathering blocked when inventory full.
- New specimen unlock occurs on first collection.

### 30.11 Fishing Integration Tests

File: `tests/integration/fishing.test.js`

Assert:

- Fishing starts only on fish spot tile.
- Fishing starts only if inventory can hold 1 fish.
- Casting lasts 0.6 seconds.
- Wait time is within tool wait range.
- Bite meter appears after wait.
- Strike in green zone succeeds.
- Strike in yellow zone uses yellow success chance.
- Strike outside zones fails.
- Missing meter entirely fails.
- Success gives 1 fish.
- Bonus fish adds 1 only if chance succeeds and space exists.
- Success starts cooldown.
- Failure starts cooldown.
- Cannot start new fishing while cooldown active.
- Leaving fish spot during fishing fails and starts cooldown.
- Fishing state resets to null after resolution.

### 30.12 Shop Integration Tests

File: `tests/integration/shop.test.js`

Assert:

- Opening shop shows only matching category sell rows.
- Selling one resource updates coins, inventory, supply, and sales.
- Selling full stack works.
- Sell All sells only matching category.
- Sell All uses pre-update supply price.
- Selling increases cumulative sold.
- Shop tier unlocks at 5 and 25 cumulative category sales.
- Buying tool updates tool tier.
- Buying furniture adds build inventory.
- Buying locked item fails.
- Buying unaffordable item fails.
- Buying unique display case twice fails while owned.
- Selling resources updates goal progress.

### 30.13 Build Furniture Integration Tests

File: `tests/integration/buildFurniture.test.js`

Assert:

- Build mode only activates inside Home or Museum.
- Selecting build inventory item shows ghost.
- Placing valid furniture removes it from build inventory.
- Placed furniture becomes solid.
- Removing placed furniture returns it to build inventory.
- Placed furniture updates building score.
- Removing furniture updates building score.
- Selling unplaced furniture gives refund.
- Selling never placed furniture gives 100%.
- Selling previously placed furniture gives 50%.
- Invalid placement does not mutate state.
- Invalid placement emits `invalid:action`.

### 30.14 Museum Integration Tests

File: `tests/integration/museum.test.js`

Assert:

- Display cases can only be placed in Museum.
- Placed display case has correct number of slots.
- Specimen can only be assigned while display case is placed.
- Assigning unlocked specimen updates museum score.
- Unassigning specimen updates museum score.
- Assigned specimen cannot be assigned elsewhere.
- Removing display case unassigns all specimens.
- Selling unplaced display case does not affect assignments.
- Museum score includes exhibit scores and furniture value.
- Museum unlock occurs after First Trades.

### 30.15 Save/Load Tests

File: `tests/integration/save.test.js`

Assert:

- New game state matches starting state.
- Save/load round-trips player position.
- Save/load round-trips coins.
- Save/load round-trips inventory.
- Save/load round-trips tool tiers.
- Save/load round-trips node empty/full state.
- Save/load round-trips node respawn timers.
- Save/load round-trips ore charges.
- Save/load round-trips fish cooldowns.
- Save/load round-trips shop supply.
- Save/load round-trips shop cumulative sold.
- Save/load round-trips sales counters.
- Save/load round-trips collection log.
- Save/load round-trips build inventory.
- Save/load round-trips placed furniture.
- Save/load round-trips display assignments.
- Save/load round-trips goal completion.
- Save/load round-trips completion.
- Save/load round-trips settings.
- Corrupted save starts new game without throwing.
- World version mismatch starts new game.

### 30.16 Playthrough Test

File: `tests/integration/playthrough.test.js`

This test proves the full game is completable through core actions.

Use real core actions. Use test-only teleport for speed where necessary.

Required sequence:

1. Create new headless game.
2. Assert starting state:
   - 25 coins.
   - Tier 1 tools.
   - Museum locked.
   - Empty inventory.
   - Empty build inventory.
   - All goals incomplete.
3. Collect 1 Sweet Berry.
4. Collect 1 Copper Ore.
5. Catch 1 Minnow.
6. Assert `firstHarvest` complete.
7. Assert coins increased by 10.
8. Sell 5 Sweet Berries to Moss.
9. Sell 5 Copper Ores to Grit.
10. Sell 5 Minnows to Reed.
11. Assert `firstTrades` complete.
12. Assert museum unlocked.
13. Assert all shop tiers at least 2.
14. Collect all 9 resource types.
15. Assert `fullCollection` complete.
16. Sell enough resources to reach 25 category sales in each category.
17. Assert all shop tiers are 3.
18. Buy all 4 display cases.
19. Buy enough non-display furniture to place at least 12 museum furniture pieces total.
20. Enter Museum.
21. Place 4 display cases in valid museum tiles.
22. Place remaining museum furniture in valid museum tiles.
23. Assign all 9 unlocked specimens to display case slots.
24. Assert `curatorsSeal` complete.
25. Assert `state.completion` is true.
26. Assert completion event fired.
27. Save game.
28. Load game into new core.
29. Assert completion and all final state remain true.

This test is the primary “game is finished and playable” validation.

### 30.17 E2E Smoke Tests

File: `tests/e2e/smoke.spec.js`

Required assertions:

- Page loads without console errors.
- Title screen is visible.
- Canvas exists and has non-zero size.
- HUD does not appear before game starts.
- Clicking `Start` begins a new game.
- HUD appears after start.
- Player sprite or world pixels render.
- Pressing `C` opens Ledger.
- Pressing `Esc` closes Ledger.
- Pressing `E` near a shopkeeper opens shop if within range.
- No missing asset errors when `?test=1`.

### 30.18 E2E Asset Tests

File: `tests/e2e/assets.spec.js`

Required assertions:

- All sprite manifest entries load.
- All music files load or are decodable.
- All SFX files load or are decodable.
- No manifest ID is missing.
- No 404 requests occur.

If audio decoding is restricted in headless browser, at minimum assert network requests succeed for all manifest asset URLs.

---

## 31. Acceptance Criteria

The engineering implementation is complete when all of the following are true:

### Core

- `GameCore` runs in Node.js without DOM.
- All required unit and integration tests pass.
- The playthrough test completes Curator’s Seal.
- No required gameplay rule is hard-coded outside content where content can represent it.
- World generation is deterministic from seed 42.
- All node quotas are exact.
- No invalid placement can block the door path.
- No softlock exists from furniture placement.
- Supply meters cannot cause permanent price ruin.
- Inventory full does not block movement.
- Museum locked state does not block world play.
- Completion remains latched after save/load.

### Browser

- Game loads in modern browser.
- Canvas renders world and interiors.
- HUD updates correctly.
- Shop, ledger, build, settings, title, and completion UI work.
- Audio plays after user interaction.
- Settings persist.
- Accessibility toggles apply.
- Save/load works in browser.
- No runtime dependency is required.
- No console errors occur during normal play.
- E2E smoke and asset tests pass.

---

## 32. Final Engineering Principle

The implementation should feel like a small, reliable diorama:

- The simulation is deterministic and testable.
- The UI is responsive but not part of core rules.
- The renderer is a presentation layer.
- The audio system is an event listener, not a gameplay owner.
- The world generator creates the places the gameplay designer specified.
- The test harness proves the game can actually be played from start to completion.

If a feature does not directly support:

- Collecting,
- Selling,
- Building,
- Museum curation,
- Saving,
- Testing,
- Accessibility,
- Or readable visual/audio feedback,

cut it.