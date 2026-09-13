# 0. SCOPE

## 0.1 Asked

- “An open world collector game” → a continuous 2D top-down world produced by the World Generator, with free walking, resources, water, buildings, and a shop.
- “The player walks around” → Player record, PlayerMovement system, map collision, and camera following.
- “collecting resources” → ResourceNode records, Fish records, Player inventory fields, HarvestMine system, and Fishing system.
- “harvest berries” → berry node roster, berry inventory fields, berry regrow times, and berry selling.
- “mine ores” → ore node roster, ore inventory fields, ore regrow times, and ore selling.
- “fish fish” → fish roster, water tiles, fish movement, fishing wait, and fish inventory.
- “sell them to a shop keeper for each type” → shopkeeper record, ShopTrade system, sell prices for every resource type, and shop screen.
- “buy furniture to decorate their home and a small museum type building” → furniture roster, home and museum buildings, FurniturePlacement system, display cases, HomeComfort system, and MuseumRating system.

## 0.2 Decisions

- The game is 2D top-down, not 3D, because the best version is about reading one open map, choosing where to gather, and placing furniture in two readable interior floors.
- The world is a bounded 160 metre by 160 metre tile map, not an endless procedural planet, because a bounded open map keeps resource counts, shop progression, and museum completion testable.
- There is no combat, because the request is a collector game and the challenge should come from resource timing, shop progression, and museum building.
- The player carries one furniture item at a time, because carrying one item makes placing, buying, and screen prompts clear without a large inventory UI.
- The museum has a soft completion goal, the Charter Complete state, because a collector game needs a visible milestone, but the game remains open-ended afterward.
- The shopkeeper sells all furniture types from a fixed roster, because the request asks for buying furniture and a fixed roster keeps prices and stock rules explicit.
- The shopkeeper restocks slowly rather than being infinite, because restocking creates a small long-term economic choice.
- Touch controls are virtual buttons and a virtual pad, because a browser game should remain playable on a touch screen without changing the keyboard rules.

## 0.3 Tiers

TIER 1 is the game: Time, WorldGenerator, PlayerMovement, ResourceRegrow, HarvestMine, FishSwim, Fishing, ShopTrade, FurniturePlacement, MuseumRating.

TIER 2, in order: HomeComfort, ShopRestock, MuseumIncome, Completion, Audio, Art.

TIER 3, in order: a first-run tutorial prompt, a collection log screen, ambient music, particle effects on harvest, a settings pause option.

# 1. CONVENTIONS

One game unit is one metre. One metre is drawn as 32 pixels. The world axes are x east/right and y south/down. The origin is the top-left corner of the map at tile 0,0. North is the top of the screen, so moving north decreases y. All ground has height 0.

The camera is top-down, centred on the player, and clamped to the map. The player facing angle is in radians, 0 means east, and positive values turn clockwise on screen.

The update loop uses a fixed step of 1/60 second. Each tick, in this order, the game reads current input, then runs Time, PlayerMovement, ResourceRegrow, FishSwim, Fishing, ShopRestock, MuseumIncome, Completion, and finally renders.

There is one seeded random source named R. Nothing else is random. R is used only by the WorldGenerator and by the FishSwim spawn rule.

Controls:

| Input | Action |
|---|---|
| W or ArrowUp | move north, direction vector 0,-1 |
| S or ArrowDown | move south, direction vector 0,1 |
| A or ArrowLeft | move west, direction vector -1,0 |
| D or ArrowRight | move east, direction vector 1,0 |
| Any combination of held WASD or arrow keys | sum the held directions, then scale to length 1 if needed |
| E | interact |
| B | place carried furniture in play, buy highlighted furniture in shop |
| Escape | pause in play, close shop to play, close pause to play |
| Touch left pad | set the persistent move direction |
| Touch right action button | interact |
| Touch right build button | place carried furniture or buy highlighted furniture |
| Touch top menu button | pause or close a panel |

# 2. RECORDS

RECORDS: GAME, MAP, PLAYER, RESOURCE_NODE, FISH, FURNITURE, SHOPKEEPER, BUILDING.

GAME: seed (integer, starts 7), time (seconds, starts 0), state (title/play/shop/pause, starts title), lakeX (metres, set by generator), lakeY (metres, set by generator), lakeRadius (metres, set by generator), fishSpawnTimer (seconds, starts 0), charterComplete (boolean, starts false).

MAP: width (tiles, 160), height (tiles, 160), tiles (grid of tile kind, generated), waterTiles (list of water tile positions in tile coordinates, generated).

PLAYER: x (metres, starts 50), y (metres, starts 50), facing (radians, starts 0), speed (metres per second, 4), coins (coins, starts 100), redBerry (count, starts 0), blueBerry (count, starts 0), copper (count, starts 0), iron (count, starts 0), crystal (count, starts 0), minnow (count, starts 0), perch (count, starts 0), trout (count, starts 0), salmon (count, starts 0), carryId (furniture id, starts null), interactCooldown (seconds, starts 0), fishTimer (seconds, starts 0).

RESOURCE_NODE: id (integer, unique), kind (resource kind, from roster), x (metres), y (metres), amount (units), maxAmount (units), regrowTimer (seconds), state (ready/regrowing).

FISH: id (integer, unique), kind (fish kind, from roster), x (metres), y (metres), facing (radians), speed (metres per second), state (swimming).

FURNITURE: id (integer, unique), kind (furniture kind, from roster), state (carried/placed), buildingId (home/museum/null), localX (tiles inside building, starts 0), localY (tiles inside building, starts 0), storedKind (resource kind or null).

SHOPKEEPER: x (metres, starts 52), y (metres, starts 38), state (idle/shop), shopTimer (seconds, starts 0), highlight (buy index, starts 0), stockRug (count, starts 3), stockChair (count, starts 3), stockTable (count, starts 3), stockPlant (count, starts 3), stockLamp (count, starts 3), stockShelf (count, starts 3), stockJar (count, starts 3), stockCase (count, starts 3), stockTank (count, starts 3).

BUILDING: id (home/museum), kind (home/museum), x (metres, top-left tile), y (metres, top-left tile), width (metres), height (metres), doorX (local tile), doorY (local tile), comfort (points, starts 0), fame (points, starts 0), star (integer, starts 1), incomeTimer (seconds, starts 0), displayedCount (count, starts 0). The home starts at x 30, y 30, width 12, height 10, doorX 6, doorY 10. The museum starts at x 70, y 40, width 18, height 14, doorX 9, doorY 14.

Tile roster:

| Tile kind | Blocks movement |
|---|---:|
| grass | no |
| water | yes |
| sand | no |
| forest | no |
| rock | no |
| path | no |
| floorHome | no |
| floorMuseum | no |
| wall | yes |

Resource roster:

| Sell key | Kind | Sell price coins | Max amount units | Regrow seconds | Player field | Display fame |
|---:|---|---:|---:|---:|---|---:|
| 1 | berryRed | 5 | 3 | 60 | redBerry | 5 |
| 2 | berryBlue | 8 | 3 | 90 | blueBerry | 8 |
| 3 | oreCopper | 12 | 4 | 240 | copper | 10 |
| 4 | oreIron | 20 | 3 | 360 | iron | 20 |
| 5 | oreCrystal | 50 | 2 | 720 | crystal | 50 |
| 6 | fishMinnow | 4 | not applicable | not applicable | minnow | 5 |
| 7 | fishPerch | 10 | not applicable | not applicable | perch | 10 |
| 8 | fishTrout | 18 | not applicable | not applicable | trout | 20 |
| 9 | fishSalmon | 35 | not applicable | not applicable | salmon | 40 |

Fish roster:

| Kind | Sell price coins | Speed metres per second | Initial count | Display fame |
|---|---:|---:|---:|---:|
| minnow | 4 | 1.5 | 10 | 5 |
| perch | 10 | 1.2 | 8 | 10 |
| trout | 18 | 1.8 | 4 | 20 |
| salmon | 35 | 0.9 | 2 | 40 |

Furniture roster:

| Buy index | Kind | Price coins | Display category | Comfort points | Base fame points |
|---:|---|---:|---|---:|---:|
| 1 | rug | 40 | none | 3 | 0 |
| 2 | chair | 30 | none | 2 | 0 |
| 3 | table | 50 | none | 3 | 0 |
| 4 | plant | 25 | none | 2 | 1 |
| 5 | lamp | 35 | none | 2 | 1 |
| 6 | shelf | 45 | none | 1 | 2 |
| 7 | berryJar | 60 | berry | 0 | 0 |
| 8 | oreCase | 80 | ore | 0 | 0 |
| 9 | fishTank | 100 | fish | 0 | 0 |

# 3. SYSTEMS

SYSTEMS: Time, WorldGenerator, PlayerMovement, ResourceRegrow, HarvestMine, FishSwim, Fishing, ShopTrade, FurniturePlacement, HomeComfort, MuseumRating, ShopRestock, MuseumIncome, Completion.

## Time (T1)

- On every tick, set game.time = game.time + dt.
- On every tick, if game.state is play, shop, or pause, no random value is consumed by Time.

## WorldGenerator (T1)

- On seed(n), set R to seed n, set game.seed = n, set game.time = 0, set game.state = play, reset player to x 50, y 50, speed 4, coins 100, all resource counts 0, carryId null, interactCooldown 0, fishTimer 0, clear ResourceNode, Fish, Furniture records, and reset all shopkeeper stock fields to 3.
- On seed(n), generate the map in this order: fill all 160 by 160 tiles with grass; generate a lake; generate a forest; generate rock; generate path; generate buildings; generate waterTiles; generate resource nodes; generate fish.
- Lake rule: set lakeX = 90 + floor(R() * 31), lakeY = 90 + floor(R() * 31), lakeRadius = 18 + floor(R() * 11). For every tile within Euclidean distance lakeRadius - 2 of lakeX, lakeY, set tile to water. For every tile within distance lakeRadius but outside distance lakeRadius - 2, set tile to sand.
- Forest rule: set forestX = 20 + floor(R() * 21), forestY = 20 + floor(R() * 21), forestRadius = 16 + floor(R() * 11). For every tile within Euclidean distance forestRadius of forestX, forestY, set tile to forest.
- Rock rule: set rockX = 110 + floor(R() * 21), rockY = 40 + floor(R() * 21), rockRadius = 16 + floor(R() * 11). For every tile within Euclidean distance rockRadius of rockX, rockY, set tile to rock.
- Path rule: set path tiles for the following line segments: from tile 50,50 to 50,38 to 52,38; from 52,38 to 36,38 to 36,39; from 50,50 to 79,50 to 79,53. Each segment is one tile wide.
- Buildings rule: set home building x 30, y 30, width 12, height 10; set all interior tiles of the home to floorHome; set all perimeter tiles of the home to wall except the tile at local doorX 6, doorY 10, which is set to path. Set museum building x 70, y 40, width 18, height 14; set all interior tiles of the museum to floorMuseum; set all perimeter tiles of the museum to wall except the tile at local doorX 9, doorY 14, which is set to path.
- waterTiles rule: after final tiles are placed, collect every tile with kind water into MAP.waterTiles.
- Resource node rule: place 8 berryRed nodes on distinct forest tiles, 8 berryBlue nodes on distinct forest tiles, 8 oreCopper nodes on distinct rock tiles, 6 oreIron nodes on distinct rock tiles, and 4 oreCrystal nodes on distinct rock tiles. Use R to choose an unused tile of the required kind for each node. Set each node x and y to the chosen tile centre in metres, set maxAmount from the resource roster, set amount = maxAmount, set state ready, and set regrowTimer = 0.
- Fish rule: sort MAP.waterTiles by Euclidean distance to lakeX, lakeY, nearest first. Assign the first 2 tiles to salmon, the next 4 tiles to trout, the next 8 tiles to perch, and the next 10 tiles to minnow. For each fish, set x and y to the chosen water tile centre in metres, set speed from the fish roster, set facing = R() * 2 * PI, and set state swimming.
- Verifier rule: the generated world must have at least 24 water tiles, at least 16 forest tiles, at least 18 rock tiles, at least 10 interior floor tiles in the home, at least 10 interior floor tiles in the museum, the player spawn tile 50,50 must not be water or wall, the shopkeeper tile 52,38 must not be water or wall, every resource node must be on its required tile kind, and every fish must be on a water tile.
- Re-roll rule: if any verifier check fails, increment n by 1 and repeat the entire WorldGenerator sequence from the lake rule with the new n. Set game.seed to the n that passed.

## PlayerMovement (T1)

- If game.state is not play, PlayerMovement does nothing.
- On every tick, if the current input direction vector length is greater than 1, scale it to length 1.
- On every tick, propose newX = player.x + dirX * player.speed * dt and newY = player.y + dirY * player.speed * dt.
- If the tile at newX, player.y is traversable, set player.x = newX; otherwise keep player.x.
- If the tile at player.x, newY is traversable, set player.y = newY; otherwise keep player.y.
- If the direction vector is not 0,0, set player.facing = atan2(dirY, dirX).
- On every tick, set player.interactCooldown = max(0, player.interactCooldown - dt).

## ResourceRegrow (T1)

- On every tick, for each ResourceNode with state regrowing, set regrowTimer = regrowTimer - dt.
- If a regrowing node has regrowTimer <= 0, set amount = maxAmount and set state ready.

## HarvestMine (T1)

- On interact() while game.state is play, if player.interactCooldown > 0, do nothing.
- On interact(), find the nearest target within 2.0 metres among the shopkeeper, a placed Furniture with storedKind null and a matching nonempty display category, a ResourceNode with amount > 0, and a water edge. A water edge is true if the nearest water tile is within 1.5 metres of the player. Tie by this order: shopkeeper, display, resource, water.
- If the target is the shopkeeper, set game.state = shop and set shopkeeper.state = shop.
- If the target is a ResourceNode, set player.interactCooldown = 0.3, set node.amount = node.amount - 1, increase the matching player inventory field by 1, and if node.amount becomes 0, set node.state = regrowing and set node.regrowTimer to the roster regrow seconds.
- If the target is a display Furniture, set player.interactCooldown = 0.3. Choose the inventory item of the furniture display category with the highest sell price. If one exists, set furniture.storedKind to that resource kind, decrease that player inventory field by 1, and run MuseumRating if the furniture is in the museum or HomeComfort if the furniture is in the home.
- If the target is a water edge and player.fishTimer is 0, set player.fishTimer = 2.0.

## FishSwim (T1)

- On every tick, for each Fish, propose newX = x + cos(facing) * speed * dt and newY = y + sin(facing) * speed * dt.
- If the tile at newX, newY is water, set the fish x and y to newX and newY.
- If the proposed tile is not water, set the fish facing = atan2(game.lakeY - y, game.lakeX - x) + 0.4 * (id mod 5 - 2), then re-propose the move. If the re-proposed tile is water, move the fish; otherwise keep the fish position.
- On every tick, set game.fishSpawnTimer = game.fishSpawnTimer + dt.
- If game.fishSpawnTimer >= 30 and the total Fish count is less than 24, set game.fishSpawnTimer = 0, choose a kind by r = R(): minnow if r < 0.45, perch if r >= 0.45 and r < 0.75, trout if r >= 0.75 and r < 0.95, salmon if r >= 0.95; choose a water tile index = floor(R() * MAP.waterTiles.length); set the new fish x and y to that tile centre; set facing = R() * 2 * PI; set speed from the fish roster; set state swimming.

## Fishing (T1)

- On every tick, if player.fishTimer > 0, set player.fishTimer = player.fishTimer - dt.
- When player.fishTimer reaches 0 or less, find the nearest Fish within 6.0 metres. If tied, choose the highest fish id. If one is found, remove that fish, increase the matching player inventory field by 1, and set player.fishTimer = 0. If none is found, set player.fishTimer = 0.

## ShopTrade (T1)

- If game.state is not shop, ShopTrade does nothing except allowing interact to open the shop through HarvestMine.
- While game.state is shop, if number key 1 through 9 is pressed, map it to the resource roster sell key, and if that player inventory field is greater than 0, set player.coins = player.coins + count * roster sell price, then set that count to 0.
- While game.state is shop, if ArrowLeft is pressed, set shopkeeper.highlight = (shopkeeper.highlight + 8) mod 9.
- While game.state is shop, if ArrowRight is pressed, set shopkeeper.highlight = (shopkeeper.highlight + 1) mod 9.
- While game.state is shop, if B is pressed, buy the furniture kind at the highlighted buy index if player.carryId is null, that shopkeeper stock field is greater than 0, and player.coins is at least the effective price.
- Effective price rule: set discount = 0 if home comfort < 10; set discount = 5 if comfort >= 10 and < 25; set discount = 10 if comfort >= 25 and < 50; set discount = 15 if comfort >= 50 and < 100; set discount = 20 if comfort >= 100. Set effectivePrice = floor(base price * (100 - discount) / 100).
- On successful purchase, create a Furniture with state carried, buildingId null, localX 0, localY 0, storedKind null; decrement the matching stock field by 1; set player.coins = player.coins - effectivePrice; set player.carryId to the new furniture id.
- While game.state is shop, if Escape or E is pressed, set game.state = play and set shopkeeper.state = idle.

## FurniturePlacement (T1)

- On B while game.state is play, if player.carryId is null, do nothing.
- Set target tile x = floor(player.x), target tile y = floor(player.y).
- If the target tile is floorHome or floorMuseum, identify the building whose interior contains the target tile.
- If no placed Furniture already has the same buildingId, localX, and localY, set the carried furniture state to placed, set its buildingId to that building, set localX = target tile x - building.x, set localY = target tile y - building.y, and set player.carryId = null.
- If the target tile is not furniture floor or the target local tile is occupied, do nothing.

## HomeComfort (T2)

- On any furniture placement in the home, set the home building comfort field to the sum of the roster comfort points of all placed furniture in the home.

## MuseumRating (T1)

- On any furniture placement in the museum or any display fill in the museum, set the museum fame field to the sum of base fame points for all placed furniture in the museum plus the display fame from the resource or fish roster for each placed museum furniture whose storedKind is not null.
- At the same time, set the museum displayedCount field to the number of placed museum furniture whose storedKind is not null.
- Set the museum star field: 1 if fame < 50, 2 if fame >= 50 and < 150, 3 if fame >= 150 and < 400, 4 if fame >= 400 and < 1000, 5 if fame >= 1000.

## ShopRestock (T2)

- On every tick, set shopkeeper.shopTimer = shopkeeper.shopTimer + dt.
- If shopkeeper.shopTimer >= 300, set shopkeeper.shopTimer = 0, and for each stock field set the stock value to min(8, stock value + 1).

## MuseumIncome (T2)

- On every tick, set the museum building incomeTimer = incomeTimer + dt.
- If incomeTimer >= 60, set incomeTimer = 0 and set player.coins = player.coins + (museum.star * 2) + museum.displayedCount.

## Completion (T2)

- On every tick after MuseumRating is current, if game.charterComplete is false, check the museum for at least one placed berryJar with storedKind not null, one placed oreCase with storedKind crystal, one placed fishTank with storedKind salmon, and museum fame >= 150.
- If all those conditions are true, set game.charterComplete = true.

# 4. CORE LOOP

Minute to minute, the player moves with PlayerMovement to a berry, ore, or water edge. Time advances. ResourceRegrow restores depleted nodes. FishSwim moves fish and slowly refills the lake. HarvestMine turns berries and ores into inventory, and Fishing turns water time into fish. The player walks to the shopkeeper, opens ShopTrade, sells one or more resource types for coins, and buys a furniture item. FurniturePlacement puts that item in the home or museum. HomeComfort raises home comfort, which lowers shop prices. MuseumRating raises museum fame, displayedCount, and star level. ShopRestock returns furniture to stock over time. MuseumIncome pays small recurring museum income. The player then gathers again, fills more displays, and buys more furniture. What grows is coins, furniture, home comfort, museum fame, star level, and museum income. What unlocks is better discounts, higher stars, more income, and finally the Charter Complete state. The game has no failing end. The visible end is Charter Complete, after which the world remains playable for continued collecting, decorating, and raising the museum to 5 stars.

# 5. SCREENS

State machine: title (shows title and start prompt) → play (shows world and HUD) → shop (shows sell and buy panel) → play; play → pause (shows pause panel) → play; pause → title if title is chosen.

- Title: Enter or E starts play. Escape does nothing.
- Play: E opens the shop only near the shopkeeper. B places carried furniture. Escape opens pause.
- Shop: number keys 1 through 9 sell the matching resource type. ArrowLeft and ArrowRight move the buy highlight. B buys the highlighted furniture. Escape or E returns to play.
- Pause: Escape returns to play. Enter returns to title.

HUD:

| HUD element | Record field |
|---|---|
| Coin counter | player.coins |
| Red berry count | player.redBerry |
| Blue berry count | player.blueBerry |
| Copper count | player.copper |
| Iron count | player.iron |
| Crystal count | player.crystal |
| Minnow count | player.minnow |
| Perch count | player.perch |
| Trout count | player.trout |
| Salmon count | player.salmon |
| Carried item name | furniture.kind where furniture.id is player.carryId |
| Home comfort | building.home.comfort |
| Museum fame | building.museum.fame |
| Museum star | building.museum.star |
| World time | game.time |
| Charter complete badge | game.charterComplete |

# 6. AUDIO

Generated with Web Audio API:

| Sound name | Recipe | Rule that plays it |
|---|---|---|
| ui_click | triangle wave, 660 Hz, 0.05 seconds, attack 0.01 seconds, decay 0.04 seconds | any screen state change |
| harvest | square wave, 220 Hz, 0.12 seconds, attack 0.01 seconds, decay 0.11 seconds | a resource node amount decreases |
| fish_splash | sine wave, 180 Hz, 0.25 seconds, attack 0.01 seconds, decay 0.24 seconds | player.fishTimer is set to 2.0 |
| catch | triangle wave, 784 Hz, 0.15 seconds, attack 0.01 seconds, decay 0.14 seconds | a fish is removed by Fishing |
| coin | sine wave, 988 Hz, 0.08 seconds, attack 0.01 seconds, decay 0.07 seconds | player.coins increases from selling |
| buy | sine wave, 392 Hz, 0.10 seconds, attack 0.01 seconds, decay 0.09 seconds | a furniture purchase succeeds |
| place | triangle wave, 440 Hz, 0.10 seconds, attack 0.01 seconds, decay 0.09 seconds | a furniture placement succeeds |
| error | square wave, 110 Hz, 0.15 seconds, attack 0.01 seconds, decay 0.14 seconds | a failed interact, buy, or place |
| star | sine wave, 1047 Hz, 0.30 seconds, attack 0.02 seconds, decay 0.28 seconds | museum.star increases or game.charterComplete becomes true |

# 7. ART

Ask for a top-down cartoon forager in a green tunic as a sprite. Ask for a top-down cartoon shopkeeper in a blue apron as a sprite. Ask for a top-down red berry bush as a sprite. Ask for a top-down blueberry bush as a sprite. Ask for a top-down copper ore rock as a sprite. Ask for a top-down iron ore rock as a sprite. Ask for a top-down glowing crystal ore rock as a sprite. Ask for a top-down minnow as a sprite. Ask for a top-down perch as a sprite. Ask for a top-down trout as a sprite. Ask for a top-down salmon as a sprite. Ask for a top-down round rug as a sprite. Ask for a top-down wooden chair as a sprite. Ask for a top-down wooden table as a sprite. Ask for a top-down potted plant as a sprite. Ask for a top-down standing lamp as a sprite. Ask for a top-down wooden shelf as a sprite. Ask for a top-down berry jar display as a sprite. Ask for a top-down ore display case as a sprite. Ask for a top-down fish tank display as a sprite.

No animation assets are requested. Each sprite is one subject with a transparent background.

RECIPE: each tile is 32 by 32 pixels. Grass fill is #6aa84f. Water fill is #3f7fbf. Sand fill is #e0c98f. Forest fill is #4f8c3a. Rock fill is #7a7f87. Path fill is #c2a27a. Home floor fill is #d7b899. Museum floor fill is #9db0c4. Wall fill is #6d4c33.

RECIPE: on each water tile, draw three concentric ripple circles with radii 4, 8, and 12 pixels in #6ea3d1, offset by sine of game.time * 2 plus tile x times 2 pixels horizontally and cosine of game.time * 2 plus tile y times 2 pixels vertically.

RECIPE: resource node sprites are drawn 48 pixels wide and 48 pixels tall, centred on the node tile. Fish sprites are drawn 32 pixels wide and 18 pixels tall, centred on the fish position. Furniture sprites are drawn 48 pixels wide and 48 pixels tall, centred on their local tile.

RECIPE: the player sprite is drawn 40 pixels wide and 48 pixels tall, centred on player.x, player.y, with a 2 pixel vertical bob at 2 cycles per second while the input direction is not 0,0.

RECIPE: the selection ring is a circle 28 pixels in diameter, stroke 2 pixels wide, colour #ffffff, drawn around the nearest interactable target while one is within 2.0 metres.

RECIPE: the main HUD panel is a rectangle 320 pixels wide and 210 pixels tall, fill #222b33, border 2 pixels #51606d, text colour #f4f1ea, font size 14 pixels.

RECIPE: the shop panel is a rectangle 640 pixels wide and 420 pixels tall, fill #263038, border 2 pixels #51606d, with a sell column 260 pixels wide and a buy column 320 pixels wide.

RECIPE: the pause panel is a rectangle 420 pixels wide and 260 pixels tall, fill #1f2730, border 2 pixels #51606d.

RECIPE: the Charter Complete banner is a rectangle 520 pixels wide and 90 pixels tall, fill #3a5f4b, border 2 pixels #8fd1a6, text colour #f4f1ea, font size 22 pixels.

Everything else — tile map, water ripples, selection ring, HUD panel, shop panel, pause panel, banner, player bob, fish orientation, furniture shadows, path edges, wall shadows, and prompt text — is drawn in code.

# 8. DEBUG API

| Call | What it does | What it returns |
|---|---|---|
| start() | enters play from title without a click | true |
| step(dt, n) | advances n ticks of dt seconds without waiting for real time, then draws once | true |
| setTime(t) | advances the fixed-step loop to absolute time t seconds without drawing; if t is before current time, do nothing | true |
| seed(n) | reseeds R to n, rebuilds generated world records, resets player and shop stock, and sets state to play | true |
| getState() | returns plain data for game, map summary, player, resourceNodes, fish, furniture, shopkeeper, and buildings | plain object |
| setMove(dx, dy) | sets the player’s persistent input direction; clamps dx and dy to -1 through 1 | true |
| setPlayer(x, y) | sets player.x and player.y to metres | true |
| interact() | performs the E action once | true |
| place() | performs the B action once | true |
| sellResource(kind) | sells all of that resource kind at its roster sell price regardless of screen state | coins gained |
| buyFurniture(kind) | buys one furniture kind directly if stock and coins allow and player.carryId is null | new furniture id or 0 |
| setCoins(n) | sets player.coins to n | true |
| giveResource(kind, n) | adds n to the matching player inventory field | true |
| setCarry(kind) | if player.carryId is null, creates a carried furniture of that kind without cost; otherwise do nothing | new furniture id or 0 |
| setResourceAmount(nodeId, amount) | sets the node amount; if amount is less than maxAmount, set state regrowing and regrowTimer to roster regrow seconds; if amount equals maxAmount, set state ready and regrowTimer 0 | true |
| spawnFishAt(kind, x, y) | spawns a fish of that kind at the given water tile, snapping to the nearest water tile if needed | new fish id |
| toWaterEdge() | moves the player to a traversable tile adjacent to water and returns a water tile position near the player | plain object with x and y |
| toHome() | sets the player to home interior world tile 36,35 | true |
| toMuseum() | sets the player to museum interior world tile 76,46 | true |
| placeFurniture(kind, buildingId, localX, localY) | creates placed furniture directly in that building local tile and updates rating or comfort | new furniture id |
| fillDisplay(furnitureId, kind) | if the furniture display category matches kind and the player has at least one of kind, set storedKind, decrease player inventory by 1, and update rating | true |
| restockShop() | runs one ShopRestock cycle immediately | true |
| triggerIncome() | runs one MuseumIncome cycle immediately | coins added |
| setFame(n) | sets museum fame to n, updates museum star, and runs Completion | true |
| setComfort(n) | sets home comfort to n and updates shop discount state | true |
| completeCharter() | sets game.charterComplete true | true |
| tileAt(x, y) | returns the tile kind at tile coordinates x, y | tile kind string |

# 9. TESTS

1. start(), seed(7), step(1/60, 1). Then getState().game.state is play, getState().game.time is at least 1/60, getState().map.width is 160, getState().resourceNodes.length is 34, getState().fish.length is 24, and getState().player.x is between 48 and 52.
2. start(), seed(7), setPlayer(50, 60), setMove(1, 0), step(1/60, 60). Then getState().player.x is at least 53.5 and getState().player.y is 60.
3. start(), seed(7), let node be the first getState().resourceNodes item with kind berryRed, let old be node.amount, setPlayer(node.x, node.y), interact(), step(1/60, 1). Then getState().player.redBerry is 1 and the node with node.id has amount old - 1.
4. start(), seed(7), let node be the first getState().resourceNodes item with kind oreCopper, let old be node.amount, setPlayer(node.x, node.y), interact(), step(1/60, 1). Then getState().player.copper is 1 and the node with node.id has amount old - 1.
5. start(), seed(7), let w be toWaterEdge(), spawnFishAt(minnow, w.x, w.y), interact(), step(1/60, 120). Then getState().player.minnow is 1 and getState().fish.length is 24.
6. start(), seed(7), for each resource roster kind in order: giveResource(kind, 1), sellResource(kind). Then getState().player.coins is 262 and every player resource count is 0.
7. start(), seed(7), setCoins(500), buyFurniture(rug). Then getState().furniture.length is 1, getState().player.carryId is 1, getState().shopkeeper.stockRug is 2, and getState().player.coins is 460.
8. start(), seed(7), setCoins(500), buyFurniture(rug), toHome(), place(). Then the furniture with id 1 has state placed, buildingId home, localX 6, localY 5; getState().player.carryId is null; the home building comfort is 3; and getState().player.coins is 460.
9. start(), seed(7), let id be placeFurniture(berryJar, museum, 2, 2), giveResource(blueBerry, 1), fillDisplay(id, blueBerry). Then the museum building fame is 8, displayedCount is 1, and getState().player.blueBerry is 0.
10. start(), seed(7), setFame(400), triggerIncome(). Then getState().player.coins is 108.
11. start(), seed(7), restockShop(). Then getState().shopkeeper.stockRug is 4 and getState().shopkeeper.stockTank is 4.
12. start(), seed(7), setComfort(25), setCoins(100), buyFurniture(rug). Then getState().player.coins is 64 and getState().shopkeeper.stockRug is 2.
13. start(), seed(7), giveResource(blueBerry, 1), giveResource(crystal, 1), giveResource(salmon, 1), let idJar be placeFurniture(berryJar, museum, 1, 1), let idCase be placeFurniture(oreCase, museum, 2, 1), let idTank be placeFurniture(fishTank, museum, 3, 1), fillDisplay(idJar, blueBerry), fillDisplay(idCase, crystal), fillDisplay(idTank, salmon), setFame(150), step(1/60, 1). Then getState().game.charterComplete is true.
14. start(), seed(7), let node be the first getState().resourceNodes item with kind berryRed, setResourceAmount(node.id, 0), setTime(61). Then the node with node.id has amount 3 and state ready.
15. start(), seed(7), let old be the fish with id 1 in getState().fish, step(1/60, 60). Then the distance between the old x,y and the current x,y of fish id 1 is at least 0.5 metres.

SCREENSHOTS:

| Screen and state | What a person must see |
|---|---|
| Title screen | game title, start prompt, and a readable background map or scene behind the panel |
| Play, outdoors | player sprite on a tile map, water lake, berry and ore sprites, HUD coins and resource counts |
| Play, carrying furniture | carried item name in HUD, selection ring or prompt for B place, and the carried furniture visible near the player or as an HUD icon |
| Shop screen | shopkeeper sprite, sell list for all nine resource types, buy list for all nine furniture types, highlighted buy item, and current coins |
| Pause screen | pause panel with resume and title options over the play view |
| Charter Complete | banner showing Charter Complete, museum fame and star visible, and at least one display case filled in the museum |

# 10. BUILD ORDER

1. Page, title, world, player: add page, title screen, WorldGenerator, PlayerMovement, camera, and basic tile drawing. Check 1 and 2 show it landed.
2. Gathering: add ResourceNode records, HarvestMine, ResourceRegrow, and resource HUD counts. Check 3, 4, and 14 show it landed.
3. Fishing: add Fish records, FishSwim, Fishing, water edge interaction, and fish HUD counts. Check 5 and 15 show it landed.
4. Shop: add shopkeeper, ShopTrade, shop screen, sell prices, furniture buying, stock, and discount. Check 6, 7, 11, and 12 show it landed.
5. Buildings and decoration: add home and museum interior floors, FurniturePlacement, HomeComfort, MuseumRating, and display filling. Check 8 and 9 show it landed.
6. Progression and presentation: add ShopRestock, MuseumIncome, Completion, audio, art, HUD polish, and pause. Check 10 and 13 show it landed.

# 11. DONE

- “An open world collector game” is true when Check 1 passes and the play screenshot shows a continuous map with resources and water.
- “The player walks around” is true when Check 2 passes and the play screenshot shows the player sprite on the map.
- “collecting resources” is true when Checks 3, 4, and 5 pass and the play HUD shows inventory counts.
- “harvest berries” is true when Check 3 passes and the play screenshot shows berry sprites.
- “mine ores” is true when Check 4 passes and the play screenshot shows ore sprites.
- “fish fish” is true when Checks 5 and 15 pass and the play screenshot shows fish in water.
- “sell them to a shop keeper for each type” is true when Check 6 passes and the shop screenshot shows the sell list for every type.
- “buy furniture to decorate their home and a small museum type building” is true when Checks 7, 8, 9, 12, and 13 pass and the carrying, shop, and Charter Complete screenshots show furniture and displays.

# A. SANITY

- Every field a rule reads or writes is on a record: player.fishTimer, node.regrowTimer, shopkeeper.shopTimer, building.incomeTimer, building.fame, building.displayedCount, furniture.storedKind, and all inventory fields are defined in section 2. Result: closes.
- Every place, thing, or kind a rule names is placed by a generator or listed in a roster: tile kinds are in the tile roster; resource kinds are in the resource roster; fish kinds are in the fish roster; furniture kinds are in the furniture roster; nodes and fish are placed by WorldGenerator; buildings and shopkeeper are fixed records. Result: closes.
- Consumables close against the core loop: nodes regrow after depletion; fish are capped at 24 and respawn every 30 seconds while below the cap; shop stock is capped at 8 and restocks every 300 seconds, while the player can carry only one furniture at a time. Result: closes.
- Timing pairs close: player speed 4 metres per second crosses the 160 metre map in 40 seconds; fishing wait is 2 seconds and catch radius is 6 metres while maximum fish speed is 1.8 metres per second, so a fish starting within 1.5 metres cannot move farther than 5.1 metres away; berry regrow is 60 seconds and ore regrow is 240 to 720 seconds against 0.3 second interact cooldown; shop restock is 300 seconds against one-at-a-time carrying; museum income is 60 seconds against fame and display progression. Result: closes.
- Every call in section 9 is in section 8: start, seed, step, getState, setPlayer, setMove, interact, sellResource, giveResource, setCoins, buyFurniture, toWaterEdge, spawnFishAt, toHome, place, placeFurniture, fillDisplay, setResourceAmount, setTime, setFame, triggerIncome, restockShop, and setComfort are all listed. Result: closes.