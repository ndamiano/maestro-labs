# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Open-world game: explore an island *(request)* | §3 space; §4.1 World & Level; §4.4 Sectors roster |
| Find treasure *(request)* | §4.7 Final Vault; §5 Vault; §7 End screen; §6 `game_complete` |
| 2.5D isometric, fixed non-rotating camera *(added)* | §1.1; §3 projection; §4.2 |
| Five Tide Keys + distance clue rings that locate the vault *(added)* | §4.5 Caches/Keys/Clues; §4.5 clue roster; §3 map clue rings |
| Continuous tide with low/high states and safe displacement *(added)* | §4.3 Tide & Safe Displacement; §3 water/tide rendering |
| Hoard Map: fog of war, landmarks, hunt areas, vault marker *(added)* | §4.4 Hoard Map/Fog/Landmarks; §3 map overlay |
| Stamina-based movement; no health, no combat *(added)* | §4.2 Movement & Stamina |
| Optional coin score + end rank *(added)* | §4.6 Coins & Score |
| Web Audio–generated SFX + adaptive music *(added)* | §6 Audio |
| HUD, start screen, end screen *(added)* | §7 UX |
| Deterministic authored level + validation + fallback *(added)* | §2.3 generator/validator; §4.1; §9 |
| Headless test suite + single-seed playthrough proof *(added)* | §8 Debug API; §9 Tests; §10 |

## 0.2 Decisions

Topic · gameplay said · visual said · engineering said · **Ruling (clause why)**.

| Topic | gameplay | visual | engineering | Ruling |
| --- | --- | --- | --- | --- |
| Middle tide-state name | "Rising/Mid" (0.7–1.3) | "RISING" | `tideState()` → "RISING" | **Name it `RISING`.** State is one string used by HUD, music and events; two docs already agree. |
| Audio source | lists 11 events | asset categories + synth examples | "attempt load, else synth fallback" | **All audio synthesized at runtime via Web Audio API; no external audio asset files are loaded.** The §6 table is a generation recipe set; keeps the bundle self-contained. |
| Coin SFX pitch | — | table "1200–1800 Hz" vs code "1400 + rand·500" | — | **1200–1800 Hz.** The table is the readable spec; the code sample was illustrative. |
| Shipped seed | — | — | `createLevel(seed=12345)`, harness default 123 | **Shipped build uses fixed seed 123.** Deterministic default island; other seeds are T3 tests/debug. |
| Fixed timestep | — | — | harness `dt` 0.016 / 0.05 | **Browser runs a 60 Hz fixed-step accumulator (`dt = 1/60` s); the harness `advance(sec, dt)` uses a caller-supplied `dt` (default `1/60`, playthrough uses 0.05).** Stable in browser and headless. |
| Player facing count | — (no facing spec) | "walk/run/swim 4 directions" | 4-axis input booleans | **4 facings (N/E/S/W) from dominant velocity axis; horizontal wins ties.** Matches the authored 4-dir animation set. |
| High-tide flood preview | — | §9.1 "optional" but §9.5 "important" | required map layer + dirty flag | **Required map layer (not optional).** Engineering validates it; it is core to tide planning. |
| Cache open sound | — | generic `cache_opened` + specific `rope_pulled`/`column_moved` | maps both `cache_opened` and `rope`/`column` | **Key 3 → `rope_pulled`, Key 4 → `column_moved`, Keys 1/2/5 → `cache_opened` (per-prop variant).** Sound follows the physical action. |
| Vault open: function vs cinematic | functional open + complete | 9-step cinematic | functional open + events | **T1 = functional open (events + state + complete). T2 = full cinematic.** Completion must ship; the cinematic is a flourish. |
| Music depth | 11 event cues | full 5-layer adaptive + motifs | 5 layers | **T1 = sea bed + event stingers. T2 = full adaptive layers + sector motifs.** Silence is acceptable to ship; full music elevates. |
| Start-screen controls | E/Enter, M/Right Mouse | E, M/Right Mouse (omits Enter) | E/Enter, M/Right Mouse | **Full set: Move WASD/Arrows, Run Shift, Interact E/Enter, Map M/Right Mouse.** gameplay+engineering agree on the full set. |
| SCREENSHOTS table | — | none (only §16 checklist) | — | **Integrator constructs the SCREENSHOTS table (§9) from visual §16 checklist + defined states.** Template requires it; checklist items become screenshot rows. |
| Tide threshold times | — | — | approximate (24.194/36.033/83.967/95.806) | **Use exact values from the agreed formula (24.182/35.823/84.182/95.818 s), computed at runtime.** The formula is authoritative; doc values were rounded. |
| Start / Shipwreck / Key-1 elevations | (implied dunes=1; no value for these tiles) | — | start elev 1; shipwreck elev 1; key1 elev 1 | **Start (32,220) elev 1; Shipwreck (40,210) elev 1; Key-1 barrel (45,208) elev 1.** engineering owns the numbers; start elev 1 makes it a valid high-safe tile. |
| Interact radius | "stand near" | — | 1.5 tiles | **1.5 tiles.** engineering owns the number. |
| Movement substep | — | — | 0.1 tile | **0.1 tile.** Prevents tunneling at 5 tiles/s. |
| End-screen restart | — | "optional restart button" | "reload the page" | **Include a Restart button that reloads the page.** Trivial UX; single-session design needs no state reset. |
| Random source | — | — | `mulberry32(seed)` | **Single PRNG `mulberry32(seed)`; only level generation draws from it, in a fixed order (cache offsets keys 2–5, then scattered coins per sector).** No `Math.random` in gameplay (coin-pitch jitter is cosmetic). |
| Map world visibility | — | 92% opaque, 8% world | — | **Carry 92% opaque / 8% world.** Single agreed value; tide warnings stay readable. |

## 0.3 Tiers

**T1 — the game that must ship (by system name):** World & Level; Movement & Stamina; Tide & Safe Displacement; Hoard Map / Fog / Landmarks / Hunt Areas; Caches / Keys / Channels / Clue Rings; Coins & Score; Final Vault (functional); Objectives; HUD (persistent + start + end + map overlay + banners); Audio (SFX one-shots + sea bed + event stingers); Input & Controls; Core test suite (unit + single-seed playthrough).

**T2 — stage after T1 (each line independent, in this order):**
1. Adaptive music: full 5 layers (sea bed + percussion + melody + tide accent + stingers) with adaptive state rules.
2. Sector discovery banners + two-note sector motifs.
3. Collection flourishes: coin/key fly-to-counter animations + bursts.
4. Safe-displacement animation (ripple + splash + "Tide pushed you").
5. Vault opening cinematic (door opens, light spills, water drains, treasure burst, compass rises, fade).
6. Landmark discovery flourish (golden outline + map stamp + brass pin).

**T3 — stage after T2 (each line independent, in this order):**
1. Small-screen support (800×480, HUD scale 0.85, safe area).
2. Decorative world richness (gull shadows, eagle, wind streaks, reef coral, tide-line on exposed sand).
3. Multi-seed playthrough (seeds 1, 7, 42, 123, 999) + completion-time bound (< 30 min) + event-order assertions.
4. Browser E2E smoke test.
5. Performance optimization pass (pre-rendered tile atlases, map offscreen layer caching, culling, SFX pool) + 60 FPS profiling.
6. End-screen confetti (gold + foam) + rank icons.

Every §4 system is tagged with its tier where specified (all T1).

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- **Unit:** 1 tile = 1 meter = 1 world unit. Player and entity positions are tile-space floats.
- **Axes:** `x` increases right, `y` increases down (world and screen). Tile `(x, y)` occupies `[x, x+1] × [y, y+1]`; tile center is `(x+0.5, y+0.5)`. `tileX = Math.floor(player.x)`, `tileY = Math.floor(player.y)`.
- **Origin:** tile `(0,0)` is top-left. The island is inside an **8-tile ocean border** (tiles `0..7` and `248..255` on each axis are ocean, impassable).
- **Projection (isometric):** `TILE_W = 48 px`, `TILE_H = 24 px`, `HEIGHT_STEP = 18 px`. One tile = one meter; the visual tile is an isometric diamond.
  ```js
  const TAU = Math.PI * 2;
  const ISO = { tileW: 48, tileH: 24, heightStep: 18 };
  function isoToScreen(tileX, tileY, elevation, camX, camY, viewW, viewH, scale = 1) {
    const sx = (tileX - tileY) * (ISO.tileW / 2) * scale;
    const sy = (tileX + tileY) * (ISO.tileH / 2) * scale - elevation * ISO.heightStep * scale;
    return { x: viewW / 2 + sx - camX, y: viewH / 2 + 24 + sy - camY };
  }
  ```
- **Camera:** fixed isometric. Follows the player with slight smoothing and a small dead zone; keeps the player near center; clamps to island bounds; **no rotation, no free zoom**; scale `1.0` on standard screens, `0.85` below `800×480`.
- **Map space:** `1 tile = 2 px`, canvas max `512×512 px` (see §3 map).
  ```js
  function tileToMap(tileX, tileY, scale = 2) { return { x: tileX * scale, y: tileY * scale }; }
  ```
- **Frames:** fixed-step loop, 60 Hz accumulator, `dt = 1/60` s; clamp the accumulator to avoid spiral-of-death. The headless harness advances with a caller-supplied `dt`.

## 1.2 Important conventions

- **Units / axes / origin / camera / fixed-step:** as §1.1.
- **Order systems run (per `Game.update(dt)`), authoritative:**
  1. if `state.complete` → return
  2. `state.elapsedTime += dt`
  3. `updateTide(dt)`
  4. if current tile is impassable → `safeDisplacement()` → return
  5. `updateMovement(dt)`
  6. `updateStamina(dt)`
  7. if player tile changed → `updateFog()`
  8. `updateLandmarks()`
  9. `updateCaches(dt)`
  10. `updateCoins()`
  11. `updateVault(dt)`
  12. `updateObjectives()`
  (Ruling: step 4 runs immediately after tide and before movement, per engineering §8.1; the §2.2 layering list is the system *set*, the function order above is canonical.)
- **The one random source:** `rng = mulberry32(seed)` (§2.3 `core/rng.js`). Only `level/generator.js` draws from it, in this fixed order: (a) cache offsets for keys 2,3,4,5 (dx,dy each), (b) scattered coins per sector in fixed sector order. No gameplay `Math.random` (coin-pitch audio jitter is cosmetic only).
- **Controls table (merged):**

| Input | Action |
| --- | --- |
| W / ArrowUp | move up |
| S / ArrowDown | move down |
| A / ArrowLeft | move left |
| D / ArrowRight | move right |
| Shift | run (hold) |
| M **or** Right Mouse | open map (hold) |
| E / Enter | interact (hold) |

Right Mouse suppresses the context menu on the game canvas. Holding map open sets `input.map = true` and cancels any active channel.

- **Constants:** the authoritative numeric table is the **Core Constants record in §4**. The JS export object that mirrors it is `CONFIG` (§2.2).

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

# 3. VISUAL SPEC

**The look — one paragraph.** *Island of the Hidden Hoard* is a **salt-light salvage chart**: a hand-inked island chart brought to life. Bright, clean, hand-painted, chunky, nautical, warm, and clearly readable — sunny, slightly weathered, inviting, never hostile. The island has warm sandy beaches, clear teal water, lush-but-readable jungle, sun-bleached stone ruins, rocky cliffs with strong silhouettes, and brass/rope/wood salvage props. The player is a careful salvager, not a combat explorer. It should read like a bright salvage chart, not a mysterious dark island; details decorate but never hide gameplay information. *(Ruled vs gameplay: no conflict — this is pure presentation over the same 2.5D world.)*

**Lighting and atmosphere.** Warm midday, single global light from the top-left, **no day/night cycle, no dynamic lighting, no post-processing, no full-screen blur, no dynamic weather**. Readability is carried by shape + text + color (never color alone): strong drop shadows make elevation legible; entities cast simple elliptical shadows; a light top-left highlight on tile tops. Avoid photorealism, dark horror tones, heavy fog, neon, and cluttered micro-detail.

**The space.** Fixed isometric camera (§1.1) over a 256×256 tile island ringed by an 8-tile ocean border. Elevation 0–5 renders as vertical offset (`screenY -= elevation * 18`) with top tile + side walls + shadows + edge highlights. **Diff 1 = small step lip (walkable); diff ≥2 = tall cliff face (darker face, vertical striations, jagged top, soft cast shadow, edge language that is never used for a walkable step).** Render order: (1) ocean background, (2) terrain tiles sorted by `tileX+tileY`, (3) side walls, (4) water overlays, (5) terrain details/props/caches/coins/landmarks, (6) player, (7) world effects (wakes, dust, sparkles), (8) UI overlay. Six sectors share one palette/tile/prop/shadow/water language and differ only by local ground color, accent, 1–2 motifs, one landmark, one cache prop, one short label. *(Ruled vs gameplay: "diff 1 walkable / diff ≥2 blocked" matches the §4.2 movement rule; "deep water impassable" matches §4.3 — carried, not new rules.)*

**Water & tide readability (gameplay-relevant rule carried):**

| Depth state | Condition | Appearance |
| --- | --- | --- |
| Dry | `depth <= 0` | Full terrain color, brightest, no overlay |
| Shallow | `0 < depth <= 1.0` | Pale teal overlay 30–40% alpha, slow ripple, terrain visible, small player wake |
| Deep | `depth > 1.0` | Darker blue 65–75% alpha, stronger/slower wave, terrain nearly hidden, no inner foam line |

Shoreline shows a thin foam line where water meets dry land. Trying to enter deep water → short blocked bump animation + soft thud (no damage). Low-tide moment: foam recedes, exposed shelves show wet sand + a thin darker "tide-line", low-tide coins visible, Gull Flats shelf clearly dry, vault cave floor reachable, map water lighter. High-tide moment: water darkens, shallow more opaque, elevation-0 tiles deep, elevation-1 shallow, player pushed to high ground, dial HIGH (double-wave, orange) — still safe, a planning problem not a monster.

**Recipe tables (from visual.md, carried whole):**

*Global palette:*

| Use | Hex | Note |
| --- | --- | --- |
| Parchment UI | `#F3E4C2` | map, panels, prompts |
| UI border | `#5B4632` | panel edges |
| Brass | `#D8A24B` | keys, buttons, interactive trim, channel ring |
| Ink | `#201812` | UI text on parchment |
| Player | `#FFFFFF` | player outline + marker |
| Shadow | `rgba(16,24,36,0.25)` | terrain/entity shadows |
| Ocean deep | `#0B2C47` | deep water + ocean border |
| Water mid | `#1D5F8E` | mid-depth water |
| Shallow water | `#7FD9D2` | passable shallow |
| Foam | `#FFF6E4` | shoreline, water edges |
| Sand | `#E7D0A5` | beaches, dry lowland |
| Jungle floor | `#7DB26A` | Palm Hollow base |
| Rock | `#A89B8A` | cliffs, ruins |
| Ruin stone | `#CFC3AC` | Sunken Ruins |
| Cliff cap | `#D9D1BE` | cliff tops |
| Key gold | `#FFC845` | keys, vault glow, completion |
| Coin gold | `#F2C14E` | coins |
| Low tide | `#45E0C6` | LOW state, ring 1 |
| Rising tide | `#FFD166` | RISING state |
| High tide | `#FF7A3D` | HIGH state + warning |
| Vault marker | `#E5484D` | exact vault marker (red reserved for this) |
| Open vault | `#FFC845` | vault ready/open |
| Hunt area | `#FF9F43` | map search areas |

Color meaning: gold/brass = treasure/positive/interact; teal/cyan = water/low/safe/ring 1; amber/orange = warning/high/search; **red = vault marker only**; gray/hollow = missing/sealed; white = player/foam.

*Clue ring style table (color + line style required; color alone is not enough):*

| Key | Landmark | Color | Line style | Canvas dash | Fill |
| --- | --- | --- | --- | --- | --- |
| 1 | Shipwreck | `#45E0C6` | solid | `[]` | `rgba(69,224,198,0.16)` |
| 2 | Gull Flats Lighthouse | `#9A7BFF` | long dash | `[12,8]` | `rgba(154,123,255,0.16)` |
| 3 | Palm Hollow Idol | `#8ADB6A` | short dash | `[4,8]` | `rgba(138,219,106,0.16)` |
| 4 | Sunken Arch | `#FF7AC0` | dash-dot | `[14,6,4,6]` | `rgba(255,122,192,0.16)` |

*Terrain tile recipe* (`makeTileCanvas(seed, sector, elevation, wet)` → 64×32 canvas): diamond path `(32,0)→(64,16)→(32,32)→(0,16)`; fill `shade(sectorPalette.ground, elevation*0.05)`; 14 noise specks via `mulberry32(seed)` (`rgba(0,0,0, 0.03..0.09)`); if `wet` overlay `rgba(18,68,94,0.16)`; stroke `rgba(31,24,18,0.24)`. Goal: soft hand-painted tile, not a crisp checkerboard.

*Water overlay recipe* (`drawWaterOverlay(ctx, depth, time, tileX, tileY)`): if `depth<=0` return; `isDeep = depth>1.0`; `ripple = sin(time*3.2 + tileX*0.4 + tileY*0.3)`; `alpha = isDeep ? 0.66+0.05*ripple : 0.28+0.08*ripple`; fill `isDeep ? rgba(12,47,74,α) : rgba(127,217,210,α)`; if not deep, stroke foam `rgba(255,246,228, 0.18+0.10*sin(time*4 + tileX + tileY))`.

*Map overlay* (§3 map, carried):
- Canvas `512×512`, `1 tile = 2 px`, parchment background, thin wood/brass border, **92% opaque (8% world visible)**, tile→map `tileToMap`.
- Layer order: (1) parchment, (2) revealed terrain, (3) unrevealed dark overlay `rgba(16,24,40,0.82)` + hatch `rgba(255,255,255,0.04)`, (4) current tide water, (5) high-tide flood preview (elev-0 revealed tiles, light-blue dashed hatch α 0.25, legend "Floods at high tide"), (6) sector labels, (7) hunt areas, (8) clue rings, (9) landmarks, (10) vault marker, (11) player, (12) legend (bottom-left, ≥10 px text).
- Revealed terrain map colors: Beach/lowland `#E7D0A5`, Jungle `#7DB26A`, Rock/ruin `#A89B8A`, Cliff top `#D9D1BE`, Cave/low shelf `#C9B48F`.
- Current water per revealed tile: `depth = max(0, waterLevel - elev)`; if `>0`: `isDeep = depth>1.0`; `alpha = isDeep?0.72:0.38`; color `isDeep ? rgba(11,44,71,1) : rgba(127,217,210,1)`.
- Landmark icons: triangle 10–12 px, parchment border, dark-ink glyph, label below; unique glyph per landmark (not color).
- Hunt area: orange dashed circle, radius 24 tiles, fill `rgba(255,159,67,0.12)`, stroke `#FF9F43`, dash `[10,8]`, question-mark/cache icon at center.
- Clue ring: annulus centered on landmark, `inner = max(0,D-6)*2`, `outer = (D+6)*2`; fill α 0.16, stroke 3 px, key-specific color+dash; `drawClueRing` uses `fill("evenodd")`; animate draw-on when added.
- Vault marker: **4 geometric clues → red X (`#E5484D`), two thick diagonals, pulse 1.0→1.12, label `VAULT`**; **5 keys + low tide → gold X + compass icon, label `OPEN` (`#FFC845`)**.
- Player marker: white arrow, black outline, points in movement direction, small idle pulse.
- Transition: open = parchment unfurls top→bottom + slight scale-up, 0.22 s, paper swish; close = folds back, 0.18 s, paper settle. Map must not obscure tide warnings.

*Sector identity tables (palette + motifs + landmark + cache, carried whole):*

**Driftwood Cove** — Sand `#E7D0A5`, Dune `#D8BC88`, Driftwood `#8A6E58`, Rope `#D7B98C`. Motifs: driftwood logs, loose planks, rope knots, sand ripples, gentle foam. Landmark **Shipwreck** = broken hull + tilted mast + anchor (strong 24-tile silhouette). Cache **Shipwreck barrel** = wooden barrel, brass band, rope closure, openable lid (first clearly interactable prop).

**Gull Flats** — Mudflat `#C8B298`, Wet sand `#DBC7A5`, Lighthouse white `#F5F0E1`, Lighthouse band `#2FA6A6`, Gull `#F7F3E8`. Motifs: flat mud, tide pools, gull shadows, exposed rock shelf, sparse grass. Landmark **Gull Flats Lighthouse** = white tower, teal horizontal bands, small lantern, 2-tile base (**no red on the lighthouse**). Cache **Low-tide rock shelf** = flat stone platform, tide pool, brass-edged rock hatch, seaweed; underwater at high tide, dry+openable at low tide.

**Palm Hollow** — Jungle floor `#7DB26A`, Palm leaf `#3E8C5A`, Root `#6B5A47`, Idol `#6FCF97`. Motifs: palm billboards (sparse, never hide terrain), root mats, fallen trunks, bright floor patches, soft leaf shadows. Landmark **Palm Hollow Idol** = carved pedestal, jade-green mask, moss. Cache **Root gate** = two thick roots over a 2-tile gap, rope tied to a root (rope is the only clearly interactable element), root-wrapped chest behind.

**Sunken Ruins** — Ruin stone `#CFC3AC`, Moss `#7AA96B`, Mosaic blue `#3E7BB0`, Coral `#E98A6D`. Motifs: broken columns, cracked floors, faded mosaics, small coral, shallow channels (abandoned, not haunted). Landmark **Sunken Arch** = broken arch, two pillar ends, missing span, mosaic detail. Cache **Movable stone column** = large mossy column with brass tide-key emblem, visually heavy, open niche behind.

**Cliffpath Ridge** — Rock `#A89B8A`, Cliff cap `#D9D1BE`, Eagle `#F2F2F2`, Wind accent `#EAF6FF`. Motifs: jagged rock, pale tops, thin path ledges, wind streaks, small eagle. Landmark **Cliffpath Eagle Rock** = tall jagged rock + white eagle, strong distance silhouette. Cache **Eagle Rock alcove** = stone chest in alcove, brass keyhole, rope trim, small ledge (a reward for travel, not a trap). Cliff edges clearly non-walkable where jump ≥2.

**Vault Point** — Reef `#E98A6D`, Cave rock `#5E6A72`, Treasure gold `#FFC845`, Water `#1D5F8E`. Motifs: reef rocks, cave mouth, coral branches, wet stone, golden glow. Landmark **Vault Point Reef** = coral cluster, curved outcrop, small cave opening behind. **Vault** = circular stone+brass door, five key slots around the edge, central tide lock, golden glow when low+all-keys, water swirl when sealed; large architectural door, distinct from all caches. Vault states: <5 keys = 5 hollow slots (gray/brass); 5 keys not low = partially submerged + wave icon; 5 keys + low = glows gold, slots fill, lock opens; opening = door swings/slides + light spills; open = treasure + golden compass rises.

*Props:*
- **Player** — human silhouette: oilskin coat, rope belt, small backpack, boots, **white outline**. Distinct from props (body, head, legs, motion).
- **Coins** — 10–14 px, gold, spiral/star mark, slow spin, light bounce, tiny sparkle; smaller and lower than keys; **not marked on the map**.
- **Tide Keys** — larger than coins, brass key with teal tide emblem, floats above cache, soft golden pulse; all five share one base design (sector shown by map clue + counter position, not by color).
- **Caches** — shared language (clear silhouette, brass tide-key emblem, prompt when near, channel ring while interacting, open state stays open) but unique shapes: 1 Barrel, 2 Rock shelf hatch, 3 Root-wrapped chest, 4 Stone column, 5 Alcove chest. Sealed = padlock icon + desaturated brass + "Sealed. Find the first Tide Key."; openable = brighter brass + prompt + ring; channel = brass ring fills clockwise.
- **Landmarks** — strong silhouette, 24-tile visible, unique shape + map glyph + short name. On discovery: brief golden outline + map stamp + map icon (triangle+glyph); after discovery a small brass pin above the object in-world.

*Typography / UI style:* UI = salvager's chart table — parchment panels, dark-wood borders, brass rivets, rope trim on important buttons, crisp modern icons. Display font `"Squada One","Arial Black",sans-serif`; UI font `"Nunito Sans","Trebuchet MS",system-ui,sans-serif`. Titles uppercase bold spaced; HUD labels short uppercase; prompts sentence case; objective one line (two max); map labels short uppercase ≥10 px. Text: on parchment `#201812`; on dark water `#FFF6E4` + dark outline; on gold `#201812`; contrast ≥4.5:1 for critical text.

# 4. GAMEPLAY SPEC

**The game — one paragraph.** You are a shipwrecked salvager on a tide-locked island. Explore a bounded 2.5D isometric island, find **five Tide Keys**, read their **distance clues**, and use the overlapping **clue rings** on the Hoard Map to pinpoint the hidden vault; then time the **low tide** and open it to collect the treasure. There is no combat, no health, and no fail state — the only pressure is the tide, and it is always readable and avoidable. Session 15–25 minutes. Core loop: move/explore → discover landmarks & sectors → find 5 key caches → the first four keys each add a clue ring → after four geometric clues the exact vault marker appears → with 5 keys + low tide, open the vault → collect the final treasure and end.

**Core Constants (record — every number gameplay gave, carried as given):**

| Constant | Value | | Constant | Value |
| --- | --- | --- | --- | --- |
| World size | 256×256 tiles | | Walk speed | 3.0 tiles/s |
| Tile size | 1 meter | | Run speed | 5.0 tiles/s |
| Ocean border | 8 tiles | | Swim speed | 2.0 tiles/s |
| Max elevation | 5 | | Low-stamina swim | 1.5 tiles/s |
| Tide cycle | 120 s | | Max stamina | 100 |
| Water level range | 0–2 | | Run drain | 12 stamina/s |
| Low tide threshold | `< 0.7` | | Swim drain | 10 stamina/s |
| High tide threshold | `> 1.3` | | Stamina regen | 20 stamina/s |
| Passable water depth | `<= 1.0` | | Map reveal radius | 10 tiles |
| Low-tide window (computed) | ~48.4 s / cycle | | Landmark visible dist | 24 tiles |
| | | | Cache visible dist | 8 tiles |
| | | | Hunt area radius | 24 tiles |
| | | | Clue ring width | D ± 6 tiles |
| | | | Safe displacement radius | 16 tiles |
| | | | Interact radius | 1.5 tiles |
| | | | Key cache coins | 10 each |
| | | | Scattered coins | 40 total (8/sector) |
| | | | Vault coins | 70 |
| | | | Total coins | 160 |
| | | | Movement substep | 0.1 tile |
| | | | Max overlap tiles (clues) | < 400 |

**Records with rosters:**

*Sectors (6):*

| id | Name | Role | Bounds (x,y) | highAnchor | lowAnchor/base | Elevation |
| --- | --- | --- | --- | --- | --- | --- |
| driftwood-cove | Driftwood Cove | start, tutorial, Key 1 | 16–70, 190–240 | (32,215) | (32,220) | 0 beach, 1 dunes |
| gull-flats | Gull Flats | low-tide teaching, Key 2 | 90–170, 210–250 | (150,218) | (150,225) | 0 mudflats, 1 flats |
| palm-hollow | Palm Hollow | jungle + interaction, Key 3 | 40–110, 70–150 | (75,110) | (75,105) | 1 lowland, 2 hills |
| sunken-ruins | Sunken Ruins | coastal ruins + movement, Key 4 | 170–220, 100–160 | (195,130) | (195,125) | 1 ruins, 2 floor, 3 tower |
| cliffpath-ridge | Cliffpath Ridge | high ground, Key 5 | 110–180, 30–100 | (145,65) | (145,55) | 2 foothills, 3–4 ridge, 5 tops |
| vault-point | Vault Point | final vault | 185–230, 170–215 | (205,185) | (205,185) | 0 cave, 1 rocks, 2 reef |

*Landmarks (6):*

| id | Name | x,y | elevation | sector | isSectorLandmark | Map glyph |
| --- | --- | --- | --- | --- | --- | --- |
| shipwreck | Shipwreck | 40,210 | 1 | driftwood-cove | yes | anchor |
| lighthouse | Gull Flats Lighthouse | 150,225 | 2 | gull-flats | yes | vertical tower |
| idol | Palm Hollow Idol | 75,105 | 2 | palm-hollow | yes | mask circle |
| arch | Sunken Arch | 195,125 | 2 | sunken-ruins | yes | arch shape |
| eagle-rock | Cliffpath Eagle Rock | 145,55 | 4 | cliffpath-ridge | yes | V-shaped eagle |
| reef | Vault Point Reef | 205,185 | 2 | vault-point | yes | coral branch |

*Caches / Keys (5):*

| id | keyId | Sector | x,y | elevation | Interaction | Channel | requiresKey1 | clue {landmarkId, distance} | prompt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| key1 | 1 | driftwood-cove | 45,208 | 1 | Open barrel | 0.5 s | no | {shipwreck, 169} | Open barrel |
| key2 | 2 | gull-flats | 135,222 | 0 | Open rock shelf | 0.5 s | yes | {lighthouse, 67} | Open low-tide shelf |
| key3 | 3 | palm-hollow | 80,112 | 1 | Pull rope | 1.0 s | yes | {idol, 159} | Pull rope |
| key4 | 4 | sunken-ruins | 192,132 | 1 | Move column | 1.5 s | yes | {arch, 68} | Move column |
| key5 | 5 | cliffpath-ridge | 148,58 | 1 | Open chest | 0.5 s | yes | — (no geometric clue) | Open chest |

Key 3 blocker tiles (gate, 2 tiles) default: `tileIndex(80,111)`, `tileIndex(80,110)`; interact `{80,109}`, reward `{80,112}`. Key 4 blocker tile (column, 1 tile) default: `tileIndex(192,131)`; interact `{192,130}`, reward `{192,132}`. Key notes: Key 1 "The treasure is 169 paces from the Shipwreck." Key 2 "…67 paces from the Gull Flats Lighthouse." Key 3 "…159 paces from the Palm Hollow Idol." Key 4 "…68 paces from the Sunken Arch." Key 5 "The fifth tide turns the lock. The reef cave opens only at low tide."

*Clues (4 geometric):* Keys 1–4 (table above) with ring color/dash from §3. Key 5 adds no clue. Ring inner `D-6`, outer `D+6`.

*Coins (total 160):* 40 scattered (8 per sector, ids `coin-001..coin-040`, on low-tide-passable tiles, ≥2 tiles apart, some in elev-0 low-tide-only spots) + 5×10 cache coins (granted on `cache_opened`, not world coins) + 70 vault coins (granted on `vault_opened`). Rank: 0–99 Beachcomber, 100–139 Salvager, 140–159 Master Salvager, 160 Tide Baron.

*High anchors (6):* the `highAnchor` column of the Sectors table (elevation ≥1, reachable at high tide).

*Progression states (10):* `START → TUTORIAL_KEY1 → FREE_KEYS_1_OF_5 → FREE_KEYS_2_OF_5 → FREE_KEYS_3_OF_5 → FREE_KEYS_4_OF_5 → FREE_KEYS_5_OF_5 → VAULT_READY → VAULT_OPEN → GAME_COMPLETE`. (`TUTORIAL_KEY1` ≡ `keys.totalCollected === 0`; used for objective text.)

*Objective text (record):* Start "Open the shipwreck barrel."; 1/5 "Find the Tide Keys. 1/5"; 2/5 "Find the Tide Keys. 2/5"; 3/5 "Find the Tide Keys. 3/5"; 4/5 "Find the Tide Keys. 4/5"; 5/5 "Open the vault at low tide."; Complete "Treasure found."

*Vault prompt (record):* `<5` keys → "Locked. Requires 5/5 Tide Keys."; 5 keys not low → "Sealed by the tide. Wait for low tide."; 5 keys + low → "Open vault".

*Cache sealed prompt:* "Sealed. Find the first Tide Key."

---

### 4.1 World & Level — T1

The island is **authored, not procedurally critical**: a fixed base layout guarantees every key and the vault are reachable; a per-run seed varies only cache positions (keys 2–5, ≤3 tiles) and scattered coin positions. If any variation or the whole level fails validation, fall back to guaranteed defaults.

Generator pipeline (`createLevel(seed=123)`): `buildBaseLevel` → `applySectorBaseFeatures` → `applyRequiredPointElevations` → `carveGuaranteedRoutes` → `addDecorativeHighGround` → `applySeededCacheVariation(level, rng)` → `placeScatteredCoins(level, rng)` → `applyBlockers(level)` → `validateLevel(level)` → if `!ok`, `createFallbackLevel()`.

- **buildBaseLevel:** all tiles elevation 0; ocean border (8 tiles) marked ocean+impassable; interior default elevation 1 (guarantees a connected high-tide spine); the ring of interior tiles adjacent to the border (shore) set to elevation 0 (beaches).
- **applySectorBaseFeatures:** per-sector low-detail elevation matching the roster — Driftwood: keep start area 1, lower beach to 0; Gull Flats: lower southern flats to 0, keep anchor ≥1; Palm Hollow: base 1, small hills 2, routes 1; Sunken Ruins: base 1, ruin floors 2, tower 3, routes 1; Cliffpath Ridge: ridge plateau 3–5 with a walkable ramp 1→4; Vault Point: cave floor 0 around vault, rocks 1, reef outcrop 2, keep low-tide route to vault. Helpers `setTile`, `fillRect`, `raiseEllipse`, `carveRectRoute`, `carveGradualRoute` (adjacent route tiles differ ≤1); all respect the ocean border and never break protected tiles.
- **applyRequiredPointElevations:** Start 1, Vault 0, Gull Flats cache 0, Lighthouse 2, Idol 2, Arch 2, Eagle Rock 4, Reef 2; other caches 1 unless specified. Any point elev ≥2 gets a local ramp from a nearby passable tile (`ensureReachablePoint`).
- **carveGuaranteedRoutes:** L-shaped paths (no diagonal corners) from start to every cache interact, to every cache reward (after blockers), to vault, to every high anchor, to every landmark. Low routes use elevation 1 where possible; if destination elev ≥2, interpolate ≤1 per step. Mark tiles in a `protected` mask that decoration may not alter.
- **addDecorativeHighGround:** after routes are protected — ridge plateau near Eagle Rock (max 4–5, protected ramp to 4, surrounding 4/5 to form non-walkable cliff edges), ruins tower, lighthouse base, reef outcrop. No high-tide passable pockets disconnected from the spine; Cliffpath has ≥1 walkable ramp to 4.
- **applySeededCacheVariation:** for keys 2–5, Chebyshev offset `dx,dy ∈ [-3,3]` via `rng`; new position must be in-bounds, not ocean, not on a required route blocker, ≥2 tiles from any other cache and from the vault (unless it is the vault-area cache), passable at low tide; **Key 2 must be elevation 0**; Key 3/4 blocker + interact/reward move with the cache and stay valid. Any failure → default position.
- **placeScatteredCoins:** 8 per sector (40 total) on low-tide-passable tiles, not ocean, not on blockers, ≥2 tiles from other coins, ≥2 from start; may be in elev-0 low-tide areas; sampling failure → deterministic fallback positions for that sector.
- **applyBlockers:** register key3 (2 tiles) + key4 (1 tile) default blocker tiles in `level.blockers` (or their moved positions); removed when the cache opens.
- **createFallbackLevel:** size 256, ocean border, interior 1, shore ring 0, start 1, vault 0, landmarks 1 with local ramps, caches at default positions, Key 2 elev 0, no decorative cliffs, blockers removed or converted to trivial single-tile gaps with guaranteed access. Less rich, always valid — completion outranks decoration.

**Validation (`validateLevel` → `{ok, fallbackUsed, errors}`):**
- *Passability:* `tilePassable(level,x,y,waterLevel,blockers)` = not ocean, not blocked, `depthAt <= 1.0`; movement between tiles also needs `abs(Δelev) <= 1`.
- *Low tide (waterLevel 0):* start passable; every cache interact passable (initial blockers); every landmark passable; every high anchor passable; **with all cache blockers removed**, every cache reward passable and vault passable (BFS from start for each).
- *High tide (waterLevel 2):* start passable; every high anchor passable and reachable from start (initial and removed blockers); **all high-tide passable tiles belong to the same connected component as start** (no disconnected pockets).
- *Caches:* in-bounds, not ocean, interact reachable at low tide, reward reachable after blockers, channel time > 0, Key 2 elev 0, Keys 2–5 require Key 1, Keys 1–4 have clue data, Key 5 has none.
- *Clues:* for Keys 1–4, `D = round(euclidean(landmark, vault))`; authored distance must equal computed (else invalid → fallback); compute overlap of all four rings (`|dist(tile, landmark) - D| <= 6` for all); valid iff vault tile is in the overlap **and** `overlapCount < 400`.
- *Coins:* exactly 40, none in ocean, none on blockers, none <2 tiles apart, all low-tide passable.

### 4.2 Movement & Stamina — T1

Tile-based with smooth float position. Speed by current-tile depth (`depth = max(0, waterLevel - elev)`):

| Condition | Speed | Stamina |
| --- | --- | --- |
| Dry (depth ≤ 0), walking | 3.0 | none |
| Dry, running, stamina > 0 | 5.0 | −12/s |
| Shallow (0 < depth ≤ 1.0) | 2.0 | −10/s |
| Shallow, stamina == 0 | 1.5 | −10/s |
| Deep (depth > 1.0) | impassable | — |

Rules: running only on **dry** land and only while `stamina > 0`; the player can always **walk** even at 0 stamina; in water the player is "swimming" (drains 10/s) and cannot run. **Stamina:** max 100; drain run 12/s, swim 10/s; regen 20/s when not draining; at 0 → running disabled, swim speed 1.5, no death, still moves. `updateStamina` clamps to [0,100].

**Collision:** axis-separated (`tryMove(dx,dy)` → `moveAxis` per axis) with substeps of `0.1` tile (prevents tunneling at 5 tiles/s). A target-tile change is allowed only if current passable **and** target passable **and** `abs(Δelev) <= 1` **and** target not in an active `blocker`. A blocked axis does not move.

### 4.3 Tide & Safe Displacement — T1

Global, continuous. `waterLevel(t) = 1 - cos(2π t / 120)`; range 0–2; cycle 120 s; low at t=0, high at t=60. Tile `depth = max(0, waterLevel - elevation)`; passable if `depth <= 1.0`, deep if `> 1.0`. **State:** `LOW` if `waterLevel < 0.7`; `HIGH` if `> 1.3`; else `RISING`. Threshold times per cycle (computed at runtime from the formula): enter RISING (from LOW) t = **24.182 s**; enter HIGH t = **35.823 s**; enter RISING (from HIGH) t = **84.182 s**; enter LOW t = **95.818 s**. **LOW window ≈ 48.4 s** (95.818→144.182); **HIGH window ≈ 48.4 s** (35.823→84.182).

**Warnings:** emit `tide_warning {threshold, secondsUntil:10}` **once per threshold per cycle**, 10 s before each of the four threshold times (at t ≈ 14.182, 25.823, 74.182, 85.818). **State change:** emit `tide_state_changed {state}` only on an actual change. Low tide is required to open the vault; some shelves/coins are low-tide-only.

**Safe displacement (checked every update, before movement):** if the current tile is impassable (tide just flooded it): (1) 4-dir BFS for the nearest passable tile within **16** tiles (current water level, ignore ocean + blockers); if found → move there, cancel any active channel, emit `safe_displacement_occurred`; (2) if none → teleport to `lastHighSafeTile` if it exists, else to the start tile; cancel channel; emit event. **No keys, coins, or progress are lost.** `lastHighSafeTile` updates whenever the player stands on a tile with **elevation ≥ 1** (passable at high tide); initialized to start (32,220, elev 1). Tide is a planning problem, not a death trap.

### 4.4 Hoard Map, Fog, Landmarks, Hunt Areas — T1

**Fog / reveal:** when the player enters a new tile, reveal all tiles within **radius 10** that have line of sight; revealed tiles stay revealed forever. **LOS:** sample the ray from player tile center to target tile center every **0.5** tiles; blocked if any sampled tile has `elevation > playerTile.elevation + 1`; **water does not block visibility**.

**Sector discovery:** a sector is discovered when the player tile enters its bounds **or** its sector landmark is discovered; emit `sector_discovered {sectorId, sectorName}` once; show a banner once per sector.

**Landmarks (6, roster §4):** every frame (throttle ≥10 Hz), for each undiscovered landmark, if `distance(player, landmark) <= 24` **and** LOS exists → discover: add to `state.landmarks.discovered`, emit `landmark_discovered`; if it is a sector landmark → discover the sector + emit `sector_discovered`; **if Key 1 is already collected → reveal that sector's hunt area** + emit `hunt_area_revealed`. Discovered landmarks remain on the map (triangle icon + glyph).

**Hunt areas:** when **Key 1 is collected AND the sector's main landmark is discovered AND the cache is uncollected**, the Hoard Map shows an **orange dashed circle of radius 24** centered on the uncollected cache. The exact cache prop is only visible in-world when the player is within **8 tiles** and has LOS (sealed caches stay visible so the padlock reads). Hunt areas prevent search-fail without revealing the exact cache.

### 4.5 Caches, Keys, Channels, Clue Rings — T1

Five caches, each 1 Tide Key + 10 coins. **Keys 2–5 are sealed until Key 1 is collected.**

**Visibility / prompt:** a cache is visible when uncollected, player within **8** tiles of its interact or reward, and LOS exists (sealed still visible). Within the **1.5-tile interact radius**, show the context prompt (openable = brass `[E]` + gold outline; sealed = padlock + "Sealed. Find the first Tide Key.").

**Channel state:** `state.activeChannel = {type:"cache"|"vault", targetId, startTime, duration, progress}`. Starts when the cache is visible, player within interact radius, not sealed, not opened, and `input.interact` is held. **Cancels** (emit `channel_cancelled {reason}`; prompt shows `Cancelled`) if: player moves, `input.interact` released, map opened, safe displacement occurs, or (vault) tide is no longer low. On completion (emit `channel_complete`), a cache: marks opened+collected, removes its `blockerTiles`, grants the key, grants 10 coins, emits `cache_opened`, `key_collected`, `coin_collected`; if the key has a geometric clue → add clue, increment `geometricCollected`, emit `geometric_clue_added`; **if Key 1 just collected → unseal Keys 2–5 and reveal any hunt areas whose landmarks are already discovered**; **if `geometricCollected === 4` → `vault.markerRevealed = true`, emit `vault_marker_revealed`**; update objective.

**Clue rings:** the first four keys each add a ring centered on their landmark, inner `D-6`, outer `D+6` (D = authored distances 169/67/159/68; §4.1 validates these equal `round(euclidean(landmark, vault))`). Progression by geometric clues: 0 → no rings; 1 → one ring; 2 → two overlap; 3 → overlap shrinks; **4 → exact vault marker appears**. Vault opens only at **5 total keys + low tide**. (Rings, not manual bearings: same puzzle, lower friction.)

### 4.6 Coins & Score — T1

Coins are optional score; they do not affect completion, keys, or the vault. Collected by **walking over** (player distance to coin center ≤ 0.5, coin tile passable). Low-tide-only coins are submerged at high tide. No regeneration. On collect: mark collected, `state.coins.collected += 1`, emit `coin_collected {amount:1, totalCollected}`. Total possible **160** (40 scattered + 5×10 cache + 70 vault). **Rank at completion:** 0–99 Beachcomber, 100–139 Salvager, 140–159 Master Salvager, 160 Tide Baron.

### 4.7 Final Vault — T1

Location: Vault Point, **(208,192)**, elevation **0**, in a sea cave behind reef rocks. Requirements: **5/5 keys** and **low tide (`waterLevel < 0.7`)**. Prompt logic (record §4): `<5` keys → "Locked. Requires 5/5 Tide Keys."; 5 keys not low → "Sealed by the tide. Wait for low tide."; 5 keys + low → "Open vault". **Vault ready** = `totalCollected >= 5 && waterLevel < 0.7`; emit `vault_ready_changed {ready}` on change. **Channel time 1.0 s**; requires 5/5 + low tide + player near + interact held. **Cancels** on move, map open, interact release, safe displacement, or tide no longer low. On success: mark `unlocked` + `completed`, +70 coins, enter `GAME_COMPLETE`, disable input, emit `channel_complete`, `vault_unlocked`, `vault_opened`, `game_complete {time, keys:5, coins, rank}`; collect the 70 coins and the Golden Compass.

### 4.8 Objectives — T1

`currentObjective()` derived from state (record §4): complete → "Treasure found."; 0 keys → "Open the shipwreck barrel."; ≥5 keys → "Open the vault at low tide."; else `Find the Tide Keys. ${keys}/5`. Emit `objective_changed {text}` when the text changes; HUD updates on the event.

### 4.9 Progression & Difficulty — T1

State machine: `START → TUTORIAL_KEY1 → FREE_KEYS_1..5_OF_5 → VAULT_READY → VAULT_OPEN → GAME_COMPLETE` (roster §4). Difficulty has no health, no combat, no fail state; the **tide is the only pressure** and it is always readable/avoidable. Key 1 teaches the map, clue rings, and the loop; Keys 2–5 stay sealed until Key 1 so the player never wanders into a late sector unprepared. **Pacing expectations:** first key < 60 s; Gull Flats low-tide lesson 2–4 min; all five keys 10–20 min; full game 15–25 min. **Feel target:** rarely lost > 60 s; tide understood within the first 3 min; the map feels like a tool, not a tutorial; the final vault feels like a timed ritual, not a boss fight.

### 4.10 Feel — T1

Calm but alive: water ripple, foam, coin spin, key pulse, landmark discovery pulse, map ring draw, vault glow, walk/run/swim. Short readable animations; no fast flashing, no large screen shake, no particle bursts that obscure the player, no disorienting camera moves. *(See §5 motion rules, §6 audio, §11 motion feel.)*

# 5. CHARACTERS

**Player (salvager).** Silhouette: human — oilskin coat, rope belt, small backpack, boots, **white outline** for readability (distinct from keys/coins/props: it has a body, head, legs, and motion). **Facings: 4** (N/E/S/W) from dominant velocity axis (horizontal wins ties), matching the 4-dir animation set.

*Animations by name (with motion rules):*
- `idle` — subtle breathing; small marker pulse on map.
- `walk` ×4 — small dust puff on dry; short slosh + small wake in shallow.
- `run` ×4 — larger dust puff (dry only, stamina > 0).
- `swim` ×4 — continuous small wake (shallow, stamina > 0).
- `swim_tired` ×4 — slower wake, lower cadence (shallow, stamina == 0).
- `channel` — leans into the prop; brass ring fills around `[E]` and around the prop.
- `blocked_bump` — short nudge + (deep water) splash + shake; no damage.

*State → animation (the states gameplay's rules need):* dry walking→`walk`; running→`run`; shallow swimming→`swim`; shallow at 0 stamina→`swim_tired`; deep water or cliff attempt→`blocked_bump`; channeling→`channel`; idle (no input)→`idle`; safe-displaced→`blocked_bump` at origin + ripple (T2 adds the full displacement animation, §0.3).

**Vault (animated entity).** States from §4.7, each mapped to a visual/animation: `locked` (<5 keys) = 5 hollow slots, gray/brass; `sealed` (5 keys, not low) = partially submerged + water swirl + wave icon; `openable` (5 keys + low) = glows gold, slots fill, tide lock opens; `opening` = heavy door swings/slides, light spills, water drains; `open` = treasure visible, golden compass rises. (Functional open = T1; the full 9-step cinematic = T2, §0.3.)

**Caches.** Shared open animation: lid/hatch/gate lifts or column slides, prop goes to its open state, small coin burst; open state persists. *(Prop shapes & sealed/openable looks: §3 props. Eagle/gulls are decorative, T3.)*

# 6. AUDIO

All audio is **generated with the Web Audio API at runtime; no external audio asset files are loaded** (§0.2 ruling). `audioManager` unlocks on the **Begin Salvage** gesture, maps events to sounds via the table below, and limits one-shot SFX to **8 simultaneous** (priority: 1 key, 2 vault, 3 tide, 4 cache, 5 coin, 6 movement, 7 UI; overflow drops lowest priority). World SFX pan by screen position; UI and tide-dial sounds are centered. Missing/no assets never crash (synth is the only path).

**SFX table — one row per event named by gameplay's rules and visual's feedback:**

| Sound | Recipe (waveform · frequency · duration · envelope) | Rule that plays it |
| --- | --- | --- |
| `key` | triangle+sine sweep 660→990 Hz (0.15 s) · lowpass 4000 Hz · 0.60 s · gain 0.35 → exp 0.001 | on `key_collected` |
| `coin` | square · random 1200–1800 Hz · lowpass 3000 Hz · 0.12 s · gain 0.18 → exp 0.001 | on `coin_collected` |
| `cache_sealed` | sine 120 Hz + square click 900 Hz (0.03 s) · lowpass 800 Hz · 0.35 s · gain 0.25 → exp 0.001 | on `cache_sealed_prompt` (once per attempt/visibility entry) |
| `cache_opened` | filtered sawtooth creak 200→90 Hz + sine thud 80 Hz · 0.5 s · gain 0.3 → exp 0.001 | on `cache_opened` for Keys 1, 2, 5 |
| `rope_pulled` | filtered sawtooth creak 160→70 Hz + 3× square 400 Hz ratchet (0.02 s) · 1.0 s · gain 0.28 → exp 0.001 | on `cache_opened` for Key 3 |
| `column_moved` | low noise burst, lowpass 800→120 Hz (1.4 s) + sine rumble 50 Hz · 1.5 s · gain 0.25 → exp 0.001 | on `cache_opened` for Key 4 |
| `tide_warning` | two sine gongs 180 Hz then 150 Hz (0.10 s apart) + short echo · lowpass 900 Hz · 0.8 s · gain 0.22 → exp 0.001 | on `tide_warning` |
| `low_tide` | noise swell desc (bandpass 600→200 Hz) + sine chime 880 Hz (0.15 s) · 0.7 s · gain 0.25 → exp 0.001 | on `tide_state_changed` → LOW |
| `high_tide` | noise swell asc (bandpass 200→600 Hz) + sine gong 110 Hz (0.3 s) · 0.7 s · gain 0.25 → exp 0.001 | on `tide_state_changed` → HIGH |
| `vault_locked` | sine 70 Hz + square 140 Hz (0.05 s) · 0.5 s · gain 0.3 → exp 0.001 | on vault prompt "Locked. Requires 5/5" (once per visibility entry) |
| `vault_opening` | low rumble (lowpass 300→80 Hz) + brass bell 520/660 Hz (0.4 s) + water drain (bandpass 400→100 Hz) · 1.2 s · gain 0.35 → exp 0.001 | on `vault_opened` |
| `game_complete` | D-major-pentatonic marimba/brass arpeggio D5–A5–D6 (3×0.15 s) + gull cry (sawtooth 900→400 Hz, 0.4 s) · 2.0 s · gain 0.4 → exp 0.001 | on `game_complete` |
| `landmark` | paper stamp (noise 0.05 s) + small bell sine 1046 Hz (0.1 s) · 0.4 s · gain 0.25 → exp 0.001 | on `landmark_discovered` |
| `clue` | compass tick square 1200 Hz (0.03 s) + chart swish (noise 0.2 s) · 0.5 s · gain 0.22 → exp 0.001 | on `geometric_clue_added` |
| `safe_displacement` | air whoosh (noise 200→2000 Hz, 0.15 s) + splash (bandpass 800 Hz, 0.2 s) · 0.4 s · gain 0.25 → exp 0.001 | on `safe_displacement_occurred` |
| `footstep_dry` | lowpass noise thud (lowpass 400 Hz) · 0.08 s · gain 0.12 → exp 0.001 | once per tile entered while dry (depth ≤ 0) |
| `footstep_shallow` | bandpass noise slosh (500 Hz) · 0.10 s · gain 0.14 → exp 0.001 | once per tile entered while shallow (0 < depth ≤ 1.0) |
| `swim_loop` | continuous lowpass water noise (lowpass 600 Hz) · looping · gain 0.20, linear ramp 0↔0.20 over 0.2 s | active while depth > 0; stops when dry |
| `ui_hover` | sine 1600 Hz · 0.05 s · gain 0.1 → exp 0.001 | on UI hover |
| `ui_click` | filtered square 600 Hz (lowpass 2000 Hz) · 0.08 s · gain 0.15 → exp 0.001 | on UI press (Begin Salvage, Restart) |
| `map_open` | noise sweep up 200→4000 Hz · 0.2 s · gain 0.18 → exp 0.001 | on `map_opened` |
| `map_close` | noise sweep down 4000→200 Hz · 0.18 s · gain 0.18 → exp 0.001 | on `map_closed` |

All one-shots: quick attack, clean decay, no sharp peaks. Design rules: key bright/unmistakable; coin small/satisfying; tide watery not alarming; vault heavy/ceremonial; interactions match material (rope creak, stone grind, wood creak, brass chime).

**Music (Web Audio generative layers, D-major pentatonic D·E·F#·A·B, base 84 BPM):**

| Layer | Recipe (waveform · frequency/pattern) | Level | Purpose / adaptive rule |
| --- | --- | --- | --- |
| Sea bed | filtered noise + low sine ~55 Hz | −18 dB | constant ocean presence (start + always) |
| Percussion | wood block/shaker/soft kick at 84 BPM | −16 dB | exploration; −30% in shallow; ducks in deep-blocked |
| Melody | marimba/celesta/muted guitar, D-pentatonic | −12 dB | main exploration; very soft on start screen |
| Tide accent | water wash / low swell | −14 dB | rises with tide state (low→bright celesta ostinato; rising→swells; high→low marimba pulse ~slower feel) |
| Stinger | brass/marimba motif | −6 dB | key (3-note), vault (heavy bell+marimba), completion (2-s fanfare+gull) |

Adaptive state rules: start screen = sea bed + distant gull + very soft melody; dry exploration = full percussion+melody; shallow = percussion −30% + water wash up; deep-blocked = music ducks + low swell; low tide = + bright celesta ostinato; rising = + soft swells; high = + low marimba pulse; vault ready = slow bell pulse at 60 BPM for ~10 s; vault opening = heavy bell+marimba hit; game complete = 2-s light fanfare + gull cry. **Sector motifs (T2), <1 s each:** Driftwood Cove D→A; Gull Flats F#→B; Palm Hollow A→B; Sunken Ruins low D→F#; Cliffpath Ridge high B→A; Vault Point D→B (+bell). **Mixing:** music −12 dB, SFX −6 dB, UI −10 dB, water loop −14 dB, stingers −6 dB; duck music 3 dB when important SFX play; keep SFX clearer than music; never let water overpower key/vault. *(Music is T1 = sea bed + stingers; T2 = full adaptive layers + motifs, §0.3.)*

# 7. UX

HTML + CSS only (DOM HUD; the game and map are canvases). 

**Screens as a state machine:**

| State | Enter trigger | Visible elements | Events |
| --- | --- | --- | --- |
| `START` | page load | Start screen (title, subtitle, controls, **Begin Salvage**) | — |
| `PLAYING` | **Begin Salvage** clicked (unlock audio, start loop, enable input) | All persistent HUD (+ map overlay / banners / prompt when applicable) | `game_start`, `map_opened/closed`, `channel_*`, `tide_*`, `sector_discovered`, `objective_changed` |
| `COMPLETE` | `vault_opened` → `game_complete` | End screen (Treasure Found, rank, time, coins, keys, **Restart** reloads) | `game_complete` |

Sub-flags inside `PLAYING`: `mapOpen` (M / Right Mouse held → `map_opened`/`map_closed`; opens at 0.22 s, closes 0.18 s), `channeling` (`activeChannel` set → `channel_started`/`complete`/`cancelled`), `warning` (tide warning banner, ~the 10 s window).

**HUD table (element → record field → when visible; sizes from visual §10.4):**

| Element | Reads | When visible | Size |
| --- | --- | --- | --- |
| Tide dial (top-left) | `state.tide.waterLevel`, `state.tide.state` | always (PLAYING) | 72×72 circular; state LOW/RISING/HIGH + icon (down-arrow-empty-wave / up-arrow-half-wave / double-wave) + color + seconds-to-next-threshold |
| Stamina bar (top-left) | `state.player.stamina` (0–100) | always | 120×12; fill `#6FCF97`; boot icon; at 0 → gray stripes + `WALK` |
| Key counter (top-left) | `state.keys.totalCollected` (0–5) | always | 5 slots, filled gold / hollow gray + `n/5` |
| Coin counter (bottom-right) | `state.coins.collected` | always | coin icon + `X / 160`; golden pulse on collect |
| Map button (top-right) | (opens map) | always | 64×64, map/scroll icon + small preview; hold M/Right Mouse |
| Objective (top-right) | `currentObjective()` | always | parchment strip, max width 220 px (two lines max) |
| Context prompt (bottom-center) | nearest interactable / `activeChannel` | when within interact radius or channeling | 260×52 pill; `[E]` icon + text + channel ring |
| Tide warning banner (top-center) | `tide_warning` / state | during the 10 s warning | icon + text, e.g. "Tide rising in 10s" / "High tide in 10s" / "Low tide in 10s"; dial pulses; no full-screen flash |
| Sector banner (top-center) | `sector_discovered` | 2 s after discovery | sector icon + name, parchment + stamp sound |
| Map overlay | `state.tiles.revealed`, clues, landmarks, hunt areas, `state.vault`, `state.player` | when `mapOpen` | 512×512 parchment, 92% opaque, layers + legend (§3) |
| Start screen | (static) | `START` | title `Island of the Hidden Hoard`, subtitle `A tide-locked salvage hunt`, controls, **Begin Salvage** |
| End screen | `game_complete` payload | `COMPLETE` | `Treasure Found`, rank + icon, time, coins, keys, **Restart** |

Context-prompt states: sealed (padlock, gray) / openable (brass `[E]`, gold outline) / channeling (ring fills) / cancelled (ring breaks, `Cancelled`, gray) / vault-locked-by-keys (5 hollow keys) / vault-sealed-by-tide (wave icon) / vault-openable (gold keys, glow). Channel ring appears in the prompt **and** around the prop; on cancel it breaks into two arcs.

# 8. DEBUG API

Headless, driven by `harness.js`. Every function a §9 test calls is defined here. `debug.newGame(seed)` returns `{ game, level, state, events }`.

**Lifecycle / time:** `debug.newGame(seed=123)`, `debug.advance(seconds, dt=1/60)`, `debug.waitFor(cond, maxSeconds=60)`, `debug.state()` (live `STATE`), `debug.level()` (live `LEVEL`), `debug.snapshot()` (deep copy of `STATE`).

**Inputs (as functions):** `debug.input.move({up,down,left,right})`, `debug.input.clear()`, `debug.input.run(bool)`, `debug.input.map(bool)`, `debug.input.interact(bool)`, `debug.pressInteract(durationSeconds)`, `debug.openMap(durationSeconds)`, `debug.moveTowards(tile, {waitSeconds, requireLowTide})` (pathfinding controller: A* with current water level + blockers, waits/retries for tide/blockers, follows by input), `debug.interactWith(cache, {advance, moveTowards})` (nearest passable tile within 1.5 of `cache.interact`, hold interact for `channelTime + 0.2 s`).

**Pure queries:** `debug.depth(x,y,waterLevel)`, `debug.passable(x,y,waterLevel)` (uses live `LEVEL.blockers`).

**Per-system reachers (one function per system):**
- Tide: `debug.tide.set(time)`, `debug.tide.setLevel(level)`, `debug.tide.setState(state)`, `debug.tide.level()`, `debug.tide.state()`.
- Player/movement: `debug.player.set(x,y)`, `debug.player.setStamina(n)`, `debug.player.setFacing(dir)`, `debug.player.state()`.
- Safe displacement: `debug.safeDisplacement.force()`.
- Fog: `debug.fog.reveal(x,y,r)`, `debug.fog.clear()`, `debug.fog.isRevealed(x,y)`.
- Landmarks: `debug.landmarks.discover(id)`, `debug.landmarks.clear()`, `debug.landmarks.discovered()`.
- Caches/keys/clues: `debug.caches.open(id)`, `debug.caches.sealAll(bool)`, `debug.caches.state()`, `debug.keys.set(n)`, `debug.clues.set(n)`, `debug.clues.state()`, `debug.clues.overlap()` → `{count, includesVault}`, `debug.clues.validate()` → `{ok, overlapCount, vaultInOverlap, distances[]}`, `debug.clueDistance(keyId)`.
- Coins: `debug.coins.add(n)`, `debug.coins.set(n)`, `debug.coins.collectAll()`, `debug.coins.state()`, `debug.coins.rank(n)`.
- Vault: `debug.vault.setKeys(n)`, `debug.vault.open()`, `debug.vault.state()`.
- Objectives/progress: `debug.objectives.current()`, `debug.progress.set(state)`, `debug.complete()`.
- Level: `debug.level.setTile(x,y,elev)`, `debug.level.blockers.add(i)`, `debug.level.blockers.remove(i)`, `debug.level.blockers.clear()`, `debug.level.summary()`, `debug.level.validate()`, `debug.level.reachableFrom(start, {waterLevel, removeBlockers})`.
- Events: `debug.events.list()`, `debug.events.last(name)`, `debug.events.clear()`.
- Audio (stub context in tests): `debug.audio.map(event)` → SFX name, `debug.audio.play(name)`, `debug.audio.poolSize()`.

# 9. TESTS

Headless (Node, no browser). **Every unit + playthrough call is a §8 function; every expected state follows from §4.** T3 e2e drives the real page (keyboard/mouse = the §1.2 inputs) and is listed for completeness; it does not consume the debug API.

**Unit tests (each system ≥1 check):**

- **`tide.test.js`** — `waterLevelAt(0)=0`, `waterLevelAt(60)=2`, `waterLevelAt(120)=0`; `tideState` LOW/HIGH/RISING at `<0.7`/`>1.3`/between; `tide_state_changed` fires only on real change; `tide_warning` fires 10 s before each threshold, once per cycle, no duplicates. *Calls:* `debug.tide.set`, `debug.advance`, `debug.tide.level/state`, `debug.events.last`.
- **`passability.test.js`** — elev 0 passable at wl 0, impassable at wl 2; elev 1 passable at wl 2; elev 2 passable at wl 2; `debug.depth` correct; ocean border impassable; Δelev 1 walkable, Δelev 2 not; active blockers impassable, removed blockers passable. *Calls:* `debug.level.setTile`, `debug.depth`, `debug.passable`, `debug.level.blockers`.
- **`movement.test.js`** — dry walk ≈3.0, run ≈5.0, no run in water, swim ≈2.0, low-stamina swim 1.5, blocked movement no position change, no corner clipping, no 1-tile-cliff tunneling at speed. *Calls:* `debug.player.set/state`, `debug.input.move/run`, `debug.tide.setLevel`, `debug.advance`.
- **`stamina.test.js`** — run −12/s, swim −10/s, regen +20/s when not draining, clamp to 0, run disabled at 0, walk still possible at 0. *Calls:* `debug.player.setStamina/state`, `debug.input.run/move`, `debug.advance`.
- **`safeDisplacement.test.js`** — current tile deep → moves to nearest passable; channel cancelled; no local tile → `lastHighSafeTile`; none → start; event emitted. *Calls:* `debug.tide.setLevel(2)`, `debug.player.set`, `debug.advance`, `debug.player.state`, `debug.level.setTile`, `debug.events.last`.
- **`fog.test.js`** — entering a tile reveals radius 10; revealed persists; LOS blocked by elev > player+1; water does not block LOS; nothing outside radius revealed. *Calls:* `debug.fog.clear/isRevealed`, `debug.player.set`, `debug.level.setTile`, `debug.advance`.
- **`landmarks.test.js`** — within 24 + LOS discovered; beyond 24 not; no LOS not; event fires; sector landmark discovers sector; hunt area reveals after Key 1 + landmark. *Calls:* `debug.landmarks.discovered/discover`, `debug.player.set`, `debug.keys.set`, `debug.advance`, `debug.events.last`.
- **`caches.test.js`** — Key 1 available at start; Keys 2–5 sealed before Key 1; sealed → `cache_sealed_prompt`; after Key 1 others available when visible; channel completes after its time; move/map-release cancel; opened stays open; blockers removed; key + 10 coins granted; clue added for 1–4, none for 5. *Calls:* `debug.caches.state/open`, `debug.keys.set`, `debug.player.set`, `debug.pressInteract`, `debug.openMap`, `debug.advance`, `debug.events`.
- **`coins.test.js`** — walking over a coin collects it; no regen; total increments; rank thresholds correct; completion works with 0 coins; total possible 160. *Calls:* `debug.coins.set/add/collectAll/state/rank`, `debug.player.set`, `debug.advance`.
- **`vault.test.js`** — locked <5 keys; sealed (5 keys, not low); openable (5 keys + low); channel completes only at low tide; tide-rise/move/map cancel; success +70 coins; emits `game_complete`; input disabled. *Calls:* `debug.vault.setKeys/state`, `debug.tide.setLevel`, `debug.player.set`, `debug.pressInteract`, `debug.openMap`, `debug.advance`, `debug.coins.state`, `debug.events`.
- **`clues.test.js`** — authored distances equal rounded landmark→vault distances; 0 clues no rings; 1 clue one ring; 4 clues reveal marker; overlap contains vault; overlap < 400; ring data correct for 1–4; Key 5 adds none. *Calls:* `debug.clues.set/state/overlap/validate`, `debug.clueDistance`.
- **`levelGenerator.test.js`** — level 256×256, ocean border impassable, start/vault/landmarks/caches exist; low-tide BFS (initial blockers) reaches all cache interacts + landmarks; low-tide after blockers removed reaches all rewards + vault; high-tide BFS reaches all high anchors; high-tide passable tiles connected to start; clue validation passes; coin placement passes; seeded caches valid; invalid variation → default; fallback always valid. *Calls:* `debug.newGame`, `debug.level.summary/validate/reachableFrom`.
- **`events.test.js`** — all major events present with contract payloads; no unknown events required by renderer/audio; `game_complete` payload has time, keys, coins, rank. *(Also the objectives check: `debug.keys.set(0/3/5)` + `debug.complete()` → `debug.objectives.current()` returns "Open the shipwreck barrel." / "Find the Tide Keys. 3/5" / "Open the vault at low tide." / "Treasure found.")* *Calls:* `debug.events.list`, `debug.keys.set`, `debug.complete`, `debug.objectives.current`.
- **`audio.test.js`** (stub `AudioContext`) — unlock required before start; `key_collected`→`key`, `coin_collected`→`coin`, `tide_warning`→`tide_warning`, `vault_opened`→`vault_opening`; pool caps simultaneous SFX at 8; missing assets fall back to synth without throwing. *Calls:* `debug.audio.map/play/poolSize`.

**Playthrough (`playthrough.test.js`)** — headless, seed 123, `dt 0.05`: start state (`progress START`, 0 keys) → `interactWith` Key 1 (→1 key, 1 geometric, ≥10 coins) → for Keys 2–5 `interactWith` (Key 2 gated by `waitFor(waterLevel < 0.7, 120)`) → 5 keys, 4 geometric, `vault.markerRevealed` true → `moveTowards(vault, {waitSeconds:180, requireLowTide:true})` → `interactWith` vault (1.0 s) → `complete` true, coins ≥70 and ≤160; `game_complete` event present with `keys 5` and matching `coins`. *Calls:* all from the harness set above.

**T3 additions:** multi-seed playthrough (1, 7, 42, 123, 999); completion time `< 30*60` s; no soft-lock (no exceptions, player in-world, current tile passable each update, displacement loses nothing, reaches `GAME_COMPLETE`); event order `game_start → key 1..5 → clue 1..4 (may interleave with keys) → vault_marker_revealed → vault_opened → game_complete` (relative, not exact frame).

**E2E smoke (`tests/e2e/smoke.spec.js`, T3, optional)** — page loads with no console errors; start screen visible; **Begin Salvage** hides it, shows canvas, starts audio context; movement keys change position; holding M opens map, releasing closes; HUD elements exist (tide dial, stamina, keys, coins, objective); interacting near the first cache completes the channel; no unhandled promise rejections.

**SCREENSHOTS table** *(constructed from visual §16 checklist + defined states; §0.2 ruling):*

| ID | Visual state shown | From | Check that must be true |
| --- | --- | --- | --- |
| SS-01 | Water-depth trio: dry / shallow / deep | §4.3/6 | three visually distinct states; dry brightest; shallow 30–40% teal, terrain visible; deep darker + more opaque |
| SS-02 | Elevation diff 1 step | §4.3 | small lip, light shadow, reads walkable |
| SS-03 | Elevation diff ≥2 cliff | §4.3 | tall dark face, jagged top, cast shadow, reads non-walkable |
| SS-04 | Sealed cache | §4.5/props | padlock icon, desaturated brass, prompt "Sealed. Find the first Tide Key." |
| SS-05 | Openable cache + channeling | §4.5/§10.6 | brass `[E]`, gold outline, progress ring in prompt and around prop |
| SS-06 | Single clue ring (Key 1) | §4.5/§9.8 | teal solid annulus centered on Shipwreck |
| SS-07 | Two rings overlapping | §4.5/§9.8 | two distinct colors/dashes, overlap visible |
| SS-08 | Exact vault marker | §4.5/§9.9 | red X, label `VAULT`, pulse, distinct from rings/hunt |
| SS-09 | Vault ready | §4.7/§9.9 | gold X + compass, label `OPEN` |
| SS-10 | Full map overlay | §3 map/§9 | parchment, revealed, water, flood preview, landmarks, hunt area, clue rings, player, legend |
| SS-11 | Full HUD | §7/§10.4 | tide dial LOW, stamina full, keys 0/5, coins 0/160, objective, map button |
| SS-12 | Tide warning banner | §7/§10.7 | icon + text (e.g. "High tide in 10s"), double-wave, orange; no full-screen flash |
| SS-13 | Sector discovery banner | §7/§10.8 | icon + name (e.g. "Gull Flats"), parchment, 2 s |
| SS-14 | Start screen | §7/§10.3 | title, subtitle, controls, **Begin Salvage** |
| SS-15 | End screen | §7/§10.9 | Treasure Found, rank + icon, time, coins, keys, **Restart** |
| SS-16 | Player moving (dry/water) | §5/§8.1 | dust puff (dry) vs wake (shallow); 4-dir facing |
| SS-17 | Player blocked (deep water) | §5/§8.1 | short bump + splash + shake, no damage |
| SS-18 | Low-tide moment | §6.5 | exposed shelf dry, vault cave reachable, tide-line on sand, map water lighter |
| SS-19 | High-tide moment | §6.6 | compressed, player on high ground, dial HIGH (double-wave, orange) |

# 10. BUILD ORDER

Each milestone names the §9 check that shows it landed.

| # | Milestone | §9 check that proves it | Tier |
| --- | --- | --- | --- |
| M1 | Skeleton: file tree, `package.json`, `CONFIG`, `EventBus`, `rng`, `geometry`, boot flow | `events.test.js` (payload contract) | T1 |
| M2 | Level: `LAYOUT`, `generator`, `validator`, `fallback` | `levelGenerator.test.js` (all BFS + clue + coin + fallback checks) | T1 |
| M3 | Tide system | `tide.test.js` | T1 |
| M4 | Passability + movement + stamina + safe displacement | `passability.test.js`, `movement.test.js`, `stamina.test.js`, `safeDisplacement.test.js` | T1 |
| M5 | Fog + landmarks + hunt areas | `fog.test.js`, `landmarks.test.js` | T1 |
| M6 | Caches + keys + channels + clue rings | `caches.test.js`, `clues.test.js` | T1 |
| M7 | Coins + rank | `coins.test.js` | T1 |
| M8 | Vault + objectives + game complete | `vault.test.js`, `events.test.js` (objectives check) | T1 |
| M9 | Audio manager + event→sound mapping + pool | `audio.test.js` | T1 |
| M10 | Renderer (world + map + HUD) | E2E smoke (HUD/canvas) + SS-01…SS-19 | T1 |
| M11 | Single-seed playthrough | `playthrough.test.js` (seed 123) | T1 |
| M12 | T2: adaptive music, sector banners+motifs, collection flourishes, displacement animation, vault cinematic, landmark flourish | SS-05/SS-09/SS-12/SS-13 + audio adaptive rows | T2 |
| M13 | T3: small-screen, decorative richness, multi-seed+time+event-order, E2E, perf pass, confetti | multi-seed `playthrough`, E2E smoke, 60 FPS profile, SS-15 | T3 |

# 11. DEFINITION OF DONE

One header per §0.1 row; the §9 checks + SCREENSHOTS rows under each make it true. When every header is complete, the game is complete.

**1. Open-world island exploration (request).** Checks: `levelGenerator.test.js` (256×256, six sectors/landmarks/caches placed, low- and high-tide BFS reachability); `fog.test.js`; `landmarks.test.js`. Screenshots: SS-10 (map of the island), SS-11 (HUD), SS-18/SS-19 (low/high tide moments).

**2. Find treasure (request).** Checks: `vault.test.js` (opens at 5 keys + low tide, +70 coins, emits `game_complete`); `playthrough.test.js` (reaches `GAME_COMPLETE`); `coins.test.js` (rank). Screenshots: SS-08/SS-09 (marker → ready), SS-15 (end screen).

**3. 2.5D isometric fixed camera (added).** Checks: `movement.test.js` (axis-separated, substepped); E2E smoke (canvas renders, no rotation). Screenshots: SS-02/SS-03 (elevation + cliff read in iso), SS-01 (water in iso).

**4. Five Tide Keys + distance clue rings (added).** Checks: `caches.test.js` (5 keys, clues 1–4, none for 5); `clues.test.js` (rings, overlap < 400, vault in overlap, marker at 4). Screenshots: SS-06/SS-07 (rings), SS-08 (exact marker).

**5. Continuous tide + safe displacement (added).** Checks: `tide.test.js` (formula, states, warnings); `safeDisplacement.test.js` (push to nearest / lastHighSafeTile / start, channel cancel, event). Screenshots: SS-12 (warning), SS-18/SS-19 (low/high), SS-01 (depth).

**6. Hoard Map: fog, landmarks, hunt areas, marker (added).** Checks: `fog.test.js`; `landmarks.test.js` (discovery + hunt-area reveal). Screenshots: SS-10 (full map), SS-08/SS-09 (marker), SS-13 (sector banner).

**7. Stamina movement, no health/combat (added).** Checks: `stamina.test.js` (drains, regen, clamp, no-run-at-0); `movement.test.js` (walk always possible). Screenshots: SS-16 (walk/water), SS-17 (blocked, no damage).

**8. Optional coin score + end rank (added).** Checks: `coins.test.js` (collect, no regen, thresholds, 0-coin completion, total 160). Screenshots: SS-15 (rank + coin total).

**9. Web Audio SFX + adaptive music (added).** Checks: `audio.test.js` (unlock, event mapping, pool cap, synth fallback). Screenshots: n/a (audio); behavior covered by §6 recipes. (Adaptive layers = T2.)

**10. HUD, start, end screens (added).** Checks: E2E smoke (all HUD elements exist; start → play → end transitions); `events.test.js` (objective text). Screenshots: SS-14 (start), SS-11 (HUD), SS-12 (warning), SS-15 (end).

**11. Deterministic level + validation + fallback (added).** Checks: `levelGenerator.test.js` (validation passes, invalid variation → default, fallback always valid). Screenshots: SS-10 (a valid generated island).

**12. Headless tests + single-seed playthrough proof (added).** Checks: full unit suite + `playthrough.test.js` (seed 123) all green. Screenshots: n/a.

# A. SANITY

Re-read §2, §4, §8, §9; the following checks were made and the sections were fixed where needed (result stated).

- **Every field a rule reads or writes is in the global context.** Cross-referenced §4 rules and §9 assertions against `STATE`/`LEVEL`/`CONFIG` (§2.2): `player.{x,y,tileX,tileY,facing,stamina}`, `tide.{time,waterLevel,state}`, `keys.{totalCollected,geometricCollected,collected,clues}`, `coins.collected`, `vault.{markerRevealed,ready,unlocked,completed}`, `tiles.revealed`, `landmarks.discovered`, `sectors.discovered`, `caches.{collected,opened}`, `activeChannel`, `lastHighSafeTile`, `input.*`, `complete`, and `LEVEL.{elevation,ocean,sector,start,vault,landmarks,caches,coins,highAnchors,blockers,validation}` — all present. **closes.**
- **Every place/thing/kind a rule names is placed by a generator or listed in a roster.** Six sectors (§4 roster + `LAYOUT`), six landmarks (§4 roster), five caches/keys (§4 roster), six high anchors (§4 roster), 40 scattered coins + 5×10 cache + 70 vault (§4.1/§4.6), vault (208,192) + start (32,220) in `LAYOUT`. **closes.**
- **Consumables: total placed vs total demanded along the core loop.** Coins: placed 40 + 50 + 70 = 160 = total possible 160; completion demands none (rank references up to 160) — no shortfall. Keys: 5 placed, 5 demanded by vault. Geometric clues: 4 placed (Keys 1–4), 4 demanded for the marker. Stamina is a resource, not a placed consumable (checked as a timing pair below). **closes.**
- **Timing pairs close AND still bite.** (a) Drain vs refill: regen 20/s > run 12/s and swim 10/s → recovers when idle; bites because sustained running hits 0 in 100/12 ≈ 8.3 s. (b) Travel vs distance at speed: the longest low-tide-only crossings on the core loop (Gull Flats shelf approach, vault-cave approach) are ≤ ~15 tiles ≈ ≤ 5 s at walk 3.0, well inside the ~48.4 s LOW window; first key is ~18 tiles ≈ 6 s from start (< 60 s). Bites (must time the tide) but is generous. (c) End-condition clock vs expected clear: there is **no lose timer**; the vault is gated by tide phase, and LOW recurs every 120 s with a ~48.4 s window, so the "clock" is always hittable (wait ≤ ~60 s + 1 s channel). **No clock the player can never hit exists → nothing to change.** Completion bound is the < 30 min playthrough assertion (T3). All threshold times recomputed exact from the agreed formula (24.182 / 35.823 / 84.182 / 95.818 s); warnings at −10 s of each. **closes.**
- **Every call §9 makes is in §8.** Aligned the unit + playthrough tests to the §8 function set (`debug.tide.*`, `debug.player.*`, `debug.input.*`, `debug.pressInteract`, `debug.openMap`, `debug.moveTowards`, `debug.interactWith`, `debug.depth`, `debug.passable`, `debug.fog.*`, `debug.landmarks.*`, `debug.caches.*`, `debug.keys.set`, `debug.clues.*`, `debug.coins.*`, `debug.vault.*`, `debug.objectives.current`, `debug.level.*`, `debug.events.*`, `debug.audio.*`). E2E (T3) drives the real page with the §1.2 inputs, not the debug API. **closes.**
- **No placeholder in angle brackets remains.** Scanned the merged doc: only comparison operators (`<`, `>`) and one generic-type note (`Set<string>`, rendered as prose "a Set of … ids"); no `<placeholder>` tokens. **closes.**