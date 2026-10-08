#!/usr/bin/env bash
# overnight.sh: every ask in asks.txt through the whole production path, one after another, on this
# box. Per build: run id and result in builds.tsv, chain log in logs/, a 60 s heartbeat in
# logs/watch.log with a STALL line when the step has not moved for 15 min, local_gpu auto relaunched
# if it dies, pending mesh jobs abandoned (no local mesh venv). Needs the control plane up and
# ninfer answering on :8090 before it starts.
set -u
LAB="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$LAB/../.." && pwd)"; DB=$REPO/data/platform.db
say() { echo "$(date +%FT%T) $*" >> "$LAB/logs/watch.log"; }
heartbeat() {   # $1 = chain log; polls the newest run dir once the chain names it
  local rid="" last="" same=0 st cur
  while kill -0 "$2" 2>/dev/null; do
    [ -z "$rid" ] && rid=$(grep -oE '^run: [0-9a-f]{12}' "$1" | cut -c6- | head -1)
    if [ -n "$rid" ]; then
      st=/home/nick/output/runs/$rid/build_state.json
      cur=$(python3 -c "import json;d=json.load(open('$st'));print(d['kind'],d['step'],d['phase'],'compact',d.get('compacted',0),'ok',d.get('ok'))" 2>/dev/null)
      say "$rid ${cur:-designing (no cursor yet)}"
      if [ -n "$cur" ] && [ "$cur" = "$last" ]; then same=$((same+1)); else same=0; fi; last=$cur
      [ $same -ge 15 ] && say "STALL: $rid no step change for $same min"
    else say "waiting for a run id in $1"; fi
    for j in $(sqlite3 $DB "select id from jobs where queue='mesh' and status='pending'" 2>/dev/null); do
      (cd $REPO/src && $REPO/venv/bin/python -c "from db import jobs; jobs.abandon_job('$j','mesh leg unavailable locally')" >/dev/null 2>&1) && say "abandoned mesh job $j"; done
    if ! pgrep -fx 'venv/bin/python scripts/local_gpu.py auto' >/dev/null; then
      (cd $REPO && setsid nohup env NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve labs/rig-lab/safe -m 45G venv/bin/python scripts/local_gpu.py auto >> /tmp/maestro-local/auto.log 2>&1 < /dev/null &)
      say "local_gpu auto was gone — relaunched"; fi
    sleep 60
  done
}
say "overnight up"
n=0
while IFS= read -r ask; do
  [ -z "$ask" ] && continue; n=$((n+1)); log="$LAB/logs/full.$n.log"
  say "ask $n: $ask"
  (cd $REPO/src && PYTHONUNBUFFERED=1 $REPO/venv/bin/python -m maestro.codegen.run "$ask" > "$log" 2>&1) &
  chain=$!
  heartbeat "$log" $chain
  wait $chain; rc=$?
  rid=$(grep -oE '^run: [0-9a-f]{12}' "$log" | cut -c6- | head -1)
  printf '%s\t%s\t%s\t%s\n' "$n" "${rid:-?}" "rc=$rc" "$ask" >> "$LAB/builds.tsv"
  say "ask $n finished rc=$rc run=${rid:-?}"
  [ -n "$rid" ] && rsync -a --delete /home/nick/output/runs/$rid/game/ $REPO/runtime/games/$rid/ && say "synced to :8765/$rid"
done < "$LAB/asks.txt"
say "overnight down"
