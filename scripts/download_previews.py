#!/usr/bin/env python
"""
Download Spotify track preview URLs to local files and annotate a tracks CSV with paths.

Inputs:
  - tracks CSV with columns: track_id, preview_url (from fetch_spotify.py)

Outputs:
  - downloads previews to <audio_root>/<track_id>.mp3 (default: data/previews)
  - writes an updated tracks CSV with a 'path' column
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

import pandas as pd
import requests


def download_preview(url: str, dest: Path, timeout: int = 30) -> bool:
    try:
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.content)
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Download Spotify previews to local files.")
    parser.add_argument("--tracks", type=Path, required=True, help="tracks CSV with preview_url column")
    parser.add_argument("--audio-root", type=Path, default=Path("data/previews"))
    parser.add_argument("--output", type=Path, default=Path("data_samples/spotify_tracks_with_paths.csv"))
    args = parser.parse_args()

    df = pd.read_csv(args.tracks)
    paths: List[str] = []
    successes = 0
    for _, row in df.iterrows():
        url = row.get("preview_url")
        track_id = row.get("track_id")
        if pd.isna(url) or pd.isna(track_id):
            paths.append("")
            continue
        dest = args.audio_root / f"{track_id}.mp3"
        ok = download_preview(url, dest)
        if ok:
            successes += 1
            paths.append(str(dest))
        else:
            paths.append("")

    df["path"] = paths
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Downloaded {successes} previews. Wrote annotated tracks CSV to {args.output}")


if __name__ == "__main__":
    main()
