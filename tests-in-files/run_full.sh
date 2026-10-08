#!/usr/bin/env bash
# The whole production path on one ask: design chain, then the build, `python -m maestro.codegen.run`.
# Usage: ./run_full.sh "<ask>" > logs/full.<slug>.log     (run id on the first line)
cd "$(dirname "$0")/../.."; source venv/bin/activate; cd src
exec python -m maestro.codegen.run "$1"
