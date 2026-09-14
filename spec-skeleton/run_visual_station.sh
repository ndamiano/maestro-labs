#!/usr/bin/env bash
# Visual p2 on station without, then with, the p2 gameplay.md. 27B xhigh.
cd "$(dirname "$0")"
ARM=team_visual_p2 REASONING=xhigh SLUGS=station ./design.sh
ARM=team_visual_p2_gp.station REASONING=xhigh SLUGS=station ./design.sh
echo done > visual_station.done
