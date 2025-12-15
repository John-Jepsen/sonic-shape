#!/usr/bin/env python
"""
Helper for Spotify OAuth:
  1) Print an authorization URL.
  2) Exchange an auth code for access + refresh tokens.

Usage:
  python scripts/spotify_oauth.py --step url --client-id ... --redirect-uri ... --scope "user-library-read playlist-read-private"
  python scripts/spotify_oauth.py --step exchange --client-id ... --client-secret ... --redirect-uri ... --code <auth_code>

Do NOT commit tokens; store in .env or a local gitignored file.
"""

from __future__ import annotations

import argparse
import json

from classically_punk.ingest.spotify_auth import build_auth_url, exchange_code_for_token


def main():
    parser = argparse.ArgumentParser(description="Spotify OAuth helper")
    parser.add_argument("--step", choices=["url", "exchange"], required=True)
    parser.add_argument("--client-id", required=True)
    parser.add_argument("--client-secret")
    parser.add_argument("--redirect-uri", required=True)
    parser.add_argument("--scope", default="user-library-read playlist-read-private")
    parser.add_argument("--code", help="Auth code from redirect when step=exchange")
    args = parser.parse_args()

    if args.step == "url":
        url = build_auth_url(args.client_id, args.redirect_uri, args.scope)
        print("Open this URL in your browser, authorize, and copy the 'code' param from the redirect:")
        print(url)
    else:
        if not args.client_secret:
            raise SystemExit("--client-secret is required for exchange step")
        if not args.code:
            raise SystemExit("--code is required for exchange step")
        tokens = exchange_code_for_token(args.client_id, args.client_secret, args.code, args.redirect_uri)
        print(json.dumps(tokens, indent=2))
        print("Store refresh_token, access_token, and expires_at in your environment or token store (do not commit).")


if __name__ == "__main__":
    main()
