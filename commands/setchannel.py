import discord
from discord.ext import commands
from discord import app_commands

from utils.channel_utils import save_channel
from utils.permissions import is_admin_user  # ✅ Centralized permission logic

class SetChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setchannel", description="Assign a bot channel role like admin or gallery")
    @app_commands.describe(
        type="The type of channel to assign (admin or gallery)",
        target="The channel to assign this role to"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="Admin Channel", value="admin"),
        app_commands.Choice(name="Gallery Channel", value="gallery")
    ])
    async def setchannel(
        self,
        interaction: discord.Interaction,
        type: app_commands.Choice[str],
        target: discord.abc.GuildChannel
    ):
        if not is_admin_user(interaction):
            await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
            return

        # Validate it is a text-based channel
        if not isinstance(target, discord.TextChannel):
            await interaction.response.send_message("❌ Please select a valid text channel.", ephemeral=True)
            return

        # Ensure the bot has permission to send messages in that channel
        permissions = target.permissions_for(interaction.guild.me)
        if not permissions.send_messages:
            await interaction.response.send_message(
                f"❌ I don't have permission to send messages in {target.mention}.",
                ephemeral=True
            )
            return

        # Save channel mapping under this server
        guild_id = str(interaction.guild.id)
        save_channel(guild_id, type.value, str(target.id))

        await interaction.response.send_message(
            f"✅ `{type.name}` successfully assigned to {target.mention}.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(SetChannel(bot))
