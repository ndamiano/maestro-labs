# Anim sheet — 2026-09-09

Why Aldenmere's 23 actors came back with 170 of 288 clips flagged weak motion, and what fixes it.
Nothing here is in the repo yet.

## 1. The still was never a sprite (FIXED, measured)

Prod sends `style. subject, <view> view.` and nothing else. Across 5 subjects x 2 seeds:
**8/10 silhouettes ran off the bottom of the frame**, 0/10 had a plain background — every one a
cropped bust portrait on painted scenery. The video leg then tells MiniMax "plain white
background" 17 times about a picture that has neither.

The clause that fixes it, appended to the prompt (0/10 cropped, all five subjects, two styles):

    Full body from head to feet, both feet visible and planted on the ground, standing upright
    in a neutral pose with arms clear of the body and space around the figure on every side.
    Plain flat white background, flat even lighting, no cast shadow.

Rejected: "Full-length game sprite of X" — adds a die-cut sticker outline that mattes badly.
Open: a brown ground-shadow smudge survives into the alpha despite "no cast shadow".

`view` must NOT reach the prompt when `facings: 4` — the video leg feeds the still in as the
FRONT facing and turns from there, so a profile still makes all four rows wrong at the source.

## 2. H3 resolves "move + hold still" by HOLDING (measured, six confirmations)

Every clip carries `_I2V_ACTION_TAIL` = "It ends exactly as it started."

| clip | prompt | travel over the whole clip |
|---|---|---|
| walk (cyclic) | "walks in place" + pin | 25-38 — fine |
| attack | "lunges forward" + pin | **1.2** — never leaves the pose |
| defeat | "drops to one knee" + pin | 1.2 (7 of 8 facings) |
| four-clip test | "turns a quarter turn" + "stands completely still for the rest of the clip" | **1.0** — never turns |

A pin is free for a cycle and fatal for a one-shot. The single-clip variant that ALTERNATES
("snaps a quarter turn... holds for two frames") works and produced a five-frame stationary
true profile — the hold as a beat, not as a terminal state.

## 3. Frame picking was never the problem (measured against hand-picked truth)

Six turntables, facings hand-picked by the owner. Mean frames off:

| method | mean off |
|---|---|
| shipped quarter marks | 1.38 |
| CLIP ViT-L-14 | 1.33 |
| **three hardcoded constants (0,6,10,14)** | **1.46** |

Five geometric pickers were built and thrown away (silhouette distance, colour distance,
symmetry trough, mirror pair, silhouette width). Each failed on some body plan: a back view is
as symmetric as a front, a back mirrored is still a back, and a horse is widest side-on where a
person is narrowest.

## 4. What works: ask the vision model, constrained, thinking OFF

`qwen3.8_27b_quasar` on ninfer with `--vision`, per frame, five allowed answers
(FRONT/RIGHT/LEFT/BACK/OTHER), `reasoning_effort: none`:

- **742-token prompt, 3 tokens out, 0.12 s a frame — 2.2 s for a 22-frame turntable.**
- Answers form clean runs; OTHER lands on the transitions.
- Segment into runs, take the longest run per facing: **0.39 frames off** vs truth, and every
  tile is genuinely the facing it claims — the first method all day to clear that bar 6/6.
- A second ranking pass ("which of these is the truest side profile", all 22 images in one
  call, 2.1 s) scores 0.44 and fixes what runs miss on brann. The two fail on different
  characters; combining them is untried.

Two hard rules learned:

- **Never ask the model left vs right.** Asked "which is most left" and "which is most right"
  over the same 22 frames it returned frame 5 for both. Ask for "the truest side profile,
  ignore which way it faces" and take one before the back and one after — clip order supplies
  the side.
- **Thinking ON costs 1,150 tokens to answer with one number**, and at a 2,048 cap it burns the
  whole budget thinking and returns an EMPTY string with `finish_reason: length`. That is 1,400x
  slower and it is what made the first pass look like it was refusing ambiguous frames.

`front` must be FOUND, not assumed: the cavalier's still is a three-quarter horse and its only
true front is frame 19. The run picker found it; nothing else could.

## 5. Still open

- The clip prompt: ~60% of its words are hold-still clauses, "walks in place" reads as "don't
  go anywhere", and no count or distance is ever given.
- One-shot anims (attack, defeat) need the pin dropped — untested.
- Turn direction is asserted by the prompt ("screen-right first") and verified by nothing, so
  profile A/B -> left/right is unproven.
- Every measurement here is bipeds plus one horse, two art styles. No wyvern, no non-humanoid.

Lab: `~/Documents/Labs/anim-still/`. Renders: `/home/nick/output/anim-still/`.
