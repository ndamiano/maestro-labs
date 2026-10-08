#!/bin/bash
# g7e.2xlarge boot measurement: launch -> /health_generate 200, with host RAM sampled
# through the prepacked restore. Writes the timeline and both logs to S3, then terminates.
exec > /var/log/gsboot.log 2>&1
set -x

B="__BUCKET__"
BREGION="__BREGION__"
TAG="__TAG__"
T0=$(date +%s)
mark() { echo "[ec2 +$(( $(date +%s) - T0 ))s] $*"; }

mark "userdata start"
command -v aws >/dev/null || { snap install aws-cli --classic 2>/dev/null || \
  { apt-get update -q && apt-get install -y -q awscli; }; }
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader || mark "NO GPU"
free -m | awk '/Mem:/{print "host mem total MiB:", $2}'

# /workspace must land on the 1.9 TB instance store, never the EBS root. The DLAMI already
# consumes the instance store into an LVM volume group mounted at /opt/dlami/nvme, so mkfs on
# the raw device fails (busy) — use the LVM when it is there, format the raw disk when it is not.
if mountpoint -q /opt/dlami/nvme; then
    mkdir -p /opt/dlami/nvme/workspace /workspace
    mount --bind /opt/dlami/nvme/workspace /workspace
    mark "workspace bind-mounted onto DLAMI ephemeral LVM"
else
    DEV=$(lsblk -dno NAME,MODEL | awk '/Instance Storage/{print "/dev/"$1; exit}')
    mkfs.ext4 -F -E nodiscard,lazy_itable_init=1,lazy_journal_init=1 "$DEV"
    mkdir -p /workspace
    mount -o noatime "$DEV" /workspace
    mark "workspace formatted on $DEV"
fi

# A failed mount silently leaves /workspace on the 96 GB root, where the 145 GB sync dies of
# ENOSPC twelve minutes later on a GPU that is billing. Fail here instead.
AVAIL=$(df -BG --output=avail /workspace | tail -1 | tr -dc 0-9)
if [ "${AVAIL:-0}" -lt 200 ]; then
    mark "FATAL: /workspace has only ${AVAIL}G free — not on the instance store"
    aws s3 cp /var/log/gsboot.log "s3://$B/bootlogs/latest-gsboot.log" --region "$BREGION"
    shutdown -h now
    exit 1
fi
mark "workspace ready (${AVAIL}G free)"

# Docker's data-root moves to the NVMe: the 7 GB image and the ~10 GB env tar both land in the
# container filesystem, and gp3 at 125 MB/s would be the boot bottleneck rather than anything
# we are trying to measure. Merge, never overwrite — daemon.json carries the nvidia runtime.
systemctl stop docker docker.socket containerd 2>/dev/null
mkdir -p /workspace/docker /etc/docker
python3 - <<'PY'
import json, os
p = "/etc/docker/daemon.json"
d = {}
if os.path.exists(p):
    try:
        d = json.load(open(p))
    except Exception:
        d = {}
d["data-root"] = "/workspace/docker"
json.dump(d, open(p, "w"), indent=2)
print("daemon.json:", d)
PY
systemctl start docker
docker info --format 'docker root: {{.DockerRootDir}} | runtimes: {{.Runtimes}}'
mark "docker on nvme"

# Host RAM every 2 s: total, used, free, available. The 47.68 GiB pinned PLE table lands here.
( while true; do
    echo "$(( $(date +%s) - T0 )) $(free -m | awk '/Mem:/{print $2,$3,$4,$7}')"
    sleep 2
  done ) > /var/log/ram.log &
RAM_PID=$!

aws configure set default.s3.max_concurrent_requests 32
aws configure set default.s3.max_queue_size 10000
mark "syncing workspace from s3"
aws s3 sync "s3://$B/workspace/" /workspace/ --region "$BREGION" --only-show-errors
mark "workspace synced ($(du -sh /workspace | cut -f1))"

TOK=$(aws ssm get-parameter --name /gamesummoner/dockerhub/auth --with-decryption \
      --region us-east-1 --query Parameter.Value --output text)
echo "$TOK" | base64 -d | cut -d: -f2- | docker login -u "$(echo "$TOK" | base64 -d | cut -d: -f1)" --password-stdin
mark "docker login ok"

docker pull "ndamiano100/maestro-worker:$TAG"
mark "image pulled"

# Real entrypoint, real serve script. CP_URL is deliberately unroutable: the engine reaches
# healthy and stamps its own [boot +Ns] marks before the agent ever dials out, which is the
# whole measurement. The agent then fails and the container exits.
# The PLE table is a single 47.68 GiB cudaHostAlloc. Pinned memory is LOCKED memory, so the
# container's RLIMIT_MEMLOCK must allow it (Docker's default ceiling refuses it outright), and
# the kernel needs that much reclaimable space in one go — the S3 sync just filled page cache.
sync; echo 3 > /proc/sys/vm/drop_caches
mark "caches dropped: $(free -m | awk '/Mem:/{print "avail " $7 " MiB"}')"
mark "host memlock: $(ulimit -l)"
mark "container memlock default: $(docker run --rm --entrypoint sh "ndamiano100/maestro-worker:$TAG" -c 'ulimit -l' 2>&1 | tail -1)"
mark "container memlock raised:  $(docker run --rm --entrypoint sh --ulimit memlock=-1:-1 "ndamiano100/maestro-worker:$TAG" -c 'ulimit -l' 2>&1 | tail -1)"

docker run --rm --gpus all --network host --ipc=host \
  --ulimit memlock=-1:-1 \
  -v /workspace:/workspace \
  -e CP_URL=http://127.0.0.1:9 \
  -e WORKER_TOKEN=boot-measurement \
  -e LLM_MODEL=pennyroyal \
  -e LLM_N_CTX=131072 \
  -e WORKER_SLOTS=2 \
  "ndamiano100/maestro-worker:$TAG" > /var/log/container.log 2>&1 &
DOCKER_PID=$!
mark "container started"

healthy=""
for _ in $(seq 1 240); do
  if curl -sf -o /dev/null http://127.0.0.1:8001/health_generate; then healthy=1; break; fi
  kill -0 $DOCKER_PID 2>/dev/null || break
  sleep 2
done

if [ -n "$healthy" ]; then
  mark "HEALTHY — launch to health_generate 200"
  curl -s http://127.0.0.1:8001/get_model_info || true
  echo
  mark "peak host RAM used MiB: $(awk '{if($3>m)m=$3}END{print m}' /var/log/ram.log)"
  mark "min available MiB: $(awk 'NR==1{m=$5}{if($5<m)m=$5}END{print m}' /var/log/ram.log)"
else
  mark "NEVER HEALTHY"
  mark "peak host RAM used MiB: $(awk '{if($3>m)m=$3}END{print m}' /var/log/ram.log)"
  dmesg | grep -iE "out of memory|oom-kill|killed process" | tail -20
fi

kill $RAM_PID 2>/dev/null
for f in gsboot ram container; do
  aws s3 cp "/var/log/$f.log" "s3://$B/bootlogs/$(date +%Y%m%dT%H%M%S)-$f.log" --region "$BREGION"
done
aws s3 cp /var/log/gsboot.log "s3://$B/bootlogs/latest-gsboot.log" --region "$BREGION"
shutdown -h now
