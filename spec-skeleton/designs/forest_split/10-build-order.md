# 10. BUILD ORDER

| Milestone | Work | Check that shows it landed |
| --- | --- | --- |
| M0: Project shell | Create files, package.json, input, clock, RNG, event bus, math helpers. | CORE-001, CORE-002, CORE-004, CORE-005 |
| M1: Map and validation | Create `assets/map.json`, Map class, validator. | MAP-001 to MAP-008, CONTRACT-001 |
| M2: Player movement and breath | Collision, underbrush, sprint, breath lock. | COL-001 to COL-003, PLAYER-001 to PLAYER-008 |
| M3: Light and perception | Light radius, safe zone, LOS, hearing. | LIGHT-001 to LIGHT-007, PERC-001 to PERC-011, LOS-001 to LOS-004 |
| M4: Pathfinding and Hollow | A*, no-path fallback, Hollow state machine. | PATH-001 to PATH-006, HOLLOW-001 to HOLLOW-014 |
| M5: Pickups and gate | Keys, embers, gate hold, threshold. | PICKUP-001 to PICKUP-005, GATE-001 to GATE-004 |
| M6: Win, fail, retry | Sim states, win priority, fail checks, retry. | SIM-001 to SIM-008 |
| M7: Audio, UX, render | Web Audio recipes, DOM HUD, screens, renderer. | INTEG-001 to INTEG-005, UX-001 to UX-008, SHOT-01 to SHOT-24 |
| M8: Integration playthroughs | Full route and gate under threat. | INTEG-013, INTEG-014, INTEG-015 |
| M9: Performance and smoke | Performance budget, manual browser smoke. | PERF-001 to PERF-003, manual smoke checklist in section 11 |
