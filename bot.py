import discord
import os
import asyncio
from discord.ext import commands, tasks
from dotenv import load_dotenv
from colorama import Fore, Style, init
from datetime import datetime
from utils.console import configure_console_encoding

configure_console_encoding()
init(autoreset=True)

# ──────────────────────────────────────────────
# Load environment
load_dotenv()
TOKEN = os.getenv("TOKEN")

# ──────────────────────────────────────────────
# Bot setup
intents = discord.Intents.all()
intents.members = True
client = commands.AutoShardedBot(command_prefix="n!", shard_count=1, intents=intents)
client.remove_command("help")

# ──────────────────────────────────────────────
# Terminal Style Helpers
def terminal_banner():
    print(f"""{Fore.MAGENTA}{Style.BRIGHT}
╔════════════════════════════════════════════════╗
║               BONKIE SYSTEM v0.3               ║
╚════════════════════════════════════════════════╝
    """)

def log(msg: str, level: str = "info"):
    time = datetime.now().strftime("%H:%M:%S")
    levels = {
        "info": Fore.CYAN + "[INFO]",
        "success": Fore.GREEN + "[SUCCESS]",
        "warn": Fore.YELLOW + "[WARN]",
        "error": Fore.RED + "[ERROR]",
        "critical": Fore.MAGENTA + "[CRITICAL]",
    }
    tag = levels.get(level, Fore.WHITE + "[LOG]")
    print(f"{Fore.BLACK}[{time}]{Style.RESET_ALL} {tag} {Fore.WHITE}{msg}{Style.RESET_ALL}")

# ──────────────────────────────────────────────
# Status rotation
status_index = 0

def build_status_messages(guild_count: int, latency_ms: int) -> list[str]:
    ping = "999+ms" if latency_ms > 999 else f"{latency_ms}ms"
    server_label = f"{guild_count} server" if guild_count == 1 else f"{guild_count} servers"
    return [
        "/knockout | /revive",
        "/stats | /leaderboard",
        "/help for commands",
        server_label,
        f"ping: {ping}",
    ]

@tasks.loop(seconds=15)
async def update_status_loop():
    global status_index

    try:
        guild_count = len(client.guilds)
        latency = round(client.latency * 1000)
        statuses = build_status_messages(guild_count, latency)
        current = statuses[status_index % len(statuses)]
        status_index += 1
        await client.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(type=discord.ActivityType.watching, name=current)
        )
    except Exception as e:
        log(f"Status update failed: {e}", "error")

# ──────────────────────────────────────────────
# Events
@client.event
async def on_ready():
    terminal_banner()
    if client.user:
        log(f"System online as {client.user} ({client.user.id})", "success")
    log(f"Connected to {len(client.guilds)} guilds.", "info")

    try:
        synced = await client.tree.sync()
        log(f"Slash commands synced: {len(synced)}", "success")
    except Exception as e:
        log(f"Command sync failed: {e}", "error")

    if not update_status_loop.is_running():
        update_status_loop.start()

# ──────────────────────────────────────────────
# Cog loader
async def load_cogs():
    loaded = []
    failed = []

    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            name = filename[:-3]
            try:
                await client.load_extension(f"cogs.{name}")
                loaded.append(filename)
            except Exception as e:
                failed.append((filename, str(e)))

    if loaded:
        log("Loaded cogs:", "success")
        for file in loaded:
            print(Fore.GREEN + f"   → {file}")
    if failed:
        log("Failed to load cogs:", "error")
        for file, error in failed:
            print(Fore.RED + f"   → {file}: {error}")

# ──────────────────────────────────────────────
# Main entry
async def main():
    try:
        await load_cogs()
    except Exception as e:
        log(f"Critical error loading cogs: {e}", "critical")

    try:
        log("Starting Bonkie client...", "info")
        if not TOKEN:
            raise RuntimeError("TOKEN is not set in environment variables")
        await client.start(TOKEN)
    except KeyboardInterrupt:
        log("Manual shutdown requested (Ctrl+C)", "warn")
        await client.close()
    except Exception as e:
        log(f"Failed to start bot: {e}", "critical")

if __name__ == "__main__":
    asyncio.run(main())