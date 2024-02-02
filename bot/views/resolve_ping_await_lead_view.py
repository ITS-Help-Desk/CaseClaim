import discord
import discord.ui as ui

from bot.models.checked_claim import CheckedClaim
from bot.models.feedback import Feedback

from bot.status import Status

# Avoid circular import
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot

class ResolvePingAwaitLeadView(ui.View):
    def __init__(self, bot: "Bot"):
        """
        Creates a temporary view with buttons that lead to all of a
        leads resolve options.

        Args:
            bot (Bot): A reference to the original bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Acknowledged", style=discord.ButtonStyle.)
    async def button_acknowledge_feedback(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

