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
            description="Here are the available commands:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="/qrbuild",
            value="Convert a text or link into a QR-coded object layout.",
            inline=False
        )
        embed.add_field(
            name="/qrimage",
            value="Upload a QR image (PNG/JPG) and generate a build layout.",
            inline=False
        )
        embed.add_field(
            name="/preview",
            value="Re-send the most recent QR preview image + zip (if available).",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
