import numpy as np
import pandas as pd

from pathlib import Path

from classically_punk.graph.export import edges_to_networkx, export_node_link_json
from classically_punk.graph.schema import Edge, aggregate_genre_embeddings, build_knn_edges
from classically_punk.graph.shapes import build_genre_hulls, radial_glyph_from_features


def test_build_knn_edges_cosine_weights():
    embeddings = np.array([[1, 0], [0, 1], [1, 1]], dtype=float)
    ids = ["a", "b", "c"]
    edges = build_knn_edges(embeddings, ids, k=1, metric="cosine", source="test", version="vX")
    assert all(e.type == "SIMILAR_TO" for e in edges)
    assert all(0.0 <= e.weight <= 1.0 for e in edges)


def test_aggregate_genre_embeddings_returns_centroids():
    df = pd.DataFrame(
        [
            {"label": "rock", "f0": 1.0, "f1": 0.0},
            {"label": "rock", "f0": 3.0, "f1": 2.0},
            {"label": "jazz", "f0": 0.0, "f1": 2.0},
        ]
    )
    agg_df, vectors, ids = aggregate_genre_embeddings(df)
    assert set(agg_df["genre"]) == {"rock", "jazz"}
    assert vectors.shape[0] == len(ids) == 2


def test_radial_glyph_from_features_normalizes():
    vec = np.array([1.0, 2.0, 0.5])
    names = ["a", "b", "c"]
    glyph = radial_glyph_from_features(vec, names, scale=2.0)
    assert len(glyph.vertices) == 3
    assert glyph.metadata["feature_names"] == names


def test_build_genre_hulls():
    # Create two simple tetrahedrons for two genres
    coords = pd.DataFrame(
        {
            "x": [0, 1, 0, 1, 10, 11, 10, 11],
            "y": [0, 0, 1, 1, 0, 0, 1, 1],
            "z": [0, 1, 1, 0, 0, 1, 1, 0],
            "label": ["rock", "rock", "rock", "rock", "jazz", "jazz", "jazz", "jazz"],
        }
    )
    hulls = build_genre_hulls(coords, label_col="label")
    assert "rock" in hulls and "jazz" in hulls
    assert hulls["rock"]["vertices"]


def test_edges_to_networkx_and_export(tmp_path):
    edges = [
        Edge(src="a", dst="b", type="SIMILAR_TO", weight=0.9, source="test", version="v1"),
        Edge(src="b", dst="c", type="HAS_TAG", weight=1.0, source="test", version="v1"),
    ]
    G = edges_to_networkx(edges)
    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 2

    out = tmp_path / "graph.json"
    export_node_link_json(edges, out)
    assert out.exists()
