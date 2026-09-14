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
