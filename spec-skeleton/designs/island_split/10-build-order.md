# 10. BUILD ORDER

Each milestone names the §9 check that shows it landed.

| # | Milestone | §9 check that proves it | Tier |
| --- | --- | --- | --- |
| M1 | Skeleton: file tree, `package.json`, `CONFIG`, `EventBus`, `rng`, `geometry`, boot flow | `events.test.js` (payload contract) | T1 |
| M2 | Level: `LAYOUT`, `generator`, `validator`, `fallback` | `levelGenerator.test.js` (all BFS + clue + coin + fallback checks) | T1 |
| M3 | Tide system | `tide.test.js` | T1 |
| M4 | Passability + movement + stamina + safe displacement | `passability.test.js`, `movement.test.js`, `stamina.test.js`, `safeDisplacement.test.js` | T1 |
| M5 | Fog + landmarks + hunt areas | `fog.test.js`, `landmarks.test.js` | T1 |
| M6 | Caches + keys + channels + clue rings | `caches.test.js`, `clues.test.js` | T1 |
| M7 | Coins + rank | `coins.test.js` | T1 |
| M8 | Vault + objectives + game complete | `vault.test.js`, `events.test.js` (objectives check) | T1 |
| M9 | Audio manager + event→sound mapping + pool | `audio.test.js` | T1 |
| M10 | Renderer (world + map + HUD) | E2E smoke (HUD/canvas) + SS-01…SS-19 | T1 |
| M11 | Single-seed playthrough | `playthrough.test.js` (seed 123) | T1 |
| M12 | T2: adaptive music, sector banners+motifs, collection flourishes, displacement animation, vault cinematic, landmark flourish | SS-05/SS-09/SS-12/SS-13 + audio adaptive rows | T2 |
| M13 | T3: small-screen, decorative richness, multi-seed+time+event-order, E2E, perf pass, confetti | multi-seed `playthrough`, E2E smoke, 60 FPS profile, SS-15 | T3 |
