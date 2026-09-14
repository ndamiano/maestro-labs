# 5. CHARACTERS

## Player

Silhouette:

- Hooded figure.
- Dark blue-grey cloak.
- Simple silhouette.
- Small lantern in one hand.
- No detailed face.
- No weapon.
- No armor.
- Human and vulnerable, not heroic.

Sprite size:

- Approximately 40 px by 48 px.
- Visual sprite may be slightly taller than gameplay hitbox.
- Player center is the primary visible point.
- Lantern is clearly visible on one side.

Facing:

- Top-down 8-directional facing.
- Facing follows the last non-zero movement vector.
- If no movement input, facing remains from the last move.

Animation states:

| Animation name | Visual | Motion rule |
| --- | --- | --- |
| player_idle | Subtle breathing, lantern flame steady or mild flicker | Plays when not moving. |
| player_walk | Slow 8-way walk cycle | Plays when moving at walk speed. |
| player_sprint | Faster cycle, slight forward lean, small breath mist | Plays when sprinting. Breath mist appears only while sprinting. |
| player_covered_underbrush | Sprite lowers, lower half darkened, grass tufts over feet | Plays when player center is underbrush. |
| player_covered_blocker | Slight tuck against rock or tree, darker side facing blocker | Plays when adjacent to a blocking tile. |
| player_lantern_on | Warm flame, light mask active | Plays when lantern is on and fuel is above 0. |
| player_lantern_off | Cold ambient halo only | Plays when lantern is off or fuel is 0. |
| player_fuel_low | Flame sputters, light flickers | Plays when fuel is below 20. |
| player_caught | Black tendrils or shadow shape overtakes the player | Plays only on caught fail. |

Motion notes:

- Keep animations small and slow.
- Do not use exaggerated superhero movement.
- Sprint should look urgent but not comedic.
- Breath mist should appear only while sprinting.
- The player should not visually bob too much.

## The Hollow

Silhouette:

- Tall.
- Thin.
- Ragged.
- Dark.
- Cold.
- Slightly larger than the player.
- Not human-shaped enough to be relatable.
- Not too detailed to be distracting.

Sprite size:

- Approximately 64 px by 76 px.
- Visual silhouette may be larger than gameplay hitbox.
- Fatal center is the dense core of the sprite.
- Outer tendrils, shadow, and mist are decorative.
- In high-contrast T2 mode, show a faint cold outline around the fatal core.

Color:

- Body: Deep Night Black.
- Rim: Hollow Blue.
- Eyes: Cold Moon.
- Aura: very faint cold blue.
- State accents: pale cold blue, never red.

Facing:

- Top-down 8-directional facing.
- Facing follows movement target or player direction when detected.
- While Sleeping or Waking, facing is fixed toward the player start or the well center.

Animation states:

| Animation name | Visual | Motion rule |
| --- | --- | --- |
| hollow_sleeping | Dark shape under faint well mist, no eyes, slow breathing distortion | Plays in Sleeping. No movement. |
| hollow_waking | Mist rises, black shape straightens, pale eyes open, cold rim appears | Plays in Waking. No movement. 8-second telegraph. |
| hollow_curious | Dim blue rim, slow drift, head scans, low posture | Plays in Curious. Slow wandering within 6 tiles of wake point. |
| hollow_investigating | Upright, leans toward target, one eye brighter, faint cold trail | Plays in Investigating. Faster, purposeful movement to last known position. |
| hollow_searching | Circling motion, head sweeps, faint ripple around feet | Plays in Searching. Medium patterned movement around last known position. |
| hollow_hunting | Bright eyes, stretched silhouette, faster lurch, cold shadow stretches | Plays in Hunting. Fast urgent movement. |
| hollow_safe_wait | Stops at safe zone edge, shadow may stretch toward light, may pace or lean | Plays when blocked by active safe zone. |
| hollow_caught | Black tendrils consume player and Hollow | Plays only on caught fail. |

State-change cues:

- Brief cold blue pulse around The Hollow.
- Small audio sting or intake.
- If The Hollow is not on screen, use subtle cold vignette pulse and audio only.
- Do not show a marker pointing to The Hollow.

Waking cue:

- At 90 seconds, if The Hollow is visible, well mist rises and the shape forms clearly.
- If The Hollow is not visible, play a low groan and brief cold vignette pulse.
- Music shifts into pressure layer.

Hunting cue:

- The Hollow’s eyes flare briefly.
- A cold blue vignette pulse appears for about 0.5 seconds.
- A short high whisper or cold sting plays.
- The Hollow’s silhouette stretches slightly toward the player.

Interaction with light safe zone:

- When The Hollow is outside an active light safe zone, it stops at the edge.
- Its shadow may stretch toward the light.
- It may pace or lean, but it cannot cross.
- If the safe zone flickers or disappears, its eyes brighten slightly.
