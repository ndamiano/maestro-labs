# BUILD SPEC — *Isle of Gilt* (open-world island treasure hunt)

## 0. SCOPE

### 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Open world (continuous, seamless, free-roaming play area) | §1.2 world extent, `main.js` camera, `world.js` |
| Explore an island | §1.2 biome layout, §3.1 island geometry, `world.js` generation |
| Find treasure | §4.3 treasure rules, `treasure.js`, §4.4 progression |

Elevating requirements added (good version obviously needs these):

| Requirement | Where it lives |
| --- | --- |
| Title screen and end screen (game needs an arc) | §7, `main.js` state machine |
| Compass hint + minimap (finding treasure is the loop; it must be playable) | §4.3, `hud.js`, `map.js` |
| Stamina + dash (movement identity; makes travel fun) | §4.1, `player.js` |
| Day/night cycle (open world needs a living clock) | §4.5, `main.js` loop |
| Named NPC wanderers with hint bubbles (an island without life feels empty) | §5, `entities.js` |
| Tiered treasure + a gated finale (progression and a win state) | §4.4, `treasure.js` |
| Procedural audio (no assets allowed in this build) | §6 |

### 0.2 Tiers

| Tier | Features |
| --- | --- |
| T1 — must ship | Title → play state machine; generated island (biomes, water, features); collision; player move/dash/stamina; 115 chests + seeded loot; points/relics; compass; minimap map+; HUD; day/night tint; audio recipes; end card; seed-deterministic generation |
| T2 — should ship | 9 named NPCs with wander + hint bubbles; cave + vault; shimmer-coin event; relic quest lines; toasts; compass "far" state |
| T3 — polish | Confetti ending, woodwind ambience, screen-space sun/shadow, vignette, stamina bar easing, title art animation |

## 1. CONVENTIONS

### 1.1 Units, axes, frames
- **Tile = 10 px** in world space. `x` right, `y` down. Positions are floats in **tile units** (e.g. island center = (100,100)).
- Character: body 0.8×1.2 tiles; shadow ellipse 0.9×0.4 tiles.
- World: **200×200-tile island** (2000×2000 px). Everything outside the water mask is deep water.
- Fixed timestep: **1 tick = 1/60 s**, max **5 ticks per frame**, leftover accumulated. One draw after ticks.
- Speeds in **tiles/sec**; radii in tiles.

### 1.2 Important conventions (all agents)
- **Biome bands** by elevation `h`: `h ≤ -0.06` deep, `h ≤ -0.02` shallow, `h ≤ 0.02` sand, `h ≤ 0.28` grass, `h ≤ 0.52` forest, `h ≤ 0.72` rock, else snow. Elevation = 1 − d²/46 − 0.16·noise, where d = tile distance from center and noise is value-noise from the seeded hash (smoothed 3×3).
- **Solid tiles:** deep, shallow, rock-band cliffs at h > 0.8, cave walls. **Solid features:** every tree and rock block. Cave floor and vault room are passable.
- **Gate:** sealed treasure gate on the **east beach** at tile (168,100) (generator finds nearest sand tile and records it). Sealed = solid on its tile + 2 neighbors to the west; open = passable.
- **Cave:** entrance on the **north beach** near x=100 (generator places it), a 1×12-tile rock corridor straight down into a 5×4 vault room with a torch and the Vault chest.
- **Day/night:** `timeSec` counts play seconds; `phase = (timeSec mod 240) / 240`; night = phase ∈ [0.5, 0.75).
- **Loot values:** coin 10 pts, gem 50 pts, relic 500 pts.
- **Gate rule:** opens permanently when `points ≥ 2500` AND `relicsCollected ≥ 3`. Opening toasts + pings the gate on the minimap.
- One random source: `RNG.next()` (mulberry32) inside `ctx.rng`. All generation and loot consume it in a fixed order: island noise → features → NPCs → chests → coins. No other randomness anywhere.
- Chest IDs `C001…C115`, NPC IDs `N01…N09`, coin IDs `K01…K30`.

## 2. CONTRACTS

### 2.1 File layout
- **`index.html`** — canvas (`#game`, 900×600, centered, letterboxed) + all DOM HUD elements; loads `main.js` only.
- **`main.js`** — builds `window.__game` (ctx), state machine (title/play/ending), fixed-timestep loop, day/night tint draw, camera transform, screen draw order: island canvas → water sparkle → features → coins → NPCs → chests → player → effects → tint/vignette.
- **`rng.js`** — `mulberry32(seed)`, `hash2i(x,y,seed)→[0,1)`; exports the single RNG.
- **`input.js`** — key set/clear on `keydown/keyup` (WASD/arrows/Space/E/M/C/N), writes to `ctx.input`; exposes `setMove`/`setAction` helpers used by debug.
- **`world.js`** — `buildIsland(seed)` (tiles, features, NPCs, chests, coins, cave, gate placement; returns island bitmap canvas 2000×2000 at 10px/tile), `isPassable(tx,ty)`, `collideCircle(px,py,r)→{x,y}` (axis-separated against solid tiles + solid features + sealed gate).
- **`player.js`** — `updatePlayer(dt)` movement/dash/stamina, `interact()` (opens chest within 1.2 tiles), player state + draw.
- **`entities.js`** — NPC wander/look/hint rules, coin bob, shimmer-wave spawn/despawn event, entity draw.
- **`treasure.js`** — chest open/loot, `nearestChestTarget()`, compass rule, gate check, ending trigger, relic quest lines.
- **`map.js`** — minimap render + `zoomAt()` wheel zoom.
- **`audio.js`** — Web Audio synth per §6; `Sfx.play(name)`, `Sfx.ambient(phase, nearWater)`, `Sfx.muted`.
- **`hud.js`** — DOM HUD updates (points, relic pips, stamina, clock, compass text, toasts, title/end overlays, map toggle).

### 2.2 Global context
`window.__game` (also `ctx` in all files) — plain object:
```
{ state:'title'|'play'|'ending', timeSec:0, points:0, chestsOpened:0,
  player:{x:0,y:0,vx:0,vy:0,dir:0,stamina:100,dashing:0,facing:'down',dead:false},
  input:{moveX:0,moveY:0,dash:false,interact:false,mute:false},
  rng:mulberry32(seed), seed:1,
  island:{canvas, tiles, features:[], gate:{x,y,open:false}, cave:{entrance:{x,y}, vault:{x,y}}},
  chests:[], coins:[], npcs:[], effects:[],
  dayPhase:0, night:false, muted:false, waveTimer:0,
  gateOpen:false, ending:false, ended:false }
```

### 2.3 File specifics (signatures + minimal rules)
- **rng.js** `mulberry32(seed)→next():[0,1)`; `hash2i(tx,ty,seed)→[0,1)` (deterministic per tile — used only for island noise).
- **world.js**
  - `buildIsland(seed)`: clears arrays; computes 200×200 tiles from §1.2; places **60 trees** (0.4-tile trunk + 0.8-radius canopy, on grass/forest), **18 rock blocks** (0.7 radius, forest/rock band), each 1-tile pad cleared of other solids, ≥3-tile spacing; places **9 NPCs** at biome targets (3 sand, 2 grass, 2 forest, 1 rock, 1 snow — see §5) with 1-tile cleared pad; places **115 chests** sorted by biome: beach 40, grass 30, forest 25, rock 12, snow 4, cave 3, plus 5 hidden (attached to trees or the cave room) — each 1.0-tile pad; places **30 coins** in 8 beach clusters; carves cave + vault; finds gate sand tile. Records each record per §9.
  - `collideCircle`: try X move then Y move vs solid tiles in footprint, feature circles, sealed gate tiles.
- **player.js**
  - `updatePlayer(dt)`: speed = dashing>0 ? 2.6/0.15*0.15·(dt) burst ⇒ effective 17.3 t/s… **concretely**: dash moves 2.6 tiles over 0.15 s (17.3 t/s) else 3.2 t/s; `vx,vy` from normalized `ctx.input` × speed; `collideCircle`; stamina: drain 25/dash, regen 30/s to 100; dash only if stamina ≥ 20; `facing` from movement; `walkPhase += speed·dt` for animation.
  - `interact()`: nearest open-able chest within 1.2 tiles → `treasure.openChest(chest)`.
- **entities.js**
  - NPC: `timer` counts down; on 0 pick `timer ∈ [2,5]` and new `tx,ty` within 4 tiles (passable), else `state:'look'` 1–2 s; `dir` = angle to target; walk speed 1.1 t/s; hint bubble when `dist(npc,player) < 2` and `hint` truthy.
  - Shimmer wave: `waveTimer` starts 90, counts down; at 0 spawn 12–16 coins on sand tiles within 20 tiles of player x (beach arcs), each `life:20`; every frame decrement `life`, despawn at 0, reset `waveTimer = 90 + 30·next()`.
  - Coin: `phase += dt` bob; collect radius 0.7 of player → `treasure.collectCoin`.
- **treasure.js**
  - `openChest(c)`: `c.opened=true`, `chestsOpened++`, loot roll: `r<0.5`→1–3 coins (+10 each), `r<0.8`→1–2 gems (+50), else 1 relic (+500, adds to `ctx.relics`, toast with name); if `c.relic` is a quest relic → toast its quest line (§5); check gate; if `c.isVault` → `ending=true`, `state='ending'`, Sfx `end`.
  - `nearestChestTarget()`: nearest unopened chest ≤ 64 tiles → `{x,y,dist,far:false}`; none → nearest quest-relic-bearing chest → `{x,y,dist,far:true}`.
  - `checkGate()`: if `!gateOpen && points≥2500 && relics≥3` → `gateOpen=true`, `island.gate.open=true`, toast "The treasure gate is open!", Sfx `gate`, minimap ping.
- **map.js** `zoomAt(px,py)`: `mapZoom = clamp(mapZoom·(1.25 or 0.8), 1, 3)` anchored at cursor; map button toggles a 240×240 enlarged panel.
- **main.js** `start()`: from title → `state='play'`, HUD title hides. `step(dt,n)`: n×(update(dt); ) then one draw. `setTime(t)`: `timeSec = t`, no draw. `seed(n)`: `ctx.rng = mulberry32(n); buildIsland(n); resetPlayer(); rebuild HUD`. `getState()`: JSON-clone of §2.2 minus canvas.

## 3. VISUAL SPEC

Bright, sun-soaked cartoon diorama: a small palm-dotted island rising from a flat cyan sea, everything rendered as simple layered shapes (ellipses, rounded rects, circles) with 2px dark outlines and a flat 8%-darker underside; the mood is postcard-bright and warm, with treasure reading as shiny yellow highlights and the day/night cycle gently shifting the whole palette without ever becoming dark or scary.

**Lighting (§3.1):** single sun top-right. Every solid feature casts a soft shadow ellipse offset (0.25, 0.35) tiles, 25% black. Global tint layer over the world: day = none; dusk (phase 0.45–0.5) = `#ff9c4a` at 12% (multiply blend); night (0.5–0.75) = `#202a55` at 38%; dawn (0.75–0.85) = `#ffcf8a` at 14%. Sun sprite: bright circle top-right, 4-ray halo; at night replaced by a crescent moon + 20 static stars. Cave interior is never tinted (torch circle of light, `#ffd98a` 25% radius 3). Screen-space radial vignette 10%.

**Texture/geometry tables (§3.2):**
- Tiles (flat fill, subtle 2% checker): deep `#1663b0` + slow sine sparkle lines; shallow `#3fb1d6`; sand `#ead9a5`; grass `#6cb657`; forest `#4b9248`; rock `#8b919c`; snow `#eef4f8`.
- Tree: trunk `#7a4a2b` (0.35×0.4), palm canopy = 5 leaf ellipses `#3f8f3f`/`#57ab4f`, coconut dots. Rock: rounded polygon `#9aa2ad`, top facet `#b7bec8`, crack lines. Chest: body `#8a5a2b`, lid `#a06a33`, gold trim + lock `#ffce54`; open = lid rotated −70°, inner glow `#ffe9a8`. Coin: `#ffd23f` circle, `#c99a1f` ring, 3px bob. Relic: 6-point star, per-relic hue (Coral Charm `#ff8f7a`, Moss Ring `#7bd88a`, Stone Idol `#c9cfd8`, Tidal Crown `#59d6ff`), 1px white sparkle sweep.
- Gate: two 1-tile stone pillars `#9aa2ad` + a golden chain ring spanning 2 tiles; open = pillars apart, chain lowered, glow. Cave entrance: dark `#1d2333` arch; room: grey stone walls, sand floor, torch = stick + flickering `#ffb547` flame.
- Island art (title): same generator seed 1, drawn at 0.35 scale with 3 drifting cloud ellipses.

## 4. GAMEPLAY SPEC

The core loop is **sprint → read hints (compass, minimap, NPC bubbles) → reach the next treasure → open it → get richer, further, rarer**: early beach chests teach the compass, mid-island treasure demands stamina management and dash, and the final gated beach gate forces a full-island crawl for 3 relics + 2,500 pts before the cave vault delivers the Tidal Crown and the end card. The most important feeling is *the pull of the compass finding its target*.

### 4.1 Player Controller
- WASD/arrows: 8-way, 3.2 t/s; Space = dash (2.6 tiles/0.15 s, stamina 25, needs ≥20); E = interact; M = big map; C = compass text on/off; N = mute.
- Collision per `world.collideCircle`, radius 0.4; blocked by solids + sealed gate (bump Sfx).
- Camera: lerps to player (factor 0.12/tick), zoom 10 px/tile × user wheel zoom (1–3) clamped to island.
- Stats: stamina 100 (bar, regen 30/s); `points`, `relics` {ids}, `chestsOpened`.

### 4.2 Movement & stamina (details)
Dash sets `facing` and leaves a 3-tile dust effect (0.3 s). Stamina bar flashes red below 25. Dashing into a wall cancels dash and refunds half cost.

### 4.3 Treasures & hints
- 115 chests, one-time: open with E within 1.2 tiles, lid anim 0.25 s, loot burst particles (gold sparks), Sfx `chest`/`relic`.
- Compass: HUD text `◆ bearing 042° (37t)` to nearest unopened chest ≤ 64 t; if none in range → `★ far` pointing to nearest quest relic chest. Off with C.
- Minimap: 150×150 always (bottom-left) + M for 240×240; draws island mask, player dot (N-rotating), chests (yellow) if < 40 t, NPCs (white), gate (red sealed / green open + pulse when open), shimmer coins (cyan).
- Shimmer wave event: §4.5, beached coin streak for 20 s.

### 4.4 Progression & finale
Points: coins 10, gems 50, relics 500; HUD shows `pts / 2500` until gate opens. Gate (east beach) sealed → open on `points ≥ 2500 ∧ relics ≥ 3` (toast + chime). Cave north side → vault chest → Tidal Crown relic + **ending**: confetti 2 s, end card (points, chests opened, play time), "New Island" → `seed(random from RNG.next())` → `buildIsland`.

### 4.5 Day/night & events
240 s cycle §1.2; night = moon, stars, tint, no gameplay penalty (keep it friendly) but ambient waves soften and a night-cricket blip recipe plays. Shimmer wave §4.3.

## 5. CHARACTERS

A cast of nine tiny, big-eyed island sprites (round body 0.8 tiles, two-dot eyes, blush, 3-frame idle bob + 4-frame walk leg shuffle, directional by `facing`) — cute, expressive, zero menace — plus the player: a straw-hatted explorer in a teal shirt who walks with a light 2-frame bob and a dash pose (lean + arm back).

### 5.1 NPCs (roster — one per record, placed per §1.2 biome targets)
| id | name | biome | hint line |
| --- | --- | --- | --- |
| N01 | Gull | sand, west | "Coins wash up where the waves give up!" |
| N02 | Coral | sand, west | "The Coral Charm is on the west shore." |
| N03 | Pearl | sand, east | "The gate loves 2,500 and three relics." |
| N04 | Mossy | grass, south | "The Moss Ring sleeps in the southern green." |
| N05 | Bark | forest, east | "The Stone Idol stands in the eastern stone." |
| N06 | Fennel | forest, north | "Listen… the sea carved a throat in the north." |
| N07 | Pebble | rock, north-east | "Old rock keeps old things." |
| N08 | Wisp | snow, peak | "I am the isle's spark. The Tidal Crown rests in the vault." |
| N09 | Kite | sand, south | "Dash hard, then rest — the beach is your friend." |

Animation pieces: walk (legs 4 frames), idle bob (3), look (eye offset to `dir`, 1 s), hint (bubble pop 1.5 s, one-shot per 20 s per NPC).

## 6. AUDIO (Web Audio API, all synthesized)

Master gain 0.8. Table: recipe = waveform, frequency(s), duration, envelope.

| Sound | Recipe | Plays when |
| --- | --- | --- |
| click | square 440 → 660, 0.08 s, exp decay 0.06 | any button |
| step | sine 160, 0.03 s, tri env 0.02/0.02 | every 0.3 s of movement |
| dash | sawtooth 300→90, 0.15 s, linear out | dash start |
| bump | square 90, 0.08 s, decay 0.06 | wall collision (min gap 0.2 s) |
| chest | triangle 520, 0.12 s, then 780, 0.12 s | chest opens |
| coin | sine 880→1320, 0.1 s, ping env | coin/gem collected |
| relic | triangle arpeggio 523/659/784, 3×0.1 s | relic found |
| gate | saw 130→65, 0.8 s + triangle 261→523 swell | gate opens |
| end | triangle fanfare 523/659/784/1046, 4×0.15 s | ending begins |
| wave | lowpass noise burst 1.2 s, gain swell | every 4 s near water (ambient) |
| cricket | square 2400, 2×0.02 s | night, every 3 s |
| woodwind | sine 392 vibrato 4 Hz, 2 s, soft | play state, every 9 s (T3) |
| mute | — | N toggles `muted` (all gains → 0) |

## 7. UX (HTML/CSS only)
- **Title screen** (overlay): island art, title "ISLE OF GILT", "Set Sail" button, control list. Clicking `start`/button → play.
- **HUD top-left panel**: points `1,240 / 2,500` (gold text), 4 quest-relic pips (dim → filled), stamina bar (teal, flashes red <25).
- **Top-right**: clock (sun/moon icon + `10:40` from dayPhase), compass line, day dot.
- **Bottom-left**: 150×150 minimap. **Bottom-right**: button row — Map (M), Compass (C), Mute (N), each with key label; active state highlighted.
- **Toast stack** (top-center): slide-in cards, auto-hide 3 s, max 3; used for relics, gate, quest lines, gate hint when player crosses 2,000 pts.
- **Ending overlay**: dark veil, "THE TIDAL CROWN RECOVERED", stat lines (points, chests, time), "New Island" button → reseed + rebuild + state play.
- **Help hint** (first 10 s): fading one-liner "WASD move · Space dash · E open · M map".

## 8. DEBUG API — `window.__game`

| Call | Does | Returns |
| --- | --- | --- |
| `start()` | title → play (no click) | `{state}` |
| `step(dt, n)` | n synchronous ticks of `dt` s, then one draw | `{state, timeSec, ticks:n}` |
| `setTime(t)` | sets `timeSec = t`, no draw | `{timeSec}` |
| `seed(n)` | reseeds the one RNG, rebuilds island/chests/NPCs/coins/cave/gate, resets player & scores | `{seed:n, chests:115, npcs:9}` |
| `getState()` | plain-data clone of §2.2 (canvas excluded) | state object |
| `move(x, y)` | persistent input direction (normalized; 0,0 stops) | `{moveX, moveY}` |
| `dash()` | one dash action (same as Space) | `{stamina, dashing:bool}` |
| `interact()` | one E action | `{opened:chestId\|null}` |
| `mapOn(b)` | toggle big map | `{mapOpen}` |
| `muteOn(b)` | toggle mute | `{muted}` |
| `openChestAt(x, y)` | force-open nearest chest within 1.2 t of (x,y) | `{id, loot}` |
| `addPoints(n)` | adds points, runs gate check | `{points, gateOpen}` |
| `giveRelic(k)` | adds relic k of {coral,moss,stone,crest}, runs gate check | `{relics, gateOpen}` |
| `setGate(open)` | force gate state | `{gateOpen}` |
| `spawnNpc(kind, x, y)` | places an NPC (kind = roster name) at passable spot | `{id, x, y}` |
| `setStamina(v)` | set stamina | `{stamina}` |

All calls synchronous, plain-data returns; `seed`+`step`+`move`/`dash`/`interact` is fully deterministic.

## 9. TESTS (run in order, fresh load)
1. `seed(1)` → `getState()` : `chests.length == 115`, every chest `{id, x, y, biome, opened:false}`; `npcs.length == 9`; `island.gate.open == false`.
2. `start(); getState()` → `state == 'play'`, `player.x in [99,101]`, `player.y in [99,101]`, tile under player is sand, `points == 0`, `chestsOpened == 0`.
3. `seed(7), setTime(20)` → `getState()` : `dayPhase ≈ 20/240`, `night == false`, `timeSec == 20`.
4. `seed(7), move(1,0), step(1/60, 190)` → `getState()` : `player.x > 10.1` (≈ 100 − 3.2·(190/60)), `stamina == 100` (no dash used).
5. `setStamina(100), dash(), step(1/60, 10)` → `stamina == 75`, `dashing == false`, `player` moved ≈ 2.6 t along last `move` direction from check 4.
6. `seed(11), openChestAt(nearest beach chest x,y)` → `{loot}` non-empty, `chestsOpened == 1`, `points ≥ 10`, that chest `opened == true`.
7. `seed(11), addPoints(2500), giveRelic('coral'), giveRelic('moss'), giveRelic('stone')` → `gateOpen == true`, `island.gate.open == true`; then `setGate(false)` → sealed again; walk-into-gate check: `move` toward gate then `step(1/60, 200)` → player `x` stays ≥ gate `x − 1.5`.
8. `seed(11), setGate(true), openChestAt(cave vault x,y)` → `relics` contains `crest`, `ending == true`, `state == 'ending'`.
9. `seed(13), spawnNpc('Mossy', 95, 95), step(1/60, 600)` → that NPC `x,y` differ from spawn by > 1 tile and ≤ 22 tiles.
10. `seed(13), setTime(150), step(1/60, 1)` → `night == true`, `dayPhase ≈ 0.625`.
11. `seed(15), step(1/60, 5400)` (90 s ×60) → a shimmer coin exists with `life ∈ (0, 20]` within 20 t of player x on a sand tile, then another `step(1/60, 1300)` → all `life ≤ 0` coins removed.
12. `muteOn(true)` → `getState().muted == true`; `mapOn(true)` → `mapOpen == true`.

**SCREENSHOTS (human-verified):**
| Screen/state | A person must see |
| --- | --- |
| Title | Island art + "ISLE OF GILT" + Set Sail button |
| Play, day, center | Cyan sea, sand ring, green island, palm shadows, player + minimap + HUD panel |
| Night (check 10) | Indigo tint, crescent moon, stars, dimmed palette |
| Open chest (check 6) | Lid open, gold spark burst, toast with loot name |
| Gate sealed (check 7) | Stone pillars + golden chain on east beach, minimap dot red |
| Gate open | Pillars apart, chain lowered, green minimap pulse |
| Cave (check 8) | Dark arch on north beach, lit vault room, torch |
| Ending (check 8) | Confetti + end card with stats + New Island |

## 10. BUILD ORDER
1. `rng.js` + `index.html` skeleton + canvas/ctx bootstrap (state `title` blank).
2. `world.js` generation + island canvas + `isPassable`/`collideCircle` (verify checks 1, 2).
3. `main.js` loop/camera/draw + `player.js` (check 4, 5) + `input.js`.
4. `treasure.js` chests/loot/gate + `hud.js` (checks 6, 7, 8).
5. `entities.js` NPCs/coins/event (checks 9, 11) + `map.js`.
6. `audio.js` (mute check 12) + day/night tint (check 10) + title/ending overlays.
7. T2/T3 polish: compass far-state, toasts, confetti, ambience, shadows, vignette.
8. Full §9 regression pass + §A re-audit.

## 11. DEFINITION OF DONE
- **Generation & world**: 115 chests/9 NPCs/30 coins/cave/gate placed, deterministic per seed, collision correct, island canvas renders.
- **Player & movement**: 8-way 3.2 t/s, dash/stamina exact values, camera lerp + zoom, all debug moves work.
- **Treasure loop**: open→loot→points→relics→gate→vault→ending all reachable; economy values exact (§1.2).
- **Systems**: day/night phases, shimmer event, compass/minimap, toasts.
- **Audio**: every §6 recipe plays on its rule, mute works.
- **UX**: title, HUD, minimap, ending screens match §7; keyboard + buttons both work.
- **Determinism & tests**: §9 all pass; same `seed`+`step` sequence twice → identical `getState()`.

## A. SANITY
- **Fields on records**: every field a rule reads/writes (`opened, x, y, biome, stamina, dashing, points, gateOpen, life, hint, dayPhase, night, mapOpen, muted, ending, relics, waveTimer, facing, walkPhase, tx, ty, timer, dist`) is declared on §2.2 or §9 record shapes → **closes**.
- **Places/kinds by generator**: beach/grass/forest/rock/snow/sand clusters (buildIsland), cave + vault (carved), gate (searched), 9 NPCs (roster targets), 115 chests, 30 coins → every named place/kind has a placer → **closes**.
- **Consumables vs demand**: stamina demand ≤ 25/dash, regen 30/s → sustainable; points: 115 chests ≈ 1,000 (coins) + 500 (gems) + 6,000 (12 relics) ≈ 7,500+ ≥ gate 2,500, and ≥ 25 relics-equivalent needed never exceeds 12 placed (3 required) → **closes**.
- **Timing pairs**: shimmer spawn 90 s ≫ despawn 20 s (no overlap); night 120 s > cricket 3 s & wave 4 s cadence; dash 0.15 s × 17.3 t/s = 2.6 t exact; cave vault 45 t ÷ 3.2 t/s ≈ 14 s, stamina covers; step(1/60, 190) = 3.16 s × 3.2 = 10.1 t matches check 4 → **closes**.
- **Test calls ⊆ §8**: start, step, setTime, seed, getState, move, dash, interact (unused but listed), mapOn, muteOn, openChestAt, addPoints, giveRelic, setGate, spawnNpc, setStamina — all present in §8 → **closes**.
- **Fix made during audit**: compass "far" fallback now explicitly targets quest-relic chests only (edited §4.3/§2.3 `nearestChestTarget`), so the rule never reads an undefined target.