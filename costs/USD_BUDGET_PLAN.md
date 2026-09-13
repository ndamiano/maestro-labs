# Plan: game budgets in USD, priced by the pod's own rate

Status: planned 2026-09-10, not started. Do it after the admin.py cleanup lands.

## Why

Today a game's budget is counted in 5090-seconds. A debit is `exec_seconds × gpu_rate(card)`,
where `gpu_rate` comes from a hand-kept table in settings (`billing.gpu_rates` ×
`usd_per_5090_hour`). Every worker row already carries RunPod's real `costPerHr`
(`workers.usd_per_hour`, stamped at pod create, and backfilled 2026-09-10). Two prices for one
thing: the table matches today only by hand-upkeep — a price change or a secure/community
split goes stale silently — and an unlisted card debits at the 5090's rate.

After: a budget is dollars; a job costs `exec_seconds / 3600 × COALESCE(worker.usd_per_hour, 0.99)`.
One price source, the table is deleted.

**Unit: integer micros (millionths of a dollar), rounded UP per job.** Named what-then-unit,
like `exec_seconds`; USD is the only currency so no `usd` in names — the store's docstring says
"micros = millionths of a dollar" once. Example: $2.21/h × 47 s = $0.0288528 → 28,853.

Users see nothing change — they see credits and a budget percentage, never seconds.

## Decisions (made)

- **Missing rate → flat $0.99/hr.** Should not happen on RunPod (create stamps it; the scaler tick
  fills it within 15 s, long before a boot finishes; 40/40 workers since 2026-09-07 priced). It
  also covers home-box workers, which are ignored as a hack — no special path for them.
  The 0.99 is a constant in code, not a setting.
- **Reservation at enqueue → $0.99/hr × `QUEUE_SECONDS[queue]`.** The card is unknown at enqueue;
  the reservation bounds overdraw, it is not a charge. A 6000 job overdraws ~2.2× its
  reservation until its real debit lands — same shape as today.
- **One credit = 3,000,000 micros ($3.00)** — up from $2.97 (10,800 5090-s), a slight bump for
  customers. Existing grants convert at the old rate (2,970,000) — no retro top-up.
- **Rounding:** per job, `ceil`. Worst case +$0.000001 per job.

## Code changes

1. `src/auth/billing.py` — `SECONDS_PER_CREDIT = 10_800` → `MICROS_PER_CREDIT = 3_000_000`.
   Call sites: `api/routers/games.py:149, :338`, `maestro/codegen/run.py:140`.
2. `src/db/estimates.py` — keep `QUEUE_SECONDS` / `estimate_seconds` (the autoscaler sizes the
   fleet in seconds, `autoscaler.py:103`). Add the fallback rate constant and
   `reserve_micros(queue)` = `ceil(QUEUE_SECONDS × 990_000 / 3600)` (llm 15 s → 4,125);
   `cheapest_seconds()` → `cheapest_micros()` (`games.py:85`). Delete
   `gpu_rate`, `_unrated`, and the module docstring's 5090-seconds paragraph.
3. `src/db/store.py`
   - Schema: `games.seconds_granted/seconds_used` → `granted_micros/spent_micros`;
     `builds.seconds_used` → `spent_micros`; `jobs.billed_seconds` → `billed_micros`;
     `jobs.est_seconds` → `reserved_micros`. All INTEGER.
   - `charge_game(game_id, credits, micros)`.
   - `_remaining_locked` / `compute_remaining` return micros; `_insert_job_locked` reserves
     `reserve_micros(queue)`; `InsufficientCompute` carries micros.
   - `complete_job` (~:607): read the claiming worker's `usd_per_hour` inside the same
     transaction (`jobs.worker_id = workers.id`), `rate_micros = round(usd_per_hour × 10⁶)` (round, not ceil — float
     noise on 2.21×10⁶), `billed = ceil(exec_seconds × rate_micros / 3600)`. Rewrite
     the docstring's debit paragraph.
   - `exec_seconds_by_gpu` / `games_exec_seconds_by_gpu`: return per-card seconds AND micros,
     the micros summed per job from the worker's rate, same formula as the debit. Admin stops pricing anything.
4. `src/api/routers/admin.py` — delete `_usd_per_hour`, `_worked_usd`, the `gpu_rate` import;
   `_workers` reads `w["usd_per_hour"]` directly; `_window` takes micros from the store and shows dollars.
5. `src/api/routers/games.py` — `_budget_pct` over the renamed columns (a ratio, unit-free).
6. `src/config/settings_manager.py` + `settings.example.json` — delete the `billing` block
   (`usd_per_5090_hour`, `gpu_rates`). If nothing else is in it, the whole block goes.

grep to confirm nothing left: `_e4|gpu_rate|usd_per_5090|SECONDS_PER_CREDIT|seconds_granted|seconds_used|billed_seconds|est_seconds|cheapest_seconds`
(note admin's `ghost_30d.billed_seconds` is RunPod's billed wall-clock — unrelated, keep).

## Tests

Update: `test_compute_budget.py`, `test_job_metering.py`, `test_credits.py`,
`test_games_db_wiring.py`, `test_admin_api.py`, `test_admin_store.py`.
New contracts to assert:
- $2.21/h × 47 s debits exactly 28,853; $0.99/h × 1 s debits exactly 275;
- a job on a $2.19 worker debits ~2.2× a $0.99 worker for the same exec_seconds;
- a worker with NULL rate debits at 0.99;
- a failed job debits nothing (unchanged, re-assert under the new column);
- reservation = `reserve_micros(queue)`, and admission refuses below `cheapest_micros()`;
- admin per-game cost equals the sum of per-job debits.

## Docs (same commit)

- `docs/deploy.md` — the ALTER block below.
- `docs/architecture.md`, `docs/build_path.md`, `docs/local_dev.md`: any "5090-seconds" /
  `gpu_rates` mention → dollars. grep `5090-second|gpu_rates` across docs.

## Prod migration (on the box, before the deploy)

DB is `/data/platform.db` per docs/deploy.md. Take `.backup` first. SQLite ≥ 3.25 for RENAME.

```sql
-- 5090-seconds → micros: × 0.99 / 3600 × 10^6 = × 275 exactly; ceil only bites on fractional seconds
BEGIN;
ALTER TABLE games RENAME COLUMN seconds_granted TO granted_micros;
ALTER TABLE games RENAME COLUMN seconds_used    TO spent_micros;
UPDATE games SET granted_micros = CAST(round(granted_micros * 275) AS INTEGER),
                 spent_micros   = CAST(ceil(spent_micros * 275) AS INTEGER);
ALTER TABLE builds RENAME COLUMN seconds_used TO spent_micros;
UPDATE builds SET spent_micros = CAST(ceil(spent_micros * 275) AS INTEGER);
ALTER TABLE jobs RENAME COLUMN billed_seconds TO billed_micros;
UPDATE jobs SET billed_micros = CAST(ceil(billed_micros * 275) AS INTEGER) WHERE billed_micros IS NOT NULL;
ALTER TABLE jobs RENAME COLUMN est_seconds TO reserved_micros;
UPDATE jobs SET reserved_micros = CAST(ceil(reserved_micros * 275) AS INTEGER);
COMMIT;
```
`ceil()` needs SQLite ≥ 3.35 built with math functions — check `SELECT ceil(1.1)` on the box;
if missing, run the same through python's sqlite3 with `math.ceil`. Column affinity stays REAL
after a rename; values are whole numbers and the code reads them as int. A fresh DB gets
INTEGER from the new CREATE TABLE.

Converting history at the flat 0.99 keeps every game's remaining budget where it is, to the unit
(old billing was 5090-seconds, so × $0.99/h is the same money). Re-pricing past jobs by actual
worker rate would move balances — not wanted.

Then remove the `billing` block from prod `settings.json` and `compose restart app`.
Deploy order: stop app → backup → SQL → deploy code → settings edit → restart.
Run with no builds in flight so no job completes between SQL and new code.
