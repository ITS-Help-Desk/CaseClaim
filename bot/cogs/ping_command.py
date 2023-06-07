import csv
import datetime
from discord import app_commands
from discord.ext import commands
import discord
from ..modals.feedback_modal import FeedbackModal
from ..claim import Claim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.bot import Bot


class PingCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /ping command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Manually pings a case")
    @app_commands.describe(case_num="The case number that will be pinged.")
    @app_commands.describe(user="The user that will be pinged.")
    async def ping(self, interaction: discord.Interaction, case_num: str, user: discord.Member) -> None:
        """This command allows a lead to manually ping a case by providing the case number and the user.

        After running this command, the Feedback Modal will appear and allow
        a lead to type in a description and a severity level.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            case_num (str): The case number that will be pinged.
            user (discord.Member): The user that will be pinged.
        """
        # Check if user is a lead
        if self.bot.check_if_lead(interaction.user):
            case = Claim(case_num=case_num, tech_id=user.id)
            case_row = self.find_case(case_num, user.id)
            if len(case_row) == 0:
                await interaction.response.send_message(content="Error! Case couldn't be found. Please ensure it's already been checked and reported in the log file.", ephemeral=True)
                return
            
            case.message_id = int(case_row[0])
            case.submitted_time = datetime.datetime.strptime(case_row[1], "%Y-%m-%d %H:%M:%S.%f")

            self.remove_case(user.id, case_num)

            fbModal = FeedbackModal(self.bot, case)
            await interaction.response.send_modal(fbModal)
        else:
            # Return error message if user is not Lead
            bad_user_embed = discord.Embed(
                description=
                f"<@{interaction.user.id}>, you do not have permission to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=bad_user_embed, ephemeral=True)
    

    def find_case(self, case_num: str, user_id: int) -> list[str]:
        """Finds the first case in the log file that matches
        the provided information and hasn't been pinged.

        Args:
            case_num (str): The case number of the case that needs to be pinged.
            user_id (int): The user for the case that needs to be pinged.

        Returns:
            list[str]: The row from the log file for this case.
        """
        case_row = []
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Save row once found
                if row[2] == case_num and row[5] != "Pinged" and int(row[3]) == user_id:
                    case_row = row
                    break
        
        return case_row
    

    def remove_case(self, user_id: int, case_num: str) -> None:
        """Removes the first case in the log file that
        matches the provided information and hasn't been pinged.

        Args:
            user_id (int): The user for the case that needs to be pinged.
            case_num (str): The case number of the case that needs to be pinged.
        """
        # Collect rows with this case
        lines = []
        found_row = False
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Exclude row once found
                if not found_row and row[2] == case_num and row[5] != "Pinged" and int(row[3]) == user_id:
                    found_row = True
                    continue
                
                lines.append(row)
                    
        with open('log.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerows(lines)