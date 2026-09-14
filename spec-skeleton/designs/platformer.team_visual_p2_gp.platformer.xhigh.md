# visual.md

## 0. Document Purpose and Authority

This is the complete visual, UX, presentation, and audio design for **Signal Courier**.

Another agent will integrate this game using only this file for:

- Dimensionality and presentation.
- Art style.
- UI and HUD.
- Entity appearance.
- VFX.
- World/stage visual identity.
- Music.
- Sound effects.
- Presentation UX.

If this document conflicts with `gameplay.md` on **mechanics, numbers, states, or rules**, `gameplay.md` remains authoritative.

If this document conflicts with `gameplay.md` on **appearance, readability, UI, audio, or presentation**, this document is authoritative.

Important principle:

> Visuals must make the gameplay easier to read, not decorate it into obscurity.

---

## 1. Dimensionality

The game is **2D gameplay** with **2.5D presentation**.

### 1.1 Gameplay Plane

- All gameplay occurs on a single 2D plane.
- Positive X is right.
- Positive Y is down.
- No Z-axis gameplay.
- No 3D aiming.
- No camera rotation.
- No gameplay depth.
- Collision, movement, shooting, and camera are strictly 2D.

### 1.2 Presentation Depth

The world may use **parallax background layers** to create depth, but parallax is presentation only.

Background layers do not create gameplay depth.

Parallax must not imply that the player can move into or out of the screen.

### 1.3 Logical Viewport

- Logical viewport: **960 x 540**.
- Scale to fit screen while preserving aspect ratio.
- Prefer integer or clean fractional scaling where available.
- All visual measurements in this document are in logical pixels at **960 x 540**.

### 1.4 Layer Stack

Render layers in this order:

| Layer | Content | X Parallax | Y Parallax | Notes |
|---:|---|---:|---:|---|
| 0 | Sky / gradient | 0.0 | 0.0 | Static or very slow vertical interpolation only. |
| 1 | Far silhouette | 0.12 | 0.04 | Distant pipes, spires, market frames. |
| 2 | Mid structures | 0.28 | 0.10 | Pipes, catwalks, shelves, clouds. |
| 3 | Near props | 0.55 | 0.19 | Non-interactive props, lamps, cloth, cables. |
| 4 | Gameplay layer | 1.0 | 1.0 | Tiles, player, enemies, projectiles, pickups. |
| 5 | VFX layer | 1.0 | 1.0 | Sparks, beams, particles, telegraphs. |
| 6 | HUD layer | 0.0 | 0.0 | UI, HUD, notifications. |

### 1.5 Foreground Rule

There is no gameplay-occluding foreground.

Optional screen-edge framing may exist, but:

- It may not cover more than **80 px** on any side.
- It may not cover the center of the screen.
- It may not obscure projectiles, enemies, hazards, or the player.
- It must not create fake depth.

Why:

> Any foreground object can accidentally hide a projectile or spike. The game is designed around safe, readable challenge.

---

## 2. Visual Identity

Working title:

# **SIGNAL COURIER**

Player:

# **Courier Jex**

Core visual theme:

> A dying industrial city being re-awakened by signal light.

The style is:

- **Rust-circuit industrial.**
- **Flat-shaded vector presentation.**
- **High-contrast silhouettes.**
- **Limited palette.**
- **Emissive signal accents.**
- **No photographic realism.**
- **No anime style.**
- **No heavy 3D rendering.**
- **No hand-painted clutter.**
- **No Mario-like pipes, coins, mushrooms, castles, or flagpoles.**

The world should feel like a maintenance city under emergency signal control:

- Rust.
- Steel.
- Cables.
- Maintenance drones.
- Conveyors.
- Canals.
- Floating market platforms.
- Signal beacons.
- Industrial warning shapes.

The emotional arc:

- **World 1:** cold, wet, rusty, oppressive.
- **World 2:** brighter, airy, wind-swept, but more exposed.
- **End:** the city’s signal network wakes up in coherent cyan/white light.

---

## 3. Global Color System

The palette is deliberately limited so that color always means something.

### 3.1 Core Palette

| Name | Hex | Use |
|---|---:|---|
| Void Dark | `#0B1017` | Backgrounds, shadows, UI backgrounds. |
| Deep Steel | `#1C2530` | Mid-background panels, walls. |
| Steel | `#3A4856` | Neutral structures. |
| Rust Dark | `#7A3E33` | World 1 metal, pipes. |
| Rust Light | `#B86B4F` | Rust highlights, enemy armor. |
| Oil Teal | `#2E5F5A` | World 1 canal water, wet metal. |
| Water Dark | `#153136` | Pits, canal depths. |
| Signal Cyan | `#4BE2FF` | Player, checkpoints, conduit, active UI. |
| Signal White | `#F5FBFF` | Cores, highlights, beam cores. |
| Signal Amber | `#FFB347` | Tuners, collectible accents, Sifter, warnings. |
| Danger Red | `#FF4F5A` | Enemy damage, spikes, boss, danger. |
| Warning Orange | `#FF8B3D` | Enemy projectiles, telegraphs. |
| Heart Pink | `#FF7D9B` | Signal hearts, warm pickups. |
| UI Neutral | `#D7DDE4` | Text, inactive UI. |
| UI Dark | `#303841` | Locked UI, disabled slots. |

### 3.2 Color Semantics

These meanings must be consistent across the entire game.

| Color | Meaning |
|---|---|
| Cyan | Player, safe signal, active systems, checkpoints, conduit, active UI. |
| White | Pure signal, cores, beam centers, high-value highlights. |
| Amber | Collectibles, tuners, Sifter, special weapon energy, mild warnings. |
| Red / Orange | Enemy attacks, damage, hazards, boss energy, locked objectives. |
| Neutral steel / rust | Environment. |
| Pink | Health. |

Why:

> The player should be able to identify danger, safety, and collectibles from color alone, even when shapes are small or motion is fast.

### 3.3 Contrast Rules

- Enemy projectiles must always have a **white or bright core**.
- Player projectiles must be visually distinct from enemy projectiles.
- Spikes must never match the color of the floor they sit on.
- One-way platforms must have a brighter top edge than the background.
- Boss telegraphs must be visible against both World 1 and World 2 backgrounds.
- Minimum gameplay readability brightness: background areas should not drop below roughly `#121820` behind gameplay.

Why:

> Dark industrial mood is desirable, but if a projectile can be missed because the background is too dark, the visual design has failed.

---

## 4. Typography and UI Grammar

### 4.1 Type Direction

Use a **condensed technical sans-serif** feel.

If custom fonts are not available, use a fallback stack:

```css
"Chakra Petch", "Rajdhani", "Bahnschrift", "Arial Narrow", sans-serif
```

For numbers and counters, prefer a monospace or tabular numeric feel:

```css
"JetBrains Mono", "Consolas", "Courier New", monospace
```

### 4.2 Type Sizes at 960 x 540

| Use | Size |
|---|---:|
| Title logo | 64 px |
| World label | 28 px |
| Main menu button | 24 px |
| HUD text | 16 px |
| Notification text | 18 px |
| Stage name card | 40 px |
| Small UI text | 12 px |

### 4.3 UI Shape Grammar

All UI panels use:

- 6 px corner radius.
- 2 px border.
- Dark translucent background: `#0B1017` at 82% opacity.
- Primary border: `#4BE2FF`.
- Secondary border: `#3A4856`.
- Danger border: `#FF4F5A`.
- Text: `#D7DDE4`, unless highlighted.

Buttons:

- Default: dark panel, neutral border.
- Hover: cyan border, white text, 1 px upward shift.
- Confirm: 80 ms white flash.
- Deny: red border, 0.15 s horizontal shake, low deny sound.

Why:

> A single UI grammar keeps title, map, pause, summary, and game over feeling like one coherent signal system.

---

## 5. State-by-State UX

## 5.1 Title

### Layout

- Center-left menu.
- Large logo center or upper-center.
- Animated background.
- Small footer: `Desktop mouse + keyboard`.

### Background

The title background should show the two districts:

- Left half: **Sumpworks** rust pipes, dark canal, amber lamps.
- Right half: **Skyloom** floating market, sky, cloth canopies, cyan signal.
- Center: Courier Jex silhouette standing on a small signal platform.

The background slowly parallaxes. No gameplay occurs.

### Menu Rules

No progress:

- `Begin Signal`
- `Controls`

With progress:

- `Continue`
- `New Signal`
- `Controls`

`Continue` starts the furthest unlocked uncompleted stage.

`New Signal` resets progress.

### New Signal Confirm

Before reset, show a small confirm panel:

> **Erase saved signal?**

Buttons:

- `Erase`
- `Cancel`

Why:

> Resetting all progress is irreversible. Accidental reset is a bad UX experience.

### Title Visual Motif

The logo should include a small signal wave under the text:

- Three cyan horizontal pulses.
- One white peak pulse.
- Slow 2-second loop.

---

## 5.2 Intro

The intro shows 4 short story cards.

### Visual Layout

- Black background.
- Thin cyan scanline moving vertically.
- One centered panel: 640 x 180.
- Icon on left: 64 x 64.
- Text on right: 2 lines max.
- Skip prompt bottom center:

> `Enter / Space / Click`

### Story Cards

Card 1:

- Icon: broken relay tower.
- Text: `The central relay has gone silent.`

Card 2:

- Icon: swarm of small red drones.
- Text: `The Hush swarm has locked the districts.`

Card 3:

- Icon: Courier Jex silhouette with weapon.
- Text: `Courier Jex carries the last tuned weapons.`

Card 4:

- Icon: signal map with two districts.
- Text: `Recover 10 nodes. Restore the broadcast.`

### Card Transition

- Fade out old card: 0.25 s.
- Fade in new card: 0.25 s.
- Each card can be skipped.
- No voice.
- Music is minimal narrative drone.

Why:

> The story is compact. Four cards are enough to set the premise without slowing the player down.

---

## 5.3 Signal Map

The Signal Map is world/stage selection.

### Layout

Two large panels:

- Left: **World 1: Sumpworks**
- Right: **World 2: Skyloom**

Each panel:

- Width: 420 px.
- Height: 320 px.
- Spacing: 20 px.
- Centered horizontally and vertically.

Each panel contains 5 stage nodes.

### Node Layout

Nodes are arranged in a horizontal signal chain:

```text
[1] --- [2] --- [3] --- [4] --- [5]
```

Node size: 40 x 40.

Spacing: 52 px.

### Node States

| State | Appearance |
|---|---|
| Locked | Dark grey node, red lock icon, no pulse. |
| Unlocked | Cyan outline, white center, subtle 1-second pulse. |
| Completed | Filled cyan node, small white check, brighter glow. |

The current furthest unlocked uncompleted stage pulses slightly stronger.

### World 1 Panel

- Background: rust pipes, canal, dark teal water.
- Accent: amber lamps.
- World label: `W1 · SUMPWORKE`.

### World 2 Panel

- Background: sky, floating market, cloth canopies.
- Accent: cyan signal and lantern amber.
- World label: `W2 · SKYLOOM`.

### World 2 Lock

Until World 1 Stage 5 is completed:

- World 2 panel is dimmed to 50%.
- A padlock icon appears center.
- Text: `RESTORE W1 SIGNAL`.
- Nodes are not selectable.

### Selection

Selected node:

- Cyan bracket corners.
- 2 px brighter border.
- Small signal tick sound.

Start stage:

- Confirm sound.
- Signal wipe transition into stage.

Why:

> The map should feel like a signal network being restored, not a generic level select screen.

---

## 5.4 Stage

### Stage Start

When entering a stage:

1. 0.5 s signal wipe transition.
2. Stage name card for 1.2 s:
   - World label small.
   - Stage name large.
   - Example: `W1 · N3`
   - Example: `Pressure Lock`
3. Fade out.
4. Gameplay begins.

The stage name is not shown permanently except in the HUD top-right label.

### Stage Visual Clarity

Every stage must maintain:

- Clear player silhouette.
- Clear enemy silhouettes.
- Clear hazard shapes.
- Clear objective direction.
- No background element stronger than foreground gameplay.
- No background element using enemy projectile colors.

---

## 5.5 Pause

Pause only exists during Stage state.

### Visuals

- Dim stage to 65% brightness.
- Do not use heavy blur.
- Center panel: 420 x 240.
- Title: `PAUSED`
- Buttons:
  - `Resume`
  - `Restart Stage`
  - `Signal Map`
  - `Title`

All timers, enemies, projectiles, music intensity, and VFX stop.

Pause in/out uses UI cue.

Why:

> Blur can hide layout and hurt readability when resuming. A simple dim is faster and clearer.

---

## 5.6 Stage Summary

Shown after non-final stage completion.

### Panel

- Size: 520 x 260.
- Center.
- Dark translucent background.
- Cyan border.

### Content

Top:

- Stage name.
- Stage label, e.g. `W1 · N2`.

Stats:

- `Time`
- `Deaths`
- `Cores in Stage`
- `Total Cores`

Buttons:

- `Continue`
- `Signal Map`

`Continue` proceeds to next unlocked stage.

`Signal Map` returns to map.

### Visual Feedback

- Panel slides up 12 px.
- Core total pulses once.
- Music changes to summary theme.

---

## 5.7 Game Over

Shown when lives reach 0.

### Visuals

- Background stage dims to 40%.
- Red vignette.
- Large text: `SIGNAL LOST`
- Subtext: `Connection failed.`

Buttons:

- `Retry Stage`
- `Signal Map`
- `Title`

### Feel

- Static signal noise.
- Low red pulse.
- No harsh punishment visuals.
- No skull, gore, or dark fantasy imagery.

Why:

> Game Over should feel like a lost transmission, not a moral failure.

---

## 5.8 End

Shown after World 2 Stage 5 completion.

### Visuals

- Bright background.
- City signal network lights up.
- Cyan/white light beams rise from both districts.
- Large text: `SIGNAL RESTORED`
- Subtext: `The broadcast is back.`

Stats:

- `Total Time`
- `Total Deaths`
- `Total Cores`

Example:

```text
Total Cores 30/30
```

Buttons:

- `Signal Map`
- `Title`

### Final Visual Beat

During the End screen:

- World 1 and World 2 icons both glow.
- A final signal pulse travels across the screen.
- Music resolves to a brighter major-key version of the title motif.

---

## 6. HUD Specification

The HUD must be minimal, readable, and non-intrusive.

All HUD is rendered at 960 x 540.

---

## 6.1 Top Left: Health and Weapons

### Hearts

Position:

- Start at x = 16, y = 16.
- 5 heart icons.
- Icon size: 20 x 16.
- Spacing: 4 px.

Heart appearance:

- Filled: `#FF7D9B` with 1 px dark outline.
- Empty: dark outline only.
- Lost heart: pulses scale 1.2 for 0.4 s.

Why:

> Hearts are health. They should be warm and immediately distinguishable from cyan signal elements.

### Weapon Slots

Position:

- Below hearts.
- Start at x = 16, y = 44.
- 4 slots.
- Slot size: 36 x 28.
- Spacing: 6 px.

Slot content:

- Small number top-left: 10 px.
- Weapon icon center: 16 x 16.

States:

| State | Appearance |
|---|---|
| Locked | Grey background, grey icon, diagonal slash. |
| Unlocked inactive | Neutral border, white icon. |
| Active | Cyan border, cyan glow, brighter icon. |
| Deny | Red border flash + 0.15 s horizontal shake. |

Weapon icons:

| Weapon | Icon |
|---|---|
| Chirp | Single small dart. |
| Sifter | Three small pellets in a fan. |
| Lance | Long horizontal line. |
| Bloom | Three curved shards from center. |

Why:

> The player needs to identify weapons at a glance, even while aiming.

---

## 6.2 Top Right: Stage and Cores

Position:

- Right aligned at x = 944.

Content:

- Stage label:
  - Example: `W1 · N3`
  - Size: 16 px.
- Core counter:
  - Example: `Cores 12/30`
  - Size: 16 px.
  - Small core icon before text.
- Pause icon:
  - 24 x 24.
  - Two vertical bars.
  - Bottom-right area of top-right cluster.

Core counter feedback:

- When a core is collected:
  - Number flashes white for 0.4 s.
  - Small cyan burst at HUD counter.
  - No bottom-center text notification.

Why:

> A core pickup is optional and frequent. A text popup would clutter the notification area.

---

## 6.3 Top Center: Boss HUD

Shown only during boss fights.

### Boss Name

- Center.
- Size: 20 px.
- Color: white.
- Example: `HUSH WARDEN`
- Example: `NULL RELAY`

### Boss Health Bar

- Width: 480 px.
- Height: 12 px.
- Position: below name.
- Border: 1 px `#D7DDE4`.
- Background: `#1C2530`.
- Fill:
  - Hush Warden: `#FF4F5A`.
  - Null Relay: phase-colored:
    - Phase 1: `#9F7BFF`
    - Phase 2: `#FF6BD6`
    - Phase 3: `#FFFFFF`

### Boss Phase Warning

When a phase begins:

- Text appears below boss bar:
  - `PHASE 2`
  - `OVERLOAD`
- Size: 24 px.
- Color: white with red outline.
- Hold: 1.2 s.
- Fade: 0.3 s.

Why:

> Boss phase changes are major gameplay events. The player must not miss them.

---

## 6.4 Bottom Center: Notifications

Position:

- Center.
- y = 494.
- Width: 560 px.
- Height: 28 px.

Appearance:

- Dark translucent panel.
- Cyan text.
- Slide up 0.2 s.
- Hold 1.2 s.
- Fade out 0.3 s.

Notification priority:

1. Weapon unlock.
2. Boss phase warning.
3. Checkpoint.
4. Generic stage message.

Examples:

```text
CHECKPOINT
TUNER: SIFTER
PHASE 2
CONDUIT READY
```

Do not use notifications for:

- Core collection.
- Every heartbeat.
- Weapon switch.
- Regular enemy deaths.

Why:

> The notification area is for important, time-sensitive information.

---

## 6.5 Edge Objective Arrow

When the current objective is off-screen:

- Show a small chevron at the screen edge.
- Size: 16 px.
- Color: cyan.
- Pulse: 0.5 s.

Objective target:

- Non-boss stages: Conduit.
- Boss stages before boss death: Boss.
- Boss stages after boss death: Conduit.

Why:

> During a boss stage, the Conduit is locked. Pointing to a locked exit would be confusing.

The arrow must not cover:

- Player.
- Enemy projectiles.
- Boss telegraphs.
- Center screen.

---

## 6.6 First Stage Control Hint

Stage 1-1 only.

Bottom text:

```text
A/D move    W jump    S crouch    Mouse shoot
```

Behavior:

- Visible for 10 seconds or until first successful jump.
- Fade out 0.5 s.
- Font: 16 px.
- Color: `#D7DDE4`.
- Background: none.

Why:

> The first stage is the tutorial. A brief reminder reduces mouse-aim confusion.

---

## 6.7 Damage Feedback

When the player takes damage:

1. Red vignette flash:
   - Color: `#FF4F5A`.
   - Alpha: 0.35.
   - Duration: 0.3 s.
2. Player sprite flickers during invulnerability:
   - Alpha alternates 0.35 / 0.9.
   - Flicker rate: 0.08 s on / 0.08 s off.
3. Lost heart pulses:
   - Scale 1.2.
   - Duration: 0.4 s.
4. Player hurt SFX.

No full-screen red flash beyond vignette.

Why:

> The player must know they were hit, but the screen must remain readable.

---

## 7. Cursor and Aiming UX

Mouse aiming is primary.

### Crosshair

Hide the OS cursor during Stage state.

Show a custom crosshair:

- Size: 12 px.
- Color: `#4BE2FF`.
- Center dot: 2 px.
- Four short lines, 4 px long.
- 1 px line width.

On mouse move:

- Crosshair follows mouse.

On shoot:

- Crosshair expands to 14 px for 0.05 s.

If mouse leaves window:

- Crosshair dims to 50%.
- Aim remains last known mouse position.
- Shooting stops.

### Keyboard Fallback

If mouse aiming is unavailable:

- Crosshair is hidden.
- Shooting uses facing direction.
- Show a small facing indicator:
  - 8 px cyan arrow.
  - Positioned 16 px from player center in facing direction.
  - Visible only while keyboard fallback is active.

Why:

> Keyboard-only players need to know which direction they are shooting.

---

## 8. Player Visuals

Player name:

# **Courier Jex**

### 8.1 Silhouette

Courier Jex is a compact courier:

- Hooded upper body.
- Small mask or visor.
- Signal backpack.
- Slightly bulky chest panel.
- Narrow legs.
- Compact weapon arm.

Silhouette must read as a lone human courier, not a knight, robot, or cartoon hero.

### 8.2 Player Colors

| Part | Color |
|---|---|
| Suit | `#2A323C` |
| Suit shadow | `#171D24` |
| Hood edge | `#3A4856` |
| Visor | `#4BE2FF` |
| Backpack | `#3A4856` |
| Signal belt | `#FFB347` |
| Boots | `#1C2530` |

The cyan visor is the main identity point.

Why:

> A bright cyan visor makes the player readable against dark industrial backgrounds and distinguishes them from rust-colored enemies.

### 8.3 Sprite Size

Hitboxes are from `gameplay.md`.

Visual sprites may be slightly larger than hitboxes for readability.

| State | Hitbox | Visual Sprite |
|---|---:|---:|
| Standing | 16 x 24 | 32 x 40 |
| Crouching | 16 x 12 | 32 x 28 |

Origin:

- Center bottom.

Facing:

- Flip sprite horizontally.
- Visual facing follows mouse X or last horizontal input.

### 8.4 Player Animations

| Animation | Frames | Duration | Notes |
|---|---:|---:|---|
| Idle | 4 | 1.2 s | Slight breathing. |
| Run | 6 | 0.45 s | Compact courier stride. |
| Jump | 3 | one-time | Knees tuck. |
| Fall | 2 | one-time | Arms back. |
| Crouch | 4 | 0.2 s | Body compresses 65% height. |
| Crouch Run | 4 | 0.5 s | Low shuffling. |
| Shoot | 2 | 0.15 s | Weapon recoil. |
| Hurt | 2 | 0.2 s | Body tilts back. |
| Death | 6 | 0.5 s | No blood. Signal shatter. |

Death visual:

- Player breaks into cyan/white signal shards.
- Small rust shards.
- No gore.
- No lingering corpse.
- Death lasts 0.5 s, then respawn or game over.

Why:

> The player should disappear as a burst of signal, matching the courier/signal theme.

### 8.5 Crouch Visual

When crouching:

- Sprite compresses vertically.
- Visor remains visible.
- Weapon lowers.
- Muzzle origin visually matches gameplay crouch offset.
- Hitbox is smaller, but sprite may still show some head height for readability.

The crouch state should be obvious.

---

## 9. Weapon Visuals

Weapons are visible extensions of the player arm.

They do not change hitbox.

They should be readable at small size.

---

## 9.1 Chirp

Role: fast default weapon.

Visual:

- Compact pistol.
- Dark steel body.
- Cyan energy tip.
- Small side vent.

Muzzle flash:

- Small 1-frame cyan star.
- 6 px radius.
- Duration: 0.05 s.

Weapon color accent:

- Cyan.

Why:

> Chirp is the baseline tool. It should look simple and reliable.

---

## 9.2 Sifter

Role: close-range spread.

Visual:

- Boxier shotgun-like device.
- Three front vents.
- Amber energy chamber.

Muzzle flash:

- Three small puffs.
- One white center puff.
- Two amber side puffs.
- Duration: 0.06 s.

Weapon color accent:

- Amber.

Why:

> Sifter is about controlled spray. The three vents visually explain the spread.

---

## 9.3 Lance

Role: piercing single-target weapon.

Visual:

- Long rail.
- Narrow body.
- White core line running through the barrel.
- Cyan edge glow.

Muzzle flash:

- Elongated white/cyan line.
- 16 px long.
- Duration: 0.08 s.

Weapon color accent:

- White/cyan.

Why:

> Lance should look like it fires something sharp and straight.

---

## 9.4 Bloom

Role: splitting area weapon.

Visual:

- Bulky emitter.
- Round drum.
- Amber core.
- Three small arc vents around the front.

Muzzle flash:

- Round amber ring.
- 10 px radius.
- Duration: 0.1 s.

Weapon color accent:

- Amber/white.

Why:

> Bloom is heavy and spatial. The round drum and arc vents suggest area control.

---

## 9.5 Weapon Switching Visual

When switching weapons:

- Old weapon fades out over 0.05 s.
- New weapon slides in over 0.07 s.
- Small white spark at the player’s hand.
- No gameplay effect beyond cooldown defined by `gameplay.md`.

When locked weapon is selected:

- Slot shakes.
- Red deny flash.
- Weapon does not change.
- Deny SFX.

---

## 10. Projectile Visuals

Projectiles must be extremely readable.

### 10.1 Player Projectiles

Player projectiles are cool-toned:

- Cyan.
- White.
- Light amber only for Bloom.

All player projectiles have a bright white core.

#### Chirp Projectile

- Hitbox radius: 4 px.
- Visual: 8 px long dart.
- Color: cyan outer, white core.
- Trail: 2 fading segments.
- Lifetime visual: trail fades over 0.15 s.

#### Sifter Pellet

- Hitbox radius: 3 px.
- Visual: 6 px round pellet.
- Color: cyan outer, white core.
- Trail: 1 short segment.
- Spread visually matches -8°, -4°, 0°, +4°, +8°.

#### Lance Projectile

- Hitbox radius: 5 px.
- Visual: 20 px long beam bolt.
- Color: white core, cyan outer.
- Trail: 3 segments.
- Pierce indicator:
  - First hit: small white ripple.
  - Second hit: brighter ripple.
  - Third hit: final rupture.

#### Bloom Main Projectile

- Hitbox radius: 8 px.
- Visual: 16 px round orb.
- Color: amber outer, white core.
- Slight pulse: 0.25 s.
- Trail: soft amber glow.

#### Bloom Shard

- Hitbox radius: 4 px.
- Visual: 8 px shard.
- Color: amber outer, white core.
- Trail: 1 segment.
- Angle visually matches -25°, 0°, +25° from main direction.

---

### 10.2 Enemy Projectiles

Enemy projectiles are warm-toned:

- Red.
- Orange.
- Violet for final boss special shots.

All enemy projectiles must have a white or pale core to remain visible.

#### Dredge Drone Projectile

- Visual: 12 px round orb.
- Color: red outer, white core.
- Slow pulse: 0.3 s.
- Small smoke trail.

#### Warden Sentry Projectile

- Visual: 12 px rectangular bolt.
- Color: orange outer, white core.
- Short rectangular trail.

#### Bolt Golem Heavy Bolt

- Visual: 20 px round orb.
- Color: dark red outer, white core.
- Outer ring: 1 px.
- Heavy thump visual scale:
  - 1.0 → 1.15 → 1.0 over 0.2 s.

#### Boss Rain Projectile

- Visual: 12 x 24 vertical shard.
- Color: red outer, white core.
- Falls downward.
- Small impact splash.

#### Boss Echo Shot

- Visual: 12 x 18 bolt.
- Color: violet outer, white core.
- Bounce effect:
  - Small violet spark at wall.
  - Slight squash on impact.

#### Boss Beam

Visual:

- Telegraph: dashed red/orange line.
- Active beam: solid red with white core.
- Beam height matches gameplay width: 24 px.
- Edge caps: bright orange.

Why:

> Beams are high-damage. They need a distinct telegraph shape and color separate from small projectiles.

---

## 11. Enemy Visuals and Telegraphs

All enemies must have:

- Clear idle silhouette.
- Clear attack telegraph.
- Clear hit feedback.
- Clear death effect.
- Distinct shape from player.

General hit feedback:

- White flash: 0.05 s.
- Small spark at impact point.
- Knockback visual squash or stretch.

---

## 11.1 Mite Crawler

Type: small ground swarm.

Visual:

- Small rust bug.
- Four legs.
- Red eye.
- 16 x 16 hitbox.
- Visual sprite: 24 x 24.

Palette:

- Rust dark.
- Rust light.
- Red eye.

Animation:

- Crawl: 4 frames, 0.5 s loop.
- Blocked: 0.5 s wait, antennae twitch.
- Hit: squash.
- Death: 4 rust shards.

Why:

> Mites are small and numerous. They need a simple bug silhouette and quick death.

---

## 11.2 Dredge Drone

Type: flying shooter.

Visual:

- Small maintenance drone.
- Single red eye.
- Two side thrusters.
- 24 x 20 hitbox.
- Visual sprite: 32 x 28.

Palette:

- Steel.
- Rust light.
- Red eye.
- Amber thruster glow.

Animation:

- Hover: 4 frames, 0.8 s loop.
- Fire telegraph:
  - Eye brightens for 0.15 s before projectile spawn.
  - Thrusters flash amber.
- Fire:
  - Small recoil.
  - Red projectile.
- Death:
  - Smoke puff.
  - Small red flash.
  - Drone body splits.

Why:

> Drones are aerial threats. The eye brightening gives a readable prefire cue.

---

## 11.3 Pincer Bot

Type: melee charger.

Visual:

- Low armored walker.
- Two front pincers.
- Red core between pincers.
- 24 x 24 hitbox.
- Visual sprite: 32 x 32.

Palette:

- Rust dark.
- Steel.
- Red core.

States:

| State | Visual |
|---|---|
| Idle | Slow walk, pincers closed. |
| Telegraph | Pincers open, red core brightens, body shakes 2 px. |
| Charge | Body stretches forward, red trail. |
| Cooldown | Pincers lower, core dims. |

Telegraph:

- Duration: 0.5 s.
- Shake: 2 px horizontal.
- Pincers open.
- Red glow intensifies.

Charge:

- Body stretches 1.2x horizontally.
- Red trail: 3 fading frames.
- Stops with small impact puff.

Why:

> The charge must be readable early enough to dodge by jump or crouch.

---

## 11.4 Warden Sentry

Type: stationary aimed turret.

Visual:

- Wall or floor turret.
- Rotating head.
- Thick barrel.
- Red target light.
- 32 x 32 hitbox.
- Visual sprite: 40 x 40.

Palette:

- Steel.
- Rust.
- Red target light.
- Orange muzzle.

Animation:

- Idle: slow scan.
- Aim: head rotates toward player.
- Fire:
  - Muzzle flash.
  - Barrel recoil.
  - Two-shot burst.
- Death:
  - Head drops.
  - Smoke.
  - Power-down light.

Why:

> The barrel angle communicates target direction. The red target light shows active threat.

---

## 11.5 Mist Wraith

Type: flying phasing enemy.

Visual:

- Ghost-like signal creature.
- Tattered lower body.
- Pale cyan/white form.
- Dark hollow center.
- 24 x 24 hitbox.
- Visual sprite: 32 x 32.

Palette:

- Signal cyan.
- Signal white.
- Dark void center.

Phased visual:

- Alpha drops to 0.25.
- Outline becomes dashed.
- Small ripple appears at phase start and end.
- Player projectiles pass through with a faint distortion.
- No player damage while phased.

Why:

> Phasing must be visually unmistakable. The dashed outline and low alpha communicate intangibility.

---

## 11.6 Bolt Golem

Type: large armored enemy.

Visual:

- Large rust machine.
- Heavy arms.
- Central chest cannon.
- Thick legs.
- 48 x 48 hitbox.
- Visual sprite: 64 x 64.

Palette:

- Rust dark.
- Rust light.
- Steel.
- Red chest core.

Animations:

- Walk: 4 frames, 1.2 s loop.
- Heavy bolt telegraph:
  - Chest core glows for 0.3 s.
  - Arms raise slightly.
- Fire:
  - Large recoil.
  - Smoke puff.
- Stomp telegraph:
  - Arms raise.
  - Red ring appears on ground in front.
  - Ring size: 3 tiles diameter.
  - Duration: 0.4 s.
- Stomp:
  - Screen shake: 3 px, 0.1 s.
  - Dust puff.
  - Temporary spike patches appear.

Why:

> The golem is a heavy pressure enemy. Its telegraphs should feel large and heavy.

---

## 11.7 World 2 Enemy Variants

World 2 enemies use the same shapes but with a brighter Skyloom palette.

Changes:

- Rust replaced with pale steel.
- Red eyes remain red.
- Thruster glows are slightly brighter.
- Small sky-fin or cable detail added.
- Shadows are softer.

Why:

> The player should recognize enemy roles instantly, while World 2 still feels visually distinct.

---

## 12. Boss Visuals

Bosses are major set pieces.

They must be visually larger, more dramatic, and easier to read than normal enemies.

---

## 12.1 Hush Warden

Location: Stage 1-5.

Role: World 1 guardian.

### Base Appearance

- Large maintenance warden.
- Rust armor.
- Single red optic.
- Four heavy arms.
- 64 x 64 hitbox.
- Visual sprite: 80 x 80.

Palette:

- Rust dark.
- Rust light.
- Steel.
- Red optic.
- Orange warning lights.

Phase 1:

- Red optic dim.
- Armor intact.
- Movement heavy.

Phase 2:

- Red optic brighter.
- Armor cracks reveal orange core.
- Slight red glow around body.

### Attacks

#### Charge

Telegraph:

- 0.6 s.
- Boss crouches.
- Red line appears from boss toward player direction.
- Red chevrons pulse along the path.

Action:

- Boss dashes.
- Red trail.
- Spike patches appear along path.
- Spike patches have red tips.

#### Fan Bolt

- Three red bolts.
- Muzzle flash from chest.
- Bolts match Dredge Drone projectile style but larger.

#### Sweep Beam

Phase 2 only.

Telegraph:

- 0.8 s.
- Dashed red line appears at boss/player Y.
- Height: 24 px.
- Edge arrows appear at arena boundaries.

Beam:

- Solid red beam.
- White core line.
- Orange edge glow.
- Lasts 0.7 s.

#### Drone Summon

Phase 2 only.

- Red ring appears at boss.
- Two Dredge Drones fade in over 0.4 s.
- Small smoke puff.

#### Death

2-second sequence:

1. Boss stops.
2. Optic flickers.
3. Red light turns off.
4. Armor panels fall.
5. White signal burst.
6. Conduit activates.

---

## 12.2 Null Relay

Location: Stage 2-5.

Role: final boss.

### Base Appearance

- Abstract central relay.
- Rotating geometric rings.
- Central core.
- No human face.
- Should feel like a corrupted city relay, not a monster.
- 80 x 80 hitbox.
- Visual sprite: 96 x 96.

Palette by phase:

| Phase | Core | Rings |
|---|---|---|
| 1 | Violet | Cyan |
| 2 | Magenta | Violet |
| 3 | White | Red |

### Attacks

#### Rain

- Three vertical columns.
- Telegraph:
  - 0.3 s red dashed vertical lines.
- Projectiles:
  - Red vertical shards.
  - White core.
- Impact:
  - Small dust or water splash.

#### Side Sweep

Telegraph:

- 0.8 s.
- Dashed horizontal line.
- Red/orange.
- Edge arrows.

Beam:

- Horizontal beam.
- 24 px height.
- Red outer, white core.

#### Echo Shot

- Three violet bolts.
- Each bolt bounces once.
- Bounce visual:
  - Violet spark.
  - Slight squash.
  - Short trail.

#### Wraith Summon

- Purple ring.
- Two Mist Wraiths fade in.
- Similar to Hush Warden summon but violet.

#### Overload Cycle

Phase 3.

Sequence:

1. Horizontal beam:
   - Telegraph 0.6 s.
   - Active 0.6 s.
2. Vertical beam:
   - Telegraph 0.6 s.
   - Active 0.6 s.
3. Core Exposed:
   - Boss becomes stationary.
   - Core turns bright white.
   - Ring of white light pulses.
   - Visual damage multiplier cue:
     - Player projectiles hitting core produce extra white ripple.
     - Boss bar pulses white.

Why:

> The player must understand that Core Exposed is a reward window, so the visual language must become brighter and more inviting.

#### Death

3-second sequence:

1. Boss stops.
2. Rings slow.
3. Core flashes white.
4. Rings collapse inward.
5. Large white burst.
6. Background city lights begin to restore.
7. Conduit activates.

---

## 13. Stage Objects and Hazard Grammar

All stage objects must follow the same visual grammar.

| Object | Visual Meaning |
|---|---|
| Spike | Immediate damage. Red tip. |
| Conveyor | Movement aid. Animated arrows. |
| One-way platform | Safe floor from below. Cyan top edge. |
| Moving platform | Temporary floor. Rust slab, cyan edge. |
| Wind zone | Invisible-ish force, but visually shown. |
| Checkpoint | Safe respawn. Beacon. |
| Core | Optional signal collectible. |
| Signal Heart | Health. |
| Tuner Shard | Weapon unlock. |
| Conduit | Stage exit. |

---

## 13.1 Spikes

Size: 32 x 16.

Appearance:

- Rust base.
- Red tips.
- 1 px dark outline.
- Slight bevel.

Feedback:

- On player contact: red vignette and hurt SFX.
- Spike does not animate except small warning pulse when boss leaves spike patches.

Temporary spike patches:

- Appear with 0.2 s warning:
  - Red outline.
  - Then solid spikes pop out.
- Last duration matches gameplay.
- Disappear with small rust dust.

Why:

> Spikes are instant damage. The red tip must be visible from a distance.

---

## 13.2 Conveyor Tiles

Size: 32 x 32.

Appearance:

- Steel surface.
- Animated arrows on top.
- Arrow color: cyan.
- Arrow direction matches conveyor direction.

Animation:

- 4-frame arrow loop.
- Speed: 0.4 s loop.
- Right conveyor: arrows point right.
- Left conveyor: arrows point left.

Why:

> Cyan arrows communicate movement without using red, which means danger.

---

## 13.3 One-Way Platforms

Size: 32 x 8.

Appearance:

- Dark slab.
- Top edge: 2 px cyan.
- No side thickness.
- Slight transparent underside.

Behavior visual:

- Player can jump through from below.
- No visual change when jumping through.
- Landing: small dust puff.

Why:

> The cyan top edge tells the player this is a floor only from below.

---

## 13.4 Moving Platforms

Size: usually 64 x 16, but visual size may follow stage definition.

Appearance:

- Rust slab.
- Cyan edge lights.
- Small warning stripes on front edge.
- Edge lights pulse when platform moves.

Why:

> Moving platforms are safe but temporary. The cyan edges make them readable against pits.

---

## 13.5 Wind Zones

Wind zones must be visible.

### Updraft

Visual:

- Vertical cyan streaks.
- Small dust particles moving upward.
- Alpha: 0.25.
- Particle speed: roughly 160 px/s upward.
- Edges: soft fade, not hard lines.

Why:

> Updraft is a movement aid, not damage. Cyan communicates safety.

### Horizontal Gust Right

Visual:

- Rightward streaks.
- Small arrows.
- Alpha: 0.2.
- Particles move right.

### Horizontal Gust Left

Visual:

- Leftward streaks.
- Small arrows.
- Alpha: 0.2.
- Particles move left.

### Strong Wind

For World 2 strong wind:

- More particles.
- Faster streaks.
- Slight camera-independent background sway:
  - Nearby props sway 2 px.
  - No gameplay effect beyond defined acceleration.

Why:

> Wind affects movement strongly, so it must be obvious before the player is pushed.

---

## 13.6 Checkpoint

Size: 32 x 48.

Appearance:

- Beacon pillar.
- Inactive: dark grey, red light.
- Active: cyan light, soft glow.

Activation:

- 0.5 s cyan beam rises.
- Ring expands.
- Small positive chime.
- HUD notification: `CHECKPOINT`
- If below max health, restore 1 heart:
  - Heart icon pulses.
  - Small pink spark.

Why:

> Checkpoints are relief. Their visual should feel safe and clean.

---

## 13.7 Core

Size: 24 x 24.

Appearance:

- Rotating diamond.
- White core.
- Cyan outer glow.
- 8-frame spin.
- Spin duration: 1.0 s.

Collection:

- 6 small cyan/white particles.
- HUD counter flashes.
- Bright pickup sound.
- No bottom-center text.

Already collected:

- Not spawned on stage load or retry.

Why:

> Cores are optional signal fragments. White/cyan makes them feel valuable but not hostile.

---

## 13.8 Signal Heart

Size: 24 x 24.

Appearance:

- Pink heart.
- 1 px dark outline.
- Pulse: 0.8 s.
- Soft warm glow.

Collection:

- Only if player hearts below 5.
- Small pink burst.
- Heart HUD pulses.
- Warm pickup sound.

If player is full:

- Heart remains in world.
- No sparkle.
- No pickup sound.

Why:

> Hearts are health. They should feel warm and comforting, unlike cold enemy projectiles.

---

## 13.9 Tuner Shard

Size: 32 x 48.

Appearance:

- Amber crystal.
- Weapon icon etched on surface.
- 6-frame shimmer.
- Slight floating bob.

Collection:

- Amber/white burst.
- Unlock beam travels from pickup to HUD weapon slot.
- Weapon slot flashes cyan.
- Notification:
  - `TUNER: SIFTER`
  - `TUNER: LANCE`
  - `TUNER: BLOOM`
- Major unlock SFX.

Already collected:

- Not spawned on stage load or retry.

Why:

> Weapon unlocks are major progression moments. The visual should connect the shard to the HUD slot.

---

## 13.10 Conduit

Size: 64 x 96.

Role: stage exit.

### Inactive / Locked

- Dark grey tower.
- Red lock icon.
- Red ring at base.
- Slow red pulse: 1.0 s.

### Active Non-Boss

- Cyan spiral.
- White core.
- Fast cyan pulse: 0.5 s.

### Boss Stage

Before boss death:

- Locked red.
- Boss is the objective.

After boss death:

- Turns cyan.
- Notification: `CONDUIT READY`
- Activation available.

### Activation

When player overlaps active conduit:

- Tower flashes white.
- 0.5 s signal burst.
- Screen fades to summary or end.
- Stage complete SFX.

Why:

> The Conduit is the stage objective. Its state must be clear from a distance.

---

## 14. World Art Direction

The two worlds must feel distinct but part of the same game.

They share:

- Same UI.
- Same font.
- Same hazard colors.
- Same signal cyan/amber/red grammar.
- Same sprite style.
- Same projectile readability.

They differ in:

- Palette.
- Backgrounds.
- Environmental props.
- Lighting.
- Mood.
- Music.

---

## 14.1 World 1: Sumpworks

Theme:

- Lower industrial canal.
- Rust.
- Pipes.
- Low ceilings.
- Conveyors.
- Pits.
- Turrets.

### Visual Mood

- Cold.
- Wet.
- Oppressive.
- Industrial.
- Slightly dangerous but readable.

### Palette Emphasis

- Void dark.
- Deep steel.
- Rust.
- Oil teal.
- Amber lamps.
- Signal cyan for safe systems.

### Background Layers

Far:

- Distant bridge silhouettes.
- Broken relay towers.
- Dark sky.

Mid:

- Pipes.
- Catwalks.
- Drain grates.
- Cables.

Near:

- Rust panels.
- Warning stripes.
- Dripping pipes.
- Canal water edges.

### Environment Details

- Water in pits:
  - Dark teal.
  - Small foam ripples.
  - No death animation beyond splash and hurt.
- Low ceilings:
  - Exposed pipes.
  - Amber warning lights.
  - Cables.
- Conveyor areas:
  - Animated arrows.
  - Dust particles moving with belt.
- Sentry alcoves:
  - Small red target lights.
  - Steel frames.

### World 1 Stage Visual Notes

These are presentation notes only, not level design.

| Stage | Visual Focus |
|---|---|
| 1-1 First Current | Brighter, cleaner, clear tutorial silhouettes. |
| 1-2 Dredge Run | More moving platforms, conveyor belts, water below. |
| 1-3 Pressure Lock | Vertical shafts, pistons, steel pressure doors. |
| 1-4 Rust Gallery | Long low ceiling, gallery lights, rusted catwalks. |
| 1-5 Hush Warden | Dark boss arena, red beacon lighting, side ledges. |

Why:

> World 1 should teach the player through readable industrial spaces.

---

## 14.2 World 2: Skyloom

Theme:

- Floating market.
- Vertical platforms.
- Wind currents.
- Wide gaps.
- Open sightlines.
- More aggressive enemy patterns.

### Visual Mood

- Airy.
- Exposed.
- Brighter.
- Wind-swept.
- More open than World 1.

### Palette Emphasis

- Sky blue.
- Pale steel.
- Lavender.
- Signal cyan.
- Lantern amber.
- Danger red remains consistent.

### Background Layers

Far:

- Sky gradient.
- Distant spires.
- Small floating islands.
- Slow clouds.

Mid:

- Market stalls.
- Cloth canopies.
- Ropes.
- Lanterns.
- Hanging cables.

Near:

- Light cloth edges.
- Small lamps.
- Wind-rippled banners.

### Environment Details

- Pits:
  - Show sky below, not water.
  - Distant clouds.
  - Small floating debris.
- One-way shelves:
  - Market stalls.
  - Cloth-topped platforms.
  - Cyan top edge remains.
- Updraft columns:
  - Stronger cyan particles.
  - Small cloth scraps rising.
- Wind gusts:
  - More streaks.
  - Banners ripple.
  - Dust particles move with wind.

### World 2 Stage Visual Notes

| Stage | Visual Focus |
|---|---|
| 2-1 Lifted Bazaar | Vertical market shelves, updraft, cloth. |
| 2-2 Market Veils | Hanging veils, lanterns, shelf loops. |
| 2-3 Windrace | Strong wind streaks, open gaps, golem chamber. |
| 2-4 Highspire Ascent | Tall sky ledges, crosswind, narrow platforms. |
| 2-5 Null Relay | Final relay arena, bright core, abstract geometry. |

Why:

> World 2 should feel like the city has opened upward. The danger is still present, but the space is more vertical and exposed.

---

## 15. VFX and Readability Rules

### 15.1 General VFX Principles

- VFX must never hide hazards.
- VFX must never change hitboxes.
- VFX must not create false damage cues.
- Player VFX should be brief.
- Enemy telegraphs must be long enough to read.
- Boss telegraphs must be the most prominent visual elements.

### 15.2 Hit Sparks

Player projectile hits enemy:

- 3 small particles.
- White/cyan for player weapons.
- Duration: 0.1 s.
- Size: 2-4 px.

Enemy projectile hits player:

- 4 small particles.
- Red/orange.
- Duration: 0.15 s.

### 15.3 Enemy Death Effects

| Enemy | Death Effect |
|---|---|
| Mite Crawler | 4 rust shards. |
| Dredge Drone | Smoke puff + small red flash. |
| Pincer Bot | Metallic clank + 4 rust/steel shards. |
| Warden Sentry | Head drops + power-down spark. |
| Mist Wraith | Phasing ripple + cyan dust. |
| Bolt Golem | Low explosion + 6 rust shards + dust. |
| Boss | Large multi-stage signal burst. |

Why:

> Each enemy should have a distinct death so the player understands what they destroyed.

### 15.4 Beam Telegraphs

All beams use:

- Dashed line before activation.
- Edge arrows.
- Hold time.
- Solid beam after telegraph.

Dashed line:

- 4 dashes.
- Dash length: 12 px.
- Gap: 8 px.
- Color: red/orange.
- Alpha: 0.6.

Active beam:

- Solid core.
- White center.
- Red/orange outer.
- Edge caps bright.

Why:

> Beams are lethal and horizontal/vertical. The player needs a consistent pre-beam warning shape.

### 15.5 Screen Shake

Screen shake is used sparingly.

| Event | Shake | Duration |
|---|---:|---:|
| Player hurt | 2 px | 0.08 s |
| Bolt Golem stomp | 3 px | 0.10 s |
| Boss charge impact | 3 px | 0.10 s |
| Boss death | 4 px | 0.15 s |

No shake for:

- Regular enemy deaths.
- Core pickup.
- Checkpoint.
- Weapon switch.
- Regular shooting.

Why:

> Shake is feedback, not constant noise.

### 15.6 Damage Vignette

- Red vignette on player damage.
- No permanent vignette.
- No low-health visual effect unless explicitly added later.

Why:

> Keep damage feedback immediate and clean.

---

## 16. Audio and Music Design

Audio identity:

> Industrial signal. Clean synth pulses, metallic percussion, analog beeps, soft wind, and short procedural cues.

The music should feel like a city trying to reboot.

No voice acting.

No sampled heavy metal.

No orchestral fantasy.

No lo-fi bedroom pop.

The sound should be tight, modern, and readable.

---

## 16.1 Music Identity

### Core Instruments

- Soft analog pads.
- Short square-wave beeps.
- Metallic percussion.
- Filtered noise for wind.
- Simple bass pulses.
- Occasional high sine signal melody.

### Musical Feel

- Sparse but rhythmic.
- Repetitive motifs.
- Melody is short and memorable.
- Percussion enters gradually in harder stages.
- Boss music is more driving.
- End music resolves to a brighter major motif.

---

## 16.2 Music Map

| State / Zone | Key | BPM | Style |
|---|---:|---:|---|
| Title | D minor | 72 | Slow signal pulse, sparse pads. |
| Intro | D minor | 68 | Minimal drone, narrative beeps. |
| Signal Map | D major | 96 | Bright, clean, optimistic. |
| World 1 Stages 1-4 | D minor | 104 | Rust industrial, medium pulse. |
| World 1 Boss | E minor | 120 | Heavy drive, red pulse. |
| World 2 Stages 1-4 | F major | 112 | Airy pads, faster metallic percussion. |
| World 2 Boss | C minor | 126 | Layered tension, phase-driven. |
| Stage Summary | D major | 100 | Short resolution motif. |
| Game Over | C minor | 60 | Low signal loss. |
| End | D major | 96 | Full bright resolution. |

### World 1 Music

- Low bass.
- Metallic clanks.
- Drip sounds.
- Conveyor-like rhythmic pulses.
- Amber warning beeps.
- Mood: industrial, damp, determined.

### World 2 Music

- Higher synth pads.
- Wind noise.
- Lighter percussion.
- More open stereo space.
- Occasional high signal melody.
- Mood: exposed, fast, brighter but dangerous.

### Boss Music

Hush Warden:

- Phase 1: heavy pulse.
- Phase 2: adds high metallic arp and faster percussion.

Null Relay:

- Phase 1: violet/cyan tension, layered pads.
- Phase 2: adds urgent pulse.
- Phase 3: strips back to strong bass and warning beeps during Core Exposed.

Why:

> Phase changes should be felt musically, not just visually.

### Music Transitions

- Crossfade: 0.5 s.
- Stage start sting: 0.6 s.
- Boss start: music intensity rises.
- Boss death: music cuts, then resolution cue.
- Pause: music stops or ducks to 20%.
- Resume: 0.2 s fade in.

---

## 16.3 SFX Design

All SFX should be short and distinct.

General rules:

- Player SFX are bright and clean.
- Enemy SFX are harsher.
- UI SFX are short and digital.
- Pickups are positive.
- Damage is urgent but not painful.
- No SFX should be longer than 0.8 s except boss death and stage complete.

### SFX Table

| Event | Sound Design | Duration | Notes |
|---|---|---:|---|
| Title confirm | Short high beep | 0.08 s | Clean UI. |
| UI hover | Very soft tick | 0.03 s | Subtle. |
| UI deny | Low buzz | 0.12 s | Used for locked weapon, invalid input. |
| Pause in | Soft down blip | 0.08 s |  |
| Pause out | Soft up blip | 0.08 s |  |
| Stage start sting | Two-note world motif | 0.6 s | World 1 lower, World 2 higher. |
| Player jump | Quick upward sine | 0.06 s | 300 Hz to 600 Hz. |
| Player land | Soft thud | 0.08 s | Lowpassed. |
| Chirp fire | Fast square pop | 0.05 s | 900 Hz. |
| Sifter fire | Short micro-spread | 0.08 s | 3 tiny pops. |
| Lance fire | Deeper piercing sweep | 0.12 s | 1200 Hz down to 200 Hz. |
| Bloom fire | Heavy low pulse | 0.15 s | 80 Hz + filtered noise. |
| Bloom split | Small burst | 0.10 s | Bright chime. |
| Player projectile hit | Impact click | 0.05 s | Vary pitch by enemy size. |
| Player hurt | Short alarm | 0.12 s | 200 Hz square. |
| Player death | Deeper falling cue | 0.5 s | Descending sweep. |
| Checkpoint | Positive two-note | 0.3 s | Rising clean tones. |
| Core collected | Bright pickup arpeggio | 0.25 s | Three fast notes. |
| Heart collected | Warm pickup | 0.2 s | Soft thump + chime. |
| Tuner unlock | Major unlock cue | 0.6 s | Clear and important. |
| Enemy death: Mite | Small rust crunch | 0.10 s |  |
| Enemy death: Drone | Zap + servo | 0.20 s |  |
| Enemy death: Pincer | Metallic clank | 0.30 s |  |
| Enemy death: Sentry | Power-down beep | 0.30 s |  |
| Enemy death: Wraith | Phase-out sine fall | 0.40 s |  |
| Enemy death: Golem | Low boom + crack | 0.50 s |  |
| Boss warning | Warning alarm | 0.5 s | Used before major attack. |
| Boss phase change | Pitch-shift cue | 0.4 s | Phase 2: higher, Phase 3: white-noise burst. |
| Boss death | Large resolution | 0.8 s | Explosion + rising signal. |
| Conduit complete | Stage complete sweep | 0.7 s | Rising sweep, clean ending. |

### SFX Priority

If multiple SFX trigger at once, prioritize:

1. Player hurt.
2. Player death.
3. Boss warning.
4. Checkpoint.
5. Tuner unlock.
6. Core/heart pickup.
7. Enemy death.
8. Weapon fire.
9. UI.

Why:

> The player must always know if they are damaged or if a major event is happening.

---

## 16.4 Mixing Guidelines

Target for browser game:

- Music volume: 0.5.
- SFX volume: 0.7.
- UI volume: 0.8.
- Master limiter peak: -3 dB.
- Avoid clipping.
- Duck music by -6 dB during important SFX:
  - Player hurt.
  - Boss warning.
  - Stage complete.
  - Boss death.

Do not use:

- Long reverb tails.
- Harsh high-frequency spikes.
- SFX that overlap identically.
- Random noise without purpose.

Why:

> Browser audio needs to stay clean at low quality and small speakers.

---

## 17. Asset Generation Conventions

These are presentation production rules, not gameplay implementation.

### 17.1 Sprite Style

- Flat vector.
- 1 px dark outline: `#10151C`.
- 2 px shadow where needed.
- Limited palette.
- No heavy gradients.
- No bloom-based readability.
- No motion blur required.
- Use simple shapes.

### 17.2 Sprite Sizes

All sprites include padding for VFX.

| Entity | Hitbox | Visual Sprite |
|---|---:|---:|
| Player standing | 16 x 24 | 32 x 40 |
| Player crouching | 16 x 12 | 32 x 28 |
| Mite Crawler | 16 x 16 | 24 x 24 |
| Dredge Drone | 24 x 20 | 32 x 28 |
| Pincer Bot | 24 x 24 | 32 x 32 |
| Warden Sentry | 32 x 32 | 40 x 40 |
| Mist Wraith | 24 x 24 | 32 x 32 |
| Bolt Golem | 48 x 48 | 64 x 64 |
| Hush Warden | 64 x 64 | 80 x 80 |
| Null Relay | 80 x 80 | 96 x 96 |
| Core | 24 x 24 | 32 x 32 |
| Heart | 24 x 24 | 32 x 32 |
| Tuner | 32 x 48 | 40 x 56 |
| Checkpoint | 32 x 48 | 48 x 64 |
| Conduit | 64 x 96 | 96 x 128 |

### 17.3 Animation Timing

- Character animation frame rate: 12 frames/s.
- VFX frame rate: 24 frames/s.
- UI animation frame rate: 60 frames/s.
- All loops should be seamless.

### 17.4 Tile Textures

Tile size: 32 x 32.

Textures should use:

- 1 px border.
- 2-3 shades of the base material.
- Subtle 1-2 px noise.
- No fine detail smaller than 2 px.

Tile types:

- Solid floor.
- Solid wall.
- One-way platform.
- Conveyor right.
- Conveyor left.
- Spike base.
- Boss floor.
- Skyloom shelf.
- Sumpworks pipe.

Why:

> At 960 x 540, small details disappear. Larger shapes read better.

---

## 18. Important UX Decisions and Rationale

### 18.1 Why Cyan Means Safety?

Cyan is used for:

- Player.
- Checkpoints.
- Conduit.
- Active UI.
- Player projectiles.

Why:

> The player should instinctively trust cyan. It is the color of the restored signal.

### 18.2 Why Red Means Danger?

Red is used for:

- Enemy projectiles.
- Spikes.
- Boss energy.
- Locked objectives.
- Damage feedback.

Why:

> Red is the fastest visual warning. The player should recognize it before consciously reading shapes.

### 18.3 Why Amber Means Tuner and Sifter?

Amber is used for:

- Tuner shards.
- Sifter.
- Bloom energy.
- Some warning highlights.

Why:

> Amber is warm but not as aggressive as red. It feels like special signal power.

### 18.4 Why No Damage Numbers?

There are no damage numbers.

Why:

> The game has a simple heart system and clear weapon identities. Damage numbers would add clutter without improving core decision-making.

### 18.5 Why No Minimap?

There is no in-stage minimap.

Why:

> Stages are linear or mostly linear. The objective arrow and Conduit visuals are enough. A minimap would compete with HUD space.

### 18.6 Why No Core Text Notification?

Core collection updates the HUD counter but does not show a bottom-center text notification.

Why:

> Cores are optional and frequent. The notification area is reserved for checkpoints, unlocks, and boss phases.

### 18.7 Why No Heavy Screen Effects?

The game avoids:

- Heavy blur.
- Full-screen flash.
- Constant screen shake.
- Chromatic aberration.
- Damage numbers.
- Blood.
- Voice lines.

Why:

> The core fantasy is a tight run-and-gun courier game. Readability is more important than cinematic intensity.

### 18.8 Why Mouse Crosshair Is Required?

Mouse aiming is a core control.

Why:

> The player needs a visible aiming point. The OS cursor is inconsistent and can be hidden by UI.

### 18.9 Why Boss Telegraphs Are World Objects?

Boss beam and charge telegraphs appear in the world, not just HUD.

Why:

> Telegraphs must be aligned to the actual damage area. A HUD warning would not tell the player where to move.

### 18.10 Why World 2 Uses the Same Shapes?

World 2 enemies and objects use the same basic shapes as World 1, only with palette and environmental changes.

Why:

> The player should not have to relearn enemy roles in World 2. The challenge comes from layout, wind, verticality, and stronger patterns.

---

## 19. Final Visual Checklist

A stage is visually complete when:

- The player can identify the player character immediately.
- The player can identify their active weapon.
- Enemy projectiles are visually distinct from player projectiles.
- Spikes are visible from at least 3 tiles away.
- One-way platforms have a clear top edge.
- Wind zones show direction.
- Conveyors show direction.
- Checkpoints have clear active/inactive states.
- Conduit has clear locked/active states.
- Cores, hearts, and tuners are visually distinct.
- Boss telegraphs are visible against both world palettes.
- HUD does not cover important gameplay.
- Crosshair is visible in Stage state.
- Damage feedback is clear but readable.
- Stage start, pause, summary, game over, and end are visually distinct.
- Music and SFX match the event.
- World 1 and World 2 feel distinct but coherent.
- No visual element creates unfair ambiguity.