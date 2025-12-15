#!/usr/bin/env python
"""
Extract audio feature vectors for a list of tracks with preview URLs or local paths.

Inputs:
  - CSV with columns: track_id, label (optional), path (optional), preview_url (optional)
    If preview_url is provided, you must download audio separately; this script expects local paths.

Outputs:
  - CSV with feature columns suitable for modeling/graph use.

Example:
  PYTHONPATH=src python scripts/extract_features.py --tracks data_samples/spotify_tracks_with_paths.csv --audio-root . --output data_samples/spotify_features.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from classically_punk.features.audio import extract_from_file


def main():
    parser = argparse.ArgumentParser(description="Extract audio features for tracks with local paths.")
    parser.add_argument("--tracks", type=Path, required=True, help="CSV with columns: track_id, label?, path")
    parser.add_argument("--audio-root", type=Path, default=None, help="Root folder to prepend to relative paths")
    parser.add_argument("--output", type=Path, required=True, help="Output CSV for features")
    parser.add_argument("--sr", type=int, default=22050)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--n-mfcc", type=int, default=20)
    args = parser.parse_args()

    df = pd.read_csv(args.tracks)
    records = []
    for _, row in df.iterrows():
        path = row.get("path")
        if pd.isna(path):
            continue
        audio_path = Path(path)
        if args.audio_root:
            audio_path = args.audio_root / audio_path
        vector, names = extract_from_file(audio_path, sr=args.sr, duration=args.duration, n_mfcc=args.n_mfcc)
        rec = {"track_id": row.get("track_id"), "label": row.get("label")}
        rec.update({name: float(val) for name, val in zip(names, vector)})
        records.append(rec)

    out_df = pd.DataFrame.from_records(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(args.output, index=False)
    print(f"Wrote {len(out_df)} feature rows to {args.output}")


if __name__ == "__main__":
    main()
