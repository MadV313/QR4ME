# QR-Build Bot for DayZ

A Discord bot that converts a QR code (text or image) into a grid of in-game DayZ objects (e.g. SmallProtectorCase), aligned over a Mirror Test Kit object. Used to generate scannable QR layouts inside DayZ servers.

## Features
- Slash command: `/qrbuild`
- Converts input text or image into QR layout
- Spawns grid of DayZ objects (default: protector case)
- Auto-aligns to Land_Mirror_TestKit
- PNG preview rendering
- Packages output as a downloadable .zip
- Admin-only channel delivery (configurable)

## Output
Each build generates:
- `objects.json` — spawn data
- `qr_preview.png` — visual grid layout
- `README.txt` — summary info
- `qr_code.zip` — packaged files

## Setup Instructions
1. Clone this repo
2. Create a `.env` or fill in `config.json` (channel IDs, bot token)
3. Run `pip install -r requirements.txt`
4. Launch with `python bot.py`

## License
MIT
