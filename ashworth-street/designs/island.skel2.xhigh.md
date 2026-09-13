# 0. SCOPE

## 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| An open world game | Section 1.2, Section 2.1, Section 4.1 |
| Explore an island | Section 3.2, Section 4.1, Section 4.2 |
| Find treasure | Section 4.3, Section 4.6 |
| Playable browser experience | Section 7, Section 8, Section 9 |
| Clear goal and progression | Section 4.3, Section 4.6, Section 11 |
| Challenge and tension | Section 4.2, Section 4.4, Section 4.6 |
| Deterministic debuggable build | Section 2.2, Section 8, Section 9 |
| Audio feedback | Section 6 |
| UI and readability | Section 7 |

## 0.2 Tiers

| Tier | Features |
| --- | --- |
| T1 | Island world, player movement, five treasure caches, five relics, final vault, win and lose states, tide clock, core HUD, deterministic seed |
| T2 | Wraith encounters, machete attack, flare stun, lantern, rope, diver’s bell, weeds, flooded damage, rations, storm timer |
| T3 | Lighthouse beam, particles, screen effects, weather darkening, animated water, wraith ghost trail, clue text, minimap-style compass |
| T4 | Sound mixer, pause menu, accessibility text size, replay seed display, post-game summary |

# 1. CONVENTIONS

## 1.1 Units, axes, frames

- World is a 96 by 96 tile grid.
- One tile is one world unit.
- Pixel scale is 32 pixels per tile on the base render surface.
- X axis increases east.
- Y axis increases south.
- Elevation is a number from 0 to 10.
- Tide level is a number from 0.5 at low tide to 4.0 at high tide.
- Time is in seconds.
- Simulation uses fixed ticks of 1/60 second when running in real time.
- Debug step may use larger tick lengths and must produce identical results for the same input.
- Player speed is 6 tiles per second on dry ground.
- Player speed is 3 tiles per second in shallow water.
- Player collision circle radius is 0.35 tiles.
- Interact radius is 1.25 tiles.
- Camera viewport is 1280 by 720 pixels, clamped to the world bounds.

## 1.2 Important conventions

- The world is one continuous island. No level transitions occur.
- The island is procedurally generated from one seed, but all named landmarks and treasure caches use fixed coordinates so tests and clues are stable.
- All randomness comes from one seeded 32-bit PRNG. The PRNG is reseeded only by `seed(n)`.
- The PRNG is used for terrain noise, pebble placement, grass tufts, palm scatter, and minor visual variation. It is not used for gameplay outcomes.
- Gameplay state is a single shared context object consumed by all modules.
- Game phases are `title`, `playing`, `paused`, `win`, and `lose`.
- Caches are interactable markers. They are not solid objects.
- Some caches are hidden in dark tiles and require the lantern to discover or open.
- Some caches require low tide, a rope, a diver’s bell, cleared weeds, or the vault key.
- The final vault requires five relics and the vault key.
- The tide cycle is 70 seconds:
  - 0 to 25 seconds: low tide, level 0.5
  - 25 to 35 seconds: rising tide, level 0.5 to 4.0
  - 35 to 60 seconds: high tide, level 4.0
  - 60 to 70 seconds: falling tide, level 4.0 to 0.5
- Storm timer starts at 700 seconds and counts down. Reaching zero causes a loss.
- Health starts at 100. Reaching zero causes a loss.
- Relics are not stackable. They are listed by id.
- Tools are booleans.
- Flares and rations are counts.
- Wraiths are temporary enemies tied to caches or the vault.
- Wraiths do not persist between cache encounters unless the player fails to kill or evade them. Each wraith despawns 30 seconds after spawning if not killed.
- The player may open caches in any order, but tools gate certain caches.

# 2. CONTRACTS

## 2.1 Module layout

| Module | Responsibility |
| --- | --- |
| state | Owns the shared game context, phase, time, seed, tide, storm, player, items, relics, caches, wraiths, and world references |
| rng | Provides one seeded PRNG and helper functions |
| worldgen | Builds the island, elevation, tile types, landmarks, caches, and fixed positions |
| player | Handles movement, collision, health, actions, facing, and action cooldowns |
| tide | Calculates tide level, phase, flooding, and water damage |
| caches | Handles discovery, requirements, opening, rewards, and cache wraith summons |
| wraith | Handles wraith spawning, movement, attacking, stuns, death, and despawn |
| tools | Applies tool effects: machete swing, lantern reveal, rope crossing, bell protection, flares, rations |
| ui | Builds DOM screens, HUD, buttons, prompts, and input bindings |
| audio | Generates all sounds with Web Audio API and plays them by name |
| debug | Installs `window.__game` with deterministic control functions |

## 2.2 Global context

The shared context is a plain mutable object:

```js
GameState = {
  phase: "title",
  time: 0,
  seed: 0,
  world: {
    width: 96,
    height: 96,
    tiles: [],
    landmarks: [],
    landmarksByName: {}
  },
  tide: {
    cycleTime: 0,
    level: 0.5,
    phase: "low"
  },
  storm: {
    remaining: 700,
    warning: false
  },
  player: {
    x: 48,
    y: 12,
    facing: "east",
    health: 100,
    maxHealth: 100,
    moveX: 0,
    moveY: 0,
    speed: 6,
    inWater: false,
    hurtTimer: 0,
    swingCooldown: 0
  },
  tools: {
    machete: true,
    lantern: false,
    rope: false,
    bell: false
  },
  items: {
    flares: 1,
    rations: 1
  },
  relics: [],
  keys: {
    vaultKey: false
  },
  caches: {},
  wraiths: [],
  crown: false,
  loseCause: null
}
```

`getState()` returns this structure as plain data, excluding function references and the PRNG object.

## 2.3 Module specifics

### rng

- `next()` returns a number from 0 to 1.
- `int(min, max)` returns an integer from min to max inclusive.
- `range(min, max)` returns a number from min to max.
- `pick(items)` returns one item.
- `chance(p)` returns true with probability p.

### worldgen

- `generate(seed)` returns a world object.
- Fixed landmarks:
  - `shack` at tile 48, 12
  - `beach_cache` at tile 60, 20
  - `grove_cache` at tile 72, 38
  - `wreck_cache` at tile 48, 82
  - `cave_cache` at tile 22, 56
  - `ruins_cache` at tile 74, 18
  - `vault` at tile 30, 12
  - `lighthouse` at tile 56, 60
- Tile record:
  - `x`
  - `y`
  - `type`: one of `deep`, `shallow`, `sand`, `grass`, `palm`, `rock`, `ruin`, `cave`, `wreck`, `gap`, `shack`, `lighthouse`, `vault`
  - `elevation`
  - `blocked`
  - `dark`
  - `floodDamage`
- Fixed tile rules:
  - Shack tile is `shack`, elevation 3, not blocked.
  - Beach cache tile is `sand`, elevation 2, not blocked.
  - Grove cache tile is `grass`, elevation 3, not blocked.
  - Grove weeds are three adjacent tiles: 71,38; 73,38; 72,37. They are not solid but interactable.
  - Wreck cache tile is `wreck`, elevation 1, not blocked, floodDamage 8.
  - Cave entrance and cache tile are `cave`, elevation 0, not blocked if bell is owned or if the tile is the entrance, dark true, floodDamage 15.
  - Ruins cache tile is `ruin`, elevation 4, not blocked, dark true.
  - Ruins gap is four tiles wide between tile 70,18 and tile 74,18. Gap tiles are `gap`, blocked unless the player owns rope.
  - Vault tile is `vault`, elevation 6, not blocked.
  - Lighthouse tile is `lighthouse`, elevation 6, not blocked.
  - Deep water tiles are blocked.
  - Shallow water tiles are passable at reduced speed.
  - Rock tiles are blocked.

### player

- `update(dt)` moves the player using persistent `moveX` and `moveY`.
- Movement is normalized so diagonal speed does not exceed the current speed.
- Collision checks the target tile.
- If target tile is blocked, movement is canceled.
- If target tile is shallow or flooded, speed is 3.
- If player is in a flooded tile and `floodDamage > 0`, health decreases by `floodDamage * dt` unless protected by bell in cave tiles.
- `interact()` opens the nearest eligible cache or clears a weed if the player is adjacent to a weed.
- `attack()` performs a machete swing in the facing direction.
  - Range: 1.25 tiles.
  - Arc: 120 degrees.
  - Damage: 1.
  - Cooldown: 0.6 seconds.
- `useFlare()` consumes one flare.
  - Stuns the nearest wraith within 6 tiles for 3 seconds.
  - Reveals hidden caches within 6 tiles for 5 seconds by setting `discovered` to true.
- `eatRation()` consumes one ration and restores 30 health over 2 seconds.

### tide

- `update(dt)` advances `cycleTime` modulo 70.
- Tide level is calculated by the 70-second cycle.
- A tile is flooded if `tide.level > tile.elevation`.
- A tile is deep blocked if tile type is `deep` or if `tide.level - tile.elevation > 2.5` on `shallow` or `wreck` tiles.
- Flood damage is applied only when the player stands on a flooded tile with `floodDamage > 0`.

### caches

Cache record fields:

```js
{
  id: "cache_beach",
  name: "Shell Beach Cache",
  x: 60,
  y: 20,
  discovered: false,
  opened: false,
  weeds: 0,
  weedsCleared: true,
  requiresLantern: false,
  requiresBell: false,
  requiresRope: false,
  requiresLowTide: false,
  rewardRelic: "relic_1",
  rewardTool: "lantern",
  rewardFlares: 0,
  rewardRations: 1,
  rewardVaultKey: false,
  wraithKind: "normal",
  wraithSpawn: { x: 57, y: 20 }
}
```

Cache roster:

| Cache | Position | Requirements | Relic | Reward |
| --- | --- | --- | --- | --- |
| `cache_beach` | 60, 20 | None | `relic_1` | Lantern, 1 ration |
| `cache_grove` | 72, 38 | Weeds cleared | `relic_2` | Rope, 1 flare, 1 ration |
| `cache_wreck` | 48, 82 | Low tide, lantern | `relic_3` | Diver’s bell, 1 flare, 1 ration |
| `cache_cave` | 22, 56 | Bell, lantern | `relic_4` | Vault key, 1 flare |
| `cache_ruins` | 74, 18 | Rope, lantern | `relic_5` | 1 flare, 1 ration |
| `vault` | 30, 12 | 5 relics, vault key | `crown` | Final wraith, win after defeating final wraith |

- `interact()` returns a plain result describing the action.
- Opening a cache:
  - Adds relic to `relics`.
  - Applies tool reward.
  - Adds flares and rations.
  - Sets `vaultKey` if rewarded.
  - Spawns one wraith at the cache’s spawn point unless the cache is the vault.
  - Opening the vault spawns the final wraith.

### wraith

Wraith record:

```js
{
  id: "wraith_cache_beach",
  kind: "normal",
  x: 57,
  y: 20,
  hp: 4,
  maxHp: 4,
  stunTimer: 0,
  attackCooldown: 0,
  alive: true,
  age: 0
}
```

- Normal wraith:
  - HP 4.
  - Speed 4.5 tiles per second.
  - Attack damage 20.
  - Attack range 1.0 tile.
  - Attack cooldown 1.0 second.
- Final wraith:
  - HP 8.
  - Speed 5.0 tiles per second.
  - Attack damage 25.
  - Attack range 1.25 tiles.
  - Attack cooldown 0.9 seconds.
- Wraith despawns after 30 seconds if alive.
- Final wraith does not despawn.
- If final wraith dies, the player receives the crown and the phase becomes `win`.

### tools

- `machete` allows weed clearing and attacks.
- `lantern` reveals dark caches and dark tile lighting.
- `rope` makes gap tiles passable.
- `bell` prevents flooded damage in cave tiles.
- Flare use is gated by `items.flares > 0`.
- Ration use is gated by `items.rations > 0` and health below max.

### ui

- All UI is DOM and CSS.
- UI reads state and writes input through the player module.
- UI does not store gameplay state.
- Screens:
  - Title
  - Help
  - Playing
  - Pause
  - Win
  - Lose

### audio

- Audio starts after first user gesture or `start()`.
- All sounds are generated by Web Audio API.
- No external audio assets.
- Sound name keys are fixed.

### debug

- `window.__game` is installed after boot.
- All calls are synchronous.
- All calls return plain data.
- No call schedules delayed behavior.
- `step(dt, n)` advances simulation by `n` ticks of `dt` seconds and draws once.
- `setTime(t)` advances simulation to `t` seconds without drawing.
- `seed(n)` reseeds the PRNG and rebuilds the world, resetting to title phase.

# 3. VISUAL SPEC

The game is a top-down painterly island with a warm, sunlit palette: turquoise shallows, pale sand, dense jungle green, weathered stone, and a pale blue sky glow. The player is a small salvage diver visible against the terrain. Treasure caches appear as glowing sand mounds, broken ruins, a sunken ship, a dark cave mouth, and a rune-marked vault. The tide visibly rises and falls, flooding low shelves and revealing wrecks. Wraiths are translucent blue-green ghosts with soft trailing auras. The final vault sits on a cliff and glows when the key and relics are present. As the storm timer nears the end, the scene darkens, clouds thicken, and the lighthouse beam becomes the strongest light source.

Lighting:

- Base ambient light is warm daylight.
- Water has a moving shimmer pattern.
- Dark tiles are drawn with a heavy blue-black shadow.
- The lantern creates a 6-tile radial glow around the player when owned and the player is on a dark tile.
- The lighthouse emits a rotating beam every 4 seconds.
- Flares create a bright white-orange burst and a 3-second glow ring.
- Wraiths emit a soft green self-light.
- Storm warning adds a dark blue overlay and reduces ambient brightness.
- Low tide water is brighter cyan.
- High tide water is deeper teal.
- The final vault door has a rune glow when the player has all relics and the key.

## 3.1 Tile and landmark look

| Tile or object | Appearance | Palette | Motion or effect |
| --- | --- | --- | --- |
| Deep water | Dark blue with wave lines | #123B5A, #0E2F4A | Slow diagonal wave offset |
| Shallow water | Turquoise with foam flecks | #39B7C9, #7EDCE6 | Shimmer highlight sweep |
| Sand | Pale beige with pebbles | #E8D5A3, #D6BE86 | Static |
| Grass | Green tufts and patches | #5FA35B, #3E7C43 | Subtle sway |
| Palm | Top-down canopy with trunk shadow | #4E8A4F, #2F5D33 | Canopy sway |
| Rock | Grey boulders | #8A8D93, #64676E | Static |
| Ruin | Broken columns and stone floor | #B7A88D, #8F7E63 | Dust particles |
| Cave | Dark opening, wet stone rim | #1B2430, #394457 | Inner fog pulse |
| Wreck | Broken ship ribs and dark wood | #7A5A3C, #4C3526 | Foam at high tide |
| Gap | Chasm with rope anchor stones | #2A2622, #5B4B3A | Rope shimmer when owned |
| Shack | Small wooden hut | #8C6B4A, #5C4430 | Door light |
| Lighthouse | White tower, red top, base rocks | #F2F5F7, #D34B4B | Rotating beam |
| Vault | Stone door with rune ring | #7B7E86, #4D4F57 | Rune glow when ready |
| Cache marker | Sand mound or rune stone | #F4E7C5, #FFC64A | Pulse when discovered |
| Weeds | Dense brush patch | #3F6D3A, #2B4D28 | Sway |
| Wraith | Translucent ghost with tattered cloak | #9BEDE0, #59C7B6 | Bob and trail |

## 3.2 Island layout and camera

- The island is a roughly oval landmass in the center of a 96 by 96 grid.
- Beaches ring the island.
- Jungle occupies the east and center.
- Rock outcrops occupy the northwest and west.
- Ruins sit on a high plateau in the northeast.
- The cave is on the west coast.
- The wreck is on the southern drowned shelf.
- The shack is on the northern beach.
- The vault is on the northwest cliff.
- The lighthouse is on the southern central ridge.
- Camera follows the player with linear interpolation.
- Camera clamps so the render surface does not show beyond the world bounds.
- Camera zoom is fixed.
- The player is centered unless near a world edge.

# 4. GAMEPLAY SPEC

The most important part of play is the tension between exploration and tide. The player is not racing against a countdown alone; the island itself opens and closes. Low tide reveals the wreck and other low caches, high tide punishes slow movement, and wraiths punish careless digging. The tactile core is discovering a cache, clearing its obstacle, receiving a relic or tool, and using that new tool to reach the next place. The final vault is the reward, but the storm timer and final wraith ensure the ending is earned.

## 4.1 Player Controller

- Movement:
  - WASD or arrow keys set a persistent move direction.
  - Diagonal input is normalized.
  - The player faces the last non-zero movement direction.
- Camera:
  - Follows the player.
  - Smooth follow factor is 0.15 per tick at 60 ticks per second.
- Collision:
  - Circle against tile grid.
  - Deep water, rock, gap without rope, cave interior without bell, and solid ruin walls block movement.
  - Weeds do not block movement but block cache interaction until cleared.
- Actions:
  - E interact
  - Space or J machete swing
  - Q use flare
  - R eat ration
  - Esc or P pause
- Stats:
  - Health max 100.
  - Health regenerates 2 per second after 3 seconds without damage.
  - Wraith hit damage 20 for normal, 25 for final.
  - Flood damage is tile-dependent.

## 4.2 Tide and flooding

- Tide cycle is 70 seconds.
- Low tide exposes the drowned shelf at the wreck cache.
- High tide floods the southern shelf and low sand.
- The wreck cache can only be opened during low tide.
- Standing in flooded water causes health drain.
- Flood damage rates:
  - Shallow water: 8 per second.
  - Wreck shelf: 8 per second.
  - Cave flooded chamber: 15 per second unless the player owns the bell.
- Low tide gives the player 25 seconds to open the wreck and leave.
- Rising tide takes 10 seconds, creating a warning window.
- High tide lasts 25 seconds.
- Falling tide takes 10 seconds.

## 4.3 Caches, relics, and final vault

- The player begins with a machete, one flare, and one ration.
- The player must collect five relics:
  - `relic_1`
  - `relic_2`
  - `relic_3`
  - `relic_4`
  - `relic_5`
- Tool progression:
  - Start: machete.
  - Beach cache gives lantern.
  - Grove cache gives rope.
  - Wreck cache gives diver’s bell.
  - Cave cache gives vault key.
  - Ruins cache gives the final relic.
- Final vault:
  - Requires all five relics.
  - Requires vault key.
  - Opens only after both are present.
  - Summons final wraith.
  - Defeating final wraith grants the crown and wins the game.
- Cache clues:
  - Each relic shows a short line of text pointing to the next area.
  - Clues are flavor and do not block gameplay, but they reinforce the treasure hunt.

## 4.4 Wraiths

- Wraiths are the main opponent.
- Each cache, except the vault, spawns one normal wraith when opened.
- The vault spawns one final wraith.
- Wraith behavior:
  - Stunned by flare for 3 seconds.
  - Moves toward player when not stunned.
  - Attacks when within range.
  - Dies when HP reaches zero.
  - Despawns after 30 seconds unless final.
- Combat rule:
  - Player machete damage is 1.
  - Normal wraith HP is 4.
  - Final wraith HP is 8.
  - Player can kite because player speed is higher than wraith speed.
- Wraith visual feedback:
  - Hit flash.
  - Death burst.
  - Stun ring.
  - Attack lurch.

## 4.5 Items, tools, and consumables

| Item | Start | Sources | Use |
| --- | --- | --- | --- |
| Machete | Yes | None | Attack, clear weeds |
| Lantern | No | `cache_beach` | Reveal dark caches, light dark tiles |
| Rope | No | `cache_grove` | Cross gap tiles |
| Diver’s bell | No | `cache_wreck` | Prevent cave flood damage |
| Flare | 1 | Grove, wreck, cave, ruins | Stun wraith, reveal hidden caches |
| Ration | 1 | Beach, grove, wreck, ruins | Restore 30 health |
| Vault key | No | `cache_cave` | Opens final vault with relics |
| Relic | 0 | One per cache | Required for final vault |

## 4.6 Win and lose conditions

- Win:
  - Open final vault with five relics and vault key.
  - Defeat final wraith.
  - Receive crown.
  - Phase becomes `win`.
- Lose by health:
  - Player health reaches 0.
  - Phase becomes `lose`.
  - `loseCause` is `health`.
- Lose by storm:
  - Storm timer reaches 0 before win.
  - Phase becomes `lose`.
  - `loseCause` is `storm`.
- Post-game summary shows:
  - Relics found
  - Time taken
  - Wraiths defeated
  - Cause of loss, if applicable

# 5. CHARACTERS

The player is Marisol, a practical salvage diver from a nearby fishing town. She is not a warrior; she is quick, curious, and stubborn. Her visual design should read clearly against sand and jungle: bright oilskin coat, dark boots, a machete on her back, and a small satchel that glows faintly when it contains relics. The wraiths are salt spirits born from old graves, drowned crews, and buried promises. They are not angry in a human way; they drift, lunge, and fade. Their design should feel cold, wet, and slightly wrong: pale blue-green translucency, loose tattered edges, and a soft inner glow. The final wraith is larger, crowned with broken coral, and carries a heavier presence.

## 5.1 Animation

- Player:
  - Idle: subtle breathing and satchel sway.
  - Walk: two-frame leg cycle in four directions.
  - Attack: machete swing arc.
  - Hurt: brief red flash and stagger.
  - Use flare: arm raises, flare bursts.
  - Eat ration: small crouch and hand motion.
- Wraith:
  - Idle: vertical bob and cloak ripple.
  - Move: drifting lean.
  - Attack: quick lurch and claw extend.
  - Stun: spin and dim.
  - Death: burst into salt particles.
- Cache marker:
  - Hidden: low opacity.
  - Discovered: pulse.
  - Opened: fade and rune collapse.
- Vault:
  - Locked: dark runes.
  - Ready: glowing runes.
  - Opened: door slides down and crown rises.

# 6. AUDIO

All audio is generated with Web Audio API.

| Sound | Recipe | Rule |
| --- | --- | --- |
| water_ambient | Looping white noise, lowpass 300 Hz, gain 0.05 plus 0.10 multiplied by tide level divided by 4 | Always during play |
| footstep | Noise burst, 0.06 second, bandpass 800 Hz, gain 0.18, fast decay | Every 0.35 seconds while moving on dry ground |
| splash | Noise burst, 0.25 second, lowpass 400 Hz, gain 0.28 | When player enters flooded water |
| machete_swing | Sawtooth sweep 220 Hz to 80 Hz, 0.12 second, gain 0.32 | Player attack |
| wraith_hit | Square wave, 160 Hz, 0.08 second, gain 0.22 | Machete hits wraith |
| wraith_die | Sine sweep 420 Hz to 60 Hz, 0.35 second, gain 0.30 | Wraith HP reaches zero |
| cache_open | Triangle notes 660, 990, 1320 Hz, 0.05 seconds each, gain 0.25 | Cache opened |
| relic_glint | Sine 1046 Hz, 0.15 second, gain 0.20 | Relic added |
| flare_burst | Noise burst 0.30 second, highpass 2000 Hz, plus sine 1200 Hz 0.20 second, gain 0.28 | Flare used |
| ration_chew | Sine 80 Hz, 0.08 second, gain 0.20, soft decay | Ration consumed |
| tide_change | Noise swell 0.80 second, lowpass 500 Hz, gain rises then falls | Tide phase changes |
| thunder | Noise 1.20 second, lowpass 120 Hz, gain 0.40 | Storm warning and random storm strikes |
| win_chord | Triangle notes 523, 659, 784, 1046 Hz, 0.12 seconds apart, gain 0.30 | Phase becomes win |
| lose_drone | Sine 110 Hz to 40 Hz over 2 seconds, gain 0.35 | Phase becomes lose |

# 7. UX

All UI is HTML and CSS. No gameplay UI is drawn on the render surface.

| UI piece | Location | Purpose |
| --- | --- | --- |
| Title screen | Full screen | Show title, subtitle, Begin button, How to Play button, seed display |
| Help overlay | Centered panel | Show controls, tool icons, tide explanation, cache list |
| Health bar | Top left | Shows player health as a red bar |
| Tide clock | Top center | Shows current tide phase and seconds until next phase |
| Storm timer | Top center | Counts down total storm time; changes color when warning is active |
| Relic pips | Top right | Five slots, filled as relics are found |
| Vault key icon | Top right | Appears when vault key is owned |
| Tool icons | Bottom left | Machete, lantern, rope, bell; dim when absent, bright when owned |
| Consumables | Bottom right | Flare and ration counts |
| Interaction prompt | Bottom center | Shows the nearest available action, such as `E Open cache` or `E Clear weeds` |
| Clue toast | Center lower third | Shows short relic clue text for 4 seconds |
| Wraith warning | Center upper third | Brief red warning when a wraith is summoned |
| Pause menu | Centered panel | Resume, Restart, Help |
| Win screen | Full screen | Treasure summary, time, relics, Play Again |
| Lose screen | Full screen | Cause of loss, relics found, Retry |
| Storm warning banner | Top edge | Appears when 100 seconds remain, pulses dark blue |
| Tide warning banner | Bottom edge | Appears during rising tide and falling tide |

# 8. DEBUG API

`window.__game` exposes these functions.

| Call | What it does | Returns |
| --- | --- | --- |
| `start()` | Enters play from title | `{ phase, time }` |
| `step(dt, n)` | Advances n ticks of dt seconds, then draws once | `{ time, phase }` |
| `setTime(t)` | Advances simulation to t seconds without drawing | `{ time, phase }` |
| `seed(n)` | Reseed one random source and rebuild generated world, resets to title | `{ seed, phase }` |
| `getState()` | Returns all gameplay records as plain data | full state object |
| `move(x, y)` | Sets persistent player move direction, values from -1 to 1 | `{ moveX, moveY }` |
| `stop()` | Sets player move direction to zero | `{ moveX, moveY }` |
| `interact()` | Performs the nearest eligible interact action | `{ action, cacheId, relic, tool, opened }` |
| `attack()` | Performs one immediate machete swing | `{ swing, hit, damage, wraithId }` |
| `useFlare()` | Uses one flare if available | `{ used, flares, stunnedId, stunTimer }` |
| `eatRation()` | Uses one ration if available and health is below max | `{ ate, health, rations }` |
| `setPlayerPos(x, y)` | Places player directly on a tile | `{ x, y }` |
| `setWraithPos(id, x, y)` | Places a wraith directly | `{ id, x, y }` |
| `spawnWraith(kind, x, y)` | Spawns a wraith of kind normal or final at a place | `{ id, kind, hp }` |
| `damageWraith(id, n)` | Applies n damage to a wraith | `{ id, hp, alive, win }` |
| `clearWraiths()` | Removes all wraiths | `{ count }` |
| `setHealth(h)` | Sets player health directly | `{ health }` |
| `setFlares(n)` | Sets flare count directly | `{ flares }` |
| `setRations(n)` | Sets ration count directly | `{ rations }` |
| `setTide(t)` | Sets tide cycle time to t seconds within the 70-second cycle | `{ cycleTime, level, phase }` |
| `setStorm(t)` | Sets storm remaining time directly | `{ remaining, warning }` |
| `clearWeeds(cacheId)` | Clears weeds for a cache | `{ cacheId, weeds }` |
| `giveTool(tool)` | Gives a tool directly: `lantern`, `rope`, or `bell` | `{ tools }` |
| `openCache(cacheId)` | Forces a cache open if requirements are met | `{ cacheId, opened, relic, tool, wraithSpawned }` |
| `setPhase(name)` | Sets phase directly to `title`, `playing`, `paused`, `win`, or `lose` | `{ phase }` |

# 9. TESTS

All checks use only calls listed in section 8.

1. After `seed(7)`, `start()`, `getState()`:
   - `phase` is `playing`
   - `time` is 0
   - `seed` is 7
   - `player.x` is 48
   - `player.y` is 12
   - `player.health` is 100
   - `tide.level` is 0.5
   - `tide.phase` is `low`
   - `storm.remaining` is 700
   - `tools.machete` is true
   - `tools.lantern` is false
   - `items.flares` is 1
   - `items.rations` is 1
   - `relics.length` is 0
   - `wraiths.length` is 0
   - `caches.cache_beach.opened` is false

2. After `setPlayerPos(48, 12)`, `move(1, 0)`, `step(1, 1)`, `getState()`:
   - `time` is 1
   - `player.x` is 54.0 within 0.001
   - `player.y` is 12

3. After `setPlayerPos(60, 20)`, `interact()`, `getState()`:
   - `interact` return has `action` equal to `open_cache`
   - `interact` return has `cacheId` equal to `cache_beach`
   - `interact` return has `relic` equal to `relic_1`
   - `interact` return has `tool` equal to `lantern`
   - `caches.cache_beach.opened` is true
   - `relics` includes `relic_1`
   - `tools.lantern` is true
   - `items.rations` is 2
   - `wraiths.length` is 1
   - `wraiths[0].id` is `wraith_cache_beach`
   - `wraiths[0].hp` is 4

4. After `setWraithPos("wraith_cache_beach", 60, 20)`, `attack()`, `getState()`:
   - `attack` return has `hit` true
   - `attack` return has `damage` equal to 1
   - `wraiths[0].hp` is 3

5. After `useFlare()`, `getState()`:
   - `useFlare` return has `used` true
   - `items.flares` is 0
   - `wraiths[0].stunTimer` is 3.0
   - `wraiths[0].alive` is true

6. After `clearWraiths()`, `getState()`:
   - `wraiths.length` is 0

7. After `setHealth(100)`, `setTide(35)`, `setPlayerPos(48, 82)`, `step(0.5, 1)`, `getState()`:
   - `tide.level` is 4.0
   - `tide.phase` is `high`
   - `player.health` is 96.0
   - `player.inWater` is true

8. After `setTide(0)`, `setPlayerPos(48, 82)`, `interact()`, `getState()`:
   - `interact` return has `cacheId` equal to `cache_wreck`
   - `interact` return has `relic` equal to `relic_3`
   - `interact` return has `tool` equal to `bell`
   - `caches.cache_wreck.opened` is true
   - `relics` includes `relic_3`
   - `tools.bell` is true
   - `items.flares` is 1
   - `wraiths.length` is 1
   - `wraiths[0].id` is `wraith_cache_wreck`

9. After `setPlayerPos(72, 38)`, `interact()`:
   - `interact` return has `action` equal to `blocked_weeds`
   - `interact` return has `opened` false
   - `caches.cache_grove.opened` is false
   - `caches.cache_grove.weeds` is 3
   Then after `clearWeeds("cache_grove")`, `interact()`, `getState()`:
   - `clearWeeds` return has `weeds` equal to 0
   - `interact` return has `cacheId` equal to `cache_grove`
   - `interact` return has `relic` equal to `relic_2`
   - `interact` return has `tool` equal to `rope`
   - `caches.cache_grove.opened` is true
   - `relics` includes `relic_2`
   - `tools.rope` is true
   - `items.flares` is 2
   - `items.rations` is 3

10. After `clearWraiths()`, `setPlayerPos(22, 56)`, `interact()`, `clearWraiths()`, `getState()`:
    - `interact` return has `cacheId` equal to `cache_cave`
    - `interact` return has `relic` equal to `relic_4`
    - `caches.cache_cave.opened` is true
    - `relics` includes `relic_4`
    - `keys.vaultKey` is true
    - `items.flares` is 3
    - `wraiths.length` is 0

11. After `setPlayerPos(74, 18)`, `interact()`, `clearWraiths()`, `getState()`:
    - `interact` return has `cacheId` equal to `cache_ruins`
    - `interact` return has `relic` equal to `relic_5`
    - `caches.cache_ruins.opened` is true
    - `relics.length` is 5
    - `items.flares` is 4
    - `items.rations` is 4
    - `wraiths.length` is 0

12. After `setPlayerPos(30, 12)`, `interact()`, `damageWraith("wraith_vault", 8)`, `getState()`:
    - `interact` return has `cacheId` equal to `vault`
    - `wraiths.length` is 1
    - `wraiths[0].id` is `wraith_vault`
    - `wraiths[0].hp` is 8
    - `damageWraith` return has `alive` false
    - `damageWraith` return has `win` true
    - `phase` is `win`
    - `crown` is true
    - `loseCause` is null

13. After `seed(7)`, `start()`, `setStorm(0)`, `step(0.1, 1)`, `getState()`:
    - `phase` is `lose`
    - `loseCause` is `storm`
    - `storm.remaining` is 0

14. After `seed(7)`, `start()`, `setHealth(0)`, `step(0.001, 1)`, `getState()`:
    - `phase` is `lose`
    - `loseCause` is `health`
    - `player.health` is 0

15. After `seed(7)`, `start()`, `setHealth(50)`, `eatRation()`, `getState()`:
    - `eatRation` return has `ate` true
    - `player.health` is 80
    - `items.rations` is 0

## SCREENSHOTS

| Screen | Visible state | What a person must see |
| --- | --- | --- |
| Title | `phase` is `title` | Island silhouette, title text, Begin button, How to Play button, seed number |
| Help | Help overlay open | Controls list, tool icons, tide explanation, cache objectives |
| Play Low Tide | Low tide, player near beach | Turquoise shallow water, sand marker pulse, player at northern beach, HUD shows one relic after beach cache |
| Wraith Encounter | Wraith spawned near beach cache | Translucent green ghost near cache, flare glow after `useFlare`, stun ring around wraith |
| High Tide Flood | Tide high, player at wreck shelf | Water covers wreck shelf, player is in water, health bar decreasing, tide clock shows high |
| Wreck Low Tide | Tide low, player at wreck cache | Exposed ship ribs, cache marker visible, bell icon appears after opening |
| Grove Weeds | Player at grove cache before clearing | Dense brush around cache, prompt says clear weeds, machete icon active |
| Final Vault | Player at vault with relics and key | Vault runes glow, prompt says open vault, final wraith appears after opening |
| Win | `phase` is `win` | Crown icon, treasure summary, time taken, Play Again button |
| Lose Storm | `phase` is `lose`, cause storm | Dark storm overlay, lose screen says the storm took the island, Retry button |
| Lose Health | `phase` is `lose`, cause health | Red-tinted lose screen, cause says Marisol drowned or was overwhelmed, Retry button |

# 10. BUILD ORDER

1. Create the shared state object and phase flow.
2. Create the seeded PRNG and deterministic world generation.
3. Generate the island tiles, fixed landmarks, and cache positions.
4. Add the render loop, camera, tile drawing, and player movement.
5. Add basic HUD, title screen, and input controls.
6. Add cache discovery, interaction, relics, and tool rewards.
7. Add final vault and win condition.
8. Add tide system, flooding, and wreck cache timing.
9. Add wraith spawning, movement, attack, stun, and death.
10. Add machete attack, flares, rations, weeds, rope, bell, and lantern rules.
11. Add storm timer and lose conditions.
12. Add audio generation and sound triggers.
13. Add visual lighting, particles, wraith trail, lighthouse beam, and storm darkening.
14. Add help, pause, win, and lose screens.
15. Add debug API.
16. Run all numbered tests and screenshot checks.

# 11. DEFINITION OF DONE

## Core loop

- Player can start from title without a physical click through debug.
- Player can move in all directions.
- Player can open all five caches.
- Player can collect all five relics.
- Player can receive lantern, rope, bell, vault key, flares, and rations.
- Player can open final vault with five relics and vault key.
- Player can win by defeating final wraith.
- Player can lose by health.
- Player can lose by storm.

## World

- World is 96 by 96 tiles.
- All fixed landmarks exist at their stated coordinates.
- Deep water blocks movement.
- Shallow water slows movement.
- Rock tiles block movement.
- Gap tiles block movement unless rope is owned.
- Cave flooded tiles damage player unless bell is owned.
- Dark tiles require lantern for cache discovery and opening.
- Wreck cache only opens during low tide.

## Tide

- Tide cycle is 70 seconds.
- Low tide level is 0.5.
- High tide level is 4.0.
- Tide phase changes correctly.
- Flood damage applies in flooded tiles.
- Wreck shelf is exposed at low tide and flooded at high tide.

## Combat and tools

- Machete swing has range, damage, and cooldown.
- Normal wraith has HP 4.
- Final wraith has HP 8.
- Flare stuns wraith for 3 seconds.
- Flare reveals hidden caches nearby.
- Lantern reveals dark caches.
- Rope allows crossing gap tiles.
- Bell prevents cave flood damage.
- Ration restores 30 health.
- Weed clearing is required for grove cache.

## UX

- Title screen works.
- Help overlay works.
- HUD shows health, tide, storm, relics, tools, flares, rations.
- Interaction prompt appears correctly.
- Pause works.
- Win screen works.
- Lose screen shows correct cause.
- UI is HTML and CSS only.

## Audio

- Water ambient plays during play.
- Footsteps play while moving.
- Splash plays when entering water.
- Machete, wraith hit, wraith death, cache open, relic, flare, ration, tide change, thunder, win, and lose sounds play.
- All audio is generated with Web Audio API.

## Determinism and debug

- `window.__game` exists.
- `seed(n)` rebuilds world deterministically.
- `step(dt, n)` advances without real-time waiting.
- `setTime(t)` advances without drawing.
- `getState()` returns plain data.
- Movement input persists until changed.
- All numbered tests pass.
- All screenshot checks pass.

## Polish

- Camera follows player smoothly.
- Tide visual is obvious.
- Storm warning is visible.
- Wraith has clear visual feedback.
- Cache markers are readable.
- Tool icons update immediately.
- Clue text appears after each relic.
- Final vault glows when ready.

# A. SANITY

- Every field read or written by a rule is on a record:
  - Player fields used: `x`, `y`, `facing`, `health`, `moveX`, `moveY`, `speed`, `inWater`, `hurtTimer`, `swingCooldown`.
  - Tide fields used: `cycleTime`, `level`, `phase`.
  - Storm fields used: `remaining`, `warning`.
  - Cache fields used: `id`, `x`, `y`, `discovered`, `opened`, `weeds`, `weedsCleared`, `requiresLantern`, `requiresBell`, `requiresRope`, `requiresLowTide`, `rewardRelic`, `rewardTool`, `rewardFlares`, `rewardRations`, `rewardVaultKey`, `wraithKind`, `wraithSpawn`.
  - Wraith fields used: `id`, `kind`, `x`, `y`, `hp`, `maxHp`, `stunTimer`, `attackCooldown`, `alive`, `age`.
  - Tile fields used: `x`, `y`, `type`, `elevation`, `blocked`, `dark`, `floodDamage`.
  - Result: closes.

- Every place, thing, or kind named by a rule is placed by a generator or roster:
  - Shack, beach cache, grove cache, wreck cache, cave cache, ruins cache, vault, lighthouse, gaps, weeds, normal wraith, final wraith, relics, tools, flares, rations, and crown are all listed in the worldgen and cache roster.
  - Result: closes.

- Consumable totals against core loop demand:
  - Start flares: 1.
  - Cache flare rewards: grove 1, wreck 1, cave 1, ruins 1.
  - Total flares: 5.
  - Wraith encounters: five cache wraiths plus one final wraith, six total.
  - Flares are optional because wraiths can be defeated by machete, and total flares are enough to stun at least all cache wraiths if the player chooses.
  - Start rations: 1.
  - Cache ration rewards: beach 1, grove 1, wreck 1, ruins 1.
  - Total rations: 5.
  - Health max is 100, wraith hits are 20 or 25, flood damage is 8 to 15 per second, health regenerates 2 per second after 3 seconds, and each ration restores 30.
  - Result: closes.

- Timing pairs:
  - Low tide lasts 25 seconds.
  - Travel from beach cache to wreck shelf is under 15 tiles at 6 tiles per second, under 3 seconds.
  - Opening a cache, combat, and leaving the wreck shelf fits inside 25 seconds.
  - Rising tide lasts 10 seconds, enough warning to move from the wreck shelf to higher ground.
  - Storm timer is 700 seconds.
  - Minimum travel between all caches and vault is under 60 seconds at player speed.
  - Combat adds at most 30 to 45 seconds if the player opens every cache.
  - Total expected clear time is well under 700 seconds.
  - Wraith speed is 4.5 to 5.0, below player speed 6.0, so the player can kite.
  - Normal wraith HP 4 at 0.6 second attack cooldown requires 2.4 seconds of swings.
  - Final wraith HP 8 at 0.6 second attack cooldown requires 4.8 seconds of swings.
  - Result: closes.

- Every call made in section 9 appears in section 8:
  - `seed`, `start`, `getState`, `setPlayerPos`, `move`, `step`, `interact`, `setWraithPos`, `attack`, `useFlare`, `clearWraiths`, `setHealth`, `setTide`, `clearWeeds`, `damageWraith`, `setStorm`, `eatRation` are all listed.
  - Result: closes.