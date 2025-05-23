import qrcode
import json

# 🔧 In-game class mapping
OBJECT_CLASS_MAP = {
    "ImprovisedContainer": "Land_Container_1Mo",
    "SmallProtectiveCase": "SmallProtectorCase",
    "SmallProtectorCase": "SmallProtectorCase",
    "DryBag_Black": "DryBag_Black",
    "PlasticBottle": "PlasticBottle",
    "CookingPot": "CookingPot",
    "MetalWire": "MetalWire",
    "WoodenCrate": "WoodenCrate",
    "Armband_Black": "Armband_Black"
}

# 🔧 Optional spacing tweaks for visual balance
OBJECT_SIZE_ADJUSTMENTS = {
    "SmallProtectiveCase": 1.0,
    "SmallProtectorCase": 1.0,
    "DryBag_Black": 1.25,
    "PlasticBottle": 0.75,
    "CookingPot": 0.8,
    "MetalWire": 0.6,
    "ImprovisedContainer": 1.0,
    "WoodenCrate": 1.1,
    "Armband_Black": 0.5
}


def generate_qr_matrix(data: str, box_size: int = 1) -> list:
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.get_matrix()


def qr_to_object_list(matrix: list, object_type: str, origin: dict, scale: float = 1.0) -> list:
    objects = []
    rows = len(matrix)
    cols = len(matrix[0])

    spacing = scale * OBJECT_SIZE_ADJUSTMENTS.get(object_type, 1.0)
    resolved_type = OBJECT_CLASS_MAP.get(object_type, object_type)

    offset_x = origin["x"] - ((cols / 2) * spacing)
    offset_z = origin["z"] - ((rows / 2) * spacing)

    for row in range(rows):
        for col in range(cols):
            if matrix[row][col]:
                x = offset_x + (col * spacing)
                z = offset_z + (row * spacing)
                obj = {
                    "type": resolved_type,
                    "position": [x, origin["y"], z],
                    "rotation": [0.0, 0.0, 0.0]
                }
                objects.append(obj)

    # ✅ Add fixed background anchor object behind the entire grid
    center_x = origin["x"]
    center_z = origin["z"]
    background = {
        "type": "DoorTestCamera",
        "position": [center_x, origin["y"] - 0.01, center_z],
        "rotation": [0.0, 0.0, 0.0]
    }
    objects.append(background)

    return objects


def save_object_json(object_list: list, output_path: str):
    with open(output_path, "w") as f:
        json.dump(object_list, f, indent=2)


# 🔧 Optional manual test
if __name__ == "__main__":
    from config import CONFIG
    test_data = "https://discord.gg/your-server"
    matrix = generate_qr_matrix(test_data)
    object_list = qr_to_object_list(matrix, CONFIG["default_object"], CONFIG["origin_position"])
    save_object_json(object_list, CONFIG["object_output_path"])
    print(f"Generated {len(object_list)} objects (including anchor).")
