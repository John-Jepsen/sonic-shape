"""
3D projection and surface utilities for audio features and embeddings.

Exports Plotly-friendly data for interactive rendering, plus helper functions for
static matplotlib/plotly generation.
"""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from sklearn.neighbors import KernelDensity

from classically_punk.features.projection import project_with_umap


def project_3d(df: pd.DataFrame, target_col: str = "label", **umap_kwargs) -> Tuple[pd.DataFrame, object]:
    """
    Produce a 3D UMAP projection (n_components=3) and return coords+labels.
    """
    umap_kwargs.setdefault("n_components", 3)
    coords_df, mapper = project_with_umap(df, target_col=target_col, **umap_kwargs)
    return coords_df, mapper


def kde_density_surface(coords: np.ndarray, bandwidth: float = 0.5, grid_size: int = 30) -> Dict[str, np.ndarray]:
    """
    Estimate a 3D density over projected coordinates and return a mesh grid.
    """
    kde = KernelDensity(bandwidth=bandwidth, kernel="gaussian")
    kde.fit(coords)

    mins = coords.min(axis=0)
    maxs = coords.max(axis=0)
    xs = np.linspace(mins[0], maxs[0], grid_size)
    ys = np.linspace(mins[1], maxs[1], grid_size)
    zs = np.linspace(mins[2], maxs[2], grid_size)
    xx, yy, zz = np.meshgrid(xs, ys, zs, indexing="ij")
    grid_points = np.vstack([xx.ravel(), yy.ravel(), zz.ravel()]).T
    log_dens = kde.score_samples(grid_points)
    dens = np.exp(log_dens).reshape(xx.shape)
    return {"xx": xx, "yy": yy, "zz": zz, "density": dens}


def plotly_scatter3d(coords_df: pd.DataFrame, label_col: str = "label") -> go.Figure:
    """
    Build a Plotly 3D scatter figure from projected coordinates.
    """
    fig = go.Figure()
    for label, grp in coords_df.groupby(label_col):
        fig.add_trace(
            go.Scatter3d(
                x=grp["x"],
                y=grp["y"],
                z=grp["z"],
                mode="markers",
                name=str(label),
                marker=dict(size=3),
                text=grp.get("path"),
            )
        )
    fig.update_layout(scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z"))
    return fig


def plotly_isosurface(density_mesh: Dict[str, np.ndarray], iso_threshold: float = 0.1) -> go.Figure:
    """
    Build a Plotly isosurface figure from KDE density mesh.
    """
    xx = density_mesh["xx"]
    yy = density_mesh["yy"]
    zz = density_mesh["zz"]
    density = density_mesh["density"]
    fig = go.Figure(
        data=go.Isosurface(
            x=xx.ravel(),
            y=yy.ravel(),
            z=zz.ravel(),
            value=density.ravel(),
            isomin=iso_threshold,
            isomax=density.max(),
            surface_count=4,
            caps=dict(x_show=False, y_show=False, z_show=False),
        )
    )
    fig.update_layout(scene=dict(xaxis_title="x", yaxis_title="y", zaxis_title="z"))
    return fig

