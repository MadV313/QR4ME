import discord
from discord.ext import commands
from discord import app_commands

from utils.permissions import remove_admin_user, is_admin_user

class RevokePerms(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="revokeperms", description="Remove a user's permission to use bot commands")
    @app_commands.describe(user="The user to revoke access from")
    async def revokeperms(self, interaction: discord.Interaction, user: discord.User):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        removed = remove_admin_user(user.id)

        if removed:
            await interaction.response.send_message(
                f"🛑 `{user.name}` has been revoked from using bot commands.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"ℹ️ `{user.name}` was not listed as a permitted user.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(RevokePerms(bot))
