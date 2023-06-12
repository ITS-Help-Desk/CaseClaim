from discord import app_commands
from discord.ext import commands
import discord
import csv
from bot.helpers import month_string_to_number, month_number_to_name

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING, Optional, Union

from bot.status import Status

if TYPE_CHECKING:
    from ..bot import Bot


class ReportCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /report command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot


    @app_commands.command(description = "Generate a report of cases logged.")
    @app_commands.describe(user="The user the report will be generated for.")
    @app_commands.describe(month="The month for the report (e.g. \"march\").")
    async def report(self, interaction: discord.Interaction, user: discord.Member = None, month: str = None, pinged: bool = False):
        """Creates a report of all cases, optionally within a certain month and optionally
        for one specific user.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            user (discord.Member, optional): The user that the report will correspond to. Defaults to None.
            month (str, optional): The month that all of the cases comes from. Defaults to None.
            pinged (bool, optional): Whether or not the case has been pinged. Defaults to False.
        """
        # Check if user is a lead
        if self.bot.check_if_lead(interaction.user):
            await interaction.response.defer(ephemeral=True) # Wait in case process takes a long time

            try:
                # Generate report embed
                report_embed = discord.Embed(
                    description= self.build_description(interaction.user, user, month, pinged),
                    color=self.bot.embed_color
                )

                report = await self.get_report(interaction.guild, user, month, pinged)

                await interaction.followup.send(embed=report_embed, file=report)
            except Exception as e:
                print(e)
                msg = f"<@{interaction.user.id}>, an error occurred when trying to pull this report!"
                await interaction.response.send_message(content=msg, ephemeral=True)
        else:
            # Return error message if user is not Lead
            msg = f"<@{interaction.user.id}>, you do not have permission to pull this report!"
            await interaction.response.send_message(content=msg, ephemeral=True)


    async def get_report(self, guild: discord.Guild, user: Optional[discord.Member]=None, month: Optional[str]=None, pinged: bool=False) -> discord.File:
        """Generated a report for a given user and month. If neither if these values are provided, this
        function will return a general report for a month, or a general report for a user.

        The log information is saved to a temporary csv and is uploaded to Discord.

        Args:
            user (Optional[discord.Member], optional): The user the report will be generated for. Defaults to None.
            month (Optional[str], optional): The month the report will be generated for (e.g. "march"). Defaults to None.
            pinged (bool, optional): Whether or not the cae has been pinged. Defaults to None.

        Returns:
            discord.File: The csv file saved on Discord.
        """
        user_map: dict[int, Union[discord.Member, int]] = {}
        
        # Open file and record all data requested
        with open('log.csv', 'r') as csvfile:
            reader = csv.reader(csvfile)
            rows = []
            try:
                month_num = self.month_string_to_number(month.lower())
            except:
                pass
            for row in reader:
                # Check for correct month
                if month is not None:
                    if row[1][5:7] != month_num:
                        continue
                    
                # Check for correct user
                if user is not None:
                    if row[3] != str(user.id):
                        continue
                
                # Check if pinged
                if pinged:
                    if row[5] != Status.PINGED and row[5] != Status.RESOLVED:
                        continue
                
                for index in [3,4]:
                    if not int(row[index]) in user_map.keys():
                        # Add user to local map
                        try:
                            user_map[int(row[index])] = await guild.fetch_member(int(row[index]))
                        except:
                            user_map[int(row[index])] = int(row[index])
                        
                        if user_map.get(int(row[index]), None) == None:
                            user_map[int(row[index])] = int(row[index])
                        
                    if type(user_map[int(row[index])]) != int:
                        row[index] = user_map[int(row[index])].display_name
                
                row[1] = row[1][0:16] # Fix time
                
                # If all tests pass, add row
                row.pop(0) # Remove message_id
                rows.append(row)

        
        # Save to a temp file, then upload to Discord.
        return self.save_to_tempfile(rows)
        
    
    def save_to_tempfile(self, rows: list[list[str]]) -> discord.File:
        """Saves a given nested list to a temporary csv file.

        Args:
            rows (list[str]): The nested list containing the log information about the user's cases.

        Returns:
            discord.File: The csv file saved on Discord.
        """
        with open('temp.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in rows:
                writer.writerow(row)

        return discord.File('temp.csv')


    def build_description(self, requester: discord.User, user: Optional[discord.User], month: Optional[str], pinged: Optional[bool]) -> str:
        """Builds a description for the /report command depending on the parameters
        given by the user.

        Args:
            requester (discord.User): The user requesting the report.
            user (Optional[discord.User]): The user the report is for.
            month (Optional[str]): The month the report is for.
            pinged (Optional[bool]): Whether or not to show only pinged cases.

        Returns:
            str: The description for the /report command embed.
        """
        description = f"<@!{requester.id}>, here is your report for cases"

        if user is not None:
            description += f" by <@!{user.id}>"
        
        try:
            if month is not None:
                month_num = int(month_string_to_number(month.lower()))
                description += f" for the month of {month_number_to_name(month_num)}"
        except Exception as e:
            print(e)
        
        if pinged is not None:
            if pinged:
                description += " that've been pinged"
        

        description += "."
        return description
        