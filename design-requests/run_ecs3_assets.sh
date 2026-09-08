#!/usr/bin/env bash
# Top up the 28 art renders the reaper failed (pending >1800s while the card was on llm) for d89a69a0f3a3.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test; rid=d89a69a0f3a3
cd $REPO; source venv/bin/activate; export NINFER_BIN=/home/nick/Documents/ninfer-quasar/build/apps/ninfer-serve
pgrep -f "local_gpu.py auto" >/dev/null || { python scripts/local_gpu.py auto --idle-exit 240 > $LAB/gpu_ecs3_assets.log 2>&1 & }
cd src; python -m maestro.codegen.run --assets $rid > $LAB/logs/skyrim3d.ecs3.assets.log 2>&1; echo "ASSETS-ENQUEUED $(date)"
