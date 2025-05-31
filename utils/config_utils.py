import json
import os

CONFIGS_FILE = "data/guild_configs.json"

DEFAULTS = {
    "origin_position": {"x": 5000.0, "y": 0.0, "z": 5000.0},
    "preview_output_path": "previews/{guild_id}_preview.png",
    "zip_output_path": "outputs/{guild_id}_qr.zip",
    "object_output_path": "data/objects_{guild_id}.json",
    "originOffset": {"x": 0.0, "y": 0.0, "z": 0.0},
    "defaultScale": 0.5,
    "defaultSpacing": 1.0,
    "selected_map": "Chernarus",
    "map_coordinates": {"x": 5000.0, "y": 0.0, "z": 5000.0},
    "custom_spacing": {},
    "custom_scale": {}
}

def get_guild_config(guild_id: int) -> dict:
    """
    Load per-guild configuration. Fills in any missing keys with defaults.
    """
    os.makedirs("data", exist_ok=True)
    guild_id_str = str(guild_id)

    try:
        with open(CONFIGS_FILE, "r") as f:
            all_configs = json.load(f)
    except FileNotFoundError:
        all_configs = {}

    config = all_configs.get(guild_id_str, {})

    updated = False
    for key, value in DEFAULTS.items():
        if key not in config:
            config[key] = value if not isinstance(value, str) else value.format(guild_id=guild_id_str)
            updated = True

    if updated:
        all_configs[guild_id_str] = config
        with open(CONFIGS_FILE, "w") as f:
            json.dump(all_configs, f, indent=2)

    return config

def save_guild_config(guild_id: int, updated_config: dict) -> None:
    """
    Save the updated config dictionary for a guild back to the config file.
    """
    os.makedirs("data", exist_ok=True)
    guild_id_str = str(guild_id)

    try:
        with open(CONFIGS_FILE, "r") as f:
            all_configs = json.load(f)
    except FileNotFoundError:
        all_configs = {}

    all_configs[guild_id_str] = updated_config
    with open(CONFIGS_FILE, "w") as f:
        json.dump(all_configs, f, indent=2)
