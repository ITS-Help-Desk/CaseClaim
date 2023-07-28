from discord import app_commands
from discord.ext import commands
import discord
import time
import datetime
import io
import matplotlib.pyplot as plt
from matplotlib import ticker

from bot.models.checked_claim import CheckedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class CaseDistCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /casedist command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a graph of the timing of case claims")
    @app_commands.default_permissions(mute_members=True)
    async def casedist(self, interaction: discord.Interaction, previous_days: int) -> None:
        """Sends a matplotlib graph of the average case claim time.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        start = datetime.datetime.now() - datetime.timedelta(days=previous_days)
        start = start.replace(hour=7, minute=0, second=0)

        days = []  # 44 segments
        for i in range(44):
            days.append(0)

        claims = CheckedClaim.search(self.bot.connection)
        for claim in claims:
            if claim.claim_time > start:
                start_time = claim.claim_time.replace(hour=7, minute=0, second=0)
                fixed_date = int(time.mktime(claim.claim_time.timetuple())) - int(time.mktime(start_time.timetuple()))

                index = (fixed_date // 60) // 15

                days[min(index, len(days) - 1)] += 1

        data_stream = io.BytesIO()
        fig, ax = plt.subplots()

        labels = self.create_labels()

        # Create plot
        ax.set_title(f"ITS Case Histogram (Starting {start.strftime('%b %d, %Y')})")
        plt.xticks(rotation=90, ha="right")

        ax.bar(labels, days, color="b", zorder=3)

        plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(nbins=13))

        # Save and send
        fig.savefig(data_stream, format='png', bbox_inches="tight", dpi=80)
        plt.close()
        data_stream.seek(0)

        chart = discord.File(data_stream, filename="chart.png")

        embed = discord.Embed(title="ITS Case Histogram")

        embed.set_image(
            url="attachment://chart.png"
        )

        embed.colour = self.bot.embed_color

        await interaction.response.send_message(embed=embed, file=chart, ephemeral=True)

    def create_labels(self) -> list[str]:
        """Creates a list of labels for the graph broken up by 15 minute increments
        7:00, 7:15, 7:30, 7:45, 8:00...

        Returns:
            list[str]: A list with all labels
        """
        labels = []

        hour = 7
        minute = 0
        for i in range(44):
            next_minute = minute + 15
            next_hour = hour
            if next_minute >= 60:
                next_minute = 0
                next_hour += 1
                if next_hour > 12:
                    next_hour %= 12

            fminute = f"0{minute}" if minute < 10 else str(minute)
            labels.append(f"{hour}:{fminute}")

            minute = next_minute
            hour = next_hour

        return labels