#!/usr/bin/env bash
# Session-independent guard for the overnight chain: abandons mesh jobs (no local kimodo venv, a
# pending one crashes local_gpu auto), relaunches auto and the control plane if they die, logs
# every action. Exits when tail.done exists.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd); DB=$REPO/data/platform.db; LOG=$LAB/logs/guard.log
say() { echo "$(date +%FT%T) $*" >> $LOG; }
say "guard up"
cpgone=0
while [ ! -f tail.done ]; do
  m=$(sqlite3 $DB "select id from jobs where queue='mesh' and status='pending'" 2>/dev/null)
  for j in $m; do (cd $REPO/src && $REPO/venv/bin/python -c "from db import jobs; jobs.abandon_job('$j','mesh leg unavailable locally: SPRITE_PYTHON venv missing')" >/dev/null 2>&1) && say "abandoned mesh job $j"; done
  if ! pgrep -fx 'venv/bin/python scripts/local_gpu.py auto' >/dev/null; then
    (cd $REPO && setsid nohup env NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve labs/rig-lab/safe -m 45G venv/bin/python scripts/local_gpu.py auto >> /tmp/maestro-local/auto.log 2>&1 < /dev/null &)
    say "local_gpu auto was gone — relaunched"; sleep 20
  fi
  if pgrep -fx 'venv/bin/python run.py' >/dev/null; then cpgone=0; else
    cpgone=$((cpgone+1))
    if [ $cpgone -ge 3 ]; then (cd $REPO && setsid nohup venv/bin/python run.py >> /tmp/maestro-local/run.log 2>&1 < /dev/null &); say "control plane was gone 90 s — relaunched"; cpgone=0; sleep 15; fi
  fi
  sleep 30
done
say "guard down: tail.done"
