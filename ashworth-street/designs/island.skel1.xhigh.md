# 0. SCOPE

## 0.1 Asked

- "An open world game" → sections 0.2, 1, 2, 3: a large generated island, free player movement, camera, and no fixed linear level.
- "where you explore an island" → sections 2, 3, 5: IslandMap, Player, Camera, FogOfWar, LandmarkClues, DayNight, and the HUD minimap.
- "and find treasure" → sections 2, 3, 5, 6, 7: TreasureCache, MapShard, Win, reward sounds, treasure art, and the won screen.

## 0.2 Decisions

- The game is 2D top-down, not 3D, because the player needs to read an island map, follow clues, and spot hidden dig sites without camera depth ambiguity.
- The world is a 256 by 256 tile grid, and one tile is 12 screen pixels, because that gives a large enough island to feel open while keeping every screen readable.
- The player is a single explorer with no combat, because the request asks for exploration and treasure-finding, not fighting; the challenge comes from hidden caches, fog, night, and landmark clues.
- There is one Grand Cache and eight minor caches: five minor caches contain MapShards and three contain gold, because the player needs a short progression before the main treasure can be found.
- Water blocks movement, land is always connected, and the island is circular with a guaranteed beach ring, because an open world island needs clear travel bounds and reliable spawn placement.
- The player has a fixed speed of 8 tiles per second, with terrain and night modifiers, because the game should feel responsive and readable.
- The update loop uses a fixed step of 1/60 second, because tests and animation timing need deterministic values.
- Touch play uses a virtual stick on the left and one action button on the right, because the game needs only movement and one interaction verb.
- The game ends when the Grand Cache is opened, then a new seeded island can be started, because a single clear treasure goal gives the loop a satisfying finish and an easy reason to replay.

## 0.3 Tiers

TIER 1 is the game:

- IslandGenerator
- PlayerMovement
- Camera
- TreasureCache
- MapShard
- Win

TIER 2 is what makes it good, in this order:

- FogOfWar hides the island until visited.
- DayNight slows the player at night and adds a light circle.
- LandmarkClues gives optional arrows to the Grand Cache from five landmarks.
- Sound gives feedback for shards, chests, landmarks, night, and victory.

TIER 3:

- Ambient sea drone music.
- Sparkle particles around revealed caches and the Grand Cache.
- A saved seed list that lets the player return to a previous island.

# 1. CONVENTIONS

- One tile is the world unit. One tile is 12 screen pixels at zoom 1.
- Coordinates are in tiles. x increases east, to the right. y increases south, downward. North is decreasing y.
- The origin is the top-left corner of the 256 by 256 grid, tile (0, 0).
- The camera is top-down and follows the player.
- The update loop runs in fixed steps of dt = 1/60 second.
- Each tick, input values are read first, then systems run in this order: DayNight, PlayerMovement, Camera, TreasureCache, MapShard, FogOfWar, LandmarkClues, Win, Sound. Rendering happens after all systems.
- The only random source is named RNG. RNG is seeded by IslandGenerator from GameState.baseSeed and finalSeed. No other system, screen, particle, or sound may use randomness.
- Touch is supported: the left half of the screen is a virtual stick that calls setMove with the stick direction, and the right-bottom button calls pressAction.

Controls:

| Input | Action |
|---|---|
| W or ArrowUp | setMove(0, -1) |
| S or ArrowDown | setMove(0, 1) |
| A or ArrowLeft | setMove(-1, 0) |
| D or ArrowRight | setMove(1, 0) |
| E or Space | pressAction |
| Escape | pressEscape |
| Touch left-half stick | setMove(stickX, stickY) continuously while touched |
| Touch right-bottom button | pressAction |

# 2. RECORDS

RECORDS: GameState, IslandMap, Player, Camera, TreasureCache, MapShard, Landmark, DayNight.

GameState: mode is a string with values title, playing, paused, won; it starts as title. time is a number in seconds, starting at 0, range 0 to 999999. baseSeed is an integer, starting at 7, range 0 to 999999. finalSeed is an integer, starting at 7, range 0 to 999999. lastSound is a string, starting as none. previousSound is a string, starting as none. inputX is an integer with values -1, 0, or 1, starting at 0. inputY is an integer with values -1, 0, or 1, starting at 0. pendingAction is a boolean, starting as false.

IslandMap: width is an integer in tiles, fixed at 256. height is an integer in tiles, fixed at 256. spawnX is an integer tile, starting at 0, range 0 to 255. spawnY is an integer tile, starting at 0, range 0 to 255. tiles is a 256 by 256 array of terrain names from the terrain roster; it starts generated. decor is a 256 by 256 array of booleans, starting generated false. revealed is a 256 by 256 array of booleans, starting false for every tile. grandNorth is a boolean, starting false. grandEast is a boolean, starting false. grandSouth is a boolean, starting false. grandWest is a boolean, starting false. grandCenter is a boolean, starting false. grandAll is a boolean, starting false.

Player: x is a number in tiles, starting at 0, range 0 to 256. y is a number in tiles, starting at 0, range 0 to 256. facing is an integer with values 0 north, 1 east, 2 south, 3 west; it starts at 0. speed is a number in tiles per second, fixed at 8. action is a string with values none or dig; it starts as none. actionTimer is a number in seconds, starting at 0, range 0 to 3. shards is an integer, starting at 0, range 0 to 5. gold is an integer, starting at 0, range 0 to 9999. treasure is a boolean, starting false.

Camera: x is a number in tiles, starting at 0, range 0 to 256. y is a number in tiles, starting at 0, range 0 to 256. zoom is a number, fixed at 1.

TreasureCache: id is an integer from 1 to 9. x is an integer tile, starting generated, range 0 to 255. y is an integer tile, starting generated, range 0 to 255. kind is a string from the cache kind roster. state is a string with values hidden, available, opening, opened; it starts as hidden. openTimer is a number in seconds, starting at 0, range 0 to 3. shardId is an integer from 0 to 5, starting at 0; 0 means no shard. goldAmount is an integer, starting at 0, range 0 to 9999. isTreasure is an integer with value 0 or 1, starting at 0. visible is a boolean, starting false.

MapShard: id is an integer from 1 to 5. state is a string with values unseen or collected; it starts as unseen.

Landmark: id is an integer from 1 to 5. type is a string from the landmark roster. x is an integer tile, starting generated, range 0 to 255. y is an integer tile, starting generated, range 0 to 255. visited is a boolean, starting false. clueX is an integer tile, starting at 0, range 0 to 255. clueY is an integer tile, starting at 0, range 0 to 255.

DayNight: phase is a string with values day, dusk, night, dawn; it starts as day. timer is a number in seconds, starting at 45, range 0 to 45. speedMult is a number, starting at 1, range 0.75 to 1. lightRadius is a number in tiles, starting at 9999, range 8 to 9999.

Terrain roster:

| Terrain | Colour hex | Walkable | Speed multiplier | Decor rule |
|---|---|---|---|---|
| water | #176c8a | no | 0 | none |
| beach | #e0c878 | yes | 1 | none |
| grass | #78b05a | yes | 1 | none |
| forest | #4f8a43 | yes | 0.75 | tree if decor is true |
| rock | #8a8a85 | yes | 0.85 | boulder if decor is true |

Cache kind roster:

| Kind | Shard id | Gold amount | isTreasure | Open time seconds | Requirement |
|---|---|---|---|---|---|
| minorMap | 1 to 5 assigned by generator | 0 | 0 | 2 | none |
| minorGold | 0 | 10 | 0 | 2 | none |
| grand | 0 | 0 | 1 | 3 | Player.shards equals 5 |

MapShard roster:

| Shard id | Sector | Reveal offset in tiles from Grand Cache |
|---|---|---|
| 1 | North | x -8 to 7, y -16 to -1 |
| 2 | East | x 1 to 16, y -8 to 7 |
| 3 | South | x -8 to 7, y 1 to 16 |
| 4 | West | x -16 to -1, y -8 to 7 |
| 5 | Center | x -4 to 4, y -4 to 4 |

Landmark roster:

| Landmark id | Type | Minimap colour hex |
|---|---|---|
| 1 | Lighthouse | #ffd54a |
| 2 | Stone Ruins | #b8b8b8 |
| 3 | Old Boat | #8b5a2b |
| 4 | Tide Pools | #4dd0e1 |
| 5 | Watch Tower | #ff8a65 |

# 3. SYSTEMS

SYSTEMS: IslandGenerator, PlayerMovement, Camera, TreasureCache, MapShard, Win, FogOfWar, DayNight, LandmarkClues, Sound.

### IslandGenerator (T1)

- On initial load, on start, or on seed(n), RNG is seeded with GameState.baseSeed and GameState.finalSeed.
- For candidateSeed starting at GameState.baseSeed and increasing by 1 for at most nine attempts, build the island.
- For each tile (x, y): calculate d as the square root of (x - 128) squared plus (y - 128) squared.
- If d is greater than 120, set tiles[x][y] to water.
- Else if d is greater than 110, set tiles[x][y] to beach.
- Else calculate h as (x times 73856093 plus y times 19349663 plus candidateSeed times 83492791) modulo 10000, and set n to h divided by 10000.
- If n is less than 0.35, set tiles[x][y] to grass. If n is less than 0.70, set tiles[x][y] to forest. Else set tiles[x][y] to rock.
- Set spawnX and spawnY to the beach tile with the greatest x value; if there is a tie, choose the tile with the y value closest to 128. For the guaranteed circular island, this is tile (248, 128).
- Place the Grand Cache as cache id 9. Build a list of all tiles whose terrain is grass, forest, or rock, whose distance d from center is between 35 and 105, and whose distance from spawn is greater than 30. Sort that list descending by hGrand, where hGrand is (x times 126233193 plus y times 297452319 plus candidateSeed times 521053) modulo 100000. Choose the first tile. Set cache id 9 to that tile, kind grand, state hidden, visible false, openTimer 0, shardId 0, goldAmount 0, isTreasure 1.
- Place eight minor caches as ids 1 to 8. Build a list of all tiles whose terrain is grass, forest, or rock, whose distance d from center is between 20 and 105. Sort that list descending by hMinor, where hMinor is (x times 190102347 plus y times 668265263 plus candidateSeed times 812341) modulo 100000. Choose the first tile that is at least 22 tiles from spawn, the Grand Cache, and every already chosen minor cache. Repeat until eight caches are chosen. Assign the first five chosen caches to kind minorMap with shardId 1 through 5 in that order. Assign the next three chosen caches to kind minorGold with goldAmount 10.
- Place five landmarks as ids 1 to 5. Build a list of all tiles whose terrain is grass, forest, or rock. Sort that list descending by hLand, where hLand is (x times 429496731 plus y times 2166136261 plus candidateSeed times 987654) modulo 100000. Choose the first tile that is at least 40 tiles from every already chosen landmark and at least 12 tiles from spawn and every cache. Repeat until five landmarks are chosen. Assign types in landmark roster order: id 1 Lighthouse, id 2 Stone Ruins, id 3 Old Boat, id 4 Tide Pools, id 5 Watch Tower. Set each visited false, clueX 0, clueY 0.
- For every forest tile, if (x times 31 plus y times 17 plus candidateSeed times 7) modulo 10000 is less than 6000, set decor[x][y] to true. For every rock tile, if the same value is less than 2000, set decor[x][y] to true. All other decor values are false.
- Set all revealed values to false.
- Set all MapShard state values to unseen.
- Set all grand sector fields grandNorth, grandEast, grandSouth, grandWest, grandCenter, and grandAll to false.
- Run the verifier. The verifier checks: spawn tile is beach; there are exactly nine TreasureCache records; there are exactly five Landmark records; no cache or landmark is on water; every cache tile has distance d from center less than or equal to 110; a breadth-first search from spawn over walkable tiles reaches every cache and every landmark.
- If any verifier check fails, re-roll with the next seed: candidateSeed becomes baseSeed plus the next attempt number, rebuild, and run the verifier again.
- If no candidate from attempt 0 through 8 passes, use a circular fallback layout: water if d is greater than 120, beach if d is greater than 110, grass otherwise; spawn at (248, 128); Grand Cache at (128, 60); minorMap caches at (100, 90), (156, 90), (128, 100), (128, 150), (100, 150); minorGold caches at (170, 110), (90, 120), (128, 180); landmarks at (128, 40), (160, 128), (128, 180), (96, 128), (128, 100). Set finalSeed to the failed candidateSeed and mark the verifier as passed by fallback.
- Set GameState.finalSeed to the candidateSeed that was used.
- Reset Player.x to spawnX, Player.y to spawnY, Player.action to none, Player.actionTimer to 0, Player.shards to 0, Player.gold to 0, Player.treasure to false.
- Reset DayNight.phase to day, DayNight.timer to 45, DayNight.speedMult to 1, DayNight.lightRadius to 9999.
- Reset GameState.time to 0, GameState.lastSound to none, GameState.previousSound to none, GameState.inputX to 0, GameState.inputY to 0, GameState.pendingAction to false.

### PlayerMovement (T1)

- Read GameState.inputX and GameState.inputY as the direction vector. If both values are nonzero, multiply both by 0.7071068.
- Set Player.facing to 1 if inputX is greater than inputY and inputX is greater than 0; to 3 if inputX is less than inputY and inputX is less than 0; to 2 if inputY is greater than inputX and inputY is greater than 0; to 0 if inputY is less than inputX and inputY is less than 0; otherwise leave Player.facing unchanged.
- Calculate speed as Player.speed times DayNight.speedMult times the terrain speed multiplier of the tile under the player. If Player.action is not none, set speed to 0.
- Calculate step as speed times dt.
- If step is greater than 0 and the direction is horizontal, move axis by axis with a player radius of 0.4 tiles.
- For east movement: calculate leadingX as Player.x plus 0.4. Calculate tileX as the floor of leadingX plus step. If the tile at tileX and floor(Player.y) is not walkable, set Player.x to tileX minus 0.4. Else set Player.x to Player.x plus step.
- For west movement: calculate leadingX as Player.x minus 0.4. Calculate tileX as the floor of leadingX minus step. If the tile at tileX and floor(Player.y) is not walkable, set Player.x to tileX plus 1 plus 0.4. Else set Player.x to Player.x minus step.
- For south movement: calculate leadingY as Player.y plus 0.4. Calculate tileY as the floor of leadingY plus step. If the tile at floor(Player.x) and tileY is not walkable, set Player.y to tileY minus 0.4. Else set Player.y to Player.y plus step.
- For north movement: calculate leadingY as Player.y minus 0.4. Calculate tileY as the floor of leadingY minus step. If the tile at floor(Player.x) and tileY is not walkable, set Player.y to tileY plus 1 plus 0.4. Else set Player.y to Player.y minus step.
- If movement is blocked, the player remains at the clamped position and no movement occurs on that axis in that tick.
- If step is 0, do not change Player.x or Player.y.

### Camera (T1)

- Set Camera.x to Player.x.
- Set Camera.y to Player.y.
- Set Camera.zoom to 1.

### TreasureCache (T1)

- For every TreasureCache with state available and visible true, calculate the distance from Player.x and Player.y to cache.x plus 0.5 and cache.y plus 0.5. If that distance is less than or equal to 1.25 tiles, the cache is eligible for prompt and action.
- If GameState.pendingAction is true and at least one cache is eligible, set GameState.pendingAction to false.
- Choose the eligible cache with the smallest distance. Set its state to opening, set its openTimer to the open time from the cache kind roster, set Player.action to dig, and set Player.actionTimer to the same openTimer.
- If GameState.pendingAction is true and no cache is eligible, leave GameState.pendingAction unchanged so LandmarkClues can use it.
- For every TreasureCache with state opening and Player.action dig, calculate oldTimer as the cache openTimer before decrementing.
- Decrease cache openTimer by dt and set Player.actionTimer to cache openTimer.
- If oldTimer is greater than 1.0 and the new openTimer is less than or equal to 1.0, set GameState.lastSound to dig.
- Calculate the distance from the player to the cache centre. If that distance is greater than 2.0 tiles, set cache state to available, cache openTimer to 0, Player.action to none, and Player.actionTimer to 0.
- If cache openTimer is less than or equal to 0, set cache state to opened, cache openTimer to 0, Player.action to none, and Player.actionTimer to 0.
- When a minorGold cache becomes opened, set Player.gold to Player.gold plus 10 and set GameState.lastSound to openChest.
- When a minorMap cache becomes opened, set the matching MapShard state to collected and set Player.shards to Player.shards plus 1.
- When a grand cache becomes opened, set Player.treasure to true, set GameState.lastSound to grandWin, and leave mode change to the Win system.

### MapShard (T1)

- When MapShard 1 changes from unseen to collected, set IslandMap.grandNorth to true and reveal every tile in its roster offset from the Grand Cache.
- When MapShard 2 changes from unseen to collected, set IslandMap.grandEast to true and reveal every tile in its roster offset from the Grand Cache.
- When MapShard 3 changes from unseen to collected, set IslandMap.grandSouth to true and reveal every tile in its roster offset from the Grand Cache.
- When MapShard 4 changes from unseen to collected, set IslandMap.grandWest to true and reveal every tile in its roster offset from the Grand Cache.
- When MapShard 5 changes from unseen to collected, set IslandMap.grandCenter to true and reveal every tile in its roster offset from the Grand Cache.
- When any MapShard changes from unseen to collected, set GameState.lastSound to shard.
- When Player.shards becomes 5, set IslandMap.grandAll to true.
- When IslandMap.grandAll becomes true, set the Grand Cache state to available if it is hidden, and set Grand Cache visible to true.

### Win (T1)

- If Player.treasure is true and GameState.mode is playing, set GameState.mode to won and set GameState.lastSound to grandWin.
- If GameState.mode is won, stop PlayerMovement, TreasureCache, MapShard, FogOfWar, LandmarkClues, and DayNight from changing gameplay fields; only Sound and rendering run.

### FogOfWar (T2)

- When GameState.mode changes from title or won to playing, reveal every tile within 8 tiles of IslandMap.spawnX and IslandMap.spawnY.
- Each tick, reveal every tile whose centre is within 6 tiles of Player.x and Player.y.
- For every TreasureCache with state hidden:
  - If kind is grand and IslandMap.grandAll is false, leave it hidden.
  - Else if any revealed tile is within 3 tiles of the cache centre, set cache state to available and cache visible to true.
- For every TreasureCache with state available, opening, or opened, set cache visible to true.
- The minimap draws only tiles whose IslandMap.revealed value is true.

### DayNight (T2)

- Each tick, decrease DayNight.timer by dt.
- If DayNight.timer is less than or equal to 0:
  - If phase is day, set phase to dusk, set timer to 10, set speedMult to 0.9, and set lightRadius to 10.
  - If phase is dusk, set phase to night, set timer to 20, set speedMult to 0.75, set lightRadius to 8, and set GameState.lastSound to nightCreak.
  - If phase is night, set phase to dawn, set timer to 10, set speedMult to 0.9, and set lightRadius to 10.
  - If phase is dawn, set phase to day, set timer to 45, set speedMult to 1, and set lightRadius to 9999.

### LandmarkClues (T2)

- If GameState.pendingAction is true and Player.action is not dig:
  - For every Landmark with visited false, calculate the distance from Player.x and Player.y to landmark.x plus 0.5 and landmark.y plus 0.5.
  - If at least one landmark distance is less than or equal to 1.5 tiles, set GameState.pendingAction to false.
  - Choose the nearest eligible landmark.
  - Set that landmark visited to true.
  - Set that landmark clueX to the Grand Cache x and clueY to the Grand Cache y.
  - Set GameState.lastSound to landmark.
- Each tick, for every visited Landmark, the minimap draws an arrow from that landmark toward clueX and clueY.

### Sound (T2)

- Each tick, if GameState.lastSound is not equal to GameState.previousSound, play the audio recipe named by GameState.lastSound.
- Set GameState.previousSound to GameState.lastSound.
- If GameState.lastSound is none, play nothing.

# 4. CORE LOOP

The player starts at the east beach, sees a small revealed area, and moves with WASD or touch. Each tick, FogOfWar reveals land around the player, DayNight changes speed and light, and LandmarkClues may add arrows after landmarks are visited. The player explores, finds minor caches, presses the action key to dig for 2 seconds, and collects gold or MapShards. Each MapShard reveals a sector of the Grand Cache area and moves Player.shards closer to 5. When five MapShards are collected, the Grand Cache becomes available and appears on the minimap. The player travels to the Grand Cache, presses the action key to dig for 3 seconds, and opens the final treasure. What grows is revealed land, gold, shards, and visited landmarks. What unlocks is the Grand Cache marker. The end is the won screen. The game says so explicitly: it is finished when the Grand Cache is opened. After the won screen, the player can start a new seeded island, which keeps it going through replay.

# 5. SCREENS

State machine:

title (title scene, game name, Start button, New Island button, controls list) → playing (HUD, island view) → paused (resume and quit overlay) → playing  
title → won only after Win system fires from playing  
won (treasure pile, gold count, Sail On button) → title after Sail On or Enter, with baseSeed increased by 1

- On title, Enter or the Start button calls start and goes to playing.
- On title, N or the New Island button increases baseSeed by 1, calls seed with the new baseSeed, and stays on title.
- On playing, Escape calls pressEscape and goes to paused.
- On paused, Escape calls pressEscape and goes to playing.
- On paused, Q or the Quit button sets mode to title.
- On won, Enter or the Sail On button increases baseSeed by 1, calls seed with the new baseSeed, and goes to title.
- pressEscape toggles between playing and paused while mode is playing or paused; in title or won it does nothing.

HUD:

| HUD element | Record field shown |
|---|---|
| Shard counter text "n/5" | Player.shards |
| Gold counter text | Player.gold |
| Day/night icon | DayNight.phase |
| Minimap revealed terrain | IslandMap.revealed |
| Minimap player dot | Player.x, Player.y |
| Minimap cache markers | TreasureCache.state, TreasureCache.visible |
| Minimap Grand Cache marker | TreasureCache.state for the Grand Cache, IslandMap.grandAll |
| Minimap landmark arrows | Landmark.visited, Landmark.clueX, Landmark.clueY |
| Objective text | Player.shards, GameState.mode, IslandMap.grandAll |
| Dig prompt | TreasureCache.state, TreasureCache.visible |
| Treasure text on won screen | Player.gold, Player.treasure |

# 6. AUDIO

Generated with the Web Audio API.

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| shard | sine wave, 880 Hz, duration 0.15 s, attack 0.01 s, release 0.14 s | MapShard changes from unseen to collected |
| openChest | triangle wave, 220 Hz, duration 0.25 s, attack 0.01 s, release 0.24 s | minorGold cache changes to opened |
| dig | square wave, 100 Hz, duration 0.08 s, attack 0.005 s, release 0.075 s | TreasureCache openTimer crosses from greater than 1.0 to less than or equal to 1.0 |
| landmark | sine wave, 660 Hz, duration 0.20 s, attack 0.01 s, release 0.19 s | Landmark changes from visited false to visited true |
| nightCreak | sawtooth wave, 90 Hz, duration 0.40 s, attack 0.05 s, release 0.35 s | DayNight.phase becomes night |
| grandWin | three sine waves together at 523 Hz, 659 Hz, and 784 Hz, duration 0.80 s, attack 0.02 s, release 0.78 s | GameState.mode becomes won |

# 7. ART

- Ask for title_scene as a scene: a top-down fantasy island with a palm tree, a small beach, and a closed chest, painted as one title image.
- Ask for player_walk as an anim, four-way, with four one-subject frames: player_north, player_south, player_east, player_west. Each frame is a top-down explorer with a straw hat and a satchel.
- Ask for chest_closed as a sprite: a wooden chest with brass bands, closed.
- Ask for chest_open as a sprite: the same chest open, with dark interior and no treasure pile inside.
- Ask for map_shard as a sprite: a torn yellow map fragment with a red X.
- Ask for gold_pile as a sprite: a small pile of gold coins.
- Ask for treasure_pile as a sprite: a larger treasure pile with gold coins, jewels, and a crown.
- Ask for lighthouse as a sprite: a white lighthouse with a red top.
- Ask for stone_ruins as a sprite: grey stone ruins with broken columns.
- Ask for old_boat as a sprite: a beached wooden boat.
- Ask for tide_pools as a sprite: a cluster of small blue tide pools with rocks.
- Ask for watch_tower as a sprite: a small wooden watch tower.

RECIPE: Tile drawing uses 12 by 12 pixel squares. water is solid #176c8a. beach is solid #e0c878. grass is solid #78b05a. forest is #4f8a43. rock is #8a8a85.

RECIPE: If a forest tile has decor true, draw a tree: a circle 8 pixels in diameter, colour #3d7a3a, centred on the tile, with a trunk rectangle 2 by 4 pixels, colour #6b4a2b, below the centre. If a rock tile has decor true, draw a boulder: a rounded triangle 8 pixels wide and 6 pixels high, colour #6f6f6a, with a 3 pixel highlight #b5b5b0.

RECIPE: Player sprite is drawn 24 by 24 pixels, centred on Player.x and Player.y, scaled so the feet occupy one tile. The four-way anim uses one frame per facing direction. A code bob moves the sprite 2 pixels up and down over 0.5 seconds while moving.

RECIPE: chest_closed and chest_open are drawn 20 by 16 pixels at cache centres. map_shard, gold_pile, and treasure_pile are drawn 16 by 16 pixels except treasure_pile, which is drawn 32 by 24 pixels on the won screen. Landmark sprites are drawn 24 by 24 pixels at landmark centres.

RECIPE: Minimap is a 128 by 128 pixel rectangle in the top-right corner. Each minimap pixel represents a 2 by 2 tile block. Draw each pixel using the colour of the most common revealed terrain in that block; if no tile is revealed, draw #101418. Player dot is a 2 by 2 pixel white square at Player.x times 0.5 and Player.y times 0.5. Available cache markers are 2 by 2 pixel circles, colour #ffd54a. The Grand Cache marker is a 2 by 2 pixel X, colour #ff3b3b, drawn only when IslandMap.grandAll is true. Visited landmark arrows are 8 pixel triangles, colour #ffd54a, pointing from the landmark pixel toward clueX and clueY.

RECIPE: Night and dusk overlay is a fullscreen black rectangle, colour #000000, with alpha 0 for day, 0.25 for dusk, 0.45 for night, and 0.25 for dawn. A circular hole is cut around the player with radius DayNight.lightRadius times 12 pixels and a soft edge 12 pixels wide.

RECIPE: HUD panel is a rectangle 220 by 40 pixels in the top-left corner, colour #000000 with alpha 0.6. Text is drawn in a monospace font at 12 pixels, colour #ffffff. The dig prompt is drawn centred below the player as a 12 pixel text string "E dig", colour #ffffff.

Everything else — water shimmer, button hover states, sparkle particles, screen shake, text antialiasing — is drawn in code.

# 8. DEBUG API

The game installs window.__game as plain functions.

| Call | What it does | What it returns |
|---|---|---|
| start() | Enters play from title or won. Sets mode to playing, resets time to 0, places Player at spawn, and resets transient inputs. | object with mode |
| step(dt, n) | Advances n ticks of dt seconds without waiting for real time, then draws once. | number time |
| setTime(t) | Advances GameState.time to t seconds without drawing. | number time |
| seed(n) | Sets baseSeed to n, reseeds RNG, rebuilds IslandMap, caches, landmarks, mapshards, fog, day/night, and player, keeping mode if playing or title. | object with baseSeed and finalSeed |
| getState() | Returns the fields of every record as plain data. | object with gameState, island, player, camera, caches, mapShards, landmarks, dayNight |
| setMove(dx, dy) | Sets persistent input direction, clamping dx and dy to -1, 0, or 1. | object with inputX and inputY |
| pressAction() | Sets GameState.pendingAction to true, simulating E or Space. | object with pendingAction true |
| pressEscape() | Toggles paused and playing while in play; otherwise returns current mode unchanged. | string mode |
| setPlayerPosition(x, y) | Sets Player.x and Player.y directly. | object with x and y |
| setTile(x, y, terrain) | Sets IslandMap.tiles[x][y] to terrain and leaves revealed unchanged. | string terrain |
| setRectangle(x0, y0, w, h, terrain) | Sets a rectangular block of tiles to terrain. | number count |
| placeCache(id, x, y, kind) | Creates or modifies cache id at x, y with kind. MinorMap caches take the smallest uncollected MapShard id. Minor and grand caches are visible. Grand cache is available only when Player.shards is 5. | object cache |
| placeLandmark(id, x, y, type) | Creates or modifies landmark id at x, y with type, sets visited false, and sets clue target to the current Grand Cache position. | object landmark |
| setShards(n) | Sets Player.shards to n, collects MapShards 1 through n, uncollects the rest, updates all grand sector fields, sets grandAll true if n is 5, and makes the Grand Cache available if n is 5. | number shards |
| setGold(n) | Sets Player.gold to n. | number gold |
| setDay(phase) | Sets DayNight.phase and its matching speedMult and lightRadius; sets timer to 1 second before the phase end for testing. | string phase |
| clearFog() | Sets every IslandMap.revealed value to true and makes every non-grand hidden cache available; grand cache becomes available only if grandAll is true. | boolean true |
| openCache(id) | Immediately sets cache id to opened and applies its contents. | object cache |
| forceWin() | Sets Player.treasure to true and GameState.mode to won. | string mode |

# 9. TESTS

1. After start(): getState().gameState.mode is "playing", getState().player.x is 248, getState().player.y is 128, getState().gameState.time is 0.
2. After start(), seed(7): getState().gameState.finalSeed is 7, getState().island.width is 256, getState().island.spawnX is 248, getState().island.spawnY is 128, the caches array has 9 entries, and the landmarks array has 5 entries.
3. After start(), seed(7), setRectangle(128, 128, 64, 64, "grass"), setPlayerPosition(128, 128), setMove(1, 0), step(1/60, 60): getState().player.x is 136.0 within 0.001, getState().player.y is 128.0 within 0.001, getState().player.facing is 1.
4. After start(), seed(7), setRectangle(128, 128, 64, 64, "grass"), setTile(130, 128, "water"), setPlayerPosition(128, 128), setMove(1, 0), step(1/60, 60): getState().player.x is 129.6 within 0.001, getState().player.facing is 1.
5. After start(), seed(7), placeCache(1, 132, 128, "minorGold"), setPlayerPosition(132, 128), pressAction(), step(1/60, 120): cache id 1 state is "opened", getState().player.gold is 10, getState().gameState.lastSound is "openChest".
6. After start(), seed(7), setShards(0), placeCache(2, 132, 128, "minorMap"), setPlayerPosition(132, 128), pressAction(), step(1/60, 120): cache id 2 state is "opened", getState().player.shards is 1, mapShard id 1 state is "collected", getState().island.grandNorth is true.
7. After start(), seed(7), placeCache(9, 132, 128, "grand"), setShards(5), setPlayerPosition(132, 128), pressAction(), step(1/60, 180): cache id 9 state is "opened", getState().player.treasure is true, getState().gameState.mode is "won", getState().gameState.lastSound is "grandWin".
8. After start(), seed(7), setRectangle(128, 128, 64, 64, "grass"), setPlayerPosition(128, 128), setDay("night"), setMove(1, 0), step(1/60, 60): getState().player.x is 134.0 within 0.001, getState().dayNight.phase is "night", getState().dayNight.speedMult is 0.75.
9. After start(), seed(7), setPlayerPosition(128, 128), step(1/60, 1): getState().island.revealed[128][128] is true and getState().island.revealed[122][128] is true.
10. After start(), seed(7), placeCache(9, 140, 128, "grand"), placeLandmark(1, 132, 128, "Lighthouse"), setPlayerPosition(132, 128), pressAction(), step(1/60, 1): landmark id 1 visited is true, landmark id 1 clueX is 140, landmark id 1 clueY is 128, getState().gameState.lastSound is "landmark".
11. After start(), seed(7), setPlayerPosition(128, 128), step(1/60, 1): getState().camera.x is 128.0 within 0.001, getState().camera.y is 128.0 within 0.001, getState().camera.zoom is 1.
12. After start(), seed(7), placeCache(1, 132, 128, "minorGold"), setPlayerPosition(132, 128), pressAction(), step(1/60, 60): cache id 1 state is "opening", cache id 1 openTimer is 1.0 within 0.001, getState().gameState.lastSound is "dig".

SCREENSHOTS:

| Screen and state | What a person must see |
|---|---|
| title | The title scene fills the screen, the game name is visible, a Start button is visible, a New Island button is visible, and the controls list shows WASD and E. |
| playing island | The top-down island is visible, the player stands on the east beach, the HUD shows "0/5" shards and "0" gold, the minimap is mostly black with a small revealed beach area in the top-right. |
| near gold cache | A closed chest sprite is visible near the player, the minimap shows a yellow cache marker, and the text "E dig" appears below the player. |
| map shard collected | The HUD shows "1/5" shards, a map fragment icon appears briefly in the HUD, and one sector of the minimap around the hidden Grand Cache area is revealed. |
| night | A dark overlay covers the screen, a circular light area surrounds the player, the day/night icon in the HUD shows a moon, and the player moves slower than in day. |
| won | A large treasure pile is visible, the text "Treasure claimed!" is visible, the gold count matches Player.gold, and a Sail On button is visible. |

# 10. BUILD ORDER

1. Title and first playable island: add IslandGenerator, PlayerMovement, Camera, and title/playing screens. Check 1 shows the title enters play and places the player at spawn.
2. Movement and world collision: finish PlayerMovement terrain speed and water collision, Camera following, and basic tile rendering. Check 3 shows open movement distance and Check 4 shows water clamping.
3. Treasure goal: add TreasureCache, MapShard, Win, cache art, and the won screen. Check 5 shows a gold cache opens, Check 6 shows a map shard collects, and Check 7 shows the Grand Cache wins the game.
4. Exploration and feedback: add FogOfWar, DayNight, LandmarkClues, Sound, minimap arrows, HUD, and audio. Check 8 shows night slows movement, Check 9 shows fog reveals tiles, Check 10 shows landmark clues, Check 11 shows camera following, and Check 12 shows dig sound timing.

Every milestone after the first leaves the game playable.

# 11. DONE

- "An open world game"
  - Checks 2, 3, 8, 11
  - Screenshot rows: playing island, night
- "where you explore an island"
  - Checks 2, 4, 9, 10
  - Screenshot rows: playing island, near gold cache, night
- "and find treasure"
  - Checks 5, 6, 7, 12
  - Screenshot rows: near gold cache, map shard collected, won

# A. SANITY

- Every field read or written by a rule is on a record: closes.
- Every place, thing, or kind named by a rule is placed by IslandGenerator or listed in a roster: closes.
- Terrain kinds water, beach, grass, forest, rock are all in the terrain roster and placed by IslandGenerator: closes.
- Cache kinds minorMap, minorGold, grand are in the cache kind roster and placed by IslandGenerator: closes.
- MapShard ids 1 through 5 are in the MapShard roster and placed through minorMap caches by IslandGenerator: closes.
- Landmark types 1 through 5 are in the landmark roster and placed by IslandGenerator: closes.
- Consumable total: IslandGenerator places five minorMap caches containing five MapShards; the Grand Cache requirement demands five MapShards: closes.
- Gold total: IslandGenerator places three minorGold caches worth 30 gold; no rule demands gold, so gold is score only: closes.
- Timing pair: minor cache open time 2 seconds and Grand Cache open time 3 seconds are longer than one tick and shorter than the 45-second day phase: closes.
- Timing pair: player speed 8 tiles per second crosses the 240-tile island in 30 seconds, shorter than the 85-second full day-night cycle: closes.
- Timing pair: FogOfWar reveal radius 6 tiles is larger than the 3-tile cache visibility radius, so a cache becomes visible before its edge leaves the explored area: closes.
- Timing pair: night lightRadius 8 tiles is larger than FogOfWar reveal radius 6 tiles, so the visible light area always contains the newly revealed exploration radius: closes.
- Every call used in section 9 is listed in section 8: closes.