# DFlash2 drafter on the local 27B

Status: single-run PASSED 2026-09-14 (1.41× token-weighted decode, 1.27–1.62× per call); next = battery on the design chain, then adopt
Control: prove-it run 17c92bff6bda (2026-09-14): four design calls 472/343/525/426 s = 29.5 min at xhigh; ninfer's own log on the integrator call `decode=112–125 tok/s, running=1` at ~117K context (60K prompt + 57K reply)

## Purpose

Local dev only; prod serves Flash-Next on SGLang and is untouched. The local design leg is 30
minutes and a station-sized build another 35–50, all decode-bound on one 5090 at 112–125 tok/s
once the context is long. ninfer's own numbers for this card and model
(docs/performance/qwen3.8-27b.md): MTP3 195 tok/s short / 151 at a 65K completion / 126 on
prose; the DFlash2 K=7 drafter 321 short / 183 at 65K. Roughly 1.4× where we live, which is
~8 minutes off design and ~10 off a build, every run, for a weights change.

## Hypothesis

Serve the same target with `--spec dflash2 --draft-tokens 7` and measure decode tok/s from
ninfer's throughput log on the same station design chain: expect ≥1.3× on the long calls with the
same outputs (the target model is the authority; the drafter only proposes). Idea failure: the
companion was trained on base Qwen3.8-27B and the QUASAR checkpoint accepts its drafts poorly, so
the gain evaporates; or the sm_120 build of upstream ninfer costs more than the gain is worth.

## Setup

What DFlash2 needs (upstream README + docs/maintainer/qwen3.8-27b-artifact.md):
- The companion is packed INTO the .ninfer artifact at convert time; an existing artifact cannot
  have it added. Our `qwen3_8_27b_quasar_nvfp4.ninfer` (2026-08-27) has no `dflash2/` namespace.
- Convert: `python3 -m tools.convert.qwen3_8_27b.convert_nvfp4 --model <Qwen3.8-27B bf16>
  --quantized-model <vllm nvfp4-fp8 checkpoint> --dflash2-model <z-lab/Qwen3.8-27B-DFlash2 @
  50307d4c> --out out/qwen3_8_27b_nvfp4.ninfer --device cuda`. Needs the BF16 base (~55 GB), the
  vLLM NVFP4 quant, and the 2B companion on disk; the QUASAR variant's source checkpoints if we
  want the pairing we run today.
- Serve: today's launch line with `--spec dflash2 --draft-tokens 7` in place of
  `--spec mtp --draft-tokens 3 --lm-head-draft`. Vision, int8 KV, prefix reuse and B≤8 are all
  documented as supported with DFlash2 (docs/maintainer/qwen3.8-27b-dflash2.md); companion state
  is 40 MiB.
- Our local ninfer is the `ninfer-quasar` checkout (93d7a61, "support Qwen3.8 QUASAR artifacts"),
  which predates DFlash2; `--spec` there takes `mtp|dflash` only. Upstream master builds for
  sm_120 the same way (`docs/local_dev.md`); keep the quasar build beside it, `NINFER_BIN` picks.

Two routes, cheapest first:
1. Prebuilt: `kaushikvira/Qwen3.8-27B-nvfp4full-dflash2-NInfer` on HF is a base-model NVFP4
   artifact with the companion packed (third party: read its LICENSE and provenance before it
   lands; it is Qwen3.8-27B base, not QUASAR). One download (~18 GB, /var/lib/models has room:
   check `df` first), one `--model-id`, one bench. Measures the drafter, not our checkpoint.
2. Convert: the QUASAR sources + the z-lab companion through upstream's convert. Measures what
   we'd actually run. Do this only if route 1 shows the gain.

Bench: the station design chain (`python -m maestro.codegen.run --new "Survive on a derelict
space station."`) with `llm.model` pointed at the new artifact; read `decode=` from the ninfer log
over the integrator call and the four call durations from the CLI log. Same ask, same prompts,
same reasoning (xhigh). One GPU: nothing else on the card during the bench.

## Log

### 2026-09-14 — setup

- Route 1 as written is moot: the same week the lab was drafted, three artifact publishers
  repacked their Qwen3.8-27B artifacts with the z-lab companion (`50307d4c`) appended. The one
  that matters is `MirkoCovizzi/Qwen3.8-27B-QUASAR-NVFP4-NInfer` (2026-09-06, 19.78 GB): the
  1,268 base payloads are byte-identical to the 17.55 GB QUASAR artifact we serve today, plus 66
  DFlash2 tensors (21 W8G32 + 45 BF16). So the bench isolates the drafter exactly: same weights,
  same engine lineage, only `--spec` changes. `neroued`'s own nvfp4 v2 (23.72 GB) and the
  `kaushikvira` nvfp4full graft (20.55 GB, needs its own fork for the `nvfp4full` profile) are
  both bigger than the card has room for beside 131K int8 KV + vision.
- Engine: our `ninfer-quasar` checkout (93d7a61) is Mirko's fork, now named
  `ninfer-rtx5090-mobile`. Its master `8debca3` = upstream through `ce7dee50` (DFlash2 engine +
  perf record) + QUASAR support + one fix ("refresh dflash prefill state slot after checkpoint
  forks", past the README-validated `d4bc75d`). Built as a worktree at
  `~/Documents/ninfer-quasar-dflash2` with `/usr/local/cuda-13.1/bin/nvcc` (master requires 13.1;
  PATH nvcc is 13.0, the existing builds already use 13.1). `--spec mtp|dflash|dflash2`,
  `--kv-dtype bf16|int8|fp8|nvfp4|k8v4`.
- Artifact lands at `/var/lib/models/ninfer/dflash2-src/quasar/qwen3_8_27b_nvfp4.ninfer`
  (sha256 `da5efb33…`); on adoption it replaces `qwen3_8_27b_quasar_nvfp4.ninfer` under the same
  model id and `ninfer-quasar` moves to `8debca3`.
- Control detail from the ninfer log (req 1268–1271, the four design calls, MTP3):
  decode 159.4 / 147.3 / 139.1 / 136.3 tok/s, 2.73 / 2.72 / 2.75 / 3.14 tok/round
  (57.6 / 57.4 / 58.5 / 71.4 % acceptance), gen 55317 / 50303 / 72851 / 57036. The integrator
  (req 1271) is prompt 47901 + gen 57036 at 136.3 tok/s. Upstream's own DFlash2 K=7 numbers
  on nvfp4: 224 tok/s short reasoning, 133.5 at a 65K completion, code 191 / story 84 /
  structured 267 — story prose is where DFlash2 loses to MTP, and a design doc is prose.
- Scripts: `serve.sh` (stops the MTP server, serves the v2 artifact with
  `--spec dflash2 --draft-tokens 7 --lm-head-draft`, everything else as `local_gpu.py`),
  `bench.sh` (the `--new` station design chain, then the four request lines from the server log
  into `~/output/dflash2-lab/`).

### 2026-09-14 — run 1: a149981e8c49, DFlash2 K=7 on the QUASAR v2 artifact

Same ask, same prompts, xhigh, one request at a time, nothing else on the card. Server footprint
identical to MTP3 (25.8 GB used, 6.14 GiB free after KV; weights 18.0 GiB). Design calls, ninfer's
own request lines (control = 17c92bff6bda, MTP3, req 1268–1271):

| Call | Prompt | Output ctrl → new | Decode ctrl → new (tok/s) | × | Accepted | Wall ctrl → new |
|---|---:|---:|---:|---:|---:|---:|
| gameplay | 413 | 55,317 → 47,147 | 159.4 → 203.0 | 1.27 | 33.9% | 347 → 232 s |
| visual | 11.5K | 50,303 → 39,855 | 147.3 → 200.1 | 1.36 | 32.8% | 343 → 201 s |
| engineering | 11.6K | 72,851 → 67,208 | 139.1 → 202.0 | 1.45 | 33.7% | 525 → 334 s |
| integrator | 47.0K | 57,036 → 44,319 | 136.3 → 220.7 | 1.62 | 39.0% | 425 → 208 s |
| chain | | 235.5K → 198.5K | | | | 29m27s → 16m15s |

- Decode is flat at ~200 tok/s regardless of output length or prompt size; MTP3 sagged from 159
  to 136 as the sequence grew. The gain therefore grows with the call: 1.27× on the short one,
  1.62× on the integrator — the long calls are exactly where a design and a build live.
- Acceptance 33–39% of 7 drafts ≈ 3.3–3.7 tokens/round, matching upstream's own 65K-completion
  number (34.7%), so the QUASAR checkpoint accepts the base-trained companion as well as base
  does. Idea-failure branch (a) is closed.
- Token-weighted decode over the chain: 145 → 205 tok/s = 1.41×. The 1.81× wall gain includes a
  shorter run (198.5K vs 235.5K output tokens), which is spec-draft variance, not the drafter:
  the target samples with the same temperature and is the only authority on output.
- Outputs: spec.md has the same 33 sections as the control (84.5 KB vs 102.8 KB); per-doc
  sizes within the run-to-run range seen on this ask. Not judged for quality beyond structure.
- Engine notes: the new ninfer log format is `req#N done | … | decode 203.0 tok/s | dflash2
  accepted a/b (p%)` and `throughput | 5.0s | decode N tok/s`, so any log scraper keyed on
  `decode=` / `speculative=` needs updating. Runs are in `~/output/dflash2-lab/`.

### 2026-09-14 — adopted

Nick's call on run 1. The v2 artifact now sits at `/var/lib/models/ninfer/qwen3_8_27b_quasar_nvfp4.ninfer`
(old MTP-only file kept beside it as `dflash2-src/qwen3_8_27b_quasar_nvfp4.ninfer.v1-mtp-only`
until someone deletes it), `~/Documents/ninfer-quasar` is at `8debca3`, `scripts/local_gpu.py`
serves `--spec dflash2 --draft-tokens 7`, and the server on :8090 runs that exact argv.
`docs/local_dev.md`, `docs/models.md`, `docs/experiments.md` updated in the same change.

## Outcome

Single run passed the ≥1.3× bar on every long call and missed it only on the 413-token-prompt
gameplay call (1.27×). Adoption is three edits, all needing signoff: the v2 artifact replaces
`/var/lib/models/ninfer/qwen3_8_27b_quasar_nvfp4.ninfer` under the same model id;
`~/Documents/ninfer-quasar` moves to `8debca3` (or `ninfer-quasar` becomes the new worktree);
`scripts/local_gpu.py` serves `--spec dflash2 --draft-tokens 7` instead of `--spec mtp
--draft-tokens 3` (or the spec line moves into `llm.ninfer_args` so settings own it, as they own
the KV dtype). Prod is untouched: Flash-Next on SGLang has no DFlash2 companion.
