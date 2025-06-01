import discord
from discord import app_commands
from discord.ext import commands
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode

from utils.config_utils import get_guild_config, save_guild_config
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip
from utils.channel_utils import get_channel_id
from utils.permissions import is_admin_user

class QRImage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="qrimage", description="Upload a QR code image to generate a DayZ object layout")
    @app_commands.describe(
        image="Upload a PNG or JPG of a QR code",
        scale="Overall object scale (default 0.5 or overridden per object)",
        object_spacing="Spacing between objects (default 1.0 or overridden per object)",
        object_type="Choose the object to use for QR layout",
        add_mirror="Add the MirrorTestKit background object (optional toggle)"
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
            app_commands.Choice(name="Armband (Black)", value="Armband_Black"),
            app_commands.Choice(name="Jerry Can", value="JerryCan"),
            app_commands.Choice(name="Box Wooden", value="BoxWooden"),
        ]
    )
    async def qrimage(
        self,
        interaction: discord.Interaction,
        image: discord.Attachment,
        object_type: app_commands.Choice[str],
        scale: float = None,
        object_spacing: float = None,
        add_mirror: bool = False
    ):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()
        obj_type = object_type.value
        guild_id = str(interaction.guild.id)
        config = get_guild_config(guild_id)
        origin = config.get("origin_position", {"x": 0.0, "y": 0.0, "z": 0.0})
        offset = config.get("originOffset", {"x": 0.0, "y": 0.0, "z": 0.0})

        # Fallback values
        scale = scale or config.get("custom_scale", {}).get(obj_type, config.get("defaultScale", 0.5))
        object_spacing = object_spacing or config.get("custom_spacing", {}).get(obj_type, config.get("defaultSpacing", 1.0))

        # Step 1: Decode the image
        img_bytes = await image.read()
        np_array = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

        decoded = decode(img)
        if not decoded:
            await interaction.followup.send("❌ Failed to decode QR code from the image.", ephemeral=True)
            return

        qr_text = decoded[0].data.decode("utf-8")

        # Step 2: Build matrix and objects
        matrix = generate_qr_matrix(qr_text)
        mirror_enabled = add_mirror or config.get("enable_mirror_test_kit", False)
        config["enable_mirror_test_kit"] = mirror_enabled
        objects = qr_to_object_list(matrix, obj_type, origin, offset, scale, object_spacing, include_mirror_kit=mirror_enabled)

        # Step 3: Save outputs
        save_object_json(objects, config["object_output_path"])
        render_qr_preview(matrix, config["preview_output_path"], object_type=obj_type)

        # Step 4: Save config
        config["default_object"] = obj_type
        config["defaultScale"] = scale
        config.setdefault("custom_spacing", {})[obj_type] = object_spacing
        config["last_qr_data"] = qr_text
        save_guild_config(guild_id, config)

        # Step 5: Send results to gallery
        channel_id = get_channel_id("gallery", guild_id) or config.get("admin_channel_id")
        channel = self.bot.get_channel(int(channel_id)) if channel_id else None

        if not channel:
            await interaction.followup.send("✅ Build created, but gallery channel was not found.", ephemeral=True)
            return

        await channel.send(
            content=(
                f"📷 **QR Image Build Complete**\n"
                f"• Decoded: `{qr_text}`\n"
                f"• Size: {len(matrix)}x{len(matrix[0])}\n"
                f"• Objects: {len(objects)}\n"
                f"• Type: `{obj_type}`\n"
                f"• Scale: `{scale}` | Spacing: `{object_spacing}`\n"
                f"• Origin: X: {origin['x']}, Y: {origin['y']}, Z: {origin['z']}\n"
                f"• Mirror Test Kit: {'Enabled' if mirror_enabled else 'Disabled'}"
            ),
            files=[
                discord.File(config["object_output_path"], filename="objects.json"),
                discord.File(config["preview_output_path"], filename="qr_preview.png")
            ]
        )

        await interaction.followup.send("✅ QR image decoded and build posted in gallery channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QRImage(bot))
