"""
Schema and utilities for graph modeling.

Defines edge types and lightweight builders for genre/artist/track/tag graphs,
including kNN similarity edges and genre aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Literal, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

EdgeType = Literal[
    "SIMILAR_TO",
    "HAS_TAG",
    "IS_A",
    "IN_PLAYLIST",
    "PERFORMS",
    "SLANG_ALIAS",
    "LANG_VARIANT",
    "COVERS",
    "SAMPLES",
    "REMIXES",
]


@dataclass
class Edge:
    src: str
    dst: str
    type: EdgeType
    weight: float = 1.0
    source: str = "unknown"  # provenance
    version: str = "v1"


def build_knn_edges(
    embeddings: np.ndarray,
    ids: Sequence[str],
    k: int = 10,
    metric: str = "cosine",
    source: str = "embedding",
    version: str = "v1",
) -> List[Edge]:
    """
    Build SIMILAR_TO edges from embeddings using kNN.
    """
    if embeddings.shape[0] != len(ids):
        raise ValueError("embeddings and ids length mismatch")

    nn = NearestNeighbors(n_neighbors=min(k + 1, len(ids)), metric=metric)
    nn.fit(embeddings)
    distances, indices = nn.kneighbors(embeddings)

    edges: List[Edge] = []
    for i, src_id in enumerate(ids):
        for dist, j in zip(distances[i], indices[i]):
            if src_id == ids[j]:
                continue  # skip self
            weight = 1.0 - float(dist) if metric == "cosine" else float(1.0 / (1.0 + dist))
            edges.append(
                Edge(
                    src=src_id,
                    dst=ids[j],
                    type="SIMILAR_TO",
                    weight=weight,
                    source=source,
                    version=version,
                )
            )
    return edges


def aggregate_genre_embeddings(df: pd.DataFrame, target_col: str = "label") -> Tuple[pd.DataFrame, np.ndarray, List[str]]:
    """
    Aggregate track-level features/embeddings to genre-level centroids and covariance traces.
    """
    feature_cols = [c for c in df.columns if c not in {target_col, "path"}]
    if not feature_cols:
        raise ValueError("No feature columns to aggregate.")

    grouped = df.groupby(target_col)
    records = []
    ids = []
    vectors = []
    for genre, grp in grouped:
        vecs = grp[feature_cols].to_numpy()
        centroid = vecs.mean(axis=0)
        cov_trace = float(np.trace(np.cov(vecs, rowvar=False))) if vecs.shape[0] > 1 else 0.0
        records.append({"genre": genre, "cov_trace": cov_trace, **{f"feat_{i}": v for i, v in enumerate(centroid)}})
        ids.append(f"genre::{genre}")
        vectors.append(centroid)

    agg_df = pd.DataFrame(records)
    return agg_df, np.vstack(vectors), ids

