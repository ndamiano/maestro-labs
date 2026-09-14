# 1. THE LOOK IN ONE PARAGRAPH

2D, side-scrolling camera (horizontal follow, no rotation, fixed zoom). The game is a neon-soaked post-industrial wasteland: a lone scavenger in a battered exo-suit blasts through the skeletal remains of a drowned mega-city. The palette is deep oxidized teal (#1A2E33) and rust-orange (#C45A2D) as the ground truth, punctuated by electric cyan (#00E5FF) and hot magenta (#FF2D78) from gunfire, signage, and bioluminescence. The mood is "gritty Saturday-morning cartoon"—chunky readable shapes, bold outlines, and exaggerated squash-and-stretch on every impact. The screenshot that sells it: the player mid-air, crouching-then-jumping off a rusted conveyor belt, magenta plasma bolt streaking right, a two-story enemy robot reeling with a cyan hit-flash, parallax layers of dripping pipes and flickering neon signs visible in the background, all rendered in thick 3-pixel black outlines over flat saturated fills.

# 2. THE SPACE

**Coordinate system:** 1 unit = 1 game-pixel at base resolution (960×540 viewport). The player stands 3 units tall, 2 units wide. Tiles are 1×1 unit. A stage is a horizontal corridor 240 units wide × 24 units tall (20 visible, 4 of dead air above).

**Stage layout (per stage, left → right):**

| Region | Width (units) | Contents | Visual tell |
|---|---|---|---|
| Spawn ledge | 0–12 | Flat ground, a single flickering lamp post, the "start" banner | Warm sodium glow (#FFB347) pools on the floor |
| Mid traversal | 12–160 | Platforms, pits, enemy spawns, pickups, environmental hazards (steam vents, conveyor belts, electrified water) | Background parallax shifts; ground texture changes every 40 units |
| Checkpoint shrine | at 80, 120, 160 (some stages) | A glowing totem the player touches to save | Pulsing cyan ring, hum particles |
| Arena / boss room | 160–220 | Enclosed space, 3 layers of platforms, boss spawn pad | Lighting drops to 60%, single overhead spotlight, walls close in (ceilings lower to 16 units) |
| Exit gate | 220–240 | A massive shutter door with a stage-number stencil, confetti cannons | Magenta (#FF2D78) rim-light on the door frame |

**World 1 – "The Rustbelt":** Ground is corrugated steel plates and broken concrete. Backgrounds show smokestacks, hanging chains, conveyor machinery. Palette skews rust-orange dominant. Stage 5 is the boss arena: a giant hydraulic press room, ceiling at 20 units, floor is a grate over boiling oil.

**World 2 – "The Undercity":** Ground is cracked tile and flooded shallow channels (1 unit deep, ankle-high). Backgrounds show dripping brick arches, subway tunnels, bioluminescent moss. Palette skews deep teal dominant with magenta/cyan fungi pops. Stage 5 boss arena: a drained reservoir with concentric ring platforms.

**Stage progression visual cue:** Each stage number (1–5) adds one more background parallax layer and one more colour accent. Stage 1: 2 layers, 2 accents. Stage 5: 4 layers, 4 accents. The player should feel the world "filling in" as they advance.

**Generated vs. hand-placed:** Stage geometry is hand-placed (fixed platform layouts per stage). Enemy spawn positions and pickup locations are hand-placed. A "good roll" for the verifier: the player can always reach the exit gate via a continuous chain of platforms no wider than 6-unit gaps and no higher than 4-unit steps. A "bad roll": a gap wider than 7 units with no intermediate platform, or a required jump above 5 units with no crouch-jump assist ledge.

# 3. RECIPES

| Name | Shapes & Size (units) | Colours (hex) | Count | Motion / Effect |
|---|---|---|---|---|
| **Player – idle** | Rounded rect body 2×3, circle head r=0.7 atop, 2 stub arms, 2 stub legs. 3px black outline. | Suit: #2C3E50 (dark steel). Visor: #00E5FF. Accents: #FF2D78. | 1 | 2-frame breathing bob (y ±0.05, 0.8s cycle) |
| **Player – crouch** | Squashed rect 2×1.8, head tucks into shoulders. | Same | 1 | None (static pose) |
| **Player – run** | Same body, legs alternate 4-frame stride (y ±0.1 bounce). | Same | 1 | Leg cycle at stride frequency; dust puffs (#8B7355, r=0.3, fade 0.3s) at feet |
| **Player – jump** | Body stretched vertically 1.8×3.6, arms up. | Same | 1 | Launch squash → stretch → return. Trail: 3 ghost copies at 40% alpha, 0.1s apart |
| **Player – hurt** | Same body, tinted #FF2D78 at 70% opacity, 3-frame flash. | Flash: #FF2D78 → white → back | 1 | 0.15s per frame, knockback wobble (x ±0.2) |
| **Player – death** | Body shatters into 8 triangle shards (r=0.4 each), fly outward. | Shards: #2C3E50 with #FF2D78 edges | 1 | Shards spin and fade over 1.2s |
| **Gun – Rivet Driver (default)** | Rect barrel 1.5×0.4, circle muzzle r=0.25. | Body: #5C6B73. Muzzle ring: #FFB347. | 1 | Recoil: barrel x-offset −0.3 for 0.08s |
| **Rivet Driver – projectile** | Small circle r=0.15, trailing line 0.5. | Core: #FFB347. Trail: #FFB347→transparent. | On-screen max 12 | Linear, no arc. Fades at 40-unit range |
| **Gun – Scatter Cannon (shotgun)** | Wide rect barrel 1.2×0.7, 3 muzzle ports r=0.12 each. | Body: #8B4513 (leather grip). Ports: #FF2D78. | 1 | Muzzle flash: 3 radial lines 0.8 long, #FF2D78, 0.06s |
| **Scatter – projectile (×5 pellets)** | Tiny circles r=0.1, spread 30° cone. | #FF2D78 | 5 per shot | Linear, fade at 12-unit range |
| **Gun – Arc Welder (plasma/beam)** | Cylindrical barrel 2×0.5, glowing coil rings ×3. | Body: #1A2E33. Coils: #00E5FF. | 1 | Continuous beam: rect 0.3 wide, length 30 units, gradient #00E5FF→#FF2D78, 6 flicker frames |
| **Arc Welder – beam** | Rect 0.3×30, wavy edges (sine amp 0.1). | #00E5FF core, #FF2D78 edge glow | 1 active | Flickers 60Hz; impact sparks on wall |
| **Gun – Mortar Launcher (explosive)** | Short fat rect 0.8×0.9, curved arm. | Body: #4A3728. Warhead: #FF2D78. | 1 | Launch: barrel tilts up 15° for 0.12s |
| **Mortar – projectile** | Circle r=0.3, 4 tiny fins. | #FF2D78 body, #FFB347 fins | On-screen max 3 | Parabolic arc (gravity). Explodes on land |
| **Mortar – explosion** | Expanding circle r=0→4 over 0.3s, then 8 triangle shards. | Ring: #FFB347→#FF2D78→transparent. Shards: #4A3728 | 1 per detonation | Radial burst, smoke puffs ×6 (#666, r=0.5, drift up, 0.8s) |
| **Enemy – Rust Crawler (ground, W1)** | Low rect 2×1.2, 4 stub legs, single red eye r=0.2. | Body: #C45A2D. Eye: #FF2D78. | 3–6 per stage | 4-frame leg crawl, y ±0.05 bob |
| **Enemy – Rust Crawler – hurt** | Same, white flash overlay. | Flash: #FFFFFF 50% | 1 | 0.1s |
| **Enemy – Dripling (flying, W2)** | Teardrop body 1×1.5, 2 wing arcs r=0.8. | Body: #00E5FF. Wings: #1A2E33. Eye: #FF2D78. | 2–5 per stage | Sine-wave hover (y ±0.5, 1.2s). Wings flap 4-frame |
| **Enemy – Dripling – hurt** | Same, magenta flash. | #FF2D78 60% | 1 | 0.1s |
| **Enemy – Press Golem (W1 boss)** | Massive rect 6×8, piston arms ×2 (3×1 each), single visor slit. | Body: #3D3D3D. Pistons: #C45A2D. Visor: #FFB347. | 1 | Idle: slow hydraulic hiss (steam puffs from joints). Attack: arm slam, screen shake |
| **Enemy – Reservoir Warden (W2 boss)** | Octagonal core r=3, 4 rotating tentacle arms (length 5, r=0.3). | Core: #1A2E33. Arms: #00E5FF. Eye: #FF2D78. | 1 | Arms rotate 15°/s. Charge: core pulses magenta |
| **Pickup – Health Cell** | Hexagon r=0.5, cross icon inside. | Shell: #00E5FF. Cross: #FFFFFF. | 2–4 per stage | Float y ±0.2 sine, 1s. Glow halo r=1.2, 40% alpha |
| **Pickup – Ammo Crate** | Rect 1×1, lid at 30° angle, bullet icon. | Body: #FFB347. Lid: #8B7355. | 1–2 per stage | Static; wobble 0.05 when player nears (2-unit radius) |
| **Pickup – Stage Key (exit)** | Diamond r=0.7, spinning. | #FF2D78 with #FFB347 inner glow | 1 per stage | Spin 180°/s, bob 0.15 |
| **Checkpoint Totem** | Pillar 1×4, glowing orb r=0.5 atop. | Pillar: #2C3E50. Orb: #00E5FF. | 0–3 per stage | Inactive: orb dim #1A2E33. Active: orb bright, ring pulses outward r=0.5→2, 1.5s loop |
| **Platform – Solid** | Rect, variable width ×1. Top surface 0.15 lighter strip. | W1: #5C6B73 top #8B7355. W2: #1A2E33 top #2C4A52. | Many | Static |
| **Platform – Crumble** | Same as solid, 4 crack lines. | #8B7355 with #C45A2D cracks | 1–3 per stage | Static until touched; then 0.4s shake → 6 shard pieces fall |
| **Platform – Conveyor** | Rect with 6 directional chevrons scrolling. | Body: #3D3D3D. Chevrons: #FFB347. | 1–2 per stage | Chevrons scroll x at constant speed (visual only) |
| **Haz – Steam Vent** | Floor grate 1.5×0.3, vertical column of circles. | Grate: #5C6B73. Steam: #FFFFFF 30%→transparent. | 1–4 per stage | Column pulses upward, 6 puffs r=0.4, 0.8s cycle |
| **Haz – Electrified Water** | Rect pool 20×1, wavy top edge. | #00E5FF 50% alpha, white sparks ×3 r=0.15 | 1–2 per stage (W2) | Wave sine 0.1 amp; sparks blink 0.2s random |
| **Haz – Spikes** | Row of triangles base 0.4 height 0.6. | #8B7355 with #FF2D78 tips | Clusters of 4–8 | Static |
| **BG Layer 1 – Far skyline** | Silhouette rects/triangles, parallax 0.2×. | W1: #0F1B1F. W2: #0A1618. | Full-width | Static (camera parallax only) |
| **BG Layer 2 – Mid structures** | Pipes, arches, smokestacks, parallax 0.5×. | W1: #1A2E33. W2: #15292E. | Full-width | Parallax scroll |
| **BG Layer 3 – Near detail** | Dripping chains, fungi clusters, broken signs, parallax 0.8×. | W1: #2C3E50. W2: #1E3A40. | Full-width | Parallax scroll; drips fall (0.3s, 4-unit drop) |
| **BG Layer 4 – Foreground fog** | Horizontal gradient band, bottom 3 units. | #1A2E33 20% alpha | Full-width | Static |
| **Neon Sign (decor)** | Rect frame 3×1.5, text shape inside. | Frame: #2C3E50. Text: #FF2D78 or #00E5FF. | 2–4 per stage | Flicker: 80% on, 20% random 0.1s off. Buzz: tiny y jitter 0.02 |
| **Exit Gate** | Rect 4×6, shutter lines ×8, stencil number. | Door: #3D3D3D. Rim: #FF2D78. Number: #FFB347. | 1 per stage | Closed: static. Opening: shutter slides up 0.8s, light floods from behind (#FFB347 radial) |
| **UI – HUD bar** | Rect 20×1.5 top-left. | BG: #0F1B1F 80% alpha. Border: #2C3E50. | 1 | Static |
| **UI – Health bar** | 3 hearts inside HUD, r=0.4 each. | Full: #FF2D78. Empty: #3D3D3D. | 1 set | Pulse scale 1.1 when <1 heart, 0.5s |
| **UI – Ammo counter** | Text block 4×1.5 top-right. | Text: #FFB347. BG: #0F1B1F 80%. | 1 | Flash white 0.1s on pickup |
| **UI – Gun selector** | 4 small icons (0.8×0.8) bottom-left, active has ring. | Inactive: #5C6B73. Active ring: #00E5FF. | 1 set | Active icon pulses scale 1.0→1.15, 0.6s |
| **UI – Stage banner (intro)** | Full-screen rect, large stencil text. | BG: #0F1B1F. Text: #FFB347. Sub: #00E5FF. | 1 per stage | Slide in from top 0.6s, hold 1.5s, fade out 0.4s |
| **UI – Death screen** | Dark overlay, "SCRAPPED" text, retry button. | Overlay: #0F1B1F 85%. Text: #FF2D78. Button: #FFB347. | 1 | Fade in 0.8s. Button pulses 0.8s |
| **UI – World map** | 2×5 grid of stage nodes, connecting path line. | Path: #FFB347. Completed node: #00E5FF. Locked: #3D3D3D. Current: #FF2D78 pulse. | 1 | Player icon walks along path between nodes |
| **Particle – Hit spark** | 6 radial lines, length 0.6. | #FFFFFF → #FFB347 | 1 per hit | 0.1s, scale 1→0 |
| **Particle – Pickup sparkle** | 8 tiny stars r=0.1, spiral outward. | #FFB347, #00E5FF | 1 per pickup | 0.4s, fade |
| **Particle – Dust (land)** | 3 ellipses 0.5×0.25 at feet. | #8B7355 50%→0% | 1 per landing | 0.25s, drift outward |
| **Particle – Checkpoint activate** | Expanding ring + 12 rising motes. | Ring: #00E5FF. Motes: #FFB347. | 1 per activation | Ring r=0→5 over 0.6s, fade. Motes rise 2 units, 0.8s |

# 4. LIGHTING AND ATMOSPHERE

**Ambient:** Very low. Base ambient colour #0F1B1F at 25% intensity. The world is dark; light sources are diegetic (lamps, neon, gunfire, bioluminescence).

**Light sources (per stage, placed as decor):**

| Source | Colour | Radius (units) | Motion |
|---|---|---|---|
| Sodium lamp post (spawn area) | #FFB347 | 8 | Static; subtle 0.03 flicker |
| Neon sign | #FF2D78 or #00E5FF | 5 | Flicker (see recipe) |
| Checkpoint orb (active) | #00E5FF | 6 | Pulse 4→6→4, 2s |
| Gunfire (muzzle flash) | #FFB347 / #FF2D78 / #00E5FF (per gun) | 4 | Instantaneous, 0.06s |
| Bioluminescent moss (W2) | #00E5FF | 3 | Slow breathe, 4s cycle |
| Boss arena spotlight | #FFFFFF 60% | 12 | Static cone from ceiling |
| Exit gate (opening) | #FFB347 | 10 | Radial flood, 0.8s ramp |

**Fog / darkness rules:** Background layers 1–2 are darkened by 40% relative to foreground. In W2 stages, a vertical fog band (#15292E, 30% alpha) sits at 60% height to separate the flooded lower half from the upper architecture. Boss arenas drop global ambient to 10%; only the spotlight and gunfire illuminate.

**Time-of-day / weather:** None. Each world has a fixed "time": W1 is perpetual dusk (orange horizon glow in BG layer 1). W2 is perpetual night with no sky (closed tunnel ceiling in BG layer 1). No dynamic weather.

**Post effects:**

| Effect | Trigger | Strength / Duration |
|---|---|---|
| Vignette | Always on | 40% darkening at edges, radius 70% of viewport |
| Screen shake | Player hit, boss slam, mortar explosion | Intensity 0.3 units, 0.2s. Decays linearly |
| Hit flash (full screen) | Player takes damage | 1-frame #FF2D78 at 15% alpha |
| Chromatic aberration | Low health (<1 heart) | 0.02-unit red/blue split, constant while low |
| Grain | Always on | 3% monochrome noise, 24fps refresh |
| Radial flash | Checkpoint activated | White ring expands from totem, 0.4s, 30% alpha |
| Desaturation | Death | Screen desaturates to 20% colour over 0.8s |

# 5. CHARACTERS AND ANIMATION

## Player (the Scavenger)

**Silhouette:** Chunky, top-heavy. Broad shoulders, short legs, oversized helmet with a glowing visor slit. The exo-suit has visible piston joints at knees and elbows. At a glance: "small tough thing with a big head and a big gun." The visor colour changes with equipped gun (cyan = Arc Welder, magenta = Scatter/Mortar, amber = Rivet).

**Facings:** Left, Right (mirrored). Crouch, jump, and run states exist for both. No diagonal.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | 2 frames: breathe (y ±0.05). Head tilts 2° alternating. | 0.8s loop |
| Run | 4 frames: legs alternate, body bobs y ±0.1, arms swing ±15°. | 0.3s loop |
| Crouch | 1 pose (static). Helmet retracts 0.2 into shoulders. | No loop |
| Jump (ascend) | 1 pose: body stretch 1.8×, legs tucked, arms up. | Transition only |
| Jump (descend) | 1 pose: body return, legs extend forward. | Transition only |
| Land | 2 frames: squash 1.2× → normal. | 0.15s |
| Shoot (Rivet/Scatter) | 2 frames: recoil lean back 5° → return. | 0.1s |
| Shoot (Arc Welder) | 1 pose: arms locked forward, slight lean. | Hold while firing |
| Shoot (Mortar) | 3 frames: crouch → stand → recoil. | 0.2s |
| Hurt | 3 frames: white flash, wobble, recover. | 0.45s |
| Death | Shatter into 8 shards (see recipe). | 1.2s, no loop |

## Rust Crawler (W1 enemy)

**Silhouette:** Low, wide, insect-like. Four legs splayed, single glowing eye on a stalk. At a glance: "a rusty beetle that scuttles."

**Facings:** Left, Right.

| Animation | Frames | Loop |
|---|---|---|
| Idle | 2 frames: eye stalk sways ±3°. | 1.2s |
| Walk | 4 frames: legs alternate, body y ±0.05. | 0.4s |
| Hurt | 1 frame: white flash, legs tuck. | 0.1s |
| Death | Collapse: legs fold inward, body flattens to 0.6 height, fades. | 0.5s |

## Dripling (W2 enemy)

**Silhouette:** Floating teardrop with two moth-like wings. Glowing cyan body, single magenta eye. At a glance: "a angry glowing raindrop."

**Facings:** Left, Right.

| Animation | Frames | Loop |
|---|---|---|
| Hover | 4 frames: wings up/mid/down/mid, body sine y ±0.5. | 1.2s |
| Lunge (attack) | 2 frames: stretch forward 1.5×, wings back. | 0.2s |
| Hurt | 1 frame: magenta flash, body compresses. | 0.1s |
| Death | Pop: expand to 1.3×, then shatter into 6 droplet circles, fade. | 0.6s |

## Press Golem (W1 boss)

**Silhouette:** A squat hydraulic press given legs. Two massive piston arms, a visor slit across its "face," exhaust pipes on shoulders. At a glance: "a construction press that wants to flatten you."

**Facings:** Left, Right.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Steam puffs from joints every 1.5s. Body bobs y ±0.1. | 2s |
| Arm Slam | 4 frames: arm raises 3 units → descends fast → impact squash → recover. | 0.8s |
| Charge (telegraph) | Visor pulses amber 3× over 0.6s, body glows #FFB347. | Before attack |
| Hurt | White flash on piston joints. | 0.1s |
| Death | Pistons explode outward (8 shards), body crumbles over 2s, steam floods screen. | 2s |

## Reservoir Warden (W2 boss)

**Silhouette:** A floating octagonal core with four long segmented tentacle arms ending in claw pincers. Bioluminescent veins pulse across its surface. At a glance: "a deep-sea jellyfish made of subway infrastructure."

**Facings:** Rotates; no fixed facing.

| Animation | Frames / Rule | Loop |
|---|---|---|
| Idle | Arms rotate slowly (15°/s). Core pulses cyan. | Continuous |
| Sweep | 2 arms extend 5 units in a line, core flashes magenta (telegraph 0.5s). | 1s |
| Spin | All 4 arms extend, core spins 360° in 0.8s. | 0.8s |
| Hurt | Core dims to 30% for 0.15s, veins flash white. | 0.15s |
| Death | Core cracks (4 lines), collapses inward to r=0.5, then detonates in expanding cyan ring + 12 shard fragments. | 2.5s |

# 6. FEEDBACK

| Event | Visual | Duration |
|---|---|---|
| **Player hits enemy** | Hit-spark particles (6 radial lines, #FFFFFF→#FFB347) at impact point. Enemy flashes white 50%. Screen shake 0.1 units. | 0.1s |
| **Enemy dies** | Enemy-specific death anim (see §5). +score popup text floats up 2 units, #FFB347. | 0.5–0.6s |
| **Player takes damage** | Player flashes #FF2D78. Full-screen 1-frame pink overlay. Screen shake 0.3 units. Health heart depletes (crack + fade). Chromatic aberration activates if now at 1 heart. | 0.45s |
| **Player at low health (1 heart)** | Heart pulses scale 1.0→1.15 every 0.5s. Vignette darkens to 55%. Red tint 8% on screen edges. | Persistent while low |
| **Pickup collected (health/ammo)** | Pickup pops into 8 star particles (#FFB347/#00E5FF), floats up. HUD element flashes white. | 0.4s |
| **Stage Key collected** | Diamond spins faster, expands to 1.5×, then teleports into HUD. Radial ring expands from player, #FFB347. | 0.6s |
| **Checkpoint activated** | Ring expands from totem (r=0→5). 12 motes rise. Screen radial flash 30%. Totem orb turns from dim to bright cyan permanently. | 0.8s |
| **Door / Exit Gate opening** | Shutter slides up over 0.8s revealing warm light behind (#FFB347 radial). Confetti particles (20 tiny rects, random palette colours) burst from top of gate. | 1.2s total |
| **Timer running out (if stage has timer)** | Screen edges pulse red 3× (0.3s each). HUD timer text flashes #FF2D78. | 0.9s warning |
| **Boss phase transition** | Screen flash white 100%. Boss roars (screen shake 0.5, 0.4s). New attack pattern telegraph colour appears on boss. | 1.0s |
| **Gun switch** | Muzzle flash in new gun's colour at player position. HUD selector ring slides to new icon, 0.15s. | 0.2s |
| **Player crouch-jump** | Dust puff at feet (3 ellipses, #8B7355). Player briefly in crouch pose then extends. | 0.15s |

# 7. SCREENSHOT CHECKLIST

| Screen / State | How to Reach | What a Reviewer Must See |
|---|---|---|
| **Title screen** | Launch game | Game logo in stencil font (#FFB347), subtitle in cyan (#00E5FF), "PRESS START" pulsing magenta. BG: parallax layers 1–3 visible, a single neon sign flickering. Vignette + grain active. |
| **World map** | After title | 2×5 node grid. World 1 row: all 5 nodes. World 2 row: all 5 nodes locked (grey #3D3D3D). Path line in amber. Player icon at Stage 1-1. Completed nodes glow cyan. |
| **Stage intro banner** | Enter any stage | Full-screen slide-in: "WORLD 1 – STAGE 1" in large stencil (#FFB347), subtitle "THE RUSTBELT" (#00E5FF), on dark BG (#0F1B1F). Holds 1.5s then fades. |
| **Gameplay – W1 Stage 1, mid-run** | Play to unit ~60 | Player on a corrugated-steel platform, right-facing, running. BG layers: smokestacks (far), pipes (mid), dripping chain (near). One neon sign flickering in BG. Ground is rust-orange/steel. A Rust Crawler 2 platforms ahead. HUD visible: 3 magenta hearts, ammo counter, 4 gun icons bottom-left with Rivet Driver ringed cyan. |
| **Gameplay – firing Scatter Cannon** | Equip gun 2, shoot | Muzzle flash: 3 radial magenta lines. 5 pellets fanning out in a 30° cone. Player in recoil lean-back pose. Gun selector ring on Scatter icon. |
| **Gameplay – Arc Welder beam hitting wall** | Equip gun 3, shoot into surface | Continuous cyan→magenta wavy beam, 30 units long. Impact sparks (white, 6 radial lines) at wall. Coil rings on gun glowing. Beam flicker visible. |
| **Gameplay – Mortar explosion** | Equip gun 4, lob projectile onto ground | Expanding ring (#FFB347→#FF2D78), 8 shard triangles flying out, 6 grey smoke puffs rising. Screen shake visible. |
| **Gameplay – crouch under a low pipe** | Crouch beneath a 2-unit ceiling | Player in squashed crouch pose (1.8 tall), helmet retracted, passing under a pipe prop. Conveyor platform visible nearby with scrolling chevrons. |
| **Gameplay – W2 Stage 3, flooded section** | Play W2 Stage 3 to mid | Player ankle-deep in electrified water (cyan, wavy top, white sparks). Drippling enemy hovering above. Bioluminescent moss on walls (pulsing cyan). BG: brick arches, dripping. Palette teal-dominant. |
| **Checkpoint activation** | Touch a totem mid-stage | Ring expanding from totem orb, 12 amber motes rising. Orb now bright cyan. Radial white flash. Totem permanently lit. |
| **Boss fight – Press Golem** | W1 Stage 5, enter arena | Arena lighting: ambient 10%, single overhead white spotlight cone. Press Golem (6×8) on far side, visor pulsing amber (telegraph). Player small in foreground. Steam puffs from Golem joints. Walls close in (ceiling at 20 units). |
| **Boss fight – Reservoir Warden** | W2 Stage 5, enter arena | Drained reservoir with concentric ring platforms. Octagonal core floating centre, 4 tentacle arms extended. Bioluminescent veins pulsing. Player on innermost ring. Dark ambient, cyan glow dominant. |
| **Player hurt – low health** | Take damage until 1 heart | Player flashing magenta. Screen: 55% vignette, red edge tint, chromatic aberration (slight red/blue offset on edges). Single heart pulsing. |
| **Player death** | Health reaches 0 | Screen desaturated to 20% colour. 8 triangle shards of player body flying apart. "SCRAPPED" text in #FF2D78. Retry button pulsing #FFB347. |
| **Stage clear / Exit Gate opening** | Collect key, reach gate | Shutter sliding up, warm #FFB347 light flooding out. 20 confetti rects scattering. Stage number stencil on door. Player walking toward light. |
| **World clear (after W1 Stage 5)** | Defeat Press Golem, exit | Transition to World Map: W1 row all nodes now cyan (completed). W2 row unlocks—nodes shift from grey to amber outline. Player icon walks to W2 node 1. |
| **Particle effects close-up** | Any moment with multiple effects | Hit sparks, dust puffs, pickup sparkles, and steam vent puffs all visible simultaneously. Distinct shapes: lines (sparks), ellipses (dust), stars (sparkle), circles (steam). All with 3px black outlines where applicable. |