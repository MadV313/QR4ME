import os
import json

# Load static fallback values from config.json
with open("config.json", "r") as f:
    file_config = json.load(f)

# Main CONFIG object used globally
CONFIG = {
    # Required secrets (env > fallback)
    "discord_token": os.getenv("DISCORD_BOT_TOKEN", file_config.get("discord_token")),
    "admin_channel_id": os.getenv("ADMIN_CHANNEL_ID", file_config.get("admin_channel_id")),

    # Admin roles from env (split by comma) or fallback list
    "admin_roles": (
        os.getenv("ADMIN_ROLE_IDS", "").split(",") if os.getenv("ADMIN_ROLE_IDS")
        else file_config.get("admin_roles", [])
    ),

    # Default object type if none is specified
    "default_object": file_config.get("default_object", "SmallProtectiveCase"),

    # Default QR build placement origin (if no guild override exists)
    "origin_position": file_config.get("origin_position", {
        "x": 5000.0,
        "y": 0.0,
        "z": 5000.0
    }),

    # Default output paths (used as fallback in single-server mode or during init)
    "preview_output_path": file_config.get("preview_output_path", "previews/qr_preview.png"),
    "object_output_path": file_config.get("object_output_path", "data/objects.json"),
    "zip_output_path": file_config.get("zip_output_path", "outputs/qr_code.zip"),

    # Gallery URL override
    "gallery_url": file_config.get("gallery_url", os.getenv("GALLERY_URL", "")),

    # Static permitted users fallback
    "permitted_users": [str(uid) for uid in file_config.get("permitted_users", [])],

    # ✅ Toggle for including the mirror kit object behind the QR
    "include_mirror_kit": file_config.get("include_mirror_kit", False)
}
