# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Open-world game: explore an island *(request)* | §3 space; §4.1 World & Level; §4.4 Sectors roster |
| Find treasure *(request)* | §4.7 Final Vault; §5 Vault; §7 End screen; §6 `game_complete` |
| 2.5D isometric, fixed non-rotating camera *(added)* | §1.1; §3 projection; §4.2 |
| Five Tide Keys + distance clue rings that locate the vault *(added)* | §4.5 Caches/Keys/Clues; §4.5 clue roster; §3 map clue rings |
| Continuous tide with low/high states and safe displacement *(added)* | §4.3 Tide & Safe Displacement; §3 water/tide rendering |
| Hoard Map: fog of war, landmarks, hunt areas, vault marker *(added)* | §4.4 Hoard Map/Fog/Landmarks; §3 map overlay |
| Stamina-based movement; no health, no combat *(added)* | §4.2 Movement & Stamina |
| Optional coin score + end rank *(added)* | §4.6 Coins & Score |
| Web Audio–generated SFX + adaptive music *(added)* | §6 Audio |
| HUD, start screen, end screen *(added)* | §7 UX |
| Deterministic authored level + validation + fallback *(added)* | §2.3 generator/validator; §4.1; §9 |
| Headless test suite + single-seed playthrough proof *(added)* | §8 Debug API; §9 Tests; §10 |

## 0.2 Decisions

Topic · gameplay said · visual said · engineering said · **Ruling (clause why)**.

| Topic | gameplay | visual | engineering | Ruling |
| --- | --- | --- | --- | --- |
| Middle tide-state name | "Rising/Mid" (0.7–1.3) | "RISING" | `tideState()` → "RISING" | **Name it `RISING`.** State is one string used by HUD, music and events; two docs already agree. |
| Audio source | lists 11 events | asset categories + synth examples | "attempt load, else synth fallback" | **All audio synthesized at runtime via Web Audio API; no external audio asset files are loaded.** The §6 table is a generation recipe set; keeps the bundle self-contained. |
| Coin SFX pitch | — | table "1200–1800 Hz" vs code "1400 + rand·500" | — | **1200–1800 Hz.** The table is the readable spec; the code sample was illustrative. |
| Shipped seed | — | — | `createLevel(seed=12345)`, harness default 123 | **Shipped build uses fixed seed 123.** Deterministic default island; other seeds are T3 tests/debug. |
| Fixed timestep | — | — | harness `dt` 0.016 / 0.05 | **Browser runs a 60 Hz fixed-step accumulator (`dt = 1/60` s); the harness `advance(sec, dt)` uses a caller-supplied `dt` (default `1/60`, playthrough uses 0.05).** Stable in browser and headless. |
| Player facing count | — (no facing spec) | "walk/run/swim 4 directions" | 4-axis input booleans | **4 facings (N/E/S/W) from dominant velocity axis; horizontal wins ties.** Matches the authored 4-dir animation set. |
| High-tide flood preview | — | §9.1 "optional" but §9.5 "important" | required map layer + dirty flag | **Required map layer (not optional).** Engineering validates it; it is core to tide planning. |
| Cache open sound | — | generic `cache_opened` + specific `rope_pulled`/`column_moved` | maps both `cache_opened` and `rope`/`column` | **Key 3 → `rope_pulled`, Key 4 → `column_moved`, Keys 1/2/5 → `cache_opened` (per-prop variant).** Sound follows the physical action. |
| Vault open: function vs cinematic | functional open + complete | 9-step cinematic | functional open + events | **T1 = functional open (events + state + complete). T2 = full cinematic.** Completion must ship; the cinematic is a flourish. |
| Music depth | 11 event cues | full 5-layer adaptive + motifs | 5 layers | **T1 = sea bed + event stingers. T2 = full adaptive layers + sector motifs.** Silence is acceptable to ship; full music elevates. |
| Start-screen controls | E/Enter, M/Right Mouse | E, M/Right Mouse (omits Enter) | E/Enter, M/Right Mouse | **Full set: Move WASD/Arrows, Run Shift, Interact E/Enter, Map M/Right Mouse.** gameplay+engineering agree on the full set. |
| SCREENSHOTS table | — | none (only §16 checklist) | — | **Integrator constructs the SCREENSHOTS table (§9) from visual §16 checklist + defined states.** Template requires it; checklist items become screenshot rows. |
| Tide threshold times | — | — | approximate (24.194/36.033/83.967/95.806) | **Use exact values from the agreed formula (24.182/35.823/84.182/95.818 s), computed at runtime.** The formula is authoritative; doc values were rounded. |
| Start / Shipwreck / Key-1 elevations | (implied dunes=1; no value for these tiles) | — | start elev 1; shipwreck elev 1; key1 elev 1 | **Start (32,220) elev 1; Shipwreck (40,210) elev 1; Key-1 barrel (45,208) elev 1.** engineering owns the numbers; start elev 1 makes it a valid high-safe tile. |
| Interact radius | "stand near" | — | 1.5 tiles | **1.5 tiles.** engineering owns the number. |
| Movement substep | — | — | 0.1 tile | **0.1 tile.** Prevents tunneling at 5 tiles/s. |
| End-screen restart | — | "optional restart button" | "reload the page" | **Include a Restart button that reloads the page.** Trivial UX; single-session design needs no state reset. |
| Random source | — | — | `mulberry32(seed)` | **Single PRNG `mulberry32(seed)`; only level generation draws from it, in a fixed order (cache offsets keys 2–5, then scattered coins per sector).** No `Math.random` in gameplay (coin-pitch jitter is cosmetic). |
| Map world visibility | — | 92% opaque, 8% world | — | **Carry 92% opaque / 8% world.** Single agreed value; tide warnings stay readable. |

## 0.3 Tiers

**T1 — the game that must ship (by system name):** World & Level; Movement & Stamina; Tide & Safe Displacement; Hoard Map / Fog / Landmarks / Hunt Areas; Caches / Keys / Channels / Clue Rings; Coins & Score; Final Vault (functional); Objectives; HUD (persistent + start + end + map overlay + banners); Audio (SFX one-shots + sea bed + event stingers); Input & Controls; Core test suite (unit + single-seed playthrough).

**T2 — stage after T1 (each line independent, in this order):**
1. Adaptive music: full 5 layers (sea bed + percussion + melody + tide accent + stingers) with adaptive state rules.
2. Sector discovery banners + two-note sector motifs.
3. Collection flourishes: coin/key fly-to-counter animations + bursts.
4. Safe-displacement animation (ripple + splash + "Tide pushed you").
5. Vault opening cinematic (door opens, light spills, water drains, treasure burst, compass rises, fade).
6. Landmark discovery flourish (golden outline + map stamp + brass pin).

**T3 — stage after T2 (each line independent, in this order):**
1. Small-screen support (800×480, HUD scale 0.85, safe area).
2. Decorative world richness (gull shadows, eagle, wind streaks, reef coral, tide-line on exposed sand).
3. Multi-seed playthrough (seeds 1, 7, 42, 123, 999) + completion-time bound (< 30 min) + event-order assertions.
4. Browser E2E smoke test.
5. Performance optimization pass (pre-rendered tile atlases, map offscreen layer caching, culling, SFX pool) + 60 FPS profiling.
6. End-screen confetti (gold + foam) + rank icons.

Every §4 system is tagged with its tier where specified (all T1).
