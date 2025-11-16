# Skema — Agent Guide

## Commands
```bash
# Tests (CI runs contract tests only):
PYTHONPATH=. pytest tests/unit -v                    # 5 domain + use case tests
PYTHONPATH=. pytest tests/contracts -v               # 2 port contract tests
PYTHONPATH=. pytest tests/integration -v             # 2 integration flow tests
PYTHONPATH=. pytest tests/ -v                        # all 9 tests

# Lint / typecheck:
ruff check .                                 # ruff (from pyproject.toml)
mypy .                                       # mypy (from pyproject.toml)

# Run API locally:
python -m skema.api.main                     # starts FastAPI on :8000

# Docker:
docker-compose up --build                    # starts PostgreSQL + API
```

## Critical Quirks

- **Hexagonal Architecture — strict layer isolation**: 
  - `skema/core/` = pure domain (models, interfaces/ports, use cases). **Zero framework imports allowed** (no FastAPI, no SQLAlchemy, no requests).
  - `skema/adapters/` = concrete implementations of ports (classifiers, storage, processor).
  - `skema/infrastructure/` = database setup, ORM models, PostgreSQL repositories.
  - `skema/api/` = FastAPI REST endpoints.
  - **Dependencies flow inward**: adapters → core, infrastructure → core, api → core. Never import from adapters/infrastructure/api into core.
- **`setup.py` exists** alongside `pyproject.toml` — `find_packages()` auto-discovers `skema.*`. If you add a new package directory, ensure it's under `skema/`.
- **PostgreSQL required** for integration tests. `docker-compose up postgres` before running `tests/integration/`. Unit + contract tests use in-memory fakes and don't need Postgres.
- **`requirements.full.txt`** includes optional deps (sentence-transformers for embeddings). `requirements.txt` is the minimal set.
- **CI runs only `tests/contracts`** — not unit or integration. If adding tests, ensure contracts pass CI.
- **Classifier models**: `hybrid` (keywords + embeddings) is the production classifier. `dummy` is for testing. Set `CLASSIFIER_MODEL=dummy` for fast local dev without embedding dependencies.
- **Vercel entry point** at `api/index.py` uses Mangum. The dashboard templates (`skema/dashboard/templates/`) are Jinja2 — served by FastAPI, not a separate frontend service.
