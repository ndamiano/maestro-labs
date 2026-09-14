#!/bin/bash
# Six fire points from four prod builds. nudge-floor differs from nudge only where the build had
# not yet written anything, so it is run on the three orientation positions only.
cd "$(dirname "$0")"
export PYTHONPATH=..
C=/home/nick/output/replay-corpus
K=3
T=12

for spec in "$C/345fcb132db8 74a9f0b3c662 108" \
            "$C/345fcb132db8 74a9f0b3c662 145" \
            "$C/345fcb132db8 74a9f0b3c662 166" \
            "$C/e153dddc53b6 d6741e9099d2 69"; do
  python3 run_readstreak.py $spec $T $K control,nudge
done

for spec in "$C/e153dddc53b6 a736b59e5e11 9" \
            "$C/0df4c0941141 dab5b252615c 9"; do
  python3 run_readstreak.py $spec $T $K control,nudge,nudge-floor
done
echo "GRID DONE"
