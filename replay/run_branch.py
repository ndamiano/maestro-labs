import sys
from pathlib import Path

import branch
import direct

direct.install()

src = Path(sys.argv[1])
position = int(sys.argv[2])
turns = int(sys.argv[3])
arm = sys.argv[4] if len(sys.argv) > 4 else "dsh"
build = sys.argv[5] if len(sys.argv) > 5 else None
reasoning = sys.argv[6] if len(sys.argv) > 6 else "medium"

install = None
if arm.startswith("dsh"):
    import arms_dsh
    install = arms_dsh.install

out = branch.run(src, position, turns, install=install, arm=arm, build=build,
                 reasoning=reasoning)
print(out.report(), flush=True)
