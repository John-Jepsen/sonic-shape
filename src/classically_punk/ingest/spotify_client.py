"""
Spotify client scaffolding using async HTTP (httpx).

Provides OAuth-aware, rate-limited fetches for artists, tracks, playlists, and
audio features. The client refreshes tokens automatically when a refresh token
is available.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Dict, Optional

import httpx

from classically_punk.ingest.spotify_auth import refresh_access_token


@dataclass
class SpotifyAuthConfig:
    client_id: str
    client_secret: str
    redirect_uri: str
    scope: str = "user-library-read playlist-read-private"


class SpotifyClient:
    """
    Spotify Web API client with token refresh and basic rate limiting.
    """

    def __init__(self, auth_config: SpotifyAuthConfig, token_store, http_client: Optional[httpx.AsyncClient] = None):
        self.auth_config = auth_config
        self.token_store = token_store  # inject storage (file/env/secrets manager)
        self.http = http_client or httpx.AsyncClient(base_url="https://api.spotify.com/v1", timeout=30)

    async def ensure_token(self) -> Dict[str, str]:
        """Retrieve a valid access token; refresh if expired and refresh token available."""
        tokens = self.token_store.load()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_at = tokens.get("expires_at")
        now = time.time()

        if access_token and expires_at and now < expires_at - 60:
            return tokens

        if refresh_token:
            refreshed = refresh_access_token(
                client_id=self.auth_config.client_id,
                client_secret=self.auth_config.client_secret,
                refresh_token=refresh_token,
            )
            if hasattr(self.token_store, "save"):
                try:
                    self.token_store.save(refreshed)  # type: ignore
                except Exception:
                    pass
            return refreshed

        # Fallback to whatever we have
        if access_token:
            return tokens
        raise RuntimeError("No access token available. Set SPOTIFY_ACCESS_TOKEN or provide refresh flow.")

    async def get(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict:
        """
        Rate-limited GET with retry on 429.
        """
        url = path if path.startswith("http") else f"/{path.lstrip('/')}"
        token = await self.ensure_token()
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        resp = await self.http.get(url, params=params or {}, headers=headers)
        if resp.status_code == 429:
            retry_after = int(resp.headers.get("Retry-After", "1"))
            await asyncio.sleep(retry_after)
            return await self.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def list_user_playlists(self, limit: int = 50) -> Dict:
        return await self.get("me/playlists", params={"limit": limit})

    async def list_playlist_items(self, playlist_id: str, limit: int = 100) -> Dict:
        return await self.get(f"playlists/{playlist_id}/tracks", params={"limit": limit})

    async def list_saved_tracks(self, limit: int = 50) -> Dict:
        return await self.get("me/tracks", params={"limit": limit})

    async def get_audio_features(self, track_ids: list[str]) -> Dict:
        joined = ",".join(track_ids)
        return await self.get("audio-features", params={"ids": joined})

    async def close(self):
        await self.http.aclose()
