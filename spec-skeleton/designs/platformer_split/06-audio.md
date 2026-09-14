# 6. AUDIO

All audio is generated with the Web Audio API. No external audio files are loaded.

Mixing:

- Music volume: 0.5.
- SFX volume: 0.7.
- UI volume: 0.8.
- Master limiter peak: -3 dB.
- Duck music by -6 dB during player hurt, boss warning, stage complete, and boss death.
- Avoid clipping.
- No long reverb tails.
- No harsh high-frequency spikes.

SFX priority:

| Priority | Event class |
| ---: | --- |
| 1 | Player hurt |
| 2 | Player death |
| 3 | Boss warning |
| 4 | Checkpoint |
| 5 | Tuner unlock |
| 6 | Core or heart pickup |
| 7 | Enemy death |
| 8 | Weapon fire |
| 9 | UI |

If multiple SFX trigger at once, play the highest priority. Lower priority events may be dropped.

SFX table:

| Sound name | Recipe | Rule that plays it |
| --- | --- | --- |
| uiConfirm | Square 880 Hz, 0.08 s, fast decay | UI confirm, title begin, stage select confirm |
| uiHover | Sine 1200 Hz, 0.03 s, gain 0.1 | Button hover |
| uiDeny | Square 110 Hz plus 120 Hz, 0.12 s, low buzz | Locked weapon select, invalid input |
| pauseIn | Sine 440 Hz to 220 Hz, 0.08 s | Pause opened |
| pauseOut | Sine 220 Hz to 440 Hz, 0.08 s | Pause closed |
| stageStart | Two-note motif, 0.6 s total; World 1: 220 Hz then 261.63 Hz; World 2: 440 Hz then 523.25 Hz | Stage start |
| playerJump | Sine 300 Hz to 600 Hz, 0.06 s, quick attack | Player jump |
| playerLand | Triangle 120 Hz, 0.08 s, lowpass | Player land |
| chirpFire | Square 900 Hz, 0.05 s, fast pop | Chirp fire |
| sifterFire | Three square pops 800, 900, 1000 Hz staggered 0.02 s, total 0.08 s | Sifter fire |
| lanceFire | Sawtooth 1200 Hz down to 200 Hz, 0.12 s | Lance fire |
| bloomFire | Sine 80 Hz plus filtered noise, 0.15 s, heavy pulse | Bloom fire |
| bloomSplit | Sine 1400 Hz to 1800 Hz, 0.10 s, bright chime | Bloom main split |
| playerProjectileHit | Square 1600 Hz, 0.05 s; small enemy pitch 1.2 times, medium 1.0 times, large 0.8 times | Player projectile hits enemy |
| playerHurt | Square 200 Hz, 0.12 s, short alarm | Player takes damage |
| playerDeath | Sawtooth 400 Hz down to 60 Hz, 0.5 s | Player death |
| checkpoint | Two sine notes 660 Hz then 990 Hz, 0.3 s | Checkpoint activated |
| coreCollected | Three sine notes 880, 1108, 1318 Hz over 0.25 s | Core collected |
| heartCollected | Sine 520 Hz plus 780 Hz, 0.2 s | Heart collected |
| tunerUnlock | Major arpeggio 440, 554, 659, 880 Hz over 0.6 s | Tuner collected and weapon unlocked |
| enemyDeathMite | Noise crunch plus square 150 Hz, 0.10 s | Mite Crawler death |
| enemyDeathDrone | Square 2000 Hz to 800 Hz plus sine 120 Hz, 0.20 s | Dredge Drone death |
| enemyDeathPincer | Square 300 Hz plus filtered noise, 0.30 s | Pincer Bot death |
| enemyDeathSentry | Sine 800 Hz down to 100 Hz, 0.30 s | Warden Sentry death |
| enemyDeathWraith | Sine 800 Hz down to 200 Hz, 0.40 s | Mist Wraith death |
| enemyDeathGolem | Sine 60 Hz plus filtered noise, 0.50 s | Bolt Golem death |
| bossWarning | Square 440 Hz and 554 Hz alternating, 0.5 s | Major boss attack warning or phase warning |
| bossPhaseChange | Phase 2: sine 880 Hz to 1320 Hz, 0.4 s; Phase 3: white noise burst plus sine 1320 Hz, 0.4 s | Boss phase change |
| bossDeath | Filtered noise explosion plus sine 200 Hz to 800 Hz, 0.8 s | Boss death |
| conduitComplete | Sine 300 Hz to 900 Hz, 0.7 s, clean rising sweep | Conduit activation and stage complete |

Music table:

| Music name | Recipe | Rule that plays it |
| --- | --- | --- |
| musicTitle | D minor, 72 BPM, slow sine pad on D2 and A2, sparse square motif every 2 beats, 8-bar loop | Title state |
| musicIntro | D minor, 68 BPM, minimal low sine drone, short narrative beeps every 4 beats | Intro state |
| musicMap | D major, 96 BPM, clean triangle pad, short square pickup every 4 beats | Signal Map state |
| musicW1 | D minor, 104 BPM, low bass pulse, metallic square stabs, filtered noise drips | World 1 stages 1 through 4 |
| musicW1Boss | E minor, 120 BPM, heavy square pulse, red-pulse bass, added high square arp in Phase 2 if T2 layering is active | World 1 boss stage |
| musicW2 | F major, 112 BPM, airy sine pads, lighter metallic percussion, wind noise | World 2 stages 1 through 4 |
| musicW2Boss | C minor, 126 BPM, layered sine tension, urgent square pulse in Phase 2, stripped bass and warning beeps in Phase 3 if T2 layering is active | World 2 boss stage |
| musicSummary | D major, 100 BPM, short resolution motif, 4 bars | Stage Summary state |
| musicGameOver | C minor, 60 BPM, low sine loss, slow pad decay | Game Over state |
| musicEnd | D major, 96 BPM, bright pad, rising sine motif, final resolution | End state |

Music transitions:

- Crossfade: 0.5 s.
- Stage start sting: 0.6 s.
- Boss start: music intensity rises.
- Boss death: music cuts, then resolution cue.
- Pause: music stops or ducks to 20 percent.
- Resume: 0.2 s fade in.
