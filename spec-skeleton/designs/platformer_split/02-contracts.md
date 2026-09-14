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
