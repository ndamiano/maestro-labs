# 5. CHARACTERS

**Player (salvager).** Silhouette: human — oilskin coat, rope belt, small backpack, boots, **white outline** for readability (distinct from keys/coins/props: it has a body, head, legs, and motion). **Facings: 4** (N/E/S/W) from dominant velocity axis (horizontal wins ties), matching the 4-dir animation set.

*Animations by name (with motion rules):*
- `idle` — subtle breathing; small marker pulse on map.
- `walk` ×4 — small dust puff on dry; short slosh + small wake in shallow.
- `run` ×4 — larger dust puff (dry only, stamina > 0).
- `swim` ×4 — continuous small wake (shallow, stamina > 0).
- `swim_tired` ×4 — slower wake, lower cadence (shallow, stamina == 0).
- `channel` — leans into the prop; brass ring fills around `[E]` and around the prop.
- `blocked_bump` — short nudge + (deep water) splash + shake; no damage.

*State → animation (the states gameplay's rules need):* dry walking→`walk`; running→`run`; shallow swimming→`swim`; shallow at 0 stamina→`swim_tired`; deep water or cliff attempt→`blocked_bump`; channeling→`channel`; idle (no input)→`idle`; safe-displaced→`blocked_bump` at origin + ripple (T2 adds the full displacement animation, §0.3).

**Vault (animated entity).** States from §4.7, each mapped to a visual/animation: `locked` (<5 keys) = 5 hollow slots, gray/brass; `sealed` (5 keys, not low) = partially submerged + water swirl + wave icon; `openable` (5 keys + low) = glows gold, slots fill, tide lock opens; `opening` = heavy door swings/slides, light spills, water drains; `open` = treasure visible, golden compass rises. (Functional open = T1; the full 9-step cinematic = T2, §0.3.)

**Caches.** Shared open animation: lid/hatch/gate lifts or column slides, prop goes to its open state, small coin burst; open state persists. *(Prop shapes & sealed/openable looks: §3 props. Eagle/gulls are decorative, T3.)*
