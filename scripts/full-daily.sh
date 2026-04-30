#!/usr/bin/env bash
# 全日端到端：抓取→简报 HTML→article→MP3（见 tools/run_full_daily.py）
# cron 示例：0 5 * * * cd /path/to/DFOS && bash scripts/full-daily.sh >> logs/$(date +\%Y-\%m-\%d).log 2>&1
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"
exec python3 -m tools.run_full_daily "$@"
