from classically_punk.ingest.spotify_client import SpotifyAuthConfig, SpotifyClient


def test_spotify_client_placeholder_get_can_be_overridden():
    class DummyTokenStore:
        def load(self):
            return {"access_token": "dummy", "token_type": "Bearer"}

    calls = []

    def fake_get(path, params=None):
        calls.append((path, params))
        return {"ok": True}

    client = SpotifyClient(SpotifyAuthConfig("id", "secret", "http://localhost"), DummyTokenStore())
    # override async method with sync stub for unit test
    client.get = fake_get  # type: ignore

    resp = client.get("me/playlists", {"limit": 5})  # type: ignore
    assert resp["ok"]
    assert calls == [("me/playlists", {"limit": 5})]
