# visual.md

Working title: **DERELICT STATION**

This document defines the visual, UX, music, and sound-effect design for a 2D top-down survival game set on a derelict orbital space station. It is written to be handed off directly to integration.

Core visual promise:

> The station is a system. The player reads systems, not scenery.

Every important state — O2, power, hull, drones, coolant, launch requirements, and de-orbit pressure — must be readable instantly, without relying on color alone.

---

## 1. Dimensionality

### Decision

The game is **flat 2D top-down**.

- No 3D.
- No 2.5D perspective.
- No camera rotation.
- No zooming.
- No parallax.
- No exterior space gameplay.
- No vertical movement.
- No zero-gravity player movement.

### Logic

The gameplay design is centered on rooms, doors, airflow, power, and drones. The most important visual boundary is the **room boundary**. A flat top-down view makes doors, room state, airflow, and drone movement easier to read than 3D or 2.5D.

A 2.5D look would add faux-depth but could blur the exact boundary between rooms, which is where the survival tension lives.

### Camera

The camera is a fixed top-down orthographic camera.

- Follows the player.
- No rotation.
- No zoom.
- No parallax.
- No exterior view.
- No looking at walls from an angle.

The player should always be near the center of the screen. The camera should show the current room and enough adjacent wall to make doors readable.

### Recommended Visual Scale

For browser integration, use a lightweight 2D scale.

- Base tile: **96 px** at 1080p
- Player sprite: **32–40 px**
- Drone sprite: **36–44 px**
- Machines: **64–128 px**
- Pickups: **20–28 px**
- HUD panels: UI scale independent of world scale

This is a recommended scale, not a physics rule. The engine may scale the world, but proportions should remain similar.

### Visual Layer Order

Use this draw order:

1. Floor
2. Floor decals and non-interactive room markings
3. State overlays: airflow, power conduits, breach effects, hazard shimmer
4. Machines, doors, items, player, drones
5. Particles and impact effects
6. Screen vignettes and warning overlays
7. HUD

Do not use dynamic shadows. Use flat sprites with subtle dark underlays if needed for object separation.

---

## 2. Art Direction

### Visual Identity

The game should look like a **practical, worn, emergency-mode space station**.

It is not:

- Not cyberpunk neon.
- Not cartoonish.
- Not horror-gore.
- Not sleek new space station.
- Not sci-fi fantasy.
- Not a maze.

It is:

- Functional.
- Damaged.
- Still operating.
- Slightly lived-in.
- Readable as an emergency system.
- Cold, mechanical, and controlled.

The station is dying, but the player is not helpless. The visuals should communicate **managed degradation**, not chaos.

### Style Pillars

#### 1. Readability First

Decoration must never compete with state information.

If a visual element could be mistaken for O2, power, hull damage, drone threat, or a warning, cut it or make it more neutral.

#### 2. Systemic Legibility

The HUD, map, and world should show the same system states.

The player should be able to answer these questions in under one second:

- Can I breathe here?
- Is this room breached?
- Is this room powered?
- Is a drone here?
- What is the next objective?
- What is missing for launch?
- How much time do I have?

#### 3. Worn Functionality

The station should look like maintenance happened here long ago.

Use:

- Scratched metal plating.
- Faded painted lines.
- Scratched decals.
- Worn caution stripes.
- Loose cables.
- Small dust particles.
- Dimmed lights.
- Functional warning lights.

Avoid excessive gore, blood, corpses, and horror detail. The tension comes from systems failing, not from graphic damage.

#### 4. Controlled Tension

The player should feel pressure, not panic.

Visual warnings should be:

- Clear.
- Persistent.
- Icon-based.
- Labeled.
- Audible.
- Not strobing.
- Not full-screen noise.

Use subtle pulses, not chaotic flashing.

---

## 3. Core Color and Icon System

### State Colors Are Reserved

State colors are not decoration. They are reserved for system information.

Room accent colors may be used for floors, wall panels, and set dressing, but they must not imitate state colors.

| Token | Hex | Meaning | Reserved Use |
|---|---:|---|---|
| `o2` | `#4fd8ff` | Breathable air | Player O2, room O2, O2 machines, airflow particles |
| `integrity` | `#77f2a8` | Player survivability | Player Integrity bar, medkit icon |
| `power` | `#ffb300` | Electrical power | Power conduits, power nodes, power cells |
| `breach` | `#ff4d4d` | Hull failure/damage | Breach effects, hull warnings, damage feedback |
| `drone` | `#ff8a00` | Automated threat | Drones, drone map markers, drone alerts |
| `coolant` | `#62a4ff` | Reactor coolant | Coolant cells, coolant timer, reactor coolant flow |
| `objective` | `#ffffff` | Action/progress | Objective marker, interaction highlight, checklist checks |
| `base_floor` | `#171c22` | Station floor | Neutral room floor |
| `base_wall` | `#2a3138` | Station wall | Neutral wall and HUD panel background |
| `text` | `#eaf2f8` | Primary text | HUD text |
| `text_dim` | `#9aa7b5` | Secondary text | Labels, old event log entries |

### Why Icons and Text Matter

Color is never the only signal.

Every critical state must also use:

- An icon.
- A label.
- A shape.
- An animation.
- A sound cue.

This is required for accessibility and for fast readability.

### Core Icons

| State | Icon | Shape Language |
|---|---|---|
| O2 | Air waves: three short horizontal wavy lines | Soft, rounded, system-like |
| Integrity | Shield | Protection, player survival |
| Power | Lightning bolt | Electrical energy |
| Hull breach | Cracked hexagon | Structural failure |
| Drone | Triangle with exclamation | Threat |
| Coolant | Snowflake | Reactor cooling |
| Fuel | Fuel rod / vertical capsule with flame tip | Installable resource |
| Objective | Chevron | Direction, next action |
| Warning | Triangle with exclamation | Urgent alert |
| Complete | Rounded check | Requirement satisfied |
| Failed | Rounded X | Requirement missing |

### Shape Language

- Rounded shapes: resources, player, O2, usable items.
- Angular shapes: hazards, breaches, drones.
- Straight lines: power, conduits, doors, airflow.
- White: player action, objective, progress, checklist completion.

---

## 4. Typography and UI Style

### Type Style

Use a clean, high-contrast sans-serif UI font.

Recommended style:

- Labels: uppercase sans-serif
- Numbers: tabular/monospaced numerals
- Timer text: monospaced or tabular so it does not jump
- Avoid decorative sci-fi fonts for critical numbers

Suggested pairing:

- UI font: **Inter**, **Roboto**, or similar clean sans
- Timer/numeric font: **JetBrains Mono**, **IBM Plex Mono**, or similar

### HUD Panel Style

HUD panels should be flat and readable.

- Dark translucent background: `rgba(10, 14, 18, 0.82)`
- 1 px border: `#3a4450`
- No heavy bevels
- No animated sci-fi clutter
- No unnecessary glow
- High contrast text
- Icons left-aligned with values where useful

### Visual Hierarchy

Priority order on screen:

1. Player critical state
2. Active warning banner
3. Interaction prompt / active channel
4. Current room status
5. Map and launch checklist
6. Time and objective
7. Event log
8. World decoration

The player should not need to scan the whole screen to know if they are dying.

---

## 5. Core State Grammar

This is the main contract between visual design and gameplay state.

### 5.1 Player O2

#### Display

Player O2 is shown in the top-left vitals panel.

- Bar color: `o2` cyan
- Icon: air waves
- Numeric value: `O2 64`
- Bar shape: rounded ends
- Warning below 25: `LOW` label appears
- Critical below 10: `CRITICAL` label appears, bar pulses white/cyan

#### World Feedback

- Suit O2 light on player backpack pulses cyan when low.
- Below 10, a subtle cyan vignette pulses at the screen edges.
- At 0, the vignette intensifies slightly and the O2 warning sound repeats.

#### Logic

Player O2 is the first death pressure. It must be impossible to miss. The HUD number is authoritative; the suit light and vignette are secondary feedback.

---

### 5.2 Player Integrity

#### Display

Player Integrity is shown directly below Player O2.

- Bar color: `integrity` green
- Icon: shield
- Numeric value: `INTEGRITY 82`
- Bar shape: straight edges, slightly angular
- Warning below 25: `LOW`
- Critical below 10: `CRITICAL`, bar pulses white/green

#### Damage Feedback

When player takes damage:

- Brief red hit flash on player sprite.
- Small red vignette flash, max 0.2 seconds.
- Subtle screen shake, max 4 px, 0.15 seconds.
- 0.5 second invulnerability: player sprite flickers white at 10 Hz.

#### Logic

Integrity is the player’s final survivability stat. It must be visually distinct from room hull, so it uses the shield icon and the word `INTEGRITY`.

---

### 5.3 Room O2

#### Current Room Status

The current room status panel shows:

```
STORAGE
O2 20 LOW
HULL 30 LOW
POWER NO POWER
DRONE --
```

Room O2 states:

| Room O2 | Display |
|---:|---|
| 60–100 | `O2 80` |
| 30–59 | `O2 45 LOW` |
| 1–29 | `O2 12 LOW` |
| 0 | `O2 0 LOW` |

Use the air-wave icon next to O2.

If O2 is below 30, add a small warning triangle.

If O2 is 0, the air-wave icon becomes outlined with an X.

#### Map O2 Display

Each map room node shows a small air icon in the top-left corner.

- High O2: filled cyan air icon
- Medium O2: half-filled air icon
- Low O2: outlined air icon with exclamation
- Zero O2: air icon with X

This is shape-based, not color-only.

#### Logic

Room O2 is the main environmental pressure. The player should be able to read room air quality from both the current room panel and the map.

---

### 5.4 Room Hull and Breach

#### Hull Display

Current room status shows:

```
HULL 30 LOW
```

If hull is below 30, show `LOW`.

If hull is 0, show:

```
HULL 0 BREACH
```

The word `BREACH` appears with a cracked hexagon icon.

#### Breach World Visual

When a room is breached:

- A jagged dark opening appears on the room floor or wall.
- Vacuum particle streaks move inward or outward depending on airflow.
- The room gets a thin red border on the map.
- The map room node gets a cracked hexagon icon.
- Event log entry appears: `Hull breach in STORAGE`.
- Warning banner appears if the breach is recent or critical.

#### Low Hull Visual

When hull is below 30 but not breached:

- Small cracks appear on floor or wall decals.
- Occasional tiny dust puff.
- Map node gets a small cracked hexagon icon.

#### Logic

Breach is one of the most important states in the game. It must be unmistakable. The word `BREACH`, the cracked icon, the map border, and the vacuum particles all reinforce it.

---

### 5.5 Power State

#### Power Display

Current room status shows one of:

```
POWER NO POWER
POWER POWERED
POWER EPC 4:12
POWER CELL 2:03
POWER REACTOR
```

Rules:

- Local timed source: show source and timer.
- Non-local power path: show `POWERED`.
- Reactor: show `REACTOR`.
- No power: show `NO POWER` with gray lightning icon.

#### Power World Visual

Power is shown by thin wall conduits.

- Unpowered: dark gray conduit lines.
- Powered: amber conduit glow.
- Timed power source: small amber pulse every second.
- Reactor power: stronger amber glow, slightly deeper pulse.
- Power loss: conduits fade out over 0.3 seconds.
- Power cell expiration: brief amber blink before fade.

Power nodes show a small diegetic display:

```
EPC 3:12
CELL 2:05
REACTOR
EMPTY
```

#### Map Power Display

Each map node has a lightning icon in the top-right corner.

- Off: gray outline
- On: amber filled
- Reactor: amber filled with small reactor dot or pulse

#### Logic

Power propagates through open doors. The player must understand which rooms are powered and why. Conduits along walls make power paths readable without adding extra UI.

---

### 5.6 Drone State

#### Drone Visual

Drones are maintenance bots, not horror enemies.

Base sprite:

- Circular or squarish hovering body.
- Two short mechanical arms.
- Orange caution light.
- Small scanner arm or scanner ring.
- Slight hover bob.

Drone states:

| State | Visual |
|---|---|
| Inactive | Parked, gray light, no motion |
| Patrol | Slow movement, soft hover, gray/low orange light |
| Alert | Orange light brightens, small orange ring or triangle appears above drone, movement speed increases |
| Attack | Brief orange zap effect, short red/orange flash on player |
| Disabled | Smoking, one arm bent or sparking, gray light, no motion |

#### Drone Map Display

Each map node has a drone icon in the bottom-right corner when an active drone is in that room.

- Inactive: no icon
- Active: orange triangle
- Disabled: no icon

#### Current Room Drone Display

Current room status shows:

```
DRONE ACTIVE
```

or

```
DRONE --
```

#### Logic

Drones are avoidable hazards. They must be readable as machines, not monsters. The orange triangle and word `DRONE` make the threat clear without relying on sprite detail.

---

### 5.7 Reactor Coolant

#### Coolant Timer Display

When the reactor is online, the player must see coolant time clearly.

Display a dedicated coolant chip near the time panel or current room status:

```
COOLANT 2:14
```

Icon: snowflake.

States:

| Coolant | Display |
|---|---|
| Above 30 | `COOLANT 2:14` |
| 30 or below | `COOLANT 0:24` flashes |
| Expired | `COOLANT EXPIRED` with warning |

#### Reactor World Visual

Reactor core states:

| State | Visual |
|---|---|
| Offline | Dark core, gray lights |
| Damaged | Red blinking light, wrench prompt |
| Coolant pump repaired | Blue snowflake light |
| Coolant active | Blue-white flow lines, coolant timer visible |
| Spin-up | Core rotates, white-blue progress ring |
| Online | Amber-red glow, strong power conduits |
| Coolant low | Blue timer flashes, warning banner |
| Coolant expired | Core glow turns red, steam puffs, heat shimmer |
| Heat hazard | Red floor pulse in Reactor Core, steam, warning |

#### Logic

Coolant is a hard timer. If the player misses it, launch can fail. It needs its own dedicated display, not just a power label.

---

### 5.8 Launch Checklist

The launch checklist appears once the player has entered Bridge or Shuttle Bay, or once the reactor has been online at least once.

Display:

```
LAUNCH
[✓] REACTOR ONLINE
[ ] SHUTTLE POWERED
[✓] COMPUTER PRIMED
[ ] FUEL INSTALLED
[ ] SHUTTLE O2 42/60

LAUNCH 34%
```

Requirement states:

- Complete: white rounded check
- Incomplete: gray rounded X
- Failing during launch: red X flashes briefly, event log shows reason

If launch channel resets, show:

```
LAUNCH RESET — SHUTTLE O2 LOW
```

or similar specific reason.

#### Shuttle Visual

The shuttle in Shuttle Bay has state lights:

- Gray: inactive
- White: requirements satisfied
- Blue-white: launch channel active
- Red: requirement failed / launch reset
- Bright white: launch success

#### Logic

The final phase requires multiple systems to stay true simultaneously. The checklist removes ambiguity. The player should never have to guess why launch is not progressing.

---

### 5.9 Objective State

The main objective is displayed at top-center.

Example:

```
DAY 3
TIME TO DE-ORBIT 02:14
OBJECTIVE: Bring Reactor Online
```

Objective markers:

- Current objective room on map: white chevron.
- Relevant machine: interaction prompt when close.
- Objective complete: soft major blip, event log entry.

Do not add subobjective text unless it is short and useful. The interaction prompt should handle local direction.

---

### 5.10 Warnings

Warnings must be clear, labeled, and audible.

Warning banner location: top-center, below the time/objective panel.

Example:

```
WARNING: PLAYER O2 LOW 12
WARNING: HULL EVENT — STORAGE 0:07
WARNING: COOLANT LOW 0:24
WARNING: DE-ORBIT 1:45
WARNING: LAUNCH RESET — FUEL MISSING
```

Warning rules:

- One warning type may persist; do not stack five identical warnings.
- If multiple warnings occur, show the most critical first.
- Persistent warnings pulse slowly, max 2 Hz.
- Critical warnings use a white border with red icon, not full-screen strobing.
- Each warning has a matching event log entry.

Warning priority:

1. Player O2 critical
2. Player Integrity critical
3. Launch reset
4. Room breach
5. Reactor coolant low/expired
6. Hull event warning
7. Power source low/expiring
8. De-orbit warning
9. Room O2 low

---

## 6. HUD Layout

### Target Resolution

Design for:

- Primary: 1920x1080
- Minimum comfortable: 1366x768
- UI scales with screen size
- Keep HUD inside a safe area with 24 px margin

### Layout Diagram

```text
+--------------------------------------------------------------------------+
| VITALS                    |  DAY 3   02:14 TO DE-ORBIT                 |
| O2 64                     |  OBJECTIVE: Bring Reactor Online           |
| INTEGRITY 82              |                                            |
+--------------------------------------------------------------------------+
|                                 | SHUTTLE BAY                           |
|                                 | O2 0  HULL 50                         |
|                                 | POWER NO POWER  DRONE ACTIVE          |
|                                 |                                       |
|                                 | LAUNCH CHECKLIST when active          |
|                                 | [inventory slots]                     |
|                                 | [station map]                         |
+--------------------------------------------------------------------------+
| EVENT LOG                       | [E] HOLD — REACTOR SPIN-UP [====]    |
| - Power cell installed          |                                       |
| - Hull breach in Storage        |                                       |
+--------------------------------------------------------------------------+
```

The warning banner overlays the top-center area when active.

---

## 7. HUD Components

### 7.1 Vitals Section

Location: top-left.

Content:

- Player O2 bar
- Player Integrity bar
- Numeric O2
- Numeric Integrity
- LOW / CRITICAL labels
- Air-wave and shield icons

Recommended size:

- Panel width: 240 px
- Bar width: 180 px
- Bar height: 18 px
- Label size: 14 px
- Numeric size: 22 px

Behavior:

- O2 warning below 25
- O2 critical below 10
- Integrity warning below 25
- Integrity critical below 10
- Critical state pulses slowly and plays audible warning

Logic:

This is the most important survival information. It must always be visible and never obscured.

---

### 7.2 Current Room Status Section

Location: top-right.

Content:

- Room name
- Room O2
- Hull value
- Power state
- Drone state
- Breach state

Example:

```text
CREW QUARTERS
O2 70  HULL 100
POWER EPC 3:12
DRONE --
```

Breach example:

```text
STORAGE
O2 0  HULL 0 BREACH
POWER NO POWER
DRONE --
```

Drone example:

```text
CARGO HOLD
O2 0  HULL 80
POWER NO POWER
DRONE ACTIVE
```

Power state examples:

```text
POWER NO POWER
POWER POWERED
POWER EPC 4:12
POWER CELL 2:03
POWER REACTOR
```

Logic:

The current room is the most important immediate context. The player should not need to open a map to know if the room is breathable, powered, breached, or threatened.

---

### 7.3 Time and Objective Section

Location: top-center.

Content:

- Day number
- Time to de-orbit
- Main objective text

Example:

```text
DAY 4
TIME TO DE-ORBIT 02:14
OBJECTIVE: Prime Launch Computer
```

Warning:

When time to de-orbit is below 120 seconds:

```text
DE-ORBIT 1:45
```

The timer text turns red and the warning banner appears.

Logic:

The global timer is the hard failure condition. It must always be visible.

---

### 7.4 Launch Checklist Section

Location: right side, below current room status.

Visible when:

- Player has entered Bridge or Shuttle Bay, or
- Reactor has been online at least once.

Content:

```text
LAUNCH
[✓] REACTOR ONLINE
[ ] SHUTTLE POWERED
[✓] COMPUTER PRIMED
[ ] FUEL INSTALLED
[ ] SHUTTLE O2 42/60

LAUNCH 34%
```

Requirement display:

- Complete: white check icon
- Incomplete: gray X icon
- Failing during launch: red X flash
- Launch progress: horizontal bar below checklist

If shuttle O2 is below 60, show current value:

```text
SHUTTLE O2 42/60
```

If launch channel resets, show specific reason:

```text
LAUNCH RESET — REACTOR OFFLINE
LAUNCH RESET — SHUTTLE O2 LOW
LAUNCH RESET — FUEL MISSING
LAUNCH RESET — COMPUTER NOT PRIMED
LAUNCH RESET — SHUTTLE UNPOWERED
```

Logic:

The final objective is multi-system. The checklist must tell the player exactly what is missing.

---

### 7.5 Inventory Section

Location: right side, above station map.

Content:

- 6 slots
- Item icons
- Stack counts
- Selected slot indicator
- Key labels: 1–6

Recommended slot size:

- Slot: 48 px
- Gap: 8 px
- Icon: 28 px
- Count: bottom-right corner
- Selected slot: white 2 px outline

Behavior:

- Select item with 1–6.
- Selected slot gets white outline.
- O2 Tank and Medkit are instant-use.
- Other items show interaction prompts when valid.
- If inventory is full, pickup prompt shows `INVENTORY FULL` and plays UI error.

Logic:

Inventory is simple but limited. The player should be able to select and use items without leaving the current context.

---

### 7.6 Interaction Prompt Section

Location: bottom-center.

Content:

- Current interactable action
- Required item, if applicable
- Channel progress
- Pause reason
- Reset reason

Examples:

```text
E — PICK UP O2 TANK
HOLD E — REPAIR O2 GENERATOR
HOLD E — PATCH HULL
HOLD E — INSTALL POWER CELL
HOLD E — REACTOR SPIN-UP
HOLD E — INSTALL FUEL
HOLD E — LAUNCH
```

Paused example:

```text
HOLD E — REACTOR SPIN-UP
PAUSED: NO POWER
```

Requires item example:

```text
HOLD E — INSTALL FUEL
REQUIRES: FUEL ROD
```

Reset example:

```text
LAUNCH RESET — SHUTTLE O2 LOW
```

Progress bar:

- Thin bar below text
- White fill
- Channel progress updates smoothly
- Repair channels retain progress if interrupted
- Launch channel resets to 0 with red flash if interrupted

Logic:

All actions should feel intentional. The player should always know what action is available, what is blocking it, and how much progress remains.

---

### 7.7 Event Log Section

Location: bottom-left.

Content:

- Last 5 important events
- Icon per event
- Short text
- Newest entry on top

Examples:

```text
[air] O2 Generator repaired
[light] Power cell installed in Hydroponics
[crack] Hull breach in Storage
[drone] Drone active in Shuttle Bay
[fuel] Launch requirement met: Fuel installed
```

Behavior:

- New events push old events down.
- Older entries dim.
- Critical events remain in log and also trigger warning banner.
- Do not spam the log with minor movement events.

Logic:

The log gives history without requiring the player to remember every state change. It should not become a wall of text.

---

### 7.8 Station Map Section

Location: bottom-right.

Content:

- 10 room nodes
- Door connections
- Current room highlight
- Power state
- O2 state
- Hull breach state
- Active drone state
- Objective marker
- Hull event warning marker

The map is persistent. It is not a menu. It should always be visible.

#### Room Nodes

Use abbreviated room names:

```text
DB   DOCKING BAY
CQ   CREW QUARTERS
ST   STORAGE
CH   CARGO HOLD
MB   MEDBAY
HY   HYDROPONICS
EN   ENGINEERING
RC   REACTOR CORE
BR   BRIDGE
SB   SHUTTLE BAY
```

Each node is a small rounded rectangle.

Node state icons:

| Position | Meaning |
|---|---|
| Top-left | O2 state |
| Top-right | Power state |
| Bottom-left | Hull state / breach |
| Bottom-right | Drone state |
| Center | Objective chevron |

Current room:

- Thick white outline
- Slight white fill

Breach:

- Red jagged outer border
- Cracked hexagon icon
- Room name may get red text

Objective room:

- White chevron in center

Hull event warning:

- Red target reticle over target room
- Countdown number near reticle
- Warning banner shows same information

#### Door Lines

Door connections between map nodes:

| Door State | Line Style |
|---|---|
| Open | Solid white line |
| Closed | Dashed gray line |
| Jammed | Crossed red line with small X |

Logic:

The map is a core survival tool. It must show systemic state, not just geography.

---

### 7.9 Warning Banner Section

Location: top-center, below time/objective.

Content:

- Warning icon
- Warning text
- Countdown if applicable

Examples:

```text
WARNING: PLAYER O2 LOW 12
WARNING: PLAYER O2 CRITICAL 7
WARNING: INTEGRITY LOW 20
WARNING: INTEGRITY CRITICAL 8
WARNING: ROOM O2 LOW — HYDROPONICS 22
WARNING: HULL BREACH — STORAGE
WARNING: HULL EVENT — SHUTTLE BAY 0:08
WARNING: POWER SOURCE LOW — EPC 0:45
WARNING: COOLANT LOW 0:24
WARNING: DE-ORBIT 1:45
WARNING: LAUNCH RESET — REACTOR OFFLINE
```

Behavior:

- Trigger sound on first appearance.
- Persistent warnings pulse slowly.
- Do not show more than two warnings at once.
- If more than two warnings exist, show highest priority and log the rest.
- No full-screen strobing.
- Max pulse frequency: 2 Hz.

Logic:

Warnings must be urgent but not annoying. The player should understand the warning without reading a paragraph.

---

### 7.10 Onboarding and Controls

The game should teach through diegetic prompts, not popups.

Recommended controls:

```text
MOVE: W A S D / ARROWS
INTERACT: E
SELECT ITEM: 1–6
USE SELECTED ITEM: E if applicable, or F
```

Use whatever control scheme the engine uses, but visual prompts must match.

#### Title Screen

Minimal title screen:

- Working title: **DERELICT STATION**
- Short tagline: `Survive until Day 8`
- Start button
- Control list
- State icon legend

Title visual:

- Dark station background
- Faint machine room
- No animated cinematic
- No heavy logo animation
- Small red distress mark or cracked icon

#### Tutorial Prompts

In Docking Bay and Crew Quarters, use short prompts:

```text
PICK UP WRENCH
HOLD E — REPAIR O2 GENERATOR
WATCH ROOM O2
CLOSE DOORS TO CONTROL AIRFLOW
MAP SHOWS POWER, O2, AND BREACHES
```

Do not block the player with tutorial popups. The tutorial should be environmental and prompt-based.

#### First Drone

When Drone A activates:

```text
DRONE ACTIVE — CARGO HOLD
```

The drone light changes from gray to orange. A short robotic chirp plays.

No tutorial popup is needed if the map, drone light, and event log are clear.

---

## 8. World Visuals

### 8.1 Player Sprite

The player is a top-down astronaut.

Base sprite:

- White or light gray suit
- Dark visor indicating facing direction
- Small backpack
- O2 light on backpack
- Slight footstep animation
- No detailed face
- No character portrait

Player states:

| State | Visual |
|---|---|
| Normal | Steady suit light, subtle movement animation |
| Moving | Tiny dust or boot particles, very subtle |
| Low O2 | Cyan backpack pulse |
| Critical O2 | Rapid cyan/white pulse |
| Damaged | Red flash on sprite |
| Invulnerable | White flicker for 0.5 seconds |
| Death | Suit light turns gray, screen desaturates |

Logic:

The player must always be easy to identify. The white suit gives contrast against dark station floors. The visor shows direction without needing animation-heavy detail.

---

### 8.2 Drone Sprite

Drones are maintenance bots.

Base sprite:

- Circular or compact square hover body
- Two short arms
- Orange caution light
- Small scanner element
- Slight hover bob
- No face

Drone states:

| State | Visual |
|---|---|
| Inactive | Parked, gray light |
| Patrol | Slow movement, soft hum |
| Alert | Orange ring or triangle above drone, faster movement |
| Attack | Orange zap, short red/orange flash on player |
| Disabled | Smoking, sparking, one arm bent, gray light |

Drones should not look like organic enemies. They should look like dangerous machines still doing maintenance.

---

### 8.3 Item Visuals

Items are small floor pickups.

They should be readable but not brighter than warnings.

| Item | Icon | Visual |
|---|---|---|
| Wrench | Wrench shape | Gray tool, slightly larger than other items |
| O2 Tank | Cyan canister with air-wave icon | Cyan body, white top |
| Medkit | White box with green cross | Rounded box, green cross |
| Hull Patch | Gray square with tape/plus | Flat square, subtle highlight |
| Power Cell | Amber cylinder with lightning | Amber body, lightning icon |
| EMP Charge | Dark coil with white ring | Coil shape, white pulse ring |
| Coolant Cell | Blue canister with snowflake | Blue body, snowflake icon |
| Fuel Rod | Black rod with orange flame tip | Vertical capsule |

Dropped items:

- Same icon as inventory.
- Slight floor shadow.
- No despawn visual.
- No aggressive pulsing.
- Selected target interaction shows white outline.

Logic:

Items are resources, not loot. They should be readable but not distract from system warnings.

---

### 8.4 Machine Visuals

Machines are wall-mounted or floor-anchored. They do not block movement.

General machine states:

| State | Visual |
|---|---|
| Off | Gray light, no glow |
| Damaged | Red blinking light, small crack or spark detail |
| Powered working | Function-colored light |
| Repairing | Progress ring or bar, sparks |
| Complete | Steady light, no red blink |

#### O2 Machines

O2 machines use cyan state color.

- Damaged: red blink, wrench prompt
- Powered working: cyan light
- Airflow output: subtle cyan particles when generating O2

Machines:

- Crew O2 Generator
- Hydroponics O2 Recycler
- Shuttle O2 Vent

#### Power Node

Power node is a wall panel.

Display:

```text
EMPTY
EPC 3:12
CELL 2:05
REACTOR
```

Visual:

- Empty: gray
- EPC: amber light
- Player Power Cell: amber light, cell icon
- Reactor: amber light with reactor dot
- Low timed power: amber pulse increases below 60 seconds

#### Reactor Coolant Pump

Visual:

- Pipe machine
- Snowflake icon
- Damaged: red blink
- Repaired: blue snowflake light
- Coolant cell use: blue-white flow lines
- Coolant active: small timer display or flow pulse

#### Reactor Core

The reactor is the largest machine.

States:

| State | Visual |
|---|---|
| Offline | Dark core, gray lights |
| Damaged | Red blinking core light |
| Spin-up | Rotating core, white-blue progress ring |
| Online | Amber-red glow |
| Coolant active | Blue-white flow near pump, strong power glow |
| Coolant low | Timer flashes, core glow flickers slightly |
| Coolant expired | Core glow turns red, steam, heat shimmer |
| Heat hazard | Red floor pulse in Reactor Core |

#### Launch Computer

Visual:

- Console screen
- Checklist lights
- Inactive: gray
- Priming: blue-white progress
- Primed: white light

#### Fuel Line

Visual:

- Pipe slot
- Empty: gray outline
- Fuel installed: orange/white fuel rod visible
- Complete: steady white light

#### Launch Pad

Visual:

- Large floor outline
- Shuttle silhouette
- Pad lights around edge
- Inactive: gray
- Requirements satisfied: white lights
- Launch channel active: blue-white cycling lights
- Launch reset: red flash
- Launch success: bright white flash

Logic:

Machines are system components. Their visual state should match the simulation state exactly. The player should never wonder if a machine is working, damaged, powered, or complete.

---

### 8.5 Door Visuals

Doors are the only transitions between rooms. They must be extremely clear.

Door states:

| State | Visual |
|---|---|
| Open | Door panels retracted into walls, white light line, airflow possible |
| Closed | Door panels filled, gray light line, no airflow |
| Jammed | Panels slightly askew, red flashing light, warning stripes |
| Repairing jammed | Wrench sparks, progress ring |
| Repaired | Becomes closed, red light gone |

Door frame:

- Thick wall opening
- State light on frame
- Small label or door code optional
- Map line matches door state

Airflow:

- Airflow particles only appear through open doors.
- No particles through closed or jammed doors.

Logic:

Doors are the spatial core of the game. Open, closed, and jammed must be instantly distinguishable by shape, light, and map representation.

---

### 8.6 Airflow Visualization

Airflow is visible through open doors.

Use small cyan particles moving from the higher-O2 room to the lower-O2 room.

Rules:

- No particles if O2 difference is small, below 5.
- Particle count scales with difference: `clamp(abs(A.O2 - B.O2) / 10, 1, 5)`
- Particles are small, low alpha, and slow.
- If a room is breached, particles are pulled toward the breach or through open doors to the breached room.
- Breached rooms show stronger vacuum streaks.

Logic:

Airflow is a core decision. The player must see that opening a door can move air. Subtle particles make this readable without adding a complex simulation overlay.

---

### 8.7 Power Visualization

Power is shown through wall conduits.

Rules:

- Conduits run along walls.
- Conduits glow amber when the room is powered.
- Conduits do not cross closed or jammed doors.
- Power propagation through open doors is shown by continuous conduit glow.
- When power is lost, conduits fade out.
- Power node displays show source and timer.

Logic:

Power is binary per room and propagates through open doors. Conduits make the power graph visible without requiring the player to infer it from lights alone.

---

### 8.8 Hull and Breach Visualization

Hull damage is shown by cracks and breach openings.

Low hull:

- Small floor or wall cracks
- Tiny dust puffs
- Map crack icon

Breach:

- Jagged dark opening
- Vacuum particles
- Red map border
- Cracked hexagon icon
- Event log entry
- Warning sound

Hull patch:

- Repair plate appears over breach or damaged section
- Sealing hiss
- Crack visuals removed or reduced

Logic:

Breach is a major survival event. It must be visible in the world, on the map, and in the HUD simultaneously.

---

### 8.9 Reactor Heat Hazard

When reactor coolant has expired and the reactor is online:

- Reactor Core room floor pulses red.
- Steam puffs appear near core.
- Subtle heat shimmer overlay in Reactor Core.
- Warning banner shows coolant expired.
- Player takes integrity damage while in room.

Do not make the entire screen red. The hazard is room-specific.

Logic:

The reactor heat hazard should be readable as a room hazard, not a global screen effect.

---

### 8.10 Launch Visualization

Shuttle Bay is the final convergence room.

Shuttle state lights:

- Gray: not ready
- White: ready
- Blue-white: launch channel active
- Red: launch reset
- Bright white: success

Launch channel:

- 30-second channel
- Pad lights cycle
- Shuttle engine glow builds
- Progress shown in checklist and interaction prompt
- If interrupted, lights flicker red and checklist shows reason
- If successful, screen fades white with engine sound

Logic:

Launch is the final system check. The shuttle itself should visually mirror the checklist state.

---

## 9. Room Identity and Coherence

### Rule

The station has 10 rooms. They should feel like one station, not ten different games.

All rooms share:

- Same base floor style
- Same base wall style
- Same door frame style
- Same machine state language
- Same HUD icons
- Same warning system
- Same particle system

Each room gets:

- One muted accent color
- One or two signature non-interactive details
- A room sign or floor decal with abbreviation
- A distinct but restrained material feel

Room accents are decoration only. They must not use reserved state colors.

---

### Room Table

| Room | Visual Identity | Accent | Non-Interactive Details | Why Distinct |
|---|---|---|---|---|
| Docking Bay | Clean start area, neutral gray | Cool gray | Docking clamps, faint white lights, small porthole | Safe tutorial room, visually calmer |
| Crew Quarters | Lived-in hub | Warm gray | Bunks, personal storage, soft amber wall light | Central hub should feel occupied |
| Storage | Industrial resource room | Brown/steel | Shelves, crates, caution stripes | Resource room, caution theme |
| Cargo Hold | Dark cargo space | Dark graphite | Large crates, cargo nets, hazard stripes | Drone room, darker and more dangerous |
| Medbay | Cleaner medical room | Pale blue/white | Medical beds, cross decal, sterile floor lines | Health room, contrast without state color |
| Hydroponics | Muted green life support | Desaturated green | Planters, water stains, recycler fan | Life support midpoint, organic but worn |
| Engineering | Maintenance and reactor prep | Rust orange, desaturated | Tools, coolant pump, maintenance boards | Reactor preparation, industrial |
| Reactor Core | Dangerous power core | Dark red/charcoal | Large reactor, heat vents, warning lines | Final power hazard, visually intense |
| Bridge | Tactical control room | Dark blue | Launch computer, console screens, tactical map | Launch computer room, information hub |
| Shuttle Bay | Final launch bay | Graphite/white | Large shuttle, launch stripes, fuel line | Final objective, visually open and important |

### Coherence Rules

1. Room accent must be desaturated.
2. Room accent must not look like a state color.
3. State colors only appear on machines, HUD, map icons, and effects.
4. Each room should be recognizable from its signature object, not just its color.
5. No room should introduce a new visual state language.

---

## 10. Feedback and Effects

### Action Feedback Table

| Action | Visual Feedback | Audio Feedback | Why |
|---|---|---|---|
| Pick up item | Small white blip on item, item disappears to inventory | Soft pickup blip | Confirms pickup |
| Inventory full | Red X on prompt, prompt says `INVENTORY FULL` | UI error | Prevents confusion |
| Use O2 Tank | Cyan ring around player, O2 bar rises | Air hiss + rising blip | Confirms instant use |
| Use Medkit | White/green cross flash on player, integrity bar rises | Clean chirp | Confirms healing |
| Repair start | Wrench icon, progress ring, sparks | Mechanical click | Confirms action began |
| Repair progress | Progress bar/ring fills | Soft tick at 25/50/75% | Gives channel feel |
| Repair complete | Machine light changes, red blink stops | Satisfying clank | Confirms system restored |
| Door open | Door slides, state light changes | Servo slide + thud | Confirms transition changed |
| Door close | Door slides, state light changes | Servo slide + thud | Confirms containment |
| Jammed door repair | Sparks, progress ring, jammed light changes | Rattle + clank | Confirms repair |
| Hull patch | Patch plate appears, breach closes | Sealing hiss + clank | Confirms hull restored |
| Power cell install | Conduits glow, node display updates | Hum rise | Confirms power source added |
| Power cell expiration | Amber blink, conduits fade | Descending buzz | Confirms timed power loss |
| Power loss | Conduits fade, lights dim | Breaker click + descending hum | Confirms major system change |
| EMP use | Expanding white ring, drones spark and go gray | Sweep + zap | Confirms drone disable |
| Drone activation | Drone light changes gray to orange, event log appears | Robotic chirp | Confirms threat |
| Drone alert | Orange ring above drone, movement speeds up | Short warning chirp | Confirms pursuit |
| Drone attack | Orange zap, player red flash, screen shake | Crackle zap | Confirms damage |
| Breach | Vacuum particles, red map border, warning | Metallic shriek + whoosh | Confirms major damage |
| Reactor coolant low | Coolant timer flashes, warning banner | Soft high pulse | Confirms timer pressure |
| Reactor coolant expired | Reactor glow turns red, steam, warning | Heavy thud + alarm | Confirms system failure |
| Reactor spin-up | Core rotates, progress ring fills | Rising whir | Confirms long channel |
| Launch requirement met | Checklist item turns to check, small blip | Positive blip | Confirms progress |
| Launch reset | Red flash on checklist, progress bar resets | Low descending blip | Confirms failure reason |
| Launch success | White flash, shuttle engine glow, screen fade | Engine rumble + chord | Confirms victory |

### Screen Effects

Use subtle screen effects only.

- Low O2: cyan edge vignette
- Critical O2: stronger cyan/white edge pulse
- Damage: brief red edge flash
- Breach: brief red map/HUD emphasis, not full screen
- Reactor heat: warm vignette only in Reactor Core
- Launch success: white fade
- Game over: desaturate and darken

No full-screen strobing.

No excessive screen shake.

---

## 11. Music

### Musical Identity

The music should sound like a failing station:

- Sparse
- Mechanical
- Industrial
- Tense but controlled
- Not orchestral
- Not cinematic hero music
- Not constant panic

The music supports the simulation. It does not tell the player what to do. The HUD and SFX handle urgency.

### Recommended Style

- Analog synth pads
- Low metallic pulses
- Soft filtered noise
- Mechanical textures
- Slow tempo
- Minor key

Recommended base:

- Key: D minor
- Base tempo: 72 BPM
- Final phase tempo: 90 BPM

### Music Layers

Use layerable stems rather than many separate tracks.

| Layer | Trigger | Content | Mix Note |
|---|---|---|---|
| Base station | Always during gameplay | Slow pad, low pulse, distant mechanical hum | -18 to -22 LUFS |
| Low O2 | Player O2 below 25 | Filtered breath-like noise, slow heartbeat-like pulse | Duck base slightly |
| Critical O2 | Player O2 below 10 | Faster air noise, sharper pulse | Keep below SFX warnings |
| Power loss | Major power loss | Remove pulse, leave sparse dissonant pad | Subtle, not alarm music |
| Drone alert | Drone enters alert | Short metallic stinger, optional tremolo layer | Short and dry |
| Reactor online | Reactor online | Deep sub drone, warm harmonic | Add depth, not excitement |
| Coolant low | Reactor coolant below 30 | Tick-like texture, rising tension | Do not overpower timer SFX |
| Final countdown | Time to de-orbit below 120 | Pulse increases to 90 BPM, rising pads | Urgent but controlled |
| Launch success | Launch complete | Bright major chord, quiet resolve | Clear victory, not bombastic |
| Game over | Failure | Low detuned drone, fading alarms | Melancholic, not punitive |

### Music Tracks

Minimum tracks/stems:

1. Title loop
2. Gameplay base
3. Low O2 layer
4. Power loss layer
5. Drone alert stinger
6. Reactor layer
7. Final countdown layer
8. Success theme
9. Failure theme

Tracks should loop cleanly.

### Mixing Rules

- Music should sit below SFX.
- Warnings should always be audible above music.
- No constant high-volume alarms.
- Drone alert stingers should be short.
- Reactor and final layers should build, not panic.
- Success should feel like escape, not celebration noise.

---

## 12. Sound Effects

Sound effects are part of the UX. Every critical visual warning must have a matching sound.

### SFX Design Principles

- Short.
- Clear.
- Mechanical.
- Not cartoonish.
- Not loud unless critical.
- Do not mask each other.
- Use positional audio where useful.

### Mandatory SFX List

These are required by the gameplay design.

| Event | SFX Name | Sonic Design | Notes |
|---|---|---|---|
| Low player O2 | `o2_low` | Soft air hiss, 1 Hz pulse | Starts below 25 |
| Critical player O2 | `o2_critical` | Faster air hiss, 2 Hz pulse | Starts below 10 |
| Low Integrity | `integrity_low` | Muffled thump, slow pulse | Starts below 25 |
| Critical Integrity | `integrity_critical` | Harder thump, faster pulse | Starts below 10 |
| Room breach | `breach` | Metallic shriek + vacuum whoosh + low rumble | Major event |
| Power loss | `power_loss` | Breaker click + descending hum | Major system change |
| Power cell expiration | `power_cell_expire` | Amber buzz descent + soft click | Timed power ends |
| Reactor coolant low | `coolant_low` | Soft high sine pulse, 1 Hz | Starts below 30 |
| Reactor coolant expired | `coolant_expired` | Heavy thud + red alert tone | Major failure |
| Drone activation | `drone_activate` | Robotic chirp, 3 notes, servo sound | Threat appears |
| Drone attack | `drone_attack` | Crackle zap, short | Damage feedback |
| Hull event warning | `hull_event_warning` | Two-tone horn, 300 ms | 10 second warning |
| De-orbit warning | `deorbit_warning` | Deep two-tone alarm | At 120 seconds remaining |
| Launch success | `launch_success` | Engine rumble + bright major chord | Victory |
| Game over | `game_over` | Low detuned drone, fading alarms | Failure |

### Support SFX List

These improve usability and feedback.

| Event | SFX Name | Sonic Design | Notes |
|---|---|---|---|
| UI select | `ui_select` | 1.2 kHz sine blip, 40 ms | Inventory, buttons |
| UI error | `ui_error` | Low 200 Hz square, 80 ms | Invalid action |
| Pickup | `pickup` | 700→1000 Hz sine, 60 ms | Item collected |
| Drop item | `drop` | Soft thud | Item dropped |
| Use O2 Tank | `use_o2` | Air hiss + 880 Hz blip | Instant use |
| Use Medkit | `use_medkit` | Clean 1.4 kHz chirp | Instant use |
| Repair start | `repair_start` | Mechanical click | Channel begins |
| Repair progress tick | `repair_tick` | Soft tick every 25% | Channel feedback |
| Repair complete | `repair_complete` | Clank + 1.2 kHz blip | System restored |
| Door open | `door_open` | Servo slide + thud | Door state change |
| Door close | `door_close` | Servo slide + thud | Door state change |
| Jammed door warning | `door_jammed` | Metallic rattle | Jammed state |
| Jammed door repair | `door_repair` | Clank + servo | Jam cleared |
| Power cell install | `power_install` | Hum rise | Power source added |
| Hull patch | `hull_patch` | Sealing hiss + clank | Hull restored |
| EMP use | `emp` | 200→2000 Hz sweep + zap | Drone disable |
| Reactor spin-up | `reactor_spinup` | Rising whir | Long channel |
| Reactor online | `reactor_online` | Deep thump + harmonic | Major system online |
| Reactor heat | `reactor_heat` | Soft steam hiss | Room hazard |
| Objective complete | `objective_complete` | Soft major blip | Progress |
| Launch requirement met | `launch_requirement` | Check blip | Checklist update |
| Launch reset | `launch_reset` | Low descending blip | Failure reason |
| Launch channel tick | `launch_tick` | Very soft tick every 10% | Optional |

### Positional Audio

Use simple positional audio where it helps.

- Drone sounds pan based on drone screen position.
- Machine sounds pan based on machine position.
- Breach in current room is center-loud.
- Breach in adjacent room is quieter and panned toward the room.
- Dropped items do not need positional audio.

Do not use complex reverb if it hurts clarity.

---

## 13. End Screens

### Success Screen

When launch completes:

1. Shuttle engines glow.
2. White flash.
3. Screen fades to success screen.

Success screen content:

```text
SHUTTLE LAUNCHED
SURVIVED UNTIL DAY X

SYSTEMS RESTORED
[✓] O2 GENERATOR
[✓] O2 RECYCLER
[✓] REACTOR ONLINE
[✓] LAUNCH COMPUTER
[✓] FUEL INSTALLED

TIME USED: 04:32 / 16:00
DRONES DISABLED: 1/2
BREACHES SEALED: 2/2
```

Style:

- Calm
- Bright but not flashy
- White/blue palette
- Small engine glow background
- No heavy celebration

---

### Failure Screen

When player dies or de-orbit occurs:

1. Screen desaturates.
2. Alarms fade.
3. Failure screen appears.

Failure screen content:

```text
STATION LOST
CAUSE: ASPHYXIA
TIME SURVIVED: 06:12

SYSTEMS RESTORED
[✓] O2 GENERATOR
[ ] REACTOR ONLINE
[✓] FUEL INSTALLED
```

Cause display:

| Cause | Icon |
|---|---|
| Asphyxia | Air icon with X |
| Drone attack | Drone triangle |
| Reactor heat | Snowflake/heat icon |
| Integrity failure | Shield with X |
| De-orbit | Downward arrow |

Style:

- Dark
- Red accent only for cause
- No blame text
- No respawn option mid-run
- Restart returns to title or restarts run from beginning

---

## 14. Cuts and Anti-Goals

These are intentionally not in the game.

| Cut Item | Logic |
|---|---|
| No 3D or 2.5D | Room boundaries and system state are clearer in flat top-down |
| No fog of war | The map is a survival tool, not exploration mystery |
| No dynamic lighting | Too expensive and can obscure state |
| No dynamic shadows | Flat readability is better |
| No parallax | Adds depth confusion |
| No exterior space | Gameplay is entirely interior |
| No animated starfield | Setting is sold with static portholes |
| No detailed character faces | Top-down survival does not need facial detail |
| No gore | Tension comes from systems, not damage spectacle |
| No decorative state colors | Prevents false warnings |
| No random visual flicker | State changes must be meaningful |
| No map zoom/rotation | Persistent map should be stable and schematic |
| No pause menu in core run | Keeps timer pressure consistent; if platform requires pause, use a minimal state-free pause screen |
| No cinematic cutscenes | Session is short and gameplay is immediate |
| No enemy variety beyond two drones | Visual clarity and gameplay fairness |
| No alternate map states | The 10 rooms are enough |
| No collectible trinkets | Reduces UI and world clutter |

---

## 15. Integration Notes

### For Engineering Agent

The engine should expose the following visual states:

```ts
type RoomState = {
  id: string;
  name: string;
  o2: number;
  hull: number;
  breached: boolean;
  powered: boolean;
  droneActive: boolean;
  objective: boolean;
  eventWarning: boolean;
  eventWarningTime?: number;
}

type PowerState = {
  source: "none" | "epc" | "cell" | "reactor" | "powered";
  timeLeft?: number;
}

type PlayerState = {
  o2: number;
  integrity: number;
  currentRoom: string;
  invulnerable: boolean;
}

type ReactorState = {
  online: boolean;
  coolant: number;
  spinningUp: boolean;
  heatHazard: boolean;
}

type LaunchState = {
  reactorOnline: boolean;
  shuttlePowered: boolean;
  computerPrimed: boolean;
  fuelInstalled: boolean;
  shuttleO2: number;
  progress: number;
}
```

HUD should update immediately when state changes.

Bars may interpolate visually, but numbers should be exact.

### Map Data

Map needs:

- Room nodes
- Door connections
- Door state
- O2 bucket
- Power bool
- Breach bool
- Drone bool
- Objective bool
- Event warning target and countdown

### Visual Update Cadence

- State icons: immediate
- HUD numbers: immediate
- Bars: smooth interpolation optional
- Particles: target 60 FPS if available, acceptable at 30 FPS
- Warning pulses: max 2 Hz
- Particle cap: 128 active particles per visible room

### Audio Event Names

Use these event names for integration:

```text
ui_select
ui_error
pickup
drop
use_o2
use_medkit
repair_start
repair_tick
repair_complete
door_open
door_close
door_jammed
door_repair
hull_patch
power_install
power_cell_expire
power_loss
o2_low
o2_critical
integrity_low
integrity_critical
breach
hull_event_warning
coolant_low
coolant_expired
reactor_spinup
reactor_online
reactor_heat
drone_activate
drone_alert
drone_attack
emp
deorbit_warning
objective_complete
launch_requirement
launch_reset
launch_success
game_over
```

### Visual QA Checklist

The integration should verify:

1. Can the player tell player O2 is low without reading the number?
2. Can the player tell room O2 is low?
3. Can the player tell a room is breached?
4. Can the player tell a room is powered?
5. Can the player tell a room is unpowered?
6. Can the player tell a drone is active?
7. Can the player tell coolant is low?
8. Can the player tell which launch requirement is missing?
9. Can the player tell which door is jammed?
10. Can the player tell what action is available?
11. Can the player tell why an action is paused or reset?
12. Can the player tell the de-orbit timer is critical?
13. Can the player identify all states with audio off?
14. Can the player identify all critical states with colorblindness?

---

## 16. Design Tokens

### Palette Tokens

```json
{
  "base": {
    "void": "#07090c",
    "floor": "#171c22",
    "wall": "#2a3138",
    "line": "#4a5560",
    "panel": "rgba(10, 14, 18, 0.82)",
    "text": "#eaf2f8",
    "text_dim": "#9aa7b5"
  },
  "state": {
    "o2": "#4fd8ff",
    "integrity": "#77f2a8",
    "power": "#ffb300",
    "breach": "#ff4d4d",
    "drone": "#ff8a00",
    "coolant": "#62a4ff",
    "objective": "#ffffff"
  }
}
```

### Room Accent Tokens

These are decorative only and must not be used for state colors.

```json
{
  "rooms": {
    "docking":     "#8ea1b3",
    "crew":        "#b8a98f",
    "storage":     "#8f7358",
    "cargo":       "#4a4f57",
    "medbay":      "#a9c2c9",
    "hydro":       "#6f9b6a",
    "engineering": "#a46a3a",
    "reactor":     "#7a2b2b",
    "bridge":      "#3f6b8a",
    "shuttle":     "#9aa7b3"
  }
}
```

### Icon List

```json
{
  "icons": [
    "air",
    "shield",
    "lightning",
    "cracked_hex",
    "drone_triangle",
    "snowflake",
    "fuel_rod",
    "objective_chevron",
    "warning_triangle",
    "check",
    "x",
    "door_open",
    "door_closed",
    "door_jammed",
    "emp",
    "wrench",
    "o2_tank",
    "medkit",
    "hull_patch",
    "power_cell",
    "coolant_cell"
  ]
}
```

### Procedural Texture Recipe

For browser generation, keep textures simple.

Base floor texture recipe:

```json
{
  "size": 256,
  "base_color": "#171c22",
  "noise": {
    "scale": 0.02,
    "contrast": 0.08
  },
  "scratches": {
    "count": 18,
    "alpha": 0.08,
    "width": 1
  },
  "panel_lines": {
    "spacing": 64,
    "color": "#20262d",
    "alpha": 0.9
  },
  "wear_stains": {
    "count": 6,
    "alpha": 0.06
  }
}
```

Wall texture recipe:

```json
{
  "size": 256,
  "base_color": "#2a3138",
  "panel_height": 96,
  "panel_gap": 4,
  "noise": {
    "scale": 0.03,
    "contrast": 0.07
  },
  "caution_stripe_probability": 0.15,
  "caution_color": "#6b6f73"
}
```

Do not generate highly detailed textures. The game should remain lightweight for browser performance.

---

## 17. Final Visual Principle

The game should feel like the player is looking at a station control problem, not a decorative sci-fi environment.

Every visual element should answer one of three questions:

1. **What is the state of this system?**
2. **What should the player do next?**
3. **What is dangerous right now?**

If an asset cannot answer one of those questions, it is decoration. Decoration is allowed, but it must stay quiet.