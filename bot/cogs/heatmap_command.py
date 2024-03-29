from discord import app_commands
from discord.ext import commands
import discord
import io
import numpy as np
import matplotlib.pyplot as plt
from typing import Optional

import traceback

from bot.models.checked_claim import CheckedClaim
# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class HeatmapCommand(commands.Cog):
    def __init__(self, bot: "Bot") -> None:
        """Creates the /heatmap command using a cog.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        self.bot = bot

    @app_commands.command(description="Generate a heatmap of cases logged.")
    @app_commands.describe(year="The year of cases.")
    @app_commands.describe(month="(Optional) The month of cases.")
    @app_commands.default_permissions(mute_members=True)
    async def heatmap(self, interaction: discord.Interaction, year: int, month: Optional[int]):
        # Check if user is a lead
        if not self.bot.check_if_lead(interaction.user):
            # Return error message if user is not Lead
            msg = f"<@{interaction.user.id}>, you do not have permission!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=180)
            return

        await interaction.response.defer(ephemeral=True)  # Wait in case process takes a long time
        if month is None:
            cases = CheckedClaim.get_all_from_year(self.bot.connection, year)
            title = f"HD Heatmap ({year})"
        else:
            cases = CheckedClaim.get_all_from_month(self.bot.connection, month, year)
            title = f"HD Heatmap ({month}/{year})"

        data = self.generate(cases, title)

        chart = discord.File(data, filename="chart.png")

        await interaction.followup.send(content="Heatmap created successfully", file=chart)

    def generate(self, cases: list[CheckedClaim], title: str) -> io.BytesIO:
        """Converts a list of cases into a heatmap to show which leads have
        checked cases from which techs.

        Args:
            cases (list[CheckedClaim]): The list of CheckedClaims that will be combed through
            title (str): The title of the matplotlib graph

        Returns:
            BytesIO - A byte stream that can be attached as a Discord file that will show the heatmap
        """
        data_stream = io.BytesIO()

        plt.rcParams.update({'font.size': 7})

        all_data: dict[int, dict[int, int]] = {}  # dict of dicts (parentkey = lead, childkey = tech)
        leads: dict[int, str] = {}
        techs: dict[int, str] = {}

        total_cases: dict[int, int] = {}
        # Collect data
        for case in cases:
            lead = case.lead.discord_id
            tech = case.tech.discord_id

            total_cases.setdefault(tech, 0)
            total_cases[tech] += 1

            leads[lead] = case.lead.abb_name
            techs[tech] = case.tech.abb_name

            all_data.setdefault(lead, {})
            all_data[lead].setdefault(tech, 0)

            all_data[lead][tech] += 1

        # Initialize all data
        for key in list(all_data.keys()):
            for tech in list(techs.keys()):
                all_data[key].setdefault(tech, 0)

        # Remove techs with less than 20 cases
        for tech in list(total_cases.keys()):
            if total_cases[tech] < 40:
                for key in list(all_data.keys()):
                    all_data[key].pop(tech)
                techs.pop(tech)

        # Create 2D matrix of values
        sorted_keys = sorted(techs, key=techs.get)
        matrix = []
        for lead_key in list(all_data.keys()):
            temp = []
            for tech_key in sorted_keys:
                temp.append(all_data[lead_key][tech_key])
            matrix.append(temp)

        # Labels
        xlabs = [techs[key] for key in sorted_keys]
        ylabs = list(leads.values())

        # Heat map
        fig, ax = plt.subplots()
        ax.imshow(matrix)

        plt.colorbar(ax.get_children()[0])

        # Add the labels
        ax.set_title(title)
        ax.set_xticks(np.arange(len(xlabs)), labels=xlabs, rotation=90)
        ax.set_yticks(np.arange(len(ylabs)), labels=ylabs)
        plt.xlabel("Techs")
        plt.ylabel("Leads")

        plt.savefig(data_stream, format='png', bbox_inches="tight", dpi=800)
        plt.close()
        data_stream.seek(0)

        plt.rcParams.update({'font.size': 11})

        return data_stream

    @heatmap.error
    async def heatmap_error(self, ctx: discord.Interaction, error):
        full_error = traceback.format_exc()

        ch = await self.bot.fetch_channel(self.bot.error_channel)
        msg = f"Error with **/heatmap** ran by <@!{ctx.user.id}>.\n```{full_error}```"
        if len(msg) > 1993:
            msg = msg[:1993] + "...```"
        await ch.send(msg)
