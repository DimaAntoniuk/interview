#!/bin/bash
set -e

echo "Running tests with coverage..."
poetry run pytest -vv -n auto --cov=src --cov-report=term-missing --cov-report=html

echo ""
echo "Coverage report generated in htmlcov/index.html"
