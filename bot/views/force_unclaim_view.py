import discord
import discord.ui as ui

from bot.models.active_claim import ActiveClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class ForceUnclaimView(ui.View):
    def __init__(self, bot: "Bot"):
        """Allows a lead to force unclaim a case.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Yes", style=discord.ButtonStyle.primary, custom_id='forceunclaimyes')
    async def button_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Once "Yes" is pressed, the case will be removed from the ActiveClaims database.
        The case message and ephemeral message are also deleted.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case_num = interaction.message.content.split(" ")[0].replace("*", "")
        case = ActiveClaim.from_case_num(self.bot.connection, case_num)

        if case is None:
            await interaction.response.send_message("Error, please try again.", ephemeral=True, delete_after=300)

            raise AttributeError(f"Case is none (message ID: {interaction.message.id})")

        if self.bot.check_if_lead(interaction.user):
            await interaction.response.defer(thinking=False)  # Acknowledge button press

            # Delete message from channel
            channel = await self.bot.fetch_channel(interaction.channel_id)
            msg = await channel.fetch_message(case.claim_message_id)
            await msg.delete()

            # Delete the case from database
            case.remove_from_database(self.bot.connection)

            # Delete ephemeral message
            await interaction.delete_original_response()
