# 3. VISUAL SPEC

The game has a Moonlit Folk Horror look: a quiet, wet, old forest at night, with low-detail painterly tiles, silhouette-based characters, soft edges, muted blue-green ground, cold moonlight, and warm lantern amber. The forest should feel old and lived-in but not cluttered. Every visual element must answer one of four questions: where can I safely see, where am I covered, what is The Hollow doing, and where do I need to go. Warm amber belongs to the player, lantern, fuel, and safe light. Bone white belongs to keys, UI, and objective accents. Cold blue belongs to The Hollow, threat states, breath, and detection cues. Deep green and blue belong to the forest. Dawn gold belongs only to time pressure and escape. Red is not used.

Lighting and atmosphere are the core visual system. The player’s lantern is the brightest warm source in the game. When the lantern is on and fuel is above 0, the bright inner area extends to the gameplay light radius, and a dim outer area extends to light radius plus 2 tiles. Outside that range, the forest becomes very low-contrast night shadow. When the lantern is off or fuel is 0, the player sees a cold ambient halo: 3 tiles if covered, 6 tiles if uncovered. The light safe zone is shown as a soft warm edge at the light radius when active. The edge is not a hard white circle. It uses a faint amber ring or shimmer, 1 to 2 px soft. When safe is active and fuel is below 30, the edge flickers. When fuel is below 25, the edge fades and the safe zone is gone. When The Hollow is outside the safe zone, it pauses or paces at the edge.

Dawn color progression over 480 seconds:

| Time remaining | Visual state |
| ---: | --- |
| 480s | Deep night blue, cold and quiet |
| 360s | Slightly lighter moon shadow, still dark |
| 240s | Forest shadows lift very slightly, cold blue remains |
| 120s | Faint pale grey-blue at the edges, tension increases |
| 60s | Very faint dawn gold at top of screen, timer warns |
| 0 | Dawn gold wash fills the screen |

Lantern fuel visual states:

| Fuel state | Lantern flame | Light behavior | HUD state |
| --- | --- | --- | --- |
| 100 to 50 | Steady warm amber | Stable light | Normal |
| 50 to 30 | Slightly smaller, mild flicker | Stable safe zone | Normal |
| 30 to 25 | Flickering | Safe zone flickers while active | Fuel warning begins at 20 |
| Below 25 | Small sputtering flame | Safe zone gone, light weak | Clear fuel warning below 20 |
| 0 | No flame | Lantern off | Dark ambient only |

World layers:

| Z-order | Layer | Purpose |
| ---: | --- | --- |
| 0 | Base ground | Grass, path, water, cracked ground, stone floor |
| 1 | Ground decals | Roots, bones, pebbles, faint moss, stains |
| 2 | Underbrush | Passable cover |
| 3 | Objective ground glow | Key pulse, ember glow, gate threshold light |
| 4 | Entities | Player, The Hollow, pickups |
| 5 | Vertical props | Tree trunks, rocks, well rim, gate structure |
| 6 | Weather and mist | Low mist, drifting leaves, faint dust |
| 7 | Lighting mask | Lantern light, ambient darkness, dawn color grade |
| 8 | Screen effects | Vignette, cold pulse, warm dawn wash |
| 9 | HUD | DOM HUD overlay, not canvas-drawn |

Visual rules:

- Underbrush may tint and partially occlude the lower half of a sprite, but it must not hide The Hollow or the player unfairly.
- Tree trunks and rocks may partially occlude adjacent sprites, but they must not hide an active threat in a way that conflicts with gameplay line of sight.
- The Hollow is drawn above underbrush so its silhouette remains clear.
- Lantern light affects entities and ground, but DOM HUD is unaffected by lighting.
- No visual cover blocks line of sight unless it is an impassable tree trunk, rock, or water.
- No camera tilt, isometric projection, perspective scaling, or parallax.
- Cosmetic vertical offsets are allowed for sprites, but all gameplay uses the 2D tile grid.

Space and zone treatments:

| Zone | Visual treatment | Distinctive props | Accent | Readability goal |
| --- | --- | --- | --- | --- |
| Start Clearing | Slightly open, softer moss, fewer blockers | Young trees, small bone marker, faint path | Moss Green | Teach movement without pressure |
| Southeast Root Shrine | Exposed pale roots, small stones, shallow key alcove | Root ring, stone fragments | Pale bone and faint warm moss | First key area, readable objective |
| Central Clearing | Open, cracked pale ground, dead well at center | Dead Well, sparse underbrush pockets | Cold blue mist | High-risk space, light defense |
| Western Thorn Grove | Dense low thorn, narrower gaps, darker floor | Thorn branches, heavy underbrush | Deeper Moss Green | Stealth and cover |
| Northeast Fuel Hollow | Small dry hollow, sparse wood, ember pebbles | Dry branches, orange pebbles | Ember Orange | Optional fuel, easy to spot |
| North Gate Approach | Worn path, stone gate, moonlit clearing | Old Gate, cover pockets, dawn light | Stone Grey and Dawn Gold | Final escape tension |

Palette:

| Role | Hex | Use |
| --- | ---: | --- |
| Deep Night Black | `#05070C` | Darkness, The Hollow core, deepest shadows |
| Night Blue | `#0A1220` | Base darkness, background, unlit areas |
| Moon Shadow Blue | `#16243A` | Vignette, soft shadows, night ground |
| Forest Ground Blue-Green | `#182A2F` | Default grass/forest floor |
| Moss Green | `#223833` | Start clearing, mossy patches, soft forest floor |
| Path Grey-Blue | `#2A3540` | Worn path, open ground |
| Stone Grey | `#4B5A64` | Rocks, gate, well rim |
| Bark Dark | `#2B3132` | Tree trunks, roots |
| Bone White | `#E8E3D4` | Keys, UI text, objective accents |
| Pale Bone | `#CFC8B8` | Dim UI, empty key slots |
| Lantern Amber | `#FFB14A` | Player lantern, fuel, safe light |
| Ember Orange | `#FF7A2A` | Ember stones, fuel pickup feedback |
| Cold Moon | `#BFE8FF` | The Hollow eyes, cold rim, detection cue |
| Hollow Blue | `#355A80` | The Hollow aura, threat pulse |
| Dawn Gold | `#D8B26A` | Dawn progression, timer warning, escape light |

Recipe table:

| Item | Recipe |
| --- | --- |
| Ground tile | Fill 40 by 40 canvas with base ground color. Add low-frequency noise. Add 5 to 12 small speckles using moss or stone colors. Darken edges slightly. Add one faint darker patch. Save 3 to 5 variants per tile type. |
| Underbrush tile | Use a darker base. Add 4 to 8 low tuft shapes. Keep top edge soft. Tile is not fully opaque. Add one or two lighter highlights so it reads as passable cover. |
| Tree trunk | Draw central circular or irregular trunk shape. Add root lines. Darken base. Add faint cold edge highlight on one side. Avoid large canopies. |
| Rock | Draw angular stone shape. Add dark shadow underneath. Add faint cold wet highlight. Keep silhouette readable at small size. |
| Water | Deep Night Black with Moon Shadow Blue highlights. Slow ripple animation, 2 to 3 seconds per cycle. No bright reflection. Reads as impassable and sight-blocking. |
| Bone key | 28 by 28 px. Vertical shaft 8 by 16 px. Ring 10 px circle at top. Two small teeth at bottom. Bone White. Add 1 to 2 subtle bone texture speckles. Add soft white glow, 4 to 6 px blur. Float 1 to 2 px up and down on a 1.5 to 2 second loop. |
| Ember stone | 24 by 24 px. Rounded irregular polygon. Dark outer shell. Inner warm Ember Orange glow. Add 3 bright speckles. Slow pulse weaker than key. Optional very subtle heat shimmer. |
| Dead Well | Approximately 2 by 2 tiles. Dark water center. Stone rim. Faint pale mist. A few broken bones or roots around edge. Water darker than normal water. |
| Old Gate | Approximately 3 by 3 tiles. Large stone frame. Dark wooden or stone gate panels. Three bone key sockets visible when close. Closed gate feels sealed. Ready sockets glow faint bone white. Opening gate creaks and shifts with light leaking through gap. Open gap is clear and safe. |
| Gate threshold | 3-tile-deep pale dawn light fills threshold once gate is open. Soft gold and white mist drifts through. Edge is readable but not hard. The Hollow does not visually enter the threshold once open. |
| Player sprite | Approximately 40 by 48 px. Hooded figure. Dark blue-grey cloak. Simple silhouette. Small lantern in one hand. No detailed face. No weapon. No armor. |
| The Hollow sprite | Approximately 64 by 76 px. Tall, thin, ragged, dark, cold. Core is dense black vertical shape. Outer tendrils are semi-transparent black. Rim is faint Hollow Blue. Eyes are two small Cold Moon points. |
| Mist particles | Maximum 10 to 15 visible. Slow drift. Soft edges. |
| Ember sparks | Maximum 8 to 12 per pickup. Small amber burst. |
| Key pulse | Simple glow, no heavy particles. |
| Hollow cold pulse | Simple rim or vignette, no complex particles. |
| Dawn light | Gradient wash, not thousands of particles. |

Motion rules:

- Motion is subtle.
- No excessive screen shake in T1.
- No full-screen flashes.
- No particle overload.
- Mist drift, lantern flame flicker, key pulse, ember spark, Hollow rim pulse, dawn edge glow, small ground ripple, and brief cold vignette pulse are allowed.
- Warnings must use pulse, shape, or icon changes, not only color.
