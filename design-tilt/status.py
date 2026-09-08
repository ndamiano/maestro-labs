import json,sys,collections
sys.path.insert(0,"/app/src")
from db import store
ids=json.load(open("/tmp/design-tilt/ids.json"))
c=collections.Counter((store.get_job(e["id"]) or {}).get("status") for e in ids)
print(" ".join(f"{k}={v}" for k,v in sorted(c.items())))
