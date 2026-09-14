#!/usr/bin/env bash
# Decode arms: each stream ramps to ~100K (cache-warm, as measured on pod 3hlhgezwnhtv6k), then
# generates 2048 tokens with EOS ignored; 1, 2 and 4 streams. Tokens/s per stream is the number.
set -uo pipefail
target=$1
C=/workspace/conc
R=$C/results/$RUNPOD_POD_ID
LOG=$C/log/$RUNPOD_POD_ID.log
PY=/opt/venv/bin/python3
mkdir -p "$R"

pool() { grep -o "max_mamba_cache_size: [0-9]*\|max_total_num_tokens=[0-9]*\|max_running_requests=[0-9]*" "$LOG" | tail -3 | tr "\n" " "; }
flush() { curl -s -X POST "$target/flush_cache" >/dev/null; sleep 2; }
stamp() { echo "[arms +$(( $(date +%s) - T0 ))s] $*"; }
arm() { flush; stamp "$1 streams=$2"; $PY "$C/synth.py" --target "$target" --arm "$1" --streams "$2" --turns 80 --decode-tokens 2048 --out "$R/$1.jsonl"; }
T0=$(date +%s)

echo "boot: $(pool)" | tee -a "$R/pools.txt"
arm decode1 1
arm decode2 2
arm decode4 4
stamp "all arms done"
