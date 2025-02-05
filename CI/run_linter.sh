#!/bin/bash

# When using flake8 we ignore:
# E501: Line too long: Too strict for us
# W503: Line break before binary operator: The advice is changing to the opposite here soon (W504), so no point. See: https://www.flake8rules.com/rules/W503.html.
# For tests we ignore:
# E402: Module level import not at top of file: It's a common pattern in tests to import modules after setting up the test environment.
poetry run flake8 --ignore=E501,W503 --per-file-ignores="tests/*:E402"