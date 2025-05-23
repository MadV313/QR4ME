import discord
from discord.ext import commands
from discord import app_commands
import os

from config import CONFIG
from utils.permissions import is_admin_user  # ✅ NEW

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cleanup", description="Delete the most recent preview + ZIP build output")
    async def cleanup(self, interaction: discord.Interaction):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
            return

        removed = []

        for path in [CONFIG["preview_output_path"], CONFIG["zip_output_path"]]:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    removed.append(os.path.basename(path))
            except Exception as e:
                await interaction.response.send_message(f"❌ Failed to delete `{path}`: {e}", ephemeral=True)
                return

        if removed:
            await interaction.response.send_message(
                f"🧹 Removed: `{', '.join(removed)}`", ephemeral=True
            )
        else:
            await interaction.response.send_message("✅ Nothing to clean.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Cleanup(bot))
