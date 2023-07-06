import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING
from bot.announcement import Announcement

from bot.views.announcement_view import AnnouncementView

if TYPE_CHECKING:
    from bot.bot import Bot


class AnnouncementModal(ui.Modal, title='Announcement Form'):
    def __init__(self, bot: "Bot"):
        super().__init__()
        self.bot = bot

    a_title = ui.TextInput(label='Title',style=discord.TextStyle.short)
    description = ui.TextInput(label='Description', style=discord.TextStyle.paragraph)
    days = ui.TextInput(label='Days Shown (1-14) (Optional, Default=4)', style=discord.TextStyle.paragraph, required=False)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Create announcement for AnnouncementManager
        a_title = str(self.a_title)
        description = str(self.description)
        days = 4 if len(str(self.days)) == 0 else int(str(self.days))

        info = {
            "title": a_title,
            "description": description,
            "days": days
        }

        announcement = Announcement("announcement", info)

        announcement_embed = announcement.to_announcement_embed()

        # Send announcement message
        announcement_channel = await self.bot.fetch_channel(self.bot.announcement_channel)    
        announcement_message = await announcement_channel.send(content="@everyone", embed=announcement_embed, view=AnnouncementView(self.bot))

        announcement.announcement_message_id = announcement_message.id


        case_embed = announcement.to_case_embed(announcement_message.jump_url)

        # Send case message
        case_channel = await self.bot.fetch_channel(self.bot.cases_channel)    
        case_message = await case_channel.send(embed=case_embed, silent=True)


        announcement.info["case_message_id"] = case_message.id
        self.bot.announcement_manager.add_announcement(announcement)

        
        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True)