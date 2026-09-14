# gameplay.md

## 1. Game Definition

**Working title:** *Island of the Hidden Hoard*  
**Genre:** Open-world exploration / puzzle-action  
**Platform assumption:** Browser  
**Dimensionality:** **2.5D isometric**  
**Session length:** **15–25 minutes**  
**Fantasy:** You are a shipwrecked salvager on a tide-locked island. Explore the island, find five Tide Keys, read their distance clues, time the low tide, and open the hidden vault.

**Core fantasy:** A careful, spatial treasure hunt. The player is not fighting enemies; the player is reading the island.

**Core loop:**
1. Move and explore the island.
2. Discover landmarks and sectors.
3. Find five Tide Key caches.
4. Each of the first four keys adds a clue ring to the Hoard Map.
5. After four geometric clues, the exact vault marker appears.
6. With all five keys and low tide, open the vault.
7. Collect the final treasure and end the game.

**Important decision: 2.5D, not 3D.**  
The game is about reading terrain, tide depth, elevation, and map clues. A fixed isometric camera makes lowland flooding, cliffs, landmarks, and clue rings much easier to understand than a free 3D camera. It is also better for browser performance and UI clarity.

---

## 2. Dimensionality

**Choice:** **2.5D**

**Definition:**
- 2D top-down movement on a tile grid.
- 2.5D rendered elevation using tile height and shadows.
- Fixed isometric camera.
- No camera rotation.
- No first-person view.
- No free 3D camera navigation.

**Why this dimensionality:**
- Tide flooding must be readable at a glance.
- Elevation differences must communicate what can be climbed.
- Map clues and rings must align cleanly with the world.
- A browser open-world game should avoid expensive free 3D navigation.
- The game’s main puzzle is spatial, not reflex-based.

---

## 3. Space and Layout

### 3.1 World Size

- World: **256 x 256 tiles**
- 1 tile = **1 meter**
- Coordinate system:
  - x increases right
  - y increases down
- Playable island is inside the square.
- Outer **8 tiles** are ocean border.
  - Ocean border is impassable.
  - It exists to visually contain the island and prevent edge cases.

### 3.2 Elevation Tiles

Tiles have integer elevation **0 to 5**.

| Elevation | Meaning | Tide behavior |
|---:|---|---|
| 0 | Beach, shallow shelf, cave floor | Dry at low tide; flooded at high tide |
| 1 | Lowland, flats, jungle floor, ruin floor | Shallow at high tide, passable but slow |
| 2 | Hills, ruins, rocky outcrops | Dry at high tide |
| 3 | Ridge paths | Dry |
| 4 | High cliff paths | Dry |
| 5 | Cliff tops | Dry |

**Movement rule:**
- Player can move between adjacent tiles if elevation difference is **1 or less**.
- Elevation difference of **2 or more** blocks movement.

**Why:**  
This makes cliffs readable without needing health, falling damage, or complex physics.

---

### 3.3 Tide and Water Depth

The island has a continuous tide system.

**Tide formula:**

```text
waterLevel = 1 - cos(2π * t / 120)
```

- `t` = elapsed seconds since game start
- Water level range: **0 to 2**
- Cycle time: **120 seconds**
- Low tide at `t = 0`
- High tide at `t = 60`
- Low tide again at `t = 120`

**Tile water depth:**

```text
depth = max(0, waterLevel - elevation)
```

**Passability:**
- If `depth <= 1.0`, tile is passable.
- If `depth > 1.0`, tile is deep water and impassable.

**Tide states for UI:**
- **Low:** water level `< 0.7`
- **Rising/Mid:** water level `0.7` to `1.3`
- **High:** water level `> 1.3`

**Why tide matters:**
- Low tide exposes secret shelves and the vault.
- High tide forces players onto higher ground.
- Tide creates time pressure without adding health or combat.
- It is the main “danger” system, but it is avoidable and readable.

---

### 3.4 Island Sectors

The island is one connected open world divided into six authored sectors.

The base layout is fixed. A per-run seed only varies minor coin positions and small cache offsets. The critical progression path is not procedurally generated because the game must always be completable and smooth.

| Sector | Role | General Location |
|---|---|---|
| Driftwood Cove | Start, tutorial, first key | Southwest beach |
| Gull Flats | Low-tide secret | South coast |
| Palm Hollow | Jungle interior and first interaction puzzle | West/center |
| Sunken Ruins | Coastal ruins and movement puzzle | East coast |
| Cliffpath Ridge | High-ground final key | North |
| Vault Point | Final sea cave and treasure | Southeast |

---

## 4. Core Progression

### 4.1 Progression States

```text
START
  -> TUTORIAL_KEY1
  -> FREE_KEYS_1_OF_5
  -> FREE_KEYS_2_OF_5
  -> FREE_KEYS_3_OF_5
  -> FREE_KEYS_4_OF_5
  -> FREE_KEYS_5_OF_5
  -> VAULT_READY
  -> VAULT_OPEN
  -> GAME_COMPLETE
```

### 4.2 Key Structure

There are **5 Tide Keys**.

| Key | Sector | Clue Type | Interactable When |
|---:|---|---|---|
| 1 | Driftwood Cove | Distance clue | Always |
| 2 | Gull Flats | Distance clue | After Key 1 |
| 3 | Palm Hollow | Distance clue | After Key 1 |
| 4 | Sunken Ruins | Distance clue | After Key 1 |
| 5 | Cliffpath Ridge | No distance clue; unlock key | After Key 1 |

**Important rule:**  
Keys 2 through 5 are sealed until Key 1 is collected.

**Why:**  
The first key teaches the map, clue rings, and the core loop. This prevents the player from wandering into a late sector without understanding the game.

---

### 4.3 Clue System

The vault location, `V`, is fixed in the base layout.

Each of Keys 1 through 4 gives a distance clue:

```text
The treasure is D paces from [Landmark].
```

When collected, the Hoard Map displays a **clue ring** centered on that landmark.

**Clue ring display:**
- Inner radius: `D - 6`
- Outer radius: `D + 6`
- The player does not measure anything manually.
- The map shows the overlap visually.

**Progression by clue count:**

| Geometric Clues Collected | Map Result |
|---:|---|
| 0 | No clue rings |
| 1 | One large search ring |
| 2 | Two rings overlap |
| 3 | Overlap becomes small |
| 4 | Exact vault marker appears |

**Vault unlock rule:**
- Exact vault marker appears when **4 geometric clues** are collected.
- Vault can be opened when **5 total keys** are collected and tide is low.

**Why rings instead of manual bearings:**  
The game is a browser game with a short session. Manual distance measuring would be tedious and frustrating. Visual ring overlap gives the same puzzle feel with much lower friction.

---

### 4.4 Objectives

| Game State | Objective Text |
|---|---|
| Start | “Open the shipwreck barrel.” |
| 1/5 keys | “Find the Tide Keys. 1/5” |
| 2/5 keys | “Find the Tide Keys. 2/5” |
| 3/5 keys | “Find the Tide Keys. 3/5” |
| 4/5 keys | “Find the Tide Keys. 4/5” |
| 5/5 keys | “Open the vault at low tide.” |
| Complete | “Treasure found.” |

---

## 5. Systems

## 5.1 Movement and Stamina

### Controls

| Input | Action |
|---|---|
| WASD / Arrow Keys | Move |
| Shift | Run |
| M or Right Mouse | Hold to open map |
| E / Enter | Interact |

### Movement

Player movement is tile-based with smooth float position.

**Speeds:**
- Dry walking: **3.0 tiles/sec**
- Dry running: **5.0 tiles/sec**
- Shallow water: **2.0 tiles/sec**
- Shallow water with 0 stamina: **1.5 tiles/sec**
- Deep water: impassable

**Rules:**
- Running is only allowed on dry land.
- Running requires `stamina > 0`.
- The player cannot run in water.
- The player can always walk, even with 0 stamina.

### Stamina

- Max stamina: **100**
- Running drain: **12 stamina/sec**
- Swimming drain: **10 stamina/sec**
- Regen when not draining: **20 stamina/sec**

**Rules:**
- If stamina reaches 0:
  - Running is disabled.
  - Swimming speed drops to **1.5 tiles/sec**.
  - The player cannot die.
  - The player can still move slowly.

**Why no health:**  
The game is exploration and puzzle progression. Health would add failure states that do not serve the treasure-hunt fantasy. Stamina creates resource awareness without punishment.

---

## 5.2 Tide System

The tide is global and continuous.

**Important tide events:**
- Tide warning **10 seconds** before crossing into Rising or High.
- Low tide is required to open the vault.
- Some shelves and coins are only reachable at low tide.

### Safe Displacement

If the player’s current tile becomes deep water because the tide rises, the game performs a safe displacement.

**Algorithm:**
1. Check current tile passability every frame.
2. If current tile is impassable:
   - Search for nearest passable tile within **16 tiles**.
   - Move player there.
   - Cancel any active interaction channel.
3. If no passable tile is found within 16 tiles:
   - Teleport player to `lastHighSafeTile`.
4. If `lastHighSafeTile` does not exist:
   - Teleport player to start tile.
5. Do not remove keys, coins, or progress.

`lastHighSafeTile`:
- Updated whenever the player is on a tile with elevation `>= 1`.
- This tile is passable at high tide.
- The start tile is elevation 1 and is always the fallback safe tile.

**Why safe displacement:**  
The player should never be stranded by the tide. Tide is a planning problem, not a death trap.

---

## 5.3 Map, Fog of War, and Landmarks

### Map Reveal

- Reveal radius: **10 tiles**
- Reveal happens when player enters a new tile.
- Line of sight is used.
- Once revealed, a tile remains revealed forever.

**Line of sight rule:**
- A ray is cast from player tile to target tile.
- If an intermediate tile has elevation greater than the player’s elevation by more than 1, the target is blocked.
- Water does not block visibility.

### Landmarks

Landmarks are discoverable world objects.

- Landmark visible from distance: **24 tiles**
- Once discovered, landmark remains on map.
- Landmarks are used by clue rings.

**Landmarks:**
- Shipwreck
- Gull Flats Lighthouse
- Palm Hollow Idol
- Sunken Arch
- Cliffpath Eagle Rock
- Vault Point Reef

### Cache Hunt Areas

Each key sector has a cache.

When:
- Key 1 is collected, and
- the sector’s main landmark is discovered,

then the Hoard Map shows a **hunt area circle** around the uncollected cache.

- Hunt area radius: **24 tiles**
- The exact cache prop becomes visible when the player is within **8 tiles** and has line of sight.

**Why hunt areas exist:**  
The game is open-world, but it is short and should not become a search-fail state. The player is guided enough to finish, but still has to physically explore each sector.

---

## 5.4 Caches and Keys

There are **5 caches**.

Each cache contains:
- 1 Tide Key
- 10 coins

Keys 2–5 are sealed until Key 1 is collected.

### Cache Interactions

| Cache | Sector | Interaction | Channel Time |
|---|---|---|---:|
| Key 1 | Driftwood Cove | Open shipwreck barrel | 0.5s |
| Key 2 | Gull Flats | Open low-tide rock shelf | 0.5s |
| Key 3 | Palm Hollow | Pull root rope | 1.0s |
| Key 4 | Sunken Ruins | Move stone column | 1.5s |
| Key 5 | Cliffpath Ridge | Open alcove chest | 0.5s |

**Rules:**
- Interactions require standing near the cache.
- Moving cancels the channel.
- Opening the map cancels the channel.
- Safe displacement cancels the channel.
- Once opened, the cache remains open.

### Key Notes

Key 1:
```text
The treasure is 169 paces from the Shipwreck.
```

Key 2:
```text
The treasure is 67 paces from the Gull Flats Lighthouse.
```

Key 3:
```text
The treasure is 159 paces from the Palm Hollow Idol.
```

Key 4:
```text
The treasure is 68 paces from the Sunken Arch.
```

Key 5:
```text
The fifth tide turns the lock. The reef cave opens only at low tide.
```

---

## 5.5 Coins and Score

Coins are optional score. They do not affect completion.

**Coin sources:**

| Source | Amount |
|---|---:|
| 5 key caches | 50 coins |
| 5 key sectors, 8 coins each | 40 coins |
| Final vault | 70 coins |
| **Total possible** | **160 coins** |

**Rules:**
- Coins are picked up by walking over them.
- Coins in low-tide-only spots are submerged at high tide.
- Coins do not regenerate.
- Coins do not affect keys or vault access.

**End rank:**

| Coins | Rank |
|---:|---|
| 0–99 | Beachcomber |
| 100–139 | Salvager |
| 140–159 | Master Salvager |
| 160 | Tide Baron |

**Why coins exist:**  
They fill the island with small rewards and encourage optional exploration without adding progression risk.

---

## 5.6 Final Vault

**Vault location:**
- Sector: Vault Point
- Fixed vault coordinate: **(208, 192)**
- Tile elevation: **0**
- Located in a sea cave behind reef rocks.

**Vault requirements:**
- 5/5 keys
- Low tide: water level `< 0.7`

**Vault prompt logic:**

| Condition | Prompt |
|---|---|
| `< 5` keys | “Locked. Requires 5/5 Tide Keys.” |
| `5` keys, not low tide | “Sealed by the tide. Wait for low tide.” |
| `5` keys, low tide | “Open vault” |

**Vault channel time:**
- 1 second

**Rules:**
- If tide rises before channel completes, cancel.
- If player moves, cancel.
- If map is opened, cancel.
- On success:
  - Vault opens.
  - Player collects 70 coins and the Golden Compass.
  - Game enters `GAME_COMPLETE`.

**Why low tide is required:**  
The final moment should combine all major systems: keys, clues, map, and tide.

---

## 6. Algorithms

## 6.1 World Variation Algorithm

The base island is fixed. The seed only varies minor content.

```text
seed = random seed

for each cache 2 through 5:
    cache.position = defaultCachePosition + random offset within 3 tiles
    if cache.position is not passable at low tide:
        use defaultCachePosition

for each key sector:
    place 8 coins on random low-tide passable tiles
    avoid placing coins within 2 tiles of other coins

if any validation fails:
    use default fixed positions
```

**Why fixed base layout:**  
An open-world browser game with puzzle progression must not generate dead ends. The authored island guarantees every sector and key is reachable.

---

## 6.2 Connectivity Validation

Before the game starts, validate the world.

### Low Tide Graph

- Water level = 0
- All elevation 0 and 1 tiles are passable.
- Check that:
  - Start is reachable.
  - All key caches are reachable.
  - Vault is reachable.

### High Tide Graph

- Water level = 2
- Elevation 0 is deep water and blocked.
- Elevation 1 is shallow and passable.
- Elevation 2+ is dry and passable.
- Check that:
  - Start is reachable.
  - At least one route exists to each sector.
  - Player is not stranded in any sector.

**If validation fails:**
- Use default fixed layout.

---

## 6.3 Tide Passability Algorithm

```text
waterLevel = 1 - cos(2π * t / 120)

for each tile:
    depth = max(0, waterLevel - tile.elevation)
    tile.passable = depth <= 1.0
```

For movement between tiles:

```text
canMove = currentTile.passable
        and targetTile.passable
        and abs(targetTile.elevation - currentTile.elevation) <= 1
```

---

## 6.4 Safe Displacement Algorithm

```text
if !currentTile.passable:
    search = BFS from current tile, radius 16
    if search finds passable tile:
        move player there
        cancel active channel
    else:
        if lastHighSafeTile exists:
            move player to lastHighSafeTile
        else:
            move player to startTile
        cancel active channel
```

---

## 6.5 Fog Reveal Algorithm

When player enters a new tile:

```text
for each tile within radius 10:
    if lineOfSight(playerTile, targetTile):
        reveal targetTile
```

Line of sight:

```text
sample every 0.5 tiles along the line
if any sampled tile elevation > playerTile.elevation + 1:
    blocked
```

---

## 6.6 Landmark Discovery Algorithm

Every frame:

```text
for each undiscovered landmark:
    if distance(player, landmark) <= 24:
        if lineOfSight(player, landmark):
            discover landmark
            show landmark on map
            if landmark is a sector landmark:
                mark sector discovered
```

---

## 6.7 Clue Ring Validation Algorithm

The vault location `V` is fixed by default.

For each of Keys 1–4:

```text
d = round(distance(landmark, V))
store clue = { landmark, d }
```

Validation:

```text
overlapTiles = []

for each tile in island:
    insideAll = true
    for each clue:
        if abs(distance(tile, clue.landmark) - clue.d) > 6:
            insideAll = false
            break
    if insideAll:
        overlapTiles.add(tile)

valid = V is in overlapTiles
valid = overlapTiles.size < 400
```

**Why validation matters:**  
The clue rings must become small enough to identify the vault, but not so thin that they are hard to read.

---

## 6.8 End Screen Algorithm

```text
if vault opened:
    stats = {
        time: elapsed time,
        keys: 5,
        coins: total coins collected
    }
    show end screen
    disable input
```

---

## 7. HUD and Player Information

## 7.1 Persistent HUD

### Top Left

1. **Tide Dial**
   - Shows current water level from 0 to 2.
   - Shows text state:
     - LOW
     - RISING
     - HIGH
   - Shows seconds until next threshold.
   - Must use shape and text, not only color.

2. **Stamina Bar**
   - Horizontal bar.
   - Length represents 0–100.
   - Full when 100.
   - Empty when 0.

3. **Key Counter**
   - 5 key icons.
   - Collected keys are filled.
   - Missing keys are hollow.

### Bottom Right

1. **Coin Counter**
   - Shows `X / 160`.

### Top Right

1. **Map Button**
   - Opens map overlay.
   - Shows a small map preview.
   - Can be held with M or right mouse.

2. **Objective Text**
   - Short one-line objective.
   - Updates after key and vault events.

### Center Bottom

1. **Context Prompt**
   - Shows interactable action.
   - Examples:
     - “Open barrel”
     - “Pull rope”
     - “Move column”
     - “Open vault”
     - “Sealed by the tide”

---

## 7.2 Map Overlay

When opened, the map covers most of the screen.

**Map canvas size:**
- Maximum **512 x 512 pixels**
- Scales to screen.
- 1 tile = 2 pixels at full size.

**Map layers:**

| Layer | Content |
|---|---|
| Base | Revealed tiles |
| Unrevealed | Dark overlay |
| Water | Current tide depth |
| High-tide preview | Optional faint overlay showing areas that become deep water |
| Landmarks | Triangle icons |
| Player | White arrow/dot |
| Hunt areas | Orange circles around uncollected caches |
| Clue rings | Translucent colored rings |
| Vault marker | Red X after 4 geometric clues |
| Open vault | Gold X after 5 keys |

**Map legend:**
- Player
- Landmark
- Hunt area
- Clue ring
- Vault marker
- Low tide only

**Why the map is central:**  
The map is the main puzzle tool. It must show enough information to reduce frustration but not solve the travel automatically.

---

## 8. Content by Sector

## 8.1 Driftwood Cove

**Role:** Start, tutorial, Key 1.

**Approx bounds:**
- x: 16–70
- y: 190–240

**Elevation:**
- Elevation 0 beach
- Elevation 1 dunes

**Start tile:**
- **(32, 220)**

**Landmark:**
- Shipwreck
- Position: **(40, 210)**

**Key 1 cache:**
- Shipwreck barrel
- Position: **(45, 208)**
- Interaction: open barrel
- Channel: 0.5s
- Always available.

**Clue:**
- Distance ring from Shipwreck to vault
- `D = 169`

**Optional content:**
- 8 coins near driftwood and dunes.

**Hazard:**
- None.

**Design purpose:**  
Teach movement, stamina, map, interaction, and the first clue ring immediately.

---

## 8.2 Gull Flats

**Role:** Low-tide teaching sector, Key 2.

**Approx bounds:**
- x: 90–170
- y: 210–250

**Elevation:**
- Elevation 0 mudflats
- Elevation 1 flats

**Landmark:**
- Gull Flats Lighthouse
- Position: **(150, 225)**
- Base elevation: 2

**Key 2 cache:**
- Low-tide rock shelf
- Position: **(135, 222)**
- Tile elevation: 0
- Interaction: open cache
- Channel: 0.5s
- Only reachable at low tide.

**Clue:**
- Distance ring from Gull Flats Lighthouse to vault
- `D = 67`

**Optional content:**
- 8 coins
- 3 coins only on low-tide shelf

**Hazard:**
- High tide makes elevation 0 shelves deep water.

**Design purpose:**  
Teach the tide system and waiting for low tide.

---

## 8.3 Palm Hollow

**Role:** Jungle interior, interaction puzzle, Key 3.

**Approx bounds:**
- x: 40–110
- y: 70–150

**Elevation:**
- Elevation 1 lowland
- Elevation 2 small hills
- Dense palm coverage

**Landmark:**
- Palm Hollow Idol
- Position: **(75, 105)**
- Elevation: 2

**Key 3 cache:**
- Behind root gate
- Position: **(80, 112)**
- Interaction: pull rope
- Channel: 1.0s
- Rope opens a 2-tile gap.
- Once opened, gate remains open.

**Clue:**
- Distance ring from Palm Hollow Idol to vault
- `D = 159`

**Optional content:**
- 8 coins in palms and on ledges.

**Hazard:**
- None beyond missed interaction.

**Design purpose:**  
Add a simple physical interaction and encourage interior exploration.

---

## 8.4 Sunken Ruins

**Role:** Coastal ruins, movement puzzle, Key 4.

**Approx bounds:**
- x: 170–220
- y: 100–160

**Elevation:**
- Elevation 1 coastal ruins
- Elevation 2 ruin floor
- Elevation 3 small tower base

**Landmark:**
- Sunken Arch
- Position: **(195, 125)**
- Elevation: 2

**Key 4 cache:**
- Behind movable stone column
- Position: **(192, 132)**
- Interaction: move column
- Channel: 1.5s
- Column moves once and path remains open.

**Clue:**
- Distance ring from Sunken Arch to vault
- `D = 68`

**Optional content:**
- 8 coins in ruined mosaics.

**Hazard:**
- Some corridors are flooded at high tide.
- High tide slows movement but does not block main route.

**Design purpose:**  
Add route choice and a slightly longer interaction without making tide mandatory.

---

## 8.5 Cliffpath Ridge

**Role:** High ground, final key, Key 5.

**Approx bounds:**
- x: 110–180
- y: 30–100

**Elevation:**
- Elevation 2 foothills
- Elevation 3–4 ridge paths
- Elevation 5 cliff tops

**Landmark:**
- Cliffpath Eagle Rock
- Position: **(145, 55)**
- Elevation: 4

**Key 5 cache:**
- Eagle Rock alcove
- Position: **(148, 58)**
- Interaction: open chest
- Channel: 0.5s
- No extra lock.

**Clue:**
- No distance clue.
- Note says the fifth key turns the vault lock and low tide is required.

**Optional content:**
- 8 coins on cliff ledges.

**Hazard:**
- Stamina pressure if running along cliff path.
- No fall damage.

**Design purpose:**  
Make the final key feel earned through travel and stamina management, but not punish the player.

---

## 8.6 Vault Point

**Role:** Final vault, completion.

**Approx bounds:**
- x: 185–230
- y: 170–215

**Elevation:**
- Elevation 0 cave floor
- Elevation 1 rocks
- Elevation 2 reef outcrop

**Landmark:**
- Vault Point Reef
- Position: **(205, 185)**
- Elevation: 2

**Vault:**
- Position: **(208, 192)**
- Elevation: 0
- Sea cave behind reef.

**Requirements:**
- 5/5 keys
- Low tide

**Final reward:**
- 70 coins
- Golden Compass

**Optional content:**
- 8 coins around the reef
- Some coins only at low tide

**Hazard:**
- Vault is sealed by tide until low water.

**Design purpose:**  
Combine all systems in the final moment.

---

## 9. Numbers and Feel

## 9.1 Core Constant Table

| Constant | Value |
|---|---:|
| World size | 256 x 256 tiles |
| Tile size | 1 meter |
| Ocean border | 8 tiles |
| Max elevation | 5 |
| Tide cycle | 120 seconds |
| Water level range | 0 to 2 |
| Low tide threshold | `< 0.7` |
| High tide threshold | `> 1.3` |
| Passable water depth | `<= 1.0` |
| Walk speed | 3.0 tiles/sec |
| Run speed | 5.0 tiles/sec |
| Swim speed | 2.0 tiles/sec |
| Low stamina swim speed | 1.5 tiles/sec |
| Max stamina | 100 |
| Run drain | 12 stamina/sec |
| Swim drain | 10 stamina/sec |
| Stamina regen | 20 stamina/sec |
| Map reveal radius | 10 tiles |
| Landmark visible distance | 24 tiles |
| Cache visible distance | 8 tiles |
| Cache hunt area radius | 24 tiles |
| Clue ring width | distance ± 6 tiles |
| Safe displacement radius | 16 tiles |
| Key cache coins | 10 each |
| Scattered coins | 40 total |
| Vault coins | 70 |
| Total coins | 160 |

---

## 9.2 Pacing Expectations

| Moment | Expected Time |
|---|---:|
| First key | Under 60 seconds |
| Gull Flats low-tide lesson | 2–4 minutes |
| All five keys | 10–20 minutes |
| Full game | 15–25 minutes |

**Feel target:**
- The player should rarely be lost for more than 60 seconds.
- The player should understand the tide within the first 3 minutes.
- The map should feel like a tool, not a tutorial.
- The final vault should feel like a timed ritual, not a boss fight.

---

## 10. Edge Cases and Recovery

| Case | Resolution |
|---|---|
| Player reaches a sealed cache before Key 1 | Prompt: “Sealed. Find the first Tide Key.” |
| Player has 4 keys but not the fifth | Vault marker may appear if 4 geometric clues exist, but vault remains locked. |
| Player has 5 keys but no geometric clues? | Not possible if only Key 5 is non-geometric and Keys 1–4 are the only geometric keys. |
| Player reaches vault early | Cave exists, but vault prompt says locked or sealed by tide. |
| Player is in shallow water when tide rises to deep | Safe displacement to nearest passable tile. |
| Safe displacement cannot find local tile | Teleport to `lastHighSafeTile`, or start if none. |
| Player has 0 stamina | Cannot run; can walk or swim slowly. |
| Player in water with 0 stamina | Swim speed drops to 1.5 tiles/sec. |
| Player tries to enter deep water | Movement blocked. |
| Player tries to climb a 2+ elevation cliff | Movement blocked. |
| Player opens map during channel | Channel cancels. |
| Player moves during channel | Channel cancels. |
| Tide changes during vault channel | Channel cancels if tide is no longer low. |
| Player collects all coins | End rank is Tide Baron. |
| Player ignores coins | Completion is unaffected. |
| Generation/validation fails | Use default fixed layout. |

---

## 11. Cuts and Non-Goals

The following are intentionally cut.

| Cut | Reason |
|---|---|
| Combat | Would add enemy AI, health, weapons, and damage, diluting the treasure-hunt fantasy. |
| Health / death | Would create frustration without adding meaningful decision-making. |
| Inventory | Keys and coins are automatic; inventory would add UI burden for no gameplay value. |
| NPCs | Would require dialogue, pacing, and content scope beyond the core loop. |
| Weather | Tide is already the dynamic environmental pressure. |
| Day/night | Would add visual complexity without changing the core puzzle. |
| Vehicles / boats | Would require separate physics and water navigation systems. |
| Crafting | No resource loop supports it. |
| Shops / meta progression | Single 15–25 minute session does not need it. |
| Multiplayer | Would require synchronization and balance systems outside this gameplay scope. |
| Permadeath | Would conflict with exploration recovery. |
| Save system | Single session is the intended play. |
| Infinite world | A bounded island is more legible and guaranteed to be completable. |

---

## 12. Functional Requirements for Other Design Areas

These are not art direction, but the gameplay depends on these being readable.

### Visual Designer

- Cache props must be visually distinct from coins, terrain, and landmarks.
- Tide depth must be readable:
  - Dry
  - Shallow
  - Deep
- Elevation difference of 1 must be readable.
- Cliff blocks of 2+ elevation must be clearly non-walkable.
- Clue rings must be visible over terrain.
- The vault marker must be obvious once revealed.
- Map icons must not rely on color alone:
  - Use shape and label.

### Audio Designer

The following events need distinct audio cues:
- Key collected
- Coin collected
- Cache sealed
- Tide warning
- Low tide reached
- High tide reached
- Rope pulled
- Column moved
- Vault locked
- Vault opening
- Game complete

The gameplay does not depend on hearing these, but they strongly support readability.

---

## 13. Integration State and Events

The integrator should treat these as the main gameplay state.

### Main State Variables

```text
player.position
player.stamina
tide.time
tide.waterLevel
tide.state
keys.totalCollected
keys.geometricCollected
coins.collected
vault.markerRevealed
vault.unlocked
vault.completed
tiles.revealed
landmarks.discovered
caches.collected
```

### Gameplay Events

```text
game_start
landmark_discovered(landmarkId)
sector_discovered(sectorId)
cache_sealed_prompt(cacheId)
cache_opened(cacheId)
key_collected(keyId)
geometric_clue_added(clueIndex)
coin_collected(amount)
hunt_area_revealed(sectorId)
vault_marker_revealed
vault_unlocked
tide_warning(threshold)
tide_state_changed(newState)
safe_displacement_occurred
vault_opened
game_complete(stats)
```

---

## 14. Final Design Summary

*Island of the Hidden Hoard* is a short, complete open-world exploration game built around one fantasy: reading the island to find treasure.

The player explores a bounded 2.5D island, finds five Tide Keys, uses distance clue rings to locate the vault, and opens it during low tide. The game has no combat, no health, and no fail state. The only danger is the tide, and the tide is always readable and avoidable.

The design is complete end to end:
- Start in Driftwood Cove.
- Get first key and first clue immediately.
- Learn tide in Gull Flats.
- Learn interactions in Palm Hollow and Sunken Ruins.
- Earn final key on Cliffpath Ridge.
- Solve clue rings.
- Return to Vault Point.
- Open vault at low tide.
- Collect treasure and end.