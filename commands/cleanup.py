import discord
from discord.ext import commands
from discord import app_commands
import os

from config import CONFIG

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, interaction: discord.Interaction):
        if not CONFIG["admin_roles"]:
            return True
        user_roles = [str(role.id) for role in interaction.user.roles]
        return any(role in CONFIG["admin_roles"] for role in user_roles)

    @app_commands.command(name="cleanup", description="Delete the most recent preview + ZIP build output")
    async def cleanup(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
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
