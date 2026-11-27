#!/usr/bin/env bash
set -euo pipefail
PY="${PY:-/home/sam/flex/bin/python}"
cd /home/sam/em-llm
exec "$PY" -m em_llm.cli "$@"
