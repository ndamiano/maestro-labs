# 10. BUILD ORDER

| Milestone | Work | Section 9 check that proves it landed |
| --- | --- | --- |
| M0 Repository and boot | Create repo layout, index, canvas, main boot, fixed timestep | stateFlow.test.js Title no save |
| M1 Core player and tiles | Input, movement, collision, one-way, low clearance, conveyor, wind | physics.test.js and tilemap.test.js |
| M2 Weapons and projectiles | Weapon switching, fire cooldown, projectile spawn, tile collision, limits | weapon.test.js and projectile.test.js |
| M3 Enemies and activation | Enemy roster, activation, line of sight, death, World 2 modifiers | enemy.test.js |
| M4 Bosses and beams | Boss phases, attacks, telegraphs, death, conduit unlock | boss.test.js and bossDefeat.test.js |
| M5 Stages and validation | 10 stage files, stage factory, validator, stage content roster | stageLoad.test.js |
| M6 Progression and save | Session save, stage unlock, weapon unlock, core persistence, continue | progression.test.js, weaponProgression.test.js, coreProgression.test.js |
| M7 Checkpoints, death, pit | Checkpoint trigger, death reset, pit rule, game over | checkpointDeath.test.js and pit.test.js |
| M8 Pause and state screens | Pause, summary, game over, end, map transitions | pause.test.js and stateFlow.test.js |
| M9 Presentation and HUD | Canvas rendering, HUD, crosshair, VFX, audio | stageLoad.test.js 5-second idle plus screenshot rows S06 through S09 |
| M10 Full proof | Completion bot, full game, all cores | stageCompletionProof.test.js, fullGame.test.js, allCores.test.js |
