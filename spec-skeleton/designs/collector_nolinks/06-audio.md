# 6. AUDIO

All audio is **generated with the Web Audio API** from `src/audio/recipes.js` (no audio files). Master chain: `musicGain (0.7)`, `sfxGain (0.8)`, `ambienceGain (0.5)` → master; settings adjust 0–1. Audio context resumes on first user interaction (autoplay policy). Short SFX use playback-rate variation 0.98–1.02 to avoid mechanical repetition; stingers (rows 23–26) are never rate-varied. Recipes below are the exact build spec: `osc` = OscillatorNode (waveform, f0→f1 over duration), `noise` = white-noise buffer through the filter; envelope = attack (A) / release (R) on a GainNode.

| # | Sound | Recipe (Web Audio) | Duration | Rule that plays it |
| --- | --- | --- | ---: | --- |
| 1 | ui_hover | osc sine 1200→1100Hz, A 0.001, R 0.01, g 0.03 | 20ms | Any UI hover (buttons/tabs/rows) in any modal or HUD |
| 2 | ui_click | osc square 1800→1600Hz, A 0.001, R 0.01, g 0.05 | 30ms | Any confirmed UI click (buy, sell, assign, tab, place…) |
| 3 | ui_open | noise bandpass 400→1200Hz, g 0.06 | 80ms | Modal opens (shop, ledger, settings, completion) |
| 4 | ui_close | noise bandpass 1200→400Hz, g 0.06 | 80ms | Modal closes |
| 5 | invalid | osc square 220→180Hz through lowpass 800Hz, A 0.002, R 0.02, g 0.08 | 100ms | `invalid:action` (failed buy/place/toggle/etc.) |
| 6 | inventory_full | osc sine 120→80Hz, A 0.005, R 0.03, g 0.10 | 80ms | Gather/catch attempted while `canHold(1)` false (`Bag Full`) |
| 7 | footstep_grass | noise highpass 2000Hz, g 0.04 | 40ms | `player:stepped` surface `grass` (grass, berry_grove, path) |
| 8 | footstep_stone | noise bandpass 1000Hz, g 0.05 | 50ms | `player:stepped` surface `stone` (ore ground, interior floors) |
| 9 | water_step | osc sine 300→180Hz, g 0.06 + noise blip bandpass 900Hz g 0.03 | 80ms | `player:stepped` surface `water` (any water tile) |
| 10 | berry_pick | noise highpass 2000Hz g 0.06 (30ms) + osc sine 880→1320Hz g 0.10, A 0.002, R 0.03 | 80ms | `resource:collected` where nodeType = berry |
| 11 | ore_mine | noise bandpass 900Hz g 0.10 (60ms) + osc sine 90Hz g 0.12, A 0.002, R 0.04 | 100ms | `resource:collected` where nodeType = ore |
| 12 | fish_cast | noise bandpass 600→1400Hz g 0.05 (120ms) + plop osc sine 400→250Hz g 0.07 at end | 120ms | `fish:cast` |
| 13 | fish_bite | osc sine 300→200Hz g 0.08 (40ms) + noise blip bandpass 800Hz g 0.05 | 80ms | `fish:bite` |
| 14 | fish_catch | noise bandpass 1200Hz, pitch-slide −30%, g 0.12 (180ms) + chime osc sine 1320→1760Hz g 0.10, A 0.005, R 0.12 | 250ms | `fish:catch` |
| 15 | fish_fail | noise bandpass 700Hz g 0.08 (120ms) + osc sine 160→120Hz g 0.08 | 150ms | `fish:fail` |
| 16 | coin_sale | osc square 1400→1900Hz g 0.12 (80ms) + jingle sines 2200Hz/2700Hz offset 30ms g 0.05 (70ms) | 150ms | `shop:sold`, `shop:allSold` |
| 17 | coin_buy | osc sine 1200→1600Hz g 0.08, A 0.005, R 0.03 | 100ms | `shop:bought` (tool or furniture) |
| 18 | furniture_place | noise lowpass 600Hz g 0.10 (40ms) + osc sine 200→150Hz g 0.10 | 80ms | `furniture:placed` |
| 19 | furniture_remove | osc sine 500→300Hz g 0.06, R 0.02 | 60ms | `furniture:removed` |
| 20 | furniture_sell | osc sine 1400→1900Hz g 0.08 (60ms) + noise highpass 3000Hz g 0.05 | 120ms | `furniture:sold` |
| 21 | specimen_assign | sines 1568Hz + 2093Hz, A 0.005, R 0.15, g 0.09 | 200ms | `specimen:assigned` |
| 22 | specimen_unassign | sines 1047Hz + 1319Hz, A 0.005, R 0.10, g 0.07 | 150ms | `specimen:unassigned` |
| 23 | goal_complete | osc sine 523→784Hz g 0.12, A 0.02, R 1.2 + chord sines 659/880Hz g 0.05 at t+0.1s (1.5s) | 2s | `goal:completed` |
| 24 | shop_unlock | sines 659/880/1318Hz, A 0.01, R 0.4, g 0.06 each | 800ms | `shop:tierUnlocked` |
| 25 | museum_unlock | osc sine 440→660Hz g 0.09 (400ms) + noise highpass 4000Hz g 0.03 | 800ms | `museum:unlocked` |
| 26 | final_completion | pad sines 330/440/550/660Hz, A 0.5, R 3, g 0.08 + celesta arpeggio sines 1046/1318/1568Hz (8 notes, 0.5s apart, g 0.07) | 6s | `completion:completed` |

Music (generated loops; keys stay in the related family E major / A minor / C# minor / D major; no dissonant cuts; crossfades 1s zone-to-zone, 1s world-to-interior, 0.5s layer add/remove):

| Sound | Recipe (Web Audio) | Rule that plays it |
| --- | --- | --- |
| music_title | pad sines E3/G#3/B3 (165/208/247Hz) g 0.05 + pluck pattern (sine, fast R) 8th notes, 76 BPM | Title screen |
| music_village | pad E major (165/208/247) g 0.05 + marimba motif (sine, R 0.15) 8ths, 84 BPM | Biome `Village` |
| music_berry_grove | pad A minor (110/131/165) g 0.05 + ocarina melody (sine + 5Hz vibrato), 80 BPM | Biome `Berry Grove` |
| music_ore_ridge | pad D major (147/185/220) g 0.05 + low strings (detuned saw, lowpass 500Hz) + kalimba (triangle) 8ths, 76 BPM | Biome `Ore Ridge` |
| music_lakeside | pad A minor (110/131/165) g 0.05 + harp arpeggio (sine, R 0.4), 72 BPM | Biome `Lakeside` |
| music_home | piano-like triangles (chord + sparse melody), 72 BPM, g 0.06 | Scene `home` |
| music_museum | strings pad (detuned saw, lowpass 800Hz) + celesta sines, 74 BPM, g 0.06 | Scene `museum` |
| layer_shop (T2) | soft wood ticks: sine 800Hz, 30ms, 8/8, g 0.03 | Shop modal open |
| layer_build (T2) | kalimba tick: triangle 1046Hz, 40ms, sparse, g 0.03 | Build mode active |
| amb_village (T2) | pink-ish noise lowpass 400Hz g 0.02 + bird blips (sine 2200→2600, 60ms) every 4–8s | Biome `Village` |
| amb_berry (T2) | noise bandpass 3000Hz g 0.015 + insect chirp pattern | Biome `Berry Grove` |
| amb_ore (T2) | noise lowpass 250Hz g 0.02 + rare stone tap (rows 11-style, 10% gain) | Biome `Ore Ridge` |
| amb_lake (T2) | noise bandpass 500Hz, gain LFO 0.2Hz, g 0.02 + soft lap blips | Biome `Lakeside` |
| amb_home (T2) | noise lowpass 150Hz g 0.015 + lamp hum sine 120Hz g 0.01 | Scene `home` |
| amb_museum (T2) | noise lowpass 300Hz g 0.012 | Scene `museum` |

Stingers (goal/shop/museum/final) are SFX rows 23–26 playing over current music; no separate music-stinger files.
