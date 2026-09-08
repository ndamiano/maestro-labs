import bpy, sys, os, mathutils

argv = sys.argv[sys.argv.index('--') + 1:]
in_path, out_path, char_id = argv[0], argv[1], argv[2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=in_path)
arm_obj = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm = arm_obj.data

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
ebones = arm.edit_bones

children = {b.name: [] for b in ebones}
for b in ebones:
    if b.parent:
        children[b.parent.name].append(b.name)

root = [b for b in ebones if b.parent is None][0]

def head_z(name):
    return ebones[name].head.z

def tail_z(name):
    return ebones[name].tail.z

def head_x(name):
    return ebones[name].head.x

# split root's children into spine-up vs legs-down
kids = children[root.name]
spine_start = [k for k in kids if tail_z(k) >= root.head.z]
leg_starts = [k for k in kids if tail_z(k) < root.head.z]

name_map = {root.name: 'Hips'}

# walk spine, branching into arms when a spine bone has a lateral child
spine_names = ['Spine', 'Spine1', 'Spine2', 'Spine3', 'Spine4', 'Neck', 'Neck1', 'Head']
cur = spine_start[0] if spine_start else None
spine_idx = 0
arm_roots = []  # (side_hint_x, bone_name)
passed_shoulder_level = False

while cur is not None:
    kids_cur = children[cur]
    if len(kids_cur) >= 2 and not passed_shoulder_level:
        # lateral branches = arms (large |x| tail offset), continuation = highest tail_z
        lateral = [k for k in kids_cur if abs(head_x(k) - head_x(cur)) > 0.02]
        forward = [k for k in kids_cur if k not in lateral]
        for lat in lateral:
            arm_roots.append((head_x(lat), lat))
        passed_shoulder_level = True
        nxt_candidates = forward if forward else kids_cur
        nxt = max(nxt_candidates, key=tail_z) if nxt_candidates else None
    else:
        nxt = max(kids_cur, key=tail_z) if kids_cur else None

    label = spine_names[spine_idx] if spine_idx < len(spine_names) else f'Spine{spine_idx}'
    name_map[cur] = label
    spine_idx += 1
    cur = nxt

# any remaining head-chain extras
def label_extra_chain(start, base):
    n = 0
    node = start
    while node is not None:
        kids_n = children[node]
        name_map[node] = base if n == 0 else f'{base}{n}'
        n += 1
        node = kids_n[0] if kids_n else None

def side_of(x):
    return 'Right' if x > 0 else 'Left'

arm_chain_names = ['Shoulder', 'Arm', 'ForeArm', 'Hand']

def label_limb_chain(start, prefix, chain_names, side):
    node = start
    idx = 0
    stack = [(node, idx)]
    while stack:
        node, idx = stack.pop(0) if False else stack.pop()
        break
    # simple linear walk with branch handling for fingers/toes
    node = start
    idx = 0
    while node is not None:
        base = chain_names[idx] if idx < len(chain_names) else f'{prefix}Extra{idx - len(chain_names) + 1}'
        name_map[node] = f'{side}{base}'
        kids_n = children[node]
        idx += 1
        if len(kids_n) == 0:
            node = None
        elif len(kids_n) == 1:
            node = kids_n[0]
        else:
            # branch (e.g. fingers on a hand) -> label each sub-chain distinctly and stop main walk
            for fi, k in enumerate(kids_n):
                label_finger_chain(k, f'{side}Hand', fi + 1)
            node = None

def label_finger_chain(start, prefix, finger_idx):
    node = start
    n = 1
    while node is not None:
        name_map[node] = f'{prefix}Finger{finger_idx}_{n:02d}'
        kids_n = children[node]
        node = kids_n[0] if kids_n else None
        n += 1

for x, root_name in arm_roots:
    side = side_of(x)
    label_limb_chain(root_name, side, arm_chain_names, side)

leg_chain_names = ['UpLeg', 'Leg', 'Foot', 'ToeBase']
for leg_root in leg_starts:
    side = side_of(head_x(leg_root))
    label_limb_chain(leg_root, side, leg_chain_names, side)

# any bones never reached (shouldn't happen) get numbered fallback
for b in ebones:
    if b.name not in name_map:
        name_map[b.name] = f'Extra_{b.name}'

# apply renames (two-pass to avoid collisions with original bone_N names)
for old, new in name_map.items():
    ebones[old].name = f'__tmp__{new}'
for old, new in name_map.items():
    ebones[f'__tmp__{new}'].name = new

bpy.ops.object.mode_set(mode='OBJECT')

print(f'=== bone mapping for {char_id} ===')
for old, new in name_map.items():
    print(f'{old} -> {new}')

os.makedirs(os.path.dirname(out_path), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')
print('saved', out_path)
