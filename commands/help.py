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
        embed.add_field(
            name="/pushgallery",
            value="Push the most recent build into the public gallery page.",
            inline=False
        )
        embed.add_field(
            name="/setorigin",
            value="Set the base world coordinates where QR layouts are placed.",
            inline=False
        )
        embed.add_field(
            name="/setchannel",
            value="Assign a channel for bot functions like admin, gallery, or log.",
            inline=False
        )
        embed.add_field(
            name="/giveperms",
            value="Grant a user permission to run bot commands without admin role.",
            inline=False
        )
        embed.add_field(
            name="/cleanup",
            value="Delete the most recent preview image and zip build.",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
