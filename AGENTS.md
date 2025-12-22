# Agent Notes

## Project overview
- Streamlit app for nutrition scanning + meal logging with Open Food Facts lookup.
- Architecture follows a simple layered layout: domain models/rules, application services, infrastructure adapters (API + SQLite), and presentation (Streamlit UI).

## Key paths
- `havij/presentation/streamlit_app.py`: Streamlit entry point.
- `havij/application/services/`: service layer (meal, product, user).
- `havij/domain/model/`: core domain models (meal, product, nutrients, user) and rules in `havij/domain/rules.py`.
- `havij/infrastructure/`: persistence (SQLite) + external API (Open Food Facts).
- `tests/`: unit tests grouped by domain/application/infrastructure.

## Runtime configuration
- `DB_PATH` env var controls SQLite file location (default: `data/app.sqlite`).

## Dev setup
- Install dependencies: `poetry install`
- Run app: `poetry run streamlit run havij/presentation/streamlit_app.py`

## Quality gates (match .github/workflows/check.yml)
- Compile check: `poetry run poe compile`
- Type checks: `poetry run poe mypy`
- Tests: `poetry run poe test`
- Coverage run/report: `poetry run poe coverage` and `poetry run poe coverage-report`

For a change to go through, tests must pass and mypy must succeed, consistent with `.github/workflows/check.yml`.

## Git workflow
- Default branch is `dev`. All changes branch from `dev`.
- Branching style follows git-flow conventions (feature/ release/ hotfix branches off `dev` as appropriate).
- Commit messages follow Conventional Commits.
- When `dev` is merged into `main`, a release is created automatically.
