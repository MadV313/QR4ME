import discord
from discord.ext import commands
from discord import app_commands

from utils.config_utils import get_guild_config, save_guild_config
from utils.permissions import is_admin_user

class SetOrigin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setorigin", description="Update the origin position for QR placement")
    @app_commands.describe(
        x="X coordinate",
        y="Y coordinate (default 0.0)",
        z="Z coordinate"
    )
    async def setorigin(self, interaction: discord.Interaction, x: float, z: float, y: float = 0.0):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        config = get_guild_config(guild_id)

        config["origin_position"] = {"x": x, "y": y, "z": z}
        save_guild_config(guild_id, config)

        await interaction.response.send_message(
            f"📍 **New origin position set for this server:**\n"
            f"> `X`: {x}\n> `Y`: {y}\n> `Z`: {z}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(SetOrigin(bot))
