from discord import app_commands
from discord.ext import commands
import discord

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class UpdatePercentCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /update_percent command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    
    @app_commands.command(description="Changes the percent of cases that will be sent to the review channel")
    @app_commands.describe(percentage="The new percent of cases (e.g. 100 or 50)")
    async def update_percent(self, interaction: discord.Interaction, percentage: int) -> None:
        """Changes the percent of cases that will be sent to the review channel. If a case isn't sent
        for review, it will automatically be logged.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            percentage (int): The new percent of cases that'll be reviewed.
        """
        # Check if user is a lead
        if self.bot.check_if_lead(interaction.user):
            old = self.bot.review_rate * 100
            self.bot.review_rate = percentage / 100

            await interaction.response.send_message(f"Successfully updated case review rate from {old}% to {percentage}%.", ephemeral=True)
        else:
            # Wrong user tries to use the command
            bad_user_embed = discord.Embed(
                description=
                f"<@{interaction.user.id}>, you do not have permission to use this command!",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=bad_user_embed, ephemeral=True)
            