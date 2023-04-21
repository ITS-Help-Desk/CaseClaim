from discord import app_commands
from discord.ext import commands
import discord


class Help(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot


    @app_commands.command(description = "Instructions for how to use the /claim command.")
    async def help(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Claim a case using /claim followed by a case number.\n  - React with a ☑️ when you have completed the case.\n  - React with a ⚠️ to unclaim the case.\n", ephemeral = True, delete_after=300)