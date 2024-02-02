import discord
import discord.ui as ui

from bot.models.checked_claim import CheckedClaim
from bot.models.feedback import Feedback

from bot.views.resolve_ping_view import ResolvePingView

from bot.status import Status

# Avoid circular import
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot

class ResolvePingAwaitLeadView(ui.View):
    def __init__(self, bot: "Bot"):
        """
        Creates a temporary view with buttons that lead to all of a
        leads resolve options.

        Args:
            bot (Bot): A reference to the original bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Acknowledged", style=discord.ButtonStyle.primary, custom_id="leadackping")
    async def button_acknowledge_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Close the ping. Not sure what this button is supposed to do at the moment so just copying
        the other button at the moment when I clarify the acknowledge request.
        """
        await interaction.response.send_message(content="You clicked the acknowledge button :)", ephemeral=True)

    @ui.button(label="Complete", style=discord.ButtonStyle.primary, custom_id="completesender")
    async def button_complete_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Create the temporary message that gives the lead the option to generate a message to handle the ping.

        Args:
            interaction: The discord interaction to respond to
            button: This button from the decorator
        """
        case = CheckedClaim.from_ping_thread_id(self.bot.connection, interaction.channel_id)
        
        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True, delete_after=180)
            return
        if case.lead.discord_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True, delete_after=180)
            return
        # Return the original resolve_ping_view as an ephemeral message.
        await interaction.response.send_message(content=f"Select an Option to Close the Case", view=ResolvePingView(self.bot), ephemeral=True)

