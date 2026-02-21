import argparse
import json
import os
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from dotenv import load_dotenv
from spotipy.cache_handler import CacheHandler
from spotipy.exceptions import SpotifyOauthError
from spotipy.oauth2 import SpotifyOAuth

SCOPES = "playlist-modify-public playlist-modify-private"


class MemoryCacheHandler(CacheHandler):
    def __init__(self):
        self._token_info = None

    def get_cached_token(self):
        return self._token_info

    def save_token_to_cache(self, token_info):
        self._token_info = token_info


def update_env_var(env_path: Path, key: str, value: str) -> None:
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    key_prefix = f"{key}="
    replaced = False
    for index, line in enumerate(lines):
        if line.startswith(key_prefix):
            lines[index] = f"{key}={value}"
            replaced = True
            break

    if not replaced:
        lines.append(f"{key}={value}")

    env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value
    raise RuntimeError(f"Missing required environment variable: {name}")


def extract_code(user_input: str, oauth: SpotifyOAuth) -> str:
    parsed = urlparse(user_input)

    # If user pasted just the raw code from query params, accept it.
    if parsed.scheme == "" and parsed.netloc == "":
        if " " in user_input:
            raise RuntimeError(
                "Invalid code input. Paste only the raw code or full callback URL.")
        return user_input

    query = parse_qs(parsed.query)
    if "error" in query:
        error = query.get("error", ["unknown_error"])[0]
        description = query.get("error_description", [""])[0]
        raise RuntimeError(
            f"Spotify returned an OAuth error: {error} {description}".strip())

    code = oauth.parse_response_code(user_input)
    if code:
        return code

    raise RuntimeError(
        "Could not parse auth code. Paste the full callback URL (the one your app redirects to) "
        "or paste only the `code` value from that URL."
    )


def warn_redirect_uri(redirect_uri: str) -> None:
    parsed = urlparse(redirect_uri)
    host = parsed.hostname or ""

    if host == "localhost":
        print(
            "\nWarning: Spotify no longer accepts localhost redirect URIs in this flow.\n"
            "Use a loopback IP instead, e.g. http://127.0.0.1:8888/callback,\n"
            "and update it in both Spotify Dashboard and your .env."
        )

    if parsed.scheme == "http" and host not in ("127.0.0.1", "::1"):
        print(
            "\nWarning: Non-loopback HTTP redirect URI detected.\n"
            "Spotify may reject this as insecure. Prefer HTTPS, or use loopback "
            "http://127.0.0.1:<port>/callback for local development."
        )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate SPOTIFY_AUTH_CACHE for .env using Spotify OAuth."
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to env file with Spotify app credentials (default: .env).",
    )
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="Write/update SPOTIFY_AUTH_CACHE inside the env file.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not auto-open the authorization URL.",
    )
    args = parser.parse_args()

    env_path = Path(args.env_file)
    load_dotenv(dotenv_path=env_path)

    client_id = require_env("SPOTIPY_CLIENT_ID")
    client_secret = require_env("SPOTIPY_CLIENT_SECRET")
    redirect_uri = require_env("SPOTIPY_REDIRECT_URI")

    cache_handler = MemoryCacheHandler()
    oauth = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPES,
        cache_handler=cache_handler,
        open_browser=not args.no_browser,
    )

    auth_url = oauth.get_authorize_url()
    print("Open this URL and authorize the app:")
    print(auth_url)
    print("\nSPOTIPY_REDIRECT_URI currently set to:")
    print(redirect_uri)
    print(
        "\nImportant: This URI must exactly match one Redirect URI configured "
        "in your Spotify app dashboard."
    )
    warn_redirect_uri(redirect_uri)

    if not args.no_browser:
        try:
            webbrowser.open(auth_url)
        except Exception as exc:
            print(f"Warning: Failed to open web browser automatically: {exc}")
            print("Please open the authorization URL shown above manually in your browser.")

    response_input = input(
        "\nPaste the full redirect URL here (or just the `code` value): "
    ).strip()
    code = extract_code(response_input, oauth)

    try:
        oauth.get_access_token(code=code, check_cache=False)
        token_info = oauth.get_cached_token()
    except SpotifyOauthError as exc:
        raise RuntimeError(
            "Spotify OAuth failed. Common causes:\n"
            "1) The redirect URI is not allowed by Spotify.\n"
            "2) The redirect URI in .env does not exactly match your app dashboard.\n"
            "3) You pasted the authorize URL instead of the callback URL/code.\n"
            f"Details: {exc}"
        ) from exc

    if not token_info:
        raise RuntimeError("Spotify did not return token data.")

    cache_json = json.dumps(token_info, separators=(",", ":"))

    print("\nSPOTIFY_AUTH_CACHE JSON:")
    print(cache_json)

    print("\nAdd this line to your .env:")
    print(f"SPOTIFY_AUTH_CACHE={cache_json}")

    if args.write_env:
        update_env_var(env_path, "SPOTIFY_AUTH_CACHE", cache_json)
        print(f"\nUpdated {env_path} with SPOTIFY_AUTH_CACHE.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
