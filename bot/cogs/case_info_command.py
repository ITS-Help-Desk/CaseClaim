from discord import app_commands
from discord.ext import commands
import discord
import csv
import time
import datetime

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class CaseInfoCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /case_info command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Shows a list of all the previous techs who've worked on a case")
    @app_commands.describe(case_num="Case #")
    async def case_info(self, interaction: discord.Interaction, case_num: str) -> None:
        """Changes the percent of cases that will be sent to the review channel. If a case isn't sent
        for review, it will automatically be logged.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            percentage (int): The new percent of cases that'll be reviewed.
        """
        # Check if user is a lead
        data = []
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[2] == case_num:
                    data.append(row)
        

        if self.bot.check_if_lead(interaction.user):
            description = self.rows_to_str(data, include_comments=True)
        else:
            description = self.rows_to_str(data)
        
        embed = discord.Embed(title=f'History of Case {case_num}')
        embed.colour = self.bot.embed_color
        embed.description = description

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=300)
        
        
    async def rows_to_str(self, rows: list[str], include_comments=False) -> str:
        copy = rows[:]
        copy.reverse()
        s = ''
        for row in copy:
            user = await self.bot.fetch_user(row[3])
            t = row[1]
            t = time.mktime(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timetuple())
            s += f'<t:{t}:f> - {user.name}'

            if include_comments and row[5] == "Flagged":
                s += f' [**{row[6]}**: {row[7]}]'


            s += '\n'
        
        return s
