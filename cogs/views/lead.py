import discord
import discord.ui as ui
from datetime import datetime
from ..modals.feedback import FeedbackModal
from ..case import Claim

from typing import Union
# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import Bot


class LeadView(ui.View):
    def __init__(self, bot: "Bot", original_user: Union[discord.User, discord.Member], case: Claim):
        """Creates a lead view in the lead case claim channel for submitting
        feedback on a completed case submitted by a tech.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            original_user (Union[discord.User, discord.Member]): The user who sent the command to show the TechView.
            case (Claim): The case object.
        """
        super().__init__(timeout=None)
        self.bot = bot
        self.original_user = original_user #tech that claimed the case
        self.case = case
	
    @ui.button(label="Check", style=discord.ButtonStyle.success)
    async def button_check(self, interaction: discord.Interaction, button):
        #Log the case as checked, then delete it
        self.case.status = "Checked"
        self.case.lead_id = interaction.user.id
        self.case.log()
        
        await interaction.message.delete()
    
    @ui.button(label="Flag", style=discord.ButtonStyle.danger)
    async def button_flag(self, interaction: discord.Interaction, button):
        #Prompt with Modal, record the response, create a private thread, then delete
        fbModal = FeedbackModal(self.bot, self.original_user, self.case)
        await interaction.response.send_modal(fbModal)
        await interaction.message.delete()