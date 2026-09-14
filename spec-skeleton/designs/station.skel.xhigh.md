# Derelict Station: Last Shift — Build Spec

## 0. SCOPE

### 0.1 Asked

| Requirement | Where it lives |
| --- | --- |
| Survive on a derelict space station | Section 4, Section 5, module `survival` |
| Station environment with damaged systems | Section 1.2, Section 3.1, module `station` |
| Player movement and interaction | Section 4.1, module `player` |
| Life-support and hull survival systems | Section 4.2, module `sim` |
| Repair, tools, inventory, containers | Section 4.3, Section 4.4, module `inventory` |
| Escalating hazards and random failures | Section 4.5, module `events` |
| Hostile maintenance drones | Section 4.6, module `drones` |
| Rescue objective and win condition | Section 4.7, module `rescue` |
| Deterministic simulation and debug controls | Section 8, module `debug` |
| Automated checks | Section 9, module `tests` |
| Atmospheric visual lighting | Section 3, module `render` |
| Web Audio feedback | Section 6, module `audio` |
| Browser-game UX screens | Section 7, module `ux` |

### 0.2 Tiers

| Feature | Tier | Purpose |
| --- | ---: | --- |
| Title screen, play state, pause, victory, defeat | T1 | Must ship |
| Fixed station map, rooms, terminals, containers | T1 | Must ship |
| Player movement, collision, interaction | T1 | Must ship |
| Power, oxygen, pressure, radiation, reactor fuel/coolant | T1 | Must ship |
| Damage objects, repair actions, inventory, item effects | T1 | Must ship |
| Rescue comms progress and escape pod win | T1 | Must ship |
| Health loss, suit oxygen, defeat | T1 | Must ship |
| DOM HUD, message log, inventory bar, event banner | T1 | Must ship |
| Seeded deterministic simulation, debug API, tests | T1 | Must ship |
| Basic Web Audio sounds | T1 | Must ship |
| Dynamic lighting and emergency flicker | T1 | Must ship |
| Drones, pathfinding, combat interaction | T2 | Elevates tension |
| Radiation storms, shield terminal, event scheduler escalation | T2 | Elevates replay value |
| Score, final stats, high score | T2 | Elevates completion |
| Particle effects, screen shake, sound layering | T3 | Polish |
| Accessibility options, reduced motion, volume control | T3 | Polish |

---

## 1. CONVENTIONS

### 1.1 Units, axes, frames

- 1 tile = 32 pixels.
- World size = 24 tiles wide by 16 tiles tall.
- X increases right.
- Y increases down.
- Object coordinates are in tile units.
- A coordinate of `(11.5, 9.5)` means the center of tile column 11, row 9.
- Player collision radius = 0.35 tile.
- Player movement speed = 5 tiles/second.
- Interaction radius = 1.25 tiles.
- Simulation tick = 0.1 seconds.
- The display may render at 60 frames per second, but simulation only changes on fixed 0.1-second ticks.
- All system meters are 0 to 100 unless stated otherwise.
- Reactor fuel and coolant are 0 to 100.
- Rescue progress is 0 to 100.
- Health is 0 to 100.
- Suit oxygen is 0 to 100.
- IDs are integers.

### 1.2 Important conventions

- There is one global simulation state. All systems read and write that state.
- No hidden randomness is allowed. All random choices use one seeded random source.
- Visual flicker is deterministic from time and object ID, not from random numbers.
- Phases are:
  - `title`
  - `playing`
  - `paused`
  - `victory`
  - `defeat`
- The station is derelict, but the run starts with all major meters stable and no active damage. Dereliction is expressed through visuals, containers, and later events.
- Interact priority when multiple objects are in range:
  1. Drone
  2. Damage
  3. Terminal
  4. Container
- Repair progress pauses if the player leaves the interaction radius or loses the required item.
- Damage effects pause while the player is within interaction radius and has the required item for that damage.
- Wrench is a non-consumed tool.
- Other items are consumed when successfully used.
- Containers yield exactly 2 items when opened.
- The event scheduler does not run before `time >= 50`.
- The first scheduled event is at `time = 50`.
- After each event, the next event is scheduled at `current_time + 40 + rng(0, 10)`.
- The rescue escape pod is only usable after rescue progress reaches 100.
- Defeat occurs only when player health reaches 0.
- Victory occurs when the player interacts with the escape pod after rescue progress reaches 100.

Station layout:

| Room | Tile bounds | Purpose |
| --- | --- | --- |
| Habitat | x 2 to 6, y 2 to 4 | Player start flavor, lockers |
| Recycler | x 9 to 13, y 2 to 4 | Oxygen terminal, crates |
| Cargo | x 16 to 20, y 2 to 4 | Supply crates |
| Medbay | x 2 to 6, y 7 to 10 | Medical drawers |
| Comms | x 9 to 13, y 7 to 10 | Rescue terminal |
| Reactor | x 16 to 20, y 7 to 10 | Fuel/coolant terminal |
| Power | x 2 to 6, y 12 to 14 | Power terminal, crates |
| Escape | x 9 to 13, y 12 to 14 | Escape pod |
| Shield Bay | x 16 to 20, y 12 to 14 | Shield terminal |

Corridors:

- Vertical corridor at x 7 to 8, y 2 to 14.
- Vertical corridor at x 14 to 15, y 2 to 14.
- Horizontal corridor at y 5 to 6, x 2 to 20.
- Horizontal corridor at y 11, x 2 to 20.

Fixed terminals:

| Terminal | Kind | Position |
| --- | --- | --- |
| Recycler | `recycler` | `(11.5, 3.5)` |
| Comms | `comms` | `(11.5, 9.5)` |
| Reactor | `reactor` | `(19.5, 9.5)` |
| Power | `power` | `(4.5, 13.5)` |
| Shield | `shield` | `(18.5, 13.5)` |
| Escape Pod | `escapePod` | `(11.5, 13.5)` |

Fixed containers:

| Container | Kind | Position |
| --- | --- | --- |
| Habitat locker 1 | `locker` | `(3.5, 2.5)` |
| Habitat locker 2 | `locker` | `(5.5, 2.5)` |
| Habitat locker 3 | `locker` | `(3.5, 4.5)` |
| Recycler crate 1 | `crate` | `(10.5, 2.5)` |
| Recycler crate 2 | `crate` | `(12.5, 4.5)` |
| Recycler tool cabinet | `toolCabinet` | `(13.5, 3.5)` |
| Cargo crate 1 | `crate` | `(16.5, 2.5)` |
| Cargo crate 2 | `crate` | `(18.5, 2.5)` |
| Cargo crate 3 | `crate` | `(20.5, 2.5)` |
| Cargo crate 4 | `crate` | `(17.5, 4.5)` |
| Medbay drawer 1 | `medDrawer` | `(3.5, 7.5)` |
| Medbay drawer 2 | `medDrawer` | `(5.5, 7.5)` |
| Medbay drawer 3 | `medDrawer` | `(3.5, 10.5)` |
| Reactor cache 1 | `reactorCache` | `(17.5, 7.5)` |
| Reactor cache 2 | `reactorCache` | `(19.5, 10.5)` |
| Reactor tool cabinet | `toolCabinet` | `(20.5, 9.5)` |
| Power crate 1 | `crate` | `(3.5, 12.5)` |
| Power crate 2 | `crate` | `(5.5, 12.5)` |
| Comms crate | `crate` | `(10.5, 10.5)` |

Damage kinds:

| Damage kind | Required item | Repair time | Immediate effect on repair |
| --- | --- | ---: | --- |
| `breach` | `patch` | 1.0 s | Pressure +10 |
| `breaker` | `wrench` | 2.0 s | Power +10 |
| `coolantLeak` | `wrench` | 2.0 s | Stops coolant drain |
| `radiationLeak` | `wrench` | 2.0 s | Stops radiation generation |

Item kinds:

| Item | Consumed | Effect |
| --- | ---: | --- |
| `wrench` | no | Repairs breakers, coolant leaks, radiation leaks, drones |
| `patch` | yes | Repairs breaches, adds +10 pressure on completion |
| `powerCell` | yes | Power +30 |
| `coolant` | yes | Reactor coolant +25, usable near reactor |
| `fuelCell` | yes | Reactor fuel +25, usable near reactor |
| `o2Cartridge` | yes | Suit oxygen +30 |
| `medkit` | yes | Health +30 |
| `raduit` | yes | Radiation -30, health +5 |
| `scrap` | yes | Score +10 when used, or +10 score at victory if carried |

Starting inventory:

| Slot | Item |
| ---: | --- |
| 0 | `wrench` |
| 1 | `patch` |
| 2 | `powerCell` |
| 3 | `medkit` |
| 4 | `o2Cartridge` |
| 5 | empty |
| 6 | empty |
| 7 | empty |

---

## 2. CONTRACTS

### 2.1 File layout

The following layout blocks are required. They are the build units and must not be merged into one opaque block.

| Block | Responsibility | Consumes | Produces |
| --- | --- | --- | --- |
| `boot` | Creates initial state, input listeners, audio context, render loop, pause handling | DOM, input events | running game |
| `rng` | Seeded random number source | seed | deterministic random values |
| `station` | Fixed map, walkable grid, terminals, containers | seed, state | station records |
| `sim` | Fixed-tick simulation for systems, damage, events, drones, health | state, dt | updated state |
| `player` | Player movement, collision, inventory, interaction | state, input | updated player, interaction results |
| `ui` | DOM HUD, screens, log, prompts | state | DOM updates |
| `audio` | Web Audio sound engine | sound name, state events | audio playback |
| `render` | Scene drawing, lighting, effects | state, time | rendered frame |
| `debug` | Public debug API | state | plain data returns |

### 2.2 Global context

The simulation state is a single plain object:

```text
state = {
  phase,
  time,
  tick,
  seed,
  rngState,
  moveX,
  moveY,
  player,
  systems,
  rescueProgress,
  rescueReady,
  shieldTimer,
  damages,
  drones,
  containers,
  terminals,
  events,
  log,
  score,
  repairs,
  itemsLooted,
  dronesDisabled,
  nextEventAt,
  lootQueue,
  defeatReason
}
```

Player record:

```text
player = {
  x,
  y,
  facing,
  health,
  suitO2,
  inventory,
  damagedTimer
}
```

Systems record:

```text
systems = {
  power,
  oxygen,
  pressure,
  radiation,
  reactorFuel,
  reactorCoolant
}
```

Damage record:

```text
damage = {
  id,
  kind,
  x,
  y,
  room,
  repairProgress
}
```

Drone record:

```text
drone = {
  id,
  x,
  y,
  health,
  cooldown,
  repairProgress,
  pathTimer
}
```

Container record:

```text
container = {
  id,
  kind,
  x,
  y,
  room,
  looted
}
```

Terminal record:

```text
terminal = {
  id,
  kind,
  x,
  y,
  room
}
```

Event record:

```text
event = {
  id,
  kind,
  startTime,
  duration
}
```

Log record:

```text
logEntry = {
  time,
  message
}
```

Initial state values:

| Field | Initial value |
| --- | ---: |
| `phase` | `title` |
| `time` | 0 |
| `tick` | 0 |
| `seed` | 1 |
| `moveX` | 0 |
| `moveY` | 0 |
| `player.x` | 11.5 |
| `player.y` | 9.5 |
| `player.health` | 100 |
| `player.suitO2` | 100 |
| `systems.power` | 100 |
| `systems.oxygen` | 100 |
| `systems.pressure` | 100 |
| `systems.radiation` | 0 |
| `systems.reactorFuel` | 80 |
| `systems.reactorCoolant` | 80 |
| `rescueProgress` | 0 |
| `rescueReady` | false |
| `shieldTimer` | 0 |
| `nextEventAt` | 50 |
| `score` | 0 |
| `repairs` | 0 |
| `itemsLooted` | 0 |
| `dronesDisabled` | 0 |
| `defeatReason` | `null` |

### 2.3 Block specifics

`rng.next()`:
- Returns a float from 0.0 inclusive to 1.0 exclusive.
- Must be the only source of randomness in simulation.

`rng.range(min, max)`:
- Returns an integer from `min` inclusive to `max` inclusive.

`station.build(state)`:
- Sets terminals, containers, walkable grid, room labels.
- Uses fixed positions from Section 1.2.
- Does not use randomness for geometry.

`sim.tick(state, dt)`:
- Advances time by `dt`.
- Updates events, systems, damage, drones, player, health, score.
- Must be deterministic for a given seed and dt.

`player.update(state, dt)`:
- Applies `moveX` and `moveY`.
- Collides with walls and room bounds.
- Normalizes diagonal movement.

`player.interact(state)`:
- Finds nearest interactable in range.
- Returns plain data result.
- Starts repair, uses terminal, or opens container.

`player.useItem(state, slot)`:
- Uses item in slot.
- Returns plain data result.

`ui.sync(state)`:
- Updates DOM-only HUD.
- Does not draw UI in the scene viewport.

`audio.play(name)`:
- Plays a synthesized sound.
- Does not load external assets.

`render.draw(state)`:
- Draws the station, entities, lighting, and effects.
- Uses deterministic flicker formulas.

---

## 3. VISUAL SPEC

The game is a top-down derelict space station rendered as a cold, industrial survival space. The station is a dark metallic grid of small rooms connected by narrow corridors. The player is a lone engineer in a compact pressure suit, moving through flickering lights, leaking steam, exposed wiring, and dim red emergency lighting. The visual language should feel abandoned but still operational: panels are scarred, terminals glow weakly, cargo is scattered, and every meter on the HUD is tied to a visible station system. The lighting is the primary mood driver. Power gives cyan light, oxygen gives green light, pressure gives blue light, radiation gives purple light, and critical failures turn the environment into red alarm light. The overall palette is desaturated steel with a few bright system colors so the player can read danger at a glance.

### 3.1 Map geometry and scene composition

- The scene viewport shows the station grid.
- The camera follows the player with a smooth lerp.
- The camera should not show more than a few rooms at once.
- Rooms have metallic floor tiles and dark walls.
- Corridors are slightly darker than rooms.
- Terminals are placed against walls or on open floor near the back of rooms.
- Containers are visually distinct:
  - Lockers are tall thin cabinets.
  - Crates are square wooden/metal boxes.
  - Tool cabinets have a red cross or wrench glyph.
  - Medical drawers are white with a red cross.
  - Reactor caches are gray with orange hazard stripes.

Room visual identity:

| Room | Visual accent |
| --- | --- |
| Habitat | warm dim lamp, bed outline, personal lockers |
| Recycler | green tubes, fan unit |
| Cargo | scattered crates, orange hazard tape |
| Medbay | white panels, red cross, blue light |
| Comms | blinking antenna dish, purple/blue screens |
| Reactor | orange core glow, coolant pipes |
| Power | yellow/cyan breaker panels |
| Escape | white pod outline, green ready light |
| Shield Bay | purple shield rings, radiation warning |

### 3.2 Texture and asset table

| Asset | Size | Description |
| --- | ---: | --- |
| Floor tile | 32x32 | Dark steel with subtle panel lines |
| Corridor floor | 32x32 | Same floor, 10% darker |
| Wall tile | 32x32 | Dark gray, vertical panel seams |
| Door frame | 32x32 | Metallic frame, no functional doors |
| Player sprite | 32x32 | Compact engineer, cyan visor, gray suit |
| Drone sprite | 32x32 | Rust-red maintenance drone, red eye |
| Terminal base | 32x32 | Dark console with glowing screen |
| Recycler terminal | 32x32 | Green fan icon |
| Comms terminal | 32x32 | Purple antenna icon |
| Reactor terminal | 32x32 | Orange core icon |
| Power terminal | 32x32 | Yellow breaker icon |
| Shield terminal | 32x32 | Purple shield icon |
| Escape pod | 48x48 | White oval pod, green ready light |
| Locker | 16x32 | Tall locker |
| Crate | 32x32 | Square supply crate |
| Tool cabinet | 16x32 | Red wrench cabinet |
| Medical drawer | 32x16 | White drawer, red cross |
| Reactor cache | 32x32 | Gray box, orange stripes |
| Breach damage | 32x32 | Torn metal, white steam particles |
| Breaker damage | 32x32 | Sparking panel, yellow/orange sparks |
| Coolant leak | 32x32 | Blue vapor puddle |
| Radiation leak | 32x32 | Purple glow, warning icon |

Item icons:

| Item | Icon shape |
| --- | --- |
| `wrench` | gray wrench |
| `patch` | green bandage square |
| `powerCell` | yellow battery |
| `coolant` | blue droplet |
| `fuelCell` | orange capsule |
| `o2Cartridge` | green gas tank |
| `medkit` | white box with red cross |
| `raduit` | purple radiation shield |
| `scrap` | brown gear |

### 3.3 Lighting

- Base ambient light = 0.18.
- Player emits a warm white light:
  - Radius = 4.5 tiles.
  - Intensity = 0.9.
  - Flicker = `0.88 + 0.12 * sin(time * 11)`.
- Terminals emit colored light:
  - Radius = 1.8 tiles.
  - Power = cyan.
  - Oxygen = green.
  - Pressure = blue.
  - Radiation = purple.
  - Shield = orange.
- If `systems.power < 30`, terminal lights are dimmed to 20% and emergency red fixtures flicker.
- Emergency red flicker formula:
  - `0.55 + 0.35 * sin(time * 7 + id * 1.7)`
- Critical state triggers:
  - Oxygen below 30: green lights strobe.
  - Pressure below 30: blue lights strobe and steam particles appear near breaches.
  - Radiation above 60: purple vignette increases.
  - Health below 30: red vignette pulses.
- Radiation storm adds purple screen edge flicker.
- No random lighting. All flicker is computed from time and ID.

### 3.4 Effects

| Effect | Rule |
| --- | --- |
| Breach steam | White particles rise from breach for 1 second after spawn |
| Breaker sparks | Yellow/orange sparks every 0.3 seconds while active |
| Coolant vapor | Blue particles drift from coolant leak |
| Radiation glow | Purple pulsing ring around radiation leak |
| Repair sparks | Small white/yellow sparks during repair progress |
| Drone hover | Slight vertical bob, no sprite flip needed |
| Player damage | Red flash on player for 0.2 seconds |
| Storm | Purple edge flicker and small particle streaks |
| Victory | Green light pulse from escape pod |
| Defeat | Red static fade and audio drop |

---

## 4. GAMEPLAY SPEC

The most important part of play is triage. The player is not just collecting items; the player is choosing which failing station system to save before personal health, suit oxygen, or rescue progress fails. Every event creates a competing demand on time, tools, and movement. The core tension is: the station is stable enough to learn, but unstable enough that ignoring one room for too long makes the whole run collapse.

### 4.1 Player Controller

Controls:

| Input | Action |
| --- | --- |
| W / Up | Move up |
| S / Down | Move down |
| A / Left | Move left |
| D / Right | Move right |
| E | Interact with nearest object |
| 1 through 8 | Use inventory slot |
| P or Esc | Pause |

Movement:
- Player movement uses normalized vector from `moveX` and `moveY`.
- Movement speed = 5 tiles/second.
- Player cannot pass through walls.
- Player collision circle radius = 0.35 tile.
- Player position is clamped to walkable tiles.
- Camera follows player with a lerp of 0.15 per frame.

Player stats:
- Health = 0 to 100.
- Suit oxygen = 0 to 100.
- Suit oxygen drains only when station conditions are poor.
- Player dies at health 0.

Interaction:
- `interact()` finds nearest interactable within 1.25 tiles.
- Priority: drone, damage, terminal, container.
- If no object is in range, the result is `ok: false`.

### 4.2 Station Systems

All system updates run once per 0.1-second tick.

Power:
- Base load = 6 per second.
- Reactor output = 6 per second if `reactorFuel > 0` and `reactorCoolant > 0`, otherwise 0.
- Extra drain comes from active unrepaired breaker damage and active shield.
- Active unrepaired breaker damage adds 8 per second.
- Active shield adds 4 per second.
- Power update:

```text
powerDelta = reactorOutput - baseLoad - extraDrain
power = clamp(power + powerDelta * dt, 0, 100)
```

- If `power < 95` and reactor output is active, reactor fuel drains 1 per second.
- If `power < 95` and reactor output is active and `radiation > 20`, reactor coolant drains 0.5 per second.
- At the start, power is 100, reactor output equals base load, and fuel/coolant do not drain.
- `powerCell` adds +30 power.

Oxygen:
- Base oxygen drain = 4 per second.
- Each active drone adds 1 per second oxygen drain.
- Each active unrepaired breach adds 1 per second oxygen drain.
- Oxygen generation = `4 * pressure / 100` if `power > 10`, otherwise 0.
- Oxygen update:

```text
oxygenDelta = oxygenGeneration - oxygenDrain
oxygen = clamp(oxygen + oxygenDelta * dt, 0, 100)
```

- At the start, oxygen stays 100 because generation equals base drain.

Pressure:
- Each active unrepaired breach reduces pressure by 4 per second.
- Pressure otherwise does not regenerate automatically.
- Patching a breach adds +10 pressure immediately.

Radiation:
- Each active unrepaired radiation leak adds 3 per second.
- An active radiation storm adds 5 per second.
- Active shield reduces radiation by 4 per second.
- Radiation update:

```text
radiationDelta = leakDrain + stormDrain - shieldReduction
radiation = clamp(radiation + radiationDelta * dt, 0, 100)
```

Reactor:
- Reactor fuel starts at 80.
- Reactor coolant starts at 80.
- Fuel and coolant are 0 to 100.
- Fuel is only consumed when power is under 95 and reactor output is active.
- Coolant is only consumed when radiation is above 20 and reactor output is active.
- `fuelCell` adds +25 fuel near the reactor terminal.
- `coolant` adds +25 coolant near the reactor terminal.
- `scrap` can be used near the reactor terminal for +10 fuel.

Shield:
- The shield terminal starts the shield for 30 seconds if `power > 40`.
- While `shieldTimer > 0`, shield is active.
- Active shield drains 4 power per second.
- Active shield reduces radiation by 4 per second.
- Shield cannot be restarted until `shieldTimer` reaches 0.

Suit oxygen:
- If station oxygen is below 30, suit oxygen drains 3 per second.
- If station oxygen is 0, suit oxygen drains 8 per second.
- If station pressure is below 30, suit oxygen drains 2 per second.
- If station oxygen is above 60, suit oxygen recovers 5 per second.
- If suit oxygen is 0, player health drains 4 per second.

Health:
- Health regens 1 per second if:
  - Health is below 100
  - Power is above 60
  - Oxygen is above 70
  - Pressure is above 70
  - Radiation is below 20
- Health drains from environmental damage:
  - Pressure below 30: 2 per second
  - Radiation above 50: 2 per second
  - Radiation above 80: 6 per second
  - Suit oxygen at 0: 4 per second
- Drone hit: 8 health with 1-second cooldown.

### 4.3 Damage and Repair

Damage objects appear from events or debug.

Active damage effects:

| Damage kind | Effect while active |
| --- | --- |
| `breach` | Pressure -4/s, oxygen drain +1/s |
| `breaker` | Power extra drain +8/s |
| `coolantLeak` | Reactor coolant -3/s |
| `radiationLeak` | Radiation +3/s |

Damage effects pause while the player is within 1.25 tiles and has the required item.

Repair progress:
- Progress increases by `dt` while the player remains in range and has the required item.
- If the player leaves range or loses the item, progress resets to 0.
- Repair times:
  - `breach`: 1.0 s
  - `breaker`: 2.0 s
  - `coolantLeak`: 2.0 s
  - `radiationLeak`: 2.0 s
  - drone: 1.0 s

Repair completion:
- Damage is removed.
- `repairs` increases by 1.
- Immediate effect applies:
  - `breach`: pressure +10
  - `breaker`: power +10
  - `coolantLeak`: stops drain
  - `radiationLeak`: stops radiation generation
- Patch is consumed.
- Wrench is not consumed.

### 4.4 Inventory and Items

Inventory:
- 8 slots.
- Slots 0 through 7.
- Each slot holds one item kind or is empty.
- Items are consumed on successful use except wrench.

Item rules:

| Item | Usable anywhere? | Effect |
| --- | ---: | --- |
| `wrench` | no | Used by interaction on machines/drones |
| `patch` | no | Used by interaction on breach |
| `powerCell` | yes | Power +30 |
| `coolant` | no | Reactor coolant +25 near reactor |
| `fuelCell` | no | Reactor fuel +25 near reactor |
| `scrap` | yes | Score +10, or +10 score at victory if carried |
| `o2Cartridge` | yes | Suit oxygen +30 |
| `medkit` | yes | Health +30 |
| `raduit` | yes | Radiation -30, health +5 |

Terminal interactions:

| Terminal | Action |
| --- | --- |
| `recycler` | Message only; oxygen is managed by station systems and items |
| `comms` | Rescue progress +15 if power > 50 and oxygen > 40 |
| `reactor` | Use coolant, fuelCell, or scrap if near terminal |
| `power` | Power terminal; interacting with nearby breaker damage is required for repair |
| `shield` | Starts shield for 30 s if power > 40 and shieldTimer is 0 |
| `escapePod` | Wins if rescueReady is true |

Container loot tables:

| Container kind | Loot table |
| --- | --- |
| `locker` | wrench 40%, medkit 20%, patch 20%, powerCell 10%, scrap 10% |
| `crate` | scrap 40%, coolant 20%, o2Cartridge 15%, patch 15%, powerCell 10% |
| `medDrawer` | medkit 50%, o2Cartridge 30%, raduit 20% |
| `toolCabinet` | wrench 60%, patch 25%, powerCell 15% |
| `reactorCache` | fuelCell 40%, coolant 40%, scrap 20% |

Loot generation:
- Each container yields 2 items.
- If a `lootQueue` is present, it is consumed in order.
- Otherwise, the container chooses 2 entries from its loot table using the seeded random source.

### 4.5 Events

Events only occur while phase is `playing`.

Scheduler:
- First event at 50 seconds.
- After each event, next event is at `current_time + 40 + rng(0, 10)`.
- Event duration is immediate unless stated.
- Active events can overlap, but caps apply.

Event kinds:

| Event kind | Effect |
| --- | --- |
| `breach` | Spawns a breach damage in a random room |
| `breaker` | Spawns a breaker damage and immediately reduces power by 10 |
| `coolantLeak` | Spawns a coolant leak in reactor area and immediately reduces coolant by 10 |
| `radiationLeak` | Spawns a radiation leak in reactor/shield area and immediately raises radiation by 10 |
| `storm` | Radiation storm active for 20 seconds |
| `swarm` | Spawns 1 to 3 drones in random walkable tiles |

Difficulty tiers:

| Tier | Time range | Event weights |
| --- | ---: | --- |
| 1 | 0 to 120 s | breach 4, breaker 3, coolantLeak 2, radiationLeak 1, storm 0, swarm 0 |
| 2 | 120 to 300 s | breach 3, breaker 3, coolantLeak 2, radiationLeak 2, storm 1, swarm 2 |
| 3 | 300 to 480 s | breach 3, breaker 2, coolantLeak 2, radiationLeak 3, storm 2, swarm 3 |
| 4 | 480 to 600 s | breach 4, breaker 2, coolantLeak 1, radiationLeak 3, storm 2, swarm 4 |

Event caps:
- Maximum active breaches = 2.
- Maximum active breakers = 2.
- Maximum active coolant leaks = 2.
- Maximum active radiation leaks = 2.
- Maximum active drones = 4.
- If a scheduled event would exceed a cap, choose the next highest weighted event. If all options exceed caps, skip the event but still advance the schedule.

### 4.6 Drones

Drone behavior:
- Drones spawn from random walkable tiles.
- Drones move toward the player at 2.5 tiles/second.
- Drones use pathfinding on the walkable grid.
- Path is recomputed every 0.5 seconds.
- Drones attack if within 1.2 tiles of the player.
- Attack damage = 8 health.
- Attack cooldown = 1 second.
- Each drone drains 1 oxygen per second while active.
- A drone can be disabled by interacting with it while carrying a wrench.
- Drone repair time = 1 second.
- While a drone is being disabled, it cannot attack.
- Disabling a drone increases `dronesDisabled` by 1 and adds score.

### 4.7 Rescue, Win, Loss, Score

Rescue:
- Rescue progress starts at 0.
- Interacting with the comms terminal adds 15 progress if:
  - Power > 50
  - Oxygen > 40
- If power or oxygen is insufficient, show a message and do not add progress.
- When rescue progress reaches 100, `rescueReady` becomes true.
- The escape pod only wins if `rescueReady` is true.

Victory:
- Phase becomes `victory`.
- Score is finalized.
- Escape pod plays victory sound.

Defeat:
- Phase becomes `defeat` when health reaches 0.
- Defeat reason is the last damage source:
  - `asphyxiation` if suit oxygen caused the final drain
  - `pressure` if low pressure caused the final drain
  - `radiation` if high radiation caused the final drain
  - `drone` if drone damage caused the final drain
  - `general` otherwise

Score:
- Score updates continuously during play.
- On victory, final score is:

```text
score = floor(time * 10)
      + floor(rescueProgress * 2)
      + floor(health * 5)
      + floor(oxygen * 2)
      + repairs * 25
      + itemsLooted * 10
      + dronesDisabled * 20
      + carriedScrapCount * 10
```

- Score is displayed on the end screen.

---

## 5. CHARACTERS

The player is the only human character: a practical station engineer trying to keep a dying habitat alive long enough to reach the escape pod. They should feel competent but constrained, wearing a compact pressure suit with a cyan visor, a small backpack, and tool loops. Their animation should be crisp and readable, not heroic. The hostile characters are rusted maintenance drones, former station service bots now damaged and hostile. They are not intelligent enemies; they are persistent hazards that drain oxygen and force the player to spend wrench time. Their visual identity should be clearly mechanical and hostile: red eye, rust texture, slow hover, and occasional spark.

### 5.1 Player animation

Player animation states:

| State | Frames | Description |
| --- | ---: | --- |
| Idle | 1 | Slight breathing bob |
| Walk | 4 | Simple 4-frame cycle |
| Interact | 2 | Reaches toward object |
| Damaged | 1 | Red flash overlay |

Orientation:
- Top-down, no separate left/right mirror needed if sprite is symmetric.
- Facing is stored as one of: up, down, left, right, and diagonals.

### 5.2 Drone animation

Drone animation states:

| State | Frames | Description |
| --- | ---: | --- |
| Hover | 2 | Slight bob |
| Move | 2 | Slight forward tilt |
| Attack | 1 | Red eye flashes |
| Disabled | 2 | Sparks stop, eye dims |

Orientation:
- Drones always face the player.
- Drone sprite can rotate or flip based on direction.

---

## 6. AUDIO

All sounds are generated with the Web Audio API. No external audio assets are used. Master gain = 0.25. Overlapping sounds of the same name are limited to one active voice.

| Sound name | Recipe | Rule |
| --- | --- | --- |
| `ui_blip` | Square wave, 660 Hz, 0.05 s, attack 0.005 s, decay 0.04 s | UI button press |
| `footstep` | Filtered noise, lowpass 400 Hz, 0.05 s, attack 0.005 s, decay 0.04 s | Player moves every 0.35 s |
| `repair` | Sawtooth sweep 220 Hz to 440 Hz, 0.20 s, attack 0.01 s, decay 0.18 s | Repair progress completes |
| `pickup` | Sine sweep 880 Hz to 1320 Hz, 0.08 s, attack 0.005 s, decay 0.07 s | Item collected from container |
| `use_item` | Triangle wave, 330 Hz, 0.12 s, attack 0.01 s, decay 0.10 s | Consumable used |
| `breach` | Noise burst 1.2 s, lowpass 800 Hz, plus sine 55 Hz 1.2 s | Breach damage spawns |
| `alarm` | Square wave alternating 520 Hz and 650 Hz, 0.15 s per note, 3 notes | Oxygen, pressure, or health enters critical |
| `drone` | Sawtooth 120 Hz with 20 Hz wobble, 0.30 s, attack 0.02 s, decay 0.25 s | Drone is within 4 tiles |
| `drone_hit` | Square wave, 180 Hz, 0.10 s, attack 0.005 s, decay 0.08 s | Player is hit by drone or drone is disabled |
| `storm` | Filtered noise, lowpass 1200 Hz rising to 3000 Hz, 0.8 s | Radiation storm begins |
| `victory` | Sine arpeggio 523, 659, 784 Hz, 0.30 s total | Escape pod win |
| `defeat` | Sine sweep 220 Hz to 80 Hz, 1.0 s, attack 0.05 s, decay 0.90 s | Player health reaches 0 |

Audio rules:
- Footsteps only play while `phase` is `playing` and player is moving.
- Alarm sounds every 3 seconds while any critical condition is active.
- Drone sound loops while a drone is within 4 tiles, with 0.5-second spacing.
- Critical conditions are:
  - Oxygen below 30
  - Pressure below 30
  - Radiation above 60
  - Health below 30
  - Power below 30

---

## 7. UX

All UX is HTML and CSS. No UI is drawn inside the game scene viewport.

Layout:

| Area | Purpose |
| --- | --- |
| Top bar | Station meters |
| Bottom bar | Inventory and interact prompt |
| Left side | Message log |
| Top center | Event banner |
| Center overlays | Title, pause, victory, defeat |

### 7.1 Top bar

Shows five station meters and one player meter:

| Meter | Color | Label |
| --- | --- | --- |
| Power | cyan | PWR |
| Oxygen | green | O2 |
| Pressure | blue | PSI |
| Radiation | purple | RAD |
| Reactor Fuel | orange | FUEL |
| Reactor Coolant | light blue | CLNT |
| Player Health | red | HP |
| Suit O2 | bright green | SUIT |

Meters:
- Width 160 pixels.
- Height 10 pixels.
- Text label on left.
- Numeric value on right.
- Critical state blinks when below threshold.
- Radiation meter blinks when above threshold.

### 7.2 Bottom bar

- 8 inventory slots.
- Each slot is 48x48 pixels.
- Slot number shown in corner.
- Item icon centered.
- Selected slot has a bright outline.
- Clicking a slot uses that item.
- Number keys 1 through 8 use that item.
- Interact prompt appears above inventory:
  - Example: `[E] Patch breach`
  - Example: `[E] Use medkit`
  - Example: `[E] Open crate`

### 7.3 Message log

- Shows last 5 messages.
- Each message fades after 6 seconds.
- Message types:
  - `info` = white
  - `warning` = yellow
  - `danger` = red
  - `success` = green
- Examples:
  - `Hull breach in Medbay`
  - `Comms progress 35%`
  - `Rescue ready`
  - `Radiation storm detected`

### 7.4 Event banner

- Appears at top center for major events.
- Lasts 5 seconds.
- Large text with warning icon.
- Examples:
  - `RADIATION STORM`
  - `DRONE SWARM`
  - `HULL BREACH`
  - `POWER FAILURE`

### 7.5 Objective panel

Small panel in top right:

```text
RESCUE: 35%
Reach escape pod at 100%
```

When ready:

```text
RESCUE READY
Go to escape pod
```

### 7.6 Title screen

- Title text: `DERELICT STATION`
- Subtitle: `Last Shift`
- Short instructions:
  - Move with WASD
  - Interact with E
  - Use items with 1-8
- Button: `Begin Shift`
- Background: dim station silhouette with flickering red light.

### 7.7 Pause screen

- Shown when `P` or `Esc` is pressed during play.
- Buttons:
  - Resume
  - Restart
- Simulation pauses.
- Audio pauses or ducks.

### 7.8 Victory screen

- Title: `ESCAPE SUCCESSFUL`
- Stats:
  - Time survived
  - Score
  - Repairs
  - Items looted
  - Drones disabled
- Button: `Play Again`

### 7.9 Defeat screen

- Title: `SIGNAL LOST`
- Reason text from `defeatReason`
- Stats same as victory screen
- Button: `Try Again`

---

## 8. DEBUG API

The game installs `window.__game` with plain functions. Every call is synchronous and returns only plain data.

| Call | What it does | What it returns |
| --- | --- | --- |
| `start()` | Resets to a fresh run at time 0 and enters `playing` using the current seed | `{ phase, time, seed }` |
| `step(dt, n)` | Advances `n` ticks of `dt` seconds without waiting for real time, then draws once | `{ time, phase }` |
| `setTime(t)` | Advances simulation forward to `t` seconds without drawing | `{ time, phase }` |
| `seed(n)` | Sets seed to `n`, reseeds the random source, rebuilds generators, and returns to `title` | `{ seed, phase }` |
| `getState()` | Returns a plain-data copy of every record field | full state object |
| `setMove(dx, dy)` | Sets persistent player movement direction; values are -1, 0, or 1 | `{ moveX, moveY }` |
| `interact()` | Performs one interact action with the nearest object | `{ ok, target, action }` |
| `useItem(slot)` | Uses inventory slot 0 through 7 | `{ ok, kind, deltas }` |
| `setPaused(v)` | Sets pause state; true pauses, false resumes | `{ phase }` |
| `setPlayer(x, y)` | Teleports player to tile coordinates | `{ x, y }` |
| `setPlayerHealth(v)` | Sets player health | `{ health }` |
| `setSuitO2(v)` | Sets player suit oxygen | `{ suitO2 }` |
| `setSystem(name, v)` | Sets `power`, `oxygen`, `pressure`, `radiation`, `reactorFuel`, or `reactorCoolant` | `{ name, value }` |
| `setRescue(v)` | Sets rescue progress and updates rescueReady | `{ progress, ready }` |
| `setInventory(slot, kind)` | Sets an inventory slot to an item kind or empty string | `{ slot, kind }` |
| `clearInventory()` | Sets all inventory slots to empty | `{ inventory }` |
| `spawnDamage(kind, x, y)` | Adds a damage object at a location | `{ id }` |
| `spawnDrone(x, y)` | Adds a drone at a location | `{ id }` |
| `setEvent(kind)` | Starts the named event immediately | `{ id, kind }` |
| `setLoot(kinds)` | Queues exact items for the next container open | `{ queued }` |
| `setShield(timer)` | Sets shield timer in seconds | `{ shieldTimer }` |

Debug determinism:
- The same seed and the same sequence of debug calls always produce the same state.
- `step` and `setTime` use the simulation tick, not real time.
- `setTime` only advances forward.
- `getState()` returns no functions, no internal references, and no live objects.

---

## 9. TESTS

Each check uses only calls listed in Section 8. Numeric checks use a tolerance of 0.000001.

1. `seed(1); start(); getState()`  
   Must find:
   - `phase` is `playing`
   - `time` is 0
   - `player.health` is 100
   - `player.suitO2` is 100
   - `systems.power` is 100
   - `systems.oxygen` is 100
   - `systems.pressure` is 100
   - `systems.radiation` is 0
   - `systems.reactorFuel` is 80
   - `systems.reactorCoolant` is 80
   - `rescueProgress` is 0
   - `rescueReady` is false
   - `player.inventory[0]` is `wrench`
   - `player.inventory[1]` is `patch`

2. `seed(7); start(); step(0.1, 100); getState()`  
   Must find:
   - `time` is 10.0
   - `phase` is `playing`
   - `damages.length` is 0
   - `drones.length` is 0
   - `systems.power` is 100
   - `systems.oxygen` is 100
   - `systems.pressure` is 100
   - `systems.radiation` is 0
   - `systems.reactorFuel` is 80
   - `systems.reactorCoolant` is 80

3. `seed(7); start(); setTime(45.0); getState()`  
   Must find:
   - `time` is 45.0
   - `phase` is `playing`
   - `damages.length` is 0
   - `events.length` is 0

4. `seed(7); start(); setPlayer(9.5, 7.5); setMove(1, 0); step(0.1, 2); setMove(0, 0); getState()`  
   Must find:
   - `player.x` is 10.5
   - `player.y` is 7.5
   - `phase` is `playing`

5. `seed(7); start(); setRescue(85); setPlayer(11.5, 9.5); interact(); getState()`  
   Must find:
   - `rescueProgress` is 100
   - `rescueReady` is true
   - `phase` is `playing`

6. `seed(7); start(); setRescue(100); setPlayer(11.5, 13.5); interact(); getState()`  
   Must find:
   - `phase` is `victory`
   - `rescueReady` is true

7. `seed(7); start(); setSystem('pressure', 50); spawnDamage('breach', 3.5, 8.5); setPlayer(3.5, 8.5); interact(); step(0.1, 10); getState()`  
   Must find:
   - `damages.length` is 0
   - `systems.pressure` is 60
   - `player.inventory[1]` is empty
   - `repairs` is 1

8. `seed(7); start(); setSystem('power', 80); spawnDamage('breaker', 4.5, 13.5); setPlayer(4.5, 13.5); interact(); step(0.1, 20); getState()`  
   Must find:
   - `damages.length` is 0
   - `systems.power` is 80
   - `player.inventory[0]` is `wrench`
   - `repairs` is 1

9. `seed(7); start(); setSystem('reactorFuel', 20); setSystem('power', 50); step(0.1, 10); getState()`  
   Must find:
   - `systems.reactorFuel` is 10
   - `systems.power` is 50
   - `systems.reactorCoolant` is 80

10. `seed(7); start(); setSystem('oxygen', 10); step(0.1, 10); getState()`  
   Must find:
   - `systems.oxygen` is 10
   - `player.suitO2` is 97

11. `seed(7); start(); setSystem('radiation', 20); spawnDamage('radiationLeak', 17.5, 10.5); step(0.1, 10); getState()`  
   Must find:
   - `systems.radiation` is 50
   - `damages.length` is 1

12. `seed(7); start(); setSystem('radiation', 0); setEvent('storm'); step(0.1, 10); getState()`  
   Must find:
   - `systems.radiation` is 50
   - `events.length` is 1
   - `events[0].kind` is `storm`

13. `seed(7); start(); spawnDrone(9.5, 7.5); setPlayer(9.5, 7.5); step(0.1, 10); getState()`  
   Must find:
   - `player.health` is 92
   - `drones.length` is 1
   - `systems.oxygen` is 99

14. `seed(7); start(); spawnDrone(9.5, 7.5); setPlayer(9.5, 7.5); interact(); step(0.1, 10); getState()`  
   Must find:
   - `drones.length` is 0
   - `player.health` is 100
   - `systems.oxygen` is 99
   - `dronesDisabled` is 1

15. `seed(7); start(); setPlayerHealth(30); useItem(3); getState()`  
   Must find:
   - `player.health` is 60
   - `player.inventory[3]` is empty

16. `seed(7); start(); setSystem('radiation', 70); setPlayerHealth(90); setInventory(0, 'raduit'); useItem(0); getState()`  
   Must find:
   - `systems.radiation` is 40
   - `player.health` is 95
   - `player.inventory[0]` is empty

17. `seed(7); start(); setSystem('power', 50); setInventory(0, 'powerCell'); useItem(0); getState()`  
   Must find:
   - `systems.power` is 80
   - `player.inventory[0]` is empty

18. `seed(7); start(); setSuitO2(70); setInventory(0, 'o2Cartridge'); useItem(0); getState()`  
   Must find:
   - `player.suitO2` is 100
   - `player.inventory[0]` is empty

19. `seed(7); start(); clearInventory(); setLoot(['scrap', 'patch']); setPlayer(16.5, 2.5); interact(); step(0.1, 1); getState()`  
   Must find:
   - `player.inventory[0]` is `scrap`
   - `player.inventory[1]` is `patch`
   - the container at `(16.5, 2.5)` has `looted` true
   - `itemsLooted` is 1

20. `seed(7); start(); setPlayerHealth(1); setSystem('radiation', 90); step(0.1, 10); getState()`  
   Must find:
   - `phase` is `defeat`
   - `defeatReason` is `radiation`
   - `player.health` is 0

21. `seed(7); start(); setRescue(100); setPlayer(11.5, 13.5); interact(); getState()`  
   Must find:
   - `phase` is `victory`
   - `score` is 900

SCREENSHOTS:

| Screen/state | What a person must see |
| --- | --- |
| Title | Large `DERELICT STATION` title, `Last Shift` subtitle, control list, `Begin Shift` button, dim flickering station background |
| Normal play | Top meters all green or bright, player in Comms room, inventory bar with starting items, objective panel showing `RESCUE: 0%` |
| Low power | Power meter red and blinking, cyan terminal lights dim, emergency red fixtures visible, message log warning |
| Hull breach | Breach damage visible with white steam particles, pressure meter dropping, interact prompt `[E] Patch breach` |
| Radiation storm | Purple event banner, purple edge flicker, radiation meter rising, storm particles visible |
| Drone encounter | Drone near player, red drone eye, drone sound icon or visual pulse, health bar decreasing after hit |
| Rescue ready | Objective panel shows `RESCUE READY`, escape pod glows green, escape pod interact prompt visible |
| Victory | `ESCAPE SUCCESSFUL` screen, score, stats, `Play Again` button |
| Defeat | `SIGNAL LOST` screen, defeat reason, score, stats, `Try Again` button |

---

## 10. BUILD ORDER

1. Build state structure, seeded random source, phases, and fixed 0.1-second tick.
2. Build the fixed station map, walkable grid, rooms, terminals, and containers.
3. Build player movement, collision, input, and camera.
4. Build the base survival meters: power, oxygen, pressure, radiation, reactor fuel, reactor coolant, suit oxygen, and health.
5. Build inventory, item use, and terminal interactions.
6. Build damage objects and repair progress.
7. Build containers and deterministic loot.
8. Build the rescue system: comms progress, escape pod, victory, defeat, and score.
9. Build the event scheduler and event effects.
10. Build drones, pathfinding, attack cooldown, and drone disable interaction.
11. Build the DOM UX: top meters, inventory, log, event banner, objective, title, pause, victory, and defeat.
12. Build lighting, room visuals, item icons, damage visuals, and effects.
13. Build Web Audio sounds and audio rules.
14. Build the debug API and make all simulation paths debuggable.
15. Run Section 9 tests and fix any mismatch.
16. Polish performance, flicker, particles, sound overlap, and readability.

---

## 11. DEFINITION OF DONE

### Simulation Core

- [ ] Fixed 0.1-second tick runs during play.
- [ ] Title, playing, paused, victory, and defeat phases work.
- [ ] Time, tick, seed, and rngState are stored in state.
- [ ] No hidden randomness exists outside the seeded random source.
- [ ] Pause stops simulation and audio.

### Station Map

- [ ] 24x16 world renders correctly.
- [ ] All rooms match Section 1.2 bounds.
- [ ] Corridors connect all rooms.
- [ ] All terminals exist at listed positions.
- [ ] All containers exist at listed positions.
- [ ] Walkable grid blocks walls correctly.

### Player Controller

- [ ] WASD and arrow keys move the player.
- [ ] Diagonal movement is normalized.
- [ ] Player collides with walls.
- [ ] Camera follows the player smoothly.
- [ ] Interact radius is 1.25 tiles.
- [ ] Interact priority is drone, damage, terminal, container.

### Survival Systems

- [ ] Power follows Section 4.2 formula.
- [ ] Oxygen follows Section 4.2 formula.
- [ ] Pressure follows Section 4.2 formula.
- [ ] Radiation follows Section 4.2 formula.
- [ ] Reactor fuel and coolant drain only under specified conditions.
- [ ] Suit oxygen drains and recovers correctly.
- [ ] Health regen and damage rules work.
- [ ] Critical meter warnings appear.

### Items and Repair

- [ ] Starting inventory matches Section 1.2.
- [ ] All item effects work as listed.
- [ ] Wrench is not consumed.
- [ ] Patch is consumed on breach repair.
- [ ] All damage kinds repair correctly.
- [ ] Repair progress pauses when player leaves range or lacks item.
- [ ] Containers yield exactly 2 items.
- [ ] Loot tables match Section 4.4.

### Events and Hazards

- [ ] First event occurs at 50 seconds.
- [ ] Event spacing follows `40 + rng(0, 10)`.
- [ ] Difficulty tiers change weights at 120, 300, and 480 seconds.
- [ ] Event caps are enforced.
- [ ] Breach, breaker, coolant leak, radiation leak, storm, and swarm work.
- [ ] Storm lasts 20 seconds.
- [ ] Shield terminal starts 30-second shield.

### Drones

- [ ] Drones spawn within active event caps.
- [ ] Drones path to the player.
- [ ] Drones move at 2.5 tiles/second.
- [ ] Drones attack with 1-second cooldown.
- [ ] Drones drain oxygen.
- [ ] Drones can be disabled with wrench in 1 second.
- [ ] Disabled drones stop draining oxygen and attacking.

### Rescue, Win, Loss

- [ ] Comms terminal adds 15 rescue progress when conditions are met.
- [ ] Comms terminal refuses progress when power or oxygen is too low.
- [ ] Rescue progress reaches 100 and sets rescueReady.
- [ ] Escape pod wins only when rescueReady is true.
- [ ] Defeat occurs when health is 0.
- [ ] Defeat reason is stored correctly.
- [ ] Score formula matches Section 4.7.

### Visual

- [ ] Rooms are visually distinct.
- [ ] Player, drones, terminals, containers, and damage are readable.
- [ ] Lighting follows Section 3.3.
- [ ] Critical states produce visible color and flicker changes.
- [ ] Breach, breaker, coolant, and radiation effects are visible.
- [ ] Victory and defeat have distinct visual states.

### UX

- [ ] All UI is HTML and CSS.
- [ ] No UI is drawn in the scene viewport.
- [ ] Top bar shows all meters.
- [ ] Inventory shows 8 slots and item icons.
- [ ] Number keys and clicks use items.
- [ ] Message log shows last 5 messages.
- [ ] Event banner appears for major events.
- [ ] Objective panel updates.
- [ ] Title, pause, victory, and defeat screens exist.

### Audio

- [ ] All sounds in Section 6 are synthesized.
- [ ] No external audio assets are used.
- [ ] Footsteps play while moving.
- [ ] Alarms play on critical conditions.
- [ ] Drone sound plays when drone is near.
- [ ] Victory and defeat sounds play.

### Debug and Tests

- [ ] `window.__game` exposes all Section 8 calls.
- [ ] Every debug call returns plain data.
- [ ] `seed`, `start`, `step`, and `setTime` are deterministic.
- [ ] All Section 9 checks pass in order.
- [ ] `getState()` returns full plain data.
- [ ] Debug can set every major system, entity, and phase.

### Performance

- [ ] Simulation remains stable for at least 600 seconds.
- [ ] No unbounded growth in log, events, drones, or damage arrays.
- [ ] UI updates do not block simulation.
- [ ] Audio voices do not stack infinitely.
- [ ] Game remains playable at 60 frames per second on a normal browser viewport.

---

## A. SANITY

Checks made and results:

1. Every field a rule reads or writes is on a record.  
   Checked player health, suitO2, inventory, systems power/oxygen/pressure/radiation/reactorFuel/reactorCoolant, rescueProgress, rescueReady, shieldTimer, damage repairProgress, drone repairProgress/cooldown, container looted, event duration, score, repairs, itemsLooted, dronesDisabled, defeatReason, nextEventAt, lootQueue.  
   Result: closes.

2. Every place, thing, or kind a rule names is placed by a generator or listed in a roster.  
   Checked rooms, corridors, terminals, containers, damage kinds, item kinds, event kinds, drone, player, shield timer, storm, swarm. All are in Section 1.2, Section 4, or Section 8.  
   Result: closes.

3. For every consumable, the total the generators place against the total the rules can demand along the core loop closes.  
   Starting inventory gives 1 patch, 1 powerCell, 1 medkit, 1 o2Cartridge, and 1 wrench. Nineteen containers yield 38 items. Expected event demand over 600 seconds is about 14 events, with at most 5 breaches, 4 breakers, 3 coolant leaks, 4 radiation leaks, 2 storms, and 4 swarms. Patches needed are about 5, powerCells about 5, coolant/fuel about 8, medkits about 3, raduits about 3, o2Cartridges about 4. Generator supply plus starting inventory exceeds maximum expected demand.  
   Result: closes.

4. Every timing pair closes.  
   - Event spacing 40 to 50 seconds versus maximum travel plus repair: maximum station traversal is under 12 seconds at 5 tiles/second, repair is 1 to 2 seconds, so player can respond.  
   - Breach pressure drain 4 per second from 100 to 30 takes 17.5 seconds; patch travel plus 1-second repair is usually under 12 seconds, and player can use emergency O2/health if delayed.  
   - Radiation storm 20 seconds at +5 per second reaches 100 only without shield or raduit; health damage remains survivable if player uses shield or raduit.  
   - Reactor fuel 80 start plus fuel items can cover power-damaged intervals because fuel only drains when power is under 95.  
   - Suit oxygen drain at 8 per second from 100 to 0 takes 12.5 seconds; o2Cartridge and station oxygen recovery provide response time.  
   Result: closes.

5. Every call Section 9 makes is in Section 8.  
   Checked `seed`, `start`, `step`, `setTime`, `getState`, `setPlayer`, `setMove`, `setSystem`, `spawnDamage`, `interact`, `setRescue`, `setEvent`, `spawnDrone`, `setPlayerHealth`, `setSuitO2`, `useItem`, `setInventory`, `clearInventory`, `setLoot`. All appear in Section 8.  
   Result: closes.

6. Section and rule consistency fixes applied during review.  
   - First event moved to 50 seconds so early tests remain stable.  
   - Damage effects pause while the player is in range and has the required item, making pressure and breaker tests exact.  
   - Breaker spawn immediate power loss set to 10 and breaker repair immediate power gain set to 10, making breaker test exact.  
   - Reactor fuel drain gated to `power < 95`, making baseline stable and reactor fuel test exact.  
   - Shield made a 30-second terminal timer instead of an always-on system, making storm and radiation tests exact.  
   Result: closes.