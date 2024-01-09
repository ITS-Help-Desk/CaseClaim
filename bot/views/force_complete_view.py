import discord
import discord.ui as ui
from datetime import datetime

from bot.views.check_view import CheckView

from bot.models.active_claim import ActiveClaim
from bot.models.completed_claim import CompletedClaim

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class ForceCompleteView(ui.View):
    def __init__(self, bot: "Bot"):
        """Allows a lead to confirm if they would like to force complete a case.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Yes", style=discord.ButtonStyle.primary, custom_id='forcecompleteyes')
    async def button_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Once "Yes" is pressed, the case will be removed from the ActiveClaims database
        and a lead check message will be sent to lead check channel.
        The case message and ephemeral message are also deleted.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case_num = interaction.message.content.split(" ")[0].replace("*", "")
        case = ActiveClaim.from_case_num(self.bot.connection, case_num)

        if case is None:
            # Case not found
            await interaction.response.send_message("Error, please try again.", ephemeral=True, delete_after=300)

            raise AttributeError(f"Case is none (message ID: {interaction.message.id})")

        if self.bot.check_if_lead(interaction.user):
            await interaction.response.defer(thinking=False)  # Acknowledge button press

            # Delete message from channel
            channel = await self.bot.fetch_channel(interaction.channel_id)
            msg = await channel.fetch_message(case.claim_message_id)
            await msg.delete()

            user = await channel.guild.fetch_member(case.tech.discord_id)

            # Complete the claim as normal
            case.remove_from_database(self.bot.connection)

            # Send a message in the claims channel and add the lead view to it.
            channel = interaction.user.guild.get_channel(self.bot.claims_channel)  # claims channel
            lead_embed = discord.Embed(description=f"Has been marked as complete by <@{case.tech.discord_id}>",
                                       colour=self.bot.embed_color,
                                       timestamp=datetime.now())
            lead_embed.set_author(name=f"{case.case_num}", icon_url=f'{user.display_avatar}')
            lead_embed.set_footer(text="Completed")
            msg = await channel.send(embed=lead_embed, view=CheckView(self.bot))

            # Add case to CompletedClaims
            completed_claim = CompletedClaim(msg.id, case.case_num, case.tech, case.claim_time, datetime.now())
            completed_claim.add_to_database(self.bot.connection)

            # Delete ephemeral message
            await interaction.delete_original_response()
