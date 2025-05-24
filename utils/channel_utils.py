import json
import os

CHANNELS_FILE = "data/channels.json"

def load_channels():
    """Load all channel mappings from the JSON file."""
    if not os.path.exists(CHANNELS_FILE):
        return {}
    with open(CHANNELS_FILE, "r") as f:
        return json.load(f)

def save_channel(server_id: str, channel_type: str, channel_id: str):
    """Save a specific channel type (admin, gallery, log) for a given server ID."""
    os.makedirs(os.path.dirname(CHANNELS_FILE), exist_ok=True)
    data = load_channels()

    if server_id not in data:
        data[server_id] = {}

    data[server_id][channel_type] = channel_id

    with open(CHANNELS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_channel_id(channel_type: str, server_id: str) -> str | None:
    """Retrieve a stored channel ID by type and server."""
    data = load_channels()
    return data.get(server_id, {}).get(channel_type)
