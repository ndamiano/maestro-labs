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
