from discord import app_commands
from discord.ext import commands
import discord

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class HelpCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /help command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot


    @app_commands.command(description = "Instructions for how to use the bot.")
    async def help(self, interaction: discord.Interaction) -> None:
        """Sends a message back to the user explaining how to use the bot.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        
        embed = discord.Embed(title='ITS Help Desk Case Claim Bot')
        embed.description = 'For more information, go [here](https://github.com/ajockelle/CaseClaim).'
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.color = discord.Color.from_rgb(117, 190, 233)

        embed.add_field(name='/help', value='Shows all the commands for the bot.')
        embed.add_field(name='/claim <case_num>', value=f'Claims a case in the <#{self.bot.cases_channel}> channel')
        embed.add_field(name='/mickie', value='😉')
        
        # Check if user is not a lead
        if not self.bot.check_if_lead(interaction.user):
            # Send standard help message
            await interaction.response.send_message(embed=embed, ephemeral = True, delete_after=300)
            return
        
        embed.add_field(name='/report [user] [month]', value=f'Shows a report for an optionally given user and month.')
        embed.add_field(name='/flag', value='Manually flags a case and a user.')
        await interaction.response.send_message(embed=embed, ephemeral = True, delete_after=300)