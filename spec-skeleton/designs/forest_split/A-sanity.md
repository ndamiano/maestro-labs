# A. SANITY

- Check: every field a rule reads or writes is in the global context.
  - Result: closes. Section 2.2 includes player, hollow, gate, pickups, objectives, onboarding, noise, and HUD fields required by section 4 rules.

- Check: every place, thing, or kind a rule names is placed by a generator or listed in a roster.
  - Result: closes. Section 4 rosters list player start, gate, gap, threshold, Dead Well, keys A B C, embers E1 to E5, zones, and content counts. No runtime generator is used for required objects.

- Check: consumable totals placed against total rules can demand along core loop.
  - Fuel: placed supply is 50 starting plus 5 embers times 40, total 250. Maximum demand is 480 seconds times 0.5 per second, total 240. Closes with 10 fuel spare. It still bites because missing one ember leaves 210 fuel, which supports only 420 seconds of continuous light.
  - Breath: sprint drain is 20 per second, full breath supports 5 seconds of sprint. Walking recovery is 15 per second, standing recovery is 30 per second, unlock threshold is 25. Standing from 0 reaches unlock in about 0.83 seconds. Closes and bites.

- Check: timing pairs close and still bite.
  - Hollow wake versus clear: minimum expected route is 550 tiles. Even theoretical full sprint at 6.0 tiles per second takes about 91.7 seconds, before gate hold, underbrush, breath, and navigation. Hollow wakes at 90 seconds. Closes and bites.
  - Fuel drain versus supply: drain demand is 240 fuel, supply is 250 fuel. Closes with 20 seconds of light spare. Bites if an ember is missed or light is used carelessly.
  - Sprint drain versus recovery: sprint drains 20 per second, walking recovers 15 per second, standing recovers 30 per second. Closes for escape pressure and bites because breath can lock.
  - Hollow hunt speed versus player sprint: Hollow hunts at 5.0, player sprints at 6.0, underbrush Hollow is 4.25, player sprint in underbrush is 5.1. Closes for escape and bites because breath limits sprint.
  - Gate hold versus decay: hold time is 2 seconds, decay is 4 per second. Closes for a 2-second hold and bites if the player releases early.
  - Path recalculation versus movement: recalculation is every 0.5 seconds, Hollow hunting speed is 5.0, so worst-case reaction step is about 2.5 tiles. Closes and bites enough to feel physical without cheating.
  - Dawn clock versus expected clear: dawn is 480 seconds, expected efficient completion is 330 to 390 seconds, cautious completion is 390 to 450 seconds. Closes and bites.

- Check: every call section 9 makes is in section 8.
  - Result: closes. Section 9 uses `createSim`, `createMockAudio`, `createMockInput`, `createMapFixture`, `loadRealMap`, `advanceSim`, `validateMap`, `renderSimFrame`, `sim.debug.*`, and `input.*`, all defined in section 8.

- Check: no placeholder in angle brackets remains.
  - Result: closes. No placeholder angle brackets remain in this document.

- Fixes applied above:
  - Moved HUD and screens to HTML and CSS DOM overlays.
  - Replaced external audio files with Web Audio API generated recipes.
  - Replaced sprite file loading with procedural canvas drawing from visual recipes.
  - Corrected safe-zone visual table so safe zone is active only at fuel 25 or higher.
  - Clarified gate threshold as y below 6 with passable gap rows 3, 4, 5.
