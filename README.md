# 🧱 QR-Build Bot for DayZ (QR4ME)

A Discord bot that converts a QR code (text or image) into a grid of in-game DayZ objects (e.g. SmallProtectiveCase), auto-aligned to a Mirror Test Kit location. Used to generate scannable QR layouts for creative builds inside DayZ servers.

---

## ✨ Features

- `/qrbuild` — Convert **text or URL** into a DayZ object QR layout
- `/qrimage` — Upload and decode a **QR code image (PNG/JPG)**
- Uses in-game **DayZ objects** like crates, pots, bags, wires
- Automatically aligns grid to **Mirror Test Kit** location
- PNG **visual preview** rendered from thumbnail images
- ZIP **download package** including objects and preview
- **Admin-only command access**, with `/giveperms` to allow trusted users
- **Dynamic channel control** using `/setchannel`
- `/pushgallery` — Add most recent build to a web gallery
- `/preview` — Re-post the last preview and ZIP to Discord
- `/cleanup` — Remove old builds
- `/setorigin` — Set your build's X, Y, Z base coordinates

---

## 🗂️ Output Per Build

Each QR layout includes:

- `data/objects.json` — Object placement for import
- `previews/qr_preview.png` — Grid visualization
- `outputs/qr_code.zip` — Zipped JSON + preview + README
- `README.txt` — Summary inside the ZIP

---

## 🔧 Setup Instructions

1. **Clone the repo**:
   ```bash
   git clone https://github.com/YOURNAME/qr4me-bot.git
   cd qr4me-bot
   ```

2. **Set up your bot token and config**:

   - Option A: `.env` file (for Railway or hosting):
     ```
     DISCORD_BOT_TOKEN=your-token
     ADMIN_CHANNEL_ID=1234567890
     ADMIN_ROLE_IDS=111,222
     ```

   - Option B: Manually update `config.json`:
     ```json
     {
       "discord_token": "YOUR_DISCORD_BOT_TOKEN",
       "admin_channel_id": "YOUR_ADMIN_CHANNEL_ID",
       "admin_roles": ["ROLE_ID_1", "ROLE_ID_2"],
       "permitted_users": [],
       "origin_position": { "x": 5000.0, "y": 0.0, "z": 5000.0 }
     }
     ```

3. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the bot**:
   ```bash
   python bot.py
   ```

---

## ✅ Server Setup: Channels and Permissions

After inviting the bot to your server:

1. **Set your bot output channels**:
   - Use `/setchannel` and choose one of:
     - `Admin Channel` — where builds post
     - `Gallery Channel` — where previews/postings go
     - `Log Channel` — optional future logging
   - Example:
     ```
     /setchannel type: Admin Channel target: #qr-admin
     ```

2. **Allow non-admin users to use commands**:
   - Use `/giveperms` to grant access to trusted users
   - Example:
     ```
     /giveperms user: @PlayerName
     ```

3. **Revoke user access** if needed:
   - Use `/revokeperms user: @PlayerName`

---

## 🌐 Web Gallery

When you run `/pushgallery`, the most recent build is added to:
- `/public/gallery/` — images and ZIPs
- `data/gallery.json` — index metadata

Static web page:
```
public/gallery.html
```

You can host this folder with GitHub Pages or Netlify.

---

## 🔐 Required Discord Bot Permissions

For best results, your bot invite URL should include:

- `Send Messages`
- `Attach Files`
- `Use Slash Commands`
- `View Channels`
- *(Optional)* `Embed Links` and `Read Message History`

---

## 🧪 Testing Locally

To test without using `/giveperms`:
- Add your own Discord user ID to `"permitted_users"` in `config.json`
- Or use a role ID you hold in `"admin_roles"`

---

## 📄 License

This project is licensed under the **MIT License**.
