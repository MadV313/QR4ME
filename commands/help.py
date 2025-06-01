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
            description="🛠️ Setup your build correctly by following the command flow below.\n"
                        "Make sure to run `/setorigin` and `/setmap` before building anything.\n\n"
                        "Here are the available bot commands:",
            color=discord.Color.blurple()
        )

        # 🔧 Setup Commands
        embed.add_field(
            name="🔧 Setup Commands",
            value=(
                "**/setorigin** — Set the in-game X/Y/Z coordinates for QR layout placement.\n"
                "**/setmap** — Choose the DayZ map (e.g., Chernarus, Livonia, Sakhalin) and its coordinates.\n"
                "**/objectinfo** — View and fine-tune object settings like scale, spacing, and origin.\n"
                "  ➤ Toggle the Mirror Test Kit on/off for CE testing.\n"
                "  ➤ Adjust object type used in builds.\n"
                "  ➤ Rebuild the last QR layout using updated settings."
            ),
            inline=False
        )

        # 🧱 Build Commands
        embed.add_field(
            name="🧱 Build Commands",
            value=(
                "**/qrbuild** — Convert a block of text or URL into a QR code layout using in-game objects.\n"
                "**/qrimage** — Upload a QR image (PNG/JPG) and convert it into a build layout.\n"
                "**/preview** — Re-post the last build’s preview image and export file (ZIP/JSON).\n"
                "**/pushgallery** — Push your latest build to the public gallery."
            ),
            inline=False
        )

        # ⚙️ Configuration & Management
        embed.add_field(
            name="⚙️ Configuration & Admin Tools",
            value=(
                "**/setchannel** — Assign admin, gallery, or log channels.\n"
                "**/giveperms** — Grant a user permission to use bot commands without an admin role.\n"
                "**/revokeperms** — Revoke a user’s permission to run QR bot commands.\n"
                "**/cleanup** — Delete the most recent build preview and ZIP/JSON output."
            ),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Help(bot))
