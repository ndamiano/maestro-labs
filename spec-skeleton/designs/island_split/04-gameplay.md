# 4. GAMEPLAY SPEC

**The game — one paragraph.** You are a shipwrecked salvager on a tide-locked island. Explore a bounded 2.5D isometric island, find **five Tide Keys**, read their **distance clues**, and use the overlapping **clue rings** on the Hoard Map to pinpoint the hidden vault; then time the **low tide** and open it to collect the treasure. There is no combat, no health, and no fail state — the only pressure is the tide, and it is always readable and avoidable. Session 15–25 minutes. Core loop: move/explore → discover landmarks & sectors → find 5 key caches → the first four keys each add a clue ring → after four geometric clues the exact vault marker appears → with 5 keys + low tide, open the vault → collect the final treasure and end.

**Core Constants (record — every number gameplay gave, carried as given):**

| Constant | Value | | Constant | Value |
| --- | --- | --- | --- | --- |
| World size | 256×256 tiles | | Walk speed | 3.0 tiles/s |
| Tile size | 1 meter | | Run speed | 5.0 tiles/s |
| Ocean border | 8 tiles | | Swim speed | 2.0 tiles/s |
| Max elevation | 5 | | Low-stamina swim | 1.5 tiles/s |
| Tide cycle | 120 s | | Max stamina | 100 |
| Water level range | 0–2 | | Run drain | 12 stamina/s |
| Low tide threshold | `< 0.7` | | Swim drain | 10 stamina/s |
| High tide threshold | `> 1.3` | | Stamina regen | 20 stamina/s |
| Passable water depth | `<= 1.0` | | Map reveal radius | 10 tiles |
| Low-tide window (computed) | ~48.4 s / cycle | | Landmark visible dist | 24 tiles |
| | | | Cache visible dist | 8 tiles |
| | | | Hunt area radius | 24 tiles |
| | | | Clue ring width | D ± 6 tiles |
| | | | Safe displacement radius | 16 tiles |
| | | | Interact radius | 1.5 tiles |
| | | | Key cache coins | 10 each |
| | | | Scattered coins | 40 total (8/sector) |
| | | | Vault coins | 70 |
| | | | Total coins | 160 |
| | | | Movement substep | 0.1 tile |
| | | | Max overlap tiles (clues) | < 400 |

**Records with rosters:**

*Sectors (6):*

| id | Name | Role | Bounds (x,y) | highAnchor | lowAnchor/base | Elevation |
| --- | --- | --- | --- | --- | --- | --- |
| driftwood-cove | Driftwood Cove | start, tutorial, Key 1 | 16–70, 190–240 | (32,215) | (32,220) | 0 beach, 1 dunes |
| gull-flats | Gull Flats | low-tide teaching, Key 2 | 90–170, 210–250 | (150,218) | (150,225) | 0 mudflats, 1 flats |
| palm-hollow | Palm Hollow | jungle + interaction, Key 3 | 40–110, 70–150 | (75,110) | (75,105) | 1 lowland, 2 hills |
| sunken-ruins | Sunken Ruins | coastal ruins + movement, Key 4 | 170–220, 100–160 | (195,130) | (195,125) | 1 ruins, 2 floor, 3 tower |
| cliffpath-ridge | Cliffpath Ridge | high ground, Key 5 | 110–180, 30–100 | (145,65) | (145,55) | 2 foothills, 3–4 ridge, 5 tops |
| vault-point | Vault Point | final vault | 185–230, 170–215 | (205,185) | (205,185) | 0 cave, 1 rocks, 2 reef |

*Landmarks (6):*

| id | Name | x,y | elevation | sector | isSectorLandmark | Map glyph |
| --- | --- | --- | --- | --- | --- | --- |
| shipwreck | Shipwreck | 40,210 | 1 | driftwood-cove | yes | anchor |
| lighthouse | Gull Flats Lighthouse | 150,225 | 2 | gull-flats | yes | vertical tower |
| idol | Palm Hollow Idol | 75,105 | 2 | palm-hollow | yes | mask circle |
| arch | Sunken Arch | 195,125 | 2 | sunken-ruins | yes | arch shape |
| eagle-rock | Cliffpath Eagle Rock | 145,55 | 4 | cliffpath-ridge | yes | V-shaped eagle |
| reef | Vault Point Reef | 205,185 | 2 | vault-point | yes | coral branch |

*Caches / Keys (5):*

| id | keyId | Sector | x,y | elevation | Interaction | Channel | requiresKey1 | clue {landmarkId, distance} | prompt |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| key1 | 1 | driftwood-cove | 45,208 | 1 | Open barrel | 0.5 s | no | {shipwreck, 169} | Open barrel |
| key2 | 2 | gull-flats | 135,222 | 0 | Open rock shelf | 0.5 s | yes | {lighthouse, 67} | Open low-tide shelf |
| key3 | 3 | palm-hollow | 80,112 | 1 | Pull rope | 1.0 s | yes | {idol, 159} | Pull rope |
| key4 | 4 | sunken-ruins | 192,132 | 1 | Move column | 1.5 s | yes | {arch, 68} | Move column |
| key5 | 5 | cliffpath-ridge | 148,58 | 1 | Open chest | 0.5 s | yes | — (no geometric clue) | Open chest |

Key 3 blocker tiles (gate, 2 tiles) default: `tileIndex(80,111)`, `tileIndex(80,110)`; interact `{80,109}`, reward `{80,112}`. Key 4 blocker tile (column, 1 tile) default: `tileIndex(192,131)`; interact `{192,130}`, reward `{192,132}`. Key notes: Key 1 "The treasure is 169 paces from the Shipwreck." Key 2 "…67 paces from the Gull Flats Lighthouse." Key 3 "…159 paces from the Palm Hollow Idol." Key 4 "…68 paces from the Sunken Arch." Key 5 "The fifth tide turns the lock. The reef cave opens only at low tide."

*Clues (4 geometric):* Keys 1–4 (table above) with ring color/dash from §3. Key 5 adds no clue. Ring inner `D-6`, outer `D+6`.

*Coins (total 160):* 40 scattered (8 per sector, ids `coin-001..coin-040`, on low-tide-passable tiles, ≥2 tiles apart, some in elev-0 low-tide-only spots) + 5×10 cache coins (granted on `cache_opened`, not world coins) + 70 vault coins (granted on `vault_opened`). Rank: 0–99 Beachcomber, 100–139 Salvager, 140–159 Master Salvager, 160 Tide Baron.

*High anchors (6):* the `highAnchor` column of the Sectors table (elevation ≥1, reachable at high tide).

*Progression states (10):* `START → TUTORIAL_KEY1 → FREE_KEYS_1_OF_5 → FREE_KEYS_2_OF_5 → FREE_KEYS_3_OF_5 → FREE_KEYS_4_OF_5 → FREE_KEYS_5_OF_5 → VAULT_READY → VAULT_OPEN → GAME_COMPLETE`. (`TUTORIAL_KEY1` ≡ `keys.totalCollected === 0`; used for objective text.)

*Objective text (record):* Start "Open the shipwreck barrel."; 1/5 "Find the Tide Keys. 1/5"; 2/5 "Find the Tide Keys. 2/5"; 3/5 "Find the Tide Keys. 3/5"; 4/5 "Find the Tide Keys. 4/5"; 5/5 "Open the vault at low tide."; Complete "Treasure found."

*Vault prompt (record):* `<5` keys → "Locked. Requires 5/5 Tide Keys."; 5 keys not low → "Sealed by the tide. Wait for low tide."; 5 keys + low → "Open vault".

*Cache sealed prompt:* "Sealed. Find the first Tide Key."

---

### 4.1 World & Level — T1

The island is **authored, not procedurally critical**: a fixed base layout guarantees every key and the vault are reachable; a per-run seed varies only cache positions (keys 2–5, ≤3 tiles) and scattered coin positions. If any variation or the whole level fails validation, fall back to guaranteed defaults.

Generator pipeline (`createLevel(seed=123)`): `buildBaseLevel` → `applySectorBaseFeatures` → `applyRequiredPointElevations` → `carveGuaranteedRoutes` → `addDecorativeHighGround` → `applySeededCacheVariation(level, rng)` → `placeScatteredCoins(level, rng)` → `applyBlockers(level)` → `validateLevel(level)` → if `!ok`, `createFallbackLevel()`.

- **buildBaseLevel:** all tiles elevation 0; ocean border (8 tiles) marked ocean+impassable; interior default elevation 1 (guarantees a connected high-tide spine); the ring of interior tiles adjacent to the border (shore) set to elevation 0 (beaches).
- **applySectorBaseFeatures:** per-sector low-detail elevation matching the roster — Driftwood: keep start area 1, lower beach to 0; Gull Flats: lower southern flats to 0, keep anchor ≥1; Palm Hollow: base 1, small hills 2, routes 1; Sunken Ruins: base 1, ruin floors 2, tower 3, routes 1; Cliffpath Ridge: ridge plateau 3–5 with a walkable ramp 1→4; Vault Point: cave floor 0 around vault, rocks 1, reef outcrop 2, keep low-tide route to vault. Helpers `setTile`, `fillRect`, `raiseEllipse`, `carveRectRoute`, `carveGradualRoute` (adjacent route tiles differ ≤1); all respect the ocean border and never break protected tiles.
- **applyRequiredPointElevations:** Start 1, Vault 0, Gull Flats cache 0, Lighthouse 2, Idol 2, Arch 2, Eagle Rock 4, Reef 2; other caches 1 unless specified. Any point elev ≥2 gets a local ramp from a nearby passable tile (`ensureReachablePoint`).
- **carveGuaranteedRoutes:** L-shaped paths (no diagonal corners) from start to every cache interact, to every cache reward (after blockers), to vault, to every high anchor, to every landmark. Low routes use elevation 1 where possible; if destination elev ≥2, interpolate ≤1 per step. Mark tiles in a `protected` mask that decoration may not alter.
- **addDecorativeHighGround:** after routes are protected — ridge plateau near Eagle Rock (max 4–5, protected ramp to 4, surrounding 4/5 to form non-walkable cliff edges), ruins tower, lighthouse base, reef outcrop. No high-tide passable pockets disconnected from the spine; Cliffpath has ≥1 walkable ramp to 4.
- **applySeededCacheVariation:** for keys 2–5, Chebyshev offset `dx,dy ∈ [-3,3]` via `rng`; new position must be in-bounds, not ocean, not on a required route blocker, ≥2 tiles from any other cache and from the vault (unless it is the vault-area cache), passable at low tide; **Key 2 must be elevation 0**; Key 3/4 blocker + interact/reward move with the cache and stay valid. Any failure → default position.
- **placeScatteredCoins:** 8 per sector (40 total) on low-tide-passable tiles, not ocean, not on blockers, ≥2 tiles from other coins, ≥2 from start; may be in elev-0 low-tide areas; sampling failure → deterministic fallback positions for that sector.
- **applyBlockers:** register key3 (2 tiles) + key4 (1 tile) default blocker tiles in `level.blockers` (or their moved positions); removed when the cache opens.
- **createFallbackLevel:** size 256, ocean border, interior 1, shore ring 0, start 1, vault 0, landmarks 1 with local ramps, caches at default positions, Key 2 elev 0, no decorative cliffs, blockers removed or converted to trivial single-tile gaps with guaranteed access. Less rich, always valid — completion outranks decoration.

**Validation (`validateLevel` → `{ok, fallbackUsed, errors}`):**
- *Passability:* `tilePassable(level,x,y,waterLevel,blockers)` = not ocean, not blocked, `depthAt <= 1.0`; movement between tiles also needs `abs(Δelev) <= 1`.
- *Low tide (waterLevel 0):* start passable; every cache interact passable (initial blockers); every landmark passable; every high anchor passable; **with all cache blockers removed**, every cache reward passable and vault passable (BFS from start for each).
- *High tide (waterLevel 2):* start passable; every high anchor passable and reachable from start (initial and removed blockers); **all high-tide passable tiles belong to the same connected component as start** (no disconnected pockets).
- *Caches:* in-bounds, not ocean, interact reachable at low tide, reward reachable after blockers, channel time > 0, Key 2 elev 0, Keys 2–5 require Key 1, Keys 1–4 have clue data, Key 5 has none.
- *Clues:* for Keys 1–4, `D = round(euclidean(landmark, vault))`; authored distance must equal computed (else invalid → fallback); compute overlap of all four rings (`|dist(tile, landmark) - D| <= 6` for all); valid iff vault tile is in the overlap **and** `overlapCount < 400`.
- *Coins:* exactly 40, none in ocean, none on blockers, none <2 tiles apart, all low-tide passable.

### 4.2 Movement & Stamina — T1

Tile-based with smooth float position. Speed by current-tile depth (`depth = max(0, waterLevel - elev)`):

| Condition | Speed | Stamina |
| --- | --- | --- |
| Dry (depth ≤ 0), walking | 3.0 | none |
| Dry, running, stamina > 0 | 5.0 | −12/s |
| Shallow (0 < depth ≤ 1.0) | 2.0 | −10/s |
| Shallow, stamina == 0 | 1.5 | −10/s |
| Deep (depth > 1.0) | impassable | — |

Rules: running only on **dry** land and only while `stamina > 0`; the player can always **walk** even at 0 stamina; in water the player is "swimming" (drains 10/s) and cannot run. **Stamina:** max 100; drain run 12/s, swim 10/s; regen 20/s when not draining; at 0 → running disabled, swim speed 1.5, no death, still moves. `updateStamina` clamps to [0,100].

**Collision:** axis-separated (`tryMove(dx,dy)` → `moveAxis` per axis) with substeps of `0.1` tile (prevents tunneling at 5 tiles/s). A target-tile change is allowed only if current passable **and** target passable **and** `abs(Δelev) <= 1` **and** target not in an active `blocker`. A blocked axis does not move.

### 4.3 Tide & Safe Displacement — T1

Global, continuous. `waterLevel(t) = 1 - cos(2π t / 120)`; range 0–2; cycle 120 s; low at t=0, high at t=60. Tile `depth = max(0, waterLevel - elevation)`; passable if `depth <= 1.0`, deep if `> 1.0`. **State:** `LOW` if `waterLevel < 0.7`; `HIGH` if `> 1.3`; else `RISING`. Threshold times per cycle (computed at runtime from the formula): enter RISING (from LOW) t = **24.182 s**; enter HIGH t = **35.823 s**; enter RISING (from HIGH) t = **84.182 s**; enter LOW t = **95.818 s**. **LOW window ≈ 48.4 s** (95.818→144.182); **HIGH window ≈ 48.4 s** (35.823→84.182).

**Warnings:** emit `tide_warning {threshold, secondsUntil:10}` **once per threshold per cycle**, 10 s before each of the four threshold times (at t ≈ 14.182, 25.823, 74.182, 85.818). **State change:** emit `tide_state_changed {state}` only on an actual change. Low tide is required to open the vault; some shelves/coins are low-tide-only.

**Safe displacement (checked every update, before movement):** if the current tile is impassable (tide just flooded it): (1) 4-dir BFS for the nearest passable tile within **16** tiles (current water level, ignore ocean + blockers); if found → move there, cancel any active channel, emit `safe_displacement_occurred`; (2) if none → teleport to `lastHighSafeTile` if it exists, else to the start tile; cancel channel; emit event. **No keys, coins, or progress are lost.** `lastHighSafeTile` updates whenever the player stands on a tile with **elevation ≥ 1** (passable at high tide); initialized to start (32,220, elev 1). Tide is a planning problem, not a death trap.

### 4.4 Hoard Map, Fog, Landmarks, Hunt Areas — T1

**Fog / reveal:** when the player enters a new tile, reveal all tiles within **radius 10** that have line of sight; revealed tiles stay revealed forever. **LOS:** sample the ray from player tile center to target tile center every **0.5** tiles; blocked if any sampled tile has `elevation > playerTile.elevation + 1`; **water does not block visibility**.

**Sector discovery:** a sector is discovered when the player tile enters its bounds **or** its sector landmark is discovered; emit `sector_discovered {sectorId, sectorName}` once; show a banner once per sector.

**Landmarks (6, roster §4):** every frame (throttle ≥10 Hz), for each undiscovered landmark, if `distance(player, landmark) <= 24` **and** LOS exists → discover: add to `state.landmarks.discovered`, emit `landmark_discovered`; if it is a sector landmark → discover the sector + emit `sector_discovered`; **if Key 1 is already collected → reveal that sector's hunt area** + emit `hunt_area_revealed`. Discovered landmarks remain on the map (triangle icon + glyph).

**Hunt areas:** when **Key 1 is collected AND the sector's main landmark is discovered AND the cache is uncollected**, the Hoard Map shows an **orange dashed circle of radius 24** centered on the uncollected cache. The exact cache prop is only visible in-world when the player is within **8 tiles** and has LOS (sealed caches stay visible so the padlock reads). Hunt areas prevent search-fail without revealing the exact cache.

### 4.5 Caches, Keys, Channels, Clue Rings — T1

Five caches, each 1 Tide Key + 10 coins. **Keys 2–5 are sealed until Key 1 is collected.**

**Visibility / prompt:** a cache is visible when uncollected, player within **8** tiles of its interact or reward, and LOS exists (sealed still visible). Within the **1.5-tile interact radius**, show the context prompt (openable = brass `[E]` + gold outline; sealed = padlock + "Sealed. Find the first Tide Key.").

**Channel state:** `state.activeChannel = {type:"cache"|"vault", targetId, startTime, duration, progress}`. Starts when the cache is visible, player within interact radius, not sealed, not opened, and `input.interact` is held. **Cancels** (emit `channel_cancelled {reason}`; prompt shows `Cancelled`) if: player moves, `input.interact` released, map opened, safe displacement occurs, or (vault) tide is no longer low. On completion (emit `channel_complete`), a cache: marks opened+collected, removes its `blockerTiles`, grants the key, grants 10 coins, emits `cache_opened`, `key_collected`, `coin_collected`; if the key has a geometric clue → add clue, increment `geometricCollected`, emit `geometric_clue_added`; **if Key 1 just collected → unseal Keys 2–5 and reveal any hunt areas whose landmarks are already discovered**; **if `geometricCollected === 4` → `vault.markerRevealed = true`, emit `vault_marker_revealed`**; update objective.

**Clue rings:** the first four keys each add a ring centered on their landmark, inner `D-6`, outer `D+6` (D = authored distances 169/67/159/68; §4.1 validates these equal `round(euclidean(landmark, vault))`). Progression by geometric clues: 0 → no rings; 1 → one ring; 2 → two overlap; 3 → overlap shrinks; **4 → exact vault marker appears**. Vault opens only at **5 total keys + low tide**. (Rings, not manual bearings: same puzzle, lower friction.)

### 4.6 Coins & Score — T1

Coins are optional score; they do not affect completion, keys, or the vault. Collected by **walking over** (player distance to coin center ≤ 0.5, coin tile passable). Low-tide-only coins are submerged at high tide. No regeneration. On collect: mark collected, `state.coins.collected += 1`, emit `coin_collected {amount:1, totalCollected}`. Total possible **160** (40 scattered + 5×10 cache + 70 vault). **Rank at completion:** 0–99 Beachcomber, 100–139 Salvager, 140–159 Master Salvager, 160 Tide Baron.

### 4.7 Final Vault — T1

Location: Vault Point, **(208,192)**, elevation **0**, in a sea cave behind reef rocks. Requirements: **5/5 keys** and **low tide (`waterLevel < 0.7`)**. Prompt logic (record §4): `<5` keys → "Locked. Requires 5/5 Tide Keys."; 5 keys not low → "Sealed by the tide. Wait for low tide."; 5 keys + low → "Open vault". **Vault ready** = `totalCollected >= 5 && waterLevel < 0.7`; emit `vault_ready_changed {ready}` on change. **Channel time 1.0 s**; requires 5/5 + low tide + player near + interact held. **Cancels** on move, map open, interact release, safe displacement, or tide no longer low. On success: mark `unlocked` + `completed`, +70 coins, enter `GAME_COMPLETE`, disable input, emit `channel_complete`, `vault_unlocked`, `vault_opened`, `game_complete {time, keys:5, coins, rank}`; collect the 70 coins and the Golden Compass.

### 4.8 Objectives — T1

`currentObjective()` derived from state (record §4): complete → "Treasure found."; 0 keys → "Open the shipwreck barrel."; ≥5 keys → "Open the vault at low tide."; else `Find the Tide Keys. ${keys}/5`. Emit `objective_changed {text}` when the text changes; HUD updates on the event.

### 4.9 Progression & Difficulty — T1

State machine: `START → TUTORIAL_KEY1 → FREE_KEYS_1..5_OF_5 → VAULT_READY → VAULT_OPEN → GAME_COMPLETE` (roster §4). Difficulty has no health, no combat, no fail state; the **tide is the only pressure** and it is always readable/avoidable. Key 1 teaches the map, clue rings, and the loop; Keys 2–5 stay sealed until Key 1 so the player never wanders into a late sector unprepared. **Pacing expectations:** first key < 60 s; Gull Flats low-tide lesson 2–4 min; all five keys 10–20 min; full game 15–25 min. **Feel target:** rarely lost > 60 s; tide understood within the first 3 min; the map feels like a tool, not a tutorial; the final vault feels like a timed ritual, not a boss fight.

### 4.10 Feel — T1

Calm but alive: water ripple, foam, coin spin, key pulse, landmark discovery pulse, map ring draw, vault glow, walk/run/swim. Short readable animations; no fast flashing, no large screen shake, no particle bursts that obscure the player, no disorienting camera moves. *(See §5 motion rules, §6 audio, §11 motion feel.)*
