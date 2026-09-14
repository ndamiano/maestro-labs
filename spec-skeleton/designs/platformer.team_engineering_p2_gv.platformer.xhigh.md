# engineering.md

## 1. Document Purpose and Authority

This file is the engineering design for **Signal Courier**.

It defines:

- The required repository layout.
- The runtime architecture.
- The data contracts that make the gameplay designer’s levels function.
- The implementation of the visual designer’s presentation requirements.
- A deterministic test harness.
- The tests that prove the game is complete and playable.

Authority:

| Concern | Authority |
|---|---|
| Mechanics, numbers, states, rules | `gameplay.md` |
| Art, UI, VFX, audio identity, presentation UX | `visual.md` |
| File layout, implementation architecture, data contracts, tests | This document |

If this document resolves an ambiguity from `gameplay.md` or `visual.md`, the resolution must be implemented as written here.

Important principle:

> The simulation must be deterministic, testable, and independent of the DOM wherever possible. Rendering, audio, and input are adapters around the simulation.

---

## 2. Scope and Cuts

This game is built with:

- HTML
- CSS
- Vanilla JavaScript ES modules
- Canvas 2D for world rendering
- DOM overlay for UI/HUD
- Node.js built-in test runner for validation
- No external runtime libraries
- No build step

Cut because unnecessary:

- No framework.
- No ECS library.
- No build pipeline.
- No physics engine.
- No procedural generation of production levels.
- No render interpolation.
- No object pooling beyond simple array expiration.
- No minimap.
- No score.
- No touch controls.
- No accessibility layer beyond basic keyboard focus where DOM UI exists.

Rationale:

The game is small enough that a clear module system and fixed timestep are enough. Adding frameworks or ECS would increase integration risk without improving maintainability for a 10-stage game.

Production stages are **data-driven**, not procedurally generated, because the gameplay designer has already designed the 10 stages. Procedural generation would make fairness and tests harder.

---

## 3. Repository Layout

The following files and directories must exist.

```text
/
  index.html
  css/
    styles.css
  package.json
  assets/
    manifest.json
    audio/
      /* audio files provided by visual/audio design */
    sprites/
      /* sprite sheets provided by visual design */
  js/
    main.js
    config.js
    constants.js

    utils/
      math.js
      rng.js
      eventbus.js

    core/
      Game.js
      FixedTimestep.js
      StateMachine.js
      Input.js
      Audio.js
      Assets.js
      Renderer.js
      Camera.js
      SpriteSheet.js
      Animator.js
      VFX.js
      Save.js

    sim/
      Physics.js
      Tilemap.js
      Player.js
      Weapon.js
      Projectile.js
      Beam.js
      TempSpike.js
      Enemy.js
      Stage.js
      StageFactory.js
      StageValidator.js
      Progression.js

    sim/enemies/
      index.js
      MiteCrawler.js
      DredgeDrone.js
      PincerBot.js
      WardenSentry.js
      MistWraith.js
      BoltGolem.js

    sim/bosses/
      HushWarden.js
      NullRelay.js

    states/
      TitleState.js
      IntroState.js
      MapState.js
      StageState.js
      PauseState.js
      SummaryState.js
      GameOverState.js
      EndState.js

    hud/
      HUD.js

    stages/
      index.js
      w1s1.js
      w1s2.js
      w1s3.js
      w1s4.js
      w1s5.js
      w2s1.js
      w2s2.js
      w2s3.js
      w2s4.js
      w2s5.js

  test/
    harness/
      headless.js
      inputProxy.js
      memorySave.js
      completionBot.js
      asserts.js

    fixtures/
      minimalStage.js
      weaponTestStage.js
      bossTestStage.js
      verticalTestStage.js

    unit/
      math.test.js
      rng.test.js
      save.test.js
      input.test.js
      physics.test.js
      tilemap.test.js
      player.test.js
      weapon.test.js
      projectile.test.js
      enemy.test.js
      boss.test.js
      progression.test.js

    integration/
      stateFlow.test.js
      stageLoad.test.js
      checkpointDeath.test.js
      pit.test.js
      pause.test.js
      weaponProgression.test.js
      coreProgression.test.js
      bossDefeat.test.js

    e2e/
      allStagesSmoke.test.js
      stageCompletionProof.test.js
      fullGame.test.js
      allCores.test.js

  README.md
```

`package.json` must include:

```json
{
  "name": "signal-courier",
  "private": true,
  "type": "module",
  "scripts": {
    "test": "node --test test",
    "start": "npx serve ."
  }
}
```

Rationale:

- ES modules let the same simulation run in browser and Node.
- `node --test` requires no dependencies.
- Stage files are separate so stage authors can work independently.
- Test files are grouped by abstraction level.

---

## 4. Runtime Architecture

### 4.1 Boot Flow

`index.html` loads:

```html
<canvas id="game-canvas" width="960" height="540"></canvas>
<div id="game-ui"></div>
<script type="module" src="/js/main.js"></script>
```

`js/main.js` must:

1. Create the `Game`.
2. Load assets using `assets/manifest.json`.
3. Create input, audio, save, renderer, and state machine.
4. Start the fixed-timestep loop.
5. Enter `Title` state.

The browser loop:

```js
let last = performance.now();
let accumulator = 0;

function frame(now) {
  let delta = (now - last) / 1000;
  last = now;

  if (delta > 0.1) delta = 0.1;

  accumulator += delta;

  while (accumulator >= STEP) {
    game.update(STEP);
    accumulator -= STEP;
  }

  game.render(accumulator / STEP);
  requestAnimationFrame(frame);
}
```

Where:

```js
const STEP = 1 / 60;
```

Rationale:

Fixed timestep ensures deterministic movement, damage, cooldowns, and tests.

---

### 4.2 Game Object

`Game` owns:

```js
game = {
  state: null,
  stage: null,
  input: Input,
  audio: Audio,
  save: Save,
  renderer: Renderer,
  progression: Progression,
  simTime: 0,
  stageTimeMs: 0,
  stageDeaths: 0,
  runStats: {
    timeMs: 0,
    deaths: 0
  }
}
```

`Game.update(dt)` calls:

```js
this.simTime += dt;
this.state.update(dt);
```

`Game.render(alpha)` calls:

```js
this.state.render(alpha);
```

No interpolation is required because the target update rate is 60 Hz and the logical viewport is fixed.

Rationale:

Interpolation would improve high-refresh-rate smoothness slightly, but it adds state complexity. The game targets 60 updates per second and the visual designer did not require frame-interpolated rendering.

---

### 4.3 State Machine

States:

| State | File | Notes |
|---|---|---|
| `title` | `TitleState.js` | Uses save progression |
| `intro` | `IntroState.js` | Four story cards |
| `map` | `MapState.js` | World/stage select |
| `stage` | `StageState.js` | Main gameplay |
| `pause` | `PauseState.js` | Overlay over stage |
| `summary` | `SummaryState.js` | Non-final stage complete |
| `gameOver` | `GameOverState.js` | Lives exhausted |
| `end` | `EndState.js` | Final complete |

State interface:

```js
enter(game, payload)
update(game, dt)
render(game, alpha)
onInput(game, input, dt)
```

`PauseState` must not destroy `game.stage`.

When pausing:

- Simulation updates stop.
- Audio ducks or stops.
- VFX stop.
- HUD pause panel shows.

When resuming:

- Simulation continues.
- Audio fades in 0.2 seconds.

Rationale:

Pause must preserve exact stage state.

---

## 5. Constants

`js/constants.js` must contain all gameplay numbers.

Required key values:

```js
export const TILE = 32;
export const VIEWPORT_W = 960;
export const VIEWPORT_H = 540;
export const STEP = 1 / 60;

export const PLAYER = {
  standingWidth: 16,
  standingHeight: 24,
  crouchWidth: 16,
  crouchHeight: 12,
  maxSpeed: 240,
  crouchSpeed: 120,
  groundAccel: 2800,
  airAccel: 1900,
  groundFriction: 2800,
  airFriction: 400,
  gravity: 1800,
  maxFall: 1100,
  jumpVel: -640,
  jumpCutVel: -320,
  coyoteTime: 0.09,
  jumpBuffer: 0.10,
  hearts: 5,
  livesPerStage: 3,
  invulnTime: 1.0,
  knockbackX: 280,
  knockbackY: -240,
  pitDistance: 64
};
```

Weapon constants must match `gameplay.md` exactly.

Enemy constants must match `gameplay.md` exactly.

World 2 modifier constants:

```js
export const WORLD2 = {
  enemyHpMultiplier: 1.15,
  enemyProjectileSpeedMultiplier: 1.1
};
```

Bosses do not receive World 2 standard-enemy modifiers.

Rationale:

Centralizing constants prevents drift between tests and gameplay code.

---

## 6. Input System

`js/core/Input.js` handles:

- Keyboard state.
- Mouse position.
- Mouse buttons.
- Edge-triggered actions.
- Keyboard fallback shooting.

Input mapping:

| Action | Primary | Alternate |
|---|---:|---:|
| Left | `KeyA` | `ArrowLeft` |
| Right | `KeyD` | `ArrowRight` |
| Jump | `KeyW` | `ArrowUp`, `Space` |
| Crouch | `KeyS` | `ArrowDown` |
| Shoot | `Mouse0` | `KeyJ` |
| Weapon 1 | `Digit1` | — |
| Weapon 2 | `Digit2` | — |
| Weapon 3 | `Digit3` | — |
| Weapon 4 | `Digit4` | — |
| Cycle forward | `KeyE` | `KeyQ` |
| Pause | `Escape` | `KeyP` |

Input model:

```js
input = {
  left: false,
  right: false,
  jumpHeld: false,
  jumpPressed: false,
  crouchHeld: false,
  shootHeld: false,
  mouse: {
    screenX: 480,
    screenY: 270,
    worldX: 0,
    worldY: 0,
    inside: true
  },
  weaponSelect: null,
  cycleDirection: 0,
  pausePressed: false
}
```

Mouse handling:

- `mousemove` updates screen position.
- `mousedown` sets `shootHeld` only if mouse is inside the window.
- `mouseleave` sets `mouse.inside = false` and stops mouse shooting.
- Aim remains at last known mouse position.
- If `KeyJ` is held, shooting continues even if mouse leaves.
- If no mouse movement has occurred and only `KeyJ` is used, keyboard fallback is active.

Keyboard fallback:

- Aim vector is facing direction.
- Facing is set by last horizontal input.
- If no horizontal input has occurred, face right.

Rationale:

The game requires mouse aim as primary, but `J` fallback keeps the game playable on keyboard-only sessions and is required by `gameplay.md`.

---

## 7. Save System

`js/core/Save.js` uses `localStorage` if available.

Storage key:

```text
signal-courier-progress-v1
```

If storage is unavailable, use an in-memory session save.

Save schema:

```js
{
  version: 1,
  completed: ["w1s1", "w1s2"],
  unlocked: ["w1s1", "w1s2", "w1s3"],
  weapons: ["chirp"],
  cores: {
    "w1s1-core-1": true
  },
  stats: {
    timeMs: 0,
    deaths: 0
  }
}
```

Stage order:

```js
[
  "w1s1",
  "w1s2",
  "w1s3",
  "w1s4",
  "w1s5",
  "w2s1",
  "w2s2",
  "w2s3",
  "w2s4",
  "w2s5"
]
```

Rules:

- New Signal:
  - `completed = []`
  - `unlocked = ["w1s1"]`
  - `weapons = ["chirp"]`
  - `cores = {}`
  - `stats = { timeMs: 0, deaths: 0 }`

- Completing a stage:
  - Marks it completed.
  - Unlocks next stage in order.
  - Completing `w1s5` unlocks World 2.
  - Completing `w2s5` completes the game.

- Continue:
  - Returns the first stage in order that is unlocked and not completed.
  - If none exists, returns `null`, and Title goes to Signal Map.

Stats:

- `stageTimeMs` resets at stage start.
- `stageDeaths` resets at stage start.
- On death:
  - `stageDeaths += 1`
  - `stats.deaths += 1`
- On stage completion:
  - `stats.timeMs += stageTimeMs`

Rationale:

Stage-level lives reset every stage, but global stats persist for the End screen.

---

## 8. Stage Data Contract

Production stages are JavaScript module objects.

Each file in `js/stages/` exports one stage spec.

Example:

```js
export default {
  id: "w1s1",
  world: 1,
  index: 1,
  name: "First Current",
  width: 75,
  height: 12,
  boss: false,

  spawn: { x: 96, y: 320 },

  tiles: [
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "................................................",
    "####################################################"
  ],

  lowClearance: [
    { x: 960, y: 352, w: 384, h: 12 }
  ],

  wind: [],
  platforms: [],

  enemies: [
    { type: "mite", x: 800, y: 352 },
    { type: "drone", x: 1920, y: 224 }
  ],

  checkpoints: [
    { x: 1280, y: 320 }
  ],

  cores: [
    { id: "w1s1-core-1", x: 320, y: 320 },
    { id: "w1s1-core-2", x: 1280, y: 320 },
    { id: "w1s1-core-3", x: 1664, y: 224 }
  ],

  hearts: [
    { x: 2080, y: 320 }
  ],

  tuners: [],

  conduit: { x: 2240, y: 256 },

  validationRoute: [
    { x: 96, y: 336 },
    { x: 1664, y: 336, crouch: true },
    { x: 2240, y: 336 }
  ]
};
```

### 8.1 Stage ID and Label

Stage IDs:

```text
w1s1 ... w1s5
w2s1 ... w2s5
```

HUD label:

```text
W{world} · N{index}
```

Example:

```text
W2 · N3
```

---

### 8.2 Tile Map

`tiles` is an array of strings.

Row count must equal `height`.

Every row must be `width` characters long.

Tile characters:

| Char | Meaning |
|---|---|
| `.` | Empty |
| `#` | Solid tile, 32 x 32 |
| `=` | One-way platform, 32 x 8 at top of tile |
| `^` | Up-facing spike, 32 x 16 damage volume |
| `v` | Down-facing spike, 32 x 16 damage volume |
| `>` | Right conveyor solid tile |
| `<` | Left conveyor solid tile |

Solid tiles:

- Block player.
- Block non-flying enemies.
- Block projectiles.
- Are full 32 x 32 collision.

One-way platforms:

- Block player only from below.
- Projectiles pass through.
- Visual top edge is 2 px cyan.
- Collision top is the top of the tile.

Spikes:

- Non-solid damage volumes.
- Up spikes occupy lower 16 px of the tile.
- Down spikes occupy upper 16 px of the tile.
- Contact deals 1 heart.

Conveyors:

- Solid tiles.
- Add horizontal offset while player is grounded.
- Right conveyor: `+120 px/s`
- Left conveyor: `-120 px/s`
- Total horizontal speed while on conveyor clamped to `±360 px/s`.

---

### 8.3 Low Clearance Volumes

`lowClearance` is required because tile resolution is 32 px, but the standing player hitbox is 24 px. A normal 32 px tile gap would still allow standing, making crouch-only passages impossible to express with full tiles.

`lowClearance` entries are pixel rectangles:

```js
{
  x: number,
  y: number,
  w: number,
  h: number
}
```

Behavior:

- Blocks player when standing.
- Does not block player when crouching.
- Does not damage the player.
- Does not block projectiles.
- Does not block enemies.
- Does not block beams.

Collision rule:

- If player hitbox is 16 x 24 and intersects a `lowClearance` rectangle, resolve as solid.
- If player hitbox is 16 x 12 and does not intersect, pass through.

Stage validator must ensure:

- No low clearance blocks spawn.
- No low clearance blocks checkpoints.
- No low clearance blocks conduit.
- The validation route can pass through low-clearance sections while crouching.

Rationale:

This is the minimum addition needed to make crouch a required traversal tool without changing tile collision or adding a new gameplay system.

---

### 8.4 Wind Zones

`wind` entries:

```js
{
  x: number,
  y: number,
  w: number,
  h: number,
  type: "updraft" | "gustRight" | "gustLeft"
}
```

Rules:

- Wind applies while player hitbox intersects zone.
- Updraft:
  - Vertical acceleration: `-2400 px/s²`
  - Vertical speed minimum: `-420 px/s`
  - Fall speed still clamped to `1100 px/s`
- Gust right:
  - Horizontal acceleration: `+1600 px/s²`
  - Horizontal speed maximum: `+360 px/s`
- Gust left:
  - Horizontal acceleration: `-1600 px/s²`
  - Horizontal speed minimum: `-360 px/s`
- Wind does not affect enemies unless an enemy definition explicitly says otherwise.
- Multiple overlapping wind zones sum accelerations before clamping.

Rationale:

Wind is a movement force, not damage. It must be applied before integration for responsive vertical climbs and horizontal pushes.

---

### 8.5 Moving Platforms

`platforms` entries:

```js
{
  id: "p1",
  x: number,
  y: number,
  w: 64,
  h: 16,
  speed: number,
  waypoints: [
    { x: number, y: number },
    { x: number, y: number }
  ],
  pingPong: true
}
```

Waypoints are platform top-left positions in pixels.

Rules:

- Platforms move linearly between waypoints.
- Default `pingPong: true`.
- If `pingPong: false`, path loops.
- Platforms are dynamic one-way floors for the player.
- Projectiles pass through moving platforms.
- Enemies do not ride moving platforms.
- If player is standing on platform, player position is carried by platform delta.
- If player jumps off, player is no longer carried.
- Platform reset happens on stage reset.

Carry algorithm:

1. Update all platforms and store `deltaX`, `deltaY`.
2. If player is riding platform `p`, add `p.deltaX` and `p.deltaY` to player position.
3. Run player input, gravity, and collision.
4. If player lands on platform, set `ridingPlatform = p`.
5. If player leaves platform, set `ridingPlatform = null`.

Rationale:

Position carry is simpler and deterministic than velocity carry for linear platforms.

---

### 8.6 Stage Objects

All positions are pixels, top-left.

Spawn:

```js
spawn: { x, y }
```

Player top-left on stage load.

Checkpoint:

```js
{ x, y }
```

Checkpoint size: 32 x 48.

Respawn player position:

```js
x = checkpoint.x + 8
y = checkpoint.y + 24
```

Core:

```js
{ id, x, y }
```

Core size: 24 x 24.

Core IDs must be global:

```text
{stageId}-core-1
{stageId}-core-2
{stageId}-core-3
```

Signal Heart:

```js
{ x, y }
```

Size: 24 x 24.

Tuner Shard:

```js
{ weapon: "sifter" | "lance" | "bloom", x, y }
```

Size: 32 x 48.

Conduit:

```js
{ x, y }
```

Size: 64 x 96.

---

### 8.7 Boss Stage Spec

Boss stages include:

```js
boss: {
  type: "hushWarden" | "nullRelay",
  x: number,
  y: number,
  arena: {
    x: number,
    y: number,
    w: number,
    h: number
  },
  trigger?: {
    x: number,
    y: number,
    w: number,
    h: number
  }
}
```

If `trigger` is omitted, boss activates when player enters the arena rectangle.

Boss stages:

- Conduit inactive until boss dies.
- HUD edge objective arrow points to boss until boss dies.
- After boss dies, arrow points to conduit.

---

### 8.8 Validation Route

Every production stage must include a `validationRoute`.

This is test-only data. It is not shown to the player.

Waypoint format:

```js
{
  x: number,
  y: number,
  crouch?: boolean,
  jump?: boolean,
  holdJump?: boolean,
  faceLeft?: boolean,
  waitMs?: number,
  shoot?: boolean
}
```

Waypoints represent the intended path through the stage.

Rules:

- Route must start at spawn.
- Route must end at conduit.
- If a section requires crouch, waypoints in that section must set `crouch: true`.
- If a gap requires jumping, the waypoint before the gap may set `jump: true`.
- If an updraft requires holding jump, set `holdJump: true`.
- For boss stages, route must include boss arena and conduit.
- For core collection tests, stages may include `coreRoutes`:

```js
coreRoutes: [
  {
    coreId: "w1s1-core-1",
    route: [ ... ]
  }
]
```

Rationale:

A route-based proof is deterministic and does not require a general-purpose platformer AI. It validates that the designed level is physically passable with the intended actions.

---

## 9. Stage Factory

`js/sim/StageFactory.js` converts stage spec into runtime stage.

`createStage(spec, progression)` returns:

```js
{
  id,
  world,
  index,
  name,
  widthPx,
  heightPx,
  tilemap,
  player: Player,
  enemies: Enemy[],
  boss: Boss | null,
  projectiles: Projectile[],
  enemyProjectiles: Projectile[],
  beams: Beam[],
  tempSpikes: TempSpike[],
  platforms: Platform[],
  windZones: Rect[],
  checkpoints: Checkpoint[],
  cores: Core[],
  hearts: Heart[],
  tuners: Tuner[],
  conduit: Conduit,
  respawnPoint: { x, y },
  checkpointActivated: false
}
```

Stage factory must:

1. Parse tile strings.
2. Build tilemap arrays.
3. Create player at spawn.
4. Create enemies with world modifiers.
5. Create boss if present.
6. Create pickups, skipping globally collected cores and tuners.
7. Create moving platforms.
8. Validate stage in test/dev mode.

---

### 9.1 Stage Reset

`stage.resetDynamic()` resets:

- Player position.
- Player hearts.
- Player lives.
- Player velocity.
- Player invulnerability.
- Player active weapon.
- Enemy positions and states.
- Enemy projectiles.
- Player projectiles.
- Beams.
- Temporary spikes.
- Moving platforms.
- Wind zones.
- Boss HP/state if present.
- Checkpoint activated flags.
- Stage-local hearts.

It does not reset:

- Globally collected cores.
- Globally unlocked weapons.
- Globally collected tuners.
- Global progression stats.

Death respawn rule:

When the player dies with lives remaining:

1. Decrement lives.
2. Restore hearts to 5.
3. Reset dynamic stage state.
4. Teleport player to last checkpoint or stage start.
5. Enter invulnerability 1.0 seconds.

Rationale:

A checkpoint respawn that leaves enemies and projectiles in arbitrary states can create impossible or unfair situations. Full dynamic reset makes the checkpoint a predictable safe state while preserving global progression.

---

## 10. Stage Validator

`js/sim/StageValidator.js` validates stage specs.

It must run in tests and in development builds.

Validation errors are fatal in tests.

Required checks:

### 10.1 Structure

- `id` matches filename.
- `width` and `height` match tile rows.
- Every tile row length equals `width`.
- Tile characters are valid.
- Spawn is inside stage.
- Spawn is not inside solid tile.
- Spawn has at least 24 px vertical clearance for standing player.
- Conduit is inside stage.
- Conduit does not overlap solid tiles.
- Conduit has clear 64 x 96 area.
- Checkpoints are inside stage.
- Checkpoints do not overlap solid tiles.
- Player respawn box from checkpoint is not inside solid tile.

### 10.2 Required Content

Every stage must have:

- 1 spawn.
- 1 conduit.
- At least 1 checkpoint.
- Exactly 3 cores.
- Exactly 1 Signal Heart.

Tuner rules:

- `w1s2` must have exactly one tuner for `sifter`.
- `w1s4` must have exactly one tuner for `lance`.
- `w2s2` must have exactly one tuner for `bloom`.
- No other stage may have a tuner.

### 10.3 Enemy Counts

Tests must verify the following enemy counts from `gameplay.md`:

| Stage | Expected enemies |
|---|---|
| w1s1 | mite 3, drone 1 |
| w1s2 | drone 3, mite 4, pincer 1 |
| w1s3 | sentry 2, pincer 3, drone 2 |
| w1s4 | drone 4, pincer 4, mite 4 |
| w1s5 | sentry 1, mite 2, boss hushWarden |
| w2s1 | drone 3, wraith 2, pincer 2 |
| w2s2 | sentry 3, wraith 4, mite 4 |
| w2s3 | sentry 3, wraith 4, golem 2 |
| w2s4 | sentry 4, golem 2, wraith 6 |
| w2s5 | wraith 2, golem 1, boss nullRelay |

Boss stages also include the boss.

### 10.4 Object Placement

- Cores are not inside solid tiles.
- Cores do not overlap conduit.
- Cores do not overlap checkpoints.
- Cores do not overlap tuners.
- Signal hearts are not inside solid tiles.
- Tuners are not inside solid tiles.
- Enemy spawn positions are valid for their type.
- Ground enemies have floor below.
- Flying enemies are not inside solid tiles.
- Bosses are inside stage.
- Boss arenas are inside stage.
- Boss arenas do not overlap solid tiles except intended floor/ledges.

### 10.5 Low Clearance

- Low-clearance rectangles are inside stage.
- Low clearance does not overlap spawn.
- Low clearance does not overlap checkpoints.
- Low clearance does not overlap conduit.
- A crouching player box can pass through low-clearance sections used by validation route.

### 10.6 Route Proof

- `validationRoute` exists.
- Route starts at spawn.
- Route ends at conduit.
- Route waypoints are inside stage.
- Running the completion bot with hazards disabled and enemies disabled reaches conduit.
- If the route includes `crouch: true`, the stage must have a low-clearance or other geometry requiring crouch.

Rationale:

The validator proves that each designed stage is structurally valid before gameplay systems are tested.

---

## 11. Physics and Player

### 11.1 Player State

Player uses top-left hitbox coordinates.

```js
player = {
  x,
  y,
  vx,
  vy,
  w: 16,
  h: 24,
  crouching: false,
  grounded: false,
  coyoteTimer: 0,
  jumpBuffer: 0,
  invulnTimer: 0,
  hearts: 5,
  lives: 3,
  facing: 1,
  ridingPlatform: null,
  weapons: {
    active: "chirp",
    unlocked: ["chirp"],
    switchCooldown: 0,
    fireCooldown: {}
  }
}
```

Feet position:

```js
feetY = player.y + player.h
```

Crouch state:

- If crouch input is held, `crouching = true`.
- If crouch is released, player attempts to stand.
- Standing requires 24 px vertical clearance.
- If standing is blocked, player remains crouched.
- Crouching is allowed in air.
- Crouching reduces height to 12 px.
- Crouching reduces max horizontal speed to 120 px/s.

When changing height:

```js
const feetY = player.y + player.h;
player.h = crouching ? 12 : 24;
player.y = feetY - player.h;
```

Then run vertical collision to resolve head/bottom overlap.

---

### 11.2 Horizontal Movement

Each update:

1. `moveX = (right ? 1 : 0) - (left ? 1 : 0)`.
2. `maxSpeed = crouching ? 120 : 240`.
3. `targetVX = maxSpeed * moveX`.
4. If `moveX === 0`, apply friction.
5. If `moveX !== 0`, apply acceleration.

Friction:

- Ground: `2800 px/s²`
- Air: `400 px/s²`

Acceleration:

- Ground: `2800 px/s²`
- Air: `1900 px/s²`

Input-derived speed is clamped to `maxSpeed`.

Wind and conveyor can push total speed beyond input speed up to `±360 px/s`.

---

### 11.3 Vertical Movement

Gravity:

```js
if in updraft:
  vy += -2400 * dt
  vy = clamp(vy, -420, 1100)
else:
  vy += 1800 * dt
  vy = clamp(vy, -Infinity, 1100)
```

Jump:

- Jump press sets `jumpBuffer = 0.10`.
- If grounded, `coyoteTimer = 0.09`.
- If not grounded, `coyoteTimer -= dt`.
- If `jumpBuffer > 0` and `(grounded || coyoteTimer > 0)`:
  - `vy = -640`
  - `grounded = false`
  - `coyoteTimer = 0`
  - `jumpBuffer = 0`
- If jump released while `vy < -320`:
  - `vy = -320`

No double jump.

Rationale:

Coyote time and jump buffer are required by gameplay.

---

### 11.4 Muzzle Origin

The gameplay document gives a center-relative formula that becomes ambiguous with crouch height. Engineering resolves it by anchoring to a standing-height reference.

Define:

```js
feetY = player.y + player.h
baseY = feetY - 12
centerX = player.x + player.w / 2
```

Muzzle Y:

```js
muzzleY = baseY + (crouching ? 8 : 2)
```

Result:

- Standing muzzle: 10 px above feet.
- Crouched muzzle: 4 px above feet.

Muzzle X:

If aim is mostly horizontal:

```js
muzzleX = centerX + 14 * sign
```

If aim is mostly vertical:

```js
muzzleX = centerX
```

Where:

```js
mostlyHorizontal = Math.abs(aimX) >= Math.abs(aimY)
sign = aimX !== 0 ? Math.sign(aimX) : player.facing
```

Rationale:

This preserves the gameplay intent that crouching lowers the muzzle while keeping the origin inside the player’s body.

---

### 11.5 Collision Order

Player update order:

1. Read input.
2. Update facing.
3. Update weapon selection and cooldowns.
4. Update platform carry.
5. Apply horizontal acceleration/friction.
6. Apply wind acceleration.
7. Apply conveyor offset if grounded.
8. Apply gravity or updraft.
9. Handle jump.
10. Integrate X and resolve horizontal collision.
11. Integrate Y and resolve vertical collision.
12. Update grounded state.
13. Update coyote and jump buffer.
14. Check pit.
15. Check hazards.
16. Check triggers/pickups.
17. Update camera.

Rationale:

Applying wind before integration avoids one-frame delay and matches the intended responsiveness of vertical climbs.

---

### 11.6 Solid Tile Collision

Use AABB tile collision.

Horizontal pass:

1. Move player X.
2. For each overlapping solid tile or standing-blocking low clearance:
   - Push player out horizontally.
   - Set `vx = 0`.

Vertical pass:

1. Store previous bottom.
2. Move player Y.
3. If moving down:
   - Check solid tiles.
   - Check one-way platforms.
   - Check moving platforms.
   - If landed, set `vy = 0`, `grounded = true`.
4. If moving up:
   - Check solid tiles.
   - Check low clearance if standing.
   - If hit ceiling, set `vy = 0`.

One-way landing condition:

```js
vy >= 0
previousBottom <= platformTop + EPS
playerBottom >= platformTop
horizontal overlap
```

`EPS = 0.01`

Projectiles ignore one-way platforms.

Rationale:

This is the standard deterministic platformer collision model.

---

### 11.7 Conveyor Collision

If player lands on conveyor tile:

- Set `grounded = true`.
- Store conveyor offset.

Conveyor offset:

```js
if grounded on right conveyor:
  vx += 120
if grounded on left conveyor:
  vx -= 120
vx = clamp(vx, -360, 360)
```

Conveyor offset is applied every frame while grounded on conveyor.

---

### 11.8 Wind Collision

Each frame, find wind zones intersecting player.

For each zone:

```js
if type === "updraft":
  vy += -2400 * dt

if type === "gustRight":
  vx += 1600 * dt

if type === "gustLeft":
  vx += -1600 * dt
```

After all wind:

```js
if any updraft:
  vy = clamp(vy, -420, 1100)
else:
  vy = clamp(vy, -Infinity, 1100)

if any horizontal wind:
  vx = clamp(vx, -360, 360)
```

Rationale:

Clamps are applied after acceleration to keep movement stable.

---

### 11.9 Pit Rule

If:

```js
player.y > stage.heightPx + 64
```

then:

1. If `player.hearts > 1`:
   - `player.hearts -= 1`
   - Teleport to last checkpoint or stage start.
   - `player.invulnTimer = 0.5`
2. If `player.hearts == 1`:
   - `player.hearts = 0`
   - Trigger normal death.

Death from pit uses normal death rules.

Rationale:

A pit with 1 heart should cause death, not a harmless checkpoint respawn.

---

### 11.10 Damage Pipeline

`player.takeDamage(sourceX, sourceY)`:

If:

- Player is dead.
- `player.invulnTimer > 0`.

then ignore.

Otherwise:

1. `player.hearts -= 1`.
2. If `player.hearts > 0`:
   - `player.invulnTimer = 1.0`
   - Apply knockback:
     - `vx += 280 * sign(player.centerX - sourceX)`
     - `vy = -240`
3. If `player.hearts == 0`:
   - Trigger death.

Death:

1. If `player.lives > 0`:
   - `player.lives -= 1`
   - `stageDeaths += 1`
   - `runStats.deaths += 1`
   - Reset dynamic stage.
   - Respawn at checkpoint or start.
   - `player.hearts = 5`
   - `player.invulnTimer = 1.0`
2. If `player.lives == 0`:
   - Enter Game Over state.

Rationale:

This matches gameplay damage, knockback, lives, and death rules.

---

### 11.11 Checkpoints

Checkpoint trigger:

- Triggers once per stage dynamic reset.
- On trigger:
  - Set respawn point.
  - If `player.hearts < 5`, restore 1 heart.
  - Show `CHECKPOINT` notification.
  - Play checkpoint audio.
  - Activate visual state.

If player dies with no checkpoint activated:

- Respawn at stage start.

---

## 12. Camera

Camera uses top-left viewport coordinates.

```js
camera = {
  x: 0,
  y: 0
}
```

Target:

```js
playerCenterX = player.x + player.w / 2
playerCenterY = player.y + player.h / 2

lookahead = 0
if input.right:
  lookahead = 120
if input.left:
  lookahead = -120

targetX = playerCenterX - VIEWPORT_W / 2 + lookahead
targetY = playerCenterY - 32 - VIEWPORT_H / 2
```

Clamp:

```js
if stage.widthPx > VIEWPORT_W:
  camera.x = clamp(camera.x, 0, stage.widthPx - VIEWPORT_W)
else:
  camera.x = (stage.widthPx - VIEWPORT_W) / 2

if stage.heightPx > VIEWPORT_H:
  camera.y = clamp(camera.y, 0, stage.heightPx - VIEWPORT_H)
else:
  camera.y = (stage.heightPx - VIEWPORT_H) / 2
```

Smoothing:

```js
camera.x += (targetX - camera.x) * min(1, 8 * dt)
camera.y += (targetY - camera.y) * min(1, 8 * dt)
```

If stage is shorter than viewport, background layers fill the extra vertical space.

Rationale:

World 1 stages are 12 tiles high, which is 384 px, less than the 540 px viewport. Centering the camera and filling with background is required to avoid letterboxing while preserving the logical viewport.

---

## 13. Weapons

Weapon definitions live in `js/constants.js`.

Weapon slots:

| Slot | Weapon |
|---:|---|
| 1 | Chirp |
| 2 | Sifter |
| 3 | Lance |
| 4 | Bloom |

Weapon state:

```js
player.weapons = {
  active: "chirp",
  unlocked: ["chirp"],
  switchCooldown: 0,
  fireCooldown: {
    chirp: 0,
    sifter: 0,
    lance: 0,
    bloom: 0
  }
}
```

Weapon switching:

- Selecting unlocked weapon:
  - Changes active weapon.
  - Sets `switchCooldown = 0.12`.
- Selecting locked weapon:
  - No weapon change.
  - HUD deny animation.
  - UI deny audio.
- Cycle forward:
  - Advances through unlocked weapons only.
  - Wraps from last unlocked to first unlocked.
  - Sets `switchCooldown = 0.12`.

Firing:

Player can fire if:

- Player is alive.
- `switchCooldown <= 0`.
- `fireCooldown[active] <= 0`.
- Shoot input is held.

On fire:

1. Compute aim vector.
2. Compute muzzle origin.
3. Spawn projectile(s).
4. Set fire cooldown.
5. Play weapon audio.
6. Emit muzzle VFX event.

Aim vector:

Mouse:

```js
aim = normalize(mouseWorld - muzzleOrigin)
```

If length near zero:

```js
aim = facing direction
```

Keyboard fallback:

```js
aim = (facing, 0)
```

Crouch does not restrict aim.

---

### 13.1 Chirp

```js
{
  damage: 7,
  fireInterval: 0.15,
  speed: 950,
  lifetime: 0.7,
  radius: 4,
  count: 1,
  spread: [0],
  pierce: 0,
  knockback: 80
}
```

Behavior:

- One straight projectile.
- No pierce.

---

### 13.2 Sifter

```js
{
  damage: 4,
  fireInterval: 0.55,
  speed: 720,
  lifetime: 0.35,
  radius: 3,
  count: 5,
  spread: [-8, -4, 0, 4, 8],
  pierce: 0,
  knockback: 60
}
```

Behavior:

- Spawns 5 pellets.
- Each pellet has independent lifetime and tile collision.
- Each pellet applies its own knockback.

Angles are degrees relative to aim.

---

### 13.3 Lance

```js
{
  damage: 24,
  fireInterval: 0.62,
  speed: 1500,
  lifetime: 0.8,
  radius: 5,
  count: 1,
  spread: [0],
  pierce: 3,
  knockback: 260
}
```

Projectile state:

```js
lanceProjectile = {
  hitEnemyIds: Set()
}
```

Pierce algorithm:

On enemy hit:

1. If enemy id is in `hitEnemyIds`, do nothing.
2. Add enemy id.
3. Apply damage and knockback.
4. If `hitEnemyIds.size < 3`, continue.
5. If `hitEnemyIds.size == 3`, destroy projectile.

Lance is destroyed by solid tile collision.

Rationale:

Enemy ID set prevents infinite damage from overlapping enemies or repeated collision with the same enemy.

---

### 13.4 Bloom

```js
{
  mainDamage: 12,
  shardDamage: 6,
  fireInterval: 1.0,
  mainSpeed: 520,
  mainLifetime: 0.45,
  mainRadius: 8,
  shardSpeed: 620,
  shardLifetime: 0.5,
  shardRadius: 4,
  shardAngles: [-25, 0, 25],
  mainKnockback: 180,
  shardKnockback: 80
}
```

Main projectile behavior:

- Does not split on tile collision.
- If it hits an enemy:
  - Apply main damage.
  - Apply main knockback.
  - Destroy main projectile.
  - Spawn 3 shards at hit location.
- If it reaches lifetime without hitting enemy:
  - Destroy main projectile.
  - Spawn 3 shards at current position.

Shards:

- Do not split.
- Damage 6.
- Lifetime 0.5.
- Speed 620.
- Angles relative to main direction.

Rationale:

Bloom is an area-control weapon. The split condition is spatial and must not be allowed to occur inside solid geometry.

---

## 14. Projectiles

Projectile entity:

```js
{
  id,
  team: "player" | "enemy",
  x,
  y,
  vx,
  vy,
  radius,
  damage,
  lifetime,
  age,
  weapon?,
  knockback?,
  pierceIds?,
  isBloomMain?,
  isBloomShard?,
  bounceRemaining?
}
```

Update order:

1. Move projectile using substeps.
2. Check solid tile collision.
3. Check target collision.
4. Apply damage/behavior.
5. Remove if expired, destroyed, or killed.

Substep movement:

```js
distance = speed * dt
stepSize = 16
segments = max(1, ceil(distance / stepSize))
```

For each segment:

1. Move a fraction of projectile velocity.
2. Check tile collision.
3. If tile hit, destroy.

Target collision:

- Player projectiles check enemies and boss.
- Enemy projectiles check player.
- Projectiles do not damage owner.

Tile collision:

- Projectile circle expanded by radius against solid tile AABBs.
- One-way platforms ignored.
- Low clearance ignored.
- Moving platforms ignored.

Lifetime:

```js
age += dt
if age >= lifetime:
  remove or Bloom split if applicable
```

Entity limits:

- Maximum player projectiles: 80.
- Maximum enemy projectiles: 120.
- If limit exceeded, oldest projectile expires.

Rationale:

Substepping prevents high-speed Lance projectiles from tunneling through tiles or enemies.

---

## 15. Enemies

Enemy base:

```js
enemy = {
  id,
  type,
  world,
  x,
  y,
  w,
  h,
  hp,
  maxHp,
  vx,
  vy,
  active,
  dormant,
  grounded,
  state,
  timers,
  spawnX,
  spawnY,
  facing,
  isBoss: false
}
```

Activation:

- Activation radius: 10 tiles = 320 px.
- Inactive enemies do not act.
- Once active, remain active until death, dormant, or stage reset.
- Maximum active enemies: 16.
- If more than 16 are within radius, activate the 16 closest.
- If active count exceeds 16 due to summons:
  - Farthest active enemy beyond 320 px becomes dormant.
  - Dormant enemies stop acting.
  - They can reactivate when space is available.

World 2 modifiers:

For standard enemies only:

```js
hp = ceil(baseHp * 1.15)
projectileSpeed = baseProjectileSpeed * 1.1
```

Bosses are not modified.

Contact damage:

- All enemy contact deals 1 heart.
- If player invulnerable, no damage.
- If enemy is phased/intangible, no damage.
- Player contact damage to enemies is only through projectiles.

Enemy death:

1. Remove enemy.
2. Clear enemy-owned projectiles.
3. Play enemy death audio.
4. Emit enemy death VFX.
5. If Bolt Golem, spawn Signal Heart at its center.

Rationale:

Clearing enemy-owned projectiles on death prevents posthumous damage and keeps stage states clean.

---

### 15.1 Mite Crawler

Stats:

| Parameter | Value |
|---|---:|
| Hitbox | 16 x 16 |
| HP | 4 |
| Contact damage | 1 |
| Move speed | 90 |
| World 2 HP | 5 |

Behavior:

- Ground enemy.
- Gravity.
- If active and player within 5 tiles:
  - Move horizontally toward player.
- If blocked by solid tile:
  - Stop.
  - Wait 0.5 seconds.
  - Try again.
- Does not jump.
- Dies to 1 Chirp shot.

---

### 15.2 Dredge Drone

Stats:

| Parameter | Value |
|---|---:|
| Hitbox | 24 x 20 |
| HP | 10 |
| Contact damage | 1 |
| Move speed | 120 |
| Fire interval | 1.6 |
| Projectile speed | 350 |
| Projectile lifetime | 2.5 |
| Projectile radius | 6 |
| Attack range | 6 tiles |
| World 2 HP | 12 |
| World 2 projectile speed | 385 |

Behavior:

- Flying enemy.
- No gravity.
- Patrols horizontally within 4 tiles of spawn.
- Adds vertical sine offset of 12 px.
- If player within 6 tiles and LOS:
  - Hover.
  - Fire straight projectile toward player every 1.6 seconds.
- Collides with solid tiles.
- Ignores one-way platforms.

LOS:

- Ranged enemies require line of sight.
- Sample line every 4 px.
- Solid tiles block LOS.
- One-way platforms do not block LOS.

---

### 15.3 Pincer Bot

Stats:

| Parameter | Value |
|---|---:|
| Hitbox | 24 x 24 |
| HP | 18 |
| Contact damage | 1 |
| Walk speed | 130 |
| Charge speed | 420 |
| Charge duration | 0.35 |
| Telegraph time | 0.5 |
| Attack range | 4 tiles |
| Cooldown | 1.5 |
| World 2 HP | 21 |

States:

| State | Behavior |
|---|---|
| Idle | Wanders slowly near spawn |
| Telegraph | Stops, shakes, opens pincers |
| Charge | Dashes toward player’s current position |
| Cooldown | Cannot charge again |

Charge:

- Uses player position at charge start.
- Stops on solid collision or after 0.35 seconds.
- Contact damage applies during charge.

---

### 15.4 Warden Sentry

Stats:

| Parameter | Value |
|---|---:|
| Hitbox | 32 x 32 |
| HP | 30 |
| Contact damage | 1 |
| Aim speed | 3 rad/s |
| Burst shots | 2 |
| Burst gap | 0.15 |
| Fire cooldown | 2.6 |
| Projectile speed | 520 |
| Projectile lifetime | 1.5 |
| Projectile radius | 6 |
| Attack range | 8 tiles |
| World 2 HP | 35 |
| World 2 projectile speed | 572 |

Behavior:

- Stationary.
- If player within 8 tiles and LOS:
  - Aim at player.
  - When aim is within 10 degrees of player, fire 2-round burst.
- If no LOS:
  - Rotate to last known angle.
  - If no last known angle, face right.

Burst:

```js
shoot()
wait 0.15
shoot()
cooldown 2.6
```

---

### 15.5 Mist Wraith

Stats:

| Parameter | Value |
|---|---:|
| Hitbox | 24 x 24 |
| HP | 22 |
| Contact damage | 1 |
| Move speed | 180 |
| Phase interval | 2.5 |
| Phase duration | 0.8 |
| Sine offset | 30 |
| World 2 HP | 25 |

Behavior:

- Flying enemy.
- Moves toward player with vertical sine motion.
- Collides with solid tiles.
- Ignores one-way platforms.
- Every 2.5 seconds:
  - Phases for 0.8 seconds.
  - While phased:
    - Player projectiles pass through.
    - Enemy contact does no damage to player.
    - Enemy cannot be damaged by player.

---

### 15.6 Bolt Golem

Stats:

| Parameter | Value |
|---|---:|
| Hitbox | 48 x 48 |
| HP | 60 |
| Contact damage | 1 |
| Move speed | 60 |
| Heavy bolt interval | 3.0 |
| Heavy bolt speed | 300 |
| Heavy bolt lifetime | 3.0 |
| Heavy bolt radius | 10 |
| Attack range | 8 tiles |
| Stomp interval | 4.0 |
| Stomp range | 3 tiles |
| World 2 HP | 69 |
| World 2 heavy bolt speed | 330 |

Behavior:

- Ground enemy.
- Moves toward player if within 8 tiles.
- Does not jump.
- If player within 8 tiles and LOS:
  - Fire heavy bolt toward player every 3 seconds.
- If player within 3 tiles:
  - Telegraph 0.4 seconds.
  - Stomp.
  - Spawn 2 temporary spike patches in front for 2 seconds.
- Drops 1 Signal Heart on death.

Stomp spike patches:

- Two 32 x 16 spikes.
- Placed in front of golem on the ground.
- If space is blocked, place as many as fit.
- Duration: 2 seconds.
- Warning: 0.2 seconds before damage.

---

## 16. Temporary Spike Patches

`TempSpike` entity:

```js
{
  x,
  y,
  w,
  h,
  warnTimer,
  activeTimer,
  duration
}
```

States:

1. Warn:
   - No damage.
   - Visual warning.
2. Active:
   - Damages player on contact.
3. Removed.

Max temporary spike patches: 20.

If limit exceeded:

- Remove oldest patch.

Boss charge and golem stomp create temporary spike patches.

Rationale:

Temporary hazards need a warning state so damage is never invisible or unavoidable.

---

## 17. Beams

`Beam` entity:

```js
{
  id,
  type: "horizontal" | "vertical",
  x,
  y,
  width,
  height,
  state: "telegraph" | "active" | "done",
  telegraphTime,
  activeTime,
  timer,
  damage: 1
}
```

Horizontal beam:

```js
{
  type: "horizontal",
  y: beamY,
  x: arena.x,
  width: arena.w,
  height: 24
}
```

Vertical beam:

```js
{
  type: "vertical",
  x: beamX,
  y: arena.y,
  width: 24,
  height: arena.h
}
```

Rules:

- Telegraph state:
  - No damage.
  - Visual dashed line and edge arrows.
- Active state:
  - Damages player on overlap.
- Beam does not collide with tiles.
- Beam passes through one-way platforms.
- Beam passes through low clearance.
- Beam is removed when active time ends.

Beam target locking:

For all boss beams:

- The beam line is locked to player position at telegraph start.
- If player moves during telegraph, beam does not follow.

Rationale:

Locked telegraphs make beams fair and readable.

---

## 18. Bosses

Boss base:

```js
boss = {
  id,
  type,
  x,
  y,
  w,
  h,
  hp,
  maxHp,
  phase,
  state,
  cooldowns,
  active,
  dying,
  deathTimer,
  arena
}
```

Boss activation:

- Boss stage has a boss.
- Boss is inactive until player enters boss trigger/arena.
- Once active, remains active until death or stage reset.
- If player dies with lives remaining:
  - Boss resets to full HP.
  - Boss state resets to idle.
  - Summons are cleared.

Boss damage:

- Player projectiles can damage boss unless boss is dying.
- Contact with boss deals 1 heart.
- Boss projectiles and beams deal 1 heart.
- If player invulnerable, no damage.

Boss death:

1. Set `dying = true`.
2. Stop attacks.
3. Remove boss-owned projectiles.
4. Remove active beams.
5. Remove summoned enemies.
6. Make boss invulnerable.
7. Run death sequence.
8. Unlock conduit.

Rationale:

Removing boss attacks and projectiles during death prevents unfair damage after the boss is already defeated.

---

### 18.1 Hush Warden

Stats:

| Parameter | Value |
|---|---:|
| HP | 180 |
| Hitbox | 64 x 64 |
| Contact damage | 1 |
| Arena | 36 x 12 tiles |

Phases:

| Phase | HP range |
|---|---|
| 1 | 100% to 60% |
| 2 | 60% to 0% |

Base movement:

The gameplay document says Phase 2 increases boss move speed by 10%, but does not define a base move speed. Engineering defines:

```js
baseMoveSpeed = 80 px/s
phase2MoveSpeed = 88 px/s
```

Rationale:

A small repositioning speed makes the phase 2 modifier meaningful without creating an unfair faster charge. The charge speed remains exactly 480 px/s.

Attacks:

| Attack | Available | Cooldown |
|---|---|---:|
| Charge | Phase 1 and 2 | 6.0 |
| Fan Bolt | Phase 1 and 2 | 4.0 |
| Sweep Beam | Phase 2 only | 7.0 |
| Drone Summon | Phase 2 only | 10.0 |

Attack selection:

Among ready attacks, choose lowest remaining cooldown.

Tie priority:

```text
Charge
Fan Bolt
Sweep Beam
Drone Summon
```

#### Charge

- Telegraph: 0.6 seconds.
- Dash horizontally toward player.
- Speed: 480 px/s.
- Duration: 1.2 seconds.
- Stops on solid collision.
- Leaves 4 temporary spike patches along path.

Spike patch placement:

- Spawn at fractional distances along actual dash path:
  - 25%
  - 50%
  - 75%
  - 100%
- Each patch is 32 x 16.
- Patches snap to floor below path point.
- If no floor exists at a sample, skip that patch.
- Patch duration: 3 seconds.
- Patch warning: 0.2 seconds.

#### Fan Bolt

- Fires 3 projectiles.
- Angles relative to aim at player:
  - -20°
  - 0°
  - +20°
- Projectile speed: 380 px/s.
- Lifetime: 2.0 seconds.
- Radius: 6 px.

#### Sweep Beam

- Phase 2 only.
- Telegraph: 0.8 seconds.
- Active: 0.7 seconds.
- Beam height: player Y at telegraph start.
- Beam spans arena width.
- Beam height: 24 px.

#### Drone Summon

- Phase 2 only.
- Summons 2 Dredge Drones.
- Maximum active Dredge Drones: 3.
- Summoned drones use normal Dredge Drone behavior.
- If max reached, summon is skipped.

Death:

- 2-second death sequence.
- Conduit unlocks.

---

### 18.2 Null Relay

Stats:

| Parameter | Value |
|---|---:|
| HP | 300 |
| Hitbox | 80 x 80 |
| Contact damage | 1 |
| Arena | 40 x 15 tiles |

Phases:

| Phase | HP range |
|---|---|
| 1 | 100% to 70% |
| 2 | 70% to 35% |
| 3 | 35% to 0% |

Phase 2 and Phase 3 begin with a 1.5-second warning.

During warning:

- Boss does not attack.
- Boss is stationary or slowly moves to warning position.
- HUD shows phase warning.
- Boss warning audio plays.

---

#### Phase 1

Attacks:

| Attack | Cooldown/Interval |
|---|---:|
| Rain | 1.5 interval |
| Side Sweep | 6.0 cooldown |

Movement:

- Horizontal movement at 60 px/s.

Rain:

- Warning: 0.3 seconds.
- Spawn vertical projectiles from 3 columns.
- Columns are chosen deterministically using stage RNG.
- Projectiles move downward at 420 px/s.
- Lifetime: 2.0 seconds.
- Visual: 12 x 24 vertical shards.

Side Sweep:

- Telegraph: 0.8 seconds.
- Horizontal beam at random Y.
- Beam spans arena width.
- Beam height: 24 px.
- Active: 0.8 seconds.

---

#### Phase 2

Attacks:

| Attack | Cooldown |
|---|---:|
| Echo Shot | 4.0 |
| Wraith Summon | 12.0 |

Movement:

- Small zigzag.
- Speed: 90 px/s.

Zigzag implementation:

- Horizontal movement toward player.
- Vertical sine offset of 40 px.
- Sine period: 2.0 seconds.

Echo Shot:

- Fires 3 projectiles toward player.
- Projectile speed: 520 px/s.
- Lifetime: 2.0 seconds.
- Each projectile bounces once off arena boundary.
- Bounce is reflected velocity.
- Projectile is destroyed after one bounce or if it hits solid geometry.

Wraith Summon:

- Summons 2 Mist Wraiths.
- Maximum active Mist Wraiths: 4.
- If max reached, summon is skipped.

---

#### Phase 3

Overload cycle:

Repeat until death:

1. Horizontal beam:
   - Telegraph: 0.6 seconds.
   - Active: 0.6 seconds.
   - Beam Y locked to player Y at telegraph start.
2. Vertical beam:
   - Telegraph: 0.6 seconds.
   - Active: 0.6 seconds.
   - Beam X locked to player X at telegraph start.
3. Core Exposed:
   - Boss stationary.
   - Duration: 1.5 seconds.
   - Boss cannot attack.
   - Player damage to boss multiplied by 1.5.

Core Exposed damage:

```js
if boss.state === "coreExposed":
  boss.takeDamage(amount * 1.5)
```

Death:

- 3-second death sequence.
- Conduit unlocks.
- After conduit activation, go to End state.

---

## 19. RNG

`js/utils/rng.js` implements deterministic random number generation.

Use `mulberry32`.

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

Use RNG for:

- Boss random beam Y.
- Boss rain columns.
- Minor VFX variation if needed.

Do not use `Math.random()` in simulation.

Rationale:

Deterministic RNG allows tests to reproduce boss behavior.

---

## 20. Progression

`js/sim/Progression.js` manages:

- Stage completion.
- Stage unlocking.
- Weapon unlocking.
- Core collection.
- Stats.

API:

```js
newProgression()
loadProgression(saveData)
saveProgression()
isStageUnlocked(stageId)
isStageCompleted(stageId)
completeStage(stageId, stageStats)
unlockWeapon(weapon)
isWeaponUnlocked(weapon)
collectCore(coreId)
isCoreCollected(coreId)
getContinueStage()
reset()
```

Weapon unlock mapping:

| Weapon | Unlock source |
|---|---|
| Chirp | Start |
| Sifter | `w1s2` tuner |
| Lance | `w1s4` tuner |
| Bloom | `w2s2` tuner |

World 2 unlock:

- World 2 stages are unlocked only after `w1s5` is completed.

Final completion:

- Completing `w2s5` sets game completed.
- Signal Map remains available.

Rationale:

Progression is global and persistent, while stage lives and dynamic state reset per stage.

---

## 21. Presentation Integration

The visual designer’s document is authoritative for appearance. Engineering defines how the code makes that presentation work.

### 21.1 Asset Manifest

`assets/manifest.json` must define:

```json
{
  "sprites": [
    {
      "id": "player",
      "file": "sprites/player.png",
      "animations": {
        "idle": {
          "frames": 4,
          "fps": 12,
          "frameSize": [32, 40]
        },
        "run": {
          "frames": 6,
          "fps": 12,
          "frameSize": [32, 40]
        }
      }
    }
  ],
  "audio": {
    "music": {
      "title": {
        "file": "audio/title.ogg",
        "loop": true,
        "volume": 0.5
      }
    },
    "sfx": {
      "uiConfirm": {
        "file": "audio/ui_confirm.ogg",
        "volume": 0.8,
        "priority": 9
      }
    }
  }
}
```

`js/core/Assets.js` loads all assets before booting the game.

If assets fail to load, show a technical error in browser and fail tests if test assets are required.

Rationale:

A manifest keeps visual asset naming separate from gameplay code.

---

### 21.2 Canvas Rendering

Canvas is 960 x 540.

Render layers in this order:

| Layer | Content |
|---:|---|
| 0 | Sky/gradient |
| 1 | Far silhouette |
| 2 | Mid structures |
| 3 | Near props |
| 4 | Gameplay tiles and entities |
| 5 | VFX and telegraphs |

DOM HUD is layer 6.

Parallax:

Background layers use visual document parallax factors.

```js
offsetX = camera.x * factorX
offsetY = camera.y * factorY
```

Background layers must fill viewport even if stage is smaller than viewport.

Rationale:

Parallax is presentation only and must not affect gameplay.

---

### 21.3 Entity Rendering

Render order within gameplay layer:

1. Solid tiles.
2. One-way platforms.
3. Moving platforms.
4. Wind zones.
5. Pickups.
6. Checkpoints.
7. Conduit.
8. Enemies.
9. Boss.
10. Player.
11. Projectiles.
12. Beams and telegraphs.

VFX layer:

- Hit sparks.
- Muzzle flashes.
- Death effects.
- Core bursts.
- Beam telegraphs.
- Damage vignette.

VFX must not affect gameplay.

Rationale:

This order matches the visual layer stack and keeps player/projectiles readable.

---

### 21.4 HUD Implementation

HUD is DOM-based inside `#game-ui`.

HUD elements:

```html
<div id="hud">
  <div id="hud-left">
    <div id="hearts"></div>
    <div id="weapon-slots"></div>
  </div>

  <div id="hud-right">
    <div id="stage-label"></div>
    <div id="core-counter"></div>
    <div id="pause-icon"></div>
  </div>

  <div id="boss-hud">
    <div id="boss-name"></div>
    <div id="boss-bar"></div>
    <div id="boss-phase"></div>
  </div>

  <div id="notification"></div>
  <div id="edge-arrow"></div>
  <div id="control-hint"></div>
</div>
```

HUD updates only when values change.

Required HUD behaviors:

- Hearts:
  - 5 icons.
  - Filled/empty.
  - Lost heart pulses 0.4 seconds.
- Weapon slots:
  - 4 slots.
  - Locked greyed.
  - Active highlighted.
  - Deny shake for locked selection.
- Core counter:
  - Shows global total / 30.
  - Flashes white for 0.4 seconds on core collection.
  - No bottom-center text for cores.
- Boss HUD:
  - Visible only during boss.
  - Boss name.
  - HP bar.
  - Phase warning text.
- Notifications:
  - Bottom center.
  - Priority:
    1. Weapon unlock.
    2. Boss phase warning.
    3. Checkpoint.
    4. Generic stage message.
- Edge objective arrow:
  - Points to conduit normally.
  - Points to boss in boss stage before death.
  - Hides when objective on screen.

Stage 1-1 control hint:

- Visible for 10 seconds or until first successful jump.
- Shows:

```text
A/D move    W jump    S crouch    Mouse shoot
```

Rationale:

DOM HUD is easier to style, update, and test than canvas text, and it matches the visual designer’s UI grammar.

---

### 21.5 VFX Events

Simulation emits VFX events:

```js
game.vfx.emit("playerHurt", { x, y });
game.vfx.emit("enemyDeath", { x, y, type: "mite" });
game.vfx.emit("muzzleFlash", { x, y, weapon: "chirp" });
game.vfx.emit("beamTelegraph", { beamId });
```

`js/core/VFX.js` maintains a list of active visual effects.

VFX effects have:

- Position.
- Timer.
- Draw function.
- No gameplay effect.

Rationale:

Separating VFX from simulation ensures visuals cannot change collision or damage.

---

### 21.6 Audio Implementation

`js/core/Audio.js` implements:

- Music playback.
- SFX playback.
- Priority handling.
- Ducking.
- Pause/resume.

Audio event names must match visual document SFX table.

Required SFX event keys include:

```text
uiConfirm
uiHover
uiDeny
pauseIn
pauseOut
stageStart
playerJump
playerLand
chirpFire
sifterFire
lanceFire
bloomFire
bloomSplit
playerProjectileHit
playerHurt
playerDeath
checkpoint
coreCollected
heartCollected
tunerUnlock
enemyDeathMite
enemyDeathDrone
enemyDeathPincer
enemyDeathSentry
enemyDeathWraith
enemyDeathGolem
bossWarning
bossPhaseChange
bossDeath
conduitComplete
```

Priority:

| Priority | Event class |
|---:|---|
| 1 | Player hurt |
| 2 | Player death |
| 3 | Boss warning |
| 4 | Checkpoint |
| 5 | Tuner unlock |
| 6 | Core/heart pickup |
| 7 | Enemy death |
| 8 | Weapon fire |
| 9 | UI |

If multiple SFX trigger same frame:

- Play highest priority.
- Lower priority events may be dropped.

Music:

- Use visual document music map.
- Crossfade 0.5 seconds.
- Duck music by -6 dB during:
  - Player hurt.
  - Boss warning.
  - Stage complete.
  - Boss death.

Rationale:

Audio priority ensures critical gameplay feedback is not masked.

---

## 22. Test Harness

The test harness must run in Node without a browser.

### 22.1 Headless Game

`test/harness/headless.js` exports:

```js
createHeadlessGame(options)
```

Options:

```js
{
  state: "title",
  stageId: null,
  seed: 1,
  save: MemorySave,
  input: InputProxy,
  debug: true
}
```

Headless game:

- No canvas.
- No audio.
- No real input listeners.
- Uses injected save and input.
- Uses deterministic RNG seed.
- Allows fixed-step advancement.

API:

```js
game.advance(ms)
game.advanceUntil(predicate, timeoutMs)
game.debug.teleportPlayer(x, y)
game.debug.damageBoss(amount)
game.debug.killEnemy(type)
game.debug.activateBoss()
game.debug.setStageTimeMs(ms)
```

`game.advance(ms)`:

```js
const steps = Math.round(ms / 1000 / STEP);
for (let i = 0; i < steps; i++) {
  game.update(STEP);
}
```

Rationale:

Fixed-step advancement makes tests deterministic and independent of wall-clock time.

---

### 22.2 Input Proxy

`test/harness/inputProxy.js` simulates input.

API:

```js
input.setKeys({ left, right, crouch })
input.pressJump()
input.releaseJump()
input.holdJump(value)
input.pressShoot()
input.releaseShoot()
input.selectWeapon(slot)
input.cycleWeapons(direction)
input.setMouseWorld(x, y)
input.pressPause()
```

Edge events:

- `pressJump()` sets jump pressed for one update.
- `pressShoot()` sets shoot pressed for one update.

Rationale:

Input proxy allows tests to simulate player actions exactly.

---

### 22.3 Memory Save

`test/harness/memorySave.js` implements save interface:

```js
getItem(key)
setItem(key, value)
removeItem(key)
```

Used when `localStorage` is unavailable or in tests.

---

### 22.4 Completion Bot

`test/harness/completionBot.js` is test-only.

It controls a player through a stage using the stage’s `validationRoute`.

Bot behavior:

1. Follow current waypoint.
2. Move left/right toward waypoint X.
3. If waypoint requires crouch, hold crouch.
4. If waypoint requires jump, press jump.
5. If waypoint requires hold jump, hold jump.
6. If waypoint requires shoot, hold shoot.
7. If boss is active and no other target, shoot toward boss.
8. If a standard enemy is within 300 px, shoot toward it.
9. Continue until conduit reached or timeout.

Bot uses the same player physics and weapons as production.

Bot does not use god mode.

Rationale:

A route-following bot is simple, deterministic, and sufficient to prove that each designed stage can be completed using intended mechanics.

---

## 23. Test Plan

Tests are grouped into unit, integration, and end-to-end.

All tests must pass with:

```bash
npm test
```

---

### 23.1 Unit Tests

#### `math.test.js`

Assert:

- Clamp.
- Lerp.
- Angle difference.
- Normalize.
- Rect overlap.
- Point in rect.
- LOS sampling.

Pass criteria:

- All math helpers return expected values.

---

#### `rng.test.js`

Assert:

- Same seed produces same sequence.
- Different seed produces different sequence.
- Output range is `[0, 1)`.

---

#### `save.test.js`

Assert:

- New progression unlocks only `w1s1`.
- Completing `w1s1` unlocks `w1s2`.
- Completing `w1s5` unlocks World 2.
- Continue returns furthest unlocked uncompleted stage.
- Reset clears progress.
- Unavailable storage falls back to memory.

---

#### `input.test.js`

Assert:

- Primary and alternate keys map correctly.
- Jump edge trigger works.
- Mouse position updates.
- Mouse leave stops mouse shooting.
- `J` still shoots after mouse leave.
- Weapon select keys work.
- Cycle weapons only unlocks unlocked weapons.

---

#### `physics.test.js`

Assert:

- Ground acceleration reaches max speed.
- Air acceleration is slower.
- Friction stops player.
- Crouch max speed is 120.
- Jump sets velocity to -640.
- Coyote time allows jump after leaving ground within 0.09 seconds.
- Jump buffer allows jump before landing.
- Jump cut sets velocity to -320.
- Gravity applies.
- Max fall speed clamped.
- Updraft applies vertical acceleration.
- Updraft vertical speed clamped to -420.
- Horizontal wind clamped to ±360.
- Conveyor adds offset and clamps to ±360.
- One-way platform landing works.
- One-way platform pass-through works.
- Moving platform carry works.
- Low clearance blocks standing player.
- Low clearance allows crouching player.

---

#### `tilemap.test.js`

Assert:

- Tile parsing creates correct solid, one-way, spike, conveyor arrays.
- Solid query returns true for `#`.
- One-way query returns correct top surface.
- Spike query returns correct damage volume.
- Conveyor query returns correct offset.

---

#### `player.test.js`

Assert:

- Standing hitbox is 16 x 24.
- Crouch hitbox is 16 x 12.
- Crouch preserves feet position.
- Standing is blocked by insufficient clearance.
- Muzzle origin lowers when crouched.
- Muzzle X offset applies when aiming horizontally.
- Player takes 1 heart damage.
- Invulnerability prevents damage.
- Knockback applies from source.
- Death with lives remaining respawns.
- Death with zero lives triggers Game Over.
- Pit with full hearts respawns.
- Pit with 1 heart triggers death.
- Checkpoint sets respawn.
- Checkpoint restores 1 heart if below max.

---

#### `weapon.test.js`

Assert:

- Chirp fires one projectile with correct damage, speed, lifetime, radius.
- Sifter fires 5 pellets with correct spread.
- Lance pierces 3 distinct enemies.
- Lance does not hit same enemy twice.
- Bloom main splits on enemy hit.
- Bloom main splits on lifetime.
- Bloom main does not split on tile hit.
- Bloom shards have correct damage, lifetime, speed.
- Weapon switch sets 0.12 cooldown.
- Locked weapon selection does not change weapon.
- Locked weapon selection triggers deny event.
- Cycle weapon skips locked weapons.

---

#### `projectile.test.js`

Assert:

- Player projectile destroys on solid tile.
- Player projectile passes through one-way.
- Enemy projectile destroys on solid tile.
- Projectile lifetime expires.
- Projectile does not damage owner.
- High-speed projectile uses substeps.
- Lance pierce ID set works.
- Bloom split spawns correct shards.
- Echo shot bounces once.
- Projectile limits expire oldest.

---

#### `enemy.test.js`

Assert:

- Enemy activation radius is 320 px.
- Max 16 active enemies.
- If more than 16 are in radius, closest activate.
- World 2 HP is ceil(base * 1.15).
- World 2 projectile speed is base * 1.1.
- Mite moves toward player within 5 tiles.
- Mite waits 0.5 seconds when blocked.
- Drone patrols within 4 tiles.
- Drone requires LOS.
- Drone fires every 1.6 seconds.
- Pincer telegraphs 0.5 seconds before charge.
- Pincer charge stops on solid collision.
- Sentry aims at 3 rad/s.
- Sentry fires 2-round burst when aim within 10 degrees.
- Wraith phases every 2.5 seconds.
- Wraith phased state blocks player damage and contact.
- Golem stomp spawns spike patches.
- Golem death spawns Signal Heart.
- Enemy death clears enemy-owned projectiles.

---

#### `boss.test.js`

Assert:

- Hush Warden phase changes at 60%.
- Hush Warden charge leaves 4 spike patches.
- Hush Warden fan bolt fires 3 projectiles.
- Hush Warden phase 2 enables sweep beam.
- Hush Warden phase 2 drone summon respects max 3.
- Hush Warden death unlocks conduit after 2 seconds.
- Null Relay phase changes at 70% and 35%.
- Null Relay phase 2 has 1.5-second warning.
- Null Relay echo shot bounces once.
- Null Relay wraith summon respects max 4.
- Null Relay phase 3 overload cycle alternates beams and core exposed.
- Null Relay core exposed multiplies damage by 1.5.
- Null Relay death unlocks conduit after 3 seconds.
- Boss reset on player death restores full HP.

---

#### `progression.test.js`

Assert:

- Start unlocks Chirp only.
- Collecting Sifter tuner unlocks Sifter.
- Collecting Lance tuner unlocks Lance.
- Collecting Bloom tuner unlocks Bloom.
- Cores persist globally.
- Already collected cores are not spawned on stage load.
- Stage completion unlocks next stage.
- Final completion marks game complete.

---

### 23.2 Integration Tests

#### `stateFlow.test.js`

Assert:

- Title with no save shows Begin Signal.
- Title with save shows Continue and New Signal.
- Intro can be skipped with Enter, Space, or click.
- Intro leads to Signal Map.
- Signal Map starts unlocked stage.
- Stage leads to Summary after non-final conduit.
- Summary Continue proceeds to next stage.
- Game Over leads to retry, map, or title.
- End leads to map or title.

---

#### `stageLoad.test.js`

For every production stage:

Assert:

- Stage spec loads.
- Stage validator passes.
- Player spawns inside stage.
- Conduit exists.
- Checkpoint exists.
- Exactly 3 cores exist unless already collected.
- Enemy counts match expected table.
- Boss stages contain correct boss.
- World 2 stages apply enemy modifiers.
- Stage camera stays within bounds.
- No exceptions during 5-second idle simulation.

---

#### `checkpointDeath.test.js`

Assert:

- Death at checkpoint resets stage dynamic state.
- Player respawns at checkpoint.
- Hearts reset to 5.
- Lives decrement.
- Boss resets if present.
- Game Over triggers when lives reach 0.

---

#### `pit.test.js`

Assert:

- Falling 64 px below stage triggers pit.
- Pit with >1 heart respawns and enters 0.5 invulnerability.
- Pit with 1 heart triggers death.
- Pit without checkpoint respawns at stage start.

---

#### `pause.test.js`

Assert:

- Pause stops simulation.
- Enemies do not move during pause.
- Projectiles do not move during pause.
- Boss timers do not advance.
- Resume continues stage.
- Restart from pause resets stage.
- Map from pause exits stage.

---

#### `weaponProgression.test.js`

Assert:

- At `w1s1`, only Chirp is unlocked.
- Selecting Sifter at `w1s1` triggers deny.
- Collecting `w1s2` tuner unlocks Sifter.
- Collecting `w1s4` tuner unlocks Lance.
- Collecting `w2s2` tuner unlocks Bloom.
- Unlocked weapons persist across stages and retries.

---

#### `coreProgression.test.js`

Assert:

- Collecting a core removes it from stage.
- Core does not respawn on stage retry.
- Core total increments globally.
- Collecting all cores in a stage increases total by 3.

---

#### `bossDefeat.test.js`

For both bosses:

Assert:

- Boss can be damaged.
- Boss phase warnings appear.
- Boss attacks have telegraphs.
- Boss death clears projectiles and summons.
- Conduit activates after death sequence.
- Non-final boss stage leads to Summary.
- Final boss stage leads to End.

---

### 23.3 End-to-End Tests

#### `allStagesSmoke.test.js`

For every production stage:

1. Load stage in headless game.
2. Advance 10 seconds with idle player.
3. Assert no uncaught exceptions.
4. Assert player is alive unless killed by unavoidable hazard.
5. Assert stage validator passed.
6. Assert all entities are within reasonable bounds.

Pass criteria:

- All 10 stages load and simulate without crashing.

---

#### `stageCompletionProof.test.js`

For every production stage:

1. Load stage.
2. Run completion bot with `validationRoute`.
3. Assert bot reaches conduit.
4. Assert stage complete event fires.
5. Assert stage summary or end state appears.
6. Assert completion time is below a generous limit:

```text
limitMs = max(60000, targetTimeMs * 3)
```

For boss stages:

- Assert boss HP reaches 0 before conduit.
- Assert conduit was locked before boss death.

Pass criteria:

- Every stage can be completed by the route bot.

Rationale:

This proves the level is physically and mechanically playable, not just loadable.

---

#### `fullGame.test.js`

Test flow:

1. Start Title.
2. Begin Signal.
3. Skip Intro.
4. Enter Signal Map.
5. For each stage in order:
   - Start stage.
   - Run completion bot.
   - Assert stage complete.
   - Continue from summary.
6. Assert End state after `w2s5`.
7. Assert total deaths are non-negative.
8. Assert total time is positive.
9. Assert cores are 0 if no core routes used.

Pass criteria:

- A full game can be played from Title to End.

---

#### `allCores.test.js`

For every production stage:

1. Load stage.
2. For each core in stage:
   - Run `coreRoutes` entry for that core.
   - Assert core is collected.
3. Run main `validationRoute` to conduit.
4. Assert stage complete.
5. Continue to next stage.

After all stages:

Assert:

- Total cores = 30.
- End screen shows `Cores 30/30`.

Pass criteria:

- All 30 cores are collectible.

---

### 23.4 Manual QA Checklist

Automated tests prove function, but manual QA is required for feel.

Check:

- Title menu hover/confirm feels correct.
- Intro cards can be skipped.
- Signal Map nodes show locked/unlocked/completed correctly.
- World 2 is dimmed until `w1s5` complete.
- Player movement feels snappy.
- Coyote time and jump buffer feel fair.
- Crouch is clearly visible and usable.
- Low-clearance sections clearly require crouch.
- Mouse aim is responsive.
- Crosshair is visible in Stage state.
- Keyboard fallback facing indicator works.
- All 4 weapons feel mechanically distinct.
- Weapon switch cooldown is noticeable but not annoying.
- Locked weapon deny is readable.
- Hearts display correctly.
- Core counter flashes on collection.
- Checkpoint feedback is clear.
- Damage vignette is readable but not blinding.
- Enemy telegraphs are readable.
- Wraith phase is unmistakable.
- Boss beams are telegraphed before damage.
- Boss phase changes are clear.
- Boss death feels like resolution.
- Game Over feels like lost signal.
- End screen shows correct stats.
- Audio events match actions.
- No audio clipping.
- Performance stays near 60 updates/second on desktop.
- No memory leak after playing all stages.

---

## 24. Performance and Limits

Entity limits:

| Limit | Value |
|---|---:|
| Active enemies | 16 |
| Player projectiles | 80 |
| Enemy projectiles | 120 |
| Temporary spike patches | 20 |
| Active summoned boss enemies | 4 |

Overflow rules:

- If player projectiles exceed 80:
  - Expire oldest.
- If enemy projectiles exceed 120:
  - Expire oldest.
- If temporary spike patches exceed 20:
  - Remove oldest.
- If active enemies exceed 16:
  - Make farthest active enemy beyond 320 px dormant.

Dormant enemy:

- Does not act.
- Does not count as active.
- Can reactivate if space is available.

Collision performance:

- Use tile grid for tiles.
- Use direct AABB checks for entities.
- No spatial hash required for this entity count.

Rationale:

These limits are low enough that simple linear checks are fast and easier to debug.

---

## 25. Edge Cases

The implementation must handle all of these.

| Case | Required behavior |
|---|---|
| No checkpoint activated | Respawn at stage start |
| Pit with full hearts | Lose 1 heart, respawn checkpoint |
| Pit with 1 heart | Trigger death |
| Weapon switch while firing | Switch allowed, switch cooldown prevents fire |
| Select locked weapon | Deny, no change |
| Player dies during boss | Boss resets, respawn checkpoint |
| Player reaches conduit while dead | Cannot happen; conduit checks alive |
| Boss projectile during invulnerability | No damage |
| Enemy contact during invulnerability | No damage |
| Multiple projectiles kill same enemy same frame | First projectile applies, later skip dead enemy |
| Bloom splits inside wall | Does not split |
| Lance hits same enemy twice | Enemy ID set prevents double damage |
| Mouse leaves window while shooting | Mouse shooting stops, J still works |
| Keyboard-only fallback | Shoots facing direction |
| Pause during boss | All timers stop |
| Pause during summary | Not available |
| Storage unavailable | Session-only progress |
| Stage retry | Dynamic reset, global progression persists |
| Boss death | Clear boss attacks, projectiles, summons |
| World 2 standard enemy | HP and projectile speed modifiers apply |
| World 2 boss | No standard enemy modifiers |
| Stage shorter than viewport | Center camera, background fills |
| Low clearance with standing player | Blocked |
| Low clearance with crouching player | Passable |

---

## 26. Definition of Done

The game is engineering-complete when:

1. The repository layout exists.
2. `index.html` boots the game in a desktop browser.
3. All 10 stage files exist.
4. Stage validator passes for all 10 stages.
5. Player can move left/right, jump, crouch, aim, and shoot.
6. All 4 weapons exist and unlock in the correct stages.
7. All standard enemies behave according to `gameplay.md`.
8. Both bosses behave according to `gameplay.md` and `visual.md`.
9. World 1 has 5 stages.
10. World 2 has 5 stages.
11. World 2 unlocks after World 1 completion.
12. Each stage has 3 optional cores.
13. All 30 cores are collectible.
14. Checkpoints work.
15. Pit rule works.
16. Lives and death work.
17. Pause works.
18. Stage retry works.
19. Signal Map replay works.
20. Save/continue works.
21. Audio events fire for all required gameplay events.
22. HUD matches visual document.
23. VFX do not affect gameplay.
24. All unit tests pass.
25. All integration tests pass.
26. All end-to-end tests pass.
27. Manual QA checklist is complete.

Final completion proof:

```text
Title
-> Intro
-> Signal Map
-> w1s1 through w1s5
-> w2s1 through w2s5
-> End
```

With optional all-core route:

```text
Total Cores 30/30
```

Rationale:

This definition proves the requested game is complete: a side-scrolling platformer shooter with 4 gun types, player jump/move/crouch, 2 worlds, 5 stages each, and a playable end state.