import discord
from discord.ext import commands
from discord import app_commands
import os
import json

from config import CONFIG
from utils.gallery_utils import save_to_gallery
from utils.channel_utils import get_channel_id
from utils.permissions import is_admin_user  # ✅ Permission logic

class PushGallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pushgallery", description="Add the most recent QR build to the public gallery")
    async def pushgallery(self, interaction: discord.Interaction):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
            return

        preview_path = CONFIG["preview_output_path"]
        zip_path = CONFIG["zip_output_path"]
        object_path = CONFIG["object_output_path"]

        if not os.path.exists(preview_path) or not os.path.exists(zip_path):
            await interaction.response.send_message("❌ No QR build found to push.", ephemeral=True)
            return

        # Extract object metadata for gallery entry
        metadata = {
            "object_type": "Unknown",
            "qr_size": "N/A",
            "total_objects": 0
        }

        try:
            with open(object_path, "r") as f:
                objects = json.load(f)
                metadata["total_objects"] = len(objects)
                metadata["object_type"] = objects[0]["type"] if objects else "Unknown"
                size_estimate = round(len(objects) ** 0.5)
                metadata["qr_size"] = f"{size_estimate}x{size_estimate}"
        except Exception as e:
            print(f"[pushgallery] Failed to load object metadata: {e}")

        # Save files + metadata to gallery
        save_to_gallery(preview_path, zip_path, metadata)

        # Post to configured gallery channel
        channel_id = get_channel_id("gallery") or CONFIG["admin_channel_id"]
        channel = self.bot.get_channel(int(channel_id))

        if not channel:
            await interaction.response.send_message("✅ Build saved, but gallery channel was not found.", ephemeral=True)
            return

        await channel.send(
            content=(
                f"🧱 **QR Build Pushed to Gallery**\n"
                f"• Object: `{metadata['object_type']}`\n"
                f"• Size: {metadata['qr_size']}\n"
                f"• Objects: {metadata['total_objects']}"
            ),
            files=[
                discord.File(zip_path),
                discord.File(preview_path)
            ]
        )

        await interaction.response.send_message("✅ QR build pushed and posted in gallery channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PushGallery(bot))
