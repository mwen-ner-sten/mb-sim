# Repository Guidelines

## Project Structure & Module Organization
mb-sim is in active scaffolding; keep all runtime code inside `src/mb_sim/` with subpackages such as `src/mb_sim/protocols/` for frame logic and `src/mb_sim/models/` for device abstractions. Scenario definitions belong in `scenarios/`, while reusable fixtures, sample captures, and config templates live in `assets/` and `configs/`. Mirror the package layout under `tests/` (e.g., `tests/protocols/test_rtu.py`) so every module ships with a matching test file.

## Build, Test, and Development Commands
Work against Python 3.11+. Create a virtual env (`python -m venv .venv && source .venv/bin/activate`) and install local dependencies (`pip install -r requirements.txt`). Use the helper targets in the forthcoming `Makefile`: `make lint` runs `ruff check` and `black --check`, `make test` calls `pytest`, and `make sim` executes the CLI entry point `python -m mb_sim.cli`. When Make targets are unavailable, invoke the underlying commands directly.

## Coding Style & Naming Conventions
Follow Black formatting (88 char line width) with Ruff for linting; run both before pushing. Indent with four spaces. Modules and functions use snake_case, classes PascalCase, constants UPPER_SNAKE_CASE. Name scenario files with the pattern `scenario_<bus-mode>_<feature>.yml`. Favor type hints and descriptive docstrings for public APIs.

## Testing Guidelines
Write tests with Pytest. Co-locate fixtures in `tests/conftest.py` and mark slow, integration-heavy simulations with `@pytest.mark.slow`. Test modules start with `test_` and follow the package path. Aim for ≥90% coverage using `pytest --cov=src/mb_sim --cov-report=term-missing`. Provide packet-capture samples under `tests/data/` and assert on decoded message fields rather than raw bytes alone.

## Commit & Pull Request Guidelines
Adopt Conventional Commit prefixes (`feat:`, `fix:`, `chore:`). Keep commits scoped to a single concern and include relevant scenario IDs in the body when applicable. Pull requests must describe the change, enumerate verification steps (`make test`, `make lint`), and attach CLI output or screenshots for new behaviors. Link the tracking issue and request review once CI passes.

## Security & Configuration Tips
Never commit `.env` or sensitive capture files; add new patterns to `.gitignore` when needed. Scrub device identifiers from example payloads before publishing. Regenerate requirements with `pip-compile` to ensure deterministic builds and review diffs for unintended upgrades.
