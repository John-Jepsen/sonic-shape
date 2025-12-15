# Classically Punk
Genre classification and audio feature mapping inspired by EveryNoise. The goal is to ingest music datasets, extract robust features, and classify genres while exposing data for interactive maps and analysis.

## Project Layout
- `src/classically_punk/`: package code.
  - `data/`: dataset indexing and loading.
  - `features/`: audio feature extraction.
  - `features/visualization.py`: 3D projections, density surfaces, Plotly exports.
  - `models/`: modeling helpers (to be added).
  - `ingest/`: external API clients (Spotify, EveryNoise).
    - `ingest/spotify_auth.py`: OAuth helpers (auth URL, token exchange/refresh).
    - `ingest/everynoise.py`: scrape EveryNoise genre map.
  - `graph/`: graph schema, kNN edges, glyphs, and genre hull generation.
- `tests/`: pytest suite for utilities.
- `context/`: project briefs and inspiration docs.
- `docs/`: add pipeline notes and reports here.
- `data/`: place local audio datasets (gitignored).

## Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Add `export PYTHONPATH=src` to use the package without installing.
```

## Usage Examples
Index labeled folders (e.g., GTZAN-style):
```python
from classically_punk.data.dataset import index_labeled_folders
rows = index_labeled_folders("data/gtzan")
```

Extract features into a DataFrame:
```python
from classically_punk.features.audio import featurize_dataset
df = featurize_dataset(rows, sr=22050, duration=30.0, n_mfcc=20)
```

Train a baseline classifier:
```python
from classically_punk.models import train_baseline_classifier, evaluate_classifier

clf, X_test, y_test = train_baseline_classifier(df, target_col="label")
metrics = evaluate_classifier(clf, X_test, y_test)
print(metrics["accuracy"])
```

Project to 2D map coordinates (EveryNoise-style):
```python
from classically_punk.features.projection import project_with_umap
coords_df, umap_model = project_with_umap(df, target_col="label", n_components=2)
```

## Testing
Run the suite:
```bash
pytest
```

## Data Fetching Pipeline

### 1. EveryNoise genres to CSV:
```bash
PYTHONPATH=src python scripts/fetch_everynoise.py --output data_samples/everynoise_genres.csv
```

### 2. Spotify OAuth setup:
```bash
# Generate authorization URL (use 127.0.0.1, not localhost per Spotify's 2025 policy)
python scripts/spotify_oauth.py --step url \
  --client-id $SPOTIFY_CLIENT_ID \
  --redirect-uri http://127.0.0.1:8888/callback \
  --scope "user-library-read playlist-read-private"

# After authorizing and copying the code from the redirect URL:
python scripts/spotify_oauth.py --step exchange \
  --client-id $SPOTIFY_CLIENT_ID \
  --client-secret $SPOTIFY_CLIENT_SECRET \
  --redirect-uri http://127.0.0.1:8888/callback \
  --code <AUTH_CODE>
```

### 3. Fetch Spotify playlists and tracks:
```bash
export SPOTIFY_CLIENT_ID=<your_client_id>
export SPOTIFY_CLIENT_SECRET=<your_client_secret>
export SPOTIFY_REFRESH_TOKEN=<your_refresh_token>

# Fetch from public genre playlists (default):
PYTHONPATH=src python scripts/fetch_spotify.py \
  --source featured \
  --max-playlists 100 \
  --max-tracks 5000 \
  --output-dir data_samples

# Or fetch from your own playlists:
PYTHONPATH=src python scripts/fetch_spotify.py --source me --max-tracks 500 --output-dir data_samples
```

### 4. Download audio previews (if available):
```bash
PYTHONPATH=src python scripts/download_previews.py \
  --tracks data_samples/spotify_tracks.csv \
  --audio-root data/previews \
  --output data_samples/spotify_tracks_with_paths.csv
```
> **Note:** Spotify restricted preview URLs for new apps (Nov 2024). Most tracks return empty preview_url.

### 5. Build graph edges:
```bash
PYTHONPATH=src python scripts/spotify_to_graph.py \
  --playlists data_samples/spotify_playlists.csv \
  --tracks data_samples/spotify_tracks.csv \
  --output data_samples/spotify_edges.csv
```

### 6. Extract audio features (requires audio files):
```bash
PYTHONPATH=src python scripts/extract_features.py \
  --tracks data_samples/spotify_tracks_with_paths.csv \
  --audio-root . \
  --output data_samples/spotify_features.csv
```

### 7. Load into Postgres:
```bash
PGHOST=... PGPORT=... PGUSER=... PGPASSWORD=... PGDATABASE=... \
PYTHONPATH=src python scripts/load_postgres.py \
  --playlists data_samples/spotify_playlists.csv \
  --tracks data_samples/spotify_tracks_with_paths.csv \
  --edges data_samples/spotify_edges.csv \
  --everynoise data_samples/everynoise_genres.csv
```

## Current Data Status
- **102 playlists** fetched from Spotify genre searches
- **5,000 tracks** with metadata (name, artist, popularity)
- **10,050 graph edges** (playlist→track, track→artist relationships)
- **0 audio previews** (Spotify API restriction)

## Known Limitations
- **Spotify audio-features API** deprecated for new apps (Nov 2024). We extract our own features from audio files instead.
- **Preview URLs** restricted. Alternative audio sources (Free Music Archive, etc.) needed for feature extraction.
- **Redirect URI** must use `http://127.0.0.1:PORT/callback` (not `localhost`) per Spotify's April 2025 policy.

## Notes
- Keep raw audio and large artifacts out of Git; use `data/`.
- Reference `context/project_description.md` and `context/everynoise_inspiration.md` for the product brief and roadmap.
- Contributor guidance: see `AGENTS.md`.
