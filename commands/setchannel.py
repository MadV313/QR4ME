import discord
from discord.ext import commands
from discord import app_commands
from config import CONFIG
from utils.channel_utils import save_channel

class SetChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def is_admin(self, interaction: discord.Interaction):
        if not CONFIG["admin_roles"]:
            return True
        user_roles = [str(role.id) for role in interaction.user.roles]
        return any(role in CONFIG["admin_roles"] for role in user_roles)

    @app_commands.command(name="setchannel", description="Assign a bot channel role like admin, gallery, or log")
    @app_commands.describe(
        type="The type of channel to assign (admin, gallery, log)",
        target="The channel to assign this role to"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="Admin Channel", value="admin"),
        app_commands.Choice(name="Gallery Channel", value="gallery"),
        app_commands.Choice(name="Log Channel", value="log")
    ])
    async def setchannel(self, interaction: discord.Interaction, type: app_commands.Choice[str], target: discord.TextChannel):
        if not self.is_admin(interaction):
            await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
            return

        save_channel(type.value, str(target.id))
        await interaction.response.send_message(
            f"✅ `{type.name}` successfully assigned to {target.mention}.", ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(SetChannel(bot))
