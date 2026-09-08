"""TRELLIS 2 at 1024_cascade → RAW mesh → watertight 80 mm STL, in two processes.

    raw_trellis.py gen [ptype]   GPU: pipeline resident, dumps <name>.npz (vertices, faces) only
    raw_trellis.py fix           CPU: per npz, decimate to 1M, pymeshfix, scale, write STL

Two processes because the 1024 pipeline holds ~40 GB of host RAM and a 10M-face trimesh on top
of it takes the desktop down.
"""
import os, sys, glob, time, gc
O = "/home/nick/output/img2threed/fun"; R = f"{O}/stl_raw1024"; os.makedirs(R, exist_ok=True)
stage = sys.argv[1]

if stage == "gen":
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    os.environ["SPCONV_ALGO"] = "native"
    sys.path.insert(0, "/home/nick/cube3d-lab/trellis2")
    import torch
    try:
        import flex_gemm.kernels.triton as _fgk
        def _fwd(feats, indices, weight):
            idx = indices.long().clamp(0, feats.shape[0] - 1)
            return (feats[idx] * weight.unsqueeze(-1)).sum(dim=1)
        _fgk.indice_weighed_sum_fwd = _fwd
    except Exception as e:
        print("[patch] skipped:", e)
    import trellis2.modules.sparse.config as sparse_cfg
    import trellis2.modules.attention.config as attn_cfg
    sparse_cfg.ATTN = "sdpa"; attn_cfg.BACKEND = "sdpa"
    import numpy as np
    from PIL import Image
    from trellis2.pipelines import Trellis2ImageTo3DPipeline
    ptype = sys.argv[2] if len(sys.argv) > 2 else "1024_cascade"
    pipe = Trellis2ImageTo3DPipeline.from_pretrained("/home/nick/cube3d-lab/trellis2-weights"); pipe.cuda()
    for f in sorted(p for p in glob.glob(f"{O}/*.png") if not p.endswith(".render.png")):
        n = os.path.basename(f)[:-4]
        if os.path.exists(f"{R}/{n}.npz") or os.path.exists(f"{R}/{n}.stl"):
            continue
        t = time.time()
        with torch.inference_mode():
            mesh = pipe.run(Image.open(f), pipeline_type=ptype, seed=42)[0]
        v = mesh.vertices.detach().cpu().numpy().astype(np.float32); fc = mesh.faces.detach().cpu().numpy().astype(np.int32)
        np.savez(f"{R}/{n}.npz", v=v, f=fc)
        print(f"{n:20s} gen {time.time()-t:.0f}s raw F={len(fc)}", flush=True)
        del mesh, v, fc; gc.collect(); torch.cuda.empty_cache()

elif stage == "fix":
    import numpy as np, trimesh, pymeshfix
    for z in sorted(glob.glob(f"{R}/*.npz")):
        n = os.path.basename(z)[:-4]
        if os.path.exists(f"{R}/{n}.stl"):
            continue
        t = time.time(); d = np.load(z)
        m = trimesh.Trimesh(d["v"].astype(float), d["f"], process=True); m.merge_vertices()
        m = max(m.split(only_watertight=False), key=lambda b: len(b.faces))
        if len(m.faces) > 1_000_000:
            m = m.simplify_quadric_decimation(face_count=1_000_000)
        mf = pymeshfix.MeshFix(np.asarray(m.vertices, dtype=float), np.asarray(m.faces, dtype=np.int32))
        mf.repair(joincomp=True, remove_smallest_components=True)
        r = trimesh.Trimesh(mf.points, mf.faces); r.fix_normals(); r.apply_scale(80.0 / r.extents.max())
        r.export(f"{R}/{n}.stl")
        print(f"{n:20s} fix {time.time()-t:.0f}s F={len(r.faces)} watertight={r.is_watertight} {os.path.getsize(f'{R}/{n}.stl')//1_000_000}MB", flush=True)
        del m, r, mf, d; gc.collect()
