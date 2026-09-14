# 3. VISUAL SPEC

**Look.** Cozy Hand-Painted Pixel Diorama: the world is a small, lovingly arranged painterly diorama viewed from directly above — a miniature collector’s garden, a warm little village outside a small museum. Soft pixel shading, gentle color separation, low-to-medium saturation, warm earth tones as the base, bright but controlled resource accents, rounded shapes, small animation. **No hard black outlines** — use darker shaded edges, 1-pixel dark accents, light rim highlights, and soft drop shadows. It must never read as neon action, grim survival, loud-outlined cartoon, AAA 3D, or sterile vector UI.

**Lighting and atmosphere.** No day/night, no weather, no dynamic lighting, no parallax (cut list). Light is fixed and readable: soft baked shadows under every actor/node/furniture (1-pixel `#2E241B` at 25–35% alpha, elliptical/soft-rectangular, no hard black shadows); warm lamp/window glow in the Home; soft spotlight pools around display cases in the Museum; Tier-3 resources pulse with a slow emissive cycle of `1.5s` full cycle (no fast flashing; disabled under Reduce Motion). Painted sprite height is allowed (bushes/roofs may extend above their base tile) but must never imply a vertical axis, caves, ladders, or elevation.

**Space.** One continuous `120×120` outdoor map plus two interior scenes. Tile `24×24`; design resolution `960×540` (≈`40×22` tiles); nearest-neighbor scaling, no full-screen anti-aliasing. Soft transitions between zones; small overlapping decorations; paths visually connect the village to every resource zone; the perimeter reads as a natural 2-tile boundary (dark water/forest edge), not a missing texture. Draw order bottom-to-top: 1 terrain, 2 water base, 3 shore/path, 4 low non-solid decorations, 5 placed furniture bases, 6 actors + solid resource nodes (y-sorted), 7 tall non-blocking decorations, 8 water ripples/overlays, 9 particles (≤20 active), 10 UI. Y-sort Z values: furniture base 0.5, player/shopkeeper/berry node/ore node 1.0, fish bobber 1.2, interaction highlight 1.5. Decorations never hide an interaction target (make transparent, move, or draw below). Animation limits: characters/water max 8 FPS; UI animations max 300ms; no full-screen flash/shake/wash — all feedback is localized (small pops, small coin flight, small case glow).

**Recipe table** (all colors are the shared palette; tiles are generated per recipe: fill base → 20–40 darker speckles → 10–20 lighter speckles → 1–2 accent details → 1px bottom shadow line `#2E241B` @ 15%):

| Palette | Hex | Use |
| --- | ---: | --- |
| Ink Shadow | `#2E241B` | Shadows, text, dark UI |
| Warm Dark Wood | `#5C4032` | Borders, dark wood |
| Medium Wood | `#8A5A3B` | Furniture, buttons |
| Light Wood | `#B98A63` | Trims, highlights, button hover |
| Parchment | `#F3E4C7` | UI panels, cards |
| Paper | `#F9F1DC` | Highlighted panels |
| Earth Path | `#C2A374` | Village paths, dirt, shore sand |
| Dry Grass | `#A3B37A` | Village edges, light speckles |
| Grass Base | `#85A66A` | Main grass (dark: `#5F7A4C`) |
| Stone Grey | `#8C867B` | Rocks, museum floor (dark: `#6D675D`) |
| Stone Light | `#B9B2A6` | Highlights, walls |
| Water Shallow | `#6FB0C4` | Shallow lake (ripple lines lighter blue) |
| Water Deep | `#3F7D96` | Deep lake |
| UI Gold | `#D9A441` | Coins, highlights, goal reward |
| Valid Feedback | `#6FBF73` | Valid placement, success, green zone |
| Invalid Feedback | `#D96A5A` | Invalid placement, errors, red zone |
| Warning Amber | `#E3B23C` | Low supply, yellow zone, caution |
| Coin icon | `#E5C158` | Coin HUD icon |

| Zone accent | Primary | Secondary | Minimap color |
| --- | ---: | ---: | ---: |
| Village | `#D9A441` warm amber | `#8A5A3B` wood | `#D9A441` |
| Berry Grove | `#5E8C4A` leaf green | `#D94F5C` sweet berry | `#5E8C4A` |
| Ore Ridge | `#A5765B` earth stone | `#C06A3F` copper | `#A5765B` |
| Lakeside | `#4E9BB0` teal water | `#9BB8E8` moon blue | `#4E9BB0` |
| Home interior | `#C99B6A` warm wood floor | `#F3E4C7` parchment walls | — |
| Museum interior | `#C8B494` stone plaster | `#C7A24A` brass | — |

| Resource / specimen color | Hex | Character | Icon shape (colorblind-safe) |
| --- | ---: | --- | --- |
| Sweet Berry | `#D94F5C` | Warm red-pink | Round berry with leaf |
| Moon Berry | `#8E7BD1` | Lavender-blue | Round berry with crescent mark |
| Ember Berry | `#F07A3A` | Warm orange, slight glow | Round berry with flame mark |
| Copper Ore | `#C06A3F` | Earthy orange-brown | Hexagonal ore with speckles |
| Silver Ore | `#CFCFCF` | Cool silver | Hexagonal ore with vertical stripe |
| Crystal Shard | `#86E8FF` | Bright cyan, soft glow | Triangle prism |
| Minnow | `#D8C97A` | Pale yellow-silver | Small round fish |
| Trout | `#D97A4F` | Orange-red | Longer fish |
| Moonfish | `#9BB8E8` | Pale blue-silver | Fish with crescent mark |

Tier visual logic: Tier 1 natural/no glow; Tier 2 slightly cooler/brighter; Tier 3 soft emissive pulse, 1.5s cycle. Resource colors must be identical in world sprites, inventory icons, shop UI, ledger cards, display-case contents, toasts.

Tile recipes: **grass** base `#85A66A`, dark speckles `#5F7A4C`, light `#A3B37A`, accent small flower `#D94F5C`/`#F3E4C7`; **berry_grove** grass + leaf litter + fallen leaves; **ore_ground** stone `#8C867B` base, dark `#6D675D`, light `#B9B2A6`, accent copper/crystal fleck; **path** `#C2A374` packed dirt with 1px wood trim; **water** `#6FB0C4`/`#3F7D96` with lighter ripple lines, shore edge `#C2A374`; **perimeter** darker water/forest band.

Sprite sizes: player 16×16 (shadow 12×6 ellipse); furniture `1x1`=24×24, `2x1`=48×24, `1x2`=24×48, `2x2`=48×48. UI skin: panels parchment `#F3E4C7`, border `#5C4032` 2px, radius 3px, shadow `rgba(0,0,0,0.25)` 4px offset; buttons normal `#8A5A3B` / hover `#B98A63` / pressed `#7A4A32` / disabled `#8A7A66` / selected `#D9A441` border, text `#2A1B12`; tabs: active raised parchment + brass underline, inactive darker parchment; font stack `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`; sizes: title 18px, body 14px, small/hint 12px (never below 12px); important text always on a background panel. Build ghost: valid `#6FBF73` @ 40%, invalid `#D96A5A` @ 40%, selected item white outline, steady (no flashing) with red reason pill. Grid lines `rgba(255,255,255,0.12)`; valid/invalid tile highlight `rgba(111,191,115,0.25)` / `rgba(217,106,90,0.25)`.

**Visual-implied rules, ruled**: (a) 5-segment supply meter maps to `floor(supply)` 0..3 with fills 5/4/3/2 and labels Normal/Low/Very Low/Barely (§4.7) — color plus text, never color alone; (b) target highlight = soft white outline + slight brightening, no bounce/pulse, shown when `state.target` is set; (c) “Bag Full” = red `Bag Full` prompt + one short inventory-border pulse (feedback only; movement is never blocked); (d) locked museum door shows brass lock icon + prompt `Museum Locked` with the exact First Trades requirement text; after unlock the lock fades and a brass shimmer crosses the door; (e) fishing meter 240×20: dark water background `#2E241B`, parchment border, green zone `#6FBF73`, yellow zones `#E3B23C`, white vertical indicator bar; prompt says `Strike!` during the bite meter; (f) gathering progress bar 160×12: dark wood background, neutral gold fill, parchment border, category icon — one bar for both berry and mining; (g) Reduce Motion disables water ripple frames, Tier-3 pulse, particles, and toast slide; High Contrast thickens borders and strengthens highlights without changing mechanics; (h) no resource nodes on the minimap.
