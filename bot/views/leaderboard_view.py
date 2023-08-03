import datetime
import discord
import discord.ui as ui
from mysql.connector import MySQLConnection
from bot.helpers import month_number_to_name

from bot.models.checked_claim import CheckedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.status import Status

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
    async def button_refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False)  # Acknowledge button press

        new_embed = LeaderboardView.create_embed(self.bot, interaction.created_at)
        new_embed.set_thumbnail(url=interaction.guild.icon.url)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed)

    @ui.button(label="My Rank", style=discord.ButtonStyle.secondary, custom_id="myrank")
    async def button_myrank(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a user it shows their personal
        rank and statistics.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False)  # Acknowledge button press

        user_id = interaction.user.id
        data = LeaderboardView.get_data(self.bot, interaction.created_at)

        # Create embed
        embed = discord.Embed(title=f"{interaction.user.display_name}'s Ranking")
        embed.colour = self.bot.embed_color
        try:
            embed.set_thumbnail(url=interaction.user.avatar.url)
        except:
            pass  # User doesn't have avatar

        # Set footer
        embed.set_footer(text="Last Updated")
        embed.timestamp = interaction.created_at

        # Get month data
        try:
            mc = data[0][0]  # Get general count
            mp = data[2]  # Get general ping count

            mc_sorted_keys = data[0][1]  # Get sorted count
            month_rank = mc_sorted_keys.index(user_id) + 1  # Find ranks

            month_count = mc[user_id]  # Get user count
            month_pings = mp[user_id]  # Get user ping

            month_checked_rate = int(((month_count - month_pings) / month_count) * 100)  # Get ping rate
            embed.add_field(name="Month Rank",
                            value=f"Rank: **{month_rank}**\nClaims: **{month_count}**\nCheck Percent: **{month_checked_rate}%**")
        except ValueError:
            pass

        # Get semester data
        try:
            sc = data[1][0]  # Get general counts
            sp = data[3]  # Get general ping count

            sc_sorted_keys = data[1][1]  # Get sorted count
            semester_rank = sc_sorted_keys.index(user_id) + 1  # Find ranks

            semester_count = sc[user_id]  # Get user count
            semester_pings = sp[user_id]  # Get user ping

            semester_checked_rate = int(((semester_count - semester_pings) / semester_count) * 100)  # Get ping rate
            embed.add_field(name="Semester Rank",
                            value=f"Rank: **{semester_rank}**\nClaims: **{semester_count}**\nCheck Percent: **{semester_checked_rate}%**")
        except ValueError:
            pass

        await interaction.followup.send(embed=embed, ephemeral=True)

    @staticmethod
    def create_embed(bot: 'Bot', interaction_date: datetime.datetime) -> discord.Embed:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            bot (Bot): A reference to the bot class
            interaction_date (datetime.datetime): The time at which this request is made.

        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        month_ranking, semester_ranking, team_ranking = LeaderboardView.create_rankings(bot, interaction_date)

        # Create embed
        embed = discord.Embed(title="ITS Case Claim Leaderboard")
        embed.colour = bot.embed_color

        embed.add_field(name=f"{month_number_to_name(interaction_date.month)} Ranks", value=month_ranking, inline=True)
        embed.add_field(name=f"Team Ranks", value=team_ranking, inline=True)
        embed.add_field(name="Semester Ranks", value=semester_ranking, inline=True)
        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed

    @staticmethod
    def create_rankings(bot: 'Bot', interaction_date: datetime.datetime) -> tuple[str, str, str]:
        """Creates the ranking strings for monthly and semester ranks.

        Args:
            bot (Bot): A reference to the bot class
            interaction_date (datetime.datetime): The time at which this request is made.

        Returns:
            tuple[str, str, str]: Returns a tuple containing ("1. Andrew\n2. James", "1. James\n2. Andrew") where
            the first element is for monthly and second element is for semester.
        """
        data = LeaderboardView.get_data(bot, interaction_date)

        mc = data[0][0]
        sc = data[1][0]

        mc_sorted_keys = data[0][1]
        sc_sorted_keys = data[1][1]

        tc = data[4][0]
        tc_sorted_keys = data[4][1]

        month_ranks = []
        semester_ranks = []
        team_ranks = []

        # Create month written ranking
        for i in range(min(4, len(mc_sorted_keys))):
            month_id = mc_sorted_keys[i]
            month_ranks.append(f"**{i + 1}.** <@!{month_id}> ({mc[month_id]})")

        month_ranking = "\n".join(user for user in month_ranks)

        # Create year written ranking
        for i in range(min(4, len(sc_sorted_keys))):
            semester_id = sc_sorted_keys[i]
            semester_ranks.append(f"**{i + 1}.** <@!{semester_id}> ({sc[semester_id]})")

        semester_ranking = "\n".join(user for user in semester_ranks)

        # Create team written ranking
        for i in range(min(4, len(tc_sorted_keys))):
            team_id = tc_sorted_keys[i]
            team_ranks.append(f"**{i + 1}.** <@&{team_id}> ({tc[team_id]})")

        team_ranks = "\n".join(user for user in team_ranks)

        return month_ranking, semester_ranking, team_ranks

    @staticmethod
    def get_data(bot: 'Bot', interaction_date: datetime.datetime) -> tuple[
        tuple[dict[int, int], list[int]], tuple[dict[int, int], list[int]], dict[int, int], dict[int, int], tuple[dict[int, int], list[int]]]:
        """Collects a large amount of data to be used by various commands and events within this bot.
        This function collects:
            - Total amount of cases claimed by each user by month
            - Total amount of cases claimed by each user by semester
            - Ranking of cases claimed by each user by month
            - Ranking of cases claimed by each user by semester
            - Total amount of pinged cases by each user by month
            - Total amount of pinged cases by each user by semester
        Args:
            bot (Bot): A reference to the Bot class
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

        teams = {}
        for team in bot.teams:
            teams[team] = 0

        claims = CheckedClaim.search(bot.connection)
        for claim in claims:
            # Skip cases that are "done"
            if claim.status == Status.DONE:
                continue

            # Initialize month/semester ping count dicts
            if claim.tech.discord_id not in month_ping_counts.keys():
                month_ping_counts[claim.tech.discord_id] = 0
            if claim.tech.discord_id not in semester_ping_counts.keys():
                semester_ping_counts[claim.tech.discord_id] = 0

            # Organize data for month
            if claim.claim_time.month == interaction_date.month and claim.claim_time.year == interaction_date.year:
                if claim.tech.discord_id not in month_counts.keys():
                    month_counts[claim.tech.discord_id] = 0
                month_counts[claim.tech.discord_id] += 1

                # Add pinged
                if claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                    month_ping_counts[claim.tech.discord_id] += 1

            # Check for semester
            if claim.claim_time.year != interaction_date.year:
                continue

            if 1 <= claim.claim_time.month <= 6:
                sem1 = "Spring"
            else:
                sem1 = "Fall"

            if 1 <= interaction_date.month <= 6:
                sem2 = "Spring"
            else:
                sem2 = "Fall"

            if sem1 != sem2:
                continue

            # Organize data for semester
            if claim.tech.discord_id not in semester_counts.keys():
                semester_counts[claim.tech.discord_id] = 0
            semester_counts[claim.tech.discord_id] += 1

            # Add pinged
            if claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                semester_ping_counts[claim.tech.discord_id] += 1

            # Organize team data
            if claim.tech.team == 0:
                continue
            teams[claim.tech.team] += 1

        # Sort data
        semester_counts_sorted_keys = sorted(semester_counts, key=semester_counts.get, reverse=True)
        month_counts_sorted_keys = sorted(month_counts, key=month_counts.get, reverse=True)
        team_counts_sorted_keys = sorted(teams, key=teams.get, reverse=True)

        return ((month_counts, month_counts_sorted_keys), (semester_counts, semester_counts_sorted_keys), month_ping_counts, semester_ping_counts, (teams, team_counts_sorted_keys))