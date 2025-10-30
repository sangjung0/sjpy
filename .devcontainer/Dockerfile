FROM nvidia/cuda:12.8.1-cudnn-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-lc"]

ARG PYTHON_VERSION=3.10

# INSTALL DEPENDENCIES
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    git \
    sudo \
    zsh \
    curl \
    python${PYTHON_VERSION} \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# LOAD SCRIPT
COPY .devcontainer/sjsh /tmp/scripts
RUN chmod -R +x /tmp/scripts/*.sh

# ADD USER AND SETUP ZSH
ARG CONTAINER_USER
ARG CONTAINER_UID
ARG CONTAINER_HOME
RUN /tmp/scripts/add_user_and_setup_sudo.sh ${CONTAINER_USER} ${CONTAINER_UID}
RUN /tmp/scripts/setup_zsh.sh ${CONTAINER_USER} ${CONTAINER_UID} ${CONTAINER_HOME}

# Install UV
RUN sudo -u ${CONTAINER_USER} curl -LsSf https://astral.sh/uv/install.sh | sudo -u ${CONTAINER_USER} sh
RUN sudo -u ${CONTAINER_USER} -H env PATH="${CONTAINER_HOME}/.local/bin:$PATH"

## PREPARE UV ENV
ARG CONTAINER_WORK_DIR
WORKDIR ${CONTAINER_WORK_DIR}
COPY pyproject.toml uv.lock ${CONTAINER_WORK_DIR}/
RUN install -d -o ${CONTAINER_UID} -g ${CONTAINER_UID} ${CONTAINER_WORK_DIR}/.venv ${CONTAINER_HOME}

## SYNC UV
ARG CONTAINER_UV_GROUP
RUN chown -R ${CONTAINER_UID}:${CONTAINER_UID} ${CONTAINER_WORK_DIR} ${CONTAINER_HOME}
RUN sudo -u ${CONTAINER_USER} -H bash -lc "/tmp/scripts/sync_uv.sh ${CONTAINER_WORK_DIR} ${CONTAINER_HOME} ${CONTAINER_UV_GROUP}"

## CLEANUP
RUN rm -f ${CONTAINER_WORK_DIR}/pyproject.toml ${CONTAINER_WORK_DIR}/uv.lock /tmp/* || true

# FINALIZE
USER ${CONTAINER_USER}
ENV VIRTUAL_ENV="${CONTAINER_WORK_DIR}/.venv"
ENV PATH="${CONTAINER_WORK_DIR}/.venv/bin:${PATH}"
