#!/bin/bash
# Script to run black, lint, and demo (flask equivalent)

set -e

echo "=== Running Black (format) ==="
make format

echo "=== Running Lint ==="
make lint

echo "=== Running Demo (flask equivalent) ==="
bash scripts/demo.sh

echo "All done!"
