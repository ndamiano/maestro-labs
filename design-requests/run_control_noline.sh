#!/usr/bin/env bash
# Control arm: build.txt WITHOUT the broad-strokes line for one build, restored after.
set -u
LAB=/home/nick/Documents/Labs/design-requests; REPO=/home/nick/Documents/ai-agent-test
slug=$1; src=$2; ARM=noline
cd $REPO && sed -i '/^- The first reply settles only the file layout/d' src/maestro/codegen/prompts/build.txt
grep -c "broad strokes" src/maestro/codegen/prompts/build.txt
$LAB/run_short_rebuild.sh "$slug" "$src" "$ARM"
cd $REPO && git checkout src/maestro/codegen/prompts/build.txt && echo "build.txt restored $(date)"
