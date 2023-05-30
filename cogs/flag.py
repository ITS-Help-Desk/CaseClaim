from discord import app_commands
from discord.ext import commands
import discord

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING
from cogs.case import Claim

from cogs.modals.feedback import FeedbackModal

if TYPE_CHECKING:
    from bot import Bot


class FlagCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /flag command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Manually flags a case")
    @app_commands.describe(case_num="The case number that will be flagged.")
    @app_commands.describe(user="The user that will be pinged.")
    async def flag(self, interaction: discord.Interaction, case_num: str, user: discord.Member) -> None:
        """This command allows a lead to manually flag a case by providing the case number and the user.

        After running this command, the Feedback Modal will appear and allow
        a lead to type in a description and a severity flag.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            case_num (str): The case number that will be flagged.
            user (discord.Member): The user that will be pinged.
        """
        guild = interaction.user.guild
        lead_role = discord.utils.get(guild.roles, name="Lead")
        if lead_role in interaction.user.roles:
            case = Claim(case_num, user.id)
            fbModal = FeedbackModal(self.bot, user, case)
            await interaction.response.send_modal(fbModal)
        else:
            # Return error message if user is not Lead
            bad_user_embed = discord.Embed(
                description=
                f"<@{interaction.user.id}>, you do not have permission to use this command!",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=bad_user_embed, ephemeral=True)