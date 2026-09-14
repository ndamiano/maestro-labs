# 6. AUDIO

All audio is **generated with the Web Audio API at runtime; no external audio asset files are loaded** (§0.2 ruling). `audioManager` unlocks on the **Begin Salvage** gesture, maps events to sounds via the table below, and limits one-shot SFX to **8 simultaneous** (priority: 1 key, 2 vault, 3 tide, 4 cache, 5 coin, 6 movement, 7 UI; overflow drops lowest priority). World SFX pan by screen position; UI and tide-dial sounds are centered. Missing/no assets never crash (synth is the only path).

**SFX table — one row per event named by gameplay's rules and visual's feedback:**

| Sound | Recipe (waveform · frequency · duration · envelope) | Rule that plays it |
| --- | --- | --- |
| `key` | triangle+sine sweep 660→990 Hz (0.15 s) · lowpass 4000 Hz · 0.60 s · gain 0.35 → exp 0.001 | on `key_collected` |
| `coin` | square · random 1200–1800 Hz · lowpass 3000 Hz · 0.12 s · gain 0.18 → exp 0.001 | on `coin_collected` |
| `cache_sealed` | sine 120 Hz + square click 900 Hz (0.03 s) · lowpass 800 Hz · 0.35 s · gain 0.25 → exp 0.001 | on `cache_sealed_prompt` (once per attempt/visibility entry) |
| `cache_opened` | filtered sawtooth creak 200→90 Hz + sine thud 80 Hz · 0.5 s · gain 0.3 → exp 0.001 | on `cache_opened` for Keys 1, 2, 5 |
| `rope_pulled` | filtered sawtooth creak 160→70 Hz + 3× square 400 Hz ratchet (0.02 s) · 1.0 s · gain 0.28 → exp 0.001 | on `cache_opened` for Key 3 |
| `column_moved` | low noise burst, lowpass 800→120 Hz (1.4 s) + sine rumble 50 Hz · 1.5 s · gain 0.25 → exp 0.001 | on `cache_opened` for Key 4 |
| `tide_warning` | two sine gongs 180 Hz then 150 Hz (0.10 s apart) + short echo · lowpass 900 Hz · 0.8 s · gain 0.22 → exp 0.001 | on `tide_warning` |
| `low_tide` | noise swell desc (bandpass 600→200 Hz) + sine chime 880 Hz (0.15 s) · 0.7 s · gain 0.25 → exp 0.001 | on `tide_state_changed` → LOW |
| `high_tide` | noise swell asc (bandpass 200→600 Hz) + sine gong 110 Hz (0.3 s) · 0.7 s · gain 0.25 → exp 0.001 | on `tide_state_changed` → HIGH |
| `vault_locked` | sine 70 Hz + square 140 Hz (0.05 s) · 0.5 s · gain 0.3 → exp 0.001 | on vault prompt "Locked. Requires 5/5" (once per visibility entry) |
| `vault_opening` | low rumble (lowpass 300→80 Hz) + brass bell 520/660 Hz (0.4 s) + water drain (bandpass 400→100 Hz) · 1.2 s · gain 0.35 → exp 0.001 | on `vault_opened` |
| `game_complete` | D-major-pentatonic marimba/brass arpeggio D5–A5–D6 (3×0.15 s) + gull cry (sawtooth 900→400 Hz, 0.4 s) · 2.0 s · gain 0.4 → exp 0.001 | on `game_complete` |
| `landmark` | paper stamp (noise 0.05 s) + small bell sine 1046 Hz (0.1 s) · 0.4 s · gain 0.25 → exp 0.001 | on `landmark_discovered` |
| `clue` | compass tick square 1200 Hz (0.03 s) + chart swish (noise 0.2 s) · 0.5 s · gain 0.22 → exp 0.001 | on `geometric_clue_added` |
| `safe_displacement` | air whoosh (noise 200→2000 Hz, 0.15 s) + splash (bandpass 800 Hz, 0.2 s) · 0.4 s · gain 0.25 → exp 0.001 | on `safe_displacement_occurred` |
| `footstep_dry` | lowpass noise thud (lowpass 400 Hz) · 0.08 s · gain 0.12 → exp 0.001 | once per tile entered while dry (depth ≤ 0) |
| `footstep_shallow` | bandpass noise slosh (500 Hz) · 0.10 s · gain 0.14 → exp 0.001 | once per tile entered while shallow (0 < depth ≤ 1.0) |
| `swim_loop` | continuous lowpass water noise (lowpass 600 Hz) · looping · gain 0.20, linear ramp 0↔0.20 over 0.2 s | active while depth > 0; stops when dry |
| `ui_hover` | sine 1600 Hz · 0.05 s · gain 0.1 → exp 0.001 | on UI hover |
| `ui_click` | filtered square 600 Hz (lowpass 2000 Hz) · 0.08 s · gain 0.15 → exp 0.001 | on UI press (Begin Salvage, Restart) |
| `map_open` | noise sweep up 200→4000 Hz · 0.2 s · gain 0.18 → exp 0.001 | on `map_opened` |
| `map_close` | noise sweep down 4000→200 Hz · 0.18 s · gain 0.18 → exp 0.001 | on `map_closed` |

All one-shots: quick attack, clean decay, no sharp peaks. Design rules: key bright/unmistakable; coin small/satisfying; tide watery not alarming; vault heavy/ceremonial; interactions match material (rope creak, stone grind, wood creak, brass chime).

**Music (Web Audio generative layers, D-major pentatonic D·E·F#·A·B, base 84 BPM):**

| Layer | Recipe (waveform · frequency/pattern) | Level | Purpose / adaptive rule |
| --- | --- | --- | --- |
| Sea bed | filtered noise + low sine ~55 Hz | −18 dB | constant ocean presence (start + always) |
| Percussion | wood block/shaker/soft kick at 84 BPM | −16 dB | exploration; −30% in shallow; ducks in deep-blocked |
| Melody | marimba/celesta/muted guitar, D-pentatonic | −12 dB | main exploration; very soft on start screen |
| Tide accent | water wash / low swell | −14 dB | rises with tide state (low→bright celesta ostinato; rising→swells; high→low marimba pulse ~slower feel) |
| Stinger | brass/marimba motif | −6 dB | key (3-note), vault (heavy bell+marimba), completion (2-s fanfare+gull) |

Adaptive state rules: start screen = sea bed + distant gull + very soft melody; dry exploration = full percussion+melody; shallow = percussion −30% + water wash up; deep-blocked = music ducks + low swell; low tide = + bright celesta ostinato; rising = + soft swells; high = + low marimba pulse; vault ready = slow bell pulse at 60 BPM for ~10 s; vault opening = heavy bell+marimba hit; game complete = 2-s light fanfare + gull cry. **Sector motifs (T2), <1 s each:** Driftwood Cove D→A; Gull Flats F#→B; Palm Hollow A→B; Sunken Ruins low D→F#; Cliffpath Ridge high B→A; Vault Point D→B (+bell). **Mixing:** music −12 dB, SFX −6 dB, UI −10 dB, water loop −14 dB, stingers −6 dB; duck music 3 dB when important SFX play; keep SFX clearer than music; never let water overpower key/vault. *(Music is T1 = sea bed + stingers; T2 = full adaptive layers + motifs, §0.3.)*
