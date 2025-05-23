import discord
from discord.ext import commands
from discord import app_commands
import json

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
        from config import CONFIG  # Reloadable in dev

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
                f"📍 New origin set:\n`X: {x}`\n`Y: {y}`\n`Z: {z}`",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to update origin: {e}", ephemeral=True)

# ✅ This is the correct setup pattern
async def setup(bot):
    await bot.add_cog(SetOrigin(bot))
