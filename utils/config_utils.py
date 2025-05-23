import json
import os

DEFAULT_PREVIEW_PATH = "outputs/preview.png"
DEFAULT_ZIP_PATH = "outputs/preview_build.zip"

CONFIGS_FILE = "data/guild_configs.json"

def get_guild_config(guild_id: int) -> dict:
    """
    Load per-guild configuration. Falls back to default if not found.
    """
    try:
        with open(CONFIGS_FILE, "r") as f:
            all_configs = json.load(f)
    except FileNotFoundError:
        all_configs = {}

    guild_id_str = str(guild_id)
    config = all_configs.get(guild_id_str, {})

    return {
        "preview_output_path": config.get("preview_output_path", DEFAULT_PREVIEW_PATH),
        "zip_output_path": config.get("zip_output_path", DEFAULT_ZIP_PATH),
        "object_output_path": config.get("object_output_path", "data/output_build.json")
    }
