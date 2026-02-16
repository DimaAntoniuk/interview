#!/bin/bash
set -e

echo "Running type checks with mypy..."
poetry run mypy src/

echo ""
echo "Type checks passed!"
