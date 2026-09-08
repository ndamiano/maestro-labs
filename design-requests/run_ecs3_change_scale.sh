#!/usr/bin/env bash
# --change on the 3D skyrim: stop stretching the composed world into the design's 2000x1400 m; the game is the world's size.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; rid=d89a69a0f3a3
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
pgrep -f "local_gpu.py auto" >/dev/null || { python scripts/local_gpu.py auto --idle-exit 240 > $LAB/gpu_ecs3_change.log 2>&1 & }
cd src
python -m maestro.codegen.run --change $rid "The map is stretched: the composed world is 600 m square but terrain.js scales it by 2000/600 in x and 1400/600 in z, so every tree, rock and slope is squashed and the ground textures smear. Stop scaling the world. The game space IS the world's own size (world.sizeM, square), heights are the world's own heightAt with no multiplier, blocking uses world coordinates directly, and the player, enemies, NPCs, chests, loot and quest markers are placed inside the world's own regions (world.regions / world.regionAt) — map each of the design's six named regions onto one of the world's regions by category (snow → mountain, forest → forest, farmland → grassland, rocky → foothills, swamp → wetland, hills → the remaining one) rather than placing your own region centres. Keep everything else playing as it does." > $LAB/logs/skyrim3d.ecs3.change.log 2>&1
python3 - "$rid" <<'PY'
import json,sys,time
p=f"/home/nick/output/runs/{sys.argv[1]}/build_state.json"; quiet=0; t=0
while quiet<45 and t<7200:
    try: d=json.load(open(p)); done=d.get("phase")=="done"
    except Exception: done=False
    quiet=quiet+1 if done else 0; time.sleep(1); t+=1
PY
echo "CHANGED $(date)"
