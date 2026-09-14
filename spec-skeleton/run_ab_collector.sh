#!/usr/bin/env bash
# After the integrators land: collector p2 spec built twice on local 27B, spec as design.md (A)
# then spec inline as the prompt (B, current path). Brings up the control plane and a worker.
cd "$(dirname "$0")"; REPO="$(cd ../.. && pwd)"
while [ ! -f integrate_5.done ]; do sleep 30; done
mkdir -p /tmp/maestro-local
pgrep -fx 'venv/bin/python run.py' >/dev/null || (cd "$REPO" && setsid nohup venv/bin/python run.py >> /tmp/maestro-local/run.log 2>&1 < /dev/null &)
for i in $(seq 1 60); do curl -s -m 2 localhost:8000/ -o /dev/null && break; sleep 2; done
setsid nohup ./worker.sh >> worker.log 2>&1 < /dev/null &
sleep 8
./build_file.sh designs/collector.team_integrate_p2.xhigh.md collector "collector — team p2, design.md" > ab_file.log 2>&1
: inline arm B skipped, Nick: first arm only
echo done > ab_collector.done
