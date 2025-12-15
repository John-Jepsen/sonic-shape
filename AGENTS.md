# Repository Guidelines

## Project Structure & Module Organization
- `context/`: reference briefs and planning notes (do not edit programmatically).
- `src/classically_punk/`: main package code
  - `data/`: dataset indexing and loading
  - `features/`: audio feature extraction, UMAP projection, visualization
  - `models/`: baseline classifiers and evaluation
  - `ingest/`: external API clients (Spotify OAuth, EveryNoise scraper)
  - `graph/`: schema definitions, kNN edges, graph export (JSON/GraphML)
  - `tags/`: genre tag normalization
- `scripts/`: CLI tools for pipeline steps (fetch, download, extract, load)
- `tests/`: pytest suite
- `data/` (gitignored): local audio files
- `data_samples/`: CSV outputs (playlists, tracks, edges, features)
- `docs/`: reports, backlog, workflow notes
- `notebooks/`: EDA (keep lean, move reusable code to `src/`)

## Build, Test, and Development Commands
- Create env: `python -m venv .venv && source .venv/bin/activate`.
- Install deps: `pip install -r requirements.txt`.
- Run tests: `pytest`.
- Run scripts: `PYTHONPATH=src python scripts/<script>.py`.
- Format (if configured): `black src tests` and `isort src tests`.
- Lint (if configured): `flake8 src tests` or `ruff check src tests`.

## Current Pipeline Commands
```bash
# 1. Fetch playlists/tracks from Spotify
PYTHONPATH=src python scripts/fetch_spotify.py --source featured --max-playlists 100 --max-tracks 5000 --output-dir data_samples

# 2. Download audio previews (if available)
PYTHONPATH=src python scripts/download_previews.py --tracks data_samples/spotify_tracks.csv --audio-root data/previews --output data_samples/spotify_tracks_with_paths.csv

# 3. Build graph edges
PYTHONPATH=src python scripts/spotify_to_graph.py --playlists data_samples/spotify_playlists.csv --tracks data_samples/spotify_tracks.csv --output data_samples/spotify_edges.csv

# 4. Extract audio features (requires audio files)
PYTHONPATH=src python scripts/extract_features.py --tracks data_samples/spotify_tracks_with_paths.csv --audio-root . --output data_samples/spotify_features.csv

# 5. Load into Postgres
PGHOST=... PGPORT=... PGUSER=... PGPASSWORD=... PGDATABASE=... PYTHONPATH=src python scripts/load_postgres.py
```

## Spotify API Limitations (as of 2024-2025)
- **audio-features endpoint**: Deprecated for new apps (Nov 2024). Extract features from audio files instead.
- **preview_url**: Restricted for most tracks. Need alternative audio sources (FMA, Jamendo, GTZAN).
- **Redirect URI**: Must use `http://127.0.0.1:PORT/callback` (not `localhost`) per April 2025 policy.
- **OAuth scopes**: Use `user-library-read playlist-read-private` for library access.

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
- **Current data**: 102 playlists, 5,000 tracks, 10,050 edges in `data_samples/`.  
