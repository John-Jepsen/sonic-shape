"""
Baseline modeling utilities for genre classification.

Provides simple train/test splitting, scaling, and a multinomial logistic
regression classifier suitable for quick baselines on extracted features.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def _split_features_targets(
    df: pd.DataFrame, target_col: str = "label"
) -> Tuple[pd.DataFrame, pd.Series, List[str]]:
    feature_cols = [c for c in df.columns if c not in {target_col, "path"}]
    X = df[feature_cols]
    y = df[target_col]
    return X, y, feature_cols


def train_baseline_classifier(
    df: pd.DataFrame,
    target_col: str = "label",
    test_size: float = 0.2,
    random_state: int = 42,
):
    """
    Train a scaled multinomial logistic regression classifier on feature DataFrame.
    Returns the fitted pipeline, X_test, and y_test for evaluation.
    """
    X, y, _ = _split_features_targets(df, target_col=target_col)
    stratify = y if len(y.unique()) > 1 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    clf = Pipeline(
        steps=[
            ("scale", StandardScaler()),
            (
                "logreg",
                LogisticRegression(
                    max_iter=1000,
                    multi_class="auto",
                    n_jobs=None,
                    solver="lbfgs",
                ),
            ),
        ]
    )
    clf.fit(X_train, y_train)
    return clf, X_test, y_test


def evaluate_classifier(clf, X_test: pd.DataFrame, y_test: Iterable) -> dict:
    """
    Evaluate a fitted classifier and return metrics.
    """
    y_pred = clf.predict(X_test)
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "f1_macro": float(f1_score(y_test, y_pred, average="macro")),
        "report": classification_report(y_test, y_pred, output_dict=False),
    }

