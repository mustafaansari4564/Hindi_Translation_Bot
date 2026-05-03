# 🇮🇳 Hindi Translation Bot

A Discord bot that translates **Hindi (Devanagari)** text and images to **English** and **Urdu**, powered by OpenRouter's free AI vision & language models.

---

## ⚡ Commands

| Command | Aliases | Description |
|---------|---------|-------------|
| `!he <hindi text>` | `!e`, `!en`, `!english` | Translate Hindi → **English** |
| `!hu <hindi text>` | `!u`, `!ur`, `!urdu` | Translate Hindi → **Urdu** |
| `!translate <hindi text>` | `!t`, `!tr`, `!both` | Translate Hindi → **Both** |
| `!guide` | `!h`, `!commands` | Show full command guide |
| `!ping` | — | Check bot latency |

### 🖼️ Image Translation
Attach a Hindi image and use any command above:
- Attach image + `!he` → English
- Attach image + `!hu` → Urdu
- Attach image + `!translate` → Both

---

## 🛠️ Setup

### 1. Clone & install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment variables
Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
```

Required values:
- `DISCORD_TOKEN` — Your Discord bot token
- `OPENROUTER_API_KEY` — Your OpenRouter API key (get one free at https://openrouter.ai)

### 3. Run the bot
```bash
python bot.py
```

---

## 🖥️ Render / Railway Deployment

Use `build.sh` as the build command — it installs Tesseract for Hindi OCR:
```bash
bash build.sh
```

---

## 🔒 Access Control (Optional)

Set these in your `.env` to restrict who can use the bot:

| Variable | Description |
|----------|-------------|
| `ALLOWED_SERVERS` | Comma-separated Discord server IDs (leave blank = all servers) |
| `COUNCIL_ROLE_ID` | Role ID with full bot access |
| `LIBRARY_ROLE_ID` | Role ID with forum-only access |
| `FORUM_CHANNEL_ID` | Forum channel ID for Library Pass holders |

---

## 🤖 Powered By
- [OpenRouter](https://openrouter.ai) — Free AI models for OCR & translation
- [discord.py](https://discordpy.readthedocs.io) — Discord bot framework
