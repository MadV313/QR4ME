import discord
from discord import app_commands
from discord.ext import commands
import asyncio

from utils.config_utils import get_guild_config, update_guild_config
from utils.permissions import is_admin_user
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip
from utils.channel_utils import get_channel_id

OBJECT_SIZE_ADJUSTMENTS = {
    "SmallProtectiveCase": 1.0,
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
        view = QRAdjustPanelView(config, guild_id)
        embed = view.build_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        view.message = await interaction.original_response()

class QRAdjustPanelView(discord.ui.View):
    def __init__(self, config, guild_id):
        super().__init__(timeout=900)
        self.config = config
        self.guild_id = guild_id
        self.message = None

    def build_embed(self):
        obj = self.config.get("default_object", "SmallProtectiveCase")
        spacing = self.config.get("custom_spacing", {}).get(obj, OBJECT_SIZE_ADJUSTMENTS.get(obj, 1.0))
        scale = self.config.get("custom_scale", {}).get(obj, self.config.get("defaultScale", 0.5))
        origin = self.config.get("origin_position", {"x": 5000.0, "y": 0.0, "z": 5000.0})

        embed = discord.Embed(title="🔧 Adjust QR Settings", color=0x00ffff)
        embed.add_field(name="Object Type", value=f"`{obj}`", inline=True)
        embed.add_field(name="Spacing", value=f"`{spacing}`", inline=True)
        embed.add_field(name="Scale", value=f"`{scale}`", inline=True)
        embed.add_field(name="Origin", value=f"`X: {origin['x']}, Y: {origin['y']}, Z: {origin['z']}`", inline=False)
        return embed

    async def interaction_check(self, interaction: discord.Interaction):
        return is_admin_user(interaction)

    @discord.ui.button(label="🧱 Adjust Object", style=discord.ButtonStyle.secondary)
    async def adjust_object(self, interaction: discord.Interaction, button: discord.ui.Button):
        options = [
            discord.SelectOption(label=obj, value=obj)
            for obj in OBJECT_SIZE_ADJUSTMENTS.keys()
        ]
        select = discord.ui.Select(placeholder="Select object", options=options)
        view = discord.ui.View(timeout=60)
        view.add_item(select)

        async def callback(i: discord.Interaction):
            selected = select.values[0]
            self.config["default_object"] = selected
            update_guild_config(self.guild_id, self.config)
            await i.response.send_message(f"✅ Object changed to `{selected}`", ephemeral=True, delete_after=2)
            if self.message:
                await self.message.edit(embed=self.build_embed(), view=self)
            try:
                await i.message.delete()
            except:
                pass

        select.callback = callback
        await interaction.response.send_message("🔄 Choose object:", view=view, ephemeral=True)

    @discord.ui.button(label="📏 Adjust Scale", style=discord.ButtonStyle.secondary)
    async def adjust_scale(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AdjustScaleModal(self))

    @discord.ui.button(label="📐 Adjust Spacing", style=discord.ButtonStyle.secondary)
    async def adjust_spacing(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AdjustSpacingModal(self))

    @discord.ui.button(label="🌍 Adjust Origin", style=discord.ButtonStyle.secondary)
    async def adjust_origin(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(AdjustOriginModal(self))

    @discord.ui.button(label="✅ Approve + Rebuild", style=discord.ButtonStyle.green)
    async def approve_and_rebuild(self, interaction: discord.Interaction, button: discord.ui.Button):
        if "last_qr_data" not in self.config:
            await interaction.response.send_message("⚠️ No previous QR data found. Use `/qrimage` or `/qrbuild` first.", ephemeral=True)
            return
        if self.message:
            try:
                await self.message.delete()
            except:
                pass
        await interaction.response.defer(ephemeral=True)
        await handle_qr_rebuild(interaction, self.config, self.guild_id)

class AdjustScaleModal(discord.ui.Modal, title="Set Scale"):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.add_item(discord.ui.TextInput(label="Scale", placeholder="e.g. 0.5", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            obj = self.view.config.get("default_object", "SmallProtectiveCase")
            val = float(self.children[0].value)
            self.view.config.setdefault("custom_scale", {})[obj] = val
            update_guild_config(self.view.guild_id, self.view.config)
            await interaction.response.edit_message(embed=self.view.build_embed(), view=self.view)
        except ValueError:
            await interaction.response.send_message("❌ Invalid scale. Use a numeric value.", ephemeral=True)

class AdjustSpacingModal(discord.ui.Modal, title="Set Spacing"):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.add_item(discord.ui.TextInput(label="Spacing", placeholder="e.g. 1.0", required=True))

    async def on_submit(self, interaction: discord.Interaction):
        try:
            obj = self.view.config.get("default_object", "SmallProtectiveCase")
            val = float(self.children[0].value)
            self.view.config.setdefault("custom_spacing", {})[obj] = val
            update_guild_config(self.view.guild_id, self.view.config)
            await interaction.response.edit_message(embed=self.view.build_embed(), view=self.view)
        except ValueError:
            await interaction.response.send_message("❌ Invalid spacing. Use a numeric value.", ephemeral=True)

class AdjustOriginModal(discord.ui.Modal, title="Set Origin Coordinates"):
    def __init__(self, view):
        super().__init__()
        self.view = view
        origin = view.config.get("origin_position", {"x": 5000.0, "y": 0.0, "z": 5000.0})
        self.x_input = discord.ui.TextInput(label="Origin X", default=str(origin["x"]), required=True)
        self.y_input = discord.ui.TextInput(label="Origin Y", default=str(origin["y"]), required=True)
        self.z_input = discord.ui.TextInput(label="Origin Z", default=str(origin["z"]), required=True)
        self.add_item(self.x_input)
        self.add_item(self.y_input)
        self.add_item(self.z_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            x = float(self.x_input.value)
            y = float(self.y_input.value)
            z = float(self.z_input.value)
            self.view.config["origin_position"] = {"x": x, "y": y, "z": z}
            update_guild_config(self.view.guild_id, self.view.config)
            await interaction.response.edit_message(embed=self.view.build_embed(), view=self.view)
        except ValueError:
            await interaction.response.send_message("❌ Invalid origin values. Use numeric coordinates.", ephemeral=True)

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
    render_qr_preview(matrix, config["preview_output_path"], object_type=config.get("default_object", obj))
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
    await interaction.followup.send("✅ Settings applied and QR rebuilt.", ephemeral=True)
