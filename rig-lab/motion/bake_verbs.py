"""Bake the verb library's text embeddings ONCE, so prod never loads Llama.

Kimodo needs a 4096-dim embedding per prompt, and the encoder that makes it is a gated 15 GB
Llama-3 under Meta's licence. But the model only ever calls `text_encoder(texts) -> (feat,
lengths)`. For a FIXED verb library the answer is the same every time, so it is computed here,
on the lab box, and shipped as a table.
"""
import argparse, json, os
import numpy as np
import torch

VERBS = {
  "walk":   "a person walks forward at a steady pace",
  "run":    "a person runs forward quickly",
  "idle":   "a person stands still, breathing calmly, shifting weight slightly from foot to foot",
  "attack": "a warrior swings a sword downward in a powerful overhead attack, then returns to a fighting stance",
  "thrust": "a warrior lunges forward with a spear thrust, then steps back into a guard",
  "cast":   "a wizard raises both arms and casts a spell forward, then lowers their arms",
  "hurt":   "a person flinches backward as they are hit, clutching their chest, then recovers",
  "death":  "a person is struck, staggers backward and collapses to the ground, lying still",
  "dodge":  "a person dives sideways into a quick roll and comes back up onto their feet",
  "jump":   "a person crouches and jumps straight up, landing on both feet",
  "block":  "a person raises a shield in front of them and braces against a blow",
  "cheer":  "a person raises both fists and celebrates",
}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/home/nick/Documents/Labs/rig-lab/motion/verb_embeddings.npz")
    args = ap.parse_args()
    from kimodo.model.llm2vec.llm2vec_wrapper import LLM2VecEncoder
    enc = LLM2VecEncoder(
        base_model_name_or_path=os.environ.get("KIMODO_BASE_LLM", "NousResearch/Meta-Llama-3-8B-Instruct"),
        peft_model_name_or_path="McGill-NLP/LLM2Vec-Meta-Llama-3-8B-Instruct-mntp",
        dtype="float32", llm_dim=4096, device="cpu")
    names = list(VERBS)
    feats, lengths = enc([VERBS[n] for n in names])
    feats = feats.detach().cpu().numpy().astype(np.float32)
    np.savez_compressed(args.out, names=np.array(names), prompts=np.array([VERBS[n] for n in names]),
                        feats=feats, lengths=np.array(lengths))
    print(f"baked {len(names)} verbs -> {args.out}  feats {feats.shape} "
          f"({os.path.getsize(args.out)/1e6:.1f} MB)")
