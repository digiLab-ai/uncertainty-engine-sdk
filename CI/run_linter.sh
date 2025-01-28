#!/bin/bash

# When using flake8 we ignore:
# E501: Line too long: Too strict for us
# W503: Line break before binary operator: The advice is changing to the opposite here soon (W504), so no point. See: https://www.flake8rules.com/rules/W503.html.
poetry run flake8 --ignore=E501,W503