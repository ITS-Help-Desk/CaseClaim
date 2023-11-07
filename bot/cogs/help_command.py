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
        embed.description = 'For more information, go [here](https://github.com/ajockelle/CaseClaim).'
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.colour = self.bot.embed_color

        # Add standard commands
        embed.add_field(name='/help', value='Shows all the commands for the bot.')
        embed.add_field(name='/join', value='Records your first and last name for analytic purposes')
        embed.add_field(name='/claim <case_num>', value=f'Claims a case in the <#{self.bot.cases_channel}> channel')
        embed.add_field(name='/caseinfo <case_num>', value='See the history of who\'s worked on a case.')
        embed.add_field(name='/mycases', value='Shows all the cases that a user has worked on.')

        # Check if user is not a lead
        if not self.bot.check_if_lead(interaction.user):
            # Send standard help message
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=300)
            return

        # Add lead commands
        embed.add_field(name='/report', value=f'Shows a report for an optionally given user and month, or if it\'s pinged.')
        embed.add_field(name='/get_log', value='Returns the bot\'s log file.')
        embed.add_field(name='/casedist', value='Returns a graph of the case claim time distribution.')
        embed.add_field(name='/leaderboard', value='Shows a leaderboard of all users by case claim amount.')
        embed.add_field(name='/leadstats', value='Shows a leaderboard of all leads by case check amount.')
        embed.add_field(name='/ping', value='Manually ping a case')
        embed.add_field(name='/award', value='Award points to a team')

        # Check if user is not a lead
        if not self.bot.check_if_pa(interaction.user):
            # Send standard help message
            await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=300)
            return

        # Add PA commands
        embed.add_field(name='/announcement <type>', value='Sends an announcement/outage to the announcements channel.')

        await interaction.response.send_message(embed=embed, ephemeral=True, delete_after=300)

    @help.error
    async def help_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/help** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
