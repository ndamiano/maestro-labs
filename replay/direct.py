"""Talk to the local engine directly, with the queue taken out of the middle.

`LLMConnector` enqueues an `llm` job and waits for a worker to claim it, which on this box means
the API server, a minted worker token and a worker process — three things a replay does not need
and one more thing that can be misconfigured between a measurement and its answer. The PAYLOAD is
the connector's own, and the translation to the engine's dialect is `worker.handlers.llm`'s own
(`wire.chat_body_for_wire`), so what the model receives is byte for byte what a real turn sends.
"""

from __future__ import annotations

import time

import requests

from llm_clients import connector as _connector
from llm_clients import wire


class DirectConnector(_connector.LLMConnector):
    def __init__(self, target: str = "http://127.0.0.1:8090", **kw):
        super().__init__(**kw)
        self.target = target

    def _run_job(self, payload: dict) -> dict:
        t0 = time.time()
        try:
            r = requests.post(f"{self.target}/v1/chat/completions",
                              json=wire.chat_body_for_wire(payload), timeout=1800)
        except requests.RequestException as e:
            return {"status": "failed", "error": str(e), "result": None}
        if r.status_code != 200:
            return {"status": "failed", "error": f"Status {r.status_code}: {r.text[:2000]}",
                    "result": None}
        return {"status": "done", "result": r.json(), "error": None,
                "elapsed": time.time() - t0}


def install(target: str = "http://127.0.0.1:8090") -> None:
    """Make `get_connector()` hand back the direct one for the rest of this process."""
    from config.settings_manager import settings_manager

    llm = settings_manager.get_settings().get("llm") or {}
    _connector._cached_connector = DirectConnector(
        target=target, model=llm.get("model", "default"),
        max_tokens=llm.get("max_tokens", 50000), reasoning=llm.get("reasoning"))
