from discord import app_commands
from discord.ext import commands
import discord

from bot.modals.announcement_modal import AnnouncementModal
from ..modals.outage_modal import OutageModal
import traceback

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bot.bot import Bot


class AnnouncementCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /announcement command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

        
    @app_commands.command(description="Sends an announcement")
    #@app_commands.autocomplete(choices=rps_autocomplete)

    @app_commands.choices(choices=[
        app_commands.Choice(name="Outage", value="outage"),
        app_commands.Choice(name="Announcement", value="announcement"),
        #app_commands.Choice(name="Informational Announcement", value="infoannouncement"),
    ])
    async def announcement(self, interaction: discord.Interaction, choices: app_commands.Choice[str]) -> None:
        """This command allows a PA to create an announcement.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        # Check if user is a PA
        if self.bot.check_if_pa(interaction.user):
            if str(choices.value) == "outage":
                outage_modal = OutageModal(self.bot)
                await interaction.response.send_modal(outage_modal)
            elif str(choices.value) == "announcement":
                announcement_modal = AnnouncementModal(self.bot)
                await interaction.response.send_modal(announcement_modal)
            elif str(choices.value) == "infoannouncement":
                pass
            else:
                await interaction.response.send_message(content="Error! Invalid choice selected", ephemeral=True)
        else:
            # Return error message if user is not PA
            msg = f"<@{interaction.user.id}>, you do not have permission to use this command!"
            await interaction.response.send_message(content=msg, ephemeral=True)

    
    @announcement.error
    async def announcement_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)
        await ch.send(f"Error with **/outage** ran by <@!{ctx.user.id}>.\n```{full_error}```")