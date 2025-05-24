import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import json

from config import CONFIG
from utils.permissions import add_admin_user  # ✅ Added for owner auto-permit

# --- Bot Setup ---
intents = discord.Intents.default()
intents.guilds = True  # Required for on_guild_join
bot = commands.Bot(command_prefix="!", intents=intents)

# --- Auto Config Setup ---
def load_or_init_guild_config(guild_id: int, invoking_user_id: int) -> dict:
    path = f"data/configs/config_{guild_id}.json"
    os.makedirs("data/configs", exist_ok=True)

    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)

    new_config = {
        "admin_roles": [],
        "permitted_users": [str(invoking_user_id)],
        "origin_position": { "x": 5000.0, "y": 0.0, "z": 5000.0 },
        "preview_output_path": f"previews/{guild_id}_preview.png",
        "object_output_path": f"data/objects_{guild_id}.json",
        "zip_output_path": f"outputs/{guild_id}_qr.zip",
        "admin_channel_id": None
    }

    with open(path, "w") as f:
        json.dump(new_config, f, indent=2)

    print(f"[+] Auto-config created for guild {guild_id}")
    return new_config

# --- On Join: Auto-generate guild config and auto-permit owner ---
@bot.event
async def on_guild_join(guild):
    try:
        owner = guild.owner or (await guild.fetch_owner())
        load_or_init_guild_config(guild.id, owner.id)
        add_admin_user(owner.id, str(guild.id))  # ✅ Auto grant permission
        print(f"[+] Initialized config and permission for: {guild.name} ({guild.id})")
    except Exception as e:
        print(f"❌ Failed to create config for {guild.id}: {e}")

# --- Bot Ready Event ---
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"🔁 Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# --- Legacy Admin Role Check (fallback for core config use) ---
def is_admin(interaction: discord.Interaction):
    if not CONFIG["admin_roles"]:
        return True
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
