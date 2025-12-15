#!/usr/bin/env python
"""
Load Spotify/EveryNoise CSVs into Postgres with pgvector-ready schema.

Requires env:
  PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

Inputs (defaults):
  data_samples/spotify_playlists.csv
  data_samples/spotify_tracks_with_paths.csv
  data_samples/spotify_audio_features.csv
  data_samples/spotify_edges.csv
  data_samples/everynoise_genres.csv

Schema (created if not exists):
  playlists(id primary key, name text)
  tracks(id primary key, name text, preview_url text, path text, duration_ms int, popularity int)
  track_artists(track_id text, artist_id text, artist_name text)
  audio_features(track_id text primary key, tempo float, zcr_mean float, centroid_mean float, rolloff_mean float, ... placeholder for MFCC/chroma not loaded here)
  edges(src text, dst text, type text, weight float, source text, version text)
  everynoise_genres(id text, name text, color text, top_px float, left_px float, font_size_pct float)

Note: pgvector column can be added later for embeddings; this script seeds tables with CSV data.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import pandas as pd
import psycopg


def load_csv(conn, df: pd.DataFrame, table: str, create_sql: str):
    with conn.cursor() as cur:
        cur.execute(create_sql)
        cols = list(df.columns)
        placeholders = ",".join(["%s"] * len(cols))
        colnames = ",".join(cols)
        records = [tuple(None if pd.isna(v) else v for v in row) for row in df.to_records(index=False)]
        if records:
            cur.executemany(f"INSERT INTO {table} ({colnames}) VALUES ({placeholders}) ON CONFLICT DO NOTHING", records)
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Load CSVs into Postgres.")
    parser.add_argument("--playlists", type=Path, default=Path("data_samples/spotify_playlists.csv"))
    parser.add_argument("--tracks", type=Path, default=Path("data_samples/spotify_tracks_with_paths.csv"))
    parser.add_argument("--audio-features", type=Path, default=Path("data_samples/spotify_audio_features.csv"))
    parser.add_argument("--edges", type=Path, default=Path("data_samples/spotify_edges.csv"))
    parser.add_argument("--everynoise", type=Path, default=Path("data_samples/everynoise_genres.csv"))
    args = parser.parse_args()

    conn = psycopg.connect()

    playlists = pd.read_csv(args.playlists)
    load_csv(
        conn,
        playlists[["id", "name"]] if "id" in playlists.columns else playlists.rename(columns={"playlist_id": "id", "playlist_name": "name"}),
        "playlists",
        "CREATE TABLE IF NOT EXISTS playlists (id text primary key, name text)",
    )

    tracks = pd.read_csv(args.tracks)
    tracks_cols = ["track_id", "track_name", "preview_url", "path", "duration_ms", "popularity"]
    existing = [c for c in tracks_cols if c in tracks.columns]
    load_csv(
        conn,
        tracks[existing],
        "tracks",
        "CREATE TABLE IF NOT EXISTS tracks (id text primary key, name text, preview_url text, path text, duration_ms int, popularity int)",
    )

    # Track artists (explode artists columns if present)
    if "artist_ids" in tracks.columns and "artist_names" in tracks.columns:
        rows = []
        for _, row in tracks.iterrows():
            tid = row.get("track_id")
            ids = str(row.get("artist_ids", "")).strip("[]").replace("'", "").split(",")
            names = str(row.get("artist_names", "")).strip("[]").replace("'", "").split(",")
            for aid, aname in zip(ids, names):
                aid = aid.strip()
                aname = aname.strip()
                if aid:
                    rows.append({"track_id": tid, "artist_id": aid, "artist_name": aname})
        artists_df = pd.DataFrame(rows)
        load_csv(
            conn,
            artists_df,
            "track_artists",
            "CREATE TABLE IF NOT EXISTS track_artists (track_id text, artist_id text, artist_name text)",
        )

    # Audio features (raw Spotify features, not our extracted ones)
    audio = pd.read_csv(args.audio_features)
    if not audio.empty:
        load_csv(
            conn,
            audio,
            "audio_features",
            "CREATE TABLE IF NOT EXISTS audio_features (track_id text primary key, danceability float, energy float, key int, loudness float, mode int, speechiness float, acousticness float, instrumentalness float, liveness float, valence float, tempo float, duration_ms int, time_signature int)",
        )

    # Edges
    edges = pd.read_csv(args.edges)
    load_csv(
        conn,
        edges,
        "edges",
        "CREATE TABLE IF NOT EXISTS edges (src text, dst text, type text, weight float, source text, version text)",
    )

    # EveryNoise
    everynoise = pd.read_csv(args.everynoise)
    if not everynoise.empty:
        everynoise = everynoise.rename(columns={"id": "id"})
        load_csv(
            conn,
            everynoise[["id", "name", "color", "top_px", "left_px", "font_size_pct"]] if set(["name", "color", "top_px", "left_px", "font_size_pct"]).issubset(everynoise.columns) else everynoise,
            "everynoise_genres",
            "CREATE TABLE IF NOT EXISTS everynoise_genres (id text, name text, color text, top_px float, left_px float, font_size_pct float)",
        )

    conn.close()
    print("Loaded data into Postgres.")


if __name__ == "__main__":
    main()
