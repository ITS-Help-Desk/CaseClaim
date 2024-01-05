from discord import app_commands
from discord.ext import commands
import discord
import csv
import traceback
from typing import Any, Optional

from bot.models.checked_claim import CheckedClaim
from bot.status import Status

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class EvaldataCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /evaldata command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Generate a spreadsheet of cases metrics for everyone.")
    @app_commands.describe(year="The year of cases.")
    @app_commands.describe(month="(Optional) The month of cases.")
    @app_commands.default_permissions(mute_members=True)
    async def evaldata(self, interaction: discord.Interaction, month: Optional[int], year: int):
        """Creates two spreadsheets to represent data for all techs and leads
        collected from the bot over a year

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
            year (int): The year for which the data will be representing
        """
        # Check if user is a lead
        if not self.bot.check_if_lead(interaction.user):
            # Return error message if user is not Lead
            msg = f"<@{interaction.user.id}>, you do not have permission to pull this report!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)
            return

        '''if interaction.channel_id != self.bot.log_channel:
            # Return an error if used in the wrong channel
            msg = f"You can only use this command in the <#{self.bot.log_channel}> channel."
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)
            return'''

        await interaction.response.defer(ephemeral=True)  # Wait in case process takes a long time

        data = self.get_data(month, year)

        # Create techs csv
        with open('techs.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in data[0]:
               writer.writerow(row)

        # Create leads csv
        with open('leads.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            for row in data[1]:
               writer.writerow(row)

        tech_data = discord.File('techs.csv')
        lead_data = discord.File('leads.csv')

        await interaction.followup.send(content=f"Success", files=[tech_data, lead_data])

    def get_data(self, month: Optional[int], year: int) -> tuple[list[Any], list[Any]]:
        """Collects all the data from every tech and every lead
        and compiles it into data that can easily be written to a
        spreadsheet.

        Args:
            year (int): The year for which the data will be collected from

        Returns:
            tuple[list[Any], list[Any]] - A tuple containing two lists: tech and lead and are ready
            to be converted to a spreadsheet using writerow
        """
        if month is None:
            all_cases = CheckedClaim.get_all_from_year(self.bot.connection, year)
        else:
            all_cases = CheckedClaim.get_all_from_month(self.bot.connection, month, year)

        # Tech data
        total_checked_cases = {}
        total_done_cases = {}
        total_pinged_cases = {}
        total_resolved_cases = {}
        total_kudos_cases = {}

        average_completion_time = {}
        average_check_time = {}

        # Lead data
        total_checked_claims = {}
        total_done_claims = {}
        total_pinged_claims = {}
        total_resolved_claims = {}
        total_kudos_claims = {}

        total_hd_cases = 0
        hd_case_percent = {}
        hd_claim_percent = {}

        techs = {}
        leads = {}
        for case in all_cases:
            total_hd_cases += 1
            techs[case.tech.full_name] = case.tech.discord_id
            leads[case.lead.full_name] = case.lead.discord_id
            # Initialize tech data
            for category in [total_checked_cases, total_done_cases, total_pinged_cases, total_resolved_cases, total_kudos_cases, hd_case_percent, average_completion_time]:
                category.setdefault(case.tech.discord_id, 0)
            # Initialize lead data
            for category in [total_checked_claims, total_done_claims, total_pinged_claims, total_resolved_claims, total_kudos_claims, hd_claim_percent, average_check_time]:
                category.setdefault(case.lead.discord_id, 0)

            # Update tech data
            if case.status == str(Status.CHECKED):
                total_checked_cases[case.tech.discord_id] += 1
                total_checked_claims[case.lead.discord_id] += 1
            elif case.status == str(Status.DONE):
                total_done_cases[case.tech.discord_id] += 1
                total_done_claims[case.lead.discord_id] += 1
            elif case.status == str(Status.PINGED):
                total_pinged_cases[case.tech.discord_id] += 1
                total_pinged_claims[case.lead.discord_id] += 1
            elif case.status == str(Status.RESOLVED):
                total_resolved_cases[case.tech.discord_id] += 1
                total_resolved_claims[case.lead.discord_id] += 1
            elif case.status == str(Status.KUDOS):
                total_kudos_cases[case.tech.discord_id] += 1
                total_kudos_claims[case.lead.discord_id] += 1

            # Add complete/check time differences
            complete_diff = case.complete_time - case.claim_time
            complete_diff_seconds = complete_diff.seconds + (complete_diff.days * 86400)

            check_diff = case.check_time - case.complete_time
            check_diff_seconds = check_diff.seconds + (check_diff.days * 86400)

            average_completion_time[case.tech.discord_id] += complete_diff_seconds
            average_check_time[case.lead.discord_id] += check_diff_seconds

        # Calculate averages
        for key in list(average_completion_time.keys()):
            average_completion_time[key] /= (total_checked_cases[key] + total_done_cases[key] + total_pinged_cases[key] + total_resolved_cases[key] + total_kudos_cases[key])
        for key in list(average_check_time.keys()):
            average_check_time[key] /= (total_checked_claims[key] + total_done_claims[key] + total_pinged_claims[key] + total_resolved_claims[key] + total_kudos_claims[key])

        # Calculate percentages
        for key in list(hd_case_percent):
            hd_case_percent[key] = (total_checked_cases[key] + total_done_cases[key] + total_pinged_cases[key] + total_resolved_cases[key] + total_kudos_cases[key]) / total_hd_cases
        for key in list(hd_claim_percent):
            hd_claim_percent[key] = (total_checked_claims[key] + total_done_claims[key] + total_pinged_claims[key] + total_resolved_claims[key] + total_kudos_claims[key]) / total_hd_cases

        # Create tech rows
        tech_rows = [["Tech", "Total Cases", "Total Checked Cases", "Total Done Cases", "Total Pinged Cases", "Total Resolved Cases", "Total Kudos Cases", "Percent Checked", "Percent Done", "Percent Pinged", "Percent Resolved", "Percent Kudos", "Percent Resolved after Pinged", "Average Case Completion Time (Seconds)", "HD Case Percent"]]

        for key in dict(sorted(techs.items())):
            user_id = techs[key]
            total = total_checked_cases[user_id] + total_done_cases[user_id] + total_pinged_cases[user_id] + total_resolved_cases[user_id] + total_kudos_cases[user_id]
            if key in list(leads.keys()) and total < 100:
                continue

            row = [key,
                   total,
                   total_checked_cases[user_id],
                   total_done_cases[user_id],
                   total_pinged_cases[user_id],
                   total_resolved_cases[user_id],
                   total_kudos_cases[user_id],
                   round(total_checked_cases[user_id] / total, 4),
                   round(total_done_cases[user_id] / total, 4),
                   round(total_pinged_cases[user_id] / total, 4),
                   round(total_resolved_cases[user_id] / total, 4),
                   round(total_kudos_cases[user_id] / total, 4),
                   round(total_resolved_cases[user_id] / (total_resolved_cases[user_id] + total_pinged_cases[user_id]), 4) if total_resolved_cases[user_id] + total_pinged_cases[user_id] > 0 else 0,
                   average_completion_time[user_id],
                   hd_case_percent[user_id]]
            tech_rows.append(row)

        # Create lead rows
        lead_rows = [["Lead", "Total Cases", "Total Checked Claims", "Total Done Claims", "Total Pinged Claims", "Total Resolved Claims", "Total Kudos Claims", "Percent Checked", "Percent Done", "Percent Pinged", "Percent Resolved", "Percent Kudos", "Percent Resolved after Pinged", "Average Claim Check Time (Seconds)", "HD Claim Percent"]]
        for key in dict(sorted(leads.items())):
            user_id = leads[key]
            total = total_checked_claims[user_id] + total_done_claims[user_id] + total_pinged_claims[user_id] + total_resolved_claims[user_id] + total_kudos_claims[user_id]
            row = [key,
                   total,
                   total_checked_claims[user_id],
                   total_done_claims[user_id],
                   total_pinged_claims[user_id],
                   total_resolved_claims[user_id],
                   total_kudos_claims[user_id],
                   round(total_checked_claims[user_id] / total, 4),
                   round(total_done_claims[user_id] / total, 4),
                   round(total_pinged_claims[user_id] / total, 4),
                   round(total_resolved_claims[user_id] / total, 4),
                   round(total_kudos_claims[user_id] / total, 4),
                   round(total_resolved_claims[user_id] / (total_resolved_claims[user_id] + total_pinged_claims[user_id]), 4) if total_resolved_claims[user_id] + total_pinged_claims[user_id] > 0 else 0,
                   average_check_time[user_id],
                   hd_claim_percent[user_id]]
            lead_rows.append(row)

        return tech_rows, lead_rows

    @evaldata.error
    async def evaldata_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/evaldata** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
