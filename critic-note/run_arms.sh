#!/usr/bin/env bash
cd /home/nick/Documents/ai-agent-test/src
L=/home/nick/Documents/Labs/critic-note
echo "A start $(date +%T)"
../venv/bin/python -m maestro.codegen.run --change 84cc8f73a252 "$(cat $L/review.txt)" > $L/arm_A.log 2>&1
echo "A done rc=$? $(date +%T)"
echo "B start $(date +%T)"
../venv/bin/python -m maestro.codegen.run --change 8f84ce1e07fc "$(cat $L/note_B.txt)" > $L/arm_B.log 2>&1
echo "B done rc=$? $(date +%T)"
