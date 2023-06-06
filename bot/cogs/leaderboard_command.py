from discord import app_commands
from discord.ext import commands
import discord
import csv
import time
import datetime
from .. import paginator

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from ..bot import Bot


class LeaderboardCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /leaderboard command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Shows a list of all cases a user has worked on")
    async def leaderboard(self, interaction: discord.Interaction) -> None:
        """Shows a leaderboard of all users by case numbers on the log file.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        await interaction.response.defer(ephemeral=True) # Wait in case process takes a long time

        # Count the amount of cases worked on by each user
        counts = {}
        first_date = None
        with open('log.csv', 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                # Find first date
                if first_date is None:
                    first_date = row[1]

                id = int(row[3])
                if not id in counts.keys():
                    counts[id] = 0
                counts[id] += 1
        
        row_strs = []
        counts_sorted_keys = sorted(counts, key=counts.get, reverse=True)

        for i in range(len(counts_sorted_keys)):
            desc = ''
            key = counts_sorted_keys[i]
            desc += f'{i + 1}: '
            
            # Get user, replace with ID if absent
            user: Union[Optional[discord.Member], int]
            try:
                user = await interaction.guild.fetch_member(key)
            except:
                user = key
            if user is None:
                user = key
            
            if type(user) == int:
                desc += f'**{user}**'
            else:
                desc += f'**{user.display_name}**'
            desc += f' ({counts[key]})'
            row_strs.append(desc)

        titles = f'ITS Help Desk Case Leaderboard'
        try:
            start_time = datetime.datetime.strptime(first_date, "%Y-%m-%d %H:%M:%S.%f")  
        except:
            start_time = datetime.datetime.now()
        embeds = self.create_paginator_embeds(row_strs, titles, start_time)
        await paginator.Simple(ephemeral=True).start(interaction, embeds)

 
    def create_paginator_embeds(self, data: list[str], title: str, start_time: datetime.datetime) -> list[discord.Embed]:
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
            new_embed.set_footer(text="Starting from")
            new_embed.timestamp = start_time
            description = ''
            
            # Add ten (or fewer) cases
            for j in range(min(10, len(data))):
                row = data.pop(0)
                description += row + '\n'
            
            new_embed.description = description
            embeds.append(new_embed)
            i += 10

        return embeds
        
