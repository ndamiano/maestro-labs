# engineering.md

## 0. Scope and Authority

This document is the engineering handoff for *Island of the Hidden Hoard*.

It defines:

- the files that must exist,
- the runtime architecture,
- the level data contract and level-generation/validation strategy,
- the core gameplay systems that make the authored island playable,
- the rendering integration contract,
- the audio implementation contract,
- the test harness,
- the automated test set that proves the game is complete and playable.

Where `gameplay.md` and `visual.md` already define constants, this document does not re-derive them. It only specifies how to implement them reliably and testably.

Important engineering principles:

1. **Gameplay logic is separated from rendering, input, and audio.**
   - Why: the core game must be testable headlessly, debuggable, and reusable.
2. **The level is authored by designers, but implemented as deterministic level data plus validation.**
   - Why: the game must always be completable.
3. **If generated or seeded content fails validation, the game falls back to a guaranteed-playable default.**
   - Why: an open-world browser game with progression must never soft-lock.
4. **All state changes flow through a single event bus.**
   - Why: renderer, audio, HUD, and systems stay decoupled.
5. **No unnecessary systems are included.**
   - Why: the game is a short, complete session. Complexity that does not serve readability or completion is cut.

---

## 1. Deliverables and File Tree

The game is a static HTML/CSS/JS app. No build step is required. ES modules are used. Tests run in Node without a browser.

Required files:

```text
/
  index.html
  package.json
  css/
    main.css
  js/
    main.js
    config/
      constants.js
    core/
      eventBus.js
      rng.js
      geometry.js
      tilemap.js
      pathfinding.js
      state.js
      game.js
    level/
      layout.js
      generator.js
      validator.js
    systems/
      tide.js
      movement.js
      fog.js
      landmarks.js
      caches.js
      coins.js
      vault.js
      objectives.js
    render/
      renderer.js
      mapRenderer.js
      hudRenderer.js
    audio/
      audioManager.js
  tests/
    harness.js
    unit/
      tide.test.js
      passability.test.js
      movement.test.js
      stamina.test.js
      safeDisplacement.test.js
      fog.test.js
      landmarks.test.js
      caches.test.js
      coins.test.js
      vault.test.js
      clues.test.js
      levelGenerator.test.js
      events.test.js
      audio.test.js
    playthrough.test.js
    e2e/
      smoke.spec.js
```

`package.json` should contain at least:

```json
{
  "name": "island-of-the-hidden-hoard",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test tests/",
    "test:play": "node --test tests/playthrough.test.js",
    "test:unit": "node --test tests/unit/"
  }
}
```

No runtime dependencies are required for the core game or unit tests.

Optional E2E testing may use Playwright or a similar browser driver, but it is not required for core validation.

---

## 2. Runtime Architecture

### 2.1 Boot Flow

`index.html` loads:

- `css/main.css`
- `js/main.js`

`main.js` is only run in the browser. It:

1. Reads canvas and DOM elements.
2. Creates the level.
3. Creates the headless/game logic instance.
4. Creates renderer, HUD, and audio manager.
5. Shows the start screen.
6. On user click of **Begin Salvage**:
   - unlocks audio,
   - starts the game loop,
   - enables input.

### 2.2 Layering

```text
Input
  -> Game.update(dt)
       -> tide
       -> movement
       -> stamina
       -> safe displacement
       -> fog
       -> landmarks
       -> caches
       -> coins
       -> vault
       -> objectives
       -> event bus
            -> renderer
            -> HUD
            -> audio
```

Rules:

- Renderer never mutates gameplay state directly.
- Audio never mutates gameplay state directly.
- HUD reads state and listens to events.
- Input is the only external mutation source, dispatched into the game.

### 2.3 Event Bus

Use a small event bus:

```js
class EventBus {
  constructor() {
    this.listeners = new Map();
  }

  on(event, fn) {
    if (!this.listeners.has(event)) this.listeners.set(event, []);
    this.listeners.get(event).push(fn);
    return () => this.off(event, fn);
  }

  off(event, fn) {
    const arr = this.listeners.get(event);
    if (!arr) return;
    const i = arr.indexOf(fn);
    if (i >= 0) arr.splice(i, 1);
  }

  emit(event, payload = {}) {
    const arr = this.listeners.get(event);
    if (!arr) return;
    for (const fn of arr.slice()) fn(payload);
  }
}
```

Events are the main integration seam.

---

## 3. Core Data Contracts

### 3.1 Coordinate System

World coordinates are tile units.

- World size: `256 x 256`
- Tile index `x` increases right.
- Tile index `y` increases down.
- Outer `8` tiles are ocean and impassable.
- Continuous player position uses tile-space floats.
  - Tile `(x, y)` occupies `[x, x+1] x [y, y+1]`.
  - Tile center is `(x + 0.5, y + 0.5)`.
  - `tileX = Math.floor(player.x)`
  - `tileY = Math.floor(player.y)`

Authored positions such as start `(32, 220)` are tile indices. Runtime entity positions store both:

```js
{
  x: 32,
  y: 220,
  centerX: 32.5,
  centerY: 220.5
}
```

Distance calculations between authored tiles use integer differences.

### 3.2 Level Object

The level is created once at boot and is immutable except for runtime mutable sets such as blockers and collected coins.

```js
{
  seed: 123,
  size: 256,
  elevation: Uint8Array,     // length 65536, values 0-5
  ocean: Uint8Array,         // 1 for outer ocean border
  sector: Uint8Array,        // sector id per tile, 0 for ocean/no sector
  start: { x: 32, y: 220 },
  vault: { x: 208, y: 192 },
  landmarks: [...],
  caches: [...],
  coins: [...],
  highAnchors: [...],
  blockers: Set<number>,     // dynamic tile indices
  validation: {
    ok: true,
    fallbackUsed: false,
    errors: []
  }
}
```

Tile index helper:

```js
const index = y * size + x;
const x = index % size;
const y = Math.floor(index / size);
```

### 3.3 Landmark Object

```js
{
  id: "shipwreck",
  name: "Shipwreck",
  x: 40,
  y: 210,
  elevation: 1,
  sectorId: "driftwood-cove",
  isSectorLandmark: true,
  discovered: false
}
```

Landmark discovery state can be stored either in the landmark object or in game state. For clarity, store runtime discovery in game state:

```js
state.landmarks.discovered = Set<string>
```

### 3.4 Cache Object

```js
{
  id: "key1",
  keyId: 1,
  sectorId: "driftwood-cove",
  x: 45,
  y: 208,
  elevation: 1,

  interact: { x: 45, y: 208 },
  reward: { x: 45, y: 208 },

  channelTime: 0.5,
  requiresKey1: false,
  clue: {
    landmarkId: "shipwreck",
    distance: 169
  },

  blockerTiles: [],
  blockerActive: false,

  collected: false,
  opened: false
}
```

Important fields:

- `interact`: where the player must be near to start the channel.
- `reward`: where the key/coins are logically granted.
- `blockerTiles`: optional tiles that block movement until the cache is opened.
- `blockerActive`: true until opened.

Caches with physical puzzles:

- Key 3: root gate blocks 2 tiles until rope is pulled.
- Key 4: stone column blocks 1 tile until moved.

Default blockers:

```js
key3.blockerTiles = [tileIndex(80, 111), tileIndex(80, 110)];
key3.interact = { x: 80, y: 109 };
key3.reward = { x: 80, y: 112 };

key4.blockerTiles = [tileIndex(192, 131)];
key4.interact = { x: 192, y: 130 };
key4.reward = { x: 192, y: 132 };
```

If a seeded cache offset is applied, blocker tiles and interact/reward positions move with the cache, then validation is required. If invalid, use default positions.

### 3.5 Coin Object

```js
{
  id: "coin-001",
  x: 52,
  y: 205,
  collected: false,
  lowTideOnly: false
}
```

World coin total is `40` scattered coins.

Coins from caches and vault are not represented as world coins. They are granted directly on events:

- Each cache: `10`
- Vault: `70`

Total possible: `160`.

### 3.6 Game State

The core state should mirror the gameplay design.

```js
{
  progress: "START",
  elapsedTime: 0,
  player: {
    x: 32.5,
    y: 220.5,
    tileX: 32,
    tileY: 220,
    facing: "down",
    stamina: 100
  },
  tide: {
    time: 0,
    waterLevel: 0,
    state: "LOW"
  },
  keys: {
    totalCollected: 0,
    geometricCollected: 0,
    collected: Set(),
    clues: []
  },
  coins: {
    collected: 0
  },
  vault: {
    markerRevealed: false,
    ready: false,
    unlocked: false,
    completed: false
  },
  tiles: {
    revealed: Uint8Array
  },
  landmarks: {
    discovered: Set()
  },
  sectors: {
    discovered: Set()
  },
  caches: {
    collected: Set(),
    opened: Set()
  },
  activeChannel: null,
  lastHighSafeTile: { x: 32, y: 220 },
  input: {
    up: false,
    down: false,
    left: false,
    right: false,
    run: false,
    map: false,
    interact: false
  },
  complete: false
}
```

Progression states:

```text
START
TUTORIAL_KEY1
FREE_KEYS_1_OF_5
FREE_KEYS_2_OF_5
FREE_KEYS_3_OF_5
FREE_KEYS_4_OF_5
FREE_KEYS_5_OF_5
VAULT_READY
VAULT_OPEN
GAME_COMPLETE
```

`TUTORIAL_KEY1` is an alias for `keys.totalCollected === 0`. It is used for objective text.

---

## 4. Events

Use these events as the integration contract.

Core gameplay events:

```text
game_start
landmark_discovered
sector_discovered
cache_sealed_prompt
cache_opened
key_collected
geometric_clue_added
coin_collected
hunt_area_revealed
vault_marker_revealed
vault_unlocked
tide_warning
tide_state_changed
safe_displacement_occurred
vault_opened
game_complete
```

Additional implementation events:

```text
map_opened
map_closed
channel_started
channel_cancelled
channel_complete
vault_ready_changed
objective_changed
```

Event payloads:

```js
// landmark_discovered
{ landmarkId }

// sector_discovered
{ sectorId, sectorName }

// cache_sealed_prompt
{ cacheId, prompt }

// cache_opened
{ cacheId }

// key_collected
{ keyId, totalCollected, geometricCollected }

// geometric_clue_added
{ keyId, landmarkId, distance }

// coin_collected
{ amount, totalCollected }

// hunt_area_revealed
{ sectorId, cacheId }

// vault_marker_revealed
{ x, y }

// vault_ready_changed
{ ready }

// channel_started
{ type, targetId, duration }

// channel_cancelled
{ type, targetId, reason }

// channel_complete
{ type, targetId }

// safe_displacement_occurred
{ fromTile, toTile, reason }

// game_complete
{
  time,
  keys: 5,
  coins,
  rank
}
```

Events are emitted, not returned. Systems should not depend on return values.

---

## 5. Constants

`js/config/constants.js` must export all gameplay constants.

Key constants:

```js
export const CONFIG = {
  size: 256,
  oceanBorder: 8,
  maxElevation: 5,

  tide: {
    period: 120,
    lowThreshold: 0.7,
    highThreshold: 1.3,
    passableDepth: 1.0,
    warningSeconds: 10
  },

  movement: {
    walk: 3.0,
    run: 5.0,
    swim: 2.0,
    lowStaminaSwim: 1.5,
    substepMax: 0.1
  },

  stamina: {
    max: 100,
    runDrain: 12,
    swimDrain: 10,
    regen: 20
  },

  fog: {
    radius: 10,
    losStep: 0.5
  },

  landmarks: {
    visibleDistance: 24
  },

  caches: {
    visibleDistance: 8,
    interactRadius: 1.5,
    huntRadius: 24
  },

  clues: {
    width: 6,
    maxOverlapTiles: 400
  },

  safeDisplacement: {
    radius: 16
  },

  coins: {
    total: 160,
    scatteredPerSector: 8,
    perCache: 10,
    vault: 70
  },

  map: {
    tilePx: 2,
    maxPx: 512
  }
};
```

### 5.1 Interaction Radius Decision

`caches.interactRadius = 1.5`.

Why:

- Movement uses smooth float positions.
- Tile centers are integer-based.
- A 1.5 tile radius avoids pixel-perfect frustration while still requiring the player to be near the prop.
- It is consistent with the cache visibility distance of 8 tiles.

---

## 6. Level Generation and Validation

The gameplay designer has authored the island concept, sector roles, landmarks, caches, vault, and progression. Engineering does not redesign those. Engineering provides a deterministic builder that turns that authored layout into a valid 256x256 tile grid and validates it.

### 6.1 Level Descriptor

The level layout is defined in `js/level/layout.js`.

It contains fixed data:

- world size,
- ocean border,
- start,
- vault,
- sectors,
- landmarks,
- caches,
- high-tide anchors,
- default blocker tiles.

This file is data, not art.

Example:

```js
export const LAYOUT = {
  size: 256,
  oceanBorder: 8,
  start: { x: 32, y: 220 },
  vault: { x: 208, y: 192 },

  sectors: [
    {
      id: "driftwood-cove",
      name: "Driftwood Cove",
      bounds: { x0: 16, y0: 190, x1: 70, y1: 240 },
      highAnchor: { x: 32, y: 215 },
      lowAnchor: { x: 32, y: 220 }
    },
    // ... other sectors
  ],

  landmarks: [
    { id: "shipwreck", name: "Shipwreck", x: 40, y: 210, elevation: 1, sectorId: "driftwood-cove" },
    // ...
  ],

  caches: [
    {
      id: "key1",
      keyId: 1,
      x: 45,
      y: 208,
      elevation: 1,
      channelTime: 0.5,
      requiresKey1: false,
      clue: { landmarkId: "shipwreck", distance: 169 }
    },
    // ...
  ]
};
```

High anchors are used for high-tide validation. They must be reachable when water level is `2.0`.

Recommended high anchors:

```text
Driftwood Cove:    (32, 215)
Gull Flats:        (150, 218)
Palm Hollow:       (75, 110)
Sunken Ruins:      (195, 130)
Cliffpath Ridge:   (145, 65)
Vault Point:       (205, 185)
```

These can be adjusted as long as they remain reachable at high tide.

---

### 6.2 Canonical Level Generator

`js/level/generator.js` creates a playable level from `LAYOUT` and an optional seed.

Seed only varies:

- cache positions 2-5 within 3 tiles,
- scattered coin positions.

It does not generate the critical progression path.

High-level algorithm:

```js
export function createLevel(seed = 12345) {
  const rng = mulberry32(seed);

  let level = buildBaseLevel();
  applySectorBaseFeatures(level);
  applyRequiredPointElevations(level);
  carveGuaranteedRoutes(level);
  addDecorativeHighGround(level);
  applySeededCacheVariation(level, rng);
  placeScatteredCoins(level, rng);
  applyBlockers(level);

  const report = validateLevel(level);

  if (!report.ok) {
    console.warn("Level validation failed; using fallback level.", report);
    level = createFallbackLevel();
    level.validation = {
      ok: true,
      fallbackUsed: true,
      errors: report.errors
    };
  }

  return level;
}
```

#### 6.2.1 `buildBaseLevel()`

Creates the guaranteed base island.

Rules:

1. All tiles initialize to elevation `0`.
2. Ocean border tiles are marked ocean and impassable.
3. Interior tiles default to elevation `1`.
4. The first interior ring adjacent to ocean is elevation `0` to create beaches.

Pseudocode:

```js
function buildBaseLevel() {
  const size = CONFIG.size;
  const border = CONFIG.oceanBorder;

  const elevation = new Uint8Array(size * size);
  const ocean = new Uint8Array(size * size);
  const sector = new Uint8Array(size * size);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const i = y * size + x;
      const inBorder =
        x < border ||
        y < border ||
        x >= size - border ||
        y >= size - border;

      if (inBorder) {
        ocean[i] = 1;
        elevation[i] = 0;
        continue;
      }

      elevation[i] = 1;
    }
  }

  // Shore ring
  for (let y = border; y < size - border; y++) {
    for (let x = border; x < size - border; x++) {
      const i = y * size + x;
      const shore = Math.min(
        x - border,
        y - border,
        size - 1 - x - border,
        size - 1 - y - border
      );

      if (shore <= 0) {
        elevation[i] = 0;
      }
    }
  }

  return { elevation, ocean, sector };
}
```

Why:

- The interior elevation `1` grid is passable at high tide.
- This guarantees a connected high-tide spine across the island.
- Elevation `0` shore tiles create low-tide beaches and flood naturally at high tide.

#### 6.2.2 `applySectorBaseFeatures()`

Apply low-detail sector elevation so sectors read correctly and match gameplay bounds.

Rules:

- Do not break the base elevation `1` connectivity.
- Use local low areas for beaches, flats, caves.
- Use local high features only with walkable ramps.
- Protect guaranteed routes from later elevation changes.

Sector operations:

| Sector | Operation |
|---|---|
| Driftwood Cove | Keep start area elevation `1`. Lower nearby beach to `0`. |
| Gull Flats | Lower southern flats to `0`. Keep a high-tide anchor at elevation `1` or higher. |
| Palm Hollow | Base `1`, optional small hills `2`. Keep routes at `1`. |
| Sunken Ruins | Base `1`, ruin floors `2`, optional tower base `3`. Keep routes at `1`. |
| Cliffpath Ridge | Add high ridge plateau `3-5`. Carve a walkable ramp from base `1` to `4`. |
| Vault Point | Cave floor `0` around vault, rocks `1`, reef outcrop `2`. Keep low-tide route to vault. |

Implementation should use helper functions:

```js
setTile(level, x, y, elevation)
fillRect(level, x0, y0, x1, y1, elevation)
raiseEllipse(level, cx, cy, rx, ry, maxElevation)
carveRectRoute(level, from, to, targetElevation)
carveGradualRoute(level, from, to, targetElevation)
```

Important:

- `fillRect` and `raiseEllipse` must respect ocean border.
- `carveGradualRoute` must ensure elevation difference between consecutive route tiles is at most `1`.

#### 6.2.3 Required Point Elevations

Set explicit elevations for authored points.

Required values from gameplay:

```text
Start:                  elevation 1
Vault:                  elevation 0
Gull Flats cache:       elevation 0
Gull Flats Lighthouse:  elevation 2
Palm Hollow Idol:       elevation 2
Sunken Arch:            elevation 2
Cliffpath Eagle Rock:   elevation 4
Vault Point Reef:       elevation 2
```

Other caches can be elevation `1` unless gameplay specifies otherwise.

If a required point has elevation `2` or higher, the generator must add a local ramp from a nearby passable tile so the point is reachable at low tide.

Function:

```js
function ensureReachablePoint(level, point, elevation) {
  setTile(level, point.x, point.y, elevation);

  const source = findNearestLowLandTile(level, point);
  carveGradualRoute(level, source, point, elevation);
}
```

Why:

- Landmarks and keys must be reachable or at least visually discoverable.
- For keys, physical reachability is required.
- For landmarks, reachability is required for validation simplicity and to avoid inaccessible puzzle references.

#### 6.2.4 Guaranteed Routes

Before decorative cliffs are added, carve guaranteed routes.

Required routes:

1. Start to every cache interact position.
2. Start to every cache reward position after blockers are removed.
3. Start to vault.
4. Start to every high anchor.
5. Start to every landmark.

Route carving rules:

- Use L-shaped paths to avoid diagonal corner issues.
- Low routes should use elevation `1` where possible.
- If the destination elevation is `2` or higher, interpolate elevation so adjacent route tiles differ by at most `1`.
- Mark route tiles in a `protected` mask.
- Decorative features must not break protected tiles.

Pseudocode:

```js
function carveLRoute(level, from, to, targetElevation) {
  const path = [];

  path.push(...horizontalLine(from, to));
  path.push(...verticalLine(horizontalEnd, to));

  let currentElev = elevationAt(level, from.x, from.y);

  for (const tile of path) {
    let desired = currentElev;

    if (targetElevation > currentElev) {
      desired = Math.min(targetElevation, currentElev + 1);
    } else if (targetElevation < currentElev) {
      desired = Math.max(targetElevation, currentElev - 1);
    }

    setTile(level, tile.x, tile.y, desired);
    currentElev = desired;
    protect(level, tile.x, tile.y);
  }
}
```

Why:

- This guarantees the critical progression path.
- It prevents procedural decoration from creating dead ends.
- It makes validation more stable.

#### 6.2.5 Decorative High Ground

After routes are protected, add decorative high ground.

Rules:

- Do not modify protected tiles.
- Do not create high-tide passable pockets disconnected from the high-tide spine.
- Cliff drops of `2+` are allowed outside protected routes.
- The Cliffpath Ridge should contain at least one walkable ramp to elevation `4`.

Recommended implementation:

```js
function addDecorativeHighGround(level) {
  addRidgePlateau(level);
  addRuinsTower(level);
  addLighthouseBase(level);
  addReefOutcrop(level);
}
```

The ridge plateau should be the main cliff feature:

- Center near Eagle Rock.
- Max elevation `4` or `5`.
- Protected ramp from lowland to `4`.
- Surrounding tiles may be `4` or `5` to create non-walkable cliff edges.

Why:

- The game needs readable cliffs.
- But the final key must still be reachable.
- A protected ramp gives both.

#### 6.2.6 Seeded Cache Variation

Apply small offsets to caches `key2` through `key5`.

Rules:

- Offset is within 3 tiles using the seed.
- Use Chebyshev distance for offset range:

```js
dx = Math.floor(rng() * 7) - 3;
dy = Math.floor(rng() * 7) - 3;
```

- New cache position must be:
  - inside playable bounds,
  - not ocean,
  - not on a required route blocker,
  - not within 2 tiles of another cache,
  - not within 2 tiles of the vault unless it is the vault-area cache,
  - passable at low tide,
  - for Key 2, elevation `0`,
  - for Key 3 and Key 4, associated blocker tiles must also move and remain valid.

If any check fails, use the default cache position.

Why:

- The gameplay design only allows minor variation.
- This gives replay texture without risking completion.

#### 6.2.7 Scattered Coin Placement

Place `8` coins in each key sector.

Total scattered coins: `40`.

Rules:

- Coins must be on low-tide passable tiles.
- Coins must not be in the ocean border.
- Coins must not be on active blocker tiles.
- Coins must not be within 2 tiles of another scattered coin.
- Coins may be in elevation `0` low-tide-only areas.
- If sampling fails, use deterministic fallback positions for that sector.

Pseudocode:

```js
function placeScatteredCoins(level, rng) {
  const placed = [];

  for (const sector of LAYOUT.sectors) {
    let attempts = 0;

    while (placedCount(sector) < 8 && attempts < 1000) {
      const tile = randomTileInSector(rng, sector);
      attempts++;

      if (!isLowTidePassable(level, tile, { blockers: true })) continue;
      if (isTooCloseToCoin(tile, placed, 2)) continue;
      if (isTooCloseToStart(tile, 2)) continue;

      placed.push(createCoin(tile));
    }

    if (placedCount(sector) < 8) {
      fillDeterministicSectorCoins(level, sector, placed);
    }
  }
}
```

Why:

- Coins are optional score.
- They should not block progression.
- They should not be unreachable or duplicated.

---

### 6.3 Level Validation

`js/level/validator.js` validates the level before the game starts.

Validation must be fast and deterministic.

Report:

```js
{
  ok: boolean,
  fallbackUsed: boolean,
  errors: [string]
}
```

#### 6.3.1 Passability Check

Passability is computed for a given water level.

```js
function tilePassable(level, x, y, waterLevel, blockers) {
  const i = y * level.size + x;

  if (level.ocean[i]) return false;
  if (blockers.has(i)) return false;

  const depth = Math.max(0, waterLevel - level.elevation[i]);
  return depth <= CONFIG.tide.passableDepth;
}
```

Movement between two adjacent tiles also requires:

```js
Math.abs(targetElevation - currentElevation) <= 1
```

Ocean border is always impassable.

#### 6.3.2 Low Tide Validation

Test at `waterLevel = 0`.

Checks:

1. Start is passable.
2. Every cache interact tile is passable with initial blockers.
3. Every landmark is passable with initial blockers.
4. Every high anchor is passable with initial blockers.
5. With all cache blockers removed:
   - every cache reward tile is passable,
   - vault is passable.

BFS from start is used for each condition.

Why:

- The game must be completable at low tide.
- Some caches are low-tide only, but they must be reachable when low tide occurs.

#### 6.3.3 High Tide Validation

Test at `waterLevel = 2`.

Checks:

1. Start is passable.
2. Every high anchor is passable.
3. Every high anchor is reachable from start with initial blockers.
4. Every high anchor is reachable from start with all blockers removed.

Recommended stricter check:

- All high-tide passable tiles should belong to the same connected component as start.

If a high-tide passable pocket is disconnected, the level is invalid.

Why:

- The gameplay design says the player should not be stranded by high tide.
- Safe displacement is a recovery system, not a replacement for a valid level.

#### 6.3.4 Cache Validation

For each cache:

- Position inside playable bounds.
- Not ocean.
- Not on a blocker unless intended as interact tile.
- Interact tile reachable at low tide.
- Reward tile reachable at low tide after blockers removed.
- Channel time is positive.
- Key 2 is elevation `0`.
- Keys 2-5 require Key 1.
- Keys 1-4 have clue data.
- Key 5 has no geometric clue.

#### 6.3.5 Clue Ring Validation

For Keys 1-4:

```js
D = Math.round(euclideanDistance(landmark, vault))
```

Validate:

1. Each clue distance matches the authored distance within `0` if possible.
2. If a mismatch occurs, the level is invalid and fallback is used.
3. Compute overlap for all four clues:

```js
overlapTiles = []

for each tile:
  insideAll = true

  for each clue:
    d = euclideanDistance(tile, clue.landmark)
    if Math.abs(d - clue.D) > CONFIG.clues.width:
      insideAll = false
      break

  if insideAll:
    overlapTiles.push(tile)

valid = overlapTiles.length < CONFIG.clues.maxOverlapTiles
valid = overlapTiles.includes(vaultTile)
```

Why:

- The map puzzle must become solvable.
- The final marker must appear at the vault.
- The overlap must not be too large.

#### 6.3.6 Coin Validation

Checks:

- Exactly `40` scattered coins.
- No coin in ocean.
- No coin on blocker tile.
- No two coins within 2 tiles.
- Every coin is low-tide passable.

#### 6.3.7 Fallback Level

If validation fails, use `createFallbackLevel()`.

Fallback level rules:

- Size `256`.
- Ocean border.
- Interior elevation `1`.
- Shore ring elevation `0`.
- Start elevation `1`.
- Vault elevation `0`.
- Landmarks set to elevation `1` with local ramp if needed.
- Caches at default positions.
- Key 2 elevation `0`.
- No decorative cliffs.
- No optional high pockets.
- Cache interactions still exist, but physical blockers are either:
  - removed, or
  - converted to trivial single-tile gaps with guaranteed access.

The fallback is intentionally less visually rich.

Why:

- Completion is more important than decoration.
- The player should never encounter a broken island.

---

## 7. Tide System

### 7.1 Formula

```js
const TAU = Math.PI * 2;

function waterLevelAt(t) {
  return 1 - Math.cos(TAU * t / CONFIG.tide.period);
}
```

Water level range: `0` to `2`.

Low tide at `t = 0`.
High tide at `t = 60`.

### 7.2 State

```js
function tideState(waterLevel) {
  if (waterLevel < CONFIG.tide.lowThreshold) return "LOW";
  if (waterLevel > CONFIG.tide.highThreshold) return "HIGH";
  return "RISING";
}
```

Exact thresholds:

- `waterLevel < 0.7` => `LOW`
- `waterLevel > 1.3` => `HIGH`
- otherwise => `RISING`

Vault low tide requirement uses the same strict `< 0.7`.

### 7.3 Threshold Times

The cycle can be treated as four threshold events per 120 seconds.

Approximate times:

```text
t = 24.194s   enter RISING from LOW
t = 36.033s   enter HIGH from RISING
t = 83.967s   enter RISING from HIGH
t = 95.806s   enter LOW from RISING
```

These can be computed analytically:

```js
const period = CONFIG.tide.period;
const lowTheta = Math.acos(1 - 0.7);
const highTheta = Math.acos(1 - 1.3);

const thresholds = [
  { time: lowTheta / TAU * period, enter: "RISING" },
  { time: highTheta / TAU * period, enter: "HIGH" },
  { time: (TAU - highTheta) / TAU * period, enter: "RISING" },
  { time: (TAU - lowTheta) / TAU * period, enter: "LOW" }
];
```

### 7.4 Warnings

Warn `10` seconds before each threshold.

Store:

```js
lastWarningCycle
lastWarningIndex
```

Each cycle, emit `tide_warning` once per threshold:

```js
{
  threshold: "RISING" | "HIGH" | "LOW",
  secondsUntil: 10
}
```

The HUD can display:

- `Tide rising in 10s`
- `High tide in 10s`
- `Low tide in 10s`

Why:

- Warnings are required for readability.
- Low tide warning is important for the final vault.

### 7.5 State Changed Event

Emit:

```js
tide_state_changed
{ state: "LOW" | "RISING" | "HIGH" }
```

Only when state actually changes.

---

## 8. Movement and Stamina

### 8.1 Update Order

Each game update:

```js
function update(dt) {
  if (state.complete) return;

  state.elapsedTime += dt;

  updateTide(dt);

  if (currentTileImpassable()) {
    safeDisplacement();
    return;
  }

  updateMovement(dt);
  updateStamina(dt);

  if (tileChanged) {
    updateFog();
  }

  updateLandmarks();
  updateCaches(dt);
  updateCoins();
  updateVault(dt);
  updateObjectives();
}
```

Why this order:

- Tide can make the current tile impassable.
- The player must be displaced before attempting movement.
- Movement changes tile and stamina.
- World systems react after movement.

### 8.2 Speeds

Current tile depth:

```js
const depth = Math.max(0, waterLevel - currentTile.elevation);
```

Speed rules:

| Condition | Speed |
|---|---:|
| Dry, walking | `3.0` |
| Dry, running, stamina > 0 | `5.0` |
| Shallow water, swimming | `2.0` |
| Shallow water, stamina == 0 | `1.5` |
| Deep water | impassable |

Dry means `depth <= 0`.

Running is only allowed when:

- current tile is dry,
- `stamina > 0`,
- input `run` is true.

### 8.3 Stamina

Max: `100`.

Drain:

- Running: `12 / sec`
- Swimming: `10 / sec`

Regen:

- When not draining: `20 / sec`

Rules:

- If stamina reaches `0`:
  - running disabled,
  - swimming speed becomes `1.5`,
  - player cannot die,
  - player can still move.

Pseudocode:

```js
function updateStamina(dt) {
  let draining = false;

  if (isRunning) {
    state.player.stamina -= CONFIG.stamina.runDrain * dt;
    draining = true;
  } else if (inWater) {
    state.player.stamina -= CONFIG.stamina.swimDrain * dt;
    draining = true;
  }

  if (!draining) {
    state.player.stamina += CONFIG.stamina.regen * dt;
  }

  state.player.stamina = clamp(state.player.stamina, 0, CONFIG.stamina.max);
}
```

### 8.4 Movement Collision

Player position is continuous.

Movement should be axis-separated to avoid corner clipping.

Pseudocode:

```js
function tryMove(dx, dy) {
  if (dx !== 0) moveAxis(dx, 0);
  if (dy !== 0) moveAxis(0, dy);
}
```

For each substep:

- Compute current tile.
- Compute target tile after moving.
- If target is same tile, only check current passability.
- If target is different tile:
  - current tile passable,
  - target tile passable,
  - elevation difference <= 1,
  - target not blocked by active cache blocker.

If blocked, do not move that axis.

Use substeps so high-speed movement does not tunnel through one-tile walls:

```js
const maxStep = CONFIG.movement.substepMax; // 0.1 tiles
```

Why:

- Axis-separated movement is simple and robust.
- Substeps prevent tunneling at `5 tiles/sec`.

### 8.5 Input

Input state:

```js
{
  up: boolean,
  down: boolean,
  left: boolean,
  right: boolean,
  run: boolean,
  map: boolean,
  interact: boolean
}
```

Keyboard mapping:

```text
W / ArrowUp      up
S / ArrowDown    down
A / ArrowLeft    left
D / ArrowRight   right
Shift            run
M                map
Right Mouse      map
E / Enter        interact
```

Right mouse should prevent context menu on the game canvas.

Opening map sets `input.map = true` while held.

Map open cancels active channel.

---

## 9. Safe Displacement

### 9.1 Condition

Check current tile passability every update.

If current tile is impassable:

1. Search for nearest passable tile within `16` tiles.
2. If found:
   - move player there,
   - cancel channel,
   - emit `safe_displacement_occurred`.
3. If not found:
   - if `lastHighSafeTile` exists, move there,
   - otherwise move to start tile,
   - cancel channel,
   - emit `safe_displacement_occurred`.

`lastHighSafeTile`:

- Updated whenever player is on a tile with elevation `>= 1`.
- Start tile is elevation `1` and is the initial fallback.

### 9.2 Search

Use BFS in 4 directions.

Search bounds:

- Chebyshev distance <= `16`.
- Ignore ocean.
- Ignore active blockers.
- Use current water level.
- Target tile must be passable.

The search does not need a full path from the current tile because the current tile is already impassable. The result is a safe destination.

Pseudocode:

```js
function findNearestPassable(level, from, waterLevel, radius, blockers) {
  const queue = [[from.x, from.y, 0]];
  const seen = new Set();

  while (queue.length) {
    const [x, y, dist] = queue.shift();

    if (dist > radius) break;

    if (tilePassable(level, x, y, waterLevel, blockers)) {
      return { x, y };
    }

    for (const [dx, dy] of DIRECTIONS_4) {
      const nx = x + dx;
      const ny = y + dy;
      const key = ny * size + nx;

      if (seen.has(key)) continue;
      seen.add(key);
      queue.push([nx, ny, dist + 1]);
    }
  }

  return null;
}
```

Why:

- The player must never be stranded by tide.
- The displacement should feel like being pushed to higher ground, not death.

---

## 10. Fog of War and Line of Sight

### 10.1 Reveal

When the player enters a new tile, reveal tiles within radius `10`.

Pseudocode:

```js
function revealAround(tileX, tileY) {
  const r = CONFIG.fog.radius;

  for (let dy = -r; dy <= r; dy++) {
    for (let dx = -r; dx <= r; dx++) {
      const x = tileX + dx;
      const y = tileY + dy;

      if (!insideWorld(x, y)) continue;

      const i = y * size + x;
      if (state.tiles.revealed[i]) continue;

      if (hasLineOfSight(playerTile, { x, y })) {
        state.tiles.revealed[i] = 1;
        markMapDirty("revealed");
      }
    }
  }
}
```

Revealed tiles remain revealed forever.

### 10.2 Line of Sight

LOS is from player tile center to target tile center.

Sample every `0.5` tiles.

Blocked if any sampled tile has elevation greater than player tile elevation + `1`.

Water does not block visibility.

Pseudocode:

```js
function hasLineOfSight(from, to) {
  const fromElev = elevationAt(from);
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const dist = Math.hypot(dx, dy);
  const steps = Math.max(1, Math.ceil(dist / CONFIG.fog.losStep));

  for (let s = 1; s <= steps; s++) {
    const t = s / steps;
    const x = Math.floor(from.x + dx * t);
    const y = Math.floor(from.y + dy * t);

    if (!insideWorld(x, y)) return false;

    if (elevationAt({ x, y }) > fromElev + 1) {
      return false;
    }
  }

  return true;
}
```

Why:

- Matches gameplay design.
- Keeps fog simple and testable.

### 10.3 Sector Discovery

A sector is discovered when:

- player tile enters sector bounds, or
- its sector landmark is discovered.

Store:

```js
state.sectors.discovered = Set<sectorId>
```

Emit:

```js
sector_discovered
{ sectorId, sectorName }
```

Show banner once per sector.

---

## 11. Landmarks

### 11.1 Discovery

Every frame, or throttled to at least `10 Hz`:

```js
for each undiscovered landmark:
  if distance(player, landmark) <= 24:
    if hasLineOfSight(playerTile, landmarkTile):
      discover landmark
```

Discovery:

- Add to `state.landmarks.discovered`.
- Emit `landmark_discovered`.
- If landmark is sector landmark:
  - discover sector,
  - emit `sector_discovered`.
- If Key 1 is already collected:
  - reveal corresponding hunt area,
  - emit `hunt_area_revealed`.

### 11.2 Hunt Areas

A hunt area is shown when:

- Key 1 is collected, and
- the sector landmark for that cache sector is discovered, and
- the cache is not collected.

Hunt area:

- radius `24` tiles,
- centered on uncollected cache position,
- shown on map only.

Emit:

```js
hunt_area_revealed
{ sectorId, cacheId }
```

Why:

- Prevents search-fail states.
- Does not reveal exact cache until player is near it.

---

## 12. Caches, Keys, and Channels

### 12.1 Cache Visibility

A cache is visible in the world when:

- not collected,
- player distance to `interact` or `reward` <= `8`,
- line of sight exists to the cache,
- if sealed, it is still visible so the player can see the padlock state.

If visible and player is within `interactRadius`, show context prompt.

### 12.2 Sealed State

Keys 2-5 are sealed until Key 1 is collected.

Prompt:

```text
Sealed. Find the first Tide Key.
```

Emit `cache_sealed_prompt` when player attempts to interact while sealed.

Do not spam the event every frame. Emit once per interaction attempt or once per visibility entry.

### 12.3 Channel State

Active channel:

```js
state.activeChannel = {
  type: "cache" | "vault",
  targetId: string,
  startTime: number,
  duration: number,
  progress: 0
}
```

Channel starts when:

- cache is visible,
- player within interact radius,
- cache is not sealed,
- cache is not opened,
- `input.interact` is true.

Channel cancels when:

- player moves,
- `input.interact` becomes false,
- map is opened,
- safe displacement occurs,
- for vault, tide is no longer low.

Why release cancels:

- The channel represents a physical action.
- If the player stops holding interact, the action should stop.
- This prevents accidental completion while the player is not intentionally interacting.

On cancel:

- emit `channel_cancelled`,
- prompt shows `Cancelled` briefly.

### 12.4 Cache Completion

When cache channel completes:

1. Mark cache `opened` and `collected`.
2. Remove blocker tiles if any.
3. Grant key.
4. Grant `10` coins.
5. Emit events:
   - `cache_opened`
   - `key_collected`
   - `coin_collected`
6. If key has a geometric clue:
   - add clue,
   - increment `geometricCollected`,
   - emit `geometric_clue_added`.
7. If Key 1 collected:
   - unseal keys 2-5,
   - reveal any hunt areas whose landmarks are already discovered.
8. If `geometricCollected === 4`:
   - set `vault.markerRevealed = true`,
   - emit `vault_marker_revealed`.
9. Update objective.

### 12.5 Cache Blocker Removal

When a cache with blockers opens:

```js
for (const tileIndex of cache.blockerTiles) {
  level.blockers.delete(tileIndex);
}

cache.blockerActive = false;
```

Pathfinding and movement use `level.blockers` dynamically.

---

## 13. Coins

### 13.1 Collection

Check every frame or every tile change.

Collect coin when:

- coin not collected,
- player distance to coin center <= `0.5`,
- coin tile is passable for the player.

On collect:

- set `coin.collected = true`,
- increment `state.coins.collected`,
- emit `coin_collected { amount: 1 }`.

Coins do not regenerate.

### 13.2 Rank

Compute at completion:

```js
function rankForCoins(coins) {
  if (coins >= 160) return "Tide Baron";
  if (coins >= 140) return "Master Salvager";
  if (coins >= 100) return "Salvager";
  return "Beachcomber";
}
```

---

## 14. Vault

### 14.1 Prompt Logic

```js
function vaultPrompt() {
  if (state.keys.totalCollected < 5) {
    return "Locked. Requires 5/5 Tide Keys.";
  }

  if (!isLowTide()) {
    return "Sealed by the tide. Wait for low tide.";
  }

  return "Open vault";
}
```

### 14.2 Vault Ready

```js
state.vault.ready =
  state.keys.totalCollected >= 5 &&
  state.tide.waterLevel < CONFIG.tide.lowThreshold;
```

Emit `vault_ready_changed` when ready state changes.

### 14.3 Vault Channel

Channel time: `1.0s`.

Requirements:

- 5/5 keys,
- low tide,
- player near vault,
- interact held.

Cancellation:

- moving,
- map opened,
- interact released,
- safe displacement,
- tide no longer low.

On success:

1. Mark vault `unlocked` and `completed`.
2. Add `70` coins.
3. Enter `GAME_COMPLETE`.
4. Emit:
   - `channel_complete`
   - `vault_opened`
   - `game_complete`
5. Disable input.

### 14.4 Game Complete Event

```js
game_complete
{
  time: state.elapsedTime,
  keys: 5,
  coins: state.coins.collected,
  rank: rankForCoins(state.coins.collected)
}
```

End screen uses this payload.

Restart can reload the page. A full state reset is not required for the single-session design.

---

## 15. Objectives

Objective text is derived from state.

```js
function currentObjective() {
  if (state.complete) return "Treasure found.";

  const keys = state.keys.totalCollected;

  if (keys === 0) return "Open the shipwreck barrel.";
  if (keys >= 5) return "Open the vault at low tide.";

  return `Find the Tide Keys. ${keys}/5`;
}
```

Emit `objective_changed` when text changes.

---

## 16. Rendering Integration

Rendering does not own gameplay logic. It reads state and level, and emits input events.

### 16.1 Canvas Setup

`index.html` should contain:

```html
<canvas id="game" width="1280" height="720"></canvas>
<canvas id="map" width="512" height="512"></canvas>
```

The game canvas should resize to the window while preserving aspect ratio.

The map canvas is shown only when map is open.

### 16.2 Projection

Use the visual designer’s isometric projection:

```js
const ISO = {
  tileW: 48,
  tileH: 24,
  heightStep: 18
};

function isoToScreen(tileX, tileY, elevation, camera, view) {
  const sx = (tileX - tileY) * (ISO.tileW / 2);
  const sy = (tileX + tileY) * (ISO.tileH / 2) - elevation * ISO.heightStep;

  return {
    x: view.width / 2 + sx - camera.x,
    y: view.height / 2 + 24 + sy - camera.y
  };
}
```

Camera:

- follows player,
- smooths position,
- clamps to island bounds,
- no rotation,
- no free zoom,
- scale `1.0` on standard screens,
- scale `0.85` below `800x480` if needed.

### 16.3 Terrain Renderer

`js/render/renderer.js` should handle world rendering.

Render order:

1. Ocean background.
2. Terrain tiles sorted by `tileX + tileY`.
3. Side walls/cliffs.
4. Water overlays.
5. Entities:
   - coins,
   - caches,
   - landmarks,
   - vault,
   - player,
   - effects.

#### 16.3.1 Terrain Pre-rendering

Pre-render tile top canvases:

```text
sector x elevation x optional wet
```

Suggested count:

- 6 sectors
- 6 elevations
- 2 wet variants
- total: `72` small canvases

This is acceptable memory-wise.

Do not generate tile canvases every frame.

#### 16.3.2 Elevation Rendering

For each visible tile:

- Draw top tile.
- If neighbor below has lower elevation:
  - draw side wall.
  - if elevation difference `1`: draw small step/lip.
  - if elevation difference `>=2`: draw cliff face style.

Do not rely on color alone.

#### 16.3.3 Water Overlay

For each visible tile:

```js
const depth = Math.max(0, waterLevel - elevation);

if (depth > 0) {
  drawWaterOverlay(depth);
}
```

Deep water if `depth > 1.0`.

Water overlay should be animated using time and tile position.

#### 16.3.4 Culling

Compute visible tile bounds from viewport corners.

Expand bounds by maximum elevation offset to account for height.

Draw only tiles inside bounds.

Why:

- Keeps frame cost proportional to visible area.
- Prevents drawing the entire 256x256 grid every frame.

### 16.4 Map Renderer

`js/render/mapRenderer.js` owns the map overlay.

Map size:

- `512x512`
- `1 tile = 2px`

Map coordinate:

```js
function tileToMap(x, y) {
  return {
    x: x * 2,
    y: y * 2
  };
}
```

Map layers:

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

#### 16.4.1 Caching

Use dirty flags:

```js
{
  revealed: boolean,
  floodPreview: boolean,
  huntAreas: boolean,
  clues: boolean,
  landmarks: boolean,
  vault: boolean,
  water: boolean,
  player: boolean
}
```

Static layers can be cached in offscreen canvases:

- `terrainLayer`
- `unrevealedLayer`
- `floodPreviewLayer`
- `huntAreaLayer`
- `clueRingLayer`
- `landmarkLayer`
- `vaultLayer`

Dynamic layers:

- water,
- player.

Redraw strategy:

- When map is closed: do not redraw.
- When map is open:
  - redraw static layers only when dirty.
  - redraw water layer at `10-15 FPS` or every frame if performance allows.
  - redraw player every frame.

Why:

- The map is the main puzzle tool.
- It must stay readable and performant.
- Redrawing 65,536 tiles every frame is unnecessary.

#### 16.4.2 Clue Rings

Draw each collected geometric clue:

```js
inner = Math.max(0, D - 6) * 2;
outer = (D + 6) * 2;
```

Use key-specific color and dash style from visual design.

When a clue is added, mark `clues` dirty and animate ring drawing.

#### 16.4.3 Vault Marker

Show when `state.vault.markerRevealed` is true.

- If 5/5 keys and low tide: gold/open style.
- Otherwise: red marker.

### 16.5 HUD Renderer

`js/render/hudRenderer.js` updates DOM elements.

HUD should be DOM-based for text accessibility, with small canvas for tide dial if needed.

Required HUD elements:

- tide dial,
- stamina bar,
- key counter,
- coin counter,
- map button,
- objective text,
- context prompt,
- sector banner,
- tide warning banner,
- start screen,
- end screen.

Update policy:

- Text updates only when state changes.
- Tide dial updates every frame or at `30 FPS`.
- Stamina bar updates when stamina changes.
- Key/coin counters update on events.
- Context prompt updates when interactable state changes.

Why:

- Avoids unnecessary DOM writes.
- Keeps UI responsive.

### 16.6 Context Prompt

Prompt states:

```text
Open barrel
Open low-tide shelf
Pull rope
Move column
Open chest
Sealed. Find the first Tide Key.
Locked. Requires 5/5 Tide Keys.
Sealed by the tide. Wait for low tide.
Open vault
Cancelled
```

While channeling:

- show progress ring,
- show `[E]` icon,
- show prompt text.

Use both text and icon, not color alone.

---

## 17. Audio Implementation

`js/audio/audioManager.js` owns audio.

Audio must be initialized after a user gesture.

Start screen button click is the gesture.

### 17.1 Audio Manager API

```js
const audio = new AudioManager({
  assets: AUDIO_ASSETS,
  enabled: true
});

audio.unlock();
audio.startMusic();
audio.handle(event, payload, game);
audio.stop();
```

### 17.2 Assets and Fallback

The visual designer has provided audio designs.

Engineering implementation should:

1. Attempt to load audio assets if present.
2. If an asset is missing, use a Web Audio synthesized fallback matching the intended sonic shape.

This keeps the game playable even if an asset path is misspelled.

Suggested asset names:

```text
/audio/music_sea.ogg
/audio/music_percussion.ogg
/audio/music_melody.ogg
/audio/sfx/key.ogg
/audio/sfx/coin.ogg
/audio/sfx/cache_sealed.ogg
/audio/sfx/cache_opened.ogg
/audio/sfx/rope.ogg
/audio/sfx/column.ogg
/audio/sfx/tide_warning.ogg
/audio/sfx/low_tide.ogg
/audio/sfx/high_tide.ogg
/audio/sfx/vault_locked.ogg
/audio/sfx/vault_opening.ogg
/audio/sfx/game_complete.ogg
/audio/sfx/landmark.ogg
/audio/sfx/clue.ogg
/audio/sfx/safe_displacement.ogg
/audio/sfx/footstep_dry.ogg
/audio/sfx/footstep_shallow.ogg
/audio/sfx/swim_loop.ogg
/audio/sfx/ui_hover.ogg
/audio/sfx/ui_click.ogg
/audio/sfx/map_open.ogg
/audio/sfx/map_close.ogg
```

### 17.3 Event Mapping

Map events to sounds:

```text
key_collected            -> key
coin_collected           -> coin
cache_sealed_prompt      -> cache_sealed
cache_opened             -> cache_opened
rope interaction         -> rope
column interaction       -> column
tide_warning             -> tide_warning
tide_state_changed LOW   -> low_tide
tide_state_changed HIGH  -> high_tide
vault locked prompt      -> vault_locked
vault_opened             -> vault_opening
game_complete            -> game_complete
landmark_discovered      -> landmark
geometric_clue_added     -> clue
safe_displacement_occurred -> safe_displacement
map_opened               -> map_open
map_closed               -> map_close
ui click                 -> ui_click
```

### 17.4 Music Layers

Use adaptive layers:

- sea bed,
- percussion,
- melody,
- tide accent,
- stingers.

State rules:

| State | Music Behavior |
|---|---|
| Start screen | sea bed + very soft melody |
| Exploration dry | full percussion + melody |
| Shallow water | reduce percussion, increase water wash |
| Deep water blocked | duck music, increase low swell |
| Low tide | add bright celesta layer if available |
| Rising tide | add water swells |
| High tide | add low pulse |
| Vault ready | short bell pulse |
| Vault opening | heavy stinger |
| Game complete | fanfare + gull |

No in-game volume sliders are included.

Why:

- Single-session browser game.
- Browser system volume is sufficient.
- Volume UI adds unneeded scope.

### 17.5 SFX Limits

Maximum simultaneous one-shot SFX: `8`.

Implementation:

- Maintain a pool of active SFX nodes.
- If pool is full, discard lowest-priority SFX.
- Priority:
  1. Key
  2. Vault
  3. Tide
  4. Cache
  5. Coin
  6. Movement
  7. UI

World SFX may be panned by screen position.

UI and tide dial sounds should be centered.

---

## 18. Test Harness

The test harness must validate the game without a browser.

It lives in `tests/harness.js`.

### 18.1 Headless Game Creation

```js
export function createHeadlessGame(options = {}) {
  const level = createLevel(options.seed ?? 123);
  const game = new Game({
    level,
    dt: options.dt ?? 0.016,
    withRenderer: false,
    withAudio: false
  });

  const events = [];

  game.bus.on("*", (event, payload) => {
    events.push({ event, payload });
  });

  return {
    game,
    level,
    state: game.state,
    events,
    input: game.input,
    advance,
    waitFor,
    setTile,
    moveTowards,
    interactWith,
    clearEvents
  };
}
```

### 18.2 Time Control

`advance(seconds)` runs the game loop in fixed steps.

```js
function advance(seconds, dt = game.dt) {
  let remaining = seconds;

  while (remaining > 0) {
    const step = Math.min(dt, remaining);
    game.update(step);
    remaining -= step;
  }
}
```

For playthrough tests, use a larger `dt` such as `0.05` to run faster while still testing tide and movement.

For movement precision tests, use `0.001` to `0.016`.

### 18.3 Waiting

```js
function waitFor(condition, maxSeconds = 60) {
  let elapsed = 0;

  while (!condition() && elapsed < maxSeconds) {
    advance(0.1);
    elapsed += 0.1;
  }

  return condition();
}
```

### 18.4 Input Helpers

```js
function setMovement({ up, down, left, right, run }) { ... }
function clearMovement() { ... }
function pressInteract(durationSeconds) { ... }
function openMap(durationSeconds) { ... }
```

### 18.5 Pathfinding Test Controller

The harness uses the same pathfinding system used by safe displacement, plus A* for longer paths.

`moveTowards(tile, options)`:

1. Computes current player tile.
2. Uses `findPath` with current water level and current blockers.
3. If no path:
   - waits up to `options.waitSeconds` for tide or blockers to change,
   - retries.
4. Follows path by setting movement input.
5. Recomputes path when player tile changes significantly.
6. Returns true when within one tile of target.

`interactWith(cache)`:

1. Finds the nearest passable tile within `interactRadius` of `cache.interact`.
2. Moves there.
3. Holds interact for `cache.channelTime + 0.2` seconds.
4. Returns true when cache is opened.

Why:

- This simulates a real player route.
- It tests tide waiting, movement, interaction, and progression together.
- It does not teleport the player magically.

### 18.6 Event Recording

The harness records all events.

Tests should assert event order where important.

Example:

```js
assert(
  events.some(e => e.event === "key_collected" && e.payload.keyId === 1)
);
```

For ordered events, use:

```js
function eventsInOrder(events, names) { ... }
```

---

## 19. Required Unit Tests

Each test file should be small and focused.

### 19.1 `tide.test.js`

Assert:

- `waterLevelAt(0) === 0`
- `waterLevelAt(60) === 2`
- `waterLevelAt(120) === 0`
- state is `LOW` at low water
- state is `HIGH` at high water
- state is `RISING` between thresholds
- `tide_state_changed` emits only on actual changes
- `tide_warning` emits 10 seconds before thresholds
- no duplicate warnings within the same cycle

### 19.2 `passability.test.js`

Assert:

- elevation `0` is passable at water level `0`
- elevation `0` is impassable at water level `2`
- elevation `1` is passable at water level `2`
- elevation `2` is passable at water level `2`
- depth calculation is correct
- ocean border is impassable
- elevation difference `1` is walkable
- elevation difference `2` is not walkable
- active blockers are impassable
- removed blockers become passable

### 19.3 `movement.test.js`

Assert:

- dry walking speed is approximately `3.0`
- running speed is approximately `5.0`
- running does not occur in water
- swimming speed is approximately `2.0`
- low-stamina swimming speed is `1.5`
- blocked movement does not change position
- diagonal movement does not clip through corners
- high-speed movement does not tunnel through one-tile cliffs

### 19.4 `stamina.test.js`

Assert:

- running drains `12/sec`
- swimming drains `10/sec`
- stamina regens `20/sec` when not draining
- stamina clamps to `0`
- running disabled at `0`
- walking still possible at `0`

### 19.5 `safeDisplacement.test.js`

Assert:

- if current tile becomes deep water, player moves to nearest passable tile
- channel cancels on displacement
- if no local tile exists, player moves to `lastHighSafeTile`
- if no `lastHighSafeTile`, player moves to start
- displacement emits event

### 19.6 `fog.test.js`

Assert:

- entering a tile reveals radius `10`
- revealed tiles persist
- LOS is blocked by elevation greater than player + 1
- water does not block LOS
- no tiles outside radius are revealed

### 19.7 `landmarks.test.js`

Assert:

- landmark within 24 and LOS is discovered
- landmark beyond 24 is not discovered
- landmark without LOS is not discovered
- discovery emits event
- sector landmark discovery discovers sector
- hunt area reveals after Key 1 and landmark discovery

### 19.8 `caches.test.js`

Assert:

- Key 1 available at start
- Keys 2-5 sealed before Key 1
- sealed cache emits sealed prompt on interact
- after Key 1, other caches are available when visible
- channel completes after required time
- moving cancels channel
- opening map cancels channel
- releasing interact cancels channel
- opened cache remains open
- blockers removed after cache opens
- key and 10 coins granted
- geometric clue added for Keys 1-4
- no clue added for Key 5

### 19.9 `coins.test.js`

Assert:

- walking over coin collects it
- coin does not regenerate
- total coin count increments
- rank thresholds are correct
- completion works with zero coins
- total possible coin count is 160

### 19.10 `vault.test.js`

Assert:

- vault locked with less than 5 keys
- vault sealed by tide with 5 keys but not low tide
- vault prompt is open with 5 keys and low tide
- vault channel completes only at low tide
- tide rising cancels vault channel
- moving cancels vault channel
- map opening cancels vault channel
- success grants 70 coins
- success emits `game_complete`
- completion disables input

### 19.11 `clues.test.js`

Assert:

- authored distances match rounded landmark-to-vault distances
- 0 clues shows no rings
- 1 clue adds one ring
- 4 clues reveal vault marker
- overlap contains vault
- overlap size is below `400`
- clue ring data is correct for Keys 1-4
- Key 5 does not add a clue

### 19.12 `levelGenerator.test.js`

Assert:

- generated level is `256x256`
- ocean border is impassable
- start exists
- vault exists
- all landmarks exist
- all caches exist
- low tide BFS reaches all cache interact tiles
- low tide BFS reaches all landmarks
- low tide after blockers removed reaches all cache rewards and vault
- high tide BFS reaches all high anchors
- high-tide passable tiles are connected to start
- clue validation passes
- coin placement passes
- seeded caches remain valid
- invalid seed variation falls back to default
- fallback level is always valid

### 19.13 `events.test.js`

Assert:

- all major events exist
- event payloads match contract
- no unknown events are required for renderer/audio
- `game_complete` payload includes time, keys, coins, rank

### 19.14 `audio.test.js`

Use a stub `AudioContext`.

Assert:

- audio unlock required before start
- `key_collected` triggers key sound
- `coin_collected` triggers coin sound
- `tide_warning` triggers warning sound
- `vault_opened` triggers vault sound
- SFX pool limits simultaneous sounds
- missing assets fall back to synth without throwing

---

## 20. Playthrough Test

`tests/playthrough.test.js` is the primary proof that the game is finished and playable.

It should run headlessly.

Test outline:

```js
test("full headless playthrough completes", () => {
  const harness = createHeadlessGame({ seed: 123, dt: 0.05 });
  const { game, advance, moveTowards, interactWith } = harness;

  game.start();

  // Start state
  assert(game.state.progress === "START");
  assert(game.state.keys.totalCollected === 0);

  // Key 1
  assert(interactWith(level.caches.find(c => c.keyId === 1), { advance, moveTowards }));
  assert(game.state.keys.totalCollected === 1);
  assert(game.state.keys.geometricCollected === 1);
  assert(game.state.coins.collected >= 10);

  // Keys 2 through 5
  for (const keyId of [2, 3, 4, 5]) {
    const cache = level.caches.find(c => c.keyId === keyId);

    if (keyId === 2) {
      waitFor(() => game.state.tide.waterLevel < CONFIG.tide.lowThreshold, 120);
    }

    assert(interactWith(cache, { advance, moveTowards }));
    assert(game.state.keys.totalCollected === keyId);
  }

  assert(game.state.keys.totalCollected === 5);
  assert(game.state.keys.geometricCollected === 4);
  assert(game.state.vault.markerRevealed === true);

  // Vault
  const vaultReached = moveTowards(level.vault, {
    waitSeconds: 180,
    requireLowTide: true
  });

  assert(vaultReached);

  const vaultCache = {
    interact: level.vault,
    channelTime: 1.0
  };

  assert(interactWith(vaultCache, { advance, moveTowards }));

  assert(game.state.complete === true);
  assert(game.state.coins.collected >= 70);
  assert(game.state.coins.collected <= 160);

  const completeEvent = harness.events.find(e => e.event === "game_complete");
  assert(completeEvent);
  assert(completeEvent.payload.keys === 5);
  assert(completeEvent.payload.coins === game.state.coins.collected);
});
```

Additional playthrough tests:

### 20.1 Multiple Seeds

Run the playthrough with at least these seeds:

```text
1
7
42
123
999
```

Why:

- Seeded cache and coin variation must not break completion.

### 20.2 Completion Time

Assert elapsed simulated time is less than a generous upper bound.

Recommended:

```js
assert(game.state.elapsedTime < 30 * 60);
```

Why:

- Design target is 15-25 minutes.
- Automated pathing may be faster or slower depending on tide waiting.
- `30` minutes gives margin while still catching broken pacing.

### 20.3 No Soft-Lock

Assert:

- no exceptions,
- player position remains inside world,
- current tile is passable after each update,
- safe displacement, if used, does not lose keys or coins,
- game reaches `GAME_COMPLETE`.

### 20.4 Event Order

Assert major events appear in a valid order:

```text
game_start
key_collected keyId 1
key_collected keyId 2
key_collected keyId 3
key_collected keyId 4
key_collected keyId 5
geometric_clue_added keyId 1
geometric_clue_added keyId 2
geometric_clue_added keyId 3
geometric_clue_added keyId 4
vault_marker_revealed
vault_opened
game_complete
```

Note: clue events may interleave with key events. Tests should check relative order, not exact frame order.

---

## 21. Browser E2E Smoke Test

Optional but recommended.

`tests/e2e/smoke.spec.js` should verify the real page boots.

Checks:

1. Page loads without console errors.
2. Start screen is visible.
3. Clicking **Begin Salvage**:
   - hides start screen,
   - shows game canvas,
   - starts audio context.
4. Pressing movement keys changes player position.
5. Holding `M` opens map.
6. Releasing `M` closes map.
7. HUD elements exist:
   - tide dial,
   - stamina bar,
   - key counter,
   - coin counter,
   - objective text.
8. Interacting near first cache completes channel if player is positioned there.
9. No unhandled promise rejections.

This test does not need to play the full game. The headless playthrough already proves completion.

---

## 22. Performance Requirements

Targets:

- `60 FPS` on mid-range browser hardware.
- No dynamic lighting.
- No post-processing.
- No free 3D navigation.
- No full-screen blur.
- Limited particles.

Implementation rules:

- Pre-render terrain tiles.
- Cull invisible tiles.
- Avoid allocating large arrays every frame.
- Use typed arrays for tile data.
- Reuse BFS queues where practical.
- Update HUD text only on state changes.
- Redraw map layers only when dirty.
- Limit active SFX nodes to `8`.
- Use one sea loop instead of many water sounds.
- Avoid per-frame DOM creation.

Memory expectations:

- elevation: `65,536` bytes
- ocean: `65,536` bytes
- sector: `65,536` bytes
- revealed: `65,536` bytes
- coins: tiny
- caches: tiny

This is well within browser limits.

---

## 23. Edge Cases and Recovery

Engineering must implement these recovery rules.

| Case | Implementation |
|---|---|
| Player reaches sealed cache before Key 1 | Prompt sealed, no channel |
| Player has 4 keys but not fifth | Vault marker may show, vault remains locked |
| Player reaches vault early | Prompt locked or sealed by tide |
| Player becomes deep water | Safe displacement |
| No local safe tile | Teleport to `lastHighSafeTile` |
| No `lastHighSafeTile` | Teleport to start |
| Player has 0 stamina | Can walk or swim slowly |
| Player tries to enter deep water | Movement blocked |
| Player tries to climb 2+ elevation | Movement blocked |
| Player opens map during channel | Channel cancels |
| Player moves during channel | Channel cancels |
| Player releases interact during channel | Channel cancels |
| Tide rises during vault channel | Vault channel cancels |
| Level validation fails | Use fallback level |
| Seeded cache invalid | Use default cache position |
| Seeded coin placement invalid | Use deterministic fallback coins |
| Audio asset missing | Use synth fallback |
| Audio context blocked | Unlock on start button |

---

## 24. Cuts

These are intentionally not included.

| Cut | Reason |
|---|---|
| Save system | Single 15-25 minute session |
| Camera rotation | Isometric readability |
| Free zoom | Performance and UI clarity |
| Dynamic lighting | Tide and elevation are the visual focus |
| Day/night | Cut by gameplay |
| Weather | Tide is the environmental pressure |
| Combat | Cut by gameplay |
| Health/death | Cut by gameplay |
| Inventory | Keys and coins are automatic |
| NPCs | Cut by gameplay |
| Vehicles | Cut by gameplay |
| Multiplayer | Cut by gameplay |
| Volume sliders | Browser volume is sufficient |
| Full 3D | 2.5D is clearer and cheaper |
| Procedural critical path | Must remain guaranteed completable |

---

## 25. Acceptance Criteria

The game is engineering-complete when all of the following are true.

### 25.1 Tests

- `npm test` passes.
- `npm run test:unit` passes.
- `npm run test:play` passes.
- Playthrough passes for multiple seeds.
- No known soft-lock paths remain.
- Fallback level is used only when validation fails.

### 25.2 Gameplay Completion

- Player can start in Driftwood Cove.
- Player can collect all five keys.
- Four geometric clues appear.
- Vault marker appears after four geometric clues.
- Vault opens at low tide with five keys.
- End screen shows rank, time, coins, and keys.

### 25.3 Readability

- Dry, shallow, and deep water are visually distinct.
- Elevation difference `1` is walkable.
- Elevation difference `2+` is visually and mechanically blocked.
- Tide state is readable with icon, text, and color.
- Stamina is readable.
- Key counter is readable.
- Map shows:
  - revealed terrain,
  - current water,
  - high-tide flood preview,
  - landmarks,
  - hunt areas,
  - clue rings,
  - vault marker,
  - player,
  - legend.

### 25.4 Audio

- Audio starts after user gesture.
- Key sound is distinct.
- Coin sound is distinct.
- Tide warning is distinct from tide state change.
- Vault sound is distinct.
- Missing assets do not crash the game.

### 25.5 Performance

- Game runs at target frame rate on mid-range hardware.
- Map does not cause frame drops when open.
- No full-screen post-processing.
- No dynamic lighting.
- No unbounded particle growth.

---

## 26. Integration Checklist for Other Agents

The integrator should verify:

1. All files exist.
2. Core logic imports do not touch `document` or `window`.
3. `Game` can run headlessly.
4. Level generator returns a valid level.
5. Renderer consumes level and state without mutating gameplay.
6. Audio consumes events without mutating gameplay.
7. HUD updates from state and events.
8. Map cache invalidation works.
9. Safe displacement works.
10. Playthrough test completes.
11. No gameplay constants were changed from `gameplay.md`.
12. No visual requirements were removed from `visual.md`.