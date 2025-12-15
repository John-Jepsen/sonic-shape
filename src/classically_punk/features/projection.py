"""
Projection utilities for map-like visualizations.

Generates low-dimensional coordinates (UMAP) from feature DataFrames so genres,
artists, or tracks can be plotted similarly to EveryNoise.
"""

from __future__ import annotations

from typing import Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
import umap


def select_feature_matrix(df: pd.DataFrame, target_col: str = "label") -> Tuple[pd.DataFrame, List[str]]:
    feature_cols = [c for c in df.columns if c not in {target_col, "path"}]
    return df[feature_cols], feature_cols


def project_with_umap(
    df: pd.DataFrame,
    target_col: str = "label",
    n_components: int = 2,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    metric: str = "euclidean",
    random_state: int = 42,
) -> Tuple[pd.DataFrame, umap.UMAP]:
    """
    Fit UMAP on numeric feature columns and return coords merged with id/label metadata.
    """
    X, feature_cols = select_feature_matrix(df, target_col=target_col)
    if X.empty:
        raise ValueError("No feature columns available for projection.")

    mapper = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
    )
    coords = mapper.fit_transform(X.values)

    coord_cols = ["x", "y", "z"][:n_components]
    coords_df = pd.DataFrame(coords, columns=coord_cols, index=df.index)

    meta_cols: List[str] = []
    if "path" in df.columns:
        meta_cols.append("path")
    if target_col in df.columns:
        meta_cols.append(target_col)

    result = pd.concat([df[meta_cols], coords_df], axis=1)
    return result, mapper

