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
