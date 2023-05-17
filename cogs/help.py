from discord import app_commands
from discord.ext import commands
import discord

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


class HelpCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /help command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot


    @app_commands.command(description = "Instructions for how to use the /claim command.")
    async def help(self, interaction: discord.Interaction) -> None:
        """Sends a message back to the user explaining how to use the bot.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        await interaction.response.send_message("Claim a case using /claim followed by a case number.\n  - React with a ☑️ when you have completed the case.\n  - React with a ⚠️ to unclaim the case.\n", ephemeral = True, delete_after=300)