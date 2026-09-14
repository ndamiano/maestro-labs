# 5. CHARACTERS

## 5.1 Courier Jex

Silhouette:

- Compact courier.
- Hooded upper body.
- Small mask or visor.
- Signal backpack.
- Slightly bulky chest panel.
- Narrow legs.
- Compact weapon arm.
- Silhouette must read as a lone human courier, not a knight, robot, or cartoon hero.

Player colors:

| Part | Color |
| --- | --- |
| Suit | `#2A323C` |
| Suit shadow | `#171D24` |
| Hood edge | `#3A4856` |
| Visor | `#4BE2FF` |
| Backpack | `#3A4856` |
| Signal belt | `#FFB347` |
| Boots | `#1C2530` |

The cyan visor is the main identity point.

Sprite size:

| State | Hitbox | Visual Sprite |
| --- | ---: | ---: |
| Standing | 16 x 24 | 32 x 40 |
| Crouching | 16 x 12 | 32 x 28 |

Origin:

- Center bottom.

Facing:

- Flip sprite horizontally.
- Visual facing follows mouse X or last horizontal input.
- If no horizontal input has occurred, face right.

Animations:

| Animation | Frames | Duration | Notes |
| --- | ---: | ---: | --- |
| Idle | 4 | 1.2 s | Slight breathing |
| Run | 6 | 0.45 s | Compact courier stride |
| Jump | 3 | one-time | Knees tuck |
| Fall | 2 | one-time | Arms back |
| Crouch | 4 | 0.2 s | Body compresses 65 percent height |
| Crouch Run | 4 | 0.5 s | Low shuffling |
| Shoot | 2 | 0.15 s | Weapon recoil |
| Hurt | 2 | 0.2 s | Body tilts back |
| Death | 6 | 0.5 s | No blood, signal shatter |

Death visual:

- Player breaks into cyan and white signal shards.
- Small rust shards.
- No gore.
- No lingering corpse.
- Death lasts 0.5 seconds, then respawn or game over.

Crouch visual:

- Sprite compresses vertically.
- Visor remains visible.
- Weapon lowers.
- Muzzle origin visually matches gameplay crouch offset.
- Hitbox is smaller, but sprite may still show some head height for readability.
- Crouch state must be obvious.

## 5.2 Mite Crawler

Silhouette:

- Small rust bug.
- Four legs.
- Red eye.
- Visual sprite: 24 x 24.

Palette:

- Rust dark.
- Rust light.
- Red eye.

Animation and states:

- Crawl: 4 frames, 0.5 s loop.
- Blocked: 0.5 s wait, antennae twitch.
- Hit: squash.
- Death: 4 rust shards.

Facing:

- Face movement direction.
- If blocked, keep last facing.

## 5.3 Dredge Drone

Silhouette:

- Small maintenance drone.
- Single red eye.
- Two side thrusters.
- Visual sprite: 32 x 28.

Palette:

- Steel.
- Rust light.
- Red eye.
- Amber thruster glow.

Animation and states:

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

Facing:

- Face player when firing.
- Otherwise face patrol direction.

## 5.4 Pincer Bot

Silhouette:

- Low armored walker.
- Two front pincers.
- Red core between pincers.
- Visual sprite: 32 x 32.

Palette:

- Rust dark.
- Steel.
- Red core.

States:

| State | Visual |
| --- | --- |
| Idle | Slow walk, pincers closed |
| Telegraph | Pincers open, red core brightens, body shakes 2 px |
| Charge | Body stretches forward, red trail |
| Cooldown | Pincers lower, core dims |

Telegraph:

- Duration: 0.5 s.
- Shake: 2 px horizontal.
- Pincers open.
- Red glow intensifies.

Charge:

- Body stretches 1.2 times horizontally.
- Red trail: 3 fading frames.
- Stops with small impact puff.

Facing:

- Face charge direction.

## 5.5 Warden Sentry

Silhouette:

- Wall or floor turret.
- Rotating head.
- Thick barrel.
- Red target light.
- Visual sprite: 40 x 40.

Palette:

- Steel.
- Rust.
- Red target light.
- Orange muzzle.

Animation and states:

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

Facing:

- Barrel angle communicates target direction.

## 5.6 Mist Wraith

Silhouette:

- Ghost-like signal creature.
- Tattered lower body.
- Pale cyan or white form.
- Dark hollow center.
- Visual sprite: 32 x 32.

Palette:

- Signal cyan.
- Signal white.
- Dark void center.

Phased visual:

- Alpha drops to 0.25.
- Outline becomes dashed.
- Small ripple appears at phase start and end.
- Player projectiles pass through with faint distortion.
- No player damage while phased.

Facing:

- Face movement direction toward player.

## 5.7 Bolt Golem

Silhouette:

- Large rust machine.
- Heavy arms.
- Central chest cannon.
- Thick legs.
- Visual sprite: 64 x 64.

Palette:

- Rust dark.
- Rust light.
- Steel.
- Red chest core.

Animations and states:

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
  - Screen shake: 3 px, 0.1 s if T2 screen shake is active.
  - Dust puff.
  - Temporary spike patches appear.

Facing:

- Face movement direction or player when attacking.

## 5.8 World 2 Enemy Variants

World 2 enemies use the same shapes with a brighter Skyloom palette.

Changes:

- Rust replaced with pale steel.
- Red eyes remain red.
- Thruster glows are slightly brighter.
- Small sky-fin or cable detail added.
- Shadows are softer.

## 5.9 Hush Warden

Silhouette:

- Large maintenance warden.
- Rust armor.
- Single red optic.
- Four heavy arms.
- Visual sprite: 80 x 80.

Palette:

- Rust dark.
- Rust light.
- Steel.
- Red optic.
- Orange warning lights.

Phase visuals:

- Phase 1:
  - Red optic dim.
  - Armor intact.
  - Movement heavy.
- Phase 2:
  - Red optic brighter.
  - Armor cracks reveal orange core.
  - Slight red glow around body.

Attack visuals:

- Charge:
  - 0.6 s telegraph.
  - Boss crouches.
  - Red line appears from boss toward player direction.
  - Red chevrons pulse along path.
  - Boss dashes with red trail.
  - Spike patches appear along path with red tips.
- Fan Bolt:
  - Three red bolts.
  - Muzzle flash from chest.
- Sweep Beam:
  - 0.8 s telegraph.
  - Dashed red line appears at boss or player Y.
  - Height: 24 px.
  - Edge arrows appear at arena boundaries.
  - Solid red beam with white core and orange edge glow.
  - Lasts 0.7 s.
- Drone Summon:
  - Red ring appears at boss.
  - Two Dredge Drones fade in over 0.4 s.
  - Small smoke puff.

Death:

- 2-second sequence:
  1. Boss stops.
  2. Optic flickers.
  3. Red light turns off.
  4. Armor panels fall.
  5. White signal burst.
  6. Conduit activates.

## 5.10 Null Relay

Silhouette:

- Abstract central relay.
- Rotating geometric rings.
- Central core.
- No human face.
- Should feel like a corrupted city relay, not a monster.
- Visual sprite: 96 x 96.

Palette by phase:

| Phase | Core | Rings |
| --- | --- | --- |
| 1 | Violet | Cyan |
| 2 | Magenta | Violet |
| 3 | White | Red |

Attack visuals:

- Rain:
  - Three vertical columns.
  - Telegraph: 0.3 s red dashed vertical lines.
  - Red vertical shards with white core.
  - Small dust or water splash on impact.
- Side Sweep:
  - 0.8 s telegraph.
  - Dashed horizontal line at random valid Y chosen at telegraph start.
  - Red or orange.
  - Edge arrows.
  - Horizontal beam, 24 px height, red outer, white core.
- Echo Shot:
  - Three violet bolts.
  - Each bolt bounces once.
  - Bounce visual: violet spark, slight squash, short trail.
- Wraith Summon:
  - Purple ring.
  - Two Mist Wraiths fade in.
- Overload Cycle:
  - Horizontal beam telegraph and active.
  - Vertical beam telegraph and active.
  - Core Exposed:
    - Boss becomes stationary.
    - Core turns bright white.
    - Ring of white light pulses.
    - Player projectiles hitting core produce extra white ripple.
    - Boss bar pulses white.

Death:

- 3-second sequence:
  1. Boss stops.
  2. Rings slow.
  3. Core flashes white.
  4. Rings collapse inward.
  5. Large white burst.
  6. Background city lights begin to restore.
  7. Conduit activates.
