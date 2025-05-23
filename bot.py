import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

from config import CONFIG

# --- Bot Setup ---
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# --- Optional: Check for Admin Role IDs ---
def is_admin(interaction: discord.Interaction):
    if not CONFIG["admin_roles"]:
        return True  # allow if no roles defined
    user_roles = [str(role.id) for role in interaction.user.roles]
    return any(role in CONFIG["admin_roles"] for role in user_roles)

# --- Extension Loader ---
async def load_extensions():
    await bot.load_extension("commands.qrbuild")
    await bot.load_extension("commands.qrimage")
    await bot.load_extension("commands.preview")
    await bot.load_extension("commands.pushgallery")
    await bot.load_extension("commands.setorigin")
    await bot.load_extension("commands.setchannel")
    await bot.load_extension("commands.cleanup")
    await bot.load_extension("commands.giveperms")
    await bot.load_extension("commands.revokeperms")
    await bot.load_extension("commands.help")

# --- Launch Bot ---
if __name__ == "__main__":
    asyncio.run(load_extensions())
    token = os.getenv("DISCORD_BOT_TOKEN") or CONFIG["discord_token"]
    bot.run(token)
