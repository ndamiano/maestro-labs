#!/usr/bin/env bash
# Engineering p2 with each ask's p2 gameplay.md and with-gameplay visual.md, all five asks, after
# the visual pass finishes. 27B xhigh.
cd "$(dirname "$0")"
while [ ! -f visual_4.done ]; do sleep 30; done
python3 - <<'PY'
from pathlib import Path
t = Path("variants/team_engineering_p2_gv.txt").read_text()
for s in ("collector", "island", "station", "forest", "platformer"):
    gp = Path(f"designs/{s}.team_gameplay_p2.xhigh.md").read_text()
    vis = Path(f"designs/{s}.team_visual_p2_gp.{s}.xhigh.md").read_text()
    Path(f"variants/team_engineering_p2_gv.{s}.txt").write_text(t.replace("{gameplay}", gp).replace("{visual}", vis))
PY
for s in collector island station forest platformer; do ARM=team_engineering_p2_gv.$s REASONING=xhigh SLUGS=$s ./design.sh; done
echo done > eng_5.done
