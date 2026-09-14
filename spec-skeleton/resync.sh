#!/usr/bin/env bash
# Keep the :8765 copies fresh: a run's gate can launch a fix round AFTER build.sh returned, so the
# chain's one-shot rsync may have copied a pre-fix game. Every 5 min, rsync every run this lab
# built whose game dir changed; one last pass after tail.done, then exit.
cd "$(dirname "$0")"; REPO=$(cd ../.. && pwd)
ids() { { awk -F'\t' '{print $3}' builds.tsv; grep -h '^run:' logs/build.*.log | awk '{print $2}'; } 2>/dev/null | grep -E '^[0-9a-f]{12}$' | sort -u; }
pass() { for r in $(ids); do [ -d /home/nick/output/runs/$r/game ] && rsync -a --delete /home/nick/output/runs/$r/game/ $REPO/runtime/games/$r/ 2>/dev/null; done; }
while [ ! -f tail.done ]; do pass; sleep 300; done
sleep 60; pass; echo "$(date +%FT%T) final resync done" >> logs/guard.log
