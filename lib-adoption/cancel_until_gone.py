"""Cancel a build's next turn the moment it is pending — the turn in flight cannot be taken back,
so this waits for the chain to enqueue the next one and refuses it there."""
import sys
import time
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from db.store import _db, cancel_pending_build_turn

game = sys.argv[1]
deadline = time.time() + 900
while time.time() < deadline:
    with _db() as c:
        row = c.execute("select id, status from builds where game_id = ? and status = 'running'",
                        (game,)).fetchone()
    if row is None:
        print("build is no longer running")
        break
    if cancel_pending_build_turn(row["id"], "lab: cancelled — the control arm is live data"):
        print("cancelled the pending turn of", row["id"])
        break
    time.sleep(3)
