# Author: SangJeong Kim
# Last Modified: 2026-07-29

FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-lc"]

# INSTALL SYSTEM AND DEVELOPMENT DEPENDENCIES
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    fonts-dejavu-core \
    fonts-liberation2 \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-noto-core \
    ghostscript \
    git \
    graphviz \
    libheif-examples \
    libreoffice \
    poppler-utils \
    python3 \
    python3-pip \
    python3-venv \
    sudo \
    zsh \
    && rm -rf /var/lib/apt/lists/*

# LOAD SCRIPT
ARG SCRIPT_PATH=/tmp/scripts
COPY sjsh ${SCRIPT_PATH}
RUN find "${SCRIPT_PATH}" -name "*.sh" -exec chmod +x {} +

# SET AGENT TOOLS
ARG CODEX_OFFICE_VENV=/opt/codex-office
RUN "${SCRIPT_PATH}/root/install_codex_office_python.sh" "${CODEX_OFFICE_VENV}"
ENV CODEX_OFFICE_PYTHON="${CODEX_OFFICE_VENV}/bin/python"

# ADD USER AND SETUP ZSH
ARG CONTAINER_USER
ARG CONTAINER_UID
ARG CONTAINER_HOME
RUN "${SCRIPT_PATH}/root/add_user_and_setup_sudo.sh" "${CONTAINER_USER}" "${CONTAINER_UID}"
RUN "${SCRIPT_PATH}/root/setup_zsh_for_user.sh" "${CONTAINER_USER}"

# CLEANUP
RUN rm -rf /tmp/* || true
ENV DEBIAN_FRONTEND=dialog

# SWITCH USER
USER ${CONTAINER_USER}

# INSTALL UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="${CONTAINER_HOME}/.local/bin:${PATH}"

SHELL ["/bin/zsh", "-lc"]
