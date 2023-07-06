import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.announcement import Announcement

if TYPE_CHECKING:
    from bot.bot import Bot


class EditAnnouncementModal(ui.Modal, title='Announcement Update Form'):
    def __init__(self, bot: "Bot", announcement: Announcement):
        super().__init__()
        self.bot = bot
        self.announcement = announcement

        self.title = ui.TextInput(label='Title',style=discord.TextStyle.short, default=announcement.info["title"])
        self.add_item(self.title)
        self.description = ui.TextInput(label='Description',style=discord.TextStyle.short, required=False, default=announcement.info["description"])
        self.add_item(self.description)


    async def on_submit(self, interaction: discord.Interaction) -> None:
        new_title = str(self.title)
        new_description = str(self.description)

        self.bot.announcement_manager.remove_announcement(self.announcement)

        self.announcement.info["title"] = new_title
        self.announcement.info["description"] = new_description

        self.bot.announcement_manager.add_announcement(self.announcement)

        # Edit announcement message
        announcement_message = await interaction.channel.fetch_message(self.announcement.announcement_message_id)
        await announcement_message.edit(embed=self.announcement.to_announcement_embed())
        
        # Edit case message
        case_channel = await interaction.guild.fetch_channel(self.bot.cases_channel)
        case_message = await case_channel.fetch_message(self.announcement.info["case_message_id"])
        await case_message.edit(embed=self.announcement.to_case_embed(announcement_message.jump_url))

        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True)