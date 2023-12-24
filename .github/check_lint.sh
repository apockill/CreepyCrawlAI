#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports creepycrawlai/ tests/
poetry run isort --check --diff creepycrawlai/ tests/
poetry run black --check creepycrawlai/ tests/
poetry run flake8 creepycrawlai/ tests/ --darglint-ignore-regex '^test_.*'
poetry run bandit -r --severity medium high creepycrawlai/ tests/
poetry run vulture --min-confidence 100 creepycrawlai/ tests/
echo "Lint successful!"