# Linting and Testing Standards

These standards define the checks expected before a pull request is marked ready. Run the sections for the
languages touched by the change.

## Required Gates

- Start from the default branch and keep the PR focused on one reviewable change.
- Run `git diff --check` before committing.
- Run `repowave scan .` when `repowave.toml` is present.
- Run every applicable language command below. If a command needs credentials, a live service, or unavailable
  platform tooling, state that in the PR and run the closest local gate.
- Add or update tests for behavior changes. Documentation-only changes still need the diff and repository gates.

## Python

- Use the service-local `pyproject.toml` in `services/control-plane`.
- Run Ruff, MyPy, and Pytest for API and orchestration changes.
- Keep unit tests independent of live Temporal, telemetry, or external backing services unless explicitly marked
  as integration tests.

## JavaScript/TypeScript

- Use the frontend-local package in `frontend/control-plane`.
- Run ESLint and the Next.js production build for UI changes.
- Add component or browser tests before merging non-trivial interactive behavior.

## Shell

- Run `shellcheck` and `shfmt -d` on touched shell scripts.

## Current Command Map

- Python install: `cd services/control-plane && python -m pip install -e '.[dev]'`.
- Python lint/type/test: `cd services/control-plane && python -m ruff check .`,
  `cd services/control-plane && python -m mypy app`, and `cd services/control-plane && python -m pytest -q`.
- Frontend install: `cd frontend/control-plane && npm install`.
- Frontend checks: `cd frontend/control-plane && npm run lint && npm run build`.
