import argparse
import time

import torch

from kimodo import load_model
from kimodo.constraints import load_constraints_lst
from kimodo.exports.motion_io import save_kimodo_npz
from kimodo.model.null_text_encoder import NullTextEncoder


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--constraints", required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--diffusion_steps", type=int, default=100)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--bvh", action="store_true")
    args = ap.parse_args()

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    print(f"device={device}")
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    null_enc = NullTextEncoder(llm_dim=4096, device=device, dtype=torch.float32)
    t0 = time.time()
    model = load_model(None, device=device, default_family="Kimodo", text_encoder=null_enc)
    t_load = time.time() - t0
    print(f"model load: {t_load:.1f}s")

    num_frames = [int(args.duration * model.fps)]
    constraint_lst = load_constraints_lst(args.constraints, model.skeleton)
    print(f"loaded {len(constraint_lst)} constraint set(s) from {args.constraints}")

    torch.manual_seed(args.seed)
    t0 = time.time()
    output = model(
        [""],
        num_frames,
        constraint_lst=constraint_lst,
        num_denoising_steps=args.diffusion_steps,
        num_samples=1,
        multi_prompt=True,
        num_transition_frames=5,
        post_processing=True,
        return_numpy=True,
    )
    t_gen = time.time() - t0
    peak_vram = torch.cuda.max_memory_allocated() / (1024 ** 3) if torch.cuda.is_available() else 0.0
    print(f"generation: {t_gen:.1f}s, peak VRAM: {peak_vram:.2f} GiB")

    single = {k: (v[0] if hasattr(v, "shape") and len(v.shape) > 0 else v) for k, v in output.items()}
    save_kimodo_npz(args.output + ".npz", single)
    print(f"saved {args.output}.npz")

    if args.bvh:
        from kimodo.exports.bvh import save_motion_bvh
        from kimodo.skeleton import SOMASkeleton30, global_rots_to_local_rots

        skeleton = model.skeleton
        if isinstance(skeleton, SOMASkeleton30):
            skeleton = skeleton.somaskel77.to(device)
        joints_pos = torch.from_numpy(output["posed_joints"][0]).to(device)
        joints_rot = torch.from_numpy(output["global_rot_mats"][0]).to(device)
        local_rot_mats = global_rots_to_local_rots(joints_rot, skeleton)
        root_positions = joints_pos[:, skeleton.root_idx, :]
        save_motion_bvh(
            args.output + ".bvh",
            local_rot_mats,
            root_positions,
            skeleton=skeleton,
            fps=model.fps,
            standard_tpose=True,
        )
        print(f"saved {args.output}.bvh")

    print(f"RESULT load_s={t_load:.2f} gen_s={t_gen:.2f} peak_vram_gib={peak_vram:.3f}")


if __name__ == "__main__":
    main()
