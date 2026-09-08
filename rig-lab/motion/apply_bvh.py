import bpy, sys, os, math

argv = sys.argv[sys.argv.index('--') + 1:]
named_glb, bvh_path, out_glb, frames_dir, strip_path, char_id = argv

bpy.ops.wm.read_factory_settings(use_empty=True)

bpy.ops.import_scene.gltf(filepath=named_glb)
target_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
target_arm.name = 'TargetArmature'

bpy.ops.import_anim.bvh(filepath=bvh_path, axis_forward='-Z', axis_up='Y', update_scene_fps=True)
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
matched = sorted(src_bone_names & tgt_bone_names)
print(f'matched {len(matched)} / {len(tgt_bone_names)} target bones by name')
missing = sorted(tgt_bone_names - src_bone_names)
if missing:
    print('unmatched target bones (kept static):', missing)

for f in range(frame_start, frame_end + 1):
    scene.frame_set(f)
    for name in matched:
        spb = src_arm.pose.bones[name]
        tpb = target_arm.pose.bones[name]
        tpb.rotation_mode = 'QUATERNION'
        if spb.rotation_mode == 'QUATERNION':
            tpb.rotation_quaternion = spb.rotation_quaternion.copy()
        else:
            tpb.rotation_quaternion = spb.rotation_euler.to_quaternion()
        if name == 'Hips':
            tpb.location = spb.location.copy()
        tpb.keyframe_insert(data_path='rotation_quaternion', frame=f)
        if name == 'Hips':
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
