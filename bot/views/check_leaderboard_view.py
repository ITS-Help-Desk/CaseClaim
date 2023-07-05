import csv
import datetime
import io
import discord
import discord.ui as ui
import matplotlib.pyplot as plt
from bot.helpers import month_number_to_name

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.status import Status

if TYPE_CHECKING:
    from ..bot import Bot


class CheckLeaderboardView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a leaderboard view for the /leaderboard command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

	
    @ui.button(label="Refresh", style=discord.ButtonStyle.primary, custom_id="checkrefresh")
    async def button_refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False) # Acknowledge button press
        
        new_embed, file = CheckLeaderboardView.create_embed(interaction.created_at, self.bot.embed_color)
        new_embed.set_thumbnail(url=interaction.guild.icon.url)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed, attachments=[file])
    

    @staticmethod
    def create_embed(interaction_date: datetime.datetime, embed_color: discord.Color) -> list[discord.Embed, discord.File]:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            interaction_date (datetime.datetime): The time at which this request is made.
            embed_color (discord.Color): The color of the embed.

        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        m, s, mp, sp = CheckLeaderboardView.get_data(interaction_date)

        month_counts = m[0]
        month_keys = m[1]

        semester_counts = s[0]
        semester_keys = s[1]


        labels = []
        data_points1 = []
        data_points2 = []
        for key in month_keys:
            data_points1.append(month_counts[key] - mp[key])
            data_points2.append(mp[key])

            labels.append(str(key))

        data_stream = CheckLeaderboardView.convert_to_plot(labels, data_points1, data_points2)
        chart = discord.File(data_stream,filename="chart.png")
        
        embed = discord.Embed(title="ITS Case Check Leaderboard")
        embed.color = embed_color

        embed.set_image(
            url="attachment://chart.png"
        )

        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed, chart


    @staticmethod
    def convert_to_plot(labels, y1, y2):
        data_stream = io.BytesIO()
        # plot bars in stack manner
        plt.bar(labels, y1, color='r')
        plt.bar(labels, y2, bottom=y1, color='b')

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
        plt.close()

        data_stream.seek(0)
        return data_stream


    @staticmethod
    def get_data(interaction_date: datetime.datetime) -> tuple[tuple[dict[int, int], list[int]], tuple[dict[int, int], list[int]], dict[int, int], dict[int, int]]:
        """Collects a large amount of data to be used by various commands and events within this bot.
        This function collects:
            - Total amount of cases claimed by each user by month
            - Total amount of cases claimed by each user by semester
            - Ranking of cases claimed by each user by month
            - Ranking of cases claimed by each user by semester
            - Total amount of pinged cases by each user by month
            - Total amount of pinged cases by each user by semester
        Args:
            interaction_date (datetime.datetime): The time that this data was requested at.

        Returns:
            tuple[tuple[dict[int, int], list[int]], tuple[dict[int, int], list[int]], dict[int, int], dict[int, int]]:
            Returns the data in the format ((month counts, sorted month keys), (semester counts, sorted semester keys), month ping counts, semester ping counts)
        """
        # Count the amount of cases worked on by each user
        month_counts = {}
        semester_counts = {}
       
        month_ping_counts = {}
        semester_ping_counts = {}
    
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                date = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f")
    
                id = int(row[4])

                # Initialize information as zero
                if not id in month_ping_counts.keys():
                    month_ping_counts[id] = 0
                if not id in semester_ping_counts.keys():
                    semester_ping_counts[id] = 0

                # Organize data for month
                if date.month == interaction_date.month:
                    if not id in month_counts.keys():
                        month_counts[id] = 0
                    month_counts[id] += 1

                    # Add pinged
                    if row[5] == Status.PINGED or row[5] == Status.RESOLVED:
                        month_ping_counts[id] += 1

                # Organize data for semester
                if date.year == interaction_date.year:
                    if not id in semester_counts.keys():
                        semester_counts[id] = 0
                    semester_counts[id] += 1

                    # Add pinged
                    if row[5] == Status.PINGED or row[5] == Status.RESOLVED:
                        semester_ping_counts[id] += 1

                
        semester_counts_sorted_keys = sorted(semester_counts, key=semester_counts.get, reverse=True)
        month_counts_sorted_keys = sorted(month_counts, key=month_counts.get, reverse=True)

        return ((month_counts, month_counts_sorted_keys), (semester_counts, semester_counts_sorted_keys), month_ping_counts, semester_ping_counts)