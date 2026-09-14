#!/usr/bin/env bash
# Pod entry: run the image's own entrypoint up to "pennyroyal up", then hand the engine to arms.sh
# instead of the worker agent. Everything the engine prints lands in the volume log.
C=/workspace/conc
mkdir -p "$C/log" "$C/results/$RUNPOD_POD_ID"
export CP_URL=http://127.0.0.1:9 WORKER_TOKEN=dummy LLM_MODEL=pennyroyal LLM_N_CTX=131072 \
       WORKER_SLOTS=4 SGLANG_ARGS_EXTRA="--enable-cache-report"
n=$(grep -n "^/opt/venv/bin/python3 -m worker.agent" /opt/maestro/entrypoint.sh | cut -d: -f1)
head -n $((n - 1)) /opt/maestro/entrypoint.sh > /tmp/boot.sh
cat >> /tmp/boot.sh <<'TAIL'
set +e
bash /workspace/conc/arms.sh "$target"
touch "/workspace/conc/results/$RUNPOD_POD_ID/DONE"
sleep infinity
TAIL
bash /tmp/boot.sh 2>&1 | tee -a "$C/log/$RUNPOD_POD_ID.log"
