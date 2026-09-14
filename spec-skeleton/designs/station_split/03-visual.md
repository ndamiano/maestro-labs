# 3. VISUAL SPEC

**The look in one paragraph.** DERELICT STATION looks like a practical, worn, emergency-mode space station — functional, damaged, still operating, slightly lived-in, cold and mechanical, a controlled system dying slowly. It is not cyberpunk neon, not cartoonish, not horror-gore, not a sleek new station, not sci-fi fantasy, not a maze. The core promise: *the station is a system; the player reads systems, not scenery.* Every important state — O2, power, hull, drones, coolant, launch requirements, de-orbit pressure — must be readable instantly, and never by color alone.

**Lighting and atmosphere.** No dynamic lighting, no dynamic shadows, no parallax. Flat sprites with subtle dark underlays for separation. Static dimmed lights in the world; functional warning lights only. Atmosphere effects are subtle pulses (max 2 Hz), never strobing or full-screen noise: low-O2 cyan edge vignette, damage red edge flash (max 0.2 s), screen shake (max 4 px, 0.15 s), warm vignette confined to Reactor Core during heat hazard, white fade on launch success, desaturate-and-darken on game over. No exterior space; the setting is sold with static portholes and a faint machine-room backdrop on the title screen.

**The space.** One station, 10 rooms, drawn as flat top-down rectangles at 96 px/tile (1080p). All rooms share base floor (`#171c22`), base wall (`#2a3138`), door frame style, machine state language, HUD icons, warning system, and particle budget. Each room carries one desaturated accent, one or two signature non-interactive details, and a floor decal with its abbreviation. Room accents are decoration only and must never imitate a state color. No room introduces a new visual state language; each is recognizable from its signature object, not just its color.

Room identity table (carried from visual §9):

| Room | Visual identity | Accent token | Non-interactive details | Why distinct |
| --- | --- | --- | --- | --- |
| Docking Bay | Clean start area, neutral gray | `docking #8ea1b3` | Docking clamps, faint white lights, small porthole | Safe tutorial room, visually calmer |
| Crew Quarters | Lived-in hub | `crew #b8a98f` | Bunks, personal storage, soft amber wall light | Central hub should feel occupied |
| Storage | Industrial resource room | `storage #8f7358` | Shelves, crates, caution stripes | Resource room, caution theme |
| Cargo Hold | Dark cargo space | `cargo #4a4f57` | Large crates, cargo nets, hazard stripes | Drone room, darker and more dangerous |
| Medbay | Cleaner medical room | `medbay #a9c2c9` | Medical beds, cross decal, sterile floor lines | Health room, contrast without state color |
| Hydroponics | Muted green life support | `hydro #6f9b6a` | Planters, water stains, recycler fan | Life support midpoint, organic but worn |
| Engineering | Maintenance and reactor prep | `engineering #a46a3a` | Tools, coolant pump, maintenance boards | Reactor preparation, industrial |
| Reactor Core | Dangerous power core | `reactor #7a2b2b` | Large reactor, heat vents, warning lines | Final power hazard, visually intense |
| Bridge | Tactical control room | `bridge #3f6b8a` | Launch computer, console screens, tactical map | Launch computer room, information hub |
| Shuttle Bay | Final launch bay | `shuttle #9aa7b3` | Large shuttle, launch stripes, fuel line | Final objective, visually open and important |

**Recipe table — design tokens** (carried from visual §16; these are the exact values the builder uses):

Palette tokens:

```json
{
  "base": {
    "void": "#07090c",
    "floor": "#171c22",
    "wall": "#2a3138",
    "line": "#4a5560",
    "panel": "rgba(10, 14, 18, 0.82)",
    "text": "#eaf2f8",
    "text_dim": "#9aa7b5"
  },
  "state": {
    "o2": "#4fd8ff",
    "integrity": "#77f2a8",
    "power": "#ffb300",
    "breach": "#ff4d4d",
    "drone": "#ff8a00",
    "coolant": "#62a4ff",
    "objective": "#ffffff"
  }
}
```

State color reservation: `o2` cyan = breathable air (player/room O2, O2 machines, airflow); `integrity` green = player survivability (bar, medkit); `power` amber = electrical (conduits, nodes, cells); `breach` red = hull failure (breach effects, hull warnings, damage feedback); `drone` orange = threat (drones, map markers, alerts); `coolant` blue = reactor coolant (cells, timer, flow); `objective` white = action/progress (marker, highlight, checklist checks). State colors appear only on machines, HUD, map icons, and effects — never on room decoration.

Icon list (drawn procedurally; no font files): `air` (three short horizontal wavy lines), `shield`, `lightning` (bolt), `cracked_hex`, `drone_triangle` (triangle + exclamation), `snowflake`, `fuel_rod` (vertical capsule, flame tip), `objective_chevron`, `warning_triangle`, `check` (rounded), `x` (rounded), `door_open`, `door_closed`, `door_jammed`, `emp`, `wrench`, `o2_tank`, `medkit`, `hull_patch`, `power_cell`, `coolant_cell`.

Shape language: rounded = resources, player, O2, usable items; angular = hazards, breaches, drones; straight lines = power, conduits, doors, airflow; white = player action, objective, progress, checklist completion.

Typography: labels uppercase sans-serif (`Inter, Roboto, "Segoe UI", system-ui, sans-serif`); numbers monospaced/tabular (`ui-monospace, "JetBrains Mono", "IBM Plex Mono", monospace`); timers never jump. HUD panels: flat, dark translucent background `rgba(10, 14, 18, 0.82)`, 1 px border `#3a4450`, no bevels, no animated sci-fi clutter, no unnecessary glow, icons left-aligned with values.

On-screen priority: 1 player critical state, 2 active warning banner, 3 interaction prompt/active channel, 4 current room status, 5 map and launch checklist, 6 time and objective, 7 event log, 8 world decoration.

**3.4 Draw order** (carried from engineering, ruled in 0.2): floor → floor decals → state overlays (airflow, power conduits, breach effects, hazard shimmer) → machines → doors → items → player → drones → particles → screen warning overlays → HUD.

**3.5 Procedural texture recipes** (carried from visual §16; base version is T1, detail is T2 item 6):

Floor (256×256, tiled): base `#171c22`; noise scale 0.02, contrast 0.08; 18 scratches, alpha 0.08, width 1 (T2); panel lines spacing 64, color `#20262d`, alpha 0.9; 6 wear stains, alpha 0.06 (T2).

Wall (256×256, tiled): base `#2a3138`; panel height 96, panel gap 4; noise scale 0.03, contrast 0.07; caution stripe probability 0.15, color `#6b6f73` (T2).

Do not generate highly detailed textures; keep the station lightweight for browser performance.

**3.6 World state feedback (state grammar).** Carried in full from visual §5 and §8; visual implies the rules it names, and gameplay already contains them — no conflict beyond those ruled in 0.2.

- **Player O2 (top-left vitals):** cyan bar, air icon, `O2 64`; below 25 the label `LOW` appears; below 10 `CRITICAL` appears and the bar pulses white/cyan. Suit backpack O2 light pulses cyan when low, faster below 10; below 10 a subtle cyan vignette pulses at screen edges; at 0 the vignette intensifies and the O2 warning sound repeats. The HUD number is authoritative; light and vignette are secondary.
- **Player Integrity (below O2):** green bar, shield icon, `INTEGRITY 82`; below 25 `LOW`; below 10 `CRITICAL` with white/green pulse. On any damage: brief red hit flash on the sprite, red vignette flash max 0.2 s, screen shake max 4 px for 0.15 s. Invulnerability: player sprite flickers white at 10 Hz for 0.5 s.
- **Room O2 (current room panel + map):** panel shows `O2 80`, `O2 45 LOW`, `O2 12 LOW`, `O2 0 LOW` with the air icon; below 30 add a warning triangle; at 0 the air icon becomes outlined with an X. Map node top-left air icon: high = filled, medium (30–59) = half-filled, low (1–29) = outlined with exclamation, zero = with X.
- **Hull and breach:** panel `HULL 30 LOW` below 30; at 0 `HULL 0 BREACH` with cracked-hexagon icon. World: low hull (below 30) shows small floor/wall cracks plus occasional tiny dust puff; breach shows a jagged dark opening, vacuum particle streaks (T2), a thin red border on the map node, and the cracked-hexagon icon. Low hull also puts a small cracked-hexagon icon on the map node.
- **Power:** panel shows exactly one of `POWER NO POWER` (gray lightning), `POWER POWERED`, `POWER EPC mm:ss`, `POWER CELL mm:ss`, `POWER REACTOR`. World: thin wall conduits; unpowered = dark gray; powered = amber glow; timed source = small amber pulse every second; reactor = stronger amber with deeper pulse; power loss = conduits fade out over 0.3 s; cell expiration = brief amber blink before fade. Power nodes show a diegetic display: `EMPTY`, `EPC mm:ss`, `CELL mm:ss`. Map top-right lightning icon: off = gray outline, on = amber filled, reactor = amber filled with small pulse.
- **Drones:** base sprite is a circular/squarish hovering body with two short mechanical arms, orange caution light, scanner ring, slight hover bob. States: Inactive = parked, gray light, no motion; Patrol = slow movement, soft hover, gray/low-orange light; Alert = orange light brightens, small orange ring or triangle above the drone, faster movement; Attack = brief orange zap effect plus short red/orange flash on player; Disabled = smoking, one arm bent or sparking, gray light, no motion. Map bottom-right orange triangle when an active drone is in that room (none when inactive or disabled). Panel shows `DRONE ACTIVE` or `DRONE --`.
- **Reactor coolant chip:** dedicated chip, snowflake icon: above 30 s `COOLANT 2:14`; at or below 30 s the value flashes; expired shows `COOLANT EXPIRED` with warning. Reactor core states: Offline = dark core, gray lights; Damaged = red blinking light, wrench prompt; Pump repaired = blue snowflake light; Coolant active = blue-white flow lines; Spin-up = core rotates with white-blue progress ring; Online = amber-red glow, strong power conduits; Coolant low = blue timer flashes, core glow flickers slightly; Coolant expired = core glow turns red, steam puffs, heat shimmer; Heat hazard = red floor pulse inside Reactor Core room, steam, warning banner. The hazard is room-specific — the whole screen never turns red.
- **Launch checklist:** appears on the right once the player has entered Bridge or Shuttle Bay, or once the reactor has been online at least once; it stays visible. Rows: `[check] REACTOR ONLINE`, `[x] SHUTTLE POWERED`, `[check] COMPUTER PRIMED`, `[x] FUEL INSTALLED`, `[x] SHUTTLE O2 42/60`, then `LAUNCH 34%`. Complete = white rounded check; incomplete = gray rounded X; failing during launch = red X flashes briefly and the event log shows the reason. If the O2 row is unmet it shows the current value `SHUTTLE O2 42/60`. Reset shows a specific line, e.g. `LAUNCH RESET — SHUTTLE O2 LOW`. Shuttle state lights: gray = not ready, white = requirements satisfied, blue-white = launch channel active, red = reset, bright white = success.
- **Objective:** top-center `DAY 3`, `TIME TO DE-ORBIT 02:14`, `OBJECTIVE: Bring Reactor Online`. Current objective room on map: white chevron. Objective complete: soft major blip plus event log entry. No subobjective text; the interaction prompt handles local direction.
- **Warnings:** banner top-center below the time panel. Examples: `WARNING: PLAYER O2 LOW 12`, `WARNING: HULL EVENT — STORAGE 0:07`, `WARNING: COOLANT LOW 0:24`, `WARNING: DE-ORBIT 1:45`, `WARNING: LAUNCH RESET — FUEL MISSING`. Rules: one type per banner, no stacking five identical; most critical first; max two banners; persistent warnings pulse slowly, max 2 Hz (T2); critical warnings use a white border with red icon, no full-screen strobing; every warning has a matching event log entry and sound.

**3.7 Station map (persistent, bottom-right).** 10 rounded-rectangle room nodes using the abbreviations from the 4.2 roster, connected by door lines. Node icon positions: top-left O2 state, top-right power state, bottom-left hull/breach, bottom-right drone state, center objective chevron. Current room: thick white outline plus slight white fill. Breach: red jagged outer border, cracked-hexagon icon, room name may get red text. Hull event warning: red target reticle over the target room with a countdown number next to it; the banner shows the same information. Door line styles: open = solid white; closed = dashed gray; jammed = crossed red line with small X. The map updates in real time; it is a survival tool, not a menu, and never a zoomable/rotatable widget.

**3.8 Machine and door visuals.** Machines are wall-mounted or floor-anchored and never block movement. General machine states: Off = gray light; Damaged = red blinking light with small crack/spark detail; Powered working = function-colored light; Repairing = progress ring with sparks; Complete = steady light, no red blink. O2 machines use cyan when working with subtle cyan output particles (T2). The Reactor is the largest machine (states in 3.6). Launch Computer: console with checklist lights — inactive gray, priming blue-white progress, primed white. Fuel Line: pipe slot — empty gray outline, installed orange/white fuel rod, complete steady white light. Launch Pad: large floor outline, shuttle silhouette, edge pad lights — gray / white / blue-white cycling (channel active) / red flash (reset) / bright white (success).

Doors are the only transitions and must be instantly distinguishable: Open = panels retracted into walls, white light line; Closed = panels filled, gray light line; Jammed = panels slightly askew, red flashing light, warning stripes; Repairing jammed = wrench sparks and progress ring; Repaired = becomes closed, red light gone. Airflow particles appear only through open doors.

**3.9 Item and door/airflow rules.** Pickups are small floor items (20–28 px) with the inventory icon shape: Wrench = gray tool, slightly larger; O2 Tank = cyan canister with air icon; Medkit = white box, green cross; Hull Patch = flat gray square with tape/plus; Power Cell = amber cylinder with lightning; EMP Charge = dark coil with white ring; Coolant Cell = blue canister with snowflake; Fuel Rod = black rod, orange flame tip. Dropped items: same icon, slight floor shadow, no despawn visual, no aggressive pulsing; the selected target shows a white outline.

Airflow particles (T2, presentation only): small cyan particles from the higher-O2 room to the lower-O2 room through open doors; none if O2 difference is below 5; count per door = `clamp(abs(A.O2 − B.O2) / 10, 1, 5)`; small, low alpha, slow; if a room is breached, particles are pulled toward the breach or through open doors to the breached room; breached rooms show stronger vacuum streaks.

Power conduits (3.6): run along walls, never cross closed or jammed doors, glow continuously through open doors, fade out on loss.

**3.10 Action feedback table** (carried in full from visual §10; audio names map to 6.3):

| Action | Visual feedback | Audio feedback |
| --- | --- | --- |
| Pick up item | Small white blip on item, item disappears to inventory | `pickup` |
| Inventory full | Red X on prompt, prompt says `INVENTORY FULL` | `ui_error` |
| Use O2 Tank | Cyan ring around player, O2 bar rises | `use_o2` |
| Use Medkit | White/green cross flash on player, integrity bar rises | `use_medkit` |
| Repair start | Wrench icon, progress ring, sparks | `repair_start` |
| Repair progress | Progress bar/ring fills; soft tick at 25/50/75% | `repair_tick` |
| Repair complete | Machine light changes, red blink stops | `repair_complete` |
| Door open | Door slides, state light changes | `door_open` |
| Door close | Door slides, state light changes | `door_close` |
| Jammed door repair | Sparks, progress ring, jammed light changes | `door_repair` |
| Hull patch | Patch plate appears, breach closes, cracks reduced | `hull_patch` |
| Power cell install | Conduits glow, node display updates | `power_install` |
| Power cell expiration | Amber blink, conduits fade | `power_cell_expire` |
| Power loss | Conduits fade, lights dim | `power_loss` |
| EMP use | Expanding white ring, drones spark and go gray | `emp` |
| Drone activation | Drone light gray to orange, event log entry | `drone_activate` |
| Drone alert | Orange ring above drone, speed increases | `drone_alert` |
| Drone attack | Orange zap, player red flash, screen shake | `drone_attack` |
| Breach | Vacuum particles, red map border | `breach` |
| Reactor coolant low | Coolant timer flashes, warning banner | `coolant_low` |
| Reactor coolant expired | Reactor glow turns red, steam | `coolant_expired` |
| Reactor spin-up | Core rotates, progress ring fills | `reactor_spinup` |
| Launch requirement met | Checklist item turns to check, small blip | `launch_requirement` |
| Launch reset | Red flash on checklist, progress bar resets | `launch_reset` |
| Launch success | White flash, shuttle engine glow, screen fade | `launch_success` |

Carried anti-goals (visual §14): no fog of war, no dynamic lighting/shadows, no parallax, no exterior space, no animated starfield, no detailed faces, no gore, no decorative state colors, no random visual flicker, no map zoom/rotation, no pause menu in core run, no cinematic cutscenes, no enemy variety beyond two drones, no alternate map states, no collectible trinkets.

Carried visual integration requirements (visual §15): the engine exposes the render views in 2.3 (`roomView`, `powerView`, plus `reactor` and `launch` state directly) so HUD updates immediately when state changes; bars may interpolate visually (T2) but numbers are exact; state icons and map update immediately; particle caps 128 per visible room / 512 total; warning pulses max 2 Hz; audio event names are exactly the 6.4 list.
