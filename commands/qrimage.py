import discord
from discord import app_commands
from discord.ext import commands
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode

from config import CONFIG
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip

class QRImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, interaction: discord.Interaction):
        if not CONFIG["admin_roles"]:
            return True
        user_roles = [str(role.id) for role in interaction.user.roles]
        return any(role in CONFIG["admin_roles"] for role in user_roles)

    @app_commands.command(name="qrimage", description="Upload a QR code image to generate a DayZ object layout")
    @app_commands.describe(
        image="Upload a PNG or JPG of a QR code",
        scale="Spacing between objects (default 1.0)",
        object_type="DayZ object to use (default: SmallProtectorCase)"
    )
    async def qrimage(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        scale: float = 1.0,
        object_type: str = "SmallProtectorCase"
    ):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()

        # Download image
        img_bytes = await image.read()
        np_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # Decode QR code
        decoded = decode(img)
        if not decoded:
            await interaction.followup.send("❌ Failed to decode QR code from the image.", ephemeral=True)
            return

        qr_text = decoded[0].data.decode("utf-8")

        # Generate QR + output files
        matrix = generate_qr_matrix(qr_text)
        objects = qr_to_object_list(matrix, object_type, CONFIG["origin_position"], scale)
        save_object_json(objects, CONFIG["object_output_path"])
        render_qr_preview(matrix, CONFIG["preview_output_path"])
        create_qr_zip(
            CONFIG["object_output_path"],
            CONFIG["preview_output_path"],
            CONFIG["zip_output_path"],
            extra_text=f"(from image)\nQR Size: {len(matrix)}x{len(matrix[0])}\nTotal Objects: {len(objects)}\nObject Used: {object_type}"
        )

        # Post to admin channel
        channel = self.bot.get_channel(int(CONFIG["admin_channel_id"]))
        if not channel:
            await interaction.followup.send("❌ Admin channel not found.")
            return

        await channel.send(
            content=f"📷 **QR Image Build Complete**\n• Decoded: `{qr_text}`\n• Size: {len(matrix)}x{len(matrix[0])}\n• Objects: {len(objects)}\n• Type: `{object_type}`",
            files=[
                discord.File(CONFIG["zip_output_path"]),
                discord.File(CONFIG["preview_output_path"])
            ]
        )

        await interaction.followup.send("✅ QR image decoded and build posted in admin channel.")

async def setup(bot):
    await bot.add_cog(QRImage(bot))
