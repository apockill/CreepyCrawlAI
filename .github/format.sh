#!/bin/bash
set -euxo pipefail

poetry run isort creepycrawlai/ tests/
poetry run black creepycrawlai/ tests/
