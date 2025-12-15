"""
Spotify OAuth helper utilities.

Supports building auth URLs, exchanging auth codes for tokens, and refreshing
access tokens. Store tokens securely (e.g., .env, secret manager); do not commit.
"""

from __future__ import annotations

import base64
import os
import time
import urllib.parse
from typing import Dict, Optional

import requests

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


def build_auth_url(
    client_id: str,
    redirect_uri: str,
    scope: str,
    state: str = "classically-punk",
    show_dialog: bool = False,
) -> str:
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "show_dialog": "true" if show_dialog else "false",
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def _basic_auth_header(client_id: str, client_secret: str) -> Dict[str, str]:
    token = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def exchange_code_for_token(
    client_id: str, client_secret: str, code: str, redirect_uri: str
) -> Dict[str, object]:
    """
    Exchange authorization code for access and refresh tokens.
    """
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    headers = _basic_auth_header(client_id, client_secret)
    resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
    resp.raise_for_status()
    token_data = resp.json()
    token_data["expires_at"] = int(time.time()) + int(token_data.get("expires_in", 3600))
    return token_data


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> Dict[str, object]:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    headers = _basic_auth_header(client_id, client_secret)
    resp = requests.post(TOKEN_URL, data=data, headers=headers, timeout=30)
    resp.raise_for_status()
    token_data = resp.json()
    token_data["refresh_token"] = token_data.get("refresh_token", refresh_token)
    token_data["expires_at"] = int(time.time()) + int(token_data.get("expires_in", 3600))
    return token_data


class EnvTokenStore:
    """
    Loads tokens from environment variables.
    Expected vars: SPOTIFY_ACCESS_TOKEN (optional), SPOTIFY_REFRESH_TOKEN (recommended), SPOTIFY_EXPIRES_AT (epoch seconds).
    """

    def load(self) -> Dict[str, object]:
        token = os.environ.get("SPOTIFY_ACCESS_TOKEN")
        refresh = os.environ.get("SPOTIFY_REFRESH_TOKEN")
        expires_at = os.environ.get("SPOTIFY_EXPIRES_AT")
        data: Dict[str, object] = {}
        if token:
            data["access_token"] = token
        if refresh:
            data["refresh_token"] = refresh
        if expires_at:
            data["expires_at"] = int(expires_at)
        return data

    def save(self, data: Dict[str, object]) -> None:
        # No-op for env store; user can export manually.
        return None


class FileTokenStore:
    """
    Persists tokens to a local JSON file (gitignored).
    """

    def __init__(self, path: str = "data_samples/spotify_tokens.json"):
        self.path = path

    def load(self) -> Dict[str, object]:
        if not os.path.exists(self.path):
            return {}
        import json

        with open(self.path, "r") as f:
            return json.load(f)

    def save(self, data: Dict[str, object]) -> None:
        import json
        import pathlib

        pathlib.Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(data, f)
