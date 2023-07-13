from discord import app_commands
from discord.ext import commands
import discord
from ..modals.feedback_modal import FeedbackModal
from bot.helpers import find_case
import traceback

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.bot import Bot


class PingCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /ping command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Manually pings a case")
    @app_commands.describe(case_num="The case number that will be pinged.")
    @app_commands.describe(user="The user that will be pinged.")
    @app_commands.default_permissions(mute_members=True)
    async def ping(self, interaction: discord.Interaction, case_num: str, user: discord.Member) -> None:
        """This command allows a lead to manually ping a case by providing the case number and the user.

        After running this command, the Feedback Modal will appear and allow
        a lead to type in a description and a severity level.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            case_num (str): The case number that will be pinged.
            user (discord.Member): The user that will be pinged.
        """
        # Check if user is a lead
        if self.bot.check_if_lead(interaction.user):
            case = find_case(case_num, user_id=user.id, pinged=False)
            if case is None:
                await interaction.response.send_message(content="Error! Case couldn't be found. Please ensure it's already been checked and reported in the log file.", ephemeral=True)
                return

            fbModal = FeedbackModal(self.bot, case)
            await interaction.response.send_modal(fbModal)
        else:
            # Return error message if user is not Lead
            msg = f"<@{interaction.user.id}>, you do not have permission to use this command!"
            await interaction.response.send_message(content=msg, ephemeral=True)
        
    
    @ping.error
    async def ping_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)
        
        msg = f"Error with **/ping** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)