# 8. DEBUG API

All test calls that reach game state must use `game.debug`.

```js
game.debug = {
  // Simulation
  advance(ms),
  advanceUntil(predicate, timeoutMs),
  setSimTime(seconds),
  setRngSeed(seed),
  getRngSeed(),

  // Stage
  loadStage(id),
  resetStage(),
  setStageTimeMs(ms),
  addStageDeath(),
  setStageDeaths(n),
  completeStage(),
  setConduitReady(value),
  getStage(),

  // Player
  teleportPlayer(x, y),
  setPlayerVel(vx, vy),
  setPlayerHearts(n),
  setPlayerLives(n),
  setPlayerInvuln(seconds),
  setPlayerCrouch(value),
  setPlayerFacing(dir),
  damagePlayer(sourceX, sourceY),
  killPlayer(),
  respawnPlayer(),

  // Input
  pressKey(action),
  releaseKey(action),
  setKeys({ left, right, crouch }),
  pressJump(),
  releaseJump(),
  holdJump(value),
  pressShoot(),
  releaseShoot(),
  setShoot(value),
  setMouseWorld(x, y),
  setMouseInside(value),
  selectWeapon(slot),
  cycleWeapons(direction),
  pressPause(),

  // Weapons
  unlockWeapon(weapon),
  selectWeapon(weapon),
  setSwitchCooldown(seconds),
  setFireCooldown(weapon, seconds),
  giveAllWeapons(),

  // Projectiles
  spawnPlayerProjectile(weapon, x, y, aimX, aimY),
  spawnEnemyProjectile(type, x, y, vx, vy, radius, damage, lifetime),
  clearProjectiles(),
  setProjectileLimit(team, limit),

  // Enemies
  spawnEnemy(type, x, y),
  killEnemy(type),
  killAllEnemies(),
  setEnemyHp(typeOrId, hp),
  setEnemyActive(typeOrId, value),
  setEnemyState(typeOrId, state),
  setEnemyCooldown(typeOrId, attack, seconds),
  setEnemyDormant(typeOrId, value),

  // Boss
  activateBoss(),
  damageBoss(amount),
  setBossHp(hp),
  setBossPhase(n),
  setBossState(state),
  setBossCooldown(attack, seconds),
  clearBossSummons(),
  setBossDying(value),

  // Hazards
  spawnBeam(type, x, y, width, height, telegraphTime, activeTime),
  clearBeams(),
  spawnTempSpike(x, y, w, h, warnDuration, activeDuration),
  clearTempSpikes(),
  setTempSpikeState(id, state),

  // Platforms
  setPlatform(id, x, y),
  setPlatformVelocity(id, vx, vy),
  resetPlatforms(),

  // Pickups
  collectCore(id),
  spawnCore(id, x, y),
  clearCores(),
  spawnHeart(x, y),
  spawnTuner(weapon, x, y),
  collectTuner(weapon),

  // Checkpoints
  setCheckpoint(x, y),
  activateCheckpoint(),
  resetCheckpoints(),

  // Progression
  setStageCompleted(id, value),
  setStageUnlocked(id, value),
  setCoreCollected(id, value),
  setWeaponUnlocked(weapon, value),
  resetProgression(),
  setRunStats(timeMs, deaths),
  addStatDeath(),
  addStatTimeMs(ms),

  // Events
  emitVfx(name, data),
  emitSfx(name)
}
```
