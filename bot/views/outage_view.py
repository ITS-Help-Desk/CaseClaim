import discord
import discord.ui as ui

from bot.forms.edit_outage_form import EditOutageForm
from bot.models.outage import Outage

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..bot import Bot


class OutageView(ui.View):
    def __init__(self, bot: "Bot"):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="Update", style=discord.ButtonStyle.primary, custom_id="update")
    async def button_update(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a PA to update the information for an outage. It prompts a modal for the PA
        to fill in new information for each field.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        if self.bot.check_if_pa(interaction.user):
            outage = Outage.from_message_id(self.bot.connection, interaction.message.id)

            edit_modal = EditOutageForm(self.bot, outage)
            await interaction.response.send_modal(edit_modal)

    @ui.button(label="Close", style=discord.ButtonStyle.secondary, custom_id="close")
    async def button_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Allows a PA to close an outage and deletes the cases channel message.

        Args:
            interaction (discord.Interaction): The interaction this button press originated from.
            button (discord.ui.Button): Unused argument that's required to be passed in.
        """
        if self.bot.check_if_pa(interaction.user):
            outage = Outage.from_message_id(self.bot.connection, interaction.message.id)
            outage.deactivate(self.bot.connection)

            announcement_message: discord.Message = await interaction.channel.fetch_message(outage.message_id)
            announcement_embed = announcement_message.embeds[0]
            announcement_embed.colour = self.bot.embed_color
            announcement_embed.add_field(name="Marked as Resolved",
                                         value=f"<t:{int(interaction.created_at.timestamp())}:f> by **{interaction.user.display_name}**",
                                         inline=True)

            await announcement_message.edit(content="", embed=announcement_embed, view=None)

            # Delete case message
            case_channel = await self.bot.fetch_channel(self.bot.cases_channel)
            case_message = await case_channel.fetch_message(outage.case_message_id)
            await case_message.delete()

            await interaction.response.send_message("👍", ephemeral=True, delete_after=0)