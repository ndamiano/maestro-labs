# 2. CONTRACTS

## 2.1 Module layout

Carried from engineering, with the audio ruling (0.2) applied: **no `assets/` directory** — audio is synthesized (6), art is procedural canvas (3.5), fonts are system stacks (0.2). Added: `render/playerRenderer.js`, `render/textures.js`, `audio/recipes.js`.

```text
/
  index.html
  styles.css
  main.js
  package.json
  src/
    core/
      config.js
      input.js
      gameLoop.js
    data/
      levelData.js
      levelLayout.js
      audioEvents.js
    state/
      createInitialState.js
      cloneState.js
    simulation/
      advance.js
      rooms.js
      doors.js
      movement.js
      atmosphere.js
      power.js
      reactor.js
      drones.js
      hull.js
      vitals.js
      items.js
      machines.js
      channels.js
      launch.js
      objectives.js
      warnings.js
      endStates.js
      invariants.js
    render/
      renderer.js
      camera.js
      worldRenderer.js
      machineRenderer.js
      doorRenderer.js
      itemRenderer.js
      playerRenderer.js
      droneRenderer.js
      particleSystem.js
      mapRenderer.js
      hudRenderer.js
      overlayRenderer.js
      textures.js
    audio/
      audioManager.js
      musicManager.js
      recipes.js
  tests/
    harness.js
    level.test.js
    movement.test.js
    doors.test.js
    atmosphere.test.js
    power.test.js
    reactor.test.js
    drones.test.js
    hull.test.js
    vitals.test.js
    items.test.js
    channels.test.js
    launch.test.js
    objectives.test.js
    audioEvents.test.js
    invariants.test.js
    acceptance/
      referenceWin.test.js
      noEmpWin.test.js
      failureModes.test.js
      resourceFairness.test.js
    browser/
      smoke.test.js
```

File responsibilities:

| File | Responsibility |
| --- | --- |
| `index.html` | canvas, map canvas, HUD DOM, title screen, end-screen overlay; loads `main.js` |
| `styles.css` | HUD layout, warning styles, end screens, 24 px safe-area margins |
| `main.js` | wires title, input, simulation, renderer, HUD, audio; exposes `window.dbg` (8) |
| `src/core/config.js` | every constant in 4.2 and 4.x, as named exports |
| `src/core/input.js` | keyboard → per-tick input frame |
| `src/core/gameLoop.js` | fixed-timestep accumulator and render loop (1.2) |
| `src/data/levelData.js` | rooms, doors, machines, content, drones, hull events, power nodes (4.2 rosters) |
| `src/data/levelLayout.js` | deterministic geometry compiler and validator |
| `src/data/audioEvents.js` | event name → recipe id mapping (6.4) |
| `src/state/createInitialState.js` | initial state from compiled level |
| `src/state/cloneState.js` | deep clone for tests/debug |
| `src/simulation/advance.js` | tick facade, runs the 15-step order |
| `src/simulation/*.js` | the system modules in 2.3 |
| `src/render/*.js` | presentation only; reads state; only `particleSystem.js` may call `Math.random()` |
| `src/audio/*.js` | Web Audio synthesis; consumes events; never alters gameplay |
| `tests/*.js` | harness and test suite (9) |

Carried cuts (engineering 3.2, 31 — nothing silently dropped): no save/load, no pause menu, no settings menu, no multiplayer, no random level generator, no tile-based pathfinding, no dynamic lighting, no 3D/2.5D renderer, no complex particle engine beyond room-local effects, no audio reverb/3D positional system, no inventory drag/drop, no mid-run respawn.

## 2.2 Global context

The simulation state is plain serializable data: no functions, no classes, no Sets, no DOM references. Created only by `createInitialState`. This is the single authoritative shape (engineering's 4.3, with the 0.2 additions: `state.channels`, `meta.nextItemId`, `player.facing`).

```js
{
  meta: {
    version: 1,
    tick: 0,                 // integer, increments 20/sec
    time: 0,                 // seconds, += 0.05 per tick
    status: 'running',       // 'running' | 'success' | 'failure'
    debugInvariants: false,  // true in tests
    nextEventId: 1,
    nextItemId: 1
  },

  end: null,                 // set at end: { status, cause, timeSurvived, stats }

  player: {
    x: 6, y: 9,              // tile coordinates (docking center)
    room: 'docking',
    o2: 100,                 // 0..100
    integrity: 100,          // 0..100
    hasWrench: false,        // not stored in inventory; cannot be dropped
    invulnerable: 0,         // seconds remaining (drone damage only)
    selectedSlot: 0,         // 0..5
    facing: { x: 0, y: 1 },  // last non-zero movement direction (visor)
    inventory: [null, null, null, null, null, null],  // slots: { type, count } | null
    lastDamageSource: null,  // 'drone' | 'reactor' | 'asphyxia' | null
    tookDamageThisTick: false
  },

  rooms: {
    // one per room id in 4.2; 10 total
    [roomId]: {
      id: 'crew', name: 'Crew Quarters', abbr: 'CQ',
      x: 8, y: 5, w: 8, h: 8,
      o2: 70,                // 0..100
      hull: 100,             // 0..100
      breached: false,       // hull <= 0
      powered: false,
      powerSource: { type: 'none', timeLeft: null },
      // type: 'none' | 'epc' | 'cell' | 'reactor' | 'powered'
      eventWarning: null     // { eventId, targetRoom, damage, timeLeft }
    }
  },

  doors: {
    // one per door id in 4.2; 10 total
    [doorId]: {
      id: 'door_crew_storage', a: 'crew', b: 'storage',
      state: 'jammed',       // 'open' | 'closed' | 'jammed'
      axis: 'y',             // compiler: shared side vertical => 'x', horizontal => 'y'
      x: 13, y: 5,           // door center
      gap: 2                 // DOOR_GAP_TILES
    }
  },

  machines: {
    // one per machine id in 4.2; 8 machines + 3 power nodes
    [machineId]: {
      id: 'crew_o2_generator', room: 'crew',
      type: 'o2_generator',  // 4.2 machine roster types
      repaired: false,       // machines that start damaged
      completed: false,      // one-time operational channels
      rate: 8,               // O2 machines: O2/sec; null for non-O2 machines
      x: 0, y: 0             // placed by levelLayout (6.1 placement in 4.2)
    }
  },

  channels: {                // carried from engineering 13.1
    // { [channelId]: { progress: number (seconds), duration: number } }
  },

  droppedItems: [
    { id: 1, type: 'o2_tank', room: 'docking', x: 5, y: 8 }
  ],

  power: {
    sources: [
      { id: 'epc_start', room: 'crew', type: 'epc', timeLeft: 400 }
    ],
    nodes: {
      crew: 'epc_start',     // source id | null (empty)
      hydro: null,
      shuttle: null
    }
  },

  reactor: {
    pumpRepaired: false,
    coreRepaired: false,
    coolantActive: false,
    coolantTime: 0,          // seconds, 180 when a cell is used
    spinUpComplete: false,
    spinUpProgress: 0,       // seconds, 0..20
    online: false,
    heatHazard: false,
    onlineEver: false
  },

  drones: [
    // two entries, ids 'A' and 'B'
    {
      id: 'A', homeRoom: 'cargo',
      room: 'cargo', x: 0, y: 0,
      state: 'inactive',     // 'inactive' | 'patrol' | 'alert' | 'attack' | 'disabled'
      active: false, disabled: false,
      alertDelay: 0,         // seconds accumulated toward the 1 s alert delay
      patrolIndex: 0,
      noPathTimer: 0,
      attackCooldown: 0,
      path: []               // room ids, next entry is the door target
    }
  ],

  launch: {
    visible: false,
    computerPrimed: false,
    fuelInstalled: false,
    progress: 0,             // percent 0..100
    lastResetReason: null,
    success: false,
    requirements: {
      reactorOnline: false,
      shuttlePowered: false,
      computerPrimed: false,
      fuelInstalled: false,
      shuttleO2Sufficient: false
    }
  },

  objectives: {
    index: 0,                // next incomplete objective, 0..9
    seenRooms: { [roomId]: false },
    stabilizeCrewTimer: 0,   // seconds crew O2 >= 60 held continuously
    shuttleO2Reached: false,
    reactorOnlineEver: false,
    completed: { [objectiveId]: false }
  },

  warnings: {
    active: [ { id, type, text, critical, room, timeLeft } ],  // max 2, priority order
    trackers: { [type]: false }
  },

  log: [ { id, time, type, text, audio, critical } ],  // full log; HUD shows last 5

  stats: {
    systemsRestored: {
      crewO2Generator: false,
      hydroO2Recycler: false,
      shuttleO2Vent: false,
      reactorOnline: false,
      launchComputerPrimed: false,
      fuelInstalled: false
    },
    breachesSealed: 0,
    dronesDisabled: 0,
    hullPatchesUsed: 0,
    powerCellsUsed: 0,
    coolantUsed: 0,
    empUsed: 0,
    launchResets: 0
  }
}
```

Advance contract: `advance(state, input) → events[]`. It may mutate `state`; it is deterministic; it never calls `Math.random()`; it returns this tick's semantic events (2.3), each of the shape `{ type, id, room, text, audio, critical }` (fields optional per event). Renderer and audio consume state and events only.

## 2.3 Module specifics

Carried from engineering; extended so every field a rule reads and every function a rule or test calls exists.

| Module | Exports (function → contract) |
| --- | --- |
| `config.js` | all constants: `SIM_HZ=20`, `DT=0.05`, `DAY_SEC=120`, `DEORBIT_SEC=960`, `PLAYER_SPEED=3.5`, `INVENTORY_SIZE=6`, `STACK_LIMITS`, `O2_PLAYER_RATES`, `ROOM_BASELINE_DRAIN=0.5`, `BREACH_DRAIN=15`, `AIRFLOW_K=5`, `MACHINE_RATES`, `DOOR_OPEN_TIME=1`, `DOOR_CLOSE_TIME=1`, `DOOR_REPAIR_TIME=5`, `HULL_PATCH_TIME=3`, `HULL_PATCH_AMOUNT=40`, `BREACH_SEAL_TIME=4`, `BREACH_SEAL_HULL=60`, `WARNING_LEAD=10`, `HULL_EVENTS`, `EPC_DURATION=400`, `CELL_DURATION=400`, `CELL_INSTALL_TIME=2`, `COOLANT_DURATION=180`, `COOLANT_LOW=30`, `COOLANT_PUMP_TIME=5`, `COOLANT_USE_TIME=5`, `CORE_REPAIR_TIME=8`, `SPINUP_TIME=20`, `HEAT_DPS=5`, `ASPHYXIA_DPS=5`, `DRONE_PATROL_SPEED=2.5`, `DRONE_ALERT_SPEED=3.0`, `DRONE_ALERT_DELAY=1.0`, `DRONE_NO_PATH_RETURN=3.0`, `DRONE_ATTACK_RANGE=1.0`, `DRONE_ATTACK_DAMAGE=20`, `DRONE_ATTACK_COOLDOWN=1.0`, `PLAYER_INVULN=0.5`, `EMP_TIME=1.0`, `MEDKIT_HEAL=50`, `O2_TANK_AMOUNT=50`, `PICKUP_RANGE=1.0`, `MACHINE_RANGE=1.5`, `DOOR_RANGE_NEAR=1.5`, `DOOR_RANGE_ADJACENT=2.0`, `LAUNCH_COMPUTER_TIME=15`, `LAUNCH_FUEL_TIME=10`, `LAUNCH_PAD_TIME=30`, `LAUNCH_VENT_TIME=5`, `LAUNCH_O2_MIN=60`, `STABILIZE_SEC=5`, `DOOR_GAP_TILES=2`, warning thresholds (`PLAYER_O2_LOW=25`, `PLAYER_O2_CRIT=10`, `INTEGRITY_LOW=25`, `INTEGRITY_CRIT=10`, `ROOM_O2_LOW=30`, `POWER_SOURCE_LOW=60`, `DEORBIT_WARN=120`) |
| `input.js` | `pollFrame() → input` — input frame: `{ moveX, moveY, interactDown, interactPressed, useDown, usePressed, drop, select }`; `select` is null or 0..5 |
| `gameLoop.js` | `start({ onTick, onRender })` — accumulator loop per 1.2 |
| `levelData.js` | exports the 4.2 rosters: `ROOMS`, `DOOR_EDGES`, `MACHINES`, `POWER_NODES`, `CONTENT`, `DRONE_DEFS`, `HULL_EVENTS` |
| `levelLayout.js` | `compileLevel() → { rooms, doors, machineSpots, pickupSpots, playerStart }`; `validateLevel(compiled) → string[]` — empty means pass; runs the 15 checks in 4.2 |
| `createInitialState.js` | `createInitialState(compiled) → state` (2.2 shape; player at docking center, `o2=100`, `integrity=100`, `hasWrench=false`, empty inventory, EPC in crew node with 400 s) |
| `cloneState.js` | `cloneState(state) → state` (deep, deterministic) |
| `advance.js` | `advance(state, input) → events[]` (15-step tick order, 1.2) |
| `rooms.js` | `roomAt(state, x, y) → room\|null`; `connectedRooms(state, roomId) → [{room, doorId}]`; `roomView(state, roomId)` — the render view, carrying visual's integration types: `{ id, name, abbr, o2, hull, breached, powered, droneActive, objective, eventWarning, eventWarningTime }` where `droneActive` is any active non-disabled drone in the room and `objective` marks the current objective room; `powerView(state, roomId) → { source, timeLeft }` |
| `doors.js` | `doorTarget(state) → door\|null` (range rule 4.5); `doorChannelSpec(door) → { duration, action }` (open/close 1 s, repair 5 s) |
| `movement.js` | `isWalkable(state, x, y) → bool` (room interiors + open door gap rectangles); `stepPlayer(state, input, events)` — slide-per-axis, room-change rule 4.3; `nearestItem(state, x, y, range) → item\|null` |
| `atmosphere.js` | `updateAtmosphere(state, events)` — 4.7 |
| `power.js` | `updatePower(state, events)` — 4.8; `powerLabel(state, roomId) → string` — `"NO POWER" \| "POWERED" \| "EPC mm:ss" \| "CELL mm:ss" \| "REACTOR"` |
| `reactor.js` | `updateReactor(state, events)` — 4.10; `reactorHeatActive(state) → bool` |
| `drones.js` | `updateDrones(state, events)` — 4.11; `roomPath(state, fromRoom, toRoom) → [roomId]...\|null` (BFS through open doors only) |
| `hull.js` | `updateHullEvents(state, events)` — 4.9; `selectEventTarget(state, event) → {roomId, damage}\|null` |
| `vitals.js` | `updateVitals(state, events)` — 4.4 |
| `items.js` | `pickUpNearest(state, events)`; `dropSelected(state, events)`; `useSelectedInstant(state, events)` (O2 Tank / Medkit; invalid use emits `invalid_use`) |
| `machines.js` | `machineTarget(state) → {machineId}\|null` (within 1.5 tiles); `machineChannelSpec(machineId) → { duration, requiresWrench, requiresItem, effect }` |
| `channels.js` | `channelTarget(state) → { channelId, target, pausedReason }\|null` — nearest valid target across doors, machines, power nodes, hull, launch pad; `updateChannels(state, input, events)` — 4.17 |
| `launch.js` | `updateLaunch(state, events)` — 4.12; `launchRequirements(state) → {reactorOnline, shuttlePowered, computerPrimed, fuelInstalled, shuttleO2Sufficient}`; `resetReason(state) → string\|null` (priority order 4.12) |
| `objectives.js` | `updateObjectives(state, events)`; `currentObjective(state) → {id, text, roomId}\|null` |
| `warnings.js` | `updateWarnings(state, events)` — thresholds, priority, max 2, tracker transitions → audio events; `activeWarnings(state) → [{type, text, critical}]` |
| `endStates.js` | `updateEndStates(state, events)` — precedence 4.14; `endSummary(state) → { status, cause, day, timeUsed, systemsRestored, dronesDisabled, breachesSealed }` |
| `invariants.js` | `assertInvariants(state) → string[]` (failures; empty = pass) — the 16 checks in 9.2 |
| `audioManager.js` | `init()` (after user gesture), `play(name, {pan}\|null)`, `startLoop(name)`, `stopLoop(name)` — from `recipes.js` (6); missing recipe → console warn, no crash |
| `recipes.js` | `SFX_RECIPES` (6.3), `MUSIC_RECIPES` (6.2) |
| `musicManager.js` | `setLayers([layerNames])` with 0.5 s gain crossfades; `playTheme('success'\|'failure')` |
| `renderer.js` | `renderFrame(state, events, ctx)` — runs the 11-step draw order (1.2) |
| `camera.js` | `updateCamera(state)` — 1.2 camera rules |
| `worldRenderer.js` | draws floors/walls from `textures.js` static canvas |
| `textures.js` | `buildStatic(compiled) → offscreenCanvas`; procedural floor/wall recipes (3.5); sprite/icon drawing per 3 and 5 |
| `machineRenderer.js` / `doorRenderer.js` / `itemRenderer.js` / `playerRenderer.js` / `droneRenderer.js` | draw each entity from state, per 3.8, 3.7, 5 |
| `particleSystem.js` | `update(state)`, `draw(ctx)` — T2; the only `Math.random()` consumer; caps: 128 particles per visible room, 512 total |
| `mapRenderer.js` | draws the station map from `roomView` + doors + `reactor` + warnings (3.7) |
| `hudRenderer.js` | updates DOM HUD from state every tick (7.2 table); numbers exact, labels required |
| `overlayRenderer.js` | vignettes, warning flashes, damage shake (3.9) |
