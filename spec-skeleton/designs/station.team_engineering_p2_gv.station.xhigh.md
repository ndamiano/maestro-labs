# engineering.md

## 1. Handoff Summary

This document is the engineering source of truth for building the browser game defined in `gameplay.md` and `visual.md`.

The integration agent should implement:

- A deterministic fixed-timestep simulation.
- A level compiler/validator that makes the designed station function.
- Scalable system modules for atmosphere, power, hull, reactor, drones, items, machines, launch, objectives, warnings, and end states.
- A rendering/HUD layer that reads simulation state without modifying it.
- An audio implementation layer that consumes simulation events.
- A headless test harness and test suite proving the game is complete, playable, and not broken by the core systems.

Important integration principle:

> The simulation owns all gameplay state and all win/lose rules.  
> The renderer and audio layers only observe state and events.

This keeps the game testable in Node, deterministic, and independent of canvas/DOM/audio availability.

---

## 2. High-Level Architecture

### 2.1 Separation of Concerns

The game is split into four layers:

1. **Simulation**
   - Pure gameplay logic.
   - No DOM, no canvas, no audio, no renderer, no random numbers.
   - Fixed timestep: 20 updates/sec.
   - Deterministic.

2. **Input**
   - Translates keyboard events into a simple per-tick input frame.
   - No gameplay logic.

3. **Presentation**
   - Canvas world rendering.
   - DOM HUD.
   - Map rendering.
   - Particles/effects.
   - Reads simulation state.

4. **Audio**
   - SFX and music.
   - Consumes simulation events.
   - Does not alter gameplay.

Why:
- The core game is system-heavy: O2, power, hull, reactor, drones, launch requirements.
- Those systems must be testable without a browser.
- Visual/audio design is already specified; engineering should expose clean state/event contracts.

---

## 3. Required Files

The following files should exist in the final implementation.

```text
/
  index.html
  styles.css
  main.js
  package.json
  assets/
    manifest.json
    audio/
      sfx/
      music/
    sprites/
      player/
      drones/
      machines/
      items/
      icons/
      doors/
    fonts/
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
      droneRenderer.js
      particleSystem.js
      mapRenderer.js
      hudRenderer.js
      overlayRenderer.js
    audio/
      audioManager.js
      musicManager.js
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

### 3.1 File Responsibilities

| File | Responsibility |
|---|---|
| `index.html` | Loads canvas, HUD DOM, audio unlock button/title screen, and `main.js`. |
| `styles.css` | HUD layout, warning styles, end-screen styling, safe-area margins. |
| `main.js` | Wires title screen, input, simulation, renderer, HUD, audio. |
| `src/core/config.js` | All gameplay constants from `gameplay.md`. |
| `src/core/input.js` | Keyboard state and per-tick input frame. |
| `src/core/gameLoop.js` | Fixed-timestep accumulator and render loop. |
| `src/data/levelData.js` | Designed room dimensions, initial room state, door graph, content, machines. |
| `src/data/levelLayout.js` | Deterministic geometry compiler and validator. |
| `src/data/audioEvents.js` | Simulation event to audio asset mapping. |
| `src/state/createInitialState.js` | Creates initial game state from compiled level. |
| `src/state/cloneState.js` | Deep clone helper for tests/debug. |
| `src/simulation/advance.js` | Main simulation tick facade. |
| `src/simulation/*.js` | Individual system modules. |
| `src/render/*.js` | Presentation only. |
| `src/audio/*.js` | Audio implementation only. |
| `tests/*.js` | Validation harness and game-completion tests. |

### 3.2 Cut Files

The following are intentionally not included because they add complexity without improving the designed game:

- No save/load system.
- No pause menu.
- No settings menu.
- No multiplayer.
- No random level generator.
- No tile-based pathfinding.
- No dynamic lighting.
- No 3D/2.5D renderer.
- No complex particle engine beyond room-local effects.
- No audio reverb/3D positional audio system.

Why:
- The station is fixed and small.
- The core loop is systems, not exploration or combat.
- A fixed layout and deterministic simulation are easier to validate.
- Extra features would complicate the test harness without increasing gameplay quality.

---

## 4. Core Engine Contracts

### 4.1 Fixed Timestep

Use:

```js
SIM_HZ = 20
DT = 0.05
```

All rates in `gameplay.md` are per second.

The main loop:

1. Accumulate real elapsed time.
2. Clamp max frame delta to `0.25s` to avoid spiral-of-death after tab sleep.
3. While accumulator >= `DT`, run one simulation tick.
4. Render latest state.

Why:
- All survival rates are time-based.
- Fixed timestep makes tests deterministic.
- Rendering can remain 60 FPS while simulation remains 20 Hz.

---

### 4.2 Input Frame

Each simulation tick receives:

```js
{
  moveX: -1 | 0 | 1,
  moveY: -1 | 0 | 1,
  interactDown: boolean,
  interactPressed: boolean,
  useDown: boolean,
  usePressed: boolean,
  drop: boolean,
  select: null | 0 | 1 | 2 | 3 | 4 | 5
}
```

Controls:

| Input | Action |
|---|---|
| `WASD` / arrows | Move |
| `E` press | Pick up nearest item |
| `E` hold | Channel with nearest interactable |
| `1-6` | Select inventory slot |
| `F` press | Instant use selected item |
| `F` hold | Timed direct use, currently EMP |
| `Q` | Drop selected item |

Why:
- `E` is the primary station-interaction key.
- `F` is for direct item effects.
- `Q` is needed because dropped items must persist.
- `E` press vs hold separates instant pickup from channel actions.

---

### 4.3 Simulation State Contract

The simulation state must be plain serializable data. No functions, no classes, no Sets, no DOM references.

Recommended shape:

```js
{
  meta: {
    version: 1,
    tick: number,
    time: number,
    status: 'running' | 'success' | 'failure',
    debugInvariants: boolean,
    nextEventId: number
  },

  end: null | {
    status: 'success' | 'failure',
    cause: null | string,
    timeSurvived: number,
    stats: object
  },

  player: {
    x: number,
    y: number,
    room: string,
    o2: number,
    integrity: number,
    hasWrench: boolean,
    invulnerable: number,
    selectedSlot: number,
    inventory: [
      { type: string, count: number } | null,
      ...
    ],
    lastDamageSource: null | 'drone' | 'reactor' | 'asphyxia',
    tookDamageThisTick: boolean
  },

  rooms: {
    [roomId]: {
      id: string,
      name: string,
      abbr: string,
      x: number,
      y: number,
      w: number,
      h: number,
      o2: number,
      hull: number,
      breached: boolean,
      powered: boolean,
      powerSource: {
        type: 'none' | 'epc' | 'cell' | 'reactor' | 'powered',
        timeLeft: number | null
      },
      eventWarning: null | {
        eventId: number,
        targetRoom: string,
        damage: number,
        timeLeft: number
      }
    }
  },

  doors: {
    [doorId]: {
      id: string,
      a: string,
      b: string,
      state: 'open' | 'closed' | 'jammed',
      axis: 'x' | 'y',
      x: number,
      y: number,
      gap: number
    }
  },

  machines: {
    [machineId]: {
      id: string,
      room: string,
      type: string,
      repaired: boolean,
      completed: boolean,
      rate: number | null,
      x: number,
      y: number
    }
  },

  droppedItems: [
    {
      id: number,
      type: string,
      room: string,
      x: number,
      y: number
    }
  ],

  power: {
    sources: [
      {
        id: string,
        room: string,
        type: 'epc' | 'cell',
        timeLeft: number
      }
    ],
    nodes: {
      crew: string | null,
      hydro: string | null,
      shuttle: string | null
    }
  },

  reactor: {
    pumpRepaired: boolean,
    coreRepaired: boolean,
    coolantActive: boolean,
    coolantTime: number,
    spinUpComplete: boolean,
    spinUpProgress: number,
    online: boolean,
    heatHazard: boolean,
    onlineEver: boolean
  },

  drones: [
    {
      id: string,
      homeRoom: string,
      room: string,
      x: number,
      y: number,
      state: 'inactive' | 'patrol' | 'alert' | 'attack' | 'disabled',
      active: boolean,
      disabled: boolean,
      patrolIndex: number,
      noPathTimer: number,
      attackCooldown: number,
      path: [string, ...]
    }
  ],

  launch: {
    visible: boolean,
    computerPrimed: boolean,
    fuelInstalled: boolean,
    progress: number,
    lastResetReason: null | string,
    success: boolean,
    requirements: {
      reactorOnline: boolean,
      shuttlePowered: boolean,
      computerPrimed: boolean,
      fuelInstalled: boolean,
      shuttleO2Sufficient: boolean
    }
  },

  objectives: {
    index: number,
    seenRooms: {
      [roomId]: boolean
    },
    stabilizeCrewTimer: number,
    shuttleO2Reached: boolean,
    reactorOnlineEver: boolean,
    completed: {
      [objectiveId]: boolean
    }
  },

  warnings: {
    active: [
      {
        id: string,
        type: string,
        text: string,
        critical: boolean,
        room: string | null,
        timeLeft: number | null
      }
    ],
    trackers: {
      [key]: boolean
    }
  },

  log: [
    {
      id: number,
      time: number,
      type: string,
      text: string,
      audio: string | null,
      critical: boolean
    }
  ],

  stats: {
    systemsRestored: {
      crewO2Generator: boolean,
      hydroO2Recycler: boolean,
      shuttleO2Vent: boolean,
      reactorOnline: boolean,
      launchComputerPrimed: boolean,
      fuelInstalled: boolean
    },
    breachesSealed: number,
    dronesDisabled: number,
    hullPatchesUsed: number,
    powerCellsUsed: number,
    coolantUsed: number,
    empUsed: number,
    launchResets: number
  }
}
```

### 4.4 Simulation Advance Contract

Use:

```js
advance(state, input) -> events[]
```

Rules:

- `advance` may mutate `state`.
- `state` must be created by `createInitialState()`.
- Tests must clone state before running if they need the original.
- `advance` must be deterministic.
- `advance` must not call `Math.random()`.
- `advance` returns simulation events.
- Renderer/audio consume events.

Example event:

```js
{
  type: 'machine_repaired',
  id: 'crew_o2_generator',
  room: 'crew',
  text: 'O2 Generator repaired',
  audio: 'repair_complete',
  critical: false
}
```

Why:
- Events make audio/HUD warnings decoupled from state polling.
- Tests can assert that the right audio events fire without loading audio.

---

## 5. Level Functionality and Geometry

The gameplay designer defined the room graph, room dimensions, initial room state, door states, machines, and content.

Engineering must turn that into a working top-down level.

This is not level design. It is level instantiation and validation.

### 5.1 Coordinate System

Use world coordinates in tile units.

- 1 tile = 0.5 meters.
- Player, drones, doors, machines, and pickups use continuous tile coordinates.
- `x` increases right.
- `y` increases down.

Use point-based movement for simulation.

Why:
- Room interiors have no gameplay-critical blocking obstacles.
- Doors are the only transitions.
- Point movement with door gaps is simpler, deterministic, and testable.
- The renderer can draw a player sprite around the point.

### 5.2 Required Room Coordinates

Use these tile coordinates.

| Room | x | y | w | h |
|---|---:|---:|---:|---:|
| Docking Bay | 4 | 7 | 4 | 4 |
| Crew Quarters | 8 | 5 | 8 | 8 |
| Storage | 10 | 0 | 6 | 5 |
| Cargo Hold | 4 | 0 | 6 | 5 |
| Medbay | 16 | 7 | 6 | 5 |
| Hydroponics | 9 | 13 | 6 | 6 |
| Engineering | 9 | 19 | 6 | 5 |
| Reactor Core | 10 | 24 | 5 | 5 |
| Bridge | 15 | 19 | 6 | 5 |
| Shuttle Bay | 15 | 13 | 8 | 6 |

Why:
- This layout preserves the designed room graph.
- All doors can be placed on shared walls.
- No room interiors overlap.
- The central hub is Crew Quarters.
- The final sequence remains readable: Hydroponics -> Engineering -> Reactor Core -> Bridge -> Shuttle Bay.

### 5.3 Room IDs

Use stable IDs:

```js
docking
crew
storage
cargo
medbay
hydro
engineering
reactor
bridge
shuttle
```

Display names come from `levelData.js`.

### 5.4 Door Data

Doors are computed from room rectangles and edge definitions.

Edge list:

```js
[
  { a: 'docking', b: 'crew', state: 'open' },
  { a: 'crew', b: 'storage', state: 'jammed' },
  { a: 'crew', b: 'medbay', state: 'open' },
  { a: 'crew', b: 'hydro', state: 'closed' },
  { a: 'storage', b: 'cargo', state: 'closed' },
  { a: 'hydro', b: 'engineering', state: 'jammed' },
  { a: 'hydro', b: 'shuttle', state: 'closed' },
  { a: 'engineering', b: 'reactor', state: 'closed' },
  { a: 'engineering', b: 'bridge', state: 'closed' },
  { a: 'bridge', b: 'shuttle', state: 'closed' }
]
```

Door IDs:

```js
door_docking_crew
door_crew_storage
door_crew_medbay
door_crew_hydro
door_storage_cargo
door_hydro_engineering
door_hydro_shuttle
door_engineering_reactor
door_engineering_bridge
door_bridge_shuttle
```

Door gap width:

```js
DOOR_GAP_TILES = 2
```

Why:
- 2 tiles is wide enough for point movement and readable for the player.
- It matches the visual door panel design.

### 5.5 Door Geometry Compiler

For each edge:

1. Find shared side between two room rectangles.
2. Validate shared side overlap >= `DOOR_GAP_TILES`.
3. Compute door center as midpoint of shared side.
4. Assign axis:
   - Shared side vertical: `axis = 'x'`
   - Shared side horizontal: `axis = 'y'`
5. Store door center.

Open door walkable rectangle:

For vertical wall, `axis = 'x'`:

```js
{
  x: wallX - 0.25,
  y: doorY - DOOR_GAP_TILES / 2,
  w: 0.5,
  h: DOOR_GAP_TILES
}
```

For horizontal wall, `axis = 'y'`:

```js
{
  x: doorX - DOOR_GAP_TILES / 2,
  y: wallY - 0.25,
  w: DOOR_GAP_TILES,
  h: 0.5
}
```

Why:
- The door rectangle bridges the two room interiors.
- A point can move through the door only when open.
- Closed/jammed doors are simply not walkable.

### 5.6 Level Validation

`levelLayout.js` must validate the compiled level before the game starts.

Required assertions:

1. Exactly 10 rooms.
2. Room IDs unique.
3. Room dimensions match `gameplay.md`.
4. Room interiors do not overlap.
5. Every door edge connects two distinct rooms.
6. Every door lies on a shared wall.
7. Every door gap fits within the shared wall overlap.
8. The room graph is connected.
9. All rooms are reachable from `docking` if all jammed doors are repaired and all closed doors are opened.
10. Every required machine exists in the correct room.
11. Every required content item exists in the correct room.
12. Total content counts match `gameplay.md`.
13. Power nodes exist only in `crew`, `hydro`, and `shuttle`.
14. Initial door states match `gameplay.md`.
15. Initial room O2/hull values match `gameplay.md`.

Why:
- The gameplay document is the design source of truth.
- A broken level graph would create softlocks or impossible objectives.
- These tests catch coordinate mistakes before gameplay testing.

---

## 6. Content Placement

### 6.1 Machine Placement

Machines are placed automatically by the level compiler.

Rules:

1. Machines are wall-mounted or floor-anchored.
2. Machines do not block movement.
3. Machines must be inside their room.
4. Machines must not overlap door centers by more than `1.5` tiles.
5. Machine positions must be deterministic.

Placement algorithm:

1. For each room, list machines in fixed order.
2. Assign wall slots in cycle: top, right, bottom, left.
3. Place machine inset `0.5` tiles from the wall.
4. Space machines evenly along the wall.
5. If a machine would be too close to a door, shift it along the wall.
6. If no valid position exists, level validation fails.

Why:
- Machines are interactables, not obstacles.
- Deterministic placement keeps tests stable.
- Validation ensures no machine is hidden behind a door.

### 6.2 Pickup Placement

Pickups are placed automatically.

Rules:

1. Pickups must be inside the room.
2. Pickups must not overlap machines, power nodes, or door centers.
3. Pickups must be at least `1.0` tile apart when possible.
4. If a room is too small, minimum spacing may relax to `0.75` tiles.
5. Placement order follows the order in `levelData.js`.
6. No pickup may be placed in a door gap.

Candidate points, in order:

1. Room center.
2. Four corners inset by `1.0` tile.
3. Four edge midpoints inset by `1.0` tile.
4. Quarter-grid points inside room.

Why:
- The designer specified item counts and rooms, not exact pixel positions.
- Automatic placement is scalable and easier to validate.
- Explicit positions would be brittle to small layout changes.

### 6.3 Initial Player Position

Player starts at the center of `docking`.

```js
player.room = 'docking'
player.x = room.x + room.w / 2
player.y = room.y + room.h / 2
```

Initial player stats:

```js
player.o2 = 100
player.integrity = 100
player.hasWrench = false
player.inventory = [null, null, null, null, null, null]
player.selectedSlot = 0
```

Why:
- The Docking Bay is the safe start room.
- The player must pick up the wrench before repairs.
- This matches the visual onboarding prompt: `PICK UP WRENCH`.

---

## 7. Simulation Tick Order

The tick order matters for fairness and testability.

Use this exact order:

1. **Check running state**
   - If status is not `'running'`, return no events.

2. **Advance time**
   - `state.meta.tick += 1`
   - `state.meta.time += DT`
   - Clear per-tick flags.

3. **Hull event warnings and damage**
   - Recalculate active hull event warnings during the 10-second warning window.
   - Apply scheduled damage when event time is reached.
   - Update breached state.
   - Emit breach events.

4. **Player movement**
   - Apply movement input.
   - Resolve collision against room interiors and open door gaps.
   - Determine new current room.

5. **Direct player actions**
   - Pick up nearest item on `interactPressed`.
   - Use selected item on `usePressed` or `useDown`.
   - Drop selected item on `drop`.
   - Update inventory.

6. **Non-launch channels**
   - Resolve nearest channel target while `interactDown` is true.
   - Advance progress.
   - Complete doors, repairs, installs, coolant use, launch computer, fuel line, reactor spin-up, hull patch/seal, power cell install.
   - Consume items only on completion.

7. **Power update**
   - Decrement timed power sources.
   - Remove expired sources.
   - Recompute power propagation through open doors.
   - Emit power loss/expiry events.

8. **Reactor update**
   - Decrement coolant timer if active.
   - Update `coolantActive`.
   - Abort spin-up if coolant expires before completion.
   - Update `online`.
   - Update `heatHazard`.
   - Emit reactor events.

9. **Atmosphere update**
   - Apply room baseline/breach drain.
   - Apply repaired and powered O2 machines.
   - Apply airflow through open doors.
   - Clamp room O2 to `0-100`.

10. **Drone update**
    - Update activation.
    - Update patrol/alert/attack state.
    - Move drones.
    - Apply drone attacks.
    - Emit drone events.

11. **Player vitals update**
    - Apply player O2 change from current room O2.
    - Apply asphyxia if player O2 is 0.
    - Apply reactor heat if applicable.
    - Clamp player stats.
    - Update invulnerability.
    - Set `tookDamageThisTick` if integrity decreased.

12. **Launch update**
    - Evaluate launch requirements.
    - Advance launch channel if player is at launch pad and all requirements are true.
    - Reset launch progress if required.
    - Emit launch reset/success events.

13. **End-state evaluation**
    - If launch success occurred this tick, set success.
    - Else if player integrity <= 0, set failure.
    - Else if time >= 960, set de-orbit failure.

14. **Warnings and event log update**
    - Compute warning transitions.
    - Emit warning audio events.
    - Append important events to log.

15. **Invariants**
    - If debug invariants enabled, validate state.

Why this order:

- Hull damage should affect atmosphere in the same tick.
- Player movement happens before drones so the player can leave dangerous rooms.
- Launch is checked after vitals and drones because launch resets if the player takes damage.
- Success is checked before death and de-orbit to satisfy same-tick precedence.

---

## 8. Movement and Collision

### 8.1 Player Speed

```js
PLAYER_SPEED = 3.5
```

Tiles per second.

Why:
- Drone alert speed is `3.0`.
- The player should be able to outrun a drone, but not feel untouchable.
- `3.5` gives enough margin for door management.

### 8.2 Movement Model

The player is a point.

Each tick:

1. Normalize input vector.
2. Multiply by `PLAYER_SPEED * DT`.
3. Try moving x and y separately.
4. For each axis, if the proposed point is walkable, apply it.
5. Otherwise, keep the original axis value.

This gives sliding along walls.

### 8.3 Walkable Check

A point is walkable if it is inside:

- Any room interior rectangle, or
- Any open door rectangle.

Use small epsilon for rectangle containment.

### 8.4 Room Assignment

The player’s `room` is the room interior containing the point.

Special rule:

- If the point is inside a door gap but not fully inside a new room interior, keep the previous room.
- Change room only when the point enters the new room interior.

Why:
- Prevents flicker in O2, power, drone room, and current-room HUD.
- Door crossing remains stable.

### 8.5 Drone Movement

Drones use the same walkable check.

Drones can pass only through open doors.

If a door closes while a drone is moving, the drone stops and re-paths next tick.

Why:
- Drones are not required to do tile-level obstacle avoidance.
- The room graph is the authoritative threat path.

---

## 9. Doors System

### 9.1 Door States

```js
open
closed
jammed
```

Behavior:

| State | Movement | Airflow | Power | Drones |
|---|---:|---:|---:|---:|
| open | allowed | allowed | allowed | allowed |
| closed | blocked | blocked | blocked | blocked |
| jammed | blocked | blocked | blocked | blocked |

### 9.2 Door Channels

Door channel times:

| Action | Time | Requirements |
|---|---:|---|
| Open closed door | 1s | none |
| Close open door | 1s | none |
| Repair jammed door | 5s | Wrench |

Rules:

- Jammed doors cannot be opened or closed.
- Repairing a jammed door changes it to `closed`.
- Progress is retained if the player pauses.
- Door state changes affect systems in the same tick after channel completion.

Why:
- Door management is a core survival mechanic.
- Jammed doors teach repair without requiring complex item use.
- Progress retention is forgiving and matches machine repair behavior.

### 9.3 Door Interaction Target

The player can interact with a door if:

- Door center is within `1.5` tiles, or
- Player is in one of the adjacent rooms and within `2.0` tiles of the door center.

Why:
- Door frames are on walls.
- The player may approach from either side.

---

## 10. Atmosphere System

### 10.1 Room O2 Range

```js
room.o2 in [0, 100]
```

### 10.2 Baseline Drain

For every room:

```js
if room.breached:
  delta -= 15 * DT
else:
  delta -= 0.5 * DT
```

Why:
- This directly matches `gameplay.md`.
- Breach drain should dominate small generators.

### 10.3 O2 Machine Generation

Machines generate O2 only if:

- Machine repaired.
- Room powered.

Machine rates:

| Machine | Room | Rate |
|---|---|---:|
| Crew O2 Generator | crew | +8/sec |
| Hydroponics O2 Recycler | hydro | +4/sec |
| Shuttle O2 Vent | shuttle | +6/sec |

A room may be breached and still powered. In that case, generation happens but breach drain usually dominates.

Why:
- The gameplay document says breach drain usually overwhelms small generators, not that machines stop.

### 10.4 Airflow Between Rooms

For every open door:

```js
a = room A
b = room B
diff = a.o2 - b.o2
if abs(diff) < 0.0001:
  transfer = 0
else:
  transferRate = 5 * abs(diff) / 100
  transfer = transferRate * DT
```

Transfer from higher O2 room to lower O2 room.

Important:

- Compute all transfers using O2 values at the start of the airflow phase.
- Apply all transfers after computing them.
- Then clamp room O2 to `0-100`.

Why simultaneous:
- Sequential door updates can depend on iteration order.
- Simultaneous application is deterministic and fair.

Closed and jammed doors transfer zero O2.

### 10.5 Player O2 Change

Use current room O2 after atmosphere update.

Thresholds:

| Room O2 | Player O2 change |
|---:|---:|
| >= 60 | +0.5/sec |
| 30 to 59.999 | -0.5/sec |
| 1 to 29.999 | -1.5/sec |
| < 1 | -3/sec |

Use `< 1` for the lowest bucket because O2 is continuous.

Why:
- The document says `0` gives -3/sec.
- A room at `0.4` O2 is effectively zero-air for gameplay purposes.

Clamp player O2 to `0-100`.

---

## 11. Player Vitals System

### 11.1 Player Stats

```js
player.o2 in [0, 100]
player.integrity in [0, 100]
```

### 11.2 Asphyxia

If player O2 <= 0:

```js
player.integrity -= 5 * DT
player.lastDamageSource = 'asphyxia'
```

### 11.3 Reactor Heat

If:

- `reactor.heatHazard === true`, and
- `player.room === 'reactor'`,

then:

```js
player.integrity -= 5 * DT
player.lastDamageSource = 'reactor'
```

### 11.4 Drone Damage

Drone attack damage:

```js
20 integrity
```

Rules:

- Only applies if player invulnerability is not active.
- On damage:
  - `player.invulnerable = 0.5`
  - `player.lastDamageSource = 'drone'`
  - drone `attackCooldown = 1.0`

Invulnerability blocks drone attacks only. It does not block reactor heat or asphyxia.

Why:
- The document specifically says damage invulnerability after drone damage.
- Environmental hazards should not be framed.

### 11.5 Integrity Death

If `player.integrity <= 0`:

- Set status to failure.
- Cause comes from `player.lastDamageSource`.
- If `lastDamageSource` is null, use `'integrity_failure'`.

Possible failure causes:

```js
asphyxia
drone_attack
reactor_heat
integrity_failure
deorbit
```

Use `drone_attack`, not `drone`, in end-screen data to match visual cause table.

---

## 12. Items and Inventory

### 12.1 Inventory Size

```js
INVENTORY_SIZE = 6
```

Stack limits:

| Item | Max Stack |
|---|---:|
| O2 Tank | 5 |
| Medkit | 3 |
| Hull Patch | 4 |
| Power Cell | 3 |
| EMP Charge | 3 |
| Coolant Cell | 2 |
| Fuel Rod | 1 |

Wrench does not occupy a slot.

### 12.2 Wrench

- Initial state: `hasWrench = false`.
- Picking up the wrench sets `hasWrench = true`.
- Wrench cannot be dropped.
- Wrench cannot be lost.
- Required for:
  - Machine repairs.
  - Jammed door repair.
  - Hull patch/seal.

Not required for:
- Door open/close.
- Power cell install.
- Coolant cell use.
- Fuel line install.
- Launch computer.
- Reactor spin-up.

Why:
- The item table says wrench is required for repairs and jammed doors.
- Installation and operation actions are separate.

### 12.3 Pickup

On `interactPressed`:

1. Find nearest dropped item within `1.0` tile.
2. If inventory can accept item:
   - Add to existing stack if below max stack.
   - Otherwise use first empty slot.
   - Remove dropped item.
   - Emit `pickup` event.
3. If inventory full:
   - Do not pick up.
   - Emit `ui_error` event.
   - HUD shows `INVENTORY FULL`.

Special wrench:

- If item type is `wrench`, set `player.hasWrench = true`.
- Do not place in inventory.

### 12.4 Drop

On `drop`:

1. If selected slot is empty, do nothing.
2. Remove one item from selected slot.
3. Create dropped item at player position.
4. Emit `drop` event.

Dropped items:

- Persist forever.
- Do not despawn.
- Do not move.
- Can be picked up again.

Why:
- Prevents softlocks from inventory mistakes.
- Required by fairness rules.

### 12.5 Direct Item Use

`F` press:

| Item | Effect |
|---|---|
| O2 Tank | +50 player O2, instant |
| Medkit | +50 integrity, instant |
| EMP Charge | Start 1s EMP channel if valid |
| Others | UI error |

Rules:

- O2 Tank cannot be used if player O2 is 100.
- Medkit cannot be used if integrity is 100.
- EMP can only be used if at least one active drone is in the player’s current room.
- Consumed only on successful completion.

EMP channel:

- Duration: 1s.
- Requires `F` held.
- Requires at least one active drone in current room at start and completion.
- On completion:
  - Disable all active drones in current room.
  - Consume EMP.
  - Emit `emp` event.
- If condition fails during the 1s, channel cancels and item is not consumed.

Why:
- EMP is a short vulnerability action, not an instant button.
- Consuming only on completion prevents losing an EMP if the player releases input.

---

## 13. Channels System

A channel is a timed action.

Types:

- Repair.
- Door open/close.
- Door jammed repair.
- Hull patch/seal.
- Power cell install.
- Coolant cell use.
- Reactor spin-up.
- Launch computer.
- Fuel line.
- Launch pad.
- EMP use.

### 13.1 Channel Progress Storage

Use a map:

```js
state.channels = {
  [channelId]: {
    progress: number,
    duration: number
  }
}
```

Channel IDs are stable, for example:

```js
door_crew_storage:repair
machine:crew_o2_generator:repair
hull:storage
power_node:hydro:install
reactor:spinup
launch:computer
launch:pad
item:emp
```

Rules:

- Progress is retained if paused.
- Progress resets only when explicitly specified.
- Completion applies effect and removes channel progress.
- Launch pad progress resets on interruption/failure.

Why:
- Most repairs should retain progress.
- Launch is the only major reset-on-failure channel.

### 13.2 Consumable Item Rule

For channels requiring a consumable item:

- Required item must exist in inventory while the channel is active.
- If missing, channel pauses.
- Item is consumed only on completion.
- If interrupted, item is not consumed.

No item locking is required.

Why:
- Simpler to implement and test.
- The player cannot lose the item because dropped items persist.
- If the player uses or drops the required item, the channel simply cannot complete.

### 13.3 Wrench Rule

For wrench-required channels:

- If `player.hasWrench` is false, channel is invalid.
- Progress does not advance.
- HUD prompt shows `REQUIRES WRENCH`.

Why:
- Wrench is required before repairs become possible.

---

## 14. Machines System

### 14.1 Machine List

| Machine ID | Room | Type | Time | Effect |
|---|---|---|---:|---|
| `crew_o2_generator` | crew | O2 generator | 5s repair | +8 O2/sec when powered |
| `hydro_o2_recycler` | hydro | O2 recycler | 6s repair | +4 O2/sec when powered |
| `shuttle_o2_vent` | shuttle | O2 vent | 5s repair | +6 O2/sec when powered |
| `reactor_coolant_pump` | engineering | coolant pump | 5s repair | enables coolant use |
| `reactor_core` | reactor | reactor core | 8s repair | enables spin-up |
| `launch_computer` | bridge | console | 15s channel | primes launch computer |
| `fuel_line` | shuttle | fuel install | 10s channel | installs fuel rod |
| `launch_pad` | shuttle | launch pad | 30s channel | final launch |

Power nodes are not standard machines but are interactables:

| Power Node | Room |
|---|---|
| `power_node_crew` | crew |
| `power_node_hydro` | hydro |
| `power_node_shuttle` | shuttle |

### 14.2 Machine Interaction Range

Machine interact range:

```js
1.5 tiles
```

Why:
- Machines are wall-anchored.
- 1.5 tiles gives a comfortable interaction radius.

### 14.3 Machine States

Each machine has:

```js
repaired: boolean
completed: boolean
```

Meaning:

- `repaired` is for machines that start damaged.
- `completed` is for one-time operational channels, such as launch computer or fuel line.

Examples:

- O2 generator:
  - `repaired = true` after repair.
  - `completed = true` after repair.
- Launch computer:
  - `repaired = false` initially.
  - `completed = true` after 15s channel.
- Fuel line:
  - `completed = true` after fuel rod installed.

Why:
- Some machines need repair, some need operation, some both.
- A uniform state shape keeps rendering and tests simple.

### 14.4 Repair Channels

Repair channels require:

- Wrench.
- Machine not already repaired.
- Player within range.

Progress is retained if paused.

On completion:

- Set machine repaired/completed where appropriate.
- Emit `repair_complete` event.
- Update stats.

### 14.5 Launch Computer

Requirements:

- Bridge powered.
- Player within range.
- Channel not already complete.

Time:

```js
15s
```

Progress retained if paused.

On completion:

- `launch.computerPrimed = true`
- Requirement stays complete permanently.
- Emit `launch_requirement` event.

Why:
- The document says progress is retained and completion stays complete.

### 14.6 Fuel Line

Requirements:

- Fuel Rod in inventory.
- Player within range.
- Fuel not already installed.

Time:

```js
10s
```

Progress retained if paused.

On completion:

- Consume fuel rod.
- `launch.fuelInstalled = true`
- Requirement stays complete permanently.
- Emit `launch_requirement` event.

Why:
- Fuel rod is the only fuel rod in the world.
- Losing it should be avoidable because dropped items persist, but once installed it is final.

---

## 15. Power System

### 15.1 Power Model

Power is binary per room:

```js
room.powered = boolean
```

Power propagates only through open doors.

### 15.2 Power Sources

| Source | Type | Duration |
|---|---|---:|
| Start Emergency Power Cell | epc | 400s |
| Player Power Cell | cell | 400s |
| Reactor | reactor | infinite while coolant active and spin-up complete |

Initial state:

- `crew` has start EPC installed.
- `power.nodes.crew = 'epc_start'`
- `power.sources[0] = { id: 'epc_start', room: 'crew', type: 'epc', timeLeft: 400 }`

### 15.3 Power Nodes

Power nodes exist in:

```js
crew
hydro
shuttle
```

Rules:

- A node can hold one source at a time.
- Start EPC occupies `crew`.
- When start EPC expires, `crew` node becomes empty.
- Player power cells can be installed only into an empty node.
- A node being empty means no local source is installed.
- A room being powered by propagation does not prevent installing a cell in an empty node.

Why:
- The gameplay phrase “unpowered node” should mean the node has no local source.
- If propagated power blocked installation, power cells would be useless in connected rooms.

### 15.4 Power Cell Install

Requirements:

- Power Cell in inventory.
- Target node empty.
- Player within range.

Time:

```js
2s
```

Consumes power cell only on completion.

On completion:

- Add source:
  ```js
  {
    id: 'cell_' + state.meta.tick,
    room: nodeRoom,
    type: 'cell',
    timeLeft: 400
  }
  ```
- Set node occupancy.
- Emit `power_install` event.

### 15.5 Power Propagation Algorithm

Every tick:

1. Create empty `powered` set.
2. Add rooms with active timed sources.
3. If reactor is online, add `reactor` room.
4. Queue seeded rooms.
5. BFS through open doors:
   - For each powered room, inspect doors.
   - If door is open and adjacent room not powered, mark it powered and enqueue it.

After propagation:

- Update `room.powered`.
- Compute `room.powerSource` for HUD.

Power source display rules:

| Condition | Display |
|---|---|
| Local EPC active | `EPC mm:ss` |
| Local power cell active | `CELL mm:ss` |
| Reactor room and reactor online | `REACTOR` |
| Powered but no local source | `POWERED` |
| Not powered | `NO POWER` |

Why:
- This matches the visual power state grammar.
- BFS is simple and matches the designed power puzzle.

### 15.6 Power Loss

If a room was powered previous tick and is not powered current tick:

- Emit `power_loss` event if any rooms lost power.
- Log major power loss.

If a timed source expires:

- Emit `power_cell_expire` event.
- Remove source.
- Clear node if occupied by that source.

Why:
- Power loss is a major survival event.
- Audio must fire on transition, not every tick.

---

## 16. Reactor System

### 16.1 Reactor State

```js
reactor = {
  pumpRepaired: false,
  coreRepaired: false,
  coolantActive: false,
  coolantTime: 0,
  spinUpComplete: false,
  spinUpProgress: 0,
  online: false,
  heatHazard: false,
  onlineEver: false
}
```

### 16.2 Reactor Requirements

To bring reactor online:

1. Repair `reactor_coolant_pump` in Engineering.
2. Use Coolant Cell on pump.
3. Repair `reactor_core` in Reactor Core.
4. Complete reactor spin-up.
5. Coolant timer must be greater than 0.

### 16.3 Coolant Pump Repair

- Room: engineering.
- Time: 5s.
- Requires wrench.
- On completion: `reactor.pumpRepaired = true`.

### 16.4 Coolant Cell Use

Requirements:

- Pump repaired.
- Coolant Cell in inventory.
- Player within range.

Time:

```js
5s
```

On completion:

- Consume coolant cell.
- Set:
  ```js
  reactor.coolantTime = 180
  reactor.coolantActive = true
  ```
- Do not add to existing timer.
- Emit `coolant_used` or `repair_complete` event; audio can use `reactor_spinup`? No, use `power_install`? Better: use `reactor_online` only when online. For coolant use, use `reactor_spinup`? The audio list does not have `coolant_used`. Use `power_install` is wrong. Add semantic event with audio `reactor_spinup` is also wrong. Use `repair_complete`? Coolant use is not repair. Use `ui_select`? no.

Solution: simulation can emit event type `coolant_applied` with audio `reactor_heat`? No.

The visual SFX list does not include a dedicated coolant applied sound. It includes `coolant_low`, `coolant_expired`, `reactor_spinup`, `reactor_online`. For coolant application, use `repair_complete` as a generic completion blip? That may be confusing. Better to use `power_install` because a coolant cell is being installed into the pump. However, `power_install` is semantically power.

Cleanest: add an internal event audio name `coolant_apply` but if no asset exists, audio manager maps it to `repair_complete`. To avoid expanding visual SFX list, map to `repair_complete`.

So:

- Emit event:
  ```js
  {
    type: 'coolant_applied',
    text: 'Reactor coolant applied',
    audio: 'repair_complete'
  }
  ```

Why:
- The audio designer did not provide a dedicated coolant-apply SFX.
- `repair_complete` is a safe mechanical completion sound.

### 16.5 Reactor Core Repair

- Room: reactor.
- Time: 8s.
- Requires wrench.
- On completion: `reactor.coreRepaired = true`.

### 16.6 Reactor Spin-Up

Requirements:

- Core repaired.
- Coolant active.
- Player within range of reactor core.

Time:

```js
20s
```

Progress:

- `reactor.spinUpProgress` in seconds, `0-20`.
- Advances only while all requirements true and player holding E.
- If paused, progress is retained.
- If coolant expires before completion:
  - `spinUpProgress = 0`
  - `spinUpComplete = false`
  - Emit event log: `Reactor spin-up aborted`
  - Audio: `launch_reset` is too strong; use `ui_error`.
  - Also `coolant_expired` fires.

On completion:

- `spinUpComplete = true`
- If coolant active, `online = true`
- `onlineEver = true`
- Emit `reactor_online` event.

Why:
- The document says coolant expiry during spin-up aborts and resets progress.

### 16.7 Reactor Online

```js
reactor.online = reactor.coolantActive && reactor.spinUpComplete
```

While online:

- Reactor provides power to `reactor` room.
- Power propagates through open doors.
- No heat hazard.

### 16.8 Coolant Timer

While coolant active:

```js
reactor.coolantTime -= DT
```

If `coolantTime <= 0`:

- `coolantTime = 0`
- `coolantActive = false`
- If `spinUpComplete`:
  - `online = false`
  - `heatHazard = true`
- Else:
  - `heatHazard = false`
- Emit `coolant_expired` event.

Using a new coolant cell while heat is active:

- Sets `coolantTime = 180`.
- If `spinUpComplete`, `online = true`.
- `heatHazard = false`.

Why:
- The second coolant cell is the recovery action.

### 16.9 Heat Hazard

Heat hazard occurs only if:

```js
reactor.spinUpComplete === true
reactor.coolantActive === false
```

If player is in `reactor` room:

- Integrity drains 5/sec.
- `lastDamageSource = 'reactor'`.

If reactor never spun up and coolant expires:

- No heat hazard.

Why:
- The document says if reactor is offline normally, no heat hazard.
- Heat is a consequence of a spun-up reactor losing coolant.

---

## 17. Hull and Breach System

### 17.1 Hull Range

```js
room.hull in [0, 100]
```

Breach condition:

```js
room.breached = room.hull <= 0
```

### 17.2 Breach Effects

If breached:

- Room O2 drain becomes 15/sec.
- Map shows breach state.
- Event log records breach.
- Warning banner may show breach.
- Audio `breach` plays on transition into breach.

### 17.3 Hull Patch

Requirements:

- Hull Patch in inventory.
- Wrench.
- Target room accessible/selected.
- Room not already hull 100 and unbreached.

Two actions:

| Situation | Time | Effect |
|---|---:|---|
| Hull > 0 | 3s | hull += 40, max 100 |
| Breached | 4s | hull = 60, breached = false |

Consumes Hull Patch only on completion.

If interrupted:

- Progress retained.
- Hull Patch not consumed.

On successful seal of a breach:

- Increment `stats.breachesSealed`.
- Emit `hull_patch` event.

Why:
- Patching must be intentional and consumable.
- Sealing a breach should be clearly logged for success stats.

### 17.4 Scheduled Hull Events

Events are fixed.

| Event | Warning At | Damage At |
|---|---:|---:|
| Event 1 | 230s | 240s |
| Event 2 | 470s | 480s |
| Event 3 | 710s | 720s |

Each warning lasts 10 seconds.

### 17.5 Event Target Selection

General rules:

- Never target the room the player is currently in.
- Do not target a room that is already breached.
- If no valid target exists, skip that damage.
- Event damage cannot raise hull.
- Event damage can cause breach.

#### Event 1

Candidates in order:

1. Storage -30
2. Cargo Hold -30
3. Crew Quarters -20

Choose first valid candidate.

#### Event 2

Two independent damages:

Primary 1:

- Medbay -30
- Fallback: Crew Quarters, Shuttle Bay, Storage, Engineering, Bridge, using -30.

Primary 2:

- Hydroponics -30
- Fallback: Crew Quarters, Shuttle Bay, Storage, Engineering, Bridge, using -30.

Avoid applying both damages to the same room in the same event.

#### Event 3

Candidates in order:

1. Shuttle Bay -50
2. Crew Quarters -20
3. Hydroponics -20

Choose first valid candidate.

### 17.6 Warning Behavior

During warning window:

- Recalculate target every tick using current state.
- If target changes, update warning banner.
- Audio `hull_event_warning` plays once when warning first appears.
- HUD shows target room and countdown.

Why:
- The player may move into a warned room.
- Recalculating keeps the rule “never target current player room” fair.

### 17.7 Damage Application

At damage time:

1. Select target using current state.
2. If no target, skip.
3. Apply damage:
   ```js
   room.hull = max(0, room.hull - damage)
   ```
4. If hull becomes 0:
   - Set breached.
   - Emit `breach` event.
5. Log event.

Why:
- Applying damage at event time, not warning time, prevents stale damage.

---

## 18. Drone System

### 18.1 Drone Count

Exactly two drones.

| Drone | Home Room | Activation |
|---|---|---|
| Drone A | cargo | player first enters cargo |
| Drone B | shuttle | player first enters shuttle |

No other enemies.

### 18.2 Drone States

```js
inactive
patrol
alert
attack
disabled
```

### 18.3 Inactive

- Does not move.
- Does not attack.
- Activates only by its activation condition.

Activation:

- When player room becomes drone home room.
- Set `active = true`.
- Set state to `patrol`.
- Emit `drone_activate` event.

Why:
- Drones are avoidable by never entering their home room.

### 18.4 Patrol

Speed:

```js
2.5 tiles/sec
```

Patrol waypoints are generated deterministically per home room:

1. Room center.
2. Top-left inset.
3. Bottom-right inset.

Drone moves to current waypoint. On arrival within `0.5` tile, selects next.

If player is in same room:

- Enter alert state.
- Emit `drone_alert` event.

### 18.5 Alert

Speed:

```js
3.0 tiles/sec
```

Behavior:

- If player in same room:
  - Move directly toward player.
- If player in different room:
  - Compute room-graph path through open doors.
  - Move toward next door in path.
- If no path exists:
  - Start/increment `noPathTimer`.
  - After 3 seconds, return to patrol.
  - Reset `noPathTimer` if a path exists.

Why:
- The document says drones use room graph pathfinding.
- Returning to patrol after 3 seconds prevents drones from permanently camping at doors.

### 18.6 Attack

If drone is within:

```js
1.0 tile
```

of player and attack cooldown is 0:

- Attempt attack.
- If player invulnerable:
  - No damage.
  - No cooldown.
- If not invulnerable:
  - Deal 20 integrity damage.
  - Set player invulnerability 0.5s.
  - Set drone attack cooldown 1.0s.
  - Set state to `attack` for visual purposes.
  - Emit `drone_attack` event.

Why:
- Invulnerability should not waste the drone’s attack cooldown.
- The drone can immediately retry after i-frames end, but no damage occurs.

### 18.7 Disabled

- Permanent.
- Does not move.
- Does not attack.
- Does not reactivate.
- Increment `stats.dronesDisabled`.

### 18.8 Pathfinding

Use BFS on room graph.

Graph edges exist only for doors in state `open`.

Path target:

- If same room as player: target player position.
- If different room: target next door center.
- Recompute path when:
  - Drone room changes.
  - Player room changes.
  - A door state changes.
  - Every tick is acceptable for this game size.

No tile-level pathfinding.

Why:
- The station is small.
- Room graph pathing is readable and matches the design.
- Drones do not need to avoid internal obstacles because interiors have none.

### 18.9 Drone Avoidance Without EMP

The simulation must allow launch without EMP.

A valid strategy is:

1. Enter Shuttle Bay.
2. Drone B activates.
3. Move player toward Bridge door.
4. Drone follows.
5. Enter Bridge.
6. Close Bridge-Shuttle door.
7. Drone loses path and returns to patrol after 3s.
8. Keep Bridge-Shuttle closed.
9. Keep Hydro-Shuttle open for power/O2 if needed.
10. Launch from Shuttle Bay.

The test suite should verify this is possible.

Why:
- `gameplay.md` explicitly requires launch to be possible without EMP.

---

## 19. Launch System

### 19.1 Launch Requirements

Launch requires all of the following simultaneously:

```js
reactor.online === true
rooms.shuttle.powered === true
launch.computerPrimed === true
launch.fuelInstalled === true
rooms.shuttle.o2 >= 60
```

### 19.2 Launch Checklist Visibility

Checklist becomes visible when any of these occur:

- Player enters `bridge`.
- Player enters `shuttle`.
- Reactor has been online at least once.

Once visible, it stays visible.

Why:
- The document says this exact visibility rule.

### 19.3 Launch Pad Channel

Location:

- `shuttle` room.
- `launch_pad` machine position.

Duration:

```js
30s
```

Progress:

- Store as percent `0-100`.
- Advances only while:
  - Player is in `shuttle` room.
  - Player is within `1.5` tiles of launch pad.
  - Player holds `E`.
  - All launch requirements are true.
  - Player did not take damage this tick.

If progress reaches 100:

- Set `launch.success = true`.
- Emit `launch_success` event.
- End state success.

### 19.4 Launch Reset

If launch progress > 0 and any of the following occur:

- Player leaves launch pad range.
- Player takes damage.
- Reactor offline.
- Shuttle unpowered.
- Launch computer not primed.
- Fuel not installed.
- Shuttle O2 < 60.

Then:

- Reset `launch.progress = 0`.
- Set `launch.lastResetReason`.
- Increment `stats.launchResets`.
- Emit `launch_reset` event.

Reset reason priority:

1. `PLAYER DAMAGED`
2. `LEFT PAD`
3. `REACTOR OFFLINE`
4. `SHUTTLE UNPOWERED`
5. `COMPUTER NOT PRIMED`
6. `FUEL MISSING`
7. `SHUTTLE O2 LOW`

Why:
- The player needs to know exactly what broke.
- Damage is the most urgent reason.

### 19.5 Paused vs Reset

- If player stops holding `E` but remains at pad and all requirements remain true:
  - Progress pauses.
  - Do not reset.
- If player leaves pad:
  - Reset.

Why:
- Releasing E should not punish the player.
- Leaving the pad is a clear launch interruption.

### 19.6 Same-Tick Precedence

If launch success and player death occur on the same simulation tick:

- Success wins.

If launch completes exactly at 960s:

- Success wins over de-orbit failure.

Implementation:

- Evaluate success before death and de-orbit.

Why:
- Required by `gameplay.md`.

---

## 20. Objectives System

### 20.1 Objective Sequence

Use this exact sequence:

1. Repair Crew O2 Generator
2. Stabilize Crew Atmosphere
3. Reach Hydroponics
4. Restore Hydroponics O2 Recycler
5. Bring Reactor Online
6. Prime Launch Computer
7. Install Shuttle Fuel
8. Pressurize Shuttle
9. Launch Shuttle

### 20.2 Objective Completion Rules

| Objective | Completion |
|---|---|
| Repair Crew O2 Generator | `crew_o2_generator.repaired === true` |
| Stabilize Crew Atmosphere | `rooms.crew.o2 >= 60` continuously for 5s |
| Reach Hydroponics | Player enters `hydro` |
| Restore Hydroponics O2 Recycler | `hydro_o2_recycler.repaired === true` |
| Bring Reactor Online | `reactor.online === true` |
| Prime Launch Computer | `launch.computerPrimed === true` |
| Install Shuttle Fuel | `launch.fuelInstalled === true` |
| Pressurize Shuttle | `rooms.shuttle.o2 >= 60` at least once |
| Launch Shuttle | `launch.success === true` |

Rules:

- Objectives advance only forward.
- Once an objective completes, it does not un-complete.
- `Pressurize Shuttle` completes once Shuttle O2 reaches 60, even if it later drops.

Why:
- The HUD should guide the player without regressing.
- Launch requirements can still fail later; the checklist handles that.

### 20.3 Objective HUD

Display next incomplete objective.

When all objectives complete, show:

```js
OBJECTIVE: SHUTTLE LAUNCHED
```

or similar.

---

## 21. Warnings and Event Log

### 21.1 Warning Types

Use these warning types:

```js
player_o2_low
player_o2_critical
integrity_low
integrity_critical
room_o2_low
room_breach
power_source_low
coolant_low
coolant_expired
hull_event_warning
deorbit_warning
launch_reset
```

### 21.2 Warning Thresholds

| Warning | Trigger |
|---|---|
| Player O2 low | player O2 < 25 |
| Player O2 critical | player O2 < 10 |
| Integrity low | integrity < 25 |
| Integrity critical | integrity < 10 |
| Room O2 low | current room O2 < 30 |
| Room breach | current room breached |
| Power source low | local timed source < 60s |
| Coolant low | reactor coolant active and < 30s |
| Coolant expired | reactor coolant just expired |
| Hull event | scheduled event warning active |
| De-orbit | time remaining < 120s |
| Launch reset | launch progress reset |

### 21.3 Warning Priority

Display max two warnings.

Priority order:

1. `player_o2_critical`
2. `integrity_critical`
3. `launch_reset`
4. `room_breach`
5. `coolant_expired`
6. `coolant_low`
7. `hull_event_warning`
8. `power_source_low`
9. `deorbit_warning`
10. `player_o2_low`
11. `integrity_low`
12. `room_o2_low`

Why:
- The visual document defines a priority system.
- This prevents warning spam.

### 21.4 Audio Warning Triggers

Audio plays when a warning enters active state.

Do not play every tick.

Use state trackers:

```js
state.warnings.trackers.player_o2_critical = boolean
```

When transition from false to true, emit audio event.

When transition from true to false, stop looping warning sounds if applicable.

Looping sounds:

- `o2_low`
- `o2_critical`
- `integrity_low`
- `integrity_critical`
- `coolant_low`

One-shot sounds:

- `breach`
- `power_loss`
- `power_cell_expire`
- `hull_event_warning`
- `deorbit_warning`
- `launch_reset`
- `drone_activate`
- `drone_alert`
- `drone_attack`
- `coolant_expired`
- `reactor_online`
- `game_over`
- `launch_success`

Why:
- Persistent states need loops.
- Discrete events need one-shots.
- This matches the visual/audio design.

### 21.5 Event Log

Store full log in state for tests.

HUD displays last 5.

Each entry:

```js
{
  id: number,
  time: number,
  type: string,
  text: string,
  audio: string | null,
  critical: boolean
}
```

Important events must be logged.

Minor movement events should not be logged.

---

## 22. End States

### 22.1 Success

Success occurs when:

```js
launch.success === true
```

End state:

```js
{
  status: 'success',
  cause: null,
  timeSurvived: state.meta.time,
  stats: state.stats
}
```

Success screen data:

- Time used.
- Day.
- Systems restored.
- Drones disabled.
- Breaches sealed.

### 22.2 Failure

Failure occurs if:

1. Player integrity <= 0.
2. Time >= 960 and launch not complete.

Cause values:

```js
asphyxia
drone_attack
reactor_heat
integrity_failure
deorbit
```

Failure screen data:

- Cause.
- Time survived.
- Systems restored.

### 22.3 No Respawn

There is no mid-run retry.

Restart button returns to a fresh initial state.

Why:
- Required by gameplay design.

---

## 23. Simulation Event List

The simulation emits semantic events. Audio and HUD consume them.

Important events:

| Event Type | Audio | When |
|---|---|---|
| `pickup` | `pickup` | Item picked up |
| `drop` | `drop` | Item dropped |
| `inventory_full` | `ui_error` | Pickup blocked |
| `invalid_use` | `ui_error` | Invalid item use |
| `door_open` | `door_open` | Door opens |
| `door_close` | `door_close` | Door closes |
| `door_repaired` | `door_repair` | Jammed door repaired |
| `repair_start` | `repair_start` | Channel starts |
| `repair_tick` | `repair_tick` | Channel 25/50/75% |
| `repair_complete` | `repair_complete` | Repair completes |
| `hull_patch` | `hull_patch` | Hull patch/seal completes |
| `power_install` | `power_install` | Power cell installed |
| `power_cell_expire` | `power_cell_expire` | Timed power source expires |
| `power_loss` | `power_loss` | Rooms lose power |
| `reactor_coolant_applied` | `repair_complete` | Coolant cell used |
| `reactor_spinup_start` | `reactor_spinup` | Spin-up channel starts |
| `reactor_online` | `reactor_online` | Reactor comes online |
| `coolant_low` | `coolant_low` | Coolant enters <30s |
| `coolant_expired` | `coolant_expired` | Coolant reaches 0 |
| `reactor_heat` | `reactor_heat` | Heat hazard begins |
| `drone_activate` | `drone_activate` | Drone first activates |
| `drone_alert` | `drone_alert` | Drone enters alert |
| `drone_attack` | `drone_attack` | Drone damages player |
| `emp` | `emp` | EMP disables drones |
| `breach` | `breach` | Room becomes breached |
| `hull_event_warning` | `hull_event_warning` | Hull event warning begins |
| `objective_complete` | `objective_complete` | Main objective completes |
| `launch_requirement` | `launch_requirement` | Launch checklist item becomes true |
| `launch_reset` | `launch_reset` | Launch progress resets |
| `launch_success` | `launch_success` | Launch completes |
| `game_over` | `game_over` | Failure occurs |
| `deorbit_warning` | `deorbit_warning` | Time remaining <120s |

Why:
- This gives audio a stable contract.
- Tests can verify required audio events without loading audio assets.

---

## 24. Audio Implementation

### 24.1 Audio Architecture

Use:

- `AudioManager` for SFX.
- `MusicManager` for layered music.

Both are created after user gesture on title screen.

Why:
- Browser autoplay policies require user interaction.

### 24.2 Asset Manifest

`assets/manifest.json` should map event names to files.

Example:

```json
{
  "audio": {
    "sfx": {
      "pickup": "audio/sfx/pickup.ogg",
      "breach": "audio/sfx/breach.ogg"
    },
    "music": {
      "base": "audio/music/base.ogg",
      "low_o2": "audio/music/low_o2.ogg",
      "reactor": "audio/music/reactor.ogg"
    }
  }
}
```

If an asset is missing:

- Audio manager should not crash.
- It should log a console warning and skip.

Why:
- Visual designer owns assets; engineering must be resilient to missing files during integration.

### 24.3 SFX Playback

`AudioManager.play(name, options)`.

Options:

```js
{
  pan: number | null,
  room: string | null
}
```

Simple positional rule:

- If `pan` is provided, use `StereoPannerNode`.
- Clamp pan to `-1..1`.
- If no pan, center.

Cut:

- No complex 3D audio.
- No reverb.
- No per-sound distance falloff system.

Why:
- The game is short and top-down.
- Simple pan is enough for drone/machine positioning.
- Complex audio would add integration risk.

### 24.4 Looping Warnings

`AudioManager.startLoop(name)`  
`AudioManager.stopLoop(name)`

Loops:

- `o2_low`
- `o2_critical`
- `integrity_low`
- `integrity_critical`
- `coolant_low`

Rules:

- Start loop when warning enters active.
- Stop loop when warning exits active.
- If critical O2 active, stop low O2 loop and start critical O2 loop.
- If critical integrity active, stop low integrity loop and start critical integrity loop.

Why:
- Prevents overlapping duplicate warning sounds.

### 24.5 Music Layers

Use state-driven stems.

Base:

- Play `base` gameplay loop after start.

Layers:

| Condition | Layer |
|---|---|
| Player O2 < 25 | low O2 layer |
| Player O2 < 10 | critical O2 layer replaces low |
| Drone alert active | short drone alert stinger |
| Reactor online | reactor layer |
| Coolant < 30 | coolant low layer |
| Time remaining < 120 | final countdown layer |
| Success | success theme |
| Failure | failure theme |

Crossfade duration:

```js
0.5s
```

Why:
- The visual document defines layerable stems.
- Simple gain crossfades are enough and testable.

---

## 25. Rendering Implementation

### 25.1 Render Targets

Use:

- One main canvas for world.
- DOM elements for HUD.
- One small canvas for station map.

Why:
- DOM HUD is easier for text/accessibility.
- Canvas world is best for sprites/particles.
- Map canvas can draw schematic state efficiently.

### 25.2 Render Loop

Main loop:

1. Run simulation ticks as needed.
2. Render world canvas.
3. Render map canvas.
4. Update DOM HUD.
5. Process audio events from latest tick.

Render rate:

- Target 60 FPS.
- Simulation remains 20 Hz.

### 25.3 Camera

Fixed top-down orthographic camera.

Rules:

- Follows player.
- No rotation.
- No zoom.
- No parallax.
- Clamp camera so the player is not lost outside station bounds.
- Show current room and enough adjacent wall to read doors.

Tile scale:

- Target 96 px/tile at 1080p.
- Scale down for smaller windows.
- HUD is independent of world scale.

Why:
- Matches visual design.
- Prevents door readability issues.

### 25.4 Draw Order

Use this exact order:

1. Floor.
2. Floor decals.
3. State overlays: airflow, power conduits, breach effects, hazard shimmer.
4. Machines.
5. Doors.
6. Items.
7. Player.
8. Drones.
9. Particles.
10. Screen warning overlays.
11. HUD.

Why:
- State must never be obscured by decoration.
- Player and drones are the most important moving entities.

### 25.5 Static Background Optimization

Pre-render static room floors/walls to an offscreen canvas.

Dynamic elements draw on top.

Why:
- The station has only 10 rooms.
- Re-drawing static floor every frame is wasteful.

### 25.6 Particles

Particle budget:

- Max 128 active particles per visible room.
- Max 512 total.

Particle types:

- Airflow.
- Breach vacuum streaks.
- EMP ring.
- Damage flash.
- Reactor steam.
- Repair sparks.

Renderer may use `Math.random()` for visual variety.

Simulation must not use randomness.

Why:
- Visual variety is presentation-only.
- Gameplay must remain deterministic.

### 25.7 HUD Update Cadence

Update HUD every simulation tick.

Rules:

- Numbers must be exact.
- Bars may interpolate visually, but numeric values must not.
- Warning banner updates immediately on warning state change.
- Map updates immediately on room/power/door state change.

Why:
- Survival game needs immediate readability.

### 25.8 HUD Components

Required DOM/canvas components:

- Vitals panel.
- Current room status panel.
- Time/objective panel.
- Warning banner.
- Inventory panel.
- Interaction prompt.
- Event log.
- Station map.
- Launch checklist.
- End-screen overlay.

All critical text must include labels, not color alone.

Examples:

```text
O2 64
INTEGRITY 82
POWER NO POWER
HULL 0 BREACH
DRONE ACTIVE
COOLANT 0:24
LAUNCH RESET — SHUTTLE O2 LOW
```

Why:
- Required by visual design and accessibility.

---

## 26. Test Harness

### 26.1 Test Environment

Use Node.js built-in test runner:

```sh
node --test tests/
```

No browser required for core tests.

Optional browser smoke test can use Playwright, but it is not required for simulation correctness.

### 26.2 Test Harness Module

`tests/harness.js` should export:

```js
createState()
cloneState(state)
runTicks(state, tickCount, inputFactory)
runUntil(state, predicate, maxTicks)
getEvents(runResult)
assertInvariants(state)
```

`inputFactory` can be:

- A fixed input object.
- A function:
  ```js
  (tick, state) => input
  ```

### 26.3 Run Result

```js
{
  state: state,
  events: [ ...all events... ],
  ticks: number
}
```

### 26.4 Determinism Rules

- No `Math.random()` in simulation.
- No timestamps inside simulation.
- No async in simulation.
- All event IDs come from state counters.
- Dropped item IDs come from state counters.
- Power cell IDs come from state counters.

Why:
- Tests must be reproducible.
- Flaky tests would make validation useless.

### 26.5 Debug Invariants

Run invariants in tests and optionally in browser debug mode.

Check after every tick:

- Time is non-negative.
- Room O2 in `0-100`.
- Room hull in `0-100`.
- Player O2 in `0-100`.
- Player integrity in `0-100`.
- All inventory slots valid.
- Stack counts positive and below limits.
- Wrench not in inventory.
- Dropped items are inside valid rooms.
- Doors have valid states.
- Power nodes have valid occupancy.
- Reactor coolant time not negative.
- Launch progress in `0-100`.
- Drone positions are walkable or in a valid door gap.
- No `NaN` in numeric state.
- If status is ended, no further gameplay changes.

Why:
- Invariants catch system bugs early.
- They are the cheapest way to prove the simulation is healthy.

---

## 27. Required Test Suite

The following tests are required to prove the game is finished and playable.

### 27.1 Level Tests

File: `tests/level.test.js`

Tests:

1. Level compiles exactly 10 rooms.
2. Room IDs match expected list.
3. Room dimensions match gameplay designer.
4. Initial room O2 matches designer.
5. Initial room hull matches designer.
6. Initial door states match designer.
7. Door graph matches designer.
8. Room interiors do not overlap.
9. Every door is on a shared wall.
10. All rooms reachable from docking when all operable doors are opened and jammed doors repaired.
11. Content counts match full resource counts.
12. Machines exist in correct rooms.
13. Power nodes exist only in crew/hydro/shuttle.
14. Drone homes are cargo and shuttle.
15. Hull event times match designer.

Why:
- A broken level graph is a hard failure.

---

### 27.2 Movement and Door Tests

File: `tests/movement.test.js`  
File: `tests/doors.test.js`

Tests:

1. Player moves within a room.
2. Player cannot pass closed door.
3. Player cannot pass jammed door.
4. Player can pass open door.
5. Door open channel takes 1s.
6. Door close channel takes 1s.
7. Jammed door repair takes 5s.
8. Jammed repair requires wrench.
9. Repaired jammed door becomes closed.
10. Door progress retains if paused.
11. Airflow/power use door state correctly.
12. Player room changes only when entering adjacent room interior.

Why:
- Doors are the core spatial mechanic.

---

### 27.3 Atmosphere Tests

File: `tests/atmosphere.test.js`

Tests:

1. Unbreached room drains 0.5 O2/sec.
2. Breached room drains 15 O2/sec.
3. Repaired powered O2 machine generates correct rate.
4. Unpowered repaired machine generates zero.
5. Unrepaired machine generates zero.
6. Airflow formula matches designer.
7. Airflow only through open doors.
8. Closed doors transfer zero.
9. Jammed doors transfer zero.
10. Simultaneous airflow is deterministic.
11. Room O2 clamps to 0 and 100.
12. Breached room with powered generator still loses O2 if drain exceeds generation.

Why:
- Airflow is the central survival puzzle.

---

### 27.4 Power Tests

File: `tests/power.test.js`

Tests:

1. Start EPC powers crew.
2. Power does not pass through closed door.
3. Power passes through open door.
4. Power does not pass through jammed door.
5. Power cell install takes 2s.
6. Power cell install requires empty node.
7. Power cell can be installed in an empty node even if room is powered by propagation.
8. Power cell provides 400s power.
9. Power cell expiration emits `power_cell_expire`.
10. Power loss emits `power_loss`.
11. Reactor online powers reactor room.
12. Reactor power propagates through open doors.
13. Power display source is correct.

Why:
- Power propagation is a major systemic mechanic.

---

### 27.5 Reactor Tests

File: `tests/reactor.test.js`

Tests:

1. Coolant pump repair takes 5s.
2. Coolant cell use takes 5s.
3. Coolant cell sets timer to 180s.
4. Coolant cell does not add to existing timer.
5. Reactor core repair takes 8s.
6. Spin-up takes 20s.
7. Spin-up requires coolant active.
8. Spin-up progress pauses if player leaves.
9. Spin-up progress resets if coolant expires before completion.
10. Reactor online requires spin-up complete and coolant active.
11. Reactor online provides power.
12. Coolant expiry after spin-up creates heat hazard.
13. Coolant expiry before spin-up does not create heat hazard.
14. Player in reactor room takes 5/sec heat damage only during heat hazard.
15. New coolant restores online and removes heat hazard.
16. Coolant low warning triggers below 30s.
17. Coolant expired event fires.

Why:
- Reactor timing is critical for launch.

---

### 27.6 Drone Tests

File: `tests/drones.test.js`

Tests:

1. Drones start inactive.
2. Drone A activates when player enters cargo.
3. Drone B activates when player enters shuttle.
4. Inactive drones do not move.
5. Patrol speed is 2.5 tiles/sec.
6. Alert speed is 3.0 tiles/sec.
7. Drone enters alert when player in same room.
8. Drone follows player through open doors.
9. Drone does not follow player through closed doors.
10. Drone with no path returns to patrol after 3s.
11. Drone attack deals 20 damage.
12. Drone attack cooldown is 1s.
13. Player invulnerability blocks drone damage for 0.5s.
14. EMP disables all active drones in current room.
15. EMP only usable if active drone in current room.
16. EMP consumed only on completion.
17. Disabled drones do not reactivate.
18. Player can avoid Drone B by luring it into Bridge and closing Bridge-Shuttle.

Why:
- Drones are the only enemy system and must be fair.

---

### 27.7 Hull Event Tests

File: `tests/hull.test.js`

Tests:

1. Event 1 warning starts at 230s.
2. Event 1 damage applies at 240s.
3. Event 2 warning starts at 470s.
4. Event 2 damage applies at 480s.
5. Event 3 warning starts at 710s.
6. Event 3 damage applies at 720s.
7. Event never targets current player room.
8. Event skips if target already breached.
9. Event 1 fallback works.
10. Event 2 fallback works.
11. Event 2 does not damage the same room twice.
12. Event 3 fallback works.
13. Event damage can cause breach.
14. Event damage cannot raise hull.
15. Hull patch adds +40 hull, max 100.
16. Breach seal sets hull to 60.
17. Hull patch consumed only on completion.
18. Hull patch not consumed if interrupted.
19. Breach emits `breach` event.

Why:
- Hull events are scheduled fairness-critical events.

---

### 27.8 Vitals Tests

File: `tests/vitals.test.js`

Tests:

1. Room O2 >=60 increases player O2 +0.5/sec.
2. Room O2 30-59 decreases player O2 -0.5/sec.
3. Room O2 1-29 decreases player O2 -1.5/sec.
4. Room O2 <1 decreases player O2 -3/sec.
5. Player O2 clamps to 0-100.
6. Player O2 0 drains integrity 5/sec.
7. Medkit adds +50 integrity.
8. Medkit cannot be used at 100 integrity.
9. O2 Tank adds +50 player O2.
10. O2 Tank cannot be used at 100 player O2.
11. Reactor heat drains integrity 5/sec in reactor room.
12. Drone damage sets last damage source.
13. Death cause is correct for asphyxia.
14. Death cause is correct for drone.
15. Death cause is correct for reactor heat.

Why:
- Vitals define survival.

---

### 27.9 Item Tests

File: `tests/items.test.js`

Tests:

1. Inventory has 6 slots.
2. Items stack below max.
3. Inventory full blocks pickup.
4. Dropped items persist.
5. Dropped items can be picked up again.
6. Wrench is not stored in inventory.
7. Wrench cannot be dropped.
8. Wrench remains available after dropping other items.
9. Selecting empty slot does nothing.
10. Using invalid item emits UI error.
11. Stack limits enforced.
12. Item counts match world resource counts.

Why:
- Inventory mistakes must not softlock the player.

---

### 27.10 Channel Tests

File: `tests/channels.test.js`

Tests:

1. Repair progress retains when paused.
2. Machine repair completes only after full time.
3. Jammed door repair requires wrench.
4. Hull patch requires wrench and hull patch.
5. Power cell install consumes power cell only on completion.
6. Coolant cell consumes coolant only on completion.
7. Fuel line consumes fuel rod only on completion.
8. Launch computer progress retains when paused.
9. Launch computer requires bridge power.
10. Reactor spin-up progress retains when paused.
11. Reactor spin-up resets if coolant expires.
12. EMP channel consumes EMP only on completion.
13. Channel progress does not advance if required item missing.
14. Channel progress does not advance if player out of range.

Why:
- Channel consumption is a common source of unfair bugs.

---

### 27.11 Launch Tests

File: `tests/launch.test.js`

Tests:

1. Launch checklist hidden before trigger.
2. Launch checklist visible after entering bridge.
3. Launch checklist visible after entering shuttle.
4. Launch checklist visible after reactor online.
5. Launch progress advances only when all requirements true.
6. Launch progress advances only when player at launch pad.
7. Launch progress advances only while holding E.
8. Stopping E pauses launch but does not reset.
9. Leaving pad resets launch.
10. Taking damage resets launch.
11. Reactor offline resets launch.
12. Shuttle unpowered resets launch.
13. Computer not primed resets launch.
14. Fuel missing resets launch.
15. Shuttle O2 low resets launch.
16. Reset reason is specific.
17. Launch progress reaching 100 triggers success.
18. Success takes precedence over death same tick.
19. Success takes precedence over de-orbit at 960s.
20. De-orbit failure occurs if launch not complete at 960s.

Why:
- Launch is the final multi-system check.

---

### 27.12 Objective Tests

File: `tests/objectives.test.js`

Tests:

1. Initial objective is Repair Crew O2 Generator.
2. Objective advances after crew O2 generator repaired.
3. Stabilize Crew Atmosphere requires 5s of crew O2 >=60.
4. Objective advances when player enters hydro.
5. Objective advances after hydro recycler repaired.
6. Objective advances when reactor online.
7. Objective advances after launch computer primed.
8. Objective advances after fuel installed.
9. Objective advances when shuttle O2 reaches 60.
10. Objective completes on launch success.
11. Objectives never regress.

Why:
- The HUD must guide the player.

---

### 27.13 Audio Event Tests

File: `tests/audioEvents.test.js`

Tests:

1. Breach emits `breach`.
2. Power loss emits `power_loss`.
3. Power cell expiration emits `power_cell_expire`.
4. Drone activation emits `drone_activate`.
5. Drone alert emits `drone_alert`.
6. Drone attack emits `drone_attack`.
7. Hull event warning emits `hull_event_warning`.
8. Coolant low emits `coolant_low`.
9. Coolant expired emits `coolant_expired`.
10. Reactor online emits `reactor_online`.
11. De-orbit warning emits `deorbit_warning`.
12. Launch reset emits `launch_reset`.
13. Launch success emits `launch_success`.
14. Game over emits `game_over`.
15. All emitted audio names exist in audio manifest mapping.
16. Warning audio does not repeat every tick.

Why:
- Audio is required UX, but tests should verify event wiring, not sound quality.

---

### 27.14 Invariant Tests

File: `tests/invariants.test.js`

Tests:

1. Run 1000 ticks with no input; invariants hold.
2. Run 1000 ticks with random-looking but deterministic input pattern; invariants hold.
3. Run through a forced breach; invariants hold.
4. Run through reactor coolant expiry; invariants hold.
5. Run through both drone activations; invariants hold.
6. Run through all hull events; invariants hold.
7. Run through launch reset and success; invariants hold.

Why:
- Invariants prove the simulation does not corrupt state.

---

### 27.15 Acceptance Test: Reference Win

File: `tests/acceptance/referenceWin.test.js`

This test proves the game is playable by a legal scripted player.

The test must use only legal simulation inputs. It may use high-level helper macros, but macros must not teleport the player or directly set machine states.

Reference strategy:

1. Start in docking.
2. Pick up wrench, O2 tanks, medkit, hull patch.
3. Move to crew.
4. Repair Crew O2 Generator.
5. Wait for crew O2 >=60 for 5s.
6. Repair jammed crew-storage door.
7. Enter storage.
8. Patch storage hull.
9. Pick up storage resources.
10. Leave storage and close crew-storage door.
11. Enter medbay.
12. Patch medbay hull before 480s.
13. Pick up medbay resources.
14. Close medbay door.
15. Open crew-hydro door.
16. Enter hydro.
17. Pick up power cell.
18. Install power cell in hydro node.
19. Repair Hydro O2 Recycler.
20. Keep crew-hydro open for power/airflow.
21. Repair jammed hydro-engineering door.
22. Open hydro-engineering door.
23. Enter engineering.
24. Pick up coolant cell and fuel rod.
25. Repair Reactor Coolant Pump.
26. Use coolant cell.
27. Open engineering-reactor door.
28. Enter reactor.
29. Pick up second coolant cell, EMP, hull patch.
30. Repair Reactor Core.
31. Start reactor spin-up.
32. Complete spin-up.
33. Reactor online.
34. Return to engineering.
35. Open engineering-bridge door.
36. Enter bridge.
37. Prime launch computer.
38. Pick up EMP if not already collected.
39. Prepare shuttle power:
   - Open hydro-shuttle and/or bridge-shuttle as needed.
   - Install shuttle power cell if needed.
40. Enter shuttle.
41. Deal with Drone B:
   - Reference may use EMP.
42. Patch shuttle hull before 720s.
43. Repair Shuttle O2 Vent.
44. Install fuel rod.
45. Raise shuttle O2 to 60.
46. Use second coolant before coolant expires.
47. Stand at launch pad.
48. Complete 30s launch channel.
49. Assert success before 960s.

Required assertions:

- `state.meta.status === 'success'`
- `state.meta.time < 960`
- `launch.success === true`
- All launch requirements true at success.
- Player alive.
- Fuel rod consumed.
- At least one coolant cell used.
- Reactor online at launch.
- Launch computer primed.
- No invariant failures.
- No negative item counts.
- No dropped required item lost.
- Event log contains `launch_success`.

Why:
- This is the strongest proof that the game can be completed.

---

### 27.16 Acceptance Test: No EMP Win

File: `tests/acceptance/noEmpWin.test.js`

This test proves the fairness rule that launch is possible without EMP.

Strategy:

1. Follow reference win but do not use EMP.
2. Do not pick up EMP charges, or if picked up, do not use them.
3. When entering shuttle, lure Drone B toward bridge.
4. Enter bridge.
5. Close bridge-shuttle door.
6. Wait for drone to lose path and return to patrol.
7. Keep bridge-shuttle closed.
8. Keep hydro-shuttle open for power/O2 if needed.
9. Complete launch from shuttle.

Required assertions:

- `state.meta.status === 'success'`
- `state.stats.empUsed === 0`
- `state.drones[droneB].disabled === false`
- Launch requirements true at success.
- Drone B did not deal damage during launch channel.

Why:
- The gameplay document explicitly requires this fairness condition.

---

### 27.17 Failure Mode Tests

File: `tests/acceptance/failureModes.test.js`

Tests:

1. Player can die from asphyxia.
2. Player can die from drone attack.
3. Player can die from reactor heat.
4. Player can fail by de-orbit.
5. Death sets failure cause correctly.
6. De-orbit sets failure cause `deorbit`.
7. End screen stats include time survived.
8. End screen stats include systems restored.
9. No respawn occurs after failure.

Why:
- Failure states must be clean and correct.

---

### 27.18 Resource Fairness Tests

File: `tests/acceptance/resourceFairness.test.js`

Tests:

1. All required resources exist in the world.
2. Player can win without picking up Cargo Hold resources.
3. Player can prevent Event 1 breach by patching storage before 240s.
4. Player can prevent Event 2 medbay breach by patching medbay before 480s.
5. Player can prevent Event 3 shuttle breach by patching shuttle before 720s.
6. If a room is breached, sealing it restores hull to 60.
7. If all major breaches are prevented, no room starts breached from events.
8. Dropped required items can be recovered.
9. Closing all doors does not permanently prevent reopening.

Why:
- The design promises a fair, preventable, non-softlocking run.

---

### 27.19 Browser Smoke Test

File: `tests/browser/smoke.test.js`

Optional but recommended.

Use Playwright or equivalent.

Tests:

1. Page loads without console errors.
2. Title screen is visible.
3. Start button starts game.
4. World canvas is visible.
5. HUD panels are visible.
6. Simulation time advances after 1 real second.
7. HUD numbers update.
8. Map is visible.
9. No uncaught exceptions after 10 seconds.

Do not assert visual quality.

Why:
- Core correctness is covered by headless tests.
- Browser smoke test catches integration wiring problems.

---

## 28. Performance Requirements

Target:

- Simulation: 20 Hz.
- Rendering: 60 FPS where possible.
- 10 rooms.
- 2 drones.
- Max 512 particles.
- HUD updated 20 Hz.

Performance expectations:

- One simulation tick should be cheap enough to run many ticks in tests.
- Avoid per-tick full state cloning in the browser.
- Pre-render static world background.
- Use offscreen canvas for static floor/walls.
- Cache room state objects.
- Avoid creating new arrays for powered rooms every tick if possible, but correctness first.

Test:

- 1000 simulation ticks should complete quickly in Node.
- The exact time threshold is not critical, but it should not be near real-time.

Why:
- The game is small, so performance issues would come from bad implementation, not design.

---

## 29. Accessibility Requirements

The HUD must be playable with audio off and must not rely on color alone.

Required text/shape signals:

- `O2` label with number.
- `INTEGRITY` label with number.
- `POWER NO POWER` / `POWER POWERED` / `POWER EPC` / `POWER CELL` / `POWER REACTOR`.
- `HULL 0 BREACH`.
- `DRONE ACTIVE`.
- `COOLANT EXPIRED`.
- Launch checklist item names.
- Launch reset reason.
- Door states on map: open/closed/jammed.

Tests should assert that critical states have text labels in HUD state, not only CSS classes.

Why:
- Required by visual design and accessibility principle.

---

## 30. Important Ambiguity Resolutions

These decisions resolve gaps between documents.

### 30.1 EMP Consumption

Decision:

- EMP has a 1s channel.
- EMP is consumed only on completion.

Why:
- Consistent with other consumable channels.
- Prevents losing EMP if input is interrupted.

### 30.2 Power Cell Node Rule

Decision:

- A power cell can be installed in an empty node even if the room is currently powered by propagation.

Why:
- “Unpowered node” means no local source.
- Otherwise power cells would be blocked by the very power they are meant to extend.

### 30.3 Player O2 Lowest Bucket

Decision:

- Room O2 `< 1` uses the -3/sec bucket.

Why:
- O2 is continuous.
- A room at 0.3 O2 is effectively zero air.

### 30.4 Launch Pause vs Reset

Decision:

- Stopping E while at launch pad pauses launch progress.
- Leaving pad, taking damage, or losing requirements resets launch progress.

Why:
- Players should not be punished for releasing E, but launch requires sustained presence.

### 30.5 Hull Event Targeting

Decision:

- Hull event target is recalculated during the 10s warning window.
- If the player moves into the target room, the event reselects a valid target.

Why:
- The rule “never target current player room” must remain fair.

### 30.6 Reactor Heat Condition

Decision:

- Heat hazard occurs only if reactor spin-up is complete and coolant is not active.

Why:
- A reactor that never spun up should not become a heat trap just because coolant expired.

### 30.7 Door State Timing

Decision:

- Door state changes from a completed channel affect power, airflow, and drones in the same tick.

Why:
- Simpler mental model: when the door action finishes, the door is open/closed/repaired.

### 30.8 Simultaneous Airflow

Decision:

- Airflow transfers are computed from start-of-phase O2 values and applied simultaneously.

Why:
- Prevents iteration-order bugs and makes airflow deterministic.

---

## 31. Cut List for Engineering

These are intentionally cut.

| Cut | Reason |
|---|---|
| Save/load | Not required, adds serialization complexity. |
| Pause menu | Timer pressure is core; browser tab pause is acceptable. |
| Random events | Gameplay requires fixed events. |
| Random enemies | Only two drones. |
| Procedural map | Station is fixed and validated. |
| Tile collision | Room interiors have no blocking obstacles. |
| Complex drone AI | Room graph pathing is enough. |
| Dynamic lighting | Obscures state and costs performance. |
| 3D audio | Simple pan is enough. |
| Particle simulation | Presentation only, not gameplay. |
| Inventory drag/drop | Slot selection and drop is enough. |
| Settings screen | Not needed for 16-minute browser game. |
| Multiplayer | Not in design. |
| Multiple shuttles | Not in design. |
| Alternate endings | Not in design. |
| Mid-run respawn | Explicitly cut. |

---

## 32. Definition of Done

The game is considered finished when:

1. All required files exist.
2. Level validation passes.
3. Simulation runs at 20 Hz deterministically.
4. All core systems match `gameplay.md`.
5. HUD matches `visual.md` state grammar.
6. Audio events fire for all required warning/action events.
7. Title screen starts the game.
8. Success and failure screens display correct data.
9. Restart creates a fresh run.
10. All headless tests pass.
11. Reference win test passes before 960s.
12. No-EMP win test passes.
13. Failure mode tests pass.
14. Invariant tests pass.
15. Browser smoke test passes without console errors.
16. No simulation randomness.
17. No softlocks from dropped items, closed doors, inventory full, or drone behavior.
18. Player can win by following the main objective chain.

This is the bar for handing the implementation to final integration.