import bpy, sys, os, math
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from poses import POSES
from pose_lib import apply_pose

RIGS = {
    "knight": "motion/knight_tex_named.glb",
    "troll": "motion/troll_tex_named.glb",
    "specter": "motion/specter_tex_named.glb",
}

OUT_DIR = "motion/poses"
os.makedirs(OUT_DIR, exist_ok=True)

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
only_poses = set(argv) if argv else set(POSES.keys())


def load_rig(path):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=path)
    for o in list(bpy.data.objects):
        if o.name.startswith("Icosphere"):
            bpy.data.objects.remove(o, do_unlink=True)
    arm = [o for o in bpy.data.objects if o.type == "ARMATURE"][0]
    return arm


def bounds(arm):
    meshes = [o for o in bpy.data.objects if o.type == "MESH"]
    lo = Vector((1e9,) * 3)
    hi = Vector((-1e9,) * 3)
    for m in meshes:
        for c in m.bound_box:
            w = m.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w))
            hi = Vector(map(max, hi, w))
    return lo, hi


def setup_render():
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "FLAT"
    sc.display.shading.color_type = "TEXTURE"
    sc.display.shading.show_cavity = True
    sc.display.shading.show_object_outline = True
    sc.render.resolution_x = 500
    sc.render.resolution_y = 500
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = "RGBA"


def render_view(arm, lo, hi, direction, out_path):
    sc = bpy.context.scene
    ctr = (lo + hi) / 2
    size = max((hi - lo).length, 0.5)
    for o in list(bpy.data.objects):
        if o.type == "CAMERA":
            bpy.data.objects.remove(o, do_unlink=True)
    cam = bpy.data.cameras.new("cam")
    cam.type = "ORTHO"
    cam.ortho_scale = size * 1.4
    co = bpy.data.objects.new("cam", cam)
    sc.collection.objects.link(co)
    co.location = ctr + Vector(direction).normalized() * size * 3
    co.rotation_euler = (ctr - co.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = co
    sc.render.filepath = out_path
    bpy.ops.render.render(write_still=True)


for rig_id, rig_path in RIGS.items():
    for pose_id, spec in POSES.items():
        if pose_id not in only_poses:
            continue
        arm = load_rig(rig_path)
        apply_pose(arm, spec)
        lo, hi = bounds(arm)
        setup_render()
        front_path = os.path.join(OUT_DIR, f"{rig_id}_{pose_id}_front.png")
        iso_path = os.path.join(OUT_DIR, f"{rig_id}_{pose_id}_iso.png")
        render_view(arm, lo, hi, (0, -1, 0), front_path)
        render_view(arm, lo, hi, (-1, -1, 0.6), iso_path)
        print("rendered", rig_id, pose_id)

print("DONE")
