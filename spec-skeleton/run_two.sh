#!/usr/bin/env bash
# Serial builds of the two remaining designs. Needs the control plane and local_gpu auto up.
cd "$(dirname "$0")"
for a in collector forest; do
  STEPS=200 ./build.sh designs/$a.skel.xhigh.md "$a — skel xhigh (spec-skeleton)" > logs/build.$a.skel.xhigh.log 2>&1
done
echo ALLDONE >> logs/build.forest.skel.xhigh.log
