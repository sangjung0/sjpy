FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-lc"]

# INSTALL DEPENDENCIES
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    git sudo zsh curl python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# LOAD SCRIPT
ARG SCRIPT_PATH=/tmp/scripts
COPY .devcontainer/sjsh ${SCRIPT_PATH}
RUN find "${SCRIPT_PATH}" -name "*.sh" -exec chmod +x {} +

# ADD USER AND SETUP ZSH
ARG CONTAINER_USER
ARG CONTAINER_UID
ARG CONTAINER_HOME
RUN ${SCRIPT_PATH}/root/add_user_and_setup_sudo.sh ${CONTAINER_USER} ${CONTAINER_UID}
RUN ${SCRIPT_PATH}/root/setup_zsh_for_user.sh ${CONTAINER_USER}

# CLEANUP
RUN rm -rf /tmp/* || true

# SWITCH USER
USER ${CONTAINER_USER}

# INSTALL UV
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="${CONTAINER_HOME}/.local/bin:$PATH"
