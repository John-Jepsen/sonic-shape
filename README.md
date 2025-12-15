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

## Data Fetching
- EveryNoise genres to CSV:
```bash
PYTHONPATH=src python scripts/fetch_everynoise.py --output data_samples/everynoise_genres.csv
```
- Spotify OAuth helper (generate URL / exchange code):
```bash
python scripts/spotify_oauth.py --step url --client-id $SPOTIFY_CLIENT_ID --redirect-uri $SPOTIFY_REDIRECT_URI --scope "user-library-read playlist-read-private"
# After copying the code from the redirect:
python scripts/spotify_oauth.py --step exchange --client-id $SPOTIFY_CLIENT_ID --client-secret $SPOTIFY_CLIENT_SECRET --redirect-uri $SPOTIFY_REDIRECT_URI --code <AUTH_CODE>
```
- Spotify library sample to CSV (requires access token env):
```bash
SPOTIFY_ACCESS_TOKEN=<token> PYTHONPATH=src python scripts/fetch_spotify.py --max-tracks 500 --output-dir data_samples
```

## Notes
- Keep raw audio and large artifacts out of Git; use `data/`.
- Reference `context/project_description.md` and `context/everynoise_inspiration.md` for the product brief and roadmap.
- Contributor guidance: see `AGENTS.md`.
