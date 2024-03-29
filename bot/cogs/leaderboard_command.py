from discord import app_commands
from discord.ext import commands
import discord
import traceback

from bot.helpers.leaderboard_helpers import *

from bot.views.leaderboard_view import LeaderboardView

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class LeaderboardCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /leaderboard command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a list of all cases a user has worked on")
    @app_commands.default_permissions(mute_members=True)
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        """Shows a leaderboard of all users by case numbers on the database.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        if not self.bot.check_if_lead(interaction.user):
            # Return error message if user is not Lead
            bad_user_embed = discord.Embed(
                description=
                f"<@{interaction.user.id}>, you do not have permission to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=bad_user_embed, ephemeral=True, delete_after=180)
            return

        # Show current leaderboard
        await interaction.response.defer()  # Wait in case process takes a long time
        result = LeaderboardResults(
            CheckedClaim.get_all_leaderboard(self.bot.connection, interaction.created_at.year),
            TeamPoint.get_all(self.bot.connection), interaction.created_at, None)

        embed = result.create_embed(self.bot, interaction)
        await interaction.followup.send(embed=embed, view=LeaderboardView(self.bot))

    @leaderboard.error
    async def leaderboard_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/leaderboard** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
