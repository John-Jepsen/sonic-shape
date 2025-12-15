# Repository Guidelines

## Project Structure & Module Organization
- `context/`: reference briefs and planning notes (do not edit programmatically).
- Recommended layout as code lands: `src/` for pipeline modules (ingest, features, modeling), `notebooks/` for EDA, `data/` (gitignored) for local audio, `docs/` for reports/slides, `tests/` for unit/integration checks.
- Keep pure Python modules in `src/` and import via package-relative paths; keep notebooks lean and back reusable code into modules.

## Build, Test, and Development Commands
- Create env: `python -m venv .venv && source .venv/bin/activate`.
- Install deps (once `requirements.txt` exists): `pip install -r requirements.txt`.
- Run tests: `pytest`.
- Format (if configured): `black src tests` and `isort src tests`.
- Lint (if configured): `flake8 src tests` or `ruff check src tests`.

## Coding Style & Naming Conventions
- Python 3; 4-space indentation; UTF-8 files.
- Modules/functions/variables: `snake_case`; classes: `CapWords`; constants: `UPPER_SNAKE`.
- Prefer type hints and docstrings for public functions.
- Keep notebooks stripped of outputs before commit (`nbstripout` if enabled); move durable logic into `src/`.

## Testing Guidelines
- Use `pytest` with descriptive test names (`test_feature_extraction.py`, `test_<function>()`).
- Cover feature extraction edge cases (silence, clipping, short clips) and model scoring paths.
- For audio-dependent tests, include small fixtures or mocks; avoid committing large binaries.

## Commit & Pull Request Guidelines
- Commits: short imperative subject (`Add MFCC extraction`), include scope when helpful.
- Commit early/often: prefer a commit for each meaningful file change so diffs stay tight and reviewable.
- PRs: describe change, mention datasets touched, add before/after metrics for models, include screenshots/plots if UI or visualization changes.
- Link issues/tasks when available; note any migration or data-refresh steps.

## Data & Security Notes
- Keep raw datasets out of Git; store under `data/` with `.gitignore`.
- Do not commit API keys or tokens; use env vars (`.env` locally, secrets in deployment).
- Document dataset provenance and licenses in `docs/` before sharing outputs.  
