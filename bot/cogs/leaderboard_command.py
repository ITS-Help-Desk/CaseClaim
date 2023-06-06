from discord import app_commands
from discord.ext import commands
import discord
import csv
import datetime

from bot.views.leaderboard_view import LeaderboardView

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class LeaderboardCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /leaderboard command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Shows a list of all cases a user has worked on")
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        """Shows a leaderboard of all users by case numbers on the log file.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        await interaction.response.defer() # Wait in case process takes a long time

        embed = LeaderboardView.create_embed(interaction.created_at, self.bot.embed_color)

        await interaction.followup.send(embed=embed, view=LeaderboardView(self.bot))
