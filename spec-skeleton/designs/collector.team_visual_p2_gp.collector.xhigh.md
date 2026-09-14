# visual.md

## 0. Handoff Promise

This document defines the visual, UX, music, and sound-effect direction for the open-world collector game. The integrating agent should treat this as the source of truth for:

- Dimensionality and visual depth.
- Overall art style.
- Color system.
- Zone identity.
- Resource node states.
- Character states.
- Furniture presentation.
- HUD and UI skin.
- Build-mode feedback.
- Minimap and ledger presentation.
- Music identity and audio cues.
- Sound-effect list and character.
- Accessibility and readability rules.
- Asset naming and technical art constraints.

If a decision is important, it is stated explicitly below with a short rationale. If something is missing, do not invent a contradictory style. Use the closest rule in this document.

---

## 1. Dimensionality

### Decision

The game is **2D top-down**.

It is not isometric, not 3D, and not a side-scroller.

### Visual Depth Rule

The game may use **painted sprite height** and **soft shadows** to create a gentle sense of depth, but it must never imply:

- A vertical axis the player can move through.
- Caves.
- Ladders.
- Elevation changes.
- Walkable rooftops.
- Hidden lower or upper floors.

Example:

- A berry bush can be drawn taller than one tile.
- A roof can overhang.
- A tree can visually extend above its base tile.

But none of those visuals may suggest the player can climb, fall, or move vertically.

### Why

The gameplay document defines a tile-based top-down world. The visual style should preserve that clarity. A slight painted-depth feel makes the world cozy and handmade, but the core spatial logic must remain completely readable.

---

## 2. Overall Art Style

### Style Name

**Cozy Hand-Painted Pixel Diorama**

### Description

The world should look like a small, lovingly arranged painterly diorama viewed from above.

It should feel like:

- A miniature collector’s garden.
- A warm little village outside a small museum.
- A place where picking berries, mining ore, fishing, and curating objects are calm and satisfying.

It should not feel like:

- A harsh neon action game.
- A grim survival world.
- A cartoon with loud outlines.
- A polished AAA 3D diorama.
- A sterile vector UI game.

### Visual Qualities

The art should have:

- Soft pixel shading.
- Gentle color separation.
- Low-to-medium saturation.
- Warm earth tones as the base.
- Bright but controlled resource accents.
- Rounded shapes.
- No heavy black outlines.
- Subtle shadows.
- Small animation, not exaggerated animation.

### Outline Rule

Use **no hard black outlines**.

Use:

- Darker shaded edges.
- 1-pixel dark accents.
- Light rim highlights where needed.
- Soft drop shadows.

### Why

Heavy outlines would make the world feel harsh and gamey. A soft painterly style supports the collector/museum fantasy and keeps the world calm.

---

## 3. Global Palette

The palette should feel coherent across all zones. Use a shared base palette and then allow each zone to add one or two accent colors.

### Base Palette

| Name | Hex | Use |
|---|---:|---|
| Ink Shadow | `#2E241B` | Shadows, text, dark UI |
| Warm Dark Wood | `#5C4032` | Borders, dark wood, outlines |
| Medium Wood | `#8A5A3B` | Furniture, UI buttons |
| Light Wood | `#B98A63` | Buttons, trims, highlights |
| Parchment | `#F3E4C7` | UI panels, cards |
| Paper | `#F9F1DC` | Highlighted panels, bright cards |
| Earth Path | `#C2A374` | Village paths, dirt |
| Dry Grass | `#A3B37A` | Village edges, dry fields |
| Grass Base | `#85A66A` | Main grass |
| Grass Shadow | `#5F7A4C` | Dark grass, leaves |
| Stone Grey | `#8C867B` | Rocks, museum floor |
| Stone Light | `#B9B2A6` | Highlights, walls |
| Water Shallow | `#6FB0C4` | Shallow lake |
| Water Deep | `#3F7D96` | Deep lake |
| UI Gold | `#D9A441` | Coins, highlights, goal reward |
| Valid Feedback | `#6FBF73` | Valid placement, success |
| Invalid Feedback | `#D96A5A` | Invalid placement, errors |
| Warning Amber | `#E3B23C` | Low supply, caution |

### Zone Accent Palette

| Zone | Primary Accent | Secondary Accent |
|---|---:|---:|
| Village | `#D9A441` warm amber | `#8A5A3B` wood |
| Berry Grove | `#5E8C4A` leaf green | `#D94F5C` sweet berry |
| Ore Ridge | `#A5765B` earth stone | `#C06A3F` copper |
| Lakeside | `#4E9BB0` teal water | `#9BB8E8` moon blue |
| Home Interior | `#C99B6A` warm wood | `#F3E4C7` parchment |
| Museum Interior | `#C8B494` stone plaster | `#C7A24A` brass |

### Resource and Specimen Colors

These colors must be consistent in:

- World sprites.
- Inventory icons.
- Shop UI.
- Ledger collection cards.
- Display case contents.
- Toast icons.
- Minimap if resources are ever shown.

| Resource | Hex | Visual Character |
|---|---:|---|
| Sweet Berry | `#D94F5C` | Warm red-pink |
| Moon Berry | `#8E7BD1` | Lavender-blue |
| Ember Berry | `#F07A3A` | Warm orange, slight glow |
| Copper Ore | `#C06A3F` | Earthy orange-brown |
| Silver Ore | `#CFCFCF` | Cool silver |
| Crystal Shard | `#86E8FF` | Bright cyan, soft glow |
| Minnow | `#D8C97A` | Pale yellow-silver |
| Trout | `#D97A4F` | Orange-red |
| Moonfish | `#9BB8E8` | Pale blue-silver |

### Tier Color Logic

Use color to communicate tier without using numbers alone.

| Tier | Visual Rule |
|---|---|
| Tier 1 | Common, natural, no glow |
| Tier 2 | Slightly cooler or brighter than Tier 1 |
| Tier 3 | Rare, soft emissive pulse |

Tier 3 resources should pulse slowly, about `1.5s` full cycle. Do not use fast flashing. This keeps the game calm while making rare items readable.

### Why

A shared base palette keeps the world coherent. Zone accents make travel feel meaningful. Resource colors are repeated everywhere so the player immediately recognizes what they are collecting, selling, and displaying.

---

## 4. World Presentation

The world should feel like one continuous compact place, not a collection of disconnected maps.

Use:

- Soft transitions between zones.
- Small overlapping decorations.
- Paths that visually connect village to zones.
- A clear boundary that reads as “you cannot leave.”

### 4.1 World Tile and Sprite Grid

- World tile size: `24 x 24` pixels.
- Design resolution: `960 x 540`.
- Viewport: approximately `40 x 22` tiles.
- All world art should be drawn to feel native to the `24px` tile size.
- Character sprites may be smaller than a full tile, but their bounding box should be centered and readable.
- Use nearest-neighbor scaling for pixels.
- Use no full-screen anti-aliasing on sprites.

### 4.2 Draw Order

Use standard top-down y-sort.

Draw order from bottom to top:

1. Terrain.
2. Water base.
3. Shore and path autotiles.
4. Low non-solid decorations.
5. Placed furniture bases.
6. Actors and solid resource nodes.
7. Tall non-blocking decorations.
8. Water ripples and overlays.
9. Particle effects.
10. UI.

Rules:

- Resource nodes should draw above nearby terrain and low decorations.
- A player standing behind a tall bush or rock may be partially obscured, but the resource node being interacted with must remain readable.
- If a decoration would hide a resource node, the decoration should be transparent, moved, or drawn below the node.
- Do not use visual clutter that hides interaction targets.

### 4.3 Shadows

Use soft shadows for:

- Player.
- Shopkeepers.
- Berry bushes.
- Ore nodes.
- Placed furniture.
- Fish bobber.
- Tall decorations.

Shadow style:

- 1-pixel dark `#2E241B` at `25-35%` alpha.
- Elliptical or soft rectangular.
- No hard black shadows.

### Why

Shadows ground objects in the world and make top-down space readable without using vertical axis mechanics.

---

## 5. Zone Visual Identity

Each zone must be distinct but share the same style.

The rule:

> Each zone has one dominant material and one accent color.

### 5.1 Village

#### Identity

The village is the warm starting place.

#### Visual Character

- Packed dirt paths.
- Soft grass edges.
- Small flowers.
- Wooden path trims.
- Lantern posts or small warm lights.
- No large trees.
- No harsh borders.

#### Colors

- Warm earth.
- Dry grass.
- Wood.
- Amber accents.

#### Important Visuals

- Home exterior.
- Museum exterior.
- Trading post area.
- Paths connecting buildings and exits.

The village should feel like a small, maintained home area. It should not be empty.

#### Location Label

- Name: `Village`.
- Icon: small house or lantern.

---

### 5.2 Berry Grove

#### Identity

The berry grove is a soft, leafy collecting area.

#### Visual Character

- Grass with leaf litter.
- Small bushes.
- Fallen leaves.
- Light canopy shadows.
- Berry-colored accents.
- No dense forest that blocks readability.

#### Colors

- Leaf green.
- Warm brown leaf litter.
- Berry red, lavender, and orange accents.

#### Berry Node Visibility

Berry bushes must be clearly visible from a distance.

Use:

- A rounded bush base.
- A visible berry cluster when full.
- A bare branch structure when empty.
- A small shadow.

Do not make berry bushes look like generic trees. They should read as pickable bushes.

#### Location Label

- Name: `Berry Grove`.
- Icon: leaf or berry.

---

### 5.3 Ore Ridge

#### Identity

The ore ridge is a rocky, mineral-rich area.

#### Visual Character

- Gravel paths.
- Cracked stone.
- Small rock clusters.
- Mineral veins.
- Sparse dry grass.
- No dense forest.

#### Colors

- Stone grey.
- Earth brown.
- Copper orange.
- Silver accents.
- Cyan crystal accent for rare tier.

#### Ore Node Visibility

Ore nodes should read as rocks with visible mineral content.

Use:

- A rock base.
- Mineral speckles.
- Visible cracks as charges decrease.
- A soft glow for Crystal Shards.

Do not make ore nodes look like generic boulders without mineral cues.

#### Location Label

- Name: `Ore Ridge`.
- Icon: pick or rock.

---

### 5.4 Lake / Lakeside

#### Identity

The lake is calm, reflective, and easy to read.

#### Visual Character

- Shallow water near shore.
- Deeper water in the middle.
- Reeds and lily pads.
- Soft ripple animation.
- Sandy or pebbly shore.
- No waves that obscure fish spots.

#### Colors

- Teal shallow water.
- Deeper blue water.
- Pale shore sand.
- Reed green.

#### Fish Spot Visibility

Fish spots are water tiles. They should be subtle but readable.

Use:

- A very small ripple or fish-shadow hint.
- A stronger highlight when the player is within interaction radius.
- A bobber during casting/waiting.
- A clear bite animation.

Do not make idle fish spots look like a major animation. The water should remain calm.

#### Location Label

- Name: `Lakeside`.
- Icon: fish or water drop.

---

### 5.5 Perimeter

The perimeter is impassable.

It should visually read as:

- Ocean.
- Cliff edge.
- Dense forest.
- A soft boundary, not a hard wall.

Use:

- Darker water or forest.
- A 1-2 tile visual border.
- No interactive-looking resources in the perimeter.

### Why

The perimeter needs to feel like a natural edge of the island or clearing, not a missing texture.

---

## 6. Resource Node Visual States

The following states are required.

---

### 6.1 Berry Nodes

#### States

| State | Visual |
|---|---|
| Full | Bush with visible berries |
| Empty | Bare bush |
| Picking | Berry shake and pop |
| Respawn | Berry cluster fades/grows in |

#### Full State

A full bush should show:

- A green rounded bush.
- 1 to 3 visible berry clusters.
- A soft shadow.
- Tier-specific berry color.

If the node contains 1 berry, show one clear berry cluster.

If the node contains 2 berries, show two smaller clusters or one larger cluster.

The exact count does not need to be perfectly countable, but it should communicate “there are berries here.”

#### Empty State

An empty bush should show:

- Bare branches.
- A muted green or brown base.
- No berries.
- Slightly lower saturation than full state.

#### Picking Feedback

When picking:

- Bush shakes once.
- A berry icon pops toward the player.
- A small `+1` or `+2` text appears if the resource is collected.

#### Respawn Feedback

When respawning:

- Berries fade in over about `0.3s`.
- Use no flashy burst.

---

### 6.2 Ore Nodes

#### States

| State | Visual |
|---|---|
| 3 charges | Intact rock with mineral speckles |
| 2 charges | One chipped side, one crack |
| 1 charge | Large crack, missing chunk |
| Empty | Hollow cracked rock, muted mineral |
| Mining | Rock shake and chip particles |
| Respawn | Cracks close and mineral reappears |

#### Charge Presentation

Use visible damage progression.

| Charges | Visual Rule |
|---|---|
| 3 | Clean rock shape |
| 2 | Small chip on one side |
| 1 | Larger missing section and crack |
| 0 | Dark interior visible, no bright mineral |

#### Tier Presentation

| Ore | Visual |
|---|---|
| Copper Ore | Brown-orange speckles |
| Silver Ore | Pale silver speckles |
| Crystal Shard | Cyan crystal facets with slow glow |

#### Mining Feedback

When mining:

- Rock shakes.
- 2-3 small stone chips fly.
- A small ore icon pops toward the player.
- A crack appears or grows.

#### Respawn Feedback

When regrowing:

- Cracks fade out.
- Mineral speckles fade in.
- Duration: about `0.3s`.

---

### 6.3 Fish Spots

#### States

| State | Visual |
|---|---|
| Idle | Subtle ripple or fish shadow |
| In Range | Slight highlight |
| Casting | Rod line extends, bobber appears |
| Waiting | Bobber bobs gently |
| Bite | Bobber dips, ripple expands |
| Catch | Splash and fish icon pop |
| Fail | Dull splash, line flicks |
| Cooldown | No major animation |

#### Idle State

Idle fish spots should be subtle.

Use:

- A small ripple ring every `2-3s`.
- A faint fish shadow moving slowly.
- Low contrast.

Do not make every fish spot constantly animated. It would become noisy.

#### Bite State

The bite is the most important fish visual.

Use:

- Bobber dips sharply.
- One ripple ring expands.
- A small splash.
- The interaction prompt changes to strike.

#### Catch State

Use:

- A small fish splash.
- A fish icon pops upward.
- A soft ring expands.

#### Fail State

Use:

- A duller splash.
- The line flicks.
- No fish icon.
- Slight desaturation for one frame.

---

## 7. Characters

### 7.1 Player Character

The player should read as a small, warm, curious collector.

#### Design

Use a simple character with:

- Neutral warm clothing.
- A small satchel or basket.
- A hat or hood for silhouette.
- No large weapon.
- No complex facial detail.

Recommended look:

- Cream shirt.
- Brown vest.
- Straw or wool hat.
- Small canvas satchel.
- Simple legs.

The character should be smaller than most furniture and resource nodes so the world feels larger.

#### Sprite Size

- Character sprite: `16 x 16` pixels.
- Bounding box: centered in a `24 x 24` tile area.
- Shadow: `12 x 6` soft ellipse.

#### Directions

Use **8 directions** for idle and walk.

Use **4 cardinal directions** for action animations:

- Berry picking.
- Mining.
- Fishing.

Why:

- 8-direction idle/walk supports diagonal movement naturally.
- Action states are less frequent, so 4 directions are enough and reduce asset burden.
- This keeps the world feeling smooth without requiring a huge animation set.

#### Animation States

| State | Frames | FPS | Notes |
|---|---:|---:|---|
| Idle | 2 | 4 | Gentle breathing |
| Walk | 4 | 8 | Short step |
| Berry Pick | 2 | 8 | Reaches toward bush |
| Mine | 2 | 8 | Pick swings |
| Fish Cast | 2 | 12 | Rod extends |
| Fish Wait | 2 | 4 | Holding rod |
| Fish Strike | 1 | 12 | Rod snaps forward |
| Fish Catch | 2 | 12 | Small celebration |
| Fish Fail | 2 | 12 | Rod relaxes |

#### Player Visual Feedback

- When gathering: resource icon pops.
- When full inventory: red `Bag Full` prompt.
- When interacting: target object gets a soft highlight.
- When fishing: rod line is visible.

---

### 7.2 Shopkeepers

There are three shopkeepers:

- Moss, berries.
- Grit, ores.
- Reed, fish.

Each should have a distinct silhouette and color accent, but all should share the same painterly style.

#### Moss

- Resource: Berries.
- Silhouette: rounded, soft.
- Colors: soft green, leaf brown, cream.
- Costume: leaf-like hood or small plant hat.
- Personality visual: calm, cozy, approachable.

#### Grit

- Resource: Ores.
- Silhouette: broader, sturdier.
- Colors: brown, copper, grey.
- Costume: sturdy coat, tool belt.
- Personality visual: practical, solid, dependable.

#### Reed

- Resource: Fish.
- Silhouette: longer, relaxed.
- Colors: blue, teal, pale straw.
- Costume: loose poncho, straw hat.
- Personality visual: easygoing, water-adjacent.

#### Animation States

| State | Frames | FPS |
|---|---:|---:|
| Idle | 2 | 4 |
| Talk | 2 | 8 |
| Sell | 1 | 12 |
| Buy | 1 | 12 |
| Unlock | 2 | 12 |

#### Shopkeeper Visual Cues

Each shopkeeper should have:

- A small overhead sign or canopy accent.
- A category color.
- A simple icon:
  - Moss: berry.
  - Grit: pick.
  - Reed: fish.

The trading post should be open-air. Do not build a large closed shop building.

---

## 8. Buildings

### 8.1 Home

#### Exterior

The home should feel warm and small.

Use:

- Wooden walls.
- A simple roof overhang.
- A visible door.
- A small path to the door.
- A soft shadow.

The door should be the clearest interactive point.

#### Interior

The home interior should feel cozy and personal.

Use:

- Warm wood floor.
- Light parchment walls.
- Soft window light or warm lamp glow.
- No clutter by default.
- Clear floor grid in build mode.

The interior should feel like a place the player can personalize.

---

### 8.2 Museum

#### Exterior

The museum should feel like a small public building, not a castle.

Use:

- Stone or plaster walls.
- Brass trim.
- A clear entrance.
- A small museum sign.
- A locked state before unlock.

#### Locked State

Before unlock:

- Door has a brass lock icon.
- The prompt says `Museum Locked`.
- The lock should be visible but not hostile.

#### Unlocked State

After unlock:

- Lock disappears.
- Door opens with a soft brass shimmer.
- The interior becomes visible.

#### Interior

The museum should feel curated and calm.

Use:

- Stone tile floor.
- Warm plaster walls.
- Brass display accents.
- Soft spotlight pools around display cases.
- Slightly brighter than the home.
- More formal but still cozy.

The museum should visually reward placement and curation.

---

### 8.3 Trading Post

The trading post is open-air.

Use:

- Three small stalls or canopy signs.
- Each shopkeeper stands under a colored canopy.
- The canopy color matches their category:
  - Moss: berry red/green.
  - Grit: copper/stone.
  - Reed: blue/teal.
- A small path leads to all three.

Do not make the trading post feel like a closed building.

### Why

The trading post is the economic center. It should be readable at a glance: three shopkeepers, three categories, one small interaction area.

---

## 9. Furniture Visual Presentation

All furniture is top-down.

Furniture should be readable by footprint.

### 9.1 General Furniture Rules

- Each furniture piece should have a clear top-down silhouette.
- Furniture should not look too busy at small size.
- Use one dominant material or color per piece.
- Use small details, not dense texture.
- Use a soft shadow under each placed piece.

### 9.2 Furniture Sprite Sizes

| Furniture Size | Sprite Size |
|---|---:|
| `1x1` | `24 x 24` pixels |
| `2x1` | `48 x 24` pixels |
| `1x2` | `24 x 48` pixels |
| `2x2` | `48 x 48` pixels |

### 9.3 Berry Shop Furniture

| Item | Visual |
|---|---|
| Berry Planter | Square pot, leaves, small berries |
| Berry Jar | Round jar with amber tint and berries |
| Rug | Soft rectangular rug, cream and berry red pattern |
| Berry Bench | Wooden bench with berry cushion |
| Berry Rug | Larger rug with leaf border |

Style: cozy, plant-focused, warm.

### 9.4 Ore Shop Furniture

| Item | Visual |
|---|---|
| Side Table | Small wooden table with a book or ore |
| Bookshelf | Tall shelf with books and tools |
| Ore Lamp | Small round lamp with warm glow |
| Ore Workbench | Worktable with tools |

Style: sturdy, practical, mineral accents.

### 9.5 Fish Shop Furniture

| Item | Visual |
|---|---|
| Fish Net Rack | Small rack with hanging nets |
| Fish Barrel | Round barrel with rope detail |
| Water Shelf | Shelf with shells, bottles, or small fish decor |
| Fish Bench | Bench with a rope or fish hook detail |
| Fish Tank | Glass tank with animated water and small fish shadow |

Style: relaxed, nautical, water-focused.

### 9.6 Display Cases

Display cases are museum-only furniture.

They should look special.

Use:

- Glass or crystal material.
- Brass or stone base.
- Visible exhibit slots.
- Soft light when specimens are assigned.

| Display Case | Visual |
|---|---|
| Small Display Case | Square glass case with 2 visible slot dots |
| Pedestal | Round pedestal with 1 visible slot |
| Crystal Display Case | Square glass case with cyan edge and 3 slots |
| Moon Display Case | Round glass dome with pale blue edge and 3 slots |

#### Exhibit Slot States

| State | Visual |
|---|---|
| Empty | Small dashed circle or faint dot |
| Assigned | Mini specimen icon appears |
| Highlighted | Soft glow around slot |

When a specimen is assigned:

- The display case gets a subtle light.
- The mini specimen icon fades in.
- The museum score update should feel like a small reward.

### 9.7 Build Ghost States

When placing furniture:

| State | Visual |
|---|---|
| Valid | Green footprint at `40%` alpha |
| Invalid | Red footprint at `40%` alpha |
| Selected | White outline around item |
| Rotated | Footprint updates immediately |
| Reason Shown | Small red reason pill near player |

Valid color: `#6FBF73`.

Invalid color: `#D96A5A`.

Do not use flashing for invalid placement. Use a steady red and a clear reason.

### Why

Furniture placement is a core part of the collector fantasy. The ghost must be instantly readable so the player can arrange without frustration.

---

## 10. UI and UX

The UI should feel like a collector’s ledger, not a sci-fi dashboard.

### 10.1 UI Theme

Use:

- Parchment panels.
- Wooden buttons.
- Brass accents.
- Soft drop shadows.
- Rounded corners.
- Small iconography.
- Clear text labels.

#### Panel Style

- Background: `#F3E4C7`.
- Border: `#5C4032`, 2 pixels.
- Corner radius: `3px`.
- Shadow: `rgba(0, 0, 0, 0.25)`, 4-pixel offset.

#### Button Style

| State | Background |
|---|---|
| Normal | `#8A5A3B` |
| Hover | `#B98A63` |
| Pressed | `#7A4A32` |
| Disabled | `#8A7A66` |
| Selected | `#D9A441` border |

Text on buttons: `#2A1B12`.

#### Tab Style

- Active tab: raised parchment card.
- Inactive tab: darker parchment.
- Selected tab gets a brass underline.

### 10.2 Typography

Use a rounded humanist sans-serif.

Recommended fallback stack:

```css
font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
```

If a custom font is desired, use a soft rounded font, but do not require an external font to make the UI readable.

#### Sizes

| Use | Size |
|---|---:|
| Title | `18px` |
| Body | `14px` |
| Small label | `12px` |
| Button text | `14px` |
| Hint text | `12px` |

#### Text Rules

- Text must be readable at `960 x 540`.
- Do not use text smaller than `12px`.
- Use high contrast:
  - Dark text on parchment.
  - Parchment text on dark wood.
- Do not place important text directly over busy world art without a background panel.

---

## 11. Persistent HUD

The HUD should be readable at a glance and should not cover important world space.

Use a minimal layout.

### 11.1 HUD Layout

At `960 x 540`:

| HUD Element | Position |
|---|---|
| Location label | Top-left |
| Ledger button | Top-left, next to location |
| Coins | Top-right |
| Minimap | Top-right, below coins |
| Tool tier indicators | Bottom-left |
| Inventory | Bottom-center |
| Contextual hints | Bottom-right |
| Interaction prompt | Center-lower screen |
| Gathering progress bar | Above interaction prompt |
| Fishing meter | Center screen |
| Toasts | Top-center |

### 11.2 Location Label

Top-left.

Shows current zone:

- Village.
- Berry Grove.
- Ore Ridge.
- Lakeside.
- Home.
- Museum.

Style:

- Small parchment tag.
- 16-pixel zone icon.
- Zone name.
- Slight drop shadow.

Why:

The player needs constant orientation in a compact open world.

---

### 11.3 Ledger Button

Next to location label.

Style:

- Small wooden button.
- Book or scroll icon.
- Keyboard hint: `C`.
- If a goal is active, show a small gold dot.

---

### 11.4 Coins

Top-right.

Style:

- Parchment pill.
- Coin icon.
- Coin amount.
- Coin icon: `#E5C158`.

When coins increase:

- Coin icon pulses.
- A small `+N` floats upward.

When coins are spent:

- A small `-N` floats upward.
- Do not use red for normal spending. Use neutral amber.

---

### 11.5 Minimap

Size: approximately `96 x 96` pixels.

Style:

- Wooden frame.
- Parchment background.
- Biome color regions.
- Player dot.
- Home dot.
- Museum dot.
- Trading post dot.

Biome colors on minimap:

| Zone | Minimap Color |
|---|---:|
| Village | `#D9A441` |
| Berry Grove | `#5E8C4A` |
| Ore Ridge | `#A5765B` |
| Lakeside | `#4E9BB0` |

Player marker:

- White dot.
- Small direction triangle.

Building markers:

- Home: small house icon.
- Museum: small museum icon.
- Trading Post: small coin or stall icon.

Do not show individual resource nodes on the minimap.

### Why

The minimap helps orientation without cluttering the world. Showing every node would reduce the feeling of exploration and create visual noise.

---

### 11.6 Tool Tier Indicators

Bottom-left.

Show three tool categories:

- Berry tool.
- Mining tool.
- Fishing tool.

Each indicator:

- 32-pixel icon.
- Category color ring.
- Tier pips below.

Tier display:

| Tier | Visual |
|---|---|
| Tier 1 | One pip |
| Tier 2 | Two pips |
| Tier 3 | Three pips |

Pip color:

- Empty: `#5C4032`.
- Filled: `#D9A441`.

Do not use stars if pips are clearer.

### Why

Pips are easier to read at small size than stars and scale cleanly.

---

### 11.7 Inventory

Bottom-center.

Use 10 slots.

Slot style:

- 28 x 28 pixels.
- Parchment background.
- 2-pixel wood border.
- Empty slots show a faint dashed border.
- Stack count appears in bottom-right corner of the slot.

Slot hover:

- Tooltip appears above slot.
- Tooltip shows:
  - Resource name.
  - Stack count.
  - Base sell price.
  - Current shop price if at matching shop.

Inventory full:

- Slots border becomes invalid red for one short pulse.
- Prompt says `Bag Full`.

### Why

The inventory is central. It must be readable even when the world is busy.

---

### 11.8 Contextual Hints

Bottom-right.

Show only hints that apply to the current context.

Examples:

- `E` Interact.
- `B` Build Mode.
- `C` Ledger.
- `Esc` Cancel.

Style:

- Small parchment tag.
- Key shown in a wooden key cap.
- Short label.

Do not show all controls at once.

### Why

A collector game should feel calm. Constant control lists create clutter.

---

## 12. Interaction and Feedback UX

### 12.1 Interaction Prompt

The interaction prompt appears when an object is in range.

Style:

- Center-lower screen.
- Pill-shaped parchment tag.
- Action icon.
- Key hint.
- Short text.

Examples:

- `Pick Sweet Berry`
- `Mine Copper Ore`
- `Cast Line`
- `Talk to Moss`
- `Enter Home`
- `Museum Locked`
- `Place Furniture`

Locked state:

- Grey pill.
- Lock icon.
- Requirement text if helpful.

---

### 12.2 Target Highlight

When an interactable object is targeted:

- Soft white outline.
- Slight brightening.
- No bouncing.
- No fast pulse.

Why:

A calm highlight communicates target without breaking the relaxed mood.

---

### 12.3 Gathering Progress Bar

Used for:

- Berry picking.
- Mining.

Style:

- 160 x 12 pixels.
- Dark wood background.
- Gold fill.
- 2-pixel parchment border.
- Small category icon on the left.

Fill color:

- Use neutral gold for all gathering actions.
- Do not change color per resource.

Why:

A single progress bar is easier to read and keeps the HUD consistent.

---

### 12.4 Fishing Meter

Used during the bite phase.

Style:

- 240 x 20 pixels.
- Dark water background.
- Parchment border.
- Moving indicator.
- Green success zone.
- Yellow chance zones.

Zones:

| Zone | Color |
|---|---:|
| Green | `#6FBF73` |
| Yellow | `#E3B23C` |
| Background | `#2E241B` |

The indicator should be a small vertical white bar.

During fishing:

- The water around the bobber slightly darkens.
- The meter is centered.
- The prompt says `Strike!` when the bite appears.

### Why

The fishing meter is the only timed skill moment. It must be readable without becoming stressful.

---

### 12.5 Required Visual Feedback

The following events need visible feedback.

| Event | Visual Feedback |
|---|---|
| Resource collected | Icon pops, `+1` or `+2` text |
| Resource sold | Coins fly to coin HUD, `+N` appears |
| Coins changed | Coin HUD pulse |
| Goal progress updated | Small ledger icon pulse |
| Goal completed | Center checkmark and gold glow |
| Shop stock unlocked | Shopkeeper sign sparkles |
| Museum unlocked | Lock fades, door shimmer |
| New specimen collected | Collection card flips |
| Tool purchased | Tool pips update, sparkle |
| Furniture purchased | Item card enters build inventory |
| Furniture placed | Soft dust and settle |
| Furniture removed | Item shrinks and fades |
| Furniture sold | Coin pop and card exit |
| Specimen assigned | Display slot icon fades in |
| Specimen unassigned | Display slot icon fades out |
| Final completion | Curator’s Seal screen |

---

## 13. Shop UI

The shop UI is a modal.

### 13.1 Shop Modal

Size: approximately `640 x 420` pixels.

Position: centered.

Style:

- Parchment panel.
- Wooden frame.
- Shopkeeper name at top.
- Coin total at top-right.
- Buy and Sell tabs.

Tabs:

- Buy.
- Sell.

Active tab:

- Raised parchment.
- Brass underline.

---

### 13.2 Sell Tab

Show one row for each sellable resource.

Each row:

- Resource icon.
- Resource name.
- Stack count.
- Current unit price.
- Stack total.
- Sell button.

Controls:

- Click sell to sell one unit.
- Shift-click or stack button to sell whole stack.
- Sell All button.

Coin feedback:

- On sale, coins fly from the row to the coin HUD.
- A small `+N` appears.

---

### 13.3 Supply Meter

The supply meter must be readable and accessible.

Use a 5-segment horizontal meter.

Each segment:

- 24 x 10 pixels.
- Filled based on supply level.

States:

| Supply State | Label | Meter Fill | Color |
|---|---|---:|---:|
| Normal Price | `Normal Price` | 5/5 | `#6FBF73` |
| Low Price | `Low Price` | 4/5 | `#E3B23C` |
| Very Low Price | `Very Low Price` | 3/5 | `#E37B3C` |
| Barely Buying | `Barely Buying` | 2/5 | `#D96A5A` |

Also show text label.

Do not rely on color alone.

### Why

Colorblind-safe design is important for a UI that uses color states. Text labels and segmented fill make the state understandable.

---

### 13.4 Buy Tab

Show shop items in a two-column grid.

Each item card:

- Item icon.
- Item name.
- Cost.
- Short description.
- Buy button.

Locked item:

- Card at `30%` alpha.
- Lock icon.
- Requirement text.

Examples:

- `Sell 5 berries to unlock`
- `Sell 25 ores to unlock`
- `Unique: already owned`
- `Museum only`

Disabled buy button:

- Use disabled style.
- Do not remove the item card.

### Why

Locked items should communicate progression, not hide content.

---

## 14. Build Mode UI

Build mode is available only inside the Home or Museum.

### 14.1 Build Mode Visual State

When build mode is active:

- Floor grid appears.
- Grid lines: `rgba(255, 255, 255, 0.12)`.
- Valid tile highlight: `rgba(111, 191, 115, 0.25)`.
- Invalid tile highlight: `rgba(217, 106, 90, 0.25)`.
- Furniture ghost follows mouse.
- Selected item card appears.
- Building score appears.

---

### 14.2 Selected Item Card

Show:

- Item icon.
- Item name.
- Footprint size.
- Rotation state.
- Placement validity.
- Reason if invalid.

Invalid reasons:

- `Blocked`
- `Not Floor`
- `Museum Only`
- `Blocks Door Path`
- `Covers Door`
- `Covers Player`

Style:

- Small parchment card.
- Red reason text.
- No alarm effect.

---

### 14.3 Build Inventory Panel

Show purchased but unplaced furniture.

Style:

- Right-side panel.
- Parchment background.
- Item list.
- Each item shows:
  - Icon.
  - Name.
  - Footprint.
  - Resell value.
  - Museum-only badge if applicable.

Selected item:

- Brass outline.
- Slightly larger.

---

### 14.4 Resell Panel

For unplaced furniture:

- Show item icon.
- Show refund amount.
- Sell button.

Refund logic visual:

- If never placed: show `100%` refund.
- If previously placed: show `50%` refund.

Do not show complicated math. Just show the exact coin amount.

---

### 14.5 Exhibit Panel

When selecting a placed display case:

Show:

- Display case name.
- Exhibit slots.
- Assigned specimens.
- Unassigned unlocked specimens.
- Assign button.
- Remove button.

Style:

- Museum parchment panel.
- Brass trim.
- Specimen mini icons.
- Empty slots as faint dashed circles.

When assigning:

- The slot icon fades in.
- A soft chime plays.
- The display case gets a subtle light.

When removing:

- The slot icon fades out.
- The case light dims.

### Why

The exhibit panel is where the museum fantasy becomes real. It should feel like curating specimens, not filling inventory slots.

---

## 15. Ledger UI

The Ledger is the player’s record of goals, collection, and building scores.

### 15.1 Ledger Modal

Size: approximately `640 x 440` pixels.

Tabs:

- Goals.
- Collection.
- Scores.

Style:

- Parchment book.
- Wooden cover.
- Brass tab dividers.
- Small checkmark icons.

---

### 15.2 Goals Tab

Show:

- Current goal.
- Progress.
- Rewards.
- Completed goals.

Each goal row:

- Goal name.
- Requirement text.
- Progress bar or fraction.
- Reward.
- Checkmark if complete.

Active goal:

- Brass border.
- Slight highlight.

Completed goal:

- Green checkmark.
- Slightly reduced contrast.

Progress bars:

- Parchment background.
- Gold fill.
- Small fraction text.

---

### 15.3 Collection Tab

Show all 9 specimens in a 3x3 grid.

Each collection card:

- Specimen icon.
- Specimen name.
- Location hint.
- Exhibit score.
- Assigned status.

Unlocked specimen:

- Full color icon.
- Paper background.
- Location hint.

Locked specimen:

- Silhouette icon.
- Grey background.
- Location hint.
- `Not Collected` text.

Assigned to museum:

- Small brass badge.
- `Displayed` text.

### Why

The collection tab is the collector’s heart. It should feel like a field guide or museum catalogue.

---

### 15.4 Scores Tab

Show:

- Home Score.
- Museum Score.
- Museum exhibit count.
- Museum furniture count.
- Home furniture count.

Style:

- Two large cards.
- One for Home.
- One for Museum.
- Brass numerals.

Scores should feel non-threatening. They are progress, not grades.

---

## 16. Toasts

Toasts appear top-center.

### 16.1 Toast Style

Size: approximately `320 x 44` pixels.

Style:

- Parchment card.
- 4-pixel left color bar.
- Small icon.
- Text.
- Drop shadow.

Duration: `3s`.

Animation:

- Slide down `16px`.
- Fade out after `3s`.
- No bounce.

Stacking:

- Max 3 visible toasts.
- Stack downward.
- Older toasts fade out first.

---

### 16.2 Toast Types

| Type | Color Bar | Icon |
|---|---:|---|
| Goal Complete | `#D9A441` | Checkmark |
| Shop Unlock | `#86E8FF` | Shop sign |
| Museum Unlock | `#C7A24A` | Museum door |
| New Specimen | `#8E7BD1` | Specimen card |
| Tool Purchase | `#D9A441` | Tool icon |
| Furniture Purchase | `#8A5A3B` | Furniture icon |
| Coin Gain | `#E5C158` | Coin |
| Error | `#D96A5A` | Cross |
| Save | `#6FBF73` | Quill or check |

Examples:

- `Goal Complete: First Trades`
- `Museum Unlocked`
- `New Specimen: Moon Berry`
- `Bought Honey Pouch`
- `Museum Locked: Sell more resources`

### Why

Toasts should inform without interrupting. They are important progression feedback, but they should never feel like alerts.

---

## 17. Minimap and World Legibility

### 17.1 Minimap Style

Use a soft parchment map.

Rules:

- No individual resource nodes.
- No moving animation.
- Clear biome colors.
- Player dot always visible.
- Building icons always visible.
- The current zone can have a slightly brighter highlight.

### 17.2 Location Clarity

Each zone should be identifiable before the player reaches the label.

Use:

- Distinct terrain.
- Distinct accent colors.
- Distinct resource sprites.
- Small environmental details.

Examples:

- Berry Grove: leaves and bushes.
- Ore Ridge: rocks and gravel.
- Lakeside: water and reeds.
- Village: paths and lanterns.

### Why

The player should feel they are moving through a coherent island, not loading separate levels.

---

## 18. UX Journey

The visual UX should guide the player through the collector fantasy without being hand-holdy.

### 18.1 First Launch

The first visual moment should be calm and clear.

On first load:

- Show title screen.
- Show `Start` and `Continue` if save exists.
- Show short controls:
  - `WASD` Move.
  - `E` Interact.
  - `C` Ledger.
  - `B` Build inside buildings.

Do not show a long tutorial.

---

### 18.2 First World Moment

When the game starts:

- Player is near Home.
- Location label says `Village`.
- A toast says:
  - `Goal: First Harvest`.
- The ledger icon has a gold dot.
- The first goal is visible in the HUD.

The player should understand:

- I can move.
- I can interact.
- I need to collect things.
- I can check goals in the ledger.

---

### 18.3 First Gathering

When the player first collects a resource:

- Resource icon pops.
- Inventory slot fills.
- A small toast appears if it is a new specimen:
  - `New Specimen: Sweet Berry`.

---

### 18.4 First Selling

When the player first sells:

- Coin HUD pulses.
- Coins fly.
- Supply meter appears in shop UI.
- If shop tier unlocks, show toast:
  - `Moss’s Stock Updated`.

---

### 18.5 First Furniture

When the player first enters build mode:

- Floor grid appears.
- A one-time hint appears:
  - `Use mouse to place, R to rotate, X to remove`.
- The build inventory panel appears.
- The first furniture item should be visually clear.

---

### 18.6 Museum Unlock

When the museum unlocks:

- The lock on the museum door fades.
- A brass shimmer crosses the door.
- A toast appears:
  - `Museum Unlocked`.
- The first time the player enters, the interior should feel slightly brighter and more formal.

---

### 18.7 Final Completion

When Curator’s Seal completes:

- The screen gently darkens at the edges.
- A curator’s seal stamps onto the center.
- Gold leaf particles fall slowly.
- A final music sting plays.
- Text says:
  - `Curator’s Seal Complete`
- Subtext says:
  - `Your museum is open.`

Do not use confetti. Use slow gold leaf.

### Why

Completion should feel like a museum opening, not a victory lap.

---

## 19. Accessibility

The game should be readable for a broad range of players.

### 19.1 Colorblind Safety

Never rely on color alone for important states.

Use:

- Icons.
- Text labels.
- Patterns.
- Shapes.
- Position.

Examples:

- Supply meter uses color plus text and segment fill.
- Valid placement uses green plus checkmark or solid outline.
- Invalid placement uses red plus cross or reason text.
- Resource icons have unique silhouettes.

---

### 19.2 Resource Icon Shapes

Use distinct silhouettes for all resources.

| Resource | Icon Shape |
|---|---|
| Sweet Berry | Round berry with leaf |
| Moon Berry | Round berry with crescent mark |
| Ember Berry | Round berry with flame mark |
| Copper Ore | Hexagonal ore with speckles |
| Silver Ore | Hexagonal ore with vertical stripe |
| Crystal Shard | Triangle prism |
| Minnow | Small round fish |
| Trout | Longer fish |
| Moonfish | Fish with crescent mark |

### Why

Colorblind players and small-screen readers need shape differentiation.

---

### 19.3 Text Readability

Rules:

- Minimum UI text size: `12px`.
- Important text always has a background panel.
- Use high contrast.
- Avoid placing white text on bright water without shadow.
- Avoid placing dark text on dark rock without panel.

---

### 19.4 Reduce Motion

Add a `Reduce Motion` setting.

When enabled:

- Disable water ripple animation.
- Disable particles.
- Disable toast slide.
- Disable goal pulse.
- Keep essential state changes.
- Keep text updates.

Why:

Some players need to reduce visual motion, but they still need to see state changes.

---

### 19.5 High Contrast

Add a `High Contrast` setting.

When enabled:

- Increase UI border thickness.
- Use stronger text contrast.
- Make valid/invalid placement outlines thicker.
- Make inventory slot borders clearer.
- Make target highlights stronger.

Do not change gameplay mechanics.

---

### 19.6 Audio Settings

The UI should include:

- Music volume.
- SFX volume.
- Ambient volume.
- Reduce Motion toggle.
- High Contrast toggle.

These are visual/UX settings even though audio values are implementation details.

---

## 20. Music Design

The music should feel warm, small, and collector-like.

### 20.1 Musical Identity

Style:

- Cozy acoustic.
- Gentle lo-fi warmth.
- Soft percussion.
- Wood and string instruments.
- No heavy drums.
- No aggressive electronic pulses.
- No dark horror themes.

Instruments:

- Marimba.
- Kalimba.
- Soft guitar.
- Piano.
- Ocarina.
- Harp.
- Light strings.
- Celesta.
- Soft brushed percussion.
- Subtle water or wind textures.

Tempo:

- `72-84 BPM` for world music.
- `70-78 BPM` for interiors.
- Stingers can be faster but remain soft.

Key relationship:

Keep music in a related family so transitions feel calm.

Use:

- E major.
- A minor.
- C# minor.
- D major.

Do not use dissonant or jarring transitions between zones.

---

### 20.2 Music Layers

Use adaptive layering.

#### Layer 1: Zone Base

Each zone has its own base loop.

#### Layer 2: Zone Motif

A short melodic motif identifies the zone.

#### Layer 3: Activity Layer

A small layer appears during specific actions:

- Gathering.
- Fishing.
- Building.
- Shop interaction.

#### Layer 4: Moment Stingers

Used for:

- Goal complete.
- Shop unlock.
- Museum unlock.
- Final completion.

### Why

Layered music makes the world feel alive without becoming busy. The player should feel the game is responding softly.

---

### 20.3 Zone Music

| Zone | Instrument Focus | Mood |
|---|---|---|
| Village | Marimba, soft guitar | Warm, home-like |
| Berry Grove | Ocarina, pizzicato strings | Gentle, leafy |
| Ore Ridge | Kalimba, low strings | Steady, earthy |
| Lakeside | Harp, soft strings | Calm, reflective |
| Home | Piano, muted guitar | Cozy, personal |
| Museum | Strings, celesta | Curated, bright but quiet |

---

### 20.4 Activity Music Cues

| Activity | Layer |
|---|---|
| Gathering berries | Soft marimba pluck |
| Mining | Gentle low pulse |
| Fishing | Light harp glissando or water note |
| Build mode | Soft kalimba tick |
| Shop open | Bright but quiet wood layer |

These layers should be optional and subtle.

If the activity layer becomes distracting, remove it. The base zone loop must still work alone.

---

### 20.5 Transitions

Use crossfades:

- Zone to zone: `1s` crossfade.
- World to interior: `1s` crossfade.
- Shop open: quick `0.5s` layer add.
- Shop close: quick `0.5s` layer remove.
- Goal complete: stinger over current music.
- Final completion: music fades into completion theme.

No hard cuts unless entering a new interior.

---

### 20.6 Required Music Files

Use these naming conventions:

| File | Purpose |
|---|---|
| `music/title_loop.ogg` | Title screen |
| `music/village_loop.ogg` | Village |
| `music/berry_grove_loop.ogg` | Berry Grove |
| `music/ore_ridge_loop.ogg` | Ore Ridge |
| `music/lakeside_loop.ogg` | Lakeside |
| `music/home_loop.ogg` | Home interior |
| `music/museum_loop.ogg` | Museum interior |
| `music/shop_layer.ogg` | Shop overlay |
| `music/build_layer.ogg` | Build overlay |
| `music/goal_complete.ogg` | Goal stinger |
| `music/shop_unlock.ogg` | Shop unlock stinger |
| `music/museum_unlock.ogg` | Museum unlock stinger |
| `music/final_completion.ogg` | Completion theme |

Use `.ogg` for browser compatibility.

---

## 21. Sound Effects

The SFX should be short, warm, and satisfying.

General rules:

- No harsh clicks.
- No loud explosions.
- No scary sounds.
- Most SFX should be `50ms` to `300ms`.
- Use small pitch variation to avoid mechanical repetition.
- Keep SFX lower than music except for important moments.

### 21.1 Required SFX List

| Event | SFX Character | Duration |
|---|---|---:|
| Footstep on grass | Soft short noise | `40ms` |
| Footstep on stone | Slightly harder tap | `50ms` |
| Water step | Soft plop | `80ms` |
| Berry pick complete | Sweet pop plus pluck | `80ms` |
| Ore mine complete | Stone chip plus low thud | `100ms` |
| Fish cast | Soft whoosh | `120ms` |
| Fish bite | Bobber dip plus small plop | `80ms` |
| Fish catch | Splash plus bright chime | `250ms` |
| Fish fail | Dull splash plus low blip | `150ms` |
| Coin sale | Coin plink plus tiny jingle | `150ms` |
| Coin buy | Softer coin | `100ms` |
| Furniture place | Wood tap | `80ms` |
| Furniture remove | Soft pop | `60ms` |
| Furniture sell | Coin plus paper | `120ms` |
| UI hover | Very soft tick | `20ms` |
| UI click | Small click | `30ms` |
| UI open | Soft whoosh | `80ms` |
| UI close | Soft reverse whoosh | `80ms` |
| Invalid action | Low muted buzz | `100ms` |
| Inventory full | Muted thud | `80ms` |
| Specimen assigned | Glass chime | `200ms` |
| Specimen unassigned | Lower glass chime | `150ms` |
| Goal complete | Warm rising bell | `2s` |
| Shop unlock | Soft bright chord | `800ms` |
| Museum unlock | Door chime plus shimmer | `800ms` |
| Final completion | Full warm theme sting | `6-10s` |

---

### 21.2 SFX Details

#### Berry Pick

Character:

- Small sweet pop.
- Tiny musical pluck.
- Slight upward pitch.

Purpose:

The player should feel like they are picking something fresh.

---

#### Ore Mine

Character:

- Short stone chip.
- Low wooden or stone thud.
- Slight grit.

Purpose:

The player should feel like they are working a rock.

---

#### Fish Cast

Character:

- Soft whoosh.
- Line extends.
- Water entry plop.

Purpose:

The cast should feel light, not heavy.

---

#### Fish Bite

Character:

- Quick plop.
- Slight ripple.
- No alarm.

Purpose:

The bite should be noticeable but not stressful.

---

#### Fish Catch

Character:

- Soft splash.
- Bright chime.
- Slight upward feel.

Purpose:

The catch should feel rewarding.

---

#### Fish Fail

Character:

- Duller splash.
- Low blip.
- Slight deflation.

Purpose:

Failure should be mild. The player should feel a small miss, not punishment.

---

#### Coin Sale

Character:

- Coin plink.
- Tiny jingle.
- Warm, not metallic-sharp.

Purpose:

Selling is the core satisfying loop.

---

#### Furniture Place

Character:

- Soft wood tap.
- Tiny settle.

Purpose:

Placement should feel satisfying and physical.

---

#### Invalid Action

Character:

- Low short buzz.
- Muted.
- Not annoying.

Purpose:

The player should understand the action failed without feeling punished.

---

#### Goal Complete

Character:

- Warm rising bell.
- Soft chord.
- No fanfare horns.

Purpose:

Goals are meaningful, but the game remains calm.

---

#### Final Completion

Character:

- Full but gentle theme.
- Warm strings and celesta.
- Slow gold-leaf shimmer.

Purpose:

The final moment should feel like a museum opening.

---

## 22. Ambient Audio

Use soft ambient loops per zone.

Ambience should be low volume and never compete with music or SFX.

| Zone | Ambience |
|---|---|
| Village | Distant birds, soft wind, faint village life |
| Berry Grove | Leaves, soft insects, gentle breeze |
| Ore Ridge | Low wind, small stone taps |
| Lakeside | Water lapping, distant birds, soft reed rustle |
| Home | Quiet room tone, soft fire crackle or lamp hum |
| Museum | Quiet room tone, subtle air movement |

Rules:

- Ambience should loop seamlessly.
- No sudden animal sounds.
- No loud water splashes unless fishing.
- No creepy night sounds.
- Keep the world feeling safe.

---

## 23. Audio Balance

Suggested relative volumes:

| Audio Type | Relative Level |
|---|---:|
| Music | `-18dB` |
| SFX | `-12dB` |
| Ambience | `-24dB` |
| Important stingers | `-10dB` |

Rules:

- SFX should be clearly audible.
- Music should remain pleasant in the background.
- Ambience should be barely noticed unless the player is idle.
- No sound should cause discomfort.

---

## 24. Audio Generation Reference

The following is a reference style for simple SFX synthesis if assets are generated procedurally.

This is not required implementation, but it defines the intended sound character.

### 24.1 Simple Tone Reference

```text
Tone:
  start frequency
  end frequency
  duration
  waveform
  attack
  release

Example coin:
  start: 1400Hz
  end: 1900Hz
  duration: 0.08s
  waveform: sine
  attack: 0.005s
  release: 0.02s
  gain: 0.12

Example UI click:
  start: 1800Hz
  end: 1600Hz
  duration: 0.02s
  waveform: square
  attack: 0.001s
  release: 0.01s
  gain: 0.04

Example invalid:
  start: 220Hz
  end: 180Hz
  duration: 0.08s
  waveform: square
  attack: 0.002s
  release: 0.02s
  gain: 0.08
  filter: lowpass 800Hz
```

### 24.2 Noise Reference

```text
Noise:
  duration
  filter type
  filter frequency
  gain

Example berry pop:
  duration: 0.03s
  filter: highpass
  frequency: 2000Hz
  gain: 0.06

Example ore chip:
  duration: 0.06s
  filter: bandpass
  frequency: 900Hz
  gain: 0.10

Example water splash:
  duration: 0.18s
  filter: bandpass
  frequency: 1200Hz
  gain: 0.12
  pitch slide: -30%
```

### Why

This gives the audio agent a concrete target for procedural or synthesized sounds while allowing real recorded assets if preferred.

---

## 25. Asset Handoff

### 25.1 File Naming

Use consistent naming.

#### World Tiles

```text
world/village/grass_01.png
world/village/path_01.png
world/berry_grove/grass_01.png
world/berry_grove/leaf_litter_01.png
world/ore_ridge/rock_01.png
world/lakeside/shallow_water_01.png
world/lakeside/deep_water_01.png
world/perimeter/ocean_01.png
```

#### Resource Nodes

```text
nodes/berry/sweet_full_01.png
nodes/berry/sweet_full_02.png
nodes/berry/sweet_empty_01.png
nodes/berry/moon_full_01.png
nodes/berry/moon_empty_01.png
nodes/berry/ember_full_01.png
nodes/berry/ember_empty_01.png

nodes/ore/copper_3.png
nodes/ore/copper_2.png
nodes/ore/copper_1.png
nodes/ore/copper_0.png
nodes/ore/silver_3.png
nodes/ore/silver_2.png
nodes/ore/silver_1.png
nodes/ore/silver_0.png
nodes/ore/crystal_3.png
nodes/ore/crystal_2.png
nodes/ore/crystal_1.png
nodes/ore/crystal_0.png
```

#### Fish Spots

```text
fish/idle_01.png
fish/idle_02.png
fish/highlight.png
fish/cast_line.png
fish/bobber.png
fish/bite_ripple.png
fish/catch_splash.png
fish/fail_splash.png
```

#### Player

```text
player/idle_n_00.png
player/idle_n_01.png
player/walk_n_00.png
player/walk_n_01.png
player/walk_n_02.png
player/walk_n_03.png

player/gather_berry_up_00.png
player/gather_berry_down_00.png
player/mine_left_00.png
player/fish_cast_right_00.png
```

Use the same pattern for all directions.

#### Shopkeepers

```text
npc/moss/idle_n_00.png
npc/moss/talk_n_00.png
npc/moss/sell_00.png

npc/grit/idle_n_00.png
npc/grit/talk_n_00.png
npc/grit/sell_00.png

npc/reed/idle_n_00.png
npc/reed/talk_n_00.png
npc/reed/sell_00.png
```

#### Furniture

```text
furniture/berry/planter_1x1.png
furniture/berry/jar_1x1.png
furniture/berry/rug_2x2.png
furniture/berry/bench_2x1.png

furniture/ore/table_1x1.png
furniture/ore/bookshelf_1x2.png
furniture/ore/lamp_1x1.png
furniture/ore/workbench_2x1.png

furniture/fish/net_rack_1x1.png
furniture/fish/barrel_1x1.png
furniture/fish/water_shelf_1x1.png
furniture/fish/bench_2x1.png
furniture/fish/tank_2x1.png

furniture/display/small_case_1x1.png
furniture/display/pedestal_1x1.png
furniture/display/crystal_case_1x1.png
furniture/display/moon_case_1x1.png
```

#### Icons

```text
icon/resource/sweet_berry.png
icon/resource/moon_berry.png
icon/resource/ember_berry.png
icon/resource/copper_ore.png
icon/resource/silver_ore.png
icon/resource/crystal_shard.png
icon/resource/minnow.png
icon/resource/trout.png
icon/resource/moonfish.png

icon/tool/berry_t1.png
icon/tool/berry_t2.png
icon/tool/berry_t3.png
icon/tool/mine_t1.png
icon/tool/mine_t2.png
icon/tool/mine_t3.png
icon/tool/fish_t1.png
icon/tool/fish_t2.png
icon/tool/fish_t3.png

icon/ui/coin.png
icon/ui/ledger.png
icon/ui/lock.png
icon/ui/check.png
icon/ui/valid.png
icon/ui/invalid.png
```

#### UI

```text
ui/panel_parchment.png
ui/button_wood.png
ui/button_wood_hover.png
ui/button_wood_pressed.png
ui/button_wood_disabled.png
ui/tab_active.png
ui/tab_inactive.png
ui/progress_bar_background.png
ui/progress_bar_fill.png
ui/fishing_meter_background.png
ui/fishing_meter_green.png
ui/fishing_meter_yellow.png
ui/toast_background.png
ui/supply_meter_segment.png
ui/minimap_frame.png
ui/inventory_slot.png
ui/inventory_slot_empty.png
```

#### Music and SFX

```text
music/title_loop.ogg
music/village_loop.ogg
music/berry_grove_loop.ogg
music/ore_ridge_loop.ogg
music/lakeside_loop.ogg
music/home_loop.ogg
music/museum_loop.ogg
music/shop_layer.ogg
music/build_layer.ogg
music/goal_complete.ogg
music/shop_unlock.ogg
music/museum_unlock.ogg
music/final_completion.ogg

sfx/footstep_grass.ogg
sfx/footstep_stone.ogg
sfx/water_step.ogg
sfx/berry_pick.ogg
sfx/ore_mine.ogg
sfx/fish_cast.ogg
sfx/fish_bite.ogg
sfx/fish_catch.ogg
sfx/fish_fail.ogg
sfx/coin_sale.ogg
sfx/coin_buy.ogg
sfx/furniture_place.ogg
sfx/furniture_remove.ogg
sfx/furniture_sell.ogg
sfx/ui_hover.ogg
sfx/ui_click.ogg
sfx/ui_open.ogg
sfx/ui_close.ogg
sfx/invalid.ogg
sfx/inventory_full.ogg
sfx/specimen_assign.ogg
sfx/specimen_unassign.ogg
sfx/goal_complete.ogg
sfx/shop_unlock.ogg
sfx/museum_unlock.ogg
sfx/final_completion.ogg

ambience/village.ogg
ambience/berry_grove.ogg
ambience/ore_ridge.ogg
ambience/lakeside.ogg
ambience/home.ogg
ambience/museum.ogg
```

---

## 26. Texture and Sprite Generation Reference

This section provides a simple reference for generating coherent pixel textures.

It is not required implementation, but it defines the visual target.

### 26.1 Palette Object

```js
const palette = {
  ink: "#2E241B",
  woodDark: "#5C4032",
  wood: "#8A5A3B",
  woodLight: "#B98A63",
  parchment: "#F3E4C7",
  paper: "#F9F1DC",
  path: "#C2A374",
  grass: "#85A66A",
  grassShadow: "#5F7A4C",
  stone: "#8C867B",
  stoneLight: "#B9B2A6",
  waterShallow: "#6FB0C4",
  waterDeep: "#3F7D96",
  gold: "#D9A441",
  valid: "#6FBF73",
  invalid: "#D96A5A",
  warning: "#E3B23C"
};
```

### 26.2 Terrain Tile Generation Rule

A tile should be generated as:

1. Fill with base color.
2. Add 20-40 darker speckles.
3. Add 10-20 lighter speckles.
4. Add 1-2 accent details.
5. Add a soft bottom shadow line.

Example concept:

```text
grass tile:
  base: #85A66A
  dark speckles: #5F7A4C
  light speckles: #A3B37A
  accent: small flower in #D94F5C or #F3E4C7
  shadow: 1px bottom row, #2E241B at 15% alpha
```

```text
stone tile:
  base: #8C867B
  dark speckles: #6D675D
  light speckles: #B9B2A6
  accent: small copper or crystal fleck
  shadow: 1px bottom row, #2E241B at 15% alpha
```

```text
water tile:
  base: #6FB0C4 for shallow, #3F7D96 for deep
  ripple lines: lighter blue
  shore edge: sand color #C2A374
```

### Why

Using the same generation logic helps different tiles feel like they belong to the same world.

---

## 27. Visual Moments

These are the emotional beats the visuals should support.

### 27.1 Opening

The player sees a small warm village.

Goal:

Make the player feel safe and curious.

Visual cues:

- Soft grass.
- Wooden paths.
- Warm home light.
- Clear goal indicator.

---

### 27.2 First Collection

The player picks a berry or mines an ore.

Goal:

Make gathering feel tactile.

Visual cues:

- Node shake.
- Resource icon pop.
- Inventory fill.
- Soft SFX.

---

### 27.3 First Sale

The player sells to a shopkeeper.

Goal:

Make trading feel satisfying.

Visual cues:

- Coin flight.
- Coin HUD pulse.
- Supply meter visible.
- Shopkeeper reaction.

---

### 27.4 First Furniture

The player places their first furniture.

Goal:

Make building feel personal.

Visual cues:

- Build ghost.
- Valid green footprint.
- Soft dust on placement.
- Home score update.

---

### 27.5 Museum Unlock

The museum opens.

Goal:

Make the collection fantasy become real.

Visual cues:

- Lock fades.
- Brass shimmer.
- Museum interior brighter.
- Display cases become available.

---

### 27.6 First Specimen Display

The player assigns a specimen.

Goal:

Make curation feel rewarding.

Visual cues:

- Slot icon fades in.
- Display case lights.
- Museum score updates.
- Soft chime.

---

### 27.7 Final Completion

The Curator’s Seal completes.

Goal:

Make completion feel like a quiet ceremony.

Visual cues:

- Gold leaf.
- Curator’s seal stamp.
- Warm final theme.
- Museum remains open.

---

## 28. Cut List

These elements are intentionally cut.

### 28.1 No Day/Night Cycle

Cut.

Why:

Day/night would add lighting complexity and visual noise. The game is about collecting and decorating, not survival or time pressure.

### 28.2 No Weather

Cut.

Why:

Weather would affect visibility and pacing. The game should feel calm and stable.

### 28.3 No Parallax

Cut.

Why:

Parallax can make a top-down world harder to read. The world should feel like a clean diorama.

### 28.4 No Character Customization

Cut.

Why:

The player character is a fixed collector archetype. Customization would add UI and asset burden without improving the core fantasy.

### 28.5 No Heavy Particles

Cut.

Why:

Particles can become noisy. Use small, controlled effects only.

### 28.6 No Complex Facial Animation

Cut.

Why:

At small top-down sprite size, facial animation is not readable. Silhouette and posture are more important.

### 28.7 No Separate Level Music Files for Every Small Area

Cut.

Why:

Use one music loop per major zone. This keeps audio coherent and performance simple.

### 28.8 No Resource Nodes on Minimap

Cut.

Why:

Showing every node reduces exploration and clutters the minimap.

### 28.9 No Day/night Lighting for Furniture

Cut.

Why:

Furniture should have a fixed readable appearance. Dynamic lighting would make placement harder to evaluate.

### 28.10 No Scary or Aggressive Audio

Cut.

Why:

The game has no fail state and should never feel threatening.

---

## 29. Performance and Technical Visual Rules

### 29.1 Texture Atlases

Use atlases to reduce draw calls.

Suggested atlases:

- `atlas/world_1024x1024.png`
- `atlas/nodes_512x512.png`
- `atlas/characters_512x512.png`
- `atlas/furniture_1024x1024.png`
- `atlas/ui_1024x1024.png`

### 29.2 Animation Limits

- Character animations: max `8 FPS` for walk/idle.
- Water animation: max `8 FPS`.
- Particle effects: max `20` active particles.
- UI animations: max `300ms` duration.

### 29.3 Avoid Full-Screen Effects

Use localized effects:

- Small pop at resource.
- Small coin flight.
- Small display case glow.

Avoid:

- Full-screen flash.
- Full-screen shake.
- Full-screen color wash.
- Large particle bursts.

### Why

The game should feel calm and readable on lower-end browsers.

---

## 30. Acceptance Checklist

The final visuals should pass these checks.

### World

- [ ] The world is clearly 2D top-down.
- [ ] No visual implies vertical movement.
- [ ] All zones are distinct but coherent.
- [ ] Resource nodes are readable from a distance.
- [ ] Empty and full states are obvious.
- [ ] Ore charge states are obvious.
- [ ] Fish spots are readable without clutter.
- [ ] Perimeter is clearly impassable.
- [ ] Decorations do not hide interaction targets.

### Characters

- [ ] Player is readable against all terrain.
- [ ] Player walk animation is smooth.
- [ ] Player action states are distinct.
- [ ] Shopkeepers are visually distinct.
- [ ] Shopkeeper category is obvious.

### UI

- [ ] HUD is readable at a glance.
- [ ] Inventory is clear.
- [ ] Tool tiers are clear.
- [ ] Minimap is useful but not cluttered.
- [ ] Shop UI shows supply state clearly.
- [ ] Build mode valid/invalid states are obvious.
- [ ] Ledger is easy to navigate.
- [ ] Toasts are readable and not intrusive.
- [ ] All color states have non-color cues.

### Feedback

- [ ] Gathering shows progress.
- [ ] Selling shows coin feedback.
- [ ] Placing furniture shows clear ghost feedback.
- [ ] Museum curation feels rewarding.
- [ ] Goal completion feels meaningful.
- [ ] Final completion feels calm and ceremonial.

### Audio

- [ ] Music is calm and coherent.
- [ ] Zone music is distinct but related.
- [ ] SFX are short and satisfying.
- [ ] Invalid sounds are not annoying.
- [ ] Fishing sounds support the timing meter.
- [ ] Completion audio feels warm, not aggressive.

---

## 31. Final Visual Principle

The entire game should feel like this:

> A small, warm island where collecting is gentle, selling is satisfying, and the museum slowly becomes a place the player is proud of.

Every visual and audio decision should support that feeling.

If a feature feels:

- Loud.
- Harsh.
- Confusing.
- Distracting.
- Unnecessary.

Cut it.

The game should feel curated, not cluttered.