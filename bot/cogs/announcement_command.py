from discord import app_commands
from discord.ext import commands
import discord
import traceback

from bot.forms.outage_form import OutageForm
from bot.forms.announcement_form import AnnouncementForm

from bot.models.user import User

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
    @app_commands.choices(choices=[
        app_commands.Choice(name="Outage", value="outage"),
        app_commands.Choice(name="Announcement", value="announcement"),
        app_commands.Choice(name="Informational", value="informational")
    ])
    @app_commands.default_permissions(administrator=True)
    async def announcement(self, interaction: discord.Interaction, choices: app_commands.Choice[str]) -> None:
        """This command allows a PA to create an announcement.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            choices (Choice[str]): A list of choices for the type of announcement (Outage/Announcement).
        """
        # Check to see if user is in the list
        u = User.from_id(self.bot.connection, interaction.user.id)
        if u is None:
            msg = f"Please use the **/join** using this command."
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
            return

        # Check if user is a PA
        if self.bot.check_if_pa(interaction.user):
            if str(choices.value) == "outage":
                outage_modal = OutageForm(self.bot)
                await interaction.response.send_modal(outage_modal)
            elif str(choices.value) == "announcement":
                announcement_modal = AnnouncementForm(self.bot, False)
                await interaction.response.send_modal(announcement_modal)
            elif str(choices.value) == "informational":
                announcement_modal = AnnouncementForm(self.bot, True)
                await interaction.response.send_modal(announcement_modal)
            else:
                await interaction.response.send_message(content="Error! Invalid choice selected", ephemeral=True, delete_after=180)
        else:
            # Return error message if user is not PA
            msg = f"<@{interaction.user.id}>, you do not have permission to use this command!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)

    @announcement.error
    async def announcement_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/announcement** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)