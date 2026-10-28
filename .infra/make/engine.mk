# Automatically export the host user's UID and GID so compose runs the container
# natively as the active user, avoiding root-owned permission issues on mapped volumes.
export UID := $(shell id -u)
export GID := $(shell id -g)

# Container engine: prefers podman when installed, falls back to docker.
# Force one with `make <target> CONTAINER_ENGINE=docker` (or set it in the env).
CONTAINER_ENGINE := $(or $(CONTAINER_ENGINE),$(shell command -v podman >/dev/null 2>&1 && echo podman || echo docker))

ifeq ($(CONTAINER_ENGINE),podman)
# Only rootless podman is supported: rootful podman maps the container user to root
# on the host, so files the agent writes would not belong to the host user.
PODMAN_ROOTLESS := $(shell podman info --format '{{.Host.Security.Rootless}}' 2>/dev/null)
ifneq ($(PODMAN_ROOTLESS),true)
$(error Podman must run rootless (got rootless='$(PODMAN_ROOTLESS)'). Run make as your user, without sudo)
endif
# Rootless podman maps container UIDs to host subuids, so `user: UID:GID` alone
# would leave bind-mounted files owned by an unrelated host UID. keep-id maps the
# host user 1:1 into the container, matching docker's behavior.
export USERNS_MODE := $(or $(USERNS_MODE),keep-id)
# `podman compose` delegates to an external provider. Pin podman-compose so the
# whole stack stays on podman (and keep-id is applied natively). Profiles need >= 1.1.
export PODMAN_COMPOSE_PROVIDER := $(or $(PODMAN_COMPOSE_PROVIDER),podman-compose)
ifeq ($(notdir $(PODMAN_COMPOSE_PROVIDER)),podman-compose)
PODMAN_COMPOSE_VERSION := $(shell $(PODMAN_COMPOSE_PROVIDER) version 2>/dev/null | sed -n 's/^podman-compose version //p')
ifneq ($(firstword $(shell printf '1.1.0\n%s\n' '$(PODMAN_COMPOSE_VERSION)' | sort -V)),1.1.0)
$(error podman-compose >= 1.1 required (found '$(PODMAN_COMPOSE_VERSION)'). Install it with: pipx install podman-compose)
endif
# podman-compose wraps services in a pod by default, which conflicts with per-container
# --userns (keep-id). Docker compose has no pods.
COMPOSE_FLAGS := --in-pod false
endif
endif

COMPOSE = $(CONTAINER_ENGINE) compose $(COMPOSE_FLAGS)
