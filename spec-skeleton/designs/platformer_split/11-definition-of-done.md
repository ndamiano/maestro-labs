# 11. DEFINITION OF DONE

| Requirement from 0.1 | Done checks | Screenshot rows |
| --- | --- | --- |
| Make a side-scrolling, platformer shooter | Player moves, jumps, shoots; stage scrolls; 10 stages simulate; all stages complete by bot | S06, S07 |
| At least 4 different gun types | Chirp, Sifter, Lance, Bloom exist; all unlock correctly; weapon tests pass | S07 |
| Character can move left or right | Input left and right change velocity; physics test passes | S07 |
| Character can jump | Jump sets -640; variable cut sets -320; coyote and buffer work | S07 |
| Character can crouch | Crouch changes hitbox to 16 x 12; crouch speed 120; low clearance passable | S07 |
| Story progression like Mario with worlds and stages | 2 worlds and 10 stages exist; sequential unlock works; final completion reaches End | S04, S05, S13 |
| Start with 2 worlds | World 1 and World 2 panels exist; World 2 lock works | S04, S05 |
| 5 stages per world, 10 total | All 10 stage files load and pass validator | S04 |
| Do not simply copy Mario | Signal Courier theme, enemy roster, boss identity, no Mario visual vocabulary | S01, S06, S09 |
| Added: 2D gameplay with 2.5D presentation | Gameplay is 2D; parallax is presentation only; no gameplay depth | S06 |
| Added: named player, enemies, bosses, and stage identity | Courier Jex, 6 enemies, 2 bosses, 10 named stages render and simulate | S06, S09 |
| Added: checkpoints, pits, hazards, and stage reset | Checkpoint, pit, death reset, and boss reset tests pass | S07, S10, S12 |
| Added: optional cores for completion stats | 30 cores placed; allCores test passes; total counter updates | S07, S11, S13 |
| Added: HUD, crosshair, damage feedback, and state screens | HUD table fields update; crosshair and vignette behave; state tests pass | S07, S08, S10, S11, S12, S13 |
| Added: generated Web Audio sound and music | Audio.js generates SFX and music; no external audio files; event rules fire | S06, S09, S11 |
| Added: deterministic simulation and testable build | `npm test` passes; fixed timestep; deterministic RNG; all section 9 checks pass | S13 |
