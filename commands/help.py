import discord
from discord.ext import commands
from discord import app_commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Show command usage for QR-Build Bot")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📘 QR-Build Bot Help",
            description="Here are the available bot commands and what they do:",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="/qrbuild",
            value="🔤 Convert a block of text or URL into a grid of DayZ objects (QR format).",
            inline=False
        )
        embed.add_field(
            name="/qrimage",
            value="🖼️ Upload a QR code image (PNG/JPG) and generate a build layout from it.",
            inline=False
        )
        embed.add_field(
            name="/preview",
            value="📦 Re-post the most recent build's preview image and ZIP output.",
            inline=False
        )
        embed.add_field(
            name="/pushgallery",
            value="🌐 Push the most recent build into the public gallery and index it.",
            inline=False
        )
        embed.add_field(
            name="/setorigin",
            value="📍 Update the world coordinate (X/Y/Z) used as the center of QR layouts.",
            inline=False
        )
        embed.add_field(
            name="/setchannel",
            value="📢 Assign channels used for bot output: admin, gallery, or log.",
            inline=False
        )
        embed.add_field(
            name="/giveperms",
            value="✅ Grant a user permission to run QR commands without admin role.",
            inline=False
        )
        embed.add_field(
            name="/revokeperms",
            value="🚫 Revoke a user's permission to run bot commands.",
            inline=False
        )
        embed.add_field(
            name="/cleanup",
            value="🧹 Delete the last preview and ZIP build from the bot's output.",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
