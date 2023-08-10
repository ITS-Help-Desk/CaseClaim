from discord import app_commands
from discord.ext import commands
import discord
import csv
import os
import traceback

from datetime import datetime

from bot.models.active_claim import ActiveClaim
from bot.models.announcement import Announcement
from bot.models.checked_claim import CheckedClaim
from bot.models.completed_claim import CompletedClaim
from bot.models.outage import Outage
from bot.models.ping import Ping
from bot.models.user import User

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class ExportCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /export command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Export all MySQL data to CSV")
    @app_commands.default_permissions(mute_members=True)
    async def export(self, interaction: discord.Interaction) -> None:
        """Creates CSV versions of all MySQL tables in the database.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
        """
        if self.bot.check_if_lead(interaction.user):
            ac = ActiveClaim.get_all(self.bot.connection)
            an = Announcement.get_all(self.bot.connection)
            ch = CheckedClaim.get_all(self.bot.connection)
            co = CompletedClaim.get_all(self.bot.connection)
            ou = Outage.get_all(self.bot.connection)
            pi = Ping.get_all(self.bot.connection)
            us = User.get_all(self.bot.connection)

            file_names = ["activeclaims", "announcements", "checkedclaims", "completedclaims", "outages", "pings", "users"]
            data = [ac, an, ch, co, ou, pi, us]

            root = f"export/{datetime.now().strftime('%Y-%m-%d %H-%M-%S')}/"

            # Create root folder if it doesn't already exist
            try:
                os.mkdir('export')
            except FileExistsError:
                pass

            # Create timestamped folder
            os.mkdir(root)

            # Add data
            for i, file in enumerate(file_names):
                with open(f"{root}{file}.csv", 'w', newline='', encoding='utf-8') as f:
                    csv_writer = csv.writer(f)

                    for item in data[i]:
                        csv_writer.writerow(item.export())

            await interaction.response.send_message(f"Export finished! Data can be found in **{root}**", ephemeral=True)
        else:
            # Return error message if user is not Lead
            msg = f"<@{interaction.user.id}>, you do not have permission to use this command!"
            await interaction.response.send_message(content=msg, ephemeral=True)

    @export.error
    async def export_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/export** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
