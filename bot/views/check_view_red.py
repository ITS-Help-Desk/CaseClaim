import discord
import discord.ui as ui

from bot.status import Status
from datetime import datetime

from bot.models.completed_claim import CompletedClaim
from bot.models.checked_claim import CheckedClaim
from bot.models.user import User

from bot.forms.ping_form import PingForm

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class CheckViewRed(ui.View):
    def __init__(self, bot: "Bot"):
        """Creates a lead view in the lead case claim channel for submitting
        feedback on a completed case submitted by a tech.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Check", style=discord.ButtonStyle.secondary, custom_id="check")
    async def button_check(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a lead, it logs this case as Checked.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = CompletedClaim.from_id(self.bot.connection, interaction.message.id)
        case.remove_from_database(self.bot.connection)

        new_case = CheckedClaim(case.checker_message_id, case.case_num, case.tech,
                                User.from_id(self.bot.connection, interaction.user.id), case.claim_time,
                                case.complete_time, datetime.now(), Status.CHECKED, None)
        new_case.add_to_database(self.bot.connection)

        await interaction.message.delete()

    @ui.button(label="Ping", style=discord.ButtonStyle.secondary, custom_id="ping")
    async def button_ping(self, interaction: discord.Interaction, button: discord.ui.Button):
        """When pressed by a lead, it brings up a feedback modal
        for a lead to ping a case.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case = CompletedClaim.from_id(self.bot.connection, interaction.message.id)

        # Prompt with Modal, record the response, create a private thread, then delete
        form = PingForm(self.bot, case)
        await interaction.response.send_modal(form)
