# 0. SCOPE
## 0.1 Asked
- “open world game” → the 2D island, free movement, and UI State systems in sections 1, 3, and 5 deliver one continuous playable space with no level gates.
- “explore” → the Island Generator, Map Reveal, and Compass systems in section 3 let the player move, discover, and navigate the island.
- “an island” → the Island Generator and Treasure Layout Generator in section 3 place one bounded, generated island with land, water, points of interest, and treasure.
- “find treasure” → the Treasure Layout Generator, Chest Interaction, and Treasure Progression systems in section 3 place locked caches, map fragments, key shards, and a final vault.

## 0.2 Decisions
- 2D top-down is used, not 3D, because the best version of this game is judged by what the player must see at a glance: the island outline, fog of war, compass bearing, chest icons, and map clues. A top-down view keeps navigation legible in a browser.
- The island is a 128 by 128 tile grid with 16 pixel tiles, because that size is large enough to feel open while still being fully revealable by walking in a short play session.
- The treasure goal is fixed: 5 map fragments reveal the vault, 3 key shards unlock the vault, and 4 lock items open the 12 field caches, because this gives a clear exploration loop and a definite end without requiring permanent survival.
- Lock items are reusable, because the challenge should be finding the ruins, not repeating the same fetch quest.
- There is no permanent death; if pirates reduce health to zero, the player is wrecked back to the start and loses 20 gold, because the game is an exploration treasure hunt, not a survival game.
- All randomness comes from one seeded random source named RNG, because the island, treasure layout, and enemy placement must be reproducible by seed.
- The HUD includes an always-on compass, minimap, health, stamina, gold, fragments, shards, and weather, because orientation and inventory are the core player questions.
- The full map is opened with M, because the full map is the reward for exploration and the tool for planning the next treasure run.

## 0.3 Tiers
TIER 1 is the game: Island Generator, Treasure Layout Generator, Player Movement, Map Reveal, Compass, Chest Interaction, Treasure Progression, UI State.

TIER 2 items, in the order to add them:
- Day/Night, because it changes stamina regeneration and gives a visible clock.
- Weather, because it changes sprint speed and adds an overlay.
- Pirate Enemies, because they add danger to shrine and treasure routes.
- Black Chest, because it adds a late-game bonus once 10 field chests are opened.

TIER 3 items:
- Photo mode that pauses time and saves the current viewport.
- Achievement log for first chest, first lock, first shard, first vault, and wrecked.
- Island seed sharing through a numeric seed input on the title screen.
- Speedrun timer shown on the victory screen.

# 1. CONVENTIONS
One tile is 16 pixels. One pixel is one screen pixel. The world is 128 tiles by 128 tiles, which is 2048 pixels by 2048 pixels. Time is measured in seconds. One fixed update step is 1/60 second.

The origin is the top-left corner of the world. The x axis points right. The y axis points down. North is the negative y direction. The top of the screen is north. All compass angles are radians, with 0 pointing north and positive angles turning clockwise on screen. The player facing angle uses the same convention.

The camera is centered on the player. The viewport is 960 pixels wide and 640 pixels tall. The camera is clamped so it never shows outside the 2048 by 2048 world.

The update loop runs a fixed step of 1/60 second. In each tick, systems run in this order:
1. Advance WORLD.time by 1/60 second.
2. Day/Night, if present.
3. Weather, if present.
4. Player Movement.
5. Pirate Behavior, if present.
6. Black Chest, if present.
7. Map Reveal.
8. Compass.
9. Treasure Progression.
10. UI State.
Rendering happens after the tick.

If UI.state is not playing, no update systems change world records; the game still renders.

The one seeded random source is named RNG. RNG is a deterministic 32-bit linear sequence with multiplier 1664525, increment 1013904223, and modulus 4294967296. Each call returns the next value divided by 4294967296, giving a number from 0 to less than 1. No system may use any other random source.

Controls:

| Input | Action |
|---|---|
| W or Arrow Up | Set INPUT.moveY to -1 while held; release sets it to 0 |
| A or Arrow Left | Set INPUT.moveX to -1 while held; release sets it to 0 |
| S or Arrow Down | Set INPUT.moveY to 1 while held; release sets it to 0 |
| D or Arrow Right | Set INPUT.moveX to 1 while held; release sets it to 0 |
| Shift held | Set INPUT.sprint to true; release sets it to false |
| Space or E | Perform interact |
| M | Toggle map |
| Escape | Change screen state according to UI State |
| Touch left half, drag | Set INPUT.moveX and INPUT.moveY to the normalized drag direction clamped to -1, 0, or 1; direction persists until the stick changes or is released; release sets both to 0 |
| Touch right half, tap | Perform interact |
| Touch right half, hold 0.3 seconds | Set INPUT.sprint to true; release sets it to false |

# 2. RECORDS
RECORDS: WORLD, TILE, INPUT, PLAYER, COMPASS, CHEST, RUIN, ENEMY, UI

WORLD: The world record carries seed, int, starting value 1 and set by seed; width, int, starting value 128; height, int, starting value 128; time, float seconds, starting value 0; phase, enum day, dusk, night, starting value day; weather, enum sunny, cloudy, rain, storm, starting value sunny; weatherTimer, float seconds, starting value 0; landCount, int, starting value 0; fieldOpened, int, starting value 0; blackChestSpawned, bool, starting value false; victory, bool, starting value false.

TILE: The tile record carries x, int tile column, starting value 0 to 127 set by generator; y, int tile row, starting value 0 to 127 set by generator; kind, enum water, sand, grass, palm, rock, starting value water; revealed, bool, starting value false; visited, bool, starting value false.

Tile kind roster:

| Kind | Colour | Walkable |
|---|---|---|
| water | #1f6f8b | false |
| sand | #e8d48f | true |
| grass | #4c9b47 | true |
| palm | #2f7d32 | true |
| rock | #7c828a | true |

INPUT: The input record carries moveX, int, range -1 to 1, starting value 0; moveY, int, range -1 to 1, starting value 0; sprint, bool, starting value false.

PLAYER: The player record carries x, float pixels, starting value 1032; y, float pixels, starting value 1032; facing, float radians, starting value 0; health, int, starting value 100; stamina, float, starting value 100; gold, int, starting value 0; fragments, int, starting value 0; shardRed, bool, starting value false; shardBlue, bool, starting value false; shardGreen, bool, starting value false; lockRed, bool, starting value false; lockBlue, bool, starting value false; lockGreen, bool, starting value false; lockPurple, bool, starting value false; attackCooldown, float seconds, starting value 0.

COMPASS: The compass record carries angle, float radians, starting value 0; targetId, int, starting value 0; distance, float tiles, starting value 0.

CHEST: The chest record carries id, int, starting value 1 and increasing without reuse; kind, enum from the chest kind roster, starting value set by generator; x, float pixels, starting value set by generator; y, float pixels, starting value set by generator; opened, bool, starting value false.

Chest kind roster:

| Kind | Lock | Gold | Item | Count in base island |
|---|---|---|---|---|
| red_cache | red | 30 | none | 1 |
| red_fragment_cache | red | 60 | fragment | 2 |
| blue_cache | blue | 30 | none | 2 |
| blue_fragment_cache | blue | 60 | fragment | 1 |
| green_cache | green | 30 | none | 2 |
| green_fragment_cache | green | 60 | fragment | 1 |
| purple_cache | purple | 30 | none | 2 |
| purple_fragment_cache | purple | 60 | fragment | 1 |
| shrine_red_shard | none | 100 | shard_red | 1 |
| shrine_blue_shard | none | 100 | shard_blue | 1 |
| shrine_green_shard | none | 100 | shard_green | 1 |
| vault_cache | final | 1000 | victory | 1 |
| black_cache | none | 500 | none | 0 |

RUIN: The ruin record carries id, int, starting value 1 and increasing without reuse; kind, enum from the ruin kind roster, starting value set by generator; x, float pixels, starting value set by generator; y, float pixels, starting value set by generator; searched, bool, starting value false.

Ruin kind roster:

| Kind | Lock | Count in base island |
|---|---|---|
| ruin_red | red | 3 |
| ruin_blue | blue | 3 |
| ruin_green | green | 3 |
| ruin_purple | purple | 3 |

ENEMY: The enemy record carries id, int, starting value 1 and increasing without reuse; kind, enum pirate, starting value pirate; x, float pixels, starting value set by generator; y, float pixels, starting value set by generator; health, int, starting value 30; lastAttack, float seconds, starting value 0.

Enemy kind roster:

| Kind | Health | Speed | Detect range | Attack range | Damage | Attack interval | Gold on death |
|---|---|---|---|---|---|---|---|
| pirate | 30 | 80 pixels per second | 96 pixels | 16 pixels | 5 | 1 second | 10 |

UI: The UI record carries state, enum title, playing, map, pause, victory, starting value title.

# 3. SYSTEMS
SYSTEMS: Island Generator, Treasure Layout Generator, Player Movement, Map Reveal, Compass, Chest Interaction, Treasure Progression, UI State, Day/Night, Weather, Pirate Generator, Pirate Behavior, Black Chest

## Island Generator (T1)
- If start() is called with no built world, or seed(n) is called, set candidate seed s to n and rebuild TILE records, then CHEST and RUIN records through Treasure Layout Generator, then ENEMY records through Pirate Generator if Tier 2 is present.
- Initialize every TILE.kind to water, TILE.revealed to false, and TILE.visited to false.
- For i from 0 to 119, choose angle equal to 2π times RNG(), choose radius equal to 45 times the square root of RNG(), set tx to 64 plus the rounded horizontal component, and set ty to 64 plus the rounded vertical component; if tx and ty are both inside 0 to 127, set the 3 by 3 tile block centered on tx and ty to grass.
- For every tile that is grass, if RNG() is less than 0.18, set one randomly chosen in-bounds neighbor to grass.
- Set every tile on the outer border of the world to water.
- Force the 5 by 5 tile block centered on tile 64, 64 to grass.
- Reclassify land tiles: a land tile with at least one water neighbor becomes sand; all other land tiles become grass.
- Count land tiles and set WORLD.landCount to that count.
- Choose 600 distinct grass tiles that are not sand and not inside the 5 by 5 start block, and set their kind to palm. If fewer than 600 such tiles exist, the island generation fails.
- Choose 150 distinct remaining grass tiles that are not palm and not inside the 5 by 5 start block, and set their kind to rock. If fewer than 150 such tiles exist, the island generation fails.
- VERIFIER: tile 64, 64 is grass; WORLD.landCount is at least 3500 and at most 7000; a flood fill from tile 64, 64 over all land tiles reaches every land tile. If any check fails, set s to s plus 1 and repeat from the first rule of this system. When all checks pass, set WORLD.seed to s.

## Treasure Layout Generator (T1)
- After the island generation passes, build CHEST and RUIN records in the order below using RNG.
- The start tile is 64, 64. A tile is reachable if it is land and connected to the start tile over land.
- Place vault first: up to 5000 times, choose a random reachable land tile with Chebyshev distance from the start tile at least 40 and at most 60; if chosen, create a CHEST with kind vault_cache at that tile center. If none is accepted, the layout fails.
- Place 3 shrine caches: up to 5000 times each, choose a random reachable land tile with Chebyshev distance from start at least 25, at least 15 tiles from every existing point of interest, and at least 10 tiles from the vault; create CHEST records with kinds shrine_red_shard, shrine_blue_shard, and shrine_green_shard in that order. If any cannot be placed, the layout fails.
- Place 12 field caches: up to 5000 times each, choose a random reachable land tile with Chebyshev distance from start at least 10 and at least 8 tiles from every existing point of interest. Create 12 CHEST records with this exact kind distribution: red_cache 1, red_fragment_cache 2, blue_cache 2, blue_fragment_cache 1, green_cache 2, green_fragment_cache 1, purple_cache 2, purple_fragment_cache 1. If any cannot be placed, the layout fails.
- Place 12 ruins: up to 5000 times each, choose a random reachable land tile with Chebyshev distance from start at least 8, at least 3 tiles from every CHEST, and at least 6 tiles from every other RUIN. Create RUIN records with this exact kind distribution: ruin_red 3, ruin_blue 3, ruin_green 3, ruin_purple 3. If any cannot be placed, the layout fails.
- VERIFIER: there are exactly 16 CHEST records and 12 RUIN records; no two CHEST or RUIN records share a tile; every CHEST and RUIN tile is reachable; exactly 5 CHEST records have item fragment; exactly 3 CHEST records have a shard item; for each of red, blue, green, and purple, at least one RUIN has that lock and at least one field CHEST has that lock; the vault is at least 40 tiles from the start. If any check fails, set s to s plus 1 and repeat from the Island Generator.

## Player Movement (T1)
- If UI.state is not playing, this system has no effect.
- If INPUT.moveX or INPUT.moveY is not 0, set dx to INPUT.moveX and dy to INPUT.moveY; if both are nonzero, set dx to INPUT.moveX divided by the square root of 2 and dy to INPUT.moveY divided by the square root of 2.
- Set speed to 120 pixels per second. If INPUT.sprint is true and PLAYER.stamina is greater than 0, set speed to 180 pixels per second. If INPUT.sprint is true and WORLD.weather is rain, set speed to 150 pixels per second. If INPUT.sprint is true and WORLD.weather is storm, set speed to 120 pixels per second.
- If INPUT.sprint is true and the player is moving, reduce PLAYER.stamina by 20 times dt. If WORLD.weather is storm and the player is moving, reduce PLAYER.stamina by an additional 10 times dt. If PLAYER.stamina is below 0, set it to 0.
- If INPUT.sprint is false, increase PLAYER.stamina by the regeneration rate times dt: day 15, dusk 12, night 8. If PLAYER.stamina is above 100, set it to 100.
- Try to move horizontally: compute newX equal to PLAYER.x plus dx times speed times dt; if the tile at pixel newX and PLAYER.y is walkable, set PLAYER.x to newX.
- Try to move vertically: compute newY equal to PLAYER.y plus dy times speed times dt; if the tile at PLAYER.x and pixel newY is walkable, set PLAYER.y to newY.
- Set PLAYER.facing to the angle whose sine component is dy and cosine component is negative dy, using the screen convention where 0 is north and positive is clockwise.
- Reduce PLAYER.attackCooldown by dt. If PLAYER.attackCooldown is below 0, set it to 0.

## Map Reveal (T1)
- If UI.state is not playing, this system has no effect.
- Set player tile tx to the integer part of PLAYER.x divided by 16, and player tile ty to the integer part of PLAYER.y divided by 16.
- For every TILE with x and y such that the maximum of the absolute difference between x and tx and the absolute difference between y and ty is 8 or less, set TILE.revealed to true.
- For the TILE at tx, ty, set TILE.visited to true.

## Compass (T1)
- If UI.state is not playing, this system has no effect.
- If PLAYER.fragments is 5 and an unopened CHEST with kind vault_cache exists, set COMPASS.targetId to that chest’s id.
- Else, build a candidate list of unopened CHEST records: include every field or shrine chest whose lock is none or matches a true lock on PLAYER; include black_cache if one exists. Choose the candidate with the smallest Euclidean distance from PLAYER in tiles; if two are equal, choose the lower id. Set COMPASS.targetId to that chest’s id.
- Else, build a candidate list of all unopened field and shrine CHEST records. Choose the nearest by Euclidean distance in tiles; if two are equal, choose the lower id. Set COMPASS.targetId to that chest’s id.
- Else, set COMPASS.targetId to 0, COMPASS.angle to 0, and COMPASS.distance to 0.
- If COMPASS.targetId is not 0, let dx be the target chest x minus PLAYER.x in pixels, and dy be the target chest y minus PLAYER.y in pixels. Set COMPASS.angle to the angle whose sine component is dx and cosine component is negative dy. Set COMPASS.distance to the Euclidean distance of dx and dy divided by 16.

## Chest Interaction (T1)
- If UI.state is not playing, this system has no effect.
- On interact, build a list of interactables within range: any ENEMY within 24 pixels has priority; if no enemy is in range, include any unopened CHEST within 20 pixels and any unsearched RUIN within 20 pixels. If multiple non-enemy interactables are tied, choose the lower id.
- If an enemy is chosen: if PLAYER.attackCooldown is less than or equal to WORLD.time, reduce the enemy’s health by 10 and set PLAYER.attackCooldown to WORLD.time plus 0.5. If the enemy’s health is 0 or less, remove the enemy and increase PLAYER.gold by 10.
- If a ruin is chosen: set RUIN.searched to true. If the ruin kind is ruin_red, set PLAYER.lockRed to true. If ruin_blue, set PLAYER.lockBlue to true. If ruin_green, set PLAYER.lockGreen to true. If ruin_purple, set PLAYER.lockPurple to true.
- If a chest is chosen: a chest is openable if it is a shrine chest, a black chest, or a field chest whose lock matches a true lock on PLAYER; the vault is openable only if PLAYER.fragments is at least 5 and PLAYER.shardRed, PLAYER.shardBlue, and PLAYER.shardGreen are all true.
- If the chest is openable: set CHEST.opened to true. Increase PLAYER.gold by the chest kind’s gold. If the item is fragment, increase PLAYER.fragments by 1. If the item is shard_red, set PLAYER.shardRed to true. If shard_blue, set PLAYER.shardBlue to true. If shard_green, set PLAYER.shardGreen to true. If the item is victory, set WORLD.victory to true. If the chest kind is one of the 12 field cache kinds, increase WORLD.fieldOpened by 1.
- If the chest is not openable, no record changes.

## Treasure Progression (T1)
- If UI.state is not playing, this system has no effect.
- If PLAYER.fragments is greater than 5, set PLAYER.fragments to 5.
- If WORLD.victory is false and PLAYER.fragments is 5 and PLAYER.shardRed is true and PLAYER.shardBlue is true and PLAYER.shardGreen is true, the vault is eligible to open.
- If WORLD.victory becomes true, set UI.state to victory.

## UI State (T1)
- On the title screen, Enter or start() sets UI.state to playing and builds the world if it is absent.
- On the playing screen, M or Map sets UI.state to map.
- On the map screen, M or Escape sets UI.state to playing.
- On the playing screen, Escape sets UI.state to pause.
- On the pause screen, Escape or Resume sets UI.state to playing.
- On the victory screen, Continue sets UI.state to playing.
- On the victory screen, New Island sets UI.state to title and clears the current world so the next start builds a fresh island.
- On the victory screen, Escape sets UI.state to title.

## Day/Night (T2)
- If UI.state is not playing, this system has no effect.
- Set phaseT to WORLD.time modulo 600.
- If phaseT is less than 360, set WORLD.phase to day.
- Else, if phaseT is less than 480, set WORLD.phase to dusk.
- Else, set WORLD.phase to night.

## Weather (T2)
- If UI.state is not playing, this system has no effect.
- Increase WORLD.weatherTimer by dt.
- If WORLD.weatherTimer is at least 120, reduce it by 120 and advance WORLD.weather in the sequence sunny, cloudy, rain, storm, sunny.

## Pirate Generator (T2)
- After Treasure Layout Generator passes, place 20 ENEMY records with kind pirate.
- For each enemy, up to 5000 times, choose a random reachable land tile with Chebyshev distance from start at least 15, at least 10 tiles from every other enemy, and not within 5 tiles of start; if accepted, create the ENEMY record at that tile center.
- VERIFIER: there are exactly 20 ENEMY records; every enemy is on a land tile reachable from start; every enemy is at least 10 tiles from every other enemy. If any check fails, set s to s plus 1 and repeat from the Island Generator.

## Pirate Behavior (T2)
- If UI.state is not playing, this system has no effect.
- For each ENEMY: compute distance to PLAYER.
- If distance is 96 pixels or less, the pirate perceives the player.
- If distance is greater than 16 pixels, move the pirate toward PLAYER at 80 pixels per second. Do not move into water; if the attempted tile is water, keep the old component.
- If distance is 16 pixels or less and WORLD.time minus ENEMY.lastAttack is at least 1, reduce PLAYER.health by 5, set ENEMY.lastAttack to WORLD.time, and play enemy hit.
- If PLAYER.health is 0 or less, set PLAYER.health to 100, reduce PLAYER.gold by 20 but not below 0, set PLAYER.x to 1032, set PLAYER.y to 1032, set INPUT.moveX to 0, set INPUT.moveY to 0, and set INPUT.sprint to false.

## Black Chest (T2)
- If UI.state is not playing, this system has no effect.
- If WORLD.blackChestSpawned is false and WORLD.fieldOpened is at least 10, choose the reachable land tile with the greatest Euclidean distance from start that is not within 5 tiles of any existing CHEST or RUIN; if several are tied, choose the lowest tile index. Create a CHEST with kind black_cache at that tile center and set WORLD.blackChestSpawned to true.
- VERIFIER: the chosen tile is land and reachable. If no such tile exists, set s to s plus 1 and repeat from the Island Generator.

# 4. CORE LOOP
The player moves across the island, reveals fog of war, follows the compass, searches ruins for lock items, opens field caches for gold and map fragments, opens shrine caches for key shards, and finally opens the vault. Each chest opened increases gold and progress. Each ruin searched unlocks more caches. Each fragment brings the vault location onto the compass. Each shard makes the vault openable. The end is the vault: when PLAYER.fragments is 5 and all three shards are true, the player can open vault_cache, WORLD.victory becomes true, and the victory screen appears. After victory, the player may continue exploring or start a new island.

# 5. SCREENS
title → playing → map → playing. playing → pause → playing. playing → victory → playing. playing → victory → title.

- title shows the island title scene, the game title, and a Start button; Enter or clicking Start calls start().
- playing shows the world, HUD, and controls.
- map shows the full island map and HUD; M or Escape returns to playing.
- pause shows a dimmed playing screen and a Resume button; Escape or clicking Resume returns to playing.
- victory shows the golden vault, the gold total, the time, Continue, and New Island; Continue returns to playing, New Island returns to title, Escape returns to title.

Escape does this:
- On playing, it opens pause.
- On map, it returns to playing.
- On pause, it returns to playing.
- On victory, it returns to title.

HUD:

| Element | Record field shown |
|---|---|
| Health bar | PLAYER.health |
| Stamina bar | PLAYER.stamina |
| Gold counter | PLAYER.gold |
| Fragment counter | PLAYER.fragments out of 5 |
| Shard icons | PLAYER.shardRed, PLAYER.shardBlue, PLAYER.shardGreen |
| Compass needle | COMPASS.angle |
| Compass target label | CHEST.kind for COMPASS.targetId, or none if targetId is 0 |
| Clock icon | WORLD.time modulo 600 and WORLD.phase |
| Weather icon | WORLD.weather |
| Minimap | TILE.revealed and CHEST, RUIN, ENEMY positions |

# 6. AUDIO
Generated audio (oscillators and noise):

| Sound | Recipe | Rule that plays it |
|---|---|---|
| footstep | sine, 70 Hz, 0.05 seconds, attack 0.005, decay 0.045 | every 0.4 seconds while the player is moving on a walkable tile |
| chest_open | triangle, 660 Hz, 0.2 seconds, attack 0.01, decay 0.19 | when CHEST.opened becomes true |
| lock_found | sine, 880 Hz, 0.15 seconds, attack 0.01, decay 0.14 | when RUIN.searched becomes true |
| fragment_found | sine, 1046 Hz, 0.2 seconds, attack 0.01, decay 0.19 | when a chest item fragment is collected |
| shard_found | sine, 1318 Hz, 0.25 seconds, attack 0.01, decay 0.24 | when a chest item shard is collected |
| enemy_hit | square, 110 Hz, 0.08 seconds, attack 0.005, decay 0.075 | when an ENEMY’s health is reduced by player attack |
| enemy_death | sawtooth, 180 Hz, 0.2 seconds, attack 0.01, decay 0.19 | when an ENEMY is removed |
| victory | three sine notes 523 Hz, 659 Hz, 784 Hz, each 0.15 seconds, gap 0.02 seconds | when WORLD.victory becomes true |
| map_open | triangle, 320 Hz, 0.1 seconds, attack 0.01, decay 0.09 | when UI.state changes between playing and map |
| pause | sine, 440 Hz, 0.05 seconds, attack 0.005, decay 0.045 | when UI.state changes between playing and pause |
| weather_change | white noise, 0.5 seconds, lowpass 800 Hz | when WORLD.weather changes |

# 7. ART
AI art:
- ask for a tropical island aerial title scene as a scene
- ask for a nautical map paper as a sprite
- ask for a weathered treasure chest locked as a sprite
- ask for a weathered treasure chest open as a sprite
- ask for a golden treasure vault as a sprite
- ask for a black treasure chest as a sprite
- ask for a stone pirate ruin as a sprite
- ask for a pirate flag as a sprite

RECIPE: tile drawing: each TILE is a 16 by 16 square filled with the roster colour; water adds two horizontal 2 pixel stripes of #3b8fa8 at y 4 and y 12; grass adds three 1 pixel speckles of #3a7a36 at tile-local points 4,5; 9,8; 12,11; sand adds two 1 pixel dots of #d6c07a at tile-local points 5,6 and 11,10; palm adds a 2 by 8 trunk of #7a5230 from tile-local 8,14 to 8,6 and a canopy circle radius 5 of #2f7d32 centered at 8,6; rock adds a circle radius 4 of #7c828a centered at 8,8 and a 1 pixel highlight of #aeb4bb at 7,7.

RECIPE: player: a shadow ellipse 8 pixels wide and 3 pixels tall of rgba(0,0,0,0.2) below the player, then a circle radius 6 of #f4d06f with stroke #6b4423 width 1 centered on PLAYER.x, PLAYER.y.

RECIPE: enemy pirate: a circle radius 5 of #b33333 with stroke #411111, plus a 4 pixel red flag triangle above it.

RECIPE: chest fallback: a 12 by 8 rectangle of #8b5a2b with a 2 by 2 clasp of #ffd23f; use the AI sprite when present.

RECIPE: ruin fallback: a 12 by 10 rectangle of #7c828a with a 4 by 6 black door; use the AI sprite when present.

RECIPE: vault fallback: a circle radius 10 of #ffd23f with stroke #8b6a1b; use the AI sprite when present.

RECIPE: compass HUD: a circle radius 24 of #223344 with stroke #445566, a north tick 2 by 4 of #ffffff at the top, and a needle triangle 18 pixels long and 5 pixels wide of #d33333 rotated by COMPASS.angle.

RECIPE: minimap: each TILE is 2 by 2 pixels; revealed tiles use their roster colour, unexplored tiles are #0a0f14; CHEST icons are 4 by 4 squares of #ffd23f, RUIN icons are 4 by 4 squares of #7c828a, the player is a 2 by 2 square of #ffffff.

RECIPE: day and night overlay: a full viewport rectangle of rgba(0,0,20,alpha) where alpha is 0 for day, 0.18 for dusk, and 0.35 for night.

RECIPE: weather overlay: rain is 120 diagonal 2 pixel lines of #a8c7ff at alpha 0.3; storm is 200 diagonal 2 pixel lines of #a8c7ff at alpha 0.4 plus a screen flash of alpha 0.1 every 2 seconds.

RECIPE: UI bars: each bar is 120 by 10 with background #223344; health fill is #d33333 with width equal to PLAYER.health divided by 100 times 120; stamina fill is #6bcf6b with width equal to PLAYER.stamina divided by 100 times 120.

Everything else — tiles, player, enemies, compass, minimap, day and night overlay, weather overlay, UI bars, and fallback sprites — is drawn in code.

# 8. DEBUG API
The game installs window.__game with plain synchronous functions:

| Call | What it does | Returns |
|---|---|---|
| start() | Enters play from title using the current seed, default 1, building a fresh world if needed | object with seed and time |
| step(dt, n) | Advances n fixed ticks of dt seconds without waiting for real time, then draws once | object with time |
| setTime(t) | Advances WORLD.time forward to t seconds by applying the same tick rules without drawing; t must be a multiple of 1/60 | object with time |
| seed(n) | Sets the current seed to n and rebuilds all generated records, keeping UI.state playing if already playing | object with actual seed |
| getState() | Returns all record fields as plain data | object with world, tiles, input, player, compass, chests, ruins, enemies, ui |
| setMove(dx, dy) | Sets INPUT.moveX and INPUT.moveY, values clamped to -1, 0, 1 | object with moveX and moveY |
| setSprint(b) | Sets INPUT.sprint to b | object with sprint |
| interact() | Performs the interact action at the current player position | object with kind and id, or none |
| toggleMap() | Toggles UI.state between playing and map | object with state |
| togglePause() | Toggles UI.state between playing and pause | object with state |
| setPlayer(x, y) | Sets PLAYER.x and PLAYER.y | object with x and y |
| setTile(x, y, kind) | Sets TILE.kind for tile x, y | object with x, y, kind |
| revealAll() | Sets every TILE.revealed to true | object with revealedCount |
| clearChests() | Removes all CHEST records | object with removed |
| clearRuins() | Removes all RUIN records | object with removed |
| clearEnemies() | Removes all ENEMY records | object with removed |
| spawnChest(kind, x, y) | Adds a CHEST with the given kind at pixel x, y | object with id |
| spawnRuin(kind, x, y) | Adds a RUIN with the given kind at pixel x, y | object with id |
| spawnEnemy(kind, x, y) | Adds an ENEMY with the given kind at pixel x, y | object with id |
| openChest(id) | Forces the chest with that id to open and applies its loot | object with opened |
| grantLock(lock) | Sets the matching PLAYER lock to true for red, blue, green, or purple | object with lockRed, lockBlue, lockGreen, lockPurple |
| grantFragment(count) | Increases PLAYER.fragments by count, capped at 5 | object with fragments |
| grantShard(shard) | Sets the matching PLAYER shard to true for red, blue, or green | object with shardRed, shardBlue, shardGreen |
| setGold(n) | Sets PLAYER.gold to n | object with gold |
| setFieldOpened(n) | Sets WORLD.fieldOpened to n | object with fieldOpened |
| setWeather(kind) | Sets WORLD.weather to kind and WORLD.weatherTimer to 0 | object with weather |

# 9. TESTS
1. After seed(1), start(): getState().ui.state is playing; getState().world.width is 128; getState().world.height is 128; the tile at y 128 times 64 plus x 64 has kind grass.
2. After seed(1), start(): getState().world.landCount is at least 3500; getState().world.landCount is at most 7000; the tile at 0, 0 has kind water; the tile at 64, 64 has kind grass.
3. After seed(1), start(): getState().chests length is 16; getState().ruins length is 12; the number of chest kinds with item fragment is 5; the number of chest kinds with a shard item is 3; for each of red, blue, green, and purple, at least one ruin kind matches and at least one field chest kind matches.
4. After seed(1), start(), setPlayer(1032, 1032), setMove(1, 0), step(1/60, 2): getState().player.x is 1036 and getState().player.y is 1032.
5. After seed(1), start(), setPlayer(1032, 1032), setMove(1, 0), setSprint(true), step(1/60, 30): getState().player.stamina is 90.
6. After seed(1), start(), revealAll(): every tile in getState().tiles has revealed true.
7. After seed(1), start(), clearChests(), clearRuins(), grantLock("red"), spawnChest("red_cache", 1104, 1032), setPlayer(1032, 1032), step(1/60, 1): the chest id returned by spawnChest is the compass target; getState().compass.angle is π/2; getState().compass.distance is 4.5.
8. After seed(1), start(), clearChests(), grantLock("red"), spawnChest("red_cache", 1032, 1048), setPlayer(1032, 1032), interact(): the chest id returned by spawnChest has opened true; getState().player.gold is 30.
9. After seed(1), start(), clearChests(), grantLock("blue"), spawnChest("red_cache", 1032, 1048), setPlayer(1032, 1032), interact(): the chest id returned by spawnChest has opened false; getState().player.gold is 0.
10. After seed(1), start(), clearRuins(), spawnRuin("ruin_red", 1032, 1048), setPlayer(1032, 1032), interact(): the ruin id returned by spawnRuin has searched true; getState().player.lockRed is true.
11. After seed(1), start(), clearChests(), grantLock("red"), spawnChest("red_fragment_cache", 1032, 1048), setPlayer(1032, 1032), interact(): the chest id returned by spawnChest has opened true; getState().player.fragments is 1; getState().player.gold is 60.
12. After seed(1), start(), clearChests(), grantFragment(5), grantShard("red"), grantShard("blue"), grantShard("green"), spawnChest("vault_cache", 1032, 1048), setPlayer(1032, 1032), interact(): the chest id returned by spawnChest has opened true; getState().world.victory is true; getState().ui.state is victory; getState().player.gold is 1000.
13. After seed(1), start(), setTime(480): getState().world.phase is night.
14. After seed(1), start(), setWeather("storm"), setTime(120): getState().world.weather is sunny.
15. After seed(1), start(): getState().enemies length is 20; every enemy has kind pirate and health 30.
16. After seed(1), start(), clearEnemies(), setTile(64, 64, "grass"), setTile(65, 64, "grass"), setTile(66, 64, "grass"), setTile(67, 64, "grass"), setTile(68, 64, "grass"), setTile(69, 64, "grass"), setTile(70, 64, "grass"), setPlayer(1032, 1032), spawnEnemy("pirate", 1128, 1032), step(1/60, 90): the enemy id returned by spawnEnemy has x 1048 and y 1032; getState().player.health is 95.
17. After seed(1), start(), setFieldOpened(10), step(1/60, 1): getState().world.blackChestSpawned is true; at least one chest in getState().chests has kind black_cache.
18. After seed(1), start(), toggleMap(): getState().ui.state is map; after toggleMap(): getState().ui.state is playing.

SCREENSHOTS:

| Screen or state | What a person must see |
|---|---|
| title | tropical island title scene, game title, Start button |
| playing | top-down island, player dot, HUD bars, compass, minimap, weather icon |
| map | full 128 by 128 island map, revealed area, chest and ruin icons, player marker |
| pause | dimmed island behind a pause overlay and Resume button |
| victory | golden vault sprite, gold total, Continue and New Island buttons |
| storm | diagonal rain lines over the island and a darker weather tint |
| pirate | red pirate circle near the player with a small flag |
| black chest | black treasure chest sprite visible on the map after 10 field chests are opened |

# 10. BUILD ORDER
1. Title and entry: page opens, title renders, start enters play. Check 1.
2. Island and movement: Island Generator, Player Movement, Map Reveal, UI State. Checks 4, 6.
3. Treasure and navigation: Treasure Layout Generator, Compass, Chest Interaction. Checks 3, 7, 8.
4. Progression and victory: Treasure Progression, vault interaction, victory screen. Check 12.
5. Day and weather: Day/Night, Weather. Checks 13, 14.
6. Pirates: Pirate Generator, Pirate Behavior. Checks 15, 16.
7. Bonus chest: Black Chest. Check 17.
8. Full polish: audio, art, HUD, map, debug, and all screens. Check 18 and screenshot rows.

# 11. DONE
- “open world game” → checks 1, 2, 4, 18; screenshots title and playing.
- “explore” → checks 4, 6, 7; screenshots playing and map.
- “an island” → checks 2, 3; screenshots playing and map.
- “find treasure” → checks 8, 11, 12; screenshots victory.

The game is finished when every line above is true.

# A. SANITY
- Every field a rule reads or writes is on a record: WORLD.seed, width, height, time, phase, weather, weatherTimer, landCount, fieldOpened, blackChestSpawned, victory; TILE.x, y, kind, revealed, visited; INPUT.moveX, moveY, sprint; PLAYER.x, y, facing, health, stamina, gold, fragments, shards, locks, attackCooldown; COMPASS.angle, targetId, distance; CHEST.id, kind, x, y, opened; RUIN.id, kind, x, y, searched; ENEMY.id, kind, x, y, health, lastAttack; UI.state. Result: closes.
- Every place, thing, or kind a rule names is placed by a generator or listed in a roster: tile kinds are in the tile roster; chest kinds are in the chest roster; ruin kinds are in the ruin roster; enemy kind is in the enemy roster; base chests and ruins are placed by Treasure Layout Generator; base enemies are placed by Pirate Generator; black chest is placed by Black Chest. Result: closes.
- Consumable totals: locks: 12 ruins supply 3 of each lock and 12 field caches demand 3 of each lock; locks are reusable, so demand is at most one of each lock type. Fragments: 5 fragment chests are placed and 5 are required. Shards: 3 shrine chests are placed and 3 are required. Field opens: 12 field chests are placed and 10 are required for the black chest. Stamina: 100 maximum against 20 per second sprint drain gives 5 seconds of sprint, and 15 per second day regen refills it in 6.67 seconds. Enemy health: 30 against 10 damage per player hit gives 3 hits. Result: closes.
- Timing pairs: player speed 120 pixels per second against 16 pixel tiles gives 0.133 seconds per tile; 128 tiles gives a minimum 17.1 second crossing. Sprint drain 20 per second against 100 stamina gives 5 seconds; day regen 15 per second gives 6.67 seconds to refill. Enemy speed 80 pixels per second against the 96 pixel detect range and 16 pixel attack range closes the 80 pixel gap in 1 second. Weather 120 seconds against day length 600 seconds gives 5 weather changes per day. Map reveal radius 8 tiles at 16 pixels is 128 pixels, and player speed 120 pixels per second reveals new tiles continuously while moving. Result: closes.
- Every call section 9 makes is in section 8: seed, start, getState, setPlayer, setMove, setSprint, step, revealAll, clearChests, clearRuins, clearEnemies, spawnChest, spawnRuin, spawnEnemy, setTile, grantLock, grantFragment, grantShard, interact, setTime, setWeather, setFieldOpened, toggleMap. Result: closes.