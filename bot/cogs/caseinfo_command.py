from discord import app_commands
from discord.ext import commands
import discord
import time
from bot import paginator
import traceback

from bot.helpers.other import create_paginator_embeds

from bot.models.active_claim import ActiveClaim
from bot.models.completed_claim import CompletedClaim
from bot.models.checked_claim import CheckedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class CaseInfoCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /caseinfo command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Shows a list of all users a case has been worked on by")
    @app_commands.describe(case_num="Case #")
    async def caseinfo(self, interaction: discord.Interaction, case_num: str) -> None:
        """Shows a list of all users a case has worked on by.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from
            case_num (str): The case number in Salesforce (e.g. "00960979")
        """
        await interaction.response.defer(ephemeral=True)  # Wait in case process takes a long time

        # Collect rows with this case
        rows: list[ActiveClaim | CompletedClaim | CheckedClaim] = []
        for result in ActiveClaim.get_all_with_case_num(self.bot.connection, case_num):
            rows.append(result)

        for result in CompletedClaim.get_all_with_case_num(self.bot.connection, case_num):
            rows.append(result)

        for result in CheckedClaim.get_all_with_case_num(self.bot.connection, case_num):
            rows.append(result)

        # Sort data, create written descriptions
        rows.sort(key=lambda x: x.claim_time, reverse=True)
        row_str = self.data_to_rowstr(rows, interaction.user)

        # Create paginator embed
        title = f'Cases History of {case_num} ({len(rows)})'
        if len(row_str) <= 10:
            embed = discord.Embed(title=title)
            embed.colour = self.bot.embed_color
            embed.description = '\n'.join(row for row in row_str)

            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            embeds = create_paginator_embeds(row_str, title, self.bot.embed_color)
            await paginator.Simple(ephemeral=True).start(interaction, embeds)

    def data_to_rowstr(self, rows: list[ActiveClaim | CompletedClaim | CheckedClaim], user: discord.Member) -> list[str]:
        """Converts the raw data into a list of strings
        that can be used in the embed description.

        Args:
            rows (list[ActiveClaim | CompletedClaim | CheckedClaim]): The list of raw strings from the database.

        Returns:
            list[str]: The list of descriptions that can be directly used in an embed.
        """
        row_str = []
        for row in rows:
            s = ''
            if type(row) == ActiveClaim:
                s += "**[ACTIVE]**"

            # Convert timestamp to UNIX
            t = int(time.mktime(row.claim_time.timetuple()))
            s += f'<t:{t}:f> - <@!{row.tech.discord_id}>'

            if self.bot.check_if_lead(user) and type(row) == CheckedClaim:
                s += f' {row.status}'
                s += f' by <@!{row.lead.discord_id}>'

            row_str.append(s)

        return row_str

    @caseinfo.error
    async def caseinfo_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)

        msg = f"Error with **/caseinfo** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
