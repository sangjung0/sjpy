#!/usr/bin/env bash

# Author: SangJeong Kim
# Last Modified: 2026-07-29

set -euo pipefail

CONTAINER_WORK_DIR="${1:?Usage: $0 <CONTAINER_WORK_DIR>}"

if [[ ! -d "${CONTAINER_WORK_DIR}/.devcontainer/sjsh" ]]; then
    git clone --branch v0.0.7 https://github.com/sangjung0/sjsh.git \
        "${CONTAINER_WORK_DIR}/.devcontainer/sjsh"
fi
