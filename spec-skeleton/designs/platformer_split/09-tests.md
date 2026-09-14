# 9. TESTS

Run tests with:

```bash
npm test
```

Tests run in Node without a browser. Tests use headless game, input proxy, memory save, and completion bot. Unit tests may call pure utility exports directly. Every `game.debug` call in this section exists in section 8.

## 9.1 Unit Tests

| Test file | System | Check | Debug calls | Expected state |
| --- | --- | --- | --- | --- |
| math.test.js | Math | Clamp, lerp, angle difference, normalize, rect overlap, point in rect, LOS sampling | None | Pure helpers return expected values |
| rng.test.js | RNG | Same seed produces same sequence; different seed produces different sequence; output range is 0 to 1 exclusive | `debug.setRngSeed(101)`, `debug.getRngSeed()` | Deterministic sequence |
| save.test.js | Save | New progression unlocks only w1s1; completing w1s1 unlocks w1s2; completing w1s5 unlocks World 2; Continue returns furthest unlocked uncompleted stage; reset clears progress; unavailable storage falls back to memory | `debug.resetProgression()`, `debug.setStageCompleted("w1s1", true)` | Correct unlock and continue behavior |
| input.test.js | Input | Primary and alternate keys map; jump edge works; mouse updates; mouse leave stops mouse shooting; J still shoots after mouse leave; weapon select works; cycle only unlocked | `debug.pressJump()`, `debug.selectWeapon(2)`, `debug.setMouseInside(false)`, `debug.setMouseWorld(100, 100)` | Input flags correct |
| physics.test.js | Player movement | Ground acceleration reaches 240; air acceleration slower; friction stops; crouch max 120; jump sets -640; coyote 0.09; buffer 0.10; jump cut -320; gravity 1800; max fall 1100; updraft -2400 clamp -420; horizontal wind clamp plus or minus 360; conveyor plus or minus 120 clamp plus or minus 360; one-way landing; one-way pass-through; moving platform carry; low clearance blocks standing; low clearance allows crouch | `debug.loadStage("minimalStage")`, `debug.setPlayerVel(0, 0)`, `debug.setKeys({ right: true })`, `debug.pressJump()`, `debug.advance(1000)`, `debug.setPlayerCrouch(true)` | Player velocity, position, and grounded state match rules |
| tilemap.test.js | Tilemap | Parsing creates correct solid, one-way, spike, conveyor arrays; solid query; one-way top; spike query; conveyor offset | `debug.loadStage("weaponTestStage")`, `debug.advance(16)` | Tile queries correct |
| player.test.js | Player | Standing hitbox 16 x 24; crouch 16 x 12; crouch preserves feet; standing blocked by clearance; muzzle lowers when crouched; muzzle X offset horizontal; damage 1 heart; invulnerability prevents damage; knockback from source; death with lives respawns; death with zero lives Game Over; pit full hearts respawns; pit 1 heart death; checkpoint sets respawn; checkpoint restores 1 heart | `debug.damagePlayer(0, 0)`, `debug.setPlayerInvuln(1.0)`, `debug.setPlayerHearts(1)`, `debug.advance(1000)`, `debug.activateCheckpoint()` | Player hearts, lives, position, and invulnerability match rules |
| weapon.test.js | Weapons | Chirp one projectile damage 7 speed 950 lifetime 0.7 radius 4; Sifter 5 pellets spread; Lance pierces 3 distinct enemies; Lance does not hit same enemy twice; Bloom splits on enemy hit; Bloom splits on lifetime; Bloom does not split on tile hit; shards damage 6 lifetime 0.5 speed 620; switch cooldown 0.12; locked weapon deny; cycle skips locked | `debug.loadStage("weaponTestStage")`, `debug.giveAllWeapons()`, `debug.selectWeapon("chirp")`, `debug.spawnPlayerProjectile("chirp", 0, 0, 1, 0)`, `debug.advance(100)`, `debug.selectWeapon("sifter")`, `debug.setSwitchCooldown(0.12)` | Projectiles and cooldowns match weapon tables |
| projectile.test.js | Projectiles | Player projectile destroys on solid tile; passes one-way; enemy projectile destroys on solid; lifetime expires; no owner damage; high-speed substeps; Lance pierce ID set; Bloom split; Echo bounce once; projectile limits expire oldest | `debug.spawnPlayerProjectile("lance", 0, 0, 1, 0)`, `debug.spawnEnemyProjectile("echo", 0, 0, 100, 0, 6, 1, 2.0)`, `debug.advance(1000)`, `debug.clearProjectiles()` | Projectile lifecycle and limits match rules |
| enemy.test.js | Enemies | Activation radius 320; max 16 active; closest activate; World 2 HP ceil base times 1.15; World 2 projectile speed times 1.1; Mite moves within 5 tiles and waits 0.5 blocked; Drone patrols 4 tiles and fires 1.6; Pincer telegraph 0.5 and charge stops; Sentry aims 3 rad/s and bursts within 10 degrees; Wraith phases 2.5 and 0.8; phased blocks damage; Golem stomp spikes; Golem death heart; death clears enemy projectiles | `debug.loadStage("minimalStage")`, `debug.spawnEnemy("mite", 100, 100)`, `debug.activateBoss()`, `debug.setEnemyHp("mite", 4)`, `debug.advance(1000)` | Enemy state and damage match roster |
| boss.test.js | Bosses | Hush phase at 60 percent; charge leaves 4 spikes; fan bolt 3 projectiles; Phase 2 enables sweep beam; drone summon max 3; Hush death unlocks conduit after 2 s; Null phases at 70 and 35; Phase 2 warning 1.5; Echo bounce once; Wraith summon max 4; Phase 3 overload alternates beams and core exposed; core exposed damage times 1.5; Null death unlocks conduit after 3 s; boss reset on player death | `debug.loadStage("bossTestStage")`, `debug.activateBoss()`, `debug.damageBoss(180)`, `debug.setBossHp(100)`, `debug.advance(2000)` | Boss phase, attacks, death, and conduit unlock match rules |
| progression.test.js | Progression | Start unlocks Chirp only; Sifter tuner unlocks Sifter; Lance tuner unlocks Lance; Bloom tuner unlocks Bloom; cores persist; collected cores not spawned; stage completion unlocks next; final completion marks complete | `debug.unlockWeapon("sifter")`, `debug.setCoreCollected("w1s1-core-1", true)`, `debug.setStageCompleted("w1s2", true)` | Progression state matches unlock and core rules |

## 9.2 Integration Tests

| Test file | System | Check | Debug calls | Expected state |
| --- | --- | --- | --- | --- |
| stateFlow.test.js | States | Title no save shows Begin Signal; title with save shows Continue and New Signal; intro skips; map starts unlocked stage; stage leads to summary; summary continues; game over leads to retry, map, title; end leads to map or title | `debug.resetProgression()`, `debug.loadStage("w1s1")`, `debug.completeStage()`, `debug.pressKey("enter")` | State transitions correct |
| stageLoad.test.js | Stage factory | Every production stage loads; validator passes; player spawns; conduit exists; checkpoint exists; exactly 3 cores unless collected; enemy counts match table; boss stages contain correct boss; World 2 modifiers apply; camera bounds; 5-second idle no exceptions | `debug.loadStage(id)`, `debug.advance(5000)` | All 10 stages load and simulate cleanly |
| checkpointDeath.test.js | Death and checkpoint | Death at checkpoint resets dynamic state; respawn at checkpoint; hearts reset 5; lives decrement; boss resets if present; game over at zero lives | `debug.loadStage("bossTestStage")`, `debug.activateCheckpoint()`, `debug.setPlayerHearts(0)`, `debug.killPlayer()`, `debug.advance(1000)` | Player and stage reset correctly |
| pit.test.js | Pit | Falling 64 px below stage triggers pit; pit with over 1 heart respawns and 0.5 invulnerability; pit with 1 heart death; no checkpoint respawns at start | `debug.teleportPlayer(0, stageHeightPlus70)`, `debug.setPlayerHearts(5)`, `debug.advance(1000)` | Pit rule and respawn correct |
| pause.test.js | Pause | Pause stops simulation; enemies do not move; projectiles do not move; boss timers do not advance; resume continues; restart resets; map exits | `debug.loadStage("bossTestStage")`, `debug.pressPause()`, `debug.advance(1000)`, `debug.pressKey("resume")` | Simulation freezes and resumes correctly |
| weaponProgression.test.js | Weapon progression | At w1s1 only Chirp unlocked; selecting Sifter triggers deny; w1s2 tuner unlocks Sifter; w1s4 unlocks Lance; w2s2 unlocks Bloom; unlocks persist | `debug.loadStage("w1s1")`, `debug.selectWeapon(2)`, `debug.spawnTuner("sifter", 100, 100)`, `debug.advance(100)` | Deny and unlock behavior correct |
| coreProgression.test.js | Core progression | Collecting core removes it; core does not respawn on retry; total increments; all 3 in stage increases total by 3 | `debug.loadStage("w1s1")`, `debug.collectCore("w1s1-core-1")`, `debug.resetStage()`, `debug.advance(100)` | Core persistence correct |
| bossDefeat.test.js | Boss defeat | Boss can be damaged; phase warnings appear; attacks telegraph; death clears projectiles and summons; conduit activates; non-final boss leads summary; final boss leads end | `debug.loadStage("w1s5")`, `debug.activateBoss()`, `debug.damageBoss(180)`, `debug.advance(2000)`, `debug.setConduitReady(true)` | Boss death and state transition correct |

## 9.3 End-to-End Tests

| Test file | System | Check | Debug calls | Expected state |
| --- | --- | --- | --- | --- |
| allStagesSmoke.test.js | All stages | Every stage loads; 10-second idle no exceptions; player alive unless unavoidable hazard; validator passes; entities within bounds | `debug.loadStage(id)`, `debug.advance(10000)` | All stages stable |
| stageCompletionProof.test.js | Completion | Every stage validationRoute reaches conduit; stage complete fires; summary or end appears; time under limit; boss stages boss HP zero before conduit; conduit locked before boss death | `debug.loadStage(id)`, `debug.advanceUntil(conduitReached, limitMs)` | Bot completes every stage |
| fullGame.test.js | Full game | Title to End through all stages; total deaths non-negative; total time positive; cores zero if no core routes used | `debug.resetProgression()`, `debug.loadStage(id)`, `debug.completeStage()` | Full game completes |
| allCores.test.js | Core collection | Every stage coreRoutes collect 3 cores; main route reaches conduit; total cores 30; end shows Cores 30/30 | `debug.loadStage(id)`, `debug.spawnCore(id, x, y)`, `debug.collectCore(id)`, `debug.completeStage()` | All 30 cores collectible |

## 9.4 SCREENSHOTS

| Screenshot ID | State | Must show | Must not show |
| --- | --- | --- | --- |
| S01 | Title | SIGNAL COURIER logo, Begin Signal or Continue, New Signal, Controls, footer | Stage gameplay, boss HUD |
| S02 | Title confirm | Erase saved signal? panel, Erase, Cancel | Hidden confirm options |
| S03 | Intro | One story card, skip prompt, thin cyan scanline | Gameplay |
| S04 | Map unlocked | Two world panels, 5 nodes each, unlocked cyan node, completed check | Selectable locked nodes |
| S05 | Map World 2 locked | World 2 dimmed 50 percent, padlock, Restore W1 Signal | World 2 node selectable |
| S06 | Stage start | Stage name card, world label, stage label, signal wipe | Permanent stage name except HUD |
| S07 | In-stage HUD | Hearts, weapon slots, stage label, core counter, pause icon, crosshair | Boss HUD on non-boss stage |
| S08 | Damage feedback | Red vignette, lost heart pulse, player flicker | Full-screen opaque red |
| S09 | Boss HUD | Boss name, boss bar, phase warning | Hearts hidden, core counter hidden |
| S10 | Pause | PAUSED panel, Resume, Restart Stage, Signal Map, Title | Moving enemies or projectiles |
| S11 | Summary | Stage name, Time, Deaths, Cores in Stage, Total Cores, Continue, Signal Map | Stage gameplay |
| S12 | Game Over | SIGNAL LOST, Connection failed, Retry Stage, Signal Map, Title | Gore or harsh punishment visuals |
| S13 | End | SIGNAL RESTORED, Total Time, Total Deaths, Total Cores, Signal Map, Title | Incomplete stats |
