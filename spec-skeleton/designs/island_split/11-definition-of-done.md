# 11. DEFINITION OF DONE

One header per §0.1 row; the §9 checks + SCREENSHOTS rows under each make it true. When every header is complete, the game is complete.

**1. Open-world island exploration (request).** Checks: `levelGenerator.test.js` (256×256, six sectors/landmarks/caches placed, low- and high-tide BFS reachability); `fog.test.js`; `landmarks.test.js`. Screenshots: SS-10 (map of the island), SS-11 (HUD), SS-18/SS-19 (low/high tide moments).

**2. Find treasure (request).** Checks: `vault.test.js` (opens at 5 keys + low tide, +70 coins, emits `game_complete`); `playthrough.test.js` (reaches `GAME_COMPLETE`); `coins.test.js` (rank). Screenshots: SS-08/SS-09 (marker → ready), SS-15 (end screen).

**3. 2.5D isometric fixed camera (added).** Checks: `movement.test.js` (axis-separated, substepped); E2E smoke (canvas renders, no rotation). Screenshots: SS-02/SS-03 (elevation + cliff read in iso), SS-01 (water in iso).

**4. Five Tide Keys + distance clue rings (added).** Checks: `caches.test.js` (5 keys, clues 1–4, none for 5); `clues.test.js` (rings, overlap < 400, vault in overlap, marker at 4). Screenshots: SS-06/SS-07 (rings), SS-08 (exact marker).

**5. Continuous tide + safe displacement (added).** Checks: `tide.test.js` (formula, states, warnings); `safeDisplacement.test.js` (push to nearest / lastHighSafeTile / start, channel cancel, event). Screenshots: SS-12 (warning), SS-18/SS-19 (low/high), SS-01 (depth).

**6. Hoard Map: fog, landmarks, hunt areas, marker (added).** Checks: `fog.test.js`; `landmarks.test.js` (discovery + hunt-area reveal). Screenshots: SS-10 (full map), SS-08/SS-09 (marker), SS-13 (sector banner).

**7. Stamina movement, no health/combat (added).** Checks: `stamina.test.js` (drains, regen, clamp, no-run-at-0); `movement.test.js` (walk always possible). Screenshots: SS-16 (walk/water), SS-17 (blocked, no damage).

**8. Optional coin score + end rank (added).** Checks: `coins.test.js` (collect, no regen, thresholds, 0-coin completion, total 160). Screenshots: SS-15 (rank + coin total).

**9. Web Audio SFX + adaptive music (added).** Checks: `audio.test.js` (unlock, event mapping, pool cap, synth fallback). Screenshots: n/a (audio); behavior covered by §6 recipes. (Adaptive layers = T2.)

**10. HUD, start, end screens (added).** Checks: E2E smoke (all HUD elements exist; start → play → end transitions); `events.test.js` (objective text). Screenshots: SS-14 (start), SS-11 (HUD), SS-12 (warning), SS-15 (end).

**11. Deterministic level + validation + fallback (added).** Checks: `levelGenerator.test.js` (validation passes, invalid variation → default, fallback always valid). Screenshots: SS-10 (a valid generated island).

**12. Headless tests + single-seed playthrough proof (added).** Checks: full unit suite + `playthrough.test.js` (seed 123) all green. Screenshots: n/a.
