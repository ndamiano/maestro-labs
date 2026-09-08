"""Run TripoSplat on every PNG in samples/, write PLY + preprocessed image + timing."""
import sys, time, json, os
sys.path.insert(0, "/home/nick/cube3d-lab/triposplat")
os.chdir("/home/nick/cube3d-lab/triposplat")
import torch
from triposplat import TripoSplatPipeline

S = "/home/nick/output/img2threed/samples"
OUT = "/home/nick/output/img2threed/triposplat"
os.makedirs(OUT, exist_ok=True)

t0 = time.time()
pipe = TripoSplatPipeline(
    ckpt_path="ckpts/diffusion_models/triposplat_fp16.safetensors",
    decoder_path="ckpts/vae/triposplat_vae_decoder_fp16.safetensors",
    dinov3_path="ckpts/clip_vision/dino_v3_vit_h.safetensors",
    flux2_vae_encoder_path="ckpts/vae/flux2-vae.safetensors",
    rmbg_path="ckpts/background_removal/birefnet.safetensors",
    device="cuda",
)
print(f"load {time.time()-t0:.1f}s", flush=True)
timing = {"load_s": round(time.time() - t0, 1)}
counts = [32768, 262144]
for f in sorted(os.listdir(S)):
    if not f.endswith(".png"):
        continue
    name = f[:-4]
    torch.cuda.reset_peak_memory_stats()
    t = time.time()
    gs, prepared = pipe.run(f"{S}/{f}", num_gaussians=counts, show_progress=False)
    torch.cuda.synchronize()
    dt = time.time() - t
    prepared.save(f"{OUT}/{name}.prepared.webp")
    for n, g in zip(counts, gs):
        g.save_ply(f"{OUT}/{name}.{n}.ply")
    peak = torch.cuda.max_memory_allocated() / 2**30
    timing[name] = {"s": round(dt, 1), "peak_gib": round(peak, 1)}
    print(name, timing[name], flush=True)
json.dump(timing, open(f"{OUT}/timing.json", "w"), indent=1)
