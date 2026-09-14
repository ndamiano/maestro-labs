# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Runs as a browser game (page, canvas, keyboard; no installs, no assets pipeline) | 1.1, 2.1, 10 (M11), 9 (browser smoke) |
| Survival gameplay: the player has survival stats, stats can run out, failure ends the run | 4.4 (Player Vitals), 4.14 (End States), 11 |
| Set in a derelict space station: one derelict orbital station, 10 compartments, no exterior, is the entire world | 4.2 (Room roster), 3.3 (Space), 11 |
| *added* Air management: room O2, airflow through doors, O2 machines, player O2 | 4.7 (Atmosphere) |
| *added* Power management: timed sources, installable cells, propagation through open doors | 4.8 (Power) |
| *added* Hull integrity with three scheduled breach events and patches | 4.9 (Hull and Breach) |
| *added* Reactor: coolant, spin-up, online power, heat hazard | 4.10 (Reactor) |
| *added* Threat: exactly two maintenance drones, avoidable without items | 4.11 (Drones) |
| *added* Objective: launch the shuttle before de-orbit (960 s), multi-requirement final channel | 4.12 (Launch), 4.14 |
| *added* Guided progression: 9-objective chain and pacing | 4.13 (Objectives), 4.15 |
| *added* Items and inventory: 6 slots, stacks, drops persist, fairness counts | 4.16 (Items and Inventory) |
| *added* Readable HUD: vitals, room status, map, checklist, warnings, log, prompt | 7 (UX) |
| *added* Audio feedback: every warning and major event has a sound, synthesized at runtime | 6 (Audio) |
| *added* End screens: success and failure with cause and stats, restart | 7.5, 4.14 |
| *added* Deterministic, fixed-step simulation with a full headless test suite | 1.2, 8 (Debug API), 9 (Tests) |
| *added* Presentation polish: music layers, particles, positional pan, texture detail | 3, 6.2, 0.3 (T2) |

## 0.2 Decisions

| Topic | Gameplay said | Visual said | Engineering said | Ruling |
| --- | --- | --- | --- | --- |
| Audio delivery | Lists 15 required audio events; "sound specificity is not part of this document" | SFX designs and music stems described, implying sound files | `.ogg` asset manifest with missing-file fallback | **No audio assets.** All SFX and music are synthesized at runtime with the Web Audio API from the recipes in 6; the event names in 6.4 are the contract; a missing recipe logs a console warning and plays nothing. One clause why: the build is a self-contained browser page and the builder must own every sound. |
| Player O2 zero-air bucket | "0 → −3/sec" | silent | "room O2 below 1 → −3/sec" | **Room O2 below 1 uses the −3/sec bucket** (engineering 30.3). One clause why: O2 is continuous, so a room at 0.4 is zero air. |
| Direct item-use key | silent | "USE SELECTED ITEM: E if applicable, or F" | E = station interact/pickup, F = direct item use, Q = drop | **Engineering's mapping** (E pick up / hold channel, F press instant use, F hold EMP, Q drop); all prompts display F. One clause why: E is already the channel key, so one direct-use key keeps prompts unambiguous. |
| Drone alert delay | "Alert delay: 1 second" | silent | delay omitted | **Carry the 1-second delay:** drone lingers in patrol 1 s before switching to alert (4.11). One clause why: gameplay's number governs; the omission was a gap. |
| Power cell node rule | "installed in an unpowered node" | silent | node empty = no local source; propagated power allowed | **Engineering's rule** (15.3): a cell installs into a node with no local source even if the room is powered by propagation. One clause why: otherwise cells cannot extend the grid they are meant to extend. |
| EMP consumption | "Use time: 1 second. Consumed instantly." | silent | 1 s channel, consumed on completion | **1 s channel, consumed only on completion** (4.11, 4.17). One clause why: an interrupted EMP must not burn a charge; consistent with every consumable channel. |
| Coolant-application feedback | silent | no dedicated SFX | unresolved (event/audio deliberated, no final) | **Event `reactor_coolant_applied`, audio `repair_complete`, log "Reactor coolant applied"** (6.3). One clause why: stable event name, and a generic mechanical completion sound is safe. |
| Spin-up abort feedback | "Spin-up aborts. Progress resets to 0." | silent | use `ui_error` | **Event `reactor_spinup_aborted`, log "Reactor spin-up aborted", audio `ui_error`** (6.3). One clause why: an abort is a soft failure, not a launch reset. |
| Warning priority | silent | 9-item priority list | 12-item priority list | **Engineering's 12-item list** (4.13): it splits coolant low/expired and adds low vitals while preserving visual's relative order. One clause why: superset that keeps visual's ordering. |
| Render layer order | silent | 7 draw groups | 11-step draw order | **Engineering's 11-step order** (3.4). One clause why: it refines visual's grouping and pins player and drones above particles. |
| HUD placement | "top-left or bottom-left, depending on visual layout" (defers) | concrete layout diagram and component locations | component list only | **Visual's layout wins** (7.2). One clause why: visual owns screen placement and gameplay deferred to it. |
| Fonts | silent | Inter/Roboto + monospaced numerals recommended | no assets implied | **System font stacks, no downloads:** labels `Inter, Roboto, "Segoe UI", system-ui, sans-serif`; numbers `ui-monospace, "JetBrains Mono", "IBM Plex Mono", monospace`. One clause why: offline browser page; visual's "or similar" permits fallbacks. |
| Restart / pause | "no respawn, no checkpoint, no retry from mid-run" | "No pause menu in core run; restart returns to title or restarts run" | no pause; restart button → fresh initial state | **No pause.** End screens have RESTART (immediately a fresh run) and TITLE (back to title). One clause why: fastest retry fits the 16-minute session and visual permits either target. |
| Screenshots table | silent | 14-item Visual QA Checklist, no table | silent | **The 9 SCREENSHOTS table is constructed from visual's QA checklist plus its end screens** (9.3). One clause why: the build spec needs concrete screenshot rows and the checklist defines the states; no QA check is dropped (each maps to a row or an 11 accessibility check). |
| Player renderer | silent | player sprite with 7 states | render file list omits a player module | **Add `src/render/playerRenderer.js`** (2.1). One clause why: visual specifies a player sprite; engineering's omission was a gap. |
| State omissions | silent | n/a | `state.channels` defined in 13.1 but absent from the 4.3 state shape | **Add `state.channels`, `meta.nextItemId`, `player.facing` to 2.2.** One clause why: channel progress, item IDs, and visor facing must live in the serializable state. |
| Wrench scope | "required for repairs and jammed doors" | silent | enumerates required and not-required uses | **Engineering's list:** wrench required for machine repairs, jammed door repair, hull patch/seal; not required for door open/close, power cell install, coolant use, fuel line, launch computer, reactor spin-up (4.17). One clause why: explicit scope prevents over-gating. |
| Launch pad range | "player must remain at the launch pad" (no number) | silent | 1.5 tiles | **1.5 tiles** (4.12). One clause why: engineering pins the number; it matches the machine interaction range. |
| Player speed | silent | silent | 3.5 tiles/sec | **3.5 tiles/sec** (4.3). One clause why: it outruns an alert drone (3.0) with margin, as the design requires. |
| Drone patrol waypoints | "two or three fixed waypoints" | silent | three deterministic waypoints | **Three: room center, top-left inset, bottom-right inset** (4.11). One clause why: engineering pins gameplay's open range. |
| Music tier | silent | full music identity (9 stems) | MusicManager with crossfades | **All SFX are T1; all music layers are T2** (0.3). One clause why: every mandatory warning already has a T1 SFX; music is atmosphere, not information. |
| Particles tier | silent | airflow/breach/EMP/steam particles | particle budgets | **T1 ships with core feedback only** (damage flash, vignette, flicker, shake) and a no-op particle system; airflow, breach, spark, steam, EMP particles are T2 (0.3). One clause why: every state is already readable via HUD, map, labels, and sound; particles decorate, they do not inform. |
| Hull event retargeting | fallback chains per event | silent | recalculate target every tick during the 10 s warning | **Recalculate every tick using gameplay's candidate chains** (4.9). One clause why: "never target the current player room" must stay fair. |
| Airflow simultaneity | "apply transfer from higher to lower" | silent | compute from start-of-phase values, apply simultaneously | **Simultaneous transfer** (4.7). One clause why: removes iteration-order dependence. |
| Reactor heat condition | "reactor online but coolant has expired" | silent | `spinUpComplete and not coolantActive` | **`spinUpComplete and not coolantActive`** (4.10). One clause why: the conditions are identical, and a reactor that never spun up must not become a heat trap. |
| Launch pause vs reset | "leaves pad / damaged / requirement fails → reset" | silent | releasing E pauses; leaving resets | **Releasing E at the pad pauses; leaving the pad or any requirement failing resets** (4.12). One clause why: releasing E is not an interruption; leaving the pad is. |
| Random source | "no RNG is required for core progression" | silent | no `Math.random` in simulation; renderer may | **`Math.random()` is the one random source, used only in `src/render/particleSystem.js`; simulation, audio, and input never randomize** (1.2). One clause why: one audited source keeps every run deterministic and testable. |
| Browser smoke test | silent | silent | "optional but recommended" | **T1**, part of Definition of Done. One clause why: browser wiring is ship risk that Node tests cannot cover. |

## 0.3 Tiers

**T1 — the game that must ship, by system name:** Level compile and validation; Fixed-step simulation; Movement and doors; Player vitals; Atmosphere; Power; Reactor; Hull and scheduled events; Drones; Items and inventory; Channels and machines; Launch; Objectives; Warnings and event log; End states and end screens; Title screen; Core HUD (all sections in 7.2); Core SFX (all 6.3 rows); Invariants; Test suite (all 9.1–9.2 files including acceptance); Browser smoke test.

**T2 — staged polish; each item is independent of the others; add in this order:**
1. Music layers (base, low O2, power loss, reactor, coolant low, final countdown, success, failure; 0.5 s crossfades) — 6.2.
2. Airflow particles through open doors and breach vacuum streaks — 3.6.
3. Cosmetic particles: repair sparks, EMP ring, reactor steam, dust puffs, boot dust — 3.6, 10.
4. Positional pan (drones, machines, adjacent-room breaches) — 6.4.
5. Warning-banner pulse (max 2 Hz) and HUD bar interpolation — 7.4.
6. Procedural texture detail: scratches, wear stains, caution stripes — 3.5.
7. Static world pre-render to offscreen canvas — 10.
8. Title-screen state icon legend — 7.3.
9. Browser debug-invariants toggle (`dbg.invariants(on)`) — 8.

Every system in section 4 is tagged `Tier: T1` where specified; T2 items above are presentation only and never gate a T1 check.
