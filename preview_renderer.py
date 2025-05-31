from PIL import Image, ImageDraw
import os

def render_qr_preview(matrix: list, output_path: str, scale: int = 64, border: int = 2, object_type: str = "SmallProtectiveCase"):
    """
    Renders a PNG preview of the QR object layout using thumbnails with grid overlay.

    - matrix: 2D list from generate_qr_matrix()
    - output_path: where to save the image (can be per-guild)
    - scale: pixel size per QR unit (default 64px for thumbnails)
    - border: empty border (in matrix units)
    - object_type: name of the DayZ object (matches thumbnail PNG)
    """
    rows = len(matrix)
    cols = len(matrix[0])

    img_width = (cols + border * 2) * scale
    img_height = (rows + border * 2) * scale

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    thumbnail_name = object_type + ".PNG"
    thumb_path = os.path.join("assets", "thumbnails", thumbnail_name)

    try:
        thumb = Image.open(thumb_path).convert("RGBA").resize((scale, scale))

        # Special case: Rotate DoorTestKit 90 degrees to stand upright
        if object_type.lower() == "doortestkit":
            thumb = thumb.rotate(90, expand=True)

    except Exception as e:
        print(f"[preview_renderer] ⚠️ Thumbnail not found: {thumb_path} — using fallback. Error: {e}")
        thumb = Image.new("RGBA", (scale, scale), "black")

    for r in range(rows):
        for c in range(cols):
            x = (c + border) * scale
            y = (r + border) * scale
            if matrix[r][c]:
                img.paste(thumb, (x, y), mask=thumb if thumb.mode == "RGBA" else None)

            # Draw a light border for each cell
            draw.rectangle([x, y, x + scale, y + scale], outline="#cccccc", width=1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"✅ Saved QR preview to {output_path}")
