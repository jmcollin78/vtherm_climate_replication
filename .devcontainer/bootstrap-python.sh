#!/usr/bin/env bash

set -euo pipefail

bash .devcontainer/setup-homeassistant.sh

python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt