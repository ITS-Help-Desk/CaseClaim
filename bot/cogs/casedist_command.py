from discord import app_commands
from discord.ext import commands
import discord

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class CaseDist(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /casedist command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a list of all the previous techs who've worked on a case")
    async def casedist(self, interaction: discord.Interaction) -> None:
        """Shows a list of all techs who've previously worked on a case, and shows the
        ping comments if the command sender is a lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        await interaction.response.defer(ephemeral=True) # Wait in case process takes a long time

        # 7-6
        
        # 11 hour segments
        # 66 ten minute increments
        


