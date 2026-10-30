# Agent container

A Hermes agent (Claude) in a rootless, capability-free container, for developing pyseiskit,
running benchmarks against Seismic Unix and documenting them. Start it with `make agent`.

## What it can change

| Path | Access | Why |
| --- | --- | --- |
| repo root (`pyseiskit/`, `demos/`, `docs/`, `benchmark/`, new folders) | read-write | the work itself |
| `.git` | read-only | it is the host's checkout; the agent opens PRs from its own clone in its Hermes volume |
| `.github/`, `pyproject.toml`, `uv.lock`, `README.md`, `LICENSE`, `.gitignore` | read-only | CI publishes to PyPI from them |
| `Makefile`, `compose.yml`, `docker/`, `.dockerignore`, `.agents/` | read-only | its own container and config |
| `.agents/hermes.yaml` | read-write | mounted as its Hermes config, so `hermes config set` works |
| `/data` | read-only | benchmark datasets from `PYSEISKIT_DATA_DIR` |

The container venv lives in its own volume (`UV_PROJECT_ENVIRONMENT`), so it never touches
a host `.venv`. Seismic Unix 44R28 is in the image (`CWPROOT=/opt/cwp/44R28`).

## Setup

1. Credentials, in `.secrets/` (gitignored, hidden inside the container):
   - `agent.env` with `GH_APP_ID=<GitHub App id>`;
   - the GitHub App private key (`*.private-key.pem`), mounted read-only at `/run/secrets`.
2. Benchmark datasets: a host folder, `$HOME/seismicData` by default
   (`make agent PYSEISKIT_DATA_DIR=/path/to/data` to change it).
3. `make agent`. On the first start, log in to Claude: `claude` -> `/login`, then
   `hermes chat --provider anthropic`.

The agent's repo skills live in `.agents/skills/` (`github-prs`: pushes and PRs as the
GitHub App).

Jupyter, when started inside the container on port 8888, is reachable at
`http://127.0.0.1:8888` on the host only.
