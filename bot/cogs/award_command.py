from discord import app_commands
from discord.ext import commands
import discord
import traceback

from bot.models.team import Team

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

    @app_commands.command()
    async def award(self, interaction: discord.Interaction, team: discord.Role, points: int) -> None:
        """

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            team (discord.Role): The team that will be awarded
            points (int): The amount of points that will be awarded
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

        t.give_points(self.bot.connection, points)
        ch = await interaction.guild.fetch_channel(self.bot.announcement_channel)
        await ch.send(content=f"<@&{team.id}> has been awarded {points} point{'s' if points != 1 else ''} by <@!{interaction.user.id}>")

        await interaction.response.send_message(content="👍", ephemeral=True, delete_after=300)

    @award.error
    async def award_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/award** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)