#!/usr/bin/env bash
# The station design chain against whatever serves :8090, then the four design-call lines from
# the server log. Control: run 17c92bff6bda in labs/ninfer-dflash2/README.md.
set -uo pipefail
OUT=/home/nick/output/dflash2-lab
LOG=${SERVER_LOG:-/home/nick/output/logs/ninfer-dflash2.log}
ts=$(date +%Y%m%d-%H%M%S)
until curl -sf -m 2 http://127.0.0.1:8090/v1/models >/dev/null; do sleep 5; done
start=$(wc -l < "$LOG")
cd /home/nick/Documents/ai-agent-test && source venv/bin/activate && cd src
python -m maestro.codegen.run --new "Survive on a derelict space station." 2>&1 \
  | grep -v 'Event bus not started' | tee "$OUT/design-$ts.log"
tail -n +"$start" "$LOG" | grep -E 'req [0-9]+\] (done|openai)' | sed 's/sampler=.*→/→/' \
  | tee "$OUT/server-$ts.log"
echo "BENCH DONE $ts"
