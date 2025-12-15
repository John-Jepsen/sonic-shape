"""
Audio feature extraction utilities.

Converts raw waveforms into fixed-length numeric feature vectors suited for
baseline genre classification and visualization.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Union

import numpy as np
import pandas as pd
import librosa


def _feature_names(n_mfcc: int = 20) -> List[str]:
    names = ["tempo", "zcr_mean", "centroid_mean", "rolloff_mean"]
    names += [f"chroma_mean_{i}" for i in range(12)]
    names += [f"mfcc_mean_{i}" for i in range(n_mfcc)]
    return names


def extract_feature_vector(y: np.ndarray, sr: int, n_mfcc: int = 20) -> Tuple[np.ndarray, List[str]]:
    """
    Compute a compact feature vector from a mono waveform.
    """
    if y.size == 0:
        raise ValueError("Waveform is empty.")

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    zcr = librosa.feature.zero_crossing_rate(y=y)
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)

    vector_parts = [
        np.array([tempo], dtype=float),
        np.array([zcr.mean()], dtype=float),
        np.array([centroid.mean()], dtype=float),
        np.array([rolloff.mean()], dtype=float),
        chroma.mean(axis=1),
        mfcc.mean(axis=1),
    ]

    vector = np.concatenate(vector_parts)
    vector = np.nan_to_num(vector, nan=0.0, posinf=0.0, neginf=0.0)
    return vector, _feature_names(n_mfcc=n_mfcc)


def extract_from_file(
    path: Union[str, Path],
    sr: int = 22_050,
    duration: float | None = 30.0,
    n_mfcc: int = 20,
) -> Tuple[np.ndarray, List[str]]:
    """
    Load an audio file and return its feature vector.
    """
    y, out_sr = librosa.load(path, sr=sr, mono=True, duration=duration)
    return extract_feature_vector(y, out_sr, n_mfcc=n_mfcc)


def featurize_dataset(
    rows: Iterable[Dict[str, object]],
    sr: int = 22_050,
    duration: float | None = 30.0,
    n_mfcc: int = 20,
) -> pd.DataFrame:
    """
    Given an iterable of rows with 'path' and optional 'label', return a feature DataFrame.
    """
    records: List[Dict[str, object]] = []
    names = _feature_names(n_mfcc=n_mfcc)

    for row in rows:
        path = row["path"]
        label = row.get("label")
        vector, _ = extract_from_file(path, sr=sr, duration=duration, n_mfcc=n_mfcc)
        record: Dict[str, object] = {"path": str(path), "label": label}
        record.update({name: float(value) for name, value in zip(names, vector)})
        records.append(record)

    return pd.DataFrame.from_records(records)

