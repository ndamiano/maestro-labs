# Each pose value = {"bones": [(bone_name, world_axis, degrees), ...] applied
# parent-to-child, "hips_translate": (dx, dy, dz) optional}.
# Rest pose is an A-pose: arms point out to the sides (+x = Right bones, -x =
# Left bones). World-axis conventions used below (character faces -Y, Z up):
#   Y-axis rotation: swings an out-stretched arm down to the side
#     (+deg for Right-side bones, -deg for Left-side bones -> arm down).
#   X-axis rotation on an already-down arm/leg: swings it in the sagittal
#     plane (-deg = forward/toward -Y, +deg = backward).
#   Z-axis rotation on an already-down arm: swings it across the body
#     (+deg for Right-side, -deg for Left-side -> across to the front/other side).

POSES = {
    "idle": {
        "bones": [
            ("RightArm", "Y", 75),
            ("LeftArm", "Y", -75),
            ("RightForeArm", "X", -12),
            ("LeftForeArm", "X", -12),
        ],
    },
    "walk_a": {
        "bones": [
            ("LeftUpLeg", "X", -32),
            ("RightUpLeg", "X", 28),
            ("RightLeg", "X", -22),
            ("RightArm", "Y", 75),
            ("LeftArm", "Y", -75),
            ("RightArm", "X", -28),
            ("LeftArm", "X", 24),
            ("RightForeArm", "X", -15),
            ("LeftForeArm", "X", -10),
        ],
    },
    "walk_b": {
        "bones": [
            ("RightUpLeg", "X", -32),
            ("LeftUpLeg", "X", 28),
            ("LeftLeg", "X", -22),
            ("LeftArm", "Y", -75),
            ("RightArm", "Y", 75),
            ("LeftArm", "X", -28),
            ("RightArm", "X", 24),
            ("LeftForeArm", "X", -15),
            ("RightForeArm", "X", -10),
        ],
    },
    "attack_windup": {
        "bones": [
            ("Spine2", "Z", -22),
            ("Spine3", "Z", -14),
            ("RightArm", "Y", -100),
            ("RightArm", "X", -25),
            ("RightForeArm", "X", 60),
            ("LeftArm", "Y", -60),
            ("LeftForeArm", "X", -25),
            ("RightUpLeg", "X", 12),
        ],
    },
    "attack_strike": {
        "bones": [
            ("Spine1", "X", -12),
            ("Spine2", "Z", 18),
            ("RightArm", "Y", 55),
            ("RightArm", "X", -80),
            ("RightForeArm", "X", 5),
            ("LeftArm", "Y", -70),
            ("LeftArm", "X", 20),
            ("LeftUpLeg", "X", -30),
            ("RightUpLeg", "X", 15),
        ],
    },
    "block": {
        "bones": [
            ("LeftArm", "Y", -55),
            ("LeftArm", "X", -35),
            ("LeftArm", "Z", 40),
            ("LeftForeArm", "X", -95),
            ("RightArm", "Y", 70),
            ("RightArm", "X", -8),
            ("RightForeArm", "X", -15),
        ],
    },
    "hit": {
        "bones": [
            ("Spine1", "X", 18),
            ("Spine2", "X", 14),
            ("RightArm", "Y", 55),
            ("RightArm", "X", 40),
            ("LeftArm", "Y", -55),
            ("LeftArm", "X", 40),
            ("RightForeArm", "X", 20),
            ("LeftForeArm", "X", 20),
            ("RightUpLeg", "X", 18),
            ("LeftUpLeg", "X", -10),
        ],
        "hips_translate": (0, 0.05, -0.01),
    },
    "cast": {
        "bones": [
            ("RightArm", "Y", 80),
            ("RightArm", "X", -85),
            ("LeftArm", "Y", -80),
            ("LeftArm", "X", -85),
            ("RightForeArm", "X", -5),
            ("LeftForeArm", "X", -5),
            ("Spine1", "X", -6),
        ],
    },
    "jump": {
        "bones": [
            ("RightArm", "Y", 95),
            ("RightArm", "X", 70),
            ("LeftArm", "Y", -95),
            ("LeftArm", "X", 70),
            ("RightForeArm", "X", 30),
            ("LeftForeArm", "X", 30),
            ("RightUpLeg", "X", -75),
            ("LeftUpLeg", "X", -75),
            ("RightLeg", "X", 95),
            ("LeftLeg", "X", 95),
        ],
        "hips_translate": (0, 0, 0.28),
    },
    "death": {
        "bones": [
            ("Hips", "X", 92),
            ("RightArm", "Y", 70),
            ("LeftArm", "Y", -70),
            ("RightArm", "X", 8),
            ("LeftArm", "X", -8),
            ("RightForeArm", "X", -12),
            ("LeftForeArm", "X", 12),
            ("RightUpLeg", "X", -6),
            ("LeftUpLeg", "X", 6),
        ],
        "hips_translate": (0, 0, -0.32),
    },
}
