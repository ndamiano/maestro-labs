#!/usr/bin/env bash
# Rent one Pro 6000 on whichever llm volume has stock, watch the volume log until the arms finish,
# pull the results, terminate the pod. Detached; everything it says goes to results/rent.log.
set -uo pipefail
cd "$(dirname "$0")"
KEY=$(cat ~/.runpod_key)
API=https://rest.runpod.io/v1
VOLS=("juqk1aq0ew eu-ro-1" "szjxc7ha34 us-nc-2")
GPUS=("NVIDIA RTX PRO 6000 Blackwell Workstation Edition" "NVIDIA RTX PRO 6000 Blackwell Server Edition")
NAME=conc-lab-$(date +%H%M)
CAP_MIN=60
s3() { local dc=$1; shift; aws --profile runpod --region "$dc" --endpoint-url "https://s3api-$dc.runpod.io" s3 "$@"; }
log() { echo "$(date +%H:%M:%S) $*"; }
pod_id() { python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("id",""))
except Exception: print("")'; }
pod_status() { curl -s "$API/pods/$1" -H "Authorization: Bearer $KEY" | python3 -c 'import sys,json
try: print(json.load(sys.stdin).get("desiredStatus","?"))
except Exception: print("?")'; }

pod=""
for try in $(seq 1 20); do
  for v in "${VOLS[@]}"; do
    set -- $v; vol=$1; dc=$2
    for gpu in "${GPUS[@]}"; do
      body=$(python3 - "$NAME" "$vol" "$gpu" <<'PY'
import json, sys
name, vol, gpu = sys.argv[1:]
print(json.dumps({
    "name": name, "imageName": "ndamiano100/maestro-worker:llm-v20",
    "containerRegistryAuthId": "cmrtn9wl200gcb9svb78kn7e0",
    "gpuTypeIds": [gpu], "gpuCount": 1, "allowedCudaVersions": ["13.0"],
    "networkVolumeId": vol, "volumeMountPath": "/workspace", "containerDiskInGb": 200, "ports": [],
    "dockerEntrypoint": ["bash", "-c", "bash /workspace/conc/pod_main.sh"],
    "env": {"CP_URL": "http://127.0.0.1:9", "WORKER_TOKEN": "dummy",
            "LLM_MODEL": "pennyroyal", "LLM_N_CTX": "131072"}}))
PY
)
      resp=$(curl -s -X POST "$API/pods" -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' -d "$body")
      pod=$(echo "$resp" | pod_id)
      if [ -n "$pod" ]; then log "try $try: pod $pod on $vol ($dc), ${gpu##*Blackwell }"; break 3; fi
      log "try $try: refused ($dc, ${gpu##*Blackwell }): $(echo "$resp" | head -c 140)"
    done
  done
  sleep 120
done
[ -n "$pod" ] || { log "gave up on capacity after 20 tries"; exit 1; }
echo "$pod $vol $dc" > results/pod.txt
T0=$(date +%s)
terminate() {
  curl -s -o /dev/null -X DELETE "$API/pods/$pod" -H "Authorization: Bearer $KEY"
  log "pod $pod terminated after $(( ($(date +%s) - T0) / 60 )) min"
}
trap terminate EXIT
mkdir -p "results/$pod"
last=""
while :; do
  sleep 30
  el=$(( ($(date +%s) - T0) / 60 ))
  s3 "$dc" cp "s3://$vol/conc/log/$pod.log" "results/$pod/boot.log" >/dev/null 2>&1
  tail=$(grep -E "^\[(boot|arms)" "results/$pod/boot.log" 2>/dev/null | tail -1 | cut -c1-160)
  [ "$tail" != "$last" ] && { log "+${el}m | $tail"; last=$tail; }
  s3 "$dc" sync "s3://$vol/conc/results/$pod/" "results/$pod/" >/dev/null 2>&1
  [ -f "results/$pod/DONE" ] && { log "DONE"; break; }
  grep -q "engine never became healthy" "results/$pod/boot.log" 2>/dev/null && { log "engine failed"; break; }
  [ "$el" -ge "$CAP_MIN" ] && { log "hard cap $CAP_MIN min"; break; }
  st=$(pod_status "$pod")
  case "$st" in RUNNING|"?") ;; *) log "pod status '$st'"; break ;; esac
done
sleep 5
s3 "$dc" sync "s3://$vol/conc/results/$pod/" "results/$pod/" >/dev/null 2>&1
s3 "$dc" cp "s3://$vol/conc/log/$pod.log" "results/$pod/boot.log" >/dev/null 2>&1
log "results in results/$pod: $(ls results/$pod | tr '\n' ' ')"
