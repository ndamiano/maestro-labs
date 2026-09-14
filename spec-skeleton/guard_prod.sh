#!/usr/bin/env bash
# Guard for the prod leg: relaunch the control plane if it dies (it hosts the autoscaler), log
# queue depth and live pods every 5 min. Exits on prod.done.
cd "$(dirname "$0")"; LAB=$(pwd); REPO=$(cd ../.. && pwd); DB=$REPO/data/platform.db; LOG=$LAB/logs/guard_prod.log; DONE=${1:-prod.done}
say() { echo "$(date +%FT%T) $*" >> $LOG; }
say "guard_prod up"; gone=0; n=0
while [ ! -f $DONE ]; do
  if pgrep -fx 'venv/bin/python run.py' >/dev/null; then gone=0; else gone=$((gone+1)); if [ $gone -ge 3 ]; then (cd $REPO && setsid nohup venv/bin/python run.py >> /tmp/maestro-local/run.log 2>&1 < /dev/null &); say "control plane gone 90 s — relaunched"; gone=0; sleep 20; fi; fi
  n=$((n+1)); if [ $((n % 10)) -eq 0 ]; then say "jobs: $(sqlite3 $DB "select queue||':'||status||':'||count(*) from jobs where status in ('pending','claimed') group by 1,2" | tr '\n' ' ') | workers live: $(sqlite3 $DB "select count(*) from workers where terminated_at is null and pod_id is not null")"; fi
  sleep 30
done
say "guard_prod down: $DONE"
