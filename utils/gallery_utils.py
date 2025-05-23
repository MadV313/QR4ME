import os
import json
from datetime import datetime

GALLERY_DIR = "public/gallery"
GALLERY_JSON = "public/data/gallery.json"

def save_to_gallery(preview_path, zip_path, metadata: dict):
    os.makedirs(GALLERY_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = metadata["object_type"] + "_" + timestamp

    # Copy + rename files into gallery folder
    preview_target = os.path.join(GALLERY_DIR, f"{base_name}.png")
    zip_target = os.path.join(GALLERY_DIR, f"{base_name}.zip")
    os.rename(preview_path, preview_target)
    os.rename(zip_path, zip_target)

    # Load existing index
    try:
        with open(GALLERY_JSON, "r") as f:
            gallery = json.load(f)
    except FileNotFoundError:
        gallery = []

    # Add new entry
    gallery.append({
        "image": f"gallery/{base_name}.png",
        "zip": f"gallery/{base_name}.zip",
        "object_type": metadata["object_type"],
        "qr_size": metadata["qr_size"],
        "total_objects": metadata["total_objects"],
        "created": timestamp
    })

    # Save index
    os.makedirs(os.path.dirname(GALLERY_JSON), exist_ok=True)
    with open(GALLERY_JSON, "w") as f:
        json.dump(gallery, f, indent=2)
