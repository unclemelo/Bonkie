import discord
import traceback
import sys
from datetime import datetime
from discord import app_commands, Interaction
from discord.ext import commands
from colorama import Fore, Style, init
from typing import Type
from utils.console import configure_console_encoding

configure_console_encoding()
init(autoreset=True)


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_app_command_error
        sys.excepthook = self.handle_uncaught_exception

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%H:%M:%S")

    def log_terminal(self, tag: str, message: str, *, color=Fore.WHITE):
        print(
            f"{Fore.BLACK}[{self._timestamp()}]{Style.RESET_ALL} "
            f"{tag} {color}{message}{Style.RESET_ALL}"
        )

    def log_command_error(
        self,
        *,
        command: str,
        user: discord.abc.User,
        guild: str,
        error_type: str,
        error: Exception,
        expected: bool,
    ):
        if expected:
            self.log_terminal(
                Fore.YELLOW + "[WARN]",
                f"/{command} blocked for {user} ({user.id}) in {guild}: {error_type} — {error}",
            )
            return

        trace = "".join(traceback.format_exception(type(error), error, error.__traceback__))
        self.log_terminal(Fore.RED + Style.BRIGHT + "[ERROR]", f"/{command} failed in {guild}")
        print(
            f"{Fore.CYAN}User:{Style.RESET_ALL} {user} ({user.id})\n"
            f"{Fore.CYAN}Type:{Style.RESET_ALL} {error_type}\n"
            f"{Fore.CYAN}Message:{Style.RESET_ALL} {error}\n"
            f"{Fore.MAGENTA}Traceback:{Style.RESET_ALL}\n{trace}"
        )

    async def on_app_command_error(self, interaction: Interaction, error: Exception):
        if isinstance(error, app_commands.CommandInvokeError):
            error = error.original

        command = interaction.command.name if interaction.command else "unknown"
        guild = interaction.guild.name if interaction.guild else "DMs"
        expected = self.is_expected_error(error)

        self.log_command_error(
            command=command,
            user=interaction.user,
            guild=guild,
            error_type=type(error).__name__,
            error=error,
            expected=expected,
        )

        await self.safe_respond(interaction, self.get_user_message(error, expected=expected))

    def get_user_message(self, error: Exception, *, expected: bool) -> str:
        error_map: dict[Type[Exception], str] = {
            app_commands.CommandOnCooldown: "This command is on cooldown. Try again later.",
            app_commands.MissingPermissions: "You do not have permission to use this command.",
            app_commands.BotMissingPermissions: "I'm missing required permissions.",
            app_commands.NoPrivateMessage: "This command can't be used in DMs.",
            app_commands.CheckFailure: "You don't meet the requirements for this command.",
        }

        if isinstance(error, app_commands.MissingRole):
            return f"You must have the `{error.missing_role}` role."

        if isinstance(error, app_commands.MissingAnyRole):
            roles = ", ".join(f"`{r}`" for r in error.missing_roles)
            return f"You need one of these roles: {roles}"

        for exc, message in error_map.items():
            if isinstance(error, exc):
                return message

        if expected:
            return "That command could not be completed."

        return "Something went wrong while running that command."

    def is_expected_error(self, error: Exception) -> bool:
        return isinstance(
            error,
            (
                app_commands.CommandOnCooldown,
                app_commands.MissingPermissions,
                app_commands.BotMissingPermissions,
                app_commands.CheckFailure,
                app_commands.NoPrivateMessage,
                app_commands.MissingRole,
                app_commands.MissingAnyRole,
            ),
        )

    async def safe_respond(self, interaction: Interaction, message: str):
        try:
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
        except discord.HTTPException:
            pass

    def handle_uncaught_exception(self, exctype, value, tb):
        if exctype is KeyboardInterrupt:
            self.log_terminal(Fore.YELLOW + "[WARN]", "KeyboardInterrupt — shutting down cleanly.")
            return

        trace = "".join(traceback.format_exception(exctype, value, tb))
        self.log_terminal(Fore.MAGENTA + Style.BRIGHT + "[CRITICAL]", f"Uncaught {exctype.__name__}: {value}")
        print(f"{Fore.MAGENTA}Traceback:{Style.RESET_ALL}\n{trace}")


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))
