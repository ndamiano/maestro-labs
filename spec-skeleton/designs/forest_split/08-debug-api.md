# 8. DEBUG API

Debug and test API is for tests and scripted playthroughs. The browser App must not use these functions for normal gameplay. They must not break normal sim behavior.

## 8.1 Test factory functions

| Function | Purpose |
| --- | --- |
| `createSim(options)` | Creates a sim with map, config, seed, audio, and input. Options may override defaults. |
| `createMockAudio()` | Returns an audio recorder with `play`, `startLayer`, `stopLayer`, `setPhase`, and `calls`. |
| `createMockInput()` | Returns an input object with functions from section 8.3. |
| `createMapFixture()` | Creates a small deterministic map for engine tests. |
| `loadRealMap()` | Loads `assets/map.json` as a map object. |
| `advanceSim(sim, seconds, inputFactory)` | Advances sim in fixed steps using an input factory that receives sim and returns an input frame. |
| `validateMap(mapJson)` | Runs the map contract validator and returns errors. |
| `renderSimFrame(sim, mockCanvas)` | Renders one frame to a mock canvas for renderer tests. |

## 8.2 Sim debug functions

| Function | Purpose |
| --- | --- |
| `sim.debug.setElapsed(seconds)` | Sets run elapsed time. |
| `sim.debug.setDawnRemaining(seconds)` | Sets dawn remaining time. |
| `sim.debug.setPlayerState(partial)` | Sets player fields such as pos, fuel, breath, lanternOn, keysCollected, breathLocked. |
| `sim.debug.setHollowState(state, pos)` | Sets Hollow state and position. |
| `sim.debug.setHollowTimers(partial)` | Sets Hollow stateTimer, lostTimer, waypointTimer, pathTimer. |
| `sim.debug.forceGateOpen()` | Sets gate open and applies threshold exclusion. |
| `sim.debug.forceGateClosed()` | Sets gate closed and resets charge. |
| `sim.debug.setGateCharge(seconds)` | Sets gate charge. |
| `sim.debug.addNoiseEvent(event)` | Adds a one-time noise event with x, y, radius. |
| `sim.debug.collectNoiseEvents()` | Returns queued noise events and clears the queue. |
| `sim.debug.giveKey(id)` | Marks a key collected and updates HUD. |
| `sim.debug.giveEmber(id)` | Marks an ember collected and adds fuel. |
| `sim.debug.setPickupCollected(id, value)` | Sets a key or ember collected flag. |
| `sim.debug.setObjectiveTarget(pos)` | Overrides objective target for arrow tests. |
| `sim.debug.setArrow(visible, angle)` | Sets arrow visible and angle. |
| `sim.debug.findPath(from, to, options)` | Runs pathfinding with player or Hollow predicate. |
| `sim.debug.nearestReachable(from, to, options)` | Runs nearest reachable fallback. |
| `sim.debug.hasLineOfSight(from, to)` | Checks line of sight. |
| `sim.debug.lightRadius()` | Returns current light radius. |
| `sim.debug.safeActive()` | Returns whether safe zone is active. |
| `sim.debug.isSafeTile(tx, ty)` | Returns whether a tile is currently safe for The Hollow. |
| `sim.debug.detect()` | Returns current perception detection result. |
| `sim.debug.simSnapshot()` | Returns a shallow snapshot of sim state for assertions. |
| `sim.debug.setRngSeed(seed)` | Resets sim RNG to a supplied seed. |

## 8.3 Player input functions

| Function | Purpose |
| --- | --- |
| `input.setMove(x, y)` | Sets movement direction, x and y are -1, 0, or 1. |
| `input.setSprint(value)` | Sets sprint held. |
| `input.pressLantern()` | Presses lantern toggle once. |
| `input.setInteract(value)` | Sets gate interact held. |
| `input.pressRetry()` | Presses retry once. |
