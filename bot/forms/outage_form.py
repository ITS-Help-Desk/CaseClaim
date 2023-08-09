import discord
import discord.ui as ui
import datetime

from bot.views.outage_view import OutageView
from bot.models.outage import Outage
from bot.models.user import User


# Use TYPE_CHECKING to avoid circular import from bot
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.bot import Bot


class OutageForm(ui.Modal, title='Outage Form'):
    def __init__(self, bot: "Bot"):
        """Creates a form for creating an outage.
        Records the service name, parent case, description,
        troubleshooting steps, and resolution time.

        Args:
            bot (Bot): A reference to the original Bot instantiation.
        """
        super().__init__()
        self.bot = bot

    service = ui.TextInput(label='Service', style=discord.TextStyle.short)
    parent_case = ui.TextInput(label='Parent Case # (Optional)', style=discord.TextStyle.short, required=False)
    description = ui.TextInput(label='Description of Outage', style=discord.TextStyle.paragraph)
    troubleshooting_steps = ui.TextInput(label='How to Troubleshoot (Optional)', style=discord.TextStyle.paragraph,
                                         required=False)
    resolution_time = ui.TextInput(label='Expected Resolution Time (Optional)', style=discord.TextStyle.short,
                                   required=False)

    async def on_submit(self, interaction: discord.Interaction):
        """Creates an outage object and saves it to the database. Also sends a message
        to the announcement and cases channels.

        Args:
            interaction (discord.Interaction): Interaction that the slash command originated from.
        """
        user = User.from_id(self.bot.connection, interaction.user.id)

        service = str(self.service)
        parent_case = str(self.parent_case) if len(str(self.parent_case)) != 0 else None
        description = str(self.description)
        troubleshooting_steps = str(self.troubleshooting_steps) if len(str(self.troubleshooting_steps)) != 0 else None
        resolution_time = str(self.resolution_time) if len(str(self.resolution_time)) != 0 else None

        announcement_embed = discord.Embed(colour=discord.Color.red())
        announcement_embed.set_author(name=f"{service} Outage", icon_url="https://thumbs.gfycat.com/DelayedVacantDassie-size_restricted.gif")

        try:
            announcement_embed.set_footer(text=user.full_name, icon_url=interaction.user.avatar.url)
        except:
            # Avatar not found
            announcement_embed.set_footer(text=user.full_name)

        announcement_embed.timestamp = datetime.datetime.now()


        # Add parent case
        if parent_case is not None and len(str(parent_case)) != 0:
            announcement_embed.description = f"Parent Case: **{parent_case}**"

        announcement_embed.add_field(name="Description", value=f"{description}", inline=False)

        # Add troubleshooting steps
        if troubleshooting_steps is not None and len(str(troubleshooting_steps)) != 0:
            announcement_embed.add_field(name="How to Troubleshoot", value=f"{troubleshooting_steps}", inline=False)

        # Add resolution time
        if troubleshooting_steps is not None and len(str(resolution_time)) != 0:
            announcement_embed.add_field(name="ETA to Resolution", value=f"{resolution_time}", inline=False)

        # Send announcement message
        announcement_channel = await self.bot.fetch_channel(self.bot.announcement_channel)
        announcement_message = await announcement_channel.send(content="@here", embed=announcement_embed, view=OutageView(self.bot))

        # Create case embed
        case_embed = discord.Embed(title=f"{service} Outage", colour=discord.Color.red())
        case_embed.description = f"{announcement_message.jump_url}"

        if parent_case is not None and len(str(parent_case)) != 0:
            case_embed.description += f"\nParent Case: **{parent_case}**"

        # Send case message
        case_channel = await self.bot.fetch_channel(self.bot.cases_channel)
        case_message = await case_channel.send(embed=case_embed, silent=True)

        out = Outage(announcement_message.id, case_message.id, service, parent_case, description, troubleshooting_steps, resolution_time, User.from_id(self.bot.connection, interaction.user.id), True)
        out.add_to_database(self.bot.connection)
        # Send confirmation message
        await interaction.response.send_message(content="👍", ephemeral=True, delete_after=0)

        await announcement_message.edit(content="")
