from discord import app_commands
from discord.ext import commands
import discord
import csv
import time
import datetime

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.status import Status

if TYPE_CHECKING:
    from ..bot import Bot


class CaseInfoCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /caseinfo command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Shows a list of all the previous techs who've worked on a case")
    @app_commands.describe(case_num="Case #")
    async def caseinfo(self, interaction: discord.Interaction, case_num: str) -> None:
        """Shows a list of all techs who've previously worked on a case, and shows the
        ping comments if the command sender is a lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
            case_num (str): The case number in Salesforce (e.g. "00960979")
        """
        await interaction.response.defer(ephemeral=True) # Wait in case process takes a long time

        # Collect rows with this case
        data = []
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[2] == case_num:
                    data.append(row)
        
        for message_id in self.bot.active_cases.keys():
            c = self.bot.active_cases[message_id]
            if c.case_num == case_num:
                data.append(c.log_format())
        
        # Check if user is a lead
        if self.bot.check_if_lead(interaction.user):
            description = await self.rows_to_str(data, include_comments=True)
        else:
            description = await self.rows_to_str(data)
        
        # Send data
        embed = discord.Embed(title=f'History of Case {case_num}')
        embed.colour = self.bot.embed_color
        embed.description = description

        await interaction.followup.send(embed=embed, ephemeral=True)
        
        
    async def rows_to_str(self, rows: list[str], include_comments=False) -> str:
        """Converts the rows provided into a string containing only the times and users
        and (optionally) case comments.

        Args:
            rows (list[str]): The list of rows that will be converted.
            include_comments (bool, optional): Whether or not comments will be included (only for leads). Defaults to False.

        Returns:
            str: The description containing the list with times, users, and comments.
        """
        copy = rows[:]
        copy.reverse()
        s = ''
        for row in copy:
            # Include just ID in case user cannot be found
            try:
                user = await self.bot.fetch_user(row[3])
                user = user.display_name
            except:
                user = row[3]
            if user is None:
                user = row[3]
            
            t = row[1]

            if row[5] == "":
                s += "**[ACTIVE]** "

            # Convert timestamp to UNIX
            try:
                t = int(time.mktime(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timetuple()))
                s += f'<t:{t}:f> - {user}'
            except:
                s += f'{user}'

            # Add comments
            if include_comments and (row[5] == Status.PINGED or row[5] == Status.RESOLVED):
                s += f' [**{row[6]}**: {row[7]}]'

            s += '\n'
        
        return s
