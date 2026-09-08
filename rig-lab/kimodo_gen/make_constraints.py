import json, math, os

FPS = 30
OUT = os.path.dirname(__file__)

def root2d(name, xz_fn, n_frames):
    frame_indices = list(range(n_frames))
    smooth_root_2d = [xz_fn(i) for i in frame_indices]
    data = [{
        "type": "root2d",
        "frame_indices": frame_indices,
        "smooth_root_2d": smooth_root_2d,
    }]
    path = os.path.join(OUT, f"{name}.json")
    json.dump(data, open(path, "w"), indent=2)
    print("wrote", path, "n_frames", n_frames)

# straight line: 2m forward (z) over 3s (90 frames @30fps)
n = int(3.0 * FPS)
root2d("constraints_path_straight", lambda i: [0.0, 2.0 * i / (n - 1)], n)

# curved path: gentle rightward arc, same 2m arc-length-ish over 3s
R = 1.3
theta_max = 2.0 / R  # arc length / radius
root2d("constraints_path_curved", lambda i: [
    R * (1 - math.cos(theta_max * i / (n - 1))),
    R * math.sin(theta_max * i / (n - 1)),
], n)

# full-body keyframes: T-pose -> arm raised, in place, 2s (60 frames)
NBJ = 30  # SOMASkeleton30 joint count
LEFT_ARM_IDX = 11  # bone_order_names_with_parents index of "LeftArm"
kf_n = int(2.0 * FPS)
zero_rot = [0.0, 0.0, 0.0]
frame0_rots = [list(zero_rot) for _ in range(NBJ)]
frame1_rots = [list(zero_rot) for _ in range(NBJ)]
frame1_rots[LEFT_ARM_IDX] = [0.0, 0.0, -1.45]  # ~-83 deg about local Z: raise arm from T-pose

root_y = 1.0  # meters, from somaskel77_standard_tpose.bvh Hips OFFSET Y=100cm
data = [{
    "type": "fullbody",
    "frame_indices": [0, kf_n - 1],
    "local_joints_rot": [frame0_rots, frame1_rots],
    "root_positions": [[0.0, root_y, 0.0], [0.0, root_y, 0.0]],
    "smooth_root_2d": [[0.0, 0.0], [0.0, 0.0]],
}]
path = os.path.join(OUT, "constraints_keyframe.json")
json.dump(data, open(path, "w"), indent=2)
print("wrote", path, "n_frames total (duration)", kf_n)
