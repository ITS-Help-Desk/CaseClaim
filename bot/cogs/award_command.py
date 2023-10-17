from discord import app_commands
from discord.ext import commands
import discord
import traceback

from bot.models.team import Team
from bot.models.team_point import TeamPoint

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class AwardCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /award command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a graph of the timing of case claims")
    @app_commands.default_permissions(mute_members=True)
    @app_commands.describe(team="The team that the points will be awarded to")
    @app_commands.describe(points="The amount of points that will be awarded")
    @app_commands.describe(description="Why the points are being awarded")
    async def award(self, interaction: discord.Interaction, team: discord.Role, points: int, description: str) -> None:
        """Allows a lead to assign a team points for completing certain tasks.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            team (discord.Role): The team that will be awarded
            points (int): The amount of points that will be awarded
            description (str): The reason why the points are being given
        """
        if not self.bot.check_if_lead(interaction.user):
            msg = f"<@{interaction.user.id}>, you do not have permission to use this command!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)
            return

        t = Team.from_role_id(self.bot.connection, team.id)
        if t is None:
            msg = f"<@{interaction.user.id}>, team not found!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)
            return

        if not 0 < points < 9:
            msg = f"<@{interaction.user.id}>, please award no more than 9 points!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)
            return

        tp = TeamPoint(t.role_id, points, description, interaction.created_at)
        tp.add_to_database(self.bot.connection)

        ch = await interaction.guild.fetch_channel(self.bot.bot_channel)
        await ch.send(content=f"<@&{team.id}> has been awarded {points} point{'s' if points != 1 else ''} by <@!{interaction.user.id}>.\n> " + description, silent=True)

        await interaction.response.send_message(content="👍", ephemeral=True, delete_after=300)

    @award.error
    async def award_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/award** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)