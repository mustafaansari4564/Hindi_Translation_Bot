# v4.0 - Full OpenRouter (OCR + Translation) - Hindi to English & Urdu

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiohttp
import re
import base64
import asyncio
import time
from flask import Flask
from threading import Thread

# ── Keep-alive server ────────────────────────────────────────────────────────

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive! 🤖"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask, daemon=True).start()

load_dotenv()

TOKEN              = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
PROXY_URL          = os.getenv("PROXY_URL")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ── Allowed Servers Whitelist ─────────────────────────────────────────────────
# Add server IDs to ALLOWED_SERVERS env variable (comma-separated).
# Leave empty to allow ALL servers.
ALLOWED_SERVERS_ENV = os.getenv("ALLOWED_SERVERS", "")
ALLOWED_SERVERS = [int(x.strip()) for x in ALLOWED_SERVERS_ENV.split(",") if x.strip().isdigit()]

# Best free vision models for Hindi OCR - Updated 2026
VISION_MODELS = [
    "openrouter/healer-alpha",
    "nvidia/llama-3.2-nemotron-nano-vl-8b-v1:free",
    "qwen/qwen2.5-vl-72b-instruct:free",
    "qwen/qwen2.5-vl-32b-instruct:free",
    "meta-llama/llama-4-maverick:free",
    "meta-llama/llama-4-scout:free",
    "moonshotai/kimi-vl-a3b-thinking:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]

# Translation model
TRANSLATION_MODEL = "openrouter/auto"

# ── Bot setup ────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None,
    proxy=PROXY_URL
)

# ── Helpers ──────────────────────────────────────────────────────────────────

def contains_hindi(text):
    """Check if the text contains Devanagari (Hindi) script characters."""
    return bool(re.search(r'[\u0900-\u097F]', text))

async def call_openrouter(messages, model, retries=2):
    """Generic OpenRouter API call."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://discord-translation-bot.com",
        "X-Title": "Hindi Translation Bot"
    }
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4000
    }

    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    OPENROUTER_URL,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    data = await resp.json()

                    if "error" in data:
                        error_msg = data["error"].get("message", "Unknown error")
                        print(f"OpenRouter error [{model}] (attempt {attempt+1}): {error_msg}")
                        if "rate" in error_msg.lower():
                            await asyncio.sleep(10)
                        continue

                    content = data["choices"][0]["message"]["content"]
                    if content and content.strip():
                        return content.strip()
                    return None

        except Exception as e:
            print(f"Exception [{model}] (attempt {attempt+1}): {e}")
            await asyncio.sleep(3)

    return None

async def extract_hindi_from_image(image_bytes, mime_type):
    """Try multiple free vision models for Hindi OCR."""
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_b64}"
                    }
                },
                {
                    "type": "text",
                    "text": """This image contains Hindi text written in Devanagari script.
Your task is to extract ALL Hindi text visible in the image.

- Extract every Hindi word and sentence you can see
- Include highlighted or bold text
- Preserve the original Hindi (Devanagari) text exactly
- Do NOT translate anything
- Return ONLY the Hindi text, nothing else
- If you cannot find any Hindi text, return: NONE"""
                }
            ]
        }
    ]

    for model in VISION_MODELS:
        print(f"Trying vision model: {model}")
        result = await call_openrouter(messages, model)
        if result:
            cleaned = result.strip()
            if cleaned and cleaned.upper() != "NONE" and contains_hindi(cleaned):
                print(f"✅ OCR succeeded with: {model}")
                return cleaned
            print(f"❌ Model {model} returned: {cleaned[:50] if cleaned else 'empty'}")
        else:
            print(f"❌ Model {model} failed completely")

    print("❌ All vision models failed")
    return ""

async def translate_text(hindi_text, language="both"):
    """Translate Hindi text using OpenRouter."""
    if language == "urdu":
        prompt = f"""Translate the COMPLETE Hindi text below to Urdu.
Do not skip or truncate any part. Return ONLY the Urdu translation.

Hindi text:
{hindi_text}"""

    elif language == "english":
        prompt = f"""Translate the COMPLETE Hindi text below to English.
Do not skip or truncate any part. Return ONLY the English translation.

Hindi text:
{hindi_text}"""

    else:
        prompt = f"""Translate the COMPLETE Hindi text below to both Urdu and English.
Do not skip or truncate any part.

Hindi text:
{hindi_text}

Respond in EXACTLY this format:
URDU: [complete urdu translation]
ENGLISH: [complete english translation]"""

    messages = [
        {
            "role": "system",
            "content": "You are a professional Hindi translator. Translate accurately and completely."
        },
        {"role": "user", "content": prompt}
    ]

    response = await call_openrouter(messages, TRANSLATION_MODEL)

    if not response:
        return {"urdu": "Translation failed", "english": "Translation failed"}

    if language == "urdu":
        return {"urdu": response, "english": ""}
    elif language == "english":
        return {"urdu": "", "english": response}
    else:
        return parse_both(response)

def parse_both(text):
    result = {"urdu": "", "english": ""}
    for line in text.strip().split('\n'):
        line = line.strip()
        if line.upper().startswith("URDU:"):
            result["urdu"] = line[5:].strip()
        elif line.upper().startswith("ENGLISH:"):
            result["english"] = line[8:].strip()

    if not result["urdu"] and not result["english"]:
        result["english"] = text[:500]
        result["urdu"] = "Could not parse"

    return result

def add_long_field(embed, name, value):
    if not value or not value.strip():
        return
    chunks = [value[i:i+1024] for i in range(0, len(value), 1024)]
    for i, chunk in enumerate(chunks):
        embed.add_field(
            name=name if i == 0 else f"{name} (cont.)",
            value=chunk,
            inline=False
        )

async def get_image_hindi(ctx):
    """Download image and extract Hindi text."""
    attachment = ctx.message.attachments[0]
    if not attachment.content_type or not attachment.content_type.startswith("image/"):
        await ctx.reply("⚠️ Please attach a valid image.")
        return None

    async with aiohttp.ClientSession() as session:
        async with session.get(attachment.url) as resp:
            image_bytes = await resp.read()

    await ctx.reply("🔍 Extracting Hindi text from image, please wait...")
    extracted = await extract_hindi_from_image(image_bytes, attachment.content_type)

    if not extracted:
        await ctx.reply("🖼️ Could not extract Hindi text from this image. Try a clearer/higher resolution image.")
        return None

    return extracted

# ── Events ───────────────────────────────────────────────────────────────────

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"OpenRouter: {'✅' if OPENROUTER_API_KEY else '❌ MISSING'}")
    print(f"Vision models: {len(VISION_MODELS)} models available")

    if ALLOWED_SERVERS:
        print(f"🔒 Restricted to servers: {ALLOWED_SERVERS}")
    else:
        print("🌐 No whitelist — all servers allowed")

    # Auto-leave unauthorized servers
    for guild in bot.guilds:
        if ALLOWED_SERVERS and guild.id not in ALLOWED_SERVERS:
            print(f"⛔ Leaving unauthorized server: {guild.name} ({guild.id})")
            await guild.leave()

@bot.event
async def on_guild_join(guild):
    """Auto-leave if server is not whitelisted."""
    if ALLOWED_SERVERS and guild.id not in ALLOWED_SERVERS:
        print(f"⛔ Leaving unauthorized server: {guild.name} ({guild.id})")
        try:
            await guild.system_channel.send(
                "⛔ This bot is restricted to specific servers only. Leaving now."
            )
        except:
            pass
        await guild.leave()

# 🔐 ────── Role & Channel Restrictions ─────────────────────────────────────────────────

FORUM_CHANNEL_ID = int(os.getenv("FORUM_CHANNEL_ID", "0"))
COUNCIL_ROLE_ID  = int(os.getenv("COUNCIL_ROLE_ID",  "0"))
LIBRARY_ROLE_ID  = int(os.getenv("LIBRARY_ROLE_ID",  "0"))

# ── Global Server Check ───────────────────────────────────────────────────────

@bot.check
async def global_server_check(ctx):
    """Global check — role + channel restrictions + no DMs"""
    # ❌ Ignore DMs completely
    if not ctx.guild:
        return False

    # If no role IDs configured, allow all members
    if COUNCIL_ROLE_ID == 0 and LIBRARY_ROLE_ID == 0:
        return True

    member = ctx.author

    # Role checks
    has_council = any(role.id == COUNCIL_ROLE_ID for role in member.roles)
    has_library  = any(role.id == LIBRARY_ROLE_ID  for role in member.roles)

    # ✅ Council role → full access
    if has_council:
        return True

    # ✅ Library Pass → ONLY in forum (including posts/threads)
    if has_library and (
        ctx.channel.id == FORUM_CHANNEL_ID or
        getattr(ctx.channel, "parent_id", None) == FORUM_CHANNEL_ID
    ):
        return True

    # ❌ No permission
    await ctx.reply("❌ You don't have permission to use this bot.")
    return False

# ── Commands ─────────────────────────────────────────────────────────────────

@bot.command(name="he", aliases=["english", "e", "en"])
async def translate_english(ctx, *, text=None):
    """Translate Hindi to English only  |  !he <hindi text>"""

    if ctx.message.attachments:
        hindi = await get_image_hindi(ctx)
        if not hindi:
            return

        async with ctx.typing():
            translations = await translate_text(hindi, "english")

        embed = discord.Embed(title="✒️ English Translation", color=0x00f3ff)
        add_long_field(embed, "📝 Original Hindi", hindi)
        add_long_field(embed, "✒️ English", translations["english"])
        embed.set_footer(text="Powered by OpenRouter 🦙")
        await ctx.reply(embed=embed)
        return

    if not text:
        await ctx.reply("**Usage:** `!he <hindi text>` or attach image + `!he`")
        return

    if not contains_hindi(text):
        await ctx.reply("⚠️ Please provide Hindi (Devanagari) text.")
        return

    async with ctx.typing():
        translations = await translate_text(text, "english")

    embed = discord.Embed(title="✒️ English Translation", color=0x00f3ff)
    add_long_field(embed, "📝 Original Hindi", text)
    add_long_field(embed, "✒️ English", translations["english"])
    embed.set_footer(text="Powered by OpenRouter 🦙")
    await ctx.reply(embed=embed)


@bot.command(name="hu", aliases=["urdu", "u", "ur"])
async def translate_urdu(ctx, *, text=None):
    """Translate Hindi to Urdu only  |  !hu <hindi text>"""

    if ctx.message.attachments:
        hindi = await get_image_hindi(ctx)
        if not hindi:
            return

        async with ctx.typing():
            translations = await translate_text(hindi, "urdu")

        embed = discord.Embed(title="🖋️ Urdu Translation", color=0x00f3ff)
        add_long_field(embed, "📝 Original Hindi", hindi)
        add_long_field(embed, "🖋️ Urdu", translations["urdu"])
        embed.set_footer(text="Powered by OpenRouter 🦙")
        await ctx.reply(embed=embed)
        return

    if not text:
        await ctx.reply("**Usage:** `!hu <hindi text>` or attach image + `!hu`")
        return

    if not contains_hindi(text):
        await ctx.reply("⚠️ Please provide Hindi (Devanagari) text.")
        return

    async with ctx.typing():
        translations = await translate_text(text, "urdu")

    embed = discord.Embed(title="🖋️ Urdu Translation", color=0x00f3ff)
    add_long_field(embed, "📝 Original Hindi", text)
    add_long_field(embed, "🖋️ Urdu", translations["urdu"])
    embed.set_footer(text="Powered by OpenRouter 🦙")
    await ctx.reply(embed=embed)


@bot.command(name="translate", aliases=["t", "tr", "both", "b"])
async def translate_both_command(ctx, *, text=None):
    """Translate Hindi to both English and Urdu"""

    if ctx.message.attachments:
        hindi = await get_image_hindi(ctx)
        if not hindi:
            return

        async with ctx.typing():
            translations = await translate_text(hindi, "both")

        embed = discord.Embed(title="🌐 Hindi Translation", color=0x00f3ff)
        add_long_field(embed, "📝 Original Hindi", hindi)
        add_long_field(embed, "✒️ English", translations["english"])
        add_long_field(embed, "🖋️ Urdu", translations["urdu"])
        embed.set_footer(text="Powered by OpenRouter 🦙")
        await ctx.reply(embed=embed)
        return

    if not text:
        await ctx.reply(
            "**📖 Quick Guide:**\n\n"
            "`!he <hindi>` — English only\n"
            "`!hu <hindi>` — Urdu only\n"
            "`!translate <hindi>` — Both\n"
            "Attach image + any command for image translation\n\n"
            "Type `!guide` for full guide."
        )
        return

    if not contains_hindi(text):
        await ctx.reply("⚠️ Please provide Hindi (Devanagari) text.")
        return

    async with ctx.typing():
        translations = await translate_text(text, "both")

    embed = discord.Embed(title="🌐 Hindi Translation", color=0x00f3ff)
    add_long_field(embed, "📝 Original Hindi", text)
    add_long_field(embed, "✒️ English", translations["english"])
    add_long_field(embed, "🖋️ Urdu", translations["urdu"])
    embed.set_footer(text="Powered by OpenRouter 🦙")
    await ctx.reply(embed=embed)


@bot.command(name="guide", aliases=["h", "commands"])
async def guide(ctx):
    """Show full guide"""
    embed = discord.Embed(
        title="📖 Hindi Translation Bot — Full Guide",
        description="Translates Hindi text and images to English and/or Urdu.",
        color=0x00f3ff
    )

    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━", value="**📝 TEXT TRANSLATION**", inline=False)
    embed.add_field(name="✒️ English only",       value="`!he <hindi text>`\n`!e <hindi text>`",       inline=False)
    embed.add_field(name="🖋️ Urdu only",           value="`!hu <hindi text>`\n`!u <hindi text>`",       inline=False)
    embed.add_field(name="🌐 Both English + Urdu", value="`!translate <hindi text>`\n`!t <hindi text>`", inline=False)

    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━", value="**🖼️ IMAGE TRANSLATION**", inline=False)
    embed.add_field(name="✒️ Image → English",     value="Attach image + `!he` or `!e`",      inline=False)
    embed.add_field(name="🖋️ Image → Urdu",        value="Attach image + `!hu` or `!u`",      inline=False)
    embed.add_field(name="🌐 Image → Both",        value="Attach image + `!translate` or `!t`", inline=False)

    embed.add_field(name="━━━━━━━━━━━━━━━━━━━━", value="**⚙️ OTHER**", inline=False)
    embed.add_field(name="🏓 Status", value="`!ping`",        inline=False)
    embed.add_field(name="📖 Guide",  value="`!guide` or `!h`", inline=False)

    embed.set_footer(text="Powered by OpenRouter 🦙")
    await ctx.reply(embed=embed)


@bot.command(name="ping")
async def ping(ctx):
    await ctx.reply(f"🏓 Pong! Latency: {round(bot.latency * 1000)}ms")


@bot.command(name="servers")
@commands.is_owner()
async def servers(ctx):
    """Show all servers the bot is in (owner only)"""
    guilds = bot.guilds
    if not guilds:
        await ctx.reply("Bot is not in any servers!")
        return

    embed = discord.Embed(
        title=f"🌐 Servers ({len(guilds)} total)",
        color=0x00f3ff
    )
    for guild in guilds:
        embed.add_field(
            name=guild.name,
            value=f"👥 Members: {guild.member_count}\n🆔 ID: {guild.id}",
            inline=False
        )
    embed.set_footer(text="Only visible to bot owner")
    await ctx.reply(embed=embed)

@servers.error
async def servers_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.reply("⛔ This command is only for the bot owner!")


@bot.command(name="stats")
@commands.is_owner()
async def stats(ctx):
    """Show bot statistics (owner only)"""
    total_members = sum(g.member_count for g in bot.guilds)
    embed = discord.Embed(title="📊 Bot Statistics", color=0x00f3ff)
    embed.add_field(name="🌐 Servers",       value=str(len(bot.guilds)),             inline=True)
    embed.add_field(name="👥 Total Members", value=str(total_members),               inline=True)
    embed.add_field(name="🏓 Latency",       value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.set_footer(text="Hindi Translation Bot")
    await ctx.reply(embed=embed)

@stats.error
async def stats_error(ctx, error):
    if isinstance(error, commands.NotOwner):
        await ctx.reply("⛔ This command is only for the bot owner!")


if __name__ == "__main__":
    print("⏳ Waiting 5 seconds before connecting...")
    time.sleep(5)
    bot.run(TOKEN, reconnect=True, log_handler=None)
