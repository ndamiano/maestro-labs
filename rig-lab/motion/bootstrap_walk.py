import bpy, sys, os, math

argv = sys.argv[sys.argv.index('--') + 1:]
named_glb, out_bvh = argv[0], argv[1]

N_FRAMES = 48
FPS = 24

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=named_glb)
arm_obj = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

bpy.context.scene.render.fps = FPS
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = N_FRAMES

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')

pbones = arm_obj.pose.bones
for pb in pbones:
    pb.rotation_mode = 'XYZ'

hips = pbones['Hips']
hips_rest_z = hips.bone.head_local.z

action = bpy.data.actions.new(name='crude_walk')
arm_obj.animation_data_create()
arm_obj.animation_data.action = action

def deg(d):
    return math.radians(d)

for f in range(1, N_FRAMES + 1):
    bpy.context.scene.frame_set(f)
    t = (f - 1) / N_FRAMES  # 0..1 over one full gait cycle
    phase = 2 * math.pi * t

    # hips: bob (2x per cycle, one per footfall) + forward translation
    bob = 0.02 * hips_rest_z * abs(math.sin(phase * 2))
    hips.location = (0.0, 0.0, bob)
    hips.keyframe_insert('location', frame=f)

    # legs: antiphase swing, knee bends on the swing (lift) half
    for side, sign in (('Right', 1.0), ('Left', -1.0)):
        leg_phase = phase + (0 if sign > 0 else math.pi)
        up_leg_angle = deg(25) * math.sin(leg_phase)
        pbones[f'{side}UpLeg'].rotation_euler = (up_leg_angle, 0.0, 0.0)
        pbones[f'{side}UpLeg'].keyframe_insert('rotation_euler', frame=f)

        swing = max(0.0, math.sin(leg_phase))  # 0..1 on the forward-swing half
        knee_angle = deg(40) * swing
        pbones[f'{side}Leg'].rotation_euler = (-knee_angle, 0.0, 0.0)
        pbones[f'{side}Leg'].keyframe_insert('rotation_euler', frame=f)

        arm_angle = deg(20) * math.sin(leg_phase + math.pi)  # antiphase to same-side leg
        pbones[f'{side}Arm'].rotation_euler = (arm_angle, 0.0, 0.0)
        pbones[f'{side}Arm'].keyframe_insert('rotation_euler', frame=f)

bpy.ops.object.mode_set(mode='OBJECT')

os.makedirs(os.path.dirname(out_bvh), exist_ok=True)
bpy.ops.export_anim.bvh(filepath=out_bvh, frame_start=1, frame_end=N_FRAMES, root_transform_only=False)
print('saved', out_bvh)
