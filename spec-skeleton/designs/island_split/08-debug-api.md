# 8. DEBUG API

Headless, driven by `harness.js`. Every function a §9 test calls is defined here. `debug.newGame(seed)` returns `{ game, level, state, events }`.

**Lifecycle / time:** `debug.newGame(seed=123)`, `debug.advance(seconds, dt=1/60)`, `debug.waitFor(cond, maxSeconds=60)`, `debug.state()` (live `STATE`), `debug.level()` (live `LEVEL`), `debug.snapshot()` (deep copy of `STATE`).

**Inputs (as functions):** `debug.input.move({up,down,left,right})`, `debug.input.clear()`, `debug.input.run(bool)`, `debug.input.map(bool)`, `debug.input.interact(bool)`, `debug.pressInteract(durationSeconds)`, `debug.openMap(durationSeconds)`, `debug.moveTowards(tile, {waitSeconds, requireLowTide})` (pathfinding controller: A* with current water level + blockers, waits/retries for tide/blockers, follows by input), `debug.interactWith(cache, {advance, moveTowards})` (nearest passable tile within 1.5 of `cache.interact`, hold interact for `channelTime + 0.2 s`).

**Pure queries:** `debug.depth(x,y,waterLevel)`, `debug.passable(x,y,waterLevel)` (uses live `LEVEL.blockers`).

**Per-system reachers (one function per system):**
- Tide: `debug.tide.set(time)`, `debug.tide.setLevel(level)`, `debug.tide.setState(state)`, `debug.tide.level()`, `debug.tide.state()`.
- Player/movement: `debug.player.set(x,y)`, `debug.player.setStamina(n)`, `debug.player.setFacing(dir)`, `debug.player.state()`.
- Safe displacement: `debug.safeDisplacement.force()`.
- Fog: `debug.fog.reveal(x,y,r)`, `debug.fog.clear()`, `debug.fog.isRevealed(x,y)`.
- Landmarks: `debug.landmarks.discover(id)`, `debug.landmarks.clear()`, `debug.landmarks.discovered()`.
- Caches/keys/clues: `debug.caches.open(id)`, `debug.caches.sealAll(bool)`, `debug.caches.state()`, `debug.keys.set(n)`, `debug.clues.set(n)`, `debug.clues.state()`, `debug.clues.overlap()` → `{count, includesVault}`, `debug.clues.validate()` → `{ok, overlapCount, vaultInOverlap, distances[]}`, `debug.clueDistance(keyId)`.
- Coins: `debug.coins.add(n)`, `debug.coins.set(n)`, `debug.coins.collectAll()`, `debug.coins.state()`, `debug.coins.rank(n)`.
- Vault: `debug.vault.setKeys(n)`, `debug.vault.open()`, `debug.vault.state()`.
- Objectives/progress: `debug.objectives.current()`, `debug.progress.set(state)`, `debug.complete()`.
- Level: `debug.level.setTile(x,y,elev)`, `debug.level.blockers.add(i)`, `debug.level.blockers.remove(i)`, `debug.level.blockers.clear()`, `debug.level.summary()`, `debug.level.validate()`, `debug.level.reachableFrom(start, {waterLevel, removeBlockers})`.
- Events: `debug.events.list()`, `debug.events.last(name)`, `debug.events.clear()`.
- Audio (stub context in tests): `debug.audio.map(event)` → SFX name, `debug.audio.play(name)`, `debug.audio.poolSize()`.
