import os
import json
import shutil
from datetime import datetime

GALLERY_ROOT = "public/gallery"
GALLERY_DATA_ROOT = "data/galleries"
LATEST_PREVIEW_JSON = "data/previews.json"
LATEST_OUTPUT_JSON = "data/output_build.json"

def save_to_gallery(preview_path, zip_path, metadata: dict, server_id: str = "unknown"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"{metadata['object_type']}_{timestamp}"

    # Create target folders per server
    gallery_dir = os.path.join(GALLERY_ROOT, server_id)
    os.makedirs(gallery_dir, exist_ok=True)

    # Target output paths
    preview_target = os.path.join(gallery_dir, f"{base_name}.png")
    zip_target = os.path.join(gallery_dir, f"{base_name}.zip")

    # Copy preview and zip into server folder
    shutil.copy(preview_path, preview_target)
    shutil.copy(zip_path, zip_target)

    # Load or initialize server-specific gallery JSON
    server_gallery_json = os.path.join(GALLERY_DATA_ROOT, f"gallery_{server_id}.json")
    os.makedirs(os.path.dirname(server_gallery_json), exist_ok=True)

    try:
        with open(server_gallery_json, "r") as f:
            gallery = json.load(f)
    except FileNotFoundError:
        gallery = []

    # Build gallery entry
    entry = {
        "image": f"gallery/{server_id}/{base_name}.png",
        "zip": f"gallery/{server_id}/{base_name}.zip",
        "object_type": metadata["object_type"],
        "qr_size": metadata["qr_size"],
        "total_objects": metadata["total_objects"],
        "created": timestamp
    }
    gallery.append(entry)

    # Save updated gallery file
    with open(server_gallery_json, "w") as f:
        json.dump(gallery, f, indent=2)

    # Also write last build to latest pointer
    with open(LATEST_PREVIEW_JSON, "w") as f:
        json.dump(entry, f, indent=2)

    # Optional: copy raw object data to global latest
    if os.path.exists(LATEST_OUTPUT_JSON):
        with open(LATEST_OUTPUT_JSON, "r") as f:
            obj_data = json.load(f)
        with open("data/latest_objects.json", "w") as f:
            json.dump(obj_data, f, indent=2)

    print(f"[+] Saved gallery item for server {server_id} to {server_gallery_json}")
