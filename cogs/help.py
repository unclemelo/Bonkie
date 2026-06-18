import discord
from discord import app_commands
from discord.ext import commands

GITHUB_REPO = "https://github.com/unclemelo/Bonkie"
SUPPORT_SERVER = "https://discord.gg/Jd5kSsvb56"


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Learn how to use Bonkie and see available commands.")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Bonkie Help",
            description=(
                "Bonkie is a knockout battle bot. Use slash commands to attack other members, "
                "earn XP, level up, and climb the leaderboard."
            ),
            color=discord.Color.blurple(),
        )

        embed.add_field(
            name="Game Commands",
            value=(
                "`/knockout <member>` — Attack someone with a random weapon. "
                "Hits can time them out and earn you XP. Protected members (like mods) "
                "still count toward your stats even if they can't be timed out.\n"
                "`/revive <member>` — Clear a game knockout timeout and earn XP."
            ),
            inline=False,
        )

        embed.add_field(
            name="Stats Commands",
            value=(
                "`/stats [member]` — View your global kills, deaths, revives, K/D, level, XP, and prestige.\n"
                "`/leaderboard [sort_by]` — See the top 10 players worldwide by kills, level, prestige, or XP."
            ),
            inline=False,
        )

        embed.add_field(
            name="Tips",
            value=(
                "• You can't knock out someone already timed out or in a voice channel.\n"
                "• Reach level 15 to unlock prestige from `/stats`.\n"
                "• Knockout and revive commands have cooldowns between uses.\n"
                "• Server boosters in the current server get half the normal cooldown on knockout and revive."
            ),
            inline=False,
        )

        embed.add_field(
            name="Need More Help?",
            value=(
                f"[GitHub Repository]({GITHUB_REPO})\n"
                f"[Support Server]({SUPPORT_SERVER})"
            ),
            inline=False,
        )

        embed.set_footer(text="Bonkie v0.3")
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
