# visual.md

## 1. Dimensionality

### Decision: 2D Top-Down with Cosmetic 2.5D Layering

The game is a **2D top-down** game with a fixed north-up camera.

- The camera is locked to north-up.
- The camera follows the player.
- There is no camera rotation.
- There is no camera zoom during gameplay.
- There is no 3D perspective.
- All gameplay collision, line of sight, movement, and threat logic uses the 2D tile grid.
- Visual layering, sprite height, shadows, and soft depth are cosmetic only.

### Cosmetic 2.5D Rules

The game may use subtle 2.5D visual depth, but it must never affect gameplay.

Allowed:

- Sprites can have vertical offsets to feel grounded.
- Tree trunks, rocks, the well, and the gate can be drawn slightly taller than their tile footprint.
- Soft shadows can suggest height.
- Mist, lantern light, and particles can drift above the ground layer.
- The player can visually sink slightly into underbrush.

Not allowed:

- No camera tilt.
- No isometric projection.
- No perspective scaling.
- No occlusion that hides The Hollow or the player in a way that conflicts with gameplay line of sight.
- No visual cover that blocks line of sight unless it is an impassable tree trunk, rock, or water.
- No parallax that changes tactical readability.

### Logical Resolution

- Tile size: **40 x 40 px**.
- Readable view: **24 tiles wide by 16 tiles tall**.
- Internal render size: **960 x 640 px**.
- The game should scale to the window while preserving aspect ratio.
- HUD elements should be anchored to screen edges.

### Why

The core fantasy depends on readable light, cover, noise, and threat behavior. A fixed top-down view makes the player’s lantern radius, The Hollow’s approach, and cover placement easy to understand. Cosmetic depth can make the forest feel like a place without making navigation or detection ambiguous.

---

## 2. Art Direction

### Style Name

**Moonlit Folk Horror**

The game should feel like a quiet, wet, old forest at night. The fear comes from what the lantern reveals, what stays hidden, and what is listening.

### Mood

- Slow and strange at the start.
- Cold and watchful after The Hollow wakes.
- Desperate near the gate.
- Briefly peaceful at dawn if the player escapes.

### Visual Language

The art should be:

- Low-detail.
- Painterly.
- Silhouette-based.
- Soft-edged.
- Slightly desaturated.
- High contrast where gameplay matters.
- Not photorealistic.
- Not cartoonish.
- Not gore-heavy.
- Not neon.

The forest should feel old and lived-in, but not cluttered. Every prop should either support cover, block movement, or communicate a zone.

### Core Rule

The visual system must answer four questions quickly:

1. Where can I safely see?
2. Where am I covered?
3. What is The Hollow doing?
4. Where do I need to go?

Anything that does not help answer one of those questions should be cut.

### Master Palette

| Role | Hex | Use |
|---|---:|---|
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

### Color Roles

The palette must be used consistently.

- **Warm amber** belongs to the player, the lantern, fuel, and safety created by light.
- **Bone white** belongs to objectives, keys, UI, and important prompts.
- **Cold blue** belongs to The Hollow, night, breath, and threat states.
- **Deep green/blue** belongs to the forest environment.
- **Dawn gold** belongs only to time pressure and escape.
- **Red is not used.** Danger is communicated with cold blue and dawn gold, not alarm red.

### Why

A limited palette keeps the game coherent across all zones. The player must be able to read danger, safety, objective, and environment at a glance. If the forest used many bright zone colors, it would become a map tutorial instead of a haunted night.

---

## 3. Readability Priorities

The visual system should prioritize information in this order:

1. **The player’s light and safe zone.**
2. **The Hollow’s current state and location.**
3. **Objective direction and key progress.**
4. **Cover and open space.**
5. **Dawn progression.**

### Readability Rules

- The player’s lantern must be the brightest warm source in the game.
- The Hollow must be readable against dark forest using a cold rim, not just a black silhouette.
- Keys must be bone-white and clearly distinguishable from embers.
- Embers must be warm orange but smaller and less bright than the lantern.
- The gate must be readable as the final objective once the player has all keys.
- Underbrush must look passable but distinct from open grass.
- Tree trunks, rocks, and water must look impassable.
- Areas outside the player’s visible range should not be pure black. Use a very low-contrast night texture so the screen does not feel empty, but it must not provide useful navigation information.

### Contrast Requirements

- UI text should be at least 80% opacity bone white or pale bone.
- Warning states should use pulse, shape, and color together.
- The Hollow’s eyes should be the coldest brightest point in the enemy sprite.
- The lantern’s safe-zone edge should be visible without becoming a hard circle.

### Why

The gameplay is about subtle choices: light on or off, sprint or walk, hide or move. If the visuals are too subtle, the player cannot learn the system. If they are too loud, the horror disappears. The art should make the choices clear but keep the atmosphere uneasy.

---

## 4. World Layers and Z-Order

The game should use a fixed layer order. This is visual only; all gameplay uses the tile grid.

| Z-Order | Layer | Purpose |
|---:|---|---|
| 0 | Base ground | Grass, path, water, cracked ground, stone floor |
| 1 | Ground decals | Roots, bones, pebbles, faint moss, stains |
| 2 | Underbrush | Passable cover |
| 3 | Objective ground glow | Key pulse, ember glow, gate threshold light |
| 4 | Entities | Player, The Hollow, pickups |
| 5 | Vertical props | Tree trunks, rocks, well rim, gate structure |
| 6 | Weather and mist | Low mist, drifting leaves, faint snow/dust |
| 7 | Lighting mask | Lantern light, ambient darkness, dawn color grade |
| 8 | Screen effects | Vignette, cold pulse, warm dawn wash |
| 9 | HUD | Timer, bars, keys, objective, prompts |

### Important Rules

- Underbrush should not fully hide entities. It may tint and partially occlude the lower half of a sprite, but The Hollow and the player must remain readable.
- Tree trunks and rocks may partially occlude adjacent sprites, but they must not hide an active threat in a way that feels unfair.
- The Hollow should be drawn above underbrush so its silhouette remains clear.
- Lantern light should affect entities and ground, but not HUD.

### Why

A fixed z-order keeps the forest coherent and prevents visual flicker. It also helps the integration agent understand how to render the game without inventing their own layer rules.

---

## 5. Environment and Tile Style

### Base Tile Style

All tiles are 40 x 40 px.

Tiles should use soft painterly shapes, not hard pixel grids. Each tile type should have 3 to 5 variants to avoid visible repetition.

Variants should differ by:

- Small color noise.
- Moss or dirt speckles.
- Slight rotation or offset of small details.
- Faint edge darkening.

### Ground / Grass

- Base color: Forest Ground Blue-Green.
- Add small moss speckles.
- Add faint dark patches for depth.
- Should read as open but soft.
- Not a bright green. It is night, so green should be muted blue-green.

### Path / Open Grass

- Base color: Path Grey-Blue.
- Slightly lighter than grass.
- Less dense detail.
- Should read as easier to move through.
- Used in clearings, gate approach, and central hub.

### Water

- Base color: Deep Night Black with Moon Shadow Blue highlights.
- Slow ripple animation, 2 to 3 seconds per cycle.
- No bright reflection.
- Should read as impassable and sight-blocking.
- Water should feel cold and still.

### Tree Trunks

- Impassable.
- Draw as circular or slightly irregular trunk bases with roots.
- Use Bark Dark with faint Moon Shadow Blue edge.
- Do not use large full canopies that block the view.
- Optional very low canopy shadows may be used, but they must not obscure entities.
- Tree trunks should be visually solid and clearly block line of sight.

### Rocks

- Impassable.
- Use Stone Grey with dark shadow and a faint cold wet highlight.
- Angular but not jagged to the point of visual noise.
- Rocks should read as blockers and possible cover-adjacent tiles.

### Underbrush

- Passable.
- Visually darker than grass.
- Use Moss Green and Forest Ground Blue-Green.
- Composed of low tufts, not tall bushes.
- Should read as cover, not wall.
- When the player enters underbrush:
  - The player sprite lowers slightly.
  - The lower half of the player is tinted darker.
  - A few grass tufts are drawn over the player’s lower body.
  - The ambient visibility halo shrinks if the lantern is off.

### Why Underbrush Must Be Low

Underbrush does not block line of sight or sound in gameplay. If it visually blocks The Hollow, the player will misunderstand stealth. Low tufts communicate “I am hidden from easy sight” without implying full line-of-sight blocking.

---

## 6. Zone Treatments

The map has one forest, but the zones must feel distinct while remaining coherent.

Distinctiveness should come from:

- Ground color shift.
- Prop type.
- Light color.
- Density of underbrush.
- Small environmental accent.

No zone should use a radically different palette.

| Zone | Visual Treatment | Distinctive Props | Accent | Readability Goal |
|---|---|---|---|---|
| Start Clearing | Slightly open, softer moss, fewer blockers | Young trees, small bone marker, faint path | Moss Green | Teach movement without pressure |
| Southeast Root Shrine | Exposed pale roots, small stones, shallow key alcove | Root ring, stone fragments | Pale bone and faint warm moss | First key area, readable objective |
| Central Clearing | Open, cracked pale ground, dead well at center | Dead Well, sparse underbrush pockets | Cold blue mist | High-risk space, light defense |
| Western Thorn Grove | Dense low thorn, narrower gaps, darker floor | Thorn branches, heavy underbrush | Deeper Moss Green | Stealth and cover |
| Northeast Fuel Hollow | Small dry hollow, sparse wood, ember pebbles | Dry branches, orange pebbles | Ember Orange | Optional fuel, easy to spot |
| North Gate Approach | Worn path, stone gate, moonlit clearing | Old Gate, cover pockets, dawn light | Stone Grey and Dawn Gold | Final escape tension |

### Start Clearing

- The start area should feel slightly safer than the rest of the forest.
- Use lighter moss and fewer blockers.
- The player should be able to understand movement, sprint, lantern, and objective arrow without immediate threat.
- A small bone marker or faint path can hint at the world’s objective language without showing a full map.

### Southeast Root Shrine

- This is the first key area.
- The key should be visible in a small shallow alcove or stone nook.
- Pale roots and stones should make the area feel ancient but not hostile.
- Underbrush near the key should teach that cover exists.
- The ember stone nearby should be slightly brighter than the key but still secondary.

### Central Clearing

- The central clearing must feel exposed.
- Use open ground around the Dead Well.
- The ground should be slightly cracked or pale to mark it as important.
- The Dead Well is the visual center of the map’s danger.
- Mist should drift slowly around the well.
- Cover pockets should be sparse and clearly readable.
- This zone should make the player think: “I can use light here, but it will cost me.”

### Western Thorn Grove

- The thorn grove should feel quieter and denser.
- Use more underbrush and lower visibility.
- Thorn branches should be low and dark, not sharp cartoon spikes.
- The key area should reward careful movement.
- This zone should visually promise safety if the player hides, while still feeling tense.

### Northeast Fuel Hollow

- This should feel like a small break.
- Use dry wood, pale stones, and faint ember pebbles.
- The ember glow should be warm but not large.
- The area should be easy to identify as optional fuel, not a hidden key zone.

### North Gate Approach

- The gate approach should feel like the threshold between forest and escape.
- Use a clearer path and stronger moonlight.
- The Old Gate should be the largest structure in the game.
- Two underbrush cover pockets should be clearly visible near the gate.
- Once the gate opens, pale dawn light should spill from the threshold.

### Why Distinct but Coherent

The player must be able to infer danger and opportunity from the environment. If every zone looks identical, the map feels flat. If every zone is radically different, the game stops feeling like one continuous night. Subtle ground and prop shifts give the player landmarks without breaking mood.

---

## 7. Lighting and Visibility

Lighting is the core visual system.

### Player Visible Range

The player’s visible area should be controlled by a darkness mask.

#### Lantern On

When the lantern is on and fuel is greater than 0:

- The lantern creates a warm light radius.
- The bright inner area extends to the gameplay light radius.
- A dim outer area extends to the gameplay light radius plus 2 tiles.
- Outside that range, the forest becomes very low-contrast night shadow.

Visual gradient:

1. Center: bright warm amber.
2. Inner radius: warm light, readable details.
3. Outer radius: dim amber fading to night blue.
4. Outside: low-contrast night shadow.

#### Lantern Off

When the lantern is off:

- The player sees only a small ambient halo.
- If the player is covered, the halo is smaller.
- If the player is uncovered, the halo is larger.
- The halo should be cold moonlight, not warm.
- Outside the halo, the forest becomes very low-contrast.

### Cover Visual State

When the player is covered:

- The player sprite should look lower and darker.
- The ambient halo should visibly shrink.
- If in underbrush, grass should partially cover the player.
- If adjacent to a rock or tree, the player should appear slightly tucked against the blocker.

This is important because cover changes gameplay visibility. The player should see their own state change.

### Light Safe Zone Visual

The gameplay light safe zone exists when:

- Lantern is on.
- Fuel is 25 or higher.
- The tile is within the light radius.

Visual representation:

- Show a soft warm edge at the light radius.
- The edge should look like the outer limit of the lantern’s influence.
- It should not be a hard white circle.
- Use a faint amber ring or shimmer, 1 to 2 px soft.
- When fuel is below 30, the safe-zone edge should begin flickering.
- When fuel is below 25, the safe-zone edge should collapse or fade.
- When The Hollow is outside the safe zone, it should visually pause or pace at the edge.

### Why the Safe Zone Needs a Visual Edge

The player needs to understand that light is not just navigation. It is also defense. If The Hollow simply refuses to cross an invisible boundary, the system will feel arbitrary. A soft visible edge makes the rule readable and makes The Hollow’s behavior feel physical.

### Lantern Fuel Visual States

| Fuel State | Lantern Flame | Light Behavior | HUD State |
|---|---|---|---|
| 100 to 50 | Steady warm amber | Stable light | Normal |
| 50 to 25 | Slightly smaller, mild flicker | Stable safe zone | Normal |
| 25 to 20 | Flickering | Safe zone flickers | Fuel warning begins |
| Below 20 | Small sputtering flame | Safe zone gone, light weak | Clear warning |
| 0 | No flame | Lantern off | Dark ambient only |

### Dawn Color Progression

The night should slowly change over 480 seconds.

| Time Remaining | Visual State |
|---:|---|
| 480s | Deep night blue, cold and quiet |
| 360s | Slightly lighter moon shadow, still dark |
| 240s | Forest shadows lift very slightly, cold blue remains |
| 120s | Faint pale grey-blue at the edges, tension increases |
| 60s | Very faint dawn gold at top of screen, timer warns |
| 0 | Dawn gold wash fills the screen |

The dawn shift should be subtle until the final minute. The player should feel time passing even if they ignore the timer.

### Why

Dawn is the main time pressure. The environment should express it. A visual color shift makes the 8-minute timer feel organic instead of only a number in the corner.

---

## 8. Player Visuals

### Player Design

The player is a lone wanderer.

Visual style:

- Hooded figure.
- Dark blue-grey cloak.
- Simple silhouette.
- Small lantern in one hand.
- No detailed face.
- No weapon.
- No armor.

The player should look human and vulnerable, not heroic.

### Sprite Size

- Player visual size: approximately **40 x 48 px**.
- The visual sprite can be slightly taller than the gameplay hitbox.
- The player’s center should be the primary visible point.
- The lantern should be clearly visible on one side.

### Player States

| State | Visual |
|---|---|
| Idle | Subtle breathing, lantern flame steady or mild flicker |
| Walk | Slow 4-way or 8-way walk cycle |
| Sprint | Faster cycle, slight forward lean, small breath mist |
| Covered in underbrush | Sprite lowers, lower half darkened, grass over feet |
| Adjacent cover | Slight tuck against rock/tree, darker side facing blocker |
| Lantern on | Warm flame, light mask active |
| Lantern off | Cold ambient halo only |
| Fuel low | Flame sputters, light flickers |
| Caught | Black tendrils or shadow shape overtakes the player |

### Player Animation Notes

- Keep animations small and slow.
- Do not use exaggerated superhero movement.
- Sprint should look urgent but not comedic.
- Breath mist should appear only while sprinting, especially in cold areas.
- The player should not visually “bob” too much; top-down readability matters more than idle charm.

### Why

The player needs to feel like a person moving through a dangerous place, not a character with combat presence. Simplicity keeps attention on light, sound, and The Hollow.

---

## 9. The Hollow Visuals

The Hollow is the only enemy and the central horror. It must be readable as a state machine, not a random ghost.

### Design Philosophy

The Hollow should feel like something wrong that was sleeping in the well.

It should be:

- Tall.
- Thin.
- Ragged.
- Dark.
- Cold.
- Slightly larger than the player.
- Not human-shaped enough to be relatable.
- Not too detailed to be distracting.

### Sprite Size

- Visual size: approximately **64 x 76 px**.
- The visual silhouette can be larger than the gameplay hitbox.
- The fatal center should be the dense core of the sprite.
- Outer tendrils, shadow, and mist are decorative.
- In high-contrast accessibility mode, show a faint cold outline around the fatal core.

### Color

- Body: Deep Night Black.
- Rim: Hollow Blue.
- Eyes: Cold Moon.
- Aura: very faint cold blue.
- State accents: pale cold blue, never red.

### The Hollow States

| State | Visual Appearance | Movement Feel | Audio Cue |
|---|---|---|---|
| Sleeping | Dark shape under faint well mist, no eyes, slow breathing distortion | None | Low wet breath, well ripple |
| Waking | Mist rises, black shape straightens, pale eyes open, cold rim appears | None, 8-second telegraph | Rising groan, cold pulse |
| Curious | Dim blue rim, slow drift, head scans, low posture | Slow, wandering | Soft rustle, faint whisper |
| Investigating | Upright, leans toward target, one eye brighter, faint cold trail | Faster, purposeful | Sharp intake, low creak |
| Searching | Circling motion, head sweeps, faint ripple around feet | Medium, patterned | Low circular whisper |
| Hunting | Bright eyes, stretched silhouette, faster lurch, cold shadow stretches | Fast, urgent | High whisper, cold sting |

### State-Change Cues

Whenever The Hollow changes state, the player should receive a short cue.

Required cues:

- A brief cold blue pulse around The Hollow.
- A small audio sting or intake.
- If The Hollow is not on screen, use a subtle cold vignette pulse and audio only.
- Do not show a marker pointing to The Hollow.

### Waking Cue

At 90 seconds:

- If The Hollow is visible, the well mist rises and the shape forms clearly.
- If The Hollow is not visible, play a low groan and a brief cold vignette pulse.
- The music shifts into the pressure layer.
- The player should understand that the safe beginning is over.

### Hunting Cue

When The Hollow enters Hunting:

- The Hollow’s eyes flare briefly.
- A cold blue vignette pulse appears for about 0.5 seconds.
- A short high whisper or cold sting plays.
- The Hollow’s silhouette stretches slightly toward the player.
- This cue should be clear but not overwhelming.

### Why

The gameplay depends on The Hollow being fair and readable. The player should always understand why The Hollow is moving. A clear state-change cue prevents the feeling that The Hollow is arbitrarily appearing or chasing.

### Interaction with Light Safe Zone

When The Hollow is outside an active light safe zone:

- It should stop at the edge.
- Its shadow may stretch toward the light.
- It may pace or lean, but it cannot cross.
- If the safe zone flickers or disappears, its eyes should brighten slightly.

### Why

This makes the player’s light defense feel real. The player should see that The Hollow is being held back by light, not by invisible pathfinding.

---

## 10. Pickups and World Objects

### Bone Keys

There are three bone keys.

Visual design:

- Bone-white key shape.
- Simple skeletal form.
- Small floating animation, 1 to 2 px up and down.
- Soft white glow.
- Pulse every 1.5 to 2 seconds.
- Should be clearly distinct from embers.

Key variants:

The three keys can be visually identical for clarity, or have very subtle differences:

- Key A: slightly curved root-like bow.
- Key B: small thorn on the shaft.
- Key C: hollow ring in the center.

Subtle differences are allowed, but the primary identity should be “bone-white key.”

Pickup feedback:

- Small white pulse at pickup location.
- Key slot in HUD fills with a short pop.
- Short bone chime plays.
- A very small ground ripple may appear, but do not show the full noise radius.

### Ember Stones

There are five ember stones.

Visual design:

- Small stone, approximately 24 x 24 px.
- Dark outer shell.
- Inner warm orange glow.
- 2 to 4 tiny bright speckles.
- Slow pulse, weaker than keys.
- Slight heat shimmer is optional and should be very subtle.

Pickup feedback:

- Small amber spark burst.
- Fuel bar rises.
- Lantern flame brightens briefly.
- Warm ember sound plays.

### Why Keys and Embers Are Different

Keys are objectives. Embers are resources. Keys should look important and permanent. Embers should look useful and consumable. Making them too similar would confuse objective progress from fuel management.

### Dead Well

The Dead Well is The Hollow’s wake point.

Visual design:

- Approximately 2 x 2 tiles.
- Dark water center.
- Stone rim.
- Faint pale mist.
- A few broken bones or roots around the edge.
- The water should be darker than normal water.
- During waking, mist rises and the Hollow emerges.

The well should feel like the source of danger, but not visually dominate the entire map.

### Old Gate

The Old Gate is the final exit.

Visual design:

- Approximately 3 x 3 tiles.
- Large stone frame.
- Dark wooden or stone gate panels.
- Three bone key sockets are visible when close.
- The gate should look old, heavy, and barely standing.
- When closed, it should feel sealed.
- When ready to open, the sockets glow faint bone white.
- When opening, the gate should creak and shift, with light leaking through the gap.
- Once open, the gap is clear and safe.

### Gate Threshold

The threshold is the 3-tile-deep safe zone once the gate is open.

Visual design:

- Pale dawn light fills the threshold.
- Soft gold/white mist drifts through.
- The edge should be readable but not hard.
- The Hollow should not visually enter the threshold once it is open.
- The threshold should feel like escape, not another room.

### Why

The gate should feel like the end of the forest. It is the only thing that matters once all keys are collected. Its visual weight should increase as the player approaches escape.

---

## 11. HUD and UI

The HUD should be minimal, quiet, and readable. It should not feel like a modern action game.

### HUD Style

- Bone-white text.
- Pale bone secondary text.
- No bright frames.
- No heavy panels.
- Slight transparency, approximately 80%.
- Use simple icons and bars.
- Use shape and pulse for warnings, not only color.
- No numerical fuel or breath values.
- No enemy position markers.
- No minimap.

### Font

Use a clean, readable humanist sans-serif for gameplay UI.

The title screen may use a slightly rustic serif, but all in-game UI should prioritize readability.

Text sizes:

- Timer: 24 px equivalent.
- Objective text: 18 px equivalent.
- Prompts: 16 px equivalent.
- Small icons: 24 to 32 px.

### HUD Layout

| HUD Element | Location | Description |
|---|---|---|
| Dawn timer | Top-left | `mm:ss` countdown |
| Moon/sun dial | Top-left, next to timer | Small circular dial showing night to dawn |
| Objective text | Top-center | Short current goal |
| Key slots | Top-center, below objective | Three key slots |
| Fuel bar | Top-right | Lantern fuel gauge |
| Breath bar | Top-right, below fuel | Sprint breath gauge |
| Objective arrow | Edge of screen | Points to off-screen objective |
| Interaction prompt | Near player | Gate interaction feedback |

### Dawn Timer

The timer should count down from `08:00`.

Normal state:

- Bone-white text.
- Moon/sun dial shows a crescent moon moving toward dawn.

Warning state, below 60 seconds:

- Timer text shifts to Dawn Gold.
- Timer pulses gently every second.
- Moon/sun dial glows faintly.
- A thin dawn glow appears at the top edge of the screen.

### Why the Moon/Sun Dial Exists

The timer is a number, but the dial gives emotional context. The player should feel the night changing, not just watch a countdown.

### Objective Text

The objective text should be very short.

Examples:

- `Find the bone keys`
- `Find the remaining bone keys`
- `Escape before dawn`
- `The gate is sealed (x / 3)`
- `Hold to open the gate`

The text should fade in when the objective changes and remain until replaced.

### Key Slots

Display three slots.

Empty slot:

- Pale bone outline key silhouette.

Filled slot:

- Bone-white filled key.
- Small pop animation on pickup.
- Soft chime.

The key slots should be the primary progression feedback.

### Fuel Bar

The fuel bar represents lantern fuel.

Visual design:

- Horizontal bar, approximately 140 px wide and 10 px tall.
- Small flame icon on the left.
- Bar color: Lantern Amber.
- Bar shrinks as fuel drains.
- Fuel below 30: flame icon flickers.
- Fuel below 20:
  - Flame icon flickers strongly.
  - Bar color shifts to dull orange.
  - A small warning pulse appears.
  - The light safe-zone edge is gone or collapsing.

Do not show a numerical fuel value.

### Breath Bar

The breath bar represents sprinting.

Visual design:

- Horizontal bar below fuel.
- Smaller than fuel bar, approximately 140 px wide and 6 px tall.
- Color: pale cold blue.
- Bar drains while sprinting.
- Bar recovers while walking or standing.
- When breath reaches 0:
  - Bar becomes empty.
  - A faint slash or locked icon appears over it.
  - Sprinting is visually locked.
  - A short exhausted gasp plays.
- Sprinting becomes available again visually when the bar recovers enough.

Do not show a numerical breath value.

### Why Breath Is Secondary

Fuel is the central resource. Breath is a momentary escape tool. The fuel bar should be more visually important.

### Objective Arrow

The objective arrow appears at the edge of the screen.

Visual design:

- Bone-white arrow.
- Approximately 24 px.
- Placed 20 px from the screen edge.
- Points toward the current objective’s first meaningful waypoint.
- Hidden when the objective is visible on screen.
- Pulses very gently when visible.
- Should not look like a minimap marker.

### Interaction Prompt

The interaction prompt appears near the player when relevant.

Gate locked:

- Small gray bone key icon.
- Text: `Sealed (x / 3)`.

Gate ready:

- Bright bone key icon.
- Text: `Hold E to open`.
- A circular progress ring appears around the prompt.
- The ring fills over 2 seconds.
- If the player releases early, the ring shrinks quickly.

Gate opening:

- Text: `The gate is open`.
- A soft dawn pulse appears at the threshold.

### Accessibility Visual Rules

- Warning states must use pulse, shape, or icon changes, not only color.
- The Hollow should have a clear cold rim, not only black silhouette.
- UI text should maintain strong contrast against dark backgrounds.
- Add an optional reduce-motion mode that disables screen shake, heavy pulsing, and large particle bursts.
- Add an optional high-contrast mode that adds a faint cold outline around The Hollow’s fatal core.

### What Is Not in the HUD

The HUD does not include:

- Minimap.
- Health bar.
- Enemy position marker.
- Fuel number.
- Breath number.
- Noise radius indicator.
- Inventory list.
- Quest log.
- Pause menu.

### Why

The game is a short high-pressure escape. The HUD should communicate survival state only. Extra information would make the forest feel like a game UI instead of a dangerous place.

---

## 12. Game State Screens

### Title / Start Screen

A minimal start screen should exist.

Visual style:

- Dark forest background.
- A single lantern glow in the center.
- Game title in bone-white, slightly rustic but readable.
- Simple control list.
- One primary button: `Begin the Night`.

Controls shown:

- Move: `WASD / Arrow Keys`
- Sprint: `Shift / Space`
- Lantern: `L`
- Interact: `E`

### Why

The player needs basic control clarity before the run. A simple start screen sets the tone without adding a separate tutorial phase.

### Playing State

No pause screen is required.

The game should keep running once started.

### Why

Pausing an 8-minute tension run can break the experience. The fantasy is a continuous night. If pause is added later, it should be a simple dimmed overlay that freezes time and audio, but it is not core.

### Failed: Caught by The Hollow

Visual sequence:

1. The Hollow touches the player.
2. A brief 0.25-second freeze or slow-down.
3. Black tendrils spread from The Hollow across the screen.
4. The player silhouette is consumed.
5. Screen darkens.
6. Text appears:
   - `The Hollow found you.`
   - `Press R to retry`

Audio:

- Short dissonant cold hit.
- Music drops to a low drone.
- Then near silence.

### Failed: Dawn Arrives

Visual sequence:

1. Dawn timer reaches zero.
2. The forest floods with soft Dawn Gold.
3. The player is still in the forest.
4. Text appears:
   - `Dawn came before you escaped.`
   - `Press R to retry`

Audio:

- Music becomes a quiet bright chord.
- Distant birds or wind.
- No horror stinger.

### Win: Escape Before Dawn

Visual sequence:

1. Player crosses the gate threshold.
2. The screen brightens into dawn light.
3. The forest behind becomes soft and distant.
4. Text appears:
   - `You crossed before dawn.`
   - Optional: `Time: mm:ss`
   - `Play again`

Audio:

- Music resolves into a gentle morning chord.
- Soft wind and birds.

### Why Different Fail Screens

The two fail states have different emotional meanings.

- Being caught is horror.
- Dawn arriving is loss of opportunity.

They should not use the same visual language.

---

## 13. Required Event Cues

| Event | Visual Cue | Audio Cue | Why |
|---|---|---|---|
| The Hollow wakes | Cold vignette pulse; if visible, well mist and eyes open | Low rising groan, music pressure layer begins | Player understands the safe phase is over |
| The Hollow enters Hunting | Eyes flare, cold blue vignette pulse | Short cold sting or high whisper | State change is clear |
| Fuel below 20 | Fuel bar pulses, flame sputters, safe-zone edge gone | Soft sizzle or warning tick | Player knows defense is failing |
| Dawn below 60 seconds | Timer pulses gold, top edge gains dawn glow | Music becomes more urgent | Time pressure is felt visually |
| Key picked up | White pulse, HUD key slot fills | Bone chime | Progress is clear |
| Ember picked up | Amber spark, fuel bar rises, lantern brightens | Warm crackle | Resource gain is clear |
| Gate ready to open | Bone sockets glow, prompt appears | Low ready hum | Final objective is clear |
| Gate opened | Light leaks through gap, threshold glow appears | Heavy creak, rumble, wind | Climactic risk |
| Player caught | Black tendrils consume screen | Dissonant cold hit | Fail state is unmistakable |
| Dawn arrives | Warm gold flood | Quiet bright chord | Fail state is distinct from being caught |

### Why

These cues are required because gameplay depends on the player understanding state changes. If the player cannot tell when The Hollow wakes, hunts, or when dawn is near, the tension becomes frustration.

---

## 14. Music

The music should be adaptive, ambient, and quiet. It should support tension without becoming a full action score.

### Musical Style

- Sparse.
- Nocturne-like.
- Folk-horror texture.
- Low strings.
- Detuned pads.
- Occasional celesta or soft piano.
- Wind and room tone.
- Minimal percussion.
- No loud drums until the final phase.
- No bright major melodies until escape.

### Key and Emotional Arc

- Night music: A minor or D minor, cold and sparse.
- Dawn/escape music: resolve toward a warmer major key, such as C major or F major.
- The shift from minor night to warm dawn should feel like relief, not triumph.

### Adaptive Layers

| Layer | When Active | Content |
|---|---|---|
| Night Bed | Always from start | Low drone, wind, room tone |
| Mystery Layer | Start phase, before Hollow wakes | Sparse celesta/piano, soft strings, very slow |
| Pressure Layer | After The Hollow wakes | Low pulse, muted percussion, dissonant strings |
| Escape Layer | Final 60 seconds | Faster pulse, warmer pad, rising tension, faint dawn sound |
| Hunting Transient | When The Hollow enters Hunting | Short high string or whisper sting |
| Dawn Resolve | Win or dawn fail | Warm chord, birds, wind |

### Phase Timing

| Game Time | Music State |
|---|---|
| 0:00 to 1:30 | Quiet night, sparse melody, low tension |
| 1:30 to 5:30 | Pressure layer begins, pulse becomes present |
| 5:30 to 7:00 | Escape layer begins, tension rises |
| Final 60 seconds | Stronger pulse, but still ambient |
| Win | Resolve to dawn warmth |
| Caught | Music cuts to low drone, then silence |
| Dawn fail | Music becomes warm and empty |

### Mixing Rules

- Music should sit lower than important SFX.
- No music stinger should mask key pickup, gate creak, or The Hollow’s hunting cue.
- The Hollow’s state cues should be slightly louder than the music bed.
- Ambient wind should never become distracting.
- The final 60 seconds should increase tension through pulse and texture, not volume spikes.

### Why

The player is managing fear and time. Loud music would remove subtlety. The music should make the forest feel aware without telling the player exactly where danger is.

---

## 15. Sound Effects

Sound effects should be clear, short, and emotionally consistent.

### General Audio Rules

- Use short reverb for keys, gate, and The Hollow.
- Use dry close sound for player footsteps and UI.
- Use low-pass filtering for distant or hidden sounds.
- Underbrush should change footstep texture, not make noise disappear.
- Sprinting should sound louder and more urgent.
- The Hollow should always sound slightly unnatural.

### Ambient Sounds

| Sound | Description |
|---|---|
| Wind loop | Constant low forest wind |
| Night insects | Distant cicadas or crickets, sparse |
| Wood creak | Occasional tree or gate creak |
| Water ripple | Soft ripple near dead well or water tiles |
| Leaf rustle | Small movement in underbrush |
| Dawn birds | Only in final phase or win state |

### Player Sounds

| Event | Sound | Notes |
|---|---|---|
| Walk | Soft footstep | Short, low, organic |
| Sprint | Faster footstep | Sharper, louder |
| Walk in underbrush | Dry leaf rustle | Muffled but still present |
| Sprint in underbrush | Crunchier rustle | Should feel loud and risky |
| Sprint breath | Panting loop | Increases as breath lowers |
| Breath locked | Exhausted gasp | When sprint becomes unavailable |
| Lantern on | Small fire whoosh and click | Soft click, warm whoosh |
| Lantern off | Hiss | Flame dies quickly |
| Fuel low | Faint sizzle or warning tick | Subtle, not mechanical |

### Pickup Sounds

| Event | Sound | Notes |
|---|---|---|
| Key pickup | Bone chime | Two short notes, slight reverb |
| Ember pickup | Warm crackle | Small spark, high soft sparkle |
| Gate locked | Dull thud and low creak | Communicates sealed gate |
| Gate open | Heavy creak and rumble | Large, slow, dramatic |
| Threshold open | Soft dawn hum | Warm, quiet, hopeful |

### The Hollow Sounds

| State | Sound | Notes |
|---|---|---|
| Sleeping | Low wet breath | Barely audible near well |
| Waking | Rising groan and mist | 8-second telegraph |
| Curious | Soft rustle and faint whisper | Slow, uncertain |
| Investigating | Sharp intake | The Hollow noticed something |
| Searching | Low circular whisper | Patterned, eerie |
| Hunting | High whisper, dragging, cold pulse | Urgent but not cartoonish |
| Caught | Dissonant cold hit | Short, harsh, then silence |

### Fail and Win Sounds

| Event | Sound |
|---|---|
| Caught | Cold dissonant hit, low drone, silence |
| Dawn fail | Quiet bright chord, wind, distant birds |
| Win | Gentle dawn chord, soft wind, birds |

### Why

Audio is half the horror. The player may not see The Hollow, but they should hear its state changes. Sound effects should make stealth choices meaningful: walking, sprinting, picking up, and opening the gate should all have audible consequences.

---

## 16. Motion, Particles, and Performance

### General Motion Rules

- Motion should be subtle.
- No excessive screen shake.
- No full-screen flashes.
- No particle overload.
- The game should feel calm until it needs to feel urgent.

### Allowed Effects

- Mist drift.
- Lantern flame flicker.
- Key pulse.
- Ember spark.
- The Hollow cold rim pulse.
- Dawn edge glow.
- Small ground ripple for pickups.
- Brief cold vignette pulse for threat state changes.

### Screen Shake

Screen shake is optional and should be minimal.

If used:

- Caught: small 2 to 3 px shake for 0.2 seconds.
- Gate opening: very subtle 1 to 2 px shake for 0.5 seconds.
- No shake for footsteps, pickups, or The Hollow movement.

### Reduce Motion Mode

If implemented, reduce motion should:

- Disable screen shake.
- Replace pulsing warnings with steady color changes.
- Reduce particle bursts.
- Slow mist and flame flicker.

### Particle Budget

For browser performance:

- Mist particles: maximum 10 to 15 visible.
- Ember sparks: maximum 8 to 12 per pickup.
- Key pulse: simple glow, no heavy particles.
- The Hollow cold pulse: simple rim/vignette, no complex particles.
- Dawn light: gradient wash, not thousands of particles.

### Why

The atmosphere should come from composition, color, and sound. Overdoing particles would make the game feel busy and could hurt performance.

---

## 17. Asset Generation Notes

These are reference recipes for generating or guiding asset creation. They are not implementation requirements unless an asset is missing.

### Ground Tile Recipe

For each base ground tile:

1. Fill a 40 x 40 canvas with the base ground color.
2. Add low-frequency noise to create soft color variation.
3. Add 5 to 12 small speckles using moss or stone colors.
4. Darken the edges slightly.
5. Add one faint darker patch for depth.
6. Save 3 to 5 variants per tile type.

For underbrush:

1. Use a darker base.
2. Add 4 to 8 low tuft shapes.
3. Keep the top edge soft.
4. Ensure the tile is not fully opaque.
5. Add one or two lighter highlights so the player can read it as passable.

For tree trunks:

1. Draw a central circular or irregular trunk shape.
2. Add root lines extending outward.
3. Darken the base.
4. Add a faint cold edge highlight on one side.
5. Avoid large canopies.

For rocks:

1. Draw an angular stone shape.
2. Add a dark shadow underneath.
3. Add a faint cold wet highlight.
4. Keep the silhouette readable at small size.

### Key Sprite Recipe

Bone key:

- Total size: 28 x 28 px.
- Vertical shaft: 8 x 16 px.
- Ring: 10 px circle at top.
- Teeth: two small protrusions at bottom.
- Color: Bone White.
- Add 1 to 2 subtle bone texture speckles.
- Add a soft white glow, 4 to 6 px blur.
- Animation: 1 to 2 px float, 1.5 to 2 second loop.

### Ember Sprite Recipe

Ember stone:

- Total size: 24 x 24 px.
- Base stone shape: rounded irregular polygon.
- Outer color: dark brown-grey.
- Inner glow: Ember Orange.
- Add 3 bright speckles.
- Add a very soft heat shimmer, optional.
- Animation: slow pulse, weaker than key.

### The Hollow Sprite Recipe

The Hollow:

- Total visual size: approximately 64 x 76 px.
- Core: dense black vertical shape, slightly ragged.
- Outer tendrils: semi-transparent black, extending beyond core.
- Rim: faint Hollow Blue outline.
- Eyes: two small Cold Moon points.
- Sleeping: core compressed, eyes closed or absent.
- Waking: core rises, eyes open.
- Hunting: core stretches, eyes brighter, rim stronger.

### Player Sprite Recipe

Player:

- Total size: approximately 40 x 48 px.
- Hooded cloak: dark blue-grey.
- Lantern: small amber circle on one side.
- Feet: simple dark shape.
- Lantern flame: 4 to 8 px, animated.
- Covered state: lower half tinted darker, 2 to 3 grass tufts overlaid.

### Audio Synthesis Reference

If assets are generated procedurally, use these approximate parameters.

| Sound | Type | Pitch/Frequency | Envelope | Notes |
|---|---|---:|---|---|
| Key chime | Triangle/sine | 880 Hz to 1318 Hz | Short attack, 0.25s decay | Add slight reverb |
| Ember crackle | Filtered noise | 2k to 6k Hz | Short burst, 0.3s | Warm low-pass |
| Footstep | Low noise | 100 to 300 Hz | 0.1s decay | Dry |
| Sprint footstep | Low noise | 200 to 500 Hz | 0.08s decay | Sharper |
| Lantern on | Sine + noise | 300 Hz click + whoosh | 0.2s | Soft |
| Gate creak | Sawtooth | 80 to 120 Hz with slow pitch bend | 1.5 to 3s | Low, gritty |
| Hollow hunt sting | Filtered noise + sine | 1.5k to 4k Hz | 0.4s attack, 0.6s decay | Cold, airy |
| Waking groan | Detuned sawtooth | 50 to 80 Hz | 8s swell | Very low, distant |
| Dawn resolve | Soft triangle chord | C major or F major | 3s attack, 4s release | Warm, quiet |

### Why Include Generation Notes

The integration agent may need to create placeholder assets quickly. These notes give enough direction to produce assets that match the final art direction without needing separate asset files at the start.

---

## 18. UX Onboarding

The first 90 seconds are the safe teaching phase. Visual onboarding should be minimal and diegetic.

### First-Run Cues

Only if the player is in a new run:

- On first movement: a small bone text near the player says `Move` for 2 seconds.
- On first sprint: `Sprint` appears for 2 seconds.
- On first lantern toggle: `Lantern` appears for 2 seconds.
- When the first key is off-screen: the objective arrow appears with a soft pulse.

These cues should be:

- Small.
- Bottom-center or near player.
- Low opacity.
- Fade quickly.
- Never block movement.

### Why

The start clearing should teach the core controls without a separate tutorial screen. The cues should feel like faint notes left by the forest, not a UI lesson.

---

## 19. Visual Cues for Stealth and Noise

The player needs to understand noise without seeing explicit radius circles.

### Approach

Use diegetic feedback, not measurement UI.

- Walking creates small ground disturbance.
- Sprinting creates slightly larger dust or mist disturbance.
- Pickups create a small visible pulse.
- If The Hollow hears the player:
  - If visible, The Hollow turns or its eyes brighten.
  - If not visible, a subtle cold audio intake plays.
- Sprinting in underbrush should visually look messier and louder than walking.

Do not show exact noise radius rings.

### Why

Explicit radius circles would turn stealth into a measurement puzzle. The player should learn risk from feedback: The Hollow reacts, the music shifts, and the forest feels more aware.

---

## 20. Cuts and Design Logic

The following are intentionally not in the game.

### No Minimap

**Cut.**

Why:

- The compass arrow is enough.
- A minimap would reduce the unknown-forest feeling.
- Navigation is part of the tension.

### No Enemy Position Marker

**Cut.**

Why:

- The Hollow should be found through sound, light, and observation.
- A marker would make the threat less readable and less scary.

### No Visible Noise Radii

**Cut.**

Why:

- Explicit circles would remove the feeling of risk.
- The player should learn from The Hollow’s reactions and audio.

### No Red Warning Color

**Cut.**

Why:

- Red would break the night palette.
- Dawn gold and cold blue communicate threat and time more elegantly.

### No Full 3D Environment

**Cut.**

Why:

- Top-down readability is essential for light, cover, and line of sight.
- 3D would increase asset scope and camera complexity without improving the core stealth experience.

### No Parallax Background

**Cut.**

Why:

- Parallax can make top-down tactical spaces feel less grounded.
- The forest should feel like a place the player is in, not a scrolling background.

### No Full Tree Canopies

**Cut.**

Why:

- Canopies would hide entities and make line of sight harder to read.
- Low trunks and underbrush are enough for forest depth.

### No Health Bar

**Cut.**

Why:

- One contact with The Hollow is failure.
- A health bar would soften the threat and add UI complexity.

### No Lore Text

**Cut.**

Why:

- The player should infer danger from the environment and sound.
- Lore would slow the game and dilute the escape loop.

### No Pause Screen

**Cut from core design.**

Why:

- The game is an 8-minute continuous tension run.
- Pausing would break the night fantasy.
- If pause is added later, it should be minimal and non-core.

### No Extra Collectibles

**Cut.**

Why:

- The game is complete with three keys, five embers, one gate, and one enemy.
- Extra collectibles would distract from the central resource and time pressure.

---

## 21. Final Visual Contract

The integration agent should use this document as the authority for:

- Visual dimensionality.
- Art style.
- Palette.
- Zone presentation.
- Lighting and visibility.
- Player and enemy appearance.
- HUD layout.
- Event cues.
- Music and SFX direction.
- Asset generation direction.

The game should always feel like one continuous night:

- Quiet at the start.
- Cold after The Hollow wakes.
- Dangerous in the open.
- Safe only in cover.
- Bright only at escape.

If a visual element does not help the player understand light, cover, threat, objective, or dawn, cut it.