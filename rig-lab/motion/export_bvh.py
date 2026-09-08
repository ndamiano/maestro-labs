import bpy, sys, os

argv = sys.argv[sys.argv.index('--') + 1:]
in_path, out_path = argv[0], argv[1]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=in_path)
arm_obj = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

bpy.context.view_layer.objects.active = arm_obj
arm_obj.select_set(True)
bpy.ops.object.mode_set(mode='POSE')

action = bpy.data.actions.new(name='rest')
arm_obj.animation_data_create()
arm_obj.animation_data.action = action
for pb in arm_obj.pose.bones:
    pb.keyframe_insert(data_path='rotation_quaternion', frame=1)
    pb.keyframe_insert(data_path='location', frame=1)
    pb.keyframe_insert(data_path='rotation_quaternion', frame=2)
    pb.keyframe_insert(data_path='location', frame=2)

bpy.ops.object.mode_set(mode='OBJECT')

bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 2

os.makedirs(os.path.dirname(out_path), exist_ok=True)
bpy.ops.export_anim.bvh(filepath=out_path, frame_start=1, frame_end=2, root_transform_only=False)
print('saved', out_path)
