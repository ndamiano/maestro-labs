#!/usr/bin/env bash
# overnight: auto leg (llm/image/mesh swapped by pending work) + transplant builds; exits when all drained.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
python scripts/local_gpu.py auto --idle-exit 900 > $LAB/gpu_transplant.log 2>&1 &
GPU=$!
$LAB/run_transplant.sh transplant27b
echo "builds done $(date)"
wait $GPU
echo "NIGHTDONE $(date)"
