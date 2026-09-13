"""Rig a T-posed humanoid from a TEMPLATE, not from what a network can find in the geometry.

A learned rigger reads limbs out of a mesh, so a knight whose shield welds to his torso comes
back with 22 bones and no arms, and a mage in a floor-length robe comes back with no legs. But we
CHOOSE the pose: in a T-pose the arms are horizontal at shoulder height and the legs are below the
hips, so the skeleton can be placed by measuring the silhouette instead of inferring it. Bones are
correct by construction and already carry Mixamo names; only the weights are computed, by
Blender's bone-heat.

usage: python template_rig.py -- <mesh.glb> <out.glb>
"""
import sys
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index('--') + 1:]
mesh_glb, out_glb = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=mesh_glb)
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
for m in meshes:
    m.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
if len(meshes) > 1:
    bpy.ops.object.join()
mesh = bpy.context.view_layer.objects.active

# the mesh's own measurements, in world space
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
verts = [mesh.matrix_world @ v.co for v in mesh.data.vertices]
xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
x0, x1 = min(xs), max(xs); z0, z1 = min(zs), max(zs)
H = z1 - z0
cx = (x0 + x1) / 2.0
cy = sum(ys) / len(ys)

def span_at(z_frac, tol=0.03):
    """how wide the body is at a height, so the shoulders and hips are measured not guessed"""
    z = z0 + H * z_frac
    band = [v for v in verts if abs(v.z - z) < H * tol]
    if not band:
        return 0.0, cx
    bx = [v.x for v in band]
    return max(bx) - min(bx), (max(bx) + min(bx)) / 2.0

arm_span, _ = span_at(0.80)          # arms are horizontal in a T-pose: the widest band
hip_w, _ = span_at(0.52)
shoulder_z = z0 + H * 0.80
hip_z = z0 + H * 0.52
half_arm = max(arm_span / 2.0, H * 0.18)
hip_off = max(hip_w * 0.25, H * 0.04)

# a canonical humanoid, proportioned to this mesh
CHAIN = [
    ("Hips",        None,           (cx, cy, hip_z)),
    ("Spine",       "Hips",         (cx, cy, hip_z + H * 0.09)),
    ("Spine1",      "Spine",        (cx, cy, hip_z + H * 0.18)),
    ("Spine2",      "Spine1",       (cx, cy, shoulder_z)),
    ("Neck",        "Spine2",       (cx, cy, shoulder_z + H * 0.05)),
    ("Head",        "Neck",         (cx, cy, shoulder_z + H * 0.10)),
    ("HeadTop",     "Head",         (cx, cy, z1)),
]
for side, s in (("Left", -1.0), ("Right", 1.0)):
    CHAIN += [
        (f"{side}Shoulder", "Spine2",            (cx + s * H * 0.05, cy, shoulder_z)),
        (f"{side}Arm",      f"{side}Shoulder",   (cx + s * half_arm * 0.32, cy, shoulder_z)),
        (f"{side}ForeArm",  f"{side}Arm",        (cx + s * half_arm * 0.66, cy, shoulder_z)),
        (f"{side}Hand",     f"{side}ForeArm",    (cx + s * half_arm * 0.92, cy, shoulder_z)),
        (f"{side}HandEnd",  f"{side}Hand",       (cx + s * half_arm, cy, shoulder_z)),
        (f"{side}UpLeg",    "Hips",              (cx + s * hip_off, cy, hip_z)),
        (f"{side}Leg",      f"{side}UpLeg",      (cx + s * hip_off, cy, z0 + H * 0.28)),
        (f"{side}Foot",     f"{side}Leg",        (cx + s * hip_off, cy, z0 + H * 0.04)),
        (f"{side}ToeBase",  f"{side}Foot",       (cx + s * hip_off, cy - H * 0.05, z0)),
    ]

arm = bpy.data.armatures.new("Armature")
rig = bpy.data.objects.new("Armature", arm)
bpy.context.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode='EDIT')
heads = {n: Vector(p) for n, _, p in CHAIN}
kids = {}
for n, par, _ in CHAIN:
    kids.setdefault(par, []).append(n)
for n, par, p in CHAIN:
    b = arm.edit_bones.new(n)
    b.head = heads[n]
    child = kids.get(n, [None])[0]
    b.tail = heads[child] if child else heads[n] + Vector((0, 0, H * 0.04))
    if (b.tail - b.head).length < 1e-4:
        b.tail = b.head + Vector((0, 0, H * 0.03))
for n, par, _ in CHAIN:
    if par:
        arm.edit_bones[n].parent = arm.edit_bones[par]
bpy.ops.object.mode_set(mode='OBJECT')
print(f"[template] height {H:.3f} arm span {arm_span:.3f} hips {hip_w:.3f} -> {len(CHAIN)} bones")

# Blender's bone heat reports success and writes ZERO weights on these meshes, so the weights are
# computed directly: a vertex belongs to the bones whose segment it is nearest, falling off with
# distance. Crude next to heat diffusion, and entirely adequate for a 128px sprite.
import numpy as np
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True); rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type='ARMATURE_NAME')      # modifier + groups, no weights

bones = [(b.name, np.array(b.head_local), np.array(b.tail_local)) for b in rig.data.bones]
V = np.array([[v.co.x, v.co.y, v.co.z] for v in mesh.data.vertices])
D = np.zeros((len(V), len(bones)))
for i, (_, h, t) in enumerate(bones):
    seg = t - h; L2 = float(seg @ seg) or 1e-9
    u = np.clip(((V - h) @ seg) / L2, 0.0, 1.0)[:, None]
    D[:, i] = np.linalg.norm(V - (h + u * seg), axis=1)

K = 3
order = np.argsort(D, axis=1)[:, :K]
groups = {n: mesh.vertex_groups[n] for n, _, _ in bones if n in mesh.vertex_groups}
for n, _, _ in bones:
    if n not in groups:
        groups[n] = mesh.vertex_groups.new(name=n)
eps = H * 0.02
for vi in range(len(V)):
    idx = order[vi]
    d = D[vi, idx] + eps
    w = (1.0 / d ** 4)
    w = w / w.sum()
    for k, bi in enumerate(idx):
        if w[k] > 0.005:
            groups[bones[bi][0]].add([vi], float(w[k]), 'REPLACE')
print(f"[template] weights: {len(V)} verts x {K} bones")

bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB',
                          use_selection=True, export_skins=True, export_yup=True)
print("[template] saved", out_glb)
