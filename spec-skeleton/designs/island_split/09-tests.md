# 9. TESTS

Headless (Node, no browser). **Every unit + playthrough call is a §8 function; every expected state follows from §4.** T3 e2e drives the real page (keyboard/mouse = the §1.2 inputs) and is listed for completeness; it does not consume the debug API.

**Unit tests (each system ≥1 check):**

- **`tide.test.js`** — `waterLevelAt(0)=0`, `waterLevelAt(60)=2`, `waterLevelAt(120)=0`; `tideState` LOW/HIGH/RISING at `<0.7`/`>1.3`/between; `tide_state_changed` fires only on real change; `tide_warning` fires 10 s before each threshold, once per cycle, no duplicates. *Calls:* `debug.tide.set`, `debug.advance`, `debug.tide.level/state`, `debug.events.last`.
- **`passability.test.js`** — elev 0 passable at wl 0, impassable at wl 2; elev 1 passable at wl 2; elev 2 passable at wl 2; `debug.depth` correct; ocean border impassable; Δelev 1 walkable, Δelev 2 not; active blockers impassable, removed blockers passable. *Calls:* `debug.level.setTile`, `debug.depth`, `debug.passable`, `debug.level.blockers`.
- **`movement.test.js`** — dry walk ≈3.0, run ≈5.0, no run in water, swim ≈2.0, low-stamina swim 1.5, blocked movement no position change, no corner clipping, no 1-tile-cliff tunneling at speed. *Calls:* `debug.player.set/state`, `debug.input.move/run`, `debug.tide.setLevel`, `debug.advance`.
- **`stamina.test.js`** — run −12/s, swim −10/s, regen +20/s when not draining, clamp to 0, run disabled at 0, walk still possible at 0. *Calls:* `debug.player.setStamina/state`, `debug.input.run/move`, `debug.advance`.
- **`safeDisplacement.test.js`** — current tile deep → moves to nearest passable; channel cancelled; no local tile → `lastHighSafeTile`; none → start; event emitted. *Calls:* `debug.tide.setLevel(2)`, `debug.player.set`, `debug.advance`, `debug.player.state`, `debug.level.setTile`, `debug.events.last`.
- **`fog.test.js`** — entering a tile reveals radius 10; revealed persists; LOS blocked by elev > player+1; water does not block LOS; nothing outside radius revealed. *Calls:* `debug.fog.clear/isRevealed`, `debug.player.set`, `debug.level.setTile`, `debug.advance`.
- **`landmarks.test.js`** — within 24 + LOS discovered; beyond 24 not; no LOS not; event fires; sector landmark discovers sector; hunt area reveals after Key 1 + landmark. *Calls:* `debug.landmarks.discovered/discover`, `debug.player.set`, `debug.keys.set`, `debug.advance`, `debug.events.last`.
- **`caches.test.js`** — Key 1 available at start; Keys 2–5 sealed before Key 1; sealed → `cache_sealed_prompt`; after Key 1 others available when visible; channel completes after its time; move/map-release cancel; opened stays open; blockers removed; key + 10 coins granted; clue added for 1–4, none for 5. *Calls:* `debug.caches.state/open`, `debug.keys.set`, `debug.player.set`, `debug.pressInteract`, `debug.openMap`, `debug.advance`, `debug.events`.
- **`coins.test.js`** — walking over a coin collects it; no regen; total increments; rank thresholds correct; completion works with 0 coins; total possible 160. *Calls:* `debug.coins.set/add/collectAll/state/rank`, `debug.player.set`, `debug.advance`.
- **`vault.test.js`** — locked <5 keys; sealed (5 keys, not low); openable (5 keys + low); channel completes only at low tide; tide-rise/move/map cancel; success +70 coins; emits `game_complete`; input disabled. *Calls:* `debug.vault.setKeys/state`, `debug.tide.setLevel`, `debug.player.set`, `debug.pressInteract`, `debug.openMap`, `debug.advance`, `debug.coins.state`, `debug.events`.
- **`clues.test.js`** — authored distances equal rounded landmark→vault distances; 0 clues no rings; 1 clue one ring; 4 clues reveal marker; overlap contains vault; overlap < 400; ring data correct for 1–4; Key 5 adds none. *Calls:* `debug.clues.set/state/overlap/validate`, `debug.clueDistance`.
- **`levelGenerator.test.js`** — level 256×256, ocean border impassable, start/vault/landmarks/caches exist; low-tide BFS (initial blockers) reaches all cache interacts + landmarks; low-tide after blockers removed reaches all rewards + vault; high-tide BFS reaches all high anchors; high-tide passable tiles connected to start; clue validation passes; coin placement passes; seeded caches valid; invalid variation → default; fallback always valid. *Calls:* `debug.newGame`, `debug.level.summary/validate/reachableFrom`.
- **`events.test.js`** — all major events present with contract payloads; no unknown events required by renderer/audio; `game_complete` payload has time, keys, coins, rank. *(Also the objectives check: `debug.keys.set(0/3/5)` + `debug.complete()` → `debug.objectives.current()` returns "Open the shipwreck barrel." / "Find the Tide Keys. 3/5" / "Open the vault at low tide." / "Treasure found.")* *Calls:* `debug.events.list`, `debug.keys.set`, `debug.complete`, `debug.objectives.current`.
- **`audio.test.js`** (stub `AudioContext`) — unlock required before start; `key_collected`→`key`, `coin_collected`→`coin`, `tide_warning`→`tide_warning`, `vault_opened`→`vault_opening`; pool caps simultaneous SFX at 8; missing assets fall back to synth without throwing. *Calls:* `debug.audio.map/play/poolSize`.

**Playthrough (`playthrough.test.js`)** — headless, seed 123, `dt 0.05`: start state (`progress START`, 0 keys) → `interactWith` Key 1 (→1 key, 1 geometric, ≥10 coins) → for Keys 2–5 `interactWith` (Key 2 gated by `waitFor(waterLevel < 0.7, 120)`) → 5 keys, 4 geometric, `vault.markerRevealed` true → `moveTowards(vault, {waitSeconds:180, requireLowTide:true})` → `interactWith` vault (1.0 s) → `complete` true, coins ≥70 and ≤160; `game_complete` event present with `keys 5` and matching `coins`. *Calls:* all from the harness set above.

**T3 additions:** multi-seed playthrough (1, 7, 42, 123, 999); completion time `< 30*60` s; no soft-lock (no exceptions, player in-world, current tile passable each update, displacement loses nothing, reaches `GAME_COMPLETE`); event order `game_start → key 1..5 → clue 1..4 (may interleave with keys) → vault_marker_revealed → vault_opened → game_complete` (relative, not exact frame).

**E2E smoke (`tests/e2e/smoke.spec.js`, T3, optional)** — page loads with no console errors; start screen visible; **Begin Salvage** hides it, shows canvas, starts audio context; movement keys change position; holding M opens map, releasing closes; HUD elements exist (tide dial, stamina, keys, coins, objective); interacting near the first cache completes the channel; no unhandled promise rejections.

**SCREENSHOTS table** *(constructed from visual §16 checklist + defined states; §0.2 ruling):*

| ID | Visual state shown | From | Check that must be true |
| --- | --- | --- | --- |
| SS-01 | Water-depth trio: dry / shallow / deep | §4.3/6 | three visually distinct states; dry brightest; shallow 30–40% teal, terrain visible; deep darker + more opaque |
| SS-02 | Elevation diff 1 step | §4.3 | small lip, light shadow, reads walkable |
| SS-03 | Elevation diff ≥2 cliff | §4.3 | tall dark face, jagged top, cast shadow, reads non-walkable |
| SS-04 | Sealed cache | §4.5/props | padlock icon, desaturated brass, prompt "Sealed. Find the first Tide Key." |
| SS-05 | Openable cache + channeling | §4.5/§10.6 | brass `[E]`, gold outline, progress ring in prompt and around prop |
| SS-06 | Single clue ring (Key 1) | §4.5/§9.8 | teal solid annulus centered on Shipwreck |
| SS-07 | Two rings overlapping | §4.5/§9.8 | two distinct colors/dashes, overlap visible |
| SS-08 | Exact vault marker | §4.5/§9.9 | red X, label `VAULT`, pulse, distinct from rings/hunt |
| SS-09 | Vault ready | §4.7/§9.9 | gold X + compass, label `OPEN` |
| SS-10 | Full map overlay | §3 map/§9 | parchment, revealed, water, flood preview, landmarks, hunt area, clue rings, player, legend |
| SS-11 | Full HUD | §7/§10.4 | tide dial LOW, stamina full, keys 0/5, coins 0/160, objective, map button |
| SS-12 | Tide warning banner | §7/§10.7 | icon + text (e.g. "High tide in 10s"), double-wave, orange; no full-screen flash |
| SS-13 | Sector discovery banner | §7/§10.8 | icon + name (e.g. "Gull Flats"), parchment, 2 s |
| SS-14 | Start screen | §7/§10.3 | title, subtitle, controls, **Begin Salvage** |
| SS-15 | End screen | §7/§10.9 | Treasure Found, rank + icon, time, coins, keys, **Restart** |
| SS-16 | Player moving (dry/water) | §5/§8.1 | dust puff (dry) vs wake (shallow); 4-dir facing |
| SS-17 | Player blocked (deep water) | §5/§8.1 | short bump + splash + shake, no damage |
| SS-18 | Low-tide moment | §6.5 | exposed shelf dry, vault cave reachable, tide-line on sand, map water lighter |
| SS-19 | High-tide moment | §6.6 | compressed, player on high ground, dial HIGH (double-wave, orange) |
