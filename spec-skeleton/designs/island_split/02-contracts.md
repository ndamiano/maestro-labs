# 2. CONTRACTS

## 2.1 Module layout

```text
/
  index.html
  package.json
  css/main.css
  js/
    main.js
    config/constants.js
    core/eventBus.js
    core/rng.js
    core/geometry.js
    core/tilemap.js
    core/pathfinding.js
    core/state.js
    core/game.js
    level/layout.js
    level/generator.js
    level/validator.js
    systems/tide.js
    systems/movement.js
    systems/fog.js
    systems/landmarks.js
    systems/caches.js
    systems/coins.js
    systems/vault.js
    systems/objectives.js
    render/renderer.js
    render/mapRenderer.js
    render/hudRenderer.js
    audio/audioManager.js
  tests/harness.js
  tests/unit/  (tide, passability, movement, stamina, safeDisplacement, fog,
                landmarks, caches, coins, vault, clues, levelGenerator, events,
                audio)
  tests/playthrough.test.js
  tests/e2e/smoke.spec.js
```

`package.json`:
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
No runtime dependencies. `main.js` runs only in the browser: read DOM/canvas → create level → create headless `Game` → create renderer/HUD/audio → show start screen → on **Begin Salvage**: unlock audio, start loop, enable input. Core logic (everything but `render/`, `audio/`, `main.js`) never touches `document`/`window` and runs headlessly.

## 2.2 Global context

One runtime global, `GLOBAL = { CONFIG, LEVEL, STATE, BUS, rng }`. Every field a §4 rule reads or writes and every value a §9 test asserts lives here (verified in §A).

**`CONFIG`** (export of `config/constants.js`, mirrors §4 Core Constants):
```js
export const CONFIG = {
  size: 256,
  oceanBorder: 8,
  maxElevation: 5,

  tide: { period: 120, lowThreshold: 0.7, highThreshold: 1.3, passableDepth: 1.0, warningSeconds: 10 },

  movement: { walk: 3.0, run: 5.0, swim: 2.0, lowStaminaSwim: 1.5, substepMax: 0.1 },

  stamina: { max: 100, runDrain: 12, swimDrain: 10, regen: 20 },

  fog: { radius: 10, losStep: 0.5 },

  landmarks: { visibleDistance: 24 },

  caches: { visibleDistance: 8, interactRadius: 1.5, huntRadius: 24 },

  clues: { width: 6, maxOverlapTiles: 400 },

  safeDisplacement: { radius: 16 },

  coins: { total: 160, scatteredPerSector: 8, perCache: 10, vault: 70 },

  map: { tilePx: 2, maxPx: 512 }
};
```

**`LEVEL`** (created once at boot; immutable except runtime sets `blockers` and coin/cache `collected` flags):
```js
{
  seed: 123,
  size: 256,
  elevation: Uint8Array(65536),   // 0..5
  ocean:     Uint8Array(65536),   // 1 = ocean border
  sector:    Uint8Array(65536),   // sector index, 0 = ocean
  start:  { x: 32,  y: 220 },
  vault:  { x: 208, y: 192 },
  landmarks: [ /* 6, §4.4 roster */ ],
  caches:    [ /* 5, §4.5 roster */ ],
  coins:     [ /* 40 scattered, §4.6 roster */ ],
  highAnchors: [ /* 6, §4.4 roster */ ],
  blockers: Set(),                // dynamic tile indices (cache physical blockers)
  validation: { ok: true, fallbackUsed: false, errors: [] }
}
```
Tile index helpers: `index = y * size + x`; `x = index % size`; `y = Math.floor(index / size)`.

**`STATE`** (mirrors gameplay §13 + engineering §3.6):
```js
{
  progress: "START",          // §4.9 roster
  elapsedTime: 0,
  player:  { x: 32.5, y: 220.5, tileX: 32, tileY: 220, facing: "down", stamina: 100 },
  tide:    { time: 0, waterLevel: 0, state: "LOW" },
  keys:    { totalCollected: 0, geometricCollected: 0, collected: Set(), clues: [] },
  coins:   { collected: 0 },
  vault:   { markerRevealed: false, ready: false, unlocked: false, completed: false },
  tiles:   { revealed: Uint8Array(65536) },
  landmarks: { discovered: Set() },   // of landmark id (string)
  sectors:   { discovered: Set() },   // of sector id (string)
  caches:    { collected: Set(), opened: Set() },
  activeChannel: null,           // §4.5 channel object when channeling
  lastHighSafeTile: { x: 32, y: 220 },
  input: { up:false, down:false, left:false, right:false, run:false, map:false, interact:false },
  complete: false
}
```

**`BUS`** (event bus):
```js
class EventBus {
  constructor(){ this.listeners = new Map(); }
  on(ev, fn){ if(!this.listeners.has(ev)) this.listeners.set(ev, []);
              this.listeners.get(ev).push(fn); return () => this.off(ev, fn); }
  off(ev, fn){ const a = this.listeners.get(ev); if(!a) return;
               const i = a.indexOf(fn); if(i>=0) a.splice(i,1); }
  emit(ev, payload = {}){ const a = this.listeners.get(ev); if(!a) return;
                          for (const fn of a.slice()) fn(payload); }
}
```
`BUS` also supports a `*` wildcard used by the test recorder. Events are the integration seam; renderer/audio/HUD subscribe, and only `Game`/`Input` mutate state.

**`rng`** = `mulberry32(GLOBAL_LEVEL_seed)` (§2.3).

## 2.3 Module specifics

Each module exports exactly the functions a §4 rule or §9 test needs. Signatures use `GLOBAL` implicitly.

- **`core/rng.js`** — `mulberry32(seed) → fn()→float[0,1)`:
  ```js
  function mulberry32(seed){ let a = seed>>>0;
    return function(){ a|=0; a=(a+0x6D2B79F5)|0;
      let t=Math.imul(a^(a>>>15), 1|a);
      t=(t+Math.imul(t^(t>>>7), 61|t))^t;
      return ((t^(t>>>14))>>>0)/4294967296; }; }
  ```
- **`core/geometry.js`** — `euclideanDistance(a,b)`, `chebyshev(a,b)`, `tileIndex(x,y,size)`, `indexToXY(i,size)`, `isoToScreen(...)`, `tileToMap(...)`, `clamp(v,lo,hi)`.
- **`core/tilemap.js`** — `elevationAt(level,x,y)`, `depthAt(level,x,y,waterLevel) = max(0, waterLevel - elevation)`, `insideWorld(x,y,size)`, `tilePassable(level,x,y,waterLevel,blockers)` (false if ocean or blocked; else `depthAt <= CONFIG.tide.passableDepth`), `canMoveBetween(level,a,b,waterLevel,blockers)` (both passable **and** `abs(elevB - elevA) <= 1`).
- **`core/pathfinding.js`** — `findNearestPassable(level,from,waterLevel,radius,blockers)` (4-dir BFS, Chebyshev ≤ radius, current tile already impassable), `findPath(level,from,to,waterLevel,blockers)` (A* for the test controller).
- **`core/state.js`** — `createState(level) → STATE`.
- **`core/game.js`** — `class Game { constructor({level, dt, withRenderer, withAudio}); start(); update(dt); get state; get input; get bus }` implementing the §1.2 order.
- **`level/layout.js`** — `LAYOUT` (§4.1 data: sectors with bounds + highAnchor/lowAnchor, landmarks, caches, vault, start, highAnchors, default blocker tiles).
- **`level/generator.js`** — `createLevel(seed=123)`, `createFallbackLevel()`, and internal `buildBaseLevel`, `applySectorBaseFeatures`, `applyRequiredPointElevations`, `carveGuaranteedRoutes`, `addDecorativeHighGround`, `applySeededCacheVariation(level,rng)`, `placeScatteredCoins(level,rng)`, `applyBlockers(level)` (algorithms in §4.1).
- **`level/validator.js`** — `validateLevel(level) → {ok, fallbackUsed, errors}`, `waterLevelAt(t)`, `tideState(waterLevel)`, `tideThresholdTimes() → [4 times]`, `reachableFrom(level,start,{waterLevel,removeBlockers}) → Set<index>`, `validateClues(level) → {ok, overlapCount, vaultInOverlap, distances[]}`, `validateCoins(level)`.
- **`systems/tide.js`** — `updateTide(dt)`, `waterLevelAt(t)`, `tideState(wl)`, `isLowTide() (STATE.tide.waterLevel < 0.7)`, warning/state-change emission.
- **`systems/movement.js`** — `updateMovement(dt)` (axis-separated, substepped), `updateStamina(dt)`, `tryMove(dx,dy)`.
- **`systems/fog.js`** — `updateFog()`, `revealAround(tileX,tileY)`, `hasLineOfSight(from,to)`, `discoverSector(sectorId)`.
- **`systems/landmarks.js`** — `updateLandmarks()` (discovery + hunt-area reveal).
- **`systems/caches.js`** — `updateCaches(dt)`, channel start/cancel/complete, blocker removal, key/coin/clue grant.
- **`systems/coins.js`** — `updateCoins()`, `rankForCoins(coins)`.
- **`systems/vault.js`** — `updateVault(dt)`, `vaultPrompt()`, `setVaultReady()`.
- **`systems/objectives.js`** — `currentObjective()`, `updateObjectives()`.
- **`render/renderer.js`** — world rendering (§3), reads `LEVEL`/`STATE`, emits input only.
- **`render/mapRenderer.js`** — map overlay (§3 map), dirty-flag layer caching.
- **`render/hudRenderer.js`** — DOM HUD (§7), updates on state change / events.
- **`audio/audioManager.js`** — `unlock()`, `startMusic()`, `handle(event,payload,game)`, `stop()`; event→sound table (§6); SFX pool (max 8).
- **`main.js`** — browser boot (§2.1).

**Event contract (union of gameplay §13 + engineering §4).** Core: `game_start`, `landmark_discovered{landmarkId}`, `sector_discovered{sectorId,sectorName}`, `cache_sealed_prompt{cacheId,prompt}`, `cache_opened{cacheId}`, `key_collected{keyId,totalCollected,geometricCollected}`, `geometric_clue_added{keyId,landmarkId,distance}`, `coin_collected{amount,totalCollected}`, `hunt_area_revealed{sectorId,cacheId}`, `vault_marker_revealed{x,y}`, `vault_unlocked{x,y}`, `tide_warning{threshold,secondsUntil}`, `tide_state_changed{state}`, `safe_displacement_occurred{fromTile,toTile,reason}`, `vault_opened{x,y}`, `game_complete{time,keys,coins,rank}`. Implementation: `map_opened`, `map_closed`, `channel_started{type,targetId,duration}`, `channel_cancelled{type,targetId,reason}`, `channel_complete{type,targetId}`, `vault_ready_changed{ready}`, `objective_changed{text}`. Events are emitted, not returned; systems never depend on return values.
