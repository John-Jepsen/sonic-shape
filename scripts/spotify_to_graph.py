#!/usr/bin/env python
"""
Convert Spotify CSV exports (playlists/tracks/audio_features) into edge CSV for graph ingestion.

Inputs (from fetch_spotify.py):
  data_samples/spotify_playlists.csv
  data_samples/spotify_tracks.csv

Outputs:
  data_samples/spotify_edges.csv with columns: src,dst,type,weight,source,version
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_edges(playlists_csv: Path, tracks_csv: Path) -> pd.DataFrame:
    playlists = pd.read_csv(playlists_csv)
    tracks = pd.read_csv(tracks_csv)

    edges = []

    # Playlist -> track edges
    for _, row in tracks.iterrows():
        pl_id = row.get("playlist_id")
        track_id = row.get("track_id")
        if pd.isna(pl_id) or pd.isna(track_id):
            continue
        edges.append(
            {
                "src": f"playlist::{pl_id}",
                "dst": f"track::{track_id}",
                "type": "IN_PLAYLIST",
                "weight": 1.0,
                "source": "spotify",
                "version": "v1",
            }
        )

    # Track -> artist edges
    for _, row in tracks.iterrows():
        track_id = row.get("track_id")
        if pd.isna(track_id):
            continue
        artist_ids = row.get("artist_ids", "")
        if isinstance(artist_ids, str):
            try:
                # artist_ids stored as list-like string: "['id1', 'id2']" or "[id1, id2]"
                cleaned = artist_ids.strip("[]").replace("'", "").split(",")
                cleaned = [a.strip() for a in cleaned if a.strip()]
            except Exception:
                cleaned = []
        else:
            cleaned = []
        for aid in cleaned:
            edges.append(
                {
                    "src": f"artist::{aid}",
                    "dst": f"track::{track_id}",
                    "type": "PERFORMS",
                    "weight": 1.0,
                    "source": "spotify",
                    "version": "v1",
                }
            )

    return pd.DataFrame(edges)


def main():
    parser = argparse.ArgumentParser(description="Convert Spotify CSV exports to graph edges CSV.")
    parser.add_argument("--playlists", type=Path, default=Path("data_samples/spotify_playlists.csv"))
    parser.add_argument("--tracks", type=Path, default=Path("data_samples/spotify_tracks.csv"))
    parser.add_argument("--output", type=Path, default=Path("data_samples/spotify_edges.csv"))
    args = parser.parse_args()

    edges_df = build_edges(args.playlists, args.tracks)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    edges_df.to_csv(args.output, index=False)
    print(f"Wrote {len(edges_df)} edges to {args.output}")


if __name__ == "__main__":
    main()
