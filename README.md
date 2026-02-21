# Slack to Spotify Bot

A simple Slack bot that listens for song recommendations in a Slack channel and automatically adds them to a Spotify playlist!

## Features

- Listens for messages in a specified Slack channel.
- Extracts song name and artist from messages formatted as `song name - artist` from the first line of the message.
- Adds the song to a predefined Spotify playlist.
- Reacts with emojis to indicate processing status.

## Setup

### Prerequisites

- Python 3.7+
- A Slack workspace with a bot token.
- A Spotify Developer account with API credentials.

### Installation

1. Clone the repository:

   ```sh
   git clone https://github.com/javierferrersb/slack-spotify-playlist-bot.git
   cd slack-spotify-playlist-bot
   ```

2. Create and activate a virtual environment:

   ```sh
   python3 -m venv .venv
   ```

   - On Linux/macOS:
     ```sh
     source .venv/bin/activate
     ```
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```

3. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your credentials:

   ```ini
   SLACK_BOT_TOKEN=your-slack-bot-token
   SLACK_SIGNING_SECRET=your-slack-signing-secret
   SPOTIPY_CLIENT_ID=your-spotify-client-id
   SPOTIPY_CLIENT_SECRET=your-spotify-client-secret
   SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
   PLAYLIST_ID=your-spotify-playlist-id
   SPOTIFY_AUTH_CACHE=generated-json-token-cache
   ```

   Note: Do not use `localhost` for Spotify redirect URI. Use loopback IP such as
   `http://127.0.0.1:8888/callback` in both your Spotify app dashboard and `.env`.

5. Generate `SPOTIFY_AUTH_CACHE`:

   The bot reads Spotify token data from `SPOTIFY_AUTH_CACHE`. Use the helper script to generate it.

   ```sh
   python scripts/get_spotify_auth_cache.py
   ```

   The script will:
   - Open (or print) the Spotify authorization URL.
   - Ask you to paste the full redirect URL after approving access.
   - Print a ready-to-paste line in this format:

   ```ini
   SPOTIFY_AUTH_CACHE={"access_token":"...","token_type":"Bearer","expires_in":3600,"refresh_token":"...","scope":"playlist-modify-public playlist-modify-private","expires_at":1234567890}
   ```

   You can also write/update `.env` automatically:

   ```sh
   python scripts/get_spotify_auth_cache.py --write-env
   ```

## Running the Bot

Start the Flask server:

```sh
python app.py
```

The bot will listen for messages in the Slack channel and process song requests automatically.

## How It Works

1. A user posts a message in the format `song name - artist`.
2. The bot adds a ⏳ (loading) emoji to indicate processing.
3. It searches for the song on Spotify and adds it to the playlist.
4. If successful, the bot replaces ⏳ with ✅ (done) emoji.

## Contributing

Feel free to fork this project and submit pull requests with improvements!

## License

This project is open-source and available under the MIT License.
