import numpy as np

TRUEBONES_COND = "Anytop/dataset/truebones/zoo/truebones_processed/cond.npy"
KNIGHT_COND = "motion/knight_anytop/cond.npy"
OUT_COND = "motion/knight_anytop/cond_spliced.npy"

# Knight joint (our named rig) -> closest Monkey joint (nearest humanoid topology in Truebones)
MAP = {
    "Hips": "Bip01_Pelvis",
    "Spine": "Bip01_Spine",
    "Spine1": "Bip01_Spine1",
    "Spine2": "Bip01_Spine2",
    "Spine3": "Bip01_Neck",
    "Spine4": "Bip01_Head",
    "RightShoulder": "Bip01_R_Clavicle",
    "RightArm": "Bip01_R_UpperArm",
    "RightForeArm": "Bip01_R_Forearm",
    "RightHand": "Bip01_R_Hand",
    "RightHandFinger1_01": "Bip01_R_Finger1",
    "RightHandFinger1_02": "Bip01_R_Finger11",
    "RightHandFinger1_03": "Bip01_R_Finger12",
    "RightHandFinger2_01": "Bip01_R_Finger2",
    "RightHandFinger2_02": "Bip01_R_Finger21",
    "RightHandFinger2_03": "Bip01_R_Finger22",
    "LeftShoulder": "Bip01_L_Clavicle",
    "LeftArm": "Bip01_L_UpperArm",
    "LeftForeArm": "Bip01_L_Forearm",
    "LeftHand": "Bip01_L_Hand",
    "LeftHandFinger1_01": "Bip01_L_Finger1",
    "LeftHandFinger1_02": "Bip01_L_Finger11",
    "LeftHandFinger1_03": "Bip01_L_Finger12",
    "LeftHandFinger2_01": "Bip01_L_Finger2",
    "LeftHandFinger2_02": "Bip01_L_Finger21",
    "LeftHandFinger2_03": "Bip01_L_Finger22",
    "RightUpLeg": "Bip01_R_Thigh",
    "RightLeg": "Bip01_R_Calf",
    "RightFoot": "Bip01_R_Foot",
    "RightToeBase": "Bip01_R_Toe1",
    "LeftUpLeg": "Bip01_L_Thigh",
    "LeftLeg": "Bip01_L_Calf",
    "LeftFoot": "Bip01_L_Foot",
    "LeftToeBase": "Bip01_L_Toe1",
}

tb = np.load(TRUEBONES_COND, allow_pickle=True).item()
monkey = tb["Monkey"]
monkey_names = list(monkey["joints_names"])
monkey_idx = {n: i for i, n in enumerate(monkey_names)}

kc = np.load(KNIGHT_COND, allow_pickle=True).item()
knight = kc["Knight"]
knight_names = list(knight["joints_names"])

print("knight joints:", len(knight_names), "monkey joints:", len(monkey_names))

new_mean = knight["mean"].copy()
new_std = knight["std"].copy()

# non-root fallback = monkey's homogenized non-root std block (index 1, representative of all non-root joints)
fallback_mean_nonroot = monkey["mean"][1:].mean(axis=0)
fallback_std_nonroot = monkey["std"][1]  # already homogeneous across non-root joints per get_mean_std

matched, unmatched = [], []
for i, kn in enumerate(knight_names):
    mn = MAP.get(kn)
    if mn is not None and mn in monkey_idx:
        mi = monkey_idx[mn]
        new_mean[i] = monkey["mean"][mi]
        new_std[i] = monkey["std"][mi]
        matched.append(kn)
    else:
        if kn == "Hips":
            new_mean[i] = monkey["mean"][0]
            new_std[i] = monkey["std"][0]
        else:
            new_mean[i] = fallback_mean_nonroot
            new_std[i] = fallback_std_nonroot
        unmatched.append(kn)

print(f"matched {len(matched)}/{len(knight_names)}; unmatched (fallback): {unmatched}")

knight["mean"] = new_mean
knight["std"] = new_std
kc["Knight"] = knight

np.save(OUT_COND, kc)
print("saved", OUT_COND)
