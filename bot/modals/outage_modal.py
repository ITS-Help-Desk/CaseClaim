import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING
from bot.announcement import Announcement

from bot.views.outage_view import OutageView

if TYPE_CHECKING:
    from bot.bot import Bot


class OutageModal(ui.Modal, title='Outage Form'):
    def __init__(self, bot: "Bot"):
        super().__init__()
        self.bot = bot

    service = ui.TextInput(label='Service',style=discord.TextStyle.short)
    parent_case = ui.TextInput(label='Parent Case # (Optional)',style=discord.TextStyle.short, required=False)
    description = ui.TextInput(label='Description of Outage', style=discord.TextStyle.paragraph)
    troubleshooting_steps = ui.TextInput(label='How to Troubleshoot (Optional)', style=discord.TextStyle.paragraph, required=False)
    resolution_time = ui.TextInput(label='Expected Resolution Time (Optional)', style=discord.TextStyle.short, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        # Create outage for OutageManager
        service = str(self.service)
        parent_case = str(self.parent_case) if len(str(self.parent_case)) != 0 else None
        description = str(self.description)
        troubleshooting_steps = str(self.troubleshooting_steps) if len(str(self.troubleshooting_steps)) != 0 else None
        resolution_time = str(self.resolution_time) if len(str(self.resolution_time)) != 0 else None

        info = {
            "service": service,
            "parent_case": parent_case,
            "description": description,
            "troubleshooting_steps": troubleshooting_steps,
            "resolution_time": resolution_time
        }

        outage = Announcement("outage", info)

        announcement_embed = outage.to_announcement_embed()

        # Send announcement message
        announcement_channel = await self.bot.fetch_channel(self.bot.announcement_channel)    
        announcement_message = await announcement_channel.send(content="@everyone", embed=announcement_embed, view=OutageView(self.bot))

        outage.announcement_message_id = announcement_message.id


        case_embed = outage.to_case_embed(announcement_message.jump_url)

        # Send case message
        case_channel = await self.bot.fetch_channel(self.bot.cases_channel)    
        case_message = await case_channel.send(embed=case_embed, silent=True)


        outage.info["case_message_id"] = case_message.id
        self.bot.announcement_manager.add_announcement(outage)

        
        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True)