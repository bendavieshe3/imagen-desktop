#!/bin/bash
# Script to install test dependencies and run tests

set -e

echo "=== Installing test dependencies ==="
pip install -r requirements.txt

echo "=== Running tests ==="
python -m pytest -k "not ui" "$@"

echo "=== Done ==="