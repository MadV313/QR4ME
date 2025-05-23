import json
import os

CONFIG_PATH = "config.json"
ADMIN_USERS_FILE = "data/admin_users.json"

def _load_admin_users():
    if not os.path.exists(ADMIN_USERS_FILE):
        return {}
    with open(ADMIN_USERS_FILE, "r") as f:
        data = json.load(f)
    # Auto-migrate old flat formats to valid structure
    fixed = {}
    for sid, value in data.items():
        if isinstance(value, list):
            fixed[sid] = {"permitted_users": value}
        elif isinstance(value, dict) and "permitted_users" in value:
            fixed[sid] = value
        else:
            fixed[sid] = {"permitted_users": []}
    return fixed

def _save_admin_users(data):
    os.makedirs(os.path.dirname(ADMIN_USERS_FILE), exist_ok=True)
    with open(ADMIN_USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin_user(interaction) -> bool:
    """
    Checks if the user is allowed based on:
    - Their ID in server-specific permitted_users
    - Their role ID in server-specific admin_roles
    """
    try:
        server_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        user_roles = [str(role.id) for role in getattr(interaction.user, "roles", [])]

        data = _load_admin_users()
        permitted = data.get(server_id, {}).get("permitted_users", [])

        if user_id in permitted:
            return True

        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)

        admin_roles = config.get("admin_roles", [])
        return any(role_id in admin_roles for role_id in user_roles)

    except Exception as e:
        print(f"[permissions] Error in is_admin_user: {e}")
        return False

def add_admin_user(user_id: int, server_id: str):
    data = _load_admin_users()
    user_id_str = str(user_id)
    server_id = str(server_id)

    if server_id not in data:
        data[server_id] = {"permitted_users": []}
    elif "permitted_users" not in data[server_id]:
        data[server_id]["permitted_users"] = []

    if user_id_str not in data[server_id]["permitted_users"]:
        data[server_id]["permitted_users"].append(user_id_str)
        _save_admin_users(data)

def remove_admin_user(user_id: int, server_id: str) -> bool:
    data = _load_admin_users()
    user_id_str = str(user_id)
    server_id = str(server_id)

    if server_id not in data or user_id_str not in data[server_id].get("permitted_users", []):
        return False

    data[server_id]["permitted_users"].remove(user_id_str)
    _save_admin_users(data)
    return True
