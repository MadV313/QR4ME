import zipfile
import os

def create_qr_zip(object_json_path: str, preview_image_path: str, zip_output_path: str, extra_text: str = ""):
    """
    Packages the generated QR layout files into a zip archive.
    Includes:
      - objects.json
      - qr_preview.png
      - README.txt (summary)
    """
    os.makedirs(os.path.dirname(zip_output_path), exist_ok=True)

    readme_content = f"""
QR Code Build Summary

• Object Map: {os.path.basename(object_json_path)}
• Preview Image: {os.path.basename(preview_image_path)}

{extra_text.strip()}
""".strip()

    readme_path = "outputs/README.txt"
    with open(readme_path, "w") as f:
        f.write(readme_content)

    with zipfile.ZipFile(zip_output_path, 'w') as zipf:
        zipf.write(object_json_path, arcname="objects.json")
        zipf.write(preview_image_path, arcname="qr_preview.png")
        zipf.write(readme_path, arcname="README.txt")

    print(f"Created zip: {zip_output_path}")
