3D, fixed angled overhead camera with 360° orbit, 54° tilt, and zoom from 18 to 55 units.

# 1. THE LOOK IN ONE PARAGRAPH

The game is a low-poly, sun-washed pastoral world with soft edges, readable colours, and a cozy collector mood. The palette is led by moss green `#7FC850`, berry red `#E84A4F`, ore teal `#3AA6A6`, lake cyan `#7FE3F0`, warm timber `#B98A5B`, and museum cream `#F3EAD8`. The feeling should be calm, slightly misty, and inviting, with golden-hour warmth rather than realism. The one screenshot that should sell the game is a cottage and small museum in the foreground, a lit door spilling warm light, a red berry bush just outside, a fishing bobber dipping in a cyan lake to the left, and three clearly coloured regions visible around the edges: berry-green bushes, gray-brown mine rock, and cream home furniture.

# 2. THE SPACE

All world sizes are in game units (`u`). The world is a `300 x 300 u` square from `-150` to `+150` on both horizontal axes. It is generated once per session from the fixed regional plan below.

| Region | Bounds | Size | Main contents |
|---|---:|---:|---|
| Berry Grove | `x -150 to -30`, `z -150 to -30` | `120 x 120 u` | 36 berry bushes, 18 berry trees, 12 rocks |
| Mine | `x 30 to 150`, `z -150 to -30` | `120 x 120 u` | 24 ore nodes, 16 rocks, 4 stumps |
| Crossroads | `x -30 to 30`, `z -30 to 30` | `60 x 60 u` | 4 path branches, 4 rocks, 2 trees |
| Lake | `x -150 to 30`, `z 30 to 150` | `180 x 120 u` | 3 docks, 12 reed clusters, 8 rocks |
| Home Meadow | `x 30 to 150`, `z 30 to 150` | `120 x 120 u` | 1 cottage, 1 museum, 1 shop, 14 fence segments, 6 trees, 10 rocks |

The player starts at the cottage front door at `x 80, z 72`, facing west toward the Crossroads. The visual goal is the museum porch at `x 110, z 84`; the museum is a small cream building with teal roof and columns, placed in the Home Meadow near the cottage.

Paths are `4 u` wide dirt ribbons connecting the cottage to the Crossroads and then to the Berry Grove, Mine, and Lake. The eye tells regions apart by dominant colour and prop density: the Berry Grove is dense green with red berry points; the Mine is gray-brown with sparkling crystals; the Lake is cyan water with docks and reeds; the Home Meadow is warm timber, cream walls, and placed furniture; the Crossroads is neutral path with sparse grass.

Good generated roll, verifiable:

- Exact region counts are present: 36 berry bushes, 18 berry trees, 12 grove rocks; 24 ore nodes, 16 mine rocks, 4 stumps; 3 docks, 12 reed clusters, 8 lake rocks; 1 cottage, 1 museum, 1 shop, 14 fence segments, 6 meadow trees, 10 meadow rocks.
- Paths are continuous and `4 u` wide from cottage to each region.
- No prop overlaps the player start point by more than `2 u`.
- The museum and shop are visible from the cottage start point.
- At least 14 berry bushes are within `20 u` of the Berry Grove path entry.
- At least 6 ore nodes are within `20 u` of the Mine path entry.
- All 3 docks are placed at the lake shore and perpendicular to the shore line.
- Lake shore has a visible `3 u` sand band.

Bad generated roll, verifiable:

- Any region is missing any required prop count.
- A path is broken, narrower than `4 u`, or blocked by a prop wider than `3 u`.
- The player start point is inside a prop.
- The museum is not visible from the cottage start point.
- A dock is placed in the Home Meadow or Crossroads.
- An ore node is placed in the Lake.
- A berry bush is placed in the Mine with no berry-grove ground colour.
- Two adjacent regions have the same dominant hue and the same prop type.

# 3. RECIPES

World sizes are in game units. UI sizes are in screen pixels (`px`), a separate given UI unit.

| Thing / state | Shape | Size | Colour(s) | Count | Motion / effect |
|---|---|---:|---|---:|---|
| Grass base | Plane | `300 x 300 x 0 u` | `#7FC850` | 1 | Subtle vertex variation, static |
| Berry-grove ground | Plane | `120 x 120 x 0 u` | `#6DBA4A`, leaf patches `#3E7C3F` | 1 | 24 leaf patches, static |
| Mine ground | Plane | `120 x 120 x 0 u` | `#8A8F98`, cracks `#6B4A33` | 1 | 12 crack decals, static |
| Lake water | Plane | `180 x 120 x -0.1 u` | `#38B7C9`, ripple `#7FE3F0` | 1 | Slow ripple bands, shore depth `#7FE3F0` |
| Shore sand | Ring plane | `3 u` wide | `#E6D3A3`, wet edge `#C9B27D` | 1 | Static |
| Path segment | Ribbon | `4 u` wide, `0.05 u` high | `#C9A15A`, edge `#A8854B` | 7 | Static |
| Cottage walls | Box + pyramid roof | `12 x 12 x 4 u`, roof `2 u` high | `#B98A5B`, roof `#C85B3C` | 1 | Static |
| Cottage door, closed | Box | `2 x 3 x 0.2 u` | `#5C3A21` | 1 | Static |
| Cottage door, open | Box rotated `-80°` | `2 x 3 x 0.2 u` | `#5C3A21`, light `#FFE9A8` | 1 | Light spill `2 x 3 u`, alpha `0.35` |
| Cottage windows, day | 3 rectangles | `1.2 x 1.8 x 0.1 u` each | `#BDE8FF`, frame `#5C3A21` | 3 | Static |
| Cottage windows, night | 3 rectangles | `1.2 x 1.8 x 0.1 u` each | `#FFE9A8`, frame `#5C3A21` | 3 | Glow radius `4 u` |
| Museum walls | Box + 4 columns + roof | `16 x 10 x 5 u`, roof `1.5 u`, columns `0.6 u` diameter | `#F3EAD8`, columns `#FFF8EF`, roof `#3AA6A6` | 1 | Static |
| Museum windows, day | 3 rectangles | `1.2 x 1.8 x 0.1 u` each | `#BDE8FF`, frame `#3AA6A6` | 3 | Static |
| Museum windows, night | 3 rectangles | `1.2 x 1.8 x 0.1 u` each | `#FFE9A8`, frame `#3AA6A6` | 3 | Glow radius `5 u` |
| Shop stall | Box + striped awning | `8 x 8 x 3 u`, awning panels `2 x 2 u` | `#8C5E3C`, `#F4D16C`, `#E1554F` | 1 | Awning sways `1°` |
| Shop counter | Box | `4 x 1 x 1 u` | `#8C5E3C`, top `#A07A4F` | 1 | 3 jars `#D9784A` on counter |
| Fence segment | 2 posts + 2 rails | `2 x 0.1 x 1.2 u` | `#B98A5B` | 14 | Static |
| Berry bush, full | 5 overlapping spheres + 12 berry spheres | `1.6 u` diameter, `1.8 u` high | `#3E7C3F`, berries `#E84A4F` | 18 | Berry sway `2°` |
| Berry bush, sparse | Same form, 4 berries | `1.6 u` diameter, `1.8 u` high | `#3E7C3F`, berries `#E84A4F` | 9 | Berry sway `2°` |
| Berry bush, empty | Same form, 0 berries | `1.6 u` diameter, `1.8 u` high | `#2F5F33` | 9 | Sway `1°` |
| Berry tree | Cylinder trunk + sphere canopy | `0.8 u` trunk, `3.5 u` canopy | `#6B4A33`, `#4FA35A` | 18 | Canopy sway `2°` |
| Ore node, copper, full | Icosahedron + 8 crystals | `2.2 u` rock, `0.18 u` crystals | `#9AA0A6`, crystals `#D9784A` | 8 | Crystal glint `0.25 s` |
| Ore node, tin, full | Icosahedron + 8 crystals | `2.2 u` rock, `0.18 u` crystals | `#9AA0A6`, crystals `#DDE3E8` | 8 | Crystal glint `0.25 s` |
| Ore node, gold, full | Icosahedron + 8 crystals | `2.2 u` rock, `0.18 u` crystals | `#9AA0A6`, crystals `#F4D16C` | 8 | Crystal glint `0.25 s` |
| Ore node, mined | Icosahedron with hollow | `2.2 u` rock | `#9AA0A6`, hollow `#4A4E53` | 0 at load; maximum 24 | Dust puff on conversion |
| Reed cluster | 7 cones | `0.8 u` high | `#4F8C45` | 12 | Sway `3°` |
| Rock, small | Icosahedron | `1.0 u` | `#7A7F86` | 26 | Static |
| Rock, large | Icosahedron | `1.8 u` | `#7A7F86` | 14 | Static |
| Tree, meadow | Cylinder trunk + sphere canopy | `1 u` trunk, `4 u` canopy | `#6B4A33`, `#4FA35A` | 6 | Canopy sway `2°` |
| Stump | Cylinder | `0.8 u` diameter, `0.5 u` high | `#A07A4F` | 4 | Static |
| Dock | Plank box + 4 posts | `6 x 1.2 x 0.2 u` | `#8C5E3C`, posts `#6B4A33` | 3 | Static |
| Fishing bobber, idle | Sphere with top band | `0.2 u` | `#FF6B4A`, top `#FFF8EF` | 3 | Bob `0.05 u` |
| Fishing bobber, bite | Sphere | `0.2 u` | `#FF6B4A`, top `#FFF8EF` | 0 at load; maximum 1 | Dip `0.15 u` |
| Fish, on hook | Elongated diamond | `0.5 x 0.15 x 0.15 u` | `#8AD6E8`, belly `#FFF8EF` | 0 at load; maximum 1 | Wiggle `4°` |
| Chair | Box seat + 4 legs | `0.6 x 0.6 x 0.8 u` | `#A05A2C`, legs `#7A431F` | 0 at load; maximum 4 | Static |
| Table | Box top + 4 legs | `1.2 x 0.7 x 0.8 u` | `#A07A4F`, legs `#8C5E3C` | 0 at load; maximum 2 | Static |
| Rug | Flat box | `2 x 1.5 x 0.02 u` | `#C85B3C`, border `#F4D16C` | 0 at load; maximum 2 | Static |
| Shelf | Box | `1.2 x 0.4 x 1.8 u` | `#8C5E3C` | 0 at load; maximum 2 | Static |
| Plant pot | Cylinder pot + cone plant | `0.5 u` diameter, `0.7 u` high | `#D9784A`, plant `#55A35A` | 0 at load; maximum 4 | Static |
| Display case | Box frame + glass | `1.2 x 1.2 x 1.5 u` | frame `#3AA6A6`, glass `#FFFFFF` alpha `0.35` | 0 at load; maximum 3 | Static |
| Painting | Flat box | `0.8 x 0.5 x 0.05 u` | frame `#D9B25A`, canvas `#7FC850` | 0 at load; maximum 3 | Static |
| Candle lamp | Base + flame sphere | `0.3 u` base, `0.15 u` flame | `#7A431F`, flame `#FFD26B` | 0 at load; maximum 3 | Flame brightness varies `±10%` |
| Berry pickup | Sphere | `0.12 u` | `#E84A4F` | 0 at load; maximum 1 | Pop scale `1.25` for `0.15 s` |
| Ore pickup, copper | Crystal shard | `0.18 u` | `#D9784A` | 0 at load; maximum 1 | Rotate `90°` for `0.2 s` |
| Ore pickup, tin | Crystal shard | `0.18 u` | `#DDE3E8` | 0 at load; maximum 1 | Rotate `90°` for `0.2 s` |
| Ore pickup, gold | Crystal shard | `0.18 u` | `#F4D16C` | 0 at load; maximum 1 | Rotate `90°` for `0.2 s` |
| Fish pickup | Elongated diamond | `0.5 u` | `#8AD6E8`, belly `#FFF8EF` | 0 at load; maximum 1 | Wiggle `6°` |
| Coin pickup | Cylinder | `0.18 x 0.04 u` | `#F4D16C`, edge `#C9A15A` | 0 at load; maximum 5 | Arc `0.4 u` for `0.2 s` |
| Gather sparkle | 8 particles | `0.08 u` each | `#FFE9A8` | 0 at load; maximum 1 set per harvest | Expand `0.3 u` for `0.18 s` |
| Ore chip | 6 shards | `0.12 u` each | `#9AA0A6` | 0 at load; maximum 1 set per mine | Fall `0.4 u` for `0.20 s` |
| Fish splash | 8 droplets | `0.06 u` each | `#7FE3F0` | 0 at load; maximum 1 set per catch | Expand `0.5 u` for `0.25 s` |
| Door light spill | Triangle | `2 x 3 u` | `#FFE9A8` alpha `0.35` | 0 at load; maximum 1 | Fade for `0.25 s` |
| Selection ring | Circle | `1.2 u` | `#F4D16C` alpha `0.8` | 0 at load; maximum 1 | Static |
| Placement ghost, valid | Selected furniture, transparent | Object size | `#FFFFFF` alpha `0.45`, outline `#7FE37F` | 0 at load; maximum 1 | Pulse 2 times over `0.2 s` |
| Placement ghost, invalid | Selected furniture, transparent | Object size | `#FFFFFF` alpha `0.45`, outline `#E84A4F` | 0 at load; maximum 1 | Shake `0.05 u` for `0.15 s` |
| Inventory bar | Rounded rectangle | `520 x 84 px` | `#1F2A22` alpha `0.82`, border `#F4D16C` | 1 | Static |
| Inventory slot, empty | Square | `64 x 64 px` | `#334238`, border `#5A6B5D` | 12 | Static |
| Inventory slot, filled | Square + icon | `64 x 64 px`, icon `48 x 48 px` | `#3E5244`, border `#F4D16C` | 0 at load; maximum 12 | Icon pop for `0.15 s` |
| Inventory slot, selected | Square | `64 x 64 px` | `#3E5244`, border `#FFE9A8` `4 px` wide | 0 at load; maximum 1 | Glow for `0.2 s` |
| Notification toast | Rounded rectangle + icon | `220 x 48 px`, icon `32 x 32 px` | `#1F2A22` alpha `0.88`, text `#FFF8EF`, icon `#F4D16C` | 0 at load; maximum 1 | Slide in for `0.18 s` |
| Shop panel | Rounded rectangle | `420 x 520 px` | `#F4E9C9`, header `#E1554F`, border `#B98A5B` | 0 at load; maximum 1 | Slide in for `0.18 s` |
| Shop item row | Row + icon | `380 x 56 px`, icon `48 x 48 px` | `#FFF8EF`, icon varies by item type | 8 | Static |
| Shop button, normal | Rounded rectangle | `120 x 40 px` | `#7FC850`, label `#1F2A22` | 3 | Static |
| Shop button, hover | Rounded rectangle | `120 x 40 px` | `#8FD45B`, label `#1F2A22` | 0 at load; maximum 1 | Scale `1.03` for `0.1 s` |
| Shop button, selected | Rounded rectangle | `120 x 40 px` | `#F4D16C`, label `#1F2A22`, border `#E1554F` | 0 at load; maximum 1 | Pulse for `0.2 s` |
| Health bar | Rounded rectangle + fill | `180 x 18 px` | background `#334238`, fill `#E84A4F` | 1 | Fill width follows visual health state |
| Health bar, low | Rounded rectangle + fill | `180 x 18 px` | background `#334238`, fill `#FF6B4A` | 0 at load; maximum 1 | Pulse for `0.15 s` |

# 4. LIGHTING AND ATMOSPHERE

The default look is bright day with soft shadows. Night is darker but never fully black; the player should always see nearby props and path edges.

- Ambient light: hemisphere light with sky `#BFE8FF` and ground `#7FC850`. Day intensity is `0.65`; night intensity is `0.35`; rain intensity is `0.50`.
- Sun/moon directional light: day colour `#FFE3A1`, intensity `0.95`, angle `50°` above horizon; dusk colour `FF9E5A`, intensity `0.60`, angle `15°`; night colour `#8FB8FF`, intensity `0.20`, angle `30°`. Directional light position follows any in-game time signal without adding a visual timer.
- Window lights: cottage and museum windows emit point light `#FFE9A8`, radius `5 u`, intensity `0.6` at night only.
- Lamp lights: candle lamps emit point light `#FFD26B`, radius `6 u`, intensity `0.8`. Flame brightness varies `±10%`.
- Door light: open cottage door emits point light `#FFE9A8`, radius `5 u`, intensity `0.6`.
- Darkness: at night, ambient drops to `0.35`; unlit ground becomes `#2E4A33`; unlit water becomes `#28788A`; path edges remain readable at `#9C7A42`.
- Fog: distance fog starts at `60 u` and ends at `140 u`. Day fog colour is `#CFE9F2`; night fog colour is `#203044`; rain fog colour is `#9FB6C9`.
- Time-of-day changes: day, dusk, night, and rain states use the lighting values above. Dusk adds a warm ground tint `#FFC78A` at alpha `0.12`.
- Weather: rain is a visual state with `800` streaks, each `0.02 u` long, colour `#B8D9FF`, alpha `0.55`. Rain adds puddle decals `#28788A`, alpha `0.12`, and wet ground darkening alpha `0.10`.
- Post effect, vignette: day strength `0.18`, black `#000000`; night strength `0.28`; low-health state strength `0.35`, red `#E84A4F`.
- Post effect, grain: day strength `0.04`; rain strength `0.07`.
- Post effect, flash: damage flash red `#E84A4F`, strength `0.12`, duration `0.15 s`; pickup flash gold `#FFE9A8`, strength `0.08`, duration `0.10 s`.
- Post effect, shake: ore mining shake strength `0.03 u`, duration `0.12 s`; invalid placement shake strength `0.05 u`, duration `0.15 s`.

# 5. CHARACTERS AND ANIMATION

Player:

- Silhouette and read at a glance: a compact `0.9 u` tall, `0.5 u` wide figure with a rounded hooded cloak, a brown backpack, and a small pale face. The player reads as a soft green cone with a brown pack and one pale face dot.
- Main colours: cloak `#55A35A`, pack `#B98A5B`, face `#FFF8EF`, boots `#6B4A33`.
- Facings: 8 directions.
- idle: 12-frame loop, body bob `0.03 u`, pack settle `1°`.
- walk: 8-frame loop, stride `0.18 u`, body bob `0.04 u`, arms swing `20°`.
- attack: none; gather instead: 6-frame reach, tool extends `0.6 u`, lean `5°`, sparkle effect.
- hurt: 4-frame flinch, body recoil `0.06 u`, red tint `#E84A4F` alpha `0.30` for `0.12 s`.
- death: 10-frame collapse, body drop `0.3 u`, fade for `0.3 s`.

Shopkeeper:

- Silhouette and read at a glance: a stout `1.0 u` tall, `0.6 u` wide figure with a wide apron, a small hat, and a counter stance. The shopkeeper reads as a yellow triangle body with a red hat and a pale face.
- Main colours: apron `#F4D16C`, hat `#E1554F`, face `#FFF8EF`, sleeves `#8C5E3C`.
- Facings: 4 directions.
- idle: 10-frame loop, hand wave `5°`, body bob `0.02 u`.
- walk: 6-frame loop, stride `0.16 u`, body bob `0.03 u`.
- attack: none; serve instead: 8-frame gesture, arm raises `0.3 u`, counter glow `#FFE9A8` alpha `0.25`.
- hurt: 3-frame surprise, hat hop `0.04 u`.
- death: 6-frame sit-down, fade for `0.25 s`.

# 6. FEEDBACK

- Berry harvest: full bush scales to `1.04` and back, 3 red particles `#E84A4F`, duration `0.18 s`.
- Berry bush empty: 5 brown particles `#A07A4F`, duration `0.15 s`.
- Ore mine: rock white flash `#FFFFFF` alpha `0.50` for `0.10 s`, 6 gray shards `#9AA0A6`, duration `0.20 s`, screen shake `0.03 u` for `0.12 s`.
- Fish catch: bobber dips `0.15 u`, 8 cyan droplets `#7FE3F0`, duration `0.25 s`.
- Pickup: item icon pops scale `1.25` to `1.0`, duration `0.15 s`.
- Damage taken: red vignette `#E84A4F` alpha `0.20`, duration `0.15 s`.
- Low health: red vignette `#E84A4F` alpha `0.35`, steady edge pulse, duration `0.15 s`.
- Door opening: door rotates from `0°` to `-80°`, light spill expands, duration `0.25 s`.
- Furniture placed: green placement pulse `#7FE37F` 2 times, duration `0.20 s`.
- Invalid placement: red placement outline `#E84A4F` shakes `0.05 u`, duration `0.15 s`.
- Sell: 5 coin pickups arc `0.4 u`, duration `0.20 s`.
- Shop open: shop panel slides in, duration `0.18 s`.
- Timer running out, visual only: the final `25%` of any provided progress bar pulses amber `#F4D16C` for `0.15 s`, then red `#E84A4F` for `0.15 s`.

# 7. SCREENSHOT CHECKLIST

| Screen / state | How to reach it | What a person must see there |
|---|---|---|
| Spawn day view | Load the game | Player at cottage door, cottage, museum, and shop visible, three regions readable, paths continuous, no prop overlap |
| Berry Grove entry | Walk west to the Grove | Dense green ground, red berry bushes, berry trees, at least 10 bushes visible, leaf patches visible |
| Berry harvest | Stand at a full bush and use gather | Bush scale pulse, 3 red particles, berry pickup pop, inventory slot filled |
| Empty berry bush | View a bush in its empty state | No red berries, darker leaves `#2F5F33`, sparse twig shapes visible |
| Mine entry | Walk east to the Mine | Gray-brown ground, 8 visible ore nodes, copper/tin/gold crystals readable, rocks and stumps present |
| Ore mine | Stand at a full ore node and use gather | White flash, 6 gray shards, small screen shake, ore pickup pop |
| Mined ore node | View a mined node | Hollow dark rock `#4A4E53`, no crystals, no glint, dust puff absent |
| Lake fishing | Walk south to a dock | 3 docks, cyan water, reed clusters, idle bobbers, shore sand visible |
| Fish catch | Use fishing action at a dock | Bobber dip, 8 cyan droplets, fish pickup wiggle, water ripple visible |
| Shop transaction | Approach the shop and open the panel | Shopkeeper, striped stall, shop panel with 8 item rows, 3 buttons, coin icon, header colour `#E1554F` |
| Shop button hover | Move pointer over a shop button | Button colour `#8FD45B`, scale `1.03`, label readable |
| Home interior | Enter the cottage | Warm lamp light, timber walls, furniture placement cursor if selecting, door light spill if door open |
| Museum interior | Enter the museum | Cream walls, teal roof visible outside, display case glass, painting, warm window light at night |
| Furniture placed | Select furniture and place it on valid floor | Solid furniture object, selection ring, no red ghost, notification toast |
| Valid placement ghost | Select furniture and hover over valid floor | Transparent furniture alpha `0.45`, green outline `#7FE37F`, green pulse |
| Invalid placement ghost | Select furniture and hover over water or outside floor | Transparent furniture alpha `0.45`, red outline `#E84A4F`, red shake |
| Door open state | Open the cottage door | Door rotated `-80°`, warm light spill triangle, path visible through doorway |
| Night state | Set time to night | Moonlight, darker fog, window/lamp glow, vignette strength `0.28`, path edges still readable |
| Low health state | Enter the low-health visual state | Red vignette, health bar fill `#FF6B4A`, edge pulse |
| Rain state | Set weather to rain | 800 rain streaks, puddle decals, wet ground darkening, grain strength `0.07`, rain fog colour `#9FB6C9` |
| Inventory filled state | Collect at least 3 item types | Inventory bar visible, filled slots with distinct berry, ore, and fish icons, selected slot glow if one is selected |