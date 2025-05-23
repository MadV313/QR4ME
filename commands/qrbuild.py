import discord
from discord.ext import commands
from discord import app_commands

from config import CONFIG
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip
from utils.channel_utils import get_channel_id
from utils.permissions import is_admin_user  # ✅ Updated permissions

class QRBuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="qrbuild", description="Convert text into a DayZ object QR layout")
    @app_commands.describe(
        text="The text or URL to encode as a QR code",
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
            app_commands.Choice(name="Armband (Black)", value="Armband_Black"),
            app_commands.Choice(name="Box Wooden", value="BoxWooden"),
        ]
    )
    async def qrbuild(
        self,
        interaction: discord.Interaction,
        text: str,
        object_type: app_commands.Choice[str],
        scale: float = 1.0
    ):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()
        obj_type = object_type.value

        # Step 1: Generate QR matrix
        matrix = generate_qr_matrix(text)

        # Step 2: Convert to object list
        objects = qr_to_object_list(matrix, obj_type, CONFIG["origin_position"], scale)

        # Step 3: Save JSON
        save_object_json(objects, CONFIG["object_output_path"])

        # Step 4: Render preview image
        render_qr_preview(matrix, CONFIG["preview_output_path"], object_type=obj_type)

        # Step 5: Zip it all up
        create_qr_zip(
            CONFIG["object_output_path"],
            CONFIG["preview_output_path"],
            CONFIG["zip_output_path"],
            extra_text=f"QR Size: {len(matrix)}x{len(matrix[0])}\nTotal Objects: {len(objects)}\nObject Used: {obj_type}"
        )

        # Step 6: Send ZIP and preview to configured channel
        channel_id = get_channel_id("gallery") or CONFIG["admin_channel_id"]
        channel = self.bot.get_channel(int(channel_id))

        if not channel:
            await interaction.followup.send("❌ Could not find configured channel.", ephemeral=True)
            return

        await channel.send(
            content=f"🧱 **QR Build Complete**\n• Size: {len(matrix)}x{len(matrix[0])}\n• Objects: {len(objects)}\n• Type: `{obj_type}`",
            files=[
                discord.File(CONFIG["zip_output_path"]),
                discord.File(CONFIG["preview_output_path"])
            ]
        )

        await interaction.followup.send("✅ QR build generated and posted in gallery channel.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QRBuild(bot))
