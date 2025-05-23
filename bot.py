import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio

from config import CONFIG
from qr_generator import generate_qr_matrix, qr_to_object_list, save_object_json
from preview_renderer import render_qr_preview
from zip_packager import create_qr_zip

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

# --- Slash Command: /qrbuild ---
@bot.tree.command(name="qrbuild", description="Convert text into a DayZ object QR layout")
@app_commands.describe(
    text="The text or URL to encode as a QR code",
    scale="Spacing between objects (default 1.0)",
    object_type="DayZ object to use (default: SmallProtectorCase)"
)
async def qrbuild(interaction: discord.Interaction, text: str, scale: float = 1.0, object_type: str = "SmallProtectorCase"):
    if not is_admin(interaction):
        await interaction.response.send_message("❌ You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer()

    # Step 1: Generate QR matrix
    matrix = generate_qr_matrix(text)

    # Step 2: Convert to object list
    objects = qr_to_object_list(matrix, object_type, CONFIG["origin_position"], scale)

    # Step 3: Save JSON
    save_object_json(objects, CONFIG["object_output_path"])

    # Step 4: Render preview image
    render_qr_preview(matrix, CONFIG["preview_output_path"])

    # Step 5: Zip it all up
    create_qr_zip(
        CONFIG["object_output_path"],
        CONFIG["preview_output_path"],
        CONFIG["zip_output_path"],
        extra_text=f"QR Size: {len(matrix)}x{len(matrix[0])}\nTotal Objects: {len(objects)}\nObject Used: {object_type}"
    )

    # Step 6: Send ZIP and preview to admin channel
    channel = bot.get_channel(int(CONFIG["admin_channel_id"]))
    if not channel:
        await interaction.followup.send("❌ Could not find admin channel.")
        return

    await channel.send(
        content=f"🧱 **QR Build Complete**\n• Size: {len(matrix)}x{len(matrix[0])}\n• Objects: {len(objects)}\n• Type: `{object_type}`",
        files=[
            discord.File(CONFIG["zip_output_path"]),
            discord.File(CONFIG["preview_output_path"])
        ]
    )

    await interaction.followup.send("✅ QR build generated and posted in admin channel.")

# --- Extension Loader ---
async def load_extensions():
    await bot.load_extension("commands.qrimage")

# --- Launch Bot ---
if __name__ == "__main__":
    asyncio.run(load_extensions())
    token = os.getenv("DISCORD_BOT_TOKEN") or CONFIG["discord_token"]
    bot.run(token)
