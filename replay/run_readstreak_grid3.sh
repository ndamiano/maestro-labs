#!/bin/bash
# The turn floor: no nudge before turn 25, so a fix's opening read-back is never interrupted.
# Only the two orientation positions can tell it from plain nudge — everywhere else the streak
# hits ten well past turn 25.
cd "$(dirname "$0")"
export PYTHONPATH=..
C=/home/nick/output/replay-corpus

python3 run_readstreak.py $C/e153dddc53b6 a736b59e5e11 9 12 3 nudge-t25
python3 run_readstreak.py $C/0df4c0941141 dab5b252615c 9 12 3 nudge-t25
echo "GRID3 DONE"
