import datetime
from collections import OrderedDict
import discord
import discord.ui as ui
from mysql.connector import MySQLConnection
from bot.helpers import month_number_to_name
from bot.helpers import get_semester
from bot.helpers import LeaderboardResults

from bot.models.checked_claim import CheckedClaim
from bot.models.user import User
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

        new_embed, result = LeaderboardView.create_embed(self.bot, interaction)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed)

        await self.bot.update_icon(result.ordered_team_semester)

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

        user = User.from_id(self.bot.connection, interaction.user.id)

        result = LeaderboardResults(CheckedClaim.get_all_leaderboard(self.bot.connection, interaction.created_at.year), interaction.created_at, user)

        try:
            month_count = int(result.month_counts[user.discord_id])
            month_checked_rate = int(((month_count - result.month_ping_count) / month_count) * 100)
            month_rank = list(result.ordered_month.keys()).index(interaction.user.id) + 1

            embed.add_field(name="Month Rank", value=f"Rank: **{month_rank}**\nClaims: **{month_count}**\nCheck Percent: **{month_checked_rate}%**\n")
        except (KeyError, ValueError):
            pass

        try:
            semester_count = int(result.semester_counts[user.discord_id])
            semester_checked_rate = int(((semester_count - result.semester_ping_count) / semester_count) * 100)
            semester_rank = list(result.ordered_semester.keys()).index(interaction.user.id) + 1

            print(semester_count)
            print(result.semester_ping_count)

            embed.add_field(name="Semester Rank", value=f"Rank: **{semester_rank}**\nClaims: **{semester_count}**\nCheck Percent: **{semester_checked_rate}%**\n")
        except (KeyError, ValueError):
            pass

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180)

    @staticmethod
    def create_embed(bot: 'Bot', interaction: discord.Interaction) -> tuple[discord.Embed, LeaderboardResults]:
        """Creates the leaderboard embed for the /leaderboard command and for the
        Refresh button.

        Args:
            bot (Bot): A reference to the bot class
            interaction (discord.Interaction): The interaction requesting the leaderboard.

        Returns:
            discord.Embed: The embed object with everything already completed for month and semester rankings.
        """
        result = LeaderboardResults(CheckedClaim.get_all_leaderboard(bot.connection, interaction.created_at.year), interaction.created_at, None)

        month_ranking = ""
        # Create month written ranking
        for i in range(min(4, len(result.ordered_month.keys()))):
            user_id = list(result.ordered_month.keys())[i]
            month_ranking += f"**{i + 1}.** <@!{user_id}> | {result.ordered_month[user_id]}\n"

        semester_ranking = ""
        # Create semester written ranking
        for i in range(min(4, len(result.ordered_semester.keys()))):
            user_id = list(result.ordered_semester.keys())[i]
            semester_ranking += f"**{i + 1}.** <@!{user_id}> | {result.ordered_semester[user_id]}\n"

        month_team_ranking = ""
        # Create team written ranking
        for i in range(min(4, len(result.ordered_team_month.keys()))):
            team_id = list(result.ordered_team_month.keys())[i]
            month_team_ranking += f"**{i + 1}.** <@&{team_id}> | {result.ordered_team_month[team_id]}\n"

        semester_team_ranking = ""
        # Create team written ranking
        for i in range(min(4, len(result.ordered_team_semester.keys()))):
            team_id = list(result.ordered_team_semester.keys())[i]
            semester_team_ranking += f"**{i + 1}.** <@&{team_id}> | {result.ordered_team_semester[team_id]}\n"

        # Create embed
        embed = discord.Embed()
        embed.colour = bot.embed_color

        # Add leaderboard fields
        embed.add_field(name=f"{month_number_to_name(interaction.created_at.month)}", value="", inline=False)
        embed.add_field(name="", value=month_team_ranking, inline=True)
        embed.add_field(name="", value=month_ranking, inline=True)

        embed.add_field(name="Semester", value="", inline=False)

        embed.add_field(name="", value=semester_team_ranking, inline=True)
        embed.add_field(name="", value=semester_ranking, inline=True)

        embed.set_author(name="Leaderboard", icon_url=interaction.guild.icon.url)
        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed, result
