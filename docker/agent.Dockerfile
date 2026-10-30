# *** Seismic Unix 44R28 on Ubuntu 24.04 (python3 3.12), for the SU benchmarks.
# *** Pinned by digest: the tag is third-party and `latest` can change underneath.
FROM docker.io/cadu21/seismic-unix@sha256:8c1c9e9e8ff1f16be539c5cd5e36204fca0b12735d63f6748c165688ef9ce565

# Host UID/GID (exported by the Makefile) so files the agent writes on bind mounts
# belong to the host user, without needing root or capabilities at runtime.
ARG UID=1000
ARG GID=1000

# The Hermes installer brings its own pinned Python/Node; libatomic1 is required by
# that Node and would otherwise make the installer ask for sudo.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    bash \
    git \
    ca-certificates \
    tar \
    xz-utils \
    libatomic1 \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/agent
ENV PATH=/home/agent/.local/bin:$PATH
# Keep Claude Code's whole state (credentials + .claude.json) in one persisted dir.
# It is also the default credentials path, which Hermes reads to borrow the login.
ENV CLAUDE_CONFIG_DIR=/home/agent/.claude
# The repo's .venv belongs to the host interpreter; the container keeps its own.
ENV UV_PROJECT_ENVIRONMENT=/home/agent/.venvs/pyseiskit

# -o: Ubuntu 24.04 already ships a user and group with id 1000.
RUN groupadd -o -g ${GID} agent_group && \
    useradd -o -u ${UID} -g ${GID} -d /home/agent -s /bin/bash agent_user && \
    mkdir -p /home/agent/.claude /home/agent/.venvs && \
    chown -R ${UID}:${GID} /home/agent

WORKDIR /workspace

# The installers must run as the user that will use them (they install under $HOME).
USER agent_user

# ~/.hermes mixes runtime (hermes-agent, installs, tools: ~2.4 GB, baked into the image)
# with user data, which compose persists.
RUN curl -fsSL --compressed https://hermes-agent.nousresearch.com/install.sh | \
    bash -s -- --non-interactive --skip-browser --skip-computer-use

# ~/.hermes is the agent-hermes-state volume, so Hermes' state.db is a real file inside its
# home (Hermes refuses a symlinked one). The installed tree moves to ~/.hermes-runtime and
# the entrypoint links the runtime dirs back into the volume. The empty ~/.hermes is the
# mount point, created here so the volume is user-owned.
RUN mv /home/agent/.hermes /home/agent/.hermes-runtime && mkdir /home/agent/.hermes

# Claude Code: its account login (/login) persists in the agent-claude volume and Hermes
# borrows it.
RUN curl -fsSL --compressed https://claude.ai/install.sh | bash

# pyseiskit is a uv project (uv.lock).
RUN curl -LsSf https://github.com/astral-sh/uv/releases/download/0.13.6/uv-installer.sh | sh

RUN git config --global --add safe.directory /workspace

COPY docker/agent-entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
