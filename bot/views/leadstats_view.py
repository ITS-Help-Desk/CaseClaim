import discord
import discord.ui as ui

from bot.helpers.leaderboard_helpers import LeadstatsResults
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

    @ui.button(label="See Past", style=discord.ButtonStyle.secondary, custom_id="seepast")
    async def see_past(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Shows past leadstats leaderboards. This command will open a modal prompting the user to input a date.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        claims = CheckedClaim.search(bot.connection)
        results = LeadstatsResults(claims, interaction.created_at)
        data_stream = results.convert_to_plot(bot.connection, month, f"ITS Lead CC Statistics ({f'{month_number_to_name(interaction.created_at.month)}' if month else 'Semester'})")
        chart = discord.File(data_stream, filename="chart.png")

        embed = discord.Embed(title="ITS Case Check Leaderboard")
        embed.colour = bot.embed_color

        embed.set_image(url="attachment://chart.png")

        embed.set_footer(text="Last Updated")
        embed.timestamp = datetime.datetime.now()

        return embed, chart

