import discord
import discord.ui as ui

from bot.status import Status
from ..modals.feedback_modal import FeedbackModal
from datetime import datetime

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class LeadViewRed(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a lead view in the lead case claim channel for submitting
        feedback on a completed case submitted by a tech.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

	
    @ui.button(label="Check", style=discord.ButtonStyle.secondary, custom_id="checkred")
    async def button_check(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a lead, it logs this case as Checked.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        self.case = self.bot.get_case(interaction.message.id)

        #Log the case as checked, then delete it
        self.case.status = Status.CHECKED
        self.case.lead_id = interaction.user.id
        self.case.submitted_time = datetime.now()
        self.case.log()
        self.bot.remove_case(self.case.message_id)
        
        await interaction.message.delete()
    
    @ui.button(label="Ping", style=discord.ButtonStyle.secondary, custom_id="pingred")
    async def button_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a lead, it brings up a feedback modal
        for a lead to ping a case.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        self.case = self.bot.get_case(interaction.message.id)

        #Prompt with Modal, record the response, create a private thread, then delete
        self.case.lead_id = interaction.user.id
        fbModal = FeedbackModal(self.bot, self.case)
        await interaction.response.send_modal(fbModal)