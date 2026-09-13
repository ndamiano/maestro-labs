"""Verbs authored as TRAJECTORIES, not joint angles.

Measured: a clip authored as sparse joint rotations comes back near-rest (attack: RightArm 20deg,
forearm 2deg, legs 3deg), while `death` — the one clip that also drove the root DOWN — came back
with a real collapse (knee 154deg, hip 80deg, spine 55deg). Kimodo fills in convincing full-body
motion around where the BODY GOES; it treats a joint angle as a weak suggestion. So every verb
here says where the root travels, and lets the model invent the limbs.
"""
import json, math, os
FPS = 30
OUT = os.path.dirname(os.path.abspath(__file__))
J = {n: i for i, n in enumerate("""Hips Spine1 Spine2 Chest Neck1 Neck2 Head Jaw LeftEye RightEye
LeftShoulder LeftArm LeftForeArm LeftHand LeftHandThumbEnd LeftHandMiddleEnd
RightShoulder RightArm RightForeArm RightHand RightHandThumbEnd RightHandMiddleEnd
LeftLeg LeftShin LeftFoot LeftToeBase RightLeg RightShin RightFoot RightToeBase""".split())}
NBJ = 30

def write(name, secs, xz, y=None, keys=None):
    n = int(secs * FPS)
    frames = list(range(n))
    data = [{"type": "root2d", "frame_indices": frames,
             "smooth_root_2d": [list(xz(i / (n - 1))) for i in frames]}]
    if y or keys:
        kf = keys or [(0.0, [[0.0]*3 for _ in range(NBJ)]), (1.0, [[0.0]*3 for _ in range(NBJ)])]
        idx = [min(n-1, int(round(t*(n-1)))) for t, _ in kf]
        data.append({"type": "fullbody", "frame_indices": idx,
                     "local_joints_rot": [p for _, p in kf],
                     "root_positions": [[0.0, (y(t) if y else 1.0), 0.0] for t, _ in kf],
                     "smooth_root_2d": [list(xz(t)) for t, _ in kf]})
    json.dump(data, open(os.path.join(OUT, f"constraints_{name}.json"), "w"), indent=1)
    print(f"authored {name}: {secs}s, {n} frames")

# a lunge: drive forward hard, plant, recover — the arm follows because the body does
write("attack2", 1.2, lambda t: [0.0, 0.55 * math.sin(math.pi * min(t / 0.55, 1.0)) if t < 0.55
                                 else 0.55 * (1 - (t - 0.55) / 0.45) * 0.6])
# recoil: thrown backwards, then step in to recover
write("hurt2", 0.9, lambda t: [0.0, -0.30 * math.sin(math.pi * min(t / 0.4, 1.0))])
# jump: no travel, the root leaves the ground
write("jump2", 1.1, lambda t: [0.0, 0.15 * t],
      y=lambda t: 1.0 - 0.25 * math.sin(math.pi * min(t / 0.25, 1.0)) if t < 0.25
      else (1.0 + 0.55 * math.sin(math.pi * (t - 0.25) / 0.5) if t < 0.75 else 1.0))
# run: four metres in a second and a half
write("run2", 1.5, lambda t: [0.0, 4.0 * t])
# a sidestep, for a dodge
write("dodge2", 0.8, lambda t: [1.1 * math.sin(math.pi * min(t / 0.5, 1.0)), 0.0])
# idle: almost nothing, a slow weight shift
write("idle2", 2.4, lambda t: [0.04 * math.sin(2 * math.pi * t), 0.0])
