# Getting text-driven sprite sheets into prod

State 2026-09-10. Everything below runs locally today; nothing is in the repo.

## What already fits, and does not change

`generate_media(kind="actor", details={"anims":[{"name","action"}], "facings", "view", "body"})`
is unchanged. The builder already writes `action` as PROSE describing motion — "lunges forward
with a two-handed sword slash" — which is exactly a motion prompt. No new tool, no `build.txt`
line, nothing new for the model to learn.

`lib/sprites.js` and the sheet manifest are unchanged: same `{cell, dirs, anims:{rows, frames,
fps}, pivot}` shape, so a game written against the H3 sheets plays a 3D-rendered one unmodified.
Proven by swapping Aldenmere's `actor-aldric.png/.json` and playing it.

## The work, in order

### 1. The still becomes a T-pose when a thing has anims  (`assets.py`, `comfyui_tools.py`)
One still serves both the sprite and the mesh today. A mesh needs limbs clear of the body or
voxelisation welds them; a sprite does not want a T-pose. So when `details.anims` is present the
still is rendered with the T-POSE framing clause and is the MESH's input; the sprite comes from
the sheet. `view` stops reaching the prompt for these.

### 2. The chain, as queue work  (`assets.py:_then_for`, `asset_chain.py`, `worker/handlers.py`)
Today `kind=="anim"` chains `anim_from_image` on the `video` queue. It becomes:

    image (T-pose still)  ->  mesh_from_image (TRELLIS, exists)
                          ->  rig_and_sheet   (NEW: template rig, retarget, render)

`rig_and_sheet` is one handler because the three steps share a Blender process and a browser;
splitting them costs two more model loads and buys nothing. It lands the same `<id>.png` +
`<id>.json` that `_save_anim` lands now, so `asset_chain` barely changes.

### 3. The worker image  (new deps, no gated repos)
TRELLIS weights (have), Kimodo weights, `bpy` (Blender as a pip module), Playwright + Chromium,
and the 184 KB verb table. **No Llama**: the text encoder is baked offline
(`motion/bake_verbs.py` -> `verb_embeddings.npz`, `motion/table_encoder.py` at runtime, proven
bit-identical to the live encoder). Runtime is ~0.4 s load + ~1.4 s a clip.

Queue: the `mesh` queue already carries TRELLIS and the right idle profile. Adding the rig/render
steps there avoids a fourth queue; if the browser proves awkward beside CUDA, split it out then,
not before.

### 4. Resolving prose to a verb
The library is fixed (12 baked today, 50 is still under a megabyte). The builder's `action` is
free prose, so it must resolve to a library entry. Cheapest first cut: ask the build model, with
the answer constrained to the library's names — the same three-token trick that solved the facing
picker. Falls back to `idle` when nothing matches.

### 5. Non-humanoids keep the H3 path
`template_rig.py` measures a HUMANOID (spine up, two legs down, arms lateral). A wyvern, a horse
or a card has no such silhouette. Detect it and fall back to the existing MiniMax sheet, which is
why the H3 code stays: its CYCLIC clips (walk, idle) were always the ones that worked.

### 6. Safety
The still is screened at prompt time and gets a verdict on landing, as now. The sheet is a RENDER
of an approved mesh, but the seam still needs a verdict of its own before staging — cheapest is
classifying a few cells, same fail-closed rule.

## What has to be answered before it ships

- **Kimodo's weights and the Bones mocap dataset licence.** The code is Apache-2.0; the weights
  and training data are the question, and this generates assets that ship inside customer games.
- **The T-pose still sheathes a weapon INTO the body**, so the character cannot swing what it
  holds — visible in Aldric's attack, where the arm swings empty. Needs a mesh-still arm.
- Per-verb seed variance: the same `death` prompt gave a proper collapse on one run and a settle
  on another. Either fix a seed per verb or generate two and keep the one that moves.
- Template weights are distance-based; coats and capes move as one lump.

## The bar

Doctrine: prove use before commit. The merge is the pipeline PLUS a real build that used it, with
the owner playing the result. A local build against the local queues is the rehearsal; the battery
after that.
