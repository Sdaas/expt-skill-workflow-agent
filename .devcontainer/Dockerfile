# Base image: Microsoft's Debian-based devcontainer image with Python 3.12
# preinstalled. It already includes git, curl, common build tools, and a
# non-root "vscode" user set up for development. Python is what the real
# /implement-feature product generates and tests.
FROM mcr.microsoft.com/devcontainers/python:3.12

# A few shell niceties (git/curl are already in the base image).
RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        bash-completion \
        jq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package manager) into the non-root user's environment.
# The official installer places it in ~/.local/bin. We'll use it for the real
# product's venv + test deps (pytest, mutation testing) later.
USER vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

# Default working directory. VS Code / the devcontainer CLI mount the repo under
# /workspaces/<repo>; setting this keeps sessions sensible.
WORKDIR /workspaces

# NOTE: Node.js + the Claude Code CLI are installed via devcontainer *features*
# (see devcontainer.json), NOT hand-installed here — features survive rebuilds
# and avoid the "node present but npm missing" build failure.
