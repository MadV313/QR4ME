import discord
from discord.ext import commands
from discord import app_commands
import os
import json

from config import CONFIG
from utils.gallery_utils import save_to_gallery

class PushGallery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, interaction: discord.Interaction):
        if not CONFIG["admin_roles"]:
            return True
        user_roles = [str(role.id) for role in interaction.user.roles]
        return any(role in CONFIG["admin_roles"] for role in user_roles)

    @app_commands.command(name="pushgallery", description="Add the most recent QR build to the public gallery")
    async def pushgallery(self, interaction: discord.Interaction):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
            return

        preview_path = CONFIG["preview_output_path"]  # should point to /previews/preview_output.png
        zip_path = CONFIG["zip_output_path"]          # should point to /outputs/output_build.zip
        object_path = CONFIG["object_output_path"]    # should point to /data/output_build.json

        if not os.path.exists(preview_path) or not os.path.exists(zip_path):
            await interaction.response.send_message("❌ No QR build found to push.", ephemeral=True)
            return

        # Try to load object data for metadata
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

        # Push to gallery
        save_to_gallery(preview_path, zip_path, metadata)

        await interaction.response.send_message("✅ QR build pushed to public gallery!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PushGallery(bot))
