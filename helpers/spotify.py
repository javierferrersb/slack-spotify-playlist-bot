import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
PLAYLIST_ID = os.getenv("PLAYLIST_ID")


class EnvCacheHandler(CacheHandler):
    def get_cached_token(self):
        cache_data = os.getenv("SPOTIFY_AUTH_CACHE")
        return json.loads(cache_data) if cache_data else None

    def save_token_info(self, token_info):
        os.environ["SPOTIFY_AUTH_CACHE"] = json.dumps(token_info)


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
