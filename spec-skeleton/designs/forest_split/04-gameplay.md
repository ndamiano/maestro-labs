# 4. GAMEPLAY SPEC

The player is a lone wanderer trapped in a haunted forest at night. The player starts in the Start Clearing with 480 seconds until dawn, 50 lantern fuel, and 100 breath. The player must explore the forest, collect three bone keys, manage lantern fuel and breath, avoid one readable hunter named The Hollow, reach the Old Gate, hold E for 2 seconds to open the gate, and cross the gate threshold before dawn. The Hollow wakes 90 seconds after the run begins, telegraphs for 8 seconds, then hunts through sight, hearing, light, cover, and pathfinding. The player wins when the gate is open and the player center y coordinate is below 6. The player fails when The Hollow touches the player or when dawn remaining time reaches 0. Win takes priority over same-frame fail.

## Records and rosters

### Map record

| Field | Value |
| --- | --- |
| Width | 120 tiles |
| Height | 80 tiles |
| Orientation | North is up |
| Border | Impassable except gate gap |
| Procedural generation | None |
| Levels | One |

Tile types:

| Tile character | Tile | Passable | Movement effect | Cover | Blocks sight and sound |
| ---: | --- | ---: | --- | ---: | ---: |
| `g` | Grass | Yes | Normal speed | No | No |
| `p` | Path | Yes | Normal speed | No | No |
| `u` | Underbrush | Yes | 85 percent speed | Yes when lantern off or fuel 0 | No |
| `t` | Tree | No | Impassable | N/A | Yes |
| `r` | Rock | No | Impassable | N/A | Yes |
| `w` | Water | No | Impassable | N/A | Yes |

Coordinate rosters:

| Location | Coordinate | Purpose |
| --- | ---: | --- |
| Start Clearing | 60, 72 | Player start and tutorial area |
| Old Gate | 60, 5 | Final exit |
| Gate threshold | y below 6 | Safe win zone once gate is open |
| Gate gap | x 59, 60, 61 and y 3, 4, 5 | Passable once gate opens |
| Central Clearing | 60, 40 | High-risk central hub |
| Dead Well | 60, 40 | The Hollow wake point |
| Bone Key A | 95, 60 | Southeast shrine key |
| Bone Key B | 22, 26 | Western grove key |
| Bone Key C | 64, 42 | Central clearing key |
| Ember 1 | 88, 57 | Near Key A |
| Ember 2 | 25, 30 | Near Key B |
| Ember 3 | 88, 22 | Northeast optional fuel |
| Ember 4 | 58, 45 | Near central clearing |
| Ember 5 | 58, 10 | Near gate approach |
| Gate approach target | 60, 6 | Compass target before gate opens |

Zone rosters:

| Zone | Location | Size | Content | Purpose |
| --- | ---: | ---: | --- | --- |
| Start Clearing | 60, 72 | Approximately 10 by 8 tiles | No required pickups, open space, bone marker or faint path | Safe introduction |
| Southeast Root Shrine | 95, 60 | Small clearing | Bone Key A, Ember 1, stone features, underbrush | First key |
| Central Clearing | 60, 40 | Approximately 18 by 18 tiles | Bone Key C, Ember 4, Dead Well, open exposure | Highest-risk objective area |
| Western Thorn Grove | 22, 26 | Approximately 14 by 12 tiles | Bone Key B, Ember 2, more underbrush, narrow tree cover | Stealth and cover |
| Northeast Fuel Hollow | 88, 22 | Approximately 8 by 6 tiles | Ember 3, short branch off main route | Optional fuel |
| North Gate Approach | Around 60, 10 | Approximately 10 by 8 tiles | Ember 5, Old Gate, at least two underbrush cover pockets | Final escape area |

Layout rules:

1. All keys, embers, and the gate are reachable without first collecting other required items.
2. No corridor should be narrower than 2 tiles.
3. The central clearing must be open enough to make light defense useful, but large enough that The Hollow can approach from multiple sides.
4. The gate approach must have at least two cover pockets.
5. The map must have no required backtracking after the third key if the player follows the compass.
6. The map boundary is impassable except through the gate gap.
7. There are at least 8 underbrush clusters.
8. At least 2 underbrush clusters are within Chebyshev distance 6 of gate approach 60, 6.
9. An underbrush cluster is a 4-connected component of underbrush tiles with at least 9 underbrush tiles.
10. Corridor width validator: for every passable tile, count passable 4-neighbor tiles. Ignore the check for required object tiles, tiles within Chebyshev distance 1 of required objects, gate gap tiles, and tiles in passable connected components with area at least 100. Remaining tiles must have at least 3 passable 4-neighbors.

Route length targets:

| Route | Target path length |
| --- | ---: |
| Start to Key A | 120 to 160 tiles |
| Key A to Key C | 120 to 160 tiles |
| Key C to Key B | 160 to 200 tiles |
| Key B to Gate approach | 160 to 200 tiles |
| Total expected route | 550 to 750 tiles |

Route length is measured as Euclidean polyline length in tiles between tile centers using A* paths on static passability.

Content inventory:

| Content | Count | Purpose |
| --- | ---: | --- |
| 2D tile map | 1 | Main forest |
| Player | 1 | Protagonist |
| Bone keys | 3 | Unlock gate |
| Ember stones | 5 | Refill lantern fuel |
| Old Gate | 1 | Final exit |
| Dead Well | 1 | The Hollow wake point |
| The Hollow | 1 | Primary threat |
| Start Clearing | 1 | Safe tutorial area |
| Central Clearing | 1 | High-risk key area |
| Southeast Root Shrine | 1 | First key area |
| Western Thorn Grove | 1 | Stealth key area |
| Northeast Fuel Hollow | 1 | Optional fuel area |
| North Gate Approach | 1 | Final escape area |
| Underbrush clusters | 8 minimum | Cover and stealth |

### Player record

| Field | Initial value |
| --- | ---: |
| pos | 60, 72 |
| radius | 0.5 |
| lanternOn | true |
| fuel | 50 |
| breath | 100 |
| breathLocked | false |
| keysCollected | 0 |
| covered | false |
| inUnderbrush | false |
| moving | false |
| sprinting | false |
| currentNoiseRadius | 0 |
| stepTimer | 0 |
| lastStepTime | 0 |
| gateCharge | 0 |

### Hollow record

| Field | Initial value |
| --- | ---: |
| pos | 60, 40 |
| radius | 0.6 |
| state | Sleeping |
| stateTimer | 0 |
| lostTimer | 0 |
| waypointTimer | 0 |
| pathTimer | 0 |
| path | empty |
| pathIndex | 0 |
| target | null |
| lastKnown | null |
| speed | 0 |

### Gate record

| Field | Initial value |
| --- | ---: |
| x | 60 |
| y | 5 |
| open | false |
| charge | 0 |

## 4.1 Run and Game States [T1]

Game states:

| State | Description |
| --- | --- |
| `title` | Title screen is visible. Simulation is not running. |
| `playing` | Normal gameplay. Timers, movement, pickups, and The Hollow are active. |
| `won` | The gate is open and the player crossed the safe threshold before dawn. |
| `failed` | Dawn arrived, or The Hollow touched the player. |

Initial state when gameplay starts:

- Player is in Start Clearing at 60, 72.
- Dawn timer: 480 seconds.
- Lantern fuel: 50 / 100.
- Breath: 100 / 100.
- Keys collected: 0 / 3.
- The Hollow: Sleeping.
- Gate: Closed.
- Lantern: On.

Retry:

- Pressing R from Won or Failed starts a completely new run.
- All pickups reset.
- The Hollow returns to Sleeping at 60, 40.
- Dawn timer resets to 480 seconds.
- Gate resets to closed.
- Player position, fuel, breath, keys, and charge reset.
- RNG uses the supplied test seed or a new app seed in browser play.

Why no checkpoints:

- The game is a short, self-contained run.
- Full retries preserve time pressure and keep scope small.

## 4.2 Time and Dawn [T1]

- Total time: 480 seconds.
- The timer counts down in real time.
- The player can win at any time before dawn.
- If the timer reaches 0 before the player wins, the run fails.
- Dawn warning begins when time remaining is below 60 seconds.
- Dawn warning uses shape, pulse, color, and audio.

Why 8 minutes:

- Long enough for one full exploration run.
- Short enough to avoid repetition.
- Creates constant pressure without meta-progression.

## 4.3 Player Movement and Breath [T1]

Movement:

- Player can move in 8 directions.
- Diagonal movement is normalized so it is not faster than straight-line movement.
- Player cannot pass through tree trunks, rocks, water, or closed gate gap.
- Underbrush slows movement by multiplying speed by 0.85.

Movement speed:

| Mode | Speed |
| --- | ---: |
| Walk | 3.6 tiles per second |
| Sprint | 6.0 tiles per second |
| Underbrush modifier | 85 percent speed |

Examples:

- Walk in underbrush: 3.6 times 0.85 equals 3.06 tiles per second.
- Sprint in underbrush: 6.0 times 0.85 equals 5.1 tiles per second.

Breath:

| Value | Amount |
| --- | ---: |
| Max breath | 100 |
| Starting breath | 100 |
| Sprint drain | 20 per second |
| Walking recovery | 15 per second |
| Standing recovery | 30 per second |

Rules:

- Sprint is allowed while input sprint is held, breath is above 0, and breath is not locked.
- If breath reaches 0, sprinting is disabled until breath reaches 25.
- Sprinting drains breath.
- Walking recovers breath.
- Standing still recovers breath faster than walking.
- Breath is clamped between 0 and 100.

No player health:

- The player has no health bar.
- If The Hollow touches the player, the run fails.
- There is no damage, healing, or invulnerability.

Why breath exists:

- Prevents the player from outrunning The Hollow indefinitely.
- Makes sprinting a tactical choice.
- Adds tension to chase moments without adding a full health system.

## 4.4 Lantern and Light [T1]

Lantern state:

- The player can toggle the lantern on or off with L.
- The player starts with the lantern on.

Fuel:

| Value | Amount |
| --- | ---: |
| Max fuel | 100 |
| Starting fuel | 50 |
| Ember pickup | +40 fuel |
| Fuel cap | 100 |
| Fuel drain | 0.5 per second while lit |

There are 5 ember stones.

Total available fuel if all embers are collected:

```text
50 starting fuel + 5 times 40 ember fuel = 250 fuel
```

At 0.5 fuel per second, this supports:

```text
250 divided by 0.5 = 500 seconds of continuous light
```

The run is 480 seconds. A player who uses all fuel and never turns the lantern off has a small spare margin. If one ember is missed, the player must use darkness for a meaningful portion of the run.

Light radius:

If the lantern is on and fuel is above 0:

```text
light_radius = 4 + fuel times 0.04
```

Examples:

| Fuel | Light radius |
| ---: | ---: |
| 1 | 4.04 |
| 25 | 5.00 |
| 50 | 6.00 |
| 100 | 8.00 |

If the lantern is off or fuel is 0:

```text
light_radius = 0
```

Player visibility:

| Lantern state | Condition | Player visible range |
| --- | --- | ---: |
| On | Fuel above 0 | light radius + 2 |
| Off or fuel 0 | Player covered | 3 tiles |
| Off or fuel 0 | Player uncovered | 6 tiles |

A player is covered if:

- The player center tile is underbrush, or
- Any of the 4 orthogonal adjacent tiles is blocking.

Light safe zone:

The Hollow cannot enter the player’s light safe zone when:

- Lantern is on.
- Fuel is 25 or higher.
- The tile is within the player’s light radius.

If fuel drops below 25, the safe zone disappears.

The light radius still exists below 25 fuel, but it no longer repels The Hollow.

Fuel warning:

- HUD shows a clear warning state when fuel is below 20.
- Warning uses pulse, shape, color, and audio.

Why light is central:

- Navigation: the player needs light to see the forest.
- Defense: The Hollow cannot enter the safe light radius while fuel is high enough.
- Risk: using light drains fuel and makes the player more visible.

## 4.5 Pickups and Objectives [T1]

Bone keys:

- There are 3 bone keys.
- Keys can be collected in any order.
- Keys are required to open the gate.
- Keys are auto-picked-up when the player center is 0.75 tiles or closer to the key center.
- Picking up a key produces a noise event with radius 6 tiles.

Ember stones:

- There are 5 ember stones.
- Ember stones are auto-picked-up when the player center is 0.75 tiles or closer to the ember center.
- Each adds 40 fuel.
- Fuel is capped at 100.
- Picking up an ember produces a noise event with radius 4 tiles.

Pickup feedback:

- Key pickup: small white pulse, HUD key slot fills, bone chime, very small ground ripple.
- Ember pickup: amber spark burst, fuel bar rises, lantern flame brightens briefly, warm ember sound.

Why auto-pickups:

- Keeps movement fluid.
- Avoids fumbling during tense moments.
- Still creates noise through the pickup event.
- Only the final gate requires a held interaction because it is the climactic risk.

## 4.6 Gate and Threshold [T1]

Gate:

- The gate is at 60, 5.
- The gate is closed at the start.
- The player can interact with the gate only when the player center is 1.5 tiles or closer to the gate center.
- If keys are missing, the gate shows a locked prompt.
- With all 3 keys, the player must hold E for 2 seconds to open the gate.
- Opening the gate produces a noise event with radius 12 tiles.
- Once open, the gate remains open.
- If E is released before 2 seconds, gate charge decays at 4 per second.
- The player must cross the threshold to win.

Gate gap:

- The passable gate gap is x 59, 60, 61 and y 3, 4, 5.
- While closed, gap tiles block the player.
- While open, gap tiles allow the player.

Gate threshold:

- The threshold is the zone where y is below 6.
- Once the gate is open, The Hollow cannot enter any tile where y is below 6.
- The player wins when the gate is open and the player center y coordinate is below 6.

If The Hollow is in the threshold when the gate opens:

- Move The Hollow to the nearest reachable tile where y is 6 or higher.
- Do not damage The Hollow.
- Do not count this as a fail unless The Hollow is still overlapping the player before the win check.

## 4.7 The Hollow State Machine [T1]

The Hollow is the only enemy.

Basic rules:

- The Hollow cannot be killed.
- The Hollow cannot be permanently disabled.
- The Hollow can be avoided, delayed, or kept away using light and cover.
- If The Hollow touches the player, the run fails.
- The Hollow visual may be larger than the gameplay hitbox.
- The Hollow hitbox radius is 0.6 tiles.
- Player hitbox radius is 0.5 tiles.
- Contact fail occurs when distance between player center and Hollow center is 1.1 tiles or less.

States:

| State | Description |
| --- | --- |
| Sleeping | No threat before wake time |
| Waking | 8-second telegraph, non-hostile |
| Curious | Patrols around the wake point |
| Investigating | Moves to the last known player location |
| Searching | Searches around the last known player location |
| Hunting | Actively chases the player |

### Sleeping

- Duration: until run elapsed reaches 90 seconds.
- Movement: none.
- Detection: none.
- Damage: none.

Transition:

- When elapsed reaches 90 seconds, state becomes Waking.
- State timer resets to 0.
- Emit `hollow.wake`.

### Waking

- Duration: 8 seconds.
- Location: Dead Well at 60, 40.
- Movement: none.
- Detection: none.
- Damage: none.
- Purpose: telegraph The Hollow’s activation.

Transition:

- When state timer reaches 8 seconds, state becomes Curious.
- Emit `hollow.state_change`.
- Recalculate path.

### Curious

- Speed: 2.4 tiles per second.
- Behavior:
  - Patrols within a 6-tile radius of the wake point.
  - Chooses new waypoints every 2 seconds or when reached.
  - Avoids active light safe zones.
- Transition:
  - If The Hollow detects the player, it enters Investigating.

### Investigating

- Speed: 3.2 tiles per second.
- Duration: up to 8 seconds.
- Behavior:
  - Moves to the player’s last known position.
  - If it detects the player, it enters Hunting.
  - If it reaches the last known position and does not detect the player, it enters Searching.
- Light rule:
  - If the last known position is inside the player’s light safe zone, The Hollow targets the nearest reachable tile outside the safe radius.

### Searching

- Speed: 3.2 tiles per second.
- Duration: 12 seconds.
- Behavior:
  - Searches around the last known player position.
  - Chooses random waypoints within a 6-tile radius.
  - Avoids light safe zones.
  - If it detects the player, it enters Hunting.
  - If 12 seconds pass without detection, it returns to Curious.

Why Searching matters:

- Gives the player a chance to escape by hiding.
- Prevents The Hollow from permanently chasing the player forever.
- Makes stealth meaningful.
- Rewards using cover and turning off the lantern.

### Hunting

- Speed: 5.0 tiles per second.
- Behavior:
  - Targets the player’s current position if detected.
  - If the player is not detected for 6 seconds, targets the last known position.
  - If detection continues, The Hollow remains in Hunting.
  - If the player is lost for 6 seconds, The Hollow enters Searching.
- Light rule:
  - If the player is inside the light safe zone, The Hollow targets the nearest reachable tile outside the safe radius and waits.
  - If the safe zone shrinks or disappears, The Hollow recalculates its path.

Speed comparison:

| Entity | Speed |
| --- | ---: |
| Player walk | 3.6 tiles per second |
| Player sprint | 6.0 tiles per second |
| The Hollow hunt | 5.0 tiles per second |
| The Hollow hunt in underbrush | 4.25 tiles per second |
| Player sprint in underbrush | 5.1 tiles per second |

Why these speeds:

- The player can outrun The Hollow while sprinting.
- Breath limits how long the player can outrun it.
- Underbrush slows both entities, but the player can still escape if they have breath.
- The Hollow is fast enough to create real pressure.

## 4.8 Perception [T1]

The Hollow detects the player through sight and hearing. Detection is not random.

Sight:

The Hollow can see the player if:

1. The Hollow is not Sleeping or Waking.
2. There is line of sight.
3. The player is within The Hollow’s sight range.

Line of sight:

- Blocked by tree trunks, rocks, and water.
- Not blocked by underbrush.
- Underbrush affects cover state, not ray blocking.

Sight range:

| Player lantern | Player condition | Sight range |
| --- | --- | ---: |
| On, fuel above 0 | Any | light radius + 2 |
| Off or fuel 0 | Covered | 3 tiles |
| Off or fuel 0 | Uncovered | 6 tiles |

Why lantern on increases sight:

- A lit player is easier to see.
- Light is both a defensive tool and a liability.

Why covered range is lower:

- When the lantern is off and the player is in underbrush or adjacent to cover, The Hollow has a much harder time spotting them.

Hearing:

The player generates noise.

Noise is heard if:

1. The Hollow is not Sleeping or Waking.
2. The Hollow is within the noise radius.
3. There is line of sight between The Hollow and the player.
4. Noise is blocked by the same impassable tiles that block sight.
5. Underbrush does not block noise.

Noise radii:

| Action | Noise radius |
| --- | ---: |
| Walking | 5 tiles |
| Sprinting | 10 tiles |
| Sprinting in underbrush | 12 tiles |
| Key pickup | 6 tiles |
| Ember pickup | 4 tiles |
| Gate opening | 12 tiles |

Continuous noise:

- Standing still: 0.
- Walking: 5.
- Sprinting: 10.
- Sprinting in underbrush: 12.

Event noise:

- Key pickup: 6.
- Ember pickup: 4.
- Gate opening: 12.

Detection priority:

- The newest detection becomes the last known position.
- If the player is currently visible, The Hollow targets the player directly.
- If the player is not visible, The Hollow targets the last known position.

Why noise exists:

- Movement is a risk.
- Sprinting is powerful but loud.
- Pickups are useful but can attract The Hollow.
- The final gate opening is a deliberate loud event.

## 4.9 Light Safe Zones [T1]

Safe zone rule:

The safe zone is active when:

- The player’s lantern is on.
- Player fuel is 25 or higher.
- Light radius is above 0.

A tile is safe for The Hollow when:

- Safe zone is active.
- Distance from tile center to player center is less than or equal to light radius.

Use tile center distance.

If The Hollow is already in a tile that becomes safe:

- The Hollow may remain in that tile.
- It cannot enter new safe tiles.
- It can move out of the safe area if its path allows it.

This prevents The Hollow from being permanently trapped inside the player’s light.

If the player stands in light:

- The Hollow waits outside the safe radius.
- Fuel continues to drain.
- Once fuel drops below 25, the safe zone disappears.

Why this is fair:

- The player can defend with light, but cannot stall forever.
- The Hollow cannot cheat through light.
- The player must eventually move because dawn is approaching.

## 4.10 Compass and Objective Aid [T1]

The game includes a subtle objective arrow.

Objective sequence:

1. Find the first bone key.
2. Find the remaining bone keys.
3. Escape before dawn.

Arrow behavior:

- Before all keys are collected, the arrow points to the nearest uncollected bone key.
- After all keys are collected and gate is closed, the arrow points to gate approach 60, 6.
- After all keys are collected and gate is open, the arrow points to gate gap center 60, 4.
- The arrow appears when the objective target is off-screen.
- The arrow is hidden when the target is visible on-screen.
- The arrow is not a minimap.
- The arrow does not show obstacles.

Arrow algorithm:

1. Determine the objective target.
2. Use A* pathfinding from the player to the target.
3. If a path exists, point the arrow toward the first meaningful waypoint after the player’s current tile.
4. If no path exists, fall back to straight-line direction.
5. Update the arrow every 0.5 seconds.

Nearest key tie-break:

- Use Euclidean distance.
- Ties resolve by key ID order: A, B, C.

Why a compass arrow exists:

- Prevents soft-stuck states.
- Reduces frustration.
- Still requires the player to navigate manually.
- Avoids giving away the full map.

Why no minimap:

- A minimap would remove too much tension and make the forest feel less like an unknown space.

## 4.11 Win, Fail, Priority [T1]

Win condition:

The player wins when:

1. The gate is open.
2. The player center y coordinate is below 6.
3. Dawn has not yet arrived.

Fail conditions:

The player fails when either:

1. Dawn remaining time reaches 0 before the win condition is met.
2. The Hollow’s hitbox overlaps the player’s hitbox.

Contact fail:

- Contact occurs when distance between player center and Hollow center is less than or equal to 1.1 tiles.

Frame priority:

If a win condition and a fail condition happen on the same frame:

- Win takes priority.

Check order:

1. Win condition.
2. Fail by The Hollow contact.
3. Fail by dawn.

This means if the player crosses the threshold and a fail condition happens on the same frame, the player wins.

## 4.12 Edge Cases [T1]

| Edge case | Behavior |
| --- | --- |
| Player runs out of fuel | Lantern light radius becomes 0. Safe zone disappears. Player sees ambient range: 3 tiles if covered, 6 tiles if uncovered. Run can still be completed. |
| Player runs out of breath | Sprinting disabled until breath reaches 25. Player can still walk. The Hollow can catch the player if escape is impossible. |
| Player stands in light safe zone | The Hollow waits outside the safe radius. Fuel continues to drain. Once fuel drops below 25, the safe zone disappears. |
| The Hollow cannot path to target | Moves to nearest reachable waypoint. Waits or locally wanders. Does not teleport. Does not pass through blockers. |
| Player hides in underbrush | If lantern is off and player is covered, sight range is 3 tiles. The Hollow can still hear walking noise at 5 tiles, or sprinting in underbrush at 12 tiles. If The Hollow loses the player during Searching, it leaves after 12 seconds. |
| Player reaches gate without all keys | Gate remains closed. Prompt shows sealed. Player cannot win. Dawn can still fail the player. |
| Player opens gate but does not cross | Gate remains open. Player can still cross later. Dawn still applies. The Hollow still applies outside the threshold. |
| The Hollow is in threshold when gate opens | The Hollow moves to nearest reachable tile where y is 6 or higher. No damage. No fail unless still overlapping player before win check. |
| Win and fail happen on same frame | Win takes priority. |
| Player ignores compass | Player may fail by dawn. |
| Player wastes fuel | No separate fail. Reduced visibility and loss of safe-zone defense. |
| Player sprints too much | Breath lock forces tactical pause. Sprinting also makes the player easier to hear. |

## Progression and difficulty

Phase 1: Safe Start

- Time: 0:00 to 1:30.
- Objective: learn movement, lantern, sprint and breath, reach Key A.
- The Hollow is sleeping.
- Feel: curious, slightly tense, not yet in immediate danger.

Phase 2: The Hollow Wakes

- Time: 1:30 to approximately 5:30.
- Objective: collect remaining keys, manage fuel, avoid The Hollow, use cover and light.
- The Hollow is active.
- Feel: pressured, cautious, aware of noise and light.

Phase 3: Escape

- Time: approximately 5:30 to 8:00.
- Objective: reach the gate, open the gate, cross the threshold.
- Feel: fast, risky, resolved.

Expected timing:

| Player skill | Expected time |
| --- | ---: |
| Efficient | 5:30 to 6:30 |
| Cautious | 6:30 to 7:30 |
| Hard fail threshold | 8:00 |

Why these times:

- The player should feel the possibility of failure but not the feeling of impossible timing.
- A cautious player should have enough time if they manage fuel and avoid bad fights.
- A reckless player should fail from noise, bad light use, or bad routing.

## Feel goals

The game should feel:

- Slow at first.
- Increasingly tense after The Hollow wakes.
- Dangerous in the central clearing.
- Quiet in underbrush.
- Desperate near the gate.

Key feel rules:

1. The player should usually have 2 or 3 meaningful choices:
   - Turn lantern on or off.
   - Walk or sprint.
   - Hide or move.
2. The Hollow should never feel random.
   - It should always be reacting to sight or noise.
3. The player should usually understand why they died:
   - They made too much noise.
   - They used too much light.
   - They stayed in the open.
   - They ran out of breath.
   - They ran out of fuel.
   - They were too late.
