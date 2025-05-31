import discord
from discord.ext import commands
from discord import app_commands
import json
import os

from utils.permissions import is_admin_user  # ✅ Centralized admin check

CONFIG_FOLDER = "data/configs"

def update_origin_in_config(guild_id: str, x: float, y: float, z: float):
    os.makedirs(CONFIG_FOLDER, exist_ok=True)
    config_path = os.path.join(CONFIG_FOLDER, f"config_{guild_id}.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError("Config file not found. Please rejoin the server or contact an admin.")

    with open(config_path, "r") as f:
        config = json.load(f)

    config["origin_position"] = {"x": x, "y": y, "z": z}

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

class SetOrigin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setorigin", description="Update the origin position for QR placement")
    @app_commands.describe(
        x="X coordinate",
        y="Y coordinate (default 0.0)",
        z="Z coordinate"
    )
    async def setorigin(self, interaction: discord.Interaction, x: float, z: float, y: float = 0.0):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)

        try:
            update_origin_in_config(guild_id, x, y, z)
            await interaction.response.send_message(
                f"📍 **New origin position set for this server:**\n"
                f"> `X`: {x}\n> `Y`: {y}\n> `Z`: {z}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to update origin: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetOrigin(bot))
