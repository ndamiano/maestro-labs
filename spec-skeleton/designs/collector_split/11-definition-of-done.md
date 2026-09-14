# 11. DEFINITION OF DONE

One header per §0.1 row. When every header’s checks pass, the game is complete.

- **Open world collector game (single continuous map, free roam)** — worldGenerator.test (exact counts, masks, perimeter, reachability of every node/door/shopkeeper); screenshots S2, S3, S4, S5.
- **The player walks around** — movement.test (speeds 6/3, diagonal normalization, collision, doors, scene transitions); screenshot S2.
- **Collecting resources into an inventory** — inventory.test (slots, stacks 20/10/5, full behavior) + movement.test (`Bag Full`); screenshot S15.
- **Harvest berries** — gathering.test (berry: yield = stack, bonus rule, empty/respawn 20/45/120s, cancel); screenshot S3.
- **Mine ores** — gathering.test (ore: 3 charges, 1.20s T1, respawns 300/360/720s); screenshot S4.
- **Fish fish** — fishing.test (full state machine, zones, cooldowns, leave-fail); screenshots S5, S6.
- **Sell them to a shop keeper for each type** — shop.test + economy.test (per-category sells, pre-update prices, supply +n/5, recovery, tiers 5/25); screenshots S7, S8.
- **Buy furniture to decorate their home** — economy.test (buy rules, unique) + buildFurniture.test (place/score/refund); screenshots S9, S10.
- **Decorate a small museum-type building** — museum.test (cases, slots 9, assignment, unassignment, score, unlock); screenshot S11.
- **(added) Relaxed no-fail fantasy** — content.test (no health/fail fields in content or state); playthrough.test (no failure path exercised); DoD invariant: no rule can end the game.
- **(added) Purchasable tool tiers** — economy.test (tool rules: higher-tier only, replace, no resell) + gathering.test/fishing.test (tier tables 0.80/0.65/0.55, 1.20/0.95/0.80, green/yellow/cooldown values).
- **(added) Goals ending in Curator’s Seal** — goals.test (all six, latching, rewards) + playthrough.test (full completion, latch survives save/load); screenshot S17.
- **(added) Collection log & specimen curation** — museum.test (unlock on first collect, 9 specimens, uniqueness) + goals.test (fullCollection); screenshot S13.
- **(added) Supply-meter price fluctuation** — economy.test (multipliers 1.00/0.85/0.70/0.60, floor 1, recovery); screenshot S7.
- **(added) Non-binding Home/Museum scores** — buildFurniture.test + museum.test (value = ceil(cost/10); formulas); screenshot S14.
- **(added) Save/load persistence** — save.test (full round-trip, corrupted-save safety).
- **(added) Accessibility settings** — e2e smoke (data attributes applied) + §4.12 effects; screenshot S18.
- **(added) Deterministic world (seed 42)** — worldGenerator.test (repeat-identical, min distance ≥3, quotas exact) + rng.test.
- **(added) Cozy hand-painted pixel look** — visual acceptance: SCREENSHOTS S1–S18 pass (palette, no hard outlines, zone identity, ghost colors, no color-only states, 12px minimum text, node/charge/fish states readable).
- **(added) Calm generated audio** — e2e assets (every recipe renders) + §6 table complete (26 SFX + 15 music/ambience recipes) with volume defaults 0.7/0.8/0.5.
