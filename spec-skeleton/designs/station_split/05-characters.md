# 5. CHARACTERS

**Player silhouette (carried from visual §8.1).** A top-down astronaut: white/light-gray suit, dark visor, small backpack with an O2 light, no detailed face, no portrait. The white suit gives contrast against dark floors. Facing: the visor marks the facing direction — always the last non-zero movement direction (`player.facing`), so it persists when stopped.

Player animations, by name (state → motion rule):
- `idle` — steady suit light, subtle breathing bob.
- `move` — footstep cycle; tiny boot/dust particles (T2), very subtle.
- `low_o2` — backpack O2 light pulses cyan (below 25).
- `critical_o2` — rapid cyan/white backpack pulse (below 10).
- `damage` — red flash on the sprite; red vignette flash max 0.2 s; screen shake max 4 px, 0.15 s.
- `invulnerable` — white flicker at **10 Hz** for **0.5 s** (matches 4.4).
- `death` — suit light turns gray; screen desaturates.

**Drone silhouette (carried from visual §8.2).** Maintenance bot, not horror enemy: circular or compact square hover body, two short mechanical arms, orange caution light, small scanner element, slight hover bob, no face. Facing: sprite rotates toward its velocity vector; when stationary it keeps the last facing.

Drone animations, by name (the five states 4.11 requires, motion rules):
- `inactive` — parked, gray light, no motion.
- `patrol` — slow movement (2.5 tiles/sec) between waypoints, soft hover bob, gray/low-orange light.
- `alert` — orange light brightens, small orange ring or triangle appears above the drone, movement speed increases to 3.0 tiles/sec.
- `attack` — brief orange zap effect (one tick), short red/orange flash on the player.
- `disabled` — smoking, one arm bent or sparking, gray light, no motion; never reactivates.

Drones must read as machines still doing maintenance; the orange triangle plus the word `DRONE` carry the threat, not sprite detail.
