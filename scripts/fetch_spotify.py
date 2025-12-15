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


async def collect(client: SpotifyClient, max_tracks: int = 5000, max_playlists: int = 200, source: str = "featured"):
    async def paginate(path: str, params: dict | None = None):
        url = path
        first = True
        while url:
            resp = await client.get(url, params=params if first else None)
            yield resp
            url = resp.get("next")
            first = False

    playlists: List[dict] = []
    
    if source == "me":
        # User's own playlists
        async for page in paginate("me/playlists", params={"limit": 50}):
            playlists.extend(page.get("items", []))
            if len(playlists) >= max_playlists:
                break
    else:
        # Search for playlists by genre keywords for variety
        genres = ["rock", "pop", "jazz", "classical", "hip hop", "electronic", "indie", "metal", "punk", "r&b", "country", "latin", "blues", "folk", "soul"]
        seen_ids = set()
        for genre in genres:
            if len(playlists) >= max_playlists:
                break
            try:
                search_resp = await client.get("search", params={"q": genre, "type": "playlist", "limit": 20})
                for pl in search_resp.get("playlists", {}).get("items", []):
                    if pl and pl.get("id") not in seen_ids:
                        seen_ids.add(pl["id"])
                        playlists.append(pl)
            except Exception:
                continue

    tracks: List[dict] = []
    for pl in playlists:
        pl_id = pl["id"]
        pl_name = pl["name"]
        async for items_resp in paginate(f"playlists/{pl_id}/tracks", params={"limit": 100}):
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
        if len(tracks) >= max_tracks:
            break

    # Note: Spotify deprecated the audio-features endpoint for new apps (Nov 2024).
    # We'll extract our own features from audio previews instead.
    features: List[dict] = []

    return playlists, tracks, features


async def main():
    parser = argparse.ArgumentParser(description="Fetch Spotify playlists/tracks.")
    parser.add_argument("--max-tracks", type=int, default=500)
    parser.add_argument("--max-playlists", type=int, default=200)
    parser.add_argument("--output-dir", type=Path, default=Path("data_samples"))
    parser.add_argument("--source", choices=["me", "featured"], default="featured", help="'me' for user playlists, 'featured' for public/category playlists")
    args = parser.parse_args()

    auth = SpotifyAuthConfig(
        client_id=os.environ.get("SPOTIFY_CLIENT_ID", "dummy"),
        client_secret=os.environ.get("SPOTIFY_CLIENT_SECRET", "dummy"),
        redirect_uri=os.environ.get("SPOTIFY_REDIRECT_URI", "http://localhost"),
    )
    client = SpotifyClient(auth_config=auth, token_store=EnvTokenStore())
    playlists, tracks, features = await collect(client, max_tracks=args.max_tracks, max_playlists=args.max_playlists, source=args.source)
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
