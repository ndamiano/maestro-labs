# 1. CONVENTIONS

## 1.1 Units, axes, frames

- All gameplay coordinates are logical pixels.
- Positive X is right.
- Positive Y is down.
- Stage origin is top-left.
- Tile size is 32 px.
- Logical viewport is 960 x 540 px.
- Canvas is scaled to fit the screen while preserving aspect ratio.
- Simulation uses a fixed timestep.
- `STEP = 1 / 60` seconds.
- Frame delta is clamped to 0.1 seconds.
- Simulation time advances in fixed steps.
- Rendering receives the accumulator fraction but does not interpolate.
- Time values are seconds unless marked `Ms`.
- Distance values are pixels.
- Speed values are pixels per second.
- Acceleration values are pixels per second squared.
- Angle values are degrees in design tables. Conversion to radians is implementation detail.
- Entity positions are top-left pixel coordinates unless a rule says center or feet.

## 1.2 Important conventions

- No touch controls.
- Desktop mouse and keyboard are the only required inputs.
- No external runtime libraries.
- No build step.
- No physics engine.
- No ECS library.
- No frame interpolation.
- No object pooling beyond simple array expiration.
- Simulation is deterministic.
- No `Math.random` in simulation.
- One random source per stage: `mulberry32`.
- Default stage seed is `100 * world + index`.
  - World 1 Stage 1 seed is 101.
  - World 2 Stage 5 seed is 205.
- Tests may override the stage seed with `debug.setRngSeed`.

Fixed loop:

```js
let last = performance.now();
let accumulator = 0;

function frame(now) {
  let delta = (now - last) / 1000;
  last = now;

  if (delta > 0.1) delta = 0.1;

  accumulator += delta;

  while (accumulator >= STEP) {
    game.update(STEP);
    accumulator -= STEP;
  }

  game.render(accumulator / STEP);
  requestAnimationFrame(frame);
}
```

System run order each fixed step:

1. Advance stage time.
2. Update moving platforms and store platform deltas.
3. Apply platform carry to player if riding.
4. Read player input.
5. Update player facing.
6. Update weapon selection, switch cooldown, and fire cooldown.
7. Apply horizontal acceleration or friction.
8. Apply wind acceleration.
9. Apply conveyor offset if grounded.
10. Apply gravity or updraft.
11. Handle jump buffer, coyote time, and variable jump cut.
12. Integrate X and resolve horizontal collision.
13. Integrate Y and resolve vertical collision.
14. Update grounded state.
15. Update coyote and jump buffer timers.
16. Check pit rule.
17. Check hazards.
18. Update player projectiles.
19. Update enemy projectiles.
20. Update enemies.
21. Update boss.
22. Update beams.
23. Update temporary spikes.
24. Update pickups.
25. Update checkpoint and conduit triggers.
26. Update camera.
27. Update HUD.
28. Emit VFX and audio events.

Controls table:

| Action | Primary input | Alternate input |
| --- | --- | --- |
| Move left | A | Left Arrow |
| Move right | D | Right Arrow |
| Jump | W | Up Arrow or Space |
| Crouch | S | Down Arrow |
| Aim and shoot | Left mouse button | J |
| Switch to weapon 1 | 1 | None |
| Switch to weapon 2 | 2 | None |
| Switch to weapon 3 | 3 | None |
| Switch to weapon 4 | 4 | None |
| Cycle weapons forward | E | Q |
| Pause | Escape | P |

Aiming rules:

- Mouse aiming is primary.
- Player can aim in any 2D direction.
- Visual facing follows mouse X relative to player.
- If mouse input is unavailable, J shoots in facing direction.
- If no horizontal input has occurred, facing is right.
- Crouch does not restrict aim.
- Crouch lowers muzzle origin and hitbox.
