# Map API & UX Sketch (EveryNoise-Inspired)

## Goals
- Serve fast similarity-based browsing of genres/artists/tracks with hover previews.
- Keep projections versioned so the map is reproducible and refreshable.

## API Sketch (REST-ish)
- `GET /genres?search=rock&limit=20` → genre list with ids, parent, counts.
- `GET /map/genres?projection=v1` → 2D coords for genres: `[id, name, x, y, count, updated_at]`.
- `GET /map/artists?genre_id=...&projection=v1` → artist coords + top genre/tag list.
- `GET /map/tracks?artist_id=...&projection=v1` → track coords + preview_uri + tempo/key/loudness snippets.
- `GET /tracks/{id}/neighbors?top=30` → similarity based on embeddings (HNSW/pgvector).
- `GET /search?q=ambient piano&entity=track|artist|genre` → federated search.
- `GET /audio/{id}/preview` → 30s clip streaming (or redirect).
- `POST /feedback/tag` → suggested tag/genre corrections with optional user id.
- `GET /projections` → list available projection versions (model, date, metrics).

## Frontend UX Notes
- **Map view:** UMAP scatter of genres (default) with search; hover to preview a canonical track; click to drill into artists and then tracks.
- **Filters:** year range, popularity, audio brightness/warmth sliders; toggle to bias toward recency.
- **Detail drawer:** for a selected node show mini waveform, tempo/key, loudness, top similar items, and “export playlist” CTA.
- **Layout:** keep density manageable via clustering at higher zoom; show counts; staggered reveal on load.
- **Explainability:** surface top features driving similarity for the selection; show projection version badge.

## Data/Storage Notes
- Store coords in `projections` table keyed by entity/model/version; keep embeddings in vector index.
- Cache search/autocomplete results; rate-limit preview streaming.
- Keep raw dataset paths and licenses tracked; never expose private data.
