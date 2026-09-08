"""request -> systems design by the local model -> a run whose PROMPT is that design.
usage: design.py "<request>" [--build]     (backend + local_gpu auto must be up)"""
import sys, time
from pathlib import Path
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from auth import store
from auth.billing import SECONDS_PER_CREDIT
from db import store as db_store
from llm_clients.connector import get_connector
from llm_clients.message_builder import MessageBuilder
from maestro.codegen import run as runmod
from maestro.state import RunState
from tools.execution_context import run_scope

LAB = Path(__file__).parent
request = sys.argv[1]
build = "--build" in sys.argv
run_id = runmod.create_run(store.list_users()[0].id)
db_store.charge_game(run_id, 0, SECONDS_PER_CREDIT)
prompt = (LAB / "design_prompt.txt").read_text().format(request=request)
t0 = time.time()
with run_scope(run_id):
    reply = get_connector().generate_with_tools(
        MessageBuilder("You design browser games.").add_user(prompt).build(), [], max_tokens=100000)
msg = (reply.get("choices") or [{}])[0].get("message", {}) or {}
text = (msg.get("content") or "").strip()
if not text: print("EMPTY REPLY:", str(reply)[:600]); sys.exit(1)
usage = reply.get("usage") or {}
print(f"run: {run_id}  design {len(text.split())} words  out={usage.get('completion_tokens')}tok  {time.time()-t0:.0f}s")
(LAB / f"design_{run_id}.txt").write_text(text)
runmod.set_prompt(run_id, text)
if build:
    print(runmod.run_build(run_id).__dict__)
