# Word2World recipe on qwen3.8_27b — results

**Question:** does the Word2World recipe (LLM extracts entities/tilesets/walkability, then layered coarse-to-fine terrain + object passes with self-critique rounds) produce coherent 2D tile maps on a small local model?

**Short answer: yes, with decomposition.** 12/12 maps completed with zero pipeline failures, all fully connected, and most read as the requested place at a glance. The recipe survives the move from GPT-4-class to 27B *only because* every stage is a small single-purpose call with a JSON skeleton and a validate-and-reask loop — the paper's original monolithic chat-history prompts were not attempted after inspecting them (freeform dict extraction from prose, whole world as one backtick blob).

## Setup

- Adapted pipeline, per map: tileset call → objects/entities call → coarse 6×8 zone grid → deterministic ×4 upscale + majority smoothing (24×32) → fine pass as line/rect paint ops → coordinate placement (invalid terrain snapped to nearest preferred cell) → up to 2 self-critique rounds (issues JSON → fix ops/moves), early exit when critique reports no issues.
- Direct place requests instead of story generation. 4 places × 3 seeds.
- All JSON-validated with one-error-at-a-time reask; every call logged to `*_transcript.jsonl`.

## Cost per map

| metric | median | range |
|---|---|---|
| LLM calls | 10 | 6–11 |
| tokens (prompt+completion) | ~15k | 3.8k–18.2k |
| wall-clock | 37s | 6–49s |

Whole 12-map sweep ≈ 6 min.

## Per-map notes

Checklist: coherent layout / open ground vs corridors / entities where implied / walkability (connected, >40% ground).

### fishing_village — "a fishing village on a south coast" (`sheet_fishing_village.png`)
- **seed 1** — walk 84%, conn 100%, 10 calls. Coherent banding: grass north, sand beach, water on south edge as asked. Huts at grass/sand boundary, boats at the waterline, villagers near piers. Flaw: fix round painted the pier as a large filled brown blob instead of a thin walkway. Open ground.
- **seed 2** — walk 66%, conn 100%. Clean coast bands; stone pier platform at the waterline with huts on it, fisherfolk clustered at the pier, boats in open water. Nets placed on the north grass (odd but harmless). Coherent.
- **seed 3** — walk 83%, conn 100%. Correct bands and a 1-tile-wide pier running into the water with boats and fishermen at its foot — best pier of the three. Flaw: a huge stone slab (~10×18) on the upland; scale of "village stonework" wildly off. Semi-coherent.

### dungeon_floor — "a dungeon floor with a locked treasury" (`sheet_dungeon_floor.png`)
- **seed 1** — walk 32%, conn 100%, **6 calls / 6s**: critique round 0 returned score 9, zero issues → early exit. Map is actually the weakest of the three: rooms are fine but the treasure chest sits in an open room with no enclosure, and the locked door floats mid-floor. **Self-critique false pass** — the one clear critique blind spot in the run. Also the only map under the 40% walkable bar (32%, though corridor-style low walkability is arguably genre-appropriate).
- **seed 2** — walk 42%, conn 100%. Rooms + corridors read, but treasury again not enclosed; locked door in open floor. Middling.
- **seed 3** — walk 38%, conn 100%. Best dungeon: an enclosed dark-walled chamber containing the gold treasury, locked door at its single entrance, chests in the outer room corners. The "locked treasury" brief is actually satisfied. Walk 38% — just under bar, corridor-style, fully connected.

### forest_clearing — "a forest clearing with a hermit hut" (`sheet_forest_clearing.png`)
- **seed 1** — walk 40%, conn 100%. Textbook: light-green clearing inside dark forest, stone hut in the center with a dirt path leading south, hermit + props at the hut. Coherent, correct entity placement.
- **seed 2** — walk 41%, conn 100%. Concentric clearing is right, but the center is over-built — a sprawling brown/stone complex rather than one hut. Entities cluster there sensibly. Middling coherence.
- **seed 3** — walk 88%, conn 100%. Broken layout: map framed by a water border, dominated by brown dirt, clearing pushed to a small patch; trees ended up as scattered *objects*. Critique scored it 5–6 and fixes didn't rescue it. The one genuinely incoherent map of the 12.

### desert_oasis — "a desert oasis market" (`sheet_desert_oasis.png`)
- **seed 1** — walk 96%, conn 100%. Sand field, green oasis ring with water, market plaza with stall row, huts, camels south, paths crossing the sand. Coherent; very open.
- **seed 2** — walk 88%, conn 100%. Best oasis: central water pool ringed by a mud bank, palm green around it, gray market ground on the south shore with stalls, merchants, camels, goods. Exactly the brief.
- **seed 3** — walk 95%, conn 100%. Plaza slab with stalls/merchants inside and a pond to the east; sparser and pool detached from market, but reads. 6 placements snapped (worst case) — placement call ignored preferred-terrain most here.

## Aggregate findings

1. **Coherent layout:** 9/12 clearly coherent, 2 middling, 1 broken (forest seed 3). Macro-geography from the coarse 6×8 pass is the recipe's strongest link on the 27B — coast/clearing/oasis geometry came out right in 11/12.
2. **Walkability:** largest walkable component = 100% on all 12 maps; walkable ground 32–96% (only dungeon seed 1 under 40%). No repair pass was ever needed — smoothing + open zone painting keeps maps connected for free.
3. **Entities:** implied placement mostly right (boats in water, hermit at hut, stalls in plaza). Terrain-snap fallback fired 0–6 times per map (median 1) — the placement call is the least reliable stage, but cheap deterministic snapping fully covers it.
4. **Self-critique is real but asymmetric.** Critiques cite concrete rows/cols and genuine problems (scattered stalls, disconnected piers, unenclosed treasury). But fixes are coarse — the worst visual artifacts (filled-blob pier, giant slab) were *introduced* by fix-round rect ops with `fill:true`. And one round-0 critique (dungeon seed 1) passed a mediocre map with 9/10. Net effect of critique rounds on scores: flat (scores don't climb round-to-round).
5. **Scale blindness** matches the paper's own limitation list: single-tile semantics ("a hut is one tile") vs. the model painting 10×18 "buildings".
6. **Model handling:** zero model-ceiling failures. Every stage eventually produced valid JSON; the validate-and-reask loop fired occasionally (worst case one extra call per stage). Skeleton-first prompts + single-error feedback were sufficient — no stage needed further decomposition beyond the initial design.

## Verdict

Recipe transfers to a 27B once "one giant conversation" becomes "ten small schema-validated calls". Terrain layering coarse-to-fine works well; self-critique adds specificity but not monotone improvement, and its fix vocabulary (rects) causes the ugliest artifacts. Cheapest wins available: drop `fill:true` from fix ops, cap structure footprints, and replace LLM self-scoring with the programmatic checks as gate.

---

# Arm 2: LLM relations + ASP constraint solve (clingo)

Same LLM front for tileset + objects, plus one **relations** call (bands pinned to edges, coverage percents, per-item near/cluster rules — never coordinates). Layout solved by clingo at 12×16 following Smith & Mateas: one-terrain-per-cell choice rule; integrity constraints for edge bands, coverage counts, 2×2-same-terrain openness (zones are patches, not corridors), walkable ≥60% of open ground, anchor + transitive-closure reachability of the whole walkable region, and item placement (preferred terrain, near-terrain ≤2, cluster ≤3, adjacent to reachable ground, distinct cells). Per-seed variety from `--sign-def=rnd --rand-freq=0.7 --seed=N`. Relaxation ladder on UNSAT: drop openness → drop coverage → drop bands. ×2 upscale + same smoothing and render path as arm 1.

## Head-to-head

| | arm 1 (LLM places tiles) | arm 2 (ASP places tiles) |
|---|---|---|
| completed | 12/12 | 12/12 (1 needed a validator re-ask, see failure modes) |
| LLM calls / map | 10 (6–11) | 3 (3–4) |
| tokens / map | ~15k | ~1.7k |
| wall-clock / map | ~37s | ~4.5s (solve itself 0.1–0.9s) |
| walkable connected | 100% all 12 | ≥99.3% all 12 (guaranteed at coarse res; smoothing + blocking objects nick off ≤0.7%) |
| walkable ≥ target | 11/12 over 40% | 10/12 over 60% (dungeons 30–37% after blocking objects/smoothing) |
| layout coherence (eye) | 9/12 coherent | ~2/12 coherent (fishing/oasis seeds with strong south-coast bands); rest read as patchwork quilts |
| variety across seeds | moderate; occasionally collapses to same banding | high in pixel terms, low in character — every map is a different quilt of the same texture |

## What the sheets show

- **Arm 2's only macro-structure is what the relations language can say.** Where the LLM declared an edge band (water south in fishing seeds 2–3, oasis seeds 2–3), that part of the map is right, and it is the *only* legible geography. Everything else — coverage percents + openness — is satisfied by scattering mid-size patches everywhere: technically valid, visually noise. Dungeon seed 3 is the extreme: "gold ≥ some percent" became a giant gold continent.
- **Arm 1 wins coherence precisely where no constraint was written**: villages hug the shore, a clearing sits inside forest, a treasury is a room. That's prior knowledge acting through direct painting — the thing arm 2's solver, given only the declared relations, cannot recover.
- **Letter-vs-spirit gaming**: the solver puts boats in any water patch satisfying "near sand", including inland puddles; items sit at legal but meaningless spots. Constraints prune invalid maps; they don't rank valid ones (satisficing, exactly as the paper frames it).
- **Guarantees flip sides**: arm 2 gets connectivity, walkable share, openness, and reachable buildings *by construction* — arm 1 got them by luck (and it did get them, which is itself a finding: on open outdoor maps these properties are easy). Arm 2's guarantees survive everything except the deterministic post-passes (smoothing can pinch a 1-cell isthmus; a blocking object can wall off a nub — worst case 5 components, 99.3% main).

## Failure modes

- **Arm 1**: fix-round `fill:true` blobs; single-tile scale blindness (10×18 "stonework"); self-critique false pass (dungeon seed 1 scored 9/10); placement needing terrain-snap (median 1, max 6 per map).
- **Arm 2**: *relations conflicts* — fishing seed 3 declared two south bands (water depth 3 + sand depth 1), row 11 forced to be two terrains at once → UNSAT at every relaxation level, since bands were never relaxed. Fixed with a band-overlap validator (the model corrected itself on one re-ask) plus a drop-bands ladder level. *Coverage misuse* — the LLM hands out percents to decorative terrains (gold 20–30%) that the solver then dutifully floods. *Under-specification* — the relations vocabulary (bands/coverage/near/cluster) is too weak to force village-shaped villages; everything the vocabulary doesn't pin down comes out arbitrary.

## Verdict (head-to-head)

Arm 2 is ~8× cheaper, ~8× faster, and delivers hard guarantees arm 1 can only hope for — but with today's relations vocabulary it loses the thing being judged: layout coherence. Arm 1's LLM painting carries implicit spatial prior knowledge that never made it into the constraint language. The obvious synthesis (untested): arm 1's coarse LLM zone-painting for macro-geography, arm 2's ASP for item placement + guarantees — each arm doing the part it demonstrably wins.

## Files

- arm 2: `output/<place>/asp_seed<N>_{map.json,map.png,transcript.jsonl}`, `output/summary_arm2.json` (includes solve logs + relations specs)
- combined sheets: `output/sheet_<place>.png` — arm 1 seeds 1–3 then arm 2 seeds 1–3
- solver encoding: `lab/asp_arm.py`

## Files (arm 1)

- `output/<place>/seed<N>_map.json` — grid, terrain, placements, history, cost
- `output/<place>/seed<N>_map.png` — rendered map
- `output/<place>/seed<N>_transcript.jsonl` — every prompt/response with tokens + latency
- `output/sheet_<place>.png` — 3-seed contact sheet
- `output/summary.json` — machine-readable stats

---

# Ground & sprite rounds (2026-08-23)

Question: can the arm-1 grid become a good-looking map? Answer: yes — ground is solved, sprites have a proven formula, static composition was deliberately stopped (the game composites at runtime).

## Ground recipe (proven, ~10s/map at 48px/cell on the 5090)

1. **LLM paintspec** (1 call): per terrain region, a muted painterly hex + a 5-12 word material phrase. Show the LLM the layout's rough color as intent (bright yellow treasury → gold). Beats the hand word-table it replaced (round 7 vs 9).
2. **Guide:** flat fill per region at 48px/cell, per-pixel jitter ±22 (NO coarse blotches — they invite region reinterpretation).
3. **Regional pass:** per-region ConditioningSetMask prompts, one KSampler pass, DreamShaperXL Turbo, denoise 0.55. Mask feather radius from region erosion depth (thin regions hard-masked — a fixed 24px feather drowned the treasury under its neighbours' conditioning).
4. **Blend pass:** global prompt img2img, denoise 0.35. 0.45+ smears material identity back to mush.

Key laws learned:
- **Guide color anchors final hue at 0.55** — no prompt wording overrides a traffic-cone guide. Color quality lives in the guide, not the prompt.
- Flat guides need denoise ≥0.7 to texture (structure dies); jittered guides texture at 0.55 (structure lives).
- Regional prompts stop cross-region word bleed and let each region use its own vocabulary.
- md5 the outputs: two "different" runs byte-identical exposed a substring-matching bug (`treasury_floor` hit `floor` before `gold`). Longest-key match.

## Sprites

- Generic one-word prompts on NetaYume produced garbage (briefcase fisherman, deck-chair pier).
- **Qwen-2512 + worldgen's subject_style.txt + one contextual descriptive sentence** produced excellent assets for every item type including characters (spritebench/all.png). The routing table's NetaYume-for-characters lost to Qwen here.
- Top-down variants work for props/boats/creatures; buildings resist pure overhead (¾ convention is the likely ruling; undecided, deliberately parked).
- Whole-map unify img2img after compose: measured harmful (0.3 mushes sprites). Dead end.

## Files
- ground rounds: output/ground{,2,3,4,5,6,7,9}/ (round 8 = adaptive-feather scripts inline)
- LLM specs: output/<place>/seed<N>_paintspec.json + transcripts
- sprite bench: output/spritebench/all.png; top-down arm: output/topdown/
- scripts: run_ground*.py, run_objects*.py, run_spritebench.py, run_topdown.py
