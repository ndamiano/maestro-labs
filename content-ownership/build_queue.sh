#!/usr/bin/env bash
# build_queue.sh: build each design in designs.tsv, one at a time, at the branch's 400 step cap.
# Per build: result appended to builds.tsv, log in logs/build.N.log, heartbeat in logs/bqueue.log,
# game rsynced to runtime/games/<run> so it is playable at :8765/<run>/index.html.
set -u
LAB="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$LAB/../.." && pwd)"
say() { echo "$(date +%FT%T) $*" >> "$LAB/logs/bqueue.log"; }
n=1
while IFS=$'\t' read -r idx rid sizes ask; do
  [ -z "${rid:-}" ] && continue
  log="$LAB/logs/build.$((n + 1)).log"
  say "build $n: $rid — $ask"
  (cd "$REPO/src" && PYTHONUNBUFFERED=1 "$REPO/venv/bin/python" -m maestro.codegen.run --build "$rid" > "$log" 2>&1)
  res=$(grep -oE 'ok=(True|False)  steps=[0-9]+  elapsed=[0-9hm]+[0-9s]*' "$log" | tail -1)
  printf '%s\t%s\t%s\t%s\n' "$n" "$rid" "${res:-no result line}" "$ask" >> "$LAB/builds.tsv"
  say "build $n done $rid ${res:-?}"
  rsync -a --delete /home/nick/output/runs/$rid/game/ "$REPO/runtime/games/$rid/" && say "staged :8765/$rid/index.html"
  n=$((n + 1))
done < "$LAB/designs.tsv"
say "build queue down"
