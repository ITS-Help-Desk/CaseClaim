import discord
import discord.ui as ui
from bot.helpers.leaderboard_helpers import LeaderboardResults
from bot.helpers.other import *

from bot.models.checked_claim import CheckedClaim
from bot.models.user import User
from bot.models.team_point import TeamPoint

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.forms.leaderboard_form import LeaderboardForm

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

        result = LeaderboardResults(
            CheckedClaim.get_all_leaderboard(self.bot.connection, interaction.created_at.year),
            TeamPoint.get_all(self.bot.connection),
            interaction.created_at,
            User.from_id(self.bot.connection, interaction.user.id)
        )
        new_embed = result.create_embed(self.bot, interaction)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed)
        await self.bot.update_icon(result.ordered_team_month)

    @ui.button(label="My Rank", style=discord.ButtonStyle.success, custom_id="myrank")
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

        result = LeaderboardResults(
            CheckedClaim.get_all_leaderboard(self.bot.connection, interaction.created_at.year),
            TeamPoint.get_all(self.bot.connection),
            interaction.created_at,
            user
        )

        # Organize month data
        try:
            month_count = int(result.month_counts[user.discord_id])
            month_checked_rate = int(((month_count - result.month_ping_count) / month_count) * 100)
            month_rank = list(result.ordered_month.keys()).index(interaction.user.id) + 1

            embed.add_field(name="Month Rank", value=f"Rank: **{month_rank}**\nClaims: **{month_count}**\nCheck Percent: **{month_checked_rate}%**\n")
        except (KeyError, ValueError):
            pass

        # Organize semester data
        try:
            semester_count = int(result.semester_counts[user.discord_id])
            semester_checked_rate = int(((semester_count - result.semester_ping_count) / semester_count) * 100)
            semester_rank = list(result.ordered_semester.keys()).index(interaction.user.id) + 1

            embed.add_field(name="Semester Rank", value=f"Rank: **{semester_rank}**\nClaims: **{semester_count}**\nCheck Percent: **{semester_checked_rate}%**\n")
        except (KeyError, ValueError):
            pass

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=180)

    @ui.button(label="See Past", style=discord.ButtonStyle.secondary, custom_id="pastleaderboard")
    async def button_seepast(self, interaction: discord.Interaction, button: discord.ui.Button):
        form = LeaderboardForm(self.bot)
        await interaction.response.send_modal(form)

