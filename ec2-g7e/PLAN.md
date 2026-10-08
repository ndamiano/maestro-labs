# EC2 g7e: the llm queue on AWS instead of RunPod

## Goal
Serve Flash-Next on `g7e.2xlarge` (RTX PRO Server 6000, the same SM120 card Pennyroyal was forked
for) at spot prices under RunPod's $2.19/hr, driven by the RunPod 6000 stock-out. Success = a
prepacked engine reaching `/health_generate` 200 on EC2, with a boot time and a $/game that beat
RunPod.

## Quota, and what the numbers actually mean
Both G/VT quotas are **measured in vCPUs, per account AND per region** — an 8 vCPU grant is
**one g7e.2xlarge**, not eight boxes.

| Quota | us-east-1 | elsewhere |
|---|---|---|
| `L-DB2E81BA` on-demand G/VT | 8 | 0 |
| `L-3819A6DF` spot G/VT | 8 | 0 |

Cases still `CASE_OPENED` for the desired 32 / 256 (= 4 / 32 cards at 2xlarge). Standard vCPU
quota `L-1216C47A` is 64, so CPU helper instances are free of this constraint.

Spot 2026-09-16: $1.71 us-east-1d, $1.84 us-east-1b — only those two AZs offer g7e.
On-demand $3.36. RunPod $2.19.

## The 64 GiB question, answered without renting anything
`g7e.2xlarge` = 8 vCPU / 65536 MiB / 98304 MiB GPU / 1900 GB instance-store NVMe / 50 Gbit.
The worry was that `--ple-offload-embedding` is load-bearing and lives in host RAM, against
RunPod's 188 GB cgroup.

The pack manifest answers it for free —
`prepacked/Qwen4ExpForConditionalGeneration_de07d8c98cc8bd54.json`, 987 KB, on volume szjxc7ha34:

```
device=cpu    pinned=True :    1 storage,  47.68 GiB   <- the PLE table
device=cuda:0 pinned=False: 1922 storages, 73.46 GiB
```

`prepacked_loader.py` `preadv`s **straight into the pinned destination**, so there is no
pageable→pinned double; staging is `SGLANG_PREPACKED_THREADS`(8) × `_CHUNK`(256 MiB) = 2 GiB, and
`posix_fadvise(DONTNEED)` holds page cache flat. Peak ≈ 47.68 + 2 + ~5 runtime ≈ **56 of 64 GiB**.
2xlarge fits; the 8 vCPU grant is enough; no 4xlarge, no waiting on the quota cases.

**Corollary: never DUMP a pack on a 64 GiB box.** A dump is a normal safetensors load + repack —
the thing that ate RunPod's 188 GB cgroup. EC2 must COPY the pack. This also retires
`runai_streamer` as a primary path: it streams safetensors, i.e. the 102–123 s CPU repack the
prepacked loader exists to remove.

`--ple-offload-embedding` has no alternative. `Qwen4ExpPinnedHostEmbedding` gathers from pinned
host memory per token via a Triton kernel — unswappable, not mmap-able off NVMe.
`--no-ple-offload-embedding` puts the table back over 96 GB; `--cpu-offload-gb` and
`--offload-group-size` raise a ValueError against it by design.

## Standing infrastructure (account <account>, us-east-1)
| Thing | Id |
|---|---|
| bucket | `gamesummoner-models-<account>`, public access blocked |
| S3 gateway endpoint | `vpce-09883550ad82c6d4f` on `rtb-d4ccc2aa` (mandatory — NAT would bill $5.67/boot) |
| security group | `sg-016db859b2be7f1d1`, inbound `[]`, egress all |
| role / instance profile | `gs-gpu-worker` — S3 on the bucket, `AmazonSSMManagedInstanceCore`, `ssm:GetParameter` on exactly two parameters |
| AL2023 AMI | `ami-0e34b50e714a297f1` |
| DLAMI base (driver+docker+nvidia-container-toolkit) | `ami-0a021d98c6c76a762` (Ubuntu 24.04, 20260915) |

Credentials live in SSM as SecureStrings, never in user-data or on disk:
`/gamesummoner/runpod/s3` (volume gateway key) and `/gamesummoner/dockerhub/auth`. Delete both
when the evaluation closes.

## Gotchas burned
- The RunPod S3 gateway **rejects presigned URLs** — `missing Authorization`, header auth only.
  So the key cannot stay on the dev box; it has to reach the copying instance somehow.
- `aws` against the gateway needs `--region us-nc-2` explicitly or it signs for us-east-1 and
  gets "the region 'us-east-1' is wrong".
- The entrypoint refuses to boot if the image's `/opt/maestro/env.id` ≠ the env tar on the
  volume. `llm-v19` and `llm-v20` both carry `c0ca5f12c86f`, which is what is on szjxc7ha34.
- `WORKER_SLOTS` sets `--cuda-graph-bs 1..N`; changing it re-keys the FlashInfer autotune cache
  and costs one ~300 s re-tune. The baked cache was keyed at 2 slots.

## Order of work
1. ~~Quota, scaffolding, the 64 GiB question.~~ Done 2026-09-16.
2. Copy `/workspace` (424 objects + the 10 GB env tar, 144.82 GB) from szjxc7ha34 to
   `s3://<bucket>/workspace/`, ranged GET → multipart PUT from a c7i.4xlarge.
3. One g7e.2xlarge boot: NVMe → `/workspace`, S3 sync, real entrypoint and real serve script,
   `free -m` every 2 s. Measure launch → `/health_generate` 200 and peak host RAM.
4. If green: a full build through an EC2 pod for adoption evidence, then `Ec2Client` beside
   `runpod_client.py` (69 lines, 4 methods; `policy.py` is untouched).

## Code gaps for adoption (not blockers for the measurement)
- `scripts/worker-llm-entrypoint.sh` hardcodes `--source runpod` and self-terminates via the
  RunPod API. EC2 needs its own branch, or `InstanceInitiatedShutdownBehavior=terminate` plus a
  shutdown on clean agent exit.
- Art queues stay on RunPod — no 5090 on EC2. Scaler config is already per-queue.

## Append-only results

### 2026-09-16 session 1: scaffolding + the pack copy, and a capacity wall
- The 64 GiB question answered from the manifest, no GPU rented (see above). 2xlarge fits.
- **Pack copy DONE.** c7i.4xlarge, ranged GET from the szjxc7ha34 gateway -> multipart PUT:
  `VERIFIED 425 objects, 144.82 GB` in 13 min wall, ~$0.16 of instance time. Throughput
  **191 MB/s** on the 130 GB target pack, 168 MB/s on the env tar, 144 MB/s on the 4.3 GB draft.
  The gateway is the limit, not EC2. Script at `bootstrap/copy_pack.py` in the bucket; it is
  idempotent (skips by key+size) so a rerun resumes.
- **g7e.2xlarge is STOCKED OUT in us-east-1.** Both AZs that offer it (1d, 1b), both on-demand
  and spot, all refuse `InsufficientInstanceCapacity` — each AZ's error helpfully recommends the
  other. Omitting the AZ does not help. This is the same failure that drove us off RunPod
  ([[project_runpod_6000_stockout]]), which is a real mark against the EC2 thesis: the quota
  cases being granted would not have helped, because capacity, not quota, is the binding
  constraint right now. 4xlarge would dodge the pool but needs 16 vCPU against an 8 vCPU grant.
- Retry loop armed across all four pools; first one to open wins.
- **Open question this raises:** if g7e supply in us-east-1 is this thin, the eval needs a
  capacity story before a cost story. Worth pricing an On-Demand Capacity Reservation or a
  Capacity Block, and worth filing quota in us-east-2/us-west-2 so there are more pools to fish
  in — quota is per-region and takes days, so filing early costs nothing.

### 2026-09-16 session 1b: region survey — g7e is scarce everywhere, not just Virginia
Nick's ruling: latency is irrelevant (a build runs minutes; 200 ms RTT is noise), so region is
free to choose. The one real regional constraint is **S3 locality** — the bucket is us-east-1, and
a cross-region boot pulls 145 GB at $0.02/GB = **$2.90/boot** in egress, which eats the whole spot
saving. Fix is a bucket replica per region used (~$3.30/mo per copy, one-time ~$2.90 to seed).

Only 9 of 17 regions offer g7e.2xlarge at all:

| region | AZs | spot min | placement score |
|---|---|---|---|
| eu-north-1 | 2 | **$1.1909** | **3** |
| us-west-2 | **4** | $1.2558 | 1 |
| us-east-1 | 2 | $1.7104 | **absent** |
| ap-south-1 | 2 | $1.7936 | **3** |
| us-east-2 | 2 | $1.9092 | 1 |
| eu-west-2 | 2 | $2.1862 | 1 |
| eu-central-1 | 2 | $2.2195 | — |
| ap-northeast-2 | 2 | $2.2607 | **3** |
| ap-northeast-1 | 2 | $2.5559 | 1 |

**`get-spot-placement-scores` tops out at 3/10 anywhere on earth for this family.** us-east-1 —
the only region where we hold quota — does not appear in the scored set at all. So the stock-out
is not a bad region choice, it is a scarce instance family. Any capacity plan for g7e has to
assume thin supply everywhere, which materially weakens the "spot is 45% under RunPod" thesis:
an arm you cannot rent has no $/game.

Quota filed 2026-09-16, all PENDING, 128 spot vCPU (16 cards) + 16 on-demand vCPU (2 cards) in
**eu-north-1** (best score AND cheapest), **ap-south-1** (score 3), **us-west-2** (score 1 but
four AZs = most pools, and $1.26). eu-north-1 is the one to build against if granted.

Next when a region lands: create a bucket there, one-time `aws s3 sync` from the us-east-1
bucket (~$2.90 egress), then the same boot script with `__BUCKET__` repointed.

### 2026-09-16 session 1c: on-demand is a real tier, not a rejected one
Nick's correction, and it is the standing rule ([[feedback_quality_over_compute]]): cost is a fact
about an arm, never an argument against it. "We get a GPU at $3.36" beats "we get no GPU at
$2.19" — the customer's credits drain faster and they still get a game. Do not disqualify a tier
on price when the alternative is no capacity.

On-demand confirmed via the pricing API, per-second billed with a 60 s minimum (a 20 min build
bills 20 min): **us-east-1 $3.3631, us-west-2 $3.3631, eu-north-1 $4.8516**. At RunPod's $2.19
a game runs $1.81, so on-demand EC2 lands near **$2.78/game**.

**THE LADDER (Nick's ruling 2026-09-16): all AWS spot → RunPod → all AWS on-demand.**
First pool that answers wins; within a tier, cheapest first. RunPod sits in the middle as the
known-good incumbent — it already has the volumes, the images and a measured boot.

| tier | range | notes |
|---|---|---|
| 1. AWS spot, all 9 regions | $1.19 – $2.56 | eu-north-1 cheapest and best-scoring |
| 2. RunPod | $2.19 | incumbent; volumes szjxc7ha34 + juqk1aq0ew |
| 3. AWS on-demand, all regions | $3.36 – $4.85 | us-east-1/us-west-2 $3.36, eu-north-1 $4.85 |

Known wrinkle Nick accepted: 4 of the 9 spot pools price at or above RunPod (eu-west-2 $2.19,
eu-central-1 $2.22, ap-northeast-2 $2.26, ap-northeast-1 $2.56), so tier 1 can cost up to $0.37/hr
(~17%) more than tier 2 in those pools. Trying them first still wins because it exhausts scarce
spot capacity before falling back, and the spread is small against the availability gain.

The ordering is NOT the same per tier — eu-north-1 is the cheapest spot ($1.19) and the most
expensive on-demand ($4.85) — so a fallback cannot walk a single price-sorted region list.
`Ec2Client` should take a list of (region, az, market) pools and try them in per-tier price order,
treating `InsufficientInstanceCapacity` as "next pool" rather than an error.

Caveat that survives the correction: us-east-1 refused **on-demand as well as spot**, in both AZs,
for 50+ min. The retry loop tries on-demand first. So today's block is not "spot is too scarce and
on-demand too dear" — it is no g7e capacity at any price in this region.

### 2026-09-16 session 1d: price-sorted pool walk replaces the fixed ladder
Nick: query price everywhere and try cheapest → most expensive, RunPod included. This subsumes
the three-tier ladder and auto-resolves the "4 spot pools cost more than RunPod" wrinkle — the
sort handles it instead of a rule.

**Price is queryable on every provider:**
- AWS spot: `describe-spot-price-history`, live, per region+AZ, ~9 calls, parallelizable.
- AWS on-demand: `aws pricing get-products`, effectively static — cache it.
- RunPod: `gpuTypes(input:{id}){lowestPrice(input:{gpuCount,secureCloud}){minimumBidPrice
  uninterruptablePrice stockStatus}}`.

**Availability is NOT, and the asymmetry is the whole design constraint:**
- RunPod exposes `stockStatus` (Low/…); a null price means no capacity in that cloud. Measured
  2026-09-16: PRO 6000 SE secure = **$2.09, stock Low**; community = null/null (no stock).
  The unfiltered `gpuTypes` aggregate reports $1.69 — do NOT use it, it is not the secure price
  prod rents at. $2.09 is the number; eu-north-1 spot $1.19 is 43% under it.
- AWS has no capacity API. `get-spot-placement-scores` is 1–10, advisory and rate-limited, and
  **read 3/10 across every region while every pool actually returned zero** (measured today).
  Treat it as a hint for ordering ties at best, never as a gate.
- **Therefore the launch attempt is the only truthful probe.** The price-sorted walk IS the
  availability check.

**Consequence to build: a refusal cache.** ~20 AWS spot pools × 1–3 s per refused RunInstances
≈ 20–60 s of walking before reaching RunPod, on every job, whenever spot is scarce. Record
"pool X refused at T", skip it for a cooldown, let it age back in. Without it, scarcity taxes
every build's boot latency.

`src/scaler/policy.py` carries flat cost constants today and the repo queries no provider prices
anywhere — so the price table is new capability, and per doctrine it merges only bundled with the
consumer that uses it.

### 2026-09-16 20:0x UTC: the error type names which wall you hit
Service Quotas metadata is not the authority on whether a quota is live — RunInstances is — but
checked head to head they agreed, so there is no CLI cache or propagation lag to route around
(the AWS CLI caches credentials only, never API responses).

| probe | response | means |
|---|---|---|
| eu-north-1 spot | `MaxSpotInstanceCountExceeded` | quota is 0 |
| eu-north-1 on-demand | `VcpuLimitExceeded` | quota is 0 |
| us-east-1 spot + on-demand | `InsufficientInstanceCapacity` | quota fine, no hardware |

Use this pair to tell the two failures apart — they need opposite responses (file a case vs. try
another pool), and a price-sorted pool walker must not retry a `VcpuLimitExceeded` pool at all,
while an `InsufficientInstanceCapacity` pool should age back in after a cooldown.

Gotcha: a g7e launch probe must target an AZ that actually offers the type, or it returns
`Unsupported` and tells you nothing. `Subnets[0]` in a default VPC is usually the wrong AZ —
resolve via `describe-instance-type-offerings --location-type availability-zone` first.

Quota status 20:10 UTC: all six cases still CASE_OPENED, no APPROVED/CASE_CLOSED records in any
of the nine g7e regions, all values still 0 outside us-east-1's 8/8.

### 2026-09-16 run 1 (eu-north-1a spot, i-01ee5a9803a47291e): FIRST EC2 BOOT — engine refused a 47.68 GiB cudaHostAlloc

Quota landed ~20:10 UTC (Stockholm on-demand granted 16→8; spot propagated minutes later, and the
*case* still read CASE_OPENED throughout — the applied value is the only truth). First pool tried
won it: **eu-north-1a spot at $1.2072/hr**, 42% under RunPod secure's $2.09.

**Measured:**
| stage | number |
|---|---|
| `run-instances` → kernel boot | **16 s** |
| → SSM agent active (= shell) | **62 s** (RunPod create→container: 129 s cold) |
| S3 sync 145 GB, us-east-1 → eu-north-1 | 311 s, **465 MB/s** |
| S3 upload 145 GB, in-region | 131 s, **1.1 GB/s** |
| 7 GB image pull in eu-north-1 | 33 s, 212 MB/s |
| peak host RAM at failure | **6353 MiB** of 64 GiB; 57.4 GiB still available |

**The engine never came up.** All three entrypoint attempts died identically at model-skeleton
build, in `Qwen4ExpPinnedHostEmbedding.__init__` (qwen4_exp.py:799):
`torch.empty(shape, device="cpu", pin_memory=True)` → `torch.AcceleratorError: CUDA error: out of
memory`. That is a **`cudaHostAlloc` of the 47.68 GiB PLE table being refused**, not GPU memory
and not physical RAM — 57 GiB was free and peak usage never exceeded 6.3 GiB.

Two candidate causes, both addressed in run 2:
1. ~~`RLIMIT_MEMLOCK` in the container.~~ **DISPROVEN in run 2**: memlock measured `unlimited`
   on the host, in the container by default, and with `--ulimit memlock=-1:-1`. Docker was always
   handing out unlimited locked memory. There is no portability bug in the image contract.
2. **Page cache.** The bank-to-S3 pass had just pushed 145 GB through cache immediately before
   the engine asked the kernel to pin 74% of RAM in one allocation. Fix: `drop_caches` first.

Run 2 logs `ulimit -l` inside the container both default and raised, which settles which one it was.

**The DLAMI trap that nearly cost the instance:** the Deep Learning AMI already consumes the
1.9 TB instance store into an LVM volume group at `/opt/dlami/nvme`, so `mkfs` on the raw device
fails busy. With `set -x` but no `set -e` the script sailed on with `/workspace` on the 96 GB EBS
root and would have died of ENOSPC ~12 min into a billing GPU. Fixed two ways in `g7e_boot.sh`:
use the LVM when present, and a hard gate that aborts if `/workspace` has <200 GB free. The silent
degradation was the real defect — a failed mount must never turn into "works until it's expensive".

**eu-north-1 is now self-sufficient:** bucket `gamesummoner-models-eu-north-1-<account>` holds
all 425 objects / 144.82 GB. Seeded by uploading from the GPU box's local disk (in-region, free)
rather than replicating from us-east-1.

**Cost:** ~$3.45 total. $3.09 of it was cross-region egress pulling us-east-1 → eu-north-1, which
was avoidable — the right move was to pull straight from the RunPod volume again (ingress to AWS
is free, ~$0.16 of CPU instance time), as Nick pointed out. That spend is now converted into the
permanent regional copy, so no future boot repeats it.

### Gotcha: a terminated spot instance still holds its quota
The instance reached `terminated` but its one-time spot request `sir-jtwzmezk` stayed `active`,
and **the request, not the instance, is what counts against `L-3819A6DF`** — so the next launch
got `MaxSpotInstanceCountExceeded` with nothing running. `cancel-spot-instance-requests` is
accepted immediately but the state field lags there too.

At an 8 vCPU grant (one box) this fully blocks the next boot, so a scaler that relaunches
promptly must cancel the old request explicitly and treat `MaxSpotInstanceCountExceeded` as
"retry shortly" rather than "out of quota" — it is a different condition from `VcpuLimitExceeded`,
which means the case really has not been granted. Three distinct refusals now, needing three
different responses:

| error | meaning | response |
|---|---|---|
| `VcpuLimitExceeded` / quota is 0 | case not granted | file/appeal; never retry this pool |
| `MaxSpotInstanceCountExceeded` with nothing running | stale request holds the slot | cancel it, retry in seconds |
| `InsufficientInstanceCapacity` | quota fine, no hardware | next pool; age back in after a cooldown |

Also confirmed: EC2 does not bill the `shutting-down` state, so terminate-on-exit costs nothing
and there is no reason to rush teardown.

### Billing shape: EC2 vs RunPod (Nick, 2026-09-16)
- **EC2 bills from the `running` state**, not from the `RunInstances` call. The pending phase
  (~16 s, API call → kernel) is free. It also does **not** bill the `shutting-down` state
  (confirmed by Nick against his console), so terminate-on-exit is free and there is no reason to
  rush teardown.
- **RunPod bills from pod create**, so its 99–160 s provision+image-pull is billed dead time.
- Not a clean sweep: on EC2 everything after `running` is billed, including **~70 s of cloud-init
  before user-data starts**, plus the S3 sync and the image pull. RunPod folds the pull into its
  own provisioning. The number that decides it is **billed seconds to serving** — RunPod's is
  129 s cold, ours is still unmeasured.
- **VERIFIED against AWS docs: no charge for a Spot instance AWS interrupts within the first
  hour after launch.** (docs.aws.amazon.com/AWSEC2/latest/UserGuide/billing-for-interrupted-spot-instances.html)
  After the first hour, Linux is charged for every second used.** A build is ~20 min, so every interruption would land inside that window — turning
  the usual spot risk into a free partial run. Given a 3/10 placement score, interruptions are
  likely enough that this materially changes the economics. Verify against a real interrupted
  instance on the bill before relying on it.
- Cloud-init's ~70 s is the cheapest thing on the boot critical path to remove: a baked AMI with a
  systemd unit starts the work at boot instead of waiting for cloud-init's final stage.

### The free-interruption window is a bigger deal than it looks
A build runs 8-15 min and a full card-cycle implies ~50 min, so **essentially every build falls
inside the first hour** — meaning an AWS-initiated interruption costs wall-clock and **zero
money**. Spot's two risks separate cleanly:
- **Scarcity is real and unsolved** (3/10 placement score globally, us-east-1 refused all four
  pools for an hour). This is the risk that matters.
- **Interruption is financially free at our job shape.** Retry costs only latency. This inverts
  the usual spot calculus and argues for retrying aggressively rather than paying up for
  on-demand the moment spot wobbles.

**New design constraint: keep a build under an hour.** Past 60 min the free window closes and an
interruption bills every second used with nothing delivered. Build duration was a latency concern;
it is now a cost cliff, and a job approaching ~55 min should checkpoint or be cut rather than
gamble the whole spend.

### 2026-09-16 run 2 (eu-north-1a spot, i-06402a89de264421b): both hypotheses dead, ratio is the suspect
Same failure, same place. Diagnostics settle two things and open a third.

| mark | value |
|---|---|
| in-region S3 sync, 145 GB | **258 s = 562 MB/s** — SLOWER than the cross-region download (465 MB/s) and half the 1.1 GB/s upload |
| host / container / raised memlock | **unlimited / unlimited / unlimited** |
| MemAvailable after `drop_caches` | 62461 MiB |
| min MemAvailable during engine | **57306 MiB** vs a 48827 MiB request |
| peak host RAM used | 6453 MiB |
| GPU at failure | `Load weight begin. avail mem=94.14 GB` |

- **Not memlock.** Unlimited everywhere; the `--ulimit` flag changed nothing.
- **Not page cache.** Caches were dropped first and 56 GiB was still available at the low point.
- **Not GPU memory, not total host RAM.**
- **Remaining suspect: the ratio.** A single `cudaHostAlloc` for 47.68 GiB is **76% of 64 GiB**
  physical. On RunPod the identical allocation was 25% of a 188 GB cgroup, which is why this never
  appeared there. NOT YET PROVEN — two hypotheses have already died here, so it gets a probe
  before it gets a quota appeal.
- **The staging bottleneck is the AWS CLI, not the network.** 562 MB/s is 9% of the 50 Gbit NIC on
  8 vCPUs of Python TLS. Levers: `s5cmd`, or delete the leg entirely by pointing the prepacked
  loader's ranged `pread`s at S3 (mountpoint-s3 needs no code change; a native S3 reader gives
  retry control, which matters because S3 can 500 where a local `pread` cannot fail).

**Next: a pinned-allocation ceiling probe** — find the largest single `pin_memory=True` tensor a
64 GiB g7e.2xlarge will grant, and whether 24+24 GiB succeeds where 48 does. If the ceiling is
below 47.68 GiB, 2xlarge is structurally disqualified and we need **g7e.4xlarge** (16 vCPU,
128 GiB, 47.68 = 37%), spot **$1.8161 in eu-north-1a — still under RunPod's $2.09**. That needs a
16 vCPU quota; the grant was 8 in every region, so it would require an appeal.

### The PLE table is already fp8 — there is no quant escape hatch
Nick asked whether this should just fit on the card, or fit with a smaller quant. Checked against
the pack manifest:

```
model.layers.1.ple.ple_embedding.ngram_embedding.weight
shape [320001536, 160]  dtype float8_e4m3fn  1.00 bytes/elem  = 47.68 GiB
```

- **Already fp8.** 51.2e9 elements at one byte. The 47.68 GiB IS the compressed form; there is no
  dtype left to drop to that the gather kernel supports.
- **It cannot go on-card even hypothetically at fp4**: 73.46 (weights) + 23.84 (fp4 PLE) =
  **97.30 GiB against a 96 GiB card**, with nothing left for KV cache. At the real fp8 size it is
  121.14 GiB. The model does not fit in 96 GB on ANY provider — RunPod offloads the identical
  47.68 GiB, it just has 188 GB of cgroup to do it in.

**Consequence, and it is not EC2-specific: this model has a hard ~48 GiB host-RAM requirement.**
Any host sizing for Flash-Next must budget 48 GiB of pinned host memory plus overhead, forever,
independent of provider. g7e.2xlarge's 64 GiB is marginal *by construction* (75%, ~16 GiB slack);
g7e.4xlarge's 128 GiB is the correctly-shaped instance (37%), not a workaround. At **$1.8161 spot
in eu-north-1a it is still under RunPod's $2.09**, so moving up a size does not break the thesis.

### CORRECTION: 64 GiB is enough. The killer is MemFree vs MemAvailable.
Nick pushed back with github.com/SSHdotCodes/qwen-3.8-flash-next-pro6000 — same checkpoint
(`RadixArk/Qwen3.8-Flash-Next-NVFP4`), same `--ple-offload-embedding`, README requires
**"~50 GiB free host RAM"** on one PRO 6000. He was right; my "64 GiB is marginal by construction"
was wrong, as was the memlock theory before it.

Measured cause, from our own `ram.log`:

```
free right after drop_caches   62,697 MiB    <- ample
free during every attempt      37,442-40,700 MiB
PLE allocation needs           48,827 MiB    <- short by 8-11 GiB
MemAvailable throughout        ~58,000 MiB   <- reassuring and irrelevant
```

`cudaHostAlloc` needs genuinely **free** pages; the kernel does not aggressively reclaim page
cache to satisfy one huge pinned request. `MemAvailable` counts reclaimable cache and is therefore
the wrong gauge. The ~22 GiB of cache between our `drop_caches` and the allocation comes from
**our own entrypoint extracting the ~10 GB env tar off the volume**, plus assorted reads — the
reference setup has no such step because its environment is baked into `lmsysorg/sglang`.

**The engine-on-the-volume design is the problem here, and it is a RunPod-shaped optimisation.**
It exists to cut RunPod's 90-120 s image pull. On EC2 a 7 GB pull took **33 s**, so an image with
the env baked in costs ~45 s more and removes both the tar extraction and the cache churn.
`llm-v14` was exactly that variant (16.7 GB, engine in image) before v15/v16 moved it to the
volume — so the known-good configuration already exists.

Fix ladder, cheapest first:
1. Host-side `drop_caches` loop during container startup (crude, proves the diagnosis in one run).
2. Run the engine-in-image variant so no tarball is extracted at boot.
3. Longer term this disappears anyway if the pack is read straight from S3 (no staging, no cache).

Other flags worth noting from the reference launch, none of which caused this but all of which
differ from ours: `--context-length 262144` (our serve script bakes 524288, and our own log warns
`User-specified context_length (524288) is greater than the derived context_length (262144)`),
`--max-running-requests 1`, `--cuda-graph-max-bs-decode 1`, `--shm-size 32g`, and
`--disable-flashinfer-autotune`.
