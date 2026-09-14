# `visual.md` — Visual Design: Derelict Space Station Survival

This document is the visual source of truth for the game. The integrator should use only the decisions in this file for dimensionality, style, UX, zone art direction, music, and sound effects.

---

## 1. Core Design Decisions

### 1.1 Dimensionality: 2D top-down with 2.5D lighting

**Decision:** The game is **2D top-down**, rendered as sprites/tiles/vectors on a 2D canvas. It uses **2.5D lighting effects** — light cones, radial gradients, shadow masks, particles, and vertical prop shading — but does **not** use true 3D geometry, isometric projection, or perspective.

**Why:**
- A derelict space station is spatially coherent as a top-down plan: corridors, pressure zones, doors, vents, and hull breaches are easier to read from above.
- Survival mechanics such as oxygen loss, pressure loss, radiation spread, and escape routes need immediate spatial readability.
- Top-down 2D keeps the browser-friendly, high-contrast, low-asset pipeline simple for a three-person team.
- 2.5D lighting gives depth, dread, and atmosphere without the complexity of 3D models, shaders, collision meshes, or perspective foreshortening.

**Rule:** All game areas are viewed from directly above. The camera does not rotate. Objects may imply height through shadows and outlines, but the gameplay space is top-down.

---

## 2. Visual Identity

### 2.1 Style Name

**Functional Brutalist Decay**

The station is old, industrial, and abandoned. It should feel engineered, not alien. The horror comes from abandonment, low light, failing systems, and environmental danger — not gore, gore-like detail, or excessive fantasy.

### 2.2 Overall Mood

- Cold, mechanical, empty.
- Low contrast in normal areas, higher contrast when a system is active.
- Emergency lighting is the primary source of color.
- Materials are worn: scratched metal, grime, frost, water, dust, cracked glass, burned cable insulation.
- Motion should be slow and mechanical: doors slide, vents rattle, lights flicker, particles drift.

### 2.3 What the visuals should communicate

The player should always understand, at a glance:

1. What zone they are in.
2. Whether power is available.
3. Where light is coming from.
4. Where the nearest interactive object is.
5. What hazard is active.
6. Whether the situation is getting worse.

If a visual element does not help one of those six things, it should be reduced or removed.

---

## 3. Rendering and Composition

### 3.1 Base Resolution

- Base design resolution: **1280 x 720**.
- Maintain **16:9**.
- Scale uniformly to screen size.
- Prefer integer scaling where possible to keep sprites sharp.

### 3.2 Tile / Sprite Scale

- Base tile: **32px**.
- Player collision radius: approximately **14px**.
- Player sprite visual footprint: approximately **24–32px**.
- Door width: typically **2–3 tiles**, unless the level designer specifies otherwise.
- Interactive object highlight radius: approximately **48px** around the object center.

### 3.3 Camera

- Fixed top-down orthographic view.
- Camera follows the player.
- No camera rotation.
- No zoom.
- Slight camera drift is allowed for atmosphere, but the player must remain clearly centered.
- No cinematic tracking shots during normal gameplay.

### 3.4 Render Order

Use this layering order:

1. Floor material  
2. Floor decals, stains, scratches, hazard markings  
3. Lower props: crates, pipes, cables, plants, debris  
4. Player and major interactive objects  
5. Dynamic particles: dust, steam, water mist, radiation specks, debris  
6. Darkness / shadow overlay  
7. Additive light cones and glow  
8. Vignettes and hazard fog  
9. UI, prompts, icons, bars  

**Why:** This order keeps light readable, allows dark areas to obscure detail, and ensures UI remains clear.

---

## 4. Color System

Use a limited palette. Most of the screen should be dark neutral color. Accent colors are reserved for systems and hazards.

### 4.1 Core Palette

| Role | Color | Hex | Use |
|---|---:|---:|---|
| Deep black | `#07090B` | Backgrounds, void, deep shadow |
| Charcoal | `#11151A` | Default floor base |
| Gunmetal | `#1E262E` | Metal panels |
| Steel | `#384550` | Walls, raised surfaces |
| Bone gray | `#CFC9BC` | Scratches, old paint, suit |
| Emergency amber | `#FFB000` | Power, caution, UI, default active light |
| Oxygen cyan | `#58D8FF` | O2, water, life support, success state |
| Warning red | `#FF3B30` | Critical hazard, locked, fail, breach |
| Bio green | `#79E08A` | Hydroponics, plant life, biological systems |
| Cryo blue | `#69A8FF` | Cold, frost, med/cryo areas |
| Reactor orange | `#FF7A26` | Heat, reactor, machinery under load |
| Radiation violet | `#A47BFF` | Radiation only, used sparingly |

### 4.2 Color Rules

- **Amber** is the default active system color.
- **Cyan** is only for life support, oxygen, water, or success.
- **Red** is only for immediate danger or locked systems.
- **Green** is only for plants/biological areas, not general success.
- **Violet** is only for radiation.
- Do not let zone colors become the main UI color. UI stays amber and gray, with state colors for specific bars/icons.

### 4.3 Accessibility Rules

- Do not communicate critical information by color alone.
- Pair color with shape:
  - O2: cyan bar with circle/valve icon.
  - Power: amber bar with lightning bolt.
  - Hazard: red triangle.
  - Radiation: violet diamond with Geiger sound.
- Critical UI text should have at least **4.5:1 contrast** against its background.
- Provide a high-contrast mode if implementation allows: increase outline visibility and reduce dark fog.

---

## 5. Material and Shape Language

### 5.1 Materials

All zones use the same core materials, with localized modifications.

#### Core Materials

- **Worn steel plates:** flat panels with scratches, rivets, and stains.
- **Scuffed flooring:** dark gray with directional wear lines.
- **Pipes:** cylindrical, with joints, valves, and occasional leaks.
- **Cables:** thin dark lines, sometimes sparking or hanging.
- **Glass:** cracked, fogged, or shattered.
- **Grime:** low-contrast dark overlays on floors and walls.
- **Warning paint:** faded stripes, chevrons, and stencil text.

#### Zone Modifications

- Hydroponics adds moisture, soil, glass tubes, and plant silhouettes.
- Cryo adds frost, glass, white breath vapor, and pale blue surfaces.
- Reactor adds heat shimmer, orange glow, burned edges, and cable bundles.
- Airlock adds external starfield, hull plating, and pressure markings.
- Crew quarters add bunks, small personal items, warm dim light, and worn fabric.

### 5.2 Shape Language

- Predominantly rectangular geometry.
- Straight corridors and angular rooms.
- Small rounding only on pipes, valves, and viewports.
- Hazard markings are angular: chevrons, stripes, dashed borders.
- Avoid decorative curves. The station should feel manufactured and damaged.

### 5.3 Decals and Story

Environmental storytelling should be subtle and sparse. Use:

- Scorch marks.
- Painted footprints.
- Stamped emergency directions.
- Cracked console glass.
- Dripping stains.
- Small personal objects: cups, patches, tool cases, logs.
- Faded warning labels.

Do not place large narrative objects unless the gameplay designer requires them. Visuals should suggest the station died, not explain the entire story.

---

## 6. Lighting System

Lighting is the primary atmosphere tool.

### 6.1 Default State

- Most areas are dark or dim.
- The player has a weak helmet light.
- Active station lights are amber.
- Dead areas have no light except occasional flicker.

### 6.2 Light Types

| Light Type | Color | Behavior |
|---|---|---|
| Player helmet light | Warm white, slightly amber | Small oval or circular radius, follows player, slight flicker |
| Station emergency light | Amber | Fixed to walls/ceilings, may flicker or die |
| O2 / life support light | Cyan | Indicates breathable area, canister, or vent |
| Hazard beacon | Red | Slow or fast pulse depending on severity |
| Reactor glow | Orange | Heat source, pulses with station state |
| Cryo glow | Blue | Cold areas, glass frost |
| Radiation glow | Violet | Subtle speckled glow around radiation sources |

### 6.3 Lighting Behavior

- Light should be dim enough to create tension but bright enough to read interactive objects.
- When power is on, room lights are visible but still weak.
- When power is off, all station lights die; only player light and small emergency glow remain.
- Flickering lights should be slow, not seizure-inducing.
  - Safe flicker: no faster than **3Hz**.
  - No rapid white flashes.
- Light sources should have soft radial falloff.

### 6.4 Readability Rule

Any object the player can interact with must be visible or highlighted when within interaction range.

- Within **48px** of an interactable object, draw a thin amber outline around the object.
- If the object is in darkness, the outline remains visible.
- Locked objects get a red outline plus a lock icon.

---

## 7. Player Visuals

### 7.1 Player Appearance

- Small suited figure.
- Predominantly bone gray and charcoal.
- Cyan visor glow.
- Amber helmet light.
- Slight backpack shape indicating O2.
- Suit should be simple; avoid detailed anatomy.

### 7.2 Player States

| State | Visual |
|---|---|
| Normal | Steady helmet light, cyan visor |
| Low O2 | Cyan vignette pulses at screen edge, breath particles |
| Injured / critical | Light dims slightly, red edge pulse |
| Power tool active | Amber glow around relevant tool |
| Carrying canister | Cyan canister icon near player |
| Carrying cell | Amber cell icon near player |
| Sealing breach | White steam particles around hands |

### 7.3 Movement Visuals

- Footprints in dust/water only when relevant.
- No heavy screen shake for normal movement.
- Breach or reactor events may cause very small camera shake, no more than **2px** for 150ms.

---

## 8. UX and Interface

### 8.1 UI Style

The UI is a **station terminal / wrist display**.

- Font: monospace or stencil-style uppercase.
- Text is uppercase.
- Tracking: wide.
- No decorative gradients.
- No rounded consumer-style buttons.
- Borders are thin, 1–2px.
- Backgrounds are semi-transparent dark gray, not solid black.

#### UI Colors

- Default text: `#D8D4C8`
- Active text: `#FFB000`
- Disabled text: `#5A646E`
- Positive / O2: `#58D8FF`
- Danger: `#FF3B30`
- Radiation: `#A47BFF`

### 8.2 Main HUD

Keep the HUD minimal.

#### Top-Left: Objective / Prompt

- Small line of text.
- Examples:
  - `FIND O2`
  - `RESTORE POWER`
  - `SEAL BREACH`
  - `REACH AIRLOCK`

#### Bottom-Left: Survival Bars

| Bar | Color | Icon | Meaning |
|---|---|---:|---|
| O2 | Cyan | Circle/valve | Player oxygen |
| Power | Amber | Lightning bolt | Station power or player cell reserve |

Do not show a separate health bar. Oxygen is the primary survival metric.

#### Bottom-Center: Carry Slots

Three small square slots:

1. O2 canister  
2. Power cell  
3. Sealant / tool  

Each slot shows:
- Empty: dark gray outline.
- Filled: small icon.
- Selected: amber outline.
- Insufficient charge: darkened icon with red slash.

**Why:** A full inventory screen is unnecessary. The player only needs to carry three survival resources.

### 8.3 Interaction Prompts

When the player is near an interactive object:

- Show a small amber prompt above the object.
- Format: `[E] USE`, `[E] SEAL`, `[E] OPEN`, `[E] SCAN`.
- If the game supports mouse, also allow click.
- If the object is locked: `[LOCKED]` in red with lock icon.
- If missing resource: `[NO O2]`, `[NO CELL]`, `[NO SEALANT]` in red.

### 8.4 Zone Indicator

Do not use a large minimap.

Instead, show a small **station schematic** only when the player is near a wall terminal or major junction.

- Schematic uses amber lines.
- Current location is a cyan dot.
- Known areas are solid lines.
- Unknown areas are dashed.
- Hazards are small red markers.
- Radiation markers are violet diamonds.

**Why:** A permanent minimap breaks the claustrophobic feel and adds UI clutter. A diegetic schematic terminal keeps orientation available while preserving atmosphere.

### 8.5 Menus

#### Title / Boot Screen

- Black background.
- Single amber light blinking once.
- Title in stencil font:
  - `STATION DERELICT`
  - or a similar short name.
- One prompt:
  - `[ENTER] BOOT`

No story text. The station speaks through the game.

#### Pause

- Dark overlay.
- Large text: `PAUSED`
- Options:
  - `RESUME`
  - `RESTART`
  - `SOUND ON/OFF`

#### Death Screen

- Black background.
- Red warning triangle.
- Cause of death in one line:
  - `OXYGEN DEPLETED`
  - `HULL BREACH`
  - `RADIATION EXPOSURE`
  - `CRYOGENIC LOCKDOWN`
- One prompt:
  - `[ENTER] REBOOT`

#### Success Screen

- Dark background with steady cyan light.
- Text:
  - `STATION STABILIZED`
- One prompt:
  - `[ENTER] NEXT SEGMENT`
- No celebration music. Success should feel quiet and relieved.

---

## 9. Visual States and Feedback

### 9.1 O2 States

| O2 Level | Visual |
|---|---|
| 100–50% | Normal cyan bar, no vignette |
| 49–25% | Slight cyan vignette, breath particles |
| 24–10% | Strong cyan vignette pulse, heartbeat audio |
| Below 10% | Pulsing red-cyan edge, vision softens, light flickers slightly |

**Why:** Oxygen loss should feel gradual, then urgent, without relying on a numeric health bar.

### 9.2 Power States

| Power State | Visual |
|---|---|
| On | Amber station lights, consoles glow amber |
| Low | Lights flicker, amber pulses slowly |
| Off | Station lights die, only player light remains |
| Restoring | Amber pulse travels along power lines/cables |

**Why:** Power is the station’s heartbeat. Its state should be visually obvious across the map.

### 9.3 Hazard States

#### Hull Breach

- White steam particles flow from the breach point.
- Blue-cyan vapor ring pulses outward.
- Red rotating warning marker near the breach.
- Air movement particles drift toward the breach.
- Optional: small pressure bar in red near local panels.

#### Radiation

- Violet specks drift in the air.
- Radiation source has a faint violet glow.
- Warning signs use diamond + Geiger icon.
- No large violet color floods; radiation should feel invasive, not decorative.

#### Cold / Cryo

- Blue frost creeps onto surfaces.
- Player breath shows white vapor.
- Glass surfaces fog.
- Movement through cryo areas may show slow frost particles.

#### Heat / Reactor

- Orange glow from reactor core.
- Heat shimmer is subtle vertical distortion.
- Cables may spark with small amber particles.
- Warning stripes use orange/black, not yellow/red, to avoid clashing with general UI.

#### Lockdown / Door Failure

- Door edges pulse red.
- Lock icon appears.
- Small mechanical shake for 100ms.
- Denied interaction plays a dull thud, not a loud alarm.

### 9.4 Feedback Rules

All player actions must have immediate feedback:

| Action | Visual |
|---|---|
| Pick up item | Item icon flies from object to HUD slot |
| Use item | Slot flashes amber, then depletes |
| Success | Brief cyan outline on affected object |
| Failure | Red outline + shake, max 2px |
| Door opens | Amber edge glow slides open |
| Door locked | Red lock icon pulses once |
| Alarm triggered | Red beacon rotates, UI border flashes red once |
| Radiation scanned | Violet diamond appears with Geiger crackle |

---

## 10. Zone Art Direction

Each zone must feel distinct but use the same core material system. The player should identify the zone within one second.

### 10.1 Zone Presets

| Zone | Main Accent | Floor | Walls / Props | Lighting | Audio Motif | Distinct Markers |
|---|---|---|---|---|---|---|
| Core Spine | Amber | Dark gray scuffed metal | Broken consoles, cable bundles, emergency strips | Flickering amber | Low drone + air hiss | Central station plate, painted directions |
| Crew Quarters | Warm amber / brown | Worn matting, stains | Bunks, small lights, personal items, cups, patches | Dim warm lamps | Soft detuned hum, paper rustle | Small warm personal objects, photos |
| Hydroponics | Green / cyan | Dark soil, moisture, glass tubes | Plants, water tanks, cracked glass | Soft green ambient, cyan water | Water drips, wet reverb | Fog, plants, water puddles |
| Cryo / Med | Blue / white | Pale gray, frost | Cryo caskets, glass, medical trays | Cool blue glow, frost | Low airy tone, faint hiss | Frost, glass, white breath |
| Reactor | Orange / violet | Burned metal, warning stripes | Pipes, cores, heavy machinery | Strong orange pulse, violet radiation edge | Mechanical pulse, metal stress | Heat shimmer, orange glow, radiation signs |
| Airlock / Outer Hull | Red / white / black | Black hull plating, stars through viewports | Pressure locks, gauges, hull seams | Minimal, white/red hazard | Vacuum rumble, pressure ticks | Viewports, starfield, hazard chevrons |
| Maintenance Tunnels | Amber / dark gray | Cramped pipe floor | Exposed pipes, valves, cables | Very dark, small amber bulbs | Creaks, distant metal | Narrow corridors, hazard tape |

### 10.2 Coherence Rule

No zone may introduce a new base material family. All zones are variations of the same worn station:

- Metal.
- Pipes.
- Glass.
- Cables.
- Grime.
- Warning paint.
- Moisture or heat effects.

If a zone needs to feel different, change the accent color, lighting, prop density, and floor wear — not the fundamental art style.

### 10.3 Decay Levels

The level designer may set a decay level for each area. Visuals should support three levels:

| Decay Level | Visual Treatment |
|---|---|
| Intact | Lights work, minor grime, few debris |
| Damaged | Flickering lights, cracks, hanging cables, small leaks |
| Critical | Broken glass, large stains, exposed wiring, heavy debris, hazard markers |

**Why:** This lets different levels feel like different stages of the station’s failure without breaking the coherent style.

---

## 11. Object Visual Language

All interactive objects should follow a consistent state system.

### 11.1 Object States

| State | Visual |
|---|---|
| Inactive / dead | Dark gray, no glow |
| Active / usable | Amber outline or small amber light |
| Selected / in range | Bright amber outline |
| Locked | Red outline + lock icon |
| Damaged | Cracks, sparks, red warning |
| Powered | Amber glow |
| Depleted | Dim icon, red slash |
| Success | Brief cyan flash |

### 11.2 Key Objects

#### O2 Canister

- Small cylindrical object.
- Cyan glow when active.
- Valve icon.
- When inserted, cyan light strengthens nearby.

#### Power Cell

- Rectangular pack.
- Amber glow.
- Bolt icon.
- When used, nearby lights flicker back on.

#### Sealant / Patch Tool

- Compact tool.
- Amber outline.
- When used, white foam/steam particles cover the breach.
- Breach particles stop when successful.

#### Door

- Sliding metal panel.
- Amber edge when open.
- Red edge when locked.
- Small status light:
  - Amber: openable.
  - Gray: dead.
  - Red: locked or hazard.

#### Console

- Flat screen with amber terminal text.
- Broken consoles have cracked glass and dim text.
- Active consoles show small scrolling data.

#### Vents

- Metal grates.
- O2 vents show cyan airflow.
- Damaged vents show white steam.

#### Airlock

- Large circular or rectangular hatch.
- Red/white hazard stripes.
- Pressure gauge with needle.
- When cycled, lights blink in sequence:
  - Amber
  - Cyan
  - Red
  - Amber

---

## 12. Particle System

Particles should be subtle and purposeful.

### 12.1 Allowed Particles

| Particle | Use | Color |
|---|---|---|
| Dust | General atmosphere in light beams | Pale gray |
| Steam | Breaches, vents, cryo | White / cyan |
| Water droplets | Hydroponics, leaks | Cyan |
| Frost | Cryo areas | White / blue |
| Heat shimmer | Reactor | Orange |
| Radiation specks | Radiation zones | Violet |
| Sparks | Damaged power | Amber |
| Foam | Sealant use | White |

### 12.2 Limits

- Maximum active particles on screen: **120**.
- No particle effect should obscure the player or important UI.
- Particles should move slowly unless representing a breach.
- Breach particles move faster and flow directionally.

---

## 13. Audio Design

Audio is part of the visual experience. The game should feel like the station is dying, not like a soundtrack is playing over it.

### 13.1 Audio Philosophy

- Sparse, ambient, mechanical.
- No melodic score for most of the game.
- Sound layers should respond to player state.
- Critical information should have both audio and visual representation.
- Avoid loud alarm spam. Use short, sharp, diegetic warnings.

### 13.2 Music Direction

The “music” is an ambient score made from layered sound sources.

#### Base Layer

- Low drone:
  - Pitch: around **55Hz**.
  - Timbre: muted triangle or sine with slow tremolo.
  - Volume: very low.
  - Purpose: station presence.

- Air breath:
  - Filtered noise.
  - Slow swells.
  - Volume: low.
  - Purpose: feeling of vacuum and pressure.

- Metal:
  - Occasional creaks, knocks, distant panel shifts.
  - Random interval: every **4–9 seconds**.
  - Purpose: abandoned station movement.

#### State Layers

| State | Added Audio |
|---|---|
| Powered room | Soft pad, slight hum |
| Hydroponics | Water drips, wet reverb |
| Cryo | Airy hiss, faint frost crackle |
| Reactor | Low mechanical pulse, around **54 BPM** |
| Low O2 | Heartbeat, around **70–90 BPM** |
| Power off | Drone lowers, ambient hum disappears, player breathing becomes clearer |
| Breach | Air hiss, sharp alarm stabs |
| Radiation | Geiger crackle |
| Success | Drone resolves, cyan hum becomes stable |

#### Music Rules

- No melody during normal survival.
- No victory fanfare.
- No long dramatic strings.
- If a musical phrase is used, it should be a detuned, slow, broken tone.
- The loudest moment is the breach alarm, and it should still be controlled.

### 13.3 Dynamic Audio Rules

Use these rules for implementation:

1. **Normal state**
   - Base drone at low volume.
   - Occasional metal creak.
   - Air breath.

2. **Powered zone**
   - Add soft pad.
   - Slight hum near consoles.

3. **Low O2 below 30%**
   - Add heartbeat.
   - Reduce music layer by **3dB**.
   - Increase player breathing clarity.

4. **Power off**
   - Remove station pad.
   - Lower drone by **6dB**.
   - Add muffled silence under player light.

5. **Breach active**
   - Add air hiss from breach direction.
   - Add alarm stab every **1.2 seconds**.
   - Alarm is short: 150ms.
   - No continuous wail.

6. **Radiation active**
   - Add Geiger crackle.
   - Crackles increase with proximity.
   - Use spatial panning if stereo is available.

7. **Success**
   - Drone becomes steady.
   - Add quiet cyan hum.
   - Stop alarm and heartbeat.

### 13.4 Sound Effects List

#### Movement

| SFX | Description |
|---|---|
| Footstep metal | Dull step on metal plate |
| Footstep grate | Slightly hollow step |
| Footstep water | Small splash, only in puddles |
| Footstep ice | Soft crunch, cryo areas |
| Footstep dust | Dry scrape, maintenance tunnels |

#### Station Systems

| SFX | Description |
|---|---|
| Door open | Slow hydraulic slide |
| Door close | Heavy mechanical thud |
| Door locked | Dull lock clunk |
| Airlock cycle | Sequence of ticks and hiss |
| Vent open | Low air release |
| O2 canister insert | Small valve click |
| Power cell insert | Electrical snap |
| Console boot | Short static then amber blip |
| Console dead | Muffled buzz |
| Light flicker | Tiny electrical crackle |

#### Hazards

| SFX | Description |
|---|---|
| O2 low | Slow breath, heartbeat |
| Breach | Air rushing outward |
| Radiation | Geiger crackle |
| Cryo | Frost crackle, airy hiss |
| Reactor | Low pulse, metal stress |
| Alarm | Short red warning beep |

#### UI

| SFX | Description |
|---|---|
| Menu select | Short square-wave blip |
| Menu back | Lower blip |
| Item pickup | Small mechanical click |
| Item use | Valve click or electrical snap |
| Failure | Dull thud, no alarm |
| Scan | Soft cyan ping |

### 13.5 Audio Levels

Suggested relative levels:

- Music / ambient: **-18dB**
- Footsteps: **-12dB**
- Major SFX: **-6dB**
- Alarm: **-3dB**, but short and limited
- UI: **-12dB**

**Why:** The player should hear the station, not be overwhelmed by it.

---

## 14. UX Flow

### 14.1 First Session

1. Boot screen:
   - Black.
   - Single amber light.
   - `[ENTER] BOOT`.

2. First gameplay area:
   - Player wakes in a dark section.
   - O2 bar is visible.
   - One objective prompt:
     - `FIND O2`
   - First interactable object is clearly outlined when approached.

3. First tutorial teaching:
   - No written tutorial.
   - Learn through environmental prompts:
     - Walk to light.
     - See amber outline.
     - Press interact.
     - Hear confirmation.
     - See O2 change.

### 14.2 General Flow

- The HUD should be always visible but unobtrusive.
- Objective text only changes when the objective changes.
- Zone names should not flash. They appear briefly only at major junctions:
  - `CREW QUARTERS`
  - `HYDROPONICS`
  - `REACTOR`
  - `AIRELOCK`

### 14.3 Failure / Success Flow

- Death:
  - Screen desaturates.
  - O2 or hazard state is shown once.
  - Cause of death appears.
  - No long animation.

- Success:
  - Lights stabilize.
  - Cyan glow becomes steady.
  - Music resolves.
  - One line of text:
    - `STATION STABILIZED`

---

## 15. Accessibility and Readability

### 15.1 Colorblind Support

- Never use red/green as the only distinction.
- Use icons and shapes.
- O2: cyan circle.
- Power: amber bolt.
- Hazard: red triangle.
- Radiation: violet diamond.
- Lock: lock icon.

### 15.2 Motion Sensitivity

- No rapid flicker above 3Hz.
- No full-screen strobing.
- Screen shake is minimal and optional.
- Particle density should not create visual noise.

### 15.3 Audio Dependency

- All critical state changes must be visible.
- All critical UI choices must be selectable without sound.
- Audio should enhance, not explain, the game.

---

## 16. What Is Deliberately Cut

The following elements are intentionally not part of the visual design:

| Cut Item | Reason |
|---|---|
| 3D models | Unnecessary for top-down readability and browser scope |
| Isometric perspective | Station plans are clearer top-down |
| Permanent minimap | Breaks claustrophobia and adds HUD clutter |
| Full inventory screen | Survival only needs three resource slots |
| Cinematic cutscenes | The station should be discovered, not narrated |
| Gore | Horror should come from environment and systems |
| Enemy bestiary | The derelict is the threat |
| Complex status screen | Too much UI for a survival atmosphere |
| Bright neon palette | Would break the decayed industrial mood |
| Continuous loud alarm music | Desensitizes the player and breaks tension |

---

## 17. Integration Notes for Other Agents

### 17.1 Level Design Handoff

When applying visuals to designed levels:

- Use one zone preset per area.
- Keep the base material system consistent.
- Use decay levels to vary damage.
- Place amber emergency lights at regular intervals.
- Ensure every major interactable object has a clear visual state.
- Ensure every hazard has a visible marker and a corresponding audio cue.
- Ensure every locked or unavailable action shows a red lock or missing-resource prompt.

### 17.2 Audio Integration Notes

- Ambient music is layered, not a single track.
- Audio stems should be toggleable by game state.
- Breach, radiation, and O2 states should affect audio dynamically.
- UI sounds should be very short and consistent.
- All directional hazard sounds should pan toward the hazard if stereo is available.

### 17.3 UI Integration Notes

- Keep HUD text short.
- Use uppercase monospace/stencil.
- Use amber for active systems.
- Use cyan only for O2/success/water.
- Use red only for danger/lock/fail.
- Use violet only for radiation.
- Do not add permanent labels for every room.

---

## 18. Reference Texture Generation Code

This optional code is a reference for generating a coherent worn metal tile using Canvas 2D. It is not required for gameplay logic.

```js
function makeMetalTile(size = 32, base = '#1E262E', accent = '#384550') {
  const canvas = document.createElement('canvas');
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext('2d');

  ctx.fillStyle = base;
  ctx.fillRect(0, 0, size, size);

  // Subtle panel noise
  for (let i = 0; i < size * size * 0.18; i++) {
    const x = Math.random() * size;
    const y = Math.random() * size;
    const a = Math.random() * 0.08;
    ctx.fillStyle = `rgba(0, 0, 0, ${a})`;
    ctx.fillRect(x, y, 1, 1);
  }

  // Light edge
  ctx.strokeStyle = accent;
  ctx.lineWidth = 1;
  ctx.globalAlpha = 0.35;
  ctx.strokeRect(0.5, 0.5, size - 1, size - 1);
  ctx.globalAlpha = 1;

  // Scratches
  ctx.strokeStyle = 'rgba(207, 201, 188, 0.12)';
  for (let i = 0; i < 4; i++) {
    const x1 = Math.random() * size;
    const y1 = Math.random() * size;
    const x2 = x1 + (Math.random() - 0.5) * 10;
    const y2 = y1 + (Math.random() - 0.5) * 10;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
  }

  // Dark stain
  const gradient = ctx.createRadialGradient(
    Math.random() * size,
    Math.random() * size,
    1,
    Math.random() * size,
    Math.random() * size,
    size * 0.5
  );
  gradient.addColorStop(0, 'rgba(0, 0, 0, 0.18)');
  gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);

  return canvas;
}
```

---

## 19. Reference Ambient Audio Code

This optional code is a reference for the base station ambience. It should be layered and modified by game state.

```js
function createStationAmbience(audioCtx) {
  const master = audioCtx.createGain();
  master.gain.value = 0.12;
  master.connect(audioCtx.destination);

  // Low drone
  const drone = audioCtx.createOscillator();
  drone.type = 'triangle';
  drone.frequency.value = 55;

  const droneGain = audioCtx.createGain();
  droneGain.gain.value = 0.35;

  const tremolo = audioCtx.createOscillator();
  tremolo.frequency.value = 0.08;

  const tremoloGain = audioCtx.createGain();
  tremoloGain.gain.value = 0.12;

  tremolo.connect(tremoloGain);
  tremoloGain.connect(droneGain.gain);

  drone.connect(droneGain);
  droneGain.connect(master);

  // Air noise
  const bufferSize = audioCtx.sampleRate * 2;
  const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
  const data = buffer.getChannelData(0);

  for (let i = 0; i < bufferSize; i++) {
    data[i] = Math.random() * 2 - 1;
  }

  const noise = audioCtx.createBufferSource();
  noise.buffer = buffer;
  noise.loop = true;

  const noiseFilter = audioCtx.createBiquadFilter();
  noiseFilter.type = 'lowpass';
  noiseFilter.frequency.value = 400;

  const noiseGain = audioCtx.createGain();
  noiseGain.gain.value = 0.18;

  noise.connect(noiseFilter);
  noiseFilter.connect(noiseGain);
  noiseGain.connect(master);

  drone.start();
  tremolo.start();
  noise.start();

  return {
    master,
    droneGain,
    noiseGain
  };
}
```

Use this only as a reference. The final audio should be layered with state-dependent effects as described in section 13.