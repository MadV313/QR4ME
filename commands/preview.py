import discord
from discord.ext import commands
from discord import app_commands
from config import CONFIG
import os

class Preview(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="preview", description="Re-send the latest generated QR build preview and zip")
    async def preview(self, interaction: discord.Interaction):
        if not os.path.exists(CONFIG["preview_output_path"]) or not os.path.exists(CONFIG["zip_output_path"]):
            await interaction.response.send_message("❌ No preview available yet. Please run `/qrbuild` or `/qrimage` first.", ephemeral=True)
            return

        await interaction.response.send_message(
            content="📦 Here is the most recent QR build preview + zip:",
            files=[
                discord.File(CONFIG["preview_output_path"]),
                discord.File(CONFIG["zip_output_path"])
            ],
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Preview(bot))
