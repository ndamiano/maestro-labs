# 8. DEBUG API

Exposed only when running with `?test=1`: `window.__game = core`, `window.__content = content`, `window.__world = core.world` (read-only generated definitions). Never attached on normal URLs.

**8.1 Player inputs as functions** (production core API — tests drive the game through these):

`setMoveInput(dx, dy)` · `interactDown()` · `interactUp()` · `openShop(shopId)` · `closeShop()` · `buyItem(shopId, itemId)` · `sellOne(shopId, resourceId)` · `sellStack(shopId, resourceId)` · `sellAll(shopId)` · `openLedger()` · `closeLedger()` · `toggleBuild()` · `selectBuildItem(instanceId)` · `selectPlacedItem(instanceId)` · `rotateBuildItem()` · `setBuildAnchor(x, y)` · `placeBuildItem()` · `removePlacedItem(instanceId)` · `sellBuildItem(instanceId)` · `assignSpecimen(buildingId, instanceId, slotIndex, resourceIdOrNull)` · `setSettings(partial)` · `saveGame()` · `loadGame(data)` · `newGame()` · `setPaused(bool)` · `update(dt)` · `init()`

**8.2 Test harness helpers** (`tests/harness/headless.js`; all calls used by §9):

`createHeadlessGame({ seed, runtimeRng, saveAdapter }) → core` · `advance(game, seconds, step = 0.016)` · `getEvents(game) → [events]` (recorded event log) · `interactFor(game, seconds)` (interactDown + advance + interactUp) · `releaseInteract(game)` · `teleport(game, x, y)` (test-only; uses `debug.teleport`) · `walkTo(game, x, y)` (BFS + real movement updates) · `findPlaceableTile(game, buildingId, itemId, rotation) → {x,y} | null`. `MockRNG(values)` per engineering (queue of `next()` values; `range`, `int`).

**8.3 Debug state functions** — one direct-state reach per gameplay system (test-only; not part of production behavior; no-op-safe):

| System | Functions |
| --- | --- |
| Player | `debug.setCoins(n)` · `debug.teleport(x, y)` · `debug.setScene("world"|"home"|"museum")` (places player at the door) |
| Inventory | `debug.giveResource(resourceId, n)` · `debug.clearInventory()` · `debug.fillInventory()` (all 10 slots at stack limits) |
| Nodes | `debug.setNodeState(nodeId, { empty?, count?, charges?, respawn? })` · `debug.fillAllNodes(resourceId?)` (all nodes of a type, or all) |
| Fishing | `debug.setFishing(spotId, "casting"|"waiting"|"biteMeter", progress = 0)` · `debug.setFishCooldown(spotId, s)` |
| Shops | `debug.setSupply(shopId, v)` · `debug.setCumulativeSold(shopId, n)` |
| Build | `debug.giveFurniture(itemId)` (add to buildInventory, `hasBeenPlaced:false`) · `debug.forcePlace(buildingId, itemId, x, y, rotation)` (bypasses `canPlace`, records placed + display slots) · `debug.clearFurniture(buildingId)` (all placed → buildInventory, `hasBeenPlaced:true`, specimens unassigned) |
| Museum | `debug.collectAll()` (all `collection` true + `specimen:unlocked` events) |
| Goals | `debug.setGoalComplete(goalId, bool)` (test-only latch set; `true` grants reward/unlock once) |
| Scores | `debug.readScores() → { home, museum }` |
| Save | `debug.saveNow()` · `debug.loadFresh()` · `debug.resetAll()` |
| UI | `debug.toast(text, type)` · `debug.openSettings()` |
