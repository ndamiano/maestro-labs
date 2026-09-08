#!/bin/bash
# Arms on the knight still. Run after the video leg frees the card.
cd "$(dirname "$0")"
PY=/home/nick/Documents/ai-agent-test/venv/bin/python
K=knight_src.png
$PY run_arm.py walk22_pin knight_right.png 22 "The character walks in place, legs alternating, arms swinging, seen from the side, facing right, and ends exactly as it started." --pin
$PY run_arm.py attack22_pin $K 22 "The character performs one quick melee attack with its weapon — a big wind-up and a fast swing — seen from the front, facing the camera, and ends exactly as it started." --pin
$PY run_arm.py cut39 $K 39 "The character walks in place, legs alternating, arms swinging, seen from the side, facing left. Halfway through the video a hard cut: the same character walks in place seen from the side, facing right. No turning between the two shots."
$PY run_arm.py cut73_4dirs $K 73 "Four shots of the character walking in place, legs alternating, each shot a hard cut to the next with no turning: first facing the camera, then facing the right side of the screen, then facing away from the camera, then facing the left side of the screen."
