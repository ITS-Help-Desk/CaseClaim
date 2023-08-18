import datetime
from collections import OrderedDict
import discord
import discord.ui as ui
from mysql.connector import MySQLConnection
from bot.helpers import month_number_to_name

from bot.models.checked_claim import CheckedClaim
from bot.models.team import Team

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

        new_embed = LeaderboardView.create_embed(self.bot, interaction)

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

        month_ranks, semester_ranks, _, month_ping_ranks, semester_ping_ranks = LeaderboardView.get_rankings(self.bot.connection)

        try:
            # Get month data
            month_count = month_ranks[interaction.user.id]
            month_rank = list(month_ranks.keys()).index(interaction.user.id) + 1

            try:
                month_ping_count = month_ping_ranks[interaction.user.id]
                month_checked_rate = int(((month_count - month_ping_count) / month_count) * 100)
            except KeyError:
                month_checked_rate = 100

            embed.add_field(name="Month Rank", value=f"Rank: **{month_rank}**\nClaims: **{month_count}**\nCheck Percent: **{month_checked_rate}%**\n")
        except KeyError:
            pass

        try:
            # Get semester data
            semester_count = semester_ranks[interaction.user.id]
            semester_rank = list(semester_ranks.keys()).index(interaction.user.id) + 1

            try:
                semester_ping_count = semester_ping_ranks[interaction.user.id]
                semester_checked_rate = int(((semester_count - semester_ping_count) / semester_count) * 100)
            except KeyError:
                semester_checked_rate = 100

            embed.add_field(name="Semester Rank", value=f"Rank: **{semester_rank}**\nClaims: **{semester_count}**\nCheck Percent: **{semester_checked_rate}%**")
        except KeyError:
            pass

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180)

    @staticmethod
    def create_embed(bot: 'Bot', interaction: discord.Interaction) -> discord.Embed:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            bot (Bot): A reference to the bot class
            interaction (discord.Interaction): The interaction requesting the leaderboard.

        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        month_ranks, semester_ranks, team_ranks, _, _ = LeaderboardView.get_rankings(bot.connection)

        month_ranking = ""
        # Create month written ranking
        for i in range(min(4, len(month_ranks.keys()))):
            user_id = list(month_ranks.keys())[i]
            month_ranking += f"**{i + 1}.** <@!{user_id}> | {month_ranks[user_id]}\n"

        semester_ranking = ""
        # Create semester written ranking
        for i in range(min(4, len(semester_ranks.keys()))):
            user_id = list(semester_ranks.keys())[i]
            semester_ranking += f"**{i + 1}.** <@!{user_id}> | {semester_ranks[user_id]}\n"

        team_ranking = ""
        # Create team written ranking
        for i in range(min(4, len(team_ranks))):
            team_id = list(team_ranks.keys())[i]
            team_ranking += f"**{i + 1}.** <@&{team_id}> | {team_ranks[team_id]}\n"

        # Create embed
        embed = discord.Embed()
        embed.colour = bot.embed_color

        # Add leaderboard fields
        embed.add_field(name=f"Team", value=team_ranking, inline=True)
        embed.add_field(name=f"{month_number_to_name(interaction.created_at.month)}", value=month_ranking, inline=True)
        embed.add_field(name="Semester", value=semester_ranking, inline=True)

        embed.set_author(name="Leaderboard", icon_url=interaction.guild.icon.url)
        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed

    @staticmethod
    def get_rankings(connection: MySQLConnection) -> tuple[OrderedDict, OrderedDict, OrderedDict, dict, dict]:
        """Creates various rankings based on many factors for claims and pings. These factors
        are mostly date based.

        Args:
            claims (list[CheckedClaim]): The list of CheckedClaims that will be checked through.

        Returns:
            tuple[OrderedDict, OrderedDict, OrderedDict, dict, dict] - A tuple containing the data as follows:
                1. The ordered month claim counts
                2. The ordered semester claim counts
                3. The ordered semester team counts
                4. The month ping counts
                5. The semester ping counts
        """
        claims = CheckedClaim.get_all(connection)

        month_counts = {}
        semester_counts = {}
        team_counts = {}
        month_ping_counts = {}
        semester_ping_counts = {}

        current = datetime.datetime.now()
        current_sem = LeaderboardView.get_semester(current)
        for claim in claims:
            # Filter out DONE cases
            if claim.status == Status.DONE:
                continue

            # Filter out claims from different years
            if claim.claim_time.year != current.year:
                continue

            # Filter out claims from different semesters
            if LeaderboardView.get_semester(claim.claim_time) != current_sem:
                continue

            # Add semester claims
            semester_counts.setdefault(claim.tech.discord_id, 0)
            semester_counts[claim.tech.discord_id] += 1

            # Add to ping count (if the case was pinged)
            if claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                semester_ping_counts.setdefault(claim.tech.discord_id, 0)
                semester_ping_counts[claim.tech.discord_id] += 1

            # User doesn't have a team
            if claim.tech.team_id is None or claim.tech.team_id == 0:
                continue

            # Add team claims
            team_counts.setdefault(claim.tech.team_id, 0)
            team_counts[claim.tech.team_id] += 1

            # Filter out cases from different months
            if claim.claim_time.month != current.month:
                continue

            # Add month claims
            month_counts.setdefault(claim.tech.discord_id, 0)
            month_counts[claim.tech.discord_id] += 1

            # Add to ping count (if the case was pinged)
            if claim.status == Status.PINGED or claim.status == Status.RESOLVED:
                month_ping_counts.setdefault(claim.tech.discord_id, 0)
                month_ping_counts[claim.tech.discord_id] += 1

        for team in Team.get_all(connection):
            if team.role_id == 0:
                continue
            team_counts.setdefault(team.role_id, 0)
            team_counts[team.role_id] += team.points

        # Sort the data
        month_sorted_keys = sorted(month_counts, key=month_counts.get, reverse=True)
        semester_sorted_keys = sorted(semester_counts, key=semester_counts.get, reverse=True)
        team_sorted_keys = sorted(team_counts, key=team_counts.get, reverse=True)




        # Create ordered dictionaries
        ordered_month = OrderedDict()
        ordered_semester = OrderedDict()
        ordered_teams = OrderedDict()
        for key in month_sorted_keys:
            ordered_month[key] = month_counts[key]

        for key in semester_sorted_keys:
            ordered_semester[key] = semester_counts[key]

        for key in team_sorted_keys:
            ordered_teams[key] = team_counts[key]

        return ordered_month, ordered_semester, ordered_teams, month_ping_counts, semester_ping_counts

    @staticmethod
    def get_semester(t: datetime.datetime) -> str:
        """Returns the semester that the datetime object is located in.

        Jan - May -> Spring
        Jun - Aug 20 -> Summer
        Aug 21 - Dec -> Winter

        Args:
            t (datetime.datetime): The datetime object

        Returns:
            str - The name of the semester
        """
        if 1 <= t.month <= 5:
            return "Spring"

        if 6 <= t.month < 8:
            return "Summer"

        if t.month == 8 and t.day < 21:
            return "Summer"

        return "Fall"
