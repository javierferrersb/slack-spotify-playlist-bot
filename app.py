import json
import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from helpers.spotify import add_song_to_playlist

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")

# Initialize Flask app
app = Flask(__name__)
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Initialize Slack client
slack_events_adapter = SlackEventAdapter(
    SLACK_SIGNING_SECRET, "/slack/events", app)
client = slack.WebClient(token=SLACK_BOT_TOKEN)

BOT_ID = client.api_call("auth.test")["user_id"]

# Define emojis
LOADING = "hourglass_flowing_sand"
DONE = "white_check_mark"
BOT_NAME = "Javier's Super Awesome Spotify Bot"
BOT_ICON = ":robot_face:"
PLAYLIST_ID = os.getenv("PLAYLIST_ID")


@slack_events_adapter.on('message')
def handle_message(payload):
    event = payload.get('event', {})
    channel_id = event.get('channel')
    user_id = event.get('user')

    if user_id == BOT_ID or user_id is None:
        return

    client.reactions_add(
        channel=channel_id,
        name=LOADING,
        timestamp=event.get('ts')
    )

    print("Event received:", event)
    print("Channel ID:", channel_id)

    # Ignore messages from the bot itself
    if user_id == BOT_ID:
        return

    song_input = event['text']
    added = add_song_to_playlist(song_input)
    if added:
        client.reactions_remove(
            channel=channel_id,
            name=LOADING,
            timestamp=event.get('ts')
        )
        client.reactions_add(
            channel=channel_id,
            name=DONE,
            timestamp=event.get('ts')
        )
    else:
        client.reactions_remove(
            channel=channel_id,
            name=LOADING,
            timestamp=event.get('ts')
        )


if __name__ == "__main__":
    app.run(debug=DEBUG, port=5000)
