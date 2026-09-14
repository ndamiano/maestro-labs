# A. SANITY

Re-read of §2, §4, §8, §9, checked and fixed in place:

1. **Global-context completeness** — walked every field the §4 rules read or write: `time, scene, player.{x,y,coins,tools,inventory}, target, activeGather, fishing, build, nodes, fishSpots, shops, sales, collection, buildInventory, nextInstanceId, placed, goals, museumUnlocked, completion, settings`. *Finding: engineering’s state shape (§10) omitted `activeGather`, `fishing`, `build`, and `target` while its own §17/§18/§20 referenced them.* **Fixed**: all four added to §2.2 as non-persisted fields. **Closes.**
2. **Places/things/kinds placed or rostered** — 9 resources → generator quotas + submasks (§4.2); 26 fish spots → generator; 3 shopkeepers → content positions; 2 doors + 2 exits + footprints → buildings roster; 6 path runs → generator; 5 zone masks → content/constants; start tile `(57,70)` → content; 18 furniture + 9 tools → content roster; 6 goals, 9 specimens → content. No rule names an unplaced thing. **Closes.**
3. **Consumables: placed vs demanded** —
   - Berries: 50 nodes × 1–2 = 50–100 per respawn cycle (20–120s) vs demand 25 sold + 9 collection ⇒ **closes** (≥4 cycles of headroom; respawns restore).
   - Ores: 41 nodes × 3 = 123 charges (respawn 300–720s) vs 25 sold + collection ⇒ **closes**.
   - Fish: 26 non-depleting spots, cooldown ≤ 3.0s vs 25 sold + collection ⇒ **closes**.
   - Furniture: demand = 12 museum + 5 home placed vs supply = 14 decor kinds (repeatable, tier-1 from start) + 4 unique display (3 required by Open Museum; 4 required by the 9 slots) ⇒ **closes**.
   - Coins (worst case for the full goal set): 25 start + 235 goal rewards + minimum sale income. Minimum sale income occurs when all 25+25+25 units are dumped at supply 3.0 (0.60 multiplier, floor 1): 25×`max(1,floor(2×0.6))` + 25×`floor(4×0.6)` + 25×`floor(4×0.6)` = 25×1 + 25×2 + 25×2 = 125. Total = 385. Maximum required spend: 4 display cases (40+35+80+80 = 235) + 8 museum decor @10 = 80 + 5 home decor @10 = 50 ⇒ 365. 385 ≥ 365 ⇒ **closes** (margin 20; supply recovery only widens it).
4. **Timing pairs** —
   - Pick (0.55–0.80s) vs berry respawn (20–120s): **closes**.
   - Full ore node work (3 × 0.80–1.20s = 2.4–3.6s) vs regrow (300–720s): **closes**.
   - Fishing worst cycle: cast 0.6 + wait ≤ 3.0 + meter 1.5 + cooldown ≤ 3.0 = ≤ 8.1s vs non-depleting spots: **closes**.
   - Supply drain (+n/5, cap 3.0) vs recovery (1/120s): worst 3.0 → 0.0 in 360s; price floor 1 prevents permanent ruin: **closes**.
   - Travel: longest village→zone leg ≈ 28 tiles (plaza y=66 to berry edge y=38) = 4.7s at 6 t/s, within the 3–6s design band: **closes**.
   - Bite meter: green window 0.30s/1.5s at 60Hz ≈ 18 frames in-zone; yellow fallback 40–70%: **closes AND bites** (still a timing skill).
   - End-condition clock: no timer exists; the 2–3h target is pacing guidance, not a rule: **closes** (nothing to miss).
5. **Progression graph** — Open Museum needs 3 display cases; only 2 are tier-2 (small_display_case, pedestal), so a tier-3 (25 category sales) is required first — reachable in-world ⇒ **closes**. Curator’s Seal needs 9 slots = all 4 cases, including the two tier-3 cases, whose unlock sales (25 ore, 25 fish) are already requirements of the same goal ⇒ **closes**.
6. **Every call in §9 is in §8** — calls used: `core.{init,newGame,update,setMoveInput,interactDown,interactUp,openShop,closeShop,buyItem,sellOne,sellStack,sellAll,openLedger,closeLedger,toggleBuild,selectBuildItem,selectPlacedItem,rotateBuildItem,setBuildAnchor,placeBuildItem,removePlacedItem,sellBuildItem,assignSpecimen,setSettings,saveGame,loadGame,setPaused}`; `harness.{createHeadlessGame,advance,getEvents,interactFor,releaseInteract,teleport,walkTo,findPlaceableTile,MockRNG}`; `debug.{setCoins,teleport,setScene,giveResource,clearInventory,fillInventory,setNodeState,fillAllNodes,setFishing,setFishCooldown,setSupply,setCumulativeSold,giveFurniture,forcePlace,clearFurniture,collectAll,setGoalComplete,readScores,saveNow,loadFresh,resetAll,toast,openSettings}` — all present in §8.1–8.3. **Closes.**
7. **Placeholders** — no angle-bracket placeholders exist in the merged spec; the three source documents contained none either. **Closes.**

All checks pass; sections above already carry the one fix (item 1). The spec is final.
