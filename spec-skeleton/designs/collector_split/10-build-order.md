# 10. BUILD ORDER

Milestones (derived from engineering’s structure and acceptance criteria — it shipped no milestone list; §0.2 ruling), each naming the §9 check that proves it landed:

| Milestone | Scope | Proof (section 9) |
| --- | --- | --- |
| M1 | Bootstrap: index.html, constants, content.js + ContentValidator, package scripts, serve | content.test.js (all assertions) |
| M2 | SeededRNG, WorldGenerator (terrain/lake/paths/buildings/nodes/fish), Pathfinding | worldGenerator.test.js + rng.test.js + pathfinding.test.js |
| M3 | GameCore, EventBus, PlayerSystem (movement/collision/scene), InteractionSystem, InventorySystem | movement.test.js + inventory.test.js |
| M4 | NodeSystem, GatheringSystem, FishingSystem | gathering.test.js + fishing.test.js |
| M5 | ShopSystem, GoalSystem, ScoreSystem | economy.test.js + shop.test.js + goals.test.js |
| M6 | BuildSystem, MuseumSystem | build.test.js + buildFurniture.test.js + museum.test.js |
| M7 | Save adapters, save/load rules, full playthrough | save.test.js + playthrough.test.js |
| M8 | Renderer + all UI (title/HUD/minimap/shop/ledger/build/toasts/completion) | e2e smoke.spec.js + screenshots S1–S16 |
| M9 | Audio (all §6 recipes, zone music, settings application) + accessibility attributes | e2e assets.spec.js + screenshot S18 |
| M10 | Completion flow + T1 polish (prompts, toasts, feedback states) | playthrough.test.js (steps 6–7) + screenshot S17 |
| M11 | T2 staging in §0.3 order (settings modal → ambience → layers → lines → hint → juice); T3 after ship | S18, assets.spec.js ambience IDs, S2 toast, S6/S17 juice states |
