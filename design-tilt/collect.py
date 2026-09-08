import json,sys,re
sys.path.insert(0,"/app/src")
from db import store
ids=json.load(open(sys.argv[1])); out=[]
for e in ids:
    j=store.get_job(e["id"]) or {}
    txt=""
    if j.get("result"):
        txt=(((j["result"].get("choices") or [{}])[0].get("message") or {}).get("content") or "")
    first=txt.strip().split("\n")[0][:160]
    out.append({**e,"status":j.get("status"),"exec":j.get("exec_seconds"),"first":first,
        "dim":"3D" if re.search(r"\b3D\b",first) else ("2D" if re.search(r"\b2D\b",first) else "?"),
        "world":len(re.findall("compose_world",txt)),"chars":len(txt),"text":txt})
print(json.dumps(out))
