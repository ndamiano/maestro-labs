"""Launch one llm box on EC2 from the local control plane through scaler.ec2_client, queue one
small job for it, and watch it register, answer and end itself.

Run from the repo root: venv/bin/python labs/ec2-g7e/cp_launch.py [--on-demand]
"""

import configparser
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from config.settings_manager import settings_manager  # noqa: E402
from db import jobs, workers  # noqa: E402
from db.connection import platform_db  # noqa: E402
from llm_clients.connector import LLMConnector  # noqa: E402
from scaler.ec2_client import Ec2Client, Ec2Error  # noqa: E402

CP_URL = "https://nick-ms-7e70.taild62b23.ts.net"
AMIS = {"eu-north-1": "ami-0116c8c4637c00e43", "us-west-2": "ami-0fe3c370e158967ca"}
INSTANCE_TYPE = "g7e.2xlarge"
MODEL = "pennyroyal"
NAME_PREFIX = "gs-llm-"
T0 = time.time()


def say(msg: str) -> None:
    print(f"[{time.time() - T0:6.0f}s] {msg}", flush=True)


def main() -> int:
    markets = ["spot", "on-demand"] if "--on-demand" in sys.argv else ["spot"]
    creds = configparser.ConfigParser()
    creds.read(Path.home() / ".aws" / "credentials")
    client = Ec2Client(creds["default"]["aws_access_key_id"],
                       creds["default"]["aws_secret_access_key"])
    settings = settings_manager.get_settings()

    running = client.list_instances(AMIS, NAME_PREFIX)
    if running:
        say(f"already running, not launching: {running}")
        return 1

    offers = client.offers(AMIS, [INSTANCE_TYPE], markets)
    for o in offers:
        say(f"offer {o.zone} {o.market} ${o.usd_per_hour:.4f}/hr")

    worker_id = uuid.uuid4().hex
    env = {
        "CP_URL": CP_URL,
        "WORKER_TOKEN": settings["workqueue"]["token"],
        "WORKER_QUEUE": "llm",
        "WORKER_ID": worker_id,
        "WORKER_SOURCE": "aws",
        "WORKER_SLOTS": "1",
        "IDLE_EXIT_SECONDS": "60",
        "JOB_TIMEOUT_SECONDS": "1800",
        "LLM_MODEL": MODEL,
        "LLM_N_CTX": str(settings["llm"]["n_ctx"]),
        "SGLANG_ARGS_EXTRA": "",
    }

    launched = None
    for offer in offers:
        try:
            instance_id = client.launch(offer, f"{NAME_PREFIX}{worker_id[:8]}", AMIS[offer.region],
                                        env, "gs-gpu-worker", "gs-gpu-worker")
        except Ec2Error as e:
            say(f"{offer.zone} {offer.market} refused: {e}")
            if not e.stock:
                break
            continue
        launched = (offer, instance_id)
        break
    if not launched:
        say("nothing launched")
        return 2

    offer, instance_id = launched
    workers.worker_created(worker_id, f"{offer.region}/{instance_id}", "llm",
                           offer.instance_type, offer.usd_per_hour)
    say(f"launched {instance_id} in {offer.zone} ({offer.market} ${offer.usd_per_hour:.4f}/hr), "
        f"worker {worker_id}")

    payload, model = LLMConnector(model=MODEL, max_tokens=64).build_llm_job(
        [{"role": "user", "content": "Reply with the single word: summoned"}], [])
    job_id = jobs.enqueue_job("llm", payload, model=model)
    say(f"queued job {job_id}")

    registered = False
    status = "pending"
    while time.time() - T0 < 1200:
        time.sleep(10)
        if not registered:
            with platform_db() as conn:
                row = conn.execute("SELECT registered_at FROM workers WHERE id = ?",
                                   (worker_id,)).fetchone()
            if row["registered_at"]:
                registered = True
                say("worker registered")
        job = jobs.get_job(job_id)
        if job["status"] != status:
            status = job["status"]
            say(f"job {status}: {str(job.get('result') or job.get('error'))[:300]}")
        if status not in ("pending", "claimed") or \
                (not registered and not client.list_instances([offer.region], NAME_PREFIX)):
            break

    while time.time() - T0 < 1500:
        if not client.list_instances([offer.region], NAME_PREFIX):
            say("instance gone")
            return 0 if status == "done" else 1
        time.sleep(10)
    say(f"instance {instance_id} still up; terminating")
    client.terminate(offer.region, instance_id)
    return 1


if __name__ == "__main__":
    sys.exit(main())
