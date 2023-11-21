import asyncio
from discord import app_commands
from discord.ext import commands
import discord
from bot.models.checked_claim import CheckedClaim
#import time
#import datetime
#import io
#import matplotlib.pyplot as plt
#from matplotlib import ticker

# from bot.models.checked_claim import CheckedClaim
import graphs.casedist as cd

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class CaseDistCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /casedist command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a graph of the timing of case claims")
    @app_commands.default_permissions(mute_members=True)
    @app_commands.describe(month="The start month number")
    @app_commands.describe(day="The start day number")
    async def casedist(self, interaction: discord.Interaction, month: int, day: int) -> None:
        """Sends a graph of the case claim time distribution

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            month (int): The month of when cases will start being counted
            day (int): The day that cases will start being counted
        """
        claims = CheckedClaim.search(self.bot.connection) 
        data_stream = await asyncio.to_thread(cd.generate_casedist_plot, claims,month,day)

        # Create embed with chart
        chart = discord.File(data_stream, filename="chart.png")
        embed = discord.Embed(title="ITSHD Total Case Claim-Time Histogram")
        embed.set_image(url="attachment://chart.png")
        embed.colour = self.bot.embed_color

        await interaction.response.send_message(embed=embed, file=chart, ephemeral=True)
        
