#!/usr/bin/env bash
set -euo pipefail

# Demo: run health, then a tiny pipeline with a sample config

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
cd "$ROOT"

# 1) Health
python -m src.cli health | jq . || python -m src.cli health

# 2) Create a temp feeds.yaml pointing to an example RSS
TMP_CFG="$(mktemp -t feeds.XXXX).yaml"
cat > "$TMP_CFG" <<'YAML'
version: 1
defaults:
  max_parallel_fetches: 3
  timeout: 10
sources:
  - name: Example
    type: rss
    url: https://www.espn.com/espn/rss/nfl/news
    publisher: ESPN
    nfl_only: true
    enabled: true
YAML

# 3) Run pipeline
python -m src.cli pipeline --config "$TMP_CFG"

echo
echo "Demo complete."
