#!/usr/bin/env bash
# Bring the local stack back after a reboot so a stranded build resumes: ninfer (131K, int8 KV),
# control plane, llm worker. The reaper requeues the lapsed turn on its own.
set -u
TOKEN=${1:?usage: resume_stack.sh <workqueue token — nicknotes "Current Token">}
REPO=/home/nick/Documents/ai-agent-test; LOGS=/home/nick/output/logs; mkdir -p $LOGS
cd $REPO; source venv/bin/activate
nohup /home/nick/Documents/ninfer/build/apps/ninfer-serve /var/lib/models/ninfer/qwen3_8_27b.ninfer \
  --model-id qwen3.8_27b --host 127.0.0.1 --port 8090 --max-context 131072 --kv-dtype int8 \
  --spec mtp --draft-tokens 3 --lm-head-draft --presence-penalty 0 --cors --vision > $LOGS/ninfer.log 2>&1 &
nohup python run.py > $LOGS/run.py.log 2>&1 &
until curl -s -m 2 localhost:8090/v1/models >/dev/null; do sleep 5; done; echo ninfer up
until curl -s -m 2 localhost:8000/ >/dev/null; do sleep 2; done; echo control plane up
cd src && nohup python -m worker.agent --server http://localhost:8000 --token "$TOKEN" --queue llm --target http://localhost:8090 > $LOGS/worker-llm.log 2>&1 &
echo worker up; sleep 90; tail -2 $LOGS/run.py.log | cut -c1-200
