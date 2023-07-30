from discord import app_commands
from discord.ext import commands
import discord
import traceback

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class GetLogCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /getlog command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Returns the bot's log file.")
    async def getlog(self, interaction: discord.Interaction) -> None:
        """Sends a message back to the user explaining how to use the bot.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        # Check if user is not a lead
        if not self.bot.check_if_dev(interaction.user):
            # Return error message if user is not Lead
            msg = f"<@{interaction.user.id}>, you do not have permission to use this command!"
            await interaction.response.send_message(content=msg, ephemeral=True)
            return

        await interaction.response.send_message(content="Here's the log:", file=discord.File('discord.log'),
                                                ephemeral=True, delete_after=300)

    @getlog.error
    async def getlog_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/getlog** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)