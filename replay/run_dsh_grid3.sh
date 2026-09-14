#!/bin/bash
# dsh arm x3 on 67a1 and 6843 (program-era, quasar), each to done or the step cap; then one short
# 151689 run only to show it no longer compacts every turn (not maestro's paradigm).
cd "$(dirname "$0")"
export PYTHONPATH=..
PY=~/Documents/ai-agent-test/venv/bin/python
OUT=~/output/dsh-grid; R=~/output/runs
while pgrep -f "run_branch.py" >/dev/null; do sleep 20; done
one() {  # src position turns build label
  log="$OUT/$1-$5.log"
  [ -e "$log" ] && grep -q "^dsh" "$log" && return
  echo "START $1 $5 $(date)" >> "$OUT/progress"
  $PY run_branch.py "$R/$1" "$2" "$3" "dsh-$1-$5" "$4" medium > "$log" 2>&1
  echo "END $1 $5 rc=$? $(date)" >> "$OUT/progress"
}
for rep in 1 2 3; do
  one 67a1f6e389f4 49 151 c61737a30168 r$rep
  one 68430462413d 31 169 ec128eef7cbc r$rep
done
one 151689d5c549 34 20 d5e1f3ac17f2 short
echo ALLDONE >> "$OUT/progress"
