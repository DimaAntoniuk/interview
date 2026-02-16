#!/bin/bash
set -e

echo "Fixing code formatting with black..."
poetry run black src/

echo ""
echo "Fixing import sorting with isort..."
poetry run isort src/

echo ""
echo "Code formatting fixed!"
