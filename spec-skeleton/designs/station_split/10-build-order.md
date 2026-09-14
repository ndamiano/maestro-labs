# 10. BUILD ORDER

Milestones derived from engineering's structure and DoD; each names the section-9 check that shows it landed.

1. **M1 — Level and contracts.** Files exist (2.1); `compileLevel` + `validateLevel`; `createInitialState`. *Landed when: `level.test.js` checks 1–15 pass.*
2. **M2 — Fixed-step loop, movement, doors.** `gameLoop`, `advance` skeleton, player point movement, door channels. *Landed when: movement/doors tests checks 1–12 pass.*
3. **M3 — Atmosphere and vitals.** Room O2, machines, airflow, player O2/integrity. *Landed when: `atmosphere.test.js` 1–12 and `vitals.test.js` 1–15 pass.*
4. **M4 — Power.** Sources, nodes, propagation, display, loss. *Landed when: `power.test.js` 1–13 pass.*
5. **M5 — Hull and events.** Patch/seal, scheduled events with retargeting. *Landed when: `hull.test.js` 1–19 pass.*
6. **M6 — Reactor.** Pump, coolant, core, spin-up, online, heat. *Landed when: `reactor.test.js` 1–17 pass.*
7. **M7 — Drones.** States, pathing, attacks, EMP, containment. *Landed when: `drones.test.js` 1–18 pass.*
8. **M8 — Items and channels.** Inventory, drops, channels, machines. *Landed when: `items.test.js` 1–12 and `channels.test.js` 1–14 pass.*
9. **M9 — Launch, objectives, warnings, end states.** *Landed when: `launch.test.js` 1–20, `objectives.test.js` 1–11, `audioEvents.test.js` 1–16 pass.*
10. **M10 — Determinism and acceptance.** Invariants in tests; scripted wins and failures. *Landed when: `invariants.test.js` 1–7, `referenceWin`, `noEmpWin`, `failureModes` 1–9, `resourceFairness` 1–9 pass.*
11. **M11 — Presentation.** World render (11-step order), textures, map, HUD, title, end screens. *Landed when: `browser/smoke.test.js` 1–9 pass and screenshots S1–S16 match.*
12. **M12 — Audio wiring.** Web Audio synthesis from 6.3/6.4; loops and swaps. *Landed when: `audioEvents.test.js` 1–16 still pass and smoke test reports zero console errors with audio active.*
13. **M13 — T2 items (0.3 order).** Music layers → airflow/breach particles → cosmetic particles → positional pan → warning pulse + bar interpolation → texture detail → static pre-render → title icon legend → browser invariants toggle. *Landed when: smoke stays green and S4/S6/S11/S13 show the new effects; music verified by layer triggers per 6.2.*
