import qrcode
import json

def generate_qr_matrix(data: str, box_size: int = 1) -> list:
    """
    Converts input text to a binary matrix (1 = black, 0 = white).
    """
    qr = qrcode.QRCode(
        version=None,  # auto size
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    return matrix  # 2D list of booleans


def qr_to_object_list(matrix: list, object_type: str, origin: dict, scale: float = 1.0) -> list:
    """
    Converts QR matrix into a list of DayZ objects at mapped coordinates.
    Only '1' (black) pixels result in objects.
    """
    objects = []
    rows = len(matrix)
    cols = len(matrix[0])

    offset_x = origin["x"] - ((cols / 2) * scale)
    offset_z = origin["z"] - ((rows / 2) * scale)

    for row in range(rows):
        for col in range(cols):
            if matrix[row][col]:
                x = offset_x + (col * scale)
                z = offset_z + (row * scale)
                obj = {
                    "type": object_type,
                    "position": [x, origin["y"], z],
                    "rotation": [0.0, 0.0, 0.0]
                }
                objects.append(obj)

    return objects


def save_object_json(object_list: list, output_path: str):
    with open(output_path, "w") as f:
        json.dump(object_list, f, indent=2)


# 🔧 Optional direct test
if __name__ == "__main__":
    from config import CONFIG
    test_data = "https://discord.gg/your-server"
    matrix = generate_qr_matrix(test_data)
    object_list = qr_to_object_list(matrix, CONFIG["default_object"], CONFIG["origin_position"])
    save_object_json(object_list, CONFIG["object_output_path"])
    print(f"Generated {len(object_list)} objects.")
