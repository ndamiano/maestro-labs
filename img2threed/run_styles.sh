#!/bin/bash
O=/home/nick/output/img2threed
for f in $O/styles/*.png; do b=$(basename ${f%.png}); for t in 512 1024_cascade; do
  d=$([ $t = 512 ] && echo styles_512 || echo styles_1024); tex=$([ $t = 512 ] && echo 1024 || echo 2048)
  [ -s $O/$d/$b.glb ] && continue
  s=$(date +%s); curl -s -o $O/$d/$b.glb -H "Content-Type: image/png" --data-binary @$f "http://127.0.0.1:8189/generate?ptype=$t&texture=$tex"
  echo "$b $t $(( $(date +%s)-s ))s $(stat -c%s $O/$d/$b.glb)"
done; done; echo DONE
