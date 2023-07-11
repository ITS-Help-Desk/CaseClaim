import discord
import discord.ui as ui

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

from bot.announcement import Announcement

if TYPE_CHECKING:
    from bot.bot import Bot


class EditOutageModal(ui.Modal, title='Outage Update Form'):
    def __init__(self, bot: "Bot", outage: Announcement):
        super().__init__()
        self.bot = bot
        self.outage = outage

        self.service = ui.TextInput(label='Service',style=discord.TextStyle.short, default=outage.info["service"])
        self.add_item(self.service)
        self.parent_case = ui.TextInput(label='Parent Case # (Optional)',style=discord.TextStyle.short, required=False, default=outage.info["parent_case"])
        self.add_item(self.parent_case)
        self.description = ui.TextInput(label='Description of Outage', style=discord.TextStyle.paragraph, default=outage.info["description"])
        self.add_item(self.description)
        self.troubleshoot_steps = ui.TextInput(label='How to Troubleshoot (Optional)', style=discord.TextStyle.paragraph, required=False, default=outage.info["troubleshooting_steps"])
        self.add_item(self.troubleshoot_steps)
        self.resolution_time = ui.TextInput(label='Expected Resolution Time (Optional)', style=discord.TextStyle.short, required=False, default=outage.info["resolution_time"])
        self.add_item(self.resolution_time)


    async def on_submit(self, interaction: discord.Interaction) -> None:
        new_service = str(self.service)
        new_parent_case = str(self.parent_case)
        new_description = str(self.description)
        new_troubleshoot_steps = str(self.troubleshoot_steps)
        new_resolution_time = str(self.resolution_time)

        self.bot.announcement_manager.remove_announcement(self.outage)

        self.outage.info["service"] = new_service
        self.outage.info["parent_case"] = new_parent_case
        self.outage.info["description"] = new_description
        self.outage.info["troubleshooting_steps"] = new_troubleshoot_steps
        self.outage.info["resolution_time"] = new_resolution_time


        self.bot.announcement_manager.add_announcement(self.outage)

        # Edit announcement message
        announcement_message = await interaction.channel.fetch_message(self.outage.announcement_message_id)
        await announcement_message.edit(embed=self.outage.to_announcement_embed())
        
        # Edit case message
        case_channel = await interaction.guild.fetch_channel(self.bot.cases_channel)
        case_message = await case_channel.fetch_message(self.outage.info["case_message_id"])
        await case_message.edit(embed=self.outage.to_case_embed(announcement_message.jump_url))

        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True, delete_after=0)