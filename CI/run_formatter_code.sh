#!/bin/bash

poetry run black --check --diff --exclude '.*\.ipynb$' .