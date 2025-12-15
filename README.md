# Classically Punk

Genre classification and audio feature mapping inspired by EveryNoise. Ingest music datasets, extract features, classify genres, and build interactive maps.

## Current Data
- **102 playlists** from Spotify genre searches
- **5,000 tracks** with metadata
- **10,050 graph edges** (playlist→track, track→artist)

## Project Structure
```
src/classically_punk/
  data/       # dataset indexing
  features/   # audio extraction, UMAP, visualization
  models/     # classifiers
  ingest/     # Spotify, EveryNoise clients
  graph/      # schema, kNN edges, export
scripts/      # CLI pipeline tools
data_samples/ # CSV outputs
```

## Known Limitations
- Spotify **audio-features API** deprecated (Nov 2024)
- **Preview URLs** restricted for new apps
- Redirect URI must use `127.0.0.1` not `localhost`

See `AGENTS.md` for full pipeline commands and contributor guidelines.
