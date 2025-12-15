import numpy as np
import pandas as pd

from classically_punk.features.projection import project_with_umap


def test_project_with_umap_returns_coordinates():
    # Create a tiny linearly separable dataset with labels
    data = []
    for i in range(10):
        data.append({"label": "rock", "feat1": 2 + 0.1 * i, "feat2": 0.1})
    for i in range(10):
        data.append({"label": "jazz", "feat1": 0.1, "feat2": 2 + 0.1 * i})
    df = pd.DataFrame(data)

    coords_df, mapper = project_with_umap(df, target_col="label", n_components=2, n_neighbors=5, random_state=0)

    assert coords_df.shape[0] == df.shape[0]
    assert {"label", "x", "y"}.issubset(coords_df.columns)
    assert np.isfinite(coords_df[["x", "y"]].values).all()
    assert mapper.n_components == 2
