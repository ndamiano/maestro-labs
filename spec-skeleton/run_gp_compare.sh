#!/usr/bin/env bash
# After the team_gameplay_p2 pass exits, run the old team_gameplay prompt on the asks that lack a
# local xhigh gameplay doc. Both at xhigh on the 27B.
cd "$(dirname "$0")"
while pgrep -fx 'bash ./design.sh' >/dev/null; do sleep 20; done
ARM=team_gameplay REASONING=xhigh SLUGS="island forest platformer" ./design.sh > logs/design.3asks.team_gameplay.xhigh.log 2>&1
echo done > gp_compare.done
