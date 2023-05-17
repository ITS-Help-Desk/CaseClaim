from discord import app_commands
from discord.ext import commands
import discord

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


class MickieCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /mickie command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="you're so fine")
    async def mickie(self, interaction: discord.Interaction) -> None:
        """Sends a message back to the user with a funny message (essentially
        acts as a ping command).

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        await interaction.response.send_message(f"Oh {interaction.user.mention} you're so fine, you blow my mind.")
        