#!/bin/bash
# Wait for the running novisual build to finish, then rerun the same design on the committed code.
LAB=/home/nick/Documents/Labs/ashworth-street
while kill -0 125739 2>/dev/null; do sleep 20; done
cp $LAB/logs/ablation.novisual.log $LAB/logs/ablation.novisual.f7f816519d16.log
kill 125587; for i in $(seq 1 15); do kill -0 125587 2>/dev/null || break; sleep 1; done
kill -9 125587 2>/dev/null
cd /home/nick/Documents/ai-agent-test
LAB_MAX_TURNS=200 NINFER_MODELS=/var/lib/models/ninfer nohup venv/bin/python $LAB/serve_lab.py >> $LAB/logs_server.log 2>&1 &
echo "serve_lab $!"
for i in $(seq 1 30); do [ "$(curl -s -o /dev/null -w '%{http_code}' localhost:8000/)" != 000 ] && break; sleep 2; done
rm -f $LAB/logs/ablation.novisual.log
cd $LAB && VARIANTS=novisual STEPS=200 ./run_ablation.sh
