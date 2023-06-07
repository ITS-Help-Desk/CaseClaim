import csv
from discord import app_commands
from discord.ext import commands
import discord

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class UnpingCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /unping command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot


    @app_commands.command(description = "Unping a case if you accidentally pinged one.")
    @app_commands.describe(case_num="The Case #")
    @app_commands.describe(user="The user that claimed the case and got pinged")
    async def unping(self, interaction: discord.Interaction, case_num: str, user: discord.Member) -> None:
        """This command allows a lead to manually unping a case by providing the case number and the user.

        After running this command, the case will show as completed in the log file.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            case_num (str): The case number that will be unpinged.
            user (discord.Member): The user that will be unpinged.
        """
        # Check if user is a lead
        if self.bot.check_if_lead(interaction.user):
            await interaction.response.defer(ephemeral=True) # Wait in case process takes a long time

            try:
                UnpingCommand.remove_ping(interaction.user.id, user.id, case_num)
            except Exception as e:
                await interaction.followup.send(content=f"Error: {e}", ephemeral=True)
                return
            

            await interaction.followup.send(content="Success! Remember to inform the tech that this case has been unpinged.", ephemeral=True)
        else:
            # Return error message if user is not Lead
            bad_user_embed = discord.Embed(
                description=
                f"<@{interaction.user.id}>, you do not have permission to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=bad_user_embed, ephemeral=True)
    

    @staticmethod
    def remove_ping(interaction_user: int, user_id: int, case_num: str) -> None:
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
