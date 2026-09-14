# conc-replay — does a 4-build pod keep its prefix cache?

Status: done
Control: the solo arm of the same pod; the 2026-09-02 Pennyroyal bench (experiments.md: conc2
1.7× aggregate at 54K, conc4 collapses)

## Purpose

A build turn resends its whole transcript (~100K tokens by mid-build). Prod pods run 2 slots.
If a pod could run 4 builds with every turn a prefix-cache hit, the pod-hour serves 4 games for
the price of 2. If concurrency evicts the cache, every turn re-prefills ~100K (~10 s) before the
first token and the 4th build pays for itself in latency. Today's two concurrent prod builds
recorded no cache telemetry (`prompt_tokens_details: None` — the engine needs
`--enable-cache-report`), so nothing on disk answers this.

## Hypothesis

Flash-Next is hybrid: per-sequence Mamba/DeltaNet states live in a small fixed pool
(`max_mamba_cache_size`, ratio-sized by default), separate from KV. Four resident builds plus
the radix tree's cached prefixes exceed the default pool, states evict, and a turn whose KV
prefix is cached still re-prefills from the last cached mamba state. Measured: per turn, time
to first token and `cached_tokens`/`prompt_tokens`, solo vs four concurrent vs four concurrent
with the mamba pool 4×. Expected: solo TTFT flat (~1 s) across prompt length; conc4-default TTFT
proportional to prompt tokens (misses); conc4-mamba×4 back to flat. Idea failure: conc4-default
already flat (then 4 slots is a settings edit) or mamba×4 does not fix it (then the eviction is
KV, and the lever is `mem-fraction`/window, not this flag).

## Setup

Content does not matter to a cache; counts do. So the probe is synthetic (`synth.py`): N
conversations grown concurrently, one thread each, every turn appending ~1K tokens of random
words as a user/assistant pair so each request extends the previous one's token prefix exactly
as a build turn does. 100 turns, ~23K to ~123K tokens per stream, `max_tokens 32`, thinking off.
Per turn: time to first token, `prompt_tokens`, `cached_tokens`. Engine: image `llm-v20`, the
pod's own serve script (mamba pool pinned at 24, 4 running requests), worker agent skipped,
`--enable-cache-report`. Radix cache flushed before every arm.

    aws s3 sync . s3://<llm volume>/conc/ --exclude '*' --include 'synth.py' --include 'arms.sh' --include 'pod_main.sh'
    setsid nohup ./rent.sh > results/rent.log 2>&1 &            # rent, watch, fetch, terminate
    python3 analyze.py results/<pod>                            # after DONE

Arms, in order on one pod (`arms.sh`): `solo`, `conc2` (prod today), `conc4`, then a relaunch
with `--max-mamba-cache-size 96` (48 if 96 will not boot) and `conc4-pool96`, `conc2-pool96`.

## Log

## Outcome

- 2026-09-13 16:10 — bundle on both llm volumes (46 MB: four rebuilt request logs + scripts).
  Client smoke-tested against the local ninfer (prompt tokens within 7 of the recording; TTFT
  and SSE parsed). `rent.sh` detached: first create try refused on both DCs, both editions
  (stock-out), retrying every 120 s for 40 min.
- 2026-09-13 16:12 — pod `n869scfg0mjqyx` landed on try 2 (EU-RO-1, Workstation Edition),
  engine up at +100 s, no autotune re-key from `--enable-cache-report` or `--cuda-graph-bs 1 2 3 4`.
  Cache report works (turn 1: 23,104 cached of 50,143; the 27K miss prefilled at ~11K tok/s).
  Pool from the boot log: KV `max_total_num_tokens=918464` (not the limit), mamba
  `max_mamba_cache_size: 24` (pinned by the serve script, ssm 1.32 GB total), one running
  sequence holds 4 of the 24 state slots. `arms.sh`'s pool grep did not match this log format,
  so this pod runs solo + conc4-default only; the ×4 arm needs a second pod (grep fixed in repo,
  volumes updated after this pod is done — the running pod reads arms.sh from the volume).
- 2026-09-13 16:22 — Nick: the recorded replay is unnecessary, content does not matter to the
  cache; kill it and test the thing that matters. Pod terminated at 10 min (~$0.37). Kept:
  200 solo turns of `9cd536de2ac9` in `results/n869scfg0mjqyx/solo.jsonl` (TTFT median 0.49 s,
  uncached median 1,308 tokens/turn, 0 errors) — a real-prompt warm baseline. Rewritten as the
  synthetic ramp above; second pod launched.
- 2026-09-13 16:26 — pod `3hlhgezwnhtv6k` (EU-RO-1 WK), engine up +2 min, all cache arms done
  by +11 min. Synthetic ramp, 100 turns to ~123K, `max_tokens 32`:

  | arm | TTFT p50 @100K | TTFT p50 @40K | uncached/turn | cached frac | evictions past turn 0 |
  |---|---|---|---|---|---|
  | solo | 0.53 s | 0.35 s | ~1K | 0.99 | 0 |
  | conc2 (pool 24) | 0.81 s | 0.63 s | ~1K | 0.99 | 0 |
  | conc4 (pool 24) | 1.40 s | 1.11 s | ~1K | 0.99 | 0 |
  | conc4 (pool 96) | 1.39 s | 1.11 s | ~1K | 0.99 | 0 |
  | conc2 (pool 96) | 0.85 s | 0.67 s | ~1K | 0.99 | 0 |

  Read: the eviction hypothesis is false at four streams. Engine log peak during conc4: mamba
  pool 0.67 (16 of 24 slots, ~4 per stream, room for two more streams), KV 0.53 of 918K.
  Raising the pool to 96 changes nothing and shrinks KV to 619K. TTFT grows ~2.7 ms per 1K
  tokens of context on a HIT (the hybrid layers' per-turn cost), and concurrency adds a flat
  offset (+0.3 s at 2, +0.9 s at 4): the card's prefill compute shared, not cache misses. The
  only real misses are the four cold first prompts, serialized in the prefill queue (5.5 → 18 s).
  Verdict: works — 4 slots is a settings edit as far as the cache goes. Open: decode throughput
  per stream at 4 (next log entry). RunPod proxy ssh works on these pods (`-tt`, interactive
  shell only, files via the volume's S3 API), so arms can be added to a live pod.
- 2026-09-13 16:50 — decode arms on the same pod (added live over proxy ssh + S3). Each stream
  ramped to ~104K (cache-warm, ~1K uncached), then 2,048 tokens with EOS ignored:

  | streams | tok/s per stream | aggregate tok/s | TTFT |
  |---|---|---|---|
  | 1 | 128 | 124 | 0.53 s |
  | 2 | 114–115 | 218 | 0.83 s |
  | 4 | 79–88 | 290 | 0.6–1.0 s |

  Read: 2 streams = 1.76× aggregate at −10% per stream; 4 streams = 2.3× aggregate at −35% per
  stream. Decode is not free at 4 on Flash-Next at 100K: the hybrid layers' per-token work
  scales with resident sequences. Zero errors, zero cache misses across all arms.

## Outcome

Verdict: works, with a cost curve. Nick: 1→2 is the worthwhile step (each user ~10% slower, compute per game ~57%); 2→4 not worth −27% per stream. Prod stays at 2 slots. Four builds on one Pro 6000 keep every turn a prefix-cache
hit (mamba pool 24 has 8 slots spare; pool 96 buys nothing and costs a third of KV). What the
4th slot costs is per-stream speed: a build's turn writes at ~83 tok/s instead of ~114 (2 slots)
or ~128 (solo), and its first token lands ~0.6 s later. Pod-hour throughput: 2 slots 1.76×,
4 slots 2.3× solo. So `llm.slots` 4 is a settings edit that lowers cost per game ~25% over 2
slots and lengthens each build ~35%. Whether that trade is wanted is a product call (queue wait
vs build wall). Not measured: prefill contention when four turns start together — the cold
turn-0 queue showed serialization (5.5 → 18 s), and real builds' compaction turns re-prefill
~20K. To ship in experiments.md as one section with pod `3hlhgezwnhtv6k`'s two tables.
Also shipped as a prod ask: `SGLANG_ARGS=--enable-cache-report` (free, boots clean, gives
`cached_tokens` per turn in every recorded build).
