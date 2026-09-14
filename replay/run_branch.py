import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pathlib import Path

from lib.replay import branch, direct

direct.install()

src = Path(sys.argv[1])
position = int(sys.argv[2])
turns = int(sys.argv[3])
arm = sys.argv[4] if len(sys.argv) > 4 else "dsh"
build = sys.argv[5] if len(sys.argv) > 5 else None
reasoning = sys.argv[6] if len(sys.argv) > 6 else "medium"

install = restore = None
if arm.startswith("dsh"):
    import arms_dsh
    install, restore = arms_dsh.install, arms_dsh.restore

out = branch.run(src, position, turns, install=install, restore=restore, arm=arm, build=build,
                 reasoning=reasoning)
print(out.report(), flush=True)
