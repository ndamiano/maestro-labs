# Pennyroyal fast-boot: get rent→serving under 180 s

## Goal
Qwen3.8-Flash-Next served by the Pennyroyal SGLang fork on a rented RTX PRO 6000 SE (RunPod, US-NC-2)
must go from pod-create to /health_generate 200 in ≤180 s average. Today: ~435 s. Nick's ruling:
solve it here — no engine split, no Modal (+60%), no Hetzner (monthly commit), no FlashBoot
(bimodal, worst-case for sporadic builds), CRIU impossible on RunPod (no caps).

## Measured baseline (2026-09-02, all on PRO 6000 SE $2.09/hr)
| stage | today | target | lever |
|---|---|---|---|
| provision + image pull | 110 s (28 GB image; 53 s when host-cached) | 20-50 s | image diet |
| O_DIRECT copy volume→NVMe | 105 s | 0 | stream direct from volume in new loader |
| python/CLI import → "Load weight begin" | ~90 s | 25-40 s | profile it first — nobody has; bake pycache |
| weight load+repack | 102 s (NVMe) / ~190 s (volume) — CPU-bound, NOT IO (NVMe 10× faster bought only 1.7×) | 15-25 s | THE PATCH (below) |
| FlashInfer autotune | 2 s warm; ~300-500 s when cache key changes | 2 s | bake post-graph-bs cache into image v4; key = server-args hash |
| CUDA graph capture | ~26 s with --cuda-graph-bs 1 2 4 | 10-15 s | try bs {1,2} (builds run ≤2 streams) |

## THE PATCH: `--load-format prepacked` in the fork
Clone at labs/penny-fork (jpezzulli/sglang-rtxpro6000 @ pennyroyal-v2.1.0).
`process_weights_after_loading` (python/sglang/srt/layers/quantization/modelopt_quant.py:
linear ~1770, MoE ~2422; invoked from model_loader/loader.py ~1018) rewrites layer params in place
(deinterleave w13, pad, flashinfer shuffle_matrix_a/sf_a, rebind scales) + side attrs
(weights_padding_cols, _w13_deinterleaved, output_size_per_partition, MoE _cache_permute_indices).
1. DUMP (once per checkpoint+layout-config): after normal load+process, stream model.state_dict()
   to ONE flat file on the volume + sidecar JSON of side attrs. Key by config hash (same idea as
   the autotune cache key).
2. LOAD: init model skeleton, stream flat file sequential→pinned→H2D, restore attrs, SKIP
   load_weights and the process loop entirely.
3. Template in-tree: model_loader/expert_pack_loader.py is the fork's own prepacked SSD loader
   for deepseek-v4-flash/kimi — copy its structure.
4. Watch: aliased/derived params (weight_scale_interleaved), non-persistent buffers, dump
   invalidation on --fp4-gemm-backend / moe backend / tp change.
Est. 2–4 days incl. pod test iterations (~$0.40 each: rent SE pod with image llm-penny-v3,
containerRegistryAuthId cmrtn9wl200gcb9svb78kn7e0 — MANDATORY, repo private, without it pod exits
in 1 s with no logs).

## Order of work
1. Import profile (1 pod-hour): python -X importtime -m sglang.launch_server …; find the 90 s.
2. The patch (dump/load). Validate: identical logits on a fixed prompt vs normal load, then a
   full cards build.
3. Image v4: bake correct autotune cache + pycache + patched fork; diet the 28 GB image.
4. Re-measure full chain 3×; average vs 180 s gate.
5. If green: swap prod template to penny (entrypoint scripts already correct in repo working
   tree: Dockerfile.worker-llm-penny + scripts/worker-llm-penny-entrypoint.sh, UNCOMMITTED —
   commit only bundled with the adoption evidence, per doctrine).

## Serving contract that must survive the patch
Canonical launch = configs/pennyroyal/serve-nohicache.sh pattern (in image at /root/serve-nohicache.sh):
--ple-offload-embedding is LOAD-BEARING (without it weights alone exceed 96 GB → OOM),
--json-model-override-args YaRN rope, --reasoning-parser qwen3 --tool-call-parser qwen3_coder,
chat_template.jinja from ckpt, PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,
--mem-fraction-static 0.981, --cuda-graph-bs 1 2 4 --skip-server-warmup (v3 additions).
Env: TARGET_MODEL/CACHE_BASE/NIXL_STORAGE_BASE/SGLANG_EXE/REPO_ROOT/NIXL_CONFIG.
Model: RadixArk/Qwen3.8-Flash-Next-NVFP4 — ON THE VOLUME at /workspace/models/pennyroyal
(126 G; the GGUF is DELETED; volume szjxc7ha34 has ~20 G free).

## Operational gotchas (each cost real time tonight)
- SGLang setproctitle: `pkill python` does NOT kill its servers. Kill with -f sglang FROM A
  SCRIPT FILE ONLY — any inline ssh command carrying the string kills its own shell (5 incidents).
- Health-wait: trust only HTTP 200 or sustained VRAM≈0. pgrep races; a stale server answers
  "healthy in 1 s".
- Container cgroup = 188 GB; mmap'd 126 G ckpt + PLE offload + load buffers can SIGKILL (-9) the
  scheduler. O_DIRECT for staging copies; a relaunch after OOM usually loads.
- Only ONE timing harness at a time on a pod — two loops pkill each other's servers.
- Changing server args re-keys the FlashInfer autotune cache → one 300-500 s re-tune; bake after
  flags settle.
- runpod REST: no dataCenterIds for US-NC-2 (omit; volume pins DC). Worker token env WORKER_TOKEN.
- Local maestro pieces for a build test: settings llm.model=pennyroyal reasoning=medium, backend
  `python run.py`, worker `python -m worker.agent --queue llm --target http://<IP>:<port8001>`,
  harness ~/Documents/Labs/design-requests/run_battery10.sh <arm> <set.json>.

## Wider context
Pennyroyal beat llama.cpp everywhere else: decode 203 vs 96 short / ~100 vs 55 at 54K, conc-2 agg
1.7× vs 1.19×, F1 quality "one of the better ones" (~$0.68/game vs ~$1 for 27B-5090). Boot time is
the ONLY blocker to it becoming the prod llm engine. Memory file reference_pennyroyal.md has the
full trail.

## Progress 2026-09-02 (session 1, pod 9v35py1scumhns, ~25 min @ $2.09/hr)
- **The "90 s import" was misattributed — actual import is 10.7 s cold / 5.4 s warm** (full
  `launch_server` chain; compileall bake worth ~5 s at most).
- **Real thief: derive_namespace.py full-file SHA256 fallback — ~170 s silent, every boot.**
  Ckpt on volume had no `.cache/huggingface/download/*.metadata`, so the NIXL namespace helper
  hashed all 126 GB before the first log line.
- **FIXED on volume (persistent):** real sha256 metadata written for all 206 shards
  (revision 7b719225242aacd3dbd3f9407468c2ee9a9d2594; hashed in 52 s, 12-way parallel).
  Verified: NIXL namespace line at **+1 s**, "Load weight begin" at **+16 s** (was +187 s).
  Side effect: namespace digest changed (identity source field) — harmless, NIXL stripped.
- Run 1 timeline (cold): +187 load-begin → +453 target shards (206 @ ~1 s/it off volume) →
  +515 draft pass + KV alloc → scheduler SIGKILL -9 at +516 (the known 188 GB cgroup OOM),
  never healthy. Run 2 (serve2, warm page cache) was at +35 s mid-load when session ended —
  **no clean healthy-boot number yet; rerun on fresh pod tomorrow.**
- New floor estimate: provision ~110 + namespace ~2 + import/init ~16 + load/repack (patch
  target) + capture ~26. The prepacked-loader patch now owes the load+repack phase only.
- Harness that works (reuse tomorrow): no ssh needed — pod entrypoint waits for
  s3://szjxc7ha34/fastboot/run.sh (profile+poller), commands land as fastboot/cmd-NN-*.sh via
  volume S3 (`--profile runpod --endpoint-url https://s3api-us-nc-2.runpod.io`), outputs in
  fastboot/out/. Poller self-terminates on fastboot/STOP or after 100 min. Pod create JSON as
  in serve trial: image llm-penny-v3 + containerRegistryAuthId, no dataCenterIds, ports [].
- Next: fresh-pod serve rerun for clean post-fix number, then THE PATCH (dump/load), then
  image v4 (bake pycache ~5 s + re-keyed autotune cache).

## Progress 2026-09-02 (session 2, pod 3keym3shu2qtbz, ~25 min)
- Clean measurements on fresh pod (same host opulb0ogokgh, image + ckpt page cache warm):
  container up +1.4 s after create; namespace fix holds (+1 s).
- **Autotune cache in llm-penny-v3 is STALE**: runtime key 99004d33460b8ec4, baked keys
  76a60bb0/50116542 → every fresh pod re-tunes ~285 s. Fresh cache harvested to volume:
  s3://szjxc7ha34/fastboot/penny_cache_v4.tgz (39 MB: /root/cache + serve script + nixl toml)
  → bake into image v4.
- Cgroup OOM reproduced on FIRST launch of the pod (died mid-autotune +305); attempt 2 on same
  pod loaded clean. Pattern now: first-launch OOM ~50%, relaunch works — entrypoint needs the
  retry loop. Harness flaw found: health-wait must watch engine pid and bail early, not sit out
  the full timeout (wasted ~4 min).
- **Warm-everything launch→healthy = 161 s** (init 16, load 111+12 = CPU repack floor ~102-123,
  autotune ~2, capture+startup ~15). Old 451 s → 161 s with zero code changes.
- Full-chain estimate: ~270 s cold-host / ~165 s warm-host. THE PATCH (load 123→~20-25 s) puts
  cold ≈ 180 s gate. Volume-cold load penalty (~+135 s vs page-cache-warm) still unmeasured
  post-fix — patch makes it moot (single sequential stream read).
- Next: prepacked-loader patch in ~/Documents/Labs/penny-fork; then image v4 (penny_cache_v4.tgz
  + retry-loop entrypoint); then 3× fresh-host re-measure.

## Progress 2026-09-02 (session 3, pod 7ba7kn7mssevul ~65 min): THE PATCH WORKS
- Patch written in ~/Documents/Labs/penny-fork (uncommitted): prepacked_loader.py (new) +
  LoadFormat.PREPACKED in load_config.py + top-of-get_model_loader dispatch in loader.py +
  LOAD_FORMAT_CHOICES in server_args.py. Generic snapshot design: dump params/buffers/__dict__
  tensors (object+storage dedup keeps aliases), scalar attrs, pinned flag per storage; restore
  frees only manifest-bound init tensors (2x-VRAM OOM otherwise), rebinds via param.data,
  keeps None placeholders registered, deletes consumed names. Standalone torch test green
  (scratchpad test_prepacked.py, cpu+cuda).
- Bugs burned on the way: LOAD_FORMAT_CHOICES hardcoded; modelopt auto-select shadowed the
  dispatch (must be top of get_model_loader); _prepare_weights format switch (flip
  load_config.load_format to SAFETENSORS in __init__); emptying unbound init tensors = illegal
  memory access at first forward; deleting None param placeholders = AttributeError 'bias';
  CPU pack storages must be re-pinned (PLE zero-copy).
- MEASURED on pod: dump 121.1 GiB target + 4.0 GiB draft (draft routes through prepacked too,
  separate key); **restore 121 GiB in 20.7-31.2 s**; restored engine launch→healthy **68 s**
  (warm autotune; vs 161 s post-fix normal, 451 s original). Load phase 123 s → ~35 s incl draft.
- CORRECTNESS: same-engine double probe diverges @14 (engine nondet at temp 0, spec decode);
  normal-vs-normal cross-process diverges @23; **prepacked-vs-normal tokens fully equal** →
  pack-restored model indistinguishable from normal load.
- OPEN: pack lives on container disk only — volume has ~20 GB free, pack ~125 GB total; needs
  Nick's ruling: delete safetensors ckpt from volume after dump (re-downloadable in ~2 min via
  hf_transfer) or grow/second volume. Then: dump-to-volume run, restore-from-volume timing,
  image v4 (autotune cache + patched fork + retry entrypoint), full cards build through a
  prepacked engine, 3x fresh-host chain measurement vs 180 s gate.

## Progress 2026-09-02 (session 4, pod 07mt0a4tfsh914 ~25 min): PACK ON VOLUME, ckpt swapped
- Option A executed: 205 safetensors shards DELETED from volume (kept config/tokenizer/index +
  model-bf16-00010.safetensors — derive_namespace.py raises with zero *.safetensors). Pack at
  /workspace/models/pennyroyal/prepacked/ (130.1 GB target .bin + manifest, 4.3 GB draft).
  Refill path if ever needed: hf_transfer ~2 min.
- Dump-run engine OOM'd post-dump (known cgroup OOM), retry restored from NVMe pack and went
  healthy — the retry loop + pack self-heals a crashed first boot.
- **Restore from VOLUME: 121.1 GiB in 104.5 s (~1.2 GB/s single stream); launch→healthy 157 s**
  (warm autotune). NVMe restore was 24 s — volume read is now THE bottleneck. The 12-thread
  sha256 pass read the same volume at ~2.4 GB/s → parallel range readers in restore_model
  should roughly halve the 104 s.
- Chain arithmetic now: cold host ≈ 110 provision + ~157 = ~267 s; warm host ≈ ~160 s. To beat
  the 180 s average: (1) parallel-read restore (~-50 s), (2) image v4 diet (provision), then
  3x fresh-host measure.

## Progress 2026-09-02 (session 5): autotune mystery SOLVED, v4/v5/v6 images
- v4 (pushed): correct-key autotune json + patched fork + prepacked-default entrypoint with
  3-attempt retry. Fresh-pod measure: pull fast (75 s), pack hit, restore **32-37 s from volume
  (parallel readers, was 104.5 single-stream)** — but healthy +613 s: attempt-1 OOM (+215 s tax)
  and ~294 s "autotune" phase. Worker agent also crashed (system python3 lacks requests) — fixed
  by running worker on /opt/venv/bin/python3.
- **"Autotune" 294 s is NOT tuning — it's cutlass fused_moe JIT COMPILATION.** The tactics json
  stays a 1670-byte metadata stub always (never persists tactics; also the key re-keys under
  --load-format prepacked). The real cache is the compiled .so under
  flashinfer/.cache/.../cached_ops/, and flashinfer's try_load trusts ONLY the AOT dir without
  re-running ninja — the tarred JIT dir re-ninjas every fresh container. --disable-flashinfer-
  autotune does NOT help (still compiles; decode drops ~200→~130 tok/s) — autotune stays ON.
- v5: diet via cudnn-runtime base + toolkit subset (nvcc/cudart-dev/cccl/nvrtc-dev/nvml-dev/
  cusparse-dev/cublas-dev/cusolver-dev): **28.8 → 22.1 GB**. Boot-tested only as part of v6.
- v6 (building): v5 base + penny_cache_v6.tgz + **compiled ops promoted to FLASHINFER_AOT_DIR**
  (/opt/venv/.../flashinfer/data/aot/<op>/<op>.so) + **posix_fadvise(DONTNEED) in the pack
  reader** — the first-launch cgroup OOM is page cache from reading the 130 GB pack buffered.
- Next: fresh-pod v6 measure (expect: no OOM, no 294 s compile, restore ~35 s → chain ~110-160 s
  cold); then 3x average vs the 180 s gate; then swap prod template + commit bundle.

## Progress 2026-09-02 (session 6): v6 MEASURED — engine fixed, pull is the remaining tail
- llm-penny-v6 pushed (22.1 GB): AOT-promoted kernels + fadvise reader + parallel restore +
  venv worker python + retry entrypoint + diet base.
- 3x fresh-pod rent→healthy, real entrypoint: **205 s** (cold host, pull ~99 s), **265 s**
  (cold host, slow pull ~160 s), **127 s** (host-cached image, provision 20 s). Average 199 s.
- Engine phase is now SOLID: attempt 1 clean every run (no OOM — fadvise fix verified), no JIT
  compile (AOT verified), launch→healthy 105-109 s every time (restore 50-53 s + init + capture).
  Worker agent imports fine on venv python (claim loop reached, dummy CP as designed).
- Remaining variance is 100% provision+pull (20-160 s). Warm-host boots ≈ 127 s — well under
  gate; cold-host ≈ 205-265. Levers if the average must drop: further image diet (multi-stage),
  or accept host-cache warmth in steady state (autoscaler re-rents same DC hosts).
- Verdict vs Nick's ≤180 s average gate: warm-host YES (127), mixed 3x average 199 — close.
  Prod-swap + commit decision is Nick's; adoption evidence = a full build through a v6 pod.

## Progress 2026-09-02 (session 7): v7 image diet — 22.2 → 16.6 GB
- Two-stage squash (rm in a later layer is a whiteout; FROM scratch + COPY --from=builder / /
  makes the deletions count). Cut: system cudnn ~925 MB + nccl 241 MB (torch RPATHs the venv
  wheels), base NPP/cuFFT/cuRAND/nvjpeg/cusolverMg ~660 MB, apt CUDA lib bodies → symlinks into
  the pip wheels ~1.2 GB (they exist only for the JIT link line), nixl cu12 variants ~200 MB,
  /opt/penny/.git. Compressed pull 7.09 → 4.89 GB (−31%).
- Entrypoint: --cuda-graph-bs 1 2 appended via SGLANG_ARGS_EXTRA (last occurrence wins over the
  script's baked 1 2 4; builds run ≤2 streams). Nick's call. Est −3–4 s capture, unmeasured.
- Smoke on the 5090: torch cuda matmul, sglang/flashinfer import, nvrtc CDLL, prepacked loader
  import, nvcc -cudart shared link line — all green, v6/v7 byte-identical behavior (static cudart
  already gone since v5's *_static*.a rm).
- Gotcha burned: the squash layer tar goes through /tmp (DOCKER_TMPDIR unset) and /tmp is ON
  ROOT on this box — first build filled the 3.6 T root to 0 and bricked every Claude Code Bash
  (harness can't create its output file). Freed by pruning build cache + rm v3/v4 local images.
- v7 pushed. First measure run died in 3 s ×3: the diet's rm of /opt/penny/.git broke the serve
  script's `git rev-parse` (SGLANG_REV) under set -e. .git is LOAD-BEARING; deletion reverted,
  16.7 GB rebuilt+repushed. Local smoke never runs the serve script — add a
  SGLANG_EXE=/bin/echo dry-run of serve-nohicache.sh to any future image smoke.
- **v7 MEASURED, 3x fresh pod, all SE (WK does not exist in US-NC-2 — volume pins the DC):
  192 s (cold, pull 102) / 97 s (warm host, provision 13) / 220 s (cold, pull 119).
  Average 170 s — UNDER the 180 s gate.** Engine phase 89/84/105 s (was 105-109): restore
  36.5-54.9 s (volume contention is the spread), capture ~1.8+1.4+1.0 s with bs{1,2}, attempt 1
  clean all three. Repo tars/Dockerfiles moved to docker/ (deploy.sh + deploy.md updated).
- SE capacity droughts are real: two ~20 min waits for a pod today. v8 (env tarball on volume,
  image → base+entrypoint) still available if cold-pull needs to go below ~110 s; not needed
  for the gate.
- Next: prod-swap decision + adoption evidence (full cards build through a v7 pod), commit the
  bundle (docker/Dockerfile.worker-llm-penny + entrypoint + fork patch upstreaming).

## 2026-09-02 (session 8): PROMOTED to prod + DC redundancy started
- Repo: penny image is docker/Dockerfile.worker-llm; llm-v14 pushed; template mcss4tfwhs → llm-v14,
  200 GB disk, env +LLM_MODEL/LLM_N_CTX. Prod settings: queues.llm gpu [WK, SE],
  network_volume_ids ["szjxc7ha34"]; .env LLM_MODEL=pennyroyal, WORKQUEUE_JOB_TIMEOUT=1800; deployed.
- DC survey: WK only in EU-RO-1 (+EUR-IS-1 flickers); SE in 9 DCs. New volume juqk1aq0ew (160 GB,
  EU-RO-1) created, EMPTY. Provisioning pod create was blocked by the harness classifier — run by hand:
    curl -s -X POST https://rest.runpod.io/v1/pods -H "Authorization: Bearer $(cat ~/.runpod_key)" \
      -H 'Content-Type: application/json' -d @provision_eu_pod.json
  It hf-downloads the ckpt to /workspace/models/pennyroyal, then the entrypoint's normal load dumps
  the pack (log: s3://juqk1aq0ew/boot-logs/provision-<pod>.log, eu-ro-1 endpoint). Then: delete
  *.safetensors except model-bf16-00010 + index, terminate pod, prepend "juqk1aq0ew" to
  network_volume_ids on prod.

## 2026-09-02 (session 8): PROMOTED to prod + DC redundancy started
- Repo: penny image is docker/Dockerfile.worker-llm; llm-v14 pushed; template mcss4tfwhs → llm-v14,
  200 GB disk, env +LLM_MODEL/LLM_N_CTX. Prod settings: queues.llm gpu [WK, SE],
  network_volume_ids ["szjxc7ha34"]; .env LLM_MODEL=pennyroyal, WORKQUEUE_JOB_TIMEOUT=1800; deployed.
- DC survey: WK only in EU-RO-1 (+EUR-IS-1 flickers); SE in 9 DCs. New volume juqk1aq0ew (160 GB,
  EU-RO-1) created, EMPTY. Provisioning pod create was blocked by the harness classifier — run by hand:
    curl -s -X POST https://rest.runpod.io/v1/pods -H "Authorization: Bearer $(cat ~/.runpod_key)" \
      -H 'Content-Type: application/json' -d @provision_eu_pod.json
  It hf-downloads the ckpt to /workspace/models/pennyroyal, then the entrypoint's normal load dumps
  the pack (log: s3://juqk1aq0ew/boot-logs/provision-<pod>.log, eu-ro-1 endpoint). Then: delete
  *.safetensors except model-bf16-00010 + index, terminate pod, prepend "juqk1aq0ew" to
  network_volume_ids on prod.
- EU volume provisioning, what actually happened: pods 1-5 ($~5) all wrote into a FULL volume —
  hf download (126 GB) + partial pack hit the 160 GB quota; FUSE writes fail silent, S3 HEAD/ls
  serve stale sizes for known keys, only put-object from outside says QuotaExceeded. Lessons:
  (a) shards out BEFORE pack in; (b) never trust ls/HEAD sizes on a runpod volume for liveness —
  do a tiny put-object as the probe; (c) copying the pack S3→S3 from a $0.12/hr CPU pod is the
  provisioning path (spec: s3copy_pod.json), no GPU pod needed since the pack key is path-free.
  Shards deleted 23:1x UTC (kept model-bf16-00010 + index); copy pod u9r0sy6va8n746 running.
- RunPod volume S3 gateway limits (measured 2026-09-02, EU-RO-1 dest / US-NC-2 src):
  UploadPart > ~128 MB → 413 Content Too Large; 48 concurrent uploads → 524 (Cloudflare origin
  timeout); 16 concurrent 100 MB parts = ~33 parts/min ≈ 55 MB/s aggregate, link-bound (per-stream
  from home 24-33 MB/s). Single `aws s3 cp - | aws s3 cp -` stream ≈ 15 MB/s. Range GET supported.
  Spec that works: s3copy_par5_pod.json (cpu3c ×8, amazon/aws-cli, ranged get-object → upload-part,
  xargs -P 16). 130 GB ≈ 40 min, $0.16 in pod time.
- DONE 2026-09-03 00:1x UTC: EU volume juqk1aq0ew holds the pack (4 range spot-checks match US).
  What worked: fusecopy_pod.json — CPU pod in EU-RO-1, volume mounted, truncate + 16× ranged
  get-object from US gateway → dd seek into the mounted file: 1241 parts, 0 retries, 9.3 min
  (~215 MB/s). Gateway-upload path is dead: multipart session lost ~20-60% of parts over 40 min
  (list-parts inconsistent call to call). Prod: queues.llm.network_volume_ids
  ["juqk1aq0ew","szjxc7ha34"], gpu [WK, SE]; restarted, healthy. First real autoscaled EU pod
  = the boot-from-EU-volume measurement, unseen.
- 2026-09-03 e2e on prod: build 1 (reasoning none) 200 steps/no done, one bad export; build 2
  (medium) ok=True 39 steps 7m53s, playing game, EU WK. Boot 205 s cold-host / 49 s warm-host.
  GPU rate multiplier built+deployed (billing.gpu_rates, jobs.billed_seconds; ALTER run on prod).
  Runs: 2533bb377168 (bad), 1ea20f6c7d29 (good). Prod LLM_REASONING now medium.
- 2026-09-03 v15 (env on volume): fork ndamiano/sglang-rtxpro6000 tag pennyroyal-v2.1.0-prepacked1
  (f9ab07610a) carries the loader; image = cuda runtime + JIT toolchain, 7.0 GB (was 16.7);
  env tarball llm-env-d5b890eab18e.tar (10.08 GB) on both volumes under env/; entrypoint
  restores if /opt/venv missing. Template mcss4tfwhs → llm-v15. Validation build 3 launched
  01:48 UTC (run 002753a79bd5). Repo: master 10d8854 pushed (multiplier code landed in the
  first commit by hook accident; second commit is a 3-line trim).
- v15 boot-looped: runtime stage has no system python3; serve script helpers use #!/usr/bin/env
  python3 → v16 puts /opt/venv/bin first on PATH (verified locally: helper runs, fails only on the
  fake ckpt). Builder cache missed on the v16 build → new env id c0ca5f12c86f → re-upload (old
  d5b890eab18e deleted from both volumes first: US hit QuotaExceeded with both present).
  Local repro recipe: docker run --gpus all -v ws:/workspace -v env.tar:/workspace/env/llm-env-<id>.tar
  with a fake config.json/index/chat_template in ws/models/pennyroyal → reaches the serve script.
- v16 VALIDATED 2026-09-03 02:17-02:33 UTC: pod create→worker 129 s (cold host, 7.0 GB image +
  ~10 GB env tar restore off the volume); build 4 ok=True 47 steps 14m59s, playing game, gate on
  the same pod (idle 60 s held). Template mcss4tfwhs = llm-v16; env tar c0ca5f12c86f on both
  volumes. Master pushed. Remaining levers: warm-host boot (~110 s → mostly engine phase: restore
  36-55 + init 16 + capture ~15); speculative pod start on prompt_proposed; parallel untar if
  the restore shows >10 s on a pod (unmeasured pod-side).
