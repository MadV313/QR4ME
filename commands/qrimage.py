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
from utils.channel_utils import get_channel_id  # ✅ NEW

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
        object_type="Choose the object to use for QR layout"
    )
    @app_commands.choices(
        object_type=[
            app_commands.Choice(name="Small Protective Case", value="SmallProtectiveCase"),
            app_commands.Choice(name="Wooden Crate", value="WoodenCrate"),
            app_commands.Choice(name="Improvised Container", value="ImprovisedContainer"),
            app_commands.Choice(name="Dry Bag (Black)", value="DryBag_Black"),
            app_commands.Choice(name="Plastic Bottle", value="PlasticBottle"),
            app_commands.Choice(name="Cooking Pot", value="CookingPot"),
            app_commands.Choice(name="Metal Wire", value="MetalWire"),
        ]
    )
    async def qrimage(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        object_type: app_commands.Choice[str],
        scale: float = 1.0
    ):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()
        obj_type = object_type.value

        # Step 1: Download image
        img_bytes = await image.read()
        np_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        # Step 2: Decode QR
        decoded = decode(img)
        if not decoded:
            await interaction.followup.send("❌ Failed to decode QR code from the image.", ephemeral=True)
            return

        qr_text = decoded[0].data.decode("utf-8")

        # Step 3: Generate build
        matrix = generate_qr_matrix(qr_text)
        objects = qr_to_object_list(matrix, obj_type, CONFIG["origin_position"], scale)
        save_object_json(objects, CONFIG["object_output_path"])
        render_qr_preview(matrix, CONFIG["preview_output_path"], object_type=obj_type)
        create_qr_zip(
            CONFIG["object_output_path"],
            CONFIG["preview_output_path"],
            CONFIG["zip_output_path"],
            extra_text=f"(from image)\nQR Size: {len(matrix)}x{len(matrix[0])}\nTotal Objects: {len(objects)}\nObject Used: {obj_type}"
        )

        # Step 4: Post to configured gallery/admin channel
        channel_id = get_channel_id("gallery") or CONFIG["admin_channel_id"]
        channel = self.bot.get_channel(int(channel_id))

        if not channel:
            await interaction.followup.send("✅ Build created, but gallery channel was not found.", ephemeral=True)
            return

        await channel.send(
            content=f"📷 **QR Image Build Complete**\n• Decoded: `{qr_text}`\n• Size: {len(matrix)}x{len(matrix[0])}\n• Objects: {len(objects)}\n• Type: `{obj_type}`",
            files=[
                discord.File(CONFIG["zip_output_path"]),
                discord.File(CONFIG["preview_output_path"])
            ]
        )

        await interaction.followup.send("✅ QR image decoded and build posted in gallery channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QRImage(bot))
