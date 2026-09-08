#!/bin/bash
# TRELLIS server at 1024_cascade with a host-RAM watchdog: below 6 GB available it dies, not the desktop.
O=/home/nick/output/img2threed
/home/nick/cube3d-lab/trellis2-venv/bin/python /home/nick/Documents/ai-agent-test/src/tools/trellis_server.py \
  --repo /home/nick/cube3d-lab/trellis2 --weights /home/nick/cube3d-lab/trellis2-weights --stage-dir "" \
  --port 8189 --ptype 1024_cascade --texture 2048 > $O/trellis_server_styles.log 2>&1 &
SP=$!
while kill -0 $SP 2>/dev/null; do
  a=$(awk '/MemAvailable/{print int($2/1048576)}' /proc/meminfo)
  if [ "$a" -lt 6 ]; then echo "WATCHDOG $(date +%T): MemAvailable ${a}G, killing server" >> $O/trellis_server_styles.log; kill -9 $SP; break; fi
  sleep 1
done
