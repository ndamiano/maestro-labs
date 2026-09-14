# 1. CONVENTIONS

## 1.1 Units, axes, frames

- **Unit:** 1 tile = 1 meter = 1 world unit. Player and entity positions are tile-space floats.
- **Axes:** `x` increases right, `y` increases down (world and screen). Tile `(x, y)` occupies `[x, x+1] × [y, y+1]`; tile center is `(x+0.5, y+0.5)`. `tileX = Math.floor(player.x)`, `tileY = Math.floor(player.y)`.
- **Origin:** tile `(0,0)` is top-left. The island is inside an **8-tile ocean border** (tiles `0..7` and `248..255` on each axis are ocean, impassable).
- **Projection (isometric):** `TILE_W = 48 px`, `TILE_H = 24 px`, `HEIGHT_STEP = 18 px`. One tile = one meter; the visual tile is an isometric diamond.
  ```js
  const TAU = Math.PI * 2;
  const ISO = { tileW: 48, tileH: 24, heightStep: 18 };
  function isoToScreen(tileX, tileY, elevation, camX, camY, viewW, viewH, scale = 1) {
    const sx = (tileX - tileY) * (ISO.tileW / 2) * scale;
    const sy = (tileX + tileY) * (ISO.tileH / 2) * scale - elevation * ISO.heightStep * scale;
    return { x: viewW / 2 + sx - camX, y: viewH / 2 + 24 + sy - camY };
  }
  ```
- **Camera:** fixed isometric. Follows the player with slight smoothing and a small dead zone; keeps the player near center; clamps to island bounds; **no rotation, no free zoom**; scale `1.0` on standard screens, `0.85` below `800×480`.
- **Map space:** `1 tile = 2 px`, canvas max `512×512 px` (see §3 map).
  ```js
  function tileToMap(tileX, tileY, scale = 2) { return { x: tileX * scale, y: tileY * scale }; }
  ```
- **Frames:** fixed-step loop, 60 Hz accumulator, `dt = 1/60` s; clamp the accumulator to avoid spiral-of-death. The headless harness advances with a caller-supplied `dt`.

## 1.2 Important conventions

- **Units / axes / origin / camera / fixed-step:** as §1.1.
- **Order systems run (per `Game.update(dt)`), authoritative:**
  1. if `state.complete` → return
  2. `state.elapsedTime += dt`
  3. `updateTide(dt)`
  4. if current tile is impassable → `safeDisplacement()` → return
  5. `updateMovement(dt)`
  6. `updateStamina(dt)`
  7. if player tile changed → `updateFog()`
  8. `updateLandmarks()`
  9. `updateCaches(dt)`
  10. `updateCoins()`
  11. `updateVault(dt)`
  12. `updateObjectives()`
  (Ruling: step 4 runs immediately after tide and before movement, per engineering §8.1; the §2.2 layering list is the system *set*, the function order above is canonical.)
- **The one random source:** `rng = mulberry32(seed)` (§2.3 `core/rng.js`). Only `level/generator.js` draws from it, in this fixed order: (a) cache offsets for keys 2,3,4,5 (dx,dy each), (b) scattered coins per sector in fixed sector order. No gameplay `Math.random` (coin-pitch audio jitter is cosmetic only).
- **Controls table (merged):**

| Input | Action |
| --- | --- |
| W / ArrowUp | move up |
| S / ArrowDown | move down |
| A / ArrowLeft | move left |
| D / ArrowRight | move right |
| Shift | run (hold) |
| M **or** Right Mouse | open map (hold) |
| E / Enter | interact (hold) |

Right Mouse suppresses the context menu on the game canvas. Holding map open sets `input.map = true` and cancels any active channel.

- **Constants:** the authoritative numeric table is the **Core Constants record in §4**. The JS export object that mirrors it is `CONFIG` (§2.2).
