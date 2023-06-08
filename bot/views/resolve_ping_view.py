import csv
import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.helpers import find_case

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
        case = find_case(message_id=self.original_message_id, pinged=True)
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
            self.remove_ping(interaction.user.id, case.tech_id, case.case_num)
        except Exception as e:
                await interaction.response.send(content=f"Error: {e}", ephemeral=True)
                return
            
        await interaction.response.defer(thinking=False) # Acknowledge button press
            

    @ui.button(label="Keep as Pinged", style=discord.ButtonStyle.danger, custom_id="keeppinged")
    async def button_keep_pinged(self, interaction: discord.Interaction, button: discord.ui.Button):
        case = find_case(message_id=self.original_message_id, pinged=True)
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
        

    def remove_ping(self, interaction_user: int, user_id: int, case_num: str) -> None:
        """This function removes a ping from the log.csv file, and replaces the information
        to show as if the case was never pinged.

        Args:
            interaction_user (int): The user that sent the command.
            user_id (int): The user for the case that's been pinged.
            case_num (str): The case number of the case that's been pinged.

        Raises:
            ValueError: If the case provided couldn't be found
        """
        # Collect rows with this case
        lines = []
        found_row = False
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Exclude row once found
                if not found_row and row[2] == case_num and row[5] == "Pinged" and int(row[3]) == user_id:
                    found_row = True
                    row[4] = str(interaction_user)
                    row[5] = "Complete"
                    row[6] = ""
                    row[7] = ""
                
                lines.append(row)
                
                
        # No case could be found, return False
        if not found_row:
            raise ValueError("Case not found. Case num or user is incorrect, or case itself isn't pinged.")
    
        with open('log.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for line in lines:
                writer.writerow(line)