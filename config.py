import os
import json

# Optional fallback config from config.json
with open("config.json") as f:
    file_config = json.load(f)

CONFIG = {
    # Required secrets pulled from Railway environment
    "discord_token": os.getenv("DISCORD_BOT_TOKEN"),
    "admin_channel_id": os.getenv("ADMIN_CHANNEL_ID"),
    "admin_roles": os.getenv("ADMIN_ROLE_IDS", "").split(",") if os.getenv("ADMIN_ROLE_IDS") else file_config.get("admin_roles", []),

    # Configurable object logic
    "default_object": file_config.get("default_object", "SmallProtectiveCase"),
    "origin_position": file_config.get("origin_position", {
        "x": 5000.0,
        "y": 0.0,
        "z": 5000.0
    }),

    # File paths
    "preview_output_path": file_config.get("preview_output_path", "previews/qr_preview.png"),
    "object_output_path": file_config.get("object_output_path", "data/objects.json"),
    "zip_output_path": file_config.get("zip_output_path", "outputs/qr_code.zip"),

    # Optional: public gallery link
    "gallery_url": file_config.get("gallery_url", os.getenv("GALLERY_URL", "")),
}
