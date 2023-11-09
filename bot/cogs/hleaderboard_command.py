import datetime
import calendar

from discord import app_commands
from discord.ext import commands
import discord
import traceback
from typing import Optional

from bot.models.checked_claim import CheckedClaim
from bot.models.team_point import TeamPoint
from bot.helpers.leaderboard_helpers import *

from bot.views.leaderboard_view import LeaderboardView

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class HLeaderboardCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /leaderboard command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a list of all cases a user has worked on")
    @app_commands.describe(date="The date the leaderboard starts (MM/YY).")
    @app_commands.default_permissions(mute_members=True)
    async def hleaderboard(self, interaction: discord.Interaction, date: str) -> None:
        """Shows a leaderboard of all users by case numbers on the database.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
            date (str): A month/year formatted as MM/YY
        """
        date2 = self.validate_input(date)
        await interaction.response.defer(ephemeral=True)  # Wait in case process takes a long time

        try:
            result = LeaderboardResults(
                CheckedClaim.get_all_leaderboard(self.bot.connection, date2.year),
                TeamPoint.get_all(self.bot.connection), date2, None, True)

            embed = LeaderboardView.create_embed(self.bot, interaction, result)
            embed.title = f"Historic Leaderboard: {date}"
            await interaction.followup.send(embed=embed)
        except:
            await interaction.followup.send(content="Error! Please ensure you provided a correct date (MM/YY).")

    def validate_input(self, date: str) -> Optional[datetime.datetime]:
        try:
            month = int(date.split("/")[0])
            year = int(date.split("/")[1])

            if 0 < month <= 12 and 0 < year <= 99:
                # Create a datetime object for the last day of the month
                last_day = calendar.monthrange(2000 + year, month)[1]
                return datetime.datetime(2000 + year, month, last_day)
            return None
        except:
            return None

    @hleaderboard.error
    async def leaderboard_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/leaderboard** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
