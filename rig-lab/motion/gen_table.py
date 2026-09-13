"""Generate motion from the BAKED verb table — no language model at runtime.

usage: python gen_table.py <verb> <duration> <out_base>
"""
import sys, time
import torch
sys.path.insert(0, "/home/nick/Documents/Labs/rig-lab/motion")
from table_encoder import TableTextEncoder
from kimodo import load_model
from kimodo.exports.motion_io import save_kimodo_npz

TABLE = "/home/nick/Documents/Labs/rig-lab/motion/verb_embeddings.npz"

def main(verb, duration, out_base, seed=7):
    enc = TableTextEncoder(TABLE, device="cpu")
    t0 = time.time()
    model = load_model(None, device="cuda:0", default_family="Kimodo", text_encoder=enc)
    load_s = time.time() - t0
    prompt = enc.prompts[enc.by_name[enc._key(verb)]]
    torch.manual_seed(seed)
    t0 = time.time()
    out = model([prompt], [int(duration * model.fps)], num_denoising_steps=100, num_samples=1,
                multi_prompt=True, num_transition_frames=5, post_processing=True, return_numpy=True)
    gen_s = time.time() - t0
    single = {k: (v[0] if hasattr(v, "shape") and len(v.shape) > 0 else v) for k, v in out.items()}
    save_kimodo_npz(out_base + ".npz", single)

    from kimodo.exports.bvh import save_motion_bvh
    from kimodo.skeleton import SOMASkeleton30, global_rots_to_local_rots
    skel = model.skeleton
    if isinstance(skel, SOMASkeleton30):
        skel = skel.somaskel77.to("cuda:0")
    joints_pos = torch.from_numpy(out["posed_joints"][0]).to("cuda:0")
    joints_rot = torch.from_numpy(out["global_rot_mats"][0]).to("cuda:0")
    save_motion_bvh(out_base + ".bvh", global_rots_to_local_rots(joints_rot, skel),
                    joints_pos[:, skel.root_idx, :], skeleton=skel, fps=model.fps,
                    standard_tpose=True)
    print(f"[table] {verb}: load {load_s:.1f}s gen {gen_s:.1f}s -> {out_base}.bvh")

if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), sys.argv[3])
