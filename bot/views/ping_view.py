import csv
import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING, Optional

from bot.claim import Claim
from bot.views.resolve_ping_view import ResolvePingView

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
        case = self.find_case(interaction.message.id)
        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return
        
        if case.tech_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return 

        await interaction.channel.send(content=f"<@!{case.lead_id}>, this case has been affirmed by <@!{interaction.user.id}>.")
        await interaction.channel.remove_user(interaction.user)
        
        await interaction.response.defer(thinking=False) # Acknowledge button press
    
    @ui.button(label="Resolve", style=discord.ButtonStyle.secondary, custom_id="resolve")
    async def button_resolve(self, interaction: discord.Interaction, button: discord.ui.Button):
        case = self.find_case(interaction.message.id)
        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return
        
        if case.lead_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return 
        
        # Confirm that tech has affirmed the case (left the thread)
        try:
            user = await interaction.channel.fetch_member(case.tech_id)
        except:
            user = None
        
        if user is None:
            await interaction.response.send_message(view=ResolvePingView(self.bot, interaction.message.id), ephemeral=True)
        else:
            await interaction.response.send_message(content="You cannot press this button yet.", ephemeral=True)
    

    def find_case(self, message_id: int) -> Optional[Claim]:
        case_row = []
        message_id = str(message_id)
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Save row once found
                if row[0] == message_id:
                    case_row = row
                    break
        
        if len(case_row) == 0:
            return None
        return Claim.load_from_row(case_row)