#!/usr/bin/env bash
# Visual p2 with each ask's p2 gameplay.md, the four asks after station. 27B xhigh.
cd "$(dirname "$0")"
for s in collector island forest platformer; do ARM=team_visual_p2_gp.$s REASONING=xhigh SLUGS=$s ./design.sh; done
echo done > visual_4.done
