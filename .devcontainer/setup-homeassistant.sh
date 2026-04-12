#!/usr/bin/env bash

set -euo pipefail

mkdir -p .homeassistant
ln -sfn ../custom_components .homeassistant/custom_components
