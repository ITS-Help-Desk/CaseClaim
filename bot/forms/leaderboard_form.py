import calendar
import datetime

import discord
import discord.ui as ui

from bot.helpers.leaderboard_helpers import LeaderboardResults
from bot.helpers.other import month_number_to_name
from bot.models.checked_claim import CheckedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING, Optional

from bot.models.team_point import TeamPoint
#from bot.views.leaderboard_view import LeaderboardView

if TYPE_CHECKING:
    from bot.bot import Bot


class LeaderboardForm(ui.Modal, title='Past Leaderboard Form'):
    def __init__(self, bot: "Bot"):
        """Creates a feedback form for showing previous leaderboard leaderboards.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__()
        self.bot = bot

    date = ui.TextInput(label='Date (MM/YYYY)', style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        """Shows previous leaderboard leaderboards.

        Args:
            interaction (discord.Interaction): The submit modal interaction
        """

        d = self.validate_input(str(self.date))

        if d is None:
            await interaction.response.send_message(content="Please provide a valid date in MM/YYYY format.", ephemeral=True, delete_after=30)
            return

        result = LeaderboardResults(
            CheckedClaim.get_all_leaderboard(self.bot.connection, d.year),
            TeamPoint.get_all(self.bot.connection), d, None, True)

        embed = result.create_embed(self.bot, interaction)

        embed.title = f"Leaderboard ({month_number_to_name(d.month)} {d.year})"

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=90)

    def validate_input(self, date: str) -> Optional[datetime.datetime]:
        """Converts a MM/YYYY into a datetime on the last day of the month.

        Args:
            date (str): The date str formatted as MM/YYYY

        Returns:
            Optional[datetime.datetime] - The datetime on the last day of the month (if the input is valid)
        """
        try:
            month = int(date.split("/")[0])
            year = int(date.split("/")[1])

            if 0 < month <= 12:
                # Create a datetime object for the last day of the month
                last_day = calendar.monthrange(year, month)[1]
                return datetime.datetime(year, month, last_day)
            return None
        except:
            return None
