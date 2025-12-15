# Backlog & Branch Placeholders

## Active Now
- `feature/spotify-oauth-curio`
  - Goal: Spotify OAuth (auth code flow) and async client using Curio for metadata/audio features/previews.
  - Deliverables: token storage interface (env/file), rate-limited GET helpers, track/artist/playlist fetchers, preview URI capture, tests with mocked responses.

## Ready Next
- `feature/ingest-pipeline`
  - Storage schema (Postgres + pgvector), ingest jobs, dedupe for tracks/artists/genres.
- `feature/speech-embeddings`
  - Spoken-word pipeline (OpenL3/wav2vec), tagging, and filters.
- `feature/projection-service`
  - Projection runner (UMAP versioning) + endpoints per `docs/map_api_ux.md`.
- `feature/linear-regression`
  - Multivariable linear regression model + evaluation/reporting.
- `docs/presentation-outline`
  - Slide outline covering assumptions, risks, user/business impact.

## Process Notes
- Every item above should map to a Git issue; open PRs from the matching branch name with human review required.
