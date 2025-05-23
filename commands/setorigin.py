import discord
from discord.ext import commands
from discord import app_commands
import json
import os

from utils.permissions import is_admin_user  # ✅ Centralized admin check

ORIGINS_FILE = "data/origins.json"

def load_origins():
    if not os.path.exists(ORIGINS_FILE):
        return {}
    with open(ORIGINS_FILE, "r") as f:
        return json.load(f)

def save_origin(guild_id: str, x: float, y: float, z: float):
    data = load_origins()
    data[guild_id] = {"x": x, "y": y, "z": z}
    with open(ORIGINS_FILE, "w") as f:
        json.dump(data, f, indent=2)

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
            save_origin(guild_id, x, y, z)
            await interaction.response.send_message(
                f"📍 **New origin position set for this server:**\n"
                f"> `X`: {x}\n> `Y`: {y}\n> `Z`: {z}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to update origin: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetOrigin(bot))
