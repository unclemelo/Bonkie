import discord
import time
from typing import Literal

BUCKET_TYPES = {
    "user": lambda interaction: interaction.user.id,
    "guild": lambda interaction: interaction.guild.id if interaction.guild else interaction.user.id,
}

BOOSTER_COOLDOWN_MULTIPLIER = 0.5


def is_booster_in_guild(interaction: discord.Interaction) -> bool:
    """Return True if the user is boosting the server where the command was used."""
    if interaction.guild is None:
        return False

    member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(interaction.user.id)
    if member is None:
        return False

    return member.premium_since is not None


class BoosterCooldownManager:
    def __init__(self, rate: int, per: float, bucket_type: Literal["user", "guild"] = "user"):
        self.rate = rate
        self.per = per
        self.bucket_type = bucket_type
        self.cooldowns = {}  # key -> [timestamps]

    def _get_key(self, interaction: discord.Interaction):
        return BUCKET_TYPES[self.bucket_type](interaction)

    def _cooldown_period(self, interaction: discord.Interaction) -> float:
        if is_booster_in_guild(interaction):
            return self.per * BOOSTER_COOLDOWN_MULTIPLIER
        return self.per

    def get_period(self, interaction: discord.Interaction) -> float:
        return self._cooldown_period(interaction)

    async def get_remaining(self, interaction: discord.Interaction) -> float:
        key = self._get_key(interaction)
        now = time.time()
        cooldown_period = self._cooldown_period(interaction)

        timestamps = self.cooldowns.get(key, [])
        valid = [t for t in timestamps if now - t < cooldown_period]
        self.cooldowns[key] = valid

        if len(valid) >= self.rate:
            return cooldown_period - (now - valid[0])
        return 0.0

    async def trigger(self, interaction: discord.Interaction):
        key = self._get_key(interaction)
        now = time.time()
        self.cooldowns.setdefault(key, []).append(now)


def format_cooldown_footer(interaction: discord.Interaction, manager: BoosterCooldownManager) -> str:
    seconds = manager.get_period(interaction)
    minutes = max(1, round(seconds / 60))
    footer = f"🕐 Cooldown: {minutes} min"
    if is_booster_in_guild(interaction):
        footer += " · Server booster"
    return footer
