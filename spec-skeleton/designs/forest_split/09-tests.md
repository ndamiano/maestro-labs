# 9. TESTS

All tests use functions from section 8. Expected states follow from section 4 rules.

## 9.1 Core and math tests

| ID | Call | Expected state |
| --- | --- | --- |
| CORE-001 | `createSim({})`, then `sim.debug.simSnapshot()` | Sim state is title with default config. |
| CORE-002 | `createSim({ seed: 123 })`, then advance two steps, then `createSim({ seed: 123 })` and advance two steps | RNG-driven waypoint states are identical. |
| CORE-003 | `createSim({})`, then `sim.debug.setDawnRemaining(480)`, then `advanceSim(sim, 1, idleInput)` | Dawn remaining is 479. |
| CORE-004 | `createMockInput()`, then `input.setMove(1, 1)`, then `input.frame()` | Input frame moveX is 1 and moveY is 1. |
| CORE-005 | `createMockInput()`, then `input.setSprint(true)`, then `input.frame()` | Input frame sprint is true. |

## 9.2 Map tests

| ID | Call | Expected state |
| --- | --- | --- |
| MAP-001 | `createMapFixture()`, then `map.tileAt(0, 0)` | Border tile is impassable. |
| MAP-002 | `loadRealMap()`, then `validateMap(mapJson)` | No contract errors. |
| MAP-003 | `loadRealMap()`, then `map.isInGateGap(60, 4)` | True. |
| MAP-004 | `loadRealMap()`, then `map.isPassable(60, 6)` | True. |
| MAP-005 | `loadRealMap()`, then `map.objectAt(95, 60)` | Key A. |
| MAP-006 | `loadRealMap()`, then count underbrush clusters | At least 8 clusters. |
| MAP-007 | `loadRealMap()`, then check clusters near 60, 6 | At least 2 clusters within Chebyshev distance 6. |
| MAP-008 | `loadRealMap()`, then run route length checks | Start to A 120 to 160, A to C 120 to 160, C to B 160 to 200, B to gate 160 to 200, total 550 to 750. |

## 9.3 Collision tests

| ID | Call | Expected state |
| --- | --- | --- |
| COL-001 | `createSim({})`, set player near tree, `input.setMove` into tree, `advanceSim(sim, 1, inputFactory)` | Player position does not enter tree tile. |
| COL-002 | `createSim({})`, set player near underbrush, move into underbrush | Player center enters underbrush tile. |
| COL-003 | `createSim({})`, set player at diagonal corner, move diagonally around blocker | Player does not cut corner. |
| COL-004 | `createSim({})`, gate closed, set player near gap, move north into gap | Player does not enter closed gap. |
| COL-005 | `createSim({})`, `sim.debug.forceGateOpen()`, move north into gap | Player enters gap. |
| COL-006 | `createSim({})`, set safe zone active, place Hollow outside safe tile, force movement into safe tile | Hollow does not enter active safe tile. |
| COL-007 | `createSim({})`, place Hollow in tile, make tile safe after Hollow is already there | Hollow remains in tile and does not teleport. |

## 9.4 Line-of-sight tests

| ID | Call | Expected state |
| --- | --- | --- |
| LOS-001 | `sim.debug.hasLineOfSight(a, b)` with tree between | False. |
| LOS-002 | `sim.debug.hasLineOfSight(a, b)` with rock between | False. |
| LOS-003 | `sim.debug.hasLineOfSight(a, b)` with water between | False. |
| LOS-004 | `sim.debug.hasLineOfSight(a, b)` with underbrush between | True. |

## 9.5 Pathfinding tests

| ID | Call | Expected state |
| --- | --- | --- |
| PATH-001 | `sim.debug.findPath(start, target, { forHollow: false })` in open area | Path exists. |
| PATH-002 | `sim.debug.findPath(start, target, { forHollow: false })` with blockers | Path does not enter impassable tiles. |
| PATH-003 | `sim.debug.findPath(start, target, { forHollow: true })` with safe predicate | Path avoids active safe tiles. |
| PATH-004 | `sim.debug.findPath` through underbrush | Underbrush tile cost is 1.25. |
| PATH-005 | `sim.debug.nearestReachable(start, unreachableTarget, { forHollow: true })` | Returns nearest reachable tile, not null. |
| PATH-006 | `sim.debug.findPath` diagonal through corner | Diagonal path does not cut blocked corners. |

## 9.6 Player tests

| ID | Call | Expected state |
| --- | --- | --- |
| PLAYER-001 | Set idle, `input.setMove(1, 0)`, `advanceSim(sim, 1, inputFactory)` | Player moves approximately 3.6 tiles. |
| PLAYER-002 | Set idle, `input.setMove(1, 0)`, `input.setSprint(true)`, `advanceSim(sim, 1, inputFactory)` | Player moves approximately 6.0 tiles while breath remains. |
| PLAYER-003 | Place player in underbrush, walk 1 second | Movement is approximately 3.06 tiles. |
| PLAYER-004 | `sim.debug.setPlayerState({ breath: 100 })`, sprint for 1 second | Breath decreases by 20. |
| PLAYER-005 | `sim.debug.setPlayerState({ breath: 100 })`, walk for 1 second | Breath increases by 15. |
| PLAYER-006 | `sim.debug.setPlayerState({ breath: 100 })`, stand for 1 second | Breath increases by 30. |
| PLAYER-007 | `sim.debug.setPlayerState({ breath: 0 })`, sprint input, advance 1 second | Player does not sprint. |
| PLAYER-008 | `sim.debug.setPlayerState({ breath: 20 })`, stand 1 second | Breath reaches at least 25 and breathLocked becomes false if it was locked. |
| PLAYER-009 | `sim.debug.setPlayerState({ fuel: 50 })`, lantern on, advance 1 second | Fuel decreases by 0.5. |
| PLAYER-010 | `sim.debug.setPlayerState({ fuel: 70 })`, `sim.debug.giveEmber('E1')` | Fuel is 100. |
| PLAYER-011 | `sim.debug.setPlayerState({ fuel: 50 })`, `sim.debug.lightRadius()` | Light radius is 6.0. |
| PLAYER-012 | `sim.debug.setPlayerState({ fuel: 25 })`, lantern on, `sim.debug.safeActive()` | True. |
| PLAYER-013 | `sim.debug.setPlayerState({ fuel: 24.999 })`, lantern on, `sim.debug.safeActive()` | False. |
| PLAYER-014 | Place player in underbrush, `sim.debug.simSnapshot()` | Player covered is true. |
| PLAYER-015 | Place player adjacent to rock, `sim.debug.simSnapshot()` | Player covered is true. |

## 9.7 Lighting tests

| ID | Call | Expected state |
| --- | --- | --- |
| LIGHT-001 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 100 })`, `sim.debug.lightRadius()` | Radius is 8.0. |
| LIGHT-002 | `sim.debug.setPlayerState({ lanternOn: false, fuel: 100 })`, `sim.debug.lightRadius()` | Radius is 0. |
| LIGHT-003 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 0 })`, `sim.debug.lightRadius()` | Radius is 0. |
| LIGHT-004 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 25 })`, `sim.debug.isSafeTile` at player center tile | True. |
| LIGHT-005 | `sim.debug.setPlayerState({ lanternOn: true, fuel: 24.999 })`, `sim.debug.isSafeTile` at player center tile | False. |
| LIGHT-006 | `sim.debug.setPlayerState({ covered: true, lanternOn: false })`, `sim.debug.visibleRange()` | Range is 3. |
| LIGHT-007 | `sim.debug.setPlayerState({ covered: false, lanternOn: false })`, `sim.debug.visibleRange()` | Range is 6. |

## 9.8 Perception tests

| ID | Call | Expected state |
| --- | --- | --- |
| PERC-001 | Set player lit with fuel 50, place Hollow within light radius plus 2, line of sight clear | Detection seen is true. |
| PERC-002 | Set player off, covered, place Hollow 3 tiles away with line of sight | Detection seen is true. |
| PERC-003 | Set player off, covered, place Hollow 3.5 tiles away with line of sight | Detection seen is false. |
| PERC-004 | Set player off, uncovered, place Hollow 6 tiles away with line of sight | Detection seen is true. |
| PERC-005 | Set player walking, Hollow 5 tiles away, line of sight clear | Detection heard is true. |
| PERC-006 | Set player sprinting, Hollow 10 tiles away, line of sight clear | Detection heard is true. |
| PERC-007 | Set player sprinting in underbrush, Hollow 12 tiles away, line of sight clear | Detection heard is true. |
| PERC-008 | Set player walking, Hollow 5 tiles away, tree between | Detection heard is false. |
| PERC-009 | `sim.debug.giveKey('A')` near Hollow with line of sight | Noise event radius 6 is processed and detection can occur. |
| PERC-010 | `sim.debug.giveEmber('E1')` near Hollow with line of sight | Noise event radius 4 is processed and detection can occur. |
| PERC-011 | `sim.debug.forceGateOpen()` with Hollow within 12 tiles and line of sight | Noise event radius 12 is processed and detection can occur. |

## 9.9 Hollow tests

| ID | Call | Expected state |
| --- | --- | --- |
| HOLLOW-001 | `sim.debug.setElapsed(89.999)`, advance 1 second | Hollow state is Waking. |
| HOLLOW-002 | `sim.debug.setHollowState('Waking', { x: 60, y: 40 })`, advance 8 seconds | Hollow state is Curious. |
| HOLLOW-003 | Set Hollow Curious, move toward waypoint for 1 second | Speed is approximately 2.4 tiles per second. |
| HOLLOW-004 | Set Hollow Investigating, move toward target for 1 second | Speed is approximately 3.2 tiles per second. |
| HOLLOW-005 | Set Hollow Searching, move toward target for 1 second | Speed is approximately 3.2 tiles per second. |
| HOLLOW-006 | Set Hollow Hunting, move toward target for 1 second | Speed is approximately 5.0 tiles per second. |
| HOLLOW-007 | Set Hollow in underbrush while Hunting, move 1 second | Speed is approximately 4.25 tiles per second. |
| HOLLOW-008 | Set Hollow Curious, make player detected | Hollow state is Investigating. |
| HOLLOW-009 | Set Hollow Investigating, make player detected | Hollow state is Hunting. |
| HOLLOW-010 | Set Hollow Hunting, no detection for 6 seconds | Hollow state is Searching. |
| HOLLOW-011 | Set Hollow Searching, advance 12 seconds with no detection | Hollow state is Curious. |
| HOLLOW-012 | Place player in safe zone, Hollow Hunting outside radius | Hollow waits outside safe radius. |
| HOLLOW-013 | Set fuel below 25 while Hollow waiting | Safe zone disappears and Hollow can enter. |
| HOLLOW-014 | `sim.debug.forceGateOpen()` with Hollow at y below 6 | Hollow moves to nearest reachable tile where y is 6 or higher. |

## 9.10 Gate and pickup tests

| ID | Call | Expected state |
| --- | --- | --- |
| GATE-001 | Set keysCollected 1, player near gate, `input.setInteract(true)`, advance 1 second | Prompt type is locked and charge stays 0. |
| GATE-002 | Set keysCollected 3, player near gate, `input.setInteract(true)`, advance 2 seconds | Gate opens. |
| GATE-003 | Set gateCharge 1, `input.setInteract(false)`, advance 0.5 seconds | Gate charge is 0. |
| GATE-004 | `sim.debug.forceGateOpen()`, then advance 10 seconds | Gate remains open. |
| PICKUP-001 | Place player within 0.75 tiles of Key A, advance 1 step | keysCollected becomes 1 and Key A collected is true. |
| PICKUP-002 | Place player within 0.75 tiles of Ember E1, advance 1 step | Fuel increases by 40 and E1 collected is true. |
| PICKUP-003 | Place player within 0.75 tiles of Key A, `sim.debug.collectNoiseEvents()` | Noise event radius 6 exists. |
| PICKUP-004 | Place player within 0.75 tiles of Ember E1, `sim.debug.collectNoiseEvents()` | Noise event radius 4 exists. |
| PICKUP-005 | Pick up Key A twice in separate steps | Key is collected only once. |

## 9.11 GameSim tests

| ID | Call | Expected state |
| --- | --- | --- |
| SIM-001 | `createSim({})`, start run, `sim.debug.simSnapshot()` | Initial state matches section 4.1. |
| SIM-002 | `sim.debug.setDawnRemaining(0)`, advance 1 step without win | State is failed with dawn fail. |
| SIM-003 | Place player and Hollow overlapping, advance 1 step | State is failed with caught fail. |
| SIM-004 | `sim.debug.forceGateOpen()`, set player y below 6, advance 1 step | State is won. |
| SIM-005 | Set player y below 6, gate open, Hollow overlapping, advance 1 step | State is won. |
| SIM-006 | Set dawn remaining 0, gate open, player y below 6, advance 1 step | State is won. |
| SIM-007 | `sim.retry(seed)`, then snapshot | All run state resets. |
| SIM-008 | Create sim with config `hollowEnabled: false`, run full route | Full route test can run without Hollow interference. |

## 9.12 Integration tests

| ID | Call | Expected state |
| --- | --- | --- |
| INTEG-001 | `createMockAudio()`, `createSim({ audio })`, trigger `pickup.key`, inspect audio calls | Audio calls include `sfx_key_pickup`. |
| INTEG-002 | `createMockAudio()`, trigger `hollow.wake`, inspect audio calls | Audio calls include `startLayer` for pressure and `sfx_hollow_wake`. |
| INTEG-003 | `createMockAudio()`, trigger `hollow.state_change` to Hunting, inspect audio calls | Audio calls include `sfx_hollow_hunt`. |
| INTEG-004 | `createMockAudio()`, trigger `player.fuel.low`, inspect audio calls | Audio calls include `sfx_fuel_low`. |
| INTEG-005 | `sim.debug.setDawnRemaining(59.999)`, advance 1 step, inspect HUD | Dawn warning is true. |
| INTEG-006 | `sim.debug.setPlayerState({ fuel: 19.999 })`, advance 1 step, inspect HUD | Fuel warning is true. |
| INTEG-007 | Set keysCollected 0, snapshot HUD | Objective text is `Find the bone keys`. |
| INTEG-008 | Set keysCollected 1, not near gate, snapshot HUD | Objective text is `Find the remaining bone keys`. |
| INTEG-009 | Set keysCollected 3, near gate, gate closed, snapshot HUD | Objective text is `Hold to open the gate`. |
| INTEG-010 | Set gate open, snapshot HUD | Objective text is `Cross the threshold`. |
| INTEG-011 | Set objective target off-screen, `sim.debug.setArrow(true, 90)`, inspect HUD | Arrow visible is true. |
| INTEG-012 | Set objective target on-screen, update arrow, inspect HUD | Arrow visible is false. |
| INTEG-013 | `loadRealMap()`, `createSim({ map, config with hollowEnabled false })`, scripted full route | State becomes won, all 3 keys collected, at least embers E1, E2, E4, E5 collected, dawn has not reached 0. |
| INTEG-014 | `loadRealMap()`, active Hollow, set player 60,6, keys 3, fuel 100, lantern on, Hollow Hunting at 60,20, hold E for 2 seconds then move north | Gate opens, player wins, no caught fail, Hollow does not enter safe zone while fuel is 25 or higher. |
| INTEG-015 | Cause fail, then `input.pressRetry()`, start run | New run has all initial values. |

## 9.13 Renderer and UX tests

| ID | Call | Expected state |
| --- | --- | --- |
| UX-001 | `renderSimFrame(sim, mockCanvas)` in title state | No exception. |
| UX-002 | `renderSimFrame(sim, mockCanvas)` in playing state | Canvas draw calls occur for visible tiles. |
| UX-003 | Set safe active, `renderSimFrame(sim, mockCanvas)` | Safe edge stroke occurs. |
| UX-004 | Set fuel below 25, `renderSimFrame(sim, mockCanvas)` | Safe edge is not drawn as active. |
| UX-005 | Set playing HUD fields, inspect DOM HUD | Timer, fuel bar, breath bar, key slots, and objective text are visible. |
| UX-006 | Set state won, inspect DOM | Win screen is visible and retry works. |
| UX-007 | Set state failed, inspect DOM | Fail screen is visible and retry works. |
| UX-008 | Set fuel below 20, inspect DOM HUD | Fuel warning uses pulse or shape, not only color. |

## 9.14 Map contract and performance tests

| ID | Call | Expected state |
| --- | --- | --- |
| CONTRACT-001 | `validateMap(loadRealMap())` | Map width 120, height 80, border impassable, gate gap valid, objects reachable, route targets met, underbrush clusters present, corridor heuristic passes. |
| PERF-001 | `createSim({})`, `advanceSim(sim, 480, idleInput)` | Simulation completes without exceptions. |
| PERF-002 | `createSim({})`, `advanceSim(sim, 480, scriptedInput)` in test environment | 28,800 fixed updates complete under 10 seconds. |
| PERF-003 | Run full route with pathfinding at 2 Hz | A* allocations do not grow unbounded across the run. |

## SCREENSHOTS

| Screenshot ID | Screen or state | Required visible elements |
| --- | --- | --- |
| SHOT-01 | Title screen | Dark forest background, lantern glow, title, control list, Begin the Night button. |
| SHOT-02 | Playing, safe start | Player in Start Clearing, lantern light, timer 08:00, fuel bar 50, breath bar 100, empty key slots, objective text. |
| SHOT-03 | Playing, onboarding Move | Small `Move` text near player or bottom-center. |
| SHOT-04 | Playing, onboarding Sprint | Small `Sprint` text near player or bottom-center. |
| SHOT-05 | Playing, onboarding Lantern | Small `Lantern` text near player or bottom-center. |
| SHOT-06 | Playing, objective arrow | Bone-white arrow at screen edge pointing off-screen objective. |
| SHOT-07 | Playing, key pickup | Key slot fills, small white pulse at key location. |
| SHOT-08 | Playing, ember pickup | Amber spark, fuel bar rises, lantern flame brightens briefly. |
| SHOT-09 | Playing, covered in underbrush | Player sprite lowered and darker, grass tufts over feet, ambient halo smaller if lantern off. |
| SHOT-10 | Playing, light safe zone active | Soft amber safe edge at light radius, Hollow waiting outside. |
| SHOT-11 | Playing, fuel below 30 | Safe edge flickers, flame icon flickers. |
| SHOT-12 | Playing, fuel below 20 | Fuel bar warning pulse, flame sputters, safe zone gone. |
| SHOT-13 | Hollow waking | Well mist rises, Hollow shape forms, cold vignette pulse if not visible. |
| SHOT-14 | Hollow curious | Hollow dim blue rim, slow drift near Dead Well. |
| SHOT-15 | Hollow investigating | Hollow upright, leans toward last known position, one eye brighter. |
| SHOT-16 | Hollow searching | Hollow circling motion, head sweeps, faint ripple around feet. |
| SHOT-17 | Hollow hunting | Bright eyes, stretched silhouette, cold vignette pulse, fast lurch. |
| SHOT-18 | Gate locked prompt | Gate visible, gray bone key icon, text `Sealed (x / 3)`. |
| SHOT-19 | Gate ready prompt | Bright bone key icon, text `Hold E to open`, circular progress ring. |
| SHOT-20 | Gate opened | Light leaks through gap, threshold glow appears, text `The gate is open`. |
| SHOT-21 | Dawn below 60 seconds | Timer pulses gold, top edge gains dawn glow, dial glows. |
| SHOT-22 | Win screen | Dawn light, text `You crossed before dawn.`, `Time: mm:ss`, Play again. |
| SHOT-23 | Caught fail screen | Black tendrils consume screen, text `The Hollow found you.`, `Press R to retry`. |
| SHOT-24 | Dawn fail screen | Dawn Gold flood, text `Dawn came before you escaped.`, `Press R to retry`. |
