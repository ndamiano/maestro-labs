import bpy, sys, os, math

argv = sys.argv[sys.argv.index('--') + 1:]
named_glb, bvh_path, out_glb, frames_dir, strip_path, char_id = argv

# SOMA (somaskel77) -> knight_named.glb (mixamo-style) bone name map, ~20 major joints.
# Confirmed from kimodo/assets/skeletons/somaskel77/somaskel77_standard_tpose.bvh joint
# names and the target armature's actual pose-bone names (read via bpy, see report).
SOMA_TO_TARGET = {
    'Hips': 'Hips',
    'Spine1': 'Spine',
    'Spine2': 'Spine1',
    'Chest': 'Spine2',
    'Neck1': 'Spine3',
    'Neck2': 'Spine4',
    'LeftShoulder': 'LeftShoulder',
    'LeftArm': 'LeftArm',
    'LeftForeArm': 'LeftForeArm',
    'LeftHand': 'LeftHand',
    'LeftLeg': 'LeftUpLeg',
    'LeftShin': 'LeftLeg',
    'LeftFoot': 'LeftFoot',
    'LeftToeBase': 'LeftToeBase',
    'RightShoulder': 'RightShoulder',
    'RightArm': 'RightArm',
    'RightForeArm': 'RightForeArm',
    'RightHand': 'RightHand',
    'RightLeg': 'RightUpLeg',
    'RightShin': 'RightLeg',
    'RightFoot': 'RightFoot',
    'RightToeBase': 'RightToeBase',
}

bpy.ops.wm.read_factory_settings(use_empty=True)

bpy.ops.import_scene.gltf(filepath=named_glb)
target_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
target_arm.name = 'TargetArmature'

# Kimodo BVH export uses centimeter units (Hips offset ~100 = 1m hip height,
# confirmed against somaskel77_standard_tpose.bvh); global_scale converts to meters.
bpy.ops.import_anim.bvh(filepath=bvh_path, axis_forward='-Z', axis_up='Y', update_scene_fps=True, global_scale=0.01)
src_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o.name != 'TargetArmature'][0]

scene = bpy.context.scene
frame_start = int(src_arm.animation_data.action.frame_range[0])
frame_end = int(src_arm.animation_data.action.frame_range[1])
scene.frame_start = frame_start
scene.frame_end = frame_end

target_arm.animation_data_create()
target_action = bpy.data.actions.new(name='retarget')
target_arm.animation_data.action = target_action

src_bone_names = {b.name for b in src_arm.pose.bones}
tgt_bone_names = {b.name for b in target_arm.pose.bones}
pairs = [(s, t) for s, t in SOMA_TO_TARGET.items() if s in src_bone_names and t in tgt_bone_names]
print(f'matched {len(pairs)} / {len(tgt_bone_names)} target bones via SOMA name map')
missing = sorted(tgt_bone_names - {t for _, t in pairs})
if missing:
    print('unmatched target bones (kept static):', missing)

# Rest-pose correction: SOMA's rest is a T-pose (arms straight out), the target rig's
# rest is a relaxed A-pose (arms down) with different per-bone roll/axis conventions.
# A raw rotation_quaternion copy is defined in each bone's own local rest frame, so it
# must be re-expressed in the target bone's local frame via a per-bone conjugation by
# the fixed offset between the two rest orientations (both taken in armature/object
# space, which src and tgt share since both are imported into the same scene).
corrections = {}
for src_name, tgt_name in pairs:
    # Bone.matrix (parent-relative rest) matches the space PoseBone.rotation_quaternion
    # is defined in -- Bone.matrix_local (armature-cumulative) does not.
    src_rest_q = src_arm.data.bones[src_name].matrix.to_quaternion()
    tgt_rest_q = target_arm.data.bones[tgt_name].matrix.to_quaternion()
    corrections[(src_name, tgt_name)] = tgt_rest_q.inverted() @ src_rest_q

for f in range(frame_start, frame_end + 1):
    scene.frame_set(f)
    for src_name, tgt_name in pairs:
        spb = src_arm.pose.bones[src_name]
        tpb = target_arm.pose.bones[tgt_name]
        tpb.rotation_mode = 'QUATERNION'
        if spb.rotation_mode == 'QUATERNION':
            src_local_q = spb.rotation_quaternion.copy()
        else:
            src_local_q = spb.rotation_euler.to_quaternion()
        corr = corrections[(src_name, tgt_name)]
        tpb.rotation_quaternion = corr @ src_local_q @ corr.inverted()
        if tgt_name == 'Hips':
            tpb.location = spb.location.copy()
        tpb.keyframe_insert(data_path='rotation_quaternion', frame=f)
        if tgt_name == 'Hips':
            tpb.keyframe_insert(data_path='location', frame=f)

bpy.data.objects.remove(src_arm, do_unlink=True)

os.makedirs(os.path.dirname(out_glb), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out_glb, export_format='GLB', export_animations=True)
print('saved', out_glb)

# --- render 8 evenly spaced frames ---
os.makedirs(frames_dir, exist_ok=True)
scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x = 600
scene.render.resolution_y = 600
scene.render.image_settings.file_format = 'PNG'

bpy.ops.object.camera_add(location=(2.2, -2.6, 1.4), rotation=(math.radians(72), 0, math.radians(40)))
cam = bpy.context.object
scene.camera = cam

sun_data = bpy.data.lights.new('sun', type='SUN')
sun = bpy.data.objects.new('sun', sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(30))

n_frames_to_render = 8
step = max(1, (frame_end - frame_start) // (n_frames_to_render - 1))
render_frames = [frame_start + i * step for i in range(n_frames_to_render)]
render_frames = [min(f, frame_end) for f in render_frames]

out_paths = []
for i, f in enumerate(render_frames):
    scene.frame_set(f)
    path = os.path.join(frames_dir, f'{char_id}_{i}.png')
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    out_paths.append(path)

from PIL import Image
imgs = [Image.open(p) for p in out_paths]
w, h = imgs[0].size
strip = Image.new('RGB', (w * len(imgs), h), 'white')
for i, im in enumerate(imgs):
    strip.paste(im.convert('RGB'), (i * w, 0))
strip.save(strip_path)
print('saved', strip_path)
