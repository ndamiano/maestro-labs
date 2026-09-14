# DERELICT STATION — INTEGRATED BUILD SPEC

This document supersedes `gameplay.md`, `visual.md`, and `engineering.md` in full. Every number, name, and rule in it is final. Where the three sources disagreed, the ruling in 0.2 is the rule. Where one left a placeholder, it is filled here. Nothing from the three documents is dropped: each piece is carried, ruled on, or staged under a tier (0.3).

---

# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Runs as a browser game (page, canvas, keyboard; no installs, no assets pipeline) | 1.1, 2.1, 10 (M11), 9 (browser smoke) |
| Survival gameplay: the player has survival stats, stats can run out, failure ends the run | 4.4 (Player Vitals), 4.14 (End States), 11 |
| Set in a derelict space station: one derelict orbital station, 10 compartments, no exterior, is the entire world | 4.2 (Room roster), 3.3 (Space), 11 |
| *added* Air management: room O2, airflow through doors, O2 machines, player O2 | 4.7 (Atmosphere) |
| *added* Power management: timed sources, installable cells, propagation through open doors | 4.8 (Power) |
| *added* Hull integrity with three scheduled breach events and patches | 4.9 (Hull and Breach) |
| *added* Reactor: coolant, spin-up, online power, heat hazard | 4.10 (Reactor) |
| *added* Threat: exactly two maintenance drones, avoidable without items | 4.11 (Drones) |
| *added* Objective: launch the shuttle before de-orbit (960 s), multi-requirement final channel | 4.12 (Launch), 4.14 |
| *added* Guided progression: 9-objective chain and pacing | 4.13 (Objectives), 4.15 |
| *added* Items and inventory: 6 slots, stacks, drops persist, fairness counts | 4.16 (Items and Inventory) |
| *added* Readable HUD: vitals, room status, map, checklist, warnings, log, prompt | 7 (UX) |
| *added* Audio feedback: every warning and major event has a sound, synthesized at runtime | 6 (Audio) |
| *added* End screens: success and failure with cause and stats, restart | 7.5, 4.14 |
| *added* Deterministic, fixed-step simulation with a full headless test suite | 1.2, 8 (Debug API), 9 (Tests) |
| *added* Presentation polish: music layers, particles, positional pan, texture detail | 3, 6.2, 0.3 (T2) |

## 0.2 Decisions

| Topic | Gameplay said | Visual said | Engineering said | Ruling |
| --- | --- | --- | --- | --- |
| Audio delivery | Lists 15 required audio events; "sound specificity is not part of this document" | SFX designs and music stems described, implying sound files | `.ogg` asset manifest with missing-file fallback | **No audio assets.** All SFX and music are synthesized at runtime with the Web Audio API from the recipes in 6; the event names in 6.4 are the contract; a missing recipe logs a console warning and plays nothing. One clause why: the build is a self-contained browser page and the builder must own every sound. |
| Player O2 zero-air bucket | "0 → −3/sec" | silent | "room O2 below 1 → −3/sec" | **Room O2 below 1 uses the −3/sec bucket** (engineering 30.3). One clause why: O2 is continuous, so a room at 0.4 is zero air. |
| Direct item-use key | silent | "USE SELECTED ITEM: E if applicable, or F" | E = station interact/pickup, F = direct item use, Q = drop | **Engineering's mapping** (E pick up / hold channel, F press instant use, F hold EMP, Q drop); all prompts display F. One clause why: E is already the channel key, so one direct-use key keeps prompts unambiguous. |
| Drone alert delay | "Alert delay: 1 second" | silent | delay omitted | **Carry the 1-second delay:** drone lingers in patrol 1 s before switching to alert (4.11). One clause why: gameplay's number governs; the omission was a gap. |
| Power cell node rule | "installed in an unpowered node" | silent | node empty = no local source; propagated power allowed | **Engineering's rule** (15.3): a cell installs into a node with no local source even if the room is powered by propagation. One clause why: otherwise cells cannot extend the grid they are meant to extend. |
| EMP consumption | "Use time: 1 second. Consumed instantly." | silent | 1 s channel, consumed on completion | **1 s channel, consumed only on completion** (4.11, 4.17). One clause why: an interrupted EMP must not burn a charge; consistent with every consumable channel. |
| Coolant-application feedback | silent | no dedicated SFX | unresolved (event/audio deliberated, no final) | **Event `reactor_coolant_applied`, audio `repair_complete`, log "Reactor coolant applied"** (6.3). One clause why: stable event name, and a generic mechanical completion sound is safe. |
| Spin-up abort feedback | "Spin-up aborts. Progress resets to 0." | silent | use `ui_error` | **Event `reactor_spinup_aborted`, log "Reactor spin-up aborted", audio `ui_error`** (6.3). One clause why: an abort is a soft failure, not a launch reset. |
| Warning priority | silent | 9-item priority list | 12-item priority list | **Engineering's 12-item list** (4.13): it splits coolant low/expired and adds low vitals while preserving visual's relative order. One clause why: superset that keeps visual's ordering. |
| Render layer order | silent | 7 draw groups | 11-step draw order | **Engineering's 11-step order** (3.4). One clause why: it refines visual's grouping and pins player and drones above particles. |
| HUD placement | "top-left or bottom-left, depending on visual layout" (defers) | concrete layout diagram and component locations | component list only | **Visual's layout wins** (7.2). One clause why: visual owns screen placement and gameplay deferred to it. |
| Fonts | silent | Inter/Roboto + monospaced numerals recommended | no assets implied | **System font stacks, no downloads:** labels `Inter, Roboto, "Segoe UI", system-ui, sans-serif`; numbers `ui-monospace, "JetBrains Mono", "IBM Plex Mono", monospace`. One clause why: offline browser page; visual's "or similar" permits fallbacks. |
| Restart / pause | "no respawn, no checkpoint, no retry from mid-run" | "No pause menu in core run; restart returns to title or restarts run" | no pause; restart button → fresh initial state | **No pause.** End screens have RESTART (immediately a fresh run) and TITLE (back to title). One clause why: fastest retry fits the 16-minute session and visual permits either target. |
| Screenshots table | silent | 14-item Visual QA Checklist, no table | silent | **The 9 SCREENSHOTS table is constructed from visual's QA checklist plus its end screens** (9.3). One clause why: the build spec needs concrete screenshot rows and the checklist defines the states; no QA check is dropped (each maps to a row or an 11 accessibility check). |
| Player renderer | silent | player sprite with 7 states | render file list omits a player module | **Add `src/render/playerRenderer.js`** (2.1). One clause why: visual specifies a player sprite; engineering's omission was a gap. |
| State omissions | silent | n/a | `state.channels` defined in 13.1 but absent from the 4.3 state shape | **Add `state.channels`, `meta.nextItemId`, `player.facing` to 2.2.** One clause why: channel progress, item IDs, and visor facing must live in the serializable state. |
| Wrench scope | "required for repairs and jammed doors" | silent | enumerates required and not-required uses | **Engineering's list:** wrench required for machine repairs, jammed door repair, hull patch/seal; not required for door open/close, power cell install, coolant use, fuel line, launch computer, reactor spin-up (4.17). One clause why: explicit scope prevents over-gating. |
| Launch pad range | "player must remain at the launch pad" (no number) | silent | 1.5 tiles | **1.5 tiles** (4.12). One clause why: engineering pins the number; it matches the machine interaction range. |
| Player speed | silent | silent | 3.5 tiles/sec | **3.5 tiles/sec** (4.3). One clause why: it outruns an alert drone (3.0) with margin, as the design requires. |
| Drone patrol waypoints | "two or three fixed waypoints" | silent | three deterministic waypoints | **Three: room center, top-left inset, bottom-right inset** (4.11). One clause why: engineering pins gameplay's open range. |
| Music tier | silent | full music identity (9 stems) | MusicManager with crossfades | **All SFX are T1; all music layers are T2** (0.3). One clause why: every mandatory warning already has a T1 SFX; music is atmosphere, not information. |
| Particles tier | silent | airflow/breach/EMP/steam particles | particle budgets | **T1 ships with core feedback only** (damage flash, vignette, flicker, shake) and a no-op particle system; airflow, breach, spark, steam, EMP particles are T2 (0.3). One clause why: every state is already readable via HUD, map, labels, and sound; particles decorate, they do not inform. |
| Hull event retargeting | fallback chains per event | silent | recalculate target every tick during the 10 s warning | **Recalculate every tick using gameplay's candidate chains** (4.9). One clause why: "never target the current player room" must stay fair. |
| Airflow simultaneity | "apply transfer from higher to lower" | silent | compute from start-of-phase values, apply simultaneously | **Simultaneous transfer** (4.7). One clause why: removes iteration-order dependence. |
| Reactor heat condition | "reactor online but coolant has expired" | silent | `spinUpComplete and not coolantActive` | **`spinUpComplete and not coolantActive`** (4.10). One clause why: the conditions are identical, and a reactor that never spun up must not become a heat trap. |
| Launch pause vs reset | "leaves pad / damaged / requirement fails → reset" | silent | releasing E pauses; leaving resets | **Releasing E at the pad pauses; leaving the pad or any requirement failing resets** (4.12). One clause why: releasing E is not an interruption; leaving the pad is. |
| Random source | "no RNG is required for core progression" | silent | no `Math.random` in simulation; renderer may | **`Math.random()` is the one random source, used only in `src/render/particleSystem.js`; simulation, audio, and input never randomize** (1.2). One clause why: one audited source keeps every run deterministic and testable. |
| Browser smoke test | silent | silent | "optional but recommended" | **T1**, part of Definition of Done. One clause why: browser wiring is ship risk that Node tests cannot cover. |

## 0.3 Tiers

**T1 — the game that must ship, by system name:** Level compile and validation; Fixed-step simulation; Movement and doors; Player vitals; Atmosphere; Power; Reactor; Hull and scheduled events; Drones; Items and inventory; Channels and machines; Launch; Objectives; Warnings and event log; End states and end screens; Title screen; Core HUD (all sections in 7.2); Core SFX (all 6.3 rows); Invariants; Test suite (all 9.1–9.2 files including acceptance); Browser smoke test.

**T2 — staged polish; each item is independent of the others; add in this order:**
1. Music layers (base, low O2, power loss, reactor, coolant low, final countdown, success, failure; 0.5 s crossfades) — 6.2.
2. Airflow particles through open doors and breach vacuum streaks — 3.6.
3. Cosmetic particles: repair sparks, EMP ring, reactor steam, dust puffs, boot dust — 3.6, 10.
4. Positional pan (drones, machines, adjacent-room breaches) — 6.4.
5. Warning-banner pulse (max 2 Hz) and HUD bar interpolation — 7.4.
6. Procedural texture detail: scratches, wear stains, caution stripes — 3.5.
7. Static world pre-render to offscreen canvas — 10.
8. Title-screen state icon legend — 7.3.
9. Browser debug-invariants toggle (`dbg.invariants(on)`) — 8.

Every system in section 4 is tagged `Tier: T1` where specified; T2 items above are presentation only and never gate a T1 check.

---

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- 1 tile = 0.5 meters. World positions are continuous tile coordinates.
- Origin (0,0) is the top-left of the world. `x` increases right, `y` increases down.
- Simulation: fixed timestep, **20 updates/sec**, `DT = 0.05 s`. All rates in this document are per second.
- Rendering: target 60 FPS; simulation stays 20 Hz. Frame is designed for **1920×1080**, minimum comfortable **1366×768**; HUD stays inside a 24 px safe margin and scales with window.
- World scale: **96 px/tile** at 1080p, scaled down for smaller windows. HUD is independent of world scale.
- Sprite sizes at 1080p (proportions preserved when scaled): base tile 96 px; player 32–40 px; drone 36–44 px; machines 64–128 px; pickups 20–28 px.
- Time formats: de-orbit countdown, EPC/CELL timers, and coolant timer display as `mm:ss`. Day display: `Day 1`…`Day 8`, computed as `min(8, floor(time / 120) + 1)`.
- Performance: one tick must be cheap enough to run thousands of ticks in Node; no per-tick full state cloning in the browser; 10 rooms, 2 drones, max 512 particles total (T2); HUD updated 20 Hz.

## 1.2 Important conventions

Carried from engineering, ruled against the other two where they touched it (rulings in 0.2).

- **Units/axes/origin:** tile units, origin top-left, `x` right, `y` down (above).
- **Camera:** fixed top-down orthographic; follows the player; player kept near screen center; shows current room plus enough adjacent wall to read doors; no rotation, no zoom, no parallax; clamped so the player is never lost outside station bounds.
- **Fixed-step loop:** accumulate real elapsed time; clamp max frame delta to **0.25 s** (tab-sleep spiral guard); while accumulator ≥ `DT`, run one simulation tick; then render.
- **Simulation purity:** the simulation owns all gameplay state and win/lose rules. No DOM, no canvas, no audio, no `Math.random`, no timestamps, no async inside simulation. Renderer and audio only observe state and events.
- **One random source:** `Math.random()` is used only by `src/render/particleSystem.js` (T2). Simulation, audio, and input are never randomized.
- **Determinism:** all event IDs, log IDs, dropped item IDs, and power cell IDs come from `state` counters. Same input sequence → same state and event sequence.
- **Tick order** — every simulation tick runs these 15 steps in this exact order:
  1. Check running state — if `status` is not `'running'`, return no events.
  2. Advance time — `meta.tick += 1`, `meta.time += DT`, clear per-tick flags (`player.tookDamageThisTick`).
  3. Hull event warnings and damage — recalculate active warnings during the 10 s window; apply scheduled damage at event time; update breached state; emit breach events.
  4. Player movement — apply input, resolve against room interiors and open door gaps, determine new current room.
  5. Direct player actions — pick up on `interactPressed`; instant use on `usePressed`/`useDown`; drop on `drop`; update inventory.
  6. Non-launch channels — resolve nearest channel target while `interactDown`; advance progress; complete doors, repairs, installs, coolant use, launch computer, fuel line, reactor spin-up, hull patch/seal, power cell install; consume items only on completion. A completed door action changes the door and affects power/airflow/drones **in this same tick**.
  7. Power update — decrement timed sources; remove expired; recompute propagation through open doors; emit power loss/expiration events.
  8. Reactor update — decrement coolant; update `coolantActive`; abort spin-up if coolant expires; update `online`, `heatHazard`; emit reactor events.
  9. Atmosphere update — baseline/breach drain; O2 machines; airflow through open doors; clamp room O2 to 0–100.
  10. Drone update — activation, states, movement, attacks; emit drone events.
  11. Player vitals — player O2 from room O2; asphyxia; reactor heat; clamp; invulnerability; set `tookDamageThisTick` if integrity decreased.
  12. Launch update — evaluate requirements; advance channel; reset or succeed; emit launch events.
  13. End-state evaluation — success first, then integrity ≤ 0 failure, then time ≥ 960 de-orbit failure (same-tick precedence: success beats death, death beats de-orbit).
  14. Warnings and event log — warning transitions, warning audio events, append important events.
  15. Invariants — if `meta.debugInvariants`, validate state.
- **Render pass order** (per rendered frame): 1 floor, 2 floor decals, 3 state overlays (airflow, conduits, breach, hazard shimmer), 4 machines, 5 doors, 6 items, 7 player, 8 drones, 9 particles, 10 screen warning overlays/vignettes, 11 HUD. Ruling: engineering's 11-step order over visual's 7 groups (0.2).
- **Controls table:**

| Input | Action |
| --- | --- |
| `WASD` / arrows | move |
| `E` press | pick up nearest item (within 1.0 tile) |
| `E` hold | channel with nearest interactable (repair, door, install, patch, spin-up, computer, fuel, launch) |
| `1`–`6` | select inventory slot |
| `F` press | instant-use selected item (O2 Tank, Medkit) |
| `F` hold | timed direct use — EMP channel (1 s) |
| `Q` | drop selected item (wrench cannot be dropped) |

Ruling: engineering's key map over visual's "E or F" (0.2). Visual prompts must match this table exactly.

---

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

---

# 3. VISUAL SPEC

**The look in one paragraph.** DERELICT STATION looks like a practical, worn, emergency-mode space station — functional, damaged, still operating, slightly lived-in, cold and mechanical, a controlled system dying slowly. It is not cyberpunk neon, not cartoonish, not horror-gore, not a sleek new station, not sci-fi fantasy, not a maze. The core promise: *the station is a system; the player reads systems, not scenery.* Every important state — O2, power, hull, drones, coolant, launch requirements, de-orbit pressure — must be readable instantly, and never by color alone.

**Lighting and atmosphere.** No dynamic lighting, no dynamic shadows, no parallax. Flat sprites with subtle dark underlays for separation. Static dimmed lights in the world; functional warning lights only. Atmosphere effects are subtle pulses (max 2 Hz), never strobing or full-screen noise: low-O2 cyan edge vignette, damage red edge flash (max 0.2 s), screen shake (max 4 px, 0.15 s), warm vignette confined to Reactor Core during heat hazard, white fade on launch success, desaturate-and-darken on game over. No exterior space; the setting is sold with static portholes and a faint machine-room backdrop on the title screen.

**The space.** One station, 10 rooms, drawn as flat top-down rectangles at 96 px/tile (1080p). All rooms share base floor (`#171c22`), base wall (`#2a3138`), door frame style, machine state language, HUD icons, warning system, and particle budget. Each room carries one desaturated accent, one or two signature non-interactive details, and a floor decal with its abbreviation. Room accents are decoration only and must never imitate a state color. No room introduces a new visual state language; each is recognizable from its signature object, not just its color.

Room identity table (carried from visual §9):

| Room | Visual identity | Accent token | Non-interactive details | Why distinct |
| --- | --- | --- | --- | --- |
| Docking Bay | Clean start area, neutral gray | `docking #8ea1b3` | Docking clamps, faint white lights, small porthole | Safe tutorial room, visually calmer |
| Crew Quarters | Lived-in hub | `crew #b8a98f` | Bunks, personal storage, soft amber wall light | Central hub should feel occupied |
| Storage | Industrial resource room | `storage #8f7358` | Shelves, crates, caution stripes | Resource room, caution theme |
| Cargo Hold | Dark cargo space | `cargo #4a4f57` | Large crates, cargo nets, hazard stripes | Drone room, darker and more dangerous |
| Medbay | Cleaner medical room | `medbay #a9c2c9` | Medical beds, cross decal, sterile floor lines | Health room, contrast without state color |
| Hydroponics | Muted green life support | `hydro #6f9b6a` | Planters, water stains, recycler fan | Life support midpoint, organic but worn |
| Engineering | Maintenance and reactor prep | `engineering #a46a3a` | Tools, coolant pump, maintenance boards | Reactor preparation, industrial |
| Reactor Core | Dangerous power core | `reactor #7a2b2b` | Large reactor, heat vents, warning lines | Final power hazard, visually intense |
| Bridge | Tactical control room | `bridge #3f6b8a` | Launch computer, console screens, tactical map | Launch computer room, information hub |
| Shuttle Bay | Final launch bay | `shuttle #9aa7b3` | Large shuttle, launch stripes, fuel line | Final objective, visually open and important |

**Recipe table — design tokens** (carried from visual §16; these are the exact values the builder uses):

Palette tokens:

```json
{
  "base": {
    "void": "#07090c",
    "floor": "#171c22",
    "wall": "#2a3138",
    "line": "#4a5560",
    "panel": "rgba(10, 14, 18, 0.82)",
    "text": "#eaf2f8",
    "text_dim": "#9aa7b5"
  },
  "state": {
    "o2": "#4fd8ff",
    "integrity": "#77f2a8",
    "power": "#ffb300",
    "breach": "#ff4d4d",
    "drone": "#ff8a00",
    "coolant": "#62a4ff",
    "objective": "#ffffff"
  }
}
```

State color reservation: `o2` cyan = breathable air (player/room O2, O2 machines, airflow); `integrity` green = player survivability (bar, medkit); `power` amber = electrical (conduits, nodes, cells); `breach` red = hull failure (breach effects, hull warnings, damage feedback); `drone` orange = threat (drones, map markers, alerts); `coolant` blue = reactor coolant (cells, timer, flow); `objective` white = action/progress (marker, highlight, checklist checks). State colors appear only on machines, HUD, map icons, and effects — never on room decoration.

Icon list (drawn procedurally; no font files): `air` (three short horizontal wavy lines), `shield`, `lightning` (bolt), `cracked_hex`, `drone_triangle` (triangle + exclamation), `snowflake`, `fuel_rod` (vertical capsule, flame tip), `objective_chevron`, `warning_triangle`, `check` (rounded), `x` (rounded), `door_open`, `door_closed`, `door_jammed`, `emp`, `wrench`, `o2_tank`, `medkit`, `hull_patch`, `power_cell`, `coolant_cell`.

Shape language: rounded = resources, player, O2, usable items; angular = hazards, breaches, drones; straight lines = power, conduits, doors, airflow; white = player action, objective, progress, checklist completion.

Typography: labels uppercase sans-serif (`Inter, Roboto, "Segoe UI", system-ui, sans-serif`); numbers monospaced/tabular (`ui-monospace, "JetBrains Mono", "IBM Plex Mono", monospace`); timers never jump. HUD panels: flat, dark translucent background `rgba(10, 14, 18, 0.82)`, 1 px border `#3a4450`, no bevels, no animated sci-fi clutter, no unnecessary glow, icons left-aligned with values.

On-screen priority: 1 player critical state, 2 active warning banner, 3 interaction prompt/active channel, 4 current room status, 5 map and launch checklist, 6 time and objective, 7 event log, 8 world decoration.

**3.4 Draw order** (carried from engineering, ruled in 0.2): floor → floor decals → state overlays (airflow, power conduits, breach effects, hazard shimmer) → machines → doors → items → player → drones → particles → screen warning overlays → HUD.

**3.5 Procedural texture recipes** (carried from visual §16; base version is T1, detail is T2 item 6):

Floor (256×256, tiled): base `#171c22`; noise scale 0.02, contrast 0.08; 18 scratches, alpha 0.08, width 1 (T2); panel lines spacing 64, color `#20262d`, alpha 0.9; 6 wear stains, alpha 0.06 (T2).

Wall (256×256, tiled): base `#2a3138`; panel height 96, panel gap 4; noise scale 0.03, contrast 0.07; caution stripe probability 0.15, color `#6b6f73` (T2).

Do not generate highly detailed textures; keep the station lightweight for browser performance.

**3.6 World state feedback (state grammar).** Carried in full from visual §5 and §8; visual implies the rules it names, and gameplay already contains them — no conflict beyond those ruled in 0.2.

- **Player O2 (top-left vitals):** cyan bar, air icon, `O2 64`; below 25 the label `LOW` appears; below 10 `CRITICAL` appears and the bar pulses white/cyan. Suit backpack O2 light pulses cyan when low, faster below 10; below 10 a subtle cyan vignette pulses at screen edges; at 0 the vignette intensifies and the O2 warning sound repeats. The HUD number is authoritative; light and vignette are secondary.
- **Player Integrity (below O2):** green bar, shield icon, `INTEGRITY 82`; below 25 `LOW`; below 10 `CRITICAL` with white/green pulse. On any damage: brief red hit flash on the sprite, red vignette flash max 0.2 s, screen shake max 4 px for 0.15 s. Invulnerability: player sprite flickers white at 10 Hz for 0.5 s.
- **Room O2 (current room panel + map):** panel shows `O2 80`, `O2 45 LOW`, `O2 12 LOW`, `O2 0 LOW` with the air icon; below 30 add a warning triangle; at 0 the air icon becomes outlined with an X. Map node top-left air icon: high = filled, medium (30–59) = half-filled, low (1–29) = outlined with exclamation, zero = with X.
- **Hull and breach:** panel `HULL 30 LOW` below 30; at 0 `HULL 0 BREACH` with cracked-hexagon icon. World: low hull (below 30) shows small floor/wall cracks plus occasional tiny dust puff; breach shows a jagged dark opening, vacuum particle streaks (T2), a thin red border on the map node, and the cracked-hexagon icon. Low hull also puts a small cracked-hexagon icon on the map node.
- **Power:** panel shows exactly one of `POWER NO POWER` (gray lightning), `POWER POWERED`, `POWER EPC mm:ss`, `POWER CELL mm:ss`, `POWER REACTOR`. World: thin wall conduits; unpowered = dark gray; powered = amber glow; timed source = small amber pulse every second; reactor = stronger amber with deeper pulse; power loss = conduits fade out over 0.3 s; cell expiration = brief amber blink before fade. Power nodes show a diegetic display: `EMPTY`, `EPC mm:ss`, `CELL mm:ss`. Map top-right lightning icon: off = gray outline, on = amber filled, reactor = amber filled with small pulse.
- **Drones:** base sprite is a circular/squarish hovering body with two short mechanical arms, orange caution light, scanner ring, slight hover bob. States: Inactive = parked, gray light, no motion; Patrol = slow movement, soft hover, gray/low-orange light; Alert = orange light brightens, small orange ring or triangle above the drone, faster movement; Attack = brief orange zap effect plus short red/orange flash on player; Disabled = smoking, one arm bent or sparking, gray light, no motion. Map bottom-right orange triangle when an active drone is in that room (none when inactive or disabled). Panel shows `DRONE ACTIVE` or `DRONE --`.
- **Reactor coolant chip:** dedicated chip, snowflake icon: above 30 s `COOLANT 2:14`; at or below 30 s the value flashes; expired shows `COOLANT EXPIRED` with warning. Reactor core states: Offline = dark core, gray lights; Damaged = red blinking light, wrench prompt; Pump repaired = blue snowflake light; Coolant active = blue-white flow lines; Spin-up = core rotates with white-blue progress ring; Online = amber-red glow, strong power conduits; Coolant low = blue timer flashes, core glow flickers slightly; Coolant expired = core glow turns red, steam puffs, heat shimmer; Heat hazard = red floor pulse inside Reactor Core room, steam, warning banner. The hazard is room-specific — the whole screen never turns red.
- **Launch checklist:** appears on the right once the player has entered Bridge or Shuttle Bay, or once the reactor has been online at least once; it stays visible. Rows: `[check] REACTOR ONLINE`, `[x] SHUTTLE POWERED`, `[check] COMPUTER PRIMED`, `[x] FUEL INSTALLED`, `[x] SHUTTLE O2 42/60`, then `LAUNCH 34%`. Complete = white rounded check; incomplete = gray rounded X; failing during launch = red X flashes briefly and the event log shows the reason. If the O2 row is unmet it shows the current value `SHUTTLE O2 42/60`. Reset shows a specific line, e.g. `LAUNCH RESET — SHUTTLE O2 LOW`. Shuttle state lights: gray = not ready, white = requirements satisfied, blue-white = launch channel active, red = reset, bright white = success.
- **Objective:** top-center `DAY 3`, `TIME TO DE-ORBIT 02:14`, `OBJECTIVE: Bring Reactor Online`. Current objective room on map: white chevron. Objective complete: soft major blip plus event log entry. No subobjective text; the interaction prompt handles local direction.
- **Warnings:** banner top-center below the time panel. Examples: `WARNING: PLAYER O2 LOW 12`, `WARNING: HULL EVENT — STORAGE 0:07`, `WARNING: COOLANT LOW 0:24`, `WARNING: DE-ORBIT 1:45`, `WARNING: LAUNCH RESET — FUEL MISSING`. Rules: one type per banner, no stacking five identical; most critical first; max two banners; persistent warnings pulse slowly, max 2 Hz (T2); critical warnings use a white border with red icon, no full-screen strobing; every warning has a matching event log entry and sound.

**3.7 Station map (persistent, bottom-right).** 10 rounded-rectangle room nodes using the abbreviations from the 4.2 roster, connected by door lines. Node icon positions: top-left O2 state, top-right power state, bottom-left hull/breach, bottom-right drone state, center objective chevron. Current room: thick white outline plus slight white fill. Breach: red jagged outer border, cracked-hexagon icon, room name may get red text. Hull event warning: red target reticle over the target room with a countdown number next to it; the banner shows the same information. Door line styles: open = solid white; closed = dashed gray; jammed = crossed red line with small X. The map updates in real time; it is a survival tool, not a menu, and never a zoomable/rotatable widget.

**3.8 Machine and door visuals.** Machines are wall-mounted or floor-anchored and never block movement. General machine states: Off = gray light; Damaged = red blinking light with small crack/spark detail; Powered working = function-colored light; Repairing = progress ring with sparks; Complete = steady light, no red blink. O2 machines use cyan when working with subtle cyan output particles (T2). The Reactor is the largest machine (states in 3.6). Launch Computer: console with checklist lights — inactive gray, priming blue-white progress, primed white. Fuel Line: pipe slot — empty gray outline, installed orange/white fuel rod, complete steady white light. Launch Pad: large floor outline, shuttle silhouette, edge pad lights — gray / white / blue-white cycling (channel active) / red flash (reset) / bright white (success).

Doors are the only transitions and must be instantly distinguishable: Open = panels retracted into walls, white light line; Closed = panels filled, gray light line; Jammed = panels slightly askew, red flashing light, warning stripes; Repairing jammed = wrench sparks and progress ring; Repaired = becomes closed, red light gone. Airflow particles appear only through open doors.

**3.9 Item and door/airflow rules.** Pickups are small floor items (20–28 px) with the inventory icon shape: Wrench = gray tool, slightly larger; O2 Tank = cyan canister with air icon; Medkit = white box, green cross; Hull Patch = flat gray square with tape/plus; Power Cell = amber cylinder with lightning; EMP Charge = dark coil with white ring; Coolant Cell = blue canister with snowflake; Fuel Rod = black rod, orange flame tip. Dropped items: same icon, slight floor shadow, no despawn visual, no aggressive pulsing; the selected target shows a white outline.

Airflow particles (T2, presentation only): small cyan particles from the higher-O2 room to the lower-O2 room through open doors; none if O2 difference is below 5; count per door = `clamp(abs(A.O2 − B.O2) / 10, 1, 5)`; small, low alpha, slow; if a room is breached, particles are pulled toward the breach or through open doors to the breached room; breached rooms show stronger vacuum streaks.

Power conduits (3.6): run along walls, never cross closed or jammed doors, glow continuously through open doors, fade out on loss.

**3.10 Action feedback table** (carried in full from visual §10; audio names map to 6.3):

| Action | Visual feedback | Audio feedback |
| --- | --- | --- |
| Pick up item | Small white blip on item, item disappears to inventory | `pickup` |
| Inventory full | Red X on prompt, prompt says `INVENTORY FULL` | `ui_error` |
| Use O2 Tank | Cyan ring around player, O2 bar rises | `use_o2` |
| Use Medkit | White/green cross flash on player, integrity bar rises | `use_medkit` |
| Repair start | Wrench icon, progress ring, sparks | `repair_start` |
| Repair progress | Progress bar/ring fills; soft tick at 25/50/75% | `repair_tick` |
| Repair complete | Machine light changes, red blink stops | `repair_complete` |
| Door open | Door slides, state light changes | `door_open` |
| Door close | Door slides, state light changes | `door_close` |
| Jammed door repair | Sparks, progress ring, jammed light changes | `door_repair` |
| Hull patch | Patch plate appears, breach closes, cracks reduced | `hull_patch` |
| Power cell install | Conduits glow, node display updates | `power_install` |
| Power cell expiration | Amber blink, conduits fade | `power_cell_expire` |
| Power loss | Conduits fade, lights dim | `power_loss` |
| EMP use | Expanding white ring, drones spark and go gray | `emp` |
| Drone activation | Drone light gray to orange, event log entry | `drone_activate` |
| Drone alert | Orange ring above drone, speed increases | `drone_alert` |
| Drone attack | Orange zap, player red flash, screen shake | `drone_attack` |
| Breach | Vacuum particles, red map border | `breach` |
| Reactor coolant low | Coolant timer flashes, warning banner | `coolant_low` |
| Reactor coolant expired | Reactor glow turns red, steam | `coolant_expired` |
| Reactor spin-up | Core rotates, progress ring fills | `reactor_spinup` |
| Launch requirement met | Checklist item turns to check, small blip | `launch_requirement` |
| Launch reset | Red flash on checklist, progress bar resets | `launch_reset` |
| Launch success | White flash, shuttle engine glow, screen fade | `launch_success` |

Carried anti-goals (visual §14): no fog of war, no dynamic lighting/shadows, no parallax, no exterior space, no animated starfield, no detailed faces, no gore, no decorative state colors, no random visual flicker, no map zoom/rotation, no pause menu in core run, no cinematic cutscenes, no enemy variety beyond two drones, no alternate map states, no collectible trinkets.

Carried visual integration requirements (visual §15): the engine exposes the render views in 2.3 (`roomView`, `powerView`, plus `reactor` and `launch` state directly) so HUD updates immediately when state changes; bars may interpolate visually (T2) but numbers are exact; state icons and map update immediately; particle caps 128 per visible room / 512 total; warning pulses max 2 Hz; audio event names are exactly the 6.4 list.

---

# 4. GAMEPLAY SPEC

**The game in one paragraph.** You are the last crew member aboard a derelict orbital space station with ten compartments, dying life support, limited power, damaged hull, and two still-active maintenance drones. Your vitals — O2 and Integrity — only recover from the station's systems, so survival and restoration are the same problem: repair the O2 generator in your hub, manage airflow and power through the doors, patch scheduled hull events, bring the reactor online on a coolant clock, and finally keep five requirements true at once while you stand at the launch pad for 30 seconds. The station de-orbits in 960 real seconds (8 in-game days of 120 seconds); launch before then or fail. Every major event is scheduled, every required resource exists, drones can always be contained with doors, and the run ends cleanly — no respawn, no checkpoints.

**Core loop, minute-to-minute (carried):** 1 maintain player O2 and Integrity; 2 restore/maintain O2 in key rooms; 3 keep power available to critical machines; 4 manage doors for airflow and drone exposure; 5 move toward the next major system objective; 6 handle hull events and drones as they occur; 7 complete launch before de-orbit.
**Moment-to-moment (carried):** 1 read current room status (O2, hull, power, threat); 2 decide: stay, repair, move, close a door, or use an item; 3 execute through the interaction prompt; 4 read feedback from vitals, room status, map, and event log.
**Primary tension (carried):** airflow (open doors share O2 but drain good rooms) vs power (open doors propagate power but expose you) vs threat (drones follow open doors, so containment conflicts with progression).

## 4.2 Records and rosters

**Session and time (record).** 1 in-game day = 120 seconds. De-orbit = 960 seconds = 16:00. Target active gameplay: 16 minutes. Optional intro/debrief only.

**Room roster (10; ids are code ids, abbrs are display; coordinates in tiles; sizes are the designer's sizes):**

| Room id | Name | Abbr | x | y | w | h | Initial O2 | Initial Hull | Power node | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `docking` | Docking Bay | DB | 4 | 7 | 4 | 4 | 80 | 100 | No | Start room; safe tutorial |
| `crew` | Crew Quarters | CQ | 8 | 5 | 8 | 8 | 70 | 100 | Yes — start EPC | O2 Generator damaged; central hub |
| `storage` | Storage | ST | 10 | 0 | 6 | 5 | 20 | 30 | No | Door from crew jammed |
| `cargo` | Cargo Hold | CH | 4 | 0 | 6 | 5 | 0 | 80 | No | Drone A home |
| `medbay` | Medbay | MB | 16 | 7 | 6 | 5 | 30 | 30 | No | Medical resources |
| `hydro` | Hydroponics | HY | 9 | 13 | 6 | 6 | 10 | 50 | Yes | O2 Recycler damaged; main life-support room |
| `engineering` | Engineering | EN | 9 | 19 | 6 | 5 | 5 | 70 | No | Coolant Pump damaged |
| `reactor` | Reactor Core | RC | 10 | 24 | 5 | 5 | 0 | 100 | No | Reactor damaged/off |
| `bridge` | Bridge | BR | 15 | 19 | 6 | 5 | 10 | 80 | No | Launch Computer |
| `shuttle` | Shuttle Bay | SB | 15 | 13 | 8 | 6 | 0 | 50 | Yes | O2 Vent damaged, Fuel Line, Launch Pad |

Spatial intent (carried): Crew Quarters is the central hub; Docking Bay the safe start; Storage and Cargo Hold the resource branch; Medbay the health/resource branch; Hydroponics the life-support midpoint; Engineering and Reactor Core the power objective; Bridge and Shuttle Bay the final sequence. No secret rooms, no alternate maps, no exterior EVA, no vertical gameplay.

**Door roster (10; states as designed; axis derived by the compiler — shared side vertical = `x`, horizontal = `y`):**

| Door id | Rooms | Initial state | Axis |
| --- | --- | --- | --- |
| `door_docking_crew` | docking ↔ crew | Open | x |
| `door_crew_storage` | crew ↔ storage | Jammed | y |
| `door_crew_medbay` | crew ↔ medbay | Open | x |
| `door_crew_hydro` | crew ↔ hydro | Closed | y |
| `door_storage_cargo` | storage ↔ cargo | Closed | x |
| `door_hydro_engineering` | hydro ↔ engineering | Jammed | y |
| `door_hydro_shuttle` | hydro ↔ shuttle | Closed | x |
| `door_engineering_reactor` | engineering ↔ reactor | Closed | y |
| `door_engineering_bridge` | engineering ↔ bridge | Closed | x |
| `door_bridge_shuttle` | bridge ↔ shuttle | Closed | y |

Door gap width: `DOOR_GAP_TILES = 2`. No door is ever destroyed in normal play; no keycards, keys, or item-locked doors.

**Machine roster (8 machines + 3 power nodes):**

| Machine id | Room | Type | Time | Effect | Requires |
| --- | --- | --- | ---: | --- | --- |
| `crew_o2_generator` | crew | o2_generator | 5 s repair | +8 O2/sec when powered | Wrench |
| `hydro_o2_recycler` | hydro | o2_recycler | 6 s repair | +4 O2/sec when powered | Wrench |
| `shuttle_o2_vent` | shuttle | o2_vent | 5 s repair | +6 O2/sec when powered | Wrench |
| `reactor_coolant_pump` | engineering | coolant_pump | 5 s repair | enables coolant cell use | Wrench |
| `reactor_core` | reactor | reactor_core | 8 s repair | enables spin-up | Wrench |
| `launch_computer` | bridge | console | 15 s channel | primes launch computer (one-time) | Bridge powered |
| `fuel_line` | shuttle | fuel_install | 10 s channel | installs Fuel Rod (one-time) | Fuel Rod in inventory |
| `launch_pad` | shuttle | launch_pad | 30 s channel | final launch | all launch requirements |
| `power_node_crew` | crew | power_node | 2 s install | 400 s cell power | Power Cell, empty node |
| `power_node_hydro` | hydro | power_node | 2 s install | 400 s cell power | Power Cell, empty node |
| `power_node_shuttle` | shuttle | power_node | 2 s install | 400 s cell power | Power Cell, empty node |

No machine can become permanently broken once repaired (carried invariant). Machines are interactable but do not block movement.

**Item roster (types, effects, stack limits, world counts, placement):**

| Item | Effect | Max stack | World count | Placement |
| --- | --- | ---: | ---: | --- |
| Wrench | required for machine repairs, jammed door repair, hull patch/seal; cannot drop; occupies no slot | — | 1 | Docking Bay |
| O2 Tank | +50 player O2, instant; cannot use at 100 player O2 | 5 | 8 | Docking 2, Crew 1, Storage 1, Cargo 2, Medbay 1, Shuttle 1 |
| Medkit | +50 Integrity, instant; cannot use at 100 Integrity | 3 | 5 | Docking 1, Cargo 1, Medbay 2, Shuttle 1 |
| Hull Patch | patch hull +40 (3 s) or seal breach to 60 (4 s); consumed on completion | 4 | 6 | Docking 1, Storage 2, Hydro 1, Reactor 1, Shuttle 1 |
| Power Cell | 400 s power in an empty node; 2 s install; consumed on completion | 3 | 3 | Crew 1, Hydro 1, Shuttle 1 |
| EMP Charge | 1 s channel; disables all active drones in the current room; only usable if at least one active drone is there; consumed on completion | 3 | 3 | Storage 1, Reactor 1, Bridge 1 |
| Coolant Cell | sets reactor coolant timer to 180 s (5 s use); not additive; consumed on completion | 2 | 2 | Engineering 1, Reactor 1 |
| Fuel Rod | installs shuttle fuel (10 s); consumed on completion | 1 | 1 | Engineering 1 |

Total pickups in the world: 29 (8 + 5 + 6 + 3 + 3 + 2 + 1 + 1 wrench).

**Drone roster (2):**

| Drone | Home | Activation | Waypoints (deterministic) | Patrol speed |
| --- | --- | --- | --- | ---: |
| `A` | cargo | player first enters cargo | room center; top-left inset; bottom-right inset | 2.5 tiles/sec |
| `B` | shuttle | player first enters shuttle | room center; top-left inset; bottom-right inset | 2.5 tiles/sec |

No other enemies exist.

**Hull event roster (3; fixed, not random; 10 s warning before damage):**

| Event | Warning at | Damage at | Target selection (first valid candidate) |
| --- | ---: | ---: | --- |
| 1 | 230 s | 240 s | Storage −30 → Cargo Hold −30 → Crew Quarters −20 |
| 2 | 470 s | 480 s | two independent damages: Medbay −30 and Hydroponics −30; each fallback (in order, −30): Crew Quarters, Shuttle Bay, Storage, Engineering, Bridge; the two damages never hit the same room |
| 3 | 710 s | 720 s | Shuttle Bay −50 → Crew Quarters −20 → Hydroponics −20 |

Event rules (carried): never target the room the player is currently in; never target an already-breached room; if no valid target, skip; damage cannot raise hull; damage can cause a breach. Design intent: Storage (30), Medbay (30), Shuttle Bay (50) all breach on their event unless patched — so collecting and using Hull Patches early is the preventable path.

**Objective roster (9, exact order):**

| # | Objective | Completes when |
| --- | --- | --- |
| 1 | Repair Crew O2 Generator | `crew_o2_generator` repaired |
| 2 | Stabilize Crew Atmosphere | Crew Quarters O2 ≥ 60 continuously for 5 s |
| 3 | Reach Hydroponics | player first enters hydro |
| 4 | Restore Hydroponics O2 Recycler | `hydro_o2_recycler` repaired |
| 5 | Bring Reactor Online | reactor online |
| 6 | Prime Launch Computer | launch computer channel complete |
| 7 | Install Shuttle Fuel | fuel line channel complete |
| 8 | Pressurize Shuttle | Shuttle Bay O2 ≥ 60 at least once |
| 9 | Launch Shuttle | launch pad channel complete |

## 4.3 Movement — Tier: T1

- Player speed: **3.5 tiles/sec** (drone alert speed 3.0, so the player can outrun but not feel untouchable).
- The player is a point. Each tick: normalize input vector; multiply by `3.5 × DT`; try x and y separately; apply an axis only if the proposed point is walkable (sliding along walls).
- A point is walkable if inside any room interior rectangle or any **open** door gap rectangle. Closed and jammed doors are not walkable. Door gap rectangles: for `axis = x`, `{x: wallX − 0.25, y: doorY − 1, w: 0.5, h: 2}`; for `axis = y`, `{x: doorX − 1, y: wallY − 0.25, w: 2, h: 0.5}` (gap 2 tiles, bridging both interiors).
- Room assignment: `player.room` is the room interior containing the point. If the point is inside a door gap but not yet inside a new room interior, keep the previous room; change room only when the point enters the new room interior (prevents flicker in O2, power, drone room, and HUD).
- Interaction ranges: pick up items within **1.0 tile**; machines within **1.5 tiles**; doors within **1.5 tiles** of the door center, or within **2.0 tiles** while in one of the two adjacent rooms.
- Drones use the same walkable check and can pass only through open doors. If a door closes while a drone is moving, the drone stops and re-paths next tick. No tile-level obstacle avoidance (room interiors have no gameplay-critical obstacles).

## 4.4 Player Vitals — Tier: T1

Stats: O2 max 100, Integrity max 100. No water, food, temperature, or stamina system.

Player O2 change from the current room's O2 (after the atmosphere step), per second:

| Current room O2 | Player O2 change |
| ---: | ---: |
| 60 or higher | +0.5/sec |
| 30 to below 60 | −0.5/sec |
| 1 to below 30 | −1.5/sec |
| below 1 | −3/sec |

(Ruling 0.2: the lowest bucket is "below 1", carried from engineering 30.3.) If player O2 reaches 0: Integrity drains **5/sec** (asphyxia), `lastDamageSource = 'asphyxia'`. Player O2 clamps 0–100.

Integrity is damaged by: drone attacks **20** (discrete, 4.11); reactor heat **5/sec** (4.10); asphyxia **5/sec**. Restored by: Medkit **+50**. If Integrity reaches 0, the player dies (failure cause from `lastDamageSource`, or `integrity_failure` if null).

- O2 Tank: **+50 player O2**, instant, cannot be used at 100 player O2.
- Medkit: **+50 Integrity**, instant, cannot be used at 100 Integrity.
- Damage invulnerability: after taking drone damage, **0.5 s** invulnerability; it blocks **drone attacks only** (not asphyxia or reactor heat) — carried ruling (0.2 wrench-scope row family; engineering 11.4).

## 4.5 Doors — Tier: T1

States and behavior (carried):

| State | Movement | Airflow | Power | Drones |
| --- | --- | --- | --- | --- |
| Open | allowed | allowed | allowed | allowed |
| Closed | blocked | blocked | blocked | blocked |
| Jammed | blocked (must be repaired) | blocked | blocked | blocked |

Channels: open a closed door **1 s** (no requirements); close an open door **1 s**; repair a jammed door **5 s**, requires Wrench. A jammed door cannot be opened or closed until repaired; a repaired jammed door becomes a normal **closed** door. Progress is retained if paused. A completed door action affects power, airflow, and drones in the same tick.

## 4.7 Atmosphere — Tier: T1

Room O2 is 0–100, the main environmental survival pressure.

- Baseline: every room with no breach loses O2 at **0.5/sec**. A breached room's baseline is replaced by a breach drain of **15/sec**.
- O2 machines generate only if **repaired** and **their room is powered**. Rates: Crew O2 Generator **+8/sec**, Hydroponics O2 Recycler **+4/sec**, Shuttle O2 Vent **+6/sec**. A room may be breached and still powered: generation continues but the 15/sec drain usually overwhelms it. Generation caps room O2 at 100.
- Airflow, per open door between rooms A and B, per second: `transferRate = 5 × abs(A.O2 − B.O2) / 100`; `transfer = transferRate × DT`, moved from the higher-O2 room to the lower-O2 room. Closed and jammed doors transfer zero. A breached room open to another room acts as an O2 sink. All transfers are computed from **start-of-phase** O2 values and applied **simultaneously**, then all room O2 clamps to 0–100 (ruling 0.2: simultaneous).
- Why it matters (carried): open doors share power and movement but mix O2; closed doors preserve O2 but block power and can strand machines. This is the central spatial puzzle.

## 4.8 Power — Tier: T1

Power is binary per room and propagates only through **open doors**.

Sources:

| Source | Location | Duration | Notes |
| --- | --- | ---: | --- |
| Start Emergency Power Cell | crew | 400 s | installed at game start, occupies the crew node |
| Player Power Cell | any empty node | 400 s | 3 exist in the world |
| Reactor | reactor | infinite while coolant active and spin-up complete | 4.10 |

Power nodes exist only in `crew`, `hydro`, `shuttle`. Rules: a node holds one source at a time; when the start EPC expires, the crew node becomes empty; a Power Cell installs only into a node with **no local source** (propagated power does not block installation — ruling 0.2); installation takes **2 s** and requires a Power Cell in inventory; the cell is consumed only on completion.

Propagation, every tick: 1 mark all rooms unpowered; 2 seed rooms with active timed sources; 3 if the reactor is online, seed the reactor room; 4 BFS through open doors — for each powered room, mark neighbors behind open doors powered; repeat until stable. Then update `room.powered` and compute the display:

| Condition | Display |
| --- | --- |
| Local EPC active | `EPC mm:ss` |
| Local Power Cell active | `CELL mm:ss` |
| Reactor room, reactor online | `REACTOR` |
| Powered, no local source | `POWERED` |
| Not powered | `NO POWER` |

Power failure: if a source expires or the reactor shuts down, every room that loses its only power path becomes unpowered; machines there stop; if any room loses power, emit `power_loss` (audible alert required); cell expiration emits `power_cell_expire`.

## 4.9 Hull and Breach — Tier: T1

Room hull is 0–100. **Breach condition: hull ≤ 0.** Breach effects: room O2 drains at **15/sec**; the room is dangerous to remain in; the map shows the room breached (red border, cracked hexagon); the event log records `Hull breach in ROOM`; audio `breach` plays on the transition into breach.

Hull repair (requires Hull Patch in inventory **and** Wrench):

| Situation | Action | Time | Effect |
| --- | --- | ---: | --- |
| Hull > 0, not at 100 | Patch hull | 3 s | hull + 40, max 100 |
| Breached | Seal breach | 4 s | hull set to 60, breach cleared, `stats.breachesSealed += 1` |

The Hull Patch is consumed only when the channel completes; interrupting does not consume it. A room at hull 100 with no breach cannot be patched.

Scheduled events: the three in the 4.2 roster, fixed by timer, each with a **10 s warning** (230/240, 470/480, 710/720). During the warning window the target is **recalculated every tick** (ruling 0.2) using the candidate chain, honoring "never the current player room" and "not already breached"; the HUD banner and map reticle show the current target with its countdown; `hull_event_warning` audio plays once when the warning first appears. At damage time the currently-selected target takes the damage: `hull = max(0, hull − damage)`; a resulting breach emits `breach`. If all valid targets are breached, the event is skipped.

## 4.10 Reactor — Tier: T1

Machines: Reactor Coolant Pump (engineering, 5 s repair, wrench) enables coolant use; Reactor Core (reactor, 8 s repair, wrench) enables spin-up.

To bring the reactor online (all required): 1 repair the coolant pump; 2 use a Coolant Cell on the pump (5 s channel, Coolant Cell in inventory, consumed on completion — sets `coolantTime = 180`, not additive; emits `reactor_coolant_applied`); 3 repair the core; 4 complete the spin-up channel (**20 s**, requires core repaired, coolant active, player within 1.5 tiles of the core, holding E; progress in seconds is retained while paused).

Coolant: duration **180 s** per cell; while active, `coolantTime` decrements every tick; HUD displays it clearly; warning `coolant_low` (audible) below **30 s**; a new cell while active or expired sets the timer back to 180.

- **Online:** `online = coolantActive and spinUpComplete`. While online: infinite power to the reactor room, propagating through open doors; no heat hazard.
- **Shutdown:** at `coolantTime = 0`: `coolantActive = false`; if `spinUpComplete`, `online = false` and **heat hazard** activates (emit `coolant_expired`); if the reactor never spun up, no heat hazard.
- **Spin-up abort:** if coolant expires during the 20 s spin-up: `spinUpProgress = 0`, `spinUpComplete = false`, log "Reactor spin-up aborted", event `reactor_spinup_aborted` (audio `ui_error` — ruling 0.2).
- **Heat hazard:** active only when `spinUpComplete and not coolantActive`. While the player is in the reactor room, Integrity drains **5/sec** (`lastDamageSource = 'reactor'`); leaving the room or applying a coolant cell ends it.

## 4.11 Drones — Tier: T1

Exactly two drones (A in cargo, B in shuttle; 4.2). States:

- **Inactive:** no movement, no attack. Activates only when the player's room first becomes its home room: `active = true`, state → patrol, emit `drone_activate` (robotic chirp; the drone light goes gray to orange).
- **Patrol:** speed **2.5 tiles/sec**; moves between the three deterministic waypoints (room center, top-left inset, bottom-right inset); arrival within **0.5 tile** selects the next. If the player is in the same room: begin the **1-second alert delay** (drone lingers, still patrolling, counting `alertDelay`); after 1 s, enter alert and emit `drone_alert`.
- **Alert:** speed **3.0 tiles/sec**. If the player is in the same room, move directly toward the player. If in a different room, compute the shortest room-graph path through **open doors** (BFS) and move toward the next door on the path. Re-path when the drone room, player room, or any door state changes. If no path exists, run `noPathTimer`; after **3 s** return to patrol (the timer resets while a path exists). A drone whose path to its target is walled off waits in place — a door closed behind it stays closed, and a contained drone is harmless to the other side (this containment is a legal strategy, not a bug).
- **Attack:** if the drone is within **1.0 tile** of the player and its cooldown is 0: attempt attack. If the player is invulnerable: no damage, no cooldown (retry immediately after i-frames). Otherwise: **20 Integrity damage**, player invulnerability **0.5 s**, drone `attackCooldown = 1.0 s`, state set to `attack` for one tick (visual), emit `drone_attack`.
- **Disabled:** permanent; no movement, no attack, no reactivation; `stats.dronesDisabled += 1`.

Pathfinding is room-graph only (no tile pathfinding); drones cannot softlock the player: no path → wait → patrol.

**EMP Charge:** 1 s channel (F held), usable only if at least one **active** drone is in the player's current room at start; if the condition fails during the 1 s, the channel cancels and the charge is not consumed; on completion all active drones in the current room are disabled and the charge is consumed (emit `emp`).

**Avoidance without EMP (fairness, carried):** the player can always avoid drones: close doors behind them; lure a drone into another room and close the door; use geometry and patrol behavior; use room O2/state to decide when to engage. The canonical no-EMP line for Drone B: enter Shuttle Bay, lure B toward the Bridge, enter Bridge, close Bridge–Shuttle (1 s) — B has no path and waits/patrols harmlessly in the Bridge — then keep Hydro–Shuttle open for power and O2 and launch. **The launch must be possible with zero EMP charges.**

## 4.12 Launch — Tier: T1

Success requires all five simultaneously:

| Requirement | Condition |
| --- | --- |
| Reactor online | coolant active and spin-up complete |
| Shuttle powered | shuttle room powered |
| Launch computer primed | Bridge channel complete (one-time) |
| Fuel installed | Fuel Line channel complete using Fuel Rod (one-time) |
| Shuttle O2 sufficient | shuttle room O2 ≥ 60 |

Machines: Launch Computer (bridge, **15 s**, requires Bridge powered, progress retained if interrupted, stays complete); Shuttle O2 Vent (shuttle, **5 s** repair, +6 O2/sec when powered); Fuel Line (shuttle, **10 s**, Fuel Rod consumed on completion, stays complete); Launch Pad (shuttle, **30 s**).

Launch Pad channel: player in the shuttle, within **1.5 tiles** of the pad (ruling 0.2), holding E, all requirements true, and no damage this tick → progress (percent) advances. At 100: `launch.success = true`, emit `launch_success`, end state success **immediately**.

Reset (progress > 0 and any of): player leaves pad range; player takes damage; reactor offline; shuttle unpowered; computer not primed; fuel missing; shuttle O2 below 60 → progress resets to 0, `lastResetReason` set (priority order: 1 `PLAYER DAMAGED`, 2 `LEFT PAD`, 3 `REACTOR OFFLINE`, 4 `SHUTTLE UNPOWERED`, 5 `COMPUTER NOT PRIMED`, 6 `FUEL MISSING`, 7 `SHUTTLE O2 LOW`), `stats.launchResets += 1`, emit `launch_reset`. Paused vs reset (ruling 0.2): releasing E at the pad **pauses** (no reset); leaving the pad **resets**.

Shuttle O2 strategy (carried): reach 60 faster by repairing/powering the vent or by opening a door to a high-O2 room (usually Hydroponics). If the Shuttle Bay is breached, the vent cannot raise O2 to 60 until the breach is repaired — this makes the final hull event meaningful.

## 4.13 Objectives, Warnings, and Event Log — Tier: T1

**Objectives.** The sequence is the 9-item roster (4.2); completion rules as rostered. Objectives advance only forward and never un-complete; "Pressurize Shuttle" completes once shuttle O2 reaches 60 even if it later drops. The HUD shows the next incomplete objective; when all are complete it shows `OBJECTIVE: SHUTTLE LAUNCHED`.

**Launch checklist visibility:** becomes visible when the player enters Bridge or Shuttle Bay, or the reactor has been online at least once; once visible it stays visible.

**Warning types and thresholds (carried):**

| Warning | Trigger |
| --- | --- |
| `player_o2_low` | player O2 below 25 |
| `player_o2_critical` | player O2 below 10 |
| `integrity_low` | integrity below 25 |
| `integrity_critical` | integrity below 10 |
| `room_o2_low` | current room O2 below 30 |
| `room_breach` | current room breached |
| `power_source_low` | a local timed source below 60 s |
| `coolant_low` | coolant active and below 30 s |
| `coolant_expired` | coolant just expired |
| `hull_event_warning` | scheduled event warning active (10 s window) |
| `deorbit_warning` | time to de-orbit below 120 s |
| `launch_reset` | launch progress just reset |

**Priority (12-item list, ruling 0.2):** 1 `player_o2_critical`, 2 `integrity_critical`, 3 `launch_reset`, 4 `room_breach`, 5 `coolant_expired`, 6 `coolant_low`, 7 `hull_event_warning`, 8 `power_source_low`, 9 `deorbit_warning`, 10 `player_o2_low`, 11 `integrity_low`, 12 `room_o2_low`. Max **two** banners shown, most critical first; each warning has a matching log entry and sound; audio plays only on the false→true transition (loops start/stop on transition, 6.3).

**Event log.** The state stores the full log; the HUD displays the **last 5**, newest on top, older entries dimmed. Entries: `{id, time, type, text, audio, critical}`. Important events are logged; minor movement is not. Carried examples: `O2 Generator repaired`, `Power cell installed in Hydroponics`, `Power lost in Crew Quarters`, `Hull breach in Storage`, `Reactor coolant 0:30`, `Drone active in Shuttle Bay`, `Launch requirement met: Fuel installed`.

## 4.14 End States — Tier: T1

**Success:** `launch.success` true. Same-tick precedence: **success beats death, death beats de-orbit** (evaluated in that order at the tick boundary); a launch completing exactly at 960 s wins over de-orbit. End: `{status: 'success', cause: null, timeSurvived: time, stats}`.
**Failure:** integrity ≤ 0 (cause: `asphyxia` | `drone_attack` | `reactor_heat` | `integrity_failure`), or time ≥ 960 without launch (cause `deorbit`). No respawn, no checkpoint, no mid-run retry. Restart starts a fresh initial state (7.5).

**Edge cases and invariants (carried in full from gameplay §19):**
- Player dies → game ends immediately, cause shown (asphyxia / drone attack / reactor heat / integrity failure).
- Launch completes → success; precedence as above.
- De-orbit at 960 → failure unless launch complete on or before that tick.
- No O2 and no O2 Tanks → survivable while room O2 ≥ 60; otherwise player O2 depletes, then Integrity.
- No Medkits → win by avoiding damage (doors, coolant management).
- No Hull Patches → survive by keeping breached doors closed, avoiding breached rooms, short O2-Tank visits; failing while operating in a breached room too long is legitimate.
- No Power Cells → win by reaching the reactor in time; otherwise may fail from O2 loss.
- No EMP Charges → win by avoiding/luring; launch is possible without EMPs.
- Coolant used too early → may run out before launch; player error, and the HUD timer makes it avoidable.
- All doors closed → power stops propagating, O2 preserved; doors reopen manually; no softlock.
- Too many doors open → good rooms drain O2 into bad ones; close doors to recover.
- Reactor coolant expires during launch → channel resets; second coolant recovers if available.
- Shuttle breached during launch → O2 cannot reach 60 until sealed.
- Drone stuck (no path) → returns to patrol; drones cannot softlock the player.
- Required item dropped → dropped items persist and can be retrieved (if the player can survive the trip).
- Item forgotten outside a closed door → doors reopen; no item despawn.
- Machine repair interrupted → progress retained; consumables not consumed until success.
- Launch channel interrupted → progress resets; installed fuel stays installed; launch can be retried.

Carried fairness principles: all major events scheduled, not random; all required resources exist in the world; drones always avoidable by closing doors; all three major breaches preventable with enough patches; launch possible without EMPs; the reactor is maintainable through a normal run with two coolant cells; every operable door can always be opened manually; the wrench cannot be lost.

## 4.15 Progression and Difficulty — Tier: T1

The player may explore in any order; the HUD guides the required path. Expected pacing (carried):

| Time | Expected player state |
| ---: | --- |
| 0–60 s | Tutorial in Docking Bay/Crew Quarters; repair O2 Generator |
| 60–180 s | Explore Crew, Storage, Cargo, Medbay; collect O2 and patches |
| 180–300 s | Reach Hydroponics; repair O2 Recycler; manage power |
| 300–480 s | Reach Engineering; repair coolant pump; use coolant; spin up reactor |
| 480–600 s | Prime launch computer; install fuel; repair shuttle O2 vent |
| 600–720 s | Use second coolant; handle shuttle hull event; manage drone |
| 720–900 s | Final launch sequence; maintain requirements |
| 960 s | De-orbit failure if launch not complete |

The player should be able to launch comfortably before 960 s by following the main path. Difficulty comes from competing pressures, not randomness: hard timers (cells 400 s, coolant 180 s), scheduled damage (240/480/720 s), drone containment vs door openness, and a five-requirement final channel.

## 4.16 Items and Inventory — Tier: T1

- **6 slots.** The Wrench is equipped, occupies no slot, and cannot be dropped, deleted, or lost. Stackable items use one slot and show a count (stack limits in the 4.2 item roster).
- **Pickup:** on E press, nearest item within 1.0 tile. If the inventory can accept it (existing stack below max, or an empty slot), take it and emit `pickup`. If full: no pickup, `ui_error`, prompt shows `INVENTORY FULL`. Picking up the wrench sets `hasWrench = true` (no slot used).
- **Drop:** Q drops one item from the selected slot to the player position (wrench never droppable). Dropped items persist forever, do not despawn, do not move, and can be picked up again — this prevents softlocks from inventory mistakes.
- **Use:** F press instant (O2 Tank +50, not at 100; Medkit +50, not at 100); F hold 1 s for EMP (4.11); other items via E-hold channels at their targets (patch, install, coolant, fuel). Invalid use emits `ui_error`.
- **Inventory full rule:** the player cannot pick up another item but can drop or use.

## 4.17 Channels and Machines — Tier: T1

A channel is a timed action: repairs, door open/close/repair, hull patch/seal, power cell install, coolant cell use, reactor spin-up, launch computer, fuel line, launch pad, EMP. Channel progress lives in `state.channels` as `{[channelId]: {progress (seconds), duration}}` with stable ids (e.g. `door_crew_storage:repair`, `machine:crew_o2_generator:repair`, `hull:storage`, `power_node:hydro:install`, `reactor:spinup`, `launch:computer`, `launch:pad`, `item:emp`).

Rules: progress is retained when paused; it advances only while the player is in range, holding the right key, and meeting requirements; **consumable items are consumed only on completion** — if the required item is missing from inventory, the channel pauses (no item locking; if the player drops or uses it, the channel simply cannot complete); wrench-required channels are invalid without `hasWrench` (prompt shows `REQUIRES WRENCH`); the only channel that resets on interruption is the launch pad (4.12); machine repairs are one-time — a repaired machine stays repaired for the rest of the run.

Wrench scope (ruling 0.2): required for machine repairs, jammed door repair, hull patch/seal. Not required for: door open/close, power cell install, coolant cell use, fuel line, launch computer, reactor spin-up.

Machine behavior notes (carried content design): Crew O2 Generator is the first objective; Hydroponics O2 Recycler is the midpoint; Engineering is a short, dangerous objective room (O2 starts at 5, no O2 machine); the Reactor Core room is the final major system but not the final objective; the Bridge is a short objective room; the Shuttle Bay converges O2, fuel, power, drone, and hull into the final objective.

## 4.18 Cut List (carried from gameplay §20)

No water/thirst, no food/hunger, no temperature system, no gravity changes, no exterior EVA, no radiation, no crafting, no upgrades, no multiplayer, no random enemy spawning, no enemy variety beyond two drones, no keycard progression, no destructible doors, no destructible machines, no save mid-run, no respawn, no multiple shuttles, no alternate endings. Logic (carried): each cut system would add UI, balance, and integration cost without strengthening the core loop of O2, power, hull, threats, and launch timing.

---

# 5. CHARACTERS

**Player silhouette (carried from visual §8.1).** A top-down astronaut: white/light-gray suit, dark visor, small backpack with an O2 light, no detailed face, no portrait. The white suit gives contrast against dark floors. Facing: the visor marks the facing direction — always the last non-zero movement direction (`player.facing`), so it persists when stopped.

Player animations, by name (state → motion rule):
- `idle` — steady suit light, subtle breathing bob.
- `move` — footstep cycle; tiny boot/dust particles (T2), very subtle.
- `low_o2` — backpack O2 light pulses cyan (below 25).
- `critical_o2` — rapid cyan/white backpack pulse (below 10).
- `damage` — red flash on the sprite; red vignette flash max 0.2 s; screen shake max 4 px, 0.15 s.
- `invulnerable` — white flicker at **10 Hz** for **0.5 s** (matches 4.4).
- `death` — suit light turns gray; screen desaturates.

**Drone silhouette (carried from visual §8.2).** Maintenance bot, not horror enemy: circular or compact square hover body, two short mechanical arms, orange caution light, small scanner element, slight hover bob, no face. Facing: sprite rotates toward its velocity vector; when stationary it keeps the last facing.

Drone animations, by name (the five states 4.11 requires, motion rules):
- `inactive` — parked, gray light, no motion.
- `patrol` — slow movement (2.5 tiles/sec) between waypoints, soft hover bob, gray/low-orange light.
- `alert` — orange light brightens, small orange ring or triangle appears above the drone, movement speed increases to 3.0 tiles/sec.
- `attack` — brief orange zap effect (one tick), short red/orange flash on the player.
- `disabled` — smoking, one arm bent or sparking, gray light, no motion; never reactivates.

Drones must read as machines still doing maintenance; the orange triangle plus the word `DRONE` carry the threat, not sprite detail.

---

# 6. AUDIO

Carried architecture (engineering §24, ruled in 0.2): **all audio is generated with the Web Audio API at runtime — no asset files.** `AudioManager` (SFX) and `MusicManager` (music) are created only after the user's start-gesture on the title screen (autoplay policy). `play(name, {pan})` with pan clamped −1..1 (pan is T2); missing recipe → console warning, no crash. The simulation emits event names (2.3); audio consumes them and never alters gameplay.

## 6.2 Music — Tier: T2

Identity (carried): a failing station — sparse, mechanical, industrial, tense but controlled; not orchestral, not cinematic hero music, not constant panic. Key **D minor**; base tempo **72 BPM**; final phase **90 BPM**. State-driven layers, **0.5 s** gain crossfades; music always sits below SFX; warnings always audible above music; stingers short; reactor/final layers build rather than panic; success feels like escape, not celebration noise.

| Layer | Recipe (Web Audio synthesis) | Trigger | Mix note |
| --- | --- | --- | --- |
| `base` | D2 sine 73.4 Hz (g 0.05) + D3 sawtooth 146.8 Hz through lowpass 400 Hz (g 0.03); low pulse: sine 36.7 Hz, 100 ms, A 2 ms / R 80 ms, every 0.833 s (72 BPM), g 0.06; faint bandpass noise (800 Hz) loop at g 0.01 | Always during gameplay | −18 to −22 LUFS equivalent |
| `low_o2` | Bandpass noise (1–2 kHz), 600 ms cycle, gain LFO 1 Hz; added to base | Player O2 below 25 | duck base 20% |
| `critical_o2` | Bandpass noise (2–4 kHz), 500 ms cycle, gain LFO 2 Hz; replaces `low_o2` | Player O2 below 10 | keep below SFX warnings |
| `power_loss` | Remove the low pulse; sparse dissonant pad: D2 73.4 + F2 87.3 sines, 2 s decay each cycle, g 0.04 | Major power loss (event `power_loss`) | subtle, not alarm |
| `reactor` | Deep sub drone: sine 55 Hz (g 0.07) + 82.4 Hz (g 0.04), slow 0.1 Hz amplitude LFO; 72 BPM pulse resumes | Reactor online | add depth, not excitement |
| `coolant_low` | Tick texture: sine 1000 Hz, 80 ms, 4 per bar, with 8-bar rising filter cutoff 300→2000 Hz | Coolant below 30 s | do not overpower the `coolant_low` SFX |
| `final_countdown` | Base at **90 BPM** (0.667 s pulse); rising pad adds A2 110 Hz and C3 130.8 sines each +3 dB per 16 bars, capped | Time to de-orbit below 120 s | urgent but controlled |
| `success` (theme) | D-major chord: sines 293.7 / 349.2 / 440 / 587.3 Hz, 4 s, A 0.5 / R 2.5, g 0.12; soft engine rumble (lowpass 250 Hz noise) under it | Launch success | replaces everything; quiet resolve |
| `failure` (theme) | Detuned drone: sines 110 + 116 Hz, 4 s fade; three fading square alarm pulses 440/330 Hz, 200 ms each, 600 ms apart, gains 0.10/0.07/0.04 | Failure | replaces everything; melancholic, not punitive |

The drone-alert stinger is the `drone_alert` SFX (6.3) — no separate music asset.

## 6.3 SFX — Tier: T1

Recipe notation: `waveform f Hz (sweep to f2 over t), duration, envelope A/D/S/R, gain g, [LFO rate on gain], [filter]`. One-shot unless marked LOOP.

| Name | Recipe | The rule that plays it |
| --- | --- | --- |
| `ui_select` | sine 1200 Hz, 40 ms, A 2 / R 30, g 0.2 | Slot selection (1–6) or button press |
| `ui_error` | square 200 Hz, 80 ms, hard stop, g 0.25 | Invalid action: full inventory, invalid item use, `reactor_spinup_aborted` |
| `pickup` | sine sweep 700→1000 Hz, 60 ms, A 2 / R 20, g 0.3 | Item picked up |
| `drop` | sine 180 Hz, 100 ms, A 1 / R 60, lowpass 400 Hz, g 0.3 | Item dropped |
| `use_o2` | bandpass noise (2–4 kHz) 0.35 s, g 0.15, plus sine 880 Hz 80 ms A 2 / R 40 g 0.2 | O2 Tank used |
| `use_medkit` | sine 1400 Hz, 60 ms, A 2 / R 40, g 0.25 | Medkit used |
| `repair_start` | square 320 Hz 30 ms + 10 ms noise click, g 0.2 | Channel starts (any repair/channel) |
| `repair_tick` | sine 1000 Hz, 25 ms, g 0.15 | Channel hits 25 / 50 / 75% |
| `repair_complete` | triangle 260 Hz 80 ms (thud) + sine 1200 Hz 50 ms blip, g 0.3 | Repair completes; also coolant application (`reactor_coolant_applied`, ruling 0.2) |
| `door_open` | sawtooth sweep 120→300 Hz, 300 ms, g 0.25, + sine 90 Hz 60 ms thud at end | Door opens |
| `door_close` | sawtooth sweep 300→120 Hz, 300 ms, g 0.25, + thud | Door closes |
| `door_jammed` | square 90 Hz, 120 ms × 2, gain LFO 8 Hz (rattle), lowpass 500 Hz, g 0.25 | Interaction with a jammed door before repair |
| `door_repair` | triangle 200 Hz 100 ms clank + sawtooth 150→250 Hz 200 ms servo, g 0.3 | Jammed door repaired |
| `hull_patch` | bandpass noise (1–3 kHz, descending) 0.5 s g 0.2 + clank (triangle 200 Hz 100 ms) at 0.4 s | Hull patch or breach seal completes |
| `power_install` | sine sweep 100→400 Hz 400 ms, g 0.25, then 400 Hz steady 50 ms | Power cell installed |
| `power_cell_expire` | sawtooth 400→80 Hz, 500 ms, g 0.25, + 100 Hz click at end | A timed source expires |
| `power_loss` | square 60 Hz 400 ms g 0.3 + lowpass (200 Hz) noise burst 100 ms | Any room loses power |
| `breach` | sawtooth 1200→300 Hz 0.4 s (shriek) + bandpass (2–5 kHz) noise whoosh 0.6 s g 0.3 + sine 55 Hz rumble 0.8 s g 0.3 | Room becomes breached |
| `hull_event_warning` | square 440 Hz 150 ms + square 330 Hz 150 ms (300 ms total), g 0.3 | Hull event warning first appears |
| `deorbit_warning` | sine 392 Hz 200 ms + sine 330 Hz 200 ms (400 ms total), g 0.35 | Time to de-orbit enters below 120 s |
| `drone_activate` | square chirps 880 / 1100 / 1320 Hz, 60 ms each, 40 ms gaps + 100 ms servo noise, g 0.25 | Drone first activates |
| `drone_alert` | square 990 Hz, 80 ms × 2, 40 ms gap, g 0.25 | Drone enters alert state |
| `drone_attack` | highpass (2 kHz) noise crackle 80 ms, gain LFO 30 Hz, + square 150 Hz 40 ms, g 0.4 | Drone deals 20 damage |
| `emp` | sine sweep 200→2000 Hz 300 ms g 0.3 + 50 ms noise zap | EMP channel completes |
| `coolant_low` (LOOP) | sine 1400 Hz, 500 ms cycle, gain LFO 1 Hz (A 100 / R 100 ms per cycle), g 0.15 | Warning `coolant_low` active (below 30 s); stop on exit |
| `coolant_expired` | sine 60 Hz thud 300 ms + square 660 Hz alarm 200 ms, g 0.4 | Coolant reaches 0 |
| `reactor_spinup` | sawtooth 60→180 Hz sweep over 2 s, lowpass 800 Hz, g 0.3 | Spin-up channel starts |
| `reactor_online` | sine 55 Hz thud 200 ms + fifth 165 Hz 400 ms decay, g 0.4 | Reactor comes online |
| `reactor_heat` (LOOP) | bandpass noise (800–1500 Hz), 400 ms cycle, gain LFO 0.8 Hz, g 0.12 | Heat hazard active; stop when hazard ends |
| `o2_low` (LOOP) | bandpass noise (3–5 kHz), 600 ms cycle, gain LFO 1 Hz, g 0.12 | Player O2 below 25; stop on exit |
| `o2_critical` (LOOP) | bandpass noise (3–5 kHz), 500 ms cycle, gain LFO 2 Hz, g 0.18 | Player O2 below 10; stop on exit |
| `integrity_low` (LOOP) | sine 70 Hz thump, 500 ms cycle, gain LFO 1 Hz, lowpass 300 Hz, g 0.2 | Integrity below 25; stop on exit |
| `integrity_critical` (LOOP) | sine 70 Hz thump, 250 ms cycle, gain LFO 2 Hz, lowpass 300 Hz, g 0.25 | Integrity below 10; stop on exit |
| `objective_complete` | sine 880→1320 Hz, 100 ms, g 0.2 | Main objective completes |
| `launch_requirement` | sine 1000 Hz 60 ms + sine 1200 Hz 60 ms, g 0.2 | A launch checklist row becomes true |
| `launch_reset` | sine 600→200 Hz, 300 ms, g 0.3 | Launch progress resets (with the specific reason) |
| `launch_tick` | sine 900 Hz, 20 ms, g 0.08 | Launch channel hits every 10% |
| `launch_success` | lowpass (300 Hz) noise rumble 2 s g 0.25 + major chord sines 261.6 / 329.6 / 392 / 523.3 Hz, 1.5 s, A 0.2 / R 1.0, g 0.3 | Launch channel reaches 100% |
| `game_over` | sines 110 + 116 Hz (detuned drone) 3 s fade g 0.25 + three fading square alarm pulses 440/330 Hz 200 ms, 600 ms apart, g 0.15/0.10/0.05 | Failure occurs |

Loop management (carried from engineering 24.4): loops start when their warning enters active and stop when it exits; if `o2_critical` activates, stop `o2_low`; if `integrity_critical` activates, stop `integrity_low`. One-shot list: `breach`, `power_loss`, `power_cell_expire`, `hull_event_warning`, `deorbit_warning`, `launch_reset`, `drone_activate`, `drone_alert`, `drone_attack`, `coolant_expired`, `reactor_online`, `game_over`, `launch_success` (plus the action one-shots above). Warning audio fires on transition only, never per tick.

## 6.4 Event names (the contract)

Simulation event → audio mapping is complete in `src/data/audioEvents.js`; the audio names are exactly the 6.3 roster: `ui_select`, `ui_error`, `pickup`, `drop`, `use_o2`, `use_medkit`, `repair_start`, `repair_tick`, `repair_complete`, `door_open`, `door_close`, `door_jammed`, `door_repair`, `hull_patch`, `power_install`, `power_cell_expire`, `power_loss`, `breach`, `hull_event_warning`, `coolant_low`, `coolant_expired`, `drone_activate`, `drone_alert`, `drone_attack`, `emp`, `o2_low`, `o2_critical`, `integrity_low`, `integrity_critical`, `reactor_spinup`, `reactor_online`, `reactor_heat`, `deorbit_warning`, `objective_complete`, `launch_requirement`, `launch_reset`, `launch_tick`, `launch_success`, `game_over`.

Positional audio (T2, carried from visual §12): drone sounds pan by drone screen position; machine sounds pan by machine position; a breach in the current room is center-loud; a breach in an adjacent room is quieter and panned toward that room; dropped items have no positional audio; no complex reverb.

---

# 7. UX

HTML and CSS only for all UI; canvas for world and map. The renderer observes state and never mutates it.

## 7.1 Screens (state machine)

```text
        start click
TITLE -----------------> RUNNING
  ^                        |
  | TITLE button           | launch success ............. SUCCESS
  |                        | integrity 0 / time 960 ...... FAILURE
  |________________________|  (RESTART -> fresh run, no popup)
```

- **TITLE:** working title **DERELICT STATION**; tagline `Survive until Day 8`; start button; control list (the 1.2 table); state icon legend (T2); dark station background with faint machine room; no animated cinematic; small red distress mark/cracked icon.
- **RUNNING:** the HUD below; no pause (0.2); the browser tab's natural stop is absorbed by the 0.25 s accumulator clamp.
- **SUCCESS** screen content (carried): `SHUTTLE LAUNCHED`, `SURVIVED UNTIL DAY {day}`, `SYSTEMS RESTORED` with `[check]`/`[x]` rows for O2 GENERATOR, O2 RECYCLER, REACTOR ONLINE, LAUNCH COMPUTER, FUEL INSTALLED, then `TIME USED: mm:ss / 16:00`, `DRONES DISABLED: n/2`, `BREACHES SEALED: n`. Style: calm, bright but not flashy, white/blue palette, small engine glow background, no heavy celebration. Buttons: RESTART, TITLE.
- **FAILURE** screen content (carried): `STATION LOST`, `CAUSE: {cause}` with icon (asphyxia = air icon with X; drone attack = drone triangle; reactor heat = snowflake/heat icon; integrity failure = shield with X; de-orbit = downward arrow), `TIME SURVIVED: mm:ss`, `SYSTEMS RESTORED` checklist rows. Style: dark, red accent only for the cause, no blame text. Buttons: RESTART, TITLE.

## 7.2 HUD (element → record field → when visible)

| Element (location) | Record field / function | When visible |
| --- | --- | --- |
| O2 bar + `O2 {n}` (top-left vitals) | `player.o2` | running; `LOW` below 25, `CRITICAL` below 10 with pulse |
| Integrity bar + `INTEGRITY {n}` | `player.integrity` | running; `LOW` below 25, `CRITICAL` below 10 |
| Room name (top-right room status) | `rooms[player.room].name` | running |
| Room O2 `O2 {n}` + `LOW` + X icon | `rooms[player.room].o2` (buckets: 60–100 plain; 30–59 LOW; 1–29 LOW; 0 LOW with X icon) | running |
| `HULL {n}` + `LOW` + `BREACH` | `rooms[player.room].hull`, `rooms[player.room].breached` | running; `LOW` below 30; `BREACH` at 0 |
| `POWER {state}` | `powerLabel(state, player.room)` | running (one of NO POWER / POWERED / EPC mm:ss / CELL mm:ss / REACTOR) |
| `DRONE {ACTIVE|—}` | active non-disabled drone in `player.room` | running |
| Coolant chip `COOLANT {mm:ss\|EXPIRED}` (near time panel) | `reactor.coolantTime` | `reactor.coolantActive` or `reactor.spinUpComplete`; flashing at or below 30 s |
| `DAY {n}` + `TIME TO DE-ORBIT {mm:ss}` (top-center) | `meta.time` (day = min(8, floor(time/120)+1); countdown = 960 − time) | running; red + banner below 120 s |
| `OBJECTIVE: {text}` | `currentObjective(state)` | running; after all complete: `SHUTTLE LAUNCHED` |
| Launch checklist rows (right side) | `launch.requirements.*`, `launch.progress` | `launch.visible` (bridge/shuttle entered, or reactor online ever); stays visible; O2 row shows `SHUTTLE O2 {n}/60` when under 60 |
| Launch progress bar + `LAUNCH {p}%` | `launch.progress` | checklist visible; reset reason line when `launch.lastResetReason` set |
| Inventory 6 slots + counts + selected outline (right) | `player.inventory`, `player.selectedSlot` | running; key labels 1–6 |
| Interaction prompt (bottom-center) | `channelTarget(state)` | when a target is in range: `E — PICK UP {item}` / `HOLD E — {action}` + progress bar + `REQUIRES {item/wrench}` / `PAUSED: {reason}` / reset reason |
| Event log, last 5 (bottom-left) | `log` (newest on top, older dimmed) | running |
| Station map (bottom-right, persistent) | `roomView(state, id)` × 10, `doors`, `reactor`, `warnings.active` (hull-event reticle + countdown) | running |
| Warning banner (top-center, max 2) | `activeWarnings(state)` | when non-empty; countdown when applicable |
| Tutorial prompts (Docking Bay / Crew Quarters) | static once-per-room list: `PICK UP WRENCH`, `HOLD E — REPAIR O2 GENERATOR`, `WATCH ROOM O2`, `CLOSE DOORS TO CONTROL AIRFLOW`, `MAP SHOWS POWER, O2, AND BREACHES` | first visit only; never blocking |
| First-drone prompt | `DRONE ACTIVE — CARGO HOLD` / `DRONE ACTIVE — SHUTTLE BAY` | on drone activation |

Layout is visual's (0.2): vitals top-left (panel width 240 px, bar width 180 px, bar height 18 px, label 14 px, numeric 22 px); time/objective top-center; room status top-right; launch checklist right below room status; inventory right above map; map bottom-right; log bottom-left; prompt bottom-center; warning banner overlays below the time panel. HUD inside a 24 px safe margin; scales with window.

## 7.3 Accessibility (carried from engineering §29 + visual principles)

The HUD must be playable with audio off and must not rely on color alone. Required text/shape signals present in HUD state (asserted in tests): `O2` label with number; `INTEGRITY` label with number; `POWER NO POWER` / `POWER POWERED` / `POWER EPC` / `POWER CELL` / `POWER REACTOR`; `HULL 0 BREACH`; `DRONE ACTIVE`; `COOLANT EXPIRED`; launch checklist item names; launch reset reason; door states on map (open/closed/jammed by line style + icon). Every critical state also has icon + label + sound (state colors are never the only signal).

## 7.4 Update cadence (carried)

State icons: immediate; HUD numbers: immediate (every simulation tick); bars: smooth interpolation optional (T2) but numeric values exact; warning banner: immediate on state change; map: immediate on room/power/door state change; particles: 60 FPS target, acceptable 30 FPS (T2); warning pulses: max 2 Hz (T2).

---

# 8. DEBUG API

One namespace, `dbg`, exposed as `window.dbg` in the browser (main.js) and mirrored by `tests/harness.js` (`createState` ≡ `dbg.reset`, `runTicks` ≡ `dbg.run`, `runUntil` ≡ `dbg.until`, `getEvents` returns the accumulated events, `assertInvariants` ≡ `dbg.invariants`). Rung on top of engineering's harness (0.2). All state reachers clamp to legal ranges and apply between ticks; invariants still validate on the next `advance`, so a debug value that violates a rule is caught, not hidden.

**Run control:**

| Function | Effect |
| --- | --- |
| `dbg.state` | reference to the live state (tests should clone) |
| `dbg.reset()` | fresh initial state from the compiled level |
| `dbg.clone()` | deep clone of current state |
| `dbg.run(n)` | advance n ticks with `dbg.input`; returns events |
| `dbg.until(predicate, maxTicks)` | advance until predicate(state) or maxTicks; returns events |
| `dbg.invariants()` | `assertInvariants(dbg.state)` → failure list (empty = pass) |

**Player inputs as functions (set the pending input frame):**

| Function | Effect |
| --- | --- |
| `dbg.move(x, y)` | `input.moveX, input.moveY` (−1/0/1) |
| `dbg.holdE(on)` | `input.interactDown` |
| `dbg.tapE()` | `input.interactPressed` for the next tick |
| `dbg.holdF(on)` | `input.useDown` |
| `dbg.tapF()` | `input.usePressed` for the next tick |
| `dbg.pressDrop()` | `input.drop` for the next tick |
| `dbg.select(slot)` | `input.select` (0–5) |
| `dbg.clearInput()` | neutral input frame |

**State reachers — one per gameplay system:**

| Function | System | Effect |
| --- | --- | --- |
| `dbg.setTime(t)` | time | `meta.time = clamp(t, 0, 960)` (warning/event windows recompute on next tick) |
| `dbg.setPlayerO2(v)` | vitals | `player.o2 = clamp(v, 0, 100)` |
| `dbg.setPlayerIntegrity(v)` | vitals | `player.integrity = clamp(v, 0, 100)` |
| `dbg.setWrench(b)` | items | `player.hasWrench = b` |
| `dbg.addItem(type, count = 1)` | items | add to inventory respecting stack limits; false if full |
| `dbg.removeItem(type, count = 1)` | items | remove from inventory; false if absent |
| `dbg.dropItem(type, roomId, x, y)` | items | append a dropped item (id from `meta.nextItemId`) |
| `dbg.setRoomO2(roomId, v)` | atmosphere | `rooms[roomId].o2 = clamp(v, 0, 100)` |
| `dbg.setHull(roomId, v)` | hull | `rooms[roomId].hull = clamp(v, 0, 100)`; `breached` recomputed |
| `dbg.setDoor(doorId, s)` | doors | `doors[doorId].state = 'open'\|'closed'\|'jammed'` |
| `dbg.givePower(roomId, type, seconds)` | power | add a timed source (`'epc'\|'cell'`) to the room's node (400 s max unless specified); node occupancy set |
| `dbg.setReactor({ pumpRepaired, coreRepaired, coolantTime, spinUpProgress, spinUpComplete, online })` | reactor | sets fields (subset ok); `coolantActive`/`heatHazard` recomputed from the rules |
| `dbg.setDrone(id, { state, x, y, room, disabled })` | drones | set drone fields (subset ok) |
| `dbg.setMachine(machineId, { repaired, completed })` | machines | set machine flags (subset ok) |
| `dbg.setLaunch({ computerPrimed, fuelInstalled, progress, visible })` | launch | set launch fields (subset ok) |
| `dbg.setObjective(index)` | objectives | `objectives.index = clamp(index, 0, 9)`; completions backfilled consistently |
| `dbg.end(status, cause)` | end states | set `meta.status` and `end` (for failure-mode tests) |
| `dbg.invariants(on)` (T2) | invariants | toggle `meta.debugInvariants` in the browser |

---

# 9. TESTS

Harness: Node.js built-in runner (`node --test tests/`), no browser required for core tests. `tests/harness.js` exports `createState()`, `cloneState(state)`, `runTicks(state, n, inputFactory)`, `runUntil(state, predicate, maxTicks)`, `getEvents(result)`, `assertInvariants(state)`; `inputFactory` is a fixed frame or a function `(tick, state) → input`; a run result is `{state, events, ticks}`. **All setup in every test below goes through the 8 reachers; all advancement through `dbg.run` / `dbg.until`; every call used here exists in 8.** Determinism rules (carried): no `Math.random` in simulation, no timestamps inside simulation, no async, all IDs from state counters — two runs with the same inputs produce identical states and event sequences.

Invariants (run after every tick in invariant tests; the 16 checks): time non-negative; room O2 in 0–100; room hull in 0–100; player O2 in 0–100; player integrity in 0–100; all inventory slots valid; stack counts positive and within limits; wrench not in inventory; dropped items inside valid rooms; doors have valid states; power nodes have valid occupancy; reactor coolant time not negative; launch progress in 0–100; drone positions walkable or in a valid door gap; no NaN in numeric state; if status is ended, no further gameplay changes.

## 9.1 Per-file checks

**`tests/level.test.js`** (setup: `compileLevel`; no `dbg` needed):
1. Level compiles exactly 10 rooms. 2. Room IDs match `docking, crew, storage, cargo, medbay, hydro, engineering, reactor, bridge, shuttle`. 3. Room dimensions match the 4.2 roster (e.g. crew 8×8, shuttle 8×6). 4. Initial room O2 matches the roster (docking 80, crew 70, storage 20, cargo 0, medbay 30, hydro 10, engineering 5, reactor 0, bridge 10, shuttle 0). 5. Initial hull matches (100/100/30/80/30/50/70/100/80/50). 6. Initial door states match (open, jammed, open, closed, closed, jammed, closed, closed, closed, closed). 7. Door graph matches the 10 edges. 8. Room interiors do not overlap. 9. Every door lies on a shared wall with overlap ≥ 2 tiles (minimum observed overlap: 4). 10. All rooms reachable from docking when jammed doors are repaired and closed doors opened. 11. Content counts match the full roster (29 pickups: 8/5/6/3/3/2/1 + 1 wrench). 12. Every machine exists in its correct room. 13. Power nodes exist only in crew/hydro/shuttle. 14. Drone homes are cargo and shuttle. 15. Hull event times are 230/240, 470/480, 710/720.

**`tests/movement.test.js` + `tests/doors.test.js`**:
1. Player moves within a room (`dbg.move(1, 0); dbg.run(20)` → x + 2.5 tiles). 2. Player cannot pass a closed door (position stays on the near side across 40 ticks). 3. Player cannot pass a jammed door. 4. Player passes an open door; room changes only when the point enters the adjacent room interior. 5. Open-closed-door channel takes 1 s (`dbg.tapE` + `dbg.holdE(true); dbg.run(20)` → `door_open` event; 19 ticks → still closing). 6. Close takes 1 s. 7. Jammed repair takes 5 s and requires the wrench (`dbg.setWrench(false)` → channel invalid, prompt reason `REQUIRES WRENCH`). 8. Repaired jammed door becomes `closed`. 9. Door progress retains if paused (hold 10 ticks, release, resume → completes at 20 total ticks). 10. Airflow and power follow door state (open → transfer and power pass; closed → both zero). 11. Completed door action affects power in the same tick. 12. Room assignment never flickers in a door gap (room constant while crossing).

**`tests/atmosphere.test.js`**:
1. Unbreached room drains 0.5 O2/sec (`dbg.setRoomO2('crew', 70); dbg.run(20)` → 69.5, no machines powered). 2. Breached room drains 15/sec (`dbg.setHull('storage', 0); dbg.run(20)` → −15 O2). 3. Repaired powered generator: `dbg.setMachine('crew_o2_generator', {repaired: true, completed: true})` with crew powered → +8/sec net of drain = +7.5 (20 ticks → +7.5). 4. Repaired but unpowered machine generates zero. 5. Unrepaired machine generates zero. 6. Airflow formula: rooms 100 and 0, door open, all else isolated → transfer 5 O2 in 1 s (`dbg.run(20)` → 95 / 5). 7. Airflow only through open doors. 8. Closed doors transfer zero. 9. Jammed doors transfer zero. 10. Simultaneous airflow is deterministic (three-room chain, run twice, identical states). 11. Room O2 clamps to 0 and 100. 12. Breached room with powered generator still loses O2 (15 drain > 6 gen → net −9).

**`tests/power.test.js`**:
1. Start EPC powers crew (`powerLabel('crew')` = `EPC 6:40` at 40 s). 2. Power does not pass a closed door (crew-hydro closed → hydro `NO POWER`). 3. Power passes an open door. 4. Power does not pass a jammed door. 5. Cell install takes 2 s (`dbg.addItem('power_cell'); dbg.run(40)` at node → `power_install`). 6. Install requires empty node (crew with active EPC → channel invalid). 7. Cell installs into an empty node even when the room is powered by propagation. 8. Cell provides 400 s. 9. Expiration emits `power_cell_expire` and clears the node. 10. Losing all paths emits `power_loss`. 11. Reactor online powers the reactor room (`dbg.setReactor({spinUpComplete: true, coolantTime: 100})` → `powerLabel('reactor')` = `REACTOR`). 12. Reactor power propagates through open doors. 13. Display source is correct in all five states.

**`tests/reactor.test.js`**:
1. Pump repair takes 5 s. 2. Coolant use takes 5 s. 3. Coolant cell sets `coolantTime = 180`. 4. Second cell does not add (180 → 180). 5. Core repair takes 8 s. 6. Spin-up takes 20 s (`dbg.run(400)` at core holding E with coolant → `spinUpComplete`). 7. Spin-up requires coolant active. 8. Spin-up progress pauses when the player leaves (retains). 9. Coolant expiry before completion resets `spinUpProgress` to 0 and emits `reactor_spinup_aborted`. 10. `online` requires `spinUpComplete` and active coolant. 11. Online reactor provides power. 12. Expiry after spin-up sets `heatHazard`. 13. Expiry before spin-up sets no heat hazard. 14. Player in reactor room during heat hazard loses 5/sec (`dbg.run(20)` → −5 integrity, `lastDamageSource = 'reactor'`). 15. New coolant restores online and clears heat. 16. `coolant_low` warning enters below 30 s. 17. `coolant_expired` fires at 0.

**`tests/drones.test.js`**:
1. Both drones start inactive. 2. A activates when the player first enters cargo (`dbg`-move player via legal path; `drone_activate` event). 3. B activates on first shuttle entry. 4. Inactive drones do not move. 5. Patrol speed 2.5 tiles/sec (20 ticks → 2.5 tiles toward waypoint). 6. Alert speed 3.0 tiles/sec. 7. Same-room player enters alert after exactly the 1 s delay (19 ticks: still patrol; 20th: alert + `drone_alert`). 8. Drone follows the player through open doors (room path BFS). 9. Drone does not follow through closed doors. 10. No path → returns to patrol after 3 s. 11. Attack deals 20 damage (within 1 tile, cooldown 0, no i-frames). 12. Attack cooldown 1 s. 13. I-frames block damage for 0.5 s without consuming the cooldown. 14. EMP disables all active drones in the room. 15. EMP unusable with no active drone in the room (`ui_error`). 16. EMP consumed only on completion (release F mid-channel → charge retained). 17. Disabled drones do not reactivate (run 200 ticks). 18. No-EMP containment: player lures B into bridge, closes bridge-shuttle, keeps hydro-shuttle open → B has no path, waits, and deals zero damage during a full 30 s launch channel run at the pad.

**`tests/hull.test.js`**:
1. Event 1 warning starts at 230 (`dbg.setTime(229); dbg.run(20)` → warning active, reticle on storage, `hull_event_warning` once). 2. Damage applies at 240 (`dbg.setTime(239); dbg.run(20)`; storage hull 30 → 0, `breach` event). 3. Event 2 warning at 470. 4. Event 2 damage at 480 (two rooms, −30 each). 5. Event 3 warning at 710. 6. Event 3 damage at 720 (shuttle −50). 7. Events never target the current player room (`dbg`-place player in storage → event 1 hits cargo instead). 8. Events skip already-breached targets. 9. Event 1 fallback chain (storage breached → cargo; both breached → crew −20). 10. Event 2 fallbacks, and 11. Event 2 never damages the same room twice. 12. Event 3 fallbacks. 13. Event damage can cause a breach. 14. Event damage never raises hull. 15. Patch adds +40 max 100 (`dbg.setHull('storage', 30)` + patch channel → 70; from 80 → 100). 16. Seal sets hull to 60 and increments `breachesSealed`. 17. Patch consumed only on completion. 18. Interrupted patch not consumed. 19. `breach` event fires on the transition.

**`tests/vitals.test.js`**:
1. Room O2 ≥ 60 → player O2 +0.5/sec (`dbg.setRoomO2` + `dbg.run(20)` → +0.5). 2. 30–59 → −0.5/sec. 3. 1–29 → −1.5/sec. 4. Below 1 → −3/sec. 5. Player O2 clamps 0–100. 6. Player O2 0 → integrity −5/sec, source asphyxia. 7. Medkit +50. 8. Medkit blocked at 100 (`ui_error`). 9. O2 Tank +50. 10. O2 Tank blocked at 100. 11. Reactor heat −5/sec in the reactor room during hazard only. 12. Drone damage sets `lastDamageSource = 'drone'`. 13. Death cause `asphyxia`. 14. Death cause `drone_attack`. 15. Death cause `reactor_heat`.

**`tests/items.test.js`**:
1. Inventory has 6 slots. 2. Stacking below max (two O2 Tanks → one slot count 2). 3. Full inventory blocks pickup (`ui_error`). 4. Dropped items persist (run 500 ticks, still present). 5. Dropped items re-pickable. 6. Wrench not in inventory. 7. Wrench cannot be dropped (Q → nothing). 8. Wrench remains available after dropping other items. 9. Selecting an empty slot does nothing. 10. Invalid use emits `ui_error`. 11. Stack limits enforced (6th O2 Tank pickup blocked while 5 stacked). 12. Item counts match world counts (29 total at start).

**`tests/channels.test.js`**:
1. Repair progress retains when paused. 2. Machine repair completes only after full time. 3. Jammed door repair requires wrench. 4. Hull patch requires wrench and Hull Patch. 5. Power cell consumed only on completion. 6. Coolant cell consumed only on completion. 7. Fuel rod consumed only on completion. 8. Launch computer progress retains when paused. 9. Launch computer requires bridge power (unpowered → paused `PAUSED: NO POWER`). 10. Spin-up progress retains when paused. 11. Spin-up resets if coolant expires. 12. EMP consumed only on completion. 13. Progress does not advance with the required item missing. 14. Progress does not advance out of range.

**`tests/launch.test.js`**:
1. Checklist hidden before trigger. 2. Visible after entering bridge. 3. Visible after entering shuttle. 4. Visible after reactor online. 5. Progress advances only with all requirements true. 6. Only at the pad (1.5 tiles). 7. Only while holding E. 8. Releasing E pauses, does not reset. 9. Leaving the pad resets (`LEFT PAD`). 10. Damage resets (`PLAYER DAMAGED`). 11. Reactor offline resets. 12. Shuttle unpowered resets. 13. Computer not primed resets. 14. Fuel missing resets. 15. Shuttle O2 below 60 resets. 16. Reset reason is the correct priority (damage beats pad-left beats requirements). 17. 100% triggers success. 18. Success precedence over same-tick death (`dbg.setPlayerIntegrity(0)` at the completing tick → success). 19. Success precedence over de-orbit at 960 s. 20. De-orbit failure when launch is not complete at 960 s.

**`tests/objectives.test.js`**:
1. Initial objective is "Repair Crew O2 Generator". 2. Advances after the generator repair. 3. "Stabilize Crew Atmosphere" requires 5 continuous seconds of crew O2 ≥ 60 (5 s with a dip below 60 → timer resets). 4. Advances on first hydro entry. 5. Advances after recycler repair. 6. Advances on reactor online. 7. Advances after computer primed. 8. Advances after fuel installed. 9. Advances once shuttle O2 reaches 60 (stays complete if it later drops). 10. Completes on launch success. 11. Objectives never regress.

**`tests/audioEvents.test.js`** (assert event audio fields; no audio loaded):
1. Breach emits `breach`. 2. Power loss emits `power_loss`. 3. Cell expiration emits `power_cell_expire`. 4. Drone activation emits `drone_activate`. 5. Drone alert emits `drone_alert`. 6. Drone attack emits `drone_attack`. 7. Hull event warning emits `hull_event_warning` exactly once per window. 8. `coolant_low` enters below 30 s. 9. `coolant_expired` at 0. 10. `reactor_online` on online transition. 11. `deorbit_warning` at 120 s remaining. 12. `launch_reset` with reason. 13. `launch_success`. 14. `game_over`. 15. Every emitted audio name exists in the 6.3 roster (manifest check). 16. Warning audio never repeats per tick (trackers).

**`tests/invariants.test.js`**:
1. 1000 ticks, no input → invariants hold. 2. 1000 ticks, deterministic pseudo-input pattern (fixed sequence, no RNG) → invariants hold. 3. Forced breach run → invariants hold. 4. Reactor coolant expiry run → invariants hold. 5. Both drone activations → invariants hold. 6. All three hull events → invariants hold. 7. Launch reset then success → invariants hold.

**`tests/acceptance/referenceWin.test.js`** (legal inputs only; macros may wrap legal sequences — no teleports, no direct machine writes): the 49-step strategy carried from engineering §27.15: start in docking; take wrench, 2 O2 Tanks, medkit, hull patch; crew: repair O2 Generator, hold crew O2 ≥ 60 for 5 s; repair jammed crew-storage door; storage: patch hull before 240 s, collect 1 O2 + 2 patches + 1 EMP; close crew-storage; medbay: patch before 480 s, collect, close medbay; open crew-hydro; hydro: pick up power cell, install in hydro node, repair O2 Recycler, keep crew-hydro open; repair jammed hydro-engineering door; engineering: pick up coolant cell + fuel rod, repair pump, use coolant, open engineering-reactor; reactor: pick up coolant, EMP, patch, repair core, spin up 20 s, online; engineering → bridge: open engineering-bridge, prime computer 15 s; shuttle prep: open hydro-shuttle and/or bridge-shuttle, install shuttle cell if needed; shuttle: EMP Drone B (allowed here), patch before 720 s, repair vent, install fuel, raise shuttle O2 to 60, use second coolant before expiry, stand at pad, 30 s channel. Assertions: `status = 'success'`; `time < 960`; `launch.success`; all five requirements true at success; player alive; fuel rod consumed; at least one coolant used; reactor online at launch; computer primed; no invariant failures; no negative item counts; no required dropped item lost; log contains `launch_success`.

**`tests/acceptance/noEmpWin.test.js`** (carried): same route but no EMP used or picked up; at the shuttle, lure B into the bridge, close bridge-shuttle, wait for B to lose path (3 s) and settle, keep hydro-shuttle open for power/O2, launch. Assertions: `status = 'success'`; `stats.empUsed = 0`; drone B `disabled = false`; all requirements true at success; drone B dealt zero damage during the launch channel.

**`tests/acceptance/failureModes.test.js`** (carried):
1. Death by asphyxia (isolated zero-O2 room, no tanks). 2. Death by drone attack (no evasion). 3. Death by reactor heat (heat hazard, stand in room). 4. De-orbit failure (idle to 960). 5. Death sets the correct cause. 6. De-orbit cause is `deorbit`. 7. End data includes time survived. 8. End data includes systems restored. 9. No respawn after failure (status stays ended; further ticks produce no events).

**`tests/acceptance/resourceFairness.test.js`** (carried):
1. All required resources exist (roster counts). 2. Win path that never collects Cargo Hold resources. 3. Event 1 breach preventable by patching storage before 240 s. 4. Event 2 medbay breach preventable before 480 s. 5. Event 3 shuttle breach preventable before 720 s. 6. Sealing a breach restores hull to 60. 7. If all three major breaches are prevented, no event starts a room breached. 8. Dropped required items are recoverable. 9. Closing all doors never permanently prevents reopening.

**`tests/browser/smoke.test.js`** (Playwright or equivalent; T1):
1. Page loads without console errors. 2. Title screen visible. 3. Start button starts the game. 4. World canvas visible. 5. All HUD panels visible. 6. Simulation time advances after 1 real second. 7. HUD numbers update. 8. Map visible. 9. No uncaught exceptions after 10 seconds. Do not assert visual quality.

## 9.2 SCREENSHOTS

Constructed from visual's QA checklist and end screens (ruling 0.2); every one of visual's 14 QA items maps to a row or to the 11 accessibility checks.

| ID | Screen / state | Must be visible |
| --- | --- | --- |
| S1 | TITLE | Title "DERELICT STATION", tagline "Survive until Day 8", start button, control list (WASD/arrows, E, 1–6, F, Q), state icon legend (T2), dark station background, red distress mark |
| S2 | RUNNING, start (Docking Bay, t=0) | Vitals `O2 100` / `INTEGRITY 100`; `DAY 1`, `TIME TO DE-ORBIT 16:00`; `OBJECTIVE: Repair Crew O2 Generator`; room status `DOCKING BAY / O2 80 / HULL 100 / POWER NO POWER / DRONE —`; floor pickups: wrench, 2 O2 Tanks, medkit, hull patch; prompt `E — PICK UP WRENCH`; map with all 10 nodes, docking outlined; log empty |
| S3 | RUNNING, Crew Quarters (t≈30 s, generator repaired) | `POWER EPC 6:40`; `OBJECTIVE: Stabilize Crew Atmosphere`; O2 Generator cyan working light; EPC node display `EPC 6:40`; map shows crew + medbay powered (open door), hydro/storage not |
| S4 | RUNNING, Storage approach | `door_crew_storage` jammed: askew panels, red flashing light, warning stripes; map line crossed red with X; `HULL 30 LOW` with crack decals; prompt `HOLD E — REPAIR JAMMED DOOR / REQUIRES WRENCH` |
| S5 | RUNNING, hull event warning (t≈233 s) | Banner `WARNING: HULL EVENT — STORAGE 0:07`; red target reticle + countdown on ST node; room O2 `O2 20 LOW`; audio `hull_event_warning` |
| S6 | RUNNING, Hydroponics (recycler working, crew-hydro open) | `POWER CELL 3:44`; O2 Recycler cyan with subtle output particles (T2); airflow particles through the open door from crew to hydro (T2); `OBJECTIVE: Reach Hydroponics` complete state |
| S7 | RUNNING, Engineering (pump repaired, coolant just applied) | Coolant chip `COOLANT 3:00` (snowflake); coolant pump blue snowflake light; prompt `HOLD E — REACTOR SPIN-UP` (after core repair) or `HOLD E — REPAIR REACTOR CORE`; `O2 5 LOW` on room status |
| S8 | RUNNING, Reactor Core (spin-up in progress) | Core rotating with white-blue progress ring at ~60%; coolant chip counting down; `HOLD E — REACTOR SPIN-UP` with progress bar |
| S9 | RUNNING, Reactor Core (heat hazard) | Core glow red, steam puffs, red floor pulse inside the room only; banner `COOLANT EXPIRED`; chip `COOLITY EXPIRED` → `COOLANT EXPIRED`; integrity draining; `WARNING: INTEGRITY LOW {n}` if below 25 |
| S10 | RUNNING, Bridge (checklist first visible) | Checklist: `[✓] REACTOR ONLINE`, `[ ] SHUTTLE POWERED`, `[ ] COMPUTER PRIMED` (priming light), `[ ] FUEL INSTALLED`, `[ ] SHUTTLE O2 0/60`; `LAUNCH 0%`; map BR highlighted |
| S11 | RUNNING, Shuttle Bay (Drone B alert) | Drone with orange light + ring above it; `DRONE ACTIVE`; checklist partial `[✓] REACTOR ONLINE [✓] SHUTTLE POWERED [✓] COMPUTER PRIMED [✓] FUEL INSTALLED [ ] SHUTTLE O2 42/60`; O2 Vent machine |
| S12 | RUNNING, launch channel active | Pad lights blue-white cycling; `LAUNCH 34%`; prompt `HOLD E — LAUNCH` with progress bar; shuttle lights blue-white; `LAUNCH 34` tick sound state |
| S13 | RUNNING, launch reset | Banner `LAUNCH RESET — SHUTTLE O2 LOW`; checklist O2 row red X flashing; `LAUNCH 0%`; log entry with reason |
| S14 | SUCCESS | `SHUTTLE LAUNCHED`, `SURVIVED UNTIL DAY {day}`, systems-restored checklist with checks, `TIME USED: mm:ss / 16:00`, `DRONES DISABLED: n/2`, `BREACHES SEALED: n`; calm white/blue palette; RESTART/TITLE buttons |
| S15 | FAILURE | `STATION LOST`, `CAUSE: {cause}` with matching icon (e.g. air icon with X for asphyxia), `TIME SURVIVED: mm:ss`, systems restored list; dark style, red only on cause; RESTART/TITLE |
| S16 | RUNNING, critical vitals | `O2 7` with `CRITICAL` label and pulsing bar; cyan edge vignette; banner `WARNING: PLAYER O2 CRITICAL 7`; (T2) pulse max 2 Hz |

QA mapping (carried, no check dropped): tell player O2 low without reading the number → S16; room O2 low → S2/S6; room breached → S4/S5; room powered → S3; unpowered → S2; drone active → S11; coolant low → S7/S9; missing launch requirement → S10/S13; jammed door → S4; available action → S4/S8; paused/reset reason → S13; de-orbit critical → S5-pattern banner (de-orbit row of 7.2); all states with audio off → 7.3; all critical states colorblind-safe → 7.3.

---

# 10. BUILD ORDER

Milestones derived from engineering's structure and DoD; each names the section-9 check that shows it landed.

1. **M1 — Level and contracts.** Files exist (2.1); `compileLevel` + `validateLevel`; `createInitialState`. *Landed when: `level.test.js` checks 1–15 pass.*
2. **M2 — Fixed-step loop, movement, doors.** `gameLoop`, `advance` skeleton, player point movement, door channels. *Landed when: movement/doors tests checks 1–12 pass.*
3. **M3 — Atmosphere and vitals.** Room O2, machines, airflow, player O2/integrity. *Landed when: `atmosphere.test.js` 1–12 and `vitals.test.js` 1–15 pass.*
4. **M4 — Power.** Sources, nodes, propagation, display, loss. *Landed when: `power.test.js` 1–13 pass.*
5. **M5 — Hull and events.** Patch/seal, scheduled events with retargeting. *Landed when: `hull.test.js` 1–19 pass.*
6. **M6 — Reactor.** Pump, coolant, core, spin-up, online, heat. *Landed when: `reactor.test.js` 1–17 pass.*
7. **M7 — Drones.** States, pathing, attacks, EMP, containment. *Landed when: `drones.test.js` 1–18 pass.*
8. **M8 — Items and channels.** Inventory, drops, channels, machines. *Landed when: `items.test.js` 1–12 and `channels.test.js` 1–14 pass.*
9. **M9 — Launch, objectives, warnings, end states.** *Landed when: `launch.test.js` 1–20, `objectives.test.js` 1–11, `audioEvents.test.js` 1–16 pass.*
10. **M10 — Determinism and acceptance.** Invariants in tests; scripted wins and failures. *Landed when: `invariants.test.js` 1–7, `referenceWin`, `noEmpWin`, `failureModes` 1–9, `resourceFairness` 1–9 pass.*
11. **M11 — Presentation.** World render (11-step order), textures, map, HUD, title, end screens. *Landed when: `browser/smoke.test.js` 1–9 pass and screenshots S1–S16 match.*
12. **M12 — Audio wiring.** Web Audio synthesis from 6.3/6.4; loops and swaps. *Landed when: `audioEvents.test.js` 1–16 still pass and smoke test reports zero console errors with audio active.*
13. **M13 — T2 items (0.3 order).** Music layers → airflow/breach particles → cosmetic particles → positional pan → warning pulse + bar interpolation → texture detail → static pre-render → title icon legend → browser invariants toggle. *Landed when: smoke stays green and S4/S6/S11/S13 show the new effects; music verified by layer triggers per 6.2.*

---

# 11. DEFINITION OF DONE

One header per 0.1 row. When every header is complete, the game is complete (T1 ship = rows 1–15; full completion = row 16 as well).

**1. Runs as a browser game**
- Checks: `browser/smoke.test.js` 1–9; HUD inside the 24 px safe margin at 1080p and 1366×768.
- Screenshots: S2.

**2. Survival gameplay**
- Checks: `vitals.test.js` 1–15; `referenceWin` "player alive"; invariants: player O2/integrity in 0–100 every tick.
- Screenshots: S2, S16.

**3. Derelict space station setting**
- Checks: `level.test.js` 1–9 (10 rooms, roster sizes/O2/hull, shared-wall doors, connected graph).
- Screenshots: S3, S4.

**4. Air management**
- Checks: `atmosphere.test.js` 1–12 (drains 0.5/15, machine rates 8/4/6, airflow 5×|Δ|/100, simultaneous, clamps).
- Screenshots: S6.

**5. Power management**
- Checks: `power.test.js` 1–13 (EPC 400 s, propagation through open doors only, 2 s install, empty-node rule, display states).
- Screenshots: S3.

**6. Hull and scheduled events**
- Checks: `hull.test.js` 1–19; `resourceFairness` 3–7 (all three breaches preventable; seal to 60).
- Screenshots: S4, S5.

**7. Reactor**
- Checks: `reactor.test.js` 1–17 (180 s coolant, 20 s spin-up, abort, heat 5/sec, recovery with second cell).
- Screenshots: S7, S8, S9.

**8. Drones**
- Checks: `drones.test.js` 1–18; `noEmpWin` passes (`empUsed = 0`, B undamaged during channel).
- Screenshots: S11.

**9. Launch objective**
- Checks: `launch.test.js` 1–20; `referenceWin` asserts success before 960 s with all requirements true.
- Screenshots: S10, S11, S12, S13.

**10. Guided progression**
- Checks: `objectives.test.js` 1–11 (sequence, 5 s stabilization, no regression).
- Screenshots: S3 (objective text), S12.

**11. Items and inventory**
- Checks: `items.test.js` 1–12; `resourceFairness` 8–9 (drops recoverable; no door softlock).
- Screenshots: S2.

**12. Readable HUD**
- Checks: all 7.3 text/shape signals asserted present in HUD state; `smoke` check 5 (all panels); numbers exact, bars optional-interpolated only.
- Screenshots: S2–S16 (all).

**13. Audio feedback**
- Checks: `audioEvents.test.js` 1–16 (every required event name, no per-tick repeats); M12 smoke with audio active, zero console errors.
- Screenshots: S16 (visual counterpart — banner + vignette paired with the audible warning).

**14. End screens**
- Checks: `failureModes` 5–9 (causes, time survived, systems restored, no respawn); `referenceWin` success data.
- Screenshots: S14, S15.

**15. Deterministic, fixed-step simulation with tests**
- Checks: `invariants.test.js` 1–7; determinism rules (no `Math.random` in simulation; IDs from counters); `referenceWin` and `noEmpWin` reproduce identically across runs.
- Screenshots: S2 (a live run proves the loop).

**16. Presentation polish (T2)**
- Checks: each 0.3 T2 item implemented per its section (6.2 music triggers; 3.6 particle rules; 6.4 pan; 7.4 pulses; 3.5 texture detail; 10.M13 pre-render; 7.3 legend; 8 invariants toggle); smoke stays green.
- Screenshots: S4, S6, S11, S13 (with T2 effects).

---

# A. SANITY

Re-read of sections 2, 4, 8, and 9; sections above fixed where a check failed. Results:

1. **Every field a rule reads or writes is in the global context (2.2).** Audited each 4.x rule against 2.2: `player.*` (x, y, room, o2, integrity, hasWrench, invulnerable, selectedSlot, facing, inventory, lastDamageSource, tookDamageThisTick), `rooms.*` (o2, hull, breached, powered, powerSource, eventWarning, geometry), `doors.*`, `machines.*`, `channels` (4.17), `droppedItems`, `power.sources/nodes`, `reactor.*`, `drones.*` (including `alertDelay` for the 1 s rule), `launch.*`, `objectives.*`, `warnings.active/trackers`, `log`, `stats.*`, `meta.*`, `end`. **Finding fixed:** engineering's 4.3 shape lacked `state.channels`, `meta.nextItemId`, and `player.facing` — all three added to 2.2 (ruling 0.2 row "State omissions"). Result: **closes (after fix)**.
2. **Every place, thing, or kind a rule names is placed by a generator or rostered.** 10 rooms (4.2 roster, coordinates verified against the designer's sizes; every door edge verified on a shared wall with overlap ≥ 2 tiles: docking-crew 4, crew-storage 6, crew-medbay 4, crew-hydro 6, storage-cargo 5, hydro-engineering 6, hydro-shuttle 6, engineering-reactor 5, engineering-bridge 5, bridge-shuttle 6); 10 doors (roster); 8 machines + 3 power nodes (roster, placed by the `levelLayout` compiler per the 4.2 rules); 29 pickups (roster + placement algorithm, counts verified: docking 5, crew 2, storage 4, cargo 3, medbay 3, hydro 2, engineering 2, reactor 3, bridge 1, shuttle 4 = 29, matching item totals 8+5+6+3+3+2+1+1); 2 drones with homes and three deterministic waypoints each; 3 hull events with candidate chains; 9 objectives. Result: **closes**.
3. **Consumable totals: placed vs demanded along the core loop.** Hull Patch 6 placed vs 3 demanded (prevent events 1–3) — 3 spare for recovery; Power Cell 3 vs 2 demanded (hydro + shuttle bridge) — 1 spare; Coolant Cell 2 vs 2 demanded (spin-up + hold online through launch) — exact, and the HUD timer makes the sequencing visible (fairness principle carried); Fuel Rod 1 vs 1; EMP 3 vs 0 demanded (no-EMP win is a test, not a demand); O2 Tank 8 and Medkit 5 are contingency (room O2 regeneration is primary; up to ~5 drone hits survivable) — sufficient. Result: **closes** (all margins ≥ 0; coolant is exact by design).
4. **Timing pairs close AND still bite.**
   - De-orbit 960 s vs expected clear 720–900 s (4.15 pacing): margin 60–240 s — closes and still bites (a stalled player fails).
   - EPC 400 s vs reactor online (expected by ~300–480 s): if the reactor lands after 400 s, the hydro cell (available by ~180 s, 2 s install) must be in by 400 s; pacing installs it by ~250 s → 150 s margin — closes; bites if the player never reaches hydro.
   - Cell 400 s vs launch start (720–900 s): shuttle cell installed by ~650 s covers to ~1050 s — closes.
   - Coolant 180 s vs 30 s channel + reactor→shuttle travel (≤ ~12 s at 3.5 tiles/sec via the room graph): 180 ≥ 42 — closes; bites at exactly two cells (ruling: no third).
   - Hull event warning 10 s vs reaction (adjacent-room travel ≤ 10 s + patch 3 s / seal 4 s): closes — events target single rooms and patches are pre-collectible (6 vs 3); bites because an unpatched target breaches (30−30, 30−30, 50−50 with −30/−30/−50).
   - Breach drain 15/sec vs vent 6/sec in a breached shuttle: net −9 → 60 O2 unreachable until sealed — intended bite (4.12), and `resourceFairness` 6 covers the recovery.
   - Room baseline 0.5/sec vs O2 Tank +50: a 70-O2 room holds 140 s — closes.
   - Drone chase: player 3.5 > alert 3.0 tiles/sec — closes; bites within 1-tile attack range with 1 s cooldown.
   - Spin-up 20 s vs coolant 180 s: 160 s of slack — closes.
   - Same-tick order: success evaluated before death, death before de-orbit (1.2 step 13) — closes.
   Result: **closes** (every pair verified; no clock is unreachable, and each pressure still costs).
5. **Every call section 9 makes is in section 8.** Cross-checked the reacher set used across 9.1/9.2: `setTime`, `setPlayerO2`, `setPlayerIntegrity`, `setWrench`, `addItem`, `removeItem`, `dropItem`, `setRoomO2`, `setHull`, `setDoor`, `givePower`, `setReactor`, `setDrone`, `setMachine`, `setLaunch`, `setObjective`, `end`, `move`, `holdE`, `tapE`, `holdF`, `tapF`, `pressDrop`, `select`, `clearInput`, `run`, `until`, `reset`, `clone`, `invariants`, `state` — all present in 8 (harness mirroring stated in 8). Result: **closes**.
6. **No placeholder in angle brackets remains.** Scanned the merged document: visual's `SURVIVED UNTIL DAY X` replaced with the computed `DAY {day}` field (7.1); engineering 16.4's deliberated audio names resolved to `reactor_coolant_applied`/`repair_complete` (0.2); all other bracketed unions are type syntax, not placeholders. Result: **closes**.