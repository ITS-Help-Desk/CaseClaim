import csv
import datetime
import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class LeaderboardView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a leaderboard view for the /leaderboard command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

	
    @ui.button(label="Refresh", style=discord.ButtonStyle.primary, custom_id="refresh")
    async def button_refresh(self, interaction: discord.Interaction, button):
        await interaction.response.defer(thinking=False) # Acknowledge button press
        
        new_embed = LeaderboardView.create_embed(interaction.created_at, self.bot.embed_color)

        await interaction.message.edit(embed=new_embed)
    
    
    @ui.button(label="My Rank", style=discord.ButtonStyle.secondary, custom_id="myrank")
    async def button_myrank(self, interaction: discord.Interaction, button):
        pass
        '''self.case = self.bot.get_case(interaction.message.id)

        data = LeaderboardView.get_data(interaction.created_at)

        mc = data[0][0]
        sc = data[1][0]
        
        mc_sorted_keys = data[0][1]
        sc_sorted_keys = data[1][1]

        await interaction.response.send_message(embed=embed, ephemeral=True)'''
    

    @staticmethod
    def create_embed(interaction_date: datetime.datetime, embed_color: discord.Color) -> discord.Embed:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            interaction_date (datetime.datetime): The time at which this request is made.
            embed_color (discord.Color): The color of the embed.

        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        month_ranking, semester_ranking = LeaderboardView.create_rankings(interaction_date)

        # Create embed
        embed = discord.Embed(title="ITS Case Claim Leaderboard")
        embed.color = embed_color

        embed.add_field(name=f"{LeaderboardView.month_number_to_name(interaction_date.month)} Ranks", value=month_ranking, inline=True)
        embed.add_field(name="Semester Ranks", value=semester_ranking, inline=True)
        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed


    @staticmethod
    def create_rankings(interaction_date: datetime.datetime) -> tuple[str]:
        """Creates the ranking strings for monthly and semester ranks.

        Args:
            interaction_date (datetime.datetime): The time at which this request is made.

        Returns:
            tuple[str]: Returns a tuple containing ("1. Andrew\n2. James", "1. James\n2. Andrew") where
            the first element is for monthly and second element is for semester.
        """
        data = LeaderboardView.get_data(interaction_date)

        mc = data[0][0]
        sc = data[1][0]
        
        mc_sorted_keys = data[0][1]
        sc_sorted_keys = data[1][1]
        
        month_ranks = []
        semester_ranks = []

        # Create month written ranking
        for i in range(min(4, len(mc_sorted_keys))):
            month_id = mc_sorted_keys[i]
            month_ranks.append(f"{i + 1}. <@!{month_id}> ({mc[month_id]})")
        
        month_ranking = "\n".join(user for user in month_ranks)

        # Create year written ranking
        for i in range(min(4, len(sc_sorted_keys))):
            semester_id = sc_sorted_keys[i]
            semester_ranks.append(f"{i + 1}. <@!{semester_id}> ({sc[semester_id]})")

        semester_ranking = "\n".join(user for user in semester_ranks)

        return month_ranking, semester_ranking


    @staticmethod
    def get_data(interaction_date: datetime.datetime) -> tuple[tuple[dict[int, int], list[int]]]:
        """Gets the ranking data for all users at a particular time

        Args:
            interaction_date (datetime.datetime): The time at which this request is made

        Returns:
            tuple[tuple[dict[int, int], list[int]]]: A tuple containing ((month counts, sorted keys), (semester counts, semester keys))
        """
        # Count the amount of cases worked on by each user
        semester_counts = {}
        month_counts = {}
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                date = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S.%f")
    
                id = int(row[3])

                # Organize data for month
                if date.month == interaction_date.month:
                    if not id in month_counts.keys():
                        month_counts[id] = 0
                    month_counts[id] += 1

                # Organize data for semester
                if date.year == interaction_date.year:
                    if not id in semester_counts.keys():
                        semester_counts[id] = 0
                    semester_counts[id] += 1
                
        semester_counts_sorted_keys = sorted(semester_counts, key=semester_counts.get, reverse=True)
        month_counts_sorted_keys = sorted(month_counts, key=month_counts.get, reverse=True)

        return ((month_counts, month_counts_sorted_keys), (semester_counts, semester_counts_sorted_keys))
    

    @staticmethod
    def get_individual_ranking():
        pass


    @staticmethod
    def month_number_to_name(month_number: int) -> str:
        """Converts a month number to the actual name.
        (e.g. 1 -> January)

        Args:
            month_number (int): The number of the month (from 1 to 12)

        Raises:
            ValueError: If the number provided is < 1 or > 12

        Returns:
            str: The full name of the month (e.g. "February")
        """
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        if 1 <= month_number <= 12:
            return month_names[month_number - 1]
        else:
            raise ValueError("Invalid month number")