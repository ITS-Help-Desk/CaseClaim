import discord
import discord.ui as ui

from ..claim import Claim
from bot.views.resolve_ping_view import ResolvePingView

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class AssessmentModal(ui.Modal, title='Tech Assessment'):
    def __init__(self, bot: "Bot", case: Claim):
        """Creates an assessment form for a tech to provide
        how they resolved a ping, and allows a lead to review
        this assessment with a separate ResolvePingView.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            case (Claim): The case object.
        """
        super().__init__()
        self.bot = bot
        self.case = case
    
    assessment = ui.TextInput(label='Assessment (Optional)',style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates a private thread with the tech and sends a message
        with the feedback from the lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        await interaction.response.send_message(f"<@{self.case.lead_id}> has been pinged.", ephemeral=True)

        embed = discord.Embed(
            title="Case Assessment",
            description=f"<@!{self.case.tech_id}> has affirmed this case.")
        embed.colour = self.bot.embed_color

        if len(str(self.assessment)) != 0:
            embed.add_field(name="Assessment", value=self.assessment)
        
        await interaction.channel.send(content= f"<@!{self.case.lead_id}>", embed=embed, view=ResolvePingView(self.bot, self.case.message_id))