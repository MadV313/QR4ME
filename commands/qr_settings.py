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

OBJECT_OPTIONS = [
    discord.SelectOption(label=name, value=name) for name in OBJECT_SIZE_ADJUSTMENTS.keys()
]

class QRSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="object_info", description="View current QR object settings and optionally rebuild")
    async def object_info(self, interaction: discord.Interaction):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        config = get_guild_config(guild_id)
        obj = config.get("default_object", "SmallProtectiveCase")
        spacing = config.get("custom_spacing", {}).get(obj, OBJECT_SIZE_ADJUSTMENTS.get(obj, 1.0))
        scale = config.get("custom_scale", {}).get(obj, config.get("defaultScale", 0.5))
        origin = config.get("origin_position", {"x": 5000.0, "y": 0.0, "z": 5000.0})

        embed = discord.Embed(title="🔧 Current QR Object Settings", color=0x00ffff)
        embed.add_field(name="Object Type", value=f"`{obj}`", inline=True)
        embed.add_field(name="Spacing Multiplier", value=f"`{spacing}`", inline=True)
        embed.add_field(name="Scale (Box Size)", value=f"`{scale}`", inline=True)
        embed.add_field(name="Origin", value=f"`X: {origin['x']}` | `Y: {origin['y']}` | `Z: {origin['z']}`", inline=False)

        view = ObjectInfoButtons(config=config, guild_id=guild_id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ObjectInfoButtons(discord.ui.View):
    def __init__(self, config, guild_id):
        super().__init__(timeout=60)
        self.config = config
        self.guild_id = guild_id

    @discord.ui.button(label="✅ Approve + Rebuild", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "last_qr_data" not in self.config:
            await interaction.response.send_message("⚠️ No previous QR text found. Run `/qrbuild` or `/qrimage` first.", ephemeral=True)
            return

        await handle_qr_rebuild(interaction, self.config, self.guild_id)

    @discord.ui.button(label="⚙️ Adjust Settings", style=discord.ButtonStyle.blurple)
    async def adjust(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🛠️ Adjust your QR settings below:", view=AdjustQRSettings(self.config, self.guild_id), ephemeral=True)

class AdjustQRSettings(discord.ui.View):
    def __init__(self, config, guild_id):
        super().__init__(timeout=120)
        self.config = config
        self.guild_id = guild_id

        # Current values from config
        current_obj = config.get("default_object", "SmallProtectiveCase")
        current_spacing = str(config.get("custom_spacing", {}).get(current_obj, OBJECT_SIZE_ADJUSTMENTS.get(current_obj, 1.0)))
        current_scale = str(config.get("custom_scale", {}).get(current_obj, config.get("defaultScale", 0.5)))
        origin = config.get("origin_position", {"x": 5000.0, "y": 0.0, "z": 5000.0})

        # Dropdown to select object type
        self.object_select = discord.ui.Select(
            placeholder="Select Object Type",
            options=OBJECT_OPTIONS,
            default=discord.SelectOption(label=current_obj, value=current_obj)
        )
        self.object_select.callback = self.select_object
        self.add_item(self.object_select)

        # Pre-filled editable fields
        self.spacing_input = discord.ui.TextInput(
            label="Spacing (e.g. 1.0)", default=current_spacing, required=False
        )
        self.scale_input = discord.ui.TextInput(
            label="Scale (e.g. 0.5)", default=current_scale, required=False
        )
        self.x_input = discord.ui.TextInput(
            label="Origin X", default=str(origin.get("x", 5000.0)), required=False
        )
        self.y_input = discord.ui.TextInput(
            label="Origin Y", default=str(origin.get("y", 0.0)), required=False
        )
        self.z_input = discord.ui.TextInput(
            label="Origin Z", default=str(origin.get("z", 5000.0)), required=False
        )

        # Add text fields to view
        for field in [self.spacing_input, self.scale_input, self.x_input, self.y_input, self.z_input]:
            self.add_item(field)

        # Submit button
        self.add_item(SubmitButton(self))

    async def select_object(self, interaction: discord.Interaction):
        selected = self.object_select.values[0]
        await interaction.response.send_message(f"Selected: `{selected}`. You can now edit fields and press Submit.", ephemeral=True)

class SubmitButton(discord.ui.Button):
    def __init__(self, view):
        super().__init__(label="Submit + Rebuild", style=discord.ButtonStyle.success)
        self.custom_view = view

    async def callback(self, interaction: discord.Interaction):
        config = self.custom_view.config
        guild_id = self.custom_view.guild_id

        obj = self.custom_view.object_select.values[0]
        spacing_val = float(self.custom_view.spacing_input.value) if self.custom_view.spacing_input.value else OBJECT_SIZE_ADJUSTMENTS.get(obj, 1.0)
        scale_val = float(self.custom_view.scale_input.value) if self.custom_view.scale_input.value else 0.5
        x = float(self.custom_view.x_input.value) if self.custom_view.x_input.value else 5000.0
        y = float(self.custom_view.y_input.value) if self.custom_view.y_input.value else 0.0
        z = float(self.custom_view.z_input.value) if self.custom_view.z_input.value else 5000.0

        config["default_object"] = obj
        config.setdefault("custom_spacing", {})[obj] = spacing_val
        config.setdefault("custom_scale", {})[obj] = scale_val
        config["origin_position"] = {"x": x, "y": y, "z": z}
        update_guild_config(guild_id, config)

        if "last_qr_data" not in config:
            await interaction.response.send_message("⚠️ No previous QR text found. Run `/qrbuild` or `/qrimage` first.", ephemeral=True)
            return

        await handle_qr_rebuild(interaction, config, guild_id)

async def handle_qr_rebuild(interaction: discord.Interaction, config: dict, guild_id: str):
    qr_text = config["last_qr_data"]
    obj = config.get("default_object", "SmallProtectiveCase")
    scale = config.get("custom_scale", {}).get(obj, config.get("defaultScale", 0.5))
    spacing = config.get("custom_spacing", {}).get(obj, config.get("defaultSpacing", 1.0))
    origin = config.get("origin_position", {"x": 5000.0, "y": 0.0, "z": 5000.0})
    offset = config.get("originOffset", {"x": 0.0, "y": 0.0, "z": 0.0})

    matrix = generate_qr_matrix(qr_text)
    objects = qr_to_object_list(matrix, obj, origin, offset, scale, spacing)
    save_object_json(objects, config["object_output_path"])
    render_qr_preview(matrix, config["preview_output_path"], object_type=obj)
    create_qr_zip(config["object_output_path"], config["preview_output_path"], config["zip_output_path"])

    channel_id = get_channel_id("gallery", guild_id) or config.get("admin_channel_id")
    channel = interaction.client.get_channel(int(channel_id)) if channel_id else None

    if channel:
        await channel.send(
            content=(
                f"🧱 **QR Build Regenerated**\n"
                f"• Size: {len(matrix)}x{len(matrix[0])}\n"
                f"• Objects: {len(objects)}\n"
                f"• Type: `{obj}`\n"
                f"• Scale: `{scale}` | Spacing: `{spacing}`\n"
                f"• Origin: X: {origin['x']}, Y: {origin['y']}, Z: {origin['z']}"
            ),
            files=[
                discord.File(config["zip_output_path"]),
                discord.File(config["preview_output_path"])
            ]
        )
    await interaction.response.send_message("✅ Settings updated and QR rebuilt.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(QRSettings(bot))
