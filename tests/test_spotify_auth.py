from classically_punk.ingest.spotify_auth import build_auth_url


def test_build_auth_url_contains_params():
    url = build_auth_url("cid", "http://localhost/callback", "user-library-read", state="xyz", show_dialog=True)
    assert "client_id=cid" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%2Fcallback" in url
    assert "scope=user-library-read" in url
    assert "state=xyz" in url
    assert "show_dialog=true" in url
