# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Make a side-scrolling, platformer shooter | 1.1, 4.1, 4.5, 4.9 |
| At least 4 different gun types | 4.8, 4.9 |
| Character can move left or right | 4.4, 4.5 |
| Character can jump | 4.5 |
| Character can crouch | 4.4, 4.5, 4.6 |
| Story progression like Mario with worlds and stages | 4.2, 4.13 |
| Start with 2 worlds | 4.2 World Roster |
| 5 stages per world, 10 total | 4.2 Stage Roster |
| Do not simply copy Mario | 3.1, 4.2, 5.1 |
| Added: 2D gameplay with 2.5D presentation | 1.1, 3.3 |
| Added: named player, enemies, bosses, and stage identity | 4.2, 4.10, 4.11, 5 |
| Added: checkpoints, pits, hazards, and stage reset | 4.4, 4.6, 4.17 |
| Added: optional cores for completion stats | 4.13, 7 |
| Added: HUD, crosshair, damage feedback, and state screens | 7 |
| Added: generated Web Audio sound and music | 6 |
| Added: deterministic simulation and testable build | 1.2, 2, 9 |

## 0.2 Decisions

| Topic | What gameplay said | What visual said | What engineering said | Ruling and one clause why |
| --- | --- | --- | --- | --- |
| Audio implementation | Listed audio events only | Defined SFX table, music map, and asset files | Used `assets/audio` and manifest audio files | All audio is generated with the Web Audio API; no external audio files are required. This follows the integrator instruction that the game must use Web Audio generation. |
| Sprite implementation | Did not define art assets | Defined sprite sizes, palettes, animation names, and frame counts | Expected sprite sheets and `assets/sprites` | All sprites are drawn in code as flat vector shapes using the visual sizes, palettes, and animation names. No external image files are required. |
| Final authority | Mechanics authority for numbers/rules | Presentation authority for appearance/audio/UX | Architecture authority for modules/tests | This merged spec is final. Where the three docs disagreed, the ruling in this table wins. |
| Muzzle origin | Player center plus 2 standing, plus 8 crouching | Crouch lowers muzzle visually | Anchored muzzle to standing feet reference: standing 10 px above feet, crouched 4 px above feet | Use the engineering anchored muzzle formula. It keeps the muzzle inside the player body while preserving the gameplay intent that crouch lowers the muzzle. |
| Hush Warden base movement | Phase 2 increases move speed by 10 percent, but gave no base speed | No base speed | Defined base 80 px/s and phase 2 88 px/s | Use 80 px/s base and 88 px/s phase 2. This gives the 10 percent modifier a concrete value without changing the 480 px/s charge speed. |
| Crouch-only traversal | Required crouch sections and low ceilings | Crouch is visually obvious | Added `lowClearance` pixel volumes to make 12 px crouch passages possible | Use `lowClearance` rectangles for crouch-only passages. Tile resolution alone cannot express a 24 px standing block that a 12 px crouch can pass. |
| Death respawn reset | Respawn at checkpoint with full hearts and 1.0 s invulnerability | No reset rule | Reset dynamic stage state on death with lives remaining | Use engineering full dynamic reset on death. This makes checkpoints predictable and prevents impossible enemy/projectile states after respawn. |
| Camera for short stages | Clamp camera to stage bounds | Background must fill viewport | Center camera on an axis when stage is shorter than viewport | Center vertically or horizontally when a stage dimension is less than the viewport. This avoids letterboxing while keeping 960 x 540 gameplay coordinates. |
| Player update order | Gave a high-level player update order | No order | Gave a more detailed fixed-step order | Use the engineering detailed order. It resolves wind, conveyor, platform carry, and jump timing deterministically. |
| Random source | Did not define RNG | No RNG rules | Use `mulberry32` and ban `Math.random` in simulation | Use one deterministic `mulberry32` RNG per stage. Boss choices must be reproducible in tests. |
| Core notification | Allowed “Core collected, if desired” notification | No bottom-center core text; HUD counter flashes | No core notification | Use no bottom-center core notification. Cores are frequent and optional; the counter flash is the feedback. |
| Beam positioning | Null Relay Side Sweep uses random Y | Beam telegraphs are world objects | All boss beams locked to player position at telegraph start | Telegraphs lock the displayed line at telegraph start. Hush Sweep and Null Phase 3 horizontal beams use player Y at telegraph start. Null Relay Phase 1 Side Sweep uses a random valid arena Y chosen at telegraph start. This keeps the visual telegraph honest and preserves the gameplay random-Y rule. |
| Touch controls | Out of scope | No touch rules | Cut touch controls | Desktop mouse and keyboard only. The request is a browser game, but the provided design is desktop-focused. |
| Score system | No score | No damage numbers or score | No score | No score. Cores and completion stats are the only completion metrics. |
| Progress persistence | Store progress if browser storage available | Title supports Continue/New Signal | localStorage with memory fallback | T1 ships session save and in-memory save. T2 adds localStorage persistence. This keeps the core game playable without storage. |
| Presentation depth | Allowed 2.5D parallax | Defined parallax layer stack | Defined parallax as presentation only | T1 requires readable layer 4 gameplay and layer 5 VFX. T2 adds animated parallax background layers. |
| Music layering | Required state audio cues | Full music map and phase layering | Audio manager with crossfade and ducking | T1 ships basic state music loops and SFX. T2 adds boss phase layering and richer state music. |
| Screen shake | Not specified | Defined small shake events | No explicit shake architecture | T1 ships damage vignette and critical feedback. T2 adds the listed small screen shakes. |
| Render interpolation | Fixed timestep at 60 updates/s | No interpolation requirement | No interpolation | No render interpolation. The logical viewport is fixed and the target update rate is 60 Hz. |
| Object pooling | Entity limits given | No pooling rules | No pooling beyond array expiration | Use simple array expiration and entity limits. |
| Keyboard fallback | J shoots in facing direction | Facing indicator for keyboard fallback | Defined keyboard fallback aim | Use J fallback. If no horizontal input has occurred, face right. |
| World 2 modifiers | Standard enemy HP x1.15 and projectile speed x1.1 | World 2 palette changes | Standard enemies only; bosses unmodified | Use World 2 modifiers for standard enemies only. Bosses use their defined stats. |
| Stage lives | 3 lives per stage, reset each stage | No lives rule | Stage lives reset per stage | Lives reset to 3 at every stage start and retry. This keeps progression smooth and prevents long-stage death spirals. |
| Cores | Optional, 3 per stage, 30 total | Core visual and HUD counter | Core IDs and progression storage | Cores are optional, globally persistent, and used only for completion stats. |
| Boss reset | Boss resets if player dies during boss | Boss death visual | Boss resets to full HP/idle on player death | Boss resets to full HP and idle on player death with lives remaining. |
| Foreground occlusion | No gameplay depth | No gameplay-occluding foreground; edge framing max 80 px | No foreground rule | No gameplay-occluding foreground. Optional edge framing may not cover projectiles, enemies, hazards, or the player. |
| Minimap and damage numbers | No minimap or damage numbers implied | No damage numbers, no minimap | No minimap | No damage numbers and no minimap. The HUD and world telegraphs carry readability. |
| Test strategy | Fairness rules and completion definition | Final visual checklist | Route-based completion bot and deterministic tests | Use deterministic route-based completion bot for stage proof. Every production stage must have a `validationRoute`. |

## 0.3 Tiers

T1 is the game that must ship:

- FixedTimestep
- Input
- PlayerMovement
- TileCollision
- LowClearance
- Weapons
- Projectiles
- Enemies
- Bosses
- Stages
- Progression
- SessionSave
- Checkpoints
- Hazards
- Conduit
- Camera
- HUD
- SFX
- StateMachine
- Tests

T2 stages the rest, in this order:

- T2-1 localStorage persistence for Continue, New Signal, and stats.
- T2-2 animated parallax background layers for Title, Intro, Map, Stage, and End.
- T2-3 animated title background showing Sumpworks and Skyloom.
- T2-4 boss music phase layering and richer state music.
- T2-5 small screen shake events for golem stomp, boss charge impact, and boss death.
- T2-6 extra projectile trails, wind particles, and background sway.
