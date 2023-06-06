from discord import app_commands
from discord.ext import commands
import discord
import csv
import time
import datetime
from .. import paginator

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class MyCasesCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /mycases command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Shows a list of all cases a user has worked on")
    async def mycases(self, interaction: discord.Interaction) -> None:
        """Shows a list of all cases a user has worked on.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        await interaction.response.defer(ephemeral=True) # Wait in case process takes a long time

        # Collect rows with this case
        data = []
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if int(row[3]) == interaction.user.id:
                    data.append(row)
        
        for message_id in self.bot.active_cases.keys():
            c = self.bot.active_cases[message_id]
            if c.tech_id == interaction.user.id:
                data.append(c.log_format())
        
        # Send data
        new_data = self.data_to_rowstr(data)
        name = await interaction.guild.fetch_member(interaction.user.id)
        name = name.display_name
        title = f'Cases Worked on by {name} ({len(new_data)})'
        if len(new_data) <= 10:
            embed = discord.Embed(title=title)
            embed.colour = self.bot.embed_color
            embed.description = '\n'.join(row for row in new_data)

            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embeds = self.create_paginator_embeds(new_data, title)
            await paginator.Simple(ephemeral=True).start(interaction, embeds)
        
        
    def data_to_rowstr(self, rows: list[str]) -> list[str]:
        """Converts the raw data into a list of strings
        that can be used in the embed description.

        Args:
            rows (list[str]): The list of raw strings from the csv.

        Returns:
            list[str]: The list of descriptions that can be directly used in an embed.
        """
        copy = rows[:]
        copy.reverse()
        new_data = []
        for row in copy:
            s = ''
            # Include just ID in case user cannot be found    
            t = row[1]

            if row[5] == "":
                s += "**[ACTIVE]**"

            # Convert timestamp to UNIX
            t = int(time.mktime(datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S.%f").timetuple()))
            s += f'<t:{t}:f> - {row[2]}'

            new_data.append(s)
        
        return new_data

 
    def create_paginator_embeds(self, data: list[str], title: str) -> list[discord.Embed]:
        """Creates a list of embeds that can be used with a paginator.

        Args:
            data (list[str]): The list of case descriptions.
            title (str): The title for each of the embeds

        Returns:
            list[discord.Embed]: A list of embeds for the paginator.
        """
        # Create a list of embeds to paginate
        embeds = []
        i = 0
        data_len = len(data)

        # Go through all cases
        while i < data_len:
            # Create an embed for every 10 cases
            new_embed = discord.Embed(title=title)
            new_embed.colour = self.bot.embed_color
            description = ''
            
            # Add ten (or fewer) cases
            for j in range(min(10, len(data))):
                row = data.pop(0)
                description += row + '\n'
            
            new_embed.description = description
            embeds.append(new_embed)
            i += 10

        return embeds
        
