# *** SU vs pyseiskit benchmarks: Seismic Unix and uv. The repo is mounted read-only and
# *** uv installs it, with the benchmarks group, into an environment under /tmp.
FROM docker.io/cadu21/seismic-unix@sha256:8c1c9e9e8ff1f16be539c5cd5e36204fca0b12735d63f6748c165688ef9ce565
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /usr/local/bin/uv
ENV UV_PROJECT_ENVIRONMENT=/tmp/venv UV_CACHE_DIR=/tmp/uv-cache
WORKDIR /workspace
ENTRYPOINT ["uv", "run", "--locked", "--no-dev", "--group", "benchmarks", "python", "-m", "benchmarks"]
