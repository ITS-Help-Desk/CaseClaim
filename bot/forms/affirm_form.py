import discord
import discord.ui as ui
from datetime import datetime

from bot.models.checked_claim import CheckedClaim
from bot.models.feedback import Feedback

# from bot.views.resolve_ping_await_lead_view import ResolvePingAwaitLeadView
from bot.views.resolve_ping_view import ResolvePingView

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class AffirmForm(ui.Modal, title='Tech Assessment'):
    def __init__(self, bot: "Bot", case: CheckedClaim):
        """Creates an assessment form for a tech to provide
        how they resolved a ping, and allows a lead to review
        this assessment with a separate ResolvePingView.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
            case (Claim): The case object.
        """
        super().__init__()
        self.bot = bot
        self.case = case

    # Change max length to 1024 to align with embed char limit.
    assessment = ui.TextInput(label='Assessment (Optional)', style=discord.TextStyle.paragraph, required=False, max_length=1024)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates a private thread with the tech and sends a message
        with the feedback from the lead.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """

        # Remove tech after they submit an acknowledgement
        await interaction.channel.remove_user(interaction.user)
        
        # Try to remove the Affirm button and update it to be the lead resolve view
        try:
            ping = Feedback.from_thread_id(self.bot.connection, interaction.channel_id)
            ch = await self.bot.fetch_channel(interaction.channel_id)
            msg = await ch.fetch_message(ping.message_id)
            original_embed = msg.embeds[0]
            original_embed.insert_field_at(index=2,name="Feedback", value=str(self.assessment), inline=False)
            await msg.edit(view=ResolvePingView(self.bot), embed=original_embed)
        except Exception as e:
            print(e)

        await interaction.channel.send(content=f"<@!{self.case.lead.discord_id}> Tech has responded.", delete_after=10)
