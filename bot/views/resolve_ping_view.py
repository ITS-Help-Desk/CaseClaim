import csv
import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.helpers import find_case
from bot.status import Status

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

	
    @ui.button(label="Close and Change Status", style=discord.ButtonStyle.success, custom_id="changestatus")
    async def button_change_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a lead to close the thread and change the log
        status of a case that's been pinged to Resolved.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = find_case(message_id=self.original_message_id, pinged=True)
        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return
        
        if case.lead_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return
        
        user = await interaction.channel.fetch_member(case.tech_id)
        
        await interaction.channel.remove_user(interaction.user) # Remove lead
        await interaction.channel.remove_user(user) # Remove tech
        
        # Change Log file
        self.remove_ping(interaction.user.id, case.tech_id, case.case_num, Status.RESOLVED)
            
        await interaction.response.defer(thinking=False) # Acknowledge button press
            

    @ui.button(label="Close and Keep Pinged", style=discord.ButtonStyle.danger, custom_id="keeppinged")
    async def button_keep_pinged(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a lead to close the thread and keep
        the status of the case as Pinged in the log file.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = find_case(message_id=self.original_message_id, pinged=True)
        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return
        
        if case.lead_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return
        
        user = await interaction.channel.fetch_member(case.tech_id)

        await interaction.channel.remove_user(interaction.user) # Remove lead
        await interaction.channel.remove_user(user) # Remove tech

        await interaction.response.defer(thinking=False) # Acknowledge button press
    

    @ui.button(label="Unping", style=discord.ButtonStyle.secondary, custom_id="mistakeping")
    async def button_mistake_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a lead to close the thread and change the log
        status of a case that's been pinged to Checked. This is used if the case is
        mistakenly pinged.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = find_case(message_id=self.original_message_id, pinged=True)
        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return
        
        if case.lead_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return
        
        user = await interaction.channel.fetch_member(case.tech_id)
        
        await interaction.channel.remove_user(interaction.user) # Remove lead
        await interaction.channel.remove_user(user) # Remove tech
        
        # Change Log file
        self.remove_ping(interaction.user.id, case.tech_id, case.case_num, Status.CHECKED)
            
        await interaction.response.defer(thinking=False) # Acknowledge button press
        

    def remove_ping(self, interaction_user: int, user_id: int, case_num: str, new_status: Status) -> None:
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
                # Replace row once found
                if not found_row and row[2] == case_num and row[5] == Status.PINGED and int(row[3]) == user_id:
                    found_row = True
                    row[4] = str(interaction_user)
                    row[5] = Status.RESOLVED
                
                    # Remove severity and comment
                    if new_status == Status.CHECKED:
                        row[5] = Status.CHECKED
                        row[6] = ''
                        row[7] = ''
                lines.append(row)
                
        # No case could be found, return False
        if not found_row:
            raise ValueError("Case not found. Case num or user is incorrect, or case itself isn't pinged.")
    
        with open('log.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for line in lines:
                writer.writerow(line)