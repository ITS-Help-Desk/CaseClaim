import csv
import datetime
import io
import discord
import discord.ui as ui
import matplotlib.pyplot as plt

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.status import Status

if TYPE_CHECKING:
    from ..bot import Bot


class LeadStatsView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a leaderboard view for the /leaderboard command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

	
    @ui.button(label="Month", style=discord.ButtonStyle.primary, custom_id="checkrefreshmonth")
    async def show_month(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server for the month.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False) # Acknowledge button press
        
        new_embed, file = await LeadStatsView.create_embed(interaction, self.bot.embed_color)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed, attachments=[file])
    

    @ui.button(label="Semester", style=discord.ButtonStyle.primary, custom_id="checkrefreshsemester")
    async def show_semester(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server for the semester.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False) # Acknowledge button press
        
        new_embed, file = await LeadStatsView.create_embed(interaction, self.bot.embed_color, month=False)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed, attachments=[file])
    

    @staticmethod
    async def create_embed(interaction: discord.Interaction, embed_color: discord.Color, month=True) -> list[discord.Embed, discord.File]:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            interaction_date (datetime.datetime): The time at which this request is made.
            embed_color (discord.Color): The color of the embed.

        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        m, s, mp, sp = LeadStatsView.get_data(interaction.created_at)

        month_counts = m[0]
        month_keys = m[1]
    
        semester_counts = s[0]
        semester_keys = s[1]

        if month:
            counts = month_counts
            pings = mp
            keys = month_keys
        else:
            counts = semester_counts
            pings = sp
            keys = semester_keys

        labels = []
        data_points1 = []
        data_points2 = []

        users: dict[int, discord.Member] = {}
        for key in keys:
            data_points1.append(counts[key] - pings[key])
            data_points2.append(pings[key])

            if key in users.keys():
                if type(users[key]) == int:
                    labels.append(str(key))
                else:
                    labels.append(users[key].display_name)
            else:
                try:
                    try:
                        user = await interaction.guild.get_member(key)
                    except:
                        user = None
                        
                    if user is None:
                        user = await interaction.guild.fetch_member(key)

                    if user is None:
                        users[key] = key
                        labels.append(str(key))
                    else:
                        users[key] = user
                        labels.append(users[key].display_name)
                except:
                    users[key] = key
                    labels.append(str(key))
    
        data_stream = LeadStatsView.convert_to_plot(f"ITS Lead CC Statistics ({'Month' if month else 'Semester'})", labels, data_points1, data_points2)
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
    def convert_to_plot(title: str, labels: list[str], y1: list[int], y2: list[int]) -> io.BytesIO:
        """Converts data into a plot that can be sent in a Discord message. It uses three
        parallel lists in order to generate the plot using matplotlib

        Args:
            title (str): The title of the graph
            labels (list[str]): The text labels for the bottom X axis of the graph
            y1 (list[int]): The data points for the checks
            y2 (list[int]): The data points for the pings

        Returns:
            io.BytesIO: The bytes that can be used to generate the graph
        """
        data_stream = io.BytesIO()
        fig, ax = plt.subplots()

        # Create plot
        ax.set_title(title)
        plt.xticks(rotation=45, ha="right")

        ax.bar(labels, y1, color = "b", zorder=3)
        ax.bar(labels, y2, bottom = y1, color = "r", zorder=3)
        #ax.grid(zorder=0)

        # Show labels on top of bars
        for i, (x, y1_val, y2_val) in enumerate(zip(labels, y1, y2)):
            total = y1_val + y2_val
            percentage = int(round(y2_val / total, 2) * 100)
            label = f"{percentage}%"
            ax.annotate(label, (x, total), ha='center', va='bottom', fontsize=8)


        # Create legend
        colors = {'Pings':'red', 'Checks':'blue'}
        ls = list(colors.keys())
        handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in ls]
        ax.legend(handles, ls)


        
        # Save and send
        fig.savefig(data_stream, format='png', bbox_inches="tight", dpi = 80)
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