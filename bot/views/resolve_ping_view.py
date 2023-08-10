import discord
import discord.ui as ui

from bot.models.checked_claim import CheckedClaim
from bot.models.ping import Ping

from bot.status import Status

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class ResolvePingView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a leaderboard view for the /leaderboard command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            original_message_id (int): The ID of the original ping message.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Close and Change Status", style=discord.ButtonStyle.success, custom_id="changestatus")
    async def button_change_status(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a lead to close the thread and change the log
        status of a case that's been pinged to Resolved.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = CheckedClaim.from_ping_thread_id(self.bot.connection, interaction.channel_id)

        if case.lead.discord_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return

        await interaction.channel.remove_user(interaction.user)  # Remove lead

        try:
            user = await interaction.channel.fetch_member(case.tech.discord_id)
            await interaction.channel.remove_user(user)  # Remove tech
        except:
            pass

        case.change_status(self.bot.connection, Status.RESOLVED)

        await interaction.response.defer(thinking=False)  # Acknowledge button press

    @ui.button(label="Close and Keep Pinged", style=discord.ButtonStyle.danger, custom_id="keeppinged")
    async def button_keep_pinged(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a lead to close the thread and keep
        the status of the case as Pinged in the log file.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = CheckedClaim.from_ping_thread_id(self.bot.connection, interaction.channel_id)
        if case.lead.discord_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return

        await interaction.channel.remove_user(interaction.user)  # Remove lead

        try:
            user = await interaction.channel.fetch_member(case.tech.discord_id)
            await interaction.channel.remove_user(user)  # Remove tech
        except:
            pass

        await interaction.response.defer(thinking=False)  # Acknowledge button press

    @ui.button(label="Unping", style=discord.ButtonStyle.secondary, custom_id="mistakeping")
    async def button_mistake_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a lead to close the thread and change the log
        status of a case that's been pinged to Checked. This is used if the case is
        mistakenly pinged.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = CheckedClaim.from_ping_thread_id(self.bot.connection, interaction.channel_id)
        ping = Ping.from_thread_id(self.bot.connection, interaction.channel_id)

        if case is None:
            await interaction.response.send_message(content="Error!", ephemeral=True)
            return

        if case.lead.discord_id != interaction.user.id:
            await interaction.response.send_message(content="You cannot press this button.", ephemeral=True)
            return

        await interaction.channel.remove_user(interaction.user)  # Remove lead

        try:
            user = await interaction.channel.fetch_member(case.tech.discord_id)
            await interaction.channel.remove_user(user)  # Remove tech
        except:
            pass

        # Change Log file
        case.change_status(self.bot.connection, Status.CHECKED)
        ping.remove_from_database(self.bot.connection)

        await interaction.response.defer(thinking=False)  # Acknowledge button press
