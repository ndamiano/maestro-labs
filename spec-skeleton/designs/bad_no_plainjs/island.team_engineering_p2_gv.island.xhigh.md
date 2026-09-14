# engineering.md

## 0. Integration Purpose

This document defines the **engineering architecture**, **file layout**, **core algorithms**, **test harness**, and **acceptance tests** for *Island of the Hidden Hoard*.

The integrator should treat this file as the authoritative source for:

- which source files should exist,
- how the simulation is structured,
- how level data is loaded/validated/generated,
- how gameplay state is represented,
- how tests prove the game is complete and playable,
- how rendering, audio, and input are decoupled from the simulation.

If this document conflicts with `gameplay.md`, gameplay constants and rules win.  
If this document conflicts with `visual.md`, visual presentation constants win.

Important engineering priority:

1. The simulation must be **deterministic** and **testable without a browser**.
2. The level must be **validated** so the game cannot ship in an uncompletable state.
3. Rendering and audio are presentation-only subscribers to game state.
4. The code should be small enough for a three-person browser game, but separated cleanly enough to test each system independently.

---

## 1. Technology Choice

Use:

- **Browser**
- **Modern JavaScript ES modules**
- **Canvas 2D** for world and map rendering
- **DOM** for HUD, start screen, end screen, banners, and buttons
- **Web Audio API** for audio
- **Vite** for dev/build
- **Vitest** for tests
- **No game engine**
- **No external runtime library**

Why:

- The game is tile-based 2.5D, not 3D. Canvas 2D is sufficient.
- A browser open-world game with 256x256 tiles does not need an engine.
- DOM UI is better for readable HUD text, accessible buttons, and lower canvas draw cost.
- Plain ES modules make the simulation testable in Node without DOM/canvas.
- Vitest can run the same source modules used by the browser.
- Vite gives a simple dev/build pipeline without extra complexity.

The core simulation must not require:

- `document`
- `canvas`
- `window`
- `AudioContext`
- `Math.random()` in gameplay-critical logic

Why:

- This enables headless tests and deterministic playthrough validation.

---

## 2. File Tree

These files should exist.

```text
/
├─ index.html
├─ package.json
├─ vite.config.mjs
├─ public/
│  └─ assets/
│     └─ audio/
│        └─ *.ogg or *.mp3
├─ src/
│  ├─ main.js
│  ├─ style.css
│  ├─ config.js
│  ├─ rng.js
│  ├─ eventBus.js
│  ├─ clock.js
│  ├─ state.js
│  ├─ game.js
│  ├─ input.js
│  │
│  ├─ level/
│  │  ├─ level.js
│  │  ├─ canonicalLevel.js
│  │  ├─ levelValidator.js
│  │  └─ seedVariation.js
│  │
│  ├─ systems/
│  │  ├─ tide.js
│  │  ├─ terrain.js
│  │  ├─ movement.js
│  │  ├─ stamina.js
│  │  ├─ safeDisplacement.js
│  │  ├─ fog.js
│  │  ├─ landmarks.js
│  │  ├─ interaction.js
│  │  ├─ clues.js
│  │  ├─ coins.js
│  │  ├─ vault.js
│  │  └─ progression.js
│  │
│  ├─ render/
│  │  ├─ renderer.js
│  │  ├─ nullRenderer.js
│  │  ├─ camera.js
│  │  ├─ iso.js
│  │  ├─ terrainCache.js
│  │  ├─ entities.js
│  │  ├─ mapRenderer.js
│  │  ├─ hud.js
│  │  └─ screens.js
│  │
│  └─ audio/
│     ├─ audio.js
│     ├─ nullAudio.js
│     └─ synth.js
│
└─ test/
   ├─ setup.js
   ├─ harness/
   │  ├─ headlessGame.js
   │  ├─ bot.js
   │  ├─ aStar.js
   │  └─ helpers.js
   ├─ fixtures/
   │  ├─ smallLevel.json
   │  └─ canonicalSeed.json
   ├─ unit/
   │  ├─ config.test.js
   │  ├─ tide.test.js
   │  ├─ terrain.test.js
   │  ├─ movement.test.js
   │  ├─ stamina.test.js
   │  ├─ safeDisplacement.test.js
   │  ├─ fog.test.js
   │  ├─ landmarks.test.js
   │  ├─ interaction.test.js
   │  ├─ clues.test.js
   │  ├─ coins.test.js
   │  ├─ vault.test.js
   │  ├─ levelValidator.test.js
   │  └─ canonicalLevel.test.js
   ├─ integration/
   │  ├─ startup.test.js
   │  ├─ keyCollection.test.js
   │  ├─ vaultCompletion.test.js
   │  └─ playthrough.test.js
   └─ performance/
      └─ culling.test.js
```

Notes:

- `tools/generate-level.mjs` is optional and can be added later if an authored level file needs to be produced externally.
- The production game should not depend on test files.
- `src/` must not import from `test/`.
- Test harness may import from `src/`.

---

## 3. Public API

### 3.1 `src/main.js`

Responsibility:

- Create the game.
- Create DOM UI.
- Create canvas renderer.
- Create audio manager.
- Initialize audio on user gesture.
- Start the browser loop.
- Handle start screen and restart.

Expected shape:

```js
import { createGame } from "./game.js";
import { CanvasRenderer } from "./render/renderer.js";
import { Audio } from "./audio/audio.js";
import { HUD } from "./render/hud.js";
import { Screens } from "./render/screens.js";

const container = document.querySelector("#game");
const canvas = document.querySelector("#world-canvas");

const audio = new Audio();
const renderer = new CanvasRenderer(canvas);
const hud = new HUD(container);
const screens = new Screens(container);

const game = createGame({
  level: buildDefaultLevel(),
  renderer,
  audio,
  hud,
  screens,
});

game.start();
```

Why `createGame` instead of exporting a singleton:

- Easier to create multiple games in tests.
- Easier to dispose listeners and audio.
- Easier to restart.

---

### 3.2 `createGame(options)`

`src/game.js` exports:

```js
export function createGame(options) {
  // returns Game instance
}
```

Options:

```js
{
  level: Level,
  renderer: Renderer,
  audio: AudioManager,
  hud: HUD,
  screens: Screens,
  input: Input,
  seed: number,
  fixedDt: number,       // default 1/60
  maxFrameDt: number,    // default 0.25
}
```

The returned `Game` object exposes:

```js
{
  state,
  level,
  events,
  input,
  clock,
  start(),
  tick(dt),
  restart(),
  dispose(),
  debug,
}
```

`game.state` is the single mutable gameplay state.  
`game.level` is immutable after creation.  
`game.events` is an event bus.  
`game.debug` is only for tests/devtools.

---

### 3.3 `createHeadlessGame(options)`

This should exist in `test/harness/headlessGame.js`, not necessarily in production `src/`.

```js
export function createHeadlessGame({ level, seed = 1, fixedDt = 1/60 }) {
  return createGame({
    level,
    renderer: new NullRenderer(),
    audio: new NullAudio(),
    hud: new NullHUD(),
    screens: new NullScreens(),
    input: new TestInput(),
    seed,
    fixedDt,
  });
}
```

Why:

- The same `Game` class is used in browser and tests.
- Headless tests can run the full simulation without DOM/canvas/audio.

---

## 4. Central Constants

`src/config.js` is the only place for gameplay numbers.

Do not scatter constants through systems.

Minimum required constants:

```js
export const CONFIG = {
  WORLD: {
    width: 256,
    height: 256,
    oceanBorder: 8,
    maxElevation: 5,
  },

  TIDE: {
    period: 120,
    minLevel: 0,
    maxLevel: 2,
    lowThreshold: 0.7,
    highThreshold: 1.3,
    passableDepth: 1.0,
    warningSeconds: 10,
  },

  MOVEMENT: {
    walkSpeed: 3.0,
    runSpeed: 5.0,
    swimSpeed: 2.0,
    lowStaminaSwimSpeed: 1.5,
    maxClimb: 1,
    maxSubstep: 0.25,
  },

  STAMINA: {
    max: 100,
    runDrain: 12,
    swimDrain: 10,
    regen: 20,
  },

  MAP: {
    revealRadius: 10,
    landmarkVisibleDistance: 24,
    cacheVisibleDistance: 8,
    huntAreaRadius: 24,
    clueRingWidth: 6,
    mapCanvasSize: 512,
    mapTileScale: 2,
  },

  INTERACTION: {
    radius: 1.5,
    channelCancelOnMove: true,
    channelCancelOnMap: true,
  },

  SAFE: {
    displacementRadius: 16,
  },

  COINS: {
    perCache: 10,
    perSector: 8,
    sectorCount: 5,
    vault: 70,
    total: 160,
  },

  VAULT: {
    channelTime: 1.0,
    x: 208,
    y: 192,
    elevation: 0,
  },
};
```

Why:

- Tests can assert constants.
- Designers can tune without hunting through systems.
- The integrator can change one table if gameplay numbers are corrected.

---

## 5. State Shape

`src/state.js` creates the initial state.

The simulation owns this object.

Renderer, HUD, and audio read from it.

```js
export function createState(level) {
  return {
    screen: "start",
    progression: "START",
    time: 0,

    tide: {
      time: 0,
      waterLevel: 0,
      state: "LOW",
      secondsToThreshold: 0,
      activeWarning: null,
    },

    player: {
      x: level.start.x + 0.5,
      y: level.start.y + 0.5,
      tileX: level.start.x,
      tileY: level.start.y,
      elevation: level.getElevation(level.start.x, level.start.y),
      depth: 0,
      speed: 0,
      moving: false,
      running: false,
      inWater: false,
      facing: { x: 0, y: 1 },
      stamina: 100,
      lastHighSafeTile: null,
    },

    keys: {
      totalCollected: 0,
      geometricCollected: 0,
      collected: [false, false, false, false, false],
    },

    coins: {
      collected: 0,
      totalPossible: CONFIG.COINS.total,
      rank: "Beachcomber",
    },

    vault: {
      markerRevealed: false,
      unlocked: false,
      completed: false,
      state: "LOCKED",
      channel: null,
    },

    caches: level.caches.map(cache => ({
      ...cache,
      collected: false,
      open: false,
      sealed: cache.keyId > 1,
      channel: null,
    })),

    coinsList: level.coins.map(coin => ({
      ...coin,
      collected: false,
    })),

    landmarks: level.landmarks.map(landmark => ({
      ...landmark,
      discovered: false,
    })),

    sectors: level.sectors.map(sector => ({
      ...sector,
      discovered: false,
    })),

    huntAreas: level.caches.map(cache => ({
      cacheId: cache.id,
      sectorId: cache.sectorId,
      revealed: false,
    })),

    clues: [],

    fog: {
      revealed: new Uint8Array(level.width * level.height),
      revealedCount: 0,
    },

    prompt: {
      visible: false,
      kind: null,
      text: "",
      channelProgress: 0,
    },

    mapOpen: false,

    stats: {
      time: 0,
      keys: 0,
      coins: 0,
      rank: "Beachcomber",
    },
  };
}
```

Important rules:

- State is mutable, but only through systems and `game.tick()`.
- Renderer and audio do not write state.
- Input writes only to `game.input`, not directly to state.
- `game.state.time` is simulated time, not wall time.

Why simulated time:

- Deterministic tests.
- Tide is a pure function of simulated time.
- End screen time is reproducible.

---

## 6. Event Bus

`src/eventBus.js` implements a tiny synchronous event bus.

```js
export class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(event, handler) {
    if (!this.listeners.has(event)) this.listeners.set(event, []);
    this.listeners.get(event).push(handler);
    return () => this.off(event, handler);
  }

  off(event, handler) {
    const list = this.listeners.get(event);
    if (!list) return;
    const i = list.indexOf(handler);
    if (i >= 0) list.splice(i, 1);
  }

  emit(event, payload) {
    const list = this.listeners.get(event);
    if (!list) return;
    for (const handler of [...list]) handler(payload);
  }

  once(event, handler) {
    const wrap = (payload) => {
      this.off(event, wrap);
      handler(payload);
    };
    return this.on(event, wrap);
  }
}
```

Events are synchronous and emitted in a stable order.

Why:

- Tests can assert event order.
- Audio/HUD subscriptions stay deterministic.

### 6.1 Required Events

Use the gameplay event names, plus a few presentation-support events.

| Event | Payload |
|---|---|
| `game_start` | `{}` |
| `game_complete` | `{ time, keys, coins, rank }` |
| `landmark_discovered` | `{ landmarkId, name }` |
| `sector_discovered` | `{ sectorId, name }` |
| `cache_sealed_prompt` | `{ cacheId, prompt }` |
| `cache_lowtide_prompt` | `{ cacheId, prompt }` |
| `cache_opened` | `{ cacheId }` |
| `key_collected` | `{ keyId }` |
| `geometric_clue_added` | `{ keyId, clue }` |
| `coin_collected` | `{ amount, total }` |
| `hunt_area_revealed` | `{ cacheId, sectorId }` |
| `vault_marker_revealed` | `{}` |
| `vault_unlocked` | `{ keysTotal }` |
| `vault_state_changed` | `{ state }` |
| `vault_opened` | `{}` |
| `tide_warning` | `{ targetState, atTime, seconds }` |
| `tide_state_changed` | `{ state }` |
| `safe_displacement_occurred` | `{ from, to, reason }` |
| `blocked_movement` | `{ reason }` |
| `interaction_started` | `{ targetId }` |
| `interaction_cancelled` | `{ targetId, reason }` |
| `map_opened` | `{}` |
| `map_closed` | `{}` |
| `player_facing_changed` | `{ facing }` |
| `stamina_empty` | `{}` |
| `stamina_full` | `{}` |

Why extra events:

- `interaction_started/cancelled` are needed for audio and HUD feedback.
- `blocked_movement` is needed for the soft blocked-step feedback required by visual design.
- `vault_state_changed` makes vault prompt/audio easier to implement without hardcoding prompt logic in multiple places.

---

## 7. Level System

The level system is responsible for:

- loading authored level data,
- generating a deterministic canonical fallback level,
- applying seed variation,
- validating that the level is completable.

Important decision:

The **canonical level is not final art**.  
It is a deterministic functional level used to prove the game is playable and to support tests.

If an authored level file exists, it should replace the canonical level.

Why:

- `gameplay.md` gives sector positions and key positions, but not a full tile heightmap.
- Engineering must still produce a runnable, testable game.
- A validated canonical level guarantees the integrator can test completion.
- A later authored level can be dropped in without changing simulation systems.

---

## 8. Level Data Schema

A level is a plain JSON-compatible object.

```js
{
  version: 1,
  width: 256,
  height: 256,
  seed: 12345,

  start: { x: 32, y: 220 },
  vault: { x: 208, y: 192, elevation: 0 },

  // One string per row. Each character is elevation 0-5 or ocean.
  // O = ocean/impassable
  tiles: [
    "OOOOOOOO...",
    "OO111111..."
  ],

  sectors: [
    {
      id: "driftwood_cove",
      name: "Driftwood Cove",
      bounds: { x0: 16, y0: 190, x1: 70, y1: 240 },
      landmarkId: "shipwreck",
      highSafeTile: { x: 40, y: 210 }
    }
  ],

  landmarks: [
    {
      id: "shipwreck",
      name: "Shipwreck",
      sectorId: "driftwood_cove",
      x: 40,
      y: 210,
      elevation: 1,
      glyph: "anchor"
    }
  ],

  caches: [
    {
      id: "cache_key1",
      keyId: 1,
      sectorId: "driftwood_cove",
      x: 45,
      y: 208,
      elevation: 1,
      interaction: "open_barrel",
      channelTime: 0.5,
      requiresLowTide: false,
      note: "The treasure is 169 paces from the Shipwreck.",
      clue: { landmarkId: "shipwreck", distance: 169 }
    }
  ],

  coins: [
    { id: "coin_1", x: 41, y: 207, lowTideOnly: false }
  ],

  clues: [
    { keyId: 1, landmarkId: "shipwreck", distance: 169 }
  ]
}
```

Tile encoding rules:

- Each row is a string of length `width`.
- Each character represents one tile.
- `O` = ocean/impassable.
- `0` through `5` = land elevation.
- Any other character is invalid.

Why string rows:

- Easy to inspect.
- Compact enough for 256x256.
- Easy to generate programmatically.
- Easy to diff.

Level accessor helpers:

```js
level.isLand(x, y)
level.isOcean(x, y)
level.getElevation(x, y)
level.getTile(x, y)
level.getCacheById(id)
level.getLandmarkById(id)
level.getCacheByKeyId(keyId)
level.getIndex(x, y)
level.toIndex(x, y)
```

Out-of-bounds tiles are ocean/impassable.

---

## 9. Canonical Level Builder

`src/level/canonicalLevel.js` builds a deterministic functional island from `CONFIG` and gameplay sector data.

This is the fallback used when no authored level file is supplied.

It is not intended to be the final artist-directed level.

Its purpose is to produce a valid, completable, testable island that satisfies the core gameplay constraints.

### 9.1 Canonical Builder Algorithm

```text
buildCanonicalLevel(seed):
  1. Create a 256x256 grid.
  2. Fill outer 8 tiles with ocean.
  3. Fill all remaining tiles with land elevation 1.
  4. Create a coastline ring at elevation 0 near the outer border.
  5. Apply sector-specific functional features:
     - Gull Flats: low-tide elev0 pocket around Key 2.
     - Vault Point: elev0 cave floor around vault.
     - Landmarks: local elevation ramps matching required landmark elevation.
  6. Enforce critical tile elevations:
     - start tile elevation 1
     - vault tile elevation 0
     - Key 1 cache elevation 1
     - Key 2 cache elevation 0
     - other caches elevation 1 unless otherwise required
  7. Ensure critical interactables have adjacent passable tiles at the required tide.
  8. Apply seed variation.
  9. Validate.
  10. If validation fails, return the ultra-safe fallback level.
```

### 9.2 Canonical Land Mask

The canonical level uses a simple full square island inside the ocean border:

```text
ocean: x < 8 or x >= 248 or y < 8 or y >= 248
land: everything else
```

Why:

- Guarantees global connectivity.
- Avoids accidental dead ends.
- Makes high-tide validation simple.
- Is enough to prove the game is playable.
- Can later be replaced by an authored level file.

This is an engineering fallback, not a level design decision.

---

### 9.3 Canonical Elevation

Base:

```text
all land = elevation 1
coast ring = elevation 0
```

Then apply local ramps for landmarks.

For a landmark at `(lx, ly)` with required elevation `E`:

```text
for each tile (x, y) where manhattanDistance((x,y), (lx,ly)) <= E:
  elevation = max(currentElevation, E - distance)
```

Example:

Landmark elevation 4:

```text
center: 4
distance 1: 3
distance 2: 2
distance 3: 1
```

Why:

- Guarantees a walkable ramp to landmarks with elevation differences of at most 1.
- Avoids cliffs blocking discovery or pathing in the canonical level.

Critical low-tide areas:

```text
Key 2 cache tile and nearby Gull Flats shelf: elevation 0
Vault tile and nearby cave floor: elevation 0
```

Why:

- Matches low-tide gameplay.
- Makes these tiles passable at low tide and deep at high tide.

---

### 9.4 Seed Variation

Seed variation is limited to minor content, as required by `gameplay.md`.

`src/level/seedVariation.js` uses `src/rng.js`.

Rules:

- Use a deterministic RNG.
- Do not move landmarks.
- Do not move vault.
- Do not move start.
- Do not change clue distances.
- Do not change sector bounds.
- Only vary:
  - minor cache offsets for caches 2 through 5,
  - scattered coin positions.

Cache offset rules:

```text
for cache in [2,3,4,5]:
  candidate = defaultPosition + random offset within Chebyshev radius 3
  if candidate is ocean:
    use default
  if candidate is not passable at low tide:
    use default
  if cache.requiresLowTide:
    candidate elevation must be 0
    if not, set candidate elevation to 0 only if it is land and not a critical tile
  if candidate is too close to another cache:
    use default
```

Coin placement rules:

```text
for each of 5 sectors:
  place 8 coins on land tiles inside sector bounds
  coin tile must be passable at low tide
  coin tile must not be ocean
  coin tile must not be within 2 tiles of another scattered coin
  coin tile must not be on a cache, landmark, start, or vault
  if a coin is on elevation 0, mark lowTideOnly = true
```

Why:

- Preserves guaranteed progression.
- Allows minor replay variation.
- Keeps the critical path deterministic enough for tests.

---

## 10. Level Validation

`src/level/levelValidator.js` validates a level before it is used.

Validation is mandatory.

If validation fails:

- Log a detailed warning.
- Replace the level with the ultra-safe fallback.
- The fallback must always be completable.

Why:

- An open-world browser game must not start in a state where a key or vault is unreachable.
- Tests should fail loudly if a level file breaks progression.

### 10.1 Validation Checks

#### A. Structural

- Width/height match config or provided size.
- Tile rows have correct length.
- All tile values are valid.
- Outer 8 tiles are ocean in canonical/full-size levels.
- Start is land.
- Start elevation is at least 1.
- Vault is land.
- Vault elevation is 0.
- All caches are inside the world.
- All caches are land.
- All landmarks are inside the world.
- All landmarks are land.

#### B. Low Tide Reachability

Use `waterLevel = 0`.

Passability:

```text
depth = max(0, 0 - elevation) = 0
all land passable
```

Check:

- Start can reach Key 1 cache.
- Start can reach all caches.
- Start can reach vault.
- Movement obeys elevation difference rule.

Why:

- Low tide is the most permissive tide state.
- If a tile is unreachable at low tide, it is fundamentally blocked by cliffs or ocean.

#### C. High Tide Reachability

Use `waterLevel = 2`.

Passability:

```text
elevation 0: depth 2, impassable
elevation 1: depth 1, passable
elevation 2+: depth 0, passable
```

Check:

- Start can reach each sector’s `highSafeTile`.
- Each sector’s `highSafeTile` must have elevation at least 1.
- The player cannot be stranded in a sector.

For the canonical level, this can be made strict:

```text
all land tiles with elevation >= 1 must be reachable from start at high tide
```

Why:

- Ensures high tide compresses the island but does not trap the player.
- Matches the safe-displacement requirement.

#### D. Clue Validation

For all four geometric clues:

```text
for each tile in island:
  inside = true
  for each clue:
    d = distance(tile, clue.landmark)
    if abs(d - clue.distance) > 6:
      inside = false
  if inside:
    overlapTiles.push(tile)
```

Require:

- Vault tile is in `overlapTiles`.
- `overlapTiles.length < 400`.

If a clue distance is invalid:

- Correct it to `round(distance(landmark, vault))`.
- Revalidate.

Why:

- Guarantees the visual ring puzzle resolves to the actual vault.
- Prevents a broken clue set from making the game uncompletable.

#### E. Coin Validation

Require:

- Total possible coins = 160.
- 5 caches x 10 coins = 50.
- 5 sectors x 8 scattered coins = 40.
- Vault = 70.
- Scattered coins are not on ocean.
- Scattered coins are not within 2 tiles of another scattered coin.
- Scattered coins are not on critical interactables.

Why:

- Rank system depends on 160 maximum coins.
- Prevents unfair coin placement.

#### F. Safe Tile Validation

Require:

- Start elevation >= 1.
- At least one `lastHighSafeTile` exists from start.
- For each sector, `highSafeTile` elevation >= 1.

Why:

- Safe displacement fallback depends on a high-tide-safe tile.

---

## 11. Core Simulation Loop

`game.tick(dt)` is the only public update entry point.

Browser loop:

```js
let last = performance.now();

function frame(now) {
  const dt = (now - last) / 1000;
  last = now;
  game.tick(dt);
  requestAnimationFrame(frame);
}

requestAnimationFrame(frame);
```

Internal fixed timestep:

```js
const FIXED_DT = 1 / 60;
const MAX_FRAME_DT = 0.25;

tick(dt) {
  dt = Math.min(Math.max(dt, 0), MAX_FRAME_DT);
  this.accumulator += dt;

  while (this.accumulator >= FIXED_DT) {
    this.update(FIXED_DT);
    this.accumulator -= FIXED_DT;
  }

  this.renderer.render(this.state, this.level, this.view);
}
```

Why fixed timestep:

- Movement, stamina, tide, and channel times become deterministic.
- Tests can simulate exact seconds.
- Variable frame rates do not change gameplay outcome.

### 11.1 Update Order

Each fixed step runs in this order:

```text
1. If screen !== "playing", return.
2. Update tide.
3. Update player tile/depth.
4. If current tile is impassable, run safe displacement.
5. Update movement and stamina.
6. Update player tile again if movement changed tile.
7. Update lastHighSafeTile.
8. Update fog reveal if player tile changed.
9. Update interaction/channel.
10. Update coins.
11. Update landmarks.
12. Update clues/vault marker.
13. Update progression state.
14. Emit state-change events.
```

Why this order:

- Tide is environmental; it should be resolved before player movement.
- Safe displacement happens before input movement so the player is not stranded at the start of a tick.
- Fog and landmarks update after movement.
- Interaction depends on final player position.

---

## 12. Tide System

`src/systems/tide.js`

Tide is global and continuous.

Formula from `gameplay.md`:

```js
waterLevel = 1 - Math.cos(TAU * time / CONFIG.TIDE.period);
```

Where:

```text
time = seconds since game start
period = 120
waterLevel range = 0 to 2
low tide at t = 0
high tide at t = 60
low tide again at t = 120
```

### 12.1 Tide State

```js
if (waterLevel < 0.7) state = "LOW";
else if (waterLevel < 1.3) state = "RISING";
else state = "HIGH";
```

### 12.2 Warnings

The game should warn 10 seconds before crossing into a new tide state.

Required warnings:

- Before Rising.
- Before High.

Recommended additional warning:

- Before Low.

Why include low warning:

- The final vault requires low tide.
- Low-tide shelves and coins become reachable.
- Visual design includes a low tide warning example.
- It improves planning without adding panic.

Threshold crossing times can be precomputed.

```text
lowRisingTime = (120 / TAU) * acos(1 - 0.7)
lowFallingTime = 120 - lowRisingTime

highRisingTime = (120 / TAU) * acos(1 - 1.3)
highFallingTime = 120 - highRisingTime
```

For any current time `t`:

```text
phase = t mod 120
nextWarning = min positive time until a threshold crossing - 10
if nextWarning >= 0 and warning not already emitted:
  emit tide_warning
```

State change:

```text
if newState !== oldState:
  emit tide_state_changed
```

Why:

- Exact threshold logic is easy to test.
- Warnings do not depend on frame rate.

---

## 13. Terrain and Passability

`src/systems/terrain.js`

Do not recompute passability for all 65,536 tiles every frame.

Compute depth and passability on demand.

```js
function depthAt(level, x, y, waterLevel) {
  if (!level.isLand(x, y)) return Infinity;
  const elevation = level.getElevation(x, y);
  return Math.max(0, waterLevel - elevation);
}

function isTilePassable(level, x, y, waterLevel) {
  const depth = depthAt(level, x, y, waterLevel);
  return depth <= CONFIG.TIDE.passableDepth;
}

function canEnterTile(level, fromX, fromY, toX, toY, waterLevel) {
  if (!level.isLand(toX, toY)) return false;
  if (!isTilePassable(level, fromX, fromY, waterLevel)) return false;
  if (!isTilePassable(level, toX, toY, waterLevel)) return false;

  const fromElevation = level.getElevation(fromX, fromY);
  const toElevation = level.getElevation(toX, toY);

  return Math.abs(fromElevation - toElevation) <= CONFIG.MOVEMENT.maxClimb;
}
```

Why on-demand:

- The player only needs current/target tile passability most of the time.
- Rendering only needs visible tiles.
- Safe displacement only needs local search.
- Pathfinding can use the same functions.
- This scales better than maintaining a full mutable passability grid every frame.

---

## 14. Movement

`src/systems/movement.js`

Player position is float in tile units.

Tile coordinates:

- Tile `(x, y)` occupies `[x, x+1]` by `[y, y+1]`.
- Tile center is `(x + 0.5, y + 0.5)`.
- Current tile is `floor(player.x), floor(player.y)`.

### 14.1 Movement Speed

Each tick:

```text
depth = depthAt(playerTile)
inWater = depth > 0

if depth > 1:
  speed = 0
  player cannot move

else if depth == 0:
  if input.run and stamina > 0:
    speed = runSpeed
    draining = runDrain
  else:
    speed = walkSpeed
    draining = 0

else:
  if stamina > 0:
    speed = swimSpeed
  else:
    speed = lowStaminaSwimSpeed
  draining = swimDrain
```

Rules:

- Running only on dry land.
- No running in water.
- Stamina 0 still allows walking/swimming slowly.
- No death.

### 14.2 Movement Substeps

Use substeps to prevent crossing multiple tiles in one update.

```js
const MAX_SUBSTEP = 0.25;
let remaining = speed * dt;

while (remaining > 0) {
  const step = Math.min(remaining, MAX_SUBSTEP);
  moveAxisX(dir.x * step);
  moveAxisY(dir.y * step);
  remaining -= step;
}
```

Why axis-separated movement:

- Prevents corner cutting.
- Makes collision clamping simpler.
- Keeps tile-based rules predictable.

### 14.3 Axis Movement

For X movement:

```js
function moveAxisX(delta) {
  const oldX = player.x;
  const oldTileX = Math.floor(oldX);
  const newX = clamp(oldX + delta, 0, level.width);
  const newTileX = Math.floor(newX);

  if (newTileX !== oldTileX) {
    const dir = Math.sign(newTileX - oldTileX);
    const targetX = oldTileX + dir;
    const targetY = player.tileY;

    if (!canEnterTile(level, oldTileX, targetY, targetX, targetY, waterLevel)) {
      if (delta > 0) {
        player.x = (oldTileX + 1) - EPS;
      } else {
        player.x = oldTileX + EPS;
      }
      return;
    }
  }

  player.x = newX;
}
```

Same for Y.

Why clamping:

- The player can hug cliffs and deep water edges without entering them.
- The player does not sink into blocked tiles.

### 14.4 Blocked Movement Feedback

If the player attempts movement but is blocked:

- Emit `blocked_movement` once per blocked attempt.
- Do not spam every frame.
- Use a short cooldown, for example 0.15s.

Why:

- Visual design requires a soft blocked feedback.
- Without cooldown, audio/animation would spam.

---

## 15. Stamina

`src/systems/stamina.js`

Rules:

- Max stamina 100.
- Running drain 12/s.
- Swimming drain 10/s.
- Regen 20/s when not draining.
- Stamina does not kill the player.
- At 0 stamina:
  - running disabled,
  - swim speed becomes 1.5 tiles/s.

Implementation:

```js
if (draining > 0) {
  player.stamina = Math.max(0, player.stamina - draining * dt);
  if (player.stamina === 0) emit stamina_empty
} else {
  player.stamina = Math.min(100, player.stamina + CONFIG.STAMINA.regen * dt);
  if (player.stamina === 100) emit stamina_full
}
```

Why:

- Matches gameplay resource pressure.
- No health/death.

---

## 16. Safe Displacement

`src/systems/safeDisplacement.js`

If the player’s current tile becomes impassable:

1. Search for nearest passable tile within 16 tiles.
2. If found, move player there.
3. If not found, move to `lastHighSafeTile`.
4. If no `lastHighSafeTile`, move to start.
5. Cancel active interaction channel.
6. Do not remove keys, coins, or progress.

### 16.1 Search

Use BFS/grid search by distance, not passability path search.

Why:

- The current tile is already impassable.
- Safe displacement is a rescue teleport, not a normal path.
- The goal is the nearest currently passable tile within radius.

Algorithm:

```text
for radius from 0 to 16:
  for each tile in ring around current tile:
    if tile is in bounds:
      if tile is passable at current water level:
        return tile
return null
```

Tie-breaking:

- Smaller grid distance.
- Then smaller x.
- Then smaller y.

Why deterministic tie-breaking:

- Tests can assert exact displacement result.

### 16.2 `lastHighSafeTile`

Update:

```js
if (level.getElevation(player.tileX, player.tileY) >= 1) {
  player.lastHighSafeTile = { x: player.tileX, y: player.tileY };
}
```

Why elevation >= 1:

- Elevation 1 is passable at high tide.
- Elevation 0 is deep water at high tide.

Start tile must be elevation 1.

---

## 17. Fog of War and Line of Sight

`src/systems/fog.js`

Fog is a `Uint8Array` of size `width * height`.

Reveal happens when the player enters a new tile.

Reveal radius: 10 tiles.

```js
function revealAround(playerTile) {
  const px = playerTile.x;
  const py = playerTile.y;

  for (let dy = -10; dy <= 10; dy++) {
    for (let dx = -10; dx <= 10; dx++) {
      if (dx*dx + dy*dy > 10*10) continue;

      const x = px + dx;
      const y = py + dy;

      if (!level.inBounds(x, y)) continue;

      if (lineOfSight(level, px, py, x, y)) {
        reveal(x, y);
      }
    }
  }
}
```

Line of sight:

```js
function lineOfSight(level, ax, ay, bx, by) {
  const baseElevation = level.getElevation(ax, ay);

  for (let s = 0; s <= 1; s += 0.5) {
    const x = Math.round(ax + (bx - ax) * s);
    const y = Math.round(ay + (by - ay) * s);

    if (!level.inBounds(x, y)) return false;

    if (level.getElevation(x, y) > baseElevation + 1) {
      return false;
    }
  }

  return true;
}
```

Rules:

- Water does not block visibility.
- A tile blocks visibility only if its elevation is greater than player tile elevation + 1.
- Once revealed, a tile remains revealed.

Why:

- Matches gameplay fog rule.
- Simple enough for 256x256.

---

## 18. Landmarks, Sectors, and Hunt Areas

`src/systems/landmarks.js`

Landmarks are discoverable objects.

Every frame:

```js
for each undiscovered landmark:
  if distance(playerPosition, landmarkPosition) <= 24:
    if lineOfSight(playerTile, landmarkTile):
      discover landmark
      emit landmark_discovered
      if landmark has sectorId:
        discover sector
        emit sector_discovered
        maybe reveal hunt area
```

Distance uses continuous player position and landmark tile center.

Landmark tile center:

```text
(x + 0.5, y + 0.5)
```

### 18.1 Hunt Areas

A hunt area is revealed when:

- Key 1 has been collected, and
- the sector’s main landmark has been discovered, and
- the sector’s cache is uncollected.

```js
function maybeRevealHuntArea(cacheId) {
  if (!state.keys.collected[0]) return;

  const cache = state.caches.find(c => c.id === cacheId);
  if (cache.collected) return;

  const landmark = level.getLandmarkById(level.sectorForCache(cacheId).landmarkId);
  if (!landmark.discovered) return;

  reveal hunt area;
  emit hunt_area_revealed;
}
```

Why:

- Matches gameplay guidance without revealing exact cache position.
- Prevents hunt areas before the first key teaches the map.

---

## 19. Caches and Interaction

`src/systems/interaction.js`

There are 5 caches.

Each cache has:

- key ID,
- sector ID,
- position,
- elevation,
- channel time,
- interaction type,
- note,
- clue if geometric,
- `requiresLowTide`.

Key rules:

- Key 1 is always available.
- Keys 2 through 5 are sealed until Key 1 is collected.
- Once opened, a cache remains open.
- Interaction requires proximity.
- Moving cancels channel.
- Opening map cancels channel.
- Safe displacement cancels channel.

### 19.1 Interaction Radius

Use:

```text
INTERACTION_RADIUS = 1.5 tiles
```

Why 1.5:

- Adjacent tile center distance is 1.0.
- 1.5 allows small off-tile positioning but prevents channeling from far away.
- Keeps interaction readable in isometric view.

### 19.2 Prompt Eligibility

Each tick, find the nearest eligible interactable.

Eligible target types:

- Uncollected cache.
- Vault.

A target is in range if:

```text
distance(playerPosition, targetTileCenter) <= 1.5
lineOfSight(playerTile, targetTile)
player tile is passable
```

Prompt logic:

| Target | Condition | Prompt |
|---|---|---|
| Cache 2-5 | Key 1 not collected | `Sealed. Find the first Tide Key.` |
| Low-tide cache | Tile not passable or `requiresLowTide` and not low tide | `Wait for low tide.` |
| Cache | In range and unlocked | `Open cache` / `Pull rope` / `Move column` |
| Vault | Keys < 5 | `Locked. Requires 5/5 Tide Keys.` |
| Vault | Keys 5, not low tide | `Sealed by the tide. Wait for low tide.` |
| Vault | Keys 5, low tide | `Open vault` |

### 19.3 Channel

Channel state:

```js
{
  targetId,
  remaining,
  duration,
}
```

Starting channel:

- Requires `E` or `Enter`.
- Requires eligible target.
- Requires player tile passable.
- For low-tide targets, requires low tide.
- For vault, requires 5 keys and low tide.

Channel update:

```js
if channel active:
  if player moved:
    cancel
  if map open:
    cancel
  if safe displacement occurred:
    cancel
  if target no longer eligible:
    cancel
  if target is vault and tide is not low:
    cancel

  else:
    channel.remaining -= dt
    if channel.remaining <= 0:
      complete channel
```

“Player moved” means:

- Input movement axis is nonzero, or
- Player position changed beyond a tiny epsilon.

Why:

- Matches gameplay rule that moving cancels channel.
- Prevents accidental channel completion while drifting.

### 19.4 Cache Completion

On cache channel complete:

```text
cache.open = true
cache.collected = true
player.stamina unchanged
state.keys.collected[keyId - 1] = true
state.keys.totalCollected += 1
state.coins.collected += 10
emit cache_opened
emit key_collected
if cache.clue exists:
  add clue
  emit geometric_clue_added
```

For Key 5:

- No geometric clue.
- Note says low tide is required for vault.
- Vault unlock state updates after 5 keys.

---

## 20. Clues and Vault Marker

`src/systems/clues.js`

Keys 1 through 4 give geometric clues.

Clue shape:

```js
{
  keyId,
  landmarkId,
  distance
}
```

When a geometric clue is added:

- Store clue.
- Update `state.keys.geometricCollected`.
- If `geometricCollected === 4`:
  - `state.vault.markerRevealed = true`
  - emit `vault_marker_revealed`

Why not manually compute marker from rings at runtime:

- The vault location is fixed.
- Level validation already guarantees the rings resolve to the vault.
- Runtime marker logic should be simple and deterministic.

Clue ring data for rendering:

```text
innerRadius = max(0, distance - 6)
outerRadius = distance + 6
```

Each key uses unique color/dash style from visual design.

---

## 21. Coins

`src/systems/coins.js`

Coins are optional score.

Coin pickup:

```js
for each uncollected coin:
  if distance(playerPosition, coinPosition) <= 0.6:
    if coin tile is not deep water:
      collect coin
```

Use pickup radius 0.6.

Why 0.6:

- Walking over a tile center should collect.
- Slightly off-center still collects.
- Prevents collecting from too far away.

Coin collection:

```text
coin.collected = true
state.coins.collected += 1
update rank
emit coin_collected
```

Rank:

```js
if coins >= 160 rank = "Tide Baron"
else if coins >= 140 rank = "Master Salvager"
else if coins >= 100 rank = "Salvager"
else rank = "Beachcomber"
```

Rules:

- Coins do not regenerate.
- Coins do not affect keys or vault.
- Low-tide coins may be deep at high tide and therefore uncollectable.

---

## 22. Vault

`src/systems/vault.js`

Vault state:

```js
"LOCKED"       // fewer than 5 keys
"SEALED"       // 5 keys, not low tide
"READY"        // 5 keys, low tide
"OPENING"      // channel active
"OPEN"         // completed
```

Vault prompt logic:

| Condition | Prompt |
|---|---|
| Keys < 5 | `Locked. Requires 5/5 Tide Keys.` |
| Keys 5, not low tide | `Sealed by the tide. Wait for low tide.` |
| Keys 5, low tide | `Open vault` |

Channel time:

```text
1.0 second
```

Cancel conditions:

- Player moves.
- Map opens.
- Safe displacement.
- Tide is no longer low.
- Player leaves interaction radius.

On success:

```text
vault.completed = true
coins += 70
state.screen = "complete"
state.progression = "GAME_COMPLETE"
emit vault_opened
emit game_complete
disable input
```

Why vault is a separate system:

- It combines keys, tide, clues, channeling, and completion.
- Tests can validate vault state transitions independently.

---

## 23. Progression State

`src/systems/progression.js`

Derive progression from state rather than storing redundant flags where possible.

```js
function updateProgression(state) {
  if (state.screen === "start") {
    state.progression = "START";
    return;
  }

  if (state.vault.completed) {
    state.progression = "GAME_COMPLETE";
    return;
  }

  if (state.keys.totalCollected === 5) {
    state.progression = "VAULT_READY";
    return;
  }

  if (state.keys.totalCollected === 0) {
    state.progression = "START";
    return;
  }

  state.progression = `FREE_KEYS_${state.keys.totalCollected}_OF_5`;
}
```

Objective text:

| State | Objective |
|---|---|
| Start | `Open the shipwreck barrel.` |
| 1/5 keys | `Find the Tide Keys. 1/5` |
| 2/5 keys | `Find the Tide Keys. 2/5` |
| 3/5 keys | `Find the Tide Keys. 3/5` |
| 4/5 keys | `Find the Tide Keys. 4/5` |
| 5/5 keys | `Open the vault at low tide.` |
| Complete | `Treasure found.` |

Why derived progression:

- Fewer desynchronization bugs.
- Tests can assert progression from keys/vault.

---

## 24. Renderer Architecture

Rendering is presentation-only.

Renderer interface:

```js
class Renderer {
  render(state, level, view) {}
  resize() {}
  dispose() {}
}
```

Browser renderer:

```js
CanvasRenderer
```

Headless renderer:

```js
NullRenderer
```

Why interface:

- Tests can run the full simulation without canvas.
- Browser renderer can be replaced or improved independently.

---

## 25. World Rendering

`src/render/renderer.js`

Use one main canvas for the world.

Render order:

1. Ocean background.
2. Terrain tiles sorted by `x + y`.
3. Terrain side walls.
4. Water overlays.
5. Coins.
6. Caches.
7. Landmarks.
8. Player.
9. World effects.
10. HUD is DOM, not drawn into world canvas.

Why:

- Keeps painter’s algorithm simple for fixed isometric view.
- Entities are sorted by depth.

---

## 26. Isometric Projection

Use visual design constants:

```js
TILE_W = 48
TILE_H = 24
HEIGHT_STEP = 18
```

Projection:

```js
function isoToScreen(tileX, tileY, elevation, camera, view, scale = 1) {
  const sx = (tileX - tileY) * (TILE_W / 2) * scale;
  const sy = (tileX + tileY) * (TILE_H / 2) * scale - elevation * HEIGHT_STEP * scale;

  return {
    x: view.width / 2 + sx - camera.x,
    y: view.height / 2 + 24 + sy - camera.y,
  };
}
```

Camera:

- Follows player.
- No rotation.
- No free zoom.
- Smooth follow.
- Clamped to world bounds.
- Small dead zone to prevent jitter.

Why:

- Matches visual design.
- Fixed isometric camera keeps tide/elevation readable.

---

## 27. Terrain Caching

`src/render/terrainCache.js`

Pre-render terrain tile canvases.

Cache key:

```text
sectorId|elevation|wet|variant
```

Variant:

- 2 or 3 variants per sector for subtle noise.
- Deterministic from tile hash.

Why pre-render:

- Drawing 256x256 terrain procedurally every frame is wasteful.
- Pre-rendered canvases allow fast blitting.
- Water is dynamic, but terrain is static.

Terrain cache memory is small:

```text
6 sectors x 6 elevations x 2 variants = 72 small canvases
```

---

## 28. Terrain Culling

Do not draw the whole 256x256 world every frame.

Compute visible tile bounds from camera and viewport.

Use a margin for elevation:

```text
maxElevationOffset = CONFIG.WORLD.maxElevation * HEIGHT_STEP
tileMargin = 12
```

Approximate visible range:

```text
centerTile = inverseIso(camera)
x0 = center.x - rangeX - tileMargin
x1 = center.x + rangeX + tileMargin
y0 = center.y - rangeY - tileMargin
y1 = center.y + rangeY + tileMargin
```

Then iterate visible tiles only.

Why:

- 256x256 is 65,536 tiles.
- Visible tiles are much fewer.
- This is the main performance win.

Performance target:

- Draw under 3,000 visible tile passes per frame on standard screens.
- No full-screen blur.
- No dynamic lighting.
- No post-processing.

---

## 29. Water Rendering

Water is rendered as a dynamic overlay on visible flooded tiles.

For each visible tile:

```js
depth = max(0, waterLevel - elevation)

if depth <= 0:
  draw dry tile

if depth > 0 and depth <= 1:
  draw shallow water overlay

if depth > 1:
  draw deep water overlay
```

Use alpha:

```text
shallow: ~0.28 to 0.38 alpha
deep:    ~0.65 to 0.75 alpha
```

Add simple ripple using time and tile coordinates.

Why not pre-render all water states:

- Water level is continuous.
- Depth changes every tide tick.
- Alpha overlay is cheap for visible tiles.

---

## 30. Map Renderer

`src/render/mapRenderer.js`

Map is a canvas overlay.

Maximum size:

```text
512 x 512 pixels
1 tile = 2 pixels
```

Map coordinate mapping:

```js
function tileToMap(x, y) {
  return {
    x: x * 2,
    y: y * 2,
  };
}
```

Map layers, in order:

1. Parchment background.
2. Revealed terrain.
3. Unrevealed dark overlay.
4. Current tide water.
5. High-tide flood preview.
6. Sector labels.
7. Hunt areas.
8. Clue rings.
9. Landmarks.
10. Vault marker.
11. Player.
12. Legend.

Performance strategy:

- Static layers redraw only when dirty.
- Current tide water updates at most 10 times/sec unless water level changes significantly.
- Player marker updates every frame while map is open.
- Clue rings redraw only when a clue is added.
- Vault marker redraws only when marker/unlock state changes.

Why:

- The map is central but should not consume unnecessary CPU.
- 512x512 is small, but redrawing every layer every frame is avoidable.

---

## 31. HUD

`src/render/hud.js`

Use DOM for HUD.

Reasons:

- Text readability.
- Accessibility.
- Simpler layout.
- Less canvas draw cost.
- Easier to support small screens.

HUD components:

### Top Left

- Tide dial.
- Stamina bar.
- Key counter.

Tide dial can be a small canvas or SVG/DOM shape.

### Top Right

- Map button.
- Objective text.

### Bottom Right

- Coin counter.

### Bottom Center

- Context prompt.
- Channel progress ring.

HUD updates from state:

```js
hud.update(state)
```

Do not let HUD mutate gameplay state.

Why:

- Keeps presentation one-way.
- Makes HUD tests simpler.

---

## 32. Screens

`src/render/screens.js`

Screens:

- Start screen.
- End screen.
- Sector banner.
- Tide warning banner.

Start screen:

- Title.
- Subtitle.
- Controls.
- Begin button.
- Initializes audio on click.

End screen:

- Treasure found.
- Rank.
- Time.
- Coins.
- Keys.
- Restart button.

Why start screen:

- Browser audio requires user gesture.
- Player needs controls.
- Gives a clean audio unlock.

---

## 33. Input

`src/input.js`

Input is separate from movement logic.

Input state:

```js
{
  moveX: 0,
  moveY: 0,
  run: false,
  interact: false,
  map: false,
}
```

Controls:

| Input | Action |
|---|---|
| W/A/S/D or Arrows | Move |
| Shift | Run |
| E or Enter | Interact |
| M or Right Mouse | Hold to open map |

Rules:

- Right mouse context menu must be prevented while playing.
- Opening map cancels channel.
- While map is open, movement input is ignored.
- Interact is edge-triggered, not hold-triggered.

Why map disables movement:

- The map is a large puzzle overlay.
- Holding the map while moving would make the map hard to read.
- Tide and safe displacement still apply while map is open.

---

## 34. Audio Architecture

`src/audio/audio.js`

Audio manager interface:

```js
class AudioManager {
  init() {}
  play(name, options = {}) {}
  setMusicState(state) {}
  dispose() {}
}
```

Browser audio uses Web Audio.

Headless audio uses `NullAudio`.

Audio is initialized only after user gesture.

Why:

- Browser autoplay policy.
- Tests do not need real audio.

---

## 35. SFX Mapping

Map gameplay/presentation events to SFX.

| Event | SFX |
|---|---|
| `key_collected` | key collected |
| `coin_collected` | coin collected |
| `cache_sealed_prompt` | padlock thunk |
| `cache_opened` | cache opened |
| rope interaction complete | rope pulled |
| column interaction complete | column moved |
| `tide_warning` | tide warning |
| `tide_state_changed` to LOW | low tide reached |
| `tide_state_changed` to HIGH | high tide reached |
| vault locked prompt | vault locked |
| `vault_opened` | vault opening |
| `game_complete` | game complete |
| `landmark_discovered` | map stamp |
| `geometric_clue_added` | clue added |
| `safe_displacement_occurred` | safe displacement |
| `blocked_movement` | soft blocked thud |
| dry movement | footstep dry |
| shallow movement | footstep shallow |
| in water | swim loop |
| UI hover | UI hover |
| UI click | UI click |
| map open | map open |
| map close | map close |

SFX priority:

1. Key collected.
2. Vault opening/complete.
3. Tide warning/state.
4. Cache interaction.
5. Coin collected.
6. Movement/water.
7. UI.

Max simultaneous SFX:

```text
8
```

If more SFX request playback, drop the lowest priority.

Why:

- Prevents audio clipping and annoying overlap.
- Matches visual SFX priority.

---

## 36. Music Architecture

Use simple adaptive layering, not separate full tracks.

Layers:

- Sea bed.
- Percussion.
- Melody.
- Tide accent.
- Stingers.

Music state can be derived from:

- screen,
- player depth,
- tide state,
- vault state.

Example:

```js
function getMusicState(state) {
  if (state.screen === "start") return "start";
  if (state.screen === "complete") return "complete";
  if (state.vault.state === "READY") return "vault_ready";
  if (state.player.depth > 1) return "blocked_water";
  if (state.player.depth > 0) return "shallow";
  if (state.tide.state === "HIGH") return "high_tide";
  if (state.tide.state === "RISING") return "rising";
  if (state.tide.state === "LOW") return "low_tide";
  return "exploration";
}
```

Rules:

- Duck music by about 3 dB when high-priority SFX play.
- Keep SFX clearer than music.
- Do not let water loops overpower key/vault sounds.

Why simple:

- The game is short.
- Full procedural music composition is out of scope.
- Layered state changes are enough to support the visual audio design.

---

## 37. Deterministic RNG

`src/rng.js`

Use a small deterministic RNG such as mulberry32.

```js
export function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0;
    a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
```

Rules:

- Level seed variation uses RNG.
- Simulation does not use `Math.random()`.
- Visual-only effects may use `Math.random()`, but they must not affect state.

Why:

- Tests must be reproducible.
- Level validation must be deterministic.

---

## 38. Test Harness

The test harness must prove the game is complete and playable.

Use Vitest.

Headless game factory:

```js
test/harness/headlessGame.js
```

It creates:

- NullRenderer.
- NullAudio.
- NullHUD.
- NullScreens.
- TestInput.

TestInput should expose:

```js
{
  setMove(x, y),
  setRun(bool),
  pressInteract(),
  setMapOpen(bool),
  reset()
}
```

Helper utilities:

```js
async function tickFor(game, seconds)
function until(game, predicate, maxTicks)
function assertEvent(events, name)
function collectEvents(events)
```

Example:

```js
await tickFor(game, 1);
```

Should tick in fixed steps.

Why:

- Tests can reason in seconds, not frames.
- Deterministic simulation.

---

## 39. Unit Tests

These tests validate individual systems.

### 39.1 `config.test.js`

Assert constants match gameplay:

- World 256x256.
- Tide period 120.
- Water level range 0 to 2.
- Low threshold 0.7.
- High threshold 1.3.
- Passable depth 1.0.
- Walk/run/swim speeds.
- Stamina values.
- Total coins 160.

Why:

- Prevents accidental constant drift.

---

### 39.2 `tide.test.js`

Assert:

- `waterLevel(0) === 0`
- `waterLevel(60) === 2`
- `waterLevel(120) ≈ 0`
- State at t=0 is LOW.
- State around t=30 is RISING.
- State at t=60 is HIGH.
- Warnings occur 10 seconds before threshold crossings.
- State changes emit events.

Example:

```js
expect(tide.waterLevel(0)).toBeCloseTo(0);
expect(tide.waterLevel(60)).toBeCloseTo(2);
expect(tide.stateAt(0)).toBe("LOW");
expect(tide.stateAt(60)).toBe("HIGH");
```

---

### 39.3 `terrain.test.js`

Assert:

- Elevation 0 at water level 0 is passable.
- Elevation 0 at water level 1 is passable.
- Elevation 0 at water level 1.01 is impassable.
- Elevation 1 at water level 2 is passable.
- Elevation 2 at water level 2 is passable.
- Movement between elevation difference 1 is allowed.
- Movement between elevation difference 2 is blocked.
- Ocean is impassable.

---

### 39.4 `movement.test.js`

Use a small custom level.

Assert:

- Walking speed is approximately 3 tiles/sec.
- Running speed is approximately 5 tiles/sec when dry and stamina > 0.
- Running does not work in water.
- Swimming speed is approximately 2 tiles/sec in shallow water.
- Swimming speed is 1.5 tiles/sec when stamina is 0.
- Player cannot enter deep water.
- Player cannot climb elevation difference 2.
- Player clamps at blocked tile edge.

Use tolerance for float movement:

```js
expect(distance).toBeGreaterThan(2.8);
expect(distance).toBeLessThan(3.2);
```

---

### 39.5 `stamina.test.js`

Assert:

- Running drains 12/sec.
- Swimming drains 10/sec.
- Regen is 20/sec when not draining.
- Stamina clamps at 0 and 100.
- Running disabled at 0 stamina.
- Player does not die at 0 stamina.

---

### 39.6 `safeDisplacement.test.js`

Create a test level or modify a headless level.

Assert:

- If current tile becomes deep water, player moves to nearest passable tile within 16.
- If no tile within 16, player moves to `lastHighSafeTile`.
- If no `lastHighSafeTile`, player moves to start.
- Active channel is cancelled.
- Keys/coins remain collected.
- Event `safe_displacement_occurred` is emitted.

---

### 39.7 `fog.test.js`

Assert:

- Entering a new tile reveals radius 10.
- Tiles beyond radius 10 are not revealed.
- High elevation blocks line of sight.
- Water does not block line of sight.
- Revealed tiles remain revealed.

---

### 39.8 `landmarks.test.js`

Assert:

- Landmark not discovered beyond 24 tiles.
- Landmark discovered within 24 tiles with line of sight.
- Line of sight blocked prevents discovery.
- Sector discovered when sector landmark discovered.
- Hunt area not revealed before Key 1.
- Hunt area revealed after Key 1 and landmark discovery.

---

### 39.9 `interaction.test.js`

Assert:

- Key 1 cache is not sealed.
- Keys 2-5 are sealed before Key 1.
- Channel starts on interact.
- Channel completes after exact duration.
- Channel cancels if player moves.
- Channel cancels if map opens.
- Channel cancels if safe displacement occurs.
- Opened cache remains open.
- Cache awards key and 10 coins.

---

### 39.10 `clues.test.js`

Assert:

- Keys 1-4 add clues.
- Key 5 does not add clue.
- Vault marker appears after 4 geometric clues.
- Clue ring distances match level data.
- Corrected clue distances still resolve to vault.

---

### 39.11 `coins.test.js`

Assert:

- Walking over coin collects it.
- Coin cannot be collected twice.
- Coin counter updates.
- Rank thresholds are correct.
- Canonical level total possible coins is 160.
- Low-tide coin on elevation 0 cannot be collected when tile is deep water.

---

### 39.12 `vault.test.js`

Assert:

- Vault locked with fewer than 5 keys.
- Vault sealed by tide with 5 keys but not low tide.
- Vault ready with 5 keys and low tide.
- Vault channel cancels if tide rises.
- Vault channel cancels if player moves.
- Vault channel completes and emits `game_complete`.
- Completion awards 70 vault coins.
- End stats include time, keys, coins, rank.

---

### 39.13 `levelValidator.test.js`

Assert canonical/seeded levels pass:

- Low tide reachability to all caches and vault.
- High tide reachability to sector safe tiles.
- Clue overlap contains vault.
- Clue overlap size < 400.
- Total coins = 160.
- Cache positions valid.
- Start safe tile valid.
- Ocean border valid.

Also assert:

- Invalid level triggers fallback.
- Fallback level is completable.

---

## 40. Integration Tests

### 40.1 `startup.test.js`

Assert:

- Game starts on start screen.
- Calling `start()` emits `game_start`.
- Screen becomes `playing`.
- Player is at start tile.
- Objective is start objective.
- Tide starts at low tide.
- Fog around start is revealed.

---

### 40.2 `keyCollection.test.js`

Use headless game and debug positioning if needed.

Assert:

- Collecting Key 1 emits `key_collected`.
- Key 1 adds clue.
- Keys 2-5 unseal after Key 1.
- Collecting Keys 2-4 adds clues.
- Key 5 does not add clue.
- Vault marker appears after 4 geometric clues.
- Vault unlocks after 5 keys.

This test may use `game.debug.setPosition()` for speed.

Why debug positioning is okay here:

- This test validates key/clue state logic, not navigation.
- Navigation is tested separately.

---

### 40.3 `vaultCompletion.test.js`

Assert:

- Vault cannot open before 5 keys.
- Vault cannot open before low tide.
- With 5 keys and low tide, channel completes.
- Game complete event fires.
- Coins include vault coins.
- Input disabled after completion.
- Restart resets state.

---

## 41. Playthrough Test

This is the primary test that proves the game is finished and playable.

File:

```text
test/integration/playthrough.test.js
```

It uses a headless game and a bot.

No debug teleportation should be used in this test, except possibly setting a deterministic seed.

The bot must:

1. Start at the start tile.
2. Collect Key 1.
3. Collect Keys 2 through 5.
4. Reach the vault.
5. Wait for low tide if necessary.
6. Open the vault.
7. Trigger `game_complete`.

This test should simulate the game using real tide timing.

Maximum simulated time:

```text
30 minutes = 1800 seconds
```

At 60 fixed steps/sec:

```text
108,000 ticks
```

This is acceptable for a Node test.

---

## 42. Bot Design

`test/harness/bot.js`

The bot is a simple greedy agent.

It does not need to be perfect; it only needs to complete the canonical level.

### 42.1 Bot Objective Selection

```text
if no keys collected:
  target = Key 1 cache
else if keys collected < 5:
  target = nearest uncollected unlocked cache
else:
  target = vault
```

Use Euclidean distance for candidate selection.

Path cost can be A* distance if needed.

---

### 42.2 Pathfinding Utility

`test/harness/aStar.js`

Use A* for the bot.

This is test/dev tooling, not production gameplay.

Why not put A* in production:

- The game does not need automatic player pathing.
- The player is supposed to explore.
- Keeping A* out of production reduces scope.

A* requirements:

- 4-directional grid.
- Start tile.
- Target tile.
- Passability function based on current water level.
- Elevation difference rule.
- Deterministic tie-breaking.
- Max node limit to prevent pathological searches.

Pseudo:

```js
function findPath(level, start, target, waterLevel, maxNodes = 20000) {
  // A*
  // neighbor order: down, right, up, left for determinism
  // cost = 1 per tile
  // heuristic = manhattan distance
  // edge valid if canEnterTile(...)
  // return array of tiles or null
}
```

Why A* instead of BFS:

- Island is large.
- A* usually explores fewer nodes for long paths.
- Deterministic neighbor order keeps tests stable.

---

### 42.3 Bot Movement

Bot loop:

```text
repeat until complete or max ticks:
  choose objective
  compute path to objective
  if no path:
    if target requires low tide and not low tide:
      wait at high-safe tile
    else if current tile unsafe:
      move to lastHighSafeTile
    else:
      wait one tick
  else:
    follow path by setting input.moveX/moveY toward next tile center
  if in interaction range and target eligible:
    stop moving
    press interact
    wait until channel completes
```

Stuck detection:

- Store last player position.
- If position does not change for 60 ticks, recompute path.
- If path still fails, move to `lastHighSafeTile`.
- If stuck for more than 2 simulated minutes, fail.

Why:

- Handles tide changes.
- Recovers from path invalidation.
- Prevents infinite loops.

---

### 42.4 Bot Tide Waiting

If target is unreachable because of tide:

1. If current tile elevation >= 1, wait in place.
2. If current tile elevation < 1, move to `lastHighSafeTile`.
3. Recompute path every 1 second or when tide state changes.
4. If no path for more than 130 seconds, fail.

Why 130 seconds:

- Full tide cycle is 120 seconds.
- A little buffer avoids flaky failures.

---

### 42.5 Bot Interaction

When target is in range:

- Set movement to zero.
- Press interact once.
- Tick until channel completes or cancels.
- If cancelled due to tide, wait and retry.
- If cancelled due to movement, ensure bot did not move.

For vault:

- Wait until 5 keys and low tide.
- Channel for 1 second.
- Assert completion.

---

## 43. Acceptance Test: Game Is Finished and Playable

The playthrough test should assert:

```js
expect(game.state.vault.completed).toBe(true);
expect(game.state.screen).toBe("complete");
expect(game.state.keys.totalCollected).toBe(5);
expect(game.state.keys.collected).toEqual([true, true, true, true, true]);
expect(game.state.coins.collected).toBeGreaterThanOrEqual(120);
expect(events.emitted("game_complete")).toBe(true);
expect(events.emitted("key_collected", 5)).toBe(true);
expect(events.emitted("vault_opened")).toBe(true);
expect(game.state.progression).toBe("GAME_COMPLETE");
```

Why `coins >= 120`:

- 5 caches x 10 = 50.
- Vault = 70.
- Minimum completion coins = 120.
- Scattered coins are optional.

Also assert:

- All 5 caches collected.
- Vault marker revealed before completion.
- No unhandled exceptions.
- Player position remains inside bounds.
- Player tile is passable at completion or immediately after completion.
- Simulated time is under 30 minutes.

This test is the strongest proof that the game is playable end-to-end.

---

## 44. Edge Case Tests

The test suite must include targeted edge cases.

### 44.1 Sealed Cache Before Key 1

- Player reaches Keys 2-5 before Key 1.
- Prompt says sealed.
- No channel starts.
- After Key 1, cache becomes openable.

---

### 44.2 Player in Shallow Water When Tide Rises

- Player is on elevation 0 or 1 shallow tile.
- Tide rises to deep water.
- Safe displacement occurs.
- Player ends on passable tile.
- Channel cancelled if active.

---

### 44.3 No Local Passable Tile

- Use test level where player is in a deep-water pocket.
- Safe displacement uses `lastHighSafeTile`.
- If none, uses start.

---

### 44.4 Map Open During Channel

- Start channel.
- Open map.
- Channel cancels.
- Player can resume after closing map.

---

### 44.5 Movement During Channel

- Start channel.
- Press movement.
- Channel cancels.

---

### 44.6 Vault Tide Cancellation

- 5 keys.
- Low tide.
- Start vault channel.
- Force tide past low threshold before 1 second completes.
- Channel cancels.
- Vault remains unopened.

Use debug tide setter for this specific unit test.

---

### 44.7 Zero Stamina

- Set stamina to 0.
- Player can still walk.
- Player swims slowly in water.
- Player does not die.

---

### 44.8 Coin Total

- Canonical level must contain exactly 40 scattered coins.
- Total possible coins must be 160.

---

### 44.9 Invalid Level Fallback

- Provide intentionally invalid level.
- Validator fails.
- Game uses fallback.
- Fallback is completable.

---

## 45. Performance Tests

Performance tests should be lightweight.

### 45.1 Culling Test

Assert:

- Visible tile count is below a budget.
- For a 1920x1080 viewport, visible tile count < 3000.
- For a 800x480 viewport, visible tile count < 1200.

Why:

- Ensures renderer does not draw the whole world.

---

### 45.2 Map Dirty Redraw Test

Assert:

- Static map layers do not redraw when only player position changes.
- Water layer redraws at throttled rate.
- Clue layer redraws only when clue count changes.

This can be tested by spying on layer draw calls.

---

### 45.3 Simulation Tick Budget

Optional but useful:

- Measure average `game.tick(1/60)` time in headless Node.
- Assert under a generous budget, for example 1 ms per tick in CI.

Why:

- 60 ticks/sec requires the update loop to be fast.
- A 256x256 game should not do full-world passability every frame.

This should be a warning-level performance guard, not a strict gameplay rule.

---

## 46. Debug API

`game.debug` is for tests and development.

Minimum methods:

```js
debug.setPosition(x, y)
debug.setTile(x, y)
debug.setTideTime(t)
debug.setStamina(value)
debug.collectKey(keyId)
debug.collectAllCoins()
debug.revealAll()
debug.getTileInfo(x, y)
```

Rules:

- Debug methods are not called in normal browser gameplay.
- Debug methods can be enabled only in tests or when `?debug=1`.
- Debug methods must not break determinism if used in tests.

Why:

- Some edge-case tests need exact state setup.
- Avoids building complicated UI for manual testing.

---

## 47. Build and Run

`package.json` scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "test": "vitest run",
    "test:watch": "vitest"
  }
}
```

Commands:

- `npm install`
- `npm run dev`
- `npm run build`
- `npm test`

Why:

- Minimal tooling.
- Integrator can run immediately.

---

## 48. Testing Philosophy

The test suite is divided into three confidence layers.

### Layer 1: Unit

Proves each system follows its rules.

Examples:

- Tide formula.
- Passability.
- Movement speed.
- Channel cancellation.
- Fog LOS.

### Layer 2: Integration

Proves systems work together.

Examples:

- Key collection updates clues.
- Landmark discovery reveals hunt area.
- Vault completion ends game.

### Layer 3: Playthrough

Proves the whole game is completable.

Examples:

- Bot starts at start tile.
- Bot collects all keys.
- Bot waits for low tide.
- Bot opens vault.
- Game complete event fires.

Why this structure:

- Unit tests isolate bugs.
- Integration tests catch interface mismatches.
- Playthrough test proves the player can actually finish.

---

## 49. Important Engineering Decisions and Rationale

### 49.1 Fixed Timestep

Decision:

- Use 1/60 second fixed simulation steps.

Why:

- Deterministic movement, tide, stamina, and channel timing.
- Tests can simulate exact seconds.
- Variable browser frame rates do not change gameplay.

---

### 49.2 On-Demand Passability

Decision:

- Do not maintain a full mutable passability grid updated every frame.

Why:

- The player only needs local tile passability most of the time.
- Renderer only needs visible tiles.
- Safe displacement only needs local search.
- This avoids 65,536 tile updates per frame.

---

### 49.3 Canonical Level Fallback

Decision:

- Include a deterministic canonical level builder.

Why:

- The gameplay design provides key/sector positions but not a complete tile heightmap.
- Engineering needs a runnable level for tests.
- A validated fallback prevents shipping an uncompletable game.
- Designers can later replace it with an authored level file.

---

### 49.4 DOM HUD

Decision:

- Use DOM for HUD and screens.

Why:

- Better text readability.
- Better accessibility.
- Simpler layout.
- Less canvas overhead.

---

### 49.5 A* Only in Tests

Decision:

- Do not ship automatic player pathfinding in the game.

Why:

- The game is about exploration, not assisted travel.
- Pathfinding would add production complexity.
- Tests still need a reliable bot to prove playability.

---

### 49.6 Map Open Disables Movement

Decision:

- While the map is open, movement input is ignored.

Why:

- The map is the main puzzle tool.
- Holding the map while moving would obscure the map and cause accidental position changes.
- Tide and safe displacement still continue, so the player is not exempt from environmental pressure.

---

### 49.7 Low Tide Warning Added

Decision:

- Warn 10 seconds before low tide in addition to rising/high warnings.

Why:

- Low tide is required for vault and low-tide content.
- Visual design includes low tide warning examples.
- It improves planning without adding combat-style panic.

---

## 50. Cuts and Non-Goals

The following are intentionally cut.

| Cut | Reason |
|---|---|
| Save system | Single 15-25 minute session. |
| Inventory UI | Keys/coins are automatic. |
| Combat | Cut by gameplay design. |
| Health/death | Cut by gameplay design. |
| Free 3D camera | 2.5D isometric is required and clearer. |
| WebGL | Canvas 2D is sufficient. |
| Full procedural music composition | Adaptive layers are enough. |
| Volume sliders | Browser volume is enough for a short session. |
| In-game pathfinding | Would reduce exploration and add scope. |
| Global per-frame passability grid | Not needed; on-demand is faster. |
| Complex particle systems | Keep browser performance stable. |
| Dynamic lighting | Not needed for readability. |
| Day/night | Cut by gameplay design. |
| Weather | Tide is the environmental system. |
| Multiplayer | Out of scope. |
| Permadeath | Cut by gameplay design. |
| Shops/meta progression | Single session does not need it. |

---

## 51. Final Engineering Checklist

Before the game is considered engineering-complete:

### Build

- [ ] `npm install` works.
- [ ] `npm run dev` runs.
- [ ] `npm run build` succeeds.
- [ ] `npm test` passes.

### Simulation

- [ ] Game uses fixed timestep.
- [ ] Tide formula matches gameplay.
- [ ] Passability uses depth <= 1.0.
- [ ] Elevation difference > 1 blocks movement.
- [ ] Stamina rules match gameplay.
- [ ] Safe displacement always places player on passable tile.
- [ ] Fog reveal uses radius 10 and LOS.
- [ ] Landmarks discover within 24 tiles and LOS.
- [ ] Hunt areas reveal after Key 1 and sector landmark.
- [ ] Caches 2-5 are sealed until Key 1.
- [ ] Channeling cancels on movement/map/safe displacement.
- [ ] Clues 1-4 reveal vault marker at 4 clues.
- [ ] Vault requires 5 keys and low tide.
- [ ] Completion awards vault coins and ends game.

### Level

- [ ] Level validator runs before gameplay.
- [ ] Low tide reachability passes.
- [ ] High tide reachability passes.
- [ ] Clue overlap validation passes.
- [ ] Total possible coins is 160.
- [ ] Invalid level falls back to playable level.

### Rendering

- [ ] World renders in fixed isometric view.
- [ ] Terrain is culled.
- [ ] Terrain tiles are cached.
- [ ] Water depth is visually distinguishable.
- [ ] Map shows fog, water, landmarks, hunt areas, clues, vault, player.
- [ ] HUD shows tide, stamina, keys, coins, objective, prompt.
- [ ] Start screen initializes audio.
- [ ] End screen shows stats.

### Audio

- [ ] Audio initializes on user gesture.
- [ ] Key/vault/tide SFX are mapped.
- [ ] Max SFX limit enforced.
- [ ] Music ducks for important SFX.

### Tests

- [ ] Unit tests pass.
- [ ] Integration tests pass.
- [ ] Playthrough bot completes game.
- [ ] Edge case tests pass.
- [ ] Performance/culling guard passes.

When all of these are true, the engineering handoff should be considered complete.