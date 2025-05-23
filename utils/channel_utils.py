import json
import os

CHANNELS_FILE = "data/channels.json"

def load_channels():
    if not os.path.exists(CHANNELS_FILE):
        return {}
    with open(CHANNELS_FILE, "r") as f:
        return json.load(f)

def save_channel(channel_type: str, channel_id: str, server_id: str):
    os.makedirs(os.path.dirname(CHANNELS_FILE), exist_ok=True)
    data = load_channels()

    if server_id not in data:
        data[server_id] = {}

    data[server_id][channel_type] = channel_id

    with open(CHANNELS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_channel_id(channel_type: str, server_id: str) -> str | None:
    data = load_channels()
    server_data = data.get(server_id, {})
    return server_data.get(channel_type)
