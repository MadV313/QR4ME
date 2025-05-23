import discord
from discord.ext import commands
from discord import app_commands

from config import CONFIG
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip

class QRBuild(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, interaction: discord.Interaction):
        if not CONFIG["admin_roles"]:
            return True
        user_roles = [str(role.id) for role in interaction.user.roles]
        return any(role in CONFIG["admin_roles"] for role in user_roles)

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
        ]
    )
    async def qrbuild(
        self,
        interaction: discord.Interaction,
        text: str,
        object_type: str = "SmallProtectiveCase",
        scale: float = 1.0
    ):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        await interaction.response.defer()

        # Step 1: Generate QR matrix
        matrix = generate_qr_matrix(text)

        # Step 2: Convert to object list
        objects = qr_to_object_list(matrix, object_type, CONFIG["origin_position"], scale)

        # Step 3: Save JSON
        save_object_json(objects, CONFIG["object_output_path"])

        # Step 4: Render preview image
        render_qr_preview(matrix, CONFIG["preview_output_path"], object_type=object_type)

        # Step 5: Zip it all up
        create_qr_zip(
            CONFIG["object_output_path"],
            CONFIG["preview_output_path"],
            CONFIG["zip_output_path"],
            extra_text=f"QR Size: {len(matrix)}x{len(matrix[0])}\nTotal Objects: {len(objects)}\nObject Used: {object_type}"
        )

        # Step 6: Send ZIP and preview to admin channel
        channel = self.bot.get_channel(int(CONFIG["admin_channel_id"]))
        if not channel:
            await interaction.followup.send("❌ Could not find admin channel.")
            return

        await channel.send(
            content=f"🧱 **QR Build Complete**\n• Size: {len(matrix)}x{len(matrix[0])}\n• Objects: {len(objects)}\n• Type: `{object_type}`",
            files=[
                discord.File(CONFIG["zip_output_path"]),
                discord.File(CONFIG["preview_output_path"])
            ]
        )

        await interaction.followup.send("✅ QR build generated and posted in admin channel.")

# ✅ Proper setup function
async def setup(bot):
    await bot.add_cog(QRBuild(bot))
