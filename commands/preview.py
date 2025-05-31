import discord
from discord.ext import commands
from discord import app_commands
import os

from utils.config_utils import get_guild_config
from utils.channel_utils import get_channel_id
from utils.permissions import is_admin_user

class Preview(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="preview", description="Re-send the latest generated QR build preview and zip")
    async def preview(self, interaction: discord.Interaction):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        config = get_guild_config(guild_id)

        preview_path = config["preview_output_path"]
        zip_path = config["zip_output_path"]

        if not os.path.exists(preview_path) or not os.path.exists(zip_path):
            await interaction.response.send_message(
                "❌ No preview available yet. Please run `/qrbuild` or `/qrimage` first.",
                ephemeral=True
            )
            return

        channel_id = get_channel_id("gallery", guild_id) or config.get("admin_channel_id")
        channel = self.bot.get_channel(int(channel_id)) if channel_id else None

        if not channel:
            await interaction.response.send_message("❌ Gallery channel not found.", ephemeral=True)
            return

        await channel.send(
            content="📦 **Reposted Preview + ZIP**",
            files=[
                discord.File(zip_path),
                discord.File(preview_path)
            ]
        )

        await interaction.response.send_message("✅ Reposted in gallery channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Preview(bot))
