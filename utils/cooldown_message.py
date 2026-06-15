import discord


def format_cooldown(seconds: float) -> str:
    total = max(1, int(seconds + 0.999))
    hours, rem = divmod(total, 3600)
    minutes, secs = divmod(rem, 60)

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def cooldown_embed(command_name: str, remaining: float) -> discord.Embed:
    return discord.Embed(
        title="⏳ On Cooldown",
        description=f"`/{command_name}` will be ready again in **{format_cooldown(remaining)}**.",
        color=discord.Color.orange(),
    )
