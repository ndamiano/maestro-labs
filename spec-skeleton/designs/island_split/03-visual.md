# 3. VISUAL SPEC

**The look — one paragraph.** *Island of the Hidden Hoard* is a **salt-light salvage chart**: a hand-inked island chart brought to life. Bright, clean, hand-painted, chunky, nautical, warm, and clearly readable — sunny, slightly weathered, inviting, never hostile. The island has warm sandy beaches, clear teal water, lush-but-readable jungle, sun-bleached stone ruins, rocky cliffs with strong silhouettes, and brass/rope/wood salvage props. The player is a careful salvager, not a combat explorer. It should read like a bright salvage chart, not a mysterious dark island; details decorate but never hide gameplay information. *(Ruled vs gameplay: no conflict — this is pure presentation over the same 2.5D world.)*

**Lighting and atmosphere.** Warm midday, single global light from the top-left, **no day/night cycle, no dynamic lighting, no post-processing, no full-screen blur, no dynamic weather**. Readability is carried by shape + text + color (never color alone): strong drop shadows make elevation legible; entities cast simple elliptical shadows; a light top-left highlight on tile tops. Avoid photorealism, dark horror tones, heavy fog, neon, and cluttered micro-detail.

**The space.** Fixed isometric camera (§1.1) over a 256×256 tile island ringed by an 8-tile ocean border. Elevation 0–5 renders as vertical offset (`screenY -= elevation * 18`) with top tile + side walls + shadows + edge highlights. **Diff 1 = small step lip (walkable); diff ≥2 = tall cliff face (darker face, vertical striations, jagged top, soft cast shadow, edge language that is never used for a walkable step).** Render order: (1) ocean background, (2) terrain tiles sorted by `tileX+tileY`, (3) side walls, (4) water overlays, (5) terrain details/props/caches/coins/landmarks, (6) player, (7) world effects (wakes, dust, sparkles), (8) UI overlay. Six sectors share one palette/tile/prop/shadow/water language and differ only by local ground color, accent, 1–2 motifs, one landmark, one cache prop, one short label. *(Ruled vs gameplay: "diff 1 walkable / diff ≥2 blocked" matches the §4.2 movement rule; "deep water impassable" matches §4.3 — carried, not new rules.)*

**Water & tide readability (gameplay-relevant rule carried):**

| Depth state | Condition | Appearance |
| --- | --- | --- |
| Dry | `depth <= 0` | Full terrain color, brightest, no overlay |
| Shallow | `0 < depth <= 1.0` | Pale teal overlay 30–40% alpha, slow ripple, terrain visible, small player wake |
| Deep | `depth > 1.0` | Darker blue 65–75% alpha, stronger/slower wave, terrain nearly hidden, no inner foam line |

Shoreline shows a thin foam line where water meets dry land. Trying to enter deep water → short blocked bump animation + soft thud (no damage). Low-tide moment: foam recedes, exposed shelves show wet sand + a thin darker "tide-line", low-tide coins visible, Gull Flats shelf clearly dry, vault cave floor reachable, map water lighter. High-tide moment: water darkens, shallow more opaque, elevation-0 tiles deep, elevation-1 shallow, player pushed to high ground, dial HIGH (double-wave, orange) — still safe, a planning problem not a monster.

**Recipe tables (from visual.md, carried whole):**

*Global palette:*

| Use | Hex | Note |
| --- | --- | --- |
| Parchment UI | `#F3E4C2` | map, panels, prompts |
| UI border | `#5B4632` | panel edges |
| Brass | `#D8A24B` | keys, buttons, interactive trim, channel ring |
| Ink | `#201812` | UI text on parchment |
| Player | `#FFFFFF` | player outline + marker |
| Shadow | `rgba(16,24,36,0.25)` | terrain/entity shadows |
| Ocean deep | `#0B2C47` | deep water + ocean border |
| Water mid | `#1D5F8E` | mid-depth water |
| Shallow water | `#7FD9D2` | passable shallow |
| Foam | `#FFF6E4` | shoreline, water edges |
| Sand | `#E7D0A5` | beaches, dry lowland |
| Jungle floor | `#7DB26A` | Palm Hollow base |
| Rock | `#A89B8A` | cliffs, ruins |
| Ruin stone | `#CFC3AC` | Sunken Ruins |
| Cliff cap | `#D9D1BE` | cliff tops |
| Key gold | `#FFC845` | keys, vault glow, completion |
| Coin gold | `#F2C14E` | coins |
| Low tide | `#45E0C6` | LOW state, ring 1 |
| Rising tide | `#FFD166` | RISING state |
| High tide | `#FF7A3D` | HIGH state + warning |
| Vault marker | `#E5484D` | exact vault marker (red reserved for this) |
| Open vault | `#FFC845` | vault ready/open |
| Hunt area | `#FF9F43` | map search areas |

Color meaning: gold/brass = treasure/positive/interact; teal/cyan = water/low/safe/ring 1; amber/orange = warning/high/search; **red = vault marker only**; gray/hollow = missing/sealed; white = player/foam.

*Clue ring style table (color + line style required; color alone is not enough):*

| Key | Landmark | Color | Line style | Canvas dash | Fill |
| --- | --- | --- | --- | --- | --- |
| 1 | Shipwreck | `#45E0C6` | solid | `[]` | `rgba(69,224,198,0.16)` |
| 2 | Gull Flats Lighthouse | `#9A7BFF` | long dash | `[12,8]` | `rgba(154,123,255,0.16)` |
| 3 | Palm Hollow Idol | `#8ADB6A` | short dash | `[4,8]` | `rgba(138,219,106,0.16)` |
| 4 | Sunken Arch | `#FF7AC0` | dash-dot | `[14,6,4,6]` | `rgba(255,122,192,0.16)` |

*Terrain tile recipe* (`makeTileCanvas(seed, sector, elevation, wet)` → 64×32 canvas): diamond path `(32,0)→(64,16)→(32,32)→(0,16)`; fill `shade(sectorPalette.ground, elevation*0.05)`; 14 noise specks via `mulberry32(seed)` (`rgba(0,0,0, 0.03..0.09)`); if `wet` overlay `rgba(18,68,94,0.16)`; stroke `rgba(31,24,18,0.24)`. Goal: soft hand-painted tile, not a crisp checkerboard.

*Water overlay recipe* (`drawWaterOverlay(ctx, depth, time, tileX, tileY)`): if `depth<=0` return; `isDeep = depth>1.0`; `ripple = sin(time*3.2 + tileX*0.4 + tileY*0.3)`; `alpha = isDeep ? 0.66+0.05*ripple : 0.28+0.08*ripple`; fill `isDeep ? rgba(12,47,74,α) : rgba(127,217,210,α)`; if not deep, stroke foam `rgba(255,246,228, 0.18+0.10*sin(time*4 + tileX + tileY))`.

*Map overlay* (§3 map, carried):
- Canvas `512×512`, `1 tile = 2 px`, parchment background, thin wood/brass border, **92% opaque (8% world visible)**, tile→map `tileToMap`.
- Layer order: (1) parchment, (2) revealed terrain, (3) unrevealed dark overlay `rgba(16,24,40,0.82)` + hatch `rgba(255,255,255,0.04)`, (4) current tide water, (5) high-tide flood preview (elev-0 revealed tiles, light-blue dashed hatch α 0.25, legend "Floods at high tide"), (6) sector labels, (7) hunt areas, (8) clue rings, (9) landmarks, (10) vault marker, (11) player, (12) legend (bottom-left, ≥10 px text).
- Revealed terrain map colors: Beach/lowland `#E7D0A5`, Jungle `#7DB26A`, Rock/ruin `#A89B8A`, Cliff top `#D9D1BE`, Cave/low shelf `#C9B48F`.
- Current water per revealed tile: `depth = max(0, waterLevel - elev)`; if `>0`: `isDeep = depth>1.0`; `alpha = isDeep?0.72:0.38`; color `isDeep ? rgba(11,44,71,1) : rgba(127,217,210,1)`.
- Landmark icons: triangle 10–12 px, parchment border, dark-ink glyph, label below; unique glyph per landmark (not color).
- Hunt area: orange dashed circle, radius 24 tiles, fill `rgba(255,159,67,0.12)`, stroke `#FF9F43`, dash `[10,8]`, question-mark/cache icon at center.
- Clue ring: annulus centered on landmark, `inner = max(0,D-6)*2`, `outer = (D+6)*2`; fill α 0.16, stroke 3 px, key-specific color+dash; `drawClueRing` uses `fill("evenodd")`; animate draw-on when added.
- Vault marker: **4 geometric clues → red X (`#E5484D`), two thick diagonals, pulse 1.0→1.12, label `VAULT`**; **5 keys + low tide → gold X + compass icon, label `OPEN` (`#FFC845`)**.
- Player marker: white arrow, black outline, points in movement direction, small idle pulse.
- Transition: open = parchment unfurls top→bottom + slight scale-up, 0.22 s, paper swish; close = folds back, 0.18 s, paper settle. Map must not obscure tide warnings.

*Sector identity tables (palette + motifs + landmark + cache, carried whole):*

**Driftwood Cove** — Sand `#E7D0A5`, Dune `#D8BC88`, Driftwood `#8A6E58`, Rope `#D7B98C`. Motifs: driftwood logs, loose planks, rope knots, sand ripples, gentle foam. Landmark **Shipwreck** = broken hull + tilted mast + anchor (strong 24-tile silhouette). Cache **Shipwreck barrel** = wooden barrel, brass band, rope closure, openable lid (first clearly interactable prop).

**Gull Flats** — Mudflat `#C8B298`, Wet sand `#DBC7A5`, Lighthouse white `#F5F0E1`, Lighthouse band `#2FA6A6`, Gull `#F7F3E8`. Motifs: flat mud, tide pools, gull shadows, exposed rock shelf, sparse grass. Landmark **Gull Flats Lighthouse** = white tower, teal horizontal bands, small lantern, 2-tile base (**no red on the lighthouse**). Cache **Low-tide rock shelf** = flat stone platform, tide pool, brass-edged rock hatch, seaweed; underwater at high tide, dry+openable at low tide.

**Palm Hollow** — Jungle floor `#7DB26A`, Palm leaf `#3E8C5A`, Root `#6B5A47`, Idol `#6FCF97`. Motifs: palm billboards (sparse, never hide terrain), root mats, fallen trunks, bright floor patches, soft leaf shadows. Landmark **Palm Hollow Idol** = carved pedestal, jade-green mask, moss. Cache **Root gate** = two thick roots over a 2-tile gap, rope tied to a root (rope is the only clearly interactable element), root-wrapped chest behind.

**Sunken Ruins** — Ruin stone `#CFC3AC`, Moss `#7AA96B`, Mosaic blue `#3E7BB0`, Coral `#E98A6D`. Motifs: broken columns, cracked floors, faded mosaics, small coral, shallow channels (abandoned, not haunted). Landmark **Sunken Arch** = broken arch, two pillar ends, missing span, mosaic detail. Cache **Movable stone column** = large mossy column with brass tide-key emblem, visually heavy, open niche behind.

**Cliffpath Ridge** — Rock `#A89B8A`, Cliff cap `#D9D1BE`, Eagle `#F2F2F2`, Wind accent `#EAF6FF`. Motifs: jagged rock, pale tops, thin path ledges, wind streaks, small eagle. Landmark **Cliffpath Eagle Rock** = tall jagged rock + white eagle, strong distance silhouette. Cache **Eagle Rock alcove** = stone chest in alcove, brass keyhole, rope trim, small ledge (a reward for travel, not a trap). Cliff edges clearly non-walkable where jump ≥2.

**Vault Point** — Reef `#E98A6D`, Cave rock `#5E6A72`, Treasure gold `#FFC845`, Water `#1D5F8E`. Motifs: reef rocks, cave mouth, coral branches, wet stone, golden glow. Landmark **Vault Point Reef** = coral cluster, curved outcrop, small cave opening behind. **Vault** = circular stone+brass door, five key slots around the edge, central tide lock, golden glow when low+all-keys, water swirl when sealed; large architectural door, distinct from all caches. Vault states: <5 keys = 5 hollow slots (gray/brass); 5 keys not low = partially submerged + wave icon; 5 keys + low = glows gold, slots fill, lock opens; opening = door swings/slides + light spills; open = treasure + golden compass rises.

*Props:*
- **Player** — human silhouette: oilskin coat, rope belt, small backpack, boots, **white outline**. Distinct from props (body, head, legs, motion).
- **Coins** — 10–14 px, gold, spiral/star mark, slow spin, light bounce, tiny sparkle; smaller and lower than keys; **not marked on the map**.
- **Tide Keys** — larger than coins, brass key with teal tide emblem, floats above cache, soft golden pulse; all five share one base design (sector shown by map clue + counter position, not by color).
- **Caches** — shared language (clear silhouette, brass tide-key emblem, prompt when near, channel ring while interacting, open state stays open) but unique shapes: 1 Barrel, 2 Rock shelf hatch, 3 Root-wrapped chest, 4 Stone column, 5 Alcove chest. Sealed = padlock icon + desaturated brass + "Sealed. Find the first Tide Key."; openable = brighter brass + prompt + ring; channel = brass ring fills clockwise.
- **Landmarks** — strong silhouette, 24-tile visible, unique shape + map glyph + short name. On discovery: brief golden outline + map stamp + map icon (triangle+glyph); after discovery a small brass pin above the object in-world.

*Typography / UI style:* UI = salvager's chart table — parchment panels, dark-wood borders, brass rivets, rope trim on important buttons, crisp modern icons. Display font `"Squada One","Arial Black",sans-serif`; UI font `"Nunito Sans","Trebuchet MS",system-ui,sans-serif`. Titles uppercase bold spaced; HUD labels short uppercase; prompts sentence case; objective one line (two max); map labels short uppercase ≥10 px. Text: on parchment `#201812`; on dark water `#FFF6E4` + dark outline; on gold `#201812`; contrast ≥4.5:1 for critical text.
