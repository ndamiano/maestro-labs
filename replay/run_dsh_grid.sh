#!/bin/bash
# dsh arm x3 on three heavy-compaction builds, each run to done or the source's step cap.
# Serial: one GPU. Logs in ~/output/dsh-grid/.
cd "$(dirname "$0")"
export PYTHONPATH=~/Documents/ai-agent-test/src:.
PY=~/Documents/ai-agent-test/venv/bin/python
OUT=~/output/dsh-grid; mkdir -p "$OUT"
R=~/output/runs
# src position turns build
CELLS=(
  "67a1f6e389f4 49 151 c61737a30168"
  "151689d5c549 34 966 d5e1f3ac17f2"
  "de0187bf4529 10 190 48f6d1547432"
)
for rep in 1 2 3; do
  for cell in "${CELLS[@]}"; do
    set -- $cell
    log="$OUT/$1-r$rep.log"
    [ -e "$log" ] && grep -q "^dsh" "$log" && continue
    echo "START $1 r$rep $(date)" >> "$OUT/progress"
    $PY run_branch.py "$R/$1" "$2" "$3" "dsh-$1-r$rep" "$4" medium > "$log" 2>&1
    echo "END $1 r$rep rc=$? $(date)" >> "$OUT/progress"
  done
done
echo ALLDONE >> "$OUT/progress"
