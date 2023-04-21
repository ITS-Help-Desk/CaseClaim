from discord import app_commands
from discord.ext import commands
import discord


class Mickie(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    
    @app_commands.command(description="you're so fine")
    async def mickie(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"Oh {interaction.user.mention} you're so fine, you blow my mind.")
        