import discord
import os
from discord.ext import commands
from discord import app_commands
from utils.files import read_json, write_json

DATA_FILE = "data/royal_stats.json"

def load_data():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        write_json(DATA_FILE, {})
    return read_json(DATA_FILE)

def save_data(data):
    write_json(DATA_FILE, data)


PRESTIGE_TIERS = [
    ("Bronze", "🥉", discord.Color.dark_orange()),
    ("Silver", "🥈", discord.Color.light_grey()),
    ("Gold", "🥇", discord.Color.gold()),
    ("Platinum", "💎", discord.Color.teal()),
    ("Diamond", "🔷", discord.Color.blurple()),
    ("Mythic", "🔥", discord.Color.red())
]


class PrestigeButton(discord.ui.View):
    def __init__(self, user_id: int, cog, timeout=60):
        super().__init__(timeout=timeout)
        self.user_id = user_id
        self.cog = cog

    @discord.ui.button(label="Prestige Now ⭐", style=discord.ButtonStyle.primary, emoji="✨")
    async def prestige_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This isn’t your prestige menu!", ephemeral=True)
            return

        self.cog.reload_data()
        user = self.cog.get_user(self.user_id)
        if user["level"] < self.cog.max_level:
            await interaction.response.send_message("You haven’t reached max level yet!", ephemeral=True)
            return

        user["prestige"] += 1
        user["level"] = 1
        user["xp"] = 0
        save_data(self.cog.data)

        stars = "★" * user["prestige"]
        title, emoji, _ = self.cog.get_prestige_tier(user["prestige"])
        embed = discord.Embed(
            title=f"{emoji} Prestige Achieved!",
            description=f"{interaction.user.mention} has ascended to **{title} Prestige {user['prestige']}!**\n\n"
                        f"{stars}\n\nYour level and XP have been reset.",
            color=discord.Color.gold()
        )
        await interaction.response.edit_message(embed=embed, view=None)


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.data = load_data()
        self.max_level = 15
        self.global_xp_multiplier = 1.5

    def reload_data(self):
        self.data = load_data()

    @staticmethod
    def format_user_name(user: discord.abc.User) -> str:
        if isinstance(user, discord.Member):
            return user.display_name
        return user.global_name or user.name

    async def resolve_user_name(self, user_id: int) -> str:
        cached = self.bot.get_user(user_id)
        if cached is not None:
            return self.format_user_name(cached)

        try:
            fetched = await self.bot.fetch_user(user_id)
            return self.format_user_name(fetched)
        except (discord.NotFound, discord.HTTPException):
            return f"User {user_id}"

    def get_user(self, user_id: int):
        uid = str(user_id)
        if uid not in self.data:
            self.data[uid] = {
                "kills": 0,
                "deaths": 0,
                "revives": 0,
                "xp": 0,
                "level": 1,
                "prestige": 0
            }
        return self.data[uid]

    def add_xp(self, user_id: int, amount: int):
        user = self.get_user(user_id)
        amount = int(amount * self.global_xp_multiplier)
        user["xp"] += amount
        msg = None

        while user["xp"] >= self.xp_needed(user["level"]):
            user["xp"] -= self.xp_needed(user["level"])
            user["level"] += 1
            if user["level"] >= self.max_level:
                user["level"] = self.max_level
                msg = f"🌟 You’ve reached **Level {self.max_level}!** Ready to Prestige!"
                break
            else:
                msg = f"⬆️ Leveled up to **Level {user['level']}!**"

        save_data(self.data)
        return msg

    def xp_needed(self, level: int):
        return 60 + (level * 12)

    def get_prestige_tier(self, prestige: int):
        if prestige == 0:
            return ("Unranked", "—", discord.Color.light_grey())
        index = min(prestige // 2, len(PRESTIGE_TIERS) - 1)
        return PRESTIGE_TIERS[index]

    def xp_bar(self, current, needed, length=12):
        filled = int((current / needed) * length)
        return "█" * filled + "░" * (length - filled)

    @app_commands.command(name="stats", description="View your global knockout stats, XP, and prestige progress.")
    async def stats(
        self,
        interaction: discord.Interaction,
        member: discord.Member | discord.User | None = None,
    ):
        self.reload_data()
        target: discord.abc.User = member or interaction.user
        user = self.get_user(target.id)

        kills, deaths, revives = user["kills"], user["deaths"], user["revives"]
        xp, level, prestige = user["xp"], user["level"], user["prestige"]
        kd_ratio = round(kills / deaths, 2) if deaths > 0 else kills
        prestige_stars = "★" * prestige

        title, emoji, color = self.get_prestige_tier(prestige)
        progress_bar = self.xp_bar(xp, self.xp_needed(level))
        display_name = self.format_user_name(target)

        embed = discord.Embed(
            title=f"{emoji} {display_name}'s Global Stats",
            description=f"**Prestige:** {title} {prestige_stars or '—'}",
            color=color
        )
        embed.add_field(name="Kills", value=f"🔪 {kills}", inline=True)
        embed.add_field(name="Deaths", value=f"💀 {deaths}", inline=True)
        embed.add_field(name="Revives", value=f"❤️ {revives}", inline=True)
        embed.add_field(name="K/D Ratio", value=f"⚔️ {kd_ratio}", inline=True)
        embed.add_field(name="Level", value=f"📈 {level}/{self.max_level}", inline=True)
        embed.add_field(name="XP", value=f"✨ {xp}/{self.xp_needed(level)}\n`{progress_bar}`", inline=False)

        view = None
        if target.id == interaction.user.id and level >= self.max_level:
            view = PrestigeButton(target.id, self)

        if view:
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="leaderboard", description="View the global top players across all servers.")
    @app_commands.describe(sort_by="What stat to rank players by")
    @app_commands.choices(sort_by=[
        app_commands.Choice(name="Kills", value="kills"),
        app_commands.Choice(name="Level", value="level"),
        app_commands.Choice(name="Prestige", value="prestige"),
        app_commands.Choice(name="XP", value="xp"),
    ])
    async def leaderboard(self, interaction: discord.Interaction, sort_by: str = "kills"):
        await interaction.response.defer()

        self.reload_data()
        sorted_users = sorted(self.data.items(), key=lambda x: x[1].get(sort_by, 0), reverse=True)
        top = sorted_users[:10]

        if not top:
            return await interaction.followup.send("No stats recorded yet!", ephemeral=True)

        desc = []
        for i, (uid, player_stats) in enumerate(top, 1):
            name = await self.resolve_user_name(int(uid))
            title, emoji, _ = self.get_prestige_tier(player_stats.get("prestige", 0))
            desc.append(
                f"**#{i}** — {name} {emoji}\n"
                f"> 🗡️ {player_stats.get('kills', 0)} kills | 📈 Lvl {player_stats.get('level', 1)} | ⭐ {player_stats.get('prestige', 0)}"
            )

        embed = discord.Embed(
            title=f"🌍 Global Leaderboard — Sorted by {sort_by.title()}",
            description="\n\n".join(desc),
            color=discord.Color.gold()
        )
        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
