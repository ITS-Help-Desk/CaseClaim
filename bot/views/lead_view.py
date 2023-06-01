import discord
import discord.ui as ui
from ..modals.feedback_modal import FeedbackModal

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class LeadView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a lead view in the lead case claim channel for submitting
        feedback on a completed case submitted by a tech.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

	
    @ui.button(label="Check", style=discord.ButtonStyle.success, custom_id="check")
    async def button_check(self, interaction: discord.Interaction, button):
        self.case = self.bot.get_case(interaction.message.id)

        #Log the case as checked, then delete it
        self.case.status = "Checked"
        self.case.lead_id = interaction.user.id
        self.case.log()
        self.bot.remove_case(self.case.message_id)
        
        await interaction.message.delete()
    
    @ui.button(label="Flag", style=discord.ButtonStyle.danger, custom_id="flag")
    async def button_flag(self, interaction: discord.Interaction, button):
        self.case = self.bot.get_case(interaction.message.id)

        #Prompt with Modal, record the response, create a private thread, then delete
        self.case.lead_id = interaction.user.id
        fbModal = FeedbackModal(self.bot, self.case)
        await interaction.response.send_modal(fbModal)
        await interaction.message.delete()