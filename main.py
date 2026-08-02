import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

# ===============
# CONFIGURAZIONE
# ===============

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN") or "TOKEN_NON_INSERITO"
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID") or 0)
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID") or 0)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ==========
# FILE JSON
# ==========

WARN_FILE = "Log_WARN/warns.json"
BAN_FILE = "Log_BAN/bans.json"

def load_json(path):
    """Carica un file JSON"""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}

def save_json(path, data):
    """Salva un JSON"""
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

warns = load_json(WARN_FILE)
bans = load_json(BAN_FILE)

# =============
# EVENTO READY
# =============

@bot.event
async def on_ready():
    print(f"[READY] {bot.user} è online")
    log = bot.get_channel(LOG_CHANNEL_ID)
    if log:
        await log.send(f"🟢 Bot avviato: {bot.user}")

# ================
# WELCOME / ADDIO
# ================

@bot.event
async def on_member_join(member):
    ch = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(f"👋 Benvenuto {member.mention}!")

@bot.event
async def on_member_remove(member):
    ch = member.guild.get_channel(WELCOME_CHANNEL_ID)
    if ch:
        await ch.send(f"👋 {member.name} ha lasciato il server.")

# =====
# WARN
# =====

@bot.command()
async def warn(ctx, member: discord.Member, *, motivo="Nessun motivo"):
    uid = str(member.id)

    # ⚠️ Nessuna validazione → voluto
    warns.setdefault(uid, []).append({
        "motivo": motivo,
        "mod": ctx.author.id,
        "time": datetime.utcnow().isoformat()
    })

    save_json(WARN_FILE, warns)

    await ctx.send(f"⚠️ {member.mention} warnato.")

@bot.command()
async def warnlist(ctx, member: discord.Member):
    uid = str(member.id)
    lista = warns.get(uid, [])

    if not lista:
        await ctx.send("Nessun warn registrato.")
        return

    # ⚠️ Formattazione grezza → voluto
    msg = "\n".join(f"- {w['motivo']} ({w['time']})" for w in lista)
    await ctx.send(msg)

# ====
# BAN 
# ====

@bot.command()
async def ban(ctx, member: discord.Member, *, motivo="Nessun motivo"):
    uid = str(member.id)
    bans[uid] = {
        "motivo": motivo,
        "mod": ctx.author.id,
        "time": datetime.utcnow().isoformat()
    }
    save_json(BAN_FILE, bans)
    await ctx.send(f"⛔ {member.mention} bannato.")

# =======
# TICKET
# =======

@bot.command()
async def ticket(ctx, *, motivo="Nessuna descrizione"):
    autore = ctx.author
    nome = f"ticket-{autore.id}"
    canale = await ctx.guild.create_text_channel(nome)
    await ctx.send(f"Ticket creato: {canale.mention}")
    await canale.send(f"👋 Ticket aperto.\nMotivo: `{motivo}`")

@bot.command()
async def ticketclose(ctx):
    await ctx.send("Ticket chiuso.")
    await ctx.channel.delete()

# ==========
# AVVIO BOT
# ==========

bot.run(TOKEN)
