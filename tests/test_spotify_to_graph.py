from pathlib import Path

import pandas as pd

from scripts.spotify_to_graph import build_edges


def test_build_edges_creates_playlist_and_artist_edges(tmp_path: Path):
    playlists_csv = tmp_path / "playlists.csv"
    tracks_csv = tmp_path / "tracks.csv"

    pd.DataFrame([{"id": "pl1", "name": "Test"}]).to_csv(playlists_csv, index=False)
    pd.DataFrame(
        [
            {
                "playlist_id": "pl1",
                "playlist_name": "Test",
                "track_id": "t1",
                "artist_ids": "['a1','a2']",
            }
        ]
    ).to_csv(tracks_csv, index=False)

    edges = build_edges(playlists_csv, tracks_csv)
    assert not edges.empty
    types = set(edges["type"].tolist())
    assert "IN_PLAYLIST" in types
    assert "PERFORMS" in types
