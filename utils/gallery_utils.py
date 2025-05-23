import os
import json
import shutil
from datetime import datetime

GALLERY_DIR = "public/gallery"
GALLERY_JSON = "data/gallery.json"
LATEST_PREVIEW_JSON = "data/previews.json"
LATEST_OUTPUT_JSON = "data/output_build.json"

def save_to_gallery(preview_path, zip_path, metadata: dict, server_id: str = "Unknown"):
    os.makedirs(GALLERY_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = metadata["object_type"] + "_" + timestamp

    # Build destination paths
    preview_target = os.path.join(GALLERY_DIR, f"{base_name}.png")
    zip_target = os.path.join(GALLERY_DIR, f"{base_name}.zip")

    # Move/copy files from previews/ and outputs/ into public/gallery/
    shutil.copy(preview_path, preview_target)
    shutil.copy(zip_path, zip_target)

    # Load existing gallery index
    try:
        with open(GALLERY_JSON, "r") as f:
            gallery = json.load(f)
    except FileNotFoundError:
        gallery = []

    # Add new entry with server_id
    entry = {
        "image": f"gallery/{base_name}.png",
        "zip": f"gallery/{base_name}.zip",
        "object_type": metadata["object_type"],
        "qr_size": metadata["qr_size"],
        "total_objects": metadata["total_objects"],
        "created": timestamp,
        "server_id": server_id
    }
    gallery.append(entry)

    # Save updated gallery index
    os.makedirs(os.path.dirname(GALLERY_JSON), exist_ok=True)
    with open(GALLERY_JSON, "w") as f:
        json.dump(gallery, f, indent=2)

    # Update previews.json (latest build pointer)
    with open(LATEST_PREVIEW_JSON, "w") as f:
        json.dump(entry, f, indent=2)

    # Optionally copy raw object list for latest build
    output_path = "data/output_build.json"
    if os.path.exists(output_path):
        with open(output_path, "r") as f:
            obj_data = json.load(f)
        with open("data/latest_objects.json", "w") as f:
            json.dump(obj_data, f, indent=2)
