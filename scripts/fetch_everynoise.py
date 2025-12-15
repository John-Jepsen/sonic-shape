#!/usr/bin/env python
"""
Fetch EveryNoise genre map data and export to CSV.

Outputs to data_samples/everynoise_genres.csv by default.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from classically_punk.ingest.everynoise import fetch_everynoise


def main():
    parser = argparse.ArgumentParser(description="Fetch EveryNoise genre map.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data_samples/everynoise_genres.csv"),
        help="Output CSV path",
    )
    args = parser.parse_args()

    records = fetch_everynoise()
    df = pd.DataFrame.from_records(records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} genres to {args.output}")


if __name__ == "__main__":
    main()
