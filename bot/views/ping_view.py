import discord
import discord.ui as ui

from bot.modals.assessment_modal import AssessmentModal
from bot.helpers import find_case

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class PingView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a view for when a case is pinged and a
        message is sent to a private thread

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

	
    @ui.button(label="Affirm", style=discord.ButtonStyle.primary, custom_id="affirm")
    async def button_affirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a tech to affirm a case of theirs that's
        been pinged.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = find_case(message_id=interaction.message.id, pinged=True)
        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return
        
        if case.tech_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return 

        fbModal = AssessmentModal(self.bot, case)
        await interaction.response.send_modal(fbModal)
        