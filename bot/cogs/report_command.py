import datetime

from discord import app_commands
from discord.ext import commands
import discord
import csv
from bot.helpers.other import month_string_to_number, month_number_to_name
import traceback

from bot.models.checked_claim import CheckedClaim
from bot.models.feedback import Feedback
from bot.models.user import User
from bot.status import Status

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class ReportCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /report command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Generate a report of cases logged.")
    @app_commands.describe(user="The user the report will be generated for.")
    @app_commands.describe(month="The month for the report (e.g. \"march\").")
    @app_commands.describe(year="The year for the report (e.g. 2023).")
    @app_commands.choices(status=[
        app_commands.Choice(name="Kudos", value="kudos"),
        app_commands.Choice(name="Pinged", value="pinged")
    ])
    @app_commands.default_permissions(mute_members=True)
    async def report(self, interaction: discord.Interaction, user: discord.Member = None, month: str = None, year: int = None, status: app_commands.Choice[str] = None):
        """Creates a report of all cases, optionally within a certain month and optionally
        for one specific user.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            user (discord.Member, optional): The user that the report will correspond to. Defaults to None.
            month (str, optional): The month that all the cases comes from. Defaults to None.
            status (app_command.Choice[str]): The status of cases that will be presented in the report
        """
        # Check if user is a lead
        if not self.bot.check_if_lead(interaction.user):
            # Return error message if user is not Lead
            msg = f"<@{interaction.user.id}>, you do not have permission to pull this report!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)

            return

        if interaction.channel_id != self.bot.log_channel:
            # Return an error if used in the wrong channel
            msg = f"You can only use this command in the <#{self.bot.log_channel}> channel."
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)
            return

        # Ensure user inputted a valid month
        if month is not None:
            try:
                m = int(month_string_to_number(month))
            except ValueError:
                await interaction.response.send_message(content="Invalid month! Please use 3 letter abbreviations (e.g. \"jan\", \"feb\",...)", ephemeral=True, delete_after=180)
                return

        # Automatically setup the year for previous months
        now = datetime.datetime.now()
        if year is None and int(month_string_to_number(month)) <= now.month:
            year = datetime.datetime.now().year

        await interaction.response.defer()  # Wait in case process takes a long time

        description = "Here's your report of cases"

        if month is not None:
            month = int(month_string_to_number(month))
            description += f" in **{month_number_to_name(month)}"
            if year is not None:
                description += f"/{year}"
            description += "**"
        if user is not None:
            user = User.from_id(self.bot.connection, user.id)
            description += f" from user **{user.full_name}**"

        if status is not None:
            status = Status.from_str(status.value)
            description += f" with status **{status}**"

        results = CheckedClaim.search(self.bot.connection, user, year, month, status)
        row_str = self.data_to_rowstr(results)

        with open('temp.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in row_str:
                writer.writerow(row)

        report = discord.File('temp.csv')

        await interaction.followup.send(content=f"{description}.", file=report)


    def data_to_rowstr(self, data: list[CheckedClaim]) -> list[list[str]]:
        """Converts the raw data into a list of strings
        that can be used in the embed description.

        Args:
            data (list[CheckedClaim]): The list of raw strings from the database.

        Returns:
            list[list[str]]: The list of descriptions that can be directly used to be put in the temp.csv file.
        """
        new_list = []
        for claim in data:
            t = claim.claim_time.strftime("%b %d %Y %#I:%M %p")  # Format time (replace '#' with '-' for Unix)
            row = [str(t), str(claim.case_num), str(claim.tech.full_name), str(claim.lead.full_name), str(claim.status)]

            # Add ping data
            if claim.ping_thread_id is not None:
                p = Feedback.from_thread_id(self.bot.connection, claim.ping_thread_id)
                row.append(p.severity)
                row.append(p.description)

            new_list.append(row)

        return new_list

    @report.error
    async def report_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        print(full_error)

        msg = f"Error with **/report** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
