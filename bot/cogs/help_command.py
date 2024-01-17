from discord import app_commands
from discord.ext import commands
import discord
import traceback

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

    @app_commands.command(description="Instructions for how to use the bot.")
    async def help(self, interaction: discord.Interaction) -> None:
        """Sends a message back to the user explaining how to use the bot.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        embed = discord.Embed(title='ITS Help Desk Case Claim Bot')
        embed.description = 'For more information, go to the bot\'s [GitHub page](https://github.com/ajockelle/CaseClaim).'
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.colour = self.bot.embed_color

        # Add standard commands
        embed.add_field(name='/claim <case_num>', value=f'Claims a case in the <#{self.bot.cases_channel}> channel.')
        embed.add_field(name='/mycases', value='Shows a list of all the cases that you\'ve worked on.')
        embed.add_field(name='/caseinfo <case_num>', value=' Shows who\'s worked on a case in the past.')

        # Check if user is not a lead
        if not self.bot.check_if_lead(interaction.user):
            # Send standard help message
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=300)
            return

        # Add lead commands
        embed.add_field(name='/report', value=f'Get a list of cases in a spreadsheet')
        embed.add_field(name='/announcement', value='Make a global announcement or outage in Discord.')
        embed.add_field(name='/ping', value='Manually ping a case after it\'s been checked.')
        embed.add_field(name='/heatmap', value='Show a heatmap of what leads are checking certain tech\'s claims.')
        embed.add_field(name='/evaldata', value='Shows statistics that can be used for monthly evals.')
        embed.add_field(name='/casedist', value='Shows the distribution of cases claimed throughout the day.')
        embed.add_field(name='/award', value='Award a team points as a prize.')

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=300)

    @help.error
    async def help_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/help** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
