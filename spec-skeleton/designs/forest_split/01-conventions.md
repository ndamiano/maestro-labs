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
