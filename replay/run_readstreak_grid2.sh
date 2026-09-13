#!/bin/bash
# The half the pause interrupted: the third nudge sample at 69, then the two orientation positions
# where the build had written nothing yet — the only place nudge-floor differs from nudge.
cd ~/Documents/Labs/replay
export PYTHONPATH=/home/nick/Documents/ai-agent-test/src
C=/home/nick/output/replay-corpus

python3 run_readstreak.py $C/e153dddc53b6 d6741e9099d2 69 12 1 nudge
python3 run_readstreak.py $C/e153dddc53b6 a736b59e5e11  9 12 3 control,nudge,nudge-floor
python3 run_readstreak.py $C/0df4c0941141 dab5b252615c  9 12 3 control,nudge,nudge-floor
echo "GRID2 DONE"
