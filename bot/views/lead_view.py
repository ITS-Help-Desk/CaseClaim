import discord
import discord.ui as ui
from .lead_view_red import LeadViewRed

from bot.status import Status
from ..modals.feedback_modal import FeedbackModal
from datetime import datetime

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
    async def button_check(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a lead, it logs this case as Checked.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        self.case = self.bot.claim_manager.get_claim(interaction.message.id)

        #Log the case as checked, then delete it
        self.case.status = Status.CHECKED
        self.case.lead_id = interaction.user.id
        self.case.submitted_time = datetime.now()
        self.case.log()
        self.bot.claim_manager.remove_claim(self.case.message_id)
        
        await interaction.message.delete()
    
    @ui.button(label="Ping", style=discord.ButtonStyle.danger, custom_id="ping")
    async def button_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a lead, it brings up a feedback modal
        for a lead to ping a case.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        self.case = self.bot.claim_manager.get_claim(interaction.message.id)

        #Prompt with Modal, record the response, create a private thread, then delete
        self.case.lead_id = interaction.user.id
        fbModal = FeedbackModal(self.bot, self.case)
        await interaction.response.send_modal(fbModal)

        # Update button appearance
        embed = interaction.message.embeds[0]
        embed.colour = discord.Colour.red()

        await interaction.message.edit(embed=embed, view=LeadViewRed(self.bot))