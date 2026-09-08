#!/usr/bin/env bash
# 3x fresh-pod rent→healthy measure of llm-penny-v7. Real entrypoint, boot log tee'd to the
# network volume (fetched via the volume's S3 API). Pods terminated after each run.
# SE capacity comes and goes: each run retries create every 120 s for up to 40 min.
set -euo pipefail
KEY=$(cat ~/.runpod_key)
S3="aws --profile runpod --region us-nc-2 --endpoint-url https://s3api-us-nc-2.runpod.io s3"
API=https://rest.runpod.io/v1
REQ=$(mktemp)

for run in 1 2 3; do
  echo "=== run $run ==="
  cat > "$REQ" <<EOF
{
  "name": "fastboot-v7-$run",
  "imageName": "ndamiano100/maestro-worker:llm-penny-v7",
  "containerRegistryAuthId": "cmrtn9wl200gcb9svb78kn7e0",
  "gpuTypeIds": ["NVIDIA RTX PRO 6000 Blackwell Server Edition", "NVIDIA RTX PRO 6000 Blackwell Workstation Edition"],
  "gpuCount": 1,
  "networkVolumeId": "szjxc7ha34",
  "volumeMountPath": "/workspace",
  "containerDiskInGb": 200,
  "ports": [],
  "dockerEntrypoint": ["bash","-c","mkdir -p /workspace/boot-logs; /opt/maestro/entrypoint.sh 2>&1 | tee /workspace/boot-logs/v7-\$RUNPOD_POD_ID.log"],
  "env": {"CP_URL":"http://127.0.0.1:9","WORKER_TOKEN":"dummy","LLM_MODEL":"pennyroyal","LLM_N_CTX":"131072"}
}
EOF
  pod=""
  for try in $(seq 1 20); do
    t0=$(date +%s)
    resp=$(curl -s -X POST "$API/pods" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' -d @"$REQ")
    pod=$(echo "$resp" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("id",""))
except Exception: print("")')
    [ -n "$pod" ] && break
    echo "create try $try failed: $(echo "$resp" | head -c 120) — retry in 120s"
    sleep 120
  done
  [ -n "$pod" ] || { echo "RUN $run: gave up on capacity"; continue; }
  echo "pod $pod created t0=$t0"
  log="s3://szjxc7ha34/boot-logs/v7-$pod.log"
  t_first=""; t_healthy=""
  for i in $(seq 1 200); do
    sleep 5
    body=$($S3 cp "$log" - 2>/dev/null || true)
    if [ -n "$body" ] && [ -z "$t_first" ]; then t_first=$(date +%s); echo "log appeared +$((t_first-t0))s"; fi
    if echo "$body" | grep -q "pennyroyal up"; then t_healthy=$(date +%s); break; fi
    if echo "$body" | grep -q "engine never became healthy"; then echo "RUN $run FAILED"; break; fi
  done
  echo "RUN $run: provision+pull=$([ -n "$t_first" ] && echo $((t_first-t0)) || echo "?")s rent->healthy=$([ -n "$t_healthy" ] && echo $((t_healthy-t0)) || echo TIMEOUT)s"
  [ -n "$t_healthy" ] && echo "$body" | grep -E '^\[boot' | tail -3
  curl -s -X DELETE "$API/pods/$pod" -H "Authorization: Bearer $KEY" >/dev/null
  echo "pod $pod terminated"
done
rm -f "$REQ"
