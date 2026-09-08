import bpy, math
from mathutils import Matrix

AXIS_MAP = {"X": (1, 0, 0), "Y": (0, 1, 0), "Z": (0, 0, 1)}


def apply_world_rotation(arm_obj, bone_name, axis, degrees):
    """Rotate a pose bone by `degrees` about the world-space `axis` (X/Y/Z),
    pivoting on the bone's CURRENT (already-posed) head. Bones must be applied
    parent-to-child so a parent's rotation is baked into the child's starting
    matrix before the child is rotated."""
    pb = arm_obj.pose.bones[bone_name]
    M = pb.matrix.copy()
    head = M.translation.copy()
    R = (
        Matrix.Translation(head)
        @ Matrix.Rotation(math.radians(degrees), 4, axis)
        @ Matrix.Translation(-head)
    )
    pb.matrix = R @ M
    bpy.context.view_layer.update()


def apply_pose(arm_obj, spec):
    """spec: {"bones": [(bone_name, axis, degrees), ...] in parent->child order,
              "hips_translate": (dx, dy, dz) optional}"""
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="POSE")
    bpy.ops.pose.select_all(action="SELECT")
    bpy.ops.pose.transforms_clear()
    bpy.context.view_layer.update()
    for bone_name, axis, degrees in spec.get("bones", []):
        if bone_name not in arm_obj.pose.bones:
            continue
        apply_world_rotation(arm_obj, bone_name, axis, degrees)
    if "hips_translate" in spec and "Hips" in arm_obj.pose.bones:
        hips = arm_obj.pose.bones["Hips"]
        dx, dy, dz = spec["hips_translate"]
        hips.location.x += dx
        hips.location.y += dy
        hips.location.z += dz
        bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode="OBJECT")
