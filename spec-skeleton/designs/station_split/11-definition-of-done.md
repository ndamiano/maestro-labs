# 11. DEFINITION OF DONE

One header per 0.1 row. When every header is complete, the game is complete (T1 ship = rows 1–15; full completion = row 16 as well).

**1. Runs as a browser game**
- Checks: `browser/smoke.test.js` 1–9; HUD inside the 24 px safe margin at 1080p and 1366×768.
- Screenshots: S2.

**2. Survival gameplay**
- Checks: `vitals.test.js` 1–15; `referenceWin` "player alive"; invariants: player O2/integrity in 0–100 every tick.
- Screenshots: S2, S16.

**3. Derelict space station setting**
- Checks: `level.test.js` 1–9 (10 rooms, roster sizes/O2/hull, shared-wall doors, connected graph).
- Screenshots: S3, S4.

**4. Air management**
- Checks: `atmosphere.test.js` 1–12 (drains 0.5/15, machine rates 8/4/6, airflow 5×|Δ|/100, simultaneous, clamps).
- Screenshots: S6.

**5. Power management**
- Checks: `power.test.js` 1–13 (EPC 400 s, propagation through open doors only, 2 s install, empty-node rule, display states).
- Screenshots: S3.

**6. Hull and scheduled events**
- Checks: `hull.test.js` 1–19; `resourceFairness` 3–7 (all three breaches preventable; seal to 60).
- Screenshots: S4, S5.

**7. Reactor**
- Checks: `reactor.test.js` 1–17 (180 s coolant, 20 s spin-up, abort, heat 5/sec, recovery with second cell).
- Screenshots: S7, S8, S9.

**8. Drones**
- Checks: `drones.test.js` 1–18; `noEmpWin` passes (`empUsed = 0`, B undamaged during channel).
- Screenshots: S11.

**9. Launch objective**
- Checks: `launch.test.js` 1–20; `referenceWin` asserts success before 960 s with all requirements true.
- Screenshots: S10, S11, S12, S13.

**10. Guided progression**
- Checks: `objectives.test.js` 1–11 (sequence, 5 s stabilization, no regression).
- Screenshots: S3 (objective text), S12.

**11. Items and inventory**
- Checks: `items.test.js` 1–12; `resourceFairness` 8–9 (drops recoverable; no door softlock).
- Screenshots: S2.

**12. Readable HUD**
- Checks: all 7.3 text/shape signals asserted present in HUD state; `smoke` check 5 (all panels); numbers exact, bars optional-interpolated only.
- Screenshots: S2–S16 (all).

**13. Audio feedback**
- Checks: `audioEvents.test.js` 1–16 (every required event name, no per-tick repeats); M12 smoke with audio active, zero console errors.
- Screenshots: S16 (visual counterpart — banner + vignette paired with the audible warning).

**14. End screens**
- Checks: `failureModes` 5–9 (causes, time survived, systems restored, no respawn); `referenceWin` success data.
- Screenshots: S14, S15.

**15. Deterministic, fixed-step simulation with tests**
- Checks: `invariants.test.js` 1–7; determinism rules (no `Math.random` in simulation; IDs from counters); `referenceWin` and `noEmpWin` reproduce identically across runs.
- Screenshots: S2 (a live run proves the loop).

**16. Presentation polish (T2)**
- Checks: each 0.3 T2 item implemented per its section (6.2 music triggers; 3.6 particle rules; 6.4 pan; 7.4 pulses; 3.5 texture detail; 10.M13 pre-render; 7.3 legend; 8 invariants toggle); smoke stays green.
- Screenshots: S4, S6, S11, S13 (with T2 effects).
