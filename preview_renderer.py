from PIL import Image, ImageDraw
import os

def render_qr_preview(matrix: list, output_path: str, scale: int = 64, border: int = 2, object_type: str = "SmallProtectiveCase"):
    """
    Renders a PNG preview of the QR object layout using thumbnails with grid overlay.

    - matrix: 2D list from generate_qr_matrix()
    - output_path: where to save the image
    - scale: pixel size per QR unit (default 64px for thumbnails)
    - border: empty border (in matrix units)
    - object_type: used to select thumbnail image (expects .PNG exact case)
    """
    rows = len(matrix)
    cols = len(matrix[0])

    img_width = (cols + border * 2) * scale
    img_height = (rows + border * 2) * scale

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    # Match your actual file naming
    thumbnail_name = object_type + ".PNG"
    thumb_path = os.path.join("assets", "thumbnails", thumbnail_name)

    try:
        thumb = Image.open(thumb_path).convert("RGBA").resize((scale, scale))
    except Exception:
        thumb = Image.new("RGBA", (scale, scale), "black")

    for r in range(rows):
        for c in range(cols):
            x = (c + border) * scale
            y = (r + border) * scale
            if matrix[r][c]:
                img.paste(thumb, (x, y), mask=thumb if thumb.mode == "RGBA" else None)

            # Always draw grid
            draw.rectangle([x, y, x + scale, y + scale], outline="#cccccc", width=1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Saved QR preview to {output_path}")
