import discord
from discord.ext import commands
from discord import app_commands
import json
from config import CONFIG

class SetOrigin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, interaction: discord.Interaction):
        if not CONFIG["admin_roles"]:
            return True
        user_roles = [str(role.id) for role in interaction.user.roles]
        return any(role in CONFIG["admin_roles"] for role in user_roles)

    @app_commands.command(name="setorigin", description="Update the origin position for QR placement")
    @app_commands.describe(
        x="X coordinate",
        y="Y coordinate (default 0.0)",
        z="Z coordinate"
    )
    async def setorigin(self, interaction: discord.Interaction, x: float, z: float, y: float = 0.0):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        try:
            with open("config.json", "r") as f:
                data = json.load(f)

            data["origin_position"] = {
                "x": x,
                "y": y,
                "z": z
            }

            with open("config.json", "w") as f:
                json.dump(data, f, indent=2)

            await interaction.response.send_message(
                f"📍 **New origin position set:**\n"
                f"> `X`: {x}\n> `Y`: {y}\n> `Z`: {z}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to update origin: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SetOrigin(bot))
