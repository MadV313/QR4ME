import discord
from discord.ext import commands
from discord import app_commands
import os
import json

from config import CONFIG
from utils.gallery_utils import save_to_gallery
from utils.channel_utils import get_channel_id
from utils.permissions import is_admin_user
from utils.config_utils import get_guild_config  # ✅ Multi-server config

class PushGallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pushgallery", description="Add the most recent QR build to the public gallery")
    async def pushgallery(self, interaction: discord.Interaction):
        # Check user permissions
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
            return

        guild_id = str(interaction.guild_id)
        guild_config = get_guild_config(guild_id)
        preview_path = guild_config["preview_output_path"]
        zip_path = guild_config["zip_output_path"]
        object_path = guild_config["object_output_path"]

        # Check if required files exist
        if not os.path.exists(preview_path) or not os.path.exists(zip_path):
            await interaction.response.send_message("❌ No QR build found to push.", ephemeral=True)
            return

        # Extract metadata from object JSON
        metadata = {
            "object_type": "Unknown",
            "qr_size": "N/A",
            "total_objects": 0
        }

        try:
            with open(object_path, "r") as f:
                obj_data = json.load(f)
                objects = obj_data.get("Objects", [])
                metadata["total_objects"] = len(objects)
                metadata["object_type"] = objects[1]["name"] if len(objects) > 1 else "Unknown"
                side_len = round((len(objects) - 1) ** 0.5)  # Exclude camera object
                metadata["qr_size"] = f"{side_len}x{side_len}"
        except Exception as e:
            print(f"[pushgallery] Metadata extraction error: {e}")

        # Save gallery entry with server ID
        save_to_gallery(preview_path, zip_path, metadata, server_id=guild_id)

        # Send build to gallery channel
        channel_id = get_channel_id("gallery", guild_id) or guild_config.get("admin_channel_id")
        channel = self.bot.get_channel(int(channel_id)) if channel_id else None

        if not channel:
            await interaction.response.send_message("✅ Build saved, but gallery channel was not found.", ephemeral=True)
            return

        await channel.send(
            content=(
                f"🧱 **QR Build Pushed to Gallery**\n"
                f"• Object: `{metadata['object_type']}`\n"
                f"• Size: `{metadata['qr_size']}`\n"
                f"• Total Objects: `{metadata['total_objects']}`"
            ),
            files=[
                discord.File(zip_path),
                discord.File(preview_path)
            ]
        )

        await interaction.response.send_message("✅ QR build pushed and posted in gallery channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PushGallery(bot))
