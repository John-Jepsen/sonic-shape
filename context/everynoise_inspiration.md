# EveryNoise Inspiration and Database Plan

## What EveryNoise Does
- Interactive scatter of genres and artists positioned by audio similarity using Spotify embeddings.
- Click-to-play samples, drill-down from genre to artists to playlists.
- Simple map UI with search, genre lists, and generated playlists.

## Goals for a Bigger, Better Database
- Broader coverage: include Spotify catalog samples, open datasets (GTZAN, FMA), and crowd-sourced tags (MusicBrainz/AcousticBrainz).
- Richer signals: combine Spotify audio features, open-source embeddings (VGGish, OpenL3), tempo/key/timbre descriptors, and lyrical metadata when licensed.
- Multi-level entities: genres → subgenres → artists → tracks → clips, each with embeddings and tags.
- Freshness: periodic re-crawls of APIs and recalc of embeddings so the map stays current.
- Interactivity: fast search, hover-to-preview, drill-down analytics, playlist export, and similarity browsing powered by vector search.

## Data Sources to Aggregate
- Spotify Web API (audio features, genres, popularity, 30s previews; limited by API terms).
- MusicBrainz (canonical IDs, release/artist metadata).
- AcousticBrainz (if available mirrors; low-level descriptors).
- Free Music Archive / GTZAN / other open sets for ground-truth genre labels.
- User-submitted corrections/tags stored separately with moderation.

## Pipeline Outline
1) Ingest metadata: pull artist/album/track records and IDs (Spotify + MusicBrainz) with rate-limit aware workers.  
2) Fetch audio: use Spotify previews or local datasets; store clip URIs and checksum for dedupe.  
3) Feature extraction: compute MFCCs, chroma, tempo, spectral stats; generate embeddings via VGGish/OpenL3 for each clip.  
4) Label & taxonomy: normalize genre strings; map to a curated hierarchy (genre → subgenre) and keep raw source tags.  
5) Similarity + clustering: build UMAP/TSNE/PaCMAP projections for map coordinates; maintain HNSW vectors for fast nearest-neighbor search.  
6) Serving layer: expose REST/GraphQL for metadata, search, and similarity; back with Postgres + pgvector (or Pinecone/Weaviate if external allowed).  
7) Frontend: scatter/heatmap of genres, search box, audio hover previews, drill-down to artist/track pages, playlist export.  
8) Monitoring: track ingestion freshness, missing audio, model drift on embeddings, and tag quality.

## Core Schemas (sketch)
- genres(id, name, parent_id, source_tags[])  
- artists(id, name, mbid, spotify_id, genres[], popularity)  
- tracks(id, title, artist_id, album, isrc, spotify_id, mbid, preview_uri, bpm, key, duration, source)  
- audio_features(track_id, mfcc_mean[], chroma_mean[], spectral[], tempo, loudness, mode)  
- embeddings(track_id, model, vector, created_at)  
- tags(entity_id, entity_type, tag, source, confidence, user_id?)  
- projections(entity_type, model, dim2_coords, dim3_coords, version)

## Feature Ideas to Beat EveryNoise
- Multi-embedding agreement: compare Spotify-style features with open models to reduce bias.
- Time-aware maps: show genre drift over years and track recency weighting.
- Explainability: display top features driving similarity (e.g., tempo/key/brightness).
- Quality flags: missing audio, low-SNR clips, or low-confidence tags surfaced in UI.
- Collaborative corrections: propose/approve genre fixes without breaking source data.

## Immediate Next Steps
- Confirm primary data sources allowed for this project (Spotify + open sets).  
- Stand up a small Postgres+pgvector instance and load a pilot slice (e.g., GTZAN + 500 Spotify tracks).  
- Generate embeddings (OpenL3/VGGish) and a 2D projection to validate the map UX.  
- Define a minimal genre taxonomy and tag normalizer to handle synonyms.  
- Prototype a lightweight frontend scatter with hover previews to mirror the EveryNoise feel.
