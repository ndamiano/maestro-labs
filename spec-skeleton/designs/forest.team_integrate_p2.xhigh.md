# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Explore a haunted forest at night | Section 3, Section 4, Section 5 |
| Escape before dawn | Section 4.2, Section 4.11, Section 7 |
| Added: one handcrafted 2D top-down forest map | Section 1, Section 3, Section 4 |
| Added: lantern fuel as a core resource | Section 4.4 |
| Added: sprint breath as a core resource | Section 4.3 |
| Added: one readable hunter, The Hollow | Section 4.7, Section 5 |
| Added: three bone keys required to open the gate | Section 4.5, Section 4.6 |
| Added: Old Gate threshold win zone | Section 4.6, Section 4.11 |
| Added: readable visual and audio cues | Section 3, Section 5, Section 6, Section 7 |
| Added: retry resets the entire run | Section 4.1, Section 7, Section 8 |
| Added: deterministic, headless-testable simulation | Section 1, Section 2, Section 8, Section 9 |
| Added: HTML and CSS screens and HUD | Section 7 |
| Added: generated Web Audio API sound and music | Section 6 |
| Added: title screen and end screens | Section 7 |
| Added: map contract validation and scripted playthrough tests | Section 9, Section 10, Section 11 |

## 0.2 Decisions

| Topic | What gameplay said | What visual said | What engineering said | Ruling and one clause why |
| --- | --- | --- | --- | --- |
| HUD implementation | HUD elements and warnings are defined. | Quiet HUD layout, bone-white text, bars, dial, arrow, prompt. | Canvas HUD via `hudRenderer.js`. | All screens and HUD are HTML and CSS DOM elements; canvas draws only the world. The prompt requires HTML and CSS only, and DOM HUD keeps canvas rendering cheaper. |
| Audio source | Audio cues are required for events. | Music and SFX direction, procedural synthesis reference. | Audio manifest with audio files. | All audio is generated at runtime with the Web Audio API from recipes in code. No external audio files are required, and the prompt requires Web Audio API generation. |
| Art assets | Visual layering is cosmetic; gameplay uses tiles. | Asset generation recipes for tiles, sprites, particles. | Sprite manifest and asset loader. | All art is drawn procedurally on canvas from the visual recipes. No external sprite files are required, and only `assets/map.json` is external data. |
| Safe-zone fuel threshold | Safe zone exists when fuel is 25 or higher. | Fuel table suggests safe-zone flicker between 25 and 20. | Safe active at fuel 25 or higher. | Safe zone is active when fuel is 25 or higher and inactive below 25. The edge flickers when active and fuel is below 30, then fades below 25. Gameplay and engineering rules win. |
| Gate threshold boundary | Gate threshold is `y < 6` and described as 3 tiles deep. | Threshold is a 3-tile-deep safe zone. | Canonical boundary is `y < 6`; map gap is rows 3, 4, 5. | Win boundary is player center y coordinate below 6. The passable gate gap is x 59, 60, 61 and y 3, 4, 5. Rows y 0, 1, 2 remain impassable. This preserves both the rule and the visual depth. |
| Camera and viewport | Target readable view is approximately 24 tiles by 16 tiles. | Internal render size is 960 by 640 px; tile size 40 px. | Camera follows player with clamp; view 24 by 16. | Exact viewport is 24 tiles wide by 16 tiles tall, 40 px tiles, internal canvas 960 by 640 px, scaled while preserving aspect ratio. Engineering precision wins. |
| Map generation | One handcrafted map, no procedural generation. | Zone treatments for one forest. | Static JSON map plus validator. | The shipped map is one static `assets/map.json` file. No runtime procedural generation is allowed. All three agree, and validation is required. |
| Corridor width rule | No corridor should be narrower than 2 tiles. | Not specified. | Hard validator rule: passable 4-neighbor count at least 3 for remaining tiles. | Adopt the engineering corridor heuristic. It is a deterministic guard against 1-tile corridors and enforces the gameplay rule. |
| Underbrush cluster definition | At least 8 underbrush clusters, 3 to 4 tiles wide. | Underbrush is passable cover. | Cluster is a 4-connected component with at least 9 underbrush tiles. | A cluster is a 4-connected component of underbrush tiles with at least 9 tiles. This makes the gameplay intent machine-checkable. |
| Gate approach target | Gate approach zone is around coordinate 60, 10. | Gate approach visual zone includes Old Gate at 60, 5. | Compass target tile is 60, 6 when gate is closed and 60, 4 when open. | The gameplay compass target is 60, 6 before the gate opens and 60, 4 after the gate opens. The visual zone remains around 60, 10. Engineering tile target wins for arrow logic. |
| Pause | Not specified as a core state. | No pause screen required. | No pause. | No pause in T1. The game is a continuous 8-minute run. |
| Accessibility modes | Warnings should be clear. | Optional reduce-motion and high-contrast modes. | Optional accessibility modes cut. | T1 implements mandatory accessibility rules: warnings use shape and pulse, Hollow has a cold rim, UI contrast is strong. Optional reduce-motion and high-contrast toggles are T2. |
| Onboarding cues | Start clearing teaches movement, sprint, lantern, arrow. | First-run cues for Move, Sprint, Lantern, arrow pulse. | Per-run onboarding text for 2 seconds. | T1 includes minimal diegetic onboarding text: Move, Sprint, Lantern, each shown once per run for 2 seconds. |
| Path smoothing | The Hollow follows waypoints. | Visual animation may smooth motion. | No path smoothing; tile-center waypoints. | Simulation uses tile-center waypoints. The renderer may apply small visual smoothing without changing sim positions or pathing. |
| Screen shake | Not specified. | Optional minimal shake for caught and gate opening. | No shake requirement. | T1 has no screen shake. Tiny shake is T2: caught 2 to 3 px for 0.2 seconds, gate opening 1 to 2 px for 0.5 seconds. |
| Music scope | Required cues include state changes and time warnings. | Adaptive music layers across the run. | Music director maps events to layers. | T1 includes generated night bed, mystery, pressure, escape, resolve, drone, and required SFX. Richer procedural music textures are T2. |
| Retry seed | Retry resets the run. | Retry prompt on end screens. | RNG can use new or supplied seed. | In browser play, retry uses a new seed from the app. In tests, retry uses the supplied seed. Determinism wins for tests. |
| Title and end screens | Win and fail conditions exist. | Title, win, caught, and dawn fail screens are specified. | DOM title and end screens implied by app layer. | T1 includes Title, Playing, Won, and Failed screens as HTML and CSS overlays. |
| Win-screen time | Win condition exists. | Optional time display `mm:ss`. | Not specified. | Win screen shows `Time: mm:ss`, where mm:ss is the elapsed run time. |
| Red color | No HUD warning color specified. | Red is not used; danger uses cold blue and dawn gold. | No color-only warnings. | No red is used anywhere. Danger and time pressure use cold blue, dawn gold, shape, pulse, and icons. |
| Cover adjacency | Covered means center in underbrush or adjacent to impassable tile. | Cover visual state changes. | Covered means underbrush or 4-orthogonal adjacent blocking tile. | Cover uses 4-orthogonal adjacency only, not diagonal. This is readable and testable. |
| Detection during Waking | Waking is non-hostile. | Waking is an 8-second telegraph. | Waking has no detection or damage. | The Hollow cannot detect, move, or harm the player during Sleeping or Waking. |
| Objective arrow frequency | Arrow updates twice per second. | Arrow appears at screen edge. | Arrow updates at 2 Hz using A* or straight fallback. | Arrow updates every 0.5 seconds. A* pathing is used when available; straight-line direction is the fallback. |
| Gate interaction radius | Gate requires held interact. | Prompt and circular progress. | Interact radius is 1.5 tiles. | The gate interaction radius is 1.5 tiles from the player center to gate center. |
| Pickup radius | Auto-pickup when overlapping. | Pickup feedback. | Pickup radius is 0.75 tiles. | Pickups occur when player center distance to pickup center is 0.75 tiles or less. |
| Initial lantern state | Starting fuel 50, lantern can be toggled. | Lantern is the primary light source. | Initial state has lantern on. | The player starts with lantern on. This matches the visual contract and makes the light system immediately readable. |

## 0.3 Tiers

T1 is the game that must ship:

- Map and Layout
- Run States and Retry
- Time and Dawn
- Player Movement and Breath
- Lantern and Light
- Pickups and Objectives
- Gate and Threshold
- The Hollow State Machine
- Perception
- Light Safe Zones
- Compass and Objective Aid
- Win and Fail Resolution
- Visual World Rendering
- Character and State Presentation
- Audio Cues and Generated Music
- HTML and CSS UX
- Debug and Test API
- Map Contract and Tests

T2 stages the remaining optional work, in this order:

1. Reduce-motion toggle: disables screen shake, replaces pulse warnings with steady changes, reduces particle bursts, slows mist and flame flicker.
2. High-contrast toggle: adds a faint cold outline around The Hollow’s fatal core.
3. Decorative ambient loops: night insects, occasional wood creaks, water ripple variation, leaf rustle variation.
4. Tiny screen shake: caught 2 to 3 px for 0.2 seconds, gate opening 1 to 2 px for 0.5 seconds.
5. Richer procedural music textures: celesta-like plucks, detuned pad layers, warmer escape pads, birds on win.
6. Extra particle polish: slightly richer mist drift, key pulse, ember spark, and gate light leak within visual budgets.

# 1. CONVENTIONS

## 1.1 Units, axes, frames

| Concept | Convention |
| --- | --- |
| Map size | 120 tiles wide by 80 tiles tall |
| Tile size | 40 px by 40 px |
| Internal canvas | 960 px by 640 px |
| Viewport | 24 tiles wide by 16 tiles tall |
| X axis | x increases east |
| Y axis | y increases south |
| North | y = 0 is the northern border |
| Tile coordinates | integer tile indices |
| Entity coordinates | floating-point tile units |
| Entity center | A position of x = 60, y = 72 is the center of tile 60, 72 |
| Pixel conversion | pixelX = tileX + 0.5, times tileSize; pixelY = tileY + 0.5, times tileSize |
| Time unit | seconds |
| Simulation step | fixed 1/60 second |
| Maximum frame delay | 0.25 seconds |
| Distance unit | tiles |
| Speed unit | tiles per second |
| Noise radius unit | tiles |
| Light radius unit | tiles |

## 1.2 Important conventions

The browser uses a fixed-timestep loop.

1. Accumulate real frame delta.
2. Clamp accumulated delta to 0.25 seconds.
3. While accumulated delta is at least 1/60 second:
   - call sim update with dt = 1/60
   - subtract 1/60 from accumulated delta
4. Render once after all fixed updates.

This makes collision, pathing, perception, and timers deterministic. Tests may call sim update repeatedly with dt = 1/60.

System update order for every sim update while state is Playing:

1. Return immediately if state is not Playing.
2. Advance run elapsed time and dawn remaining time. Do not fail on dawn yet.
3. Update player movement, breath, fuel, lantern, cover, continuous noise, pickups, and gate charge.
4. Process gate interaction and gate opening.
5. Process queued noise events.
6. Update The Hollow: perception, state machine, pathing, movement, safe-zone rules, threshold exclusion.
7. Check win condition.
8. Check fail by The Hollow contact.
9. Check fail by dawn.
10. Update HUD fields, objective arrow timer, onboarding timer, and warning flags.

This order satisfies the rule that win beats same-frame fail, and contact fail is checked before dawn fail.

One random source:

- The sim uses one seeded 32-bit RNG per run.
- The sim must not use unseeded browser randomness.
- The Hollow waypoint choices use the sim RNG.
- The app may choose a new seed for retry in browser play.
- Tests use fixed seeds.

Controls:

| Input | Action |
| --- | --- |
| W or ArrowUp | Move up |
| S or ArrowDown | Move down |
| A or ArrowLeft | Move left |
| D or ArrowRight | Move right |
| Shift or Space, held | Sprint |
| L, pressed | Toggle lantern |
| E, held | Interact with gate |
| R, pressed | Retry from Won or Failed |

Default config:

```js
const DEFAULT_CONFIG = {
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
    fuelLowWarning: 20,
    safeFuelThreshold: 25,
    safeFlickerFuel: 30,
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
    curiousWaypointInterval: 2,
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
  },
  compass: {
    updateInterval: 0.5
  },
  audio: {
    walkStepInterval: 0.35,
    sprintStepInterval: 0.20
  },
  onboarding: {
    duration: 2
  }
};
```

Tests may override config values. The real browser game uses defaults.

Event names used by the sim:

- `run.start`
- `run.win`
- `run.fail.caught`
- `run.fail.dawn`
- `hollow.wake`
- `hollow.state_change`
- `pickup.key`
- `pickup.ember`
- `gate.open`
- `dawn.warning`
- `player.fuel.low`
- `player.breath.locked`
- `player.step`
- `onboarding.show`

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

# 3. VISUAL SPEC

The game has a Moonlit Folk Horror look: a quiet, wet, old forest at night, with low-detail painterly tiles, silhouette-based characters, soft edges, muted blue-green ground, cold moonlight, and warm lantern amber. The forest should feel old and lived-in but not cluttered. Every visual element must answer one of four questions: where can I safely see, where am I covered, what is The Hollow doing, and where do I need to go. Warm amber belongs to the player, lantern, fuel, and safe light. Bone white belongs to keys, UI, and objective accents. Cold blue belongs to The Hollow, threat states, breath, and detection cues. Deep green and blue belong to the forest. Dawn gold belongs only to time pressure and escape. Red is not used.

Lighting and atmosphere are the core visual system. The player’s lantern is the brightest warm source in the game. When the lantern is on and fuel is above 0, the bright inner area extends to the gameplay light radius, and a dim outer area extends to light radius plus 2 tiles. Outside that range, the forest becomes very low-contrast night shadow. When the lantern is off or fuel is 0, the player sees a cold ambient halo: 3 tiles if covered, 6 tiles if uncovered. The light safe zone is shown as a soft warm edge at the light radius when active. The edge is not a hard white circle. It uses a faint amber ring or shimmer, 1 to 2 px soft. When safe is active and fuel is below 30, the edge flickers. When fuel is below 25, the edge fades and the safe zone is gone. When The Hollow is outside the safe zone, it pauses or paces at the edge.

Dawn color progression over 480 seconds:

| Time remaining | Visual state |
| ---: | --- |
| 480s | Deep night blue, cold and quiet |
| 360s | Slightly lighter moon shadow, still dark |
| 240s | Forest shadows lift very slightly, cold blue remains |
| 120s | Faint pale grey-blue at the edges, tension increases |
| 60s | Very faint dawn gold at top of screen, timer warns |
| 0 | Dawn gold wash fills the screen |

Lantern fuel visual states:

| Fuel state | Lantern flame | Light behavior | HUD state |
| --- | --- | --- | --- |
| 100 to 50 | Steady warm amber | Stable light | Normal |
| 50 to 30 | Slightly smaller, mild flicker | Stable safe zone | Normal |
| 30 to 25 | Flickering | Safe zone flickers while active | Fuel warning begins at 20 |
| Below 25 | Small sputtering flame | Safe zone gone, light weak | Clear fuel warning below 20 |
| 0 | No flame | Lantern off | Dark ambient only |

World layers:

| Z-order | Layer | Purpose |
| ---: | --- | --- |
| 0 | Base ground | Grass, path, water, cracked ground, stone floor |
| 1 | Ground decals | Roots, bones, pebbles, faint moss, stains |
| 2 | Underbrush | Passable cover |
| 3 | Objective ground glow | Key pulse, ember glow, gate threshold light |
| 4 | Entities | Player, The Hollow, pickups |
| 5 | Vertical props | Tree trunks, rocks, well rim, gate structure |
| 6 | Weather and mist | Low mist, drifting leaves, faint dust |
| 7 | Lighting mask | Lantern light, ambient darkness, dawn color grade |
| 8 | Screen effects | Vignette, cold pulse, warm dawn wash |
| 9 | HUD | DOM HUD overlay, not canvas-drawn |

Visual rules:

- Underbrush may tint and partially occlude the lower half of a sprite, but it must not hide The Hollow or the player unfairly.
- Tree trunks and rocks may partially occlude adjacent sprites, but they must not hide an active threat in a way that conflicts with gameplay line of sight.
- The Hollow is drawn above underbrush so its silhouette remains clear.
- Lantern light affects entities and ground, but DOM HUD is unaffected by lighting.
- No visual cover blocks line of sight unless it is an impassable tree trunk, rock, or water.
- No camera tilt, isometric projection, perspective scaling, or parallax.
- Cosmetic vertical offsets are allowed for sprites, but all gameplay uses the 2D tile grid.

Space and zone treatments:

| Zone | Visual treatment | Distinctive props | Accent | Readability goal |
| --- | --- | --- | --- | --- |
| Start Clearing | Slightly open, softer moss, fewer blockers | Young trees, small bone marker, faint path | Moss Green | Teach movement without pressure |
| Southeast Root Shrine | Exposed pale roots, small stones, shallow key alcove | Root ring, stone fragments | Pale bone and faint warm moss | First key area, readable objective |
| Central Clearing | Open, cracked pale ground, dead well at center | Dead Well, sparse underbrush pockets | Cold blue mist | High-risk space, light defense |
| Western Thorn Grove | Dense low thorn, narrower gaps, darker floor | Thorn branches, heavy underbrush | Deeper Moss Green | Stealth and cover |
| Northeast Fuel Hollow | Small dry hollow, sparse wood, ember pebbles | Dry branches, orange pebbles | Ember Orange | Optional fuel, easy to spot |
| North Gate Approach | Worn path, stone gate, moonlit clearing | Old Gate, cover pockets, dawn light | Stone Grey and Dawn Gold | Final escape tension |

Palette:

| Role | Hex | Use |
| --- | ---: | --- |
| Deep Night Black | `#05070C` | Darkness, The Hollow core, deepest shadows |
| Night Blue | `#0A1220` | Base darkness, background, unlit areas |
| Moon Shadow Blue | `#16243A` | Vignette, soft shadows, night ground |
| Forest Ground Blue-Green | `#182A2F` | Default grass/forest floor |
| Moss Green | `#223833` | Start clearing, mossy patches, soft forest floor |
| Path Grey-Blue | `#2A3540` | Worn path, open ground |
| Stone Grey | `#4B5A64` | Rocks, gate, well rim |
| Bark Dark | `#2B3132` | Tree trunks, roots |
| Bone White | `#E8E3D4` | Keys, UI text, objective accents |
| Pale Bone | `#CFC8B8` | Dim UI, empty key slots |
| Lantern Amber | `#FFB14A` | Player lantern, fuel, safe light |
| Ember Orange | `#FF7A2A` | Ember stones, fuel pickup feedback |
| Cold Moon | `#BFE8FF` | The Hollow eyes, cold rim, detection cue |
| Hollow Blue | `#355A80` | The Hollow aura, threat pulse |
| Dawn Gold | `#D8B26A` | Dawn progression, timer warning, escape light |

Recipe table:

| Item | Recipe |
| --- | --- |
| Ground tile | Fill 40 by 40 canvas with base ground color. Add low-frequency noise. Add 5 to 12 small speckles using moss or stone colors. Darken edges slightly. Add one faint darker patch. Save 3 to 5 variants per tile type. |
| Underbrush tile | Use a darker base. Add 4 to 8 low tuft shapes. Keep top edge soft. Tile is not fully opaque. Add one or two lighter highlights so it reads as passable cover. |
| Tree trunk | Draw central circular or irregular trunk shape. Add root lines. Darken base. Add faint cold edge highlight on one side. Avoid large canopies. |
| Rock | Draw angular stone shape. Add dark shadow underneath. Add faint cold wet highlight. Keep silhouette readable at small size. |
| Water | Deep Night Black with Moon Shadow Blue highlights. Slow ripple animation, 2 to 3 seconds per cycle. No bright reflection. Reads as impassable and sight-blocking. |
| Bone key | 28 by 28 px. Vertical shaft 8 by 16 px. Ring 10 px circle at top. Two small teeth at bottom. Bone White. Add 1 to 2 subtle bone texture speckles. Add soft white glow, 4 to 6 px blur. Float 1 to 2 px up and down on a 1.5 to 2 second loop. |
| Ember stone | 24 by 24 px. Rounded irregular polygon. Dark outer shell. Inner warm Ember Orange glow. Add 3 bright speckles. Slow pulse weaker than key. Optional very subtle heat shimmer. |
| Dead Well | Approximately 2 by 2 tiles. Dark water center. Stone rim. Faint pale mist. A few broken bones or roots around edge. Water darker than normal water. |
| Old Gate | Approximately 3 by 3 tiles. Large stone frame. Dark wooden or stone gate panels. Three bone key sockets visible when close. Closed gate feels sealed. Ready sockets glow faint bone white. Opening gate creaks and shifts with light leaking through gap. Open gap is clear and safe. |
| Gate threshold | 3-tile-deep pale dawn light fills threshold once gate is open. Soft gold and white mist drifts through. Edge is readable but not hard. The Hollow does not visually enter the threshold once open. |
| Player sprite | Approximately 40 by 48 px. Hooded figure. Dark blue-grey cloak. Simple silhouette. Small lantern in one hand. No detailed face. No weapon. No armor. |
| The Hollow sprite | Approximately 64 by 76 px. Tall, thin, ragged, dark, cold. Core is dense black vertical shape. Outer tendrils are semi-transparent black. Rim is faint Hollow Blue. Eyes are two small Cold Moon points. |
| Mist particles | Maximum 10 to 15 visible. Slow drift. Soft edges. |
| Ember sparks | Maximum 8 to 12 per pickup. Small amber burst. |
| Key pulse | Simple glow, no heavy particles. |
| Hollow cold pulse | Simple rim or vignette, no complex particles. |
| Dawn light | Gradient wash, not thousands of particles. |

Motion rules:

- Motion is subtle.
- No excessive screen shake in T1.
- No full-screen flashes.
- No particle overload.
- Mist drift, lantern flame flicker, key pulse, ember spark, Hollow rim pulse, dawn edge glow, small ground ripple, and brief cold vignette pulse are allowed.
- Warnings must use pulse, shape, or icon changes, not only color.

# 4. GAMEPLAY SPEC

The player is a lone wanderer trapped in a haunted forest at night. The player starts in the Start Clearing with 480 seconds until dawn, 50 lantern fuel, and 100 breath. The player must explore the forest, collect three bone keys, manage lantern fuel and breath, avoid one readable hunter named The Hollow, reach the Old Gate, hold E for 2 seconds to open the gate, and cross the gate threshold before dawn. The Hollow wakes 90 seconds after the run begins, telegraphs for 8 seconds, then hunts through sight, hearing, light, cover, and pathfinding. The player wins when the gate is open and the player center y coordinate is below 6. The player fails when The Hollow touches the player or when dawn remaining time reaches 0. Win takes priority over same-frame fail.

## Records and rosters

### Map record

| Field | Value |
| --- | --- |
| Width | 120 tiles |
| Height | 80 tiles |
| Orientation | North is up |
| Border | Impassable except gate gap |
| Procedural generation | None |
| Levels | One |

Tile types:

| Tile character | Tile | Passable | Movement effect | Cover | Blocks sight and sound |
| ---: | --- | ---: | --- | ---: | ---: |
| `g` | Grass | Yes | Normal speed | No | No |
| `p` | Path | Yes | Normal speed | No | No |
| `u` | Underbrush | Yes | 85 percent speed | Yes when lantern off or fuel 0 | No |
| `t` | Tree | No | Impassable | N/A | Yes |
| `r` | Rock | No | Impassable | N/A | Yes |
| `w` | Water | No | Impassable | N/A | Yes |

Coordinate rosters:

| Location | Coordinate | Purpose |
| --- | ---: | --- |
| Start Clearing | 60, 72 | Player start and tutorial area |
| Old Gate | 60, 5 | Final exit |
| Gate threshold | y below 6 | Safe win zone once gate is open |
| Gate gap | x 59, 60, 61 and y 3, 4, 5 | Passable once gate opens |
| Central Clearing | 60, 40 | High-risk central hub |
| Dead Well | 60, 40 | The Hollow wake point |
| Bone Key A | 95, 60 | Southeast shrine key |
| Bone Key B | 22, 26 | Western grove key |
| Bone Key C | 64, 42 | Central clearing key |
| Ember 1 | 88, 57 | Near Key A |
| Ember 2 | 25, 30 | Near Key B |
| Ember 3 | 88, 22 | Northeast optional fuel |
| Ember 4 | 58, 45 | Near central clearing |
| Ember 5 | 58, 10 | Near gate approach |
| Gate approach target | 60, 6 | Compass target before gate opens |

Zone rosters:

| Zone | Location | Size | Content | Purpose |
| --- | ---: | ---: | --- | --- |
| Start Clearing | 60, 72 | Approximately 10 by 8 tiles | No required pickups, open space, bone marker or faint path | Safe introduction |
| Southeast Root Shrine | 95, 60 | Small clearing | Bone Key A, Ember 1, stone features, underbrush | First key |
| Central Clearing | 60, 40 | Approximately 18 by 18 tiles | Bone Key C, Ember 4, Dead Well, open exposure | Highest-risk objective area |
| Western Thorn Grove | 22, 26 | Approximately 14 by 12 tiles | Bone Key B, Ember 2, more underbrush, narrow tree cover | Stealth and cover |
| Northeast Fuel Hollow | 88, 22 | Approximately 8 by 6 tiles | Ember 3, short branch off main route | Optional fuel |
| North Gate Approach | Around 60, 10 | Approximately 10 by 8 tiles | Ember 5, Old Gate, at least two underbrush cover pockets | Final escape area |

Layout rules:

1. All keys, embers, and the gate are reachable without first collecting other required items.
2. No corridor should be narrower than 2 tiles.
3. The central clearing must be open enough to make light defense useful, but large enough that The Hollow can approach from multiple sides.
4. The gate approach must have at least two cover pockets.
5. The map must have no required backtracking after the third key if the player follows the compass.
6. The map boundary is impassable except through the gate gap.
7. There are at least 8 underbrush clusters.
8. At least 2 underbrush clusters are within Chebyshev distance 6 of gate approach 60, 6.
9. An underbrush cluster is a 4-connected component of underbrush tiles with at least 9 underbrush tiles.
10. Corridor width validator: for every passable tile, count passable 4-neighbor tiles. Ignore the check for required object tiles, tiles within Chebyshev distance 1 of required objects, gate gap tiles, and tiles in passable connected components with area at least 100. Remaining tiles must have at least 3 passable 4-neighbors.

Route length targets:

| Route | Target path length |
| --- | ---: |
| Start to Key A | 120 to 160 tiles |
| Key A to Key C | 120 to 160 tiles |
| Key C to Key B | 160 to 200 tiles |
| Key B to Gate approach | 160 to 200 tiles |
| Total expected route | 550 to 750 tiles |

Route length is measured as Euclidean polyline length in tiles between tile centers using A* paths on static passability.

Content inventory:

| Content | Count | Purpose |
| --- | ---: | --- |
| 2D tile map | 1 | Main forest |
| Player | 1 | Protagonist |
| Bone keys | 3 | Unlock gate |
| Ember stones | 5 | Refill lantern fuel |
| Old Gate | 1 | Final exit |
| Dead Well | 1 | The Hollow wake point |
| The Hollow | 1 | Primary threat |
| Start Clearing | 1 | Safe tutorial area |
| Central Clearing | 1 | High-risk key area |
| Southeast Root Shrine | 1 | First key area |
| Western Thorn Grove | 1 | Stealth key area |
| Northeast Fuel Hollow | 1 | Optional fuel area |
| North Gate Approach | 1 | Final escape area |
| Underbrush clusters | 8 minimum | Cover and stealth |

### Player record

| Field | Initial value |
| --- | ---: |
| pos | 60, 72 |
| radius | 0.5 |
| lanternOn | true |
| fuel | 50 |
| breath | 100 |
| breathLocked | false |
| keysCollected | 0 |
| covered | false |
| inUnderbrush | false |
| moving | false |
| sprinting | false |
| currentNoiseRadius | 0 |
| stepTimer | 0 |
| lastStepTime | 0 |
| gateCharge | 0 |

### Hollow record

| Field | Initial value |
| --- | ---: |
| pos | 60, 40 |
| radius | 0.6 |
| state | Sleeping |
| stateTimer | 0 |
| lostTimer | 0 |
| waypointTimer | 0 |
| pathTimer | 0 |
| path | empty |
| pathIndex | 0 |
| target | null |
| lastKnown | null |
| speed | 0 |

### Gate record

| Field | Initial value |
| --- | ---: |
| x | 60 |
| y | 5 |
| open | false |
| charge | 0 |

## 4.1 Run and Game States [T1]

Game states:

| State | Description |
| --- | --- |
| `title` | Title screen is visible. Simulation is not running. |
| `playing` | Normal gameplay. Timers, movement, pickups, and The Hollow are active. |
| `won` | The gate is open and the player crossed the safe threshold before dawn. |
| `failed` | Dawn arrived, or The Hollow touched the player. |

Initial state when gameplay starts:

- Player is in Start Clearing at 60, 72.
- Dawn timer: 480 seconds.
- Lantern fuel: 50 / 100.
- Breath: 100 / 100.
- Keys collected: 0 / 3.
- The Hollow: Sleeping.
- Gate: Closed.
- Lantern: On.

Retry:

- Pressing R from Won or Failed starts a completely new run.
- All pickups reset.
- The Hollow returns to Sleeping at 60, 40.
- Dawn timer resets to 480 seconds.
- Gate resets to closed.
- Player position, fuel, breath, keys, and charge reset.
- RNG uses the supplied test seed or a new app seed in browser play.

Why no checkpoints:

- The game is a short, self-contained run.
- Full retries preserve time pressure and keep scope small.

## 4.2 Time and Dawn [T1]

- Total time: 480 seconds.
- The timer counts down in real time.
- The player can win at any time before dawn.
- If the timer reaches 0 before the player wins, the run fails.
- Dawn warning begins when time remaining is below 60 seconds.
- Dawn warning uses shape, pulse, color, and audio.

Why 8 minutes:

- Long enough for one full exploration run.
- Short enough to avoid repetition.
- Creates constant pressure without meta-progression.

## 4.3 Player Movement and Breath [T1]

Movement:

- Player can move in 8 directions.
- Diagonal movement is normalized so it is not faster than straight-line movement.
- Player cannot pass through tree trunks, rocks, water, or closed gate gap.
- Underbrush slows movement by multiplying speed by 0.85.

Movement speed:

| Mode | Speed |
| --- | ---: |
| Walk | 3.6 tiles per second |
| Sprint | 6.0 tiles per second |
| Underbrush modifier | 85 percent speed |

Examples:

- Walk in underbrush: 3.6 times 0.85 equals 3.06 tiles per second.
- Sprint in underbrush: 6.0 times 0.85 equals 5.1 tiles per second.

Breath:

| Value | Amount |
| --- | ---: |
| Max breath | 100 |
| Starting breath | 100 |
| Sprint drain | 20 per second |
| Walking recovery | 15 per second |
| Standing recovery | 30 per second |

Rules:

- Sprint is allowed while input sprint is held, breath is above 0, and breath is not locked.
- If breath reaches 0, sprinting is disabled until breath reaches 25.
- Sprinting drains breath.
- Walking recovers breath.
- Standing still recovers breath faster than walking.
- Breath is clamped between 0 and 100.

No player health:

- The player has no health bar.
- If The Hollow touches the player, the run fails.
- There is no damage, healing, or invulnerability.

Why breath exists:

- Prevents the player from outrunning The Hollow indefinitely.
- Makes sprinting a tactical choice.
- Adds tension to chase moments without adding a full health system.

## 4.4 Lantern and Light [T1]

Lantern state:

- The player can toggle the lantern on or off with L.
- The player starts with the lantern on.

Fuel:

| Value | Amount |
| --- | ---: |
| Max fuel | 100 |
| Starting fuel | 50 |
| Ember pickup | +40 fuel |
| Fuel cap | 100 |
| Fuel drain | 0.5 per second while lit |

There are 5 ember stones.

Total available fuel if all embers are collected:

```text
50 starting fuel + 5 times 40 ember fuel = 250 fuel
```

At 0.5 fuel per second, this supports:

```text
250 divided by 0.5 = 500 seconds of continuous light
```

The run is 480 seconds. A player who uses all fuel and never turns the lantern off has a small spare margin. If one ember is missed, the player must use darkness for a meaningful portion of the run.

Light radius:

If the lantern is on and fuel is above 0:

```text
light_radius = 4 + fuel times 0.04
```

Examples:

| Fuel | Light radius |
| ---: | ---: |
| 1 | 4.04 |
| 25 | 5.00 |
| 50 | 6.00 |
| 100 | 8.00 |

If the lantern is off or fuel is 0:

```text
light_radius = 0
```

Player visibility:

| Lantern state | Condition | Player visible range |
| --- | --- | ---: |
| On | Fuel above 0 | light radius + 2 |
| Off or fuel 0 | Player covered | 3 tiles |
| Off or fuel 0 | Player uncovered | 6 tiles |

A player is covered if:

- The player center tile is underbrush, or
- Any of the 4 orthogonal adjacent tiles is blocking.

Light safe zone:

The Hollow cannot enter the player’s light safe zone when:

- Lantern is on.
- Fuel is 25 or higher.
- The tile is within the player’s light radius.

If fuel drops below 25, the safe zone disappears.

The light radius still exists below 25 fuel, but it no longer repels The Hollow.

Fuel warning:

- HUD shows a clear warning state when fuel is below 20.
- Warning uses pulse, shape, color, and audio.

Why light is central:

- Navigation: the player needs light to see the forest.
- Defense: The Hollow cannot enter the safe light radius while fuel is high enough.
- Risk: using light drains fuel and makes the player more visible.

## 4.5 Pickups and Objectives [T1]

Bone keys:

- There are 3 bone keys.
- Keys can be collected in any order.
- Keys are required to open the gate.
- Keys are auto-picked-up when the player center is 0.75 tiles or closer to the key center.
- Picking up a key produces a noise event with radius 6 tiles.

Ember stones:

- There are 5 ember stones.
- Ember stones are auto-picked-up when the player center is 0.75 tiles or closer to the ember center.
- Each adds 40 fuel.
- Fuel is capped at 100.
- Picking up an ember produces a noise event with radius 4 tiles.

Pickup feedback:

- Key pickup: small white pulse, HUD key slot fills, bone chime, very small ground ripple.
- Ember pickup: amber spark burst, fuel bar rises, lantern flame brightens briefly, warm ember sound.

Why auto-pickups:

- Keeps movement fluid.
- Avoids fumbling during tense moments.
- Still creates noise through the pickup event.
- Only the final gate requires a held interaction because it is the climactic risk.

## 4.6 Gate and Threshold [T1]

Gate:

- The gate is at 60, 5.
- The gate is closed at the start.
- The player can interact with the gate only when the player center is 1.5 tiles or closer to the gate center.
- If keys are missing, the gate shows a locked prompt.
- With all 3 keys, the player must hold E for 2 seconds to open the gate.
- Opening the gate produces a noise event with radius 12 tiles.
- Once open, the gate remains open.
- If E is released before 2 seconds, gate charge decays at 4 per second.
- The player must cross the threshold to win.

Gate gap:

- The passable gate gap is x 59, 60, 61 and y 3, 4, 5.
- While closed, gap tiles block the player.
- While open, gap tiles allow the player.

Gate threshold:

- The threshold is the zone where y is below 6.
- Once the gate is open, The Hollow cannot enter any tile where y is below 6.
- The player wins when the gate is open and the player center y coordinate is below 6.

If The Hollow is in the threshold when the gate opens:

- Move The Hollow to the nearest reachable tile where y is 6 or higher.
- Do not damage The Hollow.
- Do not count this as a fail unless The Hollow is still overlapping the player before the win check.

## 4.7 The Hollow State Machine [T1]

The Hollow is the only enemy.

Basic rules:

- The Hollow cannot be killed.
- The Hollow cannot be permanently disabled.
- The Hollow can be avoided, delayed, or kept away using light and cover.
- If The Hollow touches the player, the run fails.
- The Hollow visual may be larger than the gameplay hitbox.
- The Hollow hitbox radius is 0.6 tiles.
- Player hitbox radius is 0.5 tiles.
- Contact fail occurs when distance between player center and Hollow center is 1.1 tiles or less.

States:

| State | Description |
| --- | --- |
| Sleeping | No threat before wake time |
| Waking | 8-second telegraph, non-hostile |
| Curious | Patrols around the wake point |
| Investigating | Moves to the last known player location |
| Searching | Searches around the last known player location |
| Hunting | Actively chases the player |

### Sleeping

- Duration: until run elapsed reaches 90 seconds.
- Movement: none.
- Detection: none.
- Damage: none.

Transition:

- When elapsed reaches 90 seconds, state becomes Waking.
- State timer resets to 0.
- Emit `hollow.wake`.

### Waking

- Duration: 8 seconds.
- Location: Dead Well at 60, 40.
- Movement: none.
- Detection: none.
- Damage: none.
- Purpose: telegraph The Hollow’s activation.

Transition:

- When state timer reaches 8 seconds, state becomes Curious.
- Emit `hollow.state_change`.
- Recalculate path.

### Curious

- Speed: 2.4 tiles per second.
- Behavior:
  - Patrols within a 6-tile radius of the wake point.
  - Chooses new waypoints every 2 seconds or when reached.
  - Avoids active light safe zones.
- Transition:
  - If The Hollow detects the player, it enters Investigating.

### Investigating

- Speed: 3.2 tiles per second.
- Duration: up to 8 seconds.
- Behavior:
  - Moves to the player’s last known position.
  - If it detects the player, it enters Hunting.
  - If it reaches the last known position and does not detect the player, it enters Searching.
- Light rule:
  - If the last known position is inside the player’s light safe zone, The Hollow targets the nearest reachable tile outside the safe radius.

### Searching

- Speed: 3.2 tiles per second.
- Duration: 12 seconds.
- Behavior:
  - Searches around the last known player position.
  - Chooses random waypoints within a 6-tile radius.
  - Avoids light safe zones.
  - If it detects the player, it enters Hunting.
  - If 12 seconds pass without detection, it returns to Curious.

Why Searching matters:

- Gives the player a chance to escape by hiding.
- Prevents The Hollow from permanently chasing the player forever.
- Makes stealth meaningful.
- Rewards using cover and turning off the lantern.

### Hunting

- Speed: 5.0 tiles per second.
- Behavior:
  - Targets the player’s current position if detected.
  - If the player is not detected for 6 seconds, targets the last known position.
  - If detection continues, The Hollow remains in Hunting.
  - If the player is lost for 6 seconds, The Hollow enters Searching.
- Light rule:
  - If the player is inside the light safe zone, The Hollow targets the nearest reachable tile outside the safe radius and waits.
  - If the safe zone shrinks or disappears, The Hollow recalculates its path.

Speed comparison:

| Entity | Speed |
| --- | ---: |
| Player walk | 3.6 tiles per second |
| Player sprint | 6.0 tiles per second |
| The Hollow hunt | 5.0 tiles per second |
| The Hollow hunt in underbrush | 4.25 tiles per second |
| Player sprint in underbrush | 5.1 tiles per second |

Why these speeds:

- The player can outrun The Hollow while sprinting.
- Breath limits how long the player can outrun it.
- Underbrush slows both entities, but the player can still escape if they have breath.
- The Hollow is fast enough to create real pressure.

## 4.8 Perception [T1]

The Hollow detects the player through sight and hearing. Detection is not random.

Sight:

The Hollow can see the player if:

1. The Hollow is not Sleeping or Waking.
2. There is line of sight.
3. The player is within The Hollow’s sight range.

Line of sight:

- Blocked by tree trunks, rocks, and water.
- Not blocked by underbrush.
- Underbrush affects cover state, not ray blocking.

Sight range:

| Player lantern | Player condition | Sight range |
| --- | --- | ---: |
| On, fuel above 0 | Any | light radius + 2 |
| Off or fuel 0 | Covered | 3 tiles |
| Off or fuel 0 | Uncovered | 6 tiles |

Why lantern on increases sight:

- A lit player is easier to see.
- Light is both a defensive tool and a liability.

Why covered range is lower:

- When the lantern is off and the player is in underbrush or adjacent to cover, The Hollow has a much harder time spotting them.

Hearing:

The player generates noise.

Noise is heard if:

1. The Hollow is not Sleeping or Waking.
2. The Hollow is within the noise radius.
3. There is line of sight between The Hollow and the player.
4. Noise is blocked by the same impassable tiles that block sight.
5. Underbrush does not block noise.

Noise radii:

| Action | Noise radius |
| --- | ---: |
| Walking | 5 tiles |
| Sprinting | 10 tiles |
| Sprinting in underbrush | 12 tiles |
| Key pickup | 6 tiles |
| Ember pickup | 4 tiles |
| Gate opening | 12 tiles |

Continuous noise:

- Standing still: 0.
- Walking: 5.
- Sprinting: 10.
- Sprinting in underbrush: 12.

Event noise:

- Key pickup: 6.
- Ember pickup: 4.
- Gate opening: 12.

Detection priority:

- The newest detection becomes the last known position.
- If the player is currently visible, The Hollow targets the player directly.
- If the player is not visible, The Hollow targets the last known position.

Why noise exists:

- Movement is a risk.
- Sprinting is powerful but loud.
- Pickups are useful but can attract The Hollow.
- The final gate opening is a deliberate loud event.

## 4.9 Light Safe Zones [T1]

Safe zone rule:

The safe zone is active when:

- The player’s lantern is on.
- Player fuel is 25 or higher.
- Light radius is above 0.

A tile is safe for The Hollow when:

- Safe zone is active.
- Distance from tile center to player center is less than or equal to light radius.

Use tile center distance.

If The Hollow is already in a tile that becomes safe:

- The Hollow may remain in that tile.
- It cannot enter new safe tiles.
- It can move out of the safe area if its path allows it.

This prevents The Hollow from being permanently trapped inside the player’s light.

If the player stands in light:

- The Hollow waits outside the safe radius.
- Fuel continues to drain.
- Once fuel drops below 25, the safe zone disappears.

Why this is fair:

- The player can defend with light, but cannot stall forever.
- The Hollow cannot cheat through light.
- The player must eventually move because dawn is approaching.

## 4.10 Compass and Objective Aid [T1]

The game includes a subtle objective arrow.

Objective sequence:

1. Find the first bone key.
2. Find the remaining bone keys.
3. Escape before dawn.

Arrow behavior:

- Before all keys are collected, the arrow points to the nearest uncollected bone key.
- After all keys are collected and gate is closed, the arrow points to gate approach 60, 6.
- After all keys are collected and gate is open, the arrow points to gate gap center 60, 4.
- The arrow appears when the objective target is off-screen.
- The arrow is hidden when the target is visible on-screen.
- The arrow is not a minimap.
- The arrow does not show obstacles.

Arrow algorithm:

1. Determine the objective target.
2. Use A* pathfinding from the player to the target.
3. If a path exists, point the arrow toward the first meaningful waypoint after the player’s current tile.
4. If no path exists, fall back to straight-line direction.
5. Update the arrow every 0.5 seconds.

Nearest key tie-break:

- Use Euclidean distance.
- Ties resolve by key ID order: A, B, C.

Why a compass arrow exists:

- Prevents soft-stuck states.
- Reduces frustration.
- Still requires the player to navigate manually.
- Avoids giving away the full map.

Why no minimap:

- A minimap would remove too much tension and make the forest feel less like an unknown space.

## 4.11 Win, Fail, Priority [T1]

Win condition:

The player wins when:

1. The gate is open.
2. The player center y coordinate is below 6.
3. Dawn has not yet arrived.

Fail conditions:

The player fails when either:

1. Dawn remaining time reaches 0 before the win condition is met.
2. The Hollow’s hitbox overlaps the player’s hitbox.

Contact fail:

- Contact occurs when distance between player center and Hollow center is less than or equal to 1.1 tiles.

Frame priority:

If a win condition and a fail condition happen on the same frame:

- Win takes priority.

Check order:

1. Win condition.
2. Fail by The Hollow contact.
3. Fail by dawn.

This means if the player crosses the threshold and a fail condition happens on the same frame, the player wins.

## 4.12 Edge Cases [T1]

| Edge case | Behavior |
| --- | --- |
| Player runs out of fuel | Lantern light radius becomes 0. Safe zone disappears. Player sees ambient range: 3 tiles if covered, 6 tiles if uncovered. Run can still be completed. |
| Player runs out of breath | Sprinting disabled until breath reaches 25. Player can still walk. The Hollow can catch the player if escape is impossible. |
| Player stands in light safe zone | The Hollow waits outside the safe radius. Fuel continues to drain. Once fuel drops below 25, the safe zone disappears. |
| The Hollow cannot path to target | Moves to nearest reachable waypoint. Waits or locally wanders. Does not teleport. Does not pass through blockers. |
| Player hides in underbrush | If lantern is off and player is covered, sight range is 3 tiles. The Hollow can still hear walking noise at 5 tiles, or sprinting in underbrush at 12 tiles. If The Hollow loses the player during Searching, it leaves after 12 seconds. |
| Player reaches gate without all keys | Gate remains closed. Prompt shows sealed. Player cannot win. Dawn can still fail the player. |
| Player opens gate but does not cross | Gate remains open. Player can still cross later. Dawn still applies. The Hollow still applies outside the threshold. |
| The Hollow is in threshold when gate opens | The Hollow moves to nearest reachable tile where y is 6 or higher. No damage. No fail unless still overlapping player before win check. |
| Win and fail happen on same frame | Win takes priority. |
| Player ignores compass | Player may fail by dawn. |
| Player wastes fuel | No separate fail. Reduced visibility and loss of safe-zone defense. |
| Player sprints too much | Breath lock forces tactical pause. Sprinting also makes the player easier to hear. |

## Progression and difficulty

Phase 1: Safe Start

- Time: 0:00 to 1:30.
- Objective: learn movement, lantern, sprint and breath, reach Key A.
- The Hollow is sleeping.
- Feel: curious, slightly tense, not yet in immediate danger.

Phase 2: The Hollow Wakes

- Time: 1:30 to approximately 5:30.
- Objective: collect remaining keys, manage fuel, avoid The Hollow, use cover and light.
- The Hollow is active.
- Feel: pressured, cautious, aware of noise and light.

Phase 3: Escape

- Time: approximately 5:30 to 8:00.
- Objective: reach the gate, open the gate, cross the threshold.
- Feel: fast, risky, resolved.

Expected timing:

| Player skill | Expected time |
| --- | ---: |
| Efficient | 5:30 to 6:30 |
| Cautious | 6:30 to 7:30 |
| Hard fail threshold | 8:00 |

Why these times:

- The player should feel the possibility of failure but not the feeling of impossible timing.
- A cautious player should have enough time if they manage fuel and avoid bad fights.
- A reckless player should fail from noise, bad light use, or bad routing.

## Feel goals

The game should feel:

- Slow at first.
- Increasingly tense after The Hollow wakes.
- Dangerous in the central clearing.
- Quiet in underbrush.
- Desperate near the gate.

Key feel rules:

1. The player should usually have 2 or 3 meaningful choices:
   - Turn lantern on or off.
   - Walk or sprint.
   - Hide or move.
2. The Hollow should never feel random.
   - It should always be reacting to sight or noise.
3. The player should usually understand why they died:
   - They made too much noise.
   - They used too much light.
   - They stayed in the open.
   - They ran out of breath.
   - They ran out of fuel.
   - They were too late.

# 5. CHARACTERS

## Player

Silhouette:

- Hooded figure.
- Dark blue-grey cloak.
- Simple silhouette.
- Small lantern in one hand.
- No detailed face.
- No weapon.
- No armor.
- Human and vulnerable, not heroic.

Sprite size:

- Approximately 40 px by 48 px.
- Visual sprite may be slightly taller than gameplay hitbox.
- Player center is the primary visible point.
- Lantern is clearly visible on one side.

Facing:

- Top-down 8-directional facing.
- Facing follows the last non-zero movement vector.
- If no movement input, facing remains from the last move.

Animation states:

| Animation name | Visual | Motion rule |
| --- | --- | --- |
| player_idle | Subtle breathing, lantern flame steady or mild flicker | Plays when not moving. |
| player_walk | Slow 8-way walk cycle | Plays when moving at walk speed. |
| player_sprint | Faster cycle, slight forward lean, small breath mist | Plays when sprinting. Breath mist appears only while sprinting. |
| player_covered_underbrush | Sprite lowers, lower half darkened, grass tufts over feet | Plays when player center is underbrush. |
| player_covered_blocker | Slight tuck against rock or tree, darker side facing blocker | Plays when adjacent to a blocking tile. |
| player_lantern_on | Warm flame, light mask active | Plays when lantern is on and fuel is above 0. |
| player_lantern_off | Cold ambient halo only | Plays when lantern is off or fuel is 0. |
| player_fuel_low | Flame sputters, light flickers | Plays when fuel is below 20. |
| player_caught | Black tendrils or shadow shape overtakes the player | Plays only on caught fail. |

Motion notes:

- Keep animations small and slow.
- Do not use exaggerated superhero movement.
- Sprint should look urgent but not comedic.
- Breath mist should appear only while sprinting.
- The player should not visually bob too much.

## The Hollow

Silhouette:

- Tall.
- Thin.
- Ragged.
- Dark.
- Cold.
- Slightly larger than the player.
- Not human-shaped enough to be relatable.
- Not too detailed to be distracting.

Sprite size:

- Approximately 64 px by 76 px.
- Visual silhouette may be larger than gameplay hitbox.
- Fatal center is the dense core of the sprite.
- Outer tendrils, shadow, and mist are decorative.
- In high-contrast T2 mode, show a faint cold outline around the fatal core.

Color:

- Body: Deep Night Black.
- Rim: Hollow Blue.
- Eyes: Cold Moon.
- Aura: very faint cold blue.
- State accents: pale cold blue, never red.

Facing:

- Top-down 8-directional facing.
- Facing follows movement target or player direction when detected.
- While Sleeping or Waking, facing is fixed toward the player start or the well center.

Animation states:

| Animation name | Visual | Motion rule |
| --- | --- | --- |
| hollow_sleeping | Dark shape under faint well mist, no eyes, slow breathing distortion | Plays in Sleeping. No movement. |
| hollow_waking | Mist rises, black shape straightens, pale eyes open, cold rim appears | Plays in Waking. No movement. 8-second telegraph. |
| hollow_curious | Dim blue rim, slow drift, head scans, low posture | Plays in Curious. Slow wandering within 6 tiles of wake point. |
| hollow_investigating | Upright, leans toward target, one eye brighter, faint cold trail | Plays in Investigating. Faster, purposeful movement to last known position. |
| hollow_searching | Circling motion, head sweeps, faint ripple around feet | Plays in Searching. Medium patterned movement around last known position. |
| hollow_hunting | Bright eyes, stretched silhouette, faster lurch, cold shadow stretches | Plays in Hunting. Fast urgent movement. |
| hollow_safe_wait | Stops at safe zone edge, shadow may stretch toward light, may pace or lean | Plays when blocked by active safe zone. |
| hollow_caught | Black tendrils consume player and Hollow | Plays only on caught fail. |

State-change cues:

- Brief cold blue pulse around The Hollow.
- Small audio sting or intake.
- If The Hollow is not on screen, use subtle cold vignette pulse and audio only.
- Do not show a marker pointing to The Hollow.

Waking cue:

- At 90 seconds, if The Hollow is visible, well mist rises and the shape forms clearly.
- If The Hollow is not visible, play a low groan and brief cold vignette pulse.
- Music shifts into pressure layer.

Hunting cue:

- The Hollow’s eyes flare briefly.
- A cold blue vignette pulse appears for about 0.5 seconds.
- A short high whisper or cold sting plays.
- The Hollow’s silhouette stretches slightly toward the player.

Interaction with light safe zone:

- When The Hollow is outside an active light safe zone, it stops at the edge.
- Its shadow may stretch toward the light.
- It may pace or lean, but it cannot cross.
- If the safe zone flickers or disappears, its eyes brighten slightly.

# 6. AUDIO

All audio is generated with the Web Audio API. No external audio files are required. Audio starts after a user gesture, usually the title button click.

General rules:

- Music sits below important SFX.
- No music stinger masks key pickup, gate creak, or The Hollow’s hunting cue.
- The Hollow’s state cues are slightly louder than the music bed.
- Ambient wind is subtle and never distracting.
- The final 60 seconds increase tension through pulse and texture, not volume spikes.
- Underbrush changes footstep texture, not noise disappearance.
- Sprinting sounds louder and more urgent than walking.
- The Hollow sounds slightly unnatural.

| Sound name | Web Audio recipe | Rule that plays it |
| --- | --- | --- |
| `music_night_bed` | Loop. Sine oscillator 55 Hz, low-pass noise wind 80 to 200 Hz, gain 0.35, slow LFO on filter cutoff. | Start on `run.start`. Stop on `hollow.wake` only if mystery layer is replaced, or stop on end states. |
| `music_mystery` | Loop. Sparse triangle notes 220 Hz and 262 Hz, each 1.2 seconds long, 4 seconds apart, gain 0.25, low-pass 1200 Hz. | Start on `run.start`. Stop on `hollow.wake`. |
| `music_pressure` | Loop. Low sawtooth 40 Hz with tremolo 0.25 Hz, muted noise pulse 80 Hz every 1.0 seconds, gain 0.40. | Start on `hollow.wake`. Stop on `dawn.warning` or end state. |
| `music_escape` | Loop. Sawtooth 80 Hz pulse every 0.5 seconds, warm triangle pad 110 Hz, gain 0.45, low-pass 1800 Hz. | Start on `dawn.warning`. Stop on end state. |
| `dawn_resolve` | One-shot. Triangle chord 262 Hz, 330 Hz, 392 Hz. 3 seconds attack, 4 seconds release, gain 0.65. | Play on `run.win`. |
| `caught_drone` | One-shot. Detuned sawtooth 55 Hz and 62 Hz. 0.5 seconds attack, 3 seconds decay, low-pass 400 Hz, gain 0.65. | Play on `run.fail.caught` after caught hit. |
| `ambient_wind` | Loop. Filtered noise, low-pass 120 Hz, gain 0.15, slow random LFO. | Runs during Playing. |
| `sfx_key_pickup` | Triangle. Two notes: 880 Hz then 1318 Hz. Each 0.12 seconds. 0.01 second attack, 0.25 second decay. Add short reverb tail 0.4 seconds. | Play on `pickup.key`. |
| `sfx_ember_pickup` | Filtered noise, band-pass 2000 to 6000 Hz, plus triangle sparkle 1800 Hz. 0.3 seconds duration. 0.01 second attack, 0.3 second decay. Warm low-pass 4000 Hz. | Play on `pickup.ember`. |
| `sfx_step_walk` | Low noise, band-pass 100 to 300 Hz. 0.1 seconds decay. Dry. | Play on `player.step` with type `walk` every 0.35 seconds while moving. |
| `sfx_step_sprint` | Low noise, band-pass 200 to 500 Hz. 0.08 seconds decay. Dry, sharper. | Play on `player.step` with type `sprint` every 0.20 seconds while moving. |
| `sfx_step_walk_underbrush` | Dry leaf rustle: filtered noise 400 to 1200 Hz. 0.12 seconds decay. Muffled but present. | Play on `player.step` with type `walk_underbrush` every 0.35 seconds while moving in underbrush. |
| `sfx_step_sprint_underbrush` | Crunchier rustle: filtered noise 600 to 1800 Hz. 0.10 seconds decay. Louder. | Play on `player.step` with type `sprint_underbrush` every 0.20 seconds while moving in underbrush. |
| `sfx_lantern_on` | Sine click 300 Hz plus short noise whoosh, low-pass 800 Hz. 0.2 seconds duration. 0.02 second attack, 0.2 second decay. | Play when lantern toggles on. |
| `sfx_lantern_off` | Noise hiss, low-pass 1200 Hz. 0.15 seconds duration. 0.02 second attack, 0.15 second decay. | Play when lantern toggles off. |
| `sfx_fuel_low` | Square tick 1200 Hz plus faint noise sizzle 3000 Hz. 0.15 seconds duration. 0.01 second attack, 0.15 second decay. | Play once when fuel crosses below 20. Reset when fuel increases back above 20. |
| `sfx_dawn_warning` | Rising triangle 220 Hz to 440 Hz over 0.8 seconds, gain 0.35. | Play once when dawn remaining crosses below 60 seconds. |
| `sfx_gate_ready` | Low sine hum 80 Hz, 0.5 seconds duration, 0.1 second attack, 0.4 seconds decay. | Play when prompt changes from locked to hold-to-open. |
| `sfx_gate_open` | Sawtooth 80 to 120 Hz with slow pitch bend over 1.5 to 3 seconds, plus low noise rumble 60 to 120 Hz. 2 seconds duration. 0.2 second attack, 2 seconds decay. | Play on `gate.open`. |
| `sfx_hollow_wake` | Detuned sawtooth 50 to 80 Hz. 8 seconds swell. Very low, distant, low-pass 500 Hz. | Play on `hollow.wake`. |
| `sfx_hollow_state` | Filtered noise 1500 to 4000 Hz, plus sine 700 Hz. 0.3 seconds duration. 0.05 second attack, 0.3 seconds decay. | Play on `hollow.state_change` except when entering Hunting. |
| `sfx_hollow_hunt` | Filtered noise 1500 to 4000 Hz, plus sine 1000 Hz. 0.4 seconds attack, 0.6 seconds decay. Cold, airy. | Play when `hollow.state_change` to Hunting. |
| `sfx_caught` | Dissonant cold hit: sawtooth 55 Hz and 62 Hz, plus noise burst 1000 Hz. 0.4 seconds duration. 0.01 second attack, 0.4 seconds decay. | Play on `run.fail.caught`. |
| `sfx_dawn_fail` | Quiet bright chord: triangle 262 Hz, 330 Hz, 392 Hz. 3 seconds attack, 4 seconds release. Wind and distant birds optional T2. | Play on `run.fail.dawn`. |
| `sfx_win` | Gentle dawn chord: triangle 262 Hz, 330 Hz, 392 Hz with warm sine 131 Hz. 3 seconds attack, 4 seconds release. | Play on `run.win`. |
| `sfx_breath_locked` | Exhausted gasp: filtered noise 800 to 1500 Hz. 0.3 seconds duration. 0.05 second attack, 0.3 seconds decay. | Play on `player.breath.locked`. |

Music layer mapping:

| Sim event | Audio action |
| --- | --- |
| `run.start` | Start `night_bed` and `mystery`. |
| `hollow.wake` | Stop `mystery`, start `pressure`, play `sfx_hollow_wake`. |
| `hollow.state_change` to Hunting | Play `sfx_hollow_hunt`. |
| `hollow.state_change` to other active states | Play `sfx_hollow_state`. |
| `player.fuel.low` | Play `sfx_fuel_low`. |
| `dawn.warning` | Start `escape`. |
| `gate.open` | Play `sfx_gate_open`. |
| `run.win` | Stop all loops, play `sfx_win`. |
| `run.fail.caught` | Stop all loops, play `sfx_caught`, then `caught_drone`. |
| `run.fail.dawn` | Stop all loops, play `sfx_dawn_fail`. |

# 7. UX

All screens and HUD are HTML and CSS only. Canvas renders the world. DOM overlays render state screens and HUD.

## State machine

| State | Entry | Visible DOM | Allowed transitions |
| --- | --- | --- | --- |
| `title` | Page load | Title overlay, control list, Begin the Night button | Begin click to `playing` |
| `playing` | Begin click or retry | Canvas world, HUD, interaction prompt, onboarding text | Win to `won`, caught fail to `failed`, dawn fail to `failed` |
| `won` | Win condition | Win overlay, `You crossed before dawn.`, `Time: mm:ss`, `Play again` | R key or Play again click to `playing` |
| `failed` | Caught fail or dawn fail | Fail overlay, fail text, `Press R to retry` | R key to `playing` |

No pause state is included in T1.

Title screen:

- Dark forest background.
- A single lantern glow in the center.
- Game title in bone white, slightly rustic but readable.
- Simple control list.
- One primary button: `Begin the Night`.
- Controls shown:
  - Move: WASD / Arrow Keys
  - Sprint: Shift / Space
  - Lantern: L
  - Interact: E

Failed: Caught by The Hollow:

- Text: `The Hollow found you.`
- Text: `Press R to retry`
- Visual: black tendrils spread across the screen, then screen darkens.
- Audio: short dissonant cold hit, then low drone and near silence.

Failed: Dawn Arrives:

- Text: `Dawn came before you escaped.`
- Text: `Press R to retry`
- Visual: forest floods with soft Dawn Gold.
- Audio: quiet bright chord, wind, distant birds optional T2.

Win: Escape Before Dawn:

- Text: `You crossed before dawn.`
- Text: `Time: mm:ss`
- Button or key: `Play again`
- Visual: screen brightens into dawn light, forest behind becomes soft and distant.
- Audio: gentle morning chord, soft wind, birds optional T2.

## HUD table

| HUD element | Record field | When visible |
| --- | --- | --- |
| Dawn timer | `sim.hud.timeRemaining` formatted mm:ss | Playing |
| Moon/sun dial | `sim.hud.timeRemaining` | Playing |
| Objective text | `sim.hud.objectiveText` | Playing |
| Key slots | `sim.hud.keysCollected` | Playing |
| Fuel bar | `sim.hud.fuel` | Playing |
| Breath bar | `sim.hud.breath` and `sim.hud.breathLocked` | Playing |
| Objective arrow | `sim.hud.arrow.visible` and `sim.hud.arrow.angle` | Playing and arrow visible |
| Interaction prompt | `sim.hud.prompt.type`, `text`, `progress` | Playing and gate prompt active |
| Onboarding text | `sim.hud.onboardingVisible` and `onboardingText` | Playing and onboarding active |
| Fuel warning | `sim.hud.warnings.fuelLow` | Playing and fuel below 20 |
| Dawn warning | `sim.hud.warnings.dawnLow` | Playing and time remaining below 60 |
| Win overlay | `sim.hud.state` | Won |
| Fail overlay | `sim.hud.state` and fail reason | Failed |

HUD rules:

- Dawn timer displays mm:ss.
- Timer warning below 60 seconds uses Dawn Gold, pulse, and top-edge dawn glow.
- Moon/sun dial shows progression from night to dawn.
- Objective text fades in when the objective changes.
- Key slots show 0 to 3 collected keys.
- Empty key slots show pale bone outline.
- Filled key slots show bone white fill and a short pop animation.
- Fuel bar is approximately 140 px wide and 10 px tall.
- Fuel bar has a small flame icon on the left.
- Fuel below 30: flame icon flickers.
- Fuel below 20: flame icon flickers strongly, bar color shifts to dull orange, warning pulse appears.
- No numerical fuel value is shown.
- Breath bar is below fuel, approximately 140 px wide and 6 px tall.
- Breath bar color is pale cold blue.
- When breath reaches 0: bar becomes empty, a faint slash or locked icon appears, sprinting is visually locked.
- Sprinting becomes available again when breath reaches 25.
- No numerical breath value is shown.
- Objective arrow is a bone-white arrow approximately 24 px, placed 20 px from screen edge, pointing toward current objective.
- Arrow is hidden when objective target is visible on-screen.
- Arrow pulses gently when visible.
- Interaction prompt appears near player when relevant.
- Gate locked prompt: small gray bone key icon, text `Sealed (x / 3)`.
- Gate ready prompt: bright bone key icon, text `Hold E to open`, circular progress ring fills over 2 seconds.
- If player releases early, ring shrinks quickly according to charge decay.
- Gate opening prompt: text `The gate is open`, soft dawn pulse at threshold.
- Onboarding text appears bottom-center or near player, low opacity, fades quickly, never blocks movement.
- No minimap, health bar, enemy position marker, fuel number, breath number, inventory list, quest log, or pause menu is shown.

# 8. DEBUG API

Debug and test API is for tests and scripted playthroughs. The browser App must not use these functions for normal gameplay. They must not break normal sim behavior.

## 8.1 Test factory functions

| Function | Purpose |
| --- | --- |
| `createSim(options)` | Creates a sim with map, config, seed, audio, and input. Options may override defaults. |
| `createMockAudio()` | Returns an audio recorder with `play`, `startLayer`, `stopLayer`, `setPhase`, and `calls`. |
| `createMockInput()` | Returns an input object with functions from section 8.3. |
| `createMapFixture()` | Creates a small deterministic map for engine tests. |
| `loadRealMap()` | Loads `assets/map.json` as a map object. |
| `advanceSim(sim, seconds, inputFactory)` | Advances sim in fixed steps using an input factory that receives sim and returns an input frame. |
| `validateMap(mapJson)` | Runs the map contract validator and returns errors. |
| `renderSimFrame(sim, mockCanvas)` | Renders one frame to a mock canvas for renderer tests. |

## 8.2 Sim debug functions

| Function | Purpose |
| --- | --- |
| `sim.debug.setElapsed(seconds)` | Sets run elapsed time. |
| `sim.debug.setDawnRemaining(seconds)` | Sets dawn remaining time. |
| `sim.debug.setPlayerState(partial)` | Sets player fields such as pos, fuel, breath, lanternOn, keysCollected, breathLocked. |
| `sim.debug.setHollowState(state, pos)` | Sets Hollow state and position. |
| `sim.debug.setHollowTimers(partial)` | Sets Hollow stateTimer, lostTimer, waypointTimer, pathTimer. |
| `sim.debug.forceGateOpen()` | Sets gate open and applies threshold exclusion. |
| `sim.debug.forceGateClosed()` | Sets gate closed and resets charge. |
| `sim.debug.setGateCharge(seconds)` | Sets gate charge. |
| `sim.debug.addNoiseEvent(event)` | Adds a one-time noise event with x, y, radius. |
| `sim.debug.collectNoiseEvents()` | Returns queued noise events and clears the queue. |
| `sim.debug.giveKey(id)` | Marks a key collected and updates HUD. |
| `sim.debug.giveEmber(id)` | Marks an ember collected and adds fuel. |
| `sim.debug.setPickupCollected(id, value)` | Sets a key or ember collected flag. |
| `sim.debug.setObjectiveTarget(pos)` | Overrides objective target for arrow tests. |
| `sim.debug.setArrow(visible, angle)` | Sets arrow visible and angle. |
| `sim.debug.findPath(from, to, options)` | Runs pathfinding with player or Hollow predicate. |
| `sim.debug.nearestReachable(from, to, options)` | Runs nearest reachable fallback. |
| `sim.debug.hasLineOfSight(from, to)` | Checks line of sight. |
| `sim.debug.lightRadius()` | Returns current light radius. |
| `sim.debug.safeActive()` | Returns whether safe zone is active. |
| `sim.debug.isSafeTile(tx, ty)` | Returns whether a tile is currently safe for The Hollow. |
| `sim.debug.detect()` | Returns current perception detection result. |
| `sim.debug.simSnapshot()` | Returns a shallow snapshot of sim state for assertions. |
| `sim.debug.setRngSeed(seed)` | Resets sim RNG to a supplied seed. |

## 8.3 Player input functions

| Function | Purpose |
| --- | --- |
| `input.setMove(x, y)` | Sets movement direction, x and y are -1, 0, or 1. |
| `input.setSprint(value)` | Sets sprint held. |
| `input.pressLantern()` | Presses lantern toggle once. |
| `input.setInteract(value)` | Sets gate interact held. |
| `input.pressRetry()` | Presses retry once. |

# 9. TESTS

All tests use functions from section 8. Expected states follow from section 4 rules.

## 9.1 Core and math tests

| ID | Call | Expected state |
| --- | --- | --- |
| CORE-001 | `createSim({})`, then `sim.debug.simSnapshot()` | Sim state is title with default config. |
| CORE-002 | `createSim({ seed: 123 })`, then advance two steps, then `createSim({ seed: 123 })` and advance two steps | RNG-driven waypoint states are identical. |
| CORE-003 | `createSim({})`, then `sim.debug.setDawnRemaining(480)`, then `advanceSim(sim, 1, idleInput)` | Dawn remaining is 479. |
| CORE-004 | `createMockInput()`, then `input.setMove(1, 1)`, then `input.frame()` | Input frame moveX is 1 and moveY is 1. |
| CORE-005 | `createMockInput()`, then `input.setSprint(true)`, then `input.frame()` | Input frame sprint is true. |

## 9.2 Map tests

| ID | Call | Expected state |
| --- | --- | --- |
| MAP-001 | `createMapFixture()`, then `map.tileAt(0, 0)` | Border tile is impassable. |
| MAP-002 | `loadRealMap()`, then `validateMap(mapJson)` | No contract errors. |
| MAP-003 | `loadRealMap()`, then `map.isInGateGap(60, 4)` | True. |
| MAP-004 | `loadRealMap()`, then `map.isPassable(60, 6)` | True. |
| MAP-005 | `loadRealMap()`, then `map.objectAt(95, 60)` | Key A. |
| MAP-006 | `loadRealMap()`, then count underbrush clusters | At least 8 clusters. |
| MAP-007 | `loadRealMap()`, then check clusters near 60, 6 | At least 2 clusters within Chebyshev distance 6. |
| MAP-008 | `loadRealMap()`, then run route length checks | Start to A 120 to 160, A to C 120 to 160, C to B 160 to 200, B to gate 160 to 200, total 550 to 750. |

## 9.3 Collision tests

| ID | Call | Expected state |
| --- | --- | --- |
| COL-001 | `createSim({})`, set player near tree, `input.setMove` into tree, `advanceSim(sim, 1, inputFactory)` | Player position does not enter tree tile. |
| COL-002 | `createSim({})`, set player near underbrush, move into underbrush | Player center enters underbrush tile. |
| COL-003 | `createSim({})`, set player at diagonal corner, move diagonally around blocker | Player does not cut corner. |
| COL-004 | `createSim({})`, gate closed, set player near gap, move north into gap | Player does not enter closed gap. |
| COL-005 | `createSim({})`, `sim.debug.forceGateOpen()`, move north into gap | Player enters gap. |
| COL-006 | `createSim({})`, set safe zone active, place Hollow outside safe tile, force movement into safe tile | Hollow does not enter active safe tile. |
| COL-007 | `createSim({})`, place Hollow in tile, make tile safe after Hollow is already there | Hollow remains in tile and does not teleport. |

## 9.4 Line-of-sight tests

| ID | Call | Expected state |
| --- | --- | --- |
| LOS-001 | `sim.debug.hasLineOfSight(a, b)` with tree between | False. |
| LOS-002 | `sim.debug.hasLineOfSight(a, b)` with rock between | False. |
| LOS-003 | `sim.debug.hasLineOfSight(a, b)` with water between | False. |
| LOS-004 | `sim.debug.hasLineOfSight(a, b)` with underbrush between | True. |

## 9.5 Pathfinding tests

| ID | Call | Expected state |
| --- | --- | --- |
| PATH-001 | `sim.debug.findPath(start, target, { forHollow: false })` in open area | Path exists. |
| PATH-002 | `sim.debug.findPath(start, target, { forHollow: false })` with blockers | Path does not enter impassable tiles. |
| PATH-003 | `sim.debug.findPath(start, target, { forHollow: true })` with safe predicate | Path avoids active safe tiles. |
| PATH-004 | `sim.debug.findPath` through underbrush | Underbrush tile cost is 1.25. |
| PATH-005 | `sim.debug.nearestReachable(start, unreachableTarget, { forHollow: true })` | Returns nearest reachable tile, not null. |
| PATH-006 | `sim.debug.findPath` diagonal through corner | Diagonal path does not cut blocked corners. |

## 9.6 Player tests

| ID | Call | Expected state |
| --- | --- | --- |
| PLAYER-001 | Set idle, `input.setMove(1, 0)`, `advanceSim(sim, 1, inputFactory)` | Player moves approximately 3.6 tiles. |
| PLAYER-002 | Set idle, `input.setMove(1, 0)`, `input.setSprint(true)`, `advanceSim(sim, 1, inputFactory)` | Player moves approximately 6.0 tiles while breath remains. |
| PLAYER-003 | Place player in underbrush, walk 1 second | Movement is approximately 3.06 tiles. |
| PLAYER-004 | `sim.debug.setPlayerState({ breath: 100 })`, sprint for 1 second | Breath decreases by 20. |
| PLAYER-005 | `sim.debug.setPlayerState({ breath: 100 })`, walk for 1 second | Breath increases by 15. |
| PLAYER-006 | `sim.debug.setPlayerState({ breath: 100 })`, stand for 1 second | Breath increases by 30. |
| PLAYER-007 | `sim.debug.setPlayerState({ breath: 0 })`, sprint input, advance 1 second | Player does not sprint. |
| PLAYER-008 | `sim.debug.setPlayerState({ breath: 20 })`, stand 1 second | Breath reaches at least 25 and breathLocked becomes false if it was locked. |
| PLAYER-009 | `sim.debug.setPlayerState({ fuel: 50 })`, lantern on, advance 1 second | Fuel decreases by 0.5. |
| PLAYER-010 | `sim.debug.setPlayerState({ fuel: 70 })`, `sim.debug.giveEmber('E1')` | Fuel is 100. |
| PLAYER-011 | `sim.debug.setPlayerState({ fuel: 50 })`, `sim.debug.lightRadius()` | Light radius is 6.0. |
| PLAYER-012 | `sim.debug.setPlayerState({ fuel: 25 })`, lantern on, `sim.debug.safeActive()` | True. |
| PLAYER-013 | `sim.debug.setPlayerState({ fuel: 24.999 })`, lantern on, `sim.debug.safeActive()` | False. |
| PLAYER-014 | Place player in underbrush, `sim.debug.simSnapshot()` | Player covered is true. |
| PLAYER-015 | Place player adjacent to rock, `sim.debug.simSnapshot()` | Player covered is true. |

## 9.7 Lighting tests

| ID | Call | Expected state |
| --- | --- | --- |
| LIGHT-001 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 100 })`, `sim.debug.lightRadius()` | Radius is 8.0. |
| LIGHT-002 | `sim.debug.setPlayerState({ lanternOn: false, fuel: 100 })`, `sim.debug.lightRadius()` | Radius is 0. |
| LIGHT-003 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 0 })`, `sim.debug.lightRadius()` | Radius is 0. |
| LIGHT-004 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 25 })`, `sim.debug.isSafeTile` at player center tile | True. |
| LIGHT-005 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 24.999 })`, `sim.debug.isSafeTile` at player center tile | False. |
| LIGHT-006 | `sim.debug.setPlayerState({ covered: true, lanternOn: false })`, `sim.debug.visibleRange()` | Range is 3. |
| LIGHT-007 | `sim.debug.setPlayerState({ covered: false, lanternOn: false })`, `sim.debug.visibleRange()` | Range is 6. |

## 9.8 Perception tests

| ID | Call | Expected state |
| --- | --- | --- |
| PERC-001 | Set player lit with fuel 50, place Hollow within light radius plus 2, line of sight clear | Detection seen is true. |
| PERC-002 | Set player off, covered, place Hollow 3 tiles away with line of sight | Detection seen is true. |
| PERC-003 | Set player off, covered, place Hollow 3.5 tiles away with line of sight | Detection seen is false. |
| PERC-004 | Set player off, uncovered, place Hollow 6 tiles away with line of sight | Detection seen is true. |
| PERC-005 | Set player walking, Hollow 5 tiles away, line of sight clear | Detection heard is true. |
| PERC-006 | Set player sprinting, Hollow 10 tiles away, line of sight clear | Detection heard is true. |
| PERC-007 | Set player sprinting in underbrush, Hollow 12 tiles away, line of sight clear | Detection heard is true. |
| PERC-008 | Set player walking, Hollow 5 tiles away, tree between | Detection heard is false. |
| PERC-009 | `sim.debug.giveKey('A')` near Hollow with line of sight | Noise event radius 6 is processed and detection can occur. |
| PERC-010 | `sim.debug.giveEmber('E1')` near Hollow with line of sight | Noise event radius 4 is processed and detection can occur. |
| PERC-011 | `sim.debug.forceGateOpen()` with Hollow within 12 tiles and line of sight | Noise event radius 12 is processed and detection can occur. |

## 9.9 Hollow tests

| ID | Call | Expected state |
| --- | --- | --- |
| HOLLOW-001 | `sim.debug.setElapsed(89.999)`, advance 1 second | Hollow state is Waking. |
| HOLLOW-002 | `sim.debug.setHollowState('Waking', { x: 60, y: 40 })`, advance 8 seconds | Hollow state is Curious. |
| HOLLOW-003 | Set Hollow Curious, move toward waypoint for 1 second | Speed is approximately 2.4 tiles per second. |
| HOLLOW-004 | Set Hollow Investigating, move toward target for 1 second | Speed is approximately 3.2 tiles per second. |
| HOLLOW-005 | Set Hollow Searching, move toward target for 1 second | Speed is approximately 3.2 tiles per second. |
| HOLLOW-006 | Set Hollow Hunting, move toward target for 1 second | Speed is approximately 5.0 tiles per second. |
| HOLLOW-007 | Set Hollow in underbrush while Hunting, move 1 second | Speed is approximately 4.25 tiles per second. |
| HOLLOW-008 | Set Hollow Curious, make player detected | Hollow state is Investigating. |
| HOLLOW-009 | Set Hollow Investigating, make player detected | Hollow state is Hunting. |
| HOLLOW-010 | Set Hollow Hunting, no detection for 6 seconds | Hollow state is Searching. |
| HOLLOW-011 | Set Hollow Searching, advance 12 seconds with no detection | Hollow state is Curious. |
| HOLLOW-012 | Place player in safe zone, Hollow Hunting outside radius | Hollow waits outside safe radius. |
| HOLLOW-013 | Set fuel below 25 while Hollow waiting | Safe zone disappears and Hollow can enter. |
| HOLLOW-014 | `sim.debug.forceGateOpen()` with Hollow at y below 6 | Hollow moves to nearest reachable tile where y is 6 or higher. |

## 9.10 Gate and pickup tests

| ID | Call | Expected state |
| --- | --- | --- |
| GATE-001 | Set keysCollected 1, player near gate, `input.setInteract(true)`, advance 1 second | Prompt type is locked and charge stays 0. |
| GATE-002 | Set keysCollected 3, player near gate, `input.setInteract(true)`, advance 2 seconds | Gate opens. |
| GATE-003 | Set gateCharge 1, `input.setInteract(false)`, advance 0.5 seconds | Gate charge is 0. |
| GATE-004 | `sim.debug.forceGateOpen()`, then advance 10 seconds | Gate remains open. |
| PICKUP-001 | Place player within 0.75 tiles of Key A, advance 1 step | keysCollected becomes 1 and Key A collected is true. |
| PICKUP-002 | Place player within 0.75 tiles of Ember E1, advance 1 step | Fuel increases by 40 and E1 collected is true. |
| PICKUP-003 | Place player within 0.75 tiles of Key A, `sim.debug.collectNoiseEvents()` | Noise event radius 6 exists. |
| PICKUP-004 | Place player within 0.75 tiles of Ember E1, `sim.debug.collectNoiseEvents()` | Noise event radius 4 exists. |
| PICKUP-005 | Pick up Key A twice in separate steps | Key is collected only once. |

## 9.11 GameSim tests

| ID | Call | Expected state |
| --- | --- | --- |
| SIM-001 | `createSim({})`, start run, `sim.debug.simSnapshot()` | Initial state matches section 4.1. |
| SIM-002 | `sim.debug.setDawnRemaining(0)`, advance 1 step without win | State is failed with dawn fail. |
| SIM-003 | Place player and Hollow overlapping, advance 1 step | State is failed with caught fail. |
| SIM-004 | `sim.debug.forceGateOpen()`, set player y below 6, advance 1 step | State is won. |
| SIM-005 | Set player y below 6, gate open, Hollow overlapping, advance 1 step | State is won. |
| SIM-006 | Set dawn remaining 0, gate open, player y below 6, advance 1 step | State is won. |
| SIM-007 | `sim.retry(seed)`, then snapshot | All run state resets. |
| SIM-008 | Create sim with config `hollowEnabled: false`, run full route | Full route test can run without Hollow interference. |

## 9.12 Integration tests

| ID | Call | Expected state |
| --- | --- | --- |
| INTEG-001 | `createMockAudio()`, `createSim({ audio })`, trigger `pickup.key`, inspect audio calls | Audio calls include `sfx_key_pickup`. |
| INTEG-002 | `createMockAudio()`, trigger `hollow.wake`, inspect audio calls | Audio calls include `startLayer` for pressure and `sfx_hollow_wake`. |
| INTEG-003 | `createMockAudio()`, trigger `hollow.state_change` to Hunting, inspect audio calls | Audio calls include `sfx_hollow_hunt`. |
| INTEG-004 | `createMockAudio()`, trigger `player.fuel.low`, inspect audio calls | Audio calls include `sfx_fuel_low`. |
| INTEG-005 | `sim.debug.setDawnRemaining(59.999)`, advance 1 step, inspect HUD | Dawn warning is true. |
| INTEG-006 | `sim.debug.setPlayerState({ fuel: 19.999 })`, advance 1 step, inspect HUD | Fuel warning is true. |
| INTEG-007 | Set keysCollected 0, snapshot HUD | Objective text is `Find the bone keys`. |
| INTEG-008 | Set keysCollected 1, not near gate, snapshot HUD | Objective text is `Find the remaining bone keys`. |
| INTEG-009 | Set keysCollected 3, near gate, gate closed, snapshot HUD | Objective text is `Hold to open the gate`. |
| INTEG-010 | Set gate open, snapshot HUD | Objective text is `Cross the threshold`. |
| INTEG-011 | Set objective target off-screen, `sim.debug.setArrow(true, 90)`, inspect HUD | Arrow visible is true. |
| INTEG-012 | Set objective target on-screen, update arrow, inspect HUD | Arrow visible is false. |
| INTEG-013 | `loadRealMap()`, `createSim({ map, config with hollowEnabled false })`, scripted full route | State becomes won, all 3 keys collected, at least embers E1, E2, E4, E5 collected, dawn has not reached 0. |
| INTEG-014 | `loadRealMap()`, active Hollow, set player 60,6, keys 3, fuel 100, lantern on, Hollow Hunting at 60,20, hold E for 2 seconds then move north | Gate opens, player wins, no caught fail, Hollow does not enter safe zone while fuel is 25 or higher. |
| INTEG-015 | Cause fail, then `input.pressRetry()`, start run | New run has all initial values. |

## 9.13 Renderer and UX tests

| ID | Call | Expected state |
| --- | --- | --- |
| UX-001 | `renderSimFrame(sim, mockCanvas)` in title state | No exception. |
| UX-002 | `renderSimFrame(sim, mockCanvas)` in playing state | Canvas draw calls occur for visible tiles. |
| UX-003 | Set safe active, `renderSimFrame(sim, mockCanvas)` | Safe edge stroke occurs. |
| UX-004 | Set fuel below 25, `renderSimFrame(sim, mockCanvas)` | Safe edge is not drawn as active. |
| UX-005 | Set playing HUD fields, inspect DOM HUD | Timer, fuel bar, breath bar, key slots, and objective text are visible. |
| UX-006 | Set state won, inspect DOM | Win screen is visible and retry works. |
| UX-007 | Set state failed, inspect DOM | Fail screen is visible and retry works. |
| UX-008 | Set fuel below 20, inspect DOM HUD | Fuel warning uses pulse or shape, not only color. |

## 9.14 Map contract and performance tests

| ID | Call | Expected state |
| --- | --- | --- |
| CONTRACT-001 | `validateMap(loadRealMap())` | Map width 120, height 80, border impassable, gate gap valid, objects reachable, route targets met, underbrush clusters present, corridor heuristic passes. |
| PERF-001 | `createSim({})`, `advanceSim(sim, 480, idleInput)` | Simulation completes without exceptions. |
| PERF-002 | `createSim({})`, `advanceSim(sim, 480, scriptedInput)` in test environment | 28,800 fixed updates complete under 10 seconds. |
| PERF-003 | Run full route with pathfinding at 2 Hz | A* allocations do not grow unbounded across the run. |

## SCREENSHOTS

| Screenshot ID | Screen or state | Required visible elements |
| --- | --- | --- |
| SHOT-01 | Title screen | Dark forest background, lantern glow, title, control list, Begin the Night button. |
| SHOT-02 | Playing, safe start | Player in Start Clearing, lantern light, timer 08:00, fuel bar 50, breath bar 100, empty key slots, objective text. |
| SHOT-03 | Playing, onboarding Move | Small `Move` text near player or bottom-center. |
| SHOT-04 | Playing, onboarding Sprint | Small `Sprint` text near player or bottom-center. |
| SHOT-05 | Playing, onboarding Lantern | Small `Lantern` text near player or bottom-center. |
| SHOT-06 | Playing, objective arrow | Bone-white arrow at screen edge pointing off-screen objective. |
| SHOT-07 | Playing, key pickup | Key slot fills, small white pulse at key location. |
| SHOT-08 | Playing, ember pickup | Amber spark, fuel bar rises, lantern flame brightens briefly. |
| SHOT-09 | Playing, covered in underbrush | Player sprite lowered and darker, grass tufts over feet, ambient halo smaller if lantern off. |
| SHOT-10 | Playing, light safe zone active | Soft amber safe edge at light radius, Hollow waiting outside. |
| SHOT-11 | Playing, fuel below 30 | Safe edge flickers, flame icon flickers. |
| SHOT-12 | Playing, fuel below 20 | Fuel bar warning pulse, flame sputters, safe zone gone. |
| SHOT-13 | Hollow waking | Well mist rises, Hollow shape forms, cold vignette pulse if not visible. |
| SHOT-14 | Hollow curious | Hollow dim blue rim, slow drift near Dead Well. |
| SHOT-15 | Hollow investigating | Hollow upright, leans toward last known position, one eye brighter. |
| SHOT-16 | Hollow searching | Hollow circling motion, head sweeps, faint ripple around feet. |
| SHOT-17 | Hollow hunting | Bright eyes, stretched silhouette, cold vignette pulse, fast lurch. |
| SHOT-18 | Gate locked prompt | Gate visible, gray bone key icon, text `Sealed (x / 3)`. |
| SHOT-19 | Gate ready prompt | Bright bone key icon, text `Hold E to open`, circular progress ring. |
| SHOT-20 | Gate opened | Light leaks through gap, threshold glow appears, text `The gate is open`. |
| SHOT-21 | Dawn below 60 seconds | Timer pulses gold, top edge gains dawn glow, dial glows. |
| SHOT-22 | Win screen | Dawn light, text `You crossed before dawn.`, `Time: mm:ss`, Play again. |
| SHOT-23 | Caught fail screen | Black tendrils consume screen, text `The Hollow found you.`, `Press R to retry`. |
| SHOT-24 | Dawn fail screen | Dawn Gold flood, text `Dawn came before you escaped.`, `Press R to retry`. |

# 10. BUILD ORDER

| Milestone | Work | Check that shows it landed |
| --- | --- | --- |
| M0: Project shell | Create files, package.json, input, clock, RNG, event bus, math helpers. | CORE-001, CORE-002, CORE-004, CORE-005 |
| M1: Map and validation | Create `assets/map.json`, Map class, validator. | MAP-001 to MAP-008, CONTRACT-001 |
| M2: Player movement and breath | Collision, underbrush, sprint, breath lock. | COL-001 to COL-003, PLAYER-001 to PLAYER-008 |
| M3: Light and perception | Light radius, safe zone, LOS, hearing. | LIGHT-001 to LIGHT-007, PERC-001 to PERC-011, LOS-001 to LOS-004 |
| M4: Pathfinding and Hollow | A*, no-path fallback, Hollow state machine. | PATH-001 to PATH-006, HOLLOW-001 to HOLLOW-014 |
| M5: Pickups and gate | Keys, embers, gate hold, threshold. | PICKUP-001 to PICKUP-005, GATE-001 to GATE-004 |
| M6: Win, fail, retry | Sim states, win priority, fail checks, retry. | SIM-001 to SIM-008 |
| M7: Audio, UX, render | Web Audio recipes, DOM HUD, screens, renderer. | INTEG-001 to INTEG-005, UX-001 to UX-008, SHOT-01 to SHOT-24 |
| M8: Integration playthroughs | Full route and gate under threat. | INTEG-013, INTEG-014, INTEG-015 |
| M9: Performance and smoke | Performance budget, manual browser smoke. | PERF-001 to PERF-003, manual smoke checklist in section 11 |

# 11. DEFINITION OF DONE

### DoD: Explore a haunted forest at night

- Checks: MAP-001 to MAP-008, UX-002, SHOT-02, SHOT-09.
- Screenshot rows: SHOT-02, SHOT-09.

### DoD: Escape before dawn

- Checks: SIM-002, SIM-004, SIM-005, SIM-006, INTEG-013, SHOT-21, SHOT-22.
- Screenshot rows: SHOT-21, SHOT-22.

### DoD: One handcrafted 2D top-down forest map

- Checks: CONTRACT-001, MAP-003 to MAP-008, PERF-003.
- Screenshot rows: SHOT-02, SHOT-24.

### DoD: Lantern fuel as a core resource

- Checks: PLAYER-009, PLAYER-010, LIGHT-001 to LIGHT-005, SHOT-10, SHOT-11, SHOT-12.
- Screenshot rows: SHOT-10, SHOT-11, SHOT-12.

### DoD: Sprint breath as a core resource

- Checks: PLAYER-002 to PLAYER-008, SHOT-04.
- Screenshot rows: SHOT-04.

### DoD: One readable hunter, The Hollow

- Checks: HOLLOW-001 to HOLLOW-014, SHOT-13 to SHOT-17.
- Screenshot rows: SHOT-13, SHOT-14, SHOT-15, SHOT-16, SHOT-17.

### DoD: Three bone keys required to open the gate

- Checks: PICKUP-001, GATE-001, GATE-002, SHOT-07, SHOT-18.
- Screenshot rows: SHOT-07, SHOT-18.

### DoD: Old Gate threshold win zone

- Checks: GATE-002, GATE-004, HOLLOW-014, SIM-004, SHOT-20.
- Screenshot rows: SHOT-20.

### DoD: Readable visual and audio cues

- Checks: INTEG-001 to INTEG-005, UX-005, SHOT-07 to SHOT-24.
- Screenshot rows: SHOT-07, SHOT-08, SHOT-13, SHOT-17, SHOT-22, SHOT-23, SHOT-24.

### DoD: Retry resets the entire run

- Checks: SIM-007, INTEG-015, UX-006, UX-007.
- Screenshot rows: SHOT-22, SHOT-23, SHOT-24.

### DoD: Deterministic, headless-testable simulation

- Checks: CORE-002, PERF-001, PERF-002, INTEGRATION tests.
- Screenshot rows: none required, manual smoke confirms browser run.

### DoD: HTML and CSS screens and HUD

- Checks: UX-005 to UX-008, SHOT-01 to SHOT-24.
- Screenshot rows: SHOT-01, SHOT-02, SHOT-22, SHOT-23, SHOT-24.

### DoD: Generated Web Audio API sound and music

- Checks: INTEG-001 to INTEG-005.
- Screenshot rows: none required, audio is non-visual.

### DoD: Title screen and end screens

- Checks: UX-006, UX-007, SHOT-01, SHOT-22, SHOT-23, SHOT-24.
- Screenshot rows: SHOT-01, SHOT-22, SHOT-23, SHOT-24.

### DoD: Map contract validation and scripted playthrough tests

- Checks: CONTRACT-001, INTEG-013, INTEG-014, PERF-001 to PERF-003.
- Screenshot rows: SHOT-02, SHOT-20, SHOT-22.

# A. SANITY

- Check: every field a rule reads or writes is in the global context.
  - Result: closes. Section 2.2 includes player, hollow, gate, pickups, objectives, onboarding, noise, and HUD fields required by section 4 rules.

- Check: every place, thing, or kind a rule names is placed by a generator or listed in a roster.
  - Result: closes. Section 4 rosters list player start, gate, gap, threshold, Dead Well, keys A B C, embers E1 to E5, zones, and content counts. No runtime generator is used for required objects.

- Check: consumable totals placed against total rules can demand along core loop.
  - Fuel: placed supply is 50 starting plus 5 embers times 40, total 250. Maximum demand is 480 seconds times 0.5 per second, total 240. Closes with 10 fuel spare. It still bites because missing one ember leaves 210 fuel, which supports only 420 seconds of continuous light.
  - Breath: sprint drain is 20 per second, full breath supports 5 seconds of sprint. Walking recovery is 15 per second, standing recovery is 30 per second, unlock threshold is 25. Standing from 0 reaches unlock in about 0.83 seconds. Closes and bites.

- Check: timing pairs close and still bite.
  - Hollow wake versus clear: minimum expected route is 550 tiles. Even theoretical full sprint at 6.0 tiles per second takes about 91.7 seconds, before gate hold, underbrush, breath, and navigation. Hollow wakes at 90 seconds. Closes and bites.
  - Fuel drain versus supply: drain demand is 240 fuel, supply is 250 fuel. Closes with 20 seconds of light spare. Bites if an ember is missed or light is used carelessly.
  - Sprint drain versus recovery: sprint drains 20 per second, walking recovers 15 per second, standing recovers 30 per second. Closes for escape pressure and bites because breath can lock.
  - Hollow hunt speed versus player sprint: Hollow hunts at 5.0, player sprints at 6.0, underbrush Hollow is 4.25, player sprint in underbrush is 5.1. Closes for escape and bites because breath limits sprint.
  - Gate hold versus decay: hold time is 2 seconds, decay is 4 per second. Closes for a 2-second hold and bites if the player releases early.
  - Path recalculation versus movement: recalculation is every 0.5 seconds, Hollow hunting speed is 5.0, so worst-case reaction step is about 2.5 tiles. Closes and bites enough to feel physical without cheating.
  - Dawn clock versus expected clear: dawn is 480 seconds, expected efficient completion is 330 to 390 seconds, cautious completion is 390 to 450 seconds. Closes and bites.

- Check: every call section 9 makes is in section 8.
  - Result: closes. Section 9 uses `createSim`, `createMockAudio`, `createMockInput`, `createMapFixture`, `loadRealMap`, `advanceSim`, `validateMap`, `renderSimFrame`, `sim.debug.*`, and `input.*`, all defined in section 8.

- Check: no placeholder in angle brackets remains.
  - Result: closes. No placeholder angle brackets remain in this document.

- Fixes applied above:
  - Moved HUD and screens to HTML and CSS DOM overlays.
  - Replaced external audio files with Web Audio API generated recipes.
  - Replaced sprite file loading with procedural canvas drawing from visual recipes.
  - Corrected safe-zone visual table so safe zone is active only at fuel 25 or higher.
  - Clarified gate threshold as y below 6 with passable gap rows 3, 4, 5.