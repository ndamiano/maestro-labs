"""Keyframe constraints for the verbs a game needs. The model fills in between them."""
import json, os, math
FPS = 30
OUT = os.path.dirname(os.path.abspath(__file__))
J = {n: i for i, n in enumerate("""Hips Spine1 Spine2 Chest Neck1 Neck2 Head Jaw LeftEye RightEye
LeftShoulder LeftArm LeftForeArm LeftHand LeftHandThumbEnd LeftHandMiddleEnd
RightShoulder RightArm RightForeArm RightHand RightHandThumbEnd RightHandMiddleEnd
LeftLeg LeftShin LeftFoot LeftToeBase RightLeg RightShin RightFoot RightToeBase""".split())}
NBJ, ROOT_Y = 30, 1.0

def pose(**kw):
    r = [[0.0, 0.0, 0.0] for _ in range(NBJ)]
    for name, xyz in kw.items():
        r[J[name]] = list(xyz)
    return r

def write(name, keys, secs, root_y=None):
    n = int(secs * FPS)
    idx = [min(n - 1, int(round(t * (n - 1)))) for t, _ in keys]
    data = [{
        "type": "fullbody",
        "frame_indices": idx,
        "local_joints_rot": [p for _, p in keys],
        "root_positions": [[0.0, (root_y[i] if root_y else ROOT_Y), 0.0] for i in range(len(keys))],
        "smooth_root_2d": [[0.0, 0.0] for _ in keys],
    }]
    p = os.path.join(OUT, f"constraints_{name}.json")
    json.dump(data, open(p, "w"), indent=1)
    print(f"wrote {name}: {len(keys)} keys over {secs}s ({n} frames)")

D = math.radians
# a sword swing: wind the right arm up and behind, strike down and across, recover
write("attack", [
    (0.00, pose()),
    (0.30, pose(RightArm=(D(-100), 0, D(-35)), RightForeArm=(D(-60), 0, 0), Chest=(0, D(-25), 0))),
    (0.55, pose(RightArm=(D(60), 0, D(20)), RightForeArm=(D(-10), 0, 0), Chest=(0, D(30), 0),
                Spine1=(D(12), 0, 0))),
    (1.00, pose()),
], 1.6)

# taking a hit: recoil back, then settle
write("hurt", [
    (0.00, pose()),
    (0.25, pose(Spine1=(D(-22), 0, 0), Chest=(D(-15), 0, 0), Head=(D(-18), 0, 0),
                LeftArm=(D(-25), 0, 0), RightArm=(D(-25), 0, 0))),
    (1.00, pose()),
], 0.9)

# death: legs buckle, torso folds, arms fall
write("death", [
    (0.00, pose()),
    (0.35, pose(LeftLeg=(D(35), 0, 0), RightLeg=(D(35), 0, 0), LeftShin=(D(-70), 0, 0),
                RightShin=(D(-70), 0, 0), Spine1=(D(25), 0, 0))),
    (1.00, pose(LeftLeg=(D(80), 0, 0), RightLeg=(D(80), 0, 0), LeftShin=(D(-95), 0, 0),
                RightShin=(D(-95), 0, 0), Spine1=(D(55), 0, 0), Chest=(D(25), 0, 0),
                Head=(D(20), 0, 0))),
], 1.4, root_y=[1.0, 0.55, 0.22])

# idle: weight settles, chest breathes, arms hang
write("idle", [
    (0.00, pose()),
    (0.50, pose(Spine1=(D(3), 0, 0), Chest=(D(2), 0, 0), LeftArm=(0, 0, D(3)), RightArm=(0, 0, D(-3)))),
    (1.00, pose()),
], 2.0)

# a two-handed cast: both arms come forward and up
write("cast", [
    (0.00, pose()),
    (0.45, pose(LeftArm=(D(-70), 0, D(20)), RightArm=(D(-70), 0, D(-20)),
                LeftForeArm=(D(-35), 0, 0), RightForeArm=(D(-35), 0, 0), Spine1=(D(-8), 0, 0))),
    (1.00, pose()),
], 1.5)
