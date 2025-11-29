#!/usr/bin/env bash
set -euo pipefail

CONTAINER_WORK_DIR="${1:?Usage: $0 <CONTAINER_WORK_DIR>}"

if [[ ! -d "${CONTAINER_WORK_DIR}/.devcontainer/sjsh" ]]; then
    git clone --branch v0.0.4 https://github.com/sangjung0/sjsh.git \
        "${CONTAINER_WORK_DIR}/.devcontainer/sjsh"
fi
