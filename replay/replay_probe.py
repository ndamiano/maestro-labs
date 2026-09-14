import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path
from lib.replay import replay
import sys

SRC = Path(sys.argv[1]); TGT = Path(sys.argv[2]); POS = int(sys.argv[3])
r = replay.run_to_position(SRC, POS, TGT)
f = r.fidelity
print(f"replayed turns : {len(r.turns)}")
print(f"fidelity       : {'unknown (no turn could disagree)' if f is None else format(f, '.0%')}")
print(f"turns w/ error : {len(r.errors)}")
print(f"diverged       : {len(r.diverged)}")
for t in r.errors[:3]: print(f"  error turn {t.turn}: {t.error}")
for t in r.diverged[:3]:
    print(f"  diverged turn {t.turn}:\n    replayed: {t.replayed[:160]}\n    recorded: {t.recorded[:160]}")
