# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Open world collector game (single continuous map, free roam) | §3 Space, §4.2 |
| The player walks around | §4.1 |
| Collecting resources into an inventory | §4.6 |
| Harvest berries | §4.3, §4.4 |
| Mine ores | §4.3, §4.4 |
| Fish fish | §4.5 |
| Sell them to a shop keeper for each type | §4.7 |
| Buy furniture to decorate their home | §4.8, §4.10 |
| Decorate a small museum-type building | §4.9 |
| *(added)* Relaxed, no-fail fantasy (no health, no combat, no fail state) | §4.1, §4.11 |
| *(added)* Purchasable tool tiers that improve gathering | §4.4, §4.7 |
| *(added)* Count-based goals ending in Curator’s Seal completion | §4.11 |
| *(added)* Collection log and museum specimen curation | §4.9 |
| *(added)* Supply-meter price fluctuation per shop | §4.7 |
| *(added)* Non-binding Home/Museum scores | §4.10 |
| *(added)* Save/load persistence across sessions | §2.3 (Save), §8 |
| *(added)* Accessibility settings (reduce motion, high contrast, volumes) | §4.12, §7 |
| *(added)* Deterministic world (seed 42) | §4.2 |
| *(added)* Cozy hand-painted pixel look with per-zone identity | §3 |
| *(added)* Calm generated audio (music + SFX, Web Audio) | §6 |

## 0.2 Decisions

One row per disagreement and per request-open choice a builder would otherwise have to make. Rulings are final.

| Topic | gameplay said | visual said | engineering said | Ruling (and why) |
| --- | --- | --- | --- | --- |
| Dimensionality (request open) | 2D top-down, fixed camera, no vertical axis | 2D top-down; painted sprite height and soft shadows only; no parallax, no vertical implication | 2D tile canvas, 960×540, y-sort | **2D top-down, y-sorted sprites, no parallax, no vertical mechanics** — all three agree; the request did not specify. |
| Design resolution (open) | 960×540, ≈40×22 tiles visible | 960×540, art native to 24px tiles, nearest-neighbor | 960×540 canvas, CSS-scaled | **960×540 design resolution, 24px tiles, pixelated scaling** — unanimous. |
| Input scheme (open) | WASD/arrows + interact button; mouse in build mode | Keyboard/mouse; no touch | Keyboard/mouse table; touch cut | **Keyboard + mouse only**; full table in §1.2. |
| Player start tile (open) | “starts nearby” home | — | Start tile `(57, 70)`, position `(57.5, 70.5)` | **Start at `(57, 70)`** — the only concrete value given. |
| Perimeter width (disagreement) | Impassable “outer edge tiles” (1 tile) | “1–2 tile visual border” | 2-tile band: `x<2 ‖ x≥118 ‖ y<2 ‖ y≥118` | **2-tile band** — prevents edge-grazing, satisfies “edge is impassable,” and matches the visual border width. |
| Berry base yield (disagreement; internal to gameplay) | §5.3: base = entire stack (1–2), upgrades add bonus; §6.2 pseudo: base = 1, bonus → 2 | — | Base = `node.count`; bonus +1 only if `baseYield < 2` (cap 2) | **Base = entire available stack (1 or 2); bonus +1 only when the stack was 1, capped at 2** — preserves “picking removes the entire available stack” and keeps yields bounded at 2. |
| Tool tier indicator (disagreement) | Stars/roman: T1 none, T2 `II`-ish, T3 `III`-ish | Pips: T1=1, T2=2, T3=3 filled; “do not use stars if pips are clearer” | Pips 1/2/3, no color-only | **Pips (1–3 filled)** — two documents agree; pips are clearer at 32px. |
| Water depth & speed (disagreement) | “Shallow water walkable at 3 t/s” (deep unspecified) | Shallow and deep water both readable, both walkable-looking | All water walkable at 3 t/s | **All water (shallow and deep) walkable at 3 t/s** — deep water holds Trout and Moonfish spots, so it must be enterable. |
| Fishing green-zone position (open) | Moving indicator, zone widths given, position unspecified | Meter centered on screen; green + yellow zones | Green fixed at meter center (progress 0.5) | **Green zone fixed at center** — readable and testable; tier upgrades already widen the green zone, which is the designed ease improvement. |
| Leaving a fish spot (disagreement of scope) | Fail if leaving during the bite meter | — | Fail if leaving during any phase (casting, waiting, meter) | **Fail on leaving in any phase** — superset; prevents stalling a committed cast. |
| Supply recovery (disagreement) | 1 step of 1.0 per 120s after last sale | — | `steps = floor(elapsed/120)`, subtract steps, clamp 0, bookkeep `lastSaleTime` | **Engineering multi-step version** — identical to gameplay for single-step cases, correct after long idles. |
| Museum lock requirement text (disagreement) | §9.6 door text “Sell 5 berries / ores / fish” (category); goal itself needs specific resources | “Museum Locked” prompt | Goal uses `resource_sold` per specific resource | **Door text shows the exact First Trades requirement: “Sell 5 Sweet Berries, 5 Copper Ores, 5 Minnows”** — the goal is specific; category text would mislead. |
| Inventory hotkey `I` (disagreement) | Optional `I` for separate inventory details | No separate screen | Separate inventory screen cut | **No `I`, no separate inventory screen**; slot hover tooltip carries name/count/base price/current shop price. |
| Furniture totals (disagreement) | Summary: 15 non-display, 28 total items | Item tables per shop (14 decor visuals + 4 display) | 18 furniture rows (14 decor, 4 display) + 9 tools | **14 decor + 4 display + 9 tools (3 owned at start) = 27 distinct items**; the item tables govern — the summary counts were an arithmetic error. |
| Asset pipeline (disagreement) | — | PNG sprite files + `.ogg` audio; also gives procedural tile/audio *reference* recipes | Assets “provided”; manifest maps IDs to files; no runtime deps | **All assets generated in code**: sprites/tiles drawn to offscreen canvases from §3 recipes; all audio synthesized per §6; the manifest maps semantic IDs to *recipes*, not files. The builder is code-only, so no binary assets. |
| Music approach (disagreement) | Audio out of scope | `.ogg` loops, 72–84 BPM, zone identity table | Music file paths in content | **Generated Web Audio loops and stingers** with zone identity per visual’s instrument/mood table; no audio files. Stingers are the §6 SFX rows (no separate music-stinger files). |
| Volume defaults (disagreement) | — | −18/−12/−24 dB relative | Defaults 0.7 / 0.8 / 0.5 (music/SFX/ambience) | **0.7 / 0.8 / 0.5 linear defaults** — concrete values; the dB table is honored as relative intent (SFX loudest, ambience quietest). |
| Settings access (open) | Settings not specified | Settings UI with 3 volumes + 2 toggles | SettingsUI exists; no key bound | **`P` in play opens Settings; button on title screen**; state fields reserved in T1, modal staged T2 (§0.3). |
| Scene entry (open) | Doors walkable; interaction implied | — | Entry/exit via interaction, not auto-step | **Interaction-based entry/exit** — prevents door re-entry loops. |
| Player collider (open) | — | Sprite 16×16 centered in tile | AABB half-size 0.32 tiles, axis-separated movement | **0.32-tile half-size, axis-separated collision** — the only concrete value. |
| Fixed timestep (open) | Timers in seconds | — | `update(dt)` clamps dt to 0…0.1 | **Fixed 1/60s steps via rAF accumulator, max 6 steps/frame, 0.1s clamp as safety** — deterministic timers require a fixed step. |
| Random source (open/clarify) | “One random source” implied via seeded RNG | — | Two RNG instances: `worldRng`, `runtimeRng` | **One `SeededRNG` class; exactly two instances**: `worldRng(seed 42)` for world generation only, `runtimeRng(seed 43)` for gameplay randomness; `Math.random` is banned. |
| Footsteps (open) | — | 3 SFX: grass/stone/water steps | SFX mapping includes them | **Three footstep SFX**, surface = tile under player (mapping in §6). |
| Screenshots table (missing) | — | No SCREENSHOTS table shipped (acceptance checklist §30 and moments §18/§27 exist) | — | **§9 SCREENSHOTS table synthesized from visual’s moments + acceptance checklist**, each row reachable via §8 debug calls. |
| X / right-click target (disagreement of wording) | “deletes the selected placed furniture” | — | “remove targeted placed item” | **X / right-click removes the placed item under the pointer (targeted); clicking a placed display case opens the exhibit panel.** |
| Build mode outside interiors (open) | Build mode only inside Home/Museum | — | Same | **`B` outside interiors emits `invalid:action` + toast “Build inside your Home or Museum.”** |

## 0.3 Tiers

**T1 — the game that must ship** (by system name): World generation (deterministic), Player movement & collision, Scenes (world/Home/Museum) & doors, Interaction, Berry & Ore nodes, Gathering (pick/mine), Fishing, Inventory, Shops & economy (sell/buy/supply/tiers), Furniture & build mode, Museum & specimens, Scores, Goals & completion, Save/load, Title screen, Persistent HUD + minimap, Shop UI, Ledger UI, Build UI, Toasts, core SFX, zone music.

**T2** (independent items, add in this order):
1. Settings modal (music/SFX/ambience sliders, Reduce Motion, High Contrast) — state defaults reserved in T1.
2. Zone ambience beds (generated noise beds, §6).
3. Activity music layers: shop, build.
4. Shopkeeper flavor lines on shop open (Moss/Grit/Reed).
5. One-time build-mode hint toast (“Use mouse to place, R to rotate, X to remove”).
6. Feedback juice: coin flight to HUD, HUD pulse, shopkeeper sign sparkle, gold-leaf particles on completion.

**T3** (independent items, add in this order):
7. Shopkeeper non-idle animations (talk/sell/buy/unlock); idle ships in T1.
8. Minimap current-zone brighter highlight.
9. E2E deep audio-decode suite (smoke + asset-generation checks stay T1).

**Cuts (final, not staged)** — merged from visual §28 and engineering §2.5, carried with reasons: no day/night cycle (lighting complexity, noise); no weather (visibility/pacing); no parallax (readability); no character customization (asset/UI burden); no heavy particles (noise; ≤20 small effects allowed); no complex facial animation (unreadable at sprite size); no per-small-area music files (one loop per major zone); no resource nodes on minimap (clutter, exploration); no dynamic lighting for furniture (readable placement); no scary/aggressive audio (no fail state); no touch controls (keyboard/mouse design); no multiple save slots / cloud save (single-player relaxed); no custom map editor (generator + quotas suffice); no runtime texture-generation of *art direction* beyond §3 recipes (assets are generated code, not runtime user-facing generation); no dynamic lighting, screen shake (calm tone); BFS only, no A* (placement checks + bots suffice); no separate inventory screen; no manual stack splitting; no mobile optimization pass; no replay system; no achievements outside goals.
