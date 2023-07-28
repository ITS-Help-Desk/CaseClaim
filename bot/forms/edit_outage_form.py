import discord
import discord.ui as ui

from bot.models.outage import Outage

# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class EditOutageForm(ui.Modal, title='Outage Update Form'):
    def __init__(self, bot: "Bot", outage: Outage):
        super().__init__()
        self.bot = bot
        self.outage = outage

        self.service = ui.TextInput(label='Service', style=discord.TextStyle.short, default=outage.service)
        self.add_item(self.service)
        self.parent_case = ui.TextInput(label='Parent Case # (Optional)', style=discord.TextStyle.short, required=False,
                                        default=outage.parent_case)
        self.add_item(self.parent_case)
        self.description = ui.TextInput(label='Description of Outage', style=discord.TextStyle.paragraph,
                                        default=outage.description)
        self.add_item(self.description)
        self.troubleshoot_steps = ui.TextInput(label='How to Troubleshoot (Optional)',
                                               style=discord.TextStyle.paragraph, required=False,
                                               default=outage.troubleshooting_steps)
        self.add_item(self.troubleshoot_steps)
        self.resolution_time = ui.TextInput(label='Expected Resolution Time (Optional)', style=discord.TextStyle.short,
                                            required=False, default=outage.resolution_time)
        self.add_item(self.resolution_time)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        new_service = str(self.service)
        new_parent_case = str(self.parent_case)
        new_description = str(self.description)
        new_troubleshoot_steps = str(self.troubleshoot_steps)
        new_resolution_time = str(self.resolution_time)

        self.outage.remove_from_database(self.bot.connection)

        new_outage = Outage(self.outage.message_id, self.outage.case_message_id, new_service, new_parent_case, new_description, new_troubleshoot_steps, new_resolution_time, self.outage.user, True)

        new_outage.add_to_database(self.bot.connection)

        # Create announcement embed
        announcement_embed = discord.Embed(title=f"{new_service} Outage", colour=discord.Color.red())

        # Add parent case
        if new_parent_case is not None and len(str(new_parent_case)) != 0:
            announcement_embed.description = f"Parent Case: **{new_parent_case}**"

        announcement_embed.add_field(name="Description", value=f"{new_description}", inline=False)

        if new_troubleshoot_steps is not None and len(str(new_troubleshoot_steps)) != 0:
            announcement_embed.add_field(name="How to Troubleshoot", value=f"{new_troubleshoot_steps}", inline=False)

        if new_resolution_time is not None and len(str(new_resolution_time)) != 0:
            announcement_embed.add_field(name="ETA to Resolution", value=f"{new_resolution_time}", inline=False)

        # Edit announcement message
        announcement_message: discord.Message = await interaction.channel.fetch_message(self.outage.message_id)
        await announcement_message.edit(embed=announcement_embed)

        # Create case embed
        case_embed = discord.Embed(title=f"{new_service} Outage", colour=discord.Color.red())
        case_embed.description = f"{announcement_message.jump_url}"

        if new_parent_case is not None and len(str(new_parent_case)) != 0:
            case_embed.description += f"\nParent Case: **{new_parent_case}**"

        # Edit case message
        case_channel = await interaction.guild.fetch_channel(self.bot.cases_channel)
        case_message = await case_channel.fetch_message(self.outage.case_message_id)
        await case_message.edit(embed=case_embed)

        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True, delete_after=0)