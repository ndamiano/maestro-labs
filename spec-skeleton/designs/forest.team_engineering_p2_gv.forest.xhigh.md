# engineering.md

## 0. Authority and Conflict Resolution

This document is the engineering authority for implementation structure, file layout, deterministic simulation, testability, and validation.

Precedence:

1. `gameplay.md` is the authority for gameplay rules, numbers, and states.
2. `visual.md` is the authority for presentation, asset direction, HUD layout, and audio direction.
3. This document is the authority for how the game is coded, tested, and validated.
4. If a numeric implementation detail conflicts with prose, use the explicit formula, coordinate, or state-machine rule from `gameplay.md` and this document.

Important resolved conflict:

- `gameplay.md` says the gate threshold is `y < 6`, but also calls it “3-tile-deep”.
- The implementation treats `y < 6` as the canonical win and exclusion boundary.
- The map contract provides a 3-tile-deep gate gap at `y = 3, 4, 5` so the visual “3-tile-deep” intent is preserved without changing the gameplay rule.

---

## 1. Engineering Goals

The game must be:

- Deterministic enough to test.
- Headless-testable without a browser.
- Scalable enough to support the visual and audio systems without changing gameplay logic.
- Small enough to finish in one build.

The implementation must prove that the game is finished by:

- Passing all automated unit and integration tests.
- Passing a map contract validator.
- Running a scripted end-to-end playthrough that reaches the win state.
- Running a scripted threat interaction that proves The Hollow, light safe zones, and the gate work together.
- Passing a short manual browser smoke checklist.

---

## 2. Cuts and Rationale

These are intentionally excluded.

| Cut | Reason |
|---|---|
| No runtime procedural map generator | `gameplay.md` requires one handcrafted map. Procedural generation would add fairness risk, test complexity, and scope. |
| No level editor | A map JSON contract plus validator is enough. |
| No save system | One 8-minute run. Retry resets everything. |
| No pause | Visual design cuts pause. A tension run should not pause casually. |
| No minimap | Already cut by gameplay and visual docs. |
| No external game engine | Canvas 2D and plain ES modules are enough. |
| No network | Single-player local game. |
| No build pipeline | Native ES modules, Vitest for tests, static server for manual play. |
| No browser automation dependency | Headless simulation plus manual smoke is enough for a single-run browser game. |
| No multiple enemies | One enemy. |
| No complex UI framework | Canvas HUD plus DOM title/end screens. |
| No optional accessibility modes | Warnings must already use shape and pulse, not color alone. Reduce-motion and high-contrast modes are cut to avoid scope. |
| No path smoothing | Tile-center waypoints are readable and easier to validate. Visual can add small animation smoothing. |

---

## 3. File Layout

The integration agent should create the files below.

```text
index.html
styles.css
package.json

src/
  main.js
  config/
    defaultConfig.js
  core/
    clock.js
    rng.js
    eventBus.js
    input.js
    loop.js
    math2d.js
  game/
    map.js
    player.js
    hollow.js
    gate.js
    lighting.js
    perception.js
    objectives.js
    pathfinding.js
    gameSim.js
  audio/
    audioManager.js
    musicDirector.js
  render/
    assetLoader.js
    camera.js
    lightingCanvas.js
    hudRenderer.js
    renderer.js
  app/
    titleScreen.js
    app.js

assets/
  map.json
  sprites/
    manifest.json
  audio/
    manifest.json

scripts/
  validate-map.mjs

tests/
  setup/
    mockCanvas2d.js
    factories.js
  fixtures/
    mapFactory.js
  core/
    math2d.test.js
    rng.test.js
    eventBus.test.js
    input.test.js
  game/
    map.test.js
    collision.test.js
    los.test.js
    pathfinding.test.js
    player.test.js
    lighting.test.js
    perception.test.js
    hollow.test.js
    gate.test.js
    pickups.test.js
    gameSim.test.js
  integration/
    audio.test.js
    hud.test.js
    fullRoute.test.js
    gateUnderThreat.test.js
    retry.test.js
  render/
    renderer.test.js
  map/
    validate-map.test.js
  performance/
    budget.test.js
```

### File Responsibilities

| File | Responsibility |
|---|---|
| `index.html` | Loads the canvas, title overlay, end-screen overlay, and `src/main.js`. |
| `styles.css` | Layout, scaling, overlays, font fallbacks. No gameplay logic. |
| `src/main.js` | Browser bootstrap. Creates App, wires input, canvas, audio, assets. |
| `src/config/defaultConfig.js` | Single source of truth for gameplay constants. Tests may override. |
| `src/core/clock.js` | Deterministic clock abstraction. |
| `src/core/rng.js` | Seeded RNG for deterministic AI waypoint choices. |
| `src/core/eventBus.js` | Minimal event pub/sub used by sim, audio, and HUD. |
| `src/core/input.js` | Keyboard state and action mapping. Testable without DOM by injecting actions. |
| `src/core/loop.js` | Fixed-timestep update loop for browser. |
| `src/core/math2d.js` | Vector, distance, angle, clamp, lerp, smoothstep. |
| `src/game/map.js` | Loads and validates map JSON. Provides tile queries. |
| `src/game/player.js` | Player movement, breath, fuel, lantern, cover, pickups, gate interaction. |
| `src/game/hollow.js` | The Hollow state machine, perception response, movement, safe-zone behavior. |
| `src/game/gate.js` | Gate state, hold-to-open, threshold rules. |
| `src/game/lighting.js` | Light radius, safe zone predicate, visible range. |
| `src/game/perception.js` | Sight, hearing, line of sight, cover. |
| `src/game/objectives.js` | Objective target selection and compass arrow. |
| `src/game/pathfinding.js` | A*, line-of-sight DDA, nearest reachable fallback. |
| `src/game/gameSim.js` | Top-level run state. Owns player, hollow, gate, pickups, timers, win/fail checks. |
| `src/audio/audioManager.js` | Loads audio manifest, plays one-shots, manages loops and layers. |
| `src/audio/musicDirector.js` | Maps semantic game events to music layer changes. |
| `src/render/assetLoader.js` | Loads sprites and audio. Provides placeholders if assets are missing. |
| `src/render/camera.js` | Camera position and viewport culling. |
| `src/render/lightingCanvas.js` | Offscreen darkness and lantern light rendering. |
| `src/render/hudRenderer.js` | Canvas HUD drawing. |
| `src/render/renderer.js` | Orchestrates visible tile, entity, prop, lighting, and HUD rendering. |
| `src/app/titleScreen.js` | DOM title screen. |
| `src/app/app.js` | Wires App, Sim, Renderer, AudioManager, input, and retry. |
| `assets/map.json` | The one handcrafted map. |
| `assets/sprites/manifest.json` | Sprite asset contract. |
| `assets/audio/manifest.json` | Audio asset contract. |
| `scripts/validate-map.mjs` | Standalone map contract validator. |
| `tests/**` | Automated validation. |

---

## 4. Runtime Architecture

The game is split into three layers.

```text
Input / Clock
      |
      v
GameSim  <-- deterministic, no DOM, no canvas, no audio
      |
      +--> Event Bus
      |
      +--> Renderer
      +--> AudioManager
```

Rules:

1. `GameSim` must not touch `document`, `window`, `canvas`, `AudioContext`, or assets.
2. `GameSim` receives a fixed `dt` and an `InputFrame`.
3. `GameSim` emits semantic events.
4. `Renderer` reads a sim snapshot and draws. It must not mutate sim state.
5. `AudioManager` listens to events and plays assets. It must not mutate sim state.
6. The browser App owns the real clock and input.
7. Tests inject a fake clock, fake input, and mock audio.

This separation is required so the game can be validated without a browser.

---

## 5. Fixed Timestep

The simulation uses a fixed update step.

```text
UPDATE_DT = 1 / 60
```

Browser loop:

```text
accumulator += realFrameDelta
accumulator = min(accumulator, 0.25)
while accumulator >= UPDATE_DT:
  sim.update(UPDATE_DT, inputFrame)
  accumulator -= UPDATE_DT
render()
```

Why:

- Collision and pathing are deterministic.
- Tests can call `sim.update(UPDATE_DT)` repeatedly.
- Large real-frame delays cannot cause tunneling.
- No interpolation is required at this scale.

---

## 6. Configuration

All gameplay numbers must come from `DEFAULT_CONFIG`.

Tests may override config values, for example:

```js
{
  hollowEnabled: false,
  hollowWake: 100000,
  duration: 480
}
```

The real game uses defaults.

### Required Defaults

```js
export const DEFAULT_CONFIG = {
  map: {
    width: 120,
    height: 80,
    tileSize: 40,
    viewWidth: 24,
    viewHeight: 16
  },

  frame: {
    updateDt: 1 / 60,
    maxFrameDelay: 0.25
  },

  run: {
    duration: 480,
    dawnWarning: 60,
    hollowWake: 90,
    hollowWakingDuration: 8
  },

  player: {
    radius: 0.5,
    walkSpeed: 3.6,
    sprintSpeed: 6.0,
    underbrushSpeedMultiplier: 0.85,
    startFuel: 50,
    maxFuel: 100,
    fuelDrainPerSecond: 0.5,
    safeFuelThreshold: 25,
    startBreath: 100,
    maxBreath: 100,
    sprintDrainPerSecond: 20,
    walkRecoveryPerSecond: 15,
    standRecoveryPerSecond: 30,
    breathUnlockThreshold: 25,
    pickupRadius: 0.75,
    gateInteractRadius: 1.5
  },

  hollow: {
    radius: 0.6,
    underbrushSpeedMultiplier: 0.85,
    speeds: {
      sleeping: 0,
      waking: 0,
      curious: 2.4,
      investigating: 3.2,
      searching: 3.2,
      hunting: 5.0
    },
    patrolRadius: 6,
    investigateDuration: 8,
    searchDuration: 12,
    huntLostDuration: 6,
    pathRecalcInterval: 0.5
  },

  light: {
    baseRadius: 4,
    radiusPerFuel: 0.04,
    visibilityBonus: 2,
    coveredAmbientRange: 3,
    uncoveredAmbientRange: 6
  },

  noise: {
    walk: 5,
    sprint: 10,
    sprintUnderbrush: 12,
    keyPickup: 6,
    emberPickup: 4,
    gateOpen: 12
  },

  gate: {
    x: 60,
    y: 5,
    gapX: [59, 60, 61],
    gapYMin: 3,
    gapYMax: 5,
    holdTime: 2,
    chargeDecayPerSecond: 4,
    winY: 6
  }
};
```

### Why Config Exists

- Tests can override values without editing gameplay constants.
- The integration agent can find every gameplay number in one place.
- Future tuning does not require searching through systems.

---

## 7. Coordinate System

- Tile coordinates use integer tile indices.
- `x` increases east.
- `y` increases south.
- `y = 0` is the northern border.
- Entity positions are floating-point tile units.
- A position of `{ x: 60, y: 72 }` is the center of tile `(60, 72)`.
- Pixel position:

```text
pixel.x = (tileX + 0.5) * TILE_SIZE
pixel.y = (tileY + 0.5) * TILE_SIZE
```

---

## 8. Map Contract

The map is a static JSON asset. There is no runtime procedural generation.

### Tile Characters

| Char | Tile | Passable | Blocks Sight/Sound | Movement |
|---:|---|---:|---:|---|
| `g` | Grass | Yes | No | Normal |
| `p` | Path | Yes | No | Normal |
| `u` | Underbrush | Yes | No | 85% speed, cover |
| `t` | Tree | No | Yes | Impassable |
| `r` | Rock | No | Yes | Impassable |
| `w` | Water | No | Yes | Impassable |

### Map JSON Shape

```json
{
  "version": 1,
  "width": 120,
  "height": 80,
  "tiles": [
    "ttttttt...",
    "ttttttt..."
  ],
  "objects": {
    "playerStart": { "x": 60, "y": 72 },
    "deadWell": { "x": 60, "y": 40 },
    "hollow": { "x": 60, "y": 40 },
    "gate": { "x": 60, "y": 5 },
    "keys": [
      { "id": "A", "x": 95, "y": 60 },
      { "id": "B", "x": 22, "y": 26 },
      { "id": "C", "x": 64, "y": 42 }
    ],
    "embers": [
      { "id": "E1", "x": 88, "y": 57 },
      { "id": "E2", "x": 25, "y": 30 },
      { "id": "E3", "x": 88, "y": 22 },
      { "id": "E4", "x": 58, "y": 45 },
      { "id": "E5", "x": 58, "y": 10 }
    ]
  }
}
```

### Mandatory Map Rules

The validator must fail if any of these rules are violated.

1. Width is `120`, height is `80`.
2. Every tile row has exactly `width` characters.
3. Only valid tile characters are used.
4. All outer border tiles are impassable:
   - `x = 0`
   - `x = width - 1`
   - `y = 0`
   - `y = height - 1`
5. Gate threshold gap:
   - Rows `y = 3, 4, 5` are impassable except `x = 59, 60, 61`.
   - Rows `y = 0, 1, 2` are impassable.
   - The gate gap tiles must be passable in the static map because the gate dynamically blocks or opens them.
6. All required objects are inside the map.
7. All required objects are on passable tiles:
   - Player start
   - Keys
   - Embers
   - Dead Well
   - Hollow wake point
   - Gate approach tile `(60, 6)`
8. There are exactly 3 keys and 5 embers.
9. Key and ember IDs are unique.
10. All required objects are reachable from the player start using static passability.
11. The gate approach tile `(60, 6)` is passable.
12. The Dead Well is at `(60, 40)` and is passable.
13. There are at least 8 underbrush clusters.
14. At least 2 underbrush clusters are within Chebyshev distance 6 of the gate approach `(60, 6)`.
15. Route length targets are met using A* and Euclidean path length.

### Underbrush Cluster Rule

An underbrush cluster is a 4-connected component of underbrush tiles.

A cluster counts if it has at least 9 underbrush tiles.

This matches the gameplay requirement that clusters are 3 to 4 tiles wide and large enough for hiding.

### Corridor Width Rule

This is a hard map validation rule because narrow corridors can make stealth and The Hollow’s pathing unfair.

For every passable tile:

1. Count passable 4-neighbor tiles.
2. Ignore the corridor check for tiles that are:
   - A required object tile.
   - Within Chebyshev distance 1 of a required object.
   - Part of the gate gap.
   - Part of a passable connected component with area at least 100 tiles.
3. For remaining tiles, passable 4-neighbor count must be at least 3.

Why:

- A 1-wide corridor usually has only 2 passable 4-neighbors.
- A 2-wide corridor usually has at least 3.
- Large open clearings are exempt because edge tiles can naturally have fewer neighbors.

This is not a perfect geometry proof, but it is a cheap, deterministic guard against obvious 1-tile corridors.

### Route Length Targets

The validator must compute A* paths using static passability and tile costs.

Path length is measured as the Euclidean polyline length in tiles between tile centers.

Required ordered route checks:

| Route | Minimum | Maximum |
|---|---:|---:|
| Start to Key A | 120 | 160 |
| Key A to Key C | 120 | 160 |
| Key C to Key B | 160 | 200 |
| Key B to Gate Approach | 160 | 200 |

Total expected route length:

| Minimum | Maximum |
|---:|---:|
| 550 | 750 |

Gate approach target is `(60, 6)`, not the gate tile, because the gate may be closed.

Why this matters:

- The map must be long enough that the player cannot simply outrun The Hollow’s wake time by sprinting.
- The 8-minute dawn limit creates real pressure.

---

## 9. Core Systems

### Clock

The sim must not use `Date.now()` internally.

Real app:

```js
const clock = new SystemClock();
```

Tests:

```js
const clock = new FakeClock();
```

Required interface:

```js
clock.now()
clock.advance(seconds)
```

### RNG

Use a seeded 32-bit RNG.

Required:

```js
const rng = new SeededRng(seed);
rng.nextFloat()
rng.nextInt(min, max)
```

Why:

- The Hollow waypoint choices must be reproducible in tests.
- Different runs can use different seeds in the real app.

### Event Bus

Minimal pub/sub.

```js
bus.on(event, handler)
bus.off(event, handler)
bus.emit(event, payload)
```

Events must be semantic, not asset-specific.

Examples:

```text
run.start
run.win
run.fail.caught
run.fail.dawn
hollow.wake
hollow.state_change
pickup.key
pickup.ember
gate.open
dawn.warning
player.fuel.low
player.breath.locked
onboarding.show
```

### Input

Actions:

| Action | Keys |
|---|---|
| Move up | W / ArrowUp |
| Move down | S / ArrowDown |
| Move left | A / ArrowLeft |
| Move right | D / ArrowRight |
| Sprint | Shift / Space |
| Lantern | L |
| Interact | E |
| Retry | R |

Input frame:

```js
{
  moveX: -1 | 0 | 1,
  moveY: -1 | 0 | 1,
  sprint: boolean,
  lanternJustPressed: boolean,
  interactHeld: boolean,
  retryJustPressed: boolean
}
```

The real keyboard handler must `preventDefault()` for game keys to stop arrow-key page scrolling.

---

## 10. Map Class

`Map` loads the map JSON and exposes fast tile queries.

### Tile Storage

Use a `Uint8Array`:

```text
0 GRASS
1 PATH
2 UNDERBRUSH
3 TREE
4 ROCK
5 WATER
```

### Required Methods

```js
map.width
map.height
map.tileAt(tx, ty)
map.isPassable(tx, ty)
map.isBlocking(tx, ty)
map.isUnderbrush(tx, ty)
map.tileCost(tx, ty)
map.objectAt(tx, ty)
```

`tileCost`:

| Tile | Cost |
|---|---:|
| Grass / Path | 1.0 |
| Underbrush | 1.25 |
| Impassable | Infinity |

### Dynamic Blocking

Dynamic blocking is not stored in the map. It is computed by the sim.

For the player:

```text
blockedForPlayer(tx, ty) =
  !map.isPassable(tx, ty)
  or
  (!gate.open and tile is in gate gap)
```

For The Hollow:

```text
blockedForHollow(tx, ty) =
  blockedForPlayer(tx, ty)
  or
  (gate.open and ty < config.gate.winY)
  or
  (light.safeActive and tile is within player light radius)
```

Why:

- The static map remains immutable.
- Light safe zones and gate state can change every frame.
- Pathfinding can accept a predicate instead of a modified map.

---

## 11. Collision

Use continuous circle-vs-tile collision.

### Circle Size

- Player radius: `0.5` tiles.
- The Hollow radius: `0.6` tiles.

### Movement Resolution

Move axis-by-axis.

```text
attempt dx
resolve collision on x
attempt dy
resolve collision on y
```

Why axis separation:

- Simpler and stable enough for top-down movement.
- Prevents corner clipping when combined with diagonal corner checks in pathfinding.
- Easy to test.

### Diagonal Corner Rule

A* may not move diagonally from `(x, y)` to `(x + dx, y + dy)` if either:

```text
(x + dx, y) is blocked
(x, y + dy) is blocked
```

This prevents entities from visually clipping around tree corners.

### Collision Tests Must Verify

- Player cannot enter trees, rocks, or water.
- Player can enter underbrush.
- Player can move diagonally through open space.
- Player cannot cut diagonal corners around blockers.
- Gate gap blocks player when closed.
- Gate gap allows player when open.
- The Hollow cannot enter active safe tiles.
- The Hollow can remain in a tile that becomes safe.

---

## 12. Line of Sight

Use a grid raycast.

Required algorithm: supercover DDA over the tile grid.

Rules:

- Blocked by tree, rock, water.
- Not blocked by underbrush.
- Not blocked by gate gap for sight/sound, except dynamic impassability is separate from LOS.
- If start or target tile is blocking, treat as blocked.

Why DDA instead of pixel sampling:

- Deterministic.
- Fast.
- Independent of render resolution.
- Matches grid-based cover rules.

---

## 13. Player

### Position and State

```js
player = {
  pos: { x, y },
  lanternOn: boolean,
  fuel: number,
  breath: number,
  breathLocked: boolean,
  keysCollected: 0 | 1 | 2 | 3,
  covered: boolean,
  inUnderbrush: boolean,
  moving: boolean,
  sprinting: boolean,
  currentNoiseRadius: number,
  lastStepTime: number,
  gateCharge: number
}
```

### Movement

Each update:

1. Read input.
2. Normalize movement vector.
3. Determine `inUnderbrush` from tile under player center.
4. Determine if sprint is allowed:
   - Input sprint is true.
   - Breath is greater than 0.
   - Breath is not locked.
5. Base speed:
   - Sprint allowed and moving: `6.0`
   - Otherwise: `3.6`
6. If `inUnderbrush`, multiply speed by `0.85`.
7. Attempt movement with collision.
8. If actual displacement is greater than `0.0001`, `moving = true`.

### Breath

Rules:

- Sprinting drains `20 / s`.
- Walking recovers `15 / s`.
- Standing still recovers `30 / s`.
- Breath is clamped to `0..100`.
- If breath reaches `0`:
  - Set `breathLocked = true`.
  - Emit `player.breath.locked`.
- If `breathLocked` and breath reaches `25`:
  - Set `breathLocked = false`.

Sprint is allowed only while:

```text
breath > 0 and breathLocked == false
```

### Fuel

Rules:

- If lantern is on:
  - `fuel -= 0.5 * dt`
- Clamp fuel to `0..100`.
- If fuel crosses below `20`:
  - Emit `player.fuel.low` once.
- If fuel increases back above `20`:
  - Reset fuel low warning flag.
- Ember pickup adds `40`, capped at `100`.

### Lantern

- `L` toggles `lanternOn`.
- If `lanternOn` and `fuel > 0`, light radius exists.
- If `fuel == 0`, light radius is `0` even if `lanternOn` is true.

Why not force lantern off at zero:

- Keeps player intent readable.
- The light system already produces radius `0`.
- Avoids unexpected state changes.

### Cover

Player is covered if:

1. Player center tile is underbrush, or
2. Any of the 4 orthogonal adjacent tiles is blocking.

Use 4-neighbor adjacency, not 8-neighbor.

Why:

- Readable.
- Prevents too much cover from diagonal corners.
- Easier to test.

### Noise

Continuous noise:

| Condition | Noise Radius |
|---|---:|
| Walking | 5 |
| Sprinting | 10 |
| Sprinting in underbrush | 12 |
| Standing still | 0 |

Event noise:

| Event | Radius |
|---|---:|
| Key pickup | 6 |
| Ember pickup | 4 |
| Gate open | 12 |

Event noises are stored in a short queue during player update and consumed by The Hollow in its update.

### Pickup

Pickup occurs when center distance is less than or equal to `0.75` tiles.

Why `0.75`:

- Slightly larger than the player hitbox, so pickups feel responsive.
- Small enough to avoid accidental long-range collection.

On key pickup:

- Increase `keysCollected`.
- Emit `pickup.key`.
- Create noise event radius `6`.

On ember pickup:

- Add `40` fuel, capped at `100`.
- Emit `pickup.ember`.
- Create noise event radius `4`.

Pickups must be removed from active pickups so they cannot be collected twice.

### Gate Interaction

Player can interact with the gate when:

```text
distance(player.pos, gate.center) <= config.player.gateInteractRadius
```

If `keysCollected < 3`:

- Prompt shows locked.
- No charge accumulates.

If `keysCollected == 3` and gate is closed:

- If `interactHeld` is true:
  - `gateCharge += dt`
- Else:
  - `gateCharge = max(0, gateCharge - 4 * dt)`
- If `gateCharge >= 2`:
  - Open gate.

Why decay instead of reset:

- Matches visual spec: the ring shrinks quickly if released early.
- Still deterministic and testable.

---

## 14. Light and Safe Zones

### Light Radius

If lantern is on and fuel is greater than 0:

```text
lightRadius = 4 + fuel * 0.04
```

Otherwise:

```text
lightRadius = 0
```

### Player Visible Range

The Hollow’s sight range when it is looking at the player:

| Condition | Sight Range |
|---|---:|
| Light radius > 0 | `lightRadius + 2` |
| Lantern off or fuel 0, player covered | `3` |
| Lantern off or fuel 0, player uncovered | `6` |

### Safe Zone

Safe zone is active when:

```text
lanternOn == true
and fuel >= 25
and lightRadius > 0
```

A tile is safe for The Hollow if:

```text
safeActive == true
and distance(tileCenter, player.pos) <= lightRadius
```

Use tile center distance.

Why tile center:

- Consistent with pathfinding.
- Easy to reason about.
- Prevents edge flicker from using tile corners.

### Safe Zone Transition

The Hollow may already be in a tile that becomes safe.

It may remain there.

It may not enter a new safe tile.

It may move out if its path allows it.

Why:

- Prevents permanent trapping inside player light.
- Keeps light as a defense without making it a wall that can lock The Hollow forever.

---

## 15. Perception

The Hollow detects the player through sight and hearing.

### Sight

The Hollow sees the player if:

1. The Hollow is not Sleeping or Waking.
2. Distance between centers is less than or equal to sight range.
3. Line of sight is not blocked.

Sight range is determined by player lantern and cover:

| Player Lantern | Player Condition | Sight Range |
|---|---|---:|
| On, fuel > 0 | Any | `lightRadius + 2` |
| Off or fuel 0 | Covered | `3` |
| Off or fuel 0 | Uncovered | `6` |

### Hearing

The Hollow hears the player if:

1. The Hollow is not Sleeping or Waking.
2. Distance between centers is less than or equal to noise radius.
3. Line of sight is not blocked.
4. Underbrush does not block sound.

Continuous noise radius comes from player state.

Event noises are one-time.

### Detection Result

```js
{
  seen: boolean,
  heard: boolean,
  lastKnown: { x, y } | null
}
```

If either `seen` or `heard` is true:

- The Hollow updates `lastKnown` to the player’s current position.
- The Hollow resets its lost-timer for the current relevant state.

---

## 16. The Hollow State Machine

States:

```text
Sleeping
Waking
Curious
Investigating
Searching
Hunting
```

### Sleeping

- Duration: until `runElapsed >= 90`.
- Movement: none.
- Detection: none.
- Damage: none.

Transition:

```text
if runElapsed >= config.run.hollowWake:
  state = Waking
  stateTimer = 0
  emit hollow.wake
```

### Waking

- Duration: `8` seconds.
- Location: Dead Well.
- Movement: none.
- Detection: none.
- Damage: none.

Transition:

```text
if stateTimer >= 8:
  state = Curious
  emit hollow.state_change
  recalculate path
```

### Curious

- Speed: `2.4`
- Behavior:
  - Patrols within 6 tiles of Dead Well.
  - Chooses a new waypoint every 2 seconds or when reached.
  - Avoids active safe tiles.
- Transition:
  - If player detected: `Investigating`.

### Investigating

- Speed: `3.2`
- Duration: up to `8` seconds.
- Target: last known player position.
- Transition:
  - If player detected: `Hunting`.
  - If target reached or timer expires: `Searching`.

If last known position is inside a safe zone, The Hollow targets the nearest reachable tile that is closest to the target but not blocked by safe tiles.

### Searching

- Speed: `3.2`
- Duration: `12` seconds.
- Target: random waypoints within 6 tiles of last known position.
- Transition:
  - If player detected: `Hunting`.
  - If timer expires: `Curious`.

### Hunting

- Speed: `5.0`
- Behavior:
  - If player is detected, target player’s current position.
  - If player is not detected, target last known position.
  - If no detection for `6` seconds: `Searching`.
  - If player is inside a safe zone, target the nearest reachable tile outside the safe zone and wait.

### State Change Cues

The sim emits:

```text
hollow.state_change
```

with payload:

```js
{
  from: string,
  to: string
}
```

The audio and renderer use this.

### Why This Exact State Machine

It matches `gameplay.md` and gives the player readable phases:

- Sleeping: safe beginning.
- Waking: telegraph.
- Curious: local threat.
- Investigating: The Hollow reacted to a specific spot.
- Searching: hiding can work for a bounded time.
- Hunting: immediate chase.

---

## 17. Pathfinding

Use A* on the tile grid.

### Search Space

- 8-directional movement.
- Impassable tiles are invalid.
- Dynamic blocked tiles are invalid through a predicate.
- Diagonal moves are disallowed if either orthogonal corner is blocked.

### Tile Cost

| Tile | Cost |
|---|---:|
| Grass / Path | 1.0 |
| Underbrush | 1.25 |
| Impassable | Infinity |
| Dynamic blocked | Infinity |

### Heuristic

Use octile distance:

```text
dx = abs(ax - bx)
dy = abs(ay - by)
h = max(dx, dy) + (Math.SQRT2 - 1) * min(dx, dy)
```

### Path Output

A* returns an array of tile coordinates:

```js
[
  { x, y },
  { x, y },
  ...
]
```

The first tile is the start. The last tile is the target.

If no path exists, return `null`.

### No-Path Fallback

If The Hollow cannot path to its target:

1. Run BFS from The Hollow using the same blocked predicate.
2. Choose the reachable tile with minimum Euclidean distance to the target.
3. Move to that tile.
4. If none is reachable, wait at current position.

Why:

- The Hollow must not teleport.
- It must not path through blockers.
- It should feel like a physical entity trapped by light or geometry.

### Recalculation

The Hollow recalculates every `0.5` seconds.

It also recalculates immediately when:

- State changes.
- The player enters or exits a safe zone.
- Player fuel drops below `25`.
- The player is detected in a new location.
- Gate opens or threshold changes.

### Performance

Use typed arrays:

```text
Int32Array parent
Float32Array gScore
Uint8Array closed
```

Use a binary heap for the open list.

The map has 9600 tiles, so A* is cheap enough for 2 Hz updates.

---

## 18. Gate

### Gate State

```js
gate = {
  open: false,
  charge: 0
}
```

### Gate Gap

The gate gap is:

```text
x in [59, 60, 61]
y in [3, 4, 5]
```

When closed:

- Gap tiles are blocked for the player.
- The gate is visually sealed.

When open:

- Gap tiles are passable for the player.
- The Hollow cannot enter any tile where `y < 6`.

### Win Threshold

The player wins when:

```text
gate.open == true
and player.pos.y < 6
```

### Threshold Exclusion

Once the gate is open:

- The Hollow cannot enter `y < 6`.
- If The Hollow is already in `y < 6` when the gate opens:
  - Move The Hollow to the nearest reachable tile where `y >= 6`.
  - Do not damage The Hollow.
  - Do not trigger a fail unless The Hollow is still overlapping the player before the win check.

Why:

- Prevents an unfair last-tile interaction.
- Keeps the threshold visually and mechanically safe.

### Gate Opening Event

When the gate opens:

- Emit `gate.open`.
- Create noise event radius `12`.
- If The Hollow is in threshold, relocate.

---

## 19. Objectives and Compass Arrow

### Objective Target

Before all keys are collected:

- Target is the nearest uncollected key by Euclidean distance.
- Ties resolve by key ID order: `A`, `B`, `C`.

After all keys are collected:

- If gate is closed:
  - Target is gate approach `(60, 6)`.
- If gate is open:
  - Target is gate gap center `(60, 4)`.

### Arrow Update

Update the arrow twice per second.

Algorithm:

1. Determine target tile.
2. Run A* from player tile to target tile using static player passability.
3. If path exists, arrow points toward the first waypoint after the player’s current tile.
4. If path fails, arrow points straight to the target.
5. If target is on-screen, hide arrow.
6. If target is off-screen, show arrow.

### Why A* Arrow

The arrow should point toward the next meaningful way around obstacles, not through walls.

### Why 2 Hz

- Compass does not need per-frame updates.
- Avoids visual jitter.
- Saves pathfinding budget.

---

## 20. GameSim

`GameSim` owns the run.

### Creation

```js
const sim = createSim({
  map,
  config,
  seed,
  eventBus
});
```

### Initial State

When a run starts:

```text
state = Playing
player.pos = map.objects.playerStart
player.fuel = 50
player.breath = 100
player.lanternOn = true
player.keysCollected = 0
dawnRemaining = 480
gate.open = false
hollow.state = Sleeping
hollow.pos = map.objects.hollow
```

### Update Order

Each `sim.update(dt, input)`:

1. If state is not `Playing`, return.
2. Advance run elapsed and dawn remaining.
   - Do not fail on dawn yet.
3. Update player.
4. Process gate interaction.
5. Update pickups and noise events.
6. Update The Hollow.
7. Check win condition.
8. Check fail by Hollow contact.
9. Check fail by dawn.
10. Update HUD state and objective arrow timer.

Why this order:

- Player movement happens first so detection uses the player’s new position.
- Win is checked before fail, satisfying same-frame win priority.
- Contact fail is checked before dawn fail, matching the gameplay frame priority.

### Win Condition

```text
gate.open == true
and player.pos.y < 6
```

Emit:

```text
run.win
```

### Fail: Caught

```text
distance(player.pos, hollow.pos) <= player.radius + hollow.radius
```

Emit:

```text
run.fail.caught
```

### Fail: Dawn

```text
dawnRemaining <= 0
```

Emit:

```text
run.fail.dawn
```

### Retry

`sim.retry()` creates a new run:

- Resets player position.
- Resets fuel, breath, keys.
- Resets pickups.
- Resets gate.
- Resets The Hollow to Sleeping.
- Resets dawn timer.
- Resets RNG to a new or supplied seed.
- Emits `run.start`.

---

## 21. HUD Contract

The HUD is rendered by `hudRenderer.js`, but the data comes from the sim.

Sim exposes:

```js
sim.hud = {
  state: 'title' | 'playing' | 'won' | 'failed',
  timeRemaining: number,
  fuel: number,
  breath: number,
  breathLocked: boolean,
  keysCollected: number,
  objectiveText: string,
  arrow: {
    visible: boolean,
    angle: number
  },
  prompt: {
    type: 'none' | 'locked' | 'hold' | 'open',
    text: string,
    progress: number
  },
  warnings: {
    fuelLow: boolean,
    dawnLow: boolean
  }
}
```

### Objective Text

| Condition | Text |
|---|---|
| Keys 0 | `Find the bone keys` |
| Keys 1 or 2, not at gate | `Find the remaining bone keys` |
| Near gate, keys missing | `The gate is sealed (x / 3)` |
| Near gate, keys complete, gate closed | `Hold to open the gate` |
| Keys complete, not at gate | `Escape before dawn` |
| Gate open | `Cross the threshold` |

### Prompt

| Condition | Prompt |
|---|---|
| Near gate, keys missing | `Sealed (x / 3)` |
| Near gate, keys complete, gate closed | `Hold E to open` with circular progress |
| Gate open near player | `The gate is open` |

### Warnings

- Fuel low: `fuel < 20`
- Dawn low: `timeRemaining < 60`

Warnings must use shape, pulse, or icon changes, not only color.

---

## 22. Rendering Contract

The renderer uses one fixed internal canvas:

```text
960 x 640
```

The page scales the canvas while preserving aspect ratio.

### Camera

The camera follows the player and keeps the player centered.

View size:

```text
24 tiles wide
16 tiles tall
```

Camera clamp:

```text
camera.x = clamp(player.x - viewWidth / 2, 0, map.width - viewWidth)
camera.y = clamp(player.y - viewHeight / 2, 0, map.height - viewHeight)
```

If the map is smaller than the view, center the map.

### Culling

Render only visible tiles.

Visible range:

```text
x0 = floor(camera.x)
y0 = floor(camera.y)
x1 = min(map.width - 1, ceil(camera.x + viewWidth))
y1 = min(map.height - 1, ceil(camera.y + viewHeight))
```

Why:

- The map is 120x80, but only about 24x16 tiles are visible.
- A full-map prerendered canvas would be large.
- Visible-tile drawing is enough for this game.

### Layer Order

Use the visual designer’s layer order.

1. Base ground
2. Ground decals
3. Underbrush
4. Objective glows
5. Entities
6. Vertical props
7. Weather and mist
8. Lighting mask
9. Screen effects
10. HUD

Entities and vertical props should be sorted by `y` within their layer to preserve top-down readability.

### Lighting

Use an offscreen light canvas at internal resolution.

For each frame:

1. Fill light canvas with darkness.
2. Cut out the player’s visible range.
3. Draw light canvas onto the main canvas.

Lantern on:

- Warm radial gradient.
- Bright inner radius: `lightRadius * TILE_SIZE`
- Dim outer radius: `(lightRadius + 2) * TILE_SIZE`

Lantern off:

- Cold ambient halo.
- Covered range: `3 * TILE_SIZE`
- Uncovered range: `6 * TILE_SIZE`

Safe zone edge:

- Draw a soft ring when safe zone is active.
- Flicker when fuel is below 30.
- Fade when fuel is below 25.

Dawn grade:

- Blend toward Dawn Gold as `timeRemaining` approaches 0.
- Keep it subtle until the final minute.

### HUD Rendering

Canvas HUD draws:

- Dawn timer top-left.
- Moon/sun dial top-left.
- Objective text top-center.
- Key slots top-center.
- Fuel bar top-right.
- Breath bar below fuel.
- Objective arrow at screen edge.
- Interaction prompt near player.
- Onboarding messages bottom-center.

No minimap.

No health bar.

No enemy marker.

---

## 23. Audio Contract

The visual designer has defined the audio direction. Engineering only implements it.

### Audio Manifest

`assets/audio/manifest.json` must define music loops/layers and one-shot SFX.

Example:

```json
{
  "music": {
    "nightBed": {
      "file": "music/nightbed.ogg",
      "loop": true,
      "volume": 0.55
    },
    "mystery": {
      "file": "music/mystery.ogg",
      "loop": true,
      "volume": 0.45
    },
    "pressure": {
      "file": "music/pressure.ogg",
      "loop": true,
      "volume": 0.50
    },
    "escape": {
      "file": "music/escape.ogg",
      "loop": true,
      "volume": 0.55
    },
    "dawnResolve": {
      "file": "music/dawnResolve.ogg",
      "loop": false,
      "volume": 0.65
    },
    "caughtDrone": {
      "file": "music/caughtDrone.ogg",
      "loop": false,
      "volume": 0.65
    }
  },
  "sfx": {
    "hollow_wake": { "file": "sfx/hollow_wake.ogg", "volume": 0.9 },
    "hollow_state": { "file": "sfx/hollow_state.ogg", "volume": 0.8 },
    "hollow_hunt": { "file": "sfx/hollow_hunt.ogg", "volume": 0.9 },
    "fuel_low": { "file": "sfx/fuel_low.ogg", "volume": 0.7 },
    "key_pickup": { "file": "sfx/key_pickup.ogg", "volume": 0.9 },
    "ember_pickup": { "file": "sfx/ember_pickup.ogg", "volume": 0.85 },
    "gate_ready": { "file": "sfx/gate_ready.ogg", "volume": 0.7 },
    "gate_open": { "file": "sfx/gate_open.ogg", "volume": 1.0 },
    "caught": { "file": "sfx/caught.ogg", "volume": 1.0 },
    "dawn_fail": { "file": "sfx/dawn_fail.ogg", "volume": 0.9 },
    "walk": { "file": "sfx/walk.ogg", "volume": 0.55 },
    "sprint": { "file": "sfx/sprint.ogg", "volume": 0.7 },
    "walk_underbrush": { "file": "sfx/walk_underbrush.ogg", "volume": 0.6 },
    "sprint_underbrush": { "file": "sfx/sprint_underbrush.ogg", "volume": 0.8 },
    "lantern_on": { "file": "sfx/lantern_on.ogg", "volume": 0.7 },
    "lantern_off": { "file": "sfx/lantern_off.ogg", "volume": 0.6 },
    "breath_locked": { "file": "sfx/breath_locked.ogg", "volume": 0.75 }
  }
}
```

### AudioManager

Required interface:

```js
audio.play(name)
audio.startLayer(name)
audio.stopLayer(name)
audio.setPhase(phase)
audio.resume()
```

Audio must start after a user gesture because of browser autoplay policy.

### Music Director

Semantic event mapping:

| Sim Event | Audio Action |
|---|---|
| `run.start` | Start `nightBed` and `mystery`. |
| `hollow.wake` | Stop `mystery`, start `pressure`, play `hollow_wake`. |
| `hollow.state_change` to `Hunting` | Play `hollow_hunt`. |
| `hollow.state_change` to other active states | Play `hollow_state`. |
| `player.fuel.low` | Play `fuel_low`. |
| `dawn.warning` | Start `escape`. |
| `gate.open` | Play `gate_open`. |
| `run.win` | Stop all, play `dawnResolve`. |
| `run.fail.caught` | Stop all, play `caught`, optionally play `caughtDrone`. |
| `run.fail.dawn` | Stop all, play `dawn_fail`. |

### Footsteps

Player emits `player.step` with a type:

```text
walk
sprint
walk_underbrush
sprint_underbrush
```

Rate:

- Walk: every `0.35s` while moving.
- Sprint: every `0.20s` while moving.

Why distance/time based:

- Simpler than audio distance panning.
- Enough for a top-down game.
- Deterministic in tests.

---

## 24. Onboarding Cues

These are per-run, not persisted.

Show small bottom-center text for 2 seconds:

| First Action | Text |
|---|---|
| First movement | `Move` |
| First sprint | `Sprint` |
| First lantern toggle | `Lantern` |

When the first key is off-screen, the objective arrow may pulse once.

Why:

- The first 90 seconds are the safe teaching phase.
- Cues should be diegetic and minimal.
- No separate tutorial screen is needed.

---

## 25. Test Harness

The test harness uses Vitest.

### Package.json

```json
{
  "type": "module",
  "scripts": {
    "test": "vitest run",
    "map:validate": "node scripts/validate-map.mjs",
    "ci": "npm run map:validate && npm test"
  },
  "devDependencies": {
    "vitest": "^3"
  }
}
```

No other required dependencies.

### Test Factory

`tests/setup/factories.js` must expose:

```js
createSim({ map, config, seed, audio, input } = {})
createMockAudio()
createMockInput()
createMapFixture()
loadRealMap()
advanceSim(sim, seconds, inputFactory)
```

### Mock Audio

`createMockAudio()` returns an object that records calls:

```js
{
  calls: [],
  play(name) { this.calls.push(['play', name]); },
  startLayer(name) { this.calls.push(['startLayer', name]); },
  stopLayer(name) { this.calls.push(['stopLayer', name]); },
  setPhase(phase) { this.calls.push(['setPhase', phase]); }
}
```

Why:

- Audio is an integration concern.
- Tests must verify required cues without real audio files.

### Mock Canvas

`tests/setup/mockCanvas2d.js` provides a stub `Canvas2DContext` for renderer tests.

Required supported methods:

```text
clearRect
fillRect
strokeRect
drawImage
save
restore
translate
scale
rotate
beginPath
moveTo
lineTo
closePath
stroke
fill
createLinearGradient
createRadialGradient
```

Gradients must return an object with `addColorStop`.

Why:

- Renderer tests must not require a real browser canvas.
- The stub records calls so tests can assert layer behavior.

### Map Fixtures

`tests/fixtures/mapFactory.js` creates a small deterministic map for engine tests.

It does not need to satisfy the full route-length contract.

It must:

- Be valid enough for sim tests.
- Include all required object types.
- Have a gate gap.
- Have a few blockers to test pathfinding.
- Be deterministic.

The real map in `assets/map.json` is used by map contract and full-route tests.

---

## 26. Required Test Suite

All tests below are required.

### Core Tests

| Test | Passes When | Why |
|---|---|---|
| Vector normalize | Diagonal vector normalizes to length 1. | Prevents diagonal speed advantage. |
| Distance and angle | Distance and angle helpers match expected values. | Used by perception, camera, arrow. |
| RNG deterministic | Same seed produces same sequence. | AI tests must be reproducible. |
| Event bus | Subscribers receive emitted payloads. | Systems are decoupled. |
| Input mapping | WASD/arrows produce correct action frame. | Controls work. |
| Input prevents scroll | Game key handlers call `preventDefault`. | Browser UX. |

### Map Tests

| Test | Passes When | Why |
|---|---|---|
| Map loads fixture | Tile array matches dimensions. | Map is readable. |
| Tile queries | Passable/blocking/underbrush queries are correct. | Collision and pathing depend on this. |
| Boundary | Outer border is impassable. | Player cannot leave map. |
| Gate gap | Required gate gap tiles are passable. | Gate can function. |
| Object coordinates | Required objects match gameplay coordinates. | Design intent is preserved. |

### Collision Tests

| Test | Passes When | Why |
|---|---|---|
| Player blocks on tree | Player cannot enter tree tile. | Basic movement. |
| Player enters underbrush | Player can enter underbrush. | Cover system. |
| Diagonal corner blocked | Player cannot clip corner. | Fair movement. |
| Gate closed blocks gap | Player cannot enter gate gap. | Gate state matters. |
| Gate open allows gap | Player can enter gate gap. | Win route works. |
| Hollow blocks on safe | Hollow cannot enter safe tile. | Light defense works. |
| Hollow remains in safe tile | If safe appears over Hollow, it does not teleport. | Prevents unfair trapping. |

### Line-of-Sight Tests

| Test | Passes When | Why |
|---|---|---|
| Tree blocks LOS | LOS false through tree. | Sight and sound blocked. |
| Rock blocks LOS | LOS false through rock. | Same. |
| Water blocks LOS | LOS false through water. | Same. |
| Underbrush does not block LOS | LOS true through underbrush. | Stealth cover is not visual wall. |

### Pathfinding Tests

| Test | Passes When | Why |
|---|---|---|
| A* finds open path | Path exists in open map. | Basic pathing. |
| A* avoids blockers | Path does not enter impassable tiles. | Core pathing. |
| A* respects safe predicate | Path avoids dynamic safe tiles. | Light defense pathing. |
| A* underbrush cost | Underbrush tile cost is 1.25. | Movement cost matches design. |
| No path fallback | Returns nearest reachable tile. | The Hollow cannot teleport. |
| Diagonal corner rule | Diagonal path does not cut corners. | Readable movement. |

### Player Tests

| Test | Passes When | Why |
|---|---|---|
| Walk speed | Movement is `3.6` tiles/s. | Design number. |
| Sprint speed | Movement is `6.0` tiles/s. | Design number. |
| Underbrush speed | Movement is multiplied by `0.85`. | Cover slows movement. |
| Breath drain | Sprint drains `20/s`. | Sprint limit. |
| Breath recovery walk | Walking recovers `15/s`. | Breath system. |
| Breath recovery stand | Standing recovers `30/s`. | Breath system. |
| Breath lock | Sprint disabled at 0 until 25. | Prevents infinite sprint. |
| Fuel drain | Lantern drains `0.5/s`. | Resource pressure. |
| Fuel cap | Ember cannot exceed 100. | Resource cap. |
| Light radius formula | Radius matches `4 + fuel * 0.04`. | Light system. |
| Safe zone threshold | Safe active at 25, inactive at 24.999. | Defense rule. |
| Cover detection | Covered in underbrush or adjacent blocker. | Sight range changes. |

### Perception Tests

| Test | Passes When | Why |
|---|---|---|
| Lantern on sight range | Range is `lightRadius + 2`. | Lit player is more visible. |
| Covered ambient range | Range is 3 when covered. | Cover helps. |
| Uncovered ambient range | Range is 6 when uncovered. | Open space is risky. |
| Hearing radius walk | Walking noise radius is 5. | Movement risk. |
| Hearing radius sprint | Sprint noise radius is 10. | Sprint risk. |
| Sprint underbrush noise | Sprint underbrush noise radius is 12. | Loud escape. |
| LOS required for hearing | Noise does not pass blockers. | Walls matter. |
| Event noise key | Key pickup creates radius 6 event. | Pickups attract. |
| Event noise ember | Ember pickup creates radius 4 event. | Pickups attract. |
| Event noise gate | Gate open creates radius 12 event. | Climactic risk. |

### Hollow Tests

| Test | Passes When | Why |
|---|---|---|
| Wake at 90s | State becomes Waking at 90s. | Safe phase length. |
| Waking duration | Waking lasts 8s. | Telegraph. |
| Curious speed | Speed is 2.4. | Behavior. |
| Investigating speed | Speed is 3.2. | Behavior. |
| Searching speed | Speed is 3.2. | Behavior. |
| Hunting speed | Speed is 5.0. | Behavior. |
| Underbrush speed | Speed multiplied by 0.85. | Cover affects enemy. |
| Curious to Investigating | Detection from Curious enters Investigating. | State machine. |
| Investigating to Hunting | Detection from Investigating enters Hunting. | State machine. |
| Hunting lost 6s | No detection for 6s enters Searching. | Chase limit. |
| Searching 12s | Searching exits to Curious after 12s. | Stealth limit. |
| Safe zone wait | Hollow waits outside safe radius. | Light defense. |
| Safe zone disappears | Hollow enters when fuel below 25. | Defense is temporary. |
| Threshold exclusion | Hollow cannot enter `y < 6` when gate open. | Escape safety. |
| Hollow relocate | If in threshold when gate opens, moves to `y >= 6`. | Edge case. |

### Gate and Pickup Tests

| Test | Passes When | Why |
|---|---|---|
| Gate locked prompt | With missing keys, prompt locked. | Objective clarity. |
| Gate hold opens | Holding E for 2s with 3 keys opens gate. | Final interaction. |
| Gate release decays | Releasing E decays charge. | Hold interaction feel. |
| Gate remains open | Gate open persists. | No closing. |
| Key pickup | Overlap collects key. | Objective progression. |
| Ember pickup | Overlap adds fuel. | Resource progression. |
| Pickup noise | Pickup emits correct noise event. | Stealth risk. |
| No double pickup | Collected pickup is removed. | State correctness. |

### GameSim Tests

| Test | Passes When | Why |
|---|---|---|
| Initial state | All initial values match gameplay. | Run starts correctly. |
| Dawn fail | Run fails when dawn reaches 0. | Fail condition. |
| Contact fail | Run fails when Hollow overlaps player. | Fail condition. |
| Win condition | Gate open and `y < 6` wins. | Win condition. |
| Win priority over contact | Same-frame win beats contact. | Fairness. |
| Win priority over dawn | Same-frame win beats dawn. | Fairness. |
| Retry resets | All run state resets. | Retry works. |
| Hollow disabled option | Test config can disable Hollow. | Needed for route tests. |

### Integration Tests

| Test | Passes When | Why |
|---|---|---|
| Audio mapping | Required sim events produce required audio calls. | Audio direction is implemented. |
| HUD warnings | Fuel and dawn warnings appear at thresholds. | HUD communicates danger. |
| HUD objective | Objective text changes with keys and gate. | Objective clarity. |
| HUD arrow | Arrow visible off-screen, hidden on-screen. | Navigation aid. |
| Full route on real map | Scripted player collects keys and wins with Hollow disabled. | Map is playable end-to-end. |
| Gate under threat | Player with full fuel and all keys can open gate and win while active Hollow is held by safe zone. | Core threat system works. |
| Retry | Fail then retry starts fresh run. | Run loop complete. |

### Renderer Tests

| Test | Passes When | Why |
|---|---|---|
| Render without throw | Renderer calls mock canvas without exception. | No obvious rendering crash. |
| Culling | Visible tile draw count is bounded by view size. | Performance. |
| Safe edge drawn | Safe edge stroke occurs when safe active. | Light defense is visible. |
| Safe edge hidden | No safe edge when fuel below 25. | Defense state visible. |
| HUD drawn | HUD calls occur while playing. | HUD exists. |
| End screens | Win/fail render states do not throw. | End states render. |

### Map Contract Test

`tests/map/validate-map.test.js` runs the same validation as `scripts/validate-map.mjs`.

It must fail if:

- Map dimensions are wrong.
- Required objects are missing.
- Required coordinates are wrong.
- Objects are on impassable tiles.
- Map is disconnected.
- Route length targets are not met.
- Underbrush clusters are missing.
- Gate cover pockets are missing.
- Corridor width heuristic fails.

Why:

- The map is the main level-design risk.
- A bad map can make the game unplayable even if all code is correct.

### Performance Budget Test

`tests/performance/budget.test.js` runs a 480-second simulation on the fixture map.

It must pass if:

- The simulation completes without exceptions.
- 28,800 updates complete under 10 seconds in the test environment.
- A* allocations do not grow unbounded across the run.

Why:

- The game must run in a browser.
- A full run should not be a performance stress test.

---

## 27. Scripted Playthrough Tests

### Full Route Test

This test proves the shipped map can be completed by an input-driven player.

Setup:

- Use `assets/map.json`.
- Override `hollowEnabled: false`.
- Start with defaults except Hollow is disabled.

Scripted player objective sequence:

```text
Ember E1
Key A
Ember E4
Key C
Ember E2
Key B
Ember E5
Gate approach
Gate
```

This sequence matches the gameplay route and ensures the player picks up the required fuel near each key.

Movement policy:

1. Every 0.5 seconds, compute A* from current player tile to current target tile.
2. Move toward the next waypoint.
3. If target is reached within `0.5` tiles, advance to next objective.
4. If path fails, move straight toward target. This should not happen on a valid map.
5. Turn lantern off for this test to isolate route and pickup logic.
6. Sprint when:
   - Distance to target is greater than 8 tiles, and
   - Breath is greater than 40.
7. Otherwise walk.
8. At gate:
   - Hold E until gate opens.
   - Move north into threshold.

Pass criteria:

- State becomes `Won`.
- Dawn timer has not reached 0.
- All 3 keys collected.
- At least 4 embers collected: `E1`, `E2`, `E4`, `E5`.
- No sim exceptions.

Why this is a “playable” test:

- It uses real sim update, movement, collision, pathfinding, pickups, gate, and win checks.
- It proves the shipped map is navigable and win-reachable.
- It does not prove human balance, which is covered by route-length validation and manual smoke.

### Gate Under Threat Test

This test proves the core escape tension works.

Setup:

- Use `assets/map.json`.
- Hollow active.
- Initial debug state:
  - Player at `(60, 6)`
  - Keys collected: 3
  - Fuel: 100
  - Lantern on
  - Hollow state: `Hunting`
  - Hollow position: `(60, 20)`

Script:

1. Do not move.
2. Keep lantern on.
3. After 5 seconds, hold E for 2 seconds.
4. After gate opens, move north for 1 second.
5. Expect win.

Pass criteria:

- The Hollow does not enter player’s safe zone while fuel is above 25.
- Gate opens after 2 seconds.
- Player wins at `y < 6`.
- No caught fail occurs.

Why:

- This validates light defense, gate noise, threshold exclusion, and win condition in one scenario.

---

## 28. Manual Browser Smoke Checklist

Automated tests are required, but the final browser check is also required.

Steps:

1. Start a static server in the project root.
2. Open `index.html` in a desktop browser.
3. Confirm title screen shows:
   - Move
   - Sprint
   - Lantern
   - Interact
   - `Begin the Night`
4. Click `Begin the Night`.
5. Confirm audio starts or at least audio context resumes.
6. Confirm HUD shows:
   - Timer `08:00`
   - Fuel bar
   - Breath bar
   - Objective text
   - Empty key slots
7. Press `WASD` or arrow keys. Player moves.
8. Hold `Shift` or `Space`. Player sprints and breath bar drains.
9. Release sprint. Breath bar recovers.
10. Press `L`. Lantern toggles. Fuel drains while lit.
11. Move near a key or ember. Pickup occurs.
12. Reach the gate without all keys. Prompt says sealed.
13. Use a test-only cheat or debug method if available to collect keys, or rely on automated tests for gate-open. In manual play, complete a full run or use a debug build.
14. With all keys, hold `E` near gate. Gate opens after 2 seconds.
15. Cross threshold. Win screen appears.
16. Press `R`. Run resets.
17. Check browser console for errors. There should be none except intentional asset warnings if using placeholders.

Why manual smoke:

- It catches DOM, CSS, audio unlock, input focus, and canvas scaling issues that headless sim tests cannot fully cover.

---

## 29. Definition of Done

The game is considered engineering-complete when:

1. `npm run ci` passes.
2. `npm run map:validate` passes.
3. All required test files exist.
4. The real map in `assets/map.json` passes the map contract.
5. The scripted full route test reaches `Won`.
6. The scripted gate-under-threat test reaches `Won`.
7. The renderer smoke test passes with a mock canvas.
8. The audio mapping test passes with a mock audio manager.
9. Manual browser smoke checklist passes.
10. No required gameplay system is stubbed.
11. No console errors appear during a full browser run.

---

## 30. Edge Cases and Expected Behavior

| Edge Case | Expected Behavior |
|---|---|
| Player runs out of fuel | Light radius becomes 0. Safe zone disappears. Ambient visibility remains. |
| Player runs out of breath | Sprinting disabled until breath reaches 25. Walking still possible. |
| Player stands in safe zone | The Hollow waits outside. Fuel continues to drain. |
| Fuel drops below 25 | Safe zone disappears. The Hollow recalculates path. |
| The Hollow cannot path to target | Moves to nearest reachable tile. Waits or locally wanders. |
| The Hollow is in threshold when gate opens | Moves to nearest reachable tile where `y >= 6`. |
| Player and Hollow overlap while player crosses threshold | Win takes priority. |
| Dawn reaches 0 and player crosses same frame | Win takes priority. |
| Dawn reaches 0 and Hollow touches player same frame | Contact fail is checked before dawn fail. |
| Player picks key near The Hollow | Noise event radius 6 can trigger detection. |
| Player picks ember near The Hollow | Noise event radius 4 can trigger detection. |
| Gate opened | Noise event radius 12 can trigger detection. |
| Player misses an ember | Run is still possible but harder. |
| Player wastes fuel | No separate fail. Reduced visibility and defense. |
| Player sprints too much | Breath lock forces tactical pause. |
| Player uses compass | Points to nearest key or gate. |
| Player ignores compass | Player may fail by dawn. |

---

## 31. Debug and Test Hooks

The sim may expose a minimal debug namespace for tests.

```js
sim.debug = {
  setHollowState(state, pos),
  setPlayerState(partial),
  forceGateOpen(),
  forceDawn(seconds),
  collectNoiseEvents()
}
```

Rules:

- Debug hooks are for tests only.
- The browser App must not use them.
- They must not break normal sim behavior.
- They must be disabled or ignored in production code paths if possible.

Why:

- Controlled threat tests need to start The Hollow in a known state.
- Dawn tests need to accelerate time.
- Gate tests need to isolate gate behavior.

---

## 32. Asset Missing Behavior

If a sprite or audio file is missing:

- Log a warning.
- Continue running.
- Sprite fallback: draw a colored rectangle with the asset name in debug builds.
- Audio fallback: no sound.

Why:

- The game must remain testable before all final assets are placed.
- Missing assets should not break gameplay logic.

---

## 33. Performance Budgets

Target mid-tier desktop browser.

| System | Budget |
|---|---:|
| Fixed update | Under 4 ms average |
| A* path | Under 5 ms typical |
| Full frame render | Under 8 ms typical |
| 480-second headless sim | Under 10 seconds in test environment |
| Visible tile draw calls | Around 24 x 16 tiles plus entities |
| Particles | Respect visual designer budgets |

Why:

- The map is moderate size.
- Pathfinding is the main CPU risk.
- Rendering should be simple enough for Canvas 2D.

---

## 34. What the Integration Agent Must Not Do

- Do not add a runtime procedural map generator.
- Do not add a second enemy.
- Do not add health or damage to the player.
- Do not add a minimap.
- Do not add a pause menu.
- Do not make The Hollow pass through blockers.
- Do not make The Hollow enter active safe tiles.
- Do not let The Hollow enter the threshold after the gate opens.
- Do not let dawn fail override a same-frame win.
- Do not store gameplay state in the renderer.
- Do not use `Date.now()` inside the sim.
- Do not make audio or DOM dependencies inside `GameSim`.
- Do not add optional accessibility modes unless explicitly requested later.

---

## 35. Final Engineering Summary

The implementation should be a small, deterministic, canvas-based browser game with a clean split between simulation and presentation.

The core sim must be headless and testable. The map must be a static JSON asset validated by strict contracts. The Hollow must be a readable finite-state hunter constrained by sight, sound, light, geometry, and the gate threshold. The player must manage movement, breath, lantern fuel, cover, and timing.

The test suite must prove:

- Movement and collision are correct.
- Pathfinding respects blocks and safe zones.
- Perception is deterministic and fair.
- The Hollow state machine behaves as designed.
- Pickups, fuel, breath, dawn, gate, and win/fail all work.
- The shipped map is navigable and meets gameplay route constraints.
- The game can be played from start to win using real sim inputs.
- Audio and HUD receive the required events.
- Rendering can run without crashing and respects the visual layering contract.