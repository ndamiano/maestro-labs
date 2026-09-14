"""Designs through the llm QUEUE (a RunPod pod serves them), not a local server.
Usage: design_queue.py <skel|team> <slug> [reasoning]  → designs/<slug>.<arm>.prod.md (+ parts in designs/team/)"""
import json, sys, time
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from db import jobs
from llm_clients.connector import get_connector
from llm_clients.message_builder import MessageBuilder

LAB = "/home/nick/Documents/ai-agent-test/labs/spec-skeleton"
arm, slug = sys.argv[1], sys.argv[2]
effort = sys.argv[3] if len(sys.argv) > 3 else "medium"
MAX_TOKENS = int(sys.argv[4]) if len(sys.argv) > 4 else 50000
ask = dict(json.load(open(f"{LAB}/asks.json")))[slug]


def call(prompt: str, tag: str) -> str:
    msgs = MessageBuilder("You design browser games.").add_user(prompt).build()
    payload, model = get_connector().build_llm_job(msgs, [], MAX_TOKENS, reasoning=effort)
    t0 = time.time()
    for attempt in range(12):
        jid = jobs.enqueue_job("llm", payload, model=model, metadata={"stage": "lab-design", "tag": tag})
        print(f"{tag}: job {jid} enqueued (attempt {attempt+1})", flush=True)
        while True:
            j = jobs.get_job(jid)
            if j["status"] in ("done", "failed"):
                break
            time.sleep(10)
        if j["status"] == "done":
            break
        print(f"{tag}: job {jid} failed after {time.time()-t0:.0f}s: {j.get('error')} — re-enqueueing", flush=True)
        if "no worker" not in str(j.get("error")):
            raise SystemExit(f"{tag}: FAILED: {j.get('error')}")
    else:
        raise SystemExit(f"{tag}: gave up after 12 reaper cycles (no pod ever claimed)")
    r = j["result"]; text = ((r.get("choices") or [{}])[0].get("message", {}) or {}).get("content") or ""
    json.dump(r, open(f"{LAB}/designs/team/{slug}.{tag}.prod.json", "w"))
    print(f"{tag}: {len(text)} chars {time.time()-t0:.0f}s usage={r.get('usage')} exec={j.get('exec_seconds')}", flush=True)
    return text


if arm == "skel":
    tmpl = open(f"{LAB}/variants/skel.txt").read()
    out = call(tmpl.replace("{request}", ask), "skel")
else:
    docs = {}
    for role in ("visual", "gameplay", "engineering"):
        tmpl = open(f"{LAB}/variants/team_{role}.txt").read()
        docs[role] = call(tmpl.replace("{request}", ask), role)
        open(f"{LAB}/designs/team/{slug}.{role}.prod.md", "w").write(docs[role])
    tmpl = open(f"{LAB}/variants/team_integrate.txt").read()
    out = call(tmpl.replace("{request}", ask).replace("{gameplay}", docs["gameplay"])
               .replace("{visual}", docs["visual"]).replace("{engineering}", docs["engineering"]), "integrate")
open(f"{LAB}/designs/{slug}.{arm}.prod.md", "w").write(out)
print(f"design written: designs/{slug}.{arm}.prod.md", flush=True)
