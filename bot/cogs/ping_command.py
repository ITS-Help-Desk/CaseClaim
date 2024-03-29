from discord import app_commands
from discord.ext import commands
import discord
import traceback

from bot.models.checked_claim import CheckedClaim
from bot.models.user import User

from bot.forms.ping_form import PingForm

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class PingCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /ping command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Manually ping a case")
    @app_commands.describe(user="Tech that will be pinged")
    @app_commands.describe(case_num="Case #")
    @app_commands.default_permissions(mute_members=True)
    async def ping(self, interaction: discord.Interaction, user: discord.Member, case_num: str) -> None:
        """Allows a lead to manually ping a case.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
            user (discord.Member): The user that was responsible for the case
            case_num (str): The case number in Salesforce (e.g. "00960979")
        """
        case = CheckedClaim.find_latest_case(self.bot.connection, User.from_id(self.bot.connection, user.id), case_num)

        if case is not None:
            await interaction.response.send_modal(PingForm(self.bot, case))
        else:
            await interaction.response.send_message(content="Case not found! Please ensure that the correct case number and user are being submitted (double check using /report)", ephemeral=True, delete_after=180)


    @ping.error
    async def ping_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/ping** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
