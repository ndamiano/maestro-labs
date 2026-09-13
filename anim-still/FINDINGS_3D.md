# Sprite sheets from text, via a rigged mesh — 2026-09-09

A character comes out of a prompt and animates from a sentence. Nothing here is in the repo.

## The chain

| step | tool | time |
|---|---|---|
| T-pose still | Qwen + framing clause | 20 s |
| mesh | TRELLIS 2 @512 | 10 s |
| rig | `motion/template_rig.py` | 8 s |
| motion | `kimodo_gen "<sentence>"` | 40 s |
| retarget | `motion/retarget.py` | 5 s |
| sheet | `sheet_from_action.py` | 8 s |

## What was actually wrong, in the order it hid

**1. Kimodo's text conditioning was never on.** The lab's `gen.py` builds a `NullTextEncoder` and
passes `[""]`. Kimodo is a TEXT-TO-MOTION model (700 h of mocap, LLM2Vec/Llama-3 embeddings) with
constraints as an extra; with the text disconnected it samples unconditionally and only the
constraint steers it. That made it look like a trajectory model — authoring verbs as root paths
gave 3-20x the limb motion of authoring joint angles, which is true and beside the point.

The text encoder needs `meta-llama/Meta-Llama-3-8B-Instruct`, a GATED repo that answers 403.
`NousResearch/Meta-Llama-3-8B-Instruct` is the same weights, ungated.
`kimodo/model/llm2vec/llm2vec_wrapper.py` now reads `KIMODO_BASE_LLM` / `KIMODO_PEFT_LLM`.
The encoder is NOT swappable for another LLM — Kimodo's cross-attention learned that embedding
space, so a different model's hidden states are noise, whatever their size.

**2. A learned rigger reads limbs out of geometry, and props defeat it.** SkinTokens gave the
knight 22 bones and NO limbs (shield welded to torso), the mage no legs (floor-length robe), the
mounted rider no arms. `template_rig.py` places a canonical 25-bone humanoid by MEASURING the
T-pose — arm span at 80% height, hips at 52% — and skins it by distance to bone segment. 5/5
characters, correct Mixamo names by construction. Blender's own bone heat returns success and
writes ZERO weights on these meshes, and the glTF exporter then writes `skins: 0`.

**3. Retargeting is five separate fixes**, all in `motion/retarget.py`:
raw BVH action exported alongside the retarget and overriding it; scale taken from hip height,
which is ~0 because the rig's origin IS the hips; a BVH's armature rest is the offset skeleton,
not a T-pose, so the delta double-rotates; source and target left/right are opposite in world
space; root travel and yaw both need stripping for an in-place sprite.

**4. Sample the active window, not the clip.** A 8.3 s generated clip put the attack in
0.27-1.87 s; sampling evenly spent 9 of 12 cells on a held stance.

## Measured

Text-conditioned attack, retargeted: RightArm 63deg, forearm 56deg, hips 42deg, spine 22deg,
distributed through the clip. The joint-authored version of the same verb: arm 20deg, knee 2deg.

## Open

- Non-humanoids: the template is a humanoid. A wyvern or a horse needs its own template or a
  different route entirely.
- Template weights are distance-based; coats and capes move as one lump.
- The T-pose still sheathes a weapon INTO the body, so the character cannot swing what it holds.
- One sheet per verb per character is 4 facings x N frames; nothing yet says how many verbs a
  game should get, or what a one-shot (death) does about looping.
