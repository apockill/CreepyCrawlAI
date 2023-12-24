#!/bin/bash
set -euxo pipefail

poetry run isort crawlai/ tests/
poetry run black crawlai/ tests/
