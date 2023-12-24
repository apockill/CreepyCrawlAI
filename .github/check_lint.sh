#!/bin/bash
set -euxo pipefail

poetry run cruft check
poetry run mypy --ignore-missing-imports crawlai/ tests/
poetry run isort --check --diff crawlai/ tests/
poetry run black --check crawlai/ tests/
poetry run flake8 crawlai/ tests/ --darglint-ignore-regex '^test_.*'
poetry run bandit -r --severity medium high crawlai/ tests/
poetry run vulture --min-confidence 100 crawlai/ tests/
echo "Lint successful!"