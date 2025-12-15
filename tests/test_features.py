import numpy as np
import soundfile as sf

from classically_punk.features.audio import extract_feature_vector, featurize_dataset


def _sine_wave(freq: float = 440.0, duration: float = 2.0, sr: int = 22_050) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * freq * t)


def test_extract_feature_vector_shapes():
    y = _sine_wave()
    vector, names = extract_feature_vector(y, sr=22_050, n_mfcc=20)

    assert vector.shape[0] == len(names) == 36
    assert np.isfinite(vector).all()


def test_featurize_dataset_roundtrip(tmp_path):
    audio = _sine_wave(duration=1.0)
    wav_path = tmp_path / "rock" / "clip.wav"
    wav_path.parent.mkdir(parents=True)
    sf.write(wav_path, audio, 22_050)

    rows = [{"path": wav_path, "label": "rock"}]
    df = featurize_dataset(rows, sr=22_050, duration=1.0, n_mfcc=13)

    expected_feature_count = 4 + 12 + 13  # tempo, zcr, centroid, rolloff, chroma, mfcc
    assert df.shape[0] == 1
    assert df.filter(regex="mfcc_mean").shape[1] == 13
    assert df.columns.difference(["path", "label"]).size == expected_feature_count
    assert df.iloc[0]["label"] == "rock"
