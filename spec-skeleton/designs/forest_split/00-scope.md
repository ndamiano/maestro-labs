# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Explore a haunted forest at night | Section 3, Section 4, Section 5 |
| Escape before dawn | Section 4.2, Section 4.11, Section 7 |
| Added: one handcrafted 2D top-down forest map | Section 1, Section 3, Section 4 |
| Added: lantern fuel as a core resource | Section 4.4 |
| Added: sprint breath as a core resource | Section 4.3 |
| Added: one readable hunter, The Hollow | Section 4.7, Section 5 |
| Added: three bone keys required to open the gate | Section 4.5, Section 4.6 |
| Added: Old Gate threshold win zone | Section 4.6, Section 4.11 |
| Added: readable visual and audio cues | Section 3, Section 5, Section 6, Section 7 |
| Added: retry resets the entire run | Section 4.1, Section 7, Section 8 |
| Added: deterministic, headless-testable simulation | Section 1, Section 2, Section 8, Section 9 |
| Added: HTML and CSS screens and HUD | Section 7 |
| Added: generated Web Audio API sound and music | Section 6 |
| Added: title screen and end screens | Section 7 |
| Added: map contract validation and scripted playthrough tests | Section 9, Section 10, Section 11 |

## 0.2 Decisions

| Topic | What gameplay said | What visual said | What engineering said | Ruling and one clause why |
| --- | --- | --- | --- | --- |
| HUD implementation | HUD elements and warnings are defined. | Quiet HUD layout, bone-white text, bars, dial, arrow, prompt. | Canvas HUD via `hudRenderer.js`. | All screens and HUD are HTML and CSS DOM elements; canvas draws only the world. The prompt requires HTML and CSS only, and DOM HUD keeps canvas rendering cheaper. |
| Audio source | Audio cues are required for events. | Music and SFX direction, procedural synthesis reference. | Audio manifest with audio files. | All audio is generated at runtime with the Web Audio API from recipes in code. No external audio files are required, and the prompt requires Web Audio API generation. |
| Art assets | Visual layering is cosmetic; gameplay uses tiles. | Asset generation recipes for tiles, sprites, particles. | Sprite manifest and asset loader. | All art is drawn procedurally on canvas from the visual recipes. No external sprite files are required, and only `assets/map.json` is external data. |
| Safe-zone fuel threshold | Safe zone exists when fuel is 25 or higher. | Fuel table suggests safe-zone flicker between 25 and 20. | Safe active at fuel 25 or higher. | Safe zone is active when fuel is 25 or higher and inactive below 25. The edge flickers when active and fuel is below 30, then fades below 25. Gameplay and engineering rules win. |
| Gate threshold boundary | Gate threshold is `y < 6` and described as 3 tiles deep. | Threshold is a 3-tile-deep safe zone. | Canonical boundary is `y < 6`; map gap is rows 3, 4, 5. | Win boundary is player center y coordinate below 6. The passable gate gap is x 59, 60, 61 and y 3, 4, 5. Rows y 0, 1, 2 remain impassable. This preserves both the rule and the visual depth. |
| Camera and viewport | Target readable view is approximately 24 tiles by 16 tiles. | Internal render size is 960 by 640 px; tile size 40 px. | Camera follows player with clamp; view 24 by 16. | Exact viewport is 24 tiles wide by 16 tiles tall, 40 px tiles, internal canvas 960 by 640 px, scaled while preserving aspect ratio. Engineering precision wins. |
| Map generation | One handcrafted map, no procedural generation. | Zone treatments for one forest. | Static JSON map plus validator. | The shipped map is one static `assets/map.json` file. No runtime procedural generation is allowed. All three agree, and validation is required. |
| Corridor width rule | No corridor should be narrower than 2 tiles. | Not specified. | Hard validator rule: passable 4-neighbor count at least 3 for remaining tiles. | Adopt the engineering corridor heuristic. It is a deterministic guard against 1-tile corridors and enforces the gameplay rule. |
| Underbrush cluster definition | At least 8 underbrush clusters, 3 to 4 tiles wide. | Underbrush is passable cover. | Cluster is a 4-connected component with at least 9 underbrush tiles. | A cluster is a 4-connected component of underbrush tiles with at least 9 tiles. This makes the gameplay intent machine-checkable. |
| Gate approach target | Gate approach zone is around coordinate 60, 10. | Gate approach visual zone includes Old Gate at 60, 5. | Compass target tile is 60, 6 when gate is closed and 60, 4 when open. | The gameplay compass target is 60, 6 before the gate opens and 60, 4 after the gate opens. The visual zone remains around 60, 10. Engineering tile target wins for arrow logic. |
| Pause | Not specified as a core state. | No pause screen required. | No pause. | No pause in T1. The game is a continuous 8-minute run. |
| Accessibility modes | Warnings should be clear. | Optional reduce-motion and high-contrast modes. | Optional accessibility modes cut. | T1 implements mandatory accessibility rules: warnings use shape and pulse, Hollow has a cold rim, UI contrast is strong. Optional reduce-motion and high-contrast toggles are T2. |
| Onboarding cues | Start clearing teaches movement, sprint, lantern, arrow. | First-run cues for Move, Sprint, Lantern, arrow pulse. | Per-run onboarding text for 2 seconds. | T1 includes minimal diegetic onboarding text: Move, Sprint, Lantern, each shown once per run for 2 seconds. |
| Path smoothing | The Hollow follows waypoints. | Visual animation may smooth motion. | No path smoothing; tile-center waypoints. | Simulation uses tile-center waypoints. The renderer may apply small visual smoothing without changing sim positions or pathing. |
| Screen shake | Not specified. | Optional minimal shake for caught and gate opening. | No shake requirement. | T1 has no screen shake. Tiny shake is T2: caught 2 to 3 px for 0.2 seconds, gate opening 1 to 2 px for 0.5 seconds. |
| Music scope | Required cues include state changes and time warnings. | Adaptive music layers across the run. | Music director maps events to layers. | T1 includes generated night bed, mystery, pressure, escape, resolve, drone, and required SFX. Richer procedural music textures are T2. |
| Retry seed | Retry resets the run. | Retry prompt on end screens. | RNG can use new or supplied seed. | In browser play, retry uses a new seed from the app. In tests, retry uses the supplied seed. Determinism wins for tests. |
| Title and end screens | Win and fail conditions exist. | Title, win, caught, and dawn fail screens are specified. | DOM title and end screens implied by app layer. | T1 includes Title, Playing, Won, and Failed screens as HTML and CSS overlays. |
| Win-screen time | Win condition exists. | Optional time display `mm:ss`. | Not specified. | Win screen shows `Time: mm:ss`, where mm:ss is the elapsed run time. |
| Red color | No HUD warning color specified. | Red is not used; danger uses cold blue and dawn gold. | No color-only warnings. | No red is used anywhere. Danger and time pressure use cold blue, dawn gold, shape, pulse, and icons. |
| Cover adjacency | Covered means center in underbrush or adjacent to impassable tile. | Cover visual state changes. | Covered means underbrush or 4-orthogonal adjacent blocking tile. | Cover uses 4-orthogonal adjacency only, not diagonal. This is readable and testable. |
| Detection during Waking | Waking is non-hostile. | Waking is an 8-second telegraph. | Waking has no detection or damage. | The Hollow cannot detect, move, or harm the player during Sleeping or Waking. |
| Objective arrow frequency | Arrow updates twice per second. | Arrow appears at screen edge. | Arrow updates at 2 Hz using A* or straight fallback. | Arrow updates every 0.5 seconds. A* pathing is used when available; straight-line direction is the fallback. |
| Gate interaction radius | Gate requires held interact. | Prompt and circular progress. | Interact radius is 1.5 tiles. | The gate interaction radius is 1.5 tiles from the player center to gate center. |
| Pickup radius | Auto-pickup when overlapping. | Pickup feedback. | Pickup radius is 0.75 tiles. | Pickups occur when player center distance to pickup center is 0.75 tiles or less. |
| Initial lantern state | Starting fuel 50, lantern can be toggled. | Lantern is the primary light source. | Initial state has lantern on. | The player starts with lantern on. This matches the visual contract and makes the light system immediately readable. |

## 0.3 Tiers

T1 is the game that must ship:

- Map and Layout
- Run States and Retry
- Time and Dawn
- Player Movement and Breath
- Lantern and Light
- Pickups and Objectives
- Gate and Threshold
- The Hollow State Machine
- Perception
- Light Safe Zones
- Compass and Objective Aid
- Win and Fail Resolution
- Visual World Rendering
- Character and State Presentation
- Audio Cues and Generated Music
- HTML and CSS UX
- Debug and Test API
- Map Contract and Tests

T2 stages the remaining optional work, in this order:

1. Reduce-motion toggle: disables screen shake, replaces pulse warnings with steady changes, reduces particle bursts, slows mist and flame flicker.
2. High-contrast toggle: adds a faint cold outline around The Hollow’s fatal core.
3. Decorative ambient loops: night insects, occasional wood creaks, water ripple variation, leaf rustle variation.
4. Tiny screen shake: caught 2 to 3 px for 0.2 seconds, gate opening 1 to 2 px for 0.5 seconds.
5. Richer procedural music textures: celesta-like plucks, detuned pad layers, warmer escape pads, birds on win.
6. Extra particle polish: slightly richer mist drift, key pulse, ember spark, and gate light leak within visual budgets.
