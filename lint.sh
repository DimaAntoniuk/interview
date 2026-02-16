#!/bin/bash
set -e

echo "Checking code formatting with black..."
poetry run black --check src/

echo ""
echo "Checking import sorting with isort..."
poetry run isort --check-only src/

echo ""
echo "Checking code style with flake8..."
poetry run flake8 src/

echo ""
echo "All linting checks passed!"
