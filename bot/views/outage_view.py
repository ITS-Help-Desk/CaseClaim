import discord
import discord.ui as ui

from bot.modals.edit_outage_modal import EditOutageModal

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
        if self.bot.check_if_pa(interaction.user):
            outage = self.bot.announcement_manager.get_announcement(interaction.message.id)

            edit_modal = EditOutageModal(self.bot, outage)
            await interaction.response.send_modal(edit_modal)
    

    @ui.button(label="Close", style=discord.ButtonStyle.secondary, custom_id="close")
    async def button_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.bot.check_if_pa(interaction.user):
            outage = self.bot.announcement_manager.get_announcement(interaction.message.id)
            self.bot.announcement_manager.remove_announcement(outage)

            announcement_message = await interaction.channel.fetch_message(outage.announcement_message_id)
            outage.info["resolution_time"] = ""
            announcement_embed = outage.to_announcement_embed()
            announcement_embed.colour = self.bot.embed_color
            announcement_embed.add_field(name="Marked as Resolved", value=f"<t:{int(interaction.created_at.timestamp())}:f> by **{interaction.user.display_name}**", inline=True)

            await announcement_message.edit(embed=announcement_embed, view=None)

            # Delete case message
            case_channel = await self.bot.fetch_channel(self.bot.cases_channel)
            case_message = await case_channel.fetch_message(outage.info["case_message_id"])
            await case_message.delete()

            await interaction.response.send_message("👍", ephemeral=True)