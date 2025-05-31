import discord
from discord import app_commands
from discord.ext import commands

from utils.config_utils import get_guild_config, update_guild_config
from utils.permissions import is_admin_user
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip
from utils.channel_utils import get_channel_id

OBJECT_SIZE_ADJUSTMENTS = {
    "SmallProtectiveCase": 1.0,
    "SmallProtectorCase": 1.0,
    "DryBag_Black": 1.25,
    "PlasticBottle": 0.75,
    "CookingPot": 0.8,
    "MetalWire": 0.6,
    "ImprovisedContainer": 1.0,
    "WoodenCrate": 1.1,
    "Armband_Black": 0.5,
    "JerryCan": 1.0,
    "BoxWooden": 1.0
}

MAP_CHOICES = [
    app_commands.Choice(name="Chernarus", value="Chernarus"),
    app_commands.Choice(name="Livonia", value="Livonia"),
    app_commands.Choice(name="Sakhal", value="Sakhal")
]

class QRSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="object_info", description="View current QR object settings and adjust if needed")
    async def object_info(self, interaction: discord.Interaction):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        config = get_guild_config(guild_id)
        obj_type = config.get("default_object", "SmallProtectiveCase")
        spacing = config.get("custom_spacing", {}).get(obj_type, OBJECT_SIZE_ADJUSTMENTS.get(obj_type, 1.0))
        box_size = config.get("custom_scale", {}).get(obj_type, config.get("defaultScale", 1.0))
        origin = config.get("origin_position", {"x": 5000, "y": 0, "z": 5000})

        embed = discord.Embed(title="🔧 Current QR Object Settings", color=0x00ffff)
        embed.add_field(name="Object Type", value=f"`{obj_type}`", inline=True)
        embed.add_field(name="Spacing Multiplier", value=f"`{spacing}`", inline=True)
        embed.add_field(name="Scale (Box Size)", value=f"`{box_size}`", inline=True)
        embed.add_field(
            name="Origin Position",
            value=f"`X: {origin.get('x', 0)} | Y: {origin.get('y', 0)} | Z: {origin.get('z', 0)}`",
            inline=False
        )
        embed.set_footer(text="You can adjust these values below. Your changes will trigger a new build.")

        view = ObjectInfoView(config=config, interaction=interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ObjectInfoView(discord.ui.View):
    def __init__(self, config, interaction):
        super().__init__(timeout=60)
        self.config = config
        self.interaction = interaction

    @discord.ui.button(label="⚙️ Adjust + Rebuild", style=discord.ButtonStyle.green)
    async def adjust_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ObjectAdjustModal(config=self.config))

class ObjectAdjustModal(discord.ui.Modal, title="Adjust QR Settings"):
    object_type = discord.ui.TextInput(label="Object Type", placeholder="e.g. JerryCan", required=True)
    spacing = discord.ui.TextInput(label="Spacing Multiplier", placeholder="e.g. 1.0", required=False)
    scale = discord.ui.TextInput(label="Scale (Box Size)", placeholder="e.g. 0.5", required=False)
    origin_x = discord.ui.TextInput(label="Origin X", placeholder="e.g. 5000.0", required=False)
    origin_y = discord.ui.TextInput(label="Origin Y", placeholder="e.g. 0.0", required=False)
    origin_z = discord.ui.TextInput(label="Origin Z", placeholder="e.g. 5000.0", required=False)

    def __init__(self, config):
        super().__init__()
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)

        obj = self.object_type.value.strip()
        spacing_val = float(self.spacing.value.strip()) if self.spacing.value else OBJECT_SIZE_ADJUSTMENTS.get(obj, 1.0)
        scale_val = float(self.scale.value.strip()) if self.scale.value else 1.0
        x = float(self.origin_x.value.strip()) if self.origin_x.value else 5000.0
        y = float(self.origin_y.value.strip()) if self.origin_y.value else 0.0
        z = float(self.origin_z.value.strip()) if self.origin_z.value else 5000.0

        # Update and save
        self.config["default_object"] = obj
        self.config.setdefault("custom_spacing", {})[obj] = spacing_val
        self.config.setdefault("custom_scale", {})[obj] = scale_val
        self.config["origin_position"] = {"x": x, "y": y, "z": z}
        update_guild_config(guild_id, self.config)

        # Rebuild logic
        if "last_qr_data" not in self.config:
            await interaction.response.send_message("⚠️ No previous QR text found. Run `/qrbuild` or `/qrimage` first.", ephemeral=True)
            return

        qr_text = self.config["last_qr_data"]
        offset = self.config.get("originOffset", {"x": 0.0, "y": 0.0, "z": 0.0})
        matrix = generate_qr_matrix(qr_text)
        objects = qr_to_object_list(matrix, obj, {"x": x, "y": y, "z": z}, offset, scale_val, spacing_val)
        save_object_json(objects, self.config["object_output_path"])
        render_qr_preview(matrix, self.config["preview_output_path"], object_type=obj)
        create_qr_zip(self.config["object_output_path"], self.config["preview_output_path"], self.config["zip_output_path"])

        # Send to gallery
        channel_id = get_channel_id("gallery", guild_id) or self.config.get("admin_channel_id")
        channel = interaction.client.get_channel(int(channel_id)) if channel_id else None

        if channel:
            await channel.send(
                content=(
                    f"🛠️ **QR Build Regenerated**\n"
                    f"• Size: {len(matrix)}x{len(matrix[0])}\n"
                    f"• Objects: {len(objects)}\n"
                    f"• Type: `{obj}`\n"
                    f"• Scale: `{scale_val}` | Spacing: `{spacing_val}`\n"
                    f"• Origin: X: {x}, Y: {y}, Z: {z}"
                ),
                files=[
                    discord.File(self.config["zip_output_path"]),
                    discord.File(self.config["preview_output_path"])
                ]
            )

        await interaction.response.send_message("✅ Settings updated and QR rebuilt.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QRSettings(bot))
