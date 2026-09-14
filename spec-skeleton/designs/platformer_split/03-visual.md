# 3. VISUAL SPEC

The look is rust-circuit industrial: a dying maintenance city re-awakened by signal light. Presentation is flat vector, high-contrast, and limited-palette. The player is a compact courier with a cyan visor. Safe signal systems are cyan. Collectibles and special weapon energy are amber. Enemy damage, hazards, and boss energy are red or orange. World 1 is cold, wet, rusty, and oppressive. World 2 is brighter, airy, wind-swept, and more exposed. The end state resolves into coherent cyan and white signal light. No Mario-like pipes, coins, mushrooms, castles, or flagpoles are used.

Lighting and atmosphere:

- No photographic realism.
- No anime style.
- No heavy 3D rendering.
- No hand-painted clutter.
- Background areas behind gameplay should not drop below roughly `#121820`.
- Enemy projectiles must always have a white or bright core.
- Player projectiles must be visually distinct from enemy projectiles.
- Spikes must never match the color of the floor they sit on.
- One-way platforms must have a brighter top edge than the background.
- Boss telegraphs must be visible against both World 1 and World 2 backgrounds.
- No full-screen red flash beyond vignette.
- No gameplay-occluding foreground.
- Optional edge framing may cover no more than 80 px on any side.
- Edge framing may not cover the center of the screen.
- Edge framing may not obscure projectiles, enemies, hazards, or the player.

Space:

- Gameplay is strictly 2D.
- Presentation may use parallax background layers.
- Parallax is presentation only.
- Parallax must not imply gameplay depth.
- No camera rotation.
- No Z-axis gameplay.
- Stages shorter than the viewport are centered on the short axis and filled by background.
- The gameplay layer always occupies 960 x 540 logical pixels.

Core palette table:

| Name | Hex | Use |
| --- | --- | --- |
| Void Dark | `#0B1017` | Backgrounds, shadows, UI backgrounds |
| Deep Steel | `#1C2530` | Mid-background panels, walls |
| Steel | `#3A4856` | Neutral structures |
| Rust Dark | `#7A3E33` | World 1 metal, pipes |
| Rust Light | `#B86B4F` | Rust highlights, enemy armor |
| Oil Teal | `#2E5F5A` | World 1 canal water, wet metal |
| Water Dark | `#153136` | Pits, canal depths |
| Signal Cyan | `#4BE2FF` | Player, checkpoints, conduit, active UI |
| Signal White | `#F5FBFF` | Cores, highlights, beam cores |
| Signal Amber | `#FFB347` | Tuners, collectible accents, Sifter, warnings |
| Danger Red | `#FF4F5A` | Enemy damage, spikes, boss, danger |
| Warning Orange | `#FF8B3D` | Enemy projectiles, telegraphs |
| Heart Pink | `#FF7D9B` | Signal hearts, warm pickups |
| UI Neutral | `#D7DDE4` | Text, inactive UI |
| UI Dark | `#303841` | Locked UI, disabled slots |

Color semantics:

| Color | Meaning |
| --- | --- |
| Cyan | Player, safe signal, active systems, checkpoints, conduit, active UI |
| White | Pure signal, cores, beam centers, high-value highlights |
| Amber | Collectibles, tuners, Sifter, special weapon energy, mild warnings |
| Red or Orange | Enemy attacks, damage, hazards, boss energy, locked objectives |
| Neutral steel or rust | Environment |
| Pink | Health |

Parallax layer table:

| Layer | Content | X parallax | Y parallax | Notes |
| ---: | --- | ---: | ---: | --- |
| 0 | Sky or gradient | 0.0 | 0.0 | Static or slow vertical interpolation only |
| 1 | Far silhouette | 0.12 | 0.04 | Distant pipes, spires, market frames |
| 2 | Mid structures | 0.28 | 0.10 | Pipes, catwalks, shelves, clouds |
| 3 | Near props | 0.55 | 0.19 | Non-interactive props, lamps, cloth, cables |
| 4 | Gameplay layer | 1.0 | 1.0 | Tiles, player, enemies, projectiles, pickups |
| 5 | VFX layer | 1.0 | 1.0 | Sparks, beams, particles, telegraphs |
| 6 | HUD layer | 0.0 | 0.0 | UI, HUD, notifications |

Typography table:

| Use | Size |
| --- | ---: |
| Title logo | 64 px |
| World label | 28 px |
| Main menu button | 24 px |
| HUD text | 16 px |
| Notification text | 18 px |
| Stage name card | 40 px |
| Small UI text | 12 px |

UI shape grammar:

- Corner radius: 6 px.
- Border: 2 px.
- Panel background: `#0B1017` at 82 percent opacity.
- Primary border: `#4BE2FF`.
- Secondary border: `#3A4856`.
- Danger border: `#FF4F5A`.
- Text: `#D7DDE4`, unless highlighted.
- Button hover: cyan border, white text, 1 px upward shift.
- Confirm: 80 ms white flash.
- Deny: red border, 0.15 s horizontal shake, low deny sound.

Stage object grammar:

| Object | Visual meaning |
| --- | --- |
| Spike | Immediate damage, red tip |
| Conveyor | Movement aid, animated cyan arrows |
| One-way platform | Safe floor from below, cyan top edge |
| Moving platform | Temporary floor, rust slab, cyan edge |
| Wind zone | Visible force, cyan or pale streaks and arrows |
| Checkpoint | Safe respawn beacon |
| Core | Optional signal collectible |
| Signal Heart | Health |
| Tuner Shard | Weapon unlock |
| Conduit | Stage exit |

Visual rules that become gameplay rules:

- No bottom-center text notification for core collection.
- Cores are shown only by HUD counter flash.
- Boss telegraphs are world objects, not HUD-only warnings.
- Crosshair is hidden OS cursor in Stage state.
- Crosshair expands 14 px for 0.05 s on shoot.
- Crosshair dims to 50 percent when mouse leaves window.
- Keyboard fallback shows a small cyan facing arrow 16 px from player center.
- Damage vignette is `#FF4F5A`, alpha 0.35, duration 0.3 s.
- Player sprite flickers during invulnerability with alpha alternating 0.35 and 0.9 every 0.08 s.
- Lost heart pulses scale 1.2 for 0.4 s.
- Weapon slot deny shakes for 0.15 s with red border flash.
- Beam telegraph is dashed red or orange with edge arrows.
- Active beam is solid red or orange with white core.
- Beam width is 24 px.
