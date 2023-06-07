import csv
import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING, Optional

from bot.claim import Claim
from bot.cogs.unping_command import UnpingCommand

if TYPE_CHECKING:
    from ..bot import Bot


class ResolvePingView(ui.View):
    def __init__(self, bot: "Bot", original_message_id: int):
        """Creates a leaderboard view for the /leaderboard command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            original_message_id (int): The ID of the original ping message.
        """
        super().__init__(timeout=None)
        self.bot = bot
        self.original_message_id = original_message_id

	
    @ui.button(label="Change Status", style=discord.ButtonStyle.success, custom_id="changestatus")
    async def button_change_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        case = self.find_case(self.original_message_id)
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
        
        if user is not None:
            await interaction.response.send_message(content="You cannot press this button yet.", ephemeral=True)
            return
        
        await interaction.channel.remove_user(interaction.user)
        
        # Change Log file
        try:
            UnpingCommand.remove_ping(interaction.user.id, case.tech_id, case.case_num)
        except Exception as e:
                await interaction.response.send(content=f"Error: {e}", ephemeral=True)
                return
            
        await interaction.response.defer(thinking=False) # Acknowledge button press
            

    @ui.button(label="Keep as Pinged", style=discord.ButtonStyle.danger, custom_id="keeppinged")
    async def button_keep_pinged(self, interaction: discord.Interaction, button: discord.ui.Button):
        case = self.find_case(self.original_message_id)
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
        
        if user is not None:
            await interaction.response.send_message(content="You cannot press this button yet.", ephemeral=True)
            return

        tech = await interaction.guild.fetch_member(case.tech_id)
        await interaction.channel.add_user(tech)

        await interaction.response.defer(thinking=False) # Acknowledge button press
        

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