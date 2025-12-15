# Agentic Workflow & Human-in-the-Loop

## Branching & Reviews
- Work in short-lived feature branches: `feature/<area>-<short-desc>` (e.g., `feature/spotify-ingest`, `feature/speech-embeddings`), `chore/<desc>` for maintenance, `docs/<desc>` for documentation.
- Every branch opens a PR; no direct pushes to `main`. PRs require human review/approval before merge.
- Keep commits tight (ideally per file change) to simplify review; follow `AGENTS.md` for commit style.

## Task Loop
1) Create/assign issue with a small scope (e.g., “Add Spotify auth client scaffolding”).  
2) Branch from `main`.  
3) Implement with tests/docs as part of the same branch.  
4) Run `pytest` (and format/lint if configured).  
5) Open PR using the template; attach screenshots/plots for UX changes and metrics for models.  
6) Human reviews; address comments; merge only after approval and passing checks.

## Human Checkpoints
- Security/privacy: any change touching credentials, OAuth flows, or data export.  
- Modeling: new model versions, projection changes, or major metric shifts.  
- Data ingest: new external sources or schema migrations.  
- UX: production-facing UI changes.

## Current Priority Tracks (suggested branches)

### ✅ Completed
- `feature/spotify-oauth-curio`: Spotify OAuth flow + async client (merged, working)

### 🚧 In Progress  
- `feature/audio-sources`: Alternative audio since Spotify deprecated previews (Nov 2024)

### 📋 Up Next
- `feature/ingest-pipeline`: storage schema (Postgres+pgvector), ingestion jobs, dedupe
- `feature/projection-service`: projection runner (UMAP versioning) + endpoints per `docs/map_api_ux.md`
- `feature/linear-regression`: implement multivariable linear regression model + evaluation/reporting
- `docs/presentation-outline`: slide outline covering assumptions, risks, user/business impact

## Notes
- Keep data under `data/` (gitignored); document provenance/licenses in `docs/`.  
- Use `PYTHONPATH=src` or editable install for dev; ensure tests touch new paths.  
- Prefer small PRs that each deliver one cohesive change.
- **Spotify API changes (2024-2025):** audio-features endpoint deprecated, preview URLs restricted, redirect URIs must use `127.0.0.1` not `localhost`.  
