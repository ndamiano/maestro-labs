#!/usr/bin/env bash
# queue_designs.sh: wait for the pipes build to leave the GPU, then take every ask in
# asks.more.txt through the design chain only (--new, no build), one at a time. Run id and the
# design's leg sizes land in designs.tsv, chain log in logs/design.N.log, heartbeat in
# logs/queue.log. Control runs for these four asks: 194354ba2b2e, d615927dc0fe, 202198c78de5,
# 112ec65202b2 (design-team harness, pre content leg).
set -u
LAB="$(cd "$(dirname "$0")" && pwd)"; REPO="$(cd "$LAB/../.." && pwd)"
BUILD_ARGV="../venv/bin/python -m maestro.codegen.run --build 9ac84769bb99"
say() { echo "$(date +%FT%T) $*" >> "$LAB/logs/queue.log"; }
waited=0
while pgrep -fx "$BUILD_ARGV" > /dev/null; do
  [ $((waited % 600)) -eq 0 ] && say "waiting for the pipes build to finish (${waited}s)"
  sleep 30; waited=$((waited + 30))
  [ $waited -gt 28800 ] && { say "build still running after 8h — starting designs anyway"; break; }
done
say "build gone after ${waited}s; starting designs"
n=1
while IFS= read -r ask; do
  [ -z "$ask" ] && continue
  log="$LAB/logs/design.$((n + 1)).log"
  say "design $n: $ask"
  (cd "$REPO/src" && PYTHONUNBUFFERED=1 "$REPO/venv/bin/python" -m maestro.codegen.run --new "$ask" > "$log" 2>&1)
  rid=$(grep -oE '^run: [0-9a-f]{12}' "$log" | cut -c6- | head -1)
  sizes=""
  for leg in gameplay content visual engineering spec; do
    f=/home/nick/output/runs/$rid/design/$leg.md
    sizes="$sizes$leg=$( [ -f "$f" ] && wc -c < "$f" || echo MISSING ) "
  done
  printf '%s\t%s\t%s\t%s\n' "$n" "${rid:-?}" "$sizes" "$ask" >> "$LAB/designs.tsv"
  say "design $n done run=${rid:-?} $sizes"
  n=$((n + 1))
done < "$LAB/asks.more.txt"
say "queue down"
