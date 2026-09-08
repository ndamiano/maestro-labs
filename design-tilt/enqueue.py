import json,sys,pathlib
sys.path.insert(0,"/app/src")
from db import store
from llm_clients.connector import get_connector
from llm_clients.message_builder import MessageBuilder
root=pathlib.Path(sys.argv[1]); asks=[a for a in (root/"asks.txt").read_text().splitlines() if a.strip()]
conn=get_connector(); ids=[]
for a_i,ask in enumerate(asks):
    for vp in sorted((root/"variants").glob("*.txt")):
        msgs=MessageBuilder("You design browser games.").add_user(vp.read_text().format(request=ask)).build()
        payload,model=conn.build_llm_job(msgs,[],100000)
        jid=store.enqueue_job("llm",payload,model=model,metadata={"lab":"design-tilt","variant":vp.stem,"ask":a_i})
        ids.append({"id":jid,"variant":vp.stem,"ask":a_i,"ask_text":ask})
print(json.dumps(ids))
