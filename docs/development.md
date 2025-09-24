# Development Workflow

## 1. Local Environment Setup
- Python 3.11+ requirement and recommended pyenv/ASDF usage
- Steps: `python -m venv .venv`, `source .venv/bin/activate`
- Dependency installation via `pip install -r requirements.txt`
- Optional: `pip install -r requirements-dev.txt` for tooling

## 2. Tooling & Commands
- Run linting with `make lint` (`ruff check`, `black --check`)
- Execute unit tests with `make test` (pytest with coverage)
- Launch simulator CLI using `make sim` / `python -m mb_sim.cli`
- Format code with `black .` and run static checks (`ruff`, `mypy` TBD)

## 3. Repository Conventions
- Runtime code under `src/mb_sim/`, mirrored tests under `tests/`
- Scenario assets in `scenarios/`, fixtures in `assets/`/`configs/`
- Follow Conventional Commits and include scenario IDs when relevant
- Keep commits scoped; document verification steps in PR descriptions

## 4. Development Workflow Tips
- Enable pre-commit hooks for lint/format on commit
- Use feature branches per task (e.g., `feat/gui-dashboard`)
- Run `pytest --cov=src/mb_sim --cov-report=term-missing` before PR
- Update docs alongside code changes to maintain accuracy

## 5. Onboarding Checklist
- Install dependencies
- Run smoke tests (`make lint`, `make test`)
- Review `docs/architecture.md` and `docs/testing.md`
- Configure IDE for Black (88 cols) and Ruff

