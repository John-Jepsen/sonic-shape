# Backlog & Branch Placeholders

## ✅ Completed
- `feature/spotify-oauth-curio`
  - Spotify OAuth (auth code flow) with token exchange/refresh
  - Async client with rate-limited GET helpers
  - Track/artist/playlist fetchers via genre search
  - Tests with mocked responses
  - **Status:** Merged to main. OAuth working, 5k tracks fetched.

## Active Now
- `feature/audio-sources`
  - Goal: Alternative audio sources since Spotify deprecated preview URLs (Nov 2024).
  - Options: Free Music Archive, Jamendo, local datasets (GTZAN, FMA).
  - Deliverables: Audio downloader, path annotation, feature extraction pipeline.

## Ready Next
- `feature/ingest-pipeline`
  - Storage schema (Postgres + pgvector), ingest jobs, dedupe for tracks/artists/genres.
  - **Partial:** load_postgres.py script ready, needs pgvector embeddings.
- `feature/projection-service`
  - Projection runner (UMAP versioning) + endpoints per `docs/map_api_ux.md`.
  - **Blocked by:** Need audio features for meaningful projections.
- `feature/linear-regression`
  - Multivariable linear regression model + evaluation/reporting.
- `docs/presentation-outline`
  - Slide outline covering assumptions, risks, user/business impact.

## Deferred
- `feature/speech-embeddings`
  - Spoken-word pipeline (OpenL3/wav2vec), tagging, and filters.
  - Lower priority until core music pipeline complete.

## Process Notes
- Every item above should map to a Git issue; open PRs from the matching branch name with human review required.
