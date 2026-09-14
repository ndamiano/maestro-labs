# 1. CONVENTIONS

## 1.1 Units, axes, frames

- **World unit**: tile. Tile size `24×24` px. Design resolution `960×540`; visible area ≈ `40×22` tiles.
- **Axes**: `x` → right, `y` → down. Origin `(0,0)` top-left. World is `120×120` tiles, coordinates `0..119`; pixel cell of tile `(x,y)` is `[24x, 24x+24) × [24y, 24y+24)`.
- **Positions**: actor positions are tile-space floats; tile `(x,y)` center = `(x+0.5, y+0.5)`.
- **Frames**: fixed timestep `dt = 1/60` s. `requestAnimationFrame` accumulator; max 6 steps per frame; a single passed `dt` is clamped to `0..0.1` as safety. `state.time` is seconds of unpaused simulation time.
- **Timers** in this document are seconds unless marked otherwise.

## 1.2 Important conventions

- **Origin/camera**: camera follows the player, never rotates, clamped to world bounds (world) or interior floor bounds (interiors):
  `cameraX = clamp(player.x*24 − 480, 0, 120*24 − 960)`, `cameraY = clamp(player.y*24 − 270, 0, 120*24 − 540)`.
- **System run order per fixed step** (all use the step’s `dt`):
  1. Player movement & collision
  2. Gathering (berry/mine progress)
  3. Fishing state machine
  4. Node respawn timers
  5. Fish-spot cooldowns
  6. Shop supply recovery
  7. Goal evaluation
  8. Event emission (batch)
- **The one random source**: `SeededRNG` (class in the contracts doc). Exactly two instances: `worldRng = SeededRNG(42)` — world generation only, at world (re)build; `runtimeRng = SeededRNG(43)` — all gameplay randomness (berry counts, bonus yields, wait times, yellow-zone rolls). `Math.random` is banned in production code.
- **Pause**: simulation paused in Title, Shop, Ledger, Settings, Completion modals. Not paused in build mode or interiors. While paused, `state.time` does not advance.
- **Controls** (keyboard + mouse; touch is cut):

| Input | Action |
| --- | --- |
| `W`/`A`/`S`/`D`, Arrow keys | Move (diagonals normalized) |
| `E` or left click | Interact (world); strike (fishing bite meter); place selected item (build mode) |
| `B` | Toggle build mode (interiors only; elsewhere → `invalid:action` + toast) |
| `C` | Toggle Ledger |
| `P` | Toggle Settings (T2 modal) |
| `Esc` | Close modal / cancel build selection / exit build mode |
| `R` | Rotate selected unplaced item 90° (build mode) |
| `X` or right click | Remove targeted placed furniture (build mode) |
| Mouse move | Set placement anchor tile (build mode) |
| Shift-click | Sell whole stack (shop Sell tab) |
