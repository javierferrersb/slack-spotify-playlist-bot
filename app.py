import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter
from helpers.spotify import add_song_to_playlist

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Slack API credentials
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Initialize Flask app
app = Flask(__name__)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Initialize Slack client
slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app)
client = slack.WebClient(token=SLACK_BOT_TOKEN)

# Get bot ID
BOT_ID = client.api_call("auth.test")["user_id"]

# Define emojis
LOADING = "hourglass_flowing_sand"
DONE = "white_check_mark"


@slack_events_adapter.on('message')
def handle_message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')
    timestamp = event.get('ts')

    if (DEBUG):
        print("Received message: ", event)

    # Ignore messages from the bot itself
    if user_id == BOT_ID or user_id is None:
        return

    # Ignore messages in threads
    if event.get('thread_ts'):
        return

    # Add loading emoji
    client.reactions_add(
        channel=channel_id,
        name=LOADING,
        timestamp=timestamp
    )

    # Get the first line of the message as the song input
    input = event['text']
    song_input = input.split("\n")[0]

    # Add song to playlist
    added = add_song_to_playlist(song_input)

    if added:
        # Add done emoji
        client.reactions_add(
            channel=channel_id,
            name=DONE,
            timestamp=timestamp
        )

    # Remove loading emoji
    client.reactions_remove(
        channel=channel_id,
        name=LOADING,
        timestamp=timestamp
    )


if __name__ == "__main__":
    app.run(debug=DEBUG, port=5000)
