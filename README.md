# 🧱 QR-Build Bot for DayZ (QR4ME)

A Discord bot that converts a QR code (text or image) into a grid of in-game DayZ objects (e.g. SmallProtectiveCase), auto-aligned to a Mirror Test Kit location. Used to generate scannable QR layouts for creative builds inside DayZ servers.

---

## ✨ Features

- `/qrbuild` — Converts input **text or URL** into a QR layout
- `/qrimage` — Upload and decode a **QR code image (PNG/JPG)**
- Uses in-game **DayZ objects** (e.g. Wooden Crate, Cooking Pot)
- Auto-centered over origin coordinates (Mirror Test Kit base)
- PNG **preview render** using object thumbnails
- **ZIP pack** generation (JSON, preview, README)
- Admin-only usage + `/giveperms` to allow trusted users
- Dynamic `/setchannel` for assigning bot output channels
- `/pushgallery` — Add builds to a public web gallery
- `/preview` — Re-send the most recent ZIP + preview
- `/cleanup` — Remove previous preview and zip
- `/setorigin` — Update base coordinate placement

---

## 🗂️ Output Per Build

Each QR layout includes:

- `data/objects.json` — Placement of all objects
- `previews/qr_preview.png` — Visual layout (top-down)
- `outputs/qr_code.zip` — Download package
- `README.txt` (inside ZIP) — Build info summary

---

## 🔧 Setup Instructions

1. Clone this repo:
   ```bash
   git clone https://github.com/YOURNAME/qr4me-bot.git
   cd qr4me-bot
   ```

2. Create your config:

   - Option A: Use `.env` on Railway/hosted environments:
     ```
     DISCORD_BOT_TOKEN=your-token
     ADMIN_CHANNEL_ID=1234567890
     ADMIN_ROLE_IDS=111,222
     ```

   - Option B: Or fill in `config.json` manually:
     ```json
     {
       "discord_token": "YOUR_DISCORD_BOT_TOKEN",
       "admin_channel_id": "YOUR_CHANNEL_ID",
       "admin_roles": ["ROLE_ID_1", "ROLE_ID_2"],
       "origin_position": { "x": 5000.0, "y": 0.0, "z": 5000.0 }
     }
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the bot:
   ```bash
   python bot.py
   ```

---

## 🌐 Public Gallery Support

After using `/pushgallery`, a copy of the preview and ZIP will be moved into the `/public/gallery` folder and indexed in `data/gallery.json`.

- Default gallery webpage:
  ```
  public/gallery.html
  ```

---

## 📄 License

This project is licensed under the MIT License.
