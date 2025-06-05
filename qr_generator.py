import os
import qrcode
import json
import random

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

MAX_OBJECTS = 950  # ⬆️ Increased object cap

def generate_qr_matrix(data: str, box_size: int = 1) -> list:
    qr = qrcode.QRCode(
        version=3,  # ✅ 29x29 matrix
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=1
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.get_matrix()

def qr_to_object_list(matrix: list, object_type: str, origin: dict, offset: dict, scale: float = 1.0, spacing: float = None, include_mirror_kit: bool = False) -> list:
    rows = len(matrix)
    cols = len(matrix[0])
    resolved_type = OBJECT_CLASS_MAP.get(object_type, object_type)

    spacing = spacing if spacing is not None else scale * OBJECT_SIZE_ADJUSTMENTS.get(object_type, 1.0)

    # ✅ FIXED: Prevents diagonal tilt by aligning to even spacing grid
    offset_x = round(origin["x"] - ((cols // 2) * spacing) + offset.get("x", 0), 4)
    offset_z = round(origin["z"] - ((rows // 2) * spacing) + offset.get("z", 0), 4)

    top_y = 238.17279052734376
    y_step = 0.04

    objects = []

    # ✅ Optional test camera & mirror
    if include_mirror_kit:
        camera_object = {
            "name": "DoorTestCamera",
            "pos": [origin["x"] + offset.get("x", 0), top_y, origin["z"] + offset.get("z", 0)],
            "ypr": [0.0, 90.0, 0.0],
            "scale": 1.0,
            "enableCEPersistency": 0,
            "customString": json.dumps({"mirror_enabled": True})
        }
        mirror_object = {
            "name": "Land_Mirror_Test_Kit",
            "pos": [origin["x"], top_y - 0.1, origin["z"]],
            "ypr": [0.0, 0.0, 0.0],
            "scale": 1.5,
            "enableCEPersistency": 0,
            "customString": ""
        }
        objects.append(camera_object)
        objects.append(mirror_object)

    # ✅ Force 3 layers per black pixel (up to MAX_OBJECTS)
    for row in range(rows):
        for col in range(cols):
            if matrix[row][col]:
                base_x = offset_x + (col * spacing)
                base_z = offset_z + (row * spacing)

                for i in range(3):  # ⬅️ Force 3 layers
                    if len(objects) >= MAX_OBJECTS:
                        return objects  # ✅ Enforce object count limit early

                    y = round(top_y - i * y_step, 14)
                    obj = {
                        "name": resolved_type,
                        "pos": [base_x, y, base_z],
                        "ypr": [106.25797271728516, -3.9915712402027739e-10, -1.56961490915819e-7],
                        "scale": scale,
                        "enableCEPersistency": 0,
                        "customString": ""
                    }
                    objects.append(obj)

    return objects

def save_object_json(object_list: list, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump({"Objects": object_list}, f, indent=2)

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
        CONFIG.get("defaultSpacing", 1.0),
        CONFIG.get("include_mirror_kit", False)
    )
    save_object_json(object_list, CONFIG["object_output_path"])
    print(f"✅ Generated {len(object_list)} objects.")
