"""
Shape generation for genre/track visual encodings.

Provides utilities to turn audio features into glyphs and genre-level hulls for 3D
visualizations. Export targets include JSON (for three.js/Plotly) and numpy arrays
for plotting.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull


@dataclass
class Glyph:
    id: str
    vertices: List[Tuple[float, float, float]]
    metadata: Dict[str, object]

    def to_json(self) -> Dict[str, object]:
        return {"id": self.id, "vertices": self.vertices, "metadata": self.metadata}


def radial_glyph_from_features(
    feature_vector: np.ndarray,
    feature_names: Sequence[str],
    scale: float = 1.0,
    height_idx: int | None = None,
) -> Glyph:
    """
    Create a 3D radial glyph from a feature vector.

    - Radius per spoke is proportional to feature value (normalized).
    - Optional height dimension (e.g., loudness/brightness) if height_idx is provided.
    """
    vec = np.array(feature_vector, dtype=float)
    if vec.ndim != 1:
        raise ValueError("feature_vector must be 1D")

    n = len(vec)
    radii = vec / (np.max(np.abs(vec)) + 1e-8) * scale

    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    vertices = []
    for i, (r, theta) in enumerate(zip(radii, angles)):
        z = float(vec[height_idx]) if height_idx is not None else 0.0
        x = float(r * np.cos(theta))
        y = float(r * np.sin(theta))
        vertices.append((x, y, z))

    return Glyph(
        id="glyph",
        vertices=vertices,
        metadata={"feature_names": list(feature_names)},
    )


def genre_hull(embeddings: np.ndarray) -> Dict[str, object]:
    """
    Compute a convex hull around 3D embeddings for a genre cluster.
    """
    if embeddings.shape[0] < 4 or embeddings.shape[1] != 3:
        raise ValueError("Need at least 4 points in 3D for a convex hull.")
    hull = ConvexHull(embeddings)
    return {
        "vertices": embeddings.tolist(),
        "simplices": hull.simplices.tolist(),
        "volume": float(hull.volume),
        "area": float(hull.area),
    }


def build_genre_hulls(projection_df: pd.DataFrame, label_col: str = "label") -> Dict[str, Dict[str, object]]:
    """
    Given a projection DataFrame with x,y,z and labels, build hulls per genre.
    """
    required = {"x", "y", "z", label_col}
    if not required.issubset(projection_df.columns):
        raise ValueError("Projection DataFrame must have x,y,z and label columns.")

    hulls: Dict[str, Dict[str, object]] = {}
    for label, grp in projection_df.groupby(label_col):
        coords = grp[["x", "y", "z"]].to_numpy()
        if coords.shape[0] < 4:
            continue
        try:
            hulls[label] = genre_hull(coords)
        except Exception:
            continue
    return hulls


def hulls_to_json(hulls: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """
    Convert hull dict to JSON-serializable form for frontend consumption.
    """
    return {label: hull for label, hull in hulls.items()}
