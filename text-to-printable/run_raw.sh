#!/bin/bash
# gen under a host-RAM watchdog, then fix in its own process
O=/home/nick/output/img2threed/fun
/home/nick/cube3d-lab/trellis2-venv/bin/python /home/nick/Documents/Labs/text-to-printable/raw_trellis.py gen "${1:-1024_cascade}" > $O/raw1024.log 2>&1 &
P=$!
while kill -0 $P 2>/dev/null; do a=$(awk '/MemAvailable/{print int($2/1048576)}' /proc/meminfo); [ "$a" -lt 6 ] && { echo "WATCHDOG ${a}G" >> $O/raw1024.log; kill -9 $P; }; sleep 1; done
/home/nick/cube3d-lab/trellis2-venv/bin/python /home/nick/Documents/Labs/text-to-printable/raw_trellis.py fix >> $O/raw1024.log 2>&1
echo DONE >> $O/raw1024.log
