"""Stop the builds in flight. The lab owns the card while it runs, and a build nobody is
measuring is card time spent on nothing."""
import sys
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from db.store import _db, cancel_pending_build_turn

with _db() as c:
    rows = [dict(r) for r in c.execute(
        "select id, game_id, kind, status from builds where status in ('running','queued')")]
for r in rows:
    print(r["id"], r["game_id"], r["kind"], "->", cancel_pending_build_turn(r["id"], "lab: cancelled"))
print(len(rows), "builds")
