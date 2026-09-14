# engineering.md

## 1. Scope and Purpose

This document defines the engineering design for **DERELICT STATION**, a 2D top-down browser survival game.

It is not a gameplay or visual design document. It is the engineering handoff. It defines:

- the files that should exist,
- the deterministic simulation architecture,
- the level builder / level-functioning logic,
- the complex system logic needed to make the fixed gameplay level function,
- the test harness,
- the test suite that proves the game is finished and playable.

The integration agent should be able to build the game from this document plus `gameplay.md` and `visual.md`.

---

## 2. Top-Level Engineering Decisions

### 2.1 Technology

Use:

- TypeScript,
- Vite,
- Canvas 2D,
- Vitest for headless tests,
- optional Playwright for a minimal browser smoke test.

Do not use a game engine, physics engine, ECS framework, or procedural level generator.

Logic:

- The station is a fixed 10-room system.
- The core challenge is deterministic systems: O2, power, hull, drones, channels, and launch.
- A lightweight, headless, fixed-timestep simulation is the most testable and scalable solution.
- Browser 2D rendering is simple enough for Canvas.
- Adding an engine or ECS would increase complexity without improving the fixed gameplay.

---

### 2.2 Determinism

The simulation must be deterministic.

Rules:

- No `Math.random()` in simulation logic.
- No time-based simulation outside the fixed timestep.
- Hull events are scheduled, not random.
- Drone behavior is deterministic from state and inputs.
- Item positions, machine positions, and drone waypoints are fixed by data.
- Visual particles may use a seeded RNG, but particle RNG must never affect simulation state.

Logic:

- Tests must be repeatable.
- The gameplay design promises fairness through fixed events and fixed resources.
- Non-determinism would make headless validation and player fairness harder.

---

### 2.3 Fixed Timestep

Use:

```ts
export const SIM_DT = 0.05; // 20 updates per second
```

All gameplay rates are per second.

The renderer runs on `requestAnimationFrame` and may interpolate between the last two simulation states for smooth movement.

Logic:

- 20 Hz is enough for room-level survival systems.
- Interpolation gives smooth movement without requiring 60 Hz simulation.
- Fixed timestep makes tests and edge-case ordering reliable.

---

### 2.4 Headless Simulation

The simulation must run with no DOM, canvas, audio, or browser APIs.

Required separation:

```
simulation  ->  pure state + input + events
rendering   ->  reads simulation state and draws
audio       ->  listens to events / polls HUD state
input       ->  converts browser input into simulation input
```

Logic:

- This enables the required test harness.
- It lets us validate gameplay without a browser.
- It keeps rendering and audio from accidentally affecting balance.

---

## 3. Files That Should Exist

The repository should contain at least the following files.

```text
/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts
├── playwright.config.ts                 # optional browser smoke test
├── public/
│   └── assets/
│       ├── audio/
│       │   ├── o2_low.ogg
│       │   ├── o2_critical.ogg
│       │   ├── integrity_low.ogg
│       │   ├── integrity_critical.ogg
│       │   ├── breach.ogg
│       │   ├── power_loss.ogg
│       │   ├── power_cell_expire.ogg
│       │   ├── coolant_low.ogg
│       │   ├── coolant_expired.ogg
│       │   ├── drone_activate.ogg
│       │   ├── drone_alert.ogg
│       │   ├── drone_attack.ogg
│       │   ├── hull_event_warning.ogg
│       │   ├── deorbit_warning.ogg
│       │   ├── launch_success.ogg
│       │   ├── game_over.ogg
│       │   └── ...
│       └── audio-manifest.json
└── src/
    ├── main.ts
    ├── app.ts
    ├── constants.ts
    ├── types/
    │   ├── simulation.ts
    │   ├── layout.ts
    │   ├── items.ts
    │   ├── machines.ts
    │   ├── events.ts
    │   └── hud.ts
    ├── data/
    │   ├── station.json
    │   ├── station-layout.json
    │   └── assets.json
    ├── sim/
    │   ├── Simulation.ts
    │   ├── SimulationState.ts
    │   ├── Input.ts
    │   ├── Events.ts
    │   ├── Rng.ts
    │   ├── FixedTimestep.ts
    │   └── serialization.ts
    ├── systems/
    │   ├── playerSystem.ts
    │   ├── movementSystem.ts
    │   ├── inventorySystem.ts
    │   ├── doorSystem.ts
    │   ├── channelSystem.ts
    │   ├── atmosphereSystem.ts
    │   ├── hullSystem.ts
    │   ├── powerSystem.ts
    │   ├── reactorSystem.ts
    │   ├── droneSystem.ts
    │   ├── launchSystem.ts
    │   ├── objectiveSystem.ts
    │   ├── warningSystem.ts
    │   ├── eventLogSystem.ts
    │   └── endStateSystem.ts
    ├── layout/
    │   ├── LevelBuilder.ts
    │   ├── CollisionGrid.ts
    │   ├── RoomGraph.ts
    │   └── defaultLayout.ts
    ├── render/
    │   ├── Renderer.ts
    │   ├── Camera.ts
    │   ├── AssetLoader.ts
    │   ├── TextureFactory.ts
    │   ├── icons.ts
    │   ├── designTokens.ts
    │   ├── world/
    │   │   ├── roomRenderer.ts
    │   │   ├── doorRenderer.ts
    │   │   ├── machineRenderer.ts
    │   │   ├── itemRenderer.ts
    │   │   ├── playerRenderer.ts
    │   │   ├── droneRenderer.ts
    │   │   ├── powerConduitRenderer.ts
    │   │   ├── airflowRenderer.ts
    │   │   └── breachRenderer.ts
    │   ├── hud/
    │   │   ├── hudProjection.ts
    │   │   ├── vitalsPanel.ts
    │   │   ├── roomPanel.ts
    │   │   ├── objectivePanel.ts
    │   │   ├── launchChecklist.ts
    │   │   ├── inventoryPanel.ts
    │   │   ├── interactionPrompt.ts
    │   │   ├── eventLog.ts
    │   │   ├── mapPanel.ts
    │   │   ├── warningBanner.ts
    │   │   └── endScreens.ts
    │   └── effects/
    │       ├── particleSystem.ts
    │       └── screenEffects.ts
    ├── audio/
    │   ├── AudioManager.ts
    │   └── audioEvents.ts
    ├── input/
    │   └── InputManager.ts
    ├── ui/
    │   └── ScreenManager.ts
    ├── test/
    │   ├── harness.ts
    │   ├── fixtures.ts
    │   ├── invariants.ts
    │   ├── bot.ts
    │   └── scriptedRuns.ts
    └── __tests__/
        ├── levelBuilder.test.ts
        ├── atmosphere.test.ts
        ├── power.test.ts
        ├── hull.test.ts
        ├── reactor.test.ts
        ├── drones.test.ts
        ├── inventory.test.ts
        ├── channels.test.ts
        ├── launch.test.ts
        ├── objectives.test.ts
        ├── endStates.test.ts
        ├── hudProjection.test.ts
        ├── audioEvents.test.ts
        ├── performance.test.ts
        ├── playthroughReference.test.ts
        └── playthroughNoEmp.test.ts
```

Optional:

```text
/e2e/
└── browser.smoke.spec.ts
```

Logic:

- The file list keeps simulation, rendering, audio, layout, and tests separate.
- The test files are part of the deliverable, not optional extras.
- The data files make the level content inspectable and testable.

---

## 4. Coordinate and Data Contracts

### 4.1 Units

Use tile units in simulation.

```ts
export const TILE_METERS = 0.5;
```

- 1 tile = 0.5 meters.
- Positions are in tile units.
- Pixel scale is a rendering concern only.
- The default recommended pixel scale is 96 px per tile at 1080p, but the renderer may scale.

Room sizes from `gameplay.md` are tile counts.

Example:

```ts
{
  "id": "crew",
  "w": 8,
  "h": 8
}
```

means the room interior is 8 tiles wide and 8 tiles high.

---

### 4.2 Room IDs

Use these stable IDs:

```ts
export type RoomId =
  | "docking"
  | "crew"
  | "storage"
  | "cargo"
  | "medbay"
  | "hydro"
  | "engineering"
  | "reactor"
  | "bridge"
  | "shuttle";
```

---

### 4.3 Door IDs

Use stable door IDs:

```ts
export type DoorId =
  | "docking_crew"
  | "crew_storage"
  | "storage_cargo"
  | "crew_medbay"
  | "crew_hydro"
  | "hydro_engineering"
  | "hydro_shuttle"
  | "engineering_reactor"
  | "engineering_bridge"
  | "bridge_shuttle";
```

---

### 4.4 Machine IDs

Use:

```ts
export type MachineId =
  | "crew_o2_generator"
  | "hydro_o2_recycler"
  | "shuttle_o2_vent"
  | "coolant_pump"
  | "reactor_core"
  | "launch_computer"
  | "fuel_line"
  | "launch_pad";
```

Power nodes are not machines. They are tracked separately.

---

### 4.5 Item Types

Use:

```ts
export type ItemType =
  | "wrench"
  | "o2_tank"
  | "medkit"
  | "hull_patch"
  | "power_cell"
  | "emp_charge"
  | "coolant_cell"
  | "fuel_rod";
```

Stack limits:

```ts
export const ITEM_STACK_LIMITS: Record<ItemType, number> = {
  wrench: 1,
  o2_tank: 5,
  medkit: 3,
  hull_patch: 4,
  power_cell: 3,
  emp_charge: 3,
  coolant_cell: 2,
  fuel_rod: 1
};
```

The wrench is equipped after pickup and does not occupy an inventory slot.

Logic:

- The wrench is a core repair tool.
- It cannot be dropped, lost, deleted, or consumed.
- Treating it as an equipped capability avoids inventory edge cases.

---

### 4.6 Default Station Layout

The production level uses a fixed, deterministic layout.

This layout satisfies the room graph, room sizes, and door adjacency requirements.

Room rectangles are interior tile rectangles:

```ts
type RoomRect = {
  x: number;
  y: number;
  w: number;
  h: number;
};
```

The rectangle includes tile coordinates from `x` to `x + w` and `y` to `y + h`. Wall thickness between adjacent rooms is 1 tile.

Default layout:

| Room | x | y | w | h |
|---|---:|---:|---:|---:|
| docking | 3 | 17 | 4 | 4 |
| crew | 8 | 16 | 8 | 8 |
| storage | 8 | 10 | 6 | 5 |
| cargo | 8 | 4 | 6 | 5 |
| medbay | 8 | 25 | 6 | 5 |
| hydro | 17 | 17 | 6 | 6 |
| engineering | 17 | 24 | 6 | 5 |
| reactor | 17 | 30 | 5 | 5 |
| bridge | 24 | 24 | 6 | 5 |
| shuttle | 24 | 17 | 8 | 6 |

Door cells are wall tiles that become passable when open:

| Door | Cell x | Cell y |
|---|---:|---:|
| docking_crew | 7 | 19 |
| crew_storage | 11 | 15 |
| storage_cargo | 11 | 9 |
| crew_medbay | 11 | 24 |
| crew_hydro | 16 | 20 |
| hydro_engineering | 20 | 23 |
| hydro_shuttle | 23 | 20 |
| engineering_reactor | 19 | 29 |
| engineering_bridge | 23 | 26 |
| bridge_shuttle | 27 | 23 |

Door center is:

```ts
{ x: cell.x + 0.5, y: cell.y + 0.5 }
```

Logic:

- The layout is hand-baked for fairness.
- It makes all required doors physically adjacent.
- It avoids a procedural level generator that could produce unfair or unstable room geometry.
- The level builder still validates the layout, so a corrupted or inconsistent layout fails tests.

---

### 4.7 Station Data File

`src/data/station.json` should contain:

```json
{
  "rooms": [
    {
      "id": "docking",
      "name": "Docking Bay",
      "abbr": "DB",
      "w": 4,
      "h": 4,
      "initialO2": 80,
      "initialHull": 100,
      "powerNode": false
    }
  ],
  "doors": [
    {
      "id": "docking_crew",
      "a": "docking",
      "b": "crew",
      "initial": "open"
    }
  ],
  "machines": [
    {
      "id": "crew_o2_generator",
      "room": "crew",
      "type": "o2_generator",
      "rate": 8,
      "repairTime": 5,
      "initialRepaired": false,
      "position": { "x": 9.5, "y": 17.5 }
    }
  ],
  "powerNodes": [
    { "id": "crew_power_node", "room": "crew", "position": { "x": 14.5, "y": 17.5 } },
    { "id": "hydro_power_node", "room": "hydro", "position": { "x": 21.5, "y": 18.5 } },
    { "id": "shuttle_power_node", "room": "shuttle", "position": { "x": 28.5, "y": 18.5 } }
  ],
  "items": [
    {
      "id": "docking_wrench",
      "room": "docking",
      "type": "wrench",
      "position": { "x": 4.5, "y": 19.5 }
    }
  ],
  "drones": [
    {
      "id": "A",
      "home": "cargo",
      "waypoints": [
        { "x": 9.5, "y": 5.5 },
        { "x": 12.5, "y": 5.5 },
        { "x": 9.5, "y": 7.5 }
      ]
    }
  ],
  "hullEvents": [
    {
      "id": "event1",
      "time": 240,
      "warningLead": 10,
      "damages": [
        {
          "target": "storage",
          "amount": 30,
          "fallback": [
            { "room": "cargo", "amount": 30 },
            { "room": "crew", "amount": 20 }
          ]
        }
      ]
    }
  ]
}
```

`src/data/station-layout.json` should contain the room rectangles and door cells from section 4.6.

Logic:

- Separating content from geometry makes validation easier.
- The level builder can validate both files independently.
- The fixed layout remains inspectable by humans.

---

## 5. Level Builder

The level builder turns data into a runtime level.

It is not a procedural map generator. It is a deterministic level instantiator and validator.

### 5.1 `LevelBuilder.build()`

Responsibilities:

1. Validate station data.
2. Validate layout.
3. Build room runtime state.
4. Build door runtime state.
5. Build machine runtime state.
6. Build power nodes.
7. Build floor items.
8. Build drone waypoints.
9. Build collision grid.
10. Build static room graph.

If layout is missing, use `defaultLayout.ts`.

If layout is present, validate it.

Do not invent new rooms, doors, machines, items, or events.

Logic:

- The gameplay design fixes the level.
- A validator is safer than a procedural generator.
- Tests can assert that the built level exactly matches the intended station.

---

### 5.2 Validation Rules

The builder must throw if any of these are true:

- A room ID is duplicated.
- A room has non-positive width or height.
- A door references a missing room.
- A door is duplicated.
- A machine references a missing room.
- An item references a missing room.
- A drone references a missing home room.
- A machine or item position is outside its room.
- A drone waypoint is outside its home room.
- Two room interiors overlap.
- A door cell is not on a valid wall between its two rooms.
- A door cell is not 1 tile away from both connected room interiors.
- A required resource count does not match `gameplay.md`.
- A machine position overlaps an item position by more than 0.5 tiles.
- A power node exists in a room without a power node flag.
- A hull event references an invalid room or fallback room.
- A hull event fallback amount is missing.
- Initial door states are invalid.
- The room graph is not connected.
- The player start room is not `docking`.
- The player start position is not inside `docking`.

Logic:

- These tests catch integration drift early.
- The fixed level should never silently become unplayable.

---

### 5.3 Collision Grid

The collision grid represents the station as tiles.

Tile states:

```ts
type TileSolid =
  | { solid: true }
  | { solid: false; doorId?: DoorId };
```

Construction:

1. Determine world bounds from all room rectangles plus 2 tiles of margin.
2. Initialize all tiles solid.
3. Carve room interiors solid-free.
4. For each door cell, mark the tile as door-controlled.
5. When a door is open, its tile is passable.
6. When a door is closed or jammed, its tile is solid.

The grid must be updated when door states change.

Logic:

- This gives simple continuous movement with walls and doors.
- It avoids custom room-collision code for every entity.
- It scales if the room count changes while keeping the same rules.

---

### 5.4 Room Graph

The static room graph contains:

```ts
interface RoomGraph {
  rooms: RoomId[];
  adjacency: Map<RoomId, { room: RoomId; doorId: DoorId }[]>;
}
```

Use this graph for:

- drone pathfinding,
- bot pathfinding,
- map rendering,
- power BFS,
- airflow door iteration.

Power and airflow should not hardcode room lists.

Logic:

- The room graph is the core abstraction for the game.
- It makes power, airflow, and drone pathing easy to test.

---

## 6. Simulation Architecture

### 6.1 Core State

The simulation state should be plain serializable data.

```ts
interface SimState {
  time: number;
  day: number;
  status: "running" | "success" | "failure";
  failCause?: "asphyxia" | "drone_attack" | "reactor_heat" | "integrity_failure" | "deorbit";
  player: PlayerState;
  rooms: Record<RoomId, RoomState>;
  doors: Record<DoorId, DoorState>;
  machines: Record<MachineId, MachineState>;
  powerNodes: PowerNodeState[];
  drones: DroneState[];
  floorItems: FloorItem[];
  inventory: InventorySlot[];
  selectedSlot: number;
  reactor: ReactorState;
  power: PowerState;
  launch: LaunchState;
  objectives: ObjectiveState;
  hullEvents: HullEventState[];
  eventLog: LogEntry[];
  channel: ChannelState | null;
  lastIntegrityDamageSource: IntegrityDamageSource | null;
}
```

Required room state:

```ts
interface RoomState {
  id: RoomId;
  name: string;
  abbr: string;
  o2: number;
  hull: number;
  breached: boolean;
  powered: boolean;
  droneActive: boolean;
  objective: boolean;
  eventWarning: boolean;
  eventWarningTime?: number;
}
```

Required power state:

```ts
interface PowerState {
  poweredRooms: Set<RoomId>;
  localSources: Record<RoomId, LocalPowerSource | undefined>;
}

type LocalPowerSource =
  | { type: "epc"; remaining: number }
  | { type: "cell"; remaining: number }
  | { type: "reactor" };
```

Required reactor state:

```ts
interface ReactorState {
  pumpRepaired: boolean;
  coreRepaired: boolean;
  coolant: number;
  spinUpProgress: number;
  spinUpComplete: boolean;
  online: boolean;
  heatHazard: boolean;
}
```

Required launch state:

```ts
interface LaunchState {
  computerPrimed: boolean;
  fuelInstalled: boolean;
  progress: number;
  active: boolean;
  checklistVisible: boolean;
  lastFailReason: LaunchFailReason | null;
  reactorHasBeenOnline: boolean;
  bridgeEntered: boolean;
  shuttleEntered: boolean;
}
```

Logic:

- Plain state makes serialization, tests, and HUD projection easy.
- The state shape matches the visual integration contract.

---

### 6.2 Input

Each simulation tick receives:

```ts
interface SimInput {
  moveX: number;
  moveY: number;
  interact: boolean;
  useSelected: boolean;
  selectSlot: number | null;
  dropSelected: boolean;
}
```

Controls:

```text
MOVE: W A S D / ARROWS
INTERACT: E
USE SELECTED ITEM: F
SELECT ITEM: 1-6
DROP SELECTED ITEM: Q
```

Logic:

- `E` is world interaction.
- `F` is instant item use.
- `Q` is drop.
- This matches `visual.md` and adds the missing drop control required by `gameplay.md`.

---

### 6.3 Simulation Tick Order

Use this exact tick order for determinism:

```ts
function tick(input: SimInput) {
  if (state.status !== "running") return;

  state.time += SIM_DT;
  state.day = clampDay(state.time);

  processInputEdges(input);
  updatePlayerMovement(input);
  updateChannels(input);
  updateReactor();
  updateHullEvents();
  updatePower();
  updateAtmosphere();
  updateDrones();
  updatePlayerVitals();
  updateLaunch();
  evaluateEndStates();
  updateObjectives();
  updateWarnings();
  updateEventLog();
  emitAudioEvents();
}
```

Important ordering rules:

- Door and machine channel completion happens before power and atmosphere, so systems respond in the same tick.
- Reactor state updates before power, because reactor online status affects power.
- Hull events update before atmosphere, so a new breach drains O2 in the same tick.
- Drones update before player vitals, so drone damage applies in the same tick.
- Launch validation happens after all requirement-affecting systems have updated.
- End-state evaluation gives success precedence over death on the same tick.

Logic:

- The order prevents subtle bugs where one system uses stale state from another.
- It makes the launch success/death precedence rule explicit.

---

### 6.4 Event Bus

The simulation emits typed events.

```ts
type SimEvent =
  | { type: "item_picked_up"; item: ItemType }
  | { type: "item_dropped"; item: ItemType; roomId: RoomId }
  | { type: "door_opened"; doorId: DoorId }
  | { type: "door_closed"; doorId: DoorId }
  | { type: "door_repaired"; doorId: DoorId }
  | { type: "machine_repaired"; machineId: MachineId }
  | { type: "hull_patched"; roomId: RoomId }
  | { type: "breach"; roomId: RoomId }
  | { type: "power_cell_installed"; roomId: RoomId }
  | { type: "power_cell_expired"; roomId: RoomId }
  | { type: "epc_expired"; roomId: RoomId }
  | { type: "power_loss"; roomIds: RoomId[] }
  | { type: "reactor_coolant_used" }
  | { type: "reactor_spinup_started" }
  | { type: "reactor_online" }
  | { type: "reactor_coolant_expired" }
  | { type: "drone_activated"; droneId: "A" | "B" }
  | { type: "drone_alert"; droneId: "A" | "B" }
  | { type: "drone_attack"; droneId: "A" | "B" }
  | { type: "drone_disabled"; droneId: "A" | "B" }
  | { type: "emp_used" }
  | { type: "objective_complete"; objectiveIndex: number }
  | { type: "launch_requirement_met"; requirement: LaunchRequirement }
  | { type: "launch_reset"; reason: LaunchFailReason }
  | { type: "launch_success" }
  | { type: "game_over"; cause: FailCause }
  | { type: "hull_event_warning"; eventId: string; target: RoomId }
  | { type: "hull_event_damage"; eventId: string; target: RoomId; amount: number };
```

Logic:

- Events drive audio, log, and feedback without coupling systems.
- Tests can assert that required events happened.

---

## 7. System Designs

## 7.1 Player Movement and Vitals

### Player Constants

```ts
export const PLAYER_SPEED = 3.5;       // tiles/sec
export const PLAYER_RADIUS = 0.4;      // tiles
export const INTERACT_RADIUS = 1.5;    // tiles
export const PICKUP_RADIUS = 1.5;      // tiles
```

Logic:

- Player speed is slightly higher than drone alert speed.
- This ensures the player can avoid drones by movement and door management.
- 1.5 tile interaction radius is forgiving but still local.

### Movement

- Input vector is normalized.
- Velocity = input * `PLAYER_SPEED`.
- Movement uses tile collision.
- If a channel is active, player movement is locked.
- If the player releases `E`, leaves the interact radius, or the target becomes invalid, the channel interrupts according to channel rules.

Collision:

- Circle vs solid tile grid.
- Resolve X and Y separately for stable sliding.

### Player Vitals

Player O2 change per second based on current room O2:

```ts
if (room.o2 >= 60) player.o2 += 0.5 * dt;
else if (room.o2 >= 30) player.o2 -= 0.5 * dt;
else if (room.o2 >= 1) player.o2 -= 1.5 * dt;
else player.o2 -= 3 * dt;
```

If player O2 is 0:

```ts
player.integrity -= 5 * dt;
```

Integrity damage sources:

- Drone attack: 20 discrete damage.
- Reactor heat: 5/sec while in `reactor` and `reactor.heatHazard === true`.
- Asphyxia: 5/sec while player O2 is 0.

Clamp:

```ts
player.o2 = clamp(player.o2, 0, 100);
player.integrity = clamp(player.integrity, 0, 100);
```

Drone invulnerability:

- After taking drone damage, `player.invulnerable` is true for 0.5 sec.
- While invulnerable, drone attack attempts deal no damage.
- Reactor heat and asphyxia ignore drone invulnerability.

Logic:

- The room O2 table is the core environmental pressure.
- Drone invulnerability prevents instant death from repeated attack ticks.

---

## 7.2 Inventory and Items

### Inventory

```ts
interface InventorySlot {
  item: ItemType | null;
  count: number;
}
```

- 6 slots.
- Stackable items share one slot.
- Selected slot index is 1-based for UI, 0-based internally if needed.
- Wrench is not an inventory slot.

```ts
interface PlayerState {
  hasWrench: boolean;
  invulnerable: number;
  o2: number;
  integrity: number;
  room: RoomId;
  x: number;
  y: number;
}
```

### Pickup Rules

Pickup succeeds if:

- the item is within pickup radius, and
- either:
  - an existing stack of that item has `count < stackLimit`, or
  - an empty slot exists.

If pickup fails because inventory is full or stack is full, emit `ui_error` and show `INVENTORY FULL`.

Wrench pickup:

- If `player.hasWrench === false`, set it to true.
- If `player.hasWrench === true`, do not create a second wrench.
- The wrench cannot be dropped.

### Drop Rules

Drop:

- Requires selected slot with `count > 0`.
- Decrement stack by 1.
- Create a floor item at a deterministic nearby position.
- Dropped items persist.
- Dropped items do not despawn.
- Dropped items can be picked back up subject to stack limits.

Drop position:

- Try offsets around the player:
  - `(0.7, 0)`
  - `(0, 0.7)`
  - `(-0.7, 0)`
  - `(0, -0.7)`
  - `(0.7, 0.7)`
  - `(-0.7, 0.7)`
  - etc.
- The position must be inside the current room and not colliding with solid tiles.
- If no valid position is found, drop fails.

Logic:

- Dropped items prevent inventory softlocks.
- The wrench cannot be lost by accident.

### Instant Use

`F` uses selected item:

- O2 Tank:
  - Cannot use if player O2 is 100.
  - Adds +50 O2, clamped to 100.
  - Consumes one O2 Tank.
- Medkit:
  - Cannot use if Integrity is 100.
  - Adds +50 Integrity, clamped to 100.
  - Consumes one Medkit.

Other items do not use `F`.

Logic:

- Instant use keeps survival items responsive.
- Channel items use `E` on a target.

---

## 7.3 Doors

### Door State

```ts
type DoorState = "open" | "closed" | "jammed";
```

Initial states:

| Door | State |
|---|---|
| docking_crew | open |
| crew_storage | jammed |
| crew_medbay | open |
| storage_cargo | closed |
| crew_hydro | closed |
| hydro_engineering | jammed |
| hydro_shuttle | closed |
| engineering_reactor | closed |
| engineering_bridge | closed |
| bridge_shuttle | closed |

### Door Rules

- Open doors allow movement, airflow, power, and drones.
- Closed doors block movement, airflow, power, and drones.
- Jammed doors block everything until repaired.
- Repaired jammed doors become `closed`.
- No door is destroyed.
- No keycards.

### Door Channels

Door open/close:

- Duration: 1 sec.
- Requires player near door.
- Requires no item.
- Completion toggles state.
- Emits `door_opened` or `door_closed`.

Jammed door repair:

- Duration: 5 sec.
- Requires wrench.
- Completion sets state to `closed`.
- Emits `door_repaired`.
- Progress is retained if interrupted.

Logic:

- Doors are the main spatial control.
- Jammed doors teach repair before opening.

---

## 7.4 Channel System

Channels are the general action system.

```ts
interface ChannelState {
  action: ChannelAction;
  target: string;
  duration: number;
  progress: number;
  consumableItem?: ItemType;
  resetOnInterrupt: boolean;
  retainProgress: boolean;
}
```

Channel actions:

```ts
type ChannelAction =
  | "door_open"
  | "door_close"
  | "door_repair"
  | "machine_repair"
  | "hull_patch"
  | "power_install"
  | "coolant_use"
  | "fuel_install"
  | "launch_computer"
  | "reactor_spinup"
  | "emp_use"
  | "launch";
```

### Channel Rules

- A channel starts when `E` is held on a valid target.
- A channel progresses only while `E` is held and all requirements remain true.
- If `E` is released, the channel pauses or interrupts.
- If the player leaves the target room or interact radius, the channel interrupts.
- If a requirement becomes false:
  - most channels pause and retain progress,
  - launch resets,
  - reactor spin-up resets only if coolant expires.

Consumables are consumed only on completion.

Interrupted consumable channels do not consume the item.

### Channel Durations

| Action | Duration |
|---|---:|
| door open/close | 1 sec |
| jammed door repair | 5 sec |
| hull patch, non-breached | 3 sec |
| hull patch, breached | 4 sec |
| power cell install | 2 sec |
| O2 Generator repair | 5 sec |
| O2 Recycler repair | 6 sec |
| Shuttle O2 Vent repair | 5 sec |
| Coolant Pump repair | 5 sec |
| Coolant Cell use | 5 sec |
| Reactor Core repair | 8 sec |
| Reactor spin-up | 20 sec |
| Launch Computer | 15 sec |
| Fuel Line install | 10 sec |
| EMP use | 1 sec |
| Launch Pad channel | 30 sec |

### Channel Progress Retention

| Action | Progress on interrupt |
|---|---|
| door open/close | retained |
| jammed door repair | retained |
| machine repair | retained |
| hull patch | retained |
| power install | retained |
| coolant use | retained |
| fuel install | retained |
| launch computer | retained |
| reactor spin-up | retained unless coolant expires |
| EMP | reset |
| launch | reset |

Logic:

- Repairs should feel persistent.
- Launch is intentionally punishing and resettable.
- EMP is short and simple.

---

## 7.5 Hull and Breach System

### Room Hull

Each room has:

```ts
hull: number; // 0..100
breached: boolean;
```

Breach condition:

```ts
room.breached = room.hull <= 0;
```

Breach effects:

- Room O2 baseline drain becomes 15/sec instead of 0.5/sec.
- Map shows breach.
- Event log shows breach.
- Warning audio triggers.
- HUD shows `BREACH`.

### Hull Patch

Requires selected `hull_patch`.

If room hull > 0:

- Duration: 3 sec.
- Adds +40 hull.
- Clamps to 100.

If room is breached:

- Duration: 4 sec.
- Sets hull to 60.

Consumes Hull Patch only on completion.

Cannot patch a room with hull 100 and no breach.

Logic:

- Patching before events is the intended prevention.
- Sealing breaches is faster but leaves lower hull.

---

### Scheduled Hull Events

Events are fixed.

All events have a 10 second warning.

Data:

```ts
interface HullEventSpec {
  id: string;
  time: number;
  warningLead: number;
  damages: HullEventDamage[];
}

interface HullEventDamage {
  target: RoomId;
  amount: number;
  fallback: { room: RoomId; amount: number }[];
}
```

Event definitions:

#### Event 1

- Time: 240 sec.
- Target: `storage`, -30.
- Fallback:
  - `cargo`, -30,
  - `crew`, -20.

#### Event 2

- Time: 480 sec.
- Two separate damages:
  - `medbay`, -30,
  - `hydro`, -30.
- Fallback for each:
  - `crew`, -30,
  - `shuttle`, -30,
  - `storage`, -30,
  - `engineering`, -30,
  - `bridge`, -30.

#### Event 3

- Time: 720 sec.
- Target: `shuttle`, -50.
- Fallback:
  - `crew`, -20,
  - `hydro`, -20.

### Target Selection

At warning time:

- Select target for display and warning.
- Valid target must:
  - not be already breached,
  - not be the player’s current room,
  - not already be selected for the same event.

If the primary target is invalid, iterate fallback list in order.

At damage time:

- If the player is now in the selected target, reselect using the same fallback order to a valid room.
- If no valid target remains, skip that damage.

Apply damage:

```ts
room.hull = Math.max(0, room.hull - amount);
```

Event damage cannot raise hull.

If hull reaches 0, breach.

Logic:

- Warning at 10 sec gives the player time to react.
- Retargeting at damage time enforces “never target the room the player is currently in.”
- Fallbacks keep events fair if the intended room is already breached.

---

## 7.6 Atmosphere System

Each room has O2 from 0 to 100.

### Baseline Drain

If room is not breached:

```ts
room.o2 -= 0.5 * dt;
```

If room is breached:

```ts
room.o2 -= 15 * dt;
```

### O2 Machines

O2 machines:

| Machine | Room | Rate | Repair Time |
|---|---|---:|---:|
| crew_o2_generator | crew | +8/sec | 5 sec |
| hydro_o2_recycler | hydro | +4/sec | 6 sec |
| shuttle_o2_vent | shuttle | +6/sec | 5 sec |

Machine active if:

```ts
machine.repaired === true && room.powered === true
```

If active:

```ts
room.o2 += machine.rate * dt;
```

O2 is clamped to 100.

### Airflow

For each open door:

```ts
const a = roomA.o2;
const b = roomB.o2;
const diff = Math.abs(a - b);
const transferRate = 5 * diff / 100;
const transfer = transferRate * SIM_DT;
```

If `a > b`:

```ts
roomA.o2 -= transfer;
roomB.o2 += transfer;
```

If `b > a`:

```ts
roomB.o2 -= transfer;
roomA.o2 += transfer;
```

If difference is 0, no transfer.

Closed and jammed doors have no airflow.

All airflow should be calculated simultaneously using the pre-transfer O2 values, then applied.

Logic:

- Simultaneous airflow avoids door-order bias.
- The formula directly implements the gameplay design.
- Clamping after all changes keeps values valid.

---

## 7.7 Power System

Power is binary per room.

Power propagates only through open doors.

### Local Power Sources

Power nodes exist in:

- `crew`,
- `hydro`,
- `shuttle`.

Start EPC:

- Installed in `crew` at time 0.
- Duration: 400 sec.
- Occupies the crew power node.

Player Power Cell:

- Installable in an empty power node.
- Duration: 400 sec.
- Installation takes 2 sec.
- Consumed only on completion.

Reactor:

- Provides power from `reactor` room when online.
- Does not use a power node.
- Provides infinite power while coolant timer is active and spin-up is complete.

### Power Node Install Rule

A power node is installable when its local source slot is empty.

The room’s current powered state does not block installation.

Logic:

- `gameplay.md` says player cells are installable in empty power nodes.
- Interpreting “unpowered node” as “no local power source” avoids ambiguity.
- Requiring the whole room to be unpowered would create unnecessary edge cases and could block bridging power through already connected rooms.

### Power Propagation

Every tick:

1. Mark all rooms unpowered.
2. Add all rooms with active local sources to a queue.
3. For each powered room:
   - check connected rooms,
   - if the connecting door is open, mark the connected room powered.
4. Repeat until queue is empty.

Power does not pass through closed or jammed doors.

### Power Display

For HUD:

- Local EPC: `EPC M:SS`
- Local cell: `CELL M:SS`
- Local reactor: `REACTOR`
- Powered by non-local source: `POWERED`
- No power: `NO POWER`

### Power Events

Emit:

- `power_cell_installed`
- `power_cell_expired`
- `epc_expired`
- `power_loss`

`power_loss` should fire when a room that was powered becomes unpowered.

Logic:

- Power is a core decision system.
- BFS through open doors is simple, deterministic, and testable.

---

## 7.8 Reactor System

The reactor has two machines:

- `coolant_pump` in `engineering`
- `reactor_core` in `reactor`

### Reactor State

```ts
{
  pumpRepaired: boolean,
  coreRepaired: boolean,
  coolant: number, // seconds remaining
  spinUpProgress: number,
  spinUpComplete: boolean,
  online: boolean,
  heatHazard: boolean
}
```

### Requirements

To bring reactor online:

1. Repair `coolant_pump`.
2. Use a Coolant Cell on the pump.
3. Repair `reactor_core`.
4. Complete reactor spin-up.

### Coolant

Coolant duration:

```ts
180
```

Using a Coolant Cell:

- Requires `coolant_pump.repaired === true`.
- Channel duration: 5 sec.
- Sets `reactor.coolant = 180`.
- Does not add to existing coolant.
- Consumes Coolant Cell on completion.

### Spin-Up

Reactor spin-up:

- Requires `reactor_core.repaired === true`.
- Requires `reactor.coolant > 0`.
- Duration: 20 sec.
- Progress retained if player interrupts.
- If coolant reaches 0 during spin-up:
  - `spinUpProgress = 0`,
  - spin-up aborts.

If spin-up completes:

```ts
spinUpComplete = true;
```

### Online and Heat

```ts
reactor.online = reactor.spinUpComplete && reactor.coolant > 0;
reactor.heatHazard = reactor.spinUpComplete && reactor.coolant <= 0;
```

While `reactor.online`:

- Reactor provides power.
- Launch requirement `reactor online` is true.

While `reactor.heatHazard`:

- If player is in `reactor`, integrity drains at 5/sec.
- This is reactor heat damage, not drone damage.
- Drone invulnerability does not prevent it.

Logic:

- The coolant timer is a hard timer.
- The heat hazard makes expired coolant meaningful without creating a new damage system.

---

## 7.9 Drone System

There are exactly two drones.

```ts
interface DroneState {
  id: "A" | "B";
  home: RoomId;
  active: boolean;
  state: "inactive" | "patrol" | "alert" | "disabled";
  x: number;
  y: number;
  room: RoomId;
  waypointIndex: number;
  detectionTimer: number;
  noPathTimer: number;
  attackCooldown: number;
}
```

### Drone A

- Home: `cargo`
- Activates when player first enters `cargo`.

### Drone B

- Home: `shuttle`
- Activates when player first enters `shuttle`.

### Drone States

#### Inactive

- No movement.
- No attack.

#### Patrol

- Moves between fixed waypoints in home room.
- Speed: 2.5 tiles/sec.

#### Alert

- Activates from patrol when player is in same room for 1 second.
- Speed: 3.0 tiles/sec.
- If player is in same room:
  - move directly toward player.
- If player is in another room:
  - pathfind through open doors.
  - move toward next door on path.
- If no path exists:
  - wait 3 seconds, then return to patrol.

#### Attack

- If drone is within 1 tile of player:
  - if attack cooldown <= 0:
    - set attack cooldown = 1,
    - if player not invulnerable:
      - deal 20 integrity damage,
      - set player invulnerable = 0.5,
      - emit `drone_attack`.

#### Disabled

- Permanent.
- No movement.
- No attack.
- Does not re-activate.

### Drone Pathfinding

Use room graph BFS:

1. Build graph of rooms connected by open doors.
2. If drone and player are in same room:
   - target player position.
3. If different rooms:
   - find shortest room path.
   - target next door.
   - move until room changes.
4. If path becomes invalid:
   - re-path.
5. If no path:
   - wait 3 sec, then patrol.

Drones do not need tile-level obstacle avoidance. They use the collision grid only for wall/door passage.

Logic:

- The room graph is the gameplay abstraction.
- Drones are avoidable through doors.
- Simple BFS is sufficient for 10 rooms.

### EMP

EMP Charge:

- Use time: 1 sec.
- Can only be started if at least one active drone is in the player’s current room.
- On completion:
  - disable all active drones in the player’s current room,
  - consume one EMP Charge.
- If interrupted, progress resets and item is not consumed.

Logic:

- EMP is a threat-control tool, not a required progression item.
- The game must remain winnable without EMP.

---

## 7.10 Launch System

Launch requires all of the following to be true:

```ts
type LaunchRequirement =
  | "reactor_online"
  | "shuttle_powered"
  | "computer_primed"
  | "fuel_installed"
  | "shuttle_o2_sufficient";
```

Conditions:

```ts
reactorOnline = reactor.online;
shuttlePowered = rooms.shuttle.powered;
computerPrimed = launch.computerPrimed;
fuelInstalled = launch.fuelInstalled;
shuttleO2Sufficient = rooms.shuttle.o2 >= 60;
```

### Launch Machines

| Machine | Room | Effect |
|---|---|---|
| launch_computer | bridge | 15 sec channel, one-time |
| shuttle_o2_vent | shuttle | +6 O2/sec when repaired and powered |
| fuel_line | shuttle | 10 sec channel, requires Fuel Rod |
| launch_pad | shuttle | 30 sec final channel |

### Launch Computer

- Requires `bridge` powered.
- Duration: 15 sec.
- Progress retained if interrupted.
- Completion sets `launch.computerPrimed = true`.

### Fuel Line

- Requires selected `fuel_rod`.
- Duration: 10 sec.
- Progress retained if interrupted.
- Consumes Fuel Rod on completion.
- Completion sets `launch.fuelInstalled = true`.

### Shuttle O2 Vent

- Must be repaired.
- Requires `shuttle` powered.
- Adds +6 O2/sec to `shuttle`.

### Launch Pad Channel

- Location: `shuttle`.
- Duration: 30 sec.
- Player must remain at launch pad.
- All requirements must remain true.
- If any requirement fails:
  - progress resets to 0,
  - `lastFailReason` is set,
  - emit `launch_reset`.

Fail reasons:

```ts
type LaunchFailReason =
  | "REACTOR OFFLINE"
  | "SHUTTLE UNPOWERED"
  | "COMPUTER NOT PRIMED"
  | "FUEL MISSING"
  | "SHUTTLE O2 LOW"
  | "PLAYER DAMAGED"
  | "LEFT PAD";
```

### Launch Success

If launch progress reaches 100 and all requirements are true at end of tick:

- `status = "success"`.
- Emit `launch_success`.
- Success takes precedence over death or de-orbit on the same tick.

Logic:

- The launch checklist must always explain what is missing.
- Launch reset reasons are required by the visual design.
- Success precedence is an explicit gameplay rule.

---

## 7.11 Objectives

Main objective sequence:

| Index | Objective | Completion |
|---:|---|---|
| 0 | Repair Crew O2 Generator | `crew_o2_generator.repaired === true` |
| 1 | Stabilize Crew Atmosphere | Crew O2 >= 60 for 5 continuous seconds after objective 0 |
| 2 | Reach Hydroponics | Player first enters `hydro` |
| 3 | Restore Hydroponics O2 Recycler | `hydro_o2_recycler.repaired === true` |
| 4 | Bring Reactor Online | `reactor.online === true` |
| 5 | Prime Launch Computer | `launch.computerPrimed === true` |
| 6 | Install Shuttle Fuel | `launch.fuelInstalled === true` |
| 7 | Pressurize Shuttle | `rooms.shuttle.o2 >= 60` |
| 8 | Launch Shuttle | Launch completes |

Objective state:

```ts
interface ObjectiveState {
  current: number;
  crewStableTimer: number;
}
```

The objective sequence is sequential.

Logic:

- The HUD shows the next incomplete objective.
- This matches `gameplay.md` and `visual.md`.

---

## 7.12 HUD Projection

Create a pure function:

```ts
function createHudState(sim: SimState): HudState
```

`HudState` should expose the visual contract from `visual.md`.

Required sections:

- vitals,
- current room,
- time/objective,
- launch checklist,
- inventory,
- interaction prompt,
- event log,
- map,
- warnings,
- end screen data.

Example:

```ts
interface HudState {
  player: {
    o2: number;
    integrity: number;
    o2Warning: boolean;
    o2Critical: boolean;
    integrityWarning: boolean;
    integrityCritical: boolean;
  };
  room: {
    id: RoomId;
    name: string;
    o2: number;
    hull: number;
    breached: boolean;
    powerLabel: string;
    droneActive: boolean;
  };
  time: {
    day: number;
    timeToDeorbit: string;
    critical: boolean;
  };
  objective: {
    text: string;
  };
  launch: {
    visible: boolean;
    reactorOnline: boolean;
    shuttlePowered: boolean;
    computerPrimed: boolean;
    fuelInstalled: boolean;
    shuttleO2: number;
    progress: number;
    lastFailReason: LaunchFailReason | null;
  };
  inventory: {
    slots: {
      item: ItemType | null;
      count: number;
      selected: boolean;
    }[];
  };
  prompt: {
    text: string | null;
    progress: number | null;
    reason: string | null;
  };
  log: LogEntry[];
  map: {
    rooms: MapRoomNode[];
    doors: MapDoorLine[];
    eventWarning?: {
      roomId: RoomId;
      time: number;
    };
  };
  warnings: Warning[];
}
```

Numbers must be exact.

Bars may interpolate visually, but text values must be exact.

Logic:

- The renderer should not infer gameplay state.
- The HUD projection is the contract between simulation and visuals.

---

## 7.13 Warnings

Warnings are generated each tick.

Use priority from `visual.md`:

1. Player O2 critical
2. Player Integrity critical
3. Launch reset
4. Room breach
5. Reactor coolant low/expired
6. Hull event warning
7. Power source low/expiring
8. De-orbit warning
9. Room O2 low

Warning examples:

```text
PLAYER O2 CRITICAL 7
INTEGRITY CRITICAL 8
LAUNCH RESET — SHUTTLE O2 LOW
HULL BREACH — STORAGE
COOLANT LOW 0:24
HULL EVENT — SHUTTLE BAY 0:08
POWER SOURCE LOW — EPC 0:45
DE-ORBIT 1:45
ROOM O2 LOW — HYDROPONICS 22
```

Rules:

- Do not stack more than two visible warnings.
- If more than two exist, show highest priority and log the rest.
- Critical warnings require audible sound.
- Persistent warnings pulse slowly.
- Warning state is part of HUD projection, not stored as gameplay state beyond what is needed for deduplication.

Logic:

- The player must know immediately when they are dying.
- Warnings must not become screen noise.

---

## 7.14 Event Log

The event log stores the last 5 important events.

New events push old events down.

Examples:

```text
O2 Generator repaired
Power cell installed in Hydro
Power lost in Crew
Hull breach in Storage
Reactor coolant 0:30
Drone active in Shuttle Bay
Launch requirement met: Fuel installed
```

Do not log minor movement events.

Logic:

- The log provides history without requiring a full UI.
- It helps the player reconstruct what changed.

---

## 7.15 End States

### Success

If launch completes:

- `status = "success"`.
- Show success screen.
- Show:
  - systems restored,
  - time used,
  - drones disabled,
  - breaches sealed.

### Failure

Failure causes:

```ts
type FailCause =
  | "asphyxia"
  | "drone_attack"
  | "reactor_heat"
  | "integrity_failure"
  | "deorbit";
```

Failure occurs if:

- player integrity reaches 0, or
- time reaches 960 sec without launch success.

Success takes precedence over failure on the same tick.

Logic:

- The end screen should explain what happened.
- There is no mid-run respawn.

---

## 8. Rendering Implementation

Rendering must make the visual design work scalably.

It must not contain gameplay rules.

### 8.1 Renderer Responsibilities

- Draw world.
- Draw HUD.
- Apply camera.
- Interpolate movement.
- Manage particles.
- Render state from `HudState` and raw sim state.

Do not modify simulation state.

---

### 8.2 Camera

- Fixed top-down orthographic camera.
- Follows player.
- No rotation.
- No zoom.
- Clamp to world bounds.
- Show current room and enough adjacent walls to read doors.

Use render interpolation:

```ts
renderedX = lerp(prevX, currentX, alpha);
renderedY = lerp(prevY, currentY, alpha);
```

where `alpha = accumulator / SIM_DT`.

Logic:

- 20 Hz simulation can look choppy without interpolation.
- Interpolation improves feel without changing simulation.

---

### 8.3 Layer Order

Use:

1. Floor
2. Floor decals
3. State overlays: airflow, power conduits, breach effects, hazard shimmer
4. Machines, doors, items, player, drones
5. Particles
6. Warning vignettes
7. HUD

No dynamic shadows.

No parallax.

No zoom.

Logic:

- This matches `visual.md`.
- It keeps state readability high.

---

### 8.4 Asset Strategy

Use `src/data/assets.json` to map asset names to files.

Example:

```json
{
  "audio": {
    "o2_low": "audio/o2_low.ogg",
    "o2_critical": "audio/o2_critical.ogg"
  },
  "icons": {
    "air": "icons/air.svg",
    "shield": "icons/shield.svg"
  },
  "sprites": {
    "player": "sprites/player.png",
    "drone": "sprites/drone.png"
  }
}
```

The renderer should:

- load assets at boot,
- fail gracefully with placeholders if an asset is missing in development,
- log a console warning if a required audio asset is missing in production.

Logic:

- The visual designer owns asset creation.
- Engineering owns loading and rendering.

---

### 8.5 Procedural Textures

If no raster floor/wall assets are provided, generate lightweight procedural textures using `TextureFactory`.

Use the recipes from `visual.md`.

Keep them cheap:

- 256 px textures,
- noise,
- panel lines,
- scratches,
- no heavy detail.

Logic:

- Browser performance must remain good.
- State colors must remain reserved.

---

### 8.6 World Rendering

Render only visible and adjacent room content.

Render:

- rooms,
- walls,
- doors,
- machines,
- items,
- player,
- drones,
- power conduits,
- airflow particles,
- breach effects,
- reactor heat effects.

Door rendering:

- Open: panels retracted, white light line.
- Closed: panels filled, gray light line.
- Jammed: panels askew, red flashing light, warning stripes.

Machine rendering:

- Use simulation machine state.
- Damaged: red blink.
- Repaired: steady state color.
- Working: function-colored light.
- Channel active: progress ring.

Particle rules:

- Airflow particles only through open doors.
- No particles if O2 difference < 5.
- Particle count per door:

```ts
clamp(Math.abs(a.o2 - b.o2) / 10, 1, 5)
```

- Total particle cap: 128 per visible room.

Logic:

- Airflow is a core decision.
- Particles must be readable but not noisy.

---

### 8.7 HUD Rendering

HUD is Canvas-drawn.

Panels:

- vitals,
- current room,
- time/objective,
- launch checklist,
- inventory,
- interaction prompt,
- event log,
- map,
- warning banner,
- end screens.

HUD text must include labels, not color alone.

Required labels:

- `O2`
- `INTEGRITY`
- `HULL`
- `POWER`
- `DRONE`
- `BREACH`
- `COOLANT`
- `LAUNCH`
- `DAY`
- `TIME TO DE-ORBIT`

Logic:

- This satisfies accessibility and colorblind support.
- It matches `visual.md`.

---

## 9. Audio Implementation

The visual designer created the audio design. Engineering owns implementation.

### 9.1 AudioManager

Use one `AudioManager`.

Responsibilities:

- initialize `AudioContext` after user gesture,
- load audio assets,
- play one-shot events,
- manage looping warning sounds,
- stop loops when conditions end,
- support simple panning for drones/machines if useful.

Do not let audio affect simulation.

---

### 9.2 Audio Event Names

Use the names from `visual.md`:

```text
ui_select
ui_error
pickup
drop
use_o2
use_medkit
repair_start
repair_tick
repair_complete
door_open
door_close
door_jammed
door_repair
hull_patch
power_install
power_cell_expire
power_loss
o2_low
o2_critical
integrity_low
integrity_critical
breach
hull_event_warning
coolant_low
coolant_expired
reactor_spinup
reactor_online
reactor_heat
drone_activate
drone_alert
drone_attack
emp
deorbit_warning
objective_complete
launch_requirement
launch_reset
launch_success
game_over
```

Logic:

- The visual document defines the contract.
- Using the same names avoids integration drift.

---

### 9.3 Loop Management

Continuous warning loops are managed by polling HUD state each frame:

- `o2_low` when player O2 < 25
- `o2_critical` when player O2 < 10
- `integrity_low` when integrity < 25
- `integrity_critical` when integrity < 10
- `coolant_low` when reactor coolant <= 30 and reactor has been online
- `reactor_heat` when reactor heat hazard is active
- `deorbit_warning` when time to de-orbit <= 120 sec

Stop loops when the condition ends.

One-shot events are emitted by simulation.

Logic:

- This separates gameplay state from audio playback.
- It prevents duplicate warning spam.

---

## 10. Test Harness

The test harness must enable validation without a browser.

### 10.1 `createSimulation()`

```ts
function createSimulation(options?: {
  data?: StationData;
  layout?: LayoutData;
  seed?: number;
  overrides?: Partial<SimState>;
}): Simulation
```

Default options use `station.json` and `station-layout.json`.

The simulation must expose:

```ts
interface Simulation {
  state: SimState;
  tick(input?: SimInput): void;
  advance(seconds: number, input?: () => SimInput): void;
  emit: EventListener;
  on(event: string, cb: (data: unknown) => void): void;
  getState(): SimState;
  cloneState(): SimState;
  reset(): void;
}
```

`advance(seconds)` must run exact fixed-timestep ticks.

Logic:

- Tests need deterministic time control.
- `advance` makes full playthroughs simple.

---

### 10.2 Invariant Checker

Every test should run `assertInvariants(state)` after actions.

Check:

- No NaN in numeric state.
- Player O2 and Integrity are 0..100.
- Room O2 is 0..100.
- Room hull is 0..100.
- Breached is consistent with hull <= 0.
- Time is within 0..960 while running.
- Inventory has at most 6 slots.
- Inventory stack counts are within limits.
- Wrench is not in inventory slots.
- Wrench is not dropped.
- Floor item counts plus inventory counts do not exceed initial counts.
- Doors are valid states.
- Power state matches BFS through open doors.
- Drone positions are not outside world bounds.
- Drone room matches position or is a valid adjacent door transition.
- Reactor online/heat are consistent.
- Launch requirements are consistent with state.
- Event log has at most 5 entries.
- No negative timers.
- No active channel with invalid target.
- No item position outside room.
- No machine position outside room.

Logic:

- Invariants catch impossible states early.
- They make the simulation trustworthy.

---

### 10.3 Test Commands

The harness should allow high-level test commands:

```ts
harness.wait(sim, 1.0);
harness.set(sim, { "rooms.crew.o2": 80 });
harness.forcePlayerPosition(sim, { x: 5, y: 19 });
harness.forceDoorState(sim, "crew_hydro", "open");
harness.grantItem(sim, "o2_tank", 3);
harness.consumeChannel(sim, "crew_o2_generator", "machine_repair");
```

These are for tests only.

Logic:

- Unit tests should isolate systems.
- Full playthrough tests should use normal game actions where possible.

---

### 10.4 Test Bot

Create a `TestBot` that can play the game through the public simulation API.

Required methods:

```ts
bot.goToRoom(roomId: RoomId, opts?: { openDoors?: boolean; repairDoors?: boolean });
bot.goToPosition(x: number, y: number);
bot.pickItem(itemId: string);
bot.interact(machineId: MachineId);
bot.openDoor(doorId: DoorId);
bot.repairDoor(doorId: DoorId);
bot.patchRoom(roomId: RoomId);
bot.installPowerCell(roomId: RoomId);
bot.useCoolant();
bot.useEmp();
bot.useO2Tank();
bot.useMedkit();
bot.launch();
bot.waitCondition(predicate: (state: SimState) => boolean, timeoutSec: number);
bot.runReferenceGameplay();
bot.runNoEmpGameplay();
```

The bot should:

- use normal interactions for state changes,
- use movement and door interactions for pathing in the main playthrough,
- optionally use position overrides in fast reference tests,
- assert invariants after each major action,
- fail the test if the player dies before success.

Logic:

- A bot proves the systems are playable end-to-end.
- It is the closest thing to an automated playtest.

---

## 11. Required Test Suite

The following tests are required.

### 11.1 Level Builder Tests

`levelBuilder.test.ts`

Assert:

- default layout matches required room sizes.
- all doors are adjacent to the correct rooms.
- all machines are inside their rooms.
- all items are inside their rooms.
- all drone waypoints are inside their home rooms.
- all required items exist with correct total counts.
- all machines exist.
- all initial door states match `gameplay.md`.
- all initial room O2/hull values match `gameplay.md`.
- power nodes exist only in Crew, Hydro, Shuttle.
- start EPC is installed in Crew with 400 sec.
- room graph is connected.
- collision grid has passable interiors.
- closed/jammed doors are solid.
- open doors are passable.

---

### 11.2 Atmosphere Tests

`atmosphere.test.ts`

Assert:

- unpowered, unbreached room loses 0.5 O2/sec.
- breached room loses 15 O2/sec.
- repaired powered O2 generator adds +8/sec in Crew.
- repaired powered O2 recycler adds +4/sec in Hydro.
- repaired powered shuttle vent adds +6/sec in Shuttle.
- airflow transfer uses `5 * abs(diff) / 100 * dt`.
- closed doors do not transfer O2.
- jammed doors do not transfer O2.
- O2 clamps to 0..100.
- multiple open doors transfer simultaneously without order bias.

---

### 11.3 Power Tests

`power.test.ts`

Assert:

- start EPC powers Crew for 400 sec.
- power propagates through open doors only.
- closed doors block power.
- jammed doors block power.
- installing a power cell in an empty node adds 400 sec local power.
- installing a power cell consumes the cell only on completion.
- interrupting installation does not consume the cell.
- EPC expiration removes local power.
- reactor online powers Reactor Core and propagates through open doors.
- reactor offline removes reactor power.
- power loss events fire when rooms lose power.

---

### 11.4 Hull Tests

`hull.test.ts`

Assert:

- hull patch adds +40 when not breached.
- hull patch seals breach to 60.
- hull patch consumes item only on completion.
- interrupted patch does not consume item.
- event 1 warns at 230 and damages at 240.
- event 1 targets Storage unless already breached or player is there.
- event 1 fallback works.
- event 2 damages Medbay and Hydro at 480.
- event 3 damages Shuttle at 720.
- event damage cannot raise hull.
- event damage can cause breach.
- event skips if no valid target remains.
- warnings appear on HUD/map with countdown.

---

### 11.5 Reactor Tests

`reactor.test.ts`

Assert:

- coolant pump must be repaired before coolant use.
- coolant use sets timer to 180, not additive.
- reactor core must be repaired before spin-up.
- spin-up requires coolant > 0.
- spin-up completion sets spin-up complete.
- coolant expiration during spin-up resets spin-up.
- reactor online requires spin-up complete and coolant > 0.
- reactor heat hazard occurs when spin-up complete and coolant <= 0.
- reactor heat drains player integrity at 5/sec while in Reactor Core.
- reactor provides power while online.
- reactor stops providing power when coolant expires.

---

### 11.6 Drone Tests

`drones.test.ts`

Assert:

- Drone A activates when player first enters Cargo.
- Drone B activates when player first enters Shuttle.
- inactive drones do not move or attack.
- patrol speed is 2.5 tiles/sec.
- alert speed is 3.0 tiles/sec.
- alert requires 1 second detection in same room.
- drone pathfinds through open doors.
- closed doors block drone path.
- no path causes patrol return after 3 sec.
- drone attack deals 20 damage.
- drone attack cooldown is 1 sec.
- drone invulnerability is 0.5 sec.
- EMP disables active drones in current room.
- EMP requires at least one active drone in current room to start.
- disabled drones remain disabled.

Also include a no-EMP avoidance test:

- player can enter a drone room,
- close the entry door,
- trap the drone,
- avoid damage,
- exit through another path or remain safe.

Logic:

- The game must be avoidable without EMP.

---

### 11.7 Inventory Tests

`inventory.test.ts`

Assert:

- pickup respects stack limits.
- pickup fails if inventory full.
- drop creates persistent floor item.
- dropped items can be picked back up.
- wrench cannot be dropped.
- wrench is not in inventory slots.
- O2 tank cannot be used at 100 O2.
- Medkit cannot be used at 100 Integrity.
- O2 tank adds +50 O2.
- Medkit adds +50 Integrity.
- consumables are removed on use.

---

### 11.8 Channel Tests

`channels.test.ts`

Assert:

- channels require hold `E`.
- release `E` pauses or interrupts correctly.
- progress retained for repairs.
- progress retained for door open/close.
- progress retained for launch computer.
- progress retained for fuel install.
- consumables are not consumed on interrupt.
- consumables are consumed on completion.
- launch channel resets on requirement failure.
- launch channel resets on player leaving pad.
- launch channel resets on player damage.
- reactor spin-up resets on coolant expiration.
- jammed door repair becomes closed door.

---

### 11.9 Launch Tests

`launch.test.ts`

Assert:

- launch computer requires Bridge powered.
- launch computer completes once.
- fuel line requires Fuel Rod.
- fuel line completes once.
- launch requires reactor online.
- launch requires shuttle powered.
- launch requires shuttle O2 >= 60.
- launch requires computer primed.
- launch requires fuel installed.
- launch progress advances only at launch pad.
- launch progress resets with correct reason.
- launch succeeds at 100%.
- launch success takes precedence over death on same tick.
- launch success on exact 960 sec tick is success.
- de-orbit at 960 without launch is failure.

---

### 11.10 Objective Tests

`objectives.test.ts`

Assert:

- objective sequence is sequential.
- Crew stabilize requires 5 continuous seconds at O2 >= 60 after generator repair.
- reach Hydro objective completes on first entry.
- reactor objective completes when reactor online.
- launch checklist becomes visible after Bridge or Shuttle entry or first reactor online.
- objective completion events fire.

---

### 11.11 End State Tests

`endStates.test.ts`

Assert:

- player death by asphyxia.
- player death by drone attack.
- player death by reactor heat.
- failure by de-orbit.
- success by launch.
- success precedence over death.
- success precedence over de-orbit on same tick.
- failure screen cause is correct.
- restart resets state.

---

### 11.12 HUD Projection Tests

`hudProjection.test.ts`

Assert:

- vitals show exact O2 and Integrity.
- current room shows O2, hull, power label, drone state, breach state.
- power labels are correct:
  - `NO POWER`
  - `POWERED`
  - `EPC M:SS`
  - `CELL M:SS`
  - `REACTOR`
- launch checklist shows all five requirements.
- launch checklist shows progress.
- map nodes show room state.
- map door lines show open/closed/jammed.
- warnings respect priority.
- event log stores last 5 events.

Logic:

- The visual contract must be testable without rendering pixels.

---

### 11.13 Audio Event Tests

`audioEvents.test.ts`

Use a mock audio collector.

Assert required one-shot events fire during scripted scenarios:

- `pickup`
- `drop`
- `use_o2`
- `use_medkit`
- `repair_start`
- `repair_complete`
- `door_open`
- `door_close`
- `door_repair`
- `hull_patch`
- `power_install`
- `power_cell_expire`
- `power_loss`
- `breach`
- `hull_event_warning`
- `drone_activate`
- `drone_alert`
- `drone_attack`
- `emp`
- `coolant_expired`
- `reactor_spinup`
- `reactor_online`
- `objective_complete`
- `launch_requirement`
- `launch_reset`
- `launch_success`
- `game_over`

Logic:

- The audio design is complete; engineering must prove the hooks exist.

---

### 11.14 Reference Playthrough Test

`playthroughReference.test.ts`

This test must prove the game is finished and playable.

It should run a full deterministic bot playthrough using normal game actions.

Required assertions:

- simulation starts with all initial values correct.
- bot completes all main objectives.
- reactor comes online.
- launch computer primes.
- fuel installs.
- shuttle O2 reaches 60.
- launch completes.
- final status is `success`.
- final time is < 960 sec.
- no invariant violations occur at any point.
- required audio events fire.
- required event log entries appear.
- player does not die.
- success screen data is valid.

The bot may use high-level movement helpers, but all state changes must go through simulation actions.

Logic:

- This is the core “game is playable” test.

---

### 11.15 No-EMP Playthrough Test

`playthroughNoEmp.test.ts`

This test must prove launch is possible without EMP.

Required assertions:

- no EMP charges are granted to the player.
- bot avoids or traps drones using doors and movement.
- launch completes.
- final status is `success`.
- no drone damage is required to win.
- no invariant violations.

Logic:

- `gameplay.md` explicitly requires launch to be possible without EMP.
- This prevents hidden dependency on EMP progression.

---

### 11.16 Failure Playthrough Tests

Add at least these:

1. No O2 management:
   - player stays in a low-O2 room,
   - O2 tanks are unavailable,
   - player dies by asphyxia.

2. Reactor heat:
   - reactor spin-up completes,
   - coolant expires,
   - player remains in Reactor Core,
   - player dies by reactor heat.

3. De-orbit:
   - no launch,
   - time reaches 960,
   - failure cause is de-orbit.

4. Drone kill:
   - player fails to avoid drone,
   - integrity reaches 0,
   - cause is drone attack.

Logic:

- Failure states are part of the finished game.
- They must be deterministic and readable.

---

### 11.17 Performance Test

`performance.test.ts`

Assert:

- 960 seconds of simulation = 19200 ticks.
- Run 19200 ticks in headless mode.
- Complete within a reasonable CI budget, recommended 5 seconds.
- Memory does not grow unbounded.
- No exceptions.

Logic:

- The game is short, but the simulation must be stable for tests.

---

### 11.18 Browser Smoke Test

Optional but recommended:

`e2e/browser.smoke.spec.ts`

Assert:

- app boots.
- title screen renders.
- clicking Start starts game.
- canvas is visible.
- no console errors for 10 seconds.
- HUD is visible.
- simulation time advances.

Logic:

- Headless tests prove gameplay logic.
- A smoke test proves browser integration.

---

## 12. Acceptance Criteria

The game is finished when:

1. `npm run typecheck` passes.
2. `npm run build` passes.
3. `npm test` passes.
4. All required tests in section 11 pass.
5. The reference playthrough succeeds before 960 sec.
6. The no-EMP playthrough succeeds before 960 sec.
7. All invariants pass every tick during playthrough tests.
8. All required audio event hooks exist.
9. HUD projection exposes all required visual states.
10. No simulation logic depends on DOM, audio, or rendering.
11. No random values affect simulation.
12. The browser smoke test passes, if enabled.
13. The production build has no console errors during the reference run.

---

## 13. Cuts and Non-Goals

The following are intentionally cut:

- No save system.
- No mid-run checkpoints.
- No respawn.
- No random events.
- No random item drops.
- No random drone spawns.
- No alternate maps.
- No level procedural generation.
- No 3D.
- No 2.5D.
- No vertical gameplay.
- No exterior space.
- No water/food/temperature systems.
- No crafting.
- No upgrades.
- No multiplayer.
- No destructible doors.
- No destructible machines.
- No tile-level drone pathfinding.
- No complex physics.
- No ECS framework.
- No game engine.
- No pause menu during core run.
- No dynamic lighting.
- No fog of war.
- No decorative state colors.
- No full-screen strobing.
- No collectible trinkets.

Logic:

- Each cut system adds UI, testing, and integration cost without strengthening the core O2/power/hull/drone/launch loop.

---

## 14. Integration Contracts

### 14.1 HUD Types

The simulation must produce state compatible with the visual types in `visual.md`.

Required types:

```ts
type RoomState = {
  id: string;
  name: string;
  o2: number;
  hull: number;
  breached: boolean;
  powered: boolean;
  droneActive: boolean;
  objective: boolean;
  eventWarning: boolean;
  eventWarningTime?: number;
};

type PowerState = {
  source: "none" | "epc" | "cell" | "reactor" | "powered";
  timeLeft?: number;
};

type PlayerState = {
  o2: number;
  integrity: number;
  currentRoom: string;
  invulnerable: boolean;
};

type ReactorState = {
  online: boolean;
  coolant: number;
  spinningUp: boolean;
  heatHazard: boolean;
};

type LaunchState = {
  reactorOnline: boolean;
  shuttlePowered: boolean;
  computerPrimed: boolean;
  fuelInstalled: boolean;
  shuttleO2: number;
  progress: number;
};
```

The renderer may interpolate bars, but text numbers must be exact.

---

### 14.2 Audio Contract

Simulation events and HUD state must be sufficient for the AudioManager to play all required sounds.

The integration agent should not need to infer audio from private system state.

Use the audio event names from section 9.2.

---

### 14.3 Visual State Contract

The renderer must be able to determine:

- player O2,
- player integrity,
- current room O2,
- current room hull,
- current room breach,
- current room power,
- current room drone,
- coolant timer,
- launch checklist,
- de-orbit timer,
- door states,
- machine states,
- item positions,
- drone positions,
- objective room,
- hull event warning target,
- airflow direction between open doors,
- power conduit state.

If a state is not exposed in simulation state or HUD projection, the renderer must not need it.

---

## 15. Final Engineering Principle

The station is a deterministic system.

The engineering goal is:

1. Make every gameplay rule testable.
2. Make every required state exposed to the HUD.
3. Make every required audio event fire.
4. Make the fixed level function reliably.
5. Prove playability with an automated bot.

If a feature cannot be validated by a headless test or a deterministic bot, cut it or make it simpler.