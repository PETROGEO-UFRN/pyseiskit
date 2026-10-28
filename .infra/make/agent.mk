# Benchmark datasets folder on the host, mounted read-only at /data.
# Override with `make agent PYSEISKIT_DATA_DIR=/path/to/data`.
export PYSEISKIT_DATA_DIR := $(or $(PYSEISKIT_DATA_DIR),$(HOME)/seismicData)

.PHONY: agent check-agent

agent: check-agent
	# Build (cached, so cheap when nothing changed) and start the agent detached
	$(COMPOSE) --profile agent up -d --build agent
	# Attach to it. Detach without stopping it with "ctrl + P + Q",
	# which keeps it alive after disconnecting from a remote session.
	$(CONTAINER_ENGINE) attach pyseiskit-agent

# A missing bind-mount source would fail the mount, or be created empty and root-owned.
check-agent:
	@test -d "$(PYSEISKIT_DATA_DIR)" || { \
		echo "Benchmark data folder $(PYSEISKIT_DATA_DIR) not found."; \
		echo "Create it or run: make agent PYSEISKIT_DATA_DIR=/path/to/data"; \
		exit 1; }
	@test -f .infra/.secrets/agent.env || { \
		echo "Missing .infra/.secrets/agent.env (GH_APP_ID) and the GitHub App private key."; \
		echo "See docs/agentContainer.md"; \
		exit 1; }
