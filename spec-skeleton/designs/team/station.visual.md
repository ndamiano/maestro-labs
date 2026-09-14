3D, first-person eye-level camera with 72° vertical FOV, unlimited yaw, pitch clamped from -35° to +28°, subtle head-bob and impact shake.

# 1. THE LOOK IN ONE PARAGRAPH

Kestrel-9 is a low-poly, hard-edge derelict service station stranded in Earth orbit, rendered entirely from flat-shaded geometry, emissive lights, and procedural gradients. The palette is cold steel and shadow: #020617 void, #0b1220 deep shadow, #7d8b99 brushed station metal, #8a93a3 panel faces, #46505f scuff, #2f3743 seams, broken by safety amber #ffbf3f, emergency red #ff3b30, O2 cyan #38bdf8, hydro teal #2ee6a8, and reactor violet #b57cff. The mood is quiet, claustrophobic, and mechanically decaying: dust hangs in flashlight beams, emergency lights flicker through half-open doors, and the only true colour arrives from small survival systems still running. The one screenshot the game should sell is a narrow corridor at eye level: the player's white suited forearm and wrench enter from the lower right, a pale flashlight cone cuts through dust, a red emergency light pulses on the left wall, an amber safety strip runs along the wet floor, and a far viewport glows with a cold blue Earth disc.

# 2. THE SPACE

Unit: 1 game unit = 1 metre. The station is one level, floor at y = 0, with no vertical shafts or ladders.

## Generated layout

Each run shuffles six module shells around a central hub.

- Hub: 14.0 unit diameter, 3.6 unit high ring.
- Six spokes: 2.8 unit wide, 8.0 unit long, 3.2 unit high corridors.
- Five standard modules: 8.0 x 5.0 x 3.2 units each.
- Escape airlock module: 7.0 x 5.0 x 3.2 units.
- Whole playable station bounding box: 48.0 x 30.0 x 4.2 units.

## Regions and contents

- **000 Hub**: central junction with six doorways, one large hub console, three viewports, an amber safety ring on the floor, and bright white-amber light.
- **001 Crew Quarters**: three bunks, four crates, a warm amber work light, dented wall panels, and a dim rust-orange tool cart.
- **002 Galley**: one long table, one vending console with a cyan slot, two crates, a broken work light, and cool gray-amber lighting.
- **003 Hydroponics**: four plant racks, teal light, wet floor plates, soil, and a small mist effect near the racks.
- **004 Medbay**: start location; three med beds, red cross decals, clean white panels, one cyan O2 cell, and a soft red medical light.
- **005 Reactor**: one violet reactor core, exposed pipes, caution stripes, a jammed door, and a strong violet pulse.
- **006 Escape Airlock**: goal location; one escape pod, large forward viewport, red-and-white hazard stripes, and a green door status.

## Start and goal

- Player starts at the Medbay bunk closest to the module door, facing the Medbay doorway.
- Goal is the escape pod hatch inside the Escape Airlock module.

## Visual region language

- Hub: white metal, amber floor ring, bright console screen.
- Corridors: dark steel, narrow amber floor strips, red emergency fixtures.
- Crew Quarters: warm amber work light, rust-orange cart, dented panels.
- Galley: cool gray table, cyan vending slot, dim amber light.
- Hydroponics: teal light, green plants, wet reflective floor.
- Medbay: clean white panels, red crosses, cyan O2 glow.
- Reactor: violet core, dark pipe bundles, yellow-black caution stripes.
- Escape Airlock: red hazard stripes, large viewport, white pod, green status light.

## Good roll

A good generated station looks readable and tense.

- Start and goal are at least two doors apart.
- Every module contains 3 to 5 visual landmarks: bunks, tables, racks, console, pod, core, or cart.
- Every corridor has at least 2 emergency or work light anchors.
- No chain of 3 unlit modules.
- No dead-end corridor longer than 8.0 units.
- At least 3 modules have a viewport.
- Hub console is visible from at least 4 spokes.
- Every door has a visible status light.

## Bad roll

A bad generated station looks lost and unfair.

- Goal is adjacent to start.
- 3 or more consecutive modules have no light anchor.
- A dead-end corridor is longer than 12.0 units.
- Two doors have identical colour and no status light.
- The first 15.0 units contain no viewport, console, or landmark.
- Hub floor colour is too close to wall colour.
- The reactor or airlock entrance is visually identical to a storage door.

# 3. RECIPES

Geometry sizes use game units, where 1 game unit = 1 metre. UI sizes use screen fractions: 1 UI unit = 1% of the short screen edge.

| Thing (state) | Shape | Size | Colour | Count | Motion / effect |
|---|---|---|---|---:|---|
| Floor plate — clean | Flat slab with 0.02 bevel | 1.0 x 1.0 x 0.12 | #6b7686 top, #46505f edge, #364152 scuff | 142 | Static |
| Floor plate — wet | Flat slab with 0.02 bevel | 1.0 x 1.0 x 0.12 | #3f4a5a top, #8ecae6 sheen | 12 | Static, slight specular band |
| Floor plate — breach stain | Flat slab with cracks | 1.0 x 1.0 x 0.12 | #2b3a4a base, #90e0ff cracks | 4 | Static |
| Wall panel — intact | Box panel with seams | 1.0 x 3.2 x 0.15 | #8a93a3 face, #2f3743 seams, #556070 rivets | 168 | Static |
| Wall panel — dented | Box panel with dent normal | 1.0 x 3.2 x 0.15 | #75808f face, #3a414d dent | 22 | Static |
| Wall panel — breached | Box panel with hole | 1.0 x 3.2 x 0.15, hole 0.9 x 0.7 | #21252b rim, #b8c2cc shards, #dbeafe rim light | 3 | Emits blue light radius 4.0 |
| Ceiling panel | Flat slab with conduit line | 1.0 x 1.0 x 0.10 | #5b6473 face, #3b4352 conduit | 121 | Static |
| Hazard floor strip | Narrow raised line | 0.18 x 0.02 x 10.0 | #ffbf3f strip, #201a12 edge | 12 | Static |
| Viewport | Recessed frame and glass | 2.4 x 1.4 x 0.12, disc 0.36 diameter | #2a303c frame, #0a1122 glass, #f8fafc stars, #93c5fd Earth | 7 | 90 star dots twinkle over 1.8s; Earth disc drifts 0.02 units over 30s |
| Hub console | Box terminal with screen | 1.2 x 0.9 x 1.8 | #334155 body, #22d3ee screen, #ffbf3f buttons | 1 | Screen flicker: alpha 0.65 to 1.00 over 0.35s |
| Crew bunk | Rectangular bed frame | 1.9 x 0.85 x 0.55 | #d1d5db sheet, #64748b frame, #475569 blanket | 3 | Static |
| Galley table | Box table with top slab | 2.2 x 1.0 x 1.0 | #94a3b8 legs, #cbd5e1 top | 1 | Static |
| Vending console | Tall box with slot | 0.8 x 0.5 x 1.9 | #1f2937 body, #38bdf8 slot | 1 | Slot glow pulse: alpha 0.45 to 0.90 over 0.8s |
| Med bed | Rectangular bed with strap | 1.8 x 0.8 x 0.5 | #e5e7eb sheet, #4b5563 strap, #ef4444 cross | 3 | Static |
| Plant rack | Frame with leaf boxes | 1.6 x 0.6 x 1.8 | #243b36 frame, #2ee6a8 leaves, #16a34a dark leaves, #1f2937 soil | 4 | Leaf sway: 0.02 amplitude over 0.8s |
| Tool cart | Box cart with wheels | 1.1 x 0.6 x 1.2 | #b45309 body, #1f2937 wheels, #94a3b8 wrench | 4 | Static |
| Crate | Box crate with tape | 0.8 x 0.8 x 0.8 | #5b6b83 body, #ffbf3f tape | 10 | Static |
| Reactor core | Glass cylinder with inner emissive cylinder | 1.8 diameter, 1.8 high | #1e1b4b glass, #b57cff core, #4b5563 pipes | 1 | Core pulse: emissive 0.65 to 1.00 over 2.2s; slow rotation 0.05 rad over 2.0s |
| Airlock pod | Rounded capsule with hatch | 2.6 x 1.4 x 1.4 | #cbd5e1 body, #2a303c hatch, #ef4444 and #f8fafc stripes | 1 | Hatch status #22c55e steady |
| Door — closed | Slab with stripe and status | 2.2 x 2.6 x 0.20 | #4b5563 door, #ffbf3f stripe, #ff3b30 status | 7 | Status glow radius 0.8 |
| Door — open | Slab rotated 90° | 2.2 x 2.6 x 0.20 | #4b5563 door, #22c55e stripe, #22c55e status | 0–4 | Opening motion: 90° over 0.70s |
| Door — jammed | Slab with fault spark | 2.2 x 2.6 x 0.20 | #4b5563 door, #f59e0b status | 0–2 | Status flash: 1 Hz; 2 amber sparks every 1.0s |
| Emergency light — lit | Small wall fixture | 0.18 x 0.10 x 0.10 | #ff3b30 fixture, #ff3b30 light | 14 | Radius 5.5, cone 35°, flicker alpha 0.80 to 1.00 every 1.2s |
| Emergency light — dark | Small wall fixture | 0.18 x 0.10 x 0.10 | #7f1d1d fixture | 5 | No emission |
| Work light — lit | Small ceiling fixture | 0.22 x 0.12 x 0.10 | #ffd166 fixture, #ffd166 light | 7 | Radius 6.0, cone 55°, steady |
| Work light — broken | Small ceiling fixture with smoke | 0.22 x 0.12 x 0.10 | #a16207 fixture, #a8a29e smoke | 2 | Cone opacity 0.25, steady; smoke rises 0.4 units over 2.0s |
| Hydro light — lit | Long wall strip | 0.30 x 0.10 x 0.10 | #2ee6a8 light | 4 | Radius 4.0, cone 60°, gentle pulse 0.8s |
| Reactor light — lit | Point light around core | 1.0 sphere radius | #b57cff light | 1 | Radius 8.0, pulse 2.2s |
| Oxygen cell — active | Cylinder with band | 0.28 diameter, 0.30 high | #38bdf8 body, #f8fafc band | 3 | Bob 0.06 amplitude over 1.5s; one full spin every 2.0s; glow radius 1.2 |
| Oxygen cell — collected | Cylinder scaling down | 0.28 diameter, 0.30 high | #38bdf8 body, #f8fafc band | 0–3 | Scale 1.00 to 0.00 over 0.25s; cyan flash |
| Med injector — active | Small vial | 0.08 diameter, 0.22 high | #f8fafc glass, #ef4444 cap | 2 | Bob 0.05 amplitude over 1.6s; red glow radius 1.0 |
| Med injector — collected | Vial scaling down | 0.08 diameter, 0.22 high | #f8fafc glass, #ef4444 cap | 0–2 | Scale 1.00 to 0.00 over 0.25s |
| Repair kit — active | Small box | 0.24 x 0.18 x 0.14 | #f59e0b body, #0f172a cross | 1 | Bob 0.05 amplitude over 1.7s; amber glow radius 1.0 |
| Repair kit — collected | Box scaling down | 0.24 x 0.18 x 0.14 | #f59e0b body, #0f172a cross | 0–1 | Scale 1.00 to 0.00 over 0.25s |
| Player first-person hand | Right arm, glove, wrist lamp | 0.18 x 0.22 x 0.55 | #e2e8f0 suit, #1f2937 glove, #ffd166 wrist lamp | 1 | Breathing sway 0.02 amplitude over 4.0s |
| Player wrench | Handle and head | 0.42 long, 0.04 thick | #64748b handle, #94a3b8 head | 1 | Held in hand; swing arc 120° |
| Flashlight beam — on | Cone from wrist to corridor | Starts 0.12 radius, ends 3.5 radius at 12.0 units | #fff7d6, opacity 0.12 | 1 | Flicker alpha 0.05 to 0.12 over 0.08s when damaged |
| Flashlight beam — off | No geometry | 0.0 | #000000 | 1 | No emission |
| Scav bot — body | Box body with tracks and panel | 0.6 x 0.5 x 0.8 | #b45309 body, #1f2937 tracks, #431407 panel | 2 | Idle bob 0.03 amplitude over 2.0s |
| Scav bot — eye | Sphere | 0.09 diameter | #ff3b30 emissive | 2 | Blink: alpha 1.00 to 0.00 over 0.12s every 2.8s |
| Scav bot — pincer | Two angled plates | 0.12 x 0.08 x 0.35 | #94a3b8 metal | 4 | Attack extend 0.25 over 0.15s |
| Bot smoke — hurt | Soft sphere | 0.30 diameter | #a8a29e, opacity 0.35 | 1 per hit | Rises 0.8 units over 1.0s, fades out |
| Bot smoke — death | Soft spheres | 0.30 diameter | #a8a29e, opacity 0.35 | 3 per death | Rises 0.9 units over 1.2s, fades out |
| Spark — hit | Point particles | 0.03 size | #fbbf24 | 12 per hit | Life 0.40s; random upward bias |
| Spark — door jam | Point particles | 0.03 size | #f59e0b | 2 per flash | Life 0.30s |
| Hull breach mist | Soft cylinder and bubbles | 1.2 diameter, 1.2 high | #dbeafe, opacity 0.35 | 3 | Bubbles rise 1.0 unit over 1.5s; mist opacity pulse 0.8s |
| Dust mote — ambient | Point particle | 0.02 size | #cbd5e1, opacity 0.18 | 400 | Drifts 0.30 units over 6s; visible in beams |
| HUD O2 bar — normal | Rounded rectangle bar | 26 x 3.2 UI | #0f172a background, #334155 border, #38bdf8 fill | 1 | Fill follows O2 state; smooth 0.25s catch-up |
| HUD O2 bar — low | Rounded rectangle bar | 26 x 3.2 UI | #0f172a background, #7f1d1d border, #ef4444 fill, #f8fafc strobe | 1 | Strobe: 0.125s on, 0.125s off, continuous in low state |
| HUD suit bar — normal | Rounded rectangle bar | 26 x 2.2 UI | #0f172a background, #334155 border, #f87171 fill | 1 | Fill follows suit state; smooth 0.25s catch-up |
| HUD suit bar — low | Rounded rectangle bar | 26 x 2.2 UI | #0f172a background, #7f1d1d border, #ef4444 fill | 1 | Pulse: opacity 0.70 to 1.00 at 1 Hz |
| Objective toast | Text panel | 18 x 4.0 UI | #0f172a background, #e2e8f0 text, #ffbf3f label | 1 | Pop: scale 0.95 to 1.00 over 0.25s |
| Pickup toast | Text and icon panel | 18 x 5.0 UI, icon 4.8 UI | #0f172a background, #38bdf8 border, #e2e8f0 text | 1 | Slide in 0.25s, hold 0.70s, fade 0.35s |
| Alarm border — active | Full-screen border | 3.5 UI width | #ef4444, opacity 0.18 | 1 | Strobe: 0.80s cycle, continuous in alarm state |
| Vignette | Radial screen gradient | 100 x 100 UI | #020617 edges | 1 | Base opacity 0.25; +0.12 in unlit rooms; +0.18 in low suit state |
| Grain | Monochrome noise overlay | 120 px cells | #ffffff / #000000 | 1 | Opacity 0.07; +0.05 in low suit state; 8 fps refresh |
| Damage overlay | Radial red edge | 100 x 100 UI | #7f1d1d | 1 | Opacity 0.00 to 0.45 over 0.35s, then decay 0.25s |
| Title overlay — active | Full-screen panel | 100 x 100 UI | #020617 background, #e2e8f0 title, #ffbf3f prompt, #334155 station ring | 1 | Fade 0.50s; station ring rotation 0.20 rad over 4.0s |
| Death overlay — active | Full-screen panel | 100 x 100 UI | #020617 background, #ef4444 text, #ffbf3f prompt | 1 | Fade 1.20s |

# 4. LIGHTING AND ATMOSPHERE

## Ambient light

- Ambient base: #263244, intensity 0.35.
- Floor bounce: #0b1220, intensity 0.10.
- Unlit corridor base visibility: 18.0 units before fog black.

## Light sources

- Emergency red: #ff3b30, radius 5.5, cone 35°, flicker 1.2s.
- Work amber: #ffd166, radius 6.0, cone 55°, steady.
- Broken work amber: #a16207, radius 2.0, cone 25°, opacity 0.25.
- Hydro teal: #2ee6a8, radius 4.0, cone 60%, pulse 0.8s.
- Med red: #ef4444, radius 3.5, cone 45°, steady at opacity 0.45.
- Reactor violet: #b57cff, radius 8.0, pulse 2.2s.
- Breach blue: #dbeafe, radius 4.0, steady.
- Viewport Earthlight: #93c5fd, radius 10.0 through glass, slow tint drift from #93c5fd to #1e3a8a over 180s.
- Flashlight player beam: #fff7d6, radius 12.0, cone 18°, flicker in damaged state.

## Darkness and fog

- Fog colour: #0b1220.
- Fog density: 0.045.
- Fog far: 24.0 units.
- Beyond 24.0 units: #020617 void.
- Light radius falloff: 1.00 at centre, 0.00 at full radius.
- In unlit rooms, only emissive fixtures, viewports, pickups, and player flashlight are readable.

## Time and weather

- No external weather; the station is sealed.
- Orbital Earthlight slowly changes viewport tint over 180s.
- Dust motes drift through all lit spaces.
- Hull breaches add rising blue bubbles and a slight cold-mist cylinder.
- Hydroponics adds faint mist near plant racks, opacity 0.12, 1.0s pulse.

## Post effects

- Vignette: #020617 radial gradient, base 0.25, +0.12 in unlit, +0.18 low suit.
- Grain: monochrome 120 px cells, 0.07 base, +0.05 low suit, 8 fps.
- Pickup flash: #22d3ee, full-screen opacity 0.25, 0.18s.
- Damage flash: #ef4444, full-screen opacity 0.35, 0.25s.
- Door success flash: #22c55e, full-screen opacity 0.12, 0.12s.
- Alarm flash: #ef4444, full-screen opacity 0.20, 0.30s every 0.80s.
- Damage shake: amplitude 0.10 screen, 8 Hz, 0.35s.
- Death shake: amplitude 0.18 screen, 2 Hz, 1.20s.
- Pickup hit-stop: 0.08s, camera scale 0.98.
- Death desaturation: 0.00 to 0.85 over 1.20s, ending in #475569 grey.

# 5. CHARACTERS AND ANIMATION

## Player

Silhouette: a white suited right forearm, dark glove, gray wrench, and a small amber wrist lamp. Read at a glance: human, maintenance-grade, fragile against the rusted station.

- **Idle**: breathing vertical sway 0.02 units over 4.0s; hand micro-drift 0.01 units over 1.7s; wrist lamp steady.
- **Walk**: head-bob 0.08 units at 1.8 Hz while moving; arm pivot 6°; wrench lags 0.05 seconds behind hand.
- **Attack**: wrench swing over 0.45s: windup 0.10s, strike 0.12s, recover 0.23s; swing arc 120°; white slash flash 0.10s on strike.
- **Hurt**: red damage overlay 0.35s; hand recoil 0.05 units over 0.10s; camera dip 0.08 units over 0.08s.
- **Death**: desaturation to #475569 over 1.20s; camera tilt 8°; camera drop 0.50 units over 0.80s; fade to #020617 over 0.80s.

Facings: yaw 360°, pitch -35° to +28°, no body model, no character roll except death tilt.

## Scav Bot

Silhouette: a rust-orange box body, black caterpillar tracks, one large red eye, and a single pincer arm. Read at a glance: mechanical scavenger, damaged, slow, and dangerous when close.

- **Idle**: body bob 0.03 units over 2.0s; cable sway 0.04 units over 0.5s; eye blink every 2.8s, 0.12s off.
- **Walk**: trudge step 0.70s per step; body pitch 2°; tracks rotate; arm sway 4°.
- **Attack**: pincer extend over 0.45s: windup 0.15s, strike 0.15s, recover 0.15s; eye white #f8fafc for 0.10s on strike.
- **Hurt**: smoke puff 0.30s; eye flicker alpha 0.00 to 1.00 over 0.40s; body shake amplitude 0.05 units over 0.30s.
- **Death**: collapse over 0.80s: tilt 15°, drop 0.25 units; 12 sparks for 0.40s; 3 smoke puffs; eye becomes #450a0a.

Facings: yaw only, faces target, no roll; pitch changes only 5° when hurt or dying.

# 6. FEEDBACK

- Hit: white slash arc, 12 amber sparks, bot eye white flash, 0.20s.
- Pickup: object spins and scales to zero, cyan toast, HUD bar fill, 0.35s.
- Damage taken: red vignette to 0.45, damage shake, suit crack line flash, 0.40s.
- Low health: red edge pulse at 1 Hz, grain increase, vignette increase, continuous while low.
- Door opening: door rotates 90°, status changes red to green, dust puff, 0.70s.
- Timer running out: O2 bar strobes red/white at 4 Hz and objective text pulses, continuous while low, each strobe 0.125s on and 0.125s off.

# 7. SCREENSHOT CHECKLIST

| Screen / state | How to reach | What a person must see |
|---|---|---|
| Title | Launch the game, before pressing Start | #020617 background, #e2e8f0 title, #ffbf3f prompt, #334155 rotating station ring |
| Spawn in Medbay | Press Start | Clean white Medbay, red cross decals, cyan O2 cell bobbing, white player hand, HUD bars |
| Main corridor | Exit Medbay doorway | Dark steel corridor, red emergency light, amber floor strip, dust in flashlight beam |
| Hub | Walk from corridor into centre | Six doorways, hub console, three viewports, amber floor ring, white-amber light |
| Crew Quarters | Enter quarters module | Three bunks, rust-orange tool cart, warm amber work light, dented wall panels |
| Galley | Enter galley module | Long gray table, cyan vending slot, broken amber work light with smoke |
| Hydroponics | Enter hydro module | Four teal-lit plant racks, green leaves, wet floor plates, faint mist |
| Reactor | Enter reactor module | Violet pulsing core, dark pipes, yellow-black caution stripes, jammed door with amber flash |
| Escape Airlock goal | Enter airlock module | White escape pod, red-and-white hazard stripes, large viewport, green hatch status |
| Door open | Open any functional door | Door rotates 90° over 0.70s, status changes from #ff3b30 to #22c55e, small dust puff |
| Door jammed | Reach a jammed door state | #f59e0b status flashes at 1 Hz, two amber sparks every 1.0s, door does not rotate |
| Scav Bot idle | Bot present in corridor | Orange box bot, black tracks, red eye, idle bob, cable sway |
| Scav Bot hurt | Hit the bot once | Smoke puff, eye flicker, body shake, 12 amber sparks, 0.40s |
| Scav Bot death | Reduce bot to dead state | Bot tilts and drops 0.25 units, eye becomes #450a0a, 3 smoke puffs, sparks |
| Hull breach | Reach a breached wall | Blue-rimmed hole, #dbeafe mist, rising bubbles, shards, floor breach stain |
| Low O2 | O2 enters low state | #ef4444 O2 bar strobes red/white, red vignette, increased grain, objective text pulses |
| Player damage | Take damage | Red vignette to 0.45, damage shake, suit crack line flash, 0.40s |
| Player death | Suit integrity enters dead state | Desaturation to #475569, camera tilt and drop, #ef4444 death text, fade to black |
| Pickup toast | Collect any pickup | 18 x 5.0 UI panel, icon, #38bdf8 border, slide-in 0.25s, fade 0.35s |
| Alarm state | Alarm condition active | #ef4444 full-screen border strobes every 0.80s, emergency lights stronger, red vignette |