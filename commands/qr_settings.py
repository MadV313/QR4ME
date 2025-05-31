import discord
from discord import app_commands
from discord.ext import commands

from utils.config_utils import get_guild_config, update_guild_config
from utils.permissions import is_admin_user

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
        spacing = OBJECT_SIZE_ADJUSTMENTS.get(obj_type, 1.0)
        box_size = config.get("defaultScale", 1.0)
        origin = config.get("origin_position", {"x": 5000, "y": 0, "z": 5000})

        embed = discord.Embed(
            title="🔧 Current QR Object Settings",
            color=0x00ffff
        )
        embed.add_field(name="Object Type", value=f"`{obj_type}`", inline=True)
        embed.add_field(name="Spacing Multiplier", value=f"`{spacing}`", inline=True)
        embed.add_field(name="Scale (Box Size)", value=f"`{box_size}`", inline=True)
        embed.add_field(
            name="Origin Position",
            value=f"`X: {origin.get('x', 0)} | Y: {origin.get('y', 0)} | Z: {origin.get('z', 0)}`",
            inline=False
        )
        embed.set_footer(text="You can adjust these values or confirm to regenerate with current settings.")

        view = ObjectInfoView(config=config, interaction=interaction)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name="set_map", description="Assign the map and placement coordinates for your QR")
    @app_commands.choices(map_name=MAP_CHOICES)
    @app_commands.describe(x="X coordinate", y="Y coordinate", z="Z coordinate")
    async def set_map(self, interaction: discord.Interaction, map_name: app_commands.Choice[str], x: float, y: float, z: float):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        config = get_guild_config(guild_id)
        config["origin_position"] = {"map": map_name.value, "x": x, "y": y, "z": z}
        update_guild_config(guild_id, config)

        await interaction.response.send_message(
            f"📍 Map and coordinates updated to `{map_name.value}` at X:{x} Y:{y} Z:{z}", ephemeral=True
        )

class ObjectInfoView(discord.ui.View):
    def __init__(self, config, interaction):
        super().__init__(timeout=60)
        self.config = config
        self.interaction = interaction

    @discord.ui.button(label="✅ Accept & Rebuild", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔁 Rebuilding QR code with current settings... (Trigger logic here)", ephemeral=True)
        # 🔧 You can trigger qrbuild here if wired via backend

    @discord.ui.button(label="⚙️ Adjust Settings", style=discord.ButtonStyle.blurple)
    async def adjust_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ObjectAdjustModal(config=self.config))

class ObjectAdjustModal(discord.ui.Modal, title="Adjust QR Settings"):
    object_type = discord.ui.TextInput(label="Object Type", placeholder="e.g. JerryCan", required=True)
    spacing = discord.ui.TextInput(label="Spacing Multiplier (0.1–2.0)", placeholder="e.g. 1.0", required=False)
    scale = discord.ui.TextInput(label="Scale (Box Size)", placeholder="e.g. 1.0", required=False)

    def __init__(self, config):
        super().__init__()
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)

        obj = self.object_type.value.strip()
        spacing_val = float(self.spacing.value.strip()) if self.spacing.value else 1.0
        scale_val = float(self.scale.value.strip()) if self.scale.value else 1.0

        self.config["default_object"] = obj
        self.config["defaultScale"] = scale_val
        OBJECT_SIZE_ADJUSTMENTS[obj] = spacing_val

        update_guild_config(guild_id, self.config)
        await interaction.response.send_message(
            f"✅ Settings updated:\n"
            f"• Object: `{obj}`\n"
            f"• Spacing: `{spacing_val}`\n"
            f"• Scale: `{scale_val}`\n\n"
            f"Now rerun `/qrbuild` or `/qrimage` to apply these changes.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(QRSettings(bot))
