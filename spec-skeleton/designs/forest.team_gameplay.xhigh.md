2D, top-down camera fixed overhead, centered on the player.

# 1. THE GAME IN ONE PARAGRAPH
Minute to minute, the player moves through a dark, seeded 64x64 forest, uses a battery-limited flashlight to see paths and creatures, collects 3 Moon Sigils, and presses E at the open Dawn Gate before a 480-second dawn timer expires. It is worth doing again because each seed changes tree placement, Sigil locations, item locations, wave spawn points, and the pressure of 15 total enemies across the night; players refine flashlight economy, dash timing, flare use, and route risk. If the player has all 3 Sigils and presses E on the Gate tile before DawnTimer reaches 0, the run ends in success; if DawnTimer reaches 0, Health reaches 0, or the player misses the gate, the run ends in failure.

# 2. RECORDS
RECORDS: Player, Night, Map Tile, Entity, Item, Tool, Flare, Wave

Player: one per run. Fields: Health (points, 0–100, starts 100), Stamina (points, 0–100, starts 100), FlashlightBattery (percent, 0–100, starts 100), FlashlightOn (boolean, starts true), AimDirection (degrees, 0–359, starts 0), DashTimer (seconds, 0–0.25, starts 0), DashCooldown (seconds, 0–1.2, starts 0), DashX (px/s, starts 0), DashY (px/s, starts 0), StaminaDelay (seconds, 0–1.0, starts 0), Invulnerability (seconds, 0–1.0, starts 0), KnockbackTimer (seconds, 0–0.3, starts 0), KnockbackX (px/s, starts 0), KnockbackY (px/s, starts 0), Sigils (count, 0–3, starts 0), X (pixels, starts 1040), Y (pixels, starts 1040), VelocityX (px/s, starts 0), VelocityY (px/s, starts 0).

Night: one per run. Fields: Seed (integer, starts from a provided seed or 1, and the next run uses Seed + 1), DawnTimer (seconds, 480–0, starts 480), GateOpen (boolean, starts false), State (enum: Running, Success, Failed, starts Running), Cause (enum: None, Dawn, Death, starts None), ResultTime (seconds, 0–480, starts 0).

Map Tile: one per cell in a 64x64 grid. Fields: X (tile index, 0–63, starts from generator), Y (tile index, 0–63, starts from generator), Kind (enum: Empty, Tree, Gate, starts from generator). Each tile is 32 px wide and 32 px tall.

| Kind | Walkable | Blocks line of sight | Effect |
|---|---:|---:|---|
| Empty | true | no | no effect |
| Tree | false | yes | blocks movement and detection |
| Gate | true | no | if Player.X/Y is within 24 px of this tile center and Player.Sigils is 3, pressing E can end the run |

Entity: one per spawned creature. Fields: Id (integer, unique per run, starts 1), Kind (enum: Wraith, Howler, Lurker, starts from wave), X (pixels, starts from spawn point), Y (pixels, starts from spawn point), State (enum: Wandering, Chasing, Losing, starts Wandering), WanderTimer (seconds, 0–2.0, starts 2.0), LoseTimer (seconds, 0–5.0, starts 0), AttackTimer (seconds, 0–3.0, starts 0), SlowTimer (seconds, 0–2.5, starts 0), HitCooldown (seconds, 0–1.5, starts 0), Speed (px/s, starts from roster), WanderingSpeed (px/s, starts from roster), VelocityX (px/s, starts 0), VelocityY (px/s, starts 0), WanderX (px/s, starts 0), WanderY (px/s, starts 0).

| Kind | Speed (px/s) | WanderingSpeed (px/s) | Detection radius (px) | Lose timer (s) | Contact damage (points) | Knockback (px/s) | HitCooldown (s) | Special |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Wraith | 90 | 45 | 300 while FlashlightOn is true, otherwise 120 | 4 | 15 | 90 | 1.0 | Chases if line is clear and Player is within its detection radius |
| Howler | 150 | 75 | 0 | 4 | 25 | 140 | 1.0 | Chases if Player.DashTimer starts while distance is 260 px or less |
| Lurker | 70 | 35 | 140 | 5 | 30 | 160 | 1.5 | While Chasing, teleports 180 px toward Player every 3.0 s |

Item: one per pickup. Fields: Id (integer, unique per run, starts 101), Kind (enum: Moon Sigil, Battery, Herb, starts from generator), X (pixels, starts from generator), Y (pixels, starts from generator), Taken (boolean, starts false).

| Kind | Placed per map | Pickup effect |
|---|---:|---|
| Moon Sigil | 3 | Player.Sigils increases by 1; if Player.Sigils becomes 3, Night.GateOpen becomes true |
| Battery | 5 | Player.FlashlightBattery becomes min(100, Player.FlashlightBattery + 40) |
| Herb | 4 | Player.Health becomes min(100, Player.Health + 35) |

Tool: one per tool kind. Fields: Kind (enum: Flare, starts Flare), Count (count, 0–1, starts 1).

| Tool | Count | Use | Effect |
|---|---:|---|---|
| Flare | 1 | Q | throws a flare 220 px in AimDirection, creates a 90 px radius effect that slows and pushes entities |

Flare: one per thrown flare. Fields: X (pixels, starts from throw point), Y (pixels, starts from throw point), Timer (seconds, 2.5–0, starts 2.5), Radius (pixels, starts 90), SlowMultiplier (fraction, starts 0.5).

Wave: one per scheduled spawn group. Fields: Index (integer, 1–4, starts from roster), TriggerTime (seconds after run start, starts from roster), Wraiths (count, starts from roster), Howlers (count, starts from roster), Lurkers (count, starts from roster), SpawnX (pixels, starts from generator), SpawnY (pixels, starts from generator), Used (boolean, starts false).

| Index | TriggerTime (s) | Wraiths | Howlers | Lurkers |
|---:|---:|---:|---:|---:|
| 1 | 0 | 3 | 1 | 1 |
| 2 | 150 | 2 | 1 | 0 |
| 3 | 300 | 1 | 1 | 1 |
| 4 | 420 | 2 | 1 | 1 |

# 3. SYSTEMS
SYSTEMS: Map Generator, Controls, Movement, Light and Battery, Entities, Items and Flare, Waves and Dawn

## Map Generator
SEEDED GENERATOR: A Map Generator uses Night.Seed to place a 64x64 forest. It places, in this order: border trees, random interior trees, the start clearing, the Gate, 3 Moon Sigils, 5 Batteries, 4 Herbs, and 4 Wave spawn points. Parameters: Tree probability is 0.36 for each non-border tile; the start clearing is tiles X=30–34 and Y=30–34; the Gate side is chosen with 25% chance each for north, south, east, or west; the Gate tile index along its side is chosen from 10–53; each Moon Sigil is placed on an Empty tile 300–600 px from Player start; each Battery and Herb is placed on an Empty tile at least 64 px from every other Item; each Wave spawn point is placed on an Empty tile at least 320 px from Player start and at least 180 px from every Item; each Wave spawn point must have Empty tiles at offsets (0,0), (64,0), (-64,0), and (0,64); at least one Battery must be within 160 px of Player start; at least one Herb must be within 220 px of Player start.

VERIFIER: The map passes only if all checks succeed: tile (32,32) is Empty; the Gate tile is Gate; a 4-direction path exists from tile (32,32) to the Gate through non-Tree tiles; a 4-direction path exists from tile (32,32) to every Item through non-Tree tiles; a 4-direction path exists from tile (32,32) to every Wave spawn point through non-Tree tiles; each Wave spawn point has the four required offset tiles Empty; total Tree tiles are between 1200 and 2200; at least one Battery is within 160 px of Player start; at least one Herb is within 220 px of Player start. If any check fails, re-roll with the next seed. On the 20th failure for a run, set Tree probability to 0.28 and set the start clearing to X=29–35 and Y=29–35, then continue re-rolling with the next seed.

## Controls
- While Night.State is Running, W, Up, S, Down, A, Left, and D, Right set the move vector: W or Up adds (0,-1); S or Down adds (0,1); A or Left adds (-1,0); D or Right adds (1,0). If the summed vector length is greater than 1, scale it to length 1.
- Mouse movement sets Player.AimDirection to the angle from Player.X/Y to the mouse in degrees 0–359.
- Touch uses a left-thumb virtual joystick for the same move vector, a right-thumb drag to set Player.AimDirection, and on-screen buttons for Light, Flare, Dash, Interact, and Pause.
- Space: if Player.DashTimer is 0, Player.DashCooldown is 0, and Player.Stamina is at least 30, set Player.DashTimer to 0.25, Player.DashCooldown to 1.2, Player.Stamina to Player.Stamina - 30, Player.StaminaDelay to 1.0, and set Player.DashX/Y to the move vector at 540 px/s if the move vector is nonzero, otherwise to Player.AimDirection at 540 px/s.
- F: if Player.FlashlightOn is false and Player.FlashlightBattery is greater than 0, set Player.FlashlightOn to true; if Player.FlashlightOn is true, set Player.FlashlightOn to false.
- Q: if Tool.Count for Flare is greater than 0, throw a Flare using the Items and Flare rules.
- E: if Player is within 24 px of the Gate tile center, Player.Sigils is 3, and Night.GateOpen is true, set Night.State to Success, Night.ResultTime to Night.DawnTimer, and Night.Cause to None.
- Escape or P: while Night.State is Running, enter the paused screen.
- On the paused screen, Escape resumes; T returns to title.
- On the title screen, Enter or Start begins a new Night with Seed + 1.
- On the result screen, Enter returns to title.

## Movement
- Every second, decrease Player.DashTimer, Player.DashCooldown, Player.StaminaDelay, Player.Invulnerability, and Player.KnockbackTimer by elapsed time, never below 0.
- If Player.StaminaDelay is 0 and Player.Stamina is less than 100, increase Player.Stamina by 20 per second, capped at 100.
- If Player.KnockbackTimer is greater than 0, set Player.VelocityX to Player.KnockbackX and Player.VelocityY to Player.KnockbackY.
- Else if Player.DashTimer is greater than 0, set Player.VelocityX to Player.DashX and Player.VelocityY to Player.DashY.
- Else if the move vector length is greater than 0, set target velocity to move vector times 180 px/s; move Player.VelocityX/Y toward target velocity by 1400 px/s per second, capped at 180 px/s in magnitude.
- Else move Player.VelocityX/Y toward 0 by 2400 px/s per second, capped at 0.
- Move Player.X by Player.VelocityX times elapsed time and Player.Y by Player.VelocityY times elapsed time. Apply X movement only if the new X/Y point is not outside 0–2048 px and not inside a Tree tile; apply Y movement only if the new X/Y point is not outside 0–2048 px and not inside a Tree tile.
- If Player.KnockbackTimer becomes 0, set Player.VelocityX and Player.VelocityY to 0.

## Light and Battery
- While Player.FlashlightOn is true, decrease Player.FlashlightBattery by 1 percent every 2 seconds.
- If Player.FlashlightBattery reaches 0, set Player.FlashlightOn to false and Player.FlashlightBattery to 0.
- While Player.FlashlightOn is true, the player sees a 180 px cone of 70 degrees centered on Player.AimDirection.
- While Player.FlashlightOn is false, the player sees a 60 px circle around Player.X/Y.
- Player visibility affects only what the player sees; Entity detection uses Entity-specific rules.
- While Player.FlashlightOn is true, Wraith detection radius is 300 px. While Player.FlashlightOn is false, Wraith detection radius is 120 px.

## Entities
- A line is clear if the straight segment from an Entity to Player does not pass through a Tree tile.
- Every second, decrease Entity.WanderTimer, Entity.LoseTimer, Entity.AttackTimer, Entity.SlowTimer, and Entity.HitCooldown by elapsed time, never below 0.
- If Entity.State is Wandering: when Entity.WanderTimer is 0, set Entity.WanderX/Y to one of 8 directions times Entity.WanderingSpeed, and set Entity.WanderTimer to 2.0. Set Entity.VelocityX/Y to Entity.WanderX/Y. Move the Entity; if the destination is blocked by a Tree tile or outside the map, choose a new direction immediately.
- If Entity.State is Chasing: set Entity.VelocityX/Y toward Player.X/Y at Entity.Speed; if Entity.SlowTimer is greater than 0, use Entity.Speed times 0.5 instead. Move the Entity; if the destination is blocked, keep the Entity at its current position.
- If Entity.State is Losing: move the Entity away from Player.X/Y at Entity.WanderingSpeed for 2.0 seconds, then set Entity.State to Wandering and Entity.WanderTimer to 2.0.
- Wraith detection: while Wandering, if the line is clear and Player is within 300 px while Player.FlashlightOn is true, set State to Chasing and LoseTimer to 0; if the line is clear and Player is within 120 px while Player.FlashlightOn is false, set State to Chasing and LoseTimer to 0.
- Howler detection: when Player.DashTimer changes from 0 to greater than 0, if distance to Player is 260 px or less, set State to Chasing and LoseTimer to 0.
- Lurker detection: while Wandering, if the line is clear and Player is within 140 px, set State to Chasing and LoseTimer to 0.
- Chasing lose condition: if the Chasing condition is false, increase Entity.LoseTimer by elapsed time. If Entity.LoseTimer reaches the roster lose timer for that Kind, set Entity.State to Losing and Entity.LoseTimer to 0. If the Chasing condition becomes true, set Entity.LoseTimer to 0.
- Contact: if an Entity is within 24 px of Player, Entity.HitCooldown is 0, and Player.Invulnerability is 0, decrease Player.Health by the roster contact damage; if Player.Health reaches 0, set Night.State to Failed, Night.Cause to Death, and Night.ResultTime to Night.DawnTimer. Set Entity.HitCooldown to the roster HitCooldown, set Player.Invulnerability to 1.0, set Player.KnockbackTimer to 0.3, and set Player.KnockbackX/Y to the vector from Entity to Player at the roster knockback speed.
- Lurker teleport: while Chasing, if Entity.AttackTimer is 0, set Entity.AttackTimer to 3.0 and move the Entity 180 px toward Player.X/Y; if that destination is blocked, move it 90 px toward Player.X/Y instead.

## Items and Flare
- If Player is within 24 px of an Item and Item.Taken is false, set Item.Taken to true and apply the roster effect.
- Moon Sigil: increase Player.Sigils by 1; if Player.Sigils becomes 3, set Night.GateOpen to true.
- Battery: set Player.FlashlightBattery to min(100, Player.FlashlightBattery + 40).
- Herb: set Player.Health to min(100, Player.Health + 35).
- Flare: if Tool.Count for Flare is greater than 0, set Tool.Count to 0. Create a Flare at Player.X/Y plus 220 px in Player.AimDirection. If that point is inside a Tree tile, move the point back toward Player in 32 px steps until it is Empty, but no closer than 64 px; if still blocked, place it at Player.X/Y.
- While a Flare exists, every second decrease Flare.Timer by elapsed time.
- While Flare.Timer is greater than 0, for each Entity within Flare.Radius of Flare.X/Y, set Entity.SlowTimer to 2.5 and move the Entity 80 px away from the Flare if that destination is open; if blocked, move it 40 px away.
- When Flare.Timer reaches 0, remove the Flare.

## Waves and Dawn
- Every second, decrease Night.DawnTimer by 1.
- If Night.DawnTimer reaches 0 and Night.State is Running, set Night.State to Failed, Night.Cause to Dawn, and Night.ResultTime to 0.
- For each Wave with Used false, if Night.DawnTimer is less than or equal to 480 minus Wave.TriggerTime, set Wave.Used to true and spawn its entities.
- Spawn entities using offsets in this order: (0,0), (64,0), (-64,0), (0,64). If an offset tile is blocked despite verification, move the spawn to the nearest Empty tile within 128 px.
- Spawn Wraiths first, then Howlers, then Lurkers, assigning new Entity Ids in that order.

# 4. PROGRESSION AND DIFFICULTY
No player upgrades, no permanent unlocks, and no character progression carry between runs. Difficulty grows inside one night: the first 150 seconds contain only the initial 5 entities, and the generator guarantees one Battery within 160 px of start and one Herb within 220 px of start. At 150 seconds, 3 more entities appear; at 300 seconds, 3 more appear; at 420 seconds, 4 more appear, bringing the total to 15. The battery pressure also grows because a full flashlight battery lasts 200 seconds and only 5 Batteries add 200 percent total, so missed pickups make the late night darker. The player is expected to fail if they keep the flashlight on through open areas, dash near Howlers, delay the third Sigil, or ignore the gate after opening it. Recovery comes from Herbs, Batteries, Flare, dash, and the 1.0-second invulnerability window. Failure ends the run and the next run uses a new seed; success ends the run and the next run uses a new seed.

# 5. FEEL
Player walking speed is 180 px/s, dash speed is 540 px/s for 0.25 s, dash cooldown is 1.2 s, dash stamina cost is 30, stamina regenerates 20 per second after a 1.0 s delay, acceleration is 1400 px/s², deceleration is 2400 px/s², and knockback is applied for 0.3 s. These values make walking steady, dash decisive, and immediate recovery short, so a dash is an escape tool rather than continuous speed. Wraiths move at 90 px/s, Howlers at 150 px/s, and Lurkers at 70 px/s; Lurker teleports move 180 px every 3.0 s. Detection radii are 300 px for lit Wraiths, 120 px for unlit Wraiths, 260 px for Howler dash hearing, and 140 px for Lurkers; lose timers are 4 s for Wraiths and Howlers and 5 s for Lurkers. Contact damage is 15, 25, and 30 points, with 100 Health; knockback is 90, 140, and 160 px/s; invulnerability is 1.0 s. The flashlight cone is 180 px wide and 70 degrees, ambient sight is 60 px, battery drain is 1 percent every 2 seconds, and each Battery adds 40 percent. Flare throws 220 px, has a 90 px radius, slows enemies by 0.5 for 2.5 s, and pushes enemies 80 px. Dawn is 480 s. These numbers tune Wraiths as the cost of light, Howlers as the cost of dash, Lurkers as the cost of camping, and flare as the tool that buys a short reset.

# 6. HUD AND SCREENS
State machine: title (shows Seed, one-line objective, control list, and Start) → playing (all gameplay HUD visible) → paused (shows Resume and Quit) → playing; playing → result (success shows Night.ResultTime; failure shows Night.Cause) → title. Title: Enter or Start begins playing. Playing: Escape or P opens paused. Paused: Escape or Resume returns to playing; T or Quit returns to title. Result: Enter returns to title with Seed + 1. Escape does nothing on title or result.

| HUD element | Record field it shows | When visible |
|---|---|---|
| Dawn timer | Night.DawnTimer | playing |
| Health bar | Player.Health | playing |
| Stamina bar | Player.Stamina | playing |
| Battery bar and state | Player.FlashlightBattery, Player.FlashlightOn | playing |
| Sigil counter | Player.Sigils | playing |
| Flare icon | Tool.Count for Flare | playing, dim when Count is 0 |
| Dash cooldown icon | Player.DashCooldown | playing, covered while greater than 0 |
| Objective text | Player.Sigils and Night.GateOpen | playing |
| Compass arrow | nearest Item.X/Y where Kind is Moon Sigil and Taken is false, otherwise Gate tile center | playing |
| Threat count | count of Entities with State Chasing and distance 160 px or less from Player | playing when count is greater than 0 |
| Pause button | Night.State | playing |