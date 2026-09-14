#!/usr/bin/env bash
# Vision-in-loop arm: the platformer and island skeleton designs rebuilt with vision.patch applied
# (control plane restarted on the patched tree first). Writes vision.done at the end.
cd "$(dirname "$0")"; REPO=$(cd ../.. && pwd)
for a in platformer island; do
  STEPS=200 ./build.sh designs/$a.skel.xhigh.md "$a — skel xhigh + vision" > logs/build.$a.vision.log 2>&1
  rid=$(grep -m1 '^run:' logs/build.$a.vision.log | awk '{print $2}')
  [ -n "$rid" ] && rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ 2>/dev/null
  echo -e "$a\tvision\t$rid" >> builds.tsv
done
echo ALLDONE > vision.done
