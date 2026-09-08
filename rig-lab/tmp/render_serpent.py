import bpy, sys, math, mathutils
glb = sys.argv[-2]; out_png = sys.argv[-1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
minv = mathutils.Vector((1e9,1e9,1e9)); maxv = mathutils.Vector((-1e9,-1e9,-1e9))
for o in meshes:
    for c in o.bound_box:
        wc = o.matrix_world @ mathutils.Vector(c)
        minv.x,minv.y,minv.z = min(minv.x,wc.x), min(minv.y,wc.y), min(minv.z,wc.z)
        maxv.x,maxv.y,maxv.z = max(maxv.x,wc.x), max(maxv.y,wc.y), max(maxv.z,wc.z)
center = (minv+maxv)/2; size = maxv-minv
radius = max(size.x,size.y,size.z)*1.6
cam_data = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_data)
bpy.context.scene.collection.objects.link(cam)
cam.location = (center.x, center.y, center.z+radius)
cam.rotation_euler = (0,0,0)
bpy.context.scene.camera = cam
light_data = bpy.data.lights.new("light", type='SUN'); light_data.energy=3.0
light = bpy.data.objects.new("light", light_data)
bpy.context.scene.collection.objects.link(light)
light.location = (center.x, center.y-radius, center.z+radius)
light.rotation_euler=(math.radians(45),0,0)
bpy.context.scene.render.engine='BLENDER_WORKBENCH'
bpy.context.scene.render.resolution_x=512; bpy.context.scene.render.resolution_y=512
bpy.context.scene.render.filepath=out_png
bpy.context.scene.render.image_settings.file_format='PNG'
bpy.ops.render.render(write_still=True)
