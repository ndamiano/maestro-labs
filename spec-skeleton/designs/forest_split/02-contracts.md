# 2. CONTRACTS

## 2.1 Module layout

| File | Responsibility |
| --- | --- |
| `index.html` | Loads canvas, DOM HUD, title overlay, end-screen overlays, and `src/main.js`. |
| `styles.css` | Layout, scaling, overlays, HUD bars, prompts, warnings, font fallbacks. No gameplay logic. |
| `package.json` | Defines test scripts and Vitest dependency. |
| `src/main.js` | Browser bootstrap. Creates app, sim, renderer, audio, input, DOM HUD. |
| `src/config/defaultConfig.js` | Single source of truth for gameplay constants. |
| `src/core/clock.js` | Deterministic clock abstraction for app and tests. |
| `src/core/rng.js` | Seeded 32-bit RNG. |
| `src/core/eventBus.js` | Minimal event pub/sub. |
| `src/core/input.js` | Keyboard state, action mapping, test injection. |
| `src/core/loop.js` | Fixed-timestep browser loop. |
| `src/core/math2d.js` | Vector, distance, angle, clamp, lerp, smoothstep. |
| `src/game/map.js` | Loads and validates map JSON. Provides tile queries. |
| `src/game/player.js` | Player movement, breath, fuel, lantern, cover, pickups, gate charge. |
| `src/game/hollow.js` | The Hollow state machine, perception response, movement, safe-zone behavior. |
| `src/game/gate.js` | Gate state, hold-to-open, threshold rules. |
| `src/game/lighting.js` | Light radius, safe zone predicate, visible range. |
| `src/game/perception.js` | Sight, hearing, line of sight, cover. |
| `src/game/objectives.js` | Objective target selection and compass arrow. |
| `src/game/pathfinding.js` | A*, supercover DDA line of sight, nearest reachable fallback. |
| `src/game/gameSim.js` | Top-level run state. Owns player, hollow, gate, pickups, timers, win/fail checks. |
| `src/audio/audioManager.js` | Web Audio API synthesis, one-shots, loops, layers. |
| `src/audio/musicDirector.js` | Maps semantic game events to music layer changes. |
| `src/render/assetFactory.js` | Draws procedural sprites and tile visuals from visual recipes. |
| `src/render/camera.js` | Camera position and viewport culling. |
| `src/render/lightingCanvas.js` | Offscreen darkness and lantern light rendering. |
| `src/render/renderer.js` | Orchestrates visible tile, entity, prop, lighting rendering. |
| `src/app/titleScreen.js` | DOM title screen. |
| `src/app/hudScreen.js` | DOM HUD binding to sim HUD fields. |
| `src/app/endScreen.js` | DOM win and fail screens. |
| `src/app/app.js` | Wires app, sim, renderer, audio, input, retry. |
| `assets/map.json` | The one handcrafted map. |
| `scripts/validate-map.mjs` | Standalone map contract validator. |
| `tests/setup/mockAudio.js` | Mock audio recorder for tests. |
| `tests/setup/factories.js` | Test sim, map, input, and advance helpers. |
| `tests/fixtures/mapFactory.js` | Small deterministic map fixture for engine tests. |
| `tests/core/math2d.test.js` | Math helper tests. |
| `tests/core/rng.test.js` | RNG determinism tests. |
| `tests/core/eventBus.test.js` | Event bus tests. |
| `tests/core/input.test.js` | Input mapping tests. |
| `tests/game/map.test.js` | Map load and query tests. |
| `tests/game/collision.test.js` | Collision tests. |
| `tests/game/los.test.js` | Line-of-sight tests. |
| `tests/game/pathfinding.test.js` | Pathfinding tests. |
| `tests/game/player.test.js` | Player movement, breath, fuel tests. |
| `tests/game/lighting.test.js` | Light and safe-zone tests. |
| `tests/game/perception.test.js` | Sight and hearing tests. |
| `tests/game/hollow.test.js` | Hollow state machine tests. |
| `tests/game/gate.test.js` | Gate and threshold tests. |
| `tests/game/pickups.test.js` | Pickup tests. |
| `tests/game/gameSim.test.js` | Sim state, win, fail, retry tests. |
| `tests/integration/audio.test.js` | Audio mapping tests. |
| `tests/integration/ux.test.js` | HUD and DOM screen tests. |
| `tests/integration/fullRoute.test.js` | Scripted full route on real map. |
| `tests/integration/gateUnderThreat.test.js` | Gate under active Hollow threat. |
| `tests/integration/retry.test.js` | Retry reset tests. |
| `tests/render/renderer.test.js` | Renderer smoke tests. |
| `tests/map/validate-map.test.js` | Map contract tests. |
| `tests/performance/budget.test.js` | Performance budget tests. |

No external sprite or audio files are required. `assets/map.json` is the only required asset file.

## 2.2 Global context

The sim context is the only gameplay record. Renderer, audio, and DOM HUD read from it but do not mutate gameplay state.

```js
const sim = {
  state: 'title',
  elapsed: 0,
  dawnRemaining: 480,
  runSeed: 0,
  config: DEFAULT_CONFIG,
  map: mapInstance,
  bus: eventBus,
  player: {
    pos: { x: 60, y: 72 },
    radius: 0.5,
    lanternOn: true,
    fuel: 50,
    breath: 100,
    breathLocked: false,
    keysCollected: 0,
    covered: false,
    inUnderbrush: false,
    moving: false,
    sprinting: false,
    currentNoiseRadius: 0,
    stepTimer: 0,
    lastStepTime: 0,
    gateCharge: 0
  },
  hollow: {
    pos: { x: 60, y: 40 },
    radius: 0.6,
    state: 'Sleeping',
    stateTimer: 0,
    lostTimer: 0,
    waypointTimer: 0,
    pathTimer: 0,
    path: [],
    pathIndex: 0,
    target: null,
    lastKnown: null,
    speed: 0
  },
  gate: {
    x: 60,
    y: 5,
    open: false,
    charge: 0
  },
  pickups: {
    keys: [
      { id: 'A', x: 95, y: 60, collected: false },
      { id: 'B', x: 22, y: 26, collected: false },
      { id: 'C', x: 64, y: 42, collected: false }
    ],
    embers: [
      { id: 'E1', x: 88, y: 57, collected: false },
      { id: 'E2', x: 25, y: 30, collected: false },
      { id: 'E3', x: 88, y: 22, collected: false },
      { id: 'E4', x: 58, y: 45, collected: false },
      { id: 'E5', x: 58, y: 10, collected: false }
    ]
  },
  objectives: {
    targetKeyId: null,
    targetPos: { x: 95, y: 60 },
    arrowVisible: false,
    arrowAngle: 0,
    arrowTimer: 0
  },
  onboarding: {
    moveShown: false,
    sprintShown: false,
    lanternShown: false,
    text: '',
    visible: false,
    timer: 0
  },
  noise: {
    queue: []
  },
  hud: {
    state: 'title',
    timeRemaining: 480,
    elapsedFormatted: '00:00',
    fuel: 50,
    breath: 100,
    breathLocked: false,
    keysCollected: 0,
    objectiveText: 'Find the bone keys',
    arrow: {
      visible: false,
      angle: 0
    },
    prompt: {
      type: 'none',
      text: '',
      progress: 0
    },
    warnings: {
      fuelLow: false,
      dawnLow: false
    },
    onboardingText: '',
    onboardingVisible: false
  }
};
```

All fields read or written by section 4 rules are present in this context.

## 2.3 Module specifics

### Map

Fields:

- `width`
- `height`
- `tiles`
- `objects`

Functions:

- `tileAt(tx, ty)`
- `isPassable(tx, ty)`
- `isBlocking(tx, ty)`
- `isUnderbrush(tx, ty)`
- `tileCost(tx, ty)`
- `objectAt(tx, ty)`
- `isInGateGap(tx, ty)`
- `isGateApproach(tx, ty)`

Tile storage:

```text
0 GRASS
1 PATH
2 UNDERBRUSH
3 TREE
4 ROCK
5 WATER
```

Tile cost:

| Tile | Cost |
| --- | ---: |
| Grass or Path | 1.0 |
| Underbrush | 1.25 |
| Impassable | Infinite |

### Player

Functions:

- `update(dt, input)`
- `canSprint()`
- `currentNoiseRadius()`
- `isCovered()`
- `checkPickups()`
- `updateGateCharge(dt, input)`
- `emitStepIfNeeded(dt)`

### Hollow

Functions:

- `update(dt)`
- `detect()`
- `chooseTarget()`
- `applySafeZoneRules()`
- `applyThresholdExclusion()`
- `recalcPath()`

### Gate

Functions:

- `update(dt, input)`
- `canInteract()`
- `isOpen()`
- `thresholdBlocksHollow(ty)`

### Lighting

Functions:

- `lightRadius()`
- `safeActive()`
- `isSafeTile(tx, ty)`
- `visibleRange()`
- `ambientRange()`

### Perception

Functions:

- `hasLineOfSight(from, to)`
- `sightRange()`
- `heard()`
- `detected()`

### Pathfinding

Functions:

- `findPath(from, to, blockedPredicate)`
- `nearestReachable(from, to, blockedPredicate)`
- `octileDistance(a, b)`

### Objectives

Functions:

- `updateArrow(dt)`
- `targetPos()`
- `nearestKey()`

### GameSim

Functions:

- `update(dt, input)`
- `retry(seed)`
- `startRun()`
- `checkWin()`
- `checkFailCaught()`
- `checkFailDawn()`
- `emit(event, payload)`
- `debug`

### Input

Fields:

- `moveX`
- `moveY`
- `sprint`
- `lanternJustPressed`
- `interactHeld`
- `retryJustPressed`

Functions:

- `frame()`
- `setMove(x, y)`
- `setSprint(value)`
- `pressLantern()`
- `setInteract(value)`
- `pressRetry()`

### Audio

Functions:

- `resume()`
- `play(name)`
- `startLayer(name)`
- `stopLayer(name)`
- `setPhase(phase)`

### Renderer

Functions:

- `render(sim)`
- `updateCamera(sim)`
- `visibleRange(camera)`

### App

Functions:

- `start()`
- `bindTitle()`
- `bindEndScreens()`
- `bindHud()`
- `retryRun()`
