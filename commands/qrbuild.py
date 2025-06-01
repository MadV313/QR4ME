import discord
from discord.ext import commands
from discord import app_commands
import os

from utils.config_utils import get_guild_config, save_guild_config
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip
from utils.channel_utils import get_channel_id
from utils.permissions import is_admin_user

class QRBuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="qrbuild", description="Convert text into a DayZ object QR layout")
    @app_commands.describe(
        text="The text or URL to encode as a QR code",
        overall_scale="Overall object scale multiplier (default 0.5 or overridden per object)",
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
    async def qrbuild(
        self,
        interaction: discord.Interaction,
        text: str,
        object_type: app_commands.Choice[str],
        overall_scale: float = None,
        object_spacing: float = None,
        add_mirror: bool = False
    ):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()

        guild_id = str(interaction.guild.id)
        config = get_guild_config(guild_id)
        obj_type = object_type.value
        origin = config.get("origin_position", {"x": 0.0, "y": 0.0, "z": 0.0})
        offset = config.get("originOffset", {"x": 0.0, "y": 0.0, "z": 0.0})

        # Use stored or fallback config values
        overall_scale = overall_scale or config.get("custom_scale", {}).get(obj_type, config.get("defaultScale", 0.5))
        object_spacing = object_spacing or config.get("custom_spacing", {}).get(obj_type, config.get("defaultSpacing", 1.0))

        # Step 1: Generate QR matrix
        matrix = generate_qr_matrix(text)

        # Step 2: Generate object list
        objects = qr_to_object_list(matrix, obj_type, origin, offset, overall_scale, object_spacing)

        # ✅ Step 2.5: Add MirrorTestKit if runtime toggle is enabled
        mirror_enabled = add_mirror or config.get("enable_mirror_test_kit", False)
        if mirror_enabled:
            grid_width = len(matrix[0]) * object_spacing * overall_scale
            grid_height = len(matrix) * object_spacing * overall_scale
            mirror_obj = {
                "name": "MirrorTestKit",
                "pos": [origin["x"], origin["y"] - 0.01, origin["z"]],
                "ypr": [0.0, 90.0, 0.0],
                "scale": max(overall_scale * 12, 10.0),
                "enableCEPersistency": 0,
                "customString": ""
            }
            objects.insert(0, mirror_obj)

        # Step 3: Save JSON
        save_object_json(objects, config["object_output_path"])

        # Step 4: Preview render (MirrorTestKit is not rendered in preview)
        render_qr_preview(matrix, config["preview_output_path"], object_type=obj_type)

        # Step 5: Save updated config state
        config["default_object"] = obj_type
        config["defaultScale"] = overall_scale
        config.setdefault("custom_spacing", {})[obj_type] = object_spacing
        config["last_qr_data"] = text
        save_guild_config(guild_id, config)

        # Step 6: ZIP creation
        final_path = create_qr_zip(
            config["object_output_path"],
            config["preview_output_path"],
            config["zip_output_path"],
            extra_text=(
                f"QR Size: {len(matrix)}x{len(matrix[0])}\n"
                f"Total Objects: {len(objects)}\n"
                f"Object Used: {obj_type}\n"
                f"Scale: {overall_scale} | Spacing: {object_spacing}\n"
                f"Mirror Test Kit: {'Enabled' if mirror_enabled else 'Disabled'}"
            )
        )

        # Step 7: Send to gallery/admin channel
        channel_id = get_channel_id("gallery", guild_id) or config.get("admin_channel_id")
        channel = self.bot.get_channel(int(channel_id)) if channel_id else None

        if not channel:
            await interaction.followup.send("❌ Could not find configured gallery channel.", ephemeral=True)
            return

        await channel.send(
            content=(
                f"🧱 **QR Build Complete**\n"
                f"• Size: {len(matrix)}x{len(matrix[0])}\n"
                f"• Objects: {len(objects)}\n"
                f"• Type: `{obj_type}`\n"
                f"• Scale: `{overall_scale}` | Spacing: `{object_spacing}`\n"
                f"• Origin: X: {origin['x']}, Y: {origin['y']}, Z: {origin['z']}\n"
                f"• Mirror Test Kit: {'Enabled' if mirror_enabled else 'Disabled'}"
            ),
            files=[
                discord.File(final_path),
                discord.File(config["preview_output_path"])
            ]
        )

        await interaction.followup.send("✅ QR build generated and posted in gallery channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QRBuild(bot))
