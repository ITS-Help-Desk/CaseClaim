import csv
import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.claim import Claim

if TYPE_CHECKING:
    from ..bot import Bot


class PingView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a leaderboard view for the /leaderboard command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

	
    @ui.button(label="Affirm", style=discord.ButtonStyle.primary, custom_id="affirm")
    async def button_affirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            case = self.find_case(interaction.message.id)
        except:
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
        try:
            case = self.find_case(interaction.message.id)
        except:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return
        
        if case.lead_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return 
    

    def find_case(self, message_id: int) -> Claim:
        case_row = []
        message_id = str(message_id)
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Save row once found
                if row[0] == message_id:
                    case_row = row
                    break
        
        return Claim.load_from_row(case_row)