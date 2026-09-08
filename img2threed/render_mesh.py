"""Render GLB/OBJ meshes from the same orbit views as render_splat.py, with open3d offscreen.

    python render_mesh.py <out_png> <mesh> [<mesh> ...]   # one row per mesh
"""
import math, os, sys
os.environ.setdefault("EGL_PLATFORM", "surfaceless")
import numpy as np
import open3d as o3d
import open3d.visualization.rendering as R
from PIL import Image

RES = 512
VIEWS = [(35, 20), (125, 10), (215, 25)]


def load(path):
    if path.endswith(".glb"):
        m = o3d.io.read_triangle_model(path)
        return m, None
    mesh = o3d.io.read_triangle_mesh(path)
    mesh.compute_vertex_normals()
    return None, mesh


def bounds(model, mesh):
    if mesh is not None:
        return mesh.get_axis_aligned_bounding_box()
    bb = None
    for mi in model.meshes:
        b = mi.mesh.get_axis_aligned_bounding_box()
        bb = b if bb is None else bb + b
    return bb


def render(path):
    model, mesh = load(path)
    bb = bounds(model, mesh)
    center = bb.get_center()
    radius = float(np.linalg.norm(bb.get_extent()) / 2)
    r = R.OffscreenRenderer(RES, RES)
    r.scene.set_background([1, 1, 1, 1])
    r.scene.scene.set_sun_light([-0.4, -1, -0.6], [1, 1, 1], 60000)
    r.scene.scene.enable_sun_light(True)
    r.scene.scene.set_indirect_light_intensity(30000)
    if mesh is not None:
        mat = R.MaterialRecord(); mat.shader = "defaultLit"; mat.base_color = [0.8, 0.8, 0.8, 1]
        r.scene.add_geometry("m", mesh, mat)
        wire = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
        wire.paint_uniform_color([0.1, 0.1, 0.1])
        lm = R.MaterialRecord(); lm.shader = "unlitLine"; lm.line_width = 1
        r.scene.add_geometry("w", wire, lm)
    else:
        r.scene.add_model("m", model)
    fov = 40.0
    dist = radius / math.sin(math.radians(fov) / 2) * 1.05
    tiles = []
    for az, el in VIEWS:
        az_, el_ = math.radians(az), math.radians(el)
        eye = center + dist * np.array([math.cos(el_) * math.sin(az_), math.sin(el_), math.cos(el_) * math.cos(az_)])
        r.scene.camera.set_projection(fov, 1.0, 0.01, 100.0, R.Camera.FovType.Vertical)
        r.scene.camera.look_at(center, eye, [0, 1, 0])
        img = np.asarray(r.render_to_image())
        tiles.append(img[..., :3])
    return np.concatenate(tiles, 1)


out, meshes = sys.argv[1], sys.argv[2:]
rows = [render(m) for m in meshes]
Image.fromarray(np.concatenate(rows, 0)).save(out)
print(out)
