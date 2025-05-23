import json

CONFIG_PATH = "config.json"

def _load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def _save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def is_admin_user(interaction) -> bool:
    """Returns True if user is in admin_roles or permitted_users."""
    try:
        data = _load_config()
        user_id_str = str(interaction.user.id)
        permitted_users = data.get("permitted_users", [])
        admin_roles = data.get("admin_roles", [])

        # Check if user ID is directly permitted
        if user_id_str in permitted_users:
            return True

        # Check if user has any admin role
        if hasattr(interaction.user, "roles"):
            user_roles = [str(role.id) for role in interaction.user.roles]
            return any(role_id in admin_roles for role_id in user_roles)

        return False
    except Exception:
        return False

def add_admin_user(user_id: int):
    data = _load_config()
    user_id_str = str(user_id)

    if "permitted_users" not in data:
        data["permitted_users"] = []

    if user_id_str not in data["permitted_users"]:
        data["permitted_users"].append(user_id_str)
        _save_config(data)

def remove_admin_user(user_id: int) -> bool:
    data = _load_config()
    user_id_str = str(user_id)

    if "permitted_users" not in data or user_id_str not in data["permitted_users"]:
        return False

    data["permitted_users"].remove(user_id_str)
    _save_config(data)
    return True
