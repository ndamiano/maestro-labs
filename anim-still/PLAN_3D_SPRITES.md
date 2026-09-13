# Sprite sheets from a rigged mesh — what is left to build

State on 2026-09-09. Everything below TRELLIS/SkinTokens works today; the gap is one step.

| step | tool | time | state |
|---|---|---|---|
| T-pose still | Qwen + framing clause | 20 s | works — arms free of the body, 0/10 cropped |
| mesh | `run_trellis.py --ptype 512` | 9.6 s | works, textured, riggable |
| rig | SkinTokens `demo.py --use_transfer` | 10.8 s | works — 52 bones, clean shoulder deform |
| name the bones | `rig-lab/motion/label_bones.py` | 2 s | works — Mixamo names from structure alone |
| **motion onto the rig** | `apply_bvh*.py` | — | **BROKEN — the whole gap** |
| render a sheet | `anim-still/render_sheet.py` + `view/sheet.html` | 15 s | machinery works; poses were hand-guessed and bad |

## 1. Fix the retarget (the only blocker)

`apply_bvh_kimodo.py` maps joint NAMES but not joint FRAMES, so it produces a figure lying on
its side with its arms overhead — on Aldric and on the knight it was written for.

Three faults, all standard:

- **Rest-pose offset.** A BVH's rotations are relative to the SOURCE skeleton's rest pose. Ours is
  a T-pose with SkinTokens' arbitrary per-bone roll. Apply
  `R_local = R_offset⁻¹ · R_bvh · R_offset`, where `R_offset` is the bind-pose rotation from source
  bone to target bone, computed once per bone pair from the two rest poses.
- **Root translation.** A walk clip travels. A sprite cycle is in place: zero the root's XZ per
  frame (keep Y bob), or subtract the mean velocity.
- **Axis convention.** BVH is Y-up; convert once at import rather than per bone.

Validate on a clip whose correct result is obvious — a T-pose-to-T-pose idle should barely move,
and a walk should keep the feet under the hips.

## 2. Get clips worth retargeting

Kimodo's generated BVHs are on disk (`kimodo_gen/out_path_*.bvh`) and are the cheapest test input.
For shipping motion, a fixed library beats generation: idle, walk, run, attack, hurt, die. Check
the licence of whatever source is used — this ships inside customer games.

AnyTop is installed and was measured "weak on bipeds (shuffle)"; treat generation as the fallback
for body plans a library cannot cover, not the default.

## 3. Sheet rendering (mostly done)

`view/sheet.html` renders an orthographic, transparent-background view; `render_sheet.py` walks
anims x facings x frames and packs cells against one shared bbox, writing the same
`{cell, dirs, anims:{rows,frames,fps}}` manifest `lib/sprites.js` already plays.

Remaining: drive poses from the retargeted ACTION (sample the glb's animation track at N frames)
instead of the hand-written pose functions, and keep the four facings as camera azimuths.

## 4. The still needs a second variant

A T-pose is right for meshing and wrong for a sprite's idle frame, and the T-pose still sheathed
the sword INTO the coat, so the rigged character can never swing it. A mesh still probably wants
the weapon held clear of the body. That is a second render per actor, and `generate_media` today
renders one still per actor and uses it for everything.

## 5. Body plans

`label_bones.py` assumes a humanoid: spine up, two legs down, arms lateral. A wyvern, a horse or a
card has no such structure. Detect the failure (no two symmetric 4-joint chains descending from the
root) and fall back — H3 sheets or code-drawn — rather than shipping a mislabelled rig.

## 6. Where it runs

Mesh and rig are GPU steps of ~10 s each; the sheet render is a headless browser. The mesh queue
already exists in prod. Whole path is ~36 s a character against ~300 s of MiniMax for a sheet that
mostly holds still.

## The bar

A rendered sheet the owner plays in a game and accepts. Nothing measured here says the OUTPUT is
good yet — only that every mechanical step runs.
