# 6. AUDIO

Carried architecture (engineering §24, ruled in 0.2): **all audio is generated with the Web Audio API at runtime — no asset files.** `AudioManager` (SFX) and `MusicManager` (music) are created only after the user's start-gesture on the title screen (autoplay policy). `play(name, {pan})` with pan clamped −1..1 (pan is T2); missing recipe → console warning, no crash. The simulation emits event names (2.3); audio consumes them and never alters gameplay.

## 6.2 Music — Tier: T2

Identity (carried): a failing station — sparse, mechanical, industrial, tense but controlled; not orchestral, not cinematic hero music, not constant panic. Key **D minor**; base tempo **72 BPM**; final phase **90 BPM**. State-driven layers, **0.5 s** gain crossfades; music always sits below SFX; warnings always audible above music; stingers short; reactor/final layers build rather than panic; success feels like escape, not celebration noise.

| Layer | Recipe (Web Audio synthesis) | Trigger | Mix note |
| --- | --- | --- | --- |
| `base` | D2 sine 73.4 Hz (g 0.05) + D3 sawtooth 146.8 Hz through lowpass 400 Hz (g 0.03); low pulse: sine 36.7 Hz, 100 ms, A 2 ms / R 80 ms, every 0.833 s (72 BPM), g 0.06; faint bandpass noise (800 Hz) loop at g 0.01 | Always during gameplay | −18 to −22 LUFS equivalent |
| `low_o2` | Bandpass noise (1–2 kHz), 600 ms cycle, gain LFO 1 Hz; added to base | Player O2 below 25 | duck base 20% |
| `critical_o2` | Bandpass noise (2–4 kHz), 500 ms cycle, gain LFO 2 Hz; replaces `low_o2` | Player O2 below 10 | keep below SFX warnings |
| `power_loss` | Remove the low pulse; sparse dissonant pad: D2 73.4 + F2 87.3 sines, 2 s decay each cycle, g 0.04 | Major power loss (event `power_loss`) | subtle, not alarm |
| `reactor` | Deep sub drone: sine 55 Hz (g 0.07) + 82.4 Hz (g 0.04), slow 0.1 Hz amplitude LFO; 72 BPM pulse resumes | Reactor online | add depth, not excitement |
| `coolant_low` | Tick texture: sine 1000 Hz, 80 ms, 4 per bar, with 8-bar rising filter cutoff 300→2000 Hz | Coolant below 30 s | do not overpower the `coolant_low` SFX |
| `final_countdown` | Base at **90 BPM** (0.667 s pulse); rising pad adds A2 110 Hz and C3 130.8 sines each +3 dB per 16 bars, capped | Time to de-orbit below 120 s | urgent but controlled |
| `success` (theme) | D-major chord: sines 293.7 / 349.2 / 440 / 587.3 Hz, 4 s, A 0.5 / R 2.5, g 0.12; soft engine rumble (lowpass 250 Hz noise) under it | Launch success | replaces everything; quiet resolve |
| `failure` (theme) | Detuned drone: sines 110 + 116 Hz, 4 s fade; three fading square alarm pulses 440/330 Hz, 200 ms each, 600 ms apart, gains 0.10/0.07/0.04 | Failure | replaces everything; melancholic, not punitive |

The drone-alert stinger is the `drone_alert` SFX (6.3) — no separate music asset.

## 6.3 SFX — Tier: T1

Recipe notation: `waveform f Hz (sweep to f2 over t), duration, envelope A/D/S/R, gain g, [LFO rate on gain], [filter]`. One-shot unless marked LOOP.

| Name | Recipe | The rule that plays it |
| --- | --- | --- |
| `ui_select` | sine 1200 Hz, 40 ms, A 2 / R 30, g 0.2 | Slot selection (1–6) or button press |
| `ui_error` | square 200 Hz, 80 ms, hard stop, g 0.25 | Invalid action: full inventory, invalid item use, `reactor_spinup_aborted` |
| `pickup` | sine sweep 700→1000 Hz, 60 ms, A 2 / R 20, g 0.3 | Item picked up |
| `drop` | sine 180 Hz, 100 ms, A 1 / R 60, lowpass 400 Hz, g 0.3 | Item dropped |
| `use_o2` | bandpass noise (2–4 kHz) 0.35 s, g 0.15, plus sine 880 Hz 80 ms A 2 / R 40 g 0.2 | O2 Tank used |
| `use_medkit` | sine 1400 Hz, 60 ms, A 2 / R 40, g 0.25 | Medkit used |
| `repair_start` | square 320 Hz 30 ms + 10 ms noise click, g 0.2 | Channel starts (any repair/channel) |
| `repair_tick` | sine 1000 Hz, 25 ms, g 0.15 | Channel hits 25 / 50 / 75% |
| `repair_complete` | triangle 260 Hz 80 ms (thud) + sine 1200 Hz 50 ms blip, g 0.3 | Repair completes; also coolant application (`reactor_coolant_applied`, ruling 0.2) |
| `door_open` | sawtooth sweep 120→300 Hz, 300 ms, g 0.25, + sine 90 Hz 60 ms thud at end | Door opens |
| `door_close` | sawtooth sweep 300→120 Hz, 300 ms, g 0.25, + thud | Door closes |
| `door_jammed` | square 90 Hz, 120 ms × 2, gain LFO 8 Hz (rattle), lowpass 500 Hz, g 0.25 | Interaction with a jammed door before repair |
| `door_repair` | triangle 200 Hz 100 ms clank + sawtooth 150→250 Hz 200 ms servo, g 0.3 | Jammed door repaired |
| `hull_patch` | bandpass noise (1–3 kHz, descending) 0.5 s g 0.2 + clank (triangle 200 Hz 100 ms) at 0.4 s | Hull patch or breach seal completes |
| `power_install` | sine sweep 100→400 Hz 400 ms, g 0.25, then 400 Hz steady 50 ms | Power cell installed |
| `power_cell_expire` | sawtooth 400→80 Hz, 500 ms, g 0.25, + 100 Hz click at end | A timed source expires |
| `power_loss` | square 60 Hz 400 ms g 0.3 + lowpass (200 Hz) noise burst 100 ms | Any room loses power |
| `breach` | sawtooth 1200→300 Hz 0.4 s (shriek) + bandpass (2–5 kHz) noise whoosh 0.6 s g 0.3 + sine 55 Hz rumble 0.8 s g 0.3 | Room becomes breached |
| `hull_event_warning` | square 440 Hz 150 ms + square 330 Hz 150 ms (300 ms total), g 0.3 | Hull event warning first appears |
| `deorbit_warning` | sine 392 Hz 200 ms + sine 330 Hz 200 ms (400 ms total), g 0.35 | Time to de-orbit enters below 120 s |
| `drone_activate` | square chirps 880 / 1100 / 1320 Hz, 60 ms each, 40 ms gaps + 100 ms servo noise, g 0.25 | Drone first activates |
| `drone_alert` | square 990 Hz, 80 ms × 2, 40 ms gap, g 0.25 | Drone enters alert state |
| `drone_attack` | highpass (2 kHz) noise crackle 80 ms, gain LFO 30 Hz, + square 150 Hz 40 ms, g 0.4 | Drone deals 20 damage |
| `emp` | sine sweep 200→2000 Hz 300 ms g 0.3 + 50 ms noise zap | EMP channel completes |
| `coolant_low` (LOOP) | sine 1400 Hz, 500 ms cycle, gain LFO 1 Hz (A 100 / R 100 ms per cycle), g 0.15 | Warning `coolant_low` active (below 30 s); stop on exit |
| `coolant_expired` | sine 60 Hz thud 300 ms + square 660 Hz alarm 200 ms, g 0.4 | Coolant reaches 0 |
| `reactor_spinup` | sawtooth 60→180 Hz sweep over 2 s, lowpass 800 Hz, g 0.3 | Spin-up channel starts |
| `reactor_online` | sine 55 Hz thud 200 ms + fifth 165 Hz 400 ms decay, g 0.4 | Reactor comes online |
| `reactor_heat` (LOOP) | bandpass noise (800–1500 Hz), 400 ms cycle, gain LFO 0.8 Hz, g 0.12 | Heat hazard active; stop when hazard ends |
| `o2_low` (LOOP) | bandpass noise (3–5 kHz), 600 ms cycle, gain LFO 1 Hz, g 0.12 | Player O2 below 25; stop on exit |
| `o2_critical` (LOOP) | bandpass noise (3–5 kHz), 500 ms cycle, gain LFO 2 Hz, g 0.18 | Player O2 below 10; stop on exit |
| `integrity_low` (LOOP) | sine 70 Hz thump, 500 ms cycle, gain LFO 1 Hz, lowpass 300 Hz, g 0.2 | Integrity below 25; stop on exit |
| `integrity_critical` (LOOP) | sine 70 Hz thump, 250 ms cycle, gain LFO 2 Hz, lowpass 300 Hz, g 0.25 | Integrity below 10; stop on exit |
| `objective_complete` | sine 880→1320 Hz, 100 ms, g 0.2 | Main objective completes |
| `launch_requirement` | sine 1000 Hz 60 ms + sine 1200 Hz 60 ms, g 0.2 | A launch checklist row becomes true |
| `launch_reset` | sine 600→200 Hz, 300 ms, g 0.3 | Launch progress resets (with the specific reason) |
| `launch_tick` | sine 900 Hz, 20 ms, g 0.08 | Launch channel hits every 10% |
| `launch_success` | lowpass (300 Hz) noise rumble 2 s g 0.25 + major chord sines 261.6 / 329.6 / 392 / 523.3 Hz, 1.5 s, A 0.2 / R 1.0, g 0.3 | Launch channel reaches 100% |
| `game_over` | sines 110 + 116 Hz (detuned drone) 3 s fade g 0.25 + three fading square alarm pulses 440/330 Hz 200 ms, 600 ms apart, g 0.15/0.10/0.05 | Failure occurs |

Loop management (carried from engineering 24.4): loops start when their warning enters active and stop when it exits; if `o2_critical` activates, stop `o2_low`; if `integrity_critical` activates, stop `integrity_low`. One-shot list: `breach`, `power_loss`, `power_cell_expire`, `hull_event_warning`, `deorbit_warning`, `launch_reset`, `drone_activate`, `drone_alert`, `drone_attack`, `coolant_expired`, `reactor_online`, `game_over`, `launch_success` (plus the action one-shots above). Warning audio fires on transition only, never per tick.

## 6.4 Event names (the contract)

Simulation event → audio mapping is complete in `src/data/audioEvents.js`; the audio names are exactly the 6.3 roster: `ui_select`, `ui_error`, `pickup`, `drop`, `use_o2`, `use_medkit`, `repair_start`, `repair_tick`, `repair_complete`, `door_open`, `door_close`, `door_jammed`, `door_repair`, `hull_patch`, `power_install`, `power_cell_expire`, `power_loss`, `breach`, `hull_event_warning`, `coolant_low`, `coolant_expired`, `drone_activate`, `drone_alert`, `drone_attack`, `emp`, `o2_low`, `o2_critical`, `integrity_low`, `integrity_critical`, `reactor_spinup`, `reactor_online`, `reactor_heat`, `deorbit_warning`, `objective_complete`, `launch_requirement`, `launch_reset`, `launch_tick`, `launch_success`, `game_over`.

Positional audio (T2, carried from visual §12): drone sounds pan by drone screen position; machine sounds pan by machine position; a breach in the current room is center-loud; a breach in an adjacent room is quieter and panned toward that room; dropped items have no positional audio; no complex reverb.
