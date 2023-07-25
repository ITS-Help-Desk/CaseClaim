from discord import app_commands
from discord.ext import commands
import discord
import traceback

from bot.forms.join_form import JoinForm

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class JoinCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /join command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Allows a user to be added to our list")
    async def join(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_modal(JoinForm(self.bot))

    @join.error
    async def join_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/join** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
