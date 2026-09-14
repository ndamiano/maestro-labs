#!/usr/bin/env bash
# Stop the MTP quasar server and serve the QUASAR v2 artifact (DFlash2 companion packed) with
# the DFlash2 drafter. Same model id, context, KV and sampling flags as scripts/local_gpu.py.
set -euo pipefail
BIN=${NINFER_BIN:-/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve}
ART=${NINFER_ART:-/var/lib/models/ninfer/qwen3_8_27b_quasar_nvfp4.ninfer}
K=${DRAFT_TOKENS:-7}
LOG=/home/nick/output/logs/ninfer-dflash2.log
old=$(pgrep -fx '/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve /var/lib/models/ninfer/qwen3_8_27b_quasar_nvfp4.ninfer --model-id qwen3.8_27b_quasar --host 127.0.0.1 --port 8090 --max-context 131072 --spec mtp --draft-tokens 3 --lm-head-draft --presence-penalty 0 --cors --vision --kv-dtype int8 --preserve-thinking' || true)
if [ -n "$old" ]; then echo "stopping quasar mtp server pid $old"; kill -9 $old; sleep 3; fi
exec "$BIN" "$ART" \
  --model-id qwen3.8_27b_quasar \
  --host 127.0.0.1 --port 8090 \
  --max-context 131072 \
  --spec dflash2 --draft-tokens "$K" --lm-head-draft \
  --presence-penalty 0 --cors --vision \
  --kv-dtype int8 --preserve-thinking \
  >> "$LOG" 2>&1
