"""Render every 3DGS PLY in triposplat/ from fixed orbit views with gsplat."""
import math, os, sys
import numpy as np
import torch
from PIL import Image
from plyfile import PlyData
from gsplat import rasterization

D = "/home/nick/output/img2threed/triposplat"
RES = 512
VIEWS = [("q", 35, 20), ("side", 125, 10), ("back", 215, 25)]  # name, azimuth, elevation


def load(path):
    v = PlyData.read(path)["vertex"]
    g = lambda k: torch.tensor(np.asarray(v[k]), dtype=torch.float32)
    means = torch.stack([g("x"), g("y"), g("z")], -1)
    C0 = 0.28209479177387814
    colors = torch.stack([g("f_dc_0"), g("f_dc_1"), g("f_dc_2")], -1) * C0 + 0.5
    opac = torch.sigmoid(g("opacity"))
    scales = torch.exp(torch.stack([g("scale_0"), g("scale_1"), g("scale_2")], -1))
    quats = torch.stack([g("rot_0"), g("rot_1"), g("rot_2"), g("rot_3")], -1)
    return means, quats, scales, opac, colors.clamp(0, 1)


def camera(az, el, dist, center):
    az, el = math.radians(az), math.radians(el)
    eye = center + dist * np.array([math.cos(el) * math.sin(az), math.sin(el), math.cos(el) * math.cos(az)])
    f = center - eye; f /= np.linalg.norm(f)
    up = np.array([0, -1, 0.0])
    r = np.cross(f, up); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    # OpenCV convention: x right, y down, z forward
    R = np.stack([r, -u, f], 0)
    t = -R @ eye
    w2c = np.eye(4); w2c[:3, :3] = R; w2c[:3, 3] = t
    return torch.tensor(w2c, dtype=torch.float32)


dev = "cuda"
for f in sorted(os.listdir(D)):
    if not f.endswith(".ply"):
        continue
    means, quats, scales, opac, colors = [t.to(dev) for t in load(f"{D}/{f}")]
    center = means.mean(0).cpu().numpy()
    radius = float((means - means.mean(0)).norm(dim=1).quantile(0.98))
    fov = 40.0
    focal = RES / (2 * math.tan(math.radians(fov) / 2))
    K = torch.tensor([[focal, 0, RES / 2], [0, focal, RES / 2], [0, 0, 1]], dtype=torch.float32, device=dev)
    dist = radius / math.sin(math.radians(fov) / 2) * 1.05
    tiles = []
    for name, az, el in VIEWS:
        w2c = camera(az, el, dist, center).to(dev)
        img, alpha, _ = rasterization(means, quats, scales, opac, colors, w2c[None], K[None], RES, RES)
        rgb = img[0, ..., :3] + (1 - alpha[0])
        tiles.append((rgb.clamp(0, 1).cpu().numpy() * 255).astype(np.uint8))
    sheet = np.concatenate(tiles, 1)
    Image.fromarray(sheet).save(f"{D}/{f[:-4]}.render.png")
    print(f, "ok", flush=True)
