from discord import app_commands
from discord.ext import commands
import discord
import traceback

from bot.views.leadstats_view import LeadStatsView
from bot.helpers.leaderboard_helpers import LeadstatsResults

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from ..models.checked_claim import CheckedClaim

if TYPE_CHECKING:
    from ..bot import Bot


class LeadStatsCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /leadstats command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a list of all cases a lead has checked")
    @app_commands.default_permissions(mute_members=True)
    async def leadstats(self, interaction: discord.Interaction) -> None:
        """Shows a leaderboard of all users by cases checked on the log file.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        # Check if user is a lead
        if not self.bot.check_if_lead(interaction.user):
            # Return error message if user is not Lead
            bad_user_embed = discord.Embed(
                description=
                f"<@{interaction.user.id}>, you do not have permission to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=bad_user_embed, ephemeral=True, delete_after=180)
            return

        # Generate and send leadstats
        await interaction.response.defer()  # Wait in case process takes a long time
        result = LeadstatsResults(CheckedClaim.search(self.bot.connection), interaction.created_at)
        embed, file = result.create_embed(self.bot, interaction)
        await interaction.followup.send(embed=embed, view=LeadStatsView(self.bot), file=file)

    @leadstats.error
    async def check_leaderboard_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()
        print(full_error)

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/leadstats** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
