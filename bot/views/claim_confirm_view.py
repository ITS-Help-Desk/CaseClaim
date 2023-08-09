import discord
import discord.ui as ui
from datetime import datetime

from bot.views.claim_view import ClaimView

from bot.models.active_claim import ActiveClaim
from bot.models.user import User
from bot.models.announcement import Announcement

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class ClaimConfirmView(ui.View):
    def __init__(self, bot: "Bot"):
        """

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Yes", style=discord.ButtonStyle.success, custom_id='yes')
    async def button_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        """

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        case_num = interaction.message.content.split(" ")[0]

        # Check to see if the case claimed has already been claimed and is in progress.
        case = ActiveClaim.from_case_num(self.bot.connection, case_num)
        if case is not None:
            msg = f"**{case_num}** has already been claimed!"
            await interaction.response.send_message(content=msg, ephemeral=True, delete_after=300)
            return

        # User has claimed the case successfully, create the embed and techview.
        message_embed = discord.Embed(
            description=f"Is being worked on by <@{interaction.user.id}>",
            colour=self.bot.embed_color,
            timestamp=datetime.now()
        )
        message_embed.set_author(name=f"{case_num}", icon_url=f'{interaction.user.display_avatar}')
        message_embed.set_footer(text="Claimed")

        message_view = ClaimView(self.bot)

        # Send message
        await interaction.response.send_message(embed=message_embed, view=message_view)
        response = await interaction.original_response()

        # Now that message has been sent, update the active cases
        # with the new message id
        tech = User.from_id(self.bot.connection, interaction.user.id)

        case = ActiveClaim(response.id, case_num, tech, datetime.now())
        case.add_to_database(self.bot.connection)

        await interaction.message.delete()

        self.bot.resend_outages = True
        await Announcement.resend(self.bot)


    @ui.button(label="No", style=discord.ButtonStyle.danger, custom_id='no')
    async def button_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        """

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        #await interaction.edit_original_response(view=None)
        await interaction.delete_original_response()
        #await interaction.message.edit(delete_after=0)
