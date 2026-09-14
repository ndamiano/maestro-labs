# 6. AUDIO

All audio is generated with the Web Audio API. No external audio files are required. Audio starts after a user gesture, usually the title button click.

General rules:

- Music sits below important SFX.
- No music stinger masks key pickup, gate creak, or The Hollow’s hunting cue.
- The Hollow’s state cues are slightly louder than the music bed.
- Ambient wind is subtle and never distracting.
- The final 60 seconds increase tension through pulse and texture, not volume spikes.
- Underbrush changes footstep texture, not noise disappearance.
- Sprinting sounds louder and more urgent than walking.
- The Hollow sounds slightly unnatural.

| Sound name | Web Audio recipe | Rule that plays it |
| --- | --- | --- |
| `music_night_bed` | Loop. Sine oscillator 55 Hz, low-pass noise wind 80 to 200 Hz, gain 0.35, slow LFO on filter cutoff. | Start on `run.start`. Stop on `hollow.wake` only if mystery layer is replaced, or stop on end states. |
| `music_mystery` | Loop. Sparse triangle notes 220 Hz and 262 Hz, each 1.2 seconds long, 4 seconds apart, gain 0.25, low-pass 1200 Hz. | Start on `run.start`. Stop on `hollow.wake`. |
| `music_pressure` | Loop. Low sawtooth 40 Hz with tremolo 0.25 Hz, muted noise pulse 80 Hz every 1.0 seconds, gain 0.40. | Start on `hollow.wake`. Stop on `dawn.warning` or end state. |
| `music_escape` | Loop. Sawtooth 80 Hz pulse every 0.5 seconds, warm triangle pad 110 Hz, gain 0.45, low-pass 1800 Hz. | Start on `dawn.warning`. Stop on end state. |
| `dawn_resolve` | One-shot. Triangle chord 262 Hz, 330 Hz, 392 Hz. 3 seconds attack, 4 seconds release, gain 0.65. | Play on `run.win`. |
| `caught_drone` | One-shot. Detuned sawtooth 55 Hz and 62 Hz. 0.5 seconds attack, 3 seconds decay, low-pass 400 Hz, gain 0.65. | Play on `run.fail.caught` after caught hit. |
| `ambient_wind` | Loop. Filtered noise, low-pass 120 Hz, gain 0.15, slow random LFO. | Runs during Playing. |
| `sfx_key_pickup` | Triangle. Two notes: 880 Hz then 1318 Hz. Each 0.12 seconds. 0.01 second attack, 0.25 second decay. Add short reverb tail 0.4 seconds. | Play on `pickup.key`. |
| `sfx_ember_pickup` | Filtered noise, band-pass 2000 to 6000 Hz, plus triangle sparkle 1800 Hz. 0.3 seconds duration. 0.01 second attack, 0.3 second decay. Warm low-pass 4000 Hz. | Play on `pickup.ember`. |
| `sfx_step_walk` | Low noise, band-pass 100 to 300 Hz. 0.1 seconds decay. Dry. | Play on `player.step` with type `walk` every 0.35 seconds while moving. |
| `sfx_step_sprint` | Low noise, band-pass 200 to 500 Hz. 0.08 seconds decay. Dry, sharper. | Play on `player.step` with type `sprint` every 0.20 seconds while moving. |
| `sfx_step_walk_underbrush` | Dry leaf rustle: filtered noise 400 to 1200 Hz. 0.12 seconds decay. Muffled but present. | Play on `player.step` with type `walk_underbrush` every 0.35 seconds while moving in underbrush. |
| `sfx_step_sprint_underbrush` | Crunchier rustle: filtered noise 600 to 1800 Hz. 0.10 seconds decay. Louder. | Play on `player.step` with type `sprint_underbrush` every 0.20 seconds while moving in underbrush. |
| `sfx_lantern_on` | Sine click 300 Hz plus short noise whoosh, low-pass 800 Hz. 0.2 seconds duration. 0.02 second attack, 0.2 second decay. | Play when lantern toggles on. |
| `sfx_lantern_off` | Noise hiss, low-pass 1200 Hz. 0.15 seconds duration. 0.02 second attack, 0.15 second decay. | Play when lantern toggles off. |
| `sfx_fuel_low` | Square tick 1200 Hz plus faint noise sizzle 3000 Hz. 0.15 seconds duration. 0.01 second attack, 0.15 second decay. | Play once when fuel crosses below 20. Reset when fuel increases back above 20. |
| `sfx_dawn_warning` | Rising triangle 220 Hz to 440 Hz over 0.8 seconds, gain 0.35. | Play once when dawn remaining crosses below 60 seconds. |
| `sfx_gate_ready` | Low sine hum 80 Hz, 0.5 seconds duration, 0.1 second attack, 0.4 seconds decay. | Play when prompt changes from locked to hold-to-open. |
| `sfx_gate_open` | Sawtooth 80 to 120 Hz with slow pitch bend over 1.5 to 3 seconds, plus low noise rumble 60 to 120 Hz. 2 seconds duration. 0.2 second attack, 2 seconds decay. | Play on `gate.open`. |
| `sfx_hollow_wake` | Detuned sawtooth 50 to 80 Hz. 8 seconds swell. Very low, distant, low-pass 500 Hz. | Play on `hollow.wake`. |
| `sfx_hollow_state` | Filtered noise 1500 to 4000 Hz, plus sine 700 Hz. 0.3 seconds duration. 0.05 second attack, 0.3 seconds decay. | Play on `hollow.state_change` except when entering Hunting. |
| `sfx_hollow_hunt` | Filtered noise 1500 to 4000 Hz, plus sine 1000 Hz. 0.4 seconds attack, 0.6 seconds decay. Cold, airy. | Play when `hollow.state_change` to Hunting. |
| `sfx_caught` | Dissonant cold hit: sawtooth 55 Hz and 62 Hz, plus noise burst 1000 Hz. 0.4 seconds duration. 0.01 second attack, 0.4 seconds decay. | Play on `run.fail.caught`. |
| `sfx_dawn_fail` | Quiet bright chord: triangle 262 Hz, 330 Hz, 392 Hz. 3 seconds attack, 4 seconds release. Wind and distant birds optional T2. | Play on `run.fail.dawn`. |
| `sfx_win` | Gentle dawn chord: triangle 262 Hz, 330 Hz, 392 Hz with warm sine 131 Hz. 3 seconds attack, 4 seconds release. | Play on `run.win`. |
| `sfx_breath_locked` | Exhausted gasp: filtered noise 800 to 1500 Hz. 0.3 seconds duration. 0.05 second attack, 0.3 seconds decay. | Play on `player.breath.locked`. |

Music layer mapping:

| Sim event | Audio action |
| --- | --- |
| `run.start` | Start `night_bed` and `mystery`. |
| `hollow.wake` | Stop `mystery`, start `pressure`, play `sfx_hollow_wake`. |
| `hollow.state_change` to Hunting | Play `sfx_hollow_hunt`. |
| `hollow.state_change` to other active states | Play `sfx_hollow_state`. |
| `player.fuel.low` | Play `sfx_fuel_low`. |
| `dawn.warning` | Start `escape`. |
| `gate.open` | Play `sfx_gate_open`. |
| `run.win` | Stop all loops, play `sfx_win`. |
| `run.fail.caught` | Stop all loops, play `sfx_caught`, then `caught_drone`. |
| `run.fail.dawn` | Stop all loops, play `sfx_dawn_fail`. |
