# ADR-001: Use UV as Python Package Manager

## Status

Accepted

## Context

The project needs a modern Python package manager that provides fast dependency resolution, environment management, and reproducible builds. Historically, the project used `pip` with `requirements.txt` and `requirements-dev.txt`.

## Decision

Adopt [UV](https://docs.astral.sh/uv/) as the primary package manager. The `pyproject.toml` is the single source of truth for all dependencies, organized into optional dependency groups:

- `dev` — Development tooling (ruff, mypy, pytest, pre-commit)
- `llm` — LLM-specific dependencies (httpx, json_repair)
- `audio` — Audio processing (librosa, numpy, matplotlib, soundfile)
- `test` — Test dependencies (pytest, pytest-cov)

## Consequences

- Faster dependency resolution and installation compared to pip
- Single `pyproject.toml` file replaces `requirements.txt` and `requirements-dev.txt`
- Dependency groups allow lightweight installs in different environments
- CI/CD can use `uv sync --no-dev` for production builds
- Developers need to install UV globally (`pip install uv`)
