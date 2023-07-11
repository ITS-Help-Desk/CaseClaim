from discord import app_commands
from discord.ext import commands
import discord
import time
import csv
import datetime
import io
import matplotlib.pyplot as plt

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

    @app_commands.command(description="Shows a list of all the previous techs who've worked on a case")
    async def casedist(self, interaction: discord.Interaction, previous_days: int) -> None:
        """Shows a list of all techs who've previously worked on a case, and shows the
        ping comments if the command sender is a lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        start = datetime.datetime.now() - datetime.timedelta(days = previous_days)
        start = start.replace(hour=7, minute=0, second=0)

        days = [] # 22 segments
        for i in range(22):
            days.append(0)

        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                t = row[1]
                date_time = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f")

                if date_time > start:
                    start_time = date_time.replace(hour=7, minute=0, second=0)
                    fixed_date = int(time.mktime(date_time.timetuple())) - int(time.mktime(start_time.timetuple()))

                    index = (fixed_date // 60) // 30

                    days[min(index, len(days) - 1)] += 1
        
        data_stream = io.BytesIO()
        fig, ax = plt.subplots()

        labels = self.create_labels()
        
        # Create plot
        ax.set_title(f"ITS Case Histogram (Starting {start.strftime('%b %d, %Y')})")
        plt.xticks(rotation=90, ha="right")

        ax.bar(labels, days, color = "b", zorder=3)

        # Save and send
        fig.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()
        data_stream.seek(0)

        chart = discord.File(data_stream,filename="chart.png")

        embed = discord.Embed(title="ITS Case Histogram")

        embed.set_image(
            url="attachment://chart.png"
        )

        await interaction.response.send_message(embed=embed, file=chart)
        
    def create_labels(self) -> list[str]:
        labels = []

        hour = 7
        minute = 0
        for i in range(22):
            next_minute = minute + 30
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


