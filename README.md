# Bonkie

A Discord bot for server-wide knockout battles. Players use slash commands to knock out other members (via Discord timeouts), earn XP, level up, prestige, and revive knocked-out allies.

**Version:** 0.3.0

## Features

- **Knockout battles** — Random weapons, hit/miss/crit outcomes, and configurable timeouts
- **Revive system** — Clear game-applied timeouts and earn XP; moderator timeouts are protected
- **Stats & leaderboards** — Global kills, deaths, revives, K/D ratio, XP, levels (max 15), prestige tiers, and worldwide rankings
- **Booster cooldowns** — Nitro boosters get a 30% shorter cooldown on knockout and revive
- **Error reporting** — Unexpected errors are logged locally and optionally sent to a Discord webhook
- **Developer tools** — Git pull, dependency sync, cog reload, and restart commands (role-restricted)

## Commands

| Command | Description |
|---|---|
| `/knockout <member>` | Knock out a member with a random weapon. Cannot target users in voice channels or already timed out. Protected members still award stats. |
| `/revive <member>` | Attempt to revive a knocked-out member. Only works for timeouts applied by the game. |
| `/stats [member]` | View global knockout stats, XP progress, and prestige. Works in DMs. Shows a prestige button at max level. |
| `/leaderboard [sort_by]` | View the global top 10 players across all servers. Sort by `kills`, `level`, `prestige`, or `xp`. |
| `/help` | Show command help and support links. |
| `/update` | Pull latest code from GitHub, sync dependencies, and restart. *(Developers only)* |
| `/update_commits` | View the 5 most recent commits. *(Developers only)* |
| `/update_test` | Fetch and show git status without restarting. *(Developers only)* |
| `/update_reload` | Reload all cogs without a full restart. *(Developers only)* |
| `/update_status` | Show current git branch and commit. |
| `/update_info` | Show recent commits and version info. |

The legacy prefix `n!` is configured but slash commands are the primary interface.

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for dependency management
- A Discord bot token with the following **privileged intents** enabled in the [Discord Developer Portal](https://discord.com/developers/applications):
  - Server Members Intent
  - Message Content Intent (if used elsewhere)

### Bot permissions

The bot needs these permissions in any server where knockout/revive are used:

- **Moderate Members** — Apply and clear timeouts
- **View Audit Log** — Detect moderator-applied timeouts during revive
- Send Messages, Embed Links, Attach Files, Use Slash Commands

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/unclemelo/Bonkie.git
cd Bonkie
uv sync --all-extras
```

Or run the included setup script (Windows):

```bash
python setup_uv.py
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
TOKEN=your_discord_bot_token
WEBHOOK=https://discord.com/api/webhooks/...   # optional — error notifications
```

`TOKEN` is required. `WEBHOOK` is optional; without it, errors are only written to `bot_errors.log`.

### 3. Run the bot

**Windows (recommended):**

```cmd
run.bat
```

**Manual start:**

```bash
uv run python bot.py
```

**Windows CMD:** If emoji still look garbled, use `run.bat` instead of starting Python directly. It sets UTF-8 before launch. [Windows Terminal](https://aka.ms/terminal) also works better than legacy CMD.

On startup, Bonkie loads all cogs from `cogs/`, syncs slash commands, and begins rotating status messages.

## Project structure

```
Bonkie/
├── bot.py                  # Entry point — bot client, cog loader, status loop
├── cogs/
│   ├── knockout.py         # /knockout and /revive game logic
│   ├── stats.py            # /stats and /leaderboard
│   ├── help.py             # /help command and support links
│   ├── error_handler.py    # Global slash-command and uncaught error handling
│   └── updater.py          # Developer update/reload commands
├── utils/
│   └── booster_cooldown.py # Cooldown manager with Nitro booster discount
├── data/
│   ├── weapons.json        # Weapon definitions (timeouts, GIFs, flavor text)
│   ├── royale_config.json  # Knockout and revive cooldown durations (seconds)
│   ├── royal_stats.json    # Player stats (created at runtime, gitignored)
│   └── deathlog.json       # Active knockout tracking (created at runtime, gitignored)
├── pyproject.toml
├── uv.lock
└── .python-version
```

## Configuration

### Cooldowns (`data/royale_config.json`)

| Key | Default | Description |
|---|---|---|
| `knockout_cooldown` | `1800` | Seconds between knockout uses (30 min) |
| `revive_cooldown` | `600` | Seconds between revive uses (10 min) |

### Weapons (`data/weapons.json`)

Each weapon entry defines a title, timeout duration (seconds or list), XP multiplier, GIF URL, and flavor text for hit, crit, and miss outcomes. The `garande_hug` weapon has a lower selection weight. The `nuke` weapon is excluded from random selection.

### Developer role

Update commands in `cogs/updater.py` check for `DEV_ROLE_ID`. Set this to your server's developer role ID, or `0` to allow any user.

## Game mechanics

**Knockout**

1. A random weapon is selected (weighted).
2. Outcome is rolled: 70% hit, 15% miss, 15% crit.
3. On hit, the target receives a Discord timeout for the weapon's duration (doubled on crit).
4. The attacker earns XP and a kill is recorded; the target gets a death.

**Revive**

1. Only targets in `deathlog.json` (knocked out by the game) can be revived.
2. If a moderator applied or extended the timeout, revive is blocked.
3. Successful revives award XP and clear the timeout.

**Progression**

- Max level is 15. At max level, players can prestige via the button on `/stats`.
- Prestige tiers: Bronze, Silver, Gold, Platinum, Diamond, Mythic (every 2 prestiges).
- Prestiging resets level and XP but keeps kill/death/revive stats.

## Development

Install dev dependencies (required for linting):

```bash
uv sync --all-extras
```

Run the linter and type checker (same as CI):

```bash
uv run ruff check .
uv run pyright .
```

CI runs both tools on every push and pull request to `main` via `.github/workflows/rufflint.yml`. Dev dependencies must be installed with `--all-extras` so `pyright` and `ruff` are available in the virtual environment.

## License

MIT — see [LICENSE](LICENSE).
