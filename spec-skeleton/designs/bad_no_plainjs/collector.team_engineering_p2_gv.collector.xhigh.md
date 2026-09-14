# engineering.md

## 1. Purpose

This document defines the engineering design for the open-world collector game.

The integrating agent should treat this as the source of truth for:

- Repository layout.
- Runtime architecture.
- Data model.
- World generation.
- Simulation systems.
- Save/load.
- Rendering implementation.
- UI wiring.
- Audio wiring.
- Test harness.
- Required tests.

Gameplay numbers come from `gameplay.md`. Visual/audio asset names and presentation rules come from `visual.md`. If this document conflicts with those documents, this document wins for implementation behavior because it resolves implementation-level ambiguity.

The game is a single-player browser game with:

- 2D top-down tile world.
- Fixed timestep simulation.
- Canvas world rendering.
- DOM-based UI panels.
- Deterministic world generation.
- Headless test harness.
- Local save state.

---

## 2. Technical Approach

### 2.1 Stack

Use:

- TypeScript.
- Vite for browser bundling and dev server.
- Vitest for tests.
- HTML5 Canvas 2D for world rendering.
- DOM/CSS for HUD, shop, ledger, build panel, toasts, and title screen.
- Web Audio API for audio.

Do not use:

- A game engine.
- ECS.
- A physics library.
- Runtime 3D rendering.
- External UI framework.
- Network or multiplayer code.
- Cloud save.

Why:

The game is small enough that a directly organized TypeScript codebase is easier to integrate, test, and debug than an engine or framework. Canvas plus DOM gives the best balance of world rendering and accessible UI.

---

## 3. Required Files

The repository should contain the following files. The integrating agent may add private helper files, but these required files must exist.

```text
/index.html
/vite.config.ts
/tsconfig.json
/package.json
/src/styles.css
/src/main.ts

/src/config.ts
/src/types.ts
/src/rng.ts
/src/clock.ts
/src/events.ts
/src/id.ts

/src/content/resources.ts
/src/content/tools.ts
/src/content/furniture.ts
/src/content/shops.ts
/src/content/goals.ts
/src/content/world.ts
/src/content/audio.ts

/src/state/gameState.ts
/src/state/save.ts

/src/world/tileMap.ts
/src/world/zone.ts
/src/world/worldGenerator.ts
/src/world/collision.ts
/src/world/pathfinding.ts

/src/entities/player.ts
/src/entities/shopkeeper.ts
/src/entities/resourceNode.ts

/src/systems/input.ts
/src/systems/movement.ts
/src/systems/interaction.ts
/src/systems/gather.ts
/src/systems/fishing.ts
/src/systems/inventory.ts
/src/systems/economy.ts
/src/systems/furniture.ts
/src/systems/museum.ts
/src/systems/goals.ts
/src/systems/audio.ts
/src/systems/effects.ts

/src/render/assetManifest.ts
/src/render/camera.ts
/src/render/renderer.ts
/src/render/particles.ts

/src/ui/ui.ts
/src/ui/title.ts
/src/ui/hud.ts
/src/ui/shop.ts
/src/ui/ledger.ts
/src/ui/buildPanel.ts
/src/ui/toasts.ts

/src/testing/GameHarness.ts
/src/testing/DeterministicClock.ts
/src/testing/StubRenderer.ts
/src/testing/StubAudio.ts
/src/testing/StubSave.ts
/src/testing/assertions.ts
/src/testing/fullPlaythrough.ts

/tests/unit/rng.spec.ts
/tests/unit/inventory.spec.ts
/tests/unit/shop.spec.ts
/tests/unit/pathfinding.spec.ts
/tests/unit/placement.spec.ts
/tests/unit/fishing.spec.ts
/tests/unit/respawn.spec.ts
/tests/unit/goals.spec.ts
/tests/unit/furniture.spec.ts
/tests/unit/save.spec.ts
/tests/unit/assetManifest.spec.ts

/tests/integration/worldGenerator.spec.ts
/tests/integration/movement.spec.ts
/tests/integration/tradeFlow.spec.ts
/tests/integration/buildFlow.spec.ts
/tests/integration/museumFlow.spec.ts

/tests/e2e/fullPlaythrough.spec.ts
/tests/e2e/postCompletion.spec.ts
```

### 3.1 Root Files

#### `index.html`

Contains:

- `<div id="game"></div>`
- `<div id="ui-root"></div>`
- `<script type="module" src="/src/main.ts">`

The UI root overlays the canvas and is pointer-transparent except for active UI elements.

#### `vite.config.ts`

Configures Vite for:

- TypeScript.
- Vitest.
- Static asset serving.

#### `tsconfig.json`

Uses strict TypeScript.

#### `package.json`

Required scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

Runtime dependencies:

```json
{}
```

Dev dependencies should include:

- `typescript`
- `vite`
- `vitest`

No runtime dependencies are required.

---

## 4. Global Configuration

### 4.1 `src/config.ts`

Required constants:

```ts
export const TILE_SIZE = 24;

export const WORLD = {
  W: 120,
  H: 120
};

export const VIEW = {
  W: 960,
  H: 540
};

export const FIXED_DT = 1 / 60;

export const PLAYER = {
  WALK_SPEED: 6,
  WATER_SPEED: 3,
  INTERACT_RADIUS: 1.2,
  BOUND_HALF: 0.3
};

export const INTERIOR_ZOOM = 2;

export const SAVE_VERSION = 1;
export const SAVE_KEY = "collector_game_save_v1";
```

### 4.2 Coordinate System

Use tile coordinates as floating-point values for player position.

- `x` is tile units.
- `y` is tile units.
- Integer tile coordinate `(x, y)` means the tile with top-left at that coordinate.
- Tile center is `(x + 0.5, y + 0.5)`.
- Rendering converts tile units to pixels by multiplying by `TILE_SIZE`.

World tile integer coordinates:

```ts
x: 0..119
y: 0..119
```

---

## 5. Core Types

### 5.1 `src/types.ts`

Required base types:

```ts
export type Vec2 = {
  x: number;
  y: number;
};

export type SceneId = "exterior" | "home" | "museum";

export type Category = "berry" | "ore" | "fish";

export type Tier = 1 | 2 | 3;

export type ResourceId =
  | "sweet_berry"
  | "moon_berry"
  | "ember_berry"
  | "copper_ore"
  | "silver_ore"
  | "crystal_shard"
  | "minnow"
  | "trout"
  | "moonfish";

export type ToolId =
  | "woven_basket"
  | "honey_pouch"
  | "ember_satchel"
  | "hand_pick"
  | "copper_pick"
  | "silver_pick"
  | "short_rod"
  | "bamboo_rod"
  | "moon_rod";

export type FurnitureId =
  | "berry_planter"
  | "berry_jar"
  | "rug"
  | "berry_bench"
  | "berry_rug"
  | "side_table"
  | "bookshelf"
  | "ore_lamp"
  | "ore_workbench"
  | "fish_net_rack"
  | "fish_barrel"
  | "water_shelf"
  | "fish_bench"
  | "fish_tank"
  | "small_display_case"
  | "pedestal"
  | "crystal_display_case"
  | "moon_display_case";

export type BuildingId = "home" | "museum";

export type GoalId =
  | "firstHarvest"
  | "firstTrades"
  | "cozyHome"
  | "openMuseum"
  | "fullCollection"
  | "curatorsSeal";
```

### 5.2 Tile Types

Use a numeric enum-like object:

```ts
export const TileType = {
  GRASS: 0,
  PATH: 1,
  WATER: 2,
  PERIMETER: 3,
  SOLID: 4,
  DOOR_EXT: 5,
  FLOOR: 6,
  DOOR_INT: 7
} as const;
```

Exterior uses:

- `GRASS`
- `PATH`
- `WATER`
- `PERIMETER`
- `SOLID`
- `DOOR_EXT`

Interiors use:

- `FLOOR`
- `DOOR_INT`

Out-of-bounds is solid by definition.

---

## 6. Content Modules

Content should be typed TypeScript modules, not JSON, so the compiler catches bad data.

### 6.1 `src/content/resources.ts`

Required shape:

```ts
export interface ResourceDef {
  id: ResourceId;
  name: string;
  category: Category;
  tier: Tier;
  baseSell: number;
  stackLimit: number;
  nodeCount: number;
  respawnTime?: number;
  emptyTime?: number;
  charges?: number;
}

export const RESOURCES: Record<ResourceId, ResourceDef>;
```

Values must match `gameplay.md`:

| Resource | Category | Tier | Base Sell | Stack | Nodes | Respawn/Empty | Charges |
|---|---:|---:|---:|---:|---:|---:|---:|
| `sweet_berry` | berry | 1 | 2 | 20 | 30 | 20s | — |
| `moon_berry` | berry | 2 | 5 | 20 | 15 | 45s | — |
| `ember_berry` | berry | 3 | 12 | 20 | 5 | 120s | — |
| `copper_ore` | ore | 1 | 4 | 10 | 25 | 300s | 3 |
| `silver_ore` | ore | 2 | 10 | 10 | 12 | 360s | 3 |
| `crystal_shard` | ore | 3 | 25 | 10 | 4 | 720s | 3 |
| `minnow` | fish | 1 | 4 | 5 | 15 | — | — |
| `trout` | fish | 2 | 10 | 5 | 8 | — | — |
| `moonfish` | fish | 3 | 25 | 5 | 3 | — | — |

### 6.2 `src/content/tools.ts`

Required shape:

```ts
export interface ToolDef {
  id: ToolId;
  name: string;
  category: Category;
  tier: Tier;
  cost: number;
  berryGatherTime?: number;
  mineTime?: number;
  berryBonusChance?: number;
  mineBonusChance?: number;
  fishGreenWidth?: number;
  fishYellowSuccess?: number;
  fishBonusChance?: number;
  fishCooldown?: number;
  fishWaitMin?: number;
  fishWaitMax?: number;
}

export const TOOLS: Record<ToolId, ToolDef>;
```

Tier 1 tools are starting tools and are not bought.

Tool effects must match `gameplay.md`.

### 6.3 `src/content/furniture.ts`

Required shape:

```ts
export interface FurnitureDef {
  id: FurnitureId;
  name: string;
  shop: Category;
  unlockTier: Tier;
  type: "decor" | "display";
  footprint: {
    w: number;
    h: number;
  };
  cost: number;
  slots?: number;
  unique?: boolean;
  museumOnly?: boolean;
  description: string;
}

export const FURNITURE: Record<FurnitureId, FurnitureDef>;
```

Furniture content must match `gameplay.md`.

Display cases:

```ts
small_display_case: { slots: 2, unique: true, museumOnly: true }
pedestal: { slots: 1, unique: true, museumOnly: true }
crystal_display_case: { slots: 3, unique: true, museumOnly: true }
moon_display_case: { slots: 3, unique: true, museumOnly: true }
```

Footprints:

| Furniture | Size |
|---|---:|
| `berry_planter` | 1x1 |
| `berry_jar` | 1x1 |
| `rug` | 2x2 |
| `berry_bench` | 2x1 |
| `berry_rug` | 2x2 |
| `side_table` | 1x1 |
| `bookshelf` | 1x2 |
| `ore_lamp` | 1x1 |
| `ore_workbench` | 2x1 |
| `fish_net_rack` | 1x1 |
| `fish_barrel` | 1x1 |
| `water_shelf` | 1x1 |
| `fish_bench` | 2x1 |
| `fish_tank` | 2x1 |
| `small_display_case` | 1x1 |
| `pedestal` | 1x1 |
| `crystal_display_case` | 1x1 |
| `museum_display_case` | 1x1 |

### 6.4 `src/content/shops.ts`

Required shape:

```ts
export interface ShopDef {
  id: Category;
  npcId: "moss" | "grit" | "reed";
  category: Category;
  displayName: string;
  tagline: string;
  itemsByTier: Record<Tier, Array<ToolId | FurnitureId>>;
}

export const SHOPS: Record<Category, ShopDef>;
```

Shop stock:

| Shop | Tier 1 | Tier 2 | Tier 3 |
|---|---|---|---|
| Berry / Moss | `berry_planter`, `berry_jar`, `rug` | `honey_pouch`, `berry_bench`, `small_display_case` | `ember_satchel`, `berry_rug` |
| Ore / Grit | `side_table`, `bookshelf`, `ore_lamp` | `copper_pick`, `ore_workbench`, `pedestal` | `silver_pick`, `crystal_display_case` |
| Fish / Reed | `fish_net_rack`, `fish_barrel`, `water_shelf` | `bamboo_rod`, `fish_bench`, `fish_tank` | `moon_rod`, `moon_display_case` |

Tier 1 tools are not in shop stock. The player starts with Tier 1 tools.

### 6.5 `src/content/goals.ts`

Required shape:

```ts
export interface GoalDef {
  id: GoalId;
  name: string;
  rewardCoins: number;
  unlocksMuseum?: boolean;
  isFinal?: boolean;
}

export const GOALS: Record<GoalId, GoalDef>;
```

Goal definitions match `gameplay.md`.

### 6.6 `src/content/world.ts`

This file contains functional world constants.

```ts
export const WORLD_RECTS = {
  perimeter: { x1: 0, y1: 0, x2: 119, y2: 119 },
  village: { x1: 45, y1: 45, x2: 75, y2: 75 },
  berryGrove: { x1: 25, y1: 5, x2: 95, y2: 38 },
  oreRidge: { x1: 82, y1: 30, x2: 115, y2: 90 },
  lake: { x1: 5, y1: 40, x2: 40, y2: 100 }
};
```

Exterior doors:

```ts
export const EXT_DOORS = {
  home: { x: 52, y: 68 },
  museum: { x: 68, y: 68 }
};
```

Interior door tiles:

```ts
export const INT_DOORS = {
  home: { x: 5, y: 7 },
  museum: { x: 6, y: 9 }
};
```

Interior floor sizes:

```ts
export const INT_FLOORS = {
  home: { w: 10, h: 8 },
  museum: { w: 12, h: 10 }
};
```

Shopkeeper tiles:

```ts
export const SHOPKEEPERS = [
  { id: "moss", x: 58, y: 65 },
  { id: "grit", x: 60, y: 65 },
  { id: "reed", x: 62, y: 65 }
];
```

Exterior building footprints:

```ts
export const BUILDING_FOOTPRINTS = {
  home: { x1: 50, y1: 66, x2: 54, y2: 70 },
  museum: { x1: 66, y1: 66, x2: 70, y2: 70 }
};
```

Path segments:

```ts
export const PATHS = [
  { x1: 52, y1: 68, x2: 68, y2: 68 },
  { x1: 60, y1: 65, x2: 60, y2: 68 },
  { x1: 58, y1: 65, x2: 62, y2: 65 },
  { x1: 60, y1: 5, x2: 60, y2: 60 },
  { x1: 60, y1: 60, x2: 115, y2: 60 },
  { x1: 41, y1: 60, x2: 60, y2: 60 }
];
```

Node placement masks:

```ts
export const NODE_MASKS = {
  berryAll: { x1: 25, y1: 5, x2: 95, y2: 38 },
  berryEmber: { x1: 25, y1: 5, x2: 95, y2: 12 },
  berryMoon: { x1: 25, y1: 20, x2: 95, y2: 38 },

  oreAll: { x1: 82, y1: 30, x2: 115, y2: 90 },
  oreCrystal: { x1: 108, y1: 30, x2: 115, y2: 90 },
  oreSilver: { x1: 98, y1: 30, x2: 115, y2: 90 },

  fishMinnow: { x1: 5, y1: 40, x2: 40, y2: 100 },
  fishTrout: { x1: 5, y1: 55, x2: 40, y2: 80 },
  fishMoonfish: { x1: 5, y1: 85, x2: 40, y2: 100 }
};
```

Minnow placement should be biased toward shore. In the generator, treat minnow valid tiles as water tiles with `y <= 48` or `y >= 92`.

### 6.7 `src/content/audio.ts`

Maps audio events to asset paths.

Required mapping groups:

```ts
export const AUDIO_FILES = {
  music: { ... },
  ambience: { ... },
  sfx: { ... }
};
```

Asset names should match `visual.md`.

Example:

```ts
export const AUDIO_FILES = {
  music: {
    title: "music/title_loop.ogg",
    village: "music/village_loop.ogg",
    berryGrove: "music/berry_grove_loop.ogg",
    oreRidge: "music/ore_ridge_loop.ogg",
    lakeside: "music/lakeside_loop.ogg",
    home: "music/home_loop.ogg",
    museum: "music/museum_loop.ogg",
    shopLayer: "music/shop_layer.ogg",
    buildLayer: "music/build_layer.ogg",
    goalComplete: "music/goal_complete.ogg",
    shopUnlock: "music/shop_unlock.ogg",
    museumUnlock: "music/museum_unlock.ogg",
    finalCompletion: "music/final_completion.ogg"
  },
  ambience: { ... },
  sfx: { ... }
};
```

---

## 7. Random Number Generator

### 7.1 `src/rng.ts`

Implement a small deterministic RNG.

Required class:

```ts
export class Rng {
  constructor(seed: number);
  next(): number;
  int(min: number, max: number): number;
  range(min: number, max: number): number;
  shuffle<T>(items: T[]): T[];
}
```

Rules:

- `next()` returns a float in `[0, 1)`.
- `int(min, max)` returns an integer in `[min, max]` inclusive.
- `range(min, max)` returns a float in `[min, max)`.
- `shuffle` uses Fisher-Yates.
- Same seed produces same sequence.

Use one RNG for world generation and separate RNG streams for runtime randomness where deterministic tests need to control them.

World generation seed:

```ts
const WORLD_SEED = 42;
```

Runtime seed:

```ts
const RUNTIME_SEED = 12345;
```

The harness may replace the runtime RNG.

---

## 8. Clock and Fixed Timestep

### 8.1 `src/clock.ts`

Production clock uses `performance.now()`.

Required interface:

```ts
export interface Clock {
  readonly now: number;
  subscribe(handler: (dt: number) => void): () => void;
}
```

The game update loop should accumulate real time and consume it in fixed `FIXED_DT` steps.

### 8.2 Fixed Timestep Rules

- Simulation updates at 60 Hz.
- All gameplay timers use the fixed clock.
- Rendering may run at display refresh rate.
- Tests use `DeterministicClock`.

Why:

Fixed timestep makes fishing timers, respawn timers, supply recovery, and movement deterministic and testable.

---

## 9. Event Bus

### 9.1 `src/events.ts`

Implement a small event bus.

```ts
export type EventHandler<T = unknown> = (payload: T) => void;

export class EventBus {
  on<T>(event: string, handler: EventHandler<T>): () => void;
  emit<T>(event: string, payload: T): void;
}
```

Required events:

```text
player:coinsChanged
player:positionChanged
inventory:changed
resource:collected
resource:sold
shop:supplyChanged
shop:tierChanged
goal:progress
goal:completed
museum:unlocked
specimen:unlocked
tool:purchased
furniture:purchased
furniture:placed
furniture:removed
furniture:sold
specimen:assigned
specimen:unassigned
building:scoreChanged
completion:final
audio:play
fx:coinFly
fx:resourcePop
fx:toast
```

Why:

Systems should not directly update UI, audio, or goals. The event bus keeps the game testable and avoids circular dependencies.

---

## 10. Game State

### 10.1 `src/state/gameState.ts`

Required state shape:

```ts
export interface InventorySlot {
  resourceId: ResourceId | null;
  count: number;
}

export interface BuildItem {
  instanceId: string;
  furnitureId: FurnitureId;
  previouslyPlaced: boolean;
}

export interface PlacedFurniture {
  instanceId: string;
  furnitureId: FurnitureId;
  building: BuildingId;
  tile: Vec2;
  rotation: 0 | 1 | 2 | 3;
}

export interface DisplaySlot {
  slotId: string;
  specimenId: ResourceId | null;
}

export interface ShopState {
  supply: number;
  cumulativeSold: number;
  lastSaleTime: number;
}

export interface GameState {
  version: number;
  idCounter: number;

  scene: SceneId;
  player: {
    pos: Vec2;
    coins: number;
    tools: {
      berry: Tier;
      ore: Tier;
      fish: Tier;
    };
  };

  inventory: InventorySlot[];
  buildInventory: BuildItem[];
  placed: PlacedFurniture[];

  nodes: Record<string, NodeState>;
  shopStates: Record<Category, ShopState>;

  collection: {
    unlocked: Record<ResourceId, boolean>;
    salesByResource: Record<ResourceId, number>;
    salesByCategory: Record<Category, number>;
  };

  displaySlots: Record<string, DisplaySlot[]>;

  goals: {
    completed: Record<GoalId, boolean>;
  };

  museumUnlocked: boolean;
  completionShown: boolean;

  settings: {
    musicVolume: number;
    sfxVolume: number;
    ambienceVolume: number;
    reduceMotion: boolean;
    highContrast: boolean;
  };
}
```

Node state:

```ts
export type NodeState =
  | {
      kind: "berry";
      count: number;
      empty: boolean;
      respawnTimer: number;
    }
  | {
      kind: "ore";
      charges: number;
      empty: boolean;
      respawnTimer: number;
    }
  | {
      kind: "fish";
      cooldownTimer: number;
    };
```

### 10.2 Starting State

New game:

```ts
{
  version: SAVE_VERSION,
  idCounter: 0,
  scene: "exterior",
  player: {
    pos: { x: 52, y: 67.5 },
    coins: 25,
    tools: { berry: 1, ore: 1, fish: 1 }
  },
  inventory: 10 empty slots,
  buildInventory: [],
  placed: [],
  nodes: generated node states,
  shopStates: all supply 0, cumulativeSold 0, lastSaleTime 0,
  collection: all false, sales 0,
  displaySlots: {},
  goals: all false,
  museumUnlocked: false,
  completionShown: false,
  settings: default
}
```

Default settings:

```ts
{
  musicVolume: 0.7,
  sfxVolume: 0.8,
  ambienceVolume: 0.4,
  reduceMotion: false,
  highContrast: false
}
```

---

## 11. World Generation

### 11.1 `src/world/tileMap.ts`

Required class:

```ts
export class TileMap {
  constructor(width: number, height: number, defaultType: number);
  readonly width: number;
  readonly height: number;
  readonly tiles: Uint8Array;
  inBounds(x: number, y: number): boolean;
  get(x: number, y: number): number;
  set(x: number, y: number, type: number): void;
}
```

Out-of-bounds `get` should return `TileType.SOLID`.

### 11.2 `src/world/worldGenerator.ts`

Required function:

```ts
export function generateWorld(seed: number): GeneratedWorld;
```

`GeneratedWorld`:

```ts
export interface GeneratedWorld {
  exterior: TileMap;
  home: TileMap;
  museum: TileMap;
  nodes: WorldNode[];
}

export interface WorldNode {
  id: string;
  kind: "berry" | "ore" | "fish";
  resourceId: ResourceId;
  tile: Vec2;
}
```

### 11.3 Exterior Generation Order

Generate exterior in this order:

1. Fill all tiles with `GRASS`.
2. Mark perimeter tiles as `PERIMETER`.
3. Mark lake rectangle as `WATER`.
4. Mark village, berry grove, and ore ridge tile variants if needed.
5. Mark exterior building footprints as `SOLID`.
6. Mark path segments as `PATH`.
7. Mark exterior doors as `DOOR_EXT`.

Path segment rules:

- Horizontal or vertical line only.
- Overwrite `GRASS` to `PATH`.
- Do not overwrite `PERIMETER`.
- Do not convert water to path.
- If a path tile is water, skip it.

Why:

The lake must remain walkable water. Paths should not create bridges across water.

### 11.4 Interior Generation

Home:

- Width: `10`
- Height: `8`
- All tiles `FLOOR`
- Door tile at `(5, 7)` set to `DOOR_INT`

Museum:

- Width: `12`
- Height: `10`
- All tiles `FLOOR`
- Door tile at `(6, 9)` set to `DOOR_INT`

Why:

Using the floor dimensions directly matches the gameplay coordinates and avoids ambiguous wall-border coordinates. The renderer draws a visual wall border outside the floor.

### 11.5 Node Placement Algorithm

Use seeded RNG with seed `42`.

For each resource quota:

1. Build a list of valid candidate tiles.
2. Shuffle candidates with RNG.
3. Try minimum distances in this order: `[4, 3, 1, 0]`.
4. Place a node if Chebyshev distance to all already placed nodes is at least the current minimum distance.
5. Stop when quota is reached.
6. If a quota cannot be met at minimum distance `0`, throw a descriptive error.

Placement order:

```text
fish:
  moonfish
  trout
  minnow

berry:
  ember_berry
  moon_berry
  sweet_berry

ore:
  crystal_shard
  silver_ore
  copper_ore
```

Why:

Placing rare tier 3 nodes first guarantees they are placed in their intended submask before common nodes consume space.

### 11.6 Node Validity

A berry or ore tile is invalid if:

- It is perimeter.
- It is path.
- It is water.
- It is building solid.
- It is within Chebyshev distance `2` of any exterior door.
- It is occupied by another node.

A fish tile is invalid if:

- It is not water.
- It is perimeter.
- It is path.
- It is within Chebyshev distance `2` of any exterior door.
- It is occupied by another node.

Fish spot quotas:

| Fish | Count |
|---|---:|
| `moonfish` | 3 |
| `trout` | 8 |
| `minnow` | 15 |

Berry quotas:

| Berry | Count |
|---|---:|
| `ember_berry` | 5 |
| `moon_berry` | 15 |
| `sweet_berry` | 30 |

Ore quotas:

| Ore | Count |
|---|---:|
| `crystal_shard` | 4 |
| `silver_ore` | 12 |
| `copper_ore` | 25 |

### 11.7 Node IDs

Generate stable IDs:

```ts
berry_sweet_0
berry_sweet_1
...
ore_copper_0
...
fish_minnow_0
...
```

These IDs are used for save state.

---

## 12. Collision and Movement

### 12.1 `src/world/collision.ts`

Required functions:

```ts
export function isTileSolid(scene: SceneId, map: TileMap, x: number, y: number): boolean;
export function isNodeSolidAt(tile: Vec2): boolean;
export function isFurnitureSolidAt(building: BuildingId, tile: Vec2, placed: PlacedFurniture[]): boolean;
export function isPlayerBlocked(pos: Vec2, half: number, solidAt: (x: number, y: number) => boolean): boolean;
```

Solid exterior tiles:

- `PERIMETER`
- `SOLID`

Walkable exterior tiles:

- `GRASS`
- `PATH`
- `WATER`
- `DOOR_EXT`

Interior:

- Out of bounds is solid.
- `FLOOR` is walkable.
- `DOOR_INT` is walkable.

Resource node solidity:

- Berry nodes are solid.
- Ore nodes are solid.
- Fish spots are not solid.

Furniture solidity:

- Placed furniture is solid in its building interior.

Player collision:

- Use axis-separated movement.
- Check four corners of a bounding box with half-size `PLAYER.BOUND_HALF`.
- If x movement is blocked, keep old x.
- If y movement is blocked, keep old y.

Why:

Axis-separated movement gives simple sliding along walls and is stable at 60 Hz.

### 12.2 `src/systems/movement.ts`

Update:

1. Read input vector from WASD/arrows.
2. Normalize diagonal input.
3. Determine speed:
   - If current center tile is water and scene is exterior, use `PLAYER.WATER_SPEED`.
   - Otherwise use `PLAYER.WALK_SPEED`.
4. Move x and y separately with collision.
5. Update player position.
6. Emit `player:positionChanged`.

---

## 13. Interaction

### 13.1 `src/systems/interaction.ts`

Required:

```ts
export type Interactable =
  | { type: "berry"; nodeId: string; label: string }
  | { type: "ore"; nodeId: string; label: string }
  | { type: "fish"; nodeId: string; label: string }
  | { type: "shop"; shop: Category; label: string }
  | { type: "door_ext"; building: BuildingId; label: string }
  | { type: "door_int"; building: BuildingId; label: string };

export function getTargetInteractable(playerPos: Vec2, scene: SceneId): Interactable | null;
```

Target selection:

- Consider only objects within `PLAYER.INTERACT_RADIUS` tiles.
- Use Euclidean distance from player center to object tile center.
- If multiple are in range, choose nearest.
- If tie, choose in this priority:
  1. Door.
  2. Shop.
  3. Berry.
  4. Ore.
  5. Fish.

Fish interaction rule:

- The fish spot can be targeted if within radius.
- Fishing only starts if the player’s center tile is the fish spot tile.

Museum door:

- If museum is locked, interact does nothing.
- Prompt shows `Museum Locked`.

### 13.2 Door Transitions

Exterior door interact:

- If building is home:
  - Set scene to `home`.
  - Set player position to interior home door center.
- If building is museum:
  - If `museumUnlocked` is false, do nothing.
  - Otherwise set scene to `museum`.
  - Set player position to interior museum door center.

Interior door interact:

- Set scene to `exterior`.
- Set player position to exterior door center.

On scene change:

- Cancel active gathering.
- Cancel active fishing.
- Exit build mode.
- Update music zone.
- Update camera.

---

## 14. Inventory

### 14.1 `src/systems/inventory.ts`

Required API:

```ts
export function createInventory(): InventorySlot[];
export function inventoryCount(inv: InventorySlot[], resourceId: ResourceId): number;
export function capacityFor(inv: InventorySlot[], resourceId: ResourceId): number;
export function addItem(inv: InventorySlot[], resourceId: ResourceId, amount: number): number;
export function removeItem(inv: InventorySlot[], resourceId: ResourceId, amount: number): number;
export function clearCategory(inv: InventorySlot[], category: Category): void;
```

Rules:

- Inventory has exactly 10 slots.
- Each slot stores one resource type and count.
- Multiple stacks of the same resource are allowed.
- `addItem` fills existing compatible stacks first, then empty slots.
- `removeItem` removes from any compatible slots.
- `capacityFor` returns how many units can currently be added.

Stack limits:

| Category | Stack Limit |
|---|---:|
| berry | 20 |
| ore | 10 |
| fish | 5 |

Why multiple stacks are allowed:

The gameplay document does not forbid them, and they simplify partial berry collection and sell-all behavior.

---

## 15. Gathering

### 15.1 `src/systems/gather.ts`

Required state:

```ts
export type GatherState = {
  targetNodeId: string;
  kind: "berry" | "ore";
  timer: number;
  duration: number;
} | null;
```

API:

```ts
export function startGather(state: GameState, node: WorldNode, tool: ToolDef): boolean;
export function updateGather(state: GameState, dt: number, interactHeld: boolean, target: Interactable | null): void;
```

Rules:

- Gathering only starts if inventory capacity for the resource is at least `1`.
- The player must be targeting the node.
- Releasing interact cancels progress.
- Moving out of interaction radius cancels progress.
- Target changing to a different node cancels progress.
- Node becoming empty cancels progress.

### 15.2 Berry Yield Rule

The gameplay document contains two conflicting rules:

1. “A full bush contains 1 or 2 berries. Picking removes the entire available stack.”
2. The berry respawn pseudo-code only yields `1`, or `2` with bonus.

Engineering decision:

- A berry node stores `count` as `1` or `2`.
- Base yield is `node.count`.
- If inventory capacity is less than `node.count`, the player collects only as many as fit.
- If the node still has berries after collection, it remains full with the remaining count.
- Bonus yield can raise the total from `1` to `2`, but never above `2`.

Algorithm:

```ts
cap = inventory.capacityFor(inv, resourceId)
base = node.count
yield = Math.min(base, cap)

if yield < 2 && cap >= 2 && rng.next() < tool.berryBonusChance:
  yield = 2

node.count -= yield
inventory.add(resourceId, yield)

if node.count == 0:
  node.empty = true
  node.respawnTimer = resource.respawnTime
```

Why:

This respects “at least one unit can fit”, avoids destroying uncollected berries when inventory is tight, and keeps the max visible yield at `+2`, matching visual feedback.

### 15.3 Mining Yield Rule

Algorithm:

```ts
if node.charges <= 0: fail
cap = inventory.capacityFor(inv, resourceId)
if cap <= 0: fail

yield = 1
if cap >= 2 && rng.next() < tool.mineBonusChance:
  yield = 2

node.charges -= 1
inventory.add(resourceId, yield)

if node.charges == 0:
  node.empty = true
  node.respawnTimer = resource.emptyTime
```

Mining consumes exactly one charge regardless of bonus yield.

---

## 16. Respawn

### 16.1 Berry Respawn

Update empty berry nodes:

```ts
node.respawnTimer -= dt
if node.respawnTimer <= 0:
  node.count = rng.int(1, 2)
  node.empty = false
```

### 16.2 Ore Respawn

Update empty ore nodes:

```ts
node.respawnTimer -= dt
if node.respawnTimer <= 0:
  node.charges = 3
  node.empty = false
```

---

## 17. Fishing

### 17.1 `src/systems/fishing.ts`

Required state:

```ts
export type FishingState =
  | {
      kind: "casting";
      spotId: string;
      timer: number;
    }
  | {
      kind: "waiting";
      spotId: string;
      timer: number;
      waitDuration: number;
    }
  | {
      kind: "biteMeter";
      spotId: string;
      timer: number;
      duration: 1.5;
    }
  | null;
```

Required API:

```ts
export function startFishing(state: GameState, spot: WorldNode, tool: ToolDef, rng: Rng): boolean;
export function updateFishing(state: GameState, dt: number, rng: Rng): void;
export function strike(state: GameState, rng: Rng): void;
```

### 17.2 Fishing Sequence

1. Player stands on fish spot.
2. Player presses interact.
3. If spot cooldown is active, fail silently.
4. If inventory cannot hold at least one fish, prompt `Bag Full`.
5. State becomes `casting`, duration `0.6s`.
6. After cast, state becomes `waiting` for random wait duration.
7. After wait, state becomes `biteMeter` for `1.5s`.
8. Player presses interact during bite meter to strike.
9. If meter expires, attempt fails.
10. If player leaves the fish spot during any active fishing state, attempt fails.

### 17.3 Bite Meter

Meter progress:

```ts
p = 1 - timer / 1.5
```

`p` goes from `0` to `1`.

Green zone is centered at `p = 0.5`.

Green width from tool:

| Tier | Green Width |
|---:|---:|
| 1 | 0.30s |
| 2 | 0.40s |
| 3 | 0.50s |

Convert to progress width:

```ts
greenWidth = tool.fishGreenWidth / 1.5
```

Yellow zones:

```ts
yellowWidth = 0.20 / 1.5
```

Zone check:

```ts
if p is inside green:
  success = true
else if p is inside yellow:
  success = rng.next() < tool.fishYellowSuccess
else:
  success = false
```

### 17.4 Catch Result

If success:

```ts
cap = inventory.capacityFor(inv, fishResourceId)
yield = 1
if cap >= 2 && rng.next() < tool.fishBonusChance:
  yield = 2
inventory.add(fishResourceId, yield)
```

If success or failure:

```ts
spot.cooldownTimer = tool.fishCooldown
fishingState = null
```

### 17.5 Leaving Fish Spot

If player’s center tile changes away from the active fish spot:

- Attempt fails.
- Cooldown starts on that spot.
- Active fishing state clears.

Why:

The gameplay document says fishing is committed once the cast starts. This prevents players from abandoning attempts without cooldown consequences.

---

## 18. Economy

### 18.1 `src/systems/economy.ts`

Required API:

```ts
export function currentUnitPrice(shop: ShopState, resource: ResourceDef): number;
export function sellItems(state: GameState, shopId: Category, items: Array<{ resourceId: ResourceId; amount: number }>);
export function updateShopRecovery(state: GameState, dt: number): void;
export function shopTier(shop: ShopState): Tier;
```

### 18.2 Price Calculation

```ts
supplyTier = Math.min(3, Math.floor(shop.supply))
multiplier = [1.00, 0.85, 0.70, 0.60][supplyTier]
price = Math.max(1, Math.floor(resource.baseSell * multiplier))
```

### 18.3 Selling

When selling `n` units of one resource:

1. Use current unit price before supply update.
2. Remove resources from inventory.
3. Add coins.
4. Update supply:

```ts
shop.supply = Math.min(3.0, shop.supply + n / 5)
```

5. Update cumulative sales:

```ts
shop.cumulativeSold += n
state.collection.salesByResource[resourceId] += n
state.collection.salesByCategory[category] += n
shop.lastSaleTime = clock.now
```

6. Check shop tier unlock.
7. Check goals.
8. Emit events.

### 18.4 Sell All

`Sell All` sells every inventory stack matching the shop category.

All sold units in that sale count toward the same supply update.

### 18.5 Supply Recovery

Update each shop every frame:

```ts
if shop.supply > 0:
  while clock.now - shop.lastSaleTime >= 120:
    shop.supply = Math.max(0, shop.supply - 1.0)
    shop.lastSaleTime += 120
else if clock.now - shop.lastSaleTime > 120:
  shop.lastSaleTime = clock.now
```

Why:

This recovers supply over time without permanently stuck prices and avoids repeated one-second decay checks.

### 18.6 Shop Tier

```ts
if cumulativeSold >= 25:
  tier = 3
else if cumulativeSold >= 5:
  tier = 2
else:
  tier = 1
```

Shop tier is per shop, not global.

---

## 19. Shop Buying

### 19.1 Required API

```ts
export function canBuy(state: GameState, shopId: Category, itemId: ToolId | FurnitureId): { ok: boolean; reason?: string };
export function buyItem(state: GameState, shopId: Category, itemId: ToolId | FurnitureId): boolean;
```

### 19.2 Buying Rules

General:

- Item must be visible in current shop tier.
- Player must have enough coins.
- Tools cannot be bought if current tool tier is greater than or equal to item tier.
- Tools cannot be bought if item tier is lower than current tool tier.
- Display cases are unique.
- If a unique display case is already owned anywhere, buying is invalid.

Tool purchase:

- Set player tool tier for that category to item tier.
- Do not add to inventory.

Furniture purchase:

- Add a build inventory item:

```ts
{
  instanceId: nextId("f"),
  furnitureId: itemId,
  previouslyPlaced: false
}
```

### 19.3 Ownership of Unique Display Cases

A unique display case is considered owned if:

- It exists in `buildInventory`, or
- It exists in `placed`.

Selling it from build inventory removes ownership.

---

## 20. Furniture Placement

### 20.1 `src/systems/furniture.ts`

Required API:

```ts
export type PlacementResult =
  | { valid: true }
  | { valid: false; reason: PlacementReason };

export type PlacementReason =
  | "Museum Only"
  | "Not Floor"
  | "Covers Door"
  | "Covers Player"
  | "Blocked"
  | "Blocks Door Path";

export function getFootprint(furnitureId: FurnitureId, rotation: number): { w: number; h: number };
export function canPlace(
  state: GameState,
  building: BuildingId,
  furnitureId: FurnitureId,
  anchorTile: Vec2,
  rotation: number
): PlacementResult;
export function placeFurniture(state: GameState, building: BuildingId, buildInstanceId: string, anchorTile: Vec2, rotation: number): boolean;
export function removePlacedFurniture(state: GameState, instanceId: string): void;
export function resellBuildItem(state: GameState, instanceId: string): number;
```

### 20.2 Rotation

Rotation is `0..3`.

Footprint rules:

- `0`: original footprint.
- `1`: swapped footprint.
- `2`: original footprint.
- `3`: swapped footprint.

Square footprints do not change.

### 20.3 Placement Validity Order

Check in this order:

1. Display case in non-museum building: `Museum Only`.
2. Any footprint tile outside interior floor: `Not Floor`.
3. Any footprint tile is door: `Covers Door`.
4. Any footprint tile is occupied by placed furniture: `Blocked`.
5. Any footprint tile is player’s current tile: `Covers Player`.
6. Simulate occupancy and run path check: `Blocks Door Path`.
7. Valid.

Why this order:

The UI should show the most useful reason first.

### 20.4 Path Check

Use `src/world/pathfinding.ts`.

```ts
export function pathExists(
  map: TileMap,
  start: Vec2,
  goal: Vec2,
  blockedTiles: Set<string>
): boolean;
```

Use 4-direction BFS.

Passable interior tiles:

- `FLOOR`
- `DOOR_INT`

Blocked tiles:

- Occupied furniture tiles.
- Proposed new furniture tiles.

Start tile is player’s current floor tile.
Goal tile is interior door tile.

Why 4-direction:

It is conservative, simple, and sufficient for placement validation.

### 20.5 Removing Furniture

When placed furniture is removed:

1. Remove from `placed`.
2. Add to build inventory:

```ts
{
  instanceId: same instanceId,
  furnitureId: same furnitureId,
  previouslyPlaced: true
}
```

3. If display case, unassign all its specimens.
4. Update building scores.
5. Update goal progress.
6. Emit events.

### 20.6 Reselling Unplaced Furniture

Refund:

```ts
if item.previouslyPlaced:
  refund = Math.max(1, Math.floor(cost / 2))
else:
  refund = cost
```

Remove item from build inventory.

If the item was a display case, ownership is removed.

---

## 21. Museum and Specimens

### 21.1 `src/systems/museum.ts`

Required API:

```ts
export function initializeDisplaySlots(state: GameState, placedId: string, furnitureId: FurnitureId): void;
export function assignSpecimen(state: GameState, slotId: string, resourceId: ResourceId): boolean;
export function unassignSpecimen(state: GameState, slotId: string): void;
export function unassignAllForPlacedItem(state: GameState, placedInstanceId: string): void;
export function getAssignedSpecimenCount(state: GameState): number;
export function getMuseumScore(state: GameState): number;
export function getHomeScore(state: GameState): number;
```

### 21.2 Display Slots

When a display case is placed:

- Create one slot per `FurnitureDef.slots`.
- Slot IDs:

```ts
`${instanceId}_slot_${index}`
```

Each slot starts empty.

### 21.3 Assignment Rules

A specimen can be assigned if:

- The display case is placed in the museum.
- The slot is empty.
- The specimen is unlocked.
- The specimen is not already assigned to another slot.

Removing or selling the display case unassigns all its slots.

### 21.4 Scores

Furniture value:

```ts
value = Math.ceil(cost / 10)
```

Home score:

```ts
sum(value of placed home furniture)
```

Museum score:

```ts
sum(exhibit score of assigned specimens)
+ sum(value of placed museum furniture)
```

Exhibit scores match `gameplay.md`:

| Specimen | Score |
|---|---:|
| `sweet_berry` | 10 |
| `moon_berry` | 25 |
| `ember_berry` | 60 |
| `copper_ore` | 10 |
| `silver_ore` | 25 |
| `crystal_shard` | 60 |
| `minnow` | 10 |
| `trout` | 25 |
| `moonfish` | 60 |

---

## 22. Goals

### 22.1 `src/systems/goals.ts`

Required API:

```ts
export function checkGoals(state: GameState): GoalId[];
```

`checkGoals` should return newly completed goal IDs.

Call it after:

- Resource collected.
- Resource sold.
- Furniture placed.
- Furniture removed.
- Specimen assigned.
- Specimen unassigned.
- Display case removed.
- Display case sold.

### 22.2 Goal Conditions

```ts
firstHarvest:
  collection.salesByResource? no, use collected counts.
```

Need tracked collected counts separately from sales.

Add to state:

```ts
collection.collected: Record<ResourceId, number>
```

Update `collected` when resources are added to inventory.

Goal conditions:

```ts
firstHarvest:
  collected.sweet_berry >= 1
  collected.copper_ore >= 1
  collected.minnow >= 1

firstTrades:
  salesByResource.sweet_berry >= 5
  salesByResource.copper_ore >= 5
  salesByResource.minnow >= 5

cozyHome:
  placedCountHome >= 5

openMuseum:
  placedDisplayCaseCountMuseum >= 3
  assignedSpecimenCount >= 3

fullCollection:
  all 9 resources unlocked

curatorsSeal:
  salesByCategory.berry >= 25
  salesByCategory.ore >= 25
  salesByCategory.fish >= 25
  assignedSpecimenCount >= 9
  placedCountMuseum >= 12
```

### 22.3 Goal Completion Behavior

- A goal once complete remains complete.
- Progress can decrease before completion.
- Final goal completion is not reversed if furniture is removed later.
- Rewards are granted exactly once.
- `firstTrades` sets `museumUnlocked = true`.
- `curatorsSeal` sets `completionShown = true`.

### 22.4 Museum Unlock

When `museumUnlocked` changes from false to true:

- Emit `museum:unlocked`.
- Emit toast event.
- Play museum unlock stinger.

---

## 23. Collection

### 23.1 Specimen Unlock

When a resource is first added to inventory:

```ts
if !collection.unlocked[resourceId]:
  collection.unlocked[resourceId] = true
  emit "specimen:unlocked"
```

Collection is unlocked by collecting, not selling.

---

## 24. Save and Load

### 24.1 `src/state/save.ts`

Required API:

```ts
export function serialize(state: GameState): string;
export function deserialize(data: string): GameState | null;
```

### 24.2 Save Backend

```ts
export interface SaveBackend {
  load(): string | null;
  save(data: string): void;
  clear(): void;
}
```

Production save backend uses `localStorage` with `SAVE_KEY`.

### 24.3 Save Contents

Save:

- Version.
- ID counter.
- Scene.
- Player position, coins, tools.
- Inventory.
- Build inventory.
- Placed furniture.
- Node states.
- Shop states.
- Collection counts and unlocked flags.
- Display slots.
- Goals.
- Museum unlocked.
- Completion shown.
- Settings.

Do not save:

- Active gathering state.
- Active fishing state.
- Open UI modals.
- Runtime RNG.
- Camera.

Why:

Transient interaction state is not meaningful across browser reloads and can be discarded safely.

### 24.4 Save Timing

Save:

- Every `5s` while game is running.
- On `visibilitychange` when hidden.
- On `beforeunload`.
- Immediately after:
  - Goal completed.
  - Museum unlocked.
  - Furniture placed/removed/sold.
  - Display case sold.
  - Tool purchased.

Do not save on every coin sale to avoid excessive writes. Autosave and unload save are sufficient.

### 24.5 Corrupt Save

If deserialize fails or version mismatch:

- Return `null`.
- Game starts new.
- Do not attempt migration.

Why:

There is no release history requiring migration. A safe fallback is simpler and less risky.

---

## 25. Rendering

### 25.1 `src/main.ts`

Bootstrap:

1. Create canvas.
2. Create UI root.
3. Create production clock, renderer, audio, save, assets.
4. Create `Game`.
5. Show title screen.
6. On start, create new game or load save.
7. Start audio after user gesture.

### 25.2 `src/render/assetManifest.ts`

Required asset manifest type:

```ts
export interface AssetRect {
  x: number;
  y: number;
  w: number;
  h: number;
}

export interface AssetManifestEntry {
  file: string;
  rect?: AssetRect;
}

export type AssetManifest = Record<string, AssetManifestEntry>;
```

The manifest maps logical sprite keys to files or atlas rects.

Required logical keys include:

- Terrain tiles.
- Resource node states.
- Player states.
- Shopkeeper states.
- Furniture.
- Icons.
- UI images.
- Fish spot states.

The integrating agent should generate or maintain `src/render/assets.json` or a TypeScript manifest. Tests validate that all content-required keys exist.

### 25.3 `src/render/renderer.ts`

Required responsibilities:

- Draw current scene.
- Draw visible tiles.
- Draw nodes.
- Draw actors.
- Draw placed furniture.
- Draw build overlay.
- Draw target highlight.
- Draw gathering progress.
- Draw fishing meter.
- Apply camera transform.
- Apply zoom.
- Support reduce motion.
- Support high contrast.

### 25.4 Camera

Exterior:

- Zoom: `1`.
- Follow player.
- Clamp to world bounds.

Interiors:

- Zoom: `INTERIOR_ZOOM = 2`.
- Follow player.
- If interior pixel size is smaller than viewport, center the whole interior.
- If larger, clamp to interior bounds.

Why:

Interiors are smaller than the viewport. Zooming `2x` keeps furniture placement readable without dynamic zoom complexity.

### 25.5 Draw Order

Use y-sort for entities.

Draw order:

1. Terrain tiles.
2. Water base.
3. Paths.
4. Low decorations.
5. Placed furniture bases.
6. Actors and solid nodes.
7. Tall decorations.
8. Overlays.
9. Effects.
10. UI.

Entity sort key:

```ts
sortY = tileY + 0.5 + heightOffset
```

Use height offset for tall nodes and display cases if needed.

### 25.6 Tile Variants

Use deterministic hash:

```ts
variant = hash(x, y) % 4
```

If the manifest has multiple variants, choose one. If not, use the base tile.

Why:

Avoid repetitive flat tiles without asset randomness.

### 25.7 Missing Assets

If an asset key is missing:

- Draw a colored rectangle.
- Draw the key name if debug mode is enabled.
- Do not crash.

Why:

This lets the game be validated before all final assets are integrated.

### 25.8 Effects

`src/systems/effects.ts` and `src/render/particles.ts` should support:

- Resource icon pop.
- `+1` or `+2` text.
- Coin fly.
- Furniture place dust.
- Display case glow.
- Goal pulse.

Rules:

- Max active particles: `20`.
- Disable decorative particles when `reduceMotion` is true.
- Do not use full-screen flash.
- Do not use screen shake.

---

## 26. UI Architecture

### 26.1 `src/ui/ui.ts`

The UI should be DOM-based.

Required root components:

```text
#title-screen
#hud
#shop-modal
#ledger-modal
#build-panel
#toast-layer
#completion-screen
```

UI should not own gameplay state. It reads `GameState` and calls `Game` actions.

### 26.2 `Game` Action API

The integrating agent should expose actions on `Game`:

```ts
class Game {
  actions: {
    start(): void;
    continue(): void;
    newGame(): void;

    interact(): void;
    openLedger(): void;
    closeLedger(): void;
    openSettings(): void;
    closeSettings(): void;

    shop: {
      open(shopId: Category): void;
      close(): void;
      selectTab(tab: "buy" | "sell"): void;
      sellOne(resourceId: ResourceId): void;
      sellStack(resourceId: ResourceId): void;
      sellAll(): void;
      buy(itemId: ToolId | FurnitureId): void;
    };

    build: {
      toggle(): void;
      selectBuildItem(instanceId: string): void;
      rotate(): void;
      placeAt(tile: Vec2): void;
      selectPlaced(instanceId: string): void;
      removeSelectedPlaced(): void;
      sellBuildItem(instanceId: string): void;
    };

    museum: {
      assign(slotId: string, resourceId: ResourceId): void;
      unassign(slotId: string): void;
    };
  };
}
```

Why:

UI, tests, and future agents use the same action surface. This prevents UI from directly mutating state inconsistently.

### 26.3 HUD

`src/ui/hud.ts` renders:

- Location label.
- Ledger button.
- Coins.
- Minimap.
- Tool tier indicators.
- Inventory.
- Contextual hints.

HUD updates by subscribing to events.

### 26.4 Shop UI

`src/ui/shop.ts` renders:

- Shopkeeper name.
- Coin total.
- Buy/Sell tabs.
- Sell rows.
- Supply meter.
- Buy grid.
- Locked item requirements.

Sell controls:

- Click sell button: sell one.
- Shift-click row or stack button: sell whole stack.
- Sell All button: sell all compatible resources.

Buy controls:

- Click buy button.
- Locked items are disabled.
- Unique owned display cases show `Unique: already owned`.

### 26.5 Ledger UI

`src/ui/ledger.ts` renders three tabs:

1. Goals.
2. Collection.
3. Scores.

Goals tab:

- Current active goal.
- Progress fractions.
- Completed goals.
- Rewards.

Collection tab:

- 3x3 grid.
- Locked/unlocked state.
- Location hint.
- Exhibit score.
- Displayed status.

Scores tab:

- Home score.
- Museum score.
- Home furniture count.
- Museum furniture count.
- Museum exhibit count.

### 26.6 Build Panel

`src/ui/buildPanel.ts` renders:

- Build inventory list.
- Selected item card.
- Rotation state.
- Placement validity.
- Invalid reason.
- Building score.
- Exhibit panel when a display case is selected.
- Resell panel for unplaced furniture.

Controls:

- `B` toggles build mode.
- Mouse moves ghost.
- `R` rotates.
- Left click confirms placement.
- `X` or right click deletes selected placed furniture.
- `Esc` cancels.

### 26.7 Toasts

`src/ui/toasts.ts` renders top-center toasts.

Rules:

- Max 3 visible.
- Each toast lasts `3s`.
- Stack downward.
- Older toasts fade first.
- No bounce.
- Respect reduce motion.

### 26.8 Title Screen

`src/ui/title.ts` shows:

- Game title.
- `Start` button.
- `Continue` button if save exists.
- Controls summary.
- Settings controls:
  - Music volume.
  - SFX volume.
  - Ambience volume.
  - Reduce Motion toggle.
  - High Contrast toggle.

### 26.9 Completion Screen

Show when `curatorsSeal` completes:

- `Curator’s Seal Complete`
- Subtext: `Your museum is open.`
- Continue button.
- No confetti.
- Slow gold leaf if motion allowed.

---

## 27. Audio Implementation

### 27.1 `src/systems/audio.ts`

Required class:

```ts
export class AudioManager {
  constructor(settings: Settings);
  initialize(): void;
  setSettings(settings: Settings): void;
  playSfx(event: string): void;
  setMusicZone(zone: ZoneId): void;
  setLayer(layer: "shop" | "build" | null): void;
  playStinger(stinger: string): void;
}
```

### 27.2 Audio Context

Use Web Audio API.

- Create `AudioContext` lazily.
- Call `resume()` after user gesture.
- If audio is not initialized, all play calls are no-ops.

Why:

Browsers block audio before user interaction.

### 27.3 Music

Music zones:

```text
title
village
berryGrove
oreRidge
lakeside
home
museum
```

Crossfade:

- Zone to zone: `1s`.
- World to interior: `1s`.

Activity layers:

- `shop`
- `build`

Layer add/remove: `0.5s` crossfade.

### 27.4 Stingers

Play without replacing current music:

- `goalComplete`
- `shopUnlock`
- `museumUnlock`
- `finalCompletion`

### 27.5 SFX

Map events to files from `AUDIO_FILES.sfx`.

Add small pitch variation:

```ts
pitch = 1 + (rng.next() - 0.5) * 0.06
```

Volume categories:

- Normal SFX.
- Important stingers.

### 27.6 Ambience

Ambience loops by zone:

```text
village
berryGrove
oreRidge
lakeside
home
museum
```

Crossfade with zone music.

### 27.7 Settings

Settings volumes are `0..1`.

Reduce motion does not affect audio.

---

## 28. Test Harness

### 28.1 Purpose

The test harness must allow the game to run headless with deterministic time, inputs, and assets.

No canvas, no DOM, no Web Audio, no localStorage should be required for logic tests.

### 28.2 `src/testing/GameHarness.ts`

Required class:

```ts
export interface HarnessOptions {
  seed?: number;
  autoStart?: boolean;
}

export class GameHarness {
  readonly game: Game;
  readonly clock: DeterministicClock;
  readonly save: StubSave;
  readonly audio: StubAudio;
  readonly assets: StubAssets;

  constructor(options?: HarnessOptions);

  start(): void;
  newGame(): void;
  loadSave(data: string): void;

  advanceTime(seconds: number): void;
  advanceTicks(ticks: number): void;

  press(key: GameKey): void;
  release(key: GameKey): void;
  hold(keys: GameKey[]): void;
  releaseAll(): void;

  setMouse(x: number, y: number): void;
  mouseClick(button: "left" | "right", options?: { shift?: boolean }): void;

  waitUntil(predicate: () => boolean, timeoutSeconds?: number): void;

  teleportTo(tile: Vec2): void;
  enterScene(scene: SceneId): void;

  fishing: FishingTestControls;
  collect(resourceId: ResourceId, amount: number): void;
  sellSpecific(resourceId: ResourceId, amount: number): void;
  sellCategory(category: Category, amount: number): void;
  buy(itemId: ToolId | FurnitureId): void;
  placeInBuilding(building: BuildingId, count: number): void;
  assignAllSpecimens(): void;

  snapshot(): GameState;
}
```

### 28.3 `src/testing/DeterministicClock.ts`

Required:

```ts
export class DeterministicClock {
  now: number;
  advance(delta: number): void;
}
```

`advance` should call `game.update(FIXED_DT)` repeatedly until the requested time has elapsed.

### 28.4 Stubs

#### `StubRenderer`

- No rendering.
- Records canvas calls if needed for UI tests.
- Default: no-op.

#### `StubAudio`

Records calls:

```ts
{
  sfx: string[];
  musicZones: string[];
  stingers: string[];
}
```

#### `StubSave`

```ts
{
  data: string | null;
  save(data: string)
  load()
  clear()
}
```

### 28.5 `FishingTestControls`

Required:

```ts
export class FishingTestControls {
  setNextBiteDelay(seconds: number): void;
  setNextStrikeProgress(progress: number): void;
  setNextBonus(success: boolean): void;
  setNextYellow(success: boolean): void;
  forceCatch(): void;
}
```

`forceCatch()` configures the next attempt to:

- Bite delay: very short.
- Strike progress: center green.
- Bonus: false.
- Yellow: irrelevant.

Why:

Full playthrough should not depend on player timing skill. Fishing meter behavior is separately unit-tested.

### 28.6 Harness Helpers

These helpers should use the same `Game.actions` and systems used by the UI.

#### `collect(resourceId, amount)`

- Finds available nodes for that resource.
- Teleports player adjacent to node.
- Starts gathering using the same interaction path.
- Advances time until complete.
- Waits for respawn if necessary.
- Repeats until amount collected.

For fish:

- Uses `fishing.forceCatch()` per catch.

#### `sellSpecific(resourceId, amount)`

- Teleports to matching shop.
- Opens shop.
- Sells requested amount using shop action.

#### `sellCategory(category, amount)`

- Sells from inventory until `salesByCategory[category]` reaches target or inventory is empty.
- If inventory is empty, collects more and repeats.

#### `placeInBuilding(building, count)`

- Enters building.
- Enters build mode.
- Selects build inventory items.
- Finds valid placement tiles using `canPlace`.
- Places count items.

#### `assignAllSpecimens()`

- Ensures all four display cases are placed in museum.
- Assigns each unlocked specimen to an empty slot.

### 28.7 Test Assertions

`src/testing/assertions.ts` should provide:

```ts
expectInventoryContains
expectCoins
expectGoalComplete
expectMuseumUnlocked
expectNodeQuota
expectPathExists
expectPlacementValid
expectSnapshotEqual
```

Tests should use Vitest’s `expect` for basic assertions and these helpers for domain-specific checks.

---

## 29. Required Unit Tests

### 29.1 `tests/unit/rng.spec.ts`

Tests:

1. Same seed produces same `next()` sequence.
2. `int` returns values within inclusive bounds.
3. `range` returns values within bounds.
4. `shuffle` preserves items and changes order deterministically.

### 29.2 `tests/unit/inventory.spec.ts`

Tests:

1. Empty inventory has 10 empty slots.
2. Adding resource creates slot.
3. Adding to existing stack increments count.
4. Stack limit is respected.
5. Overflow creates a second stack if empty slot exists.
6. Full inventory cannot add.
7. `capacityFor` returns correct capacity with existing stack.
8. `capacityFor` returns correct capacity with empty slots.
9. `removeItem` removes correct amount.
10. `removeItem` clears slots at zero.

### 29.3 `tests/unit/shop.spec.ts`

Tests:

1. Price at supply `0` is base price.
2. Supply `0.2` still uses floor `0` multiplier.
3. Supply `1.0` uses `0.85` multiplier.
4. Supply `2.0` uses `0.70` multiplier.
5. Supply `3.0` uses `0.60` multiplier.
6. Final price minimum is `1`.
7. Selling uses price before supply update.
8. Selling `5` increases supply by `1.0`.
9. Supply caps at `3.0`.
10. Cumulative sales update.
11. Shop tier changes at `5` and `25`.
12. Supply recovery after `120s`.
13. Supply recovery does not go below `0`.

### 29.4 `tests/unit/pathfinding.spec.ts`

Tests:

1. Path exists in open floor.
2. Path blocked by wall.
3. Path blocked by furniture.
4. Path exists around obstacle.
5. Start equals goal returns true.
6. Out-of-bounds goal returns false.

### 29.5 `tests/unit/placement.spec.ts`

Use a small interior map.

Tests:

1. Valid 1x1 placement.
2. Valid rotated 2x1 placement.
3. Invalid outside floor.
4. Invalid over door.
5. Invalid over player.
6. Invalid over existing furniture.
7. Invalid display case in home.
8. Invalid if blocks door path.
9. Valid if path still exists.

### 29.6 `tests/unit/fishing.spec.ts`

Tests:

1. Cast starts only if inventory has fish capacity.
2. Cast transition to waiting after `0.6s`.
3. Waiting transition to bite after configured delay.
4. Strike in green succeeds.
5. Strike in yellow uses RNG chance.
6. Strike outside fails.
7. Meter timeout fails.
8. Leaving spot fails and starts cooldown.
9. Successful catch adds fish.
10. Bonus fish only if capacity allows.
11. Cooldown starts after success and failure.
12. Fish spot cannot be used during cooldown.

### 29.7 `tests/unit/respawn.spec.ts`

Tests:

1. Berry node becomes empty after pick.
2. Berry node respawns after respawn time.
3. Respawn count is `1` or `2`.
4. Ore node loses one charge per mine.
5. Ore node becomes empty at zero charges.
6. Ore node respawns with `3` charges after empty time.

### 29.8 `tests/unit/goals.spec.ts`

Tests:

1. `firstHarvest` completes after collecting required resources.
2. `firstTrades` completes after selling required specific resources.
3. `firstTrades` unlocks museum.
4. `cozyHome` completes after 5 home furniture placed.
5. `cozyHome` progress decreases if furniture removed before completion.
6. Completed `cozyHome` does not uncomplete after removal.
7. `openMuseum` completes after 3 display cases and 3 specimens.
8. `fullCollection` completes after all 9 unlocked.
9. `curatorsSeal` completes only when all final requirements true.
10. Final completion remains complete after removing furniture.

### 29.9 `tests/unit/furniture.spec.ts`

Tests:

1. New furniture refund is `100%`.
2. Previously placed refund is `50%`, rounded down.
3. Minimum refund is `1`.
4. Removing placed furniture returns to build inventory.
5. Removing display case unassigns specimens.
6. Selling display case removes unique ownership.
7. Unique display case cannot be bought while owned.
8. Unique display case can be bought after sold.

### 29.10 `tests/unit/save.spec.ts`

Tests:

1. Serialize then deserialize preserves player state.
2. Preserves inventory.
3. Preserves shop supply and cumulative sales.
4. Preserves placed furniture.
5. Preserves display slot assignments.
6. Preserves goal completion.
7. Corrupt JSON returns null.
8. Version mismatch returns null.

### 29.11 `tests/unit/assetManifest.spec.ts`

Tests:

1. Manifest includes all terrain keys.
2. Includes all node state keys.
3. Includes all furniture keys.
4. Includes all icon keys.
5. Includes all music/SFX files referenced by audio content.

This test validates manifest keys, not necessarily filesystem files.

---

## 30. Required Integration Tests

### 30.1 `tests/integration/worldGenerator.spec.ts`

Tests:

1. Generated world uses seed `42` deterministically.
2. Exterior width/height is `120x120`.
3. Perimeter is solid.
4. Home interior size is `10x8`.
5. Museum interior size is `12x10`.
6. Home door tile is `DOOR_INT` at `(5,7)`.
7. Museum door tile is `DOOR_INT` at `(6,9)`.
8. Node quotas match content:
   - Sweet berry `30`
   - Moon berry `15`
   - Ember berry `5`
   - Copper ore `25`
   - Silver ore `12`
   - Crystal shard `4`
   - Minnow `15`
   - Trout `8`
   - Moonfish `3`
9. Berry nodes are in berry grove mask.
10. Ore nodes are in ore ridge mask.
11. Fish spots are on water.
12. No node is on path.
13. No node is on perimeter.
14. No node is within `2` tiles of exterior doors.
15. Ember berries are in northern berry submask.
16. Crystal shards are in eastern ore submask.
17. Moonfish are in deep south water submask.

### 30.2 `tests/integration/movement.spec.ts`

Tests:

1. Player moves right with `D`.
2. Player moves left with `A`.
3. Player moves up with `W`.
4. Player moves down with `S`.
5. Diagonal movement is normalized.
6. Water movement speed is `3 tiles/sec`.
7. Grass movement speed is `6 tiles/sec`.
8. Player cannot enter perimeter.
9. Player cannot enter solid building tiles.
10. Player can walk on path.
11. Player can walk on water.

### 30.3 `tests/integration/tradeFlow.spec.ts`

Tests:

1. Collect sweet berry.
2. Sell to Moss.
3. Coins increase by current price.
4. Inventory decreases.
5. Shop cumulative sold increases.
6. Supply increases.
7. Selling enough berries unlocks tier 2 berry shop.
8. Selling 5 sweet berries, 5 copper ore, and 5 minnow completes `firstTrades`.
9. Museum unlocks after `firstTrades`.

### 30.4 `tests/integration/buildFlow.spec.ts`

Tests:

1. Buy berry planter.
2. Enter home.
3. Enter build mode.
4. Place planter on valid tile.
5. Planter is removed from build inventory.
6. Planter appears in placed list.
7. Home score increases.
8. Placed furniture is solid.
9. Player cannot walk through placed furniture.
10. Remove furniture returns it to build inventory.
11. Reselling previously placed furniture gives `50%`.

### 30.5 `tests/integration/museumFlow.spec.ts`

Tests:

1. Museum is locked before `firstTrades`.
2. Museum door cannot be entered while locked.
3. Museum can be entered after unlock.
4. Display case cannot be placed in home.
5. Display case can be placed in museum.
6. Exhibit slots are created for display case.
7. Specimen can be assigned.
8. Specimen cannot be assigned twice.
9. Museum score increases when specimen assigned.
10. Removing display case unassigns specimens.
11. Selling display case unassigns specimens.

---

## 31. End-to-End Playable Tests

### 31.1 `tests/e2e/fullPlaythrough.spec.ts`

This test proves the game is complete and playable from new game to final completion.

Use `GameHarness` with seed `42`.

Script:

1. Start harness.
2. Call `newGame()`.
3. Assert starting state:
   - Coins `25`.
   - Museum locked.
   - All goals incomplete.
   - Inventory empty.
4. Complete First Harvest:
   - Collect 1 sweet berry.
   - Collect 1 copper ore.
   - Collect 1 minnow.
   - Assert goal complete.
   - Assert coins increased by `10`.
5. Complete First Trades:
   - Sell 5 sweet berries.
   - Sell 5 copper ore.
   - Sell 5 minnow.
   - Assert goal complete.
   - Assert museum unlocked.
   - Assert all three shops tier 2.
6. Complete Full Collection:
   - Collect all 9 resource types.
   - Assert all specimens unlocked.
   - Assert goal complete.
7. Reach 25 category sales:
   - Collect and sell until:
     - Berry category sales `>= 25`
     - Ore category sales `>= 25`
     - Fish category sales `>= 25`
   - Assert all shops tier 3.
8. Buy museum furniture:
   - Buy:
     - `small_display_case`
     - `pedestal`
     - `crystal_display_case`
     - `moon_display_case`
     - At least 8 decorative furniture pieces.
   - Assert enough coins by collecting/selling if necessary.
9. Place 12 furniture pieces in museum:
   - Use `placeInBuilding("museum", 12)`.
   - Assert all placed furniture is valid.
   - Assert door path still exists.
10. Assign all 9 specimens:
   - Use `assignAllSpecimens()`.
   - Assert assigned count is `9`.
11. Assert `curatorsSeal` complete.
12. Assert completion event emitted.
13. Assert `completionShown` is true.
14. Save and load:
   - Serialize state.
   - Create new harness.
   - Load save.
   - Assert all goals still complete.
   - Assert museum score preserved.
   - Assert placed furniture preserved.

### 31.2 `tests/e2e/postCompletion.spec.ts`

This test proves the game remains playable after completion.

Starting from completed state:

1. Sell 1 sweet berry.
2. Coins change correctly.
3. Supply meter updates.
4. Buy a decorative furniture piece.
5. Place it in home.
6. Remove it.
7. Resell it.
8. Assign/unassign a museum specimen.
9. Move player around exterior.
10. Enter and exit home.
11. Enter and exit museum.
12. Assert no errors and no softlocked UI.

---

## 32. Required Playability Smoke Test

Add to full playthrough or as separate test:

1. From title, start new game.
2. Move player with input.
3. Target a sweet berry node.
4. Hold interact until pick complete.
5. Inventory contains sweet berry.
6. Open ledger.
7. Close ledger.
8. Sell berry to Moss.
9. Coins increase.
10. Open shop.
11. Close shop.
12. Enter home.
13. Exit home.
14. Toggle build mode.
15. Exit build mode.
16. Save game.
17. Load save.
18. State matches.

This smoke test validates basic player controls and UI wiring.

---

## 33. Test Commands

The following commands must pass:

```bash
npm test
npm run build
```

`npm run dev` should start the browser game.

`npm run preview` should serve the built game.

The full playthrough test should complete in under `10` real seconds because it uses deterministic clock advancement, not real-time waiting.

---

## 34. Definition of Done

The engineering handoff is complete when:

1. All required files exist.
2. `npm test` passes.
3. `npm run build` passes.
4. The game boots to title screen.
5. New game starts with correct starting state.
6. Player can move, gather, sell, buy, place furniture, and curate museum.
7. Full playthrough test completes Curator’s Seal.
8. Save/load preserves meaningful state.
9. Museum is locked before First Trades and unlocked after.
10. Furniture placement cannot create a softlock.
11. Missing assets do not crash the game.
12. Audio initializes after user gesture.
13. Reduce Motion and High Contrast settings affect UI/world presentation.
14. No production console errors remain in normal play.

---

## 35. Important Implementation Decisions

### 35.1 Fixed Timestep

Why:

Timers for fishing, respawn, supply recovery, and movement must be deterministic. Fixed timestep makes tests stable and gameplay consistent across refresh rates.

### 35.2 Pure Simulation Plus DOM UI

Why:

The game logic can be tested without canvas or DOM. DOM UI is simpler for shop text, buttons, accessibility, and ledger readability.

### 35.3 Seeded World Generator

Why:

The world must be reproducible for tests and consistent between sessions. Quota-based placement guarantees required resource counts while still looking organic.

### 35.4 Partial Berry Collection

Why:

This resolves conflicting gameplay text. It avoids destroying berries when inventory is tight and keeps the player able to act when at least one unit fits.

### 35.5 Interior Zoom 2

Why:

Interiors are smaller than the viewport. A fixed 2x zoom keeps furniture placement readable without dynamic camera complexity.

### 35.6 4-Direction Path Check

Why:

Placement validation only needs to prevent softlocks. 4-direction BFS is simple, conservative, and easy to test.

### 35.7 Event Bus

Why:

Goals, audio, UI, effects, and save systems all react to the same events. This prevents systems from directly depending on each other.

### 35.8 Save on Autosave and Unload

Why:

Saving on every coin sale is unnecessary and can be expensive. A 5-second autosave plus unload save meets the browser close requirement.

### 35.9 No Dynamic Lighting

Why:

Visual design already cuts dynamic lighting. Fixed readable furniture appearance keeps placement simple and performance stable.

---

## 36. Cut List

Do not add:

- Multiplayer.
- Networking.
- Cloud save.
- Multiple save slots.
- Procedural world beyond the seeded quota generator.
- Fast travel.
- Combat.
- Health.
- Inventory weight.
- Manual stack splitting.
- Resource dropping.
- Crafting.
- Day/night.
- Weather.
- Dynamic lighting.
- Screen shake.
- Full-screen flashes.
- Complex particles.
- Custom font loading.
- Accessibility options beyond reduce motion, high contrast, and audio volumes.
- Separate `I` inventory screen.
- In-game settings menu beyond title screen settings.
- Minimap resource node display.
- Dynamic interior zoom.
- ECS.
- Physics engine.
- External UI framework.
- Audio synthesis in production.

Why:

The core fantasy is collect, sell, decorate, curate. Anything that adds movement, failure, or visual noise without serving that loop should be cut.

---

## 37. Final Integration Rule

The integrating agent should make decisions using only this document.

If a behavior is not specified here, choose the simplest option that:

- Preserves determinism.
- Preserves save integrity.
- Preserves no-fail-state design.
- Preserves readable top-down presentation.
- Can be validated by the test harness.

If a feature is optional and not required by `gameplay.md`, `visual.md`, or this document, cut it.