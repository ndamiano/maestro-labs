#!/usr/bin/env bash
while kill -0 232061 2>/dev/null; do sleep 15; done
ARMS=skel REASONING=xhigh ./run_designs.sh
