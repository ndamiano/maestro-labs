#!/bin/bash
# Same stills and prompts as run_all.sh on the fused turbo checkpoint at 4 steps.
cd "$(dirname "$0")"
export UNET=minimax_h3_fused_refdelta_r1024_turbo8_mystic07_int8_convrot.safetensors STEPS=${STEPS:-4}
PY=/home/nick/Documents/ai-agent-test/venv/bin/python
K=knight_src.png
$PY run_arm.py t_walk22_pin knight_right.png 22 "The character walks in place, legs alternating, arms swinging, seen from the side, facing right, and ends exactly as it started." --pin
$PY run_arm.py t_attack22_pin $K 22 "The character performs one quick melee attack with its weapon — a big wind-up and a fast swing — seen from the front, facing the camera, and ends exactly as it started." --pin
$PY run_arm.py t_cut39_mirror $K 39 "The character walks in place, legs alternating, arms swinging, seen from the side, facing left. Halfway through the video a hard cut: the same character walks in place seen from the side, facing right. No turning between the two shots."
$PY run_arm.py t_cut39_frontback $K 39 "The character walks in place, legs alternating, arms swinging, facing the camera. Halfway through the video a hard cut: the same character walks in place seen from behind, facing away from the camera. No turning between the two shots."
$PY run_arm.py t_turn22 $K 22 "The character stands still and turns once in place like a turntable: it turns to face the right side of the screen, then turns to face away from the camera, then turns to face the left side of the screen, then turns back to face the camera exactly as it started. No walking." --pin
$PY run_arm.py t_walk73_pin knight_right.png 73 "The character walks in place, legs alternating, arms swinging, seen from the side, facing right, and ends exactly as it started." --pin
