import discord
from discord.ext import commands
from discord import app_commands

from utils.permissions import add_admin_user, is_admin_user  # ✅ Updated to support per-guild

class GivePerms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="giveperms", description="Grant another user permission to use bot commands")
    @app_commands.describe(user="The user to grant admin-like access to")
    async def giveperms(self, interaction: discord.Interaction, user: discord.User):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        add_admin_user(interaction.guild_id, user.id)  # ✅ now scoped to guild

        await interaction.response.send_message(
            f"✅ `{user.name}` has been granted permission to use bot commands in this server.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(GivePerms(bot))
