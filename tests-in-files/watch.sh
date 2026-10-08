#!/usr/bin/env bash
# watch.sh <rid>: heartbeat on one lab build. Every 60 s logs step/phase; flags a STALL when the
# step has not moved for 15 min; relaunches local_gpu auto if it is gone; abandons pending mesh
# jobs (no local mesh venv); syncs the game to :8765 and exits when the cursor says done.
cd "$(dirname "$0")"; REPO=$(cd ../.. && pwd); RID=$1
ST=/home/nick/output/runs/$RID/build_state.json; DB=$REPO/data/platform.db; LOG=logs/watch.$RID.log
say() { echo "$(date +%FT%T) $*" >> $LOG; }
say "watch up $RID"; last=""; same=0
while true; do
  cur=$(python3 -c "import json;d=json.load(open('$ST'));print(d['step'],d['phase'],d.get('compacted',0),d.get('ok'))" 2>/dev/null)
  say "${cur:-designing (no cursor yet)}"
  case "$cur" in *" done "*) break;; esac
  if [ -n "$cur" ] && [ "$cur" = "$last" ]; then same=$((same+1)); else same=0; fi; last=$cur
  [ $same -ge 15 ] && say "STALL: no step change for $same min"
  for j in $(sqlite3 $DB "select id from jobs where queue='mesh' and status='pending'" 2>/dev/null); do
    (cd $REPO/src && $REPO/venv/bin/python -c "from db import jobs; jobs.abandon_job('$j','mesh leg unavailable locally')" >/dev/null 2>&1) && say "abandoned mesh job $j"; done
  if ! pgrep -fx 'venv/bin/python scripts/local_gpu.py auto' >/dev/null; then
    (cd $REPO && setsid nohup env NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve labs/rig-lab/safe -m 45G venv/bin/python scripts/local_gpu.py auto >> /tmp/maestro-local/auto.log 2>&1 < /dev/null &)
    say "local_gpu auto was gone — relaunched"; fi
  sleep 60
done
sleep 30; rsync -a --delete /home/nick/output/runs/$RID/game/ $REPO/runtime/games/$RID/ && say "synced to :8765/$RID"
say "watch down"
