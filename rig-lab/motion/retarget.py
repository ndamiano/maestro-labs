"""Retarget a BVH onto a named rig, correctly.

The earlier script mapped joint NAMES but applied the source's LOCAL rotations directly, so a
figure rigged in a T-pose with SkinTokens' arbitrary bone rolls came out lying on its side with
its arms overhead. A rotation in a BVH is relative to the SOURCE skeleton's rest pose; what
carries across is the DELTA from that rest, expressed in world space:

    delta      = src_pose_world @ src_rest_world⁻¹
    tgt_world  = delta @ tgt_rest_world

The target's own rest pose supplies everything the source cannot know — where its arms point,
how its bones roll. Bones are set parent-first, because a parent's matrix moves its children.

usage: python retarget.py -- <named.glb> <clip.bvh> <out.glb> [--in-place] [--frames N]
"""
import sys, math
import bpy
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index('--') + 1:]
named_glb, bvh_path, out_glb = argv[0], argv[1], argv[2]
IN_PLACE = "--in-place" in argv
MAXF = int(argv[argv.index("--frames") + 1]) if "--frames" in argv else 0

# SOMA (kimodo) -> our Mixamo-style names, from label_bones.py
# SOMA's left is our right in world space (measured: SOMA LeftArm points +X, ours -X), so the
# sides are crossed here rather than silently mirroring every rotation.
MAP = {
    'Hips': 'Hips', 'Spine1': 'Spine', 'Spine2': 'Spine1', 'Chest': 'Spine2',
    'Neck1': 'Spine3', 'Neck2': 'Spine4',
    'LeftShoulder': 'RightShoulder', 'LeftArm': 'RightArm',
    'LeftForeArm': 'RightForeArm', 'LeftHand': 'RightHand',
    'LeftLeg': 'RightUpLeg', 'LeftShin': 'RightLeg', 'LeftFoot': 'RightFoot',
    'LeftToeBase': 'RightToeBase',
    'RightShoulder': 'LeftShoulder', 'RightArm': 'LeftArm',
    'RightForeArm': 'LeftForeArm', 'RightHand': 'LeftHand',
    'RightLeg': 'LeftUpLeg', 'RightShin': 'LeftLeg', 'RightFoot': 'LeftFoot',
    'RightToeBase': 'LeftToeBase',
}

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=named_glb)
tgt = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
tgt.name = "TARGET"

before = set(bpy.data.objects)
bpy.ops.import_anim.bvh(filepath=bvh_path, axis_forward='-Z', axis_up='Y',
                        rotate_mode='QUATERNION', use_fps_scale=False,
                        update_scene_fps=True, update_scene_duration=True)
src = [o for o in bpy.data.objects if o not in before and o.type == 'ARMATURE'][0]
src.name = "SOURCE"

pairs = [(s, t) for s, t in MAP.items()
         if s in src.pose.bones and t in tgt.pose.bones]
missing = [s for s in MAP if s not in src.pose.bones] + [t for t in MAP.values() if t not in tgt.pose.bones]
print(f"[retarget] mapped {len(pairs)} bones; missing: {sorted(set(missing))}")

# parent-first, so a parent's new matrix is in place before its children are set
depth = {t: len(tgt.pose.bones[t].parent_recursive) for _, t in pairs}
pairs.sort(key=lambda p: depth[p[1]])

def world(obj, pb):   return obj.matrix_world @ pb.matrix
def rest(obj, pb):    return obj.matrix_world @ pb.bone.matrix_local

scene = bpy.context.scene
f0, f1 = scene.frame_start, scene.frame_end
if MAXF: f1 = min(f1, f0 + MAXF - 1)
print(f"[retarget] frames {f0}..{f1}")

# scale between skeletons, from hip height at rest
def skel_height(obj):
    zs = [rest(obj, pb).to_translation().z for pb in obj.pose.bones]
    return max(zs) - min(zs)
src_h, tgt_h = skel_height(src), skel_height(tgt)
scale = (tgt_h / src_h) if src_h else 1.0
print(f"[retarget] hip heights src {src_h:.3f} tgt {tgt_h:.3f} -> scale {scale:.3f}")

# A BVH's armature REST is the raw offset skeleton, not a T-pose, so the reference for the source
# is its POSE on a chosen frame (the clip's first frame, or a standard T-pose clip) — otherwise the
# delta carries the stick-rest-to-pose rotation and double-rotates an already-T-posed target.
REF = int(argv[argv.index("--ref-frame") + 1]) if "--ref-frame" in argv else f0
REF_BVH = argv[argv.index("--ref-bvh") + 1] if "--ref-bvh" in argv else None
rest_offsets = {}
if REF_BVH:
    # the skeleton's own standard T-pose, so the reference matches the target's rest and the
    # delta carries only what the clip actually does
    before2 = set(bpy.data.objects)
    bpy.ops.import_anim.bvh(filepath=REF_BVH, axis_forward='-Z', axis_up='Y',
                            rotate_mode='QUATERNION', use_fps_scale=False)
    ref = [o for o in bpy.data.objects if o not in before2 and o.type == 'ARMATURE'][0]
    scene.frame_set(scene.frame_start)
    for s, t in pairs:
        rest_offsets[t] = (world(ref, ref.pose.bones[s]), rest(tgt, tgt.pose.bones[t]))
    bpy.data.objects.remove(ref, do_unlink=True)
    print(f"[retarget] source reference = {REF_BVH}")
else:
    scene.frame_set(REF)
    for s, t in pairs:
        rest_offsets[t] = (world(src, src.pose.bones[s]), rest(tgt, tgt.pose.bones[t]))
    print(f"[retarget] source reference = clip frame {REF}")

bpy.context.view_layer.objects.active = tgt
bpy.ops.object.mode_set(mode='POSE')
hips_rest = rest(tgt, tgt.pose.bones['Hips']).to_translation()
src_hips_rest = rest(src, src.pose.bones[[s for s,_ in pairs if _=='Hips'][0]]).to_translation()

ground = None
for f in range(f0, f1 + 1):
    scene.frame_set(f)
    for s, t in pairs:
        sb, tb = src.pose.bones[s], tgt.pose.bones[t]
        src_rest_w, tgt_rest_w = rest_offsets[t]
        delta = world(src, sb) @ src_rest_w.inverted()
        want = delta @ tgt_rest_w
        rot = want.to_quaternion().to_matrix().to_4x4()
        if t == 'Hips':
            travel = (world(src, sb).to_translation() - src_hips_rest) * scale
            if IN_PLACE:
                travel.x = 0.0; travel.y = 0.0        # keep the vertical bob only
                # ...and the turn, or a curved clip walks the sprite out of its own facing
                e = rot.to_euler('ZYX'); e.z = 0.0
                rot = e.to_matrix().to_4x4()
            loc = hips_rest + travel
        else:
            loc = tb.matrix.to_translation()
        tb.matrix = Matrix.Translation(loc) @ rot
        bpy.context.view_layer.update()
    # the retarget preserves the hips' height, not the feet's, so a clip whose skeleton has
    # different leg lengths floats or sinks; plant the lower foot at its rest height instead
    feet = [tgt.pose.bones[n] for n in ('LeftToeBase','RightToeBase','LeftFoot','RightFoot')
            if n in tgt.pose.bones]
    if feet:
        low = min(world(tgt, fb).to_translation().z for fb in feet)
        if f == f0:
            ground = low
        hb = tgt.pose.bones['Hips']
        m = hb.matrix.copy(); m.translation.z += (ground - low)
        hb.matrix = m
        bpy.context.view_layer.update()
    for _, t in pairs:
        tb = tgt.pose.bones[t]
        tb.rotation_mode = 'QUATERNION'
        tb.keyframe_insert('rotation_quaternion', frame=f)
        if t == 'Hips':
            tb.keyframe_insert('location', frame=f)

# one walk cycle: the shift L that makes the pose repeat most closely
import json as _json
poses = {}
for f in range(f0, f1 + 1):
    scene.frame_set(f)
    poses[f] = [tgt.pose.bones[t].rotation_quaternion.copy() for _, t in pairs]
best = None
span = f1 - f0 + 1
for L in range(max(4, span // 12), span // 2):
    errs = []
    for f in range(f0, f1 + 1 - L):
        errs.append(sum(min((a - b).magnitude, (a + b).magnitude)
                        for a, b in zip(poses[f], poses[f + L])) / len(pairs))
    e = sum(errs) / len(errs)
    if best is None or e < best[0]:
        best = (e, L)
cycle = {"frame_start": f0, "frame_end": f1, "fps": scene.render.fps,
         "cycle_frames": best[1], "cycle_error": round(best[0], 4)}
print(f"[retarget] cycle = {best[1]} frames (residual {best[0]:.4f})")
open(out_glb.rsplit('.', 1)[0] + '.cycle.json', 'w').write(_json.dumps(cycle, indent=1))

bpy.ops.object.mode_set(mode='OBJECT')
bpy.data.objects.remove(src, do_unlink=True)
# the BVH's own action targets bones of the SAME names in centimetres; exporting it would ship a
# second clip that undoes the retarget
keep = tgt.animation_data.action if tgt.animation_data else None
for act in list(bpy.data.actions):
    if act is not keep:
        bpy.data.actions.remove(act)
if keep: keep.name = "walk"
scene.frame_end = f1
bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB',
                          export_animations=True, export_frame_range=True)
print("[retarget] saved", out_glb)
