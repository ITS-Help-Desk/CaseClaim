import calendar
import datetime

import discord
import discord.ui as ui

from bot.helpers.leaderboard_helpers import LeadstatsResults
from bot.helpers.other import month_number_to_name
from bot.models.checked_claim import CheckedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from bot.bot import Bot


class LeadstatsForm(ui.Modal, title='Past Leadstats Form'):
    def __init__(self, bot: "Bot"):
        """Creates a feedback form for showing previous leadstats leaderboards.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__()
        self.bot = bot

    date = ui.TextInput(label='Date (MM/YYYY)', style=discord.TextStyle.short)
    month_or_semester = ui.TextInput(label='Month/Semester (m for month, s for semester)', style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):
        """Shows previous leadstats leaderboards.

        Args:
            interaction (discord.Interaction): The submit modal interaction
        """

        d = self.validate_input(str(self.date))
        m_or_s = str(self.month_or_semester).lower() == 'm'

        results = LeadstatsResults(CheckedClaim.search(self.bot.connection), d)

        title = f"ITS Historic {'Month' if m_or_s else 'Semester'} Lead CC Statistics ({month_number_to_name(d.month)} {d.year})"
        chart = discord.File(results.convert_to_plot(self.bot, m_or_s, title), filename="chart.png")

        await interaction.response.send_message(content="👍", ephemeral=True, file=chart, delete_after=90)

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
