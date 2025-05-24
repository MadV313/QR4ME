import discord
from discord.ext import commands
from discord import app_commands
import os

from utils.permissions import is_admin_user  # ✅ Centralized permission check
from utils.config_utils import get_guild_config  # ✅ Multi-server support
from utils.channel_utils import get_channel_id  # ✅ Per-server channel access

class Cleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cleanup", description="Delete the most recent preview + ZIP build output and bot post")
    async def cleanup(self, interaction: discord.Interaction):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
            return

        # Load per-guild config
        guild_id = str(interaction.guild_id)
        guild_config = get_guild_config(guild_id)
        preview_path = guild_config.get("preview_output_path")
        zip_path = guild_config.get("zip_output_path")

        removed_files = []

        # Attempt file cleanup
        for path in [preview_path, zip_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    removed_files.append(os.path.basename(path))
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Failed to delete `{os.path.basename(path)}`: {e}",
                    ephemeral=True
                )
                return

        # Attempt to delete most recent bot message with attachments
        channel_id = get_channel_id("gallery", guild_id) or guild_config.get("admin_channel_id")
        channel = self.bot.get_channel(int(channel_id)) if channel_id else None

        if channel:
            try:
                async for msg in channel.history(limit=10):
                    if msg.author == self.bot.user and msg.attachments:
                        await msg.delete()
                        break
            except Exception as e:
                print(f"[cleanup] Warning: could not delete previous message: {e}")

        if removed_files:
            await interaction.response.send_message(
                f"🧹 Removed: `{', '.join(removed_files)}` and latest bot message.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message("✅ Nothing to clean.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Cleanup(bot))
