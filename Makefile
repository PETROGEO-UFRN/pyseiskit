# The container runs as the host user, so files the agent writes belong to it.
export UID := $(shell id -u)
export GID := $(shell id -g)

# Prefers podman when installed, falls back to docker.
CONTAINER_ENGINE := $(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker)

ifeq ($(CONTAINER_ENGINE),podman)
# Rootless podman maps container UIDs to host subuids; keep-id maps the host user 1:1.
export USERNS_MODE := keep-id
# podman-compose (>= 1.1) applies keep-id natively; its default pod conflicts with it.
export PODMAN_COMPOSE_PROVIDER := podman-compose
COMPOSE_FLAGS := --in-pod false
endif

COMPOSE = $(CONTAINER_ENGINE) compose $(COMPOSE_FLAGS)

.PHONY: agent

agent:
	@test -f .secrets/agent.env || { echo "Missing .secrets/agent.env, see docs/agentContainer.md"; exit 1; }
	# Build (cached, so cheap when nothing changed) and start the agent detached
	$(COMPOSE) up -d --build agent
	# Attach to it. Detach without stopping it with "ctrl + P + Q".
	$(CONTAINER_ENGINE) attach pyseiskit-agent
