import zipfile
import os
import shutil

def create_qr_zip(object_json_path: str, preview_image_path: str, zip_output_path: str, extra_text: str = "", export_mode: str = "zip") -> str:
    """
    Packages the generated QR layout files.

    Modes:
      - zip: generates a .zip with objects.json, preview, and README.txt
      - json: returns path to just the object_json_path

    Returns path to the final file to send.
    """
    os.makedirs(os.path.dirname(zip_output_path), exist_ok=True)

    if export_mode == "json":
        print(f"[zip_packager] Skipping zip — returning raw JSON: {object_json_path}")
        return object_json_path

    readme_content = f"""
QR Code Build Summary

• Object Map: {os.path.basename(object_json_path)}
• Preview Image: {os.path.basename(preview_image_path)}

{extra_text.strip()}
""".strip()

    readme_path = os.path.join(os.path.dirname(zip_output_path), "README.txt")
    with open(readme_path, "w") as f:
        f.write(readme_content)

    with zipfile.ZipFile(zip_output_path, 'w') as zipf:
        zipf.write(object_json_path, arcname="objects.json")
        zipf.write(preview_image_path, arcname="qr_preview.png")
        zipf.write(readme_path, arcname="README.txt")

    print(f"[zip_packager] ✅ Created zip: {zip_output_path}")
    return zip_output_path
