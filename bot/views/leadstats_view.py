import datetime
import discord
import discord.ui as ui

from bot.helpers.leaderboard_helpers import LeadstatsResults
from bot.helpers.other import month_number_to_name

from bot.models.checked_claim import CheckedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from ..forms.leadstats_form import LeadstatsForm

if TYPE_CHECKING:
    from ..bot import Bot


class LeadStatsView(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a leaderboard view for the /leadstats command
        to allow users to refresh it.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Month", style=discord.ButtonStyle.primary, custom_id="checkrefreshmonth")
    async def show_month(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server for the month.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False)  # Acknowledge button press

        result = LeadstatsResults(CheckedClaim.search(self.bot.connection), interaction.created_at)
        new_embed, file = result.create_embed(self.bot, interaction, True)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed, attachments=[file])

    @ui.button(label="Semester", style=discord.ButtonStyle.primary, custom_id="checkrefreshsemester")
    async def show_semester(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refreshes the global ranks of case claims for the whole server for the semester.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        await interaction.response.defer(thinking=False)  # Acknowledge button press

        result = LeadstatsResults(CheckedClaim.search(self.bot.connection), interaction.created_at)
        new_embed, file = result.create_embed(self.bot, interaction, month=False)

        message = interaction.message
        if message is not None:
            await message.edit(embed=new_embed, attachments=[file])

    @ui.button(label="See past", style=discord.ButtonStyle.secondary, custom_id="seepast")
    async def see_past(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows past leadstats leaderboards. This command will open a modal prompting the user to input a date.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        form = LeadstatsForm(self.bot)
        await interaction.response.send_modal(form)

