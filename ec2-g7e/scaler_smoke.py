"""Queue one small llm job on the local control plane and watch its autoscaler serve it: the
worker row the scaler writes, the registration, the answer, and the row's termination.

Run from the repo root with run.py up and the aws scaler enabled:
venv/bin/python labs/ec2-g7e/scaler_smoke.py
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from db import jobs  # noqa: E402
from db.connection import platform_db  # noqa: E402
from llm_clients.connector import LLMConnector  # noqa: E402

T0 = time.time()


def say(msg: str) -> None:
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


def main() -> int:
    payload, model = LLMConnector(model="pennyroyal", max_tokens=64).build_llm_job(
        [{"role": "user", "content": "Reply with the single word: summoned"}], [])
    job_id = jobs.enqueue_job("llm", payload, model=model)
    say(f"queued job {job_id}")
    seen, status = {}, "pending"
    while time.time() - T0 < 1500:
        time.sleep(5)
        with platform_db() as conn:
            rows = [dict(r) for r in conn.execute(
                "SELECT id, source, pod_id, gpu_type, usd_per_hour, registered_at, terminated_at "
                "FROM workers WHERE started_at >= ? AND source != 'local'", (T0,))]
            refusals = conn.execute("SELECT COUNT(*) FROM pod_refusals WHERE created_at >= ?",
                                    (T0,)).fetchone()[0]
        for r in rows:
            state = ("terminated" if r["terminated_at"] else
                     "registered" if r["registered_at"] else "created")
            if seen.get(r["id"]) != state:
                seen[r["id"]] = state
                say(f"worker {r['id'][:8]} {state}: {r['source']} {r['pod_id']} "
                    f"{r['gpu_type']} ${r['usd_per_hour']}/hr")
        if seen.get("refusals") != refusals:
            seen["refusals"] = refusals
            say(f"full-ladder refusals so far: {refusals}")
        job = jobs.get_job(job_id)
        if job["status"] != status:
            status = job["status"]
            say(f"job {status}: {str(job.get('result') or job.get('error'))[:200]}")
        if status not in ("pending", "claimed") and rows and \
                all(r["terminated_at"] for r in rows):
            return 0 if status == "done" else 1
        if not rows and not refusals and time.time() - T0 > 90:
            jobs.abandon_job(job_id, "scaler never acted")
            say("no worker row and no refusal in 90 s: the scaler is not running")
            return 1
    say("timed out")
    return 1


if __name__ == "__main__":
    sys.exit(main())
