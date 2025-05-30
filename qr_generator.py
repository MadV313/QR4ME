import os
import qrcode
import json

# ✅ In-game object class mapping
OBJECT_CLASS_MAP = {
    "ImprovisedContainer": "Land_Container_1Mo",
    "SmallProtectiveCase": "SmallProtectorCase",
    "DryBag_Black": "DryBag_Black",
    "PlasticBottle": "PlasticBottle",
    "CookingPot": "CookingPot",
    "MetalWire": "MetalWire",
    "WoodenCrate": "WoodenCrate",
    "BoxWooden": "StaticObj_Misc_BoxWooden",
    "Armband_Black": "Armband_Black",
    "Jerrycan": "CanisterGasoline"
}

# ✅ Optional size tweaks per object for default spacing logic
OBJECT_SIZE_ADJUSTMENTS = {
    "SmallProtectiveCase": 1.0,
    "SmallProtectorCase": 1.0,
    "DryBag_Black": 1.25,
    "PlasticBottle": 0.75,
    "CookingPot": 0.8,
    "MetalWire": 0.6,
    "ImprovisedContainer": 1.0,
    "WoodenCrate": 1.1,
    "Armband_Black": 0.5,
    "Jerrycan": 1.0
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

def qr_to_object_list(matrix: list, object_type: str, origin: dict, offset: dict, scale: float = 1.0, spacing: float = None) -> list:
    rows = len(matrix)
    cols = len(matrix[0])
    resolved_type = OBJECT_CLASS_MAP.get(object_type, object_type)

    # Default spacing is based on scale × object adjustment (legacy support)
    spacing = spacing if spacing is not None else scale * OBJECT_SIZE_ADJUSTMENTS.get(object_type, 1.0)

    offset_x = origin["x"] - ((cols / 2) * spacing) + offset.get("x", 0)
    offset_y = origin["y"] + offset.get("y", 0)
    offset_z = origin["z"] - ((rows / 2) * spacing) + offset.get("z", 0)

    objects = []

    # ✅ Add camera object for orientation
    camera_object = {
        "name": "DoorTestCamera",
        "pos": [origin["x"] + offset.get("x", 0), offset_y, origin["z"] + offset.get("z", 0)],
        "ypr": [0.0, 90.0, 0.0],
        "scale": 1.0,
        "enableCEPersistency": 0,
        "customString": ""
    }
    objects.append(camera_object)

    for row in range(rows):
        for col in range(cols):
            if matrix[row][col]:
                x = offset_x + (col * spacing)
                z = offset_z + (row * spacing)

                obj = {
                    "name": resolved_type,
                    "pos": [x, offset_y, z],
                    "ypr": [0.0, 0.0, 0.0],
                    "scale": scale,
                    "enableCEPersistency": 0,
                    "customString": ""
                }
                objects.append(obj)

    return objects

def save_object_json(object_list: list, output_path: str, map_name: str = "Unknown", origin: dict = None):
    """
    Save the object layout to JSON, including map + position metadata.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    json_data = {
        "map": map_name,
        "position": origin or {"x": 0, "y": 0, "z": 0},
        "objects": object_list
    }

    with open(output_path, "w") as f:
        json.dump(json_data, f, indent=2)

# ✅ Manual test
if __name__ == "__main__":
    from config import CONFIG
    test_data = "https://discord.gg/your-server"
    matrix = generate_qr_matrix(test_data)
    object_list = qr_to_object_list(
        matrix,
        CONFIG["default_object"],
        CONFIG["origin_position"],
        CONFIG["originOffset"],
        CONFIG.get("defaultScale", 0.5),
        CONFIG.get("defaultSpacing", 1.0)
    )
    save_object_json(object_list, CONFIG["object_output_path"], CONFIG.get("selected_map", "Chernarus"), CONFIG["origin_position"])
    print(f"Generated {len(object_list)} objects including anchor.")
