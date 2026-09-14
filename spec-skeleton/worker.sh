#!/usr/bin/env bash
# An llm worker against ninfer :8090, registered the way scripts/local_gpu.py registers one (rate 0).
# Needed because local_gpu.py llm drains an empty queue and stops its worker. Foreground; Ctrl-C to stop.
set -u
cd "$(dirname "$0")/../.."; source venv/bin/activate; cd src
ID=$(hostname)-$(python3 -c "import uuid;print(uuid.uuid4().hex[:6])")
python3 -c "from db import workers; workers.worker_created('$ID', None, 'llm', None, 0.0)"
TOKEN=$(python3 -c "import json;print(json.load(open('config/settings.json'))['workqueue']['token'])")
exec python -m worker.agent --server http://localhost:8000 --token "$TOKEN" --queue llm --worker-id "$ID" --target http://localhost:8090
