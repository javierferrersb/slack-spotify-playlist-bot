import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler
from dotenv import load_dotenv
import logging
import os
import json

logger = logging.getLogger(__name__)

load_dotenv()

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
PLAYLIST_ID = os.getenv("PLAYLIST_ID")


class EnvCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in environment variables.
    """

    def __init__(self, env_var="SPOTIFY_AUTH_CACHE"):
        """
        Parameters:
            * env_var: The environment variable used to store the token.
        """
        self.env_var = env_var

    def get_cached_token(self):
        """
        Retrieve the token from the environment variable.
        """
        token_info = None
        try:
            token_info_str = os.getenv(self.env_var)
            if token_info_str:
                token_info = json.loads(token_info_str)
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(
                f"Error decoding token from environment variable {self.env_var}: {e}")

        return token_info

    def save_token_to_cache(self, token_info):
        """
        Store the token in the environment variable.
        """
        try:
            os.environ[self.env_var] = json.dumps(token_info)
        except Exception as e:
            logger.warning(
                f"Error saving token to environment variable {self.env_var}: {e}")


# Authenticate
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="playlist-modify-public playlist-modify-private",
    cache_handler=EnvCacheHandler()  # Use env variable instead of a file
))


def add_song_to_playlist(song_input):
    try:
        song_name, artist = map(str.strip, song_input.split('-'))
    except ValueError:
        print("Invalid format. Use 'song name - artist'.")
        return

    # Search for the song
    results = sp.search(
        q=f"track:{song_name} artist:{artist}", type="track", limit=1)
    tracks = results.get("tracks", {}).get("items", [])

    if not tracks:
        print("Song not found on Spotify.")
        return

    track_id = tracks[0]['id']
    sp.playlist_add_items(PLAYLIST_ID, [track_id])
    return True


if __name__ == "__main__":
    user_input = input("Enter song (format: 'song name - artist'): ")
    result = add_song_to_playlist(user_input)
    if result:
        print("Song added successfully.")
