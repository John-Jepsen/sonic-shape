#!/usr/bin/env python
"""
Fetch Spotify library slices (playlists, saved tracks, audio features) into CSV.

Requires environment variables:
  SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, and either:
    - SPOTIFY_REFRESH_TOKEN (preferred), or
    - SPOTIFY_ACCESS_TOKEN (short-lived)

Outputs:
  data_samples/spotify_playlists.csv
  data_samples/spotify_tracks.csv
  data_samples/spotify_audio_features.csv
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import List

import pandas as pd

from classically_punk.ingest.spotify_auth import EnvTokenStore
from classically_punk.ingest.spotify_client import SpotifyAuthConfig, SpotifyClient


async def collect(client: SpotifyClient, max_tracks: int = 500):
    playlists_resp = await client.list_user_playlists(limit=50)
    playlists = playlists_resp.get("items", [])

    tracks: List[dict] = []
    for pl in playlists:
        pl_id = pl["id"]
        pl_name = pl["name"]
        items_resp = await client.list_playlist_items(pl_id, limit=100)
        for item in items_resp.get("items", []):
            track = item.get("track")
            if not track:
                continue
            tracks.append(
                {
                    "playlist_id": pl_id,
                    "playlist_name": pl_name,
                    "track_id": track["id"],
                    "track_name": track["name"],
                    "artist_ids": [a["id"] for a in track.get("artists", [])],
                    "artist_names": [a["name"] for a in track.get("artists", [])],
                    "preview_url": track.get("preview_url"),
                    "duration_ms": track.get("duration_ms"),
                    "popularity": track.get("popularity"),
                }
            )
            if len(tracks) >= max_tracks:
                break
        if len(tracks) >= max_tracks:
            break

    track_ids = [t["track_id"] for t in tracks if t.get("track_id")]
    features_resp = await client.get_audio_features(track_ids[:100]) if track_ids else {"audio_features": []}
    features = features_resp.get("audio_features", [])

    return playlists, tracks, features


async def main():
    parser = argparse.ArgumentParser(description="Fetch Spotify playlists/tracks.")
    parser.add_argument("--max-tracks", type=int, default=500)
    parser.add_argument("--output-dir", type=Path, default=Path("data_samples"))
    args = parser.parse_args()

    auth = SpotifyAuthConfig(
        client_id=os.environ.get("SPOTIFY_CLIENT_ID", "dummy"),
        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET", "dummy"),
        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost"),
    )
    client = SpotifyClient(auth_config=auth, token_store=EnvTokenStore())
    playlists, tracks, features = await collect(client, max_tracks=args.max_tracks)
    await client.close()

    outdir = args.output_dir
    outdir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(playlists).to_csv(outdir / "spotify_playlists.csv", index=False)
    pd.DataFrame(tracks).to_csv(outdir / "spotify_tracks.csv", index=False)
    pd.DataFrame(features).to_csv(outdir / "spotify_audio_features.csv", index=False)
    print(f"Saved {len(playlists)} playlists, {len(tracks)} tracks, {len(features)} feature rows to {outdir}")


if __name__ == "__main__":
    import asyncio
    import os

    asyncio.run(main())
