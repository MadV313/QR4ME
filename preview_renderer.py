from PIL import Image, ImageDraw
import os

def render_qr_preview(matrix: list, output_path: str, scale: int = 20, border: int = 2):
    """
    Renders a PNG preview of the QR object layout.

    - matrix: 2D list from generate_qr_matrix()
    - output_path: where to save the image
    - scale: pixel size per QR unit (20px default)
    - border: empty border (in matrix units)
    """
    rows = len(matrix)
    cols = len(matrix[0])

    img_width = (cols + border * 2) * scale
    img_height = (rows + border * 2) * scale

    img = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(img)

    for r in range(rows):
        for c in range(cols):
            if matrix[r][c]:  # black square
                x0 = (c + border) * scale
                y0 = (r + border) * scale
                x1 = x0 + scale
                y1 = y0 + scale
                draw.rectangle([x0, y0, x1, y1], fill="black")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    print(f"Saved QR preview to {output_path}")
