# 🤖 Hindi Translation Discord Bot

A Discord bot that **translates Hindi text and images** to English using AI. Built with `chrome-lens-py` OCR and OpenRouter.

---

## ✨ Features

- 📝 **Text Translation** — Paste any Hindi text and get an instant English translation
- 🖼️ **Image Translation** — Send an image containing Hindi text and the bot extracts and translates it automatically
- ⚡ **Fast & Reliable** — Powered by OpenRouter for translation and `chrome-lens-py` for OCR
- 🆓 **Completely Free** — Uses free tiers of all APIs

---

## 🚀 Commands

| Command | Description |
|---|---|
| `!he <hindi>` |  Translate Hindi text to English |
| `!he` + image |  Extract & translate Hindi from image |
| `!hu <hindi>` |  Translate Hindi text to Urdu |
| `!hu` + image |  Extract & translate Hindi from image |
| `!guide` |  Show full command guide |
| `!ping` |  Check bot status & latency |

---

## 🛠️ Tech Stack

| Service | Purpose |
|---|---|
| [discord.py](https://discordpy.readthedocs.io/) | Discord bot framework |
| `chrome-lens-py` (v3+) | Hindi OCR from images |
| [OpenRouter](https://openrouter.ai/) | Hindi → English translation |
| [python-dotenv](https://pypi.org/project/python-dotenv/) | Environment variable management |

---

## 📋 Prerequisites

- Python 3.11+
- Discord Bot Token
- OpenRouter API Key (free at [openrouter.ai](https://openrouter.ai))

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
```env
DISCORD_TOKEN=your_discord_bot_token_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### 4. Run the bot
```bash
python bot.py
```

## 📁 Project Structure

```
hindi-translation-bot/
├── README.md           # This file
├── bot.py              # Main bot code
├── build.sh            # Deployment/build script
├── package.txt         # System packages required during deployment
└── requirements.txt    # Python dependencies


```

---

## 🔑 Getting API Keys

### Discord Bot Token
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create new application → Bot → Reset Token
3. Enable **Message Content Intent**

### OpenRouter API Key (Free)
1. Go to [openrouter.ai](https://openrouter.ai)
2. Sign up → Keys → Create Key
- Uses free-tier models by default

---

## 🤝 Invite Bot to Your Server

Generate an invite link:
1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. OAuth2 → URL Generator
3. Select `bot` scope
4. Select permissions: `Read Messages`, `Send Messages`, `Add Reactions`, `Read Message History`
5. Copy and share the generated URL

---

## 📝 Example Usage

**Text Translation:**
```
User: !he नमस्ते आप कैसे हैं
Bot:
📝 Original Hindi: नमस्ते आप कैसे हैं
🇬🇧 English: Hello, how are you
```

**Image Translation:**
```
User: [attaches image with Hindi text] !he
Bot:
📝 Extracted Hindi: [extracted text]
🇬🇧 English: [english translation]
```

---

## ⚠️ Important Notes

- Bot only responds to `!` commands — it does NOT auto-translate every message


---

## Contributing

Contributions, feature requests, and bug reports are welcome.

Feel free to fork the repository and submit a pull request.

---

⭐ If this project helped you, consider giving it a star on GitHub!
