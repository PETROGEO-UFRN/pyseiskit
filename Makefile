# The container runs as the host user, so files the agent writes belong to it.
export UID := $(shell id -u)
export GID := $(shell id -g)

# Benchmark datasets folder on the host, mounted read-only at /data.
# Override with `make agent PYSEISKIT_DATA_DIR=/path/to/data`.
export PYSEISKIT_DATA_DIR := $(or $(PYSEISKIT_DATA_DIR),$(HOME)/seismicData)

# Prefers podman when installed, falls back to docker (`make agent CONTAINER_ENGINE=docker`).
CONTAINER_ENGINE := $(or $(CONTAINER_ENGINE),$(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker))

ifeq ($(CONTAINER_ENGINE),podman)
# Rootless podman maps container UIDs to host subuids; keep-id maps the host user 1:1.
export USERNS_MODE := $(or $(USERNS_MODE),keep-id)
# podman-compose (>= 1.1) applies keep-id natively; its default pod conflicts with it.
export PODMAN_COMPOSE_PROVIDER := $(or $(PODMAN_COMPOSE_PROVIDER),podman-compose)
COMPOSE_FLAGS := --in-pod false
endif

COMPOSE = $(CONTAINER_ENGINE) compose $(COMPOSE_FLAGS)

.PHONY: agent

agent:
	@test -d "$(PYSEISKIT_DATA_DIR)" || { echo "Benchmark data folder $(PYSEISKIT_DATA_DIR) not found."; exit 1; }
	@test -f .secrets/agent.env || { echo "Missing .secrets/agent.env, see docs/agentContainer.md"; exit 1; }
	# Build (cached, so cheap when nothing changed) and start the agent detached
	$(COMPOSE) up -d --build agent
	# Attach to it. Detach without stopping it with "ctrl + P + Q",
	# which keeps it alive after disconnecting from a remote session.
	$(CONTAINER_ENGINE) attach pyseiskit-agent
