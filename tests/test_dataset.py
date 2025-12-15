from classically_punk.data.dataset import index_labeled_folders, list_audio_files


def test_list_audio_files_filters_extensions(tmp_path):
    audio_dir = tmp_path / "jazz"
    audio_dir.mkdir()
    target = audio_dir / "track.wav"
    target.touch()
    (audio_dir / "ignore.txt").touch()

    found = list_audio_files(tmp_path)
    assert target in found
    assert all(p.suffix in {".wav", ".mp3", ".flac", ".ogg", ".aiff", ".aif"} for p in found)


def test_index_labeled_folders_returns_labels(tmp_path):
    genre_dir = tmp_path / "classical"
    genre_dir.mkdir()
    audio_path = genre_dir / "example.wav"
    audio_path.touch()

    rows = index_labeled_folders(tmp_path)
    assert rows == [{"path": audio_path, "label": "classical"}]
