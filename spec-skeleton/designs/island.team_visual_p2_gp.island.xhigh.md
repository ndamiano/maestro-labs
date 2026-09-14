# visual.md

## 1. Integration Contract

This document defines the **visual dimensionality**, **art direction**, **UX**, **map readability**, **zone identity**, **music**, and **sound effects** for *Island of the Hidden Hoard*.

It is intended for handoff. The integrator should treat this file as the authoritative source for:

- how the world looks,
- how the map and HUD communicate state,
- how sectors stay distinct without breaking visual coherence,
- how music and audio support exploration,
- which visual/audio details are required for readability.

If this document conflicts with `gameplay.md`, gameplay mechanics and constants win. This document should not be used to change movement, tide formulas, puzzle logic, or progression.

### Readability priority

All visual and audio decisions follow this priority:

1. **Player can read tide depth.**
2. **Player can read elevation and cliff blocking.**
3. **Player can read caches, keys, landmarks, and vault state.**
4. **Player can read the map puzzle.**
5. **The island feels coherent, warm, and explorable.**
6. **Details decorate, but they never hide gameplay information.**

The game should feel like a bright, readable salvage chart, not a mysterious dark island.

---

## 2. Dimensionality and Projection

### 2.1 Chosen dimensionality

The game uses **2.5D isometric rendering**, matching the gameplay design.

This is not free 3D. It is a fixed isometric camera over a tile grid with height offsets and shadows.

### Why 2.5D is the right visual dimensionality

The core fantasy is **reading the island**. The player must understand:

- dry land,
- shallow water,
- deep water,
- elevation changes,
- cliff blocks,
- tide behavior,
- landmark positions,
- clue ring overlap.

A fixed isometric camera makes all of these easier to read than a free 3D camera. It also keeps browser performance stable and prevents camera navigation from becoming a distraction.

### 2.2 Projection constants

Use these as the default visual projection:

```text
TILE_W = 48 px
TILE_H = 24 px
HEIGHT_STEP = 18 px
```

One world tile is one meter. The visual tile is an isometric diamond.

Suggested screen mapping:

```js
const TAU = Math.PI * 2;
const ISO = {
  tileW: 48,
  tileH: 24,
  heightStep: 18,
};

function isoToScreen(tileX, tileY, elevation, camX, camY, viewW, viewH, scale = 1) {
  const sx = (tileX - tileY) * (ISO.tileW / 2) * scale;
  const sy = (tileX + tileY) * (ISO.tileH / 2) * scale - elevation * ISO.heightStep * scale;

  return {
    x: viewW / 2 + sx - camX,
    y: viewH / 2 + 24 + sy - camY,
  };
}
```

The camera should:

- follow the player,
- keep the player near center,
- clamp to the island bounds,
- not rotate,
- not allow free zoom,
- use a fixed 1.0 scale on standard screens,
- optionally scale to 0.85 on small screens for HUD safety.

### 2.3 Elevation rendering

Tiles with integer elevation 0 to 5 are rendered with vertical offset:

```text
screenY -= elevation * HEIGHT_STEP
```

Elevation differences are shown using:

- top tile height,
- side walls,
- drop shadows,
- edge highlights,
- terrain value ramp.

Rules:

- **Elevation difference 1:**  
  Render a small step or lip. This should look walkable.

- **Elevation difference 2 or more:**  
  Render a tall cliff face. This should look obviously non-walkable.

- **Cliff faces:**
  - use darker shading,
  - use vertical striations,
  - use a jagged top edge,
  - cast a soft shadow onto lower terrain,
  - never use the same edge language as a walkable step.

Do not rely only on height. A 2+ cliff must also read as blocked through shape and edge style.

### 2.4 Rendering order

Render the world in this general order:

1. Ocean background.
2. Terrain tiles sorted by `tileX + tileY`.
3. Terrain side walls.
4. Water overlays for flooded tiles.
5. Terrain details, props, caches, coins, landmarks.
6. Player.
7. World effects, such as wakes, dust, sparkles.
8. UI overlay.

Entities should cast simple elliptical shadows. Avoid expensive dynamic lighting.

---

## 3. Visual Identity

### 3.1 Art direction name

**Salt-light salvage chart**

The game should look like a hand-inked island chart that has been brought to life. It is sunny, nautical, slightly weathered, and clearly readable.

### 3.2 Style adjectives

The visual style should be:

- bright,
- clean,
- hand-painted,
- chunky,
- nautical,
- warm,
- readable,
- salvage-themed,
- slightly cartoonish but not childish.

The player is a careful salvager, not a combat explorer. The island should feel inviting, not hostile.

### 3.3 Core look

The island should have:

- warm sandy beaches,
- clear teal water,
- lush but readable jungle,
- sun-bleached stone ruins,
- rocky cliffs with strong silhouettes,
- brass, rope, wood, and salvage props,
- strong shadows that make elevation readable,
- simple animated water.

The overall lighting should feel like a warm midday. There is no day/night cycle.

### 3.4 What the style should avoid

Avoid:

- photorealism,
- dark horror tones,
- heavy fog,
- dynamic weather,
- complex particle systems,
- neon colors,
- cluttered micro-details,
- props that resemble coins, keys, or terrain too closely,
- UI that looks disconnected from the salvage theme,
- color-only communication for critical state.

---

## 4. Readability System

The most important visual system is state readability. The player must understand the island without reading a manual.

### 4.1 Readability hierarchy

Visual attention should be distributed in this order:

1. Current passability: dry, shallow, deep.
2. Player position and facing.
3. Nearby interactables: caches, vault, rope, column.
4. Landmarks.
5. Map clue rings.
6. Aesthetic decoration.

### 4.2 No color-only state

No critical state may rely on color alone.

Required redundancies:

- Tide state uses **color + icon + text**.
- Stamina uses **bar shape + icon + optional text**.
- Keys use **filled/hollow icon shape + count text**.
- Clue rings use **color + line style + key number**.
- Vault marker uses **shape + label + color**.
- Hunt areas use **dashed circle shape + orange color + icon**.
- Landmarks use **triangle base + unique glyph + label**.

### 4.3 Tide depth readability

The tide system is the main environmental pressure. It must be readable at a glance.

| Depth State | Condition | Visual Appearance |
|---|---:|---|
| Dry | `depth <= 0` | Full terrain color. No water overlay. |
| Shallow | `0 < depth <= 1.0` | Light translucent cyan/teal overlay. Gentle ripple. Terrain still clearly visible. |
| Deep | `depth > 1.0` | Darker blue overlay, more opaque. Stronger wave animation. Impassable. |

Visual rules:

- **Dry land** should always be the brightest and most readable state.
- **Shallow water** should look like knee-deep or shin-deep water, not dangerous.
- **Deep water** should look clearly different from shallow water:
  - darker,
  - more opaque,
  - slower-moving wave pattern,
  - less terrain detail visible.
- The shoreline should have a thin foam line where water meets dry land.
- When the player tries to enter deep water, show a short blocked movement animation and a soft audio thud. Do not show damage or death feedback.

### 4.4 Elevation readability

Elevation is read through height and edge style.

| Difference | Visual Rule |
|---:|---|
| 0 | Flat tile. |
| 1 | Small step lip. Light shadow. Walkable. |
| 2 or more | Tall cliff wall. Darker face. Jagged edge. Non-walkable. |

Elevation should also affect top tile value slightly:

- higher tiles are slightly lighter,
- lower tiles are slightly warmer or wetter,
- cliff tops are pale and rocky,
- low tide shelves are darker and wetter when exposed.

### 4.5 Interactable readability

Caches, the vault, ropes, and columns must be visually distinct from:

- coins,
- terrain,
- landmarks,
- decorative props.

When an interactable is within its visibility distance and has line of sight:

- show the prop with a short fade-in,
- add a soft golden outline pulse,
- show a context prompt at the bottom of the screen.

When an interactable is sealed:

- show a padlock icon above it,
- use a desaturated gray/brass state,
- prompt says exactly what is missing.

When an interactable is openable:

- use a brighter brass/gold state,
- show the prompt,
- show a channel progress ring while interacting.

---

## 5. Color System

Color is a communication system, not just decoration.

### 5.1 Global palette

| Use | Color | Hex | Notes |
|---|---|---:|---|
| Parchment UI | Warm paper | `#F3E4C2` | Map, panels, prompts |
| UI border | Dark wood | `#5B4632` | Panel edges |
| Brass | Salvage brass | `#D8A24B` | Keys, buttons, interactive trim |
| Ink | Dark text | `#201812` | UI text on parchment |
| Player | Pure white | `#FFFFFF` | Player arrow and player body outline |
| Shadow | Soft shadow | `rgba(16,24,36,0.25)` | Terrain and entity shadows |
| Ocean deep | Deep ocean | `#0B2C47` | Deep water and ocean border |
| Water mid | Sea blue | `#1D5F8E` | Mid-depth water |
| Shallow water | Pale teal | `#7FD9D2` | Passable shallow water |
| Foam | Salt foam | `#FFF6E4` | Shoreline and water edges |
| Sand | Warm sand | `#E7D0A5` | Beaches and dry lowland |
| Jungle floor | Leaf green | `#7DB26A` | Palm Hollow base |
| Rock | Mid rock | `#A89B8A` | Cliffs and ruins |
| Ruin stone | Bleached stone | `#CFC3AC` | Sunken Ruins |
| Cliff cap | Pale rock | `#D9D1BE` | Cliff tops |
| Key gold | Treasure gold | `#FFC845` | Keys, vault glow, positive completion |
| Coin gold | Slightly warmer gold | `#F2C14E` | Coins |
| Low tide | Cool teal | `#45E0C6` | Low tide state |
| Rising tide | Amber | `#FFD166` | Rising state |
| High tide | Orange | `#FF7A3D` | High tide warning and state |
| Vault marker | Signal red | `#E5484D` | Exact vault marker |
| Open vault | Gold | `#FFC845` | Vault ready/open |
| Hunt area | Salvage orange | `#FF9F43` | Map search areas |

### 5.2 Meaning of colors

Use color meaning consistently:

- **Gold/brass:** treasure, keys, positive progression, interactables.
- **Teal/cyan:** water, low tide, safe state, first clue ring.
- **Amber/orange:** tide warning, high tide, search area.
- **Red:** vault marker only. Do not use red for generic danger elsewhere.
- **Gray/hollow:** missing, sealed, unavailable.
- **White:** player, foam, neutral highlights.

### 5.3 Clue ring colors and line styles

Clue rings must be readable over terrain. Each geometric key gets a unique color and line style.

| Key | Landmark | Color | Line Style | Canvas Dash |
|---:|---|---|---|---:|
| 1 | Shipwreck | `#45E0C6` | Solid | `[]` |
| 2 | Gull Flats Lighthouse | `#9A7BFF` | Long dash | `[12, 8]` |
| 3 | Palm Hollow Idol | `#8ADB6A` | Short dash | `[4, 8]` |
| 4 | Sunken Arch | `#FF7AC0` | Dash-dot | `[14, 6, 4, 6]` |

The line style is required. Color alone is not enough.

---

## 6. Terrain, Water, and Tide Rendering

### 6.1 Terrain tile style

Terrain should use a simple painterly tile system.

Each tile top is an isometric diamond. Tiles should have:

- a base color,
- subtle noise,
- a thin dark edge,
- a light top-left highlight,
- sector-specific texture motifs.

Terrain details should be sparse. A tile should not be so detailed that it hides water depth or elevation.

Suggested terrain texture generation:

```js
function makeTileCanvas(seed, sector, elevation, wet) {
  const canvas = document.createElement("canvas");
  canvas.width = 64;
  canvas.height = 32;
  const ctx = canvas.getContext("2d");

  const sectorPalette = getSectorPalette(sector);
  const base = shade(sectorPalette.ground, elevation * 0.05);

  ctx.beginPath();
  ctx.moveTo(32, 0);
  ctx.lineTo(64, 16);
  ctx.lineTo(32, 32);
  ctx.lineTo(0, 16);
  ctx.closePath();

  ctx.fillStyle = base;
  ctx.fill();

  const rng = mulberry32(seed);
  for (let i = 0; i < 14; i++) {
    const x = 6 + rng() * 52;
    const y = 4 + rng() * 24;
    const alpha = 0.03 + rng() * 0.06;
    ctx.fillStyle = `rgba(0,0,0,${alpha})`;
    ctx.fillRect(x, y, 2, 2);
  }

  if (wet) {
    ctx.fillStyle = "rgba(18,68,94,0.16)";
    ctx.fill();
  }

  ctx.strokeStyle = "rgba(31,24,18,0.24)";
  ctx.lineWidth = 1;
  ctx.stroke();

  return canvas;
}
```

The integrator may improve texture quality, but the visual goal is a soft, hand-painted tile, not a crisp checkerboard.

### 6.2 Water overlay rendering

Water should be rendered as an overlay on top of terrain. It should not fully hide the terrain in shallow water.

Suggested water overlay function:

```js
function drawWaterOverlay(ctx, depth, time, tileX, tileY) {
  if (depth <= 0) return;

  const isDeep = depth > 1.0;
  const ripple = Math.sin(time * 3.2 + tileX * 0.4 + tileY * 0.3);
  const alpha = isDeep
    ? 0.66 + 0.05 * ripple
    : 0.28 + 0.08 * ripple;

  ctx.fillStyle = isDeep
    ? `rgba(12,47,74,${alpha})`
    : `rgba(127,217,210,${alpha})`;

  ctx.fill();

  if (!isDeep) {
    ctx.strokeStyle = `rgba(255,246,228,${0.18 + 0.10 * Math.sin(time * 4 + tileX + tileY)})`;
    ctx.lineWidth = 1;
    ctx.stroke();
  }
}
```

### 6.3 Shallow water look

Shallow water should look passable.

Visual traits:

- pale teal color,
- 30% to 40% alpha,
- slow ripple,
- terrain still visible underneath,
- player shows a small wake,
- coins appear slightly submerged but still recognizable.

### 6.4 Deep water look

Deep water should look impassable.

Visual traits:

- deep blue color,
- 65% to 75% alpha,
- stronger wave animation,
- terrain almost hidden,
- no foam line inside the deep area,
- blocked movement feedback when player tries to enter.

### 6.5 Low tide visual moment

At low tide, the island should feel exposed and rewarding.

Visual cues:

- shoreline foam recedes,
- exposed shelves show wet sand,
- low-tide coins become visible,
- the Gull Flats shelf becomes clearly dry,
- the vault cave floor is reachable,
- water in the map becomes lighter.

Add a subtle “tide line” on recently exposed sand: a thin darker band where water used to be. This helps the player understand that the tide has changed.

### 6.6 High tide visual moment

At high tide, the island should feel compressed but not threatening.

Visual cues:

- water color darkens,
- shallow areas become more opaque,
- elevation 0 tiles become deep water,
- elevation 1 tiles become shallow,
- the player is gently pushed to higher ground,
- the tide dial shows HIGH with a wave icon and orange color.

The visual tone should still be safe. The tide is a planning problem, not a monster.

---

## 7. Sectors: Distinct but Coherent

The six sectors must feel distinct, but they must not become unrelated art styles. All sectors share the same:

- palette system,
- tile language,
- prop silhouette style,
- shadow language,
- UI materials,
- water rendering,
- lighting.

Each sector gets:

- a local ground color,
- a local accent color,
- one or two signature motifs,
- one landmark,
- one cache prop,
- one short sector label for the map and banner.

### 7.1 Global sector consistency rule

A sector should be recognized by:

1. landmark silhouette,
2. local accent color,
3. terrain texture motif,
4. map label.

Do not make one sector look photoreal while another looks cartoonish. Do not introduce a unique lighting system per sector.

---

### 7.2 Driftwood Cove

**Role:** Start, tutorial, first key.

**Visual goal:** Safe, warm, easy to read.

**Palette:**

| Element | Color |
|---|---|
| Sand | `#E7D0A5` |
| Dune | `#D8BC88` |
| Driftwood | `#8A6E58` |
| Rope | `#D7B98C` |

**Motifs:**

- driftwood logs,
- loose planks,
- rope knots,
- sand ripples,
- gentle shoreline foam.

**Landmark: Shipwreck**

- broken wooden hull,
- tilted mast,
- visible anchor,
- weathered planks.

The shipwreck should have a strong silhouette visible from 24 tiles.

**Key 1 cache: Shipwreck barrel**

- wooden barrel,
- brass band,
- rope closure,
- openable lid.

This should be the first clearly interactable prop the player sees.

---

### 7.3 Gull Flats

**Role:** Low-tide teaching sector.

**Visual goal:** Open, wet, exposed, slightly empty.

**Palette:**

| Element | Color |
|---|---|
| Mudflat | `#C8B298` |
| Wet sand | `#DBC7A5` |
| Lighthouse white | `#F5F0E1` |
| Lighthouse band | `#2FA6A6` |
| Gull | `#F7F3E8` |

**Motifs:**

- flat mud,
- shallow tide pools,
- gull shadows,
- exposed rock shelf,
- sparse grass tufts.

**Landmark: Gull Flats Lighthouse**

- white tower,
- teal horizontal bands,
- small lantern,
- 2-tile base.

Do not use red on the lighthouse. Red is reserved for the vault marker.

**Key 2 cache: Low-tide rock shelf**

- flat stone platform,
- tide pool around it,
- rock hatch with brass edge,
- seaweed details.

At high tide, this shelf should be underwater and visually unavailable. At low tide, it becomes dry and clearly openable.

---

### 7.4 Palm Hollow

**Role:** Jungle interior and root interaction.

**Visual goal:** Dense but readable.

**Palette:**

| Element | Color |
|---|---|
| Jungle floor | `#7DB26A` |
| Palm leaf | `#3E8C5A` |
| Root | `#6B5A47` |
| Idol | `#6FCF97` |

**Motifs:**

- palm trees as billboards,
- root mats,
- fallen trunks,
- bright green floor patches,
- soft leaf shadows.

Palm trees should not block tile readability. They should be sparse enough that the player can always see terrain height and water depth.

**Landmark: Palm Hollow Idol**

- carved stone pedestal,
- jade-green face,
- simple mask shape,
- small moss details.

**Key 3 cache: Root gate**

- two thick roots blocking a 2-tile gap,
- rope tied to a root,
- root-wrapped chest behind the gap.

The rope should be the only clearly interactable element in the cluster.

---

### 7.5 Sunken Ruins

**Role:** Coastal ruins and stone movement puzzle.

**Visual goal:** Sun-bleached, broken, but bright.

**Palette:**

| Element | Color |
|---|---|
| Ruin stone | `#CFC3AC` |
| Moss | `#7AA96B` |
| Mosaic blue | `#3E7BB0` |
| Coral accent | `#E98A6D` |

**Motifs:**

- broken columns,
- cracked stone floors,
- faded mosaics,
- small coral accents,
- shallow water channels.

The ruins should look abandoned but not haunted.

**Landmark: Sunken Arch**

- broken stone arch,
- two pillar ends,
- missing center span,
- small mosaic detail.

**Key 4 cache: Movable stone column**

- large stone column,
- moss on base,
- brass tide-key emblem,
- open niche behind it.

The column should be visually heavy. The player should understand it is not a decoration.

---

### 7.6 Cliffpath Ridge

**Role:** High ground and final key.

**Visual goal:** Rocky, windy, exposed, earned.

**Palette:**

| Element | Color |
|---|---|
| Rock | `#A89B8A` |
| Cliff cap | `#D9D1BE` |
| Eagle | `#F2F2F2` |
| Wind accent | `#EAF6FF` |

**Motifs:**

- jagged rock,
- pale cliff tops,
- thin path ledges,
- wind streaks,
- small eagle silhouette.

Cliff edges must be clearly non-walkable where elevation jumps 2+.

**Landmark: Cliffpath Eagle Rock**

- tall jagged rock,
- white eagle perched on top,
- strong silhouette from distance.

**Key 5 cache: Eagle Rock alcove**

- stone chest in a rock alcove,
- brass keyhole,
- rope trim,
- small ledge.

This should feel like a reward for travel, not a hidden trap.

---

### 7.7 Vault Point

**Role:** Final vault and completion.

**Visual goal:** The payoff.

**Palette:**

| Element | Color |
|---|---|
| Reef | `#E98A6D` |
| Cave rock | `#5E6A72` |
| Treasure gold | `#FFC845` |
| Water | `#1D5F8E` |

**Motifs:**

- reef rocks,
- cave mouth,
- coral branches,
- wet stone,
- golden treasure glow.

**Landmark: Vault Point Reef**

- coral reef cluster,
- curved rock outcrop,
- small cave opening behind it.

**Vault:**

- circular stone and brass door,
- five key slots around the edge,
- central tide lock,
- golden glow when low tide and all keys are present,
- water swirl effect when sealed by tide.

The vault should be obvious once the clue ring reveals it. It should not be hidden behind decorative clutter.

---

## 8. World Props

### 8.1 Player

The player is a salvager.

Visual silhouette:

- human-shaped,
- oilskin coat,
- rope belt,
- small backpack,
- boots,
- white outline for readability.

The player should be distinct from props because it has:

- a body,
- a head,
- legs,
- movement animation.

Do not make the player look like a key, coin, or treasure chest.

Animations:

- idle,
- walk 4 directions,
- run 4 directions,
- swim 4 directions,
- interact/channel,
- blocked movement bump.

Movement feedback:

- dry walking: small dust puff,
- running: larger dust puff,
- shallow water: small wake,
- swimming: continuous wake,
- deep water blocked: short splash and shake.

### 8.2 Coins

Coins are small score items.

Visual specs:

- 10 to 14 px visual size,
- gold coin,
- simple spiral or star mark,
- rotates slowly,
- bounces lightly,
- emits a tiny sparkle when visible.

Coins must be smaller and lower to the ground than keys.

Coin collection animation:

- coin spins,
- small golden burst,
- coin flies to the bottom-right counter,
- counter number ticks up.

Coins should not be marked on the map. The map is for keys, landmarks, and the vault. Marking every coin would reduce puzzle clarity.

### 8.3 Tide Keys

Keys are progression items.

Visual specs:

- larger than coins,
- brass key with a teal tide emblem,
- clear key silhouette,
- floats slightly above the cache when visible,
- emits a soft golden pulse.

Key collection animation:

- key lifts from cache,
- spins once,
- flies to the top-left key counter,
- the corresponding slot fills with gold.

Each key should be visually the same base key. The sector association is shown by the map clue and key counter position, not by making each key a different color.

### 8.4 Caches

Caches are the physical key containers.

All caches share the same interaction language:

- clear prop silhouette,
- brass tide-key emblem,
- prompt when nearby,
- channel ring while interacting,
- open state remains open.

But each cache has a unique prop shape.

| Key | Cache | Shape Language |
|---:|---|---|
| 1 | Barrel | Wooden barrel with lid |
| 2 | Rock shelf | Flat stone hatch |
| 3 | Root chest | Root-wrapped chest |
| 4 | Column pedestal | Stone column blocking niche |
| 5 | Alcove chest | Stone chest in alcove |

Sealed state:

- padlock icon above prop,
- rope or stone seal,
- desaturated brass,
- prompt: “Sealed. Find the first Tide Key.”

Open state:

- lid, hatch, gate, or column moved,
- empty cache or opened chest,
- no key icon,
- maybe a small coin burst.

### 8.5 Landmarks

Landmarks are large world objects used by clue rings.

They should have:

- strong silhouettes,
- visible from 24 tiles,
- unique shape,
- unique map glyph,
- a short name.

When discovered:

- brief golden outline in world,
- map stamp sound,
- landmark appears on map with triangle icon and glyph,
- if it is a sector landmark, show sector banner.

After discovery, show a small brass pin above the landmark in the world. This helps the player connect the map icon to the physical object.

| Landmark | World Silhouette | Map Glyph |
|---|---|---|
| Shipwreck | Broken hull and mast | Anchor |
| Gull Flats Lighthouse | Tall tower with bands | Vertical tower |
| Palm Hollow Idol | Pedestal with mask | Mask circle |
| Sunken Arch | Broken arch | Arch shape |
| Cliffpath Eagle Rock | Jagged rock with eagle | V-shaped eagle |
| Vault Point Reef | Coral and cave mouth | Coral branch |

### 8.6 Vault

The vault is the final interactable.

It should look like a heavy sea-cave door, not a chest.

States:

| Condition | Visual State |
|---|---|
| Fewer than 5 keys | Door has 5 hollow key slots. Gray/brass. |
| 5 keys, not low tide | Door is partially submerged or blocked by water swirl. Wave icon visible. |
| 5 keys, low tide | Door glows gold. Key slots fill. Tide lock opens. |
| Opening | Heavy door swings or slides open. Light spills out. |
| Open | Treasure visible inside. Golden compass rises. |

The vault should be visually distinct from all caches. Caches are small salvage props. The vault is a large architectural door.

---

## 9. Map Overlay

The map is the main puzzle tool. It must be bright, readable, and clearly chart-like.

### 9.1 Map canvas

- Maximum size: `512 x 512 px`.
- 1 tile = 2 px.
- Scales down for smaller screens.
- Uses parchment background.
- Has a thin wooden/brass border.

Map coordinate mapping:

```js
function tileToMap(tileX, tileY, scale = 2) {
  return {
    x: tileX * scale,
    y: tileY * scale,
  };
}
```

### 9.2 Map layers

Render map layers in this order:

1. Parchment background.
2. Revealed terrain.
3. Unrevealed dark overlay.
4. Current tide water.
5. High-tide flood preview.
6. Sector labels.
7. Hunt areas.
8. Clue rings.
9. Landmarks.
10. Vault marker.
11. Player.
12. Legend.

### 9.3 Revealed terrain

Revealed terrain should use a simplified sector color map, not full world detail.

Suggested map terrain colors:

| Terrain | Map Color |
|---|---|
| Beach / lowland | `#E7D0A5` |
| Jungle floor | `#7DB26A` |
| Rock / ruin | `#A89B8A` |
| Cliff top | `#D9D1BE` |
| Cave / low shelf | `#C9B48F` |

Unrevealed areas should be dark indigo with subtle diagonal hatching:

```text
Unrevealed overlay: rgba(16, 24, 40, 0.82)
Hatch: rgba(255, 255, 255, 0.04)
```

### 9.4 Current tide water on map

The map should show current tide water.

For each revealed tile:

```js
const depth = Math.max(0, waterLevel - tile.elevation);

if (depth > 0) {
  const isDeep = depth > 1.0;
  const alpha = isDeep ? 0.72 : 0.38;
  const color = isDeep ? "rgba(11,44,71,1)" : "rgba(127,217,210,1)";
  // draw with alpha
}
```

This helps the player understand where they can currently be.

### 9.5 High-tide flood preview

Show a faint preview of areas that become deep water at high tide.

Visual:

- elevation 0 revealed tiles,
- light blue dashed hatch,
- alpha 0.25,
- label in legend: “Floods at high tide”.

This is important because the tide is the main planning system. The player should be able to see where high tide will push them.

### 9.6 Landmark icons

Landmarks use triangle icons with unique glyphs.

Specs:

- triangle size: 10 to 12 px,
- parchment border,
- dark ink glyph,
- label below icon when space allows.

Do not rely on color. Each landmark has a glyph and label.

### 9.7 Hunt areas

Hunt areas show where uncollected caches may be.

Visual specs:

- orange dashed circle,
- radius: 24 tiles,
- fill: `rgba(255,159,67,0.12)`,
- stroke: `#FF9F43`,
- dash: `[10, 8]`,
- small question mark or cache icon at center.

When a hunt area is revealed:

- circle draws outward,
- soft orange pulse,
- map audio cue.

### 9.8 Clue rings

Clue rings are the core puzzle visual.

Each clue ring is an annulus centered on a landmark.

```text
inner radius = D - 6
outer radius = D + 6
```

Visual specs:

- fill alpha: 0.16,
- stroke width: 3 px,
- use key-specific color and dash style,
- animate ring drawing when added.

Suggested code:

```js
function drawClueRing(ctx, landmark, D, scale, style) {
  const p = tileToMap(landmark.x, landmark.y, scale);
  const rOuter = (D + 6) * scale;
  const rInner = Math.max(0, D - 6) * scale;

  ctx.save();

  ctx.fillStyle = style.fill;
  ctx.strokeStyle = style.color;
  ctx.lineWidth = 3;
  ctx.setLineDash(style.dash);

  ctx.beginPath();
  ctx.arc(p.x, p.y, rOuter, 0, TAU);
  ctx.arc(p.x, p.y, rInner, 0, TAU, true);
  ctx.fill("evenodd");
  ctx.stroke();

  ctx.restore();
}
```

Clue ring style table:

| Key | Color | Fill | Dash |
|---:|---|---|---|
| 1 | `#45E0C6` | `rgba(69,224,198,0.16)` | `[]` |
| 2 | `#9A7BFF` | `rgba(154,123,255,0.16)` | `[12, 8]` |
| 3 | `#8ADB6A` | `rgba(138,219,106,0.16)` | `[4, 8]` |
| 4 | `#FF7AC0` | `rgba(255,122,192,0.16)` | `[14, 6, 4, 6]` |

When a new clue is added:

- the corresponding ring draws from center outward,
- a small key icon flies from the cache to the map,
- the map shows a brief “Clue added” text if the player has the map open.

### 9.9 Vault marker

Once four geometric clues are collected, show the exact vault marker.

Visual:

- red X,
- two thick diagonal strokes,
- pulse scale from 1.0 to 1.12,
- label: `VAULT`,
- color: `#E5484D`.

This marker must be obvious. It should not be confused with a clue ring or hunt area.

When the vault is ready:

- X changes to gold,
- add compass icon next to X,
- label: `OPEN`,
- color: `#FFC845`.

### 9.10 Player marker

Player marker:

- white arrow,
- black outline,
- points in movement direction,
- small pulse when idle.

### 9.11 Map legend

The map should include a compact legend in the bottom-left corner.

Legend items:

| Icon | Label |
|---|---|
| White arrow | Player |
| Triangle with anchor | Landmark |
| Orange dashed circle | Hunt area |
| Colored ring | Clue ring |
| Red X | Vault |
| Blue hatch | Floods at high tide |

The legend should be readable at map scale. Use 10 px UI text minimum.

### 9.12 Map transition

Opening map:

- parchment unfurls from top to bottom,
- slight scale-up,
- duration: 0.22s,
- sound: soft paper swish.

Closing map:

- parchment folds back,
- duration: 0.18s,
- sound: soft paper settle.

The map should be 92% opaque. A thin 8% world visibility is acceptable, but the map must not obscure tide warnings.

---

## 10. HUD and UX

### 10.1 UI style

UI should look like a salvager’s chart table.

Materials:

- parchment panels,
- dark wood borders,
- brass rivets,
- rope trim on important buttons,
- clean modern icons inside the panels.

The UI should not be skeuomorphic to the point of hurting readability. Panels should be crisp and bright.

### 10.2 Typography

Display font:

```text
"Squada One", "Arial Black", sans-serif
```

UI font:

```text
"Nunito Sans", "Trebuchet MS", system-ui, sans-serif
```

Rules:

- Titles: uppercase, bold, slightly spaced.
- HUD labels: short uppercase.
- Prompts: sentence case, clear.
- Objective: one line where possible.
- Map labels: short, uppercase, 10 px minimum.

Text color:

- on parchment: `#201812`,
- on dark water: `#FFF6E4` with dark outline,
- on gold: `#201812`.

Contrast must be at least 4.5:1 for critical text.

### 10.3 Start screen

A short start screen is required for UX and browser audio initialization.

Content:

- title: `Island of the Hidden Hoard`
- subtitle: `A tide-locked salvage hunt`
- controls:
  - WASD / Arrows: Move
  - Shift: Run
  - E: Interact
  - M / Right Mouse: Map
- button: `Begin Salvage`

Visual:

- parchment panel over a simplified island silhouette,
- gentle water animation in background,
- soft sea audio after user interaction.

Reason: browser audio requires a user gesture. The start button should initialize audio.

### 10.4 Persistent HUD layout

#### Top left

1. **Tide Dial**
   - 72 x 72 px circular gauge.
   - Shows water level from 0 to 2.
   - Shows text state:
     - `LOW`
     - `RISING`
     - `HIGH`
   - Shows seconds until next threshold.
   - Uses icon + text + color.

Tide dial icons:

| State | Icon |
|---|---|
| LOW | Down arrow with empty wave |
| RISING | Up arrow with half wave |
| HIGH | Double wave |

2. **Stamina Bar**
   - 120 x 12 px horizontal bar.
   - Left icon: boot or foot.
   - Fill color: `#6FCF97`.
   - Empty state: gray diagonal stripes.
   - When stamina is 0, show `WALK` text or grayed boot icon.

3. **Key Counter**
   - 5 key icon slots.
   - Filled: gold key.
   - Missing: hollow gray key.
   - Text: `1/5`, `2/5`, etc.

#### Top right

1. **Map Button**
   - 64 x 64 px.
   - Scroll/map icon.
   - Contains a small map preview.
   - Hover: brass glow.
   - Hold M or right mouse to open.

2. **Objective Text**
   - One-line parchment strip.
   - Max width: 220 px.
   - If text is long, allow two lines only.
   - Updates from gameplay states.

#### Bottom right

1. **Coin Counter**
   - Coin icon.
   - Text: `X / 160`.
   - Brief golden pulse on collect.

#### Bottom center

1. **Context Prompt**
   - 260 x 52 px parchment pill.
   - Shows `[E]` icon.
   - Shows prompt text.
   - Shows channel progress while interacting.

### 10.5 Context prompt states

| State | Prompt Visual |
|---|---|
| Cache sealed | Padlock icon, gray prompt |
| Cache openable | Brass `[E]` icon, gold outline |
| Channeling | Circular progress ring fills |
| Channel cancelled | Ring breaks, prompt flashes gray |
| Vault locked by keys | Five hollow key icons |
| Vault sealed by tide | Wave icon, blue/orange prompt |
| Vault openable | Gold key icons, glowing prompt |

### 10.6 Channel progress

Interactions require standing still. The player must see progress.

Visual:

- circular ring around the `[E]` icon in the prompt,
- same ring appears around the prop in world,
- ring fills clockwise,
- uses brass color `#D8A24B`,
- complete state: short golden burst.

Cancellation:

- moving,
- opening map,
- safe displacement,
- tide no longer low for vault.

On cancel:

- ring breaks into two arcs,
- prompt text changes to `Cancelled`,
- soft cancel sound.

### 10.7 Tide warning UX

The tide warning must be readable but not panic-inducing.

When 10 seconds remain before crossing into Rising or High:

- top-center warning banner appears,
- tide dial pulses,
- warning sound plays once,
- text uses icon + text.

Examples:

- `Tide rising in 10s`
- `High tide in 10s`
- `Low tide in 10s`

Use:

- rising: up arrow,
- high: double wave,
- low: down arrow.

Do not use flashing full-screen effects.

### 10.8 Sector discovery banner

When a sector is first discovered:

- top-center banner shows for 2 seconds,
- sector icon plus name,
- parchment background,
- soft stamp sound.

Examples:

- `Driftwood Cove`
- `Gull Flats`
- `Palm Hollow`
- `Sunken Ruins`
- `Cliffpath Ridge`
- `Vault Point`

This helps the player feel oriented without requiring a tutorial.

### 10.9 End screen

The end screen is a salvage certificate.

Content:

- `Treasure Found`
- rank,
- time,
- coins,
- keys,
- optional restart button.

Rank visuals:

| Rank | Icon |
|---|---|
| Beachcomber | Small shovel |
| Salvager | Brass hook |
| Master Salvager | Golden key |
| Tide Baron | Anchor crown |

Visual:

- parchment certificate,
- brass border,
- golden compass in center,
- soft fanfare,
- gull cry,
- confetti limited to small gold and foam pieces.

Do not use excessive celebration. The ending should feel like a clean salvage success.

---

## 11. Camera, Motion, and Animation

### 11.1 Camera

The camera is fixed isometric.

Rules:

- follow player with slight smoothing,
- no rotation,
- no player-controlled zoom,
- clamp to island,
- show enough terrain to read upcoming cliffs and water.

Use a small dead zone around the player so the camera does not jitter when the player idles.

### 11.2 Motion feel

The game should feel calm but alive.

Important motions:

- water ripple,
- foam movement,
- coin rotation,
- key pulse,
- landmark discovery pulse,
- map ring draw,
- vault glow,
- player walk/run/swim.

All animations should be short and readable. Avoid:

- fast flashing,
- large screen shake,
- particle bursts that obscure the player,
- camera moves that make the player lose orientation.

### 11.3 Key collection animation

When a key is collected:

1. Key lifts from cache.
2. Key spins once.
3. Key flies to top-left key counter.
4. Key slot fills with gold.
5. If geometric clue, clue ring appears on map.
6. Soft brass chime plays.

### 11.4 Coin collection animation

When a coin is collected:

1. Coin spins.
2. Tiny golden burst.
3. Coin flies to bottom-right counter.
4. Counter number increments.
5. Small metallic ping plays.

### 11.5 Safe displacement animation

If the player is displaced by tide:

1. Show a soft ripple at the original position.
2. Player moves to safe tile.
3. Show a small splash at destination.
4. Prompt or banner: `Tide pushed you` if needed.
5. Whoosh and splash sound.

Do not make this look like damage.

### 11.6 Vault opening animation

When the vault opens:

1. Door glows gold.
2. Tide lock rotates.
3. Heavy door slides or swings open.
4. Water drains from cave mouth.
5. Golden light spills out.
6. Treasure burst.
7. Golden compass rises.
8. Game complete stinger plays.
9. Fade to end screen.

---

## 12. Music

### 12.1 Music identity

The music should support a calm, sunny salvage hunt.

Style:

- ambient island,
- light marimba,
- celesta,
- muted guitar,
- soft percussion,
- sea noise,
- occasional brass or bell.

The music should never feel like a boss fight. The only “danger” is the tide, and the tide is a planning tool.

### 12.2 Musical key and mood

Use **D major pentatonic** as the base scale:

```text
D, E, F#, A, B
```

Base tempo:

```text
84 BPM
```

This tempo feels relaxed but active enough for exploration.

### 12.3 Music layers

Use adaptive layers rather than separate full tracks.

| Layer | Instrument / Sound | Level | Purpose |
|---|---|---:|---|
| Sea bed | Filtered noise + low sine | -18 dB | Constant ocean presence |
| Percussion | Wood block, shaker, soft kick | -16 dB | Exploration rhythm |
| Melody | Marimba, celesta, muted guitar | -12 dB | Main exploration music |
| Tide accent | Water wash, low swell | -14 dB | Communicate tide state |
| Stinger | Brass/marimba motif | -6 dB | Key, vault, completion events |

### 12.4 Adaptive music rules

| Game State | Music Change |
|---|---|
| Start screen | Sea bed + distant gull + very soft melody |
| Exploration on dry land | Full percussion + melody |
| Shallow water | Percussion reduces by 30%, water wash increases |
| Deep water blocked | Music ducks, water louder, low swell added |
| Low tide | Add bright celesta ostinato |
| Rising tide | Add soft water swells |
| High tide | Add low marimba pulse and slightly slower feeling |
| Key collected | Short 3-note brass/marimba stinger |
| Sector discovered | 2-note sector motif |
| Vault ready | Slow bell pulse at 60 BPM for about 10 seconds |
| Vault opening | Heavy bell + marimba hit |
| Game complete | 2-second light fanfare + gull cry |

### 12.5 Sector motifs

When a sector is discovered, play a short two-note motif. This keeps sectors distinct without changing the full music.

| Sector | Motif Notes |
|---|---|
| Driftwood Cove | D then A |
| Gull Flats | F# then B |
| Palm Hollow | A then B |
| Sunken Ruins | Low D then F# |
| Cliffpath Ridge | High B then A |
| Vault Point | D then B with bell |

These motifs should be very short, under 1 second.

### 12.6 Music mixing

Target mixing:

| Source | Level |
|---|---:|
| Music | -12 dB |
| SFX | -6 dB |
| UI | -10 dB |
| Water loop | -14 dB |
| Stingers | -6 dB |

Rules:

- duck music by 3 dB when important SFX play,
- keep SFX clearer than music,
- do not let water overpower key collection or vault sounds,
- pan world SFX slightly by screen position,
- keep UI and tide dial sounds centered.

---

## 13. Sound Effects

Sound effects should reinforce readability. The player should be able to understand all important events visually, but audio should make the island feel alive.

### 13.1 SFX priority

Priority order:

1. Key collected
2. Vault opening / complete
3. Tide warning / state change
4. Cache interaction
5. Coin collected
6. Movement and water
7. UI sounds

Max simultaneous SFX: 8.

### 13.2 Required SFX table

| Event | Sound Description | Duration | Character | Visual Counterpart |
|---|---|---:|---|---|
| `key_collected` | Bright brass key chime | 0.6s | Triangle/sine sweep, 660 to 990 Hz | Key flies to counter |
| `coin_collected` | Small gold ping | 0.12s | Square/triangle, 1200 to 1800 Hz, slight random pitch | Coin flies to counter |
| `cache_sealed_prompt` | Low padlock thunk | 0.35s | Low 120 Hz + metallic click | Padlock icon appears |
| `cache_opened` | Creak, clunk, or grind | 0.5 to 1.5s | Depends on prop | Cache opens |
| `rope_pulled` | Rope creak + wood ratchet | 1.0s | Filtered sawtooth + click | Gate opens |
| `column_moved` | Stone grind + low rumble | 1.5s | Low noise + lowpass | Column slides |
| `tide_warning` | Two soft water gongs | 0.8s | Low gong, short echo | Warning banner |
| `low_tide_reached` | Descending swell + bright chime | 0.7s | Water noise down + high chime | Dial shows LOW |
| `high_tide_reached` | Rising swell + low gong | 0.7s | Water noise up + low gong | Dial shows HIGH |
| `vault_locked` | Heavy brass lock | 0.5s | Low metallic thud | Vault key slots hollow |
| `vault_opening` | Stone door + brass bell + water drain | 1.2s | Low rumble + bell | Vault opens |
| `game_complete` | Light fanfare + gull cry | 2.0s | Brass/marimba + gull | End screen |
| `landmark_discovered` | Map stamp + soft chime | 0.4s | Paper stamp + small bell | Landmark appears on map |
| `clue_added` | Compass tick + chart paper | 0.5s | Tick + soft swish | Clue ring draws |
| `safe_displacement` | Whoosh + splash | 0.4s | Air sweep + water burst | Player moves safely |
| `footstep_dry` | Soft thud / sand crunch | 0.08s | Lowpass noise | Dust puff |
| `footstep_shallow` | Short slosh | 0.1s | Filtered noise | Wake |
| `swim_loop` | Continuous water loop | looping | Lowpass water | Player swims |
| `ui_hover` | Soft tick | 0.05s | High sine blip | Button highlight |
| `ui_click` | Brass clack | 0.08s | Short filtered square | Button press |
| `map_open` | Parchment swish | 0.2s | Noise sweep | Map opens |
| `map_close` | Parchment settle | 0.18s | Noise sweep down | Map closes |

### 13.3 SFX design rules

- Key sounds should be bright and unmistakable.
- Coin sounds should be small and frequent, not annoying.
- Tide sounds should feel watery, not alarm-like.
- Vault sounds should feel heavy and ceremonial.
- Interaction sounds should match the material:
  - rope: creak,
  - stone: grind,
  - wood: creak/clunk,
  - brass: chime.
- All sounds should have quick attack and clean decay.
- Avoid sharp noise peaks. Browser audio should remain pleasant at high volume.

### 13.4 Suggested SFX synthesis

This is a small example for key, coin, stone, and tide sounds. The integrator can replace these with recorded assets, but the sonic shape should match.

```js
function playSfx(audioCtx, name) {
  const t = audioCtx.currentTime;
  const gain = audioCtx.createGain();
  gain.connect(audioCtx.destination);

  if (name === "key") {
    const osc = audioCtx.createOscillator();
    const filter = audioCtx.createBiquadFilter();

    osc.type = "triangle";
    osc.frequency.setValueAtTime(660, t);
    osc.frequency.linearRampToValueAtTime(990, t + 0.15);

    filter.type = "lowpass";
    filter.frequency.value = 4000;

    osc.connect(filter);
    filter.connect(gain);

    gain.gain.setValueAtTime(0.35, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.6);

    osc.start(t);
    osc.stop(t + 0.65);
  }

  if (name === "coin") {
    const osc = audioCtx.createOscillator();
    osc.type = "square";
    osc.frequency.value = 1400 + Math.random() * 500;

    const filter = audioCtx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 3000;

    osc.connect(filter);
    filter.connect(gain);

    gain.gain.setValueAtTime(0.18, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.12);

    osc.start(t);
    osc.stop(t + 0.14);
  }

  if (name === "stone") {
    const bufferSize = audioCtx.sampleRate * 1.5;
    const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
    const data = buffer.getChannelData(0);

    for (let i = 0; i < bufferSize; i++) {
      data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (audioCtx.sampleRate * 0.5));
    }

    const source = audioCtx.createBufferSource();
    source.buffer = buffer;

    const filter = audioCtx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.setValueAtTime(800, t);
    filter.frequency.exponentialRampToValueAtTime(120, t + 1.4);

    source.connect(filter);
    filter.connect(gain);

    gain.gain.setValueAtTime(0.25, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 1.5);

    source.start(t);
    source.stop(t + 1.5);
  }

  if (name === "tide") {
    const osc = audioCtx.createOscillator();
    osc.type = "sine";
    osc.frequency.value = 180;

    const filter = audioCtx.createBiquadFilter();
    filter.type = "lowpass";
    filter.frequency.value = 900;

    osc.connect(filter);
    filter.connect(gain);

    gain.gain.setValueAtTime(0.22, t);
    gain.gain.exponentialRampToValueAtTime(0.001, t + 0.8);

    osc.start(t);
    osc.stop(t + 0.85);
  }
}
```

For a full production version, use layered noise for water and short filtered sine/triangle tones for UI and keys.

---

## 14. Asset and Performance Notes

### 14.1 Asset categories

The integrator should expect these asset categories:

#### Terrain

- base tiles per sector,
- elevation variants,
- wet variants,
- shallow water overlay,
- deep water overlay,
- foam edge,
- side wall textures,
- cliff face textures.

#### Props

- shipwreck,
- barrel,
- lighthouse,
- rock shelf,
- palm trees,
- idol,
- root gate,
- ruins,
- arch,
- column,
- eagle rock,
- reef,
- vault,
- coins,
- keys.

#### UI

- tide dial,
- stamina bar,
- key counter,
- coin counter,
- map button,
- map overlay,
- context prompt,
- channel ring,
- warning banner,
- sector banner,
- start screen,
- end screen.

#### Audio

- sea loop,
- music layers,
- SFX one-shots,
- stingers,
- UI sounds.

### 14.2 Performance budget

Target:

- 60 FPS on mid-range browser hardware,
- no full-screen blur,
- no dynamic lighting,
- no expensive post-processing,
- no free 3D navigation,
- limited particle count.

Recommended:

- pre-render terrain tiles into offscreen canvases,
- animate water with simple alpha overlay,
- use culling for tiles outside view,
- limit visible dynamic tiles to the camera area,
- keep map updates efficient by redrawing only changed layers,
- limit SFX nodes to 8 active at once,
- use one sea noise loop instead of many water sounds.

### 14.3 Small screen support

Minimum comfortable screen:

```text
800 x 480
```

On smaller screens:

- scale HUD to 0.85,
- keep tide dial and map button accessible,
- keep context prompt within safe area,
- reduce map preview size,
- do not hide objective text.

---

## 15. Cuts and Non-Goals

The following are intentionally cut:

| Cut | Reason |
|---|---|
| Dynamic lighting | Not needed; tide and elevation are the visual focus. |
| Day/night cycle | Already cut by gameplay; would add complexity without puzzle value. |
| Weather effects | Tide is the only dynamic environmental pressure. |
| Full 3D models | 2.5D isometric is clearer and cheaper. |
| Complex particles | Small dust/wake/sparkle is enough. |
| Sector-specific full music tracks | Adaptive layers are more coherent and cheaper. |
| Voice | Not needed for a short puzzle-exploration session. |
| Coin markers on map | Would clutter the map. Map is for keys and vault. |
| In-game volume sliders | Single-session browser game; browser volume is enough. |
| Enemy danger visuals | No combat. Danger is tide only. |
| Death feedback | No health or death. |
| Complex inventory UI | Keys and coins are automatic. |

---

## 16. Integration Checklist

Before the game is considered visually complete, verify:

### World readability

- [ ] Dry land is clearly different from shallow water.
- [ ] Shallow water is clearly different from deep water.
- [ ] Elevation difference of 1 looks walkable.
- [ ] Elevation difference of 2+ looks non-walkable.
- [ ] Cliff edges are visually obvious.
- [ ] The player can always tell which tiles are currently passable.

### Prop readability

- [ ] Caches are distinct from coins, terrain, and landmarks.
- [ ] Sealed caches show a clear padlock state.
- [ ] Open caches remain open.
- [ ] The vault is visually distinct from all caches.
- [ ] Vault state clearly shows locked by keys, sealed by tide, or openable.

### Map readability

- [ ] Map shows current water level.
- [ ] Map shows high-tide flood preview.
- [ ] Hunt areas are visible and distinct.
- [ ] Clue rings use both color and line style.
- [ ] Vault marker is obvious and labeled.
- [ ] Landmark icons do not rely on color alone.
- [ ] Player marker is visible.
- [ ] Legend is present.

### HUD readability

- [ ] Tide dial uses shape, text, and color.
- [ ] Stamina uses bar shape and icon.
- [ ] Key counter shows filled and hollow keys.
- [ ] Coin counter is visible.
- [ ] Objective text is always readable.
- [ ] Context prompt shows the current interaction.
- [ ] Channel progress is visible in prompt and world.
- [ ] Tide warnings are readable before high tide.

### Audio

- [ ] Key collection is bright and unmistakable.
- [ ] Coin collection is small and satisfying.
- [ ] Tide warning is distinct from state change.
- [ ] Low tide and high tide sounds are distinct.
- [ ] Vault opening sounds heavy and ceremonial.
- [ ] Music supports exploration without becoming stressful.
- [ ] All audio events have visual counterparts.

### Overall feel

- [ ] The game feels like one coherent island, not six disconnected levels.
- [ ] Sectors are recognizable but share the same visual language.
- [ ] The player rarely needs to read long text to understand state.
- [ ] The final vault feels like a timed ritual, not a boss fight.
- [ ] The ending feels like a clean salvage success.