#!/usr/bin/env bash
# After the running collector split build: collector no-links + why-comments, then split design/
# builds for the other four asks. Sequential, one GPU.
cd "$(dirname "$0")"
while ! grep -q '^result:' split.log; do sleep 60; done
./build_split_why.sh designs/collector_nolinks collector "collector — team p2, no-links, why comments" > split_why.log 2>&1
for s in island station forest platformer; do
  ./build_split.sh designs/${s}_split $s "$s — team p2, layered prompt, split design/" > split_$s.log 2>&1
done
echo done > overnight.done
