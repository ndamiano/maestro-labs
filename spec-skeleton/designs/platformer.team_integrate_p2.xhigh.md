# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Make a side-scrolling, platformer shooter | 1.1, 4.1, 4.5, 4.9 |
| At least 4 different gun types | 4.8, 4.9 |
| Character can move left or right | 4.4, 4.5 |
| Character can jump | 4.5 |
| Character can crouch | 4.4, 4.5, 4.6 |
| Story progression like Mario with worlds and stages | 4.2, 4.13 |
| Start with 2 worlds | 4.2 World Roster |
| 5 stages per world, 10 total | 4.2 Stage Roster |
| Do not simply copy Mario | 3.1, 4.2, 5.1 |
| Added: 2D gameplay with 2.5D presentation | 1.1, 3.3 |
| Added: named player, enemies, bosses, and stage identity | 4.2, 4.10, 4.11, 5 |
| Added: checkpoints, pits, hazards, and stage reset | 4.4, 4.6, 4.17 |
| Added: optional cores for completion stats | 4.13, 7 |
| Added: HUD, crosshair, damage feedback, and state screens | 7 |
| Added: generated Web Audio sound and music | 6 |
| Added: deterministic simulation and testable build | 1.2, 2, 9 |

## 0.2 Decisions

| Topic | What gameplay said | What visual said | What engineering said | Ruling and one clause why |
| --- | --- | --- | --- | --- |
| Audio implementation | Listed audio events only | Defined SFX table, music map, and asset files | Used `assets/audio` and manifest audio files | All audio is generated with the Web Audio API; no external audio files are required. This follows the integrator instruction that the game must use Web Audio generation. |
| Sprite implementation | Did not define art assets | Defined sprite sizes, palettes, animation names, and frame counts | Expected sprite sheets and `assets/sprites` | All sprites are drawn in code as flat vector shapes using the visual sizes, palettes, and animation names. No external image files are required. |
| Final authority | Mechanics authority for numbers/rules | Presentation authority for appearance/audio/UX | Architecture authority for modules/tests | This merged spec is final. Where the three docs disagreed, the ruling in this table wins. |
| Muzzle origin | Player center plus 2 standing, plus 8 crouching | Crouch lowers muzzle visually | Anchored muzzle to standing feet reference: standing 10 px above feet, crouched 4 px above feet | Use the engineering anchored muzzle formula. It keeps the muzzle inside the player body while preserving the gameplay intent that crouch lowers the muzzle. |
| Hush Warden base movement | Phase 2 increases move speed by 10 percent, but gave no base speed | No base speed | Defined base 80 px/s and phase 2 88 px/s | Use 80 px/s base and 88 px/s phase 2. This gives the 10 percent modifier a concrete value without changing the 480 px/s charge speed. |
| Crouch-only traversal | Required crouch sections and low ceilings | Crouch is visually obvious | Added `lowClearance` pixel volumes to make 12 px crouch passages possible | Use `lowClearance` rectangles for crouch-only passages. Tile resolution alone cannot express a 24 px standing block that a 12 px crouch can pass. |
| Death respawn reset | Respawn at checkpoint with full hearts and 1.0 s invulnerability | No reset rule | Reset dynamic stage state on death with lives remaining | Use engineering full dynamic reset on death. This makes checkpoints predictable and prevents impossible enemy/projectile states after respawn. |
| Camera for short stages | Clamp camera to stage bounds | Background must fill viewport | Center camera on an axis when stage is shorter than viewport | Center vertically or horizontally when a stage dimension is less than the viewport. This avoids letterboxing while keeping 960 x 540 gameplay coordinates. |
| Player update order | Gave a high-level player update order | No order | Gave a more detailed fixed-step order | Use the engineering detailed order. It resolves wind, conveyor, platform carry, and jump timing deterministically. |
| Random source | Did not define RNG | No RNG rules | Use `mulberry32` and ban `Math.random` in simulation | Use one deterministic `mulberry32` RNG per stage. Boss choices must be reproducible in tests. |
| Core notification | Allowed “Core collected, if desired” notification | No bottom-center core text; HUD counter flashes | No core notification | Use no bottom-center core notification. Cores are frequent and optional; the counter flash is the feedback. |
| Beam positioning | Null Relay Side Sweep uses random Y | Beam telegraphs are world objects | All boss beams locked to player position at telegraph start | Telegraphs lock the displayed line at telegraph start. Hush Sweep and Null Phase 3 horizontal beams use player Y at telegraph start. Null Relay Phase 1 Side Sweep uses a random valid arena Y chosen at telegraph start. This keeps the visual telegraph honest and preserves the gameplay random-Y rule. |
| Touch controls | Out of scope | No touch rules | Cut touch controls | Desktop mouse and keyboard only. The request is a browser game, but the provided design is desktop-focused. |
| Score system | No score | No damage numbers or score | No score | No score. Cores and completion stats are the only completion metrics. |
| Progress persistence | Store progress if browser storage available | Title supports Continue/New Signal | localStorage with memory fallback | T1 ships session save and in-memory save. T2 adds localStorage persistence. This keeps the core game playable without storage. |
| Presentation depth | Allowed 2.5D parallax | Defined parallax layer stack | Defined parallax as presentation only | T1 requires readable layer 4 gameplay and layer 5 VFX. T2 adds animated parallax background layers. |
| Music layering | Required state audio cues | Full music map and phase layering | Audio manager with crossfade and ducking | T1 ships basic state music loops and SFX. T2 adds boss phase layering and richer state music. |
| Screen shake | Not specified | Defined small shake events | No explicit shake architecture | T1 ships damage vignette and critical feedback. T2 adds the listed small screen shakes. |
| Render interpolation | Fixed timestep at 60 updates/s | No interpolation requirement | No interpolation | No render interpolation. The logical viewport is fixed and the target update rate is 60 Hz. |
| Object pooling | Entity limits given | No pooling rules | No pooling beyond array expiration | Use simple array expiration and entity limits. |
| Keyboard fallback | J shoots in facing direction | Facing indicator for keyboard fallback | Defined keyboard fallback aim | Use J fallback. If no horizontal input has occurred, face right. |
| World 2 modifiers | Standard enemy HP x1.15 and projectile speed x1.1 | World 2 palette changes | Standard enemies only; bosses unmodified | Use World 2 modifiers for standard enemies only. Bosses use their defined stats. |
| Stage lives | 3 lives per stage, reset each stage | No lives rule | Stage lives reset per stage | Lives reset to 3 at every stage start and retry. This keeps progression smooth and prevents long-stage death spirals. |
| Cores | Optional, 3 per stage, 30 total | Core visual and HUD counter | Core IDs and progression storage | Cores are optional, globally persistent, and used only for completion stats. |
| Boss reset | Boss resets if player dies during boss | Boss death visual | Boss resets to full HP/idle on player death | Boss resets to full HP and idle on player death with lives remaining. |
| Foreground occlusion | No gameplay depth | No gameplay-occluding foreground; edge framing max 80 px | No foreground rule | No gameplay-occluding foreground. Optional edge framing may not cover projectiles, enemies, hazards, or the player. |
| Minimap and damage numbers | No minimap or damage numbers implied | No damage numbers, no minimap | No minimap | No damage numbers and no minimap. The HUD and world telegraphs carry readability. |
| Test strategy | Fairness rules and completion definition | Final visual checklist | Route-based completion bot and deterministic tests | Use deterministic route-based completion bot for stage proof. Every production stage must have a `validationRoute`. |

## 0.3 Tiers

T1 is the game that must ship:

- FixedTimestep
- Input
- PlayerMovement
- TileCollision
- LowClearance
- Weapons
- Projectiles
- Enemies
- Bosses
- Stages
- Progression
- SessionSave
- Checkpoints
- Hazards
- Conduit
- Camera
- HUD
- SFX
- StateMachine
- Tests

T2 stages the rest, in this order:

- T2-1 localStorage persistence for Continue, New Signal, and stats.
- T2-2 animated parallax background layers for Title, Intro, Map, Stage, and End.
- T2-3 animated title background showing Sumpworks and Skyloom.
- T2-4 boss music phase layering and richer state music.
- T2-5 small screen shake events for golem stomp, boss charge impact, and boss death.
- T2-6 extra projectile trails, wind particles, and background sway.

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- All gameplay coordinates are logical pixels.
- Positive X is right.
- Positive Y is down.
- Stage origin is top-left.
- Tile size is 32 px.
- Logical viewport is 960 x 540 px.
- Canvas is scaled to fit the screen while preserving aspect ratio.
- Simulation uses a fixed timestep.
- `STEP = 1 / 60` seconds.
- Frame delta is clamped to 0.1 seconds.
- Simulation time advances in fixed steps.
- Rendering receives the accumulator fraction but does not interpolate.
- Time values are seconds unless marked `Ms`.
- Distance values are pixels.
- Speed values are pixels per second.
- Acceleration values are pixels per second squared.
- Angle values are degrees in design tables. Conversion to radians is implementation detail.
- Entity positions are top-left pixel coordinates unless a rule says center or feet.

## 1.2 Important conventions

- No touch controls.
- Desktop mouse and keyboard are the only required inputs.
- No external runtime libraries.
- No build step.
- No physics engine.
- No ECS library.
- No frame interpolation.
- No object pooling beyond simple array expiration.
- Simulation is deterministic.
- No `Math.random` in simulation.
- One random source per stage: `mulberry32`.
- Default stage seed is `100 * world + index`.
  - World 1 Stage 1 seed is 101.
  - World 2 Stage 5 seed is 205.
- Tests may override the stage seed with `debug.setRngSeed`.

Fixed loop:

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

System run order each fixed step:

1. Advance stage time.
2. Update moving platforms and store platform deltas.
3. Apply platform carry to player if riding.
4. Read player input.
5. Update player facing.
6. Update weapon selection, switch cooldown, and fire cooldown.
7. Apply horizontal acceleration or friction.
8. Apply wind acceleration.
9. Apply conveyor offset if grounded.
10. Apply gravity or updraft.
11. Handle jump buffer, coyote time, and variable jump cut.
12. Integrate X and resolve horizontal collision.
13. Integrate Y and resolve vertical collision.
14. Update grounded state.
15. Update coyote and jump buffer timers.
16. Check pit rule.
17. Check hazards.
18. Update player projectiles.
19. Update enemy projectiles.
20. Update enemies.
21. Update boss.
22. Update beams.
23. Update temporary spikes.
24. Update pickups.
25. Update checkpoint and conduit triggers.
26. Update camera.
27. Update HUD.
28. Emit VFX and audio events.

Controls table:

| Action | Primary input | Alternate input |
| --- | --- | --- |
| Move left | A | Left Arrow |
| Move right | D | Right Arrow |
| Jump | W | Up Arrow or Space |
| Crouch | S | Down Arrow |
| Aim and shoot | Left mouse button | J |
| Switch to weapon 1 | 1 | None |
| Switch to weapon 2 | 2 | None |
| Switch to weapon 3 | 3 | None |
| Switch to weapon 4 | 4 | None |
| Cycle weapons forward | E | Q |
| Pause | Escape | P |

Aiming rules:

- Mouse aiming is primary.
- Player can aim in any 2D direction.
- Visual facing follows mouse X relative to player.
- If mouse input is unavailable, J shoots in facing direction.
- If no horizontal input has occurred, facing is right.
- Crouch does not restrict aim.
- Crouch lowers muzzle origin and hitbox.

# 2. CONTRACTS

## 2.1 Module layout

The repository must contain these files.

```text
/
  index.html
  css/
    styles.css
  package.json
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
      Renderer.js
      Camera.js
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

No `assets/audio` or `assets/sprites` directory is required. All audio is generated, and all sprites are drawn in code.

## 2.2 Global context

The global `game` object must expose every field that a rule reads or writes.

```js
game = {
  state: null,
  stage: null,
  input: null,
  audio: null,
  save: null,
  renderer: null,
  progression: null,
  rng: null,
  stageSeed: 0,
  simTime: 0,
  stageTimeMs: 0,
  stageDeaths: 0,
  runStats: {
    timeMs: 0,
    deaths: 0
  },
  debug: null,
  vfx: null,
  hud: null
}
```

Stage context:

```js
stage = {
  id: "w1s1",
  world: 1,
  index: 1,
  name: "First Current",
  label: "W1 · N1",
  widthPx: 0,
  heightPx: 0,
  seed: 0,
  tilemap: null,
  player: null,
  enemies: [],
  boss: null,
  projectiles: [],
  enemyProjectiles: [],
  beams: [],
  tempSpikes: [],
  platforms: [],
  windZones: [],
  lowClearance: [],
  checkpoints: [],
  cores: [],
  hearts: [],
  tuners: [],
  conduit: null,
  respawnPoint: { x: 0, y: 0 },
  checkpointActivated: false,
  bossActive: false,
  conduitReady: false,
  stageComplete: false
}
```

Player record:

```js
player = {
  x: 0,
  y: 0,
  vx: 0,
  vy: 0,
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
    fireCooldown: {
      chirp: 0,
      sifter: 0,
      lance: 0,
      bloom: 0
    }
  }
}
```

Progression record:

```js
progression = {
  completed: [],
  unlocked: ["w1s1"],
  weapons: ["chirp"],
  cores: {},
  stats: {
    timeMs: 0,
    deaths: 0
  }
}
```

Input record:

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

Projectile record:

```js
projectile = {
  id: 0,
  team: "player",
  x: 0,
  y: 0,
  vx: 0,
  vy: 0,
  radius: 0,
  damage: 0,
  lifetime: 0,
  age: 0,
  weapon: null,
  knockback: 0,
  pierceIds: null,
  isBloomMain: false,
  isBloomShard: false,
  bounceRemaining: 0
}
```

Enemy record:

```js
enemy = {
  id: 0,
  type: "mite",
  world: 1,
  x: 0,
  y: 0,
  w: 0,
  h: 0,
  hp: 0,
  maxHp: 0,
  vx: 0,
  vy: 0,
  active: false,
  dormant: false,
  grounded: false,
  state: "idle",
  timers: {},
  spawnX: 0,
  spawnY: 0,
  facing: 1,
  isBoss: false
}
```

Boss record:

```js
boss = {
  id: 0,
  type: "hushWarden",
  x: 0,
  y: 0,
  w: 64,
  h: 64,
  hp: 0,
  maxHp: 0,
  phase: 1,
  state: "idle",
  cooldowns: {},
  active: false,
  dying: false,
  deathTimer: 0,
  arena: {
    x: 0,
    y: 0,
    w: 0,
    h: 0
  }
}
```

Stage object records:

```js
checkpoint = {
  x: 0,
  y: 0,
  w: 32,
  h: 48,
  activated: false
}
```

```js
core = {
  id: "w1s1-core-1",
  x: 0,
  y: 0,
  w: 24,
  h: 24,
  collected: false
}
```

```js
heart = {
  x: 0,
  y: 0,
  w: 24,
  h: 24,
  collected: false
}
```

```js
tuner = {
  weapon: "sifter",
  x: 0,
  y: 0,
  w: 32,
  h: 48,
  collected: false
}
```

```js
conduit = {
  x: 0,
  y: 0,
  w: 64,
  h: 96,
  active: false,
  lockedByBoss: false
}
```

Beam record:

```js
beam = {
  id: 0,
  type: "horizontal",
  x: 0,
  y: 0,
  width: 0,
  height: 24,
  state: "telegraph",
  telegraphTime: 0,
  activeTime: 0,
  timer: 0,
  damage: 1
}
```

Temporary spike record:

```js
tempSpike = {
  x: 0,
  y: 0,
  w: 0,
  h: 0,
  warnTimer: 0,
  activeTimer: 0,
  duration: 0,
  state: "warn"
}
```

Platform record:

```js
platform = {
  id: "p1",
  x: 0,
  y: 0,
  w: 64,
  h: 16,
  vx: 0,
  vy: 0,
  speed: 0,
  waypoints: [],
  pingPong: true,
  deltaX: 0,
  deltaY: 0
}
```

Wind zone record:

```js
windZone = {
  x: 0,
  y: 0,
  w: 0,
  h: 0,
  type: "updraft"
}
```

Low clearance record:

```js
lowClearance = {
  x: 0,
  y: 0,
  w: 0,
  h: 0
}
```

## 2.3 Module specifics

### main.js

Responsibilities:

- Create `Game`.
- Create `Input`.
- Create `Audio`.
- Create `Save`.
- Create `Renderer`.
- Create `Progression`.
- Start fixed-timestep loop.
- Enter `title` state.

Functions:

- `boot()`
- `frame(now)`

### Game.js

Responsibilities:

- Own global context.
- Run state machine.
- Start and reset stages.
- Handle stage completion.
- Handle game over.
- Handle end state.

Functions:

- `constructor()`
- `update(dt)`
- `render(alpha)`
- `gotoState(stateName, payload)`
- `startStage(stageId)`
- `pauseStage()`
- `resumeStage()`
- `restartStage()`
- `completeStage()`
- `gameOver()`
- `endGame()`
- `addDeath()`
- `addStageTimeMs(ms)`

### FixedTimestep.js

Responsibilities:

- Accumulate frame time.
- Clamp delta to 0.1 seconds.
- Call game updates in fixed steps.

Functions:

- `update(delta)`
- `reset()`

### StateMachine.js

Responsibilities:

- Store current state.
- Enter, update, render, and input states.
- Prevent pause from destroying stage.

State interface:

- `enter(game, payload)`
- `update(game, dt)`
- `render(game, alpha)`
- `onInput(game, input, dt)`

Functions:

- `enter(stateName, payload)`
- `update(dt)`
- `render(alpha)`
- `onInput(input, dt)`

### Input.js

Responsibilities:

- Keyboard state.
- Mouse position.
- Mouse inside state.
- Edge-triggered jump and shoot.
- Weapon select and cycle.
- Pause press.
- Keyboard fallback aim.

Fields:

- `left`
- `right`
- `jumpHeld`
- `jumpPressed`
- `crouchHeld`
- `shootHeld`
- `mouse.screenX`
- `mouse.screenY`
- `mouse.worldX`
- `mouse.worldY`
- `mouse.inside`
- `weaponSelect`
- `cycleDirection`
- `pausePressed`

Functions:

- `bind(target)`
- `unbind()`
- `update()`
- `setMouseScreen(x, y)`
- `setMouseWorld(x, y)`
- `setMouseInside(value)`
- `pressJump()`
- `releaseJump()`
- `pressShoot()`
- `releaseShoot()`
- `selectWeapon(slot)`
- `cycleWeapons(direction)`
- `pressPause()`
- `clearEdges()`

### Audio.js

Responsibilities:

- Create Web Audio context.
- Generate SFX from recipes.
- Generate music loops.
- Handle priority.
- Duck music during important SFX.
- Pause and resume.

Functions:

- `init()`
- `playSfx(name, params)`
- `playMusic(id)`
- `stopMusic()`
- `setPaused(value)`
- `duck(amountMs)`
- `resumeMusic()`

### Renderer.js

Responsibilities:

- Draw canvas world.
- Draw parallax layers.
- Draw tiles, entities, pickups, beams, and VFX.
- Use visual palette and sprite sizes.
- No gameplay effect.

Functions:

- `render(game, alpha)`
- `drawLayer(layerIndex, camera)`
- `drawTile(tile)`
- `drawPlayer(player)`
- `drawEnemy(enemy)`
- `drawBoss(boss)`
- `drawProjectile(projectile)`
- `drawBeam(beam)`
- `drawTempSpike(spike)`
- `drawPickup(pickup)`
- `drawConduit(conduit)`
- `drawCheckpoint(checkpoint)`
- `drawPlatform(platform)`
- `drawWindZone(zone)`

### Camera.js

Responsibilities:

- Follow player.
- Apply lookahead.
- Smooth camera.
- Clamp or center camera.

Functions:

- `update(game, dt)`
- `reset(stage)`

### Animator.js

Responsibilities:

- Track animation names and frame timing.
- Provide current frame for code-drawn sprites.

Functions:

- `setAnimation(name)`
- `update(dt)`
- `frameFor(name)`
- `isLooping(name)`

### VFX.js

Responsibilities:

- Maintain active visual effects.
- Draw VFX.
- No gameplay effect.

Functions:

- `emit(name, data)`
- `update(dt)`
- `render(camera)`
- `clear()`

### Save.js

Responsibilities:

- Load progress.
- Save progress.
- Reset progress.
- Use in-memory save in T1.
- Use localStorage in T2 if available.

Functions:

- `load()`
- `save()`
- `reset()`
- `getRaw()`
- `setRaw(data)`

### Progression.js

Responsibilities:

- Track completed stages.
- Track unlocked stages.
- Track unlocked weapons.
- Track collected cores.
- Track global stats.
- Provide continue stage.

Functions:

- `newProgression()`
- `loadProgression(saveData)`
- `saveProgression()`
- `isStageUnlocked(stageId)`
- `isStageCompleted(stageId)`
- `completeStage(stageId, stageStats)`
- `unlockWeapon(weapon)`
- `isWeaponUnlocked(weapon)`
- `collectCore(coreId)`
- `isCoreCollected(coreId)`
- `getContinueStage()`
- `reset()`

### Tilemap.js

Responsibilities:

- Parse tile strings.
- Store solid, one-way, spike, and conveyor tiles.
- Query tile types.
- Provide line of sight.

Tile characters:

| Char | Meaning |
| --- | --- |
| `.` | Empty |
| `#` | Solid tile |
| `=` | One-way platform |
| `^` | Up-facing spike |
| `v` | Down-facing spike |
| `>` | Right conveyor |
| `<` | Left conveyor |

Functions:

- `parse(width, height, rows)`
- `isSolid(tx, ty)`
- `isOneWay(tx, ty)`
- `spikeAt(x, y)`
- `conveyorAt(x, y)`
- `oneWayTopAt(tx, ty)`
- `los(x1, y1, x2, y2)`

### Physics.js

Responsibilities:

- Integrate player.
- Resolve tile collision.
- Resolve one-way platforms.
- Resolve moving platforms.
- Resolve low clearance.
- Apply conveyor and wind.

Functions:

- `integratePlayer(player, dt, tilemap, platforms, windZones, lowClearance)`
- `resolveHorizontal(player, tilemap, lowClearance)`
- `resolveVertical(player, tilemap, platforms, lowClearance)`
- `canStandIn(player, lowClearance)`
- `applyConveyor(player, tilemap)`
- `applyWind(player, windZones)`

### Player.js

Responsibilities:

- Player state.
- Movement.
- Crouch.
- Jump.
- Damage.
- Death.
- Respawn.
- Muzzle origin.
- Aim vector.

Functions:

- `constructor(x, y)`
- `update(dt, input, stage)`
- `takeDamage(sourceX, sourceY)`
- `die()`
- `respawn(point)`
- `setCrouch(value)`
- `tryStand()`
- `muzzleOrigin(aimX, aimY)`
- `aimVector(mouseWorld)`
- `feetY()`
- `centerX()`
- `centerY()`

### Weapon.js

Responsibilities:

- Weapon selection.
- Switch cooldown.
- Fire cooldown.
- Fire behavior.

Functions:

- `update(dt, player)`
- `select(player, weapon)`
- `cycle(player, direction)`
- `canFire(player)`
- `fire(player, aimX, aimY)`
- `deny(player)`

### Projectile.js

Responsibilities:

- Spawn player and enemy projectiles.
- Move with substeps.
- Collide with tiles.
- Apply damage.
- Handle Lance pierce.
- Handle Bloom split.
- Handle Echo bounce.
- Expire projectiles.

Functions:

- `spawnPlayerProjectile(weapon, x, y, aimX, aimY)`
- `spawnEnemyProjectile(type, x, y, vx, vy, radius, damage, lifetime)`
- `update(projectiles, dt, stage)`
- `moveSubsteps(projectile, dt)`
- `checkTile(projectile, tilemap)`
- `checkTarget(projectile, stage)`
- `applyDamage(projectile, target)`
- `remove(projectile)`

### Beam.js

Responsibilities:

- Boss beam telegraphs.
- Active beam damage.
- Beam lifecycle.

Functions:

- `spawnHorizontal(arena, y, telegraphTime, activeTime)`
- `spawnVertical(arena, x, telegraphTime, activeTime)`
- `update(beams, dt, stage)`
- `damagePlayer(beam, player)`

### TempSpike.js

Responsibilities:

- Temporary spike patches.
- Warning state.
- Active damage.
- Expiration.

Functions:

- `spawn(x, y, w, h, warnDuration, activeDuration)`
- `update(spikes, dt)`
- `damagePlayer(spike, player)`
- `clearAll()`

### Enemy.js

Responsibilities:

- Enemy activation.
- Enemy state machines.
- Enemy damage.
- Enemy death.
- World 2 modifiers.
- Enemy projectile spawning.

Functions:

- `spawn(type, world, x, y)`
- `update(enemy, dt, stage)`
- `activateIfNear(enemy, player, stage)`
- `damage(enemy, amount)`
- `die(enemy, stage)`
- `clearEnemyProjectiles(enemy, stage)`
- `world2Hp(baseHp)`
- `world2ProjectileSpeed(baseSpeed)`

### Bosses

Responsibilities:

- Boss activation.
- Boss phases.
- Boss attacks.
- Boss summons.
- Boss death.
- Conduit unlock.

Functions:

- `HushWarden.constructor(stage)`
- `HushWarden.update(dt, stage)`
- `HushWarden.damage(amount)`
- `HushWarden.die(stage)`
- `NullRelay.constructor(stage)`
- `NullRelay.update(dt, stage)`
- `NullRelay.damage(amount)`
- `NullRelay.die(stage)`

### Stage.js

Responsibilities:

- Runtime stage state.
- Dynamic reset.
- Stage trigger checks.

Functions:

- `constructor(spec, progression)`
- `resetDynamic()`
- `update(dt)`
- `checkConduit(player)`
- `checkCheckpoint(player)`

### StageFactory.js

Responsibilities:

- Convert stage spec into runtime stage.
- Apply World 2 modifiers.
- Skip globally collected cores and tuners.
- Create boss if present.

Functions:

- `createStage(spec, progression)`
- `createEnemy(type, world, x, y)`
- `createBoss(spec)`
- `applyWorld2(enemy)`
- `skipCollectedCores(spec, progression)`
- `skipCollectedTuners(spec, progression)`

### StageValidator.js

Responsibilities:

- Validate stage specs.
- Validate structure.
- Validate required content.
- Validate enemy counts.
- Validate object placement.
- Validate low clearance.
- Validate route proof.

Functions:

- `validate(spec, options)`
- `checkStructure(spec)`
- `checkRequiredContent(spec)`
- `checkEnemyCounts(spec)`
- `checkObjectPlacement(spec, tilemap)`
- `checkLowClearance(spec, tilemap)`
- `checkRoute(spec, bot)`

Stage spec fields:

```js
stageSpec = {
  id: "w1s1",
  world: 1,
  index: 1,
  name: "First Current",
  width: 75,
  height: 12,
  boss: false,
  spawn: { x: 0, y: 0 },
  tiles: [],
  lowClearance: [],
  wind: [],
  platforms: [],
  enemies: [],
  checkpoints: [],
  cores: [],
  hearts: [],
  tuners: [],
  conduit: { x: 0, y: 0 },
  bossSpec: null,
  validationRoute: [],
  coreRoutes: []
}
```

Enemy spec:

```js
{
  type: "mite",
  x: 0,
  y: 0
}
```

Core spec:

```js
{
  id: "w1s1-core-1",
  x: 0,
  y: 0
}
```

Tuner spec:

```js
{
  weapon: "sifter",
  x: 0,
  y: 0
}
```

Boss spec:

```js
{
  type: "hushWarden",
  x: 0,
  y: 0,
  arena: {
    x: 0,
    y: 0,
    w: 0,
    h: 0
  },
  trigger: {
    x: 0,
    y: 0,
    w: 0,
    h: 0
  }
}
```

Validation route waypoint:

```js
{
  x: 0,
  y: 0,
  crouch: false,
  jump: false,
  holdJump: false,
  faceLeft: false,
  waitMs: 0,
  shoot: false
}
```

### HUD.js

Responsibilities:

- Build DOM HUD.
- Update HUD only when values change.
- Show hearts, weapon slots, stage label, core counter, pause icon, boss HUD, notifications, edge arrow, control hint, crosshair, facing indicator, and damage vignette.

Functions:

- `build(container)`
- `update(game)`
- `showNotification(text, priority)`
- `flashCoreCounter()`
- `showDamageFlash()`
- `updateBossHUD(boss)`
- `updateEdgeArrow(objective, camera)`
- `showControlHint(stageId)`

# 3. VISUAL SPEC

The look is rust-circuit industrial: a dying maintenance city re-awakened by signal light. Presentation is flat vector, high-contrast, and limited-palette. The player is a compact courier with a cyan visor. Safe signal systems are cyan. Collectibles and special weapon energy are amber. Enemy damage, hazards, and boss energy are red or orange. World 1 is cold, wet, rusty, and oppressive. World 2 is brighter, airy, wind-swept, and more exposed. The end state resolves into coherent cyan and white signal light. No Mario-like pipes, coins, mushrooms, castles, or flagpoles are used.

Lighting and atmosphere:

- No photographic realism.
- No anime style.
- No heavy 3D rendering.
- No hand-painted clutter.
- Background areas behind gameplay should not drop below roughly `#121820`.
- Enemy projectiles must always have a white or bright core.
- Player projectiles must be visually distinct from enemy projectiles.
- Spikes must never match the color of the floor they sit on.
- One-way platforms must have a brighter top edge than the background.
- Boss telegraphs must be visible against both World 1 and World 2 backgrounds.
- No full-screen red flash beyond vignette.
- No gameplay-occluding foreground.
- Optional edge framing may cover no more than 80 px on any side.
- Edge framing may not cover the center of the screen.
- Edge framing may not obscure projectiles, enemies, hazards, or the player.

Space:

- Gameplay is strictly 2D.
- Presentation may use parallax background layers.
- Parallax is presentation only.
- Parallax must not imply gameplay depth.
- No camera rotation.
- No Z-axis gameplay.
- Stages shorter than the viewport are centered on the short axis and filled by background.
- The gameplay layer always occupies 960 x 540 logical pixels.

Core palette table:

| Name | Hex | Use |
| --- | --- | --- |
| Void Dark | `#0B1017` | Backgrounds, shadows, UI backgrounds |
| Deep Steel | `#1C2530` | Mid-background panels, walls |
| Steel | `#3A4856` | Neutral structures |
| Rust Dark | `#7A3E33` | World 1 metal, pipes |
| Rust Light | `#B86B4F` | Rust highlights, enemy armor |
| Oil Teal | `#2E5F5A` | World 1 canal water, wet metal |
| Water Dark | `#153136` | Pits, canal depths |
| Signal Cyan | `#4BE2FF` | Player, checkpoints, conduit, active UI |
| Signal White | `#F5FBFF` | Cores, highlights, beam cores |
| Signal Amber | `#FFB347` | Tuners, collectible accents, Sifter, warnings |
| Danger Red | `#FF4F5A` | Enemy damage, spikes, boss, danger |
| Warning Orange | `#FF8B3D` | Enemy projectiles, telegraphs |
| Heart Pink | `#FF7D9B` | Signal hearts, warm pickups |
| UI Neutral | `#D7DDE4` | Text, inactive UI |
| UI Dark | `#303841` | Locked UI, disabled slots |

Color semantics:

| Color | Meaning |
| --- | --- |
| Cyan | Player, safe signal, active systems, checkpoints, conduit, active UI |
| White | Pure signal, cores, beam centers, high-value highlights |
| Amber | Collectibles, tuners, Sifter, special weapon energy, mild warnings |
| Red or Orange | Enemy attacks, damage, hazards, boss energy, locked objectives |
| Neutral steel or rust | Environment |
| Pink | Health |

Parallax layer table:

| Layer | Content | X parallax | Y parallax | Notes |
| ---: | --- | ---: | ---: | --- |
| 0 | Sky or gradient | 0.0 | 0.0 | Static or slow vertical interpolation only |
| 1 | Far silhouette | 0.12 | 0.04 | Distant pipes, spires, market frames |
| 2 | Mid structures | 0.28 | 0.10 | Pipes, catwalks, shelves, clouds |
| 3 | Near props | 0.55 | 0.19 | Non-interactive props, lamps, cloth, cables |
| 4 | Gameplay layer | 1.0 | 1.0 | Tiles, player, enemies, projectiles, pickups |
| 5 | VFX layer | 1.0 | 1.0 | Sparks, beams, particles, telegraphs |
| 6 | HUD layer | 0.0 | 0.0 | UI, HUD, notifications |

Typography table:

| Use | Size |
| --- | ---: |
| Title logo | 64 px |
| World label | 28 px |
| Main menu button | 24 px |
| HUD text | 16 px |
| Notification text | 18 px |
| Stage name card | 40 px |
| Small UI text | 12 px |

UI shape grammar:

- Corner radius: 6 px.
- Border: 2 px.
- Panel background: `#0B1017` at 82 percent opacity.
- Primary border: `#4BE2FF`.
- Secondary border: `#3A4856`.
- Danger border: `#FF4F5A`.
- Text: `#D7DDE4`, unless highlighted.
- Button hover: cyan border, white text, 1 px upward shift.
- Confirm: 80 ms white flash.
- Deny: red border, 0.15 s horizontal shake, low deny sound.

Stage object grammar:

| Object | Visual meaning |
| --- | --- |
| Spike | Immediate damage, red tip |
| Conveyor | Movement aid, animated cyan arrows |
| One-way platform | Safe floor from below, cyan top edge |
| Moving platform | Temporary floor, rust slab, cyan edge |
| Wind zone | Visible force, cyan or pale streaks and arrows |
| Checkpoint | Safe respawn beacon |
| Core | Optional signal collectible |
| Signal Heart | Health |
| Tuner Shard | Weapon unlock |
| Conduit | Stage exit |

Visual rules that become gameplay rules:

- No bottom-center text notification for core collection.
- Cores are shown only by HUD counter flash.
- Boss telegraphs are world objects, not HUD-only warnings.
- Crosshair is hidden OS cursor in Stage state.
- Crosshair expands 14 px for 0.05 s on shoot.
- Crosshair dims to 50 percent when mouse leaves window.
- Keyboard fallback shows a small cyan facing arrow 16 px from player center.
- Damage vignette is `#FF4F5A`, alpha 0.35, duration 0.3 s.
- Player sprite flickers during invulnerability with alpha alternating 0.35 and 0.9 every 0.08 s.
- Lost heart pulses scale 1.2 for 0.4 s.
- Weapon slot deny shakes for 0.15 s with red border flash.
- Beam telegraph is dashed red or orange with edge arrows.
- Active beam is solid red or orange with white core.
- Beam width is 24 px.

# 4. GAMEPLAY SPEC

The game is a tight 2D side-scrolling platformer shooter called Signal Courier. Courier Jex races through a dying industrial city, restores communication nodes, and uses four tuned signal weapons to pass 10 stages across 2 worlds. Each stage requires reaching the Conduit. Boss stages require defeating the boss first. Optional Cores provide replay value and completion stats without blocking story progression.

## 4.1 Records with Rosters [T1]

World Roster:

| World | Name | Theme | Goal |
| --- | --- | --- | --- |
| 1 | Sumpworks | Lower industrial canal, rust, pipes, low ceilings, conveyors, pits, turrets | Restore lower relay by defeating Hush Warden |
| 2 | Skyloom | Floating market, vertical platforms, wind currents, wide gaps, open sightlines | Reach central Null Relay and silence final failure |

Stage Roster:

| Stage | Name | Size in Tiles | Focus | Target Time |
| --- | --- | ---: | --- | ---: |
| 1-1 | First Current | 75 x 12 | Tutorial | 45 s |
| 1-2 | Dredge Run | 95 x 12 | Moving platforms, conveyors | 70 s |
| 1-3 | Pressure Lock | 90 x 14 | Turrets, one-way platforms | 80 s |
| 1-4 | Rust Gallery | 105 x 12 | Crouching, drones, long low ceilings | 90 s |
| 1-5 | Hush Warden | 60 x 12 | Boss | 70 s |
| 2-1 | Lifted Bazaar | 80 x 20 | Vertical climb, wind | 80 s |
| 2-2 | Market Veils | 105 x 16 | One-way shelves, wraiths | 90 s |
| 2-3 | Windrace | 120 x 14 | Horizontal wind, timed platforms | 100 s |
| 2-4 | Highspire Ascent | 80 x 24 | Vertical pressure, golems | 110 s |
| 2-5 | Null Relay | 70 x 15 | Final boss | 120 s |

Target times are design goals, not enforced timers.

Weapon Roster:

| Slot | Weapon | Unlock Stage | Role |
| ---: | --- | --- | --- |
| 1 | Chirp | Start | Fast reliable default |
| 2 | Sifter | 1-2 | Close-range crowd control |
| 3 | Lance | 1-4 | Piercing high single-target damage |
| 4 | Bloom | 2-2 | Area control and tight-space damage |

Enemy Roster:

| Enemy | Type | Hitbox | Base HP | World 2 HP |
| --- | --- | ---: | ---: | ---: |
| Mite Crawler | Small ground swarm | 16 x 16 | 4 | 5 |
| Dredge Drone | Flying shooter | 24 x 20 | 10 | 12 |
| Pincer Bot | Melee charger | 24 x 24 | 18 | 21 |
| Warden Sentry | Stationary aimed turret | 32 x 32 | 30 | 35 |
| Mist Wraith | Flying phasing enemy | 24 x 24 | 22 | 25 |
| Bolt Golem | Large slow armored enemy | 48 x 48 | 60 | 69 |

Boss Roster:

| Boss | Stage | HP | Hitbox | Arena |
| --- | --- | ---: | ---: | ---: |
| Hush Warden | 1-5 | 180 | 64 x 64 | 36 x 12 tiles |
| Null Relay | 2-5 | 300 | 80 x 80 | 40 x 15 tiles |

Object Roster:

| Object | Size | Purpose |
| --- | ---: | --- |
| Conduit | 64 x 96 | Stage exit |
| Checkpoint | 32 x 48 | Respawn save |
| Core | 24 x 24 | Optional collectible |
| Signal Heart | 24 x 24 | Restores 1 heart |
| Tuner Shard | 32 x 48 | Unlocks one weapon |

Stage content roster:

| Stage | Purpose | Layout | Enemies | Pickups | Checkpoints | Exit |
| --- | --- | --- | --- | --- | --- | --- |
| 1-1 First Current | Teach movement, crouching, jumping, shooting | 0 to 15 flat start; 15 to 25 first spike cluster; 25 to 30 open corridor; 30 to 42 low ceiling passage requiring crouch; 42 to 48 small gap; 48 to 55 one-way platform above gap; 55 to 65 drone encounter; 65 to 70 small pit with mid platform; 70 to 75 conduit area | Mite Crawler x3: 2 near tile 25, 1 near tile 55; Dredge Drone x1 near tile 60 | Core 1 side alcove near tile 10; Core 2 inside low ceiling passage; Core 3 high ledge above gap; Signal Heart after checkpoint near tile 65 | Tile 40 | Conduit at tile 70 |
| 1-2 Dredge Run | Introduce moving platforms and conveyors; unlock Sifter | 0 to 15 start; 20 to 35 moving platforms over 8-tile pit; 35 to 50 conveyor belt; 50 to 70 drone corridor with low cover; 70 to 80 Pincer room; 80 to 90 second moving platform section; 90 to 95 conduit area | Dredge Drone x3: tiles 50, 60, 70; Mite Crawler x4: tiles 55, 60, 72, 78; Pincer Bot x1: tile 72 | Core 1 top of first moving platform; Core 2 spike corridor under conveyor; Core 3 high ledge before conduit; Signal Heart after checkpoint; Tuner Shard tile 85 unlocks Sifter | Tile 45 | Conduit at tile 92 |
| 1-3 Pressure Lock | Introduce Warden Sentry and one-way vertical pressure | 0 to 10 start; 10 to 20 short vertical shaft with one-way platforms; 20 to 35 low ceiling corridor; 35 to 50 Sentry alcove; 50 to 65 vertical moving pistons; 65 to 75 Pincer room; 75 to 85 second Sentry section; 85 to 90 conduit area | Warden Sentry x2: tiles 45 and 80; Pincer Bot x3: tiles 68, 72, 76; Dredge Drone x2: tiles 20 and 55 | Core 1 high ledge in vertical shaft; Core 2 behind low corridor; Core 3 on moving piston path; Signal Heart tile 55 | Tiles 35 and 60 | Conduit at tile 88 |
| 1-4 Rust Gallery | Emphasize crouching and long-range shooting; unlock Lance | 0 to 15 start; 15 to 35 long low ceiling gallery; 35 to 50 drone gap; 50 to 65 moving platforms; 65 to 80 conveyor and spike run; 80 to 95 Pincer charge corridor; 95 to 105 conduit area | Dredge Drone x4: tiles 30, 40, 55, 85; Pincer Bot x4: tiles 70, 80, 90, 95; Mite Crawler x4: tiles 35, 50, 65, 80 | Core 1 inside long low ceiling; Core 2 above moving platforms; Core 3 behind conveyor spike run; Signal Heart tile 70; Tuner Shard tile 98 unlocks Lance | Tiles 40 and 75 | Conduit at tile 102 |
| 1-5 Hush Warden | World 1 boss | 0 to 25 short gauntlet; 25 to 30 checkpoint; 30 to 58 boss arena; 58 to 60 conduit area; gauntlet has spike patch near tile 15, Sentry alcove near tile 20, two Mite Crawlers near tile 24; arena has flat floor, two side ledges, no moving platforms, no off-screen hazards | Warden Sentry x1 tile 20; Mite Crawler x2 tile 24; Hush Warden center of arena | Core 1 side alcove before boss; Core 2 high side ledge in arena; Core 3 appears above center during Phase 2 safe window; Signal Heart after checkpoint | Tile 30 before boss | Conduit locked until Hush Warden dies |
| 2-1 Lifted Bazaar | Introduce vertical climbing, updrafts, Mist Wraith | Bottom start vertical tiles 0 to 8; updraft column vertical tiles 10 to 20; one-way market shelves vertical tiles 20 to 35; drone corridor vertical tiles 35 to 45; mid checkpoint vertical tile 45; Wraith ledges vertical tiles 50 to 60; narrow top section vertical tiles 60 to 70; conduit at top vertical tile 72 | Dredge Drone x3: vertical tiles 35, 40, 45; Mist Wraith x2: vertical tiles 52 and 58; Pincer Bot x2: vertical tiles 25 and 60 | Core 1 inside updraft column; Core 2 hidden side shelf; Core 3 high ledge before conduit; Signal Heart mid checkpoint area | Vertical tile 45 | Conduit at top |
| 2-2 Market Veils | Introduce horizontal wind gusts and one-way shelf loops; unlock Bloom | 0 to 15 start; 20 to 30 left-push wind over 6-tile pit; 30 to 50 one-way market shelves; 50 to 65 Sentry row; 65 to 85 vertical loop with one-way platforms; 85 to 95 Wraith corridor; 95 to 105 conduit area | Warden Sentry x3: tiles 55, 60, 65; Mist Wraith x4: tiles 70, 75, 85, 90; Mite Crawler x4: tiles 35, 40, 80, 85 | Core 1 inside wind gust; Core 2 top of vertical loop; Core 3 low crouch under shelf; Signal Heart mid-stage; Tuner Shard tile 95 unlocks Bloom | Tile 45 | Conduit at tile 100 |
| 2-3 Windrace | Introduce Bolt Golem and stronger wind pressure | 0 to 15 start; 20 to 30 right-push wind; 30 to 50 moving platforms; 50 to 70 Sentry and Wraith mixed section; 70 to 85 strong left-push wind; 85 to 100 Golem chamber; 100 to 115 final run; 115 to 120 conduit area | Warden Sentry x3: tiles 55, 60, 90; Mist Wraith x4: tiles 50, 75, 85, 95; Bolt Golem x2: tiles 90 and 100 | Core 1 inside strong wind zone; Core 2 on moving platform; Core 3 side chamber near golem area; Signal Heart tile 75 | Tiles 40 and 80 | Conduit at tile 115 |
| 2-4 Highspire Ascent | Final non-boss stage, high vertical pressure | Bottom start vertical tiles 0 to 8; updraft vertical tiles 10 to 18; narrow ledges vertical tiles 18 to 35; Golem ledge vertical tiles 35 to 45; mid checkpoint vertical tile 45; crosswind section vertical tiles 50 to 65; Wraith shaft vertical tiles 65 to 75; conduit vertical tile 78 | Warden Sentry x4: vertical tiles 20, 30, 45, 60; Bolt Golem x2: vertical tiles 35 and 50; Mist Wraith x6: vertical tiles 25, 40, 55, 65, 70, 75 | Core 1 hidden ledge; Core 2 inside updraft; Core 3 high ledge before conduit; Signal Heart mid checkpoint | Vertical tiles 45 and 60 | Conduit at top |
| 2-5 Null Relay | Final boss and game completion | 0 to 20 short gauntlet; 20 to 30 checkpoint; 30 to 65 boss arena; 65 to 70 end area; gauntlet has spike patch near tile 10, Mist Wraiths near tiles 15 and 18, Bolt Golem near tile 20; arena has wide floor, two side ledges, no moving platforms, no off-screen hazards | Mist Wraith x2: tiles 15 and 18; Bolt Golem x1: tile 20; Null Relay center of arena | Core 1 pre-boss alcove; Core 2 side ledge in arena; Core 3 appears during Phase 3 Core Exposed window; Signal Heart after checkpoint | Tile 30 before boss | Conduit locked until Null Relay dies; after death and conduit, go to End |

## 4.2 Game States [T1]

| State | Purpose |
| --- | --- |
| Title | Start, continue, new game, controls |
| Intro | Short story setup |
| Signal Map | World and stage selection |
| Stage | Main gameplay |
| Pause | Pause stage and offer restart, title, map |
| Stage Summary | Show stage results and continue |
| Game Over | Lives exhausted; retry stage or title |
| End | Final boss complete; show run stats |

State flow:

- Title to Intro for new game.
- Intro to Signal Map.
- Signal Map to Stage for unlocked stages.
- Stage to Stage Summary after non-final completion.
- Stage Summary to Signal Map or next stage.
- Stage to Game Over when lives reach 0.
- Game Over to Stage retry, Signal Map, or Title.
- Stage to End after final completion.
- End to Signal Map or Title.

Title rules:

- If no progress exists, show Begin Signal.
- If progress exists, show Continue at the furthest unlocked uncompleted stage.
- If progress exists, show New Signal, which resets all progress.
- Show Controls.
- If all stages are completed and no uncompleted unlocked stage exists, Continue is hidden and Title offers Map.

Intro rules:

- Show 4 short story cards.
- Each card can be skipped with Enter, Space, or mouse click.
- After intro, go to Signal Map.

Signal Map rules:

- Show 2 worlds.
- Each world shows 5 stages.
- Stage states are Locked, Unlocked, Completed.
- Only unlocked stages can be started.
- Completed stages can be replayed.
- World 2 is locked until World 1 Stage 5 is completed.
- After final completion, the map remains available for replay.

Stage Summary rules:

- Shown after non-final stage completion.
- Display stage name, time, deaths in stage, cores collected in stage, total cores collected.
- Buttons are Continue and Signal Map.
- Continue proceeds to the next unlocked stage.
- Signal Map returns to map.

Game Over rules:

- Shown when lives reach 0.
- Display Signal Lost.
- Buttons are Retry Stage, Signal Map, Title.

End rules:

- Shown after World 2 Stage 5.
- Display Signal Restored.
- Display total time, total deaths, total cores collected out of 30.
- Buttons are Signal Map and Title.

## 4.3 Controls and Aiming [T1]

- Movement is keyboard.
- Aiming is mouse primary.
- J is keyboard fallback.
- Crouch is held.
- Jump is edge or held with variable cut.
- Weapon switch is by slot or cycle.
- Pause is only available during Stage state.

Aim vector:

- Mouse aim:
  - Convert mouse screen position to world position.
  - Aim vector is mouse world position minus muzzle origin.
  - Normalize aim vector.
  - If aim vector length is near zero, use last facing direction.
- Keyboard fallback:
  - Aim vector is right if facing right.
  - Aim vector is left if facing left.
  - Muzzle origin is adjusted for crouch height.

Muzzle origin ruling:

- `feetY = player.y + player.h`
- `baseY = feetY - 12`
- `centerX = player.x + player.w / 2`
- `muzzleY = baseY + (crouching ? 8 : 2)`
- Standing muzzle is 10 px above feet.
- Crouched muzzle is 4 px above feet.
- If aim is mostly horizontal:
  - `muzzleX = centerX + 14 * sign`
- If aim is mostly vertical:
  - `muzzleX = centerX`
- `mostlyHorizontal = Math.abs(aimX) >= Math.abs(aimY)`
- `sign = aimX !== 0 ? Math.sign(aimX) : player.facing`

Weapon switch rules:

- Weapons 1 through 4 can be selected only if unlocked.
- Attempting to select a locked weapon produces UI deny and no weapon change.
- Switching weapons sets universal weapon-switch cooldown of 0.12 seconds.
- Each weapon has its own fire cooldown.
- The player cannot shoot while the universal weapon-switch cooldown is active.

## 4.4 Player System [T1]

Player hitbox:

| State | Width | Height |
| --- | ---: | ---: |
| Standing | 16 px | 24 px |
| Crouching | 16 px | 12 px |

Feet are aligned to the bottom of the hitbox.

Player health:

- Player has 5 signal hearts.
- Each heart is 1 unit of health.
- All enemy contact, enemy projectiles, hazards, boss attacks, and pits deal 1 heart damage.
- When hearts reach 0, the player dies.
- After death, the player loses 1 life and respawns.

Player lives:

- Player starts each stage with 3 lives.
- If lives reach 0, show Game Over.
- On stage retry, lives reset to 3.
- On death with lives remaining, respawn at last checkpoint with full hearts.

Damage and invulnerability:

- When player takes damage:
  - Lose 1 heart.
  - Enter invulnerability for 1.0 seconds.
  - Apply horizontal knockback 280 px/s away from damage source.
  - Apply vertical knockback -240 px/s upward.
  - Player remains in control during invulnerability.
  - Enemy contact and enemy projectiles do not deal damage again during invulnerability.
  - Hazards do not deal damage again during invulnerability.

Death rules:

- If player dies:
  - If lives are greater than 0:
    - Lose 1 life.
    - Respawn at last checkpoint.
    - Restore hearts to 5.
    - Enter 1.0 second invulnerability.
  - If lives are 0:
    - Show Game Over.

Checkpoint respawn:

- Checkpoints are required every stage.
- When a checkpoint is activated:
  - Set respawn point.
  - Restore 1 heart if below 5.
  - Show checkpoint HUD notification.
  - Play checkpoint sound.
- If player dies and no checkpoint has been activated:
  - Respawn at stage start.

Checkpoint respawn position:

- Checkpoint size is 32 x 48.
- Respawn player top-left is:
  - `x = checkpoint.x + 8`
  - `y = checkpoint.y + 24`

Pit rule:

- If player falls below stage boundary by 64 pixels:
  - Take 1 heart damage.
  - Teleport to last checkpoint.
  - If no checkpoint exists, teleport to stage start.
  - Enter invulnerability for 0.5 seconds.
- If player has 0 hearts from a pit:
  - Trigger normal death.

## 4.5 Movement System [T1]

Movement numbers:

| Parameter | Value |
| --- | ---: |
| Ground max speed | 240 px/s |
| Crouched max speed | 120 px/s |
| Air max speed | 240 px/s |
| Ground acceleration | 2800 px/s² |
| Air acceleration | 1900 px/s² |
| Ground friction | 2800 px/s² |
| Air friction | 400 px/s² |
| Gravity | 1800 px/s² |
| Max fall speed | 1100 px/s |
| Initial jump velocity | -640 px/s |
| Jump cut velocity | -320 px/s |
| Coyote time | 0.09 seconds |
| Jump buffer | 0.10 seconds |

Movement algorithm:

Each fixed timestep:

1. Read horizontal input.
2. Determine target horizontal velocity:
   - `targetVX = maxSpeed * inputX`
3. Accelerate or decelerate toward `targetVX`.
4. Apply gravity unless the player is in an updraft zone.
5. Clamp fall speed.
6. Handle jump input.
7. Integrate X and resolve horizontal collision.
8. Integrate Y and resolve vertical collision.
9. Apply moving platform carry.
10. Apply conveyor and wind effects.
11. Update hitbox if crouch state changes.

Jump algorithm:

- Player can jump if:
  - Jump input was pressed within the last 0.10 seconds.
  - Player is grounded or within 0.09 seconds of leaving ground.
- On jump:
  - Set vertical velocity to -640 px/s.
  - Clear jump buffer.
- Variable jump:
  - If player releases jump while moving upward faster than -320 px/s, set vertical velocity to -320 px/s.

Crouch algorithm:

- Crouch is held.
- Crouching reduces height to 12 px.
- Crouching reduces max horizontal speed to 120 px/s.
- Player can jump while crouched.
- Player can shoot while crouched.
- Muzzle origin is lowered to match crouch height.
- Crouching is allowed in air.
- Standing requires 24 px vertical clearance.
- If standing is blocked, player remains crouched.

No double jump:

- The player does not have a double jump.
- Jump height and gap distance are calibrated for a single jump.
- Crouching and aiming provide mechanical variety.
- No double jump keeps platforming legible.

## 4.6 Collision System [T1]

The game uses tile-based collision.

Tile behavior:

| Tile or Object | Behavior |
| --- | --- |
| Solid tile | Blocks player, enemies, and projectiles |
| One-way platform | Blocks player only from below; projectiles pass through |
| Spike | Damages player on contact |
| Conveyor tile | Solid tile that adds horizontal velocity to grounded player |
| Wind zone | Invisible or visible force field that applies acceleration |
| Checkpoint | Triggers respawn save |
| Core | Optional collectible |
| Heart | Restores 1 heart if below max |
| Tuner | Unlocks a weapon |
| Conduit | Stage exit |

Player collision rules:

- Player collides with solid tiles.
- Player can land on one-way platforms.
- Player can pass upward through one-way platforms.
- Player cannot pass through solid tiles.
- Moving platforms push the player if the player is standing on them.

One-way platform landing rule:

- A one-way platform is solid only if:
  - Player is moving downward.
  - Player’s previous bottom was at or above the platform’s top.
  - Player is not jumping through.
- Projectiles ignore one-way platforms.
- One-way platform visual size is 32 x 8.
- Collision top is the top of the tile.

Moving platform rules:

- Moving platforms follow linear waypoint paths.
- If player is standing on a moving platform:
  - Apply platform position delta to player each timestep.
  - Maintain player foot offset relative to platform.
- If platform moves off-screen or resets on stage retry, player is no longer carried.
- Projectiles pass through moving platforms.
- Enemies do not ride moving platforms.
- Platform reset happens on stage reset.

Conveyor rules:

- Conveyor tiles apply horizontal speed offset only while player is grounded.
- Right conveyor adds 120 px/s horizontal offset.
- Left conveyor subtracts 120 px/s horizontal offset.
- Total horizontal speed while on conveyor can be clamped to plus or minus 360 px/s.

Wind zone rules:

- Wind zones apply acceleration to player while player hitbox intersects zone.
- Wind does not affect enemies unless specifically stated.
- Multiple overlapping wind zones sum accelerations before clamping.

| Wind Type | Acceleration | Clamp |
| --- | ---: | --- |
| Updraft | -2400 px/s² vertical | Vertical speed minimum -420 px/s |
| Horizontal gust right | +1600 px/s² horizontal | Horizontal speed maximum +360 px/s |
| Horizontal gust left | -1600 px/s² horizontal | Horizontal speed minimum -360 px/s |

Low clearance volumes:

- `lowClearance` rectangles are required for crouch-only passages.
- They block player when standing.
- They do not block player when crouching.
- They do not damage the player.
- They do not block projectiles.
- They do not block enemies.
- They do not block beams.
- If player hitbox is 16 x 24 and intersects a low clearance rectangle, resolve as solid.
- If player hitbox is 16 x 12 and does not intersect, pass through.

Spike volumes:

- Up spikes occupy lower 16 px of tile.
- Down spikes occupy upper 16 px of tile.
- Spike contact deals 1 heart damage.
- Spike size is 32 x 16.

## 4.7 Camera System [T1]

Camera follows player.

Camera rules:

- Logical viewport is 960 x 540.
- Camera smoothing: `camera += (target - camera) * min(1, 8 * dt)`
- Horizontal lookahead:
  - If moving right: plus 120 px.
  - If moving left: minus 120 px.
  - If idle: 0 px.
- Vertical target:
  - Player center Y minus 32 px.
- Camera is clamped to stage bounds when stage dimension is larger than viewport.
- Camera is centered on an axis when stage dimension is smaller than viewport.
- Background layers fill extra space.

Camera target:

- `playerCenterX = player.x + player.w / 2`
- `playerCenterY = player.y + player.h / 2`
- `lookahead = 0`
- If input right, `lookahead = 120`.
- If input left, `lookahead = -120`.
- `targetX = playerCenterX - 480 + lookahead`
- `targetY = playerCenterY - 32 - 270`

Clamp and center:

- If stage width is greater than 960, clamp camera X between 0 and stage width minus 960.
- If stage width is less than 960, center camera X at `(stage width - 960) / 2`.
- If stage height is greater than 540, clamp camera Y between 0 and stage height minus 540.
- If stage height is less than 540, center camera Y at `(stage height - 540) / 2`.

Camera feel:

- Camera should feel stable during jumps.
- Camera should not pan faster than player.
- Camera should not show outside stage bounds when stage is larger than viewport.

## 4.8 Weapons [T1]

Player has 4 gun types. Weapons are permanent unlocks. Once unlocked, they are available in all future stages and replays.

Weapon slots:

| Slot | Weapon | Unlock Stage |
| ---: | --- | --- |
| 1 | Chirp | Start |
| 2 | Sifter | 1-2 |
| 3 | Lance | 1-4 |
| 4 | Bloom | 2-2 |

Weapon switching:

- Selecting an unlocked weapon changes active weapon.
- Selecting a locked weapon does nothing except UI deny.
- Switching weapons sets universal shoot cooldown of 0.12 seconds.
- Weapon-specific fire cooldowns continue independently.
- Cycling forward advances through unlocked weapons only.
- Cycling wraps from last unlocked to first unlocked.

## 4.9 Weapon Details [T1]

Chirp:

| Parameter | Value |
| --- | ---: |
| Damage | 7 |
| Fire interval | 0.15 seconds |
| Projectile speed | 950 px/s |
| Projectile lifetime | 0.7 seconds |
| Projectile radius | 4 px |
| Projectiles per shot | 1 |
| Spread | 0 degrees |
| Pierce | None |
| Enemy knockback | 80 px/s |

Best use:

- General combat.
- Medium distance.
- Single enemies.

Sifter:

| Parameter | Value |
| --- | ---: |
| Damage per pellet | 4 |
| Fire interval | 0.55 seconds |
| Projectile speed | 720 px/s |
| Projectile lifetime | 0.35 seconds |
| Projectile radius | 3 px |
| Projectiles per shot | 5 |
| Spread angles | -8, -4, 0, +4, +8 degrees |
| Pierce | None |
| Enemy knockback per pellet | 60 px/s |

Best use:

- Swarms.
- Tight corridors.
- Enemies at close range.

Lance:

| Parameter | Value |
| --- | ---: |
| Damage | 24 |
| Fire interval | 0.62 seconds |
| Projectile speed | 1500 px/s |
| Projectile lifetime | 0.8 seconds |
| Projectile radius | 5 px |
| Projectiles per shot | 1 |
| Spread | 0 degrees |
| Pierce | 3 total enemies |
| Enemy knockback | 260 px/s |

Best use:

- Groups in a line.
- Bosses.
- Ranged enemies.

Lance pierce algorithm:

- Lance projectile can hit up to 3 enemies total.
- It stores the set of enemy IDs it has already hit.
- On enemy hit:
  - If enemy already in hit set, do nothing.
  - Add enemy to hit set.
  - Apply damage and knockback.
  - If hit set size is less than 3, projectile continues.
  - If hit set size is 3, projectile is destroyed.

Bloom:

| Parameter | Value |
| --- | ---: |
| Main damage | 12 |
| Shard damage | 6 |
| Fire interval | 1.0 second |
| Main projectile speed | 520 px/s |
| Main projectile lifetime | 0.45 seconds |
| Main projectile radius | 8 px |
| Shard speed | 620 px/s |
| Shard lifetime | 0.5 seconds |
| Shard radius | 4 px |
| Shards produced | 3 |
| Shard angles relative to main | -25, 0, +25 degrees |
| Split condition | On first enemy hit or after 0.45 seconds |
| Main enemy knockback | 180 px/s |
| Shard enemy knockback | 80 px/s |

Best use:

- Crowded rooms.
- Enemies partially behind cover.
- Boss pressure.

Bloom algorithm:

- Main projectile does not split on tile collision; it is destroyed.
- If main projectile hits an enemy:
  - Apply main damage.
  - Destroy main projectile.
  - Spawn 3 shards at hit location.
- If main projectile reaches lifetime without hitting an enemy:
  - Destroy main projectile.
  - Spawn 3 shards at current position.
- Shards do not split further.

## 4.10 Projectile System [T1]

All player and enemy projectiles:

- Are circular hitboxes.
- Move in straight lines unless affected by a stated special behavior.
- Are destroyed on solid tile collision.
- Have a lifetime.
- Deal damage only to the intended target group.
- Do not damage their owner.

Projectile collision order:

Each timestep, process projectiles in creation order:

1. Move projectile.
2. Check solid tile collision.
3. Check target collision.
4. Apply damage, knockback, or special behavior.
5. Remove projectile if lifetime expired, tile hit, or behavior destroyed it.

Projectile substeps:

- Distance moved per step is `speed * dt`.
- Substep size is 16 px.
- Segments are `max(1, ceil(distance / 16))`.
- Each segment checks tile collision.
- This prevents high-speed Lance projectiles from tunneling through tiles or enemies.

Tile collision:

- Projectile circle is expanded by radius against solid tile AABBs.
- One-way platforms are ignored.
- Low clearance is ignored.
- Moving platforms are ignored.

Lifetime:

- `age += dt`
- If `age >= lifetime`, remove projectile or apply Bloom split if applicable.

Entity limits:

- Maximum player projectiles: 80.
- Maximum enemy projectiles: 120.
- If limit is exceeded, oldest projectile expires.

## 4.11 Enemy System [T1]

Enemies activate when player enters activation radius.

Activation rules:

- Activation radius: 10 tiles, which is 320 px.
- Enemies do not act before activation.
- Once activated, enemies remain active until they die, become dormant, or stage reset.
- Maximum active enemies per stage: 16.
- If more than 16 are within radius, activate the 16 closest to player.
- If active count exceeds 16 due to summons, farthest active enemy beyond 320 px becomes dormant.
- Dormant enemies stop acting.
- Dormant enemies do not count as active.
- Dormant enemies can reactivate when space is available.

Enemy damage:

- All enemy attacks deal 1 heart to player.
- If player is invulnerable, no damage.
- If enemy is phased or intangible, no contact damage to player.

Enemy line of sight:

- Ranged enemies require line of sight before attacking.
- Sample line between enemy attack point and player center every 4 pixels.
- If any sample intersects a solid tile, line of sight is blocked.
- One-way platforms do not block line of sight.

Enemy death:

- Remove enemy.
- Clear enemy-owned projectiles.
- Play enemy death audio.
- Emit enemy death VFX.
- If Bolt Golem, spawn 1 Signal Heart at its center.

Mite Crawler:

| Parameter | Value |
| --- | ---: |
| Hitbox | 16 x 16 px |
| HP | 4 |
| Contact damage | 1 heart |
| Move speed | 90 px/s |
| Attack | Contact only |
| World 2 HP | 5 |

Behavior:

- If player is within 5 tiles, move toward player.
- Does not jump.
- Stops and waits 0.5 seconds if blocked by solid geometry.
- Dies to 1 Chirp shot.

Stage use:

- Tutorial enemies.
- Swarm pressure.
- Easy Sifter targets.

Dredge Drone:

| Parameter | Value |
| --- | ---: |
| Hitbox | 24 x 20 px |
| HP | 10 |
| Contact damage | 1 heart |
| Move speed | 120 px/s |
| Fire interval | 1.6 seconds |
| Projectile speed | 350 px/s |
| Projectile lifetime | 2.5 seconds |
| Projectile radius | 6 px |
| Attack range | 6 tiles |
| World 2 HP | 12 |
| World 2 projectile speed | 385 px/s |

Behavior:

- Patrols horizontally within 4 tiles of spawn.
- Adds vertical sine offset of 12 px.
- If player is within attack range and has line of sight:
  - Hover.
  - Fire straight projectile toward player.
- Collides with solid tiles but ignores one-way platforms.

Stage use:

- Aerial spacing.
- Forces jump timing.
- Good for Lance.

Pincer Bot:

| Parameter | Value |
| --- | ---: |
| Hitbox | 24 x 24 px |
| HP | 18 |
| Contact damage | 1 heart |
| Walk speed | 130 px/s |
| Charge speed | 420 px/s |
| Charge duration | 0.35 seconds |
| Telegraph time | 0.5 seconds |
| Attack range | 4 tiles |
| Cooldown | 1.5 seconds |
| World 2 HP | 21 |

Behavior states:

1. Idle:
   - Wanders slowly near spawn.
2. Telegraph:
   - If player is within attack range and has line of sight:
     - Stop.
     - Shake.
     - Show charge telegraph.
3. Charge:
   - Dash toward player’s current position.
   - Stop on solid collision or after charge duration.
4. Cooldown:
   - Cannot charge again until cooldown ends.

Stage use:

- Teaches reaction and spacing.
- Punishes standing still.
- Can be dodged by crouch or jump.

Warden Sentry:

| Parameter | Value |
| --- | ---: |
| Hitbox | 32 x 32 px |
| HP | 30 |
| Contact damage | 1 heart |
| Aim speed | 3 radians/second |
| Burst shots | 2 |
| Burst gap | 0.15 seconds |
| Fire cooldown | 2.6 seconds |
| Projectile speed | 520 px/s |
| Projectile lifetime | 1.5 seconds |
| Projectile radius | 6 px |
| Attack range | 8 tiles |
| World 2 HP | 35 |
| World 2 projectile speed | 572 px/s |

Behavior:

- Stationary.
- If player is within range and has line of sight:
  - Aim at player.
  - When aim is within 10 degrees of player, fire 2-round burst.
- If no line of sight:
  - Slowly return aim to last known angle.
  - If no last known angle, face right.

Stage use:

- Forces movement and cover usage.
- Good for Lance or Bloom.

Mist Wraith:

| Parameter | Value |
| --- | ---: |
| Hitbox | 24 x 24 px |
| HP | 22 |
| Contact damage | 1 heart |
| Move speed | 180 px/s |
| Phase interval | 2.5 seconds |
| Phase duration | 0.8 seconds |
| Sine offset | 30 px |
| World 2 HP | 25 |

Behavior:

- Flies toward player with vertical sine motion.
- Collides with solid tiles but ignores one-way platforms.
- Every 2.5 seconds:
  - Becomes intangible for 0.8 seconds.
  - While phased:
    - Player projectiles pass through.
    - Player contact does no damage to enemy.
    - Enemy contact does no damage to player.
  - Returns to normal.

Stage use:

- Teaches timing.
- Rewards burst damage.
- Good for Chirp and Lance timing.

Bolt Golem:

| Parameter | Value |
| --- | ---: |
| Hitbox | 48 x 48 px |
| HP | 60 |
| Contact damage | 1 heart |
| Move speed | 60 px/s |
| Heavy bolt interval | 3.0 seconds |
| Heavy bolt speed | 300 px/s |
| Heavy bolt lifetime | 3.0 seconds |
| Heavy bolt radius | 10 px |
| Attack range | 8 tiles |
| Stomp interval | 4.0 seconds |
| Stomp range | 3 tiles |
| World 2 HP | 69 |
| World 2 heavy bolt speed | 330 px/s |

Behavior:

- Moves toward player if within 8 tiles.
- Does not jump.
- If player is within range and has line of sight:
  - Fires a heavy straight bolt toward player.
- If player is within stomp range:
  - Telegraph 0.4 seconds.
  - Stomps.
  - Spawns 2 temporary ground spike patches in front of itself for 2 seconds.
- Drops 1 Signal Heart on death.

Stage use:

- Late-stage pressure.
- Requires patience.
- Good for Lance and Bloom.

## 4.12 Boss System [T1]

Boss stages have a boss. Boss is inactive until player enters boss trigger or arena. Once active, boss remains active until death or stage reset. If player dies with lives remaining, boss resets to full HP and idle. Summons are cleared.

Boss damage:

- Player projectiles can damage boss unless boss is dying.
- Contact with boss deals 1 heart.
- Boss projectiles and beams deal 1 heart.
- If player is invulnerable, no damage.

Boss death:

- Set dying.
- Stop all attacks.
- Remove boss-owned projectiles.
- Remove active beams.
- Remove summoned enemies.
- Make boss invulnerable.
- Run death sequence.
- Unlock conduit.

Hush Warden:

Location: Stage 1-5.

| Parameter | Value |
| --- | ---: |
| HP | 180 |
| Hitbox | 64 x 64 px |
| Contact damage | 1 heart |
| Boss projectile damage | 1 heart |
| Arena size | 36 x 12 tiles |
| Base move speed | 80 px/s |
| Phase 2 move speed | 88 px/s |

Phases:

| Phase | HP range |
| --- | --- |
| 1 | 100 percent to 60 percent |
| 2 | 60 percent to 0 percent |

Attack selection:

- Among ready attacks, choose lowest remaining cooldown.
- Tie priority:
  - Charge
  - Fan Bolt
  - Sweep Beam
  - Drone Summon

Charge:

- Cooldown: 6 seconds.
- Telegraph: 0.6 seconds.
- Dash horizontally toward player at 480 px/s.
- Duration: 1.2 seconds.
- Leaves 4 spike patches along path.
- Spike patches last 3 seconds.
- Spike patch placement:
  - Spawn at fractional distances along actual dash path: 25 percent, 50 percent, 75 percent, 100 percent.
  - Each patch is 32 x 16.
  - Patches snap to floor below path point.
  - If no floor exists at a sample, skip that patch.
  - Patch warning is 0.2 seconds.

Fan Bolt:

- Cooldown: 4 seconds.
- Fires 3 projectiles.
- Angles: -20, 0, +20 degrees.
- Projectile speed: 380 px/s.
- Projectile lifetime: 2.0 seconds.
- Projectile radius: 6 px.

Sweep Beam:

- Phase 2 only.
- Cooldown: 7 seconds.
- Telegraph: 0.8 seconds.
- Beam height: player Y at telegraph start.
- Beam width: 24 px.
- Beam duration: 0.7 seconds.
- Beam spans boss arena width.

Drone Summon:

- Phase 2 only.
- Cooldown: 10 seconds.
- Summons 2 Dredge Drones.
- Maximum active Dredge Drones: 3.
- Summoned drones use normal Dredge Drone behavior.
- If max is reached, summon is skipped.

Hush Warden death:

- Stop all attacks.
- Play 2-second death sequence.
- Boss hitbox becomes inactive.
- Conduit unlocks.
- Stage complete when player reaches Conduit.

Null Relay:

Location: Stage 2-5.

| Parameter | Value |
| --- | ---: |
| HP | 300 |
| Hitbox | 80 x 80 px |
| Contact damage | 1 heart |
| Boss projectile damage | 1 heart |
| Beam damage | 1 heart |
| Arena size | 40 x 15 tiles |

Phases:

| Phase | HP range |
| --- | --- |
| 1 | 100 percent to 70 percent |
| 2 | 70 percent to 35 percent |
| 3 | 35 percent to 0 percent |

Phase 2 and Phase 3 begin with a 1.5-second warning.

During warning:

- Boss does not attack.
- Boss is stationary or slowly moves to warning position.
- HUD shows phase warning.
- Boss warning audio plays.

Phase 1:

Rain:

- Interval: 1.5 seconds.
- Spawns vertical projectiles from 3 columns.
- Columns are chosen deterministically using stage RNG.
- Projectile speed: 420 px/s downward.
- Projectile lifetime: 2.0 seconds.
- Visual is 12 x 24 vertical shards.

Side Sweep:

- Cooldown: 6 seconds.
- Telegraph: 0.8 seconds.
- Horizontal beam at random Y chosen at telegraph start.
- Beam width: 24 px.
- Beam duration: 0.8 seconds.
- Beam spans arena width.

Movement:

- Moves horizontally at 60 px/s.

Phase 2:

Echo Shot:

- Cooldown: 4 seconds.
- Fires 3 projectiles toward player.
- Projectile speed: 520 px/s.
- Projectile lifetime: 2.0 seconds.
- Each projectile bounces once off arena walls.
- Bounce is reflected velocity.
- Projectile is destroyed after one bounce or if it hits solid geometry.

Wraith Summon:

- Cooldown: 12 seconds.
- Summons 2 Mist Wraiths.
- Maximum active Mist Wraiths: 4.
- If max is reached, summon is skipped.

Movement:

- Moves in small zigzag.
- Speed: 90 px/s.
- Vertical sine offset: 40 px.
- Sine period: 2.0 seconds.

Phase 3:

Overload Cycle:

Repeat until death:

1. Horizontal beam:
   - Telegraph: 0.6 seconds.
   - Duration: 0.6 seconds.
   - Beam Y locked to player Y at telegraph start.
2. Vertical beam:
   - Telegraph: 0.6 seconds.
   - Duration: 0.6 seconds.
   - Beam X locked to player X at telegraph start.
3. Core Exposed:
   - Boss becomes stationary.
   - Duration: 1.5 seconds.
   - All player damage to boss is multiplied by 1.5.
   - Boss cannot attack.

Null Relay death:

- Stop all attacks.
- Play 3-second death sequence.
- Show end state after player reaches Conduit or automatically after death sequence if Conduit is active.

Beam rules:

- Beam damage is 1 heart.
- Beam does not collide with tiles.
- Beam passes through one-way platforms.
- Beam passes through low clearance.
- Beam is removed when active time ends.
- Telegraph state has no damage.
- Active state damages player on overlap.
- Telegraph position is locked at telegraph start.
- If player moves during telegraph, beam does not follow.
- Exception: Null Relay Phase 1 Side Sweep uses a random valid arena Y chosen at telegraph start, then locks that displayed line.

## 4.13 Stage Objects [T1]

Conduit:

- Size: 64 x 96 px.
- Non-boss stages:
  - Activates when player overlaps it.
- Boss stages:
  - Inactive until boss dies.
  - Activates when player overlaps it after boss death.
- On activation:
  - Stop player input.
  - Play stage complete sequence.
  - Show Stage Summary or End state.

Checkpoint:

- Size: 32 x 48 px.
- Triggers once when player overlaps.
- Sets respawn point.
- Restores 1 heart if below max.
- Visual and audio feedback.

Core:

- Size: 24 x 24 px.
- Optional.
- 3 per stage.
- Once collected, global flag persists.
- On stage load or retry, already collected cores are not spawned.
- HUD updates total cores.

Signal Heart:

- Size: 24 x 24 px.
- Collects only if player hearts are below 5.
- If player hearts are already 5, the heart remains in the world.
- Restores 1 heart.

Tuner Shard:

- Size: 32 x 48 px.
- Unlocks one weapon.
- Once collected, weapon unlock persists globally.
- On stage load or retry, already collected tuners are not spawned.
- Shows unlock notification.

Tuner placement:

- `w1s2` has exactly one tuner for Sifter.
- `w1s4` has exactly one tuner for Lance.
- `w2s2` has exactly one tuner for Bloom.
- No other stage may have a tuner.

## 4.14 Progression and Difficulty [T1]

Weapon progression:

| Unlock | Stage | Weapon |
| --- | --- | --- |
| Start | None | Chirp |
| Stage 1-2 | Tuner Shard | Sifter |
| Stage 1-4 | Tuner Shard | Lance |
| Stage 2-2 | Tuner Shard | Bloom |

Stage unlocking:

- Stage 1-1 is always unlocked at New Signal.
- Completing a stage unlocks the next stage.
- Completing 1-5 unlocks World 2.
- Completing 2-5 completes the game.
- Completed stages can be replayed from Signal Map.

Core progression:

- 3 cores per stage.
- 30 total cores.
- Cores are optional.
- Cores persist once collected.
- Cores do not affect gameplay outside stats.

Life progression:

- Lives reset to 3 at the start of each stage.
- Lives do not carry between stages.

World 1 difficulty:

- Teaches core systems.
- Enemies have base HP.
- Hazards are predictable.
- Boss has 180 HP.

World 2 difficulty:

- Standard enemy HP multiplied by 1.15, rounded up.
- Standard enemy projectile speed multiplied by 1.1.
- More vertical movement.
- More wind interference.
- More ranged pressure.
- Bosses use their defined HP and projectile speeds without additional standard-enemy modifiers.

Fairness rules:

- No unavoidable damage.
- Boss attacks have telegraphs.
- No enemy attacks from off-screen without warning.
- No hazards activate without visible or audible cue.
- Checkpoints are placed before major hazard or boss sections.
- Gaps are never wider than 4 tiles.
- Jump height is sufficient to cross all required gaps.

Entity limits:

| Limit | Value |
| --- | ---: |
| Active enemies | 16 |
| Player projectiles | 80 |
| Enemy projectiles | 120 |
| Temporary spike patches | 20 |
| Active summoned boss enemies | 4 |

Overflow rules:

- If player projectiles exceed 80, expire oldest.
- If enemy projectiles exceed 120, expire oldest.
- If temporary spike patches exceed 20, remove oldest.
- If active enemies exceed 16, make farthest active enemy beyond 320 px dormant.

## 4.15 Stage Reset [T1]

On stage retry or Game Over retry:

- Player position resets to stage start.
- Hearts reset to 5.
- Lives reset to 3.
- Checkpoints reset.
- Enemies reset.
- Enemy projectiles reset.
- Player projectiles reset.
- Moving platforms reset.
- Wind zones reset.
- Boss resets if present.
- Beams reset.
- Temporary spikes reset.
- Uncollected stage Cores remain uncollected.
- Already globally collected Cores remain collected.
- Already globally unlocked weapons remain unlocked.
- Already globally collected Tuners remain collected.
- Global progression stats persist.

Death respawn rule:

When the player dies with lives remaining:

1. Decrement lives.
2. Restore hearts to 5.
3. Reset dynamic stage state.
4. Teleport player to last checkpoint or stage start.
5. Enter invulnerability 1.0 seconds.

Boss reset on death:

- If player dies during boss with lives remaining:
  - Respawn at checkpoint before boss.
  - Boss resets to full HP and idle.
  - Summons are cleared.

## 4.16 Feel [T1]

- Movement must feel snappy and fair.
- Weapons must have clear mechanical identity.
- Damage must be avoidable if the player watches telegraphs and stage layout.
- Player must always know the next objective: reach the Conduit.
- Cores provide optional completion value.
- No damage numbers.
- No minimap.
- No score.
- No permanent death.
- No weapon upgrades.
- No armor power-up.
- No health overcap.
- No touch controls.
- No 3D gameplay.
- No Z-axis depth.
- No camera rotation.
- No par time or star rating.
- No shops.
- No crafting.
- No side characters outside story text.

# 5. CHARACTERS

## 5.1 Courier Jex

Silhouette:

- Compact courier.
- Hooded upper body.
- Small mask or visor.
- Signal backpack.
- Slightly bulky chest panel.
- Narrow legs.
- Compact weapon arm.
- Silhouette must read as a lone human courier, not a knight, robot, or cartoon hero.

Player colors:

| Part | Color |
| --- | --- |
| Suit | `#2A323C` |
| Suit shadow | `#171D24` |
| Hood edge | `#3A4856` |
| Visor | `#4BE2FF` |
| Backpack | `#3A4856` |
| Signal belt | `#FFB347` |
| Boots | `#1C2530` |

The cyan visor is the main identity point.

Sprite size:

| State | Hitbox | Visual Sprite |
| --- | ---: | ---: |
| Standing | 16 x 24 | 32 x 40 |
| Crouching | 16 x 12 | 32 x 28 |

Origin:

- Center bottom.

Facing:

- Flip sprite horizontally.
- Visual facing follows mouse X or last horizontal input.
- If no horizontal input has occurred, face right.

Animations:

| Animation | Frames | Duration | Notes |
| --- | ---: | ---: | --- |
| Idle | 4 | 1.2 s | Slight breathing |
| Run | 6 | 0.45 s | Compact courier stride |
| Jump | 3 | one-time | Knees tuck |
| Fall | 2 | one-time | Arms back |
| Crouch | 4 | 0.2 s | Body compresses 65 percent height |
| Crouch Run | 4 | 0.5 s | Low shuffling |
| Shoot | 2 | 0.15 s | Weapon recoil |
| Hurt | 2 | 0.2 s | Body tilts back |
| Death | 6 | 0.5 s | No blood, signal shatter |

Death visual:

- Player breaks into cyan and white signal shards.
- Small rust shards.
- No gore.
- No lingering corpse.
- Death lasts 0.5 seconds, then respawn or game over.

Crouch visual:

- Sprite compresses vertically.
- Visor remains visible.
- Weapon lowers.
- Muzzle origin visually matches gameplay crouch offset.
- Hitbox is smaller, but sprite may still show some head height for readability.
- Crouch state must be obvious.

## 5.2 Mite Crawler

Silhouette:

- Small rust bug.
- Four legs.
- Red eye.
- Visual sprite: 24 x 24.

Palette:

- Rust dark.
- Rust light.
- Red eye.

Animation and states:

- Crawl: 4 frames, 0.5 s loop.
- Blocked: 0.5 s wait, antennae twitch.
- Hit: squash.
- Death: 4 rust shards.

Facing:

- Face movement direction.
- If blocked, keep last facing.

## 5.3 Dredge Drone

Silhouette:

- Small maintenance drone.
- Single red eye.
- Two side thrusters.
- Visual sprite: 32 x 28.

Palette:

- Steel.
- Rust light.
- Red eye.
- Amber thruster glow.

Animation and states:

- Hover: 4 frames, 0.8 s loop.
- Fire telegraph:
  - Eye brightens for 0.15 s before projectile spawn.
  - Thrusters flash amber.
- Fire:
  - Small recoil.
  - Red projectile.
- Death:
  - Smoke puff.
  - Small red flash.
  - Drone body splits.

Facing:

- Face player when firing.
- Otherwise face patrol direction.

## 5.4 Pincer Bot

Silhouette:

- Low armored walker.
- Two front pincers.
- Red core between pincers.
- Visual sprite: 32 x 32.

Palette:

- Rust dark.
- Steel.
- Red core.

States:

| State | Visual |
| --- | --- |
| Idle | Slow walk, pincers closed |
| Telegraph | Pincers open, red core brightens, body shakes 2 px |
| Charge | Body stretches forward, red trail |
| Cooldown | Pincers lower, core dims |

Telegraph:

- Duration: 0.5 s.
- Shake: 2 px horizontal.
- Pincers open.
- Red glow intensifies.

Charge:

- Body stretches 1.2 times horizontally.
- Red trail: 3 fading frames.
- Stops with small impact puff.

Facing:

- Face charge direction.

## 5.5 Warden Sentry

Silhouette:

- Wall or floor turret.
- Rotating head.
- Thick barrel.
- Red target light.
- Visual sprite: 40 x 40.

Palette:

- Steel.
- Rust.
- Red target light.
- Orange muzzle.

Animation and states:

- Idle: slow scan.
- Aim: head rotates toward player.
- Fire:
  - Muzzle flash.
  - Barrel recoil.
  - Two-shot burst.
- Death:
  - Head drops.
  - Smoke.
  - Power-down light.

Facing:

- Barrel angle communicates target direction.

## 5.6 Mist Wraith

Silhouette:

- Ghost-like signal creature.
- Tattered lower body.
- Pale cyan or white form.
- Dark hollow center.
- Visual sprite: 32 x 32.

Palette:

- Signal cyan.
- Signal white.
- Dark void center.

Phased visual:

- Alpha drops to 0.25.
- Outline becomes dashed.
- Small ripple appears at phase start and end.
- Player projectiles pass through with faint distortion.
- No player damage while phased.

Facing:

- Face movement direction toward player.

## 5.7 Bolt Golem

Silhouette:

- Large rust machine.
- Heavy arms.
- Central chest cannon.
- Thick legs.
- Visual sprite: 64 x 64.

Palette:

- Rust dark.
- Rust light.
- Steel.
- Red chest core.

Animations and states:

- Walk: 4 frames, 1.2 s loop.
- Heavy bolt telegraph:
  - Chest core glows for 0.3 s.
  - Arms raise slightly.
- Fire:
  - Large recoil.
  - Smoke puff.
- Stomp telegraph:
  - Arms raise.
  - Red ring appears on ground in front.
  - Ring size: 3 tiles diameter.
  - Duration: 0.4 s.
- Stomp:
  - Screen shake: 3 px, 0.1 s if T2 screen shake is active.
  - Dust puff.
  - Temporary spike patches appear.

Facing:

- Face movement direction or player when attacking.

## 5.8 World 2 Enemy Variants

World 2 enemies use the same shapes with a brighter Skyloom palette.

Changes:

- Rust replaced with pale steel.
- Red eyes remain red.
- Thruster glows are slightly brighter.
- Small sky-fin or cable detail added.
- Shadows are softer.

## 5.9 Hush Warden

Silhouette:

- Large maintenance warden.
- Rust armor.
- Single red optic.
- Four heavy arms.
- Visual sprite: 80 x 80.

Palette:

- Rust dark.
- Rust light.
- Steel.
- Red optic.
- Orange warning lights.

Phase visuals:

- Phase 1:
  - Red optic dim.
  - Armor intact.
  - Movement heavy.
- Phase 2:
  - Red optic brighter.
  - Armor cracks reveal orange core.
  - Slight red glow around body.

Attack visuals:

- Charge:
  - 0.6 s telegraph.
  - Boss crouches.
  - Red line appears from boss toward player direction.
  - Red chevrons pulse along path.
  - Boss dashes with red trail.
  - Spike patches appear along path with red tips.
- Fan Bolt:
  - Three red bolts.
  - Muzzle flash from chest.
- Sweep Beam:
  - 0.8 s telegraph.
  - Dashed red line appears at boss or player Y.
  - Height: 24 px.
  - Edge arrows appear at arena boundaries.
  - Solid red beam with white core and orange edge glow.
  - Lasts 0.7 s.
- Drone Summon:
  - Red ring appears at boss.
  - Two Dredge Drones fade in over 0.4 s.
  - Small smoke puff.

Death:

- 2-second sequence:
  1. Boss stops.
  2. Optic flickers.
  3. Red light turns off.
  4. Armor panels fall.
  5. White signal burst.
  6. Conduit activates.

## 5.10 Null Relay

Silhouette:

- Abstract central relay.
- Rotating geometric rings.
- Central core.
- No human face.
- Should feel like a corrupted city relay, not a monster.
- Visual sprite: 96 x 96.

Palette by phase:

| Phase | Core | Rings |
| --- | --- | --- |
| 1 | Violet | Cyan |
| 2 | Magenta | Violet |
| 3 | White | Red |

Attack visuals:

- Rain:
  - Three vertical columns.
  - Telegraph: 0.3 s red dashed vertical lines.
  - Red vertical shards with white core.
  - Small dust or water splash on impact.
- Side Sweep:
  - 0.8 s telegraph.
  - Dashed horizontal line at random valid Y chosen at telegraph start.
  - Red or orange.
  - Edge arrows.
  - Horizontal beam, 24 px height, red outer, white core.
- Echo Shot:
  - Three violet bolts.
  - Each bolt bounces once.
  - Bounce visual: violet spark, slight squash, short trail.
- Wraith Summon:
  - Purple ring.
  - Two Mist Wraiths fade in.
- Overload Cycle:
  - Horizontal beam telegraph and active.
  - Vertical beam telegraph and active.
  - Core Exposed:
    - Boss becomes stationary.
    - Core turns bright white.
    - Ring of white light pulses.
    - Player projectiles hitting core produce extra white ripple.
    - Boss bar pulses white.

Death:

- 3-second sequence:
  1. Boss stops.
  2. Rings slow.
  3. Core flashes white.
  4. Rings collapse inward.
  5. Large white burst.
  6. Background city lights begin to restore.
  7. Conduit activates.

# 6. AUDIO

All audio is generated with the Web Audio API. No external audio files are loaded.

Mixing:

- Music volume: 0.5.
- SFX volume: 0.7.
- UI volume: 0.8.
- Master limiter peak: -3 dB.
- Duck music by -6 dB during player hurt, boss warning, stage complete, and boss death.
- Avoid clipping.
- No long reverb tails.
- No harsh high-frequency spikes.

SFX priority:

| Priority | Event class |
| ---: | --- |
| 1 | Player hurt |
| 2 | Player death |
| 3 | Boss warning |
| 4 | Checkpoint |
| 5 | Tuner unlock |
| 6 | Core or heart pickup |
| 7 | Enemy death |
| 8 | Weapon fire |
| 9 | UI |

If multiple SFX trigger at once, play the highest priority. Lower priority events may be dropped.

SFX table:

| Sound name | Recipe | Rule that plays it |
| --- | --- | --- |
| uiConfirm | Square 880 Hz, 0.08 s, fast decay | UI confirm, title begin, stage select confirm |
| uiHover | Sine 1200 Hz, 0.03 s, gain 0.1 | Button hover |
| uiDeny | Square 110 Hz plus 120 Hz, 0.12 s, low buzz | Locked weapon select, invalid input |
| pauseIn | Sine 440 Hz to 220 Hz, 0.08 s | Pause opened |
| pauseOut | Sine 220 Hz to 440 Hz, 0.08 s | Pause closed |
| stageStart | Two-note motif, 0.6 s total; World 1: 220 Hz then 261.63 Hz; World 2: 440 Hz then 523.25 Hz | Stage start |
| playerJump | Sine 300 Hz to 600 Hz, 0.06 s, quick attack | Player jump |
| playerLand | Triangle 120 Hz, 0.08 s, lowpass | Player land |
| chirpFire | Square 900 Hz, 0.05 s, fast pop | Chirp fire |
| sifterFire | Three square pops 800, 900, 1000 Hz staggered 0.02 s, total 0.08 s | Sifter fire |
| lanceFire | Sawtooth 1200 Hz down to 200 Hz, 0.12 s | Lance fire |
| bloomFire | Sine 80 Hz plus filtered noise, 0.15 s, heavy pulse | Bloom fire |
| bloomSplit | Sine 1400 Hz to 1800 Hz, 0.10 s, bright chime | Bloom main split |
| playerProjectileHit | Square 1600 Hz, 0.05 s; small enemy pitch 1.2 times, medium 1.0 times, large 0.8 times | Player projectile hits enemy |
| playerHurt | Square 200 Hz, 0.12 s, short alarm | Player takes damage |
| playerDeath | Sawtooth 400 Hz down to 60 Hz, 0.5 s | Player death |
| checkpoint | Two sine notes 660 Hz then 990 Hz, 0.3 s | Checkpoint activated |
| coreCollected | Three sine notes 880, 1108, 1318 Hz over 0.25 s | Core collected |
| heartCollected | Sine 520 Hz plus 780 Hz, 0.2 s | Heart collected |
| tunerUnlock | Major arpeggio 440, 554, 659, 880 Hz over 0.6 s | Tuner collected and weapon unlocked |
| enemyDeathMite | Noise crunch plus square 150 Hz, 0.10 s | Mite Crawler death |
| enemyDeathDrone | Square 2000 Hz to 800 Hz plus sine 120 Hz, 0.20 s | Dredge Drone death |
| enemyDeathPincer | Square 300 Hz plus filtered noise, 0.30 s | Pincer Bot death |
| enemyDeathSentry | Sine 800 Hz down to 100 Hz, 0.30 s | Warden Sentry death |
| enemyDeathWraith | Sine 800 Hz down to 200 Hz, 0.40 s | Mist Wraith death |
| enemyDeathGolem | Sine 60 Hz plus filtered noise, 0.50 s | Bolt Golem death |
| bossWarning | Square 440 Hz and 554 Hz alternating, 0.5 s | Major boss attack warning or phase warning |
| bossPhaseChange | Phase 2: sine 880 Hz to 1320 Hz, 0.4 s; Phase 3: white noise burst plus sine 1320 Hz, 0.4 s | Boss phase change |
| bossDeath | Filtered noise explosion plus sine 200 Hz to 800 Hz, 0.8 s | Boss death |
| conduitComplete | Sine 300 Hz to 900 Hz, 0.7 s, clean rising sweep | Conduit activation and stage complete |

Music table:

| Music name | Recipe | Rule that plays it |
| --- | --- | --- |
| musicTitle | D minor, 72 BPM, slow sine pad on D2 and A2, sparse square motif every 2 beats, 8-bar loop | Title state |
| musicIntro | D minor, 68 BPM, minimal low sine drone, short narrative beeps every 4 beats | Intro state |
| musicMap | D major, 96 BPM, clean triangle pad, short square pickup every 4 beats | Signal Map state |
| musicW1 | D minor, 104 BPM, low bass pulse, metallic square stabs, filtered noise drips | World 1 stages 1 through 4 |
| musicW1Boss | E minor, 120 BPM, heavy square pulse, red-pulse bass, added high square arp in Phase 2 if T2 layering is active | World 1 boss stage |
| musicW2 | F major, 112 BPM, airy sine pads, lighter metallic percussion, wind noise | World 2 stages 1 through 4 |
| musicW2Boss | C minor, 126 BPM, layered sine tension, urgent square pulse in Phase 2, stripped bass and warning beeps in Phase 3 if T2 layering is active | World 2 boss stage |
| musicSummary | D major, 100 BPM, short resolution motif, 4 bars | Stage Summary state |
| musicGameOver | C minor, 60 BPM, low sine loss, slow pad decay | Game Over state |
| musicEnd | D major, 96 BPM, bright pad, rising sine motif, final resolution | End state |

Music transitions:

- Crossfade: 0.5 s.
- Stage start sting: 0.6 s.
- Boss start: music intensity rises.
- Boss death: music cuts, then resolution cue.
- Pause: music stops or ducks to 20 percent.
- Resume: 0.2 s fade in.

# 7. UX

HTML and CSS only for UI. Canvas draws the world and VFX. DOM overlay draws screens, HUD, crosshair, and notifications.

State machine:

| State | Elements | Transitions |
| --- | --- | --- |
| Title | Logo, Begin Signal or Continue, New Signal, Controls, footer | Begin Signal to Intro; Continue to stage; New Signal confirm to Intro; Controls panel open or close |
| Intro | 4 story cards, skip prompt | Skip to next card; after card 4 to Signal Map |
| Map | Two world panels, 5 stage nodes each, world lock, selection brackets | Select unlocked node to Stage |
| Stage | World, entities, VFX, HUD, crosshair, objective arrow | Complete non-final to Summary; complete final to End; lives 0 to Game Over; pause to Pause |
| Pause | Pause panel, Resume, Restart Stage, Signal Map, Title | Resume to Stage; Restart to reset Stage; Signal Map to Map; Title to Title |
| Summary | Stage name, stats, Continue, Signal Map | Continue to next stage; Signal Map to Map |
| Game Over | Signal Lost text, Retry Stage, Signal Map, Title | Retry to reset same stage; Map to Map; Title to Title |
| End | Signal Restored text, total stats, Signal Map, Title | Map to Map; Title to Title |

Title rules:

- No progress: Begin Signal and Controls.
- With progress: Continue, New Signal, Controls.
- Continue starts the furthest unlocked uncompleted stage.
- New Signal shows confirm panel:
  - Text: Erase saved signal?
  - Buttons: Erase, Cancel.
- Footer: Desktop mouse and keyboard.

Intro cards:

- Card 1: The central relay has gone silent.
- Card 2: The Hush swarm has locked the districts.
- Card 3: Courier Jex carries the last tuned weapons.
- Card 4: Recover 10 nodes. Restore the broadcast.
- Each card can be skipped with Enter, Space, or click.

Signal Map rules:

- Two panels:
  - World 1: Sumpworks.
  - World 2: Skyloom.
- Each panel has 5 stage nodes.
- Node states:
  - Locked: dark grey, red lock icon.
  - Unlocked: cyan outline, white center, subtle pulse.
  - Completed: filled cyan, white check.
- Current furthest unlocked uncompleted stage pulses slightly stronger.
- World 2 is dimmed to 50 percent until World 1 Stage 5 is completed.
- World 2 lock text: Restore W1 Signal.
- Selected node shows cyan bracket corners and brighter border.

Stage start:

- 0.5 s signal wipe transition.
- Stage name card for 1.2 s:
  - World label small.
  - Stage name large.
  - Example: W1 · N3 and Pressure Lock.
- Gameplay begins.

Pause:

- Pause only exists during Stage state.
- Stage dims to 65 percent brightness.
- Center panel: 420 x 240.
- Title: PAUSED.
- Buttons: Resume, Restart Stage, Signal Map, Title.
- All timers, enemies, projectiles, music intensity, and VFX stop.

Stage Summary:

- Panel: 520 x 260.
- Content:
  - Stage name.
  - Stage label.
  - Time.
  - Deaths.
  - Cores in Stage.
  - Total Cores.
- Buttons: Continue, Signal Map.

Game Over:

- Background stage dims to 40 percent.
- Red vignette.
- Large text: SIGNAL LOST.
- Subtext: Connection failed.
- Buttons: Retry Stage, Signal Map, Title.
- Static signal noise visual.
- Low red pulse.

End:

- Bright background.
- City signal network lights up.
- Cyan and white light beams rise.
- Large text: SIGNAL RESTORED.
- Subtext: The broadcast is back.
- Stats:
  - Total Time.
  - Total Deaths.
  - Total Cores.
- Buttons: Signal Map, Title.

HUD table:

| Element | Record field | When visible |
| --- | --- | --- |
| Hearts row | `player.hearts` | Stage state |
| Weapon slots | `player.weapons.active`, `player.weapons.unlocked`, `progression.weapons` | Stage state |
| Stage label | `stage.label` | Stage state |
| Core counter | `progression.cores` count over 30 | Stage state |
| Pause icon | `game.state` is stage | Stage state |
| Boss name | `stage.boss.type` | Boss active |
| Boss bar | `stage.boss.hp`, `stage.boss.maxHp` | Boss active |
| Boss phase warning | `stage.boss.phase`, `stage.boss.state` | Boss active and phase warning |
| Notification | `game.hud.notification` | Stage state when message is active |
| Edge arrow | Objective position versus camera | Stage state when objective is off-screen |
| Control hint | `stage.id`, hint timer | Stage 1-1 only, until 10 s or first successful jump |
| Damage vignette | `game.hud.damageFlash` | Stage state after player damage |
| Crosshair | `input.mouse.worldX`, `input.mouse.worldY`, `input.mouse.inside` | Stage state |
| Facing indicator | `player.facing` | Stage state when keyboard fallback is active |

HUD behavior:

- Hearts:
  - 5 icons.
  - Filled: `#FF7D9B` with 1 px dark outline.
  - Empty: dark outline only.
  - Lost heart pulses scale 1.2 for 0.4 s.
- Weapon slots:
  - 4 slots.
  - Slot size: 36 x 28.
  - Spacing: 6 px.
  - Locked: grey background, grey icon, diagonal slash.
  - Unlocked inactive: neutral border, white icon.
  - Active: cyan border, cyan glow, brighter icon.
  - Deny: red border flash plus 0.15 s horizontal shake.
- Weapon icons:
  - Chirp: single small dart.
  - Sifter: three small pellets in a fan.
  - Lance: long horizontal line.
  - Bloom: three curved shards from center.
- Core counter:
  - Example: Cores 12/30.
  - Number flashes white for 0.4 s on core collection.
  - Small cyan burst at HUD counter.
  - No bottom-center text notification.
- Boss HUD:
  - Boss name center.
  - Boss bar width 480 px, height 12 px.
  - Hush Warden fill: `#FF4F5A`.
  - Null Relay fill:
    - Phase 1: `#9F7BFF`.
    - Phase 2: `#FF6BD6`.
    - Phase 3: `#FFFFFF`.
  - Phase warning text:
    - PHASE 2 or OVERLOAD.
    - Size 24 px.
    - Hold 1.2 s.
    - Fade 0.3 s.
- Notification:
  - Bottom center.
  - Width 560 px.
  - Height 28 px.
  - Priority:
    1. Weapon unlock.
    2. Boss phase warning.
    3. Checkpoint.
    4. Generic stage message.
  - Examples:
    - CHECKPOINT.
    - TUNER: SIFTER.
    - PHASE 2.
    - CONDUIT READY.
  - Do not use for core collection.
- Edge arrow:
  - 16 px cyan chevron.
  - Pulse 0.5 s.
  - Points to Conduit in non-boss stages.
  - Points to boss in boss stages before boss death.
  - Points to Conduit in boss stages after boss death.
  - Hides when objective is on-screen.
  - Must not cover player, enemy projectiles, boss telegraphs, or center screen.
- Control hint:
  - Stage 1-1 only.
  - Text: A/D move    W jump    S crouch    Mouse shoot.
  - Visible for 10 seconds or until first successful jump.
  - Fade out 0.5 s.
- Crosshair:
  - Hide OS cursor during Stage state.
  - Size: 12 px.
  - Color: `#4BE2FF`.
  - Center dot: 2 px.
  - Four short lines, 4 px long.
  - 1 px line width.
  - On shoot, expands to 14 px for 0.05 s.
  - If mouse leaves window, crosshair dims to 50 percent.
  - Aim remains last known mouse position.
  - Shooting stops unless J is held.
- Facing indicator:
  - 8 px cyan arrow.
  - Positioned 16 px from player center in facing direction.
  - Visible only while keyboard fallback is active.

# 8. DEBUG API

All test calls that reach game state must use `game.debug`.

```js
game.debug = {
  // Simulation
  advance(ms),
  advanceUntil(predicate, timeoutMs),
  setSimTime(seconds),
  setRngSeed(seed),
  getRngSeed(),

  // Stage
  loadStage(id),
  resetStage(),
  setStageTimeMs(ms),
  addStageDeath(),
  setStageDeaths(n),
  completeStage(),
  setConduitReady(value),
  getStage(),

  // Player
  teleportPlayer(x, y),
  setPlayerVel(vx, vy),
  setPlayerHearts(n),
  setPlayerLives(n),
  setPlayerInvuln(seconds),
  setPlayerCrouch(value),
  setPlayerFacing(dir),
  damagePlayer(sourceX, sourceY),
  killPlayer(),
  respawnPlayer(),

  // Input
  pressKey(action),
  releaseKey(action),
  setKeys({ left, right, crouch }),
  pressJump(),
  releaseJump(),
  holdJump(value),
  pressShoot(),
  releaseShoot(),
  setShoot(value),
  setMouseWorld(x, y),
  setMouseInside(value),
  selectWeapon(slot),
  cycleWeapons(direction),
  pressPause(),

  // Weapons
  unlockWeapon(weapon),
  selectWeapon(weapon),
  setSwitchCooldown(seconds),
  setFireCooldown(weapon, seconds),
  giveAllWeapons(),

  // Projectiles
  spawnPlayerProjectile(weapon, x, y, aimX, aimY),
  spawnEnemyProjectile(type, x, y, vx, vy, radius, damage, lifetime),
  clearProjectiles(),
  setProjectileLimit(team, limit),

  // Enemies
  spawnEnemy(type, x, y),
  killEnemy(type),
  killAllEnemies(),
  setEnemyHp(typeOrId, hp),
  setEnemyActive(typeOrId, value),
  setEnemyState(typeOrId, state),
  setEnemyCooldown(typeOrId, attack, seconds),
  setEnemyDormant(typeOrId, value),

  // Boss
  activateBoss(),
  damageBoss(amount),
  setBossHp(hp),
  setBossPhase(n),
  setBossState(state),
  setBossCooldown(attack, seconds),
  clearBossSummons(),
  setBossDying(value),

  // Hazards
  spawnBeam(type, x, y, width, height, telegraphTime, activeTime),
  clearBeams(),
  spawnTempSpike(x, y, w, h, warnDuration, activeDuration),
  clearTempSpikes(),
  setTempSpikeState(id, state),

  // Platforms
  setPlatform(id, x, y),
  setPlatformVelocity(id, vx, vy),
  resetPlatforms(),

  // Pickups
  collectCore(id),
  spawnCore(id, x, y),
  clearCores(),
  spawnHeart(x, y),
  spawnTuner(weapon, x, y),
  collectTuner(weapon),

  // Checkpoints
  setCheckpoint(x, y),
  activateCheckpoint(),
  resetCheckpoints(),

  // Progression
  setStageCompleted(id, value),
  setStageUnlocked(id, value),
  setCoreCollected(id, value),
  setWeaponUnlocked(weapon, value),
  resetProgression(),
  setRunStats(timeMs, deaths),
  addStatDeath(),
  addStatTimeMs(ms),

  // Events
  emitVfx(name, data),
  emitSfx(name)
}
```

# 9. TESTS

Run tests with:

```bash
npm test
```

Tests run in Node without a browser. Tests use headless game, input proxy, memory save, and completion bot. Unit tests may call pure utility exports directly. Every `game.debug` call in this section exists in section 8.

## 9.1 Unit Tests

| Test file | System | Check | Debug calls | Expected state |
| --- | --- | --- | --- | --- |
| math.test.js | Math | Clamp, lerp, angle difference, normalize, rect overlap, point in rect, LOS sampling | None | Pure helpers return expected values |
| rng.test.js | RNG | Same seed produces same sequence; different seed produces different sequence; output range is 0 to 1 exclusive | `debug.setRngSeed(101)`, `debug.getRngSeed()` | Deterministic sequence |
| save.test.js | Save | New progression unlocks only w1s1; completing w1s1 unlocks w1s2; completing w1s5 unlocks World 2; Continue returns furthest unlocked uncompleted stage; reset clears progress; unavailable storage falls back to memory | `debug.resetProgression()`, `debug.setStageCompleted("w1s1", true)` | Correct unlock and continue behavior |
| input.test.js | Input | Primary and alternate keys map; jump edge works; mouse updates; mouse leave stops mouse shooting; J still shoots after mouse leave; weapon select works; cycle only unlocked | `debug.pressJump()`, `debug.selectWeapon(2)`, `debug.setMouseInside(false)`, `debug.setMouseWorld(100, 100)` | Input flags correct |
| physics.test.js | Player movement | Ground acceleration reaches 240; air acceleration slower; friction stops; crouch max 120; jump sets -640; coyote 0.09; buffer 0.10; jump cut -320; gravity 1800; max fall 1100; updraft -2400 clamp -420; horizontal wind clamp plus or minus 360; conveyor plus or minus 120 clamp plus or minus 360; one-way landing; one-way pass-through; moving platform carry; low clearance blocks standing; low clearance allows crouch | `debug.loadStage("minimalStage")`, `debug.setPlayerVel(0, 0)`, `debug.setKeys({ right: true })`, `debug.pressJump()`, `debug.advance(1000)`, `debug.setPlayerCrouch(true)` | Player velocity, position, and grounded state match rules |
| tilemap.test.js | Tilemap | Parsing creates correct solid, one-way, spike, conveyor arrays; solid query; one-way top; spike query; conveyor offset | `debug.loadStage("weaponTestStage")`, `debug.advance(16)` | Tile queries correct |
| player.test.js | Player | Standing hitbox 16 x 24; crouch 16 x 12; crouch preserves feet; standing blocked by clearance; muzzle lowers when crouched; muzzle X offset horizontal; damage 1 heart; invulnerability prevents damage; knockback from source; death with lives respawns; death with zero lives Game Over; pit full hearts respawns; pit 1 heart death; checkpoint sets respawn; checkpoint restores 1 heart | `debug.damagePlayer(0, 0)`, `debug.setPlayerInvuln(1.0)`, `debug.setPlayerHearts(1)`, `debug.advance(1000)`, `debug.activateCheckpoint()` | Player hearts, lives, position, and invulnerability match rules |
| weapon.test.js | Weapons | Chirp one projectile damage 7 speed 950 lifetime 0.7 radius 4; Sifter 5 pellets spread; Lance pierces 3 distinct enemies; Lance does not hit same enemy twice; Bloom splits on enemy hit; Bloom splits on lifetime; Bloom does not split on tile hit; shards damage 6 lifetime 0.5 speed 620; switch cooldown 0.12; locked weapon deny; cycle skips locked | `debug.loadStage("weaponTestStage")`, `debug.giveAllWeapons()`, `debug.selectWeapon("chirp")`, `debug.spawnPlayerProjectile("chirp", 0, 0, 1, 0)`, `debug.advance(100)`, `debug.selectWeapon("sifter")`, `debug.setSwitchCooldown(0.12)` | Projectiles and cooldowns match weapon tables |
| projectile.test.js | Projectiles | Player projectile destroys on solid tile; passes one-way; enemy projectile destroys on solid; lifetime expires; no owner damage; high-speed substeps; Lance pierce ID set; Bloom split; Echo bounce once; projectile limits expire oldest | `debug.spawnPlayerProjectile("lance", 0, 0, 1, 0)`, `debug.spawnEnemyProjectile("echo", 0, 0, 100, 0, 6, 1, 2.0)`, `debug.advance(1000)`, `debug.clearProjectiles()` | Projectile lifecycle and limits match rules |
| enemy.test.js | Enemies | Activation radius 320; max 16 active; closest activate; World 2 HP ceil base times 1.15; World 2 projectile speed times 1.1; Mite moves within 5 tiles and waits 0.5 blocked; Drone patrols 4 tiles and fires 1.6; Pincer telegraph 0.5 and charge stops; Sentry aims 3 rad/s and bursts within 10 degrees; Wraith phases 2.5 and 0.8; phased blocks damage; Golem stomp spikes; Golem death heart; death clears enemy projectiles | `debug.loadStage("minimalStage")`, `debug.spawnEnemy("mite", 100, 100)`, `debug.activateBoss()`, `debug.setEnemyHp("mite", 4)`, `debug.advance(1000)` | Enemy state and damage match roster |
| boss.test.js | Bosses | Hush phase at 60 percent; charge leaves 4 spikes; fan bolt 3 projectiles; Phase 2 enables sweep beam; drone summon max 3; Hush death unlocks conduit after 2 s; Null phases at 70 and 35; Phase 2 warning 1.5; Echo bounce once; Wraith summon max 4; Phase 3 overload alternates beams and core exposed; core exposed damage times 1.5; Null death unlocks conduit after 3 s; boss reset on player death | `debug.loadStage("bossTestStage")`, `debug.activateBoss()`, `debug.damageBoss(180)`, `debug.setBossHp(100)`, `debug.advance(2000)` | Boss phase, attacks, death, and conduit unlock match rules |
| progression.test.js | Progression | Start unlocks Chirp only; Sifter tuner unlocks Sifter; Lance tuner unlocks Lance; Bloom tuner unlocks Bloom; cores persist; collected cores not spawned; stage completion unlocks next; final completion marks complete | `debug.unlockWeapon("sifter")`, `debug.setCoreCollected("w1s1-core-1", true)`, `debug.setStageCompleted("w1s2", true)` | Progression state matches unlock and core rules |

## 9.2 Integration Tests

| Test file | System | Check | Debug calls | Expected state |
| --- | --- | --- | --- | --- |
| stateFlow.test.js | States | Title no save shows Begin Signal; title with save shows Continue and New Signal; intro skips; map starts unlocked stage; stage leads to summary; summary continues; game over leads to retry, map, title; end leads to map or title | `debug.resetProgression()`, `debug.loadStage("w1s1")`, `debug.completeStage()`, `debug.pressKey("enter")` | State transitions correct |
| stageLoad.test.js | Stage factory | Every production stage loads; validator passes; player spawns; conduit exists; checkpoint exists; exactly 3 cores unless collected; enemy counts match table; boss stages contain correct boss; World 2 modifiers apply; camera bounds; 5-second idle no exceptions | `debug.loadStage(id)`, `debug.advance(5000)` | All 10 stages load and simulate cleanly |
| checkpointDeath.test.js | Death and checkpoint | Death at checkpoint resets dynamic state; respawn at checkpoint; hearts reset 5; lives decrement; boss resets if present; game over at zero lives | `debug.loadStage("bossTestStage")`, `debug.activateCheckpoint()`, `debug.setPlayerHearts(0)`, `debug.killPlayer()`, `debug.advance(1000)` | Player and stage reset correctly |
| pit.test.js | Pit | Falling 64 px below stage triggers pit; pit with over 1 heart respawns and 0.5 invulnerability; pit with 1 heart death; no checkpoint respawns at start | `debug.teleportPlayer(0, stageHeightPlus70)`, `debug.setPlayerHearts(5)`, `debug.advance(1000)` | Pit rule and respawn correct |
| pause.test.js | Pause | Pause stops simulation; enemies do not move; projectiles do not move; boss timers do not advance; resume continues; restart resets; map exits | `debug.loadStage("bossTestStage")`, `debug.pressPause()`, `debug.advance(1000)`, `debug.pressKey("resume")` | Simulation freezes and resumes correctly |
| weaponProgression.test.js | Weapon progression | At w1s1 only Chirp unlocked; selecting Sifter triggers deny; w1s2 tuner unlocks Sifter; w1s4 unlocks Lance; w2s2 unlocks Bloom; unlocks persist | `debug.loadStage("w1s1")`, `debug.selectWeapon(2)`, `debug.spawnTuner("sifter", 100, 100)`, `debug.advance(100)` | Deny and unlock behavior correct |
| coreProgression.test.js | Core progression | Collecting core removes it; core does not respawn on retry; total increments; all 3 in stage increases total by 3 | `debug.loadStage("w1s1")`, `debug.collectCore("w1s1-core-1")`, `debug.resetStage()`, `debug.advance(100)` | Core persistence correct |
| bossDefeat.test.js | Boss defeat | Boss can be damaged; phase warnings appear; attacks telegraph; death clears projectiles and summons; conduit activates; non-final boss leads summary; final boss leads end | `debug.loadStage("w1s5")`, `debug.activateBoss()`, `debug.damageBoss(180)`, `debug.advance(2000)`, `debug.setConduitReady(true)` | Boss death and state transition correct |

## 9.3 End-to-End Tests

| Test file | System | Check | Debug calls | Expected state |
| --- | --- | --- | --- | --- |
| allStagesSmoke.test.js | All stages | Every stage loads; 10-second idle no exceptions; player alive unless unavoidable hazard; validator passes; entities within bounds | `debug.loadStage(id)`, `debug.advance(10000)` | All stages stable |
| stageCompletionProof.test.js | Completion | Every stage validationRoute reaches conduit; stage complete fires; summary or end appears; time under limit; boss stages boss HP zero before conduit; conduit locked before boss death | `debug.loadStage(id)`, `debug.advanceUntil(conduitReached, limitMs)` | Bot completes every stage |
| fullGame.test.js | Full game | Title to End through all stages; total deaths non-negative; total time positive; cores zero if no core routes used | `debug.resetProgression()`, `debug.loadStage(id)`, `debug.completeStage()` | Full game completes |
| allCores.test.js | Core collection | Every stage coreRoutes collect 3 cores; main route reaches conduit; total cores 30; end shows Cores 30/30 | `debug.loadStage(id)`, `debug.spawnCore(id, x, y)`, `debug.collectCore(id)`, `debug.completeStage()` | All 30 cores collectible |

## 9.4 SCREENSHOTS

| Screenshot ID | State | Must show | Must not show |
| --- | --- | --- | --- |
| S01 | Title | SIGNAL COURIER logo, Begin Signal or Continue, New Signal, Controls, footer | Stage gameplay, boss HUD |
| S02 | Title confirm | Erase saved signal? panel, Erase, Cancel | Hidden confirm options |
| S03 | Intro | One story card, skip prompt, thin cyan scanline | Gameplay |
| S04 | Map unlocked | Two world panels, 5 nodes each, unlocked cyan node, completed check | Selectable locked nodes |
| S05 | Map World 2 locked | World 2 dimmed 50 percent, padlock, Restore W1 Signal | World 2 node selectable |
| S06 | Stage start | Stage name card, world label, stage label, signal wipe | Permanent stage name except HUD |
| S07 | In-stage HUD | Hearts, weapon slots, stage label, core counter, pause icon, crosshair | Boss HUD on non-boss stage |
| S08 | Damage feedback | Red vignette, lost heart pulse, player flicker | Full-screen opaque red |
| S09 | Boss HUD | Boss name, boss bar, phase warning | Hearts hidden, core counter hidden |
| S10 | Pause | PAUSED panel, Resume, Restart Stage, Signal Map, Title | Moving enemies or projectiles |
| S11 | Summary | Stage name, Time, Deaths, Cores in Stage, Total Cores, Continue, Signal Map | Stage gameplay |
| S12 | Game Over | SIGNAL LOST, Connection failed, Retry Stage, Signal Map, Title | Gore or harsh punishment visuals |
| S13 | End | SIGNAL RESTORED, Total Time, Total Deaths, Total Cores, Signal Map, Title | Incomplete stats |

# 10. BUILD ORDER

| Milestone | Work | Section 9 check that proves it landed |
| --- | --- | --- |
| M0 Repository and boot | Create repo layout, index, canvas, main boot, fixed timestep | stateFlow.test.js Title no save |
| M1 Core player and tiles | Input, movement, collision, one-way, low clearance, conveyor, wind | physics.test.js and tilemap.test.js |
| M2 Weapons and projectiles | Weapon switching, fire cooldown, projectile spawn, tile collision, limits | weapon.test.js and projectile.test.js |
| M3 Enemies and activation | Enemy roster, activation, line of sight, death, World 2 modifiers | enemy.test.js |
| M4 Bosses and beams | Boss phases, attacks, telegraphs, death, conduit unlock | boss.test.js and bossDefeat.test.js |
| M5 Stages and validation | 10 stage files, stage factory, validator, stage content roster | stageLoad.test.js |
| M6 Progression and save | Session save, stage unlock, weapon unlock, core persistence, continue | progression.test.js, weaponProgression.test.js, coreProgression.test.js |
| M7 Checkpoints, death, pit | Checkpoint trigger, death reset, pit rule, game over | checkpointDeath.test.js and pit.test.js |
| M8 Pause and state screens | Pause, summary, game over, end, map transitions | pause.test.js and stateFlow.test.js |
| M9 Presentation and HUD | Canvas rendering, HUD, crosshair, VFX, audio | stageLoad.test.js 5-second idle plus screenshot rows S06 through S09 |
| M10 Full proof | Completion bot, full game, all cores | stageCompletionProof.test.js, fullGame.test.js, allCores.test.js |

# 11. DEFINITION OF DONE

| Requirement from 0.1 | Done checks | Screenshot rows |
| --- | --- | --- |
| Make a side-scrolling, platformer shooter | Player moves, jumps, shoots; stage scrolls; 10 stages simulate; all stages complete by bot | S06, S07 |
| At least 4 different gun types | Chirp, Sifter, Lance, Bloom exist; all unlock correctly; weapon tests pass | S07 |
| Character can move left or right | Input left and right change velocity; physics test passes | S07 |
| Character can jump | Jump sets -640; variable cut sets -320; coyote and buffer work | S07 |
| Character can crouch | Crouch changes hitbox to 16 x 12; crouch speed 120; low clearance passable | S07 |
| Story progression like Mario with worlds and stages | 2 worlds and 10 stages exist; sequential unlock works; final completion reaches End | S04, S05, S13 |
| Start with 2 worlds | World 1 and World 2 panels exist; World 2 lock works | S04, S05 |
| 5 stages per world, 10 total | All 10 stage files load and pass validator | S04 |
| Do not simply copy Mario | Signal Courier theme, enemy roster, boss identity, no Mario visual vocabulary | S01, S06, S09 |
| Added: 2D gameplay with 2.5D presentation | Gameplay is 2D; parallax is presentation only; no gameplay depth | S06 |
| Added: named player, enemies, bosses, and stage identity | Courier Jex, 6 enemies, 2 bosses, 10 named stages render and simulate | S06, S09 |
| Added: checkpoints, pits, hazards, and stage reset | Checkpoint, pit, death reset, and boss reset tests pass | S07, S10, S12 |
| Added: optional cores for completion stats | 30 cores placed; allCores test passes; total counter updates | S07, S11, S13 |
| Added: HUD, crosshair, damage feedback, and state screens | HUD table fields update; crosshair and vignette behave; state tests pass | S07, S08, S10, S11, S12, S13 |
| Added: generated Web Audio sound and music | Audio.js generates SFX and music; no external audio files; event rules fire | S06, S09, S11 |
| Added: deterministic simulation and testable build | `npm test` passes; fixed timestep; deterministic RNG; all section 9 checks pass | S13 |

# A. SANITY

- Check: every field a rule reads or writes is in the global context.
  - Result: closes. Player, stage, progression, input, projectile, enemy, boss, beam, tempSpike, platform, wind, lowClearance, checkpoint, core, heart, tuner, and conduit records are all listed in section 2.2.
- Check: every place, thing, or kind a rule names is placed by a generator or listed in a roster.
  - Result: closes. World, stage, weapon, enemy, boss, and object rosters are in section 4. Stage content roster places enemies, cores, hearts, tuners, checkpoints, and conduits for all 10 stages.
- Check: for every consumable, total placed against total rules can demand along the core loop.
  - Result: closes.
    - Cores: 3 per stage, 10 stages, 30 total. allCores test demands 30 and stage content places 30.
    - Signal Hearts: 1 per stage plus Bolt Golem drops. Stage content places 10 stage hearts. Golem placements are 2 in 2-3, 2 in 2-4, and 1 in 2-5, for 5 drop hearts. Health is optional; no rule requires a minimum pickup count to complete.
    - Tuners: exactly one Sifter in w1s2, one Lance in w1s4, one Bloom in w2s2, and no others. Weapon unlock rules demand exactly these three tuners.
    - Checkpoints: at least 1 per stage by validator and stage content roster.
- Check: every timing pair closes and still bites.
  - Result: closes with changes listed.
    - Jump versus required gaps: initial jump -640 and gravity 1800 give about 113 px vertical height and about 170 px horizontal range at 240 px/s. Required gaps are no wider than 4 tiles, which is 128 px. Closes.
    - Projectile lifetime versus travel: Chirp 950 times 0.7 is 665 px; Sifter 720 times 0.35 is 252 px; Lance 1500 times 0.8 is 1200 px; Bloom main 520 times 0.45 is 234 px. These match their design roles and do not exceed sane stage combat ranges. Closes.
    - Enemy projectile lifetime versus threat range: Drone 350 times 2.5 is 875 px; Sentry 520 times 1.5 is 780 px; Golem 300 times 3.0 is 900 px; boss Rain 420 times 2.0 is 840 px; Echo 520 times 2.0 is 1040 px plus one bounce. All are readable and avoidable with player speed 240 px/s. Closes.
    - Beam telegraph versus active: Hush Sweep telegraph 0.8 and active 0.7; Null Side Sweep telegraph 0.8 and active 0.8; Null Phase 3 beams telegraph 0.6 and active 0.6. Player can move or jump during telegraph. Closes.
    - Switch cooldown versus fire interval: universal switch 0.12 is shorter than every weapon fire interval, so switching does not create impossible gaps. Closes.
    - Pit distance versus fall speed: 64 px at 1100 px/s is about 0.058 seconds. Pit triggers quickly but is visible from the edge. Closes.
    - End-condition clock versus expected clear time: target times are not enforced. Completion proof uses `limitMs = max(60000, targetTimeMs * 3)`. This closes and still bites because a stage far slower than triple target time fails. Closes.
    - Hush Warden base movement: gameplay lacked base speed. Changed by adding 80 px/s base and 88 px/s Phase 2. Closes.
    - Beam random versus locked: gameplay random Y and engineering all-beams locked conflicted. Changed by ruling: telegraphs lock displayed line; Side Sweep uses random valid Y at telegraph start; other horizontal beams use player Y at telegraph start. Closes.
    - Death reset: gameplay only required respawn; engineering required dynamic reset. Changed by ruling: full dynamic reset on death with lives remaining. Closes.
    - Short-stage camera: gameplay clamp and engineering center conflicted. Changed by ruling: center when stage is smaller than viewport, clamp when larger. Closes.
- Check: every call section 9 makes is in section 8.
  - Result: closes. Section 9 lists only `game.debug` calls that appear in section 8. Pure utility unit calls are test-only module calls, not game state debug calls.
- Check: no placeholder in angle brackets remains.
  - Result: closes. No angle-bracket placeholders remain in this merged spec.